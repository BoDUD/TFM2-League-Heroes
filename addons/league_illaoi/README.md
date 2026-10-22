# 俄洛伊附加包（`league_illaoi`）

用户（2026-10-23）：「俄洛伊不用做附加包吗」「附加包就按这四项做」。

主包的俄洛伊是纯数据：触手是她身前、躯壳身上、大招砸中的人身上的几块区域，按固定节奏抽最近的英雄；灵魂试炼的灵魂只是「受到伤害增加」，到时间才变躯壳。数据读不到地图的墙，也读不到谁身上有什么标记。这个附加包把这四件事做成英雄联盟那样：

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 触手长在哪 | 普攻时长在她身前 `t_place`，躯壳、大招砸中的人身上 | 读这局地图的墙格子，长在离她（躯壳、被砸中的人）最近的**墙边**（`p_reach` 内；附近没墙就照旧长在身前 / 身上）；同时最多 6 条，新的挤掉最老的 |
| 触手抽谁 | 每 `t_per` tick 先抽英雄、再抽别的 | **先抽被严酷训诫打中的（`w_mark`）和躯壳（`e_vessel`）**，再抽英雄，再抽别的；严酷训诫新打中谁，`t_r` 的 1.5 倍内的每条触手隔 `w_gap` tick 依次抽他一下 |
| 灵魂分担伤害 | 灵魂在身上时**谁打他**都多 `e_echo`%（`damaged_amplify`） | 只有**她打他的每一下**（普攻和技能，`on_attack`）多算 `e_echo`%，和英雄联盟打灵魂传到本体一样只算她的 |
| 灵魂拉断 | 灵魂 `e_t` tick 到了才变躯壳 | 记下灵魂被扯出来时他站的地方，**他走出 `e_leash` 外**就立刻变躯壳（播灵魂碎裂、身边长触手）；没走远的到时间也变 |

## 怎么接上的

`mod.override_info` 把主包的俄洛伊换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_illaoi.py` 的 `native=1` 生成）：

- 普攻长触手时给她挂 2 tick 的 `league_illaoi_p_new`，过界信仰落地挂 2 tick 的 `league_illaoi_r_new`，数据不再自己长触手（交给本包）；
- 严酷训诫的目标照旧挂 `league_illaoi_w_mark`，数据不再自己抽它；灵魂试炼只挂 `league_illaoi_e_spirit`（没有受到伤害增加）和减速，躯壳交给本包；
- `passive` 是本包的 `league_illaoi:prophet`，参数是主包参数表 P 里的那几项（`NATIVE_KEYS`）；
- 普攻和灵魂试炼的说明换成附加包自己的文字（`description.league_illaoi.attack` / `.skill2`），游戏里看说明就知道副本有没有生效。

墙格子用卡密尔附加包内置的三张地图（[`../league_camille_wall/src/maps.rs`](../league_camille_wall/src/maps.rs)，每格 32000），按场上单位站在哪认出是哪张图。触手的画面、伤害、回血都由被动直接放（`play_view_effect` 在位置上放 `league_illaoi_tentacle`、抽中时在目标处放 `lash` / `p_slam` / `p_hit`，`deal_damage_typed` 物理伤害），她死了触手照旧站着、照旧抽。每个计时都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_illaoi`：单元测试（参数、墙边的位置、认地图、先抽谁、没墙时身前）。
- 主包的俄洛伊改了以后重新跑 `python addons/league_illaoi/make_override.py`（它先核对主包的 `league_illaoi.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_illaoi.log`：`SPAWN`、每条触手 `GROW (attack / leap of faith / vessel): ... on a wall's edge / in the open`、`STRIKE (tentacle / marked / lesson)`、`LESSON`、`SPIRIT`、`ECHO`、`VESSEL (walked off its spirit / spirit ran out)`，每 30 秒一行 `WATCH` 汇总。
