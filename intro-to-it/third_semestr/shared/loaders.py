"""Приведение трёх учебных наборов к единому формату."""

import bz2
import csv
import json
import re
import tarfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import ijson
from bs4 import BeautifulSoup

csv.field_size_limit(10_000_000)


@dataclass
class TextRecord:
    text: str
    title: str
    source: str
    url: str = ""


def clean_html(value: str | None) -> str:
    soup = BeautifulSoup(value or "", "html.parser")
    for tag in soup(["script", "style", "svg"]):
        tag.decompose()
    for tag in soup.find_all(["p", "div", "br", "li", "h1", "h2", "h3", "h4", "pre", "tr"]):
        tag.insert_before("\n")
        tag.insert_after("\n")
    text = soup.get_text().replace("\xa0", " ").replace("\u200b", "")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _article_to_record(article: dict, source: str) -> TextRecord | None:
    if "meta" in article:
        meta = article["meta"]
        article = {
            "title": meta.get("202"),
            "text": meta.get("81"),
            "url": meta.get("url") or meta.get("217"),
        }
    title = clean_html(
        str(article.get("post_title") or article.get("titleHtml") or article.get("title") or "")
    )
    body = clean_html(
        str(
            article.get("post_html")
            or article.get("textHtml")
            or article.get("text")
            or article.get("abstract")
            or article.get("content")
            or article.get("summary")
            or ""
        )
    )
    if not body:
        lead = article.get("leadData") or {}
        body = clean_html(str(lead.get("textHtml") or "")) if isinstance(lead, dict) else ""
    if not body:
        return None
    article_id = str(article.get("post_id") or article.get("id") or "")
    url = str(article.get("url") or "")
    if source == "habr" and article_id and not url.startswith("http"):
        url = f"https://habr.com/ru/articles/{article_id}/"
    return TextRecord(f"{title}\n\n{body}".strip(), title or "Без заголовка", source, url)


def iter_habr(path: Path) -> Iterator[TextRecord]:
    """JSON имеет форму {хаб: [статья, ...]}; читаем по одной статье."""
    with path.open("rb") as file:
        events = ijson.parse(file)
        for prefix, event, value in events:
            if prefix.count(".") == 1 and prefix.endswith(".item") and event == "start_map":
                builder = ijson.ObjectBuilder()
                builder.event(event, value)
                for child_prefix, child_event, child_value in events:
                    builder.event(child_event, child_value)
                    if child_prefix == prefix and child_event == "end_map":
                        break
                record = _article_to_record(builder.value, "habr")
                if record:
                    yield record


def _open_text(path: Path):
    return (
        bz2.open(path, "rt", encoding="utf-8", errors="replace")
        if path.suffix == ".bz2"
        else path.open("r", encoding="utf-8", errors="replace")
    )


def iter_csv(path: Path, source: str) -> Iterator[TextRecord]:
    with _open_text(path) as file:
        for row in csv.DictReader(file):
            record = _article_to_record(row, source)
            if record:
                yield record


def iter_json(path: Path, source: str) -> Iterator[TextRecord]:
    with path.open("rb") as file:
        first = file.read(1)
        file.seek(0)
        prefix = "item"
        if first == b"{":
            # Научный набор может хранить записи в поле data/articles/items.
            for candidate in ("data.item", "articles.item", "items.item"):
                file.seek(0)
                found = False
                for article in ijson.items(file, candidate):
                    found = True
                    record = _article_to_record(article, source)
                    if record:
                        yield record
                if found:
                    return
            return
        for article in ijson.items(file, prefix):
            record = _article_to_record(article, source)
            if record:
                yield record


def iter_science_archive(path: Path) -> Iterator[TextRecord]:
    """Читать JSON-аннотации из tar.gz без распаковки всего архива."""
    with tarfile.open(path, "r|gz") as archive:
        for member in archive:
            if member.isfile() and member.name.endswith(".json"):
                article = json.load(archive.extractfile(member))
                record = _article_to_record(article, "science")
                if record:
                    yield record


def iter_jsonl(path: Path, source: str) -> Iterator[TextRecord]:
    with _open_text(path) as file:
        for line in file:
            try:
                article = json.loads(line)
            except json.JSONDecodeError:
                continue
            record = _article_to_record(article, source)
            if record:
                yield record


def find_source_file(folder: Path) -> Path:
    extensions = ("*.tar.gz", "*.json", "*.jsonl", "*.csv", "*.bz2")
    for pattern in extensions:
        files = sorted(folder.rglob(pattern))
        if files:
            return files[0]
    raise FileNotFoundError(f"В {folder} нет поддерживаемого файла данных")


def iter_source(folder: Path, source: str) -> Iterator[TextRecord]:
    path = find_source_file(folder)
    name = path.name.lower()
    if source == "science" and tarfile.is_tarfile(path):
        yield from iter_science_archive(path)
    elif source == "habr" and name.endswith(".json"):
        yield from iter_habr(path)
    elif ".csv" in name or name.endswith(".bz2"):
        yield from iter_csv(path, source)
    elif ".jsonl" in name:
        yield from iter_jsonl(path, source)
    else:
        yield from iter_json(path, source)


def take_unique(records: Iterator[TextRecord], limit: int) -> list[TextRecord]:
    result, seen = [], set()
    for record in records:
        key = (record.title, record.text)
        if key in seen:
            continue
        seen.add(key)
        result.append(record)
        if len(result) >= limit:
            break
    return result
