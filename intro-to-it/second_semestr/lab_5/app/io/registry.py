from pathlib import Path
from typing import Callable, Iterator

from .csv_reader import read_csv
from .json_reader import read_json


READERS: dict[str, Callable[[Path], Iterator[dict]]] = {
    ".csv": read_csv,
    ".json": read_json,
}
