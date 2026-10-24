# 莎弥拉边走边射附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。做莎弥拉 R 时用户选的是「这个不能走的话可以改RUST文件」。

英雄联盟里莎弥拉的 R「炼狱扳机」旋转连射 2 秒，期间能走，玩家追着残血的人走、把更多的人留在枪口里。主包是纯数据：旋转是施法动作，动作期间引擎不让她走，所以原地转。**不装这个附加包，主包的莎弥拉也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| R 期间 | 原地旋转连射 2 秒 | 旋转连射，同时走向 90000 内生命 + 护盾最少的敌方英雄，走到 30000 内站住；被硬控时不走 |
| 枪、伤害、生命偷取、画面 | 主包 | 主包（一样） |

## 怎么做的

- `mod.override_info` 把莎弥拉换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：只加被动 `league_samira_r:walk`，R 的说明开头加【附加包】、「原地旋转连射」换成「旋转连射并走向残血的敌人」。
- 被动在她身上有主包 R 的 `league_samira_r_on`（120 tick）时，每 tick 用 `entity_set_pos` 朝目标走一步。步长是她平时走路时每 tick 挪的距离（最近 120 次的中位数，冲刺、传送不算），没量到用 550。撞墙时宿主拒绝那一步，她就站着。
- 硬控：眩晕、击飞、禁锢、嘲讽、恐惧、魅惑、强制位移（主包里被控制会打断旋转动作，枪照样打）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_samira_r` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 莎弥拉 R 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_samira_r.log`：`R #n DONE: walked 21000 in 60 steps (0 refused), step 350`。

## 开发

- `python addons/league_samira_r/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里莎弥拉改了就重跑。
- `cargo test -p league_samira_r`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
