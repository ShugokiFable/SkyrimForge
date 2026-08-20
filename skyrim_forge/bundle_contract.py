from __future__ import annotations

from typing import Any

from .version import VERSION

CONTRACT_VERSION = 1
MIN_BUNDLE = (7, 8, 0)
MAX_BUNDLE_EXCLUSIVE = (8, 0, 0)


def _version_tuple(value: str) -> tuple[int, int, int]:
    parts = value.strip().lstrip("vV").split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError(f"Expected semantic version X.Y.Z, got {value!r}")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def evaluate_bundle_contract(bundle_version: str) -> dict[str, Any]:
    """Return the machine-readable compatibility handshake used by bundle 7.8+."""
    try:
        parsed = _version_tuple(bundle_version)
    except ValueError as exc:
        return {
            "product": "Skyrim Forge",
            "forge_version": VERSION,
            "bundle_version": bundle_version,
            "contract_version": CONTRACT_VERSION,
            "result": "FAIL",
            "reason": str(exc),
            "capabilities": {},
        }

    capabilities = {
        "mcp_stdio": True,
        "provider_registration": True,
        "doctor": True,
        "self_test": True,
        "bundle_contract": True,
    }
    if parsed < MIN_BUNDLE:
        result = "FAIL"
        reason = "Skyrim Forge 5.2 requires Ultimate AI Starter Bundle >= 7.8.0"
    elif parsed >= MAX_BUNDLE_EXCLUSIVE:
        result = "FAIL"
        reason = "Skyrim Forge 5.2 contract supports Ultimate AI Starter Bundle >= 7.8.0 and < 8.0.0"
    else:
        result = "PASS"
        reason = "Compatible"
    return {
        "product": "Skyrim Forge",
        "forge_version": VERSION,
        "bundle_version": bundle_version,
        "contract_version": CONTRACT_VERSION,
        "supported_bundle_range": ">=7.8.0,<8.0.0",
        "result": result,
        "reason": reason,
        "capabilities": capabilities,
    }
