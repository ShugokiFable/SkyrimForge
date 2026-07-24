from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "writer" / "native-go"
TARGETS = {
    "linux": (ROOT / "writer" / "published" / "linux-x64" / "SkyrimForge.Native", {"CGO_ENABLED":"0","GOOS":"linux","GOARCH":"amd64"}),
    "windows": (ROOT / "writer" / "published" / "win-x64" / "SkyrimForge.Native.exe", {"CGO_ENABLED":"0","GOOS":"windows","GOARCH":"amd64"}),
}
PACKAGE_TARGETS = {
    "linux": ROOT / "skyrim_forge" / "bin" / "linux-x64" / "SkyrimForge.Native",
    "windows": ROOT / "skyrim_forge" / "bin" / "win-x64" / "SkyrimForge.Native.exe",
}


def build(target: str) -> None:
    output, environment = TARGETS[target]
    output.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy(); env.update(environment)
    command = ["go", "build", "-trimpath", "-buildvcs=false", "-ldflags=-s -w -buildid=", "-o", str(output), "."]
    subprocess.run(command, cwd=SOURCE, env=env, check=True)
    package = PACKAGE_TARGETS[target]
    package.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output, package)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rebuild deterministic Skyrim Forge native helpers")
    parser.add_argument("--target", choices=["all", *TARGETS], default="all")
    args = parser.parse_args()
    selected = TARGETS if args.target == "all" else [args.target]
    for target in selected:
        build(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
