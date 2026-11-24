import sqlite3
import unittest

from database import LedgerRepository, get_connection
from manager import LedgerManager
from models import ExpenseTransaction, IncomeTransaction


class TestLedger(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = get_connection(":memory:")
        self.repo = LedgerRepository(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def test_01_sql_injection_and_sort_whitelist(self) -> None:
        tx = ExpenseTransaction(1, "Zakupy", 100.0, tx_date="2026-11-20")
        self.repo.save_account_with_transactions(LedgerManager("Konto", 500.0, [tx]))

        results = self.repo.search_transactions(category_phrase="' OR '1'='1")
        self.assertEqual(len(results), 0)

        with self.assertRaises(ValueError):
            self.repo.search_transactions(sort_by="tx_id; DROP TABLE transactions; --")

        self.assertEqual(self.repo.count_transactions(), 1)

    def test_02_multi_criteria_search(self) -> None:
        txs = [
            ExpenseTransaction(1, "Zakupy Spożywcze", 120.0, tx_date="2026-11-05"),
            ExpenseTransaction(2, "Zakupy Elektronika", 850.0, tx_date="2026-11-15"),
            IncomeTransaction(3, "Wypłata", 4500.0, tx_date="2026-11-10"),
            ExpenseTransaction(4, "Zakupy Książki", 60.0, tx_date="2026-11-25"),
        ]
        self.repo.save_account_with_transactions(LedgerManager("Konto Główne", 0.0, txs))

        filtered = self.repo.search_transactions(
            category_phrase="Zakupy",
            tx_type="WYDATEK",
            date_from="2026-11-01",
            date_to="2026-11-20",
            min_amount=100.0,
            sort_by="amount_pln",
            sort_dir="ASC",
        )
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["category"], "Zakupy Spożywcze")
        self.assertEqual(filtered[1]["category"], "Zakupy Elektronika")

    def test_03_join_accounts_balance_report(self) -> None:
        txs = [
            IncomeTransaction(1, "Pensja", 3000.0, tax_pct=10.0, tx_date="2026-11-01"),
            ExpenseTransaction(2, "Czynsz", 1000.0, operator_fee=5.0, tx_date="2026-11-02"),
        ]
        self.repo.save_account_with_transactions(LedgerManager("Konto Główne", 200.0, txs))
        self.repo.create_account("Konto Oszczędnościowe", initial_balance_pln=100.0)

        report_all = self.repo.get_accounts_balance_report(min_balance=0.0)
        self.assertEqual(len(report_all), 2)
        self.assertEqual(report_all[0]["current_balance_pln"], 1895.0)
        self.assertEqual(report_all[1]["total_income_net"], 0.0)
        self.assertEqual(report_all[1]["current_balance_pln"], 100.0)

        report_filtered = self.repo.get_accounts_balance_report(min_balance=500.0)
        self.assertEqual(len(report_filtered), 1)
        self.assertEqual(report_filtered[0]["account_name"], "Konto Główne")

    def test_04_join_expenses_by_category_report(self) -> None:
        txs = [
            ExpenseTransaction(1, "Jedzenie", 80.0, tx_date="2026-11-01"),
            ExpenseTransaction(2, "Jedzenie", 120.0, tx_date="2026-11-05"),
            ExpenseTransaction(3, "Rozrywka", 45.0, tx_date="2026-11-08"),
            IncomeTransaction(4, "Jedzenie", 500.0, tx_date="2026-11-09"),
        ]
        self.repo.save_account_with_transactions(LedgerManager("Portfel", 1000.0, txs))

        report = self.repo.get_expenses_by_category(min_spent=100.0)
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["category"], "Jedzenie")
        self.assertEqual(report[0]["tx_count"], 2)
        self.assertEqual(report[0]["total_spent_pln"], 200.0)

    def test_05_atomic_transfer_commit_and_rollback(self) -> None:
        acc_src = self.repo.create_account("ROR", initial_balance_pln=1000.0)
        acc_dst = self.repo.create_account("Oszczędnościowe", initial_balance_pln=200.0)

        self.repo.transfer_funds(acc_src, acc_dst, 350.0, tx_date="2026-11-24")
        balances = {r["account_id"]: r["current_balance_pln"] for r in self.repo.get_accounts_balance_report()}
        self.assertEqual(balances[acc_src], 650.0)
        self.assertEqual(balances[acc_dst], 550.0)

        tx_count_before = self.repo.count_transactions()
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.transfer_funds(acc_src, 99999, 100.0, tx_date="2026-11-24")

        self.assertEqual(self.repo.count_transactions(), tx_count_before)
        balances_after = {r["account_id"]: r["current_balance_pln"] for r in self.repo.get_accounts_balance_report()}
        self.assertEqual(balances_after[acc_src], 650.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)