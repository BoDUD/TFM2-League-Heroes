# 安妮附加包（测试版 v0.3.1，可选）：Q 返还、提伯斯是真的单位

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」；2026-11-14 看了和英雄联盟不一样的地方的清单：「全改吧」。

英雄联盟里安妮的 Q「碎裂之火」击杀目标时返还法力和一半冷却，玩家用它补兵；提伯斯是一只自己走、自己打、能被打死的熊。主包是纯数据：引擎没有「打死了就减冷却」的效果，Q 击杀不返还；数据里也没有「召唤一个单位」，提伯斯是挂在目标身上的一串画面和灼烧。**不装这个附加包，主包的安妮也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| Q 击杀 | 不返还 | 返还一半冷却（120 tick；小兵、野怪、英雄都算） |
| 法力 | 没有 | 没有 |
| 提伯斯（v0.3.0，游戏里还没看过） | 画面和灼烧挂在目标身上，紧跟他 6 秒，每秒灼烧周围 14 + 8% 法强；目标阵亡就化烟离场 | 一个真的单位，落在砸下去的地方，留 8 秒：自己追、自己打（每下 12 + 7% 法强的物理伤害，1.6 秒一下），每秒灼烧身边 30000 内的敌人 7 + 4% 法强，可以被打死；安妮先死了他接着打。宿主给不出单位时照 v0.2：挂在目标身上，目标阵亡就转向 50000 内最近的敌方英雄 |

## 怎么做的

- `mod.override_info` 把安妮换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：Q 的两枚火球（带眩晕的和不带的，`league_annie_q`）打中时，在伤害之后多调用一次原生效果 `league_annie_q:refund`；Q 的说明开头加【附加包】、末尾加一句。
- 原生效果的 `input` 就是被打中的单位：他已经死了（不再活着或生命为 0），就 `entity_reduce_cooldown` 把 Q 的剩余冷却减 120 tick。

- 提伯斯：副本的 R 保留召唤那一下（落地、130 + 70% 法强、嗜火眩晕），去掉挂在目标身上的跟随（目标身上的持续效果和 15 个定时检查），改成给目标挂 `league_annie_q_tib_mark`；被动 `league_annie_q:tibbers` 看到标记就开始（下面两节：先试单位，不行就挂在目标身上）。

## 提伯斯是真的单位（v0.3.0，2026-11-14，试点）

清单里十几位英雄共同的一条是「召唤物不会走、不会打、打不掉」。稳定 mod API 有 `spawn_unit`（「生成一个有时限的战斗单位，会追、会打附近的敌人」），别人的 mod 用它做过提伯斯。公用的部分在萨科附加包的 `src/summon.rs`（这里用 `#[path]` 引进来），萨科的幻像是第一个试点，提伯斯是第二个（第一个要自己的图的）。

- 英雄联盟（wiki 现行页面）：提伯斯最多留 45 秒；生命 1150–4100 + 50% 法强，护甲、魔抗 30–100；普攻 30 / 45 / 60 + 10% 法强的魔法伤害，攻速 0.625；光环每秒 8 / 12 / 16 + 4% 法强，半径 350；安妮死了他回一半血、狂暴、追杀凶手。
- 这里：落地的画面放完的那一 tick（R 出手后 24 tick），被动在画面里那只熊站的地方（目标身后 10000：画面上在他上方 10 像素；目标被砸死了就按他倒下的地方算）排一个原生效果 `league_annie_q:tibbers`，它调 `spawn_unit`：
  - 名字 `league_annie_tibbers`。单位按名字找图（`asset/base/aseprite_resources/champions/<名字>`），本包的 `mod.override_info` 把这个名字接到主包的 `league/champions/league_annie_tibbers`（`tools/art/unit_annie_tibbers.py` 用特效图里他自己的帧拼的：站立、挥爪、化烟是原来的帧，走路是用站立那一帧按整像素挪出来的六帧）。不是高清帧，和他今天在画面上一样大（42 像素高）。
  - 活 480 tick（8 秒）；生命 = 安妮生命上限的 120%，护甲、魔抗 = 她的 + 20，移速 1050；
  - 普攻：距离 15000、间隔 96 tick（英雄联盟的 0.625 攻速）、动作 27 tick、第 10 tick 命中（和图里挥爪那一帧对上，`make_override.py` 检查），每下 12 + 7% 法强——单位的普攻是物理伤害（英雄联盟里是魔法）。
- 被动接手（`spawn_unit` 返回的 id 由效果挂在安妮身上的一个 6 tick buff 交过来）：每 tick 看他一眼，每秒记一行；落地后第 30 tick 起每 60 tick 灼烧一次（7 + 4% 法强的魔法伤害，他身边 30000 内除防御塔外的敌人，火圈和吼声播在他身上）；他没了（被打死或到时间）就在他站的地方播化烟（副本多了一个画面 `league_annie_q_tib_bye`：单位图自己的 `dead`，和他的地面线对齐）。
- 安妮先死了：死掉的英雄的被动不跑，他由引擎管着接着打；灼烧由排好的 `league_annie_q:aura` 每 60 tick 接着烧（每次再排下一次），到他没了或者安妮的尸体没了为止。这时没人看着他，结束时没有本包的化烟（单位图里有 `dead`，引擎放不放要看游戏）。
- 生成不了：宿主没有 `spawn_unit` 这个槽、返回失败、给的 id 5 tick 内读不成单位、单位 6 tick 内就没了、或者测试开关关了——就照 v0.2 挂在目标身上（下一节），第一爪晚 2–4 tick。

### 伤害的账

挂在目标身上的提伯斯（主包和 v0.2）：落地后 384 tick 里烧 6 次（第 24、84 … 324 tick），每次 14 + 8% 法强，目标一次都躲不掉：**84 + 48% 法强**（火圈里的其他人一样）。

做成单位以后（落地那一下 130 + 70% 法强是数据，不变）：

| | 次数 | 每次 | 合计 |
|---|---|---|---|
| 光环 | 8 次（落地后第 30、90 … 450 tick） | 7 + 4% 法强（魔法） | 56 + 32% 法强 |
| 普攻 | 最多 5 下（96 tick 一下，第 10、106 … 394 tick） | 12 + 7% 法强（物理） | 60 + 35% 法强 |
| 一直够得着同一个人 | | | 116 + 67% 法强（原来的 1.35–1.4 倍） |
| 估计：光环 85% 的时间烧得到、普攻 60% 的时间够得着 | | | 约 84 + 48% 法强（和原来一样） |

也就是：光环一秒是原来的一半（和英雄联盟 1 级光环的 8 + 4% 差不多），另一半给了他自己的普攻，再多留 2 秒补上他走路的时间。法强 40 / 140 / 240 / 400 时的估计值是原来的 94% / 96% / 97% / 100%（`cargo test` 里 `the_units_damage_is_about_the_riding_ones` 算的）。「85%」「60%」是猜的：单位要自己走过去，目标会跑、他会被打死。游戏里每个提伯斯结束时日志会写他的光环实际烧了几次、烧到几个人（见下），普攻打了几下 API 读不到，要看画面。经典模拟器不跑原生代码，这个改动量不出来。

### 没法在这里验证的（要一局游戏）

已经确认的：编译，单元测试和 `tests/wiring.rs`（在一个假宿主里走完整条线：落地画面放完才生成、属性、每秒灼烧 8 次、到时间 / 被打死各化烟一次、安妮先死他接着烧、目标被砸死照样生成、宿主不给单位时照 v0.2 挂在目标身上烧 6 次）；单位图逐帧放大看过。

游戏里看日志 `league_annie_q.log`（`[view …]` 是你看的那场，每行都记；`[presim …]` 是服务器预演，每种行前 40 行、之后每 200 行一行）：

| 日志 | 说明什么 |
|---|---|
| 开头第二行 `TIBBERS: a unit of his own ('league_annie_tibbers', spawn_unit) - ON … Test knobs (…): none` | 这一版装上了，开关没动 |
| `TIBBERS #n on #7` → `TIBBERS #n ASK #k: the unit asked for at (x,y) (10000 behind #7, where the drop's picture stands)` | R 的标记读到了；24 tick 后在哪要的单位 |
| `TIBBERS SPAWN #k (the queued effect): unit #id for team t at (x,y): 'league_annie_tibbers' for 480 ticks, attack 28 ap 240 hp 2280 def 110 mr 70 speed 1050; hits 0 + 100% of its attack, range 15000, every 96 ticks (27 long, lands at 10)` | `spawn_unit` 给了单位（**没有这行、而有 `TIBBERS SPAWN FAILED` / `NONE` / `LOST`：接口不能这样用，画面上是 v0.2 挂在目标身上的熊**） |
| `TIBBERS #n LOOK #k: #id reads back as name '…' kind summon team t champion=false … radius … hp …/… attack … speed … attack interval …` | 一个不是英雄 id 的名字行不行；读回来算哪一类、属性对不对 |
| `TIBBERS #n #k: 61 of 480 ticks, at (x,y) (walked 34100, …), hp 2280/2280 (-150 in the second), 22000 from its summoner; near it: champion #7 … 9000 away hp 812; minion …; its summoner's damage statistic +80 in the second (now 5210)` | 每秒一行：走不走、跟不跟安妮、身边没人时干什么、敌人打不打他、他在打什么；安妮的伤害统计涨没涨（他打的算不算她的） |
| `TIBBERS #n AURA #k: pulse 3 - 16 magic to 2 enemies within 30000 of him at (x,y)` | 光环每秒一次，烧到几个人 |
| `TIBBERS #n OVER #k: KILLED / TIMED OUT after … of 480 ticks at (x,y), last seen with hp …; its dead body is still there / no entity under its id any more; near it: …; the enemy players in its last tick: p7 gold +37 cs +1; kill log +0; its summoner's damage statistic +310 over its life (now …); his aura: 8 pulses, 6 burned someone, 9 burns, 144 magic in all before resistance` | 被打死还是到时间；**敌方那一 tick 的金币 / 补刀 / 击杀**（给不给钱）；光环的实际次数（上面那张账表的「85%」） |
| `TIBBERS #n WAKE #k: its body was there for 37 ticks after its end` / `… the enemy players from the tick before its end to 3 ticks after: …` | 尸体留多久（引擎放不放单位图的 `dead`） |
| `TIBBERS #n ORPHAN #k: Annie died, the unit #id … has 212 ticks left … his aura goes on by the queued effect`，之后 `TIBBERS ORPHAN AURA #k: … (Annie is dead)` | 安妮先死 |

画面上要看的：熊在不在、站在地上还是浮着 / 陷下去（图按「脚在中心下面 11 像素」放的）、大小对不对（应该和以前挂在目标身上时一样）、走路的六帧顺不顺、挥爪和伤害数字对不对得上、头上有没有血条、敌人打不打他、死的时候是不是两团烟（引擎的 `dead` 和本包的画面叠在一起：位置一样的话看不出，错开了就要去掉一个）。`league.log` 里看有没有新的 `DIVERGE`。

### 测试开关

日志旁边放一个 `league_annie_q.cfg`（没有这个文件就是默认；加载时读一次，日志第二行会写读到了什么），每行一个：`unit=off`（不生成单位，照 v0.2）、`still=1`（移速给 1：试站着不动的召唤物）、`name=<名字>`（换一个单位名，只收字母、数字、下划线；没有对应的图会怎样不知道）。

### 还没做

- 普攻是物理伤害（`spawn_unit` 的攻击只有「攻击力的百分之几 + 固定值」，没有伤害类型）；英雄联盟里是魔法伤害。
- 不能指挥：引擎让他打谁就打谁；英雄联盟里他可以被安妮指挥、嗜火眩晕时狂暴。
- 安妮死后他不回血、不狂暴、不追凶手；他那时结束没有本包的化烟。
- **主包要带着 `league/champions/league_annie_tibbers` 这张图**：本包的 `mod.mod_info` 对主包版本的要求还没改（主包版本号由合并的人定），发布前要把它提到带这张图的那个主包版本。主包没有这张图时单位画成什么不知道。

## 挂在目标身上的提伯斯（v0.2，现在是生成不了单位时的退路）

- 被动看到标记就开始：第 24 tick 起每 60 tick 在目标身上播主包的站立挥爪 `league_annie_tibbers` 和火圈 `league_annie_r_ring`、声音，30000 内的敌人受到 14 + 8% 法强的魔法伤害（`Ap`），384 tick 后化烟（`league_annie_tibbers_vanish`）。目标阵亡（或不能选中）就转向 50000 内最近的敌方英雄，附近没人才离场。数字由 `make_override.py` 对照主包检查。日志：`TIBBERS #n on #7`、`#7 is gone, on to #9`。
- 0.2.1（2026-11-05，11-04 的日志）：安妮死时提伯斯悄悄没了——她重生时 `on_spawn` 直接丢掉记录，没有 `gone` 行、没有化烟的画面。现在她倒下（`on_dead`）就在他最后的位置播化烟（`league_annie_tibbers_vanish`），记 `TIBBERS #n gone (Annie died)`；万一没走到 `on_dead`，重生时补（`she respawned`）。挂在目标身上的提伯斯在安妮死后不能接着烧：死掉的英雄的被动不再跑，他的挥爪没人驱动（做成单位以后可以，见上）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上；提伯斯的单位图在 2026-11-14 之后的主包里）要装着并启用。
2. 把 `league_annie_q` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 安妮 Q 的说明开头是「【附加包】」、末尾写着「击杀目标时返还一半冷却」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_annie_q.log`：`Q KILL #n on #31: cooldown 200 -> 80`；提伯斯的行以 `TIBBERS` 开头（见上）。

## 开发

- `python addons/league_annie_q/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里安妮改了就重跑；单位图改了也重跑（它检查挥爪那一帧的时刻和 `src/lib.rs` 的 `TIB_ACT` / `TIB_LANDS` 对得上）。
- `python tools/art/unit_annie_tibbers.py`：重新拼单位图（`--check` 只比较，`--preview <png>` 出一张 8 倍的逐帧图）。
- `cargo test -p league_annie_q`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。测试用的假宿主是萨科附加包的 `src/summon_mock.rs`。

## 等提伯斯站稳再读他、每秒一行按行数（v0.3.1，2026-11-14）

第一批真实对局数据（游戏 0.7.2 的预模拟，`league_annie_q.log`）：

- 新单位生成那一拍和下一拍，最大生命、攻击、防御、移速都读成 1：提伯斯在生成那一拍被读，`TIBBERS #1 LOOK` 写的是 `hp 2124/1 attack 1 def 1 mr 1 speed 1`，看不出他的属性有没有照给的来。现在等他的最大生命读出来（萨科附加包 `summon.rs` 的 `Unit::settled`）才接手，`LOOK` 行是站稳以后的数字；5 次还没读出来就照样接手，行末写 `(its health cap still reads 1 after 5 looks)`。他身上不挂东西、不设生命，所以只晚一两拍接手（光环晚一两拍开始），别的不变。
- 每秒一行的计数（U4 发现的）：`if let (Some(line), Some(k)) = (line, tally(..))` 每 tick 都数一次，日志里成了 `TIBBERS #1 #18418:`，预模拟里「前 40 行、之后每 200 行一行」变成按 tick 算，每秒那一行几乎出不来；现在有一行才数。
- 测试多一个「站稳要两拍」的（假宿主 `World::settle = 2`），别的测试没改。
