<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 荏妮 Renni

<img src="img/tft_renni.png" alt="荏妮" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_renni` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 上单 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / Tank / CC / Heal |
| 高清帧 | PPU 2 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_renni_skills.gif)、[逐帧预览](../preview/tft_renni_frames.png)、[特效表](../preview/tft_renni_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_renni.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.2 秒 · 攻击距离 25000*

链锯每次咬3下，每下造成42% 攻击力物理伤害。微光狂热：生命低于40%时注射微光（每30秒一次），4秒内攻速+40%，并回复20%最大生命。

### 技能1 · 链锯冲撞

*冷却 9 秒 · 施放距离 40000 · 施放：指定目标 · 敌人（不含防御塔）*

冲向目标，在前方扇形里锯3次，每次造成40 + 60% 攻击力物理伤害并减速30%，持续1.5秒。

### 技能2 · 锯刃格挡

*冷却 10 秒 · 施放距离 30000 · 施放：指定目标 · 敌人（不含防御塔）*

竖起链锯格挡：获得100+80% 攻击力护盾，持续2.5秒，期间减伤20%。

### 大招 · 泥奔者重击

*冷却 50 秒 · 施放距离 30000 · 施放：指定目标 · 敌方英雄*

把目标挑起举过头顶，造成120 + 190% 攻击力物理伤害并击飞1.1秒，期间回复15%最大生命；再狠狠砸下，对前方周围敌人造成70 + 110% 攻击力物理伤害。

### 数值

攻击力 82（每级 +11）、生命 1150（每级 +115）、护甲 38（每级 +8）、魔抗 30（每级 +5）、移速 1000（每级 +10）。

## 相关脚本和素材

- [`tools/kit/build_renni.py`](../../tools/kit/build_renni.py)
- [`tools/kit/setup_renni.py`](../../tools/kit/setup_renni.py)
- [`tools/lol/extract_renni.py`](../../tools/lol/extract_renni.py)
- [`tools/art/preview_renni.py`](../../tools/art/preview_renni.py)
- [`tools/art/rig_renni.py`](../../tools/art/rig_renni.py)
- [`assets/source/renni/`](../../assets/source/renni)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_renni`）的第十三个英雄，上单（Melee，近战物理坦克）。《双城之战》第二季祖安的化工男爵荏妮（用户叫她伦妮）：红头发、戴发绿光的呼吸面罩、颈上一圈黑羽毛，扛一把巨大的黄铜链锯。金铲铲第 13 赛季的三费（`TFT13_Chainsaw`「荏妮」，炼金男爵 / 格斗家，物理坦克，射程 1，生命 850，法力 40/90），技能「泥奔者重击」：1.5 秒里把目标挑起举在半空（晕眩，500% 攻击力），自己回复 15% 最大生命，再砸到地上，对相邻敌人造成 200% 攻击力。用户选了**上路**和方案 A「泥奔者」：大招照金铲铲，被动微光狂热、普攻链锯研磨、技能1 链锯冲撞、技能2 锯刃格挡是我们加的。模型在 Riot 客户端的 `TFTSet13.wad.client`（`tft13_chainsaw.skn`，107 根骨骼；链锯是子网格 `Weapon`，有自己的贴图；动作只有路径哈希，按内容命名） |
| 普攻 / 被动 | **链锯研磨**（近战，打塔）：链锯往前一顶，一次普攻锯三下，第 12、18、24 tick 各 42% 攻击力。**微光狂热**：生命低于 40% 时给自己打一针微光（30 秒一次）：4 秒内攻速 +40%，回复 20% 最大生命。数据读不到生命比例，由 tft.dll 的被动来做 |
| 技能1 | **链锯冲撞**（冷却 9 秒，距离 40000）：冲到目标面前（MoveToTarget，播 `charge`），对前方扇形（半径 38000）锯 3 下，每下隔 10 tick（播 `grind`）：40 + 60% 攻击力的物理伤害并减速 30%，持续 1.5 秒 |
| 技能2 | **锯刃格挡**（冷却 10 秒，距离 30000）：竖起链锯挡在身前，获得 100 + 80% 攻击力的护盾，持续 2.5 秒，期间减伤 20% |
| 大招 | **泥奔者重击**（冷却 50 秒，敌方英雄在 30000 以内时放，金铲铲的技能）：第 14 tick 把链锯捅进去把目标挑起举过头顶（播 `ult`：捅、挑、举），120 + 190% 攻击力物理伤害并击飞 1.1 秒，施法期间不可阻挡，举着时回复 15% 最大生命（tft.dll）；第 74 tick 砸下（播 `slam`）：30000 以内的敌人受到 70 + 110% 攻击力物理伤害，裂地特效播在被砸的目标脚下。游戏只能把目标原地击飞到半空，做不到真的挂在链锯上 |
| 数值 | 攻击 82（+11）、生命 1150（+115）、护甲 38（+8）、魔抗 30（+5）、移速 1000（+10），攻击间隔 1.2 秒，射程 25000 |
| 平衡 | 经典引擎模拟（上路，两边三套阵容，纯数据版：微光那一针改成 30 秒一次挂在技能2 上、两处回血改成固定值）：草稿 −0.06（同一批 tft_scar 纯数据版 +2.87）；攻击、每下锯的比例、技能1 和大招的数字调高一档到 +4.10，取中间为**定稿** +2.03 / +2.05（种子 1–8 / 9–16；tft_scar +1.85，league_sett +2.07）。tft.dll 里按生命比例触发的微光和按最大生命的回血没有进模拟 |
| tft.dll | 数据做不到的部分在 tft 包自己的代码里（[`addons/tft/src/renni.rs`](../../addons/tft/src/renni.rs)，和刀疤、敖兴、石甲虫、蔚奥莱、范德尔、可酷伯、洛里斯、麦迪、希尔科、拉露恩、诺拉一起编成 `tft.dll`）：被动 `tft_renni:shimmer`（生命低于线且冷却好了就打一针：攻速 buff `tft_renni_p_rush`、按最大生命分段回血、播画面和音效；大招数据挂上举着的标记时按最大生命回血），日志写到 `%APPDATA%/TeamSamoyed/TeamfightManager2/data/tft_renni.log`。`build_renni.py` 每次核对代码的默认参数和数据一致 |
| 塞拉斯 / 佛耶戈 / 妮蔻 / 俄洛伊 / 悠米 | 塞拉斯偷到的是大招的纯数据版（`build_renni.sylas_ult`：回血改成固定值，特效表复制进附加包；`sylas_steal_check.py` 模拟里挑起、砸地的特效出现 31 次）。佛耶戈 / 妮蔻的表（近战类）、俄洛伊的幽灵图和悠米骑上去的高度（27）都加上了她 |
| 精灵图（高清帧 PPU 2.0） | Codex 第 0 步画了 A（金铲铲的待机，链锯竖在肩上）和 B（链锯平端向前的架势），格子 A 约 10 px、B 约 7 px，按它自己的格子读回；A 太窄（27–29 游戏像素宽，邻居 35–43），用户定 **B-1、高 38、PPU 2.0**（[`tools/art/design_renni_model.py`](../../tools/art/design_renni_model.py)：86×77）。姿势包的骨架是她自己的动作按帧投影出来的（[`tools/art/pack_renni_poses.py`](../../tools/art/pack_renni_poses.py)：头放大 1.7 倍，链锯按 `Weapon` 子网格拟合出主轴，锯齿朝离开发动机的一头），Codex 画了 19 个姿势，守住了 12 px 格子；[`tools/art/design_renni_poses.py`](../../tools/art/design_renni_poses.py) 把颜色对回定稿的 36 色，站着的帧在最像的位置贴上定稿的头和高领（盖住 Codex 自己画的、有的下巴偏长的头），倒地两帧保留 Codex 画的歪头跟着身体倒；Codex 为了塞进画布缩小、颜色糊掉的两帧举锯（`r_heave` / `r_hold`）从原稿按 11.2 px 一格重读。[`tools/art/rig_renni.py`](../../tools/art/rig_renni.py) 拼成走路（8 帧，每帧 141 毫秒）、普攻（顶 → 锯 → 顶 → 锯）、技能1（冲撞；锯）、技能2（竖锯格挡）、大招（捅 → 挑 → 举）、砸地（砸下 → 收势）、受击、阵亡（被打飞 → 躺倒） |
| 特效 | 10 张 + 3 个技能图标，Codex 画的（[`tools/art/pack_renni_fx.py`](../../tools/art/pack_renni_fx.py) 的提示词，参考是金铲铲里她自己的粒子贴图 [`tools/lol/fx_ref_renni.py`](../../tools/lol/fx_ref_renni.py)：火花、黄铜、钢、化工绿、微光紫粉、泥浆六组色阶）。十张每帧都左右对称，[`tools/art/import_renni_fx.py`](../../tools/art/import_renni_fx.py) 按原样切成 `tft_renni_fx` / `tft_renni_big`；砸地裂纹原来放在她前方 25 像素，游戏不镜像特效图，她朝左时会跑到背后，改成播在被砸的目标脚下。图标从原稿缩到 64×64 |
| 音效 | 她自己的金铲铲音效（Riot 客户端第 13 赛季：普攻、击中、技能1 的锯和击中、大招的出手、挑起、击中和砸地），大招配英文语音；微光那一针和回血借蒙多（R、W 回血），冲撞借蔚（Q 冲出），格挡借布隆（E）（[`tools/lol/extract_renni.py`](../../tools/lol/extract_renni.py)，13 段） |
| 选人卡片 | 头发到脚底 38 游戏像素：`banpick_center` (2, −12)（头顶离卡顶 1.5 像素），不另设缩放。脸 (5, −28)（面罩上方两眼之间）。待机按 `tools/art/hero_reels.py` 剪进普攻的帧，卡片轮播普攻、技能2、砸地、大招 |

重新生成（素材来自本机的金铲铲客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_renni.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_renni.py                   # 技能数据（被动调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_renni.py                   # 五种语言的文字、音效配置、tft 包共享文件里她的键
python tools/art/design_renni_hd.py               # Codex 第 0 步的原图读回
python tools/art/design_renni_model.py            # 定稿 B-1（86×77）
python tools/art/design_renni_poses.py            # Codex 的姿势：对色、贴定稿的头；两帧举锯从原稿重读
python tools/art/import_renni_fx.py               # 特效 -> tft_renni_fx / tft_renni_big，图标
python tools/art/rig_renni.py                     # 1 倍帧和 2.0 的原帧
python tools/art/ppu_restyle.py --hero renni      # 外描边
python tools/art/ppu_hd.py --hero renni           # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero tft_renni   # 待机和选人卡片的小动作
python tools/art/preview_renni.py                 # 预览和每个技能单独的 GIF
python tools/art/review_renni_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
python addons/league_sylas/make_override.py       # 塞拉斯偷到的泥奔者重击
cargo test --manifest-path addons/Cargo.toml -p tft   # tft.dll 的单元测试
```
