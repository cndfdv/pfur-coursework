import asyncio
from unittest.mock import Mock, patch

import pytest

from main import build_test_urls, fetch_sync, fetch_url


def test_build_test_urls_count():
    urls = build_test_urls(3)
    assert urls == [
        "https://jsonplaceholder.typicode.com/comments/1",
        "https://jsonplaceholder.typicode.com/comments/2",
        "https://jsonplaceholder.typicode.com/comments/3",
    ]


def test_fetch_sync_returns_json():
    response = Mock()
    response.json.return_value = {"id": 1}
    response.raise_for_status.return_value = None

    with patch("main.requests.get", return_value=response) as get:
        assert fetch_sync(["https://example.test/1"]) == [{"id": 1}]

    get.assert_called_once()


def test_fetch_sync_handles_network_error():
    with patch("main.requests.get", side_effect=pytest.importorskip("requests").RequestException("boom")):
        assert fetch_sync(["https://example.test/1"]) == [{}]


def test_fetch_url_requires_aiohttp_when_missing(monkeypatch):
    monkeypatch.setattr("main.aiohttp", None)

    async def run():
        with pytest.raises(RuntimeError, match="aiohttp"):
            await fetch_url(Mock(), "https://example.test/1", asyncio.Semaphore(1))

    asyncio.run(run())
