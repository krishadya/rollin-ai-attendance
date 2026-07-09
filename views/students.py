import streamlit as st
import pandas as pd
import sqlite3

from database import (
    add_student,
    enroll_student,
    get_students,
    get_courses,
    delete_student
)


def show_students():
    st.header("👨‍🎓 Student Management")

    st.subheader("Add Student")

    courses = get_courses()

    if not courses:
        st.warning("Please create a course before adding students.")
        return

    course_options = {
        f"{course[1]} ({course[2]})": course[0]
        for course in courses
    }

    with st.form("add_student_form"):

        name = st.text_input("Student Name")
        student_id = st.text_input("Student ID")
        email = st.text_input("Email")

        selected_course = st.selectbox(
            "Assign Course",
            list(course_options.keys())
        )

        submitted = st.form_submit_button("Add Student")

        if submitted:
            if name and student_id and email:
                try:
                    add_student(name, student_id, email)

                    students = get_students()
                    newest_student = max(students, key=lambda s: s[0])

                    enroll_student(
                        newest_student[0],
                        course_options[selected_course]
                    )

                    st.success("Student added successfully!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("A student with this Student ID already exists.")
            else:
                st.error("Please complete all fields.")


    st.subheader("Student List")

    students = get_students()

    if students:
        df = pd.DataFrame(
            students,
            columns=["ID", "Name", "Student ID", "Email", "Course", "Course Code"]
        )
        st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
    )
    else:
        st.info("No students added yet.")


if __name__ == "__main__":
    show_students()