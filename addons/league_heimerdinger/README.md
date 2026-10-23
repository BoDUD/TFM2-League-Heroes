# 黑默丁格附加包（测试版 v0.2.0，可选）

**不装这个附加包，主包里的黑默丁格也是完整的**：普攻和每第 3 次普攻的 W 海克斯科技微型导弹、Q H-28G 进化炮台（最多 3 座，
受控英雄挨光束）、E CH-2 电子风暴手雷、R 升级！！！（刷新 Q、E 并升级下一个够得着英雄的技能：Q 放 H-28Q 巨型炮台、E 连掷 3 颗 CH-3X 手雷、普攻射出导弹群，先来的那个）、被动海克斯科技亲和和连招
E → W 都在主包数据里。主包是纯数据：数据没有召唤物，炮台是落点上的周期区域，**伤害当场结算在目标身上，看不到炮弹从炮台飞出去**；
被动是炮台的光环区域，**只认他自己的炮台**（英雄联盟：炮台和己方防御塔旁都加速）。这个附加包用原生代码把这两件事做成英雄联盟的样子
（用户 2026-10-21「需要做附加包就做」「做附加包啊」）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 炮台的样子 | 正面朝镜头（数据不知道目标在哪边） | **侧面、炮口朝目标那边**（用户：「炮台改成侧面朝敌人」）：英雄联盟模型的侧面，PPU 1.75（用户：「灵活利用PPU 炮也可以调的清晰」，PPU 3 时又「炮太高清了 降低点像素」），朝左朝右两套 |
| 炮台出手 | 炮台的区域当场打中目标，目标身上冒命中特效 | 炮弹（`t_shot`）、充能光束（`t_beam_line`）、巨型炮台的等离子弹（`x_shot`）**从侧面炮台的炮口飞向目标，飞到才扣血** |
| 打谁 | 受控英雄 → 英雄 → 其他敌人，各区域里先轮到的那个 | 同样的顺序，每档里打**最近的** |
| 海克斯科技亲和 | 自己的炮台旁 +20% 移速 | 自己的炮台旁**或己方防御塔旁** +20% 移速 |
| R 的升级给谁 | 游戏的 AI 先按哪个就是哪个 | **敌方英雄扎堆就按 E**（CH-3X 砸人堆），不然按 Q（巨型炮台），Q 没好再按 E |

伤害、射程、出手节奏、炮台数量和寿命都和主包一样（参数表 P 的同一组数）。

## 怎么做的

- `mod.override_info` 把主包的黑默丁格换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_heimerdinger.py` 的 `native=1`
  生成，主包的黑默丁格改了就重跑；它也核对 `src/lib.rs` 里 `Params` 的默认值和参数表 P 一样）：炮台保留画面、音效和 a / b / c
  三个槽位，但没有区域；Q 放炮台和升级的 Q 放巨型炮台那一 tick 跑本包的 `league_heimerdinger:q` / `:x`；被动是本包的
  `league_heimerdinger:affinity`（数字在 `passive.params`）；加上三种炮弹的 `view_projectiles`（画在主包的 `league_heimerdinger_fx`
  里，主包没用）；Q 的说明开头加【扩展包】。
- **炮台朝哪边**：`:q` / `:x` 算出的方向往左时给他挂 `league_heimerdinger_t_face_l` / `_x_face_l`（30 tick），副本的隐形弹落地时
  据此画 `league_heimerdinger_turret_l` / `_apex_l`，否则 `_r`。这四张是主包里的特效表（hd.rs EFFECTS，PPU 1.75），由
  `tools/art/design_heimerdinger_side_turrets.py`（英雄联盟模型 70 度侧面渲染，黑白两底抠图，缩到 20 / 30 游戏像素 x 1.75，16 色
  平涂加分界线，颜色往正面造型靠）和 `tools/art/import_heimerdinger_fx.py`（同样的升起、炮口闪光、开火后坐、损坏，朝左是镜像）生成。
  炮口离炮台点的位置写在 `assets/source/heimerdinger/hd/side_muzzles.json`，`src/lib.rs` 的 `T_MUZZLE` / `X_MUZZLE` 照它（`make_override.py` 核对）。
- **炮台站在哪**：`:q` / `:x` 拿施法的输入（Q 的方向），和数据的隐形弹一样朝那边 `q_place` 远、`q_place / q_speed`
  tick 后站下，和数据放的炮台图是同一个点。原生效果按（这局的种子、模拟的来源、比赛、局、他的编号）把炮台交给被动。
- **出手**：站下 `t_first` / `x_first` tick 后第一发，之后每 `t_per` / `x_per`（和炮台图的炮口闪光对齐）。受控制（游戏
  `EnemyChampionInCC` 的六种：击飞、眩晕、禁锢、强制位移、恐惧、魅惑）的英雄挨光束，否则最近的敌方英雄，再否则最近的小兵、野怪
  （防御塔不打）。`spawn_projectile` 从炮台的点（往南挪到炮口的高度）飞向目标，到了用 `deal_damage_typed` 造成魔法伤害，
  播主包的命中画面和音效；巨型炮台的等离子弹再挂主包的 `league_heimerdinger_x_slow`。他阵亡后炮台照旧打到寿命结束（主包的区域也是）。
- **海克斯科技亲和**：他活着时每 `p_per` tick 看一次，自己站稳的炮台 `p_r` 内或己方活着的防御塔 `p_tr` 内，就换上主包的
  `league_heimerdinger_haste`（+`p_ms`% 移速 `p_t` tick，画面照旧）。
- **R 的升级给谁**（`src/combo.rs`，用户 2026-10-24 把 R 改成「升级下一个技能」）：AI 钩子 `league_heimerdinger:combo`（优先级 110，
  排在 league_ult_press 之后）在他身上挂着 `league_heimerdinger_upg` 时替游戏的 AI 按：E 好了、`e_range` 内有一名敌方英雄身边
  `re_r` 内还有别的敌方英雄 → 朝身边人最多的那名按 E（`E CLUMP`）；不然 Q 好了、`q_range` 内有敌方英雄 → 朝最近的那名按 Q
  （`Q APEX`）；Q 没好、E 好了 → 朝最近的按 E（`E ONE`）。被控住、正在放技能、回城时不管。

## 在游戏里测

1. 主包（League of Legends Heroes 0.205.1 以上）要装着并启用；本包随附加包合集 `league_addons` 一起装，或单独装。
2. 看日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_heimerdinger.log`：`SPAWN`（他出场和参数）、`PUT`（炮台站下的点和
   施法输入的种类）、`SHOT`（炮台出手打谁、炮弹还是光束、多少伤害）、`HASTE`（炮台旁还是塔旁加速）、`WATCH`（每 30 秒的计数）、`E CLUMP` / `Q APEX` / `E ONE`（钩子替 AI 按的）。
3. 看炮弹是不是从炮口飞出去、落在炮台图上的炮台是不是在打（`PUT` 的点该在炮台图下）。
