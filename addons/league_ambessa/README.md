# 安蓓萨附加包（`league_ambessa`）

用户（2026-10-25）：「和原版不一样的地方要做附加包」——和克烈、约里克一样。

主包的安蓓萨是纯数据：数据读不到「离她多远」「直线上谁是第一个」「她挨没挨打」「一条线上谁最远」，所以主包里有四处只能近似。这个附加包把它们做成英雄联盟的样子：

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 暗袭（Q） | 扫中的**都**额外吃最大生命 `q_pct`% | 只有**刀尖**（离她 `q_tip`% 半径以外）扫到的才加伤 |
| 裂斩（Q 第二段） | 加伤给**技能的目标** | 加伤给**直线上的第一个敌人**（离她最近的） |
| 铁令（W） | 砸地**总**对英雄加伤最大生命 `w_pct`% | 只有格挡时**被敌方英雄或野怪打到**，砸地才加伤，而且打中的所有敌人都加 |
| 公开处刑（R） | 闪到**技能的目标**身边 | 闪到她和目标这条线上（`r_range` 长、`r_w` 半宽）**最远的敌方英雄**身边 |

暗袭、裂斩的基础伤害、血戮（E）、龙犬诡步（被动）、铁令的护盾两边一样。英雄联盟里还有两处这里不做：**能量**（团战经理没有这种资源）和**大招被动的技能吸血**（引擎不告诉被动「她的技能打出了多少伤害」）；大招被动的护甲穿透两边一样（数据的 `defence_penetration`）。

## 怎么接上的

`mod.override_info` 把主包的安蓓萨换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_ambessa.py` 的 `native=1` 生成）；`passive` 是本包的 `league_ambessa:matriarch`，参数来自主包参数表 P（`build_ambessa.ADDON_KEYS`）：

- 横扫给扫中的挂 3 拍 `league_ambessa_q_edge`、给她挂 `league_ambessa_q_on`，副本里不再有最大生命的那部分；本包看到 `q_on` 就对带 `q_edge`、离她 `q_r × q_tip%` 以外的单位造成最大生命 `q_pct`% 的物理伤害（`deal_damage_typed`，`Ad`），播 `q_tip`；
- 裂地重击的直线给打中的挂 `league_ambessa_q2_first`、给她挂 `q2_on`，副本里不再有对技能目标的加伤；本包把最大生命 `q2_pct`% 给其中离她最近的一个；
- 拒斥格挡时给她挂 `league_ambessa_w_on`（格挡那几拍）；这期间 `on_damaged` 的攻击者是敌方英雄或野怪（`Champion` / `Jungle` / `Epic`）时本包给她挂 `league_ambessa_w_hit`，副本的砸地只在有 `w_hit` 时对打中的所有敌人加最大生命 `w_pct`%（播 `w_crit`）；
- 大招到出手那一拍只给目标挂 `league_ambessa_r_aim`、给她挂 `league_ambessa_r_go`，副本里不再有数据的闪现、按住和砸下；本包找出线上最远的敌方英雄，把她放到它身边（`entity_set_pos`，两人半径之和那么远），眩晕 `r_sup` 拍（按住，播 `r_pin`），`r_slam` 拍后砸下：`r_dmg` + `r_ratio`% 攻击 + 最大生命 `r_pct`% 物理伤害、眩晕 `r_stun` 拍（播 `r_crash`），再接连招——摘掉 `q_cd`、`w_cd`，挂 `q_go`（数据的控制器读它马上横扫，横扫打中又接重击），挂强化普攻 `pw`（攻速 `pw_as`%，龙犬之步）；免控（`cc_immune`）的不眩晕；
- 普攻（龙犬诡步和铁令写在里面）、暗袭和公开处刑的说明换成附加包自己的文字（`description.league_ambessa.attack` / `.skill` / `.ult`），游戏里看说明就知道副本有没有生效。

状态都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 接入（2026-10-25，主包 0.219.0）

- `override/` 和 `text/champion.i18n` 由 `make_override.py` 写（先核对主包的 `league/champion/league_ambessa.data_champion`
  就是参数表 P 的那一份）；技能名是客户端里的官方名字（Data Dragon 16.21.1，和 `tools/kit/setup_ambessa.py` 一样）。
- `mod.override_info` 两条映射（主包安蓓萨换成副本、文字合并），`league_addons/src/lib.rs` 里登记（`mod ambessa;`、
  `ambessa::register`），`mod.mod_info` 要 `league` 0.219.0 以上。
- 特效（`tools/art/import_ambessa_fx.py`）：`q_tip`、`w_crit` 只有附加包播；`r_pin`、`r_crash` 两边共用。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_ambessa`：单元测试（参数、刀尖的距离、线上最远的英雄、落脚点、砸下的数、名字和数据一致）。
- 主包的安蓓萨改了以后重新跑 `python addons/league_ambessa/make_override.py`（它先核对主包的 `league_ambessa.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致；`--check` 只核对不写）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ambessa.log`：`SPAWN`、刀尖 `TIP`、第一个 `FIRST`、挨打 `BRACE`、大招 `R`（瞄的谁、线上最远的是谁、闪了多远）和 `SLAM`。
