from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any


@dataclass
class RuntimeStore:
    plans: dict[str, dict[str, Any]] = field(default_factory=dict)
    approvals: dict[str, dict[str, Any]] = field(default_factory=dict)
    dispatch_requests: dict[str, dict[str, Any]] = field(default_factory=dict)


@lru_cache(maxsize=1)
def get_store() -> RuntimeStore:
    return RuntimeStore()
