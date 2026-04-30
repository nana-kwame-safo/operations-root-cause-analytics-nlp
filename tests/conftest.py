from __future__ import annotations

import pytest

from app.api.dependencies import (
    get_batch_predictor,
    get_domain_registry,
    get_explanation_service,
    get_model_loader,
    get_predictor,
)
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def clear_caches() -> None:
    get_settings.cache_clear()
    get_domain_registry.cache_clear()
    get_model_loader.cache_clear()
    get_explanation_service.cache_clear()
    get_predictor.cache_clear()
    get_batch_predictor.cache_clear()
