# 盖伦大招斩杀附加包（测试版 v0.1.0，可选）

用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补附加包」。

英雄联盟里盖伦的 R「德玛西亚正义」是**斩杀**：伤害按目标**已损失**生命算，玩家留着它收人头。主包是纯数据，读不到生命：
R 写成 150 + 120% 攻击力 + 12% **最大**生命的真实伤害，AI 一好就放，常常砍在满血的人身上。**不装这个附加包，主包的盖伦也是完整的**。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 伤害 | 150 + 120% 攻击力 + 12% 目标最大生命（真实） | 150 + 120% 攻击力 + 30% 目标已损失生命（真实；英雄联盟 25/30/35%） |
| 什么时候放 | AI 看到射程内有敌方英雄就放 | 这一剑砍得死射程内的英雄才放；砍得死的人里砍生命 + 护盾最少的 |
| 不该放时 | — | AI 想放但砍不死：改成普攻那个人（打不到就走过去） |

## 怎么做的

- `mod.override_info` 把主包的盖伦换成 `override/` 里的副本。副本由 `make_override.py` 从主包生成，先核对 `src/plan.rs` 的数字和主包一样：
  - R 的 `FixedAttack` 去掉 12% 最大生命；
  - R 出手时给目标挂 `league_garen_ult_mark`（14 tick）；
  - 盖伦挂上被动 `league_garen_ult:verdict`，R 的说明换成【附加包】的。
- **AI 钩子 `league_garen_ult:ult`**：读射程（45000）内每个敌方英雄的生命、最大生命、护盾、免死和受到伤害增减（真实伤害也吃，算法照诺手附加包在经典 SDK 里量的），按 `plan.rs` 算这一剑的伤害，只为斩杀放。R 的冷却和等级自己看。
- **被动**：看到标记，10 tick 后（主包的巨剑落下的那一刻）按目标那时的已损失生命补 30% 的真实伤害（`deal_damage_typed`，`Fixed`）。画面、声音、主包那份伤害都在数据里。

- 0.1.1（2026-11-05 复查 11-03 夜里的日志：5 次 `R HELD` 的目标远在 R 伤害以下，死歌 4 次、塞恩 1 次，因为 `dies_to` 把身上任何「不死」都当砍不死）：别的附加包一直挂着的被动护身「不死」（名字以 `_p_guard` / `_rv_guard` 结尾：死歌、塞恩、艾尼维亚、扎克、扎恩、tft 的石甲虫）不再算「杀不死」——英雄联盟里处决他们照样算击杀，他们死进自己的被动里（死歌化灵体、塞恩起尸、艾尼维亚进蛋）；千珏、基兰、凯尔等的「不死」照样等。`R HELD` 的目标真带「不死」时注明 `undying`。
- 0.1.2（2026-11-06 的日志）：6 次 `R KILL` 有 4 次后面没有 `VERDICT`；t=16698 和 t=16818 是同一次按 R（`R KILL` 每 120 tick 才记一行），R 一直是好的——引擎 120 tick 以上没接。多半是他正在 E 的 3 秒旋转里（施法动作，游戏 0.6.4 记成 `Animation`），钩子只看 AI 的输入是不是技能。现在照 league_ult_press：他在放技能（`Animation`）、被强制位移（`ForceMove`）或被放不出技能的控制住时，钩子不自己按 R；AI 自己要放的 R 砍不死照样拦（`quiet`）。按了 30 tick 引擎还没接，记一行 `R NOT TAKEN: #id pressed for n ticks, R still ready (his crowd control [...], the AI's input ...)`；R 放出去了、落剑时目标已经死了或没了，记 `R GONE #n: #id was dead or gone before the sword landed - no verdict`。下一局看这两行还有没有、`R KILL` 后面是不是都有 `VERDICT`。

## 在游戏里测

1. 主包（League of Legends Heroes 0.208.0 以上）要装着并启用。
2. 把 `league_garen_ult` 文件夹放进 `<游戏目录>\mods\`，或者用附加包合集 `league_addons`（已经包含本包）。在 MOD 菜单里启用，排在主包后面，重启游戏。
3. 盖伦 R 的说明开头是「【附加包】」就说明换上了。
4. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_garen_ult.log`：
   - `R KILL: #7 hp 310/1500 + shield 0 vs 896`：为斩杀放 R；
   - `R HELD: ...`：AI 想放但砍不死，改成普攻；
   - `VERDICT #n on #7: hp 310/1500, +357 true damage`：落剑时补的那份。

## 开发

- `python addons/league_garen_ult/make_override.py`：重新生成 `override/` 和 `text/`；`--check` 只比较。主包的盖伦改了就重跑。
- `cargo test -p league_garen_ult`（在 `addons/` 下；仓库在很深的路径里时设 `CARGO_TARGET_DIR` 到短路径）。
