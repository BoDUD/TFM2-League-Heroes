# 迭嘉：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图 + 3 个技能图标。** 造型已定（`design/daeja_design.png`：3/4 朝右、直立站着的蓝色水晶龙人：冰蓝皮肤、深蓝紫的人字形胸甲、古铜尖刺；古铜面甲下品红发光的眼睛，浅青蓝的大团鬃毛；两只发光的青色水晶拳；背后两片高高竖起的翅膀（深紫翼骨、青到紫的扇形翼膜）；尾巴尖一片古铜尾鳍）。迭嘉在游戏里是**高清**的（每个游戏格子里约 1.72×1.72 个细像素），40 格高、34 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/daeja_size.png`：迭嘉缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里迭嘉自己的特效贴图（罡风轰击的冲击波、速度线、云、烟、大招的火花）（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **迭嘉是幻镜龙，特效都是风的魔法**：白色、浅青、天蓝的风和气流，弯弯的月牙形冲击波，小团的云，边上点缀他翅膀的**幻镜紫**；削魔抗的符印用他眼睛的**品红**；不要火、不要红色、不要金色，不要光滑的霓虹光束。
> - **特效要亮**：每团风都有最亮一档或白色的芯，暗底上一眼能看见。**风、冲击波、云没有黑描边**。
> - **围着人的画面只画头上、脚下，身体位置留空**，不要盖住人。
> - **对称**：画在人身上和地上的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；**飞行的画面（a_bolt、p_bolt、q_wave、e_gust、r_wave）朝右、严格上下对称**（游戏会按方向转）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `daeja_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `daeja_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/daeja_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/daeja_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「风弹」 | 拳头往前一推，射出一颗风弹 | `a_bolt` · `a_hit` |
| 被动「三连弹幕」 | 每次普攻再追加 3 颗小风弹，各带少量魔法伤害并削减魔抗（可叠加） | `p_bolt` · `p_hit` · `p_shred` |
| 技能 1 =「罡风轰击」 | 双翼往前一扫，朝敌人最多的直线打出一道穿透的风波 | `q_wave` · `q_hit` |
| 技能 2 =「振翼退风」 | 振翅朝敌人扇出一阵减速的风，自己往后跳 | `e_gust` · `e_slow` |
| 大招 =「苍穹罡风」 | 展开双翼飞起来，朝敌人最多的直线连续轰出 3 道大冲击波，然后落地 | `r_fly` · `r_wave` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 风（白、浅青、天蓝）：`#FFFFFF`、`#E6FCFF`、`#A8EEFF`、`#5CCBF2`、`#2C86D6`；
  - 幻镜紫（边上、翼膜的颜色）：`#F6EBFF`、`#D8B2FF`、`#A878F2`、`#6E48C8`；
  - 他眼睛的品红（削魔抗的符印）：`#FFE2FF`、`#FF7AF0`、`#E81CE8`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `daeja_fx_a_bolt.png`：普攻：风弹，4 帧循环

他拳头推出去的**风弹**：一颗白色芯的青色小风球，后面拖着两三道弯弯的气流尾巴。**朝右、上下对称**，4 帧循环（气流转动）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6).
Effect: A WIND BOLT, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a small ball of wind 5 squares across with a white core at the right, two or three short curling air streaks trailing behind it to the left (one above, one below, mirrored); frames 1-4 the streaks swirling. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `daeja_fx_a_hit.png`：普攻：风弹打中，4 帧

风弹打中：一下白光，一圈青色的小气流往外散开，几缕风丝四射。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6).
Effect: A WIND HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a small ring of cyan air bursting out round it, short wind wisps flying out in a symmetric star; 3 the ring wider and thinner; 4 a few fading wisps. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `daeja_fx_p_bolt.png`：被动：三连弹幕的小风弹，4 帧循环

被动「三连弹幕」的**小风弹**：比普攻的风弹小一圈，带一点幻镜紫色的边，后面一道细细的气流。**朝右、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6), a mirage violet ramp (#F6EBFF, #D8B2FF, #A878F2, #6E48C8).
Effect: A SMALL BARRAGE BOLT, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a tiny dart of wind 3 squares tall with a white tip at the right and a thin violet rim, one thin air streak trailing behind it to the left; frames 1-4 the streak flickering. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 4 equal 8:6 cells, image size 512x96 (each cell 128x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `daeja_fx_p_hit.png`：被动：小风弹打中，3 帧

小风弹打中：一个小小的青紫色闪光，两三缕风丝。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6), a mirage violet ramp (#F6EBFF, #D8B2FF, #A878F2, #6E48C8).
Effect: A SMALL WIND HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small white-cyan flash 3 squares across with a violet rim; 2 four tiny wisps flying out in a symmetric cross; 3 the wisps fading. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `daeja_fx_p_shred.png`：被动：魔抗被削（可叠加），6 帧循环

魔抗被削：被打中的人**头顶上**一个小小的品红色裂开的魔法符印（一个圆形的符，中间一道裂缝），两边一点紫色的风丝慢慢转。**只在头顶**，身体位置留空。**左右对称**，6 帧循环（符印一闪一闪）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta ramp (#FFE2FF, #FF7AF0, #E81CE8), a mirage violet ramp (#F6EBFF, #D8B2FF, #A878F2, #6E48C8).
Effect: A BROKEN MAGIC WARD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the unit stands in the middle, not drawn: 16 squares wide and 36 tall; ABOVE THE HEAD only (the top 8 squares of the cell): a small round magenta rune 6 squares across split by a crack down its middle (the magic resistance broken), two thin violet wisps circling it, one each side; frames 1-6 the rune flickering bright and dim. The body area below stays EMPTY. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 6 equal 14:30 cells, image size 1344x480 (each cell 224x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `daeja_fx_q_wave.png`：罡风轰击：飞出去的风波，4 帧循环

罡风轰击的**风波**：一道竖起来的大月牙形狂风（像一把弯刀，凸的一面朝右，往前冲），月牙里面是白色到青色的气流，边缘一点幻镜紫色，后面拖着几道横向的速度线。**朝右、上下对称**，4 帧循环（气流翻滚）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6), a mirage violet ramp (#F6EBFF, #D8B2FF, #A878F2, #6E48C8).
Effect: A WIND BLAST WAVE, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a tall CRESCENT of storming wind 20 squares tall and 7 thick, its bulge facing RIGHT (rushing forward), white along its front edge, cyan in its body, a violet rim at its two tips; behind it to the left three horizontal speed streaks (one in the middle, two mirrored); frames 1-4 the air inside rolling. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:22 cells, image size 1024x352 (each cell 256x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `daeja_fx_q_hit.png`：罡风轰击：打中，5 帧

风波打中：一下白色强光，一圈青色的气浪炸开，几片小云往外飞。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6).
Effect: A WIND BLAST HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2-3 a ring of cyan air bursting out to 18 squares wide, small puffs of cloud and wind wisps flying out symmetrically; 4-5 the ring breaking into fading wisps. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `daeja_fx_e_gust.png`：振翼退风：往前扇出的一阵减速的风，6 帧

他振翅往前扇出的**一阵风**：从左端（他身前）往右吹出一道越来越宽的风带，里面是一道道弯弯的白色和青色气流，几片小云，右端散开。左端窄（约 6 格高），右端宽（约 14 格高）。**朝右、上下对称**，6 帧（吹出去、散开）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6), a mirage violet ramp (#F6EBFF, #D8B2FF, #A878F2, #6E48C8).
Effect: A WING GUST, 6 frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a band of wind blowing from the LEFT edge (6 squares tall there: in front of him) to the RIGHT, widening to 14 squares tall at the right end; inside it curving streaks of white and cyan air and a few small cloud puffs, violet at its outer edges; 1-2 the gust pushing out from the left, 3-4 filling the whole length, 5-6 thinning and breaking into wisps at the right. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 6 equal 46:16 cells, image size 4416x256 (each cell 736x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `daeja_fx_e_slow.png`：振翼退风：被风缠住减速，6 帧循环

被减速：被吹到的人脚下一圈绕着打转的青色旋风（从斜上方看的椭圆，宽是高的 3 倍），风丝缠着往下压。**左右对称**，6 帧循环（旋风转动）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6).
Effect: A CLINGING WIND, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND round the unit's feet, an ellipse seen from above, about 18 squares wide and 6 tall: a ring of swirling cyan wind wisps winding round the feet, a few small downward-curling streaks; frames 1-6 the wisps circling (keep every frame left-right symmetric). Nothing above the feet. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:10 cells, image size 1920x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `daeja_fx_r_wave.png`：苍穹罡风：大冲击波，4 帧循环

大招的**大冲击波**：比罡风轰击更大更猛的一道双层月牙形狂风（一大一小两道月牙叠着，凸的一面朝右），白色的芯、青色的身子、幻镜紫色的边，前面一圈压出来的气浪，后面几道长长的速度线。**朝右、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6), a mirage violet ramp (#F6EBFF, #D8B2FF, #A878F2, #6E48C8).
Effect: A SKY GALE WAVE, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): TWO nested CRESCENTS of storming wind, the big one 28 squares tall and 8 thick, a smaller one inside it, their bulges facing RIGHT; white along the front edges, cyan bodies, violet rims and tips; a thin pressure ring just in front of them; long horizontal speed streaks trailing behind to the left (mirrored); frames 1-4 the air rolling. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 4 equal 22:30 cells, image size 1408x480 (each cell 352x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `daeja_fx_r_hit.png`：苍穹罡风：打中，6 帧

大冲击波打中：一下大白光，一圈青紫的气浪炸开，往上卷起一个小旋风，碎云四散。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6), a mirage violet ramp (#F6EBFF, #D8B2FF, #A878F2, #6E48C8).
Effect: A SKY GALE HIT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white flash 8 squares across; 2-3 a ring of cyan and violet air bursting out to 28 squares wide, a small whirlwind twisting up from the middle; 4-6 the ring and the whirl breaking into fading cloud puffs and wisps. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 6 equal square cells, image size 2880x480 (each cell 480x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `daeja_fx_r_fly.png`：苍穹罡风：飞行时脚下的旋风，6 帧循环

他飞在空中时，**脚下**一大圈被翅膀扇起来的旋风（从斜上方看的椭圆，宽是高的 3 倍），风丝和小云绕着转，边上一点紫色。**左右对称**，6 帧循环（风绕着转）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a wind ramp (#FFFFFF, #E6FCFF, #A8EEFF, #5CCBF2, #2C86D6), a mirage violet ramp (#F6EBFF, #D8B2FF, #A878F2, #6E48C8).
Effect: A DOWNDRAFT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon-man stands in the middle, not drawn: 34 squares wide and 40 tall, his head in the middle - only UNDER his feet: an ellipse seen from above, about 42 squares wide and 12 tall, a ring of swirling cyan wind with small cloud puffs blown out to both sides, violet at its rim; frames 1-6 the wisps circling (keep every frame left-right symmetric). Nothing above the ellipse. everything is a WIND DRAGON's magic: gusts and crescents of pale cyan and white wind, curling air streaks, small puffs of cloud, a touch of mirage VIOLET at the edges; flat shades, crisp curved shapes; no fire, no red, no gold, no smooth neon beams.
Layout: one horizontal row of 6 equal 44:14 cells, image size 4224x224 (each cell 704x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `daeja_icon_skill.png`：技能 1「罡风轰击」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bronze frame with little violet corners, a deep night-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big white-and-cyan wind crescent rushing to the right, speed streaks behind it, three small violet figures' outlines in a row being struck by it. No text, no letters.
```

### 图标 2. `daeja_icon_skill2.png`：技能 2「振翼退风」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bronze frame with little violet corners, a deep night-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: one blue-violet dragon wing (a dark violet bone, a cyan-to-violet fan membrane) beating, a gust of white wind blowing to the right from it and a curved arrow pointing back to the left. No text, no letters.
```

### 图标 3. `daeja_icon_ult.png`：大招「苍穹罡风」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bronze frame with little violet corners, a deep night-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a pair of blue-violet dragon wings spread wide high in a night sky, three wind crescents shooting out below them to the right. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `daeja_fx_a_bolt` | view_projectiles `tft_daeja_a_bolt`（飞向目标，随方向旋转；上下对称、朝右） | 10 × 8 |
| `daeja_fx_a_hit` | view_effects `tft_daeja_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `daeja_fx_p_bolt` | view_projectiles `tft_daeja_p_bolt`（飞向目标，随方向旋转；上下对称、朝右） | 8 × 6 |
| `daeja_fx_p_hit` | view_effects `tft_daeja_p_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `daeja_fx_p_shred` | view_buffs `tft_daeja_p_shred`（跟随被打中的人，头顶上，z 3；左右对称） | 14 × 30 |
| `daeja_fx_q_wave` | view_projectiles `tft_daeja_q_wave`（大表，穿透的直线风波，随方向旋转；上下对称、朝右） | 16 × 22 |
| `daeja_fx_q_hit` | view_effects `tft_daeja_q_hit`（在被穿过的人身上，z 3；左右对称） | 20 × 20 |
| `daeja_fx_e_gust` | view_projectiles `tft_daeja_e_gust`（大表，从他身上指向目标的一条线，随方向旋转；上下对称、朝右） | 46 × 16 |
| `daeja_fx_e_slow` | view_buffs `tft_daeja_e_slow`（跟随被减速的人，脚下地面，z 3；左右对称） | 20 × 10 |
| `daeja_fx_r_wave` | view_projectiles `tft_daeja_r_wave`（大表，穿透的直线大冲击波，随方向旋转；上下对称、朝右） | 22 × 30 |
| `daeja_fx_r_hit` | view_effects `tft_daeja_r_hit`（大表，在被穿过的人身上，z 3；左右对称） | 30 × 30 |
| `daeja_fx_r_fly` | view_buffs `tft_daeja_r_fly`（跟随他，在他身后，z -1；左右对称） | 44 × 14 |
| `daeja_icon_skill` | skill_icons[0] `asset/tft/icons/tft_daeja_skill` | 64 × 64 |
| `daeja_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_daeja_skill2` | 64 × 64 |
| `daeja_icon_ult` | skill_icons[2] `asset/tft/icons/tft_daeja_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_daeja_fx`（小的）和 `tft_daeja_big`（q_wave、e_gust、r_wave、r_hit），tag = 名字。
- a_bolt、p_bolt、q_wave、e_gust、r_wave 断言上下对称（朝右），其余断言左右对称。
- q_wave、r_wave 由 tft.dll 发出（朝敌人最多的直线飞的穿透风波）；e_gust 是从他身上出发的一条线（左端对着他身前）；p_shred 是叠加的减魔抗 buff（每层一个，画面会叠在一起：画得淡一点）；r_fly 是他飞行时身上的 caster buff（z -1，在他身后）。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
