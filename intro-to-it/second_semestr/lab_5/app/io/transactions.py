from pathlib import Path
from typing import Iterator

from app.core.exceptions import DataFormatError
from app.io.registry import READERS


def read_transactions(file_path: str | Path) -> Iterator[dict]:
    """Выбирает потоковый reader по расширению и отдаёт записи по одной."""
    path = Path(file_path)
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        raise DataFormatError(f"Неизвестное расширение: {path.suffix}")
    yield from reader(path)
