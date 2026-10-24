# 霞羽毛附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里霞收回羽毛时，同一个敌人被 3 根羽毛打中才定身。主包是纯数据，数不了每个目标各被打了几次：一次收回里打中**英雄**的第 3 次起（不管是不是同一个人），被打中的英雄定身。**不装这个附加包，主包的霞也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 定身条件 | 一次收回打中英雄的第 3 次起（A 一根、B 两根，B 的第二根就定身） | 同一个英雄被 3 根羽毛打中（60 tick 内） |
| 定身时长、画面、伤害 | 1.25 秒，主包 | 一样 |

## 怎么做的

- `mod.override_info` 把霞换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：收回的羽毛打中英雄时的 27 处计数梯子（`league_xayah_rh2` / `rh1`，记在霞身上）都换成原生效果 `league_xayah_feathers:hit`；Q 的说明开头加【附加包】、定身条件换掉。
- 原生效果在命中时由数据调用，`input` 就是被打中的人：在他身上数（`league_xayah_feathers_1` / `_2`，60 tick），第 3 根用 `apply_cc` 禁锢 75 tick，挂主包的定身画面 buff `league_xayah_e_bind`，播主包的画面和声音，然后从头数。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_xayah_feathers` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 霞 Q 的说明开头是「【附加包】」、写着「同一个英雄被一次收回的3根羽毛打中时」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_xayah_feathers.log`：`FEATHER #n on #7: 3 -> 0 ROOTED`。

## 开发

- `python addons/league_xayah_feathers/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里霞改了就重跑。
- `cargo test -p league_xayah_feathers`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
