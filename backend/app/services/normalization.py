from __future__ import annotations

import re


RESOURCE_ALIASES = {
    "burn kit": "Burn kits",
    "burn kits": "Burn kits",
    "item-burn-kit": "Burn kits",
    "albuterol": "Albuterol doses",
    "albuterol dose": "Albuterol doses",
    "albuterol doses": "Albuterol doses",
    "item-albuterol": "Albuterol doses",
    "oxygen": "Oxygen cylinders",
    "oxygen cylinder": "Oxygen cylinders",
    "oxygen cylinders": "Oxygen cylinders",
    "item-oxygen-cyl": "Oxygen cylinders",
    "icu": "ICU beds",
    "icu bed": "ICU beds",
    "icu beds": "ICU beds",
    "nurse": "ER nurses",
    "er nurse": "ER nurses",
    "er nurses": "ER nurses",
}


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def normalize_resource(value: str) -> str:
    normalized = normalize_key(value)
    return RESOURCE_ALIASES.get(normalized, value)
