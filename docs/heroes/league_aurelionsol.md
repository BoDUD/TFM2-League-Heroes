<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 奥瑞利安·索尔 Aurelion Sol

<img src="img/league_aurelionsol.png" alt="奥瑞利安·索尔" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_aurelionsol` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / Range / CC |
| 高清帧 | PPU 1.75 |
| 附加包 | [奥瑞利安·索尔附加包](#附加包)（`league_aurelionsol`） |

![奥瑞利安·索尔演示](../preview/league_aurelionsol_showcase.gif)

其他预览：[skills](../preview/league_aurelionsol_skills.gif)、[逐帧预览](../preview/league_aurelionsol_frames.png)、[特效表](../preview/league_aurelionsol_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_aurelionsol.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.5 秒 · 攻击距离 55000*

甩出一颗星星。星海焕然：技能命中英雄收集星尘（每层法强+3%，最多15层），每6层下一次大招变为天瀑。星穹流丽：击杀英雄后起飞4秒，移速+60%、法强+20%。

### 技能1 · 星河冲荡

*冷却 1 秒 · 施放距离 75000 · 施放：指定目标 · 敌人（不含防御塔）*

引导龙息1.5秒，每0.17秒对一线上的敌人造成26 + 17% 法强魔法伤害，喷同一目标1秒后每次额外30；被控制打断。飞行中无冷却、引导更久。

### 技能2 · 星芒凝汇

*冷却 1 秒 · 施放距离 75000 · 施放：指定目标 · 敌人（不含防御塔）*

在目标处召唤黑洞（5秒），每0.25秒造成16 + 9% 法强魔法伤害，把敌人拉向中心并减速25%；中心每秒造成英雄最大生命值4%的真实伤害。

### 大招 · 星天落瀑

*冷却 35 秒 · 施放距离 125000 · 施放：指定目标 · 敌方英雄*

星落：星星坠落在目标处，造成270 + 85% 法强魔法伤害并眩晕1秒。天瀑：范围更大，350 + 105% 法强并击飞0.83秒，外圈冲击波再造成80 + 30% 法强并减速50%。

### 数值

攻击力 66（每级 +6）、法强 40（每级 +20）、生命 1000（每级 +92）、护甲 24（每级 +6）、魔抗 26（每级 +4）、移速 900（每级 +9）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 奥瑞利安·索尔附加包

[奥瑞利安·索尔附加包](../../addons/league_aurelionsol/README.md)：`league_aurelionsol` v0.1.0

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 星海焕然（星尘） | 每层是一个永久 buff（`league_aurelionsol_d1`…`d15`，各带 `d_ap`% 法强），死亡时引擎清掉全部 buff，每条命从零叠起 | 活着时记下每一层，死亡清掉后原样补回（最多 `d_max` 层） |
| 星芒凝汇（黑洞中心） | 中心每秒打英雄最大生命的 `e_exec`%（真实伤害，处决的替身） | 同样的伤害，另外英雄生命低于 `e_low`% + 每层星尘 `e_low_d`%（默认 5% + 1%/层，最多 20%）就直接处决 |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】甩出一颗星星。星海焕然：技能命中英雄收集星尘（每层法强+3%，最多15层，死亡后保留），每6层下一次大招变为天瀑。星穹流丽：击杀英雄后起飞4秒，移速+60%、法强+20%。
- **技能2 · 星芒凝汇**：【附加包】在目标处召唤黑洞（5秒），每0.25秒造成16 + 9% 法强魔法伤害，把敌人拉向中心并减速25%；中心处决生命低于5%（每层星尘+1%）的英雄。

## 相关脚本和素材

- [`tools/kit/build_aurelionsol.py`](../../tools/kit/build_aurelionsol.py)
- [`tools/kit/setup_aurelionsol.py`](../../tools/kit/setup_aurelionsol.py)
- [`tools/lol/extract_aurelionsol.py`](../../tools/lol/extract_aurelionsol.py)
- [`tools/art/preview_aurelionsol.py`](../../tools/art/preview_aurelionsol.py)
- [`tools/art/rig_aurelionsol.py`](../../tools/art/rig_aurelionsol.py)
- [`assets/source/aurelionsol/`](../../assets/source/aurelionsol)

## 开发记录

> 下面是原来 README 里「英雄：奥瑞利安·索尔」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 中路（Magician，标签 AP / Magic / Range / CC），第 164 位英雄（I 组第四位；计划里是下路替补，用户选了中路）。铸星龙王 奥瑞利安·索尔：在宇宙里游动的星辰巨龙，浮在空中没有腿，浅蓝白的骨质龙脸、亮青色的眼睛、一排白尖牙，金色冠盔和往后扫的金角，洋红紫的鬃毛，深海军蓝的鳞甲身体爬着青色发光线，背上一排深紫尖刺，紫色龙爪戴金护腕，胸口往下是一条深蓝到紫罗兰、点着星星的星云尾巴 |
| 普攻 / 被动 | 爪子甩出一颗星星（射程 55000，每 90 tick 一下，66 攻击 +6/级）。**星海焕然**：技能命中英雄收集星尘（龙息每秒最多一层、黑洞困住英雄每秒一层、星落 / 天瀑每命中一个英雄一层），每层法强 +3%，最多 15 层（主包里死亡清零，附加包保留）；每 6 层下一次大招变为天瀑。**星穹流丽**（W 并进被动）：他打过的敌方英雄阵亡（3 秒内，谁补的刀都算）后起飞 4 秒：移速 +60%、法强 +20%、无视地形，龙息冷却 2.5 秒、引导 2.5 秒；之后 20 秒才能再飞，冷却中又有击杀就缩到 5 秒 |
| 技能1 | **星河冲荡**（冷却 5 秒，射程 75000）：引导龙息 1.5 秒（被控制打断），每 10 tick 从嘴里喷出一段星光（直线 78000、宽 6000，穿过所有敌人），26 + 17% 法强 魔法伤害；喷同一个目标 1 秒后每段再加 30。龙息一段段慢慢往前推（每 tick 2500），连成一道光流 |
| 技能2 | **星芒凝汇**（冷却 10.5 秒，射程 75000）：黑洞种子抛到目标处，张开 5 秒的黑洞（半径 26000）：每 15 tick 造成 16 + 9% 法强 魔法伤害、把敌人往中心拉一点、减速 25%；中心（半径 9000）每秒造成英雄最大生命 4% 的真实伤害（主包的处决替身：数据读不到生命；附加包按真实生命处决） |
| 大招 | **星落**（冷却 35 秒，射程 125000，对敌方英雄）：头顶聚起星座，星星笔直坠下（30 tick）砸在目标处（半径 22000），270 + 85% 法强 魔法伤害并眩晕 1 秒。**天瀑**（星尘攒满后的下一次）：半径 30000，350 + 105% 法强 魔法伤害并击飞 50 tick；12 tick 后外圈冲击波（半径 45000）再造成 80 + 30% 并减速 50%（1.5 秒） |
| 连招 | 「有连招要做连招」，用户四个都要：**E 黑洞 → Q 龙息**：黑洞第一次困住英雄，马上对他喷龙息（龙息冷却好时），黑洞存在期间法强 +15%（被拉住的吃更多伤害）；**R 星落 → E 黑洞**：星星砸下，落点立刻张开黑洞（黑洞冷却好时），先晕后拉；只有奥瑞利安·索尔自己会（塞拉斯偷到的大招只有星星）；**星尘满 → 天瀑**；**击杀 → 飞行强化**（龙息无冷却、伤害更高）。三局追踪：每局 E → Q 2–16 次、R → E 1–5 次、天瀑 1–4 次、起飞 1–3 次 |
| 数值 | 攻击 66（+6）、法术强度 40（+20）、生命 1000（+92）、护甲 24（+6）、魔抗 26（+4）、移速 900（+9）、射程 55000 |
| 平衡 | 经典引擎模拟（中路，对火法师、冰法师、雷法师、风法师、白法师，两边三套阵容；同一批对局阿萝拉 +0.93 / +1.01）：草稿 −3.01（龙息每段 14 + 9%）；龙息 22 + 15%、黑洞 14 + 8%、星落 260 + 80%、生命 1000、护甲 24 +0.35；再往上（30 + 20%、18 + 10%、280 + 90%）+1.74；取中间（26 + 17%、16 + 9%、270 + 85% / 天瀑 350 + 105%）+0.40 / +1.41；龙息放慢到每 tick 2500（画面上连成光流，伤害晚一点到）定稿 +0.54 / +1.02（种子 1–8 / 9–16） |
| 附加包 | `league_aurelionsol`（在 `league_addons` 合集里，[`addons/league_aurelionsol/README.md`](../../addons/league_aurelionsol/README.md)）：**星尘死后保留**（活着时记下每一层，死亡清掉后原样补回）；**黑洞中心按真实生命处决**：英雄生命低于 5% + 每层星尘 1%（最多 20%）就直接处决（真实伤害 = 生命 + 护盾 + 1） |
| 精灵图（高清帧 PPU 1.75） | Codex 第 0 步画了 A（悬浮待机）和 B（星穹飞行）（[`tools/art/pack_aurelionsol_picture.py`](../../tools/art/pack_aurelionsol_picture.py)：3D 模型只有上半身，星云尾巴是粒子，布局图上用紫圈画出尾巴的走向），[`tools/art/design_aurelionsol_hd.py`](../../tools/art/design_aurelionsol_hd.py) 按原图自己的格子读回（约 8 像素一格），[`tools/art/review_aurelionsol_size.py`](../../tools/art/review_aurelionsol_size.py) 摆在中路法师旁边比大小，用户定冠盔顶到尾尖 44 游戏像素、PPU 1.75。第 1 步（[`tools/art/pack_aurelionsol_model.py`](../../tools/art/pack_aurelionsol_model.py)）画游戏尺寸，用户挑 A-2（56 × 77）当待机、B-2（85 × 51）当移动（[`tools/art/design_aurelionsol_model.py`](../../tools/art/design_aurelionsol_model.py)；尾尖上第 0 步那颗小星星读回成的黑疙瘩清掉：「这里多出来一个是什么意思」）。动作：Codex 照骨架画 10 个关键姿势（[`tools/art/pack_aurelionsol_poses.py`](../../tools/art/pack_aurelionsol_poses.py)，骨架按定稿量的：手臂 23 格、尾巴 44 格），[`tools/art/design_aurelionsol_poses.py`](../../tools/art/design_aurelionsol_poses.py) 按头的大小读回、贴回定稿的头、身子缩回定稿的大小（Codex 画大了 3%–20%），吐息那张保留 Codex 张开的下颌、嘴里补成深紫；[`tools/art/rig_aurelionsol.py`](../../tools/art/rig_aurelionsol.py) 拼成待机、飞行移动（B-2 换上待机的头，上下浮动、尾巴摆动）、普攻（扬爪 → 甩出）、Q（吸气 → 吐息，身子起伏）、E（伸爪 → 捧星）、R（召星 → 拽下）、受击、死亡（仰倒 → 倒地），全部悬浮离地 4 格 |
| 特效 | 19 张特效（[`tools/art/pack_aurelionsol_fx.py`](../../tools/art/pack_aurelionsol_fx.py) 的提示词，参考是英雄联盟里奥瑞利安·索尔自己的贴图，[`tools/lol/fx_ref_aurelionsol.py`](../../tools/lol/fx_ref_aurelionsol.py)），Codex 画回来，[`tools/art/import_aurelionsol_fx.py`](../../tools/art/import_aurelionsol_fx.py) 切成 `league_aurelionsol_fx` / `league_aurelionsol_big`：星星弹、龙息光段（画在弹道点前面，从嘴里接出来）、黑洞种子、黑洞（前三帧转、后三帧收，拉满 5 秒）、中心吞噬、头顶召星、坠落的星星（落点上竖直坠下，不跟弹道转；Codex 后两帧变成了两颗星，换成单颗星往下移）、星落砸地、天瀑、外圈冲击波、起飞、飞行星尘、星尘飞进身体、天瀑就绪和头顶的小星星 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_aurelionsol.py`](../../tools/lol/extract_aurelionsol.py)，18 段）：普攻的出手和打中，龙息的出手和灼烧，黑洞的出手、张开和吞噬，星落的出手、砸地和冲击，天瀑的巨星和外圈冲击波，起飞，天瀑就绪；配音：E、R、W 的施法语音，龙息没有施法语音，用通用攻击语音 |
| 图标 | 官方技能图标（星河冲荡、星芒凝汇、星落，另有星穹流丽、星海焕然），从本地客户端取 |
| 选人卡片 | 冠盔顶到尾尖 44 游戏像素，再悬浮 2：`league.dll` 的 UI_SIZES 画成 0.86、脸 (5, −35)、`banpick_center` −3（待机小动作里普攻扬爪那帧最高，−3 才不出卡片）。待机按 `tools/art/hero_reels.py` 剪进吸气、捧星、扬爪各一帧 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_aurelionsol.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_aurelionsol.py                # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_aurelionsol.py                # 五种语言的文字、音效配置、共享文件里他的键（脸 5,-35，卡片 -3）
python tools/art/design_aurelionsol_hd.py            # Codex 第 0 步的原图读回（A、B）
python tools/art/design_aurelionsol_model.py         # Codex 第 1 步的造型读回（A-2 待机、B-2 飞行，尾尖清理）
python tools/art/design_aurelionsol_poses.py         # Codex 的姿势读回（贴回定稿的头，身子缩回定稿大小）
python tools/art/import_aurelionsol_fx.py            # 特效 -> league_aurelionsol_fx / league_aurelionsol_big
python tools/art/rig_aurelionsol.py                  # 1 倍帧和 1.75 的原帧
python tools/art/ppu_restyle.py --hero aurelionsol   # 外描边、脸的位置
python tools/art/ppu_hd.py --hero aurelionsol        # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero aurelionsol    # 待机和选人卡片的小动作
python tools/art/preview_aurelionsol.py              # 预览和演示 GIF
python addons/league_aurelionsol/make_override.py    # 附加包的奥瑞利安·索尔副本（主包的奥瑞利安·索尔改了以后要重跑）
```
