# 泽丽附加包（测试版 v0.1.0）：W 撞墙激光 + 被动偷盾

用户选泽丽技能时说：「打到小兵/野怪就变激光 这个可以做附加包」「普攻充能+强化弹+护盾 这个也是」。主包 `league` 保持纯数据：
数据读不到地图的墙，也读不到敌人身上的护盾，所以主包里

- W「强穿激光」的脉冲**先打中小兵或野怪**时才在那里化为长激光（小兵代替墙）；
- 被动「内能迁转」的电击弹打中英雄时给自己一个**小护盾**（代替偷盾）。

这个附加包把主包的泽丽换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_zeri.py` 的 `--native` 生成：技能一样，
只是 W 的脉冲飞出时在她身上挂 `league_zeri_w_go`、她身上有 `league_zeri_w_wall` 时脉冲什么都不打；电击弹不再给小护盾；普攻和
W 的说明写上偷盾和撞墙），被动 `league_zeri:battery` 每 tick 看一次：

- **撞墙激光（英雄联盟原版）**：看到 `w_go`，找出她刚射出的脉冲（下一 tick 飞了约一步的那个投射物），之后逐 tick 跟着它；
  它这一 tick 走过的线段碰到**墙格**（引擎的碰撞墙，30×30 格、每格 32000，`src/maps.rs` 是 game_core 0.5.1 的内置地图，
  与游戏 0.6.2 相同）或 **5v5 地图四边的墙面**，就在那里挂 `w_wall`（数据的脉冲到此为止），并从碰到的地方沿原方向射出
  100000 长的激光（穿透的投射物 `league_zeri_w_wall`），打中的每个敌人受到 60 + 110% 攻击力的物理伤害并减速 35% 2 秒
  （同主包的 W）。脉冲先打中了单位（数据照常处理：小兵、野怪化激光，英雄单体伤害）或飞完了，就不再跟。小兵化激光照旧保留。
- **偷盾（英雄联盟原版）**：她的伤害（普攻、技能都算）打到带护盾的敌人时，被护盾挡下的那部分的 **45%** 变成她自己的护盾，
  持续 3 秒，身上显示护盾的图。电击弹的移速照旧。

数字从英雄数据的 `passive.params` 来。只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zeri.log`（`map:` 认出的地图；`W #n: pulse fired` 每次 W；
`the pulse met a wall at ... - laser to ...` 撞墙出激光；`STEAL #n` 偷了谁的护盾、多少）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.93 以上）要装着并启用。
2. 把整个 `league_zeri` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_zeri.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看泽丽 W 的说明：写着「先打中小兵、野怪或撞到墙时」就说明换上了。

## 开发

```bash
python addons/league_zeri/make_override.py      # 主包的泽丽或她的说明改了就重跑
cd addons && cargo test --release -p league_zeri && cargo build --release -p league_zeri
```
