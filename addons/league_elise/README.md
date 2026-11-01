# 伊莉丝附加包（测试版 v0.1.2，可选）

**不装这个附加包，主包里的伊莉丝也是完整的**：人形 / 蜘蛛两种形态、按战况切换、神经毒素、剧毒之蜇、结茧、自爆蜘蛛、盘丝、
掠行狂暴、小蜘蛛的被动和 5 级的茧缚猎杀都在主包数据里。主包是纯数据，有几件事做不到，这个附加包用原生代码补上（用户 2026-10-15
「附加包要」）：

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 蜘蛛形态的样子 | 只有出招（普攻、剧毒之蜇、盘丝、变身）是蜘蛛的动作，待机、跑步、受击、阵亡还是人形（游戏按名字自动播这几个，数据换不了） | **整个身体**都是蜘蛛：待机、跑步、受击、阵亡播 `c_idle` / `c_run` / `c_hit` / `c_dead`（只在游戏 0.6.4 上，别的版本退回左边那样）；复活是人形 |
| 结茧打谁 | 射程内随机一个敌方英雄（茧碰到第一个单位就停，常常打在小兵上） | 线上**没有小兵、野怪、别的英雄挡着**的英雄：被控住的先（必中），再挑最近的；都被挡着才挑最近的英雄 |
| 盘丝落到谁身上 | 射程内随机一个敌方英雄 | **生命比例最低**的英雄（一样低就近的） |
| 茧缚猎杀打谁 | 被控住的英雄先，没有就在最近被己方打过的英雄里随机挑 | **被控住的**英雄先（其中生命比例最低的），没有就挑生命比例最低的 |

自爆蜘蛛、掠行狂暴照旧打 AI 选的目标。

## 怎么做的

- `mod.override_info` 把主包的伊莉丝换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_elise.py` 的 `native=1`
  生成，主包的伊莉丝改了就重跑）：加上本包的被动 `league_elise:queen`（参数 `e_range` 75000、`e_w` 2500、`ce_r` 50000、
  `r_range` 75000：结茧、盘丝、大招的射程，都从参数表 P 来），技能2和大招改成**对目标施放**（`Targeting`）：结茧的瞄准、
  盘丝的落点、茧缚猎杀都打向施法的目标，也就是本包 AI 钩子挑的那个，不再在射程内随机挑；技能2、大招的说明开头加【附加包】。
- **整身变蜘蛛**（`src/view.rs`）：照奈德丽附加包的整身变豹换**正在播的动画名**。显示世界每帧调用的更新函数（rva 0x23312a0，
  槽 rva 0x3c82db8）换成本包的函数：先调用槽里原来的（游戏的，或凯隐 / 佛耶戈 / 奈德丽 / 杰斯附加包的），再看名字是
  `league_elise` 的画面实体：身上有蜘蛛形态的 buff `league_elise_sp` 时，正在播的 `idle` / `run` / `hit` / `dead` 换成
  `c_idle` / `c_run` / `c_hit` / `c_dead`，普攻的第一 tick `attack` 换成 `c_attack`；变回人形就换回来。阵亡时 buff 清掉，
  尸体按倒下前的形态画。高清帧不用另管：league.dll 把动画表里每个动作（`c_idle` 也在内）就地换成它的 `hd_` 帧。
- **挑目标**（AI 钩子 `league_elise:aim`）：AI 要放技能2或大招时按上表换目标。技能2只在这次放的是结茧（人形、结茧好了、射程内
  有英雄）或盘丝（蜘蛛、盘丝好了、射程内有英雄）时换，判断照主包数据的分支（身上的 `league_elise_sp`、`league_elise_e_cd`、
  `league_elise_ce_cd`）。
- 原生代码只做判断和换名字，伤害、晕眩、盘丝的升空和落下都在数据里。

## 在游戏里测

1. 主包（League of Legends Heroes 0.115.0 以上）要装着并启用。
2. 把整个 `league_elise` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_elise.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看伊莉丝技能2的说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_elise.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `whole-body spider on: display slot …`：整身变蜘蛛装上了（`off (…)` 就是游戏版本不对）；
   - `world … Elise #…: SPIDER` / `human`：画面里变了形态；`FORM sim: SPIDER on` / `spider off`：模拟里的形态 buff；
     `SPAWN`：这局用的是附加包的伊莉丝；
   - `COCOON A -> B (CLEAR line, nearest / HELD + CLEAR line / all blocked, nearest …) AIM`、`RAPPEL … (LOWEST: …% hp)`、
     `HUNT … (HELD … / LOWEST …)`：换了目标（`kept` 是 AI 本来选的就是它）。
   - 模拟里的这几种行（`SPAWN`、`FORM sim`、`COCOON` / `RAPPEL` / `HUNT`）整个游戏一个计数：你看的那场每条都记，服务器的预模拟
     先记 40 条、之后每 50 条记一条（0.1.2：以前你看的那场也一样限，预模拟先把条数用完）。

## 开发

- `python -X utf8 addons/league_elise/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的伊莉丝和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_elise`：单元测试（参数和副本一致、副本的技能2 / 大招对目标施放、换动画名和图里的
  tag、尸体留形态、结茧 / 盘丝 / 大招挑目标）。
- 在 `addons/` 下 `cargo build --release -p league_elise`（Windows）得到 `target/release/league_elise.dll`；`league_addons`
  合集也会编进本包。工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\el_target`）。
- 经典 SDK 的模拟器跑不了原生代码；副本的数据部分（去掉原生被动）在经典 SDK 里跑过，AI 照样放结茧、盘丝和大招。本包只做了
  单元测试，要在游戏里看日志确认。
