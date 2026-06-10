from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.config import Settings
from app.services.bigquery_repository import BigQueryRepository
from app.services.mock_repository import MockRepository


@dataclass(frozen=True)
class RepositoryResult:
    records: list[dict[str, Any]]
    mode_used: str


class DataRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.mock = MockRepository()
        self.bigquery = BigQueryRepository(settings)

    def table(self, name: str) -> RepositoryResult:
        if self.settings.use_bigquery:
            try:
                return RepositoryResult(self.bigquery.table(name), "bigquery")
            except Exception:
                return RepositoryResult(self.mock.table(name), "mock")
        return RepositoryResult(self.mock.table(name), "mock")

    def first(self, name: str, **filters: Any) -> tuple[dict[str, Any] | None, str]:
        result = self.table(name)
        for record in result.records:
            if all(record.get(key) == value for key, value in filters.items()):
                return record, result.mode_used
        return None, result.mode_used

    @staticmethod
    def combine_modes(*modes: str) -> str:
        return "bigquery" if modes and all(mode == "bigquery" for mode in modes) else "mock"
