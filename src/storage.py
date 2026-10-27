import json
import csv
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
BACKUP_DIR = DATA_DIR / "backups"

DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

SEED_DATA = [
   {"id": 1, "category": "Zakupy", "amount": 256.0, "type": "wydatek"},
   {"id": 2, "category": "Wypłata", "amount": 5000.0, "type": "dochód"}
]

def create_backup(max_backups: int = 3) -> Path | None:
    if not TRANSACTIONS_FILE.exists():
        return None
    
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"transactions_{stamp}.bak"
    shutil.copy2(TRANSACTIONS_FILE, backup_path)
    
    existing_backups = sorted(BACKUP_DIR.glob("transactions_*.bak"))
    while len(existing_backups) > max_backups:
        oldest_backup = existing_backups.pop(0)
        oldest_backup.unlink(missing_ok=True)
        
    return backup_path

def save_transactions(transactions: list[dict]) -> None:
    create_backup(max_backups=3)
    
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=DATA_DIR,
        prefix="trans_tmp_",
        suffix=".json",
        delete=False,
        encoding="utf-8"
    ) as tmp:
        json.dump(transactions, tmp, indent=4, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = Path(tmp.name)
        
    os.replace(temp_path, TRANSACTIONS_FILE)

def load_transactions() -> list[dict]:
    try:
        with open(TRANSACTIONS_FILE, mode="r", encoding="utf-8") as f:
            return json.load(f)
            
    except FileNotFoundError:
        save_transactions(SEED_DATA)
        return [dict(item) for item in SEED_DATA]
        
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

def export_to_csv(transactions: list[dict]) -> int:
    target_path = EXPORTS_DIR / "ledger_export.csv"
    if not transactions:
        return 0
    
    fields = ["id", "category", "amount", "type"]
    with open(target_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(transactions)
        
    return len(transactions)