# 蛮王残血开大附加包（测试版 v0.2.3）

0.2.2（2026-11-05）：待命式大招没用掉时的冷却退还不稳：原来在窗口结束前 1 tick 读待命标记（n tick 的标记只有 n - 1 tick 看得见），经典 SDK 追踪里悟空 53 次过期有 7 次读到时标记已经没了、白等完整冷却；塞恩、艾尼维亚等在前 3 tick 读的 177/177 都退了。现在统一在窗口结束前 3 tick 读（`tools/kit/build_tryndamere.py`，主包和副本的 JSON 由 `tools/fix/arm_refund_read.py` 改（蛮王的烘焙表在 assets/ 里，这里重建不了）），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

主包 `league` 保持纯数据。数据读不到当前生命，主包里蛮王的 R 由 AI 在敌方英雄 60000 内时放出、**待命** 900 tick
（没用上就退还冷却）；待命期间他每次普攻查一次：被**两名以上**敌方英雄贴身、或**连续 5 次**检查都挨了打，才爆发「无尽怒火」。
SDK 模拟里这样开大时他的生命中位数是 75%，一半的阵亡发生在大招待命却没认出危险的时候。用户：「大招快没血的时候设置开也行」——
这个附加包用原生代码读生命，做成 League 玩家的按法：

- **快没血才开**：普攻里那段检查去掉，改由被动 `league_tryndamere_rage:guard`（挂在 `passive` 上，每 tick 运行，挨打时当场再看一次）决定：
  R 待命、没被控住、**身边 50000 内有敌方英雄**，而且**生命低于 15%**，或 **1 秒（60 tick）内被打掉 35% 以上、只剩 40% 以下**——
  爆发：怒气加满，5 秒内生命不会降到 1 以下，播主包 R 的动作、画面和声音；第 290 tick 喝嗜血杀戮，按怒气回血。
- **残血才按 R**（v0.2.0，用户：「再检查一下蛮王总是满血开大的问题」）：主包的 R 一看到敌方英雄就放出、待命 15 秒，
  游戏里每次放出都显示成「开大」，满血时一次次放（没用上退还冷却，过一会儿又放）。本包的 AI 钩子 `league_tryndamere_rage:ult`
  拦下 AI 的 R，改成普攻（打不到就走过去）；到了上面的残血条件、R 冷却好、身边有敌方英雄时由它按下 R，下一 tick 被动就爆发——
  显示的「开大」就是爆发那一刻。
- **大招没好时喝 Q**：R 在冷却（或 5 级以前）、身上有怒气、身边有敌方英雄、生命低于 30% 时喝嗜血杀戮（12 秒一次）；
  R 冷却好时留给 R，不喝。
  主包只在 R 结束时喝（数据版按「危险」喝会在满血时喝掉）。
- 数字都写在英雄数据的 `passive.params` 里，由 `make_override.py` 从 `tools/kit/build_tryndamere.py` 的参数表 `P` 写入（`n_*` 是本包的阈值），
  本包不另记一份。

## 在游戏里测

1. 主包（League of Legends Heroes 0.62 以上）要装着并启用。
2. 把整个 `league_tryndamere_rage` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_tryndamere_rage.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看蛮王 R 的说明：开头是「【残血开大测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_tryndamere_rage.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `ARMED: hp 12% (...)`：R 进入待命（游戏里显示为「开大」的那一刻）和当时的生命——应当都在残血；
   - `R CAST: hp 12% (top 40% in 60 ticks)`：AI 钩子按下 R；`R HELD: hp 100%, not about to die`：AI 想放 R 被拦下（两条都 2 秒最多记一次）；
   - `RAGE: hp 12% (top 40% in 60 ticks)`：开大，当时的生命和 1 秒内最高的生命；
   - `DRINK (hp 27% ...): 3 fury, healed 340 -> …`：喝 Q，几层怒气、回了多少；
   - `DRINK (R ends)`：R 结束时的 Q。

## 开发

- `python addons/league_tryndamere_rage/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的蛮王和参数表一致）。
  主包的蛮王改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_tryndamere_rage`：单元测试（什么时候开 R、喝 Q，参数读取，怒气层数）。
- 在 `addons/` 下 `cargo build --release -p league_tryndamere_rage`（Windows）得到 `target/release/league_tryndamere_rage.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，开大时机要在游戏里看日志确认。

## 0.2.3：「R 好了」的记录每份模拟各删各的（2026-11-06）

玩法不变。11-06 的日志里每一局看的比赛，画面都在开局 1-5 分钟和服务器的预模拟分开（三局换了赢家），排查时查了各附加包里跨模拟共用的状态。蛮王这里：AI 钩子告诉被动「R 好了」用的表按 (这份模拟的编号, 种子, 来历, 他) 记，表超过 4096 行**整张清掉**——
别的模拟里刚记下的「R 好了」没了，那一 tick 被动以为 R 没好，残血先喝了 Q，同一局的两份模拟喝的 tick 不一样。现在新的一行进来时
只删这份模拟里他前几条命的行；表满 4096 行时丢编号最小（最早开始、早已打完）的模拟的行，正在跑的这一份从不丢。测试
`a_new_row_makes_room_only_in_its_own_sim`。
