import streamlit as st

from database import (
    get_registered_faces_count,
    get_today_attendance_count,
    get_total_courses,
    get_total_students,
)
from ui import metric_card, page_header, section_card, section_heading, status_banner


def show_dashboard():
    page_header(
        "Dashboard",
        "Monitor classroom attendance, student records, and face registration status."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Students", get_total_students(), "Total enrolled")

    with col2:
        metric_card("Courses", get_total_courses(), "Active classes")

    with col3:
        metric_card("Face Profiles", get_registered_faces_count(), "Registered profiles")

    with col4:
        metric_card("Today", get_today_attendance_count(), "Attendance records")

    status_banner(
        "Recommended flow",
        "Create courses, add students, register face profiles, then start attendance scanning.",
        tone="accent",
    )

    section_heading("Overview", "A quick read on platform readiness.")

    section_card(
        "System Status",
        "Face registration, recognition, attendance history, and analytics are all available."
    )
