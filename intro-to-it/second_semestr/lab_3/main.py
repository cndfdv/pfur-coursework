import json
import logging
import os
import sys
from pathlib import Path

from app.core.exceptions import BaseAppError, DataFormatError, ValidationError
from app.core.models import Transaction
from app.io.registry import READERS
from app.services.aggregator import aggregate_by_category
from app.services.validator import validate


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def process_file(path: Path) -> tuple[list[Transaction], list[str]]:
    """Читает один файл и валидирует записи.

    Битые строки не валят процесс — они логируются и складываются в errors.
    """
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        raise DataFormatError(f"Неизвестное расширение: {path.suffix}")

    transactions: list[Transaction] = []
    errors: list[str] = []
    for i, record in enumerate(reader(path), start=1):
        try:
            transactions.append(validate(record))
        except ValidationError as e:
            msg = f"{path.name}, запись №{i}: {e}"
            errors.append(msg)
            log.warning(msg)
    return transactions, errors


def save_result(totals: dict[str, float], output: Path) -> None:
    """Атомарная запись: сначала во временный файл, потом rename."""
    tmp = output.with_suffix(output.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(totals, f, ensure_ascii=False, indent=2)
    os.replace(tmp, output)


def run(data_dir: Path, output: Path) -> dict[str, float]:
    if not data_dir.is_dir():
        log.critical(f"Директория {data_dir} не найдена")
        print(f"Директория {data_dir} не найдена", file=sys.stderr)
        sys.exit(1)

    files = sorted(p for p in data_dir.iterdir() if p.suffix.lower() in READERS)
    all_transactions: list[Transaction] = []
    all_errors: list[str] = []
    success = 0

    for path in files:
        try:
            transactions, errors = process_file(path)
        except BaseAppError as e:
            msg = f"{path.name}: {e}"
            all_errors.append(msg)
            log.error(msg)
            continue

        all_transactions.extend(transactions)
        all_errors.extend(errors)
        if not errors:
            success += 1

    totals = aggregate_by_category(all_transactions)
    save_result(totals, output)

    print(
        f"Обработано {len(files)} файлов. "
        f"Успешно: {success}. Ошибок: {len(all_errors)}."
    )
    if all_errors:
        print("Список ошибок:")
        for e in all_errors:
            print(f"  - {e}")
    return totals


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python main.py <папка_с_данными> [output.json]")
        sys.exit(1)

    data_dir = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("result.json")
    run(data_dir, output)
