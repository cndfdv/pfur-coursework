"""
У вас есть файл students.csv, который содержит данные о студентах в формате CSV:

Имя,Возраст,Средний балл
Иван,20,4.5
Мария,21,4.8
Петр,19,3.9

Задание:

Напишите программу, которая:

- Читает данные из файла students.csv.

- Используя модуль csv, преобразует данные в список словарей.

Создаёт модуль student_utils.py, который содержит функции:

- get_top_students(students, n) — возвращает список из n студентов с наивысшим средним баллом.

- get_average_age(students) — возвращает средний возраст студентов.

- filter_students_by_grade(students, min_grade) — возвращает список студентов, у которых средний балл выше min_grade.

- Используя лямбда-функции, отсортируйте студентов по возрасту и выведите результат.

- Сохраните результаты в файл report.txt.
"""

import csv
from utils.students_utils import StudentUtils

with open("additionals/second/students.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    data = [i for i in reader]

util = StudentUtils()
top_students = util.get_top_students(data, 2)
average_age = util.get_average_age(data)
filtered_students = util.filter_students_by_grade(data, 4.0)
sorted_students = sorted(data, key=lambda x: int(x["Возраст"]))

print("sorted students by age:", sorted_students)

with open("report.txt", "w") as f:
    f.write(f"Top students: {top_students}\n")
    f.write(f"Average age: {average_age}\n")
    f.write(f"Filtered students: {filtered_students}\n")
    f.write(f"Sorted students by age: {sorted_students}")

