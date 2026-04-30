from __future__ import annotations

from app.api.routes import health
from app.core.config import get_settings

def test_health_endpoint():
    payload = health(get_settings())
    assert payload["status"] == "ok"
    assert payload["app_name"] == "Operations RCA NLP"
    assert payload["active_domain"] == "aviation"
    assert "version" in payload
