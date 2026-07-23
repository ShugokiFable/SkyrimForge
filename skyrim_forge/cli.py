from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .errors import ForgeError
from .service import ForgeService
from .strictjson import dumps
from .version import VERSION


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="forge", description="Skyrim Forge 3.0 Automation Fabric")
    root.add_argument("--config", help="Alternate config.toml")
    root.add_argument("--version", action="version", version=f"Skyrim Forge {VERSION}")
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("version")
    sub.add_parser("doctor")
    sub.add_parser("self-test")
    sub.add_parser("config-show")
    setp = sub.add_parser("config-set"); setp.add_argument("key"); setp.add_argument("value")
    sub.add_parser("discover-tools")
    status = sub.add_parser("tool-status"); status.add_argument("name")
    info = sub.add_parser("plugin-info"); info.add_argument("path")
    query = sub.add_parser("record-query"); query.add_argument("path"); query.add_argument("--signature", default=""); query.add_argument("--editor-id", default=""); query.add_argument("--form-id", default=""); query.add_argument("--limit", type=int, default=5000)
    plugins = sub.add_parser("plugins"); plugins.add_argument("path", nargs="?")
    archive = sub.add_parser("archive-info"); archive.add_argument("path")
    tree = sub.add_parser("mod-tree"); tree.add_argument("path")
    lint = sub.add_parser("lint"); lint.add_argument("paths", nargs="+")
    rv = sub.add_parser("release-validate"); rv.add_argument("root")
    rb = sub.add_parser("release-build"); rb.add_argument("root"); rb.add_argument("output"); rb.add_argument("--approve", action="store_true")
    pv = sub.add_parser("plugin-plan-validate"); pv.add_argument("path")
    pb = sub.add_parser("plugin-build"); pb.add_argument("path"); pb.add_argument("output_dir"); pb.add_argument("--approve", action="store_true")
    av = sub.add_parser("automation-validate"); av.add_argument("path")
    ar = sub.add_parser("automation-run"); ar.add_argument("path"); ar.add_argument("--approve", action="store_true"); ar.add_argument("--discard-transaction", action="store_true")
    mcp = sub.add_parser("mcp")
    gui = sub.add_parser("gui")
    return root


def _exit_code(value: Any) -> int:
    if isinstance(value, dict):
        status = str(value.get("result", value.get("status", ""))).upper()
        if status in {"FAIL", "BLOCKED", "INVALID", "INCOMPLETE", "CANCELLED"}:
            return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "version":
        print(dumps({"product": "Skyrim Forge", "version": VERSION}))
        return 0
    if args.command == "self-test":
        from .frameworks import self_test as framework_self_test
        framework = framework_self_test()
        value = {"result": "PASS" if framework["result"] == "PASS" else "FAIL", "frameworks": framework, "version": VERSION}
        print(dumps(value))
        return _exit_code(value)
    if args.command == "mcp":
        from .mcp_server import serve
        serve(args.config)
        return 0
    if args.command == "gui":
        from .gui import run_gui
        run_gui(args.config)
        return 0
    from .config import load_config
    service = ForgeService(load_config(args.config))
    try:
        match args.command:
            case "doctor": value = service.doctor()
            case "config-show": value = service.config_show()
            case "config-set": value = service.config_set(args.key, args.value)
            case "discover-tools": value = service.discover()
            case "tool-status": value = service.tool_status(args.name)
            case "plugin-info": value = service.plugin_info(args.path)
            case "record-query": value = service.record_query(args.path, args.signature, args.editor_id, args.form_id, args.limit)
            case "plugins": value = service.plugins(args.path)
            case "archive-info": value = service.archive(args.path)
            case "mod-tree": value = service.mod_tree(args.path)
            case "lint": value = service.lint(args.paths)
            case "release-validate": value = service.release_validate(args.root)
            case "release-build": value = service.release_build(args.root, args.output, args.approve)
            case "plugin-plan-validate": value = service.plan_validate(args.path)
            case "plugin-build": value = service.plugin_build(args.path, args.output_dir, args.approve)
            case "automation-validate": value = service.automation_validate(args.path)
            case "automation-run": value = service.automation_run(args.path, args.approve, not args.discard_transaction)
            case _: raise AssertionError(args.command)
        print(dumps(value))
        return _exit_code(value)
    except Exception as exc:
        print(dumps({"result": "FAIL", "error": type(exc).__name__, "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
