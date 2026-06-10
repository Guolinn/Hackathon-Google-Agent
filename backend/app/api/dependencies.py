from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.services.data_repository import DataRepository


@lru_cache(maxsize=1)
def get_repository() -> DataRepository:
    return DataRepository(get_settings())
