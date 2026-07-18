from pathlib import Path
import time

import cv2
import streamlit as st

from camera_utils import open_camera
from database import get_students, mark_face_registered
from face_utils import save_face_embedding
from ui import hint_text, page_header, section_heading, status_banner


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
        st.warning("Please add students before registering faces.")
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
        cap, camera_index = open_camera()

        if cap is None:
            st.error("Unable to access webcam.")
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
            st.error("Unable to capture image.")
            return

        student_db_id, student_id_text = student_options[selected_student]

        image_path = Path(f"data/faces/{student_id_text}.jpg")
        cv2.imwrite(str(image_path), frame)

        _, error = save_face_embedding(student_id_text)

        if error:
            st.error(f"Face image saved, but embedding generation failed: {error}")
            return

        mark_face_registered(student_db_id)
        status.success("Face profile registered successfully.")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(rgb_frame, caption="Saved Face Profile", width=360)


if __name__ == "__main__":
    show_face_registration()
