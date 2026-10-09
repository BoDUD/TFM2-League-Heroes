# 奥拉夫读血附加包（测试版 v0.1.0）

主包 `league` 保持纯数据，不装本包也完整、平衡过。数据读不到生命，所以主包里奥拉夫的被动「狂战之怒」是替代做法：

- **主包**：挨打计数——普攻时发现 1 点护盾被打破就升一层（`league_olaf_p_1`..`p_4`，每层攻速 +20%，最高两层再吸血 12%），离开战斗一段时间掉一层。
- **英雄联盟**：已损失的生命越多，攻速越高。

本包用原生代码读真实的生命，做成英雄联盟的规则：

- 被动 `league_olaf_rage:rage`（挂在 `passive` 上，每 tick 运行）读奥拉夫的生命：**已损失 15%** 起一层，之后**每多损失 17%** 再多一层，最多 4 层（损失 15% / 32% / 49% / 66%）；层数一变就把 `league_olaf_p_1`..`p_4` 换成新的层数——和主包同样的名字、同样的数值，满层的红色怒气画面照常显示。
- 主包副本去掉了挨打计数（`league_olaf_sense` 和它的 1 点护盾），技能树更小。
- 数字都写在英雄数据的 `passive.params` 里，由 `make_override.py` 从 `tools/kit/build_olaf.py` 的参数表 `P` 写入（`p_n`、`p_as`、`p_vamp`、`p_vn`、`n_lo`、`n_band`），本包不另记一份。

## 在游戏里测

1. 主包（League of Legends Heroes 0.85 以上）要装着并启用。
2. 把整个 `league_olaf_rage` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_olaf_rage.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看奥拉夫普攻的说明：开头是「【读血测试版】」、写着「已损失生命越多攻速越高」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_olaf_rage.log`，每次启动游戏重写：
   - `SPAWN: the add-on's Olaf ...`：本包接管了这个奥拉夫，后面是读到的参数；
   - `RAGE 1 -> 2: hp 610/1100 (55%)`：层数变化和当时的生命（应当和上面的门槛对得上）。

## 开发

- `python addons/league_olaf_rage/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的奥拉夫和参数表一致）。
  主包的奥拉夫改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_olaf_rage`：单元测试（层数门槛、参数读取、层的 buff）。
- 在 `addons/` 下 `cargo build --release -p league_olaf_rage`（Windows，长路径时用短的 `CARGO_TARGET_DIR`）得到
  `league_olaf_rage.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试；层数要在游戏里看日志确认。
