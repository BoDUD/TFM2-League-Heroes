# 元素女皇 奇亚娜：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的原始图（`1_picture_A.png`）**样子、颜色用户认可了，全照它**。
> - 用户定了：**只做 3/4 正面朝右，不要侧面**；**从尖冠顶到脚底 60 格**。我把图直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、眼线、王冠的宝石、圆环的箍碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，**每格 18 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**两稿**（同一个奇亚娜、同样的颜色）：`A-1` / `A-2`。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A（待机）**：每格 **18 px**；照 `2_target_A.png` / `3_layout_A.png`：尖冠顶 **y = 108**（橙线），眼睛约 **y = 414**（蓝线），脚底 **y = 1188**（红线）：**60 格高、约 50 格宽**。
- 全在画布里，尖冠、头发、圆环不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **脸**（`4_head_A.png`，第 0 步读回的头，8 倍）：暖棕色的脸（2–3 档）；**两只琥珀金色的眼睛都看得见：每只约 2 × 2 格（一格深色瞳孔、一格亮金或白色高光），一样高**；每只眼睛上面**一道黑色的粗眼线**（整格），往外挑；眉毛微挑、一脸高傲；小嘴，嘴唇比皮肤深一档；**银白色的齐刘海**压在额头上，脸两边的长发垂下来（头发**白 / 浅灰 / 淡紫灰 3 档**，和脸之间有清楚的描边，**不要糊成一片白**）。
- **王冠和尖冠**：金色的王冠（2–3 档）像一排尖齿压在刘海上，嵌**几块翠绿色的宝石**（每块至少 2 格）；王冠后面竖起**一个高高的白玉色尖冠**（白 / 淡紫灰 2–3 档）。
- **身体**：暖棕皮肤（3 档，亮面偏橙金）；**翠绿和金色的珠子项圈**；**青绿色的抹胸短裙**（3 档）加**金色的边**；裙子下摆前短后长，身后一片**墨绿色的裙摆**；上臂**金色臂环**、手腕**金色手镯**；**一只手叉腰**（近处的手）；**深棕近黑的紧身裤**（2 档）上几个**金色的三角花纹**（整格）；**紫棕色的凉鞋**带金扣，踩在地面线上；**两条腿之间要有空隙和描边分开**；近处的腿（画面左边）全亮，远处的腿暗一档。
- **圆环刀刃**（她最醒目的轮廓）：远侧的手握着环，环**竖在她身侧偏后（画面左边）**，下沿贴近地面但不躺在地上，**上沿不高过她的肩膀，绝不挡脸**；环身是**深棕近黑的弯刃**（3 档，暗处带紫），**内圈一道青绿色的边**（2 档，连续的一圈），环上几道**金色和青绿色的箍**，靠近两端是**玫瑰铜色的护手**，两个对角上各一颗**白玉色水晶刃头**（白 / 淡紫灰 2–3 档，里面一格青绿宝石）。环身至少 3 格粗，**环中间是空的（透明）**。
- **一圈 1 格的近黑外描边**，连续不断（环的内圈也有）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–8 一样的像素画（本包的尼菈、艾瑞莉娅、妮蔻、薇古丝，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（元素的光、草叶、水花、碎石、冲击波都不画；圆环上的宝石就是青绿色，不画元素颜色）。

## 附图（压缩包 `qiyana_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的原始图（用户认可） | **样子、颜色、细节、姿势**全照它 |
| `2_target_A.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` | 加网格线：橙 = 尖冠顶，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head_A.png` | 第 0 步读回的头（8 倍） | 脸、眼睛、眼线、刘海、王冠、尖冠 |
| `style/5_style_nilah.png`、`6_style_irelia.png`、`7_style_neeko.png`、`8_style_vex.png` | 本包的尼菈、艾瑞莉娅、妮蔻、薇古丝，8 倍放大 | **只看风格**：这么粗的格子里女孩的脸、眼睛、头发、首饰、大刀刃怎么画 |

## 提示词（两稿用同一段，各画一张）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A your own earlier pixel-art drawing of one character - a PROUD YOUNG EMPRESS with warm tan-brown skin, LONG WAVY SILVER-WHITE HAIR with straight bangs, a GOLD TIARA set with EMERALD-TEAL GEMS and a TALL WHITE-JADE CREST rising behind it, AMBER-GOLD EYES with thick black eyeliner, a haughty raised brow, an emerald-and-gold bead choker, a TURQUOISE-TEAL STRAPLESS SHORT DRESS with GOLD TRIM and a dark green flap behind, gold armlets and bracelets, DARK BROWN-BLACK LEGGINGS with GOLD TRIANGLE MARKINGS, purple-brown sandals, and a HUGE RING BLADE (a dark brown-black curved blade with violet shadows, a TEAL INNER RIM, gold and teal bands, rose-copper guards and two WHITE-JADE CRYSTAL BLADE HEADS) held upright beside her - her LOOK and COLOURS are approved, but she is drawn with far too many small squares; 2A the same picture cut down to the RIGHT square count - 60 squares from the crest's tip to the soles - shown with big squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke the details; 3A the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4A her head enlarged; 5-8 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a girl's face, eyes, hair, jewellery and a big blade are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES, every square exactly 18 px, aligned on one straight grid from the canvas corner; the top of her crest at y 108, her eyes at about y 414, her soles on y 1188 - exactly 60 squares tall, about 50 squares wide; at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
With this few squares make every part READ: the warm-brown face in 2-3 shades; BOTH AMBER-GOLD EYES visible, each about 2x2 squares (one dark pupil square, one bright highlight square), at the SAME height, a thick black eyeliner line of whole squares above each, flicked outward; a raised haughty brow; a small mouth, the lips one shade darker than the skin; the silver-white straight bangs over the forehead and the long locks down both sides of the face, the hair in 3 shades (white, pale grey, pale lavender-grey) kept apart from the face by the outline - never one white mass; the gold tiara like a row of teeth on the bangs with emerald gems (each at least 2 squares) and the tall white-jade crest behind it. The skin in 3 shades with an orange-gold lit edge; the emerald-and-gold choker; the turquoise-teal strapless dress in 3 shades with a gold trim, short in front, a dark green flap behind; gold armlets and bracelets; the NEAR hand on her hip; the dark brown-black leggings in 2 shades with a few gold triangle markings of whole squares; purple-brown sandals with gold on the ground line, a clear gap and outline between her legs, the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker. THE RING BLADE held in her FAR hand, standing upright beside and behind her on the image left, its lower edge near the ground but never lying on it, its top edge NO HIGHER THAN HER SHOULDERS so it NEVER covers her face; the blade at least 3 squares thick, dark brown-black in 3 shades with violet in the shadows, a continuous TEAL INNER RIM in 2 shades, gold and teal bands, rose-copper guards, two white-jade crystal heads at opposite points each with one teal gem square; the middle of the ring EMPTY (transparent).
One continuous 1-square near-black outline round the figure and round the ring's inner edge; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects (no elemental glow, no leaves, no water, no rocks, no shock waves), no element colours on the ring (its gems are teal), no background, no ground, no cast shadow, no text, no grid lines.
PICTURE A: her relaxed idle exactly as images 1A, 2A and 3A - standing proudly in 3/4 view facing right, the near hand on her hip, the face to the front-right with the chin a little raised, the ring blade in her far hand beside her.
```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：每格 18 px、60 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 两只琥珀金眼睛看得见、一样高、带黑眼线；银白头发和脸分得开，不糊成一片白；金王冠、翠绿宝石、白玉尖冠清楚；青绿抹胸短裙和金边、项圈、臂环手镯、深色紧身裤和金三角纹、凉鞋清楚；两条腿分开。
- 圆环竖在身侧偏后、**不挡脸**、中间是空的；青绿内圈连续、金箍、两颗白玉刃头清楚。外描边连续；没有任何技能特效。

## 交付（`outputs/qiyana-model/`）

- `qiyana-model-A-1.png`、`qiyana-model-A-2.png`；原始生成图原样放 `outputs/qiyana-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/qiyana_model_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（约 18 px / 60 行），从 raw/ 按格读回（regrid，按读回误差最小的格子），在游戏大小下和尼菈、艾瑞莉娅、千珏、莉莉娅并排自查（PPU 1.5：40 游戏像素），把两稿给用户挑。脸放大 12 倍检查，眼睛 / 嘴的格子不清楚就在设计脚本里重画（`codex-face-half-squares` 的做法）。
- 动作帧由 Claude 自己照英雄联盟的动作拼（`tools/lol/anim_graph.py Qiyana`，`pose_ref.py --champ Qiyana` **不要** `--hide-submeshes`：皮肤把圆环藏起来了）；腿和待机一致、不变形；一张脸用在所有帧。数据里的动作名见 `tools/kit/build_qiyana.py`：idle run attack skill skill2 ult hit dead（英雄联盟：Idle / Run / Attack1–3 / Spell1 / Spell3（+ Spell2 的附魔）/ Spell4 / Death）。
