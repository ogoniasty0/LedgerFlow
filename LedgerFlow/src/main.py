from validators import get_non_empty_string
from services import display_ledger, add_expense, add_income
from storage import load_manager, export_to_csv

MANAGER = load_manager()

def handle_menu_choice(choice: str) -> bool:
    match choice.strip():
        case "1":
            display_ledger(MANAGER)
            return True
        case "2":
            print("\n--- Dodawanie Wydatku ---")
            category = get_non_empty_string("Podaj kategorię: ")
            amount = float(get_non_empty_string("Podaj kwotę PLN: "))
            fee = float(get_non_empty_string("Podaj prowizję operatora PLN [0 jeśli brak]: "))
            try:
                add_expense(MANAGER, category, amount, fee)
            except (ValueError, TypeError) as e:
                print(f"\n[BŁĄD BIZNESOWY] {e}")
            return True
        case "3":
            print("\n--- Dodawanie Przychodu ---")
            category = get_non_empty_string("Podaj kategorię: ")
            amount = float(get_non_empty_string("Podaj kwotę PLN: "))
            source = get_non_empty_string("Podaj źródło (np. Etat, Premia): ")
            tax = float(get_non_empty_string("Podaj podatek u źródła % [0-100]: "))
            try:
                add_income(MANAGER, category, amount, source, tax)
            except (ValueError, TypeError) as e:
                print(f"\n[BŁĄD BIZNESOWY] {e}")
            return True
        case "4":
            print("\n--- EKSPORT DO CSV ---")
            count = export_to_csv(MANAGER)
            print(f"Wyeksportowano {count} wierszy do pliku exports/ledger_export.csv.")
            return True
        case "5" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case _:
            print("Nieznana opcja. Wybierz 1-5.")
            return True

def print_menu():
    print("\n" + "=" * 40)
    print(" ASYSTENT BUDŻETU DOMOWEGO")
    print("=" * 40)
    print(f" Dostępne Saldo: {MANAGER.calculate_total_balance():.2f} PLN")
    print("-" * 40)
    print("1. Wyświetl rejestr i saldo portfela")
    print("2. Dodaj Wydatek")
    print("3. Dodaj Przychód")
    print("4. Eksportuj rejestr do CSV")
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