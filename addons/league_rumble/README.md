# 兰博附加包（测试版 v0.1.0）

用户 2026-10-25：「红温整套切换」。主包 `league` 的兰博是纯数据，不装这个包也完整可玩；这个附加包用原生代码补数据做不到的
一件事（照英雄联盟：过热时整个机甲烧得通红）：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 过热的样子 | 只有过热时的普攻是红温（`CasterAnimation` 播 `oh_attack`），站着、跑着、挨打、阵亡还是平常的样子 | **整身红温**：过热期间（`league_rumble_oh`）站、跑、挨打、阵亡都换成 `oh_idle` / `oh_run` / `oh_hit` / `oh_dead`，普攻第一 tick 换成 `oh_attack` |

- **不换英雄**：没有 `mod.override_info`，主包的兰博原样用；本包只在显示上换动画名。
- **整身红温**：`src/view.rs`，照希瓦娜附加包的做法挂在显示处理表的槽上（game_places 找地址，和其他变身附加包一个接一个
  调用）；找不到就什么都不做，退回只有普攻是红温。阵亡时尸体按倒下前那一帧的样子画；复活是平常的样子。高清帧：league.dll
  把每个动画名对到 `hd_<名字>`，他的图里有 `hd_oh_idle` 等，红温一样是高清。
- **按键**：本包不按任何技能键。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rumble.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  槽换上没有（`whole-body red-hot on/off`）、每个兰博红温和凉下来时一行（`Rumble #n: RED-HOT / plain (playing ...)`）、
  每 10 秒的显示统计。

## 命令

- 在 `addons/` 下 `cargo test --release -p league_rumble`：单元测试（换哪个名字、尸体的样子、他的图里有每个红温动作、主包有过热 buff）。
- 在 `addons/` 下 `cargo build --release -p league_rumble`（Windows）得到 `league_rumble.dll`；`league_addons` 合集也会编进本包。
