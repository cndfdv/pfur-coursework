from datetime import datetime

import clickhouse_connect
from clickhouse_connect.driver import Client

from config import settings


_client: Client | None = None


def get_clickhouse() -> Client:
    global _client
    if _client is None:
        _client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_PORT,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.CLICKHOUSE_DATABASE,
        )
    return _client


def ensure_schema() -> None:
    client = get_clickhouse()
    client.command(
        """
        CREATE TABLE IF NOT EXISTS search_logs (
            query String,
            results_count UInt32,
            timestamp DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY timestamp
        """
    )


def log_search(query: str, results_count: int) -> None:
    client = get_clickhouse()
    client.insert(
        "search_logs",
        [[query, results_count, datetime.utcnow()]],
        column_names=["query", "results_count", "timestamp"],
    )


def top_queries(limit: int = 10) -> list[dict]:
    client = get_clickhouse()
    rows = client.query(
        """
        SELECT query, count() AS cnt
        FROM search_logs
        GROUP BY query
        ORDER BY cnt DESC
        LIMIT {lim:UInt32}
        """,
        parameters={"lim": limit},
    ).result_rows
    return [{"query": q, "count": int(c)} for q, c in rows]


def total_searches() -> int:
    client = get_clickhouse()
    rows = client.query("SELECT count() FROM search_logs").result_rows
    return int(rows[0][0]) if rows else 0


def ping() -> bool:
    try:
        get_clickhouse().query("SELECT 1")
        return True
    except Exception:
        return False
