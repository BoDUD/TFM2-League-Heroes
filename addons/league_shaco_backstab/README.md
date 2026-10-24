# 萨科背刺附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里萨科从背后打到敌人就是背刺。主包是纯数据，读不到朝向：普攻和毒刃打中**被控制**的敌方英雄（被恐惧的人背对着他逃跑）才多一下背刺。**不装这个附加包，主包的萨科也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 普攻、毒刃的背刺 | 打中被控制的敌方英雄：+15 + 25% 攻击力 | 从背后打中敌方英雄：+15 + 25% 攻击力 |
| Q 落地那一刀、R 幻像 | 主包 | 一样 |

## 怎么做的

- `mod.override_info` 把萨科换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：两枚只打 `EnemyChampionInCC` 的分身弹（`league_shaco_a_bs` / `league_shaco_e_bs`）改成打所有敌方英雄，只给他挂 3 tick 的 `league_shaco_bs_ask`；普攻的说明开头加【附加包】、「被控制」换成「从背后」。
- 被动 `league_shaco_backstab:backstab` 每 tick 记下每个敌方英雄最近 10 tick 的位置：
  - 朝向：这 10 tick 走了 1500 以上就是他走的方向；站着不动（在打东西）就朝着离他最近的萨科一方英雄或小兵；
  - 背后：萨科在他朝向的反方向那一半；
  - 是就补物理伤害（`Ad`，吃护甲，数字在 `passive.params`，从主包读），播主包的背刺画面和声音。
- 被恐惧的人背对着萨科跑，照样算背刺；面对面打他不算。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_shaco_backstab` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 萨科普攻的说明开头是「【附加包】」、写着「从背后」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shaco_backstab.log`：`BACKSTAB #n on #7: +60 physical (12 of 40 hits from behind)`。

## 开发

- `python addons/league_shaco_backstab/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里萨科改了就重跑。
- `cargo test -p league_shaco_backstab`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
