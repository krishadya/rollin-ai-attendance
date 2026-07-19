import streamlit as st

from database import get_connection
from security import hash_password, is_password_hash, verify_password
from ui import section_heading


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, password, role FROM users WHERE email = ?",
        (email.strip().lower(),),
    )

    row = cursor.fetchone()

    if row is None or not verify_password(password, row[3]):
        conn.close()
        return None

    # Transparently upgrade legacy plaintext passwords after a successful login.
    if not is_password_hash(row[3]):
        cursor.execute(
            "UPDATE users SET password = ? WHERE id = ?",
            (hash_password(password), row[0]),
        )

        conn.commit()

    conn.close()

    return row[0], row[1], row[2], row[4]


def show_login():
    section_heading(
        "Login",
        "Sign in to manage courses, students, and attendance.",
    )

    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="Enter email address",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

        if submitted:
            user = login_user(email, password)

            if user:
                st.session_state.user = {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "role": user[3],
                }

                st.success("Login successful.")
                st.rerun()

            else:
                st.error("Invalid email or password.")

    st.caption("Use your instructor credentials to continue.")


def logout():
    st.session_state.user = None
    st.rerun()


def require_login():
    if "user" not in st.session_state:
        st.session_state.user = None

    return st.session_state.user is not None