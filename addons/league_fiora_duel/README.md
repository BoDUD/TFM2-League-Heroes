# 剑姬破绽附加包（测试版 v0.2.0）

主包 `league` 保持纯数据。数据分不清一次攻击打中的是谁，所以主包里剑姬大招「无双挑战」的 4 处破绽记在剑姬自己身上：
大招期间她打中**任何一个**敌方英雄都会刺掉一处（模拟里 42 次有 16 次刺在别人身上）。主包只保证胜利之地落在被挑战的人脚下
（`tools/fix/fix_fiora_r_zone.py`）。这个附加包用原生代码做成英雄联盟的样子：

- 开大时给被挑战的英雄挂上 `league_fiora_r_mark`（8 秒）；
- 每次破绽判定（普攻、Q 的两下、W 的两道）先调用原生效果 `league_fiora_duel:vital`：剑姬在大招中、而且打中的人身上有标记，
  才给她加 3 tick 的 `league_fiora_r_tgt`，数据读到它就刺大招的破绽（伤害、回血、Q/W 冷却减半、计数）；
- 打别的英雄只出**普通的被动破绽**；
- 数据同一 tick 读一次 `r_tgt`，读不到在下一 tick 再读一次（原生加的 buff 什么时候能被数据读到，游戏里还没证实过）；
- v0.2.0 把她拉回被挑战的人（用户：「大招不打破绽 有bug」）：AI 选目标不认挑战，2026-10-11 游戏里一局大招期间打中英雄 21 次，
  12 次打在别人身上，破绽一直留着。现在大招期间打中别的英雄时，被挑战的人还活着、她看得见、在 80000 内，就给她挂 70 tick
  （约一下普攻）指向他的嘲讽，下一下普攻打他。嘲讽期间 AI 很少放技能（SDK：被嘲讽时约十下普攻一个技能，平时约十下六个），
  所以只在打错人之后挂，不一直锁着。

## 在游戏里测

1. 主包 0.71 以上要装着并启用；本包已经编进附加包合集 `league_addons`（单独用时把 `league_fiora_duel` 文件夹放进 `mods\`）。
2. 看剑姬大招的说明：开头是「【破绽测试版】」就说明换上了。
3. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_fiora_duel.log`（每次启动游戏重写）：
   - `R hit on #…: the challenged champion - a Vital`：打中被挑战的人，刺一处；
   - `R hit on #…: another champion - the passive only; taunted onto the challenged #… (距离) for 70 ticks`：打中别人，只出被动破绽，
     把她嘲讽回被挑战的人（下一行应该是打中他）；
   - `… the challenged #… is out of reach or sight`：他太远或看不见，不拉；`no challenged champion left`：他已经死了。

## 开发

- `python addons/league_fiora_duel/make_override.py`：从主包的剑姬生成 `override/` 和 `text/`（主包的剑姬改了要重跑）。
- 在 `addons/` 下 `cargo test --release -p league_fiora_duel`；`cargo build --release -p league_fiora_duel` 或 `-p league_addons`。
- 经典 SDK 的模拟器跑不了原生代码：数据这一半用「把 Native 换成立同样的标志」在模拟器里测过（被挑战的人 -> 大招破绽，别人 -> 被动破绽）。
