from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .strictjson import load

KID_TYPES = {
    "Weapon", "Armor", "Ammo", "Magic Effect", "Potion", "Scroll", "Location", "Ingredient",
    "Book", "Misc Item", "Key", "Soul Gem", "Spell", "Activator", "Flora", "Furniture", "Race",
    "Talking Activator", "Enchantment",
}
KID_SIGNATURES = {"WEAP", "ARMO", "AMMO", "MGEF", "ALCH", "SCRL", "LCTN", "INGR", "BOOK", "MISC", "KEYM", "SLGM", "SPEL", "ACTI", "FLOR", "FURN", "RACE", "TACT", "ENCH"}
SPID_TYPES = {"Form", "Spell", "Perk", "Item", "Shout", "LevSpell", "Package", "Outfit", "Keyword", "Faction", "SleepOutfit", "Skin"}
SPID_TRAITS = {"M", "-F", "F", "-M", "U", "-U", "S", "-S", "C", "-C", "L", "-L", "T", "-T", "D", "-D"}
SKYPATCHER_CATEGORIES = {"npc", "weapon", "armor", "ammo", "race", "spell", "scroll", "alchemy", "book", "cell", "constructibleobject", "container", "enchantment", "formlist", "leveledlist", "location", "magiceffect", "other"}
BOS_SECTIONS = {"forms", "references", "transforms", "properties"}


def _strip_inline_comment(line: str) -> str:
    quote = ""
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char in {'"', "'"}:
            if not quote:
                quote = char
            elif quote == char:
                quote = ""
            continue
        if char == ";" and not quote:
            return line[:index].rstrip()
    return line.rstrip()


def _active(path: Path) -> list[tuple[int, str]]:
    result = []
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        line = _strip_inline_comment(raw).strip()
        if line and not line.startswith((";", "#", "//")):
            result.append((number, line))
    return result


def _spid_key(key: str) -> tuple[str, str]:
    if key == "ExclusiveGroup":
        return "exclusive", key
    work = key
    linked = False
    if work.startswith("Linked"):
        linked = True
        work = work[6:]
    final = False
    if work.startswith("Final"):
        final = True
        work = work[5:]
    death = False
    if work.startswith("Death"):
        death = True
        work = work[5:]
    if work not in SPID_TYPES:
        return "invalid", work
    return "linked" if linked else "ordinary", work


def _lint_spid(path: Path) -> list[dict[str, Any]]:
    issues = []
    for number, line in _active(path):
        if line.startswith("["):
            continue
        if "=" not in line:
            issues.append({"severity": "error", "line": number, "message": "SPID line lacks ="})
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        family, base = _spid_key(key)
        fields = [part.strip() for part in value.split("|")]
        if family == "invalid":
            issues.append({"severity": "error", "line": number, "message": f"Invalid SPID key {key!r}"})
            continue
        expected = (2, 2) if family == "exclusive" else ((1, 4) if family == "linked" else (1, 7))
        if not expected[0] <= len(fields) <= expected[1]:
            issues.append({"severity": "error", "line": number, "message": f"SPID {key} expects {expected[0]}-{expected[1]} fields; found {len(fields)}"})
            continue
        if family == "ordinary":
            fields += [""] * (7 - len(fields))
            level, traits, count, chance = fields[3], fields[4], fields[5], fields[6]
            if level and level.upper() != "NONE":
                for token in level.split(","):
                    token = token.strip()
                    if "/" in token:
                        parts = token.split("/")
                        if len(parts) != 2 or not all(parts) or not all(part.isdigit() for part in parts):
                            issues.append({"severity": "error", "line": number, "message": f"Malformed SPID level range {token!r}"})
            if traits and traits.upper() != "NONE":
                for token in traits.split("/"):
                    if token.strip() not in SPID_TRAITS:
                        issues.append({"severity": "error", "line": number, "message": f"Invalid SPID trait {token.strip()!r}"})
            if chance and chance.upper() != "NONE":
                if not re.fullmatch(r"\d+(?:\.\d+)?!?", chance):
                    issues.append({"severity": "error", "line": number, "message": f"Invalid SPID chance {chance!r}"})
                else:
                    numeric = float(chance.rstrip("!"))
                    if not 0 <= numeric <= 100:
                        issues.append({"severity": "error", "line": number, "message": f"SPID chance outside 0-100: {chance!r}"})
    return issues


def _lint_kid(path: Path) -> list[dict[str, Any]]:
    issues = []
    for number, line in _active(path):
        if line.startswith("["):
            continue
        if "=" not in line:
            issues.append({"severity": "error", "line": number, "message": "KID line lacks ="})
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        fields = [part.strip() for part in value.split("|")]
        if key == "ExclusiveGroup":
            if len(fields) != 2 or not all(fields):
                issues.append({"severity": "error", "line": number, "message": "KID ExclusiveGroup requires Group|KeywordList"})
            continue
        if key != "Keyword":
            issues.append({"severity": "error", "line": number, "message": f"Invalid KID key {key!r}"})
            continue
        if not 2 <= len(fields) <= 5:
            issues.append({"severity": "error", "line": number, "message": f"KID Keyword requires 2-5 fields; found {len(fields)}"})
            continue
        fields += [""] * (5 - len(fields))
        if fields[1] in KID_SIGNATURES:
            issues.append({"severity": "error", "line": number, "message": f"KID record signature {fields[1]!r} is invalid here; use the exact human-readable type label"})
        elif fields[1] not in KID_TYPES:
            issues.append({"severity": "error", "line": number, "message": f"Unsupported KID type label {fields[1]!r}"})
        if fields[4]:
            try:
                chance = float(fields[4])
                if not 0 <= chance <= 100:
                    raise ValueError
            except ValueError:
                issues.append({"severity": "error", "line": number, "message": f"Invalid KID chance {fields[4]!r}"})
    return issues


def _lint_bos(path: Path) -> list[dict[str, Any]]:
    issues = []
    section = ""
    transform = re.compile(r"(?:pos[RA]|rot[RA])\(([^)]*)\)", re.I)
    for number, line in _active(path):
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].split("|", 1)[0].strip().casefold()
            if section not in BOS_SECTIONS:
                issues.append({"severity": "warning", "line": number, "message": f"Unknown BOS section {section!r}"})
            continue
        if section not in BOS_SECTIONS:
            continue
        for match in transform.finditer(line):
            arguments = match.group(1)
            if re.search(r"\s", arguments):
                issues.append({"severity": "error", "line": number, "message": f"BOS transform arguments contain whitespace and will split: {match.group(0)!r}"})
            if len(arguments.split(",")) != 3:
                issues.append({"severity": "error", "line": number, "message": f"BOS transform requires three arguments: {match.group(0)!r}"})
    return issues


def _lint_cdf(path: Path) -> list[dict[str, Any]]:
    issues = []
    try:
        root = load(path)
    except Exception as exc:
        return [{"severity": "error", "line": 0, "message": str(exc)}]
    if not isinstance(root, dict) or not isinstance(root.get("rules"), list):
        return [{"severity": "error", "line": 0, "message": "CDF root.rules must be an array"}]
    for ri, rule in enumerate(root["rules"]):
        if not isinstance(rule, dict) or not isinstance(rule.get("changes"), list):
            issues.append({"severity": "error", "line": 0, "message": f"CDF rules[{ri}].changes must be an array"})
            continue
        for ci, change in enumerate(rule["changes"]):
            if not isinstance(change, dict):
                issues.append({"severity": "error", "line": 0, "message": f"CDF rules[{ri}].changes[{ci}] must be an object"})
                continue
            add = change.get("add")
            if add is not None:
                if not isinstance(add, list) or not all(isinstance(item, str) for item in add):
                    issues.append({"severity": "error", "line": 0, "message": f"CDF rules[{ri}].changes[{ci}].add must be a string array"})
                else:
                    for item in add:
                        if item.startswith("*"):
                            issues.append({"severity": "error", "line": 0, "message": f"CDF wildcard-like add form is unsupported: {item!r}"})
    return issues


def _lint_skypatcher(path: Path) -> list[dict[str, Any]]:
    parts = [part.casefold() for part in path.parts]
    issues = []
    if "skypatcher" in parts:
        index = parts.index("skypatcher")
        if index + 1 >= len(parts) - 1 or parts[index + 1] not in SKYPATCHER_CATEGORIES:
            issues.append({"severity": "error", "line": 0, "message": "SkyPatcher config is not inside a supported category directory"})
    return issues


def lint_file(path: Path) -> list[dict[str, Any]]:
    name = path.name.casefold()
    if name.endswith("_distr.ini"):
        return _lint_spid(path)
    if name.endswith("_kid.ini"):
        return _lint_kid(path)
    if name.endswith("_swap.ini"):
        return _lint_bos(path)
    if path.suffix.casefold() == ".json" and "cdf" in name:
        return _lint_cdf(path)
    if path.suffix.casefold() in {".ini", ".json"} and "skypatcher" in [part.casefold() for part in path.parts]:
        return _lint_skypatcher(path)
    return []


def lint_paths(paths: list[Path]) -> dict[str, Any]:
    files = []
    for path in paths:
        if path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file() and item.suffix.casefold() in {".ini", ".json"})
        else:
            files.append(path)
    reports = []
    errors = warnings = 0
    for path in sorted(set(files), key=lambda p: p.as_posix().casefold()):
        issues = lint_file(path)
        if issues:
            reports.append({"path": str(path), "issues": issues})
        errors += sum(item["severity"] == "error" for item in issues)
        warnings += sum(item["severity"] == "warning" for item in issues)
    return {
        "result": "PASS" if errors == 0 else "FAIL",
        "files_scanned": len(set(files)),
        "errors": errors,
        "warnings": warnings,
        "reports": reports,
        "evidence": "Static framework grammar and placement validation. Runtime form resolution and logs remain separate.",
    }


def self_test() -> dict[str, Any]:
    import tempfile
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        good = root / "good_DISTR.ini"
        good.write_text("DeathItem = 0x123~A.esp||||||18! ; comment\nExclusiveGroup = G|0x123~A.esp\n", encoding="utf-8")
        bad = root / "bad_DISTR.ini"
        bad.write_text("Weapon = 0x1~A.esp|||65/|||10\n", encoding="utf-8")
        kid = root / "test_KID.ini"
        kid.write_text("ExclusiveGroup = G|A,B\nKeyword = MyKeyword|Weapon|||100\n", encoding="utf-8")
        kid_bad = root / "bad_KID.ini"
        kid_bad.write_text("Keyword = MyKeyword|WEAP|||100\n", encoding="utf-8")
        bos = root / "test_SWAP.ini"
        bos.write_text("[Transforms]\n0x1~A.esp|rotR(147.9, 355.9, 82.7)\n", encoding="utf-8")
        assertions = {
            "spid_special_keys": not _lint_spid(good),
            "spid_invalid_weapon_and_range": bool(_lint_spid(bad)),
            "kid_exclusive_and_type": not _lint_kid(kid),
            "kid_signature_rejected": bool(_lint_kid(kid_bad)),
            "bos_whitespace_rejected": bool(_lint_bos(bos)),
        }
        return {"result": "PASS" if all(assertions.values()) else "FAIL", "assertions": assertions}
