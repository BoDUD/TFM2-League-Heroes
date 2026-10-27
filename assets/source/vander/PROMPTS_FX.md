# 范德尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图 + 3 个技能图标。** 造型已定（`design/vander_design.png`：祖安地下城的老拳手，往后梳的头发、短络腮胡、焦橙色皮夹克，一只手戴着黄铜框红面板的大铁拳套，屈膝压低的格斗架势）。范德尔在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），40 格高、41 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/vander_size.png`：范德尔缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里范德尔自己的特效贴图（**灰色的形状，游戏里再染色**：防御波纹、打击、冲击环、碎石、尘土），按用在我们哪张特效分好了行。只在本地用。
> - **范德尔是祖安的老拳手，特效都是他的铁拳**：白热的拳光、黄铜和红色的金属火星、厚重的冲击环、祖安的尘土和碎石；防御姿态和监察是冷冷的钢蓝色波纹，嘲讽是红色的愤怒标记；不要魔法符文，不要光滑的霓虹光束，不要火柱。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、波纹、冲击波、尘土没有黑描边**（拳头徽记、星星、螺栓这些实物可以有一圈深色描边）。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。他没有飞行道具，没有要朝向的画面。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `vander_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）；图标交付 `vander_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/vander_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/vander_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「监察」 | 一直少受伤害，血量高于一半时减得更多 | `p_watch` |
| 普攻 | 戴拳套的手抡一记重拳 | `a_hit` |
| 技能 1 =「地下猎犬」 | 摆出防御姿态，嘲讽身边的敌人，加护甲魔抗；下一拳换成一记重击 | `q_guard_in` · `q_guard` · `q_taunt` · `q_ready` · `q_hit` |
| 技能 2 =「铁拳突进」 | 冲到敌人身上打一记上勾拳，晕眩，周围的敌人一起挨一部分 | `e_dash` · `e_hit` · `e_stun` |
| 大招 =「桥头死守」 | 跳进敌群，拳套砸地，冲击波击飞周围的敌人；之后几秒减伤（身边敌人越多减得越多） | `r_slam` · `r_hit` · `r_hold` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、波纹、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 黄铜（拳套框、螺栓、图标边框）：`#FFF4D0`、`#F6D27A`、`#D69A3A`、`#94601E`、`#4E300C`；
  - 拳套红：`#FFD8C8`、`#FF6A4A`、`#D8262A`、`#8E1220`、`#460812`；
  - 白热拳光：`#FFFFFF`、`#FFF0C0`、`#FFB850`、`#F06A1E`、`#A0300C`；
  - 尘土：`#F0E2C8`、`#C8AE88`、`#9A7E5C`、`#64503A`；
  - 嘲讽红：`#FFE4D8`、`#FF8A6A`、`#E8382C`、`#A01822`、`#4C0A10`；
  - 钢蓝（防御、监察）：`#F2F8FF`、`#C8DCEE`、`#8EAACC`、`#56709A`、`#2C3C5C`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `vander_fx_a_hit.png`：普攻：铁拳打中，4 帧

拳套砸在人身上：一下白热的闪光，几颗黄铜和红色的火星往两边崩开，一小圈冲击环。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C).
Effect: A HEAVY PUNCH IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot star flash 8 squares across; 2 a short orange shock ring 12 squares wide and 6 tall, brass and red sparks flying out to both sides (mirrored); 3 the ring thinner and wider, the sparks farther, a puff of dust in the middle; 4 the last dust fading. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `vander_fx_q_guard_in.png`：地下猎犬：跳进防御姿态的一下，5 帧

范德尔放技能 1 时重重一踏摆出防御架势：脚下「咚」地一圈黄铜色冲击环和尘土，身体外面一层**钢蓝色的波纹轮廓**往外一荡（像挡下攻击的气墙），两边各有一道向上的短光。身体位置留空。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cold steel blue ramp (#F2F8FF, #C8DCEE, #8EAACC, #56709A, #2C3C5C), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A FIGHTER DROPPING INTO HIS GUARD, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad man stands in the middle, not drawn: 40 squares wide and 40 tall (a low wide fighting stance): 1 a brass flash on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 squares wide; 2 a brass shock ring on the ground 36 squares wide and 10 tall, dust puffs to both sides; 3 a steel-blue RIPPLE outline (two or three thin wavy lines) bulging out round him, a wide dome 42 squares wide and 44 tall, short upward streaks at both sides (mirrored); 4 the ripple wider and thinner; 5 fading to a few steel glints. Only the edges: the middle (the body) left empty. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 5 equal 44:48 cells, image size 3520x768 (each cell 704x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `vander_fx_q_guard.png`：地下猎犬：防御姿态（加双抗），6 帧循环

防御姿态还在：他身体两侧各一道**钢蓝色的弧形波纹**（像挡在身前的气墙），慢慢一荡一荡，脚下一圈淡淡的黄铜光圈。身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cold steel blue ramp (#F2F8FF, #C8DCEE, #8EAACC, #56709A, #2C3C5C), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C).
Effect: A HELD GUARD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad man stands in the middle, not drawn: 40 squares wide and 40 tall (a low wide fighting stance): at both sides of him (mirrored) a tall curved steel-blue RIPPLE arc (two thin wavy lines, 30 squares tall) like a wall of force, and a faint brass ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 34 squares wide and 8 tall at the bottom; frames 1-6 the arcs wavering out and in, a glint running up them. The middle (the body) left empty. Subtle. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 44:48 cells, image size 4224x768 (each cell 704x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `vander_fx_q_ready.png`：地下猎犬：下一拳是重击（蓄着劲），6 帧循环

重击还没打出去：他头顶上方一枚小小的**黄铜色拳头徽记**（红色的指节），一跳一跳地发着热光，周围几点橙色火星往上飘。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C), a gauntlet red ramp (#FFD8C8, #FF6A4A, #D8262A, #8E1220, #460812), a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C).
Effect: A PUNCH CHARGED, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad man stands in the middle, not drawn, 40 squares tall: over the head (the top 10 squares of the cell) a small brass FIST emblem seen from the front, 7 squares wide and 7 tall, red knuckle plates, a white-hot glint, and two or three orange embers drifting up beside it (mirrored); frames 1-6 the fist throbbing one square bigger and back, the embers rising. The rest of the cell empty. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 20:48 cells, image size 1920x768 (each cell 320x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `vander_fx_q_hit.png`：地下猎犬：重击打中，6 帧

蓄好的那一记重击：一下很大的白热闪光，一个**红铜色的八角形冲击波**（拳套的形状）往外炸开，橙色火星和碎石四溅，留一团尘土。比普攻狠得多。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a gauntlet red ramp (#FFD8C8, #FF6A4A, #D8262A, #8E1220, #460812), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A CRUSHING GAUNTLET BLOW, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-hot flash 14 squares across; 2 an OCTAGONAL red-and-brass shock wave (the gauntlet's outline) 16 squares across bursting out, orange sparks flying out to both sides (mirrored); 3 a wide orange shock ring 28 squares wide and 12 tall, the sparks farther, grit stones; 4 the ring thin, dust puffs in the middle; 5 the dust spreading; 6 the dust fading. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal square cells, image size 2880x480 (each cell 480x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `vander_fx_q_taunt.png`：地下猎犬：被嘲讽（只能打他），6 帧循环

被嘲讽的人：头顶一个**红色的愤怒标记**（十字形的「青筋」符号），一跳一跳的，脚下一圈淡红色的光圈。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a taunt red ramp (#FFE4D8, #FF8A6A, #E8382C, #A01822, #4C0A10), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C).
Effect: A TAUNTED UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 9 squares of the cell) a red ANGER MARK (the comic cross-vein symbol: four short curved red strokes in a cross, 7 squares across) with a brass glint, and a faint red ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 14 squares wide and 4 tall at the bottom; frames 1-6 the mark throbbing bigger and smaller, the ring pulsing. The middle (the body) left empty. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 16:44 cells, image size 1536x704 (each cell 256x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `vander_fx_e_dash.png`：铁拳突进：起步踢起的尘土，5 帧

冲出去那一脚：地上「轰」地踢起一团尘土和碎石，往两边扩散开再落下。留在他起跑的地上（不跟着他），画成圆的，往哪边冲都能用。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C).
Effect: A DASH'S KICK-OFF DUST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a burst of dust 10 squares wide at the bottom middle, two small grit stones flung up to both sides (mirrored); 2 the dust spreading 20 squares wide and 8 tall, rolling puffs; 3 30 squares wide, the stones falling; 4 thinning; 5 the last thin puffs. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 5 equal 32:14 cells, image size 2560x224 (each cell 512x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `vander_fx_e_hit.png`：铁拳突进：上勾拳打中（晕眩），5 帧

上勾拳从下往上打中：一道**竖直往上的白热光柱**，橙色和黄铜色的火星呈 V 字往两边上方喷出，脚下一小圈冲击环。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: AN UPPERCUT HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot flash in the middle 8 squares across; 2 a tall narrow vertical streak of light shooting UP 24 squares from the middle, orange and brass sparks spraying up and out in a V to both sides (mirrored), a small shock ring at the bottom 14 squares wide and 4 tall; 3 the streak thinner, the sparks higher; 4 the sparks falling, dust at the bottom; 5 the last sparks fading. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 5 equal 22:32 cells, image size 1760x512 (each cell 352x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `vander_fx_e_stun.png`：铁拳突进：晕眩，6 帧循环

被打晕的人：头顶上一圈**黄铜色的小星星**和小螺栓绕着转。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C), a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C).
Effect: A STUNNED UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 10 squares of the cell) a flat ring of three small brass STARS and two tiny hexagonal BOLTS (each 3x3 squares) circling round, seen from the side (an ellipse 14 wide and 4 tall), a tiny white glint; frames 1-6 them moving round the ring (the ones in front brighter, mirrored positions). The rest of the cell empty. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 18:44 cells, image size 1728x704 (each cell 288x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `vander_fx_r_slam.png`：桥头死守：拳套砸地的冲击波，8 帧

大招：从半空落下，拳套狠狠砸进地面，**地面炸开一圈很大的冲击波**（从中间往外推的橙红色和黄铜色的环），地上裂开几道裂缝，碎石和尘土往四周飞，裂缝里透出一点橙红的热光，最后慢慢暗下去。这是画在**地上**的（从斜上方看的扁椭圆），中心在格子底部中间（他的脚下）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A GROUND SHOCKWAVE, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell (his feet): 1 a white-hot flash 16 squares wide; 2 a thick orange shock ring 36 squares wide and 12 tall with a brass outer edge, CRACKS (dark brown lines 1 square wide) starting out from the middle (mirrored); 3 the ring 58 wide and 18 tall, the cracks longer, chunks of stone and dust flung up to both sides; 4 the ring 80 wide and 26 tall, thinner; 5 the ring at the edge breaking into bright segments, dust billowing; 6 the dust settling, the cracks glowing orange; 7 the cracks dimming; 8 faint cracks and thin dust. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 8 equal 88:30 cells, image size 11264x480 (each cell 1408x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `vander_fx_r_hit.png`：桥头死守：被击飞，4 帧

被冲击波掀起来的人：脚下「砰」地一下橙色的闪光，尘土往上喷，两边几颗碎石。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A UNIT THROWN UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an orange-white flash at the bottom middle 10 squares wide; 2 a jet of dust shooting upward 14 squares high, grit stones to both sides (mirrored); 3 the dust spreading and thinning; 4 the last puffs. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `vander_fx_r_hold.png`：桥头死守：死守（减伤），6 帧循环

砸地之后范德尔死守在原地：脚下一圈**橙红色的热光圈**，身体两侧有几点**橙色的火星**慢慢往上飘，外面一层很淡的钢蓝色轮廓。身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a cold steel blue ramp (#F2F8FF, #C8DCEE, #8EAACC, #56709A, #2C3C5C), a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C).
Effect: A LAST STAND, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad man stands in the middle, not drawn: 40 squares wide and 40 tall (a low wide fighting stance): a glowing orange-red ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 36 squares wide and 8 tall at the bottom, at both sides of him (mirrored) a few orange EMBERS (1-2 squares) drifting upward from the ring to his shoulders, and a faint thin steel-blue outline arc at each side; frames 1-6 the embers rising and new ones starting, the ring breathing. The middle (the body) left empty. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 44:50 cells, image size 4224x800 (each cell 704x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `vander_fx_p_watch.png`：监察：减伤（一直在，血多时更强），6 帧循环

监察的被动一直挂着，所以**要很淡**：只在他脚下一圈细细的**钢蓝色光圈**，一个亮点沿着光圈慢慢转。不要画在身上。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cold steel blue ramp (#F2F8FF, #C8DCEE, #8EAACC, #56709A, #2C3C5C).
Effect: A WATCHER'S CALM GUARD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): only a thin steel-blue ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 34 squares wide and 8 tall at the bottom of the cell, one square thick; frames 1-6 two bright glints at mirrored places sliding round the ring. Very subtle: thin, few squares, nothing above the ground. everything is an old UNDERCITY BRAWLER's IRON GAUNTLET at work: hot white-orange punch flashes, brass and red metal glints, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 40:12 cells, image size 3840x192 (each cell 640x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `vander_icon_skill.png`：技能 1「地下猎犬」图标

红铜色的大铁拳套竖着举在前面挡住，后面一道钢蓝色的弧形波纹，拳套边上一点白热的光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRASS frame with little riveted corners, a deep rust-brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: his IRON GAUNTLET (an octagonal brass frame, two red panels, gold hexagonal bolts, brass knuckle plates, a purple bracer at the wrist) raised upright in front as a guard, filling the middle, a curved steel-blue ripple of force behind it, a white-hot glint on its knuckles. Colours: a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C), a gauntlet red ramp (#FFD8C8, #FF6A4A, #D8262A, #8E1220, #460812), a cold steel blue ramp (#F2F8FF, #C8DCEE, #8EAACC, #56709A, #2C3C5C). No text, no letters.
```

### 图标 2. `vander_icon_skill2.png`：技能 2「铁拳突进」图标

一只缠着绷带的拳头从左下往右上勾出去，后面拖着橙色的速度线和尘土。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRASS frame with little riveted corners, a deep rust-brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big fist wrapped in grey-white bandages driving UP from the lower left to the upper right in an uppercut, bold orange speed lines and a puff of dust trailing behind it, a white-hot flash at the knuckles. Colours: a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A). No text, no letters.
```

### 图标 3. `vander_icon_ult.png`：大招「桥头死守」图标

大铁拳套从上往下砸进地面，地面炸开一圈橙红和黄铜色的冲击波，裂缝四散，碎石飞起。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRASS frame with little riveted corners, a deep rust-brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: his IRON GAUNTLET (an octagonal brass frame, two red panels, gold hexagonal bolts, brass knuckle plates, a purple bracer at the wrist) smashing DOWN into the ground at the centre, an orange-and-brass SHOCKWAVE ring bursting out flat around it, cracks spreading through the ground, grit stones flying up. Colours: a brass ramp (#FFF4D0, #F6D27A, #D69A3A, #94601E, #4E300C), a gauntlet red ramp (#FFD8C8, #FF6A4A, #D8262A, #8E1220, #460812), a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `vander_fx_a_hit` | view_effects `tft_vander_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `vander_fx_q_guard_in` | view_effects `tft_vander_q_guard_in`（跟随他，z 3；左右对称） | 44 × 48 |
| `vander_fx_q_guard` | view_buffs `tft_vander_q_guard`（跟随他，z 3；左右对称） | 44 × 48 |
| `vander_fx_q_ready` | view_buffs `tft_vander_q_ready`（跟随他，z 3；左右对称） | 20 × 48 |
| `vander_fx_q_hit` | view_effects `tft_vander_q_hit`（跟随目标，z 2；左右对称） | 30 × 30 |
| `vander_fx_q_taunt` | view_buffs `tft_vander_q_taunt`（跟随被嘲讽的人，z 4；左右对称） | 16 × 44 |
| `vander_fx_e_dash` | view_effects `tft_vander_e_dash`（留在起跑的地上，z 1；左右对称） | 32 × 14 |
| `vander_fx_e_hit` | view_effects `tft_vander_e_hit`（跟随目标，z 2；左右对称） | 22 × 32 |
| `vander_fx_e_stun` | view_buffs `tft_vander_e_stun`（跟随被晕的人，z 3；左右对称） | 18 × 44 |
| `vander_fx_r_slam` | view_effects `tft_vander_r_slam`（大表，留在他脚下的地上，z -1；左右对称） | 88 × 30 |
| `vander_fx_r_hit` | view_effects `tft_vander_r_hit`（跟随被击飞的人，z 2；左右对称） | 18 × 20 |
| `vander_fx_r_hold` | view_buffs `tft_vander_r_hold`（跟随他，z 3；左右对称） | 44 × 50 |
| `vander_fx_p_watch` | view_buffs `tft_vander_p_watch`（跟随他，z 1；左右对称） | 40 × 12 |
| `vander_icon_skill` | skill_icons[0] `asset/tft/icons/tft_vander_skill` | 64 × 64 |
| `vander_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_vander_skill2` | 64 × 64 |
| `vander_icon_ult` | skill_icons[2] `asset/tft/icons/tft_vander_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_vander_fx`（小的）和 `tft_vander_big`（r_slam），tag = 名字。
- 全部断言左右对称。
- p_watch 由 tft.dll 按血量挂上（一直在）；r_hold 由 tft.dll 在砸地时挂上；q_guard_in 在技能 1 出手时播。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
