"""Генератор большого CSV для проверки потокового пайплайна."""
import argparse
import random
from pathlib import Path


CATEGORIES = ("food", "transport", "salary", "rent", "entertainment", "utilities")


def generate(path: Path, target_size_mb: int) -> None:
    target = target_size_mb * 1024 * 1024
    written = 0
    i = 0
    with path.open("w", encoding="utf-8") as f:
        header = "id,amount,category,date\n"
        f.write(header)
        written += len(header)
        while written < target:
            i += 1
            line = (
                f"id-{i},"
                f"{random.uniform(1, 10000):.2f},"
                f"{random.choice(CATEGORIES)},"
                f"2025-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}\n"
            )
            f.write(line)
            written += len(line)
    print(f"Сгенерировано {i} записей, размер ~{written / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--size-mb", type=int, default=1024)
    args = parser.parse_args()
    generate(args.path, args.size_mb)
