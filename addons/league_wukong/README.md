# 悟空附加包（测试版 v0.1.3）

用户：「技能方案按 A 做（带扩展包 league_wukong）」。主包 `league` 的悟空是纯数据，不装这个包也完整可玩；这个附加包用原生代码补
数据做不到的三件事：

| | 主包（纯数据） | 附加包 |
|---|---|---|
| 金刚不坏的回血 | 每层每秒回固定 2 点生命（数据读不到生命） | 每 5 秒回复最大生命的 0.35%，每层再多 0.35%（叠满 5 层 2.1%，英雄联盟） |
| W 的分身 | 分身的伤害照常，但画面放在锚点弹道的 `end_effects` 里，游戏里不显示（玩家看不到分身） | 本包在分身站的地方每格画一次：站着、出手，他开大时跟着转 |
| 放 W | 游戏的 AI 几乎总先按 E，W 一局只放几次（模拟里 10 分钟 4 次，第一次在 4 分多） | W 好了、射程内有敌方英雄时替他按（英雄联盟里 W 开团、接大招） |

- **怎么换上**：`mod.override_info` 把主包的悟空换成 `override/league_wukong.data_champion`（`make_override.py` 用
  `tools/kit/build_wukong.py` 的 `native=1` 生成：技能一字不改，被动换成本包的 `league_wukong:stone`，金刚不坏的五层只留护甲、
  不再带数据里的回血）。
- **怎么回血**：每 30 tick 数他身上主包的 `league_wukong_s_1` ~ `s_5`（最高的那层在几层就是几层），按「最大生命 × 0.35% ×（1 + 层数）
  × 30/300」回复，零头攒着下次一起回；满血时不回。
- **怎么画分身**（0.1.2，用户 2026-10-29：「猴子开大还是没分身啊」「现在分身都看不见」）：副本的 W 施放那一刻调本包的
  `league_wukong:clone`，把他站的地方写成他身上的一个 buff（`league_wukong_clone:x:y:tick`），被动下一拍读走；之后按主包的
  格子（`w_slot` tick 一格，第一格在施放后 2 tick）在那里放 `w_clone`，每 `w_period` 一次出手的那格放 `w_clone_atk`，他身上有
  `r_on`（在转大招）时放 `w_clone_spin`；他死了、`w_live` 没了、`w_t` 到了就停。伤害照旧是数据锚点的，副本里锚点的画面去掉。
  英雄联盟的做法：有分身时分身也开大，没有就只有本体转（10-29 上午那版「大招没分身时召一个」已去掉）。
- **替 AI 按 W**（0.1.2，`src/trickster.rs`，AI 钩子 `league_wukong:trickster`，排在 league_ult_press 之后）：W 已解锁并好了、
  W 射程（45000）加两人身体内有敌方英雄（他不在敌方塔下时，不挑塔下的）、他没被控、不在放技能、回城、转大招时，对最近的那个按
  W；这一拍 AI 自己要按技能或大招时不管。按之前一定查 W 解锁了（技能解锁前替 AI 按会让游戏的 AI 卡死）。
- **转棒时本体也转**（0.1.3，用户 2026-10-30：「猴子开大只有分身转 本体不转」）：本包的代码没改，副本跟着主包 0.268.0 重新生成。
  主包的转棒以前每一下都冲向目标，冲刺时画面上的强制动画停在当前那一帧，本体就一直停在 `spin` 的第一帧；现在身边 28000 内有
  敌方英雄就原地转，没有才冲过去（一下之内冲完），见主包的 `tools/kit/build_wukong.py`。
- **日志**：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_wukong.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
  `REGEN`（回了多少、几层）、`W PRESS`（替他按的 W，打谁、多远）、`CLONE`（分身站在哪）、`CLONE SPINS`（他开大时分身跟着转）、`CLONE GONE`（为什么散了）；预模拟
  限了条数，你看的那场每条都记。

## 命令

- `python addons/league_wukong/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的悟空和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_wukong`：单元测试（参数、英雄联盟的回血速度、副本、分身的交接和每格画面、W 打谁）。
- 在 `addons/` 下 `cargo build --release -p league_wukong`（Windows）得到 `league_wukong.dll`；`league_addons` 合集也会编进本包。
