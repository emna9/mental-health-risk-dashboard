from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st

_BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8000").rstrip("/")
_API = f"{_BASE_URL}/api/v1"
_TIMEOUT = 10


class BackendUnavailableError(Exception):
    pass


def _get(path: str, params: dict | None = None) -> dict:
    try:
        resp = requests.get(f"{_API}{path}", params=params, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        raise BackendUnavailableError(
            f"Cannot reach backend at {_BASE_URL}. Is `uvicorn app.backend.main:app --reload` running?"
        )
    except requests.exceptions.Timeout:
        raise BackendUnavailableError(f"Backend timed out after {_TIMEOUT}s.")
    except requests.exceptions.HTTPError as exc:
        raise BackendUnavailableError(
            f"Backend HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        )


def _post(path: str, body: dict) -> dict:
    try:
        resp = requests.post(f"{_API}{path}", json=body, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        raise BackendUnavailableError(f"Cannot reach backend at {_BASE_URL}.")
    except requests.exceptions.Timeout:
        raise BackendUnavailableError(f"Backend POST timed out after {_TIMEOUT}s.")
    except requests.exceptions.HTTPError as exc:
        raise BackendUnavailableError(
            f"Backend HTTP {exc.response.status_code}: {exc.response.text[:200]}"
        )


def _filter_params(fs) -> dict:
    params: dict = {
        "age_min": fs.age_range[0],
        "age_max": fs.age_range[1],
        "search": fs.search_text,
    }
    if fs.genders:
        params["gender"] = list(fs.genders)
    if fs.countries:
        params["country"] = list(fs.countries)
    if fs.education_levels:
        params["education"] = list(fs.education_levels)
    if fs.employment_statuses:
        params["employment_status"] = list(fs.employment_statuses)
    if fs.target_values and set(fs.target_values) != {0, 1}:
        params["target"] = list(fs.target_values)
    return params


def check_health() -> dict:
    return _get("/health")


@st.cache_data(ttl=30, show_spinner=False)
def fetch_summary(filter_state) -> dict:
    return _get("/analytics/summary", _filter_params(filter_state))


@st.cache_data(ttl=30, show_spinner=False)
def fetch_demographics(filter_state) -> dict[str, pd.DataFrame]:
    data = _get("/analytics/demographics", _filter_params(filter_state))
    return {k: pd.DataFrame(data[k]) for k in ("age", "gender", "country", "employment", "education")}


@st.cache_data(ttl=30, show_spinner=False)
def fetch_factors(filter_state) -> dict[str, pd.DataFrame]:
    data = _get("/analytics/factors", _filter_params(filter_state))
    return {k: pd.DataFrame(data[k]) for k in ("factor_gaps", "symptom_summary", "stress_support", "feature_importance")}


@st.cache_data(ttl=30, show_spinner=False)
def fetch_support_patterns(filter_state) -> dict[str, pd.DataFrame]:
    data = _get("/analytics/support", _filter_params(filter_state))
    return {
        "support_patterns": pd.DataFrame(data["support_patterns"]),
        "proxy_shares": pd.DataFrame(data["proxy_shares"]),
    }


@st.cache_data(ttl=300, show_spinner=False)
def fetch_model_comparison() -> tuple[pd.DataFrame, str]:
    data = _get("/models/compare")
    return pd.DataFrame(data["models"]), data["ranking_rule"]


def call_predict(field_values: dict) -> dict:
    return _post("/predict", field_values)
