<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 索姆 Sohm

<img src="img/tft_sohm.png" alt="索姆" width="64">

| 项目 | 内容 |
|---|---|
| id | `tft_sohm` |
| 所属的包 | tft 包（金铲铲之战系列，mod_id `tft`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / Range / Shield |
| 高清帧 | PPU 1.8 |
| 附加包 | 无 |

其他预览：[skills](../preview/tft_sohm_skills.gif)、[逐帧预览](../preview/tft_sohm_frames.png)、[特效表](../preview/tft_sohm_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`tft/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `tft/champion/tft_sohm.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.5 秒 · 攻击距离 55000*

吐出水泡弹，造成100% 攻击力物理伤害。碧波之力：每次施放技能叠一层潮水（6秒，最多5层），每层法强+9%、攻速+9%。

### 技能1 · 潮涌

*冷却 4 秒 · 施放距离 62000 · 施放：指定目标 · 敌人（不含防御塔）*

朝没开花的敌人冲出一道潮涌，沿途敌人受到95 + 65% 法强魔法伤害，目标头上开出水之花（15秒）；带花的敌人倒下，花跳到附近的敌人。

### 技能2 · 海潮护佑

*冷却 8 秒 · 施放距离 60000 · 施放：无目标 · 敌人（不含防御塔）*

给附近生命比例最低的队友套上95 + 65% 法强的水盾（3秒），攻速+25%。

### 大招 · 潮汐绽放

*冷却 35 秒 · 施放距离 70000 · 施放：指定目标 · 敌方英雄*

所有水之花一齐绽放，每朵花周围的敌人受到180 + 90% 法强魔法伤害，花随之散去；没有花时在目标身上绽放。

### 数值

攻击力 78（每级 +6）、法强 40（每级 +20）、生命 980（每级 +102）、护甲 20（每级 +7）、魔抗 24（每级 +5）、移速 900（每级 +9）。

## 相关脚本和素材

- [`tools/kit/build_sohm.py`](../../tools/kit/build_sohm.py)
- [`tools/kit/setup_sohm.py`](../../tools/kit/setup_sohm.py)
- [`tools/lol/extract_sohm.py`](../../tools/lol/extract_sohm.py)
- [`tools/art/preview_sohm.py`](../../tools/art/preview_sohm.py)
- [`tools/art/rig_sohm.py`](../../tools/art/rig_sohm.py)
- [`assets/source/sohm/`](../../assets/source/sohm)

## 开发记录

| 部分 | 内容 |
|---|---|
| 定位 | tft 包（`tft_sohm`）的第二十二个英雄，中路（法师）。金铲铲第 7.5 赛季（巨龙之巢）的四费 `TFT7_AquaticDragon`「索姆」（碧波龙 / 法师 / 龙神，AP 施法者，射程 4）：一条一直浮在空中、身子盘成一圈的东方海龙，浅水蓝的蛇形身子、粉色背鳍、海草尾鳍，青绿到深紫的鬃毛，金橙头冠、紫宝石和两根珊瑚红鹿角。金铲铲原技能「潮涌」做 Q（标记、花会跳）和大招（花一齐绽放），其余按用户选的方案 A「潮汐之花」（2026-10-30）自己设计 |
| 普攻 / 被动 | **水泡弹**（射程 55000，打塔）：第 10 tick 从嘴里吐出追踪的水弹，100% 攻击力。**碧波之力**（tft.dll，金铲铲碧波龙羁绊的做法）：Q、E、R 每施放一次叠一层潮水，每层法强 +9%、攻速 +9%，6 秒，最多 5 层，叠一层所有层重新计时；身后涌起潮水 |
| 技能1 | **潮涌**（冷却 4 秒，距离 62000）：挺身蓄力，第 18 tick 整个身子弯成 S 往前一送，朝施法距离内最近的**还没开花**的敌方英雄（没有就是施法目标）冲出一道直线水浪（tft.dll 发射，穿过所有人，宽 9000，飞过目标 8000），途经的每个敌人受 95 + 65% 法强魔法伤害；到达目标时它头顶开出一朵水之花（15 秒）。带花的敌人倒下，花飞向 40000 以内最近的没花的敌人（英雄优先） |
| 技能2 | **海潮护佑**（冷却 8 秒，距离 60000）：盘紧后小爪一推，第 14 tick 给 55000 以内生命比例最低的己方英雄（可以是她自己，tft.dll 找人）套上 95 + 65% 法强的水盾（3 秒）和 25% 攻速。施法目标用 `None` 配 `EnemyWithoutTower`：配 `EnemyChampion` 时 AI 一局只放 8.6 次，这样 29 次 |
| 大招 | **潮汐绽放**（金铲铲原技能的第四次施法，冷却 35 秒，距离 70000，有敌方英雄时）：低低盘成一圈、笔直冲上去，第 24 tick 在空中一转：她的每一朵水之花一齐绽放，每朵花 32000 以内的敌人受 180 + 90% 法强魔法伤害（同一次每人只算一遍），花都谢掉；一朵花都没有时在施法目标身上绽放 |
| 数值 | 攻击 78（+6）、法强 40（+20）、生命 980（+102）、护甲 20（+7）、魔抗 24（+5）、移速 900（+9），攻击间隔 1.5 秒，射程 55000 |
| 平衡 | 经典引擎模拟（中路，对原版火法、冰法、雷法、风法、白魔，两边三套阵容，纯数据版：潮水是每次施法的限时增益（没有上限），潮涌是穿过目标的直线、没有花，水盾给随机队友，大招在 2 个随机敌方英雄身上炸）：草稿 −1.81（E 配 `EnemyChampion` 一局只放 8.6 次）；E 改 `EnemyWithoutTower` −1.89；Q 95 + 65% 每 4 秒、大招 180 + 90% 每 35 秒 +0.42；两者都改 +0.82；潮水 10% / 10%、水盾 110 + 70% +1.84；潮水 9% / 9%、水盾 95 + 65%：**+1.46 / +0.90**（种子 1–8 / 9–16；诺姆希纯数据同种子 +1.12 / +1.16） |
| tft.dll | [`addons/tft/src/sohm.rs`](../../addons/tft/src/sohm.rs)：被动 `tft_sohm:lagoon`（`on_update` 落下飞行中的水浪、照看每朵花：带花的倒下了就把花送到下一个敌人，花的增益没了就把它从表里拿掉）；原生效果 `tft_sohm:tide`（叠潮水）、`tft_sohm:wave` / `wave_hit`（挑没开花的目标、发水浪、途经伤害、开花）、`tft_sohm:guard`（找生命比例最低的队友套盾）、`tft_sohm:bloom`（每朵花绽放）；死亡时播死亡声。日志 `data/tft_sohm.log`（SPAWN / TIDE / WAVE / WAVE HIT / FLOWER / JUMP / GUARD / BLOOM） |
| 塞拉斯 / 佛耶戈 / 妮蔻 / 俄洛伊 / 悠米 | 塞拉斯偷到的潮汐绽放是纯数据版（`build_sohm.sylas_ult`：在 2 个随机敌方英雄身上开出水莲、炸开），特效表复制进附加包；佛耶戈 / 妮蔻的表（法师）、俄洛伊的灵魂（195 个）、悠米坐骑的头顶高度 28 |
| 精灵图（高清帧 PPU 1.8） | 参考是金铲铲客户端里她自己的模型（112 个关节：Spine / Neck 的长身子、Tail1–14 和尾鳍、四条小腿、耳朵和下巴；颜色贴图在 bin 里没有路径，按哈希找到；动作片段 idle / run / attack / spell / death / celebrate，另有一段 1.5 秒没名字的盘身）。第 0 步 Codex 画了 A（3/4）和 B（侧面），用户选 **B-1、40 游戏像素、PPU 1.8**（B 按它自己 8 px 一格读回正好 58×72，1:1）；读回的近处眼睛只有两格白，补了两格蓝色瞳孔。第 2 步 Codex 照她自己的动作片段画了 11 个姿势和 4 帧平游（骨架包 [`tools/art/pack_sohm_poses.py`](../../tools/art/pack_sohm_poses.py)：她的 Root 关节在地上，所以按脖子根 Neck1 对齐） |
| 动作 | Codex 每张用了自己的格子大小（大多 8 px，e_push 10、r_rise 9、游动 7 / 6），格数和定稿一样；它自己的成品统一按 8 px 缩，大格子的身体就变大、小格子的变小。所以从原稿按每张自己的格子读（[`tools/art/design_sohm_poses.py`](../../tools/art/design_sohm_poses.py)，身体是定稿的 0.91–1.05 倍）。头没转的贴定稿的脸；a_rear 的头画小了、e_push 的画大了、r_swirl 和 d_fall 的鹿角拉长了（r_swirl 多了一根，头上还飘着一条鬃毛带），这四张换成定稿的整个头、清掉多出来的鹿角和下巴；a_spit、q_send（张嘴吐水 / 推浪）、r_rise（头朝天）、d_down（躺倒）保留 Codex 的。[`tools/art/rig_sohm.py`](../../tools/art/rig_sohm.py)：待机上下浮一格；普攻挺身 + 甩头吐弹；潮涌挺身 + S 形前送；海潮护佑盘紧 + 小爪前推；潮汐绽放低盘 + 笔直上冲 + 空中转身；死亡扭身下坠 + 侧躺（躺倒那张镜像，头保持朝前，不跳到另一边） |
| 移动 | 金铲铲的「跑」是 2.67 秒先盘身、再平游、再盘回去，中间没有能循环的一下，所以取平游的 4 帧给 Codex 画。可这 4 帧 Codex 画出来身长从 115 格涨到 152 格，来回播放会像橡皮筋一样伸缩——改成只用其中一帧（run2，脸和定稿最像），让一道波浪从鬃毛后一路传到尾鳍（`rig_sohm.swim`：8 帧 × 100 ms，尾鳍处上下 2.6 格，一个波长 54 格），身长不变 |
| 特效 | 11 张 + 3 个技能图标，Codex 画（[`tools/art/pack_sohm_fx.py`](../../tools/art/pack_sohm_fx.py) 的提示词，参考是她自己第 7 赛季的粒子贴图 [`tools/lol/fx_ref_sohm.py`](../../tools/lol/fx_ref_sohm.py)）；飞出去的水弹、水浪、花苞朝右、上下对称，其余左右对称。[`tools/art/import_sohm_fx.py`](../../tools/art/import_sohm_fx.py)：大招的水莲 Codex 给的是 40 像素，可炸开的范围直径 64，从原稿重新读成 64×64；最后一帧顶上从上一格带进来的杂点清掉；3 个图标 Codex 缩得糊成一片，从 1254 像素的原稿重新缩到 64 |
| 音效 | 普攻、潮涌的水浪和标记、花的跳跃、大招的起手和命中是她自己的金铲铲音效（Riot 客户端 Map22 里第 7 赛季的音效包，`Play_sfx_tft7_AquaticDragon…`）；潮水、海潮护佑、水泡盾、大招的召唤和绽放借娜美，死亡借峡谷的小龙（[`tools/lol/extract_sohm.py`](../../tools/lol/extract_sohm.py)，15 个） |
| 选人卡片 | 鹿角尖到盘身底 40 游戏像素：`banpick_center` (0, −10)（按规则 −39 减去最高点 −29，算上浮起的一格）。脸 (9, −23)（眼睛）。待机按 `tools/art/hero_reels.py` 剪进普攻的起手帧，卡片轮播普攻、潮涌、海潮护佑、潮汐绽放 |

重新生成（素材来自本机的金铲铲客户端，音频和 Riot 的渲染不进仓库）：

```bash
python tools/lol/extract_sohm.py --riot "D:\Riot Games\League of Legends" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_sohm.py                      # 技能数据（被动、Q、E、大招调用 tft.dll），数字都在脚本的参数表 P 里；--plain 是平衡模拟用的纯数据
python tools/kit/setup_sohm.py                      # 五种语言的文字、音效配置、tft 包共享文件里她的键
python tools/art/design_sohm_hd.py                  # Codex 第 0 步的原图读回
python tools/art/design_sohm_model.py               # 定稿 B-1（58×72）
python tools/art/design_sohm_poses.py               # Codex 的姿势：从原稿按各自的格子读、换成定稿的颜色、贴定稿的脸或整个头
python tools/art/import_sohm_fx.py                  # 特效 -> tft_sohm_fx / tft_sohm_big，图标
python tools/art/rig_sohm.py                        # 1 倍帧和 1.8 的原帧
python tools/art/ppu_restyle.py --hero sohm         # 外描边
python tools/art/ppu_hd.py --hero sohm              # hd_ / lo_ 帧（要在 hero_reels 之前）
python tools/art/hero_reels.py --hero tft_sohm      # 待机和选人卡片的小动作
python tools/art/preview_sohm.py                    # 预览和每个技能单独的 GIF
python tools/art/review_sohm_actions.py --out <文件夹> --sheet   # 和金铲铲原版逐个动作对照的 GIF
cargo test --manifest-path addons/Cargo.toml -p tft   # tft.dll 的单元测试
```
