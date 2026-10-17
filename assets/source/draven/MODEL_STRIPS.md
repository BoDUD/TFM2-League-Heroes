# 德莱文：动作帧（第 2 步，给 Codex 的提示词）

> **这一轮画动作帧。每一帧单独生成一张图**（以前整条动作画在一张图里，结果糊成色块；一帧一张才清楚）。
> - **长相、大小、比例、颜色全照定稿** `1_design.png`（用户已批准：头尖到脚底 40 格，23 色，鸡冠头 + 金头带 + 马蹄胡、米白毛皮披肩 + 青绿里衬、交叉皮带、深红护腕、黑裤、银蓝护胫、两把带刺圆环双刃斧）。每一帧都是**同一个人、同样大小**：头一样大（约 11 行），身体、斧头一样大。
> - **姿势照英雄联盟**：每帧的文件夹里 `a_league_game_size.png` 是英雄联盟原版这一帧缩到游戏尺寸放在同一块画布上（**位置、大小、姿势**），`b_league_pose.png` 是同一帧的高清图（看关节怎么弯）。照着关节**整个人重画**，不要只挪手。英雄联盟的模型头小、斧头大，**我们照定稿的比例画**。
> - **3/4 正面朝右，脸朝观众**（英雄联盟有几帧转成背对镜头，我们还是画成正面朝右、只把手臂和上身扭过去）。**哪只手拿什么照定稿**（定稿远手=图左那只手、近手=图右那只手，各一把斧），不要照英雄联盟换手。
> - **出手帧**（标了【出手帧】）：投斧的手**在胸口高度或更低**、手里已经空了——游戏里斧头从人物腰胸高度飞出去，手举太高看起来就是歪的。别的帧斧头都在手里；**不要画飞在空中的斧头、旋转残影、特效**（特效第 3 步单独画）。
> - 画布 1024×1024（128×128 格，每格 8×8 纯色方块），**脚底在第 99 行（红线）**，站位点在第 64 列（蓝线）；人物（死亡躺倒也一样）**不能低于红线**。透明背景（做不到时纯品红 `#FF00FF`），透明度只有 0 和 255，一圈 1 格近黑描边，颜色只用 `2_palette.png` 的 23 色。
> - 交付到 `outputs/draven-strips/`：每帧一张 `<动作>_<帧号>.png`（文件名照下表，1024×1024），**生图原稿也交**（`raw/`），最后写 `HANDOFF.md`（列出每张读回来的大小、脚底行），打成 `draven_strips_done.zip`。

## 跑步（8 帧，100 毫秒一帧）——只画腰带以下

用户的规矩：**跑步时身体要和定稿逐像素一样，不能变形**；腿要**交叉步、自然**。所以：
- `frames/run_<k>/a_upper_body.png` 是这一帧的上半身（就是定稿，腰带以下擦掉了，按帧上下颠 0 或 1 行）。**腰带以上一个像素都不改**，原样放在原位置；只画腰带以下：胯、两条腿（黑裤 → 银蓝护胫 → 深色靴子，和定稿腿一样的颜色和粗细）、腰带垂下的深红 / 青绿飘带（跟着跑动往后飘一点）。
- 近手那把斧挂在右下方（已保留在上半身图里），腿从它后面经过。
- `b_legs_guide.png`：上半身 + 英雄联盟这一帧的腿（淡色）+ **两只靴子该在的框**（红 = 近侧腿，画在前面；蓝 = 远侧腿，被挡住的部分不画）。框的底边是靴底：在红线上 = 着地，高于红线 = 抬起。`c_league_pose.png` 是高清参考。
- **交叉步**：每半圈换一次前脚；着地那只脚一帧一帧往后退（踩住地，身体从上面过去）；离地那只先在身后抬脚跟，再从着地腿旁边越过往前伸。两只靴子相距不超过 12 格；两条腿一样的颜色（远侧不要变色）；**胯可以比站姿收窄**（跑步是侧身步），但腰带以上不动。

| 帧 | 文件 | 上半身下移 | 近侧靴 x | 近侧抬 | 远侧靴 x | 远侧抬 |
|---|---|---|---|---|---|---|
| 1 | `run_1.png` | 0 | +6 | 0 | -6 | 4 |
| 2 | `run_2.png` | 1 | +3 | 0 | -3 | 6 |
| 3 | `run_3.png` | 1 | +0 | 0 | +1 | 4 |
| 4 | `run_4.png` | 0 | -3 | 0 | +5 | 1 |
| 5 | `run_5.png` | 0 | -6 | 4 | +6 | 0 |
| 6 | `run_6.png` | 1 | -3 | 6 | +3 | 0 |
| 7 | `run_7.png` | 1 | +1 | 4 | +0 | 0 |
| 8 | `run_8.png` | 0 | +5 | 1 | -3 | 0 |

（x：靴子中心离站位点几格，向右为正；抬：靴底离开红线几行。）

## 动作（每帧一张，整个人照英雄联盟这一帧重画）

| 文件 | 动作 | 时长 | 这一帧画什么 |
|---|---|---|---|
| `attack_1.png` | 普攻（投斧） | 50 ms | 准备：和定稿一样两手各一把斧，膝盖微屈 |
| `attack_2.png` | 普攻（投斧） | 60 ms | 蓄力：近手把斧头举过头顶（斧刃朝后），身体后仰 |
| `attack_3.png` | 普攻（投斧） | 60 ms | 蓄力最满：上身扭转，举斧的手甩到头后上方，另一把斧放低在身侧 |
| `attack_4.png` | 普攻（投斧） | 90 ms | 【出手帧】弓步前冲，投斧的手臂伸直到胸口高度、手里已经空了（斧头已飞出），另一把斧在身后 |
| `attack_5.png` | 普攻（投斧） | 80 ms | 收势：身体压低，投斧的手收回胸前 |
| `attack_6.png` | 普攻（投斧） | 60 ms | 回到站姿：两手各一把斧（斧头回到手里） |
| `skill_1.png` | Q 旋转飞斧（转斧） | 50 ms | 转斧 1：近手的斧头在手里转，刃竖直 |
| `skill_2.png` | Q 旋转飞斧（转斧） | 50 ms | 转斧 2：斧头转了 1/8 圈，刃斜 |
| `skill_3.png` | Q 旋转飞斧（转斧） | 50 ms | 转斧 3：刃水平 |
| `skill_4.png` | Q 旋转飞斧（转斧） | 50 ms | 转斧 4：刃另一个斜向 |
| `skill2_1.png` | E 开道利斧（双斧掷出） | 60 ms | 准备：两把斧在身前交叉 |
| `skill2_2.png` | E 开道利斧（双斧掷出） | 60 ms | 蓄力：两臂张开、两把斧举到两侧，一条腿抬起 |
| `skill2_3.png` | E 开道利斧（双斧掷出） | 60 ms | 蓄力最满：上身后仰，两把斧拉到肩后 |
| `skill2_4.png` | E 开道利斧（双斧掷出） | 80 ms | 【出手帧】弓步前冲，两臂一起往前甩到胸口高度，手里已经空了（两把斧已飞出） |
| `skill2_5.png` | E 开道利斧（双斧掷出） | 80 ms | 收势：身体压低，两手前伸 |
| `skill2_6.png` | E 开道利斧（双斧掷出） | 60 ms | 回到站姿：两手各一把斧 |
| `ult_1.png` | R 冷血追命（巨斧掷出） | 60 ms | 准备：身体压低，两把斧握在身侧 |
| `ult_2.png` | R 冷血追命（巨斧掷出） | 70 ms | 蓄力：两臂高举、两把斧竖着举在头两侧 |
| `ult_3.png` | R 冷血追命（巨斧掷出） | 70 ms | 蓄力：一把斧伸向身后、一把举高，身体扭转 |
| `ult_4.png` | R 冷血追命（巨斧掷出） | 70 ms | 蓄力最满：两把斧都举到头两侧上方 |
| `ult_5.png` | R 冷血追命（巨斧掷出） | 80 ms | 【出手帧】大步前扑，两臂往前甩到胸口以下，手里空了（两把巨斧已飞出） |
| `ult_6.png` | R 冷血追命（巨斧掷出） | 70 ms | 收势：身体压到最低（几乎趴下），两手撑在前面 |
| `ult_7.png` | R 冷血追命（巨斧掷出） | 80 ms | 起身：站起来，两手空着在身侧 |
| `hit_1.png` | 受击 | 100 ms | 受击：身体被打得后仰，头往后，两手的斧头还在 |
| `dead_1.png` | 死亡 | 100 ms | 中招：身体一晃，膝盖一软 |
| `dead_2.png` | 死亡 | 100 ms | 向后倒：两臂往上甩，斧头还握在手里 |
| `dead_3.png` | 死亡 | 120 ms | 倒地中：身体斜着往后倒 |
| `dead_4.png` | 死亡 | 150 ms | 躺倒：背着地平躺，两把斧在手边（贴着身体，不要飞出去） |
| `dead_5.png` | 死亡 | 200 ms | 躺着：同上，胸口起伏一下 |
| `dead_6.png` | 死亡 | 400 ms | 躺着不动（最后一帧） |

## 英文提示词（每帧一次，附上 `1_design.png`、`2_palette.png` 和这一帧文件夹里的图）

动作帧（不是跑步）：

```text
Attached: FIRST the approved game sprite of this character at 8x on a 1024x1024 canvas (128x128 squares) - copy its look, colours, size and proportions exactly (40 squares from the hair crest to the soles, the same head, body and axes); SECOND its palette - use only these colours; THIRD League of Legends' own pose for this frame shrunk to the same game size and placed on the same canvas - copy the POSE, the PLACE and the SIZE; FOURTH the same pose in high detail - read how each joint bends. Redraw the WHOLE character in that pose as one crisp pixel-art sprite at 8x: every square one 8x8 block on one 8-px grid, alpha only 0 or 255, one 1-square near-black outline, flat shades, no anti-aliasing, no blur, no dithering. Keep the FIRST image's proportions (its head is bigger than League's, its axes smaller). 3/4 front view facing image right, the face toward the viewer; the far hand (image left) and the near hand (image right) hold their axes as in the FIRST image. The soles on the red line (row 99), nothing below it. No flying axes, no motion lines, no effects. Transparent background (else solid #FF00FF). This frame: <FRAME>
```

跑步帧：

```text
Attached: FIRST this frame's upper body (the approved sprite with everything below the belt erased) at 8x on a 1024x1024 canvas; SECOND the guide: the same upper body, League's running legs for this frame (faint) and two boot boxes (red = the near leg, drawn in front; blue = the far leg); THIRD League's pose in high detail; FOURTH the approved full sprite (1_design.png) for the leg colours and thickness; FIFTH the palette. Keep every square of the FIRST image exactly as it is and where it is. Draw only what is below the belt: the hips, both legs (black trousers, silver-blue greaves, dark boots - both legs the same colours and as thick as in the full sprite) with each boot in its box (a box above the red line = that foot lifted), and the belt's crimson and teal ribbons swaying back a little. A running cross-step: the planted foot pushes back, the lifted one swings past it. Crisp 8x8 squares on one grid, alpha 0/255, one near-black outline, only the palette's colours, nothing below the red line, transparent background (else solid #FF00FF). This frame: run <K> of 8.
```

每帧的 <FRAME>（照抄）：

```text
attack_1: ready: like the design, an axe in each hand, knees slightly bent
attack_2: wind-up: the near arm lifts its axe above the head, blades back, body leaning back
attack_3: full wind-up: the upper body twisted, the throwing hand swung behind the head, the other axe low at the side
attack_4: RELEASE: a forward lunge, the throwing arm straight forward at CHEST height, the hand EMPTY (the axe has left), the other axe behind him
attack_5: follow-through: body low, the throwing hand coming back to the chest
attack_6: back up: an axe in each hand again
skill_1: twirl 1: the near axe spinning in the hand, blades vertical
skill_2: twirl 2: the axe turned an eighth, blades diagonal
skill_3: twirl 3: blades horizontal
skill_4: twirl 4: blades on the other diagonal
skill2_1: ready: both axes crossed in front of the chest
skill2_2: wind-up: both arms spread wide with their axes, one knee lifted
skill2_3: full wind-up: leaning back, both axes pulled behind the shoulders
skill2_4: RELEASE: a forward lunge, both arms swung forward together at CHEST height, both hands EMPTY (the axes have left)
skill2_5: follow-through: body low, both hands forward
skill2_6: back up: an axe in each hand again
ult_1: ready: crouched, both axes at the sides
ult_2: wind-up: both arms raised, the two axes upright on both sides of the head
ult_3: wind-up: one axe reaching back, the other high, body twisting
ult_4: full wind-up: both axes high on both sides of the head
ult_5: RELEASE: a big forward lunge, both arms swung forward at chest height or lower, both hands EMPTY
ult_6: follow-through: body at its lowest, almost on the ground, hands forward
ult_7: getting up: standing, empty hands at the sides
hit_1: hit: the body knocked back, head back, both axes still in the hands
dead_1: struck: the body staggers, knees give
dead_2: falling back: both arms flung up, the axes still held
dead_3: falling: the body diagonal, going down backwards
dead_4: lying on his back on the ground, both axes beside the hands (touching the body, not flying away)
dead_5: lying: the same, the chest settling
dead_6: lying still (the last frame)
```

## 交回前自查

- [ ] 每帧一张 1024×1024，文件名照表；严格 8×8 方块、透明度 0/255、只用色板颜色、一圈近黑描边；
- [ ] 每帧都和定稿一样大（头一样大、斧头一样大），3/4 正面朝右；手拿斧照定稿；
- [ ] 跑步 8 帧腰带以上和 `a_upper_body.png` 逐像素一样；两只靴子在框里；交叉步；两腿同色；
- [ ] 出手帧的手在胸口高度或更低、手里空了；其他帧没有飞斧、没有特效；脚底不低于红线；
- [ ] 交了生图原稿；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 每张按格读回（regrid / 8 px），对齐色板；跑步帧把定稿上半身逐像素贴回（只取 Codex 的腿），量两只靴子的 x 和抬起对表；动作帧量大小和定稿比、脚底行、出手帧的手高；导入 import_native，做审核 GIF（我们 | 英雄联盟 逐帧）给用户。
