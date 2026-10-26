# 拉露恩附加包（`tft_alune`）

用户（2026-10-26）：「要做附加包的地方你就做附加包」。

金铲铲包（`tft`）的拉露恩是纯数据，有三处做不到金铲铲里的样子，这个附加包补上：

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 月之降临 | 一枚碎片落在目标身上，其余落在射程里**随机**的敌人身上 | 落在离她**最近**的 `q_n` 个敌人身上（金铲铲的规则），每枚 `q_dmg` + `q_ratio`% 法强、月蚀印记（魔抗 -`q_shred`%） |
| 月曜降临 | 范围里每个敌人都挨满额的伤害 | 整颗月亮的伤害（含月相加成）× `r_split`% 由**命中的敌人平分**，每人最多 `r_cap`%：只砸中一个人时最痛 |
| 普攻 | 月环飞出去打中就没了 | 月环**飞回来**，穿过路上的每个敌人（`a_back_r`% 攻击力），打中的那个人回来时再挨一下 |

## 怎么接上的

`mod.override_info` 把金铲铲包的拉露恩换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_alune.py` 的 `native=1` 生成）：

- 月之降临只给她挂 2 tick 的 `tft_alune_q_go`（碎片交给本包）；
- 满月砸下来只给范围里的敌人挂 2 tick 的 `tft_alune_r_mark<月相>` 和眩晕，不扣血（伤害交给本包）；
- 普攻打中时给目标挂 2 tick 的 `tft_alune_a_mark`（回程交给本包，画面 `tft_alune_a_back` = 主包的月环）；
- `passive` 是本包的 `tft_alune:moon`，参数是 `build_alune.NATIVE_KEYS`。

每个计时都在被动自己身上（被动跟着单位、每局一份），不用全局变量。月环回程的伤害是本包注册的效果 `tft_alune:ring_back`（比例用默认参数）。

## 检查

- 在 `addons/` 下 `cargo test --release -p tft_alune`：单元测试（参数、最近的 3 个、满月分摊）。
- 金铲铲包的拉露恩改了以后重新跑 `python addons/tft_alune/make_override.py`（它先核对 `tft/champion/tft_alune.data_champion` 和参数表一致，`src/lib.rs` 的默认参数和 P 一致）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_alune.log`（`SPAWN`、每次 `MOONFALL`、每颗 `MOON` 的分摊、`RING` 回程）。
- 依赖金铲铲包 `tft` 0.2.0 起（拉露恩是在 0.2.0 加进去的；mod.mod_info）。附加包自己的说明文字在 `text/champion.i18n`（`make_override.py` 写，和金铲铲包同样的键，合并后游戏里看说明就知道副本有没有生效：每段开头是【附加包】）。
