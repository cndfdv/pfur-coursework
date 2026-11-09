"""Скачать облегчённые наборы из актуальных презентаций курса."""

import json
import shutil
import tarfile
import zipfile
from pathlib import Path

import gdown

from shared.config import RAW_DIR

FILES = {
    "habr": "https://drive.google.com/file/d/1vYLYbjAW77nK9RZqytlFipJP80YX6YuA/view",
    "science": "https://drive.google.com/file/d/1itrEBAOzm2s8to5DikfSC0Y66a57xNns/view",
    "news": "https://drive.google.com/file/d/11MXoC_BYQzch0J4S1VCz8aEuth9NAv44/view",
    "injected": "https://drive.google.com/file/d/1At35kYq5GqfnuvH-qxii0XCNx0d04ilb/view",
}


def unpack(download: Path, target: Path) -> list[str]:
    target.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(download):
        with zipfile.ZipFile(download) as archive:
            archive.extractall(target)
        download.unlink()
    elif tarfile.is_tarfile(download):
        shutil.move(download, target / "dataset.tar.gz")
    else:
        with download.open("rb") as file:
            signature = file.read(3)
        suffix = ".csv.bz2" if signature == b"BZh" else ".json"
        final = target / f"dataset{suffix}"
        shutil.move(download, final)
    return [str(path.relative_to(RAW_DIR)) for path in target.rglob("*") if path.is_file()]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for source, url in FILES.items():
        folder = RAW_DIR / source
        if folder.exists() and any(folder.rglob("*")):
            print(f"{source}: уже загружен")
        else:
            temp = RAW_DIR / f"{source}.download"
            print(f"{source}: загрузка")
            file_id = url.split("/d/")[1].split("/")[0]
            gdown.download(id=file_id, output=str(temp), quiet=False)
            if not temp.exists():
                raise RuntimeError(f"Не удалось загрузить {source}")
            unpack(temp, folder)
        manifest[source] = {
            "url": url,
            "files": [
                str(path.relative_to(RAW_DIR)) for path in folder.rglob("*") if path.is_file()
            ],
        }
    (RAW_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print("Готово:", RAW_DIR)


if __name__ == "__main__":
    main()
