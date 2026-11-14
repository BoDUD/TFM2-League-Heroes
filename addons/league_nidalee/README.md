# 奈德丽附加包（测试版 v0.1.5，可选）

**不装这个附加包，主包里的奈德丽也是完整的**：人形 / 美洲狮两种形态、按战况切换、标枪、夹子、治疗、推倒、猛扑、挥击和
5 级的猛扑猎杀都在主包数据里。主包是纯数据，有几件事做不到，这个附加包用原生代码补上：

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 变身后的样子 | 只有出招（普攻、推倒、猛扑、挥击、大招）是豹子的动作，待机、跑步、受击、阵亡还是人形（游戏按名字自动播这几个，数据换不了） | **整个身体**都是豹子（只在游戏 0.6.4 上，别的版本退回左边那样） |
| 寻觅（被动） | 标枪 / 夹子命中英雄：捕猎 4 秒、移速 +20% | 另外**在草丛里和离开草丛后 2 秒移速 +10%**，附近有看得见的敌方英雄时 +30%（英雄联盟的「寻觅」） |
| 标枪投给谁 | AI 选的目标（常常是小兵、野怪） | 射程内**线上没被小兵野怪挡着的敌方英雄**：被捕猎的优先，再按飞得远（伤害高）、血少排；都被挡着就不换 |
| 猛扑猎杀扑向谁 | AI 选的最近打过的英雄 | 射程内**被捕猎的、血量比例最低的**敌方英雄 |
| 推倒（v0.1.5） | 固定伤害（捕猎 +30%） | 另外**按目标已损失的生命加伤**：每损失 1% 生命 +1%（1-3 级）/ 1.25%（4-7 级）/ 1.5%（8-10 级）/ 1.75%（11 级起），防御塔不算（英雄联盟） |

## 怎么做的

- `mod.override_info` 把主包的奈德丽换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_nidalee.py` 的
  `native=1` 生成，主包的奈德丽改了就重跑）：加上本包的被动 `league_nidalee:prowl`（参数 `brush_ms` 10、`brush_near_ms` 30、
  `brush_t` 120、`near` 93000），普攻、Q、R 的说明开头加【附加包】。
- **整身变豹**（`src/view.rs`）：照凯隐附加包的完整变身（league_kayn_form 的 view.rs）换**正在播的动画名**。显示世界每帧调用的
  更新函数（rva 0x23312a0，槽 rva 0x3c82db8；0.6.3 时 0x2808e30 / 0x3c31358）换成本包的函数：先调用槽里原来的（游戏的，或凯隐 / 佛耶戈附加包的），再看名字是
  `league_nidalee` 的画面实体：身上有美洲狮形态的 buff `league_nidalee_cg` 时，正在播的 `idle` / `run` / `hit` / `dead` /
  `attack` 换成奈德丽图里的 `c_idle` …。阵亡时 buff 清掉，尸体按倒下前的形态画；复活是人形（和英雄联盟一样）。
- **草丛**（`src/bush.rs`）：地图自定义钩子读地图文档的 `bushes`（同雷恩加尔附加包），每种模式记一张，当前对局取站进墙里的
  单位最少的那张。
- **挑目标**（AI 钩子 `league_nidalee:aim`）：AI 要放 Q（只在人形、标枪冷却好时）或 R 时，按上表换目标；换了就在日志里记一行。
- **推倒加伤**（原生效果 `league_nidalee:takedown`，v0.1.5）：副本的推倒一咬（`league_nidalee_cq_bite` 的命中效果）最前面调用它：读目标这一咬之前的生命，补「这一咬的物理、魔法伤害（捕猎时 ×130%，同数据）× 已损失生命的比例 × 每 1% 的加成」（`deal_damage`，算普攻）。数字是 `src/lib.rs` 的 `TD_*`，`make_override.py` 和参数表 P 核对。
- 别的原生代码只做判断和换名字，伤害、治疗、捕猎都在数据里。

## 在游戏里测

1. 主包（League of Legends Heroes 0.105.0 以上）要装着并启用。
2. 把整个 `league_nidalee` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_nidalee.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看奈德丽普攻的说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nidalee.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `whole-body cougar on: display slot …`：整身变豹装上了（`off (…)` 就是游戏版本不对）；
   - `world … Nidalee #…: COUGAR (playing idle)` / `human`：形态变了；
   - `== map mode=…: bushes under …` 和 `BUSHES: … bush cells`：读到的草丛；`INTO` / `OUT OF the bush`、`BRUSH SPEED a -> b%`；
   - `Q … -> … AIM` / `R … -> … AIM`：标枪 / 猛扑猎杀换了目标（`HUNTED` 是被捕猎的）。
   - `TAKEDOWN #n on #7 league_garen: 600/2000 hp before the bite, level 9 (150% a 1%), hunting true -> +… physical +… magic`：推倒按已损失的生命补的伤害（v0.1.5）。

## 开发

- `python addons/league_nidalee/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的奈德丽和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_nidalee`：单元测试（参数、换动画名、尸体的形态、草丛格子、标枪和大招挑目标、
  草丛加速、推倒加伤）。
- 在 `addons/` 下 `cargo build --release -p league_nidalee`（Windows）得到 `target/release/league_nidalee.dll`；`league_addons`
  合集也会编进本包（合集只能有一个地图钩子：`MapReaders` 先调卡密尔的读墙、雷恩加尔的读草丛，再调本包的读草丛）。
- 工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\nd`）。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。

## 0.1.2：草丛地图每次挑同一张（2026-11-06）

玩法不变。11-06 的日志里每一局看的比赛，画面都在开局 1-5 分钟和服务器的预模拟分开（三局换了赢家），排查时查了各附加包里跨模拟共用的状态。奈德丽这里（茂凯、提莫编进的是同一个 `src/bush.rs`）：读过的地图放在哈希表里，两张地图一样合适（站进墙里的单位
一样少）时挑哪张看哈希表的顺序——服务器的预模拟和屏幕上的比赛在不同的时候挑，表里多了一种模式就可能换一个顺序，两边用上不同的
草丛。现在放在按模式编号排的有序表里；一样合适时取墙多的（最「具体」的，青钢影附加包的挑法），再一样取模式编号小的。测试
`maps_that_fit_as_well_are_picked_the_same_way_every_time`。

## 射程 buff 改成主包 league.dll 的 league:range（v0.1.3，2026-11-07）

带攻击距离的 buff 改成主包 league.dll 的 `league:range` 标记——buff 不再带 `range`（游戏的 AI 按它站位、却不按它出手，英雄停在够不着的地方），射程由官方的 `range_adjust` 加，AI 的出手判断也认；副本跟着主包 0.319.0 重新生成。

## 推倒按目标已损失的生命加伤（v0.1.5，2026-11-14）

用户看了「和英雄联盟不一样的地方」清单后说「全改吧」，又说「接着做」。英雄联盟的推倒每 1% 已损失生命多 1% ～ 1.75%（随大招等级），主包是固定伤害。副本（`build_nidalee.py` 的 `native=1`）的推倒一咬先调用新的原生效果 `league_nidalee:takedown`（见上面「怎么做的」）；主包同一天把捕猎加成照英雄联盟现在的 30% 改了（原来 40%），本包的 `TD_HUNT` 跟着是 130。Q 的说明加上「目标每损失1%生命再+1%~1.75%（随等级）」。
