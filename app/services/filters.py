from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.utils.constants import TARGET_COL


@dataclass(frozen=True)
class FilterState:
    age_range: tuple[int, int]
    genders: tuple[str, ...]
    countries: tuple[str, ...]
    education_levels: tuple[str, ...]
    employment_statuses: tuple[str, ...]
    target_values: tuple[int, ...]
    search_text: str = ""


def build_filter_state(
    age_range: tuple[int, int],
    genders: list[str] | tuple[str, ...],
    countries: list[str] | tuple[str, ...],
    education_levels: list[str] | tuple[str, ...],
    employment_statuses: list[str] | tuple[str, ...],
    target_values: list[int] | tuple[int, ...],
    search_text: str = "",
) -> FilterState:
    return FilterState(
        age_range=age_range,
        genders=tuple(genders),
        countries=tuple(countries),
        education_levels=tuple(education_levels),
        employment_statuses=tuple(employment_statuses),
        target_values=tuple(target_values),
        search_text=search_text.strip().lower(),
    )


def apply_filters(df: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    filtered = df.copy()
    filtered = filtered[filtered["Age"].between(filters.age_range[0], filters.age_range[1])]
    if filters.genders:
        filtered = filtered[filtered["Gender"].isin(filters.genders)]
    if filters.countries:
        filtered = filtered[filtered["Country"].isin(filters.countries)]
    if filters.education_levels:
        filtered = filtered[filtered["Education"].isin(filters.education_levels)]
    if filters.employment_statuses:
        filtered = filtered[filtered["Employment_Status"].isin(filters.employment_statuses)]
    if filters.target_values:
        filtered = filtered[filtered[TARGET_COL].isin(filters.target_values)]
    if filters.search_text:
        text_mask = filtered.astype(str).apply(
            lambda column: column.str.lower().str.contains(filters.search_text, na=False)
        )
        filtered = filtered[text_mask.any(axis=1)]
    return filtered
