# 艾克时间倒转附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里艾克的 R「时空断裂」随时回到 4 秒前的位置，按这 4 秒里损失的生命加成治疗，玩家残血时用它逃命，或者回到人堆里打一套。主包是纯数据：引擎不记单位过去的位置，也读不到受到的伤害，R 改成施放时留锚点、4 秒后自动回来，治疗固定。**不装这个附加包，主包的艾克也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 回到哪里 | 施放时留锚点，4 秒后回到锚点 | 施放时立刻回到 4 秒前的位置（刚复活不到 4 秒就回到复活后最早的位置） |
| 治疗 | 150 + 80% 法强 | 150 + 80% 法强，这 4 秒每损失 1% 最大生命 +4%，最多 +200%（损失 50% 时加满） |
| 落地 | 短暂无敌，周围 35000 内 150 + 100% 法强魔法伤害 | 一样 |
| 什么时候放 | 30000 内有敌方英雄就放 | 生命不高于 35%、这 4 秒掉了 30% 以上、回去的地方 35000 内有 2 个以上敌方英雄、或那里有人吃得下落地这一下时才放 |

## 怎么做的

- `mod.override_info` 把艾克换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：R 去掉锚点（`league_ekko_r_anchor` 投射物、`league_ekko_chrono` / `league_ekko_lives` 两个 buff、全息残影），施放时播离开的画面、给艾克挂 3 tick 的 `league_ekko_rewind_go`；2 tick 后跑主包的落地（无敌、画面、声音、治疗、伤害），只是不再 `Teleport`。R 的说明开头加【附加包】。
- 被动 `league_ekko_rewind:rewind` 每 tick 记下艾克的位置和生命（240 tick），看到旗子就把他放回最早的那个位置（`entity_set_pos`），按这段时间生命的下降（回血不抵）补治疗。数字在英雄数据的 `passive.params`。
- AI 钩子 `league_ekko_rewind:ult` 自己也记一份轨迹，按上表决定放不放：AI 想放但不是时候，改成普攻它的目标；AI 没想放但是时候了（R 好了、等级够、不在放别的技能），就替它放。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_ekko_rewind` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 艾克 R 的说明开头是「【附加包】回到 4 秒前的位置」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ekko_rewind.log`：`REWIND #n: back 240 ticks to (x, y), hp 210 -> 640 then, lost 520/1400, heal 310 + 460`；`R HELD`（AI 想放但不是时候）。

## 开发

- `python addons/league_ekko_rewind/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里艾克改了就重跑。
- `cargo test -p league_ekko_rewind`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
