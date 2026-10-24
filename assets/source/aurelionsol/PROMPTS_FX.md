# 铸星龙王 奥瑞利安·索尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型已定（`design/aurelionsol_design.png`：浅蓝白骨质龙脸、亮青色眼睛、金冠金角、洋红鬃毛，深海军蓝鳞甲和青色发光线，紫色龙爪，胸口以下深蓝到紫罗兰的星云尾巴）。他在游戏里是**高清**的（每个游戏格子里约 1.75×1.75 个细像素），44 格高、32 格宽（高×宽，冠盔顶到尾尖）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/aurelionsol_size.png`：奥瑞利安·索尔放大 4 倍，最低点在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奥瑞利安·索尔自己的特效贴图（大多是灰度的形状），按用在我们哪张特效分好了行，只在本地用。**奥瑞利安·索尔是铸星龙王**：他的力量是**白金色的星光**（龙息和星星，清楚的四角星闪光）、**深蓝到紫罗兰的星云**、**青色发光的星座连线**、**品红的星云团**，黑洞是**近黑色的洞加一圈紫色光环**；不要火、不要电、不要烟。
> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见（黑洞除外：它中间就是黑的，但光环要亮）。
> - **星光、星云、冲击波、尘土都没有黑描边**（用它自己最深的一档）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`a_bolt`、`q_beam`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）；`e_orb` 是圆的，**左右、上下都对称**。**坠落的星星（`r_fall`）笔直往下，左右对称**。
> - **持续的画面**（黑洞 5 秒、飞行星尘、天瀑就绪的头顶星星、减速）只画几帧循环，Claude 导入时按时长拉开循环。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `aurelionsol_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/aurelionsol_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/aurelionsol_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 爪子甩出一颗小星星 | `a_bolt` · `a_hit` |
| 被动「星海焕然」 | 技能打中英雄收集星尘，永久变强；攒满星尘大招变天瀑；击杀后飞行（星穹流丽） | `d_gain` · `sky_ready` · `sky_glow` · `w_lift` · `w_trail` |
| 技能 1 =「星河冲荡」 | 引导龙息，持续喷向目标（同一目标越久越痛） | `q_beam` · `q_hit` |
| 技能 2 =「星芒凝汇」 | 在目标处放黑洞，持续伤害、把敌人往中心拉、减速，中心吞噬残血 | `e_orb` · `e_hole` · `e_core` · `slow` |
| 大招 =「星落 / 天瀑」 | 召一颗星星砸下（伤害、眩晕）；星尘满时变天瀑（更大、击飞，外圈冲击波减速） | `r_call` · `r_fall` · `r_impact` · `r_sky` · `r_wave` · `r_hit` · `slow` |

连招：**黑洞一放下 → 立刻接龙息**，**星落眩晕 → 立刻在落点放黑洞**，**星尘攒满 → 天瀑**，**击杀 → 起飞，飞行中龙息无冷却、伤害更高**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**星光、星云、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的亮点。
- 颜色（按每条写的用）：
  - 星光·白金：`#FFFFFF`、`#FFF6D8`、`#FFE08A`、`#F2B84A`、`#C07A2A`；
  - 星云·蓝紫：`#E6E8FF`、`#9EA8FF`、`#5C64F0`、`#3A2CC0`、`#24167A`、`#120A40`；
  - 发光·青：`#E8FFFF`、`#8AF4FF`、`#2ED0F0`、`#1488B8`、`#0A4A78`；
  - 星云团·品红：`#FFE6FA`、`#FF9AE8`、`#E848C8`、`#A01E98`、`#5A0C5C`；
  - 黑洞·近黑到紫：`#06030E`、`#140A2A`、`#2C1458`、`#5A2C9C`、`#9A64E0`；
  - 闪光·白：`#FFFFFF`、`#F4F8FF`、`#DCE6FF`；
  - 尘土·紫灰：`#E8E2F4`、`#B4A8D0`、`#7C6CA8`、`#4A3C74`；
- 打中、爆发居中画，不旋转；地面上的东西（黑洞、星爆、冲击波、脚下的光圈）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `aurelionsol_fx_a_bolt.png`：普攻：甩出的小星星，3 帧循环

爪子甩出去的一颗小星星（参考 ba_mis_streak、ba_energy、starspark）：前头一颗**白金色的四角星**，后面拖一条短短的蓝紫色星尘尾巴。**朝右飞、上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40).
Effect: A SMALL SHOOTING STAR, 3 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a white-gold four-pointed star 5 squares across at the front, a short blue-violet stardust trail 7 squares long behind it on the left; the star's points twinkle and the trail flickers frame to frame. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 3 equal 12:6 cells, image size 576x96 (each cell 192x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `aurelionsol_fx_a_hit.png`：普攻：星星打中，3 帧

小星星打中敌人（参考 sparkle、starspark、spark）：中间一下白色闪光，炸开一颗**白金色的四角星**，几粒蓝紫色星尘往外溅。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40).
Effect: A STAR POP, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares across; 2 a white-gold four-pointed star 11 across, a few blue-violet stardust specks flying out at mirrored places; 3 the star smaller and dimmer, the specks further out, fading. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `aurelionsol_fx_q_beam.png`：星河冲荡：龙息光束的一段，3 帧循环

星河冲荡（参考 q_beammask、q_beam_starnoise、q_hot_beammask、q_fire_noise）：从嘴里喷出去的**一段星光龙息**——中间一条**白金色的亮芯**，外面一层蓝紫色的光，边上闪着几颗小星星，前头尖、后头散开。每 1/6 秒发一段，连起来就是一道光束。**朝右飞、上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40).
Effect: A SEGMENT OF STARLIGHT BREATH, 3 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a beam 38 squares long - a white core band 2 squares thick down the middle, white-gold around it, a blue-violet glow outside (6 squares thick in all), a pointed bright head on the right, the tail end on the left fraying into specks; small four-pointed star sparkles along both edges at mirrored places, moving along frame to frame so the beam flows. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 3 equal 40:8 cells, image size 1920x128 (each cell 640x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `aurelionsol_fx_q_hit.png`：星河冲荡：被龙息烧中，3 帧

被龙息持续打中：身上一团**白金色的星光**一闪，几颗小星星和蓝紫色星尘往两边溅。**左右对称**，3 帧（打得很密，要短促）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40).
Effect: A STARLIGHT SEAR, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flare 8 squares across on the target's chest; 2 the flare with small star sparkles and blue-violet specks bursting out 13 across at mirrored places; 3 fading. It plays every sixth of a second - short and crisp. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `aurelionsol_fx_e_orb.png`：星芒凝汇：飞出去的黑洞种子，3 帧循环

从爪间飞出去、落地变成黑洞的那颗**小黑球**（参考 e_star_core、e_swirls）：近黑色的核，外面一圈紫色的光环，几颗小光点绕着转。**圆的：左右、上下都对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-hole ramp from near-black to violet (#06030E, #140A2A, #2C1458, #5A2C9C, #9A64E0), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF).
Effect: A BLACK-HOLE SEED, 3 looping frames, ROUND: SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square (the game turns it with its flight): a near-black round core 4 squares across, a violet glowing ring round it 8 across, four tiny white specks round the ring at mirrored places, their places turning frame to frame (each frame itself symmetric). everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `aurelionsol_fx_e_hole.png`：星芒凝汇：地上的黑洞，6 帧循环

星芒凝汇（参考 e_groundcracks、update_e_decal、e_swirls、e_cone、e_distortionin、e_tell_starnoise）：地上张开一个**黑洞**——中间是近黑色的洞，一圈紫色和蓝色的光环在旋转，**星尘和小星星沿着螺旋往洞里吸**，边上的地面裂出几道紫色的缝。要持续 5 秒，画成循环。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-hole ramp from near-black to violet (#06030E, #140A2A, #2C1458, #5A2C9C, #9A64E0), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a magenta nebula ramp (#FFE6FA, #FF9AE8, #E848C8, #A01E98, #5A0C5C), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A).
Effect: A BLACK HOLE ON THE GROUND, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), a near-black hole 22 squares wide and 8 tall in the middle, a glowing violet-blue accretion ring round it 46 wide, magenta nebula wisps and small white-gold stars spiralling inward along the ring (in frame k the left and right halves mirror each other, the specks a step further in each frame so the loop sucks inward), a few thin violet cracks in the ground round the edge 54 wide. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 6 equal 56:26 cells, image size 5376x416 (each cell 896x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `aurelionsol_fx_e_core.png`：星芒凝汇：黑洞中心吞噬，4 帧

黑洞中心把敌人往下吞（参考 e_flare、e_star_core）：脚下一团近黑的漩涡，**一道白紫色的光柱从敌人身上往下塌进去**，几颗星星往中间收。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-hole ramp from near-black to violet (#06030E, #140A2A, #2C1458, #5A2C9C, #9A64E0), a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40).
Effect: A CRUSHING CORE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a near-black swirl on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 12 wide; 2 a white-violet column through the target 22 squares tall, small stars pulled in toward it at mirrored places; 3 the column collapsing downward into the swirl; 4 the swirl closing, a last white glint. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 16:24 cells, image size 1024x384 (each cell 256x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `aurelionsol_fx_slow.png`：减速：脚下缠着的星尘，4 帧循环

被减速的敌人脚下：一圈**蓝紫色的星尘**绕着脚慢慢转，几颗小星星一闪一闪。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A).
Effect: A STARDUST SNARE, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat blue-violet stardust ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 wide and 5 tall, two tiny white-gold stars at mirrored places twinkling in turn. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 18:7 cells, image size 1152x112 (each cell 288x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `aurelionsol_fx_r_call.png`：星落：抬爪召星，4 帧

星落起手：他头顶上方**一圈白金色的星光聚起来**，几道细细的青色星座连线连成一个小星座图案，中间一颗星越来越亮。画在格子上半部，下半部空着（他的头在那里）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8, #0A4A78), a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF).
Effect: A STAR CALLED, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), in the upper half of the cell (his head is in the empty lower half): 1 five small white-gold stars at mirrored places; 2 thin cyan constellation lines joining them into a small symmetric constellation 22 wide; 3 a bright white-gold star swelling in its middle; 4 a white flash 10 across, the lines fading. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 26:20 cells, image size 1664x320 (each cell 416x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `aurelionsol_fx_r_fall.png`：星落：从天上坠下的星星，6 帧

星落（参考 r_comet_alpha、r_comet_flare、r_streak、r_smoketrail03）：**一颗白金色的星星从格子顶上笔直往下坠**，后面拖一条长长的蓝紫色星尘尾巴，最后一帧砸到格子底部的地面（落点在格子底边中间）。竖直往下，不歪斜。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF).
Effect: A FALLING STAR, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), coming STRAIGHT DOWN (never slanted): a white-gold star 8 squares across with a white core and a long blue-violet stardust trail above it; frame 1 the star at the top of the cell, frames 2-4 lower and lower with the trail stretching up to 50 squares, frame 5 just above the ground (the bottom middle of the cell), frame 6 a white flash 14 wide on the ground at the bottom middle, the trail fading above it. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 6 equal 26:84 cells, image size 2496x1344 (each cell 416x1344, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `aurelionsol_fx_r_impact.png`：星落：星星砸地，5 帧

星落砸地（参考 r_cometimpact、r_impact_novamask、r_decal、r_groundtar、r_rocks_2x2）：一下白色闪光，**地上炸开一圈白金色的星爆**，蓝紫色的星云往两边翻起来，几块碎石飞起，地上留一个发光的坑。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a lilac-grey dust ramp (#E8E2F4, #B4A8D0, #7C6CA8, #4A3C74).
Effect: A STAR IMPACT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 18 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 a white-gold nova ring 36 wide on the ground with blue-violet nebula puffs rolling out at both sides; 3 the ring 46 wide, lilac-grey rock bits flying up at mirrored places, a glowing crater in the middle; 4 the rocks falling, the crater glowing gold; 5 the ring and the crater fading. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 5 equal 50:26 cells, image size 4000x416 (each cell 800x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `aurelionsol_fx_r_sky.png`：天瀑：巨星砸地，6 帧

天瀑（参考 r_impact_nebulaclouds、r_einstein_purple、r_circle_space_2、r_storm_r_dome、r_ringlight）：比星落大得多——一颗**巨大的星辰从天而降砸在地上**：先是一道白金色的光柱从上往下，地上炸开一大圈星爆，品红和蓝紫的星云团往上和往两边翻滚，中间一个发光的大坑。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a magenta nebula ramp (#FFE6FA, #FF9AE8, #E848C8, #A01E98, #5A0C5C), a lilac-grey dust ramp (#E8E2F4, #B4A8D0, #7C6CA8, #4A3C74).
Effect: THE SKIES DESCEND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a wide white-gold light column coming down into the middle, 24 squares wide; 2 a huge white flash on the ground 40 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 3 a white-gold nova 64 wide with big magenta and blue-violet nebula clouds billowing up and out at mirrored places; 4 the clouds 70 wide, rock bits flying, a glowing crater in the middle; 5 the clouds thinning, star sparkles drifting; 6 the crater and the last sparkles fading. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 6 equal 72:44 cells, image size 6912x704 (each cell 1152x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `aurelionsol_fx_r_wave.png`：天瀑：外圈的冲击波，5 帧

天瀑落地后从边缘往外扩的**冲击波**（参考 r_cast_shockwave、r_shockwave_spacenoise、update_r_interiorring）：地上一圈**细细的蓝紫色光环**带着星尘往外推，一帧比一帧大，中间空着。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8, #0A4A78), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A).
Effect: A SHOCKWAVE RING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin glowing blue-violet ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) with cyan glints and stardust specks along it, the middle EMPTY; 1 the ring 50 squares wide; 2 66 wide; 3 80 wide; 4 92 wide, thinner; 5 96 wide, breaking into fading specks. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 5 equal 96:30 cells, image size 7680x480 (each cell 1536x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `aurelionsol_fx_r_hit.png`：星落 / 天瀑：被砸中，3 帧

被星星砸中的敌人：身上一下白金色闪光，几颗小星星和碎石往两边弹开。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a lilac-grey dust ramp (#E8E2F4, #B4A8D0, #7C6CA8, #4A3C74).
Effect: A STAR STRUCK, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 7 squares across on the target's chest; 2 small star sparkles and rock bits bursting out 15 across at mirrored places; 3 falling, fading. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal 16:18 cells, image size 768x288 (each cell 256x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `aurelionsol_fx_w_lift.png`：星穹流丽：击杀后起飞，4 帧

击杀以后飞起来（参考 air_trail、w_star_sparks、update_w_buff_alphamask）：他身边**一圈青色的光环往上一冲**，星尘和小星星往四周炸开。他在中间不画，**身体的位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8, #0A4A78), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40).
Effect: TAKING FLIGHT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Aurelion Sol floats in the middle, not drawn: 32 squares wide and 44 tall (his crest to his tail tip) - leave his body's place EMPTY: 1 a cyan ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 30 wide; 2 the ring rising up round him to his chest, white-gold star sparkles bursting out at mirrored places; 3 the ring at his head, sparkles and blue-violet stardust high; 4 the sparkles drifting, fading. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 40:48 cells, image size 2560x768 (each cell 640x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `aurelionsol_fx_w_trail.png`：星穹流丽：飞行时身边的星尘，4 帧循环

飞行的那几秒：他身下和身边一直**飘着蓝紫色的星尘和青色的光点**，像一条小星河。画在他身后、淡一点，身体位置留空。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8, #0A4A78), a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A).
Effect: A STARDUST STREAM, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a faint drifting band of blue-violet stardust on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 40 wide with cyan motes and tiny white-gold stars at mirrored places, rising a little and twinkling frame to frame so the loop flows. Sparse and light - it plays behind him. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 44:20 cells, image size 2816x320 (each cell 704x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `aurelionsol_fx_d_gain.png`：星海焕然：星尘飞进他身体，4 帧

收集到星尘：**几颗白金色的小星星从四周飞向他**，到身上化成一圈蓝紫色的光。他在中间不画，**身体的位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a blue-violet nebula ramp (#E6E8FF, #9EA8FF, #5C64F0, #3A2CC0, #24167A, #120A40), a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF).
Effect: STARDUST DRAWN IN, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Aurelion Sol floats in the middle, not drawn: 32 squares wide and 44 tall (his crest to his tail tip) - leave his body's place EMPTY: 1 four small white-gold stars near the cell's corners at mirrored places; 2 the stars halfway in with blue-violet stardust trails; 3 the stars reaching his outline, a white glint; 4 a faint blue-violet ring round his chest fading. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 34:46 cells, image size 2176x736 (each cell 544x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `aurelionsol_fx_sky_ready.png`：天瀑就绪：星尘攒满的一闪，4 帧

星尘攒满、下一次大招变成天瀑：他身边**一圈金色的星环亮起来**，往外一扩，几颗大星星闪一下。身体位置留空。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a magenta nebula ramp (#FFE6FA, #FF9AE8, #E848C8, #A01E98, #5A0C5C), a white flash ramp (#FFFFFF, #F4F8FF, #DCE6FF).
Effect: THE SKIES READY, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Aurelion Sol floats in the middle, not drawn: 32 squares wide and 44 tall (his crest to his tail tip) - leave his body's place EMPTY: 1 a ring of small white-gold stars round his chest 30 wide; 2 the ring flaring bright with magenta glints, 36 wide; 3 four big four-pointed stars flashing at mirrored places round him; 4 fading. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 40:50 cells, image size 2560x800 (each cell 640x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `aurelionsol_fx_sky_glow.png`：天瀑就绪期间：头顶绕着的星星，4 帧循环

天瀑就绪的这段时间：他**头顶上方绕着三颗小小的金色星星**，一闪一闪地慢慢转。只画在格子最上面（他头顶上方），下面全空着。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold starlight ramp (#FFFFFF, #FFF6D8, #FFE08A, #F2B84A, #C07A2A), a magenta nebula ramp (#FFE6FA, #FF9AE8, #E848C8, #A01E98, #5A0C5C).
Effect: STARS OVER HIS HEAD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Aurelion Sol floats in the middle, not drawn: 32 squares wide and 44 tall (his crest to his tail tip) - draw ONLY in the top 10 squares of the cell, above his crest; everything below EMPTY: three small white-gold four-pointed stars in a flat ring 20 wide (one in the middle, two at mirrored sides), twinkling in turn with a faint magenta glint, the middle one higher or lower frame to frame so they seem to circle. everything is COSMIC: white-gold starlight with crisp four-pointed star sparkles, deep blue and violet nebula wisps, glowing cyan lines; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 34:56 cells, image size 2176x896 (each cell 544x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `aurelionsol_fx_a_bolt` | view_projectiles `league_aurelionsol_a_bolt`（追踪弹道，z 2；上下对称） | 12 × 6 |
| `aurelionsol_fx_a_hit` | view_effects `league_aurelionsol_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `aurelionsol_fx_q_beam` | view_projectiles `league_aurelionsol_q_beam`（直线弹道，很快，z 2；上下对称） | 40 × 8 |
| `aurelionsol_fx_q_hit` | view_effects `league_aurelionsol_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `aurelionsol_fx_e_orb` | view_projectiles `league_aurelionsol_e_orb`（抛物线弹道，z 2；圆形，两个方向都对称） | 10 × 10 |
| `aurelionsol_fx_e_hole` | view_effects `league_aurelionsol_e_hole`（大表，落点的地上，不跟随，z -1；左右对称；约 5 秒） | 56 × 26 |
| `aurelionsol_fx_e_core` | view_effects `league_aurelionsol_e_core`（跟随目标，z 2；左右对称） | 16 × 24 |
| `aurelionsol_fx_slow` | view_buffs `league_aurelionsol_e_slow` / `league_aurelionsol_r_slow`（tag `slow`，跟随，脚下，z -1；左右对称） | 18 × 7 |
| `aurelionsol_fx_r_call` | view_effects `league_aurelionsol_r_call`（他头顶，不跟随，z 3；左右对称） | 26 × 20 |
| `aurelionsol_fx_r_fall` | view_effects `league_aurelionsol_r_fall`（大表，落点，不跟随，z 3；左右对称；半秒） | 26 × 84 |
| `aurelionsol_fx_r_impact` | view_effects `league_aurelionsol_r_impact`（大表，落点的地上，不跟随，z -1；左右对称） | 50 × 26 |
| `aurelionsol_fx_r_sky` | view_effects `league_aurelionsol_r_sky`（大表，落点的地上，不跟随，z -1；左右对称） | 72 × 44 |
| `aurelionsol_fx_r_wave` | view_effects `league_aurelionsol_r_wave`（大表，落点的地上，不跟随，z -1；左右对称） | 96 × 30 |
| `aurelionsol_fx_r_hit` | view_effects `league_aurelionsol_r_hit`（跟随目标，z 2；左右对称） | 16 × 18 |
| `aurelionsol_fx_w_lift` | view_effects `league_aurelionsol_w_lift`（在他身边，不跟随，z 3；左右对称） | 40 × 48 |
| `aurelionsol_fx_w_trail` | view_buffs `league_aurelionsol_w_fly`（tag `w_trail`，跟随他，z -1，在他身后；左右对称；约 4 秒） | 44 × 20 |
| `aurelionsol_fx_d_gain` | view_effects `league_aurelionsol_d_gain`（跟随他，z 2；左右对称） | 34 × 46 |
| `aurelionsol_fx_sky_ready` | view_effects `league_aurelionsol_sky_ready`（跟随他，z 3；左右对称） | 40 × 50 |
| `aurelionsol_fx_sky_glow` | view_buffs `league_aurelionsol_sky`（tag `sky_glow`，跟随他，z 3；左右对称；到下次大招为止） | 34 × 56 |

- 两张表：`asset/league/effects/league_aurelionsol_fx`（小的）和 `league_aurelionsol_big`（e_hole、r_fall、r_impact、r_sky、r_wave），tag = 名字（build_aurelionsol.py 的 views；e_slow 和 r_slow 用 `slow`，w_fly 用 `w_trail`，sky 用 `sky_glow`）。
- 弹道（a_bolt、q_beam）断言上下对称，e_orb 两个方向都对称；其余断言左右对称。e_hole 循环 e_t（300 tick），w_trail 循环 w_t，sky_glow 循环到下次大招，slow 循环；r_fall 的最后一帧对上 r_fall 的落地（30 tick）。
- 用 `pixel_1x/` 切格（import_belveth_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
