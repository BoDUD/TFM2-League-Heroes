# 无畏战车 厄加特：给 Codex 的特效提示词（第 3 步）

> **这一份是 22 张特效图。** 造型和动作已定（`design/urgot_idle.png`：3/4 正面朝右，苍白光头、防毒面具、毒绿软管，头顶举着巨大的霰弹炮臂，下面是青铜底盘和六条带盾甲的机械腿）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连炮臂 44 格高、47 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/urgot_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/urgot_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。**炮口火光已经画进他自己的帧里了，不用再画。**
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里厄加特自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**霰弹的火光是橙黄色（白芯）**，**化学药剂（酸液、钻头的光、爆炸）是毒绿色**，**电荷罐和钻头是钢灰色**，**处决和恐惧带一点深紫色**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，要淡一点，不要盖住人。
> - **方向（重要，红色方不会镜像）**：飞出去的 `a_shot`、`w_shot`、`r_drill` 和腿上霰弹的扇形 `p_fan` 画成朝右，**上下对称**（往左时会上下翻）；电荷罐 `q_charge` 上下左右都对称。其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `urgot_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `urgot_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「回响烈焰」 | 炮臂打霰弹；腿上的霰弹枪轮流朝目标喷扇形火焰 | `a_shot` · `a_hit` · `p_fan` · `p_hit` |
| W「净除」（Q 或 E 打中后自动开 4 秒） | 普攻换成机枪连射 | `w_shot` · `w_hit` · `w_on` |
| 技能 1 = Q「腐蚀电荷」 | 抛出电荷罐，落地 0.2 秒后炸成酸液，减速 | `q_charge` · `q_mark` · `q_blast` · `q_hit` · `q_slow` |
| 技能 2 = E「鄙弃」 | 带护盾冲向英雄，撞上后眩晕并甩到身后 | `e_shield` · `e_hit` · `e_fling` |
| 大招「超越死亡的恐惧」 | 胸口发射化学钻头钉住英雄，4 秒后拽回来处决，处决成功周围敌人恐惧 | `r_drill` · `r_hit` · `r_leash` · `r_reel` · `r_ex` · `r_fear` · `r_flee` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、烟、火星、酸液、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（电荷罐和钻头例外：钢制的东西可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 霰弹火光：`#FFFFFF`、`#FFF2B0`、`#FFD447`、`#FF9A1F`、`#D9541A`、`#7A260F`；
  - 毒绿化学药剂：`#FFFFFF`、`#EFFFB0`、`#B6FF3B`、`#4FE01E`、`#1E9A1A`、`#0B4A12`；
  - 钢（电荷罐、钻头、锁链）：`#E6EEF5`、`#A9B8C9`、`#6E7F94`、`#3E4A5C`、`#20262F`；
  - 深紫恐惧（处决、恐惧）：`#F4E8FF`、`#C49BFF`、`#8A4FE0`、`#55279E`、`#2A1150`；
  - 泥土：`#C9A27A`、`#9A7350`、`#6B4B33`、`#3E2A1C`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（22 张）

22 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 38000，腿上霰弹的扇形 52000 长，电荷爆炸半径 21000，恐惧半径 40000）。

### 1. `urgot_fx_a_shot.png`：普攻：霰弹（朝目标飞，循环），3 帧

炮臂打出去的一团霰弹：几颗亮橙黄色的弹丸挤在一起往右飞，最前面最亮（白芯），后面拖短短的火光尾巴（参考 Z_PierceSpark、Z_BrightSpark、BA_Mis_Air）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shotgun fire ramp (#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F).
Effect: a SHOTGUN SLUG CLUSTER flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): 5 bright pellets (2 squares each, white cores) in a tight wedge pointing right, the front one biggest; short orange-yellow streak tails 4-6 squares behind them, flickering between frames.
Layout: one horizontal row of 3 equal 14:8 cells, image size 672x128 (each cell 224x128, 16 px a square); the front pellet 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `urgot_fx_w_shot.png`：W 净除：机枪子弹（朝目标飞，循环），2 帧

净除的机枪曳光弹：一道细长的亮黄色光弹，白色弹头在右边（会连续出现很多发，要小）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shotgun fire ramp (#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F).
Effect: a THIN TRACER BULLET flying to the RIGHT, 2 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white 2-square head at the RIGHT end, a yellow-to-orange streak 6 squares long behind it, 1 square thick (2 at the head), the streak's length flickering.
Layout: one horizontal row of 2 equal 10:4 cells, image size 320x64 (each cell 160x64, 16 px a square); vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `urgot_fx_p_fan.png`：被动 回响烈焰：腿上霰弹喷出的扇形火焰（一条线，朝目标），4 帧

腿上的霰弹枪喷出一道扇形的火焰：尖端在左边（他的腿），向右张开成一个扇形，里面是一颗颗亮橙黄色的弹丸和火舌，外缘带一点毒绿色的火星（参考 Z_BlastStreaks、Z_BlastShapes、Z_ShockBlasts、Z_PierceSpark）。**上下对称**。这张图的中心就是扇形线的中点：从格子左边一直到右边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shotgun fire ramp (#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F) and a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a SHOTGUN BLAST CONE to the RIGHT, 4 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): 1 a white-yellow flash 6 squares at the LEFT edge (the apex), a few pellets leaving; 2 a fan of orange-yellow flame streaks and white-cored pellets opening from the apex to 16 squares tall halfway; 3 the fan reaching the RIGHT edge, 24 squares tall there, pellets scattered over it at mirrored places, a few toxic green sparks at its outer edges; 4 the fan breaking into fading pellets and sparks near the right end.
Layout: one horizontal row of 4 equal 52:24 cells, image size 3328x384 (each cell 832x384, 16 px a square); the apex in the middle of the LEFT edge, the fan symmetric about the middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `urgot_fx_a_hit.png`：普攻命中（目标身上），4 帧

霰弹打中：一团橙黄色的弹片火花炸开。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shotgun fire ramp (#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F).
Effect: a SHOTGUN HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 an orange-yellow burst 8 squares with a white core; 3 the burst 10 squares, 6 pellet sparks flying out at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `urgot_fx_w_hit.png`：W 净除：机枪命中（目标身上），3 帧

机枪每一发打中：一小点黄色火花（会连续出现很多次，要小）。**左右对称**。约 6 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shotgun fire ramp (#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F).
Effect: a TINY BULLET SPARK on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a yellow star 5 squares; 3 4 fading motes.
Layout: one horizontal row of 3 equal square cells, image size 384x128 (each cell 128x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `urgot_fx_p_hit.png`：被动 回响烈焰：命中（目标身上），4 帧

腿上霰弹打中：比普攻大一点的橙黄色爆炸，混着毒绿色的火星（参考 Z_ExplosionFireGreen、Z_FlareOmni）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shotgun fire ramp (#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F) and a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a BLAST HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 an orange-yellow burst 10 squares with a white core; 3 the burst 14 squares, toxic green sparks and pellet streaks flying out at mirrored places; 4 fading green and orange motes.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `urgot_fx_w_on.png`：W 净除：开火期间脚下（跟随他，循环），4 帧

净除开火的 4 秒里：他脚下一圈淡淡的橙黄色热浪光圈（扁椭圆），几个弹壳和火星在光圈上跳（参考 W_Aura_Self、P_sparks）。**左右对称**，只画地上的光圈，中间身体位置不画东西，要淡一点。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shotgun fire ramp (#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F).
Effect: a FAINT HEAT RING on the ground round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat orange-yellow ellipse ring 46 squares wide and 10 tall, 1-2 squares thick, half transparent-looking (use the darker shades), its brightness running round; 4 small brass shell casings (2 squares) and sparks hopping on the ring at mirrored places, taking turns.
Layout: one horizontal row of 4 equal 48:12 cells, image size 3072x192 (each cell 768x192, 16 px a square); centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `urgot_fx_q_charge.png`：Q 腐蚀电荷：飞行中的电荷罐（循环），4 帧

抛出去的腐蚀电荷：一个钢制的小罐子，中间一圈发亮的毒绿色液体，两头是钢盖，翻滚着飞（参考 Q_Projectile_TX_CM 的罐子）。**上下左右都对称**（每帧可以转 90°）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F) and a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a TUMBLING CHEMICAL CANISTER, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame (it may be drawn turned either way): a steel capsule 6 squares long and 4 thick with steel caps at both ends and a glowing toxic green band in the middle, turned 0, 45, 90 and 135 degrees in the 4 frames, a faint green glow 1 square round the band.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `urgot_fx_q_mark.png`：Q 腐蚀电荷：落点标记（地上，不跟随，循环），4 帧

电荷还在空中时，地上的落点：一圈毒绿色的警示圆环（扁椭圆），里面几道细细的绿色十字线，闪烁。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a TOXIC TARGET RING on the ground, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat toxic green ellipse ring 40 squares wide and 13 tall, 1 square thick, with 4 short tick marks at its top, bottom, left and right, a faint green cross in its middle; the ring's brightness pulsing (frames 2-3 brightest).
Layout: one horizontal row of 4 equal 42:14 cells, image size 2688x224 (each cell 672x224, 16 px a square); centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `urgot_fx_q_blast.png`：Q 腐蚀电荷：落地后的酸液爆炸（地上，不跟随），7 帧

电荷落地：前 3 帧是落在地上的罐子在闪绿光（0.2 秒的引信），然后炸成一团毒绿色的酸液爆炸，地上溅开一圈绿色酸液，飞起几块泥土（参考 Z_ExplosionFireGreen、Q_Acidflicker、Q_DirtChunks、Q_crater、Z_SmokePoofs）。**左右对称**。爆炸范围约 42 格宽（扁椭圆的地面 + 往上的爆炸）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12) and a steel ramp (#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F) and a dirt ramp (#C9A27A, #9A7350, #6B4B33, #3E2A1C).
Effect: a CANISTER LANDING THEN AN ACID EXPLOSION, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1-3 the small steel canister (6 squares) lying in the middle of the cell's lower part, its green band blinking brighter each frame; 4 a white-lime flash 12 squares; 5 a toxic green explosion 30 squares wide and 24 tall rising from the ground, a flat acid splash ellipse 42 wide and 12 tall under it, dirt chunks thrown out at mirrored places; 6 the explosion breaking into green smoke puffs, the splash ring at full width; 7 the splash fading, a few green drops and dirt bits.
Layout: one horizontal row of 7 equal 44:30 cells, image size 4928x480 (each cell 704x480, 16 px a square); centered across, the ground ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `urgot_fx_q_hit.png`：Q 腐蚀电荷：命中（目标身上），4 帧

被酸液溅到：目标身上溅开一团毒绿色的酸液，几滴往下流（参考 P_fluid、Q_Acidflicker）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: an ACID SPLASH on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-lime flash 4 squares; 2 a toxic green splash 12 squares with lime highlights; 3 green droplets flying out and dripping down at mirrored places, 14 squares; 4 a few green drips falling.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `urgot_fx_q_slow.png`：Q 腐蚀电荷：减速（目标脚下，跟随，循环），4 帧

被减速时脚下：一小滩冒泡的毒绿色酸液（扁椭圆）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a BUBBLING ACID PUDDLE on the ground, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat toxic green puddle ellipse 18 squares wide and 5 tall, darker at its rim, 3-4 lime bubbles rising and popping at mirrored places, taking turns.
Layout: one horizontal row of 4 equal 20:6 cells, image size 1280x96 (each cell 320x96, 16 px a square); centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `urgot_fx_e_shield.png`：E 鄙弃：冲锋时他身上的护盾（跟随），6 帧

冲锋开始时他获得的护盾：一层钢灰色带毒绿色边光的护甲力场罩住他，从脚下往上合拢，亮一下后变淡（参考 W_Aura_Self、P_GlowingVents）。**左右对称**，中间身体位置留空（a wide figure 46 squares wide and 42 tall stands in the middle, not drawn），光要淡一点、不要盖住他。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F) and a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a STEEL ENERGY SHIELD closing round a wide figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a wide figure 46 squares wide and 42 tall stands in the middle, not drawn): 1 steel-grey light at both sides of the feet; 2 two curved steel-grey plates of light rising at both sides with toxic green edges; 3 the plates meeting above the head into a dome outline 54 squares wide and 48 tall, a few hex lines on it; 4 the dome brightest, green glints running along its edge; 5-6 the dome fading to a faint outline.
Layout: one horizontal row of 6 equal 58:52 cells, image size 5568x832 (each cell 928x832, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `urgot_fx_e_hit.png`：E 鄙弃：撞上英雄（目标身上），4 帧

冲锋撞上英雄：一团钢灰色和橙色的冲击火花炸开，一圈冲击环，头顶几颗小星星（眩晕）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F) and a shotgun fire ramp (#FFFFFF, #FFF2B0, #FFD447, #FF9A1F, #D9541A, #7A260F).
Effect: a CRUSHING IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a steel-grey and orange burst 14 squares; 3 a shockwave ring 18 squares across, three small yellow stars in a ring 8 squares above the middle; 4 the ring fading, the stars turning.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `urgot_fx_e_fling.png`：E 鄙弃：被甩到身后落地（目标身上），5 帧

被甩过他头顶、砸在他身后：落地扬起一圈尘土和碎石（扁的），中间一下钢灰色的冲击（参考 Z_SmokePoofs、Q_DirtChunks）。**左右对称**，只画地上的尘土和冲击。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dirt ramp (#C9A27A, #9A7350, #6B4B33, #3E2A1C) and a steel ramp (#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F).
Effect: a SLAM INTO THE GROUND under a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a steel-white flash 8 squares on the ground; 2 a flat dust ring 18 wide and 6 tall bursting out, pebbles thrown up at mirrored places; 3 the dust 26 wide, two dust clouds at both ends; 4-5 the dust thinning and settling.
Layout: one horizontal row of 5 equal 28:16 cells, image size 2240x256 (each cell 448x256, 16 px a square); centered across, the ground on the cell's bottom third. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `urgot_fx_r_drill.png`：R 超越死亡的恐惧：化学钻头（朝目标飞，循环），4 帧

从胸口发射的化学钻头：一个钢制的锥形钻头（尖端朝右），钻头上一圈螺旋纹在转，尾部一颗发光的毒绿色化学球，后面拖一条绿色的光尾（参考 R_Projectile_TX_CM 的钻头和绿球、Z_EnergyStreaksAdd）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F) and a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a CHEM-DRILL flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a steel cone drill 10 squares long pointing RIGHT, its spiral grooves shifting a square each frame (spinning), a glowing toxic green orb 4 squares at its back end, a green light trail 6 squares behind it, flickering.
Layout: one horizontal row of 4 equal 20:10 cells, image size 1280x160 (each cell 320x160, 16 px a square); the drill's tip 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `urgot_fx_r_hit.png`：R 超越死亡的恐惧：钻头钉中（目标身上），5 帧

钻头钉进英雄：一团毒绿色的化学爆闪，钢灰色的碎屑和火花往外飞。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12) and a steel ramp (#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F).
Effect: a DRILL IMPALING HIT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-lime flash 6 squares; 2 a toxic green burst 14 squares; 3 the burst 18 squares, steel-grey shards and yellow sparks flying out at mirrored places; 4 green smoke wisps; 5 fading motes.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `urgot_fx_r_leash.png`：R：被拴住期间（目标身上，跟随，循环），4 帧

被钻头拴住的 4 秒里：目标身上缠着一圈发光的毒绿色化学锁链（扁椭圆，绕在腰上），胸口一点绿光在跳（像心跳），锁链上的绿光一节一节地流动。**左右对称**，中间身体位置留空（一个约 18 格宽、30 格高的人），要淡一点。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12) and a steel ramp (#E6EEF5, #A9B8C9, #6E7F94, #3E4A5C, #20262F).
Effect: a GLOWING CHEMICAL CHAIN round a figure's waist, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 18 squares wide and 30 tall stands in the middle, not drawn): a flat ellipse of steel chain links 24 squares wide and 7 tall at the waist (14 squares above the bottom row), toxic green light running along the links frame by frame; a small green pulse 3 squares at the chest growing and shrinking.
Layout: one horizontal row of 4 equal 26:30 cells, image size 1664x480 (each cell 416x480, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `urgot_fx_r_reel.png`：R：被拽回来（目标身上），4 帧

被拽向厄加特：目标身上一圈毒绿色的牵引光收紧，几道绿色光线往中间收（参考 Z_EnergyStreaksAdd）。**左右对称**，中间身体位置留空，要淡一点。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a TIGHTENING GREEN PULL round a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 18 squares wide and 30 tall stands in the middle, not drawn): toxic green streaks at both sides converging on the figure, a green ellipse at the waist shrinking from 22 to 14 squares wide over the frames, lime glints.
Layout: one horizontal row of 4 equal 24:32 cells, image size 1536x512 (each cell 384x512, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `urgot_fx_r_ex.png`：R：处决（目标身上），6 帧

处决：目标被拽进来碾碎，一团很大的毒绿色和深紫色的爆炸，中间一颗白色的爆闪，外面一圈紫黑色的冲击环（参考 R_flare-omnimax、Z_ExplosionFireGreen、R_ShockDistortion）。**左右对称**。约 34 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12) and a dread violet ramp (#F4E8FF, #C49BFF, #8A4FE0, #55279E, #2A1150).
Effect: an EXECUTION BURST on a unit, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares; 2 a toxic green explosion 22 squares with a white core; 3 the explosion 30 squares, a violet shockwave ring 34 squares round it; 4 the ring breaking into violet and green shards at mirrored places; 5 green smoke and violet motes; 6 fading motes.
Layout: one horizontal row of 6 equal square cells, image size 3456x576 (each cell 576x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `urgot_fx_r_fear.png`：R：处决后周围敌人恐惧的冲击波（他身边，跟随），6 帧

处决成功：他脚下一圈深紫色带毒绿色的恐惧冲击波（扁椭圆）向外推开，地上几缕紫色的雾往外飘（参考 R_ShockDistortion、Z_SoftClouds）。**左右对称**，只画地上的环和雾。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dread violet ramp (#F4E8FF, #C49BFF, #8A4FE0, #55279E, #2A1150) and a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a DREAD SHOCKWAVE on the ground round a wide figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a violet flash 14 squares on the ground; 2 a flat violet ellipse ring 36 wide and 12 tall with a bright lavender rim and green sparks; 3 the ring 60 wide; 4 the ring 84 wide, violet mist wisps drifting outward at mirrored places; 5-6 the ring and the mist fading.
Layout: one horizontal row of 6 equal 86:30 cells, image size 8256x480 (each cell 1376x480, 16 px a square); centered across, the ring's middle 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `urgot_fx_r_flee.png`：R：恐惧中（敌人头顶，跟随，循环），4 帧

被吓跑的敌人头顶：一个小小的深紫色骷髅幽火在晃，带一点绿光。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, smoke, sparks, acid or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dread violet ramp (#F4E8FF, #C49BFF, #8A4FE0, #55279E, #2A1150) and a toxic green ramp (#FFFFFF, #EFFFB0, #B6FF3B, #4FE01E, #1E9A1A, #0B4A12).
Effect: a TINY DREAD SKULL WISP above a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small violet skull 6 squares with two green eye dots, a lavender flame wisp 3 squares above it flickering, the skull bobbing a square up and down.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered across, the skull in the cell's lower half. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `urgot_fx_a_shot` | view_projectiles `league_urgot_a_shot`（朝飞行方向转，画成朝右飞；上下对称） | 12 × 6 |
| `urgot_fx_w_shot` | view_projectiles `league_urgot_w_shot`（朝飞行方向转，画成朝右飞；上下对称） | 8 × 3 |
| `urgot_fx_p_fan` | view_projectiles `league_urgot_p_fan`（扇形那条线的画面：朝目标方向转，画成朝右；上下对称；大图表） | 52 × 24 |
| `urgot_fx_a_hit` | view_effects `league_urgot_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `urgot_fx_w_hit` | view_effects `league_urgot_w_hit`（跟随，画在人物上面；左右对称） | 6 |
| `urgot_fx_p_hit` | view_effects `league_urgot_p_hit`（跟随，画在人物上面；左右对称） | 14 |
| `urgot_fx_w_on` | view_buffs `league_urgot_w_on`（跟随，画在他下面；左右对称） | 48 × 12 |
| `urgot_fx_q_charge` | view_projectiles `league_urgot_q_charge`（抛物线飞行；上下左右都对称） | 8 × 8 |
| `urgot_fx_q_mark` | view_effects `league_urgot_q_mark`（电荷飞行时画在落点，不跟随，画在人物下面；左右对称） | 42 × 14 |
| `urgot_fx_q_blast` | view_effects `league_urgot_q_blast`（画在落点，不跟随；左右对称；大图表） | 44 × 30 |
| `urgot_fx_q_hit` | view_effects `league_urgot_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `urgot_fx_q_slow` | view_buffs `league_urgot_q_slow`（跟随，画在人物下面；左右对称） | 20 × 6 |
| `urgot_fx_e_shield` | view_effects `league_urgot_e_shield`（跟随，画在他身上；左右对称） | 56 × 50 |
| `urgot_fx_e_hit` | view_effects `league_urgot_e_hit`（跟随，画在人物上面；左右对称） | 18 |
| `urgot_fx_e_fling` | view_effects `league_urgot_e_fling`（跟随，画在人物上面；左右对称） | 26 × 14 |
| `urgot_fx_r_drill` | view_projectiles `league_urgot_r_drill`（朝飞行方向转，画成朝右飞；上下对称） | 18 × 8 |
| `urgot_fx_r_hit` | view_effects `league_urgot_r_hit`（跟随，画在人物上面；左右对称） | 18 |
| `urgot_fx_r_leash` | view_buffs `league_urgot_r_leash`（跟随，画在人物上面；左右对称） | 26 × 30 |
| `urgot_fx_r_reel` | view_effects `league_urgot_r_reel`（跟随，画在人物上面；左右对称） | 22 × 30 |
| `urgot_fx_r_ex` | view_effects `league_urgot_r_ex`（跟随，画在人物上面；左右对称；大图表） | 34 |
| `urgot_fx_r_fear` | view_effects `league_urgot_r_fear`（跟随，画在他下面；左右对称；大图表） | 84 × 30 |
| `urgot_fx_r_flee` | view_buffs `league_urgot_r_flee`（跟随，画在人物上面；左右对称） | 10 × 10 |

- 两张表：`asset/league/effects/league_urgot_fx`（小的）和 `league_urgot_big`（p_fan、q_blast、r_ex、r_fear），tag = 名字（build_urgot.py 的 views）。
- `a_shot`、`w_shot`、`p_fan`、`q_charge`、`r_drill` 是投射物，画面朝方向转；`q_mark`、`q_blast` 不跟随；`q_mark`、`r_fear`、`q_slow`、`w_on` 画在人物下面（z -1）；`q_blast` 前 3 帧（引信）要盖满 q_apply 的 0.2 秒。
- 用 `pixel_1x/` 切格（import_kalista_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
