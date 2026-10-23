from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Manrope:wght@300;400;500;600;700;800&display=swap');

            :root {
                --bg: #f6f1ea;
                --surface: rgba(255,255,255,0.75);
                --surface-strong: rgba(255,255,255,0.95);
                --surface-hover: rgba(255,255,255,0.92);
                --border: rgba(22, 48, 43, 0.10);
                --border-strong: rgba(22, 48, 43, 0.18);
                --ink: #16302b;
                --muted: #6b7f79;
                --muted-light: #9db0aa;
                --accent: #2f6b63;
                --accent-light: rgba(47,107,99,0.10);
                --accent-mid: rgba(47,107,99,0.22);
                --highlight: #c2703d;
                --highlight-light: rgba(194,112,61,0.10);
                --rose: #a85a68;
                --rose-light: rgba(168,90,104,0.10);
                --gold: #b8953a;
                --shadow-sm: 0 2px 12px rgba(22,48,43,0.06);
                --shadow-md: 0 8px 32px rgba(22,48,43,0.09);
                --shadow-lg: 0 20px 56px rgba(22,48,43,0.12);
                --radius-sm: 14px;
                --radius-md: 20px;
                --radius-lg: 28px;
            }

            /* ── Base ── */
            .stApp {
                background:
                    radial-gradient(ellipse 60% 40% at 0% 0%, rgba(194,112,61,0.10) 0%, transparent 60%),
                    radial-gradient(ellipse 50% 50% at 100% 0%, rgba(47,107,99,0.13) 0%, transparent 55%),
                    radial-gradient(ellipse 40% 60% at 50% 100%, rgba(168,90,104,0.06) 0%, transparent 60%),
                    linear-gradient(160deg, #fdfaf5 0%, #f6f1ea 50%, #f0ebe1 100%);
                color: var(--ink);
            }

            .block-container {
                padding-top: 1.8rem;
                padding-bottom: 3rem;
                max-width: 1280px;
            }

            /* ── Typography ── */
            h1, h2, h3, h4, .dashboard-title {
                font-family: "Cormorant Garamond", Georgia, serif !important;
                color: var(--ink);
                letter-spacing: 0.01em;
            }

            html, body, p, span, div, label, button,
            [class*="css"],
            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMetricValue"],
            [data-testid="stMetricLabel"] {
                font-family: "Manrope", "Avenir Next", "Segoe UI", sans-serif;
            }

            /* ── Tabs ── */
            [data-testid="stTabs"] [data-baseweb="tab-list"] {
                background: var(--surface);
                border-radius: var(--radius-md);
                padding: 0.3rem;
                border: 1px solid var(--border);
                box-shadow: var(--shadow-sm);
                gap: 0.2rem;
            }

            [data-testid="stTabs"] [data-baseweb="tab"] {
                font-family: "Manrope", sans-serif;
                font-weight: 600;
                font-size: 0.82rem;
                color: var(--muted);
                border-radius: var(--radius-sm);
                padding: 0.5rem 1rem;
                transition: all 0.2s ease;
                border: none;
                background: transparent;
                letter-spacing: 0.03em;
            }

            [data-testid="stTabs"] [aria-selected="true"] {
                background: var(--accent) !important;
                color: white !important;
                box-shadow: 0 4px 14px rgba(47,107,99,0.35) !important;
            }

            [data-testid="stTabs"] [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
                background: var(--accent-light);
                color: var(--accent);
            }

            [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
                display: none;
            }

            [data-testid="stTabs"] [data-baseweb="tab-border"] {
                display: none;
            }

            /* ── Cards base ── */
            .hero-card, .section-card, .metric-card, .finding-card, .stat-band {
                background: var(--surface);
                backdrop-filter: blur(16px) saturate(1.4);
                -webkit-backdrop-filter: blur(16px) saturate(1.4);
                border: 1px solid var(--border);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-md);
            }

            /* ── Hero ── */
            .hero-card {
                padding: 2.4rem 2.6rem;
                margin-bottom: 1.6rem;
                position: relative;
                overflow: hidden;
            }

            .hero-card::before {
                content: "";
                position: absolute;
                top: -60px;
                right: -60px;
                width: 260px;
                height: 260px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(47,107,99,0.12), transparent 70%);
                pointer-events: none;
            }

            .hero-card::after {
                content: "";
                position: absolute;
                bottom: -40px;
                left: 30%;
                width: 180px;
                height: 180px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(194,112,61,0.09), transparent 70%);
                pointer-events: none;
            }

            .hero-kicker {
                text-transform: uppercase;
                letter-spacing: 0.20em;
                font-size: 0.72rem;
                color: var(--accent);
                font-weight: 700;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .hero-kicker::before {
                content: "";
                display: inline-block;
                width: 20px;
                height: 2px;
                background: var(--accent);
                border-radius: 2px;
            }

            .hero-title {
                font-size: 3.2rem;
                line-height: 0.95;
                margin: 0.4rem 0 0.85rem 0;
                background: linear-gradient(135deg, var(--ink) 0%, var(--accent) 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .hero-copy {
                max-width: 860px;
                color: var(--muted);
                font-size: 0.97rem;
                line-height: 1.65;
                font-weight: 400;
            }

            .hero-pills {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-top: 1.2rem;
            }

            .hero-disclaimer {
                margin-top: 1rem;
                color: var(--muted-light);
                font-size: 0.85rem;
                font-style: italic;
                padding-top: 1rem;
                border-top: 1px solid var(--border);
            }

            /* ── Metric card ── */
            .metric-card {
                padding: 1.3rem 1.4rem;
                min-height: 148px;
                position: relative;
                overflow: hidden;
                transition: box-shadow 0.25s ease, transform 0.25s ease;
            }

            .metric-card:hover {
                box-shadow: var(--shadow-lg);
                transform: translateY(-2px);
            }

            .metric-card::after {
                content: "";
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, var(--accent), var(--highlight));
                border-radius: 0 0 var(--radius-lg) var(--radius-lg);
            }

            .metric-label {
                color: var(--muted);
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.14em;
                margin-bottom: 0.6rem;
                font-weight: 700;
            }

            .metric-value {
                color: var(--ink);
                font-size: 2.4rem;
                font-weight: 800;
                line-height: 1;
                font-family: "Manrope", sans-serif;
            }

            .metric-footnote {
                color: var(--muted);
                font-size: 0.82rem;
                margin-top: 0.75rem;
                line-height: 1.4;
            }

            /* ── Section intro ── */
            .section-intro {
                margin-bottom: 1.4rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid var(--border);
            }

            .section-heading {
                margin: 0 0 0.3rem 0;
                font-size: 2rem;
                display: flex;
                align-items: center;
                gap: 0.6rem;
            }

            .section-heading::before {
                content: "";
                display: inline-block;
                width: 6px;
                height: 28px;
                background: linear-gradient(180deg, var(--accent), var(--highlight));
                border-radius: 6px;
                flex-shrink: 0;
            }

            .section-copy {
                color: var(--muted);
                font-size: 0.93rem;
                line-height: 1.6;
                margin: 0;
                padding-left: 0.9rem;
            }

            /* ── Finding / alert cards ── */
            .finding-card {
                padding: 0.95rem 1.2rem;
                margin-bottom: 0.65rem;
                border-left: 4px solid var(--accent);
                border-radius: var(--radius-sm);
                font-size: 0.92rem;
                line-height: 1.55;
                background: var(--accent-light);
                border-top: 1px solid var(--border);
                border-right: 1px solid var(--border);
                border-bottom: 1px solid var(--border);
                box-shadow: var(--shadow-sm);
            }

            .warning-card {
                border-left-color: var(--highlight);
                background: var(--highlight-light);
            }

            /* ── Pills ── */
            .pill {
                display: inline-flex;
                align-items: center;
                gap: 0.3rem;
                padding: 0.35rem 0.85rem;
                border-radius: 999px;
                background: var(--accent-mid);
                color: var(--accent);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.04em;
                border: 1px solid rgba(47,107,99,0.20);
            }

            /* ── Sidebar ── */
            [data-testid="stSidebar"] {
                background: rgba(253, 250, 244, 0.96) !important;
                border-right: 1px solid var(--border) !important;
                backdrop-filter: blur(12px);
            }

            [data-testid="stSidebar"] .block-container {
                padding-top: 1.5rem;
            }

            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] .sidebar-title {
                font-family: "Cormorant Garamond", serif !important;
                font-size: 1.5rem;
                color: var(--ink);
                border-bottom: 2px solid var(--accent);
                padding-bottom: 0.5rem;
                margin-bottom: 1rem;
            }

            /* ── Sliders ── */
            [data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
                background: var(--accent);
                color: white;
                border-radius: 6px;
                font-size: 0.78rem;
                font-weight: 700;
            }

            /* ── Multiselect ── */
            [data-baseweb="tag"] {
                background: var(--accent) !important;
                border-radius: 999px !important;
            }

            /* ── Buttons ── */
            [data-testid="stFormSubmitButton"] button,
            [data-testid="stDownloadButton"] button {
                background: linear-gradient(135deg, var(--accent) 0%, #1f4f49 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: var(--radius-sm) !important;
                font-family: "Manrope", sans-serif !important;
                font-weight: 700 !important;
                font-size: 0.88rem !important;
                letter-spacing: 0.05em !important;
                padding: 0.6rem 1.4rem !important;
                box-shadow: 0 4px 16px rgba(47,107,99,0.30) !important;
                transition: all 0.2s ease !important;
            }

            [data-testid="stFormSubmitButton"] button:hover,
            [data-testid="stDownloadButton"] button:hover {
                box-shadow: 0 6px 22px rgba(47,107,99,0.42) !important;
                transform: translateY(-1px) !important;
            }

            /* ── DataFrames ── */
            div[data-testid="stDataFrame"] {
                border: 1px solid var(--border);
                border-radius: var(--radius-md);
                overflow: hidden;
                box-shadow: var(--shadow-sm);
            }

            /* ── Expander ── */
            [data-testid="stExpander"] {
                border: 1px solid var(--border) !important;
                border-radius: var(--radius-md) !important;
                background: var(--surface) !important;
                box-shadow: var(--shadow-sm) !important;
                margin-bottom: 0.5rem !important;
            }

            [data-testid="stExpander"] summary {
                font-family: "Manrope", sans-serif !important;
                font-weight: 600 !important;
                color: var(--ink) !important;
                font-size: 0.9rem !important;
            }

            /* ── Scrollbar ── */
            ::-webkit-scrollbar { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { background: var(--muted-light); border-radius: 6px; }
            ::-webkit-scrollbar-thumb:hover { background: var(--muted); }

            /* ── Divider ── */
            hr {
                border: none;
                border-top: 1px solid var(--border);
                margin: 1.5rem 0;
            }

            /* ── Radio buttons ── */
            [data-testid="stRadio"] label {
                font-size: 0.88rem !important;
                font-weight: 500 !important;
            }

            /* ── Select boxes / inputs ── */
            [data-baseweb="select"] {
                border-radius: var(--radius-sm) !important;
            }

            /* ── Plotly chart wrapper ── */
            [data-testid="stPlotlyChart"] {
                border-radius: var(--radius-md);
                overflow: hidden;
                box-shadow: var(--shadow-sm);
                border: 1px solid var(--border);
                background: var(--surface-strong);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
