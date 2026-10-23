from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    root: Path
    raw_data: Path
    cleaned_data: Path
    modeling_data: Path
    comparison_data: Path
    models_dir: Path
    artifact_path: Path


def get_paths() -> AppPaths:
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data"
    processed_dir = data_dir / "processed"
    models_dir = root / "models"
    return AppPaths(
        root=root,
        raw_data=data_dir / "raw" / "mental_health.csv",
        cleaned_data=processed_dir / "mental_health_cleaned.csv",
        modeling_data=processed_dir / "mental_health_processed_no_proxy_cols.csv",
        comparison_data=processed_dir / "model_comparison_ranked.csv",
        models_dir=models_dir,
        artifact_path=models_dir / "balanced_rf_artifact.joblib",
    )
