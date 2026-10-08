# 雷恩加尔草丛附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。数据读不到地形，主包里雷恩加尔的被动「无形掠食者」在复活、约 3 秒没出手和 R 之后就绪
（用户：「还有草丛可以跳跃 你要记住这游戏地图的草丛」）。这个附加包用原生代码读地图的草丛，做成英雄联盟的样子：

- **站进草丛就能扑**：原生被动 `league_rengar_bush:bush` 每 tick 看——他活着、脚下的格子是草丛、身上还没有
  `league_rengar_ready`，就加上它（攻击距离 +25000，下一次攻击由数据打出扑击并去掉）。「没出手就绪」去掉。
- **走出草丛就没了**：本包给的就绪在他离开草丛 20 tick 后去掉（英雄联盟里出了草丛就不能跳）；复活和 R 给的不动。
- **草丛从地图读**：地图自定义钩子读地图文档的 `bushes`（和卡密尔附加包读 `walls` 一样），每种模式记一张，当前对局取
  站进墙里的单位最少的那张。读不到时退回「敌方队伍看不见他」，日志里会写 `NOT FOUND` 和地图文档的开头，方便改键名。
- 数字从英雄数据的 `passive.params` 来（`make_override.py` 从 `tools/kit/build_rengar.py` 的参数表 `P` 写进去）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.81 以上）要装着并启用。
2. 把整个 `league_rengar_bush` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_rengar_bush.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看雷恩加尔普攻（被动）的说明：开头是「【草丛测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rengar_bush.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `== map mode=… ==` 下面画出读到的草丛格子（`#` 是草丛）；
   - `INTO the bush` / `OUT OF the bush`：进出草丛；
   - `READY: the pounce from the bush`：草丛给了扑击；`DROP: out of the bush 20 ticks`：出草丛后收回。

## 开发

- `python addons/league_rengar_bush/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的雷恩加尔和参数表一致）。
  主包的雷恩加尔改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_rengar_bush`：单元测试（参数、格子解析、挑地图、就绪和收回的条件）。
- 在 `addons/` 下 `cargo build --release -p league_rengar_bush`（Windows）得到 `target/release/league_rengar_bush.dll`；
  `league_addons` 合集也会编进本包（合集只能有一个地图钩子：`MapReaders` 先调卡密尔的读墙，再调本包的读草丛）。
- 工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\rg`）。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
