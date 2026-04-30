"""Domain discovery and registry."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.constants import DOMAIN_PLACEHOLDERS


@dataclass(frozen=True)
class DomainConfig:
    domain_id: str
    display_name: str
    status: str
    description: str
    raw: dict[str, Any]


class DomainRegistry:
    """Loads implemented domains from config files and exposes planned placeholders."""

    def __init__(self, domains_root: Path) -> None:
        self.domains_root = domains_root
        self._implemented: dict[str, DomainConfig] = {}
        self._load_implemented_domains()

    def _load_implemented_domains(self) -> None:
        if not self.domains_root.exists():
            return

        for config_path in sorted(self.domains_root.glob("*/domain_config.json")):
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            domain = DomainConfig(
                domain_id=payload["domain_id"],
                display_name=payload["display_name"],
                status=payload.get("status", "implemented"),
                description=payload.get("description", ""),
                raw=payload,
            )
            self._implemented[domain.domain_id] = domain

    def list_domains(self) -> list[dict[str, str]]:
        domains = [
            {
                "domain_id": d.domain_id,
                "display_name": d.display_name,
                "status": d.status,
                "description": d.description,
            }
            for d in self._implemented.values()
        ]
        domains.extend(DOMAIN_PLACEHOLDERS)
        return domains

    def get_config(self, domain_id: str) -> DomainConfig:
        if domain_id not in self._implemented:
            raise KeyError(f"Domain '{domain_id}' is not implemented.")
        return self._implemented[domain_id]

    def is_implemented(self, domain_id: str) -> bool:
        return domain_id in self._implemented

    @property
    def implemented_domains(self) -> list[str]:
        return sorted(self._implemented.keys())
