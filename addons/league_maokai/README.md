# 茂凯附加包（测试版 v0.1.1）

用户：「全按推荐做：辅助、布局A、做扩展包、PPU 1.2、加高手连招」。主包 `league` 的茂凯是纯数据，不装这个包也完整可玩；
这个附加包用原生代码补数据做不到的三件事：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 吸元秘术回血 | 固定值 + 法术强度（数据读不到生命） | 按等级回复最大生命的 4.5%–12%（英雄联盟） |
| 吸元秘术就绪 | 他的技能命中敌人后 | 他的技能命中敌人后，**或被敌方英雄的技能打中后**（近似：打他的敌方英雄的技能、技能 2 或大招在 1.5 秒内刚进入冷却，就算技能打中——原生被动收到伤害时分不出普攻和技能） |
| 草丛里的树苗 | 和别处一样（数据读不到地形） | 读地图的草丛格子；立在草丛里的树苗爆炸半径更大（34000）、伤害 ×1.6、减速 45%（英雄联盟草丛里的树苗更强） |

- **怎么换上**：`mod.override_info` 把主包的茂凯换成 `override/league_maokai.data_champion`（`make_override.py` 用
  `tools/kit/build_maokai.py` 的 `native=1` 生成：技能一字不改，被动换成本包的 `league_maokai:sap_magic`，普攻的吸元秘术不再由数据回血、
  改成挂 3 tick 的 `league_maokai_sap_on` 交给本包；树苗多一份「在草丛里」的爆炸，读本包挂的 `league_maokai_e_brush`）。
- **找树苗**：原生接口里的弹道没有名字，本包把他自己留下、原地超过 20 tick 不动的区域当成树苗（他别的弹道都在飞）。
- **草丛**：同 league_nidalee 的 `bush.rs`（雷恩加尔的读法）。单独安装时本包自己注册读图钩子；在合集 `league_addons` 里由合集的
  `MapReaders` 调用。
- **按键**：本包不按任何技能键（只有被动），碰不到「低等级按技能让游戏 AI 卡死」的问题。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_maokai.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  `HEAL`（回了多少）、`STRUCK`（被哪名英雄的哪个技能打中、充好吸元秘术）、`SAPLING`（树苗立在哪、在不在草丛）、`BUSHES`（这场的草丛格子）。
  `HEAL`、`STRUCK`、`SAPLING` 整个游戏一个计数：你看的那场每条都记，服务器的预模拟先记 40 条、之后每 50 条记一条（0.1.1：以前你看的
  那场也一样限，预模拟先把条数用完）。

## 命令

- `python addons/league_maokai/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的茂凯和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_maokai`：单元测试（参数、按等级回血、「刚放过技能」、原地不动的区域、草丛格子、副本）。
- 在 `addons/` 下 `cargo build --release -p league_maokai`（Windows）得到 `league_maokai.dll`；`league_addons` 合集也会编进本包。
