# 布兰德被动层数附加包（测试版 v0.1.1）

主包 `league` 保持纯数据。数据只读得到施法者自己身上的 buff，所以主包布兰德的被动「炽热之焰」把层数记在**布兰德身上**：
技能连中不同的英雄也会叠到第 3 层，第 3 下打中的那个英雄爆炸。这个附加包用原生代码做成英雄联盟的样子：

- **层数记在每个敌人身上**：原生效果 `league_brand:blaze` 代替主包里的叠层。技能（W、E 的蔓延、Q、R 的每次弹跳）打中敌方英雄时，
  在**他**身上叠一层（每层 4 秒，再中一下全部刷新），每个英雄各算各的；头顶照旧亮 1 / 2 / 3 个小火苗。
- **第 3 层**：层数清掉，他亮起倒计时火圈，2 秒后在他所在的位置爆炸（等爆炸的这 2 秒里不再叠层；爆炸前死了就不炸）：半径 26000 内的
  敌人（不含防御塔）受到 50 + 30% 法强 + 4% 最大生命值的**魔法伤害**（主包里最大生命值部分只能是真实伤害），并被点燃 4 秒
  （每秒 6 + 4% 法强的魔法伤害）。
- W 的加成伤害和 E 的大范围蔓延照旧看「布兰德最近 4 秒有没有叠过层」（每叠一层刷新他身上的 `league_brand_b_1`）。
- 数字写在 `src/lib.rs` 的常数里，`make_override.py` 生成副本时核对它们和 `tools/kit/build_brand.py` 参数表 `P` 的同名项一致。

## 在游戏里测

1. 主包（League of Legends Heroes 0.70 以上）要装着并启用。
2. 把整个 `league_brand` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_brand.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 让布兰德上场打一局，日志里有 `SPAWN` 一行就说明换上了（选人界面的说明开头是「【层数测试版】」）。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_brand.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN: the add-on's Brand (player 3, team 0)`：这局的布兰德是附加包的副本（游戏里看不到被动说明，靠这行确认；副本的被动是
     诊断用的原生被动 `league_brand:watch`）；
   - `WATCH: alive true, level 9, ap 230; blaze calls so far 12`：每 30 秒一行，叠层被调用过几次；
   - `BLAZE #7: 2 stack(s)`：技能打中英雄 #7，他身上现在 2 层；
   - `BLAZE #7: 3 stacks, detonates in 120 ticks`：第 3 层，2 秒后爆炸；
   - `BOOM #7: 3 enemies within 26000, ap 230 -> 119 + 4% max health magic each`：爆炸打中几个敌人、每人的伤害（减免前）；
   - `BOOM #7: died before the detonation`：他在爆炸前死了；
   - `BLAZE skipped: input kind … is not a unit`：原生效果没拿到被打中的英雄（Q 和 R 弹跳的叠层在「随机目标」效果里，底层游戏的数据里
     没有这种用法的先例）——看到这行请告诉我，那几处要换个写法。

## 开发

- `python addons/league_brand/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的布兰德和参数表一致）。
  主包的布兰德改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_brand`：单元测试（三层引爆、等爆炸时不叠、伤害、点燃、爆炸半径、buff 名字长度）。
- 在 `addons/` 下 `cargo build --release -p league_brand`（Windows）得到 `target/release/league_brand.dll`；`league_addons` 合集也会编进本包。
- 经典 SDK 的模拟器跑不了原生代码。游戏里确认过（2026-10-07，v0.1.1 装进合集后约 30 分钟的日志：12 场对局里叠层 13107 次，1 层 6787、2 层 3980、第 3 层 2179 次；爆炸 2171 次，其中 375 次目标在爆炸前死了；爆炸多数只打到他本人（1293 次），最多打到 10 个；`BLAZE skipped` 0 次，Q 和 R 弹跳在「随机目标」效果里也拿得到被打中的英雄）。
