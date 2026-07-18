import pandas as pd
import streamlit as st

from database import add_course, delete_course, get_courses
from ui import page_header, section_heading, status_banner


def show_courses():
    page_header(
        "Courses",
        "Create and manage the courses that use RollIn attendance.",
    )

    status_banner(
        "Course setup",
        (
            "Use clear course names and unique course codes so attendance "
            "and reporting remain organized."
        ),
        tone="info",
    )

    section_heading(
        "Add Course",
        "Create a new course before enrolling students.",
    )

    with st.form("add_course_form", clear_on_submit=True):
        course_name = st.text_input(
            "Course Name",
            placeholder="Software Engineering",
        )

        course_code = st.text_input(
            "Course Code",
            placeholder="CSC 648",
        )

        submitted = st.form_submit_button(
            "Add Course",
            use_container_width=True,
        )

    if submitted:
        if not course_name.strip() or not course_code.strip():
            st.error("Please enter both a course name and course code.")

        else:
            try:
                add_course(
                    course_name,
                    course_code,
                    st.session_state.user["id"],
                )

                st.success("Course added successfully.")
                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception:
                st.error(
                    "The course could not be added. Please try again."
                )

    section_heading(
        "Course List",
        "Current courses available in the RollIn workspace.",
    )

    courses = get_courses()

    if not courses:
        st.info("No courses have been added yet.")
        return

    course_dataframe = pd.DataFrame(
        courses,
        columns=[
            "ID",
            "Course Name",
            "Course Code",
            "Instructor",
        ],
    )

    st.dataframe(
        course_dataframe.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True,
    )

    section_heading(
        "Delete Course",
        (
            "Deleting a course also removes its enrollments and "
            "attendance records."
        ),
    )

    course_options = {
        f"{course[1]} ({course[2]})": course[0]
        for course in courses
    }

    selected_course = st.selectbox(
        "Select Course",
        options=list(course_options.keys()),
        key="delete_course_selection",
    )

    if st.button(
        "Delete Course",
        use_container_width=True,
        key="delete_course_button",
    ):
        delete_course(course_options[selected_course])

        st.success("Course deleted successfully.")
        st.rerun()