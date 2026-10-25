<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 阿萝拉 Aurora

<img src="img/league_aurora.png" alt="阿萝拉" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_aurora` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / Range / CC |
| 高清帧 | PPU 2.25 |
| 附加包 | [阿萝拉附加包](#附加包)（`league_aurora`） |

![阿萝拉演示](../preview/league_aurora_showcase.gif)

其他预览：[逐帧预览](../preview/league_aurora_frames.png)、[特效表](../preview/league_aurora_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_aurora.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.5 秒 · 攻击距离 55000*

魔杖点出灵光。驱灵奇术：命中英雄叠层，第三层抽出灵物，造成40 + 30% 法强+2%最大生命值的伤害，回复45 + 15% 法强生命并加速。灵纱洞开：被敌方英雄贴身时后跳，隐身1.25秒、加速30%（20秒一次）。

### 技能1 · 飞去来咒

*冷却 7.5 秒 · 施放距离 85000 · 施放：方向 · 敌人（不含防御塔）*

放出咒弹穿过敌人，造成100 + 55% 法强魔法伤害并留下诅咒；0.67秒后把诅咒抽回，回程再造成100 + 55% 法强魔法伤害。

### 技能2 · 怪奇喷涌

*冷却 13 秒 · 施放距离 70000 · 施放：指定目标 · 敌人（不含防御塔）*

向前喷出灵魂冲击，造成150 + 80% 法强魔法伤害并减速60%（逐渐减弱），随后向后跳开。

### 大招 · 双界合一

*冷却 35 秒 · 施放距离 60000 · 施放：指定目标 · 敌方英雄*

跳到敌方英雄身上，冲击波造成260 + 80% 法强魔法伤害并减速40%；张开领域3.5秒，减速其中敌人30%，目标走开时她穿过领域追上去。

### 数值

攻击力 68（每级 +6）、法强 40（每级 +20）、生命 960（每级 +90）、护甲 21（每级 +6）、魔抗 26（每级 +4）、移速 920（每级 +9）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 阿萝拉附加包

[阿萝拉附加包](../../addons/league_aurora/README.md)：`league_aurora` v0.2.0

| 技能 | 主包（纯数据） | 附加包 |
|---|---|---|
| 灵纱洞开（并入被动） | 普攻或怪奇喷涌开头，`w_cd` 过了、`w_near` 内有敌方英雄，就往后跳开、隐身 `w_inv` tick、加速 `w_ms`% | 同样的跳法，但还要她**生命低于 `w_low`%**（默认 35%），英雄联盟「残血时跳开」 |

装上附加包后游戏里显示的说明（和主包不同的部分）：

- **普攻 / 被动**：【附加包】魔杖点出灵光。驱灵奇术：命中英雄叠层，第三层抽出灵物，造成40 + 30% 法强 + 目标2%最大生命值的伤害，回复45 + 15% 法强生命并加速。灵纱洞开：生命低于35%被贴身时后跳，隐身1.25秒、加速30%（20秒一次）。

## 相关脚本和素材

- [`tools/kit/build_aurora.py`](../../tools/kit/build_aurora.py)
- [`tools/kit/setup_aurora.py`](../../tools/kit/setup_aurora.py)
- [`tools/lol/extract_aurora.py`](../../tools/lol/extract_aurora.py)
- [`tools/art/preview_aurora.py`](../../tools/art/preview_aurora.py)
- [`tools/art/rig_aurora.py`](../../tools/art/rig_aurora.py)
- [`assets/source/aurora/`](../../assets/source/aurora)

## 开发记录

> 下面是原来 README 里「英雄：阿萝拉」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 中路（Magician，标签 AP / Magic / Range / CC），第 157 位英雄（H 组第三位）。双界灵兔 阿萝拉：娇小的兔子女巫，铜红卷发和两条短麻花辫、圆金框眼镜后面紫蓝的大眼睛，青绿宽檐女巫帽里竖着两只长兔耳朵（外橙红、里浅粉）、红羽毛，米白高领和长外套、浅蓝白毛边披肩、青绿胸布、棕色编织腰带、深棕过膝长袜和白毛边短靴，身后一团蓬松的橙色兔尾巴，肩上扛着一根细长的魔杖。技能方案 A（用户选）：飞去来咒 / 怪奇喷涌 / 双界合一，灵纱洞开（W）并进被动；四条连招全要 |
| 普攻 / 被动 | 魔杖点出一团灵光（射程 55000，100% 攻击）。**驱灵奇术**：普攻和技能打中敌方英雄都叠一层（她身上记数，4 秒内有效，每个来源每次施放算一次——飞去来咒的去、回各算一次），第三层抽出灵物：40 + 30% 法强 魔法伤害 + 目标 2% 最大生命值的真实伤害，灵物飞回她身上回复 45 + 15% 法强 生命并加速 15% 1.5 秒（英雄联盟 1% 最大生命值、灵物回血加速）。**灵纱洞开**（并进来，20 秒一次）：普攻或怪奇喷涌开头，35000 内有敌方英雄贴身就往后跳开、隐身 1.25 秒、加速 30% 2 秒（主包读不到生命；附加包里还要生命低于 35%，用户选的「残血时跳开」） |
| 技能1 | **飞去来咒**（冷却 7.5 秒，`Direction` 施法，对 `EnemyWithoutTower`、射程 85000：兵线野怪也放）：咒弹穿过路上所有敌人飞 85000，100 + 55% 法强 魔法伤害并留下诅咒；0.67 秒后诅咒被抽回，咒弹从停下的地方飞回她身上，路上再打 100 + 55% 法强 魔法伤害 |
| 技能2 | **怪奇喷涌**（冷却 13 秒，射程 70000，对 `EnemyWithoutTower`）：身前打开界域之窗，往目标方向喷出一道灵魂冲击（锥形，75000），150 + 80% 法强 魔法伤害，减速 60% 0.5 秒、之后 25% 再 1 秒（英雄联盟 80% 逐渐减弱），然后往后跳开 24000（英雄联盟 250 码） |
| 大招 | **双界合一**（冷却 35 秒，射程 60000，对敌方英雄）：跳到他身上，落地冲击波 260 + 80% 法强 魔法伤害、减速 40% 1 秒；在他脚下张开两界交汇的领域（半径 38000，3.5 秒），里面的敌人减速 30%；领域在的时候每隔 1 秒看一次，身边 30000 内没有敌方英雄、大招的目标又在 45000 内，她就穿过领域传送到他身上（英雄联盟从领域一边传到另一边） |
| 连招 | 「有连招要做连招」，用户选了四条：**E → Q**：冲击打中英雄、飞去来咒就绪时立刻追加一颗追踪咒弹，0.67 秒后再把诅咒抽回来打第二次；**R → E**：大招落地、怪奇喷涌就绪时立刻在她身边炸开冲击并往后跳；**Q → 被动**：去、回两次各叠一层驱灵；**领域内传送追击**（见大招） |
| 数值 | 攻击 68（+6）、法强 40（+20）、生命 960（+90）、护甲 21（+6）、魔抗 26（+4）、移速 920（+9）、射程 55000 |
| 平衡 | 经典引擎模拟（中路，对火法、冰法、雷法、风法、白魔，两边三套阵容，灵纱洞开按主包的贴身条件）：草稿（Q 60 + 40%、E 100 + 60%、R 200 + 70%）−2.31（同一批对局彗 +1.16）；加伤害 −1.66；再加血量护甲和被动 −0.03；伤害再加、魔抗 26 −0.05；领域传送追击会让她一个人冲进敌人堆（关掉传送 +0.72），改成只追 45000 内的目标：**+0.93 / +1.01**（种子 1–8 / 9–16） |
| 附加包 | [`addons/league_aurora`](../../addons/league_aurora/README.md)（`league_aurora` 0.2.0，合集里也有）：**灵纱洞开按真实的生命**：她生命低于 35% 时每 tick 挂上 `league_aurora_low`，后跳还要这个标记（主包只看有没有敌方英雄贴身）。**大招挑时机**（AI 钩子 `league_aurora:realm`，用户 2026-10-24「阿罗拉大招逻辑怎么和LOL里面高手的不太一样」）：领域能关住两个以上敌方英雄而身边有队友时开团、关住 40% 血以下想跑的、被贴脸残血时砸下去，其余时候不放。佛耶戈、塞拉斯、凯隐、大招按键的英雄表也加上了她 |
| 精灵图（高清帧 PPU 2.25） | Codex 第 0 步画了 A（四分之三侧面）和 SA（[`tools/art/pack_aurora_picture.py`](../../tools/art/pack_aurora_picture.py)），[`tools/art/design_aurora_hd.py`](../../tools/art/design_aurora_hd.py) 按各自的格子读回（regrid 给的格子要比真实格子略大，不然会多切行：A 按 10 px 读成 126 行、纵向拉长 7%，改按 11 px 读成方格）；用户选「帽顶到脚底 38 游戏像素，PPU 1.5，只做四分之三侧面」。第 1 步两稿（[`tools/art/pack_aurora_model.py`](../../tools/art/pack_aurora_model.py)，每格 16 px），按 PPU 1.5 切到 57 行后用户：「太模糊了 用PPU调下像素」——Codex 的眼镜、眼睛、帽子金边是按半格画的，[`tools/art/design_aurora_model.py`](../../tools/art/design_aurora_model.py) 改按 Codex 的细格子读回，给了 1.75 / 2.0 / 2.25 三档，用户选 A-2、PPU 2.25（53 × 104，帽顶到脚底 86 行；远侧眼睛补画得和近侧一样高）。动作：用户「Codex 照骨架画姿势」，[`tools/art/pack_aurora_poses.py`](../../tools/art/pack_aurora_poses.py) 按英雄联盟的片段画了 17 个骨架（定稿的骨长：腿 24 格、手臂 23 格；头连帽子和耳朵 48 × 56 格占了一半多身高，手臂举不过头，魔杖举起时在头的右边、扛在肩上时从头后面穿过；62 格的魔杖是一根硬杆；尾巴跟着腰走）；[`tools/art/design_aurora_poses.py`](../../tools/art/design_aurora_poses.py) 按头的大小读回、贴回定稿的头（贴的范围避开魔杖）。8 张腿画长了 2–10 行（胯到脚底比定稿的 26 行长），用户「有问题的话你自己修复」：[`tools/art/design_aurora_legfix.py`](../../tools/art/design_aurora_legfix.py) 不重画，只在长袜那一段（胯下 2 行到靴子上面，靴子、裙子、头和上身一格不动）按"和上下行最像的先删"整行删掉多出来的行，站着的腿回到 26 行、踮脚 27–28、跨步和弓步 24、跳起收腿 21；r_reach 的魔杖斜穿那一段，先拿开、删完再沿它自己的方向滑回去，保持一根直杆；跑步四帧头框顶离地 102 / 104 / 102 / 104 行（着地帧低一点）。之前出的只重画腿的包（[`tools/art/pack_aurora_legs.py`](../../tools/art/pack_aurora_legs.py)、[`tools/art/design_aurora_legs.py`](../../tools/art/design_aurora_legs.py)）留着没用上。[`tools/art/rig_aurora.py`](../../tools/art/rig_aurora.py) 照英雄联盟的动作拼：普攻（举杖、点出）、飞去来咒（小跳举杖、甩出、收回）、怪奇喷涌（蹲下推出、往后跳）、双界合一（踮脚、高高跃起、落地）、灵纱洞开（缩成一团后跳）、跑步四帧、死亡（踉跄、坐倒） |
| 特效 | 20 张特效（[`tools/art/pack_aurora_fx.py`](../../tools/art/pack_aurora_fx.py) 的提示词，参考是英雄联盟里阿萝拉自己的贴图），Codex 画回来，[`tools/art/import_aurora_fx.py`](../../tools/art/import_aurora_fx.py) 切成 `league_aurora_fx` / `league_aurora_big`：灵光和它的星点、紫色菱形咒弹（去程、带着粉紫诅咒雾的回程）、咒弹打中、诅咒被扯碎时飞出的小灵兔、胸口的诅咒印、头顶的驱灵光圈、抽出的小灵兔、绕着她转的回血灵兔、后跳的灵雾光帘、加速的脚下灵光、界域之窗、灵魂冲击波、冲击打中、脚下的霜雾减速、落地的冲击环、两界交汇的领域（灵墙光帘、绕圈的小灵兔，3.5 秒）、冲击波打中、领域里传送的椭圆门；普攻打中的第一帧 Codex 画成了格子底部的一小块，导入时补画成居中的闪光 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_aurora.py`](../../tools/lol/extract_aurora.py)）：普攻和命中，飞去来咒的出手、命中、收回和回程命中，抽出灵物，灵纱洞开，怪奇喷涌的出手和命中，双界合一的出手、落地、领域、命中和传送，三句台词 |
| 图标 | 官方技能图标（飞去来咒、怪奇喷涌、双界合一，另有灵纱洞开、驱灵奇术），从本地客户端取 |
| 选人卡片 | 连耳朵约 48 游戏像素高，卡片画布只装得下约 40：`league.dll` 的 UI_SIZES 画成 0.82、`banpick_center` −9（`tools/art/bp_card_audit.py`：耳尖离画布上沿 3 像素，脚踩在下沿）。待机 10 帧一轮（举杖、收回魔杖），选人卡片 23 帧一轮（普攻、飞去来咒、怪奇喷涌、双界合一轮流放），`tools/art/hero_reels.py` 从她自己的动作帧里切 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_aurora.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_aurora.py                     # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_aurora.py --face 1,-27        # 五种语言的文字、音效配置、共享文件里她的键（脸 1,-27）
python tools/art/design_aurora_hd.py                 # Codex 第 0 步的原图读回（A、SA）
python tools/art/design_aurora_model.py              # Codex 第 1 步的造型读回（A-2，PPU 2.25）
python tools/art/design_aurora_poses.py              # Codex 的姿势读回（贴回定稿的头）
python tools/art/design_aurora_legfix.py             # 画长的腿按整行删短（第一版读回在 hd_first/）
python tools/art/import_aurora_fx.py                 # 特效 -> league_aurora_fx / league_aurora_big
python tools/art/rig_aurora.py                       # 1 倍帧和 2.25 的原帧
python tools/art/ppu_restyle.py --hero aurora        # 外描边、脸的位置
python tools/art/ppu_hd.py --hero aurora             # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero aurora         # 待机和选人卡片的小动作
python tools/art/preview_aurora.py                   # 预览和演示 GIF
python addons/league_aurora/make_override.py         # 附加包的副本
```
