import streamlit as st
import pandas as pd
from ui import page_header

from database import (
    add_student,
    enroll_student,
    get_students,
    get_courses,
    delete_student,
    get_student_by_student_id,
    enrollment_exists,
)


def show_students():
    page_header(
    "👨‍🎓 Student Management",
    "Add students, enroll them in courses, and track face registration."
)
    st.subheader("Add Student")

    courses = get_courses()

    if not courses:
        st.warning("Please create a course before adding students.")
        return

    if "student_form_key" not in st.session_state:
        st.session_state.student_form_key = 0

    course_options = {
        f"{course[1]} ({course[2]})": course[0]
        for course in courses
    }

    with st.form(f"add_student_form_{st.session_state.student_form_key}"):
        name = st.text_input("Student Name", placeholder="Tom Harrison")
        student_id = st.text_input("Student ID", placeholder="987654321")
        email = st.text_input("Email", placeholder="student@example.com")

        selected_course = st.selectbox(
            "Assign Course",
            list(course_options.keys())
        )

        submitted = st.form_submit_button("Add Student")

        if submitted:
            if name and student_id and email:
                course_id = course_options[selected_course]
                existing_student = get_student_by_student_id(student_id)

                if existing_student:
                    student_db_id = existing_student[0]

                    if enrollment_exists(student_db_id, course_id):
                        st.error("This student is already enrolled in this course.")
                    else:
                        enroll_student(student_db_id, course_id)
                        st.success("Existing student enrolled in another course.")
                        st.session_state.student_form_key += 1
                        st.rerun()

                else:
                    add_student(name, student_id, email)

                    students = get_students()
                    newest_student = max(students, key=lambda s: s[0])

                    enroll_student(newest_student[0], course_id)

                    st.success("New student added and enrolled successfully!")
                    st.session_state.student_form_key += 1
                    st.rerun()
            else:
                st.error("Please complete all fields.")

    st.subheader("Student List")

    students = get_students()

    if students:
        df = pd.DataFrame(
            students,
            columns=[
                "ID",
                "Name",
                "Student ID",
                "Email",
                "Course",
                "Course Code",
                "Face Registered",
            ],
        )

        df["Face Registered"] = df["Face Registered"].map({
            1: "✅ Yes",
            0: "❌ No",
        })

        display_df = df.drop(columns=["ID"])

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Delete Student")

        student_options = {
            f"{student[1]} ({student[2]})": student[0]
            for student in students
        }

        selected_student = st.selectbox(
            "Select student to delete",
            list(student_options.keys())
        )

        if st.button("Delete Student"):
            delete_student(student_options[selected_student])
            st.warning("Student deleted.")
            st.rerun()

    else:
        st.info("No students added yet.")


if __name__ == "__main__":
    show_students()