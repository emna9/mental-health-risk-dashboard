from pydantic import BaseModel, ConfigDict


class RecordItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    record_id: int


class PaginatedRecordsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int
    records: list[RecordItem]
