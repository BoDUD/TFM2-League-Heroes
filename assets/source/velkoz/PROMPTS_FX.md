# 虚空之眼 维克兹：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型和动作已定（`design/velkoz_idle.png`：3/4 正面朝右、飘在空中的虚空之眼——卡其金色的甲壳、正中一只发光的品红色大眼睛和上面三只小眼睛，三条深青黑色、尖端品红的触手）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），36 格高、51 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/velkoz_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/velkoz_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里维克兹自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**他的虚空能量（普攻、裂隙、射线、E 的能量柱）是紫色的、芯是白的**，**大眼睛射出的等离子（Q）是品红色的**，**被动的研究标记是品红色的三瓣眼睛符号**，**E 炸起的碎石是灰褐色的**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **光、能量、火焰、光环、冲击波都没有黑描边**；**碎石**有 1 格暗边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、地上、头上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道和线**（普攻的能量弹、Q 的等离子弹、W 的裂隙、R 的射线）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图，往左时是倒过来的）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `velkoz_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/velkoz_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/velkoz_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（W「虚空裂隙」和被动在里面） | 从大眼睛发射虚空能量；每第 3 下朝目标撕开一道裂隙，裂隙随后爆开 | `a_bolt` · `a_hit` · `w_rift` · `w_hit` |
| 技能 1 = Q「等离子裂变」 | 发射等离子弹，打中减速并在命中点分裂成往两边飞的两颗 | `q_bolt` · `q_hit` · `q_split` · `q_split_hit` · `q_slow` |
| 技能 2 = E「构造分解」 | 目标区域地面裂开，随后爆开把敌人击飞 | `e_mark` · `e_boom` · `e_hit` |
| 大招「生命形态瓦解射线」 | 从大眼睛射出一道射线引导 2.5 秒，跟着目标烧 | `r_beam` · `r_hit` |
| 被动「有机体解构」 | 技能打中英雄叠层：头上的研究标记亮 1、2 瓣，第 3 层爆开造成真实伤害 | `p_s1` · `p_s2` · `p_full` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火焰、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**（碎石可以有 1 格暗边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 紫色的虚空能量（普攻、裂隙、射线、能量柱）：`#FFFFFF`、`#F0DCFF`、`#CC9CFF`、`#9A5CF2`、`#6430BE`、`#36167A`；
  - 品红色的等离子（Q、研究标记）：`#FFFFFF`、`#FFD4FF`、`#FF84F4`、`#E626DC`、`#A00EA6`、`#58065E`；
  - 灰褐色的碎石和尘土（E）：`#E6DAC6`、`#B8A68A`、`#8A7860`、`#5E5040`、`#382E26`；
- 打中、爆发居中画，不旋转；地面上的圆（预警圈、减速的等离子）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：他的普攻射程 55000，裂隙长 75000，E 的半径 22000，射线长 120000）。

### 1. `velkoz_fx_a_bolt.png`：普攻：虚空能量弹（弹道，循环），4 帧

从他的大眼睛射出的一小团紫色虚空能量：白色的芯，紫色的光，后面拖一小截紫色的尾巴（参考 ba_beam_bolts、ba_sparks、z_flare_purp）。**朝右飞、尾巴在左边，上下对称**，4 帧循环（光一闪一闪）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A).
Effect: A SMALL VOID BOLT, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round violet energy bolt 4 squares across with a white core 1-2 squares, a tapering violet trail 5 squares long behind it on the left; each frame the core flickers and two tiny violet sparks shift along the trail.
Layout: one horizontal row of 4 equal 10:6 cells, image size 640x96 (each cell 160x96, 16 px a square); the bolt's middle on the cell's middle row, its head 1 square from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `velkoz_fx_a_hit.png`：普攻：打中目标，3 帧

能量弹打中：一团紫色的光一闪，散成几点紫色的火星（参考 ba_sparks、z_sparks_grey）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A).
Effect: A SMALL VOID HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 6 squares across; 2 a violet ring 9 squares across with 4 sparks flying out diagonally; 3 only the fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `velkoz_fx_q_bolt.png`：Q 等离子裂变：等离子弹（弹道，循环），4 帧

从大眼睛射出的品红色等离子球：亮白的芯，品红色的球，外面一圈细细的紫色光环，后面一条闪着小星星的拖尾（参考 q_ball_mis、q_core_center_mis、q_core_ring_mis、q_smallstartrail）。**朝右飞、拖尾在左边，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta plasma ramp (#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E).
Effect: A MAGENTA PLASMA ORB, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round orb 6 squares across - a white core 2 squares, bright magenta round it, a thin violet-magenta ring just outside; a sparkling trail 7 squares long behind it on the left made of small magenta and white star sparks; each frame the ring pulses one square and the sparks shift.
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); the orb's middle on the cell's middle row, its front 1 square from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `velkoz_fx_q_hit.png`：Q：等离子弹打中，5 帧

等离子球打中目标：品红色的等离子炸开，一圈亮环往外扩，中间白光（参考 q_splitexplosion、q_implode_circle、q_tar）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta plasma ramp (#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E).
Effect: A PLASMA BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across with a magenta rim; 2 a bright magenta burst 12 squares across, white in the middle; 3 a magenta ring 18 squares across, 2 squares thick, plasma droplets inside; 4 the ring thinner and fainter, droplets falling; 5 only a few fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `velkoz_fx_q_split.png`：Q：命中点分裂（往上下两边射出两颗小等离子弹），6 帧

Q 打中东西的地方，等离子弹一分为二：命中点先亮一下，然后**两颗小一点的品红色等离子弹分别往正上方和正下方飞出去**，各拖一条星星尾巴，飞到格子的上下两头后散开（参考 q_splitexplosion、split_spark）。**左右对称，也上下对称**（上面那颗和下面那颗一模一样），6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta plasma ramp (#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E).
Effect: A PLASMA BOLT SPLITTING IN TWO, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) and also SYMMETRIC TOP TO BOTTOM: 1 a white-magenta flash 8 squares across in the middle of the cell; 2 two small magenta orbs (4 squares across, white cores) leaving it, one going straight UP and one straight DOWN, 6 squares from the middle, a short sparkling trail behind each toward the middle; 3 the orbs 12 squares from the middle; 4 18 squares; 5 the orbs at the cell's top and bottom ends, fading; 6 only fading sparks along the two paths.
Layout: one horizontal row of 6 equal 16:46 cells, image size 1536x736 (each cell 256x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `velkoz_fx_q_split_hit.png`：Q：分裂弹打中，4 帧

分裂出来的小等离子弹打中：比 q_hit 小一号的品红色爆开（参考 q_tar）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta plasma ramp (#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E).
Effect: A SMALL PLASMA POP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a magenta burst 9 squares across; 3 a thin magenta ring 12 squares across; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `velkoz_fx_q_slow.png`：Q：减速（buff，目标脚下，循环），4 帧

被等离子减速的人脚下一圈品红色的黏稠等离子，冒着小泡（参考 q_tar、q_marker_glow）。**只画在脚下，不画人**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta plasma ramp (#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E).
Effect: A PLASMA SLOW UNDER A UNIT, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a champion stands in the middle, not drawn: about 16 squares wide and 36 tall, only its feet on the cell's bottom part): a flat magenta plasma ellipse on the ground (20 wide, 5 tall), a brighter rim, small bubbles rising 1-2 squares at mirrored places and popping; each frame different bubbles.
Layout: one horizontal row of 4 equal 22:8 cells, image size 1408x128 (each cell 352x128, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `velkoz_fx_w_rift.png`：W 虚空裂隙：一道裂隙（直线，从他往目标），10 帧

他朝目标撕开一道 75 格长的虚空裂隙：先是地上一条锯齿形的紫色裂缝从左到右亮起来（第 1–3 帧），裂缝里透出白紫色的光（第 4–5 帧），然后整条裂缝**爆开**：白色的闪光，紫色的能量往上下两边喷（第 6–7 帧，这是第二段伤害），最后碎成紫色的火星散掉（第 8–10 帧）（参考 w_aoe_02、w_second_crack_tx_2、w_mis_groundtrench、w_missilehead_1、w_flash_hit）。整条裂隙**横着画、左右两头尖**，**上下对称**（游戏按方向转这张图），10 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A).
Effect: A VOID RIFT along the ground, 10 frames, lying ALONG the cell (left to right), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a long horizontal jagged crack 74 squares long, pointed at both ends: 1 the crack's left third glowing violet, 1 square thick; 2 two thirds; 3 the whole crack, 2 squares thick, violet with a darker purple edge; 4 white light inside it, the crack 4 squares thick at its middle, tapering; 5 brighter, small violet sparks above and below at mirrored places; 6 it BURSTS: a white flash along the whole line, violet energy spraying 5 squares up and down; 7 the spray at its highest (6 squares), fading at the edges; 8 the crack breaking into violet fragments; 9 scattered sparks; 10 a few fading sparks.
Layout: one horizontal row of 10 equal 78:14 cells, image size 12480x224 (each cell 1248x224, 16 px a square); the crack's middle on the cell's middle row, its ends 2 squares from the cell's left and right. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `velkoz_fx_w_hit.png`：W：裂隙打中，3 帧

裂隙伤到的人身上：紫色的能量碎片往上溅（参考 w_flash_hit）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A).
Effect: A RIFT HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a violet-white flash 6 squares across low in the cell; 2 violet shards spraying up and out in a V, 12 squares tall; 3 only fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `velkoz_fx_e_mark.png`：E 构造分解：地面裂开（预警，落点），6 帧

E 的落点地面先裂开：一个紫色发光的椭圆圈，圈里地面裂开一道道紫色的裂缝，越来越亮（约 0.55 秒后爆开）（参考 e_aoe、e_cracks、e_nova_ground、e_tar_darkground）。**只画在地面上**，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A).
Effect: A GROUND TELEGRAPH, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground 44 wide and 15 tall: 1 a thin violet ellipse outline and a dark purple patch inside; 2 four short glowing violet cracks inside, from the middle outward, mirrored; 3 the cracks longer, branching; 4 the cracks reaching the rim, the rim brighter; 5 the cracks white-violet, small dust specks lifting; 6 the brightest: the whole ellipse glowing, the cracks white.
Layout: one horizontal row of 6 equal 48:18 cells, image size 4608x288 (each cell 768x288, 16 px a square); centered across and down. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `velkoz_fx_e_boom.png`：E：地面爆开（落点），7 帧

落点爆开：地面炸起一堆碎石和尘土，中间一道紫色的虚空能量柱往上冲，碎石往两边飞（被击飞的人会飞起来）（参考 e_impactspike、e_firewall1、e_puffs、crater_01、e_lightning03）。**左右对称**（碎石也对称），7 帧，**底边是地面**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A) and a dusty grey-brown earth ramp (#E6DAC6, #B8A68A, #8A7860, #5E5040, #382E26).
Effect: AN ERUPTION from the ground, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash on the ground, an ellipse 30 wide and 8 tall; 2 a column of violet void energy shooting up from it, 12 squares wide and 30 tall, white in the middle, chunks of grey-brown rock (2-4 squares each, with dark edges) thrown up and out at mirrored places; 3 the column 44 tall, the rocks higher and wider apart, dust puffs at the ground on both sides; 4 the column breaking into violet flames at the top, the rocks at their highest; 5 the rocks falling, the energy fading to violet wisps; 6 dust settling, a few rocks on the ground; 7 faint dust.
Layout: one horizontal row of 7 equal 48:52 cells, image size 5376x832 (each cell 768x832, 16 px a square); centered across, the ground ellipse's middle 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `velkoz_fx_e_hit.png`：E：被炸中，3 帧

被炸飞的人身上：碎石和紫光一闪（参考 e_puffs）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A) and a dusty grey-brown earth ramp (#E6DAC6, #B8A68A, #8A7860, #5E5040, #382E26).
Effect: A ROCK-AND-VOID HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a violet flash 6 squares across; 2 four small grey-brown rocks flying out diagonally with violet sparks; 3 fading sparks and dust.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `velkoz_fx_r_beam.png`：R 生命形态瓦解射线：射线（一整条，Claude 切成每一帧），4 帧

大招的射线：从他的大眼睛射向前方的一整条光束，**长 128 格**：白色的芯（2 格），外面紫色，再外面一层淡淡的品红色光边，光束里有扭动的白紫色能量丝；**左端是一个圆形的亮光（眼睛处的发射点，9 格）**，右端渐渐变细、散开（参考 r_beam_middle、r_beamcore_02、r_energy、r_lightning、r_sides、r_end_line）。**横着画、上下对称**，4 帧循环（能量丝流动、光一闪一闪）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A).
Effect: A LONG DISINTEGRATION RAY, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its direction): a straight horizontal beam 128 squares long from a round white-violet flare 9 squares across at the LEFT end (where it leaves the eye); the beam 9 squares thick near the flare and 7 along its length - a white core 2 squares, violet round it, a thin pale magenta outer glow; twisting white-violet energy threads running along it; the RIGHT end thinning to 3 squares and breaking into violet sparks over its last 10 squares; each frame the threads move to the right and the flare pulses.
Layout: one horizontal row of 4 equal 130:13 cells, image size 8320x208 (each cell 2080x208, 16 px a square); the beam on the cell's middle row, the flare's middle 6 squares from the left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `velkoz_fx_r_hit.png`：R：射线灼烧（目标身上），4 帧

射线照到的人身上：紫色的能量灼烧，一团紫白色的火焰往上窜，几点火星（参考 r_hitbubble、r_impactfire、r_obscsparks）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-purple void ramp (#FFFFFF, #F0DCFF, #CC9CFF, #9A5CF2, #6430BE, #36167A).
Effect: A RAY BURN on a target, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 6 squares across; 2 violet flames 10 squares wide licking up 12 squares, white at their base; 3 the flames higher and thinner, sparks rising; 4 fading wisps.
Layout: one horizontal row of 4 equal 14:16 cells, image size 896x256 (each cell 224x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `velkoz_fx_p_s1.png`：被动 有机体解构：1 层（目标头上），4 帧

被技能打中的英雄头上出现维克兹的研究标记：一个**倒三角形、分成三瓣的品红色眼睛符号**（英雄联盟的 p_eyecounter），**亮了一瓣**（**下面正中那瓣**白色发亮，上面两瓣暗紫色）（参考 p_eyecounter_1、p_eyecounter_2、p_eyecounter_3glow、p_researchcounter_ring）。**左右对称**，4 帧：出现、停住、停住、变淡。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta plasma ramp (#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E).
Effect: A RESEARCH MARK with 1 of 3 segments lit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an inverted triangle sign 11 squares wide and 9 tall split into three petal segments (upper-left, upper-right, bottom middle) round a small dark centre; the BOTTOM MIDDLE segment lit white with a magenta rim, the two upper ones dark purple with a magenta edge; 1 it pops in a square smaller; 2 full size; 3 full size, the lit segment glowing; 4 fading.
Layout: one horizontal row of 4 equal 13:11 cells, image size 832x176 (each cell 208x176, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `velkoz_fx_p_s2.png`：被动：2 层（目标头上），4 帧

同一个标记，**亮了两瓣**（上面左右两瓣白色发亮，下面正中那瓣暗紫色）。**左右对称**，4 帧：出现、停住、停住、变淡。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta plasma ramp (#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E).
Effect: THE SAME RESEARCH MARK with 2 of 3 segments lit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the inverted triangle sign 11 squares wide and 9 tall, its two upper segments lit white with magenta rims, the bottom segment dark purple with a magenta edge; 1 it pops in a square smaller; 2 full size; 3 full size, glowing; 4 fading.
Layout: one horizontal row of 4 equal 13:11 cells, image size 832x176 (each cell 208x176, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `velkoz_fx_p_full.png`：被动：3 层引爆真实伤害（目标身上），6 帧

第 3 层：标记三瓣全亮、一闪，然后**爆开成一圈白色和品红色的几何碎片**，像被分解成碎块一样往外飞（参考 p_eyecounter_3glow、p_hit_slice、shards）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta plasma ramp (#FFFFFF, #FFD4FF, #FF84F4, #E626DC, #A00EA6, #58065E).
Effect: A DECONSTRUCTION BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 the inverted triangle sign (11 wide, 9 tall) with ALL THREE segments lit white, a magenta glow round it; 2 the sign flashing bigger (15 wide), white; 3 it shatters: angular white and magenta shards (triangles and slivers, 2-3 squares each) flying outward in a ring 20 squares across; 4 the shards 26 squares apart, a thin magenta ring between them; 5 the shards smaller and fading; 6 a few fading specks.
Layout: one horizontal row of 6 equal square cells, image size 2688x448 (each cell 448x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `velkoz_fx_a_bolt` | view_projectiles `league_velkoz_a_bolt`（跟着弹道转向；上下对称） | 10 × 6 |
| `velkoz_fx_a_hit` | view_effects `league_velkoz_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 12 × 12 |
| `velkoz_fx_q_bolt` | view_projectiles `league_velkoz_q_bolt`（还有 q_bolt_f、附加包的 q_split_bolt；跟着弹道转向；上下对称） | 14 × 10 |
| `velkoz_fx_q_hit` | view_effects `league_velkoz_q_hit`（跟随目标，画在人物上面 z 2；左右对称） | 20 × 20 |
| `velkoz_fx_q_split` | view_effects `league_velkoz_q_split`（落点，不跟随，画在人物上面 z 2；左右对称、上下对称；大图表） | 16 × 46 |
| `velkoz_fx_q_split_hit` | view_effects `league_velkoz_q_split_hit`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 14 |
| `velkoz_fx_q_slow` | view_buffs `league_velkoz_q_slow`（跟随目标，画在人物下面 z -1；左右对称；循环） | 22 × 8 |
| `velkoz_fx_w_rift` | view_projectiles `league_velkoz_w_rift`（LineRangeProjectile 的图，跟着方向转；画在线的正中间；上下对称；大图表） | 78 × 14 |
| `velkoz_fx_w_hit` | view_effects `league_velkoz_w_hit`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 14 |
| `velkoz_fx_e_mark` | view_effects `league_velkoz_e_mark`（落点，不跟随，画在人物下面 z -1；左右对称；大图表） | 48 × 18 |
| `velkoz_fx_e_boom` | view_effects `league_velkoz_e_boom`（落点，不跟随，画在人物上面 z 2；左右对称；大图表） | 48 × 52 |
| `velkoz_fx_e_hit` | view_effects `league_velkoz_e_hit`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 14 |
| `velkoz_fx_r_beam` | view_projectiles `league_velkoz_r_beam`（Claude 把每帧切成从他眼睛射出的固定射线：league_lucian Q 的做法；上下对称；大图表） | 130 × 13 |
| `velkoz_fx_r_hit` | view_effects `league_velkoz_r_hit`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 16 |
| `velkoz_fx_p_s1` | view_effects `league_velkoz_p_s1`（跟随目标，画在人物上面 z 3；左右对称） | 13 × 11 |
| `velkoz_fx_p_s2` | view_effects `league_velkoz_p_s2`（跟随目标，画在人物上面 z 3；左右对称） | 13 × 11 |
| `velkoz_fx_p_full` | view_effects `league_velkoz_p_full`（跟随目标，画在人物上面 z 3；左右对称） | 28 × 28 |

- 两张表：`asset/league/effects/league_velkoz_fx`（小的）和 `league_velkoz_big`（q_split、w_rift、e_mark、e_boom、r_beam），tag = 名字（build_velkoz.py 的 views；q_bolt_f 和附加包的 q_split_bolt 用 q_bolt 的 tag）。
- 弹道和线（a_bolt、q_bolt、w_rift、r_beam）断言上下对称，q_split 两个方向都对称，其余断言左右对称；q_split、e_mark、e_boom 不跟随（落点）。
- 时间：a_bolt 前 2 帧空（弹从他身体中间出来，先藏住穿过眼睛的那一段，league_malzahar 的做法）；w_rift 的爆开帧落在 w_det（19 tick），整条画面 w_life（34 tick）；e_mark 拉长到 e_delay（33 tick），e_boom 接在后面；r_beam 每一波 r_p（15 tick）一帧一 tick：从 4 帧的光束里取，每帧往回挪 1 像素（弹道每 tick 往前 1 像素），光束左端一直在他的眼睛上（弹道从他的站位点出发，眼睛在前面 8 像素）。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（碎石的暗边保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
