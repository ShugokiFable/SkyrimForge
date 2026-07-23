from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .config import ForgeConfig
from .errors import ToolError, ValidationError
from .safety import require_approval, require_within
from .tools import resolve_tool, run_process
from .util import sha256_file


def compile_scripts(
    config: ForgeConfig,
    scripts: list[Path],
    output_dir: Path,
    *,
    imports: list[Path],
    flags_file: Path,
    approved: bool,
) -> dict[str, Any]:
    require_approval(approved, "Papyrus compilation")
    tool, compiler = resolve_tool(config, "papyrus_compiler")
    output_dir = require_within(output_dir, config.workspace_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    if not flags_file.is_file():
        raise FileNotFoundError(flags_file)
    for path in imports:
        if not path.is_dir():
            raise FileNotFoundError(path)
    results = []
    for source in scripts:
        source = source.resolve(strict=True)
        if source.suffix.casefold() != ".psc":
            raise ValidationError(f"Papyrus source must be .psc: {source}")
        target = output_dir / f"{source.stem}.pex"
        previous = (target.stat().st_mtime_ns, sha256_file(target)) if target.is_file() else None
        args = [str(source), f"-f={flags_file}", f"-i={';'.join(str(path) for path in imports)}", f"-o={output_dir}"]
        process = run_process(compiler, args, cwd=source.parent, timeout_seconds=tool.timeout_seconds)
        fresh = target.is_file() and (previous is None or target.stat().st_mtime_ns > previous[0] or sha256_file(target) != previous[1])
        item = {"source": str(source), "process": process, "output": str(target), "fresh": fresh}
        if target.is_file():
            item.update({"sha256": sha256_file(target), "size": target.stat().st_size})
        if process["returncode"] != 0 or not fresh:
            raise ToolError(f"Papyrus compilation failed or produced no fresh PEX for {source.name}")
        results.append(item)
    return {"result": "PASS", "compiled": results}
