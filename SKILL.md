---
name: launch-native-ios-app
description: End-to-end native iOS product engineering for Swift 6, SwiftUI, UIKit, Xcode, and XcodeGen apps—from product contract, architecture, design systems, concurrency, persistence, testing, accessibility, auth, notifications, privacy, and measured performance through signing, App Store Connect, TestFlight, App Review, and launch verification. Use when creating a native iOS app, turning a prototype or DESIGN.md into production SwiftUI, implementing or reviewing launch-critical features, modernizing concurrency or tests, diagnosing build/runtime readiness, optimizing Xcode builds, or preparing and executing a TestFlight/App Store launch.
---

# Launch Native iOS App

Build a native app as a product and release system, not a pile of screens. Preserve a strict chain from user promise to current-source runtime proof to installed release artifact.

Cover only native Swift/SwiftUI/UIKit projects. For Expo, React Native, Flutter, or Kotlin, identify the mismatch and route to that stack's tooling.

## Establish the Contract

Before editing, resolve:

1. The real repository and app root, including nested repositories and generated Xcode projects.
2. The requested outcome: plan, scaffold, implement, diagnose, audit, TestFlight, App Store submission, or production launch.
3. The product's smallest complete user loop and the claims made by its website/store metadata.
4. The minimum iOS version, devices, orientation, account model, backend, offline expectations, and accessibility requirements.
5. The evidence level required at handoff.

Inspect the worktree before changes. Preserve unrelated dirty work and stage only requested paths. Never assume a wrapper directory is the app root.

If creating a new app, settle the production bundle ID before Apple records, auth, APNs, App Groups, associated domains, or provider allowlists. Treat later identity migration as a new integration project.

## Route the Job

- For a new app or major architecture change, read `references/discovery-and-architecture.md` and `references/implementation-and-quality.md`.
- For UI creation, a visual reference, or any `DESIGN.md`, read `references/design-system-and-ui.md`.
- For SwiftUI state, identity, navigation, rendering correctness, or performance, read `references/swiftui-quality-and-tracing.md`; use `$swiftui-expert-skill` for a focused implementation or review and `$build-ios-apps:swiftui-performance-audit` for a source-first performance audit when available.
- For Swift 6 diagnostics, tasks, actors, Sendable, cancellation, or migration, read `references/swift-concurrency-and-isolation.md`; use `$swift-concurrency` for the focused repair when available.
- For test design, XCTest migration, flakes, or CI filtering, read `references/testing-strategy.md`; use `$swift-testing-expert` for detailed Swift Testing work when available.
- For slow Xcode builds, read `references/build-performance.md`; use `$xcode-build-orchestrator` for the measured, approval-gated optimization loop when available.
- For persistence selection or an existing Core Data stack, read `references/persistence-selection.md`; use `$core-data-expert` only when Core Data is actually selected or detected.
- For auth, push, deep links, widgets, entitlements, credentials, or secrets, read `references/platform-services.md`.
- For TestFlight, App Store, App Review, screenshots, signing, privacy, or launch, read `references/release-and-evidence.md` and `references/official-sources.md`.
- For provenance of the specialist patterns integrated here, read `references/specialist-sources.md`.
- For tool selection, read `references/tools-and-routing.md`.
- For the concrete lessons extracted from The Odds News repository, read `references/the-odds-news-lessons.md`.
- For a greenfield XcodeGen app, read `references/starter.md`, then run `scripts/create_native_ios_app.py`.

Do not load every reference automatically. Load the files required by the current phase.

## Execute the Product-to-Launch Loop

### 1. Discover

- Inventory project/workspace files, schemes, targets, packages, deployment targets, configs, bundle IDs, entitlements, privacy manifests, backend environments, and tests.
- Run `scripts/inspect_native_ios_project.py <app-root>` for a fast, read-only inventory; verify its findings against source before acting.
- Identify current state ownership, navigation, networking, persistence, design tokens, auth, notification ownership, and generated-project inputs.
- Separate active production code from demos, web/Vite prototypes, stale installed binaries, and experimental branches.

### 2. Define

- Write a compact acceptance contract: user loop, loading/empty/error/offline states, accessibility, analytics/privacy, and explicit non-goals.
- Map each store/website claim to a reachable feature in the release build.
- Decide native framework boundaries. Prefer SwiftUI for composition, UIKit only where it materially improves behavior, RealityKit for new Apple 3D work, Swift Charts for native charts, and MapKit as the default native map unless requirements justify another renderer.

### 3. Design

- Establish semantic tokens for color, typography, spacing, shape, motion, and haptics before multiplying components.
- Use Apple navigation, sheets, controls, focus, accessibility, and system behaviors unless product requirements justify custom ownership.
- Treat third-party design packs as evidence and inspiration. Reconcile them with the app's own brand, legal rights, platform APIs, accessibility, and deployment target.
- Specify and test light/dark mode, Dynamic Type, VoiceOver order, Reduce Motion, contrast, hit targets, keyboard behavior, safe areas, and interruption.

### 4. Implement in Vertical Slices

- Build one reachable, data-backed user loop at a time.
- Keep view state local, shared observable state explicit, networking typed, cancellation-aware, and testable, and persistence migrations deliberate.
- Confirm Swift language mode and concurrency build settings before migration-sensitive changes. Give every long-lived task an owner, cancellation path, and deallocation expectation; never apply `@MainActor` as a blanket warning suppressor.
- Prefer stable model identity and explicit SwiftUI state ownership. Never use mutable offsets or indices as `ForEach` identity.
- Model loading, empty, stale, error, retry, signed-out, permission-denied, and offline states as first-class UI.
- Keep secrets out of source and app bundles. Public client identifiers are configuration; private keys and server API keys are not.
- When XcodeGen is authoritative, change `project.yml` and regenerate the project after adding files, packages, capabilities, configs, or targets.

### 5. Validate Each Slice

Run the cheapest truthful layer first:

1. Scoped diff and formatter/parse checks.
2. Focused unit/integration tests.
3. Fresh build from current source.
4. Fresh simulator install and interaction.
5. Accessibility and visual checks across required appearances/sizes.
6. Physical-device checks for haptics, APNs, camera, microphone, background delivery, performance, and other hardware behavior.

For new Swift unit and integration tests, prefer Swift Testing when the toolchain supports it. Keep XCTest for UI automation, `XCTMetric`, Objective-C tests, and unsupported cases. Migrate existing suites incrementally; do not rewrite a healthy test suite merely for style.

Make performance claims only from measurements. Audit source before profiling, reproduce the user-visible problem, and compare the same scenario before and after. Treat Simulator, physical-device, build-time, launch-time, UI-hitch, CPU, and memory evidence as different surfaces.

Stop retrying an Xcode environment that stalls before compiler processes. Report the environment prerequisite separately from source correctness.

### 6. Integrate Platform Services

- Configure one environment at a time and maintain an identity matrix for app, extensions, App Groups, auth, push, deep links, and backend allowlists.
- Distinguish APNs, Sign in with Apple, and App Store Connect `.p8` keys. Never print or commit private-key contents.
- Prove login/logout/account switching, deletion, permission denial, deep links, notification cold/background/foreground paths, and extension behavior.
- Validate push and haptics on a physical device; simulator rendering or synthetic push is not delivery proof.

### 7. Prepare the Release

- Use `$ios-shipping-preflight` when available as the focused release conductor.
- Use App Review and Greenlight skills as lenses, not authorities; require exact source/binary/dashboard evidence for each finding.
- Recheck Apple's current official guidance at release time. Do not rely on stale embedded policy prose.
- Remove placeholders, dead controls, hidden screenshot-only features, broken URLs, mismatched claims, and unreachable reviewer paths.
- Prepare review credentials, notes, support/legal URLs, privacy answers, export-compliance answers, screenshots, beta description, and what-to-test text.

### 8. Ship and Prove

Record these gates independently:

| Gate | Required proof |
| --- | --- |
| Source | Scoped diff and checks identify the exact revision |
| Build | Current source compiled for the named configuration |
| Runtime | Fresh artifact installed and required flows interacted with |
| Archive/export | Release archive and exported/upload artifact succeeded |
| Upload | App Store Connect accepted the named version/build |
| Processing | The same build completed processing and compliance blockers |
| TestFlight | A real tester installed the processed build |
| Device | Required physical-device behaviors passed on that build |
| Submission | Correct build and metadata were submitted |
| Review/release | App Review and release state were verified currently |

Never report “launched” when a required gate remains unverified. `Upload succeeded` does not prove TestFlight availability; an installed old binary does not prove current source.

## Use the Greenfield Starter

For a new app:

```bash
python3 scripts/create_native_ios_app.py \
  --name "Example App" \
  --bundle-id "com.example.exampleapp" \
  --output "/absolute/path/ExampleApp" \
  --team-id "ABCDE12345" \
  --generate
```

Omit `--team-id` until known. Omit `--generate` if XcodeGen is unavailable. The starter intentionally excludes auth, analytics, push, payments, and third-party SDKs; add them only after choosing providers and privacy ownership.

## Apply Mutation Boundaries

- A request to review, explain, or diagnose authorizes inspection, not implementation, upload, submission, credential creation, or dashboard mutation.
- A request to build authorizes local source/project changes and proportionate local verification, not App Store Connect creation or production release.
- A request to upload or launch authorizes only the named app/environment and still requires current credentials and exact target resolution.
- Ask before uploading private source to cloud testing services.
- Do not rotate credentials, create paid resources, enable public links, submit for review, or release to customers unless explicitly authorized.

## Handoff Format

Lead with the achieved outcome. Then report:

```text
Outcome:
Product loop:
Changed:
Validation:
Evidence gates:
  Source / Build / Runtime / Archive / Upload / Processing /
  TestFlight / Physical device / Submission / Review / Production
Open blockers:
Exact next action:
```

Name the artifact, configuration, simulator/device, version/build, branch/commit, and dashboard state when known. Use “not checked” instead of implication.

## Hard Rules

- Never expose secrets or private key contents.
- Never infer App Store Connect, provider-dashboard, TestFlight, or production state from local files.
- Never copy sample code without checking framework age, package/API availability, state ownership, licensing, accessibility, and compilation.
- Never copy another app's trade dress, proprietary fonts, icons, or branded assets as a substitute for a product design system.
- Never use SceneKit as the default for new Apple 3D work.
- Never claim current-source runtime proof from a stale installed app.
- Never flatten source, build, simulator, archive, upload, processing, TestFlight, physical-device, and production evidence into one “works” claim.
