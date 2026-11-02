# 薇恩附加包：圣银弩箭、恶魔审判撞墙（测试版 v0.2.0）

主包 `league` 保持纯数据。数据有两件事做不到英雄联盟的样子，这个附加包用原生代码补上：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 圣银弩箭 | 两层记在薇恩自己身上：她轮流打两个人也会凑满 3 下，在第三个被打中的人身上爆 | **同一个目标**连续挨 3 下才爆 |
| 恶魔审判 | 每一箭推完都晕一下（数据看不到墙） | 被推到**墙上**（地图的墙格、5v5 地图的四边）才再受 30 + 35% 攻击力的伤害并眩晕 1 秒；没撞墙只击退 |

- **圣银弩箭**：每一处判定（普攻、翻滚后的强化普攻、恶魔审判）先调用原生效果 `league_vayne_bolts:bolt`：它数**被打中的单位身上**的层数
  （`league_vayne_bolts_s`，每层 3.5 秒，每次命中刷新），给薇恩加 3 tick 的标志：第 1 下 `league_vayne_sb_r1`（一环）、
  第 2 下 `sb_r2`（两环）、第 3 下 `sb_go`（清层，数据打出 50 真实伤害和爆裂；英雄再加 7% 最大生命值）；
  数据同一 tick 读一次标志，读不到在下一 tick 再读一次；英雄那部分 % 最大生命值的伤害改在命中后第 2 tick 读。
- **恶魔审判**（用户 2026-11-02：「薇恩要改成不E到墙壁不能眩晕」）：重箭的击退换成原生效果 `league_vayne_bolts:condemn`。它沿击退的方向
  查墙（卡蜜尔附加包的内置墙格，5v5 地图另加四边，和波比附加包的英勇冲锋同一套）：主包的击退（每 tick 3000、8 tick）路上碰到墙，就把人
  推到墙边、给薇恩加 `league_vayne_e_wall`，到墙的那一刻（`queue_effect` 排好的 `league_vayne_bolts:pin`）把他按在墙边；主包第 8 tick
  的撞墙伤害、眩晕、画面和声音只在薇恩身上有这个标志时打出。没碰到墙就照主包击退，不伤不晕。免控的人照旧推不动、不晕。
- **找墙放 E**（AI 钩子 `league_vayne_bolts:condemn`，`src/ai.rs`；用户：「找墙放E要智能一点」「参考卡密尔多智能」）：游戏的 AI 见人就放、
  不看墙（同样规则的波比英勇冲锋，11-01 的日志里大多数冲锋没碰到墙）。照卡蜜尔附加包钩墙的做法，钩子每 tick 记下敌方英雄的位置、
  算出速度；E 好了时，射程里每个敌方英雄预判重箭打到他那一刻（第 12 tick 出箭，再飞 距离 / 7000 tick）他走到哪（最多 24000，碰墙就停），
  他现在和预判的位置身后都有墙（推的路上），就替 AI 对他放 E：AI 正在打的人优先，再挑血量低的、墙近的。谁身后都没墙时：
  贴脸的敌方英雄（身体之间不到 8000），AI 要放 E 或者她血量低于 40% 时推开自保；AI 要放 E、这一箭打得死人的照放；
  别的时候 AI 想放 E 就留着，改打那个人，等墙。免控的人不算。AI 在放 Q、R 时不打扰。

## 在游戏里测

1. 主包 0.71 以上要装着并启用；本包已经编进附加包合集 `league_addons`（单独用时把 `league_vayne_bolts` 文件夹放进 `mods\`）。
2. 看薇恩普攻的说明：开头是「【圣银弩箭测试版】」、写着「对同一目标连续第 3 次命中」；E 的说明写着「撞到墙……才再受到」：说明换上了。
3. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vayne_bolts.log`：`bolt on #…: 1 stack(s) before -> Ring2` 等；
   `CONDEMN #… a wall 12000 away, there in 4 ticks`（撞墙）/ `no wall within 24000, knocked back, no stun`（没墙）；
   `PIN #… held 6 ticks for the slam`（按在墙边，接着数据的撞墙伤害和眩晕）；AI：`E WALL on …: a wall 9000 behind him`（找到墙放 E）、
   `E PEEL`（自保）、`E KILL`（收人头）、`E HELD`（没墙，留着 E 改普攻），一次按键记一行。

## 开发

- `python addons/league_vayne_bolts/make_override.py`：从主包的薇恩生成 `override/` 和 `text/`（主包的薇恩改了要重跑；主包的击退
  速度、tick 和 `src/lib.rs` 的 `E_KB_SPEED` / `E_KB_T` 对不上会停下）。
- 在 `addons/` 下 `cargo test --release -p league_vayne_bolts`；`cargo build --release -p league_vayne_bolts` 或 `-p league_addons`。
- 圣银弩箭的数据这一半在模拟器里测过（把 Native 换成立第 3 下 / 第 1 下的标志：每下都爆 / 只出一环）；恶魔审判和找墙的 AI 只有
  单元测试（查墙、推到墙边的速度和 tick、副本里没有数据的击退、预判走位、挑谁放 E），要在游戏里看日志。
