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
    label_id: str | None = None
    label_name: str | None = None
    short_name: str | None = None
    score: float = Field(..., ge=0.0, le=1.0)
    score_percent: float | None = Field(default=None, ge=0.0, le=100.0)
    plain_language_description: str | None = None
    technical_description: str | None = None
    operational_interpretation: str | None = None
    review_guidance: str | None = None
    taxonomy_status: str | None = None
    confidence_note: str | None = None
    example_cues: List[str] = Field(default_factory=list)
    evidence_terms: List["EvidenceTerm"] = Field(default_factory=list)
    evidence_spans: List["EvidenceSpan"] = Field(default_factory=list)
    explanation_terms: List[str] = Field(default_factory=list)
    explanation_method: str | None = None


class EvidenceTerm(BaseModel):
    term: str
    display_term: str
    contribution: float
    importance: str = Field(pattern="^(high|medium|low)$")


class EvidenceSpan(BaseModel):
    term: str
    start: int = Field(ge=0)
    end: int = Field(ge=0)
    importance: str = Field(pattern="^(high|medium|low)$")


class ScoreItem(BaseModel):
    label_id: str
    label_name: str
    short_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    score_percent: float = Field(..., ge=0.0, le=100.0)


class PredictionSummary(BaseModel):
    predicted_count: int = Field(ge=0)
    top_label_id: str | None = None
    top_label_name: str | None = None
    top_score: float | None = Field(default=None, ge=0.0, le=1.0)
    top_score_percent: float | None = Field(default=None, ge=0.0, le=100.0)
    review_flag: bool
    review_message: str


class PredictionModelInfo(BaseModel):
    model_name: str
    threshold_used: float = Field(..., ge=0.0, le=1.0)
    artifact_status: str
    training_approach: str
    explanation_method: str


class PredictionResponse(BaseModel):
    status: str = "ok"
    input_text: str
    domain: str
    model_info: PredictionModelInfo | None = None
    summary: PredictionSummary | None = None
    predicted_labels: List[PredictedLabel]
    top_scores: List[ScoreItem] = Field(default_factory=list)
    all_scores: List[ScoreItem] = Field(default_factory=list)
    messages: List[str] = Field(default_factory=list)
    threshold_used: float
    review_flag: bool
    message: str
