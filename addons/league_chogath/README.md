# 科加斯附加包（测试版 v0.1.0）

用户：「做附加包」「变大可以无限 加生命」。主包 `league` 的科加斯是纯数据，不装这个包也完整可玩；这个附加包用原生代码补数据做不到的两件事
（都照英雄联盟）：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 盛宴的层数 | 每吃死一个英雄叠一层（最大生命 +70、league.dll 把身体画大 15%），**死亡清空**（引擎死亡时清掉全部 buff） | **死后原样补回**，层数一局里只增不减 |
| 什么时候放盛宴 | AI 对「队伍刚打过的敌方英雄」放出，读不到当前生命，常常咬不死 | 读射程内敌方英雄的生命、护盾、免死和受到伤害的增减，**一口吃得死才放**（几个时吃生命 + 护盾最少的，AI 没想放也放）；吃不死时 AI 想放就改成普攻那个人 |

- **怎么换上**：`mod.override_info` 把主包的科加斯换成 `override/league_chogath.data_champion`（`make_override.py` 用
  `tools/kit/build_chogath.py` 生成：技能、时机一字不改，只挂上被动 `league_chogath:keep`，大招说明换成本包的）。AI 钩子
  `league_chogath:feast` 不用数据里的任何东西。
- **伤害怎么算**：照主包的数字——真实伤害 300 + 他最大生命的 5%，加法强 50% 的魔法伤害（主包先挂 100% 魔抗穿透，等于真实），
  再按目标身上的减伤 / 增伤 / 技能减伤折算（`league_darius_ult` 在经典引擎里量的公式）。
- **按键**：R 只在 5 级以后、冷却好了的时候按（引擎的「输入合法」不看冷却，league_pyke 的教训）。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_chogath.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  `STACK`（叠到第几层）、`DEAD` / `ALIVE` / `KEEP`（死亡、复活、补回几层）、`FEAST`（放了，目标的生命 + 护盾和这一口）、
  `FEAST HELD`（AI 想放但吃不死，改普攻）。

## 命令

- `python addons/league_chogath/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的科加斯和参数表一致、
  `src/lib.rs` 的常量和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_chogath`：单元测试（死后补回、一口吃不吃得死）。
- 在 `addons/` 下 `cargo build --release -p league_chogath`（Windows）得到 `league_chogath.dll`；`league_addons` 合集也会编进本包。
