from __future__ import annotations

import math
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from app.backend.dependencies import get_loaded_datasets, parse_filters
from app.backend.schemas.records import PaginatedRecordsResponse, RecordItem
from app.services.filters import FilterState, apply_filters

router = APIRouter()


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    frame = df.copy()
    for col in frame.select_dtypes(include="category").columns:
        frame[col] = frame[col].astype(object)
    return frame.where(pd.notnull(frame), None).to_dict(orient="records")


@router.get("/records", response_model=PaginatedRecordsResponse)
def list_records(
    filters: Annotated[FilterState, Depends(parse_filters)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
) -> PaginatedRecordsResponse:
    datasets = get_loaded_datasets()
    df = datasets.analytics_df.copy()
    df.insert(0, "record_id", range(len(df)))
    filtered = apply_filters(df, filters)

    total = len(filtered)
    pages = math.ceil(total / page_size) if total > 0 else 0
    start = (page - 1) * page_size
    page_df = filtered.iloc[start : start + page_size]
    records = [RecordItem(**r) for r in _df_to_records(page_df)]

    return PaginatedRecordsResponse(
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
        records=records,
    )


@router.get("/records/{record_id}", response_model=RecordItem)
def get_record(record_id: int) -> RecordItem:
    datasets = get_loaded_datasets()
    df = datasets.analytics_df
    if record_id < 0 or record_id >= len(df):
        raise HTTPException(status_code=404, detail=f"Record {record_id} not found")
    row_df = df.iloc[[record_id]].copy()
    row_df.insert(0, "record_id", [record_id])
    return RecordItem(**_df_to_records(row_df)[0])
