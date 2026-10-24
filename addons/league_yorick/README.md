# 约里克附加包（`league_yorick`）

用户（2026-10-25）：约里克「继续接入（文字、音效、注册、扩展包）」——和克烈、瑟庄妮一样，「和英雄联盟不一样的地方都是做附加包」。

主包的约里克是纯数据：数据读不到「这一铲打死了谁」，也读不到「室女跟着谁」，所以主包里有两处只能近似。这个附加包把它们做成英雄联盟的样子：

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 挖坟 | 临终仪式打英雄挖一座坟，打别的（小兵、野怪）**每两下**挖一座 | 打英雄照旧挖一座；打别的只有**这一铲打死了它**才挖一座（英雄联盟：击杀或英雄、大型野怪） |
| 室女的加伤 | 室女在场时，约里克普攻**任何**敌方英雄都额外造成最大生命 `r_pct`% 真实伤害 | 只有普攻**室女跟着的那个英雄**才加伤 |

坟满 3 座时的唤醒（雾行者 + 灵魂墙）、黑雾、室女本身两边一样。

## 怎么接上的

`mod.override_info` 把主包的约里克换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_yorick.py` 的 `native=1` 生成）：

- 临终仪式那一铲给约里克挂几拍（`q_win`）`league_yorick_q_win`，不再有「每两下」的规则；`passive` 是本包的 `league_yorick:shepherd`，参数 `r_pct g_t` 来自主包参数表 P：`q_win` 还在时每有一个小兵或野怪被他打死（`on_unit_kill`），就照数据的阶梯给他挂下一座坟（`league_yorick_g1` → `g2` → `g3`，各 `g_t` 拍，满了不再加）；
- 大招给室女的目标挂 `league_yorick_maiden`（大招持续时间），室女在场时普攻打中英雄给它挂 3 拍 `league_yorick_hit`；本包每拍看同时有这两个的敌方英雄，造成它最大生命 `r_pct`% 的真实伤害（`deal_damage_typed`，`Fixed`），然后摘掉 `hit`；
- 普攻（牧魂人写在里面）和海屿悼词的说明换成附加包自己的文字（`description.league_yorick.attack` / `.ult`），游戏里看说明就知道副本有没有生效。

计数都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_yorick`：单元测试（参数、坟墓阶梯、室女加伤的数、名字和数据一致）。
- 主包的约里克改了以后重新跑 `python addons/league_yorick/make_override.py`（它先核对主包的 `league_yorick.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致；`--check` 只核对不写）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yorick.log`：`SPAWN`、打死单位挖坟 `GRAVE`、室女目标加伤 `MAIDEN`。
