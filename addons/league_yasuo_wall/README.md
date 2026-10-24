# 亚索风之障壁附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「还有个亚索风墙吧？但是亚索风墙要智能点放啊」「你要做风墙的特效也一起把压缩包整理了」。

主包没有 W：游戏里没有能挡掉飞行物的效果，只画一面墙显得奇怪，当时用户决定删掉。亚索也没有空的技能格，所以风墙全由原生代码做（被动 `league_yasuo_wall:wall`，不占技能格、没有施法动作）。

- **什么时候放**：墙好了（冷却 20 秒，2 级起），亚索没被硬控，敌方英雄的飞行物正朝亚索或 50000 内的队友飞来、4000-32000 内就要打到：这样的飞行物有 2 个以上，或者有一个是冲着生命不高于 40% 的人去的。飞行物的方向按它这一 tick 和上一 tick 的位置算。
- **放在哪**：亚索身前 24000，朝着来袭飞行物的平均方向，墙和这个方向垂直，长 44000，中间往敌人那边鼓 5000（英雄联盟的弧形墙），4 秒。
- **画面像英雄联盟**（用户：「跟着方向转有点奇怪啊风墙 做成像英雄联盟那样啊」）：墙脚是地上的一条弧线，跟着墙的方向；风永远往上升，图不转。Codex 画的墙（`assets/source/yasuo/windwall/yasuo_w_wall_loop.png`）由 `tools/art/import_yasuo_wall.py` 切成 7 段竖着的风（`league_yasuo_w_plume_0`..`6`），沿墙脚从屏幕左到右（竖着的墙从上到下）摆开，墙脚每 1600 放一个地上的小点（`league_yasuo_w_ground`）。
- **挡住**：敌方英雄的飞行物从墙的一边穿到另一边就算被挡，在穿过的地方播挡住的画面。引擎删不掉飞行物，所以它之后打到的友方英雄（它的路线 12000 内、这一 tick 掉了血的）把伤害补回去，这一 tick 新挂上的控制也清掉。塔的炮弹不挡。**飞行物的图还会继续飞到人身上**（只是没有伤害），这是引擎的限制。

出手的风、挡住的一下、墙散掉（特效包第 6-8 张）Codex 还没画，现在只有墙本身。

## 在游戏里测

1. 主包（League of Legends Heroes 0.210.0 以上）要装着并启用。
2. 把 `league_yasuo_wall` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 亚索普攻的说明开头是「【附加包】」、末尾有「风之障壁」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yasuo_wall.log`：`WALL #n at (x, y) facing (1.00, 0.00): 2 missiles coming, 7 of 7 pieces shown`、`BLOCKED #n: a missile of #7`、`SAVED #3: 85 damage given back`。

## 开发

- `python tools/art/import_yasuo_wall.py [--preview DIR]`：重新切墙的画面；`python addons/league_yasuo_wall/make_override.py`：重新生成副本（`--check` 只比较）。
- `cargo test -p league_yasuo_wall`（在 `addons/` 下）。
