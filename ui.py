import html
from datetime import datetime

import streamlit as st


def app_shell_card(title, body, tone="default"):
    st.markdown(
        f"""
        <section class="shell-card shell-card-{html.escape(str(tone))}">
            <h3>{html.escape(str(title))}</h3>
            <p>{html.escape(str(body))}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle=None):
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle) if subtitle else ""
    subtitle_html = f"<p>{safe_subtitle}</p>" if subtitle else ""

    st.markdown(
        f"""
        <section class="page-header">
            <h1>{safe_title}</h1>
            {subtitle_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title, subtitle=None):
    safe_title = html.escape(str(title))
    subtitle_html = (
        f"<p>{html.escape(str(subtitle))}</p>"
        if subtitle
        else ""
    )

    st.markdown(
        f"""
        <div class="section-heading">
            <h2>{safe_title}</h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title, value, subtitle):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{html.escape(str(title))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-subtitle">{html.escape(str(subtitle))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_banner(title, body, tone="info"):
    st.markdown(
        f"""
        <div class="status-banner status-banner-{html.escape(str(tone))}">
            <strong>{html.escape(str(title))}</strong>
            <span>{html.escape(str(body))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hint_text(body, label=None):
    label_html = f"<strong>{html.escape(str(label))}:</strong> " if label else ""
    st.markdown(
        f'<p class="hint-text">{label_html}{html.escape(str(body))}</p>',
        unsafe_allow_html=True,
    )


def app_footer(app_name="RollIn"):
    year = datetime.now().year
    st.markdown(
        f'<div class="app-footer">© {year} {html.escape(str(app_name))}. All rights reserved.</div>',
        unsafe_allow_html=True,
    )


def section_card(title, body):
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{html.escape(str(title))}</h3>
            <p>{html.escape(str(body))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def step_card(number, title, body):
    st.markdown(
        f"""
        <div class="step-card">
            <div class="step-badge">{html.escape(str(number))}</div>
            <h4>{html.escape(str(title))}</h4>
            <p>{html.escape(str(body))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )