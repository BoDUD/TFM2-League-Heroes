# 维迦法强常驻附加包（测试版 v0.1.2）

用户：「顺便帮小法做一个 永久叠法强的」。主包 `league` 保持纯数据：维迦的被动「超凡邪力」每一层是他身上一个永久的
`league_veigar_p_stack`（法术强度 +1，击杀英雄那一层 +5）。引擎在他死亡时清掉身上全部 buff，数据也没有「复活时」这个时机，
所以主包里法强每条命从零叠起（说明里写着「死亡时清空」）。英雄联盟里维迦叠的法强是永久的。

这个附加包把主包的维迦换成 `override/` 里的副本（`make_override.py` 生成：技能一字不改，只加被动 `league_veigar_power:keep`，
普攻说明里的「死亡时清空」换成「【扩展包】死后保留」），被动每 tick 看一次：

- 活着时把身上每一层 `league_veigar_p_stack` 原样记下来（记在被动里，被动在玩家身上，死了不丢）；
- 身上比记下的少了（死亡或复活时引擎清掉）就把缺的层原样补回，死着的时候也补，倒下时数值不掉。

层数只会变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。

只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_veigar_power.log`
（`DEAD` / `ALIVE` 带记下的层数，`KEEP` 补回了几层、死着还是活着）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.88 以上）要装着并启用。
2. 把整个 `league_veigar_power` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_veigar_power.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看维迦普攻（被动）的说明：结尾是「【扩展包】死后保留」就说明换上了。

## 开发

```bash
python addons/league_veigar_power/make_override.py      # 主包的维迦或他的说明改了就重跑
cd addons && cargo test --release -p league_veigar_power && cargo build --release -p league_veigar_power
```

## 0.1.2：扭曲空间只有牢笼的边缘晕人（2026-11-14）

用户看了「和英雄联盟不一样的地方」清单后说「全改吧」。英雄联盟的扭曲空间只晕碰到牢笼边缘的人（每次施放每人一次），站在里面的不晕；主包的区域是实心的圆，成形时站在里面的人立刻被晕（数据没有环形，主包没变）。

- 副本（`make_override.py`）：牢笼落点上的两个眩晕区域（`league_veigar_e_zone`：所有敌方单位眩晕；`league_veigar_e_zone_champ`：英雄再加声音、一层法强、一次连续命中）拿掉，换成原生效果 `league_veigar_power:cage`；两个区域的数字（半径 34000、180 tick、眩晕 60 tick、连续命中标记 240 tick）写进 `passive.params`。脚本先核对这两个区域就是代码替掉的那些（连续命中的梯子按 0–4 层各走一遍），主包改了会停下来。
- 原生效果给维迦挂一个带落点的记号（`league_veigar_power_cage:<x>:<y>`，4 tick），被动 `keep` 读到后取走、记下这座牢笼（记在被动里，他死了牢笼照样在）。
- 之后 `cage_t` tick 里每 tick 看敌方单位（英雄、小兵、野怪；不含塔、水晶、选不中的）：身体碰到圆周（中心离牢笼中心 `cage_r` ± 身体半径）的 `apply_cc` 眩晕 `stun` tick，播主包的眩晕画面，每座牢笼每人一次。站在里面不动的不晕；往外走、从外面进来、成形时正好站在圆周上的都晕；一 tick 里越过圆周的（闪现、传送）不晕。
- 晕到英雄时照主包那样：眩晕的声音、一层 `league_veigar_p_stack`、叠层的画面、连续命中 +1（`league_veigar_r_s1`..`s4`）；他死着时不叠。
- E 的说明指到本包的 `description.league_veigar_power.skill2`（「碰到它的敌人」换成「【扩展包】碰到牢笼边缘的敌人」）。原生效果向 AI 报 60 tick 的控制时长（副本的效果树里没有 `Stun` 了）。

眩晕还是主包的 1 秒（英雄联盟 1.5–2.5 秒），没有跟着加长。黑暗物质、牢笼的画面、冷却都还是主包的数据。日志：`CAGE #n at (x, y)`、`EDGE #n: #id (champion) touched the cage's edge`。经典引擎的模拟跑不了原生代码，没有量过；测试 `only_the_edge_stuns`、`each_unit_once_a_cage`、`the_hits_in_a_row_climb_as_the_main_packs_ladder`、`the_cage_numbers_come_from_the_champion_data`。
