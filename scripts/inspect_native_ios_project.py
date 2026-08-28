#!/usr/bin/env python3
"""Print a read-only Markdown inventory of a native iOS project."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path


SKIP_DIRS = {
    ".git", ".build", ".swiftpm", "DerivedData", "Pods", "Carthage",
    "node_modules", ".venv", "build", "Archives", ".revyl",
}
TEXT_NAMES = {"project.yml", "project.yaml", "Package.swift", "Podfile", "Cartfile"}
TEXT_SUFFIXES = {
    ".pbxproj", ".xcworkspacedata", ".plist", ".entitlements",
    ".xcconfig", ".xcprivacy", ".swift",
}
SENSITIVE_SUFFIXES = {".p8", ".p12", ".mobileprovision"}
UF_DATALESS = getattr(stat, "UF_DATALESS", 0x40000000)
PATTERNS = {
    "bundle IDs": re.compile(r"(?:PRODUCT_BUNDLE_IDENTIFIER\s*[:=]|bundleIdPrefix\s*:)[ \t]*[\"']?([^\"'\s;]+)"),
    "Team IDs": re.compile(r"DEVELOPMENT_TEAM\s*[:=][ \t]*[\"']?([A-Z0-9]{10})"),
    "deployment targets": re.compile(r"(?:IPHONEOS_DEPLOYMENT_TARGET\s*[:=]|iOS\s*:)[ \t]*[\"']?([0-9]+(?:\.[0-9]+){1,2})"),
    "marketing versions": re.compile(r"MARKETING_VERSION\s*[:=][ \t]*[\"']?([^\"'\s;]+)"),
    "build numbers": re.compile(r"CURRENT_PROJECT_VERSION\s*[:=][ \t]*[\"']?([^\"'\s;]+)"),
}


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="App or repository root")
    parser.add_argument("--max-files", type=int, default=5000)
    return parser.parse_args()


def candidate_files(root: Path, limit: int) -> list[Path]:
    result: list[Path] = []
    rg = shutil.which("rg")
    if rg:
        command = [rg, "--files", "--hidden"]
        for directory in sorted(SKIP_DIRS):
            command.extend(["-g", f"!{directory}/**", "-g", f"!**/{directory}/**"])
        try:
            output = subprocess.run(
                command,
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
                timeout=15,
            ).stdout.splitlines()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            output = []
        for item in output:
            path = root / item
            if path.name in TEXT_NAMES or path.suffix in TEXT_SUFFIXES or path.suffix in SENSITIVE_SUFFIXES:
                result.append(path)
            if len(result) >= limit:
                return result
        if output:
            return result

    for directory, names, filenames in os.walk(root):
        names[:] = [name for name in names if name not in SKIP_DIRS]
        base = Path(directory)
        for filename in filenames:
            path = base / filename
            if path.name in TEXT_NAMES or path.suffix in TEXT_SUFFIXES or path.suffix in SENSITIVE_SUFFIXES:
                result.append(path)
            if len(result) >= limit:
                return result
    return result


def relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def print_list(title: str, values: list[str]) -> None:
    print(f"\n## {title}")
    if values:
        for value in sorted(set(values)):
            print(f"- `{value}`")
    else:
        print("- Not found")


def main() -> int:
    options = args()
    root = options.root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}")
        return 2

    files = candidate_files(root, options.max_files)
    paths = [relative(path, root) for path in files]
    project_files = [p for p in paths if p.endswith((".xcodeproj/project.pbxproj", ".xcworkspace/contents.xcworkspacedata", "project.yml", "project.yaml", "Package.swift", "Podfile"))]
    manifests = [p for p in paths if p.endswith((".entitlements", ".xcprivacy"))]
    sensitive = [p for p in paths if Path(p).suffix in SENSITIVE_SUFFIXES]
    placeholders: list[str] = []
    findings: dict[str, list[str]] = {key: [] for key in PATTERNS}

    for path in files:
        try:
            metadata = path.stat()
        except OSError:
            continue
        if path.suffix in SENSITIVE_SUFFIXES or metadata.st_size > 2_000_000:
            continue
        if getattr(metadata, "st_flags", 0) & UF_DATALESS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for label, pattern in PATTERNS.items():
            findings[label].extend(match.group(1) for match in pattern.finditer(text))
        if path.suffix in {".swift", ".plist", ".yml", ".yaml"}:
            for line_no, line in enumerate(text.splitlines(), 1):
                if re.search(r"(?i)\b(TODO|FIXME|COMING SOON|PLACEHOLDER)\b", line):
                    placeholders.append(f"{relative(path, root)}:{line_no}")
                    if len(placeholders) >= 50:
                        break

    print("# Native iOS Project Inventory")
    print(f"\nRoot: `{root}`")
    print(f"\nFiles inspected: {len(files)} (limit {options.max_files})")
    print_list("Project inputs", project_files)
    print_list("Entitlements and privacy manifests", manifests)
    for label, values in findings.items():
        print_list(label.capitalize(), values)
    print_list("Sensitive credential files present (contents not read)", sensitive)
    print_list("Placeholder markers requiring review", placeholders)
    print("\n## Evidence boundary")
    print("- This is source inventory only. It does not prove build, signing, runtime, archive, upload, TestFlight, device behavior, or App Store state.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
