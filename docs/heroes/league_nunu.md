<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 努努和威朗普 Nunu & Willump

<img src="img/league_nunu.png" alt="努努和威朗普" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_nunu` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 打野 |
| 分类 / 标签 | 近战（Melee） · AP / Magic / Melee / Tank / CC |
| 高清帧 | PPU 1.37 |
| 附加包 | 无 |

![努努和威朗普演示](../preview/league_nunu_showcase.gif)

其他预览：[逐帧预览](../preview/league_nunu_frames.png)、[特效表](../preview/league_nunu_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_nunu.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.17 秒 · 攻击距离 25000*

爪击。每第3次普攻是吞噬：额外50 + 50% 法强魔法伤害（小兵野怪再受120真实伤害），回复25 + 25% 法强生命；随后4秒内自己和一名队友攻速+30%、移速+15%，普攻溅射周围20%。

### 技能1 · 史上最大雪球！

*冷却 12 秒 · 施放距离 70000 · 施放：指定目标 · 敌人（不含防御塔）*

推着雪球冲向目标，撞上造成55 + 42% 法强魔法伤害并击飞0.5秒；滚得越久越大，最多170%伤害、击飞1秒。

### 技能2 · 雪球飞射

*冷却 1 秒 · 施放距离 60000 · 施放：指定目标 · 敌人（不含防御塔）*

连扔6个雪球，每个11 + 7% 法强魔法伤害并减速30%；扔完禁锢被打中的英雄0.75秒，造成25 + 30% 法强魔法伤害。

### 大招 · 绝对零度

*冷却 60 秒 · 施放距离 60000 · 施放：指定目标 · 敌方英雄*

引导暴风雪2.5秒，获得护盾120 + 80% 法强，周围敌人减速40%到80%；结束时爆发造成190 + 105% 法强魔法伤害（被打断按已引导的时间计算）。

### 数值

攻击力 72（每级 +6）、法强 30（每级 +15）、生命 1150（每级 +120）、护甲 40（每级 +10）、魔抗 30（每级 +5）、移速 1000（每级 +11）。

## 相关脚本和素材

- [`tools/kit/build_nunu.py`](../../tools/kit/build_nunu.py)
- [`tools/kit/setup_nunu.py`](../../tools/kit/setup_nunu.py)
- [`tools/lol/extract_nunu.py`](../../tools/lol/extract_nunu.py)
- [`tools/art/preview_nunu.py`](../../tools/art/preview_nunu.py)
- [`tools/art/rig_nunu.py`](../../tools/art/rig_nunu.py)
- [`assets/source/nunu/`](../../assets/source/nunu)

## 开发记录

> 下面是原来 README 里「英雄：努努和威朗普」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 打野（Melee，标签 AP / Magic / Melee / Tank / CC），第 158 位英雄（H 组第二位）。雪原双子 努努和威朗普：一个大雪人骑着一个小男孩——威朗普又大又圆，淡蓝色的毛、头顶胸口前臂是白色长毛、蓝色螺旋纹，两只发蓝光的眼睛、棕鼻头、咧嘴笑露出白牙和两颗小獠牙，深蓝爪子和短腿、蓬松的尾巴，头上一对棕色大木头鹿角；努努骑在他头上扶着鹿角，蓝色毛兜帽带粉猫耳和米白毛球，橙斗篷白毛边、蓝宝石扣。技能方案 A（用户选）：史上最大雪球！ / 雪球飞射 / 绝对零度，吞噬（Q）并进被动 |
| 普攻 / 被动 | 威朗普爪击（射程 25000，100% 攻击）。**吞噬**（并进被动）：每第 3 次普攻是一口咬下去：100% 攻击 + 50 + 50% 法强 魔法伤害，回复 25 + 25% 法强 生命；小兵和野怪再受 120 真实伤害（英雄联盟的吞噬对小兵野怪伤害高得多；英雄身上一个只对英雄的影子弹挂 2 tick 标记跳过这一段）。**弗雷尔卓德的召唤**：咬完 4 秒内他们和附近一名队友攻速 +30%、移速 +15%，普攻溅射周围 30000 内的敌人 20% 攻击 |
| 技能1 | **史上最大雪球！**（冷却 12 秒，对 `EnemyWithoutTower`、射程 70000：兵线野怪也放）：威朗普搓起雪球（0.3 秒），推着它滚向目标（`MoveToTarget`，最多滚 1.5 秒），撞上时半径 18000 内 55 + 42% 法强 魔法伤害、击飞 0.5 秒；滚得越久越大：滚过 20 tick 伤害 140%、半径 26000，滚过 40 tick 伤害 170%、击飞 1 秒。英雄联盟的雪球最多滚 10 秒、玩家掌方向；数据掌不了方向，雪球直着滚向目标 |
| 技能2 | **雪球飞射**（冷却 11 秒，射程 60000，对 `EnemyWithoutTower`）：努努 0.1 秒一个连扔 6 个雪球（每个打附近随机一个敌人），每个 11 + 7% 法强 魔法伤害、减速 30% 1 秒；打中的英雄头上挂雪花记号，出手 1.1 秒后被冻住 0.75 秒，再受 25 + 30% 法强 魔法伤害（英雄联盟扔完禁锢被打中的英雄和大型野怪） |
| 大招 | **绝对零度**（冷却 60 秒，射程 60000，对敌方英雄）：原地引导 2.5 秒暴风雪，罩上 120 + 80% 法强 的护盾；每 0.25 秒周围 55000 内的敌人减速，从 40% 涨到 80%；结束时暴风雪炸开，190 + 105% 法强 魔法伤害。被控制会在下一拍打断，打断时按已引导的比例爆发（英雄联盟的伤害按引导时间涨） |
| 连招 | 「有连招要做连招」：**W → E**：雪球撞上时雪球飞射就绪就马上扔；**E → R**：冻住英雄后 2 秒内放绝对零度，引导缩短到 1.67 秒、伤害照满（英雄联盟里被禁锢的人跑不出暴风雪）；**R → 吞噬**：暴风雪炸开后，威朗普马上咬身边一个敌方英雄，普攻计数重新算 |
| 数值 | 攻击 72（+6）、法强 30（+15）、生命 1150（+120）、护甲 40（+10）、魔抗 30（+5）、移速 1000（+11）、射程 25000 |
| 平衡 | 经典引擎模拟（打野，对恶魔、马戏团刀手、猎人、审判官、忍者，两边三套阵容）：草稿的普攻所有伤害都在存活检查后面，AI 读到 0 伤害、64 / 240 局除零崩溃（俄洛伊之前普朗克同样的坑），给普攻和 W 加了让 AI 读伤害的诱饵节点；雪球没碰到目标时动作卡 10 秒，滚动最多 1.5 秒；之后 +5.75（咬一口回血 50 + 50%、溅射 40%），减半回血和溅射、W 50 + 40%、E 10 + 6% × 6、R 180 + 100% +0.27，取中间：+2.14 / +2.11（种子 1-8 / 9-16；同一天拉莫斯 +1.90） |
| 附加包 | 没有（主包的数据就够）。佛耶戈 / 妮蔻的灵魂表、塞拉斯的职业表和可偷大招、凯隐的攻击距离、大招按键的距离表都加上了努努和威朗普 |
| 精灵图（高清帧 PPU 1.37） | Codex 第 0 步画了 A（四分之三侧面）和 SA（[`tools/art/pack_nunu_picture.py`](../../tools/art/pack_nunu_picture.py)；英雄联盟模型要藏掉 snowman / claws_long / teeth_big / teeth_smile 几个分网格、威朗普用他自己的贴图，不然整个模型套努努的贴图）。Codex 画得比要的细（约 4.5 像素一格），[`tools/art/design_nunu_hd.py`](../../tools/art/design_nunu_hd.py) 缩到 105 行给用户定大小；用户「努努毛球顶到脚底 46 游戏像素，PPU 1.5，只做四分之三侧面」。第 1 步两稿（[`tools/art/design_nunu_model.py`](../../tools/art/design_nunu_model.py)），A-2 画得粗、只有 63 行，用户「努努用 A-2，PPU 1.37（46 游戏像素）」：51 × 63。动作：用户「Codex 照骨架画姿势」，[`tools/art/pack_nunu_poses.py`](../../tools/art/pack_nunu_poses.py) 按英雄联盟的片段画了 18 个威朗普的骨架（头框是威朗普的头连鹿角、骑在上面的努努，雪球是道具圆盘）；[`tools/art/design_nunu_poses.py`](../../tools/art/design_nunu_poses.py) 按努努的头读回、贴回定稿的努努头（歪着的头先擦掉再贴正的），Codex 在不同姿势里把威朗普画得忽大忽小，按他的脸、毛的面积和成对的帧逐张定比例。[`tools/art/rig_nunu.py`](../../tools/art/rig_nunu.py) 照英雄联盟的动作拼：普攻（抬爪、拍下）、吞噬（张大嘴扑、咬住）、史上最大雪球（搓雪球、推着滚——两张推雪球的姿势雪球离身体差 10 格，滚动只用一张、上下颠一格，雪球就不会来回跳——撞上张开手臂）、雪球飞射（努努左右手轮流扔）、绝对零度（举手召唤、砸地爆发）、跑步四帧、死亡（往前扑倒、趴在地上，努努坐在他头前） |
| 特效 | 20 张特效（[`tools/art/pack_nunu_fx.py`](../../tools/art/pack_nunu_fx.py) 的提示词，参考是英雄联盟里努努自己的贴图），用户交给 Gemini 画回来（一张带标签的图集 + 六条长图），[`tools/art/process_nunu_fx.py`](../../tools/art/process_nunu_fx.py) 按图块切图集、按空隙切长图（帧不是等距排的）、抠背景、做对称，咬一口的上下两排尖牙是画出来的（Gemini 画了侧面的雪人头，一镜像就糊）；w_burst 第一次画在雪地背景上抠不出来，用户让 Gemini 重画了一张；[`tools/art/import_nunu_fx.py`](../../tools/art/import_nunu_fx.py) 切成 `league_nunu_fx` / `league_nunu_big`：爪痕和雪粉、溅射、咬一口、脚下的寒风（自己和队友）、雪球扬起的雪尘、撞中、小雪球和大雪球撞碎、飞出去的小雪球和它的雪花、脚下的积雪、头上的雪花记号、冒出的冰柱和腿上的冰块、暴风雪冰圈、冰壳、结霜、整圈爆开 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_nunu.py`](../../tools/lol/extract_nunu.py)）：爪击和命中，咬一口和吞下，雪球的出手和爆开，雪球飞射的出手、扔出、冰冻，绝对零度的出手和爆发，四句台词 |
| 图标 | 官方技能图标（史上最大雪球！、雪球飞射、绝对零度，另有吞噬、弗雷尔卓德的召唤），从本地客户端取 |
| 选人卡片 | 毛球到脚底 46 游戏像素，卡片画布只装得下约 40：`league.dll` 的 UI_SIZES 画成 0.85、`banpick_center` −7（`tools/art/bp_card_audit.py`：毛球在画布里，脚踩在下沿）。待机按 `tools/art/hero_reels.py` 剪：扔雪球两帧、抬爪；选人卡片轮流放史上最大雪球、雪球飞射、绝对零度、普攻 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_nunu.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_nunu.py                       # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_nunu.py --face 3,-36          # 五种语言的文字、音效配置、共享文件里他们的键（脸 3,-36）
python tools/art/design_nunu_hd.py                   # Codex 第 0 步的原图读回（A、SA）
python tools/art/design_nunu_model.py                # Codex 第 1 步的造型读回（A-2，PPU 1.37）
python tools/art/design_nunu_poses.py                # Codex 的姿势读回（贴回定稿的努努头）
python tools/art/process_nunu_fx.py --src <放 Gemini 原图 g00.jpg–g07.png 的文件夹>
python tools/art/import_nunu_fx.py                   # 特效 -> league_nunu_fx / league_nunu_big
python tools/art/rig_nunu.py                         # 1 倍帧和 1.37 的原帧
python tools/art/ppu_restyle.py --hero nunu          # 外描边、脸的位置
python tools/art/ppu_hd.py --hero nunu               # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero nunu           # 待机和选人卡片的小动作
python tools/art/preview_nunu.py                     # 预览和演示 GIF
```
