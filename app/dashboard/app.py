from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.analytics import compute_data_explorer
from app.services.data_loader import load_datasets
from app.services.filters import apply_filters, build_filter_state
from app.services.model_service import load_best_model_artifact
from app.utils.constants import (
    APP_SUBTITLE,
    APP_TITLE,
    DISCLAIMER,
    MODEL_NAME,
    NOMINAL_COLS,
    ORDINAL_COLS,
    PERSONAL_INPUT_GROUPS,
    TARGET_COL,
)
from app.utils.formatting import format_pct, format_score, humanize_label
import plotly.graph_objects as go
from app.utils.plotting import bar_chart, histogram, metric_comparison_chart, scatter_chart
from app.dashboard.components.cards import render_finding, render_hero, render_metric_card, render_section_intro
from app.dashboard.components.theme import inject_theme
from app.dashboard.api_client import (
    BackendUnavailableError,
    call_predict,
    check_health,
    fetch_demographics,
    fetch_factors,
    fetch_model_comparison,
    fetch_summary,
    fetch_support_patterns,
)


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _render_sidebar(analytics_df: pd.DataFrame):
    st.sidebar.markdown("## Filter Studio")
    st.sidebar.caption("Tune the whole dashboard with one shared research lens.")

    age_range = st.sidebar.slider(
        "Age range",
        min_value=int(analytics_df["Age"].min()),
        max_value=int(analytics_df["Age"].max()),
        value=(int(analytics_df["Age"].min()), int(analytics_df["Age"].max())),
    )
    genders = st.sidebar.multiselect(
        "Gender",
        options=sorted(analytics_df["Gender"].dropna().unique().tolist()),
        default=[],
    )
    countries = st.sidebar.multiselect(
        "Country",
        options=sorted(analytics_df["Country"].dropna().unique().tolist()),
        default=[],
    )
    education_levels = st.sidebar.multiselect(
        "Education",
        options=sorted(analytics_df["Education"].dropna().unique().tolist()),
        default=[],
    )
    employment_statuses = st.sidebar.multiselect(
        "Employment status",
        options=sorted(analytics_df["Employment_Status"].dropna().unique().tolist()),
        default=[],
    )
    target_label = st.sidebar.radio(
        "Target slice",
        options=["All respondents", "Reported issue", "No issue reported"],
        index=0,
    )
    target_map = {
        "All respondents": [0, 1],
        "Reported issue": [1],
        "No issue reported": [0],
    }
    search_text = st.sidebar.text_input("Search across the table", placeholder="Example: germany, married, hybrid")
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Treatment-related columns appear in descriptive sections only and remain excluded from prediction logic."
    )

    return build_filter_state(
        age_range=age_range,
        genders=genders,
        countries=countries,
        education_levels=education_levels,
        employment_statuses=employment_statuses,
        target_values=target_map[target_label],
        search_text=search_text,
    )


def _render_overview(filtered_df: pd.DataFrame, filter_state) -> None:
    render_section_intro(
        "Overview",
        "A concise executive readout of the selected slice, with respectful framing around prevalence, stress load, and support context.",
    )
    try:
        summary = fetch_summary(filter_state)
    except BackendUnavailableError as exc:
        render_finding(str(exc), warning=True)
        return

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric_card("Filtered Respondents", f"{summary['total_records']:,}", "Records in the current slice")
    with metric_cols[1]:
        render_metric_card("Reported Issue Rate", format_pct(summary["issue_rate"]), "Share with target = 1")
    with metric_cols[2]:
        render_metric_card("Average Work Stress", f"{summary['average_stress']:.1f}/10", "Higher scores indicate heavier strain")
    with metric_cols[3]:
        render_metric_card("Average Social Support", f"{summary['average_support']:.1f}/10", "Higher scores indicate stronger support")

    issue_df = (
        filtered_df[TARGET_COL]
        .astype(int)
        .value_counts(normalize=True)
        .rename_axis("Target")
        .reset_index(name="Share")
        .assign(Target=lambda frame: frame["Target"].map({0: "No Issue", 1: "Issue"}))
    )
    issue_rate = summary["issue_rate"]
    no_issue_str = format_pct(1 - issue_rate)
    issue_str = format_pct(issue_rate)

    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.70);
            border: 1px solid rgba(22,48,43,0.10);
            border-radius: 20px;
            padding: 1.4rem 1.8rem 1rem 1.8rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 18px rgba(22,48,43,0.07);
        ">
            <div style="
                font-family: 'Cormorant Garamond', serif;
                font-size: 1.25rem;
                font-weight: 600;
                color: #16302b;
                margin-bottom: 0.9rem;
                letter-spacing: 0.01em;
            ">Target Distribution — Current Slice</div>
            <div style="display: flex; gap: 1.2rem; align-items: stretch;">
                <div style="
                    flex: 1;
                    background: rgba(47,107,99,0.09);
                    border: 1px solid rgba(47,107,99,0.18);
                    border-radius: 14px;
                    padding: 1rem 1.2rem;
                    text-align: center;
                ">
                    <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.14em; color: #6b7f79; font-weight: 700; margin-bottom: 0.4rem;">No Issue</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #2f6b63; line-height: 1;">{no_issue_str}</div>
                    <div style="font-size: 0.78rem; color: #6b7f79; margin-top: 0.3rem;">of respondents</div>
                </div>
                <div style="
                    flex: 1;
                    background: rgba(194,112,61,0.09);
                    border: 1px solid rgba(194,112,61,0.20);
                    border-radius: 14px;
                    padding: 1rem 1.2rem;
                    text-align: center;
                ">
                    <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.14em; color: #6b7f79; font-weight: 700; margin-bottom: 0.4rem;">Reported Issue</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #c2703d; line-height: 1;">{issue_str}</div>
                    <div style="font-size: 0.78rem; color: #6b7f79; margin-top: 0.3rem;">of respondents</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.1, 0.9])
    with left:
        _dist_fig = go.Figure(data=[
            go.Bar(
                x=issue_df["Target"],
                y=issue_df["Share"],
                marker_color=[
                    "#2f6b63" if t == "No Issue" else "#c2703d"
                    for t in issue_df["Target"]
                ],
                marker_line_width=0,
                opacity=0.92,
                text=[f"{v*100:.1f}%" for v in issue_df["Share"]],
                textposition="outside",
                textfont={"family": "Manrope, sans-serif", "size": 13, "color": "#16302b"},
            )
        ])
        _dist_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin={"l": 10, "r": 10, "t": 10, "b": 10},
            xaxis={"title": None, "showgrid": False, "zeroline": False,
                   "tickfont": {"family": "Manrope, sans-serif", "size": 13, "color": "#16302b"}},
            yaxis={"title": None, "showgrid": False, "zeroline": False,
                   "showticklabels": False, "range": [0, 1.15]},
            font={"family": "Manrope, sans-serif", "color": "#16302b"},
        )
        st.plotly_chart(_dist_fig, use_container_width=True)
    with right:
        st.markdown(
            """
            <div style="
                font-family: 'Cormorant Garamond', serif;
                font-size: 1.25rem;
                font-weight: 600;
                color: #16302b;
                margin-bottom: 0.75rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid rgba(22,48,43,0.10);
            ">Key Findings</div>
            """,
            unsafe_allow_html=True,
        )
        for finding in summary["findings"]:
            render_finding(finding)


def _render_demographics(filter_state) -> None:
    render_section_intro(
        "Demographics",
        "Compare prevalence across age bands, geographies, and life-stage markers to see where pressures cluster most visibly.",
    )
    try:
        breakdowns = fetch_demographics(filter_state)
    except BackendUnavailableError as exc:
        render_finding(str(exc), warning=True)
        return

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            bar_chart(breakdowns["gender"], x="Gender", y="Issue_Rate", color=None, title="Issue Rate by Gender"),
            use_container_width=True,
        )
        st.markdown("<div style='height: 0.6rem'></div>", unsafe_allow_html=True)
        st.plotly_chart(
            bar_chart(
                breakdowns["employment"],
                x="Employment_Status",
                y="Issue_Rate",
                color=None,
                title="Issue Rate by Employment Status",
            ),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            bar_chart(breakdowns["age"], x="Age_Band", y="Issue_Rate", color=None, title="Issue Rate by Age Band"),
            use_container_width=True,
        )
        st.markdown("<div style='height: 0.6rem'></div>", unsafe_allow_html=True)
        st.plotly_chart(
            bar_chart(
                breakdowns["country"],
                x="Country",
                y="Issue_Rate",
                color=None,
                title="Issue Rate in the Top Countries",
            ),
            use_container_width=True,
        )


def _render_outcomes(filter_state) -> None:
    render_section_intro(
        "Mental Health Outcomes",
        "Explore how symptom intensities, loneliness, and support signals shift between respondents with and without the target outcome.",
    )
    try:
        factors = fetch_factors(filter_state)
    except BackendUnavailableError as exc:
        render_finding(str(exc), warning=True)
        return

    col1, col2 = st.columns(2)
    with col1:
        symp = factors["symptom_summary"]
        if not symp.empty and "No_Issue_Mean" in symp.columns and "Issue_Mean" in symp.columns:
            symp_long = symp.melt(
                id_vars="Symptom",
                value_vars=["No_Issue_Mean", "Issue_Mean"],
                var_name="Group",
                value_name="Mean Score",
            ).assign(Group=lambda df: df["Group"].map({"No_Issue_Mean": "No Issue", "Issue_Mean": "Issue"}))
            st.plotly_chart(
                bar_chart(
                    symp_long,
                    x="Symptom",
                    y="Mean Score",
                    color="Group",
                    title="Mean Symptom Scores by Outcome Group",
                ),
                use_container_width=True,
            )
        else:
            render_finding("Symptom data unavailable for this filter slice.", warning=True)
    with col2:
        st.plotly_chart(
            scatter_chart(
                factors["stress_support"],
                x="Work_Stress_Level",
                y="Social_Support",
                color="Issue_Rate",
                size="Respondents",
                title="Stress, Support, and Issue Rate",
            ),
            use_container_width=True,
        )


def _render_risk_factors(filter_state) -> None:
    render_section_intro(
        "Risk Factors",
        "Focus on the stressors most associated with the target in this dataset, and compare those descriptive patterns with the deployed model's global feature importances.",
    )
    try:
        factors = fetch_factors(filter_state)
    except BackendUnavailableError as exc:
        render_finding(str(exc), warning=True)
        return

    top_importance = factors["feature_importance"]
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            bar_chart(
                factors["factor_gaps"].head(10),
                x="Factor",
                y="Gap",
                color=None,
                title="Difference in Mean Factor Scores: Issue vs No Issue",
                horizontal=True,
            ),
            use_container_width=True,
        )
    with right:
        if top_importance.empty:
            render_finding(
                "Prediction artifact not found yet, so feature importance is unavailable. The dashboard will still show descriptive analytics.",
                warning=True,
            )
        else:
            st.plotly_chart(
                bar_chart(
                    top_importance.sort_values("Importance"),
                    x="Feature",
                    y="Importance",
                    color=None,
                    title="Balanced RF Global Feature Importance",
                    horizontal=True,
                ),
                use_container_width=True,
            )


def _render_support_patterns(filter_state) -> None:
    render_section_intro(
        "Support Patterns",
        "Read treatment and support responses descriptively, with clear separation from the predictive feature set to avoid leakage.",
    )
    try:
        support = fetch_support_patterns(filter_state)
    except BackendUnavailableError as exc:
        render_finding(str(exc), warning=True)
        return

    left, right = st.columns(2)
    with left:
        treatment_rows = support["support_patterns"][
            support["support_patterns"]["Measure"].isin(
                [
                    "Previously Diagnosed",
                    "Ever Sought Treatment",
                    "On Therapy Now",
                    "On Medication",
                ]
            )
        ]
        st.plotly_chart(
            bar_chart(
                treatment_rows,
                x="Measure",
                y="Issue_Rate",
                color="Response",
                title="Treatment-Related Responses by Outcome Rate",
            ),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            bar_chart(
                support["proxy_shares"],
                x="Measure",
                y="Share",
                color=None,
                title="Proxy Variables Used Descriptively Only",
            ),
            use_container_width=True,
        )
        render_finding(
            "These treatment and diagnosis variables are intentionally excluded from the deployed model, even though they remain valuable for descriptive storytelling.",
            warning=True,
        )


def _render_model_lab() -> None:
    render_section_intro(
        "Model Lab",
        "Compare the three trained models on the exported benchmark table and show why Balanced RF is the deployment choice under imbalance-aware ranking.",
    )
    try:
        comparison_df, ranking_rule = fetch_model_comparison()
    except BackendUnavailableError as exc:
        render_finding(str(exc), warning=True)
        return

    winner = comparison_df.iloc[0]["Model"]
    winner_row = comparison_df.iloc[0]
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(47,107,99,0.12) 0%, rgba(47,107,99,0.04) 100%);
            border: 1px solid rgba(47,107,99,0.25);
            border-left: 5px solid #2f6b63;
            border-radius: 18px;
            padding: 1.4rem 1.8rem;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 1.4rem;
        ">
            <div style="font-size: 2.6rem; line-height: 1;">&#x1F3C6;</div>
            <div>
                <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.16em; color: #2f6b63; font-weight: 700; margin-bottom: 0.3rem;">Deployment Winner</div>
                <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.7rem; font-weight: 700; color: #16302b; line-height: 1.1;">{winner}</div>
                <div style="margin-top: 0.5rem; display: flex; gap: 0.6rem; flex-wrap: wrap;">
                    <span style="background: rgba(47,107,99,0.12); color: #2f6b63; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 999px; border: 1px solid rgba(47,107,99,0.20);">Balanced Accuracy {winner_row['Balanced_Accuracy']:.3f}</span>
                    <span style="background: rgba(47,107,99,0.12); color: #2f6b63; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 999px; border: 1px solid rgba(47,107,99,0.20);">Recall&#x2080; {winner_row['Recall_0']:.3f}</span>
                    <span style="background: rgba(47,107,99,0.12); color: #2f6b63; font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 999px; border: 1px solid rgba(47,107,99,0.20);">F1&#x2080; {winner_row['F1_0']:.3f}</span>
                </div>
            </div>
        </div>
        <div style="
            background: rgba(22,48,43,0.04);
            border: 1px solid rgba(22,48,43,0.10);
            border-radius: 12px;
            padding: 0.7rem 1.1rem;
            margin-bottom: 1.2rem;
            font-size: 0.83rem;
            color: #6b7f79;
            font-family: 'Manrope', sans-serif;
        ">
            <span style="font-weight: 700; color: #16302b;">Ranking rule: </span>
            <span style="font-family: monospace; color: #2f6b63;">{ranking_rule}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    with cols[0]:
        st.plotly_chart(
            metric_comparison_chart(comparison_df, "Balanced_Accuracy", "Balanced Accuracy"),
            use_container_width=True,
        )
    with cols[1]:
        st.plotly_chart(
            metric_comparison_chart(comparison_df, "Recall_0", "Minority-Class Recall"),
            use_container_width=True,
        )
    with cols[2]:
        st.plotly_chart(
            metric_comparison_chart(comparison_df, "F1_0", "Minority-Class F1"),
            use_container_width=True,
        )
    st.dataframe(
        comparison_df.style.format(
            {
                "Accuracy": "{:.4f}",
                "Balanced_Accuracy": "{:.4f}",
                "Precision_0": "{:.4f}",
                "Recall_0": "{:.4f}",
                "F1_0": "{:.4f}",
                "PR_AUC_0": "{:.4f}",
                "Precision_1": "{:.4f}",
                "Recall_1": "{:.4f}",
                "F1_1": "{:.4f}",
                "PR_AUC_1": "{:.4f}",
                "ROC_AUC_1": "{:.4f}",
            }
        ),
        use_container_width=True,
    )


def _render_prediction_sandbox(analytics_df: pd.DataFrame) -> None:
    render_section_intro(
        "Prediction Sandbox",
        "Try a single survey profile with the deployed Balanced RF model. This output is a dataset-specific pattern estimate, not a diagnosis.",
    )
    artifact = load_best_model_artifact()
    if artifact is None:
        render_finding(
            "The persisted model artifact is missing, so live predictions are currently unavailable. Train and save the Balanced RF artifact locally to enable this section.",
            warning=True,
        )
        return

    input_columns = artifact["input_columns"]
    field_values = {}
    with st.form("prediction_form"):
        for section_name, columns in PERSONAL_INPUT_GROUPS.items():
            with st.expander(section_name, expanded=section_name in {"Personal Profile", "Work Context"}):
                ui_cols = st.columns(2)
                slot = 0
                for column in columns:
                    if column not in input_columns:
                        continue
                    with ui_cols[slot % 2]:
                        if column in ORDINAL_COLS or column in NOMINAL_COLS:
                            options = sorted(analytics_df[column].dropna().astype(str).unique().tolist())
                            field_values[column] = st.selectbox(humanize_label(column), options=options, key=f"pred_{column}")
                        else:
                            series = analytics_df[column].dropna()
                            if pd.api.types.is_integer_dtype(series) or float(series.max()).is_integer():
                                field_values[column] = st.slider(
                                    humanize_label(column),
                                    min_value=int(series.min()),
                                    max_value=int(series.max()),
                                    value=int(round(series.median())),
                                    key=f"pred_{column}",
                                )
                            else:
                                field_values[column] = st.slider(
                                    humanize_label(column),
                                    min_value=float(series.min()),
                                    max_value=float(series.max()),
                                    value=float(round(series.median(), 1)),
                                    step=0.1,
                                    key=f"pred_{column}",
                                )
                    slot += 1

        submitted = st.form_submit_button("Estimate Pattern")

    if submitted:
        try:
            result = call_predict(field_values)
            pred_class = result["predicted_class"]
            prob = result["probability"]
            label = result["probability_label"]
            is_issue = pred_class == 1
            accent_color = "#c2703d" if is_issue else "#2f6b63"
            accent_bg = "rgba(194,112,61,0.08)" if is_issue else "rgba(47,107,99,0.08)"
            accent_border = "rgba(194,112,61,0.25)" if is_issue else "rgba(47,107,99,0.22)"
            icon = "&#x26A0;" if is_issue else "&#x2713;"
            st.markdown(
                f"""
                <div style="
                    background: {accent_bg};
                    border: 1px solid {accent_border};
                    border-left: 5px solid {accent_color};
                    border-radius: 18px;
                    padding: 1.4rem 1.8rem;
                    margin: 1rem 0;
                    display: flex;
                    align-items: center;
                    gap: 1.6rem;
                ">
                    <div style="font-size: 2.8rem; line-height: 1;">{icon}</div>
                    <div style="flex: 1;">
                        <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.16em; color: {accent_color}; font-weight: 700; margin-bottom: 0.3rem;">Pattern Estimate</div>
                        <div style="font-family: 'Cormorant Garamond', serif; font-size: 1.6rem; font-weight: 700; color: #16302b; line-height: 1.1;">{label}</div>
                        <div style="margin-top: 0.5rem; display: flex; gap: 1.4rem;">
                            <div>
                                <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.12em; color: #6b7f79; font-weight: 700;">Predicted Class</div>
                                <div style="font-size: 1.5rem; font-weight: 800; color: {accent_color};">{pred_class}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.70rem; text-transform: uppercase; letter-spacing: 0.12em; color: #6b7f79; font-weight: 700;">Probability</div>
                                <div style="font-size: 1.5rem; font-weight: 800; color: {accent_color};">{format_pct(prob)}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_finding(result["disclaimer"], warning=True)
        except BackendUnavailableError as exc:
            render_finding(str(exc), warning=True)


def _render_data_explorer(filtered_df: pd.DataFrame) -> None:
    render_section_intro(
        "Data Explorer",
        "Inspect the filtered records directly, export a subset, and keep the exploratory workflow grounded in the actual survey rows.",
    )
    explorer_df = compute_data_explorer(filtered_df)
    top_left, _ = st.columns([1, 3])
    with top_left:
        st.markdown(
            f"""
            <div style="
                background: rgba(47,107,99,0.08);
                border: 1px solid rgba(47,107,99,0.20);
                border-radius: 12px;
                padding: 0.65rem 1rem;
                margin-bottom: 0.6rem;
                font-size: 0.83rem;
                color: #2f6b63;
                font-weight: 600;
            ">&#x1F4C4;&nbsp; {len(explorer_df):,} records in current slice</div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button(
            "Download Filtered Data",
            data=explorer_df.to_csv(index=False).encode("utf-8"),
            file_name="mental_health_filtered_data.csv",
            mime="text/csv",
        )
    st.dataframe(explorer_df, use_container_width=True, height=520)


def main() -> None:
    inject_theme()
    try:
        check_health()
    except BackendUnavailableError as exc:
        st.error(
            f"**Backend unreachable** — {exc}\n\n"
            "Start the FastAPI server first:\n"
            "```\nuvicorn app.backend.main:app --reload\n```"
        )
        st.stop()

    datasets = load_datasets()
    filter_state = _render_sidebar(datasets.analytics_df)
    filtered_df = apply_filters(datasets.analytics_df, filter_state)

    render_hero(APP_TITLE, APP_SUBTITLE, DISCLAIMER, MODEL_NAME)
    if filtered_df.empty:
        render_finding("No records match the current filter selection. Adjust the sidebar filters to continue.", warning=True)
        return

    tabs = st.tabs(
        [
            "Overview",
            "Demographics",
            "Mental Health Outcomes",
            "Risk Factors",
            "Support Patterns",
            "Model Lab",
            "Prediction Sandbox",
            "Data Explorer",
        ]
    )

    with tabs[0]:
        _render_overview(filtered_df, filter_state)
    with tabs[1]:
        _render_demographics(filter_state)
    with tabs[2]:
        _render_outcomes(filter_state)
    with tabs[3]:
        _render_risk_factors(filter_state)
    with tabs[4]:
        _render_support_patterns(filter_state)
    with tabs[5]:
        _render_model_lab()
    with tabs[6]:
        _render_prediction_sandbox(datasets.analytics_df)
    with tabs[7]:
        _render_data_explorer(filtered_df)


if __name__ == "__main__":
    main()
