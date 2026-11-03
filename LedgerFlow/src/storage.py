import json
import csv
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from models import Account, Transaction

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
BACKUP_DIR = DATA_DIR / "backups"

DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNT_FILE = DATA_DIR / "transactions.json"

def get_seed_account() -> Account:
    tx1 = Transaction(1, "Zakupy", 256.0, "WYDATEK")
    tx2 = Transaction(2, "Wypłata", 5000.0, "PRZYCHOD")
    return Account(account_name="Główne Konto Domowe", initial_balance=1000.0, transactions=[tx1, tx2])

def create_backup(max_backups: int = 3) -> Path | None:
    if not ACCOUNT_FILE.exists():
        return None
    
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"transactions_{stamp}.bak"
    shutil.copy2(ACCOUNT_FILE, backup_path)
    
    existing_backups = sorted(BACKUP_DIR.glob("transactions_*.bak"))
    while len(existing_backups) > max_backups:
        oldest_backup = existing_backups.pop(0)
        oldest_backup.unlink(missing_ok=True)
        
    return backup_path

def save_account(account: Account) -> None:
    create_backup(max_backups=3)
    
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=DATA_DIR,
        prefix="trans_tmp_",
        suffix=".json",
        delete=False,
        encoding="utf-8"
    ) as tmp:
        json.dump(account.to_dict(), tmp, indent=4, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = Path(tmp.name)
        
    os.replace(temp_path, ACCOUNT_FILE)

def load_account() -> Account:
    try:
        with open(ACCOUNT_FILE, mode="r", encoding="utf-8") as f:
            raw_data = json.load(f)
            if isinstance(raw_data, list):
                txs = [Transaction.from_dict(item) for item in raw_data]
                acc = Account("Główne Konto Domowe", initial_balance=1000.0, transactions=txs)
                save_account(acc)
                return acc
            return Account.from_dict(raw_data)
            
    except FileNotFoundError:
        seed_acc = get_seed_account()
        save_account(seed_acc)
        return seed_acc
        
    except (json.JSONDecodeError, KeyError, ValueError):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupted_path = DATA_DIR / f"corrupted_{stamp}.json"
        
        if ACCOUNT_FILE.exists():
            os.replace(ACCOUNT_FILE, corrupted_path)
            print(f"[OSTRZEŻENIE] Uszkodzona baza! Kwarantanna: {corrupted_path.name}")

        backups = sorted(BACKUP_DIR.glob("transactions_*.bak"))
        if backups:
            latest_backup = backups[-1]
            print(f"[INFO] Odzyskiwanie bazy z kopii: {latest_backup.name}")
            try:
                with open(latest_backup, mode="r", encoding="utf-8") as f:
                    restored_acc = Account.from_dict(json.load(f))
                    save_account(restored_acc)
                    return restored_acc
            except Exception:
                print("[BŁĄD] Kopia zapasowa uległa uszkodzeniu!")

        seed_acc = get_seed_account()
        save_account(seed_acc)
        return seed_acc

def export_to_csv(account: Account) -> int:
    target_path = EXPORTS_DIR / "ledger_export.csv"
    transactions = account.transactions
    if not transactions:
        return 0
    
    fields = ["tx_id", "category", "amount_pln", "tx_type"]
    with open(target_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for tx in transactions:
            writer.writerow(tx.to_dict())
        
    return len(transactions)