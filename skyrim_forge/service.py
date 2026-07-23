from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .archive import inspect_archive
from .automation import run_job, validate_job
from .config import ForgeConfig, configure_value, load_config, save_config
from .environment import discover_tools, doctor
from .frameworks import lint_paths, self_test as framework_self_test
from .loadorder import parse_plugins_file
from .modtree import inspect_mod_directory
from .plugin_header import inspect_plugin_header
from .plugin_writer import build_plugin, validate_plan
from .records import query_records
from .release import build_release, validate_release_tree
from .strictjson import load
from .tools import tool_status
from .version import VERSION
from .safety import require_read, require_within


def plain(value: Any) -> Any:
    if is_dataclass(value):
        return {key: plain(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


class ForgeService:
    def __init__(self, config: ForgeConfig | None = None):
        self.config = config or load_config()

    def _read(self, path: str) -> Path:
        return require_read(Path(path), self.config.allowed_read_roots)

    def version(self) -> dict[str, Any]:
        return {"product": "Skyrim Forge", "version": VERSION}

    def doctor(self) -> dict[str, Any]:
        return doctor(self.config)

    def config_show(self) -> dict[str, Any]:
        return plain(self.config)

    def config_set(self, key: str, value: str) -> dict[str, Any]:
        configure_value(self.config, key, value)
        return {"result": "PASS", "config": str(self.config.config_path), "key": key, "value": value}

    def discover(self) -> dict[str, Any]:
        return {"found": discover_tools(self.config)}

    def tool_status(self, name: str) -> dict[str, Any]:
        return tool_status(self.config, name)

    def plugin_info(self, path: str) -> dict[str, Any]:
        return {"header": plain(inspect_plugin_header(self._read(path))), "evidence": "Header inspection only. Semantic and runtime validation not performed."}

    def record_query(self, path: str, signature: str = "", editor_id: str = "", form_id: str = "", limit: int = 5000) -> dict[str, Any]:
        parsed = int(form_id, 0) if form_id else None
        return query_records(self._read(path), signature=signature, editor_id=editor_id, form_id=parsed, limit=limit)

    def plugins(self, path: str | None = None) -> dict[str, Any]:
        target = Path(path) if path else self.config.plugins_file
        if target is None:
            return {"result": "INCOMPLETE", "message": "plugins_file is not configured"}
        return {"path": str(target), "plugins": plain(parse_plugins_file(require_read(target, self.config.allowed_read_roots)))}

    def archive(self, path: str) -> dict[str, Any]:
        return plain(inspect_archive(self._read(path), seven_zip=self.config.seven_zip, allow_external=self.config.allow_external_processes))

    def mod_tree(self, path: str) -> dict[str, Any]:
        return plain(inspect_mod_directory(self._read(path), self.config.max_scan_files))

    def lint(self, paths: list[str]) -> dict[str, Any]:
        return lint_paths([self._read(path) for path in paths])

    def release_validate(self, root: str) -> dict[str, Any]:
        return validate_release_tree(self._read(root))

    def release_build(self, root: str, output: str, approved: bool) -> dict[str, Any]:
        return build_release(self._read(root), require_within(Path(output), self.config.workspace_root), self.config.workspace_root, approved=approved)

    def plan_validate(self, path: str) -> dict[str, Any]:
        return {"result": "PASS", "plan": validate_plan(load(self._read(path)))}

    def plugin_build(self, path: str, output_dir: str, approved: bool) -> dict[str, Any]:
        return build_plugin(self._read(path), require_within(Path(output_dir), self.config.workspace_root), approved=approved)

    def automation_validate(self, path: str) -> dict[str, Any]:
        return {"result": "PASS", "job": validate_job(load(self._read(path)))}

    def automation_run(self, path: str, approved: bool, keep_transaction: bool = True) -> dict[str, Any]:
        return run_job(self.config, Path(path), approved=approved, keep_transaction=keep_transaction)

    def self_test(self) -> dict[str, Any]:
        framework = framework_self_test()
        return {"result": "PASS" if framework["result"] == "PASS" else "FAIL", "frameworks": framework, "version": VERSION}
