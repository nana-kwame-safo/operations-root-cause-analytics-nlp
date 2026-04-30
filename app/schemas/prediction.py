"""Prediction endpoint schemas."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, field_validator

from app.core.constants import DEFAULT_DOMAIN, DEFAULT_THRESHOLD, DEFAULT_TOP_K, MAX_TOP_K


class PredictionRequest(BaseModel):
    text: str = Field(..., description="Incident narrative text.")
    domain: str = Field(DEFAULT_DOMAIN, description="Narrative domain identifier.")
    threshold: float = Field(
        DEFAULT_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for predicted labels.",
    )
    top_k: int = Field(
        DEFAULT_TOP_K,
        ge=1,
        le=MAX_TOP_K,
        description="Maximum number of labels to return after thresholding.",
    )

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Narrative text must not be empty.")
        return value.strip()


class PredictedLabel(BaseModel):
    label: str
    score: float = Field(..., ge=0.0, le=1.0)
    explanation_terms: List[str] = Field(default_factory=list)


class PredictionResponse(BaseModel):
    input_text: str
    domain: str
    predicted_labels: List[PredictedLabel]
    threshold_used: float
    review_flag: bool
    message: str
