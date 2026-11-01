<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 迅捷蟹 Scuttle Crab

<img src="img/tft_scuttlecrab.png" alt="迅捷蟹" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_scuttlecrab` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 辅助 |
| 分类 / 标签 | 功能型（Util） · AP / Magic / Melee / Tank / Heal / Shield / CC |
| 高清帧 | PPU 2.67 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_scuttlecrab_skills.gif)、[逐帧预览](../preview/tft_scuttlecrab_frames.png)、[特效表](../preview/tft_scuttlecrab_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_scuttlecrab.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.33 秒 · 攻击距离 25000*

跳一段螃蟹舞，踩中身边所有敌人，造成100% 攻击力物理伤害。绿霸符：附近的友方英雄生命低于40%时回复12%最大生命（每人10秒一次）。

### 技能1 · 疾行神龛

*冷却 7 秒 · 施放距离 60000 · 施放：无目标 · 敌人（不含防御塔）*

在脚下放下神龛（4秒），水花使周围敌人受到80 + 60% 法强魔法伤害并减速40%；神龛里的友方英雄移速+30%、攻速+25%。

### 技能2 · 蟹壳护盾

*冷却 6 秒 · 施放距离 60000 · 施放：无目标 · 敌方英雄*

缩进壳里，获得120 + 60% 法强护盾（2秒）。护盾打光或到时间时蟹壳碎裂：周围敌人受到80 + 60% 法强魔法伤害、眩晕0.5秒并减速40%。

### 大招 · 你挖得动吗？

*冷却 25 秒 · 施放距离 50000 · 施放：无目标 · 敌方英雄*

钻入地下2.5秒：受到的伤害降低50%、免疫控制，持续回复250 + 80% 法强生命；然后钻出地面，周围敌人受到160 + 60% 攻击力物理伤害并被击飞1.5秒。

### 数值

攻击力 70（每级 +5）、法强 30（每级 +15）、生命 1200（每级 +115）、护甲 44（每级 +8）、魔抗 40（每级 +6）、移速 1000（每级 +10）。

## 相关脚本和素材

- [`tools/kit/build_scuttlecrab.py`](../../tools/kit/build_scuttlecrab.py)
- [`tools/kit/setup_scuttlecrab.py`](../../tools/kit/setup_scuttlecrab.py)
- [`tools/lol/extract_scuttlecrab.py`](../../tools/lol/extract_scuttlecrab.py)
- [`tools/art/preview_scuttlecrab.py`](../../tools/art/preview_scuttlecrab.py)
- [`tools/art/rig_scuttlecrab.py`](../../tools/art/rig_scuttlecrab.py)
- [`assets/source/scuttlecrab/`](../../assets/source/scuttlecrab)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_scuttlecrab`）的英雄，辅助（近战，魔法伤害，治疗，护盾，肉，控制）。金铲铲第 18 赛季的二费 `DA_Scuttlecrab18`「峡谷迅捷蟹」（峡谷野怪 / 主宰，繁中「河蟹」，英文 Scuttlecrab，射程 1）：背着青绿色叠片甲壳的河道螃蟹，甲片边缘柠檬黄绿、后沿一排尖刺，正前方一块灰色石头面甲，两只发光的柠檬黄绿眼睛长在短眼柄上，两根一节一节的长触角往后弯，甲壳下面一圈尖叶形的短腿和小钳子。游戏里叫用户说的「迅捷蟹」。金铲铲原技能「这种快乐你懂吗？」拆开用：被动「攻击换成跳舞、打身边所有敌人」做普攻，「钻地减伤回血」做大招，羁绊的「绿霸符」做被动；其余按用户选的方案 A「河道守护」（2026-11-01，辅助）照英雄联盟河蟹（加速神龛、护盾碎了会减速）自己设计 |
| 普攻 / 被动 | **螃蟹舞**（距离 25000，打塔）：第 15 tick 落地，身边 35000 以内所有敌人受 100% 攻击力物理伤害。**绿霸符**（tft.dll）：70000 以内的友方英雄（连它自己）生命掉到 40% 以下时回复 12% 最大生命，每人 10 秒一次 |
| 技能1 | **疾行神龛**（冷却 7 秒，距离 60000，打兵和野怪）：第 12 tick 在脚下放下 55000 宽的神龛，持续 4 秒；放下时水花使周围敌人受 80 + 60% 法强魔法伤害、减速 40% 1.5 秒；神龛每 15 tick 给里面的友方英雄（连自己）移速 +30%、攻速 +25%。水圈画面是它身上的施法画面（不跟随，不随方向转：范围投射物的画面在红色方会被转半圈） |
| 技能2 | **蟹壳护盾**（冷却 6 秒，距离 60000，只在打架时放）：第 8 tick 缩进壳里，得到 120 + 60% 法强的护盾 2 秒；护盾打光或到时间时蟹壳碎裂（tft.dll 每拍看护盾）：40000 以内的敌人受 80 + 60% 法强魔法伤害、眩晕 0.5 秒、减速 40% 1.5 秒 |
| 大招 | **你挖得动吗？**（金铲铲原技能，冷却 25 秒，距离 50000，有敌方英雄时）：钻进地下 2.5 秒，受到的伤害降低 50%、免疫控制，分 5 次回复 250 + 80% 法强；然后钻出地面，50000 以内的敌人受 160 + 60% 攻击力物理伤害并被击飞 1.5 秒 |
| 数值 | 攻击 70（+5）、法强 30（+15）、生命 1200（+115）、护甲 44（+8）、魔抗 40（+6）、移速 1000（+10），攻击间隔 80 tick，距离 25000 |
| 平衡 | 经典引擎模拟（辅助位，对原版牧师、武僧、吟游诗人、附魔师、道士，两边三套阵容，纯数据版：绿霸符换成放神龛时给周围回血、蟹壳到时间才碎）：初稿 −3.73（±0.44，很肉但没伤害没控制）；加神龛水花伤害减速、蟹壳碎晕、缩短冷却 −1.25 … −0.81；大招一局只放 5 次（距离 30000 太短）→ 距离 50000、蟹壳 6 秒一次、跳舞范围 35000 +0.26 / −0.25；攻击间隔 80、神龛 55000 宽 **+0.44（±0.33，种子 1–16）**；艾达丝同条件 +1.23 / +1.20。游戏里的绿霸符对所有掉血的队友生效，比模拟里强 |
| tft.dll | [`addons/tft/src/scuttlecrab.rs`](../../addons/tft/src/scuttlecrab.rs)：被动 `tft_scuttlecrab:greenbuff`（绿霸符：每拍看附近队友的生命，每人各自冷却；蟹壳：护盾打光或标记到时间就碎，伤害、眩晕、减速；倒地的声音）。日志 `data/tft_scuttlecrab.log` |
| 塞拉斯 / 佛耶戈 / 俄洛伊 / 悠米 | 塞拉斯偷到的「你挖得动吗？」就是数据版（大招本来就不调 tft.dll；特效表复制进附加包），按辅助类；佛耶戈的灵魂（辅助）、俄洛伊的灵魂、悠米坐在它背上的高度 22 |
| 精灵图（高清帧 PPU 2.667） | 参考是金铲铲客户端 TFTSet18 里它的模型（`tft18_scuttlecrab`，66 个关节，和英雄联盟河蟹 `sru_crab` 的骨架一模一样，一张贴图）；金铲铲没有它的动作文件，借英雄联盟 Map11 河蟹的 17 段动作（待机、举触角、跑、跳舞、缩壳、从壳里弹出、从地里钻出……）。第 0 步 Codex 画了 A（3/4）和 B（侧面）：A 原稿 8 px 一格，B 6 px，它自己缩的 46×32 / 50×33 糊了。用户选 **A-1、30 游戏像素、PPU 2.667**（120×80，80 行 1:1，[`tools/art/design_scuttlecrab_model.py`](../../tools/art/design_scuttlecrab_model.py)）。第 2 步 Codex 照河蟹的动作画了 20 个姿势（骨架包 [`tools/art/pack_scuttlecrab_poses.py`](../../tools/art/pack_scuttlecrab_poses.py)：脸放大 1.4 倍，跑步取 0.53 秒一整圈 8 帧，钻出地面的两帧红线以下切掉） |
| 动作 | [`tools/art/design_scuttlecrab_poses.py`](../../tools/art/design_scuttlecrab_poses.py)：Codex 每张大小都不一样（7.2–9.3 px 一格），按身体面积和石头面甲的大小定比例，每格取原稿那一格最多的定稿颜色，每张贴定稿的石头面甲（眼睛留 Codex 画在眼柄上的：它的眼柄更长，贴定稿的眼睛会变成四只眼）。[`tools/art/rig_scuttlecrab.py`](../../tools/art/rig_scuttlecrab.py)：普攻站高举钳 → 跳起 → 落地踩；技能1 举触角召唤；技能2 缩身 → 缩进壳里 → 弹出；大招缩壳后甲壳一点点沉进土里（地面以下切掉，最后只剩一点背），2.5 秒后从地里钻出、跳起、落地；死亡缩壳不动、触角瘫在地上；跑步 8 帧一整圈 |
| 特效 | 10 张 + 3 个技能图标，Codex 画（[`tools/art/pack_scuttlecrab_fx.py`](../../tools/art/pack_scuttlecrab_fx.py) 的提示词：河水、青绿甲片和黄绿边、河岸泥土、叶绿色的治疗；参考是雷克塞钻地、娑娜、索拉卡的贴图 [`tools/lol/fx_ref_scuttlecrab.py`](../../tools/lol/fx_ref_scuttlecrab.py)）。Codex 自己按格子多数取色读回时，水花、治疗的叶子和十字、击飞的土块、加速和减速的水流都丢了：[`tools/art/import_scuttlecrab_fx.py`](../../tools/art/import_scuttlecrab_fx.py) 从原稿按统一比例重读这 5 张（原稿是两列多行，按透明的间隔切开），其余用它交的；钻地的土包第 3–8 帧循环到钻出；图标从原稿缩到 64 |
| 音效 | 跳舞、加速神龛、护盾碎、眩晕、钻出地面、死亡是英雄联盟河蟹自己的（Map11 的河蟹音效包）；钻地、地下回血、钻出击飞借雷克塞，缩壳和撞击借拉莫斯，绿霸符借索拉卡的治疗，加速借娑娜（[`tools/lol/extract_scuttlecrab.py`](../../tools/lol/extract_scuttlecrab.py)，13 个） |
| 选人卡片 | 触角顶到腿尖 30 游戏像素、45 宽：`banpick_center` (0, −15)（默认 −12 时腿被卡片底边挡住），脸 (9, −12)（石头面甲），中心 (0, −15)。待机按 `tools/art/hero_reels.py` 剪进技能2 缩身的那一帧（举钳那帧触角会顶出卡片），卡片轮播普攻、疾行神龛、蟹壳护盾（大招大半时间在地下，不放进卡片） |

重新生成（素材来自本机的金铲铲 / 英雄联盟客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_scuttlecrab.py --riot "D:\Riot Games\League of Legends" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_scuttlecrab.py                     # 技能数据（被动调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_scuttlecrab.py                     # 五种语言的文字、音效配置、tft 包共享文件里它的键
python tools/art/design_scuttlecrab_hd.py                 # Codex 第 0 步的原稿读回
python tools/art/design_scuttlecrab_model.py              # 定稿 A-1（120×80）
python tools/art/design_scuttlecrab_poses.py              # Codex 的姿势：按定稿的体型读回、换成定稿的颜色、贴定稿的石头面甲
python tools/art/rig_scuttlecrab.py                       # 全部动作帧 -> assets/source/ppu
python tools/art/ppu_restyle.py --hero scuttlecrab        # 描边、补缝
python tools/art/ppu_hd.py --hero scuttlecrab             # 高清帧图集
python tools/art/import_scuttlecrab_fx.py                 # 特效和图标
python tools/art/hero_reels.py --hero tft_scuttlecrab     # 待机和选人卡片的轮播
python tools/art/preview_scuttlecrab.py                   # docs/preview 里的预览
```
