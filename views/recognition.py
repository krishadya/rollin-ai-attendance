import streamlit as st
from pathlib import Path

from face_utils import recognize_face
from database import get_student_by_student_id


def show_recognition():
    st.header("🔍 Face Recognition Test")

    camera_image = st.camera_input("Take a test photo")

    if camera_image is not None:
        test_path = Path("data/test_face.jpg")

        with open(test_path, "wb") as file:
            file.write(camera_image.getbuffer())

        result, error = recognize_face(test_path)

        if error:
            st.error(error)
            return

        student = get_student_by_student_id(result["student_id"])

        if student is None:
            st.error("Student not found in database.")
            return

        _, name, student_id, email = student

        if result["status"] == "recognized":
            st.success("✅ Face Recognized")

            st.subheader(name)

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Student ID:** {student_id}")

            with col2:
                st.write(f"**Confidence:** {result['confidence']}%")

            st.write(f"**Email:** {email}")

        else:
            st.error("❌ Unknown Person")

            st.write(f"Closest Match: {name}")
            st.write(f"Student ID: {student_id}")
            st.write(f"Highest Similarity: {result['confidence']}%")


if __name__ == "__main__":
    show_recognition()