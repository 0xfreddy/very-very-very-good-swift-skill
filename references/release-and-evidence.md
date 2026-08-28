# Release and Evidence

## Contents

1. Release identity
2. Preflight
3. TestFlight
4. App Review
5. Evidence ledger
6. Launch/rollback

## Release identity

Resolve the exact workspace/project, scheme, configuration, Team ID, app/extension bundle IDs, version, build, archive path, export method, and App Store Connect record before release commands. Confirm profiles and entitlements share the same identity family.

## Preflight

Run local/source checks, then use `$ios-shipping-preflight`, App Review, and Greenlight skills when available. Verify findings rather than inheriting severity.

Check scoped release diff/commit; Release URLs/config; signing/profiles/capabilities/extensions/App Groups/privacy manifests; current-source build and critical flows; accessibility/localization/device needs; legal/support/marketing URLs; deletion/reviewer path/permissions/IAP/UGC; metadata matching reachable features; no placeholders/debug/fake data; and backend compatibility/health.

## TestFlight

Treat these as separate steps:

1. Archive the Release device build.
2. Validate/export and upload it.
3. Wait for App Store Connect processing.
4. Resolve compliance/build metadata.
5. Add beta description, what-to-test, feedback contact, and credentials.
6. Assign the processed build to the correct group.
7. Complete Beta App Review when required.
8. Install from a real tester account.
9. Run critical/device-only flows on that installed build.

Recheck current internal/external tester and public-link rules in App Store Connect documentation/dashboard.

## App Review

Give reviewers a deterministic path with credentials when required, concise notes, permission rationale, prerequisites, and current contact details. Every screenshot and claim must map to the submitted build.

Do not submit broken URLs, visible “Coming Soon,” blurred locked cards, unreachable tabs, or placeholder content. Recheck current App Review Guidelines immediately before submission.

## Evidence ledger

Use an append-only ledger:

| Time | Gate | Artifact/version | Command/dashboard/device | Result | Evidence path |
| --- | --- | --- | --- | --- | --- |

Allowed results: `passed`, `failed`, `blocked`, `not checked`. Name exact artifact hashes/builds where possible. Keep source, build, simulator, archive/export, upload, processing, TestFlight install, physical-device behavior, submission, review, release, and backend health independent.

## Launch and rollback

Define phased/manual release, backend compatibility window, server kill switches where appropriate, monitoring owner, support path, and mitigation. Apple binary rollback is not instantaneous.

After release verify the public store version, fresh install, upgrade, auth, core data, purchases if any, notifications/deep links, backend health, crash/performance signals, and support/legal links.
