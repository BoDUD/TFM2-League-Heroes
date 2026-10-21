# 维克兹附加包（测试版 v0.1.0，可选）

**不装这个附加包，主包里的维克兹也是完整的**：普攻发射虚空能量、每第 3 下撕开虚空裂隙；Q 等离子裂变打中后在命中点周围分裂爆炸；
E 构造分解炸开一片地面击飞敌人；R 生命形态瓦解射线引导 2.5 秒，对被研究的英雄造成真实伤害；被动有机体解构技能叠 3 层造成真实伤害。
主包是纯数据：**数据只读得到施法者自己身上的 buff**，所以主包把层数记在维克兹身上（连中不同的英雄也会叠到第 3 层）；**数据也不能让
投射物拐弯**，所以 Q 的分裂是命中点周围的一圈爆炸。这个附加包用原生代码把英雄联盟的做法做出来（用户 2026-10-20：技能方案 A、中单、做附加包、
「有连招要做连招」）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 有机体解构 | 层数记在维克兹身上，第 3 下打中的英雄受到真实伤害 | **层数记在每个敌方英雄身上**（每层 7 秒，再中一下全部刷新），第 3 层对那个英雄造成真实伤害；每叠一层都「研究」他 7 秒 |
| Q 等离子裂变 | 命中点周围 26000 内的敌人受到分裂伤害和减速 | 命中点的**左右两边各射出一颗分裂弹**（垂直于飞行方向，从命中点旁 12000 起飞 55000 远），打中第一个敌人：伤害、减速，英雄还叠层并打开 Q -> W 的窗口 |
| R 生命形态瓦解射线 | 他身上有研究标记（任何英雄被研究）时，射线对谁都是真实伤害 | 只有**被他研究过的英雄**受到真实伤害，其他敌人魔法伤害；每 3 波叠一层 |
| 连招 | 数据里的窗口：E 击飞英雄后 Q 快速飞向被控的英雄、普攻马上开裂隙；Q 打中英雄后普攻开两道裂隙；没研究任何英雄时 R 不放 | AI 钩子按顺序：**E -> Q**（AI 要 Q 英雄时先 E）、**击飞后马上 Q**、**窗口里的普攻打英雄**（裂隙打在他身上）、**两层的英雄在射程里就放 R**、R 先射被研究的英雄 |

## 怎么做的

- `mod.override_info` 把主包的维克兹换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_velkoz.py` 的 `native=1` 生成，主包的
  维克兹改了就重跑）：被动是本包的 `league_velkoz:research`（数字在 `passive.params`，只记参数和写日志）；每处叠层换成
  `league_velkoz:deconstruct`，Q 的分裂换成 `league_velkoz:fission`，R 每一波的伤害线换成 `league_velkoz:ray`（射线的画面照旧是主包从眼睛
  射出的那根）；普攻、Q、R 的说明开头加【扩展包】。
- **层数**：`entity_stack_buff` 在英雄身上叠 `league_velkoz_pd_<维克兹的编号>`（最多 3 层、每次刷新时长），第 3 层清掉、
  `deal_damage_typed(Fixed)`；研究是英雄身上的 `league_velkoz_rs_<编号>`，同时刷新维克兹身上的 `league_velkoz_p_res`（主包数据的 R 读它）。
  两个维克兹各算各的。
- **分裂弹**：`spawn_projectile` 的直线弹 `league_velkoz_q_split_bolt`（主包的 Q 弹图），命中时跑 `league_velkoz:split_hit`。
- **连招**（`src/combo.rs`）：`add_player_input_ai`，优先级 110（排在 league_ult_press 之后），被控住或正在放技能时不动；R 只在他有
  `p_res` 时按（没有时 R 的格子是空的，按了白白进冷却）。
- 游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列，下一次 on_update 之前才扣血（莉莉娅 0.1.2 的教训）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_velkoz.log`：`SPAWN`、`STACK` / `BURST`（被动）、`SPLIT` / `SPLIT HIT`（Q 分裂）、
  `RAY`（射线一波）、连招（`E FIRST`、`Q AFTER E`、`RIFT`、`R ON STACKS`、`R RESEARCHED`）、`WATCH`（每 30 秒的计数），都限了条数。

## 在游戏里测

1. 主包（League of Legends Heroes 0.182.0 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_velkoz` 文件夹放进 `<游戏目录>\mods\`（文件夹里要有
   `league_velkoz.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，鼠标停在维克兹的技能上，说明开头是【扩展包】就说明副本生效了；打一局后看日志里的 STACK / BURST / SPLIT / RAY 和连招。

## 重新生成

```
python addons/league_velkoz/make_override.py
cd addons && cargo test -p league_velkoz && cargo build --release -p league_velkoz
```

## 游戏 0.6.5（0.1.1）

连招钩子回城时不出手；R 的引导不朝 AI 正在远离的人放（站着引导，撤退时放会被追上），E 之后的 Q 照放（`league_ult_press` 0.5.0 的规则，0.6.5 的官方 AI 自己决定回城、撤退）。
