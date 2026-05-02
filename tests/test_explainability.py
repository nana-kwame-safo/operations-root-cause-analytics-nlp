from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.services.explanation import ExplanationService
from app.services.label_registry import LabelRegistryService
from app.services.model_loader import LoadedModelBundle


@dataclass
class _FakeSparseRow:
    indices: np.ndarray
    data: np.ndarray
    shape: tuple[int, int]

    @property
    def nnz(self) -> int:
        return int(len(self.indices))


class _FakeVectorizer:
    def __init__(self) -> None:
        self._features = np.array(
            [
                "altitude",
                "instruction",
                "altitude conflict",
                "weather",
            ]
        )

    def transform(self, texts: list[str]) -> _FakeSparseRow:
        text = texts[0].lower()
        indices: list[int] = []
        values: list[float] = []
        for idx, feature in enumerate(self._features):
            if feature == "altitude" and "altitude" in text:
                indices.append(idx)
                values.append(0.9)
            if feature == "instruction" and "instruction" in text:
                indices.append(idx)
                values.append(0.6)
            if feature == "altitude conflict" and "altitude conflict" in text:
                indices.append(idx)
                values.append(0.4)
        return _FakeSparseRow(
            indices=np.asarray(indices, dtype=int),
            data=np.asarray(values, dtype=float),
            shape=(1, len(self._features)),
        )

    def get_feature_names_out(self) -> np.ndarray:
        return self._features


class _FakeEstimator:
    def __init__(self, coef: list[float]) -> None:
        self.coef_ = np.asarray([coef], dtype=float)


class _FakeClassifier:
    def __init__(self) -> None:
        self.estimators_ = [
            _FakeEstimator([1.5, 0.8, 0.5, -0.1]),
        ]


def test_label_registry_loading() -> None:
    project_root = Path(__file__).resolve().parents[1]
    service = LabelRegistryService(project_root / "app/domains")
    metadata = service.get_label_metadata(domain_id="aviation", label_id="Anomaly_1")
    assert metadata["label_id"] == "Anomaly_1"
    assert metadata["display_name"]
    assert metadata["taxonomy_status"] == "draft_from_model_features"


def test_label_registry_fallback_for_unknown_label() -> None:
    project_root = Path(__file__).resolve().parents[1]
    service = LabelRegistryService(project_root / "app/domains")
    metadata = service.get_label_metadata(domain_id="aviation", label_id="Unknown_Label")
    assert metadata["display_name"] == "Unknown_Label"
    assert metadata["taxonomy_status"] == "fallback"


def test_explanation_extracts_evidence_terms_and_spans() -> None:
    bundle = LoadedModelBundle(
        domain_id="aviation",
        model={},
        vectorizer=_FakeVectorizer(),
        classifier=_FakeClassifier(),
        labels=["Anomaly_1"],
        available=True,
        artifact_status="available",
    )
    service = ExplanationService()
    text = "Conflicting altitude instruction was corrected after ATC communication."
    explanation = service.explain_label(text=text, label_index=0, bundle=bundle, top_n=3)

    assert explanation["explanation_method"] == "tfidf_linear_contribution"
    assert explanation["evidence_terms"]
    assert explanation["evidence_terms"][0]["term"] == "altitude"
    assert explanation["evidence_terms"][0]["importance"] in {"high", "medium", "low"}
    assert any(span["term"] == "altitude" for span in explanation["evidence_spans"])


def test_explanation_fallback_when_model_components_missing() -> None:
    bundle = LoadedModelBundle(
        domain_id="aviation",
        model=None,
        vectorizer=None,
        classifier=None,
        labels=["Anomaly_1"],
        available=True,
        artifact_status="available",
    )
    service = ExplanationService()
    text = "Crew reported conflicting altitude guidance."
    explanation = service.explain_label(text=text, label_index=0, bundle=bundle, top_n=3)

    assert explanation["explanation_method"] == "fallback_token_match"
    assert explanation["evidence_terms"]
    assert explanation["evidence_terms"][0]["importance"] == "low"


def test_explanation_ngram_span_fallback_to_component_token() -> None:
    service = ExplanationService()
    span = service._find_term_span(text="Crew received altitude guidance.", term="altitude conflict")
    assert span is not None
