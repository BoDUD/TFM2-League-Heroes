# 派克精确斩杀附加包（测试版 v0.1.1）

主包 `league` 保持纯数据。数据读不到当前生命，主包里派克的 R 由 AI 对「队伍刚打过的敌方英雄」放出，满血的也会被砍
（用户：「大招逻辑也有点问题 总是满血砍人」）；X 里的英雄先吃斩杀线的真实伤害、下一 tick 活下来的回一半，近似「低于斩杀线处决」。
这个附加包用原生代码读生命，做成 League 的样子：

- **只砍斩得死的人**：AI 钩子 `league_pyke:ult`。斩杀线 T = 180 + 60% 攻击力（主包的 `r_dmg`、`r_ratio`）。R 只放向射程 75000 内
  生命不高于 T 的敌方英雄，几个时砍血最少的；AI 想对斩不死的人放 R，就改成打他（打不到就走过去）；R 好了、有斩得死的人，AI 没想放也放。
- **精确斩杀**：原生效果 `league_pyke:execute` 代替主包 X 里「真实伤害 + 一 tick 后回一半」：生命不高于 T 的英雄直接处决（击杀算派克的），
  其余吃 T 的一半真实伤害（同主包的净伤害）。处决后 4 tick（`league_pyke:after`）那人真死了，派克闪到他倒下的地方、R 刷新，
  播主包的 R 刷新画面、声音和台词。主包 X 里那套击杀检查在副本里去掉：原生伤害要到这一 tick 结算完才扣，数据的检查当场看人还活着，
  就把闪现取消了（用户：「放大招的时候人没过去？」）。
- AI 钩子自己看 R 的冷却和等级（引擎的「输入合法」不看冷却：v0.1.0 在冷却里每 tick 下令放 R，把派克定住好几秒）；
  AI 想对射程外或已死的人放 R 时不拦，走进射程再看。
- 数字写在 `src/lib.rs` 的常数里，`make_override.py` 生成副本时核对它们和 `tools/kit/build_pyke.py` 的参数表 `P` 一致。

## 在游戏里测

1. 主包（League of Legends Heroes 0.67 以上）要装着并启用。
2. 把整个 `league_pyke` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_pyke.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看派克 R 的说明：开头是「【精确斩杀测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_pyke.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `R EXECUTE #7: hp 180 <= 223, retargeted from #4 (hp 1500)`：放 R，砍谁、他的生命、斩杀线，AI 原来想砍谁；
   - `R HELD: #4 hp 1500 > 223, nobody in reach to execute`：AI 想放 R 但没人斩得死，改成打他；
   - `X EXECUTED #7: hp 160/1450 <= 223`、`X hit #4: hp 1300/1500 > 223, 111 true damage`：X 落下时每个英雄的结果；
   - `RESET: #7 died, blinked to (…), R ready again`：处决后闪过去、R 刷新（`X: #7 survived the execute` 是没死成）。

## 开发

- `python addons/league_pyke/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的派克和参数表一致）。
  主包的派克改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_pyke`：单元测试（斩杀线、放不放 R、砍谁）。
- 在 `addons/` 下 `cargo build --release -p league_pyke`（Windows）得到 `target/release/league_pyke.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，放 R 的时机要在游戏里看日志确认。
