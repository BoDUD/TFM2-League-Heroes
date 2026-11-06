# 格雷福斯附加包（测试版 v0.2.4）

主包 `league` 保持纯数据。用户选了「做附加包」。这个附加包用原生代码做主包数据做不到的三件事，外加连招（0.2.0）：

- **快速拔枪的冷却**：英雄联盟里格雷福斯的普攻每有一颗弹丸打中，E 的冷却少 0.5 秒。数据不能减冷却。副本里霰弹枪正面那颗
  弹丸和扇形每打中一个单位就调一次 `league_graves:hit`，本包把 E（技能 2）的冷却减 `e_cut` tick（30 = 0.5 秒），一次普攻
  最多 `e_cuts` 下（4，英雄联盟的四颗弹丸）。
- **击退小兵和野怪**：英雄联盟里被几颗弹丸同时打中的非英雄单位会被击退。一次普攻里同一个单位挨了两下（正面那颗弹丸和扇形，
  也就是普攻的目标）而且不是英雄、不是塔，就往外推 `kb_speed` × `kb_t`（1500 × 4）。
- **终极爆弹的锥形爆炸**：英雄联盟里爆弹打中第一个英雄后在他身后炸开一个锥形。主包只能在那名英雄身边炸一圈；副本去掉那一圈，
  爆弹打中英雄时调 `league_graves:cone`：按格雷福斯到那名英雄的方向，那名英雄身后 `r_len`（55000）内、偏离不到 30 度
  （`r_dot` 866 = cos 30° × 1000）的敌方单位（塔除外）受到 `r2_dmg` + `r2_ratio`% 攻击力（80 + 60%）的物理伤害，各播一次
  打中的画面。

- **连招**（0.2.0，用户：「有连招的话一起做了」；`src/combo.rs`）：AI 钩子 `league_graves:combo`（优先级 110，排在
  league_ult_press 之后）替游戏的 AI 决定 E、R 什么时候按，像英雄联盟里会玩的人那样：
  - **换弹连招（普攻 → E → 普攻 → 普攻）**：霰弹枪两发一换弹，E 装回一发，可换弹开始以后（第二发打出）就装不回了。游戏的
    AI 一有目标就按 E，大半是在换弹时按掉的。本包在第一发打出去之后（`a_1` 在、弹丸已经飞出、没在换弹）、E 好了、普攻够得着
    的地方有敌人时替 AI 按 E（打它正在打的那个，没有就最近的敌方英雄、再没有就最近的野怪 / 小兵）——这一轮换弹打三枪；
    弹匣满着或已经在换弹时 AI 按的 E 改成普攻。照放的情况：生命不到 35% 而 e_near 内有敌方英雄（E 往后滚开逃命）、生命
    不到 30% 的敌方英雄在普攻够不着而 E 够得着的地方（追）、普攻够不着任何敌人（E 当位移）；走路时只在生命不低于 50% 时替它按。
  - **大招收割**：R 停在路上的第一个敌方英雄身上。AI 想放 R 时，只有打得死那个英雄（生命 + 护盾不超过
    (`r_dmg` + `r_ratio`% 攻击力) × 100 / (100 + 护甲)）、或他身后的锥形里还有敌方英雄（一炮两人）、或自己生命不到 25%
    而 25000 内有敌方英雄（后坐力把他弹开）才放；别的方向能打死人就换过去，都不行就改成普攻。R 好了、施放距离内有打得死的
    英雄（路上第一个就是他）、AI 在普攻或走路时替它按 R。
  - 被控住、正在放技能（施法动作）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

一次普攻：同一个格雷福斯第一次打中起 14 tick 内的打中都算这一枪（扇形在开枪那 tick 打中，正面那颗弹丸飞到目标最多几 tick；
普攻间隔 54 tick）。

数字：被动 `league_graves:grit` 的参数写在英雄数据的 `passive.params`，由 `make_override.py` 从 `tools/kit/build_graves.py`
的参数表 `P` 写入；`VOLLEY_T` 写在 `src/lib.rs`，单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.178 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_graves` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_graves.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看格雷福斯的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_graves.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Graves (player 0, team 0), ...`：出生；
   - `CUT #1: shotgun hit on ... - Quickdraw -30 ticks (now ... left)`：普攻减 E 的冷却；
   - `KNOCK #1: ... took two pellets - knocked back 1500x4`：击退小兵、野怪；
   - `CONE #1: Collateral Damage hit ... - the cone behind (55000 long) struck [...]`：大招的锥形；
   - `E PRESS on ...: the first shell is out ...`：替 AI 按的换弹 E（方括号里是弹匣状态和生命）；
   - `E VETO: both shells loaded / the reload has begun ...; shoots ... instead`：AI 按的 E 改成普攻；
   - `R PRESS toward ...: a kill / turned to the kill ...`：替 AI 按的收割 R；
   - `R VETO: no kill and nobody behind ...`：AI 按的 R 改成普攻。

## 开发

- `python addons/league_graves/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的格雷福斯和参数表一致）。
  主包的格雷福斯改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_graves`：单元测试（一枪的计数、锥形、参数、和参数表一致，连招的 E / R 判断）。
- 在 `addons/` 下 `cargo build --release -p league_graves`（Windows）得到 `target/release/league_graves.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。

## 游戏 0.6.5（0.2.1）

连招钩子回城时不出手；走路时按的 E 是朝目标冲的：不朝 AI 正在远离的人冲，也不冲进敌方塔 75000 内的人（0.6.5 的官方 AI 自己决定撤退、越塔）；打得死的 R 在原地开枪，照旧。

## 11-03 夜里的日志（0.2.3）

撞了墙的炮弹没有 `q_wall` 后就炸（7 发「stopped by a wall」，43 次 `Q BOOM` 全是「after the fuse」），炸完飞回来的炮弹飞向地图的
(0, 0)：这一发的信息（撞墙、出手的地方）塞在排队效果的输入里，排队只带回位置。现在这一发记在全局表里，排的效果只带终点，
炸弹落地、爆炸时按终点找回来（找不到时 `Q BOOM` 行尾写 `its shot was not found`）。全局表（这一发、一枪、爆炸炸到的人、参数）
都按这份模拟的编号记（被动出生时挂在他身上的 `league_graves_sim:<编号>`），不再按种子：服务器并排跑的两份预模拟不再串。

## 0.2.4：每份模拟只删自己的行（2026-11-06）

玩法不变。11-06 的日志里每一局看的比赛，画面都在开局 1-5 分钟和服务器的预模拟分开（三局换了赢家），排查时查了各附加包里跨模拟共用的状态。格雷福斯这里：齐射、弹壳、爆炸的表超过 4096 行**整张清掉**——同时在跑的别的模拟一下丢了这些，同一局的两份模拟在
不同的 tick 被清；施法者身上没有编号时（上一条命的弹壳、别的英雄放了复制来的技能）按 (0, 实体) 记，所有模拟共用一行（一次齐射的
命中、一次爆炸的受害者）。现在他新的一条命只删这份模拟里自己的行；没有编号的施法者借这份模拟里第一个挂着编号的单位的编号（打上
记号）。测试 `a_new_life_never_clears_the_other_sims_rows`、`an_untagged_caster_borrows_his_sims_number`。
