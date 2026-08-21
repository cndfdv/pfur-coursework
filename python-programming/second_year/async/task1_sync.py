import time


def sync_calculate(operation, a, b, delay):
    print(f"Начало операции {a} {operation} {b}")
    time.sleep(delay)

    if operation == "+":
        result = a + b
    elif operation == "-":
        result = a - b
    elif operation == "*":
        result = a * b
    elif operation == "/":
        result = a / b if b != 0 else "Ошибка: деление на ноль"
    else:
        result = "Неизвестная операция"

    print(f"Конец операции {a} {operation} {b} = {result}")
    return result


def task1_sync_calculations():
    start_time = time.time()

    results = []
    results.append(sync_calculate("+", 15, 25, 2))
    results.append(sync_calculate("-", 40, 18, 1))
    results.append(sync_calculate("*", 12, 8, 3))
    results.append(sync_calculate("/", 100, 5, 1))

    end_time = time.time()

    print(f"Общее время выполнения: {end_time - start_time:.2f} секунд")
    print(f"Результаты: {results}")


if __name__ == "__main__":
    task1_sync_calculations()
