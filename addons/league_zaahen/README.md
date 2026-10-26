# 亚恒附加包（`league_zaahen`）

用户（2026-10-26）：亚恒「和英雄联盟不一样的地方都要做附加包」——和斯卡纳、特朗德尔、克烈一样。

主包的亚恒是纯数据：数据数不清每一下伤害、看不到致命伤害、三个技能位放不下第四个技能、回血只能按攻击力算，所以主包里有四处只能近似。这个附加包把它们做成英雄联盟的样子：

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 不落之志（果决） | 一串标记一层一层叠：控制器每 3 拍看一次，同一拍里的几下只算一层；每层攻击力 +`det_ad`%，满 `det_n` 层换成 +`full_ad`% | **每一下打在敌方英雄身上的伤害**都算一层（普攻、Q 的每一斩、上挑、W、E、R），每层攻击力 +`det_pct`%，最多 `det_n` 层、叠满翻倍；最后一下之后 `det_t` 拍没打中英雄，每 30 拍掉一层 |
| 叠满后的复活 | 数据看不到致命伤害：叠满时给一个 `rv_sh` + `rv_sh_r`% 攻击力的护盾（每 `rv_cd` 拍一次） | **叠满时受到致命伤害就倒下**：生命停在 1，放逐 `rv_rise` 拍（无敌、选不中、不能行动），慢慢回到最大生命 `rv_hp`%，再展翼站起来、果决叠满；每 `rv_cd` 拍一次。别人给的「不死」在身上时不触发 |
| 赤金突袭（E） | 三个技能位放不下：并进 W，拽完人原地绕身一斩 | **有自己的技能位**：每 `e_cd` 拍一次，`e_reach` 内有敌方英雄、他能行动时，朝最近的那个冲过去（最多 `e_dash`，停在让对方正好落在外圈的地方），落地绕身斩：内圈 `e_r0`、外圈 `e_r`，`e_dmg` + `e_ratio`% 攻击力，外圈多 `e_out`% 并加最大生命 `e_pct`% 的魔法伤害；W 不再带绕身斩 |
| 暗裔长刀的回血 | 每斩回固定的 `q_heal` + `q_heal_r`% 攻击力 | 每斩回**最大生命 `q_hp`%**（打英雄；别的单位一半），英雄联盟的算法 |

两连斩和上挑、W 的刺出 / 眩晕 / 拽回、大招的升空 / 免控减伤 / 插刀 / 每个英雄回血、R 的被动护甲穿透、四个连招（W 拽中英雄 → Q 马上好；Q 挑飞英雄 → 大招冷却缩短；大招砸中英雄 → 果决涨一大截；果决叠满 → Q、W 马上好）两边一样。

## 怎么接上的

`mod.override_info` 把主包的亚恒换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_zaahen.py` 的 `native=1` 生成），`passive` 是本包的 `league_zaahen:darkin`，参数（`build_zaahen.NATIVE_KEYS`）来自主包参数表 P，`src/lib.rs` 的默认值和它核对：

- 副本里没有果决的标记阶梯和护盾：本包在 `on_attack`（他打出的每一下伤害）里给敌方英雄算层，挂 `league_zaahen_det` / `league_zaahen_full`（攻击力），叠满时挂 `league_zaahen_fill`，数据看到就播叠满的画面、刷新 Q 和 W（连招留在数据里）；
- 复活：叠满且冷却好了时一直挂「不死」`league_zaahen_rv_guard`，生命停在 1 就放逐他（先去掉大招的 `r_guard`：免控时放逐会被拒），放逐的画面是数据的 `league_zaahen_rv_rise_r` / `_l`（`league/effects/league_zaahen_rise`，高清特效表：他倒下、拄刀跪起、展翼站起来，光柱在后面；特效图不会镜像，所以左右各画一份，按最近的敌方英雄选朝向），结束时播 `p_full`；
- 赤金突袭：本包冲刺时挂 `league_zaahen_e_rush`（数据播冲刺的动作 `dash`），用 `entity_set_pos` 一拍一拍把他挪过去（期间定身、禁普攻、禁技能），落地挂 `league_zaahen_e_go`（数据播绕身斩 `skill3` 和画面），`e_hit` 拍后本包结算内外圈的伤害；
- 暗裔长刀：副本的每一斩给打中的单位挂 3 拍 `league_zaahen_q_mark`，本包看到就回血。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_zaahen`：单元测试（参数、果决的攻击力和掉层、复活补血、冲刺停的位置、内外圈伤害、复活画面的朝向、副本用到的标记名）。
- 主包的亚恒改了以后重新跑 `python addons/league_zaahen/make_override.py`（它先核对主包的 `league_zaahen.data_champion` 和参数表一致、`src/lib.rs` 的默认值和 P 一致；`--check` 只核对不写）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zaahen.log`：`SPAWN`、`FULL`（果决叠满）、`REVIVE` / `RISEN`（倒下、站起来）、`RUSH`（赤金突袭冲向谁）、`SPIN`（打中几个英雄、几个在外圈）、`GLAIVE`（每斩回多少血）。
