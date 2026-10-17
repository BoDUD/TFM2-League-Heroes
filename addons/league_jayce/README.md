# 杰斯附加包（测试版 v0.1.0，可选）

**不装这个附加包，主包里的杰斯也是完整的**：锤 / 炮两种形态、按战况切换、苍穹之跃、电能震荡、雷霆一击、闪电领域、超能电荷、
海克斯科技电容和 5 级的加速电炮都在主包数据里。主包是纯数据，有几件事做不到，这个附加包用原生代码补上（用户 2026-10-15 选的三件）：

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 炮形态的样子 | 只有出招（普攻、电能震荡、超能电荷、变身、大招）是炮的动作，待机、跑步、受击还是锤子（游戏按名字自动播这几个，数据换不了） | **整个身体**都是炮：待机、跑步、受击播 `c_idle` / `c_run` / `c_hit`（只在游戏 0.6.4 上，别的版本退回左边那样）；阵亡还是锤子的倒地 |
| 雷霆一击往哪推 | 笔直推离杰斯 | 打中的敌方英雄推向**他这边**：8 万内有他的友方英雄就推向它们的中心，没有就推向离目标最近的己方塔；这个方向 35000 内碰到墙就左右最多偏 60°，都不行（或者没有友方和塔）才笔直推开。距离、速度和主包一样；小兵、野怪照旧 |
| 加速电炮打谁 | AI 选的英雄 | 射程内、线上没有别的英雄挡着（电炮停在第一个英雄身上）的敌方英雄：**这一炮打得死的**先（生命 + 护盾不超过估算的伤害，按护甲打折），再是受了伤的里生命比例最低的，都满血就挑**最远的** |

## 怎么做的

- `mod.override_info` 把主包的杰斯换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_jayce.py` 的 `native=1`
  生成，主包的杰斯改了就重跑）：加上本包的被动 `league_jayce:hextech`（参数 `kb_speed` 2500、`kb_t` 14、`gate_range` 90000、
  `gate_dmg` 140、`gate_ad` 161：击退和电炮的数，都从参数表 P 来），打英雄的那支雷霆一击的 `Knockback` 换成本包的原生效果
  `league_jayce:blow`，普攻、技能2、大招的说明开头加【附加包】。
- **整身变炮**（`src/view.rs`）：照奈德丽附加包的整身变豹换**正在播的动画名**。显示世界每帧调用的更新函数（rva 0x23312a0，
  槽 rva 0x3c82db8）换成本包的函数：先调用槽里原来的（游戏的，或凯隐 / 佛耶戈 / 奈德丽附加包的），再看名字是 `league_jayce` 的
  画面实体：身上有炮形态的 buff `league_jayce_cn` 时，正在播的 `idle` / `run` / `hit` 换成 `c_idle` / `c_run` / `c_hit`，普攻的
  第一 tick `attack` 换成 `c_attack`（免得每次出手闪一下锤子）；变回锤子就换回来。高清帧不用另管：league.dll 把动画表里每个动作
  （`c_idle` 也在内）就地换成它的 `hd_` 帧。
- **往己方击退**（原生效果 `league_jayce:blow`）：算好方向后用引擎的强制位移（`ForceMove`，数据的 `Knockback` 也是它）推
  `kb_speed` x `kb_t`；免疫控制的不推。墙用卡蜜尔附加包的内置墙格（`league_camille_wall/src/maps.rs`，巴德附加包同样用它）。
- **挑目标**（AI 钩子 `league_jayce:gate`）：AI 要放大招时按上表换目标；伤害估算 (140 + 161% 攻击力) x 100 / (100 + 护甲)。
- 原生代码只做判断、换名字和推的方向，伤害、减速、电炮都在数据里。

## 在游戏里测

1. 主包（League of Legends Heroes 0.114.0 以上）要装着并启用。
2. 把整个 `league_jayce` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_jayce.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看杰斯普攻的说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_jayce.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `FORM whole-body cannon on: display slot …`：整身变炮装上了（`off (…)` 就是游戏版本不对）；
   - `FORM display … Jayce #…: CANNON on` / `hammer`：画面里变了形态；`FORM sim: CANNON on` / `cannon off`：模拟里的形态 buff；
   - `BLOW 某英雄 at (…): toward 2 allied champions` / `toward his nearest tower` / `straight away from him (…)`：雷霆一击往哪推；
   - `GATE A -> B (KILL: … / LOWEST: …% hp / FARTHEST …) AIM`：电炮换了目标（`kept` 是 AI 本来选的就是它）。

## 开发

- `python -X utf8 addons/league_jayce/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的杰斯和参数表一致）。
- 在 `addons/` 下 `cargo test --release -p league_jayce`：单元测试（参数和副本一致、换动画名和图里的 tag、推的方向和避墙、电炮挑目标）。
- 在 `addons/` 下 `cargo build --release -p league_jayce`（Windows）得到 `target/release/league_jayce.dll`；`league_addons`
  合集也会编进本包。工作区路径太长时链接会失败（LNK1104），用短的 `CARGO_TARGET_DIR`（如 `C:\t\jy_target`）。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
