# 弗拉基米尔残血血池附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。数据读不到当前生命，主包里弗拉基米尔的 W「血红之池」是自动的：他身上一直跑着一个每 3 tick 看一次的轮询，
看到 `league_vladimir_w_go` 就化成血池（2 秒不可选取、脚下敌人减速吸血、20 秒冷却）；`w_go` 由普攻里的**危险信号**加上——
**两名以上**敌方英雄贴身，或**连续两次**检查都挨了打。用户选了「危险信号 + 现在就做扩展包」：这个附加包用原生代码读生命，做成 League 玩家的按法：

- **快没血才开**：普攻里那段危险信号去掉，改由被动 `league_vladimir_pool:guard`（挂在 `passive` 上，每 tick 运行，挨打时当场再看一次）决定：
  活着、没被控住（击飞、眩晕、禁锢、嘲讽、恐惧、魅惑、沉默时放不了 W）、**身边 60000 内有敌方英雄**、血池不在冷却也不在池里，
  而且**生命低于 35%**——加上 `w_go`，数据的轮询最多 3 tick 后化成血池（血池本身、它的伤害、减速、回血、画面和声音全在数据里，和主包一样）。
- 数字都写在英雄数据的 `passive.params` 里，由 `make_override.py` 从 `tools/kit/build_vladimir.py` 的参数表 `P` 写入（`n_hp`、`n_near`），
  本包不另记一份。

## 在游戏里测

1. 主包（League of Legends Heroes 0.80 以上）要装着并启用。
2. 把整个 `league_vladimir_pool` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_vladimir_pool.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看弗拉基米尔普攻（被动）的说明：开头是「【残血血池测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vladimir_pool.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `GO #3: hp 31%`：被动叫血池时的生命（应当都在 35% 以下）；
   - `POOL: hp 29%`：他真正化成血池的那一刻（GO 之后最多 3 tick）。

## 开发

- `python addons/league_vladimir_pool/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的弗拉基米尔和参数表一致）。
  主包的弗拉基米尔改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_vladimir_pool`：单元测试（什么时候开池、参数读取）。
- 在 `addons/` 下 `cargo build --release -p league_vladimir_pool`（Windows）得到 `target/release/league_vladimir_pool.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试；轮询开池的数据部分在模拟里用危险信号测过，开池时机要在游戏里看日志确认。
