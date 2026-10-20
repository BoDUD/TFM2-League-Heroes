# 塞拉斯附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户选了「做，含按类别偷大招+连招」，又要求「有连招要做连招」。主包的数据复制不了别的英雄的大招，也读不到当前生命，所以这两件事放在这个附加包里用原生代码做，外加连招：

- **其人之道（按类别偷大招）**：英雄联盟里塞拉斯偷走对方的大招再放出来。主包是两段近似：第一次 R 甩链眩晕一名敌方英雄、拿到「夺来的大招」，10 秒内再放就在目标处爆发（对谁都一样）。副本里 R 的锁链打中英雄时在对方身上挂 `league_sylas_r_mark`（3 tick）；本包的被动 `league_sylas:hijack` 每 tick 找身上有这个标记的敌方英雄，按它的 id 查 `src/classes.rs`（原版英雄的表格类别和本包英雄的 `category`，`make_override.py` 用佛耶戈附加包的同一张表生成；查不到的别的 mod 英雄算近战），给塞拉斯挂 `league_sylas_cls_<类别>`（`r_keep` 600 tick），第二次 R 放出对应的那一套（伤害都是 `r2_dmg` 200 + `r2_ratio` 80% 法强）：
  - **近战**：跃到目标身上重砸，`r2_slam_r` 内的敌人受伤并眩晕 1 秒；
  - **射手**：朝目标射出贯穿长箭（`r2_alen` 120000），路上的敌人受伤并减速 40%；
  - **法师**：主包那一套，在目标处爆发、击飞周围敌人；
  - **辅助**：身边 `r2_song_r` 内的友方英雄回血（120 + 40% 法强）加护盾（100 + 30% 法强，3 秒），周围敌人受一半伤害并减速；
  - **刺客**：闪到目标身边一记重击（1.25 倍伤害）并隐身 1 秒。
  R 的说明换成 `description.league_sylas_addon.ult`（五种语言），写明五类。
- **弑君突刺**：英雄联盟里回血随已损失生命最多多 150%。副本里突刺的回血调 `league_sylas:kingslayer`：回 (`w_heal` 40 + `w_heal_r` 35% 法强) × (1 + `w_miss` 150% × 已损失生命比例)。普攻的说明换成 `description.league_sylas_addon.attack`。
- **连招**（用户：「有连招要做连招」；`src/combo.rs`）：AI 钩子 `league_sylas:combo`（优先级 110，排在 league_ult_press 之后）替游戏的 AI 按 Q、R，改普攻目标：
  - **E → Q**：强掳把他拉到英雄身上（E 放出后 `e_dur` 到 `e_dur` + 30 tick 内），Q 好了：朝离他最近的敌方英雄按 Q，锁链交叉在落点、爆炸接在击飞后面。（E → 弑君突刺在主包数据里：落地时突刺好了就马上刺。）
  - **夺来的大招挑时机**：手里有夺来的大招、R 好了：`r_range` 内有一名敌方英雄身边 `r2_r` 内还有另一名（能炸到两个），或者有生命低于 40% 的敌方英雄，就朝他按 R；AI 自己想放、但只炸得到一个满血的人、大招也还没快过期（剩 90 tick 以上）：改成普攻那个人，留着大招。
  - **残血优先**：弑君突刺好了、AI 想普攻小兵 / 野怪，而突刺够得着的地方有生命低于 40% 的敌方英雄：改成普攻那名英雄（普攻变成突刺）。
  - 被控住、正在放技能（施法动作）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

数字：被动 `league_sylas:hijack` 的参数写在英雄数据的 `passive.params`，由 `make_override.py` 从 `tools/kit/build_sylas.py` 的参数表 `P` 写入；单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.181 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_sylas` 文件夹放进 `<游戏目录>\mods\`（要有 `league_sylas.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看塞拉斯普攻和大招的说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sylas.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Sylas (player 2, team 0), ...`：出生；
   - `STEAL #1: the ult of league_jinx#23 (range)`：偷到谁的、哪一类；
   - `HEAL #1: Kingslayer at 42% health (ap 120) - healed 152`：突刺按损失生命回血；
   - `E THEN Q ...`、`STOLEN R ...`、`HOLD R ...`、`W ON PREY ...`：替 AI 按的连招。

## 开发

- `python addons/league_sylas/make_override.py`：从参数表重新生成 `override/`、`text/` 和 `src/classes.rs`（先核对主包的塞拉斯和参数表一致）。主包的塞拉斯改了、或者加了新英雄以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_sylas`：单元测试（突刺回血、类别表、参数、和参数表一致，连招的 E → Q、夺来的大招挑时机、残血优先）。
- 在 `addons/` 下 `cargo build --release -p league_sylas`（Windows）得到 `target/release/league_sylas.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
