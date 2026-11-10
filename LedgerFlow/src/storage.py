import json
import csv
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from manager import LedgerManager
from models import ExpenseTransaction, IncomeTransaction

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
BACKUP_DIR = DATA_DIR / "backups"

DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

LEDGER_FILE = DATA_DIR / "transactions.json"

def get_seed_manager() -> LedgerManager:
    tx1 = ExpenseTransaction(1, "Zakupy Spozywcze", 150.0, operator_fee=2.50)
    tx2 = IncomeTransaction(2, "Wyplata", 4000.0, source="Etat", tax_pct=12.0)
    return LedgerManager("Główne Konto Domowe", initial_balance=500.0, transactions=[tx1, tx2])

def create_backup(max_backups: int = 3) -> Path | None:
    if not LEDGER_FILE.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"transactions_{stamp}.bak"
    shutil.copy2(LEDGER_FILE, backup_path)
    
    existing_backups = sorted(BACKUP_DIR.glob("transactions_*.bak"))
    while len(existing_backups) > max_backups:
        oldest = existing_backups.pop(0)
        oldest.unlink(missing_ok=True)
    return backup_path

def save_manager(manager: LedgerManager) -> None:
    create_backup(max_backups=3)
    with tempfile.NamedTemporaryFile(mode="w", dir=DATA_DIR, prefix="trans_tmp_", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(manager.to_dict(), tmp, indent=4, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = Path(tmp.name)
    os.replace(temp_path, LEDGER_FILE)

def load_manager() -> LedgerManager:
    try:
        with open(LEDGER_FILE, mode="r", encoding="utf-8") as f:
            raw_data = json.load(f)
            return LedgerManager.from_dict(raw_data)
    except FileNotFoundError:
        seed = get_seed_manager()
        save_manager(seed)
        return seed
    except Exception:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupted_path = DATA_DIR / f"corrupted_{stamp}.json"
        if LEDGER_FILE.exists():
            os.replace(LEDGER_FILE, corrupted_path)
            print(f"[OSTRZEŻENIE] Kwarantanna uszkodzonej bazy: {corrupted_path.name}")

        backups = sorted(BACKUP_DIR.glob("transactions_*.bak"))
        if backups:
            try:
                with open(backups[-1], mode="r", encoding="utf-8") as f:
                    restored = LedgerManager.from_dict(json.load(f))
                    save_manager(restored)
                    return restored
            except Exception:
                pass

        seed = get_seed_manager()
        save_manager(seed)
        return seed

def export_to_csv(manager: LedgerManager) -> int:
    target_path = EXPORTS_DIR / "ledger_export.csv"
    txs = manager.transactions
    if not txs:
        return 0
    
    fields = ["tx_id", "type", "category", "amount_pln", "net_impact"]
    with open(target_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for tx in txs:
            writer.writerow({
                "tx_id": tx.tx_id,
                "type": tx.to_dict()["type"],
                "category": tx.category,
                "amount_pln": tx.amount_pln,
                "net_impact": tx.net_balance_impact()
            })
    return len(txs)