# 雷克顿低血怒气附加包（测试版 v0.1.0）

0.1.3（2026-11-05）：待命式大招没用掉时的冷却退还不稳：原来在窗口结束前 1 tick 读待命标记（n tick 的标记只有 n - 1 tick 看得见），经典 SDK 追踪里悟空 53 次过期有 7 次读到时标记已经没了、白等完整冷却；塞恩、艾尼维亚等在前 3 tick 读的 177/177 都退了。现在统一在窗口结束前 3 tick 读（`tools/kit/build_renekton.py`），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

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
   - `ANGER #3: hp 41%, Fury 2 -> 3`：低血时多给的一阶（屏幕上那局每次都记；服务器预模拟一次启动先记 40 次，之后每 100 次
     记一行）。以前每 30 秒一行的 `WATCH` 已删：它要看的问题 2026-10-30 的日志已经回答（见下）。

## 开发

- `python addons/league_renekton/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的雷克顿和参数表一致）。
  主包的雷克顿改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_renekton`：单元测试（参数、低血时每 2 次多一阶、耗尽 / 清空 / 回血后重数、不超过满层、
  buff 名字）。
- 在 `addons/` 下 `cargo build --release -p league_renekton`（Windows）得到 `target/release/league_renekton.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码。游戏里的日志 2026-10-31 看过（10-30 两次启动）：279 次 `ANGER` 都在生命 50% 以下（两行显示
  50% 是四舍五入），怒气只从 2→3、3→4、4→5 多给。

## 强化冷酷捕猎打碎护盾（v0.1.4，2026-11-14）

用户看了「和英雄联盟不一样的地方」清单后说「全改吧」。英雄联盟（V26.22）：强化的冷酷捕猎「completely destroying damage-mitigating shields on the target upon the first strike if they are not a monster」（法术护盾也挡不住这一下）。主包的数据去不掉别人身上的护盾，没有这一条。

- 副本（`build_renekton.py` 的 native=1）里强化 W 的第一刀，在伤害之前调本包的原生效果 `league_renekton:rend`：目标身上的护盾全部清掉（`entity_clear_shield`；野怪不算，英雄联盟一样）。普攻一字没改（他的普攻正在别处量）。
- E 的说明换成副本自己的 `skill2` 键：「强化三刀、1.5 秒，第一刀打碎护盾」。
- 日志 `REND #n: the empowered W's first strike broke 1 shield layer(s), 230 in all`。测试 `the_empowered_ws_first_strike_breaks_shields`。

经典引擎跑不了原生代码；下一局看 `REND` 行。怒气脱战 12 秒后才慢慢掉（英雄联盟）没做：怒气的计时在普攻的效果树里，普攻现在不能动。
