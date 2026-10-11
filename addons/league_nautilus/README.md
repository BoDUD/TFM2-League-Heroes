# 诺提勒斯钩墙附加包（测试版 v0.1.0）

主包 `league` 保持纯数据、全平台可用；钩墙要读地图的墙，只能用原生代码，所以放在这个附加包里（合集 `league_addons` 也带着它）。
装上后，诺提勒斯的 Q「疏通航道」：锚沿路线**先碰到野区的墙**（引擎的碰撞墙，5v5 地图 90 格）时，把他拉到墙边，并**返还一半冷却**——
和英雄联盟一样；先碰到敌方英雄时照主包钩人（两人拉向彼此）。

- 锚飞出去的那一 tick，主包副本（`override/`，tools/kit/build_nautilus.py 的 native=1）调本包的 `league_nautilus:hook`：
  沿 Q 的方向找 85000 内的第一面墙；路线上（离路线 10000 + 身体 6000 以内）墙前有敌方英雄就什么都不做（主包的锚会钩他）。
- 墙比 12000 近不钩。锚按 6000/tick 飞到墙上时（`pull`）：强制位移把他拉到离墙 3000 处（速度 2500/tick，动作 `skill_pull`），
  播钩墙音效和钩中的水花；冷却：`skill_cooldown_mult` +100 的 3 tick buff——Q 剩下的冷却封顶到一半（W+E 若剩得更多也一起封顶：
  引擎没有只给一个技能的字段）。
- 被硬控、死了就不拉；宿主没挪他时逐 tick 自己走一步（`watch`）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.94 以上）要装着并启用。
2. 用合集 `league_addons`（推荐），或把整个 `league_nautilus` 文件夹放进 `<游戏目录>\mods\`（两者不能同时启用）。
3. 看诺提勒斯 Q 的说明：开头是「【钩墙版】」就说明副本生效了。
4. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nautilus.log`：`HOOK the wall` 是锚飞向墙，`PULL to the wall` 是拉过去。

## 开发

- `python addons/league_nautilus/make_override.py`：从主包重新生成 `override/` 和 `text/`。主包的诺提勒斯改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_nautilus`：单元测试（锚先咬墙、墙前的英雄归主包钩、墙太近或太远、地图、数值和主包一致）。
