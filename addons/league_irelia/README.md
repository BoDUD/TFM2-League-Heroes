# 艾瑞莉娅附加包（测试版 v0.1.3）：Q「利刃冲击」真正的刷新 + 跳兵线

用户选艾瑞莉娅技能时选了「做附加包：Q 真实刷新」。主包 `league` 保持纯数据：数据读不到目标身上的 buff，也不知道一次伤害打死了谁，
所以主包里

- E「比翼双刃」、R「先锋之刃」打中英雄时，在**她自己身上**挂一面旗子 `mk` 代替印记，下一次 Q 施放时附近有敌方英雄就算「打到了带印记的」；
- Q 打死目标靠 league_jinx 的击杀触发器（一个 3 tick 的持续效果在目标活着时拿掉旗子）近似。

这个附加包把主包的艾瑞莉娅换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_irelia.py` 的 `--native` 生成：技能一样，
只是印记是挂在被打中的英雄身上的真 buff `league_irelia_mark`，Q 落地不再自己判断击杀），被动 `league_irelia:surge`：

- **真实刷新（英雄联盟原版）**：她身上 `league_irelia_q_dash` 出现 = 一段 Q 冲刺开始，冲刺里她第一次造成伤害的单位就是 Q 的目标。
  目标**身上有印记**：拿掉印记（被 Q 消耗），给她挂 `league_irelia_q_again`；目标**被这一下打死**（英雄看 `on_kill`；小兵、野怪死了游戏不调 `on_kill`，看冲刺窗口里目标没了或没血）：也挂。数据里的轮询
  看到 `q_again` 就再冲一段（被控的英雄 → 英雄 → 最近的单位，一次施放最多 3 段）。
- **跳兵线（AI 钩子 `league_irelia:hop`）**：Q 好了、射程里没有敌方英雄、但 90000 以内有一个看得见、不在敌方塔下的英雄，她自己血量
  不低于 40% 时，挑一个 Q 射程内、这一下 Q 能打死（估算伤害按护甲打折，大于它现在的血量）、而且比她更靠近那个英雄的小兵或野怪，
  对它放 Q：打死它就刷新，下一段冲向英雄。内置 AI 本来就要放 Q 时，射程里有带印记的英雄就改打他。

数字从英雄数据的 `passive.params` 来。只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_irelia.log`（`SPAWN` 每次出生；`RESET #n (mark|kill)` 每次刷新；
`HOP:` 跳兵线；`Q AT THE MARK:` 改打带印记的英雄；`Q HIT` Q 打中的小兵、野怪）。每种行整个游戏一个计数：你看的那场每条都记，
服务器的预模拟先记 40 条、之后每 200 条记一条（0.1.3：以前每个艾瑞莉娅自己数、每份预模拟又从 #1 记起，`SPAWN` 每次复活都记，
一次启动记了一万一千多行）。

## 在游戏里测

1. 主包（League of Legends Heroes 0.95 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_irelia` 文件夹放进 `<游戏目录>\mods\`，文件夹里要有
   `league_irelia.dll`、`mod.mod_info`、`mod.override_info`、`override\`。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。

## 开发

```bash
python addons/league_irelia/make_override.py      # 主包的艾瑞莉娅改了就重跑
cd addons && cargo test --release -p league_irelia && cargo build --release -p league_irelia
```

## 游戏 0.6.5（0.1.2）

回城时不跳兵线（AI 的回城命令开始、别的命令结束，中间没命令的 tick 也算），也不朝 AI 正在远离的英雄跳（`league_ult_press` 0.5.0 的规则，0.6.5 的官方 AI 自己决定回城、撤退）。
