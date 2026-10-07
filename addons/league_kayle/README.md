# 凯尔升阶常驻附加包（测试版 v0.1.0）

用户：「能一直保持吗 死后不掉」。主包 `league` 保持纯数据：凯尔 5 / 8 / 12 级的升阶是她身上永久的 `league_kayle_rank5` /
`rank8` / `rank12`（12 级再加 `form3`），身后的翅膀绑在它们上。引擎在她死亡时清掉身上全部 buff，数据又没有「复活时」这个
时机，所以主包每条命第一次出手才静默补读等级：从倒下到复活后第一次出手，她没有翅膀，射程也回到近战。

这个附加包把主包的凯尔换成 `override/` 里的副本（`make_override.py` 生成：技能一字不改，只加被动 `league_kayle:ascend`），
被动每 tick 看一次：

- 活着时身上有哪几阶就记下来（记在被动里，被动在玩家身上，死了不丢）；
- 记下的阶身上缺了就原样补上，数值和主包一样（rank5 射程 +27500；rank12 攻速 +30%、移速 +10%、射程 +10000；rank8、form3
  只有画面）。死着的时候也补，倒下时翅膀还在；复活时引擎再清一次也马上补回；
- 补过之后（或补的阶撑过了死亡）给她挂上 `league_kayle_life`，主包这条命就不再补读：补读不看身上已有的阶，同名 buff 会叠成
  两层，射程变两倍。

新的一阶仍由主包的等级探测在出手时认出来（金翼仪式和语音照旧）；本包只补已经升过的阶，从不提前。提示文字没改（主包的已经
到详情面板的长度上限）。

只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kayle.log`
（`RANK` 记下一阶，`DEAD` / `ALIVE`，`KEEP` 补回了哪几阶、死着还是活着，`LIFE` 跳过主包补读）。

```bash
python addons/league_kayle/make_override.py      # 主包的凯尔改了就重跑
cd addons && cargo test -p league_kayle && cargo build --release
```
