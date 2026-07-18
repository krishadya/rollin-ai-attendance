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
from ui import page_header, section_heading, status_banner


def show_students():
    page_header(
        "Students",
        (
            "Create student profiles, enroll existing students in courses, "
            "and review registration status."
        ),
    )

    status_banner(
        "Student records",
        (
            "Create each student once. Afterward, select that student from "
            "the enrollment section to assign them to one or more courses."
        ),
        tone="info",
    )

    courses = get_courses()
    students = get_students()

    # ---------------------------------------------------------
    # ADD STUDENT
    # ---------------------------------------------------------
    section_heading(
        "Add Student",
        (
            "Create a student profile. You can enroll the student in a "
            "course after the profile has been added."
        ),
    )

    with st.form(
        "add_student_form",
        clear_on_submit=True,
    ):
        student_name = st.text_input(
            "Student Name",
            placeholder="Tom Harrison",
        )

        student_number = st.text_input(
            "Student ID",
            placeholder="987654321",
        )

        student_email = st.text_input(
            "Email",
            placeholder="student@example.com",
        )

        add_submitted = st.form_submit_button(
            "Add Student",
            use_container_width=True,
        )

    if add_submitted:
        if (
            not student_name.strip()
            or not student_number.strip()
            or not student_email.strip()
        ):
            st.error("Please complete all student fields.")

        else:
            try:
                add_student(
                    student_name,
                    student_number,
                    student_email,
                )

                st.success(
                    "Student added successfully. You can now enroll "
                    "the student in a course below."
                )
                st.rerun()

            except ValueError as error:
                st.error(str(error))

            except Exception:
                st.error(
                    "The student could not be added. Please try again."
                )

    st.divider()

    # ---------------------------------------------------------
    # ENROLL EXISTING STUDENT
    # ---------------------------------------------------------
    section_heading(
        "Enroll Student",
        (
            "Select an existing student and assign them to a course. "
            "You do not need to enter their information again."
        ),
    )

    if not students:
        st.info("Add a student before creating a course enrollment.")

    elif not courses:
        st.info("Create a course before enrolling students.")

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
            )

            selected_course_label = st.selectbox(
                "Select Course",
                options=list(course_options.keys()),
            )

            enroll_submitted = st.form_submit_button(
                "Enroll Student",
                use_container_width=True,
            )

        if enroll_submitted:
            selected_student_id = student_options[
                selected_student_label
            ]

            selected_course_id = course_options[
                selected_course_label
            ]

            if enrollment_exists(
                selected_student_id,
                selected_course_id,
            ):
                st.error(
                    "This student is already enrolled in the "
                    "selected course."
                )

            else:
                try:
                    enroll_student(
                        selected_student_id,
                        selected_course_id,
                    )

                    st.success("Student enrolled successfully.")
                    st.rerun()

                except ValueError as error:
                    st.error(str(error))

                except Exception:
                    st.error(
                        "The enrollment could not be created. "
                        "Please try again."
                    )

    st.divider()

    # ---------------------------------------------------------
    # MANAGE ENROLLMENTS
    # ---------------------------------------------------------
    section_heading(
        "Manage Enrollments",
        (
            "Select a student to review their current courses and remove "
            "an enrollment when needed."
        ),
    )

    if not students:
        st.info("Add a student before managing enrollments.")

    else:
        manage_student_options = {
            f"{student[1]} ({student[2]})": student[0]
            for student in students
        }

        selected_manage_student_label = st.selectbox(
            "Select Student",
            options=list(manage_student_options.keys()),
            key="manage_enrollment_student",
        )

        selected_manage_student_id = manage_student_options[
            selected_manage_student_label
        ]

        current_enrollments = get_student_enrollments(
            selected_manage_student_id
        )

        if not current_enrollments:
            st.info(
                "This student is not currently enrolled in any courses."
            )

        else:
            st.markdown("**Current Enrollments**")

            for course_id, course_name, course_code in current_enrollments:
                course_column, action_column = st.columns([4, 1])

                with course_column:
                    st.write(f"{course_name} ({course_code})")

                with action_column:
                    if st.button(
                        "Unenroll",
                        key=(
                            f"unenroll_"
                            f"{selected_manage_student_id}_"
                            f"{course_id}"
                        ),
                        use_container_width=True,
                    ):
                        removed = unenroll_student(
                            selected_manage_student_id,
                            course_id,
                        )

                        if removed:
                            st.success(
                                "Student unenrolled successfully."
                            )
                            st.rerun()

                        else:
                            st.error(
                                "The enrollment could not be found."
                            )

    st.divider()

    # ---------------------------------------------------------
    # STUDENT DIRECTORY
    # ---------------------------------------------------------
    section_heading(
        "Student Directory",
        (
            "Review student information, course enrollment, and "
            "face registration readiness."
        ),
    )

    if not students:
        st.info("No students have been added yet.")

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

        student_dataframe["Face Registered"] = (
            student_dataframe["Face Registered"].map(
                {
                    1: "Registered",
                    0: "Not Registered",
                }
            )
        )

        st.dataframe(
            student_dataframe.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ---------------------------------------------------------
    # DELETE STUDENT
    # ---------------------------------------------------------
    section_heading(
        "Delete Student",
        (
            "Deleting a student also removes their course enrollments, "
            "attendance records, face image, and face embedding."
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
            key="delete_student_selection",
        )

        st.warning(
            "This action permanently removes the student and all "
            "associated attendance and face-registration data."
        )

        if st.button(
            "Delete Student",
            use_container_width=True,
            key="delete_student_button",
        ):
            delete_student(
                delete_student_options[
                    selected_student_to_delete
                ]
            )

            st.success("Student deleted successfully.")
            st.rerun()


if __name__ == "__main__":
    show_students()