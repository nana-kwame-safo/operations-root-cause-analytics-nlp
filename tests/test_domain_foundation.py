from __future__ import annotations

import json
from pathlib import Path

from app.core.config import get_settings
from app.services.domain_registry import DomainRegistry


def test_domain_template_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "app/domains/_template/domain_config.example.json",
        root / "app/domains/_template/label_mapping.example.json",
        root / "app/domains/_template/metadata.example.json",
        root / "artifacts/_template/README.md",
        root / "artifacts/_template/metadata.example.json",
    ]
    for path in required:
        assert path.exists(), f"Missing template file: {path}"


def test_template_domain_is_not_registered() -> None:
    registry = DomainRegistry(get_settings().domains_root)
    domain_ids = {entry["domain_id"] for entry in registry.list_domains()}
    assert "_template" not in domain_ids
    assert "aviation" in domain_ids


def test_template_domain_config_has_required_keys() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads(
        (root / "app/domains/_template/domain_config.example.json").read_text(
            encoding="utf-8"
        )
    )
    required = {
        "domain_id",
        "display_name",
        "artifact_subdir",
        "model_artifact",
        "metadata_file",
        "label_mapping_file",
        "default_threshold",
        "default_top_k",
        "limitation_note",
        "responsible_use_note",
    }
    assert required.issubset(payload.keys())
