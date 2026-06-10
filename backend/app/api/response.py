from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def envelope(
    data: Any = None,
    *,
    success: bool = True,
    error: str | None = None,
    data_mode_used: str = "mock",
) -> dict[str, Any]:
    return {
        "success": success,
        "data": data,
        "error": error,
        "data_mode_used": data_mode_used,
        "generated_at": now_iso(),
    }
