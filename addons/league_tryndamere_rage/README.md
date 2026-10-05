# 蛮王残血开大附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。数据读不到当前生命，主包里蛮王的 R 由 AI 在敌方英雄 60000 内时放出、**待命** 900 tick
（没用上就退还冷却）；待命期间他每次普攻查一次：被**两名以上**敌方英雄贴身、或**连续 5 次**检查都挨了打，才爆发「无尽怒火」。
SDK 模拟里这样开大时他的生命中位数是 75%，一半的阵亡发生在大招待命却没认出危险的时候。用户：「大招快没血的时候设置开也行」——
这个附加包用原生代码读生命，做成 League 玩家的按法：

- **快没血才开**：普攻里那段检查去掉，改由被动 `league_tryndamere_rage:guard`（挂在 `passive` 上，每 tick 运行，挨打时当场再看一次）决定：
  R 待命、没被控住、**身边 50000 内有敌方英雄**，而且**生命低于 15%**，或 **1 秒（60 tick）内被打掉 35% 以上、只剩 40% 以下**——
  爆发：怒气加满，5 秒内生命不会降到 1 以下，播主包 R 的动作、画面和声音；第 290 tick 喝嗜血杀戮，按怒气回血。
- **大招没好时喝 Q**：R 不在待命（冷却中、5 级以前）、身上有怒气、身边有敌方英雄、生命低于 30% 时喝嗜血杀戮（12 秒一次）。
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
