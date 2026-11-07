# 卑尔维斯附加包（`league_belveth`）

用户（2026-10-24）选技能方案时定了：「E 搠面皇锋并入大招：真身期间残血时自动转风暴（减伤 + 吸血，斩最低血敌人）」，被动「击杀英雄 / 大野怪永久叠攻速」。

主包的卑尔维斯是纯数据：数据读不到生命，也没有「复活时」这个时机，所以主包里有两处只能近似。这个附加包把它们做成英雄联盟的样子：

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 搠面皇锋（真身里的风暴） | 真身期间、`e_cd` 过了、`e_near` 内有两个敌方英雄就放 | 同样的风暴，但改成她**生命低于 `e_low`%**（默认 35%）时放，英雄联盟「残血时转风暴」 |
| 溶烛化紫（击杀叠的永久攻速） | 每层是一个永久 buff（`league_belveth_l1`…`l8`），死亡时引擎清掉全部 buff，每条命从零叠起 | 活着时记下每一层，死亡清掉后原样补回（最多 `l_max` 层） |

英雄联盟里击杀大型野怪也叠层，两边都没做：数据和引擎接口都分不出一营野怪里哪只是「大的」。

## 怎么接上的

`mod.override_info` 把主包的卑尔维斯换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_belveth.py` 的 `native=1` 生成）：

- 风暴的判断改读标记 `league_belveth_low`（主包读「两个敌方英雄贴身」）；
- `passive` 是本包的 `league_belveth:banquet`，参数 `e_low`、`l_max` 来自主包参数表 P：每 tick 读她的生命，低于 `e_low`% 就挂上 3 tick 的 `league_belveth_low`（先摘再挂，只留一个），回血后 3 tick 自己消失；同时记下她身上每一层 `league_belveth_l<n>`，少了就补回（科加斯附加包的做法：层数只会变多，所以少了只会是死亡清掉的）；
- 普攻和大招的说明换成附加包自己的文字（`description.league_belveth.attack` / `.ult`，写着「死亡后保留」和生命低于多少才转风暴），游戏里看说明就知道副本有没有生效。

计时和记下的层都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_belveth`：单元测试（参数、残血的界线、层的名字、死后补回）。
- 主包的卑尔维斯改了以后重新跑 `python addons/league_belveth/make_override.py`（它先核对主包的 `league_belveth.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_belveth.log`：`SPAWN`、生命掉到界线以下 `LOW`、回到界线以上 `UP`、叠层 `STACK`、死亡 / 复活 `DEAD` / `ALIVE`、补回 `KEEP`。

## W 尾击不再漏掉身前的人（0.1.1，2026-11-06）

游戏 0.7.1 的投射物判定（拿 11-05 阿克尚 R 的子弹对出来的，见 league_akshan 0.2.7）：投射物每 tick 跳 `speed` 那么远，只打圆心在它这一 tick 位置 `radius` 以内的单位——不扫两个 tick 中间，也不算单位的体型。`speed` 大于两倍 `radius` 时，站在两 tick 之间的人整个被跨过去；圆比英雄的体型（10000）小很多时，要几乎正中才打得到。

主包的 W `league_belveth_w_tail` 圆 7000、每 tick 飞 30000、长 55000：只在 0、30000、55000 三处判定，离她 7000～23000 和 37000～48000 的人都打不到（W 射程 45000 的大半段）。主包 `build_belveth` 改成圆 14000、每 tick 28000（英雄联盟约 200 宽的尾击加一个英雄的体型；还是两 tick 到头），副本重新生成。下一局看 W 有没有把身前的人击飞。

## 射程 buff 改成主包 league.dll 的 league:range（v0.1.2，2026-11-07）

带攻击距离的 buff 改成主包 league.dll 的 `league:range` 标记——buff 不再带 `range`（游戏的 AI 按它站位、却不按它出手，英雄停在够不着的地方），射程由官方的 `range_adjust` 加，AI 的出手判断也认；副本跟着主包 0.319.0 重新生成。
