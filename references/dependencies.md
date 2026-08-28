# Standalone and Optional Dependencies

The bundled references, scripts, and starter form the complete standalone baseline. Never stop merely because another named skill is unavailable.

| Domain | Built-in baseline | Optional accelerator |
| --- | --- | --- |
| SwiftUI | `swiftui-quality-and-tracing.md` | `$swiftui-expert-skill`, `$build-ios-apps:swiftui-performance-audit` |
| Concurrency | `swift-concurrency-and-isolation.md` | `$swift-concurrency` |
| Testing | `testing-strategy.md` | `$swift-testing-expert` |
| Build performance | `build-performance.md` | `$xcode-build-orchestrator` and its specialists |
| Core Data | `persistence-selection.md` | `$core-data-expert` |
| Release | `release-and-evidence.md` | `$ios-shipping-preflight`, App Review, and Greenlight skills |

When an optional skill is absent, apply the built-in reference and report only the missing automation or depth—not the entire task as blocked. Never invent an unavailable skill's scripts, paths, or outputs.

External command-line tools are conditional:

- Python 3 is required for the bundled helper scripts.
- `xcodebuild` and an installed iOS SDK are required for `benchmark_xcode_builds.py`; `--dry-run` only validates the command contract.
- XcodeGen is required only when generating the bundled starter or an XcodeGen project.
- Xcode and its platform SDKs are required for build, Simulator, archive, and signing evidence.
- App Store Connect or provider tooling is required only for the corresponding authenticated external gate.
