# 赛恩附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户选了「主包数据 + 附加包复活」。这个附加包用原生代码做主包数据做不到的两件事：

- **死亡荣耀（复活成亡灵）**：英雄联盟里赛恩每条命第一次被打死时会站起来继续打一阵。数据读不到血量，主包做不了。
  附加包的被动 `league_sion:glory` 在他这条命还没复活过时，每 10 tick 给他挂一个 30 tick 的不死 buff `league_sion_p_guard`，
  这样致命伤害只会把他打到 1 血。他到 1 血（并且身上没有别人给的不死，比如基兰的大招）时就**变成亡灵**：
  - 生命回满，之后每 tick 掉 最大生命 ÷ `z_t`；
  - 攻速 +`z_as`%，吸血 `z_vamp`%；
  - 不能放技能（`BlockSkill` 控制，`z_t` tick）；
  - 播起身音效和台词。

  `z_t`（540 tick = 9 秒）结束时亡灵倒下：按固定伤害记在最后打他的人头上。
  只有这条命里见过他 1 血以上之后，1 血才算致命伤：游戏 0.6.4 开局第 0 tick 读到的血量是 0，之前每局一开场他就变成亡灵、
  9 秒后倒下（「开局血掉光」）。
  亡灵身上的 buff `league_sion_p_zombie` 在主包的数据里绑了特效 `p_zombie`（身边暗红色的死亡之火、小骷髅鬼火往上飘）。
- **灵魂熔炉的击杀加生命**：主包里普攻打死单位加 6 点（数据只认得出普攻的击杀，buff 死后清空）。
  附加包按英雄联盟来：**每次击杀**（技能、大招的也算）永久加最大生命：小兵、野怪加 `k_u`（4），英雄加 `k_c`（15）。小兵、野怪那份要游戏 0.6.4 起的 `on_unit_kill`（之前原生被动只有英雄击杀的回调，附加包里打死小兵野怪一直没加上）。
  这个加成**阵亡后不丢**（buff `league_sion_k_hp` 每次出生重新挂上）。附加包里的赛恩不带主包普攻的击杀检测，免得加两次。

数字：被动的参数写在英雄数据的 `passive.params`（`{"k_u": 4, "k_c": 15, "z_t": 540, "z_as": 60, "z_vamp": 100}`），
由 `make_override.py` 从 `tools/kit/build_sion.py` 的参数表 `P` 写入；`GUARD_T`、`GUARD_EVERY` 写在 `src/lib.rs`，单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.109 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_sion` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_sion.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看赛恩的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sion.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN #1: the add-on's Sion (player 0, team 0), ...`：出生；
   - `RISE #1: lethal damage caught at 1 hp (last hit by ...), zombie 540 ticks from ... hp`：变成亡灵；
   - `FALL #1: the zombie's time is up, killed by ...`：亡灵倒下；
   - `FURNACE #3: ... killed, max health +... in all`：击杀加生命。

## 开发

- `python addons/league_sion/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的赛恩和参数表一致）。
  主包的赛恩改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_sion`：单元测试（亡灵掉血、击杀加多少、别人给的不死、参数、和参数表一致）。
- 在 `addons/` 下 `cargo build --release -p league_sion`（Windows）得到 `target/release/league_sion.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
