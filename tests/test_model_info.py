from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api.routes import model_info
from app.core.config import get_settings
from app.services.domain_registry import DomainRegistry
from app.services.model_loader import ModelLoader


def test_model_info_endpoint():
    settings = get_settings()
    registry = DomainRegistry(settings.domains_root)
    loader = ModelLoader(registry, settings.artifacts_root, settings.domains_root)
    payload = model_info(None, settings, registry, loader).model_dump()

    assert payload["active_domain"] == "aviation"
    assert payload["model_name"] == "TF-IDF + One-vs-Rest Logistic Regression"
    assert payload["label_count"] == 22
    assert payload["threshold"] == 0.5
    micro_f1 = payload["evaluation_metrics"]["micro_f1"]
    assert micro_f1 is not None
    assert 0.0 <= micro_f1 <= 1.0
    if payload["artifact_status"] == "missing":
        # Falls back to metadata.example.json values when model artifact is absent.
        assert micro_f1 == 0.658
    assert payload["artifact_status"] in {"missing", "available"}


def test_model_info_unknown_domain_returns_404():
    settings = get_settings()
    registry = DomainRegistry(settings.domains_root)
    loader = ModelLoader(registry, settings.artifacts_root, settings.domains_root)
    with pytest.raises(HTTPException) as exc:
        model_info("unknown_domain", settings, registry, loader)
    assert exc.value.status_code == 404
