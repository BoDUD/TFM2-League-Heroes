# 辛吉德附加包（测试版 v0.1.2）

主包 `league` 保持纯数据。用户 2026-10-23 说「这个做附加包啊」：主包过肩摔的两处近似放到这个附加包里，用原生代码按英雄联盟的规则做；
画面、声音仍然在主包的数据里：

| | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 过肩摔怎么飞 | 没有击飞：`Pull` 把目标从他身上拉过去，落到身后（数据里击飞和拉扯同时上，目标会被定在原地） | **击飞** `e_fly` tick（16），从他头顶飞过、落到他身后 `e_behind`（30000）远；路上碰到墙就落在墙边 |
| 落进粘胶禁锢 | 数据读不到单位站在哪：**只要地上有他的强力粘胶**，被摔的就禁锢 `e_root` tick | **真的落进胶里才禁锢** `e_root` tick（60） |

## 怎么做的

- 副本里过肩摔抓住目标的那一 tick 调原生效果 `league_singed:fling`：算出从目标经过他、再往后 `e_behind` 的落点（地图墙格同波比附加包），
  给目标上击飞，然后每 tick 排一次 `league_singed:fly` 把它往落点挪一段（`entity_set_pos`），一共 `e_fly` 步正好落地。
- 落地后排三次 `league_singed:land` 查看（落地后第 1、4、8 tick 左右，盖住粘胶每 `w_p` = 6 tick 一次的减速）：目标身上有粘胶的减速
  `league_singed_w_slow` 就是落在胶里——禁锢，播 `league_singed_e_root` 的画面和声音。飞的途中每 tick 都摘掉这个减速，所以起飞前站的胶、
  空中经过的胶都不算。
- 免控（`cc_immune`）的目标不飞也不禁锢。

参数由 `make_override.py` 从 `tools/kit/build_singed.py` 的参数表 `P` 核对（`src/lib.rs` 的 `E_FLY`、`E_BEHIND`、`E_ROOT`、`W_P`
不一致就停）。

## 在游戏里测

1. 主包（League of Legends Heroes，含辛吉德的版本）要装着并启用。
2. 用附加包合集 `league_addons`，或者把整个 `league_singed` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_singed.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_singed.log`——`FLING`（从哪摔到哪、有没有墙）、`ROOT`（落进胶里）、
   `MISS`（没落进胶里）。

## 0.1.2：毒雾和胶水第一下不再晚（2026-11-06）

Q 的毒雾（`q_cloud`，每 30 tick 一次伤害）第一下晚 30 tick；他在毒雾里的标记（`q_me`，每 3 tick）晚 3 tick；W 的胶水（`w_glue`，每 6 tick 减速 + 禁锢位移）晚 6 tick。现在都是下一 tick 就生效，每团毒雾多一跳。经典 SDK 实测（2026-11-06，`trace.exe` 逐 tick 看每个区域第一次生效）：区域出现后第 `first_delay` tick 才第一次生效，写 0 等于晚整整一个周期（从飞行物落点生成的晚 `period` tick，从延迟或技能里直接生成的晚 `period - 1` tick）。改成 1 后，从落点生成的落地下一 tick 就生效，从延迟里生成的出现当 tick 就生效。主包的数据跟着改，本包的副本用 `make_override.py` 重新生成；DLL 没变。
