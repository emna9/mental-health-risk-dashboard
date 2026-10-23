from fastapi import APIRouter

from app.backend.dependencies import get_loaded_datasets
from app.backend.schemas.health import ArtifactStatus, DatasetCounts, HealthResponse
from app.config.settings import get_paths
from app.utils.constants import MODEL_NAME

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    paths = get_paths()
    datasets = get_loaded_datasets()
    return HealthResponse(
        status="ok",
        artifacts=ArtifactStatus(
            analytics_csv=paths.cleaned_data.exists(),
            modeling_csv=paths.modeling_data.exists(),
            comparison_csv=paths.comparison_data.exists(),
            model_artifact=paths.artifact_path.exists(),
        ),
        dataset_rows=DatasetCounts(
            analytics_records=len(datasets.analytics_df),
            modeling_records=len(datasets.modeling_df),
        ),
        deployed_model=MODEL_NAME,
    )
