# 艾翁附加包（`league_ivern`）

用户（2026-10-22）：「需要就做」「还有艾翁的W能触发雷恩加尔的跳 别忘了」「还有奇安娜也可以触发元素 艾翁的这个草 你们两可以联动一下」。

主包的艾翁是纯数据：揠苗助攻（W，并进被动）在每次种豆得瓜时长出草丛，数据读不到位置，只能在长草那一刻给身边的队友加攻击。这个附加包让草丛变成一块真正的草丛：

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 揠苗助攻 | 长草那一刻身边的队友攻击 +`w_atk`%，持续 `w_t` tick | 草丛记在他长草的地方（半径 `w_r`、`w_t` tick 后枯掉，他死了也还在）；**站在里面**的队友每 tick 续上攻击 +`w_atk`%；站在里面的每个英雄（两边都算）挂 2 tick 的 `league_ivern_in_brush` |
| 联动 | — | 雷恩加尔（`league_rengar_bush` 0.1.2 起）身上有这个标记就算站在草丛里，能扑；奇亚娜（`league_qiyana` 0.2.1 起）突进落地时身上有它就算身边有草，拿草元素 |

三个附加包谁装了都行：标记只是一个 buff，没装艾翁的附加包时雷恩加尔和奇亚娜照旧只看地图。合集 `league_addons` 里三个都在。

## 怎么接上的

`mod.override_info` 把主包的艾翁换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_ivern.py` 的 `native=1` 生成）：

- 长草时给他挂 2 tick 的 `league_ivern_w_new`，不再在数据里给队友加成（交给本包）；
- `passive` 是本包的 `league_ivern:brush`，参数 `{"w_atk": 15, "w_r": 26000, "w_t": 240}`；
- 普攻的说明换成附加包自己的文字（`description.league_ivern.attack`），游戏里看说明就知道副本有没有生效。

被动每 tick 看他身上有没有 `w_new`：有就去掉、在他脚下记一丛草。每个计时都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_ivern`：单元测试（参数、草丛半径、枯掉和最多 8 丛）。
- 主包的艾翁改了以后重新跑 `python addons/league_ivern/make_override.py`（它先核对主包的 `league_ivern.data_champion` 和参数表一致）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ivern.log`（`SPAWN`、每丛草 `BRUSH`），雷恩加尔从艾翁草丛扑出来时 `league_rengar_bush.log` 有 `INTO the bush` 和 `READY`，奇亚娜拿到草是 `league_qiyana.log` 的 `ELEMENT Grass by Terrain`。
