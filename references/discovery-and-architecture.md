# Discovery and Architecture

## Contents

1. Repository discovery
2. Product contract
3. Architecture defaults
4. Environment model
5. Decision records

## Repository discovery

Resolve the real app root before planning. Look for `.xcodeproj`, `.xcworkspace`, `project.yml`, `Package.swift`, `.swiftpm`, `Tuist`, `Podfile`, `Cartfile`, schemes, and nested `.git` directories. Treat a generated `.xcodeproj` as an output when XcodeGen/Tuist is authoritative.

Inspect targets and extensions, minimum OS and Swift version, build configurations, bundle identity, entitlements, dependency policy, app entry point, navigation, dependency composition, state ownership, API client, persistence, design tokens, tests, branch state, and ignored/generated artifacts.

Do not start by opening or regenerating the entire Xcode project if narrow text/source inspection can establish the architecture.

## Product contract

Write a one-page contract before a greenfield build:

- target user and job;
- smallest complete user loop;
- data source and source of truth;
- authenticated and anonymous behavior;
- loading, empty, stale, error, offline, permission-denied, and deleted-account states;
- privacy-sensitive data and retention/deletion responsibilities;
- notification/deep-link behavior;
- accessibility and localization baseline;
- store/website claims and non-goals;
- launch definition and required evidence gates.

Prefer a narrow complete product to many incomplete tabs. Every visible control in a submission build must work.

## Architecture defaults

Use defaults as starting points, not dogma:

- Swift 6 and structured concurrency.
- SwiftUI app lifecycle and NavigationStack for new apps.
- Explicit dependency composition at the app root.
- Observation or narrowly scoped `ObservableObject` ownership; avoid ambient global mutable state.
- Actor-isolated or Sendable networking/persistence boundaries.
- Typed request/response models, status validation, cancellation, bounded retry, and test seams.
- Cache metadata and staleness as data, not invisible implementation detail.
- SwiftData/Core Data only when structured local persistence is warranted; simple preferences in AppStorage/UserDefaults.
- Swift Charts for native charts, MapKit for native maps, RealityKit for new 3D work.
- UIKit bridges only for behavior SwiftUI cannot reliably provide.

Before adding a dependency, check maintenance, license, privacy manifest, binary contents, minimum OS, transitive dependencies, and whether the platform already owns the behavior.

## Environment model

Keep Debug, Staging, and Release behavior explicit. Avoid silently pointing Debug at production unless the product deliberately supports it.

For each environment record API/web URLs, public client identifiers, auth instance/domain and redirects, push identifier, associated domains, logging/analytics policy, server-side secret owner, and fixture/demo behavior.

Do not place private server credentials in `.xcconfig`, Info.plist, entitlements, assets, source, or generated project files. Assume the installed app can be inspected.

## Decision records

Record only decisions that will otherwise be rediscovered: production bundle ID, minimum OS, project generator ownership, state model, offline model, auth provider, notification owner, navigation model, and release evidence definition. Include the rejected alternative and the requirement that made the decision.
