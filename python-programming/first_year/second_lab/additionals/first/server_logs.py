"""
- Читает файл server_logs.txt.

- Используя регулярные выражения, извлекает данные из каждой строки лога.

Подсчитывает:

- Количество запросов с кодом статуса 200.

- Общий объём данных, переданных сервером (сумма всех размеров ответов).

- Количество уникальных IP-адресов.

- Сохраняет результаты в файл log_analysis.txt.

- Используя лямбда-функции, отсортируйте логи по дате и времени и выведите первые 10 записей.
"""

import re

with open('./additionals/first/server_logs.txt', 'r') as file:
    logs = file.readlines()

logs = [re.findall(r"\[(.*?)\]", line) for line in logs]

with open('log_analysis.txt', 'w') as file:
    file.write(f"requests with status 200: {len([i for i in logs if i[5] == '200'])}\n")
    file.write(f"total data: {sum([len(j) for i in logs for j in i])}\n")
    file.write(f"unique IP addresses: {len(set([i[2] for i in logs]))}\n")

print(sorted(logs, key=lambda x: (x[0][:4], x[0][5:7], x[0][-2:])[:10]))
