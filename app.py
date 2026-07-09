import streamlit as st
import pandas as pd
from database import init_db, get_connection, add_course, get_courses, delete_course

init_db()

st.set_page_config(
    page_title="RollIn",
    page_icon="✅",
    layout="wide"
)


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, role FROM users WHERE email = ? AND password = ?",
        (email, password)
    )

    user = cursor.fetchone()
    conn.close()
    return user


def courses_page():
    st.header("Courses")

    st.subheader("Add New Course")

    with st.form("add_course_form"):
        course_name = st.text_input("Course Name", placeholder="Software Engineering")
        course_code = st.text_input("Course Code", placeholder="CSC 648")
        submitted = st.form_submit_button("Add Course")

        if submitted:
            if course_name and course_code:
                add_course(course_name, course_code, st.session_state.user["id"])
                st.success("Course added successfully!")
                st.rerun()
            else:
                st.error("Please fill in both course name and course code.")

    st.subheader("All Courses")

    courses = get_courses()

    if courses:
        df = pd.DataFrame(
            courses,
            columns=["ID", "Course Name", "Course Code", "Instructor"]
        )
        st.dataframe(df, use_container_width=True)

        st.subheader("Delete Course")
        course_options = {f"{course[1]} ({course[2]})": course[0] for course in courses}
        selected_course = st.selectbox("Select course to delete", course_options.keys())

        if st.button("Delete Course"):
            delete_course(course_options[selected_course])
            st.warning("Course deleted.")
            st.rerun()
    else:
        st.info("No courses added yet.")


st.title("RollIn")
st.subheader("AI-Powered Attendance Management System")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.header("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)

        if user:
            st.session_state.user = {
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "role": user[3]
            }
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password.")

    st.info("Default admin: admin@rollin.com / admin123")

else:
    user = st.session_state.user

    with st.sidebar:
        st.success(f"{user['name']} ({user['role']})")
        page = st.radio("Navigation", ["Dashboard", "Courses"])

        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    if page == "Dashboard":
        st.header("Dashboard")
        st.write("Welcome to RollIn.")
        st.write("Use the sidebar to manage the system.")

    elif page == "Courses":
        courses_page()