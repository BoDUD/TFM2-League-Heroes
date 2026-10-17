# 深渊巨口 克格莫：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图。** 造型和动作已定（`design/kogmaw_design.png`，43×38 格，8 倍）。
> - 大小对照 `design/kogmaw_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/kogmaw_shots.png`：普攻吐酸液、Q 吐唾液、E 吐淤泥、R 朝天开炮、死亡那几帧的动作（4 倍），青色十字是脚下。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里克格莫自己的特效贴图（不少是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。颜色：**普攻、W 和 R 是绿色酸液；Q 是黄绿色的腐蚀唾液；E 的淤泥和被动的虚空之力是紫粉色**。
> - **特效要亮**：以前魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。飞行的酸液弹、唾液、淤泥、虚空分身和地上那条淤泥带会转到飞行 / 施放方向，所以**朝右画、上下对称**。R 的炮弹落下和被动的虚空爆发是**竖着的画面**，上下不能颠倒。
> - 特效照下面第 1–18 条和「所有特效图的规则」画，每张一个 PNG，文件名 `kogmaw_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`kogmaw_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 嘴管里吐出一团绿色酸液 | `kogmaw_fx_a_glob` · `kogmaw_fx_a_hit` |
| W「生化弹幕」（自动） | 打架时自动开 8 秒：射程变远，普攻附带对方最大生命值的伤害 | `kogmaw_fx_w_cast` · `kogmaw_fx_w_on` |
| 技能 1 = Q「腐蚀唾液」 | 一大口直线飞出的黄绿色唾液，打中的敌人护甲魔抗被腐蚀 | `kogmaw_fx_q_spit` · `kogmaw_fx_q_hit` · `kogmaw_fx_q_shred` |
| 技能 2 = E「虚空淤泥」 | 一团穿透的紫色淤泥，地上留下一长条减速的淤泥带 | `kogmaw_fx_e_ooze` · `kogmaw_fx_e_trail` · `kogmaw_fx_e_hit` · `kogmaw_fx_e_slow` |
| 大招 = R「活体大炮」 | 嘴管朝天开炮，远处地上出警告圈，炮弹从天上落下炸开（一轮最多三发） | `kogmaw_fx_r_mark` · `kogmaw_fx_r_fall` · `kogmaw_fx_r_hit` |
| 被动「艾卡西亚的惊喜」 | 死后体内的虚空之力爆发，化成虚空分身追向最近的敌方英雄，追上就炸 | `kogmaw_fx_p_wake` · `kogmaw_fx_p_form` · `kogmaw_fx_p_boom` · `kogmaw_fx_p_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、酸液、淤泥、火花、雾没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 绿色酸液（普攻、W、R）：`#FFFFFF`、`#F2FFD0`、`#D4F87A`、`#A8E838`、`#74C41E`、`#46961A`、`#26640E`；
  - 黄绿色腐蚀唾液（Q）：`#FFFFFF`、`#FFFCD8`、`#FFF07A`、`#E2E83A`、`#B4D21E`、`#7CA816`、`#4A760E`；
  - 紫粉色虚空（E、被动）：`#FFFFFF`、`#FFE4FF`、`#F6A8FA`、`#DA66EC`、`#AE38D0`、`#7420A0`、`#42106A`；
  - 黄绿色警告圈（R 落点）：`#FFFFFF`、`#F6FFD8`、`#DCF88A`、`#B6E44A`、`#84C02A`；
- **飞行的画面朝右画，而且上下对称**（`a_glob`、`q_spit`、`e_ooze`、`p_form`，还有地上的 `e_trail`）：游戏会把它转到飞行 / 施放方向，往左时整张会上下翻过来。
- **挂在人身上和地上的画面左右对称**，按每条写的站位画；命中、爆炸居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。`r_fall`、`p_wake` 是竖着的画面（往下落、往上冲），不能颠倒。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人；光环只画外面一圈，不要盖住人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻射程约 50000，R 爆炸半径约 15000，E 淤泥带长 110000）。

### 1. `kogmaw_fx_a_glob.png`：普攻：飞出去的酸液弹（朝右，循环），4 帧

克格莫吐出的一团绿色酸液：圆圆的亮绿色酸液球，中间白绿色的芯，后面拖一小截滴落的酸液尾巴（参考 W_mis_ball、W_mis_trail）。**朝右画**，上下对称（往左飞时游戏会把整张转过来）。约 8 格宽、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a green acid ramp (#FFFFFF, #F2FFD0, #D4F87A, #A8E838, #74C41E, #46961A, #26640E).
Effect: a small FLYING ACID GLOB pointing RIGHT, 4 frames, a seamless loop: a round bright green blob 4 squares across with a white-green core at its front (right), a short tapering tail of green acid drops 4 squares long streaming left behind it; the blob wobbles and the drops shift from frame to frame. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 128x80 (image 512x80) (16 px a square here); the blob's middle on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kogmaw_fx_a_hit.png`：普攻命中：酸液溅开（目标身上），4 帧

酸液弹打中：一团绿色酸液啪地溅开，几滴酸液往四周飞，中间一下白绿色的光（参考 W_DirectionalSplash、Splash_2x2_yellow）。左右对称，居中画。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a green acid ramp (#FFFFFF, #F2FFD0, #D4F87A, #A8E838, #74C41E, #46961A, #26640E).
Effect: an ACID SPLASH HIT, 4 frames: 1 a white-green flash 4 squares across; 2 a splat of bright green acid bursting out, 10 squares across, drops flying to all sides; 3 the drops farther out, the splat thinning, a few drips falling; 4 a few fading drops. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kogmaw_fx_w_cast.png`：W 生化弹幕开启：身上一圈绿光爆开，5 帧

W 开启的一瞬间：他全身外面一圈绿色的生化能量往外一炸，绿色的小电弧噼啪闪几下，几颗酸液光点往上飘（参考 W_Electric_Arcs、W_Glow）。只画外面一圈，**中间空着**，不要盖住人。左右对称。约 44 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a green acid ramp (#FFFFFF, #F2FFD0, #D4F87A, #A8E838, #74C41E, #46961A, #26640E).
Effect: a BURST OF GREEN BIO-ENERGY round a figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a thin bright green-white ring flaring round the rim of a wide oval 40 x 26 squares; 2 short jagged green electric arcs crackling on the rim, acid motes popping out; 3 the arcs at their brightest, motes rising; 4 the ring fading, motes higher; 5 a few motes. Left-right symmetric overall.
Layout: one horizontal row of 5 equal cells, each 768x512 (image 3840x512) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kogmaw_fx_w_on.png`：W 开着的时候：脚下一圈绿色电弧（循环），4 帧

W 开着的 8 秒：他脚下的地上一圈绿色的生化电弧在转、噼啪闪，几颗绿色光点往上冒（像一圈脚下的光环）。只画脚下的一圈，不要盖住人。左右对称，从斜上方看的椭圆。约 40 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a green acid ramp (#FFFFFF, #F2FFD0, #D4F87A, #A8E838, #74C41E, #46961A, #26640E).
Effect: a LOOPING RING OF GREEN ELECTRIC ARCS on the ground at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 38 x 8 squares made of short jagged bright green arcs and sparks, moving a quarter of the way round each frame, brighter in front, small green motes rising from it. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 640x192 (image 2560x192) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kogmaw_fx_q_spit.png`：Q 腐蚀唾液：飞出去的大口唾液（朝右，循环），4 帧

Q 吐出的一大口黄绿色腐蚀唾液：比普攻大的黄绿色酸液团，前头亮、后面拖一条冒烟、滴落的酸液尾巴（参考 Q_Trail、Q_DirectionalSplash_yellow、Z_webacid）。**朝右画**，上下对称。约 14 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a yellow-green acid ramp (#FFFFFF, #FFFCD8, #FFF07A, #E2E83A, #B4D21E, #7CA816, #4A760E).
Effect: a FLYING CAUSTIC SPIT pointing RIGHT, 4 frames, a seamless loop: a big yellow-green acid blob 6 squares across with a white-yellow core at its front, a trail 8 squares long of yellow-green acid drops and thin acid smoke streaming left behind it, the drops shifting from frame to frame. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 224x128 (image 896x128) (16 px a square here); the blob's middle on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kogmaw_fx_q_hit.png`：Q 命中：黄绿色酸液大溅开（目标身上），5 帧

Q 打中：一大团黄绿色的酸液猛地溅开，四周飞出酸液滴，中间一下白黄色的光，冒一点酸雾。左右对称，居中画。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a yellow-green acid ramp (#FFFFFF, #FFFCD8, #FFF07A, #E2E83A, #B4D21E, #7CA816, #4A760E).
Effect: a BIG CAUSTIC SPLASH, 5 frames: 1 a white-yellow flash 6 squares across; 2 a big splat of yellow-green acid bursting out, 14 squares across, drops flying to all sides; 3 the splat at full size (18 squares), drops farther out, thin acid smoke; 4 the acid dripping down, the smoke rising; 5 a few fading drops. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 288x288 (image 1440x288) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kogmaw_fx_q_shred.png`：Q 腐蚀（目标被减甲：身上滋滋冒泡，循环），4 帧

Q 打中后目标护甲魔抗被腐蚀 4 秒：目标身上几块黄绿色的酸液在滋滋冒泡，几滴酸液往下滴，一点点酸烟往上飘。只画身上零散的几块酸液和气泡，**中间大部分空着**，不要盖住人。左右对称。约 20 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a yellow-green acid ramp (#FFFFFF, #FFFCD8, #FFF07A, #E2E83A, #B4D21E, #7CA816, #4A760E).
Effect: LOOPING SIZZLING ACID on a figure (do NOT draw the figure; keep most of the inside empty), 4 frames, a seamless loop: 4-5 small patches of yellow-green acid scattered over an upright oval 18 x 22 squares, each bubbling (a bubble swelling and popping), single drops dripping down, thin acid smoke curling up; the bubbles change from frame to frame. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 320x384 (image 1280x384) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kogmaw_fx_e_ooze.png`：E 虚空淤泥：飞出去的淤泥（朝右，循环），4 帧

E 吐出的一团紫粉色虚空淤泥：一团黏糊糊、亮紫粉色的淤泥球往前滚，前头白粉色的光，后面拖一截淤泥（参考 Splash_2x2_pink、W_DirectionalSplash 的紫色）。**朝右画**，上下对称。约 12 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet void ramp (#FFFFFF, #FFE4FF, #F6A8FA, #DA66EC, #AE38D0, #7420A0, #42106A).
Effect: a FLYING BLOB OF VOID OOZE pointing RIGHT, 4 frames, a seamless loop: a gooey bright violet-pink blob 6 squares across with a white-pink glow at its front, a stretched tail of ooze 6 squares long behind it with a few drops; the blob wobbles and stretches from frame to frame. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 192x128 (image 768x128) (16 px a square here); the blob's middle on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kogmaw_fx_e_trail.png`：E 淤泥带：地上留下的一长条虚空淤泥（循环），4 帧

E 飞过的地上留下一长条紫粉色的虚空淤泥（踩上去会减速），4 秒。一条横着的、很长的淤泥带：边缘不规则、一块块黏糊糊的紫色淤泥连成一条，上面冒着泡、泛着亮光（参考 E_WaterAdd、E_RingMult 的水面纹理）。**横着画满整个格子**（左右两头收窄一点），上下对称（游戏会把它转到施放方向）。约 100 格长、14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet void ramp (#FFFFFF, #FFE4FF, #F6A8FA, #DA66EC, #AE38D0, #7420A0, #42106A).
Effect: a LONG LOOPING STRIP OF VOID OOZE lying on the ground, horizontal, 4 frames, a seamless loop: a band of gooey violet-pink ooze 96 squares long and 12 squares wide filling the cell from left to right (both ends tapering), made of joined puddles with irregular wavy edges, bright pink highlights and small bubbles that swell and pop from frame to frame, a faint glow along its middle. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 1600x224 (image 6400x224) (16 px a square here); the band's middle line on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kogmaw_fx_e_hit.png`：E 命中：淤泥糊上去（目标身上），4 帧

淤泥打中：一团紫粉色淤泥啪地糊开，几滴淤泥飞溅，中间一下白粉色的光。左右对称，居中画。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet void ramp (#FFFFFF, #FFE4FF, #F6A8FA, #DA66EC, #AE38D0, #7420A0, #42106A).
Effect: a VOID OOZE SPLAT, 4 frames: 1 a white-pink flash 4 squares across; 2 a splat of violet-pink ooze bursting out, 10 squares across, gooey drops flying; 3 the splat sagging, drips falling; 4 a few fading drops. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kogmaw_fx_e_slow.png`：E 减速：脚下黏着淤泥（循环），4 帧

被淤泥减速：脚下一小滩紫粉色的淤泥黏着脚，冒着泡。只画脚下的一滩，不要盖住人。左右对称，从斜上方看的椭圆。约 18 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet void ramp (#FFFFFF, #FFE4FF, #F6A8FA, #DA66EC, #AE38D0, #7420A0, #42106A).
Effect: a LOOPING PUDDLE OF VOID OOZE at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat gooey violet-pink puddle, an ellipse 16 x 5 squares with a wavy edge, small bubbles swelling and popping, a bright pink highlight along its front. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 288x96 (image 1152x96) (16 px a square here); the puddle's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kogmaw_fx_r_mark.png`：R 活体大炮：落点警告圈（地上），6 帧

大炮落下之前地上的警告圈（英雄联盟里是一个圈慢慢收紧）：地上一个黄绿色的圆环，里面淡淡的一层，一道内圈从边缘往中心收（倒计时），最后一帧整个圈亮一下。左右对称，从斜上方看的椭圆（宽是高的 2 倍）。约 30 格宽、15 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a warning ramp (#FFFFFF, #F6FFD8, #DCF88A, #B6E44A, #84C02A).
Effect: a TARGET WARNING RING on the ground, 6 frames: an ellipse ring 30 x 15 squares, 1 square thick, bright yellow-green, with a faint pale fill inside; a second thinner ring starts at the edge in frame 1 and closes in toward the middle frame by frame (frame 5: 6 x 3 squares); frame 6 the whole ring flashing bright white-green. Left-right symmetric; seen from above at an angle.
Layout: one horizontal row of 6 equal cells, each 512x256 (image 3072x256) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `kogmaw_fx_r_fall.png`：R 活体大炮：炮弹从天上落下来炸开（落点），7 帧

从天上掉下来的那一发酸液炮弹：一个发光的绿色酸液球拖着尾巴从上往下直直落下来，砸到地上炸开一大团绿色的酸液，四周飞溅，地上留一滩冒泡的酸液然后消失（参考 R_spit、R_hit_aoering、R_Floor_Puddle、R_Bubble）。**竖着的画面**，上下不能颠倒：第 1–2 帧炮弹在空中往下落，第 3 帧砸到地上。落点在格子下部。约 32 格宽、60 格高（炸开的范围约 30 格宽）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a green acid ramp (#FFFFFF, #F2FFD0, #D4F87A, #A8E838, #74C41E, #46961A, #26640E).
Effect: a FALLING ACID SHELL that bursts on the ground, UPRIGHT (never upside down), 7 frames: 1 a glowing green acid ball 6 squares across high in the cell (its middle 14 squares from the top) with a trail of drops streaming UP behind it; 2 the ball lower (its middle 34 squares from the top), the trail longer; 3 the IMPACT: a white-green flash on the ground point, a burst of acid 20 squares wide; 4 a big splash of green acid 30 squares wide thrown up and out, drops flying; 5 the splash falling back, a bubbling acid puddle spreading on the ground (an ellipse 26 x 10 squares); 6 the puddle bubbling, thin smoke; 7 the puddle fading. Left-right symmetric.
Layout: one horizontal row of 7 equal cells, each 512x960 (image 3584x960) (16 px a square here); the ground point (where the shell lands) 8 squares (128 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `kogmaw_fx_r_hit.png`：R 命中：酸液烧上去（目标身上），4 帧

被炮弹炸到：身上一团绿色酸液溅开、冒泡，一下白绿色的光。左右对称，居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a green acid ramp (#FFFFFF, #F2FFD0, #D4F87A, #A8E838, #74C41E, #46961A, #26640E).
Effect: an ACID BURN HIT, 4 frames: 1 a white-green flash 5 squares across; 2 a splash of green acid 12 squares across with bubbles; 3 the acid dripping, bubbles popping; 4 a few fading drips. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 224x224 (image 896x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `kogmaw_fx_p_wake.png`：被动「艾卡西亚的惊喜」：死后虚空之力从身上爆发（尸体上），6 帧

克格莫死的时候体内的虚空之力冲出来：尸体上一下紫粉色的虚空光爆开，一道紫色光柱往上冲，一圈紫色冲击波，碎光往外飞（参考 P_Shockwave、P_Material_Noise、P_aoe_explosion）。左右对称，竖着的画面。约 30 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet void ramp (#FFFFFF, #FFE4FF, #F6A8FA, #DA66EC, #AE38D0, #7420A0, #42106A).
Effect: a VOID ERUPTION from a fallen body, UPRIGHT, 6 frames: 1 a white-violet flash at the ground point; 2 a column of violet-pink void light 8 squares wide shooting UP 28 squares, a ring of violet light spreading on the ground (an ellipse 20 x 8 squares); 3 the column at full height, sparks and void wisps flying out; 4 the column thinning, the ring at full size (28 x 10); 5 the column breaking into rising wisps; 6 a few fading wisps. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 480x544 (image 2880x544) (16 px a square here); the ground point 4 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `kogmaw_fx_p_form.png`：被动：追向敌人的虚空分身（朝右，循环），4 帧

离体的虚空分身追着最近的敌人冲过去：一团发光的紫粉色虚空能量，前头一个亮白粉色的核，外面一层翻滚的紫色虚空雾，后面拖着一条紫色的光尾巴和几缕雾。**朝右画**，上下对称（往左追时游戏会把整张转过来）。约 18 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet void ramp (#FFFFFF, #FFE4FF, #F6A8FA, #DA66EC, #AE38D0, #7420A0, #42106A).
Effect: a FLYING BALL OF VOID ENERGY pointing RIGHT (a spirit chasing its prey), 4 frames, a seamless loop: a glowing core 6 squares across, white-pink in the middle, wrapped in churning violet void mist 10 squares across, a tail of violet light and wisps 8 squares long streaming left behind it; the mist swirls from frame to frame. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 288x192 (image 1152x192) (16 px a square here); the core's middle on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `kogmaw_fx_p_boom.png`：被动：虚空分身追上后爆炸（目标身上），6 帧

虚空分身追上敌人炸开：一团紫粉色的虚空光猛地爆开成一个大圆，冲击波往外推，碎光和虚空雾往四周飞（参考 P_aoe_explosion、P_Shockwave）。左右对称，居中画。约 26 格（爆炸半径）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet void ramp (#FFFFFF, #FFE4FF, #F6A8FA, #DA66EC, #AE38D0, #7420A0, #42106A).
Effect: a VOID EXPLOSION, 6 frames: 1 a white flash 6 squares across; 2 a ball of violet-pink void light bursting to 16 squares; 3 a bright shockwave ring 24 squares across, the ball breaking up, sparks flying; 4 the ring at 26 squares thinning, void wisps flying out; 5 the wisps fading; 6 a few sparks. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 416x416 (image 2496x416) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `kogmaw_fx_p_hit.png`：被动：被虚空爆炸炸到（目标身上），4 帧

被虚空爆炸波及：身上一下紫粉色的虚空火花，几道紫光碎片飞开。左右对称，居中画。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, acid, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet void ramp (#FFFFFF, #FFE4FF, #F6A8FA, #DA66EC, #AE38D0, #7420A0, #42106A).
Effect: a VOID SPARK HIT, 4 frames: 1 a white-pink flash 4 squares across; 2 violet-pink void sparks bursting out, 10 squares across; 3 the sparks farther out, thinning; 4 a few fading sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kogmaw_fx_a_glob` | view_projectiles `league_kogmaw_a_glob`（循环，朝飞行方向转） | 8 × 5 |
| `kogmaw_fx_a_hit` | view_effects `league_kogmaw_a_hit`（跟随，画在人物上面） | 12 |
| `kogmaw_fx_w_cast` | view_effects `league_kogmaw_w_cast`（跟随，画在人物上面） | 44 × 30 |
| `kogmaw_fx_w_on` | view_buffs `league_kogmaw_w_on`（循环，跟随，画在人物下面；8 秒） | 40 × 10 |
| `kogmaw_fx_q_spit` | view_projectiles `league_kogmaw_q_spit`（循环，朝飞行方向转） | 14 × 8 |
| `kogmaw_fx_q_hit` | view_effects `league_kogmaw_q_hit`（跟随，画在人物上面） | 18 |
| `kogmaw_fx_q_shred` | view_buffs `league_kogmaw_q_shred`（循环，跟随，画在人物上面；4 秒） | 20 × 24 |
| `kogmaw_fx_e_ooze` | view_projectiles `league_kogmaw_e_ooze`（循环，朝飞行方向转） | 12 × 8 |
| `kogmaw_fx_e_trail` | view_projectiles `league_kogmaw_e_trail`（循环，朝施放方向转，画在人物下面；4 秒） | 100 × 14 |
| `kogmaw_fx_e_hit` | view_effects `league_kogmaw_e_hit`（跟随，画在人物上面） | 12 |
| `kogmaw_fx_e_slow` | view_buffs `league_kogmaw_e_slow`（循环，跟随，画在人物下面） | 18 × 6 |
| `kogmaw_fx_r_mark` | view_effects `league_kogmaw_r_mark`（不跟随，画在人物下面；落下前 0.6 秒） | 30 × 15 |
| `kogmaw_fx_r_fall` | view_effects `league_kogmaw_r_fall`（不跟随，画在人物上面；落点上） | 32 × 60 |
| `kogmaw_fx_r_hit` | view_effects `league_kogmaw_r_hit`（跟随，画在人物上面） | 14 |
| `kogmaw_fx_p_wake` | view_effects `league_kogmaw_p_wake`（不跟随，画在人物上面；死亡时） | 30 × 34 |
| `kogmaw_fx_p_form` | view_projectiles `league_kogmaw_p_form`（循环，朝飞行方向转） | 18 × 12 |
| `kogmaw_fx_p_boom` | view_effects `league_kogmaw_p_boom`（跟随，画在人物上面） | 26 |
| `kogmaw_fx_p_hit` | view_effects `league_kogmaw_p_hit`（跟随，画在人物上面） | 12 |

- `w_cast` 是挂在他身上的光（左右对称），在出招第一帧播放；`w_on` 是 8 秒的脚下光环。
- `r_mark`、`r_fall`、`p_wake` 是地上 / 落点的画面：放在 ViewEffect 里（不随方向转），不要挂在 RangeProjectile 的 view 上（红色方会倒过来，蕾欧娜的教训）。
- `e_trail` 是 LineRangeProjectile 的画面（110000 × 18000，朝施放方向转），上下对称；量魔腾 `q_path` 的摆法。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
