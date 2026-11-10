from manager import LedgerManager
from models import ExpenseTransaction, IncomeTransaction
from storage import save_manager

def display_ledger(manager: LedgerManager) -> None:
    print("\n" + "=" * 80)
    print(f" PORTFEL: {manager.account_name} | Saldo Całkowite: {manager.calculate_total_balance():.2f} PLN")
    print("=" * 80)
    for tx in manager.transactions:
        print(f"  * {tx}")
    print("-" * 80)

def add_expense(manager: LedgerManager, category: str, amount: float, operator_fee: float) -> None:
    tx_id = manager.generate_next_id()
    tx = ExpenseTransaction(tx_id, category, amount, operator_fee)
    manager.register_transaction(tx)
    save_manager(manager)
    print(f"Sukces: Dodano wydatek o ID {tx_id}.")

def add_income(manager: LedgerManager, category: str, amount: float, source: str, tax_pct: float) -> None:
    tx_id = manager.generate_next_id()
    tx = IncomeTransaction(tx_id, category, amount, source, tax_pct)
    manager.register_transaction(tx)
    save_manager(manager)
    print(f"Sukces: Dodano przychód o ID {tx_id}.")