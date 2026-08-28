from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SkillPackageTests(unittest.TestCase):
    def test_frontmatter_and_agent_prompt_match_skill(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        frontmatter = skill.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name: launch-native-ios-app$")
        self.assertRegex(frontmatter, r"(?m)^description: .{80,}$")

        metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn("$launch-native-ios-app", metadata)

    def test_every_routed_reference_exists(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        references = set(re.findall(r"references/[a-z0-9-]+\.md", skill))
        self.assertGreater(len(references), 10)
        missing = [path for path in references if not (ROOT / path).is_file()]
        self.assertEqual(missing, [])

    def test_commands_resolve_scripts_through_skill_dir(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("run `scripts/", skill)
        self.assertIn('$SKILL_DIR/scripts/create_native_ios_app.py', skill)
        self.assertIn('$SKILL_DIR/scripts/inspect_native_ios_project.py', skill)
        self.assertIn('$SKILL_DIR/scripts/audit_swift_sources.py', skill)
        self.assertIn('$SKILL_DIR/scripts/benchmark_xcode_builds.py', skill)

    def test_starter_generation_replaces_tokens_and_preserves_binary_files(self) -> None:
        creator = load_script("create_native_ios_app.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "Template.swift"
            binary = root / "Icon.png"
            source.write_text("struct __SWIFT_NAME__ {}", encoding="utf-8")
            original_binary = b"\x89PNG\r\n\x1a\n__SWIFT_NAME__\x00"
            binary.write_bytes(original_binary)

            creator.replace_tokens(root, {"__SWIFT_NAME__": "ExampleApp"})

            self.assertEqual(source.read_text(encoding="utf-8"), "struct ExampleApp {}")
            self.assertEqual(binary.read_bytes(), original_binary)

    def test_generator_rejects_file_destination_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "existing-file"
            destination.write_text("occupied", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "create_native_ios_app.py"),
                    "--name", "Example App",
                    "--bundle-id", "com.example.app",
                    "--output", str(destination),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("not a directory", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_inventory_discovers_xcode_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "Example.xcworkspace" / "contents.xcworkspacedata"
            workspace.parent.mkdir()
            workspace.write_text("<Workspace version=\"1.0\"></Workspace>", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "inspect_native_ios_project.py"), str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("Example.xcworkspace/contents.xcworkspacedata", result.stdout)

    def test_inventory_distinguishes_bundle_prefix_and_ignores_placeholder_api(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "project.yml").write_text(
                "options:\n  bundleIdPrefix: com.example\nsettings:\n  PRODUCT_BUNDLE_IDENTIFIER: com.example.app\n",
                encoding="utf-8",
            )
            (root / "Widget.swift").write_text(
                "func placeholder(in context: Context) -> Entry { Entry() }\nlet token = \"PLACEHOLDER\"\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "inspect_native_ios_project.py"), str(root)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("## Target bundle ids\n- `com.example.app`", result.stdout)
            self.assertIn("## Bundle id prefixes\n- `com.example`", result.stdout)
            self.assertIn("Widget.swift:2", result.stdout)
            self.assertNotIn("Widget.swift:1", result.stdout)

    def test_swift_6_starter_uses_swift_testing(self) -> None:
        test_source = (
            ROOT / "assets" / "native-ios-starter" / "Tests" / "APIClientTests.swift"
        ).read_text(encoding="utf-8")
        self.assertIn("import Testing", test_source)
        self.assertIn("#expect", test_source)
        self.assertIn("#require", test_source)
        self.assertNotIn("import XCTest", test_source)

    def test_swift_audit_reports_advisory_concurrency_ui_and_test_findings(self) -> None:
        auditor = load_script("audit_swift_sources.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Sources").mkdir()
            (root / "Tests").mkdir()
            (root / "Sources" / "RiskyView.swift").write_text(
                """
                import SwiftUI
                struct RiskyView: View {
                    let values = [1, 2]
                    var body: some View {
                        ForEach(Array(values.enumerated()), id: \\.offset) { _, value in
                            Text(String(value))
                        }
                        .task { Task.detached { print(value) } }
                    }
                }
                """,
                encoding="utf-8",
            )
            (root / "Tests" / "NetworkTests.swift").write_text(
                'let endpoint = "https://api.acme-production.com/v1"\nlet session = URLSession.shared\nstatic var requestHandler: (() -> Void)?\n',
                encoding="utf-8",
            )

            files, findings = auditor.audit(root, 100, 80)
            rules = {finding.rule for finding in findings}

            self.assertEqual(len(files), 2)
            self.assertIn("detached-task", rules)
            self.assertIn("positional-identity", rules)
            self.assertIn("external-url-literal-in-network-capable-test", rules)
            self.assertIn("shared-urlprotocol-state", rules)

    def test_swift_audit_ignores_stable_identity_scoped_animation_and_fixture_hosts(self) -> None:
        auditor = load_script("audit_swift_sources.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Tests").mkdir()
            (root / "Tests" / "SafeTests.swift").write_text(
                """
                @State private var optionalSelection: String?
                let fixture = URL(string: "https://example.com/story")!
                ForEach(Array(values.enumerated()), id: \\.element.id) { _, value in
                    Text(value.name)
                        .animation(.smooth, value: value.name)
                }
                TimelineView(.animation(minimumInterval: 1 / 60)) { _ in Text("tick") }
                """,
                encoding="utf-8",
            )
            _, findings = auditor.audit(root, 100, 80)
            rules = {finding.rule for finding in findings}

            self.assertNotIn("positional-identity", rules)
            self.assertNotIn("unscoped-animation", rules)
            self.assertNotIn("external-url-literal-in-network-capable-test", rules)

    def test_swift_audit_flags_nonoptional_state_initialized_by_init(self) -> None:
        auditor = load_script("audit_swift_sources.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Detail.swift").write_text(
                "@State private var item: Item\ninit(item: Item) { _item = State(initialValue: item) }\n",
                encoding="utf-8",
            )
            _, findings = auditor.audit(root, 100, 80)
            self.assertIn(
                "state-initialized-outside-declaration",
                {finding.rule for finding in findings},
            )

    def test_swift_audit_can_seed_unstructured_task_ledger(self) -> None:
        auditor = load_script("audit_swift_sources.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "Worker.swift"
            source.write_text("func start() { Task { await work() } }", encoding="utf-8")

            _, default_findings = auditor.audit(root, 100, 80)
            _, ledger_findings = auditor.audit(root, 100, 80, include_task_sites=True)

            self.assertNotIn("unstructured-task-site", {item.rule for item in default_findings})
            self.assertIn("unstructured-task-site", {item.rule for item in ledger_findings})

    def test_build_benchmark_dry_run_and_schema_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "Example.xcodeproj"
            project.mkdir()
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "benchmark_xcode_builds.py"),
                    "--project", str(project),
                    "--scheme", "Example",
                    "--scenario", "clean",
                    "--runs", "2",
                    "--dry-run",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("xcodebuild -project", result.stdout)
            self.assertIn("Scenarios: clean; runs: 2", result.stdout)

        schema = json.loads(
            (ROOT / "schemas" / "build-benchmark.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)


if __name__ == "__main__":
    unittest.main()
