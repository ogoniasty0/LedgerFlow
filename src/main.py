def handle_menu_choice(choice: str) -> bool:
    match choice.strip():
        case "1":
            display_budget()
        case "2":
            add_new_transaction()
        case "3":
            show_limits()
        case "4" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case _:
            print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 4.")
    return True

def print_menu():
    print("\n" + "=" * 40)
    print(" ASYSTENT BUDŻETU DOMOWEGO ")
    print("=" * 40)
    print("1. Wyświetl rejstr transakcji/budżet")
    print("2. Dodaj nową transakcję")
    print("3. Cele i limity wydatków")
    print("4. Wyjście z programu")
    print("-" * 40)

def main():
    running = True
    while running:
        print_menu()
        user_choice = input("Wybierz opcję [1-4]: ")
        running = handle_menu_choice(user_choice)

if __name__ == "__main__":
    main()
