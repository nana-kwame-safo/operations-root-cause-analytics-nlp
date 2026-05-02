"""Single-text prediction service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from app.services.domain_registry import DomainRegistry
from app.services.explanation import ExplanationService
from app.services.label_registry import LabelRegistryService
from app.services.model_loader import LoadedModelBundle, ModelLoader


class DomainNotImplementedError(ValueError):
    """Raised when a requested domain is not implemented."""


class ModelUnavailableError(RuntimeError):
    """Raised when model artifacts are missing or failed to load."""


@dataclass
class Predictor:
    registry: DomainRegistry
    loader: ModelLoader
    explanation_service: ExplanationService
    label_registry: LabelRegistryService

    def predict(
        self,
        text: str,
        domain: str,
        threshold: float,
        top_k: int,
    ) -> dict[str, Any]:
        if not self.registry.is_implemented(domain):
            raise DomainNotImplementedError(f"Domain '{domain}' is not implemented.")

        bundle = self.loader.get_bundle(domain)
        if not bundle.available:
            raise ModelUnavailableError(bundle.error_message or "Model is unavailable.")

        scores = self._predict_scores(bundle, text)
        labels = self._resolve_labels(bundle, len(scores))

        ranked = sorted(
            (
                (idx, labels[idx], float(score))
                for idx, score in enumerate(scores)
            ),
            key=lambda item: item[2],
            reverse=True,
        )

        filtered = [item for item in ranked if item[2] >= threshold]
        filtered = filtered[:top_k]
        predicted_labels = [
            self._build_label_prediction(
                text=text,
                domain=domain,
                bundle=bundle,
                label_index=idx,
                label_id=label,
                score=score,
            )
            for idx, label, score in filtered
        ]

        all_scores = [
            self._build_score_entry(
                domain=domain,
                bundle=bundle,
                label_id=label,
                score=score,
            )
            for _, label, score in ranked
        ]
        top_scores = all_scores[:top_k]

        review_flag, message = self._review_message(ranked, filtered, threshold)
        top_prediction = predicted_labels[0] if predicted_labels else None
        explanation_method = (
            top_prediction.get("explanation_method")
            if top_prediction
            else "tfidf_linear_contribution"
        )
        return {
            "status": "ok",
            "input_text": text,
            "domain": domain,
            "model_info": {
                "model_name": bundle.metadata.get("model_name", "Unknown model"),
                "threshold_used": threshold,
                "artifact_status": bundle.artifact_status,
                "training_approach": bundle.metadata.get(
                    "training_approach",
                    "TF-IDF vectorization with One-vs-Rest Logistic Regression",
                ),
                "explanation_method": explanation_method,
            },
            "summary": {
                "predicted_count": len(predicted_labels),
                "top_label_id": top_prediction.get("label_id") if top_prediction else None,
                "top_label_name": top_prediction.get("label_name") if top_prediction else None,
                "top_score": top_prediction.get("score") if top_prediction else None,
                "top_score_percent": (
                    top_prediction.get("score_percent") if top_prediction else None
                ),
                "review_flag": review_flag,
                "review_message": message,
            },
            "predicted_labels": predicted_labels,
            "top_scores": top_scores,
            "all_scores": all_scores,
            "messages": [
                message,
                "Outputs are root-cause-related factor indicators for analyst review support.",
            ],
            "threshold_used": threshold,
            "review_flag": review_flag,
            "message": message,
        }

    @staticmethod
    def _predict_scores(bundle: LoadedModelBundle, text: str) -> np.ndarray:
        if bundle.vectorizer is not None and bundle.classifier is not None:
            matrix = bundle.vectorizer.transform([text])
            raw = bundle.classifier.predict_proba(matrix)
        elif bundle.model is not None and hasattr(bundle.model, "predict_proba"):
            raw = bundle.model.predict_proba([text])
        else:
            raise ModelUnavailableError("Loaded model does not support predict_proba.")

        scores = np.asarray(raw)
        if scores.ndim == 3:
            # Multi-output style: shape (n_labels, n_samples, n_classes)
            scores = np.asarray([label_scores[0, -1] for label_scores in scores])
        elif scores.ndim == 2:
            scores = scores[0]

        return scores.astype(float)

    @staticmethod
    def _resolve_labels(bundle: LoadedModelBundle, score_count: int) -> list[str]:
        if bundle.labels and len(bundle.labels) == score_count:
            return bundle.labels
        if bundle.labels and len(bundle.labels) > score_count:
            return bundle.labels[:score_count]
        generated = [f"Anomaly_{i}" for i in range(1, score_count + 1)]
        if bundle.labels:
            generated[: len(bundle.labels)] = bundle.labels
        return generated

    @staticmethod
    def _review_message(
        ranked: list[tuple[int, str, float]],
        filtered: list[tuple[int, str, float]],
        threshold: float,
    ) -> tuple[bool, str]:
        if not filtered:
            return True, "No strong factor prediction — analyst review recommended."

        top_score = filtered[0][2]
        second_score = filtered[1][2] if len(filtered) > 1 else 0.0
        narrow_margin = abs(top_score - second_score) < 0.08 if len(filtered) > 1 else False
        borderline_top = top_score < max(threshold + 0.1, 0.65)

        if narrow_margin or borderline_top:
            return True, "Low-confidence assessment — manual review advised."

        # If plenty of labels are near threshold, keep a cautionary flag.
        near_threshold_count = sum(1 for _, _, score in ranked if threshold <= score < threshold + 0.08)
        if near_threshold_count >= 3:
            return True, "Low-confidence assessment — manual review advised."

        return False, "Predictions generated successfully."

    def _build_label_prediction(
        self,
        *,
        text: str,
        domain: str,
        bundle: LoadedModelBundle,
        label_index: int,
        label_id: str,
        score: float,
    ) -> dict[str, Any]:
        metadata = self.label_registry.get_label_metadata(
            domain_id=domain,
            label_id=label_id,
            label_mapping=bundle.label_mapping,
        )
        explanation = self.explanation_service.explain_label(
            text=text,
            label_index=label_index,
            bundle=bundle,
            top_n=6,
        )
        score_value = round(float(score), 4)
        score_percent = round(score_value * 100, 2)
        return {
            "label": label_id,
            "label_id": label_id,
            "label_name": metadata["display_name"],
            "short_name": metadata["short_name"],
            "score": score_value,
            "score_percent": score_percent,
            "plain_language_description": metadata["plain_language_description"],
            "technical_description": metadata["technical_description"],
            "operational_interpretation": metadata["operational_interpretation"],
            "review_guidance": metadata["review_guidance"],
            "taxonomy_status": metadata["taxonomy_status"],
            "confidence_note": metadata["confidence_note"],
            "example_cues": metadata["example_cues"],
            "evidence_terms": explanation["evidence_terms"],
            "evidence_spans": explanation["evidence_spans"],
            "explanation_terms": explanation["explanation_terms"],
            "explanation_method": explanation["explanation_method"],
        }

    def _build_score_entry(
        self,
        *,
        domain: str,
        bundle: LoadedModelBundle,
        label_id: str,
        score: float,
    ) -> dict[str, Any]:
        metadata = self.label_registry.get_label_metadata(
            domain_id=domain,
            label_id=label_id,
            label_mapping=bundle.label_mapping,
        )
        score_value = round(float(score), 4)
        return {
            "label_id": label_id,
            "label_name": metadata["display_name"],
            "short_name": metadata["short_name"],
            "score": score_value,
            "score_percent": round(score_value * 100, 2),
        }
