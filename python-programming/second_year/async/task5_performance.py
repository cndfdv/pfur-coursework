import asyncio
import multiprocessing
import threading
import time


def io_task(name, duration):
    time.sleep(duration)
    return f"{name} completed"


async def async_io_task(name, duration):
    await asyncio.sleep(duration)
    return f"{name} completed"


def task5_performance_comparison():
    tasks = [
        ("Task1", 2),
        ("Task2", 3),
        ("Task3", 1),
        ("Task4", 2),
        ("Task5", 1),
    ]

    start = time.time()
    for name, duration in tasks:
        io_task(name, duration)
    sync_time = time.time() - start

    start = time.time()
    threads = []

    for name, duration in tasks:
        t = threading.Thread(target=io_task, args=(name, duration))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    threading_time = time.time() - start

    start = time.time()
    processes = []

    for name, duration in tasks:
        p = multiprocessing.Process(target=io_task, args=(name, duration))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    multiprocessing_time = time.time() - start

    async def run_async():
        coroutines = [async_io_task(name, duration) for name, duration in tasks]
        await asyncio.gather(*coroutines)

    start = time.time()
    asyncio.run(run_async())
    async_time = time.time() - start

    print(f"Синхронное время:        {sync_time:.2f} сек")
    print(f"Многопоточное время:    {threading_time:.2f} сек")
    print(f"Многопроцессное время:  {multiprocessing_time:.2f} сек")
    print(f"Асинхронное время:      {async_time:.2f} сек")


if __name__ == "__main__":
    task5_performance_comparison()
