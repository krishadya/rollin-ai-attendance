import streamlit as st
import pandas as pd

from database import get_courses, get_analytics_data
from ui import page_header


def show_analytics():
    page_header(
        "📈 Analytics",
        "Track attendance performance by student and course."
    )

    courses = get_courses()

    course_options = {"All Courses": None}
    for course in courses:
        course_options[f"{course[1]} ({course[2]})"] = course[0]

    selected_course = st.selectbox(
        "Filter by Course",
        list(course_options.keys())
    )

    data = get_analytics_data(course_options[selected_course])

    if not data:
        st.info("No analytics data available yet.")
        return

    df = pd.DataFrame(
        data,
        columns=["Name", "Student ID", "Course", "Present Count"]
    )

    st.subheader("Attendance Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Students", df["Student ID"].nunique())

    with col2:
        st.metric("Total Present Records", int(df["Present Count"].sum()))

    with col3:
        st.metric("Average Present Count", round(df["Present Count"].mean(), 2))

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Analytics CSV",
        data=csv,
        file_name="attendance_analytics.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    show_analytics()