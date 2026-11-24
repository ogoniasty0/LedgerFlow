from manager import LedgerManager
from models import ExpenseTransaction, IncomeTransaction
from storage import (
    execute_account_transfer,
    fetch_accounts_balance_report,
    fetch_expenses_by_category,
    load_manager,
    persist_new_transaction,
    query_transactions,
)


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


def display_filtered_transactions(
    category_phrase: str,
    tx_type: str | None,
    date_from: str | None,
    date_to: str | None,
    min_amount: float,
    sort_by: str,
) -> None:
    rows = query_transactions(
        category_phrase=category_phrase,
        tx_type=tx_type,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        sort_by=sort_by,
    )
    print("\n" + "=" * 92)
    print(f" WYNIKI WYSZUKIWANIA SQL (znaleziono: {len(rows)})")
    print("=" * 92)
    if not rows:
        print("  Brak transakcji spełniających podane kryteria.")
    for r in rows:
        print(
            f"  [{r['tx_id']:02d}] {r['tx_date']} | {r['account_name']:<20} | "
            f"{r['tx_type']:<8} | {r['category']:<15} | {r['amount_pln']:>8.2f} PLN"
        )
    print("-" * 92)


def display_analytical_reports(min_balance: float = 0.0, min_spent: float = 0.0) -> None:
    accounts_report = fetch_accounts_balance_report(min_balance=min_balance)
    categories_report = fetch_expenses_by_category(min_spent=min_spent)

    print("\n" + "=" * 92)
    print(f" RAPORT JOIN #1: BILANS RACHUNKÓW (saldo >= {min_balance:.2f} PLN)")
    print("=" * 92)
    for acc in accounts_report:
        print(
            f"  [ID {acc['account_id']}] {acc['account_name']:<22} | Start: {acc['initial_balance_pln']:>8.2f} | "
            f"Przychody: +{acc['total_income_net']:>8.2f} | Wydatki: -{acc['total_expense_net']:>8.2f} | "
            f"SALDO: {acc['current_balance_pln']:>8.2f} PLN (tx: {acc['tx_count']})"
        )

    print("\n" + "=" * 92)
    print(f" RAPORT JOIN #2: WYDATKI PER KATEGORIA (suma >= {min_spent:.2f} PLN)")
    print("=" * 92)
    if not categories_report:
        print("  Brak kategorii przekraczających zadany próg.")
    for cat in categories_report:
        print(
            f"  * {cat['category']:<20} | Liczba transakcji: {cat['tx_count']:<3} | "
            f"Suma: {cat['total_spent_pln']:>8.2f} PLN | Średnia: {cat['avg_spent_pln']:>8.2f} PLN"
        )
    print("-" * 92)


def perform_transfer_and_reload(from_id: int, to_id: int, amount: float) -> LedgerManager:
    out_id, in_id = execute_account_transfer(from_id, to_id, amount)
    print(f"Sukces (COMMIT): Wykonano przelew {amount:.2f} PLN (ID wydatku: {out_id}, ID przychodu: {in_id}).")
    return load_manager()