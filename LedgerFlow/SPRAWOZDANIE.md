# Sprawozdanie z Zadania Laboratoryjnego nr 1
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
    **Projekt:** LedgerFlow
**Zespół (Autorzy):**  
1. Oskar Ogonek (nr albumu: [NUMER]) – login Git: `ogoniasty0`
2. Karol Zegartowski (nr albumu: [NUMER]) – login Git: `KarolZegartowski`  
**Data oddania:** [13.10.2026r]  

---

## 1. Cel i Zakres Inżynierski Zadania
Implementacje funkcji dodających, filtrujących i wyświetlających bieżących wydatków.

---

## 2. Architektura Rozwiązania i Struktura Modułów
* `src/data.py` – Sluży jako baza danych
* `src/validators.py` – Obsluga blędów
* `src/services.py` – Wszystkie funkcje programu
* `src/main.py` – Główny plik programu zawierający menu

---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie
*(Wybrany, najważniejszy lub najciekawszy fragment kodu źródłowego zrealizowany w tym etapie – maksymalnie 15–25 linii).*

```python
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
```

**Uzasadnienie wyboru:**  
Funkcja filtrowania pozwala wyświetlić wydatki posegregowane wedlug określonej kategorii



## 4. Scenariusze Weryfikacji i Wyniki Testów
======================================================================
| id  | Kategoria            | Kwota      | Typ       
----------------------------------------------------------------------
| 1   | Zakupy               |     256.00 | wydatek   
| 2   | Wypłata              |    5000.00 | dochód    
| 3   | zakupy               |     300.00 | wydatek   
| 4   | Rozrywka             |     300.00 | wydatek   
| 5   | Zakupy               |     222.00 | wydatek   
| 6   | Rachunki             |     455.00 | wydatek   
----------------------------------------------------------------------


### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** Poprawne dodanie rekordu do tabeli
* **Oczekiwany i uzyskany wynik:**
```======================================================================
| id  | Kategoria            | Kwota      | Typ       
----------------------------------------------------------------------
| 1   | Zakupy               |     256.00 | wydatek   
| 2   | Wypłata              |    5000.00 | dochód    
| 3   | zakupy               |     300.00 | wydatek   
| 4   | Rozrywka             |     300.00 | wydatek   
| 5   | Zakupy               |     222.00 | wydatek   
| 6   | Rachunki             |     455.00 | wydatek   
----------------------------------------------------------------------

```

### Scenariusz B: Obsługa błędów i wartości brzegowych
* **Dane wejściowe (błędne):** wpisanie litery zamiast cyrf
* **Reakcja programu:**
```
Podaj kwotę: dwa
Błąd: Nieprawidłowa kwota. Wprowadź liczbę.
```

---

## 5. Podział Pracy w Zespole
*(Precyzyjne i uczciwe rozliczenie wkładu obu członków zespołu – weryfikowane z historią commitów `git log`).*
* **Karol Zegartowski:**
  * Odpowiedzialność za moduły: `src/data.py, main.py`
  * Zaimplementowane funkcjonalności: Dodanie glownego menu w pliku main, stworzenie bazy danych.
  * Liczba wykonanych commitów: 5
* **Oskar Ogonek:**
  * Odpowiedzialność za moduły: `src/validators.py, services.py`
  * Zaimplementowane funkcjonalności: Stworzenie funkcji odpowiedzialnych za wyswietlanie, dodawania i filrtowania.
  * Liczba wykonanych commitów: 4


