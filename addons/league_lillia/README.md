# 莉莉娅梦尘与昏睡附加包（测试版 v0.1.2）

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
  （梦尘自己那一下、主包数据里梦尘那一跳 `d_dmg` + `d_ratio`% 法强的魔法伤害除外）就**醒来**：眩晕解除，受到 80 + 40% 法强的魔法伤害（`league_lillia_wake` 的画面和声音）。
- **梦尘自己落下不算被打**（0.1.2，2026-10-17 反汇编游戏 0.6.4 查的）：`deal_damage_typed` 只把伤害排进效果队列，打出去以后
  马上读生命还是原来的，下一次 on_update 之前才扣血。0.1.1 在打出去的那一 tick 前后各读一次生命，把差值当成「梦尘自己打了多少」，
  结果永远是 0：下一 tick 梦尘落下，掉的血超过只给主包数据那一跳留的余量，睡着的人就被叫醒，还吃一下惊醒伤害。现在被动记下每次
  打给每个目标的梦尘（减免前），下一次看昏睡者掉血时先扣掉：按减免前的伤害再加一半扣，`damaged_amplify` 放大了也扣得住；
  主包数据那一跳的余量照旧。
- 数字从参数表 `P`（`d_period`、`d_hp`、`d_ap_bp`、`r_drowsy`、`r_slow`、`n_sleep`、`r_wake`、`r_wake_ratio`）写进副本的
  `passive.params`。

## 在游戏里测

1. 主包（League of Legends Heroes 0.75 以上）要装着并启用。
2. 把整个 `league_lillia` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_lillia.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 选人界面莉莉娅普攻的说明开头是「【梦尘测试版】」、大招是「【昏睡测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lillia.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - 第一行 `=== league_lillia v0.1.2 … loaded`：附加包自己的版本（0.1.1 编进合集时写的是合集的 v0.1.0）；
   - `SPAWN: the add-on's Lillia (player 1, team 0), Params { … }`：这局的莉莉娅是附加包的副本；
   - `LULLABY #2: 3 dusted champion(s) [..]`：大招让几个带梦尘的英雄困倦（前 8 次和之后每 20 次记一行）；
   - `WAKE #4: #23 hit for 160 while asleep (70 ticks left) -> 140 magic`：昏睡中被打醒、惊醒伤害。`hit for` 只有十几二十点、
     又在睡着后一跳梦尘（45 tick）以内、尤其是第 1、2 tick（`119`、`118 ticks left`）的，是梦尘自己被当成了被打（0.1.1 的毛病）；
   - `SLEEPS ON #3: #23 lost 21 while asleep, her own dust landing (up to 47) (88 ticks left)`：昏睡中掉的血是她自己的梦尘
     落下，没有叫醒（0.1.1 会在这里叫醒；前 8 次和之后每 20 次记一行）；
   - `WATCH: dust ticks 120, lullabies 3, sleeps 6, wakes 4, slept through her dust 5`：每 30 秒一行的累计（最后一项是
     `SLEEPS ON` 的次数）。

## 开发

- `python addons/league_lillia/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的莉莉娅和参数表一致）。
  主包的莉莉娅改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_lillia`：单元测试（参数、梦尘伤害、只有梦尘以外的伤害才叫醒、梦尘下一 tick
  才落下、buff 名字）。
- 在 `addons/` 下 `cargo build --release -p league_lillia`（Windows）得到 `target/release/league_lillia.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，只能看游戏日志（v0.1.1、v0.1.2 都是照游戏日志改的）。
- v0.1.1：游戏日志 `WAKE #1: #25 hit for 6 while asleep (100 ticks left)`——刚睡着 20 tick，三个人同时被主包数据里梦尘那一跳（4 + 3% 法强的魔法伤害，6 点）叫醒。每 tick 少掉的生命在这一跳以内不算被打（参数 `d_dmg`、`d_ratio` 从参数表写进副本）。
- v0.1.2：游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列（2026-10-17 反汇编；米利欧附加包 0.1.2 的日志也对得上），
  0.1.1 在打梦尘的同一 tick 前后读生命，记下的「梦尘自己打了多少」永远是 0。10-17 的游戏日志（0.1.1）：491 行 WAKE 里 202 行
  `hit for` ≤ 30，其中 192 行在睡着后 45 tick（一跳梦尘）以内；115 行正好在睡着后第 2 tick——R 和第一次挂上梦尘是同一下命中时，
  梦尘在第 +1、+46、+91 tick 跳，昏睡从 +90 开始，+91 那一跳排进队列、+92 之前落下，就把人叫醒了。现在被动记下每次打出去的
  （目标，减免前的伤害），下一次 on_update 看掉血时先扣掉 1.5 倍（`own_dust`），主包数据那一跳的余量照旧；日志多了
  `SLEEPS ON` 一行和 WATCH 的最后一项，第一行的版本号是附加包自己的（`VERSION`）。
