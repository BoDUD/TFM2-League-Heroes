# 沃利贝尔附加包（测试版 v0.2.0）

用户：「上单，方案 A，做附加包」。主包 `league` 的沃利贝尔是纯数据，不装这个包也完整可玩；这个附加包用原生代码补数据做不到的四件事
（都照英雄联盟）：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 狂雷渐起的闪电（满 5 层） | 一道飞向目标的闪电，路上和目标身边 22000 以内的敌人都受伤 | 打**目标和离它最近的 4 个敌人**（22000 以内，防御塔不算），每个身上闪一下 |
| 暴怒撕咬的标记 | 标记记在沃利贝尔自己身上：下一口咬**谁**都算第二口；第二口回固定值 + 攻击力加成 | 标记记在**被咬的那个英雄**身上（8 秒）：再咬**同一个人**才是第二口；第二口回复再加**已损失生命的 12%** |
| 天声震落 | 落地砸地、减速、加生命 | 另外让落点 55000 以内的**敌方防御塔 4 秒不能攻击**（塔身上缠着电光） |
| 天声震落后的 12 秒风暴形态 | 身后有雷云，他本身的颜色不变 | 他整个人变成**雷电蓝**：白毛变浅电蓝、腿变深蓝，符文和冰晶爪子发亮青光，外圈一道电蓝描边；形态结束或阵亡时变回来 |

- **怎么换上**：`mod.override_info` 把主包的沃利贝尔换成 `override/league_volibear.data_champion`（`make_override.py` 用
  `tools/kit/build_volibear.py` 的 `native=1` 生成：技能、时机一字不改；满层的闪电换成原生效果 `league_volibear:storm`，撕咬咬中英雄时
  换成 `league_volibear:maul`，大招落地另加 `league_volibear:stormbringer`）。本包没有被动，只有这三个原生效果。
- **画面**：闪电打到的人、第二口回血、失效的塔都是本包加的 buff（`league_volibear_p_zap`、`_w_healed`、`_r_tower`），副本的
  `view_buffs` 按名字给它们配了主包的 `p_hit`、`w_heal`、`r_tower` 特效。
- **风暴形态的颜色**（0.2.0，用户 2026-10-30：「沃利贝尔开大是不是得搞个变色啊」，三份草稿里选了「2 雷电蓝+描边」）：主包的
  沃利贝尔图里每个动作都有一个 `r_` 双胞胎（[`tools/art/volibear_storm.py`](../../tools/art/volibear_storm.py)：他自己的帧逐格换成
  风暴的颜色，帧数、时长、大小一样）。`src/view.rs` 挂在游戏的显示更新上（game_places::hook，照芸阿娜的超凡形态）：他身上有主包的
  风暴形态 buff（`league_volibear_r_form`，落地起 12 秒）时，正在播的待机、走、普攻、撕咬、Q、E、R、挨打换成 `r_*`，buff 没了换回来。
  主包里出招的动作数据能换、待机和走换不了，所以主包干脆不变色（免得出招时蓝、站着时白地来回闪）。只在游戏 0.6.4 起的 Windows
  版上生效，别的版本退回主包那样。
- **按键**：本包不按任何技能键，碰不到「低等级按技能让游戏 AI 卡死」的问题。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_volibear.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  `STORM`（闪电打到谁）、`MAUL`（标记 / 第二口回了多少）、`TOWER`（哪几座塔失效）、`FORM`（画面上换成 / 换回风暴形态的颜色）。

## 命令

- `python addons/league_volibear/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的沃利贝尔和参数表一致、
  `src/lib.rs` 的常量和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_volibear`：单元测试（闪电找最近的 4 个、第二口的伤害和回复、buff 名长度、副本、
  风暴形态换的动作名、这些动作和它们的 `r_` / `hd_r_` 帧都在图里）。
- 在 `addons/` 下 `cargo build --release -p league_volibear`（Windows）得到 `league_volibear.dll`；`league_addons` 合集也会编进本包。
