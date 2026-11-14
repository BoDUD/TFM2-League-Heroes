# 赫卡里姆附加包（v0.1.0）

主包 `league` 保持纯数据。用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」，再说「接着做」（能做的小项都做）。英雄联盟的暴走（Q，wiki V26.03）：命中后得一层，每层让暴走的冷却缩短 0.75 秒（4 秒，满 3 层 1.75 秒）。数据缩短冷却只有 `skill_cooldown_mult` 一种，它会把毁灭冲锋（技能 2）的冷却一起砍掉，所以主包的层数只加伤害。这个附加包用原生代码只缩短暴走这一格：

| | 主包（不装附加包） | 装了附加包 |
|---|---|---|
| 暴走（Q）的层数 | 命中得一层（最多 2 层，8 秒），每层伤害 +20%，冷却固定 4 秒 | **每层再让这一次暴走的冷却缩短 0.75 秒**：1 层 3.25 秒、2 层 2.5 秒；伤害照主包 |

## 怎么做的

- 副本（`override/`，`make_override.py` 从 `tools/kit/build_hecarim.py` 生成，先核对参数表和主包一字不差）技能一字不改，只加本包的被动 `league_hecarim:rampage`，暴走的说明换成本包的。
- 被动每 tick 读他技能（暴走）的剩余冷却：跳起来了（刚放了暴走）就看这时身上的层数——主包的旗子 `league_hecarim_q1`（一层）、`league_hecarim_q2`（两层）——用 `entity_reduce_cooldown` 只把暴走这一格减掉 `CUT`（45 tick = 0.75 秒）× 层数，毁灭冲锋不动。层数按放的那一刻算（这一下打中得的那层算到下一次）；落地回旋（R、E → R 的那一下暴走）不进冷却，也就不减。
- 冷却在动作结束时才开始走（champion-data.md 布兰德 R 那一段）：暴走的动作 24 tick（`Q_ACTION`，主包的 q_dur），这一下的层第 9 tick（`Q_HIT`，q_at）就挂上了，冷却跳起来时身上已经多了这一层。所以被动每 tick 记下层数（最近 32 tick），冷却跳起时取往前 `Q_ACTION` tick——这次暴走放出去的那一刻——的层数：一场仗的第一个暴走（0 层）冷却是满的 4 秒。
- 没做：英雄联盟最多 3 层、每层只多 3% 伤害；这里主包是 2 层、每层 +20%（主包调好的数）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.354 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_hecarim` 文件夹放进 `<游戏目录>\mods\`（要有 `league_hecarim.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看赫卡里姆的暴走说明：开头是「【附加包】」、写着「Q的冷却缩短0.75秒」就说明换上了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_hecarim.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：`SPAWN`：出生 / 复活；`RAMPAGE`：放暴走时几层、冷却从多少减到多少。

## 开发

- `python addons/league_hecarim/make_override.py`：从参数表重新生成 `override/` 和 `text/`（`--check` 只比较，CI 用）。主包的赫卡里姆改了以后要重跑。
- 在 `addons/` 下 `cargo test --release -p league_hecarim`：单元测试（冷却跳起算放出、几层减多少、副本调本包、主包的层数旗子还在）。
- 经典 SDK 的模拟器跑不了原生代码，本包只做了单元测试，要在游戏里看日志确认。
