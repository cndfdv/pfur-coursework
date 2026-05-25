import json
from pathlib import Path
from typing import Iterator

from app.core.exceptions import DataFormatError


def read_json(path: Path) -> Iterator[dict]:
    """Читает JSON-файл со списком записей.

    Args:
        path: Путь до JSON-файла.

    Yields:
        Словарь с полями записи.

    Raises:
        DataFormatError: Если файл невалидный или формат не список словарей.
    """
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise DataFormatError(f"Битый JSON в {path.name}: {e}") from e

    if not isinstance(data, list):
        raise DataFormatError(f"В {path.name} ожидался список, получили {type(data).__name__}")

    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise DataFormatError(f"{path.name}: запись №{i} не словарь")
        yield item
