# 格温被动附加包（测试版 v0.1.1）

主包 `league` 保持纯数据。数据里能读目标最大生命值的只有真实伤害，读不到法强，所以主包格温的被动「千穿百孔」对英雄造成
1% 最大生命值的**真实伤害**（用户：「这个可以改rust」）。这个附加包用原生代码做成英雄联盟的样子：

- **百分比最大生命值魔法伤害**：原生效果 `league_gwen:cuts` 代替主包里那段真实伤害。被动每次打到敌方英雄（普攻、E 落地那一剪、
  Q 的每一剪、R 的每根针），读他的最大生命值和格温的法强，造成 1% + 每 100 法强 0.3% 最大生命值的**魔法伤害**，会被魔抗减免（英雄联盟是每 100 法强 0.6%：游戏里后期 500 法强时
  一剪 4%、一套 Q 打掉二成多生命，减半）。例：对 2000 生命的英雄，0 法强时 20 点，230 法强时 33 点（减免前）。
- 回血和每次附加的固定魔法伤害照旧由数据做；其他英雄不变。
- 数字写在 `src/lib.rs` 的常数 `P_HP`、`P_HP_AP` 里，`make_override.py` 生成副本时核对它们和 `tools/kit/build_gwen.py` 参数表 `P`
  的 `p_hp`、`p_hp_ap` 一致。

## 在游戏里测

1. 主包（League of Legends Heroes 0.68 以上）要装着并启用。
2. 把整个 `league_gwen` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_gwen.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看格温普攻（被动）的说明：开头是「【魔法伤害测试版】」、写着「1%（每100法强+0.3%）最大生命值魔法伤害」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_gwen.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `CUTS #7: hp 1800/2000, ap 230 -> 1.69% = 33 magic (before resistance)`：被动打中谁、他的生命、格温的法强、比例和伤害
     （同一个格温每 60 tick 最多记一行）；
   - `CUTS skipped: input kind … is not a unit`：Q 的扇形里原生效果没拿到被剪的人（2026-10-07 游戏里没出现过：Q 的扇形也拿到了被剪的人）。

## 开发

- `python addons/league_gwen/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的格温和参数表一致）。
  主包的格温改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_gwen`：单元测试（比例、伤害、日志间隔）。
- 在 `addons/` 下 `cargo build --release -p league_gwen`（Windows）得到 `target/release/league_gwen.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，伤害要在游戏里看日志确认。
