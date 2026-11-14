from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import pandas as pd

from app.config.settings import get_paths


@dataclass(frozen=True)
class LoadedDatasets:
    analytics_df: pd.DataFrame
    modeling_df: pd.DataFrame
    comparison_df: pd.DataFrame


def _load_datasets_impl() -> LoadedDatasets:
    paths = get_paths()
    analytics_df = pd.read_csv(paths.cleaned_data)
    modeling_df = pd.read_csv(paths.modeling_data)
    comparison_df = pd.read_csv(paths.comparison_data)
    return LoadedDatasets(
        analytics_df=analytics_df,
        modeling_df=modeling_df,
        comparison_df=comparison_df,
    )


@lru_cache(maxsize=1)
def load_datasets() -> LoadedDatasets:
    # The bundled CSVs are immutable at runtime, so one cached copy serves both
    # the dashboard and the API without importing Streamlit into the API process.
    return _load_datasets_impl()


def get_ranked_models() -> pd.DataFrame:
    return load_datasets().comparison_df.copy()
