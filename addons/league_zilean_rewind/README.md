# 基兰复活附加包（测试版 v0.2.0）

主包 `league` 保持纯数据。主包里基兰的 R 由 AI 在敌方英雄 60000 内时放出、**待命** 900 tick（没用上就退还冷却）；
待命期间他每次出手查一次：附近有**被控制**的友方英雄、或自己被**两名以上**敌方英雄贴身，才给那个人挂 5 秒的时光符文
（`league_zilean_r_rune`，带「不死」，生命最低停在 1），到第 299 tick 不管有没有危险都回血。主包测过平均一局只出 0.8 次，
挂上的也多半用不上——看起来就是「基兰不放大」。这个附加包用原生代码把它做成 League 的「时光倒流」：

- **给快死的人挂**（v0.2.0）：四个动作里的那段检查去掉，改由被动 `league_zilean_rewind:guard`（挂在 `passive_ult` 上，
  学会 R 后每 tick 运行）决定：R 待命时每 3 tick 看一次基兰 **90000 内**的己方英雄（含他自己），**身边 45000 内有敌方英雄**，
  而且**生命低于 30%**，或 **1 秒（60 tick）内被打掉 30% 以上、只剩 60% 以下**——给生命比例最低的那个挂符文，播主包 R 的
  施法动作（30 tick）、画面和声音，去掉待命（冷却照常走完，不退还）。基兰被控住（眩晕、击飞、沉默等）时不放。
- 符文期间**受到致命伤害**（生命被「不死」停在 1）时：去掉符文，**倒流 2.5 秒**——清掉控制，放逐（不可选中、
  隐身、不能行动，播倒流的画面），期间不死也不受伤；结束后回复 **400 + 150% 基兰法强**（挂符文那一刻算）。
- 符文 5 秒**没用上就不回血**（同 League）。
- 基兰挂完符文就阵亡了也照样倒流，回血算被保护者自己的治疗。

## 索拉卡、凯尔不受影响

- 本包只碰**身上有基兰符文**的人；索拉卡、凯尔等别的英雄的数据都不在本包里（`mod.override_info` 只换基兰），原样不动。
- 别人给的「不死」——索拉卡 W 的 `league_soraka_w_guard`（3 tick）、凯尔的 `league_kayle_probe_undying`（2 tick）——
  在身上时**不倒流**：那段时间他本来就死不了，等它结束、生命还停在 1 才倒流。
- `tests/wiring.rs` 里专门测了：索拉卡、凯尔没有符文时吃到致命伤害，本包什么都不做；符文和她们的「不死」叠在一起时，
  等她们的结束才倒流。

## 在游戏里测

1. 主包（League of Legends Heroes 0.50 以上）要装着并启用。
2. 把整个 `league_zilean_rewind` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_zilean_rewind.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看基兰 R 的说明：开头是「【复活测试版】」、写着「快要阵亡时」就说明是 v0.2.0。
5. 打几局有基兰的对局，最好同队再放索拉卡、凯尔。
6. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zilean_rewind.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `GUARD: rune on #… (hp 22%, lost 35% in 60 ticks, enemy champion 30000 away)`：基兰放 R，给谁、他当时多危险；
   - `RUNE from #… league_zilean (rewind heal …)`：挂上符文，倒流时会回多少血；
   - `REWIND: lethal damage caught at 1 hp, banished for 150 ticks`：致命伤害被接住，开始倒流；
   - `REVIVE: healed … by …`：倒流结束、回血；
   - `rune ended unused: no heal`：符文没用上。

## 开发

- `python addons/league_zilean_rewind/make_override.py`：从主包重新生成 `override/` 和 `text/`（去掉四个动作里待命时的检查，
  挂上 `passive_ult`，检查说明文字的长度）。主包的基兰改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_zilean_rewind`：单元测试（给谁挂）和 `tests/wiring.rs`（迷你模拟：倒流、
  索拉卡 / 凯尔、被动 guard 挂符文和不挂的几种情况）。
- 在 `addons/` 下 `cargo build --release -p league_zilean_rewind`（Windows）得到 `target/release/league_zilean_rewind.dll`。
