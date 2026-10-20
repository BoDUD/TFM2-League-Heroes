# 解脱者 塞拉斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 23 张特效图。** 造型已定（`design/sylas_idle.png`：3/4 正面朝右、赤裸上身的男人，黑色长发、短黑胡子，深青灰的高领围巾和金色护颈片，两只很大的白色石头镣铐，金色的锁链拖在地上，深青绿长裤）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），约 38 格高、55 格宽（连锁链）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/sylas_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里塞拉斯自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**他的锁链是金色的**，**他的魔法（被动、突刺、偷大招）是蓝紫色的闪电，白色的芯**，**锁链鞭击的爆炸是金橙色的**，**回血是淡蓝色的**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；**弹道（q_chain、e_chain、r_hook、r2_arrow）画成朝右飞、严格上下对称**（游戏会按飞行方向转它，往左飞时整张倒过来）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sylas_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/sylas_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/sylas_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（被动「破敌禁法」和 W「弑君突刺」在里面） | 甩链；放完技能后挥链横扫一圈；每隔一阵对英雄的普攻变成突刺、回血 | `a_hit` · `p_spin` · `p_hit` · `p_1` · `w_hit` · `w_heal` |
| 技能 1 = Q「锁链鞭击」 | 两条锁链交叉在目标处，减速，延迟后交叉点爆炸 | `q_chain` · `q_hit` · `q_slow` · `q_cross` · `q_hit2` |
| 技能 2 = E「潜掠/强掳」 | 突进，再甩出锁链，命中的英雄被击飞、把自己拉过去 | `e_chain` · `e_hit` |
| 大招「其人之道」 | 第一次：锁链锁住英雄、夺走大招；第二次：在目标处放出夺来的大招 | `r_hook` · `r_steal` · `r_got` · `r_have` · `r2_boom` · `r2_hit` |
| 附加包的大招（按被偷的人的类别） | 射手 = 贯穿长箭，近战 = 跃起重砸，辅助 = 治疗之歌，刺客 = 闪身重击（法师 = 上面的 r2_boom） | `r2_arrow` · `r2_slam` · `r2_song` · `r2_blink` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、闪电、烟、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**（锁链的链环可以有一圈暗金色的边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 金色（锁链）：`#FFFFFF`、`#FFF4C2`、`#FFD84A`、`#E8A21E`、`#A86410`、`#5C3408`；
  - 蓝紫色（闪电、魔法）：`#FFFFFF`、`#E6E6FF`、`#9EA8FF`、`#6A5CF0`、`#4426B4`、`#200C5C`；
  - 金橙色（锁链鞭击的爆炸）：`#FFFFFF`、`#FFF2B0`、`#FFC040`、`#FF8A1A`、`#C24A0A`、`#5C1A04`；
  - 淡蓝色（回血、治疗之歌）：`#FFFFFF`、`#E2F4FF`、`#A8DCFF`、`#6AA8F0`、`#3A64B4`、`#1C2C5C`；
- 打中、爆发居中画，不旋转；地面上的圆（冲击波、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、他身边的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（23 张）

23 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：他的普攻射程 26000，锁链鞭击的射程 60000）。

### 1. `sylas_fx_a_hit.png`：普攻：锁链打中，3 帧

他甩链打中目标：一团金色的火花，中间一小道蓝紫色的电光（参考 ba_hit_directional2、ba_hit_tar_muzzle、hit_spark）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A CHAIN STRIKE ON A TARGET, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across with four short gold rays; 2 a gold spark burst 12 squares across, a small blue-violet lightning zigzag through its middle (mirrored); 3 a few gold sparks flying out and fading.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sylas_fx_p_spin.png`：被动 破敌禁法：挥链横扫一圈（他身边，跟随），5 帧

有层数时普攻变成挥链横扫：一圈金色的锁链带着蓝紫色的闪电在他腰部高度绕他转一圈（从斜上方看是扁椭圆），地上一圈蓝色的光（参考 p_slash、p_swipe_highlight、p_lightning、z_chains）。**他站在中间不画人，只画外圈**，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A WHIRL OF CHAINS ROUND A MAN, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the man stands in the middle, not drawn: 38 squares from his head to the ground, about 24 squares wide without his chains, his body area left EMPTY): a flat ellipse 56 wide and 16 tall drawn as a ring of GOLD CHAIN LINKS (each link 2x2 with a hole) at his waist height, blue-violet lightning crackling along it: 1 the ring's two front halves sweeping in from both sides; 2 the whole ring closed, bright, white lightning on its front; 3 the ring brightest, short lightning bolts shooting out at mirrored places; 4 the links fading into a blue-violet streak ring; 5 only sparks.
Layout: one horizontal row of 5 equal 60:30 cells, image size 4800x480 (each cell 960x480, 16 px a square); centered across, the ring's middle 12 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sylas_fx_p_hit.png`：被动：横扫打中的敌人，3 帧

横扫打中的每个敌人身上一小团蓝紫色的电光（参考 p_hit_electricity、p_hit_core、p_hit_sparks）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A LIGHTNING CRACKLE ON A TARGET, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white core 4 squares across; 2 a blue-violet star of 6 zigzag bolts 12 squares across; 3 the bolts broken into sparks, fading.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sylas_fx_w_hit.png`：W 弑君突刺：刺中（目标身上），4 帧

突刺刺中英雄：一团蓝紫色的魔法爆开，中间白光，四周一圈闪电和碎片（参考 w_hit_electricity、w_hit_shockwave、w_hit_tar_muzzle）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A MAGIC STAB BURST ON A TARGET, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a blue-violet burst 16 squares across with a white core and a thin ring; 3 lightning bolts and little petricite shards flying out at mirrored places; 4 sparks and shards fading.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sylas_fx_w_heal.png`：W：回血（他身上，跟随），5 帧

突刺回血：从他脚下升起淡蓝色的光丝，往他胸口聚过去，最后一闪（参考 w_glow、w_swirl、w_energy_trail）。**他站在中间不画人，只画两边**，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sky-blue ramp (#FFFFFF, #E2F4FF, #A8DCFF, #6AA8F0, #3A64B4, #1C2C5C).
Effect: A HEAL ROUND A MAN, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the man stands in the middle, not drawn: 38 squares from his head to the ground, about 24 squares wide without his chains, his body area left EMPTY): 1 a thin pale-blue ellipse on the ground under him (28 wide, 6 tall); 2 six thin wisps of light rising at his left and right; 3 the wisps higher, curving in toward his chest (two thirds up); 4 the wisps meeting in the middle with a white flash; 5 only the fading ellipse and two sparks.
Layout: one horizontal row of 5 equal 34:44 cells, image size 2720x704 (each cell 544x704, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sylas_fx_q_chain.png`：Q 锁链鞭击：飞出去的两条锁链（弹道，循环），3 帧

Q 甩出的两条锁链交叉着往前飞：两条金色的锁链一上一下拧在一起，最前面一道蓝紫色的电光（参考 z_chains、z_chains_glow、q_electricity）。**画成朝右飞**，**上下对称**（往左飞时游戏会把它转个方向），3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: TWO CHAINS FLYING RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight: drawn pointing RIGHT, upside down when it flies left): two GOLD CHAINS (links 2x2 with a hole) stretched horizontally, one above the other, twisting round each other so they cross at two places (mirrored top and bottom), their front ends at the right joined by a small bright blue-violet lightning tip; the twist shifts one link each frame.
Layout: one horizontal row of 3 equal 30:10 cells, image size 1440x160 (each cell 480x160, 16 px a square); the chains across the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sylas_fx_q_hit.png`：Q：锁链抽中，3 帧

锁链抽中路上的敌人：一道金色的 X 形火花（参考 q_hit_flash、q_hit_wispy、q_impact_target）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408).
Effect: A LASH HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a gold X of two crossed streaks 12 squares across; 3 the X fading into sparks.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sylas_fx_q_cross.png`：Q：交叉点蓄力、爆炸（地上，不跟随），10 帧

两条锁链交叉在地上（从斜上方看的 X），交叉点越来越亮（约 0.6 秒，前 6 帧），然后爆炸：金橙色的光柱从交叉点冲起来、一圈冲击波（后 4 帧）（参考 q_ground_impact、q_impact_glow、q_fb_explosion_centerflare、q_glowball_color、q_explosion_ring）。**左右对称**，10 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a gold-orange flare ramp (#FFFFFF, #FFF2B0, #FFC040, #FF8A1A, #C24A0A, #5C1A04).
Effect: A CHAIN CROSSING THAT BURSTS, 10 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the lower half of the cell is the ground seen from above at a slant: 1 two gold chain lines lying on the ground in a flat X (36 wide, 12 tall) with a small gold glow where they cross; 2-6 the crossing glow growing brighter each frame (a gold-white diamond, 4 then 10 squares wide), sparks crawling along the chains; 7 a bright white-gold flash at the crossing, the chains glowing white; 8 a gold-orange burst column 14 wide rising 24 squares from the crossing, a flat orange ring on the ground 36 wide; 9 the column breaking into flares, the ring wider and thinner; 10 only embers and the fading ring.
Layout: one horizontal row of 10 equal square cells, image size 6400x640 (each cell 640x640, 16 px a square); centered across, the crossing 10 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sylas_fx_q_hit2.png`：Q：爆炸打中，3 帧

爆炸打中的敌人身上一团金橙色的火花（参考 q_hit_flash、q_fb_explosion_centerflare）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold-orange flare ramp (#FFFFFF, #FFF2B0, #FFC040, #FF8A1A, #C24A0A, #5C1A04).
Effect: A FLARE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white core 5 squares across; 2 a gold-orange burst 14 squares across with short rays; 3 embers, fading.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sylas_fx_e_chain.png`：E 强掳：甩出去的锁链（弹道，循环），3 帧

E 甩出的一条锁链：一条拉直的金色锁链，最前面是一个发蓝光的禁魔石锁扣（参考 e_mis_tip、e_trail、z_chain）。**画成朝右飞**，**上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: ONE CHAIN FLYING RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight: drawn pointing RIGHT, upside down when it flies left): a straight GOLD CHAIN of links (2x2 with a hole) across the cell, at its right end a pale stone shackle tip glowing blue-violet (6 squares long, pointed), a faint blue streak along the chain behind it; the links shift one square each frame.
Layout: one horizontal row of 3 equal 24:8 cells, image size 1152x128 (each cell 384x128, 16 px a square); across the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sylas_fx_e_hit.png`：E：锁链缠住、击飞（目标身上），4 帧

锁链缠住被拉的英雄、把他击飞：一圈金色的锁链绕在他腰上，下面几道往上的白色气流（击飞），蓝紫色火花（参考 e_hit_spin、e_prison_mult、e2_swipe）。**被缠的人站在中间不画，只画锁链和气流**，**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A CHAIN SNARE AND KNOCK-UP ON A CHAMPION, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn, the body area left EMPTY): 1 a gold chain ring (an ellipse 20 wide and 6 tall) snapping round the waist with a white flash; 2 the ring bright, blue-violet sparks at its sides, three short white UP streaks under the feet; 3 the streaks longer, the ring tight; 4 the ring fading into sparks.
Layout: one horizontal row of 4 equal 22:30 cells, image size 1408x480 (each cell 352x480, 16 px a square); centered across, the waist ring 12 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `sylas_fx_r_hook.png`：R 其人之道：偷大招的锁链（弹道，循环），3 帧

R 甩出的锁链：一条金色锁链，前面一个发蓝紫光的爪形锁扣，链子周围缠着闪电（参考 r_hookmis_head、r_mis_shackles、r_lightning_beam）。**画成朝右飞**，**上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A STEALING CHAIN FLYING RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight: drawn pointing RIGHT, upside down when it flies left): a straight GOLD CHAIN of links across the cell, at its right end a glowing blue-violet claw-shaped head (two prongs, one up and one down, mirrored, 7 squares long), a thin blue-violet lightning zigzag wrapping the chain (mirrored above and below); the lightning flickers each frame.
Layout: one horizontal row of 3 equal 26:10 cells, image size 1248x160 (each cell 416x160, 16 px a square); across the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `sylas_fx_r_steal.png`：R：锁住、夺走大招（被偷的英雄身上），6 帧

被偷的英雄身上：两道金色的锁链交叉缠住他，一团蓝紫色的能量被从他胸口扯出来、往上飘走（参考 r_hit_electricity、r_swirl_01、r_bits）。**被偷的人站在中间不画**，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A HIJACK ON A CHAMPION, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn, the body area left EMPTY except the energy): 1 two gold chains crossing in an X over the body with a white flash; 2 the X bright, blue-violet lightning crawling on it; 3 a glowing blue-violet orb (6 squares) torn out at chest height in the middle; 4 the orb rising 8 squares, trailing sparks; 5 the orb at the top of the cell, the chains fading; 6 only sparks.
Layout: one horizontal row of 6 equal 26:40 cells, image size 2496x640 (each cell 416x640, 16 px a square); centered across, the chest 22 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `sylas_fx_r_got.png`：R：拿到夺来的大招（他身上，跟随），5 帧

他拿到夺来的大招：两团蓝紫色的能量从两边飞进他两只镣铐，在胸前汇成一个亮点一闪（参考 r_hand_smokeybits、r_return_lightning、r_lightning_cas）。**他站在中间不画人**，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A STOLEN POWER COMING HOME, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the man stands in the middle, not drawn: 38 squares from his head to the ground, about 24 squares wide without his chains, his body area left EMPTY): 1 two blue-violet sparks at the cell's left and right edges at hand height; 2 the sparks flying in, trailing lightning; 3 both reaching his hands (8 squares from the middle each) with small white flashes; 4 a bright white-violet point in the middle at chest height with two short arcs; 5 fading.
Layout: one horizontal row of 5 equal 32:26 cells, image size 2560x416 (each cell 512x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `sylas_fx_r2_boom.png`：R：放出夺来的大招（落点，不跟随），7 帧

第二次 R 在目标处爆发：一道蓝紫色的闪电从天上劈下来，落地炸开一圈金色和蓝紫色的冲击波（参考 r_lightning_beam_bright、r_electricity、r_timer、w_shockwave_sharp）。**左右对称**（闪电劈下来的那一道画在正中、竖直），7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C) and a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408).
Effect: A STOLEN ULTIMATE STRIKING DOWN, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin white-violet line falling from the cell's top to the ground point (8 squares above the bottom, middle); 2 a thick blue-violet lightning bolt 6 wide straight down the middle with mirrored side branches, a white flash at the ground; 3 a blast 30 squares across at the ground point, white core, a flat gold ring on the ground 40 wide; 4 the blast 40 across, lightning arcs spraying out at mirrored places; 5 the ring 46 wide and thin, the blast breaking up; 6 sparks and wisps; 7 fading.
Layout: one horizontal row of 7 equal square cells, image size 5376x768 (each cell 768x768, 16 px a square); centered across, the ground point 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `sylas_fx_r2_hit.png`：R：爆发打中，3 帧

被夺来的大招打中的敌人身上一团蓝紫色的电光（参考 r_hit_electricity）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A HEAVY LIGHTNING HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a blue-violet burst 16 squares across with four zigzag bolts; 3 sparks, fading.
Layout: one horizontal row of 3 equal square cells, image size 864x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `sylas_fx_p_1.png`：被动：有层数（他两只镣铐上，buff，循环），4 帧

破敌禁法存着层数时：他两只镣铐上噼啪跳着蓝紫色的小电光（参考 p_ready_buff、p_lightning、passive_scroll）。**他站在中间不画人，只在两只手的位置画电光**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: CRACKLING MANACLES, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the man stands in the middle, not drawn: 38 squares from his head to the ground, about 24 squares wide without his chains, his body area left EMPTY): at his two hands (14 squares left and right of the middle, 10 squares above the cell's bottom row) small blue-violet lightning sparks (4-6 squares) jumping and flickering, a white point in each; the sparks change shape each frame.
Layout: one horizontal row of 4 equal 40:24 cells, image size 2560x384 (each cell 640x384, 16 px a square); centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `sylas_fx_q_slow.png`：Q：减速（目标脚下，buff，循环），4 帧

被锁链减速的敌人脚下一圈暗金色的光，几节锁链的影子在上面慢慢转（参考 q_ringmult、q_ground）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408).
Effect: A SLOW RING under a target's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a dim gold ellipse 18 wide and 5 tall on the ground, a few dark-gold chain-link marks along its rim shifting one square round each frame (mirrored).
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `sylas_fx_r_have.png`：R：握着夺来的大招（他头顶上，buff，循环），4 帧

他握着夺来的大招时头顶上漂着一个蓝紫色的发光印记（菱形的禁魔石符文，四周一圈小电光）（参考 r_timer_mult、r_swirl_01）。**画在他头顶上方**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A STOLEN-POWER SIGIL over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a glowing blue-violet diamond rune 8 squares wide in the middle with a white core, small lightning sparks circling it (mirrored); it bobs one square up and down.
Layout: one horizontal row of 4 equal 18:12 cells, image size 1152x192 (each cell 288x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `sylas_fx_r2_arrow.png`：附加包 R（射手）：贯穿长箭（弹道，循环），3 帧

偷到射手的大招：一支蓝紫色和金色的能量长箭朝右飞，尾巴拖着光（参考 r_beam_trail_vert、r_trail_04）。**上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C) and a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408).
Effect: A STOLEN ENERGY ARROW FLYING RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight: drawn pointing RIGHT, upside down when it flies left): a long arrow of blue-violet energy with a white-gold pointed head at the right (8 squares long), its shaft 2 squares thick, a tapering trail of gold sparks to the left; the trail flickers each frame.
Layout: one horizontal row of 3 equal 28:8 cells, image size 1344x128 (each cell 448x128, 16 px a square); across the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `sylas_fx_r2_slam.png`：附加包 R（近战）：落地重砸（落点，不跟随），6 帧

偷到近战的大招：他跃起砸地，地上一圈金色的裂纹和蓝紫色的冲击波往外扩（参考 q_ground_impact、w_buff_ground、shards_2x2）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold chain ramp (#FFFFFF, #FFF4C2, #FFD84A, #E8A21E, #A86410, #5C3408) and a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A GROUND SLAM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash on the ground point; 2 gold cracks running out from it in a flat star (mirrored), a blue-violet ring 20 wide; 3 the ring 36 wide, rock chips thrown up at mirrored places; 4 the ring 50 wide, thin; 5 the cracks glowing dim, dust; 6 fading.
Layout: one horizontal row of 6 equal 56:24 cells, image size 5376x384 (each cell 896x384, 16 px a square); centered across, the ground point 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `sylas_fx_r2_song.png`：附加包 R（辅助）：治疗之歌（他身边，跟随），6 帧

偷到辅助的大招：他脚下一大圈淡蓝色的光环往外扩，几个音符和光点往上飘（参考 w_buff_ground、w_glow）。**他站在中间不画人**，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sky-blue ramp (#FFFFFF, #E2F4FF, #A8DCFF, #6AA8F0, #3A64B4, #1C2C5C).
Effect: A HEALING SONG ROUND A MAN, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the man stands in the middle, not drawn: 38 squares from his head to the ground, about 24 squares wide without his chains, his body area left EMPTY): 1 a pale-blue ellipse on the ground under him 20 wide; 2 the ellipse 40 wide, four small music notes rising at mirrored places; 3 the ellipse 56 wide, the notes higher with light motes; 4 the notes at the cell's top; 5 the ellipse thinning; 6 fading.
Layout: one horizontal row of 6 equal 60:44 cells, image size 5760x704 (each cell 960x704, 16 px a square); centered across, the ellipse's middle 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `sylas_fx_r2_blink.png`：附加包 R（刺客）：闪身（他身上，跟随），4 帧

偷到刺客的大招：他闪到目标身边，身上一团蓝紫色的烟和残影散开（参考 r_stealth_into_swooshies_rgba、r_smokeerode）。**他站在中间不画人**，**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet lightning ramp (#FFFFFF, #E6E6FF, #9EA8FF, #6A5CF0, #4426B4, #200C5C).
Effect: A BLINK OF SMOKE ROUND A MAN, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the man stands in the middle, not drawn: 38 squares from his head to the ground, about 24 squares wide without his chains, his body area left EMPTY): 1 a white-violet flash outline round where he stands; 2 blue-violet smoke puffs bursting out at his left and right; 3 the puffs bigger and darker, curling up; 4 fading wisps.
Layout: one horizontal row of 4 equal 24:40 cells, image size 1536x640 (each cell 384x640, 16 px a square); centered across, his feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `sylas_fx_a_hit` | view_effects `league_sylas_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `sylas_fx_p_spin` | view_effects `league_sylas_p_spin`（跟随他，画在人物下面 z -1；左右对称；大图表） | 60 × 30 |
| `sylas_fx_p_hit` | view_effects `league_sylas_p_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `sylas_fx_w_hit` | view_effects `league_sylas_w_hit`（跟随目标，z 2；左右对称） | 20 × 20 |
| `sylas_fx_w_heal` | view_effects `league_sylas_w_heal`（跟随他，z 3；左右对称） | 34 × 44 |
| `sylas_fx_q_chain` | view_projectiles `league_sylas_q_chain`（随飞行方向转，画成**朝右**；上下对称；循环） | 30 × 10 |
| `sylas_fx_q_hit` | view_effects `league_sylas_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `sylas_fx_q_cross` | view_effects `league_sylas_q_cross`（落点，不跟随，画在人物下面 z -1；左右对称；大图表） | 40 × 40 |
| `sylas_fx_q_hit2` | view_effects `league_sylas_q_hit2`（跟随目标，z 2；左右对称） | 16 × 16 |
| `sylas_fx_e_chain` | view_projectiles `league_sylas_e_chain`（随飞行方向转，画成**朝右**；上下对称；循环） | 24 × 8 |
| `sylas_fx_e_hit` | view_effects `league_sylas_e_hit`（跟随目标，z 2；左右对称） | 22 × 30 |
| `sylas_fx_r_hook` | view_projectiles `league_sylas_r_hook`（随飞行方向转，画成**朝右**；上下对称；循环） | 26 × 10 |
| `sylas_fx_r_steal` | view_effects `league_sylas_r_steal`（跟随目标，z 2；左右对称） | 26 × 40 |
| `sylas_fx_r_got` | view_effects `league_sylas_r_got`（跟随他，z 3；左右对称） | 32 × 26 |
| `sylas_fx_r2_boom` | view_effects `league_sylas_r2_boom`（落点，不跟随，z -1；左右对称；大图表） | 48 × 48 |
| `sylas_fx_r2_hit` | view_effects `league_sylas_r2_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `sylas_fx_p_1` | view_buffs `league_sylas_p_1`（跟随他，z 3；左右对称；循环） | 40 × 24 |
| `sylas_fx_q_slow` | view_buffs `league_sylas_q_slow`（跟随目标，z -1；左右对称；循环） | 20 × 8 |
| `sylas_fx_r_have` | view_buffs `league_sylas_r_have`（跟随他，z 3；左右对称；循环） | 18 × 12 |
| `sylas_fx_r2_arrow` | view_projectiles `league_sylas_r2_arrow`（随飞行方向转，画成**朝右**；上下对称；循环） | 28 × 8 |
| `sylas_fx_r2_slam` | view_effects `league_sylas_r2_slam`（不跟随，z -1；左右对称；大图表） | 56 × 24 |
| `sylas_fx_r2_song` | view_effects `league_sylas_r2_song`（跟随他，z -1；左右对称；大图表） | 60 × 44 |
| `sylas_fx_r2_blink` | view_effects `league_sylas_r2_blink`（跟随他，z 3；左右对称） | 24 × 40 |

- 两张表：`asset/league/effects/league_sylas_fx`（小的）和 `league_sylas_big`（p_spin、q_cross、r2_boom、r2_slam、r2_song），tag = 名字（build_sylas.py 的 views；p_1 / q_slow / r_have 绑在同名 buff 上，附加包的 r2_slow 用 q_slow 的图）。
- 打中、身上、地上的断言左右对称，弹道断言上下对称；`p_spin`、`q_cross`、`r2_boom`、`r2_slam`、`r2_song`、`q_slow` 画在他下面（z -1），`w_heal`、`r_got`、`r_have`、`p_1`、`r2_blink` 在上面（z 3）。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（链环的暗金边保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
