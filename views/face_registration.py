from pathlib import Path
import time

import cv2
import streamlit as st

from camera_utils import open_camera
from database import get_students, mark_face_registered
from face_utils import save_face_embedding
from ui import hint_text, page_header, section_heading, status_banner


@st.dialog("Capture Face Profile", width="large")
def _run_capture_dialog(selected_student, student_options):
    student_db_id, student_id_text = student_options[selected_student]
    student_display_name = selected_student.split(" (")[0]

    st.caption(f"Capturing a face profile for **{student_display_name}**.")

    cap, camera_index = open_camera()

    if cap is None:
        st.error("Unable to access webcam.")
        if st.button("Close", use_container_width=True, key="face_capture_close_error"):
            st.rerun()
        return

    preview = st.empty()
    status = st.empty()
    status.info("Opening webcam and stabilizing image...")

    frame = None
    start_time = time.time()

    while time.time() - start_time < 3:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.resize(frame, (640, 480))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        preview.image(rgb_frame, channels="RGB")

    cap.release()

    if frame is None:
        status.error("Unable to capture image.")
        if st.button("Close", use_container_width=True, key="face_capture_close_fail"):
            st.rerun()
        return

    image_path = Path(f"data/faces/{student_id_text}.jpg")
    cv2.imwrite(str(image_path), frame)

    _, error = save_face_embedding(student_id_text)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    preview.image(rgb_frame, channels="RGB", caption="Saved Face Profile")

    if error:
        status.error(f"Face image saved, but embedding generation failed: {error}")
    else:
        mark_face_registered(student_db_id)
        status.success(f"Face profile registered successfully for {student_display_name}.")

    if st.button("Done", use_container_width=True, key="face_capture_done"):
        st.rerun()


def show_face_registration():
    page_header(
        "Face Registration",
        "Capture a stable student face profile for attendance recognition."
    )

    status_banner(
        "Capture quality",
        "Use stable lighting, keep the face centered, and avoid multiple people in the frame.",
        tone="accent",
    )

    students = get_students()

    if not students:
        st.info("No students are available. Add a student before registering a face profile.")
        return

    student_options = {
        f"{student[1]} ({student[2]})": (student[0], student[2])
        for student in students
    }

    section_heading("Student Selection", "Choose the enrolled student whose face profile you want to register.")
    selected_student = st.selectbox("Select Student", list(student_options.keys()))

    hint_text(
        "The webcam opens briefly, stabilizes the view, and saves the final frame for embedding generation.",
        label="How capture works",
    )

    if st.button("Capture Face", use_container_width=True):
        _run_capture_dialog(selected_student, student_options)


if __name__ == "__main__":
    show_face_registration()
