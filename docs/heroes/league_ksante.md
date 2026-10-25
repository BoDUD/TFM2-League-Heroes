<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 奎桑提 K'Sante

<img src="img/league_ksante.png" alt="奎桑提" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_ksante` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 上单 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / Tank / Shield / CC |
| 高清帧 | PPU 1.2（画成 90%） |
| 附加包 | [奎桑提附加包](#附加包)（`league_ksante`） |

![奎桑提演示](../preview/league_ksante_showcase.gif)

其他预览：[逐帧预览](../preview/league_ksante_frames.png)、[特效表](../preview/league_ksante_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_ksante.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动

*攻击间隔 1.2 秒 · 攻击距离 25000*

陀斧重击。血性本能：技能命中后，下一次普攻额外造成15 + 目标2%最大生命值的物理伤害。

### 技能1 · 无双陀斧

*冷却 4 秒 · 施放距离 30000 · 施放：指定目标 · 敌人（不含防御塔）*

向前砸地，造成35 + 70% 攻击力 + 2% 最大生命物理伤害并减速50%。命中叠一层，两层时变成冲击波，拉回路径上的敌人，造成55 + 70% 攻击力 + 3% 最大生命物理伤害。

### 技能2 · 辟路先锋

*冷却 11 秒 · 施放距离 45000 · 施放：指定目标 · 敌方英雄*

蓄力，受到伤害降低25%并获得护盾，然后冲撞，造成30 + 60% 攻击力 + 目标6%最大生命值的物理伤害，击退并晕眩0.83秒。全盛时不击退晕眩，改为9%。

### 大招 · 傲岸雄姿

*冷却 50 秒 · 施放距离 30000 · 施放：指定目标 · 敌方英雄*

盾击敌方英雄，造成100 + 80% 攻击力物理伤害并击退，追上去砸地造成60 + 60% 攻击力 + 4% 最大生命物理伤害，进入全盛姿态15秒：攻击+20%、攻速+40%、吸血20%、技能冷却缩短，护甲和魔抗-25%。

### 数值

攻击力 82（每级 +9）、生命 1220（每级 +115）、护甲 42（每级 +8）、魔抗 30（每级 +4）、移速 1000（每级 +10）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 奎桑提附加包

[奎桑提附加包](../../addons/league_ksante/README.md)：`league_ksante` v0.1.0

|  | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 全盛的样子 | 只在出招时是全盛姿态 | **整身换姿态**：全盛的 15 秒里站着、走着、挨打都是全盛姿态（`ao_idle` / `ao_run` / `ao_hit`），普攻第一下也是 |

## 相关脚本和素材

- [`tools/kit/build_ksante.py`](../../tools/kit/build_ksante.py)
- [`tools/kit/setup_ksante.py`](../../tools/kit/setup_ksante.py)
- [`tools/lol/extract_ksante.py`](../../tools/lol/extract_ksante.py)
- [`tools/art/preview_ksante.py`](../../tools/art/preview_ksante.py)
- [`tools/art/rig_ksante.py`](../../tools/art/rig_ksante.py)
- [`assets/source/ksante/`](../../assets/source/ksante)

## 开发记录

> 下面是原来 README 里「英雄：奎桑提」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 上单（Melee，标签 AD / Melee / Tank / Shield / CC），第 151 位英雄（G 组）。纳祖芒荣耀 奎桑提：高大的黑人战士，黑色短脏辫、络腮胡、金耳环，深红长外套上金色的护肩和臂甲、蓝色围巾、紫色下摆，双手各提一把和他一样高的青灰色石质陀斧（嵌着青色的水晶、金色的箍）；**全盛**时陀斧的石壳碎掉，只剩两根细长的水晶棍，他弓背半蹲、长棍拖地 |
| 被动 | **血性本能**：Q、W、R 打中的敌人被标记 4 秒，他下一次普攻对它多打 15 + 目标最大生命 2% 的物理伤害（脚下亮一圈标记） |
| 技能1 | **无双陀斧**（冷却 4 秒，对 `EnemyWithoutTower`，野怪兵线也打）：一斧砸地，前方 14000 处半径 15000 内 35 + 70% 攻击 + 自身最大生命 2%（英雄联盟加的是额外护甲魔抗，数据读不到，换成生命），减速 50% 0.5 秒；打中东西攒一层，6 秒内攒满两层下一次是**第三下**：两把陀斧一起砸地，冲击波往前滚 70000（宽 9000），路上每个敌人 55 + 70% 攻击 + 自身最大生命 3%，并被拉向他 |
| 技能2 | **辟路先锋**（冷却 11 秒，射程 45000，只对敌方英雄；英雄联盟 E 大步驰援的护盾并进来）：顶着陀斧蓄力 0.75 秒，期间受到的伤害 -25%，得到 70 + 50% 攻击的护盾（2 秒），然后冲撞到英雄身上：身边 16000 内 30 + 60% 攻击 + 目标最大生命 6%，击退并晕眩 0.83 秒。全盛时蓄力只要 0.4 秒、减伤 50%，不击退不晕眩，改打目标最大生命 9% |
| 大招 | **傲岸雄姿**（冷却 50 秒，射程 30000，只对敌方英雄）：陀斧一推把英雄撞飞（100 + 80% 攻击，击退、晕眩 0.5 秒；2026-10-22 用户：「踢得更远，把对面的人踢离他的队友」——踢飞距离加倍，追击冲刺也更快、追得到），陀斧碎掉、进入**全盛**，追上去砸地（60 + 60% 攻击 + 自身最大生命 4%）。全盛 15 秒：攻击 +20%、攻速 +40%、吸血 20%、穿甲 30，技能冷却 -33%，护甲魔抗 -25%（英雄联盟：丢掉 85% 的额外双抗） |
| 连招 | 「有连招要做连招」：**Q → Q → Q3**（两层后第三下拉人），**Q3 → W**（冲击波打中英雄后 3 秒内放 W，蓄力只要 0.13 秒，把拉过来的人直接撞走），**R → W**（砸地后 W 的剩余冷却降到十分之一、3 秒内蓄力 0.13 秒：全盛的冲撞马上接上），**W → Q**（冲撞到英雄算一层 Q），每个技能打中都给下一次普攻挂上被动 |
| 附加包 | [`addons/league_ksante`](../../addons/league_ksante/README.md)（在附加包合集里，原生代码，主包不装它也完整；用户选全盛「单独一套」）：全盛的 15 秒里**站着、走着、挨打也是全盛姿态**（`ao_idle` / `ao_run` / `ao_hit`，普攻第一下也换），主包只在出招时是全盛动作 |
| 数值 | 攻击 82（+9）、生命 1220（+115）、护甲 42（+8）、魔抗 30（+4）、移速 1000（+10）、射程 25000 |
| 平衡 | 经典引擎模拟（上路，对战士、处刑者、骑士、狂战士、枪兵、长柄战士）：草稿 -0.46；伤害加上去 +0.38；全盛 -25%、R 50 秒、W 11 秒、护甲 42 时 +1.18 / +1.56（种子 1–8 / 9–16）；看了事件记录，AI 总是 W → Q → Q3，Q3 → W 的窗口多半刚放完 W 用不上，所以只给 R → W 加了冷却返还；定稿 Q 35、W 30、砸地 60：+1.28 / +2.22（同一天奥恩 +1.86） |
| 精灵图（高清帧 PPU 1.2） | Codex 第 0 步画了普通和全盛两种姿态；用户：「奎桑提用陀斧顶到脚底 48 游戏像素，PPU 1.5，只做四分之三侧面」，第 1 步选「普通用 A-2，全盛用 O-1」「全盛裁到 56 格，和普通姿态身体一样大」：普通 65 × 72，全盛 81 × 56。英雄联盟的动作要抡、砸、推两把大陀斧，Codex 照定稿骨长摆的 29 副骨架画了 27 个关键姿势（[`tools/art/pack_ksante_poses.py`](../../tools/art/pack_ksante_poses.py)），[`tools/art/design_ksante_poses.py`](../../tools/art/design_ksante_poses.py) 读回：Codex 把人画得比骨架大约 1.25 倍、头又偏小，所以格子按**身体面积**定（去掉头、陀斧和描边，和定稿比），再把定稿自己的头贴回去（每帧一张脸）。[`tools/art/rig_ksante.py`](../../tools/art/rig_ksante.py) 照英雄联盟的动作排帧：普攻后拉再前推、Q 跳起砸地（第二下换另一把）、Q3 双斧跳砸、W 顶墙蓄力和冲撞、R 盾推（这一下陀斧碎掉，全盛的爆光盖住变身）→ 全盛蹲伏、腾空举棍、落地砸下，全盛的普攻横扫、跳砸、交叉举棍、冲锋；每个姿势按骨架定头的位置、最低点落地。挥砍弧、Q 的地裂、Q3 的爆石、W 的扬尘、全盛的横扫画进他的帧（[`assets/source/native/ksante_bake.json`](../../assets/source/native/ksante_bake.json)：地裂从陀斧头往前跑，横扫从身后绕过不盖住身体）。待机是定格加小动作（W 顶墙、普攻蓄力；全盛：交叉举棍、抡棍）。2026-10-22 用户：「奎桑提像素也太高了」，选了 **PPU 1.2**（游戏里一样大，格子粗一些）。同一天晚上用户：「奎桑提的模型在游戏局内也太大了 还有走路跳动频率太高 和之前索拉卡一样」「还有奎桑提的头像位置不对」——局内缩到 **90%**（hd.rs SIZES，从 0.9、0.85、0.8 里选，帧往下挪 2 格踩在地上），跑步（普通和全盛）每帧 110 → 150 毫秒（一圈 0.44 → 0.6 秒，索拉卡的做法），头像取景点从眼睛挪到头顶下面（0, -36 → 1, -37：按 90% 换算，原版英雄放在头顶） |
| 特效 | 19 张特效（[`tools/art/pack_ksante_fx.py`](../../tools/art/pack_ksante_fx.py) 的提示词，参考是英雄联盟里奎桑提自己的贴图），用户用 Gemini 画的 JPG（「奎桑提的特效包在这里面」），[`tools/art/process_ksante_fx.py`](../../tools/art/process_ksante_fx.py) 读回游戏大小（地裂的全景图整张读、当成沿地面跑的波；Q3 爆石边上被尺子一样画直的沙边弄毛；棋盘格灰底和网格边上爬进来的细条抠掉；全盛爆光的黑晕剥掉；W 落地石块上像眼睛的洞填上），[`tools/art/import_ksante_fx.py`](../../tools/art/import_ksante_fx.py) 按技能放好：`league_ksante_fx` 11 张、`league_ksante_big` 8 张 |
| 音效 | 英雄联盟的音效和配音（[`tools/lol/extract_ksante.py`](../../tools/lol/extract_ksante.py)，vgmstream 解码）：普攻两种姿态、被动、Q 三下的出手和打中、W 蓄力 / 冲撞 / 落地 / 打中、R 盾推 / 追击 / 砸地、进入全盛，四句台词；照奥莉安娜和佐伊的音量标准一开始就做响（音效峰值 +8 dB，台词不动） |
| 图标 | 官方技能图标（无双陀斧、辟路先锋、傲岸雄姿），从本地客户端取 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_ksante.py --lol "D:\WeGameApps\lol" --vgmstream <vgmstream-cli.exe>
python tools/kit/build_ksante.py                    # 技能数据，数字都在脚本的参数表 P 里
python tools/kit/setup_ksante.py                    # 五种语言的文字、音效配置、共享文件里他的键（脸 0,-36，卡片 -6）
python tools/art/design_ksante_model.py             # Codex 第 1 步的造型读回（A-2 / O-1）
python tools/art/design_ksante_poses.py             # Codex 的 27 个姿势读回（--rematch 重新找头）
python tools/art/process_ksante_fx.py --src <19 张 JPG 按顺序命名 g00.jpg–g18.jpg 的文件夹>   # Gemini 的特效 -> codex_fx/
python tools/art/import_ksante_fx.py                # 特效 -> league_ksante_fx / league_ksante_big
python tools/art/rig_ksante.py                      # 1 倍帧和 1.5 的原帧（--review DIR 先看；特效按 ksante_bake.json 画进去）
python tools/art/ppu_restyle.py --hero ksante       # 外描边、脸的位置
python tools/art/ppu_hd.py --hero ksante            # hd_ / lo_ 帧
python tools/art/hero_reels.py --hero ksante        # 待机和选人卡片的动画（挑的小动作在 hero_reels.json）
python tools/art/preview_ksante.py                  # 预览和演示 GIF
```

美术提示词见 [`assets/source/ksante/`](../../assets/source/ksante) 里的 `PICTURE_PROMPT.md`、`MODEL_PROMPTS.md`、`POSE_PROMPTS.md`、`RUN_REDO_PROMPTS.md`、`PROMPTS_FX.md`。

逐帧预览：[`docs/preview/league_ksante_frames.png`](../preview/league_ksante_frames.png?v=1022a)，特效：[`docs/preview/league_ksante_effects.png`](../preview/league_ksante_effects.png?v=1022a)
