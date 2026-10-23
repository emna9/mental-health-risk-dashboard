from pydantic import BaseModel


class ArtifactStatus(BaseModel):
    analytics_csv: bool
    modeling_csv: bool
    comparison_csv: bool
    model_artifact: bool


class DatasetCounts(BaseModel):
    analytics_records: int
    modeling_records: int


class HealthResponse(BaseModel):
    status: str
    artifacts: ArtifactStatus
    dataset_rows: DatasetCounts
    deployed_model: str
