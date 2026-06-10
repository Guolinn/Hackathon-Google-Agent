from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from app.config import Settings


class BigQueryRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None

    def table(self, name: str) -> list[dict[str, Any]]:
        if not self.settings.google_cloud_project:
            raise RuntimeError("GOOGLE_CLOUD_PROJECT is not configured")
        client = self._get_client()
        table_id = f"`{self.settings.google_cloud_project}.{self.settings.bigquery_dataset}.{name}`"
        query = f"SELECT * FROM {table_id}"
        return [self._json_safe(dict(row)) for row in client.query(query).result()]

    def _json_safe(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._json_safe(item) for item in value]
        if isinstance(value, (datetime, date, time)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return int(value) if value == value.to_integral_value() else float(value)
        return value

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from google.cloud import bigquery
        except Exception as exc:
            raise RuntimeError("google-cloud-bigquery is not installed") from exc
        self._client = bigquery.Client(project=self.settings.google_cloud_project)
        return self._client
