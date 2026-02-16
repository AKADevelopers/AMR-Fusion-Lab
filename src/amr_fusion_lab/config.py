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
