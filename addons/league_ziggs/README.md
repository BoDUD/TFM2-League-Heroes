# 吉格斯附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户选了小扩展包（「可以」）。这个附加包用原生代码做主包数据做不到的两件事——它们都要读防御塔的血量：
**定点爆破炸塔**和**一触即发打塔加成**。画面、声音仍然是主包里的那一套（附加包只判断，在塔上播主包的爆炸画面）：

| | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 定点爆破（W） | 3 级起，敌方英雄贴身时自动在脚下引爆：伤害、击退敌人、自己被炸开 | 同上；另外 W 不在冷却时，身边 `w_hex_r` 以内有**血量低于 `w_ex`% 的敌方防御塔**，就在塔上炸开、直接把塔炸掉（算他的击杀），W 进入冷却（英雄联盟：W 能炸掉 25–35% 血以下的防御塔） |
| 一触即发（被动） | 每 12 秒（放技能减 4 秒）下次普攻多一份魔法伤害，打塔和打别的一样 | 强化弹打中防御塔的那一下 ×`p_tower`%（1.75 倍，英雄联盟对建筑的加成） |

## 怎么做的

- **炸塔**：每 tick 看他：活着、3 级以上、没有数据的 `league_ziggs_w_cd`（W 在冷却）也没有 `league_ziggs_busy`（在放别的技能）时，
  找身边 `w_hex_r` 以内、血量 ≤ 最大值 `w_ex`% 的敌方防御塔；找到就在塔的位置播 `league_ziggs_w_blast` 的画面和声音、他的 W 台词，
  用真实伤害打掉塔剩下的血（引擎自己的伤害流程：击杀算他的），再给他挂 `league_ziggs_w_cd`（`w_cd` tick，和数据里放一次 W 一样）。
  本包**不按任何技能键**（不会在技能没解锁时按键，解锁总闸也不涉及）。
- **打塔加成**：副本里被动强化弹打中时给他挂 2 tick 的 `league_ziggs_p_now`；本包的 `on_attack` 看到它、目标又是防御塔，就把这一下伤害
  ×`p_tower`%（整下，含普攻本身的部分）。

参数写在英雄数据的 `passive.params`（`{"p_tower": 175, "w_cd": 900, "w_ex": 30, "w_hex_r": 100000}`），由 `make_override.py` 从
`tools/kit/build_ziggs.py` 的参数表 `P` 写入。

## 在游戏里测

1. 主包（League of Legends Heroes 0.140 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_ziggs` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_ziggs.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看吉格斯的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ziggs.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN`：出生；`HEXPLODE`：W 炸掉一座塔（塔的血量、他的位置）；`FUSE`：强化弹打塔（加成前后的伤害）。

## 开发

- `python addons/league_ziggs/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的吉格斯和参数表一致）。
  主包的吉格斯改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_ziggs`：单元测试（参数、炸塔的血量线、距离、打塔倍率）。
- 在 `addons/` 下 `cargo build --release -p league_ziggs`（Windows）得到 `target/release/league_ziggs.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
