# 青钢影钩墙附加包（测试版 v0.0.1）

主包 `league` 保持纯数据、全平台可用；钩墙要读地图的墙，只能用原生代码，所以放在这个单独的附加包里。

**这一版只观测，不改玩法**。它用来确认三件事：
1. 附加包能不能替换主包的青钢影：`mod.override_info` 把 `asset/league/champion/league_camille` 指到 `override/` 里的副本。
2. 原生代码能不能读到地图的墙（30×30 格，每格 32000）。
3. 实战中每次 E 出手时，附近有没有墙可钩。

## 在游戏里测

1. 主包（League of Legends Heroes 0.48 以上）要装着并启用。
2. 把整个 `league_camille_wall` 文件夹放进 `<游戏目录>\mods\`（游戏目录一般是 `Steam\steamapps\common\Teamfight Manager2`）。
3. 进游戏，在 Mods 菜单里启用它，确认排在主包后面。
4. 看青钢影 E 的说明：开头是「【钩墙测试版】」就说明替换成功。再看一眼英雄列表里是不是只有一个卡蜜尔。
5. 用青钢影打两三局（自定义对局就行），让她多放几次 E。
6. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_camille_wall.log`（把这串路径粘到资源管理器地址栏就能打开）。每次启动游戏会清空重写。

## 日志怎么读

- `== map mode=Moba ==`：地图的墙格子，`#` 是墙，下面是基地、泉水、塔、野怪、兵线的坐标。
- `probe=engage` / `probe=escape`：E 出手的那一刻。
  - `A[y][x]` 和 `B[x][y]` 是格子的两种读法。英雄不会站在墙里，所以 `champs_in_wall` 一直是 0 的那种读法是对的。
  - `walls_in_range` 表示 32 个方向里，射程（60000）内有墙的方向数。
  - `engage=` 是离敌方英雄最近的钩点；`escape=` 是离敌人最远的钩点；`none` 表示没有。

## 开发

- `python addons/league_camille_wall/make_override.py`：从主包重新生成 `override/` 和 `text/`。主包的青钢影改了以后要重跑。
- `cargo test --release`：单元测试，加上一个走真实导出入口的接线测试。
- `cargo build --release --target x86_64-pc-windows-gnu`：在 Linux 上交叉编译 Windows 版，产物是 `league_camille_wall.dll`。在 Windows 上直接 `cargo build --release`。
