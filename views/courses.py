import streamlit as st
import pandas as pd
from database import add_course, get_courses, delete_course
from ui import page_header


def show_courses():
    page_header(
    "📚 Courses",
    "Create and manage classroom courses."
)

    st.subheader("Add New Course")

    with st.form("add_course_form"):
        course_name = st.text_input("Course Name", placeholder="Software Engineering")
        course_code = st.text_input("Course Code", placeholder="CSC 648")
        submitted = st.form_submit_button("Add Course")

        if submitted:
            if course_name and course_code:
                add_course(course_name, course_code, st.session_state.user["id"])
                st.success("Course added successfully!")
                st.rerun()
            else:
                st.error("Please fill in both course name and course code.")

    st.subheader("All Courses")

    courses = get_courses()

    if courses:
        df = pd.DataFrame(
            courses,
            columns=["ID", "Course Name", "Course Code", "Instructor"]
        )
        st.dataframe(df, use_container_width=True)

        st.subheader("Delete Course")
        course_options = {f"{course[1]} ({course[2]})": course[0] for course in courses}
        selected_course = st.selectbox("Select course to delete", course_options.keys())

        if st.button("Delete Course"):
            delete_course(course_options[selected_course])
            st.warning("Course deleted.")
            st.rerun()
    else:
        st.info("No courses added yet.")

        