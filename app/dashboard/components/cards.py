from __future__ import annotations

import streamlit as st


def render_hero(title: str, subtitle: str, disclaimer: str, model_name: str) -> None:
    st.markdown(
        f"""
        <section class="hero-card">
            <div class="hero-kicker">Mental Health Analytics Studio</div>
            <h1 class="hero-title">{title}</h1>
            <p class="hero-copy">{subtitle}</p>
            <div class="hero-pills">
                <span class="pill">&#x2713;&nbsp;Deployment model: {model_name}</span>
                <span class="pill">&#x26A0;&nbsp;Educational use only</span>
                <span class="pill">&#x1F4CA;&nbsp;Imbalance-aware ranking</span>
            </div>
            <div class="hero-disclaimer">{disclaimer}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, footnote: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-footnote">{footnote}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-intro">
            <div class="section-heading">{title}</div>
            <p class="section-copy">{copy}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_finding(text: str, warning: bool = False) -> None:
    warning_class = "warning-card" if warning else ""
    st.markdown(
        f'<div class="finding-card {warning_class}">{text}</div>',
        unsafe_allow_html=True,
    )
