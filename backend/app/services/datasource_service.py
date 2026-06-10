from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app.config import Settings
from app.services.data_repository import DataRepository


class DatasourceService:
    def __init__(self, repository: DataRepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    def get_data_sources(self) -> tuple[dict[str, Any], str]:
        if self.settings.use_fivetran:
            try:
                connectors = self._fetch_fivetran_connectors()
                if connectors:
                    return {
                        "integration_mode": "fivetran_rest",
                        "sources": connectors,
                    }, "bigquery" if self.settings.use_bigquery else "mock"
            except Exception:
                pass

        result = self.repository.table("datasource_status")
        return {
            "integration_mode": "mock_fivetran_status",
            "sources": result.records,
            "agent_note": (
                "Fivetran-style connector freshness is simulated for the hackathon demo. "
                "Production would query Fivetran MCP or REST sync history."
            ),
        }, result.mode_used

    def _fetch_fivetran_connectors(self) -> list[dict[str, Any]]:
        token = f"{self.settings.fivetran_api_key}:{self.settings.fivetran_api_secret}".encode("utf-8")
        auth = base64.b64encode(token).decode("ascii")

        # Fivetran has renamed "connectors" to "connections" in newer API surfaces.
        # Try the current resource first, then fall back to the older one so the
        # hackathon demo is not brittle across account/API versions.
        last_error: Exception | None = None
        for resource in ("connections", "connectors"):
            try:
                items = self._request_fivetran_items(resource, auth)
                return [self._normalize_fivetran_connection(item) for item in items[:8]]
            except HTTPError as exc:
                if exc.code in {401, 403}:
                    raise
                last_error = exc

        if last_error:
            raise last_error
        return []

    def _request_fivetran_items(self, resource: str, auth: str) -> list[dict[str, Any]]:
        request = Request(
            f"https://api.fivetran.com/v1/{resource}?limit=20",
            headers={"Authorization": f"Basic {auth}", "Accept": "application/json"},
        )
        with urlopen(request, timeout=4) as response:
            payload = json.loads(response.read().decode("utf-8"))
        data = payload.get("data", {})
        items = data.get("items", []) if isinstance(data, dict) else data
        return items if isinstance(items, list) else []

    def _normalize_fivetran_connection(self, connection: dict[str, Any]) -> dict[str, Any]:
        status_payload = connection.get("status", {})
        status_payload = status_payload if isinstance(status_payload, dict) else {}

        sync_state = status_payload.get("sync_state") or status_payload.get("setup_state")
        paused = bool(connection.get("paused"))
        source_name = connection.get("service") or connection.get("schema") or "Fivetran connection"
        last_sync_at = (
            connection.get("succeeded_at")
            or connection.get("last_successful_sync")
            or status_payload.get("last_successful_sync")
        )

        return {
            "source_name": source_name,
            "connector_id": connection.get("id"),
            "service": connection.get("service"),
            "last_sync_minutes": self._minutes_since(last_sync_at),
            "status": self._display_status(sync_state, paused),
            "setup_state": status_payload.get("setup_state"),
            "sync_state": status_payload.get("sync_state"),
            "records_loaded": None,
            "used_by_agent": True,
            "raw_sync_state": sync_state or "unknown",
        }

    def _display_status(self, sync_state: str | None, paused: bool) -> str:
        if paused:
            return "Paused"
        state = (sync_state or "").lower()
        if state in {"syncing", "rescheduled"}:
            return "Syncing"
        if state in {"scheduled", "connected", "succeeded"}:
            return "Fresh"
        if state in {"paused"}:
            return "Paused"
        if state in {"broken", "failed", "incomplete"}:
            return "Warning"
        return sync_state or "Unknown"

    def _minutes_since(self, value: str | None) -> int | None:
        if not value:
            return None
        try:
            timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        delta = datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)
        return max(0, int(delta.total_seconds() // 60))
