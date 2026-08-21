import asyncio
import time

import aiohttp


async def fetch_url(session, url, name):
    print(f"Начало загрузки {name}")

    try:
        async with session.get(url) as response:
            content = await response.text()
            print(f"Завершена загрузка {name}, статус: {response.status}")
            return len(content)
    except Exception as e:
        print(f"Ошибка при загрузке {name}: {e}")
        return 0


async def task4_async_scraper():
    urls = [
        ("https://httpbin.org/delay/1", "Сайт 1"),
        ("https://httpbin.org/delay/2", "Сайт 2"),
        ("https://httpbin.org/delay/1", "Сайт 3"),
        ("https://httpbin.org/delay/3", "Сайт 4"),
    ]

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url, name) for url, name in urls]

        results = await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")
    print(f"Размеры контента: {results}")


if __name__ == "__main__":
    asyncio.run(task4_async_scraper())
