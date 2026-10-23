from fastapi import APIRouter, HTTPException

from app.backend.schemas.predict import PredictionRequest, PredictionResponse
from app.services.model_service import predict_single_record
from app.utils.constants import MODEL_NAME

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(body: PredictionRequest) -> PredictionResponse:
    try:
        result = predict_single_record(body.model_dump())
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model artifact unavailable. Run train_and_persist_best_model() first.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return PredictionResponse(
        predicted_class=result.predicted_class,
        probability=result.probability,
        probability_label=result.probability_label,
        model_name=MODEL_NAME,
        disclaimer=result.disclaimer,
    )
