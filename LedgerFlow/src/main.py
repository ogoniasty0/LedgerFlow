import sqlite3

from services import (
    add_expense,
    add_income,
    display_analytical_reports,
    display_filtered_transactions,
    display_ledger,
    perform_transfer_and_reload,
)
from storage import create_secondary_account, export_to_csv, load_manager
from validators import get_int_input, get_non_empty_string

MANAGER = load_manager()


def handle_menu_choice(choice: str) -> bool:
    global MANAGER
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
        case "5":
            print("\n--- WYSZUKIWANIE TRANSAKCJI ---")
            phrase = input("Fragment kategorii [Enter = wszystkie]: ")
            tx_type = input("Typ (PRZYCHOD / WYDATEK) [Enter = wszystkie]: ").strip() or None
            date_from = input("Data od (RRRR-MM-DD) [Enter = brak]: ").strip() or None
            date_to = input("Data do (RRRR-MM-DD) [Enter = brak]: ").strip() or None
            min_amt_raw = input("Kwota minimalna PLN [Enter = 0]: ").strip()
            min_amt = float(min_amt_raw) if min_amt_raw else 0.0
            try:
                display_filtered_transactions(phrase, tx_type, date_from, date_to, min_amt, sort_by="tx_date")
            except ValueError as e:
                print(f"\n[BŁĄD WALIDACJI] {e}")
            return True
        case "6":
            print("\n--- RAPORTY ANALITYCZNE ---")
            min_bal_raw = input("Minimalne saldo konta PLN [Enter = 0]: ").strip()
            min_spent_raw = input("Minimalna suma wydatków w kategorii PLN [Enter = 0]: ").strip()
            min_bal = float(min_bal_raw) if min_bal_raw else 0.0
            min_spent = float(min_spent_raw) if min_spent_raw else 0.0
            display_analytical_reports(min_balance=min_bal, min_spent=min_spent)
            return True
        case "7":
            print("\n--- PRZELEW MIĘDZY RACHUNKAMI ---")
            print("1. Utwórz dodatkowy rachunek (np. Konto Oszczędnościowe)")
            print("2. Wykonaj przelew między istniejącymi rachunkami")
            sub = input("Wybierz [1-2]: ").strip()
            if sub == "1":
                name = get_non_empty_string("Nazwa nowego rachunku: ")
                init_bal = float(get_non_empty_string("Saldo początkowe PLN: "))
                new_id = create_secondary_account(name, init_bal)
                print(f"Utworzono rachunek '{name}' o ID = {new_id}.")
            elif sub == "2":
                from_id = get_int_input("ID konta źródłowego: ", min_val=1)
                to_id = get_int_input("ID konta docelowego: ", min_val=1)
                amount = float(get_non_empty_string("Kwota przelewu PLN: "))
                try:
                    MANAGER = perform_transfer_and_reload(from_id, to_id, amount)
                except (ValueError, sqlite3.IntegrityError) as e:
                    print(f"\n[ROLLBACK TRANSAKCJI] Przelew odrzucony: {e}")
            return True
        case "8" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case _:
            print("Nieznana opcja. Wybierz 1-8.")
            return True


def print_menu() -> None:
    print("\n" + "=" * 48)
    print(" ASYSTENT BUDŻETU DOMOWEGO")
    print("=" * 48)
    print(f" Dostępne Saldo: {MANAGER.calculate_total_balance():.2f} PLN")
    print("-" * 48)
    print("1. Wyświetl rejestr i saldo portfela")
    print("2. Dodaj Wydatek")
    print("3. Dodaj Przychód")
    print("4. Eksportuj rejestr do CSV")
    print("5. Szukaj transakcji")
    print("6. Raporty analityczne")
    print("7. Rachunki i Przelew między kontami")
    print("8. Wyjście z programu")
    print("-" * 48)


def main() -> None:
    running = True
    while running:
        print_menu()
        user_choice = input("Wybierz opcję [1-8]: ")
        running = handle_menu_choice(user_choice)


if __name__ == "__main__":
    main()