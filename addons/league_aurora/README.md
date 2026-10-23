# 阿萝拉附加包（`league_aurora`）

用户（2026-10-23）选技能方案时定了：「W 灵纱洞开并入被动：残血时跳开 + 隐身 + 加速（有冷却）」。

主包的阿萝拉是纯数据：数据读不到生命，所以主包里的灵纱洞开只看「有敌方英雄贴身」（`w_near` 内）就后跳。这个附加包按她真实的生命来：

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 灵纱洞开（并入被动） | 普攻或怪奇喷涌开头，`w_cd` 过了、`w_near` 内有敌方英雄，就往后跳开、隐身 `w_inv` tick、加速 `w_ms`% | 同样的跳法，但还要她**生命低于 `w_low`%**（默认 35%），英雄联盟「残血时跳开」 |

## 怎么接上的

`mod.override_info` 把主包的阿萝拉换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_aurora.py` 的 `native=1` 生成）：

- 灵纱洞开的判断多读一个标记 `league_aurora_low`；
- `passive` 是本包的 `league_aurora:veil`，参数 `w_low` 来自主包参数表 P：每 tick 读她的生命，低于 `w_low`% 就挂上 3 tick 的 `league_aurora_low`（先摘再挂，只留一个），回血后 3 tick 自己消失；
- 普攻的说明换成附加包自己的文字（`description.league_aurora.attack`，写着生命低于多少才跳），游戏里看说明就知道副本有没有生效。

计时在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。

## 检查

- 在 `addons/` 下 `cargo test --release -p league_aurora`：单元测试（参数、残血的界线、标记的名字）。
- 主包的阿萝拉改了以后重新跑 `python addons/league_aurora/make_override.py`（它先核对主包的 `league_aurora.data_champion` 和参数表一致、`src/lib.rs` 的默认参数和 P 一致）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aurora.log`：`SPAWN`、生命掉到界线以下 `LOW`、回到界线以上 `UP`。
