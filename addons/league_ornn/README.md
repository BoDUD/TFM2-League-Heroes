# 奥恩附加包（测试版 v0.1.0，可选）

**不装这个附加包，主包里的奥恩也是完整的**：普攻里每 12 秒喷一次风箱炎息；Q 火山突堑砸出一道裂隙、尽头升起熔岩柱；E 炽烈冲锋
在 Q 之后 4 秒内撞过去就地震击飞；R 熔铸之神的召唤召来熔岩公羊冲向自己，再一头槌把它顶回去；被动活体锻炉加护甲、魔抗和生命，
W / E / R 让敌方英雄易碎，下一下普攻引爆。主包是纯数据：**数据只读得到施法者自己身上的 buff**，所以主包把易碎记在奥恩身上（他的下一下
普攻打中任何英雄都引爆）；**数据造不出挡路的地形，也看不到柱子在哪**，所以主包的柱子只是画面，Q 之后 4 秒内的冲撞都算撞上柱子；
**数据读不到装备**，所以主包的活体锻炉只加护甲、魔抗和生命。这个附加包用原生代码把英雄联盟的做法做出来（用户 2026-10-21：技能方案 A、
上单、做附加包、「有连招要做连招」「有装备系统吧 你可以加强装备属性吧」「你也要能兼容mod的装备啊」）。

| | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 熔岩柱 | 只是画面，4 秒 | **真的地形**：立在裂隙的尽头 4 秒，立起时把站在上面的单位推开，之后谁都走不进去（两边的英雄、小兵、野怪，他自己也算） |
| E 的地震 | Q 之后 4 秒内的冲撞都地震 | **撞上柱子或墙才地震**：撞上目标的那一刻柱子够近（30000 加上柱子和他的半径），或冲撞方向 14000 内是墙（卡蜜尔附加包的墙格、地图的四边）；撞上的柱子随之碎掉 |
| 易碎 | 记在奥恩身上：W / E / R 打中英雄后，他的下一下普攻打中任何英雄都引爆 | **记在每个英雄身上**：只有带着易碎的英雄被他普攻打中才引爆（最大生命 8% 的真实伤害、击飞、从他身边击退） |
| 活体锻炉 | 护甲、魔抗 +10%，生命 +6% | **装备的主属性 +20%**（攻击、法强、护甲、生命、魔抗、攻速），按他身上的装备 buff 算，游戏的、数据 mod 的、原生 mod 的装备都一样；**9 级起锻造杰作**（英雄联盟 13 级）：他自己的装备 +35%，每个友方英雄的装备 +10% |
| 连招 | 数据里：Q 之后 4 秒内的 E 地震；R 的两段在一次施法里（公羊回到身边就头槌） | AI 钩子按顺序：**Q → E**（AI 想放 E 而柱子没立、Q 好着时先放 Q 朝那人立柱）、**柱子旁边的英雄**（柱子立着、E 好了、有敌方英雄离柱子够近就替 AI 按 E 撞过去）、**易碎优先**（普攻够得着带易碎的英雄就改打他） |

## 怎么做的

- `mod.override_info` 把主包的奥恩换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_ornn.py` 的 `native=1` 生成，先核对
  不带 native 的生成结果和主包的 `league/champion/league_ornn.data_champion` 一字不差，主包的奥恩改了就重跑）：被动是本包的
  `league_ornn:forge`（用到的数字在 `passive.params`，和 `src/lib.rs` 的常量核对，不一致就停）；裂隙到头时跑 `league_ornn:pillar`，
  E 出发时 `league_ornn:from` 记下起点、撞上目标时 `league_ornn:charge` 判断地震，普攻打中英雄时 `league_ornn:shatter` 引爆易碎；
  普攻、Q、E 的说明开头加【扩展包】。
- **熔岩柱**：位置记在他身上的 buff 名里（`league_ornn_pillar@x,y`，同一局的两份预模拟各记各的），被动每 tick 读它：中心进了柱子
  （`PILLAR_R` + 单位半径）的单位放回上一 tick 的位置。
- **地震**：`league_ornn:charge` 判断撞上的是柱子还是墙（`wall_ahead` 读 `league_camille_wall` 的地图墙格），给他挂 1 tick 后数据读的
  `league_ornn_e_quake_go`（周围击飞、伤害、易碎都是主包的数据），撞上的柱子从 buff 名里去掉。
- **易碎**：英雄身上的 `league_ornn_brittle`；引爆用 `deal_damage_typed(Fixed)`、击飞和击退，易碎随之去掉。
- **活体锻炉**：每 30 tick 读每个英雄身上的装备 buff（永久的、名字和某件装备的 `key` 一样的 buff：铁剑是 `ironsword`；没有名字的 buff 不算
  装备），按主属性算出该加多少，只补差额（`league_ornn_forged`、杰作 `league_ornn_masterwork` 两个永久 buff；重挂生命会掉血）。
  一件都认不出来时才退回游戏 0.6.4 的装备表 `ITEMS`。吸血、暴击、穿透、减伤、韧性、冷却这些副属性不放大。
- **连招**（`src/combo.rs`）：`add_player_input_ai`，优先级 110（排在 league_ult_press 之后），被控住、正在放技能或被强制位移时不动；
  按 Q、E 之前自己看格子解锁了、冷却为 0（引擎的「输入合法」不看冷却）。
- 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ornn.log`：`SPAWN`、`PILLAR`（立柱）、`HOLD` / `PUSH`（挡在柱子外）、
  `CHARGE`（撞柱 / 撞墙 / 没撞）、`BROKEN`（柱子碎了）、`SHATTER`（引爆易碎）、`ITEMS` / `FORGE` / `MASTERWORK`（活体锻炉）、
  连招（`Q FIRST`、`E PILLAR`、`BRITTLE`），都限了条数。

## 在游戏里测

1. 主包（League of Legends Heroes 0.185.0 以上）要装着并启用。
2. 用附加包合集 `league_addons`（里面已经包含本包），或者把整个 `league_ornn` 文件夹放进 `<游戏目录>\mods\`（文件夹里要有
   `league_ornn.dll`、`mod.mod_info`、`mod.override_info`、`override\`、`text\`）。
3. 进游戏，鼠标停在奥恩的技能上，说明开头是【扩展包】就说明副本生效了；打一局后看日志里的 PILLAR / CHARGE / SHATTER / FORGE 和连招。

## 重新生成

```
python addons/league_ornn/make_override.py
cd addons && cargo test -p league_ornn && cargo build --release -p league_ornn
```

## 游戏 0.6.5（0.1.1）

连招钩子回城时不出手（AI 的回城命令开始、别的命令结束，中间没命令的 tick 也算回城：`still_recalling`）；E 撞柱不朝 AI 正在远离的人撞（走路终点比现在离他远 10000 以上：`walking_away`），也不冲进敌方塔 75000 内的人。和 `league_ult_press` 0.5.0 同一套规则：0.6.5 的官方 AI 自己决定什么时候回城买装备、什么时候散开、越不越塔。
