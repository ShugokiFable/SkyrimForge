from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .config import ForgeConfig
from .tools import discover_executable, tool_status
from .version import VERSION


def doctor(config: ForgeConfig) -> dict[str, Any]:
    core = []
    core.append({"check": "workspace_root", "status": "PASS" if config.workspace_root.is_dir() else "FAIL", "path": str(config.workspace_root)})
    core.append({"check": "config", "status": "PASS" if config.config_path.is_file() else "FAIL", "path": str(config.config_path)})
    skyrim_ok = bool(config.skyrim_data and config.skyrim_data.is_dir())
    tools = {name: tool_status(config, name) for name in config.tools}
    xedit_ready = bool(tools["xedit"].get("exists") and tools["xedit"].get("hash_match", True))
    mo2_ready = bool(tools["mo2"].get("exists"))
    plugin_write_ready = config.workspace_root.is_dir()
    return {
        "product": "Skyrim Forge",
        "version": VERSION,
        "result": "PASS" if all(item["status"] == "PASS" for item in core) else "FAIL",
        "core": core,
        "read_only_ready": config.workspace_root.is_dir(),
        "plugin_write_ready": plugin_write_ready,
        "skyrim_data_ready": skyrim_ok,
        "xedit_automation_ready": config.allow_external_processes and xedit_ready,
        "mo2_automation_ready": config.allow_external_processes and mo2_ready,
        "external_processes_enabled": config.allow_external_processes,
        "ui_automation_enabled": config.allow_ui_automation,
        "tools": tools,
        "warnings": config.load_warnings,
    }


def discover_tools(config: ForgeConfig) -> dict[str, str]:
    roots = [path for path in (config.tools_root, Path("C:/Modding"), Path("C:/Games"), Path("C:/Program Files"), Path("C:/Program Files (x86)")) if path and path.exists()]
    names = {
        "xedit": ["SSEEdit64.exe", "SSEEdit.exe"],
        "mo2": ["ModOrganizer.exe"],
        "loot": ["LOOT.exe"],
        "wrye_bash": ["Wrye Bash.exe", "WryeBash.exe"],
        "creation_kit": ["CreationKit.exe"],
        "ckpe_loader": ["ckpe_loader.exe"],
        "papyrus_compiler": ["PapyrusCompiler.exe"],
        "archive": ["Archive.exe", "BSArch.exe", "7z.exe"],
    }
    found = {}
    for name, executable_names in names.items():
        path = discover_executable(executable_names, roots)
        if path:
            found[name] = str(path)
    return found
