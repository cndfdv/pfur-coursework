from collections import defaultdict
from typing import Iterable

from app.core.models import Transaction


def aggregate_by_category(transactions: Iterable[Transaction]) -> dict[str, float]:
    """Сворачивает поток транзакций в суммы по категориям.

    Память O(K), где K — число уникальных категорий, а не число транзакций.
    """
    totals: dict[str, float] = defaultdict(float)
    for t in transactions:
        totals[t.category] += t.amount
    return dict(totals)
