# 卡萨丁附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户问被动「看看rust能做吗」，附加包做哪几项「你看着办吧」——这个附加包用原生代码做主包数据做不到的三件事：

- **虚空之石正好减 10% 魔法伤害**：主包用一个固定的魔抗 buff 近似（他自己的魔抗下约 10–11%）。附加包的被动
  `league_kassadin:void_stone` 每 15 tick 读他现在的魔抗（装备、别人的减魔抗都算上），按 魔法伤害 x 100 / (100 + 魔抗)
  算出还要补多少魔抗，用一个永久 buff 补上，让魔法伤害始终正好少 10%。英雄联盟里「无视单位碰撞」游戏没有开关（数据和原生接口都没有），不做。
- **能量脉冲真实充能**：主包只有他自己放 Q 和 R 给 E 减冷却。附加包每 tick 读所有英雄的冷却，冷却跳高了就是放了技能：
  他身边（`reach` 32000）每有一个英雄放技能（敌我都算，他自己的 E 不算），E 的剩余冷却少 90 tick（英雄联盟 1.5 秒）。
  减冷却用 2 tick 的 `skill_cooldown_mult`；它也会压 Q，所以只压到不碰 Q 的程度（Q 剩余冷却占比更大时这一下不减）。
- **虚空行走挑落点**：主包随机闪到射程里的一个敌方英雄。附加包的 `league_kassadin:rift` 在 R 出手那一 tick 试射程里每个敌方英雄：
  这一下（算上叠层、对方魔抗）能打死的优先，其次爆炸里英雄多、离他远（后排）的；敌方塔 75000 以内的不去，都不行就落在大招目标身上。
- **虚空行走清兵**（0.1.2，用户 2026-10-23：「卡萨丁的R能不能对小兵造成伤害」）：爆炸本来就炸小兵，但游戏的 AI 只在打架时放大招、
  只对英雄放。副本的 R 改成对敌人放，AI 钩子 `league_kassadin:farm`：AI 在打小兵 / 野怪、R 好了、80000 内没有敌方英雄时，
  挑射程里爆炸炸到最多小兵（至少 3 个、不在敌方塔下）的那个按 R，落点就是它；AI 自己对小兵放 R 而射程里有敌方英雄时改对英雄放。
  主包不改：主包对敌人放时 AI 放大招的次数不变、打架时有几次放在小兵身上（模拟 +1.49 -> +0.33）。日志 `FARM` / `RETARGET`。
  落在目标身前 6000，之后数据里的爆炸照常。

数字：被动的参数写在英雄数据的 `passive.params`（`{"cool": 900, "q_cool": 360, "cut": 90, "reach": 32000, "dr": 10}`），
由 `make_override.py` 从 `tools/kit/build_kassadin.py` 的参数表 `P` 写入；R 的数字写在 `src/lib.rs`（`R_*`），单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.101 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_kassadin` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_kassadin.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看卡萨丁的技能说明：普攻、E、R 开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kassadin.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `VOID #1 resistance 22 (shown 22, mine 0) -> +14 = 36: magic damage x 0.735`：补魔抗。
   - `CHARGE #3 Ahri#12 Q: E 610 -> about 520 (mult 74, Q 40)`：身边有人放技能，E 减冷却。
   - `RIFT (..) -> (..) (41000 away, 1 stacks, 245 magic before resistance): 2 champions in the blast, score 26.1, a kill`：落点。

## 开发

- `python addons/league_kassadin/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的卡萨丁和参数表一致）。
  主包的卡萨丁改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_kassadin`：单元测试（10% 的魔抗、E 减冷却不碰 Q、落点打分、参数）。
- 在 `addons/` 下 `cargo build --release -p league_kassadin`（Windows）得到 `target/release/league_kassadin.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认（尤其 `stat()` 的魔抗是否含 buff：
  VOID 行在 buff 加上后应该稳定不再变）。
