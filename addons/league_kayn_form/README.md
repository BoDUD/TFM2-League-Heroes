# 凯隐「暗裔魔镰」附加包（v0.1.0，可选）

**不装这个附加包，主包里的凯隐也是完整的**：两种形态（暗裔杀手、影流刺客）的外观、光环、出招动作和效果都在主包里。
主包是纯数据，有两件事做不到，这个附加包用原生代码补上：

| | 主包（纯数据） | 装了附加包（照英雄联盟） |
|---|---|---|
| 攒哪种形态 | 技能打中**身边**的英雄攒暗裔（2 次），W 只打中**远处**的英雄攒影流（1 次）——数据读不到目标是近战还是远程，按距离近似 | 打中**近战英雄**攒暗裔、打中**远程英雄**攒影流（普攻和技能都算，各 14 次），按英雄的攻击距离分 |
| 形态能留多久 | 这条命（数据的 buff 阵亡就清掉，复活后重攒） | **整局**：阵亡复活后光环和形态效果直接回来 |

## 怎么做的

- `mod.override_info` 把主包的凯隐换成 `override/` 里的副本（`make_override.py` 从主包生成，主包的凯隐改了就重跑）：
  - 主包里四处攒能量的数据块（Q 旋转、W 近段、W 远段、R 破体，开头有 `league_kayn_mk_charge` 标记）换成「在打中的英雄身上挂
    `league_kayn_tag` 30 tick」，普攻打中英雄也挂；
  - 普攻第 1 tick 先看凯隐身上有没有本包给的准备标记（`league_kayn_ready_d` / `_s`），有就播主包的变身（动作、画面、声音、
    永久的形态 buff 和光环）并去掉标记；
  - `passive` 挂本包的被动 `league_kayn_form:orbs`（参数 `darkin_need` 14、`shadow_need` 14）。
- 被动 `orbs` 每 tick 看敌方英雄身上的标记（一层 = 一次命中），按英雄 id 查攻击距离（`src/ranges.rs`：原版英雄来自游戏数据，
  本包英雄来自各自的技能文件，`make_override.py` 生成），**35000 以上算远程**；查不到的英雄（别的 mod）按挂标记那一刻离凯隐
  多远猜（30000 以外算远程）。哪边先满就给凯隐挂准备标记，形态记在被动里（被动挂在玩家身上，阵亡不丢）：复活时、以及之后
  每 tick 发现凯隐身上没有形态 buff 也没有准备标记时，直接补上永久的形态 buff（变身动作只在第一次播）。
- 本包只换凯隐，别的英雄原样不动。原生代码只做判断（数标记、定形态、补 buff），画面、伤害、治疗都在数据里。

## 在游戏里测

1. 主包（League of Legends Heroes 0.52 以上）要装着并启用。
2. 把整个 `league_kayn_form` 文件夹放进 `<游戏目录>\mods\`，里面要有 `league_kayn_form.dll`、`mod.mod_info`、`mod.override_info`、
   `override\`、`text\`。
3. 进游戏，在 MOD 菜单里启用它（含代码的 mod 会弹一次确认），确认排在主包后面，重启游戏。
4. 看凯隐普攻的说明：「暗裔魔镰」后面写着「【附加包·照英雄联盟】」就说明副本生效了。
5. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kayn_form.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `DARKIN ready: darkin 14/14 shadow 6/14 (last hit #… fighter, range Some(23000))`：暗裔攒满，下一次普攻变身；
   - `SHADOW ready: …`：影流攒满；
   - `DARKIN form restored (respawn)`：复活后形态补回来。

## 开发

在 `addons/` 里（长路径会让链接器报 LNK1104，目标目录放短路径）：

```
CARGO_TARGET_DIR=%LOCALAPPDATA%/Temp/<x>/target cargo test -p league_kayn_form
CARGO_TARGET_DIR=%LOCALAPPDATA%/Temp/<x>/target cargo build --release -p league_kayn_form
python addons/league_kayn_form/make_override.py      # 主包的凯隐或别的英雄的攻击距离改了就重跑
```

`tests/wiring.rs` 走真实的导出入口跑被动：近战 / 远程分边、门槛、队友身上的标记不算、阵亡复活补回形态、准备标记过期也补、
查不到的英雄按距离猜。原生代码在 SDK 模拟里跑不了，平衡靠主包的数据部分和游戏日志。
