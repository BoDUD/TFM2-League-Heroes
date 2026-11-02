<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 小木灵 Meepsie

<img src="img/tft_meepsie.png" alt="小木灵" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_meepsie` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 辅助 |
| 分类 / 标签 | 功能型（Util） · AP / Magic / Melee / Tank / Heal / CC |
| 高清帧 | PPU 2.88 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_meepsie_skills.gif)、[逐帧预览](../preview/tft_meepsie_frames.png)、[特效表](../preview/tft_meepsie_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_meepsie.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.5 秒 · 攻击距离 25000*

挥出月岩重拳，造成100% 攻击力物理伤害。木灵驾驶员：每一拳额外造成15 + 25% 法强魔法伤害。

### 技能1 · 月尘震地

*冷却 6 秒 · 施放距离 30000 · 施放：指定目标 · 敌人（不含防御塔）*

一拳砸向前方地面，扇形范围内的敌人受到100 + 70% 法强魔法伤害并减速40%（2秒）。

### 技能2 · 治疗木灵

*冷却 9 秒 · 施放距离 60000 · 施放：无目标 · 敌方英雄*

驾驶员一招手，4只小木灵飞向身边生命比例最低的队友（名额有剩时也治疗自己），每0.5秒回复20 + 10% 法强生命，持续3秒。

### 大招 · 宇宙大爆炸

*冷却 35 秒 · 施放距离 45000 · 施放：指定目标 · 敌方英雄*

跳向附近敌方英雄最多的地方砸地，周围的敌人受到160 + 90% 法强魔法伤害，离中心每远一格少35%；离落点最近的3个敌方英雄被击飞1.25秒。

### 数值

攻击力 66（每级 +6）、法强 30（每级 +15）、生命 1250（每级 +118）、护甲 44（每级 +8）、魔抗 40（每级 +6）、移速 940（每级 +10）。

## 相关脚本和素材

- [`tools/kit/build_meepsie.py`](../../tools/kit/build_meepsie.py)
- [`tools/kit/setup_meepsie.py`](../../tools/kit/setup_meepsie.py)
- [`tools/lol/extract_meepsie.py`](../../tools/lol/extract_meepsie.py)
- [`tools/art/preview_meepsie.py`](../../tools/art/preview_meepsie.py)
- [`tools/art/rig_meepsie.py`](../../tools/art/rig_meepsie.py)
- [`assets/source/meepsie/`](../../assets/source/meepsie)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_meepsie`）的英雄，辅助（近战，魔法伤害，治疗，肉）。金铲铲第 17 赛季的二费 `TFT17_IvernMinion`「小木灵」（木灵族 / 牧羊人 / 旅人，繁中「小米普」，英文 Meepsie，射程 1）：没有脑袋的浅蓝白月岩巨像，身上是带陨石坑的大石块和两只巨拳，靛蓝短腿、紫色腰带，头顶和背上长着绿叶和紫蘑菇，胸口的陨石坑驾驶舱里坐着一只绿色小木灵。用户把「米普西」定名为官方的「小木灵」。金铲铲原技能「宇宙大爆炸」做大招，被动「攻击附带魔法伤害」做「木灵驾驶员」，其余按用户选的方案 A「木灵守护」（2026-11-01，辅助）自己设计 |
| 普攻 / 被动 | **月岩重拳**（距离 25000，打塔）：第 15 tick 砸下，100% 攻击力物理伤害。**木灵驾驶员**：每一拳额外 15 + 25% 法强的魔法伤害（数据，跟着普攻的命中） |
| 技能1 | **月尘震地**（冷却 6 秒，距离 30000，打兵和野怪）：第 18 tick 一拳砸向前方地面，前方扇形（半径 65000、点积 0.7）里的敌人受 100 + 70% 法强魔法伤害、减速 40% 两秒；月尘震波是一条只有画面的线（长 94000，画面的左端在拳头砸地处） |
| 技能2 | **治疗木灵**（冷却 9 秒，距离 60000，只在打架时放）：第 14 tick 驾驶员一招手，4 只小木灵飞向 60000 以内**生命比例最低**的友方英雄（先别人，名额有剩才给自己；tft.dll 的追踪弹道，速度 2500，被拒时直接治疗），每只 3 秒里每 0.5 秒回复 20 + 10% 法强 |
| 大招 | **宇宙大爆炸**（金铲铲原技能，冷却 35 秒，距离 45000，有敌方英雄时）：在 45000 以内找**周围 45000 内敌方英雄最多**的落点（候选：每个敌方英雄脚下、每两人的中点；一样多取离目标近的），30 tick 跳过去砸地：45000 以内每个敌人受 160 + 90% 法强魔法伤害，离落点每远 15000（一格）少 35%；离落点最近的 3 个敌方英雄被击飞 1.25 秒 |
| 数值 | 攻击 66（+6）、法强 30（+15）、生命 1250（+118）、护甲 44（+8）、魔抗 40（+6）、移速 940（+10），攻击间隔 90 tick，距离 25000 |
| 平衡 | 经典引擎模拟（辅助位，对原版牧师、武僧、吟游诗人、附魔师、道士，两边三套阵容，纯数据版：小木灵治疗范围内所有人、砸地全额伤害并击飞所有英雄、跳向目标）：初稿 +0.87（±0.49）；Q 100、大招 35 秒 **+1.00 / +1.12**（种子 1–8 / 9–16）；艾达丝同条件 +1.23 / +1.20：和包里的辅助持平 |
| tft.dll | [`addons/tft/src/meepsie.rs`](../../addons/tft/src/meepsie.rs)：被动 `tft_meepsie:pilot`（参数、倒地的声音）；原生效果 `tft_meepsie:meeps`（挑人、放追踪的小木灵）、`tft_meepsie:mend` / `mend_tick`（持续治疗）、`tft_meepsie:bigbang`（选落点、开始跳）、`tft_meepsie:hop`（一拍一拍挪、落地砸地、递减伤害、击飞最近的人）。日志 `data/tft_meepsie.log` |
| 塞拉斯 / 佛耶戈 / 俄洛伊 / 悠米 | 塞拉斯偷到的宇宙大爆炸是一份纯数据版（他的附加包在创意工坊，调不了 tft.dll）：跳向目标、落地的星光冲击、范围魔法伤害、击飞（特效表复制进附加包），按辅助类；佛耶戈的灵魂（辅助）、俄洛伊的灵魂、悠米坐在它头顶的高度 28 |
| 精灵图（高清帧 PPU 2.875） | 参考是金铲铲客户端 TFTSet17 里它自己的模型（`tft17_ivernminion`，87 个关节：人形巨像的骨架、三朵花、`Meep_*` 是驾驶员小木灵，一张贴图）和它自己的 10 段动作（待机、弓身待机、走路、两段出拳、蹲下、倒地、举拳、双拳砸、起跳落地砸）。第 0 步 Codex 画了 A（3/4）和 B（侧面）各两版：A 第一稿 7 px 一格（137×115）、A 粗版 9 px、B 第一稿 6 px、B 粗版 17 px，另有它自己缩的 50×40 / 26×40。用户选 **A-1、40 游戏像素、PPU 2.875**（115 行 1:1），小木灵的脸读回完整，没有补画（[`tools/art/design_meepsie_model.py`](../../tools/art/design_meepsie_model.py)）。Codex 在第 0 步之后自己按 50×40 的粗图多做了 42 帧关键帧，身形前后不一，没有用。第 2 步 Codex 照它自己的动作画了 20 个姿势（骨架包 [`tools/art/pack_meepsie_poses.py`](../../tools/art/pack_meepsie_poses.py)：驾驶员放大 1.25 倍；走路量了 1.3 秒走路动画两只脚的前后，8 帧取一整圈，含两次两腿交错） |
| 动作 | [`tools/art/design_meepsie_poses.py`](../../tools/art/design_meepsie_poses.py)：Codex 每张大小都不一样（6.2–7.7 px 一格），按身体面积和驾驶员小木灵的大小分别定比例，每格取原稿那一格最多的定稿颜色，每张贴定稿的小木灵脸。[`tools/art/rig_meepsie.py`](../../tools/art/rig_meepsie.py)：普攻抡拳 + 砸下（Codex 的普攻起手举的是近处那只拳，砸下的却是另一只，起手改用技能1 的抡拳）；技能1 抡拳 + 砸地；技能2 弓身 + 举手放木灵；大招起跳、空中最高点（按离地 3.5 / 9 游戏像素抬起）、砸落、落地压低；死亡跪倒 + 折成一团；走路 8 帧一整圈 |
| 特效 | 9 张 + 3 个技能图标，Codex 画（[`tools/art/pack_meepsie_fx.py`](../../tools/art/pack_meepsie_fx.py) 的提示词：月尘、月岩、紫色五角星光、小木灵的嫩绿；参考是它自己、艾翁的小菊和巴德小木灵的贴图 [`tools/lol/fx_ref_meepsie.py`](../../tools/lol/fx_ref_meepsie.py)）。Codex 自己按格子多数取色读回时，细的东西（小木灵、星星、叶子、彩带）都丢了，震波还被压扁成三分之一高：[`tools/art/import_meepsie_fx.py`](../../tools/art/import_meepsie_fx.py) 从原稿按统一比例重读 7 张（减速和宇宙大爆炸用它交的）；图标先裁到边框再缩到 64 |
| 音效 | 施法、砸进地面、砸中是它自己的（第 17 赛季的音效包）；出拳、打中、蓄力砸、笑声、怒吼、倒地借艾翁的小菊（也是石头巨像），魔法伤害、木灵出现 / 飞行 / 治疗、减速借巴德的小木灵（[`tools/lol/extract_meepsie.py`](../../tools/lol/extract_meepsie.py)，15 个） |
| 选人卡片 | 蘑菇顶到脚 40 游戏像素、52 宽，卡片放得下：`banpick_center` (0, −10)（中间那朵蘑菇在卡片顶下 1 像素），脸 (6, −27)（小木灵的眼睛），中心 (0, −20)。待机按 `tools/art/hero_reels.py` 剪进技能2 弓身的那一帧（举手那帧会顶出卡片），卡片轮播普攻、月尘震地、治疗木灵、宇宙大爆炸 |

重新生成（素材来自本机的金铲铲 / 英雄联盟客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_meepsie.py --riot "D:\Riot Games\League of Legends" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_meepsie.py                         # 技能数据（E 和大招调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_meepsie.py                         # 五种语言的文字、音效配置、tft 包共享文件里它的键
python tools/art/design_meepsie_hd.py                     # Codex 第 0 步的原稿读回
python tools/art/design_meepsie_model.py                  # 定稿 A-1（137×115）
python tools/art/design_meepsie_poses.py                  # Codex 的姿势：按定稿的体型从原稿读回、换成定稿的颜色、贴定稿的脸
python tools/art/rig_meepsie.py                           # 全部动作帧 -> assets/source/ppu
python tools/art/ppu_restyle.py --hero meepsie            # 描边、补缝
python tools/art/ppu_hd.py --hero meepsie                 # 高清帧图集
python tools/art/import_meepsie_fx.py                     # 特效和图标
python tools/art/hero_reels.py --hero tft_meepsie         # 待机和选人卡片的轮播
python tools/art/preview_meepsie.py                       # docs/preview 里的预览
```
