# 剑魔 W 锁链附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。主包里剑魔的 W「恶火束链」：锁链停在第一个敌人身上（40 + 40% 攻击力、减速 25% 1.5 秒）；
锁链旁边有敌方英雄时在落点放圈，1.5 秒后那个英雄再受一次伤害、被拉向剑魔。League 的两条数据写不出来：
**走出圈锁链就断**，以及拉回的是**圈的中心**。这个附加包用原生代码照 League 原版做：

- **只锁锁链真正打中的那一个**：英雄或野怪（League：英雄和大型野怪；TFM2 的野怪都是单只的大怪）。被小兵挡住时后面的
  英雄不算（主包的「锁链旁边的英雄」会算上）。小兵**当场再受一次伤害**（League：对小兵双倍）。
- **圈**：在他脚下、往剑魔那边挪 3000 的地方（League：拉回的位置比原地稍微靠近剑魔），半径 **33000**
  （League 的圈约 460、W 射程 825；主包 W 射程 60000）。
- **走出圈就断**：每 tick 量他离圈心多远，超过 33000（走出去、闪现、冲刺都算）锁链就断，播碎链的画面和声音，什么都不发生。
- **1.5 秒还在圈里**：播收紧的画面，再受一次 40 + 40% 伤害（按剑魔**当下**的攻击力算），被**拉回圈心**
  （引擎的强制位移，撞墙会停；被韧性截短了会补推剩下的路）。
- 打中英雄的那两下都照主包的规矩：剑魔吸血（7 + 7% 攻击力，大灭期间 10 + 10%）、欠被动一次冷却缩减、大灭期间打死人刷新大灭。
- 拴着的时候每 4 tick 从他脚下往圈心飞一节锁链（`league_aatrox_w_link`），圈每 16 tick 补播一次（`w_ring_beat`），
  锁链断了圈就不再补。
- 剑魔中途阵亡也照样拉、照样打（第二下不吸血）；被锁的人中途阵亡就结束。
- League 的「真实视野」（被锁住的人现形）没有接口，没做。

所有状态都在单位身上的 buff（`league_aatrox_chain_on:<圈心x>:<圈心y>:<剑魔>:<到点tick>`）和排队的效果里，不用全局变量。
**画面**：`w_link`、`w_ring_in`（出现 + 一圈，24 tick）、`w_ring_beat`（一圈，16 tick）在主包剑魔的特效图里
（`tools/art/import_aatrox.py`）；特效导入之前这几样看不见，逻辑照样跑。

## 在游戏里测

1. 主包（League of Legends Heroes 0.51 以上，有剑魔）要装着并启用。
2. 把整个 `league_aatrox_chain` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_aatrox_chain.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看剑魔 W 的说明：开头是「【W锁链测试版】」就说明覆盖生效了。
5. 打几局有剑魔的对局。
6. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aatrox_chain.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `TETHER Champion #… at (x,y) ring (x,y) (Aatrox (x,y))`：锁住谁、圈在哪；
   - `BREAK: 33500 from the ring's centre, 30 ticks before the pull`：走出圈，锁链断了；
   - `PULL: … from the centre, pulled in … ticks, hit … (hp 前 -> 后), Aatrox heals …, passive cut pc…`：拉回、第二下；
   - `DRAG: stopped … short of the centre, pushed again …`：拉回被截短，补推；
   - `chain hit killed #…`：第一下就打死了。

## 开发

- `python addons/league_aatrox_chain/make_override.py`：从主包重新生成 `override/` 和 `text/`（锁链打中时调本包，去掉主包
  「锁链旁边的英雄」那段和落点的圈，加画面条目，检查本包重复用到的数字和说明文字的长度）。主包的剑魔改了以后要重跑。
- 在 `addons/` 下 `cargo test -p league_aatrox_chain`：单元测试（圈心、标记、伤害、吸血、打中的是什么）和
  `tests/wiring.rs`（迷你模拟：站着被拉回、走出圈、闪现出圈、往剑魔那边走、小兵、野怪、大灭击杀、韧性补推、剑魔阵亡、
  目标阵亡、重复调用、数据层给位置）。
- 在 `addons/` 下 `cargo build --release -p league_aatrox_chain`（Windows）得到 `target/release/league_aatrox_chain.dll`。
