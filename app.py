from pathlib import Path
import base64

import streamlit as st
import streamlit.components.v1 as components

from auth import logout, require_login, show_login
from database import init_db
from ui import apply_widget_resets, app_footer, show_flash_messages
from views.analytics import show_analytics
from views.attendance import show_attendance
from views.courses import show_courses
from views.dashboard import show_dashboard
from views.face_registration import show_face_registration
from views.history import show_history
from views.students import show_students


APP_NAME = "RollIn"
APP_TAGLINE = "AI-powered classroom attendance"


PAGES = {
    "Dashboard": show_dashboard,
    "Courses": show_courses,
    "Students": show_students,
    "Face Registration": show_face_registration,
    "Take Attendance": show_attendance,
    "History": show_history,
    "Analytics": show_analytics,
}


def load_css():
    css_path = Path("assets/styles.css")

    if css_path.exists():
        st.markdown(
            f"<style>{css_path.read_text()}</style>",
            unsafe_allow_html=True,
        )


def get_logo_data_uri():
    logo_path = Path("logo.png")

    if not logo_path.exists():
        return None

    encoded = base64.b64encode(
        logo_path.read_bytes()
    ).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


def render_hero_brand():
    """Centered branding used on the login screen."""
    logo_data_uri = get_logo_data_uri()

    logo_html = (
        f'<img class="hero-logo" src="{logo_data_uri}" '
        f'alt="RollIn logo" />'
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


def reset_page_scroll():
    """Reliably return the destination page to the top."""
    components.html(
        """
        <script>
            function scrollRollInToTop() {
                try {
                    const doc = window.parent.document;

                    const containers = [
                        doc.querySelector(
                            '[data-testid="stAppViewContainer"]'
                        ),
                        doc.querySelector(
                            '[data-testid="stMain"]'
                        ),
                        doc.querySelector("section.main"),
                        doc.querySelector(".main"),
                        doc.scrollingElement,
                        doc.documentElement,
                        doc.body
                    ];

                    containers.forEach((container) => {
                        if (!container) {
                            return;
                        }

                        container.scrollTop = 0;
                        container.scrollLeft = 0;

                        if (
                            typeof container.scrollTo === "function"
                        ) {
                            container.scrollTo({
                                top: 0,
                                left: 0,
                                behavior: "auto"
                            });
                        }
                    });

                    window.parent.scrollTo({
                        top: 0,
                        left: 0,
                        behavior: "auto"
                    });

                } catch (error) {
                    window.parent.scrollTo(0, 0);
                }
            }

            scrollRollInToTop();

            requestAnimationFrame(() => {
                scrollRollInToTop();
            });

            setTimeout(scrollRollInToTop, 50);
            setTimeout(scrollRollInToTop, 150);
            setTimeout(scrollRollInToTop, 300);
            setTimeout(scrollRollInToTop, 600);
        </script>
        """,
        height=0,
        width=0,
    )


def render_topbar():
    """Compact, sticky, single-row application navigation."""
    page_names = list(PAGES.keys())

    pending_page = st.session_state.pop(
        "pending_page",
        None,
    )

    if pending_page in page_names:
        previous_page = st.session_state.get("page")

        st.session_state.page = pending_page
        st.session_state.top_navigation = pending_page

        if pending_page != previous_page:
            st.session_state.reset_scroll = True

    if (
        "page" not in st.session_state
        or st.session_state.page not in page_names
    ):
        st.session_state.page = page_names[0]

    if (
        "top_navigation" not in st.session_state
        or st.session_state.top_navigation not in page_names
    ):
        st.session_state.top_navigation = (
            st.session_state.page
        )

    current_page = st.session_state.page
    current_index = page_names.index(current_page)

    logo_data_uri = get_logo_data_uri()

    logo_html = (
        f'<img class="brand-logo" '
        f'src="{logo_data_uri}" '
        f'alt="RollIn logo" />'
        if logo_data_uri
        else '<div class="brand-logo-fallback">R</div>'
    )

    brand_col, nav_col, account_col = st.columns(
        [1.15, 7.1, 1.25],
        vertical_alignment="center",
    )

    with brand_col:
        st.markdown(
            f'<div class="brand-left">'
            f'{logo_html}'
            f'<input type="checkbox" id="nav-toggle" class="nav-toggle-checkbox" />'
            f'<label for="nav-toggle" class="nav-toggle-label" aria-label="Open menu">'
            f'<span></span><span></span><span></span>'
            f'</label>'
            f'<label for="nav-toggle" class="nav-toggle-overlay" aria-hidden="true"></label>'
            f'</div>',
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

        if selected_page != current_page:
            st.session_state.page = selected_page
            st.session_state.reset_scroll = True

    with account_col:
        user_name = (
            st.session_state.get(
                "user",
                {},
            ).get(
                "name",
                "User",
            )
            if st.session_state.get("user")
            else "User"
        )

        st.caption(f"Signed in as {user_name}")

        if st.button(
            "Log out",
            key="logout_button",
            use_container_width=True,
        ):
            logout()


def main():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="favicon.ico",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_db()
    load_css()
    apply_widget_resets()

    if not require_login():
        st.markdown(
            '<div class="login-shell">',
            unsafe_allow_html=True,
        )

        render_hero_brand()
        show_login()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

        app_footer(APP_NAME)
        return

    render_topbar()

    should_reset_scroll = st.session_state.pop(
        "reset_scroll",
        False,
    )

    st.markdown(
        '<div class="page-spacer"></div>',
        unsafe_allow_html=True,
    )

    show_flash_messages()
    PAGES[st.session_state.page]()
    app_footer(APP_NAME)

    # Run after the destination page has finished rendering.
    if should_reset_scroll:
        reset_page_scroll()


if __name__ == "__main__":
    main()