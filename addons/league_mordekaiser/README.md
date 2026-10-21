# 莫德凯撒附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户要了附加包；问到「R做不了独特空间吗？」，选了「放逐两人 + 附加包算单挑」，并且「嘲讽不做」（和英雄联盟一样）。这个附加包用原生代码做主包数据做不到的两件事：

- **轮回绝境（R）真的把人拖进领域**：主包里 R 是诅咒 7 秒、按固定数值偷属性、跑远了被拉回。附加包的 `league_mordekaiser:realm` 在 R 出手那一 tick：
  - 在射程（48000，加两人身体）里挑**攻击 + 法强最高**的敌方英雄（英雄联盟里大家都把大招给对面的核心）；
  - 按他此刻的面板**真偷 10%**：攻击、法强、护甲、魔抗、最大生命（他身上 `league_mordekaiser_r_curse` 减，莫德身上 `league_mordekaiser_r_steal` 加，7 秒）；
  - 两人都被**放逐 7 秒**：离开战场，谁也选不中、看不见；原地留一个 `league_mordekaiser_r_realm` 漩涡；
  - 领域里的单挑由附加包算：被动每 tick 看，谁的攻击间隔到了谁出手（`deal_damage` 走引擎自己的伤害流程：护甲魔抗、击杀、统计都算）。莫德每下 攻击 + 40% 法强，外加满层黑暗起兮的光环（每 0.5 秒 4 + 15% 法强 + 1% 最大生命）；对方每下 攻击 + 40% 法强（代替他的技能）；
  - 对方死在领域里：莫德回复 150 + 50% 法强，偷来的属性再留 15 秒（英雄联盟：留到对方复活），莫德提前出来；莫德先死：对方提前出来；都活着就 7 秒后两人在原地出现。
- **不坏之身（W）按伤害攒护盾**：主包的护盾是固定数值。附加包的被动在他每次命中时攒打出伤害的 45%（打小兵、野怪按 25% 算），每次受伤时攒受到伤害的 15%，最多最大生命的 30%，脱战 1 秒后慢慢掉。W 放出时整份变成护盾（至少最大生命的 5%，3 秒），2.5 秒后按护盾还剩多少回复 40%（护盾剩余量引擎能直接读到）。

数字：被动的参数写在英雄数据的 `passive.params`（`{"kill": 150, "kill_ap": 50, "keep": 900, "w_dealt": 45, "w_taken": 15, "w_cap": 30, "w_heal": 40}`），
由 `make_override.py` 从 `tools/kit/build_mordekaiser.py` 的参数表 `P` 写入；R 和 W 的效果在被动之外运行，用到的数字写在 `src/lib.rs`（`R_*`、`W_*`、`A_AP`、`P_*`），单元测试核对参数表。

## 在游戏里测

1. 主包（League of Legends Heroes 0.104 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_mordekaiser` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_mordekaiser.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看莫德凯撒的技能说明：E 和 R 开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_mordekaiser.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `R REALM with Jinx#12 (the AI asked for Leona#14): steals Steal { attack: 22, .. }, both banished 420 ticks`：拖进领域；
   - `R WON: Jinx#12 died in the realm (6 swings vs 5) -> +190 hp`、`R LOST`、`R END: both out`：领域的结果；
   - `R OUT: league_mordekaiser#.. targetable again 12 ticks after the realm ended early`：提前结束后他回到战场（0.1.1 起
     最多 24 tick）；`STILL BANISHED` 或 `R: renewing his banish was refused` 就是没出来，告诉我；
   - `W SHIELD 412 (stored 412, max hp 2650)` / `W HEAL #3: 230 of 412 shield left -> +92`：护盾和回血；
   - 行尾有 `(entity_banish refused)` / `(entity_add_shield refused)`：游戏没接受，告诉我。

## 0.1.1（2026-10-19）：赢了以后不再一直隐身

日志里每次「R WON」后都是 `R OUT: league_mordekaiser STILL BANISHED`（一天 95 次 + 上一次启动 43 次），而他先死时对手 0 tick
就出来了：游戏 0.6.4 解不开他自己身上那份带漩涡、7 秒的放逐，对手提前死了他还隐身、选不中到 7 秒满。现在他的放逐不带画面、
一次只给 24 tick，单挑还在就每 12 tick 续上（最后一段截到领域结束），漩涡单独播在他出手的地方；提前结束时他最多再放逐
24 tick（0.4 秒）。对方的放逐照旧一次给满 7 秒。

## 开发

- `python addons/league_mordekaiser/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的莫德凯撒和参数表一致）。
  主包的莫德凯撒改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_mordekaiser`：单元测试（偷 10%、挑核心、护盾的攒法和上下限、参数、和参数表一致）。
- 在 `addons/` 下 `cargo build --release -p league_mordekaiser`（Windows）得到 `target/release/league_mordekaiser.dll`；
  `league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认（尤其放逐后 `deal_damage` 能不能打到被放逐的人：
  `R WON` / `R LOST` 行出现、`swings` 有数字就说明单挑在算）。

## 游戏 0.6.5（0.1.2）

0.6.5 修了「道士大招打带韧性的目标，控制结束后还选不中」：引擎的放逐要是同样按韧性缩短，对手会提前出领域、单挑却还在算。现在领域里对方变回选得中（施放 2 tick 后）领域就结束：两人都出来，偷的属性还回去（日志 `R CUT`）；他自己那一段放逐被缩短、提前选得中时立刻续上。韧性不缩放逐的话这两条都不会触发。
