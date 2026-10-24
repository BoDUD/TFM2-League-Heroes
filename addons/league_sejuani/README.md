# 瑟庄妮附加包（`league_sejuani`）

用户（2026-10-24）：「没有免疫减速就做附加包」「和英雄联盟不一样的地方都是做附加包」。

主包的瑟庄妮是纯数据：数据读不到别的单位身上的 buff 和控制状态，也没有「免疫减速」和「受到伤害时」，所以主包里有四处只能近似。这个附加包把它们做成英雄联盟的样子：

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 永冻领域（霜冻叠满冻住） | 霜冻层数记在瑟庄妮自己身上（`f1`…`f3`），打不同的敌人也叠在一起 | 层数挂在**每个敌方英雄自己身上**（`league_sejuani_frost`），某一个满 `f_n` 层才冻住它 |
| 碎冰 | 只认她自己的眩晕（冻住、Q 击飞、R）之后的下一击 | 她打中的英雄**正被眩晕或击飞**就碎冰，**队友控的也算**；每个英雄单独冷却 `sh_cd` |
| 冰霜护甲 | 护甲、魔抗 + 韧性（游戏没有免疫减速，用韧性代替）；只有她自己出手才算进入战斗 | 护甲在身时每 tick 清掉她身上所有减速（**免疫减速**，副本不给韧性）；**受到伤害**也算进入战斗 |
| 极寒突袭 | 冲到目标为止，路上的敌人都击飞 | **撞到第一个敌方英雄就停下**（冲锋剩下的时间按在原地） |

英雄联盟里队友的近战普攻也会给敌人叠霜冻，两边都没做：附加包的接口只在自己英雄身上触发，看不到队友的普攻。

## 怎么接上的

`mod.override_info` 把主包的瑟庄妮换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_sejuani.py` 的 `native=1` 生成）：

- 普攻和凛冬之怒打中敌方英雄时，往它身上挂一层 `league_sejuani_frost`（头上的小雪花）和 3 tick 的 `league_sejuani_hit`；
- 冰霜护甲不给韧性；极寒突袭撞到第一个英雄时给她挂 2 tick 的 `league_sejuani_q_stop`；
- `passive` 是本包的 `league_sejuani:frost`，参数 `f_n e_stun e_dmg e_ap sh_cd sh_dmg sh_ap sh_pct q_t fa_out` 来自主包参数表 P：每 tick 数每个敌方英雄身上的霜冻，满了就摘掉、眩晕 `e_stun` tick、造成魔法伤害；看到 `hit` 标记时那个英雄正被眩晕 / 击飞就碎冰（标记看一次就摘）；护甲在身时摘掉移速为负的 buff；受伤时刷新 `league_sejuani_fight`；看到 `q_stop` 就把她按在撞到的地方 `q_t` tick；
- 普攻和极寒突袭的说明换成附加包自己的文字（`description.league_sejuani.attack` / `.skill`），游戏里看说明就知道副本有没有生效。

计时、碎冰冷却都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_sejuani`：单元测试（参数、伤害、减速的判断、每个英雄的碎冰冷却）。
- 主包的瑟庄妮改了以后重新跑 `python addons/league_sejuani/make_override.py`（它先核对主包的 `league_sejuani.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sejuani.log`：`SPAWN`、冻住 `FREEZE`、碎冰 `SHATTER`、清掉减速 `SLOW`、Q 停下 `STOP`。
