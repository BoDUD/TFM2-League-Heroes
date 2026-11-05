# 卡西奥佩娅附加包（测试版 v0.1.2）

0.1.2（2026-11-05，彩蛋「蛇女不需要鞋」）：英雄联盟的卡西奥佩娅没有脚、不能买鞋，移速随等级成长（主包一直给她更高的移速成长 `ms_g` 16，别的法师 9）。游戏本身不卖鞋，鞋来自第三方装备 mod（11-04 的日志里有 `boots`、`berserkers_greaves`、`plated_steelcaps`、`sorcerers_shoes`、`ionian_boots_of_lucidity`、`gluttonous_greaves`）。本包加了装备构筑钩子（`StableItemBuildHook`，游戏给每个 AI 选手定这一局出哪些成装时调用）：只管她，鞋（名字里有 boots / greaves / shoes / treads / steelcaps / soles / lucidity 等，`radiant_` 升级版也算）的分数压到最低；引擎挑的成装里还是有鞋，就换成同一档里还没出的别的装备（法强的先）。被动每半秒看一次她身上的装备：还是买了鞋（钩子被别的 mod 盖掉了），就把鞋的属性 buff 摘掉（没有脚穿不上；鞋还在装备栏里、钱也花了），第一次记一行 `BOOTS`。普攻说明里的「优雅蛇行」加上「不能买鞋」。看日志的 `BUILD`（成装里的鞋换掉了）和 `BOOTS`（摘了鞋的属性：应该一行都没有）。

0.1.1（2026-11-05）：待命式大招没用掉时的冷却退还从来没生效过：n tick 的待命标记只有 n - 1 tick 看得见（经典 SDK 探针 lr1105/fix_j：n - 1 之前 148/148 次看得见，第 n tick 0 次），退还在窗口最后一 tick 读它时已经没了，所以每次待命过期都要等完整冷却（塞恩追踪：过期到再待命 3558 tick，改读后 877）。现在在窗口结束前 3 tick 读（`tools/kit/build_cassiopeia.py`），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

用户：「技能方案按 A 做（带扩展包 league_cassiopeia）」。主包 `league` 的卡西奥佩娅是纯数据，不装这个包也完整可玩；这个附加包用
原生代码补数据做不到的三件事：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 双生毒牙的加伤和回血 | 她的 Q、W 毒到任何敌人后 3 秒内，毒牙都加伤、回血（数据读不到目标身上的毒） | 只有**这个目标本人中毒**时才加伤、回血（英雄联盟） |
| 石化凝视 | 扇形里近处（交战中）的英雄石化，远处的减速（数据看不到朝向） | **面朝她的石化，背对她的减速**（英雄联盟） |
| 优雅蛇行 | 移速成长更高；第三方装备 mod 的鞋照买（数据管不了装备） | **不买鞋**：装备构筑钩子把鞋从她的成装里换掉（英雄联盟） |

- **怎么换上**：`mod.override_info` 把主包的卡西奥佩娅换成 `override/league_cassiopeia.data_champion`（`make_override.py` 用
  `tools/kit/build_cassiopeia.py` 的 `native=1` 生成：技能、时机一字不改；Q、W 毒到的单位身上多挂一个标记
  `league_cassiopeia_poison`；毒牙的加伤回血换成原生效果 `league_cassiopeia:fang`；凝视对每个敌方英雄的石化或减速换成
  `league_cassiopeia:gaze`；被动换成本包的 `league_cassiopeia:venom`）。
- **朝向怎么来的**：游戏里人物只朝左或朝右。被动每 3 tick 看一次每个敌方英雄：横向走了 300 以上就按走的方向记朝向；站着不动
  30 tick 以上就记成朝向离他最近的对手英雄（站着打人时人物转向目标）；记在他身上的隐藏 buff `league_cassiopeia_face_l`（朝左）。
  离她横向不到 3000 的算正对她。
- **按键**：本包不按任何技能键，碰不到「低等级按技能让游戏 AI 卡死」的问题。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_cassiopeia.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  `FANG`（毒牙加成）、`GAZE`（石化或减速、朝向）、`BUILD`（成装里的鞋换掉了）、`BOOTS`（她还是买了鞋，属性摘掉了）。

## 命令

- `python addons/league_cassiopeia/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的卡西奥佩娅和参数表一致、
  `src/lib.rs` 的常量和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_cassiopeia`：单元测试（毒牙数字、朝向、副本）。
- 在 `addons/` 下 `cargo build --release -p league_cassiopeia`（Windows）得到 `league_cassiopeia.dll`；`league_addons` 合集也会编进本包。
