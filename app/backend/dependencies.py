from __future__ import annotations

from functools import lru_cache

from fastapi import Query

from app.services.data_loader import LoadedDatasets, load_datasets
from app.services.filters import FilterState, build_filter_state
from app.services.model_service import load_best_model_artifact


def get_loaded_datasets() -> LoadedDatasets:
    return load_datasets()


@lru_cache(maxsize=1)
def get_model_artifact() -> dict | None:
    return load_best_model_artifact()


def parse_filters(
    age_min: int = Query(18, ge=0),
    age_max: int = Query(100, le=120),
    gender: list[str] = Query(default=[]),
    country: list[str] = Query(default=[]),
    education: list[str] = Query(default=[]),
    employment_status: list[str] = Query(default=[]),
    target: list[int] = Query(default=[]),
    search: str = Query(default=""),
) -> FilterState:
    return build_filter_state(
        age_range=(age_min, age_max),
        genders=gender,
        countries=country,
        education_levels=education,
        employment_statuses=employment_status,
        target_values=target,
        search_text=search,
    )
