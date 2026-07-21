import pandas as pd
import streamlit as st

from database import get_analytics_data, get_courses
from ui import metric_card, page_header, section_heading, status_banner


def show_analytics():
    page_header(
        "Analytics",
        "Track attendance performance by student and course."
    )

    user = st.session_state.user
    courses = get_courses(user_id=user["id"], role=user["role"])

    course_options = {"All Courses": None}
    for course in courses:
        course_options[f"{course[1]} ({course[2]})"] = course[0]

    section_heading("Course Filter", "Focus on a single class or review attendance across the full system.")
    selected_course = st.selectbox(
        "Filter by Course",
        options=["All Courses"] + [
            course_name for course_name in course_options.keys() if course_name != "All Courses"
        ],
        key="analytics_course_filter",
    )

    data = get_analytics_data(
        user_id=user["id"],
        role=user["role"],
        course_id=course_options[selected_course],
    )

    if not data:
        st.info("No analytics available yet. Attendance totals will appear here after students are marked present.")
        return

    df = pd.DataFrame(
        data,
        columns=["Name", "Student ID", "Course", "Present Count"],
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Students", df["Student ID"].nunique(), "Unique students")

    with col2:
        metric_card("Present Records", int(df["Present Count"].sum()), "Total check-ins")

    with col3:
        metric_card("Average", round(df["Present Count"].mean(), 2), "Per student/course")

    status_banner(
        "Summary view",
        "Use the export when you need a clean attendance snapshot for reports or downstream analysis.",
        tone="accent",
    )
    section_heading("Attendance Summary", "Per-student attendance totals for the selected scope.")
    display_df = df.copy()
    display_df["Present Count"] = display_df["Present Count"].astype(str)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Analytics CSV",
        data=csv,
        file_name="attendance_analytics.csv",
        mime="text/csv",
        use_container_width=True,
    )


if __name__ == "__main__":
    show_analytics()
