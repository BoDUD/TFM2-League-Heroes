# 慎「秘奥义！慈悲度魂落」护盾按生命值附加包（v0.1.0，可选）

玩家：「I realised Shen ult scales with ad wouldn't it be better if it scaled with hp?」，用户：「这个也要改」，选了「附加包按生命值」。

数据里的护盾（`Shield`）只有固定值、攻击力和法强的比例，读不到生命值，所以主包的慎大招护盾是 260 + 60% 攻击力。
**不装这个附加包，主包里的慎也是完整的**（护盾照给，按攻击力算）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 大招给队友的护盾 | 260 + 60% 攻击力，5 秒 | 150 + 慎最大生命值的 12%，5 秒（英雄联盟：固定值 + 17.5% 额外生命值） |

挑队友、引导、传送、画面和声音都和主包一样。

## 怎么做的

- `mod.override_info` 把主包的慎换成 `override/` 里的副本（`make_override.py` 从主包生成，主包的慎改了就重跑）：
  `tools/kit/build_shen.py` 的 `native=1`：大招给队友挂 `league_shen_r_shield`（护盾的画面）时不给数据护盾；`passive` 挂本包的被动
  `league_shen_shield:shield`（参数 `r_sh_base`、`r_sh_hp`、`r_sh_t` 来自参数表 P）；大招的说明换成 `description.league_shen_shield.ult`
  （护盾写成「150 + 生命值图标 12%」），游戏里看说明就知道副本生效了没有。
- 被动 `shield`（`src/lib.rs`）：每 tick 看己方英雄，谁身上刚出现 `league_shen_r_shield`，就给他 `r_sh_base` + 慎最大生命值的
  `r_sh_hp`% 的护盾 `r_sh_t` tick（`entity_add_shield`）。
- 测试：`cargo test -p league_shen_shield`。

## 在游戏里测

1. 主包（League of Legends Heroes 0.116.1 以上）要装着并启用；玩家装的是附加包合集 `league_addons`，慎的部分和这里一样。
2. 看慎大招的说明：护盾后面是生命值图标就说明副本生效了。
3. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shen_shield.log`，每次启动游戏重写：
   `SHIELD #1 on #21: 438 (150 + 12% of 2400) for 300 ticks`。
