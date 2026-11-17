import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import LedgerRepository, get_connection
from manager import LedgerManager
from migrate import migrate_json_to_sqlite
from models import ExpenseTransaction, IncomeTransaction


class TestLedgerDatabase(unittest.TestCase):
    """Zestaw autotestów weryfikujących schemat DDL, integralność relacji 1:N i migrację."""

    def setUp(self) -> None:
        # Izolowana baza w pamięci RAM (:memory:) dla każdego testu
        self.conn = get_connection(":memory:")
        self.repo = LedgerRepository(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_01_ddl_schema_and_cascade_definition(self) -> None:
        """1. Weryfikacja utworzenia 2 tabel oraz klucza obcego z ON DELETE CASCADE."""
        tables_rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('accounts', 'transactions');"
        ).fetchall()
        table_names = {row["name"] for row in tables_rows}
        self.assertEqual(table_names, {"accounts", "transactions"})

        fk_rows = self.conn.execute("PRAGMA foreign_key_list(transactions);").fetchall()
        self.assertEqual(len(fk_rows), 1)
        fk = dict(fk_rows[0])
        self.assertEqual(fk["table"], "accounts")
        self.assertEqual(fk["from"], "account_id")
        self.assertEqual(fk["to"], "account_id")
        self.assertEqual(fk["on_delete"].upper(), "CASCADE")

    def test_02_foreign_key_integrity_error(self) -> None:
        """2. Próba wstawienia transakcji z nieistniejącym account_id musi rzucić IntegrityError."""
        fk_status = self.conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        self.assertEqual(fk_status, 1)

        orphan_tx = ExpenseTransaction(1, "Jedzenie", 50.0, operator_fee=0.0, tx_date="2026-11-17")
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.add_transaction(account_id=9999, tx=orphan_tx)

    def test_03_check_constraints_integrity_error(self) -> None:
        """Dodatkowa weryfikacja więzów CHECK na poziomie silnika SQLite."""
        manager = LedgerManager("Konto Testowe", initial_balance=1000.0)
        account_id = self.repo.save_account_with_transactions(manager)

        # Niepoprawny typ transakcji (spoza 'PRZYCHOD', 'WYDATEK')
        with self.assertRaises(sqlite3.IntegrityError):
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO transactions (account_id, tx_date, category, amount_pln, tx_type)
                    VALUES (?, '2026-11-17', 'Test', 100.0, 'PRZELEW');
                    """,
                    (account_id,),
                )

        # Niepoprawna kwota (amount_pln <= 0)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO transactions (account_id, tx_date, category, amount_pln, tx_type)
                    VALUES (?, '2026-11-17', 'Test', -10.0, 'WYDATEK');
                    """,
                    (account_id,),
                )

    def test_04_repository_save_and_read_aggregate(self) -> None:
        """3. Zapis agregatu nadrzędnego wraz z transakcjami i jego odczyt przez repozytorium."""
        tx1 = ExpenseTransaction(1, "Czynsz", 1200.0, operator_fee=5.0, tx_date="2026-11-01")
        tx2 = IncomeTransaction(2, "Wynagrodzenie", 5000.0, source="Etat", tax_pct=12.0, tx_date="2026-11-10")
        original = LedgerManager("Budżet Rodzinny", initial_balance=300.0, transactions=[tx1, tx2])

        account_id = self.repo.save_account_with_transactions(original)
        restored = self.repo.get_account(account_id)

        self.assertIsNotNone(restored)
        assert restored is not None
        self.assertEqual(restored.account_name, "Budżet Rodzinny")
        self.assertEqual(restored.initial_balance, 300.0)
        self.assertEqual(len(restored.transactions), 2)
        self.assertIsInstance(restored.transactions[0], ExpenseTransaction)
        self.assertIsInstance(restored.transactions[1], IncomeTransaction)
        self.assertEqual(restored.calculate_total_balance(), original.calculate_total_balance())

    def test_05_on_delete_cascade(self) -> None:
        """4. Usunięcie konta nadrzędnego automatycznie czyści powiązane transakcje (COUNT == 0)."""
        tx1 = ExpenseTransaction(1, "Kawa", 18.0, tx_date="2026-11-15")
        tx2 = ExpenseTransaction(2, "Książka", 65.0, tx_date="2026-11-16")
        manager = LedgerManager("Konto do usunięcia", initial_balance=500.0, transactions=[tx1, tx2])

        account_id = self.repo.save_account_with_transactions(manager)
        self.assertEqual(self.repo.count_accounts(), 1)
        self.assertEqual(self.repo.count_transactions(), 2)

        deleted = self.repo.delete_account(account_id)
        self.assertTrue(deleted)
        self.assertEqual(self.repo.count_accounts(), 0)
        self.assertEqual(self.repo.count_transactions(), 0)

    def test_06_json_to_sqlite_migration(self) -> None:
        """5. Skrypt migracyjny przenosi rekordy z pliku JSON do SQLite i archiwizuje JSON."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            json_path = tmp_path / "transactions.json"
            db_path = tmp_path / "ledgerflow.db"

            sample_json = {
                "account_name": "Konto z Zadania 3",
                "initial_balance": 250.0,
                "transactions": [
                    {
                        "type": "expense",
                        "tx_id": 1,
                        "category": "Transport",
                        "amount_pln": 45.0,
                        "operator_fee": 0.0,
                    },
                    {
                        "type": "income",
                        "tx_id": 2,
                        "category": "Premia",
                        "amount_pln": 1000.0,
                        "source": "Projekt",
                        "tax_pct": 10.0,
                    },
                ],
            }
            json_path.write_text(json.dumps(sample_json, ensure_ascii=False), encoding="utf-8")

            # Pierwsze uruchomienie -> przenosi dane i zmienia nazwę pliku na .json.bak
            first_run = migrate_json_to_sqlite(db_path=db_path, json_path=json_path)
            self.assertTrue(first_run)
            self.assertFalse(json_path.exists())
            self.assertTrue((tmp_path / "transactions.json.bak").exists())

            # Weryfikacja zawartości bazy SQLite
            migrated_conn = get_connection(db_path)
            try:
                migrated_repo = LedgerRepository(migrated_conn)
                self.assertEqual(migrated_repo.count_accounts(), 1)
                self.assertEqual(migrated_repo.count_transactions(), 2)
                acc_id = migrated_repo.get_first_account_id()
                assert acc_id is not None
                loaded_manager = migrated_repo.get_account(acc_id)
                assert loaded_manager is not None
                self.assertEqual(loaded_manager.account_name, "Konto z Zadania 3")
                self.assertEqual(loaded_manager.calculate_total_balance(), 1105.0)
            finally:
                migrated_conn.close()

            # Drugie uruchomienie -> idempotentność (brak duplikatów)
            second_run = migrate_json_to_sqlite(db_path=db_path, json_path=json_path)
            self.assertFalse(second_run)


if __name__ == "__main__":
    unittest.main(verbosity=2)