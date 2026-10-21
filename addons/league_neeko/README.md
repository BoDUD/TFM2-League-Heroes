# 妮蔻附加包（测试版 v0.1.0，可选）

**不装这个附加包，主包里的妮蔻也是完整的**：普攻和 W 两生花影的第三下强化、Q 盛开花种（炸到英雄再盛开两次）、E 缠结倒刺、
R 怒放，以及连招 E → Q、R → Q 都在主包数据里。主包是纯数据：**数据换不了外形**，所以主包的妮蔻没有被动。这个附加包用原生代码
做她的被动「天生幻魅」（用户 2026-10-21 选「做，附加包」）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 天生幻魅 | 没有 | 脱战 2 秒后**整个身体画成最近的友方英雄**（站、跑、出招、挨打都用他的图）；放技能、被控（击飞、晕眩、禁锢、嘲讽、恐惧、魅惑、强制位移）、假扮以来挨了她 35% 最大生命的伤害、或假扮的队友阵亡时现形；**放技能现形后 4 秒 20% 法术穿透**（英雄联盟的数值）；现形 6 秒后才能再变 |

## 怎么做的

- `mod.override_info` 把主包的妮蔻换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_neeko.py` 的 `native=1` 生成，
  主包的妮蔻改了就重跑）：数据和主包一样，多了被动 `league_neeko:glamour`（数字在 `passive.params`）和变身 / 现形的画面
  `league_neeko_p_poof`；普攻的说明开头加【附加包】、写上被动。
- **被动**（模拟里）：每 tick 看技能冷却有没有从 0 跳上去（league_yuumi 的做法：Q、E、R 都是伤害技能）、身上有没有打破伪装的控制、
  `on_damaged` 累计假扮以来挨的伤害；变身挑附近最近的、活着的、`souls.rs` 动作表里有的友方英雄（别的 mod 的英雄名字对不上图会让游戏
  panic，不变）。法术穿透是原生加的 buff `league_neeko_p_pen`（`magic_resistance_penetration`）。
- **外形**（`src/view.rs`，佛耶戈附身 0.1.7 的做法）：屏幕放的那场模拟几秒钟就把整局跑完，屏幕几分钟后才放到，显示世界也收不到原生加的
  buff，所以被动在屏幕放的那场模拟（ClientMatchView / 观战 / 回放）里记下每次变身和现形的 tick、队友的英雄 id；`game_places::hook::add`
  的显示钩子按屏幕上的比赛时钟（`game_places::clock`）把名字是 `league_neeko` 的画面实体的身体资源名（+0x50）换成那名队友显示实体的、
  正在播的动作名换成他图里有的（`hd_` / `lo_` 前缀照留：skill2 → skill → attack → idle，ult / ult_b → ult …），时段外写回她自己的。
- **时钟**：游戏每个 mod 只有一个客户端扩展槽，league_addons 里归佛耶戈的读时钟扩展；它现在也喂 `game_places::clock`，妮蔻读它。
  单独装这个附加包的 DLL 时，本包自己挂一个只喂时钟的扩展（`ClockFeed`）。
- 动作表是佛耶戈附加包的 `league_viego_soul/src/souls.rs`（`#[path]` 共用，由它的 `make_override.py` 生成）：表里没有的新英雄不会被假扮。

## 在游戏里测

- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_neeko.log`（每次启动游戏重写，上一次的在 `.prev.log`）。
  `DISGUISE n as <英雄>`、`REVEAL from <英雄> (cast / crowd control / hit through / the ally fell / dead)` 是模拟里的变身和现形；
  `Neeko #<key>: drawn as <资源名>` 是屏幕上她被画成谁。
- 看她开局 2 秒左右变成身边的队友、放技能时变回妮蔻（带一下变身的画面和音效），6 秒后又变。
