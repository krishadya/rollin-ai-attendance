import pandas as pd
import streamlit as st

from database import add_course, delete_course, get_courses
from ui import (
    page_header,
    queue_widget_reset,
    section_heading,
    set_flash_success,
    status_banner,
)


def show_courses():
    user = st.session_state.user

    page_header(
        "Courses",
        "Create and manage the courses that use RollIn attendance.",
    )

    status_banner(
        "Course setup",
        (
            "Administrators can manage every course. Instructors can manage "
            "only the courses they create."
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
                add_course(course_name, course_code, user["id"])
                set_flash_success("Course added successfully.")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
            except Exception:
                st.error("The course could not be added. Please try again.")

    st.divider()

    section_heading(
        "Course List",
        (
            "All courses in the system."
            if user["role"] == "admin"
            else "Courses created by you."
        ),
    )

    courses = get_courses(user_id=user["id"], role=user["role"])

    if not courses:
        st.info(
            "No courses yet. Create your first course above to begin enrolling students."
        )
        return

    course_dataframe = pd.DataFrame(
        courses,
        columns=["ID", "Course Name", "Course Code", "Instructor"],
    )

    st.dataframe(
        course_dataframe.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    section_heading(
        "Delete Course",
        "Deleting a course also removes its enrollments and attendance records.",
    )

    course_options = {
        f"{course[1]} ({course[2]})": course[0]
        for course in courses
    }

    selected_course = st.selectbox(
        "Select Course",
        options=list(course_options.keys()),
        index=None,
        placeholder="--- Select Course ---",
        key="delete_course_selection",
    )

    st.warning(
        "This action permanently removes the course, its enrollments, and its attendance records."
    )
    confirm_delete = st.checkbox(
        "I understand that this action cannot be undone.",
        key="confirm_course_delete",
    )

    if st.button(
        "Delete Course",
        use_container_width=True,
        key="delete_course_button",
        disabled=not confirm_delete,
    ):
        if selected_course is None:
            st.error("Please select a course.")
            return

        try:
            delete_course(
                course_id=course_options[selected_course],
                user_id=user["id"],
                role=user["role"],
            )
            queue_widget_reset("delete_course_selection")
            set_flash_success("Course deleted successfully.")
            st.rerun()
        except PermissionError as error:
            st.error(str(error))
        except Exception:
            st.error("The course could not be deleted. Please try again.")
