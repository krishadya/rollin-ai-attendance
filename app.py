import streamlit as st
from database import init_db
from auth import show_login, logout, require_login
from views.dashboard import show_dashboard
from views.courses import show_courses

init_db()

st.set_page_config(
    page_title="RollIn",
    page_icon="✅",
    layout="wide"
)

st.title("RollIn")
st.subheader("AI-Powered Attendance Management System")

if not require_login():
    show_login()
else:
    user = st.session_state.user

    with st.sidebar:
        st.success(f"{user['name']} ({user['role']})")
        page = st.radio(
            "Navigation",
            ["Dashboard", "Courses", "Students"]
        )

        if st.button("Logout"):
            logout()

    if page == "Dashboard":
        show_dashboard()

    elif page == "Courses":
        show_courses()

    elif page == "Students":
        st.header("Students")
        st.write("Student management coming next.")