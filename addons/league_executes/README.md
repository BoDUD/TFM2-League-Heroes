# 斩杀附加包（测试版 v0.1.0，可选）：伊芙琳、阿卡丽

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里伊芙琳的 R「最终抚慰」对生命 30% 以下的目标伤害 ×2.4，阿卡丽的 R2「完美刺杀」按目标已损失生命多 0–200%。主包是纯数据，读不到生命，两人都改成按她自己最近打中英雄的次数分档加伤。**不装这个附加包，主包的两人也是完整的**。

| 英雄 | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 伊芙琳 R | 150 + 75% 法强，最近每打中英雄一次 +35%（最多 ×2.4） | 150 + 75% 法强，对生命不高于 30% 的目标 ×2.4 |
| 阿卡丽 R2 | 86 + 43% 法强，两段之间每命中英雄一次 +25%（最多 +200%） | 86 + 43% 法强，按目标已损失生命最多 +200%（损失 70% 时加满） |

## 怎么做的

- `mod.override_info` 把两人换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：R 的分档加伤链（伊芙琳 `league_evelynn_h4`..`h1`，阿卡丽 `league_akali_r_s8`..`s1`）换成只打基础那一下，再给被打中的目标挂一个 3 tick 的标记（`league_executes_ev_hit` / `league_executes_ak_hit`）；R 的说明开头加【附加包】。
- 被动 `league_executes:evelynn` / `:akali` 每 tick 找身上有标记的敌人，读他的生命，补魔法伤害（`deal_damage_typed`，`Ap`，吃魔抗），数字在英雄数据的 `passive.params`。
- 生命是在基础那一下打完之后读的（同一 tick 的伤害已经结算），所以伊芙琳的「30% 以下」比英雄联盟（打之前算）略宽一点。

## 在游戏里测

1. 主包（League of Legends Heroes 0.208.0 以上）要装着并启用。
2. 把 `league_executes` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 两人 R 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_executes.log`：`EXECUTE #n on #7: hp 210/1200, hit 300, +420 magic`。

## 开发

- `python addons/league_executes/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。两人在主包里改了就重跑。
- `cargo test -p league_executes`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
