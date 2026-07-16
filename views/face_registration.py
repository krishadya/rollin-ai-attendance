from pathlib import Path
import time

import cv2
import streamlit as st

from ui import page_header
from database import get_students, mark_face_registered
from face_utils import save_face_embedding


def show_face_registration():
    page_header(
        "Face Registration",
        "Capture a stable student face profile using the webcam."
    )

    students = get_students()

    if not students:
        st.warning("Please add students before registering faces.")
        return

    student_options = {
        f"{student[1]} ({student[2]})": student[0]
        for student in students
    }

    selected_student = st.selectbox(
        "Select Student",
        list(student_options.keys())
    )

    st.info("This version uses the Mac webcam directly and captures a stabilized frame.")

    if st.button("Capture Stable Face Photo"):
        camera_index = 1
        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
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

        student_db_id = student_options[selected_student]
        student_id_text = selected_student.split("(")[1].replace(")", "")

        image_path = Path(f"data/faces/{student_id_text}.jpg")
        cv2.imwrite(str(image_path), frame)

        embedding_path, error = save_face_embedding(student_id_text)

        if error:
            st.error(f"Face image saved, but embedding failed: {error}")
        else:
            mark_face_registered(student_db_id)
            status.success("Face registered successfully.")

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.image(rgb_frame, caption="Saved Face", width=350)


if __name__ == "__main__":
    show_face_registration()