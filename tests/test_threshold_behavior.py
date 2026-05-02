from __future__ import annotations

import numpy as np

from app.services.model_loader import LoadedModelBundle
from app.services.predictor import Predictor


class FakeModel:
    def __init__(self, scores):
        self._scores = np.asarray([scores], dtype=float)

    def predict_proba(self, texts):
        return self._scores


class FakeRegistry:
    def is_implemented(self, domain: str) -> bool:
        return domain == "aviation"


class FakeLoader:
    def __init__(self, bundle: LoadedModelBundle):
        self.bundle = bundle

    def get_bundle(self, domain: str) -> LoadedModelBundle:
        return self.bundle


class FakeExplanationService:
    def explain_label(self, text: str, label_index: int, bundle: LoadedModelBundle, top_n: int):
        token = f"term_{label_index + 1}"
        return {
            "explanation_method": "fallback_token_match",
            "evidence_terms": [
                {
                    "term": token,
                    "display_term": token,
                    "contribution": 0.0,
                    "importance": "low",
                }
            ],
            "evidence_spans": [],
            "explanation_terms": [token],
        }

    def explanation_terms(self, text: str, label_index: int, bundle: LoadedModelBundle, top_n: int):
        return [f"term_{label_index + 1}"]


class FakeLabelRegistry:
    def get_label_metadata(self, *, domain_id: str, label_id: str, label_mapping=None):
        return {
            "label_id": label_id,
            "display_name": label_id,
            "short_name": label_id,
            "plain_language_description": "demo",
            "technical_description": "demo",
            "operational_interpretation": "demo",
            "review_guidance": "demo",
            "example_cues": [],
            "taxonomy_status": "fallback",
            "confidence_note": "demo",
        }


def make_predictor(scores):
    bundle = LoadedModelBundle(
        domain_id="aviation",
        model=FakeModel(scores),
        vectorizer=None,
        classifier=None,
        labels=["Anomaly_1", "Anomaly_2", "Anomaly_3"],
        available=True,
        artifact_status="loaded",
    )
    return Predictor(
        registry=FakeRegistry(),
        loader=FakeLoader(bundle),
        explanation_service=FakeExplanationService(),
        label_registry=FakeLabelRegistry(),
    )


def test_threshold_suppresses_low_scores():
    predictor = make_predictor([0.82, 0.47, 0.31])
    result = predictor.predict(
        text="narrative",
        domain="aviation",
        threshold=0.5,
        top_k=5,
    )
    assert len(result["predicted_labels"]) == 1
    assert result["predicted_labels"][0]["label"] == "Anomaly_1"


def test_no_labels_above_threshold_sets_review_flag():
    predictor = make_predictor([0.49, 0.32, 0.19])
    result = predictor.predict(
        text="narrative",
        domain="aviation",
        threshold=0.5,
        top_k=5,
    )
    assert result["predicted_labels"] == []
    assert result["review_flag"] is True
    assert "No strong factor prediction" in result["message"]


def test_borderline_scores_trigger_low_confidence_message():
    predictor = make_predictor([0.56, 0.53, 0.2])
    result = predictor.predict(
        text="narrative",
        domain="aviation",
        threshold=0.5,
        top_k=5,
    )
    assert len(result["predicted_labels"]) == 2
    assert result["review_flag"] is True
    assert "Low-confidence assessment" in result["message"]
