# 伊莉丝附加包（测试版 v0.2.1，可选）：整身变蜘蛛、挑目标、小蜘蛛是真的单位

**不装这个附加包，主包里的伊莉丝也是完整的**：人形 / 蜘蛛两种形态、按战况切换、神经毒素、剧毒之蜇、结茧、自爆蜘蛛、盘丝、
掠行狂暴、小蜘蛛的被动和 5 级的茧缚猎杀都在主包数据里。主包是纯数据，有几件事做不到，这个附加包用原生代码补上（用户 2026-10-15
「附加包要」）：

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 蜘蛛形态的样子 | 只有出招（普攻、剧毒之蜇、盘丝、变身）是蜘蛛的动作，待机、跑步、受击、阵亡还是人形（游戏按名字自动播这几个，数据换不了） | **整个身体**都是蜘蛛：待机、跑步、受击、阵亡播 `c_idle` / `c_run` / `c_hit` / `c_dead`（只在游戏 0.6.4 上，别的版本退回左边那样）；复活是人形 |
| 结茧打谁 | 射程内随机一个敌方英雄（茧碰到第一个单位就停，常常打在小兵上） | 线上**没有小兵、野怪、别的英雄挡着**的英雄：被控住的先（必中），再挑最近的；都被挡着才挑最近的英雄 |
| 盘丝落到谁身上 | 射程内随机一个敌方英雄 | **生命比例最低**的英雄（一样低就近的） |
| 茧缚猎杀打谁 | 被控住的英雄先，没有就在最近被己方打过的英雄里随机挑 | **被控住的**英雄先（其中生命比例最低的），没有就挑生命比例最低的 |
| 小蜘蛛 | 她身上的计数（人形技能命中攒一只，最多 3 只），蜘蛛普攻时每只在目标身上咬一口（12 + 10% 法强魔法，掠行狂暴时 ×1.5），没有身体 | v0.2.0（游戏里还没看过）：变成蜘蛛时攒下的小蜘蛛全部爬出来，是真的单位：自己追咬（每口 12 + 10% 法强的物理伤害——单位的普攻没有伤害类型，英雄联盟是魔法伤害——节奏和她的普攻一样），生命是她的 14%，可以被打死（死一只扣一只攒下的）；掠行狂暴时攻速 +50%；盘丝落地时落在她身边；变回人形或阵亡时收起来（放逐到时间结束）。这期间数据里挂在目标身上的撕咬不再放。宿主给不出单位时照 v0.1 |

自爆蜘蛛、掠行狂暴照旧打 AI 选的目标。

## 怎么做的

- `mod.override_info` 把主包的伊莉丝换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_elise.py` 的 `native=1`
  生成，主包的伊莉丝改了就重跑）：加上本包的被动 `league_elise:queen`（参数 `e_range` 75000、`e_w` 2500、`ce_r` 50000、
  `r_range` 75000：结茧、盘丝、大招的射程，都从参数表 P 来），技能2和大招改成**对目标施放**（`Targeting`）：结茧的瞄准、
  盘丝的落点、茧缚猎杀都打向施法的目标，也就是本包 AI 钩子挑的那个，不再在射程内随机挑；技能2、大招的说明开头加【附加包】。
- **整身变蜘蛛**（`src/view.rs`）：照奈德丽附加包的整身变豹换**正在播的动画名**。显示世界每帧调用的更新函数（rva 0x23312a0，
  槽 rva 0x3c82db8）换成本包的函数：先调用槽里原来的（游戏的，或凯隐 / 佛耶戈 / 奈德丽 / 杰斯附加包的），再看名字是
  `league_elise` 的画面实体：身上有蜘蛛形态的 buff `league_elise_sp` 时，正在播的 `idle` / `run` / `hit` / `dead` 换成
  `c_idle` / `c_run` / `c_hit` / `c_dead`，普攻的第一 tick `attack` 换成 `c_attack`；变回人形就换回来。阵亡时 buff 清掉，
  尸体按倒下前的形态画。高清帧不用另管：league.dll 把动画表里每个动作（`c_idle` 也在内）就地换成它的 `hd_` 帧。
- **挑目标**（AI 钩子 `league_elise:aim`）：AI 要放技能2或大招时按上表换目标。技能2只在这次放的是结茧（人形、结茧好了、射程内
  有英雄）或盘丝（蜘蛛、盘丝好了、射程内有英雄）时换，判断照主包数据的分支（身上的 `league_elise_sp`、`league_elise_e_cd`、
  `league_elise_ce_cd`）。
- 原生代码只做判断和换名字，伤害、晕眩、盘丝的升空和落下都在数据里。

## 在游戏里测

1. 主包（League of Legends Heroes 0.115.0 以上）要装着并启用。
2. 把整个 `league_elise` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_elise.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看伊莉丝技能2的说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_elise.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `whole-body spider on: display slot …`：整身变蜘蛛装上了（`off (…)` 就是游戏版本不对）；
   - `world … Elise #…: SPIDER` / `human`：画面里变了形态；`FORM sim: SPIDER on` / `spider off`：模拟里的形态 buff；
     `SPAWN`：这局用的是附加包的伊莉丝；
   - `COCOON A -> B (CLEAR line, nearest / HELD + CLEAR line / all blocked, nearest …) AIM`、`RAPPEL … (LOWEST: …% hp)`、
     `HUNT … (HELD … / LOWEST …)`：换了目标（`kept` 是 AI 本来选的就是它）。
   - 模拟里的这几种行（`SPAWN`、`FORM sim`、`COCOON` / `RAPPEL` / `HUNT`）整个游戏一个计数：你看的那场每条都记，服务器的预模拟
     先记 40 条、之后每 50 条记一条（0.1.2：以前你看的那场也一样限，预模拟先把条数用完）。

## 开发

- `python -X utf8 addons/league_elise/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的伊莉丝和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_elise`：单元测试（参数和副本一致、副本的技能2 / 大招对目标施放、换动画名和图里的
  tag、尸体留形态、结茧 / 盘丝 / 大招挑目标）。
- 在 `addons/` 下 `cargo build --release -p league_elise`（Windows）得到 `target/release/league_elise.dll`；`league_addons`
  合集也会编进本包。工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\el_target`）。
- 经典 SDK 的模拟器跑不了原生代码；副本的数据部分（去掉原生被动）在经典 SDK 里跑过，AI 照样放结茧、盘丝和大招。本包只做了
  单元测试，要在游戏里看日志确认。

## 射程 buff 改成主包 league.dll 的 league:range（v0.1.3，2026-11-07）

带攻击距离的 buff 改成主包 league.dll 的 `league:range` 标记——buff 不再带 `range`（游戏的 AI 按它站位、却不按它出手，英雄停在够不着的地方），射程由官方的 `range_adjust` 加，AI 的出手判断也认；副本跟着主包 0.319.0 重新生成。

## 小蜘蛛是真的单位（v0.2.0，2026-11-14）

用户：「召唤物的全做啊 剩下的一批英雄也做了啊 都做完了装进去了再测」。召唤物第二轮（公用模块 `summon.rs` 的 `Flock`：一个召唤者好几个单位）。附加包的代码 + 主包一张单位图 `league/champions/league_elise_spiderling`（`tools/art/unit_elise_spiderling.py`：自爆蜘蛛那只爬行的小蜘蛛的 1 倍帧，和它今天在画面上一样大；idle / run / attack / hit / dead）。**要和带这张图的主包一起装**。

- 英雄联盟（wiki 现行页面）：人形技能命中攒一只休眠的小蜘蛛（2–5 只），变成蜘蛛时全部召出来、回满血，变回人形时收起来；生命 85–390、魔法伤害 10–40 + 15% 法强、攻速 0.665、移速 350、射程 100、护甲 30–90、魔抗 50–110；掠行狂暴给它们攻速，盘丝时和她一起升空落下。
- 被动看到她身上出现蜘蛛形态（主包的 `league_elise_sp`）就按攒下的只数（主包的 `league_elise_sl1`–`sl3`）排原生效果 `league_elise:spiderling`，在她身边 9000（第一只朝最近的敌方英雄）生成 `league_elise_spiderling`：攻击力 = 她的法强，每口 12 + 10%（主包 `sl_dmg` / `sl_ap`），每 52 tick 一口（她的普攻间隔），射程 18400，生命是她的 14%，护甲 100% / 魔抗 170% 她的，移速 106%，一次留 900 tick；她还是蜘蛛时到时间的马上换一只，被打死的扣掉一只攒下的（去掉最高的 `sl` 标记）；蜘蛛形态时又攒到一只（大招的茧）就再来一只。
- 有小蜘蛛单位时她身上一直挂 `league_elise_sl_unit`：副本的数据读它（`make_override.py` 给蜘蛛普攻里的小蜘蛛撕咬套上 `SwitchByBuff league_elise_sl_unit`），不再放挂在目标身上的撕咬。
- 掠行狂暴（她身上的 `league_elise_cw_on`）时每 20 tick 给每只小蜘蛛挂 30 tick 的 `league_elise_sl_frenzy`（攻速 +50%，主包 `sl_fz` 150%）；盘丝落地（她从选不中变回选得中）时把小蜘蛛放到她身边（`entity_set_pos`）。
- 它们咬的是物理伤害（单位的普攻没有伤害类型）。本来打算在引擎把这一口告诉她的被动（`on_attack`，用小蜘蛛的 id）时改成 0、下一 tick 由她打出同样多的魔法伤害；游戏 0.7.2 里 `on_attack` 从来不报单位的攻击（v0.2.1 那一节），这段代码留着但不会跑。
- 退路：宿主没有 `spawn_unit`、失败、读不成单位、一出来就没了、测试开关 `unit=off`——不挂 `league_elise_sl_unit`，数据照主包咬；这一次蜘蛛形态里不再要。
- 日志（都以 `SPIDERLING` 开头）：第二行 `SPIDERLINGS: … - ON`（测试开关）；`SPIDERLING ASK #`（排了几只、在哪）→ `SPIDERLING SPAWN #`（单位 id、数字）→ `SPIDERLING UNITS ON #` → `SPIDERLING #n LOOK #`（读回来的名字、种类、能不能选中、生命、攻击间隔）→ 每秒一行 `SPIDERLING #n #k:`（走了多远、生命、身边的敌人、她的伤害统计）→ `SPIDERLING #n OVER #`（被打死还是到时间、敌方那一 tick 拿了多少钱、咬的是物理伤害（`its bites physical`；引擎报了它的攻击时是 `N of its bites dealt as magic`）、还剩几只攒下的）→ `WAKE #`；`SPIDERLING FRENZY #`（buff 挂没挂上）、`SPIDERLING DROP #`（盘丝落地时搬了几只）、`SPIDERLING BANISH #`（变回人形 / 阵亡时放逐）、`SPIDERLING HOOK #`（引擎把谁的一下告诉了被动）；失败时 `SPAWN FAILED` / `NONE` / `LOST` / `SHORT` / `UNITS OFF`。
- 测试开关：日志旁边的 `league_elise.cfg`（`unit=off` 不生成、`still=1` 移速 1、`name=<名字>` 换单位名）。

## 小蜘蛛咬的是物理伤害、站稳了再接手（v0.2.1，2026-11-14）

第一批真实对局数据（游戏 0.7.2 的预模拟）：

- 单位的攻击从来不告诉召唤者的被动（玛尔扎哈的虚空蜂：`on_attack` 的行全是他自己的攻击），所以「引擎把小蜘蛛的一口告诉被动时改成魔法伤害」那一段不会跑；别的路也看不到它咬了谁、什么时候咬（API 读不到单位的目标和出手；靠「目标这一拍掉了多少血」去猜要知道引擎的护甲算法、暴击、护盾和同一拍里别的伤害）。小蜘蛛咬的照实是**物理伤害**：`OVER` 行改写成 `its bites physical (no hit of it reached her on_attack, so none was made magic)`，第二行写明 `physical - a unit's attack has no damage type`；改成魔法伤害的代码留着（以后的宿主要是报了照样管用）。英雄联盟的小蜘蛛打魔法伤害：这里差一个伤害类型。
- 新单位生成那一拍和下一拍数字都读成 1：公用的 `Flock` 现在等它站稳才接手（萨科附加包 0.3.1 的 `summon.rs`），`SPIDERLING #n LOOK` 晚一两拍、是它自己的数字。

## 神经毒素按当前生命、剧毒之蜇按已损生命（v0.2.1，2026-11-14）

用户 11-14 看了还剩下的、做得到的小项：「接着做」。英雄联盟（wiki 现行页面）：神经毒素「deals magic damage based on the target's current health」（40–160 + 4%（每 100 法强再 +3%）当前生命），剧毒之蜇「deals damage based on the target's missing health」（50–170 + 8%（每 100 法强再 +3%）已损生命），魔法伤害；按生命算的那部分对野怪有上限（65–145 + 90% 法强）。主包的数据读不到当前生命：目标最大生命的 3% / 5% 真实伤害。

- 副本（`make_override.py` 的 `venom`）：人形 Q 那一下、蜘蛛 Q 落地那一下、大招猎杀里的那一口，主包按最大生命算的真实伤害（`FixedAttack target_hp_ratio`）拿掉，换成本包的原生效果 `league_elise:neuro` / `league_elise:bite`，放在同一下的最前面（按挨这一下之前的生命算：英雄联盟是一下打出来的）。
- 原生效果（`src/lib.rs` 的 `VenomFx`）：打中的单位从效果的输入里来（弹道的命中效果拿得到它打中的单位；输入不是一个单位时找她身边 25000 内最近的敌人，日志注明），人形 Q 目标当前生命的 4%（`Q_CUR`），剧毒之蜇已损生命的 8%（`CQ_MISS`），魔法伤害；对野怪（野怪营地、史诗野怪、峡谷先锋类）最多 75 + 90% 法强（`QM_DMG` / `QM_AP`：英雄联盟中间一级的 105 按她 Q 的固定伤害的比例缩，100 → 70）。
- 英雄联盟每 100 法强多加的 3% 没做：她 Q 的法强加成在固定的那一块（主包的 60% / 70% 法强；英雄联盟的固定伤害没有法强加成），再加就算了两次。
- AI 估伤害：按最大生命的真实伤害和原生效果在估算里都是 0，不变。
- 说明（五种语言）：技能的说明改成「目标当前生命 4% 的魔法伤害」「已损生命 8% 的魔法伤害；按生命算的部分对野怪最多 75 + 90% 法强」，数字从 `src/lib.rs` 读。
- 日志：第三行 `VENOM: …`；每一下 `Q NEURO #k on <名字>#id: hp a/b - 4% of its current health: N magic` / `Q BITE #k …`（对野怪封顶时末尾 `(capped against a monster: …)`，输入不是单位时 `(no unit in the effect's input: the nearest enemy to her)`）。
- 经典引擎模拟跑不了原生代码，量不出来；主包没动。
