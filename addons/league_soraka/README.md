# 索拉卡附加包（v0.1.0）

主包 `league` 保持纯数据。用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」，再说「接着做」（能做的小项都做）。英雄联盟的祈愿（R，wiki："increased by 50% on targets below 40% of their maximum health"）给生命低于 40% 的友军多回复 50%；数据读不到任何人的当前生命，主包只能给每个人一样多。这个附加包用原生代码按生命补上这一半：

| | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 祈愿（R） | 全图所有友方英雄（包括她自己）各回复 220 + 60% 法强 | **生命低于 40% 的多回复 50%**（110 + 30% 法强，合计 330 + 90%）：落下那一刻读每个人的生命，别的人照旧 220 + 60% |

## 怎么做的

- 副本（`override/`，`make_override.py` 从主包的 `league/champion/league_soraka.data_champion` 生成）和主包一样，只在大招那一圈治疗的最前面加了本包的原生效果 `league_soraka:wish`：圈里的每个友方英雄先过这一步，再吃主包的治疗，所以读到的是治疗之前的生命。
- `wish`：这个人的生命低于最大生命的 `LOW_HP`%（40%）就用 `heal` 多回复主包那一下的 `BONUS`%（50%），头上多一个绿色数字；不低的什么都不做。法强读的是索拉卡施放时的。
- 主包那一下的数值（`HEAL` 220、`HEAL_AP` 60%）写在 `src/lib.rs`，`make_override.py` 和单元测试核对副本里的治疗是不是这个数，主包改了就停下。
- AI 的打分不变：多回复的那一半不在数据里，AI 照旧按主包的治疗量估这个大招。

## 在游戏里测

1. 主包（League of Legends Heroes 0.354 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_soraka` 文件夹放进 `<游戏目录>\mods\`（要有 `league_soraka.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看索拉卡的大招说明：开头是「【附加包】」、最后一句是「生命低于40%的多回复50%」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_soraka.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：`WISH`：谁在祈愿落下时生命低（生命 / 最大生命、百分比），多回复了多少。

## 开发

- `python addons/league_soraka/make_override.py`：从主包重新生成 `override/` 和 `text/`（`--check` 只比较，CI 用）。主包的索拉卡改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_soraka`：单元测试（40% 的界线、多回复的量是主包那一下的一半、副本在主包的治疗前面调本包、主包的数值没变）。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
