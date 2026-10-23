from typing import Any

from pydantic import BaseModel


class ModelComparisonResponse(BaseModel):
    models: list[dict[str, Any]]
    ranking_rule: str
