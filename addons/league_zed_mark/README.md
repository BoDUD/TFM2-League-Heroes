# 劫读血附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。数据读不到生命也读不到伤害，所以主包里劫的两处是替代做法：

- **被动「影忍法！灭魂劫」**：英雄联盟里是攻击生命低于 50% 的英雄时附加其最大生命的伤害；主包改成「技能刚打中过英雄」后的下一次普攻（`league_zed_cw_ready`），附加 6% 最大生命真实伤害，10 秒一次。
- **大招「禁奥义！瞬狱影杀阵」**：英雄联盟里印记爆发时附加印记期间造成伤害的一部分；主包改成按期间命中次数（最多 3 次）每次加固定伤害（`r_1`..`r_3`）。

用户：「这个改成用 rust 附加包」。本附加包用原生代码读真实的生命和伤害，做成英雄联盟的规则：

- **蔑视弱者**：副本的普攻打中英雄时给目标挂 2 tick 的 `league_zed_cw_probe`；被动 `league_zed_mark:edge`（挂在 `passive` 上，每 tick 运行）
  看到它就读目标的生命：**低于 50%**、这个目标的 10 秒冷却已过，就追加目标最大生命的 **6% / 8% / 10%**（劫 1–6 / 7–12 / 13 级起）魔法伤害，
  并播放数据里的 `league_zed_cw_hit` 画面。
- **死亡印记**：目标身上有 `league_zed_r_mark`（数据加的，3 秒）时，劫打到这个目标的伤害（`on_attack`，技能也算）都记下来；
  印记一消失（爆发那一刻）追加记下伤害的 **35%**（物理）。数据的爆发（基础伤害、画面、声音）照旧。
- **残血换回大招影子**（用户：「做第一和第二个」）：大招影子在场（劫身上有 `league_zed_r_live`）、劫生命**低于 30%** 时，每 tick 给劫挂 `league_zed_r_back`，数据里影子的检查点（每 6 tick）看到它就把他换回影子。击杀、被包围、被控时的换回是主包数据自己判断的，不装本包也有。
- 主包副本去掉了上面两处的数据替代（`cw_ready`、`r_1`..`r_3`），技能树更小。
- 数字都写在英雄数据的 `passive.params` 里，由 `make_override.py` 从 `tools/kit/build_zed.py` 的参数表 `P` 写入
  （`cw_hp`、`cw_lo`、`cw_mid`、`cw_hi`、`cw_cd`、`r_pct`、`r_low`），本包不另记一份。

## 在游戏里测

1. 主包（League of Legends Heroes 0.82 以上）要装着并启用。
2. 把整个 `league_zed_mark` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_zed_mark.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看劫普攻（被动）的说明：开头是「【读血测试版】」就说明换上了；大招说明里写的是「外加期间所造成伤害的 35%」和「击杀、被包围、被控或生命低于30%时换回影子」。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zed_mark.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `CONTEMPT #3 on #12: hp 410/1200 (34%) +96 magic`：触发时目标的生命（应当都在 50% 以下）和追加的伤害；
   - `MARK on #12: hp 1100` / `POP #1 on #12: stored 620 (hp drop 700), +217`：印记挂上时的生命，爆发时记下的伤害
     （`on_attack` 给的数，括号里是同期目标掉的血，用来核对 `on_attack` 是否包含技能伤害）和追加的伤害；
   - `BACK: hp 280/1100 (25%) under the R shadow -> r_back`：残血换回（每次大招影子只记一次）。

## 开发

- `python addons/league_zed_mark/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的劫和参数表一致）。
  主包的劫改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_zed_mark`：单元测试（触发线、等级百分比、爆发比例、残血线、参数读取）。
- 在 `addons/` 下 `cargo build --release -p league_zed_mark`（Windows，长路径时用短的 `CARGO_TARGET_DIR`）得到
  `league_zed_mark.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试；触发和爆发要在游戏里看日志确认。
