# 斯卡纳附加包（`league_skarner`）

用户（2026-10-26）：斯卡纳「和英雄联盟不一样的地方要做附加包」——和特朗德尔、瑟庄妮、克烈、约里克一样。

主包的斯卡纳是纯数据：数据读不到「目标身上有几层」、看不到墙，也不能把人摆在他身边，所以主包里有三处只能近似。这个附加包把它们做成英雄联盟的样子：

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 战栗 | 层数记在**斯卡纳自己身上**（换了目标也接着数），满 3 层让打中的英雄战栗：每秒最大生命 `p_pct`% 的**真实伤害** | 层数叠在**每个英雄身上**（按这个斯卡纳起名），满 `p_n` 层开始战栗：每 `p_p` 拍最大生命 `p_pct`% 的**魔法伤害**，战栗中不再叠层 |
| 以绪塔尔冲击 | 撞上英雄拖一段，**每次拖完都砸一下、晕** `e_stun` 拍 | 拖的路上**碰到墙才砸、才晕**（伤害 `e_wall_dmg` + `e_ratio`% 攻击力 + 最大生命 `e_wall_hp`%），没墙就只是拖走 |
| 毒刺贯体 | 尾巴扫过的线上**所有英雄**都中：物理伤害、压制（眩晕）`r_sup` 拍，每 3 拍往他身上拽一下 | 只压**最先碰到的 `r_n` 个英雄**：魔法伤害、压制 `r_sup` 拍，压制期间**每拍摆在他身边**（保持被打中时的方向，离他最多 `R_GAP`），他走到哪拖到哪 |

冲锋时穿过地形、拖完人出护盾和地震波（震地壁垒）、拖完人 Q 立刻转好、R 举着巨石先扔擎天、R 打中的英雄立刻战栗、巨石第三下 / 擎天打中英雄让 E 最多再等 `e_cut` 拍这些两边一样。

## 怎么接上的

`mod.override_info` 把主包的斯卡纳换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_skarner.py` 的 `native=1` 生成），`passive` 是本包的 `league_skarner:sovereign`，参数（`build_skarner.NATIVE_KEYS`）来自主包参数表 P，`src/lib.rs` 的常数和它核对：

- 副本的战栗叠层换成原生效果 `league_skarner:quake`：在目标身上叠 `league_skarner_qk_<他>`（`entity_stack_buff`，最多 `P_N` 层），满层挂 `league_skarner_qq_<他>`（战栗中）和画面 buff `league_skarner_p_quake`，按时排好每一下的魔法伤害（`queue_effect`）；
- 副本的冲锋撞上英雄时不推也不砸，换成 `league_skarner:impact`：沿他冲的方向查墙（卡蜜尔附加包的墙格），有墙就强制位移到墙边并挂 `league_skarner_ed_<他>` / `league_skarner_eg_<他>`，被动看到到达就打伤害、晕、播 `league_skarner_e_slam`；
- 副本的毒刺打中英雄时不打伤害、不眩晕、不拽，换成 `league_skarner:impale`：他身上的 `league_skarner_rc_<他>` 数这次打中第几个，前 `R_N` 个才打伤害、压制、战栗、挂 `league_skarner_rd_<他>`；被动每拍用 `entity_set_pos` 把它们摆在他身边（目标点在墙里就等着，不塞进墙里）。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_skarner`：单元测试（查墙、伤害数字、拖的位置、名字长度、副本用到了原生效果并且参数和常数一致）。
- 主包的斯卡纳改了以后重新跑 `python addons/league_skarner/make_override.py`（它先核对主包的 `league_skarner.data_champion` 和参数表一致、`src/lib.rs` 的常数和 P 一致；`--check` 只核对不写；文字接入前用 `--draft`）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_skarner.log`：`SPAWN`、`QUAKE`（叠层 / 战栗）、`IMPACT`（撞墙 / 没墙）、`WALL`（撞墙眩晕）、`IMPALE`（压制 / 超过 `R_N` 个）、`DRAG`（拖着走）。
