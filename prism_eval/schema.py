"""Schema hash lock verification for ParameterManifest payloads."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

SCHEMA_VERSION = "2.2.0"


def canonical_schema_bytes(payload: Mapping[str, Any]) -> bytes:
    """Stable JSON encoding used for schema hash locks."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def schema_hash_lock(payload: Mapping[str, Any], *, schema_version: str = SCHEMA_VERSION) -> str:
    """
    Legacy value-payload lock (kept for compatibility).

    Prefer :func:`schema_contract_hash` for field-name/type contracts.
    """
    body = {
        "schema_version": schema_version,
        "payload": dict(payload),
    }
    return hashlib.blake2b(canonical_schema_bytes(body), digest_size=32).hexdigest()


def infer_field_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    text = str(value)
    if text.lstrip("-").replace(".", "", 1).isdigit() or any(ch.isdigit() for ch in text):
        # Money-like strings still declared as decimal/string contract
        return "decimal_str"
    return "string"


def schema_contract_hash(
    ground_truth: Mapping[str, Any],
    *,
    field_types: Mapping[str, str] | None = None,
    units: Mapping[str, str] | None = None,
    schema_version: str = SCHEMA_VERSION,
) -> str:
    """
    Hash the extraction *contract* (field names, types, units) — not values.

    Prevents silent schema drift while allowing value changes across cases.
    """
    names = sorted(ground_truth.keys())
    types = {
        name: (field_types or {}).get(name) or infer_field_type(ground_truth[name])
        for name in names
    }
    unit_map = {name: (units or {}).get(name, "") for name in names}
    body = {
        "schema_version": schema_version,
        "fields": names,
        "types": types,
        "units": unit_map,
    }
    return hashlib.blake2b(canonical_schema_bytes(body), digest_size=32).hexdigest()


def verify_schema_hash(
    payload: Mapping[str, Any],
    expected_hash: str,
    *,
    schema_version: str = SCHEMA_VERSION,
) -> bool:
    """Return True when the value-payload lock matches (legacy)."""
    if not expected_hash:
        return False
    return schema_hash_lock(payload, schema_version=schema_version) == expected_hash


def verify_schema_contract(
    ground_truth: Mapping[str, Any],
    expected_hash: str,
    *,
    field_types: Mapping[str, str] | None = None,
    units: Mapping[str, str] | None = None,
    schema_version: str = SCHEMA_VERSION,
) -> bool:
    """Return True when the field contract hash matches."""
    if not expected_hash:
        return False
    return (
        schema_contract_hash(
            ground_truth,
            field_types=field_types,
            units=units,
            schema_version=schema_version,
        )
        == expected_hash
    )
