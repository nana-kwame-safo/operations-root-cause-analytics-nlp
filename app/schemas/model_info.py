"""Model metadata schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvaluationMetrics(BaseModel):
    micro_f1: float | None = Field(default=None, ge=0.0, le=1.0)
    macro_f1: float | None = Field(default=None, ge=0.0, le=1.0)
    samples_f1: float | None = Field(default=None, ge=0.0, le=1.0)
    hamming_loss: float | None = Field(default=None, ge=0.0, le=1.0)


class ModelInfoResponse(BaseModel):
    app_name: str
    active_domain: str
    model_name: str
    model_type: str
    label_count: int
    threshold: float
    training_approach: str
    version: str
    training_date: str
    dataset_provenance_note: str
    evaluation_metrics: EvaluationMetrics
    limitation_note: str
    artifact_status: str
