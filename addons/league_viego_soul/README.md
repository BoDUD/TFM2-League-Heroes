# 佛耶戈「君命已决」附加包（v0.1.0，可选）

**不装这个附加包，主包里的佛耶戈也是完整的**：附身的效果（无敌、回血、借来的属性、Q / W 刷新、亡魂黑雾、放大招回到本体）都在主包里。
主包是纯数据，有几件事做不到，这个附加包用原生代码补上：

| | 主包（纯数据） | 装了附加包（照英雄联盟） |
|---|---|---|
| 什么时候附身 | 数据看不到谁死了：他打过的英雄身上挂一个每 tick 续命的计时，计时断了就当它死了；同一时间打过两个英雄，只看得到最后死的那个 | 读每个敌方英雄的死亡：他 3 秒内打过的英雄一死就算他的功劳，每个都算 |
| 灵魂在哪 | 当场附身（在他自己身上） | 尸体那里留下灵魂 8 秒，他走到 35000 以内才附身（照英雄联盟要去拿那个灵魂） |
| 附身后的样子 | 还是佛耶戈，身上裹一圈亡魂黑雾 | **整个身体变成被附身的那个英雄**：站、跑、出招、挨打都是那个英雄的图（只在游戏 0.6.3 上，别的版本退回左边那样） |
| 附身后的招式 | 佛耶戈自己的 Q、W、E，攻击 / 攻速 / 移速加成 | 按那个英雄的类别换成五套招式之一：**近战**（重斩、震地减速、冲锋眩晕）、**射手**（远程射击、穿透射击、三连射）、**法师**（法球、溅射爆发、定身）、**辅助**（远程射击、治疗周围友方英雄、减速周围敌人并加速）、**刺客**（快斩、闪到目标身边重击、隐身加速）；远程三类攻击距离 +25000 |

## 怎么做的

- `mod.override_info` 把主包的佛耶戈换成 `override/` 里的副本（`make_override.py` 从 `tools/kit/build_viego.py` 生成，native=1；主包的
  佛耶戈改了就重跑）：
  - 他的普攻、Q、W、R 打中英雄时在对方身上挂 `league_viego_mark`（3 秒），代替主包的计时近似；
  - 普攻、Q、W 按身上的 `league_viego_soul_<类别>`（melee / range / mage / util / assassin）换成五套招式，没有就是他自己的；
  - 每个动作开头看本包给的 `league_viego_p_go` / `league_viego_p_off`：播吸魂（附身动作、亡魂、声音、台词）/ 回到本体的黑雾；
  - `passive` 挂本包的被动 `league_viego_soul:possess`（参数来自 build_viego.P：附身时长、无敌时长、回血、借来的属性、灵魂距离和时长）。
- 被动每 tick 看敌方英雄身上的标记，有标记的英雄由活变死就在尸体处留下灵魂；他活着走近就附身：挂外形标记
  `league_viego_soul:<英雄 id>`、类别 buff、`league_viego_p_on`（属性）、`league_viego_p_safe`（无敌免控）、一下冷却刷新，回血。
  时间到、他阵亡、或主包的大招拿掉了 `league_viego_p_on`，就拿掉外形和类别。类别按英雄 id 查 `src/souls.rs`（`make_override.py` 从
  原版英雄表和本包英雄生成），查不到的英雄（别的 mod）按攻击距离猜。
- **整身外形**（`src/view.rs`，只在游戏 0.6.3 上）：和凯隐附加包挂在同一个显示处理槽上（rva 0x3c31358，一个接一个调用）。每帧找名字
  是 `league_viego`、身上有外形标记的画面实体，把被附身英雄画面实体的**资源名**（值 +0x50 的字符串：身体用哪套图）抄过来，正在播的
  动画名那个英雄的图里没有就换成他有的（skill2 → skill → attack → idle）；附身结束写回原来的资源名。`src/souls.rs` 里没有的英雄不换
  外形（名字对不上图，游戏会 panic）。资源名这个字段是从工坊 Rin 的佛耶戈 mod 的显示代码里读出来的，本包不依赖它，也不依赖
  tfm2_ppu_core / tfm2_transform_core。
- 原生代码只做判断（记功、灵魂、附身开始和结束、换外形）和 buff；画面、伤害、治疗在数据里。

## 在游戏里测

1. 主包（League of Legends Heroes 0.92 以上）要装着并启用。
2. 玩家装的是附加包合集 `league_addons`（见 [`../league_addons/README.md`](../league_addons/README.md)），佛耶戈的部分和这里一样；
   单独测时把 `league_viego_soul` 文件夹（含 `league_viego_soul.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）放进
   `<游戏目录>\mods\`，在 MOD 菜单里启用并排在主包后面，重启游戏（和合集不能同时启用）。
3. 看佛耶戈普攻的说明：「君命已决（附加包）」就说明副本生效了。
4. 日志在 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_viego_soul.log`，每次启动游戏重写（上一次的留在 `.prev.log`）：
   - `whole-body possession on: ...`：显示钩子挂上了（`off (...)` = 不是 0.6.3，只有数据的黑雾）；
   - `SOUL league_jinx (range) at (...)`：他参与击杀，尸体处留下灵魂；
   - `POSSESS league_jinx (range) for 600 ticks, heal ...` / `END possession of league_jinx (time | Heartbreaker | dead | a new soul)`；
   - `world 0x... Viego #...: drawn as league_jinx (soul league_jinx)`：画面上的佛耶戈换成了那个英雄的图。
