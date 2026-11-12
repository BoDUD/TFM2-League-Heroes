# 嘉文四世附加包（测试版 v0.1.4）

0.1.2（2026-11-05）：待命式大招没用掉时的冷却退还从来没生效过：n tick 的待命标记只有 n - 1 tick 看得见（经典 SDK 探针 lr1105/fix_j：n - 1 之前 148/148 次看得见，第 n tick 0 次），退还在窗口最后一 tick 读它时已经没了，所以每次待命过期都要等完整冷却（塞恩追踪：过期到再待命 3558 tick，改读后 877）。现在在窗口结束前 3 tick 读（`tools/kit/build_jarvaniv.py`），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

主包 `league` 保持纯数据。用户选了「全按推荐做：打野、布局A、做扩展包」。这个附加包用原生代码做主包数据做不到的一件事：天崩地裂的**真岩墙**。
画面、声音、伤害仍然在主包的数据里（附加包只判断、只移动单位）：

| | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 天崩地裂的岩墙环 | 落地后 `r_t` tick（3.5 秒）困住**落点周围的敌方英雄**：每 `r_lp` tick 探一次，离他超过 `r_leash` 就被拉回他身边（照卡蜜尔大招）；他自己走出岩墙环，环就塌了 | **真的墙**：以落点为圆心、`r_r` 为半径立一圈墙 `r_t` tick。立墙时在圈里的单位（两边的英雄、小兵、野怪、召唤物，他自己也算）出不去，在圈外的进不来 |

## 怎么做的

- 数据在他落地那一 tick 给他挂 `league_jarvaniv_r_on`；附加包看到它新出现，就以他那一 tick 的位置为圆心立墙，记下每个单位当时在哪一侧。
- 之后每 tick 单位的中心一碰到墙（圈里的离圆心超过 `r_r` − 单位半径，圈外的不到 `r_r` + 单位半径），就放回上一 tick 的位置；
  上一 tick 也不在该在的一侧时（冲刺、击退一步跨过墙），沿圆心方向推回墙的内侧 / 外侧。
- 副本里没有主包那套「探测 + 拉回」和「他走出环就塌」（墙真的挡路，不需要了）。

0.1.1：副本跟着主包 0.139.3 改成 3 级前技能 1 只扔旗、3 级起才接巨龙撞击（原生代码没变）。

参数写在英雄数据的 `passive.params`（`{"r_r": 36000, "r_t": 210}`），由 `make_override.py` 从 `tools/kit/build_jarvaniv.py` 的参数表 `P` 写入。

## 在游戏里测

1. 主包（League of Legends Heroes 0.139.3 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_jarvaniv` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_jarvaniv.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看嘉文四世的大招说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_jarvaniv.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN`：出生；`RING`：立墙（圆心、半径、持续 tick）；
   - `KEPT IN` / `KEPT OUT`：把单位挡在圈里 / 圈外（0.1.2，2026-11-05：一个单位一道墙只记第一下；11-04 的日志 42 道墙记了 976 行，
     挡着的每 tick 一行）；
   - `LEAPT IN` / `LEAPT OUT`：闪现、飞越过墙放行（0.1.3）；`THROUGH IN` / `THROUGH OUT`：无视地形的单位穿过墙（0.1.4）。

## 开发

- `python addons/league_jarvaniv/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的嘉文四世和参数表一致）。
  主包的嘉文四世改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_jarvaniv`：单元测试（参数、圈里的出不去、圈外的进不来、按立墙时的一侧判断、闪现和飞越过墙放行、无视地形的单位穿墙）。
- 在 `addons/` 下 `cargo build --release -p league_jarvaniv`（Windows）得到 `target/release/league_jarvaniv.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。

## 0.1.3：闪现、飞越过墙放行（2026-11-12）

11-12 的日志（用户：「和前几次一样 分析一下今天跑的日志 看看有没有bug」）：加里奥 71 次大招里 8 次没飞起来（`league_galio.log` 的 `NO FLIGHT`：`set_pos` 成功了，下一 tick 他又站回原地）。这 8 次所在的 6 局里都有嘉文四世，其中两次同一 tick 就记到 `KEPT OUT ... league_galio`（嘉文的 `KEPT` 一个单位一道墙只记一行，之后每 100 行记一行，所以另外几次没记下来）。

原因：岩墙环每 tick 把碰墙的单位放回上一 tick 的位置，不管它是走过来的还是一下瞬移过来的。加里奥的英雄登场一 tick 飞出去 8 万到 30 多万，正好越过墙，就被放回了原地。

英雄联盟里天崩地裂的墙挡不住闪现和越墙的位移（加里奥的大招、闪现）。现在：
- 一 tick 里挪了 `BLINK`（15000）以上算闪现 / 飞越，不碰墙，放过去。走路每 tick 几百，数据里的冲刺最快几千，闪现约 4 万。
- 放过去以后这个单位按落在的那一侧算：飞出去的进不来，飞进来的出不去。
- 日志 `LEAPT OUT` / `LEAPT IN`：谁、从哪到哪。
- 单元测试 `a_blink_or_a_flight_crosses_the_wall`。

## 0.1.4：无视地形的单位穿得过岩墙环（2026-11-12）

用户：「我们的蝎子能穿墙吗」「不能的话就改 联盟的可以穿墙」。斯卡纳的以绪塔尔冲击带无视地形（`league_skarner_e_ghost`，`ignore_wall`），地图上的墙挡不住他（经典引擎的模拟：48 局里冲锋时他和目标隔着墙格的 41 次，全都直接穿了过去）。可岩墙环只放过一 tick 挪 `BLINK` 以上的闪现和飞越，他冲锋每 tick 3000，撞上就被放回原处。

英雄联盟里英雄造的墙也算地形，无视地形的位移穿得过去。现在：
- 身上有 `ignore_wall` 的 buff 的单位不碰墙，穿过去；以后按它站的那一侧算（和闪现一样）。
- 带这种 buff 的：斯卡纳的以绪塔尔冲击、凯隐的掠影步、奥瑞利安·索尔和斯莫德的飞行，附加包里泰隆、巴德、阿萝拉的穿墙位移。
- 日志 `THROUGH OUT` / `THROUGH IN`：谁、哪个 buff、在哪；一个单位一道墙只记一次。
- 单元测试 `a_unit_ignoring_terrain_walks_through_the_wall`、`only_a_buff_ignoring_terrain_goes_through`。

冰鸟的冰墙（`league_anivia` 0.1.10）、巨魔的冰柱（`league_trundle` 0.1.3）、奥恩的熔岩柱、塔莉垭的墙幔同样放过。
