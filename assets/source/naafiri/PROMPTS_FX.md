# 百裂冥犬 纳亚菲利：给 Codex 的特效提示词（第 3 步）

> **这一份是 21 张特效图。** 造型已定（`design/naafiri_designs.png`：左边纳亚菲利——3/4 正面朝右的四足猎犬、红色狼头白色口鼻、石板蓝甲壳、深紫色刀刃鬃毛镶薄荷绿边；右边狗群伙伴——深红色的小猎犬、灰色骨头盔）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），30 格高、52 格长，伙伴 16 格高、33 格长；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/naafiri_size.png`：她和伙伴放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里纳亚菲利自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的暗裔之力是深红色的、芯是白的，影子是暗紫色**；刀刃边上偶尔一点**薄荷绿**的闪光；**匕首是钢刃加骨柄**；**回血是深红带金**（不是绿色）。
> - **特效要亮**：每道光、每团血光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **光、血光、斩痕、冲击波、光环都没有黑描边**；**实物**（匕首、狗群伙伴、小盾）有 1 格近黑描边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（两把匕首、狗群的速度线）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图，往左时是倒过来的；匕首转成圆盘就两边一样）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `naafiri_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/naafiri_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/naafiri_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「狂烈种群」 | 扑咬；每次普攻和技能命中，狗群也咬一口（暴吼时四只） | `a_hit` · `pk_bite` · `pk_bite4` |
| 技能 1 = Q「暗裔犬牙」 | 甩出匕首、流血；狗群扑上命中的英雄撕咬 3 秒；下一次普攻甩出第二把，命中英雄回血 | `q_dagger` · `q_leap` · `q_hit` · `q_bleed` · `pk_leap` · `pk_ride` · `q2_dagger` · `q2_hit` · `q_heal` |
| 技能 2 = E「剔骨本能」 | 冲到目标身上，周围撕裂两圈 | `e_slash` · `e_slash2` · `e_hit` |
| 大招「暴吼」+「猎狗血性」 | 先吼（不可选取、狗群翻倍 5 秒），再扑向英雄（减速、减护甲）；参与击杀后可带护盾再扑一次 | `r_roar` · `pack_aura` · `r_hit` · `r_shred` · `r_reset` · `r_shield` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、血光、斩痕、冲击波、光环没有黑描边，也不要用最深的颜色给形状描一圈边**（实物——匕首、伙伴、小盾——有 1 格近黑描边）。
- **要亮**：每个光、血光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 暗裔之力（深红）：`#FFFFFF`、`#FFD6D6`、`#FF6A6A`、`#E8283A`、`#A8122A`、`#5E0A1C`；
  - 暗影（暗紫）：`#F0D8FF`、`#C08AF0`、`#8A4AC8`、`#5A2A8E`、`#301650`；
  - 刀刃闪光（薄荷绿，只做点缀）：`#F0FFF8`、`#A8F2D0`、`#56CFA0`、`#2E8E70`；
  - 匕首骨柄：`#FFF8E8`、`#EEDCB4`、`#C8AC80`、`#8E7250`、`#5A4632`；
  - 匕首钢刃：`#FFFFFF`、`#DDE6EE`、`#A8B6C4`、`#6E7C8C`、`#3E4652`；
  - 回血（深红带金）：`#FFFFFF`、`#FFE8C8`、`#FFB070`、`#F06A4A`、`#B8303A`；
  - 狗群伙伴：`#FF5A5A`、`#D8243A`、`#A01428`、`#640C1A`、`#A8B4C4`、`#6E7C8C`、`#3E4652`、`#FFE070`、`#0E0A12`；
- 打中、爆发居中画，不旋转；地面上的圈（撕裂、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**（`pk_ride` 里的两只小狗是要画的）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（21 张）

21 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：E 撕裂半径 18000，大招射程 60000）。

### 1. `naafiri_fx_a_hit.png`：普攻：撕咬打中目标，3 帧

狼牙咬中：上下两排白色尖牙合拢的一闪，中间迸出深红色的血光（参考 naafiri_base_ba_fangs01、foundation_impactspike）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A BITE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of white fangs (an upper and a lower arc, 5 fangs each) snapping together with a crimson flash between them; 2 the fangs closed, a crimson burst of 6 short spikes flying out; 3 only the fading crimson specks.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `naafiri_fx_pk_bite.png`：被动 狂烈种群：狗群的一口（两只），3 帧

狗群在目标身上咬一口：两侧各一道小小的咬痕（三颗牙），一闪深红（比普攻小、暗一些）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A SMALL PACK BITE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two small bite marks (three white fangs each) snapping in from the left and the right sides; 2 a small crimson splash between them; 3 fading crimson specks. Smaller and darker than the leader's bite.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `naafiri_fx_pk_bite4.png`：暴吼时狗群的一口（四只），3 帧

暴吼期间狗群翻倍：四道咬痕从四个方向咬上去，深红加一点暗紫。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C), a dark violet shadow ramp (#F0D8FF, #C08AF0, #8A4AC8, #5A2A8E, #301650).
Effect: A BIG PACK BITE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 four bite marks (three white fangs each) snapping in from the upper left, the upper right, the lower left and the lower right; 2 a crimson splash in the middle with dark violet wisps; 3 fading crimson and violet specks.
Layout: one horizontal row of 3 equal 16:14 cells, image size 768x224 (each cell 256x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `naafiri_fx_pk_leap.png`：Q 命中后狗群扑上去，4 帧

Q 的匕首命中英雄、狗群扑上去的那一下：目标身上从两侧冲来两道深红色的残影（像两只狗扑来的速度线），撞在一起一闪。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A PACK POUNCE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two short crimson speed streaks coming in low from the left and the right edges; 2 the streaks halfway, bending up toward the middle; 3 they meet in a crimson flash; 4 fading specks.
Layout: one horizontal row of 4 equal 16:12 cells, image size 1024x192 (each cell 256x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `naafiri_fx_pk_ride.png`：狗群扑在目标身上撕咬（循环），4 帧

Q 命中的英雄身上：**两只小伙伴**（照 `design/naafiri_designs.png` 右边的伙伴，缩到 14 格长左右）一左一右扑在目标脚边撕咬——左边那只朝右、右边那只朝左（互为镜像），头一下一下往中间咬。**中间目标的身体位置留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from the packmate's own colours (#FF5A5A, #D8243A, #A01428, #640C1A, #A8B4C4, #6E7C8C, #3E4652, #FFE070, #0E0A12: crimson body, slate-grey helmet and blade, a yellow eye, a near-black outline), a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: TWO SMALL HOUNDS MAULING, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two small crimson hounds with slate-grey bony helmets (each about 14 squares long and 8 tall) at the bottom left and the bottom right, the left one facing RIGHT and the right one facing LEFT (mirror images), both biting toward the middle: 1 heads drawn back; 2 heads lunging in, jaws open; 3 jaws closed with a small crimson splash at each; 4 heads drawing back. SOLID OBJECTS (the daggers, the packmates) have a 1-square near-black outline; light, blood, slashes and shockwaves have none.
Layout: one horizontal row of 4 equal 40:20 cells, image size 2560x320 (each cell 640x320, 16 px a square); the hounds' paws on the cell's bottom row; the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (only its lower 20 squares are in the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `naafiri_fx_q_dagger.png`：Q 暗裔犬牙：飞出去的匕首，4 帧

旋转飞出的暗裔匕首：骨柄加弯刃，转成一个圆盘，后面拖一小道深红残光（参考 naafiri_base_q_missile01、foundation_missile）。**朝右飞、上下对称**，4 帧（转一圈）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#FFFFFF, #DDE6EE, #A8B6C4, #6E7C8C, #3E4652), a bone ramp (#FFF8E8, #EEDCB4, #C8AC80, #8E7250, #5A4632), a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A SPINNING DARKIN DAGGER, 4 frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a curved steel blade with a bone hilt spinning end over end so it reads as a disc 5 squares across (the blade's glint at a different place each frame), a short crimson streak trailing 4 squares behind it. SOLID OBJECTS (the daggers, the packmates) have a 1-square near-black outline; light, blood, slashes and shockwaves have none.
Layout: one horizontal row of 4 equal 10:6 cells, image size 640x96 (each cell 160x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `naafiri_fx_q2_dagger.png`：Q 第二把匕首（更大、更红），4 帧

第二把匕首：比第一把大一圈，刃上裹着一层深红色的光，拖的残光更长。**朝右飞、上下对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#FFFFFF, #DDE6EE, #A8B6C4, #6E7C8C, #3E4652), a bone ramp (#FFF8E8, #EEDCB4, #C8AC80, #8E7250, #5A4632), a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A SECOND, BIGGER DAGGER, 4 frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): like a spinning darkin dagger but 7 squares across, its blade wrapped in a crimson glow, a crimson streak trailing 5 squares behind it. SOLID OBJECTS (the daggers, the packmates) have a 1-square near-black outline; light, blood, slashes and shockwaves have none.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `naafiri_fx_q_leap.png`：狗群扑向目标的速度线，3 帧

跟着匕首扑向目标的狗群，只画成一道贴地的深红色速度线（参考 naafiripackmate_speedboostline）。**朝右飞、上下对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A PACK SPEED STREAK, 3 frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): three thin crimson streaks, the middle one longest (14 squares), pointed at the right end, fading to the left; each frame they flicker.
Layout: one horizontal row of 3 equal 16:5 cells, image size 768x80 (each cell 256x80, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `naafiri_fx_q_hit.png`：Q 第一把匕首打中，3 帧

匕首扎中：一道深红色的十字刺光，带几滴血珠飞散。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A DAGGER HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a crimson four-pointed star flash 7 squares across with a white core; 2 the star breaking up, 5 crimson drops flying out; 3 only falling drops.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `naafiri_fx_q_bleed.png`：Q 流血（每次跳伤害时播），3 帧

流血跳一下：目标身上冒出几滴深红色的血珠往下滴。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A BLEED TICK, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 three crimson drops appearing at the top; 2 the drops falling with short trails; 3 fading drops at the bottom.
Layout: one horizontal row of 3 equal 10:14 cells, image size 480x224 (each cell 160x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `naafiri_fx_q2_hit.png`：Q 第二把匕首打中（更大），4 帧

第二把匕首扎中：更大的深红色爆开，中间一道交叉的刃光，外圈一圈暗紫色碎片。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C), a dark violet shadow ramp (#F0D8FF, #C08AF0, #8A4AC8, #5A2A8E, #301650).
Effect: A HEAVY DAGGER HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an X of two crimson blade streaks 12 squares across with a white core; 2 a crimson burst with dark violet shards flying out; 3 the shards farther, the burst fading; 4 last specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `naafiri_fx_q_heal.png`：第二把匕首命中英雄时回血，4 帧

她回血：身边升起几点深红带金的光点（不是绿色），往上飘。**中间她的身体位置留空**，**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson-gold heal ramp (#FFFFFF, #FFE8C8, #FFB070, #F06A4A, #B8303A).
Effect: A HEAL, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): small crimson-gold light motes (2-3 squares, white cores) rising at both sides of a low body and above it, a few plus-shaped glints; the middle EMPTY where the body is.
Layout: one horizontal row of 4 equal 30:22 cells, image size 1920x352 (each cell 480x352, 16 px a square); she stands in the middle, not drawn: a hound 51 squares long and 30 tall, low on four legs (its middle part). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `naafiri_fx_e_slash.png`：E 剔骨本能：周围第一圈撕裂，4 帧

落地后在身边转圈撕裂：一圈深红色的爪痕弧线绕着她（地面上的椭圆，前后都有），刃尖带一点薄荷绿的闪光。**中间她的身体位置留空**，**左右对称**，4 帧：起、最亮、散开、余痕。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C), mint-green glints (#F0FFF8, #A8F2D0, #56CFA0, #2E8E70) as accents only.
Effect: A CIRCLE OF CLAW SLASHES, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): four curved crimson slash arcs sweeping round a flat ground ellipse 50 squares wide and 16 tall (two at the front, two at the back), white at their leading edges, a few mint glints at the tips; 1 the arcs half drawn; 2 full and brightest; 3 breaking into crimson shreds; 4 fading shreds.
Layout: one horizontal row of 4 equal 56:26 cells, image size 3584x416 (each cell 896x416, 16 px a square); the ellipse's middle on the cell's middle, 4 squares above the bottom; she stands in the middle, not drawn: a hound 51 squares long and 30 tall, low on four legs. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `naafiri_fx_e_slash2.png`：E 第二圈撕裂（更大），4 帧

第二下撕裂：更大一圈，深红加暗紫，碎片飞得更远。**中间留空**，**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C), a dark violet shadow ramp (#F0D8FF, #C08AF0, #8A4AC8, #5A2A8E, #301650), mint-green glints (#F0FFF8, #A8F2D0, #56CFA0, #2E8E70) as accents only.
Effect: A WIDER CIRCLE OF CLAW SLASHES, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): like the first but on an ellipse 58 squares wide and 18 tall, crimson arcs with dark violet edges, shreds flying farther out; 1 half drawn; 2 brightest; 3 breaking; 4 fading.
Layout: one horizontal row of 4 equal 64:30 cells, image size 4096x480 (each cell 1024x480, 16 px a square); the ellipse's middle on the cell's middle, 4 squares above the bottom; she stands in the middle, not drawn: a hound 51 squares long and 30 tall, low on four legs. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `naafiri_fx_e_hit.png`：E 打中的敌人，3 帧

被撕裂打中：两道交叉的深红爪痕。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A CLAW HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two crossing crimson claw streaks (an X, 9 squares) with a white core; 2 the streaks fading, 4 specks flying out; 3 fading specks.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `naafiri_fx_r_roar.png`：大招起手 暴吼：怒吼的冲击波，5 帧

她仰天一吼：从她头部的位置往外扩散两圈暗紫色加深红的音波弧（像吼声的冲击波），地上一圈暗紫色的光环，几点深红的火星往上飞（参考 naafiri_base_r_flash_sharp、r_cas_outline、r_eyes01）。**中间她的身体位置留空**，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark violet shadow ramp (#F0D8FF, #C08AF0, #8A4AC8, #5A2A8E, #301650), a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A ROAR SHOCKWAVE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small dark violet flash above the middle (where her raised head is); 2 two wide sound-wave arcs (crimson inner, violet outer) spreading out to both sides, a violet ring on the ground round her; 3 the arcs at the cell's sides, the ground ring widest; 4 the arcs breaking up, crimson sparks rising; 5 last sparks. The middle EMPTY where the body is.
Layout: one horizontal row of 5 equal 64:40 cells, image size 5120x640 (each cell 1024x640, 16 px a square); she stands in the middle, not drawn: a hound 51 squares long and 30 tall, low on four legs (its paws on the cell's bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `naafiri_fx_r_hit.png`：大招 猎狗血性：扑中目标，4 帧

扑中英雄：一大口深红色的獠牙咬合（上下两排大牙），外圈暗紫色的冲击，迸出血光（参考 naafiri_base_r_tar_alpha1）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C), a dark violet shadow ramp (#F0D8FF, #C08AF0, #8A4AC8, #5A2A8E, #301650).
Effect: A POUNCE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two big rows of white fangs (8 fangs each, upper and lower arcs 18 squares wide) snapping shut; 2 a crimson burst between them, a dark violet ring flashing out; 3 the fangs gone, crimson spikes and violet shards flying out; 4 fading specks.
Layout: one horizontal row of 4 equal 22:20 cells, image size 1408x320 (each cell 352x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `naafiri_fx_r_reset.png`：参与击杀、可以再扑一次，4 帧

参与击杀后大招刷新：她头顶上方亮起一对发光的深红色狼眼（参考 naafiri_base_r_eyes01），一闪后化成火星。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C), a dark violet shadow ramp (#F0D8FF, #C08AF0, #8A4AC8, #5A2A8E, #301650).
Effect: A PAIR OF GLOWING EYES, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two slanted crimson eyes (each 5 squares wide, white cores) flaring open in a dark violet haze high above the middle; 2 brightest; 3 narrowing; 4 breaking into rising crimson sparks.
Layout: one horizontal row of 4 equal 24:20 cells, image size 1536x320 (each cell 384x320, 16 px a square); the eyes in the cell's upper half; she stands in the middle, not drawn: a hound 51 squares long and 30 tall, low on four legs below (only her top is in the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `naafiri_fx_pack_aura.png`：暴吼期间（循环），4 帧

暴吼的 5 秒：她脚下一圈暗紫色的光环，边上几缕深红色的雾气往上飘（狗群翻倍的气势）。**中间留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark violet shadow ramp (#F0D8FF, #C08AF0, #8A4AC8, #5A2A8E, #301650), a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C).
Effect: A PACK AURA, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat dark violet ground ellipse 54 squares wide and 10 tall round her paws (only its rim lit), a few crimson wisps rising from the rim at both sides, flickering in turn; the middle EMPTY.
Layout: one horizontal row of 4 equal 60:18 cells, image size 3840x288 (each cell 960x288, 16 px a square); the ellipse's middle on the cell's middle; she stands in the middle, not drawn: a hound 51 squares long and 30 tall, low on four legs (only her paws reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `naafiri_fx_r_shred.png`：大招减护甲（循环），4 帧

被扑中的英雄护甲被撕开：头顶一块裂开的暗红色小盾，裂缝一闪一闪。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C), a steel ramp (#FFFFFF, #DDE6EE, #A8B6C4, #6E7C8C, #3E4652).
Effect: A SHREDDED ARMOUR MARK, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small steel shield icon 8 squares tall with a crimson claw rent down its middle (three slashes), the rent glowing brighter and dimmer in turn. SOLID OBJECTS (the daggers, the packmates) have a 1-square near-black outline; light, blood, slashes and shockwaves have none.
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `naafiri_fx_r_shield.png`：再扑一次时的护盾（循环），4 帧

第二次扑出带的护盾：罩住她的一层深红色半透明感的光膜（像素画里用一圈亮边加稀疏的内纹表现，不要整片涂满），边缘几处薄荷绿的闪光。**中间她的身体位置留空**（只画外圈和稀疏纹），**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson darkin-power ramp (#FFFFFF, #FFD6D6, #FF6A6A, #E8283A, #A8122A, #5E0A1C), mint-green glints (#F0FFF8, #A8F2D0, #56CFA0, #2E8E70) as accents only.
Effect: A SHIELD BUBBLE, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a dome-shaped crimson outline round a low body (54 squares wide, 32 tall, its bottom on the cell's bottom), a 1-square bright rim with a white highlight at the top, a few sparse crimson streaks inside the rim (never filled), mint glints moving round the rim; the middle EMPTY.
Layout: one horizontal row of 4 equal 58:36 cells, image size 3712x576 (each cell 928x576, 16 px a square); she stands in the middle, not drawn: a hound 51 squares long and 30 tall, low on four legs (its paws on the cell's bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `naafiri_fx_a_hit` | view_effects `league_naafiri_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `naafiri_fx_pk_bite` | view_effects `league_naafiri_pk_bite`（跟随目标，z 2；左右对称） | 10 × 10 |
| `naafiri_fx_pk_bite4` | view_effects `league_naafiri_pk_bite4`（跟随目标，z 2；左右对称） | 16 × 14 |
| `naafiri_fx_pk_leap` | view_effects `league_naafiri_pk_leap`（跟随目标，z 2；左右对称） | 16 × 12 |
| `naafiri_fx_pk_ride` | view_effects `league_naafiri_pk_ride`（跟随目标，z -1；左右对称） | 40 × 20 |
| `naafiri_fx_q_dagger` | view_projectiles `league_naafiri_q_dagger`（随飞行方向转；上下对称） | 10 × 6 |
| `naafiri_fx_q2_dagger` | view_projectiles `league_naafiri_q2_dagger`（随飞行方向转；上下对称） | 12 × 8 |
| `naafiri_fx_q_leap` | view_projectiles `league_naafiri_q_leap`（随飞行方向转；上下对称） | 16 × 5 |
| `naafiri_fx_q_hit` | view_effects `league_naafiri_q_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `naafiri_fx_q_bleed` | view_effects `league_naafiri_q_bleed`（跟随目标，z 2；左右对称） | 10 × 14 |
| `naafiri_fx_q2_hit` | view_effects `league_naafiri_q2_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `naafiri_fx_q_heal` | view_effects `league_naafiri_q_heal`（她身上，z 3；左右对称） | 30 × 22 |
| `naafiri_fx_e_slash` | view_effects `league_naafiri_e_slash`（她身上，z -1；左右对称） | 56 × 26 |
| `naafiri_fx_e_slash2` | view_effects `league_naafiri_e_slash2`（她身上，z -1；左右对称） | 64 × 30 |
| `naafiri_fx_e_hit` | view_effects `league_naafiri_e_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `naafiri_fx_r_roar` | view_effects `league_naafiri_r_roar`（她身上，z 3；左右对称） | 64 × 40 |
| `naafiri_fx_r_hit` | view_effects `league_naafiri_r_hit`（跟随目标，z 2；左右对称） | 22 × 20 |
| `naafiri_fx_r_reset` | view_effects `league_naafiri_r_reset`（她身上，z 3；左右对称） | 24 × 20 |
| `naafiri_fx_pack_aura` | view_buffs `league_naafiri_pack4`（tag pack_aura；跟着她，循环，z -1；左右对称） | 60 × 18 |
| `naafiri_fx_r_shred` | view_buffs `league_naafiri_r_shred`（跟着目标，循环，z 3；左右对称） | 14 × 10 |
| `naafiri_fx_r_shield` | view_buffs `league_naafiri_r_shield`（跟着她，循环，z 3；左右对称） | 58 × 36 |

- 两张表：`asset/league/effects/league_naafiri_fx`（小的）和 `league_naafiri_big`（pk_bite4、pk_ride、e_slash、e_slash2、r_roar、pack_aura、r_shield），tag = 名字（build_naafiri.py 的 views；buff pack4 的 tag 是 pack_aura）。
- 弹道（q_dagger、q2_dagger、q_leap）断言上下对称；其余断言左右对称；e_slash、e_slash2、r_roar、pack_aura、r_shield 跟随她。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
