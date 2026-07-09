import sqlite3
from pathlib import Path

DB_PATH = Path("data/database.db")


def get_connection():
    return sqlite3.connect(DB_PATH, timeout=10)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            course_code TEXT NOT NULL,
            instructor_id INTEGER,
            FOREIGN KEY (instructor_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_id TEXT UNIQUE NOT NULL,
            email TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            marked_at TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO users (name, email, password, role)
        VALUES ('Admin', 'admin@rollin.com', 'admin123', 'admin')
    """)

    conn.commit()
    conn.close()


def add_course(course_name, course_code, instructor_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO courses (course_name, course_code, instructor_id) VALUES (?, ?, ?)",
        (course_name, course_code, instructor_id)
    )

    conn.commit()
    conn.close()


def get_courses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT courses.id, courses.course_name, courses.course_code, users.name
        FROM courses
        LEFT JOIN users ON courses.instructor_id = users.id
    """)

    courses = cursor.fetchall()
    conn.close()
    return courses


def delete_course(course_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))

    conn.commit()
    conn.close()

def add_student(name, student_id, email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, student_id, email) VALUES (?, ?, ?)",
        (name, student_id, email)
    )

    conn.commit()
    conn.close()


def enroll_student(student_db_id, course_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
        (student_db_id, course_id)
    )

    conn.commit()
    conn.close()


def get_students():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            students.id,
            students.name,
            students.student_id,
            students.email,
            courses.course_name,
            courses.course_code
        FROM students
        LEFT JOIN enrollments ON students.id = enrollments.student_id
        LEFT JOIN courses ON enrollments.course_id = courses.id
    """)

    students = cursor.fetchall()
    conn.close()
    return students


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM enrollments WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))

    conn.commit()
    conn.close()