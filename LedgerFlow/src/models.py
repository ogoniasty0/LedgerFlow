from abc import ABC, abstractmethod
from typing import Any, Self

class Transaction(ABC):

    def __init__(self, tx_id: int, category: str, amount_pln: float) -> None:
        self.tx_id: int = tx_id
        self.category: str = category
        self.amount_pln = amount_pln

    @property
    def amount_pln(self) -> float:
        return self._amount_pln

    @amount_pln.setter
    def amount_pln(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise TypeError("Kwota transakcji musi być wartością liczbową.")
        if value <= 0.0:
            raise ValueError(f"Kwota musi być większa od zera (podano: {value}).")
        self._amount_pln = round(float(value), 2)

    @abstractmethod
    def net_balance_impact(self) -> float:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(tx_id={self.tx_id}, category={self.category!r}, amount_pln={self.amount_pln})"

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
            "amount_pln": self.amount_pln
        }


class ExpenseTransaction(Transaction):

    def __init__(self, tx_id: int, category: str, amount_pln: float, operator_fee: float = 0.0) -> None:
        super().__init__(tx_id, category, amount_pln)
        self.operator_fee = operator_fee

    @property
    def operator_fee(self) -> float:
        return self._operator_fee

    @operator_fee.setter
    def operator_fee(self, value: float) -> None:
        if not isinstance(value, (int, float)) or value < 0.0:
            raise ValueError("Prowizja operatora nie może być ujemna.")
        self._operator_fee = round(float(value), 2)

    def net_balance_impact(self) -> float:
        return -round(self.amount_pln + self.operator_fee, 2)

    def __str__(self) -> str:
        return f"[{self.tx_id:02d}] WYDATEK | {self.category:<15} | -{(self.amount_pln + self.operator_fee):>8.2f} PLN (Prowizja: {self.operator_fee:.2f} PLN)"

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["type"] = "expense"
        data["operator_fee"] = self.operator_fee
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            tx_id=int(data["tx_id"]),
            category=str(data["category"]),
            amount_pln=float(data["amount_pln"]),
            operator_fee=float(data.get("operator_fee", 0.0))
        )


class IncomeTransaction(Transaction):

    def __init__(self, tx_id: int, category: str, amount_pln: float, source: str = "Inne", tax_pct: float = 0.0) -> None:
        super().__init__(tx_id, category, amount_pln)
        self.source: str = source
        self.tax_pct = tax_pct

    @property
    def tax_pct(self) -> float:
        return self._tax_pct

    @tax_pct.setter
    def tax_pct(self, value: float) -> None:
        if not isinstance(value, (int, float)) or not (0.0 <= value <= 100.0):
            raise ValueError("Stawka podatku musi mieścić się w przedziale 0-100%.")
        self._tax_pct = round(float(value), 2)

    def net_balance_impact(self) -> float:
        net_amount = self.amount_pln * (1.0 - (self.tax_pct / 100.0))
        return round(net_amount, 2)

    def __str__(self) -> str:
        return f"[{self.tx_id:02d}] PRZYCHÓD | {self.category:<15} | +{self.net_balance_impact():>8.2f} PLN (Źródło: {self.source}, Podatek: {self.tax_pct}%)"

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["type"] = "income"
        data["source"] = self.source
        data["tax_pct"] = self.tax_pct
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            tx_id=int(data["tx_id"]),
            category=str(data["category"]),
            amount_pln=float(data["amount_pln"]),
            source=str(data.get("source", "Inne")),
            tax_pct=float(data.get("tax_pct", 0.0))
        )



TRANSACTION_REGISTRY: dict[str, type[Transaction]] = {
    "expense": ExpenseTransaction,
    "income": IncomeTransaction
}

def deserialize_transaction(payload: dict[str, Any]) -> Transaction:
    tx_type = payload.get("type")
    target_cls = TRANSACTION_REGISTRY.get(tx_type)
    if target_cls is None:
        raise ValueError(f"Nieznany dyskryminator typu w bazie danych: {tx_type!r}")
    return target_cls.from_dict(payload)