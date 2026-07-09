import streamlit as st
from database import get_connection


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, email, role FROM users WHERE email = ? AND password = ?",
        (email, password),
    )

    user = cursor.fetchone()
    conn.close()
    return user


def show_login():
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
                "role": user[3],
            }
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password.")

    st.info("Default admin: admin@rollin.com / admin123")


def logout():
    st.session_state.user = None
    st.rerun()


def require_login():
    if "user" not in st.session_state:
        st.session_state.user = None

    return st.session_state.user is not None