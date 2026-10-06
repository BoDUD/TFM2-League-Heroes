# 卡兹克视野与进化附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。数据读不到视野和等级，主包里卡兹克的被动「无形威胁」在 R 隐身、复活和约 4 秒没出手后就绪；
进化靠「法强探测」（每级 +1 法强，自伤打护盾）在 5/8/11 级后一两秒内认出等级（用户：「数据读不到就用rust 改写源码」）。
这个附加包用原生代码读视野和等级，做成英雄联盟的样子：

- **无形威胁看真视野**：原生被动 `league_khazix:void` 每 tick 看——他活着、敌方队伍看不见他（草丛、战争迷雾、R 的隐身都算），
  就给他加上 `league_khazix_ut`（永久，下一次攻击英雄时由数据打出伤害和减速并去掉）。「没出手就绪」去掉，R 隐身照样就绪。
- **进化读等级**：等级到 5/8/11 级就给 `league_khazix_s1`（攻击距离 +6000）/ `s2` / `s3`，播进化画面、音效和台词；
  复活后补回已有进化时不播。主包副本里的探测去掉（普攻的效果树从 587 个节点减到 40 个）。
- 孤立无援仍用主包的数据判定（命中时在目标身边数人头，已经是英雄联盟的意思）。
- 数字从英雄数据的 `passive.params` 来（`make_override.py` 从 `tools/kit/build_khazix.py` 的参数表 `P` 写进去）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.69 以上）要装着并启用。
2. 把整个 `league_khazix` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_khazix.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看卡兹克普攻（被动）的说明：开头是「【视野测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_khazix.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `UNSEEN: Unseen Threat ready`：敌方看不见他，被动就绪；
   - `EVOLVE league_khazix_s2 at level 8`：进化（复活后补回的带 `(silent, after respawn)`）。

## 开发

- `python addons/league_khazix/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的卡兹克和参数表一致）。
  主包的卡兹克改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_khazix`：单元测试（参数、按等级进化、被动就绪的条件）。
- 在 `addons/` 下 `cargo build --release -p league_khazix`（Windows）得到 `target/release/league_khazix.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
