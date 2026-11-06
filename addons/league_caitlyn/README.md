# 凯特琳附加包（测试版 v0.1.3）

用户 2026-10-22：「女警前期压制力太低」「再想想AI那边的办法」「做附加包之类的也行」。主包的凯特琳一个数字都没改，本包只加一个
AI 钩子 `league_caitlyn:lane`（优先级 105，在 league_ult_press 之后），前 10 分钟对线时让游戏的 AI 用她的射程和 Q 消耗对面英雄。

## 为什么是 AI，不是数值

经典引擎模拟（下路对 4 个原版射手、3 套阵容、两边、8 个种子）：她前 5 分钟击杀差 +0.38（金克丝 +1.29、艾希 +0.95、
厄运小姐 +0.90），10 分钟 +1.65，前期伤害只有别的射手的六七成。加攻击、加 Q 伤害、加爆头、出手加快、Q 只能对英雄放等
9 个数值方案，前期最多 +0.6 左右，能拉高前期的也让后期太强。跟踪一局看：游戏的 AI 一好 Q 就拿去清兵（前 5 分钟 15 个 Q
有 11 个打在小兵上），打小兵时对面英雄在射程边上也不打。

## 钩子做什么

只在游戏的 AI 已经要普攻或放 Q 时改目标（走位、撤退、回城、夹子、大招都不碰）。规则在 [`src/plan.rs`](src/plan.rs)（模拟器用同一份）：

- AI 放 Q：Q 射程（10 万，和主包 Q 自己挑英雄的距离一样）内有对面英雄就朝他放，血少的先；
- AI 普攻、Q 好了：Q 射程内有对面英雄就先 Q 他；
- AI 打的小兵这一枪打不死（不是补刀）：对面英雄在射程里、或往前一小步（2 万）就到，改打英雄；补刀那枪照打；
- 不改：她或目标在敌方塔下（8 万）、她血量低于 35%、9 万内敌方英雄比我方（连她）多；她正在出招（E、普攻的前摇，游戏记成
  `Animation`）或被强制位移（0.1.2，league_ult_press 的规则：2026-11-03 夜里她放 E 的 24 tick 里游戏的 AI 每 tick 都下命令，钩子
  每 tick 再按一次 Q，`Q POKE at league_lux` 连着 22 行，`TALLY` 一分钟 `QPoke:27`，Q 的冷却 8 秒一分钟最多 8 次）。
- **连改不成就歇一会**（0.1.3，2026-11-06）：日志里 `Q POKE at league_mel` 连着 11 tick、24 tick 每 tick 一行，`TALLY` 一分钟
  `QPoke:33`。两串都从 league_ult_press 记「A ORDER: held 39 / 40 ticks」那一 tick 开始：它看她站着不打人，替她下普攻命令；本包排在它
  后面，每 tick 把这个普攻换成朝梅尔放 Q，Q 一次都没放出去，它的普攻也就一直没出去，她就这么干站着。现在同一种改法（Q 或改打英雄）
  连着 3 tick 还没放出去（放出去了 Q 进冷却、普攻进前摇，下一 tick 就不会再改）就歇 30 tick：这期间游戏的 AI 和 league_ult_press 的
  命令原样放行（`TALLY` 记成 `Backoff_kept`），日志记一行写出可能挡着的东西（league_orianna 0.3.2 的做法）；一串连改只记第一下。

模拟（同样的 8 个种子）：前 5 分钟 +0.38 → **+0.74**，10 分钟 +1.65 → +2.14；再加数值（攻击 120 / 成长 15）+0.78 / +1.92，
所以只用钩子。

## 在游戏里测

1. 主包（League of Legends Heroes 0.195 以上）要装着并启用；用附加包合集 `league_addons`（已包含本包）。
2. 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_caitlyn.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `Q POKE at <英雄> (<距离> away, the AI wanted Skill)`：AI 的 Q 改打英雄；
   - `HARASS <英雄> (...)`：普攻改打英雄；
   - `... changed 3 ticks running since t=... and not taken (her cc [...], Q 0/480 charges 0 attack .../...; target ...) - backing off
     30 ticks, the AI's orders go`（0.1.3）：连改没放出去，括号里是她身上的控制、Q 和普攻的冷却、目标的状态；
   - `TALLY minute N: ...`：每分钟改了几次、没改的原因（`Danger`、`Tower`、`LastHit`、`NoneInReach`、`Busy` 正在出招、`Backoff` 连改不成在歇）。
     过了 10 分钟写出最后一分钟就不再记（0.1.2：以前之后每分钟一行 `Late_kept`）。
     每个凯特琳各记各的（记在她的 AI 钩子上，每份模拟一个）：0.1.0 所有模拟共用一份，服务器同一局两份预模拟并排跑时每换一份
     就写出去，日志里两局交替、每行只有一两项。

## 开发

- `cargo test --release -p league_caitlyn`（在 `addons/` 下）：规则和读数的单元测试。
- 经典引擎模拟：`ctsim.rs`（诺手钩子的做法：游戏自己的 AI 加 `PlayerInputAi`，从事件里存一份世界的快照），`CT_MODE=main|hook`。
