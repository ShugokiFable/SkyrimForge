from __future__ import annotations

from dataclasses import asdict

import os
import struct
from pathlib import Path
from typing import Any

from .errors import SafetyError, ValidationError
from .plugin_header import inspect_plugin_header
from .records import iter_records
from .safety import require_approval, require_within, validate_filename
from .strictjson import load
from .util import atomic_write_bytes, sha256_file

FORM_VERSION = 44
HEDR_VERSION = 1.71
ALLOWED_CREATE = {"KYWD", "GLOB", "FLST", "OTFT"}


def _sub(signature: str, payload: bytes) -> bytes:
    sig = signature.encode("ascii")
    if len(payload) <= 0xFFFF:
        return sig + struct.pack("<H", len(payload)) + payload
    return b"XXXX" + struct.pack("<H", 4) + struct.pack("<I", len(payload)) + sig + b"\0\0" + payload


def _z(value: str) -> bytes:
    return value.encode("utf-8") + b"\0"


def _record(signature: str, form_id: int, payload: bytes, flags: int = 0) -> bytes:
    return signature.encode("ascii") + struct.pack("<III", len(payload), flags, form_id) + b"\0\0\0\0" + struct.pack("<H", FORM_VERSION) + b"\0\0" + payload


def _group(signature: str, records: list[bytes]) -> bytes:
    body = b"".join(records)
    # Top-level group: label is the record signature, group type 0.
    return b"GRUP" + struct.pack("<I", 24 + len(body)) + signature.encode("ascii") + struct.pack("<i", 0) + b"\0" * 8 + body


def _header(masters: list[str], record_count: int, next_id: int, author: str, description: str, light: bool) -> bytes:
    payload = _sub("HEDR", struct.pack("<fII", HEDR_VERSION, record_count, next_id))
    payload += _sub("CNAM", _z(author)) + _sub("SNAM", _z(description))
    for master in masters:
        payload += _sub("MAST", _z(master)) + _sub("DATA", struct.pack("<Q", 0))
    flags = 0x00000200 if light else 0
    return b"TES4" + struct.pack("<III", len(payload), flags, 0) + b"\0\0\0\0" + struct.pack("<H", FORM_VERSION) + b"\0\0" + payload


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    allowed = {"schema", "output", "plugin_type", "masters", "author", "description", "operations"}
    unknown = set(plan) - allowed
    if unknown:
        raise ValidationError(f"Unknown plugin plan fields: {sorted(unknown)}")
    if plan.get("schema") != "skyrim-forge-plugin-plan/1":
        raise ValidationError("Unsupported plugin plan schema")
    output = plan.get("output")
    if not isinstance(output, str):
        raise ValidationError("output is required")
    validate_filename(output, {".esp", ".esm", ".esl"})
    plugin_type = plan.get("plugin_type", "esp")
    if plugin_type not in {"esp", "esl", "espfe"}:
        raise ValidationError("plugin_type must be esp, esl, or espfe")
    masters = plan.get("masters", [])
    if not isinstance(masters, list) or not all(isinstance(item, str) and Path(item).name == item for item in masters):
        raise ValidationError("masters must be plugin filenames")
    if len({m.casefold() for m in masters}) != len(masters):
        raise ValidationError("Duplicate masters")
    operations = plan.get("operations")
    if not isinstance(operations, list) or not operations:
        raise ValidationError("operations must be non-empty")
    editor_ids: set[str] = set()
    for index, operation in enumerate(operations):
        if not isinstance(operation, dict):
            raise ValidationError(f"operation {index} must be an object")
        kind = operation.get("record")
        if kind not in ALLOWED_CREATE:
            raise ValidationError(f"operation {index} unsupported record type: {kind!r}")
        allowed_fields = {"record", "editor_id", "value", "type", "forms"}
        if set(operation) - allowed_fields:
            raise ValidationError(f"operation {index} unknown fields: {sorted(set(operation)-allowed_fields)}")
        editor_id = operation.get("editor_id")
        if not isinstance(editor_id, str) or not editor_id or not editor_id.replace("_", "A").isalnum():
            raise ValidationError(f"operation {index} invalid editor_id")
        if editor_id.casefold() in editor_ids:
            raise ValidationError(f"duplicate editor_id: {editor_id}")
        editor_ids.add(editor_id.casefold())
        if kind == "GLOB":
            if not isinstance(operation.get("value"), (int, float)) or isinstance(operation.get("value"), bool):
                raise ValidationError(f"GLOB operation {index} requires numeric value")
            if operation.get("type", "f") not in {"f", "s", "l"}:
                raise ValidationError(f"GLOB operation {index} type must be f, s, or l")
        if kind in {"FLST", "OTFT"}:
            forms = operation.get("forms", [])
            if not isinstance(forms, list) or not all(isinstance(item, int) and 0 <= item <= 0xFFFFFFFF for item in forms):
                raise ValidationError(f"{kind} operation {index} forms must be 32-bit integers")
    return plan


def build_plugin(plan_path: Path, output_root: Path, *, approved: bool) -> dict[str, Any]:
    require_approval(approved, "plugin creation")
    plan = validate_plan(load(plan_path))
    output_root.mkdir(parents=True, exist_ok=True)
    output = require_within(output_root / plan["output"], output_root)
    if output.exists():
        raise SafetyError(f"Refusing to overwrite existing plugin: {output}")
    light = plan.get("plugin_type") in {"esl", "espfe"}
    base_id = 0x800 if light else 0x800
    max_id = 0xFFF if light else 0x00FFFFFF
    self_index = len(plan.get("masters", []))
    groups: dict[str, list[bytes]] = {}
    for offset, operation in enumerate(plan["operations"]):
        local = base_id + offset
        if local > max_id:
            raise ValidationError("Plan exceeds available local FormID range")
        form_id = (self_index << 24) | local
        kind = operation["record"]
        payload = _sub("EDID", _z(operation["editor_id"]))
        if kind == "GLOB":
            payload += _sub("FNAM", operation.get("type", "f").encode("ascii"))
            payload += _sub("FLTV", struct.pack("<f", float(operation["value"])))
        elif kind == "FLST":
            for form in operation.get("forms", []):
                payload += _sub("LNAM", struct.pack("<I", form))
        elif kind == "OTFT":
            for form in operation.get("forms", []):
                payload += _sub("INAM", struct.pack("<I", form))
        groups.setdefault(kind, []).append(_record(kind, form_id, payload))
    body = b"".join(_group(kind, groups[kind]) for kind in sorted(groups))
    header = _header(plan.get("masters", []), len(plan["operations"]), base_id + len(plan["operations"]), plan.get("author", "Skyrim Forge"), plan.get("description", "Generated by Skyrim Forge"), light)
    transaction = output.with_name(f".{output.name}.forge.tmp")
    atomic_write_bytes(transaction, header + body)
    reopened = inspect_plugin_header(transaction)
    actual_records = list(iter_records(transaction))
    if reopened.form_version != FORM_VERSION or len(actual_records) != len(plan["operations"]):
        transaction.unlink(missing_ok=True)
        raise ValidationError("Generated plugin failed reopen verification")
    os.replace(transaction, output)
    return {
        "result": "PASS",
        "output": str(output),
        "sha256": sha256_file(output),
        "size": output.stat().st_size,
        "header": asdict(reopened),
        "records": [{"signature": item.signature, "form_id": item.raw_form_id_hex, "editor_id": item.editor_id} for item in actual_records],
        "evidence": "Typed Forge writer output reopened by Forge. xEdit and Skyrim runtime checks remain separate.",
    }
