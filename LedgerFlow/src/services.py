from models import Account, Transaction
from storage import save_account

def display_budget(account: Account) -> None:
    print("\n" + "=" * 70)
    print(f" BILANS KONTA: {account.account_name} | Saldo: {account.current_balance():.2f} PLN")
    print("=" * 70)
    print(f"| {'ID':<3} | {'Kategoria':<20} | {'Kwota PLN':<10} | {'Typ':<10}")
    print("-" * 70)
    for tx in account.transactions:
        print(f"| {tx.tx_id:<3} | {tx.category:<20} | {tx.amount_pln:>10.2f} | {tx.tx_type:<10}")
    print("-" * 70)

def add_new_transaction(account: Account, category: str, amount: float, tx_type: str) -> None:
    existing_ids = [tx.tx_id for tx in account.transactions]
    new_id = max(existing_ids) + 1 if existing_ids else 1

    new_tx = Transaction(tx_id=new_id, category=category, amount_pln=amount, tx_type=tx_type)

    account.register_tx(new_tx)

    save_account(account)
    print(f"Sukces: Dodano transakcję o ID {new_id}.")

def filter_transactions(account: Account, target_category: str) -> None:
    """Filtruje transakcje po kategorii w obiekcie Account."""
    filtered = [
        tx for tx in account.transactions 
        if tx.category.lower() == target_category.lower()
    ]
    
    print(f"\n--- WYNIKI DLA KATEGORII: '{target_category}' ---")
    if not filtered:
        print("Brak transakcji w tej kategorii.")
    else:
        temp_acc = Account(f"Filtr: {target_category}", initial_balance=0.0, transactions=filtered)
        display_budget(temp_acc)