# 提莫蘑菇附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里提莫的蘑菇埋好后几分钟都在，提莫死了也在，敌人踩上才炸。主包是纯数据：蘑菇是一个限时的范围投射物，最多潜伏 12 秒。**不装这个附加包，主包的提莫也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 蘑菇在地上多久 | 最多 12 秒 | 3 分钟（10800 tick），提莫阵亡也在；最多 9 个，再多收掉最早的 |
| 扔、布好、踩发距离 8000、毒云 30000 内中毒 4 秒共 100 + 48% 法强、减速 40% 2 秒、画面 | 主包 | 一样 |
| 往哪扔 | AI 往敌方英雄脚下扔 | 一样（没有改成往草丛扔） |

## 怎么做的

- `mod.override_info` 把提莫换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：R 的三个蘑菇分支（`league_teemo_r_throw`）只留扔出去和落地的画面，后面的踩发判定、毒云和 49 个蘑菇画面去掉，换成落地时（第 20 tick）调用原生效果 `league_teemo_shrooms:plant`（`input` 是落点）；毒云的数字对照 `src/lib.rs` 检查；R 的说明开头加【附加包】、「潜伏 12 秒」换掉。
- 被动 `league_teemo_shrooms:shrooms` 管所有埋着的蘑菇：落地 60 tick 后布好，每 15 tick 在原地播一次主包的蘑菇画面 `league_teemo_r_trap`；敌人（英雄、小兵、野怪）走到 8000 内就炸：播 `league_teemo_r_burst` 画面和声音，30000 内的敌人每 60 tick 受到 25 + 12% 法强的魔法伤害（4 跳），减速 40% 120 tick，播中毒画面。
- 落点由原生效果交给被动（按模拟记：同一时间可能跑着几份模拟，各记各的）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_teemo_shrooms` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 提莫 R 的说明开头是「【附加包】」、写着「潜伏 3 分钟」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_teemo_shrooms.log`：`PLANT #n at (x, y), 4 in the ground`、`BOOM #n at (x, y) 2400 ticks after planting: 2 enemies poisoned`。

## 开发

- `python addons/league_teemo_shrooms/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里提莫改了就重跑。
- `cargo test -p league_teemo_shrooms`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
