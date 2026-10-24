# 锤石灯笼附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里锤石把 W「魂引之灯」扔给挨打的队友，队友点一下灯笼就被拉到锤石身边。主包是纯数据：引擎做不了「队友点灯笼」，灯笼飞向 50000 内一名随机友方英雄，只给护盾。**不装这个附加包，主包的锤石也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 灯笼给谁 | 50000 内随机一名友方英雄 | 50000 内有危险的友方英雄（生命不高于 45%，或身边 25000 内有 2 个以上敌方英雄），几个时挑生命比例最低的；都没危险就给最近的 |
| 护盾 | 自己和那名队友各 60 + 40% 法强，2.5 秒 | 一样 |
| 拉回来 | 没有 | 有危险的队友离锤石超过 15000、没被硬控时，拉到锤石身边（每 tick 3000） |

## 怎么做的

- `mod.override_info` 把锤石换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：Q 里灯笼那段 `RandomTarget`（`AllyNotSelf`，灯笼投射物 `league_thresh_w_lantern` 带护盾）换成原生效果 `league_thresh_lantern:throw`；Q 的说明开头加【附加包】。锤石自己的那份护盾不动。
- `throw` 挑人，用 `spawn_projectile` 放出主包的同一个灯笼（速度 5000，追着他飞）；灯笼到了跑 `league_thresh_lantern:land`：给他主包那份护盾（`entity_add_shield`，护盾画面 `league_thresh_w_shield` 跟着护盾消失）、播主包的声音，有危险就 `entity_pull` 把他拉到锤石身边（被莫甘娜黑盾之类免疫控制时拉不动）。
- 数字（50000、5000、60 + 40%、150 tick）在 `src/lib.rs`，`make_override.py` 对照主包检查。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_thresh_lantern` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 锤石 Q 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_thresh_lantern.log`：`LANTERN #n -> #7 (hp 300/1200, 2 enemies around, 32000 away) IN DANGER`、`LANDED #n on #7: shield 140, pulled 31000 in 8 ticks`。

## 开发

- `python addons/league_thresh_lantern/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里锤石改了就重跑。
- `cargo test -p league_thresh_lantern`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
