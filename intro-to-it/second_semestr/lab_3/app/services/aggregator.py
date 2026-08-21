from collections import defaultdict
from typing import Iterable

from app.core.models import Transaction


def aggregate_by_category(transactions: Iterable[Transaction]) -> dict[str, float]:
    """Суммирует amount по category."""
    totals: dict[str, float] = defaultdict(float)
    for t in transactions:
        totals[t.category] += t.amount
    return dict(totals)
