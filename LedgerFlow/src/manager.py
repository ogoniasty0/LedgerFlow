from typing import Any, Self
from models import Transaction, deserialize_transaction

class LedgerManager:
    def __init__(self, account_name: str = "Portfel Domowy", initial_balance: float = 0.0, transactions: list[Transaction] | None = None) -> None:
        self.account_name: str = account_name
        self.initial_balance: float = float(initial_balance)
        self._transactions: list[Transaction] = list(transactions) if transactions is not None else []

    @property
    def transactions(self) -> list[Transaction]:
        return list(self._transactions)

    def calculate_total_balance(self) -> float:
        impact_sum = sum(tx.net_balance_impact() for tx in self._transactions)
        return round(self.initial_balance + impact_sum, 2)

    def register_transaction(self, tx: Transaction) -> None:
        if not isinstance(tx, Transaction):
            raise TypeError("Akceptujemy tylko obiekty klasy Transaction.")

        if self.calculate_total_balance() + tx.net_balance_impact() < 0.0:
            raise ValueError("Transakcja odrzucona! Powodowałaby ujemne saldo.")

        self._transactions.append(tx)

    def generate_next_id(self) -> int:
        return max([tx.tx_id for tx in self._transactions], default=0) + 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "account_name": self.account_name,
            "initial_balance": self.initial_balance,
            "transactions": [tx.to_dict() for tx in self._transactions]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        restored_txs = [deserialize_transaction(item) for item in data.get("transactions", [])]
        return cls(str(data.get("account_name", "Portfel Domowy")), float(data.get("initial_balance", 0.0)), restored_txs)