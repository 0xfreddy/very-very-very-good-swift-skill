# Testing Strategy

Use this reference for new tests, XCTest migration, flaky suites, async waiting, CI selection, and release confidence. Route detailed Swift Testing work to `$swift-testing-expert` and broader test design to `$testing-practices` when available.

## Select the Framework Deliberately

Prefer Swift Testing for new Swift unit and integration tests when supported by the project's Xcode and Swift versions. Keep XCTest for:

- XCUITest and `XCUIApplication`
- `XCTMetric` performance tests
- Objective-C test code
- cases not yet supported by Swift Testing

Allow both frameworks in one target during migration. Only import `Testing` in test targets.

## Write High-Signal Tests

- Use `#expect` for ordinary assertions and `#require` when later assertions depend on a prerequisite value.
- Parameterize cases that share behavior and differ only by input or expected output.
- Use traits and tags for behavior, ownership, known issues, time limits, and test-plan filtering instead of encoding all metadata in names.
- Put `@available` on individual test functions, not suite types.
- Keep each test deterministic, independently reproducible, and explicit about time, locale, network, file system, database, and global-state dependencies.
- Prefer fakes or in-memory stores at boundaries; retain a smaller set of real integration tests for contract confidence.

Swift Testing runs tests in parallel by default. Isolate shared state first. Use `.serialized` only as a documented transition or when serialization is an actual product constraint.

## Migrate Incrementally

1. Preserve behavior and coverage while converting assertions.
2. Group tests into useful suites.
3. Introduce parameterization, traits, and tags where they improve signal.
4. Keep unsupported XCTest-only tests intact.
5. Compare test-plan and CI filtering before deleting the old path.

For flaky async tests, determine whether the failure is a product race, shared-fixture race, incorrect callback bridge, fixed-time sleep, or environment failure. Await observable completion; do not hide nondeterminism by increasing sleeps or serializing the entire suite.

## Release Coverage

Test the smallest complete user loop plus loading, empty, stale, error, retry, signed-out, denied-permission, offline, cancellation, and migration behavior. Unit success does not replace a fresh build, simulator interaction, accessibility check, physical-device proof, or release-artifact verification.
