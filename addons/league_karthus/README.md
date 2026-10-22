# 卡尔萨斯附加包（测试版 v0.2.0）

主包 `league` 保持纯数据。用户选了「被动做附加包」。这个附加包用原生代码做主包数据做不到的**死亡契约**：

- 英雄联盟里卡尔萨斯死后化成灵体，7 秒内照样放技能，然后才倒下。数据读不到血量，主包做不了。
  附加包的被动 `league_karthus:death_defied` 每 10 tick 给他挂一个 30 tick 的不死 buff `league_karthus_p_guard`，
  这样致命伤害只会把他打到 1 血。他到 1 血（并且身上没有别人给的不死，比如基兰的大招）时就**化成灵体** `p_t` tick（420 = 7 秒）：
  - 隐身：敌人选不中他（`entity_set_invisible`，每 30 tick 续一次）；
  - 不再受伤（`damaged_reduce` 100%）、免疫控制；
  - 照常走动、放技能、攻击；
  - 身上挂 `league_karthus_p_spirit`（附加包的副本里绑了灵体的画面），播灵体音效和台词。

  - **灵体时 AI 照常打**（0.2.0）：游戏的 AI 看他 1 血就逃跑或回城，灵体 7 秒白白浪费。本包的 AI 钩子
    `league_karthus:spirit_ai`（优先级 105，在 league_ult_press 之后）在灵体期间按：R（全图，近的英雄先）> Q（8 万内）>
    E（4 万内）> 普攻最近的敌方英雄（够不着就走过去）；正在施法（R 的引导）时不按。

  时间到灵体倒下：按固定伤害记在最后打他（化成灵体之前）的人头上。每条命都有（英雄联盟每次死亡都会触发）。
  只有这条命里见过他 1 血以上之后，1 血才算致命伤（赛恩附加包的教训：游戏 0.6.4 开局第 0 tick 读到的血量是 0）。

数字：被动的参数写在英雄数据的 `passive.params`（`{"p_t": 420}`），由 `make_override.py` 从 `tools/kit/build_karthus.py`
的参数表 `P` 写入；`GUARD_T`、`GUARD_EVERY`、`HIDE_EVERY` 写在 `src/lib.rs`，单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.175 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_karthus` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_karthus.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看卡尔萨斯的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_karthus.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Karthus (player 0, team 0), ...`：出生；
   - `SPIRIT #1: lethal damage caught at 1 hp (last hit by ...), a spirit for 420 ticks`：化成灵体；
   - `SPIRIT KILL #1: ... killed by the spirit`：灵体击杀了英雄；
   - `FALL #1: the spirit's time is up, killed by ...`：灵体倒下。
   - `SPIRIT AI #1: Ult on ... (the game's AI: Move)`：灵体时钩子替 AI 放了技能（普攻记成 Attack）。

## 开发

- `python addons/league_karthus/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的卡尔萨斯和参数表一致）。
  主包的卡尔萨斯改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_karthus`：单元测试（别人给的不死、隐身续期、参数、和参数表一致）。
- 在 `addons/` 下 `cargo build --release -p league_karthus`（Windows）得到 `target/release/league_karthus.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
