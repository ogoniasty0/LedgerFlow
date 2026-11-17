import sqlite3
from pathlib import Path

from manager import LedgerManager
from models import ExpenseTransaction, IncomeTransaction, Transaction

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "ledgerflow.db"

DDL_ACCOUNTS = """
CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_name TEXT NOT NULL,
    initial_balance_pln REAL NOT NULL DEFAULT 0.0
);
"""

DDL_TRANSACTIONS = """
CREATE TABLE IF NOT EXISTS transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    tx_date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount_pln REAL NOT NULL CHECK (amount_pln > 0.0),
    tx_type TEXT NOT NULL CHECK (tx_type IN ('PRZYCHOD', 'WYDATEK')),
    operator_fee REAL NOT NULL DEFAULT 0.0 CHECK (operator_fee >= 0.0),
    source TEXT NOT NULL DEFAULT 'Inne',
    tax_pct REAL NOT NULL DEFAULT 0.0 CHECK (tax_pct BETWEEN 0.0 AND 100.0),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);
"""


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_target = str(db_path)
    if db_target != ":memory:":
        Path(db_target).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_target)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


class LedgerRepository:

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self.init_schema()

    def init_schema(self) -> None:
        with self._conn:
            self._conn.execute(DDL_ACCOUNTS)
            self._conn.execute(DDL_TRANSACTIONS)

    def _extract_tx_params(self, account_id: int, tx: Transaction) -> tuple:
        operator_fee = tx.operator_fee if isinstance(tx, ExpenseTransaction) else 0.0
        source = tx.source if isinstance(tx, IncomeTransaction) else "Inne"
        tax_pct = tx.tax_pct if isinstance(tx, IncomeTransaction) else 0.0
        return (
            account_id,
            tx.tx_date,
            tx.category,
            tx.amount_pln,
            tx.tx_type,
            operator_fee,
            source,
            tax_pct,
        )

    def _row_to_transaction(self, row: sqlite3.Row) -> Transaction:
        data = dict(row)
        if data["tx_type"] == "WYDATEK":
            return ExpenseTransaction(
                tx_id=int(data["tx_id"]),
                category=str(data["category"]),
                amount_pln=float(data["amount_pln"]),
                operator_fee=float(data.get("operator_fee", 0.0)),
                tx_date=str(data["tx_date"]),
            )
        if data["tx_type"] == "PRZYCHOD":
            return IncomeTransaction(
                tx_id=int(data["tx_id"]),
                category=str(data["category"]),
                amount_pln=float(data["amount_pln"]),
                source=str(data.get("source", "Inne")),
                tax_pct=float(data.get("tax_pct", 0.0)),
                tx_date=str(data["tx_date"]),
            )
        raise ValueError(f"Nieznany typ transakcji w bazie SQLite: {data['tx_type']!r}")

    def save_account_with_transactions(self, manager: LedgerManager) -> int:
        """Transakcyjny zapis konta nadrzędnego wraz z kolekcją jego transakcji."""
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO accounts (account_name, initial_balance_pln) VALUES (?, ?);",
                (manager.account_name, manager.initial_balance),
            )
            account_id: int = int(cur.lastrowid)

            if manager.transactions:
                payload = [self._extract_tx_params(account_id, tx) for tx in manager.transactions]
                self._conn.executemany(
                    """
                    INSERT INTO transactions (
                        account_id, tx_date, category, amount_pln, tx_type,
                        operator_fee, source, tax_pct
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    payload,
                )
        return account_id

    def add_transaction(self, account_id: int, tx: Transaction) -> int:
        """Dodaje pojedynczą transakcję do wskazanego konta i aktualizuje jej tx_id."""
        with self._conn:
            cur = self._conn.execute(
                """
                INSERT INTO transactions (
                    account_id, tx_date, category, amount_pln, tx_type,
                    operator_fee, source, tax_pct
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                self._extract_tx_params(account_id, tx),
            )
            new_id = int(cur.lastrowid)
            tx.tx_id = new_id
            return new_id

    def get_account(self, account_id: int) -> LedgerManager | None:
        """Odczytuje konto oraz powiązane z nim transakcje i buduje obiekt LedgerManager."""
        acc_row = self._conn.execute(
            "SELECT account_id, account_name, initial_balance_pln FROM accounts WHERE account_id = ?;",
            (account_id,),
        ).fetchone()

        if acc_row is None:
            return None

        tx_rows = self._conn.execute(
            """
            SELECT tx_id, account_id, tx_date, category, amount_pln, tx_type,
                   operator_fee, source, tax_pct
            FROM transactions
            WHERE account_id = ?
            ORDER BY tx_id ASC;
            """,
            (account_id,),
        ).fetchall()

        transactions = [self._row_to_transaction(row) for row in tx_rows]
        return LedgerManager(
            account_name=str(acc_row["account_name"]),
            initial_balance=float(acc_row["initial_balance_pln"]),
            transactions=transactions,
        )

    def get_first_account_id(self) -> int | None:
        row = self._conn.execute(
            "SELECT account_id FROM accounts ORDER BY account_id ASC LIMIT 1;"
        ).fetchone()
        return int(row["account_id"]) if row is not None else None

    def delete_account(self, account_id: int) -> bool:
        """Usuwa konto nadrzędne (ON DELETE CASCADE usuwa powiązane transakcje)."""
        with self._conn:
            cur = self._conn.execute(
                "DELETE FROM accounts WHERE account_id = ?;",
                (account_id,),
            )
            return cur.rowcount > 0

    def count_accounts(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS cnt FROM accounts;").fetchone()
        return int(row["cnt"])

    def count_transactions(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS cnt FROM transactions;").fetchone()
        return int(row["cnt"])