<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 兰博 Rumble

<img src="img/league_rumble.png" alt="兰博" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_rumble` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 上单 |
| 分类 / 标签 | 近战（Melee） · AP / Magic / Melee / Shield |
| 高清帧 | PPU 1.75 |
| 附加包 | [兰博附加包](#附加包)（`league_rumble`） |

![兰博演示](../preview/league_rumble_showcase.gif)

其他预览：[skills](../preview/league_rumble_skills.gif)、[逐帧预览](../preview/league_rumble_frames.png)、[特效表](../preview/league_rumble_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_rumble.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.13 秒 · 攻击距离 25000*

抡铁球。机械重组：放技能攒热量，过半进入危险温度（技能效果+50%），满了过热5秒：不能放技能，攻速+60%，普攻附加20 + 25% 法强魔法伤害（英雄再加最大生命3%）。破碎护盾：敌方英雄靠近时自动套上60+45% 法强护盾1.5秒。

### 技能1 · 纵火盛宴

*冷却 1 秒 · 施放距离 45000 · 施放：指定目标 · 敌人（不含防御塔）*

端起喷火炮往前喷火1.5秒：锥形范围内的敌人每0.25秒受到30 + 27% 法强魔法伤害。

### 技能2 · 电子鱼叉

*冷却 1 秒 · 施放距离 55000 · 施放：指定目标 · 敌人（不含防御塔）*

射出电子鱼叉：70 + 50% 法强魔法伤害，减速20%2秒；射中英雄后再射第二发，伤害+25%，减速35%。

### 大招 · 恒温灼烧

*冷却 90 秒 · 施放距离 60000 · 施放：指定目标 · 敌方英雄*

火箭在敌方英雄脚下砸出一条火线（横着或竖着，挑罩住敌人多的一边），燃烧4秒：每0.5秒35 + 20% 法强魔法伤害，减速35%。

### 数值

攻击力 80（每级 +9）、法强 30（每级 +18）、生命 1200（每级 +115）、护甲 34（每级 +9）、魔抗 25（每级 +4）、移速 1050（每级 +11）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 兰博附加包

[兰博附加包](../../addons/league_rumble/README.md)：`league_rumble` v0.1.0

|  | 主包（纯数据） | 附加包 |
|---|---|---|
| 过热的样子 | 只有过热时的普攻是红温（`CasterAnimation` 播 `oh_attack`），站着、跑着、挨打、阵亡还是平常的样子 | **整身红温**：过热期间（`league_rumble_oh`）站、跑、挨打、阵亡都换成 `oh_idle` / `oh_run` / `oh_hit` / `oh_dead`，普攻第一 tick 换成 `oh_attack` |

## 相关脚本和素材

- [`tools/kit/build_rumble.py`](../../tools/kit/build_rumble.py)
- [`tools/kit/setup_rumble.py`](../../tools/kit/setup_rumble.py)
- [`tools/lol/extract_rumble.py`](../../tools/lol/extract_rumble.py)
- [`tools/art/preview_rumble.py`](../../tools/art/preview_rumble.py)
- [`tools/art/rig_rumble.py`](../../tools/art/rig_rumble.py)
- [`assets/source/rumble/`](../../assets/source/rumble)

## 开发记录

> 下面是原来 README 里「英雄：兰博」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 上单（Melee，标签 AP / Magic / Melee / Shield），第 169 位英雄（J 组第四位）。机械公敌 兰博：坐在自己焊出来的大机甲里的约德尔人，蓝色乱发、红色护目镜，黄铜色的机甲一手带刺铁球、一手喷火炮，背上火箭舱 |
| 普攻 / 被动 | 抡铁球（射程 25000，每 68 tick 一下，80 攻击 +9/级）。**机械重组**（热量）：Q、W 各攒 20 热量，鱼叉每发 10，最后一次攒热 4 秒后每 0.5 秒凉 10。热量过半进入**危险温度**：Q、E、W 效果 +50%，两边喷出蒸汽。满 100 **过热** 5 秒：放不了 Q、E、W（大招等到过热结束），攻速 +60%，普攻附加 20 + 25% 法强 魔法伤害（英雄再加最大生命 3% 真实伤害），整个机甲烧得通红。**破碎护盾**（W，并入被动）：冷却 7 秒，敌方英雄靠近 45000 内时自动套上 60 + 45% 法强 护盾 1.5 秒，移速 +20% 1 秒 |
| 技能1 | **纵火盛宴**（冷却 6 秒，射程 45000）：端起喷火炮往前喷火 1.5 秒，锥形（72000 长）里的敌人每 0.25 秒受到 30 + 27% 法强 魔法伤害（共 6 跳）。火画在他自己的帧里（特效图不会跟着单位翻转），喷火时站着不动 |
| 技能2 | **电子鱼叉**（冷却 8 秒，射程 55000）：射出鱼叉，打中第一个敌人 70 + 50% 法强 魔法伤害，减速 20% 2 秒 |
| 大招 | **恒温灼烧**（冷却 90 秒，射程 60000，对敌方英雄）：背上的火箭飞出去，在目标脚下砸出一条 84000 × 20000 的火线：先数横着和竖着两种放法各罩住几个敌方英雄，挑多的那边（一样多就横着放，用户：「R的大招会智能放吗 竖着放横着放 都要会」），燃烧 4 秒，每 0.5 秒 35 + 20% 法强 魔法伤害、减速 35% |
| 连招 | 「有连招要做连招」：**E → E2**：鱼叉打中英雄，0.5 秒后再射第二发（伤害 +25%、减速 35%，英雄联盟的第二发）；**E2 → Q**：第二发打中英雄时 Q 好了就立刻喷火；**R → E**：火箭落地时 E 冷却清零并立刻射向够得着的英雄；**危险温度 → W**：一进危险温度 W 冷却清零，敌方英雄在身边就马上套上加强的护盾；**过热 → 普攻带火** |
| 数值 | 攻击 80（+9）、法强 30（+18）、生命 1200（+115）、护甲 34（+9）、魔抗 25（+4）、移速 1050（+11）、射程 25000 |
| 平衡 | 经典引擎模拟（上路，对斗士、处刑人、骑士、狂战士、枪骑兵、长柄战士，两边三套阵容）：草稿（生命 1080、攻击 70 +5、法强 +14、Q 18 + 18%、E 50 + 40%、R 25 + 15%）−3.19；生命 1150、攻击 78、护甲 34、Q 26 + 24%、E 70 + 50%、R 35 + 20% −1.84；射程 25000 −1.96（不是射程的问题）；攻击 +9、法强 +18 每级 −0.77；生命 +115、护甲 +9 每级、Q 30 + 27% +0.43 / −0.22；定稿（上面的数值）+0.31（16 组种子） |
| 附加包 | `league_rumble`（在 `league_addons` 合集里，[`addons/league_rumble/README.md`](../../addons/league_rumble/README.md)）：用户「红温整套切换」——**整身红温**：过热期间站着、跑着、挨打、阵亡都换成红温的那一套（主包数据只能换普攻）。主包的数据不动 |
| 精灵图（高清帧 PPU 1.75） | 动作照本地英雄联盟客户端的动作帧摆骨架（[`tools/art/pack_rumble_poses.py`](../../tools/art/pack_rumble_poses.py)），Codex 画姿势，[`tools/art/design_rumble_poses.py`](../../tools/art/design_rumble_poses.py) 读回、贴回定稿的头，[`tools/art/rig_rumble.py`](../../tools/art/rig_rumble.py) 照英雄联盟的片段拼成待机、跑、普攻、Q（火烤进帧里）、E、R、受击、死亡；红温那一套（`oh_idle` / `oh_run` / `oh_attack` / `oh_hit` / `oh_dead`）是同样的帧把机甲换成通红的色阶，头和驾驶员的蓝色不变 |
| 特效 | 18 张特效（[`tools/art/pack_rumble_fx.py`](../../tools/art/pack_rumble_fx.py) 的提示词，参考是英雄联盟里兰博的贴图，[`tools/lol/fx_ref_rumble.py`](../../tools/lol/fx_ref_rumble.py)），Gemini 画回来，[`tools/art/process_rumble_fx.py`](../../tools/art/process_rumble_fx.py) 抠图缩到像素格，[`tools/art/fix_rumble_fx.py`](../../tools/art/fix_rumble_fx.py) 重画火箭落地、护盾、鱼叉、电流、打中和过热爆发，[`tools/art/import_rumble_fx.py`](../../tools/art/import_rumble_fx.py) 切成 `league_rumble_fx` / `league_rumble_big`：喷火、火烧中、鱼叉和第二发、电流减速、护盾和加速喷气、危险温度的蒸汽、过热的火和黑烟、火箭发射，火线横竖两张（六枚火箭依次落下，横着的从中间往两边、竖着的从远到近） |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_rumble.py`](../../tools/lol/extract_rumble.py)，19 段）：普攻的出手和打中、过热的打中，喷火和烧中，鱼叉、第二发和打中，护盾，危险温度的排气，过热，大招的发射、火线燃烧和烧中；配音：Q、R、过热，E 和 W 用他的两句攻击台词 |
| 图标 | 官方技能图标（纵火盛宴、电子鱼叉、恒温灼烧，另有机械重组、破碎护盾），从本地客户端取 |
| 选人卡片 | 脸 (4, −26)；不用 `banpick_center` 和 UI 缩放，整个机甲不出画布（`tools/art/bp_card_audit.py`）。待机按 `tools/art/hero_reels.py` 剪进大招的蹲身发射和端起喷火炮 |
| 俄洛伊的灵魂 | `tools/art/illaoi_souls.py` 加上兰博（169 个），`league_illaoi` 0.2.6 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_rumble.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_rumble.py                # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_rumble.py                # 五种语言的文字、音效配置、共享文件里他的键（脸 4,-26）
python tools/art/design_rumble_poses.py         # Codex 的姿势读回（贴回定稿的头）
python tools/art/process_rumble_fx.py           # Gemini 的特效图 -> 像素格
python tools/art/fix_rumble_fx.py               # 重画的特效
python tools/art/import_rumble_fx.py            # 特效 -> league_rumble_fx / league_rumble_big
python tools/art/rig_rumble.py                  # 1 倍帧和 1.75 的原帧（含红温一套）
python tools/art/ppu_restyle.py --hero rumble   # 外描边、脸的位置
python tools/art/ppu_hd.py --hero rumble        # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero rumble    # 待机和选人卡片的小动作
python tools/art/preview_rumble.py              # 预览、演示 GIF 和每个技能单独的 GIF
python tools/art/illaoi_souls.py                # 俄洛伊的灵魂（加了英雄或改了待机都要重跑），再跑 addons/league_illaoi/make_override.py
```
