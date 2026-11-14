# 纳亚菲利附加包（测试版 v0.2.1，可选）：斩杀、再扑、聪明开大、狗群是真的单位

**不装这个附加包，主包里的纳亚菲利也是完整的**：普攻和被动的狗群撕咬、Q 暗裔犬牙（两把匕首、流血、狗群扑上英雄）、E 剔骨本能、
大招（暴吼起手 + 猎狗血性飞扑、参与击杀后再扑一次）和连招 R → Q → 第二把匕首 → E 都在主包数据里。主包是纯数据：**读不到目标的生命**
（英雄联盟第二把匕首按目标已损失的生命加伤），再扑用佛耶戈的击杀窗口（**一个窗口只认最后一个阵亡的**），**AI 只要射程里有英雄就开大**，
暴吼时画面上还是两只狗。这个附加包用原生代码把这四件事做成英雄联盟的样子（用户 2026-10-21「做附加包啊 4也做」）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 第二把匕首 | 固定伤害 | 目标每损失 1% 生命多 1% 伤害（空血时翻倍，英雄联盟的 ExecuteMultiplier 2） |
| 再扑 | 扑中的英雄 7 秒内阵亡就能再扑一次（只看那一个） | 扑中后 7 秒内**她参与的任何一次英雄击杀**（击杀或助攻）都让大招就绪、再扑一次（一次大招只给一次） |
| 开大 | 游戏 AI 射程里有英雄就开 | 只在**扑得死**（飞扑 + 两把匕首 + 一半流血 + 剔骨 + 狗咬、按护甲算，打得穿生命和护盾）、**有队友一起打**（目标生命 60% 以下、旁边有我方英雄）或**团战**（她身边两名以上我方英雄、射程里两名以上敌方英雄）时开，扑最该扑的那个；不值得时 AI 想开大就改成普攻原目标；再扑时扑射程里生命最少的 |
| 狗群 | 两只伙伴画在她自己的帧里，一直两只；她每次普攻和技能命中时狗群一起撕咬（8 + 12% 攻击力） | v0.2.0（游戏里还没看过）：两只伙伴是真的单位，跟在她身后自己追咬（每只每口 4 + 6% 攻击力，节奏和她的普攻一样），生命是她的 13%，可以被打死，死了 15 秒后再来；暴吼时再来两只，留到暴吼结束；她阵亡时一起消失（放逐到时间结束）。这期间她的动作换成图里没有狗的 `solo_*` 版本，数据里的狗群撕咬不再放。宿主给不出单位时照 v0.1：画在她帧里、暴吼时四只 |

## 怎么做的

- `mod.override_info` 把主包的纳亚菲利换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_naafiri.py` 的 `native=1` 生成，
  主包的纳亚菲利改了就重跑；它也核对 `src/lib.rs` 里 AI 算爆发用的常量和参数表 P 一样）：第二把匕首的伤害换成本包的 `league_naafiri:q2`，
  大招落地不开击杀窗口、只挂 `league_naafiri_r_armed`（7 秒），被动是本包的 `league_naafiri:pack`（数字在 `passive.params`）；
  Q 和大招的说明开头加【附加包】。
- **斩杀**：`league_naafiri:q2` 读第二把匕首打中的单位的生命，按 `q2_dmg` + `q2_ratio`% 攻击力 × (1 + 已损失生命%) 造成物理伤害（`deal_damage`，过护甲）。
- **再扑**：被动的 `on_kill`（死的是英雄）和 `on_assist` 时，身上有 `r_armed` 就去掉它、挂主包的 `league_naafiri_r_again`（12 秒，数据读它：
  下一次大招不带暴吼、带护盾），大招冷却清零（2 tick 的 `ult_cooldown_mult` + 0.6.4 起的 `entity_reduce_cooldown`），播主包的 `r_reset` 和音效。
- **开大**：玩家输入 AI 钩子（优先级 110，在 league_ult_press 之后），自己按之前先看大招解锁和冷却（league_addons 的规矩），被控时不管。
- **狗群**：照纳尔的整身巨型，`game_places::hook::add` 的显示钩子：名字是 `league_naafiri`、身上有 `league_naafiri_pack4` 的画面实体，
  正在播的 idle / run / attack / hit / dead / skill / skill2 / ult / ult_b 换成 `p4_*`；阵亡时按倒下前的狗群画。找不到显示槽时什么都不做。
  附加包没有在单位旁边单独画一个跟着跑的精灵的接口，所以狗群是画进她自己帧里的。

## 在游戏里测

1. 主包（League of Legends Heroes 0.187.0 以上）要装着并启用；本包随附加包合集 `league_addons` 一起装，或单独装。
2. 看日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_naafiri.log`：`SPAWN`（她出场和参数；0.1.2，2026-11-05：参数只写一局的第一次出场，重生写 `SPAWN #n ... again`，11-04 的日志 146 行重生各带一份参数表）、`Q2 #…`（第二把匕首的斩杀）、
   `R POUNCE` / `R HELD`（开大 / 不开）、`RECAST`（参与击杀后再扑）、`FOUR hounds` / `two hounds`（显示钩子换了几次）。

## 游戏 0.6.5（0.1.1）

回城时（回城引导中没命令的 tick 也算）不自己开大；抓人、团战的扑击不朝 AI 正在远离的人扑，也不扑敌方塔 75000 内生命 25% 以上的人；斩杀和击杀后的再扑照旧（`league_ult_press` 0.5.0 的规则，0.6.5 的官方 AI 自己决定回城、撤退、越塔）。

## 狗群是真的单位（v0.2.0，2026-11-14）

用户：「召唤物的全做啊 剩下的一批英雄也做了啊 都做完了装进去了再测」。这是召唤物第二轮（公用模块 `summon.rs` 的 `Flock`：一个召唤者好几个单位）。附加包的代码 + 主包两处图：她的图多一套没有狗的 `solo_*`，多一张伙伴的单位图。

- 英雄联盟（wiki 现行页面）：伙伴（按等级 2–5 只）跟着她、咬她打的目标，生命 80–336、攻击 10–21 + 4% 额外攻击力、攻速和移速跟她一样、护甲魔抗 0–35，能被打死，被动冷却（30–10 秒）结束再来，和她一起阵亡；群狼之召多来 2 只，留到这次狩猎结束。
- 这里：两只伙伴（主包画的数量），每只每口 4 + 6% 攻击力（主包狗群一口 8 + 12% 的一半，两只加起来照旧），节奏是她的普攻间隔 58 tick、射程 23000（和她一样），生命是她的 13%（80–336 对她的 610–2395）、护甲魔抗是她的 30%（0–35 对她的 28–108）、移速和她一样；每只活 60 秒、到时间马上换一只新的（英雄联盟里没有时间，只是这里不能让单位一直活下去），被打死的 15 秒后再来；暴吼（`league_naafiri_pack4`）挂上时再来两只，留 300 tick（暴吼的时间）。`make_override.py` 对照参数表和单位图的出手时刻（420 毫秒，第 170 毫秒咬下）。
- 她：有伙伴单位以后身上一直挂 `league_naafiri_solo`（每 tick 续 30 tick）。副本的数据读它：每一口狗群撕咬（每次命中的那对追踪弹 `pk_c` / `pk_m`，普攻、Q、E、大招里一共 9 对）和 Q 打中英雄时扑上去挂着的那一套（`q_leap`：撕咬、画面、扑上去）外面都套 `SwitchByBuff league_naafiri_solo`——有就不放。显示钩子读到它，把她正在播的动作换成 `solo_*`（暴吼时也是，多来的两只也是单位）；她阵亡时记住的是 solo，尸体上不画狗。
- 她阵亡：伙伴被放逐到它们的时间结束（`entity_banish`：看不见、打不到、不能动——没有让单位消失的接口），记录作废；她复活时马上来两只新的。
- 退路（不挂 `solo`，照 v0.1 画在她帧里、数据照主包咬）：宿主没有 `spawn_unit`、返回失败、给的 id 读不成单位、单位一出来就没了、测试开关 `unit=off`；一只都没来就 15 秒后再试一次，不会每 tick 都要。
- 图：`tools/art/rig_naafiri.py` 多出 `solo_*`（每个动作同样的姿势、不画伙伴），整条流水线（rig → ppu_restyle → ppu_hd → hero_reels，`tools/art/hero_reels.json` 给 solo_idle 和 idle 一样的小动作）重跑后原来的 63 个标签逐帧、逐个时长没变，多了 30 个（solo_* 和它们的 hd_ / lo_、solo_idle_base）；图集 2031×2146 → 2041×2780。伙伴的单位图 `league_naafiri_packmate`（`tools/art/unit_naafiri_packmate.py`）：她 rig 里伙伴自己的造型（`hd/pack.png`）和姿势（`p_run1-4`、`p_bite`），按她 rig 摆伙伴的办法放到画布上，再按她的帧那样缩到 1 倍（`Rig.finish`、`one_of`、补描边）：idle 8 帧呼吸、run 4 帧、attack 5 帧（站 → 跃起 → 咬下 → 停 → 站）、hit 2 帧、dead 2 帧（一闪就没）。1 倍帧，和画在她帧里的一样大；要和她一样清楚得在 league.dll 里登记一行并加 hd_ 帧（现在没有）。`mod.override_info` 把单位名的图接到主包的这张图上。
- league.dll 要把她新的 `.fanim` 编进去（`hd.rs` 用 `include_str!` 读她的标签），装的时候要带新的 league.dll。

### 游戏里看日志

`league_naafiri.log`（伙伴的行 `[view …]` 每行都记，`[presim …]` 每种前 40 行、之后每 200 行一行）：

| 日志 | 说明什么 |
|---|---|
| 开头 `HOUNDS: her packmates are units ('league_naafiri_packmate', spawn_unit) - ON … Test knobs (…): none` | 这一版装上了，开关没动 |
| `HOUND ASK #n: 2 of her pack at (x,y) (x,y) (14000 behind her)`（0.2.1 起一批一行） / `HOUND SPAWN #n (her pack, the queued effect): unit #id …` | 她出生、伙伴被打死后、暴吼时要伙伴；`spawn_unit` 给了单位（**`SPAWN FAILED` / `NONE` / `LOST`：画面上还是画在她帧里的两只**） |
| `HOUND SOLO ON: her packmates are units …` / `HOUND SOLO OFF: …` | 她换成没有狗的帧、数据不再咬（OFF：回到画在她帧里） |
| `HOUND #n LOOK #k (her pack / the call): #id reads back as …` | 单位读回来叫什么、属性对不对 |
| `HOUND #n #k: 61 of 3600 ticks, at (x,y) (walked …), hp …, … from its summoner; near it: …` | 每秒一行：跟不跟她、咬谁、掉不掉血 |
| `HOUND #n OVER #k (her pack): KILLED … - another comes in 900 ticks` / `TIMED OUT … - another takes its place now` | 被打死 / 到时间 |
| `HOUND BANISH #k: Naafiri died - her packmates go with her: #1 (unit #id, N ticks) banished` | 她阵亡时伙伴消失（`REFUSED` = 放逐对召唤物不起作用，它们会接着打到时间） |
| `HOUND HOOK #k on_attack: entity #id (the packmate #n / Naafiri) -> …` | 伙伴打人时引擎告不告诉她的被动 |
| 显示钩子的行 `world … Naafiri #…: her solo frames (her packmates are units) (playing …)` | 画面上她换成了 solo 帧 |

画面上要看的：她身边不再有画上去的两只狗、两只伙伴单位跟着她跑、咬人、被打死、15 秒后再来；暴吼时四只；她倒下时伙伴一起消失。测试开关：日志旁边放一个 `league_naafiri.cfg`（`unit=off` / `still=1` / `name=<名字>`）。

## 一批伙伴一次要（v0.2.1，2026-11-14）

U4 看出来的：0.2.0 每只伙伴单独向公用的 `Flock` 要一次（`ask`），两只的原生效果在同一 tick 跑完、交接 buff 同一 tick 到，而 `Flock` 把一 tick 的交接都给最老的那一次要——两只都记在第一次上，第二次等不到就超时：日志里多一行 `HOUND NONE`（其实狗来了），下一次要伙伴被推到 900 tick 以后。暴吼的两只和缺的伙伴碰在同一 tick 要的话，还会互相拿错（暴吼的只活 300 tick）。

- 现在一批（出生时的两只、补上缺的、暴吼的两只）向 `Flock` 只要一次，每只照旧一个原生效果（伊莉丝的做法）；`Flock` 还有一次在等交接时不要新的一批（暴吼的两只先要，缺的那只下一两拍再要），所以每只单位都记成它本来是哪一批。
- 一批里只来了几只（某只生成失败、宿主没地方了）：那一次要已经被来的接走了，没有别的会超时，所以要了 `BATCH_WAIT`（11）tick 还没来齐就算没来，日志 `HOUND SHORT #k: 1 of the 2 packmates of her pack asked for at t=… never came - asked again in 900 ticks`；一只都没来照旧是 `HOUND NONE`，现在写明是几只、哪一批。
- `HOUND ASK` 一行一批：`HOUND ASK #k: 2 of her pack at (x,y) (x,y) (14000 behind her)`。
- 公用的 `Flock` 现在等单位站稳才接手（萨科附加包 0.3.1，`summon.rs`），`HOUND #n LOOK` 晚一两拍、数字是站稳以后的。
- 测试多三个：一批同一 tick 到、没有一次要会超时（下一次要不会被推远）；一批少了一只、到时候关掉、900 tick 后补；暴吼和缺的伙伴同一 tick 要时一先一后、每只记对是哪一批。
