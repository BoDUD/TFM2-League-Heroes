# 格雷福斯附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户选了「做附加包」。这个附加包用原生代码做主包数据做不到的三件事：

- **快速拔枪的冷却**：英雄联盟里格雷福斯的普攻每有一颗弹丸打中，E 的冷却少 0.5 秒。数据不能减冷却。副本里霰弹枪正面那颗
  弹丸和扇形每打中一个单位就调一次 `league_graves:hit`，本包把 E（技能 2）的冷却减 `e_cut` tick（30 = 0.5 秒），一次普攻
  最多 `e_cuts` 下（4，英雄联盟的四颗弹丸）。
- **击退小兵和野怪**：英雄联盟里被几颗弹丸同时打中的非英雄单位会被击退。一次普攻里同一个单位挨了两下（正面那颗弹丸和扇形，
  也就是普攻的目标）而且不是英雄、不是塔，就往外推 `kb_speed` × `kb_t`（1500 × 4）。
- **终极爆弹的锥形爆炸**：英雄联盟里爆弹打中第一个英雄后在他身后炸开一个锥形。主包只能在那名英雄身边炸一圈；副本去掉那一圈，
  爆弹打中英雄时调 `league_graves:cone`：按格雷福斯到那名英雄的方向，那名英雄身后 `r_len`（55000）内、偏离不到 30 度
  （`r_dot` 866 = cos 30° × 1000）的敌方单位（塔除外）受到 `r2_dmg` + `r2_ratio`% 攻击力（80 + 60%）的物理伤害，各播一次
  打中的画面。

一次普攻：同一个格雷福斯第一次打中起 14 tick 内的打中都算这一枪（扇形在开枪那 tick 打中，正面那颗弹丸飞到目标最多几 tick；
普攻间隔 54 tick）。

数字：被动 `league_graves:grit` 的参数写在英雄数据的 `passive.params`，由 `make_override.py` 从 `tools/kit/build_graves.py`
的参数表 `P` 写入；`VOLLEY_T` 写在 `src/lib.rs`，单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.177 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_graves` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_graves.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看格雷福斯的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_graves.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Graves (player 0, team 0), ...`：出生；
   - `CUT #1: shotgun hit on ... - Quickdraw -30 ticks (now ... left)`：普攻减 E 的冷却；
   - `KNOCK #1: ... took two pellets - knocked back 1500x4`：击退小兵、野怪；
   - `CONE #1: Collateral Damage hit ... - the cone behind (55000 long) struck [...]`：大招的锥形。

## 开发

- `python addons/league_graves/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的格雷福斯和参数表一致）。
  主包的格雷福斯改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_graves`：单元测试（一枪的计数、锥形、参数、和参数表一致）。
- 在 `addons/` 下 `cargo build --release -p league_graves`（Windows）得到 `target/release/league_graves.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
