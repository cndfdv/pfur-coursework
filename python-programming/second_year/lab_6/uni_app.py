# university_app.py

from tabulate import tabulate
from uni_bd import UniversityDB

def add_student_interactive():
    print("\n--- Добавление студента ---")
    first_name = input("Имя: ").strip()
    last_name = input("Фамилия: ").strip()
    group_name = input("Группа: ").strip()
    
    while True:
        try:
            admission_year = int(input("Год поступления: "))
            if 2013 <= admission_year <= 2025:
                break
            else:
                print("Год должен быть между 2013 и 2025")
        except ValueError:
            print("Введите корректный год")
    
    while True:
        try:
            average_grade = input("Средний балл (оставьте пустым, если нет): ").strip()
            if average_grade == "":
                average_grade = None
                break
            average_grade = float(average_grade)
            if 0 <= average_grade <= 5:
                break
            else:
                print("Балл должен быть между 0 и 5")
        except ValueError:
            print("Введите число от 0 до 5")
    
    with UniversityDB() as db:
        query = """
            INSERT INTO students (first_name, last_name, group_name, admission_year, average_grade)
            VALUES (%s, %s, %s, %s, %s)
        """
        success = db.execute_query(query, (first_name, last_name, group_name, admission_year, average_grade))
        if success:
            print("Студент успешно добавлен!")
        else:
            print("Ошибка при добавлении студента")

def display_all_students():
    with UniversityDB() as db:
        students = db.fetch_all("SELECT * FROM students")
        if students:
            print("\nВсе студенты:")
            print(tabulate(students, headers="keys", tablefmt="grid"))
        else:
            print("Студентов нет")

def search_student_by_last_name():
    term = input("Введите фамилию или часть фамилии: ").strip()
    with UniversityDB() as db:
        students = db.fetch_all(
            "SELECT * FROM students WHERE last_name LIKE %s", (f"%{term}%",)
        )
        if students:
            print(tabulate(students, headers="keys", tablefmt="grid"))
        else:
            print("Студенты не найдены")

def update_student_grade():
    student_id = input("ID студента для обновления: ").strip()
    try:
        student_id = int(student_id)
    except ValueError:
        print("Некорректный ID")
        return

    while True:
        try:
            new_grade = float(input("Новый средний балл: "))
            if 0 <= new_grade <= 5:
                break
            else:
                print("Балл должен быть от 0 до 5")
        except ValueError:
            print("Введите число от 0 до 5")
    
    with UniversityDB() as db:
        success = db.execute_query(
            "UPDATE students SET average_grade=%s WHERE id=%s",
            (new_grade, student_id)
        )
        if success:
            print("Средний балл обновлен!")
        else:
            print("Ошибка при обновлении")

def delete_student():
    student_id = input("ID студента для удаления: ").strip()
    try:
        student_id = int(student_id)
    except ValueError:
        print("Некорректный ID")
        return

    with UniversityDB() as db:
        success = db.execute_query("DELETE FROM students WHERE id=%s", (student_id,))
        if success:
            print("Студент удален")
        else:
            print("Ошибка при удалении")

def show_statistics():
    with UniversityDB() as db:
        stats = db.get_student_statistics()
        print(f"\nОбщее количество студентов: {stats['total_students']}")
        print(f"Средний балл по университету: {stats['average_grade']:.2f}" if stats['average_grade'] else "Нет оценок")
        print("\nКоличество студентов по группам:")
        print(tabulate(stats['groups'], headers="keys", tablefmt="grid"))

def main():
    while True:
        print("\n=== Университетский учет ===")
        print("1. Добавить студента")
        print("2. Просмотреть всех студентов")
        print("3. Найти студента по фамилии")
        print("4. Обновить оценку студента")
        print("5. Удалить студента")
        print("6. Показать статистику")
        print("7. Выход")
        
        choice = input("Выберите действие: ").strip()
        if choice == '1':
            add_student_interactive()
        elif choice == '2':
            display_all_students()
        elif choice == '3':
            search_student_by_last_name()
        elif choice == '4':
            update_student_grade()
        elif choice == '5':
            delete_student()
        elif choice == '6':
            show_statistics()
        elif choice == '7':
            print("Выход из программы")
            break
        else:
            print("Неверный выбор! Введите цифру от 1 до 7")

if __name__ == "__main__":
    main()
