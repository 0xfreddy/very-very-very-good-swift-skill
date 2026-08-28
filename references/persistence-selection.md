# Persistence Selection

Use this reference when selecting persistence or when the project already contains SwiftData, Core Data, SQLite, Realm, files, or a custom cache. Do not introduce Core Data merely because an iOS app stores data.

## Select From Product Requirements

Inventory the existing store and decide from data shape, offline behavior, query needs, migration burden, sync ownership, encryption, sharing/extensions, and deployment target.

- Use simple files or preferences for small configuration and replaceable caches.
- Consider SwiftData for a compatible modern Apple-platform app whose data model and migration needs fit it.
- Consider Core Data for an existing Core Data estate or when its mature relational model, migrations, batching, persistent history, and CloudKit integration materially fit the product.
- Preserve an existing custom persistence layer unless a measured product or maintenance problem justifies migration.

Route to `$core-data-expert` only when Core Data is selected or detected (`NSManagedObject`, `NSPersistentContainer`, `.xcdatamodeld`, or equivalent stack code).

## Core Data Guardrails

- Identify view versus background context before changing fetch/save behavior.
- Never pass `NSManagedObject` across contexts, tasks, or actors; pass `NSManagedObjectID` or a Sendable value snapshot.
- Verify merge policy, uniqueness constraints, and UI merge behavior together.
- For batch inserts, updates, or deletes, verify persistent history tracking and the merge pipeline when the UI must observe changes.
- Prefer lightweight migration when valid; plan staged migration for complex iOS 17+ changes and test real old stores.
- Treat the CloudKit production schema as immutable. Exercise schema and migration changes in development before production deployment.
- Profile fetch limits, batching, faults, memory, and save frequency before claiming performance improvement.

Use in-memory stores for fast tests, but also test migration and store behavior against representative persistent stores.
