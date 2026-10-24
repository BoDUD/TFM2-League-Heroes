# 克烈附加包（`league_kled`）

用户（2026-10-24）：克烈要做下马，「和英雄联盟不一样的地方都是做附加包」。

主包的克烈是纯数据：数据读不到别的单位离多远、没有「受到伤害时」，游戏按名字自动播的待机 / 跑 / 挨打也换不了，所以主包里有三处只能近似。这个附加包把它们做成英雄联盟的样子：

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 斯嘎尔的血 | 一层护盾当斯嘎尔的血，旁边的 `league_kled_sk` 跟着护盾走（WithShield）：大招的护盾也会让斯嘎尔"活着" | 本包**自己记斯嘎尔的血**：这条命第一次骑上 `sk_hp` + 攻击 `sk_ad`%，勇气满了重新骑上 `re_hp` + 攻击 `re_ad`%，骑着时受到的伤害从这里扣，扣完就让他下马 |
| 捕熊夹的绳子 | 夹住的英雄跑多远都会被拽回来 | 被夹住的英雄离克烈超过 `q_break`，**绳子断**，不拽 |
| 下马的样子 | 只有出招（普攻、手枪）是步行的克烈，站着、跑着、挨打还是骑着斯嘎尔 | **整身步行**：下马时站着、跑着、挨打和普攻第一帧都画步行的克烈 |

死亡本来就是步行的克烈倒下（英雄联盟骑着死也是 Rider_Death），两边一样。

## 怎么接上的

`mod.override_info` 把主包的克烈换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_kled.py` 的 `native=1` 生成）：

- 骑上和重新骑上时挂的 `league_kled_sk` 是**普通标记**（不是跟着护盾的）；斯嘎尔的护盾照样替他挡伤害；
- Q 夹住英雄时给克烈挂 `league_kled_q_hold`，拽人那一下只在它还在时才拽（主包也一样，它在主包里一直都在）；
- `passive` 是本包的 `league_kled:skaarl`，参数 `sk_hp sk_ad re_hp re_ad q_break` 来自主包参数表 P：看到新挂上的 `sk` 就记下斯嘎尔的血，骑着时受到的伤害从里面扣，扣完摘掉 `sk`（数据的控制器下一拍让他下马）；身上有 `q_hold` 时看被夹住（有 `league_kled_q_slow`）的敌方英雄离他多远，超过 `q_break` 就摘掉减速和 `q_hold`；
- `src/view.rs` 在画面上把下马时（有 `league_kled_ft`）正在播的 `idle` / `run` / `hit` / `attack` 换成 `f_idle` / `f_run` / `f_hit` / `f_attack`（league_gnar 整身变巨型的做法，同一个显示处理表的槽）；
- 普攻和飞索捕熊器的说明换成附加包自己的文字（`description.league_kled.attack` / `.skill`），游戏里看说明就知道副本有没有生效。

斯嘎尔的血、骑上的次数都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_kled`：单元测试（参数、斯嘎尔的血、绳子断的距离、下马的动作名）。
- 主包的克烈改了以后重新跑 `python addons/league_kled/make_override.py`（它先核对主包的 `league_kled.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致；`--check` 只核对不写）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kled.log`：`SPAWN`、骑上 `MOUNT`、斯嘎尔跑掉 `FLEE`、绳子断 `BREAK`，整身步行的显示 `ON FOOT` / `riding`。
