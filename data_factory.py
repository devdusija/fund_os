import csv
import os
import random
from datetime import datetime
from copy import deepcopy


class DataFactory:
    def __init__(self):
        self.accounts = ["ACC1", "ACC2", "ACC3"]

        self.distributions = {
            "EXACT_MATCH": 50,
            "PRICE_ADJUSTMENT": 15,
            "QUANTITY_ADJUSTMENT": 10,
            "MISSING_TRADE": 10,
            "PARTIAL_FILL": 10,
            "AGGREGATION": 5,
        }

    def generate_base_trades(self, n=20):
        trades = []

        for i in range(n):
            trade = {
                "trade_id": f"T{i+1:03}",
                "isin": f"IN{random.randint(100000000, 999999999)}",
                "trade_date": "2026-03-20",
                "settlement_date": "2026-03-22",
                "side": random.choice(["BUY", "SELL"]),
                "quantity": random.randint(50, 500),
                "price": round(random.uniform(100, 3000), 2),
                "account": random.choice(self.accounts),
            }
            trades.append(trade)

        return trades

    def pick_scenario(self):
        scenarios = list(self.distributions.keys())
        weights = list(self.distributions.values())

        return random.choices(scenarios, weights=weights, k=1)[0]

    def apply_scenario(self, trade, scenario):
        trade = deepcopy(trade)
        trade["scenario"] = scenario
        trade["source"] = "custodian"

        if scenario == "EXACT_MATCH":
            return trade

        elif scenario == "PRICE_ADJUSTMENT":
            trade["price"] = round(trade["price"] * random.uniform(1.001, 1.01), 2)
            return trade

        elif scenario == "QUANTITY_ADJUSTMENT":
            trade["quantity"] -= random.randint(1, 20)
            return trade

        elif scenario == "MISSING_TRADE":
            return None

        elif scenario == "PARTIAL_FILL":
            qty1 = int(trade["quantity"] * 0.4)
            qty2 = trade["quantity"] - qty1

            t1 = deepcopy(trade)
            t2 = deepcopy(trade)

            t1["trade_id"] += "-A"
            t2["trade_id"] += "-B"

            t1["quantity"] = qty1
            t2["quantity"] = qty2

            t1["price"] = round(trade["price"] * 0.999, 2)
            t2["price"] = round(trade["price"] * 1.001, 2)

            t1["parent_trade_id"] = trade["trade_id"]
            t2["parent_trade_id"] = trade["trade_id"]

            return [t1, t2]

        elif scenario == "AGGREGATION":
            return trade

    def generate_custodian_trades(self, base_trades):
        custodian = []

        for trade in base_trades:
            scenario = self.pick_scenario()
            result = self.apply_scenario(trade, scenario)

            if result is None:
                continue
            elif isinstance(result, list):
                custodian.extend(result)
            else:
                custodian.append(result)

        return custodian

    def write_csv(self, file_path, trades):
        if not trades:
            return

        all_keys = set()
        for trade in trades:
            all_keys.update(trade.keys())

        keys = list(all_keys)

        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(trades)

    def _generate_file_path(self, suffix):
        name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + f"_{suffix}.csv"
        data_dir = os.path.join(os.getcwd(), "data")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        return os.path.join(data_dir, name)

    def run(self, n=20):
        base_trades = self.generate_base_trades(n)

        broker_trades = deepcopy(base_trades)
        for t in broker_trades:
            t["source"] = "broker"
            t["scenario"] = "BASE"

        custodian_trades = self.generate_custodian_trades(base_trades)

        broker_path = self._generate_file_path("broker")
        custodian_path = self._generate_file_path("custodian")

        self.write_csv(broker_path, broker_trades)
        self.write_csv(custodian_path, custodian_trades)

        print("✅ Files generated:")
        print("Broker:", broker_path)
        print("Custodian:", custodian_path)


if __name__ == "__main__":
    factory = DataFactory()
    factory.run(30)