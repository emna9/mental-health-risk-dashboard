import pandas as pd
from fastapi import APIRouter

from app.backend.dependencies import get_loaded_datasets
from app.backend.schemas.models import ModelComparisonResponse
from app.utils.constants import RANKING_RULE

router = APIRouter()


@router.get("/compare", response_model=ModelComparisonResponse)
def compare_models() -> ModelComparisonResponse:
    df = get_loaded_datasets().comparison_df
    models = df.where(pd.notnull(df), None).to_dict(orient="records")
    return ModelComparisonResponse(models=models, ranking_rule=RANKING_RULE)
