"""Helpers for human-readable label metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class LabelRegistryService:
    """Loads per-domain label metadata for analyst-facing explanations."""

    def __init__(self, domains_root: Path) -> None:
        self.domains_root = domains_root
        self._cache: dict[str, dict[str, dict[str, Any]]] = {}

    def get_label_metadata(
        self,
        *,
        domain_id: str,
        label_id: str,
        label_mapping: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        registry = self._load_registry(domain_id)
        record = registry.get(label_id, {})
        mapped = (label_mapping or {}).get(label_id, {})

        display_name = (
            str(record.get("display_name") or "").strip()
            or str(mapped.get("display_name") or "").strip()
            or label_id
        )
        short_name = str(record.get("short_name") or "").strip() or display_name

        plain_description = (
            str(record.get("plain_language_description") or "").strip()
            or str(mapped.get("description") or "").strip()
            or f"{display_name} indicator from model output."
        )
        technical_description = (
            str(record.get("technical_description") or "").strip()
            or "Model-derived indicator from TF-IDF + One-vs-Rest Logistic Regression features."
        )
        operational_interpretation = (
            str(record.get("operational_interpretation") or "").strip()
            or "Treat this as a contributory-factor indicator for analyst review support."
        )
        review_guidance = (
            str(record.get("review_guidance") or "").strip()
            or "Validate this indicator with supporting operational evidence."
        )
        example_cues = record.get("example_cues")
        if not isinstance(example_cues, list):
            example_cues = []

        return {
            "label_id": label_id,
            "display_name": display_name,
            "short_name": short_name,
            "plain_language_description": plain_description,
            "technical_description": technical_description,
            "operational_interpretation": operational_interpretation,
            "review_guidance": review_guidance,
            "example_cues": [str(item) for item in example_cues][:8],
            "taxonomy_status": record.get("taxonomy_status", "fallback"),
            "confidence_note": (
                str(record.get("confidence_note") or "").strip()
                or "Confidence is probabilistic and requires analyst validation."
            ),
        }

    def _load_registry(self, domain_id: str) -> dict[str, dict[str, Any]]:
        cached = self._cache.get(domain_id)
        if cached is not None:
            return cached

        path = self.domains_root / domain_id / "label_registry.json"
        if not path.exists():
            self._cache[domain_id] = {}
            return {}

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self._cache[domain_id] = {}
            return {}

        registry: dict[str, dict[str, Any]] = {}
        if isinstance(payload, dict):
            for label_id, data in payload.items():
                if isinstance(data, dict):
                    registry[str(label_id)] = data
        self._cache[domain_id] = registry
        return registry
