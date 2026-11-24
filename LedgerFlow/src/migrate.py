import json
from pathlib import Path

from database import DEFAULT_DB_PATH, LedgerRepository, get_connection
from manager import LedgerManager

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_JSON_PATH = BASE_DIR / "data" / "transactions.json"


def migrate_json_to_sqlite(
    db_path: str | Path = DEFAULT_DB_PATH,
    json_path: str | Path = DEFAULT_JSON_PATH,
) -> bool:
    
    source_json = Path(json_path)
    conn = get_connection(db_path)

    try:
        repo = LedgerRepository(conn)

        if repo.count_accounts() > 0:
            return False

        if not source_json.exists():
            return False

        with open(source_json, mode="r", encoding="utf-8") as f:
            raw_data = json.load(f)

        manager = LedgerManager.from_dict(raw_data)

        repo.save_account_with_transactions(manager)

        backup_path = source_json.with_suffix(".json.bak")
        source_json.replace(backup_path)
        print(f"Przeniesiono dane do SQLite. Archiwum JSON: {backup_path.name}")
        return True
    finally:
        conn.close()


if __name__ == "__main__":
    migrated = migrate_json_to_sqlite()
    if not migrated:
        print("Pominięto (baza zawiera już dane lub brak pliku transactions.json).")