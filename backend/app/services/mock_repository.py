from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


class MockRepository:
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or Path(__file__).resolve().parents[1] / "data"

    def table(self, name: str) -> list[dict[str, Any]]:
        return list(self._load_table(str(self.data_dir), name))

    @staticmethod
    @lru_cache(maxsize=64)
    def _load_table(data_dir: str, name: str) -> tuple[dict[str, Any], ...]:
        path = Path(data_dir) / f"{name}.json"
        if not path.exists():
            return tuple()
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, list):
            raise ValueError(f"Mock table {name} must contain a JSON array")
        return tuple(payload)
