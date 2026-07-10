import streamlit as st
from database import get_students
from database import get_students, mark_face_registered
from face_utils import capture_face_image


def show_face_registration():
    st.header("📷 Face Registration")

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

    camera_image = st.camera_input("Take a face photo")

    if camera_image is not None:
        student_db_id = student_options[selected_student]
        student_id_text = selected_student.split("(")[1].replace(")", "")

        image_path = f"data/faces/{student_id_text}.jpg"

        with open(image_path, "wb") as file:
            file.write(camera_image.getbuffer())

        mark_face_registered(student_db_id)

        st.success("Face registered successfully!")
        st.image(image_path, caption="Saved Face", width=300)