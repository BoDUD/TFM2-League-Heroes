# 瑟提豪意附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里瑟提的「豪意」就是他受到的伤害，W「蓄意轰拳」的护盾是全部豪意，正中的真实伤害也随豪意涨。主包是纯数据，读不到受到多少伤害：豪意按挨打的**次数**算（最多 5 层），W 按层数分 6 档。**不装这个附加包，主包的瑟提也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 豪意 | 挨打一次一层，最多 5 层，4 秒没挨打就散 | 最近 4 秒受到的伤害（回血不抵），最多 50% 最大生命 |
| W 护盾 | 50 + 20% 攻击力，每层 +30 + 25% | 50 + 20% 攻击力 + 全部豪意 |
| W 正中真实伤害 | 30 + 30% 攻击力，每层 +10 + 8% | 30 + 30% 攻击力 + 25% 豪意 |

## 怎么做的

- `mod.override_info` 把瑟提换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：W 的豪意分档链（`league_sett_grit_5` .. `1`）只留最后一档（没有豪意时），再给瑟提挂 3 tick 的 `league_sett_grit_spend`；这一档正中的两条线（`league_sett_w_true_0` / `_truew_0`）给打中的人多挂 3 tick 的 `league_sett_grit_hit`；W 的说明开头加【附加包】、豪意的两句换掉。
- 被动 `league_sett_grit:grit` 每 tick 记下他生命的下降，最近 240 tick 的和就是豪意；看到 `spend` 就给他豪意那么多的护盾（180 tick，同主包），豪意清零；之后 60 tick 内看到 `hit` 就补真实伤害（`Fixed`）。数字在 `passive.params`（`cap` 50、`true` 25）。
- 头顶的豪意层数画面还是主包按次数挂的，和真正的豪意不一定一样。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_sett_grit` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 瑟提 W 的说明开头是「【附加包】受到的伤害积攒为豪意」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sett_grit.log`：`W #n: grit 420 (hp 900/2000, cap 1000) -> shield +420`、`W #n center on #7: +105 true damage`。

## 开发

- `python addons/league_sett_grit/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里瑟提改了就重跑。
- `cargo test -p league_sett_grit`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
