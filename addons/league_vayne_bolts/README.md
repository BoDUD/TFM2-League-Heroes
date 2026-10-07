# 薇恩圣银弩箭附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。数据分不清一次攻击打中的是谁，所以主包里圣银弩箭的两层记在薇恩自己身上：她轮流打两个人也会凑满
3 下，在第三个被打中的人身上爆。这个附加包用原生代码做成英雄联盟的样子：**同一个目标**连续挨 3 下才爆。

- 每一处圣银弩箭判定（普攻、翻滚后的强化普攻、恶魔审判）先调用原生效果 `league_vayne_bolts:bolt`：它数**被打中的单位身上**的层数
  （`league_vayne_bolts_s`，每层 3.5 秒，每次命中刷新），给薇恩加 3 tick 的标志：第 1 下 `league_vayne_sb_r1`（一环）、
  第 2 下 `sb_r2`（两环）、第 3 下 `sb_go`（清层，数据打出 50 真实伤害和爆裂；英雄再加 7% 最大生命值）；
- 数据同一 tick 读一次标志，读不到在下一 tick 再读一次；英雄那部分 % 最大生命值的伤害改在命中后第 2 tick 读。

## 在游戏里测

1. 主包 0.71 以上要装着并启用；本包已经编进附加包合集 `league_addons`（单独用时把 `league_vayne_bolts` 文件夹放进 `mods\`）。
2. 看薇恩普攻的说明：开头是「【圣银弩箭测试版】」、写着「对同一目标连续第 3 次命中」就说明换上了。
3. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vayne_bolts.log`：`bolt on #…: 1 stack(s) before -> Ring2` 等。

## 开发

- `python addons/league_vayne_bolts/make_override.py`：从主包的薇恩生成 `override/` 和 `text/`（主包的薇恩改了要重跑）。
- 在 `addons/` 下 `cargo test --release -p league_vayne_bolts`；`cargo build --release -p league_vayne_bolts` 或 `-p league_addons`。
- 数据这一半在模拟器里测过（把 Native 换成立第 3 下 / 第 1 下的标志：每下都爆 / 只出一环）。
