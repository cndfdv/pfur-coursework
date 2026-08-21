import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
}
DB_NAME = "university"


class UniversityDB:
    def __init__(self, config=DB_CONFIG, db_name=DB_NAME):
        self.config = config.copy()
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        conn = mysql.connector.connect(**self.config)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
        conn.commit()
        cur.close()
        conn.close()

        self.config["database"] = self.db_name
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(dictionary=True)

        self._create_tables()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
            self.cursor.close()
            self.connection.close()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return True
        except Error as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return False

    def fetch_all(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"Ошибка при выборке: {e}")
            return []

    def fetch_one(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as e:
            print(f"Ошибка при выборке: {e}")
            return None

    def _create_tables(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                group_name VARCHAR(20) NOT NULL,
                admission_year INT NOT NULL,
                average_grade FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                course_name VARCHAR(100) UNIQUE NOT NULL,
                instructor VARCHAR(50) NOT NULL,
                credits INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS student_courses (
                student_id INT,
                course_id INT,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        """)

    def get_student_statistics(self):
        total = self.fetch_one("SELECT COUNT(*) as total FROM students")["total"]
        avg_grade = self.fetch_one(
            "SELECT AVG(average_grade) as avg_grade FROM students"
        )["avg_grade"]
        groups = self.fetch_all(
            "SELECT group_name, COUNT(*) as count FROM students GROUP BY group_name"
        )
        return {"total_students": total, "average_grade": avg_grade, "groups": groups}

    def get_top_students(self, limit=5):
        return self.fetch_all(
            "SELECT * FROM students ORDER BY average_grade DESC LIMIT %s", (limit,)
        )

    def get_group_statistics(self):
        return self.fetch_all(
            "SELECT group_name, COUNT(*) as student_count, AVG(average_grade) as avg_grade FROM students GROUP BY group_name"
        )
