"""Общие настройки лабораторных."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INDEX_DIR = DATA_DIR / "indexes"

EMBEDDING_MODEL = "deepvk/USER2-small"
LLM_MODEL = "gpt-6-luna"
REASONING_EFFORT = "medium"

# Standard API, USD за 1M токенов, 09.11.2026. Reasoning входит в output.
INPUT_USD_PER_MILLION = float(os.getenv("OPENAI_INPUT_PRICE", "0.10"))
CACHED_USD_PER_MILLION = float(os.getenv("OPENAI_CACHED_PRICE", "0.01"))
OUTPUT_USD_PER_MILLION = float(os.getenv("OPENAI_OUTPUT_PRICE", "0.50"))
