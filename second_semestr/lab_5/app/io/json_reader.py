import json
from pathlib import Path
from typing import Iterator

from app.core.exceptions import DataFormatError


CHUNK_SIZE = 64 * 1024


def read_json(path: Path) -> Iterator[dict]:
    """Потоково читает JSON-файл со списком объектов.

    Args:
        path: Путь до JSON-файла.

    Yields:
        Словарь с полями записи.

    Raises:
        DataFormatError: Если файл невалидный или формат не список словарей.
    """
    decoder = json.JSONDecoder()
    buffer = ""
    pos = 0
    eof = False

    def load_more(file_obj) -> None:
        nonlocal buffer, eof
        chunk = file_obj.read(CHUNK_SIZE)
        if chunk == "":
            eof = True
        else:
            buffer += chunk

    def skip_spaces(file_obj) -> None:
        nonlocal pos, buffer
        while True:
            while pos < len(buffer) and buffer[pos].isspace():
                pos += 1
            if pos < len(buffer) or eof:
                return
            load_more(file_obj)

    def compact_buffer() -> None:
        nonlocal buffer, pos
        if pos > CHUNK_SIZE:
            buffer = buffer[pos:]
            pos = 0

    try:
        with path.open(encoding="utf-8") as f:
            load_more(f)
            skip_spaces(f)
            if pos >= len(buffer) or buffer[pos] != "[":
                raise DataFormatError(f"В {path.name} ожидался JSON-массив")
            pos += 1

            index = 0
            while True:
                skip_spaces(f)
                if pos >= len(buffer):
                    raise DataFormatError(f"Неожиданный конец JSON в {path.name}")

                if buffer[pos] == "]":
                    return
                if buffer[pos] == ",":
                    pos += 1
                    continue

                while True:
                    try:
                        item, next_pos = decoder.raw_decode(buffer, pos)
                        break
                    except json.JSONDecodeError as e:
                        if eof:
                            raise DataFormatError(
                                f"Битый JSON в {path.name}: {e}"
                            ) from e
                        load_more(f)

                index += 1
                if not isinstance(item, dict):
                    raise DataFormatError(f"{path.name}: запись №{index} не словарь")

                pos = next_pos
                compact_buffer()
                yield item
    except UnicodeDecodeError as e:
        raise DataFormatError(f"Битый JSON в {path.name}: {e}") from e
