# 参与击杀附加包（测试版 v0.3.1，可选）：金克丝、崔丝塔娜、易、图奇

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里这四人「击杀后」的效果都按**参与击杀**算（击杀和助攻）。主包是纯数据，只认得出他们自己打出的最后一击（league_jinx 的击杀检查），助攻看不见。易还有两处数据做不到：普攻减阿尔法突袭的冷却、无极剑道期间免疫减速。**不装这个附加包，主包的四人也是完整的**。

| 英雄 | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 金克丝 | 罪恶快感：亲手击杀英雄后 | 每一次英雄击杀和助攻（几个人同时阵亡也各算一次） |
| 崔丝塔娜 | 火箭跳跃：她击杀敌方英雄（或满层引爆炸弹）时刷新 | 每一次英雄击杀和助攻都刷新（满层引爆照旧） |
| 易 | 无极剑道期间阿尔法突袭、冥想的冷却加快 40%（近似） | 每一次英雄击杀和助攻，阿尔法突袭和冥想的剩余冷却减 70%，无极剑道开着时再延长 4 秒；每次普攻阿尔法突袭冷却减 1 秒；无极剑道期间免疫减速 |
| 图奇 | 埋伏：他击杀敌方英雄时刷新；E 毒性爆发：最近打中英雄 3 次后、或毒桶落地后就引爆 | 埋伏助攻也刷新；E 等到有人满 6 层毒、或这一爆能毒死人才引爆（v0.3.0），条件一满足下一箭就爆（v0.3.1） |

## 怎么做的

- `mod.override_info` 把四人换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成，先核对 `src/lib.rs` 里的名字和数字和主包一样：
  - **金克丝**：去掉三处击杀检查（普攻和火箭的替身投射物、大招火箭里的检查），不然她自己的击杀会算两次；
  - **崔丝塔娜**：原样（她自己的击杀检查留着，去掉的是同一个冷却标记）；
  - **易**：无极剑道去掉主包近似用的「冷却加快 40%」；
  - **图奇**：他自己的击杀检查留着；E 的 5 处引爆检查（读他的打中次数 `league_twitch_h3`、毒桶 68 tick 后的那一次）改读 `league_takedowns_tw_e_go`，每次普攻开头也读它（v0.3.1：那 5 处只在固定时刻读，标记那时多半没挂，游戏里 E 几乎不爆）；每一层毒（`AddCasted Poison`，18 处）旁边多调用原生效果 `league_takedowns:twitch_venom`，在中毒的英雄身上数层数（`league_takedowns_tw_v1`..`v6`，6 秒）；
  - 改过的说明开头加【附加包】。
- 四人各挂一个被动：`league_takedowns:jinx` / `:tristana` / `:masteryi` / `:twitch`。
  - `on_kill`（死的是英雄）和 `on_assist` 时：
    - 金克丝：照主包加上罪恶快感的四个 buff（攻速 25%、三段移速），播主包的画面和音效；
    - 崔丝塔娜：去掉火箭跳跃的冷却标记 `league_tristana_w_cd`，播「就绪」画面；
    - 易：`entity_reduce_cooldown` 减两个技能剩余冷却的 70%，无极剑道的 buff 重新挂上、多 240 tick；
    - 图奇（只在 `on_assist`，击杀由主包自己刷新）：Q 还在冷却就清零，播主包的刷新画面和声音 `league_twitch_q_reset`；`on_update`：E 不在冷却时，120000 内有英雄满 6 层、或层数 × (6 + 16% 攻击力) 按护甲折算后打得死他（算上护盾），就挂 30 tick 的 `tw_e_go`；看到主包的爆发标记 `league_twitch_e_pop` 就把层数清零（引爆本身还是主包的，每层毒各结算一次），记一行 `TWITCH E POP`。
  - 易的 `on_attack`：阿尔法突袭冷却减 60 tick；`on_update`：无极剑道期间去掉他身上所有降低移速的 buff。
- 状态都在被动自己的对象里，游戏 0.6.4 同时跑的两份预模拟各算各的。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_takedowns` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 金克丝普攻、崔丝塔娜 E（火箭跳跃）、易 R 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_takedowns.log`：`JINX EXCITED #n (assist)`、`TRISTANA W RESET #n (killed #7)`、`YI TAKEDOWN #n (assist): Q 300 -> 90, W 400 -> 120, Highlander extended`、`TWITCH E GO #n`（标记挂上）和 `TWITCH E POP #n: stacks [..]`（真的引爆了）。

## 开发

- `python addons/league_takedowns/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。三人在主包里改了就重跑。
- `cargo test -p league_takedowns`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
