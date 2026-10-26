<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 拉露恩 Alune

<img src="img/tft_alune.png" alt="拉露恩" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_alune` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / Range / CC |
| 高清帧 | PPU 2 |
| 附加包 | [拉露恩附加包](#附加包)（`tft_alune`） |

其他预览：[skills](../preview/tft_alune_skills.gif)、[逐帧预览](../preview/tft_alune_frames.png)、[特效表](../preview/tft_alune_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_alune.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.5 秒 · 攻击距离 55000*

把螺旋月环像飞盘一样甩出去，造成100% 攻击力物理伤害。月相：每放一次技能月亮长一档，最多3档；大招每档伤害+20%，砸完回到新月。

### 技能1 · 月之降临

*冷却 4.25 秒 · 施放距离 70000 · 施放：指定目标 · 敌人（不含防御塔）*

月光碎片从天而降，落在3个敌人身上（一个是目标），每枚造成42 + 32% 法强魔法伤害，并使魔抗降低20%，持续6秒。

### 技能2 · 月华

*冷却 10 秒 · 施放距离 60000 · 施放：指定目标 · 敌方英雄*

月光洒在她和身边的友方英雄身上，攻击速度提高36%，持续5秒。

### 大招 · 月曜降临

*冷却 50 秒 · 施放距离 75000 · 施放：指定目标 · 敌方英雄*

敌方英雄脚下浮现月影，0.75秒后满月砸下：范围内的敌人受到165 + 72% 法强魔法伤害，中心的敌人眩晕0.83秒。

### 数值

攻击力 74（每级 +6）、法强 40（每级 +20）、生命 880（每级 +98）、护甲 18（每级 +7）、魔抗 22（每级 +4）、移速 900（每级 +9）。

## 附加包

附加包是可选的原生代码 mod（tft 包的附加包单独安装，不在附加包合集 `league_addons` 里），**不装 tft 包里的英雄也是完整的**。

### 拉露恩附加包

[拉露恩附加包](../../addons/tft_alune/README.md)：`tft_alune` v0.1.0

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 月之降临 | 一枚碎片落在目标身上，其余落在射程里**随机**的敌人身上 | 落在离她**最近**的 `q_n` 个敌人身上（金铲铲的规则），每枚 `q_dmg` + `q_ratio`% 法强、月蚀印记（魔抗 -`q_shred`%） |
| 月曜降临 | 范围里每个敌人都挨满额的伤害 | 整颗月亮的伤害（含月相加成）× `r_split`% 由**命中的敌人平分**，每人最多 `r_cap`%：只砸中一个人时最痛 |
| 普攻 | 月环飞出去打中就没了 | 月环**飞回来**，穿过路上的每个敌人（`a_back_r`% 攻击力），打中的那个人回来时再挨一下 |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】甩出螺旋月环造成100% 攻击力物理伤害，月环飞回她手里，回程路上的敌人受到30% 攻击力物理伤害。月相：每放一次技能月亮长一档（最多3档），大招每档+20%。
- **技能1 · 月之降临**：【附加包】月光碎片落在离她最近的3个敌人身上，每枚造成42 + 32% 法强魔法伤害，并使魔抗降低20%，持续6秒。
- **技能2 · 月华**：【附加包】月光洒在她和身边的友方英雄身上，攻击速度提高36%，持续5秒。
- **大招 · 月曜降临**：【附加包】满月砸在敌方英雄身上，165 + 72% 法强魔法伤害（每档月相+20%）由范围内的敌人分摊，只砸中一个人时为180%；中心的敌人眩晕0.83秒。

## 相关脚本和素材

- [`tools/kit/build_alune.py`](../../tools/kit/build_alune.py)
- [`tools/kit/setup_alune.py`](../../tools/kit/setup_alune.py)
- [`tools/lol/extract_alune.py`](../../tools/lol/extract_alune.py)
- [`tools/art/preview_alune.py`](../../tools/art/preview_alune.py)
- [`tools/art/rig_alune.py`](../../tools/art/rig_alune.py)
- [`assets/source/alune/`](../../assets/source/alune)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_alune`）的第三个英雄，中单（Magician，标签 AP / Magic / Range / CC；分组计划里排的是下路替补，用户改成中路）。厄斐琉斯的妹妹、月之教派的女祭司，金铲铲之战第 18 赛季的五费棋子（月华神女 / 月蚀骑士 / 法师）。金铲铲里她只有一个技能「月之降临」（月光碎片落在最近的几个敌人身上，满月时整颗月亮砸下来、由所有敌人分摊），所以三个技能和被动都是自己设计的，用户从三套方案里选了 A「月相」。她坐在一把青铜月牙法杖上漂浮，金铲铲第 18 赛季的模型只在 Riot 客户端的 `TFTSet18.wad.client` 里（WeGame 客户端只到第 17 赛季），三星的满月在对局视频里确认过（YouTube UcztPIRD1m0，53–60 秒） |
| 普攻 / 被动 | 把螺旋月环像飞盘一样甩出去（射程 55000，100% 攻击）。**月相**：每放一次技能（Q 或 E）月亮长一档（新月 → 上弦 → 满月，头顶有一轮小月亮），大招每档伤害 +20%，砸完回到新月 |
| 技能1 | **月之降临**（冷却 4.25 秒，射程 70000）：三枚月光碎片从天而降，一枚落在目标身上、其余落在射程里随机的敌人身上（数据没有「最近」），每枚 42 + 32% 法强魔法伤害，魔抗 −20% 持续 6 秒 |
| 技能2 | **月华**（冷却 10 秒，只在打英雄时放）：她和身边的友方英雄攻速 +36%，持续 5 秒（金铲铲里她的攻速加成） |
| 大招 | **月曜降临**（冷却 50 秒，射程 75000，对敌方英雄）：敌方英雄脚下浮现月影，0.75 秒后满月砸下，范围内敌人 165 + 72% 法强魔法伤害（每档月相 +20%），中心 22000 内的眩晕 0.83 秒 |
| 数值 | 攻击 74（+6）、法强 40（+20）、生命 880（+98）、护甲 18（+7）、魔抗 22（+4）、移速 900（+9） |
| 平衡 | 经典引擎模拟（中单，对火法、冰法、雷法、风法、白魔法师，两边三套阵容；同一批对局 league_ziggs +1.38 / +2.22，诺拉 +1.43 / +2.32）：草稿（Q 30 + 22%、R 130 + 55%、E +30%）−2.60；Q 40 + 30%、R 160 + 70% +0.44；Q 45 + 34% 每 240、R 170 + 75%、E +40% +1.98；Q 42 + 32% 每 255、R 165 + 72%、E +36%（**定稿**）+1.20 / +1.19（种子 1–8 / 9–16）。附加包的规则在这个引擎里跑不了 |
| 附加包 | `tft_alune`（单独安装，不在 `league_addons` 合集里，要 tft 0.2.0 起，[`addons/tft_alune/README.md`](../../addons/tft_alune/README.md)）：用户「要做附加包的地方你就做附加包」——**碎片落在离她最近的 3 个敌人身上**（金铲铲的规则）；**满月的伤害由命中的敌人分摊**（整颗 × 220% 平分，每人最多 180%：只砸中一个人时最痛）；**月环打中后飞回来**，回程路上的敌人受到 30% 攻击力物理伤害 |
| 精灵图（高清帧 PPU 2.0） | 模型从 Riot 客户端读（[`tools/art/pack_alune_picture.py`](../../tools/art/pack_alune_picture.py)：武器和裙摆用第 11 赛季的贴图，九段动作只有路径哈希，按内容命名）。Codex 第 0 步画了 A（骑在月牙上）和 B（站着拿法杖），[`tools/art/design_alune_hd.py`](../../tools/art/design_alune_hd.py) 按原图自己约 8 px 的格子读回（A-1 88×134、B-1 70×102；16 px 读回糊了不用）；用户定 **A-1、高 46、PPU 2.0**（[`tools/art/design_alune_model.py`](../../tools/art/design_alune_model.py)：60×90，去掉大角尖上一条没填色的描边）。姿势包的骨架是她自己的动作按帧投影出来的（[`tools/art/pack_alune_poses.py`](../../tools/art/pack_alune_poses.py)：Q 版大头，坐着的片段从 305° 看，站着的从 35° 看），Codex 画 14 个姿势；[`tools/art/design_alune_poses.py`](../../tools/art/design_alune_poses.py) 读原稿（Codex 自己切格的成品糊），按头找比例，站着的身体 Codex 画大了 24–33%、缩回骨架大小，贴回定稿的头（后仰的两张歪了 10° 也贴正头，躺倒那张把定稿的头转 90°），举环那张头上补 3 行空间让手和月环回到头顶；[`tools/art/rig_alune.py`](../../tools/art/rig_alune.py) 拼成待机（定稿）、移动（定稿整体轻轻上下浮：Codex 的四帧滑行每帧把月牙重画了一遍，播起来会闪）、普攻（平端月牙杖 → 甩出月环 → 接回）、技能1（月环竖在身侧 → 举拳）、技能2（坐着扬手：腰以下和月牙用定稿，和待机切换时一格不变）、大招（月环举过头顶 → 指天）、受击、阵亡。站着的动作都在地上，头比坐着的待机低一截（金铲铲里她也是从月牙上下来站着出手） |
| 特效 | 10 张 + 3 个技能图标，Codex 画的（[`tools/art/pack_alune_fx.py`](../../tools/art/pack_alune_fx.py) 的提示词，参考是金铲铲里她自己的粒子贴图 [`tools/lol/fx_ref_alune.py`](../../tools/lol/fx_ref_alune.py) 和满月的视频截图），[`tools/art/import_alune_fx.py`](../../tools/art/import_alune_fx.py) 切成 `tft_alune_fx` / `tft_alune_big`。满月分成两段：出手时就在目标头上开始往下压（`r_fall`，750 毫秒，在人物上面一层），落地那一刻炸开（`r_moon`，和伤害同一 tick）；地上的月影 `r_warn` 在人物下面一层 |
| 音效 | 她自己的第 11 赛季金铲铲音效（Riot 客户端 Map22 的 `MODE_TFT_Set11_Champs_SFX`：普攻出手 / 命中、施法、碎片砸地；第 18 赛季的事件找不到音效包），大招喊的是 WeGame 客户端里她的中文配音；月华和满月砸地借用黛安娜的苍白之瀑和月落（[`tools/lol/extract_alune.py`](../../tools/lol/extract_alune.py)，9 段） |
| 选人卡片 | 角到月牙底 46 游戏像素：UI_SIZES 0.85、`banpick_center` −10（角在卡片顶下面 1 像素，月牙底贴着下沿）。脸 (2, −37)。待机按 `tools/art/hero_reels.py` 剪进月华扬手那一帧，卡片轮播月华、普攻、技能1、大招 |

重新生成（素材来自本机的金铲铲 / 英雄联盟客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_alune.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_alune.py                 # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_alune.py                 # 五种语言的文字、音效配置、tft 包共享文件里她的键
python tools/art/design_alune_hd.py             # Codex 第 0 步的原图读回（A-1 / A-2 / B-1 / B-2）
python tools/art/design_alune_model.py          # 定稿 A-1 缩到 90 行
python tools/art/design_alune_poses.py          # Codex 的姿势读回（按头的格子，身体缩回骨架大小，贴回定稿的头）
python tools/art/import_alune_fx.py             # 特效 -> tft_alune_fx / tft_alune_big，图标
python tools/art/rig_alune.py                   # 1 倍帧和 2.0 的原帧
python tools/art/ppu_restyle.py --hero alune    # 外描边
python tools/art/ppu_hd.py --hero alune         # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero tft_alune # 待机和选人卡片的小动作
python tools/art/preview_alune.py               # 预览和每个技能单独的 GIF
python tools/art/review_alune_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
python addons/tft_alune/make_override.py        # 附加包的拉露恩副本和文字（tft 包的拉露恩改了以后要重跑）
```
