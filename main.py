from data_factory import DataFactory
from reconciliation import Reconciliation



if __name__ == "__main__":
    factory = DataFactory()
    broker_trades, custodian_trades = factory.run(30)

    reconciliation = Reconciliation()
    results = reconciliation.reconcile(broker_trades, custodian_trades)

    print(f"\n Reconciliation Results ({len(results)} trades):")
    for r in results:
        print(r)