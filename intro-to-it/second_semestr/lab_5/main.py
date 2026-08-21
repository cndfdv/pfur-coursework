import json
import logging
import os
import sys
import tracemalloc
from itertools import chain
from pathlib import Path
from typing import Iterator

from app.core.exceptions import BaseAppError
from app.core.models import Transaction
from app.io.registry import READERS
from app.io.transactions import read_transactions
from app.services.aggregator import aggregate_by_category
from app.services.validator import validate_stream


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def process_file(path: Path, errors: list[str]) -> Iterator[Transaction]:
    """Генератор валидных транзакций из одного файла.

    Битые строки логируются и складываются в errors, остальные едут дальше.
    """
    yield from validate_stream(read_transactions(path), errors, source=path.name)


def save_result(totals: dict[str, float], output: Path) -> None:
    """Атомарная запись через временный файл."""
    tmp = output.with_suffix(output.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(totals, f, ensure_ascii=False, indent=2)
    os.replace(tmp, output)


def _file_streams(files: list[Path], file_errors: dict[Path, list[str]],
                    fatal_errors: list[str]) -> Iterator[Transaction]:
    """Лениво проходит по файлам, склеивая их потоки в один."""
    for path in files:
        try:
            yield from process_file(path, file_errors[path])
        except BaseAppError as e:
            msg = f"{path.name}: {e}"
            fatal_errors.append(msg)
            log.error(msg)


def run(data_dir: Path, output: Path, profile: bool = False) -> dict[str, float]:
    if not data_dir.is_dir():
        log.critical(f"Директория {data_dir} не найдена")
        print(f"Директория {data_dir} не найдена", file=sys.stderr)
        sys.exit(1)

    files: list[Path] = []
    for path in sorted(data_dir.iterdir()):
        if path.suffix.lower() in READERS:
            files.append(path)

    file_errors: dict[Path, list[str]] = {}
    for path in files:
        file_errors[path] = []
    fatal_errors: list[str] = []

    if profile:
        tracemalloc.start()

    totals = aggregate_by_category(_file_streams(files, file_errors, fatal_errors))

    if profile:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")

    save_result(totals, output)

    for path, errs in file_errors.items():
        for e in errs:
            log.warning(e)

    failed_file_names: set[str] = set()
    for error in fatal_errors:
        failed_file_names.add(error.split(":", maxsplit=1)[0])

    success = sum(
        1
        for p in files
        if not file_errors[p] and p.name not in failed_file_names
    )
    all_errors = list(chain(fatal_errors, *file_errors.values()))

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
        print("Использование: python main.py <папка_с_данными> [output.json] [--profile]")
        sys.exit(1)

    profile = "--profile" in sys.argv
    args: list[str] = []
    for arg in sys.argv[1:]:
        if arg != "--profile":
            args.append(arg)

    data_dir = Path(args[0])
    output = Path(args[1]) if len(args) > 1 else Path("result.json")
    run(data_dir, output, profile=profile)
