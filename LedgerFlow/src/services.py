from manager import LedgerManager
from models import ExpenseTransaction, IncomeTransaction
from storage import persist_new_transaction


def display_ledger(manager: LedgerManager) -> None:
    print("\n" + "=" * 92)
    print(f" PORTFEL: {manager.account_name} | Saldo Całkowite: {manager.calculate_total_balance():.2f} PLN")
    print("=" * 92)
    for tx in manager.transactions:
        print(f"  * {tx}")
    print("-" * 92)


def add_expense(manager: LedgerManager, category: str, amount: float, operator_fee: float) -> None:
    tx_id = manager.generate_next_id()
    tx = ExpenseTransaction(tx_id, category, amount, operator_fee)
    manager.register_transaction(tx)
    persist_new_transaction(tx)
    print(f"Sukces: Dodano wydatek o ID {tx.tx_id}.")


def add_income(manager: LedgerManager, category: str, amount: float, source: str, tax_pct: float) -> None:
    tx_id = manager.generate_next_id()
    tx = IncomeTransaction(tx_id, category, amount, source, tax_pct)
    manager.register_transaction(tx)
    persist_new_transaction(tx)
    print(f"Sukces: Dodano przychód o ID {tx.tx_id}.")