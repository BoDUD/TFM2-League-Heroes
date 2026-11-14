<!-- 本页上半部分由 tools/docs/gen_hero_docs.py 按仓库里现在的数据生成，手改会被覆盖；「开发记录」以下是手写的，生成时原样保留。 -->

# 亚托克斯 Aatrox

<img src="img/league_aatrox.png" alt="亚托克斯" width="64">

| 项目 | 内容 |
|---|---|
| id | `league_aatrox` |
| 所属的包 | 主包（mod_id `league`） |
| 分路 | 上单 |
| 分类 / 标签 | 近战（Melee） · AD / Melee / CC / Heal |
| 高清帧 | PPU 2.27 |
| 附加包 | [剑魔 W 锁链附加包](#附加包)（`league_aatrox_chain`） |

![亚托克斯演示](../preview/league_aatrox_showcase.gif)

其他预览：[combos](../preview/league_aatrox_combos.gif)、[w_ring](../preview/league_aatrox_w_ring.gif)、[逐帧预览](../preview/league_aatrox_frames.png)、[特效表](../preview/league_aatrox_effects.png)

## 现在的技能

下面是游戏里显示的技能说明（`league/text/champion.i18n` 的简体中文，去掉了颜色和图标），冷却、距离来自 `league/champion/league_aatrox.data_champion`；1 秒 = 60 tick。

### 普攻 / 被动（被动「赐死剑气」）

*攻击间隔 1.1 秒 · 攻击距离 26000*

被动 赐死剑气：每10秒强化一次普攻，额外造成25和英雄6%最大生命值的伤害并回血；命中英雄冷却-2秒，剑刃边缘-4秒。对英雄的伤害回复18%。

### 技能1 · 暗裔利刃

*冷却 15 秒 · 可存 3 次 · 施放距离 44000 · 施放：指定目标 · 敌人（不含防御塔）*

可连放三段，形状各异，每段+25%，造成176% 攻击力物理伤害；剑刃边缘命中再+60%并击飞。暗影冲决就绪时先冲刺，把敌人送到剑刃边缘。

### 技能2 · 恶火束链

*冷却 9 秒 · 施放距离 42000 · 施放：方向 · 敌人（不含防御塔）*

甩出锁链，第一个敌人受到40 + 40% 攻击力物理伤害；被锁住的英雄1.5秒后被拖回再受一次伤害。

### 大招 · 大灭

*冷却 50 秒 · 施放距离 45000 · 施放：无目标 · 敌方英雄*

显现恶魔形态10秒：恐惧附近小兵和野怪，攻击力+25%，自我治疗+50%，移速+45%并逐渐衰减。击杀英雄会刷新持续时间。

### 数值

攻击力 100（每级 +22）、生命 1100（每级 +105）、护甲 36（每级 +8）、魔抗 26（每级 +4）、移速 1030（每级 +10）。

## 附加包

附加包是可选的原生代码 mod（都在附加包合集 `league_addons` 里），**不装主包里的英雄也是完整的**。

### 剑魔 W 锁链附加包

[剑魔 W 锁链附加包](../../addons/league_aatrox_chain/README.md)：`league_aatrox_chain` v0.2.5

0.2.5（2026-11-05）：待命式大招没用掉时的冷却退还从来没生效过：n tick 的待命标记只有 n - 1 tick 看得见（经典 SDK 探针 lr1105/fix_j：n - 1 之前 148/148 次看得见，第 n tick 0 次），退还在窗口最后一 tick 读它时已经没了，所以每次待命过期都要等完整冷却（塞恩追踪：过期到再待命 3558 tick，改读后 877）。现在在窗口结束前 3 tick 读（`tools/fix/arm_refund_read.py`），副本跟着主包重新生成；DLL 没变。看 `league_ult_press.log` 的 `R ARMED … refunded (not used)`。

## 相关脚本和素材

- [`tools/lol/extract_aatrox.py`](../../tools/lol/extract_aatrox.py)
- [`tools/art/preview_aatrox.py`](../../tools/art/preview_aatrox.py)
- [`tools/art/rig_aatrox.py`](../../tools/art/rig_aatrox.py)
- [`tools/art/import_aatrox.py`](../../tools/art/import_aatrox.py)
- [`tools/art/design_aatrox.py`](../../tools/art/design_aatrox.py)
- [`assets/source/aatrox/`](../../assets/source/aatrox)

## 开发记录

> 下面是原来 README 里「英雄：亚托克斯」一节，原样搬过来（只改了相对链接）。

| 部分 | 内容 |
|---|---|
| 定位 | 上单（近战战士，分类 Melee），用户 10 月 2 日排的第十一组的上单。暗裔剑魔：三段 Q 的剑刃边缘击飞，W 锁链把人拖回圈心，R 恶魔形态腾空作战 |
| 普攻 / 被动 | 普攻 100% 攻击力，射程 26000。被动「赐死剑气」：每 10 秒强化一次普攻，额外 25 + 英雄 6% 最大生命值的伤害并回血；命中英雄冷却 −2 秒，剑刃边缘命中 −4 秒。对英雄的伤害回复 18%（E 的被动并入） |
| 技能1 | Q「暗裔利刃」：可连放三段，形状各异（Q1 长条、Q2 扇形、Q3 圆形砸地），每段 +25%，176% 物理伤害（2026-10-20 前是 100 + 160%）；剑刃边缘命中再 +60% 并击飞。蓄力的整个过程地上都有警示，劈下前锁定方向，走开就能躲。E「暗影冲决」并入 Q：就绪时在蓄力中途冲刺，把敌人送到剑刃边缘 |
| 技能2 | W「恶火束链」：甩出锁链，第一个敌人受到 40 + 40% 物理伤害；被锁住的英雄 1.5 秒后被拖回圈心再受一次伤害（用户要求去掉了减速）。扩展包 `league_aatrox_chain` 判断他是否已经走出圈：走出去了才不拖。锁链打中任何敌人，落点都会出现地面圈和 1.5 秒后的收紧特效（只有英雄会被拖回；原来只在打中英雄时才出圈，锁链大多被小兵挡住，平时几乎看不到。用户：「剑魔的w应该是释放了地面上就有的吧」，2026-10-05，`tools/fix/fix_aatrox_w_ring.py`） |
| 大招 | R「大灭」：显现恶魔形态 10 秒，恐惧附近的小兵和野怪，攻击力 +25%，自我治疗 +50%，移速 +45% 并逐渐衰减；击杀英雄刷新持续时间。开大期间普攻、强化普攻、W 和三段 Q 都换成空中版本：起手离地，出招时飘在空中（离地 2–11 格，照英雄联盟 ULT 动画的高度），Q 俯冲砸地，收招落回地面。引擎不能在运行时换待机和走路的动画，所以不出招时脚在地上，背后的翅膀光环一直在 |
| 附加包（站桩） | 可选的附加包 [`addons/league_ult_press`](../../addons/league_ult_press/README.md)（在附加包合集里，原生代码，主包不装它也完整）：游戏 0.6.4 的 AI 常让这位英雄在敌方英雄跟前站着不打——只读观察包里身边 50000 内有敌方英雄时站着不动 14.3%，其中 8.7% 是 AI 下令「走到自己脚下」（盖伦 2.7% / 0.7%）。照卡蜜尔、瑟提、奥拉夫的办法（用户：「站桩的按照之前卡密尔那样改 然后合并」）：原地站了 15 tick、普攻好了、AI 还让他原地站时，35000 内最近的敌方英雄——他生命不低于一半、目标离敌方塔 75000 以外、目标身边 60000 内的敌方英雄不多于他身边的我方英雄（含他）——就普攻他，打出一下或 1.5 秒后重新算 |
| 数值 | 攻击 100（+22）、生命 1100（+105）、护甲 36（+8）、魔抗 26（+4）、移速 1030（+10）。数值是自己设计的，用 SDK 对战模拟调：上单，对 5 个原版上单，三套队友阵容、两边各 24 局。W 去掉减速后击杀差 +1.59（带 25% 减速时 +1.69） |
| 精灵图 | 待机、移动、普攻、强化普攻、Q1–Q3、W、R 变身、开大的普攻 / 强化普攻 / W / Q1–Q3、受击、死亡。造型是 Codex 的生图草稿按格子读回到 40 行（`design_aatrox.py`），头和巨剑来自第一版；第 7 步补齐身上的透底小洞、两个膝盖至少两格、描边闭合。跑步、普攻、强化普攻、W、受击、死亡用待机自己的部件摆出来（`rig_aatrox.py`：手肘在臂长之内弯曲，巨剑不重采样、只用精确的方向，跑步左右腿交替、红色护甲片跟着大腿）；Q1–Q3 是 Codex 画的；开大的空中动作用 `air_aatrox.py` 从这些通过的帧拼出（腰部以上不动，待机的腿下垂，翅膀用通过的光环） |
| 高清帧（PPU 2.27） | 2026-11-03 用 PPU 重做，和魔腾、凯南、丽桑卓在同一个 PR（用户：「继续加四个 魔腾 凯南 剑魔 丽桑卓」「凯南1.81 梦魇1.8 剑魔2.27 丽桑卓1.81」「丽桑卓有模型一大一小的问题 剑魔的头看起来只看后面」「可以，开 PR 安装」）。设计图：Codex 照旧精灵描密的原图，按原图约 12 像素一格读回（97 × 91 格；最高处到脚底 91 行，旧精灵 40 行，PPU 2.27），脸那一块按格子取整格平均色、过半近黑记成黑线；眼睛和嘴里的红光只有一两格，四周是黑色面甲，整格平均会混成暗红点、头看着像后脑勺（用户：「剑魔的头看起来只看后面」），设计图和每一帧都把这几格发光的红单独取它们自己的颜色；外描边加 2 格。动作：Codex 照旧版同一帧整帧重画 73 帧（普攻第 1、6 帧，强化普攻第 6 帧，Q2 / Q3 第 8 帧，W 第 1、5、6 帧，死亡第 1、7、8 帧，开大的普攻、强化普攻、Q1–Q3 的末帧和 W 第 1、6 帧共 18 帧和别的帧或设计图一样，只画一次），白底原图读回到设计图的格子上：每帧的缩放取身高、头的大小、身体面积三种量法的中位数（只按一种，个别帧会一大一小）；强化普攻、Q2、Q3、开大的强化普攻、Q1–Q3 和 W 共 8 个动作按旧版不带特效的原生身体格画，刀光、火焰、锁链和 *_fx 由 aatrox_bake.json 重新叠上；量头用胸口发光的核心。待机和选人卡轮播是 hero_reels 从新动作剪的；选人卡偏移按 bp_card_audit 的规则 -10 → -8；附身的灵魂表跟着换成新帧。2026-11-04（和牛头、蛮王、派克、布兰德同一个 PR）：拼帧画布脚下原来只留几格，伸到脚下的特效被截平；现在脚下也多留 60 格，Q2 刀光的下缘补回来了（Q2 和开大 Q2 的身体帧及其 fx 拷贝共 24 帧，帧框不变）。|
| 修正（Q 前期伤害、射程，2026-10-20） | 用户：「剑魔（亚托克斯）前期 Q 技能直接秒人，这个有可能改一下吗？另外，要是能稍微增加一点技能范围就更好了」。Q 每段去掉固定伤害、只按攻击力加成，加成 ×1.1（Q1 176%、Q2 220%、Q3 264%，剑刃边缘再 +60%；E 的治疗同比例）：1 级三段 Q 本体从 975 降到 660（剑刃边缘全中 1560 → 1056），12 级 2427 → 2257。三段 Q 的形状、施放距离、Q 里 E 判断冲刺的距离都加大 10%，地上的警示图按新尺寸重画（[`tools/art/warn_aatrox.py`](../../tools/art/warn_aatrox.py) RANGE）。改动由 [`tools/fix/aatrox_q_tune.py`](../../tools/fix/aatrox_q_tune.py)（幂等，`--check`）写进数据和说明。经典模拟（16 个种子，对 6 个原版上单，三套阵容两边各打）：原来 +1.45；去掉固定伤害、加成不变 +0.64，×0.94 −0.03，×1.1 **+1.55**（选这个） |
| 大招期间一直飘在空中（主包图集 + `league.dll` 的 LOOKS 表，2026-11-14） | 用户 10 月 4 日问「剑魔的大招应该一直在天上的吧？」，11 月 14 日看了「和英雄联盟不一样的地方」清单后说「全改吧」。英雄联盟的大灭整段时间他都飞着（客户端 ULT 动画脚离地 39–117 单位），只有 Q 砸地时落下。这里原来开大的出招起手离地、收招落回地面，不出招时站在地上、身后是翅膀光环（`league_aatrox_r_look` 的画面，画在脚下站点上的 1 倍图）：待机、移动、受击是游戏按名字自动播的，数据换不了。现在 `league.dll` 的 LOOKS 表在他身上有 `league_aatrox_r`（整段大灭 10 秒，击杀续上）时把待机、移动、受击换成 `r_idle` / `r_run` / `r_hit`，变身 `ult` 换成 `r_ult`。这些帧都是他自己已经通过的帧整帧挪动（`tools/art/hover_aatrox.py`，不重画、不缩放、身体大小不变）：悬停的姿势是开大每个出招的收尾帧（展开翅膀的待机，头、胸口的核心、脚底和待机在同一行），抬高 7 游戏像素（高清帧 16 格），和开大普攻在空中的高度一样；待机停住、不上下摆动，移动是滑翔（身体不动），受击往后退 2 / 1 像素、第一帧像他自己的受击一样泛白、外描边不变；变身前 5 帧不变，最后 3 帧停在悬停的高度、不再落地（选人卡和待机小动作还播原来的 `ult`）。开大的普攻、强化普攻、W 每一帧都抬到不低于悬停的高度（原来每出手一次都落回地面一下）；三段 Q 只抬起手的前 2 帧，砸地和之后照旧落在地上（英雄联盟也是 Q 砸地时落下）。翅膀已经画在这些帧里，主包和附加包 `league_aatrox_chain` 的数据去掉了 `league_aatrox_r_look` 的光环画面（buff 还在：给它的普攻树不能动），不然是两对翅膀。没有 `league.dll` 时（或游戏版本认不出、LOOKS 挂不上）不出招时站在地上、也没有光环。游戏里还没看过 |

重新生成：

```bash
python tools/art/design_aatrox.py        # 造型
python tools/art/rig_aatrox.py           # 待机、跑步、普攻、强化普攻、W、受击、死亡
python tools/art/import_redo_aatrox.py   # Codex 的 Q1–Q3（之后要再跑 air_aatrox.py）
python tools/art/air_aatrox.py           # 开大的空中动作和变身
python tools/art/import_native.py --hero aatrox
python tools/art/warn_aatrox.py && python tools/art/chain_aatrox.py && python tools/art/import_aatrox.py   # 特效
python tools/art/preview_aatrox.py
# PPU 2.27 重做（2026-11-03）：
python tools/art/pack_aatrox_ppu.py --out <文件夹>          # 给 Codex 的设计图包（照旧精灵描密）
python tools/art/design_aatrox_hd.py                      # Codex 的原图（hd/raw/aatrox-A.png）按原图约 12 像素一格读回 -> hd/design.png
python tools/art/pack_aatrox_actions.py --out <文件夹>      # 给 Codex 的动作包（照旧版同一帧整帧重画）
python tools/art/casts_aatrox_hd.py --heights             # 每帧按身高的缩放；--heads 每帧头的大小（定 FRAME_ZOOM）
python tools/art/rig_aatrox_hd.py                         # 读回 -> 原始条和 1 倍图
python tools/art/ppu_restyle.py --hero aatrox && python tools/art/ppu_hd.py --hero aatrox
python tools/art/ppu_one.py --hero aatrox && python tools/art/rig_aatrox_hd.py --one-ground && python tools/art/hero_reels.py --hero aatrox
python tools/art/review_aatrox_actions.py --out <文件夹>    # 旧版 / 新版对照动图
```

逐帧预览：[`docs/preview/league_aatrox_frames.png`](../preview/league_aatrox_frames.png?v=1104hd)，特效：[`docs/preview/league_aatrox_effects.png`](../preview/league_aatrox_effects.png?v=1103hd)。
