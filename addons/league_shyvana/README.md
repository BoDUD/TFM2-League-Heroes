# 希瓦娜附加包（测试版 v0.1.2）

用户 2026-10-24：「龙女变成龙不能保持住？」。主包 `league` 的希瓦娜是纯数据，不装这个包也完整可玩；这个附加包用原生代码补
数据做不到的两件事（照英雄联盟；龙鳞铁衣是 0.1.2 加的）：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 龙形的样子 | 只有出招的动作是龙（`CasterAnimation` 播 `d_*`），站着、跑着、挨打、阵亡还是人形 | **整身变龙**：龙形期间（`league_shyvana_dg`，和龙形刚结束、还没播变回动作时的 `league_shyvana_was_dg`）站、跑、挨打、阵亡都换成 `d_idle` / `d_run` / `d_hit` / `d_dead`，普攻第一 tick 换成 `d_attack` |
| 龙鳞铁衣 | 折进龙形：龙形期间护甲、魔抗 +30%（数据看不到击杀） | **按击杀叠层**：参与击杀英雄（击杀、助攻）、击杀史诗野怪各 3 层，击杀野怪营地 1 层，每层 +0.3 护甲和魔抗（取整），整局都在；龙形只加生命（+30%） |

- **换英雄**（0.1.2 起）：`mod.override_info` 把希瓦娜换成 `override/` 里的副本，`make_override.py` 从主包生成：龙形（大招挂的 `league_shyvana_dg`）去掉护甲、魔抗 +30%，只留生命；挂上被动 `league_shyvana:scalemail`（`passive.params`：`champion` 3、`epic` 3、`large` 1、`per10` 3）；大招的说明换成本包的 `description.league_shyvana_addon.ult`（开头【附加包】，龙鳞铁衣那句换掉）。**普攻一个字节都不动**（另一边正在量她的普攻；单元测试对照主包）。0.1.1 以前没有副本，主包的希瓦娜原样用。
- **龙鳞铁衣**：被动的 `on_kill` / `on_assist`（英雄）、`on_kill` / `on_unit_kill`（史诗野怪，同一只只算一次）、`on_unit_kill`（野怪营地）数层；这局地图上没有大型小兵（只有近战、远程兵），小兵不算。层数阵亡也不丢，护甲、魔抗挂在一个永久 buff `league_shyvana_scalemail` 上，层数变了、复活（新的实体）时重新挂。
- **整身变龙**：`src/view.rs`，照纳尔附加包的做法挂在显示处理表的槽上（game_places 找地址，和其他变身附加包一个接一个
  调用）；找不到就什么都不做，退回半变身。阵亡时 buff 清掉，尸体按倒下前那一帧的形态画；复活是人形。高清帧：league.dll 把每个
  动画名对到 `hd_<名字>`，她的图里有 `hd_d_idle` 等，龙形一样是高清。
- **按键**：本包不按任何技能键。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shyvana.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  槽换上没有（`whole-body dragon on/off`）、每个希瓦娜换形态时一行（`Shyvana #n: DRAGON / human (playing ...)`）、每 10 秒的
  显示统计；`SCALE #n: +3 (killed #7) -> 14 stacks, +4 armour and magic resist`、`SCALE KEEP #n: a new body, 14 stacks hung again (+4)`。

## 命令

- `python addons/league_shyvana/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较（CI 跑）。主包里希瓦娜改了就重跑。
- 在 `addons/` 下 `cargo test --release -p league_shyvana`：单元测试（换哪个名字、尸体的形态、她的图里有每个龙形动作、主包有这两个 buff、龙鳞铁衣的层数、副本的普攻和主包一样）。
- 在 `addons/` 下 `cargo build --release -p league_shyvana`（Windows）得到 `league_shyvana.dll`；`league_addons` 合集也会编进本包。

## 0.1.1：被击飞时不变回人形

用户 2026-10-27：「龙女变龙的时候 被击飞的时候会变回去」（落地后又变回龙：龙形没断，是画面）。被击飞时游戏播的动画名她图里没有、那一刻也可能读不到龙形 buff，画面就画回人形。现在一旦是龙就一直按龙画，直到游戏播出变回人形的动作（`revert`）或阵亡后复活；龙形时她图里没有的动画名画成挨打的龙（`d_hit`），日志记一行 `plays "<名字>" (not in her sheet) - drawn as d_hit`。

## 0.1.2：龙鳞铁衣按击杀叠层（2026-11-14）

用户看了「和英雄联盟不一样的地方」清单后说「全改吧」，又说「接着做」。英雄联盟的龙鳞铁衣：大型野怪、大型小兵 1 层，敌方英雄、史诗野怪 3 层（参与击杀就算），每层 +0.3 护甲和魔抗。主包看不到击杀，折进了龙形（龙形期间护甲、魔抗 +30%）。本包从这一版起换上自己的英雄副本（`mod.override_info`、`make_override.py`、`override/`、`text/`）：龙形只留生命，被动 `league_shyvana:scalemail` 按上面的规则数层（`on_kill` / `on_assist` / `on_unit_kill`；地图上没有大型小兵，小兵不算），护甲魔抗挂在永久 buff `league_shyvana_scalemail` 上；大招的说明换成本包的。普攻不动，单元测试逐字节对照主包。CI 跑 `make_override.py --check`。
