<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 麦迪 Maddie

<img src="img/tft_maddie.png" alt="麦迪" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_maddie` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | ADC |
| 分类 / 标签 | 射手（Range） · AD / Range |
| 高清帧 | PPU 1.5 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_maddie_skills.gif)、[逐帧预览](../preview/tft_maddie_frames.png)、[特效表](../preview/tft_maddie_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_maddie.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.1 秒 · 攻击距离 68000*

步枪射击，造成100% 攻击力物理伤害。狙神：目标离得越远，她造成的伤害越高，最多+25%；被通缉的敌人阵亡时她领一份赏金：攻速+15%，最多4份。

### 技能1 · 连拨击锤

*冷却 9 秒 · 施放距离 80000 · 施放：指定目标 · 敌人（不含防御塔）*

半蹲朝范围内最远的敌人连开6枪（先打英雄），每枪打中路上第一个敌人，造成10 + 40% 攻击力物理伤害。

### 技能2 · 通缉令

*冷却 15 秒 · 施放距离 90000 · 施放：指定目标 · 敌方英雄*

通缉附近当前生命最高的敌方英雄8秒：它受到的伤害+15%。

### 大招 · 执法狙杀

*冷却 50 秒 · 施放距离 200000 · 施放：指定目标 · 敌方英雄*

瞄准后向生命比例最低的敌方英雄射出一发穿透子弹，路上每个敌人受到220 + 140% 攻击力物理伤害，按其已损失生命比例最多再加60%。

### 数值

攻击力 104（每级 +20）、生命 880（每级 +88）、护甲 18（每级 +7）、魔抗 15（每级 +3）、移速 900（每级 +9）。

## 相关脚本和素材

- [`tools/kit/build_maddie.py`](../../tools/kit/build_maddie.py)
- [`tools/kit/setup_maddie.py`](../../tools/kit/setup_maddie.py)
- [`tools/lol/extract_maddie.py`](../../tools/lol/extract_maddie.py)
- [`tools/art/preview_maddie.py`](../../tools/art/preview_maddie.py)
- [`tools/art/rig_maddie.py`](../../tools/art/rig_maddie.py)
- [`assets/source/maddie/`](../../assets/source/maddie)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_maddie`）的第五个英雄，ADC（下路，Range，标签 AD / Range）。皮尔特沃夫的执法官神枪手，金铲铲之战第 13 赛季（双城之战）的一费棋子（执法官 / 狙神）。金铲铲里她只有一个技能「连拨击锤」（朝最远的敌人连开 6 枪，每枪打中路上第一个敌人），所以技能2、大招和被动都是自己设计的，用户选了方案 A「狙神·通缉」。模型在 Riot 客户端的 `TFTSet13.wad.client`（子网格 Maddie_Mat / Maddie_Weapon_Mat 步枪，七段动作只有路径哈希，按内容命名） |
| 普攻 / 被动 | 步枪射击（射程 68000，比凯特琳的 65000 远：金铲铲里她射程 6 格是最远的；100% 攻击），开枪那一帧子弹出膛，后坐力那一帧响她自己的换弹声。**狙神**：她打出的每一下（普攻、子弹、狙击）离目标越远伤害越高，10 万距离内均匀涨到 +25%（tft.dll 的 `on_attack`：数据量不了距离）；被通缉的敌人在通缉中阵亡，她领一份赏金：攻速 +15%，最多 4 份，她阵亡清零 |
| 技能1 | **连拨击锤**（冷却 9 秒，射程 80000）：半蹲、枪托抵肩，朝范围内**最远**的敌人（先英雄）连开 6 枪、每 8 拍一枪；每颗子弹沿直线飞，打中路上**第一个**敌人，10 + 40% 攻击物理伤害（tft.dll：目标死了就重新找最远的） |
| 技能2 | **通缉令**（冷却 15 秒，只在打英雄时放）：通缉附近当前生命最高的敌方英雄 8 秒，它受到的伤害 +15%（金色执法官徽章砸在它头顶，然后变成准星挂着）；它在通缉中阵亡，麦迪领赏金（tft.dll） |
| 大招 | **执法狙杀**（冷却 50 秒，射程 200000）：低蹲瞄准约 1 秒（目标身上的红色准星慢慢缩紧），一发穿透的海克斯子弹射向范围内**生命比例最低**的敌方英雄，直线上每个敌人受到 220 + 140% 攻击物理伤害，按它已损失的生命比例最多再加 60%（tft.dll） |
| 数值 | 攻击 104（+20）、生命 880（+88）、护甲 18（+7）、魔抗 15（+3）、移速 900（+9），攻击间隔 1.1 秒（金铲铲里她攻速只有 0.70） |
| 平衡 | 经典引擎模拟（下路，对弓箭手、枪手、回旋镖猎手、毒镖猎手，两边三套阵容，纯数据版：狙神算成 +15%，连拨击锤打 AI 选的目标，狙杀按一半血算加成，没有赏金）：草稿 +2.01（同一批 league_caitlyn +2.27）；按动作帧对好时间的**定稿** +2.19 / +2.81（种子 1–8 / 9–16，league_caitlyn +2.27 / +2.47） |
| tft.dll | 数据做不到的部分在 tft 包自己的代码里（[`addons/tft/src/maddie.rs`](../../addons/tft/src/maddie.rs)，和诺拉、拉露恩、希尔科一起编成 `tft.dll`）：被动 `tft_maddie:sniper`（距离加伤、赏金），技能1 `tft_maddie:fan` → `shot` → `bullet`（`spawn_projectile` 的直线子弹，碰到第一个敌人），技能2 `tft_maddie:wanted`，大招 `tft_maddie:snipe` → `round`（穿透）。子弹从枪口高度出去（起点比站位点高 14000），线还是穿过目标。`build_maddie.py` 每次核对代码的默认参数、读写的名字和登记的效果都在数据里 |
| 塞拉斯 / 佛耶戈 / 妮蔻 / 俄洛伊 | 塞拉斯的附加包在创意工坊上、tft 包不在，偷来的大招不能调用 tft.dll：`build_maddie.sylas_ult()` 给他纯数据版的执法狙杀（准星、瞄准、一发子弹打他放大招的那个英雄、命中），`addons/league_sylas/make_override.py` 的 `STOLEN` 用它，特效表复制进附加包；`sylas_steal_check.py` 模拟里 32 次事件（准星、子弹、命中都出现）。佛耶戈 / 妮蔻的表（射手类）和俄洛伊的幽灵图（177 个）都加上了她 |
| 精灵图（高清帧 PPU 1.5） | Codex 第 0 步画了 A（步枪扛在肩上，金铲铲原样）和 B（端枪），实际格子约 13.2 px（要求 11），[`tools/art/design_maddie_hd.py`](../../tools/art/design_maddie_hd.py) 按它自己的格子读回；用户定 **A-1、高 38、PPU 1.5**（[`tools/art/design_maddie_model.py`](../../tools/art/design_maddie_model.py)：44×57，缩小时远处那只眼睛变成杂色、嘴变成灰色，按近处那只眼睛的样子重画）。姿势包的骨架是她自己的动作按帧投影出来的（[`tools/art/pack_maddie_poses.py`](../../tools/art/pack_maddie_poses.py)：头放大到定稿的比例，35° 视角，步枪画成一条线、枪口标金圈；通缉令借她庆祝动作里伸手指人的那一帧），Codex 画了 15 个姿势，直接画在定稿的格子上、只用定稿的颜色；[`tools/art/design_maddie_poses.py`](../../tools/art/design_maddie_poses.py) 逐格找到头的位置贴回定稿的头，补上身体围住的小洞和单格裂缝；[`tools/art/rig_maddie.py`](../../tools/art/rig_maddie.py) 按裤子（腰）定位（按脚定位时岔开站和并脚站之间身体左右跳 4–9 格），拼成待机、跑步、普攻（端枪 → 开枪 → 枪口上扬 → 放平）、技能1（半蹲 → 6 次开枪 → 起身）、技能2（扛枪 → 伸手指人）、大招（半蹲 → 瞄准 → 开枪 → 大后坐力 → 放平）、受击、阵亡。枪口火光朝右，不能做成特效（红色方不翻转特效图），画进开枪那几帧（叠在描边之后：`ppu_restyle` 的 `fx`） |
| 特效 | 13 张 + 3 个技能图标，Codex 画的（[`tools/art/pack_maddie_fx.py`](../../tools/art/pack_maddie_fx.py) 的提示词，参考是金铲铲里她自己的粒子贴图 [`tools/lol/fx_ref_maddie.py`](../../tools/lol/fx_ref_maddie.py)），[`tools/art/import_maddie_fx.py`](../../tools/art/import_maddie_fx.py) 切成 `tft_maddie_fx` / `tft_maddie_big`（两张枪口火光进她的帧） |
| 音效 | 她自己的第 13 赛季金铲铲音效（Riot 客户端 Map22 的 `MODE_TFT_Set13_Champs_SFX`：开枪、命中、换弹、暴击命中、施法），大招是她的英文配音（发力声）；通缉令和狙杀的瞄准、开枪、命中借凯特琳的「让子弹飞」（她的上司，同一把皮城步枪）（[`tools/lol/extract_maddie.py`](../../tools/lol/extract_maddie.py)，11 段） |
| 选人卡片 | 帽顶到脚底 38 游戏像素：`banpick_center` −11（bp_card_audit 的规则：lo_idle 在中心上方 28.0），不另设缩放。脸 (1, −31)。待机按 `tools/art/hero_reels.py` 剪进指人和端枪的帧，卡片轮播普攻、技能1、技能2、大招 |

重新生成（素材来自本机的金铲铲 / 英雄联盟客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_maddie.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_maddie.py                 # 技能数据（调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_maddie.py                 # 五种语言的文字、音效配置、tft 包共享文件里她的键
python tools/art/design_maddie_hd.py             # Codex 第 0 步的原图读回
python tools/art/design_maddie_model.py          # 定稿 A-1 缩到 57 行，重画远处的眼睛和嘴
python tools/art/design_maddie_poses.py          # Codex 的姿势（贴回定稿的头）
python tools/art/import_maddie_fx.py             # 特效 -> tft_maddie_fx / tft_maddie_big，图标
python tools/art/rig_maddie.py                   # 1 倍帧和 1.5 的原帧（枪口火光是叠加层）
python tools/art/ppu_restyle.py --hero maddie    # 外描边
python tools/art/ppu_hd.py --hero maddie         # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero tft_maddie # 待机和选人卡片的小动作
python tools/art/preview_maddie.py               # 预览和每个技能单独的 GIF
python tools/art/review_maddie_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
python addons/league_sylas/make_override.py      # 塞拉斯偷到的执法狙杀（纯数据版）
cargo test --manifest-path addons/Cargo.toml -p tft   # tft.dll 的单元测试（麦迪、希尔科、拉露恩、诺拉）
```
