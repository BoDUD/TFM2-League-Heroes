# 辛德拉举小兵附加包（测试版 v0.1.0）

0.1.2（2026-11-05）：待命式大招没用掉时的冷却退还不稳：原来在窗口结束前 1 tick 读待命标记（n tick 的标记只有 n - 1 tick 看得见），经典 SDK 追踪里悟空 53 次过期有 7 次读到时标记已经没了、白等完整冷却；塞恩、艾尼维亚等在前 3 tick 读的 177/177 都退了。现在统一在窗口结束前 3 tick 读（`tools/kit/build_syndra.py`），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

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

## 0.1.3：9 级的大招改成英雄联盟的斩杀（2026-11-14）

用户看了「和英雄联盟不一样的地方」清单后说「全改吧」。英雄联盟里卓尔不凡满 100 层碎片后，能量倾泻会斩杀被打到最大生命 15% 以下的英雄；主包读不到生命，9 级起改成「法球无视魔抗」。

- 副本（`build_syndra.py` 的 native）：9 级起法球还是普通魔法伤害，每颗打中后多调一次原生效果 `league_syndra:execute`。
- `execute`：这颗法球的伤害结算完，目标（敌方英雄）的生命低于最大生命的 15%（`R_EXEC`，`make_override.py` 核对它和主包参数表的 `r_exec` 一样）就处决：给足量的真实伤害（护盾也打穿），击杀算辛德拉的。日志 `R EXECUTE #n: 谁 at hp a/b, under 15%`（前 60 行，之后每 25 行一行）。
- 普攻（被动）的说明在副本里改成「9 级 R 斩杀生命被打到 15% 以下的英雄」。

经典引擎跑不了原生代码，斩杀量不到；副本去掉无视魔抗后的模拟（中路，240 局）是 +2.14（改之前 +1.36，主包现在 +1.68）。下一局看 `R EXECUTE` 行有没有、处决时的生命是不是都在 15% 以下。
