# 莉莉娅梦尘与昏睡附加包（测试版 v0.1.3）

0.1.6（2026-11-05）：待命式大招没用掉时的冷却退还不稳：原来在窗口结束前 1 tick 读待命标记（n tick 的标记只有 n - 1 tick 看得见），经典 SDK 追踪里悟空 53 次过期有 7 次读到时标记已经没了、白等完整冷却；塞恩、艾尼维亚等在前 3 tick 读的 177/177 都退了。现在统一在窗口结束前 3 tick 读（`tools/kit/build_lillia.py`），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

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
   - `WATCH: dust ticks 120, lullabies 3, sleeps 6, wakes 4, slept through her dust 5`：累计（最后一项是 `SLEEPS ON` 的次数），
     每 30 秒看一次，和她上一行 WATCH 比有变化才写。
   - 0.1.5（2026-11-03 的日志：1745 行里 1174 行是 WATCH，595 行全是 0）：WATCH 以前每 30 秒都写一行，现在计数没变就不写。

## 开发

- `python addons/league_lillia/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的莉莉娅和参数表一致）。
  主包的莉莉娅改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_lillia`：单元测试（参数、梦尘伤害、只有梦尘以外的伤害才叫醒、梦尘下一 tick
  才落下、WATCH 只在计数变了时写、buff 名字）。
- 在 `addons/` 下 `cargo build --release -p league_lillia`（Windows）得到 `target/release/league_lillia.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，只能看游戏日志（v0.1.1、v0.1.2 都是照游戏日志改的）。
- v0.1.1：游戏日志 `WAKE #1: #25 hit for 6 while asleep (100 ticks left)`——刚睡着 20 tick，三个人同时被主包数据里梦尘那一跳（4 + 3% 法强的魔法伤害，6 点）叫醒。每 tick 少掉的生命在这一跳以内不算被打（参数 `d_dmg`、`d_ratio` 从参数表写进副本）。
- v0.1.2：游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列（2026-10-17 反汇编；米利欧附加包 0.1.2 的日志也对得上），
  0.1.1 在打梦尘的同一 tick 前后读生命，记下的「梦尘自己打了多少」永远是 0。10-17 的游戏日志（0.1.1）：491 行 WAKE 里 202 行
  `hit for` ≤ 30，其中 192 行在睡着后 45 tick（一跳梦尘）以内；115 行正好在睡着后第 2 tick——R 和第一次挂上梦尘是同一下命中时，
  梦尘在第 +1、+46、+91 tick 跳，昏睡从 +90 开始，+91 那一跳排进队列、+92 之前落下，就把人叫醒了。现在被动记下每次打出去的
  （目标，减免前的伤害），下一次 on_update 看掉血时先扣掉 1.5 倍（`own_dust`），主包数据那一跳的余量照旧；日志多了
  `SLEEPS ON` 一行和 WATCH 的最后一项，第一行的版本号是附加包自己的（`VERSION`）。

## 游戏 0.7.0（0.1.3）

醒的时候只解除她自己的昏睡：稳定接口只能一次清掉全部控制（`entity_clear_cc`），以前叫醒会把和那一下一起落下的队友眩晕、击飞也一并清掉；现在清掉后把别的控制按剩余时长原样加回（`kept_after_wake`）。官方睡眠「受到任何伤害就醒」，她自己的梦尘每跳都会叫醒，所以不改用官方睡眠。

## E 的种子往前滚（2026-11-14）

英雄联盟的流涡种（wiki："Lillia lobs a seed at the target location that rolls forward indefinitely"，碰到敌人或地形才炸）：落点没有敌人就一直往前滚（用户看了「和英雄联盟不一样的地方」清单后说「全改吧」）。主包做不到（数据的弹道都从她身上发出），本包做：

- 副本（`tools/kit/build_lillia.py` 的 `native`）在种子落地 1 tick 后看她身上的 `league_lillia_e_hit`（落点打中人时挂的），没有就调 `league_lillia:e_roll`，输入是落点。
- `e_roll`（`src/roll.rs`）：方向从她现在站的地方到落点（英雄联盟按出手结束时她站的地方定；种子飞的那 20 tick 里她在放 E、接 W 的动作，没动）。沿这个方向每 1000 看一次地图的墙（游戏自己的 5v5 / 单线 / 死斗图：league_camille_wall 的墙格，5v5 再加四边画出来的墙面），停在墙前 4000，最远 `e_roll_len`（700000，滚满约 5 秒，碰不到下一次 E）。本包发一颗直线投射物：每 tick `e_roll_speed`（2330 = 英雄联盟 1400 码/秒），碰人的半径 `e_roll_r`（13000：附加包发的投射物按对方的中心算，游戏 0.7.1 量过），碰到第一个敌方单位就停（防御塔、水晶不算）；到头后 1 tick 排 `e_wall`。
- 滚着碰到谁（`e_roll_hit`）就在他那里炸，和落点那一下一样：`e_r` 加身体以内的敌方单位吃 `e_dmg` + `e_ratio`% 法强的魔法伤害、减速 `e_slow`% `e_slow_t` tick、主包的梦尘（数据是一个 `AddCasted`：本包按同样的时间排 5 跳 `e_dust`，`d_dmg` + `d_ratio`% 法强，算持续伤害）；英雄另挂本包的梦尘 `league_lillia_dust`，她回复 `d_heal` + `d_heal_ratio`% 法强，身上的 `league_lillia_d_on` 续上（大招读它）。炸了她身上挂 `league_lillia_e_boom`，滚到头就不再炸；没碰到人，滚到头在那里炸一下（画面，旁边有人照样吃）。
- 画面：主包 `league_lillia_fx` 的 `e_roll`（往右滚，顺时针）/ `e_roll_l`（往左滚，逆时针：游戏把往左飞的图转半圈，转不改转向），`tools/art/fx_lillia_roll.py` 用她飞着的种子（`e_seed` 第 1 帧）的身子按 90° 一格转、两缕紫烟不动，和飞着的种子一样大；高清帧照这张表别的帧的做法（densify_fx 的 Scale2x）。这张表的别的帧一格没动。装的时候 league.dll 要重新编（`fx_ppu.rs` 把这张表的 .fanim 编进去，表的清单不用改）。
- 数字从参数表 `P`（`e_roll_speed`、`e_roll_r`、`e_roll_len`，和 E、梦尘原有的）写进副本的 `passive.params`；原生效果用被动读到的那一份（每个莉莉娅都一样）。
- 没做：滚着打中英雄不会让待命中的大招放出来（数据的那一步；下一次 Q / W 打中照常放）。她死了：落地时不滚；滚着的时候她死了，碰到人照样炸（不回血），滚到头不炸（死了的英雄身上加不了旗子，分不清打没打中）。冷却缩短四成以上、两颗种子同时在滚时，墙前那一下可能多炸或少炸一次。
- E 的说明开头是「【滚种测试版】」。日志：`ROLL`（从哪滚、方向、多远、为什么停、哪张图）、`ROLL HIT`、`ROLL WALL`、`ROLL none`（落在墙前，滚不动）、`ROLL refused`、`ROLL input`（数据给的不是落点：不滚；该没有），前 40 次和之后每 50 次记一行。
- 测试：`cargo test --release -p league_lillia`（墙格上滚到墙前、地图边、最远；认地图；梦尘那 5 跳；左右两张图；副本落地后才调、两张图在表上）和 `tests/wiring.rs`（走真实的导出入口，迷你模拟里：往右 / 往左滚、碰到敌人炸开的每一样、同一颗不炸两次、滚到头不再炸、梦尘的跳、她死了不滚、滚着她死了照炸不回血、落在墙前不滚）。
