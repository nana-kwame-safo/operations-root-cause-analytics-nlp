"""Utility helpers for optional external model artifact loading."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from urllib.request import urlopen

logger = logging.getLogger(__name__)


def ensure_model_artifact(
    *,
    artifact_path: Path,
    artifact_url: str | None,
    timeout_seconds: int = 120,
) -> tuple[bool, str | None]:
    """Ensure the model artifact exists locally, optionally downloading it.

    Returns:
        (is_available, error_message)
    """
    if artifact_path.exists():
        logger.info("Model artifact already available at %s", artifact_path)
        return True, None

    if not artifact_url:
        return False, None

    try:
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(
            "Downloading model artifact from external URL to %s using MODEL_ARTIFACT_URL",
            artifact_path,
        )
        with urlopen(artifact_url, timeout=timeout_seconds) as src, artifact_path.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        logger.info("Model artifact download succeeded: %s", artifact_path)
        return True, None
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Model artifact download failed for %s: %s", artifact_path, exc)
        try:
            artifact_path.unlink(missing_ok=True)
        except OSError:
            pass
        return False, f"Model artifact download failed from MODEL_ARTIFACT_URL: {exc}"
