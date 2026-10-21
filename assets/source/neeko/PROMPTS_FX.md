# 万花通灵 妮蔻：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型已定（`design/neeko_designs.png`：3/4 正面朝右的变色龙女孩——紫蓝色头发、品红紫的羽刺、珊瑚粉百合花、青绿色鳞片皮肤、珊瑚橙抹胸、白贝壳腰带、往上弯的长尾巴）。她在游戏里是**高清**的（每个游戏格子里 2.5×2.5 个细像素），40 格高、20 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/neeko_size.png`：她放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里妮蔻自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的魔法是亮粉 / 品红的光和花瓣，配青色火花和紫色暗部**；**倒刺是紫红色的刺藤**；**大招是粉紫色的、带一点彩虹光泽的大花**。
> - **特效要亮**：每道光、每朵光之花都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **光、火花、光环、冲击波都没有黑描边**；**实物**（种子、花瓣、叶子、刺藤）有 1 格近黑描边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（`p_poof` 变身的烟除外：它就是要罩住她）。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（魔法弹、种子、倒刺团）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图，往左时是倒过来的）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `neeko_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/neeko_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/neeko_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + W「两生花影」 | 射出魔法弹；每第三下普攻额外魔法伤害并加速 | `a_bolt` · `a_hit` · `w_hit` · `w_haste` |
| 技能 1 = Q「盛开花种」 | 扔出种子，落地炸开成花；炸到英雄会再盛开（最多两次） | `q_seed` · `q_burst` · `q_bloom` · `q_hit` |
| 技能 2 = E「缠结倒刺」 | 甩出一团贯穿的倒刺，路上的敌人被禁锢 | `e_barbs` · `e_hit` · `e_bound` |
| 大招「怒放」 | 蓄力（护盾）后跳起击飞周围敌人，落地炸开大花、晕眩 | `r_charge` · `r_jump` · `r_land` · `r_hit` |
| 被动「天生幻魅」（附加包） | 变成队友的样子、现形 | `p_poof` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火花、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**（实物——种子、花瓣、叶子、刺藤——有 1 格近黑描边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 魔法（亮粉 / 品红）：`#FFFFFF`、`#FFE0F2`、`#FF9AD6`、`#FF4FB4`、`#D21E8A`、`#7E0C54`；
  - 火花（青色）：`#F0FFFC`、`#A8FFF0`、`#4FE8D2`、`#1EB4A8`、`#0E6E6E`；
  - 暗部、刺藤（紫色）：`#F4DCFF`、`#C89AF4`、`#9258E0`、`#6230B0`、`#3A1A70`；
  - 花瓣：`#FFF4F8`、`#FFC8DC`、`#FF86B0`、`#F2507E`、`#B82858`；
  - 叶子、种子：`#E8FFD8`、`#A6E87A`、`#5CB848`、`#2E7A34`、`#16401E`；
  - 花心（金色，只做点缀）：`#FFFFFF`、`#FFF2B0`、`#FFD24A`、`#E89A1E`；
- 打中、爆发居中画，不旋转；地面上的圈（花环、冲击波、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 花的半径 22000，大招落地半径 40000）。

### 1. `neeko_fx_a_bolt.png`：普攻：魔法弹（弹道，循环），4 帧

她普攻射出的一颗魔法弹：粉红色的光球，芯是白的，外面一圈青色的小火花，后面拖一小段粉色尾迹（参考 neeko_base_ba_mis、ba_speed_flash）。**朝右飞、尾巴在左，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E).
Effect: A MAGIC BOLT, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): at the right a hot pink orb 4 squares across with a white core, two tiny teal sparks circling it (one above, one mirrored below), a short tapering pink trail 5 squares long behind it to the left; each frame the trail flickers.
Layout: one horizontal row of 4 equal 10:6 cells, image size 640x96 (each cell 160x96, 16 px a square); the orb's middle on the cell's middle row, 2 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `neeko_fx_a_hit.png`：普攻：打中目标，3 帧

魔法弹打中：一团粉色的小闪光，几粒青色火花溅开。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E).
Effect: A SMALL MAGIC HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink-white four-pointed flash 5 squares across; 2 the flash 8 across with 4 teal sparks at mirrored places; 3 only the sparks further out, fading.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `neeko_fx_w_hit.png`：W 两生花影：第三下强化普攻打中，4 帧

每第三下普攻的强化：打中时绽开一朵粉色的花形光（五片花瓣的光），中间白芯，外圈一圈青色火花（参考 neeko_base_w_spark、w_cas_tex）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E), a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70).
Effect: A FLOWER BURST HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 6 squares across; 2 a five-petal flower of pink light 12 squares across (one petal straight up, the rest mirrored) with a white core; 3 the petals opening wider and breaking into pink and teal sparks; 4 fading sparks with violet specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `neeko_fx_q_seed.png`：Q 盛开花种：扔出去的种子（弹道），4 帧

她扔出去的一颗花种：圆圆的种子（青绿色带紫色花纹，像一颗花苞），后面拖一小段粉色光尾（参考 neeko_base_q_trail、q_leadingedge）。**朝右飞、上下对称**，4 帧（种子转一下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf ramp (#E8FFD8, #A6E87A, #5CB848, #2E7A34, #16401E), a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70), a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54).
Effect: A FLOWER SEED, 4 frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round seed bud 4 squares across at the right (teal-green with a violet swirl, the swirl turning a quarter each frame), a short pink light trail 4 squares long behind it. SOLID OBJECTS (the seed, petals, leaves, the barbs' vines) have a 1-square near-black outline; light, sparks, rings and shockwaves have none.
Layout: one horizontal row of 4 equal 8:6 cells, image size 512x96 (each cell 128x96, 16 px a square); the seed's middle on the cell's middle row, 2 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `neeko_fx_q_burst.png`：Q 种子落地第一次炸开，5 帧

种子落地炸开成一大朵花：地上一圈粉色的花瓣光环（从斜上方看的椭圆），中间一朵大花一下子绽开、往上爆出花瓣和青色火花（参考 neeko_base_q_aoe_flower_erode、q_aoe_petal、q_aoe_ring、q_tar_splash）。范围半径约 22 格：椭圆约 46 格宽、16 格高。**左右对称**，5 帧：落地、绽开最大、花瓣飞散、余光、消失。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a petal ramp (#FFF4F8, #FFC8DC, #FF86B0, #F2507E, #B82858), a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E), a leaf ramp (#E8FFD8, #A6E87A, #5CB848, #2E7A34, #16401E).
Effect: A BLOOMING BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small pink flash on the ground in the middle; 2 a big flower of pink light opening upward from the middle (8 petals, 20 squares tall, white core) over a flat pink ring on the ground (an ellipse 46 squares wide and 16 tall, only its rim lit); 3 the flower bursting into flying petals (solid petals with outlines) and teal sparks, the ground ring brightest; 4 petals falling, the ring fading; 5 a few last petals and specks.
Layout: one horizontal row of 5 equal 50:26 cells, image size 4000x416 (each cell 800x416, 16 px a square); the ground ellipse's middle 9 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `neeko_fx_q_bloom.png`：Q 再次盛开（命中英雄后，第二、三次），4 帧

种子炸到英雄后又盛开一次：比第一次小一点、颜色偏紫，花瓣往上翻一下。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70), a petal ramp (#FFF4F8, #FFC8DC, #FF86B0, #F2507E, #B82858).
Effect: A SECOND BLOOM, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): like the blooming burst but smaller and more violet: 1 a violet-pink flash in the middle of a flat ring (an ellipse 40 squares wide and 14 tall, only its rim lit); 2 a flower of violet-pink light 16 squares tall opening upward; 3 petals flying out; 4 fading petals and specks.
Layout: one horizontal row of 4 equal 44:22 cells, image size 2816x352 (each cell 704x352, 16 px a square); the ground ellipse's middle 8 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `neeko_fx_q_hit.png`：Q 炸中的敌人，3 帧

被花种炸中：粉色的星形一闪，几片小花瓣飞散（参考 neeko_base_q_hit_tar）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a petal ramp (#FFF4F8, #FFC8DC, #FF86B0, #F2507E, #B82858).
Effect: A PETAL HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink four-pointed star 7 squares across with a white core; 2 the star breaking up, 4 small petals flying out at mirrored places; 3 only falling petals.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `neeko_fx_e_barbs.png`：E 缠结倒刺：滚出去的倒刺团（弹道），4 帧

一团缠在一起的紫色刺藤，滚着往前飞：中间一团紫红色的藤球，伸出一圈小尖刺，外面一圈旋转的粉色光带，后面拖一道紫色尾迹（参考 neeko_base_e_mis_mesh、e_mis_swirls、e_spin、e_trail）。**朝右飞、上下对称**，4 帧（转一圈）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70), a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a leaf ramp (#E8FFD8, #A6E87A, #5CB848, #2E7A34, #16401E).
Effect: A ROLLING TANGLE OF BARBS, 4 frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a ball of twisted violet-magenta thorny vines 8 squares across at the right, short thorn tips sticking out all round (rotating a quarter each frame), a pink light swirl round it, a violet trail 5 squares long behind it. SOLID OBJECTS (the seed, petals, leaves, the barbs' vines) have a 1-square near-black outline; light, sparks, rings and shockwaves have none.
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); the ball's middle on the cell's middle row, 5 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `neeko_fx_e_hit.png`：E 打中的敌人，3 帧

倒刺打中：一圈紫色的刺爆开，中间粉色一闪（参考 neeko_base_e_ring、e_circle_01）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70), a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54).
Effect: A THORN HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink flash 6 squares across ringed by 8 short violet thorns pointing out; 2 the thorns flying further out, the flash fading; 3 fading violet specks.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `neeko_fx_e_bound.png`：E 禁锢（循环），4 帧

被禁锢的英雄脚下：几根紫色的刺藤从地上缠住双脚，藤上开着小粉花，一闪一闪（参考 neeko_base_e_stun_tex、e_empowered_stun_tex）。**中间目标的脚的位置留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70), a leaf ramp (#E8FFD8, #A6E87A, #5CB848, #2E7A34, #16401E), a petal ramp (#FFF4F8, #FFC8DC, #FF86B0, #F2507E, #B82858).
Effect: A ROOT OF THORNY VINES, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): violet thorny vines rising from the ground at both sides of the middle and curling round where the target's legs are (left and right mirrored), 12 squares tall, two tiny pink flowers on them, a faint pink glow on the ground under them pulsing in turn. SOLID OBJECTS (the seed, petals, leaves, the barbs' vines) have a 1-square near-black outline; light, sparks, rings and shockwaves have none.
Layout: one horizontal row of 4 equal 22:14 cells, image size 1408x224 (each cell 352x224, 16 px a square); the vines' roots on the cell's bottom row; the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (only its legs reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `neeko_fx_r_charge.png`：R 怒放：蓄力（身上），6 帧

蓄力 0.75 秒：她周围收拢一圈粉紫色的光（像花苞合起来），地上一圈花瓣光环越来越亮，粉色和青色的光点往她身上聚（参考 neeko_base_r_bubblearound、r_noisebubble、r_enemy_tendrils）。**中间她的身体位置留空**（只画外圈），**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70), a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E).
Effect: A CHARGING BUD, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a closing bud of pink-violet light round an upright body (only its outline and sparse inner streaks: 34 squares wide, 46 tall), a flat pink ring on the ground round her feet (an ellipse 32 squares wide and 8 tall), pink and teal motes drawn inward from the cell's edges; frame by frame the bud closes tighter and the ring brightens, frame 6 brightest. The middle EMPTY where the body is.
Layout: one horizontal row of 6 equal 40:50 cells, image size 3840x800 (each cell 640x800, 16 px a square); she stands in the middle, not drawn: an upright girl 20 squares wide and 40 tall (her feet on the cell's bottom row, 3 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `neeko_fx_r_jump.png`：R 跳起（身上），4 帧

跳起的那一下：脚下一圈粉色的冲击波往外推开，几道往上的光线（她被击飞周围的人）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E).
Effect: A SPRING-UP BLAST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a bright pink flash at the bottom middle; 2 a flat pink shockwave ring spreading on the ground (an ellipse 30 squares wide and 8 tall) with 6 short upward light streaks; 3 the ring 38 wide, the streaks higher; 4 fading pink and teal specks.
Layout: one horizontal row of 4 equal 40:24 cells, image size 2560x384 (each cell 640x384, 16 px a square); the ring's middle 4 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `neeko_fx_r_land.png`：R 落地怒放（地上），6 帧

落地的大爆发：地上一大圈粉紫色的花环（从斜上方看的椭圆，半径约 40 格：约 84 格宽、28 格高），一朵巨大的光之花从中间猛地绽开，花瓣、青色火花向四周炸开（参考 neeko_base_r_aoe_waves、r_circle_tex、r_prismflash、r_spotlight）。**左右对称**，6 帧：落地一闪、花环最亮、大花绽开、花瓣飞散、余光、消失。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70), a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E), a petal ramp (#FFF4F8, #FFC8DC, #FF86B0, #F2507E, #B82858), gold flower hearts (#FFFFFF, #FFF2B0, #FFD24A, #E89A1E) as accents only.
Effect: A HUGE BLOSSOM BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash in the middle of the ground; 2 a flat ring of pink-violet light on the ground (an ellipse 84 squares wide and 28 tall, only its rim and a few petal shapes on it lit) at its brightest; 3 a giant flower of prismatic pink-violet light opening upward from the middle (10 petals, 34 squares tall, white core, a gold heart); 4 the flower bursting, solid petals and teal sparks flying out over the whole ellipse; 5 petals falling, the ring fading; 6 last petals and specks.
Layout: one horizontal row of 6 equal 90:44 cells, image size 8640x704 (each cell 1440x704, 16 px a square); the ground ellipse's middle 15 squares above the cell's bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `neeko_fx_r_hit.png`：R 落地打中的敌人（晕眩），4 帧

被落地炸中、晕眩：粉色的爆开一闪，头上转起一圈小花瓣（晕眩）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a petal ramp (#FFF4F8, #FFC8DC, #FF86B0, #F2507E, #B82858).
Effect: A STUNNING HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink burst 10 squares across with a white core in the lower middle; 2 the burst fading, a ring of 5 tiny petals appearing at the top; 3 the petal ring turning; 4 the petals fading.
Layout: one horizontal row of 4 equal 16:18 cells, image size 1024x288 (each cell 256x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `neeko_fx_w_haste.png`：W 第三下普攻后的加速（循环），4 帧

加速的 1 秒：她脚下一圈青色和粉色的小光点，往后飘。**中间留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E), a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54).
Effect: A HASTE RING, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ring of tiny teal and pink light motes on the ground round her feet (an ellipse 22 squares wide and 6 tall), the motes winking in turn; the middle EMPTY.
Layout: one horizontal row of 4 equal 26:8 cells, image size 1664x128 (each cell 416x128, 16 px a square); the ellipse's middle on the cell's middle; she stands in the middle, not drawn: an upright girl 20 squares wide and 40 tall (only her feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `neeko_fx_p_poof.png`：被动 天生幻魅：变身 / 现形（附加包），5 帧

她变成队友、或者现形变回自己的那一下：一团彩色的烟雾和花瓣一下罩住她又散开，几颗青色和粉色的星星闪光（参考 neeko_base_p_swirls、p_texture、z_flash、z_colors）。**左右对称**，5 帧。这一张盖在人身上（是变身的烟），可以遮住身体。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink magic ramp (#FFFFFF, #FFE0F2, #FF9AD6, #FF4FB4, #D21E8A, #7E0C54), a teal-cyan spark ramp (#F0FFFC, #A8FFF0, #4FE8D2, #1EB4A8, #0E6E6E), a violet ramp (#F4DCFF, #C89AF4, #9258E0, #6230B0, #3A1A70), a petal ramp (#FFF4F8, #FFC8DC, #FF86B0, #F2507E, #B82858).
Effect: A TRANSFORMATION PUFF, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a few pink and teal sparkles round an upright body; 2 a thick puff of pink-violet swirling smoke (round clouds, 28 squares wide and 40 tall) covering the body, petals in it; 3 the puff at its fullest with teal star glints; 4 the puff breaking into wisps and petals drifting out; 5 last sparkles.
Layout: one horizontal row of 5 equal 34:46 cells, image size 2720x736 (each cell 544x736, 16 px a square); she stands in the middle, not drawn: an upright girl 20 squares wide and 40 tall (her feet on the cell's bottom row, 3 squares up). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `neeko_fx_a_bolt` | view_projectiles `league_neeko_a_bolt`（随飞行方向转；上下对称） | 10 × 6 |
| `neeko_fx_a_hit` | view_effects `league_neeko_a_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `neeko_fx_w_hit` | view_effects `league_neeko_w_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `neeko_fx_q_seed` | view_projectiles `league_neeko_q_seed`（随飞行方向转；上下对称） | 8 × 6 |
| `neeko_fx_q_burst` | view_effects `league_neeko_q_burst`（地上，不跟随，z -1；左右对称） | 50 × 26 |
| `neeko_fx_q_bloom` | view_effects `league_neeko_q_bloom`（地上，不跟随，z -1；左右对称） | 44 × 22 |
| `neeko_fx_q_hit` | view_effects `league_neeko_q_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `neeko_fx_e_barbs` | view_projectiles `league_neeko_e_barbs`（随飞行方向转；上下对称） | 14 × 10 |
| `neeko_fx_e_hit` | view_effects `league_neeko_e_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `neeko_fx_e_bound` | view_buffs `league_neeko_e_bound`（跟着目标，循环，z 3；左右对称） | 22 × 14 |
| `neeko_fx_r_charge` | view_effects `league_neeko_r_charge`（她身上，z 3；左右对称） | 40 × 50 |
| `neeko_fx_r_jump` | view_effects `league_neeko_r_jump`（她身上，z 3；左右对称） | 40 × 24 |
| `neeko_fx_r_land` | view_effects `league_neeko_r_land`（她身上落地处，z -1；左右对称） | 90 × 44 |
| `neeko_fx_r_hit` | view_effects `league_neeko_r_hit`（跟随目标，z 2；左右对称） | 16 × 18 |
| `neeko_fx_w_haste` | view_buffs `league_neeko_w_haste`（跟着她，循环，z -1；左右对称） | 26 × 8 |
| `neeko_fx_p_poof` | view_effects `league_neeko_p_poof`（她身上，z 3；左右对称） | 34 × 46 |

- 两张表：`asset/league/effects/league_neeko_fx`（小的）和 `league_neeko_big`（q_burst、q_bloom、r_charge、r_jump、r_land、p_poof），tag = 名字（build_neeko.py 的 views）。p_poof 只在附加包副本里绑定（被动现形 / 变身时 `play_view_effect`）。
- 弹道（a_bolt、q_seed、e_barbs）断言上下对称；其余断言左右对称；r_charge、r_jump、w_haste、p_poof 跟随她。
- 用 `pixel_1x/` 切格（import_naafiri_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
