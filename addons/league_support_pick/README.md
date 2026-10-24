# 辅助挑人附加包（测试版 v0.1.0，可选）：迦娜、娑娜、璐璐

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里辅助把护盾、回血给正在挨打、快死的队友，或者正在打的那个人。主包是纯数据：给队友的那一下是 `RandomTarget AllyNotSelf`，随机挑一名队友。**不装这个附加包，主包的三人也是完整的**。

| 英雄 | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 迦娜 E 风暴之眼（50000 内） | 随机一名队友 | 有危险的队友（生命不高于 50%，或身边 25000 内有 2 个以上敌方英雄）里生命比例最低的；都没危险就给离敌方英雄最近的（正在打的那个） |
| 娑娜 W 回血（60000 内） | 随机一名队友 | 损失生命最多的队友 |
| 璐璐 E 帮忙，皮克斯！（先 30000，再 60000 内） | 随机一名队友 | 同迦娜 |

护盾、回血、画面、声音的数字都和主包一样；范围内没有队友时，主包后面「给自己」的那段照常。

## 怎么做的

- `mod.override_info` 把三人换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成，先核对那几处 `RandomTarget` 里的数字和 `src/lib.rs` 一样，再换成原生效果：迦娜 `league_support_pick:janna_e`、娑娜 `:sona_w`、璐璐 `:lulu_e30` / `:lulu_e60`；三人 W/E 的说明开头加【附加包】、「一名友方英雄」换掉。
- 原生效果挑好人之后照主包给：
  - 迦娜：`entity_add_shield` 150 + 75% 法强 240 tick，挂 `league_janna_e_storm`（护盾在时攻击力 +15%），给她自己挂主包的 `league_janna_e_lock`（主包据此不再护她自己）；
  - 娑娜：`heal` 100 + 40% 法强，播 `league_sona_w_heal`；
  - 璐璐：`spawn_projectile` 放出主包的小精灵 `league_lulu_e_pix`（每 tick 4500），到了由 `:lulu_e_land` 给护盾 110 + 50% 法强 150 tick、`league_lulu_e_on`、移速攻速 +25% 210 tick，播画面和声音；给她挂主包的 `league_lulu_e_got`。
- 璐璐 R、迦娜 R 不变（R 本来就按被控制、生命低的队友挑，效果太多，原生做不了一模一样）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_support_pick` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 三人 W/E 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_support_pick.log`：`JANNA E #n -> #7 (hp 300/1200, 2 enemies around) IN DANGER, shield 260`、`SONA W #n -> #9 ..., heal 140`、`LULU E #n -> #7 ...`。

## 开发

- `python addons/league_support_pick/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。三人在主包里改了就重跑。
- `cargo test -p league_support_pick`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
