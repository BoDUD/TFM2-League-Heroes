# 悟空附加包（测试版 v0.1.0）

用户：「技能方案按 A 做（带扩展包 league_wukong）」。主包 `league` 的悟空是纯数据，不装这个包也完整可玩；这个附加包用原生代码补
数据做不到的一件事：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 金刚不坏的回血 | 每层每秒回固定 2 点生命（数据读不到生命） | 每 5 秒回复最大生命的 0.35%，每层再多 0.35%（叠满 5 层 2.1%，英雄联盟） |

- **怎么换上**：`mod.override_info` 把主包的悟空换成 `override/league_wukong.data_champion`（`make_override.py` 用
  `tools/kit/build_wukong.py` 的 `native=1` 生成：技能一字不改，被动换成本包的 `league_wukong:stone`，金刚不坏的五层只留护甲、
  不再带数据里的回血）。
- **怎么回血**：每 30 tick 数他身上主包的 `league_wukong_s_1` ~ `s_5`（最高的那层在几层就是几层），按「最大生命 × 0.35% ×（1 + 层数）
  × 30/300」回复，零头攒着下次一起回；满血时不回。
- **按键**：本包不按任何技能键（只有被动），碰不到「低等级按技能让游戏 AI 卡死」的问题。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_wukong.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  `REGEN`（回了多少、几层）。

## 命令

- `python addons/league_wukong/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的悟空和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_wukong`：单元测试（参数、英雄联盟的回血速度、副本）。
- 在 `addons/` 下 `cargo build --release -p league_wukong`（Windows）得到 `league_wukong.dll`；`league_addons` 合集也会编进本包。
