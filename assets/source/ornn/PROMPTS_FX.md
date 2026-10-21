# 山隐之焰 奥恩：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图。** 造型和动作已定（`design/ornn_idle.png`：3/4 正面朝右、驼背的羊角半神铁匠，灰蓝皮肤，一对深铁灰带暗红符文的大羊角，深红鬃毛和大胡子，青铜羊角胸甲，近侧手里一把钢青大锤，远侧手臂从肘部往下是熔岩、握着小锤）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），44 格高、48 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/ornn_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/ornn_shots.png`：动作帧（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奥恩自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行；最后一行是英雄联盟里**大招的熔岩公羊**（从正上方、从侧面、跃出地面三个角度）。只在本地用，不要提交。颜色照英雄联盟原版：**他的火是锻炉的火**（白黄的芯、橙黄的身、红橙的边、一点黑烟），**他的石头是黑色的玄武岩、裂缝里透着橙黄的熔岩光**，**公羊是带符文的黑色岩石身体、深红的大角、发光的熔岩腿和火焰尾巴**。
> - **特效要亮**：每团火和光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：两张弹道图（`q_fissure` 裂隙头、`r_ram` 公羊）**头朝右、上下严格对称**（游戏会把它们转到前进方向，往左跑时整张倒过来，所以要从正上方看、上下对称）；`w_fire` 喷火**头朝右**（我会把它画进他自己的动作帧里）；其余**全部严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - **连招**：`q_rise` / `q_pillar` 是 Q 立起来的熔岩柱，`e_quake` 是 E 撞碎柱子的地震（Q→E）；`r_call` → `r_rise` → `r_ram` 是R 第一段召唤公羊冲回来，`r_butt` 是第二段头槌把公羊顶回去（R1→R2）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ornn_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/ornn_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/ornn_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（被动「活体锻炉」的易碎和 W「风箱炎息」在里面） | 大锤砸击；打中易碎的英雄引爆；每 12 秒喷火（不可阻挡、护盾） | `a_hit` · `br_pop` · `brittle` · `w_fire` · `w_hit` · `w_shown` |
| 技能 1 = Q「火山突堑」 | 熔岩拳砸地，裂隙贴地冲出，尽头升起熔岩柱 | `q_slam` · `q_fissure` · `q_hit` · `q_rise` · `q_pillar` |
| 技能 2 = E「炽烈冲锋」 | 低头冲撞；撞碎柱子时地震击飞（Q→E 连招） | `e_quake` · `e_hit` |
| 大招「熔铸之神的召唤」 | 召唤熔岩公羊从远处冲回来，到身边时头槌顶回去击飞（R1→R2 连招） | `r_call` · `r_rise` · `r_ram` · `r_butt` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**；**只有实心的石头**（熔岩柱、碎石块、公羊的岩石身体和角、易碎的碎壳）有一圈近黑的描边。
- **要亮**：每个火和光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 锻炉的火（火焰、熔岩、发光的裂纹、火星）：`#FFFFFF`、`#FFF3A8`、`#FFC63A`、`#FF8A1E`、`#E8481A`、`#A0201A`；
  - 黑色玄武岩（柱子、碎石、公羊的身体）：`#9C8F94`、`#6E6168`、`#463B44`、`#2A2129`、`#140E14`；
  - 尘土：`#EFE2CC`、`#C9B394`、`#9A8366`、`#6B5843`；
  - 公羊的深红大角：`#FF8A9A`、`#E2334F`、`#A01A35`、`#5E1024`、`#2A0A14`；
- 打中、爆发居中画，不旋转；地面上的圈（尘土环、符文环、冲击波）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、他身边的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：他的普攻射程 25000，Q 的裂隙最长 80000，E 地震的半径 30000，公羊的宽 24000）。

### 1. `ornn_fx_a_hit.png`：普攻打中：大锤砸击，4 帧

大锤砸中目标：中间一闪白黄的冲击光，一圈橙红的火星和灰色碎石向两边飞溅，底下扬起一点灰尘，最后剩几粒火星（参考 ba_clouds、z_splash_2x2、r_sparks-orange）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A) and a dust ramp (#EFE2CC, #C9B394, #9A8366, #6B5843).
Effect: A HAMMER IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares across ringed with short orange sparks; 2 a burst 16 across - orange-red embers flying out at mirrored angles, small grey rock chips, a puff of dust at the bottom; 3 the embers further out and smaller, the dust spreading; 4 a few fading embers and dust.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `ornn_fx_br_pop.png`：易碎引爆：烧红的外壳炸裂，5 帧

普攻打中**易碎**的英雄：他身上一层烧红开裂的外壳猛地炸开——先是一圈发光的裂纹，然后白黄的闪光，几块带橙色发光边的黑色碎壳向四周飞出，火星四溅（参考 q_jhin_base_e_ash、bufftransfer_sparkle_red、recall_ember）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A) and a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14).
Effect: A BRITTLE SHELL SHATTERING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a jagged ring of glowing orange crack lines 16 squares across; 2 a white-yellow flash 10 across in the middle, the cracks blazing; 3 dark rock shards (each 2-3 squares, with glowing orange edges) flying out in a mirrored ring 22 across, orange sparks between them; 4 the shards further out and smaller, falling; 5 a few fading embers. a near-black outline round the solid rock only (never round fire, sparks, dust or glow).
Layout: one horizontal row of 5 equal square cells, image size 2080x416 (each cell 416x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `ornn_fx_brittle.png`：易碎（敌人头上，循环），4 帧

被奥恩的 W / E / R 打中的英雄**易碎**了：头上一枚小小的裂开的熔岩印记——一块黑色的圆石，十字形的裂缝里透着橙黄色的光，一明一暗地跳动（参考 livingforge_base_z_glow、recall_ember）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14) and a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A).
Effect: A SMALL CRACKED EMBER SIGIL over a head, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a dark rock disc 8 squares across with a jagged cross-shaped crack glowing orange-yellow; 1 dim, 2 the crack brighter, 3 the brightest with two tiny sparks above it at mirrored places, 4 dim again. a near-black outline round the solid rock only (never round fire, sparks, dust or glow).
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `ornn_fx_w_fire.png`：W 风箱炎息：朝前喷出的火（他嘴里，循环），6 帧

奥恩低头朝前喷出的一大股火焰：从格子左边中间（他的嘴）开始，朝右越来越宽的锥形火焰，芯是白黄，身子橙黄，边上卷起一团团红橙的火舌和几缕黑烟，尽头散成火星（参考 w_rumble_skin03_r_flamemesh、w_fuzzyshad、w_sparks-orange、distort-heat）。**头朝右**（这张会画进他自己的动作帧里，红色方随人物一起翻过来），6 帧循环，火舌一帧一帧往前翻滚。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A).
Effect: A ROARING FIRE BREATH, 6 frames, a loop, POINTING RIGHT (its root at the cell's left middle - his mouth - widening to the right): a cone of fire 46 squares long, 4 squares tall at the root and 26 at the far end, a white-yellow core along its middle, a yellow-orange body, red-orange curling tongues on its edges and a few dark smoke puffs on top, embers scattering past its end; each frame the tongues roll forward (the loop seamless).
Layout: one horizontal row of 6 equal 48:30 cells, image size 4608x480 (each cell 768x480, 16 px a square); the cone's root touching the cell's left side, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `ornn_fx_w_hit.png`：喷火打中：小火舌，3 帧

喷火每一下打中敌人：身上冒起一小簇火舌。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A).
Effect: A SMALL FLAME LICK, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an orange flame 4 squares wide and 5 tall with a yellow core; 2 two tongues 7 wide and 8 tall; 3 fading embers.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `ornn_fx_w_shown.png`：风箱炎息的护盾（他身上，循环），4 帧

喷火时他得到的护盾：围着他一圈像烧红的铁一样的热浪外框——橙红色发光的椭圆，顶上更亮，零星往上飘的火星；**中间他的身体位置留空**，不要盖住人（参考 livingforge_base_w_metal_texture、distort-heat）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A).
Effect: A HEAT SHIELD round a huge figure, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the huge horned smith stands in the middle, not drawn: 44 squares from the top of his horns to the ground, about 47 squares wide, his body area left EMPTY): an oval outline 56 squares wide and 50 tall, 2 squares thick, of glowing orange-red heat like red-hot iron, a brighter yellow rim along its top, small sparks rising from it at mirrored places; each frame the glow ripples round the oval and the sparks move up.
Layout: one horizontal row of 4 equal 60:54 cells, image size 3840x864 (each cell 960x864, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `ornn_fx_q_slam.png`：Q 熔岩拳砸地（他脚下），5 帧

熔岩拳砸地：他脚下的地面炸开一圈尘土和碎石，几道发红的裂缝朝左右两边延伸出去（参考 q_aatrox_r_explosion_firering、q_dustcloud_erosion）。从斜上方看的地面，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A), a dust ramp (#EFE2CC, #C9B394, #9A8366, #6B5843) and a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14).
Effect: A GROUND SLAM at his feet, seen from slightly above, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash on the ground 8 squares wide; 2 a dust ring 30 wide and 8 tall, rock chips jumping up at mirrored places, red-orange cracks starting in the ground; 3 the dust ring 40 wide, the glowing cracks running out to both sides; 4 the dust thinning, the cracks dimmer; 5 faint dust and two dim cracks.
Layout: one horizontal row of 5 equal 44:16 cells, image size 3520x256 (each cell 704x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `ornn_fx_q_fissure.png`：Q 火山突堑：贴地冲出的裂隙头（弹道，循环），3 帧

裂隙往前冲的那一头，**从正上方看**：地面被撕开一道锯齿形的口子，口子里透着黄橙的熔岩光，前端最宽、熔岩和火星往两边喷，后面渐渐收窄成一道细缝（参考 q_new_solar_tag、z_rockdebris）。**头朝右、上下严格对称**（游戏会把它转到前进方向），3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A) and a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14).
Effect: THE HEAD OF A RUNNING GROUND FISSURE seen from directly above, 3 frames, a loop, POINTING RIGHT (its head at the cell's right, its tail toward the left; the game turns it to its flight) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight, so it must look the same upside down): a jagged crack in dark rock 20 squares long, glowing yellow-orange inside, 8 squares wide at its head where lava drops and sparks spurt out at mirrored places, narrowing to 2 at its left end; each frame the spurts and sparks change.
Layout: one horizontal row of 3 equal 22:12 cells, image size 1056x192 (each cell 352x192, 16 px a square); the crack centred vertically, its head touching the cell's right side. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `ornn_fx_q_hit.png`：裂隙打中：熔岩碎石溅射，4 帧

裂隙打中敌人：一闪橙光，熔岩滴和黑色碎石向两边溅起又落下。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A) and a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14).
Effect: A LAVA AND ROCK SPLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an orange flash 5 squares across; 2 lava drops and dark rock chips flung up and out 12 across at mirrored places; 3 falling, smaller; 4 a few embers.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `ornn_fx_q_rise.png`：Q 熔岩柱升起（裂隙尽头的地上，不跟随），6 帧

裂隙尽头升起的柱子（**Q→E 连招撞的就是它**）：先是地面隆起裂开、裂缝里透出橙光，然后一根尖顶的黑色玄武岩柱一截一截顶出来，柱身上爬着发光的橙黄裂纹，柱脚一圈碎石。**左右对称**，6 帧，最后一帧就是立好的柱子（和下一张 q_pillar 外形一样）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14), a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A) and a dust ramp (#EFE2CC, #C9B394, #9A8366, #6B5843).
Effect: A BASALT PILLAR RISING from the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its base on the cell's bottom row: 1 the ground bulging and cracking, orange light in the cracks, dust 16 squares wide; 2 a jagged rock tip 6 squares tall breaking out, sparks; 3 the pillar 18 tall; 4 30 tall, dust and pebbles falling off it; 5 40 tall; 6 the finished pillar 42 tall and 14 wide: a chunky column of dark basalt with a pointed jagged top, glowing yellow-orange cracks running down it, a ring of broken rocks round its base. a near-black outline round the solid rock only (never round fire, sparks, dust or glow).
Layout: one horizontal row of 6 equal 20:44 cells, image size 1920x704 (each cell 320x704, 16 px a square); the pillar centered across, its base on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `ornn_fx_q_pillar.png`：熔岩柱（立着，循环），2 帧

立好的柱子，**和 q_rise 第 6 帧外形完全一样**，只是裂纹里的熔岩一明一暗。**左右对称**，2 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14) and a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A).
Effect: THE FINISHED BASALT PILLAR exactly as frame 6 of the previous sheet (42 squares tall, 14 wide, its base on the cell's bottom row, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side)), 2 frames, a loop: 1 its glowing cracks dimmer, 2 brighter with a tiny ember rising from its top. a near-black outline round the solid rock only (never round fire, sparks, dust or glow).
Layout: one horizontal row of 2 equal 20:44 cells, image size 640x704 (each cell 320x704, 16 px a square); the pillar centered across, its base on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `ornn_fx_e_quake.png`：E 撞柱的地震（以他为中心），6 帧

**Q→E 连招**：冲撞撞碎柱子（附加包里撞墙也算）的一瞬，他脚下炸开一圈冲击波——地面裂开、尘土和火焰翻卷，柱子的黑色碎石块向四周飞起再落下（参考 e_sion_base_r_explo_clouds、e_cas_spit、riftherald_smoke_dust）。从斜上方看的地面，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A), a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14) and a dust ramp (#EFE2CC, #C9B394, #9A8366, #6B5843).
Effect: A QUAKE SHOCKWAVE at his feet, seen from slightly above, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash on the ground 12 squares wide; 2 a ring of dust and fire 36 wide and 10 tall, broken basalt chunks (2-4 squares, glowing orange edges) flying up at mirrored places; 3 the ring 52 wide, the chunks higher and further out, glowing cracks in the ground; 4 the ring 60 wide, the chunks falling; 5 the dust thinning, chunks on the ground; 6 faint dust. a near-black outline round the solid rock only (never round fire, sparks, dust or glow).
Layout: one horizontal row of 6 equal 64:26 cells, image size 6144x416 (each cell 1024x416, 16 px a square); the ground ring's middle 9 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `ornn_fx_e_hit.png`：冲撞打中，4 帧

冲撞撞上敌人：一闪白黄的冲击光，尘土和橙色火星炸开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A) and a dust ramp (#EFE2CC, #C9B394, #9A8366, #6B5843).
Effect: A RAMMING IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares across; 2 a burst of dust and orange sparks 16 across; 3 the dust spreading, the sparks smaller; 4 fading dust.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `ornn_fx_r_call.png`：R 召唤（他脚下），6 帧

**R 第一段**：他砸锤召唤熔铸之神，脚下亮起一圈橙红的符文光环——环上是和他羊角上一样的方折回纹，向外扩散，地缝里冒出火舌（参考 livingforge_base_z_indicator_mult、recall_rgba）。从斜上方看的地面，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A).
Effect: A SUMMONING RING at his feet, seen from slightly above, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small glowing ring 12 squares wide; 2 the ring 30 wide and 8 tall, orange-red, angular key-pattern runes glowing on it at mirrored places; 3 the ring 46 wide, the runes brightest, short flames licking up from it; 4 the ring 52 wide, the flames higher; 5 dimming; 6 a faint ring.
Layout: one horizontal row of 6 equal 56:18 cells, image size 5376x288 (each cell 896x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `ornn_fx_r_rise.png`：R 公羊现身：远处的地上喷出火柱（不跟随），5 帧

公羊在远处出现的地方：地面裂开，喷出一根高高的火柱，四周飞溅火星和碎石，公羊就从火里冲出来（公羊本身是下一张 r_ram；参考 `refs/lol_fx_ref.png` 里公羊跃出的样子 ornnram_spawn）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A) and a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14).
Effect: A FIRE ERUPTION from the ground, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its base on the cell's bottom row: 1 glowing cracks on the ground 20 squares wide; 2 a burst of fire 14 wide and 20 tall, rock chips flying out at mirrored places; 3 a tall column of fire 18 wide and 36 tall, a white-yellow core, red-orange edges, dark smoke at its top; 4 the column breaking into flames and embers; 5 embers and smoke fading.
Layout: one horizontal row of 5 equal 34:40 cells, image size 2720x640 (each cell 544x640, 16 px a square); the eruption centered across, its base on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `ornn_fx_r_ram.png`：R 熔岩公羊（弹道，循环），4 帧

熔铸之神召唤的熔岩公羊，**从正上方往下看**（参考 `refs/lol_fx_ref.png` 里的 ornnram_top / ornnram_side）：头朝右，一对巨大的弯角向上下两边盘开（角尖深红、靠近头的地方暗铁色、刻着暗红的槽），头前一对发光的眼睛；身体是一块宽宽的深灰绿色岩石，背上刻着方折回纹的符文；后半身和四条短腿是发光的熔岩（橙黄），腿往上下两边撑开；身后拖着一条火焰尾巴。**头朝右、上下严格对称**（游戏会把它转到奔跑方向；从上往下看，往左跑也不会倒过来），4 帧循环（前后腿交替、火焰闪动，像在奔跑）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14), a crimson horn ramp (#FF8A9A, #E2334F, #A01A35, #5E1024, #2A0A14) and a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A).
Effect: A CHARGING LAVA RAM SEEN FROM DIRECTLY ABOVE, 4 frames, a loop, POINTING RIGHT (its head at the cell's right, its tail toward the left; the game turns it to its flight) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight, so it must look the same upside down): the head at the right with two HUGE CURLED HORNS sweeping out to the top and to the bottom (crimson tips, dark iron near the head, dark red grooves), two glowing eyes at the head's front; the body a broad oval of dark grey-green rock 16 squares long with an angular key-pattern rune on its back; the hindquarters and the four short legs glowing molten orange-yellow, the legs splayed to the top and the bottom; a flame tail trailing left; each frame the legs swap (the front pair forward and the back pair back, then the other way) and the tail's flames flicker. a near-black outline round the solid rock only (never round fire, sparks, dust or glow) (the horns and the rock body).
Layout: one horizontal row of 4 equal 40:28 cells, image size 2560x448 (each cell 640x448, 16 px a square); the ram centred vertically, its horns' front touching the cell's right side. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `ornn_fx_r_butt.png`：R 头槌（他身前），4 帧

**R 第二段**：公羊冲到身边，他用羊角把它顶回去的一瞬：一个白黄的大冲击闪光，一圈红橙的火焰冲击环，火星四溅。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A).
Effect: A HEADBUTT IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 10 squares across; 2 a ring of fire 28 across, thick and orange-red, sparks bursting out at mirrored angles; 3 the ring 32 across and thinner, the embers further out; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 2176x544 (each cell 544x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `ornn_fx_r_hit.png`：公羊撞中：火焰爆开，4 帧

公羊（来回两趟）撞中敌人：一团火焰爆开，夹着黑色碎石。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a forge-fire ramp (#FFFFFF, #FFF3A8, #FFC63A, #FF8A1E, #E8481A, #A0201A) and a dark basalt ramp (#9C8F94, #6E6168, #463B44, #2A2129, #140E14).
Effect: A FIRE BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares across; 2 a burst of flames 18 across, orange-red, with dark rock chips at mirrored places; 3 the flames breaking into embers; 4 fading embers and smoke.
Layout: one horizontal row of 4 equal square cells, image size 1408x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `ornn_fx_a_hit` | view_effects `league_ornn_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 18 × 18 |
| `ornn_fx_br_pop` | view_effects `league_ornn_br_pop`（跟随目标，z 2；左右对称） | 26 × 26 |
| `ornn_fx_brittle` | view_buffs `league_ornn_brittle`（跟随目标，z 3；左右对称；循环） | 14 × 10 |
| `ornn_fx_w_fire` | view_effects `league_ornn_w_fire`（他自己的 skill_w 帧里：烤进动作帧，bake_caster_fx；头朝右；大图表） | 48 × 30 |
| `ornn_fx_w_hit` | view_effects `league_ornn_w_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `ornn_fx_w_shown` | view_buffs `league_ornn_w_shown`（跟随他，z 3；左右对称；循环） | 60 × 54 |
| `ornn_fx_q_slam` | view_effects `league_ornn_q_slam`（他身上，不跟随，画在人物下面 z -1；左右对称；大图表） | 44 × 16 |
| `ornn_fx_q_fissure` | view_projectiles `league_ornn_q_fissure`（弹道：游戏会转到前进方向；头朝右、上下对称；大图表） | 22 × 12 |
| `ornn_fx_q_hit` | view_effects `league_ornn_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `ornn_fx_q_rise` | view_effects `league_ornn_q_rise`（放在裂隙尽头，不跟随，z 1；左右对称；大图表） | 20 × 44 |
| `ornn_fx_q_pillar` | view_effects `league_ornn_q_pillar`（裂隙尽头，每 0.25 秒盖一次，z 1；左右对称；大图表） | 20 × 44 |
| `ornn_fx_e_quake` | view_effects `league_ornn_e_quake`（他身上，不跟随，z -1；左右对称；大图表） | 64 × 26 |
| `ornn_fx_e_hit` | view_effects `league_ornn_e_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `ornn_fx_r_call` | view_effects `league_ornn_r_call`（他身上，不跟随，z -1；左右对称；大图表） | 56 × 18 |
| `ornn_fx_r_rise` | view_effects `league_ornn_r_rise`（放在远处公羊出发的点，不跟随，z 1；左右对称；大图表） | 34 × 40 |
| `ornn_fx_r_ram` | view_projectiles `league_ornn_r_ram`（弹道：游戏会转到奔跑方向；头朝右、上下对称；第二段头槌顶回去的 r_ram2 也用这张；大图表） | 40 × 28 |
| `ornn_fx_r_butt` | view_effects `league_ornn_r_butt`（他身上，画在人物上面 z 3；左右对称；大图表） | 34 × 34 |
| `ornn_fx_r_hit` | view_effects `league_ornn_r_hit`（跟随目标，z 2；左右对称） | 22 × 22 |

- 两张表：`asset/league/effects/league_ornn_fx`（小的）和 `league_ornn_big`（w_fire、q_slam、q_fissure、q_rise、q_pillar、e_quake、r_call、r_rise、r_ram、r_butt），tag = 名字（build_ornn.py 的 views；`r_ram2` 用 `r_ram` 的帧；`brittle`、`w_shown` 绑在同名 buff 上）。
- `w_fire` 数据里不放（CasterViewEffect 去掉）：它在 `league_ornn_big` 里只是一个 tag，`tools/art/rig_ornn.py` 的 `with_fire` 读它画进他的 skill_w 帧（火的根部对在嘴上，格雷福斯枪口火焰的做法）；其余除了两张弹道图全部断言左右对称，两张弹道图断言上下对称。
- 公羊的三张（`r_ram`、`r_rise`、`r_hit`）导入时放大 1.5 倍（用户：「R的羊的效果范围和效果都要做大点」「不重新生成 你在那个特效的基础上改」；`import_ornn_fx.py` 的 `up15`：Scale3x 后每 2×2 格取多数色，再按对称补齐），打中的半宽 `r_w` 12000 → 18000。
- `q_rise`、`q_pillar`、`r_rise` 底边对在落点的地面上；`q_slam`、`e_quake`、`r_call` 画在人物下面（z -1），`r_butt`、`brittle`、`w_shown` 在上面（z 3）；`q_pillar` 每 15 tick 盖一次，两帧的循环要接得上 `q_rise` 的最后一帧。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉给火、光描的最深色边（石头的描边保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。用户也可能用 Gemini 画好直接给图片（沃里克、格雷福斯的做法：process_*_fx.py）。
