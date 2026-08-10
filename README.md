# Flutter SDK Upgrade Skill

用于检测并升级已有 Flutter 项目的 SDK 版本，同时迁移 Android 和 iOS 原生工程配置。

该 Skill 只使用 Flutter 的 `major.minor` 选择迁移规则。例如，`3.35.1` 和 `3.35.7` 都属于 `3.35`，两者之间的补丁升级只同步项目中的版本声明，不重复执行平台迁移。

## 支持范围

- 检测 asdf、FVM、`pubspec.yaml`、VS Code、Android 本地配置及 iOS CI 中的 Flutter 版本。
- 按顺序应用跨越的 Flutter 版本迁移规则。
- 升级 Android 的 Gradle、AGP、Kotlin、Java 和相关构建配置。
- 升级 iOS deployment target、Xcode scheme 和生命周期配置。
- 保留签名、Flavor、Bundle ID、Podfile hook、ProGuard 等已有项目定制。
- 检测版本来源冲突、补丁升级和非预期降级。

当前规则覆盖从 Flutter 3.27 到 3.38 的主要迁移点，包括 `3.29`、`3.32`、`3.35` 和 `3.38`。遇到未收录版本时，Skill 会要求参考 Flutter 官方迁移说明并比较临时生成的 Android/iOS 模板，不会直接猜测配置变化。

Web、macOS、Windows 和 Linux 不在适配范围内。

## 安装

将 `upgrade-flutter-sdk` 目录复制或链接到 Codex Skills 目录：

```text
~/.codex/skills/upgrade-flutter-sdk
```

安装后的目录结构应以 `SKILL.md` 为入口：

```text
~/.codex/skills/upgrade-flutter-sdk/SKILL.md
```

## 使用

在需要升级的 Flutter 项目中调用：

```text
使用 $upgrade-flutter-sdk 将当前项目升级到 Flutter 3.38.10。
```

Skill 会先检查 Git 工作区和当前 Flutter 版本，再给出并实施 Android/iOS 迁移，最后运行环境允许的分析、测试和构建命令。

也可以独立运行只读检测脚本，提前查看会跨越哪些迁移层级：

```bash
python3 /path/to/upgrade-flutter-sdk/scripts/inspect_flutter_project.py \
  /path/to/flutter-project \
  --target 3.38.10
```

添加 `--json` 可输出机器可读的检查结果。

## 目录结构

```text
upgrade-flutter-sdk/
├── SKILL.md                         # Skill 工作流与安全约束
├── agents/openai.yaml              # Codex 展示和默认提示配置
├── references/
│   ├── evidence.md                 # tcm-app 历史和官方资料依据
│   ├── migration-rules.md          # Android/iOS 详细迁移规则
│   └── migrations.json             # 检测脚本使用的版本规则索引
└── scripts/
    └── inspect_flutter_project.py   # Flutter 版本检测和迁移规划工具
```

## 开发校验

修改 Skill 后至少执行：

```bash
python3 -m py_compile upgrade-flutter-sdk/scripts/inspect_flutter_project.py
python3 -m json.tool upgrade-flutter-sdk/references/migrations.json >/dev/null
```

同时使用 Codex `skill-creator` 提供的 `quick_validate.py` 校验 `upgrade-flutter-sdk` 目录。

规则的历史依据和可信度说明见 [`evidence.md`](upgrade-flutter-sdk/references/evidence.md)。
