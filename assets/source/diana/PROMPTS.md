# 戴安娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型和动作已经做完并导入游戏，这一轮只画特效，不画人。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里戴安娜原皮自己的特效贴图（普攻的月牙印、第三下的双月牙、新月打击的冲击和闪光、月光标记、法球的旋涡和光、护盾、E 落地的双月牙、R 的满月、地面月牙光圈和光柱），只在本地用，不要提交。英雄联盟的贴图大多是灰白的遮罩，游戏里才上色：**形状照它，颜色照下面的规则**。
> - 颜色和画风对照 `design/diana_design.png`（定稿造型，8 倍）；大小对照 `design/diana_ingame.png`（游戏里的全部帧，3 倍，绿线是脚底线，蓝线是站位点）：戴安娜从头顶到脚底 40 格，刀尖再高 3 格，其他英雄约 35–40 格。
> - 每张一个 PNG，文件名和排版按每条写的来。生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（`manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。每张保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - **不要给特效描边**（上一个英雄每个形状外面都描了一圈最深的颜色，导入时还要清掉）。**不要在格子中间挖洞给人让位**：套在她身上的特效画成完整的一片，导入时放在她身体后面（她的身体会挡住中间）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）和 `manifest.json`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「月银之刃」 | 弯刀砍中；每第 3 下顺劈目标周围的敌人（魔法伤害）；放技能后攻速变快（不用画） | `diana_fx_hit` · `diana_fx_p_cleave` · `diana_fx_p_hit` |
| 技能 1 = Q「新月打击」 | 射出一道新月光刃，穿过路上所有敌人，打中的敌人头上挂 3 秒「月光」 | `diana_fx_q_bolt` · `diana_fx_q_hit` · `diana_fx_moon_mark` |
| 技能 2 = E「月神冲刺」+ W「苍白之瀑」 | 冲到目标身边砍一下（有月光时再冲一次）；冲到时召出三颗法球绕着她转，逐个撞向身边的敌人爆开，同时有一层护盾 | `diana_fx_e_hit` · `diana_fx_w_cast` · `diana_fx_w_orb3` · `diana_fx_w_orb2` · `diana_fx_w_orb1` · `diana_fx_w_orb` · `diana_fx_w_boom` · `diana_fx_w_shield` |
| 大招 = R「月之降临」 | 把身边的敌方英雄拉到身前；1 秒后一轮满月砸在她身上，炸开月光伤害周围的敌人 | `diana_fx_r_draw` · `diana_fx_r_moon` · `diana_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边，也不要用最深的颜色给形状描一圈**（特效和角色相反）。
- 颜色（从她的造型取：月银色的刀和盔甲、淡紫的月光、紫色的披风；按每条写的用）：
  - 月光（主体）：`#FFFFFF`、`#EAF8FF`、`#BFE4F2`、`#8FC7D8`、`#5E97AE`；
  - 淡紫（月光的暗部、光晕、月光标记）：`#E6D8FF`、`#B9A2F0`、`#8B6FD6`、`#5F46A8`；
  - 深紫（少量点缀、法球的核外圈、R 的月影）：`#3E2C74`、`#26184A`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、爆开、标记居中画，不旋转；地面上的形状按游戏的斜俯视角度画成扁的（宽约是高的 2 倍）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `diana_fx_hit.png`：普攻命中，5 帧

弯刀砍中：一道小小的月银色月牙形刀光（参考 BA1_Decal_Crescent），中心一下白光，几粒淡紫碎光。约 12 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a moonlight ramp (#FFFFFF, #EAF8FF, #BFE4F2, #8FC7D8) with lavender specks (#B9A2F0, #8B6FD6).
Effect: a BLADE HIT, 5 frames: 1 a tiny white flash at the center; 2 a sharp thin crescent-shaped slash of pale moonlight curving across the center, about 50% of the cell wide, a white core; 3 the crescent at full size with a few lavender specks bursting out; 4 the crescent thins and fades; 5 two or three faint specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the hit centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `diana_fx_p_cleave.png`：第三下顺劈的新月刀光（在她身前），6 帧

第三下普攻的大横扫：从她身后划到身前右边的一道宽大的双层月牙刀光（参考 BA3_Decal_new 的双月牙、BA_Swipe），平放在地面高度到腰部之间，右边是刀尖，亮白的刃口，淡紫的尾光。画在她的站位点上，从中间往右展开。约 48 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a moonlight ramp (#FFFFFF, #EAF8FF, #BFE4F2, #8FC7D8, #5E97AE) with a lavender afterglow (#E6D8FF, #B9A2F0, #8B6FD6).
Effect: a WIDE CRESCENT BLADE SWEEP seen from a slightly high 3/4 view, 6 frames, sweeping from the left of the cell's center to the right: 1 a thin pale arc starts behind the middle; 2 a double crescent (two parallel curved blades of light, the outer one bigger) sweeps out to the right half of the cell, its bright white cutting edge in front; 3 at full size - a flat wide crescent lying on its side from the middle to the right edge, about 90% of the cell's height at its widest, a lavender afterglow trailing behind the edge; 4 the light breaks into streaks along the arc; 5 the streaks thin; 6 a few lavender sparkles.
Layout: one horizontal row of 6 equal cells, each 5 wide to 2 tall, image size 3840x768 (each cell 640x384); the arc's inner end at the cell's center, the sweep to the right; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `diana_fx_p_hit.png`：顺劈命中（每个被劈到的敌人），5 帧

被顺劈打到：一道斜的淡紫月牙闪光，中间一点白。比普攻命中稍大。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a lavender ramp (#E6D8FF, #B9A2F0, #8B6FD6, #5F46A8) with white and moonlight highlights (#FFFFFF, #BFE4F2).
Effect: a CLEAVE HIT, 5 frames: 1 a white flash at the center; 2 a diagonal crescent slash of lavender light across the center with a white core, about 60% of the cell wide; 3 the slash at full size with small lavender shards flying out; 4 the slash fades from its ends; 5 faint shards.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the hit centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `diana_fx_q_bolt.png`：新月打击的光刃（飞行），4 帧循环

一道新月形的月能光刃：弧的外侧朝前（右），两个尖角朝后，亮白的边、月光蓝的身体、淡紫的尾光（参考 Q_Trail）。约 14 格长、22 格高（它扫过的宽度）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a moonlight ramp (#FFFFFF, #EAF8FF, #BFE4F2, #8FC7D8, #5E97AE) with a lavender trail (#E6D8FF, #B9A2F0, #8B6FD6).
Effect: a CRESCENT OF MOONLIGHT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a thick crescent moon standing upright, its round outer side facing right (forward) at 75% of the cell width, its two sharp horns pointing back to the left, a bright white edge along the outer curve and pale moonlight blue inside; behind it a short lavender afterglow with a few sparkles streaming to the left edge; the edge's shine and the sparkles move each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 4 tall, image size 1152x384 (each cell 288x384); the crescent on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `diana_fx_q_hit.png`：新月打击命中，6 帧

光刃打中：一颗亮白的星形闪光（参考 Q_Tar_Flash），外面一圈细细的月光冲击环（参考 Q_Shockwave），淡紫碎光往外飞。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a moonlight ramp (#FFFFFF, #EAF8FF, #BFE4F2, #8FC7D8) with lavender (#B9A2F0, #8B6FD6).
Effect: a MOONLIGHT IMPACT, 6 frames: 1 a small white star flash at the center; 2 a bright four-to-six-pointed white star with a pale blue glow, about 50% of the cell wide; 3 a thin moonlight ring expands round it, lavender shards fly out; 4 the ring widens to 85% and thins, the star shrinks; 5 the ring breaks into dashes; 6 faint specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `diana_fx_moon_mark.png`：月光标记（头顶），6 帧循环

被新月打击打中的敌人头上挂 3 秒：一弯小小的发光月牙，淡紫白色，下面几缕向下飘的细光线（参考 Z_Moonlight）。约 10 格宽、12 格高。循环播放。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a lavender-white ramp (#FFFFFF, #E6D8FF, #B9A2F0, #8B6FD6) with moonlight blue (#BFE4F2).
Effect: a MOONLIGHT MARK floating over a head, 6 frames, a seamless loop: a small glowing crescent moon (horns up and to the right) in the upper half of the cell, with two or three thin vertical streaks of light drifting down under it; the crescent pulses brighter and dimmer by one shade, the streaks drift down one square each frame and fade.
Layout: one horizontal row of 6 equal cells, each 5 wide to 6 tall, image size 1200x288 (each cell 200x288... use 1200x240 if needed); the crescent centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `diana_fx_e_hit.png`：月神冲刺落地冲击（地面），6 帧

冲到目标身边的一击：地上一个扁扁的双月牙印（参考 E_Decal）亮起又散去，中间一颗白色星光（参考 E_Spark）。约 24 格宽、12 格高（地面，扁的）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a moonlight ramp (#FFFFFF, #EAF8FF, #BFE4F2, #8FC7D8) with lavender (#B9A2F0, #8B6FD6, #5F46A8).
Effect: a DASH IMPACT on the ground seen from a slightly high 3/4 view (flattened, twice as wide as tall), 6 frames: 1 a white star flash at the center; 2 a double crescent mark of moonlight (two nested crescents, horns up) flashes on the ground round the center; 3 at full size, 90% of the cell wide, small lavender sparks jump up; 4-5 the crescents fade from the outside in; 6 a faint glow.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); the mark centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `diana_fx_w_cast.png`：苍白之瀑出现，6 帧

三颗法球从她身上散开：一圈淡紫白的旋涡光（参考 W_Orbswirl）在她腰间转一圈，三颗亮白小球从旋涡里弹出去。画在她的站位点附近，完整一片（导入时放在她身后）。约 40 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a lavender-white ramp (#FFFFFF, #E6D8FF, #B9A2F0, #8B6FD6) with moonlight blue (#BFE4F2, #8FC7D8).
Effect: THREE MOON ORBS APPEARING seen from a slightly high 3/4 view, 6 frames: 1 a thin swirl of lavender light at the center; 2 the swirl spins into a flat ring (twice as wide as tall) round the center; 3 three bright white orbs with lavender halos pop out of the ring at even spacing; 4 the orbs move out to the ring's edge, 80% of the cell wide; 5 the ring fades, the orbs stay; 6 only the three orbs on the ring.
Layout: one horizontal row of 6 equal cells, each 5 wide to 3 tall, image size 1920x384 (each cell 320x192... use each cell 640x384, image 3840x384); the ring centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9–11. `diana_fx_w_orb3.png`、`diana_fx_w_orb2.png`、`diana_fx_w_orb1.png`：环绕的法球（3 / 2 / 1 颗），各 8 帧循环

法球绕着她转：腰的高度一个扁扁的椭圆轨道（宽约是高的 3 倍，约 40 格宽、12 格高），3 颗（2 颗、1 颗）亮白的小法球等距绕着转，一圈 8 帧，转到后面（上半圈）的法球画小一格、暗一级，前面（下半圈）的亮；不画轨道线。三张的法球位置要一致（2 颗那张就是 3 颗那张去掉一颗）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a lavender-white ramp (#FFFFFF, #E6D8FF, #B9A2F0, #8B6FD6, #5F46A8).
Effect: [N] MOON ORBS ORBITING seen from a slightly high 3/4 view, 8 frames, a seamless loop of one full turn: [N] small glowing orbs (a white core, a lavender halo, about 4 squares across) spaced evenly on a flat invisible ellipse three times as wide as tall that fills the cell; each frame they move one eighth of a turn counter-clockwise; an orb on the far (upper) half is one square smaller and one shade dimmer, an orb on the near (lower) half is full size and bright. Do not draw the ellipse itself.
Layout: one horizontal row of 8 equal cells, each 3 wide to 1 tall, image size 3072x128 (each cell 384x128); the ellipse centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```
（`[N]` 分别是 THREE / TWO / ONE；2 颗和 1 颗的那两张，法球位置照 3 颗那张去掉一颗和两颗。）

### 12. `diana_fx_w_orb.png`：飞出去的法球（飞行），4 帧循环

一颗法球飞向敌人：亮白的核、淡紫的光晕、短短的尾光（参考 Z_OrbGlow）。约 8 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a lavender-white ramp (#FFFFFF, #E6D8FF, #B9A2F0, #8B6FD6).
Effect: a MOON ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round orb with a white core and a lavender halo at 70% of the cell width, a short lavender tail to the left; the core flickers and the tail's specks move each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 768x128 (each cell 192x128); the orb on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `diana_fx_w_boom.png`：法球爆开，6 帧

法球撞到敌人爆开：一颗带尖刺的星形闪光（参考 W_impact），淡紫白色，碎光往外飞。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a lavender-white ramp (#FFFFFF, #E6D8FF, #B9A2F0, #8B6FD6) with moonlight blue (#BFE4F2).
Effect: an ORB BURST, 6 frames: 1 a white dot at the center; 2 a spiky star burst of white and lavender light with five uneven spikes, about 60% of the cell wide; 3 at full size, small shards flying out; 4 the spikes shrink and the shards spread; 5 the shards fade; 6 faint specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the burst centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `diana_fx_w_shield.png`：护盾（在她身后），6 帧循环

护盾挂着时：她身后一个淡紫白的圆形光罩（参考 W_SShield：边亮、中间淡），光罩边上一道亮光慢慢绕着转。画成完整的一个圆（导入时放在她身体后面，身体会挡住中间），约 36 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a lavender-white ramp (#FFFFFF, #E6D8FF, #B9A2F0, #8B6FD6) with moonlight blue (#BFE4F2, #8FC7D8).
Effect: a SHIELD BUBBLE, 6 frames, a seamless loop: a round bubble of pale lavender light filling 90% of the cell, its rim two squares thick and brighter, its inside a sparse checker of faint lavender squares (mostly empty); a white sheen travels round the rim one sixth of a turn each frame.
Layout: one horizontal row of 6 equal cells, each 9 wide to 10 tall, image size 1728x320 (each cell 288x320); the bubble centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `diana_fx_r_draw.png`：月之降临拉人（地面，在她脚下），8 帧

大招放出的一瞬：她脚下一个扁扁的大光圈（参考 R_GroundDecal：一圈月牙和向里收的光线），光圈的光线从外向里收拢，像把周围的人吸过来。约 70 格宽、35 格高（地面，扁的）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a moonlight ramp (#FFFFFF, #EAF8FF, #BFE4F2, #8FC7D8, #5E97AE) with lavender (#B9A2F0, #8B6FD6, #5F46A8).
Effect: a PULLING MOON CIRCLE on the ground seen from a slightly high 3/4 view (flattened, twice as wide as tall), 8 frames: 1 a wide thin ring of moonlight at the cell's edge; 2-4 short streaks of light run from the ring inward toward the center, like being sucked in, a crescent symbol glows at the center; 5 the streaks reach the center, the ring shrinks to 60%; 6 a bright crescent flash at the center; 7-8 everything fades from the outside in.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 4096x256 (each cell 512x256); the circle centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `diana_fx_r_moon.png`：月亮砸下来（在她身上），12 帧

拉人 1 秒后：一轮满月（参考 R_mis_moon：带环形山的银白满月，边上淡紫的光晕）从天上直直落到她身上，第 6 帧砸到，一道月光光柱（参考 R_up_cylinder）亮起，脚下炸开一个扁扁的大月光环，然后散去。画在她的站位点上：格子下部是她站的地面，月亮从格子顶部落下。约 70 格宽、120 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a moonlight ramp (#FFFFFF, #EAF8FF, #BFE4F2, #8FC7D8, #5E97AE), lavender (#E6D8FF, #B9A2F0, #8B6FD6) and dark violet shadows (#3E2C74, #26184A).
Effect: a FULL MOON CRASHING DOWN onto a spot on the ground at the bottom middle of the cell, 12 frames: 1 a small full moon (silver-white with a few grey craters, a lavender halo) appears at the top middle of the cell; 2-5 it falls straight down, growing, a trail of lavender light above it; 6 it hits the spot: a blinding white flash and a column of moonlight from the ground up to the top of the cell; 7 a flat wide ring of moonlight bursts out along the ground (twice as wide as tall, 90% of the cell's width), the column still bright; 8-9 the ring widens and thins, the column fades from the top; 10-11 the ring breaks into lavender sparkles; 12 faint sparkles on the ground.
Layout: one horizontal row of 12 equal cells, each 7 wide to 12 tall, image size 3360x576 (each cell 280x480... use each cell 280x480, image 3360x480); the spot on the ground at 85% of the cell's height, horizontally centered; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 17. `diana_fx_r_hit.png`：月之降临命中（每个被砸到的敌人），6 帧

被月光砸中：一道白色的竖直光束从上打下来，底部炸开淡紫的月光碎片（参考 R_Flash）。约 20 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline of any kind, a moonlight ramp (#FFFFFF, #EAF8FF, #BFE4F2, #8FC7D8) with lavender (#E6D8FF, #B9A2F0, #8B6FD6).
Effect: a MOONLIGHT STRIKE on a target, 6 frames: 1 a thin white vertical beam from the top of the cell down to the center; 2 the beam widens, a white flash where it meets the center; 3 lavender moonlight shards burst out round the center; 4 the beam fades from the top, the shards spread; 5 the shards fade; 6 faint specks.
Layout: one horizontal row of 6 equal cells, each 5 wide to 7 tall, image size 1500x420 (each cell 250x350... use each cell 250x350, image 1500x350); the impact at 70% of the cell's height, horizontally centered; no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```
