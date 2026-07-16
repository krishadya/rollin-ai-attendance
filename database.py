import sqlite3
from pathlib import Path
from datetime import datetime

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
        email TEXT,
        face_registered INTEGER DEFAULT 0
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
            courses.course_code,
            students.face_registered
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

def get_total_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM courses")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_today_attendance_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE date = date('now')
    """)
    count = cursor.fetchone()[0]
    conn.close()
    return count

def mark_face_registered(student_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE students SET face_registered = 1 WHERE id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()


def get_student_by_student_id(student_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, student_id, email FROM students WHERE student_id = ?",
        (student_id,)
    )

    student = cursor.fetchone()
    conn.close()
    return student


def enrollment_exists(student_db_id, course_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM enrollments WHERE student_id = ? AND course_id = ?",
        (student_db_id, course_id)
    )

    enrollment = cursor.fetchone()
    conn.close()
    return enrollment is not None

def get_registered_faces_count():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM students
        WHERE face_registered = 1
    """)

    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_student_by_db_id(student_db_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, student_id, email
        FROM students
        WHERE id = ?
    """, (student_db_id,))

    student = cursor.fetchone()
    conn.close()
    return student

def is_student_enrolled(student_id_text, course_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT enrollments.id
        FROM enrollments
        JOIN students ON enrollments.student_id = students.id
        WHERE students.student_id = ? AND enrollments.course_id = ?
    """, (student_id_text, course_id))

    result = cursor.fetchone()
    conn.close()
    return result is not None


def attendance_exists(student_id_text, course_id, date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT attendance.id
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE students.student_id = ?
        AND attendance.course_id = ?
        AND attendance.date = ?
    """, (student_id_text, course_id, date))

    result = cursor.fetchone()
    conn.close()
    return result is not None


def mark_attendance(student_id_text, course_id):
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM students WHERE student_id = ?",
        (student_id_text,)
    )

    student = cursor.fetchone()

    if student is None:
        conn.close()
        return False, "Student not found."

    student_db_id = student[0]

    if attendance_exists(student_id_text, course_id, today):
        conn.close()
        return False, "Attendance already marked for today."

    cursor.execute("""
        INSERT INTO attendance (student_id, course_id, date, status, marked_at)
        VALUES (?, ?, ?, ?, ?)
    """, (student_db_id, course_id, today, "Present", now))

    conn.commit()
    conn.close()

    return True, "Attendance marked successfully."

def get_attendance_records(course_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if course_id:
        cursor.execute("""
            SELECT
                students.name,
                students.student_id,
                courses.course_name,
                courses.course_code,
                attendance.date,
                attendance.marked_at,
                attendance.status
            FROM attendance
            JOIN students ON attendance.student_id = students.id
            JOIN courses ON attendance.course_id = courses.id
            WHERE courses.id = ?
            ORDER BY attendance.date DESC, attendance.marked_at DESC
        """, (course_id,))
    else:
        cursor.execute("""
            SELECT
                students.name,
                students.student_id,
                courses.course_name,
                courses.course_code,
                attendance.date,
                attendance.marked_at,
                attendance.status
            FROM attendance
            JOIN students ON attendance.student_id = students.id
            JOIN courses ON attendance.course_id = courses.id
            ORDER BY attendance.date DESC, attendance.marked_at DESC
        """)

    records = cursor.fetchall()
    conn.close()
    return records

def get_analytics_data(course_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if course_id:
        cursor.execute("""
            SELECT
                students.name,
                students.student_id,
                courses.course_name,
                COUNT(attendance.id) as present_count
            FROM students
            JOIN enrollments ON students.id = enrollments.student_id
            JOIN courses ON enrollments.course_id = courses.id
            LEFT JOIN attendance 
                ON students.id = attendance.student_id
                AND courses.id = attendance.course_id
            WHERE courses.id = ?
            GROUP BY students.id, courses.id
        """, (course_id,))
    else:
        cursor.execute("""
            SELECT
                students.name,
                students.student_id,
                courses.course_name,
                COUNT(attendance.id) as present_count
            FROM students
            JOIN enrollments ON students.id = enrollments.student_id
            JOIN courses ON enrollments.course_id = courses.id
            LEFT JOIN attendance 
                ON students.id = attendance.student_id
                AND courses.id = attendance.course_id
            GROUP BY students.id, courses.id
        """)

    data = cursor.fetchall()
    conn.close()
    return data

