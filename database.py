import sqlite3
from datetime import datetime
from pathlib import Path

from security import hash_password, is_password_hash


DB_PATH = Path("data/database.db")
FACES_DIR = Path("data/faces")
EMBEDDINGS_DIR = Path("data/embeddings")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def is_admin(role: str) -> bool:
    """Return True when the current user has administrator access."""
    return role.strip().lower() == "admin"


def can_access_course(course_id: int, user_id: int, role: str) -> bool:
    """Check whether a user may view or manage a course."""
    if is_admin(role):
        return True

    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT 1
            FROM courses
            WHERE id = ? AND instructor_id = ?
            """,
            (course_id, user_id),
        ).fetchone()
        return row is not None
    finally:
        connection.close()


def can_access_student(student_db_id: int, user_id: int, role: str) -> bool:
    """Admins access every student; instructors access students in their courses."""
    if is_admin(role):
        return True

    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT 1
            FROM enrollments
            JOIN courses ON enrollments.course_id = courses.id
            WHERE enrollments.student_id = ?
              AND courses.instructor_id = ?
            LIMIT 1
            """,
            (student_db_id, user_id),
        ).fetchone()
        return row is not None
    finally:
        connection.close()


def normalize_course_code(course_code):
    """Remove extra spaces and make course codes consistent."""
    return " ".join(course_code.strip().upper().split())


def normalize_course_name(course_name):
    """Remove unnecessary spaces from course names."""
    return " ".join(course_name.strip().split())


def ensure_default_user(
    cursor,
    name: str,
    email: str,
    password: str,
    role: str = "instructor",
):
    """
    Create a default user if the email does not already exist.

    Existing plaintext passwords are migrated to secure hashes.
    """
    cursor.execute(
        """
        SELECT id, password
        FROM users
        WHERE email = ?
        """,
        (email.strip().lower(),),
    )

    existing_user = cursor.fetchone()

    if existing_user is None:
        cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                password,
                role
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name.strip(),
                email.strip().lower(),
                hash_password(password),
                role,
            ),
        )

    elif not is_password_hash(existing_user[1]):
        cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                hash_password(existing_user[1]),
                existing_user[0],
            ),
        )


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    try:
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
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                marked_at TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)

        # Clean existing course names and codes.
        existing_courses = cursor.execute(
            "SELECT id, course_name, course_code FROM courses ORDER BY id"
        ).fetchall()

        for course_id, course_name, course_code in existing_courses:
            cursor.execute(
                """
                UPDATE courses
                SET course_name = ?, course_code = ?
                WHERE id = ?
                """,
                (
                    normalize_course_name(course_name),
                    normalize_course_code(course_code),
                    course_id,
                ),
            )

        # Merge duplicate courses that may already exist.
        existing_courses = cursor.execute(
            "SELECT id, course_code FROM courses ORDER BY id"
        ).fetchall()

        course_by_code = {}

        for course_id, course_code in existing_courses:
            normalized_code = normalize_course_code(course_code)

            if normalized_code not in course_by_code:
                course_by_code[normalized_code] = course_id
                continue

            original_course_id = course_by_code[normalized_code]
            duplicate_course_id = course_id

            # Move enrollments from the duplicate course to the original course.
            cursor.execute(
                """
                INSERT OR IGNORE INTO enrollments (student_id, course_id)
                SELECT student_id, ?
                FROM enrollments
                WHERE course_id = ?
                """,
                (original_course_id, duplicate_course_id),
            )

            # Move attendance from the duplicate course to the original course.
            cursor.execute(
                """
                INSERT OR IGNORE INTO attendance (
                    student_id,
                    course_id,
                    date,
                    status,
                    marked_at
                )
                SELECT
                    student_id,
                    ?,
                    date,
                    status,
                    marked_at
                FROM attendance
                WHERE course_id = ?
                """,
                (original_course_id, duplicate_course_id),
            )

            cursor.execute(
                "DELETE FROM attendance WHERE course_id = ?",
                (duplicate_course_id,),
            )
            cursor.execute(
                "DELETE FROM enrollments WHERE course_id = ?",
                (duplicate_course_id,),
            )
            cursor.execute(
                "DELETE FROM courses WHERE id = ?",
                (duplicate_course_id,),
            )

        # Remove duplicate enrollments already stored in the database.
        cursor.execute("""
            DELETE FROM enrollments
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM enrollments
                GROUP BY student_id, course_id
            )
        """)

        # Remove duplicate attendance records already stored in the database.
        cursor.execute("""
            DELETE FROM attendance
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM attendance
                GROUP BY student_id, course_id, date
            )
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_course_code
            ON courses(UPPER(TRIM(course_code)))
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_enrollment
            ON enrollments(student_id, course_id)
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_daily_attendance
            ON attendance(student_id, course_id, date)
        """)

        ensure_default_user(
            cursor=cursor,
            name="Admin",
            email="admin@rollin.com",
            password="admin123",
            role="admin",
        )

        ensure_default_user(
            cursor=cursor,
            name="Krish Adya",
            email="krish@rollin.com",
            password="krish473",
            role="instructor",
        )

        connection.commit()
    finally:
        connection.close()


def add_course(course_name, course_code, instructor_id):
    course_name = normalize_course_name(course_name)
    course_code = normalize_course_code(course_code)

    if not course_name or not course_code:
        raise ValueError("Course name and course code are required.")

    connection = get_connection()

    try:
        existing_course = connection.execute(
            """
            SELECT id
            FROM courses
            WHERE UPPER(TRIM(course_code)) = UPPER(TRIM(?))
            """,
            (course_code,),
        ).fetchone()

        if existing_course:
            raise ValueError(
                f"A course with code {course_code} already exists."
            )

        connection.execute(
            """
            INSERT INTO courses (
                course_name,
                course_code,
                instructor_id
            )
            VALUES (?, ?, ?)
            """,
            (
                course_name,
                course_code,
                instructor_id,
            ),
        )

        connection.commit()

    except sqlite3.IntegrityError as error:
        connection.rollback()

        raise ValueError(
            f"A course with code {course_code} already exists."
        ) from error

    finally:
        connection.close()


def get_courses(user_id: int, role: str):
    """Return all courses for admins and only owned courses for instructors."""
    connection = get_connection()

    try:
        if is_admin(role):
            return connection.execute(
                """
                SELECT
                    courses.id,
                    courses.course_name,
                    courses.course_code,
                    users.name
                FROM courses
                LEFT JOIN users ON courses.instructor_id = users.id
                ORDER BY courses.course_name, courses.course_code
                """
            ).fetchall()

        return connection.execute(
            """
            SELECT
                courses.id,
                courses.course_name,
                courses.course_code,
                users.name
            FROM courses
            LEFT JOIN users ON courses.instructor_id = users.id
            WHERE courses.instructor_id = ?
            ORDER BY courses.course_name, courses.course_code
            """,
            (user_id,),
        ).fetchall()
    finally:
        connection.close()


def delete_course(course_id: int, user_id: int, role: str):
    """Delete a course after verifying ownership or administrator access."""
    if not can_access_course(course_id, user_id, role):
        raise PermissionError("You do not have permission to delete this course.")

    connection = get_connection()

    try:
        connection.execute("BEGIN")
        connection.execute(
            "DELETE FROM attendance WHERE course_id = ?",
            (course_id,),
        )
        connection.execute(
            "DELETE FROM enrollments WHERE course_id = ?",
            (course_id,),
        )
        connection.execute(
            "DELETE FROM courses WHERE id = ?",
            (course_id,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def add_student(name, student_id, email):
    name = " ".join(name.strip().split())
    student_id = student_id.strip()
    email = email.strip().lower()

    if not name or not student_id or not email:
        raise ValueError("Name, student ID, and email are required.")

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO students (name, student_id, email)
            VALUES (?, ?, ?)
            """,
            (
                name,
                student_id,
                email,
            ),
        )

        connection.commit()

    except sqlite3.IntegrityError as error:
        connection.rollback()

        raise ValueError(
            f"A student with ID {student_id} already exists."
        ) from error

    finally:
        connection.close()


def enroll_student(
    student_db_id: int,
    course_id: int,
    user_id: int,
    role: str,
):
    """Enroll a student only when the user may manage the selected course."""
    if not can_access_course(course_id, user_id, role):
        raise PermissionError("You cannot enroll students in this course.")

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO enrollments (student_id, course_id)
            VALUES (?, ?)
            """,
            (student_db_id, course_id),
        )
        connection.commit()
    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise ValueError(
            "This student is already enrolled in the selected course."
        ) from error
    finally:
        connection.close()


def get_students(user_id: int, role: str):
    """Return all students for admins and owned-course students for instructors."""
    connection = get_connection()

    try:
        if is_admin(role):
            return connection.execute(
                """
                SELECT
                    students.id,
                    students.name,
                    students.student_id,
                    students.email,
                    COALESCE(GROUP_CONCAT(DISTINCT courses.course_name), 'Not enrolled'),
                    COALESCE(GROUP_CONCAT(DISTINCT courses.course_code), ''),
                    students.face_registered
                FROM students
                LEFT JOIN enrollments ON students.id = enrollments.student_id
                LEFT JOIN courses ON enrollments.course_id = courses.id
                GROUP BY
                    students.id,
                    students.name,
                    students.student_id,
                    students.email,
                    students.face_registered
                ORDER BY students.name, students.student_id
                """
            ).fetchall()

        return connection.execute(
            """
            SELECT
                students.id,
                students.name,
                students.student_id,
                students.email,
                GROUP_CONCAT(DISTINCT courses.course_name),
                GROUP_CONCAT(DISTINCT courses.course_code),
                students.face_registered
            FROM students
            JOIN enrollments ON students.id = enrollments.student_id
            JOIN courses ON enrollments.course_id = courses.id
            WHERE courses.instructor_id = ?
            GROUP BY
                students.id,
                students.name,
                students.student_id,
                students.email,
                students.face_registered
            ORDER BY students.name, students.student_id
            """,
            (user_id,),
        ).fetchall()
    finally:
        connection.close()


def get_students_for_enrollment():
    """Return global student profiles for enrollment selection."""
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT id, name, student_id, email, face_registered
            FROM students
            ORDER BY name, student_id
            """
        ).fetchall()
    finally:
        connection.close()


def delete_student(student_id: int, role: str):
    """Delete a global student profile; administrators only."""
    if not is_admin(role):
        raise PermissionError("Only administrators can delete student profiles.")

    student = get_student_by_db_id(student_id)
    if student is None:
        return

    student_identifier = student[2]
    connection = get_connection()

    try:
        connection.execute("BEGIN")
        connection.execute(
            "DELETE FROM attendance WHERE student_id = ?",
            (student_id,),
        )
        connection.execute(
            "DELETE FROM enrollments WHERE student_id = ?",
            (student_id,),
        )
        connection.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    files_to_remove = (
        FACES_DIR / f"{student_identifier}.jpg",
        EMBEDDINGS_DIR / f"{student_identifier}.npy",
    )
    for file_path in files_to_remove:
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            pass


def get_total_courses(user_id: int, role: str):
    connection = get_connection()
    try:
        if is_admin(role):
            return connection.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        return connection.execute(
            "SELECT COUNT(*) FROM courses WHERE instructor_id = ?",
            (user_id,),
        ).fetchone()[0]
    finally:
        connection.close()


def get_total_students(user_id: int, role: str):
    connection = get_connection()
    try:
        if is_admin(role):
            return connection.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        return connection.execute(
            """
            SELECT COUNT(DISTINCT students.id)
            FROM students
            JOIN enrollments ON students.id = enrollments.student_id
            JOIN courses ON enrollments.course_id = courses.id
            WHERE courses.instructor_id = ?
            """,
            (user_id,),
        ).fetchone()[0]
    finally:
        connection.close()


def get_today_attendance_count(user_id: int, role: str):
    today = datetime.now().strftime("%Y-%m-%d")
    connection = get_connection()
    try:
        if is_admin(role):
            return connection.execute(
                "SELECT COUNT(*) FROM attendance WHERE date = ?",
                (today,),
            ).fetchone()[0]
        return connection.execute(
            """
            SELECT COUNT(*)
            FROM attendance
            JOIN courses ON attendance.course_id = courses.id
            WHERE attendance.date = ? AND courses.instructor_id = ?
            """,
            (today, user_id),
        ).fetchone()[0]
    finally:
        connection.close()


def mark_face_registered(
    student_id: int,
    user_id: int,
    role: str,
):
    """Mark a face profile only when the user may access the student."""
    if not can_access_student(student_id, user_id, role):
        raise PermissionError(
            "You do not have permission to register this student's face profile."
        )

    connection = get_connection()
    try:
        connection.execute(
            """
            UPDATE students
            SET face_registered = 1
            WHERE id = ?
            """,
            (student_id,),
        )
        connection.commit()
    finally:
        connection.close()


def get_student_by_student_id(student_id):
    connection = get_connection()

    student = connection.execute(
        """
        SELECT id, name, student_id, email
        FROM students
        WHERE student_id = ?
        """,
        (student_id.strip(),),
    ).fetchone()

    connection.close()

    return student


def get_student_by_db_id(student_db_id):
    connection = get_connection()

    student = connection.execute(
        """
        SELECT id, name, student_id, email
        FROM students
        WHERE id = ?
        """,
        (student_db_id,),
    ).fetchone()

    connection.close()

    return student


def enrollment_exists(student_db_id, course_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT 1
        FROM enrollments
        WHERE student_id = ? AND course_id = ?
        """,
        (
            student_db_id,
            course_id,
        ),
    ).fetchone()

    connection.close()

    return row is not None


def get_registered_faces_count(user_id: int, role: str):
    connection = get_connection()
    try:
        if is_admin(role):
            return connection.execute(
                "SELECT COUNT(*) FROM students WHERE face_registered = 1"
            ).fetchone()[0]
        return connection.execute(
            """
            SELECT COUNT(DISTINCT students.id)
            FROM students
            JOIN enrollments ON students.id = enrollments.student_id
            JOIN courses ON enrollments.course_id = courses.id
            WHERE students.face_registered = 1
              AND courses.instructor_id = ?
            """,
            (user_id,),
        ).fetchone()[0]
    finally:
        connection.close()


def is_student_enrolled(student_id_text, course_id):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT 1
        FROM enrollments
        JOIN students
            ON enrollments.student_id = students.id
        WHERE students.student_id = ?
          AND enrollments.course_id = ?
        """,
        (
            student_id_text.strip(),
            course_id,
        ),
    ).fetchone()

    connection.close()

    return row is not None


def attendance_exists(student_id_text, course_id, date):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT 1
        FROM attendance
        JOIN students
            ON attendance.student_id = students.id
        WHERE students.student_id = ?
          AND attendance.course_id = ?
          AND attendance.date = ?
        """,
        (
            student_id_text.strip(),
            course_id,
            date,
        ),
    ).fetchone()

    connection.close()

    return row is not None


def mark_attendance(
    student_id_text: str,
    course_id: int,
    user_id: int,
    role: str,
):
    if not can_access_course(course_id, user_id, role):
        return False, "You cannot take attendance for this course."

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    connection = get_connection()

    student = connection.execute(
        "SELECT id FROM students WHERE student_id = ?",
        (student_id_text.strip(),),
    ).fetchone()

    if student is None:
        connection.close()
        return False, "Student not found."

    try:
        connection.execute(
            """
            INSERT INTO attendance (
                student_id, course_id, date, status, marked_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (student[0], course_id, today, "Present", current_time),
        )
        connection.commit()
        return True, "Attendance marked successfully."
    except sqlite3.IntegrityError:
        connection.rollback()
        return False, "Attendance already marked for today."
    finally:
        connection.close()


def get_attendance_records(
    user_id: int,
    role: str,
    course_id=None,
):
    connection = get_connection()
    conditions = []
    parameters = []

    if not is_admin(role):
        conditions.append("courses.instructor_id = ?")
        parameters.append(user_id)
    if course_id is not None:
        conditions.append("courses.id = ?")
        parameters.append(course_id)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    try:
        return connection.execute(
            f"""
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
            {where_clause}
            ORDER BY attendance.date DESC, attendance.marked_at DESC
            """,
            parameters,
        ).fetchall()
    finally:
        connection.close()


def get_analytics_data(
    user_id: int,
    role: str,
    course_id=None,
):
    connection = get_connection()
    conditions = []
    parameters = []

    if not is_admin(role):
        conditions.append("courses.instructor_id = ?")
        parameters.append(user_id)
    if course_id is not None:
        conditions.append("courses.id = ?")
        parameters.append(course_id)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    try:
        return connection.execute(
            f"""
            SELECT
                students.name,
                students.student_id,
                courses.course_name,
                COUNT(attendance.id) AS present_count
            FROM students
            JOIN enrollments ON students.id = enrollments.student_id
            JOIN courses ON enrollments.course_id = courses.id
            LEFT JOIN attendance
                ON students.id = attendance.student_id
                AND courses.id = attendance.course_id
            {where_clause}
            GROUP BY students.id, courses.id
            ORDER BY courses.course_name, students.name
            """,
            parameters,
        ).fetchall()
    finally:
        connection.close()


def get_student_enrollments(
    student_db_id: int,
    user_id: int,
    role: str,
):
    connection = get_connection()
    try:
        if is_admin(role):
            return connection.execute(
                """
                SELECT courses.id, courses.course_name, courses.course_code
                FROM enrollments
                JOIN courses ON enrollments.course_id = courses.id
                WHERE enrollments.student_id = ?
                ORDER BY courses.course_name, courses.course_code
                """,
                (student_db_id,),
            ).fetchall()
        return connection.execute(
            """
            SELECT courses.id, courses.course_name, courses.course_code
            FROM enrollments
            JOIN courses ON enrollments.course_id = courses.id
            WHERE enrollments.student_id = ?
              AND courses.instructor_id = ?
            ORDER BY courses.course_name, courses.course_code
            """,
            (student_db_id, user_id),
        ).fetchall()
    finally:
        connection.close()


def unenroll_student(
    student_db_id: int,
    course_id: int,
    user_id: int,
    role: str,
):
    if not can_access_course(course_id, user_id, role):
        raise PermissionError("You cannot manage enrollment for this course.")

    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            DELETE FROM enrollments
            WHERE student_id = ? AND course_id = ?
            """,
            (student_db_id, course_id),
        )
        connection.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        connection.rollback()
        raise
    finally:
        connection.close()


