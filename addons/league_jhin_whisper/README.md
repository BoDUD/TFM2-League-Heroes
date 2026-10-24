# 烬低语附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里烬的攻速是定死的：装备和增益给的额外攻速不加快他开枪，每 1% 换成 0.25% 的攻击力。主包是纯数据，攻速增益照常缩短他的攻击间隔。**不装这个附加包，主包的烬也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 额外攻速 | 开枪变快 | 不变快；每 1% 换成 0.25% 攻击力（+40% 攻速 = +10% 攻击力） |
| 攻速减益 | 开枪变慢 | 一样 |
| 低语、第四发、装弹 | 主包 | 一样 |

## 怎么做的

- `mod.override_info` 把烬换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成：只加被动 `league_jhin_whisper:whisper`，普攻（带着低语）的说明开头加【附加包】、末尾加一句。
- 被动每 6 tick 读一次他的攻速倍率 `attack_speed_mult`（100 = 没加成），减掉自己 buff 的那份，高出 100 的部分用 30 tick 的 buff `league_jhin_whisper_ad` 抵掉（攻速 −同样多，攻击力 +那么多的四分之一），数值变了就重挂。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_jhin_whisper` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 烬普攻的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_jhin_whisper.log`：`WHISPER: +40% attack speed -> +10% attack damage (attack speed x100%, interval 72)`——括号里是抵掉之后的倍率和攻击间隔，应该是 100% 和 72。

## 开发

- `python addons/league_jhin_whisper/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包里烬改了就重跑。
- `cargo test -p league_jhin_whisper`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
