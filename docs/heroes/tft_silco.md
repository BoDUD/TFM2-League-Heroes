<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 希尔科 Silco

<img src="img/tft_silco.png" alt="希尔科" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_silco` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / Range / Shield |
| 高清帧 | PPU 2 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_silco_skills.gif)、[逐帧预览](../preview/tft_silco_frames.png)、[特效表](../preview/tft_silco_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_silco.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.5 秒 · 攻击距离 55000*

甩出一支微光药剂，造成100% 攻击力物理伤害。统领：每次出生获得120 + 40% 法强护盾（15秒）；每放一次技能法强+10%，最多5层，阵亡清空。

### 技能1 · 罐装畸变体

*冷却 5 秒 · 施放距离 65000 · 施放：指定目标 · 敌人（不含防御塔）*

扔出储罐，造成65 + 45% 法强魔法伤害，放出2只畸变体扑向附近的敌人，各咬5口，每口15 + 11% 法强魔法伤害；被咬的人倒下就跳到下一个。

### 技能2 · 微光注射

*冷却 12 秒 · 施放距离 60000 · 施放：指定目标 · 敌方英雄*

把微光抛给身边攻击力最高的友方英雄（没有就自己）：攻速+50%、移速+20%，4秒；药效过去扣当前生命的8%。

### 大招 · 炼金狂潮

*冷却 50 秒 · 施放距离 70000 · 施放：指定目标 · 敌方英雄*

向敌方英雄扔出巨型储罐，造成180 + 80% 法强魔法伤害，放出4只畸变体，留下4秒毒雾：敌人减速30%，每秒受到6 + 4% 法强魔法伤害。

### 数值

攻击力 72（每级 +6）、法强 40（每级 +20）、生命 900（每级 +94）、护甲 18（每级 +7）、魔抗 22（每级 +4）、移速 900（每级 +9）。

## 相关脚本和素材

- [`tools/kit/build_silco.py`](../../tools/kit/build_silco.py)
- [`tools/kit/setup_silco.py`](../../tools/kit/setup_silco.py)
- [`tools/lol/extract_silco.py`](../../tools/lol/extract_silco.py)
- [`tools/art/preview_silco.py`](../../tools/art/preview_silco.py)
- [`tools/art/rig_silco.py`](../../tools/art/rig_silco.py)
- [`assets/source/silco/`](../../assets/source/silco)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_silco`）的第四个英雄，中单（Magician，标签 AP / Magic / Range / Shield）。祖安的化工男爵，金铲铲之战第 13 赛季（双城之战）的四费棋子（炼金男爵 / 统领）。金铲铲里他只有一个技能「罐装畸变体」（扔储罐、放出畸变体连咬几口），所以技能2、大招和被动都是自己设计的，用户从三套方案里选了 A「统领·畸变体」。模型在 Riot 客户端的 `TFTSet13.wad.client`（子网格 M_Body / ExtraShimmer 手里的药瓶 / Knife 飞刀 / M_Cane 手杖，七段动作只有路径哈希，按内容命名） |
| 普攻 / 被动 | 甩出一支微光药剂（射程 55000，100% 攻击）。**统领**：每次出生 / 复活得到 120 + 40% 法强的护盾 15 秒（tft.dll，数据没有「出生」的时机）；每放一次技能（技能 / 技能2 / 大招）法强 +10%，最多 5 层，叠满头顶亮起伤疤眼印记，阵亡清空（数据自己的阶梯） |
| 技能1 | **罐装畸变体**（冷却 5 秒，射程 65000）：储罐抛向目标，砸地 65 + 45% 法强魔法伤害，放出 2 只畸变体（tft.dll）：扑向储罐附近的敌人（先英雄，分给不同的人），各咬 5 口、每 0.75 秒一口，每口 15 + 11% 法强；被咬的人死了 / 选不中了就跳到附近最近的敌人身上接着咬。畸变体是骑在被咬的人身上的画面（左右两边各一只），像安妮的提伯斯 |
| 技能2 | **微光注射**（冷却 12 秒，只在打英雄时放）：把微光抛给身边攻击力最高的友方英雄（没有就自己），攻速 +50%、移速 +20%，4 秒；药效过去扣当前生命的 8%，不会扣死（tft.dll） |
| 大招 | **炼金狂潮**（冷却 50 秒，射程 70000，对敌方英雄）：巨型储罐抛向敌方英雄（地上预警圈），砸地 180 + 80% 法强魔法伤害，放出 4 只畸变体，留下 4 秒微光毒雾：雾里的敌人减速 30%，每秒受到 6 + 4% 法强魔法伤害（tft.dll） |
| 数值 | 攻击 72（+6）、法强 40（+20）、生命 900（+94）、护甲 18（+7）、魔抗 22（+4）、移速 900（+9） |
| 平衡 | 经典引擎模拟（中单，对火法、冰法、雷法、风法、白魔法师，两边三套阵容，纯数据版：畸变体算成储罐目标身上的持续伤害，毒雾算成减速）：草稿（Q 40 + 30%、每口 8 + 6%、R 150 + 65%、E +40%、每层 8%、生命 860）−2.40（同一批 league_ziggs +1.17）；Q 55 + 40%、每口 12 + 9%、R 180 + 80%、每层 10%、生命 900 −0.30；每口 15 + 11%、E +50% +0.32；Q 65 + 45%（**定稿**）+1.25 / +1.22（种子 1–8 / 9–16，league_ziggs +1.17 / +2.22）。tft.dll 的规则在这个引擎里跑不了：游戏里畸变体会换人接着咬，可能比模拟强一点 |
| tft.dll | 数据做不到的部分在 tft 包自己的代码里（[`addons/tft/src/silco.rs`](../../addons/tft/src/silco.rs)，和诺拉、拉露恩一起编成 `tft.dll`）：被动 `tft_silco:baron`（出生护盾），储罐落地调用 `tft_silco:canister` / `tft_silco:flood`（畸变体：每口重排一次的效果，被咬的人、剩几口、哪一边、到期的拍都记在它的输入里；毒雾每 15 拍一次），技能2 调用 `tft_silco:inject` / `comedown`。`build_silco.py` 每次核对代码的默认参数、读写的名字和登记的效果都在数据里 |
| 塞拉斯 / 佛耶戈 / 妮蔻 / 俄洛伊 | 用户：「塞拉斯的大招什么一定要能偷到特效版本的 佛爷戈妮蔻的变身 俄洛伊的幽灵图」。塞拉斯的附加包在创意工坊上、tft 包不在，偷来的大招不能调用 tft.dll：`build_silco.sylas_ult()` 给他一个纯数据版的炼金狂潮（巨型储罐、预警圈、爆炸、一次毒雾、范围减速，畸变体是目标身上每 0.75 秒啃一口的画面和伤害），`addons/league_sylas/make_override.py` 的 `STOLEN` 用它，特效表复制进附加包；`sylas_steal_check.py` 模拟里 36 次事件（储罐、爆炸、毒雾、啃咬都出现）。佛耶戈 / 妮蔻的表（法师类）和俄洛伊的幽灵图都加上了他 |
| 精灵图（高清帧 PPU 2.0） | Codex 第 0 步画了 A（拄手杖、举着微光药剂瓶，金铲铲原样）和 B（不拿手杖），实际格子约 9.8 px（要求 11），[`tools/art/design_silco_hd.py`](../../tools/art/design_silco_hd.py) 按它自己的格子读回；用户定 **A-1、高 40、PPU 2.0**（[`tools/art/design_silco_model.py`](../../tools/art/design_silco_model.py)：44×80，缩小时丢了的远处伤疤眼补回橙红色）。姿势包的骨架是他自己的动作按帧投影出来的（[`tools/art/pack_silco_poses.py`](../../tools/art/pack_silco_poses.py)：头放大到定稿的比例，35° 视角，飞刀藏掉——我们的普攻甩药剂），Codex 画了 15 个姿势；[`tools/art/design_silco_poses.py`](../../tools/art/design_silco_poses.py) 读原稿、按头找比例，身子统一缩 1/1.05（Q / R 投掷和大招起手 Codex 画大了一截，单独缩回），贴回定稿的头，去掉甩出那帧手边多画的飞瓶，补上身体围住的小洞和单格裂缝；[`tools/art/rig_silco.py`](../../tools/art/rig_silco.py) 按双脚定位（Codex 每张画布上的位置不一致）拼成待机、走路（拄杖）、普攻（拉手 → 甩出 → 收势）、技能1（低身握储罐 → 扬手）、技能2（端详药瓶 → 往后抛给队友）、大招（抬膝托起巨型储罐 → 扬手）、受击、阵亡。外描边加粗时不往手杖和腿之间的窄缝里长（`ppu_restyle.open_slits`：长满了是一块黑楔子），不用 pinholes（会把手杖围出的透空整块填黑） |
| 特效 | 18 张 + 3 个技能图标，Codex 画的（[`tools/art/pack_silco_fx.py`](../../tools/art/pack_silco_fx.py) 的提示词，参考是金铲铲里他自己的粒子贴图和畸变体模型 [`tools/lol/fx_ref_silco.py`](../../tools/lol/fx_ref_silco.py)），[`tools/art/import_silco_fx.py`](../../tools/art/import_silco_fx.py) 切成 `tft_silco_fx` / `tft_silco_big`：两张爆炸后几帧顶上残留的分隔线、注射和药效过去两边的虚线框去掉；咬人的畸变体只画了左边那只，右边那只是翻转的 |
| 音效 | 他自己的第 13 赛季金铲铲音效（Riot 客户端 Map22 的 `MODE_TFT_Set13_Champs_SFX`：普攻甩出 / 命中、储罐出手 / 爆炸），大招是他的英文配音（WeGame 客户端没有第 13 赛季的中文配音）；畸变体啃咬借纳亚菲利的小狗，微光注射借烈娜塔给队友注射，巨型储罐爆炸借古拉加斯的酒桶（[`tools/lol/extract_silco.py`](../../tools/lol/extract_silco.py)，8 段） |
| 选人卡片 | 头发到脚底 41 游戏像素（卡片画布 40 高）：`banpick_center` −10（bp_card_audit 的规则：头发在画布顶下 1 像素，脚底藏 2 像素），不另设缩放。脸 (2, −33)。待机按 `tools/art/hero_reels.py` 剪进端详药瓶那一帧，卡片轮播技能1、普攻、技能2、大招 |

重新生成（素材来自本机的金铲铲 / 英雄联盟客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_silco.py --riot "D:\Riot Games\League of Legends" --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_silco.py                 # 技能数据（调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_silco.py                 # 五种语言的文字、音效配置、tft 包共享文件里他的键
python tools/art/design_silco_hd.py             # Codex 第 0 步的原图读回
python tools/art/design_silco_model.py          # 定稿 A-1 缩到 80 行，补回伤疤眼
python tools/art/design_silco_poses.py          # Codex 的姿势读回（按头的格子，贴回定稿的头）
python tools/art/import_silco_fx.py             # 特效 -> tft_silco_fx / tft_silco_big，图标
python tools/art/rig_silco.py                   # 1 倍帧和 2.0 的原帧
python tools/art/ppu_restyle.py --hero silco    # 外描边
python tools/art/ppu_hd.py --hero silco         # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero tft_silco # 待机和选人卡片的小动作
python tools/art/preview_silco.py               # 预览和每个技能单独的 GIF
python tools/art/review_silco_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
python addons/league_sylas/make_override.py     # 塞拉斯偷到的炼金狂潮（纯数据版）
cargo test --manifest-path addons/Cargo.toml -p tft   # tft.dll 的单元测试（希尔科、拉露恩、诺拉）
```
