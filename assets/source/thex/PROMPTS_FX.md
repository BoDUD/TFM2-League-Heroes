# 海克斯霸龙：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图 + 3 个技能图标。** 造型已定（`design/thex_design.png`：3/4 朝右、机械霸王龙：深藏青机身盖着铜色装甲、嵌着海克斯蓝色发光面板，背上一排蓝色水晶尖刺；铜色恐龙头盔、蓝色面罩、白眼红眶、钢灰紫大下颌和白色三角牙；近处的前爪是六管加特林，远处是机械爪；鸟腿、铜色三趾爪脚、长机械尾巴）。海克斯霸龙在游戏里是**高清**的（每个游戏格子里约 1.9×1.9 个细像素），40 格高、54 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/thex_size.png`：海克斯霸龙缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是海克斯霸龙自己（金铲铲的枪口火光、曳光、导弹、烟、激光、护盾）和维克托（激光、电弧）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **海克斯霸龙是皮尔特沃夫的海克斯机甲，特效都是它的味道**：奶白芯的**海克斯蓝**光、小六边形、加特林**黄橙色的枪口火光**、铜色金属碎片、灰色的烟；不要绿色、不要紫色魔法、不要树叶。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：除了飞行的子弹 `a_bullet` 和激光 `r_beam`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `thex_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `thex_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/thex_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/thex_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「驾驶员弹射」 | 阵亡时驾驶员被弹出，机甲爆开，把附近敌人击退并晕眩 | `p_blast` |
| 普攻「加特林弹幕」 | 每次攻击连射 4 颗子弹；每第四次攻击最后一颗多打一下（枪手） | `a_bullet` · `a_hit` · `a_crit` |
| 技能 1 =「追踪导弹」 | 背上导弹舱翻开，导弹落在附近的敌人身上 | `q_launch` · `q_fall` |
| 技能 2 =「霸龙冲撞」 | 冲向目标一口咬住：伤害、击退、减速 | `e_dash` · `e_hit` · `e_slow` |
| 大招 =「海克斯军械库」 | 获得护盾，导弹舱全开：每秒一道贯穿激光（每多穿一人伤害递减）+ 一串导弹落在附近的敌人身上 | `r_shield` · `r_beam` · `r_hit` · `q_fall` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 海克斯蓝（面板、激光、护盾）：`#F2FFFF`、`#A8F4FF`、`#4CCBFF`、`#1F82E6`、`#1B3E9E`；
  - 铜（装甲、导弹壳、碎片）：`#FFDBA4`、`#F5A24C`、`#C96B2A`、`#8A4320`、`#4E2618`；
  - 枪口火光、爆炸：`#FFFDE6`、`#FFE66E`、`#FFAD30`、`#E8621C`、`#9E3416`；
  - 烟和尘土：`#ECE9E2`、`#B4B0A8`、`#7A7670`、`#474440`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `thex_fx_a_bullet.png`：普攻「加特林弹幕」：飞行的子弹，2 帧循环

加特林射出的一颗子弹：**一道短短的亮黄白色曳光**（往右飞），后面拖着橙色的尾巴。**上下对称、朝右**，2 帧循环（尾巴长短交替）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a muzzle-fire ramp (#FFFDE6, #FFE66E, #FFAD30, #E8621C, #9E3416).
Effect: A GATLING TRACER ROUND, 2 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a small bright pale-yellow bullet head 2 squares tall in the right part of the cell, a straight yellow-orange tracer streak behind it to the left (6 squares in frame 1, 8 in frame 2), fading to orange at its tail. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 2 equal 10:4 cells, image size 320x64 (each cell 160x64, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `thex_fx_a_hit.png`：普攻「加特林弹幕」：子弹打中，3 帧

子弹打中：一个小小的黄白火花，几粒火星往两边溅开。**左右对称**，3 帧（每次攻击会连着打中 4 下，要小、要快）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a muzzle-fire ramp (#FFFDE6, #FFE66E, #FFAD30, #E8621C, #9E3416).
Effect: A SMALL BULLET IMPACT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a tiny pale-yellow flash 3 squares across with four short rays; 2 a yellow-orange spark burst 8 squares across, a few single sparks flying out to both sides (mirrored); 3 the last sparks falling outward, orange and dim. Small and quick. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `thex_fx_a_crit.png`：普攻：每第四下的强化子弹打中（枪手），4 帧

每第四次攻击的最后一颗子弹多打一下：**一圈海克斯蓝色的六边形冲击**炸开，中间奶白色的闪光，几块铜色碎片往两边飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E), a muzzle-fire ramp (#FFFDE6, #FFE66E, #FFAD30, #E8621C, #9E3416), a copper ramp (#FFDBA4, #F5A24C, #C96B2A, #8A4320, #4E2618).
Effect: A HEXTECH ROUND IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale white-blue flash 6 squares across; 2 a bright hextech-blue HEXAGON burst 14 squares across with a yellow core, short blue rays, two copper shards flying out (mirrored); 3 the hexagon ring 18 squares across and thinning, small blue sparks; 4 the last ring fragments and sparks. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 4 equal 20:18 cells, image size 1280x288 (each cell 320x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `thex_fx_q_launch.png`：技能 1「追踪导弹」：背上导弹舱发射，5 帧

导弹从它背上发射：**格子下半部是它的身体位置（留空）**，**上半部两枚小导弹冒着火光和白烟往上窜出去**（一左一右，对称），发射口一下橙色火光，烟往上拖。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a copper ramp (#FFDBA4, #F5A24C, #C96B2A, #8A4320, #4E2618), a muzzle-fire ramp (#FFFDE6, #FFE66E, #FFAD30, #E8621C, #9E3416), a smoke ramp (#ECE9E2, #B4B0A8, #7A7670, #474440), a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E).
Effect: MISSILES LAUNCHING UPWARD, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the lower half of the cell is the mech's body (not drawn, EMPTY); from the middle of the cell: 1 two orange muzzle flashes 5 squares across, side by side (mirrored); 2 two small copper missiles (3 squares wide, 7 tall, nose up, a blue light on each) leaving the flashes, short flame tails and grey smoke puffs under them; 3 the missiles halfway to the top, the smoke trails longer and spreading; 4 the missiles leaving the top of the cell, two tall smoke trails; 5 the smoke trails thinning. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 5 equal 40:44 cells, image size 3200x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `thex_fx_q_fall.png`：技能 1「追踪导弹」：导弹落下炸开，7 帧（大招的导弹也用这张）

导弹从天上落下来：**一枚铜色小导弹头朝下、从格子最上面直直落下来**（尾巴带着火光和一道白烟），砸在格子最下面的地上，**炸开一团橙黄色的火光、外圈一圈海克斯蓝的冲击、几块铜色碎片**，然后剩一团烟。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a copper ramp (#FFDBA4, #F5A24C, #C96B2A, #8A4320, #4E2618), a muzzle-fire ramp (#FFFDE6, #FFE66E, #FFAD30, #E8621C, #9E3416), a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E), a smoke ramp (#ECE9E2, #B4B0A8, #7A7670, #474440).
Effect: A FALLING MISSILE, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the bottom of the cell is the ground: 1 a small copper MISSILE nose down (4 squares wide, 9 tall, a blue light at its tail fins) at the very top of the cell, a short flame and smoke streak above it; 2 the missile a third of the way down, the smoke streak longer (straight up above it); 3 the missile two thirds down; 4 the missile hitting the ground at the bottom, a white-yellow flash; 5 a round yellow-orange BLAST 16 squares wide at the bottom, a thin hextech-blue ring round it, copper shards flying out low to both sides (mirrored); 6 the blast turning to a grey smoke cloud, the shards falling; 7 the last smoke. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 7 equal 24:52 cells, image size 2688x832 (each cell 384x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `thex_fx_e_dash.png`：技能 2「霸龙冲撞」：冲出去时脚下扬尘，5 帧

它蹬地冲出去：脚下**一圈尘土往两边低低地扬起**，几道蓝色的短速度线。**只在地面和低处**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a smoke ramp (#ECE9E2, #B4B0A8, #7A7670, #474440), a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E).
Effect: A DASH-OFF DUST BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND and low above it: 1 a short pale flash under the feet (an ellipse 14 squares wide); 2 grey dust puffs bursting out low to both sides (mirrored), two short hextech-blue speed streaks on each side; 3 the dust 32 squares wide, rolling; 4 the dust 38 squares wide and thinning; 5 the last dust. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 5 equal 40:12 cells, image size 3200x192 (each cell 640x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `thex_fx_e_hit.png`：技能 2「霸龙冲撞」：一口咬中，4 帧

一口咬中：**上下两排白色的三角牙印一下合拢**（像一张大嘴咬下去的形状），中间一下橙黄色的冲击闪光，几块铜色碎片和火星往两边飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a muzzle-fire ramp (#FFFDE6, #FFE66E, #FFAD30, #E8621C, #9E3416), a copper ramp (#FFDBA4, #F5A24C, #C96B2A, #8A4320, #4E2618), a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E).
Effect: A MECHANICAL BITE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of white triangle TEETH shapes, one row at the top of the cell pointing down and one at the bottom pointing up, wide apart (each row 16 squares wide, five teeth); 2 the two rows snapped together in the middle, a bright yellow-white impact flash between them, short hextech-blue rays; 3 the teeth fading, an orange spark burst 20 squares across, copper shards flying out to both sides (mirrored); 4 the last sparks. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 4 equal 24:22 cells, image size 1536x352 (each cell 384x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `thex_fx_e_slow.png`：技能 2「霸龙冲撞」：减速，6 帧循环

被减速的人：脚边**一圈噼啪作响的海克斯蓝色小电火花**和几块小铜碎片，像被机械咬伤的余电。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E), a copper ramp (#FFDBA4, #F5A24C, #C96B2A, #8A4320, #4E2618).
Effect: HEXTECH STATIC AT THE FEET, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): on EACH side (mirrored) two or three tiny crackling hextech-blue sparks (2-3 square zigzags) and one small copper chip by the ankle line; frames 1-6 the sparks jumping to new spots and flickering (every frame left-right symmetric). Subtle. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 6 equal 24:8 cells, image size 2304x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `thex_fx_r_beam.png`：大招「海克斯军械库」：激光，3 帧循环

大招每秒射出的激光：**一长条奶白芯、海克斯蓝色的光束**（往右射），边上噼啪的蓝色细电弧，最前端一个亮点。**上下对称、朝右**，3 帧循环（电弧位置轮换）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E).
Effect: A HEXTECH LASER BOLT, 3 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a long straight BEAM across the cell - a white core 2 squares thick, bright hextech blue round it (6 squares thick in all), its front end at the right a round bright head 8 squares across, the tail end at the left tapering off; thin blue crackling arcs along its top and bottom edges (mirrored); frames 1-3 the arcs moving along it and the core flickering a shade. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 3 equal 56:10 cells, image size 2688x160 (each cell 896x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `thex_fx_r_hit.png`：大招「海克斯军械库」：被激光烧到，4 帧

被激光打中的人：**一下海克斯蓝色的灼烧闪光**，几道蓝色小电弧往外跳，一缕白烟往上飘。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E), a smoke ramp (#ECE9E2, #B4B0A8, #7A7670, #474440).
Effect: A LASER BURN, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash 8 squares across; 2 a hextech-blue burst 16 squares across with a white core, four short crackling arcs jumping out (mirrored); 3 the burst fading to small blue embers, a thin grey smoke wisp rising from the middle; 4 the last embers and smoke. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `thex_fx_r_shield.png`：大招「海克斯军械库」：海克斯护盾，6 帧循环

大招的护盾：身子外面**一圈由小六边形拼成的海克斯蓝色护罩**（横着的椭圆，只画外圈：一圈蓝色六边形格子，边缘奶白），六边形一格一格轮流亮起来。**里面它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E).
Effect: A HEXTECH HEX SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the mech stands in the middle, not drawn: about 53 squares wide and 40 tall, crouched on two bird legs, its gatling in front, its tail behind, its helmeted head at the top right: a ring of small HEXAGON cells (an ellipse 60 squares wide and 46 tall, only its 3-square rim drawn, made of hexagons 4 squares across with thin bright edges), hextech blue with pale white edges along the outside; frames 1-6 a few hexagons lighting up white in turn round the ring (mirrored pairs) and a soft sweep of brighter blue climbing both sides (every frame left-right symmetric). INSIDE the ring stays EMPTY (its body). everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 6 equal 64:50 cells, image size 6144x800 (each cell 1024x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `thex_fx_p_blast.png`：被动「驾驶员弹射」：机甲爆开，7 帧

它被击倒时机甲爆开、把周围的人震飞：一下巨大的奶白闪光，**一团橙黄色的大火球爆开**，外面**一圈海克斯蓝的冲击环**贴着地面推开，铜色的装甲碎片和齿轮往两边飞，最后一团灰烟。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a muzzle-fire ramp (#FFFDE6, #FFE66E, #FFAD30, #E8621C, #9E3416), a hextech blue ramp (#F2FFFF, #A8F4FF, #4CCBFF, #1F82E6, #1B3E9E), a copper ramp (#FFDBA4, #F5A24C, #C96B2A, #8A4320, #4E2618), a smoke ramp (#ECE9E2, #B4B0A8, #7A7670, #474440).
Effect: A MECH EXPLOSION, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the bottom of the cell is the ground: 1 a big white-yellow flash 20 squares across at the middle bottom; 2 a round yellow-orange FIREBALL 34 squares across, a thick hextech-blue SHOCKWAVE RING bursting open on the ground round it (an ellipse 50 squares wide, 14 tall), copper armour plates and small gears flying out to both sides (mirrored); 3 the fireball 44 squares and turning orange, the ring 72 squares wide, the pieces flying higher; 4 the fireball breaking into grey smoke with orange inside, the ring at the cell's edge and thinning, the pieces falling; 5 a big grey smoke cloud, a few orange embers; 6 the smoke thinning, the pieces on the ground at the bottom corners; 7 the last smoke. everything is the firepower of a HEXTECH WAR MACHINE (a copper-armoured mechanical T-rex from Piltover): crisp HEXTECH BLUE light with white cores, small hexagon shapes, yellow-orange MUZZLE FIRE, copper metal shards, grey smoke puffs; flat shades, crisp blocky shapes; no green, no purple magic, no leaves.
Layout: one horizontal row of 7 equal 80:56 cells, image size 8960x896 (each cell 1280x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `thex_icon_skill.png`：技能 1「追踪导弹」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark copper frame with little blue hextech corners, a deep navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: three small copper missiles with blue-lit fins arcing up and over to the right, white smoke trails curving behind them, a small orange flame at each tail. No text, no letters.
```

### 图标 2. `thex_icon_skill2.png`：技能 2「霸龙冲撞」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark copper frame with little blue hextech corners, a deep navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a copper mechanical T-rex head with a blue visor charging to the right, its steel jaws wide open with white triangle teeth, hextech-blue speed lines behind it. No text, no letters.
```

### 图标 3. `thex_icon_ult.png`：大招「海克斯军械库」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark copper frame with little blue hextech corners, a deep navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a bright hextech-blue laser beam with a white core shooting to the right from the lower left, two small missiles rising beside it, a ring of small blue hexagons behind. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `thex_fx_a_bullet` | view_projectiles `tft_thex_a_bullet`（追踪弹道，随飞行方向旋转；上下对称、朝右） | 10 × 4 |
| `thex_fx_a_hit` | view_effects `tft_thex_a_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `thex_fx_a_crit` | view_effects `tft_thex_a_crit`（跟随目标，z 2；左右对称） | 20 × 18 |
| `thex_fx_q_launch` | view_effects `tft_thex_q_launch`（跟随海克斯霸龙，画在它身上，z 2；左右对称） | 40 × 44 |
| `thex_fx_q_fall` | view_effects `tft_thex_q_fall` 和 `tft_thex_r_fall`（大表，放在落点的地面上，不跟随，z 2；画面最下面是地面；左右对称） | 24 × 52 |
| `thex_fx_e_dash` | view_effects `tft_thex_e_dash`（放在它起步的地面上，不跟随，z -1；左右对称） | 40 × 12 |
| `thex_fx_e_hit` | view_effects `tft_thex_e_hit`（跟随目标，z 2；左右对称） | 24 × 22 |
| `thex_fx_e_slow` | view_buffs `tft_thex_e_slow`（跟随被减速的人，脚下，z 3；左右对称） | 24 × 8 |
| `thex_fx_r_beam` | view_projectiles `tft_thex_r_beam`（大表，直线弹道，从嘴里射出飞得很快，随飞行方向旋转；上下对称、朝右） | 56 × 10 |
| `thex_fx_r_hit` | view_effects `tft_thex_r_hit`（跟随目标，z 2；左右对称） | 20 × 20 |
| `thex_fx_r_shield` | view_buffs `tft_thex_r_shield`（大表，跟随海克斯霸龙，z 3；左右对称） | 64 × 50 |
| `thex_fx_p_blast` | view_effects `tft_thex_p_blast`（大表，放在它倒下的地方，不跟随，z 2；画面最下面是地面；左右对称） | 80 × 56 |
| `thex_icon_skill` | skill_icons[0] `asset/tft/icons/tft_thex_skill` | 64 × 64 |
| `thex_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_thex_skill2` | 64 × 64 |
| `thex_icon_ult` | skill_icons[2] `asset/tft/icons/tft_thex_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_thex_fx`（小的）和 `tft_thex_big`（q_fall、r_beam、r_shield、p_blast），tag = 名字。
- a_bullet、r_beam 断言上下对称（朝右），其余断言左右对称。
- e_dash 放在地面上（不跟随，z -1）；q_fall（= r_fall）、p_blast 放在落点（不跟随）；q_launch 跟随它；r_shield 是它身上的 buff；e_slow 是敌人身上的 buff；a_bullet 是追踪弹道，r_beam 是直线弹道（从嘴里射出）。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
