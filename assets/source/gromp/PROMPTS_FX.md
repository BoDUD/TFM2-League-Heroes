# 魔沼蛙：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图 + 3 个技能图标。** 造型已定，见 `design/gromp_design.png`：
>   - 3/4 朝右、蹲着的**大胖蛤蟆**；
>   - 前面一个又圆又鼓的**橄榄褐大肚子**，橙色的扁头压在上面；
>   - **发黄绿色光的眼睛**、两根淡黄獠牙；
>   - 深紫色疙瘩皮，背上一丛紫色和蓝色的大蘑菇。
>
> 魔沼蛙在游戏里是**高清**的（每个游戏格子里约 1.69×1.69 个细像素），32 格高、62 格宽（高×宽）。**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/gromp_size.png`：魔沼蛙缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是大嘴（水花、地上的水洼、毒雾）、扎克（黏液）、卡西奥佩娅（毒圈）和冲击波的特效贴图。这些是**灰色的形状，游戏里再染色**，已经按用在我们哪张特效分好了行。只在本地用。
> - **魔沼蛙是峡谷里的大蛤蟆，特效都是它的味道**：湿乎乎的口水和黏液、圆滚滚带高光的毒泡泡、像它眼睛一样的**黄绿色毒**、**沼泽紫**的毒雾和孢子、橄榄色的黏液。不要闪电、不要光滑的霓虹光束；只有紫霸符那一个符文。
> - **特效要亮**：每个光都有最亮一档或近白的芯，暗底上一眼能看见。**光、雾、水花没有黑描边**。
> - **围着它的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住它。
> - **对称**：飞行的三张（a_spit、q_bubble、e_glob）**上下对称、朝右**（游戏按飞行方向转）；其余所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 交付方式：
>   - 每张生成后按格子取回（每格取多数颜色）。
>   - 交付 8 倍的 `gromp_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。
>   - 图标交付 `gromp_icon_<名字>.png`（64×64）。
>   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。
>   - 都放在 `outputs/gromp_fx/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/gromp_fx_pack_done.zip`。
>   - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「毒涎吐射」 | 远程吐毒口水 | `a_spit` · `a_hit` |
| 被动「紫霸符」 | 战斗里每 4 秒叠一层法强，有上限 | `p_ap` |
| 技能 1 =「打嗝泡泡」 | 吐一个毒泡泡，碰到第一个敌人炸开，周围一圈中毒 | `q_bubble` · `q_hit` · `q_burst` · `q_poison` |
| 技能 2 =「黏液沼泽」 | 往敌人脚下吐一滩黏液，站进去大幅减速 | `e_glob` · `e_land` · `e_pool` · `e_slow` |
| 大招 =「毒沼大嗝」 | 仰头鼓肚子变大，打一个大嗝：前方扇形毒雾伤害减速，毒雾留在地上 | `r_cast` · `r_hit` · `r_fog` · `r_slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、水花没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 毒绿（眼睛、毒、泡泡）：`#F6FFC8`、`#D2F55E`、`#8ED13A`、`#4C9A2C`、`#22521C`；
  - 沼泽紫（皮肤、毒雾、紫霸符）：`#EBD2FF`、`#B884EE`、`#8048BE`、`#4E267C`、`#261240`；
  - 黏液橄榄（肚子、黏液）：`#F4F0C4`、`#CFC67E`、`#968E4C`、`#5E5832`、`#302C1A`；
- 打中的画面居中画，不旋转；地面上的水花、水洼、毒雾是从斜上方看的扁平一团。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `gromp_fx_a_spit.png`：普攻「毒涎吐射」：飞出去的毒口水，4 帧循环

一团**黄绿色的毒口水**往右飞：前头圆、后面拖两三滴小水珠，中间一点近白的高光。**上下对称、朝右**，4 帧循环（水团微微抖动）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C), an olive slime ramp (#F4F0C4, #CFC67E, #968E4C, #5E5832, #302C1A).
Effect: A FLYING GOB OF SPIT, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a round wet toxic yellow-green GOB 5 squares across at the right with a near-white highlight square, two or three small droplets trailing behind it to the left in a line along the middle; frames 1-4 the gob wobbling (round, a little squashed, round, a little stretched) and the droplets trailing. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 12:6 cells, image size 768x96 (each cell 192x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `gromp_fx_q_bubble.png`：技能 1「打嗝泡泡」：飞出去的毒泡泡，4 帧循环

一个**圆滚滚的毒泡泡**往右飞：泡泡壁是亮黄绿色的一圈，里面一团紫色的毒雾在转，前缘正中一块近白的高光，后面拖两个小泡泡。**上下对称、朝右**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C), a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240).
Effect: A FLYING POISON BUBBLE, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a round BUBBLE 10 squares across at the right, its skin a ring of bright toxic yellow-green, its inside dark green with a swirl of SWAMP PURPLE poison turning in it, a near-white highlight on the bubble's front edge (on the middle line, so it stays symmetric), two tiny bubbles trailing behind it to the left; frames 1-4 the purple swirl turning and the bubble wobbling slightly. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `gromp_fx_e_glob.png`：技能 2「黏液沼泽」：飞出去的一团黏液，4 帧循环

一大团**橄榄色的黏液**往右飞：黏糊糊的一坨，前面圆、后面拉出黏丝，表面几个黄绿色的小气泡。**上下对称、朝右**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive slime ramp (#F4F0C4, #CFC67E, #968E4C, #5E5832, #302C1A), a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C).
Effect: A FLYING GLOB OF SLIME, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a big sticky OLIVE SLIME GLOB 7 squares across at the right, two stringy slime strands stretching back to the left, a few small toxic yellow-green bubbles on its surface; frames 1-4 the glob wobbling and the strands stretching. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `gromp_fx_a_hit.png`：普攻：毒口水溅开，4 帧

口水打中：**一团黄绿色的水花溅开**，四周飞出几滴小水珠。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C), an olive slime ramp (#F4F0C4, #CFC67E, #968E4C, #5E5832, #302C1A).
Effect: A SPIT SPLAT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a round yellow-green gob 5 squares across with a near-white core; 2 it splatting flat into a star-shaped splash 10 squares across; 3 four droplets flying out (two to each side, mirrored), the splash thinning; 4 the droplets falling, a small olive stain. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `gromp_fx_q_hit.png`：技能 1：泡泡砸中，5 帧

毒泡泡砸在第一个敌人身上：**泡泡一下撑大、啪地破开**，黄绿色的泡泡壁碎成一圈小水珠，中间冒出一团紫色毒雾。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C), a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240).
Effect: A BUBBLE POPPING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a round bubble 10 squares across, yellow-green skin, purple swirl inside; 2 it swelling to 14 squares, the skin stretched thin; 3 POP: the skin bursting into a ring of yellow-green droplets, a puff of swamp purple poison in the middle; 4 the droplets flying out, the purple puff spreading; 5 the last droplets and a fading purple wisp. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `gromp_fx_q_burst.png`：技能 1：泡泡炸开的毒圈，6 帧

泡泡停下的地方炸开（半径约 25 格内的敌人中毒）：**一圈紫绿色的毒雾往外推开**，地上溅出一圈黄绿色的毒液水花，几个小毒泡泡往上飘。从斜上方看，扁一点。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C), a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240).
Effect: A POISON BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): seen from above at a slant, centred on the bottom middle: 1 a bright yellow-green flash 8 squares across; 2 a flat RING of swamp purple and toxic green poison mist pushing out, 30 squares wide and 12 tall, yellow-green splash droplets thrown up round its edge; 3 the ring 46 squares wide, several small poison bubbles rising out of it; 4 the mist thinning, the bubbles higher; 5 the bubbles popping; 6 the last purple wisps low on the ground. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 50:30 cells, image size 4800x480 (each cell 800x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `gromp_fx_e_land.png`：技能 2：黏液落地溅开，5 帧

黏液团砸到地上：**啪地摊开成一大滩**，四周溅起几团黏液，往两边甩出黏丝。从斜上方看。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive slime ramp (#F4F0C4, #CFC67E, #968E4C, #5E5832, #302C1A), a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C).
Effect: A SLIME SPLASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND seen from above at a slant: 1 a glob of olive slime 8 squares across hitting the bottom middle; 2 it splashing flat, 30 squares wide, thick blobs flying up on both sides (mirrored); 3 the puddle spreading to 50 squares wide and 12 tall, sticky strands flung out and falling; 4 the blobs landing round the edge; 5 the puddle settled, a few yellow-green bubbles on it. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 5 equal 52:20 cells, image size 4160x320 (each cell 832x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `gromp_fx_e_pool.png`：技能 2：地上的黏液沼泽，6 帧循环

地上躺着的一大滩**黏液沼泽**（站进去的敌人被大幅减速）：椭圆形的橄榄色黏液，边缘深、中间亮，表面不停地冒出黄绿色小气泡、啵地破掉。从斜上方看。**左右对称**，6 帧循环（首尾接得上）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive slime ramp (#F4F0C4, #CFC67E, #968E4C, #5E5832, #302C1A), a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C).
Effect: A SLIME SWAMP, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND seen from above at a slant: a flat OVAL PUDDLE of sticky olive slime 50 squares wide and 14 tall, darker at the rim and lighter in the middle, a glossy highlight streak; frames 1-6 small toxic yellow-green bubbles rising, swelling and popping on its surface in turn (placed mirrored), the last frame running back into the first. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 52:18 cells, image size 4992x288 (each cell 832x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `gromp_fx_r_cast.png`：大招「毒沼大嗝」：打嗝的冲击，6 帧

它仰头打出大嗝的一下：**围着它的身子炸开一圈黄绿色的冲击波**，紫色的毒孢子往四周喷出去。**它的身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C), a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240).
Effect: A BIG BELCH SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the toad sits in the middle, not drawn: about 62 squares wide and 32 tall, a squat fat toad, its round belly and flat head at the right, the mushrooms on its back at the upper left, its feet on the bottom line of the cell: 1 a few yellow-green flecks at the top of its outline; 2 a flat oval SHOCKWAVE RING of toxic yellow-green bursting out round its body at mid height, 70 squares wide; 3 the ring at the cell's width, swamp purple poison SPORES spraying out from it to both sides (mirrored); 4 the ring breaking into arcs, the spores drifting; 5 the arcs fading, purple puffs hanging; 6 the last spores. The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 84:44 cells, image size 8064x704 (each cell 1344x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `gromp_fx_r_hit.png`：大招：毒雾喷中，5 帧

大嗝喷中：**一团紫绿色的毒雾糊在身上**，溅出几点黄绿色的毒液，两个小泡泡冒出来破掉。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C), a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240).
Effect: A POISON BLAST HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a yellow-green flash 6 squares across; 2 a cloud of swamp purple and toxic green poison 14 squares across puffing out, yellow-green droplets to both sides (mirrored); 3 the cloud rolling, two small bubbles rising in it; 4 the bubbles popping, the cloud thinning; 5 the last purple wisps. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 5 equal 18:16 cells, image size 1440x256 (each cell 288x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `gromp_fx_r_fog.png`：大招：留在地上的毒雾，6 帧循环

大嗝喷出去后留在地上的**一大片毒雾**（站在里面持续掉血）：低低的紫绿色雾团一团一团地翻滚，里面飘着黄绿色的毒孢子和小泡泡。从斜上方看，下面浓、上面淡。**左右对称**，6 帧循环（首尾接得上）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240), a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C).
Effect: A LINGERING POISON CLOUD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a low wide cloud of rolling swamp purple and toxic green MIST lumps, 60 squares wide, thick near the ground and thinning upward to 36 squares high, toxic yellow-green SPORES and small bubbles drifting up through it; frames 1-6 the lumps rolling and the spores rising (placed mirrored), the last frame running back into the first. Soft-edged lumps but still blocky pixel art. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 64:40 cells, image size 6144x640 (each cell 1024x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `gromp_fx_p_ap.png`：被动「紫霸符」：叠法强的紫色符文，6 帧循环

紫霸符（战斗里每 4 秒叠一层法强）：它**背上方飘着一个紫色的发光符文**（像峡谷 buff 那样的一圈，但是紫色），慢慢转，周围几点紫色小火星往上飘。**它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240).
Effect: PURPLE BUFF, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the toad sits in the middle, not drawn: about 62 squares wide and 32 tall, a squat fat toad, its round belly and flat head at the right, the mushrooms on its back at the upper left, its feet on the bottom line of the cell: above its back, in the top middle of the cell, a glowing SWAMP PURPLE RUNE 14 squares across (a ring with four short spikes, like a jungle buff's crest, seen slightly from above), near-white at its core; a few small purple sparks rising round its body's outline; frames 1-6 the rune slowly turning (its spikes stepping round, every frame left-right symmetric) and pulsing, the sparks drifting up. The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 70:50 cells, image size 6720x800 (each cell 1120x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `gromp_fx_q_poison.png`：技能 1：中毒的敌人身上冒泡，6 帧循环

中了打嗝泡泡的毒：**身子两边冒出黄绿色的小毒泡泡**一个个往上飘、破掉，头顶一缕紫色毒烟。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C), a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240).
Effect: POISONED, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round a champion 16 squares wide and 36 tall stands in the middle, not drawn, its feet on the bottom line of the cell: small toxic yellow-green BUBBLES (1x1 to 3x3 squares, each with a near-white highlight) rising along both sides of its outline (mirrored) and popping near the top, a thin swamp purple wisp above its head; frames 1-6 the bubbles rising and popping in turn. The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:40 cells, image size 1920x640 (each cell 320x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `gromp_fx_e_slow.png`：技能 2：被黏住减速，6 帧循环

陷在黏液里：**脚下一圈黏糊糊的橄榄色黏液**，两边拉起几根黏丝粘在脚上，偶尔冒个泡。**只在脚下**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive slime ramp (#F4F0C4, #CFC67E, #968E4C, #5E5832, #302C1A), a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C).
Effect: STUCK IN SLIME, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): at the bottom of the cell round a unit's feet (the feet 8 squares apart in the middle, not drawn): a flat oval of sticky olive slime 22 squares wide and 4 tall, slime strings stretching up 4 squares on both sides (mirrored) as if clinging to the feet, one small yellow-green bubble; frames 1-6 the strings stretching and sagging, the bubble rising and popping. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:10 cells, image size 2304x160 (each cell 384x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `gromp_fx_r_slow.png`：大招：毒雾减速，6 帧循环

被大嗝的毒雾喷中减速：**身子周围缠着几缕紫绿色的毒雾**慢慢绕圈，飘着几点黄绿色的孢子。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a swamp purple ramp (#EBD2FF, #B884EE, #8048BE, #4E267C, #261240), a toxic yellow-green ramp (#F6FFC8, #D2F55E, #8ED13A, #4C9A2C, #22521C).
Effect: CHOKED BY POISON, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round a unit standing in the middle (16 squares wide, its lower body in this cell, not drawn): two thin wisps of swamp purple and toxic green mist curling round its legs and waist on both sides (mirrored), a few yellow-green spores floating; frames 1-6 the wisps curling round and the spores drifting. The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT SWAMP TOAD's: wet gobs of SPIT and SLIME, round wobbly POISON BUBBLES with a bright highlight, TOXIC YELLOW-GREEN like its eyes, SWAMP PURPLE swirls and spores, olive slime; flat shades, crisp blocky shapes; no magic runes (except Purple Buff's one), no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `gromp_icon_skill.png`：技能 1「打嗝泡泡」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive frame with little yellow-green corner studs, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: an orange-headed toad's wide open mouth at the lower left belching a big round toxic yellow-green BUBBLE with a purple swirl inside toward the upper right, small bubbles trailing. No text, no letters.
```

### 图标 2. `gromp_icon_skill2.png`：技能 2「黏液沼泽」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive frame with little yellow-green corner studs, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big splash of sticky olive slime spread on the ground, slime strings and yellow-green bubbles, a small footprint stuck in it. No text, no letters.
```

### 图标 3. `gromp_icon_ult.png`：大招「毒沼大嗝」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive frame with little yellow-green corner studs, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge fat toad with an olive belly blown up round and a flat orange head with glowing yellow-green eyes, mouth wide open, a wave of purple-green poison mist bursting out of it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `gromp_fx_a_spit` | view_projectiles `tft_gromp_a_spit`（追踪弹道，随飞行方向转；上下对称、朝右） | 12 × 6 |
| `gromp_fx_q_bubble` | view_projectiles `tft_gromp_q_bubble`（直线弹道，随飞行方向转；上下对称、朝右） | 14 × 12 |
| `gromp_fx_e_glob` | view_projectiles `tft_gromp_e_glob`（抛物线弹道，随飞行方向转；上下对称、朝右） | 12 × 8 |
| `gromp_fx_a_hit` | view_effects `tft_gromp_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `gromp_fx_q_hit` | view_effects `tft_gromp_q_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `gromp_fx_q_burst` | view_effects `tft_gromp_q_burst`（大表，放在泡泡停下的地方，不跟随，z 2；左右对称） | 50 × 30 |
| `gromp_fx_e_land` | view_effects `tft_gromp_e_land`（大表，放在落点的地面上，不跟随，z -1；左右对称） | 52 × 20 |
| `gromp_fx_e_pool` | view_effects `tft_gromp_e_pool`（大表，放在地面上，不跟随，z -2，每 0.25 秒重放一次；左右对称） | 52 × 18 |
| `gromp_fx_r_cast` | view_effects `tft_gromp_r_cast`（大表，跟随它，z 3；左右对称） | 84 × 44 |
| `gromp_fx_r_hit` | view_effects `tft_gromp_r_hit`（跟随目标，z 2；左右对称） | 18 × 16 |
| `gromp_fx_r_fog` | view_effects `tft_gromp_r_fog`（大表，放在瞄准的地方，不跟随，z 3，每 0.25 秒重放一次；左右对称） | 64 × 40 |
| `gromp_fx_p_ap` | view_buffs `tft_gromp_p_ap`（跟随它，z 3；左右对称） | 70 × 50 |
| `gromp_fx_q_poison` | view_buffs `tft_gromp_q_poison`（跟随中毒的人，z 3；左右对称） | 20 × 40 |
| `gromp_fx_e_slow` | view_buffs `tft_gromp_e_slow`（跟随被减速的人，z 3；左右对称） | 24 × 10 |
| `gromp_fx_r_slow` | view_buffs `tft_gromp_r_slow`（跟随被减速的人，z 3；左右对称） | 24 × 24 |
| `gromp_icon_skill` | skill_icons[0] `asset/tft/icons/tft_gromp_skill` | 64 × 64 |
| `gromp_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_gromp_skill2` | 64 × 64 |
| `gromp_icon_ult` | skill_icons[2] `asset/tft/icons/tft_gromp_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_gromp_fx`（小的）和 `tft_gromp_big`（q_burst、e_land、e_pool、r_cast、r_fog），tag = 名字。
- a_spit、q_bubble、e_glob 断言上下对称（朝右），其余断言左右对称。
- a_spit 是普攻的追踪弹道，q_bubble 是不穿透的直线弹道（停下时放 q_burst），e_glob 是抛物线；a_hit、q_hit、r_hit 在被打中的人身上；q_burst、e_land、e_pool、r_fog 放在地面上（不跟随）；r_cast 跟随它；p_ap 是 tft.dll 叠的法强 buff；q_poison、e_slow、r_slow 在敌人身上。
- 用 `pixel_1x/` 切格（import_raptor_fx 的做法，改成 import_gromp_fx）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
