# 波比附加包（测试版 v0.1.4）

用户：「波比放辅助，技能按方案 A 做（带扩展包 league_poppy）」。主包 `league` 的波比是纯数据，不装这个包也完整可玩；这个附加包用
原生代码补数据做不到的五件事（都照英雄联盟）：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 坚定风采的光环 | 光环里的敌方英雄放不出**新的**位移技能（数据只能禁位移） | 光环里**正在突进**的敌方英雄被挡下：击飞 0.5 秒、受魔法伤害，然后缚地并减速 2 秒（每次光环每人一次） |
| 坚定风采的双抗 | 一直 +16% | 生命低于 40% 时翻倍 |
| 英勇冲锋 | 每次推完都晕一下（数据看不到墙） | **撞到墙上**（地图的墙格、5v5 地图的四边）才再受一次伤害并眩晕；没墙就只推开 |
| 持卫的裁决（蓄满） | 从她身边击退 | 5v5 地图上**朝他自己的水晶方向**打飞很远（撞墙会停）；别的地图照主包 |
| 钢铁大使的护盾 | 固定值 + 攻击力加成 | **最大生命的 11%（1 级）到 21%（18 级）** |

- **怎么换上**：`mod.override_info` 把主包的波比换成 `override/league_poppy.data_champion`（`make_override.py` 用
  `tools/kit/build_poppy.py` 的 `native=1` 生成：技能、时机一字不改；坚定风采去掉主包的禁位移脉冲；英勇冲锋的击退换成原生效果
  `league_poppy:charge`，持卫的裁决的击退换成 `league_poppy:verdict`，捡起圆盾的护盾换成 `league_poppy:pick`；被动换成本包的
  `league_poppy:steadfast`）。
- **怎么认出突进**：她身上有坚定风采的光环（主包的 `league_poppy_w_on`）时，被动每 tick 看光环里的敌方英雄：一 tick 里移动了
  2200 以上（走路约 1000，加速后约 1500）、不到 20000（闪现、传送那么远的英雄联盟也不挡）就算突进。被她自己的 E、R 推着飞的不算。
- **墙**：卡蜜尔附加包的内置墙格（杰斯、巴德附加包也用它），5v5 地图另加四边的石墙、石堆。推的方向上墙在推的距离内就推到墙边，
  到的那一刻（她被动看目标身上的 `league_poppy_e_due` 到期）补伤害和眩晕。
- **按键**：本包不按任何技能键，碰不到「低等级按技能让游戏 AI 卡死」的问题。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_poppy.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  `BLOCK`（挡下突进）、`CHARGE`（撞墙 / 没墙）、`WALL`（撞墙眩晕）、`VERDICT`（往哪打飞）、`PICK`（护盾）。

## 命令

- `python addons/league_poppy/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的波比和参数表一致、
  `src/lib.rs` 的常量和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_poppy`：单元测试（突进的判定、护盾、墙、水晶、副本）。
- 在 `addons/` 下 `cargo build --release -p league_poppy`（Windows）得到 `league_poppy.dll`；`league_addons` 合集也会编进本包。

## 0.1.3：盾牌拾取和 Q 的减速场不再晚（2026-11-06）

被动盾牌的拾取区（`p_ground`，每 3 tick）开头 3 tick 捡不到；Q 的减速场（`q_field`，每 10 tick）第一下晚 10 tick。现在都是落地下一 tick 就生效。经典 SDK 实测（2026-11-06，`trace.exe` 逐 tick 看每个区域第一次生效）：区域出现后第 `first_delay` tick 才第一次生效，写 0 等于晚整整一个周期（从飞行物落点生成的晚 `period` tick，从延迟或技能里直接生成的晚 `period - 1` tick）。改成 1 后，从落点生成的落地下一 tick 就生效，从延迟里生成的出现当 tick 就生效。主包的数据跟着改，本包的副本用 `make_override.py` 重新生成；DLL 没变。

## 射程 buff 改成主包 league.dll 的 league:range（v0.1.4，2026-11-07）

带攻击距离的 buff 改成主包 league.dll 的 `league:range` 标记——buff 不再带 `range`（游戏的 AI 按它站位、却不按它出手，英雄停在够不着的地方），射程由官方的 `range_adjust` 加，AI 的出手判断也认；副本跟着主包 0.319.0 重新生成。

## 撞墙要到墙边、裁决先击飞再推、光环不拦别人的推（2026-11-13）

用户：「沙皇的反推 好像推不到人 整体检查一下各个推的逻辑」「接着修」。当天下午照「引擎按目标的韧性缩短每种控制，强制位移也一样」把本包的推按韧性放长过（#763），晚上撤了：阿兹尔 70 次带人的日志（`LANDED`）说明引擎不按韧性缩短强制位移，没被打断的带人实际走的路 / 计划的路正好是 1 / (1 - 韧性)，放长多少就多推多少（见 [`push_rules`](../push_rules/src/lib.rs)）。下面是留下来的、和韧性无关的几条。

- **E 撞墙到点先看她推的人到没到**：还在位移就等一拍；停下了却不贴着墙就不砸、不晕（日志 `SHORT`）。
- **5v5 的裁决先击飞再推**：给正在位移的单位上击飞会把位移停掉（`champion-data.md`）。原来先推后击飞；数据版本来就是先击飞
  （「an Airborne beside the Knockback still lets it carry them - measured」）。这条原生的路在游戏里还没看到过日志。
- **坚定风采不拦别人的推**：原来只放过她自己推的（`league_poppy_push`），队友的击退穿过光环被当成突进击飞，击飞又把那一下推
  打断。现在「在强制位移却不在放技能」的（数据的击退、拉人、别的附加包的推）都放过（`external_push`）；自己的突进带着施法
  动作，照拦。
- 版本号没改（还没合并的 #734 改它）。测试：`the_slam_needs_the_wall_and_pushes_are_no_dashes`。
