import math
import multiprocessing
import sys
import time

sys.set_int_max_str_digits(0)


def calculate_factorial(n):
    print(f"Начало вычисления факториала {n}!")
    result = math.factorial(n)
    print(f"Завершено вычисление факториала {n}! = {result}")
    return result


def calculate_prime(n):
    print(f"Начало проверки числа {n} на простоту")

    if n < 2:  # noqa: PLR2004
        result = False
    else:
        result = all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1))

    print(f"Число {n} простое: {result}")
    return result


def apply_function(func, arg):
    return func(arg)


def task3_multiprocess_calculations():
    calculations = [
        (calculate_factorial, 50000),
        (calculate_factorial, 80000),
        (calculate_prime, 1000019),
        (calculate_prime, 1000033),
    ]

    print("=== МНОГОПРОЦЕССНОЕ ВЫПОЛНЕНИЕ (Pool) ===")
    start_time = time.time()

    with multiprocessing.Pool(processes=4) as pool:
        pool.starmap(apply_function, calculations)

    multiprocess_time = time.time() - start_time

    print("\n=== СИНХРОННОЕ ВЫПОЛНЕНИЕ ===")
    start_time = time.time()

    for func, arg in calculations:
        func(arg)

    sync_time = time.time() - start_time

    print(f"Многопроцессное время: {multiprocess_time:.2f} сек")
    print(f"Синхронное время: {sync_time:.2f} сек")
    if multiprocess_time > 0:
        print(f"Ускорение: {sync_time / multiprocess_time:.2f}x")
    else:
        print("Ускорение: недоступно (нулевое время многопроцесса)")


if __name__ == "__main__":
    task3_multiprocess_calculations()
