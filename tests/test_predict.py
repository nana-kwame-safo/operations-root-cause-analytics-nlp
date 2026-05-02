from __future__ import annotations

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.dependencies import get_predictor
from app.api.routes import predict
from app.schemas.prediction import PredictionRequest


class FakePredictor:
    def predict(self, text: str, domain: str, threshold: float, top_k: int) -> dict:
        labels = [
            {
                "label": "Anomaly_2",
                "label_id": "Anomaly_2",
                "label_name": "Draft Altitude or Flight Path Deviation Indicator",
                "short_name": "Altitude Path",
                "score": 0.81,
                "score_percent": 81.0,
                "plain_language_description": "Signals wording related to altitude assignment or flight path deviation risk.",
                "technical_description": "Draft label tied to terms around descent and altitude control.",
                "operational_interpretation": "Review altitude clearance context.",
                "review_guidance": "Cross-check ATC communication records.",
                "taxonomy_status": "draft_from_model_features",
                "confidence_note": "Model confidence is probabilistic and requires analyst validation.",
                "example_cues": ["altitude", "descent"],
                "evidence_terms": [
                    {
                        "term": "altitude",
                        "display_term": "altitude",
                        "contribution": 0.214,
                        "importance": "high",
                    }
                ],
                "evidence_spans": [
                    {
                        "term": "altitude",
                        "start": 21,
                        "end": 29,
                        "importance": "high",
                    }
                ],
                "explanation_terms": ["altitude", "approach", "clearance"],
                "explanation_method": "tfidf_linear_contribution",
            },
            {
                "label": "Anomaly_19",
                "label_id": "Anomaly_19",
                "label_name": "Draft Separation or Conflict Management Indicator",
                "short_name": "Separation Conflict",
                "score": 0.64,
                "score_percent": 64.0,
                "plain_language_description": "Signals potential separation loss or conflict handling concerns.",
                "technical_description": "Draft label linked to conflict and separation terms.",
                "operational_interpretation": "Review conflict management actions.",
                "review_guidance": "Corroborate with radar timeline.",
                "taxonomy_status": "draft_from_model_features",
                "confidence_note": "Requires analyst validation.",
                "example_cues": ["conflict", "traffic"],
                "evidence_terms": [],
                "evidence_spans": [],
                "explanation_terms": ["communication", "controller", "instruction"],
                "explanation_method": "fallback_token_match",
            },
        ][:top_k]
        return {
            "status": "ok",
            "input_text": text,
            "domain": domain,
            "model_info": {
                "model_name": "TF-IDF + One-vs-Rest Logistic Regression",
                "threshold_used": threshold,
                "artifact_status": "available",
                "training_approach": "TF-IDF vectorization with One-vs-Rest Logistic Regression",
                "explanation_method": "tfidf_linear_contribution",
            },
            "summary": {
                "predicted_count": len(labels),
                "top_label_id": labels[0]["label_id"] if labels else None,
                "top_label_name": labels[0]["label_name"] if labels else None,
                "top_score": labels[0]["score"] if labels else None,
                "top_score_percent": labels[0]["score_percent"] if labels else None,
                "review_flag": False,
                "review_message": "Predictions generated successfully.",
            },
            "predicted_labels": labels,
            "top_scores": [
                {
                    "label_id": item["label_id"],
                    "label_name": item["label_name"],
                    "short_name": item["short_name"],
                    "score": item["score"],
                    "score_percent": item["score_percent"],
                }
                for item in labels
            ],
            "all_scores": [
                {
                    "label_id": item["label_id"],
                    "label_name": item["label_name"],
                    "short_name": item["short_name"],
                    "score": item["score"],
                    "score_percent": item["score_percent"],
                }
                for item in labels
            ],
            "messages": [
                "Predictions generated successfully.",
                "Outputs are root-cause-related factor indicators for analyst review support.",
            ],
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
    assert payload["predicted_labels"][0]["label_name"]
    assert payload["predicted_labels"][0]["evidence_terms"][0]["term"] == "altitude"
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
        assert "artifact is missing" in str(exc.detail).lower()
        return

    # If a local artifact exists, prediction should succeed instead of raising.
    payload = response.model_dump()
    assert payload["domain"] == "aviation"
    assert isinstance(payload["predicted_labels"], list)


def test_predict_response_includes_explainability_fields():
    response = predict(
        PredictionRequest(
            text="Crew had conflicting instructions during approach.",
            domain="aviation",
            threshold=0.5,
            top_k=1,
        ),
        predictor=FakePredictor(),
    )
    payload = response.model_dump()
    first = payload["predicted_labels"][0]
    assert first["label_id"] == "Anomaly_2"
    assert first["label_name"]
    assert first["evidence_terms"]
    assert first["evidence_terms"][0]["importance"] in {"high", "medium", "low"}


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
