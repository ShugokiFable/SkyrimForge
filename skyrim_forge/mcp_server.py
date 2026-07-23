from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

from .config import load_config
from .service import ForgeService
from .strictjson import loads
from .version import VERSION

PROTOCOLS = {"2025-11-25", "2025-06-18", "2024-11-05"}


def _schema(properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties or {}, "required": required or [], "additionalProperties": False}


def _string(description: str = "") -> dict[str, Any]: return {"type": "string", "description": description}
def _boolean(description: str = "") -> dict[str, Any]: return {"type": "boolean", "description": description}
def _integer(description: str = "") -> dict[str, Any]: return {"type": "integer", "description": description}
def _array(description: str = "") -> dict[str, Any]: return {"type": "array", "items": {"type": "string"}, "description": description}


TOOL_SPECS: dict[str, dict[str, Any]] = {
    "forge_version": {"description": "Return Skyrim Forge version.", "inputSchema": _schema()},
    "forge_doctor": {"description": "Inspect Forge configuration and automation readiness.", "inputSchema": _schema()},
    "forge_self_test": {"description": "Run built-in framework regression fixtures.", "inputSchema": _schema()},
    "forge_config_show": {"description": "Read sanitized Forge configuration.", "inputSchema": _schema()},
    "forge_config_set": {"description": "Change one allowlisted Forge configuration value.", "inputSchema": _schema({"key": _string(), "value": _string(), "approved": _boolean()}, ["key", "value", "approved"])},
    "forge_discover_tools": {"description": "Find known Skyrim tool executables without changing configuration.", "inputSchema": _schema()},
    "forge_tool_status": {"description": "Inspect one configured tool, including pinned hash status.", "inputSchema": _schema({"name": _string()}, ["name"])},
    "forge_plugin_info": {"description": "Inspect TES4 header and masters. Header evidence only.", "inputSchema": _schema({"path": _string()}, ["path"])},
    "forge_record_query": {"description": "Query plugin records by signature, EditorID, or raw FormID.", "inputSchema": _schema({"path": _string(), "signature": _string(), "editor_id": _string(), "form_id": _string(), "limit": _integer()}, ["path"])},
    "forge_plugins": {"description": "Read plugins.txt.", "inputSchema": _schema({"path": _string()})},
    "forge_archive_info": {"description": "Inspect ZIP/7z/RAR contents safely.", "inputSchema": _schema({"path": _string()}, ["path"])},
    "forge_mod_tree": {"description": "Inspect a loose mod directory.", "inputSchema": _schema({"path": _string()}, ["path"])},
    "forge_lint_frameworks": {"description": "Lint SPID, KID, BOS, SkyPatcher, and CDF files.", "inputSchema": _schema({"paths": _array()}, ["paths"])},
    "forge_release_validate": {"description": "Validate release tree hygiene.", "inputSchema": _schema({"root": _string()}, ["root"])},
    "forge_release_build": {"description": "Build deterministic release ZIP in the workspace.", "inputSchema": _schema({"root": _string(), "output": _string(), "approved": _boolean()}, ["root", "output", "approved"])},
    "forge_plugin_plan_validate": {"description": "Validate typed plugin creation plan.", "inputSchema": _schema({"path": _string()}, ["path"])},
    "forge_plugin_build": {"description": "Build KYWD, GLOB, FLST, or OTFT plugin from typed plan.", "inputSchema": _schema({"path": _string(), "output_dir": _string(), "approved": _boolean()}, ["path", "output_dir", "approved"])},
    "forge_automation_validate": {"description": "Validate a typed Automation Fabric job.", "inputSchema": _schema({"path": _string()}, ["path"])},
    "forge_automation_run": {"description": "Execute a typed transactional automation job.", "inputSchema": _schema({"path": _string(), "approved": _boolean(), "keep_transaction": _boolean()}, ["path", "approved"])},
}


def _call(service: ForgeService, name: str, args: dict[str, Any]) -> Any:
    approved = bool(args.get("approved", False))
    match name:
        case "forge_version": return service.version()
        case "forge_doctor": return service.doctor()
        case "forge_self_test": return service.self_test()
        case "forge_config_show": return service.config_show()
        case "forge_config_set":
            if not approved: raise PermissionError("approved=true is required to change configuration")
            return service.config_set(args["key"], args["value"])
        case "forge_discover_tools": return service.discover()
        case "forge_tool_status": return service.tool_status(args["name"])
        case "forge_plugin_info": return service.plugin_info(args["path"])
        case "forge_record_query": return service.record_query(args["path"], args.get("signature", ""), args.get("editor_id", ""), args.get("form_id", ""), int(args.get("limit", 5000)))
        case "forge_plugins": return service.plugins(args.get("path") or None)
        case "forge_archive_info": return service.archive(args["path"])
        case "forge_mod_tree": return service.mod_tree(args["path"])
        case "forge_lint_frameworks": return service.lint(args["paths"])
        case "forge_release_validate": return service.release_validate(args["root"])
        case "forge_release_build": return service.release_build(args["root"], args["output"], approved)
        case "forge_plugin_plan_validate": return service.plan_validate(args["path"])
        case "forge_plugin_build": return service.plugin_build(args["path"], args["output_dir"], approved)
        case "forge_automation_validate": return service.automation_validate(args["path"])
        case "forge_automation_run": return service.automation_run(args["path"], approved, bool(args.get("keep_transaction", True)))
        case _: raise KeyError(name)


def _text(value: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True, default=str)}], "isError": False}


def _error(exc: Exception) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps({"result": "FAIL", "error": type(exc).__name__, "message": str(exc)}, indent=2)}], "isError": True}


def _resource_root() -> Path:
    return Path(__file__).resolve().parents[1]


def handle(service: ForgeService, request: dict[str, Any]) -> dict[str, Any] | None:
    if request.get("jsonrpc") != "2.0":
        raise ValueError("JSON-RPC 2.0 required")
    method = request.get("method")
    request_id = request.get("id")
    if method in {"notifications/initialized", "notifications/cancelled"}:
        return None
    if method == "initialize":
        requested = request.get("params", {}).get("protocolVersion", "2025-11-25")
        protocol = requested if requested in PROTOCOLS else "2025-11-25"
        result = {"protocolVersion": protocol, "capabilities": {"tools": {"listChanged": False}, "resources": {"subscribe": False, "listChanged": False}, "prompts": {"listChanged": False}}, "serverInfo": {"name": "skyrim-forge", "version": VERSION}, "instructions": "Use typed Forge jobs. Never send arbitrary shell commands or write to live Skyrim Data."}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": name, **spec} for name, spec in sorted(TOOL_SPECS.items())]}
    elif method == "tools/call":
        params = request.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        if name not in TOOL_SPECS or not isinstance(args, dict):
            raise ValueError("Unknown tool or invalid arguments")
        try:
            result = _text(_call(service, name, args))
        except Exception as exc:
            result = _error(exc)
    elif method == "resources/list":
        result = {"resources": [
            {"uri": "forge://docs/automation-fabric", "name": "Automation Fabric", "mimeType": "text/markdown"},
            {"uri": "forge://schemas/automation-job", "name": "Automation Job Schema", "mimeType": "application/json"},
            {"uri": "forge://config", "name": "Forge Configuration", "mimeType": "application/json"},
        ]}
    elif method == "resources/read":
        uri = request.get("params", {}).get("uri")
        if uri == "forge://docs/automation-fabric":
            text = (_resource_root() / "docs" / "AUTOMATION-FABRIC.md").read_text(encoding="utf-8")
            mime = "text/markdown"
        elif uri == "forge://schemas/automation-job":
            text = (_resource_root() / "schemas" / "automation-job.schema.json").read_text(encoding="utf-8")
            mime = "application/json"
        elif uri == "forge://config":
            text = json.dumps(service.config_show(), indent=2, default=str)
            mime = "application/json"
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
        result = {"contents": [{"uri": uri, "mimeType": mime, "text": text}]}
    elif method == "prompts/list":
        result = {"prompts": [
            {"name": "verify_mod_release", "description": "Plan a Forge verification pipeline for a mod release.", "arguments": [{"name": "release_root", "required": True}]},
            {"name": "build_compatibility_patch", "description": "Plan a typed compatibility patch without GUI handoff.", "arguments": [{"name": "mod_a", "required": True}, {"name": "mod_b", "required": True}]},
        ]}
    elif method == "prompts/get":
        params = request.get("params", {})
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "verify_mod_release":
            prompt = f"Create a skyrim-forge-automation/1 verify_release job for {args.get('release_root','<release>')}. Use xEdit only if configured. Do not claim Skyrim runtime validation."
        elif name == "build_compatibility_patch":
            prompt = f"Inspect {args.get('mod_a','<A>')} and {args.get('mod_b','<B>')}. Produce a typed Forge plugin plan or a fixed allowlisted xEdit job. Never leave the user in a GUI."
        else:
            raise ValueError(f"Unknown prompt: {name}")
        result = {"description": name, "messages": [{"role": "user", "content": {"type": "text", "text": prompt}}]}
    else:
        raise ValueError(f"Unsupported method: {method}")
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def serve(config_path: str | None = None) -> None:
    service = ForgeService(load_config(config_path))
    for raw in sys.stdin:
        if not raw.strip():
            continue
        request_id = None
        try:
            request = loads(raw)
            request_id = request.get("id") if isinstance(request, dict) else None
            response = handle(service, request)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":"), default=str) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            response = {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(exc), "data": {"type": type(exc).__name__}}}
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
