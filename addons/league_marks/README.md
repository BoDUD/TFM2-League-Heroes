# 目标标记附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

主包是纯数据：`SwitchByBuff` 只读得到施放者自己身上的 buff，读不到目标身上的。所以英雄联盟里「只对带标记的那个目标」生效的效果，主包都改成了「她自己最近有没有打中过」。原生代码读得到每个单位身上的 buff，这个附加包把它们改回英雄联盟的样子。**不装这个附加包，主包的英雄也是完整的**。

| 英雄 | 主包（纯数据） | 装了附加包（英雄联盟） |
|---|---|---|
| 黛安娜 E 月光冲击 | Q 打中过任何东西，下一次 E 就能再冲一次 | E 冲向的目标身上带月光时才再冲一次；冲到后所有敌人身上的月光都消耗掉 |
| 凯南 雷缚印 | 层数记在凯南身上：打 A 一次、打 B 两次，B 就被眩晕 | 每个英雄各记各的（6 秒），同一个人第三层眩晕 1.25 秒，7 秒内再次只有 0.5 秒 |
| 卡莎 体表活肤 | 电浆层数记在卡莎身上：打 A 叠的层数会在 B 身上引爆 | 每个英雄各记各的（4 秒）：普攻每次附加 18 + 9 × 层数 + 20% 法强的魔法伤害，同一个人第五层引爆 80 + 60% 攻击力 + 8% 最大生命的真实伤害 |

## 怎么做的

- 副本由 `make_override.py` 从主包生成：在要判断的那一下给目标挂一个 3 tick 的「问」标记（黛安娜：`league_marks_diana_e`），2 tick 后读施放者身上的「答」标记（`league_diana_moonlit`）。改过的说明开头加【附加包】。
- 被动（`league_marks:diana`）找身上有「问」标记的敌人，看他有没有主包的标记（`league_diana_moon_mark`，主包 Q 命中时挂上，3 秒），有就给施放者挂「答」标记。
- 再冲一次的画面、伤害都是主包数据里的那一套。
- 凯南、卡莎：副本把主包「读、数自己身上层数」的那一段换成给被打中的英雄挂一个命中标记（凯南 `league_marks_kennen_hit`；卡莎普攻 `league_marks_kaisa_a`、被控英雄多叠的那层 `_c`、W 的 `_w2` / `_w3`）。被动 `league_marks:kennen` / `:kaisa` 按目标数层：凯南第三层用 `apply_cc` 眩晕，卡莎的附加伤害和引爆用 `deal_damage_typed`（数字由 `make_override.py` 从主包读进 `passive.params`），层数、眩晕和引爆的画面播主包的。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_marks` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 黛安娜 E、凯南和卡莎普攻的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_marks.log`：`DIANA E #n on #7: moonlit, dash again (3 of 5 moonlit)`、`KENNEN STUN #n on #7: 75 ticks`、`KAISA POP #n on #7: 420 true`。

## 开发

- `python addons/league_marks/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。英雄在主包里改了就重跑。
- `cargo test -p league_marks`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
