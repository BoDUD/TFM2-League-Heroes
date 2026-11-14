# 玛尔扎哈附加包（测试版 v0.2.1）：虚空穿越、幻象跳转、虚空蜂是真的单位

主包 `league` 保持纯数据。用户选了「做：E 跳转 + 被动精确」；2026-11-14 用户：「召唤物的全做啊」。这个附加包用原生代码做主包数据做不准的三件事：

- **虚空穿越（被动）**：英雄联盟里玛尔扎哈身上有一层法术护盾：受到的伤害大幅减少、免疫控制；被非小兵的伤害打中后很快消失，
  一段时间没受到英雄伤害才回来。主包数据读不到「被谁打了」「多久没挨打」，只能做成墨菲特那样的护盾（打破后过一会儿回来）。
  附加包的被动 `league_malzahar:void`：
  - 准备好时给他挂 `league_malzahar_p_shift`：受到的伤害减少 `p_dr`%（90%）、**免疫控制**；画面是主包数据里绑的 `p_shift`；
  - 第一次被**英雄、野怪或防御塔**打中后再持续 `p_linger` tick（0.25 秒）就消失；**小兵**的伤害照样减少，但打不破它；
  - 消失后，**`p_cd` tick 内没受到英雄伤害**才重新准备好（每挨一次英雄伤害重新计时）；每条命开始时是准备好的。
- **煞星幻象的跳转**：主包数据里幻象的目标死了只能跳一次，而且晚零点几秒（数据看不到死亡，靠打标记再检查）。
  附加包里幻象每打中一个单位都会调用原生效果 `league_malzahar:vision` 记下它；目标在幻象的 `e_t` tick（4 秒）内死了，
  **立刻**跳到它倒下处 `e_jump`（40000）内最近的敌人身上：**先找英雄**，没有再找小兵、野怪，不找防御塔。
  新目标重新受到完整的幻象（`e_t` tick 内每 `e_p` tick 一段，共 `e_dmg` + `e_ap`% 法强的魔法伤害，由附加包结算），
  头上挂 `league_malzahar_e_markb`（主包数据里绑了幻象的画面）；它死了照样再跳，**没有次数限制**。
  英雄联盟里跳转还会刷新 E 的冷却；TFM2 的冷却加速 buff 会把 Q 一起刷新，所以不做。
- **虚空蜂是真的单位（v0.2.0，游戏里还没看过）**：主包里虚空虫群跟着幻象挂在目标身上 4 秒（每 0.5 秒咬一口 14 + 8% 法强），
  数据里召唤物不会走。附加包里 E 出手时目标两边各钻出一只虚空蜂（`spawn_unit`）：自己追、自己咬（每口 14 + 8% 法强，每只每秒
  一口），生命是他的 10%，可以被打死，留 8 秒。宿主给不出单位时和主包一样（见文末一节）。

数字：被动的参数写在英雄数据的 `passive.params`（`{"p_cd": 720, "p_linger": 15, "p_dr": 90, "e_t": 240, "e_p": 15,
"e_dmg": 170, "e_ap": 80, "e_jump": 40000}`），由 `make_override.py` 从 `tools/kit/build_malzahar.py` 的参数表 `P` 写入；
单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.111 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_malzahar` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_malzahar.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看玛尔扎哈的普攻和技能说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_malzahar.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Malzahar (player 2, team 0), ...`：出生（虚空穿越准备好）；
   - `SHIFT #3: struck by Ahri#14 (85), Void Shift fades in 15 ticks`：被非小兵打中，0.25 秒后消失；
   - `SHIFT #4: Void Shift spent, back after 720 ticks without champion damage` / `SHIFT #5: Void Shift ready again`；
   - `JUMP #2: caster_minion#40 fell, the vision moves to Ahri#14 (240 ticks, 13 a part)`：目标死了，幻象跳走；
   - `JUMP #6: ... fell under the vision, no enemy within 40000`：附近没有敌人，幻象结束。

## 重新生成

主包的玛尔扎哈改了以后：`python -X utf8 addons/league_malzahar/make_override.py`（先核对主包的数据和参数表一致；
`--check` 只核对不写）。虚空蜂的单位图：`python -I tools/art/unit_malzahar_voidling.py`（`--check` / `--review <目录>`）。

## 0.1.2：大招脚下的虚空区多打第一下（2026-11-06）

冥府之握脚下的虚空区（`r_zone`，每 30 tick 一次伤害，存在 300 tick）第一下晚 30 tick；现在下一 tick 打第一下，多一跳。经典 SDK 实测（2026-11-06，`trace.exe` 逐 tick 看每个区域第一次生效）：区域出现后第 `first_delay` tick 才第一次生效，写 0 等于晚整整一个周期（从飞行物落点生成的晚 `period` tick，从延迟或技能里直接生成的晚 `period - 1` tick）。改成 1 后，从落点生成的落地下一 tick 就生效，从延迟里生成的出现当 tick 就生效。主包的数据跟着改，本包的副本用 `make_override.py` 重新生成；DLL 没变。

## 虚空蜂是真的单位（v0.2.0，2026-11-14）

用户：「召唤物的全做啊 剩下的一批英雄也做了啊 都做完了装进去了再测」。萨科的幻像、安妮的提伯斯是试点；这是第二轮（公用模块 `summon.rs` 的 `Flock`：一个召唤者好几个单位）。只在附加包里，主包的数据没动；主包多一张单位图。

- 英雄联盟（wiki 现行页面）：虚空虫群召出 1 只虚空蜂（每层叠加多 1 只，最多 3 只），留 8 / 8 / 9 / 9 / 10 秒；生命 65–201、魔法伤害、攻速 0.67–0.89、射程 100、移速 400、护甲 16–50、魔抗 8–25；先咬冥府之握和幻象的目标，英雄和防御塔的普攻一下就打死它。
- 这里的数字：每口照主包（14 + 8% 法强，`make_override.py` 对照参数表 P），两只每只每秒一口（加起来是主包每 0.5 秒一口的节奏）。其余按英雄联盟的数字照他的套路换算：生命是他的 10%（65–201 对他的 580–2297）、护甲是他的 60%（16–50 对他的 18–89）、魔抗是他的 40%（8–25 对他的 30–52）、移速是他的 120%（400 对他的 335）、射程 10400（100 / 500 × 52000）、留 8 秒（英雄联盟 1 级的时间；主包挂着的 4 秒）。一直够得着时两只 8 秒 16 口，主包挂着的 8 口，按一半时间够得着和原来一样（比例是猜的）。
- 伤害类型：单位的普攻只能是物理伤害（API 的攻击没有伤害类型），所以虚空蜂咬的是**物理伤害**（英雄联盟是魔法伤害）。本来打算在引擎把虚空蜂打出的一下告诉玛尔扎哈的被动（`on_attack`，用虚空蜂的 id）时把这一下改成 0、下一 tick 由他打出同样多的魔法伤害；游戏 0.7.2 里 `on_attack` 从来不报单位的攻击（v0.2.1 那一节），这段代码留着但不会跑。
- 单位图：`tools/art/unit_malzahar_voidling.py`（2026-11-14 重画，用户：「马尔扎哈和蜘蛛的召唤物画高清点啊 现在像什么 一个不像虫子 一个不像蜘蛛 模糊不清」）用代码画的虚空虫（`tools/art/unit_draw.py`：形状按游戏像素定，1 倍和 2 倍的格子各取一次样，同一张画、硬边、深色描边）：侧面朝右，尾刺到钳子 22 游戏像素、背刺到脚底 14；四块紫色甲壳、缝里透出品红的虚空光、三根背刺，头上淡紫色护甲、品红的眼睛和嘴，一对钳子、两根触角，六条分节的腿。身体（甲壳 14 × 7）每帧只整格移动，不变大变小。idle 4 帧（钳子开合、触角抖、前腿点地、虚空光一明一暗，身体不动）、run 6 帧（三足交替）、attack 6 帧（后缩张钳 → 抬身 → 前冲两格咬下带品红火花（180 毫秒）→ 停 → 收回）、hit 2 帧、dead 8 帧（腿一软趴下 → 身下裂开虚空裂口沉进去 → 裂口合上 → 空帧）。高清帧 PPU 2，league.dll 的 `hd.rs` HEROES 登记（没有 league.dll 时画 1 倍帧，一样大）。`mod.override_info` 把单位名的图接到主包的这张图上。
- 副本（`make_override.py`）：E 出手时去掉 `league_malzahar_v_unit`、给目标挂 3 tick 的 `league_malzahar_v_ask`；幻象打中目标时挂着的虚空虫群（撕咬、画面、裂口和声音）外面套 `SwitchByBuff league_malzahar_v_unit`——他身上有这个标记就不放（有 Q 连招和没有的两份幻象都改了）。没有加 Native 节点，AI 估伤害走的还是原来那一支。
- 被动：看到 `v_ask` 就排原生效果 `league_malzahar:voidlings`，在目标两边各 14000（横在他和目标连线的两侧，主包画面里两只的位置）生成 2 个 `league_malzahar_voidling`，每只钻出来的地方放主包的裂口画面，成功了给他挂 `v_unit`（60 tick）；每只每秒记一行。
- 退路（标记不挂或去掉，数据照主包放挂着的虫群）：宿主没有 `spawn_unit`、返回失败、给的 id 5 tick 内读不成单位、单位 6 tick 内就没了、测试开关 `unit=off`。数据在幻象打中时读标记：出手后 9 tick 才放出幻象（有 Q 连招时马上放），再飞一会儿；单位最晚第 3 tick 生成。贴脸放、又有 Q 连招时，「读不成单位」可能晚于幻象打中，那一次就没有虫群。
- 玛尔扎哈先死了：虚空蜂由引擎管着接着打，到时间为止。

### 游戏里看日志

`league_malzahar.log`（虚空蜂的行 `[view …]` 每行都记，`[presim …]` 每种前 40 行、之后每 200 行一行）：

| 日志 | 说明什么 |
|---|---|
| 开头第二行 `VOIDLINGS: Void Swarm's voidlings are units ('league_malzahar_voidling', spawn_unit) - ON … Test knobs (…): none` | 这一版装上了，开关没动 |
| `VOIDLINGS ASK #n: E cast on … at (x,y): 2 voidlings asked for 14000 on either side of it` | 副本的 ask 被动读到了 |
| `VOIDLINGS SPAWN #n (the queued effect): 2 of 2 units [ids] … 'league_malzahar_voidling' for 480 ticks, attack … hp …` | `spawn_unit` 给了单位（**没有这行、而有 `SPAWN FAILED` / `NONE` / `LOST`：画面上是原来挂着的虫群**） |
| `VOIDLING #n LOOK #k: #id reads back as name … kind summon …` | 单位读回来叫什么、算哪一类、属性对不对 |
| `VOIDLING #n #k: 61 of 480 ticks, at (x,y) (walked …), hp …/…, … from its summoner; near it: …` | 每秒一行：走不走、掉不掉血、身边是谁 |
| `VOIDLING HOOK #k on_attack: entity #id (the voidling #n) -> …, damage 30: dealt as magic next tick` | 引擎把虚空蜂的一下告诉了他的被动：这一下改成魔法伤害。游戏 0.7.2 里只有 `entity #… (Malzahar)` 的行（他自己的攻击）：虚空蜂咬的是物理伤害 |
| `VOIDLING #n OVER #k: KILLED / TIMED OUT after A of 480 ticks …; its bites physical (…)` | 被打死还是到时间、给不给钱；引擎报了它的攻击时是 `N of its bites dealt as magic (on_attack named it)` |
| `VOIDLING #n WAKE #k` / `VOIDLING ORPHAN #k` | 尸体留多久；玛尔扎哈先死 |

画面上要看的：虚空蜂画不画得出来、站不站在地上、和挂着的画面一样大（17 像素宽）、钻出来时脚下的裂口、走路 / 咬 / 倒下播不播动作；同一时间没有挂着的虫群。测试开关：日志旁边放一个 `league_malzahar.cfg`（`unit=off` / `still=1` / `name=<名字>`）。

## 虚空蜂咬的是物理伤害、站稳了再接手（v0.2.1，2026-11-14）

第一批真实对局数据（游戏 0.7.2 的预模拟，`league_malzahar.log`）：

- 虚空蜂会走、会被小兵打死，可 `VOIDLING HOOK … on_attack` 的行全是 `entity #20 (Malzahar)`——他自己的攻击；虚空蜂咬的那一下引擎从来不告诉他的被动，所以「改成魔法伤害」那一段一次也没跑过（`0 of its bites dealt as magic`）。别的路也看不到：API 读不到单位在打谁、什么时候出手，靠「目标这一拍掉了多少血」去猜，要知道引擎的护甲算法、暴击、护盾和同一拍里别的伤害，猜错了就是把别人的伤害改了。所以虚空蜂咬的照实是**物理伤害**：`OVER` 行改写成 `its bites physical (no hit of it reached his on_attack, so none was made magic)`，第二行写明 `(physical: a unit's attack has no damage type)`；改成魔法伤害的代码留着，以后的宿主要是报了，它照样管用（`OVER` 行那时是 `N of its bites dealt as magic (on_attack named it)`）。英雄联盟的虚空蜂打魔法伤害：这里差一个伤害类型，按 14 + 8% 法强一口算，护甲和魔抗差不多的目标上差得不多。
- 虚空蜂在生成那一拍就被读，`LOOK` 行是 `hp 81/1 attack 1 def 1 mr 1 speed 1`：新单位生成那一拍和下一拍数字都读成 1。公用的 `Flock` 现在等它站稳才接手（萨科附加包 0.3.1 的 `summon.rs`），`VOIDLING #n LOOK` 晚一两拍，是它自己的数字。
- 测试没改（假宿主里单位一生成就站稳）。
