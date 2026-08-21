"""
Задание 6: Дополнительное (по желанию)
Напишите программу, которая:

- Читает текстовый файл text.txt.

- Используя регулярные выражения, находит все даты в формате DD.MM.YYYY.

- Преобразует найденные даты в формат YYYY-MM-DD.

- Сохраняет результат в файл dates.txt.

- Используя лямбда-функции, отсортируйте даты по возрастанию и выведите их.
"""
import re

with open('data/text.txt') as file:
    text = file.read()

text = text.replace('\n', ' ')
dates = re.findall(r'\b\d{1,2}\.\d{1,2}\.\d{4}\b', text)

dates_another = []
for date in dates:
    day, month, year = date.split('.')
    dates_another.append(f"{year}-{month}-{day}")

with open("result/dates.txt", "w") as file:
    for date in dates_another:
        file.write(date + "\n")

dates_another.sort(key=lambda x: (x[0:4], x[5:7], x[8:10]))
print(dates_another)