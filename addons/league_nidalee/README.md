# 奈德丽附加包（测试版 v0.1.0，可选）

**不装这个附加包，主包里的奈德丽也是完整的**：人形 / 美洲狮两种形态、按战况切换、标枪、夹子、治疗、推倒、猛扑、挥击和
5 级的猛扑猎杀都在主包数据里。主包是纯数据，有几件事做不到，这个附加包用原生代码补上：

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 变身后的样子 | 只有出招（普攻、推倒、猛扑、挥击、大招）是豹子的动作，待机、跑步、受击、阵亡还是人形（游戏按名字自动播这几个，数据换不了） | **整个身体**都是豹子（只在游戏 0.6.3 上，别的版本退回左边那样） |
| 寻觅（被动） | 标枪 / 夹子命中英雄：捕猎 4 秒、移速 +20% | 另外**在草丛里和离开草丛后 2 秒移速 +10%**，附近有看得见的敌方英雄时 +30%（英雄联盟的「寻觅」） |
| 标枪投给谁 | AI 选的目标（常常是小兵、野怪） | 射程内**线上没被小兵野怪挡着的敌方英雄**：被捕猎的优先，再按飞得远（伤害高）、血少排；都被挡着就不换 |
| 猛扑猎杀扑向谁 | AI 选的最近打过的英雄 | 射程内**被捕猎的、血量比例最低的**敌方英雄 |

## 怎么做的

- `mod.override_info` 把主包的奈德丽换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_nidalee.py` 的
  `native=1` 生成，主包的奈德丽改了就重跑）：加上本包的被动 `league_nidalee:prowl`（参数 `brush_ms` 10、`brush_near_ms` 30、
  `brush_t` 120、`near` 93000），普攻、Q、R 的说明开头加【附加包】。
- **整身变豹**（`src/view.rs`）：照凯隐附加包的完整变身（league_kayn_form 的 view.rs）换**正在播的动画名**。显示世界每帧调用的
  更新函数（rva 0x2808e30，槽 rva 0x3c31358）换成本包的函数：先调用槽里原来的（游戏的，或凯隐 / 佛耶戈附加包的），再看名字是
  `league_nidalee` 的画面实体：身上有美洲狮形态的 buff `league_nidalee_cg` 时，正在播的 `idle` / `run` / `hit` / `dead` /
  `attack` 换成奈德丽图里的 `c_idle` …。阵亡时 buff 清掉，尸体按倒下前的形态画；复活是人形（和英雄联盟一样）。
- **草丛**（`src/bush.rs`）：地图自定义钩子读地图文档的 `bushes`（同雷恩加尔附加包），每种模式记一张，当前对局取站进墙里的
  单位最少的那张。
- **挑目标**（AI 钩子 `league_nidalee:aim`）：AI 要放 Q（只在人形、标枪冷却好时）或 R 时，按上表换目标；换了就在日志里记一行。
- 原生代码只做判断和换名字，伤害、治疗、捕猎都在数据里。

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

## 开发

- `python addons/league_nidalee/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的奈德丽和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_nidalee`：单元测试（参数、换动画名、尸体的形态、草丛格子、标枪和大招挑目标、
  草丛加速）。
- 在 `addons/` 下 `cargo build --release -p league_nidalee`（Windows）得到 `target/release/league_nidalee.dll`；`league_addons`
  合集也会编进本包（合集只能有一个地图钩子：`MapReaders` 先调卡密尔的读墙、雷恩加尔的读草丛，再调本包的读草丛）。
- 工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\nd`）。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
