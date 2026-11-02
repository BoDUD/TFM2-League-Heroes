<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 斯卡纳 Skarner

<img src="img/league_skarner.png" alt="斯卡纳" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_skarner` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 打野 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / Tank / CC |
| 高清帧 | PPU 1.75 |
| 附加包 | [斯卡纳附加包](#附加包)（`league_skarner`） |

![斯卡纳演示](../preview/league_skarner_showcase.gif)

其他预览：[skills](../preview/league_skarner_skills.gif)、[逐帧预览](../preview/league_skarner_frames.png)、[特效表](../preview/league_skarner_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_skarner.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.33 秒 · 攻击距离 25000*

毒刺扎击。战栗：普攻、巨石、毒刺打中英雄叠层，满3层4秒内每秒掉最大生命1%。震地壁垒：冲锋停下时得40 + 20% 攻击力护盾3秒，震伤周围20 + 30% 攻击力、减速30%。

### 技能1 · 撼地

*冷却 1 秒 · 施放距离 30000 · 施放：指定目标 · 敌人（不含防御塔）*

掘起巨石6秒，攻速+20%；3次普攻溅射10 + 20% 攻击力，第3次加最大生命3%、减速40%。举满3秒就扔出擎天：50 + 80% 攻击力+最大生命3%。

### 技能2 · 以绪塔尔冲击

*冷却 1 秒 · 施放距离 60000 · 施放：指定目标 · 敌方英雄*

冲向敌方英雄，撞上后拖着走，停下时造成60 + 80% 攻击力物理伤害并晕眩0.67秒。

### 大招 · 毒刺贯体

*冷却 80 秒 · 施放距离 50000 · 施放：指定目标 · 敌方英雄*

三根毒刺往前扎：直线上的敌方英雄受到60 + 50% 攻击力物理伤害，被压制0.75秒并拖到身边跟着走；扎中后移速+30%2.5秒。

### 数值

攻击力 76（每级 +12）、法强 10（每级 +5）、生命 1100（每级 +110）、护甲 32（每级 +9）、魔抗 30（每级 +4）、移速 1000（每级 +10）、生命回复 2（每级 +1）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 斯卡纳附加包

[斯卡纳附加包](../../addons/league_skarner/README.md)：`league_skarner` v0.1.1

| 机制 | 主包（纯数据） | 附加包 |
|---|---|---|
| 战栗 | 层数记在**斯卡纳自己身上**（换了目标也接着数），满 3 层让打中的英雄战栗：每秒最大生命 `p_pct`% 的**真实伤害** | 层数叠在**每个英雄身上**（按这个斯卡纳起名），满 `p_n` 层开始战栗：每 `p_p` 拍最大生命 `p_pct`% 的**魔法伤害**，战栗中不再叠层 |
| 以绪塔尔冲击 | 撞上英雄拖一段，**每次拖完都砸一下、晕** `e_stun` 拍 | 拖的路上**碰到墙才砸、才晕**（伤害 `e_wall_dmg` + `e_ratio`% 攻击力 + 最大生命 `e_wall_hp`%），没墙就只是拖走 |
| 毒刺贯体 | 尾巴扫过的线上**所有英雄**都中：物理伤害、压制（眩晕）`r_sup` 拍，每 3 拍往他身上拽一下 | 只压**最先碰到的 `r_n` 个英雄**：魔法伤害、压制 `r_sup` 拍，压制期间**每拍摆在他身边**（保持被打中时的方向，离他最多 `R_GAP`），他走到哪拖到哪 |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】毒刺扎击。战栗：普攻、巨石、毒刺在敌方英雄身上叠层，满3层它4秒内每秒受到最大生命1%魔法伤害。震地壁垒：冲锋停下时得40 + 20% 攻击力护盾3秒，震伤周围20 + 30% 攻击力、减速30%。
- **技能1 · 撼地**：【附加包】掘起巨石6秒，攻速+20%；3次普攻溅射10 + 20% 攻击力，第3次加最大生命3%、减速40%。举满3秒就扔出擎天：50 + 80% 攻击力+最大生命3%。
- **技能2 · 以绪塔尔冲击**：【附加包】冲锋时穿过地形，撞上敌方英雄后拖着走；拖到墙上才造成60 + 80% 攻击力+最大生命6%物理伤害并晕眩0.67秒。
- **大招 · 毒刺贯体**：【附加包】三根毒刺往前扎：最先碰到的3个敌方英雄受到60 + 50% 攻击力魔法伤害，被压制0.75秒并拖到身边跟着走；扎中后移速+30%2.5秒。

## 相关脚本和素材

- [`tools/kit/build_skarner.py`](../../tools/kit/build_skarner.py)
- [`tools/kit/setup_skarner.py`](../../tools/kit/setup_skarner.py)
- [`tools/lol/extract_skarner.py`](../../tools/lol/extract_skarner.py)
- [`tools/art/preview_skarner.py`](../../tools/art/preview_skarner.py)
- [`tools/art/rig_skarner.py`](../../tools/art/rig_skarner.py)
- [`assets/source/skarner/`](../../assets/source/skarner)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | 打野（Melee，标签 AD / Melee / Tank / CC），第 172 位英雄（J 组最后一位英雄联盟英雄）。上古领主 斯卡纳（2024 年重做后）：以绪塔尔的水晶蝎子，青绿甲壳上橙白花纹，身体最前面一张骨白骷髅小脸罩着银白头甲，两只大钳子，背上三根分节尾巴、末端三枚青绿水晶毒刺（橙色核心），六条钩爪腿 |
| 普攻 / 被动 | 毒刺扎击（射程 25000，每 80 tick 一下，76 攻击 +12/级）。**战栗**：普攻、巨石、毒刺贯体打中英雄叠一层（层数记在他身上），满 3 层被打中的英雄 4 秒内每秒受到最大生命 1% 的真实伤害。**震地壁垒**（并入被动）：以绪塔尔冲击拖人停下时，得 40 + 20% 攻击 的护盾 3 秒，跳起砸地，16000 内敌人受到 20 + 30% 攻击 物理伤害、减速 30% 1.5 秒 |
| 技能1 | **撼地 / 擎天**（冷却 7 秒，射程 30000）：从地里掘出巨石举在背上 6 秒，攻速 +20%；接下来 3 次普攻对目标和周围 9000 内的敌人造成 10 + 20% 攻击 物理伤害，第 3 次再加最大生命 3% 并减速 40% 1 秒；举满 3 秒还没打完就把巨石扔出去（擎天）：50 + 80% 攻击 + 最大生命 3%，减速。举着巨石时普攻换成钳子戳（英雄联盟的 BaseAttack1_Rock：尾巴一直托着石头） |
| 技能2 | **以绪塔尔冲击**（冷却 15 秒，射程 60000，对敌方英雄）：冲锋（穿过地形），撞上英雄夹住拖着走 20 tick，停下时 60 + 80% 攻击 物理伤害、晕眩 0.67 秒（主包里每次拖完都砸；撞墙才晕在附加包里） |
| 大招 | **毒刺贯体**（冷却 80 秒，射程 50000，对敌方英雄）：三根尾巴往前扎一条线（52000 长）：线上的敌方英雄受到 60 + 50% 攻击 物理伤害，被压制 0.75 秒，压制期间被拖到他身边、他走到哪拖到哪（模拟里确认过：2 tick 内拽到身边，之后跟着他走）；扎中后自己移速 +30% 2.5 秒 |
| 连招 | 「有连招要做连招」：**举着巨石放大招 → 先扔出擎天**（英雄联盟原版的规则）；**冲锋拖完人 → 撼地马上转好**（停下时 Q 冷却清零，马上举石接 3 下强化普攻）；**毒刺贯体 → 战栗直接叠满**：扎中的英雄立刻开始战栗；**巨石第 3 下（或擎天）打中英雄 → 以绪塔尔冲击最多再等 4 秒** |
| 数值 | 攻击 76（+12）、生命 1100（+110）、护甲 32（+9）、魔抗 30（+4）、移速 1000（+10）、射程 25000 |
| 平衡 | 经典引擎模拟（打野，对忍者、恶魔、猎人、狼人、吸血鬼，两边三套阵容；沃里克（附加包副本）同一批对局 +0.57）：草稿（生命 1150、攻击 80、战栗 2%、E 晕 1 秒、W 护盾 120 + 60%、Q 攻速 +50% 和 20 + 40% / 6%、R 压制 1.5 秒、120 + 100%）+4.99；单独削哪一项都只降 0.3–0.7（关掉 E +2.40），全部一起削 +0.31；**定稿**：这些削弱 + 生命 1100、攻击 76、E 晕 40 tick，+0.75（16 组种子）。附加包的规则在这个引擎里跑不了（原生效果被去掉） |
| 附加包 | `league_skarner`（在 `league_addons` 合集里，[`addons/league_skarner/README.md`](../../addons/league_skarner/README.md)）：用户「和英雄联盟不一样的地方要做附加包」——**战栗按每个英雄叠层**（层数记在被打中的英雄身上，满 3 层每秒最大生命 1% 的**魔法伤害**）；**以绪塔尔冲击撞墙才晕**（拖的路上碰到墙才砸：60 + 80% 攻击 + 最大生命 6%，晕 0.67 秒；没墙只拖走）；**毒刺贯体只压最先碰到的 3 个英雄**，魔法伤害，压制期间每拍被拽到他身边（每拍最多拽 3000，不是一下瞬移）、跟着他走 |
| 精灵图（高清帧 PPU 1.75） | Codex 第 0 步画了 A（待机）和 B（尾巴举着巨石）（[`tools/art/pack_skarner_picture.py`](../../tools/art/pack_skarner_picture.py)），[`tools/art/design_skarner_hd.py`](../../tools/art/design_skarner_hd.py) 按原图自己的格子读回（A 每格 8.7 px：80×59，B 每格 9.7 px：77×75）；用户定 A 原样、PPU 1.75（毒刺尖到脚底 33.7 游戏像素、46 宽，[`tools/art/design_skarner_model.py`](../../tools/art/design_skarner_model.py) 只把远处的眼睛补成 2×1），B 是举石的样子。姿势包照英雄联盟原版的帧摆骨架（[`tools/art/pack_skarner_poses.py`](../../tools/art/pack_skarner_poses.py)：身体、三根尾巴、两只钳子、六条腿，每一节都是定稿的长短；英雄联盟骨骼的二维投影透视太强，没法直接套，所以照原版的帧手摆），Codex 画 18 个姿势；[`tools/art/design_skarner_poses.py`](../../tools/art/design_skarner_poses.py) 读回（Codex 画的头比身体小一圈：按身体对齐待机的轮廓，每张放大 1.1–1.25 倍读回到定稿的格子上），贴回定稿的头，补掉段与段之间透出地面的小洞；[`tools/art/rig_skarner.py`](../../tools/art/rig_skarner.py) 拼成待机、跑、普攻、举石普攻（`attack_rock`：远侧钳子先收后戳，尾巴不动）、掘石（`skill`）、扔石（`skill_toss`）、冲锋（`skill2`）、夹住（`grab`，撞上那一刻才播）、跳起砸地（`w`）、大招、受击、阵亡 |
| 特效 | 18 张（[`tools/art/pack_skarner_fx.py`](../../tools/art/pack_skarner_fx.py) 的提示词，参考是英雄联盟里斯卡纳自己的贴图，[`tools/lol/fx_ref_skarner.py`](../../tools/lol/fx_ref_skarner.py)），用户用 Gemini 画的（「gemini做的啊 你处理一下不就行了吗」）：[`tools/art/clean_skarner_fx.py`](../../tools/art/clean_skarner_fx.py) 去背景、去柔光、颜色收进四套色板（水晶、橙核心、沙尘、灰绿石头）、左右（弹道上下）对称、补被格子切坏的尘土，毒刺贯体的弹道用 Gemini 的毒刺重新拼成一前两后的箭头；[`tools/art/import_skarner_fx.py`](../../tools/art/import_skarner_fx.py) 切成 `league_skarner_fx` / `league_skarner_big`。举着的巨石是 buff（`league_skarner_rock_v`，掘石动作播完才挂上）的画面 `q_held`，在他背上跟着他走 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_skarner.py`](../../tools/lol/extract_skarner.py)，16 段）：普攻的出手和打中，掘石、巨石打中、扔石、石头落地，震地壁垒，冲锋、夹住、砸停，大招的出手和扎中，战栗；配音：Q、E（晕眩）、R |
| 图标 | 官方技能图标（撼地、以绪塔尔冲击、毒刺贯体，另有震地壁垒、战栗），从本地客户端取 |
| 选人卡片 | 毒刺尖到脚底 34 游戏像素、46 宽：卡片里放得下，不要 UI_SIZES 和 `banpick_center`（和拉莫斯、雷克塞一样，`tools/art/bp_card_audit.py`）。脸 (8, −14)：他的脸在身体最前面、很低，在头甲顶上（`tfm2_ase.py face` 会把尾巴尖当成头顶）。待机按 `tools/art/hero_reels.py` 剪进钳子戳和普攻各一小段 |
| 俄洛伊的灵魂 | `tools/art/illaoi_souls.py` 加上斯卡纳（172 个），`league_illaoi` 0.2.11 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_skarner.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_skarner.py                # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_skarner.py                # 五种语言的文字、音效配置、共享文件里他的键（脸 8,-14）
python tools/art/design_skarner_hd.py            # Codex 第 0 步的原图读回（A / B）
python tools/art/design_skarner_model.py         # 定稿 A 原样（远处的眼睛补成 2×1），B 是举石的样子
python tools/art/design_skarner_poses.py         # Codex 的姿势读回（按身体的大小，贴回定稿的头）
python tools/art/clean_skarner_fx.py             # Gemini 的特效清理成游戏大小
python tools/art/import_skarner_fx.py            # 特效 -> league_skarner_fx / league_skarner_big
python tools/art/rig_skarner.py                  # 1 倍帧和 1.75 的原帧
python tools/art/ppu_restyle.py --hero skarner   # 外描边（补描边围出来的小洞）
python tools/art/ppu_hd.py --hero skarner        # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero skarner    # 待机和选人卡片的小动作
python tools/art/preview_skarner.py              # 预览和每个技能单独的 GIF
python tools/art/review_skarner_actions.py --out <文件夹> --sheet   # 和英雄联盟原版逐个动作对照的 GIF
python tools/art/illaoi_souls.py                 # 俄洛伊的灵魂（加了英雄或改了待机都要重跑），再跑 addons/league_illaoi/make_override.py
python addons/league_skarner/make_override.py    # 附加包的斯卡纳副本（主包的斯卡纳改了以后要重跑）
```
