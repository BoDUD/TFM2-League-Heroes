# 泰隆「刺客之道」翻墙附加包（v0.1.0，可选）

用户：「有墙啊 青钢影不是勾墙了？」——5v5 地图的野区里有引擎的碰撞墙（30 × 30 格、每格 32000，共 90 格，卡蜜尔钩墙附加包读的同一份），
英雄联盟里泰隆的 E 就是翻过这种墙。主包是纯数据，读不到墙，所以主包里的刺客之道是空地上的撤离。

**不装这个附加包，主包里的泰隆也是完整的**：刺客之道在主包里是收刀或 Q 击杀时被包围就背向敌人翻身跃开，动作、画面、音效、加速都在主包里。
这个附加包只补上数据做不到的「看墙」：

| | 主包（纯数据） | 装了附加包（照英雄联盟） |
|---|---|---|
| 什么时候翻 | 收刀或 Q 击杀时身边有 2 名敌方英雄 | 照旧，另外：残血（低于 35%）而身边有敌方英雄，或被围（身边敌方英雄 ≥ 2、比身边友方多、生命低于 70%）时；残血敌方英雄（≤ 60%）躲在墙后、他自己生命 ≥ 40% 时 |
| 往哪翻 | 空地上背向一名敌人跃开 36000 | **翻过墙**：撤离时找背向敌人、16000 内的墙翻到另一边（落地后离敌人最远的那处）；追击时朝目标左右 35° 内找墙翻过去，落点要近 15000 以上、不翻进人堆 |
| 冷却 | 10 秒 | 同一个冷却（主包的 `league_talon_e_cd`），两种翻越不会连着出 |

## 怎么做的

- `mod.override_info` 把主包的泰隆换成 `override/` 里的副本（`make_override.py` 从主包生成，主包的泰隆改了就重跑）：
  - 数据和主包逐字相同（`tools/kit/build_talon.py` 的 `native=1`，脚本先核对不带它的构建就是主包的文件），空地上的翻越照旧；
  - `passive` 挂本包的被动 `league_talon_vault:path`，参数是参数表 P 里刺客之道的数字（`e_cd`、`e_safe_r`、`e_crowd`、`e_speed`、
    `e_anim`、`e_haste`、`e_haste_t`、`e_low`、`e_reach`、`e_far`、`e_chase_r`、`vo_gap`）；
  - 加一个 buff 画面 `league_talon_e_wall`（主包刺客之道的弧光帧，贴着他）：原生代码播的画面没验证过一定显示（剑魔锁链的教训），
    翻墙的弧光由被动挂这个 buff 来显示；
  - 普攻说明换成 `description.league_talon_vault.attack`（开头「【翻墙版】」），游戏里看说明就知道副本生效了没有。
- 被动 `path`（`src/lib.rs`）每 3 tick 看一次，刺客之道好了（身上没有 `league_talon_e_cd`）、没被控、不在强制位移里时，判断撤离或追击，
  挑好墙就翻：挂主包的冷却标记、播 `skill_e` 动作、挂弧光 buff、穿墙的强制位移（速度 `e_speed`，期间无视地形；宿主没挪他时逐 tick 自己走
  一步，凯隐穿墙的做法）、刺客之道的音效和台词（台词照主包隔 `vo_gap`），落地后加速 `e_haste`%（主包的 `e_haste` buff，画面也是主包的）。
- 这局是哪张地图：站在墙格里的英雄最少、墙又最多的那张（一个正在穿墙的凯隐不会让它认错图）。
- 本包只换泰隆，别的英雄原样不动。

## 在游戏里测

1. 主包（League of Legends Heroes 0.87 以上）要装着并启用。
2. 玩家装的是附加包合集 `league_addons`（见 [`../league_addons/README.md`](../league_addons/README.md)），泰隆的部分和这里一样；
   单独测时把整个 `league_talon_vault` 文件夹放进 `<游戏目录>\mods\`（要有 `league_talon_vault.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`），在 MOD 菜单里启用、排在主包后面、关掉合集，重启游戏。
3. 看泰隆普攻的说明：开头是「【翻墙版】」就说明副本生效了。
4. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_talon_vault.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `VAULT #3 out: (412000,288000) -> (452000,281000) (40610, 14 ticks), hp 28%`：残血或被围，翻墙撤离；
   - `VAULT #4 after #7: ...`：翻墙追击 7 号实体（隔墙的残血英雄）。

## 生成和测试

```bash
python addons/league_talon_vault/make_override.py      # 副本和文字（主包的泰隆改了就重跑）
cd addons && cargo test -p league_talon_vault          # 墙、撤离、追击、认图的单元测试
cd addons && cargo build --release -p league_talon_vault
```
