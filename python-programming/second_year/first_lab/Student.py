from typing import List


class Student:
    def __init__(self, name: str, group: str, grades: List):
        """Init

        Args:
            name (str): Stud name
            group (str): Stud group
            grades (List): Stud grades
        """
        self.name = name
        self.group = group
        self.grades = grades

    @property
    def average_grade(self) -> int:
        """Calculate student mean grade

        Returns:
            int: student mean grade
        """
        return sum(self.grades) / len(self.grades)

    def is_excellent(self) -> bool:
        """is mean > 4.5

        Returns:
            bool: bool
        """
        if self.average_grade > 4.5:
            return True
        else:
            return False
