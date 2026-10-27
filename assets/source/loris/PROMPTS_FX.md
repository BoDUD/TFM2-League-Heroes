# 洛里斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图 + 3 个技能图标。** 造型已定（`design/loris_design.png`：拿巨型塔盾的大胡子皮城执法官，蓝头巾、宝蓝镶铜边的盔甲，铜金色的巨盾上一颗青蓝宝石）。洛里斯在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），42 格高、26 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/loris_size.png`：洛里斯缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里洛里斯自己的特效贴图（**灰色的形状，游戏里再染色**：护盾、冲锋、撞击、冲击波、尘土），按用在我们哪张特效分好了行。只在本地用。
> - **洛里斯是皮尔特沃夫的神盾使，特效都是他的巨盾**：铜金色的金属、盾上宝石的**海克斯青蓝**、**蓝白色的六边形护盾**、盾砸地时的尘土和碎石，嘲讽是红色的愤怒标记；不要火焰，不要魔法符文，不要光滑的霓虹光束。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、护盾、冲击波、尘土没有黑描边**（徽章、星星、齿轮、装甲片这些实物可以有一圈深色描边）。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。他没有飞行道具，没有要朝向的画面。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `loris_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）；图标交付 `loris_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/loris_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/loris_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「神盾使」 | 每条命第一次掉到 75% 和 25% 血时各得一层最大生命的护盾 | `p_burst` · `p_shield` |
| 普攻 | 巨盾从身侧抡过来砸人 | `a_hit` |
| 技能 1 =「皮城争斗」 | 身上亮起护盾，举盾往前冲锋，撞到的敌人被击退、晕眩、受到魔法伤害 | `q_shield` · `q_dash` · `q_hit` · `q_stun` |
| 技能 2 =「盾卫」 | 冲到血量最低的队友身边把盾一立，两人都得护盾，之后 4 秒替他承受 30% 伤害 | `e_land` · `e_guard` |
| 大招 =「钢铁防线」 | 把巨盾举过头顶砸进地里，冲击波击飞周围的敌人并嘲讽他们 2 秒，自己减伤 | `r_slam` · `r_hit` · `r_taunt` · `r_wall` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、护盾、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 铜金（盾、徽章、冲击环、图标边框）：`#FFF0C8`、`#F2C878`、`#D08C3C`、`#8E5420`、`#4A2810`；
  - 海克斯青蓝（盾上的宝石）：`#F2FFFF`、`#A8F6FF`、`#3ED8F0`、`#1A8CC0`、`#0A3E6A`；
  - 护盾蓝白：`#FFFFFF`、`#DCF2FF`、`#A0D2F8`、`#5A9AE0`、`#2C56A8`；
  - 嘲讽红：`#FFE4D8`、`#FF8A6A`、`#E8382C`、`#A01822`、`#4C0A10`；
  - 尘土：`#F0E2C8`、`#C8AE88`、`#9A7E5C`、`#64503A`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `loris_fx_a_hit.png`：普攻：盾击打中，4 帧

巨盾砸在人身上：一下白色的闪光，几块铜色的碎光往两边崩开，一小圈冲击环。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A HEAVY SHIELD BASH IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white star flash 8 squares across; 2 a short bronze shock ring 12 squares wide and 6 tall, bronze chips flying out to both sides (mirrored); 3 the ring thinner and wider, the chips farther, a little dust in the middle; 4 the last dust fading. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `loris_fx_q_shield.png`：皮城争斗：身上亮起护盾，6 帧

洛里斯放技能 1 时身上「嗡」地亮起一层**蓝白色的六边形护盾**：从胸前的一点光往外张开成一个包住全身的竖椭圆，六边形的格子一闪一闪地拼上去，最后只剩一圈淡淡的外轮廓。身体位置留空（只画外圈）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shield-barrier blue-white ramp (#FFFFFF, #DCF2FF, #A0D2F8, #5A9AE0, #2C56A8), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A), a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810).
Effect: A SHIELD BARRIER SNAPPING ON, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad man stands in the middle, not drawn: 22 squares wide and 42 tall: 1 a small cyan-white spark at his chest; 2 a ring of light bursting out from it; 3 a tall upright ellipse 30 squares wide and 50 tall around him, its edge made of pale blue-white HEXAGON tiles (each 3-4 squares), a few tiles bright; 4 the hexagon tiles lighting in a wave from the bottom to the top (mirrored); 5 the whole edge bright, a bronze glint at the top; 6 settling to a thin pale outline. Only the outer edge: the middle (the body) left empty. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 32:52 cells, image size 3072x832 (each cell 512x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `loris_fx_q_dash.png`：皮城争斗：冲锋起步踢起的尘土，5 帧

冲锋起步那一脚：地上「轰」地踢起一团尘土和碎石，往两边扩散开再落下。留在他起跑的地上（不跟着他），画成圆的，往哪边冲都能用。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A), a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810).
Effect: A CHARGE'S KICK-OFF DUST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a burst of dust 10 squares wide at the bottom middle, two small grit stones flung up to both sides (mirrored); 2 the dust spreading 20 squares wide and 8 tall, rolling puffs; 3 30 squares wide, the stones falling; 4 thinning; 5 the last thin puffs. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 5 equal 32:14 cells, image size 2560x224 (each cell 512x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `loris_fx_q_hit.png`：皮城争斗：冲锋撞中（击退 + 晕眩），5 帧

巨盾冲锋撞中：一下大大的白色闪光，铜色的盾形冲击波往两边炸开，青蓝色的电火花四溅，留一点尘土。比普攻更狠。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A SHIELD CHARGE SLAMMING INTO A UNIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white flash 12 squares across; 2 a bronze shock wave in the shape of the shield's outline (a tall shape 10 wide and 16 tall) bursting out, hextech cyan sparks flying out to both sides (mirrored); 3 a wide bronze shock ring 22 squares wide and 10 tall, the sparks farther; 4 the ring thin, dust puffs in the middle; 5 the dust fading. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 1920x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `loris_fx_q_stun.png`：皮城争斗：晕眩，6 帧循环

被撞晕的人：头顶上一圈**铜金色的小星星**和小齿轮绕着转。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A).
Effect: A STUNNED UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 10 squares of the cell) a flat ring of three small bronze-gold STARS and two tiny GEARS (each 3x3 squares) circling round, seen from the side (an ellipse 14 wide and 4 tall), a tiny cyan glint; frames 1-6 them moving round the ring (the ones in front brighter, mirrored positions). The rest of the cell empty. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 18:44 cells, image size 1728x704 (each cell 288x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `loris_fx_e_land.png`：盾卫：落到队友身边，两人得到护盾，6 帧

洛里斯冲到队友身边、把盾往地上一立：地上「咚」地一圈**铜色的冲击环**，接着一面**淡蓝白色的六边形护盾**从地面往上升，包住被守护的队友，最后变成一圈淡淡的光。身体位置留空。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a shield-barrier blue-white ramp (#FFFFFF, #DCF2FF, #A0D2F8, #5A9AE0, #2C56A8), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A).
Effect: A GUARD LANDING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a bronze impact flash on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 14 squares wide; 2 a bronze shock ring on the ground 30 squares wide and 8 tall, dust to both sides; 3 a pale blue-white wall of HEXAGON tiles rising from the ring around the unit, as high as its waist; 4 the hexagon wall reaching over its head, a bright cyan gem glint at the top; 5 the wall bright; 6 settling to a thin pale outline. Only the edges: the middle (the body) left empty. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 34:46 cells, image size 3264x736 (each cell 544x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `loris_fx_e_guard.png`：盾卫：被守护中（替他承受伤害），6 帧循环

被洛里斯守护的队友：头顶上方一枚小小的**铜金色盾牌徽章**（中间一点青蓝），脚下一圈淡淡的蓝色光圈，慢慢一明一暗。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A), a shield-barrier blue-white ramp (#FFFFFF, #DCF2FF, #A0D2F8, #5A9AE0, #2C56A8).
Effect: A GUARDED ALLY, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 9 squares of the cell) a small bronze TOWER SHIELD badge 6 squares wide and 8 tall with a cyan dot in its middle, and a faint pale blue ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 squares wide and 4 tall at the bottom; frames 1-6 the badge bobbing one square and glinting, the ring breathing. The middle (the body) left empty. Subtle. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:44 cells, image size 1920x704 (each cell 320x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `loris_fx_r_slam.png`：钢铁防线：巨盾砸地的冲击波，8 帧

大招：巨盾狠狠砸进地里，**地面炸开一圈很大的冲击波**（从中间往外推的铜色和青蓝色的环），地上裂开几道裂缝，尘土和碎石往四周飞，最后裂缝慢慢暗下去。这是画在**地上**的（从斜上方看的扁椭圆），中心在格子底部中间（他的脚下）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A GROUND SHOCKWAVE, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell (his feet): 1 a white-bronze flash 16 squares wide; 2 a thick bronze shock ring 36 squares wide and 12 tall with a hextech cyan inner edge, CRACKS (dark brown lines 1 square wide) starting out from the middle (mirrored); 3 the ring 56 wide and 18 tall, the cracks longer, dust and grit flung up to both sides; 4 the ring 76 wide and 26 tall, thinner; 5 the ring at the edge breaking into bright segments, dust billowing; 6 the dust settling, the cracks glowing cyan; 7 the cracks dimming; 8 faint cracks and thin dust. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 8 equal 84:30 cells, image size 10752x480 (each cell 1344x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `loris_fx_r_hit.png`：钢铁防线：被击飞，4 帧

被冲击波掀起来的人：脚下「砰」地一下铜色的闪光，尘土往上喷，两边几颗碎石。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A UNIT THROWN UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a bronze-white flash at the bottom middle 10 squares wide; 2 a jet of dust shooting upward 14 squares high, grit stones to both sides (mirrored); 3 the dust spreading and thinning; 4 the last puffs. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `loris_fx_r_taunt.png`：钢铁防线：被嘲讽（只能打他），6 帧循环

被嘲讽的人：头顶一个**红色的愤怒标记**（一个十字形的「青筋」符号），一跳一跳的，脚下一圈淡红色的光圈。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a taunt red ramp (#FFE4D8, #FF8A6A, #E8382C, #A01822, #4C0A10), a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810).
Effect: A TAUNTED UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 9 squares of the cell) a red ANGER MARK (the comic 'cross vein' symbol: four short curved red strokes in a cross, 7 squares across) with a bronze glint, and a faint red ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 14 squares wide and 4 tall at the bottom; frames 1-6 the mark throbbing bigger and smaller, the ring pulsing. The middle (the body) left empty. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 16:44 cells, image size 1536x704 (each cell 256x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `loris_fx_r_wall.png`：钢铁防线：钢铁之躯（减伤），6 帧循环

大招后洛里斯减伤：身体两侧各有两三块**铜色的六边形装甲片**慢慢上下浮动，边上带一点青蓝光；脚下一圈铜色的光圈。身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A).
Effect: AN IRON STANCE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad man stands in the middle, not drawn: 22 squares wide and 42 tall: at both sides of him (mirrored) three bronze HEXAGON ARMOUR PLATES (each 5 squares across, a cyan rim) floating at his shoulder, waist and knee height, and a bronze ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 26 squares wide and 6 tall at the bottom; frames 1-6 the plates bobbing up and down one square in turn, a glint running along them. The middle (the body) left empty. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 34:50 cells, image size 3264x800 (each cell 544x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `loris_fx_p_shield.png`：神盾使：护盾在身（跟着护盾一起消失），6 帧循环

神盾使给的护盾还在：他外面一层**很淡的蓝白色六边形护盾轮廓**（竖椭圆），上面偶尔有一两格六边形亮一下。不要太显眼。身体位置留空（只画外圈）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shield-barrier blue-white ramp (#FFFFFF, #DCF2FF, #A0D2F8, #5A9AE0, #2C56A8), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A).
Effect: A SHIELD BARRIER HOLDING, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad man stands in the middle, not drawn: 22 squares wide and 42 tall: a faint thin upright ellipse 28 squares wide and 48 tall around him, its edge a line of pale blue-white HEXAGON tiles; frames 1-6 one or two tiles at mirrored places lighting up brighter in turn, a soft glint running round. Subtle: thin, few squares. The middle (the body) left empty. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 30:50 cells, image size 2880x800 (each cell 480x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `loris_fx_p_burst.png`：神盾使：血量掉到 75% / 25% 时触发护盾，6 帧

神盾使触发：他身前「当」地一下亮出一枚**大大的铜金色盾牌徽章**（中间一颗青蓝宝石），徽章碎成光点散开，变成一圈蓝白色的六边形护盾包住他。身体位置留空（徽章只在前两帧挡一下胸口，之后散开）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A), a shield-barrier blue-white ramp (#FFFFFF, #DCF2FF, #A0D2F8, #5A9AE0, #2C56A8).
Effect: A WARDEN'S SHIELD BURSTING ON, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the broad man stands in the middle, not drawn: 22 squares wide and 42 tall: 1 a big bronze TOWER SHIELD EMBLEM 12 squares wide and 16 tall with a glowing cyan gem, flashing over his chest; 2 it rings bright white at the edges; 3 it shatters into bronze and cyan sparks flying out to both sides (mirrored); 4 the sparks join into a tall upright ellipse of pale blue-white HEXAGON tiles 32 wide and 50 tall around him; 5 the whole ellipse bright; 6 settling to a thin outline. After frame 2 the middle (the body) left empty. everything is a PILTOVER ENFORCER's GIANT TOWER SHIELD at work: solid bronze-gold metal, crisp hextech cyan energy from the gem on his shield, a pale blue-white shield barrier made of HEXAGON tiles, heavy dust and grit where the shield hits the ground; flat shades, crisp shapes; no fire, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 34:52 cells, image size 3264x832 (each cell 544x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `loris_icon_skill.png`：技能 1「皮城争斗」图标

一面铜金色的巨盾正面朝右前方猛冲过来，盾后面拖着几道速度线和尘土，盾边亮着蓝白色的护盾光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRONZE frame with little riveted corners, a deep navy-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big bronze TOWER SHIELD (navy panels, a cyan gem in a star emblem) charging forward toward the lower right, a pale blue-white barrier glow along its rim, bold speed lines and dust trailing behind it to the upper left. Colours: a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A), a shield-barrier blue-white ramp (#FFFFFF, #DCF2FF, #A0D2F8, #5A9AE0, #2C56A8). No text, no letters.
```

### 图标 2. `loris_icon_skill2.png`：技能 2「盾卫」图标

一面铜金色的巨盾立在前面，后面护着一个小小的蓝色人影，人影周围一圈六边形护盾光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRONZE frame with little riveted corners, a deep navy-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a bronze TOWER SHIELD standing upright in front at the right, behind it a small blue silhouette of an ally wrapped in a pale blue-white ring of HEXAGON tiles, a cyan glint on the shield's gem. Colours: a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a shield-barrier blue-white ramp (#FFFFFF, #DCF2FF, #A0D2F8, #5A9AE0, #2C56A8), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A). No text, no letters.
```

### 图标 3. `loris_icon_ult.png`：大招「钢铁防线」图标

巨盾的下沿狠狠砸进地里，地面炸开一圈铜色和青蓝色的冲击波，裂缝四散，碎石飞起。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRONZE frame with little riveted corners, a deep navy-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: the bottom edge of a bronze TOWER SHIELD slammed into the ground at the centre, a bronze-and-cyan SHOCKWAVE ring bursting out flat around it, cracks spreading through the ground, grit stones flying up. Colours: a bronze-gold ramp (#FFF0C8, #F2C878, #D08C3C, #8E5420, #4A2810), a hextech cyan ramp (#F2FFFF, #A8F6FF, #3ED8F0, #1A8CC0, #0A3E6A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `loris_fx_a_hit` | view_effects `tft_loris_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `loris_fx_q_shield` | view_effects `tft_loris_q_shield`（跟随他，z 3；左右对称） | 32 × 52 |
| `loris_fx_q_dash` | view_effects `tft_loris_q_dash`（留在起跑的地上，z 1；左右对称） | 32 × 14 |
| `loris_fx_q_hit` | view_effects `tft_loris_q_hit`（跟随被撞的人，z 2；左右对称） | 24 × 24 |
| `loris_fx_q_stun` | view_buffs `tft_loris_q_stun`（跟随被晕的人，z 3；左右对称） | 18 × 44 |
| `loris_fx_e_land` | view_effects `tft_loris_e_land`（跟随被守护的队友，z 3；左右对称） | 34 × 46 |
| `loris_fx_e_guard` | view_buffs `tft_loris_e_guard`（跟随被守护的队友，z 3；左右对称） | 20 × 44 |
| `loris_fx_r_slam` | view_effects `tft_loris_r_slam`（大表，留在他脚下的地上，z -1；左右对称） | 84 × 30 |
| `loris_fx_r_hit` | view_effects `tft_loris_r_hit`（跟随被击飞的人，z 2；左右对称） | 18 × 20 |
| `loris_fx_r_taunt` | view_buffs `tft_loris_r_taunt`（跟随被嘲讽的人，z 4；左右对称） | 16 × 44 |
| `loris_fx_r_wall` | view_buffs `tft_loris_r_wall`（跟随他，z 3；左右对称） | 34 × 50 |
| `loris_fx_p_shield` | view_buffs `tft_loris_p_shield`（跟随他，z 3；左右对称） | 30 × 50 |
| `loris_fx_p_burst` | view_effects `tft_loris_p_burst`（跟随他，z 3；左右对称） | 34 × 52 |
| `loris_icon_skill` | skill_icons[0] `asset/tft/icons/tft_loris_skill` | 64 × 64 |
| `loris_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_loris_skill2` | 64 × 64 |
| `loris_icon_ult` | skill_icons[2] `asset/tft/icons/tft_loris_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_loris_fx`（小的）和 `tft_loris_big`（r_slam），tag = 名字。
- 全部断言左右对称。
- p_burst / e_land 由 tft.dll 在神盾使触发、盾卫落地时播；q_shield 在技能 1 出手时播。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
