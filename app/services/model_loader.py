"""Model artifact loading for implemented domains."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib

from app.services.domain_registry import DomainRegistry


@dataclass
class LoadedModelBundle:
    domain_id: str
    model: Any | None
    vectorizer: Any | None
    classifier: Any | None
    labels: list[str] = field(default_factory=list)
    label_mapping: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    available: bool = False
    artifact_status: str = "missing"
    error_message: str | None = None
    model_path: Path | None = None


class ModelLoader:
    """Loads model + metadata artifacts and keeps an in-memory cache per domain."""

    def __init__(self, registry: DomainRegistry, artifacts_root: Path, domains_root: Path) -> None:
        self.registry = registry
        self.artifacts_root = artifacts_root
        self.domains_root = domains_root
        self._cache: dict[str, LoadedModelBundle] = {}

    def get_bundle(self, domain_id: str) -> LoadedModelBundle:
        if domain_id not in self._cache:
            self._cache[domain_id] = self._load_bundle(domain_id)
        return self._cache[domain_id]

    def _load_bundle(self, domain_id: str) -> LoadedModelBundle:
        domain_cfg = self.registry.get_config(domain_id).raw
        artifact_dir = self.artifacts_root / domain_cfg.get("artifact_subdir", domain_id)
        domain_dir = self.domains_root / domain_id

        metadata = self._load_json_with_fallback(
            artifact_dir / domain_cfg.get("metadata_file", "metadata.json"),
            domain_dir / domain_cfg.get("metadata_example_file", "metadata.example.json"),
        )

        label_mapping = self._load_json_with_fallback(
            artifact_dir / domain_cfg.get("label_mapping_file", "label_mapping.json"),
            domain_dir / domain_cfg.get("label_mapping_file", "label_mapping.json"),
        )

        labels = self._extract_labels(domain_cfg, metadata, label_mapping)
        model_path = artifact_dir / domain_cfg.get("model_artifact", "model.joblib")

        if not model_path.exists():
            return LoadedModelBundle(
                domain_id=domain_id,
                model=None,
                vectorizer=None,
                classifier=None,
                labels=labels,
                label_mapping=label_mapping,
                metadata=metadata,
                available=False,
                artifact_status="missing",
                error_message=(
                    f"Model artifact not found at {model_path}. "
                    "Generate artifacts locally before calling prediction endpoints."
                ),
                model_path=model_path,
            )

        try:
            payload = joblib.load(model_path)
        except Exception as exc:  # pragma: no cover - defensive
            return LoadedModelBundle(
                domain_id=domain_id,
                model=None,
                vectorizer=None,
                classifier=None,
                labels=labels,
                label_mapping=label_mapping,
                metadata=metadata,
                available=False,
                artifact_status="error",
                error_message=f"Failed to load model artifact: {exc}",
                model_path=model_path,
            )

        model, vectorizer, classifier, model_labels, payload_metadata = self._unpack_payload(payload)
        merged_metadata = {**metadata, **payload_metadata}
        final_labels = model_labels or labels

        if model is None and classifier is None:
            return LoadedModelBundle(
                domain_id=domain_id,
                model=None,
                vectorizer=vectorizer,
                classifier=classifier,
                labels=final_labels,
                label_mapping=label_mapping,
                metadata=merged_metadata,
                available=False,
                artifact_status="error",
                error_message="Loaded artifact does not expose a prediction interface.",
                model_path=model_path,
            )

        return LoadedModelBundle(
            domain_id=domain_id,
            model=model,
            vectorizer=vectorizer,
            classifier=classifier,
            labels=final_labels,
            label_mapping=label_mapping,
            metadata=merged_metadata,
            available=True,
            artifact_status="loaded",
            model_path=model_path,
        )

    @staticmethod
    def _load_json_with_fallback(primary: Path, fallback: Path) -> dict[str, Any]:
        for path in (primary, fallback):
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        return {}

    @staticmethod
    def _extract_labels(
        domain_cfg: dict[str, Any],
        metadata: dict[str, Any],
        label_mapping: dict[str, Any],
    ) -> list[str]:
        if isinstance(metadata.get("labels"), list):
            return [str(x) for x in metadata["labels"]]
        if label_mapping:
            return list(label_mapping.keys())

        label_count = int(domain_cfg.get("label_count", 0))
        if label_count > 0:
            return [f"Anomaly_{i}" for i in range(1, label_count + 1)]
        return []

    @staticmethod
    def _unpack_payload(
        payload: Any,
    ) -> tuple[Any | None, Any | None, Any | None, list[str], dict[str, Any]]:
        model: Any | None = None
        vectorizer: Any | None = None
        classifier: Any | None = None
        labels: list[str] = []
        metadata: dict[str, Any] = {}

        if isinstance(payload, dict):
            model = payload.get("model")
            vectorizer = payload.get("vectorizer")
            classifier = payload.get("classifier")
            labels = payload.get("labels", []) or []
            metadata = payload.get("metadata", {}) or {}

            if model is None and vectorizer is not None and classifier is not None:
                model = payload

            if model is not None:
                extracted_vectorizer, extracted_classifier = ModelLoader._extract_components(model)
                vectorizer = vectorizer or extracted_vectorizer
                classifier = classifier or extracted_classifier

        else:
            model = payload
            vectorizer, classifier = ModelLoader._extract_components(model)

        if model is None and classifier is not None:
            model = classifier

        return model, vectorizer, classifier, labels, metadata

    @staticmethod
    def _extract_components(model: Any) -> tuple[Any | None, Any | None]:
        # Pipeline-like object with named steps.
        if hasattr(model, "named_steps"):
            vectorizer = None
            classifier = None
            for step in model.named_steps.values():
                if vectorizer is None and hasattr(step, "transform") and hasattr(
                    step,
                    "get_feature_names_out",
                ):
                    vectorizer = step
                if classifier is None and hasattr(step, "predict_proba"):
                    classifier = step

            if classifier is None:
                # Fallback to final pipeline step if available.
                steps = list(model.named_steps.values())
                if steps:
                    last = steps[-1]
                    if hasattr(last, "predict_proba"):
                        classifier = last

            return vectorizer, classifier

        # Dict payload carrying direct components.
        if hasattr(model, "predict_proba"):
            return None, model

        return None, None
