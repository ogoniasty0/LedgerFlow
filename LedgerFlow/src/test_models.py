from models import Transaction, Account

def test_1_instantiation():
    tx1 = Transaction(1, "Pensja", 3000.0, "PRZYCHOD")
    tx2 = Transaction(2, "Zakupy", 150.0, "WYDATEK")
    acc = Account("Konto Testowe", initial_balance=500.0, transactions=[tx1, tx2])
    
    assert tx1.amount_pln == 3000.0
    assert tx2.tx_type == "WYDATEK"
    assert acc.current_balance() == 3350.0
    print("[OK] Scenariusz 1: Poprawne instancjonowanie zaliczone.")

def test_2_invariants_and_exceptions():
    # 2a. Ujemna kwota transakcji
    try:
        Transaction(3, "Błąd", -50.0, "WYDATEK")
        assert False, "Powinno rzucić ValueError dla ujemnej kwoty!"
    except ValueError:
        pass

    # 2b. Niepoprawny typ transakcji
    try:
        Transaction(4, "Błąd", 100.0, "NIEZNANY_TYP")
        assert False, "Powinno rzucić ValueError dla niedozwolonego typu!"
    except ValueError:
        pass

    # 2c. Odrzucenie wydatku powodującego debet
    acc = Account("Mój Portfel", initial_balance=100.0)
    huge_expense = Transaction(5, "Drogie Zakupy", 200.0, "WYDATEK")
    try:
        acc.register_tx(huge_expense)
        assert False, "Powinno zablokować wydatek przekraczający saldo!"
    except ValueError:
        pass

    print("[OK] Scenariusz 2: Odrzucenie błędnych danych zaliczone.")

def test_3_comparison_protocol():
    #Scenariusz 3: Działanie protokołu porównań (__eq__ oraz __lt__)
    tx_small = Transaction(1, "Kawa", 15.0, "WYDATEK")
    tx_medium = Transaction(2, "Obiad", 45.0, "WYDATEK")
    tx_big = Transaction(1, "Rachunki", 300.0, "WYDATEK")  # Ten sam tx_id co tx_small

    # Test tożsamości (__eq__) po tx_id
    assert tx_small == tx_big
    assert tx_small != tx_medium

    # Test sortowania (__lt__) po kwocie
    tx_list = [tx_big, tx_small, tx_medium]
    tx_list.sort()  # Sortuje rosnąco według kwoty
    assert tx_list == [tx_small, tx_medium, tx_big]
    print("[OK] Scenariusz 3: Protokoły porównań i sort() zaliczone.")

def test_4_roundtrip_serialization():
    """Scenariusz 4: Round-Trip Serialization (to_dict -> from_dict)"""
    tx1 = Transaction(1, "Wypłata", 5000.0, "PRZYCHOD")
    tx2 = Transaction(2, "Czynsz", 1200.0, "WYDATEK")
    original_acc = Account("Konto Domowe", initial_balance=1000.0, transactions=[tx1, tx2])

    # Serializacja do słownika
    raw_dict = original_acc.to_dict()
    # Rekonstrukcja z powrotem do obiektu
    restored_acc = Account.from_dict(raw_dict)

    assert original_acc == restored_acc
    assert restored_acc.current_balance() == 4800.0  # 1000 + 5000 - 1200
    print("[OK] Scenariusz 4: Round-Trip Serialization zaliczony.")

if __name__ == "__main__":
    print("=== URUCHAMIANIE AUTOTESTÓW MODUŁU MODELS.PY ===")
    test_1_instantiation()
    test_2_invariants_and_exceptions()
    test_3_comparison_protocol()
    test_4_roundtrip_serialization()
    print("\n[SUKCES] Wszystkie 4 scenariusze zaliczone pomyślnie! Moduł gotowy do odbioru.")