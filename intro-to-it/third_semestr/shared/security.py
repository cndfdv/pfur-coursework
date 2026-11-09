"""Учебные regex-эвристики: подозрительный текст не передаётся модели."""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shared.index import RetrievedDocument


RULES = (
    ("подмена инструкций", r"\b(?:ignore|disregard)\s+(?:(?:all|the)\s+)?(?:previous|prior|above)\s+(?:instructions?|prompts?)|\bигнорируй\s+(?:все\s+)?(?:предыдущие|прежние|вышеуказанные)\s+(?:инструкции|указания)"),
    ("раскрытие системного промпта", r"\b(?:reveal|show|print)\s+(?:(?:the|your)\s+)?system\s+prompt|\b(?:раскрой|покажи|выведи)\s+(?:свой\s+)?системн\w*\s+(?:промпт|инструкци\w*)"),
    ("подмена системной роли", r"<\|(?:im_start|start_header_id)\|>\s*system|\[\s*SYSTEM\s*\]|<\s*/?system\s*>|(?:^|\n)\s*system\s*:"),
    ("команда вывести запрещённое слово", r"\b(?:выведи|напиши|скажи)\s+(?:только\s+)?запрещ[её]нное\s+слово|\b(?:output|print|say)\s+(?:(?:the|only)\s+)?(?:forbidden|banned)\s+word"),
)
PATTERNS = [(reason, re.compile(pattern, re.IGNORECASE)) for reason, pattern in RULES]


def detect_injection(text: str) -> list[str]:
    """Вернуть причины срабатывания; упоминание prompt injection само не опасно."""
    return [reason for reason, pattern in PATTERNS if pattern.search(text)]


def sanitize_documents(
    documents: list["RetrievedDocument"],
) -> tuple[list["RetrievedDocument"], list[str]]:
    """Отбросить целиком подозрительные фрагменты, сохранив порядок остальных."""
    safe, warnings = [], []
    for document in documents:
        reasons = detect_injection(f"{document.title}\n{document.text}")
        if reasons:
            warnings.append(f"Фрагмент «{document.title}» исключён: {', '.join(reasons)}.")
        else:
            safe.append(document)
    return safe, warnings
