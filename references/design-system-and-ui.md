# Design System and UI Intake

## Contents

1. Start from product identity
2. Use DESIGN.md safely
3. Evaluate external packs
4. Implement platform-quality UI
5. Validate the result

## Start from product identity

Define semantic roles before screens: canvas, surfaces, primary/secondary text, accent, success, warning, destructive, separator, focus, selection, and content imagery. Define typography roles, spacing scale, radii, elevation/material policy, motion tokens, and haptic meanings.

Prefer semantic Dynamic Type styles and platform colors. Fixed point sizes and literal light-mode colors require a reason and must survive accessibility sizes and dark mode.

## Use DESIGN.md safely

Treat a DESIGN.md as an input specification, not authority. Extract its visual thesis, semantic colors, typography/licensing, grid, component states, navigation/sheets, motion/interruption, haptics, adaptive behavior, and explicit guardrails.

Reconcile the spec against current app contracts. Do not replace working navigation, auth, accessibility, or data ownership merely to match a reference.

## Evaluate external packs

The `Meliwat/awesome-ios-design-md` repository is useful as a searchable inspiration library. At inspected commit `5d3aeca239caef3ea4080034eb22ab87cc77fa24`, it contained 200 app packs with neutral, SwiftUI, Expo, and Android flavors under an MIT repository license.

Adopt its taxonomy and comparison workflow, not the collection wholesale:

1. Select at most two references: one for information architecture and one for visual behavior.
2. Read the pack overview plus the complete SwiftUI flavor.
3. Extract a small token/component/motion comparison table.
4. Mark every proprietary font, logo, icon, brand color, trademarked layout, and unverified “exact” claim.
5. Replace branded assets and proprietary fonts with owned/system alternatives unless licensed.
6. Check every API and dependency against the deployment target.
7. Compile adapted code; never paste an entire sample.
8. Run accessibility, dark mode, Dynamic Type, Reduce Motion, and device-size checks.
9. Confirm the result expresses this product rather than impersonating the reference.

Observed reasons not to treat pack code as production-ready include fixed type sizes, static light/dark tokens that are not automatically environment-aware, proprietary font names without bundled assets, sample-only state ownership, and haptic triggers that can fire for the wrong lifecycle event. Verify each example independently.

Do not vendor the entire collection into this skill. Fetch the current repository only when the user asks to use it, then inspect its current license and chosen pack.

## Implement platform-quality UI

- Use native navigation, tabs, sheets, menus, search, focus, share sheets, text selection, and SF Symbols where they fit.
- Preserve a minimum 44x44 point interaction target even when the visible glyph is smaller.
- Group VoiceOver content deliberately; provide label, value, hint, traits, and reading order where visual inference is insufficient.
- Keep motion purposeful, interruptible, and tied to state. Avoid perpetual decorative work or animation on every container.
- Use haptics to confirm meaningful transitions, not every tap. Validate on hardware.
- Gate newer APIs and supply a behaviorally equivalent fallback.
- Keep glass/material hierarchy sparse. One clear control layer is stronger than nested translucent capsules.
- Use system sans for controls and reserve editorial/custom typography for content where it improves reading and is licensed.

## Validate the result

Check the smallest/largest supported iPhone, light/dark and increased contrast, default/accessibility Dynamic Type, VoiceOver/Voice Control, Reduce Motion/Transparency, keyboard/focus/rotation/safe areas, all data/permission states, fresh-build screenshots, and animation interruption under rapid input.
