# 约里克附加包（`league_yorick`，v0.3.0）：真的暗灵缠身墙、坟和唤醒照英雄联盟、室女跟着他、雾行者和室女是真的单位

用户（2026-10-25）：约里克「继续接入（文字、音效、注册、扩展包）」——和克烈、瑟庄妮一样，「和英雄联盟不一样的地方都是做附加包」。
2026-11-22（0.3.0）：「之前玩掘墓我也发现没完美还原 没有那个地形框出来的技能 其他我不知道 你再核对一下」——照英雄联盟现在的约里克
（V25.07 重做后的样子）把暗灵缠身做成一圈真的墙，别的逐条核对改了。

主包的约里克是纯数据：数据造不了地形、读不到生命和「这一铲打死了谁」「室女的标记在谁身上」，召唤物不会走。这个附加包把这些做成英雄联盟的样子：

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 暗灵缠身（W，没有技能格，控制器放） | 一圈墙的画面；圈里的敌方英雄被近似地关住：两个同心区域的移速相加（圈里 +99%、墙那一圈 -99%），墙那一圈不能用位移技能，立墙时墙线上的都拉进圈里；只管英雄，冲刺、闪现挡不住 | **真的墙**（`src/wall.rs`）：只挡敌人（英雄、小兵、野怪、召唤物），约里克和队友照走；立墙时墙线上的照英雄联盟拨开（离圆心不到墙线 210/225 的拉进去，其余推出去，强制位移）；走路碰墙贴着墙滑，冲刺碰墙放回，闪现和无视地形的放过；**能打塌**：被挡住的敌方英雄按攻击间隔算打了几下，够 2 / 3 / 4 下（按等级）就在下一段画面开头塌掉 |
| 挖坟 | 临终仪式打英雄挖一座坟，打别的（小兵、野怪）**每两下**挖一座；最多 4 座，一起计时 | 打英雄照旧挖一座；打别的只有**这一铲打死了它**才挖一座；**附近别的敌人死掉，每第 N 个也挖一座**（N 按等级 8 → 2） |
| 唤醒 | 4 座就唤醒；3 座时附近有敌方英雄才唤醒；每座坟一只雾行者，挂在目标身上咬 | 3 / 4 只真的雾行者单位，自己追、自己咬、可被击杀（宿主给不出单位时和主包一样） |
| 临终仪式的回复 | 固定值 + 攻击力（数据读不到生命） | **按已损失生命**：10–76（按等级）+ 已损失生命 6–10%，打的不是英雄减半 |
| 哀伤之雾 | 打中英雄后约里克移速提高（标记在的 4 秒都算） | 约里克、雾行者、室女**朝被标记的英雄走时**移速 +18–30%（按等级）；附近的雾行者扑过去 |
| 迷雾室女 | 一个挂在约里克身上的画面，跟着他，每秒朝附近敌人放魂弹（物理），打中英雄给约里克挂标记；他下一次普攻或黑雾打中**任何**英雄时消耗，最大生命 `r_pct`% 真实伤害；他阵亡就没了 | 一个真的单位，**跟着约里克**（不自己追人：本包用强制位移让她跟在他身后），每秒朝最近的敌人放魂弹（魔法），打中英雄给**那名英雄**挂标记；他普攻或黑雾打中**有标记的那名英雄**才消耗，最大生命 2 / 2.5 / 3%（按等级）魔法伤害；带 2 / 3 / 4 只雾行者（按等级）；**亡灵大军**：她附近的敌人死掉、她手下不到 4 只时拉起一只；约里克阵亡时雾行者跟着没、她 3 秒内掉光生命 |

## 怎么接上的

`mod.override_info` 把主包的约里克换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_yorick.py` 的 `native=1` 生成，
0.3.0 起副本要改的地方都在 build_yorick.py 里，make_override.py 只核对和写文字）。`passive` 是本包的 `league_yorick:shepherd`，
参数 `r_pct g_t w_r w_half w_t w_delay` 来自主包参数表 P（`w_t` 是 P 的 `w_tn`：附加包的墙按英雄联盟立 4 秒，能打塌）：

- **墙**：副本的 W 落点那名英雄挂 3 tick 的 `league_yorick_w_ask`（本包记下它站的地方当圆心），`w_delay` tick 后立墙时约里克挂
  `league_yorick_w_up`（本包立墙）；墙塌了本包给他挂 `league_yorick_w_down`，副本的画面（每 30 tick 一段）下一段放塌掉的。
- **坟**：这一铲挂 `league_yorick_q_win`；它还在时被他打死的小兵 / 野怪挖一座（`on_unit_kill`）；被动每 tick 看他附近的敌人谁死了，
  每第 N 个挖一座；坟是 `league_yorick_g1..g4`，一起挂一起计时（和数据一样，技能栏的坟数是最高那一级）。
- **回复**：这一铲挂 `league_yorick_q_hl`（数据自己的回复去掉了），本包两 tick 后回复（打英雄时孪生弹挂的 `league_yorick_q_ch` 在）。
- **唤醒**：出手时目标挂 `league_yorick_k_ask`（3 座）/ `league_yorick_k_ask4`（4 座）；本包生成雾行者单位、给约里克挂 `k_unit`，
  数据落地时看到它就不放挂着的雾行者。
- **黑雾**：打中的英雄挂 `league_yorick_e_ask`（雾行者扑过去）和 3 tick 的 `league_yorick_hit`（室女的标记在它身上就消耗）；
  英雄身上的 `league_yorick_e_mark` 是数据挂的标记，本包按它给朝它走的约里克 / 雾行者 / 室女挂 3 tick 的 `league_yorick_e_ms`。
- **室女**：出手时目标挂 `league_yorick_m_ask`；本包生成她和护卫、挂 `m_unit`（数据看到就不放挂着的室女、魂弹、两只雾行者）；
  她的魂弹是 `spawn_projectile`（画面是数据的 `league_yorick_r_bolt`），打中后的效果 `league_yorick:bolt`；标记 `league_yorick_r_mkv`
  （画面在数据的 view_buffs 里）；普攻在 `r_on` 时给打中的英雄挂 3 tick 的 `league_yorick_hit`。
- 普攻、临终仪式、哀伤之雾、海屿悼词的说明换成附加包自己的文字（`description.league_yorick.*`），游戏里看说明就知道副本有没有生效。

计数都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test -p league_yorick`：单元测试（`src/tests.rs`：参数、按等级的数字、墙的几何、墙只挡敌人 / 拨开 /
  闪现放过 / 打塌、坟和附近死亡、3 / 4 只唤醒、回复、朝标记加速、室女跟着他 / 魂弹 / 标记消耗、亡灵大军、阵亡后雾行者没和室女
  消散、日志）和 `tests/wiring.rs`（走真实的导出入口）。
- 主包的约里克改了以后重新跑 `python addons/league_yorick/make_override.py`（它先核对主包的 `league_yorick.data_champion` 和参数表
  一致、`src/lib.rs` 的默认参数和常量和 P、单位图一致、本包读写的名字副本里都有；`--check` 只核对不写）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yorick.log`，见下面「游戏里看日志（0.3.0）」。

## 雾行者和迷雾少女是真的单位（v0.2.0，2026-11-14）

用户：「召唤物的全做啊 剩下的一批英雄也做了啊 都做完了装进去了再测」。萨科的幻像、安妮的提伯斯是试点；约里克是第二轮的第一个，一个召唤者同时有好几个单位（公用模块 `summon.rs` 的 `Flock`）。只在附加包里，主包的数据没动；主包多两张单位图。

- 英雄联盟（wiki 现行页面）：雾行者生命 100–331（+15% 额外生命）、攻击 15–113、没有护甲魔抗、射程 125、移速 325（约里克附近 +60），最多 4 只，没有时间限制、打死为止；被黑雾标记的英雄附近 1500 内的雾行者扑过去咬一口。迷雾少女生命 1050–3700、每秒一击（50 / 75 / 100 + 30% 额外攻击力的魔法伤害）、射程 600、护甲魔抗 30–100，带 2 / 3 / 4 只雾行者，打死为止；约里克普攻她的目标多造成最大生命 2–3% 的伤害。
- 这里的数字：每口 / 每下的伤害、几只、多久一下照主包（9 + 13% 攻击力每秒一口、3 只；20 + 45% 攻击力每秒一下、带 2 只），`make_override.py` 逐个对照主包的参数表，主包改了它就停下来。其余按英雄联盟的数字照约里克的套路换算：雾行者生命是他的 15%（英雄联盟 100–331 对他的 650–2588）、射程 18000（125 / 175 × 25000）、移速和他一样；室女生命是他的 120%（1050–3700 对他的 1220–2588）、护甲和魔抗是他护甲的 85%（30–100 对他的 36–112）、移速和他一样。时间：英雄联盟里两者都打死为止，主包挂着的是 6 秒 / 10 秒；单位要自己走过去、会被打死，所以雾行者 10 秒、室女 15 秒（一直够得着时 30 口 / 15 下，原来 18 口 / 10 下；按 60% / 三分之二的时间够得着，和原来差不多——这两个比例是猜的）。室女的远程攻击没做：单位的攻击没有飞行物，600 射程会让她在 86000 外打人、什么都看不见，所以按他的射程 25000 近身抓。
- 单位图：`tools/art/unit_yorick_summons.py` 用主包特效图里它们自己的 1 倍帧拼（`--check` 核对，`--preview` 放大 8 倍看）：雾行者是 `k_swarm` 里左边那只（两只左右镜像，脚本核对），idle 四帧蹲伏、run 蹲伏和扑出去抬高一两行交替、attack 蹲伏 → 人立 → 张嘴扑咬（170 毫秒）→ 落地、hit 往后一格、dead 是 `k_spawn` 倒放（缩回土里）；室女是 `r_maiden`，往下挪 11 行站到地面，idle 六帧飘、run 手放下的两帧上下一行、attack 举手 → 抓下（180 毫秒）、dead 是 `r_spawn` 倒放（沉回雾里）。都是 1 倍帧，和今天画面上一样大，不用在 league.dll 里登记。`mod.override_info` 把两个单位名的图接到主包的这两张图上。
- 副本（`make_override.py` 在 `build_yorick.py --native` 的结果上改）：唤醒出手时（坟满、换成唤醒动作的那一支）去掉 `league_yorick_k_unit`、给目标挂 3 tick 的 `league_yorick_k_ask`；这一铲落地时挂在目标身上的那三只外面套 `SwitchByBuff league_yorick_k_unit`——约里克身上有这个标记就不放。黑雾的英雄分身给打中的英雄挂 `league_yorick_e_ask`。大招出手时去掉 `league_yorick_m_unit`、给目标挂 `league_yorick_m_ask`；室女升起时挂着的室女、她的爪子和她的两只雾行者外面套 `SwitchByBuff league_yorick_m_unit`。普攻和技能里的控制器（Q、E 在普攻和大招里各有一份）一起改了。没有加 Native 节点，AI 估伤害走的还是原来那一支。
- 被动：看到 `k_ask` 就排原生效果 `league_yorick:walkers`，在目标周围 12000 生成 3 个 `league_yorick_walker`（谁都不站在约里克和目标中间），成功了给约里克挂 `k_unit`（60 tick）；看到 `m_ask` 就排 `league_yorick:maiden`，在目标身后 11000 生成 `league_yorick_maiden`、她周围 12000 生成 2 个雾行者，成功了挂 `m_unit`。每个单位每秒记一行。室女读成单位时把约里克的 `league_yorick_r_on`（Q 冷却减半、普攻加伤）和目标身上的 `league_yorick_maiden` 改成跟着她的时间；她被打死就一起去掉。看到 `e_ask` 就让离那个英雄 118000 以内的雾行者单位跳到他身边 9000 处（`entity_set_pos`），扑咬（20 + 30% 攻击力）由约里克打一次。
- 退路（标记不挂或去掉，数据照主包放挂着的）：宿主没有 `spawn_unit` 这个槽、返回失败、给的 id 5 tick 内读不成单位、单位 6 tick 内就没了、测试开关 `unit=off`。数据在出手后约 15 tick（唤醒）/ 17 tick（室女）读标记，单位最晚第 3 tick 生成，读不成单位第 12 tick 前就知道。
- 约里克先死了：单位由引擎管着接着打，到时间为止（没有让单位消失的接口；英雄联盟里室女会在 3 秒内消失）。

### 游戏里看日志

`league_yorick.log`（`[view …]` 是你看的那场，每行都记；`[presim …]` 每种行前 40 行、之后每 200 行一行）：

| 日志 | 说明什么 |
|---|---|
| 开头第二行 `UNITS: the Mist Walkers ('league_yorick_walker') and the Maiden of the Mist ('league_yorick_maiden') are units (spawn_unit) - ON … Test knobs (…): none` | 这一版装上了，开关没动 |
| `WALKERS ASK #n: the Awakening on #7 … at (x,y): 3 walkers asked for round it` / `MAIDEN ASK #n: Eulogy of the Isles on #7 …` | 副本的 ask 被动读到了（行末 `(held N tick(s) …)`：压着等了几拍才发） |
| `MAIDEN HELD #k: … - the walkers' ask of t=… still waits for its units (1 held): it goes out once that one is answered` / `WALKERS HELD #k: …` | 雾行者那本账还有要在等，这个要先压着（见下面 v0.2.1）；`HELD DROPPED` = 压太久没发，画面上是原来挂着的 |
| `WALKERS SPAWN #n (the queued effect): 3 of 3 units [ids] … 'league_yorick_walker' for 600 ticks, attack … hp …` / `MAIDEN SPAWN #n …; her escort: 2 of 2 walkers [ids]` | `spawn_unit` 给了单位（**没有这行、而有 `SPAWN FAILED` / `NONE` / `LOST`：画面上是原来挂着的**） |
| `WALKER #n LOOK #k (the Awakening's / the Maiden's escort): #id reads back as name … kind summon …` / `MAIDEN #n LOOK #k: …; league_yorick_r_on on Yorick and league_yorick_maiden on #7 set for her 899 ticks` | 单位读回来叫什么、算哪一类、属性对不对；室女的时间接上了没有 |
| `MAIDEN #n DRESS #k: a tick on, league_yorick_r_on is on Yorick, league_yorick_maiden is on #7` | 标记真的挂上了（`is NOT` = 没挂上） |
| `WALKER #n #k: 61 of 600 ticks, at (x,y) (walked …), hp …/… (…), … from its summoner; near it: …` / `MAIDEN #n #k: …` | 每秒一行：走不走、掉不掉血、身边是谁、约里克的伤害统计涨没涨 |
| `WALKERS LEAP #k: the mist struck #7 … : 3 walkers leapt [ids] (3 moved by entity_set_pos), 0 out of reach; the pounce 65 physical, once` | 黑雾的扑咬；`the rest REFUSED` = `entity_set_pos` 对召唤物不起作用 |
| `WALKER #n OVER #k (…): KILLED / TIMED OUT after A of 600 ticks …; the enemy players in its last tick: …` / `MAIDEN #n OVER #k: … - league_yorick_r_on and the mark on #7 taken off` | 被打死还是到时间，给不给钱；室女被打死时加伤跟着没了 |
| `WALKER #n WAKE #k` / `MAIDEN #n WAKE #k` | 尸体留多久、死后几 tick 敌方的金币 |
| `HOOK #k on_attack: entity #id (the walker #n / the Maiden #n / Yorick) -> …` | 单位打人时引擎告不告诉约里克的被动、用谁的 id |
| `ORPHAN #k: Yorick died - N fight on unwatched until their time` | 约里克先死 |

画面上要看的：雾行者和室女画不画得出来、站不站在地上、和挂着的画面一样大（雾行者 19 像素宽、室女 49 像素高）、走路 / 攻击 / 倒下播不播动作；同一时间没有挂着的雾行者和室女。`league.log` 里看有没有新的 `DIVERGE`。

测试开关：日志旁边放一个 `league_yorick.cfg`（`summon.rs`）：`unit=off`（回到挂着的）、`still=1`（移速 1）、`name=<名字>`（两种单位都换成这个名字，只在测试时用）。

## 雾行者和室女站稳了再接手（v0.2.1，2026-11-14）

第一批真实对局数据（游戏 0.7.2 的预模拟）：新单位生成那一拍和下一拍，最大生命、攻击、防御、移速都读成 1，那时设的生命会被盖掉（悟空的分身生成后一拍读到 `hp 1851/1 attack 1 def 1 mr 1 speed 1`；玛尔扎哈的虚空蜂在生成那一拍就被读成 `hp 81/1 …`）。公用的 `Flock`（萨科附加包 0.3.1 的 `summon.rs`）现在等单位站稳（最大生命读出来）才接手：`WALKER #n LOOK` / `MAIDEN #n LOOK` 晚一两拍、是它们自己的数字（5 次还没站稳就照样接手，行末写 `(its health cap still reads 1 after 5 looks)`）。室女的 `r_on` 和她目标身上的标记在接手时挂，所以也晚一两拍。代码没改，测试没改（假宿主里单位一生成就站稳）。

**雾行者一次只等一个要**（同一版，用户：「这个要修」）：唤醒的雾行者和室女的护卫记在同一本账里，一拍交接来的单位都算最早那个还在等的要的。所以唤醒的雾行者没生成出来、它还在等（4 拍）时 R 又要了护卫，护卫会被记成唤醒的（`Awake`、600 拍、出生在 Q 那一拍）：账上提前 300 拍算它没了，黑雾也不再让它扑；反过来也一样。现在雾行者那本账还有要在等时，新的 Q / R 的要先压着（`HELD`），等前一个有了结果（单位到了，或等满时间作罢）再发，目标那时站在哪就在哪生成。正常 Q 和 R 隔好几秒，压不到；压着的一般 5 拍内发出，数据在出手后 14 / 16 拍读单位的标记，来得及；超过 10 拍还发不出就放弃（`HELD DROPPED`），画面上是原来挂着的。测试 `an_ask_made_while_the_walkers_last_one_waits_keeps_its_own_units`（两个方向都测）。

## 照英雄联盟现在的约里克（v0.3.0，2026-11-22）

用户：「之前玩掘墓我也发现没完美还原 没有那个地形框出来的技能 其他我不知道 你再核对一下」。主包和副本一起改（主包的部分见
`tools/kit/build_yorick.py` 的说明和 `docs/heroes/league_yorick.md` 的开发记录），本包新加：

- **真的墙**（`src/wall.rs`）：圆心是副本的 W 落点那名英雄站的地方，墙线半径 `w_r`（30000，画面上 30 格），圈里的单位中心离圆心不超过
  `w_r - w_half`（20000），圈外的不少于 `w_r + w_half`（40000）。只挡约里克的敌人。立墙那一 tick 墙线上的敌人：离圆心不到墙线
  210 / 225 的拉进圈里，其余推出去（4 tick 的强制位移，画面上连着动；免控的、无视地形的不拨）。之后每 tick：走路碰墙的沿圆心方向
  放回墙面（贴着墙滑）、一 tick 走 2200 以上（冲刺）碰墙的放回上一 tick 的位置、一 tick 挪 15000 以上（闪现、飞越）的放过去、
  身上有无视地形 buff 的穿过去（嘉文四世、艾尼维亚附加包的规则）。**打塌**：被挡住的敌方英雄每一 tick 算打了 1 / 攻击间隔
  （最多按 30 tick 一下）下，加起来够 2（1–4 级）/ 3（5–8 级）/ 4（9 级起）下墙就塌（一个英雄一直顶着墙：1–2 秒），塌在数据下一段画面
  的开头。墙最多立 `w_t`（4 秒）。
  墙不是单位：英雄联盟里防御塔一下就塌，这里防御塔不打墙，没做。
- **坟**：最多 4 座；附近（60000 内）别的敌人死掉，每第 N 个挖一座，N = 8 − 6 ×（等级 − 1）/ 11（1 级 8 个、12 级 2 个）；
  这一铲打死的不重复算。
- **唤醒**：3 / 4 座坟出 3 / 4 只雾行者单位（副本挂 `k_ask` / `k_ask4`）。
- **临终仪式的回复**：10 + 6 ×（等级 − 1）+ 已损失生命的 6–10%（按等级线性），打的不是英雄减半；用 `heal`，画面上有绿字。
- **朝被标记的英雄加速**：黑雾的标记在、离它 90000 以内，这一 tick 的位移和朝它的方向夹角小于 60 度，就挂 3 tick 的移速 +18–30%
  （按等级），约里克、雾行者、室女都算。
- **室女**：生成在 R 的目标身后（和 0.2.x 一样），移速 1、自己的爪子够不着人（射程 1）：本包让她离她该在的位置（约里克身后 15000，
  在她那一侧）超过 15000 时用强制位移跟过去（离他 80000 以上三倍速）；每 60 tick 朝她 40000 以内最近的敌方英雄（没有就打最近的
  别的敌人，看得见的）放一道魂弹，打中造成 20 + 45% 攻击力魔法伤害，英雄挂 240 tick 她的标记。约里克的普攻或黑雾打中有标记的
  英雄：最大生命 2%（R 1 级：5–7 级）/ 2.5%（8–10 级）/ 3%（11 级起）魔法伤害，标记消耗。带的雾行者 2 / 3 / 4 只（同样按等级）。
  亡灵大军：她 40000 以内的敌人死掉、她手下的雾行者不到 4 只、她还剩一秒以上时，从尸体上拉起一只（活到她的时间）。约里克阵亡时：
  雾行者生命设成 0；室女分 6 步、每步 30 tick 掉生命，最后一步设成 0，再下一步还活着就放逐到时间（`entity_set_hp` 设成 0 在游戏里
  死不死还没看过）。

### 游戏里看日志（0.3.0）

`league_yorick.log`（`[view …]` 是你看的那场，每行都记；`[presim …]` 每种行前 40 行、之后每 200 行一行）。开头第一行
`=== league_yorick v0.3.0 (graves from kills and deaths near him, the real Dark Procession wall, …` 说明这一版装上了。

| 日志 | 说明什么 |
|---|---|
| `WALL ASK #k: Dark Procession lands under #id … at (x,y) - the ring rises in 45 ticks` | 副本的 W 落地了，圆心记下 |
| `WALL #k (wall n): ring at (x,y) line 30000 (inside within 20000, outside beyond 40000), 240 ticks; a enemies inside, b pulled in, c pushed out` | 墙立起来了：圆心、半径、时长、立墙时圈里几个、拨了几个 |
| `WALL? #k: w_up rose but no w_ask was seen …` | 数据立墙了，本包没找到圆心（应该不出现） |
| `PUSHED #k (wall n): <单位> IN / OUT on the wall line D from the centre -> (x,y) (4 ticks forced move…)` | 立墙时站在墙线上的被拨进 / 拨出 |
| `KEPT IN #k` / `KEPT OUT #k (wall n): <单位> held at (x,y) (D from the centre)` | 墙挡住了谁（一道墙一个单位一行）：圈里的出不去 / 圈外的进不来 |
| `LEAPT IN/OUT #k` / `THROUGH IN/OUT #k` | 闪现、飞越过墙 / 无视地形穿墙，放过 |
| `BROKEN #k (wall n): the enemy champions it held struck it X times (N needed at level L) - it falls at t=… ` | 墙被打塌 |
| `WALL DOWN #k (wall n) at (x,y) after T ticks[ (broken, struck X times)]: held U units (C champions), … ticks in all, the longest …; K crossed it` | 墙倒了，一共挡了多少 |
| `GRAVE #k: <单位> #id died to Last Rites - n grave(s) now` / `GRAVE #k: a unit / the champion #id died near him, the Nth death since the last such grave (level L) - …` | 挖坟：临终仪式打死的 / 附近每第 N 个死亡 |
| `HEAL #k: Last Rites on a champion / on a unit (half) - A (hp/max health, level L)` | 临终仪式按已损失生命回复了多少 |
| `WALKERS ASK #k: the Awakening on #id …: 3 / 4 walkers asked for round it` | 唤醒几只 |
| `MAIDEN #n FOLLOW #k: D off her spot … - a forced move of T ticks` | 室女跟上约里克 |
| `MAIDEN #n BOLT #k: at #id …` / `BOLT HIT #k: #id … took D magic; her mark on it for 240 ticks` | 室女放魂弹、打中、挂标记（`spawn_projectile REFUSED` = 宿主不给飞行物，伤害当场算） |
| `MARK SPENT #k: the Maiden's mark on #id … - D magic (P per mille of its max health, level L)` | 标记被约里克的普攻或黑雾消耗 |
| `RAISE ASK #k` / `RAISED #k: a walker from the body at (x,y) (the Maiden's army of the dead): unit #id for T ticks` | 亡灵大军拉起一只 |
| `ORPHAN #k: Yorick died - W walker(s): health set to 0 for G; M Maiden: F fade steps queued` / `MAIDEN FADE #k: step s of 6 - …` | 约里克阵亡，雾行者没、室女消散（`entity_set_hp REFUSED` / `banished` 说明游戏里这条路不通） |

画面上要看的：墙环（18 个小鬼站在一圈地缝上）立在 W 落点、把人框在里面，圈里的人走到墙边停住、贴着墙滑；墙塌的时候画面也塌；
室女浮在约里克身后上方跟着他走，魂弹从她那里飞出去，被打中的英雄头顶有紫圈。
