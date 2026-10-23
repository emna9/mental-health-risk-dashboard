from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.services.filters import FilterState, apply_filters
from app.utils.constants import (
    DEMOGRAPHIC_COLS,
    MODEL_NAME,
    RISK_FACTOR_COLS,
    SUPPORT_PATTERN_COLS,
    SYMPTOM_COLS,
    TARGET_COL,
)
from app.utils.formatting import format_pct


@dataclass(frozen=True)
class OverviewMetrics:
    total_records: int
    issue_rate: float
    average_stress: float
    average_loneliness: float
    average_support: float
    winning_model: str
    findings: tuple[str, ...]


def compute_overview_metrics(filtered_df: pd.DataFrame, comparison_df: pd.DataFrame) -> OverviewMetrics:
    total_records = len(filtered_df)
    issue_rate = float(filtered_df[TARGET_COL].mean()) if total_records else 0.0
    average_stress = float(filtered_df["Work_Stress_Level"].mean()) if total_records else 0.0
    average_loneliness = float(filtered_df["Loneliness"].mean()) if total_records else 0.0
    average_support = float(filtered_df["Social_Support"].mean()) if total_records else 0.0

    findings = []
    if total_records:
        findings.append(
            f"{format_pct(issue_rate)} of the currently filtered respondents report a mental health issue."
        )
        findings.append(
            f"Average work stress is {average_stress:.1f}/10, while social support averages {average_support:.1f}/10."
        )
        symptoms = filtered_df[SYMPTOM_COLS].mean().sort_values(ascending=False).head(3)
        findings.append(
            "The highest average symptom burdens in this slice are "
            + ", ".join(f"{label.replace('_', ' ')} ({value:.1f})" for label, value in symptoms.items())
            + "."
        )
        support_share = (
            filtered_df["Ever_Sought_Treatment"].mean()
            if "Ever_Sought_Treatment" in filtered_df.columns
            else 0.0
        )
        findings.append(
            f"{format_pct(float(support_share))} of the filtered respondents have sought treatment, shown descriptively only."
        )
    else:
        findings.append("No records match the current filter selection.")

    winning_model = comparison_df.iloc[0]["Model"] if not comparison_df.empty else MODEL_NAME
    return OverviewMetrics(
        total_records=total_records,
        issue_rate=issue_rate,
        average_stress=average_stress,
        average_loneliness=average_loneliness,
        average_support=average_support,
        winning_model=winning_model,
        findings=tuple(findings),
    )


def compute_demographic_breakdowns(filtered_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    age_bins = pd.cut(
        filtered_df["Age"],
        bins=[17, 24, 34, 44, 54, 64, 100],
        labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        include_lowest=True,
    )
    age_df = (
        filtered_df.assign(Age_Band=age_bins)
        .groupby("Age_Band", observed=False)[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
    )
    gender_df = (
        filtered_df.groupby("Gender")[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
        .sort_values("Respondents", ascending=False)
    )
    country_df = (
        filtered_df.groupby("Country")[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
        .sort_values("Respondents", ascending=False)
        .head(8)
    )
    employment_df = (
        filtered_df.groupby("Employment_Status")[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
        .sort_values("Respondents", ascending=False)
    )
    education_df = (
        filtered_df.groupby("Education")[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
    )
    return {
        "age": age_df,
        "gender": gender_df,
        "country": country_df,
        "employment": employment_df,
        "education": education_df,
    }


def compute_factor_analysis(filtered_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    target_zero = filtered_df[filtered_df[TARGET_COL] == 0]
    target_one = filtered_df[filtered_df[TARGET_COL] == 1]
    gap_rows = []
    for column in RISK_FACTOR_COLS:
        baseline = float(target_zero[column].mean()) if not target_zero.empty else 0.0
        issue = float(target_one[column].mean()) if not target_one.empty else 0.0
        gap_rows.append(
            {
                "Factor": column.replace("_", " "),
                "No_Issue_Mean": round(baseline, 3),
                "Issue_Mean": round(issue, 3),
                "Gap": round(issue - baseline, 3),
            }
        )
    factor_gap_df = pd.DataFrame(gap_rows).sort_values("Gap", ascending=False)

    symptom_df = (
        filtered_df.melt(
            id_vars=[TARGET_COL],
            value_vars=SYMPTOM_COLS,
            var_name="Symptom",
            value_name="Score",
        )
        .assign(Symptom=lambda frame: frame["Symptom"].str.replace("_", " "))
    )
    scatter_df = (
        filtered_df.groupby(["Work_Stress_Level", "Social_Support"], observed=False)[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
    )
    return {
        "factor_gaps": factor_gap_df,
        "symptom_long": symptom_df,
        "stress_support": scatter_df,
    }


def compute_support_patterns(filtered_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    support_rows = []
    for column in SUPPORT_PATTERN_COLS:
        grouped = (
            filtered_df.groupby(column)[TARGET_COL]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={column: "Response", "mean": "Issue_Rate", "count": "Respondents"})
        )
        grouped["Measure"] = column.replace("_", " ")
        support_rows.append(grouped)
    support_df = pd.concat(support_rows, ignore_index=True)

    proxy_df = (
        filtered_df[["Previously_Diagnosed", "Ever_Sought_Treatment", "On_Therapy_Now", "On_Medication"]]
        .mean()
        .reset_index()
        .rename(columns={"index": "Measure", 0: "Share"})
    )
    proxy_df["Measure"] = proxy_df["Measure"].str.replace("_", " ")
    return {"support_patterns": support_df, "proxy_shares": proxy_df}


def compute_data_explorer(filtered_df: pd.DataFrame) -> pd.DataFrame:
    ordered_columns = DEMOGRAPHIC_COLS + ["Work_Stress_Level", "Financial_Stress", "Social_Support", "Loneliness", TARGET_COL]
    remaining = [column for column in filtered_df.columns if column not in ordered_columns]
    return filtered_df[ordered_columns + remaining]


def compute_model_lab_summary(comparison_df: pd.DataFrame) -> pd.DataFrame:
    return comparison_df.copy()
