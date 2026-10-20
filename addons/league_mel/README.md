# 梅尔附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户选了「做附加包」，又要求「有连招要做连招」。主包的数据做不到英雄联盟里梅尔的两件事——**夺命残影的处决**（数据读不到生命，也数不了目标身上的层数）和**灵魂折镜的反弹**（没有效果能挡住或拐弯一个弹体）——所以放在这个附加包里用原生代码做，外加连招：

- **夺命残影的处决**：英雄联盟里梅尔每次打中都叠一层残影，残影的伤害够了，下一次打中就直接处决。副本里每一层残影（普攻、灼灼之光的光弹、Q 的每次爆炸、E 的法球中心打中英雄时）除了主包的残影（R 读它），还在英雄身上挂一层 `league_mel_m_mark`，并调 `league_mel:overwhelm`：那名英雄身上的层数 × (`x_st` 20 + `x_ratio` 8% 法强) ≥ 他的生命 + 护盾时，用真实伤害打掉剩下的生命（处决），并消耗本包的层数；放一次金色的处决画面和音效。
- **灵魂折镜**：英雄联盟里 W 生成屏障，把敌人的弹体反弹回去、她自己不受伤害、加移速。主包只能「每 25 秒第一次打中英雄时张开屏障」；副本去掉了这一条，被动 `league_mel:reflect` 每 tick 看一遍场上的弹体：
  - W 好了（`w_cd` 1500 tick）、一个敌方英雄的弹体飞到她 `w_near`（30000）以内，就张开屏障 `w_t`（75 tick）：受到的伤害减少 `w_red`% 100、反弹 `w_ref`% 40、移速 +`w_ms`% 25（和主包同名的 `league_mel_w_on`，画面一样），放 W 的音效和配音；
  - 屏障开着时，飞到她 `w_back`（6000）以内的每个敌方英雄的弹体（同一个人 20 tick 内只算一次）：复制一枚金色光弹飞回发射的人，按飞行时间打中，造成 `w_back_dmg` 60 + `w_back_r` 40% 法强魔法伤害。原来的弹体删不掉（接口只能读弹体），靠屏障免伤。
- **连招**（用户：「有连招要做连招」；`src/combo.rs`）：AI 钩子 `league_mel:combo`（优先级 110，排在 league_ult_press 之后）替游戏的 AI 按 Q、E、R，像英雄联盟里会玩的人那样：
  - **E → Q**：AI 想用 Q 砸一个敌方英雄、E 好了、那名英雄在 E 的施放距离内：先替它按 E（阳炎涡旋的中心禁锢他）。
  - **禁锢住了接 Q**：法球禁锢了英雄（她身上开着 `league_mel_e_combo`）、Q 好了、Q 够得着被禁锢的敌方英雄：替 AI 朝他按 Q。主包数据里这时的 Q 快速落在被控住的英雄身上，六次爆炸全打在他身上。
  - **残影 → R**：鎏金蚀日打所有带残影的敌方英雄，伤害按层数算，所以 R 要等残影叠起来：一名英雄身上的残影够打掉他的生命 + 护盾（`R KILL`），或者两名以上英雄的残影都够打掉他们 40% 的生命（`R MANY`），才按 R；AI 自己想按 R 但两样都不够时不放，改成普攻它的目标（`R HELD`）。R 的施放点一名 R 距离内最近的敌方英雄（伤害是全图的）。
  - 被控住、正在放技能（施法动作）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

数字：被动 `league_mel:reflect` 的参数写在英雄数据的 `passive.params`，由 `make_override.py` 从 `tools/kit/build_mel.py` 的参数表 `P` 写入；单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.182 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_mel` 文件夹放进 `<游戏目录>\mods\`（要有 `league_mel.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看梅尔的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_mel.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Mel (player 3, team 0), ...`：出生；
   - `EXECUTE #1: ... - 12 stacks worth 432 >= health 410 + shield 0`：残影处决；
   - `W UP #1: a projectile of ... 21000 away - the barrier for 75 ticks`、`REFLECT #1: a projectile of ... sent back (140 magic in 9 ticks)`：屏障和反弹；
   - `E FIRST`、`Q ON ROOT`、`R KILL`、`R MANY`、`R HELD`：替 AI 按的连招（方括号里是每名英雄身上的残影层数）。

## 开发

- `python addons/league_mel/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的梅尔和参数表一致）。主包的梅尔改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_mel`：单元测试（残影的价值和处决、反弹光弹的伤害、参数、和参数表一致，连招的 E → Q、禁锢后接 Q、R 等残影）。
- 在 `addons/` 下 `cargo build --release -p league_mel`（Windows）得到 `target/release/league_mel.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
