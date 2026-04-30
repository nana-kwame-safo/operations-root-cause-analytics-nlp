"""Explainability-lite utilities based on TF-IDF and linear coefficients."""

from __future__ import annotations

import re
from typing import Any

import numpy as np

from app.services.model_loader import LoadedModelBundle

TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")


class ExplanationService:
    """Generates lightweight explanation cues for predicted labels."""

    def explanation_terms(
        self,
        text: str,
        label_index: int,
        bundle: LoadedModelBundle,
        top_n: int = 3,
    ) -> list[str]:
        terms = self._coefficient_terms(text, label_index, bundle, top_n)
        if terms:
            return terms
        return self._fallback_terms(text, top_n)

    def _coefficient_terms(
        self,
        text: str,
        label_index: int,
        bundle: LoadedModelBundle,
        top_n: int,
    ) -> list[str]:
        vectorizer = bundle.vectorizer
        classifier = bundle.classifier
        if vectorizer is None or classifier is None:
            return []

        if not hasattr(vectorizer, "transform") or not hasattr(vectorizer, "get_feature_names_out"):
            return []
        if not hasattr(classifier, "estimators_"):
            return []
        if label_index >= len(classifier.estimators_):
            return []

        estimator = classifier.estimators_[label_index]
        if not hasattr(estimator, "coef_"):
            return []

        row = vectorizer.transform([text])
        if row.shape[1] == 0 or row.nnz == 0:
            return []

        coef = np.asarray(estimator.coef_[0])
        indices = row.indices
        values = row.data
        contributions = values * coef[indices]

        feature_names = vectorizer.get_feature_names_out()
        ranked = sorted(
            (
                (int(idx), float(score))
                for idx, score in zip(indices, contributions, strict=False)
                if score > 0
            ),
            key=lambda item: item[1],
            reverse=True,
        )
        selected = [feature_names[idx] for idx, _ in ranked[:top_n]]
        return selected

    @staticmethod
    def _fallback_terms(text: str, top_n: int) -> list[str]:
        seen: set[str] = set()
        terms: list[str] = []
        for match in TOKEN_PATTERN.finditer(text.lower()):
            token = match.group(0)
            if token in seen:
                continue
            seen.add(token)
            terms.append(token)
            if len(terms) >= top_n:
                break
        return terms
