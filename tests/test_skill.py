from __future__ import annotations

import importlib.util
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

    def test_swift_6_starter_uses_swift_testing(self) -> None:
        test_source = (
            ROOT / "assets" / "native-ios-starter" / "Tests" / "APIClientTests.swift"
        ).read_text(encoding="utf-8")
        self.assertIn("import Testing", test_source)
        self.assertIn("#expect", test_source)
        self.assertIn("#require", test_source)
        self.assertNotIn("import XCTest", test_source)


if __name__ == "__main__":
    unittest.main()
