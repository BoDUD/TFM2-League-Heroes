# 诺手大招读血附加包（测试版 v0.1.0）

用户：「诺手总是在叠满血怒或敌人残血之前就放大招，这种情况可以用"插件"（或脚本）来调整吗？」「诺手需要调整」。

主包 `league` 保持纯数据。数据读不到当前生命，主包里诺手的 R「诺克萨斯断头台」由 AI 对「队伍刚打过的敌方英雄」放出：R 一好、
身边一开打就放，常常出血还没叠起来、对方血还厚，一刀砍不死，R 白白进 50 秒冷却。这个附加包用原生代码读生命，让 AI 等到该放的时候：

| | 主包 | 附加包 |
|---|---|---|
| 什么时候放 R | AI 看到队伍刚打过的敌方英雄在射程内就放 | 一刀砍得死射程内的英雄，或诺克萨斯之力期间 |
| 砍谁 | AI 选的那个 | 砍得死的人里生命 + 护盾最少的；诺克萨斯之力期间照 AI 选的（他有免死就换人） |
| 不该放的时候 | — | 改成普攻 AI 想砍的那个人（打不到就走过去），继续叠出血 |
| 伤害、击杀刷新、画面、声音 | 主包 | 主包（副本只改了 R 的说明） |

- **AI 钩子 `league_darius_ult:ult`**：读射程（46000）内每个敌方英雄的生命、护盾、身上有没有免死，读诺手身上的出血层数
  （`league_darius_hemo_1`..`_4`）和诺克萨斯之力（`league_darius_might`）还剩几 tick，照主包 R 的六档真实伤害
  （0-4 层：100 + 100% 攻击力起每层 +20%，诺克萨斯之力 200 + 200%）算这一刀**落下时**（放出后 26 tick）的伤害：层数撑不到落刀的不算，
  诺克萨斯之力落刀前就没了的按 0 层、攻击力去掉它的 40%。
- 真实伤害也吃目标身上的受到伤害增减（经典 SDK 的引擎里量的：受到伤害降低 50% 砍一半，和受到伤害提高相加后一起乘，
  技能伤害降低再乘一次——减伤 30% + 技能减伤 30% 剩 49%），所以按他身上 buff 的 `damaged_reduce`、`damaged_amplify`、
  `skill_damaged_reduce` 折算。折算后的伤害不低于生命 + 护盾、没有免死，就是「砍得死」。
- R 好了、有人砍得死（或在诺克萨斯之力里），AI 没想放也放；AI 在放别的技能或回城时不抢。
- AI 钩子自己看 R 的冷却和等级（引擎的「输入合法」不看冷却，派克附加包的教训）。
- 数字都在 `src/plan.rs`（钩子和模拟器共用这一份）；`make_override.py` 生成副本时逐个核对它们和主包的诺手一致：
  R 的六档伤害和它们读的 buff、诺克萨斯之力的攻击力加成、R 的距离和落刀时间、R 的施放目标。

## 在游戏里测

1. 主包（League of Legends Heroes 0.81.3 以上）要装着并启用。
2. 把整个 `league_darius_ult` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_darius_ult.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看诺手 R 的说明：开头是「【大招读血测试版】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_darius_ult.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `R KILL: #7 hp + shield 310 vs 476 (3 stacks, attack 198), the AI had not cast it`：放 R 斩杀，目标的生命 + 护盾、这一刀落在他身上的
     伤害（他有减伤时写成 `333 (476 before his damage taken changes)`）、落刀时的层数（5 = 诺克萨斯之力）、AI 原来想不想放 / 想砍谁；
   - `R MIGHT: #4 ...`：诺克萨斯之力期间放（没人砍得死，AI 选的人有免死，换成生命 + 护盾最少的）；
   - `R HELD: #4 hp + shield 1085 > 357 (1 stacks, attack 198), attacking instead`：AI 想放 R 但砍不死、层数不满，改成普攻他；
   - `R LANDED on #7: he died, R refreshed (cast for a kill: 476 damage at 3 stacks vs 310 hp + shield, a kill expected)`：
     放出后 34 tick 看结果。`he died before the blow (someone else's kill, no refresh)` 是落刀前他被队友打死了（这一刀落空、
     不刷新）；`he lived, hp …` 是没砍死：多半是落刀前被奶、被护盾，或诺手跃起时被控住打断。

## 开发

- `python addons/league_darius_ult/make_override.py`：从主包的诺手重新生成 `override/` 和 `text/`（先核对 `src/plan.rs` 的数字）。
  主包的诺手改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_darius_ult`：单元测试（伤害档位、层数撑不撑得到落刀、护盾、免死和减伤、放不放、砍谁），
  和 `tests/wiring.rs`：走真实的导出入口，在迷你模拟里让 AI 钩子想几 tick、看它写的日志。
- 在 `addons/` 下 `cargo build --release -p league_darius_ult`（Windows）得到 `target/release/league_darius_ult.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器（game_core 0.5.1）跑不了原生代码，但它的引擎也有同样的 AI 钩子（`PlayerInputAi`，
  `GameRunner::set_player_input_ai_templates`）：模拟程序每 tick 从事件记下生命、护盾、位置、诺手的层数、攻击力和 R 的冷却，
  挂上 `src/plan.rs` 同一份判断（只是读不到 buff 的「免死」）。放 R 的时机最终要在游戏里看日志确认。

## 模拟结果

诺手上单，对 6 个基础上单（fighter、executioner、lancer、pole_warrior、knight、berserker）× 3 套阵容 × 两边，种子 1-24，
各 864 局（每局 10 分钟）：

| | 主包 | 附加包 |
|---|---|---|
| 每局放 R | 4.6 | 5.3 |
| 落刀砍死人（都刷新） | 1.2（25%） | 3.7（70%） |
| 砍不死、也不在诺克萨斯之力 | 3.0 | 0.3 |
| 落刀前目标已被队友打死（这一刀落空、不刷新） | 0.4 | 0.9 |
| 诺手 K/D/A | 3.1 / 1.5 / 3.5 | 4.8 / 1.5 / 2.5 |
| 全队击杀差 | +1.73 | +2.19 |

- 预测的伤害和落刀扣的生命一致的占 91%；对不上的多是目标身上的减伤（模拟程序读不到 buff 的数值，游戏里本包读得到、会折算），或被护盾吸收的部分。
- 砍不死的那 0.3 次：目标有免死或减伤（同上，模拟读不到）、落刀前被奶或加盾、诺手跃起时被控住打断。
- 试过没采用的：斩杀线多留 10% 余量（全队击杀差反而低）；诺克萨斯之力期间先等斩杀、快结束才放（斩杀率 93%，全队结果一样，
  但满层时看着像不放）；R 改成对任何敌方英雄可放（多 0.1～0.2 击杀差，在波动内；诺克萨斯之力期间 AI 会挑没在打的满血英雄）。
