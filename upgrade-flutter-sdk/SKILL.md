---
name: upgrade-flutter-sdk
description: Inspect and upgrade the Flutter SDK version of an existing project while migrating only its Android and iOS host configuration. Use when asked to detect a project's current Flutter version, upgrade or migrate Flutter across stable releases, align Gradle/AGP/Kotlin/Java or Xcode/iOS settings with a target Flutter release, or diagnose platform build failures caused by a Flutter SDK upgrade. Treat versions by major.minor for migration selection, so patch-only changes such as 3.35.1 to 3.35.7 do not trigger platform migrations.
---

# Upgrade Flutter SDK

Upgrade an existing Flutter application without overwriting its Android/iOS customizations. Ignore web, macOS, Windows, Linux, and embedded platforms unless the user explicitly asks for analysis; do not modify them.

## Inspect before editing

Run the bundled inspector from the target project root:

```bash
python3 <skill-dir>/scripts/inspect_flutter_project.py . --target <target-version>
```

Use `--json` when machine-readable output is useful. Read [migration-rules.md](references/migration-rules.md) for every migration level emitted by the inspector. Read [evidence.md](references/evidence.md) only when provenance, uncertainty, or a rule's historical basis matters.

If the target version is absent, infer it from the user's request. If neither the prompt nor repository configuration gives a target, ask for the target version before changing files.

## Version semantics

Parse stable versions as `major.minor.patch`, accepting suffixes such as `-stable`. Select migrations using only `(major, minor)`:

- `3.35.1` and `3.35.7` are the same migration level (`3.35`).
- A patch-only change updates explicit SDK pins but applies no Android/iOS migration rules.
- Apply every known level where `current major.minor < level <= target major.minor`.
- Refuse a downgrade unless the user explicitly requests one. Do not reverse migrations mechanically.

When version sources disagree, report every source and resolve the conflict before platform edits. Prefer committed project pins over the globally active `flutter` command. `.metadata` revisions are evidence, not a writable semantic-version pin.

## Upgrade workflow

1. Check `git status --short`. Preserve all user changes and do not mix unrelated edits into the upgrade.
2. Run the inspector. Confirm the project has `pubspec.yaml` and at least one of `android/` or `ios/`; skip a missing platform.
3. Inventory custom platform behavior before edits:
   - Android: application ID/namespace, flavors, signing, repositories, ProGuard/R8, ABI filters, manifest entries, native code, Firebase/services plugins, and CI.
   - iOS: bundle IDs, deployment targets, capabilities, build configurations, schemes, Podfile hooks, AppDelegate/SceneDelegate logic, entitlements, and CI.
4. Update all existing explicit Flutter SDK pins to the exact requested target version. Typical locations are `.tool-versions`, `.fvmrc`, `.fvm/fvm_config.json`, `.vscode/settings.json`, and CI install scripts. Do not add a version manager the project does not already use.
5. Update `pubspec.yaml` SDK constraints only when required by the target Dart/Flutter SDK or the user asks to pin Flutter. Never bulk-upgrade package dependencies merely because Flutter changes.
6. Apply each emitted migration rule in ascending order. Treat the rule catalog as a checklist, not a blind patch:
   - Apply required compatibility changes when their condition matches.
   - Apply template-alignment changes only when compatible with project constraints.
   - Preserve custom logic while translating syntax or moving it to a new lifecycle hook.
   - Never copy signing credentials or project-specific values from the historical example.
7. For a target level not covered by the catalog, inspect official Flutter breaking-change/release notes and compare a disposable target-version template created with `flutter create --platforms=android,ios`. Merge the structural delta manually; never replace whole platform directories.
8. Let Flutter regenerate generated files. Do not hand-edit `Generated.xcconfig`, `flutter_export_environment.sh`, `Pods/`, `.dart_tool/`, `build/`, or Gradle caches.

## Validate

Use the project's selected target SDK/version manager for validation. Run the strongest commands supported by the environment:

```bash
flutter --version
flutter pub get
flutter analyze
flutter test
flutter build apk --debug
flutter build ios --simulator --no-codesign
```

Also run `cd android && ./gradlew tasks` when Gradle files changed, and `cd ios && pod install` when CocoaPods inputs changed and CocoaPods is available. Do not claim an iOS build passed if macOS/Xcode is unavailable.

Review `git diff --check` and the final diff. Report detected and target versions, migration levels applied, files changed, preserved customizations, commands run, and any remaining manual checks.

## Guardrails

- Do not run `flutter create .` over the existing project.
- Do not rewrite Groovy files to Kotlin DSL solely because a newer template uses `.kts`; do so only when explicitly requested or when a validated compatibility need justifies the larger change.
- Keep Gradle, AGP, Kotlin, Java, compile SDK, and plugins mutually compatible. Template values are baselines, not universal mandates.
- Raise iOS deployment targets consistently in the Podfile (if present), `AppFrameworkInfo.plist`, and every relevant Xcode build configuration.
- Inspect custom AppDelegate code before UIScene migration; UI lifecycle logic may need a semantic move rather than a textual edit.
- Restrict modifications to root SDK pins, dependency constraints required for the upgrade, `android/`, and `ios/`.
