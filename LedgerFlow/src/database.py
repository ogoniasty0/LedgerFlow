import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from manager import LedgerManager
from models import ExpenseTransaction, IncomeTransaction, Transaction

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "ledgerflow.db"

ALLOWED_SORT_COLS: set[str] = {"tx_id", "tx_date", "category", "amount_pln", "tx_type"}
ALLOWED_SORT_DIRS: set[str] = {"ASC", "DESC"}

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
    """Fabryka połączeń konfigurująca integralność kluczy obcych i format wyników."""
    db_target = str(db_path)
    if db_target != ":memory:":
        Path(db_target).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_target)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


class LedgerRepository:
    """Repozytorium hermetyzujące operacje SQL dla agregatu Konto -> Transakcje (1:N)."""

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

    def create_account(self, account_name: str, initial_balance_pln: float = 0.0) -> int:
        """Tworzy nowy rachunek w tabeli accounts i zwraca jego account_id."""
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO accounts (account_name, initial_balance_pln) VALUES (?, ?);",
                (account_name, float(initial_balance_pln)),
            )
            return int(cur.lastrowid)

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

    def search_transactions(
        self,
        category_phrase: str = "",
        tx_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        min_amount: float = 0.0,
        account_id: int | None = None,
        sort_by: str = "tx_date",
        sort_dir: str = "DESC",
    ) -> list[dict[str, Any]]:
        """
        Wielokryterialne wyszukiwanie transakcji z 100% parametryzacją (:klucz)
        oraz walidacją sortowania białą listą (ochrona przed SQL Injection).
        """
        sort_dir_clean = sort_dir.strip().upper()
        if sort_by not in ALLOWED_SORT_COLS:
            raise ValueError(f"Niedozwolona kolumna sortowania: {sort_by}")
        if sort_dir_clean not in ALLOWED_SORT_DIRS:
            raise ValueError(f"Niedozwolony kierunek sortowania: {sort_dir}")

        conditions: list[str] = ["t.amount_pln >= :min_amount"]
        params: dict[str, Any] = {"min_amount": float(min_amount)}

        if category_phrase.strip():
            conditions.append("t.category LIKE :category_pattern")
            params["category_pattern"] = f"%{category_phrase.strip()}%"

        if tx_type is not None and tx_type.strip():
            conditions.append("t.tx_type = :tx_type")
            params["tx_type"] = tx_type.strip().upper()

        if date_from is not None and date_from.strip():
            conditions.append("t.tx_date >= :date_from")
            params["date_from"] = date_from.strip()

        if date_to is not None and date_to.strip():
            conditions.append("t.tx_date <= :date_to")
            params["date_to"] = date_to.strip()

        if account_id is not None:
            conditions.append("t.account_id = :account_id")
            params["account_id"] = int(account_id)

        where_clause = " AND ".join(conditions)
        sql = f"""
            SELECT
                t.tx_id,
                t.account_id,
                a.account_name,
                t.tx_date,
                t.category,
                t.amount_pln,
                t.tx_type,
                t.operator_fee,
                t.source,
                t.tax_pct
            FROM transactions AS t
            INNER JOIN accounts AS a ON t.account_id = a.account_id
            WHERE {where_clause}
            ORDER BY t.{sort_by} {sort_dir_clean};
        """
        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def get_accounts_balance_report(self, min_balance: float = 0.0) -> list[dict[str, Any]]:
        """
        Analityka JOIN #1: Bilans każdego konta łączący initial_balance_pln
        z sumą przychodów i wydatków (LEFT JOIN + CASE WHEN + COALESCE + GROUP BY + HAVING).
        """
        sql = """
            SELECT
                a.account_id,
                a.account_name,
                a.initial_balance_pln,
                COUNT(t.tx_id) AS tx_count,
                ROUND(
                    COALESCE(
                        SUM(CASE WHEN t.tx_type = 'PRZYCHOD' THEN t.amount_pln * (1.0 - t.tax_pct / 100.0) ELSE 0.0 END),
                        0.0
                    ),
                    2
                ) AS total_income_net,
                ROUND(
                    COALESCE(
                        SUM(CASE WHEN t.tx_type = 'WYDATEK' THEN (t.amount_pln + t.operator_fee) ELSE 0.0 END),
                        0.0
                    ),
                    2
                ) AS total_expense_net,
                ROUND(
                    a.initial_balance_pln
                    + COALESCE(
                        SUM(CASE WHEN t.tx_type = 'PRZYCHOD' THEN t.amount_pln * (1.0 - t.tax_pct / 100.0) ELSE 0.0 END),
                        0.0
                    )
                    - COALESCE(
                        SUM(CASE WHEN t.tx_type = 'WYDATEK' THEN (t.amount_pln + t.operator_fee) ELSE 0.0 END),
                        0.0
                    ),
                    2
                ) AS current_balance_pln
            FROM accounts AS a
            LEFT JOIN transactions AS t ON a.account_id = t.account_id
            GROUP BY a.account_id, a.account_name, a.initial_balance_pln
            HAVING current_balance_pln >= :min_balance
            ORDER BY current_balance_pln DESC;
        """
        rows = self._conn.execute(sql, {"min_balance": float(min_balance)}).fetchall()
        return [dict(r) for r in rows]

    def get_expenses_by_category(self, min_spent: float = 0.0) -> list[dict[str, Any]]:
        sql = """
            SELECT
                t.category,
                COUNT(t.tx_id) AS tx_count,
                ROUND(COALESCE(SUM(t.amount_pln + t.operator_fee), 0.0), 2) AS total_spent_pln,
                ROUND(COALESCE(AVG(t.amount_pln + t.operator_fee), 0.0), 2) AS avg_spent_pln
            FROM transactions AS t
            INNER JOIN accounts AS a ON t.account_id = a.account_id
            WHERE t.tx_type = 'WYDATEK'
            GROUP BY t.category
            HAVING total_spent_pln >= :min_spent
            ORDER BY total_spent_pln DESC;
        """
        rows = self._conn.execute(sql, {"min_spent": float(min_spent)}).fetchall()
        return [dict(r) for r in rows]

    def transfer_funds(
        self,
        from_account_id: int,
        to_account_id: int,
        amount_pln: float,
        category: str = "Przelew wewnętrzny",
        tx_date: str | None = None,
    ) -> tuple[int, int]:
        """
        Atomowy przelew między dwoma rachunkami (zapis wydatku i przychodu w jednej transakcji ACID).
        Błąd na dowolnym etapie (np. brak konta docelowego -> IntegrityError lub brak środków -> ValueError)
        wyzwala automatyczny ROLLBACK.
        """
        if amount_pln <= 0.0:
            raise ValueError("Kwota przelewu musi być większa od zera.")
        if from_account_id == to_account_id:
            raise ValueError("Konto źródłowe i docelowe muszą być różne.")

        effective_date = tx_date if tx_date else datetime.now().strftime("%Y-%m-%d")
        clean_amount = round(float(amount_pln), 2)

        with self._conn:
            src_row = self._conn.execute(
                """
                SELECT
                    a.account_id,
                    ROUND(
                        a.initial_balance_pln
                        + COALESCE(
                            SUM(CASE WHEN t.tx_type = 'PRZYCHOD' THEN t.amount_pln * (1.0 - t.tax_pct / 100.0) ELSE 0.0 END),
                            0.0
                        )
                        - COALESCE(
                            SUM(CASE WHEN t.tx_type = 'WYDATEK' THEN (t.amount_pln + t.operator_fee) ELSE 0.0 END),
                            0.0
                        ),
                        2
                    ) AS balance
                FROM accounts AS a
                LEFT JOIN transactions AS t ON a.account_id = t.account_id
                WHERE a.account_id = ?
                GROUP BY a.account_id, a.initial_balance_pln;
                """,
                (from_account_id,),
            ).fetchone()

            if src_row is None:
                raise ValueError(f"Konto źródłowe o ID {from_account_id} nie istnieje.")
            if float(src_row["balance"]) < clean_amount:
                raise ValueError(
                    f"Niewystarczające środki na koncie źródłowym (dostępne: {src_row['balance']:.2f} PLN)."
                )

            cur_out = self._conn.execute(
                """
                INSERT INTO transactions (
                    account_id, tx_date, category, amount_pln, tx_type,
                    operator_fee, source, tax_pct
                ) VALUES (?, ?, ?, ?, 'WYDATEK', 0.0, 'Inne', 0.0);
                """,
                (from_account_id, effective_date, category, clean_amount),
            )
            out_tx_id = int(cur_out.lastrowid)

            cur_in = self._conn.execute(
                """
                INSERT INTO transactions (
                    account_id, tx_date, category, amount_pln, tx_type,
                    operator_fee, source, tax_pct
                ) VALUES (?, ?, ?, ?, 'PRZYCHOD', 0.0, ?, 0.0);
                """,
                (to_account_id, effective_date, category, clean_amount, f"Przelew z konta #{from_account_id}"),
            )
            in_tx_id = int(cur_in.lastrowid)

        return out_tx_id, in_tx_id