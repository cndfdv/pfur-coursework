"""Построить три индекса по 10 000 документов на GPU, если она доступна."""

from time import perf_counter

from shared.config import INDEX_DIR, RAW_DIR
from shared.index import build_index
from shared.loaders import iter_source, take_unique

DOCUMENT_LIMIT = 10_000


def main() -> None:
    for source in ("habr", "science", "news"):
        started = perf_counter()
        records = take_unique(iter_source(RAW_DIR / source, source), DOCUMENT_LIMIT)
        if not records:
            raise RuntimeError(f"Источник {source} не содержит текстов")
        meta = build_index(records, INDEX_DIR / source)
        seconds = perf_counter() - started
        print(source, meta, f"{seconds:.1f} с")


if __name__ == "__main__":
    main()
