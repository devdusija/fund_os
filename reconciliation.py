class Reconciliation:
    def __init__(self):
        pass
    
    def build_index(self, trades):
        index = {}
        for t in trades:
            index[t["trade_id"]] = t
        return index

    def match_trades(self, broker, custodian):
        broker_index = self.build_index(broker)
        custodian_index = self.build_index(custodian)
        
        matches = []
        unmatched_broker = []
        unmatched_custodian = []

        for trade_id, b_trade in broker_index.items():
            if trade_id in custodian_index:
                matches.append((b_trade, custodian_index[trade_id]))
            else:
                unmatched_broker.append(b_trade)

        for trade_id, c_trade in custodian_index.items():
            if trade_id not in broker_index:
                unmatched_custodian.append(c_trade)

        return matches, unmatched_broker, unmatched_custodian

    def compare_trades(self, b, c):
        diffs = {}

        if b["price"] != c["price"]:
            diffs["price_diff"] = round(c["price"] - b["price"], 2)
        
        if b["quantity"] != c["quantity"]:
            diffs["qty_diff"] = c["quantity"] - b["quantity"]

        return diffs
        
    def classify_break(self, b, c, diffs):
        if "price_diff" in diffs:
            return "PRICE_BREAK"
        
        if "qty_diff" in diffs:
            return "QUANTITY_BREAK"
        
        return "MATCH"

    def reconcile(self, broker, custodian):
        matches, missing_broker, missing_custodian = self.match_trades(broker, custodian)

        results = []

        for b, c in matches:
            diffs = self.compare_trades(b, c)
            status = "MATCH" if not diffs else "BREAK"

            results.append({
                "trade_id": b["trade_id"],
                "status": status,
                "break_type": self.classify_break(b, c, diffs),
                "diffs": diffs
            })

        for b in missing_broker:
            results.append({
                "trade_id": b["trade_id"],
                "status": "BREAK",
                "break_type": "MISSING_IN_CUSTODIAN",
                "diffs": None
            })
        
        for c in missing_custodian:
            results.append({
                "trade_id": c["trade_id"],
                "status": "BREAK",
                "break_type": "MISSING_IN_BROKER",
                "diffs": None
            })

        return results