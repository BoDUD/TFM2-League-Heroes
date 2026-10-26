# 希瓦娜附加包（测试版 v0.1.0）

用户 2026-10-24：「龙女变成龙不能保持住？」。主包 `league` 的希瓦娜是纯数据，不装这个包也完整可玩；这个附加包用原生代码补
数据做不到的一件事（照英雄联盟）：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 龙形的样子 | 只有出招的动作是龙（`CasterAnimation` 播 `d_*`），站着、跑着、挨打、阵亡还是人形 | **整身变龙**：龙形期间（`league_shyvana_dg`，和龙形刚结束、还没播变回动作时的 `league_shyvana_was_dg`）站、跑、挨打、阵亡都换成 `d_idle` / `d_run` / `d_hit` / `d_dead`，普攻第一 tick 换成 `d_attack` |

- **不换英雄**：没有 `mod.override_info`，主包的希瓦娜原样用；本包只在显示上换动画名。
- **整身变龙**：`src/view.rs`，照纳尔附加包的做法挂在显示处理表的槽上（game_places 找地址，和其他变身附加包一个接一个
  调用）；找不到就什么都不做，退回半变身。阵亡时 buff 清掉，尸体按倒下前那一帧的形态画；复活是人形。高清帧：league.dll 把每个
  动画名对到 `hd_<名字>`，她的图里有 `hd_d_idle` 等，龙形一样是高清。
- **按键**：本包不按任何技能键。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shyvana.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  槽换上没有（`whole-body dragon on/off`）、每个希瓦娜换形态时一行（`Shyvana #n: DRAGON / human (playing ...)`）、每 10 秒的
  显示统计。

## 命令

- 在 `addons/` 下 `cargo test --release -p league_shyvana`：单元测试（换哪个名字、尸体的形态、她的图里有每个龙形动作、主包有这两个 buff）。
- 在 `addons/` 下 `cargo build --release -p league_shyvana`（Windows）得到 `league_shyvana.dll`；`league_addons` 合集也会编进本包。

## 0.1.1：被击飞时不变回人形

用户 2026-10-27：「龙女变龙的时候 被击飞的时候会变回去」（落地后又变回龙：龙形没断，是画面）。被击飞时游戏播的动画名她图里没有、那一刻也可能读不到龙形 buff，画面就画回人形。现在一旦是龙就一直按龙画，直到游戏播出变回人形的动作（`revert`）或阵亡后复活；龙形时她图里没有的动画名画成挨打的龙（`d_hit`），日志记一行 `plays "<名字>" (not in her sheet) - drawn as d_hit`。
