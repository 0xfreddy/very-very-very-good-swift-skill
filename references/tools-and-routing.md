# Tools and Routing

Choose tools by the evidence they can produce.

| Need | Preferred route | Does not prove |
| --- | --- | --- |
| Product positioning | `positioning-products` | implemented features |
| SwiftUI composition/state | `build-ios-apps:swiftui-ui-patterns` | runtime/release |
| Simulator build/debug | `build-ios-apps:ios-debugger-agent` | physical-device behavior |
| Performance audit | SwiftUI performance/ETTrace/memgraph skills | production/App Store state |
| Accessibility | `ios-accessibility` | complete device proof without running it |
| Motion/design critique | `apple-design`, `emil-design-eng`, `review-animations` | implementation correctness |
| iOS 26 glass | `build-ios-apps:swiftui-liquid-glass` | older-OS fallback quality |
| App Review risk | `apple-appstore-reviewer` | acceptance by Apple |
| Compliance scan | `greenlight` | readiness by itself |
| Release conductor | `ios-shipping-preflight` | uninspected dashboard/device state |
| Repeatable cloud flows | Revyl CLI skills | APNs/haptics or untested artifacts |
| App Store Connect | Helm/current ASC tooling | signing/current runtime correctness |
| Symbols/icons | SF Symbols/Icon Composer | third-party asset licensing |

Ask before uploading private source to Revyl/cloud services. Use Helm after artifact identity is resolved. Treat UI cookbooks/design packs as reference material and compile adapted code.

Do not add a tool to the app because it helped development. Keep developer tooling, app dependencies, backend services, and release services separate.
