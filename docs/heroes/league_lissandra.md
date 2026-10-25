<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 丽桑卓 Lissandra

<img src="img/league_lissandra.png" alt="丽桑卓" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_lissandra` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 中单 |
| 分类 / 标签 | 法师（Magician） · AP / Magic / CC |
| 高清帧 | 1 倍像素（无高清帧） |
| 附加包 | [低血量附加包：布里茨、乐芙兰、丽桑卓](#附加包)（`league_lowhp`） |

![丽桑卓演示](../preview/league_lissandra_showcase.gif)

其他预览：[逐帧预览](../preview/league_lissandra_frames.png)、[特效表](../preview/league_lissandra_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_lissandra.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动（被动「冰脉驱役」）

*攻击间隔 1.42 秒 · 攻击距离 55000*

发射冰弹攻击。被动冰脉驱役：她击杀的敌方英雄化为冰仆，1.5秒后碎裂，对周围敌人造成150 + 70% 法强魔法伤害并减速。

### 技能1 · 寒冰碎片

*冷却 4 秒 · 施放距离 70000 · 施放：方向 · 敌人（不含防御塔）*

射出冰锥，沿途每个敌人受到120 + 100% 法强魔法伤害并减速25%。出手时方向已锁定，可以躲开。

### 技能2 · 冰霜之环

*冷却 7 秒 · 施放距离 85000 · 施放：无目标 · 敌人（不含防御塔）*

周围敌人受到100 + 80% 法强魔法伤害并定身1.25秒。身边没敌人时放冰川之径：冰爪造成80 + 60% 法强，追上正在交战的敌方英雄后再放冰环。

### 大招 · 冰封陵墓

*冷却 60 秒 · 施放距离 90000 · 施放：无目标 · 敌方英雄*

冰封敌方英雄：眩晕1.5秒，受到200 + 100% 法强魔法伤害。被两名以上敌方英雄围住时改为冰封自己2.5秒：免疫伤害和控制，回复200 + 80% 法强生命。冰块周围留下减速冰地。

### 数值

攻击力 85（每级 +6）、法强 42（每级 +21）、生命 975（每级 +106）、护甲 22（每级 +7）、魔抗 22（每级 +3）、移速 900（每级 +10）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 低血量附加包：布里茨、乐芙兰、丽桑卓

[低血量附加包：布里茨、乐芙兰、丽桑卓](../../addons/league_lowhp/README.md)：`league_lowhp` v0.2.0

| 英雄 | 主包（纯数据） | 装了附加包（英雄联盟） |
|---|---|---|
| 丽桑卓 大招冰封自己 | 被两名以上敌方英雄围住 | 生命不高于 35% |

## 相关脚本和素材

- [`tools/kit/build_lissandra.py`](../../tools/kit/build_lissandra.py)
- [`tools/kit/setup_lissandra.py`](../../tools/kit/setup_lissandra.py)
- [`tools/lol/extract_lissandra.py`](../../tools/lol/extract_lissandra.py)
- [`tools/art/preview_lissandra.py`](../../tools/art/preview_lissandra.py)
- [`tools/art/rig_lissandra.py`](../../tools/art/rig_lissandra.py)
- [`tools/art/import_lissandra.py`](../../tools/art/import_lissandra.py)
- [`tools/art/design_lissandra.py`](../../tools/art/design_lissandra.py)
- [`assets/source/lissandra/`](../../assets/source/lissandra)

## 开发记录

> 下面是原来 README 里「英雄：丽桑卓」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 中单（法师，分类 Magician），用户 10 月 2 日排的第十二组的中单（同组：瑟提、伊芙琳、韦鲁斯、牛头）。冰霜女巫：冰锥减速、冰环定身、冰爪滑进人群开团，冰封陵墓既能冻住敌人也能冻住自己保命 |
| 普攻 / 被动 | 普攻是一颗追踪的小冰弹，100% 攻击力的物理伤害，射程 55000，攻击间隔 85 tick（第 13 tick 出手，从手的高度飞出）。被动「冰脉驱役」：她的普攻、Q、W、R 打死的敌方英雄在倒下的地方化成冰仆，1.5 秒后碎裂，对周围（半径 25000）敌人造成 150 + 70% 法术强度的魔法伤害并减速 25% 1.5 秒。英雄联盟是附近任何敌方英雄死亡都会变冰仆、冰仆还会走向敌人；这里没有「有人死了」的事件，用击杀检测（金克丝那套：命中时挂标记，活着的目标一 tick 后清掉）加命中同一 tick 投一个 1 tick 的隐形落点记下位置，所以只认她自己打死的、冰仆站在原地 |
| 技能1 | Q「寒冰碎片」：射程 70000，冷却 4 秒，也对小兵和野怪放。出手瞬间（第 12 tick）射程内有敌方英雄就朝他当时的位置射（直线，可以躲），否则朝施放方向：一根冰锥穿过路上的所有敌人（英雄联盟是打中第一个后碎片继续往后飞，这里直接穿透），120 + 100% 法术强度的魔法伤害，减速 25% 1.5 秒 |
| 技能2 | W「冰霜之环」，E「冰川之径」并入（用户选的）：冷却 7 秒。身边（半径 26000）有敌人：立刻放冰环，100 + 80% 法术强度的魔法伤害并定身 1.25 秒。身边没人：E 不在冷却（15 秒）且 85000 内有队友正在打的敌方英雄时，冰爪贴地滑向他（路上的敌人 80 + 60% 法术强度），她顺着冰路滑到爪子停下的地方（英雄身前 14000），落地接冰环——英雄联盟的 E → W 开团；否则冰爪只扔出去打一下（清线、打野，不滑过去） |
| 大招 | R「冰封陵墓」：冷却 60 秒。大招位只负责「就绪」（同凯尔的大招：AI 遇到英雄就会放大招位），就绪 10 秒内她的普攻、Q、W 出手时检查：身边 30000 内有两个及以上敌方英雄（英雄联盟是残血时冻自己，这里读不到生命值，用「被围」代替）→ 冻住自己 2.5 秒，伤害和控制都免疫，期间回复 200 + 80% 法术强度的生命；否则 60000 内有队友正在打的敌方英雄 → 把他冻进冰墓，眩晕 1.5 秒，200 + 100% 法术强度的魔法伤害。两种都在冰墓周围炸开黑冰（半径 26000 内敌人 80 + 40% 法术强度），留下一片冰地 3 秒，冰地上的敌人减速 40%。10 秒内没用上就返还冷却 |
| 附加包 | 可选的附加包 [`addons/league_lowhp`](../../addons/league_lowhp/README.md)（在附加包合集里，原生代码，主包不装它也完整）：大招照英雄联盟在生命不高于 35% 时改为冰封自己（主包是被两名以上敌方英雄围住）；v0.2.0 起她身边任何敌方英雄阵亡都化成冰仆（主包只认她自己的击杀） |
| 数值 | 攻击 80（+6）、法术强度 40（+20）、生命 920（+100）、护甲 22（+7）、魔抗 22（+3）、移速 900（+10）。数值是自己设计的，用 SDK 对战模拟调：中单，对 5 个原版中单（`pyromancer`、`ice_mage`、`lightning_mage`、`wind_mage`、`white_mage`），3 套阵容、两边各打，10 分钟。初稿 −0.22（输出 7915，偏弱）；各技能伤害都加（Q 90 + 80% → 120 + 100%、冷却 4.5 → 4 秒，W 70 + 60% → 100 + 80%，E 60 + 50% → 80 + 60%，R 150 + 75% → 200 + 100%，冰仆 100 + 50% → 150 + 70%）后种子 1–24 +1.51、25–48 +1.55（本包的瑞兹 +1.50）。把「被围」的范围放大到 40000 或加坦度（生命 980、双抗 26，+2.04）都没用上 |
| 亚索联动 | 冰环的定身和冰墓的眩晕都是亚索大招要的控制：丽桑卓中单、亚索同队时，亚索每局 R 到被控英雄 1.79 次（同一批原版雷法 3.19、崔斯特 1.23），亚索不用调 |
| 精灵图 | 10 个动作 57 帧：待机、移动（滑行）、普攻、Q、W、E 掷爪（`skill2_e`）、R 冻敌人（`ult`）、R 冻自己（`ult_self`）、受击、死亡。造型 27 × 42 px，21 色；她没有腿（英雄联盟里长裙拖地、滑着走），裙摆最低一行就是脚底线。待机 6 帧同一张，呼吸时裙摆以上下沉一行（裙摆的冰晶不动）；头像截取点 (0, −39)，选人卡片 `banpick_center` −9（待机最高点 −30） |
| 特效 | Codex 生图的 21 张 97 帧（`import_lissandra.py` 缩成游戏像素）：`league_lissandra_fx` 冰弹和命中、Q 手上的寒气、冰锥和命中、减速的霜（Q、R 冰地、冰仆三处共用）、W 命中和定身的冰晶、E 手上的光、冰爪和划痕；`league_lissandra_big` W 冰环（W 和 E 落地各用一次）、E 落地的寒雾和冰晶、R 卷下的寒风、冰墓、黑冰爆发、冰地、冻自己时冰块成形和持续、冰仆站起和碎裂 |
| 音效 | 英雄联盟的音效和配音（`tools/lol/extract_lissandra.py`）：普攻出手和命中，Q 出手、飞出和命中，W 冰环和定身，E 出手、命中和滑过去，R 出手、冰墓、冻自己、冰爆、冰地，冰仆站起和碎裂；Q、W、E、R（冻敌人 / 冻自己）各一句中文配音。版权属于 Riot Games，**不提交到仓库**，按下面的命令在本地生成 |
| 图标 | 官方技能图标（Q / W / R），从本地客户端提取，缩到 64×64 |

重新生成（素材来自本机的英雄联盟客户端，音频不进仓库）：

```bash
python tools/lol/extract_lissandra.py --lol "D:\WeGameApps\lol" --vgmstream "<vgmstream-cli.exe 路径>"
python tools/kit/build_lissandra.py        # 技能数据，数字都在脚本的参数表 P 里；--nodes 看每棵技能树的节点数
python tools/kit/setup_lissandra.py --face=0,-39 --banpick=-9   # 五种语言的文字、音效配置、共享文件里她的键
python tools/art/design_lissandra.py       # 造型：Codex 换皮的 B 按格子取多数色读回、修脸
python tools/lol/native_pose.py assets/source/lissandra/poses.json --out <渲染文件夹>   # 动作参考帧
python tools/art/rig_lissandra.py          # 动作：每帧都是造型本身，只用她自己的手臂格子按英雄联盟的角度摆
python tools/art/import_native.py --hero lissandra
python tools/art/import_lissandra.py       # 特效；--raw <Codex 的特效交付文件夹> 先把生图原稿缩成游戏尺寸的原尺寸条
python tools/art/preview_lissandra.py
```

美术（原画的提示词见 [`assets/source/lissandra/PICTURE_PROMPT.md`](../../assets/source/lissandra/PICTURE_PROMPT.md)，造型的见 [`MODEL_PROMPTS.md`](../../assets/source/lissandra/MODEL_PROMPTS.md)、[`MODEL_PROMPTS_V2.md`](../../assets/source/lissandra/MODEL_PROMPTS_V2.md)、[`SKIN_PROMPT.md`](../../assets/source/lissandra/SKIN_PROMPT.md)，动作的见 [`MODEL_STRIPS.md`](../../assets/source/lissandra/MODEL_STRIPS.md)，特效的见 [`PROMPTS_FX.md`](../../assets/source/lissandra/PROMPTS_FX.md)；Codex 的交付说明在 [`codex_picture/`](../../assets/source/lissandra/codex_picture)、[`codex_model/`](../../assets/source/lissandra/codex_model)、[`codex_skin/`](../../assets/source/lissandra/codex_skin)、[`codex_strips/`](../../assets/source/lissandra/codex_strips)、[`codex_fx/`](../../assets/source/lissandra/codex_fx)）：

- 原画：Codex 画了 A（英雄联盟的待机：两臂垂在身侧）、B（Q 的起手：双臂张开），用户选 A。渲染参考时她皮肤里的子网格名字是反的：身体叫 `Lissandra_Death_subm`，`Lissandra_Model_Lissandra1` 是死亡时的冰晶，藏掉后者；英雄联盟里她的眼睛被冰冠的面罩挡住，照原版不画眼睛，下半张脸一格深蓝嘴唇。
- 造型：Codex 的生图画不准 40 行——第一轮按脚本删行拼的 A/B 很粗（辫子是一根白柱子、脸很小），细节好的那张原稿是 79 行；第二轮让它照细节原稿直接画 40 行，三张原稿还是 72–100 行，任何缩小（按面积、2×2 减半、整行删）都碎成杂点。改用用户定的「骨架 + 皮囊」：我逐格画了一张 40 行的骨架（大小、比例、姿势，`assets/source/lissandra/design_lz.py`），和 Codex 第二轮最好的原稿（皮囊）一起交给 Codex 换皮，用户选了 B（42 行）。Codex 的方块大小在 19 px 上下浮动，按格子中心取色会取到邻格，改成每格取多数色（格距 19.75 px、偏移 (16, 8)，在 18–20.5 px 之间搜出来最「纯」的一组）；读回后脸是一块浅色，按规则重修：眼睛那一行是面罩（下沿一格亮边）、两行皮肤、一格深蓝嘴唇、一行下巴阴影。
- 动作参考（`poses.json`）：镜头 yaw 45、pitch 20，镜像；头 2.4 倍，辫子按头的放大缩回（`hair` 0.42，不然辫子拖到裙摆下面）；高度 42；藏死亡冰晶和 Q 的冰刺。移动用英雄联盟的 `Run`（她滑行，2 秒一个循环，8 帧 × 250 ms）。
- 动作：Codex 的动作条（[`codex_strips/`](../../assets/source/lissandra/codex_strips)）它自己的说明就写了不合格：身体被画到 47–60 行、手臂太细、辫子对不上。她没有腿，所以每帧的身体（冰冠、头、胸甲、长裙）直接是造型本身，只把两条手臂拆下来（身前那只第 70–73 列、身后那只第 60–62 列，第 74–85 行，肘在第 80 行），用她自己的格子分大臂、小臂两段，按英雄联盟每帧的角度摆（`rig_twistedfate.place_bone`：45° 以内逐行错开，横过来整段转 90°，接近 45° 加宽一格）；身后那只画在身体后面。滑行时手臂往后拖、互相摆几度，裙摆以上起伏一行；死亡照英雄联盟：举起双臂，深色冰锥从裙摆往上长到胸口，冻成冰雕。用户看过后改了两处：R 身前那只手举过 150° 成了压在冰冠上的细钩、斜 45° 甩出成了细长棍（「放R的时候右手有点怪 违和感」），改成举到冠刃旁边、甩出收短；放技能时裙摆以上左右挪一格当作前倾后仰，上身在裙摆上错开（「放技能的时候模型左右晃动导致变形了」），去掉，只留受击的后仰。
- 特效用 Codex 画的 21 张（97 帧，生图原稿，`import_lissandra.py --raw`：每张按画的格子数等分，每个游戏像素取覆盖的原稿像素里最多的颜色，颜色归到包里给每张的色阶——白蓝的冰、寒雾、手上的青光、她的黑冰，实心冰保留描边、光效外圈最暗的一档去掉）。位置：Q、E 出手的寒光在伸出的手 (17, −16) / (17, −12)；冰墓、冰块、冰仆、定身的冰晶底边踩在脚底线上，地面的环和冰地按椭圆最宽的一行对在脚下。冰弹从 8 px 高出手（追踪弹从更高处出手会飞歪），冰锥从 15 px 高出手；飞出去的冰弹、冰锥、冰爪第一帧前空 2–3 tick（飞过手之前不画）。

逐帧预览：[`docs/preview/league_lissandra_frames.png`](../preview/league_lissandra_frames.png?v=1014g)，特效：[`docs/preview/league_lissandra_effects.png`](../preview/league_lissandra_effects.png?v=1014g)。
