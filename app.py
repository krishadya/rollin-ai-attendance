import streamlit as st

from database import init_db
from auth import show_login, logout, require_login

from views.dashboard import show_dashboard
from views.courses import show_courses
from views.students import show_students
from views.face_registration import show_face_registration
from views.attendance import show_attendance
from views.history import show_history
from views.analytics import show_analytics


def load_css():
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


init_db()

st.set_page_config(
    page_title="RollIn",
    page_icon="🎓",
    layout="wide"
)

load_css()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if not require_login():
    st.markdown("""
    <div class="app-brand">
        <h1>RollIn</h1>
        <p>AI-Powered Classroom Attendance Platform</p>
    </div>
    """, unsafe_allow_html=True)

    show_login()

else:
    st.markdown("""
    <div class="top-nav-brand">
        <div>
            <h1>🎓 RollIn</h1>
            <p>AI-Powered Classroom Attendance Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-bar">', unsafe_allow_html=True)

    nav_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 0.8])

    nav_items = [
    ("Dashboard", "📊 Dashboard"),
    ("Courses", "📚 Courses"),
    ("Students", "👨‍🎓 Students"),
    ("Face Registration", "📷 Faces"),
    ("Take Attendance", "✅ Attendance"),
    ("History", "📜 History"),
    ("Analytics", "📈 Analytics"),
    ]

    for col, (page_key, label) in zip(nav_cols[:7], nav_items):
        with col:
            if st.button(label, key=f"nav_{page_key}"):
                st.session_state.page = page_key

    with nav_cols[7]:
        if st.button("Logout", key="logout_btn"):
            logout()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.page == "Dashboard":
        show_dashboard()

    elif st.session_state.page == "Courses":
        show_courses()

    elif st.session_state.page == "Students":
        show_students()

    elif st.session_state.page == "Face Registration":
        show_face_registration()

    elif st.session_state.page == "Take Attendance":
        show_attendance()

    elif st.session_state.page == "Attendance History":
        show_history()

    elif st.session_state.page == "Analytics":
        show_analytics()