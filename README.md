# Very Very Very Good Swift Skill

Ship native iOS apps without confusing “it builds” with “it is ready.”

`launch-native-ios-app` takes a Swift or SwiftUI app from product brief to verified TestFlight or App Store release.

## What it tackles

It fixes the work coding agents often miss:

- finding the real app root, scheme, target, and generated project source
- keeping SwiftUI state, Swift concurrency, persistence, and tests correct
- handling accessibility, privacy, auth, push, deep links, signing, and App Review
- separating source, build, Simulator, archive, upload, TestFlight, device, and production proof

## How it works

It inventories the project, defines the smallest complete user loop, builds vertical slices, and records each release gate separately. Specialist skills add depth when installed but are not required.

It also includes:

- a Swift 6 and XcodeGen starter
- read-only project inspection
- Swift Testing examples
- release and evidence checklists
- regression tests and a starter build verified in GitHub Actions

## Who it is for

- indie iOS developers and technical founders using coding agents
- small teams moving a prototype toward TestFlight or the App Store
- developers inheriting a messy SwiftUI or XcodeGen project

It is not intended to replace focused specialist skills for a single isolated concurrency, Core Data, testing, or build-performance fix.

## Install

```bash
npx skills add 0xfreddy/very-very-very-good-swift-skill
```

Then ask:

```text
Use $launch-native-ios-app to take this app from brief to a verified TestFlight launch.
```

[MIT licensed](LICENSE).
