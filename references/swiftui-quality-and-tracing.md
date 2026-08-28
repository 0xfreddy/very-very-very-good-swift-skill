# SwiftUI Quality and Tracing

Use this reference for SwiftUI implementation, review, stale UI, navigation, list identity, rendering, or performance. Route deep work to `$swiftui-expert-skill`; use `$build-ios-apps:swiftui-performance-audit`, `$build-ios-apps:ios-ettrace-performance`, or `$build-ios-apps:ios-memgraph-leaks` when the matching evidence is required.

## Correctness First

- Make view-owned `@State` private. Do not store an injected value in `@State` because it will ignore later input changes.
- Use `@Binding` only when a child mutates parent-owned state.
- On iOS 17+, hold a view-owned `@Observable` model in `@State`; use `@Bindable` only where an injected observable needs bindings.
- Give every `ForEach` stable domain identity that outlives the view. Never use indices, offsets, or mutable display content as identity for a changing collection.
- Keep row structure stable and filtering outside the row builder.
- Extract complex bodies into meaningful subviews with narrow inputs; avoid broad environment dependencies that invalidate large trees.
- Use native navigation, sheets, focus, scroll, controls, and accessibility behavior before custom substitutes.
- Make previews deterministic and independent of live services.

Gate version-specific APIs with `#available` and a real fallback. Adopt Liquid Glass only when explicitly requested and supported by the product's deployment strategy.

## Audit API Age and Source Shape

Check the deployment target before replacing APIs. Prefer modern equivalents for new work, including `NavigationStack`/`NavigationSplitView`, `toolbar`, `foregroundStyle`, `clipShape(.rect(cornerRadius:))`, `animation(_:value:)`, Observation on iOS 17+, and the `Tab` API on iOS 18+. Do not perform unrelated modernization merely because an older API appears.

Run `python3 "$SKILL_DIR/scripts/audit_swift_sources.py" <app-root>` to flag positional collection identity, legacy navigation, unscoped animation, and unusually large view bodies. Confirm each finding against actual data mutation, deployment target, compile behavior, and runtime invalidation before editing.

## Performance Triage

Start with source inspection:

1. Find broad observable dependencies, unstable identity, repeated sorting/filtering, synchronous decoding, oversized images, expensive body work, and duplicate network tasks.
2. Reproduce one named user-visible symptom on a fresh current-source install.
3. Add lightweight signposts when the trace cannot identify the product event.
4. Record the smallest representative trace.

For iOS Simulator, prefer Time Profiler because the SwiftUI Instruments lane may be empty. On a physical Apple device or the host Mac, use the SwiftUI template when available. Correlate hangs, animation hitches, main-thread CPU, SwiftUI invalidation causes, and the exact interaction window before editing.

For an expensive view, identify what invalidates it; do not optimize only the leaf body while a broad state publisher continually refreshes the tree. Validate image downsampling and caching when full-size payloads are decoded on hot paths. Give Swift Charts an accessible summary or audio-graph representation appropriate to the data.

Report measured before/after behavior for the same build, hardware, data, and interaction. Simulator evidence does not prove physical-device performance.
