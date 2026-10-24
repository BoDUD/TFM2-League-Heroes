# 大招瞄准附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

只有 AI 钩子，不换任何英雄的数据：AI 放大招时，挑英雄联盟玩家会挑的目标。**不装这个附加包，主包的英雄也是完整的**。

| 英雄 | 主包（AI 自己挑） | 装了附加包 |
|---|---|---|
| 墨菲特 R 势不可挡 | 点一名敌方英雄（常常是离得最近的），撞起他身边 30000 内的人 | 改点射程（75000）内身边敌方英雄最多的那个（一样多就照 AI 的）；R 好了、有人身边能撞起 3 个以上英雄时，AI 没想放也放 |

## 怎么做的

- AI 钩子 `league_ult_aim:malphite`：每 tick 数射程内每个敌方英雄身边 30000（主包 R 落地的范围）内有几个敌方英雄，按上表改 AI 的输入。R 的冷却和等级自己看；AI 在放别的技能或回城时不抢着放。
- 冲锋、击飞、伤害、画面都是主包数据里的那一套。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_ult_aim` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，重启游戏。
3. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ult_aim.log`：`MALPHITE R -> #7 (3 champions around), the AI had #5`。

## 开发

- `cargo test -p league_ult_aim`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
