# tft 包的代码（`tft.dll`）

tft 包（mod_id `tft`，源文件在 [`tft/`](../../tft/)）是原生 mod：英雄是数据，数据做不到的地方写在这个 crate 里，编成 `tft.dll` 跟着 tft 包一起装（`python tools/package_mod.py --src tft ...` 会编好带上）。所有 tft 英雄都在这一个 mod 里，每个英雄一个模块（用户，2026-10-26：「诺拉和爆爆合并在一个mod啊」「tft的英雄都放一个mod里 参考英雄联盟」）。新英雄：在 `src/` 加一个模块，在 `src/lib.rs` 的 `init` 里调用它的 `register`。

| 英雄 | 模块 | 做什么 |
|---|---|---|
| 爆爆 `tft_powder` | — | 纯数据 |
| 诺拉 `tft_norra` | [`src/norra.rs`](src/norra.rs) | 照英雄联盟手游做的规则（下面） |

## 诺拉

用户：「你要参照手游的技能啊」「不一致的地方就做附加包」——技能照英雄联盟手游（Wild Rift），规则按手游现在的诺拉（Wild Rift wiki 和 7.3 的改动记录）。她的数据（[`tools/kit/build_norra.py`](../../tools/kit/build_norra.py)）调用这里的效果，`passive` 是 `tft_norra:trinkets`，参数来自参数表 P（`build_norra.NATIVE_KEYS`）。`build_norra.py --plain` 是不调用 DLL 的纯数据版（经典引擎的平衡模拟跑不了 DLL 的代码），左边一栏是它的近似：

| 机制 | 纯数据近似（`--plain`） | tft.dll |
|---|---|---|
| 寄情琐物（被动） | 落点放**一片**琐物，走进去的敌方英雄各挨一次 | 落点**撒 3 个**（手游按等级 2/3/4 个）：中间茶杯、左右各一个水晶，敌方英雄**踩到哪个，哪个飞到他身上**炸开，别的还在（`tft_norra:drop`、`tft_norra:trinket`） |
| 琐物冷却 | 固定 `p_cd` | 技能（Q、W、E）**命中敌方英雄**，冷却减少总冷却的 20%（`tft_norra:refund`） |
| 回忆涌现（Q） | 落点周围一圈打琐物伤害 | 对**已有线缕**的英雄多打最大生命 `q_bonus`‰；蓄满的 Q **打中英雄**，地上的琐物变成「附近有人就炸」（`tft_norra:surge`） |
| 奇异旅程（W，并进被动） | 只在**她普攻**、身边有敌方英雄时开门 | 敌方英雄**一贴身**就开门（被动每拍看：她活着、能被选中、不在控制里、冷却好了；`entity_banish`） |
| 传送门欢腾！（R） | 每波打**裂隙里所有**敌方英雄 | 每波两个毛线球从裂隙**两头沿一条线对飞**（线穿过裂隙里的一个敌方英雄，每波轮到下一个），路上敌人每波挨一次，**每个球碰到的第一个英雄**减速（`tft_norra:rift`、`volley`、`yarn_l` / `_r`） |

会变的东西都在模拟里（排着的效果、身上的状态），只有参数按诺拉的单位编号记一份给效果用（服务端预模拟和你看的那场是同一份数字）。图（`tools/art/import_norra_fx.py`）：琐物的三块 `p_trinket_l` / `_c` / `_r` 和飞的毛线球 `r_ball` 在 `tft_norra_fx` 里。

## 检查

- 在 `addons/` 下 `cargo test -p tft`（CI 也跑）：诺拉的单元测试（参数、伤害和冷却的数、三个琐物的位置、琐物装进输入再取出来、自己那发 Q 不引爆自己的琐物、最近的英雄、毛线球的线、名字）。
- `python tools/kit/build_norra.py` 每次都核对 `src/norra.rs` 的默认参数和 P 一致。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_norra.log`：`SPAWN`、撒琐物 `DROP`、琐物飞出 `TRINKET`、引爆 `PRIMED`、减冷却 `REFUND`、Q 的加伤 `SURGE`、开门 `JOURNEY`、裂隙 `RIFT`、每波 `VOLLEY`、毛线球命中 `YARN`。
