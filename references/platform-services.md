# Platform Services

## Contents

1. Identity matrix
2. Credentials
3. Authentication
4. Push notifications
5. Deep links/extensions
6. Privacy/account lifecycle

## Identity matrix

Maintain a current matrix before enabling capabilities:

| Surface | Identifier | Environment | Owner/evidence |
| --- | --- | --- | --- |
| Main app | bundle ID | Debug/Staging/Release | project + Apple record |
| Widget/intents | extension bundle ID | Release | target + profile |
| Notification service | extension bundle ID | Release | target + profile |
| App Group | group identifier | Release | entitlements + Apple |
| Keychain group | access group | Release | entitlements + profile |
| Associated domain | domain entitlement | Release | app + hosted AASA |
| Auth | native app/Services ID | each | provider + Apple |
| Push | APNs topic/provider app | each | provider + device |

Changing the production bundle ID affects every row. Resolve it before external integrations.

## Credentials

Keep similarly named Apple credentials distinct:

- APNs `.p8`: server/push-provider notification authorization.
- Sign in with Apple `.p8`: server/web OAuth developer-token signing.
- App Store Connect API `.p8`: App Store Connect automation.
- Certificates/`.p12`: code-signing identities.
- Provisioning profiles: identifier/capability/certificate/distribution binding.
- App-specific password: supported Apple Account integration credential; not a key/profile.

Record credential type, purpose, owner, Team/Issuer/Key ID, environment, creation date, secure storage, integrations, and revocation plan. Never put private material in the app/repository or print it.

## Authentication

- Keep development and production provider instances separate.
- Verify native redirect schemes, universal links, Services ID/web fallback, callbacks, and backend JWT validation.
- Recheck current App Review rule 4.8 and exceptions when social login is primary.
- Preserve server-backed OTP verification, resend cooldown, rate limits, autofill, paste, errors, and session creation. Never replace it with local code comparison for styling.
- Prove anonymous/auth transitions, logout, account switching, reinstall, expiry/revocation, and deletion.

## Push notifications

Choose one lifecycle owner. Distinguish user identity from device subscription, external ID from provider ID, user tags from permission state, and APNs delivery from local rendering/tap routing.

Configure capabilities, background modes, credentials, matching identifiers/entitlements, and a Notification Service Extension/App Group only when requirements justify them.

Test an internal segment first. Prove opt-in/denial, identity, tags, cold/background/foreground delivery, deep links, duplicates, switching, reinstall, and opt-out on a physical TestFlight/device build. `simctl push` proves rendering/routing, not provider delivery.

## Deep links and extensions

Treat URLs as untrusted input. Validate hosts/routes and provide a safe fallback. Prove cold/warm launch, signed-out destination, deleted content, and version incompatibility.

For every extension check its own bundle ID, profile, entitlements, App Groups, privacy, deployment target, resources, and extension-safe APIs. Main-target configuration does not configure extensions.

## Privacy and account lifecycle

Align code, privacy manifest, App Privacy answers, SDK collection, analytics, legal pages, retention, export, and deletion. Verify backend deletion/revocation rather than hiding a local profile.

Request permissions at the moment of value with a denial path. Remove unused usage descriptions/capabilities. Recheck third-party SDK privacy manifests and required-reason APIs for exact shipped versions.
