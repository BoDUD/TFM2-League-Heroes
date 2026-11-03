# 赵信大招远程免伤附加包（测试版 v0.1.1）

主包 `league` 保持纯数据。英雄联盟里赵信的 R「新月护卫」之后，他免疫 450 码外敌人的伤害；数据读不到伤害来自多远，
所以主包里改成 R 之后 3 秒受到的伤害降低 40%（用户选的）。用户：「读不到多远就改rust源代码 看看能不能」——
这个附加包用原生代码读攻击者的位置，做成英雄联盟的样子：

- **远处的伤害挡掉**：主包的护卫 buff `league_xinzhao_r_guard`（R 之后 3 秒，身后的金色护卫光）在附加包里去掉 40% 减伤，只留画面和计时；
  被动 `league_xinzhao_guard:guard`（挂在 `passive` 上）在他每次挨打时（`on_damaged`）看：护卫还在，攻击者离他**超过 36000**
  （R 的横扫半径，英雄联盟的 450 码，中心到中心），这一下的伤害原样加回去（最大生命放不下的那一截，这一下扣完血以后再加）。
- **近身的照常吃**：被挑战的目标留在他身边，打他照常疼；36000 以内的敌人也一样。
- 数字写在英雄数据的 `passive.params`（`{"far": 36000}`）里，由 `make_override.py` 从 `tools/kit/build_xinzhao.py` 的参数表 `P`
  （`r_far`）写入，本包不另记一份。

游戏在这一下扣血**之前**调 `on_damaged`（0.1.0 这里写反了；0.1.1 按 2026-11-03 晚的日志改：`BLOCK 6 …: hp 2750 -> 2750/2750`
之后下一下读到 2744）：被动先把血加上这一下，扣完正好回到原来的血，所以一下就能打死他的远程伤害也挡得住。0.1.0 加到最大生命
就停，满血、快满血时挡掉的伤害照样漏进来（一次启动 230 下里 11 下、共 721 点）；0.1.1 把放不下的那一截记下，这一下扣完以后
（同一拍的下一下伤害来时，或者下一拍）再加回去（日志 `BACK`）。剩下的限制：远处一下就超过他整个最大生命的伤害还是挡不住。

## 在游戏里测

1. 主包（League of Legends Heroes 0.64 以上）要装着并启用。
2. 把整个 `league_xinzhao_guard` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_xinzhao_guard.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看赵信 R 的说明：开头是「【远程免伤测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_xinzhao_guard.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `BLOCK 85 from #7 at 52000 (far 36000): hp 610 -> 695/1820`：挡掉一下，伤害、攻击者、距离、生命的变化
     （满血时 `hp 1820 -> 1820/1820, 85 back after the hit`：放不下的 85 扣完再加）；
   - `BACK 85 the cap held back: hp 1735 -> 1820/1820`：那一截加回去了。

## 开发

- `python addons/league_xinzhao_guard/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的赵信和参数表一致）。
  主包的赵信改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_xinzhao_guard`：单元测试（什么时候挡、参数读取、回血不超过上限、放不下的那截扣完再加：挡掉的伤害一点也不漏）。
- 在 `addons/` 下 `cargo build --release -p league_xinzhao_guard`（Windows）得到 `target/release/league_xinzhao_guard.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，挡伤害要在游戏里看日志确认。
