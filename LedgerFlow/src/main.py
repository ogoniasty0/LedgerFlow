from validators import get_non_empty_string
from services import display_budget, add_new_transaction, filter_transactions
from storage import load_account, export_to_csv

ACCOUNT = load_account()

def handle_menu_choice(choice: str) -> bool:
    match choice.strip():
        case "1":
            display_budget(ACCOUNT)
            return True
        case "2":
            print("\n--- Dodawanie nowej transakcji ---")
            category = get_non_empty_string("Podaj kategorię: ")

            while True:
                try:
                    amount = float(get_non_empty_string("Podaj kwotę: "))
                    break
                except ValueError:
                    print("Błąd: Nieprawidłowa kwota. Wprowadź liczbę.")

            tx_type = get_non_empty_string("Podaj typ transakcji (PRZYCHOD / WYDATEK): ")

            try:
                add_new_transaction(ACCOUNT, category, amount, tx_type)
            except (ValueError, TypeError) as e:
                print(f"\n[BŁĄD BIZNESOWY] {e}")

            return True
        case "3":
            print("\n--- FILTROWANIE TRANSAKCJI ---")
            category = get_non_empty_string("Podaj kategorię do wyszukania: ")
            filter_transactions(ACCOUNT, category)
            return True
        case "4":
            print("\n--- EKSPORT DO CSV ---")
            rows = export_to_csv(ACCOUNT)
            print(f"Sukces: Wyeksportowano {rows} transakcji z konta do pliku CSV.")
            return True
        case "5" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case _:
            print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 5.")
            return True

def print_menu():
    print("\n" + "=" * 40)
    print(" ASYSTENT BUDŻETU DOMOWEGO (OOP) ")
    print("=" * 40)
    print(f" Aktualne Saldo: {ACCOUNT.current_balance():.2f} PLN")
    print("-" * 40)
    print("1. Wyświetl rejestr transakcji/budżet")
    print("2. Dodaj nową transakcję")
    print("3. Filtruj transakcje")
    print("4. Eksportuj transakcje do CSV")
    print("5. Wyjście z programu")
    print("-" * 40)

def main():
    running = True
    while running:
        print_menu()
        user_choice = input("Wybierz opcję [1-5]: ")
        running = handle_menu_choice(user_choice)

if __name__ == "__main__":
    main()