# 韦鲁斯枯萎附加包（测试版 v0.1.2，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里韦鲁斯的「枯萎」叠在被他普攻打中的人身上，Q、E、R 打中谁就引爆谁身上的层数。主包是纯数据，读不到目标身上的层数：层数记在韦鲁斯自己身上（同卡莎的被动），打 A 叠的层会在 B 身上引爆。**不装这个附加包，主包的韦鲁斯也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 枯萎记在哪里 | 韦鲁斯身上（一共最多 3 层） | 每个敌方英雄自己身上（各最多 3 层，6 秒） |
| 引爆 | Q、E、R 打中英雄时按他自己的层数，每层 3% 最大生命真实伤害 | 按被打中的那个人身上的层数，数字一样 |
| 引爆返还冷却 | 每层 13%（冷却倍率，R 也一起压） | 每层把 Q、E 的剩余冷却减 13%，不压 R |
| R | 引爆后再叠满 3 层 | 一样（叠在被锁住的人身上） |
| R 的扩散 | 在第一个人的位置扩散一次：周围的敌方英雄禁锢 1.5 秒（头上的三个点只是画面） | 被扩散到的人也真的叠满 3 层；腐化再从每个新禁锢的人身上向 55000 内没感染过的敌方英雄扩散（每一跳 0.5 秒），直到没有新目标 |

## 怎么做的

- `mod.override_info` 把韦鲁斯换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：普攻的叠层梯子（`league_varus_b_3` .. `1`）换成原生效果 `league_varus_blight:stack`，Q 的 4 处、E 的 1 处引爆梯子换成 `:pop`，R 的换成 `:pop_r`，R 的「叠满」换成 `:fill`；普攻的说明开头加【附加包】。
- 原生效果在命中时由数据调用，`input` 就是被打中的人：层数存成他身上的 buff（`league_varus_blight_1` / `_2` / `_3`，360 tick），叠层、引爆时播主包的层数画面、引爆画面和声音；引爆伤害是 `Fixed`（真实伤害，同主包）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_varus_blight` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 韦鲁斯普攻的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_varus_blight.log`：`Stack #n on #7: 1 -> 2 stacks`、`POP #n on #7: 3 stacks, 180 true damage, Q/E cooldowns -39%`。整个游戏一个计数：你看的那场每条都记，服务器的预模拟先记 150 行、之后每 25 行记一行（0.1.1：以前你看的那场也一样限，预模拟先把条数用完）。

## 开发

- `python addons/league_varus_blight/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里韦鲁斯改了就重跑。
- `cargo test -p league_varus_blight`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。

## 0.1.2：大招的腐化反复传染（2026-11-14）

用户看了「和英雄联盟不一样的地方」清单后说「全改吧」。英雄联盟的腐败锁链会一直传染到没有新目标；主包只在第一个人的位置扩散一次（数据认不出谁已经被感染过）。

- 副本（`make_override.py`）：扩散区 `league_varus_r_spread` 打到的每个英雄，原来的禁锢、画面、声音换成原生效果 `league_varus_blight:spread`；脚本核对这个区域和 `src/lib.rs` 的 `SPREAD_T` 30 / `SPREAD_R` 55000 / `ROOT2` 90 一致，主包改了会停下来。
- `:spread`：身上没有感染记号 `league_varus_blight_inf`（360 tick）的英雄——禁锢 `ROOT2` tick（`apply_cc` Bind，挂主包的 `league_varus_r_bind`），播主包被扩散到的画面和声音，叠满 3 层枯萎（主包的扩散只画了三个点），记上记号，排一个 `SPREAD_T` tick 后的 `:chain`。
- `:chain`：从这个被感染的英雄站的地方，向 `SPREAD_R`（加身体半径）内没感染过、选得中的敌方英雄再扩散一次（有新目标才播扩散的画面），每个新目标同上；没有新目标就停。
- `:fill`（大招打中的第一个人）也记上感染记号：他不会被自己的扩散再禁锢一次（主包里那一下和他自己的禁锢同时结束）。
- 大招的说明指到本包的 `description.league_varus_blight.ult`（主包的说明后面加一句）。

扩散不带伤害、每一跳 0.5 秒，是主包的节奏（英雄联盟每一跳 2 秒、带同样的伤害），没有改。日志 `SPREAD #n: 1 champion(s) infected (#id)`、`CHAIN #n: 2 champion(s) infected from #id`。测试 `the_corruption_goes_on_to_the_ones_not_yet_infected`、`the_spread_is_the_main_packs`。
