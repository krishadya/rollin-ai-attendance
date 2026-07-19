from datetime import datetime

import streamlit as st

from database import (
    get_registered_faces_count,
    get_today_attendance_count,
    get_total_courses,
    get_total_students,
)
from ui import (
    metric_card,
    page_header,
    section_card,
    section_heading,
    status_banner,
    step_card,
)


def _navigate(page_name: str) -> None:
    """Navigate to another page using the top navigation state."""
    st.session_state.pending_page = page_name
    st.rerun()


def show_dashboard():
    user_name = st.session_state.user.get("name", "there")
    today = datetime.now().strftime("%A, %B %d, %Y")

    page_header(
        f"Welcome back, {user_name}",
        f"Here is what is happening in RollIn today. {today}",
    )

    total_students = get_total_students()
    total_courses = get_total_courses()
    registered_faces = get_registered_faces_count()
    today_attendance = get_today_attendance_count()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Students",
            total_students,
            "Student profiles",
        )

    with col2:
        metric_card(
            "Courses",
            total_courses,
            "Active classes",
        )

    with col3:
        metric_card(
            "Face Profiles",
            registered_faces,
            "Ready for recognition",
        )

    with col4:
        metric_card(
            "Attendance Today",
            today_attendance,
            "Check-ins recorded",
        )

    if total_courses == 0:
        status_banner(
            "Start with a course",
            (
                "Create your first course, then add students and "
                "register their face profiles."
            ),
            tone="accent",
        )

    elif total_students == 0:
        status_banner(
            "Add your first student",
            (
                "Your course is ready. Create a student profile "
                "and enroll the student next."
            ),
            tone="accent",
        )

    elif registered_faces < total_students:
        status_banner(
            "Face registration in progress",
            (
                f"{total_students - registered_faces} student "
                "profile(s) still need a registered face."
            ),
            tone="info",
        )

    else:
        status_banner(
            "Ready for attendance",
            (
                "Courses, students, and face profiles are available "
                "for classroom scanning."
            ),
            tone="accent",
        )

    section_heading(
        "Platform Status",
        (
            "A quick view of the setup required for reliable "
            "attendance sessions."
        ),
    )

    status_col1, status_col2 = st.columns(2)

    with status_col1:
        section_card(
            "Courses",
            (
                "Ready"
                if total_courses
                else "No courses have been created yet."
            ),
        )

        section_card(
            "Students",
            (
                "Ready"
                if total_students
                else "No student profiles have been added yet."
            ),
        )

    with status_col2:
        section_card(
            "Face Recognition",
            (
                f"{registered_faces} of {total_students} "
                "student profiles registered."
                if total_students
                else "Add students before registering face profiles."
            ),
        )

        section_card(
            "Attendance",
            (
                "Ready to start a classroom scan."
                if (
                    total_courses
                    and total_students
                    and registered_faces
                )
                else (
                    "Complete course, student, and face setup "
                    "before scanning."
                )
            ),
        )

    section_heading(
        "Getting Started",
        "Complete these steps in order for the best results.",
    )

    step1, step2, step3, step4 = st.columns(4)

    with step1:
        step_card(
            1,
            "Create Course",
            "Add the class that will use attendance tracking.",
        )

    with step2:
        step_card(
            2,
            "Add Student",
            (
                "Create the student profile once, then enroll the "
                "student in a course."
            ),
        )

    with step3:
        step_card(
            3,
            "Register Face",
            (
                "Capture a clear, well-lit face image for reliable "
                "recognition."
            ),
        )

    with step4:
        step_card(
            4,
            "Take Attendance",
            (
                "Select a course and begin the classroom attendance "
                "session."
            ),
        )

    section_heading(
        "Quick Actions",
        "Go directly to the most common RollIn tasks.",
    )

    action1, action2, action3, action4 = st.columns(4)

    with action1:
        if st.button(
            "Add Course",
            use_container_width=True,
            key="dashboard_add_course",
        ):
            _navigate("Courses")

    with action2:
        if st.button(
            "Add Student",
            use_container_width=True,
            key="dashboard_add_student",
        ):
            _navigate("Students")

    with action3:
        if st.button(
            "Register Face",
            use_container_width=True,
            key="dashboard_register_face",
        ):
            _navigate("Face Registration")

    with action4:
        if st.button(
            "Take Attendance",
            use_container_width=True,
            key="dashboard_take_attendance",
        ):
            _navigate("Take Attendance")