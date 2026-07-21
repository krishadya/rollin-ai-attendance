import pandas as pd
import streamlit as st

from database import get_attendance_records, get_courses
from ui import page_header, section_heading, status_banner


def show_history():
    page_header(
        "Attendance History",
        "Review attendance records and export course reports."
    )

    courses = get_courses()
    course_options = {"All Courses": None}

    for course in courses:
        course_options[f"{course[1]} ({course[2]})"] = course[0]

    status_banner(
        "Reporting",
        "Filter by course to isolate a class report, or keep all records visible for broader review.",
        tone="info",
    )
    section_heading("Course Filter", "Switch between a specific class and the full attendance log.")
    selected_course = st.selectbox(
        "Filter by Course",
        options=["All Courses"] + [
            course_name for course_name in course_options.keys() if course_name != "All Courses"
        ],
        key="history_course_filter",
    )

    records = get_attendance_records(course_options[selected_course])

    if not records:
        st.info("No attendance records found. Start an attendance session to generate the first classroom record.")
        return

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

    section_heading("Attendance Log", "Chronological classroom check-ins across the selected scope.")
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="attendance_history.csv",
        mime="text/csv",
        use_container_width=True,
    )


if __name__ == "__main__":
    show_history()
