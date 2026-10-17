# 辛德拉举小兵附加包（测试版 v0.1.0）

用户：「辛德拉W的球应该要做成能举小兵和野怪吧 除了大小龙」。主包 `league` 保持纯数据：数据挑不出「只要小兵和普通野怪」的目标
（大小龙也算「除防御塔外的敌人」），也不能把一个单位挪到指定的点，所以主包的 W「驱使念力」总是掷出一颗手里凝聚的法球。
英雄联盟里 W 抓的是法球，没有法球时抓身边的小兵或野怪（史诗野怪除外）。

这个附加包把主包的辛德拉换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_syndra.py` 的 `--native` 生成：技能
一样，W 施放时在她身上挂 `league_syndra_w_grab`、在投掷目标身上挂 `league_syndra_w_at`；她身上有 `league_syndra_w_unit` 时掷出的是
一个不显示的抛物线，落点照样伤害、减速，不留法球；W 的说明多了「没有时举起附近的小兵或野怪，大小龙除外」），被动
`league_syndra:grab` 每 tick 看一次：

- 看到 `w_grab`（一次施放只处理一次）：她身上还记着法球（主包的计数 `league_syndra_o1`–`o4`）就什么都不做，数据照常掷法球
  （和英雄联盟一样法球优先）；
- 没有法球：在她身边 60000 内找最近的一个敌方小兵或野怪（不要英雄、防御塔、投掷目标本身，也不要大龙 `epic_monster`、小龙
  `serpen`），挂上 `w_unit`，把它击飞（期间不能行动），逐 tick 摆到位置上：先飞到她身前举着，第 12 tick（数据出手的那一刻）起
  16 tick 飞到目标脚下（目标走动就跟着他的位置），和数据的抛物线同时落地。

数字（出手 tick、飞行 tick、抓取范围、举起的速度）从英雄数据的 `passive.params` 来。只有单元测试（经典 SDK 跑不了原生代码），
要在游戏里看日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_syndra.log`（`W #n: lifts ...` 举起了谁、从哪里到哪里、
掷向谁；`a sphere is counted` 法球优先；`no minion or monster` 身边没有能举的；`landed` 落地）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.91 以上）要装着并启用。
2. 把整个 `league_syndra` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_syndra.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看辛德拉技能 2 的说明：写着「没有时举起附近的小兵或野怪，大小龙除外」就说明换上了。

## 开发

```bash
python addons/league_syndra/make_override.py      # 主包的辛德拉或她的说明改了就重跑
cd addons && cargo test --release -p league_syndra && cargo build --release -p league_syndra
```
