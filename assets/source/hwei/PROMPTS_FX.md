# 异画师 彗：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型已定（`design/hwei_design.png`：瘦高的年轻画师，墨绿乱发、靛蓝外套和青绿翻领、橙色衬衫、一支红蓝笔头的大画笔斜指地面、背后一道弯月形的墨痕）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连墨痕 51 格高、42 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/hwei_size.png`：彗放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里彗自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**彗是画家，所有特效都是颜料**：粗笔触、干笔的毛边、颜料团和颜料滴，不要光滑的霓虹能量。颜色按主题分：**灾（Q）红橙色的火焰颜料和金白色的雷**，**靖（并进被动）青蓝色**，**悚（E）紫红色**，**大招深靛蓝的底、紫红和橙色的笔触、金线**，**落款金色**；他自己的墨是靛蓝色。
> - **特效要亮**：每道颜料都有最亮一档或白色的高光，暗底上一眼能看见。
> - **颜料、光、雷、火都没有黑描边**（鬼脸、獠牙、眼睛也是颜料画的，不要描黑边）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像；鬼脸、眼睛、大嘴都画正面）。**弹道**（`a_ink`、`q_q_ball`、`e_q_face`、`r_paint`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `hwei_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/hwei_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/hwei_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 画笔甩出一团墨 | `a_ink` · `a_hit` |
| 被动「落款」 | 伤害技能打中英雄留下落款，再打中一次就引爆 | `p_mark` · `p_burst` |
| 技能 1 =「主题：灾」 | 被控住的英雄 → 攒聚雷（金雷劈下）；有英雄 → 没骨火（火球）；清线清野 → 连皴山（熔岩地带，减速） | `q_w_tell` · `q_w_hit` · `q_q_ball` · `q_q_hit` · `q_e_lava` · `slow` |
| 技能 2 =「主题：悚」 | 贴脸的英雄 → 阴沉变意（狞笑鬼脸，恐惧）；否则轮流：滞涩幽瞳（头上睁眼，定身）/ 双钩血喉（獠牙咬合，定住减速） | `e_q_face` · `e_q_hit` · `e_w_open` · `e_w_hit` · `e_bound` · `e_e_open` · `e_e_hit` · `slow` |
| 被动里的「主题：靖」 | 每次放悚：渲浓（脚下水池，自己和队友护盾）；每次放灾：飞染（加速） | `w_pool` · `w_shield` · `w_haste` |
| 大招 =「焚心绚华绘」 | 颜料团飞向英雄，打中的地方展开旋转画卷（持续伤害、减速），3 秒后爆炸 | `r_paint` · `r_canvas` · `r_burst` · `r_hit` · `slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**颜料、光、雷、火没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **都是颜料**：粗笔触、干笔的毛边、颜料团和颜料滴；每段笔触 2–3 档平涂，亮的一边浅一档。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 灾·火焰颜料：`#FFFFFF`、`#FFF0B8`、`#FFB848`、`#FF6A20`、`#D8281C`、`#7A0E14`；
  - 灾·金雷：`#FFFFFF`、`#FFF8D8`、`#FFE07A`、`#F2B630`、`#B8781A`；
  - 靖·青蓝：`#FFFFFF`、`#DDFBFF`、`#8CEAF2`、`#3CC4D8`、`#1F86B8`、`#18467E`；
  - 悚·紫红：`#FFFFFF`、`#FFD8FA`、`#F07AE8`、`#B83CD8`、`#6A22A8`、`#2E1060`；
  - 他的墨·靛蓝：`#5A5E9A`、`#33366E`、`#1C1D44`、`#0E0E24`；
  - 落款·金色：`#FFFFFF`、`#FFF4C8`、`#FFD86A`、`#E0A42C`、`#9A6416`；
- 打中、爆发居中画，不旋转；地面上的圈（落款印、熔岩、水池、画卷）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：画卷半径 25000，熔岩半径 20000）。

### 1. `hwei_fx_a_ink.png`：普攻：甩出去的一团墨，4 帧循环

画笔甩出的一团靛蓝色的墨，后面拖一道笔触，边上一点金色的颜料点。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24), a gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416).
Effect: AN INK BLOB flung by a brush, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round indigo blob 4 squares across with a lighter highlight square in front, a tapering dry-brush stroke 7 squares long behind it, two gold paint specks beside the stroke at mirrored places; the stroke's ragged end shifts a little each frame. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 4 equal 12:6 cells, image size 768x96 (each cell 192x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `hwei_fx_a_hit.png`：普攻：墨团打中，3 帧

墨团溅开：一圈靛蓝色的墨点向外溅，中间一个金色的小闪。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24), a gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416).
Effect: AN INK SPLASH, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 3 squares across inside an indigo blot 5 across; 2 the blot burst into 8 indigo droplets at mirrored places, 8 squares across; 3 only 6 small droplets further out, fading to the darkest shade. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `hwei_fx_p_mark.png`：被动落款：敌人脚下的落款印，6 帧循环

被落款的敌人脚下：一圈金色的笔触圆环（从斜上方看的椭圆），中间一个金色的印章字形（参考 p_indicator01，**画成左右对称的篆字形状**）。金光在圈上慢慢流动。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: A PAINTER'S SEAL on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a gold dry-brush ring 20 squares wide and 7 tall, drawn as one thick stroke that does not quite close at the back, and in its middle a small upright gold seal glyph (like a carved signature stamp, 4 squares wide, symmetric), dark indigo ink under the ring; a brighter gold highlight runs round the ring through the frames, mirrored on both sides. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 6 equal 20:8 cells, image size 1920x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `hwei_fx_p_burst.png`：被动落款引爆：印章炸开，7 帧

落款完成：脚下的金色印章亮起，一道金色和靛蓝的颜料柱从地上冲起来炸开，碎成金点。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: A SIGNATURE BURSTING, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 the gold seal ring on the ground (22 wide, 7 tall) flashing white-gold; 2 a column of gold and indigo paint 8 squares wide shooting up from it to 14 squares; 3 the column 22 squares tall, its top splitting into two curling strokes; 4 it bursts: gold and indigo paint blobs flung out in a ring 26 squares across; 5 the blobs falling, a gold flash at the bottom; 6 gold specks and drips; 7 a few gold specks fading. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 7 equal square cells, image size 3136x448 (each cell 448x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `hwei_fx_q_q_ball.png`：灾·没骨火：火焰颜料球，4 帧循环

一团红橙色的火焰颜料朝前飞，后面拖着火舌一样的笔触（参考 qe_firelicks）。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange fire-paint ramp (#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14).
Effect: A FIREBALL OF PAINT, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round ball 6 squares across, white-yellow core, orange and red rings, in front; behind it three flame-lick brush strokes trailing 9 squares to the left, the middle one longest, the outer two mirrored; the licks flicker each frame. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `hwei_fx_q_q_hit.png`：灾·没骨火：火球炸开，5 帧

火焰颜料炸开：一团红橙色的火向四周溅开，火舌往上卷。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange fire-paint ramp (#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14).
Effect: A FIRE-PAINT EXPLOSION, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a white-yellow flash 6 across at the middle; 2 a burst of orange-red paint 14 across with flame licks pointing out; 3 the flames 18 across, licks curling upward, drops of red paint flung out at mirrored places; 4 the flames sinking into dark red smoke-paint; 5 a few embers and drips. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `hwei_fx_q_w_tell.png`：灾·攒聚雷：目标头顶的预警，6 帧

雷要劈下来之前：目标头顶上方聚起一团金色的颜料云，金线往中间收，越来越亮。**左右对称**，6 帧（约 0.75 秒）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold-white lightning ramp (#FFFFFF, #FFF8D8, #FFE07A, #F2B630, #B8781A), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: A GATHERING BOLT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (its head at the bottom of the cell): a small indigo paint cloud 10 squares wide hanging 6 squares above the head, gold strands spiralling into it from both sides, mirrored; frame by frame the strands get shorter and the cloud's gold core brighter, frame 6 a white-gold spark in the cloud with a thin gold line hinting down. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 6 equal 16:24 cells, image size 1536x384 (each cell 256x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `hwei_fx_q_w_hit.png`：灾·攒聚雷：金雷劈下，6 帧

一道金白色的雷从上面劈到目标身上（参考 innerbolt，**画成竖直、左右对称的锯齿**），落地炸开一圈金色的颜料。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold-white lightning ramp (#FFFFFF, #FFF8D8, #FFE07A, #F2B630, #B8781A), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: A GOLD LIGHTNING BOLT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (feet on the bottom of the cell): 1 a thin white line from the top of the cell to the feet; 2 the full bolt 6 squares wide, a white core with gold edges, zigzag bends mirrored on both sides, as if painted in one vertical stroke; 3 the bolt at its brightest with a gold splash ring 22 wide and 6 tall at the feet; 4 the bolt thinning, gold sparks flying out; 5 only the splash ring and drips; 6 a few gold specks. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 6 equal 24:48 cells, image size 2304x768 (each cell 384x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `hwei_fx_q_e_lava.png`：灾·连皴山：熔岩地带，12 帧（2.5 秒）

地上画出一片熔岩：像山水画的皴法一样的裂开的岩块，缝里流着红橙色的岩浆，火舌往上冒（参考 qe_firelicks、groundcrack）。先裂开、再烧一阵、最后暗下去。**左右对称**，12 帧，一共约 2.5 秒。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange fire-paint ramp (#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: A LAVA FIELD painted on the ground, 12 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an oval on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 40 squares wide and 13 tall; 1-2 dark ink cracks spreading from the middle; 3-4 the cracks glowing orange, dark rock plates between them drawn with short parallel brush strokes like an ink landscape; 5-9 molten red-orange lava in the cracks, small flame licks rising 4-6 squares at mirrored places, flickering frame by frame; 10-11 the flames gone, the cracks dimming to dark red; 12 only faint dark cracks. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 12 equal 44:20 cells, image size 8448x320 (each cell 704x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `hwei_fx_slow.png`：减速：脚下的墨滴，4 帧循环

被减速的敌人脚下：一滩靛蓝色的墨，几滴墨往下滴，像脚被墨粘住。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: STICKY INK on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an indigo ink puddle 14 squares wide and 4 tall, two short ink drips rising up the legs' place at mirrored spots and sliding down through the frames, a lighter highlight square on the puddle. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `hwei_fx_e_q_face.png`：悚·阴沉变意：飞出去的紫色笔触，4 帧循环

一道紫红色的颜料笔触往前飞，前头一团亮的颜料，后面拖两道卷曲的尾巴。**朝右飞，上下对称**（脸在打中时才出现），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060).
Effect: A VIOLET PAINT STREAK, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a bright magenta-white blob 4 squares across in front, two curling violet tails 10 squares long behind it, mirrored top and bottom, their curls shifting each frame. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `hwei_fx_e_q_hit.png`：悚·阴沉变意：狞笑的鬼脸，6 帧

打中的敌人身前浮出一张**紫色颜料画的狞笑鬼脸**（参考 eq_mouth：两只歪着的眼睛、一张大大的弯嘴，**正面、左右对称**），脸一闪一闪，敌人被吓跑。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: A GRIM VISAGE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (the face in front of its chest): a ghostly face painted with a few thick violet-magenta strokes, seen from the front: two slanted hollow eyes (each a curved stroke ring 4 squares across) and one huge grinning crescent mouth 14 squares wide with a few teeth, no outline of a head, dark indigo ink inside the eyes and the mouth; 1 strokes appearing; 2 the face whole; 3 the face 2 squares bigger, the eyes flashing magenta-white; 4 like 2; 5 the strokes breaking into drips; 6 a few violet drips falling. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `hwei_fx_e_w_open.png`：悚·滞涩幽瞳：头上睁开的眼睛，8 帧

目标头顶上方慢慢睁开一只**紫色的大眼睛**（参考 ew_eyeicon：一只竖着的眼，上下左右四道尖光），越睁越大，盯着它（约 0.65 秒）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: AN EYE OPENING, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (its head at the bottom of the cell): above the head a painted almond-shaped eye seen from the front, 12 squares wide, its two lids violet strokes, the iris a magenta ring round a dark indigo pupil, a white highlight square, four thin violet rays (up, down, left, right) like a four-pointed star round it; 1 a closed lid line; 2-4 the lids opening wider; 5-8 the eye fully open, the iris glowing brighter each frame, the rays growing longer. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 8 equal 20:28 cells, image size 2560x448 (each cell 320x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `hwei_fx_e_w_hit.png`：悚·滞涩幽瞳：眼睛射下定身，5 帧

眼睛睁到最大，一道紫色的光柱从眼睛射到目标身上，脚下一圈紫色的颜料把它定住。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: THE GAZE STRIKING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (feet on the bottom of the cell): 1 the eye at the top wide open, flashing magenta-white; 2 a violet beam 6 squares wide from the eye down to the feet; 3 the beam bright, a violet paint ring 18 wide and 5 tall splashed on the ground at the feet; 4 the beam thinning, the eye closing; 5 only the ground ring and the eye's lid line. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 5 equal 20:40 cells, image size 1600x640 (each cell 320x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `hwei_fx_e_bound.png`：悚·定身：腿上缠的紫色颜料，4 帧循环

被定住的敌人腿上：几道紫色的颜料笔触像藤一样缠住两条腿，脚下一滩墨。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: PAINT BINDING THE LEGS, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the lower half of a standing unit (its legs in the middle, not drawn), three violet brush strokes wrapped like loose bands at 3 heights, each 12 squares wide and drawn as an ellipse arc (front half only), an indigo puddle under them; the bands pulse lighter and darker in turn through the frames. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `hwei_fx_e_e_open.png`：悚·双钩血喉：獠牙张开，6 帧

目标身边张开一张**紫红色颜料画的大嘴**：上下两排弯钩獠牙（参考 ee_teeth01），一左一右把它围住，越张越大（约 0.5 秒）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: JAWS OPENING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: a huge mouth painted round the unit, seen from the front: an upper row of 5 curved hook fangs hanging from a violet stroke above its head and a lower row of 5 fangs rising from a stroke at its feet, the fangs ivory-white with magenta tips, the gums dark violet, the inside of the mouth empty (the unit shows through); frame by frame the jaws open wider (from 8 to 20 squares apart), the fangs trembling. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 6 equal 28:24 cells, image size 2688x384 (each cell 448x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `hwei_fx_e_e_hit.png`：悚·双钩血喉：獠牙咬合，5 帧

大嘴猛地合上：上下獠牙咬在一起，溅出紫红色的颜料。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24).
Effect: JAWS SNAPPING SHUT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 the jaws (as in e_e_open) slamming together at the unit's middle, the fangs interlocking; 2 a magenta-white flash where they meet, violet paint splashing out to both sides; 3 the jaws shut, splashes 26 squares across; 4 the jaws breaking into violet strokes and drips; 5 a few drips falling. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 5 equal 28:24 cells, image size 2240x384 (each cell 448x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `hwei_fx_w_pool.png`：靖·渲浓：脚下的青蓝色水池，6 帧

放悚时他脚下化开一片**青蓝色的颜料水池**（参考 w_shield），一圈涟漪往外荡开，几片花瓣漂着（参考 petal2x2）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-blue paint ramp (#FFFFFF, #DDFBFF, #8CEAF2, #3CC4D8, #1F86B8, #18467E).
Effect: A POOL OF REFLECTION, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), he stands in the middle, not drawn: a slim painter 42 squares wide and 51 tall with his crescent and brush: on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a teal splash 10 squares wide spreading under him; 2 a round pool of teal-blue paint 30 wide and 10 tall, a white highlight arc on its far edge; 3-4 a ripple ring travelling outward to 38 wide, two pale petals floating at mirrored places; 5 the pool fading at the edge; 6 a thin teal ring and the petals. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 6 equal 40:16 cells, image size 3840x256 (each cell 640x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `hwei_fx_w_shield.png`：靖·渲浓：队友身上的护盾，5 帧

队友身上罩上一层青蓝色的颜料光罩：一个椭圆的笔触圈从脚下升起包住身子，闪一下变淡。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-blue paint ramp (#FFFFFF, #DDFBFF, #8CEAF2, #3CC4D8, #1F86B8, #18467E).
Effect: A PAINTED SHIELD, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a teal ring on the ground at the feet; 2 the ring rising as a tall oval of teal-blue brush stroke round the unit (only the outline stroke, 3 squares thick, the middle empty); 3 the oval whole, a white highlight stroke on its upper left and its mirror on the upper right; 4 the stroke thinning; 5 a few teal specks. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 5 equal 22:40 cells, image size 1760x640 (each cell 352x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `hwei_fx_w_haste.png`：靖·飞染：脚下的青色笔触，4 帧循环

加速时他脚边：几道青蓝色的笔触往两边扫开，像风吹过水面。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-blue paint ramp (#FFFFFF, #DDFBFF, #8CEAF2, #3CC4D8, #1F86B8, #18467E).
Effect: A FLEETING CURRENT on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): four short teal-blue brush strokes, two on each side of the feet, sweeping outward along the ground, each 6 squares long, their dry-brush tails flicking further out frame by frame. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 4 equal 24:8 cells, image size 1536x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `hwei_fx_r_paint.png`：大招·焚心绚华绘：飞出去的颜料团，4 帧循环

一团旋转的颜料往前飞：深靛蓝的芯，外面绕着紫红和橙色的笔触，夹几缕金线。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24), a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), a red-orange fire-paint ramp (#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14), a gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416).
Effect: A SPIRALING PAINT BOLT, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a dark indigo ball 6 squares across with a magenta rim in front, round it two brush strokes - magenta and orange - spiralling into a tail 12 squares long, mirrored top and bottom, a gold strand between them; the spiral turns a quarter each frame. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 4 equal 20:10 cells, image size 1280x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `hwei_fx_r_canvas.png`：大招·焚心绚华绘：展开的画卷，14 帧（3 秒）

打中的地方地上展开一幅**旋转的画卷**：深靛蓝的底，紫红和橙色的笔触一圈圈往外旋，金线流动，越转越大（参考 r_cracks、goldstrand）。约 3 秒，最后几帧颜色越来越亮、快要炸开。**左右对称**，14 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24), a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), a red-orange fire-paint ramp (#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14), a gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416).
Effect: A SPIRALING CANVAS painted on the ground, 14 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an oval on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) growing from 20 squares wide (frame 1) to 52 wide and 17 tall (frame 6) and staying; a dark indigo ink ground, on it magenta and orange brush strokes curling round the middle in a mirrored double spiral, thin gold strands between them, cracks of light in the middle; through the frames the strokes turn and shimmer; frames 12-14 everything brighter, the cracks white-hot, as if about to burst. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 14 equal 56:22 cells, image size 12544x352 (each cell 896x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `hwei_fx_r_burst.png`：大招·焚心绚华绘：画卷爆炸，7 帧

画卷炸开：一大团紫红、橙色、靛蓝的颜料从地上炸起来，金线四射，颜料块往外甩。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an indigo ink ramp (#5A5E9A, #33366E, #1C1D44, #0E0E24), a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), a red-orange fire-paint ramp (#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14), a gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #E0A42C, #9A6416).
Effect: THE CANVAS EXPLODING, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the blast's base on the bottom middle of the cell: 1 a white-gold flash 18 across on the ground; 2 a fountain of magenta, orange and indigo paint 30 wide shooting up 24 squares; 3 the burst 50 wide and 40 tall, gold strands flying out, paint blobs flung to both sides; 4 the paint falling in big drops; 5 dark indigo smoke-paint with orange embers; 6 drips and specks; 7 a few specks. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 7 equal 56:44 cells, image size 6272x704 (each cell 896x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `hwei_fx_r_hit.png`：大招：被炸到的颜料溅，4 帧

被大招炸到的敌人身上：紫红和橙色的颜料溅开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta paint ramp (#FFFFFF, #FFD8FA, #F07AE8, #B83CD8, #6A22A8, #2E1060), a red-orange fire-paint ramp (#FFFFFF, #FFF0B8, #FFB848, #FF6A20, #D8281C, #7A0E14).
Effect: A PAINT SPLASH ON A UNIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a magenta-white flash 4 across; 2 magenta and orange paint splashing out 12 across at mirrored places; 3 drops further out; 4 a few drips. everything is PAINT: thick brush strokes with ragged dry-brush ends, blobs and drips of paint, never smooth neon energy; flat shades, the lit side of a stroke one shade lighter.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `hwei_fx_a_ink` | view_projectiles `league_hwei_a_ink`（弹道，z 2；上下对称） | 12 × 6 |
| `hwei_fx_a_hit` | view_effects `league_hwei_a_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `hwei_fx_p_mark` | view_buffs `league_hwei_p_mark`（跟随目标，z -1；左右对称） | 20 × 8 |
| `hwei_fx_p_burst` | view_effects `league_hwei_p_burst`（大表，跟随目标，z 3；左右对称） | 28 × 28 |
| `hwei_fx_q_q_ball` | view_projectiles `league_hwei_q_q_ball`（弹道，z 2；上下对称） | 16 × 8 |
| `hwei_fx_q_q_hit` | view_effects `league_hwei_q_q_hit`（跟随目标，z 2；左右对称） | 20 × 20 |
| `hwei_fx_q_w_tell` | view_effects `league_hwei_q_w_tell`（跟随目标，z 2；左右对称） | 16 × 24 |
| `hwei_fx_q_w_hit` | view_effects `league_hwei_q_w_hit`（大表，跟随目标，z 3；左右对称） | 24 × 48 |
| `hwei_fx_q_e_lava` | view_effects `league_hwei_q_e_lava`（大表，地上不跟随，z -1；左右对称） | 44 × 20 |
| `hwei_fx_slow` | view_buffs `league_hwei_q_e_slow` / `e_slow` / `r_slow`（跟随，z -1；左右对称） | 16 × 8 |
| `hwei_fx_e_q_face` | view_projectiles `league_hwei_e_q_face`（弹道，z 2；上下对称） | 16 × 8 |
| `hwei_fx_e_q_hit` | view_effects `league_hwei_e_q_hit`（跟随目标，z 3；左右对称） | 24 × 24 |
| `hwei_fx_e_w_open` | view_effects `league_hwei_e_w_open`（跟随目标，z 3；左右对称） | 20 × 28 |
| `hwei_fx_e_w_hit` | view_effects `league_hwei_e_w_hit`（跟随目标，z 3；左右对称） | 20 × 40 |
| `hwei_fx_e_bound` | view_buffs `league_hwei_e_bound`（跟随，z 3；左右对称） | 16 × 16 |
| `hwei_fx_e_e_open` | view_effects `league_hwei_e_e_open`（跟随目标，z 3；左右对称） | 28 × 24 |
| `hwei_fx_e_e_hit` | view_effects `league_hwei_e_e_hit`（跟随目标，z 3；左右对称） | 28 × 24 |
| `hwei_fx_w_pool` | view_effects `league_hwei_w_pool`（大表，跟随他，z -1；左右对称） | 40 × 16 |
| `hwei_fx_w_shield` | view_effects `league_hwei_w_shield`（跟随队友，z 3；左右对称） | 22 × 40 |
| `hwei_fx_w_haste` | view_buffs `league_hwei_w_haste`（跟随他，z -1；左右对称） | 24 × 8 |
| `hwei_fx_r_paint` | view_projectiles `league_hwei_r_paint`（弹道，z 2；上下对称） | 20 × 10 |
| `hwei_fx_r_canvas` | view_effects `league_hwei_r_canvas`（大表，地上不跟随，z -1；左右对称） | 56 × 22 |
| `hwei_fx_r_burst` | view_effects `league_hwei_r_burst`（大表，地上不跟随，z 3；左右对称） | 56 × 44 |
| `hwei_fx_r_hit` | view_effects `league_hwei_r_hit`（跟随目标，z 2；左右对称） | 14 × 14 |

- 两张表：`asset/league/effects/league_hwei_fx`（小的）和 `league_hwei_big`（p_burst、q_w_hit、q_e_lava、w_pool、r_canvas、r_burst），tag = 名字（build_hwei.py 的 views；q_q_ball2 用 q_q_ball，三种减速用 slow）。
- 弹道（a_ink、q_q_ball、e_q_face、r_paint）断言上下对称；其余断言左右对称；q_w_tell、e_w_open 放在目标头顶（view 的 y 偏移），q_e_lava 帧长合计 2.5 秒、r_canvas 3 秒（r_t 180 tick），w_pool 跟随他。
- 用 `pixel_1x/` 切格（import_neeko_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
