# 洛克附加包（`league_locke`）

用户（2026-10-26）：洛克「和英雄联盟不一样的地方要做附加包」——和特朗德尔、瑟庄妮、克烈、约里克一样。

主包的洛克是纯数据：数据读不到目标的当前生命、他自己的当前生命，也不知道谁死了，所以主包里有五处只能近似。这个附加包把它们做成英雄联盟的样子：

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 圣银穿心（被动） | 普攻附带固定的魔法伤害（`p_dmg` + `p_ap`% 法强） | 再加目标**已损失生命 `p_miss`%** 的魔法伤害 |
| 灵焰仪式（W，并入被动） | 每秒烧**最大生命** `w_cost`%，结束时回固定的数（`w_heal` + `w_heal_ap`% 法强） | 每秒烧**当前生命** `w_cost`%（不会把自己烧死），结束时补回烧掉的 `w_back`% |
| 万魔狱（R）的处决 | 每 `r_p` 拍打一下阈值那么多的真实伤害、下一拍补回去（低于阈值的就死了） | 被标记的英雄**当前生命低于最大生命 `r_exec`%**（每层封印 +`r_exec_step`%）就处决 |
| 封印和法器 | 标记期间参与击杀 = 一层封印（最多 3 层，死了就没），大招冷却压到 `r_cap`% | 处决的地方**掉下法器**（`r_drop` 拍），洛克走到 `pick_r` 以内捡起来：封印 +1（最多 3 层，**整局都在**），大招剩下的冷却少 `r_cap`% |
| 参与击杀刷新 E | 击杀窗口：被他打过的英雄的记号断了就算 | 被他打过（`p_win` 拍内）的敌方英雄倒下，谁打死的都算，E 立刻好 |
| W 的样子 | 和平常一样 | 灵焰仪式期间整身换成 W 的配色（第 0 步 B：深蓝 / 靛紫皮肤、白西装、发白光的眼镜、蓝水晶法器箱；用户：「洛克会变成蓝色吧？」） |

四个连招（钉中英雄 → E 好、闪到英雄身边 → 点燃 W、参与击杀 → E 刷新、大招标记 → Q 好）两边一样。

## 怎么接上的

`mod.override_info` 把主包的洛克换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_locke.py` 的 `native=1` 生成），`passive` 是本包的 `league_locke:exorcist`，参数（`build_locke.NATIVE_KEYS`）来自主包参数表 P：

- 副本的普攻给打中的单位挂 3 拍 `league_locke_p_hit`；本包读它的当前、最大生命，用 `deal_damage_typed`（`Ap`）补已损失生命那一段；
- 副本的 `league_locke_w_on` 只带攻速（移速分三段衰减照旧），**不自伤、不回血**；本包在它挂着时每 60 拍用 `deal_damage_typed`（`Fixed`）烧他当前生命的 `w_cost`%，记下实际掉的血，`w_on` 没了时 `heal` 回其中的 `w_back`%；
- 副本的大招**没有处决检查**，只给命中的英雄挂 `league_locke_r_mark`；本包每拍看挂着它的敌方英雄，低于处决线就打掉剩下的血（`Fixed`），在那里每 60 拍播一次 `league_locke_r_land`（地上的法器），他走近就捡（`entity_reduce_cooldown` 减大招冷却，播 `league_locke_r_seal`）；
- 副本**没有击杀窗口**；本包记下每个敌方英雄最近一次带着 `p_hit` / `league_locke_q_mark` / `r_mark` 的拍数，它在 `p_win` 拍内倒下就拿掉他身上的 `league_locke_e_cd`（播 `league_locke_p_reset`）；
- `view.rs`（league_kled 的做法，同一个显示处理表的槽）：名字是 `league_locke` 的实体身上有 `league_locke_w_on` 时，正在播的 idle / run / hit / attack / skill / skill2 / ult / dash（E 之后的追击）换成洛克图里的 `w_*`；
- 四个技能的说明都换成本包自己的文字（`text/champion.i18n`，开头【附加包】，写的是上面的规则），游戏里看说明就知道副本生效了没有。

封印、地上的法器、W 的账都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量；封印和法器死了也留着。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_locke`：单元测试（参数、圣银穿心随已损失生命变大、处决线随封印变高且最多 3 层、捡法器减冷却、W 换图的名字、名字和数据一致）。
- 主包的洛克改了以后重新跑 `python addons/league_locke/make_override.py`（它先核对主包的 `league_locke.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致；`--check` 只核对不写；文字接入前用 `--draft`）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_locke.log`：`SPAWN`、圣银穿心 `STAKE`、灵焰仪式 `IGNITION over`、处决 `EXECUTE`（`SEALED` = 掉了法器）、捡法器 `PICKUP`、参与击杀 `TAKEDOWN`、换图 `W LOOK`。
