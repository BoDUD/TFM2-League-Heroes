# 贝蕾亚附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

主包是纯数据：读不到墙，E 击退的英雄一律眩晕；血莽、彻底血狂期间 AI 照常挑目标（还会回城）；大招的血狂固定 6 秒。**不装这个附加包，主包的贝蕾亚也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| E 惊吼的眩晕 | 被击退的英雄都在击退结束时眩晕 1 秒 | 只眩晕撞上东西的：16 tick 的击退结束时被推出去不到 40000 的 65%（墙、地图边、别的单位挡住了） |
| 血莽 / 彻底血狂 | AI 照常挑目标，也会回城 | 普攻、走路、回城都改成普攻：彻底血狂时打猎物，否则打 50000 内最近的敌方英雄，没有就打 30000 内最近的敌人；放技能不拦 |
| 彻底血狂 | 6 秒 | 猎物活着就一直续（最多 15 秒），数值照主包 |

## 怎么做的

- `mod.override_info` 把贝蕾亚换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：E 里只打英雄的那段（16 tick 后眩晕 60 tick）换成给他挂 `league_briar_frenzy_e`；E 和 R 的说明开头加【附加包】、改掉那几个字。
- 被动 `league_briar_frenzy:frenzy`：看到标记就记下他的位置，16 tick 后量他被推出去多远，不到 65% 就 `apply_cc` 眩晕 60 tick，播主包的眩晕画面和声音；彻底血狂 `league_briar_hema` 快结束、猎物（身上有 `league_briar_r_mark`）还活着就照主包的数值续 60 tick，猎物的标记也续上。
- AI 钩子 `league_briar_frenzy:lock`：她身上有血莽或彻底血狂时，按上表改 AI 的输入。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_briar_frenzy` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 贝蕾亚 E 的说明开头是「【附加包】」、写着「撞上墙或单位的英雄」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_briar_frenzy.log`：`E #n on #7: pushed 14000 of 40000 -> hit a wall, STUNNED`、`FRENZY LOCK on #9`。

## 开发

- `python addons/league_briar_frenzy/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里贝蕾亚改了就重跑。
- `cargo test -p league_briar_frenzy`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
