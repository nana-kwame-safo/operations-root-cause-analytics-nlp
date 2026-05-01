"""Runtime configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.constants import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_DOMAIN,
    DEFAULT_THRESHOLD,
    DEFAULT_TOP_K,
)

BASE_DIR = Path(__file__).resolve().parents[2]


def _resolve_path(raw: str, base_dir: Path) -> Path:
    candidate = Path(raw)
    return candidate if candidate.is_absolute() else (base_dir / candidate).resolve()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    app_name: str
    app_version: str
    active_domain: str
    default_threshold: float
    default_top_k: int
    artifacts_root: Path
    domains_root: Path
    model_artifact_url: str | None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", APP_NAME),
        app_version=os.getenv("APP_VERSION", APP_VERSION),
        active_domain=os.getenv("ACTIVE_DOMAIN", DEFAULT_DOMAIN),
        default_threshold=float(os.getenv("DEFAULT_THRESHOLD", str(DEFAULT_THRESHOLD))),
        default_top_k=int(os.getenv("DEFAULT_TOP_K", str(DEFAULT_TOP_K))),
        artifacts_root=_resolve_path(
            os.getenv("ARTIFACTS_ROOT", "artifacts"),
            BASE_DIR,
        ),
        domains_root=_resolve_path(
            os.getenv("DOMAINS_ROOT", "app/domains"),
            BASE_DIR,
        ),
        model_artifact_url=os.getenv("MODEL_ARTIFACT_URL"),
    )
