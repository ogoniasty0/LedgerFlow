# Sprawozdanie z Zadania Laboratoryjnego nr [4]
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
    **Projekt:** [LedgerFlow]  
**Zespół (Autorzy):**  
1. Oskar Ogonek (nr albumu: 164856) – login Git: `ogoniasty0`
2. Karol Zegartowski (nr albumu: 164892) – login Git: `KarolZegartowski`  
**Data oddania:** [24.11.2026]  

---

## 1. Cel i Zakres Inżynierski Zadania
Zadanie ma na celu zaimplementowanie silnika SQLite, schematu DDL oraz relacji 1:N. Zostalo zrobione repozytorium realizujące zapis i odczyt agregatu.

---

## 2. Architektura Rozwiązania i Struktura Modułów
*(Wykaz zrealizowanych plików w katalogu `src/` wraz z przypisaniem ich odpowiedzialności).*
* `src/validators.py` – Walidacja danych/obsluga bledow.
* `src/services.py` – Wartswa aplikacji pośrednicząca między interfejsem a bazą danych i logiką.
* `src/main.py` – Glówny plik wykonawczy
* `src/database.py` – Dostęp do relacyjnej bazy danych
* `src/manager.py` – Logika zarządzania kontem
* `src/migrate.py` – Skrypt migracyjny
* `src/models.py` – Klasy domenowe
* `src/storage.py` – Zapis transakcji, eksport do CSV
* `src/test-database.py` – Automatyczne testy wykonanych zmian


---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie
*(Wybrany, najważniejszy lub najciekawszy fragment kodu źródłowego zrealizowany w tym etapie – maksymalnie 15–25 linii).*

```python
# Wklej tutaj kluczowy fragment kodu źródłowego
def example_function():
    pass
```

**Uzasadnienie wyboru:**  
*(Krótkie wyjaśnienie: dlaczego zaimplementowano to w taki sposób, jak obsłużono błędy lub jakie wzorce projektowe zastosowano).*

---

## 4. Scenariusze Weryfikacji i Wyniki Testów
*(Dowód działania programu w konsoli. Należy przedstawić przynajmniej dwa scenariusze).*

### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** [Opis danych]
* **Oczekiwany i uzyskany wynik:**
```text
[Wklej listing z konsoli lub opis poprawnego zachowania]
```

### Scenariusz B: Obsługa błędów i wartości brzegowych
* **Dane wejściowe (błędne):** [np. litery zamiast cyfr, puste wejście, wartość spoza zakresu]
* **Reakcja programu:**
```text
[Wklej listing z konsoli pokazujący bezpieczną reakcję na błąd]
```

---

## 5. Podział Pracy w Zespole
*(Precyzyjne i uczciwe rozliczenie wkładu obu członków zespołu – weryfikowane z historią commitów `git log`).*
* **[Oskar Ogonek]:**
  * Odpowiedzialność za moduły: `src/migrate.py, database.py`
  * Zaimplementowane funkcjonalności: [Zamknięcie wszystkich zapytań w pliku database, jednorazowy transfer z JSON do SQLite.]
  * Liczba wykonanych commitów: [1]
* **[Karol Zegartowski]:**
  * Odpowiedzialność za moduły: `src/models.py, storage.py, services.py`
  * Zaimplementowane funkcjonalności: [Przelaczenie magazynu aplikacji na SQLite, metody wydatek i przychód]
  * Liczba wykonanych commitów: [1]
