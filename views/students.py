import pandas as pd
import streamlit as st

from database import (
    add_student,
    delete_student,
    enrollment_exists,
    enroll_student,
    get_courses,
    get_student_enrollments,
    get_students,
    unenroll_student,
)
from ui import page_header, queue_widget_reset, section_heading, set_flash_success, status_banner


def _course_count(course_codes: str) -> int:
    if not course_codes or not course_codes.strip():
        return 0
    return len([code for code in course_codes.split(",") if code.strip()])


def show_students():
    page_header(
        "Students",
        (
            "Create student profiles, manage course enrollment, and review "
            "face-registration readiness."
        ),
    )

    status_banner(
        "Student workflow",
        (
            "Create each student once. Then select the existing student to enroll "
            "or unenroll them from courses."
        ),
        tone="info",
    )

    courses = get_courses()
    students = get_students()

    section_heading(
        "Add Student",
        "Create a student profile before assigning the student to a course.",
    )

    with st.form("add_student_form", clear_on_submit=True):
        student_name = st.text_input("Student Name", placeholder="Tom Harrison")
        student_number = st.text_input("Student ID", placeholder="987654321")
        student_email = st.text_input("Email", placeholder="student@example.com")
        add_submitted = st.form_submit_button(
            "Add Student",
            use_container_width=True,
        )

    if add_submitted:
        if not student_name.strip() or not student_number.strip() or not student_email.strip():
            st.error("Please complete all student fields.")
        else:
            try:
                add_student(student_name, student_number, student_email)
                set_flash_success(
                    "Student added successfully. You can now enroll the student below."
                )
                st.rerun()
            except ValueError as error:
                st.error(str(error))
            except Exception:
                st.error("The student could not be added. Please try again.")

    st.divider()

    section_heading(
        "Enroll Student",
        "Select an existing student and assign them to a course.",
    )

    if not students:
        st.info("No students yet. Add your first student above before creating an enrollment.")
    elif not courses:
        st.info("No courses yet. Create a course before enrolling students.")
    else:
        student_options = {
            f"{student[1]} ({student[2]})": student[0]
            for student in students
        }
        course_options = {
            f"{course[1]} ({course[2]})": course[0]
            for course in courses
        }

        with st.form("enroll_student_form"):
            selected_student_label = st.selectbox(
                "Select Student",
                options=list(student_options.keys()),
                index=None,
                placeholder="--- Select Student ---",
                key="enroll_student_selection",
            )
            selected_course_label = st.selectbox(
                "Select Course",
                options=list(course_options.keys()),
                index=None,
                placeholder="--- Select Course ---",
                key="enroll_course_selection",
            )
            enroll_submitted = st.form_submit_button(
                "Enroll Student",
                use_container_width=True,
            )

        if enroll_submitted:
            if selected_student_label is None:
                st.error("Please select a student.")
                return

            if selected_course_label is None:
                st.error("Please select a course.")
                return

            selected_student_id = student_options[selected_student_label]
            selected_course_id = course_options[selected_course_label]

            if enrollment_exists(selected_student_id, selected_course_id):
                st.error("This student is already enrolled in the selected course.")
            else:
                try:
                    enroll_student(selected_student_id, selected_course_id)
                    queue_widget_reset(
                        "enroll_student_selection",
                        "enroll_course_selection",
                    )
                    set_flash_success("Student enrolled successfully.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except Exception:
                    st.error("The enrollment could not be created. Please try again.")

    st.divider()

    section_heading(
        "Manage Enrollments",
        "Select a student to review and remove individual course enrollments.",
    )

    if not students:
        st.info("No students are available. Add a student before managing enrollments.")
    else:
        manage_student_options = {
            f"{student[1]} ({student[2]})": student[0]
            for student in students
        }
        selected_manage_student_label = st.selectbox(
            "Select Student",
            options=list(manage_student_options.keys()),
            index=None,
            placeholder="--- Select Student ---",
            key="manage_enrollment_student",
        )

        if selected_manage_student_label is None:
            st.info("Select a student to review current enrollments.")
        else:
            selected_manage_student_id = manage_student_options[selected_manage_student_label]
            current_enrollments = get_student_enrollments(selected_manage_student_id)

            if not current_enrollments:
                st.info(
                    "This student is not enrolled in any courses. Use the Enroll Student section above to add one."
                )
            else:
                st.markdown(f"**Current Enrollments ({len(current_enrollments)})**")

                with st.container(key="enrollment_table"):
                    header_course, header_code, header_action = st.columns([4, 2, 1.5])
                    with header_course:
                        st.caption("COURSE")
                    with header_code:
                        st.caption("CODE")
                    with header_action:
                        st.caption("ACTION")

                    for course_id, course_name, course_code in current_enrollments:
                        course_column, code_column, action_column = st.columns([4, 2, 1.5])
                        with course_column:
                            st.write(course_name)
                        with code_column:
                            st.write(course_code)
                        with action_column:
                            if st.button(
                                "Unenroll",
                                key=f"unenroll_{selected_manage_student_id}_{course_id}",
                                use_container_width=True,
                            ):
                                removed = unenroll_student(selected_manage_student_id, course_id)
                                if removed:
                                    queue_widget_reset("manage_enrollment_student")
                                    set_flash_success("Student unenrolled successfully.")
                                    st.rerun()
                                else:
                                    st.error("The enrollment could not be found.")

    st.divider()

    section_heading(
        "Student Directory",
        "Review student profiles, enrollment totals, and face-registration status.",
    )

    if not students:
        st.info(
            "No students yet. Add your first student above to begin building the directory."
        )
    else:
        student_dataframe = pd.DataFrame(
            students,
            columns=[
                "ID",
                "Name",
                "Student ID",
                "Email",
                "Courses",
                "Course Codes",
                "Face Registered",
            ],
        )
        student_dataframe["Courses"] = student_dataframe["Course Codes"].apply(
            lambda value: f"{_course_count(value)} course"
            if _course_count(value) == 1
            else f"{_course_count(value)} courses"
        )
        student_dataframe["Face Registered"] = student_dataframe["Face Registered"].map(
            {1: "Registered", 0: "Not Registered"}
        )

        st.dataframe(
            student_dataframe[
                ["Name", "Student ID", "Email", "Courses", "Face Registered"]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    section_heading(
        "Delete Student",
        (
            "Deleting a student also removes their enrollments, attendance records, "
            "face image, and face embedding."
        ),
    )

    if not students:
        st.info("No students are available to delete.")
    else:
        delete_student_options = {
            f"{student[1]} ({student[2]})": student[0]
            for student in students
        }
        selected_student_to_delete = st.selectbox(
            "Select Student",
            options=list(delete_student_options.keys()),
            index=None,
            placeholder="--- Select Student ---",
            key="delete_student_selection",
        )

        st.warning(
            "This action permanently removes the student and all associated attendance and face-registration data."
        )
        confirm_delete = st.checkbox(
            "I understand that this action cannot be undone.",
            key="confirm_student_delete",
        )

        if st.button(
            "Delete Student",
            use_container_width=True,
            key="delete_student_button",
            disabled=not confirm_delete,
        ):
            if selected_student_to_delete is None:
                st.error("Please select a student.")
                return

            delete_student(delete_student_options[selected_student_to_delete])
            queue_widget_reset("delete_student_selection")
            set_flash_success("Student deleted successfully.")
            st.rerun()


if __name__ == "__main__":
    show_students()
