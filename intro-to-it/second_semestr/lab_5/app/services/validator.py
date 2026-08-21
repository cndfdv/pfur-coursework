from typing import Iterable, Iterator

from app.core.exceptions import ValidationError
from app.core.models import Transaction


REQUIRED_FIELDS = ("id", "amount", "category", "date")


def validate(record: dict) -> Transaction:
    """Превращает сырую запись в Transaction, кидает ValidationError при ошибках.

    Raises:
        ValidationError: Если поля нет, оно пустое или amount не положительный.
    """
    for field in REQUIRED_FIELDS:
        if field not in record or record[field] in ("", None):
            raise ValidationError(f"Отсутствует поле {field!r}")

    try:
        amount = float(record["amount"])
    except (TypeError, ValueError) as e:
        raise ValidationError(f"amount не приводится к float: {record['amount']!r}") from e

    if amount <= 0:
        raise ValidationError(f"amount должен быть > 0, получили {amount}")

    return Transaction(
        id=str(record["id"]),
        amount=amount,
        category=str(record["category"]),
        date=str(record["date"]),
    )


def validate_stream(records: Iterable[dict], errors: list[str],
                    source: str = "") -> Iterator[Transaction]:
    """Генератор-фильтр: пропускает только валидные записи.

    Битые транзакции не валят пайплайн — добавляются в errors и отбрасываются.
    """
    prefix = f"{source}, " if source else ""
    for i, record in enumerate(records, start=1):
        try:
            yield validate(record)
        except ValidationError as e:
            errors.append(f"{prefix}запись №{i}: {e}")
