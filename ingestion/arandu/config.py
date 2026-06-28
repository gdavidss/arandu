from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def config_path() -> Path:
    return Path(os.environ.get("SERIES_CONFIG", "/app/config/series.yml"))


def load_config(path: Path | None = None) -> dict[str, Any]:
    target = path or config_path()
    with target.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Config {target} did not parse as a mapping")
    data.setdefault("sources", {})
    data.setdefault("series", [])
    return data
