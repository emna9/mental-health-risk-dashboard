from __future__ import annotations

import os
import time

import pandas as pd
import requests
import streamlit as st

_raw_base_url = os.environ.get("BACKEND_URL", "http://localhost:8000").strip().rstrip("/")
if not _raw_base_url.startswith(("http://", "https://")):
    # Render's fromService.host provides a bare hostname.
    _raw_base_url = f"https://{_raw_base_url}"
_BASE_URL = _raw_base_url
_API = f"{_BASE_URL}/api/v1"
_TIMEOUT = int(os.environ.get("BACKEND_TIMEOUT", "90"))
_ATTEMPTS = max(1, int(os.environ.get("BACKEND_ATTEMPTS", "8")))
_RETRYABLE_STATUS = {502, 503, 504}
_BACKOFF_SECONDS = (2, 4, 8, 12, 20)


class BackendUnavailableError(Exception):
    pass


def _request(method: str, path: str, *, params: dict | None = None, body: dict | None = None) -> dict:
    """Call the API, retrying through free-tier cold starts (502/503/504)."""
    last_error = "no response"
    for attempt in range(_ATTEMPTS):
        try:
            resp = requests.request(
                method,
                f"{_API}{path}",
                params=params,
                json=body,
                timeout=(10, _TIMEOUT),
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as exc:
            last_error = type(exc).__name__
        else:
            if resp.status_code in _RETRYABLE_STATUS:
                last_error = f"HTTP {resp.status_code}"
            else:
                if resp.status_code >= 400:
                    raise BackendUnavailableError(
                        f"Backend at {_BASE_URL} returned HTTP {resp.status_code}."
                    )
                return resp.json()

        if attempt < _ATTEMPTS - 1:
            time.sleep(_BACKOFF_SECONDS[min(attempt, len(_BACKOFF_SECONDS) - 1)])

    raise BackendUnavailableError(
        f"Backend at {_BASE_URL} is still starting after {_ATTEMPTS} attempts ({last_error})."
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
    return _request("GET", "/health")


@st.cache_data(ttl=30, show_spinner=False)
def fetch_summary(filter_state) -> dict:
    return _request("GET", "/analytics/summary", params=_filter_params(filter_state))


@st.cache_data(ttl=30, show_spinner=False)
def fetch_demographics(filter_state) -> dict[str, pd.DataFrame]:
    data = _request("GET", "/analytics/demographics", params=_filter_params(filter_state))
    return {k: pd.DataFrame(data[k]) for k in ("age", "gender", "country", "employment", "education")}


@st.cache_data(ttl=30, show_spinner=False)
def fetch_factors(filter_state) -> dict[str, pd.DataFrame]:
    data = _request("GET", "/analytics/factors", params=_filter_params(filter_state))
    return {k: pd.DataFrame(data[k]) for k in ("factor_gaps", "symptom_summary", "stress_support", "feature_importance")}


@st.cache_data(ttl=30, show_spinner=False)
def fetch_support_patterns(filter_state) -> dict[str, pd.DataFrame]:
    data = _request("GET", "/analytics/support", params=_filter_params(filter_state))
    return {
        "support_patterns": pd.DataFrame(data["support_patterns"]),
        "proxy_shares": pd.DataFrame(data["proxy_shares"]),
    }


@st.cache_data(ttl=300, show_spinner=False)
def fetch_model_comparison() -> tuple[pd.DataFrame, str]:
    data = _request("GET", "/models/compare")
    return pd.DataFrame(data["models"]), data["ranking_rule"]


def call_predict(field_values: dict) -> dict:
    return _request("POST", "/predict", body=field_values)
