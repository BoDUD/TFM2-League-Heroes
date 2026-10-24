# 奥瑞利安·索尔附加包（`league_aurelionsol`）

用户（2026-10-24）选技能方案时定了：被动「星海焕然：星尘永久叠层强化各技能」，技能 2「星芒凝汇：黑洞拉人，中心处决残血」。

主包的奥瑞利安·索尔是纯数据：数据读不到生命，也没有「复活时」这个时机，所以主包里有两处只能近似。这个附加包把它们做成英雄联盟的样子：

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 星海焕然（星尘） | 每层是一个永久 buff（`league_aurelionsol_d1`…`d15`，各带 `d_ap`% 法强），死亡时引擎清掉全部 buff，每条命从零叠起 | 活着时记下每一层，死亡清掉后原样补回（最多 `d_max` 层） |
| 星芒凝汇（黑洞中心） | 中心每秒打英雄最大生命的 `e_exec`%（真实伤害，处决的替身） | 同样的伤害，另外英雄生命低于 `e_low`% + 每层星尘 `e_low_d`%（默认 5% + 1%/层，最多 20%）就直接处决 |

天瀑的充能（`league_aurelionsol_c1`…）不记：放天瀑时主包自己会清掉它们，死后从零充。

## 怎么接上的

`mod.override_info` 把主包的奥瑞利安·索尔换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_aurelionsol.py` 的 `native=1` 生成）：

- 黑洞中心每次打到英雄时多跑原生效果 `league_aurelionsol:core`：读目标真实的生命和护盾，低于处决线就打出「生命 + 护盾 + 1」的真实伤害（梅尔附加包的做法）；处决线按他身上的星尘层数算；
- `passive` 是本包的 `league_aurelionsol:stardust`，参数 `d_max`、`e_low`、`e_low_d` 来自主包参数表 P：记下他身上每一层 `league_aurelionsol_d<n>`，少了就补回（卑尔维斯附加包的做法：层数只会变多，所以少了只会是死亡清掉的）；出生时把参数按（这局的种子, 单位）记一份给原生效果；
- 普攻和技能 2 的说明换成附加包自己的文字（`description.league_aurelionsol.attack` / `.skill2`，写着「死亡后保留」和处决线），游戏里看说明就知道副本有没有生效。

记下的层在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干）。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_aurelionsol`：单元测试（参数、层的名字、处决线、死后补回）。
- 主包的奥瑞利安·索尔改了以后重新跑 `python addons/league_aurelionsol/make_override.py`（它先核对主包的 `league_aurelionsol.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aurelionsol.log`：`SPAWN`、叠层 `STACK`、死亡 / 复活 `DEAD` / `ALIVE`、补回 `KEEP`、处决 `EXECUTE`（目标、生命、处决线、星尘层数）。
