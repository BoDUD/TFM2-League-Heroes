# 低血量附加包（测试版 v0.3.1，可选）：布里茨、乐芙兰、丽桑卓

0.2.5（2026-11-05）：丽桑卓的副本带上「弗雷尔卓德的女王」的冰冠冕（主包 `view_buffs` 里的 `league_eggs_crown_lissandra`，`tools/fix/eggs_crown_views.py`），副本跟着主包重新生成；英雄联盟彩蛋（`league_eggs`）在她赢下弗雷尔卓德之战时挂这个 buff。DLL 没变。

0.2.4（2026-11-05）：待命式大招没用掉时的冷却退还从来没生效过：n tick 的待命标记只有 n - 1 tick 看得见（经典 SDK 探针 lr1105/fix_j：n - 1 之前 148/148 次看得见，第 n tick 0 次），退还在窗口最后一 tick 读它时已经没了，所以每次待命过期都要等完整冷却（塞恩追踪：过期到再待命 3558 tick，改读后 877）。现在在窗口结束前 3 tick 读（布里茨：`tools/fix/arm_refund_read.py`；丽桑卓：`tools/kit/build_lissandra.py` + 同一脚本），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里这三人的保命技能都在**生命低**的时候触发。主包是纯数据，读不到生命，只能改成「身边有两名以上敌方英雄」时触发（布里茨再加「队友被控」）。**不装这个附加包，主包的三人也是完整的**。

| 英雄 | 主包（纯数据） | 装了附加包（英雄联盟） |
|---|---|---|
| 布里茨 法力屏障 | 被围攻或队友被控 | 生命不高于 30% |
| 乐芙兰 镜花水月 | 两名以上敌方英雄贴近；幻像是她站的地方放一下的画面（1 秒） | 生命不高于 40%；0.3.0 起幻像是真的单位（`spawn_unit`）：和她一模一样，生命是她当时的，会追着敌人假装攻击（没有伤害），能被打死，留 320 tick |
| 丽桑卓 大招冰封自己 | 被两名以上敌方英雄围住 | 生命不高于 35% |

## 怎么做的

- 主包每次动作先数身边的敌方英雄，两个以上就挂 `<名>_n2`（`league_blitzcrank_mb_n2` / `league_leblanc_p_n2` / `league_lissandra_r_n2`），再读它决定触不触发。
- 副本由 `make_override.py` 从主包生成：读这个标记的地方（布里茨 36 处、乐芙兰 2 处、丽桑卓 3 处）改成读本包的 `<英雄>_low`。主包的计数还在，只是没人读了。改过的说明开头加【附加包】。
- 被动 `league_lowhp:blitzcrank` / `:leblanc` / `:lissandra` 在生命不高于门槛时每 tick 把 `<英雄>_low` 续 3 tick。护盾、隐身和幻像、冰封都还是主包数据里的那一套，冷却也是。


## 丽桑卓的冰仆（v0.2.0）

主包只认她自己打死的英雄（击杀检查）；英雄联盟里她身边任何敌方英雄阵亡都化成冰仆。副本去掉数据里的 7 处冰仆（`league_lissandra_k_*` 只留去掉旗子那一下），她的被动 `league_lowhp:lissandra` 每 tick 记下敌方英雄的位置和死活：有人在她 90000 内由活变死，就在他倒下的地方播主包的冰仆画面和声音，90 tick 后碎裂，播碎裂画面和声音，25000 内的敌人（英雄、小兵、野怪）受到 150 + 70% 法强的魔法伤害、减速 25% 1.5 秒（同主包）。冰仆不会走：画面是挂在地上的，走了画面跟不上。v0.2.1 起碎裂时扑向 45000 内最近的敌方英雄（没有英雄就最近的小兵、野怪），在他身上碎裂、播碎裂画面：原地碎裂时 22 次只有 4 次炸到人（1.5 秒后尸体边上已经没人）。普攻的说明开头加【附加包】、「她击杀的」换成「她身边阵亡的」。日志：`THRALL #n rose at (x, y) where one died (kill log), lunged 31000, shattered: 2 enemies hit for 290`。

v0.2.3（2026-11-04，11-03 晚的日志：一局丽桑卓出生 7 次、`LOW` 8 次，一个冰仆也没有）：阵亡英雄的实体一般下一拍就不在了，0.2.2 只认「还在列表里、标着死了」的敌人，从来没等到过。现在上一拍还活着、这一拍不在列表里的也算阵亡，冰仆在他上一拍站的地方升起（`fallen`）。

v0.2.6（2026-11-06，11-06 的日志）：42 个冰仆里 11 个扑到人（都炸到了），31 个 `lunged 0, shattered: 0 enemies hit`——碎裂时 45000 内一个敌人（英雄、小兵、野怪）都没有。英雄联盟的冰仆会追附近看得见的敌人（英雄优先）4 秒、速度从 33 涨到 325，一路追下来 700 多码；本包 1.5 秒就碎（主包画面的长度），扑的距离就照一整只冰仆追得到的算：`THRALL_LUNGE` 45000 → 72000。复查里的另一个怀疑（没死、只是从单位列表里消失的人——被放逐、骑在别人身上——也被当成阵亡）日志里看不出来，先不改判定，`THRALL` 行写上冰仆从谁身上升起：`where one died (kill log)` / `one left the list (a death in the kill log)` / `one left the list with NO death in the kill log`（对照击杀记录），扑空时再写最近的敌方英雄和单位多远 （`nearest enemy champion D, unit D`）。下一局看扑空的还多不多、有没有 `NO death in the kill log`。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_lowhp` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 布里茨、乐芙兰的普攻和丽桑卓 R 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lowhp.log`：`LOW #n: hp 280/1000`（掉到门槛以下的那一刻）。

## 开发

- `python addons/league_lowhp/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。三人在主包里改了就重跑。
- `cargo test -p league_lowhp`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。

## 乐芙兰的幻像是真的单位（v0.3.0，2026-11-14）

用户看了「和英雄联盟不一样的地方」的清单后说「全改吧」（其中一条是「召唤物不会走、不会打、打不掉」），之后「召唤物的全做啊」。英雄联盟（wiki 现行页面）：生命降到 40% 时她和幻像一起隐身 1 秒；幻像和她一模一样，生命是她当时生命的 100%，普攻没有效果（"can cast basic attacks with no effect"），留 8 秒。这里原来的幻像是她站的地方放一下的画面（`league_leblanc_p_clone`：她的待机，然后化成光柱，1 秒）。代码在 `src/mirror.rs`（公用部分是萨科附加包的 `src/summon.rs`，用 `#[path]` 引进来）。

- **数据让开**：她活着时被动每 tick 续挂 `league_leblanc_p_unit`（同 `league_leblanc_low` 的做法）。副本里那两处幻像画面（普攻、技能里各一处）外面套了 `SwitchByBuff league_leblanc_p_unit`，有就不放。画面不算伤害，AI 估伤害看到的和原来一样。
- **什么时候生成**：触发还是数据的（生命不高于 40%、40 秒一次）；数据在那一刻挂上 40 秒的 `league_leblanc_p_cd`，被动看到它出现，就在她上一拍站的地方（她马上往后闪开）排原生效果 `league_lowhp:mirror`，它调 `spawn_unit`：单位叫 `league_leblanc`（按她自己的图画——和那张画面一样是她 PPU 2.0 的待机，一样大；`league.dll` 的高清帧按这个名字认，要在游戏里看），活 320 tick（英雄联盟的 8 秒照她被动的冷却缩：60 秒 → 40 秒），攻击和法强 0（普攻没有伤害），普攻距离 52500、每 90 tick 一下（她的普攻），移速、护甲、魔抗照她的，生命上限是她的、当前生命设成她当时的。引擎管着它：会追着敌人假装攻击，敌人打得到、打得死。数字都是她的数据里的，`make_override.py` 对照检查。
- **退路**：宿主没有这个接口、生成失败、给的 id 5 tick 内读不成单位、单位 6 tick 内就没了——在那个地方放原来那张画面（原生地放）；日志旁边的 `league_lowhp.cfg` 写了 `unit=off`（测试开关）——不挂 `league_leblanc_p_unit`，数据照旧放画面。
- **她先死了**：被动不再跑，幻像由引擎管着到时间。
- **没做的**：英雄联盟里幻像朝她面前随机一个方向跑开 1900 码、躲着伤害来源跑（API 没有下命令的接口），这里由引擎的单位 AI 带着它去追敌人。
- **日志**（`league_lowhp.log`）：第二行 `MIRROR: Mirror Image's clone is a unit ('league_leblanc', spawn_unit) - ON`（结尾是读到的测试开关）；每个幻像 `MIRROR ASK`（她站在哪、闪到了哪）→ `MIRROR SPAWN`（属性）→ `MIRROR #n LOOK`（读回来是什么：名字、种类是不是 summon、能不能被选中、生命、移速、攻击间隔；生命设成她的了没有）→ `MIRROR #n DRESS` → 每秒一行 `MIRROR #n #k`（在哪、走了多远、生命涨落、身边的敌人）→ `MIRROR #n OVER`（被打死还是到时间、尸体、敌方玩家拿到的钱）→ `WAKE`；她死时 `ORPHAN`；`HOOK` 看幻像的攻击算不算到她身上。退路：`MIRROR SPAWN FAILED`、`MIRROR NONE`、`MIRROR LOST`（都放了画面）、`MIRROR OFF`（数据放了画面）。
- 丽桑卓、布里茨的副本没变。
## 丽桑卓的冰仆是真的单位（v0.3.1，2026-11-14）

用户：「召唤物的全做啊 剩下的一批英雄也做了啊 都做完了装进去了再测」。召唤物第二轮。代码在新文件 `src/thralls.rs`（`lib.rs` 只多几处接线：一个字段、站起时问一个单位、每 tick 看一眼、碎裂从它走到的地方扑、注册一个原生效果和日志一行；`make_override.py` 没动：冰仆本来全是本包的）。版本 0.3.1（0.3.0 是乐芙兰镜花水月那条分支用的号）。主包多一张单位图 `league/champions/league_lissandra_thrall`（`tools/art/unit_lissandra_thrall.py`：冰仆自己的画面 `p_thrall` 的 1 倍帧——这张特效图是特效高清表里的，游戏按 1 倍的大小画，所以和今天一样大，不用在 league.dll 里登记：idle 站着的三帧，run 三帧轮流快放（踉跄着走），attack 站着 → 裂开 → 站着（它不打人），hit 往后一格，dead 裂开、发白、没了）。**要和带这张图的主包一起装**。

- 英雄联盟（wiki 现行页面，V26.10）：附近的敌方英雄阵亡时从尸体里站起一个冰仆，追着附近看得见的敌人走 4 秒（先追英雄，速度从 33 涨到 325），让附近的敌人减速 25%，4 秒后碎裂，120–520 + 50% 法强的魔法伤害；冰仆选不中、打不死。所以这一条照做了：英雄联盟现在的冰仆还是会走的。
- 冰仆站起时（她身边 `THRALL_REACH` 内有敌方英雄倒下）排原生效果 `league_lowhp:thrall`，在尸体处生成单位 `league_lissandra_thrall`：移速和她一样（英雄联盟的冰仆最后涨到她的速度；我们的只走 1.5 秒），攻击 0 且够不着任何人（冰仆不打人，只朝敌人走），生命是她上限的 30%，护甲魔抗和她一样，留到碎裂（`THRALL_TICKS`）；读成单位那一 tick 起挂 `league_lissandra_thrall_ice`（受到的伤害 -100%、不死、免控：英雄联盟里打不死）；成功了尸体处不再放冰仆的画面。到时间时碎裂从冰仆**走到的地方**再扑向 `THRALL_LUNGE` 内最近的敌人（以前从尸体处扑），伤害、减速照旧；`THRALL` 行多了 `walked`（走了多远）。
- 退路：宿主没有 `spawn_unit`、失败（`league_lowhp:thrall` 照旧在尸体处放画面）、读不成单位、测试开关 `unit=off`——和以前一样：画面 + 从尸体处扑（`walked 0`）。
- 日志：第二部分的 `THRALLS: … - ON` 一行（测试开关在日志旁边的 `league_lowhp.cfg`）；`THRALL UNIT SPAWN:`（单位 id、位置、数字）→ `THRALL UNIT #n LOOK:`（读回来的名字、种类、能不能选中、生命、`the ice … is on it / is NOT on it`——buff 挂不挂得上召唤物）→ 每秒一行 `THRALL UNIT #n:`（走了多远、身边的敌人）→ `THRALL UNIT #n OVER:` → `THRALL #k rose at … walked …, lunged …, shattered: …`；失败时 `THRALL UNIT SPAWN FAILED` / `THRALL UNIT LOST`。
- 还没做：选不中（没有让单位选不中又能走的接口：敌人会白打它）、活着时让附近的敌人减速 25%（这里碎裂时才减速）、速度从慢到快（这里一直是她的速度）、站起来的动作（单位一出来就站着）、它变成那个英雄的样子（英雄联盟的冰仆是死者的模样）。
