#!/usr/bin/env python3
"""Benchmark repeatable Xcode build scenarios and preserve JSON/Markdown evidence."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


SCENARIOS = ("clean", "cached-clean", "zero-change", "incremental")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--workspace", type=Path)
    source.add_argument("--project", type=Path)
    parser.add_argument("--scheme", required=True)
    parser.add_argument("--configuration", default="Debug")
    parser.add_argument("--destination", default="generic/platform=iOS Simulator")
    parser.add_argument("--sdk", default="iphonesimulator")
    parser.add_argument("--scenario", choices=SCENARIOS, action="append")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--touch-file", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(".build-benchmark"))
    parser.add_argument("--extra-arg", action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def validate(options: argparse.Namespace) -> list[str]:
    if options.runs < 1:
        raise ValueError("--runs must be at least 1")
    scenarios = options.scenario or ["clean", "zero-change"]
    if "incremental" in scenarios and options.touch_file is None:
        raise ValueError("--touch-file is required for the incremental scenario")
    source = options.workspace or options.project
    if source is None or not source.exists():
        raise ValueError(f"project input does not exist: {source}")
    if options.touch_file is not None and not options.touch_file.exists():
        raise ValueError(f"touch file does not exist: {options.touch_file}")
    return list(dict.fromkeys(scenarios))


def build_command(options: argparse.Namespace, derived_data: Path, action: str = "build") -> list[str]:
    command = ["xcodebuild"]
    if options.workspace:
        command.extend(["-workspace", str(options.workspace.resolve())])
    else:
        command.extend(["-project", str(options.project.resolve())])
    command.extend([
        "-scheme", options.scheme,
        "-configuration", options.configuration,
        "-sdk", options.sdk,
        "-destination", options.destination,
        "-derivedDataPath", str(derived_data),
        "-showBuildTimingSummary",
    ])
    command.extend(options.extra_arg)
    command.append(action)
    return command


def run(command: list[str], log_path: Path) -> tuple[int, float]:
    started = time.monotonic()
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    elapsed = time.monotonic() - started
    log_path.write_text(result.stdout + result.stderr, encoding="utf-8")
    return result.returncode, elapsed


def summary(values: list[float]) -> dict[str, float]:
    return {
        "median_seconds": round(statistics.median(values), 3),
        "minimum_seconds": round(min(values), 3),
        "maximum_seconds": round(max(values), 3),
    }


def benchmark_scenario(
    options: argparse.Namespace,
    scenario: str,
    artifact_dir: Path,
) -> dict[str, object]:
    records: list[dict[str, object]] = []
    shared_derived = artifact_dir / "DerivedData" / scenario
    shared_derived.mkdir(parents=True, exist_ok=True)

    if scenario in {"zero-change", "incremental", "cached-clean"}:
        warm_log = artifact_dir / f"{scenario}-warmup.log"
        code, elapsed = run(build_command(options, shared_derived), warm_log)
        if code != 0:
            raise RuntimeError(f"{scenario} warm-up failed; inspect {warm_log}")
        records.append({"kind": "warmup", "seconds": round(elapsed, 3), "log": warm_log.name})

    for index in range(1, options.runs + 1):
        if scenario == "clean":
            derived_context = tempfile.TemporaryDirectory(prefix="ios-build-benchmark-")
            derived_data = Path(derived_context.name)
        else:
            derived_context = None
            derived_data = shared_derived
        try:
            if scenario == "cached-clean":
                clean_log = artifact_dir / f"{scenario}-{index}-clean.log"
                code, _ = run(build_command(options, derived_data, "clean"), clean_log)
                if code != 0:
                    raise RuntimeError(f"cached-clean preparation failed; inspect {clean_log}")
            if scenario == "incremental" and options.touch_file is not None:
                options.touch_file.touch()
            log = artifact_dir / f"{scenario}-{index}.log"
            code, elapsed = run(build_command(options, derived_data), log)
            records.append({
                "kind": "measurement",
                "run": index,
                "seconds": round(elapsed, 3),
                "exit_code": code,
                "log": log.name,
            })
            if code != 0:
                raise RuntimeError(f"{scenario} run {index} failed; inspect {log}")
        finally:
            if derived_context is not None:
                derived_context.cleanup()

    measurements = [float(record["seconds"]) for record in records if record["kind"] == "measurement"]
    return {"scenario": scenario, "runs": records, "summary": summary(measurements)}


def markdown_report(payload: dict[str, object]) -> str:
    lines = [
        "# Xcode Build Benchmark",
        "",
        f"Created: `{payload['created_at']}`",
        f"Command contract: `{payload['command_contract']}`",
        "",
        "| Scenario | Median | Min | Max |",
        "| --- | ---: | ---: | ---: |",
    ]
    for result in payload["results"]:  # type: ignore[index]
        values = result["summary"]
        lines.append(
            f"| {result['scenario']} | {values['median_seconds']:.3f}s | "
            f"{values['minimum_seconds']:.3f}s | {values['maximum_seconds']:.3f}s |"
        )
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "- Fresh-DerivedData clean builds do not guarantee a cold machine-wide compilation cache.",
        "- Cached-clean results preserve machine cache state and therefore describe this machine, toolchain, and command only.",
        "- Compare changes only with the same scheme, configuration, destination, SDK, machine, toolchain, and scenario.",
        "- A successful benchmark proves compilation for this contract, not runtime, archive, TestFlight, or production behavior.",
    ])
    return "\n".join(lines)


def main() -> int:
    options = parse_args()
    try:
        scenarios = validate(options)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    command_preview = build_command(options, Path("<DERIVED_DATA>"))
    if options.dry_run:
        print(" ".join(command_preview))
        print(f"Scenarios: {', '.join(scenarios)}; runs: {options.runs}")
        return 0
    if shutil.which("xcodebuild") is None:
        print("error: xcodebuild is not available", file=sys.stderr)
        return 3

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_dir = options.output_dir.resolve() / timestamp
    artifact_dir.mkdir(parents=True, exist_ok=False)
    payload: dict[str, object] = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "command_contract": " ".join(command_preview),
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "xcodebuild": subprocess.run(
                ["xcodebuild", "-version"], check=False, capture_output=True, text=True
            ).stdout.strip(),
        },
        "results": [],
    }
    try:
        payload["results"] = [
            benchmark_scenario(options, scenario, artifact_dir) for scenario in scenarios
        ]
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 4
    json_path = artifact_dir / "benchmark.json"
    report_path = artifact_dir / "report.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report_path.write_text(markdown_report(payload), encoding="utf-8")
    shutil.rmtree(artifact_dir / "DerivedData", ignore_errors=True)
    print(f"Benchmark JSON: {json_path}")
    print(f"Benchmark report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
