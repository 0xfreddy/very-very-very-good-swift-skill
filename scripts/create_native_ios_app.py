#!/usr/bin/env python3
"""Create a minimal native SwiftUI/XcodeGen app from the bundled starter."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


BUNDLE_ID = re.compile(r"^[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")
TEAM_ID = re.compile(r"^[A-Z0-9]{10}$")
DEPLOYMENT_TARGET = re.compile(r"^[0-9]+(?:\.[0-9]+){1,2}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="User-facing app name")
    parser.add_argument("--bundle-id", required=True, help="Production-style bundle ID")
    parser.add_argument("--output", required=True, type=Path, help="New destination directory")
    parser.add_argument("--team-id", help="Optional 10-character Apple Developer Team ID")
    parser.add_argument("--deployment-target", default="17.0", help="Minimum iOS version")
    parser.add_argument("--generate", action="store_true", help="Run xcodegen after creation")
    return parser.parse_args()


def swift_identifier(name: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", name)
    result = "".join(word[:1].upper() + word[1:] for word in words)
    if not result or result[0].isdigit():
        result = f"App{result}"
    return result


def validate(args: argparse.Namespace) -> None:
    if not args.name.strip() or any(ch in args.name for ch in "\r\n"):
        raise ValueError("--name must be a non-empty single line")
    if not BUNDLE_ID.fullmatch(args.bundle_id):
        raise ValueError("--bundle-id must contain at least two dot-separated identifier segments")
    if args.team_id and not TEAM_ID.fullmatch(args.team_id):
        raise ValueError("--team-id must be 10 uppercase letters or digits")
    if not DEPLOYMENT_TARGET.fullmatch(args.deployment_target):
        raise ValueError("--deployment-target must look like 17.0")
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError(f"destination is not empty: {args.output}")


def replace_tokens(root: Path, values: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for token, value in values.items():
            text = text.replace(token, value)
        path.write_text(text, encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        validate(args)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    template = Path(__file__).resolve().parent.parent / "assets" / "native-ios-starter"
    if not template.is_dir():
        print(f"error: starter template missing at {template}", file=sys.stderr)
        return 2

    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, destination, dirs_exist_ok=True)

    swift_name = swift_identifier(args.name)
    team_setting = f'        DEVELOPMENT_TEAM: "{args.team_id}"' if args.team_id else ""
    replace_tokens(
        destination,
        {
            "__APP_NAME__": args.name.strip(),
            "__SWIFT_NAME__": swift_name,
            "__BUNDLE_ID__": args.bundle_id,
            "__DEPLOYMENT_TARGET__": args.deployment_target,
            "__TEAM_SETTING__": team_setting,
        },
    )

    generated = False
    if args.generate:
        executable = shutil.which("xcodegen")
        if not executable:
            print("error: --generate requested but xcodegen is not installed", file=sys.stderr)
            return 3
        subprocess.run([executable, "generate"], cwd=destination, check=True)
        generated = True

    print(f"Created {args.name} at {destination}")
    print(f"Swift target: {swift_name}")
    print(f"Bundle ID: {args.bundle_id}")
    print(f"Xcode project generated: {'yes' if generated else 'no'}")
    print("Next: replace DESIGN.md, add app icons, implement one vertical slice, then build a fresh simulator artifact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
