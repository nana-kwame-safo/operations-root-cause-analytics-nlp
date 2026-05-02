"""Explainability utilities based on TF-IDF and linear coefficients."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import numpy as np

from app.services.model_loader import LoadedModelBundle

TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]{2,}")


@dataclass(frozen=True)
class EvidenceTerm:
    term: str
    display_term: str
    contribution: float
    importance: str


@dataclass(frozen=True)
class EvidenceSpan:
    term: str
    start: int
    end: int
    importance: str


class ExplanationService:
    """Generates explanation cues and evidence terms for predicted labels."""

    def explain_label(
        self,
        *,
        text: str,
        label_index: int,
        bundle: LoadedModelBundle,
        top_n: int = 6,
    ) -> dict[str, Any]:
        coefficient_terms = self._coefficient_terms(
            text=text,
            label_index=label_index,
            bundle=bundle,
            top_n=top_n,
        )
        if coefficient_terms:
            method = "tfidf_linear_contribution"
            evidence_terms = coefficient_terms
        else:
            method = "fallback_token_match"
            evidence_terms = self._fallback_terms(text=text, top_n=top_n)

        spans = self._match_spans(text=text, terms=evidence_terms)
        return {
            "explanation_method": method,
            "evidence_terms": [term.__dict__ for term in evidence_terms],
            "evidence_spans": [span.__dict__ for span in spans],
            "explanation_terms": [term.display_term for term in evidence_terms],
        }

    def explanation_terms(
        self,
        text: str,
        label_index: int,
        bundle: LoadedModelBundle,
        top_n: int = 3,
    ) -> list[str]:
        explanation = self.explain_label(
            text=text,
            label_index=label_index,
            bundle=bundle,
            top_n=top_n,
        )
        return explanation["explanation_terms"]

    def _coefficient_terms(
        self,
        text: str,
        label_index: int,
        bundle: LoadedModelBundle,
        top_n: int,
    ) -> list[EvidenceTerm]:
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
        ranked_raw = [
            (int(idx), float(score))
            for idx, score in zip(indices, contributions, strict=False)
            if score > 0
        ]
        if not ranked_raw:
            return []

        ranked_raw.sort(key=lambda item: item[1], reverse=True)
        top_items = ranked_raw[:top_n]
        max_score = top_items[0][1] if top_items else 0.0
        if max_score <= 0:
            return []

        evidence: list[EvidenceTerm] = []
        for idx, score in top_items:
            importance = self._importance_level(score=score, max_score=max_score)
            raw_term = str(feature_names[idx])
            evidence.append(
                EvidenceTerm(
                    term=raw_term,
                    display_term=raw_term.replace("_", " "),
                    contribution=round(score, 6),
                    importance=importance,
                )
            )
        return evidence

    @staticmethod
    def _fallback_terms(text: str, top_n: int) -> list[EvidenceTerm]:
        seen: set[str] = set()
        terms: list[EvidenceTerm] = []
        for match in TOKEN_PATTERN.finditer(text.lower()):
            token = match.group(0)
            if token in seen:
                continue
            seen.add(token)
            terms.append(
                EvidenceTerm(
                    term=token,
                    display_term=token,
                    contribution=0.0,
                    importance="low",
                )
            )
            if len(terms) >= top_n:
                break
        return terms

    @staticmethod
    def _importance_level(*, score: float, max_score: float) -> str:
        if max_score <= 0:
            return "low"
        ratio = score / max_score
        if ratio >= 0.67:
            return "high"
        if ratio >= 0.34:
            return "medium"
        return "low"

    def _match_spans(self, *, text: str, terms: list[EvidenceTerm]) -> list[EvidenceSpan]:
        spans: list[EvidenceSpan] = []
        for evidence in terms:
            match = self._find_term_span(text=text, term=evidence.term)
            if match is None:
                continue
            start, end = match
            spans.append(
                EvidenceSpan(
                    term=evidence.display_term,
                    start=start,
                    end=end,
                    importance=evidence.importance,
                )
            )
        return spans

    @staticmethod
    def _find_term_span(*, text: str, term: str) -> tuple[int, int] | None:
        escaped = re.escape(term)
        match = re.search(escaped, text, flags=re.IGNORECASE)
        if match:
            return match.start(), match.end()

        if " " in term:
            # N-gram features are not always contiguous in raw text.
            parts = [part for part in term.split() if len(part) > 2]
            parts.sort(key=len, reverse=True)
            for part in parts:
                alt = re.search(re.escape(part), text, flags=re.IGNORECASE)
                if alt:
                    return alt.start(), alt.end()

        return None
