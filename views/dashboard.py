import streamlit as st

from database import (
    get_total_courses,
    get_total_students,
    get_registered_faces_count,
    get_today_attendance_count,
)


def show_dashboard():

    st.header("🎓 RollIn Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="👨‍🎓 Students",
            value=get_total_students()
        )

    with col2:
        st.metric(
            label="📚 Courses",
            value=get_total_courses()
        )

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            label="📷 Registered Faces",
            value=get_registered_faces_count()
        )

    with col4:
        st.metric(
            label="✅ Attendance Today",
            value=get_today_attendance_count()
        )

    st.divider()

    st.subheader("📌 Recent Activity")

    st.info("Activity feed coming soon.")

    st.write("• Students can now enroll in multiple courses.")
    st.write("• Face registration is enabled.")
    st.write("• AI attendance recognition is the next milestone.")