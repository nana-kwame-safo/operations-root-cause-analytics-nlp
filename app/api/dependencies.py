"""Dependency providers for FastAPI routes."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.batch_predictor import BatchPredictor
from app.services.domain_registry import DomainRegistry
from app.services.explanation import ExplanationService
from app.services.model_loader import ModelLoader
from app.services.predictor import Predictor


@lru_cache(maxsize=1)
def get_domain_registry() -> DomainRegistry:
    settings = get_settings()
    return DomainRegistry(settings.domains_root)


@lru_cache(maxsize=1)
def get_model_loader() -> ModelLoader:
    settings = get_settings()
    registry = get_domain_registry()
    return ModelLoader(
        registry=registry,
        artifacts_root=settings.artifacts_root,
        domains_root=settings.domains_root,
        model_artifact_url=settings.model_artifact_url,
    )


@lru_cache(maxsize=1)
def get_explanation_service() -> ExplanationService:
    return ExplanationService()


@lru_cache(maxsize=1)
def get_predictor() -> Predictor:
    return Predictor(
        registry=get_domain_registry(),
        loader=get_model_loader(),
        explanation_service=get_explanation_service(),
    )


@lru_cache(maxsize=1)
def get_batch_predictor() -> BatchPredictor:
    return BatchPredictor(predictor=get_predictor())


def settings_dependency() -> Settings:
    return get_settings()
