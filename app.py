from pathlib import Path
import base64

import streamlit as st

from auth import logout, require_login, show_login
from database import init_db
from views.analytics import show_analytics
from views.attendance import show_attendance
from views.courses import show_courses
from views.dashboard import show_dashboard
from views.face_registration import show_face_registration
from views.history import show_history
from views.students import show_students
from ui import app_footer


APP_NAME = "RollIn"
APP_TAGLINE = "AI-Powered Classroom Attendance Platform"


PAGES = {
    "🏠 Dashboard": show_dashboard,
    "📚 Courses": show_courses,
    "🧑‍🎓 Students": show_students,
    "🪪 Face Registration": show_face_registration,
    "📷 Take Attendance": show_attendance,
    "🕒 History": show_history,
    "📊 Analytics": show_analytics,
}


def load_css():
    css_path = Path("assets/styles.css")
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def get_logo_data_uri():
    logo_path = Path("logo.png")
    if not logo_path.exists():
        return None
    encoded = base64.b64encode(logo_path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def render_hero_brand():
    """Big centered logo + brand used on the login screen."""
    logo_data_uri = get_logo_data_uri()
    logo_html = (
        f'<img class="hero-logo" src="{logo_data_uri}" alt="RollIn logo" />'
        if logo_data_uri
        else '<div class="hero-logo-fallback">R</div>'
    )

    st.markdown(
        f"""
        <div class="hero-brand">
            {logo_html}
            <div class="hero-subtitle">{APP_TAGLINE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topbar():
    """Full-width, sticky navbar with logo, navigation, and account controls."""
    page_names = list(PAGES.keys())

    if "page" not in st.session_state or st.session_state.page not in page_names:
        st.session_state.page = page_names[0]

    current_index = page_names.index(st.session_state.page)

    logo_data_uri = get_logo_data_uri()
    logo_html = (
        f'<img class="brand-logo" src="{logo_data_uri}" alt="RollIn logo" />'
        if logo_data_uri
        else '<div class="brand-logo-fallback">R</div>'
    )

    brand_col, nav_col, user_col = st.columns(
        [2.1, 6.3, 1.9], vertical_alignment="center"
    )

    with brand_col:
        st.markdown(
            f'<div class="brand-left">{logo_html}</div>',
            unsafe_allow_html=True,
        )

    with nav_col:
        selected_page = st.radio(
            "Navigation",
            page_names,
            index=current_index,
            horizontal=True,
            label_visibility="collapsed",
            key="top_navigation",
        )
        st.session_state.page = selected_page

    with user_col:
        user_name = st.session_state.user["name"]
        st.markdown(
            f"""
            <div class="nav-user-card">
                <span class="nav-user-label">Signed in</span>
                <strong>{user_name}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Logout", key="logout_button", use_container_width=True):
            logout()


def main():
    init_db()

    st.set_page_config(
        page_title=APP_NAME,
        page_icon="logo.png",
        layout="wide",
    )

    load_css()

    if not require_login():
        st.markdown('<div class="login-shell">', unsafe_allow_html=True)
        render_hero_brand()
        show_login()
        st.markdown("</div>", unsafe_allow_html=True)
        app_footer(APP_NAME)
        return

    render_topbar()
    st.markdown('<div class="page-spacer"></div>', unsafe_allow_html=True)
    PAGES[st.session_state.page]()
    app_footer(APP_NAME)


if __name__ == "__main__":
    main()