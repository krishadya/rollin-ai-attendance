import streamlit as st
import pandas as pd

from database import get_courses, get_attendance_records
from ui import page_header


def show_history():
    page_header(
        "📜 Attendance History",
        "View attendance records by course."
    )

    courses = get_courses()

    course_options = {"All Courses": None}

    for course in courses:
        course_options[f"{course[1]} ({course[2]})"] = course[0]

    selected_course = st.selectbox(
        "Filter by Course",
        list(course_options.keys())
    )

    records = get_attendance_records(course_options[selected_course])

    if records:
        df = pd.DataFrame(
            records,
            columns=[
                "Name",
                "Student ID",
                "Course",
                "Course Code",
                "Date",
                "Marked At",
                "Status",
            ],
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="attendance_history.csv",
            mime="text/csv"
        )

    else:
        st.info("No attendance records found.")


if __name__ == "__main__":
    show_history()