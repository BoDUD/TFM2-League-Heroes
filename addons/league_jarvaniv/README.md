# 嘉文四世附加包（测试版 v0.1.1）

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
   - `KEPT IN` / `KEPT OUT`：把单位挡在圈里 / 圈外。

## 开发

- `python addons/league_jarvaniv/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的嘉文四世和参数表一致）。
  主包的嘉文四世改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_jarvaniv`：单元测试（参数、圈里的出不去、圈外的进不来、按立墙时的一侧判断）。
- 在 `addons/` 下 `cargo build --release -p league_jarvaniv`（Windows）得到 `target/release/league_jarvaniv.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
