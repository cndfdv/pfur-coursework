class StudentUtils:
    @staticmethod
    def get_top_students(students, n):
        top_students = sorted(
            students, key=lambda x: float(x["Средний балл"])
        )[::-1][:n]
        return top_students

    @staticmethod
    def get_average_age(students):
        return sum(int(student["Возраст"]) for student in students) / len(students)

    @staticmethod
    def filter_students_by_grade(students, min_score):
        filtered_students = [
            student
            for student in students
            if float(student["Средний балл"]) >= min_score
        ]
        return filtered_students