import streamlit as st

from database import (
    get_total_courses,
    get_total_students,
    get_today_attendance_count
)


def show_dashboard():
    st.header("📊 Dashboard")

    total_courses = get_total_courses()
    total_students = get_total_students()
    today_attendance = get_today_attendance_count()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📚 Courses", total_courses)

    with col2:
        st.metric("👨‍🎓 Students", total_students)

    with col3:
        st.metric("✅ Attendance Today", today_attendance)

    st.divider()

    st.subheader("Welcome to RollIn")
    st.write("Use the sidebar to manage courses, students, attendance, and analytics.")