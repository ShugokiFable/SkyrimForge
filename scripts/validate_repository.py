from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = "3.0.1"
EXCLUDED = {".git", ".venv", "venv", "__pycache__", "dist", "build", ".pytest_cache", "htmlcov"}
REPORTS = {"VALIDATION.json", "BUILD-RECEIPT.json", "MANIFEST.json", "SBOM.spdx.json", "CHECKSUMS-SHA256.txt"}
TEXT_SUFFIXES = {".py", ".go", ".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".xml", ".ps1", ".bat", ".pas", ".cff"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024): digest.update(chunk)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path = ROOT, timeout: int = 600, env: dict[str, str] | None = None) -> dict[str, Any]:
    full_env = os.environ.copy(); full_env.update(env or {})
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False, timeout=timeout, env=full_env, shell=False)
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def repository_files() -> list[Path]:
    result = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.is_symlink(): continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED or part.casefold().endswith(".egg-info") for part in rel.parts): continue
        if path.name in REPORTS: continue
        if path.suffix in {".pyc", ".pyo"}: continue
        result.append(path)
    return sorted(result, key=lambda p: p.relative_to(ROOT).as_posix().casefold())


def validate_files(errors: list[str], warnings: list[str]) -> dict[str, Any]:
    counts = {"python":0,"json":0,"toml":0,"yaml":0,"xml":0,"powershell":0,"go":0,"pascal":0}
    seen: dict[str, str] = {}
    for path in ROOT.rglob("*"):
        if path.is_symlink(): errors.append(f"symlink in repository: {path.relative_to(ROOT)}")
    for path in repository_files():
        rel = path.relative_to(ROOT).as_posix(); key = rel.casefold()
        if key in seen and seen[key] != rel: errors.append(f"case collision: {seen[key]} and {rel}")
        seen[key] = rel
        suffix = path.suffix.casefold()
        try:
            if suffix == ".py": counts["python"] += 1; ast.parse(path.read_text(encoding="utf-8-sig"), filename=rel)
            elif suffix == ".json": counts["json"] += 1; json.loads(path.read_text(encoding="utf-8-sig"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
            elif suffix == ".toml": counts["toml"] += 1; tomllib.loads(path.read_text(encoding="utf-8-sig"))
            elif suffix == ".xml": counts["xml"] += 1; ET.parse(path)
            elif suffix in {".yaml", ".yml"}: counts["yaml"] += 1
            elif suffix == ".ps1": counts["powershell"] += 1
            elif suffix == ".go": counts["go"] += 1
            elif suffix == ".pas": counts["pascal"] += 1
        except Exception as exc: errors.append(f"parse failure {rel}: {exc}")
        if suffix in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if re.search(r"[A-Za-z]:\\Users\\(?!YOU\\|<)", text, flags=re.I): errors.append(f"private Windows path in {rel}")
            if rel != "scripts/validate_repository.py":
                if "/mnt/data/" in text or "/tmp/" in text: errors.append(f"build-environment path in {rel}")
                if "SkyrimForge.Native 2." in text or "Skyrim Forge 2." in text: errors.append(f"stale major version in {rel}")
            if suffix in {".yml", ".yaml"}:
                for match in re.finditer(r"uses:\s*([^\s#]+)", text):
                    ref = match.group(1).rsplit("@",1)[-1]
                    if not re.fullmatch(r"[0-9a-f]{40}", ref): errors.append(f"floating GitHub Action in {rel}: {match.group(1)}")
    required = [
        "README.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "PUBLISH-TO-GITHUB.md",
        "schemas/automation-job.schema.json", "resources/xedit/SkyrimForgeCheckErrors.pas",
        "writer/published/win-x64/SkyrimForge.Native.exe", "writer/published/linux-x64/SkyrimForge.Native",
        "skyrim_forge/bin/win-x64/SkyrimForge.Native.exe", "skyrim_forge/bin/linux-x64/SkyrimForge.Native",
    ]
    for rel in required:
        if not (ROOT/rel).is_file(): errors.append(f"required file missing: {rel}")
    for name in ("automation-job.schema.json", "plugin-plan.schema.json", "external-worker-job.schema.json", "ui-job.schema.json"):
        if (ROOT/"schemas"/name).read_bytes() != (ROOT/"skyrim_forge"/"schemas"/name).read_bytes(): errors.append(f"schema copies differ: {name}")
    for name in ("SkyrimForgeCheckErrors.pas", "SkyrimForgeReportRecords.pas"):
        if (ROOT/"resources"/"xedit"/name).read_bytes() != (ROOT/"skyrim_forge"/"resources"/"xedit"/name).read_bytes(): errors.append(f"xEdit resource copies differ: {name}")
    return {"file_count":len(repository_files()),"counts":counts}


def validate_python(errors: list[str]) -> dict[str, Any]:
    compile_result = run([sys.executable,"-m","compileall","-q","skyrim_forge","tests","scripts"])
    tests = run([sys.executable,"-m","unittest","discover","-s","tests","-v"], timeout=900)
    if compile_result["returncode"]: errors.append("Python compileall failed")
    if tests["returncode"]: errors.append("Python unit tests failed")
    count_match = re.search(r"Ran (\d+) tests", tests["stderr"] + tests["stdout"])
    return {"compile":compile_result,"tests":tests,"test_count":int(count_match.group(1)) if count_match else None,"result":"PASS" if not compile_result["returncode"] and not tests["returncode"] else "FAIL"}


def validate_go(errors: list[str], warnings: list[str]) -> dict[str, Any]:
    if not shutil.which("go"):
        warnings.append("Go unavailable; native source and reproducibility checks skipped")
        return {"result":"NOT-RUN"}
    cwd = ROOT/"writer"/"native-go"
    fmt = run(["gofmt","-l","."],cwd=cwd); vet=run(["go","vet","./..."],cwd=cwd); tests=run(["go","test","./..."],cwd=cwd); race=run(["go","test","-race","./..."],cwd=cwd)
    if fmt["returncode"] or fmt["stdout"].strip(): errors.append("gofmt failed")
    if vet["returncode"]: errors.append("go vet failed")
    if tests["returncode"]: errors.append("go tests failed")
    if race["returncode"]: errors.append("go race tests failed")
    builds={}
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        for target, env in {"linux":{"CGO_ENABLED":"0","GOOS":"linux","GOARCH":"amd64"},"windows":{"CGO_ENABLED":"0","GOOS":"windows","GOARCH":"amd64"}}.items():
            suffix=".exe" if target=="windows" else ""; a=td/f"{target}-a{suffix}"; b=td/f"{target}-b{suffix}"
            for output in (a,b):
                result=run(["go","build","-trimpath","-ldflags=-s -w -buildid=","-o",str(output),"."],cwd=cwd,env=env)
                if result["returncode"]: errors.append(f"{target} native build failed")
            if a.exists() and b.exists():
                bundled=ROOT/"writer"/"published"/("win-x64" if target=="windows" else "linux-x64")/("SkyrimForge.Native.exe" if target=="windows" else "SkyrimForge.Native")
                builds[target]={"first":sha256(a),"second":sha256(b),"bundled":sha256(bundled),"result":"PASS" if sha256(a)==sha256(b)==sha256(bundled) else "FAIL"}
                if builds[target]["result"]!="PASS": errors.append(f"{target} native binary is not reproducible")
    return {"format":fmt,"vet":vet,"tests":tests,"race":race,"builds":builds,"result":"PASS" if not any(x in errors for x in ["gofmt failed","go vet failed","go tests failed","go race tests failed"]) and all(x.get("result")=="PASS" for x in builds.values()) else "FAIL"}


def validate_native(errors: list[str], warnings: list[str]) -> dict[str, Any]:
    linux = ROOT / "writer" / "published" / "linux-x64" / "SkyrimForge.Native"
    windows = ROOT / "writer" / "published" / "win-x64" / "SkyrimForge.Native.exe"
    report: dict[str, Any] = {
        "hashes": {"linux": sha256(linux), "windows": sha256(windows)},
        "linux_elf": linux.read_bytes()[:4] == b"\x7fELF",
        "windows_pe": windows.read_bytes()[:2] == b"MZ" and windows.stat().st_size > 0x40,
    }
    if not report["linux_elf"]:
        errors.append("Linux native helper is not an ELF executable")
    if not report["windows_pe"]:
        errors.append("Windows native helper is not a PE executable")
    native = windows if os.name == "nt" else linux
    platform_name = "windows" if os.name == "nt" else "linux"
    version = run([str(native), "version"])
    self_test = run([str(native), "self-test"])
    if version["returncode"] or version["stdout"].strip() != f"SkyrimForge.Native {VERSION} go":
        errors.append(f"{platform_name} native version mismatch")
    if self_test["returncode"] or "PASS" not in self_test["stdout"]:
        errors.append(f"{platform_name} native self-test failed")
    report.update({"executed_platform": platform_name, "version": version, "self_test": self_test})
    report["result"] = "PASS" if report["linux_elf"] and report["windows_pe"] and version["returncode"] == self_test["returncode"] == 0 else "FAIL"
    return report


def validate_packaging(errors: list[str]) -> dict[str, Any]:
    sys.path.insert(0,str(ROOT)); import forge_build_backend
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        wa=Path(a)/forge_build_backend.build_wheel(a); wb=Path(b)/forge_build_backend.build_wheel(b)
        wheel_hash=sha256(wa); wheel_equal=wheel_hash==sha256(wb); wheel_size=wa.stat().st_size
        with zipfile.ZipFile(wa) as archive: crc=archive.testzip(); members=set(archive.namelist())
        required={"skyrim_forge/bin/win-x64/SkyrimForge.Native.exe","skyrim_forge/resources/xedit/SkyrimForgeCheckErrors.pas"}
    with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
        sa=Path(a)/forge_build_backend.build_sdist(a); sb=Path(b)/forge_build_backend.build_sdist(b)
        sdist_hash=sha256(sa); sdist_equal=sdist_hash==sha256(sb); sdist_size=sa.stat().st_size
    if not wheel_equal or crc or not required.issubset(members): errors.append("wheel packaging failed")
    if not sdist_equal: errors.append("sdist packaging failed")
    return {"wheel":{"result":"PASS" if wheel_equal and not crc and required.issubset(members) else "FAIL","sha256":wheel_hash,"size":wheel_size},"sdist":{"result":"PASS" if sdist_equal else "FAIL","sha256":sdist_hash,"size":sdist_size}}


def validate_mcp(errors: list[str]) -> dict[str, Any]:
    initialize=json.dumps({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25"}})
    tools=json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
    completed=subprocess.run([sys.executable,"-m","skyrim_forge","mcp"],cwd=ROOT,input=initialize+"\n"+tools+"\n",text=True,capture_output=True,timeout=30,shell=False,env={**os.environ,"HOME":tempfile.mkdtemp(prefix="forge-mcp-home-")})
    try:
        responses=[json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
        count=len(responses[1]["result"]["tools"])
        passed=completed.returncode==0 and responses[0]["result"]["protocolVersion"]=="2025-11-25" and count>=18
    except Exception: count=0; passed=False
    if not passed: errors.append("MCP handshake/inventory failed")
    return {"result":"PASS" if passed else "FAIL","tools":count,"stderr":completed.stderr}


def validate_powershell(errors: list[str], warnings: list[str]) -> dict[str, Any]:
    files=sorted(ROOT.glob("*.ps1"))+sorted((ROOT/"workers").glob("*.ps1"))
    findings=[]
    for path in files:
        text=path.read_text(encoding="utf-8-sig")
        if re.search(r"Invoke-Expression|\biex\b",text,re.I): findings.append(f"dynamic expression execution: {path.name}")
        if re.search(r"SkyrimForge\.Native\s+2\.",text): findings.append(f"stale native version: {path.name}")
        # Simple delimiter scan after removing strings/comments is not a parser, but catches accidental truncation.
        scrub=re.sub(r"(?m)#.*$|'(?:''|[^'])*'|\"(?:`.|[^\"])*\"","",text)
        for left,right in (("{","}"),("(",")")):
            if scrub.count(left)!=scrub.count(right): findings.append(f"unbalanced {left}{right}: {path.name}")
    if findings: errors.extend(findings)
    warnings.append("PowerShell syntax is statically screened here; Windows CI performs the real PowerShell parser and installer smoke test")
    return {"result":"PASS" if not findings else "FAIL","files":[p.name for p in files],"findings":findings}


def portable(value: Any) -> Any:
    if isinstance(value,dict): return {k:portable(v) for k,v in value.items()}
    if isinstance(value,list): return [portable(v) for v in value]
    if isinstance(value,str): return value.replace(str(ROOT),"<REPOSITORY_ROOT>").replace(str(Path.home()),"<HOME>").replace(tempfile.gettempdir(),"<TEMP>")
    return value


def manifest() -> dict[str, Any]:
    return {"product":"Skyrim Forge","version":VERSION,"files":[{"path":p.relative_to(ROOT).as_posix(),"size":p.stat().st_size,"sha256":sha256(p),"executable":bool(p.stat().st_mode & 0o111)} for p in repository_files()]}


def write_reports(report: dict[str, Any]) -> None:
    report=portable(report); (ROOT/"VALIDATION.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    man=manifest(); (ROOT/"MANIFEST.json").write_text(json.dumps(man,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    binaries=[ROOT/"writer"/"published"/"linux-x64"/"SkyrimForge.Native",ROOT/"writer"/"published"/"win-x64"/"SkyrimForge.Native.exe"]
    (ROOT/"CHECKSUMS-SHA256.txt").write_text("\n".join(f"{sha256(p)}  {p.relative_to(ROOT).as_posix()}" for p in binaries)+"\n",encoding="utf-8")
    receipt={"product":"Skyrim Forge","version":VERSION,"result":report["result"],"native":report["checks"]["native"],"go":report["checks"]["go"],"mcp":report["checks"]["mcp"],"limitations":["Windows native helper and PowerShell installers require Windows execution; GitHub CI performs that gate.","Installed xEdit, MO2, LOOT, Wrye Bash, Creation Kit, CKPE, and Papyrus tools require local configuration and legal installations.","No Skyrim runtime, save, visual, navmesh, animation, or gameplay validation was performed in this environment."]}
    (ROOT/"BUILD-RECEIPT.json").write_text(json.dumps(portable(receipt),indent=2,sort_keys=True)+"\n",encoding="utf-8")
    sbom={"spdxVersion":"SPDX-2.3","dataLicense":"CC0-1.0","SPDXID":"SPDXRef-DOCUMENT","name":f"Skyrim-Forge-{VERSION}","documentNamespace":f"https://example.invalid/skyrim-forge/{VERSION}/spdx","creationInfo":{"created":"2026-07-23T00:00:00Z","creators":[f"Tool: Skyrim Forge validator {VERSION}"]},"packages":[{"name":"Skyrim Forge","SPDXID":"SPDXRef-Package","versionInfo":VERSION,"downloadLocation":"NOASSERTION","filesAnalyzed":True,"licenseConcluded":"MIT","licenseDeclared":"MIT","copyrightText":"NOASSERTION"}],"files":[{"fileName":"./"+f["path"],"SPDXID":"SPDXRef-File-"+re.sub(r"[^A-Za-z0-9.-]","-",f["path"]),"checksums":[{"algorithm":"SHA256","checksumValue":f["sha256"]}],"licenseConcluded":"NOASSERTION","licenseInfoInFiles":["NOASSERTION"],"copyrightText":"NOASSERTION"} for f in man["files"]]}
    (ROOT/"SBOM.spdx.json").write_text(json.dumps(sbom,indent=2,sort_keys=True)+"\n",encoding="utf-8")


def validate() -> dict[str, Any]:
    errors=[]; warnings=[]; checks={}
    checks["files"]=validate_files(errors,warnings)
    checks["powershell"]=validate_powershell(errors,warnings)
    checks["python"]=validate_python(errors)
    checks["native"]=validate_native(errors,warnings)
    checks["go"]=validate_go(errors,warnings)
    checks["packaging"]=validate_packaging(errors)
    checks["mcp"]=validate_mcp(errors)
    return {"product":"Skyrim Forge","version":VERSION,"result":"PASS" if not errors else "FAIL","errors":sorted(set(errors)),"warnings":sorted(set(warnings)),"checks":checks}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--write-reports",action="store_true"); parser.add_argument("--ci",action="store_true"); args=parser.parse_args()
    report=validate()
    if args.write_reports: write_reports(report)
    print(json.dumps(portable(report),indent=2,sort_keys=True))
    return 0 if report["result"]=="PASS" else 1

if __name__=="__main__": raise SystemExit(main())
