from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from imblearn.ensemble import BalancedRandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from app.config.settings import get_paths
from app.utils.constants import (
    DISCLAIMER,
    MODEL_NAME,
    NOMINAL_COLS,
    ORDINAL_CATEGORIES,
    ORDINAL_COLS,
    PROXY_DROP_COLS,
    TARGET_COL,
)


@dataclass(frozen=True)
class PredictionResult:
    predicted_class: int
    probability: float
    probability_label: str
    disclaimer: str


def build_preprocessor(feature_frame: pd.DataFrame) -> ColumnTransformer:
    numeric_cols = [
        column for column in feature_frame.columns if column not in ORDINAL_COLS and column not in NOMINAL_COLS
    ]
    return ColumnTransformer(
        transformers=[
            (
                "ordinal",
                OrdinalEncoder(
                    categories=ORDINAL_CATEGORIES,
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
                ORDINAL_COLS,
            ),
            (
                "nominal",
                OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False),
                NOMINAL_COLS,
            ),
            ("numeric", "passthrough", numeric_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def train_and_persist_best_model(force: bool = False) -> Path:
    paths = get_paths()
    if paths.artifact_path.exists() and not force:
        return paths.artifact_path

    df = pd.read_csv(paths.cleaned_data)
    y = df[TARGET_COL].astype(int)
    X = df.drop(columns=[TARGET_COL] + PROXY_DROP_COLS)
    preprocessor = build_preprocessor(X)
    X_encoded = preprocessor.fit_transform(X)

    model = BalancedRandomForestClassifier(
        n_estimators=700,
        max_depth=10,
        max_features="sqrt",
        min_samples_leaf=10,
        random_state=42,
        n_jobs=1,
    )
    model.fit(X_encoded, y)

    artifact = {
        "model_name": MODEL_NAME,
        "preprocessor": preprocessor,
        "model": model,
        "input_columns": list(X.columns),
        "feature_names": list(preprocessor.get_feature_names_out()),
    }
    paths.models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, paths.artifact_path)
    return paths.artifact_path


def load_best_model_artifact() -> dict | None:
    artifact_path = get_paths().artifact_path
    if not artifact_path.exists():
        return None
    return joblib.load(artifact_path)


def get_feature_importance_table(top_n: int = 15) -> pd.DataFrame:
    artifact = load_best_model_artifact()
    if artifact is None:
        return pd.DataFrame(columns=["Feature", "Importance"])
    model = artifact["model"]
    feature_names = artifact["feature_names"]
    importance_df = pd.DataFrame(
        {
            "Feature": [feature.replace("_", " ") for feature in feature_names],
            "Importance": model.feature_importances_,
        }
    ).sort_values("Importance", ascending=False)
    return importance_df.head(top_n)


def predict_single_record(form_input: dict[str, object]) -> PredictionResult:
    artifact = load_best_model_artifact()
    if artifact is None:
        raise FileNotFoundError("Balanced RF artifact is not available.")

    input_columns = artifact["input_columns"]
    missing_columns = [column for column in input_columns if column not in form_input]
    if missing_columns:
        raise ValueError(f"Missing required inputs: {', '.join(missing_columns)}")

    row = pd.DataFrame([{column: form_input[column] for column in input_columns}])
    X_encoded = artifact["preprocessor"].transform(row)
    probability = float(artifact["model"].predict_proba(X_encoded)[0, 1])
    predicted_class = int(probability >= 0.5)

    if probability >= 0.75:
        probability_label = "Elevated pattern in this dataset"
    elif probability >= 0.5:
        probability_label = "Moderate pattern in this dataset"
    else:
        probability_label = "Lower pattern in this dataset"

    return PredictionResult(
        predicted_class=predicted_class,
        probability=probability,
        probability_label=probability_label,
        disclaimer=DISCLAIMER,
    )
