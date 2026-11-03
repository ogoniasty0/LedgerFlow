from typing import Any, Self

class Transaction:
    ALLOWED_TYPES = {"PRZYCHOD", "WYDATEK"}

    def __init__(self, tx_id: int, category: str, amount_pln: float, tx_type: str) -> None:
        self.tx_id: int = tx_id
        self.category: str = category
        self.amount_pln = amount_pln 
        self.tx_type = tx_type

    @property
    def amount_pln(self) -> float:
        return self._amount_pln

    @amount_pln.setter
    def amount_pln(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Kwota transakcji musi być liczbą.")
        if value <= 0.0:
            raise ValueError(f"Kwota transakcji musi być większa od zera (podano: {value}).")
        self._amount_pln = round(float(value), 2)

    @property
    def tx_type(self) -> str:
        return self._tx_type

    @tx_type.setter
    def tx_type(self, value: str) -> None:
        normalized_type = value.strip().upper()
        if normalized_type == "DOCHÓD" or normalized_type == "PRZYCHÓD":
            normalized_type = "PRZYCHOD"

        if normalized_type not in self.ALLOWED_TYPES:
            raise ValueError(f"Typ transakcji musi być jednym z {self.ALLOWED_TYPES} (podano: '{value}').")
        self._tx_type = normalized_type

    def __repr__(self) -> str:
        return f"Transaction(tx_id={self.tx_id}, category={self.category!r}, amount_pln={self.amount_pln}, tx_type={self.tx_type!r})"

    def __str__(self) -> str:
        return f"[{self.tx_id:02d}] {self.category:<15} | {self.amount_pln:>8.2f} PLN | {self.tx_type:<8}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return False
        return self.tx_id == other.tx_id

    def __lt__(self, other: "Transaction") -> bool:
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.amount_pln < other.amount_pln

    def to_dict(self) -> dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "category": self.category,
            "amount_pln": self.amount_pln,
            "tx_type": self.tx_type
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            tx_id=int(data["tx_id"]),
            category=str(data["category"]),
            amount_pln=float(data["amount_pln"]),
            tx_type=str(data["tx_type"])
        )


class Account:

    def __init__(self, account_name: str, initial_balance: float = 0.0, transactions: list[Transaction] | None = None) -> None:
        self.account_name: str = account_name
        self.initial_balance: float = float(initial_balance)
        self._transactions: list[Transaction] = list(transactions) if transactions is not None else []

    @property
    def transactions(self) -> list[Transaction]:
        return list(self._transactions)

    def current_balance(self) -> float:
        balance = self.initial_balance
        for tx in self._transactions:
            if tx.tx_type == "PRZYCHOD":
                balance += tx.amount_pln
            elif tx.tx_type == "WYDATEK":
                balance -= tx.amount_pln
        return round(balance, 2)

    def register_tx(self, tx: Transaction) -> None:
        if not isinstance(tx, Transaction):
            raise TypeError("W koncie można rejestrować wyłącznie obiekty klasy Transaction.")

        if tx.tx_type == "WYDATEK":
            if self.current_balance() - tx.amount_pln < 0.0:
                raise ValueError(
                    f"Transakcja odrzucona! Wydatek {tx.amount_pln:.2f} PLN spowodowałby ujemne saldo "
                    f"(Aktualne saldo: {self.current_balance():.2f} PLN)."
                )

        self._transactions.append(tx)

    def __str__(self) -> str:
        lines = [f"=== KONTO: {self.account_name} (Saldo: {self.current_balance():.2f} PLN) ==="]
        for tx in self._transactions:
            lines.append(f"  * {tx}")
        return "\n".join(lines)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Account):
            return False
        return (
            self.account_name == other.account_name
            and self.initial_balance == other.initial_balance
            and self._transactions == other._transactions
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "account_name": self.account_name,
            "initial_balance": self.initial_balance,
            "transactions": [tx.to_dict() for tx in self._transactions]
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        restored_txs = [Transaction.from_dict(item) for item in data.get("transactions", [])]
        return cls(
            account_name=str(data.get("account_name", "Główne Konto")),
            initial_balance=float(data.get("initial_balance", 0.0)),
            transactions=restored_txs
        )