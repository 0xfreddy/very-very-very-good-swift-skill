# The Odds News Repository Lessons

Use these as transferable patterns, not a mandate to reproduce the app's architecture or credentials.

## What worked

- SwiftUI-first composition with Swift 6 and an iOS 17 baseline.
- XcodeGen as source of truth; regenerate after project-input changes.
- Native navigation, sheets, SF Symbols, Swift Charts, MapKit, and RealityKit where platform behavior mattered.
- Central semantic design system for editorial styling, preferences, accessibility, and consistency.
- Typed networking with cache identity, ETag/Last-Modified revalidation, stale fallback, and explicit mobile models.
- Focused tests plus separate runtime, archive, upload, TestFlight, and device evidence.
- Clerk authentication and OneSignal/APNs lifecycle ownership with environment separation.
- Notification extension/App Group treated as a complete identity family.
- Metal used selectively for signature effects, not ordinary controls.
- Web/Vite useful for prototypes/assets; critical interaction/accessibility surfaces moved native.

## What caused delay or risk

- Confusing display/product name with immutable App Store bundle identity.
- Treating compilation, stale install, archive/export, upload, processing, and TestFlight availability as equivalent.
- Missing extension identifiers, entitlements, profiles, or App Groups.
- Mixing `.p8` purposes or not recording credential lifecycle.
- Treating simulator haptics/synthetic push as hardware delivery proof.
- Copying UI samples without checking OS, age, ownership, license, accessibility, or framework direction.
- Starting new 3D guidance in SceneKit instead of RealityKit.
- Too much glass, rounded containment, motion, or custom navigation.
- Advertising features absent from the reviewed build.
- Assuming cloud QA represented current source without matching artifacts.
- Retrying an Xcode/file-coordination stall that never reached the compiler.

## Reusable rule

Maintain one row per evidence layer and report the first unverified gate. A source audit can be excellent while release status is unknown. A successful upload can be real while TestFlight installation remains pending.
