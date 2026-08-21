"""Реализуйте класс Student со следующими характеристиками:
Атрибуты:
name (строка)
student_id (строка/число)
grades (список чисел)
Методы:
add_grade(grade) - добавляет оценку с валидацией (0-10)
get_average() - возвращает средний балл
display_info() - красиво выводит информацию о студенте
"""

from typing import List, Union

class Student():
    """Student object
    """
    def __init__(self, name: str, student_id: Union, grades: List[int]):
        """Initializes students object

        Args:
            name (str): name of student
            student_id (Union): student id
            grades (List): students grades
        """
        self.name = name
        self.student_id = student_id
        self.grades = grades

    def add_grade(self, grade: int) -> int:
        """_summary_

        Args:
            grade (int): grade which need to ba edded

        Returns:
            Error (str): error if grade diappazon
        """
        if 0 <= grade <= 10:
            self.grades.append(grade)
        else:
            raise ValueError('Grade must be from 0 to 10')

    def get_average(self):
        """average grade

        Returns:
            int: average grade
        """
        return sum(self.grades) / len(self.grades)

    def display_info(self):
        """Display student info
        """
        print('Student id:', self.student_id, sep=" ")
        print('Student_name:', self.name, sep=" ")
        print("Student grades:", self.grades)
        print("Student mean grade:", self.get_average())
    
    def __str__(self):
        return f"Student {self.name} with id {self.student_id} has grades {self.grades}"
    
    def __len__(self):
        return len(self.grades)

    def __eq__(self, other):
        try:
            return self.student_id == other.student_id
        except:
            return False

    
if __name__ == "__main__":
    student = Student("Arsenii Kniazev", 14, [10, 10, 9, 10, 9, 10])
    student.display_info()
    print(student.get_average())
    student.add_grade(1)
    student.display_info()
    