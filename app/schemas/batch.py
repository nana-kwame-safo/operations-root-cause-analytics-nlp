"""Batch prediction schemas."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from app.schemas.prediction import PredictedLabel


class BatchPredictionRow(BaseModel):
    row_index: int
    input_text: str
    predicted_labels: List[PredictedLabel]
    predicted_label_ids: List[str] = Field(default_factory=list)
    predicted_label_names: List[str] = Field(default_factory=list)
    review_flag: bool
    message: str


class BatchPredictionResponse(BaseModel):
    domain: str
    threshold_used: float = Field(..., ge=0.0, le=1.0)
    top_k_used: int = Field(..., ge=1)
    text_column: str
    row_count: int = Field(..., ge=0)
    results: List[BatchPredictionRow]
