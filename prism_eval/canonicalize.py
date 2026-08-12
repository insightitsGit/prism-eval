"""Field value canonicalization for robust determinism / digit-drop checks."""

from __future__ import annotations

import re
from typing import Any


_MONEY_HINTS = ("usd", "amount", "agi", "income", "price", "total", "balance", "proceeds")


def digits_only(value: Any) -> str:
    """
    Extract a canonical integer digit string from money-like values.

    ``$450,000.00`` → ``450000`` (fractional .00 dropped).
    Non-zero cents floor to whole dollars for extraction-bench comparison.
    """
    text = str(value).strip()
    if not text:
        return ""

    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1].strip()
    if text.lstrip().startswith("-"):
        negative = True

    cleaned = text.replace(",", "").replace(" ", "")
    cleaned = re.sub(r"[$€£¥]", "", cleaned)

    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        raw = re.sub(r"\D", "", text)
        if not raw:
            return ""
        digits = raw.lstrip("0") or "0"
        return f"-{digits}" if negative and digits != "0" else digits

    number = match.group(0).lstrip("-")
    if "." in number:
        whole, _frac = number.split(".", 1)
        digits = whole.lstrip("0") or "0"
    else:
        digits = number.lstrip("0") or "0"

    return f"-{digits}" if negative and digits != "0" else digits


def looks_numeric_field(field_name: str, value: Any) -> bool:
    name = field_name.lower()
    if any(h in name for h in _MONEY_HINTS):
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return True
    text = str(value).strip()
    if re.fullmatch(r"[-+$€£]?\s*\(?\d[\d,]*(\.\d+)?\)?", text):
        return True
    return bool(digits_only(value)) and bool(re.search(r"\d", text)) and not re.search(
        r"[A-Za-z]{3,}", text
    )


def canonicalize_value(field_name: str, value: Any) -> str:
    """Normalize a field value for equality comparison."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if looks_numeric_field(field_name, value):
        return digits_only(value)
    if isinstance(value, (dict, list)):
        import json

        return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return str(value).strip()


def values_equivalent(field_name: str, proposed: Any, expected: Any) -> bool:
    return canonicalize_value(field_name, proposed) == canonicalize_value(field_name, expected)


def is_digit_truncation(proposed: Any, expected: Any) -> bool:
    """
    True when proposed digits are a strict truncation / single-digit deletion of expected.

    Classic example: expected 450000, proposed 45000.
    """
    p = digits_only(proposed)
    e = digits_only(expected)
    if not e or not p or p == e:
        return False
    if e == "0":
        return False
    # Prefix / suffix truncation
    if len(p) < len(e) and (e.startswith(p) or e.endswith(p)):
        return True
    # Single-digit deletion subsequence
    if len(e) - len(p) == 1 and _is_subsequence(p, e):
        return True
    return False


def _is_subsequence(short: str, long: str) -> bool:
    it = iter(long)
    return all(ch in it for ch in short)
