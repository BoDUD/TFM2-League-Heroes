# 莉莉娅梦尘与昏睡附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。数据里能读最大生命值的只有真实伤害，也没有「受到伤害就醒」的效果，所以主包莉莉娅：
被动「梦满枝」的梦尘对英雄每 0.75 秒造成 1% 最大生命值的**真实伤害**；大招「夜阑谣」让带梦尘的敌方英雄困倦 1.5 秒后
**眩晕** 1.5 秒（打不醒），她的 Q / W 打到眩晕中的英雄时多造成一段惊醒伤害。英雄联盟里梦尘是**魔法伤害**，昏睡 2 秒、
**受到任何伤害就醒**并吃惊醒伤害，这两条放在这个附加包里（用户：「这个需要做附加包的」）：

- 副本（`tools/kit/build_lillia.py` 的 `build(p, native=True)`）里，技能打中敌方英雄时给他挂 buff `league_lillia_dust`
  （3 秒，再中一下刷新），取代主包的真实伤害梦尘；数据里「Q / W 打到昏睡者加伤」那两段拿掉；加上本包的被动
  `league_lillia:dream`。其他技能一字不改。
- `league_lillia:dream` 每 tick 看一次：带梦尘的敌方英雄从挂上的下一 tick 起每 0.75 秒受到 1% + 每 100 法强 0.3% 最大生命值的
  **魔法伤害**（会被魔抗减免）；
- 莉莉娅身上出现大招的标记 `league_lillia_r_go`（主包的 R 照旧加它）时，所有带梦尘的敌方英雄**困倦**（减速 40%，1.5 秒，
  `league_lillia_drowsy` 的画面），之后**昏睡** 2 秒（原生眩晕 + `league_lillia_sleep` 的画面）；昏睡中生命 + 护盾少了
  （梦尘自己那一下除外）就**醒来**：眩晕解除，受到 80 + 40% 法强的魔法伤害（`league_lillia_wake` 的画面和声音）。
- 数字从参数表 `P`（`d_period`、`d_hp`、`d_ap_bp`、`r_drowsy`、`r_slow`、`n_sleep`、`r_wake`、`r_wake_ratio`）写进副本的
  `passive.params`。

## 在游戏里测

1. 主包（League of Legends Heroes 0.75 以上）要装着并启用。
2. 把整个 `league_lillia` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_lillia.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 选人界面莉莉娅普攻的说明开头是「【梦尘测试版】」、大招是「【昏睡测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lillia.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN: the add-on's Lillia (player 1, team 0), Params { … }`：这局的莉莉娅是附加包的副本；
   - `LULLABY #2: 3 dusted champion(s) [..]`：大招让几个带梦尘的英雄困倦（前 8 次和之后每 20 次记一行）；
   - `WAKE #4: #23 hit for 160 while asleep (70 ticks left) -> 140 magic`：昏睡中被打醒、惊醒伤害；
   - `WATCH: dust ticks 120, lullabies 3, sleeps 6, wakes 4`：每 30 秒一行的累计。

## 开发

- `python addons/league_lillia/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的莉莉娅和参数表一致）。
  主包的莉莉娅改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_lillia`：单元测试（参数、梦尘伤害、只有梦尘以外的伤害才叫醒、buff 名字）。
- 在 `addons/` 下 `cargo build --release -p league_lillia`（Windows）得到 `target/release/league_lillia.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，还没在游戏里看过日志。
