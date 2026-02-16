from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


def load_config(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: {path}")

    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError("Config must be a YAML object")

    required = ["sample_id", "outdir"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ConfigError(f"Missing required config keys: {missing}")

    return data


def write_default_config(path: str, force: bool = False) -> Path:
    p = Path(path)
    if p.exists() and not force:
        raise ConfigError(f"Config file already exists: {path}. Use --force to overwrite.")

    p.parent.mkdir(parents=True, exist_ok=True)

    template = {
        "sample_id": "SAMPLE_001",
        "outdir": "outputs/SAMPLE_001",
        "resfinder": "examples/resfinder_sample.tsv",
        "amrfinder": "examples/amrfinder_sample.tsv",
        "rgi": "examples/rgi_sample.tsv",
        "min_identity": 90,
        "min_coverage": 70,
        "deduplicate": True,
        "strict_validation": False,
        "ai_enable": False,
        "ai_provider": "openai_compatible",
        "ai_model": "gpt-4o-mini",
    }

    p.write_text(yaml.safe_dump(template, sort_keys=False), encoding="utf-8")
    return p
