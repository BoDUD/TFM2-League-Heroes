<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 韦鲁斯 Varus

<img src="img/league_varus.png" alt="韦鲁斯" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_varus` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | ADC |
| 分类 / 标签 | 射手（Range） · AD / Range / CC |
| 高清帧 | PPU 1.35 |
| 附加包 | [韦鲁斯枯萎附加包](#附加包)（`league_varus_blight`） |

![韦鲁斯演示](../preview/league_varus_showcase.gif)

其他预览：[逐帧预览](../preview/league_varus_frames.png)、[特效表](../preview/league_varus_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_varus.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动（被动「复仇之欲」）

*攻击间隔 0.93 秒 · 攻击距离 57500*

射箭攻击，附带20魔法伤害，命中英雄叠一层枯萎（最多3层）。被动复仇之欲：击杀英雄后攻速+60%，击杀小兵野怪+20%，持续5秒。

### 技能1 · 穿刺之箭

*冷却 6.67 秒 · 施放距离 95000 · 施放：方向 · 敌人（不含防御塔）*

拉弓射出穿透箭：射程内有敌方英雄时蓄满力，造成110 + 130% 攻击力物理伤害，否则快速出手、伤害较低；之后每个敌人伤害递减。命中英雄时引爆枯萎：每层3%最大生命值真实伤害并缩短技能冷却。每40秒一次蓄满的箭再加6%。

### 技能2 · 恶灵箭雨

*冷却 8 秒 · 施放距离 90000 · 施放：地点 · 敌人（不含防御塔）*

向目标区域射下箭雨，造成70 + 90% 攻击力物理伤害并引爆枯萎；地面腐化4秒，其中的敌人减速30%、受到的治疗降低40%。

### 大招 · 腐败锁链

*冷却 60 秒 · 施放距离 100000 · 施放：指定目标 · 敌方英雄*

射出腐败锁链，命中第一个敌方英雄：150 + 80% 攻击力物理伤害、禁锢2秒、叠满3层枯萎；锁链随后扩散到附近的敌方英雄，禁锢1.5秒。

### 数值

攻击力 100（每级 +20）、生命 950（每级 +90）、护甲 20（每级 +7）、魔抗 15（每级 +3）、移速 900（每级 +9）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 韦鲁斯枯萎附加包

[韦鲁斯枯萎附加包](../../addons/league_varus_blight/README.md)：`league_varus_blight` v0.1.1

|  | 主包（纯数据） | 装了附加包 |
|---|---|---|
| 枯萎记在哪里 | 韦鲁斯身上（一共最多 3 层） | 每个敌方英雄自己身上（各最多 3 层，6 秒） |
| 引爆 | Q、E、R 打中英雄时按他自己的层数，每层 3% 最大生命真实伤害 | 按被打中的那个人身上的层数，数字一样 |
| 引爆返还冷却 | 每层 13%（冷却倍率，R 也一起压） | 每层把 Q、E 的剩余冷却减 13%，不压 R |
| R | 引爆后再叠满 3 层 | 一样（叠在被锁住的人身上） |

## 相关脚本和素材

- [`tools/kit/build_varus.py`](../../tools/kit/build_varus.py)
- [`tools/kit/setup_varus.py`](../../tools/kit/setup_varus.py)
- [`tools/lol/extract_varus.py`](../../tools/lol/extract_varus.py)
- [`tools/art/preview_varus.py`](../../tools/art/preview_varus.py)
- [`tools/art/rig_varus.py`](../../tools/art/rig_varus.py)
- [`tools/art/import_varus.py`](../../tools/art/import_varus.py)
- [`tools/art/design_varus.py`](../../tools/art/design_varus.py)
- [`assets/source/varus/`](../../assets/source/varus)

## 开发记录

> 下面是原来 README 里「英雄：韦鲁斯」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | ADC（射手，分类 Range），用户 10 月 2 日排的第十二组的 ADC（同组：瑟提、伊芙琳、丽桑卓、牛头）。惩戒之箭：平 A 给敌方英雄叠枯萎，Q、E、R 打中时引爆，Q 拉满弓穿透一条线，E 箭雨减速重伤，R 触须禁锢并扩散 |
| 普攻 / W / 被动 | 普攻是一支追踪的箭，100% 攻击力的物理伤害，射程 57500，攻击间隔 56 tick（第 9 tick 放箭，从弓的高度飞出）。W「枯萎箭袋」并入普攻（用户选的）：每支箭附带 20 魔法伤害；打中敌方英雄叠一层枯萎（最多 3 层，6 秒，层数记在他自己身上，同卡莎的被动——这里读不到目标身上的层数），头顶亮起对应层数的标记。Q、E、R 打中英雄时引爆：每层造成目标最大生命值 3% 的真实伤害（英雄联盟是魔法伤害，但只有真实伤害能按最大生命值算），Q、E 引爆时每层把两个小技能的冷却缩短 13%（英雄联盟原版的数；引擎的冷却上限对所有技能一起生效，R 的剩余冷却也会压到同样比例，算是小小的额外收益）。W 的主动「枯萎之箭」并入 Q：每 40 秒一次，拉满弓的 Q 打中英雄时额外造成最大生命值 6% 的真实伤害（英雄联盟是已损生命值，这里读不到）。被动「复仇之欲」：他打死敌方英雄后 5 秒内攻速 +60%，打死小兵或野怪 +20%（没有「有人死了」的事件，用金克丝那套击杀检测） |
| 技能1 | Q「穿刺之箭」：冷却 400 tick（约 6.7 秒），也对小兵和野怪放。智能蓄力（用户选的）：施放时 130000 内有敌方英雄就拉满弓 66 tick（1.1 秒，前后分腿的弓步），放箭瞬间朝射程内英雄当时的位置射（直线，可以躲），110 + 130% 攻击力的物理伤害，射程 140000；只有小兵野怪时快速出手（24 tick），伤害 60%、射程 100000。箭穿透一条线，第一个敌人全额，第二个 80%，之后 60% |
| 技能2 | E「恶灵箭雨」：冷却 480 tick（8 秒），射程 90000，也对小兵和野怪放。朝目标所在的位置射一箭上天，20 tick 后箭雨落下（半径 28000，落点是出手时的位置，可以躲），70 + 90% 攻击力的物理伤害并引爆枯萎；地面腐化 4 秒，站在上面的敌人减速 30%、受到的治疗降低 40%（重伤） |
| 大招 | R「腐败锁链」：冷却 60 秒，只对英雄放。第 15 tick 甩出触须，朝目标当时的位置飞（穿过小兵，停在第一个敌方英雄身上，可以躲）：150 + 80% 攻击力的物理伤害，禁锢 2 秒，先引爆已有的枯萎再给他叠满 3 层；30 tick 后腐化从他脚下扩散（半径 55000），附近的敌方英雄都被禁锢 1.5 秒 |
| 附加包 | 可选的附加包 [`addons/league_varus_blight`](../../addons/league_varus_blight/README.md)（在附加包合集里，原生代码，主包不装它也完整）：枯萎照英雄联盟记在每个敌方英雄自己身上，Q、E、R 引爆的是打中的那个人身上的层数（主包记在韦鲁斯身上，打 A 叠的层会在 B 身上引爆）；引爆返还的冷却只给 Q、E |
| 连招 | 用户要求：「有连招要做连招」「都要帮我补」。英雄联盟的 **R→E / Q**：腐败锁链打中敌方英雄的下一 tick（那个英雄还活着），他身上挂一个 2 tick 的 `skill_cooldown_mult` 10000（同一个 buff 带 `ult_cooldown_mult` −10000 抵掉，R 自己的 60 秒不动）：Q 和 E 的剩余冷却压到 3–4 tick，R 的 30 tick 动作结束前就好了，AI 接着对被禁锢 2 秒的英雄放 E（出手 30 tick 后落下）和拉满弓的 Q（第 66 tick 放箭），都在禁锢里打中，引爆刚叠满的 3 层枯萎（引爆照旧返还冷却）。Q、E 本来就好了就什么都不变；锁链打死目标不返还。每次打中英雄的 R 最多多一次 Q 和一次 E。数据由 [`tools/fix/combo_varus.py`](../../tools/fix/combo_varus.py) 改（生成脚本之后还有别的脚本改过他的数据，所以不重新生成） |
| 数值 | 攻击 100（+20）、生命 950（+90）、护甲 20（+7）、魔抗 15（+3）、移速 900（+9）。数值是自己设计的，用 SDK 对战模拟调：下路，对 4 个原版 ADC（`gunner`、`soldier`、`archer`、`gambler`），3 套阵容、两边各打，10 分钟。初稿 +0.82；攻击间隔 62 → 56、生命 900 → 950（+1.16 / +1.85），再把 Q 冷却 480 → 400、E 冷却 540 → 480 后种子 1–24 +1.63、25–48 +1.91（本包的烬 +1.43 / +2.08、希维尔 +2.50 / +1.83）。只加 Q 伤害（140 + 150%）、枯萎 4% 或攻击 106 都不如这一版 |
| 亚索联动 | R 的禁锢是亚索大招要的控制：韦鲁斯下路、亚索同队时，亚索每局 R 到被控英雄 0.71 次（同一批原版枪手 0.19、烬 1.17）——R 要打中英雄才禁锢、冷却又长，亚索不用调 |
| 精灵图 | 9 个动作 52 帧：待机、移动、普攻、Q 满蓄力（`skill`）、Q 快速出手（`skill_quick`，从满蓄力那条里剪的第 1–3、6–7 帧）、E、R、受击、死亡。造型 29 × 40 px，26 色。待机 6 帧同一张、不呼吸；头像截取点 (−1, −37)，待机最高点 −28，不用选人卡片位置 |
| 特效 | Codex 生图的 24 张（`import_varus.py` 缩成游戏像素）：`league_varus_fx` 普攻的箭、放箭闪光、命中，枯萎 1/2/3 层标记和引爆，枯萎之箭的红光和爆发，Q 的蓄力光（快速出手用前 3 帧）、放箭爆闪、穿刺之箭（快速出手同一张）、命中，E 朝天射的闪光、命中、腐化地面上的减速重伤标记，R 甩出、触须、命中、扩散命中、禁锢的触须，被动的攻速光环；`league_varus_big` 箭雨、腐化地面、锁链扩散、被动爆发 |
| 音效 | 英雄联盟的音效和配音（`tools/lol/extract_varus.py`）：普攻放箭、飞出、命中，枯萎引爆和枯萎之箭，Q 拉弓、蓄力、放箭、飞出、命中，E 出手、箭雨落地、命中，R 出手、飞出、命中、扩散，被动；Q、E、R 各一句中文配音。版权属于 Riot Games，**不提交到仓库**，按下面的命令在本地生成 |
| 图标 | 官方技能图标（Q / E / R），从本地客户端提取，缩到 64×64 |
| 修正（0.170.2） | 用户让查附加包日志时在芸阿娜身上发现：引擎给大招冷却封顶时，把 `skill_cooldown_mult` 也算进去（技能冷却削减同时压大招）。引爆枯萎每层返还 13% 基础技能冷却时，大招冷却也被一起压了。同一个 buff 加上相同大小的负 `ult_cooldown_mult` 抵掉（[`tools/fix/ult_cooldown_offset.py`](../../tools/fix/ult_cooldown_offset.py) / 生成脚本），只减原本要减的技能。经典模拟（8 个种子，三套阵容两边各打） +0.70 → +0.65，每局开大 4.5 → 4.4 次 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_varus.py --lol "D:\WeGameApps\lol" --vgmstream "<vgmstream-cli.exe 路径>"
python tools/kit/build_varus.py        # 技能数据，数字都在脚本的参数表 P 里；--nodes 看每棵技能树的节点数
python tools/kit/setup_varus.py --face=-1,-37   # 五种语言的文字、音效配置、共享文件里他的键
python tools/art/design_varus.py       # 造型：Codex 原稿 A 按格子读回、按面积缩到 40 行、清掉零散黑点、修胸口皮带和腿
python tools/lol/native_pose.py assets/source/varus/poses.json --out <渲染文件夹>   # 动作参考帧
python tools/art/rig_varus.py          # 动作：每帧都是造型本身，手臂、弓按动作摆
python tools/art/import_native.py --hero varus
python tools/art/import_varus.py       # 特效；--raw <Codex 的特效交付文件夹> 先把生图原稿缩成游戏尺寸的原尺寸条
python tools/art/preview_varus.py
python tools/art/pack_varus_ppu.py --out <文件夹>   # 高清造型（PPU 1.5）：给 Codex 的设计图包
python tools/art/design_varus_hd.py --gen 2   # 设计图按自己的格子读回（58 × 59）
python tools/lol/league_joints.py assets/source/varus/poses.json --out assets/source/varus/hd   # 英雄联盟每帧的关节（跑步、死亡）
python tools/art/rig_varus_hd.py   # 高清帧（会重写 1 倍的图，不再跑上面的 rig_varus / import_native），写 assets/source/ppu/orig/；--review <文件夹> 先看，--parts <文件夹> 看关键姿势
python tools/art/ppu_restyle.py --hero varus
python tools/art/ppu_hd.py --hero varus
python tools/art/hero_reels.py --hero varus   # 待机和选人卡片的小动作
python tools/art/preview_varus.py   # 高清帧的预览
```

美术（原画的提示词见 [`assets/source/varus/PICTURE_PROMPT.md`](../../assets/source/varus/PICTURE_PROMPT.md)，造型的见 [`MODEL_PROMPTS.md`](../../assets/source/varus/MODEL_PROMPTS.md)，动作的见 [`MODEL_STRIPS.md`](../../assets/source/varus/MODEL_STRIPS.md)，特效的见 [`PROMPTS_FX.md`](../../assets/source/varus/PROMPTS_FX.md)；Codex 的交付说明在 [`codex_picture/`](../../assets/source/varus/codex_picture)、[`codex_model/`](../../assets/source/varus/codex_model)、[`codex_strips/`](../../assets/source/varus/codex_strips)、[`codex_fx/`](../../assets/source/varus/codex_fx)）：

- 原画：Codex 画了 A（英雄联盟的待机：左手提弓垂在腿边）、B（Q 拉弓蓄力），用户选 A。渲染参考时弓是皮肤里标成「隐藏」的子网格 `Weapon`，所以不能加 `--hide-submeshes`。
- 造型：Codex 按游戏尺寸画的 40 行 A/B 是隔行取样缩出来的，碎成杂点；它的生图原稿 A 按自己的格子（19 px）读回是 52 × 73，干净。整行删最少只能删到 42 行（73 行不能连删两行），减半是 38 行；四种缩法（减半、删到 42 / 44 行、按面积投票缩到 40 行）给用户挑，用户选按面积缩的 40 行（「这个最好 很不错」）：原稿的颜色先用 k-means 归成 24 色，再每格取覆盖面积最大的颜色。之后按用户的反馈逐格修：身体里孤立的黑点换成周围的颜色（脸不动），胸口护符旁那块黑（原画的皮带）改成深灰褐皮带色，腿上夹在中间的黑格换成腿甲的颜色，左大腿根的凹口补平，右腿从小腿往下往里收一格（出招时腰和腿对齐）。
- 动作参考（`poses.json`）：镜头 yaw 45、pitch 20，镜像；头 2.6 倍、腿 0.85；高度 40。移动用英雄联盟的 `varus_run`（1.07 秒一个循环，8 帧 × 133 ms）；普攻第 3 帧（第 9 tick）放箭，Q 第 6 帧（第 66 tick），E 第 3 帧（第 10 tick），R 第 3 帧（第 15 tick），和技能数据一致。
- 动作：Codex 的动作条（[`codex_strips/`](../../assets/source/varus/codex_strips)）是用造型的部件拼的：射箭的手臂是一根肉色长条、弓下面留着碎点、E 的弓转成一串碎块、死亡时躺着的弓是一条虚线、跑步和蹲下的腿是细棍。用户：「有奇怪的地方你帮我修复好」。改成全部用造型自己的部件摆（`rig_varus.py`）：弓、持弓手、拉弦手从造型上拆下，两只手臂按崔斯特那样分大臂（皮肤）、小臂（紫红腐化）和爪手两段摆，持弓手在身后、拉弦手在身前，弓整把跟着手走（只有 E 和死亡时用 RotSprite 转），拉弓时一根弦从弓尖拉到脸旁、弦上搭一支发光的箭、弓变亮；普攻、E、受击站在待机自己的腿上，出手时整个人连腿一起后撤一格、放箭时前移一格；Q 蓄力、R 甩出是前后分腿的弓步（腿从胯部错开）；跑步两腿从胯部交替迈步；死亡时弓脱手落地、人跪下低头。用户看过后照隔壁 oppi 的韦鲁斯改了手臂（持弓手从肩膀顶端伸出、肩膀接缝不留黑线），又逐处修了胯部的厚黑描边、腰和腿的对齐（右边从腰腹到小腿一条直线）。
- 特效用 Codex 画的 24 张（生图原稿，`import_varus.py --raw`：每张按格子等分，每个游戏像素取覆盖的原稿像素里最多的颜色，颜色归到包里给每张的色阶——暗裔紫光、品红、腐化紫红、黑紫，箭和触须保留描边、光效外圈最暗的一档去掉；枯萎标记那张的三行拆成 1/2/3 层）。位置：普攻、Q、E、R 从弓的握把出手（放箭那一帧量的：普攻 (13, −9)、Q (13, −8)、E (13, −18)、R (14, −8)），枯萎标记在头顶上方，箭雨、腐化地面、扩散的地面圈按椭圆最宽的一行对在脚下，禁锢的触须底边踩在脚底线上。箭、Q 的大箭、触须都从 8 px 高飞出（`y_offset` −3000），第一帧前空 2 tick（飞过弓之前不画）。

逐帧预览：[`docs/preview/league_varus_frames.png`](../preview/league_varus_frames.png?v=1023v2)，特效：[`docs/preview/league_varus_effects.png`](../preview/league_varus_effects.png?v=1014g)。
