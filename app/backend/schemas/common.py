from pydantic import BaseModel


class ApiError(BaseModel):
    detail: str
    status_code: int
