# Flutter SDK Upgrade Skill

检测并升级已有 Flutter 项目的 SDK 版本，同时迁移 Android 和 iOS 原生工程配置。

## 安装

```bash
npx skills add and2long/flutter_upgrade_skill --skill upgrade-flutter-sdk -g
```

去掉 `-g` 可安装到当前项目。仓库发布到 GitHub 后即可使用上述命令。

## 使用

在 Flutter 项目中调用：

```text
使用 $upgrade-flutter-sdk 将当前项目升级到 Flutter 3.38.10。
```

Skill 会检测项目当前使用的 Flutter 版本，按顺序执行跨版本的 Android/iOS 配置迁移，并运行环境支持的分析、测试和构建验证。

## 主要能力

- 从 asdf、FVM、`pubspec.yaml`、VS Code 和 CI 配置检测 Flutter 版本。
- 只按 `major.minor` 选择迁移规则；例如 `3.35.1 → 3.35.7` 不重复执行平台迁移。
- 升级 Android 的 Gradle、AGP、Kotlin、Java 等构建配置。
- 升级 iOS deployment target、Xcode scheme 和生命周期配置。
- 保留签名、Flavor、Bundle ID、Podfile hook 和 ProGuard 等项目定制。
- 检测版本来源冲突并阻止非预期降级。

当前规则覆盖 Flutter `3.29`、`3.32`、`3.35` 和 `3.38`。未收录的版本会参考 Flutter 官方迁移说明并比较临时生成的 Android/iOS 模板。

仅适配 Android 和 iOS，不处理 Web、macOS、Windows 和 Linux。

## 独立检测

只查看迁移计划、不修改项目：

```bash
python3 /path/to/upgrade-flutter-sdk/scripts/inspect_flutter_project.py \
  /path/to/flutter-project \
  --target 3.38.10
```

添加 `--json` 可输出机器可读结果。详细规则见 [`migration-rules.md`](upgrade-flutter-sdk/references/migration-rules.md)。
