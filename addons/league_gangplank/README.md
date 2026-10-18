# 普朗克附加包（测试版 v0.1.0）

主包 `league` 保持纯数据。用户选了技能方案 A（「技能方案按 A 做」，带扩展包）。这个附加包用原生代码做主包数据做不到的三件事：
**坏血病疗法真的解除控制**、**残血也吃橘子**、**火药桶按距离连锁**。画面、声音、伤害仍然是主包里的那一套（附加包只判断、挂标记）：

| | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 坏血病疗法（W） | 3 级起被控制或被围攻时自动吃橘子：回血、免控 1 秒；已经在身上的控制要等它自己结束 | 同上，另外吃下去的那个 tick **清掉他身上的硬控**（英雄联盟：W 解除控制）；**生命低于 40%** 也会吃 |
| 火药桶连锁（E） | 一个桶炸开，另一个点燃的桶边有敌人就跟着炸（不管两个桶多远）；桶边没人就不炸 | 两个桶相距不超过 `e_chain`（70000）才连锁；桶边有敌人照样由数据炸，**桶边没人也空炸**（画面、声音、刷新烈火审讯和加速都有） |

## 怎么做的

- **清控**：副本里吃橘子时给他挂 2 tick 的 `league_gangplank_w_now`；本包看到它出现、他身上又有硬控（击飞、眩晕、禁锢、嘲讽、恐惧、魅惑、
  强制位移——游戏 0.6.4 把施法动作也记成一种控制，所以不用 `cc_count() > 0`），就 `entity_clear_cc`。清控会连正在放的施法动作一起清掉，
  所以两个副本里吃橘子的动作、声音和回血都放在决定之后 2 tick；免控在决定时就挂上，这 2 tick 里不会再被控。
- **残血**：他活着、生命低于最大值的 `w_low`% 时一直挂着 `league_gangplank_w_low`，数据的自检（每 12 tick）看到它也会吃（3 级起、W 不在冷却）。
- **连锁**：桶落地（`k<s>_live` 出现）时，他新出现的两个区域落在同一点，那就是桶的位置（`ProjectileInfoV1` 没有名字）。一个桶炸开后一 tick
  数据挂 `k<s>_now`；另一个桶已点燃、两桶相距不超过 `e_chain` 时本包挂 3 tick 的 `k<o>_cn`，副本的触发区读它（主包读的是另一个桶的爆炸，
  不量距离），桶边有敌人下一 tick 就炸。桶边 `e_r` + 20000 以内一个敌方单位都没有时本包空炸：挂 `k<o>_blew`（数据的下一次贴图画爆炸）、
  摘掉 `k<o>_live` / `k<o>_ripe`，摘 `p_cd`、给被动加速（和数据的爆炸一样）。
- 本包**不按任何技能键**（不会在技能没解锁时按键，解锁总闸也不涉及）。

参数写在英雄数据的 `passive.params`（`{"e_chain": 70000, "e_link": 10, "e_r": 30000, "p_ms": 20, "p_ms_t": 120, "w_low": 40}`），由
`make_override.py` 从 `tools/kit/build_gangplank.py` 的参数表 `P` 写入。

## 在游戏里测

1. 主包（League of Legends Heroes 0.145 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_gangplank` 文件夹放进 `<游戏目录>\mods\`
   （要有 `league_gangplank.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看普朗克的普攻说明：开头是「【附加包】」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_gangplank.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `SPAWN`：出生；`CLEANSE`：吃橘子清掉了几个控制；`LOW`：生命低于线、挂上 `w_low`；`KEG`：桶的位置找到了；`KEG?`：桶落地后没找到
     它的两个区域；`CHAIN`：连锁（交给数据，或本包空炸）。

## 开发

- `python addons/league_gangplank/make_override.py`：从参数表重新生成 `override/` 和 `text/`（先核对主包的普朗克和参数表一致）。
  主包的普朗克改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_gangplank`：单元测试（参数、残血线、连锁距离、从新区域里认出桶）。
- 在 `addons/` 下 `cargo build --release -p league_gangplank`（Windows）得到 `target/release/league_gangplank.dll`；`league_addons`
  合集也会编进本包。工作区路径很长时用 `CARGO_TARGET_DIR` 指一个短路径（链接器打不开长路径的临时文件）。
- 经典 SDK 的模拟器跑不了原生被动，本包只做了单元测试，要在游戏里看日志确认。
