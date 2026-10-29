# 加里奥附加包（测试版 v0.1.1）

主包 `league` 保持纯数据。用户选了「主包数据 + 附加包」。这个附加包用原生代码做主包数据做不到的三件事：

- **杜朗护盾的被动护盾按「多久没挨打」给**：主包里加里奥普攻时给护盾（每 12 秒最多一次），因为数据读不到「多久没受伤」。
  附加包的被动 `league_galio:colossus` 记下他最后一次受伤的 tick，**12 秒没受伤**就给 90 + 30% 法强的护盾（5 秒），护盾还在不重给。
  英雄联盟里这个护盾只挡魔法伤害；被动的受伤钩子不带伤害类型，所以这里**挡所有伤害**。
- **W 的嘲讽按身边英雄数**：英雄联盟里蓄力越久嘲讽越久（0.5–1.5 秒），人多时会蓄满。附加包的 `league_galio:taunt` 在 W 放开时
  数他身边（W 的半径以内）的敌方英雄：1 个 0.75 秒、2 个 1.17 秒（主包的数）、3 个及以上 1.5 秒。
- **英雄登场选人**：主包读不到血量，只能挑「被控的」或「身边连续两次有敌人的」友军。附加包的 `league_galio:entrance` 在每次轮询时
  看所有友方英雄：离他够远、身边有敌方英雄、确实在苦战（被控 / 血量 80% 以下 / 身边两个以上敌人）的里面，**被控的优先，再挑血量比例最低的**，
  落点周围敌方英雄多的优先（每多一个当作血量少 10%）。选中谁，数据就给谁护盾、引导、飞过去。
- **引导只被硬控打断**（0.1.2）：主包每 15 tick 用 `AllyChampionInCC` 查他自己有没有被控，被控就打断引导。游戏 0.7.0 起玩家说加里奥
  不开大；游戏的控制列表里也有他自己正在播的施法动作，那个查法可能把引导动作本身当成被控、每次都打断。副本去掉数据的这个查法，
  改由附加包每 tick 看他有没有被硬控（击飞、眩晕、定身、嘲讽、恐惧、魅惑、强制位移），有才打断；自己被硬控时也不选人。

数字：被动的参数写在英雄数据的 `passive.params`（`{"ps": 90, "ps_ap": 30, "ps_t": 300, "w_r": 26000, "w_taunt": 70, "r_far": 60000, "r_sur": 25000, "r_r": 22000}`），
由 `make_override.py` 从 `tools/kit/build_galio.py` 的参数表 `P` 写入；`PS_IDLE`、`TAUNT_ONE`、`TAUNT_MANY`、`CALM_HP` 写在 `src/lib.rs`，单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.106 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_galio` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_galio.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看加里奥的技能说明：普攻、E、R 开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_galio.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `WARD #3: 132 shield after 731 ticks untouched`：被动护盾；
   - `TAUNT #5 Jinx#12: 90 ticks (3 enemy champions near)`：嘲讽；
   - `ENTRANCE #2 -> Ashe#7: hp 34% in cc, 2 enemy champions near, 2 where he lands, 84000 away`：大招选人；
   - `CHANNEL #2: R channels (crowd control on him [11])`：开始引导（方括号里是他身上的控制种类）；
   - `BROKEN #1: hard crowd control [0] 40 ticks into the channel`：引导被硬控打断；
   - `LANDED #2: the channel ended after 120 ticks, moved 84000`：飞过去落地；`NO FLIGHT`：引导结束却没飞（要查）。

## 开发

- `python addons/league_galio/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的加里奥和参数表一致）。
  主包的加里奥改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_galio`：单元测试（嘲讽时长、选人、参数、和参数表一致）。
- 在 `addons/` 下 `cargo build --release -p league_galio`（Windows）得到 `target/release/league_galio.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
