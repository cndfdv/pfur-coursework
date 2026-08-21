from typing import List, Union

import students
import teacher

class Assistant(students.Student, teacher.Teacher):
    """Assistant class"""

    def __init__(
        self,
        student_id: Union[int, str],
        student_name: str,
        student_grades: List[int],
        teacher_name: str,
        teacher_age: int,
        teacher_subject: str
    ):
        """Initializes assistant class

        Args:
            student_id (int): student id
            student_name (str): student name
            student_grades (List[]): student grades
            teacher_name (str): student name
            teacher_age (int): student age
            teacher_subject (str): student subject
        """
        self.student = students.Student(student_id=student_id, name=student_name, grades=student_grades)
        self.teacher = teacher.Teacher(name=teacher_name, age=teacher_age, subject=teacher_subject, students=[self.student])

        students.Student.__init__(self, student_id=student_id, name=student_name, grades=student_grades)
        teacher.Teacher.__init__(self, name=teacher_name, age=teacher_age, subject=teacher_subject, students=[self.student])

    def help_student(self):
        """Method to help students"""
        print(f"{self.teacher.name} is helping {self.student.name} with {self.teacher.subject}.")
        print(self.student.name, 'have marks:', self.student.grades)

if __name__ == "__main__":
    assistant = Assistant(1, "Kniazev Arsenii", [2, 2, 2], "teacher", 35, "Math")
    assistant.help_student()