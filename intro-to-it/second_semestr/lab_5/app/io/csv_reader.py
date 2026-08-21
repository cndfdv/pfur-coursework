import csv
from pathlib import Path
from typing import Iterator

from app.core.exceptions import DataFormatError


REQUIRED_FIELDS = {"id", "amount", "category", "date"}


def read_csv(path: Path) -> Iterator[dict]:
    """Читает CSV-файл и отдаёт записи по одной.

    Args:
        path: Путь до CSV-файла.

    Yields:
        Словарь с полями записи.

    Raises:
        DataFormatError: Если файл нечитаем или в нём нет нужных колонок.
    """
    try:
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise DataFormatError(f"Пустой CSV: {path.name}")
            missing = REQUIRED_FIELDS - set(reader.fieldnames)
            if missing:
                raise DataFormatError(
                    f"В {path.name} не хватает колонок: {sorted(missing)}"
                )
            for row in reader:
                yield row
    except UnicodeDecodeError as e:
        raise DataFormatError(f"Не смог прочитать {path.name}: {e}") from e
