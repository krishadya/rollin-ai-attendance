from pathlib import Path
import time

import cv2
import streamlit as st

from camera_utils import open_camera
from database import get_students, mark_face_registered
from face_utils import save_face_embedding
from ui import (
    hint_text,
    page_header,
    queue_widget_reset,
    section_heading,
    set_flash_success,
    status_banner,
)


FACE_DIALOG_OPEN_KEY = "face_dialog_open"
FACE_CAPTURE_REQUESTED_KEY = "face_capture_requested"
FACE_CAPTURE_STARTED_KEY = "face_capture_started"
FACE_CAPTURE_COMPLETE_KEY = "face_capture_complete"
FACE_CAPTURE_SUCCESS_KEY = "face_capture_success"
FACE_CAPTURE_RESULT_KEY = "face_capture_result"
FACE_SELECTED_STUDENT_KEY = "face_selected_student"
FACE_STUDENT_SELECTBOX_KEY = "face_registration_student_selection"


def _ensure_face_registration_state():
    defaults = {
        FACE_DIALOG_OPEN_KEY: False,
        FACE_CAPTURE_REQUESTED_KEY: False,
        FACE_CAPTURE_STARTED_KEY: False,
        FACE_CAPTURE_COMPLETE_KEY: False,
        FACE_CAPTURE_SUCCESS_KEY: False,
        FACE_CAPTURE_RESULT_KEY: None,
        FACE_SELECTED_STUDENT_KEY: None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _clear_face_registration_state():
    st.session_state[FACE_DIALOG_OPEN_KEY] = False
    st.session_state[FACE_CAPTURE_REQUESTED_KEY] = False
    st.session_state[FACE_CAPTURE_STARTED_KEY] = False
    st.session_state[FACE_CAPTURE_COMPLETE_KEY] = False
    st.session_state[FACE_CAPTURE_SUCCESS_KEY] = False
    st.session_state[FACE_CAPTURE_RESULT_KEY] = None
    st.session_state[FACE_SELECTED_STUDENT_KEY] = None


def _run_capture_once(
    student_db_id,
    student_id_text,
    student_display_name,
    preview_placeholder,
    status_placeholder,
):
    if st.session_state.get(FACE_CAPTURE_COMPLETE_KEY):
        return

    preview_image = None
    camera = None

    try:
        camera, _ = open_camera()

        if camera is None:
            st.session_state[FACE_CAPTURE_REQUESTED_KEY] = False
            st.session_state[FACE_CAPTURE_RESULT_KEY] = {
                "success": False,
                "message": "Unable to access webcam.",
                "image_path": None,
            }
            return

        frame = None
        start_time = time.time()
        status_placeholder.info("Opening webcam and stabilizing image...")

        while time.time() - start_time < 3:
            ret, frame = camera.read()
            if not ret:
                continue

            frame = cv2.resize(frame, (640, 480))
            preview_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            preview_placeholder.image(preview_image, channels="RGB")

        if frame is None:
            st.session_state[FACE_CAPTURE_REQUESTED_KEY] = False
            st.session_state[FACE_CAPTURE_RESULT_KEY] = {
                "success": False,
                "message": "Unable to capture image.",
                "image_path": None,
            }
            return

        image_path = Path(f"data/faces/{student_id_text}.jpg")
        cv2.imwrite(str(image_path), frame)

        _, error = save_face_embedding(student_id_text)
        preview_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if error:
            st.session_state[FACE_CAPTURE_REQUESTED_KEY] = False
            st.session_state[FACE_CAPTURE_RESULT_KEY] = {
                "success": False,
                "message": f"Face image saved, but embedding generation failed: {error}",
                "image_path": str(image_path),
                "preview_image": preview_image,
            }
            return

        mark_face_registered(student_db_id)
        success_message = (
            f"Face profile registered successfully for {student_display_name}."
        )

        st.session_state[FACE_CAPTURE_COMPLETE_KEY] = True
        st.session_state[FACE_CAPTURE_REQUESTED_KEY] = False
        st.session_state[FACE_CAPTURE_SUCCESS_KEY] = True
        st.session_state[FACE_CAPTURE_RESULT_KEY] = {
            "success": True,
            "message": success_message,
            "image_path": str(image_path),
            "preview_image": preview_image,
        }
    finally:
        if camera is not None:
            camera.release()
        cv2.destroyAllWindows()
        st.session_state[FACE_CAPTURE_STARTED_KEY] = False


@st.dialog("Capture Face Profile", width="large")
def _run_capture_dialog(student_options):
    selected_student = st.session_state.get(FACE_SELECTED_STUDENT_KEY)

    if not selected_student or selected_student not in student_options:
        st.error("Selected student could not be found.")
        if st.button("Close", use_container_width=True, key="face_capture_close_missing"):
            _clear_face_registration_state()
            st.rerun()
        return

    student_db_id, student_id_text = student_options[selected_student]
    student_display_name = selected_student.split(" (")[0]
    capture_result = st.session_state.get(FACE_CAPTURE_RESULT_KEY)
    preview_col_left, preview_col_center, preview_col_right = st.columns([1, 3, 1])
    with preview_col_center:
        preview_placeholder = st.empty()
    status_placeholder = st.empty()

    st.caption(f"Capturing a face profile for **{student_display_name}**.")

    if (
        st.session_state.get(FACE_DIALOG_OPEN_KEY)
        and st.session_state.get(FACE_CAPTURE_REQUESTED_KEY)
        and not st.session_state.get(FACE_CAPTURE_COMPLETE_KEY)
        and not st.session_state.get(FACE_CAPTURE_STARTED_KEY)
    ):
        st.session_state[FACE_CAPTURE_STARTED_KEY] = True
        _run_capture_once(
            student_db_id,
            student_id_text,
            student_display_name,
            preview_placeholder,
            status_placeholder,
        )
        capture_result = st.session_state.get(FACE_CAPTURE_RESULT_KEY)

    if (
        st.session_state.get(FACE_CAPTURE_REQUESTED_KEY)
        and not st.session_state.get(FACE_CAPTURE_COMPLETE_KEY)
        and capture_result is None
    ):
        status_placeholder.info("Opening webcam and stabilizing image...")

    capture_result = st.session_state.get(FACE_CAPTURE_RESULT_KEY)

    if capture_result and capture_result.get("preview_image") is not None:
        preview_placeholder.image(
            capture_result["preview_image"],
            channels="RGB",
            caption="Saved Face Profile",
        )

    if capture_result and capture_result.get("success"):
        status_placeholder.success(capture_result["message"])
    elif capture_result and capture_result.get("message"):
        status_placeholder.error(capture_result["message"])

    if st.session_state.get(FACE_CAPTURE_COMPLETE_KEY):
        if st.button("Done", use_container_width=True, key="face_capture_done"):
            success_message = st.session_state.get(FACE_CAPTURE_RESULT_KEY, {}).get("message")
            queue_widget_reset(FACE_STUDENT_SELECTBOX_KEY)
            if success_message:
                set_flash_success(success_message)
            _clear_face_registration_state()
            st.rerun()
    else:
        if st.button("Close", use_container_width=True, key="face_capture_close"):
            _clear_face_registration_state()
            st.rerun()


def show_face_registration():
    _ensure_face_registration_state()

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
    selected_student = st.selectbox(
        "Select Student",
        list(student_options.keys()),
        index=None,
        placeholder="--- Select Student ---",
        key=FACE_STUDENT_SELECTBOX_KEY,
    )

    hint_text(
        "The webcam opens briefly, stabilizes the view, and saves the final frame for embedding generation.",
        label="How capture works",
    )

    if st.button("Capture Face", use_container_width=True):
        if selected_student is None:
            st.error("Please select a student.")
            return

        st.session_state[FACE_SELECTED_STUDENT_KEY] = selected_student
        st.session_state[FACE_DIALOG_OPEN_KEY] = True
        st.session_state[FACE_CAPTURE_REQUESTED_KEY] = True
        st.session_state[FACE_CAPTURE_STARTED_KEY] = False
        st.session_state[FACE_CAPTURE_COMPLETE_KEY] = False
        st.session_state[FACE_CAPTURE_SUCCESS_KEY] = False
        st.session_state[FACE_CAPTURE_RESULT_KEY] = None

    if st.session_state.get(FACE_DIALOG_OPEN_KEY):
        _run_capture_dialog(student_options)


if __name__ == "__main__":
    show_face_registration()
