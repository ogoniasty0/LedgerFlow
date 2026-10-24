import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"

DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

SEED_DATA = [
   {"id": 1, "category": "Zakupy", "amount": 256.0, "type": "wydatek"},
   {"id": 2, "category": "Wypłata", "amount": 5000.0, "type": "dochód"}
]

def load_transactions() -> list[dict]:
    try:
        with open(TRANSACTIONS_FILE, mode="r", encoding="utf-8") as f:
            return json.load(f)
            
    except FileNotFoundError:
        save_transactions(SEED_DATA)
        nowa_lista = []
        for item in SEED_DATA:
            nowa_lista.append(dict(item))
        return nowa_lista
        
    except json.JSONDecodeError:
        print("Błąd: Uszkodzony plik JSON. Ładuję dane awaryjne.")
        nowa_lista = []
        for item in SEED_DATA:
            nowa_lista.append(dict(item))
        return nowa_lista

def save_transactions(transactions: list[dict]) -> None:
    with open(TRANSACTIONS_FILE, mode="w", encoding="utf-8") as f:
        json.dump(transactions, f, indent=4, ensure_ascii=False)

def export_to_csv(transactions: list[dict]) -> int:
    target_path = EXPORTS_DIR / "ledger_export.csv"
    if len(transactions) == 0:
        return 0
    
    fields = ["id", "category", "amount", "type"]
    
    with open(target_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(transactions)
        
    return len(transactions)