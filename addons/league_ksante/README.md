# 奎桑提附加包（测试版 v0.1.1，可选）

**不装这个附加包，主包里的奎桑提也是完整的**：普攻（被动血性本能：技能打中过的敌人，下一次普攻多一段伤害）、Q 无双陀斧（往前裂地减速，
两层后第三下的冲击波把敌人拉回来）、W 辟路先锋（顶着陀斧蓄力减伤、带护盾，然后冲撞击退晕眩）、R 傲岸雄姿（盾击撞飞，追上去砸地，进入
全盛姿态 15 秒）都在主包数据里，全盛时的出招也是全盛那一套动作（数据用 `CasterAnimation` 播 `ao_*`）。主包是纯数据：**待机、跑步、
挨打的动画不能在运行中换**，所以主包里全盛的他只在出招时是弓背半蹲、两根长棍拖地的样子，站着和走路还是普通姿态。这个附加包补上这一件事
（用户 2026-10-22：全盛姿态「单独一套」动作）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 全盛的样子 | 只在出招时是全盛姿态 | **整身换姿态**：全盛的 15 秒里站着、走着、挨打都是全盛姿态（`ao_idle` / `ao_run` / `ao_hit`），普攻第一下也是 |

## 怎么做的

- **不改数据**：本包没有副本，`mod.override_info` 是空的，主包的奎桑提原样。
- **整身换姿态**（`src/view.rs`）：照奎因 / 纳尔 / 奈德丽附加包的显示钩子，游戏每帧更新显示时，名字是 `league_ksante` 的实体身上有
  全盛 buff `league_ksante_ao` 时，把正在播的 `idle / run / hit / attack` 换成 `ao_*`（高清帧由 league.dll 自动换成 `hd_ao_*`）；
  全盛结束换回来。阵亡不换：全盛随死亡结束，倒下的是普通姿态。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ksante.log`：`FORM`（画面里换姿态，限了条数）和每 10 秒的显示统计。

## 在游戏里测

1. 主包（League of Legends Heroes 0.191.0 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_ksante` 文件夹放进 `<游戏目录>\mods\`（文件夹里要有
   `league_ksante.dll`、`mod.mod_info`、`mod.override_info`）。
3. 打一局让奎桑提放大招：全盛的 15 秒里他站着、走路也应该是弓背半蹲、长棍拖地；看日志里的 `FORM`。

## 全盛的生命上限（v0.1.1，2026-11-14）

用户看了「和英雄联盟不一样的地方」清单后说「全改吧」。英雄联盟（V26.20）的全盛：当前生命被压在「65% maximum health which cannot be modified nor exceeded by any means」，进入全盛时高于这条线的生命直接扣掉（「Upon entering All Out, his current health is reduced to this threshold if it is above it」），全盛结束后也不还。主包只有护甲魔抗 -25%，没有这一条：数据读不到当前生命；buff 的 `hp_mult` 试过（经典引擎里量过：-35% 时最大生命 1795 → 1166，当前生命 1723 → 1119 按比例缩，结束时又按比例长回来），不是这条规则。

- 本包加了比赛钩子 `Cap`：每 tick 身上有全盛 buff `league_ksante_ao` 的活着的英雄（塞拉斯偷来的全盛也算），生命高于最大生命的 65% 就设回这条线（`entity_set_hp`）。治疗照样有，只是加不过线。
- 单独装本包时它自己设比赛钩子；附加包合集里由 league_addons 的 `BundleMatch` 转发（一个模组只能有一个比赛钩子）。
- 主包的数据没改，`mod.override_info` 还是空的；说明里没有这一句（本包没有副本）。
- 日志 `CAP #n: All Out holds health at 65% - 1723 -> 1166 of 1795`。测试 `all_out_holds_health_at_65_percent`。

经典引擎跑不了原生代码；下一局看 `CAP` 行。
