#!/usr/bin/env python3
"""Audit Swift sources for launch-risk patterns without modifying the project."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse


SKIP_DIRS = {
    ".git", ".build", ".swiftpm", "DerivedData", "Pods", "Carthage",
    "node_modules", ".venv", "build", "Archives", ".revyl",
}


@dataclass(frozen=True)
class Finding:
    category: str
    rule: str
    path: str
    line: int
    evidence: str
    review: str


RULES: tuple[tuple[str, str, re.Pattern[str], str], ...] = (
    (
        "Concurrency",
        "detached-task",
        re.compile(r"\bTask\s*\.\s*detached\b"),
        "Confirm detached execution is required, its result is consumed, and its lifetime and cancellation are owned.",
    ),
    (
        "Concurrency",
        "unchecked-sendable",
        re.compile(r"@unchecked\s+Sendable"),
        "Document the synchronization invariant and a removal plan; do not treat this as proof of thread safety.",
    ),
    (
        "Concurrency",
        "unsafe-nonisolated",
        re.compile(r"nonisolated\s*\(\s*unsafe\s*\)"),
        "Verify the value is immutable or externally synchronized and record why actor checking is bypassed.",
    ),
    (
        "Concurrency",
        "continuation",
        re.compile(r"with(?:Checked|Unsafe)(?:Throwing)?Continuation"),
        "Verify exactly-once resume behavior, cancellation handling, and ownership when the callback never arrives.",
    ),
    (
        "SwiftUI",
        "state-initialized-outside-declaration",
        re.compile(r"@State\s+(?:private\s+)?var\s+\w+\s*:\s*[^=]+$"),
        "Check whether init assigns an injected value. View-owned State should be private and initialized from a true initial value, not used to mirror changing parent input.",
    ),
    (
        "SwiftUI",
        "positional-identity",
        re.compile(r"\bid\s*:\s*\\\.offset\b|ForEach\s*\([^,\n]*\.indices\s*,\s*id\s*:\s*\\\.self"),
        "Use stable domain identity for changing collections; positional identity can attach state or animation to the wrong row.",
    ),
    (
        "SwiftUI",
        "legacy-navigation",
        re.compile(r"\bNavigationView\b|\.navigationBarItems\s*\("),
        "Check the deployment target and prefer NavigationStack/NavigationSplitView and toolbar APIs for new code.",
    ),
    (
        "SwiftUI",
        "unscoped-animation",
        re.compile(r"\.animation\s*\([^,\n\)]*\)"),
        "Prefer animation(_:value:) or an explicit animation so unrelated state changes do not animate accidentally.",
    ),
)

TEST_RULES: tuple[tuple[str, str, re.Pattern[str], str], ...] = (
    (
        "Testing",
        "shared-urlprotocol-state",
        re.compile(r"\bstatic\s+var\s+\w*(?:handler|stub|response|error)\w*", re.IGNORECASE),
        "Mutable static stubs are unsafe under Swift Testing parallelism; inject immutable per-test transports or actors.",
    ),
    (
        "Testing",
        "serialized-test",
        re.compile(r"\.serialized\b"),
        "Require a written product constraint or migration rationale; isolate shared state instead when possible.",
    ),
    (
        "Testing",
        "fixed-wait",
        re.compile(r"\b(?:Task\s*\.\s*sleep|sleep|usleep)\s*\("),
        "Await observable completion instead of relying on wall-clock delay; determine whether this hides a product or fixture race.",
    ),
)

UNSTRUCTURED_TASK_RULE = (
    "Concurrency",
    "unstructured-task-site",
    re.compile(r"(?<![.\w])Task\s*\{"),
    "Record the owner, inherited actor, result/error handling, cancellation trigger, and expected lifetime. This syntax is not inherently wrong.",
)
EXTERNAL_URL = re.compile(r"https?://[^\s\"')]+")
NETWORK_EXECUTION = re.compile(
    r"URLSession(?:\s*\.|\s*\()|\.data\s*\(\s*from\s*:|\.dataTask\s*\(|\.upload\s*\(|\.download\s*\("
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="App or repository root")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--max-files", type=int, default=10000)
    parser.add_argument("--large-body-lines", type=int, default=80)
    parser.add_argument(
        "--include-task-sites",
        action="store_true",
        help="Include ordinary Task { } creation sites as ownership prompts",
    )
    return parser.parse_args()


def swift_files(root: Path, limit: int) -> list[Path]:
    paths: list[Path] = []
    for directory, names, filenames in os.walk(root):
        names[:] = [name for name in names if name not in SKIP_DIRS]
        for filename in filenames:
            if filename.endswith(".swift"):
                paths.append(Path(directory) / filename)
                if len(paths) >= limit:
                    return sorted(paths)
    return sorted(paths)


def is_test_file(path: Path) -> bool:
    return path.name.endswith(("Tests.swift", "Test.swift")) or any(
        component.lower() in {"tests", "test"} or component.lower().endswith("tests")
        for component in path.parts
    )


def compact(line: str, limit: int = 160) -> str:
    value = " ".join(line.strip().split())
    return value if len(value) <= limit else f"{value[: limit - 1]}…"


def skip_match(rule: str, line: str) -> bool:
    if rule == "state-initialized-outside-declaration":
        declaration = line.split("//", 1)[0].strip()
        return declaration.endswith(("?", "!"))
    if rule == "unscoped-animation":
        return ", value:" in line or "TimelineView(" in line
    if rule == "external-url-literal-in-network-capable-test":
        match = re.search(r"https?://[^\s\"')]+", line)
        host = (urlparse(match.group(0)).hostname or "").lower() if match else ""
        return (
            not host
            or host == "localhost"
            or host == "127.0.0.1"
            or host.endswith((".test", ".invalid", ".example", ".example.com"))
            or host == "example.com"
        )
    return False


def large_body_findings(path: Path, root: Path, lines: list[str], threshold: int) -> list[Finding]:
    findings: list[Finding] = []
    start_pattern = re.compile(r"\bvar\s+body\s*:\s*some\s+View\b")
    for index, line in enumerate(lines):
        if not start_pattern.search(line):
            continue
        depth = 0
        opened = False
        end = index
        for cursor in range(index, len(lines)):
            source = re.sub(r"//.*$", "", lines[cursor])
            depth += source.count("{")
            if source.count("{"):
                opened = True
            depth -= source.count("}")
            end = cursor
            if opened and depth <= 0:
                break
        span = end - index + 1
        if span > threshold:
            findings.append(
                Finding(
                    category="SwiftUI",
                    rule="large-view-body",
                    path=str(path.relative_to(root)),
                    line=index + 1,
                    evidence=f"body spans approximately {span} lines",
                    review="Extract meaningful subviews with narrow inputs, then measure type-check and invalidation behavior before claiming improvement.",
                )
            )
    return findings


def audit(
    root: Path,
    max_files: int,
    large_body_lines: int,
    include_task_sites: bool = False,
) -> tuple[list[Path], list[Finding]]:
    files = swift_files(root, max_files)
    findings: list[Finding] = []
    for path in files:
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        active_rules = RULES + TEST_RULES if is_test_file(path) else RULES
        if include_task_sites:
            active_rules += (UNSTRUCTURED_TASK_RULE,)
        relative = str(path.relative_to(root))
        file_rules_seen: set[str] = set()
        for line_number, line in enumerate(lines, 1):
            if line.lstrip().startswith("//"):
                continue
            for category, rule, pattern, review in active_rules:
                if pattern.search(line) and not skip_match(rule, line):
                    findings.append(
                        Finding(category, rule, relative, line_number, compact(line), review)
                    )
                    file_rules_seen.add(rule)
        full_text = "\n".join(lines)
        if is_test_file(path) and NETWORK_EXECUTION.search(full_text):
            for line_number, line in enumerate(lines, 1):
                if not EXTERNAL_URL.search(line) or skip_match(
                    "external-url-literal-in-network-capable-test", line
                ):
                    continue
                findings.append(Finding(
                    "Testing",
                    "external-url-literal-in-network-capable-test",
                    relative,
                    line_number,
                    compact(line),
                    "Determine whether this is inert fixture data or can reach the network. If it can, require an explicitly authorized and separately tagged contract test.",
                ))
                break
        findings.extend(large_body_findings(path, root, lines, large_body_lines))
    return files, sorted(findings, key=lambda item: (item.category, item.path, item.line, item.rule))


def render_markdown(root: Path, files: list[Path], findings: list[Finding]) -> str:
    output = [
        "# Swift Source Audit",
        "",
        f"Root: `{root}`",
        f"Swift files inspected: {len(files)}",
        f"Advisory findings: {len(findings)}",
        "",
        "> Findings are review prompts, not confirmed defects. Verify ownership, deployment target, tests, and runtime behavior before editing.",
    ]
    categories = sorted({finding.category for finding in findings})
    for category in categories:
        output.extend(["", f"## {category}", ""])
        for finding in (item for item in findings if item.category == category):
            output.append(f"- `{finding.path}:{finding.line}` **{finding.rule}** — {finding.evidence}")
            output.append(f"  Review: {finding.review}")
    if not findings:
        output.extend(["", "## Findings", "", "- None found by these heuristics."])
    output.extend([
        "",
        "## Evidence boundary",
        "",
        "- This is a source-pattern audit only. It does not prove a bug, compilation, runtime behavior, performance, cancellation, test isolation, or release readiness.",
    ])
    return "\n".join(output)


def main() -> int:
    options = parse_args()
    root = options.root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    files, findings = audit(
        root,
        options.max_files,
        options.large_body_lines,
        options.include_task_sites,
    )
    if options.format == "json":
        print(json.dumps({
            "schema_version": 1,
            "root": str(root),
            "files_inspected": len(files),
            "findings": [asdict(finding) for finding in findings],
            "evidence_boundary": "Source-pattern audit only; every finding requires verification.",
        }, indent=2))
    else:
        print(render_markdown(root, files, findings))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
