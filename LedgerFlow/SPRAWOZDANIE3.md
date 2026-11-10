# Sprawozdanie z Zadania Laboratoryjnego nr [3]
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
    **Projekt:** [NAZWA PROJEKTU, np. CineStream / BrewMaster]  
**Zespół (Autorzy):**  
1. Oskar Ogonek (nr albumu: 164856) – login Git: `ogoniasty0`
2. Karol Zegartowski (nr albumu: 164892) – login Git: `KarolZegartowski`   
**Data oddania:** [10.11.2026]  

---

## 1. Cel i Zakres Inżynierski Zadania
Zaimplementowanie encji, slowników i agregatu. 
---

## 2. Architektura Rozwiązania i Struktura Modułów
*(Wykaz zrealizowanych plików w katalogu `src/` wraz z przypisaniem ich odpowiedzialności).*
* `src/validators.py` – Obsluga blędów
* `src/services.py` – Wszystkie funkcje programu
* `src/main.py` – Główny plik programu zawierający menu
* `src/storage.py` - Plik przechowujący funkcje odpowiedzialne za atomowy zapis, eksport do csv i tworzenie kopii zapasowych.
* `src/models.py` - Obiektowa warstwa aplikacji
* `src/test-models.py` - Plik sprawdzający wszystkie zaimplementowane funkcje za jednym razem.

---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie

```python
def display_ledger(manager: LedgerManager) -> None:
    print("\n" + "=" * 80)
    print(f" PORTFEL: {manager.account_name} | Saldo Całkowite: {manager.calculate_total_balance():.2f} PLN")
    print("=" * 80)
    for tx in manager.transactions:
        print(f"  * {tx}")
    print("-" * 80)
```

**Uzasadnienie wyboru:**  
Wyswietla obliczone poilmorficznie saldo w zaleznosci od konta.

---

## 4. Scenariusze Weryfikacji i Wyniki Testów
*(Dowód działania programu w konsoli. Należy przedstawić przynajmniej dwa scenariusze).*

### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** Poprawne dodanie wydatku i wyświetlenie go
* **Oczekiwany i uzyskany wynik:**
```================================================================================
 PORTFEL: Główne Konto Domowe | Saldo Całkowite: 3843.50 PLN
================================================================================
  * [01] WYDATEK | Zakupy Spozywcze | -  152.50 PLN (Prowizja: 2.50 PLN)
  * [02] PRZYCHÓD | Wyplata         | + 3520.00 PLN (Źródło: Etat, Podatek: 12.0%)
  * [03] WYDATEK | zakupy          | -   24.00 PLN (Prowizja: 0.00 PLN)
--------------------------------------------------------------------------------

========================================
```

### Scenariusz B: Obsługa błędów i wartości brzegowych
* **Dane wejściowe (błędne):** Wpisanie prowizji operatora w wysokości -99
* **Reakcja programu:**
```
[BŁĄD BIZNESOWY] Kwota musi być większa od zera (podano: -99.0).
```

---

## 5. Podział Pracy w Zespole
*(Precyzyjne i uczciwe rozliczenie wkładu obu członków zespołu – weryfikowane z historią commitów `git log`).*
* **[Imię Nazwisko Studenta 1]:**
  * Odpowiedzialność za moduły: `src/...`
  * Zaimplementowane funkcjonalności: [...]
  * Liczba wykonanych commitów: [...]
* **[Imię Nazwisko Studenta 2]:**
  * Odpowiedzialność za moduły: `src/...`
  * Zaimplementowane funkcjonalności: [...]
  * Liczba wykonanych commitów: [...]
