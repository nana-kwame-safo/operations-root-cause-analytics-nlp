from __future__ import annotations

from app.api.routes import domains
from app.core.config import get_settings
from app.services.domain_registry import DomainRegistry


def test_domains_endpoint():
    registry = DomainRegistry(get_settings().domains_root)
    payload = domains(registry)
    assert "available_domains" in payload
    domain_list = payload["available_domains"]
    aviation = [d for d in domain_list if d["domain_id"] == "aviation"]
    assert aviation
    assert aviation[0]["status"] == "implemented"
