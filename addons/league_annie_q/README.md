# 安妮 Q 返还附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里安妮的 Q「碎裂之火」击杀目标时返还法力和一半冷却，玩家用它补兵。主包是纯数据：引擎没有「打死了就减冷却」的效果，Q 击杀不返还。**不装这个附加包，主包的安妮也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| Q 击杀 | 不返还 | 返还一半冷却（120 tick；小兵、野怪、英雄都算） |
| 法力 | 没有 | 没有 |

## 怎么做的

- `mod.override_info` 把安妮换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：Q 的两枚火球（带眩晕的和不带的，`league_annie_q`）打中时，在伤害之后多调用一次原生效果 `league_annie_q:refund`；Q 的说明开头加【附加包】、末尾加一句。
- 原生效果的 `input` 就是被打中的单位：他已经死了（不再活着或生命为 0），就 `entity_reduce_cooldown` 把 Q 的剩余冷却减 120 tick。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_annie_q` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 安妮 Q 的说明开头是「【附加包】」、末尾写着「击杀目标时返还一半冷却」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_annie_q.log`：`Q KILL #n on #31: cooldown 200 -> 80`。

## 开发

- `python addons/league_annie_q/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里安妮改了就重跑。
- `cargo test -p league_annie_q`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
