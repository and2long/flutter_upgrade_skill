# Rule evidence and confidence

## Local history analyzed

Reference repository: `/Users/lilong.zhang/projects/github/tcm-app`.

| Transition | Commit | Material host changes |
|---|---|---|
| Initial 3.27.4 | `dcb523a` | Android declarative Flutter plugin DSL; iOS 12 baseline |
| 3.27.4 → 3.29.2 | `1f41ab7` | Gradle 8.3 → 8.10.2; `.cxx` ignore; iOS GPU validation; SDK pins |
| 3.29.2 → 3.29.3 | `a6470d3` | Pins only; confirms patch changes do not require host migrations |
| 3.29.3 → 3.35.7 | `f1f7dde` | iOS 12 → 13; LLDB init; SDK pins; unrelated dependency/application edits excluded |
| 3.35.7 → 3.38.10 | `8d18620` | Gradle 8.14, AGP 8.11.1, Kotlin 2.2.20, Groovy → Kotlin DSL, Java 17 syntax, Jetifier removal, SDK pins and metadata revision |

Do not copy credentials or project-specific tuning from these commits. The 3.38 commit contains signing values and Gradle heap changes that are not reusable migration rules.

## Template comparison

Fresh projects were generated locally with installed Flutter 3.29.3, 3.38.10, 3.41.9, and 3.44.0 SDKs using `flutter create --platforms=android,ios`. This confirmed:

- 3.29.3: Dart 3.7.2 constraint, Gradle 8.10.2, AGP 8.7.0, Kotlin 1.8.22, Java/JVM 11, iOS 12.
- 3.38.10: Dart 3.10.9 constraint, Gradle 8.14, AGP 8.11.1, Kotlin 2.2.20, Java/JVM 17, iOS 13, LLDB init entries.
- 3.41.9: Dart 3.11.5; unchanged Android baseline; UIScene manifest, SceneDelegate, implicit-engine registration, and dynamically generated App.framework minimum OS version.
- 3.44.0: Dart 3.12.0; Gradle 9.1.0, AGP 9.0.1, Kotlin 2.3.20, AGP 9 compatibility flags and compiler-options layout; SwiftPM project dependency and scheme prepare action enabled by default.
- Both fresh templates already use Kotlin DSL. Therefore Groovy-to-Kotlin conversion is template alignment, not proven mandatory for upgrading an existing project.

## Official Flutter guidance used

- [Breaking-change index](https://docs.flutter.dev/release/breaking-changes): Flutter 3.29 removes Android embedding v1 Java APIs and Flutter 3.32 replaces `.flutter-plugins` with `.flutter-plugins-dependencies`.
- [Flutter 3.35 release notes](https://docs.flutter.dev/release/release-notes/release-notes-3.35.0): Flutter 3.35 raises the iOS minimum to 13.
- [Default Android ABI filters](https://docs.flutter.dev/release/breaking-changes/default-abi-filters-android): Flutter 3.35 configures supported ABI filters for non-debuggable builds.
- [Flutter 3.38 release notes](https://docs.flutter.dev/release/release-notes/release-notes-3.38.0): Flutter 3.38 raises the minimum supported Java version to 17 and introduces UIScene tooling/APIs.
- [UIScene adoption](https://docs.flutter.dev/release/breaking-changes/uiscenedelegate): UIScene APIs land in 3.38 and automatic eligible-app migration becomes default in 3.41.
- [Flutter 3.41 release notes](https://docs.flutter.dev/release/release-notes/release-notes-3.41.0): Flutter 3.41 template and host tooling changes.
- [Built-in Kotlin migration](https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin): Flutter 3.44 adds AGP 9 compatibility and prepares apps/plugins to migrate away from the legacy Kotlin Gradle Plugin.
- [Swift Package Manager for app developers](https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers): SwiftPM becomes the default native dependency manager in Flutter 3.44, with CocoaPods fallback.
- Flutter source commit `ddba36ac4a8` makes the built App.framework `MinimumOSVersion` derive dynamically from the active deployment target instead of the checked-in template plist.

When official guidance and one project's history differ, prefer official compatibility requirements and treat the project diff as an implementation example.
