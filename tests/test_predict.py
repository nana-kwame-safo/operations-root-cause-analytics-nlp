from __future__ import annotations

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.dependencies import get_predictor
from app.api.routes import predict
from app.schemas.prediction import PredictionRequest


class FakePredictor:
    def predict(self, text: str, domain: str, threshold: float, top_k: int) -> dict:
        return {
            "input_text": text,
            "domain": domain,
            "predicted_labels": [
                {
                    "label": "Anomaly_2",
                    "score": 0.81,
                    "explanation_terms": ["altitude", "approach", "clearance"],
                },
                {
                    "label": "Anomaly_19",
                    "score": 0.64,
                    "explanation_terms": ["communication", "controller", "instruction"],
                },
            ][:top_k],
            "threshold_used": threshold,
            "review_flag": False,
            "message": "Predictions generated successfully.",
        }


def test_predict_endpoint_schema():
    response = predict(
        PredictionRequest(
            text="Crew had conflicting instructions during approach.",
            domain="aviation",
            threshold=0.5,
            top_k=2,
        ),
        predictor=FakePredictor(),
    )
    payload = response.model_dump()
    assert payload["domain"] == "aviation"
    assert payload["predicted_labels"][0]["label"] == "Anomaly_2"
    assert payload["threshold_used"] == 0.5


def test_predict_empty_input_returns_validation_error():
    with pytest.raises(ValidationError):
        PredictionRequest(text="   ", domain="aviation", threshold=0.5, top_k=5)


def test_predict_missing_artifact_behavior():
    try:
        response = predict(
            PredictionRequest(
                text="Sample narrative",
                domain="aviation",
                threshold=0.5,
                top_k=5,
            ),
            predictor=get_predictor(),
        )
    except HTTPException as exc:
        assert exc.status_code == 503
        assert "Model artifact not found" in str(exc.detail)
        return

    # If a local artifact exists, prediction should succeed instead of raising.
    payload = response.model_dump()
    assert payload["domain"] == "aviation"
    assert isinstance(payload["predicted_labels"], list)


def test_predict_unknown_domain_returns_404():
    with pytest.raises(HTTPException) as exc:
        predict(
            PredictionRequest(
                text="Sample narrative",
                domain="housing_repairs",
                threshold=0.5,
                top_k=5,
            ),
            predictor=get_predictor(),
        )
    assert exc.value.status_code == 404
    assert "not implemented" in str(exc.value.detail)
