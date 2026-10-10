def display_budget(TRANSACTIONS):
    print("\n" + "=" * 70)
    print(f"| {'id':<3} | {'Kategoria':<20} | {'Kwota':<10} | {'Typ':<10}")
    print("-" * 70)
    for transaction in TRANSACTIONS:
        print(f"| {transaction['id']:<3} | {transaction['category']:<20} | {transaction['amount']:>10.2f} | {transaction['type']:<10}")
    print("-" * 70)
  