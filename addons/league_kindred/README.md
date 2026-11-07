# 千珏附加包（测试版 v0.1.5，可选）

**不装这个附加包，主包里的千珏也是完整的**：羊灵射箭和千珏之印、Q 乱箭之舞、E 横生惧意 / W 狼灵狂热、R 羊灵生息（4 秒法阵里的
友方英雄不会阵亡，结束时回血）都在主包数据里。主包是纯数据，**读不到当前生命**，所以 R 只能按数据看得见的「危险」去猜什么时候放；
这个附加包用原生代码读生命，让 R 只在真要救人的时候放（用户：「千珏r大招逻辑不要乱放」「救队友可以放啊」）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 羊灵生息什么时候放 | AI 放出后待命 15 秒，她每射一箭查一次：被控制的友方英雄身边有敌方英雄，或交战中某个友方英雄被两名以上敌方英雄围住——常常大家血还多就交了 | 法阵范围内（她身边 42000）有友方英雄（**队友或她自己**）**快要阵亡**才放：身边有敌方英雄，而且生命低于 **30%**（她自己 **35%**），或 **1 秒内被打掉三成以上、只剩六成以下**，或照最近 1 秒的掉血速度法阵落下时就会低于那条线；几个人都危险时看最危险的那个。没人危险时 AI 想放 R，改成普攻，R 留着 |
| 别人的「不死」 | — | 身上已经有别人给的「不死」（基兰的符文、凯尔的大招等）的人不算危险 |

## 怎么做的

- `mod.override_info` 把主包的千珏换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_kindred.py` 的 `r_now=1`
  生成，主包的千珏改了就重跑）：**R 一放出就落法阵**（第 20 tick，半径 50000），不再待命、不退还冷却，普攻、Q、E 里不再检查危险；
  R 的说明开头加【附加包】。
- **挑时机**（AI 钩子 `league_kindred:ult`）：每次 AI 思考时记下己方英雄最近 1 秒的生命比例；R 冷却好、等级够、她没被控住时，
  看她身边 42000（法阵 50000 小一圈：落下前那 20 tick 人还会走）内的己方英雄（含她自己）：身边 45000 内有敌方英雄、身上没有别人的
  「不死」、而且生命低于 30% 或 1 秒内掉了 30% 以上且只剩 60% 以下——**AI 没想放也放**，施放目标是她 70000 内最近的敌方英雄
  （主包 R 的施放条件）。其余时候 AI 想放 R（主包的 R 不指定目标）：改成普攻她射程（55000）内最近的敌方英雄，
  打不到就朝 70000 内最近的敌方英雄走——不会原地停一下。她正忙时引擎要几 tick 才接放 R 的命令，钩子每 tick 再下一次；
  **R 的冷却真的开始走才算放出去一次**（日志只记一条）。
- 法阵、不死、结束时的回血、画面和声音全是主包的数据；原生代码只挑时机。
- **附加包版本的数值**：大招按真实血量放、救人更准，模拟里她强到 +2.09 / +1.96（同组打野约 +1.3）。用户选「保留 4 秒法阵」，副本里改成：大招冷却 120 秒（英雄联盟原版）、结束回血 40 + 10% 攻击力、攻击力 90 → 88，模拟 +1.29 / +1.16（`make_override.py` 的 `NUMBERS`；不装附加包的主包不变，+1.18 / +1.18）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.109.0 以上）要装着并启用。
2. 把整个 `league_kindred` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_kindred.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看千珏 R 的说明：开头是「【附加包】」、写着「快要阵亡时」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kindred.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `R ORDER for 某人#id (hp 22%)`：钩子下令放 R（她正忙时会连着下几次，这一行限量记）；
   - `R CAST for 某人#id (hp 22%, lost 35% in 60 ticks; R target #…, … from him; ordered … ticks before)`：R 真的放出去了，为谁、他当时多危险；
   - `R CAST by the AI itself`：AI 自己放了 R（钩子没拦住，不应该出现）；
   - `R RESULT for 某人#id (hp …% at the cast): alive, hp …%, in the circle (undying)`：放出后 30 tick 他怎么样了；死了的（v0.1.3）写 `dead at t=…, n ticks after the cast (in the windup, before the circle's first undying / after the circle's first undying); last seen t=… (+n): hp …%, r_safe on / no r_safe, … from the circle's centre; killed by 英雄#id`（时刻和凶手来自击杀记录）；
   - `R HELD: nobody in her circle about to die, attacking instead`：AI 想放、没人危险，留着，改成普攻 / 走过去。

   每行开头是 `[presim m=… s=…] t=… #千珏的实体`（哪份模拟、哪场、哪局）。v0.1.1：`R ORDER` 也带上这个开头（以前只有 `t=… player …`，2026-11-03 夜里的日志）；玩法不变。

   v0.1.2（2026-11-05，11-04 夜里的日志）：227 个 `R RESULT` 有 50 个 dead，几乎全是她给自己放的——0–30% 时放，法阵落下要 20 tick，人死在引导里（31% 放、1 秒内掉了 41%）；而且她死了钩子就不跑，结果要等复活才记（晚 1400–2400 tick，看着像法阵没救到）。现在：她自己的线提到 **35%**，另外谁按最近 1 秒的掉血速度在法阵给到不死（26 tick 后）时会掉到线下，也算快要阵亡（提前放）；`R RESULT` 记晚了的写 `settled n ticks late - she died about t=…, m ticks after the cast (in the windup / after the circle came down)`，她自己的结果标 `(herself)`。AI 想放 R、改成的普攻被游戏拒收时原来会放过 AI 的 R（`.prev` 里一次 `R CAST by the AI itself`），现在改成原地站一 tick。

   v0.1.3（2026-11-06，11-06 的日志）：88 个 `R RESULT` 里 14 个 dead（16%），12 个是她自己，多半死在放出后 6–25 tick；其中 4 次写着「after the circle came down」（22–25 tick），可那时法阵还没给过不死。查数据：法阵的区域 `first_delay` 是 0，引擎把 0 当成「过一整个 `r_per`（6 tick）才第一次给」——经典 SDK 的追踪：动作后 +22 法阵落下、+28 才第一次挂 `league_kindred_r_safe`，中间 6 tick 没有保护；改成 1 后 +23。所以 `tools/kit/build_kindred.py` 的法阵改成 `first_delay` 1（主包和副本一起，副本已重新生成），钩子的 `WINDUP`（放出到第一次不死）从 26 改成 22（`FIRST_SAFE` = `R_AT` + 2），`R RESULT` 的分界也改成第一次不死（`in the windup, before the circle's first undying` / `after the circle's first undying`）。死了的结果再记最后一次看到他的样子（生命、有没有法阵的不死、离法阵中心多远）和击杀记录里的凶手，下一局看死在第一次不死之后的那些是走出了法阵还是别的原因。

## 开发

- `python addons/league_kindred/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的千珏和参数表一致、
  `src/lib.rs` 里 R 的射程、半径、落下的 tick 和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_kindred`：单元测试（谁算快要阵亡、救谁、1 秒内掉了多少）。
- 在 `addons/` 下 `cargo build --release -p league_kindred`（Windows）得到 `target/release/league_kindred.dll`；`league_addons`
  合集也会编进本包。
- 工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\kn`）。

## 0.1.4：W 的家第一下不再晚 10 tick（2026-11-06）

W 的「家」（`w_home`，每 10 tick 给区里的她挂一次在家的标记 `w_in`）开头 10 tick 不算在家里；现在下一 tick 就算。（R 的光圈 `r_field` 在 0.1.3 已经这样改过。）经典 SDK 实测（2026-11-06，`trace.exe` 逐 tick 看每个区域第一次生效）：区域出现后第 `first_delay` tick 才第一次生效，写 0 等于晚整整一个周期（从飞行物落点生成的晚 `period` tick，从延迟或技能里直接生成的晚 `period - 1` tick）。改成 1 后，从落点生成的落地下一 tick 就生效，从延迟里生成的出现当 tick 就生效。主包的数据跟着改，本包的副本用 `make_override.py` 重新生成；DLL 没变。

## 射程 buff 改成主包 league.dll 的 league:range（v0.1.5，2026-11-07）

带攻击距离的 buff 改成主包 league.dll 的 `league:range` 标记——buff 不再带 `range`（游戏的 AI 按它站位、却不按它出手，英雄停在够不着的地方），射程由官方的 `range_adjust` 加，AI 的出手判断也认；副本跟着主包 0.319.0 重新生成。
