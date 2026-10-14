# 玛尔扎哈附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户选了「做：E 跳转 + 被动精确」。这个附加包用原生代码做主包数据做不准的两件事：

- **虚空穿越（被动）**：英雄联盟里玛尔扎哈身上有一层法术护盾：受到的伤害大幅减少、免疫控制；被非小兵的伤害打中后很快消失，
  一段时间没受到英雄伤害才回来。主包数据读不到「被谁打了」「多久没挨打」，只能做成墨菲特那样的护盾（打破后过一会儿回来）。
  附加包的被动 `league_malzahar:void`：
  - 准备好时给他挂 `league_malzahar_p_shift`：受到的伤害减少 `p_dr`%（90%）、**免疫控制**；画面是主包数据里绑的 `p_shift`；
  - 第一次被**英雄、野怪或防御塔**打中后再持续 `p_linger` tick（0.25 秒）就消失；**小兵**的伤害照样减少，但打不破它；
  - 消失后，**`p_cd` tick 内没受到英雄伤害**才重新准备好（每挨一次英雄伤害重新计时）；每条命开始时是准备好的。
- **煞星幻象的跳转**：主包数据里幻象的目标死了只能跳一次，而且晚零点几秒（数据看不到死亡，靠打标记再检查）。
  附加包里幻象每打中一个单位都会调用原生效果 `league_malzahar:vision` 记下它；目标在幻象的 `e_t` tick（4 秒）内死了，
  **立刻**跳到它倒下处 `e_jump`（40000）内最近的敌人身上：**先找英雄**，没有再找小兵、野怪，不找防御塔。
  新目标重新受到完整的幻象（`e_t` tick 内每 `e_p` tick 一段，共 `e_dmg` + `e_ap`% 法强的魔法伤害，由附加包结算），
  头上挂 `league_malzahar_e_markb`（主包数据里绑了幻象的画面）；它死了照样再跳，**没有次数限制**。
  英雄联盟里跳转还会刷新 E 的冷却；TFM2 的冷却加速 buff 会把 Q 一起刷新，所以不做。

数字：被动的参数写在英雄数据的 `passive.params`（`{"p_cd": 720, "p_linger": 15, "p_dr": 90, "e_t": 240, "e_p": 15,
"e_dmg": 170, "e_ap": 80, "e_jump": 40000}`），由 `make_override.py` 从 `tools/kit/build_malzahar.py` 的参数表 `P` 写入；
单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.111 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_malzahar` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_malzahar.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看玛尔扎哈的普攻和技能说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_malzahar.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Malzahar (player 2, team 0), ...`：出生（虚空穿越准备好）；
   - `SHIFT #3: struck by Ahri#14 (85), Void Shift fades in 15 ticks`：被非小兵打中，0.25 秒后消失；
   - `SHIFT #4: Void Shift spent, back after 720 ticks without champion damage` / `SHIFT #5: Void Shift ready again`；
   - `JUMP #2: caster_minion#40 fell, the vision moves to Ahri#14 (240 ticks, 13 a part)`：目标死了，幻象跳走；
   - `JUMP #6: ... fell under the vision, no enemy within 40000`：附近没有敌人，幻象结束。

## 重新生成

主包的玛尔扎哈改了以后：`python -X utf8 addons/league_malzahar/make_override.py`（先核对主包的数据和参数表一致）。
