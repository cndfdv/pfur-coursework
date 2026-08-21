import concurrent.futures
import random
import time


def process_data(item):
    process_time = random.uniform(0.5, 2.0)
    time.sleep(process_time)
    result = item * 2
    print(f"Обработан элемент {item} -> {result} (время: {process_time:.2f}с)")
    return result


def run_with_thread_pool(data, max_workers):
    start_time = time.time()
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_data, item) for item in data]

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    elapsed_time = time.time() - start_time
    return results, elapsed_time


def task7_thread_pool():
    data = list(range(1, 11))

    print(">>> Пул из 2 потоков")
    results_2, time_2 = run_with_thread_pool(data, max_workers=2)

    print("\n>>> Пул из 4 потоков")
    results_4, time_4 = run_with_thread_pool(data, max_workers=4)

    print("\n>>> Пул из 8 потоков")
    results_8, time_8 = run_with_thread_pool(data, max_workers=8)

    print("\n=== РЕЗУЛЬТАТЫ ОБРАБОТКИ ===")
    print("Результаты (2 потока):", sorted(results_2))
    print("Результаты (4 потока):", sorted(results_4))
    print("Результаты (8 потоков):", sorted(results_8))

    print("\n=== СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ===")
    print(f"Пул 2 потоков: {time_2:.2f} сек")
    print(f"Пул 4 потоков: {time_4:.2f} сек")
    print(f"Пул 8 потоков: {time_8:.2f} сек")


if __name__ == "__main__":
    task7_thread_pool()
