# 加里奥附加包（测试版 v0.1.7）

0.1.6（2026-11-05）：待命式大招没用掉时的冷却退还从来没生效过：n tick 的待命标记只有 n - 1 tick 看得见（经典 SDK 探针 lr1105/fix_j：n - 1 之前 148/148 次看得见，第 n tick 0 次），退还在窗口最后一 tick 读它时已经没了，所以每次待命过期都要等完整冷却（塞恩追踪：过期到再待命 3558 tick，改读后 877）。现在在窗口结束前 3 tick 读（`tools/kit/build_galio.py`），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

主包 `league` 保持纯数据。用户选了「主包数据 + 附加包」。这个附加包用原生代码做主包数据做不到的三件事：

- **杜朗护盾的被动护盾按「多久没挨打」给**：主包里加里奥普攻时给护盾（每 12 秒最多一次），因为数据读不到「多久没受伤」。
  附加包的被动 `league_galio:colossus` 记下他最后一次受伤的 tick，**12 秒没受伤**就给 90 + 30% 法强的护盾（5 秒），护盾还在不重给。
  英雄联盟里这个护盾只挡魔法伤害；被动的受伤钩子不带伤害类型，所以这里**挡所有伤害**。
- **W 的嘲讽按身边英雄数**：英雄联盟里蓄力越久嘲讽越久（0.5–1.5 秒），人多时会蓄满。附加包的 `league_galio:taunt` 在 W 放开时
  数他身边（W 的半径以内）的敌方英雄：1 个 0.75 秒、2 个 1.17 秒（主包的数）、3 个及以上 1.5 秒。
  「以内」算两人的碰撞半径（和数据的 W 圆圈打中谁一样），被嘲讽的英雄自己一定算一个（0.1.5，2026-11-03 晚的日志：只量中心时
  一半的 `TAUNT` 写着「0 enemy champions near」，同一下打中两个英雄也是 0，没有一次到 1.5 秒）。
- **英雄登场选人**：主包读不到血量，只能挑「被控的」或「身边连续两次有敌人的」友军。附加包的 `league_galio:entrance` 在每次轮询时
  看所有友方英雄：离他够远、身边有敌方英雄、确实在苦战（被控 / 血量 80% 以下 / 身边两个以上敌人）的里面，**被控的优先，再挑血量比例最低的**，
  落点周围敌方英雄多的优先（每多一个当作血量少 10%）。选中谁，数据就给谁护盾、引导、飞过去。
- **引导只被硬控打断**（0.1.2）：主包每 15 tick 用 `AllyChampionInCC` 查他自己有没有被控，被控就打断引导。游戏 0.7.0 起玩家说加里奥
  不开大；游戏的控制列表里也有他自己正在播的施法动作，那个查法可能把引导动作本身当成被控、每次都打断。副本去掉数据的这个查法，
  改由附加包每 tick 看他有没有被硬控（击飞、眩晕、定身、嘲讽、恐惧、魅惑、强制位移），有才打断；自己被硬控时也不选人。

数字：被动的参数写在英雄数据的 `passive.params`（`{"ps": 90, "ps_ap": 30, "ps_t": 300, "w_r": 26000, "w_taunt": 70, "r_far": 60000, "r_sur": 25000, "r_r": 22000}`），
由 `make_override.py` 从 `tools/kit/build_galio.py` 的参数表 `P` 写入；`PS_IDLE`、`TAUNT_ONE`、`TAUNT_MANY`、`CALM_HP` 写在 `src/lib.rs`，单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.106 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_galio` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_galio.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看加里奥的技能说明：普攻、E、R 开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_galio.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `WARD #3: 132 shield after 731 ticks untouched`：被动护盾；
   - `SPAWN #3: the add-on's Galio (player 7, team 1)`：出生（参数只在整次启动的第一条里写；0.1.5 起 `SPAWN` 也按条数限：
     以前每次出生都写一整行参数，一次启动 761 行、占了日志的四分之三）；
   - `TAUNT #5 Jinx#12: 90 ticks (3 enemy champions near)`：嘲讽；
   - `ENTRANCE #2 -> Ashe#7: hp 34% in cc, 2 enemy champions near, 2 where he lands, 84000 away`：大招选人；
   - `CHANNEL #2: R channels (crowd control on him [11])`：开始引导（方括号里是他身上的控制种类）；
   - `BROKEN #1: hard crowd control [0] 40 ticks into the channel`：引导被硬控打断；
   - `LANDED #2: the channel ended after 120 ticks, moved 84000`：飞过去落地；`NO FLIGHT`：引导结束却没飞（要查）。

0.1.6（2026-11-05，11-04 的日志）：英雄登场没有最远距离——数据的 R 射程是整张地图（960000），41 次登场里 15 次飞过 363000，一次从 969931 外飞了 981256（`galio.log` `ENTRANCE #1 … 969931 away` → `LANDED … moved 981256`）。`choose` 现在只在 `R_MAX`（`src/lib.rs`：363000 = 英雄联盟的 5500 x 本包的尺度 66）以内挑人，再远的队友不飞；日志照旧 `ENTRANCE`，`… away` 不会再超过 363000。

0.1.7（2026-11-06，11-06 的日志，只加诊断）：`FLY #27` 飞向雷恩加尔后紧接着 `NO FLIGHT #1 ... moved 0`，`set_pos` 却没说被拒；`FLY #3`、`#7`、`#15` 后面既没有 `LANDED` 也没有 `NO FLIGHT`（多半他死了：死人的被动不跑，而数据的延时效果对死人照样跑，飞行照样发生）。现在：飞行的下一 tick 记 `AFTER FLY #n: 1 tick(s) after the flight he stands at (x, y), d from the spot (sx, sy); crowd control on him [...]`（他站在哪、离落点多远、身上的控制）；他死在引导里或刚飞完、被动还没跑就死了，记 `DIED IN CHANNEL: n ticks into R's channel[, m after the flight]` / `DIED AFTER FLY: ...`；死人的飞行在 `FLY` 行末写 `(he is dead)`。玩法没变；下一局看这几行再定要不要改。

0.1.7 还有（画面和预模拟分岔的排查）：11-06 的日志里每一局看的比赛，画面都在开局 1-5 分钟和服务器的预模拟分开（三局换了赢家），排查时查了各附加包里跨模拟共用的状态。选人、瞄准、飞过的三张表（`PICKS`、`AIM`、`FLEW`）超过 4096 行**整张清掉**——同时
在跑的别的模拟的行一起没了（引导到一半的那份丢了队友最后的位置）；现在他每次出生时只删他在这份模拟里的旧行，没有编号的施法者借
这份模拟里第一个挂着编号的单位的编号（打上记号）。

## 开发

- `python addons/league_galio/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的加里奥和参数表一致）。
  主包的加里奥改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_galio`：单元测试（嘲讽时长、嘲讽数人算两人半径、选人、参数、和参数表一致）。
- 在 `addons/` 下 `cargo build --release -p league_galio`（Windows）得到 `target/release/league_galio.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
