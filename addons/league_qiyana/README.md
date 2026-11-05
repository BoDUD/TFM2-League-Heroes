# 奇亚娜附加包（测试版 v0.3.1，可选）

**不装这个附加包，主包里的奇亚娜也是完整的**：普攻和被动凌人贵气、Q 以绪塔尔之锋（身前一条直线；有元素时掷出环刃炸开：河流定身减速、
岩石加伤、草丛伪装加速）、E 天纵之勇（突进时用方圆塑令给武器附上元素、刷新 Q）、大招惊才绝景（冲击波伤害、击退再晕眩）和连招
E → Q、R → E → Q 都在主包数据里。主包是纯数据：**读不到地图和生命**，又只有三个技能格，W 方圆塑令只能并进 E、元素按草丛 → 河流 →
岩石轮换，大招见人就晕。这个附加包（2026-11-04 照英雄联盟 V26.21 重做，用户：「奇亚娜很多机制和英雄联盟不一样 你仔细对比看看怎么改吧」）
用原生代码把这些做成英雄联盟的样子：

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| W 方圆塑令 | 并进 E：每次突进按草丛 → 河流 → 岩石轮换给元素、刷新 Q | **自己的技能**（自动放，冷却 7 秒，学会 E 后）：打架时 Q 在冷却或手上没元素，就**冲向身边两格（64000）内的地形**（冲 18000）拿那种元素——草丛给草丛，墙和地图四边的石墙给岩石，河道给河流；几种都在时按局势挑（自己残血草丛，残血英雄岩石，其他英雄河流，野怪小兵岩石）——并刷新 Q（Q → W → Q）；E 落地时 W 好了也接一个（E → W → Q）；身边没有地形不放。复活时手上是岩石 |
| 元素附着 | 攻速 +25%、攻击距离 +1500，普攻和 Q、E 多打 15 魔法（+45% 法强） | 一样，魔法伤害是 15 + 15% 攻击力（+45% 法强）；离开战斗站在手上元素的地形旁边时移速 +8% |
| Q 以绪塔尔之锋 | 身前一条直线，第一个之后 75%；有元素时掷出环刃（52000），在第一个敌人或尽头炸开 | 一样，另外**野怪吃 160%**；动作距离是元素之怒的（46000），没元素时 AI 等目标走进直线再放 |
| 岩石 | 对谁都多打 25 + 40% 攻击力 | 只对**生命 50% 以下**的多打 60%（其余人 35%） |
| 草丛 | 伪装 2.5 秒、加速 20% | 脚下留一片**草地** 3 秒：站在里面伪装、加速 20%，普攻、放 Q / E / R 或走出去就没了 |
| E 天纵之勇 | 突进必中 | 落地时目标还在身边（15000 内）才打得到 |
| 凌人贵气 | 普攻和 Q、E，一次触发后 4 秒内谁都不加伤，换新元素时重置；R 不算 | **每个敌人单独算**：同一个敌人 25 秒一次；W 换来**别的**元素时，上次带着别的元素（或没元素）触发的敌人可以再触发 |
| R 惊才绝景 | 冲击波打中路上所有人：50 + 90% 攻击力、英雄另受最大生命 10%，击退后晕眩 0.9 秒 | **风只击退、不伤害**，碰到第一面墙就停；**冲击波沿路过的草丛、河道和撞上的那面墙的边扩散**：50 + 90% 攻击力 + 最大生命 10%（野怪最多 300），按离起点远近晕 0.5～1 秒；什么地形都没碰到只击退。**AI 只在冲击波打得到敌方英雄时放**（挑打到最多的；没想放 R 时打得到两个也放），不然留着 |

## 怎么做的

- `mod.override_info` 把主包的奇亚娜换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_qiyana.py` 的 `native=1`
  生成，主包的奇亚娜改了就重跑；`--check` 只核对；它也核对 `src/lib.rs` 里 `params!` 的默认值和参数表 P 一样）：动作、动画、声音、
  冷却标记、连招都是主包的，打人的地方换成本包的原生效果——Q 出手 `league_qiyana:q`、E 落地 `league_qiyana:e`、普攻打中
  `league_qiyana:hit`、R `league_qiyana:r`；被动是本包的 `league_qiyana:empress`（数字在 `passive.params`，W、草地、复活的元素也是它跑）；
  四个技能的说明开头加【附加包】。
- **地形**（`src/terrain.rs`）：地图自定义钩子读地图文档的 `walls`（墙格子）和 `bushes`（草丛格子），和雷恩加尔、奈德丽的附加包一样，
  每种模式记一张，当前对局取站进墙里的单位最少的那张；格子 30 × 30，一格 32000。**河流先在地图文档里找**（`river`、`water` 等键）；
  地图文档里没有河，5v5 地图按中间那条斜带算：|x − y| ≤ 48000（穿过两个大野怪）。5v5 地图的四边（石墙、石堆）和地图外也算墙。
  合集 `league_addons` 一个 mod 只能有一个地图钩子：合集的 `MapReaders` 也调用本包的读法。
- **W**（`src/lib.rs` 的 `try_w`）：被动每 3 tick 看一次：学会 E、W 不在冷却（她身上的 `league_qiyana_w_cd`）、没被控、不在放技能，
  60000 内有看得见的敌方英雄（或 Q 够得着、掉了血的野怪），而且 Q 的冷却（主包的 `league_qiyana_q_cd`）还剩 90 tick 以上或手上没元素。
  挑元素后去掉身上的元素、挂上主包的 `el_on`（攻速、攻击距离）和那一种的 flag，去掉 `q_cd`，强制位移冲过去（墙停在墙前，草丛、河道冲进去
  一点），播 `w_on` 的画面和声音。
- **Q**（`q`、`q_blast`）：没元素时直接打身前那条线（31500 长，7000 + 身体宽），按离她远近第一个 100%、其余 75%，野怪再乘 160%。
  有元素时环刃（R 的金环画面 `league_qiyana_q_blade`）飞向第一个敌人（4000 + 身体宽的路上）或飞满 52000，到了炸开（10000 + 身体的圈）：
  第一个 100%、其余 75%，附着元素的魔法伤害，元素的效果。
- **R**（`src/ult.rs`）：风朝目标英雄吹（`windblast`：每 1000 一步查墙、草丛、河，碰到墙就停，最远 60000），画面是主包的
  `league_qiyana_r_wave` 飞到停点，碰到的敌人沿风的方向击退 25000（撞墙停在墙前，免控的不动）。16 tick 后冲击波（`shockwave`）：
  撞上的墙连着的墙格子里离停点 96000 内的那些格子的边 12000 内、地图边上停点前后 96000 内、路过的草丛连着的那一片里、进河的地方前后
  96000 的河道里——这些地方的敌人吃伤害和眩晕；打到敌方英雄就给她挂 `league_qiyana_r_go`，主包数据接 R → E → Q。读不到地图时照主包
  （路上的人都伤害、击退、晕）。
- **AI 钩子**（`src/ai.rs`，`league_qiyana:ai`）：R 好了时朝每个够得着的敌方英雄算一次（风路上的人先按击退挪过去），冲击波打得到
  敌方英雄才放，挑打到最多的；AI 想放 R 却谁都打不到就不放（改成 Q、E、普攻，AI 每 tick 都还想放 R）。AI 想放没元素的 Q 而目标还在
  直线够不着的地方就先不放（改成 E 或走过去）。

## 在游戏里测

日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_qiyana.log`，每次启动游戏重写（上一份改名 `.prev.log`）。每种行整次启动一个计数：
服务器的预模拟先记 40 行、之后每 200 行一行（`#n` 是第几行），你看的那场每行都记。

- `SPAWN #n`：插件版奇亚娜出场（参数）；学会 E 后复活写 `holding rock (W learned)`。
- `== map mode=…: walls …, bushes …, river … ==`：读到的地图（每种模式一行）。
- `W #n Grass/River/Rock (fight / a monster / after E) at (x, y): grass … rock … river …; dash … toward (x, y); Q reset (… ticks were left) / was ready; Royal Privilege ready again on k; Spot {...}`：
  每次 W（同一份模拟里她同一种元素 2 秒内只记一次）；`W NO TERRAIN`：想放 W 而身边两格内没有地形。
- `Q #n the plain line at #id: k hit (c champions), first #id`：没元素的 Q 打中英雄时；`Q #n: nobody to aim at`：Q 放出来时目标不在、身边也没有敌人（主包的 AI 对着死人或空位按的）。
- `Q2 #n River/Rock/Grass: the blade thrown d toward #id - first #id / its end in t ticks`、`Q2 BLAST #n …: k hit (c champions), first #id, r rooted, rock under half: #id at h% +x`：元素之怒（扔向英雄的那些；炸开的那行只记打中英雄或什么都没打中的）。
- `FIELD #n: grass at (x, y)…`、`FIELD END #n: an attack / Q / E / R / she left it / its time is over (… ticks were left)`：草地。
- `E #n: struck #id / MISSED #id (d away at the landing), then W`：E 落地（打英雄时）。
- `R #n at #id: the wind stops at the wall cell (cx, cy) / the map's … edge / blows its whole length after d; brush k cells; river at (x, y) / no; along the plan's line / at the target / re-aimed at another champion (planned t ticks ago to catch c, now k): #id is d off the line`：放 R（0.3.1 起后半句：风朝哪吹是怎么定的，目标离风路多远）。
- `R BOOM #n: c champions [#id 60t 1200 off, …] and k others caught; p pushed (c champions); wall k cells / the … edge, brush k cells, river yes/no`：冲击波（`no terrain reached: knock-back only` 是只击退）。
- `R TERRAIN at #id (the AI aimed at #id): the shockwave catches c champions [...]`、`R TERRAIN (on her own) …`、`R HELD: … - Q / E / an attack / a walk up instead`、`Q HELD: no element, #id is d off …`：AI 钩子（一次按键只记一行）。

## 0.3.1：锁着的 E、风沿算好的路吹、日志（2026-11-05）

11-04 的日志：`league_unlock_guard.log` 一天 40 行 GUARD 全是奇亚娜——1、2 级 E 还没学会，AI 钩子把够不着的 Q（`Q HELD`）换成 E，守卫包把这下按键改成站住，她停在原地不走过去。钩子现在和 `w_ready` 一样先问技能槽学会了没有（`slot_up`：引擎的 `is_valid_input` 不问），没学会就普攻、走过去。

R：104 次有预测（`R TERRAIN`）的 R 里 15 次谁都没打到、21 阵风对着人吹却没推到人。引擎接下按键后风到第 `r_at` - 1 tick 才放，这 15 tick 里他走开了，`launch` 重新朝他那时的位置吹，撞的墙不是算过的那面（`R TERRAIN … catches 1 [818]` → 15 tick 后 `the wind blows its whole length … no terrain reached`）。现在 AI 钩子把定下的方向记下来（`ult::remember`，60 tick 内有效），放的时候沿这条线、目标现在的位置、看得见的每个敌方英雄各算一次，取打到最多的（一样多时先定下的线），日志后半句写是怎么定的、目标离风路多远。

日志：`W NO TERRAIN` 在空地上打架时每 3 tick 一行（一场 248 行），现在同一份模拟里 2 秒一行；`the map's Some(Bottom) edge` 改成 `Bottom`；`Q #n: nobody to aim at` 补进上面的说明。

## 构建

`cargo build --release -p league_qiyana`（单独的 `league_qiyana.dll`），或者随合集包 `league_addons` 一起（`league_addons/src/lib.rs` 已登记）。
测试：`cargo test -p league_qiyana`（局势和地形挑元素、Q 的直线和环刃、伤害衰减和野怪、岩石斩杀、凌人贵气每个敌人单独算和换元素重置、
附着元素的魔法伤害、格子距离、河道斜带和地图边、各种地形最近的一点、风碰墙停下、冲击波沿墙 / 地图边 / 草丛 / 河道走、击退撞墙、
眩晕按远近、R 的 AI 挑目标和留着、没元素的 Q 等直线、参数读法、名字长度、日志条数）。
