# Implementation and Quality

## Contents

1. Vertical slices
2. Swift concurrency and state
3. Networking and cache
4. Testing pyramid
5. Performance
6. Generated projects and dirty worktrees

## Vertical slices

Implement one reachable user loop through view, state, API/persistence, errors, accessibility, and tests. Avoid building all models, then all screens, then discovering the product does not connect.

For each slice: state acceptance behavior; identify source of truth; add the smallest data contract/test seam; implement loading, success, empty, error, stale/offline, and cancellation; add accessibility/privacy decisions; then run narrow checks, focused tests, fresh interaction, and visual/accessibility verification.

## Swift concurrency and state

- Keep UI mutations on the main actor.
- Prefer structured tasks tied to view/model lifetime; cancel stale search, pagination, and navigation work.
- Avoid `Task.detached` unless isolation and lifetime are explicit.
- Make shared mutable services actors or otherwise prove synchronization.
- Keep `@State` private/local; use bindings for child mutation; inject shared observable state intentionally.
- Do not hide network/database work inside view bodies or computed properties.
- Make error types meaningful enough to drive retry, re-authentication, offline, and user messaging.

## Networking and cache

- Build URLs with `URLComponents` and path components, not string concatenation.
- Validate status codes and content type before decoding.
- Model dates, decimals, enums, and optionality according to the wire contract.
- Respect cancellation. Retry only idempotent requests by default, with bounds and jitter.
- Treat authentication refresh as a single-flight operation.
- Define cache identity from all request filters. Store ETag/Last-Modified when supported.
- Surface staleness and preserve useful last-known data when requirements allow it.
- Redact tokens, user data, and private payloads from logs.

## Testing pyramid

Use pure unit tests for formatting/state/routing/cache identity; API fixture tests for decoding/errors; integration tests for persistence/auth/dependencies; UI or Revyl flows for critical paths; physical-device tests for APNs/haptics/hardware/background/performance; and archive/TestFlight tests for Release configuration.

Test permission denial, logout/account switching, deletion, offline launch, stale cache, empty data, duplicate notifications, cold-start deep links, and corrupt/missing persistence—not only happy paths.

## Performance

Inspect repeated work in `body`, unstable identities, synchronous I/O, oversized images, unbounded tasks, eager lists, expensive formatters, and observation fan-out. Then measure the exact artifact with Instruments/ETTrace/memgraphs when performance matters.

Do not infer performance from simulator feel alone. Name device, OS, configuration, data size, trace interval, and before/after metric.

## Generated projects and dirty worktrees

If `project.yml` or another generator is authoritative, edit its inputs, regenerate after project-input changes, and inspect generated churn. Keep DerivedData, archives, result bundles, databases, `.revyl`, caches, and secrets out of commits.

In a dirty tree, patch scoped paths only. Do not reset unrelated work. If Git metadata is unhealthy, report byte/source validation separately from branch/commit evidence.
