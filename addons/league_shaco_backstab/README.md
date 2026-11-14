# 萨科附加包（测试版 v0.3.1，可选）：背刺看朝向、幻像和惊吓魔盒是真的单位

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」；2026-11-14 看了和英雄联盟不一样的地方的清单：「全改吧」。

英雄联盟里萨科从背后打到敌人就是背刺；大招的幻像是另一个萨科，自己走、自己打，能被打死。主包是纯数据：读不到朝向，普攻和毒刃打中**被控制**的敌方英雄（被恐惧的人背对着他逃跑）才多一下背刺；数据里也没有「召唤一个单位」，幻像的画面和伤害是挂在目标身上的。**不装这个附加包，主包的萨科也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 普攻、毒刃的背刺 | 打中被控制的敌方英雄：+15 + 25% 攻击力 | 从背后打中敌方英雄：+15 + 25% 攻击力 |
| Q 落地那一刀 | 主包 | 一样 |
| R 幻像（v0.2.0，游戏里还没看过） | 画面和伤害挂在目标身上 5 秒：萨科每打一下它跟着砍一下（10 + 40% 攻击力）；到时间或目标死了就爆炸 | 一个真的单位，出现在萨科身旁：自己追、自己打（每下 10 + 40% 攻击力，间隔照萨科的普攻），属性照萨科、生命和他当时一样，受到的伤害 +50%，可以被打死；被打死或 5 秒到了就在它站的地方爆炸（150 + 100% 法强、恐惧、三个小魔盒，数字同主包）。宿主给不出单位时和主包一样 |
| W 惊吓魔盒（v0.3.0，游戏里还没看过） | 一张画面：落地、弹开，恐惧和 5 秒的射击区域，打不到 | 魔盒有一个**身体**——真的单位，敌人能选中、能打掉（生命是他上限的 25%）；落地时生成、弹开前放逐着（落地的画面照放），弹开时出来；射击由附加包按主包的节奏打（5 秒 10 轮，每轮 10 + 12% 法强打周围所有敌人），从身体站的地方，身体被打掉就停；恐惧和声音照旧。宿主给不出单位时照主包 |

## 怎么做的

- `mod.override_info` 把萨科换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：两枚只打 `EnemyChampionInCC` 的分身弹（`league_shaco_a_bs` / `league_shaco_e_bs`）改成打所有敌方英雄，只给他挂 3 tick 的 `league_shaco_bs_ask`；普攻的说明开头加【附加包】、「被控制」换成「从背后」。
- 被动 `league_shaco_backstab:backstab` 每 tick 记下每个敌方英雄最近 10 tick 的位置：
  - 朝向：这 10 tick 走了 1500 以上就是他走的方向；站着不动（在打东西）就朝着离他最近的萨科一方英雄或小兵；
  - 背后：萨科在他朝向的反方向那一半；
  - 是就补物理伤害（`Ad`，吃护甲，数字在 `passive.params`，从主包读），播主包的背刺画面和声音。
- 被恐惧的人背对着萨科跑，照样算背刺；面对面打他不算。

## 幻像是真的单位（v0.2.0，2026-11-14，试点）

清单里十几位英雄共同的一条是「召唤物不会走、不会打、打不掉」。稳定 mod API 从第一版就有 `spawn_unit`（「生成一个有时限的战斗单位，会追、会打附近的敌人」），别人的 mod 用它做过提伯斯；我们还没用过。萨科的幻像是第一个试点（不用新画图），公用的部分在 `src/summon.rs`（安妮的提伯斯也用它）。

- 英雄联盟（wiki 现行页面）：幻像最多留 18 秒，攻击力照萨科、每下只有 60% 伤害，受到的伤害多 50%，生命和萨科当时一样；被打死或到时间就爆炸（150 / 225 / 300 + 70% 法强），放出三个小魔盒（恐惧英雄 1 秒）。这里时间和数字照主包已经调过的：5 秒，每下 10 + 40% 攻击力，爆炸 150 + 100% 法强、恐惧 0.75 秒（非英雄 1.25 秒）、小魔盒 5 次 8 + 10% 法强——所以它打出的伤害不会比主包挂在目标身上的那个多多少（每下一样；一直够得着人时 5 秒里最多 6 下，主包那个 5–6 下），而且现在要自己走过去、会被打死。
- 副本的 R：出手时去掉 `league_shaco_r_unit`、给萨科挂 3 tick 的 `league_shaco_r_ask`；挂在目标身上的那个幻像（第 12 tick 的那一整块）外面套一个 `SwitchByBuff league_shaco_r_unit`：身上有这个标记就不放。
- 被动看到 `r_ask`：在萨科身旁 14000 处选一个点（和他并排，横在他和最近的敌方英雄的连线旁边，每放一次换一边；两个身体叠在一个点上看起来只有一个萨科，原版引擎自己的召唤物也是出现在召唤者身边 20000 处。这个点不会选到场上所有单位围成的范围之外——那一边出了范围就用另一边，两边都没地方就在他站的地方：离开地图格子的点引擎怎么处理不知道，不试），排一个原生效果 `league_shaco_backstab:clone`。这个点落在墙里时引擎把单位放到哪要看游戏（`CLONE SPAWN` 写的是要的点，`CLONE #n LOOK` 的 `at (x,y)` 是单位读回来的位置）。
- `:clone` 调 `spawn_unit`：名字 `league_shaco`（单位按名字找图，叫他自己的 id 就该用他自己的图，高清帧在内——**要在游戏里看**），阵营是他的，活 312 tick，属性照他此刻的（攻击、法强、防御、移速一样，生命上限一样），普攻距离 23000、间隔 52 tick、动作 22 tick、第 9 tick 命中，每下 10 + 40% 攻击力。成功了给萨科挂 `league_shaco_r_unit`（342 tick）——数据在第 12 tick 看到它，挂在目标身上的幻像就不放；再挂一个名字里带单位 id 的 6 tick buff 交给被动。
- 被动接手：给幻像挂「受到的伤害 +50%」（`league_shaco_clone`），把它的生命设成萨科当时的，在它身上播现身的烟和声音；之后每 tick 看它一眼，每秒记一行。它没了（被打死或到时间）就排 `:burst`，在它最后站的地方：150 + 100% 法强的魔法伤害、恐惧、主包的爆炸和小魔盒画面，再排 5 次 `:box`（每次 8 + 10% 法强）。
- 回到原来的做法（标记不挂 / 去掉，数据照主包放挂在目标身上的幻像）：宿主没有 `spawn_unit` 这个槽、返回失败、给的 id 5 tick 内读不成单位、单位 6 tick 内就没了、或者测试开关关了。
- 萨科先死了：死掉的英雄的被动不跑，幻像由引擎管着接着打；被动在他倒下时排一个 `:end`，在幻像到时间前 2 tick 让它在站的地方爆炸。这期间它被打死就不爆炸（没人看着）。
- 数字都是主包的：`make_override.py` 把 `src/lib.rs` 的 `CLONE_*`、`BOOM*`、`FEAR_*`、`BOX_*` 和主包的 R、普攻逐个对照，主包改了它就停下来。

### 没法在这里验证的（要一局游戏）

经典模拟器不跑原生代码，这台机器上也不能开游戏。已经确认的：编译，单元测试和 `tests/wiring.rs`（在一个假宿主里走完整条线：生成、标记、受伤 +50%、到时间 / 被打死各爆炸一次、萨科先死、宿主不给单位时不挂标记）；副本在经典引擎上和改之前打出一样的对局（标记不会出现，走的是原来那一支）。

游戏里看日志 `league_shaco_backstab.log`（`[view …]` 是你看的那场，每行都记；`[presim …]` 是服务器预演，每种行前 40 行、之后每 200 行一行）：

| 日志 | 说明什么 |
|---|---|
| 开头第二行 `CLONE: Hallucinate's clone is a unit ('league_shaco', spawn_unit) - ON … Test knobs (…): none` | 这一版装上了，开关没动 |
| `CLONE ASK #n: R cast at (x,y), the clone asked for at (x,y) (14000 beside him, across the line to the nearest enemy champion at (x,y))` | 数据的 `r_ask` 被动读到了；点选在哪 |
| `CLONE SPAWN #n (the queued effect): unit #id for team t at (x,y): 'league_shaco' for 312 ticks, attack … hp … speed …; hits 10 + 40% …` | `spawn_unit` 给了单位（**没有这行、而有 `CLONE SPAWN FAILED` / `CLONE NONE` / `CLONE LOST`：接口不能这样用，画面上是原来的幻像**） |
| `CLONE #n LOOK: #id reads back as name '…' kind summon team t champion=false … radius … hp …/… attack … speed … attack interval …; given +50% damage taken; health to his own …: set` | 单位读回来叫什么、算哪一类（`kind`）、是不是被当成英雄、属性对不对、`entity_set_hp` 行不行 |
| `CLONE #n DRESS: … the +50% damage taken buff is on it, its health …` | buff 能不能挂到召唤物上（`is NOT` = 挂不上） |
| `CLONE #n #k: 61 of 312 ticks, at (x,y) (walked 34100, …), hp 600/1000 (-150 in the second), 22000 from its summoner; near it: champion #7 league_garen 9000 away hp 812; minion …` | 每秒一行：它走不走（`walked`）、跟不跟萨科（`from its summoner`）、身边没人时干什么、掉不掉血（敌人打不打它）、在打什么（它身边最近的各类敌人和他们的血） |
| `CLONE #n OVER: KILLED after 200 of 312 ticks at (x,y), last seen with hp …; its dead body is still there / no entity under its id any more; near it: …; the enemy players in its last tick: p7 gold +37 cs +1; kill log +0` | 被打死还是到时间；死的时候身边是谁；**敌方玩家那一 tick 的金币 / 补刀 / 击杀涨没涨**（给不给钱）；尸体留不留 |
| `CLONE BURST #n at (x,y) (queued): 180 magic to 2 enemies within 30000; feared 45 ticks: [#7 league_garen 9000 away], 75 ticks: 3 others; #7's fear reads back as 45 ticks toward (dx,dy) (asked (dx,dy)); 5 of 5 box shots queued` | 爆炸一次；原生给的恐惧引擎记成什么 |
| `CLONE BOX #n at (x,y): 11 magic to 2 enemies within 32000; champions: [#7 league_garen 15000 away (feared)]` | 小魔盒的 5 次射击；**同一个英雄一行比一行远** = 恐惧真的让他跑开了 |
| `CLONE #n WAKE: its body was there for 60 ticks after its end` / `… the enemy players from the tick before its end to 3 ticks after: …` | 尸体留多久（引擎放不放 `dead` 动作）；死后几 tick 敌方的金币 |
| `CLONE #n ORPHAN: Shaco died, his clone #id … has 212 ticks left … its blast is queued for its time` | 萨科先死 |

画面上要看的：幻像是不是萨科的样子、是不是和他一样大（高清帧没缩 = 大两倍）、走路 / 攻击 / 倒下播不播动作、头上有没有血条和名字、敌人打不打它、爆炸和小魔盒的画面在不在它站的地方。`league.log` 里看有没有新的 `DIVERGE`（预演和画面走岔）。

### 测试开关

日志旁边放一个 `league_shaco_backstab.cfg`（没有这个文件就是默认；加载时读一次，日志第二行会写读到了什么），每行一个：

- `unit=off`：不生成单位，回到原来的幻像（出问题时不用重装就能关掉）。
- `still=1`：单位的移速给 1（几乎不动）——试「炮台」那一类召唤物能不能站着打。不给 0，怕引擎拿它做除数。
- `name=<名字>`：换一个单位名（只收字母、数字、下划线），试「名字是不是随便起」。没有对应的图会怎样不知道，只在测试时用。

### 还没做

- 三个小魔盒还不是单位（打不掉、不占位置）：画面和 5 次射击照主包。
- 幻像不能指挥：引擎让它打谁就打谁（多半是最近的敌人，不一定是 R 的目标）。
- 萨科死后幻像被打死不爆炸。
- 英雄联盟里敌人看幻像和本人一样（骗人用）：这里它的属性、生命和他一样，画面一不一样要看游戏。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_shaco_backstab` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 萨科普攻的说明开头是「【附加包】」、写着「从背后」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shaco_backstab.log`：`BACKSTAB #n on #7: +60 physical (12 of 40 hits from behind)`（`#n` 是整个游戏的第几次，括号里是这一局的）。
   v0.1.1：`BACKSTAB`、`SPAWN` 整个游戏一个计数（预模拟先记 40 行、之后每 200 行一行，你看的那场每行都记），参数只在第一行 `SPAWN` 写；以前每个萨科自己数「前 80 行」，2026-11-03 夜里的日志 1339 行里 1131 行是 `BACKSTAB`。玩法不变。
   v0.2.0：幻像的行以 `CLONE` 开头（见上）；每个敌方英雄的走路记录不再跟着复活越攒越多（复活是新的单位 id，旧 id 的记录现在会清掉）。

## 开发

- `python addons/league_shaco_backstab/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里萨科改了就重跑（幻像的数字和主包对不上时它会停下来，先改 `src/lib.rs`）。
- `cargo test -p league_shaco_backstab`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。`src/summon_mock.rs` 是测试用的假宿主（我们对引擎的猜想，只检查自己这一边的逻辑）。

## 惊吓魔盒是真的单位（v0.3.0，2026-11-14）

用户：「召唤物的全做啊 剩下的一批英雄也做了啊 都做完了装进去了再测」。召唤物第二轮。代码在新文件 `src/jack.rs`，幻像的代码和 `summon.rs` 没动（`lib.rs` 只多了接线：一个字段、三处调用、两个原生效果、日志第三行）。附加包的代码 + 主包一张单位图 `league/champions/league_shaco_jack`（`tools/art/unit_shaco_jack.py`：魔盒自己的画面 `w_box` 的 1 倍帧——这张特效图是特效高清表里的，游戏按 1 倍的大小画，所以和今天一样大，不用在 league.dll 里登记：idle / run 小丑探出来的两帧，attack 探出来 → 射一下 → 探出来，hit 往后一格，dead 缩回去、一团烟、没了）。**要和带这张图的主包一起装**。

- 英雄联盟（wiki 现行页面）：魔盒生命 150–550、护甲 50、魔抗 100，弹开时恐惧周围的敌人（英雄 0.5–1.5 秒、其余 2.2 秒），之后 5 秒每 0.5 秒射一下（10–30 + 12% 法强），英雄的普攻一下打掉它三分之一，打掉给 10 金币；没弹开前隐身。
- 副本的 W 落地时（抛物线的 end_effects）跑原生效果 `league_shaco_backstab:jack`：在落点生成身体 `league_shaco_jack`：移速 1、攻击 0（射程、节奏是魔盒的，只为了朝着敌人、播射一下的动作），生命是他上限的 25%，护甲 100%、魔抗 190% 他的（英雄联盟的数字对他的数字），留到射完（10 + 300 + 2 tick）；马上放逐 9 tick（主包落地的画面照放，弹开时身体出来）；成功了给他挂 15 tick 的 `league_shaco_w_unit`：副本的数据在弹开那一 tick 读它，不画弹开的画面（`w_box`）、不放射击区域（`w_shots`）；恐惧和声音照旧是数据的。
- 被动从弹开后第 1 tick 起每 30 tick 由他打一轮：身体现在站的地方 35000 内的每个敌人（不打塔）10 + 12% 法强的魔法伤害、主包的命中画面，共 10 轮；身体被打掉（`OVER … KILLED`）就停。萨科先死了：剩下的几轮排成原生效果 `league_shaco_backstab:jack_shot`（排好的效果对死了的施法者也跑——幻像的 `:end` 也这样），在身体最后站的地方打。
- 退路：宿主没有 `spawn_unit`、失败、读不成单位、测试开关 `unit=off`——不挂 `league_shaco_w_unit`，数据照主包放画面和射击区域；读不成单位时把标记去掉。
- 日志（都以 `JACK` 开头）：第三行 `JACK: … - ON`；`JACK SPAWN #`（身体的单位 id、位置、`banished until it springs: yes / REFUSED`、数字）→ `JACK #n LOOK #`（读回来的名字、种类、能不能选中——放逐着应该是 false、生命、`speed` 是不是 1）→ 每秒一行 `JACK #n #k:` → `JACK #n SHOT #`（第几轮、打中几个）→ `JACK #n OVER #`（被打掉还是到时间、敌方那一 tick 拿了多少钱、打了几轮）→ `WAKE #`；`JACK #n ORPHAN #` / `JACK ORPHAN SHOT #`（萨科先死了）；`JACK HOOK #`；失败时 `JACK SPAWN FAILED` / `JACK LOST` / `JACK NO SPOT`（落点不是一个位置）。
- 测试开关：和幻像共用日志旁边的 `league_shaco_backstab.cfg`（`unit=off` 两样都不生成、`name=<名字>` 换单位名——会同时换掉幻像的名字，测试时注意）。
- 测试：幻像的测试一个字没改，只有 `tests/wiring.rs` 数注册的原生效果从 4 改成 6（多了 `:jack`、`:jack_shot`）；魔盒的测试在新的 `tests/jack.rs`（单独一个测试进程，日志写到自己的临时文件）。
- 第一批真实对局数据（游戏 0.7.2 的预模拟，2026-11-14，玛尔扎哈和悟空的日志）：原生效果里的 `spawn_unit` 管用，单位会被小兵打死；单位的攻击不会告诉召唤者的 `on_attack`（所以 `JACK HOOK` 多半不会出现）；生成那一 tick 对单位做的事可能被盖掉——魔盒第一次读成单位时要是还选得中（放逐没生效），就再放逐到弹开为止（LOOK 行末尾 `banished again`）。
- 还没做：没弹开前隐身（没有隐身的接口：这里本来也是扔到脚下立即弹开）、英雄的普攻一下打掉三分之一（没有按来源固定的伤害）、打一个人时伤害更高、三个小魔盒（幻像爆炸放出的）还不是单位。

## 等单位站稳再给它穿衣服（v0.3.1，2026-11-14）

第一批真实对局数据（游戏 0.7.2 的预模拟）：新单位生成那一拍和下一拍，最大生命、攻击、防御、移速都读成 1，那时设的生命会被盖掉——悟空的分身生成后一拍读到 `hp 1851/1 attack 1 def 1 mr 1 speed 1`，代码按「上限 1」把生命设成了 1，再一拍读到 1851/1851。萨科的幻像原来在交接那一拍就挂「受到的伤害 +50%」、把生命设成他的，正好落在这两拍里。

- 幻像：交接后至少等一拍，再等它的最大生命读出来（`summon.rs` 的 `Unit::settled`），才挂 +50%、设生命、放现身的烟（妮蔻 W 的做法）；5 次还没读出来就照样接手，`CLONE #n LOOK` 行末写 `(its health cap still reads 1 after 5 looks)`。数据在出手后第 12 tick 才读标记，晚两拍接手来得及。
- 公用模块 `summon.rs` 的 `Flock`（一个召唤者好几个单位：约里克、玛尔扎哈、纳亚菲利、伊莉丝、黑默丁格、婕拉、俄洛伊、丽桑卓的冰仆、本包的惊吓魔盒）同样等它站稳才给 `Look`；假宿主里单位一生成就站稳（`World::settle` 默认 0），所以别的测试一个字没改；`tests/flock.rs` 多一个站稳要两拍的测试。这些英雄的 `LOOK` 行从此是站稳以后的数字（以前全是 1），魔盒「还选得中就再放逐」也在站稳以后判断。
- 每秒一行的计数（U4 发现的）：原来 `if let (Some(line), Some(k)) = (line, tally(..))` 每 tick 都数一次，预模拟里「前 40 行、之后每 200 行一行」变成了按 tick 算，幻像每秒那一行几乎出不来；现在有一行才数。
- 测试：幻像多一个「站稳要两拍」的测试（照旧在那两拍里设生命的话，幻像会是 1 血或满血）；别的测试没改。

## 双面毒刃对低血量目标多 50%（v0.3.1，2026-11-14）

用户 11-14 看了还剩下的、做得到的小项：「接着做」（SMALL_KIT_BRIEF S1 第 9 条，因为本包在改召唤物先放着）。英雄联盟（wiki 现行页面）：双面毒刃的飞刀「deals magic damage, increased by 50% if they are below 30% of their maximum health」。主包的数据读不到生命，没有这一条。

- 副本（`make_override.py` 的 `shiv`）：普攻里那一下毒刃（`league_shaco_e_shiv`）命中时最先跑原生效果 `league_shaco_backstab:shiv`（按挨这一下之前的生命判断）；毒刃的数字（55 + 70% 法强）和 `src/lib.rs` 的 `E_HIT` / `E_HIT_AP` 对照，主包改了脚本就停。
- 原生效果：目标生命低于最大生命的 30%（`E_LOW_PCT`）时多打毒刃伤害的 50%（`E_LOW_MORE`，魔法伤害，由他打出）；野怪也算（英雄联盟的毒刃对所有敌人）。毒刃的背刺（这里是被动的物理加成，普攻和毒刃一样）不跟着加。
- 说明（五种语言）：毒刃那一句加上「目标生命低于 30% 时多 50%」。
- 日志：第四行 `SHIV: …`；每次加成一行 `SHIV #k on #id <名字>: hp a/b, below 30% - +50% of the shiv's 55 + 70% of his N ability power: +M magic`（不加成不记）。
- 幻像、惊吓魔盒的代码没动；经典引擎模拟跑不了原生代码，量不出来；主包没动。
