<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 希瓦娜 Shyvana

<img src="img/league_shyvana.png" alt="希瓦娜" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_shyvana` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 打野 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / Tank / Shield / CC |
| 高清帧 | PPU 1.5 |
| 附加包 | [希瓦娜附加包](#附加包)（`league_shyvana`） |

![希瓦娜演示](../preview/league_shyvana_showcase.gif)

其他预览：[逐帧预览](../preview/league_shyvana_frames.png)、[特效表](../preview/league_shyvana_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_shyvana.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.03 秒 · 攻击距离 25000*

挥击，附带目标1%最大生命值的物理伤害。烈火圣盾：每12秒的普攻获得70 + 50% 攻击力护盾和25%移速，2.5秒后爆炸，造成50+4%最大生命值魔法伤害。

### 技能1 · 焚焰打击

*冷却 1 秒 · 施放距离 30000 · 施放：指定目标 · 敌人（不含防御塔）*

斩击前方，造成25 + 110% 攻击力物理伤害；4秒内下次普攻横扫周围，造成25 + 110% 攻击力物理伤害；魔龙形态再下次普攻撕咬，造成40 + 110% 攻击力真实伤害。

### 技能2 · 爆炎吐息

*冷却 1 秒 · 施放距离 70000 · 施放：指定目标 · 敌人（不含防御塔）*

掷出火球，命中敌人或到达终点时爆炸，造成50+3%最大生命值魔法伤害并减速30%，持续2秒。魔龙形态下火球更大、穿透敌人，并留下燃烧的地面。

### 大招 · 魔龙降世

*冷却 30 秒 · 施放距离 90000 · 施放：指定目标 · 敌方英雄*

龙怒攒满时化身魔龙，飞向敌方英雄并沿途喷火，造成100+4%最大生命值魔法伤害并使其恐惧0.75秒。魔龙持续15秒，生命+30%，龙鳞铁衣使护甲和魔抗+30%。

### 数值

攻击力 100（每级 +20）、生命 1080（每级 +100）、护甲 34（每级 +7）、魔抗 26（每级 +4）、移速 1050（每级 +12）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 希瓦娜附加包

[希瓦娜附加包](../../addons/league_shyvana/README.md)：`league_shyvana` v0.1.0

|  | 主包（纯数据） | 附加包 |
|---|---|---|
| 龙形的样子 | 只有出招的动作是龙（`CasterAnimation` 播 `d_*`），站着、跑着、挨打、阵亡还是人形 | **整身变龙**：龙形期间（`league_shyvana_dg`，和龙形刚结束、还没播变回动作时的 `league_shyvana_was_dg`）站、跑、挨打、阵亡都换成 `d_idle` / `d_run` / `d_hit` / `d_dead`，普攻第一 tick 换成 `d_attack` |

## 相关脚本和素材

- [`tools/kit/build_shyvana.py`](../../tools/kit/build_shyvana.py)
- [`tools/kit/setup_shyvana.py`](../../tools/kit/setup_shyvana.py)
- [`tools/lol/extract_shyvana.py`](../../tools/lol/extract_shyvana.py)
- [`tools/art/preview_shyvana.py`](../../tools/art/preview_shyvana.py)
- [`tools/art/rig_shyvana.py`](../../tools/art/rig_shyvana.py)
- [`assets/source/shyvana/`](../../assets/source/shyvana)

## 开发记录

> 下面是原来 README 里「英雄：希瓦娜」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 打野（Melee，标签 AD / Melee / Tank / Shield / CC），第 147 位英雄。龙血武姬 希瓦娜：人形头戴深红龙角头冠、金色长发、钢青色胸甲和腿甲，双手是红色的龙爪，身后一条带金色尾鳍的龙尾；龙形是深红色的巨龙，背上一排橙黄色的火焰鬃毛，深紫色的翼膜，金色的爪子和尾鳍（10-20 之后分组的 F 组的打野）。照英雄联盟 16.20 重做后的技能。团战经理只有三个主动技能位，按我选的方案 A：技能 1 = Q 焚焰打击，技能 2 = E 爆炎吐息，大招 = R 魔龙降世；被动龙鳞铁衣折进龙形，W 烈火圣盾在普攻里。技能名照英雄联盟 16.20 的 Data Dragon（五种语言） |
| 两种形态 / 龙怒 | **龙怒**（魔龙降世的被动）：人形时普攻打中、焚焰打击的每一击、爆炎吐息、烈火圣盾的爆炸各攒一格，10 格攒满身上冒火，可以放大招；没满时每格 6 秒不攒就掉，攒满后保持 30 秒、每次打中都续上（英雄联盟的龙怒满了留到变身）。**龙形**持续 15 秒：生命、护甲、魔抗各 +30%（龙鳞铁衣折进来：英雄联盟按击杀叠护甲魔抗，主包的数据看不到击杀）、射程 +10000；结束后下一个动作变回人形（普攻放变回人形的动作），没打完的焚焰打击三连作废 |
| 普攻 / W | 人形挥爪、龙形一爪抓下，100% 攻击，加上焚焰打击的被动：目标最大生命 1% 的物理伤害。**烈火圣盾**不占技能位：每 12 秒的第一下普攻裹上火焰护盾（70 + 50% 攻击）、移速 +25%，2.5 秒后在身边 33000 内炸开：50 + 自身最大生命 4% 的魔法伤害；龙形时炸到敌方英雄回 50 + 50% 攻击的生命 |
| 技能1 | **焚焰打击**（冷却 6 秒，对 `EnemyWithoutTower`，野怪兵线也打）：一爪斩出火焰爪痕，前方 12000 处 16000 内 25 + 110% 攻击；4 秒内下一下普攻变成**第二击**：身边 26000 内 25 + 110% 攻击；龙形时（翼击 → 尾扫）第二击之后再下一下普攻是**撕咬**：40 + 110% 攻击的真实伤害 |
| 技能2 | **爆炎吐息**（冷却 10 秒，射程 70000）：人形掷出火球，打中第一个敌人或飞到尽头炸开（15000 内）：50 + 自身最大生命 3% 的魔法伤害、减速 30% 2 秒；龙形喷出大火球，穿过一路上的敌人（每人一半伤害），飞到 90000 尽头炸开（30000 内 65 + 自身最大生命 4%、减速），落点的地面烧 2 秒（英雄联盟的火路，区域跟不了弹道，烧在终点） |
| 大招 | **魔龙降世**（冷却 30 秒，射程 90000，只对敌方英雄）：照英雄联盟只有龙怒满了才能放；不满时什么也不放，10 秒后再试（纳尔的空放）；这 10 秒里攒满就立刻能放。化身巨龙 15 秒，0.67 秒免控，飞到目标英雄身上、一路喷火：100 + 自身最大生命 4% 的魔法伤害并恐惧 0.75 秒 |
| 连招 | 「有连招要做连招」：**Q → 普攻 → 普攻**（焚焰打击三连：翼击 / 尾扫 / 撕咬），**R → W → Q**（落地马上烈火圣盾，0.33 秒后龙形焚焰打击；冷却好了才接） |
| 附加包 | 可选的附加包 [`addons/league_shyvana`](../../addons/league_shyvana/README.md)（在附加包合集里，原生代码，主包不装它也完整；不换英雄数据）：**整身变龙**（用户 2026-10-24：「龙女变成龙不能保持住？」——主包里化龙后站着、跑着、挨打、阵亡还是人形，只有出招是龙形；附加包照纳尔的做法把龙形期间的 idle / run / hit / dead 换成 `d_idle` / `d_run` / `d_hit` / `d_dead`）。以后还可以做：龙鳞铁衣按击杀叠层、AI 连招 |
| 数值 | 攻击 100（+20）、生命 1080（+100）、护甲 34（+7）、魔抗 26（+4）、移速 1050（+12）、射程 25000（龙形 +10000） |
| 平衡 | 打野位对五个基础英雄（demon / circus_blade / hunter / inquisitor / ninja），三套阵容、两边各打，10 分钟经典引擎模拟两批 24 个种子（种子 1–24 / 25–48）。合并时的数字是照沃里克和纳尔起草、没跑过模拟的：**−1.36 / −1.65**，伤害 4682，远低于别的打野。原因是龙怒：满怒气只留 6 秒、不会续，过了就清零，大招空放后要 10 秒才再试，每局攒满 10.7 次只变龙 1.2 次。2026-10-22 改成满怒气保持 30 秒、打中就续，空放后的 10 秒里攒满立刻能放：每局变龙 2.9 次，−1.13 / −0.98；再把焚焰打击冷却 8 → 6 秒、两击 90% → 110% 攻击，攻击 90（+18）→ 100（+20）：**−0.06 / +0.22**，每局伤害约 6100、K/D/A 1.9 / 1.3 / 3.6，变龙 2.7 次。同样的种子上狼人 +0.32 / +0.11、男枪 +0.65 / +0.62、潘森 +0.62 / +0.51，和狼人同一档 |
| 精灵图（高清帧 PPU 1.5） | Codex 第 0 步画了人形和龙形（3/4 和侧面），用户选「人42 龙48 PPU1.5」；第 1 步用户选「人形用 A-2，龙形用 D-1，龙就按画的大小，只做四分之三侧面」：她 40 × 63（42 游戏像素），龙 107 × 64（照 Codex 画的大小，43 游戏像素）。龙的动作我照英雄联盟的动画摆（[`tools/art/rig_shyvana.py`](../../tools/art/rig_shyvana.py)）：身体、头和腿按整格移动，翅膀、尾巴和下颌转角度时从 Codex 的原图按那个角度重画再读回格子（不在粗格子上转）；转身甩尾整只镜像；翅膀拍向前时留在头后面（挡在前面会盖住脸）。人形的跳斩、空翻甩尾、掷火球、跃起化龙、倒地让 Codex 照骨架画了 14 个关键姿势（[`tools/art/pack_shyvana_poses.py`](../../tools/art/pack_shyvana_poses.py)，骨骼长度是定稿的），[`tools/art/design_shyvana_poses.py`](../../tools/art/design_shyvana_poses.py) 认出每张里定稿的头、按头量比例：Codex 的身子比定稿大两成，按 1.2 倍的格子读回，换上定稿的头（一张脸、一个体型）；每个姿势按骨架定的头的位置放（按脚放，跑步时身子每步前后跳 16 格）。Q 的火焰爪痕和龙的翼击气浪画进帧里（红方也朝前，龙的气浪在身子后面、不挡脸）。龙形阵亡是一道闪光后变回人倒下。龙形跑步 2026-10-24 重做（用户：「这走路腿都不动的？」「走路时腿部变形了 你应该能改好 不用依赖codex」）：照赫卡里姆的做法，身体照原图盖在腿上面，四条腿在下面依次错开迈步（四拍，各差四分之一圈）；爪子是原图的格子整块移动（贴地往后蹬 5 帧、抬起往前迈 3 帧），腿绕髋 / 肩转向爪子，按角度从 Codex 原画重画（同翅膀、尾巴），右前腿也是一整条直腿（在肘部折弯时成了 L 形：「右前脚有略微变形」） |
| 特效 | 26 张特效（[`tools/art/pack_shyvana_fx.py`](../../tools/art/pack_shyvana_fx.py) 的提示词，参考是英雄联盟里希瓦娜自己的贴图），用户用 Gemini 画的 JPG（「龙女的技能特效在这里面」），[`tools/art/process_shyvana_fx.py`](../../tools/art/process_shyvana_fx.py) 从每帧自己的边缘往里抠背景（只按边上的灰色抠：护盾淡金色的外圈碰到边也留着）、清掉圆环、护盾和烟雾围住的黑底、缩到格子（火星只认火星大小的，整个圆环不再在中心点一个点）、镜像；[`tools/art/import_shyvana_fx.py`](../../tools/art/import_shyvana_fx.py) 按技能放好，地上的圆环按 Gemini 画的椭圆中心放在脚下，对称的特效宽度取奇数、绕她的站位点正好对称；龙的火球只循环前三帧（第四帧的芯是暗的，循环时一闪一闪） |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_shyvana.py`](../../tools/lol/extract_shyvana.py)）：人形和龙形的普攻、焚焰打击三击、烈火圣盾的护盾 / 爆炸 / 回血、爆炎吐息的火球和爆炸（两种形态）、魔龙降世、化龙 / 变回人形、龙怒满了，四句台词（大招没有单独的台词，用龙的嘶吼） |
| 图标 | 官方技能图标（焚焰打击、爆炎吐息、魔龙降世），从本地客户端取 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_shyvana.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_shyvana.py                   # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_shyvana.py                   # 五种语言的文字、音效配置、共享文件里她的键（脸 2,-33，卡片 -8）
python tools/art/design_shyvana_model.py            # Codex 第 1 步的造型读回（A-2 / D-1）
python tools/art/design_shyvana_poses.py            # Codex 的 14 个姿势读回（--rematch 重新找头）
python tools/art/process_shyvana_fx.py --src <26 张 JPG 按顺序命名 g00.jpg–g25.jpg 的文件夹>   # Gemini 的特效 -> codex_fx/
python tools/art/import_shyvana_fx.py               # 特效 -> league_shyvana_fx / league_shyvana_big
python tools/art/rig_shyvana.py                     # 1 倍帧和 1.5 的原帧（Q 的斩击按 assets/source/native/shyvana_bake.json 画进去）
python tools/art/ppu_restyle.py --hero shyvana      # 外描边、脸的位置
python tools/art/ppu_hd.py --hero shyvana           # hd_ / lo_ 帧
python tools/art/preview_shyvana.py                 # 预览和演示 GIF
```

美术提示词见 [`assets/source/shyvana/`](../../assets/source/shyvana) 里的 `PICTURE_PROMPT.md`、`MODEL_PROMPTS.md`、`POSE_PROMPTS.md`、`PROMPTS_FX.md`。

逐帧预览：[`docs/preview/league_shyvana_frames.png`](../preview/league_shyvana_frames.png?v=1024a)，特效：[`docs/preview/league_shyvana_effects.png`](../preview/league_shyvana_effects.png?v=1021a)
