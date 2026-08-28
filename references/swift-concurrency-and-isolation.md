# Swift Concurrency and Isolation

Use this reference for Swift 6 diagnostics, actors, tasks, Sendable boundaries, cancellation, or migration. For detailed implementation, route to `$swift-concurrency` when available.

## Establish the Compiler Contract

Before proposing a migration-sensitive fix, inspect the authoritative project input and resolved build settings for:

- Swift language mode
- `SWIFT_STRICT_CONCURRENCY`
- `SWIFT_DEFAULT_ACTOR_ISOLATION`
- `SWIFT_APPROACHABLE_CONCURRENCY`
- enabled upcoming features

For SwiftPM, inspect `Package.swift`; do not infer language mode from only `swift-tools-version`. For XcodeGen, inspect `project.yml` and verify the generated build settings. Capture the exact diagnostic, offending symbol, and module boundary.

Do not assume new-Xcode defaults. Gate newer syntax such as `@concurrent` on the actual toolchain and deployment compatibility.

## Choose the Ownership Boundary

- Use `@MainActor` for genuinely UI-owned state and behavior, not as a blanket fix.
- Put shared mutable non-UI state behind an actor or another explicit synchronization boundary.
- Move immutable, Sendable values across isolation domains; avoid moving mutable reference graphs.
- Prefer structured concurrency (`async let`, task groups, child tasks) over unstructured tasks.
- Use `Task.detached` only when actor-context inheritance is specifically wrong and the lifetime is explicitly owned.
- Treat `@preconcurrency`, `@unchecked Sendable`, and `nonisolated(unsafe)` as temporary escape hatches requiring a written invariant and removal plan.

For each `Task`, inspect the synchronous prefix before its first `await`. Inherit main-actor context only if that prefix needs UI isolation. Separate delays, retries, and background work from the final main-actor mutation.

Maintain a task-ownership ledger for long-lived or unstructured work:

| Location | Owner | Actor inherited | Cancellation trigger | Result consumed | Deallocation verified |
| --- | --- | --- | --- | --- | --- |
| `File.swift:line` | view/model/service | actor or none | event/lifecycle | yes/no | yes/no |

Run `python3 "$SKILL_DIR/scripts/audit_swift_sources.py" <app-root> --include-task-sites` to seed the ledger with detached tasks, ordinary task sites, unsafe isolation escapes, and continuations. Source-pattern matching cannot infer lifecycle ownership, so ordinary task findings are prompts rather than defects.

## Implement and Verify Narrowly

1. Fix one diagnostic category at a time.
2. Rebuild before expanding the change.
3. Run actor-, lifetime-, and cancellation-sensitive tests.
4. Confirm long-running loops check cancellation and owned tasks are cancelled when their owner ends.
5. Check deallocation for views, models, streams, and continuations that retain tasks.
6. Use Instruments for concurrency performance claims.

Never use blocking waits, semaphores, or ad hoc locks inside async code when actor isolation or a structured primitive expresses ownership safely.

## Core Data Boundary

Never pass `NSManagedObject` instances across contexts, tasks, or actors. Pass `NSManagedObjectID` or map to an immutable Sendable value, then resolve inside the destination context. Read `persistence-selection.md` when Core Data is involved.
