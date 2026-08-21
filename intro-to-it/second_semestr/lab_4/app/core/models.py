from dataclasses import dataclass


@dataclass
class Transaction:
    """Финансовая транзакция после валидации."""

    id: str
    amount: float
    category: str
    date: str
