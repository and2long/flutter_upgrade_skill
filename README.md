# Flutter SDK Upgrade Skill

[English](README.md) | [简体中文](README.zh-CN.md)

Detect and upgrade the Flutter SDK in existing projects while migrating Android and iOS host configuration.

## Install

```bash
npx skills add and2long/flutter_upgrade_skill --skill upgrade-flutter-sdk -g
```

Remove `-g` to install the skill in the current project instead.

## Use

Invoke the skill from a Flutter project:

```text
Use $upgrade-flutter-sdk to upgrade this project to Flutter 3.44.0.
```

The skill detects the current Flutter version, applies crossed Android/iOS migrations in order, and runs the validation supported by the environment.

## Features

- Detect Flutter versions from asdf, FVM, `pubspec.yaml`, VS Code, and CI configuration.
- Select migrations by `major.minor`; for example, `3.35.1 → 3.35.7` does not repeat platform migrations.
- Upgrade Android Gradle, AGP, Kotlin, Java, and related build configuration.
- Upgrade iOS deployment targets, Xcode schemes, and lifecycle configuration.
- Preserve signing, flavors, bundle IDs, Podfile hooks, ProGuard rules, and other project customizations.
- Detect conflicting version sources and prevent accidental downgrades.

The catalog currently covers Flutter `3.29`, `3.32`, `3.35`, `3.38`, `3.41`, and `3.44`. For uncataloged versions, the skill consults official Flutter migration guidance and compares disposable Android/iOS templates.

Only Android and iOS are supported. Web, macOS, Windows, and Linux are out of scope.

## Inspect only

Preview the migration plan without modifying the project:

```bash
python3 /path/to/upgrade-flutter-sdk/scripts/inspect_flutter_project.py \
  /path/to/flutter-project \
  --target 3.44.0
```

Add `--json` for machine-readable output. See [`migration-rules.md`](upgrade-flutter-sdk/references/migration-rules.md) for details.
