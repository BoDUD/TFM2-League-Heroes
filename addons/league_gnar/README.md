# 纳尔附加包（测试版 v0.1.0）

用户：附加包「要」；「还有r墙眩晕别人的机制也要做」。主包 `league` 的纳尔是纯数据，不装这个包也完整可玩；这个附加包用原生代码补
数据做不到的两件事（都照英雄联盟）：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 巨型纳尔的样子 | 只有出招的动作是巨型（`CasterAnimation`），站着、跑着、挨打、阵亡还是迷你 | **整身变巨型**：巨型期间（和巨型刚结束、还没播变回动作时）站、跑、挨打、阵亡都换成 `m_*` |
| 呐啊！ | 从他身边击退，人人眩晕（数据看不到墙） | 所有人往**同一个方向**掀飞（挑能把最多人砸上墙的方向，敌方英雄顶十个小兵；哪边都没墙就从他身边掀开）；**撞到墙上**的再受一半伤害并眩晕，没撞墙的不晕 |

- **怎么换上**：`mod.override_info` 把主包的纳尔换成 `override/league_gnar.data_champion`（`make_override.py` 用
  `tools/kit/build_gnar.py` 的 `native=1` 生成：技能、时机一字不改；呐啊！的击退和眩晕换成原生效果 `league_gnar:wall`，
  被动换成本包的 `league_gnar:slam`；大招说明开头加【附加包】）。
- **整身变巨型**：`src/view.rs`，照奈德丽附加包的做法挂在显示处理表的槽上（game_places 找地址，和其他变身附加包一个接一个
  调用）；找不到就什么都不做，退回半变身。
- **墙**：卡蜜尔附加包的内置墙格（波比、杰斯、巴德附加包也用它），5v5 地图另加四边。掀 30000 的路上碰到墙就推到墙边，到的那一刻
  （被动看目标身上的 `league_gnar_r_due` 到期）补伤害和眩晕。
- **按键**：本包不按任何技能键。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_gnar.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  `THROW`（往哪边掀、撞不撞墙）、`WALL`（撞墙眩晕），还有整身变巨型的显示统计。

## 命令

- `python addons/league_gnar/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的纳尔和参数表一致、
  `src/lib.rs` 的常量和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_gnar`：单元测试（挑方向、英雄权重、撞墙伤害、副本）。
- 在 `addons/` 下 `cargo build --release -p league_gnar`（Windows）得到 `league_gnar.dll`；`league_addons` 合集也会编进本包。
