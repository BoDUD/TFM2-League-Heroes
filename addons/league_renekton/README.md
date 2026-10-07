# 雷克顿低血怒气附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。数据读不到当前生命，所以主包雷克顿的被动「怒之领域」只做了怒气本身：普攻和技能命中积攒怒气
（雷克顿身上的一条阶梯，最多 5 层，8 秒没积攒就清空），满层时下一个技能被强化并耗尽怒气。英雄联盟里**生命低于一半时怒气获取
+50%**，这一条要读生命，放在这个附加包里：

- 原生被动 `league_renekton:anger` 每 tick 看一次雷克顿身上的怒气阶梯：这一刻往上走了几阶，就是积攒了几次；
- 生命低于 50% 时，这些积攒记进计数，**每满 2 次就再多走一阶**（两次变三次，就是 +50%）；已经满层时不再多给；
- 生命回到一半以上、怒气被技能耗尽或到时间清空时，计数从头数。
- 技能一字不改（`make_override.py` 生成副本时核对：副本和主包只差被动这一项）。数字（层数、计时、50%、每 2 次）从
  `tools/kit/build_renekton.py` 的参数表 `P`（`f_n`、`f_t`、`n_low`、`n_every`）写进副本的 `passive.params`。

## 在游戏里测

1. 主包（League of Legends Heroes 0.73 以上）要装着并启用。
2. 把整个 `league_renekton` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_renekton.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 选人界面雷克顿普攻的说明开头是「【低血怒气测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_renekton.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN: the add-on's Renekton (player 0, team 0), Params { … }`：这局的雷克顿是附加包的副本；
   - `ANGER #3: hp 41%, Fury 2 -> 3`：低血时多给的一阶（前 8 次和之后每 50 次记一行）；
   - `WATCH: Fury 4, hp 63%, gains 120 extra 9`：每 30 秒一行，到现在积攒了几次、低血多给了几次。

## 开发

- `python addons/league_renekton/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的雷克顿和参数表一致）。
  主包的雷克顿改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_renekton`：单元测试（参数、低血时每 2 次多一阶、耗尽 / 清空 / 回血后重数、不超过满层、
  buff 名字）。
- 在 `addons/` 下 `cargo build --release -p league_renekton`（Windows）得到 `target/release/league_renekton.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，还没在游戏里看过日志。
