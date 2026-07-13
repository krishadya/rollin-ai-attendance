import time
from pathlib import Path

import cv2
import streamlit as st

from database import (
    get_courses,
    is_student_enrolled,
    mark_attendance,
    get_student_by_student_id,
)

from face_utils import recognize_face


def show_attendance():
    st.header("✅ Take Attendance")

    courses = get_courses()

    if not courses:
        st.warning("Please create a course first.")
        return

    course_options = {
        f"{course[1]} ({course[2]})": course[0]
        for course in courses
    }

    selected_course = st.selectbox("Select Course", list(course_options.keys()))
    course_id = course_options[selected_course]

    if st.button("Start Attendance Scan"):
        camera_index = 1
        scan_seconds = 15

        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
            st.error("Could not open webcam.")
            return

        frame_placeholder = st.empty()
        status_placeholder = st.empty()
        summary_placeholder = st.empty()

        marked_students = []
        already_marked_students = []
        not_enrolled_students = []
        unknown_count = 0

        start_time = time.time()
        last_check_time = 0

        while time.time() - start_time < scan_seconds:
            ret, frame = cap.read()

            if not ret:
                status_placeholder.error("Could not read webcam frame.")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(rgb_frame, channels="RGB")

            current_time = time.time()

            # Run recognition once every 2 seconds
            if current_time - last_check_time >= 2:
                last_check_time = current_time

                test_path = Path("data/live_attendance.jpg")
                cv2.imwrite(str(test_path), frame)

                result, error = recognize_face(test_path)

                if error:
                    status_placeholder.warning(error)
                    continue

                if result["status"] == "unknown":
                    unknown_count += 1
                    status_placeholder.warning(
                        f"❌ Unknown person detected. Similarity: {result['confidence']}%"
                    )
                    continue

                student = get_student_by_student_id(result["student_id"])

                if student is None:
                    status_placeholder.error("Student not found in database.")
                    continue

                _, name, student_id, email = student

                if not is_student_enrolled(student_id, course_id):
                    if name not in not_enrolled_students:
                        not_enrolled_students.append(name)

                    status_placeholder.error(
                        f"❌ {name} is recognized but not enrolled in this course."
                    )
                    continue

                success, message = mark_attendance(student_id, course_id)

                if success:
                    if name not in marked_students:
                        marked_students.append(name)

                    status_placeholder.success(
                        f"✅ Attendance marked for {name} | Confidence: {result['confidence']}%"
                    )

                else:
                    if name not in already_marked_students:
                        already_marked_students.append(name)

                    status_placeholder.warning(f"⚠️ {name}: {message}")

        cap.release()

        st.success("Attendance scan complete.")

        summary_placeholder.subheader("Session Summary")

        st.write(f"✅ Newly Marked Present: {len(marked_students)}")
        for student in marked_students:
            st.write(f"- {student}")

        st.write(f"⚠️ Already Marked: {len(already_marked_students)}")
        for student in already_marked_students:
            st.write(f"- {student}")

        st.write(f"❌ Not Enrolled: {len(not_enrolled_students)}")
        for student in not_enrolled_students:
            st.write(f"- {student}")

        st.write(f"❓ Unknown Detections: {unknown_count}")


if __name__ == "__main__":
    show_attendance()