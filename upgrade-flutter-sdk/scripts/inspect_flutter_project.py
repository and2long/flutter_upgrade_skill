#!/usr/bin/env python3
"""Inspect Flutter SDK pins and select major.minor Android/iOS migrations."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


VERSION_RE = re.compile(r"(?<!\d)(\d+)\.(\d+)(?:\.(\d+))?(?!\d)")


@dataclass(frozen=True)
class Detection:
    source: str
    version: str
    path: str
    committed: bool = True

    @property
    def level(self) -> str:
        match = VERSION_RE.search(self.version)
        assert match
        return f"{int(match.group(1))}.{int(match.group(2))}"


def normalize_version(value: str) -> str:
    match = VERSION_RE.search(value)
    if not match:
        raise ValueError(f"not a Flutter version: {value!r}")
    patch = match.group(3)
    return f"{int(match.group(1))}.{int(match.group(2))}" + (
        f".{int(patch)}" if patch is not None else ""
    )


def version_tuple(value: str) -> tuple[int, int]:
    match = VERSION_RE.search(value)
    if not match:
        raise ValueError(f"not a Flutter version: {value!r}")
    return int(match.group(1)), int(match.group(2))


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError, OSError):
        return None


def add_match(
    found: list[Detection],
    root: Path,
    relative: str,
    source: str,
    pattern: str,
    committed: bool = True,
) -> None:
    text = read_text(root / relative)
    if text is None:
        return
    match = re.search(pattern, text, re.MULTILINE)
    if match:
        found.append(
            Detection(source, normalize_version(match.group(1)), relative, committed)
        )


def detect_versions(root: Path) -> list[Detection]:
    found: list[Detection] = []
    add_match(found, root, ".tool-versions", "asdf", r"^flutter\s+([^\s]+)")

    for relative, key, source in (
        (".fvmrc", "flutter", "fvm"),
        (".fvm/fvm_config.json", "flutterSdkVersion", "fvm-legacy"),
    ):
        text = read_text(root / relative)
        if text:
            try:
                value = json.loads(text).get(key)
            except json.JSONDecodeError:
                value = None
            if isinstance(value, str) and VERSION_RE.search(value):
                found.append(Detection(source, normalize_version(value), relative))

    pubspec = read_text(root / "pubspec.yaml")
    if pubspec:
        env_match = re.search(
            r"(?ms)^environment:\s*\n(?P<body>(?:^[ \t]+.*(?:\n|$))*)", pubspec
        )
        if env_match:
            flutter_match = re.search(
                r"(?m)^\s+flutter:\s*[\"']?([^\s\"']+)", env_match.group("body")
            )
            if flutter_match and VERSION_RE.search(flutter_match.group(1)):
                found.append(
                    Detection(
                        "pubspec-environment-flutter",
                        normalize_version(flutter_match.group(1)),
                        "pubspec.yaml",
                    )
                )

    add_match(
        found,
        root,
        ".vscode/settings.json",
        "vscode-sdk-path",
        r'"dart\.flutterSdkPath"\s*:\s*"[^"]*?((?:\d+\.){2}\d+)[^"]*"',
    )
    add_match(
        found,
        root,
        "android/local.properties",
        "android-local-properties",
        r"^flutter\.sdk=.*?((?:\d+\.){2}\d+)[^\n]*$",
        False,
    )

    ci_dir = root / "ios" / "ci_scripts"
    if ci_dir.is_dir():
        for path in sorted(ci_dir.glob("*.sh")):
            text = read_text(path)
            if not text:
                continue
            match = re.search(
                r"(?:git\s+clone[^\n]*\s-b\s+|flutter-version(?:=|\s+))[\"']?((?:\d+\.){2}\d+)",
                text,
            )
            if match:
                found.append(
                    Detection(
                        "ios-ci",
                        normalize_version(match.group(1)),
                        str(path.relative_to(root)),
                    )
                )

    return found


def active_flutter_detection(root: Path) -> Detection | None:
    try:
        result = subprocess.run(
            ["flutter", "--version", "--machine"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        payload = json.loads(result.stdout)
        value = payload.get("frameworkVersion")
        if result.returncode == 0 and isinstance(value, str) and VERSION_RE.search(value):
            return Detection("active-flutter-command", normalize_version(value), "PATH", False)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        pass
    return None


def choose_current(detections: list[Detection]) -> Detection | None:
    priority = {
        "fvm": 0,
        "fvm-legacy": 1,
        "asdf": 2,
        "pubspec-environment-flutter": 3,
        "vscode-sdk-path": 4,
        "ios-ci": 5,
        "android-local-properties": 6,
        "active-flutter-command": 99,
    }
    return min(detections, key=lambda item: priority.get(item.source, 50), default=None)


def load_rules() -> list[dict]:
    rules_path = Path(__file__).resolve().parent.parent / "references" / "migrations.json"
    with rules_path.open(encoding="utf-8") as stream:
        return json.load(stream)["levels"]


def crossed_rules(current: str, target: str, rules: Iterable[dict]) -> list[dict]:
    current_level = version_tuple(current)
    target_level = version_tuple(target)
    if target_level < current_level:
        return []
    return [
        rule
        for rule in rules
        if current_level < version_tuple(rule["version"]) <= target_level
    ]


def inspect(root: Path, target: str | None, include_active: bool) -> dict:
    root = root.resolve()
    detections = detect_versions(root)
    if include_active or not detections:
        active = active_flutter_detection(root)
        if active:
            detections.append(active)

    current = choose_current(detections)
    target_version = normalize_version(target) if target else None
    levels = sorted({item.level for item in detections if item.committed}, key=version_tuple)
    conflict = len(levels) > 1
    migrations: list[dict] = []
    downgrade = False
    patch_only = False
    unknown_levels: list[str] = []

    if current and target_version:
        downgrade = version_tuple(target_version) < version_tuple(current.version)
        patch_only = (
            version_tuple(target_version) == version_tuple(current.version)
            and target_version != current.version
        )
        migrations = crossed_rules(current.version, target_version, load_rules())
        if not downgrade and version_tuple(target_version) != version_tuple(current.version):
            known = {rule["version"] for rule in load_rules()}
            target_level = f"{version_tuple(target_version)[0]}.{version_tuple(target_version)[1]}"
            if target_level not in known:
                unknown_levels = [target_level]

    return {
        "project": str(root),
        "has_pubspec": (root / "pubspec.yaml").is_file(),
        "platforms": {
            "android": (root / "android").is_dir(),
            "ios": (root / "ios").is_dir(),
        },
        "detections": [asdict(item) | {"level": item.level} for item in detections],
        "selected_current": asdict(current) | {"level": current.level} if current else None,
        "target": target_version,
        "target_level": f"{version_tuple(target_version)[0]}.{version_tuple(target_version)[1]}"
        if target_version
        else None,
        "version_conflict": conflict,
        "downgrade": downgrade,
        "patch_only": patch_only,
        "migrations": migrations,
        "uncataloged_levels": unknown_levels,
    }


def render_text(report: dict) -> str:
    lines = [f"Project: {report['project']}"]
    platforms = [name for name, exists in report["platforms"].items() if exists]
    lines.append(f"Platforms in scope: {', '.join(platforms) or 'none'}")
    lines.append("Detected Flutter versions:")
    if report["detections"]:
        for item in report["detections"]:
            kind = "committed" if item["committed"] else "environment fallback"
            lines.append(
                f"  - {item['version']} (level {item['level']}) from {item['path']} "
                f"[{item['source']}, {kind}]"
            )
    else:
        lines.append("  - none")

    selected = report["selected_current"]
    lines.append(
        f"Selected current: {selected['version']} from {selected['path']}"
        if selected
        else "Selected current: unknown"
    )
    if report["target"]:
        lines.append(f"Target: {report['target']} (level {report['target_level']})")
    if report["version_conflict"]:
        lines.append("WARNING: committed version sources disagree; reconcile before editing.")
    if report["downgrade"]:
        lines.append("WARNING: target major.minor is older; automatic reverse migration is disabled.")
    elif report["patch_only"]:
        lines.append("Patch-only change: synchronize explicit pins; no platform migration applies.")

    if report["migrations"]:
        lines.append("Migration levels to apply:")
        for rule in report["migrations"]:
            lines.append(f"  - {rule['version']}: {rule['title']}")
            lines.extend(f"      * {item}" for item in rule["summary"])
    elif report["target"] and selected and not report["downgrade"]:
        lines.append("Migration levels to apply: none")

    if report["uncataloged_levels"]:
        lines.append(
            "Uncataloged crossed levels (research official notes/template deltas): "
            + ", ".join(report["uncataloged_levels"])
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", nargs="?", default=".", help="Flutter project root")
    parser.add_argument("--target", help="Target Flutter version, for example 3.38.10")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument(
        "--include-active",
        action="store_true",
        help="Also report the Flutter executable on PATH even when project pins exist",
    )
    args = parser.parse_args()
    root = Path(args.project)
    if not root.is_dir():
        parser.error(f"project directory does not exist: {root}")
    try:
        report = inspect(root, args.target, args.include_active)
    except ValueError as error:
        parser.error(str(error))

    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_text(report))
    if not report["has_pubspec"]:
        print("ERROR: pubspec.yaml not found; this does not look like a Flutter project.", file=sys.stderr)
        return 2
    if report["selected_current"] is None:
        print("ERROR: unable to determine the current Flutter version.", file=sys.stderr)
        return 3
    if report["version_conflict"]:
        return 4
    if report["downgrade"]:
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
