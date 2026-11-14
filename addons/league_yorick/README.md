# 约里克附加包（`league_yorick`，v0.2.0）：坟照英雄联盟挖、雾行者和室女是真的单位

用户（2026-10-25）：约里克「继续接入（文字、音效、注册、扩展包）」——和克烈、瑟庄妮一样，「和英雄联盟不一样的地方都是做附加包」。

主包的约里克是纯数据：数据读不到「这一铲打死了谁」，也读不到「室女跟着谁」，所以主包里有两处只能近似。这个附加包把它们做成英雄联盟的样子：

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 挖坟 | 临终仪式打英雄挖一座坟，打别的（小兵、野怪）**每两下**挖一座 | 打英雄照旧挖一座；打别的只有**这一铲打死了它**才挖一座（英雄联盟：击杀或英雄、大型野怪） |
| 室女的加伤 | 室女在场时，约里克普攻**任何**敌方英雄都额外造成最大生命 `r_pct`% 真实伤害 | 只有普攻**室女跟着的那个英雄**才加伤 |
| 唤醒的雾行者（v0.2.0，游戏里还没看过） | 画面和伤害挂在目标身上 6 秒：3 只每秒各咬一口（9 + 13% 攻击力），目标死了就散 | 3 个真的单位，从目标身边冒出来：自己追、自己咬（每口 9 + 13% 攻击力，每秒一口），生命是约里克的 15%、没有护甲魔抗，可以被打死，留 10 秒；黑雾打中英雄时，离他 118000 以内的雾行者跳到他身边（扑咬 20 + 30% 攻击力，打一次）。宿主给不出单位时和主包一样 |
| 迷雾室女（v0.2.0，游戏里还没看过） | 画面和伤害挂在目标身后 10 秒：每秒抓一下（20 + 45% 攻击力），带 2 只挂着的雾行者 | 一个真的单位，出现在目标身后，带 2 只雾行者单位：自己追、自己抓（每下 20 + 45% 攻击力，每秒一下），生命是约里克的 120%、护甲和魔抗是他护甲的 85%，可以被打死，留 15 秒；她站着的时候约里克的 Q 冷却减半、普攻她的目标加伤，她被打死就没了。宿主给不出单位时和主包一样 |

灵魂墙（唤醒时的定身）和黑雾本身两边一样。

## 怎么接上的

`mod.override_info` 把主包的约里克换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_yorick.py` 的 `native=1` 生成）：

- 临终仪式那一铲给约里克挂几拍（`q_win`）`league_yorick_q_win`，不再有「每两下」的规则（0.1.1：和这一铲同一拍挂上；0.1.0 晚两拍才挂，追踪的那一铲下一拍就落地打死了小兵，2026-11-03 夜里的日志 6 条命一座坟都没挖）；`passive` 是本包的 `league_yorick:shepherd`，参数 `r_pct g_t` 来自主包参数表 P：`q_win` 还在时每有一个小兵或野怪被他打死（`on_unit_kill`），就照数据的阶梯给他挂下一座坟（`league_yorick_g1` → `g2` → `g3`，各 `g_t` 拍，满了不再加）；
- 大招给室女的目标挂 `league_yorick_maiden`（大招持续时间），室女在场时普攻打中英雄给它挂 3 拍 `league_yorick_hit`；本包每拍看同时有这两个的敌方英雄，造成它最大生命 `r_pct`% 的真实伤害（`deal_damage_typed`，`Fixed`），然后摘掉 `hit`；
- 普攻（牧魂人写在里面）和海屿悼词的说明换成附加包自己的文字（`description.league_yorick.attack` / `.ult`），游戏里看说明就知道副本有没有生效。

计数都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_yorick`：单元测试（参数、坟墓阶梯、室女加伤的数、名字和数据一致、副本的每一铲在出手那一拍就挂上 `q_win`）。
- 主包的约里克改了以后重新跑 `python addons/league_yorick/make_override.py`（它先核对主包的 `league_yorick.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致；`--check` 只核对不写）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yorick.log`：`SPAWN`、打死单位挖坟 `GRAVE`、室女目标加伤 `MAIDEN`。

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
| `WALKERS ASK #n: the Awakening on #7 … at (x,y): 3 walkers asked for round it` / `MAIDEN ASK #n: Eulogy of the Isles on #7 …` | 副本的 ask 被动读到了 |
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
