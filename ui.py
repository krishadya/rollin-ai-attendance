import streamlit as st


def page_header(title, subtitle=None):
    st.markdown(f"""
        <div class="page-header">
            <h1>{title}</h1>
            {f"<p>{subtitle}</p>" if subtitle else ""}
        </div>
    """, unsafe_allow_html=True)


def metric_card(icon, title, value, subtitle):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtitle">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)


def section_card(title, body):
    st.markdown(f"""
        <div class="section-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
    """, unsafe_allow_html=True)