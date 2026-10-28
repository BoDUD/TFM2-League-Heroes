# 敖兴：给 Codex 的特效提示词（第 3 步）

> **这一份是 11 张特效图 + 3 个技能图标。** 造型已定（`design/aoshin_design.png`：竖直悬浮的风暴之龙，青绿鳞片的蛇形身体和浅青尖刺鬃毛，金面具和两只弯角，金护肩蓝宝石，蓝紫龙爪，尾巴尖化成青色的风）。敖兴在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），38 格高、38 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/aoshin_size.png`：他缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲第 7 赛季敖兴自己的特效贴图（球状闪电、落雷的闪电形状、风暴符印）和英雄联盟沃利贝尔的雷云、闪电贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **敖兴是风暴之龙，特效都是雷电和风暴**：锯齿形、带白色亮芯的**闪电**，噼啪的**青蓝色电弧和电火花**，深灰蓝的**雷云**，一点青色的**风**；不要火，不要紫色魔法，不要符文，不要软软的圆泡泡。
> - **特效要亮**：每道闪电都有白色的芯，暗底上一眼能看见。**光、电弧、风、云没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：围着人、在人身上炸开的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；飞行的 `a_ball` 四面对称、`q_beam` 上下对称（游戏会跟着飞行方向转它们）；从天上劈下来的 `p_bolt`、`r_bolt` 没有朝向，不用对称。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `aoshin_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入）；图标交付 `aoshin_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/aoshin_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/aoshin_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「风暴龙威」 | 开战几秒后，天雷劈向周围所有敌方英雄（最大生命值百分比真实伤害 + 晕眩），之后他身上缠着电光、伤害提高 | `p_bolt` · `p_storm` |
| 普攻 | 往前一扑，从嘴里吐出一团球状闪电 | `a_ball` · `a_hit` |
| 技能 1 =「雷息」 | 张嘴喷出一道直线闪电，打中的敌人被电麻（短暂放不了技能） | `q_beam` · `q_hit` · `q_sil` |
| 技能 2 =「腾云」 | 敌人贴近时卷起一团风云向后飞开，身上一层风暴护盾 | `e_cast` · `e_shield` |
| 大招 =「闪电暴雨」 | 立起身子召来头顶的雷云，一连串闪电随机劈向附近的敌方英雄，每道都电麻一下 | `r_cloud` · `r_bolt` · `q_sil` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电弧、风、云没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 闪电（亮芯、电弧、电火花、球状闪电）：`#FFFFFF`、`#DFFBFF`、`#8FEFFF`、`#36C8F4`、`#1A7FD0`；
  - 雷云：`#9AA6C0`、`#6A7690`、`#444E68`、`#262C40`；
  - 青色的风（风环、风雾）：`#BFF6FF`、`#6FE0F2`、`#2AB4D2`、`#18809E`；
  - 金色（只在图标的龙头和边角用）：`#FFF1A8`、`#FFD24A`、`#E0A020`、`#9A6410`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（11 张）

11 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `aoshin_fx_a_ball.png`：普攻：球状闪电（飞行中），4 帧循环

从他嘴里吐出的**一团球状闪电**：白色的芯、青蓝色的球，外面几道细小的电弧一跳一跳。**四面对称**（飞行时会跟着方向转），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: A BALL OF LIGHTNING IN FLIGHT, 4 looping frames, ROUND: SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square (the game turns it with its flight): a round ball 8 squares across - a white core 3 squares, pale cyan around it, a cyan-blue rim - with three or four tiny jagged arcs (2-3 squares) flicking out of it at different places in each frame (keep each frame symmetric). everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `aoshin_fx_a_hit.png`：普攻：球状闪电打中，4 帧

球状闪电打中：一下白色的闪光，一圈青蓝色的小电弧往外炸开，几颗电火花。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: A SMALL LIGHTNING POP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white star flash 8 squares across; 2 a ring of short jagged cyan-blue arcs bursting out 14 squares across, a white core; 3 the arcs broken into sparks flying out; 4 the last sparks fading. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `aoshin_fx_q_beam.png`：雷息：一道闪电（飞行中），3 帧循环

从他嘴里喷出去的**一段锯齿形闪电**：中间一条白色的亮芯，外面青蓝色，前头尖、后头散成几道细电弧。**朝右飞、上下对称**，3 帧循环（每帧锯齿位置变一下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: A SEGMENT OF A LIGHTNING BREATH, 3 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a jagged horizontal BOLT 38 squares long - a white core 1-2 squares thick zigzagging along it, pale cyan and cyan-blue around (6-8 squares thick in all), the head on the right pointed and brightest, the tail on the left splitting into three thin forks; the zigzag shifting in each frame. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 3 equal 40:10 cells, image size 1920x160 (each cell 640x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `aoshin_fx_q_hit.png`：雷息：被闪电打中，4 帧

被雷息打中：身上「啪」地一下炸开一团电光，几道电弧在身上乱窜，一圈电火花。比普攻大一点。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: A UNIT STRUCK BY LIGHTNING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), centred on the unit's body: 1 a white flash 12 squares across; 2 jagged cyan-blue arcs crawling over a body-sized area 18 wide and 22 tall (mirrored), a white core; 3 the arcs thinning, sparks flying out; 4 the last sparks. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 4 equal 20:24 cells, image size 1280x384 (each cell 320x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `aoshin_fx_q_sil.png`：被电麻（沉默）：头上冒电火花，6 帧循环

被雷息或闪电暴雨电麻了（放不了技能）：头顶上一圈**噼啪作响的小电弧**，像短路一样一闪一闪。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: A UNIT STUNG BY STATIC (silenced), 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 10 squares of the cell) a little crown of crackling jagged arcs 12 squares wide, white and cyan-blue, two tiny sparks hopping beside it (mirrored); frames 1-6 the arcs flickering on and off in turn. The rest of the cell empty. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 6 equal 18:44 cells, image size 1728x704 (each cell 288x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `aoshin_fx_e_cast.png`：腾云：飞起时的一团风云，5 帧

他向后飞开的那一下：原地「呼」地卷起一团青色的风和一小片灰白的云，往两边散开。中心在格子底部中间。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan scale-and-wind ramp (#BFF6FF, #6FE0F2, #2AB4D2, #18809E), a dark storm-cloud slate ramp (#9AA6C0, #6A7690, #444E68, #262C40).
Effect: A GUST OF CLOUD AT TAKE-OFF, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small puff of pale slate cloud 12 squares wide at the bottom middle; 2 two curls of cyan wind sweeping out to both sides (mirrored) from it, the cloud 24 wide; 3 the wind curls at their widest (38 squares), the cloud rising 20 squares; 4 the cloud thinning into wisps; 5 the last wisps. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 5 equal 40:26 cells, image size 3200x416 (each cell 640x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `aoshin_fx_e_shield.png`：腾云：风暴护盾，6 帧循环

护盾在的时候：他身体外面一圈**旋转的青色风环和几缕灰白的云**，风环上时不时闪过一道小电弧。身体位置留空（只画外圈）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan scale-and-wind ramp (#BFF6FF, #6FE0F2, #2AB4D2, #18809E), a dark storm-cloud slate ramp (#9AA6C0, #6A7690, #444E68, #262C40), an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: A WIND-AND-CLOUD SHIELD HELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the hovering dragon is in the middle, not drawn: 37 squares wide and 38 tall: an outline of streaming cyan wind 44 squares wide and 42 tall around him (2 squares thick, broken into curls), a few pale slate cloud wisps on it, one tiny white arc flicking along it in each frame (mirrored); the curls flowing round in turn. The middle (the body) left empty. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 6 equal 46:44 cells, image size 4416x704 (each cell 736x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `aoshin_fx_p_bolt.png`：风暴龙威：天雷劈中（被动），5 帧

被动「风暴龙威」：一道**又粗又亮的天雷从格子顶上直劈下来**，砸在人身上，脚下炸开一圈电光。人站在格子底部中间（不画人）。5 帧（半秒）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0), a dark storm-cloud slate ramp (#9AA6C0, #6A7690, #444E68, #262C40).
Effect: A BOLT FROM THE SKY ON A UNIT, 5 frames, the unit stands at the bottom middle, not drawn (16 squares wide, 36 tall): 1 a thin white jagged bolt from the very top of the cell down to the unit's feet, a little dark cloud wisp at the top; 2 the bolt at its thickest (5-6 squares: a white core, cyan-blue edges) with two forks, a white flash ring 20 squares wide at the feet on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 3 the bolt flickering thinner, cyan-blue sparks bursting from the feet; 4 the bolt gone, arcs crawling up the unit's outline; 5 the last sparks at the feet. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 5 equal 26:90 cells, image size 2080x1440 (each cell 416x1440, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `aoshin_fx_p_storm.png`：风暴龙威：落雷后他身上的电光（增伤），6 帧循环

落雷之后他变强的几秒：身上**噼啪地缠着几道电弧**，脚下一圈淡淡的青色电光。不要太显眼，身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: A CHARGED STORM AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the hovering dragon is in the middle, not drawn: 37 squares wide and 38 tall: four or five short jagged white-cyan arcs flicking along his outline (44 squares wide, 42 tall), a different few in each frame (mirrored), and a faint thin ring of cyan light 30 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) at the bottom. The middle (the body) left empty. Subtle. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 6 equal 46:44 cells, image size 4416x704 (each cell 736x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `aoshin_fx_r_cloud.png`：闪电暴雨：头顶的雷云（召雷时），6 帧循环

他召来闪电暴雨的这一秒多：**头顶上空一大团翻滚的乌云**，云里不停地闪着电光。云画在格子最上面 22 格，下面留出他的位置（不画他）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark storm-cloud slate ramp (#9AA6C0, #6A7690, #444E68, #262C40), an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: A STORM CLOUD OVERHEAD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the hovering dragon is in the middle, not drawn: 37 squares wide and 38 tall at the bottom middle: in the top 22 squares of the cell a big rolling dark slate STORM CLOUD 66 squares wide (lumpy, lit pale on its upper edges), lightning flashing inside it - in each frame one or two jagged white-cyan flashes at mirrored places, the cloud's lumps rolling slowly. The rest of the cell empty. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 6 equal 70:64 cells, image size 6720x1024 (each cell 1120x1024, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `aoshin_fx_r_bolt.png`：闪电暴雨：一道落雷劈中，6 帧

闪电暴雨的每一道雷：**一道锯齿形的闪电从格子顶上劈到人脚下**（比被动的天雷细一点、快一点），脚下炸开一小圈电光。人站在格子底部中间（不画人）。6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric white-cyan-blue ramp (#FFFFFF, #DFFBFF, #8FEFFF, #36C8F4, #1A7FD0).
Effect: ONE STRIKE OF A LIGHTNING STORM, 6 frames, the unit stands at the bottom middle, not drawn (16 squares wide, 36 tall): 1 a thin white flicker at the top of the cell; 2 a jagged bolt (3-4 squares thick: a white core, cyan-blue edges) from the top down to the feet; 3 the bolt bright with one fork, a white flash 14 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) at the feet; 4 the bolt thinner, sparks bursting from the feet; 5 a faint afterglow line, sparks falling; 6 the last sparks. everything is the STORM DRAGON's lightning: jagged forked BOLTS with a white core, crackling cyan-blue sparks, dark slate storm clouds, a gust of cyan wind; flat shades, crisp jagged shapes; no fire, no purple magic, no runes, no soft round bubbles.
Layout: one horizontal row of 6 equal 24:90 cells, image size 2304x1440 (each cell 384x1440, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `aoshin_icon_skill.png`：技能 1「雷息」图标

雷息：一个金色的龙头侧面朝右，张开的嘴里喷出一道粗粗的白色锯齿闪电，穿过整个图标。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with small gold corners, a deep storm-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a GOLD DRAGON HEAD in profile facing right at the left, its jaw open, breathing a thick jagged white-cyan LIGHTNING BOLT straight across to the right edge, small sparks along it. No text, no letters.
```

### 图标 2. `aoshin_icon_skill2.png`：技能 2「腾云」图标

腾云：一团卷着青色风的白云，上面一条青色的龙尾往左上方飞走。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with small gold corners, a deep storm-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a swirling white-and-pale-slate CLOUD with curls of cyan wind in the lower half, a cyan dragon's spiky TAIL sweeping away up to the upper left out of it. No text, no letters.
```

### 图标 3. `aoshin_icon_ult.png`：大招「闪电暴雨」图标

闪电暴雨：上面一大团乌云，好几道白色的闪电同时劈下来。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with small gold corners, a deep storm-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big dark slate STORM CLOUD across the top, four jagged white-cyan LIGHTNING BOLTS striking down from it to the bottom edge, little flashes where they land. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `aoshin_fx_a_ball` | view_projectiles `tft_aoshin_a_ball`（追踪弹道，z 2；圆的、四面对称） | 12 × 12 |
| `aoshin_fx_a_hit` | view_effects `tft_aoshin_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `aoshin_fx_q_beam` | view_projectiles `tft_aoshin_q_beam`（直线、很快，z 2；上下对称） | 40 × 10 |
| `aoshin_fx_q_hit` | view_effects `tft_aoshin_q_hit`（跟随被打中的人，z 2；左右对称） | 20 × 24 |
| `aoshin_fx_q_sil` | view_buffs `tft_aoshin_q_sil`（跟随被沉默的人，z 4；左右对称；大招的沉默也用它） | 18 × 44 |
| `aoshin_fx_e_cast` | view_effects `tft_aoshin_e_cast`（留在起飞的地方，z 1；左右对称） | 40 × 26 |
| `aoshin_fx_e_shield` | view_buffs `tft_aoshin_e_shield`（跟随他，z 3；左右对称） | 46 × 44 |
| `aoshin_fx_p_bolt` | view_buffs `tft_aoshin_p_bolt`（大表，跟随被劈的人，z 3；不用左右对称） | 26 × 90 |
| `aoshin_fx_p_storm` | view_buffs `tft_aoshin_p_storm`（跟随他，z 3；左右对称） | 46 × 44 |
| `aoshin_fx_r_cloud` | view_buffs `tft_aoshin_r_cloud`（大表，跟随他，z 4；左右对称） | 70 × 64 |
| `aoshin_fx_r_bolt` | view_effects `tft_aoshin_r_bolt`（大表，劈在被打中的人身上，z 3；不用左右对称） | 24 × 90 |
| `aoshin_icon_skill` | skill_icons[0] `asset/tft/icons/tft_aoshin_skill` | 64 × 64 |
| `aoshin_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_aoshin_skill2` | 64 × 64 |
| `aoshin_icon_ult` | skill_icons[2] `asset/tft/icons/tft_aoshin_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_aoshin_fx`（小的）和 `tft_aoshin_big`（p_bolt、r_cloud、r_bolt），tag = 名字；r_sil 用 q_sil 的 tag。
- 对称按 `SYM`（其余左右对称）断言。
- p_bolt、p_storm 是 tft.dll 在风暴龙威落雷时挂的 buff（30 tick / p_t tick）；r_cloud 在大招整个施法期间挂在他身上；r_bolt 是每道落雷打在被劈的人身上的 ViewEffect；q_beam 是从他嘴里（y_offset q_y）飞出去的纯画面弹道。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
