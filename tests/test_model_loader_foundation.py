from __future__ import annotations

import json
from pathlib import Path

from app.services.domain_registry import DomainRegistry
from app.services.model_loader import ModelLoader


def _write_demo_domain(domains_root: Path) -> None:
    domain_dir = domains_root / "demo_ops"
    domain_dir.mkdir(parents=True, exist_ok=True)
    (domain_dir / "domain_config.json").write_text(
        json.dumps(
            {
                "domain_id": "demo_ops",
                "display_name": "Demo Ops",
                "status": "implemented",
                "description": "Demo domain for model loader tests.",
                "artifact_subdir": "demo_ops",
                "model_artifact": "model.joblib",
                "metadata_file": "metadata.json",
                "metadata_example_file": "metadata.example.json",
                "label_mapping_file": "label_mapping.json",
                "default_threshold": 0.5,
                "default_top_k": 5,
                "label_count": 2,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (domain_dir / "metadata.example.json").write_text(
        json.dumps(
            {
                "domain_id": "demo_ops",
                "domain": "demo_ops",
                "model_name": "TF-IDF + One-vs-Rest Logistic Regression",
                "model_type": "multi-label classification",
                "training_approach": "TF-IDF vectorization with One-vs-Rest Logistic Regression",
                "training_date": "YYYY-MM-DD",
                "threshold": 0.5,
                "threshold_default": 0.5,
                "label_count": 2,
                "labels": ["Anomaly_1", "Anomaly_2"],
                "evaluation_metrics": {
                    "micro_f1": 0.0,
                    "macro_f1": 0.0,
                    "samples_f1": 0.0,
                    "hamming_loss": 0.0,
                },
                "dataset_provenance_note": "Local-only demo snapshot.",
                "limitation_note": "Indicators only.",
                "responsible_use_note": "Human review required.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (domain_dir / "label_mapping.json").write_text(
        json.dumps(
            {
                "Anomaly_1": {"display_name": "Anomaly 1"},
                "Anomaly_2": {"display_name": "Anomaly 2"},
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_model_loader_uses_metadata_fallback_when_artifact_missing(tmp_path: Path) -> None:
    domains_root = tmp_path / "domains"
    artifacts_root = tmp_path / "artifacts"
    _write_demo_domain(domains_root)

    registry = DomainRegistry(domains_root)
    loader = ModelLoader(registry=registry, artifacts_root=artifacts_root, domains_root=domains_root)
    bundle = loader.get_bundle("demo_ops")

    assert bundle.available is False
    assert bundle.artifact_status == "missing"
    assert bundle.metadata["domain"] == "demo_ops"
    assert bundle.metadata["responsible_use_note"] == "Human review required."
    assert bundle.labels == ["Anomaly_1", "Anomaly_2"]
    assert bundle.error_message is not None
    assert "Generate artifacts locally" in bundle.error_message


def test_aviation_metadata_example_contains_required_fields() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads(
        (root / "app/domains/aviation/metadata.example.json").read_text(encoding="utf-8")
    )
    required = {
        "model_name",
        "model_type",
        "domain",
        "label_count",
        "threshold",
        "training_date",
        "training_approach",
        "evaluation_metrics",
        "dataset_provenance_note",
        "limitation_note",
        "responsible_use_note",
    }
    assert required.issubset(payload.keys())
