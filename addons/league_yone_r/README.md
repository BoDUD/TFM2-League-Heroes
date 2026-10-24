# 永恩 R 附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里永恩的 R「封尘绝念斩」停在直线上最后一个被命中的英雄身后，被命中的人都被拉向他落脚的地方。主包是纯数据：斩出直线后 `RushMoveToBack` 冲到**选中的目标**身后，不拉人。**不装这个附加包，主包的永恩也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 落在哪里 | 选中的目标身后 | 直线上离他最远的那个被斩中的英雄身后 6000（一个都没斩中就照主包，落在 90000 内最近的敌方英雄身后） |
| 拉人 | 没有 | 落地后把斩中的英雄拉向他（每 tick 2000，每个最多 16000，停在他身前 6000） |
| 伤害、击飞、画面、Q3 连 R | 主包 | 一样 |

## 怎么做的

- `mod.override_info` 把永恩换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：R 的两处 `RushMoveToBack`（蓄力的和 Q3 后直接斩的）换成给他挂 3 tick 的 `league_yone_r_go`；只打英雄的那条直线（`league_yone_r_mark`）给每个斩中的英雄多挂 3 tick 的 `league_yone_r_struck`；R 的说明开头加【附加包】。
- 被动 `league_yone_r:dash` 看到旗子，等斩中的标记出来（最多 4 tick），挑离他最远的那个，每 tick 12000（主包的冲刺速度）用 `entity_set_pos` 冲过去（撞墙就停在那里），落地后 `entity_pull` 拉人（免疫控制的人拉不动）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_yone_r` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 永恩 R 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yone_r.log`：`R #n: 2 struck, lands behind #7 76000 away`、`R #n LANDED after 7 steps, pulled 1 of 2`。

## 开发

- `python addons/league_yone_r/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里永恩改了就重跑。
- `cargo test -p league_yone_r`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
