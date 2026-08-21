"""
Базовый класс Person с атрибутами name, age
Дочерний класс Teacher с дополнительными атрибутами:
subject (преподаваемый предмет)
students (список объектов Student)
Реализуйте методы для работы со списком студентов:
add_student()
remove_student()
list_students()
"""
from typing import List, Union
import students

class Person():
    """Person object
    """
    def __init__(self, name: str, age: int):
        """IniInitializes a Persom class

        Args:
            name (str): person name
            age (int): person age
        """
        self.name = name
        self.age = age


class Teacher(Person):
    """Teacher object

    Args:
        Person class: parent class
    """

    def __init__(self, name: str, age: int, subject: str, students: List):
        """IniInitializes a Teacher class

        Args:
            name (str): teacher name
            age (int): teacher age
            subject (str): teacher subject
            students (List): techer students
        """
        super().__init__(name, age)
        self.subject = subject
        self.students = students
    
    def add_student(self, student_name: str, student_id: Union, student_grades: List[int]):
        """Add student to students

        Args:
            student_name (str): student name
            student_id (int): student age
            student_grades (List[int]): student grades
        """
        student = students.Student(student_name, student_id, student_grades)
        self.students.append(student)

    def remove_student(self, student_id: Union):
        """Remove student from students by id

        Args:
            student_id (int): id of removed student
        """
        flag = True

        for student in self.students:
            if student.student_id == student_id:
                print(student.name, "removed")
                self.students.remove(student)
                flag = False
                break
        
        if flag:
            raise ValueError('No students was found')

    def list_students(self):
        """Display students
        """
        if len(self.students) > 0:
            for num, student in enumerate(self.students):
                print(str(num+1) + ':', student.name)
        else:
            print('0 students')

if __name__ == "__main__":
    teacher = Teacher("Иван", 45, "Python", [])
    teacher.add_student("Arsenii Kniazev", 14, [10, 10, 10])
    teacher.add_student("Nikita", 6, [0, 0, 0])
    teacher.list_students()
    teacher.remove_student(14)
    teacher.list_students()
    