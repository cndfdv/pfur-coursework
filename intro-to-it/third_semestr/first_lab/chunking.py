"""Потоковое чтение выгрузки Хабра, очистка HTML и рекурсивный чанкинг."""

import hashlib
import re
from pathlib import Path

import ijson
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_PATH = Path(__file__).parent / "data" / "habr_hub_search.json"


def iter_articles(path=DATA_PATH):
    """Читать {hub: [article, ...]} по одной статье, не загружая весь JSON."""
    with Path(path).open("rb") as file:
        events = ijson.parse(file)
        for prefix, event, value in events:
            if prefix.count(".") == 1 and prefix.endswith(".item") and event == "start_map":
                builder = ijson.ObjectBuilder()
                builder.event(event, value)
                for child_prefix, child_event, child_value in events:
                    builder.event(child_event, child_value)
                    if child_prefix == prefix and child_event == "end_map":
                        break
                yield prefix.rsplit(".", 1)[0], builder.value


def clean_html(value):
    """Сохранить текст, абзацы и код; убрать теги, скрипты и лишние пробелы."""
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


def load_documents(path=DATA_PATH, limit=500):
    """Взять первые limit уникальных непустых статей; None — весь файл."""
    if limit is not None and limit < 1:
        raise ValueError("Лимит должен быть положительным или None.")
    documents, seen_ids, seen_texts = [], set(), set()
    stats = dict(scanned=0, duplicates=0, empty=0, lead_only=0)
    for hub, article in iter_articles(path):
        stats["scanned"] += 1
        article_id = str(article.get("id") or "")
        if article_id and article_id in seen_ids:
            stats["duplicates"] += 1
            continue
        title = clean_html(article.get("titleHtml"))
        body = clean_html(article.get("textHtml"))
        lead_only = not body
        if lead_only:
            body = clean_html((article.get("leadData") or {}).get("textHtml"))
        if not body:
            stats["empty"] += 1
            continue
        text = f"{title}\n\n{body}".strip()
        digest = hashlib.sha256(text.encode()).hexdigest()
        if digest in seen_texts:
            stats["duplicates"] += 1
            continue
        seen_ids.add(article_id)
        seen_texts.add(digest)
        stats["lead_only"] += int(lead_only)
        documents.append(Document(page_content=text, metadata={
            "article_id": article_id or digest,
            "title": title or "Без заголовка",
            "source": f"https://habr.com/ru/articles/{article_id}/" if article_id else "",
            "hub": hub,
            "date": article.get("timePublished") or "",
            "lead_only": lead_only,
        }))
        if limit is not None and len(documents) >= limit:
            break
    if not documents:
        raise ValueError("В файле не найдены статьи с текстом.")
    stats["documents"] = len(documents)
    return documents, stats


def split_documents(documents, chunk_size=1000, chunk_overlap=150):
    """Размеры задаются в символах; метаданные источника остаются у каждого чанка."""
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Нужно 0 <= chunk_overlap < chunk_size.")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True,
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = str(index)
    return chunks
