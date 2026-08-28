# Greenfield Starter

The bundled starter creates a small SwiftUI/XcodeGen app with Swift 6, configurable iOS target, Debug/Staging/Release, app and unit-test targets, optional Team ID, semantic theme tokens, typed actor-based API client, privacy manifest, empty icon/accent catalogs, and an initial DESIGN.md.

It intentionally excludes third-party SDKs, secrets, auth, push, payments, analytics, and unnecessary entitlements.

```bash
python3 scripts/create_native_ios_app.py \
  --name "Example App" \
  --bundle-id "com.example.exampleapp" \
  --output "/absolute/path/ExampleApp" \
  --team-id "ABCDE12345" \
  --deployment-target "17.0" \
  --generate
```

The generator refuses a non-empty destination. It never invents a Team ID or integration identifier. Without `--generate`, run `xcodegen generate` from the output later.

After creation, replace the DESIGN.md contract, add real icons, set environment URLs without private keys, implement one vertical loop/tests, add providers only after identity/privacy decisions, generate/build/interact with a fresh install, and use the release workflow only when complete.

The starter is a baseline, not App Store-readiness proof.
