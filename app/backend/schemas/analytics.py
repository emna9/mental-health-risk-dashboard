from typing import Any

from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_records: int
    issue_rate: float
    average_stress: float
    average_loneliness: float
    average_support: float
    winning_model: str
    findings: list[str]


class DemographicsResponse(BaseModel):
    age: list[dict[str, Any]]
    gender: list[dict[str, Any]]
    country: list[dict[str, Any]]
    employment: list[dict[str, Any]]
    education: list[dict[str, Any]]


class FactorsResponse(BaseModel):
    factor_gaps: list[dict[str, Any]]
    symptom_summary: list[dict[str, Any]]
    stress_support: list[dict[str, Any]]
    feature_importance: list[dict[str, Any]]


class TrendsResponse(BaseModel):
    age_bands: list[dict[str, Any]]
    work_stress_levels: list[dict[str, Any]]
    social_support_levels: list[dict[str, Any]]
    symptom_burden_bands: list[dict[str, Any]]


class SupportPatternsResponse(BaseModel):
    support_patterns: list[dict[str, Any]]  # Measure, Response, Issue_Rate, Respondents
    proxy_shares: list[dict[str, Any]]       # Measure, Share
