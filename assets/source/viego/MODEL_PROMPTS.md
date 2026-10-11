# 佛耶戈：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`viego/1_picture.png`：英雄联盟的待机，银白乱发 + 青绿荆棘王冠，深藏青敞开的长风衣、苍白胸口 + 倒三角印记、棕红钉扣皮带，青绿发光的破败王剑扛在远侧肩上，剑身朝右上越过头顶，大十字护手在脑后）在**游戏尺寸**重新画。A、B 只差**剑身的长短**。
> - **大小**：两版都是**从王冠顶到脚底 40 格**。剑尖可以比王冠高，但**不超过 5 格**（橙线）。脚底在第 99 行（y=792–799，红线），两脚中间在中间那一列（x=512，蓝线），绿线 = 王冠顶。姿势和位置照 `viego/2_target_A.png` / `2_target_B.png`（原画直接缩到这个大小的灰剪影，浅灰的是剑）。**人不要超过 40 格高**：本包的萨勒芬妮、格温画到 45–46 行，在游戏里太大，后来都缩到了 42。
> - **宽度**：整个造型连剑和护手**不能超出两条紫线**：**A 最宽 48 格**（剑和原画一样长，原画缩下来约 47 格）；**B 最宽 40 格**：护手、剑柄和握剑的手不变，**剑身短三分之一**（剑尖还是朝右上，只是没那么远）。
> - **头大一点（游戏比例）**：原画的头只有身高的 1/5（缩到 40 格只有 7 格高），**看不清脸和眼睛**。请把头（王冠顶到下巴）画到 **10–11 格高**，身体相应短一点（腿稍短，像 `3_quality_bar.png` 里的泰隆、慎），总高度还是 40 格。
> - **干净、不要细节（最重要）**：最多 32 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。**风衣是偏紫的深藏青；铠甲（肩、前臂、护膝、靴）是更蓝一点的深藏青 + 银灰亮边；皮带棕红 + 银钉；皮肤苍白偏冷；头发银白；王冠、眼睛和胸口印记的边是亮青绿；剑是鲜亮的青绿 + 白绿的高光线 + 暗绿描边**。深色部分之间一定要有亮边（不能糊成一团黑）。去掉这个尺寸看不清的细节：腹肌 = 苍白的胸口 2 档平涂 + 中间一条阴影；风衣的花纹 = 不画，只留一两条银灰亮边；皮带 = 两行棕红 + 一排 1 格的银钉；靴子 = 每只 5–6 格的尖头深藏青 + 1 格亮边；护手 = 一个大大的青绿十字（四个尖钩），不画里面的小刻纹。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，王冠顶到脚底只有 40 格**。
> - **头和脸**：3/4 朝右，**银白乱发**盖住额头、垂到两颊；头顶**青绿荆棘王冠**（一圈 3–5 根尖刺，比头发亮）；**苍白的脸**，**两只发青绿光的细眼**（各 1–2 格）清楚看得见，冷淡的表情；高高的深藏青立领。脸不能被剑或手挡住。
> - **剑和手**：近侧（画面左边那只）手在肩前握剑柄，**握剑的手看得见**（黑色尖指手套）；大十字护手在他脑后 / 肩后（画面左上），剑身从肩头朝右上方伸出、越过头顶；远侧手垂在身旁。
> - **直接按游戏尺寸画**，不要先画大再缩小。`viego/6_size_guide.png` 是原画直接缩到 40 格的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 44 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 32 色，描边只用一种近黑色。交付到 `outputs/viego-model/`：`viego_design_A.png`、`viego_design_B.png`（1024×1024）和各自的原尺寸图 `viego_design_A_1x.png`、`viego_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来王冠顶到脚底是多少格、剑尖高出王冠几格、整个造型多宽），最好再打成一个 zip（`viego_design_pack.zip`）。

## 附图（都在压缩包的 `viego/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：银白乱发、青绿荆棘王冠、苍白的脸 + 青绿眼睛、深藏青立领长风衣（敞开）、苍白胸口 + 倒三角印记、带刺的肩甲 / 臂甲 / 护膝、黑色尖指手套、棕红钉扣皮带、尖头铠甲靴、扛在肩上的青绿破败王剑 + 大十字护手 |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到王冠顶到脚底 40 格的灰剪影（浅灰 = 剑）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 王冠顶，橙线 = 剑尖最高能到哪，两条紫线 = 最宽的范围（48 格） | **A 的大小、姿势和位置照它** |
| `2_target_B.png` | 同一个剪影，紫线 = 40 格 | **B 的大小和位置照它，剑身短三分之一放进紫线** |
| `3_quality_bar.png` | 本包里的泰隆、劫、慎、赵信、雷克顿，游戏里现在的样子 ×8，同一条脚底线 | **像素大小、头身比和干净程度照它们**（泰隆、劫、慎都是暗色系的近战，赵信拿长兵器） |
| `4_head.png` | 原画的头，放大 | 头发、王冠、脸、眼睛、立领 |
| `5_parts.png` | 原画的十字护手 + 握剑的手、剑身、胸口和皮带、远侧手臂、两条腿和靴子，放大 | 这些部件的形状和颜色 |
| `6_size_guide.png` | 原画直接缩到 40 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的待机（模型渲染） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：王冠顶到脚底 40 格（剑尖最多再高 5 格），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画、头放大**：3/4 正面朝右；站姿松垮、有点傲慢，两脚踩在地面线上；近侧手在肩前握剑，剑扛在远侧肩上、剑身朝右上；远侧手垂在身旁；**脸、两只手都看得见**。
- **干净**：最多 32 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0A0912 outline (the only near-black); coat #1C1A36 #2C2A52 #45437A #6A6AA8; armour #1A2440 #2C3C66 #8C9CC8 (#8C9CC8 = the silver-grey edge); gloves #14141E #2A2A3C; skin #C8C4D2 #E8E6EE #FFFFFF (#FFFFFF highlight only); hair #9AA0B4 #CED2DE #F4F6FA; belt #5A1E1E #8C3430 #B85448 + studs #8C9CC8; teal #0E6A5E #1EB89C #5CF0C8 #C8FFF0 (the sword, the crown, the eyes, the chest mark's edge).
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，风衣下摆也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`viego_design_A.png` 和 `viego_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`viego/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Viego, a pale, gloomy, proud undead king: MESSY SILVER-WHITE HAIR, a GLOWING TEAL-GREEN THORN CROWN, a PALE face with narrow GLOWING TEAL EYES, a long DARK NAVY high-collared COAT worn open over a BARE PALE CHEST with a black inverted-triangle mark edged in teal, SPIKED DARK NAVY ARMOUR on the shoulders, forearms and knees with silver-grey edges, BLACK pointed gauntlets, a wide REDDISH-BROWN BELT with silver studs, pointed dark navy armoured boots, and a HUGE GLOWING TEAL-GREEN GREATSWORD with a big CROSS-SHAPED teal guard (four hooked arms), resting on his far shoulder: his near hand grips it in front of the shoulder, the guard sits behind his head, the blade points up to image right over his head. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the sword in lighter grey - use it for his SIZE, his POSE and his PLACE in the canvas; everything must fit between the two purple lines and below the orange line. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size, their head-to-body proportions and their crisp, clean look (the first three are dark-clothed melee fighters). FOURTH: the FIRST image's head, big - the hair, the crown, the face, the eyes, the collar. FIFTH: the FIRST image's guard with the gripping hand, the blade, the chest and belt, the far arm, the legs and boots, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the body is built, NOT its 3D shading.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: exactly 40 squares from the top of his crown to his soles (the blade's tip may rise at most 5 squares above the crown), and at most the WIDTH number of squares across (guard and blade included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose: a loose, weary yet arrogant stance in 3/4 FRONT view facing image right, both feet on the ground line; the NEAR hand (image left) gripping the sword in front of his shoulder, the cross guard behind his head and shoulder (image upper left), the blade rising from his shoulder up to image right over his head; the far arm hanging at his side; the face turned toward the viewer, both eyes visible; both hands visible.
Game proportions: a BIGGER HEAD than the picture - from the crown's top to the chin 10-11 squares - and a slightly shorter body (shorter legs), like the fighters in the THIRD image, the total still 40 squares crown to soles; the teal eyes, the crown's spikes, the chest mark and the guard's four hooks drawn big enough to read.
Clean, not detailed (most important): at most 32 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the dark parts apart with clear light edges - never one black blob: the violet-tinged dark navy coat, the bluer dark navy armour with silver-grey edges, the near-black gloves, the reddish-brown belt, the cool pale skin, the silver-white hair, the vivid teal crown, eyes, chest-mark edge and sword. Drop what does not read at this size: the abs = the pale chest in 2 shades with one shadow line down the middle; the coat no pattern, one or two silver-grey edge lines; the belt two rows of reddish brown with a row of 1-square silver studs; each boot 5-6 pointed dark navy squares with a 1-square light edge; the guard one big teal cross with four hooks, no inner carving; the blade a straight teal bar with a light centre line and a darker edge.
Palette (from the FIRST image, adjust if needed): #0A0912 outline (the only near-black); coat #1C1A36 #2C2A52 #45437A #6A6AA8; armour #1A2440 #2C3C66 #8C9CC8 (#8C9CC8 = silver-grey edge); gloves #14141E #2A2A3C; skin #C8C4D2 #E8E6EE #FFFFFF (#FFFFFF highlight only); hair #9AA0B4 #CED2DE #F4F6FA; belt #5A1E1E #8C3430 #B85448; teal #0E6A5E #1EB89C #5CF0C8 #C8FFF0 (sword, crown, eyes, chest-mark edge).
Face (most important detail), as the FOURTH image: the head in 3/4, silver-white hair over the forehead and down beside the cheeks, the teal thorn crown on top (3-5 spikes, brighter than the hair), a pale face with two narrow GLOWING TEAL eyes (1-2 squares each) clearly visible and a cold mouth, the high dark collar under the chin. Nothing covers the face.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the crown's top on the green line, the blade's tip no higher than the orange line, nothing outside the two purple lines. Nothing below the soles (the game draws the health bar right under them): the coat's hem stays above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the crown's top to the soles (compare with the SECOND image); the blade's tip at most 5 squares above the crown; at most WIDTH squares across; all squares 8x8 on one grid; at most 32 colours; one outline colour; the hair, the crown, the teal eyes, the chest mark, the belt, the gripping hand, the guard and the blade all readable; nothing below the soles.
VERSION A (viego_design_A.png): WIDTH 48, the sword as long as in the FIRST image (use the SECOND image 2_target_A).
VERSION B (viego_design_B.png): WIDTH 40 (use the SECOND image 2_target_B): the guard, the grip and the hands as in version A, the BLADE a third shorter so that its tip stays inside the right purple line; everything else as version A.
```

## 交回前自查

- [ ] 王冠顶到脚底 40 格（最多 44）；剑尖最多高出王冠 5 格；A 不超过 48 格宽、B 不超过 40 格宽；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 32 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；头（王冠顶到下巴）10–11 格高；深色部分之间有亮边；
- [ ] 银白乱发 + 青绿荆棘王冠 + 苍白的脸 + 两只青绿眼睛；敞开的深藏青立领风衣 + 苍白胸口 + 倒三角印记；棕红钉扣皮带；带刺的铠甲和尖头靴；握剑的手看得见；青绿大剑 + 十字护手扛在肩上；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- 先给用户看 Codex 自己整理好的 A、B，再附我按格子读回的版本；和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步：idle run attack skill(Q) skill2(E 雾 + W 冲刺) ult hit dead possess）。
