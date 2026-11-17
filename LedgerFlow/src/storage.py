import csv
from pathlib import Path

from database import DEFAULT_DB_PATH, LedgerRepository, get_connection
from manager import LedgerManager
from migrate import migrate_json_to_sqlite
from models import ExpenseTransaction, IncomeTransaction, Transaction

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"

DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

LEDGER_FILE = DATA_DIR / "transactions.json"


def get_seed_manager() -> LedgerManager:
    tx1 = ExpenseTransaction(1, "Zakupy Spozywcze", 150.0, operator_fee=2.50)
    tx2 = IncomeTransaction(2, "Wyplata", 4000.0, source="Etat", tax_pct=12.0)
    return LedgerManager("Główne Konto Domowe", initial_balance=500.0, transactions=[tx1, tx2])


def load_manager() -> LedgerManager:
    # Automatyczna, idempotentna migracja ze starego pliku JSON (jeśli istnieje)
    migrate_json_to_sqlite(db_path=DEFAULT_DB_PATH, json_path=LEDGER_FILE)

    conn = get_connection(DEFAULT_DB_PATH)
    try:
        repo = LedgerRepository(conn)
        account_id = repo.get_first_account_id()

        if account_id is None:
            seed = get_seed_manager()
            account_id = repo.save_account_with_transactions(seed)

        loaded = repo.get_account(account_id)
        if loaded is None:
            raise RuntimeError("Nie udało się wczytać konta z bazy danych SQLite.")
        return loaded
    finally:
        conn.close()


def persist_new_transaction(tx: Transaction) -> int:
    conn = get_connection(DEFAULT_DB_PATH)
    try:
        repo = LedgerRepository(conn)
        account_id = repo.get_first_account_id()
        if account_id is None:
            raise RuntimeError("Brak konta nadrzędnego w bazie danych.")
        return repo.add_transaction(account_id, tx)
    finally:
        conn.close()


def export_to_csv(manager: LedgerManager) -> int:
    target_path = EXPORTS_DIR / "ledger_export.csv"
    txs = manager.transactions
    if not txs:
        return 0

    fields = ["tx_id", "tx_date", "type", "category", "amount_pln", "net_impact"]
    with open(target_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for tx in txs:
            writer.writerow({
                "tx_id": tx.tx_id,
                "tx_date": tx.tx_date,
                "type": tx.to_dict()["type"],
                "category": tx.category,
                "amount_pln": tx.amount_pln,
                "net_impact": tx.net_balance_impact()
            })
    return len(txs)