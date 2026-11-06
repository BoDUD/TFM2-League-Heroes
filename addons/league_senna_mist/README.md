# 赛娜黑雾常驻附加包（测试版 v0.1.0）

用户：「灵魂层数 这个可以做扩展包吧」。主包 `league` 保持纯数据：赛娜被动「赦除」收集的每一层黑雾（灵魂）是她身上一个永久的
`league_senna_mist`（攻击 +1、攻击距离 +100，每第二层再带 1% 暴击），叠层靠一个永久的单双开关 `league_senna_m_odd`。引擎在她
死亡时清掉身上全部 buff，数据也没有「复活时」这个时机，所以主包里黑雾每条命从零叠起（说明里写着「死亡清空」）。英雄联盟里
赛娜的黑雾是永久的。

这个附加包把主包的赛娜换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_senna.py` 的 `--native` 生成：技能
一字不改，只加被动 `league_senna_mist:keep`，普攻说明里的「（死亡清空）」换成「（扩展包保留）」），被动每 tick 看一次：

- 活着时把身上每一层 `league_senna_mist` 原样记下来（记在被动里，被动在玩家身上，死了不丢）；
- 身上比记下的少了（死亡或复活时引擎清掉）就把缺的层原样补回（暴击层还是暴击层），再按层数单双补上或去掉
  `league_senna_m_odd`，下一层照样轮到该带暴击的那一种。死着的时候也补，倒下时数值不掉。

黑雾只会变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。

只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_senna_mist.log`
（`DEAD` / `ALIVE` 带记下的层数，`KEEP` 补回了几层、死着还是活着、单双开关）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.90 以上）要装着并启用。
2. 把整个 `league_senna_mist` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有 `league_senna_mist.dll`、`mod.mod_info`、
   `mod.override_info`、`override\`、`text\`（或者用附加包合集 `league_addons`，里面已经包含本包）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看赛娜普攻（被动）的说明：写着「（扩展包保留）」就说明换上了。

## 开发

```bash
python addons/league_senna_mist/make_override.py      # 主包的赛娜或她的说明改了就重跑
cd addons && cargo test --release -p league_senna_mist && cargo build --release -p league_senna_mist
```

## R 的暗影核心不再跨过一半的人（0.1.1，2026-11-06）

游戏 0.7.1 的投射物判定（拿 11-05 阿克尚 R 的子弹对出来的，见 league_akshan 0.2.7）：投射物每 tick 跳 `speed` 那么远，只打圆心在它这一 tick 位置 `radius` 以内的单位——不扫两个 tick 中间，也不算单位的体型。`speed` 大于两倍 `radius` 时，站在两 tick 之间的人整个被跨过去；圆比英雄的体型（10000）小很多时，要几乎正中才打得到。

主包 R 的核心 `league_senna_r_core` 圆 7500、每 tick 飞 30000：线上一半的地方是空当，站在那里的英雄不挨伤害。主包 `build_senna` 的 `r_rad` 改 15000（英雄联盟 320 宽的核心加体型，= 速度的一半），副本重新生成；护盾那条宽光（100000）不变。
