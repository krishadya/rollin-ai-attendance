import time
from datetime import datetime
from pathlib import Path

import cv2
import streamlit as st

from camera_utils import open_camera
from database import (
    get_courses,
    get_student_by_student_id,
    is_student_enrolled,
    mark_attendance,
)
from face_utils import recognize_face
from ui import hint_text, metric_card, page_header, section_heading, status_banner


@st.dialog("Live Attendance Scan", width="large")
def _run_attendance_dialog(course_id, scan_seconds=15):
    cap, camera_index = open_camera()

    if cap is None:
        st.error("Unable to access webcam.")
        if st.button("Close", use_container_width=True, key="attendance_close_error"):
            st.rerun()
        return

    frame_placeholder = st.empty()
    status_placeholder = st.empty()

    marked_students = []
    already_marked_students = []
    not_enrolled_students = []
    unknown_count = 0

    start_time = time.time()
    last_check_time = 0

    while time.time() - start_time < scan_seconds:
        ret, frame = cap.read()

        if not ret:
            status_placeholder.error("Unable to read webcam frame.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(rgb_frame, channels="RGB")

        current_time = time.time()

        if current_time - last_check_time < 3:
            continue

        last_check_time = current_time
        test_path = Path("data/live_attendance.jpg")
        small_frame = cv2.resize(frame, (640, 480))
        cv2.imwrite(str(test_path), small_frame)

        result, error = recognize_face(test_path)

        if error:
            status_placeholder.warning(error)
            continue

        if result["status"] == "unknown":
            unknown_count += 1
            status_placeholder.warning(
                f"Unknown person detected. Similarity: {result['confidence']}%"
            )
            continue

        student = get_student_by_student_id(result["student_id"])

        if student is None:
            status_placeholder.error("Student not found.")
            continue

        _, name, student_id, _ = student

        if not is_student_enrolled(student_id, course_id):
            if name not in not_enrolled_students:
                not_enrolled_students.append(name)

            status_placeholder.error(
                f"{name} is recognized but not enrolled in this course."
            )
            continue

        success, message = mark_attendance(student_id, course_id)

        if success:
            if name not in marked_students:
                marked_students.append(name)

            status_placeholder.success(
                f"Attendance recorded for {name}. Confidence: {result['confidence']}%"
            )
        else:
            if name not in already_marked_students:
                already_marked_students.append(name)

            status_placeholder.warning(f"{name}: {message}")

    cap.release()
    frame_placeholder.empty()
    status_placeholder.success("Attendance session completed.")

    section_heading("Session Summary", "Review what happened in this scan.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Marked Present", len(marked_students), "New attendance records")
    with col2:
        metric_card("Already Marked", len(already_marked_students), "Previously recorded today")
    with col3:
        metric_card("Not Enrolled", len(not_enrolled_students), "Recognized outside this class")
    with col4:
        metric_card("Unknown", unknown_count, "Unmatched detections")

    list_col1, list_col2, list_col3 = st.columns(3)
    with list_col1:
        st.markdown("**Marked Students**")
        if marked_students:
            for student in marked_students:
                st.write(f"- {student}")
        else:
            st.caption("No new students were marked present.")
    with list_col2:
        st.markdown("**Already Marked**")
        if already_marked_students:
            for student in already_marked_students:
                st.write(f"- {student}")
        else:
            st.caption("No duplicate attendance attempts.")
    with list_col3:
        st.markdown("**Not Enrolled**")
        if not_enrolled_students:
            for student in not_enrolled_students:
                st.write(f"- {student}")
        else:
            st.caption("No recognized students were outside the selected course.")

    if st.button("Close", use_container_width=True, key="attendance_close_done"):
        st.rerun()


def show_attendance():
    page_header(
        "Take Attendance",
        "Start a live classroom scan and automatically record attendance."
    )

    now = datetime.now()
    status_banner(
        "Live session",
        f"Session Date: {now.strftime('%B %d, %Y')} | "
        f"Current Time: {now.strftime('%I:%M %p')}",
        tone="info",
    )

    courses = get_courses()

    if not courses:
        st.info("No courses are available. Create a course and enroll students before starting attendance.")
        return

    course_options = {
        f"{course[1]} ({course[2]})": course[0]
        for course in courses
    }

    section_heading("Course Selection", "Choose the active class before starting the scan.")
    selected_course = st.selectbox("Select Course", list(course_options.keys()))
    course_id = course_options[selected_course]

    hint_text(
        "The default session scans for 15 seconds and checks for recognizable faces every 3 seconds.",
        label="Scan settings",
    )

    if st.button("Start Attendance", use_container_width=True):
        _run_attendance_dialog(course_id)


if __name__ == "__main__":
    show_attendance()
