# 扎克附加包（测试版 v0.1.4）

主包 `league` 保持纯数据。用户选了「粘液回血 + 扩展包复活」：主包的细胞分裂只有掉下的黏液（走过去吃掉回血），复活放在这个附加包里，
用原生代码做主包数据做不到的那一件事；画面、声音仍然在主包的数据里（附加包只判断、只改生命）：

| | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 细胞分裂·复活 | **没有**（数据读不到当前生命，也没有「受到致命伤害」的时机） | 受到致命伤害时不倒下，化成一滩 `split_t` tick（6 秒）：生命设成最大生命的 `split_hp`%（40%）当作这一滩的生命，定身、禁普攻、禁技能，双抗 −20；**这一滩被打掉才阵亡**（击杀算打掉它的人），撑过去就带着这一滩剩下的生命重新聚起。每 `split_cd` tick（300 秒）一次，**阵亡不重置** |
| 细胞分裂·黏液 | 不稳定物质、橡筋弹弓、动感弹球、延伸打击打中英雄时甩出黏液，他走过去吃掉回血 | 一样 |

## 怎么做的

- **复活**：照艾尼维亚附加包的「不死守护」：冷却好了时一直给他挂着「不死」`league_zac_p_guard`（30 tick，每 10 tick 续），生命停在 1
  就触发：生命设成最大生命的 40%，挂 `league_zac_split_go`（6 tick），定身、禁技能、禁普攻 `split_t` tick。主包数据的副本由普攻第一次挂上
  一个每 2 tick 看一次的监视（一命一次）：看到 `split_go` 就播化开（不稳定物质的爆开画面、分裂的声音和台词）、挂一滩的标记
  `league_zac_split_on`（纯标记）和双抗降低 `league_zac_split_def`，每 30 tick 续一次一滩的动作；附加包自己也挂一个纯标记
  `league_zac_split_form`，两个标记有一个在就续、显示钩子就画成一滩（0.1.1，用户 2026-10-24「扎克变细胞的时候 还能变回英雄原来的
  样子？」：以前一滩的标记同时带着双抗降低，游戏里化开没几 tick 就不在他身上了，续播停了，他站回扎克的样子）；`split_t` tick 后附加包挂 `league_zac_split_end`，数据播重新聚起。一滩期间不再挂
  「不死」，致命伤害就是真的阵亡。别人给的「不死」（基兰的大招等）在身上时不触发。
- **一滩的画面**：游戏 0.6.4 起还会把显示世界里他正在播的 idle / hit 换成 `split_idle` / `split_hit`（`src/view.rs`，照艾尼维亚附加包的
  显示钩子），两次续播之间、挨打时也不闪回站着的样子。
- **和英雄联盟的不同**：英雄联盟里他分成四块小黏液各自爬回来，8 秒后按活下来的块数决定复活时的生命；这里是一整滩、6 秒、一开始
  固定 40% 生命（这一滩被打掉多少，聚起后就少多少）。

参数写在英雄数据的 `passive.params`（`{"split_t": 360, "split_cd": 18000, "split_hp": 40}`），由 `make_override.py` 从
`tools/kit/build_zac.py` 的参数表 `P` 写入（双抗降低 `split_def`、化开 / 聚起的时长 `split_in` / `split_out` 在数据里）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.202 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_zac` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_zac.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看扎克的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zac.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN`：出生；`SPLIT`：致命伤害停在 1 血、化成一滩；`REFORM`：重新聚起；`DESTROYED`：一滩被打掉（阵亡）；
   - `FORM ... SPLIT - idle/hit drawn as split_*`：画面换成一滩；`FORM whole-body puddle off`：显示钩子没挂上（只在不认识的游戏版本上出现）。

## 开发

- `python addons/league_zac/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的扎克和参数表一致）。
  主包的扎克改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_zac`：单元测试（参数、一滩的生命、别人的不死、一滩的显示换图）。
- 在 `addons/` 下 `cargo build --release -p league_zac`（Windows）得到 `target/release/league_zac.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。

## 0.1.2：果冻落地下一 tick 就能吸（2026-11-06）

掉出来的果冻的拾取区（`b_ground`，每 3 tick）开头 3 tick 吸不到；现在落地下一 tick 就能吸。经典 SDK 实测（2026-11-06，`trace.exe` 逐 tick 看每个区域第一次生效）：区域出现后第 `first_delay` tick 才第一次生效，写 0 等于晚整整一个周期（从飞行物落点生成的晚 `period` tick，从延迟或技能里直接生成的晚 `period - 1` tick）。改成 1 后，从落点生成的落地下一 tick 就生效，从延迟里生成的出现当 tick 就生效。主包的数据跟着改，本包的副本用 `make_override.py` 重新生成；DLL 没变。

## 动感弹球只击退一次（v0.1.3，2026-11-14）

主包的动感弹球按英雄联盟改了（用户看了「和英雄联盟不一样的地方」清单后说「全改吧」）：第一跳的击退用 1 秒推完（400 × 60 tick，距离和原来一样），之后三跳只有 50% 伤害和减速，不再击飞。副本跟着主包重新生成，本包的代码没改。

## 动感弹球：后几跳第一次砸到的敌人也击退（v0.1.4，2026-11-14）

英雄联盟的动感弹球对每个敌人只在他第一次被砸中时击退、打全额伤害，之后只有一半伤害和减速。主包的数据数不了每个人挨了几跳：第一跳砸到的击退，后面三跳一律一半伤害加减速——第一跳没砸到、后面才砸到的敌人就没有击退。本包补上：

- 副本（`build_zac.py --native`）：每次落地给 26000 内砸到的敌人挂一个 3 tick 的记号，第一跳 `league_zac_r_m1`、之后 `league_zac_r_m2`；大招的数字（`r_kb` 400、`r_kb_t` 60、`r_dmg` 90、`r_ap` 50、`r_k` 50）写进 `passive.params`。
- 被动 `split` 每 tick 找身上有记号的敌人，记下这次大招已经砸过谁（200 tick 没有新记号就算下一次大招）；带 `r_m2`、这次大招第一次被砸到的人：`entity_knockback`（`r_kb` × `r_kb_t`，从扎克身边推开，同第一跳）并补上没打的那一半伤害（`deal_damage_typed`，魔法，吃魔抗）。
- 大招的说明指到 `description.league_zac_addon.ult`（主包的说明后面加一句）。

日志 `BOUNCE #n: #id first hit by a later landing - knocked back 400 x 60 ticks, +70 magic`。测试 `each_enemy_is_knocked_back_on_its_first_hit_only`、`the_bounces_numbers_are_the_kits`。经典引擎的模拟跑不了原生代码，没有量过。
