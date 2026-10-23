# 俄洛伊附加包（`league_illaoi`）

用户（2026-10-23）：「俄洛伊不用做附加包吗」「附加包就按这四项做」。

主包的俄洛伊是纯数据：触手是她身前、躯壳身上、大招砸中的人身上的几块区域，按固定节奏抽最近的英雄；灵魂试炼的灵魂只是「受到伤害增加」，到时间才变躯壳。数据读不到地图的墙，也读不到谁身上有什么标记。这个附加包把这四件事做成英雄联盟那样：

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 触手长在哪 | 普攻时长在她身前 `t_place`，躯壳、大招砸中的人身上，活 `t_life` | **按被动自己的冷却长**（1 级 `p_cd_1`、18 级 `p_cd_18`，英雄联盟 20 – 10 秒，不再跟着普攻长），长在她附近最近的**墙边**（`p_reach` 内，没墙就在她身边 `t_place`），**活 `t_long`（60 秒）**、同时最多 `t_most` 条；画面冒出来、摆动（活多久摆多久）、沉下去 |
| 触手抽谁 | 每 `t_per` tick 像炮台一样抽附近的敌人 | **平时不动**（英雄联盟）：严酷训诫打中的人（够得着的每条依次抽一下）、灵魂被扯出来的英雄和躯壳（每 `t_per` tick）；Q 并进被动：她打中敌人时够得着的触手抽一下（`q_cd` 一次）；大招期间每 `r_per` tick 抽附近的敌方英雄 |
| 灵魂分担伤害 | 灵魂在身上时**谁打他**都多 `e_echo`%（`damaged_amplify`） | 只有**她打他的每一下**（普攻和技能，`on_attack`）多算 `e_echo`%，和英雄联盟打灵魂传到本体一样只算她的 |
| 灵魂拉断 | 灵魂画在他身上（被身体挡住），`e_t` tick 到了才变躯壳 | 灵魂**朝她扯出 `e_pull` 站在外面**（`e_soul`），和他之间一直连着**灵魂线**（`e_tether`）；**他走出离灵魂 `e_leash` 外**就立刻变躯壳（播灵魂碎裂、身边长触手）；没走远的到时间也变 |

## 0.2.0：照英雄联盟的触手和看得见的灵魂

用户 2026-10-23：「俄洛伊触手乱长 和英雄联盟逻辑不一样 还有拉灵魂没有特效 完全看不出 也和英雄联盟不一样」，选了「墙边优先，没墙长身边」
「照联盟：W、灵魂、躯壳才抽」「灵魂站在外面+连线」。0.1.0 的触手跟着普攻每 6 秒长一条、只活 6 秒、像炮台一样自己抽人，场上几乎总是
一条、位置跳来跳去；灵魂是挂在他身上的 buff 画面，被身体挡住。现在触手按被动的冷却长、活一分钟、平时不动，只抽该抽的；灵魂站在
外面连着线。画面：tools/art/rig_illaoi.py `--tentacles` 给触手表加了 rise / sway / sink 三段（图不变，只加标签），
tools/art/fx_illaoi_tether.py 画灵魂线的一节（import_illaoi_fx.py 放进 league_illaoi_fx）。主包只有数据，读不到谁身上有标记，
触手照旧按固定节奏抽最近的敌人；新加的画面主包也带着，没装本包时不用。

之后用户又问「灵魂能雕刻出每个英雄的形状吗」「打灵魂时也没特效啊」：
- **每个英雄自己的灵魂**（「只要做英雄联盟的」）：tools/art/illaoi_souls.py 把主包每个英雄联盟英雄待机的第一帧（1x，和高清英雄在游戏里一样大）
  做成幽灵——轮廓原样、外缘一圈亮边、里面按明暗换成灵魂的青白色、暗的两档隔一个点去一个（看着半透明），3 帧闪动——放进
  `league_illaoi_souls`（每个英雄一个标签），`src/souls.rs` 记下有哪些。副本里每个英雄一条画面 `league_illaoi_soul_<id>`，本包按被扯出
  灵魂的英雄播他自己的；别的模组的英雄用通用的 `e_soul`。特效图不会跟着英雄转身，幽灵一直朝右。
- **打灵魂看得见**：她或触手打中灵魂被扯出来的英雄时，灵魂身上一闪（`e_echo`，fx_illaoi_tether.py 画的），一道鬼手（`e_grab`）
  顺着灵魂线飞回本体（`PULSE_SPEED`）。

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
