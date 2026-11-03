# Sprawozdanie z Zadania Laboratoryjnego nr 2
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
    **Projekt:** LedgerFlow
**Zespół (Autorzy):**  
1. Oskar Ogonek (nr albumu: 164856) – login Git: `ogoniasty0`
2. Karol Zegartowski (nr albumu: 164892) – login Git: `KarolZegartowski`  
**Data oddania:** [27.10.2026r]  

---

## 1. Cel i Zakres Inżynierski Zadania
Celem zadania jest dodanie obslugi bezpiecznego zapisu, importu danych z pliku json i eksportowanie csv.

---

## 2. Architektura Rozwiązania i Struktura Modułów
* `src/validators.py` – Obsluga blędów
* `src/services.py` – Wszystkie funkcje programu
* `src/main.py` – Główny plik programu zawierający menu
* `src/storage.py` - Plik przechowujący funkcje odpowiedzialne za atomowy zapis, eksport do csv i tworzenie kopii zapasowych.



---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie
*(Wybrany, najważniejszy lub najciekawszy fragment kodu źródłowego zrealizowany w tym etapie – maksymalnie 15–25 linii).*

```python
except json.JSONDecodeError:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupted_path = DATA_DIR / f"corrupted_{stamp}.json"
        
        if TRANSACTIONS_FILE.exists():
            os.replace(TRANSACTIONS_FILE, corrupted_path)
            print(f"Uszkodzony plik JSON! Kwarantanna: {corrupted_path.name}")

        backups = sorted(BACKUP_DIR.glob("transactions_*.bak"))
        if backups:
            latest_backup = backups[-1]
            print(f"Przywracanie bazy z kopii: {latest_backup.name}")
            try:
                with open(latest_backup, mode="r", encoding="utf-8") as f:
                    restored_data = json.load(f)
                    save_transactions(restored_data)
                    return restored_data
            except (json.JSONDecodeError, FileNotFoundError):
                print("Kopia zapasowa również uszkodzona!")

        print("Start danymi bazowymi.")
        save_transactions(SEED_DATA)
        return [dict(item) for item in SEED_DATA]

```

**Uzasadnienie wyboru:**  
Funkcja sprawdza czy plik JSON istnieje i jest sprawny, jeśli nie, zapisuje jego aktualny stan do kwarantanny, a potem podmienia jego zawartość na najnowszą kopie zapasową.



## 4. Scenariusze Weryfikacji i Wyniki Testów

Po wyeksportowaniu listy transakcji poprawnie tworzy się plik csv.

### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** Poprawne dodanie rekordu do tabeli
* **Oczekiwany i uzyskany wynik:**
```
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
  * Odpowiedzialność za moduły: `src/storage.py`
  * Zaimplementowane funkcjonalności: Zapis atomowy, automatyczna kopia zapasowa, regeneracja bazy danych.
  * Liczba wykonanych commitów: 2
* **Oskar Ogonek:**
  * Odpowiedzialność za moduły: `src/storage.py`
  * Zaimplementowane funkcjonalności: Import z JSON i eksport do CSV.
  * Liczba wykonanych commitów: 2

