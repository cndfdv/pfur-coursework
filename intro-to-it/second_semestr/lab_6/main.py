import asyncio
import logging
import time
from typing import Any

import requests

try:
    import aiohttp
except ModuleNotFoundError:
    aiohttp = None  # type: ignore[assignment]


JsonResult = dict[str, Any]

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def _response_to_result(response: requests.Response, url: str) -> JsonResult:
    """Возвращает JSON, а если тело не JSON — кладёт текст в словарь."""
    try:
        data = response.json()
    except ValueError:
        return {"url": url, "text": response.text}
    if isinstance(data, dict):
        return data
    return {"url": url, "data": data}


def fetch_sync(urls: list[str], timeout_seconds: float = 3.0) -> list[JsonResult]:
    """Синхронный baseline: запросы идут строго по одному."""
    results: list[JsonResult] = []
    for url in urls:
        try:
            response = requests.get(url, timeout=timeout_seconds)
            response.raise_for_status()
            results.append(_response_to_result(response, url))
        except requests.RequestException as e:
            log.error("Sync request failed for %s: %s", url, e)
            results.append({})
    return results


async def fetch_url(
    session: Any,
    url: str,
    semaphore: asyncio.Semaphore,
    timeout_seconds: float = 3.0,
) -> JsonResult:
    """Скачивает один URL, не давая общему пайплайну упасть на ошибке сети."""
    if aiohttp is None:
        raise RuntimeError("Для async-части установи зависимость: pip install aiohttp")

    async with semaphore:
        try:
            timeout = aiohttp.ClientTimeout(total=timeout_seconds)
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                try:
                    data = await response.json(content_type=None)
                except ValueError:
                    return {"url": url, "text": await response.text()}
                if isinstance(data, dict):
                    return data
                return {"url": url, "data": data}
        except asyncio.TimeoutError:
            log.warning("Async timeout for %s", url)
            return {}
        except aiohttp.ClientError as e:
            log.error("Async request failed for %s: %s", url, e)
            return {}


async def main_async(
    urls: list[str],
    concurrent_limit: int = 50,
    timeout_seconds: float = 3.0,
) -> list[JsonResult]:
    """Оркестратор: одна ClientSession, много конкурентных задач и семафор."""
    if aiohttp is None:
        raise RuntimeError("Для async-части установи зависимость: pip install aiohttp")

    semaphore = asyncio.Semaphore(concurrent_limit)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch_url(session, url, semaphore, timeout_seconds))
        return await asyncio.gather(*tasks)


def build_test_urls(count: int = 100) -> list[str]:
    return [
        f"https://jsonplaceholder.typicode.com/comments/{i}"
        for i in range(1, count + 1)
    ]


def _measure(label: str, callback) -> tuple[Any, float]:
    start = time.perf_counter()
    result = callback()
    elapsed = time.perf_counter() - start
    print(f"{label}: получено {len(result)} ответов за {elapsed:.2f} сек.")
    return result, elapsed


if __name__ == "__main__":
    test_urls = build_test_urls(100)

    _measure("Sync", lambda: fetch_sync(test_urls))

    if aiohttp is None:
        print("Async пропущен: установи aiohttp командой `pip install aiohttp`.")
    else:
        _measure("Async", lambda: asyncio.run(main_async(test_urls)))
