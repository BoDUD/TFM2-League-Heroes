# 千珏附加包（测试版 v0.2.0，可选）

**不装这个附加包，主包里的千珏也是完整的**：羊灵射箭和千珏之印、Q 乱箭之舞、E 横生惧意 / W 狼灵狂热、R 羊灵生息（4 秒法阵里的
友方英雄不会阵亡，结束时回血）都在主包数据里。主包是纯数据，**读不到当前生命**，所以 R 只能按数据看得见的「危险」去猜什么时候放；
这个附加包用原生代码读生命，让 R 只在真要救人的时候放（用户：「千珏r大招逻辑不要乱放」「救队友可以放啊」）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 羊灵生息什么时候放 | AI 放出后待命 15 秒，她每射一箭查一次：被控制的友方英雄身边有敌方英雄，或交战中某个友方英雄被两名以上敌方英雄围住——常常大家血还多就交了 | 法阵范围内（她身边 42000）有友方英雄（**队友或她自己**）**快要阵亡**才放：身边有敌方英雄，而且生命低于 **30%**（她自己 **35%**），或 **1 秒内被打掉三成以上、只剩六成以下**，或照最近 1 秒的掉血速度法阵落下时就会低于那条线；几个人都危险时看最危险的那个。没人危险时 AI 想放 R，改成普攻，R 留着 |
| 别人的「不死」 | — | 身上已经有别人给的「不死」（基兰的符文、凯尔的大招等）的人不算危险 |
| 千珏之印（v0.2.0） | 她普攻打过的敌方英雄 3 秒内阵亡就加一层印记，谁都算，没有哪个英雄头上有印记；她一死印记清空 | **照英雄联盟狩猎**：每 **75 秒**指名一名敌方英雄（6 秒内没和她交过手的，挑最脆的），他头顶出现半透明的印记，**8 秒**后变成完整的印记、狩猎生效；她**参与击杀**（击杀或助攻）被狩猎的英雄得一层印记，这个英雄 **240 秒**内不会再被指名；到下一次指名时他还活着就作罢、重新指名。**印记死了不掉**。每层的数值照主包（射程 +15、攻速 +4%、横生惧意 +8 魔法伤害）；层数显示在她头顶（主包 0.333.0 起，league.dll 的层数数字） |

## 怎么做的

- `mod.override_info` 把主包的千珏换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_kindred.py` 的 `r_now=1`
  生成，主包的千珏改了就重跑）：**R 一放出就落法阵**（第 20 tick，半径 50000），不再待命、不退还冷却，普攻、Q、E 里不再检查危险；
  R 的说明开头加【附加包】。v0.1.6 起放出那一刻圈内的友方英雄就先免死，接到法阵落地（见下面的 v0.1.6）。
- **挑时机**（AI 钩子 `league_kindred:ult`）：每次 AI 思考时记下己方英雄最近 1 秒的生命比例；R 冷却好、等级够、她没被控住时，
  看她身边 42000（法阵 50000 小一圈：落下前那 20 tick 人还会走）内的己方英雄（含她自己）：身边 45000 内有敌方英雄、身上没有别人的
  「不死」、而且生命低于 30% 或 1 秒内掉了 30% 以上且只剩 60% 以下——**AI 没想放也放**，施放目标是她 70000 内最近的敌方英雄
  （主包 R 的施放条件）。其余时候 AI 想放 R（主包的 R 不指定目标）：改成普攻她射程（55000）内最近的敌方英雄，
  打不到就朝 70000 内最近的敌方英雄走——不会原地停一下。她正忙时引擎要几 tick 才接放 R 的命令，钩子每 tick 再下一次；
  **R 的冷却真的开始走才算放出去一次**（日志只记一条）。
- 法阵、不死、结束时的回血、画面和声音全是主包的数据；原生代码只挑时机。
- **狩猎**（v0.2.0，用户 2026-11-11：「千珏印记是不是不能印记英雄啊 你看看 如果不能的话就要改了」；被动 `league_kindred:hunt`，`src/hunt.rs`）：
  副本用 `build_kindred.py` 的 `p_native=1` 生成，普攻里去掉数据那套「打过的英雄 3 秒内阵亡」的近似，印记全由这个被动给。
  英雄联盟的规则（客户端 zh_CN 说明、wiki，2026-11-11 读）：羊灵指名一名敌方英雄（最近 6 秒没交过手的），8 秒后生效；参与击杀被狩猎的
  目标得一层永久印记；成功狩猎过的英雄 240 秒内不会再被指名；75 秒指名一次。AI 点不了头像，挑**最大生命最少**的（一样就当前生命比例低的）。
  完成看击杀记录：她是击杀者或助攻者、而且狩猎已经生效。得印记时加主包的 `league_kindred_p_mark`（数值由副本的 params 传来）、
  `league_kindred_p_has`（横生惧意读它）、她头顶主包的得印记画面和音效；她死着时完成的记成欠的，复活后补上。被狩猎的英雄头顶的印记是
  她自己的千珏之印（主包 `league_kindred_fx` 的 `p_stack` 旋涡，`tools/art/fx_kindred_hunt.py` 放到他头顶 47 像素：`wait` 半透明一闪
  一闪、`on` 完整），两边各有千珏时名字分开。狼灵狩猎野怪没有做。
- **印记死了不掉**：活着时记下身上每一层印记和「有印记」的旗子（按完整的数值配对，和 league_veigar_power 一样），少了就补回。
- **附加包版本的数值**：大招按真实血量放、救人更准，模拟里她强到 +2.09 / +1.96（同组打野约 +1.3）。用户选「保留 4 秒法阵」，副本里改成：大招冷却 120 秒（英雄联盟原版）、结束回血 40 + 10% 攻击力、攻击力 90 → 88，模拟 +1.29 / +1.16（`make_override.py` 的 `NUMBERS`；不装附加包的主包不变，+1.18 / +1.18）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.333.0 以上）要装着并启用。
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
   - v0.2.0 狩猎：`HUNT PICK 英雄#id (hp 当前/最大, n candidates)` 指名；`HUNT ARMED on 英雄#id` 8 秒后生效；`HUNT DONE on 英雄#id: a mark (n hunts this match)`
     她参与击杀了被狩猎的英雄；`HUNT LOST on 英雄#id: died without her / before it armed / no kill record` 落空；`HUNT LAPSED on 英雄#id (alive after 75 s)`
     作罢；`ALIVE / DEAD with n marks kept`、`MARKS KEPT: n put back (alive / dead), n marks` 印记死了不掉。

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

## 大招放下就护住（v0.1.6，2026-11-07）

2026-11-07 的日志（`league_kindred.log`）：约 480 次大招里 59 次（12%）目标在施法后 0–21 tick 死掉——法阵要到 `r_at`（20 tick）才落地，
第一次免死在那之后。英雄联盟的羊灵生息放下就生效。现在施法那一刻先给她身边 `r_r` 内的友方英雄（含她自己）挂 `r_at` + `r_per` + 2 tick 的
`league_kindred_r_safe`（免死），接上法阵自己的第一次；法阵和画面照旧在 `r_at` 落下（`tools/kit/build_kindred.py` 的 `bridge`）。主包数据和
本包的副本一起重新生成；DLL 没变（挑时机的钩子照旧）。2026-11-08 夜里的日志：483 次大招只有 5 次目标死掉（之前 12%），写明时刻的 3 次都在
施法后 0–10 tick、身上没有 `r_safe`。
