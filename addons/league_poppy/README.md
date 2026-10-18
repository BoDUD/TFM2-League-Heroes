# 波比附加包（测试版 v0.1.0）

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
