from __future__ import annotations

from typing import Annotated, Any

import pandas as pd
from fastapi import APIRouter, Depends

from app.backend.dependencies import get_loaded_datasets, parse_filters
from app.backend.schemas.analytics import (
    DemographicsResponse,
    FactorsResponse,
    SummaryResponse,
    SupportPatternsResponse,
    TrendsResponse,
)
from app.services.analytics import (
    compute_demographic_breakdowns,
    compute_factor_analysis,
    compute_overview_metrics,
    compute_support_patterns,
)
from app.services.filters import FilterState, apply_filters
from app.services.model_service import get_feature_importance_table
from app.utils.constants import SYMPTOM_COLS, TARGET_COL

router = APIRouter()


def _df_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    frame = df.copy()
    for col in frame.select_dtypes(include="category").columns:
        frame[col] = frame[col].astype(object)
    return frame.where(pd.notnull(frame), None).to_dict(orient="records")


def _filtered(filters: FilterState) -> pd.DataFrame:
    return apply_filters(get_loaded_datasets().analytics_df, filters)


@router.get("/summary", response_model=SummaryResponse)
def get_summary(filters: Annotated[FilterState, Depends(parse_filters)]) -> SummaryResponse:
    datasets = get_loaded_datasets()
    df = apply_filters(datasets.analytics_df, filters)
    m = compute_overview_metrics(df, datasets.comparison_df)
    return SummaryResponse(
        total_records=m.total_records,
        issue_rate=m.issue_rate,
        average_stress=m.average_stress,
        average_loneliness=m.average_loneliness,
        average_support=m.average_support,
        winning_model=m.winning_model,
        findings=list(m.findings),
    )


@router.get("/demographics", response_model=DemographicsResponse)
def get_demographics(filters: Annotated[FilterState, Depends(parse_filters)]) -> DemographicsResponse:
    df = _filtered(filters)
    if df.empty:
        return DemographicsResponse(age=[], gender=[], country=[], employment=[], education=[])
    bd = compute_demographic_breakdowns(df)
    return DemographicsResponse(
        age=_df_to_records(bd["age"]),
        gender=_df_to_records(bd["gender"]),
        country=_df_to_records(bd["country"]),
        employment=_df_to_records(bd["employment"]),
        education=_df_to_records(bd["education"]),
    )


@router.get("/factors", response_model=FactorsResponse)
def get_factors(filters: Annotated[FilterState, Depends(parse_filters)]) -> FactorsResponse:
    df = _filtered(filters)
    if df.empty:
        return FactorsResponse(factor_gaps=[], symptom_summary=[], stress_support=[], feature_importance=[])

    factor_data = compute_factor_analysis(df)

    # Symptom summary: mean score by symptom and target class, with gap
    grp = df.groupby(TARGET_COL)[SYMPTOM_COLS].mean()
    symp_df = grp.T.reset_index().rename(columns={"index": "Symptom"})
    symp_df.columns = [str(c) for c in symp_df.columns]
    rename_map = {}
    if "0" in symp_df.columns:
        rename_map["0"] = "No_Issue_Mean"
    if "1" in symp_df.columns:
        rename_map["1"] = "Issue_Mean"
    if rename_map:
        symp_df = symp_df.rename(columns=rename_map)
    symp_df["Symptom"] = symp_df["Symptom"].str.replace("_", " ")
    if "No_Issue_Mean" in symp_df.columns and "Issue_Mean" in symp_df.columns:
        symp_df["Gap"] = symp_df["Issue_Mean"] - symp_df["No_Issue_Mean"]
        symp_df = symp_df.sort_values("Gap", ascending=False)

    importance = get_feature_importance_table(top_n=15)

    return FactorsResponse(
        factor_gaps=_df_to_records(factor_data["factor_gaps"]),
        symptom_summary=_df_to_records(symp_df),
        stress_support=_df_to_records(factor_data["stress_support"]),
        feature_importance=_df_to_records(importance),
    )


@router.get("/trends", response_model=TrendsResponse)
def get_trends(filters: Annotated[FilterState, Depends(parse_filters)]) -> TrendsResponse:
    df = _filtered(filters)
    if df.empty:
        return TrendsResponse(age_bands=[], work_stress_levels=[], social_support_levels=[], symptom_burden_bands=[])

    age_bands = _df_to_records(compute_demographic_breakdowns(df)["age"])

    stress_df = (
        df.groupby("Work_Stress_Level", observed=False)[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
    )

    support_df = (
        df.groupby("Social_Support", observed=False)[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
    )

    burden = df[SYMPTOM_COLS].sum(axis=1)
    burden_bins = pd.cut(
        burden,
        bins=[-1, 3, 7, 11, 15],
        labels=["Low (0-3)", "Moderate (4-7)", "High (8-11)", "Severe (12-15)"],
    )
    burden_df = (
        df.assign(Symptom_Burden=burden_bins)
        .groupby("Symptom_Burden", observed=False)[TARGET_COL]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "Issue_Rate", "count": "Respondents"})
    )

    return TrendsResponse(
        age_bands=age_bands,
        work_stress_levels=_df_to_records(stress_df),
        social_support_levels=_df_to_records(support_df),
        symptom_burden_bands=_df_to_records(burden_df),
    )


@router.get("/support", response_model=SupportPatternsResponse)
def get_support(filters: Annotated[FilterState, Depends(parse_filters)]) -> SupportPatternsResponse:
    df = _filtered(filters)
    if df.empty:
        return SupportPatternsResponse(support_patterns=[], proxy_shares=[])
    support = compute_support_patterns(df)
    return SupportPatternsResponse(
        support_patterns=_df_to_records(support["support_patterns"]),
        proxy_shares=_df_to_records(support["proxy_shares"]),
    )
