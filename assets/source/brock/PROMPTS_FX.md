# 岩宝：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图 + 3 个技能图标。** 造型已定（`design/brock_design.png`：3/4 朝右、深青灰板岩色的大块头岩石魔像：两只巨大的石拳垂在身体两侧；棕色树根缠满肩膀、手臂和腰；肩上亮绿叶丛和小盆景树；小头缩在两肩之间：灰蓝石兜帽、发光的橙色脸板、两只黄色圆环眼睛；胸口紫色三角水晶纹章）。岩宝在游戏里是**高清**的（每个游戏格子里约 1.16×1.16 个细像素），44 格高、60 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/brock_size.png`：岩宝缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是岩宝自己（金铲铲的碎石、尘土、冲击波）、熔岩巨兽（碎石、石盾）、奥恩（地面裂缝、冲击波、石刺）和艾翁（树根、叶子）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **岩宝是丛林里长满树根和叶子的岩石魔像，特效都是他的味道**：成块的青灰色碎石石板、地面上透着**暖琥珀橙色**光的裂缝、棕色树根、亮绿叶子、灰褐色的尘土；不要火焰、不要闪电、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：除了飞行的大石头 `q_rock`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `brock_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `brock_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/brock_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/brock_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「岩心不动」 | 不受控制效果影响 | （不用图） |
| 普攻「震地拳」 | 双拳举过头顶砸下，目标周围一小圈溅射；每第三下把目标短暂击飞 | `a_hit` · `a_quake` · `a_up` |
| 技能 1 =「巨岩投掷」 | 抡起一块大石头扔向目标：伤害并减速 | `q_rock` · `q_hit` · `q_slow` |
| 技能 2 =「苔藤缠握」 | 树根从最近的敌人脚下钻出把他定住，自己获得苔石护盾 | `e_vine` · `e_root` · `e_shield` |
| 大招 =「震地猛击」 | 高高跃起砸进敌群：范围伤害（离落点越远越低），第一次被砸中的敌人被击飞，随后天上落下一阵碎石 | `r_jump` · `r_slam` · `r_hit` · `r_rock` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 琥珀光（他的脸板、地缝里的光）：`#FFFBD0`、`#FBF82F`、`#FFC23A`、`#FB771C`、`#C4421C`；
  - 石头（他的青灰板岩）：`#B9D2D6`、`#8BB6BE`、`#63909B`、`#34586B`、`#1E3647`；
  - 树根：`#E0A262`、`#CD8544`、`#AB6A37`、`#814A29`、`#603521`；
  - 叶子和青苔：`#D8FF8A`、`#A1F75C`、`#5CD14A`、`#1D8C4E`、`#0D4A4E`；
  - 尘土：`#E2DACA`、`#B3A992`、`#7D7464`、`#4C473E`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `brock_fx_a_hit.png`：普攻「震地拳」：石拳砸中，4 帧

石拳砸中：一下琥珀色的闪光，几块青灰色的碎石和一团尘土往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C), a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A STONE FIST IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale amber-white flash 5 squares across; 2 a short burst of warm amber light with four stubby rays, 12 squares across, a few slate stone chips flying out to both sides (mirrored); 3 the chips falling outward, a low puff of grey-brown dust at the bottom; 4 the last dust and one falling chip on each side. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `brock_fx_a_quake.png`：普攻「震地拳」：周围一圈溅射的震波，5 帧

拳头砸地震出的一小圈震波（目标周围的溅射伤害）：地面上**一圈带短裂缝的震波环**往外推开（从斜上方看的椭圆，宽是高的 3 倍），裂缝透着琥珀色的光，几块碎石跳起来。**只在地面上**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C), a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A SMALL GROUND QUAKE RING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND only, seen from above at a slant: 1 a short amber flash in the middle, 8 squares wide; 2 a thin ring of short jagged cracks glowing amber (an ellipse 22 squares wide, 7 tall), a few stone chips jumping up along it; 3 the ring 34 squares wide, a little dust rolling out on both sides (mirrored); 4 the ring at 38 squares and fading, the chips falling; 5 a few dim cracks. The middle stays clear after frame 1. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 40:14 cells, image size 3200x224 (each cell 640x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `brock_fx_a_up.png`：普攻「震地拳」：第三下击飞，4 帧

每第三下普攻把目标击飞：目标**脚下地面一下拱起、几块碎石和尘土往上蹦**。只在脚下。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E), a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C).
Effect: A GROUND JOLT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low under a unit's feet only (the unit not drawn): 1 a short amber crack flash on the ground; 2 the ground bulging up in a low stone hump 12 squares wide, small chips and pebbles jumping up on both sides (mirrored), a puff of dust; 3 the pebbles at their highest, the dust spreading; 4 the pebbles falling, the last dust. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 4 equal 22:10 cells, image size 1408x160 (each cell 352x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `brock_fx_q_rock.png`：技能 1「巨岩投掷」：飞行的大石头，4 帧循环

他扔出去的大石头：**一块圆滚滚、缠着两道树根的青灰色大石头**在翻滚着飞（往右飞），后面拖着一小股尘土和两三块小碎石。**上下对称、朝右**，4 帧循环（翻滚靠石头上的高光和裂纹位置轮换来表现）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a root-brown ramp (#E0A262, #CD8544, #AB6A37, #814A29, #603521), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A FLYING BOULDER, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a ROUND slate-teal BOULDER 11 squares across in the right part of the cell, two brown ROOT bands wrapped round it (mirrored top and bottom), a few dark cracks; behind it on the left a short trail of grey-brown dust and two small chips (one above, one below, mirrored); frames 1-4 the boulder tumbling - its light patches and cracks shifting round it in turn (every frame top-bottom symmetric). everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 4 equal 20:14 cells, image size 1280x224 (each cell 320x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `brock_fx_q_hit.png`：技能 1「巨岩投掷」：石头砸中碎开，5 帧

大石头砸中：一下琥珀色的闪光，**石头碎成好几大块往两边崩开**，一团尘土炸开，几段断掉的树根飞出去。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C), a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a root-brown ramp (#E0A262, #CD8544, #AB6A37, #814A29, #603521), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: A BOULDER SMASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a bright amber-white flash 8 squares across in the middle; 2 the boulder bursting: five or six big slate stone chunks flying out to both sides (mirrored), a ring of grey-brown dust, two short broken root pieces spinning out; 3 the chunks further out and falling, the dust cloud 26 squares wide; 4 the chunks on the ground at the bottom corners, the dust thinning; 5 the last dust. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 30:22 cells, image size 2400x352 (each cell 480x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `brock_fx_q_slow.png`：技能 1「巨岩投掷」：减速，6 帧循环

被减速的人：脚边**几块碎石和一层尘土压着脚**，像被碎石绊住。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: RUBBLE AT THE FEET, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): on EACH side (mirrored) two or three small slate stone chunks and pebbles lying against the ankle line, a faint low dust haze between them; frames 1-6 the pebbles shifting a square and the dust drifting (every frame left-right symmetric). Subtle. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:8 cells, image size 2304x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `brock_fx_e_vine.png`：技能 2「苔藤缠握」：树根破土而出，6 帧

树根从目标脚下的地里钻出来：地面一下裂开透出琥珀光，**四五根粗壮的棕色树根从两边破土冲上来、往中间弯过来卷住**，带着几片绿叶和泥土碎块。**中间人站的地方（身体）留空**，树根只到腰。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a root-brown ramp (#E0A262, #CD8544, #AB6A37, #814A29, #603521), a leaf-green ramp (#D8FF8A, #A1F75C, #5CD14A, #1D8C4E, #0D4A4E), a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: ROOTS BURSTING FROM THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn (only its lower half matters): 1 an amber crack opening on the ground under its feet (an ellipse 20 squares wide, 6 tall); 2 the tips of four thick BROWN ROOTS breaking out of the ground, two on each side (mirrored), clods of earth jumping; 3 the roots shooting up 14 squares, curling inward toward the middle; 4 the roots at their tallest (up to the waist, 18 squares) hooking over, a few green leaves on them; 5 the roots settling into a cage round the legs; 6 the roots still, the crack's glow gone. The middle above the knees stays EMPTY. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal square cells, image size 2880x480 (each cell 480x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `brock_fx_e_root.png`：技能 2「苔藤缠握」：被树根定住，6 帧循环

被定身的人：**几道棕色树根缠在小腿和脚踝上**（两边各两道，往中间绕），根上冒出两三片绿叶，一点点琥珀光在根缝里闪。只缠在腿上，上身留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a root-brown ramp (#E0A262, #CD8544, #AB6A37, #814A29, #603521), a leaf-green ramp (#D8FF8A, #A1F75C, #5CD14A, #1D8C4E, #0D4A4E), a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C).
Effect: ROOTS BINDING THE LEGS, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's legs only (the unit not drawn, the cell's bottom is its soles): on EACH side (mirrored) two thick brown roots coming out of the ground and winding inward round the shins up to 12 squares high, two small green leaves sprouting on them, a few amber glints in the root cracks; frames 1-6 the roots tightening a square and loosening, the glints moving, the leaves trembling (every frame left-right symmetric). everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:16 cells, image size 2304x256 (each cell 384x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `brock_fx_e_shield.png`：技能 2「苔藤缠握」：苔石护盾，6 帧循环

他自己的护盾：身子外面**一圈长满青苔和小叶子的石板**围成的护壳（竖着的椭圆，只画外圈：一块块青灰石板，石板上铺着绿苔，石缝里透着琥珀光），叶子一闪一闪轻轻摇。**里面他的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a leaf-green ramp (#D8FF8A, #A1F75C, #5CD14A, #1D8C4E, #0D4A4E), a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C).
Effect: A MOSSY STONE SHELL, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the golem stands in the middle, not drawn: about 59 squares wide and 44 tall, upright, his two huge stone fists hanging wide at his sides, his small hooded head in the middle of the top: a ring of STONE PLATES (an upright ellipse 68 squares wide and 50 tall, only its 3-square rim drawn, made of ten slate-teal stone slabs with dark seams), bright green MOSS and small leaves growing on the slabs, a thin warm amber light line in the seams and along the inner edge; frames 1-6 the amber seams lighting up in turn round the ring (mirrored pairs) and the leaves swaying a square (every frame left-right symmetric). INSIDE the ring stays EMPTY (his body). everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 72:54 cells, image size 6912x864 (each cell 1152x864, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `brock_fx_r_jump.png`：大招「震地猛击」：起跳，5 帧

他蹬地跳起：脚下地面**一下崩出一圈尘土和碎石**，地面裂开几道琥珀色的短缝。**只在地面和低处**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E), a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C).
Effect: A LAUNCH BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND and low above it: 1 a short amber crack flash under the feet (an ellipse 24 squares wide); 2 a puff of grey-brown dust bursting out low to both sides (mirrored), stone chips and pebbles jumping up, three short amber cracks on the ground; 3 the dust rolling out 50 squares wide, the chips at their highest; 4 the dust 58 squares wide and thinning, the chips falling; 5 the last dust, the cracks dim. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 60:16 cells, image size 4800x256 (each cell 960x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `brock_fx_r_slam.png`：大招「震地猛击」：落地猛砸，6 帧

他从空中砸进地面：一下巨大的琥珀色闪光，地面上**一个很大的震波环**炸开，大块的石板翘起、碎石和尘土往两边飞，地上留下一圈透着琥珀光的裂缝，几片绿叶被震飞。**只在地面和低处**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C), a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E), a leaf-green ramp (#D8FF8A, #A1F75C, #5CD14A, #1D8C4E, #0D4A4E).
Effect: A HUGE EARTH SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND and low above it, seen from above at a slant: 1 a big amber-white flash at the middle bottom, 22 squares wide, short rays; 2 a thick bright amber SHOCKWAVE RING bursting open on the ground (an ellipse 56 squares wide, 18 tall, 3 squares thick), big slate STONE SLABS tilting up out of the ground on both sides (mirrored), chips and a few green leaves flying; 3 the ring 96 squares wide, a ring of glowing amber CRACKS left inside it, grey dust billowing out low; 4 the ring at the cell's edge and thinning, the slabs sinking, the chips falling; 5 the cracks' glow and the settling dust; 6 a few dim cracks. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 110:44 cells, image size 10560x704 (each cell 1760x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `brock_fx_r_hit.png`：大招「震地猛击」：被震飞，5 帧

被震地猛击击飞的人：脚下**地面一下崩起、几根短石刺冲上来**、一道琥珀光往上喷，碎石往两边飞。**人站的地方留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C), a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E).
Effect: AN EARTH ERUPTION, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: 1 an amber crack flash on the ground under its feet; 2 three short slate STONE SPIKES shooting up beside its feet (one each side, one small in front, mirrored), a column of warm amber light rising up its sides; 3 the spikes at their tallest (9 squares), chips flying out; 4 the spikes crumbling, the light fading upward; 5 falling chips and dust. The middle of the cell (its body) stays EMPTY. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 22:26 cells, image size 1760x416 (each cell 352x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `brock_fx_r_rock.png`：大招「震地猛击」：天上落下的石头，7 帧

砸地之后天上掉下来的碎石：**一块青灰色的大石头从格子最上面直直落下来**（后面拖一道短短的尘土尾巴），砸在格子最下面的地上，碎成几块、一圈尘土炸开、地上一道琥珀色的小裂缝。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a slate stone ramp (#B9D2D6, #8BB6BE, #63909B, #34586B, #1E3647), a dust ramp (#E2DACA, #B3A992, #7D7464, #4C473E), a warm amber earth-glow ramp (#FFFBD0, #FBF82F, #FFC23A, #FB771C, #C4421C).
Effect: A FALLING ROCK, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the bottom of the cell is the ground: 1 a round slate BOULDER 9 squares across at the very top of the cell, a short dust streak above it; 2 the boulder a third of the way down, the streak longer (straight up above it); 3 the boulder two thirds down; 4 the boulder hitting the ground at the bottom, an amber-white flash under it; 5 the boulder burst into four chunks flying out low to both sides (mirrored), a ring of dust 20 squares wide, a short amber crack; 6 the chunks on the ground, the dust thinning; 7 the last dust and the dim crack. everything is the power of a STONE GOLEM of the jungle (an earth elemental overgrown with roots and leaves): chunky slate-teal stone chips and slabs, cracks in the ground glowing a WARM AMBER-ORANGE light, brown roots, bright green leaves, grey-brown dust; flat shades, crisp blocky shapes; no fire flames, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 7 equal 22:52 cells, image size 2464x832 (each cell 352x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `brock_icon_skill.png`：技能 1「巨岩投掷」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little amber corners, a deep teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big round slate-teal boulder wrapped in two brown roots flying to the upper right, a trail of grey-brown dust and chips behind it, a warm amber glint on its edge. No text, no letters.
```

### 图标 2. `brock_icon_skill2.png`：技能 2「苔藤缠握」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little amber corners, a deep teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: thick brown roots bursting out of a glowing amber crack in the ground and curling up into a grasping hand shape, small bright green leaves on them. No text, no letters.
```

### 图标 3. `brock_icon_ult.png`：大招「震地猛击」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little amber corners, a deep teal-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge slate-teal stone fist smashing down into the ground, a bright amber shockwave ring and cracks bursting out under it, small rocks falling from the top. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `brock_fx_a_hit` | view_effects `tft_brock_a_hit`（跟随目标，z 2；左右对称） | 18 × 16 |
| `brock_fx_a_quake` | view_effects `tft_brock_a_quake`（放在目标脚下的地面上，不跟随，z -1；左右对称） | 40 × 14 |
| `brock_fx_a_up` | view_buffs `tft_brock_a_up`（跟随被击飞的人，脚下，z 3；左右对称） | 22 × 10 |
| `brock_fx_q_rock` | view_projectiles `tft_brock_q_rock`（直线弹道，随飞行方向旋转；上下对称、朝右） | 20 × 14 |
| `brock_fx_q_hit` | view_effects `tft_brock_q_hit`（跟随目标，z 2；左右对称） | 30 × 22 |
| `brock_fx_q_slow` | view_buffs `tft_brock_q_slow`（跟随被减速的人，脚下，z 3；左右对称） | 24 × 8 |
| `brock_fx_e_vine` | view_effects `tft_brock_e_vine`（放在目标脚下的地面上，不跟随，z 2；左右对称） | 30 × 30 |
| `brock_fx_e_root` | view_buffs `tft_brock_e_root`（跟随被定身的人，腿部，z 3；左右对称） | 24 × 16 |
| `brock_fx_e_shield` | view_buffs `tft_brock_e_shield`（大表，跟随岩宝，z 3；左右对称） | 72 × 54 |
| `brock_fx_r_jump` | view_effects `tft_brock_r_jump`（放在他起跳的地面上，不跟随，z -1；左右对称） | 60 × 16 |
| `brock_fx_r_slam` | view_effects `tft_brock_r_slam`（大表，放在他落地砸下的地面上，不跟随，z -1；左右对称） | 110 × 44 |
| `brock_fx_r_hit` | view_buffs `tft_brock_r_hit`（跟随被击飞的人，z 3；左右对称） | 22 × 26 |
| `brock_fx_r_rock` | view_effects `tft_brock_r_rock`（放在落点的地面上，不跟随，z 2；画面最下面是地面；左右对称） | 22 × 52 |
| `brock_icon_skill` | skill_icons[0] `asset/tft/icons/tft_brock_skill` | 64 × 64 |
| `brock_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_brock_skill2` | 64 × 64 |
| `brock_icon_ult` | skill_icons[2] `asset/tft/icons/tft_brock_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_brock_fx`（小的）和 `tft_brock_big`（e_shield、r_slam、r_rock、r_jump），tag = 名字。
- q_rock 断言上下对称（朝右），其余断言左右对称。
- a_quake、r_jump、r_slam 放在地面上（不跟随，z -1）；e_vine、r_rock 放在落点（不跟随）；e_shield 是他身上的 buff；a_up、q_slow、e_root、r_hit 是敌人身上的 buff；q_rock 是直线弹道。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
