# Xcode Build Performance

Use this reference only when the user reports slow builds or requests build optimization. Route the full workflow to `$xcode-build-orchestrator` and its benchmark, compilation, project, package, and fixer specialists when available.

## Benchmark Before Recommending

Define one repeatable contract:

- authoritative `.xcworkspace` or `.xcodeproj`
- scheme, configuration, SDK, and destination
- Xcode/toolchain version
- clean, cache-warm clean, zero-change incremental, or touched-file incremental scenario
- fixed machine and reasonably quiet environment

Record wall-clock time as the primary metric. Keep cumulative task time as diagnostic evidence only because parallel tasks do not add directly to developer wait time. Use repeated runs and report median, minimum, and maximum. If the min-to-max spread exceeds 20% of the median, label the result noisy and gather more runs before claiming improvement.

Store benchmark evidence under `.build-benchmark/`. Verify raw logs and timing categories are non-empty. Keep clean, cached-clean, zero-change, and real incremental results separate.

## Diagnose the Critical Path

Classify the evidence before changing anything:

- source compilation and type-checking
- module emission or invalidation
- project settings and scheme behavior
- serial script phases, asset catalogs, signing, or code generation
- Swift Package graph, plugins, binary dependencies, or resolution
- unhealthy Xcode, Simulator, DerivedData, disk, or file-coordination environment

If cumulative compiler time greatly exceeds wall clock, much of it is parallel; reducing it may save CPU without reducing developer wait. Rank changes by likely wall-clock impact.

For XcodeGen projects, edit `project.yml` and regenerate. Never treat generated `.pbxproj` edits as durable.

## Apply an Approval-Gated Loop

Phase 1 is recommendation-only except for benchmark artifacts and the optimization report. Present each recommendation with evidence, expected wait-time impact, affected files/settings, risk, and an approval checkbox.

After explicit approval:

1. Apply one scoped, reversible change at a time.
2. Confirm production correctness and a successful build.
3. Re-run the identical benchmark contract.
4. Keep only improvements whose benefit survives measurement and does not weaken correctness, reproducibility, signing, or CI.
5. Report absolute and percentage wall-clock deltas plus confidence/noise.

Stop and classify an environment blocker when Xcode or file coordination stalls before compiler work. Repeated retries are not evidence about source performance.
