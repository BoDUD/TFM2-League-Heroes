# 兰博附加包（测试版 v0.2.0）

用户 2026-10-25：「红温整套切换」。主包 `league` 的兰博是纯数据，不装这个包也完整可玩；这个附加包用原生代码补数据做不到的
两件事（照英雄联盟：过热时整个机甲烧得通红；喷火时还能走）：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 过热的样子 | 只有过热时的普攻是红温（`CasterAnimation` 播 `oh_attack`），站着、跑着、挨打、阵亡还是平常的样子 | **整身红温**：过热期间（`league_rumble_oh`）站、跑、挨打、阵亡都换成 `oh_idle` / `oh_run` / `oh_hit` / `oh_dead`，普攻第一 tick 换成 `oh_attack` |
| 纵火盛宴 | 站着喷 1.5 秒（火画在他的出手帧里，跑步帧上没有火） | **边走边喷**：只站着端平炮口（8 tick），之后照常每 0.25 秒喷一下、能走；喷火时站着、跑着都是炮口喷着火的样子（`q_stand` / `q_run`）。锥形还是从他当时的位置朝 Q 的目标展开。伤害是主包的 60%（每下 18 + 16% 法强，主包 30 + 27%）：能边追边喷，6 下几乎都打满 |

- **换英雄**（0.2.0 起，用户 2026-10-29：「兰博不会边走边放火吗」→「就这么做」）：`mod.override_info` 把主包的兰博换成
  `override/league_rumble.data_champion`（`make_override.py` 用 `tools/kit/build_rumble.py` 的 `native=1` 生成，主包的兰博改了
  就重跑）：纵火盛宴只播 8 tick 的 `skill`（端平炮口），再给他挂 `league_rumble_q_on`（1.5 秒），喷火的 6 下照旧，伤害打六折（`WALK_K`：上路模拟主包 +0.51 / +0.10，边走边喷不打折 +2.23 / +1.98，七折 +1.24 / +1.29，六折 +0.36 / +0.24）；Q 的说明开头
  加【扩展包】并写上能走，游戏里看说明就知道换上了没有。别的技能一字不改。
- **边走边喷的样子**：`src/view.rs` 在他挂着 `league_rumble_q_on` 时把 idle / run 换成 `q_stand` / `q_run`。这两套帧在
  `tools/art/rig_rumble.py`：每一步都是喷火姿势的上半身（身子、平端的炮、铁球）接那一步跑步帧的腿，按跑步时机身的起伏整体
  抬高，火焰跟着炮口走；没有重画。同时过热时先是喷火的样子（红温那套没有火），喷完再红温。主包里他照旧站着喷。
- **整身红温**：`src/view.rs`，照希瓦娜附加包的做法挂在显示处理表的槽上（game_places 找地址，和其他变身附加包一个接一个
  调用）；找不到就什么都不做，退回只有普攻是红温。阵亡时尸体按倒下前那一帧的样子画；复活是平常的样子。高清帧：league.dll
  把每个动画名对到 `hd_<名字>`，他的图里有 `hd_oh_idle` 等，红温一样是高清。
- **按键**：本包不按任何技能键。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rumble.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  槽换上没有（`whole-body red-hot on/off`）、每个兰博红温、喷火和恢复平常时一行（`Rumble #n: FLAMING / RED-HOT / plain (playing ...)`）、
  每 10 秒的显示统计。

## 命令

- `python addons/league_rumble/make_override.py`：从参数表重新生成 `override/` 和 `text/`（`--check` 只核对）。
- 在 `addons/` 下 `cargo test --release -p league_rumble`：单元测试（换哪个名字、尸体的样子、他的图里有每个换上的动作、主包有过热 buff、副本的 Q 只站 8 tick 并挂上喷火标记）。
- 在 `addons/` 下 `cargo build --release -p league_rumble`（Windows）得到 `league_rumble.dll`；`league_addons` 合集也会编进本包。
