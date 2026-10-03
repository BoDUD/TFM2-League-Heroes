# 剑魔 W 锁链附加包（测试版 v0.2.0）

主包 `league` 保持纯数据。主包里剑魔的 W「恶火束链」：锁链停在第一个敌人身上（40 + 40% 攻击力、减速 25% 1.5 秒）；
锁链旁边有敌方英雄时在落点放圈，1.5 秒后那个英雄再受一次伤害、被拉向剑魔。League 的两条数据写不出来：
**走出圈锁链就断**，以及拉回的是**圈的中心**。这个附加包用原生代码照 League 原版做：

- **只锁锁链真正打中的那一个**：英雄或野怪（League：英雄和大型野怪；TFM2 的野怪都是单只的大怪）。被小兵挡住时后面的
  英雄不算（主包的「锁链旁边的英雄」会算上）。小兵**再受一次伤害**（League：对小兵双倍）。
- **圈**：圈心是锁链停下的地方（锁链碰到他就停，比他稍微靠近剑魔，League 也是这样），半径 **33000**
  （League 的圈约 460、W 射程 825；主包 W 射程 60000）。
- **走出圈就断**：每 tick 量他离圈心多远，超过 33000（走出去、闪现、冲刺都算）锁链就断，什么都不发生。
- **1.5 秒还在圈里**：被**拉回圈心**（引擎的强制位移，撞墙会停；被韧性截短了会补推剩下的路），再受一次
  40 + 40% 伤害（按剑魔**当下**的攻击力算），播锁链缠身和收紧的画面。
- 打中英雄的那两下都照主包的规矩：剑魔吸血（7 + 7% 攻击力，大灭期间 10 + 10%）、欠被动一次冷却缩减、大灭期间打死人刷新大灭。
- 拴着的时候每 4 tick 从他脚下往圈心飞一节锁链（`league_aatrox_w_link`，贴着地面）。
- 剑魔中途阵亡也照样拉回（第二下没有：数据里排着的效果跟着剑魔没了）；被锁的人中途阵亡就结束。
- League 的「真实视野」（被锁住的人现形）没有接口，没做。

**v0.2 的分工**：本包只判断和挪人（锁谁、断没断、拉回），在剑魔身上挂几个短标记（`league_aatrox_w_tether`、
`w_champ`、`w_minion`、`w_pull`、`w_pull_c`）；看得见的（圈、收紧、缠身）和伤害、吸血都在副本的数据里，读这些标记再播、
再打。v0.1 由本包自己播圈、打第二下，游戏里看不到（「w技能完全看不到效果」），数据播的画面在别的英雄身上一直正常。
被锁住的人身上的标记：`league_aatrox_chain_on:<圈心x>:<圈心y>:<剑魔>:<到点tick>`。不用全局变量。

## 在游戏里测

1. 主包（League of Legends Heroes 0.51 以上，有剑魔）要装着并启用。
2. 把整个 `league_aatrox_chain` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_aatrox_chain.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看剑魔 W 的说明：开头是「【W锁链测试版】」就说明覆盖生效了。
5. 打几局有剑魔的对局。
6. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aatrox_chain.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `TETHER Champion #… at (x,y) ring (x,y) (the chain's stop; Aatrox (x,y))`：锁住谁、圈在哪；
   - `BREAK: 33500 from the ring's centre, 30 ticks before the pull`：走出圈，锁链断了；
   - `PULL: … from the centre, pulled in … ticks; the second hit flagged on Aatrox`：拉回，第二下交给数据；
   - `DRAG: stopped … short of the centre, pushed again …`：拉回被截短，补推。

## 开发

- `python addons/league_aatrox_chain/make_override.py`：从主包重新生成 `override/` 和 `text/`（锁链打中时调本包；去掉主包
  「锁链旁边的英雄」那段和落点的圈，用它们的节点拼出读标记的数据：小兵、第一下、`READ_AT` 的第二下、落点的圈和收紧；
  加锁链节的画面条目，检查说明文字的长度）。主包的剑魔改了以后要重跑。
- 在 `addons/` 下 `cargo test -p league_aatrox_chain`：单元测试（圈心、标记、打中的是什么）和 `tests/wiring.rs`
  （迷你模拟：站着被拉回、走出圈、闪现出圈、往剑魔那边走、小兵、野怪、韧性补推、剑魔阵亡、目标阵亡、重复调用、
  数据层给位置、找不到锁链；检查剑魔身上的标记在数据读的那一 tick 还在）。
- 在 `addons/` 下 `cargo build --release -p league_aatrox_chain`（Windows）得到 `target/release/league_aatrox_chain.dll`。
