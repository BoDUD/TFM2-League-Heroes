# 沃里克附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户选了「做附加包」，又要求「有连招要做连招」。主包的数据读不到当前生命，英雄联盟里沃里克最核心的两件事——**残血吸血**和**鲜血追猎**——都看生命，所以放在这个附加包里用原生代码做，外加连招：

- **血之饥渴**：英雄联盟里沃里克的普攻附带魔法伤害；他生命低于 50% 时回复同样多的生命，低于 25% 时回三倍。主包只能每下固定回一点；副本里每一下爪击（普攻、Q 的撕咬、R 的三下）打中时调 `league_warwick:hunger`：他生命低于 `p_half`%（50）时回 `p_dmg`（20，和这一下的魔法伤害一样），低于 `p_quarter`%（25）时回 `p_dmg` × `p_triple`（60）；生命高的时候不回（魔法伤害照旧在数据里）。
- **鲜血追猎**：英雄联盟里他嗅到生命低于 50% 的敌方英雄，朝他们跑得更快、打他们打得更快，低于 25% 时加成三倍。主包只能「打中英雄后加速 2 秒」；本包的被动 `league_warwick:hunt` 每 6 tick 看一次：`w_reach`（150000）内有看得见的、生命低于 `w_half`%（50）的敌方英雄，就给他挂 `league_warwick_w_hunt`（攻速 +`w_as`% 30、移速 +`w_ms`% 12，10 tick，下次看时续上，主包的红色光晕跟着亮），那人低于 `w_quarter`%（25）时三倍（攻速 +90%、移速 +36%）。
- **连招**（用户：「有连招要做连招」；`src/combo.rs`）：AI 钩子 `league_warwick:combo`（优先级 110，排在 league_ult_press 之后）替游戏的 AI 按 E、Q、R，像英雄联盟里会玩的人那样：
  - **E → Q**：AI 想用 Q 扑一个敌方英雄、E 好了、远祖嗥叫没开着、那名英雄在 E 的施放距离内：先替它按 E（减伤开着扑进去）。主包数据里 Q 咬中时远祖嗥叫开着就**立刻嚎叫**——恐惧落在他扑到的地方（英雄联盟里 E、Q、再按 E 的连招）。
  - **R → Q**：无尽束缚压住英雄、连抓三下（这期间他在压制的动作里，钩子不动），动作一结束、Q 好了，就替 AI 朝 Q 够得着的、生命比例最低的敌方英雄按 Q——压制完马上接一口撕咬。R 放出后 `r_dur` + `r_sup` + 40 tick 内算。
  - **鲜血追猎**：R 好了、`r_cast` 内有生命低于 25% 的敌方英雄、往他扑过去路上第一个英雄就是他：替 AI 按 R 追残血；AI 想用 Q 咬小兵 / 野怪，而 Q 够得着的地方有生命低于 50% 的敌方英雄：改成咬那名英雄。
  - 被控住、正在放技能（施法动作）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

数字：被动 `league_warwick:hunt` 的参数写在英雄数据的 `passive.params`，由 `make_override.py` 从 `tools/kit/build_warwick.py` 的参数表 `P` 写入；单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.179 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_warwick` 文件夹放进 `<游戏目录>\mods\`（要有 `league_warwick.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看沃里克的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_warwick.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Warwick (player 0, team 0), ...`：出生；
   - `HEAL #1: Eternal Hunger on ... at 42% health - healed 20`：残血吸血；
   - `HUNT #1: level 0 -> 1 (the weakest champion in reach at 47%)`：鲜血追猎开始、换成三倍、结束；
   - `E FIRST: the guard up before the bite ... - e on ...`、`R THEN Q ...`、`R HUNT ...`、`Q TO PREY ...`：替 AI 按的连招。

## 开发

- `python addons/league_warwick/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的沃里克和参数表一致）。主包的沃里克改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_warwick`：单元测试（吸血的三档、追猎的三档、参数、和参数表一致，连招的 E → Q、R → Q、追残血）。
- 在 `addons/` 下 `cargo build --release -p league_warwick`（Windows）得到 `target/release/league_warwick.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
