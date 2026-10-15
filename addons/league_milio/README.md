# 米利欧附加包（测试版 v0.1.0，可选）

**不装这个附加包，主包里的米利欧也是完整的**：火球普攻、Q 火爆飞踢、E 融融情谊 + W 依依不舍、R 生生不息、被动热情洋溢！都在主包数据里。
主包是纯数据：数据里没有「另一个单位打中了谁」的时机，**读不到当前生命**，所以被动只能做成加攻击力和法强，R 只能按控制和身边的敌人
猜什么时候放。这个附加包用原生代码把两件事做成英雄联盟的样子（用户 2026-10-15 选「被动主包数据近似 + 附加包精确」「R 像千珏那样挑时机」）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 热情洋溢！ | E 和 R 触及的友方 5 秒内攻击力、法强 +30% | E、R 触及的友方（**营火每一跳也算**）身上挂记号（画面不变）；他**下一次打中敌人**（普攻或技能，不算防御塔）就把那个敌人点燃：**1.5 秒内 20-100 魔法伤害**（按米利欧的等级，1-12 级线性；对野怪最多 100），记号随即用掉 |
| 生生不息什么时候放 | AI 放出后待命 10 秒，期间友方被控制、敌方英雄贴身、或友方身边有敌方英雄就放 | 他身边（R 的圈小一圈）有友方英雄（**队友或他自己**）危险才放：身边有敌方英雄，而且**被硬控着**（眩晕、禁锢、击飞、嘲讽、恐惧、魅惑，还剩半秒以上），或**生命低于 30%**，或 **1 秒内被打掉三成、只剩六成以下**；几个人都危险时救最危险的。没人危险时 AI 想放 R，改成普攻，R 留着 |
| 解控 | 只给 1 秒免控（挡新的控制，已经在身上的眩晕还在） | R 生效时圈里身上有控制的友方英雄**真的被解控**（再加主包的 1 秒免控和韧性） |

## 怎么做的

- `mod.override_info` 把主包的米利欧换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_milio.py` 生成，主包的米利欧改了就重跑）：
  `r_now=1`（R 一放出就生效，不再待命、不再在普攻和技能里查危险）、`league_milio_fired` 没有数值只当记号、营火每一跳也挂记号、
  被动是本包的 `league_milio:fired`（数字在 `passive.params`）、R 的圈里先调本包的 `league_milio:cleanse`；普攻（被动）和 R 的说明开头加【附加包】。
- **谁打中了谁**：SDK 里没有「别人打中了谁」的钩子（原生被动的 on_attack 只给被动的主人自己）。被动每 tick 读友方玩家的冷却，某一栏跳高了
  = 刚出手；观察钩子 `league_milio:watch`（挂在所有非米利欧玩家身上，优先级最低，只记不改 AI 的输入）记下每个玩家的 AI 最后一次下令打 / 放技能
  对准的敌人，出手后就等那个敌人掉血。没有命令目标时（边走边打、方向和地点技能），在出手后掉了血的敌人里先挑身边有他投射物的、再挑离他
  最近的（掉得太少的不算）；技能对准友方（治疗、护盾）的不算出手。经典引擎里量过：AI 的普攻命令 98% 就是这一下打的目标；只按掉血猜，
  目标是英雄时对 80-84%，小兵、野怪 90%。米利欧自己带记号时（E 给了自己）用他自己的 on_attack，准确。
- **R 挑时机**（AI 钩子 `league_milio:ult`，千珏附加包的做法）：危险就下令放 R（施放目标是 75000 内最近的敌方英雄，主包 R 的施放条件），
  他正忙时引擎要几 tick 才接，钩子每 tick 再下一次；**R 的冷却真的开始走才算放出去一次**。
- **每份模拟各算各的**：状态都在被动、钩子各自的对象里；观察钩子交给被动的命令表按「这份模拟的编号 + 友方实体」记，编号挂在米利欧身上
  （buff `league_milio_sim:<编号>`，没有数值、没有画面），游戏 0.6.4 同时跑的两份预模拟不会串（莫德凯撒附加包的教训）。
- 灼烧的画面借主包 Q 落地的灼烧（`league_milio_q_burn`），伤害记在米利欧名下（魔法伤害，吃魔抗）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.113.0 以上）要装着并启用。
2. 把整个 `league_milio` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_milio.dll`、`mod.mod_info`、`mod.override_info`、`override\`、
   `text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看米利欧普攻的说明：开头是「【附加包】」、写着「下一次命中敌人时将其点燃」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_milio.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN`：这局用的是附加包的米利欧（第几份模拟）；
   - `FIRED SET 某人#id fired up (n marks)`：某个友方挂上了记号；
   - `BURN 某人#id attack (ordered at it) hit 某敌#id -> 60 magic over 90 ticks (Milio Lv6)`：记号用掉、点燃了谁（`ordered at it` = 按 AI 的命令目标，
     `guessed` = 按掉血猜的，`own hit` = 米利欧自己）；
   - `FIRED UNUSED 某人#id's mark ran out`：记号没用上就过期了；
   - `R ORDER [LOW HP / BURST / CC] for 某人#id`：钩子下令放 R（他正忙时会连着下几次）；
   - `R CAST [CC] for 某人#id (crowd-controlled 52 more ticks, hp 70%; ...)`：R 真的放出去了，为谁、为什么；
   - `R CAST by the AI itself`：AI 自己放了 R（钩子没拦住，不应该出现）；
   - `R CLEANSE: 某人#id freed from [Stun 41]`：R 解掉了谁身上的什么控制；
   - `R RESULT [..] for 某人#id (hp 22% at the cast): alive, hp 48%, cc-immune (in R)`：放出后 30 tick 他怎么样了；
   - `R HELD: nobody around him in danger, attacking instead`：AI 想放、没人危险，留着。

## 开发

- `python -X utf8 addons/league_milio/make_override.py`：重新生成 `override/` 和 `text/`（先核对主包的米利欧和参数表一致、`src/rules.rs` 里 R 的射程、
  半径、生效 tick 和普攻射程和参数表一致）。被动的数字在 `make_override.py` 的 `PASSIVE`（和 `src/rules.rs` 的 `Params::default` 由测试核对），
  附加包版本的平衡数字在 `NUMBERS`。
- `src/rules.rs` 是不碰 SDK 的规则（灼烧、谁打中了谁、谁危险），`src/lib.rs` 是接 SDK 的部分；离线模拟器直接编进 `rules.rs`。
- 在 `addons/` 下 `cargo test --release -p league_milio`：单元测试。`cargo build --release -p league_milio`（Windows）得到 `league_milio.dll`；
  `league_addons` 合集也会编进本包。工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\mi_target`）。
