def display_budget(TRANSACTIONS):
    print("\n" + "=" * 70)
    print(f"| {'id':<3} | {'Kategoria':<20} | {'Kwota':<10} | {'Typ':<10}")
    print("-" * 70)
    for transaction in TRANSACTIONS:
        print(f"| {transaction['id']:<3} | {transaction['category']:<20} | {transaction['amount']:>10.2f} | {transaction['type']:<10}")
    print("-" * 70)
def add_new_transaction(TRANSACTIONS, category, amount, type):
    new_id = len(TRANSACTIONS) + 1
    new_transaction = {
        "id": new_id,
        "category": category,
        "amount": amount,
        "type": type
    }
    TRANSACTIONS.append(new_transaction)
    print(f"Nowa transakcja o id {new_id} została dodana.")    
def filter_transactions(records, target_category):   
    filtered = []

    for item in records:

        if item['category'].lower() == target_category.lower():

            filtered.append(item)
    print(f"\n--- WYNIKI DLA KATEGORII: '{target_category}' ---")

    if not filtered:
        print("Brak transakcji w tej kategorii.")
    else:
        display_budget(filtered)