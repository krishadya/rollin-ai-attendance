import streamlit as st

from database import (
    get_total_courses,
    get_total_students,
    get_registered_faces_count,
    get_today_attendance_count,
)

from ui import page_header, metric_card, section_card


def show_dashboard():
    page_header(
        "🎓 RollIn Dashboard",
        "AI-powered attendance management for modern classrooms."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("👨‍🎓", "Students", get_total_students(), "Total enrolled")

    with col2:
        metric_card("📚", "Courses", get_total_courses(), "Active classes")

    with col3:
        metric_card("📷", "Faces", get_registered_faces_count(), "Registered profiles")

    with col4:
        metric_card("✅", "Today", get_today_attendance_count(), "Attendance marked")

    st.markdown("### 📌 Recent Activity")

    col5, col6 = st.columns(2)

    with col5:
        section_card(
            "System Status",
            "Face recognition and attendance scanning are active."
        )

    with col6:
        section_card(
            "Next Steps",
            "Use Take Attendance to start a live classroom scan."
        )