import asyncio
from datetime import datetime


async def scheduled_task(name, priority, duration, semaphore):
    async with semaphore:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"Задача '{name}' (приоритет {priority}) начата"
        )
        await asyncio.sleep(duration)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Задача '{name}' завершена")
        return f"Результат {name}"


async def task6_async_scheduler():
    tasks_with_priority = [
        ("Экстренная задача", 1, 1),
        ("Важная задача", 2, 2),
        ("Обычная задача A", 3, 3),
        ("Обычная задача B", 3, 2),
        ("Фоновая задача", 4, 5),
    ]

    tasks_with_priority.sort(key=lambda x: x[1])

    semaphore = asyncio.Semaphore(2)

    tasks = [
        asyncio.create_task(scheduled_task(name, priority, duration, semaphore))
        for name, priority, duration in tasks_with_priority
    ]

    results = []
    for finished in asyncio.as_completed(tasks):
        result = await finished
        results.append(result)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Получен результат: {result}")

    print("\nВсе задачи завершены!")
    print("Порядок завершения задач:")
    for r in results:
        print(" -", r)


if __name__ == "__main__":
    asyncio.run(task6_async_scheduler())
