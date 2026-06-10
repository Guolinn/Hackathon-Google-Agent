from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()


def _csv_env(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [part.strip() for part in value.split(",") if part.strip()]


@dataclass(frozen=True)
class Settings:
    data_mode: str = os.getenv("DATA_MODE", "mock").lower()
    google_cloud_project: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "crisisflow_demo")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    fivetran_api_key: str | None = os.getenv("FIVETRAN_API_KEY")
    fivetran_api_secret: str | None = os.getenv("FIVETRAN_API_SECRET")
    cors_origins: tuple[str, ...] = tuple(
        _csv_env(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173",
        )
    )

    @property
    def use_bigquery(self) -> bool:
        return self.data_mode == "bigquery" and bool(self.google_cloud_project)

    @property
    def use_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def use_fivetran(self) -> bool:
        return bool(self.fivetran_api_key and self.fivetran_api_secret)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
