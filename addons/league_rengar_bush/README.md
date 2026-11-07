# 雷恩加尔草丛附加包（v0.2.2）

主包 `league` 保持纯数据。数据读不到地形，主包里雷恩加尔的被动「无形掠食者」在复活、约 3 秒没出手和 R 之后就绪
（用户：「还有草丛可以跳跃 你要记住这游戏地图的草丛」）。这个附加包用原生代码读地图的草丛，做成英雄联盟的样子：

- **站进草丛就能扑**：原生被动 `league_rengar_bush:bush` 每 tick 看——他活着、脚下的格子是草丛、身上没有就绪
  （`league_rengar_ready`，或在塔前收起的 `league_rengar_ready_kept`），就加上 `league_rengar_ready`（攻击距离 +25000，
  下一次攻击由数据打出扑击并去掉）。
- **打架时走出草丛就没了**：本包给的就绪在他离开草丛 20 tick 后去掉（英雄联盟里出了草丛就不能跳）——只在打架时（3 秒内出过手，
  数据的 `league_rengar_fight`）。不在打架时手上的就绪就是「脱战 3 秒」那一份，留到用掉；R 给的不动。
- **主包的就绪全留着**：复活后第一下、脱战 3 秒、R 之后照样就绪（0.2.0 起「脱战 3 秒」回来了，见下）。
- **塔不扑**：普攻读就绪之前先过原生效果 `league_rengar_bush:aim`：目标是塔或水晶时就绪收成没有射程加成的
  `league_rengar_ready_kept`（头顶的金眼照样亮着），这一下照常挥刀；下一次打单位时换回来、照常扑出去。以前扑到塔上的那一下
  （落地只打 `EnemyWithoutTower`）一点伤害都没有，就绪也白丢了。英雄联盟的扑击也不对防御塔。
- **艾翁的草丛**：身上有 `league_ivern_in_brush`（艾翁附加包给站在他草丛里的英雄挂的标记）也算站在草丛里。
- **草丛从地图读**：地图自定义钩子读地图文档的 `bushes`（和卡密尔附加包读 `walls` 一样），每种模式记一张，当前对局取
  站进墙里的单位最少的那张（一样少取最后读到的）。那张地图没有草丛就没有草丛给的扑击，不借别的模式的；哪张地图都读不到时
  退回「敌方队伍看不见他」，日志里会写 `NOT FOUND` 和地图文档的开头，方便改键名。
- 数字从英雄数据的 `passive.params` 来（`make_override.py` 从 `tools/kit/build_rengar.py` 的参数表 `P` 写进去）。

## 0.2.1（2026-11-06）

玩法不变。11-06 的日志里每一局看的比赛，画面都在开局 1-5 分钟和服务器的预模拟分开（三局换了赢家），排查时查了各附加包里跨模拟共用的状态。雷恩加尔这里：两张地图一样合适时，0.2.0 取「最后读到的」——服务器的预模拟和屏幕上的比赛在不同的时候挑，中间别的
比赛建图读了另一种模式的地图，两边就用上不同的草丛。现在只看地图本身：一样合适时取墙多的（单线的比赛也没人站在 5v5 地图的墙里），
再一样取模式编号小的；读过的地图放在按模式编号排的有序表里。测试 `maps_that_fit_as_well_pick_the_one_with_more_walls`。

## 0.2.0（2026-11-03）

玩家：「他的跳跃机制非常不稳定，有时候会跳，有时候不跳」。0.1.x 的副本去掉了「没出手就绪」，就绪只剩复活后第一下（多半扑在
第一组野怪、小兵身上）、R 和草丛；AI 不会在草丛里等人，只是路过（同一张格子，奈德丽附加包 11-02 的日志：一分多钟进出草丛
十来次，每次 1–45 tick），出了草丛 20 tick 就收回——一场架开头跳不跳全看他刚才有没有路过草丛。现在：

- 「脱战 3 秒就绪」回到副本里（`build_rengar.py` 的 `act` 不再分 `native`），开打第一下照主包那样扑；
- 本包给的就绪只在打架时出了草丛才收回，不在打架时留到用掉（开打先放 W、E 也不收）；R 期间的就绪归 R，不收；
- 塔不扑（上面的 `aim`）；
- 没有草丛的地图不再借 5v5 的草丛格子；
- 日志加了 `AIM`、`POUNCE`、`TALLY`，每种行限条数（屏幕上那场每条都写）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.81 以上）要装着并启用。
2. 把整个 `league_rengar_bush` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_rengar_bush.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看雷恩加尔普攻（被动）的说明：开头是「【草丛版】」就说明换上了。生涯存档里存着每个英雄的一份定义，不会自己更新：
   装好以后用 `tools/save/refresh_save_heroes.py` 刷新存档里的雷恩加尔（先只报告、关着游戏、备份存档）。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rengar_bush.log`，每次启动游戏重写（上一次的留在 `.prev.log`）；
   每种行先写 40 条、之后每 100 条一条，屏幕上那场每条都写：
   - `== map mode=… ==` 下面画出读到的草丛格子（`#` 是草丛）；`BUSHES:` 这一场用哪张；
   - `INTO the bush` / `OUT OF the bush`：进出草丛；
   - `READY: the pounce from a bush (in a fight)`：草丛给了扑击；`DROP: out of the bush 20 ticks in a fight`：打架时出草丛后收回；
   - `AIM <塔>: a tower - a plain swing, the pounce kept for the next unit` / `AIM <单位>: the pounce kept at a tower goes out`；
   - `POUNCE: the readiness from <草丛 / 3 s out of combat / R / the respawn>, the nearest enemy champion <距离> away`：扑出去了；
   - `TALLY m:ss: …`：每场每 3 分钟一行这一场的累计（扑了几次、各是谁给的、几次扑在英雄跟前，草丛给了几次、收回几次、塔前收起几次）。

## 开发

- `python addons/league_rengar_bush/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的雷恩加尔和参数表一致；
  再核对副本有「脱战 3 秒」的 `league_rengar_fight`、普攻在读就绪之前跑 `aim`、说明不超长）。主包的雷恩加尔改了以后要重跑。
- `cargo test --manifest-path addons/Cargo.toml -p league_rengar_bush`：单元测试（参数、格子解析、挑地图、没有草丛的地图、就绪和
  收回的条件、就绪归谁、塔前收起和拿回、TALLY 的写法、副本里有本包读写的 buff 名）。
- 在 `addons/` 下 `cargo build --release -p league_rengar_bush`（Windows）得到 `target/release/league_rengar_bush.dll`；
  `league_addons` 合集也会编进本包（合集只能有一个地图钩子：`MapReaders` 先调卡密尔的读墙，再调本包的读草丛）。
- 工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\rg`）。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。

## 射程 buff 改成主包 league.dll 的 league:range（v0.2.2，2026-11-07）

带攻击距离的 buff 改成主包 league.dll 的 `league:range` 标记——buff 不再带 `range`（游戏的 AI 按它站位、却不按它出手，英雄停在够不着的地方），射程由官方的 `range_adjust` 加，AI 的出手判断也认；副本跟着主包 0.319.0 重新生成。本包原生代码补回 / 挂上的 buff 也不再带 `range`。
