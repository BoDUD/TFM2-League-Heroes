# 斩杀附加包（测试版 v0.2.3，可选）：伊芙琳、阿卡丽、锐雯

0.2.2（2026-11-05）：待命式大招没用掉时的冷却退还从来没生效过：n tick 的待命标记只有 n - 1 tick 看得见（经典 SDK 探针 lr1105/fix_j：n - 1 之前 148/148 次看得见，第 n tick 0 次），退还在窗口最后一 tick 读它时已经没了，所以每次待命过期都要等完整冷却（塞恩追踪：过期到再待命 3558 tick，改读后 877）。现在在窗口结束前 3 tick 读（伊芙琳、锐雯：`tools/fix/arm_refund_read.py`），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里伊芙琳的 R「最终抚慰」对生命 30% 以下的目标伤害 ×2.4，阿卡丽的 R2「完美刺杀」按目标已损失生命多 0–200%。锐雯的 R 疾风斩按已损失生命多 0–200%，玩家留着收人头。主包是纯数据，读不到生命：伊芙琳、阿卡丽改成按她自己最近打中英雄的次数分档加伤，锐雯开启 5 秒后身边有人就放、伤害按 8% 最大生命算。**不装这个附加包，主包的三人也是完整的**。

| 英雄 | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 伊芙琳 R | 150 + 75% 法强，最近每打中英雄一次 +35%（最多 ×2.4） | 150 + 75% 法强，对生命不高于 30% 的目标 ×2.4 |
| 阿卡丽 R2 | 86 + 43% 法强，两段之间每命中英雄一次 +25%（最多 +200%） | 86 + 43% 法强，按目标已损失生命最多 +200%（损失 70% 时加满） |
| 锐雯 R 疾风斩 | 开启 5 秒后身边 60000 内有敌方英雄就放；100 + 100% 攻击力 + 8% 最大生命 | 60000 内有敌方英雄生命不高于 30%、这一斩砍得死人、或大招只剩 1.5 秒时才放；100 + 100% 攻击力，按目标已损失生命最多 +200% 物理伤害（损失 75% 时加满） |

## 怎么做的

- `mod.override_info` 把两人换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：R 的分档加伤链（伊芙琳 `league_evelynn_h4`..`h1`，阿卡丽 `league_akali_r_s8`..`s1`）换成只打基础那一下，再给被打中的目标挂一个 3 tick 的标记（`league_executes_ev_hit` / `league_executes_ak_hit`）；R 的说明开头加【附加包】。
- 锐雯的副本：主包每一处定时放疾风斩的检查（攻击里 1 处、大招里 40 处 `league_riven_r_wait`）多等一个 `league_riven_ws_go`，放出时去掉它；疾风斩去掉 8% 最大生命，打中的人挂 `league_executes_rv_hit`。被动 `league_executes:riven` 在疾风斩好了（`league_riven_r_slash_ready`）时看 60000 内的敌方英雄，按上表挂 4 tick 的 `ws_go`；看到标记就补物理伤害（`Ad`，吃护甲）。
- 被动 `league_executes:evelynn` / `:akali` 每 tick 找身上有标记的敌人，读他的生命，补魔法伤害（`deal_damage_typed`，`Ap`，吃魔抗），数字在英雄数据的 `passive.params`。
- 生命是在基础那一下打完之后读的（同一 tick 的伤害已经结算），所以伊芙琳的「30% 以下」比英雄联盟（打之前算）略宽一点。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_executes` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 三人 R 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_executes.log`：`EXECUTE #n on #7: hp 210/1200, hit 300, +420 magic`；`RIVEN SLASH GO`（放疾风斩的那一刻）、`RIVEN SLASH #n on #7: ... +240 physical`。
   v0.2.1：`ws_go` 每 tick 都重挂，可主包只在每 30 tick 的检查或普攻时读它，以前每挂一次记一行（2026-11-03 夜里的日志：4 次疾风斩 115 行 `GO`）；现在一串连着的只记一行 `RIVEN SLASH GO #n`，主包读走它时再记一行 `RIVEN SLASH GO #n used … ticks into the burst: Wind Slash fired`（或 `no champion in its reach`：读走了但 60000 内没有英雄可放）。没有 `used` 的那串就是没等到检查。玩法不变。

## 开发

- `python addons/league_executes/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。三人在主包里改了就重跑。
- `cargo test -p league_executes`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。

## 射程 buff 改成主包 league.dll 的 league:range（v0.2.3，2026-11-07）

带攻击距离的 buff 改成主包 league.dll 的 `league:range` 标记——buff 不再带 `range`（游戏的 AI 按它站位、却不按它出手，英雄停在够不着的地方），射程由官方的 `range_adjust` 加，AI 的出手判断也认；副本跟着主包 0.319.0 重新生成。
