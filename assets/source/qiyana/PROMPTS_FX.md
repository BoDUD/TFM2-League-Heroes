# 元素女皇 奇亚娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 22 张特效图。** 造型（`design/qiyana_designs.png`）：3/4 正面朝右的高傲女王——暖棕皮肤、银白长发、金王冠和白玉尖冠、青绿抹胸短裙、深色紧身裤，远侧的手握着竖在身边的大圆环刀刃。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），40 格高、34 格宽（连圆环）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/qiyana_size.png`：她放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奇亚娜自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她自己的光是金色、带青绿色的宝石点缀**；三种元素——**草丛是绿色的草叶**、**河流是蓝色的水和冰**、**岩石是琥珀棕色的石块和尘土**；大招三种一起。
> - **特效要亮**：每道光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **光、水、草叶、尘土、光环、冲击波都没有黑描边**；**实物**（碎石块、冰晶）有 1 格近黑描边。
> - **围着人的画面只画外圈、脚下或腰间，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`r_wave`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**画进她自己帧里的**（`q_swing`、`q_w`、`q_r`、`q_g`、`r_swing`、`r_burst`）**朝右画，不用对称**（跟着她的身体一起翻转）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `qiyana_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/qiyana_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/qiyana_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「凌人贵气」 | 挥圆环砍；对每个敌人的第一下额外伤害；武器附了元素时普攻多一点魔法伤害 | `a_hit` · `p_hit` · `w_hit` |
| 技能 1 = Q「以绪塔尔之锋」 | 圆环往前横扫；附了元素就用掉它：河流定身减速、岩石加伤、草丛伪装加速 | `q_swing` · `q_w` · `q_r` · `q_g` · `q_hit` · `q_w_hit` · `q_r_hit` · `q_g_hit` · `q_slow` · `q_haste` |
| 技能 2 = E「天纵之勇」+ W「方圆塑令」 | 突进到敌人身上砍一下，落地给武器附一种元素，刷新 Q | `e_hit` · `w_on` · `el_g` · `el_w` · `el_r` |
| 大招「惊才绝景」 | 圆环抡一大圈砸地，冲击波往前推，打中的击退再眩晕 | `r_swing` · `r_burst` · `r_wave` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、水、草叶、尘土、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**（实物——碎石块、冰晶——有 1 格近黑描边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 她的金光：`#FFFFFF`、`#FFF4C8`、`#FFD870`、`#F0B030`、`#B87818`、`#6E4210`；
  - 宝石青绿（点缀）：`#F0FFFC`、`#A8F4E8`、`#40D8C8`、`#18A098`、`#0E6466`；
  - 草丛（绿）：`#F4FFD8`、`#B8F070`、`#6CCB3A`、`#3A9028`、`#1E5A1C`；
  - 河流（蓝，水和冰）：`#FFFFFF`、`#D0F4FF`、`#78D0FF`、`#3A90E8`、`#1C52B0`、`#0E2A6A`；
  - 岩石（琥珀棕，石块和尘土）：`#FFE8B8`、`#E0B070`、`#B07C40`、`#7A5028`、`#4A3018`、`#2A1C10`；
- 打中、爆发居中画，不旋转；地面和腰间的圈是从斜上方看的椭圆（宽是高的 3–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（22 张）

22 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 横扫约 34000，大招冲击波 60000）。

### 1. `qiyana_fx_a_hit.png`：普攻：圆环砍中目标，3 帧

圆环砍中：一道金色的弧形刃光一闪，芯是白的，带两三点青绿色的火星（参考 ba_hit_tar_sharp、z_slash）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), teal jewel accents (#F0FFFC, #A8F4E8, #40D8C8, #18A098, #0E6466).
Effect: A BLADE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two short curved gold slash arcs crossing in an X 9 squares across with a white core; 2 the arcs fading, a few gold and teal sparks flying out; 3 fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `qiyana_fx_w_hit.png`：附魔普攻的额外伤害，3 帧

武器附了元素时普攻多打的一下：一小团亮光，绕着三颗小光点——绿（草）、蓝（水）、琥珀（石），不分元素都用这一张。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C), a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A), a rock amber-brown stone-and-dust ramp (#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10).
Effect: AN ENCHANTED STRIKE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small gold star flash 5 squares across with a white core; 2 three tiny motes bursting out of it - one green, one blue, one amber; 3 the motes fading.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `qiyana_fx_p_hit.png`：被动 凌人贵气：第一下的额外伤害，4 帧

对一个敌人的第一下：目标头上方亮起一顶小小的金色王冠（嵌一块青绿宝石，像她的头冠），往下一压碎成金光。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), teal jewel accents (#F0FFFC, #A8F4E8, #40D8C8, #18A098, #0E6466).
Effect: A ROYAL MARK, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small gold crown (a row of 5 points, a teal gem in the middle, 9 squares wide) appearing in the cell's upper half; 2 brightest, a white glint on it; 3 the crown pressing down and breaking into gold shards; 4 the shards fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `qiyana_fx_w_on.png`：E 落地附魔（方圆塑令）：武器吸取元素，4 帧

突进落地、圆环附上元素的一刻：她脚下一圈金色光环亮起，一股金青色的光带绕着她旋上去，夹着三色的小光点（绿、蓝、琥珀）。**中间她的身体位置留空**（只画外圈），**左右对称**，4 帧（参考 w_gainele_tex、w_flares_03）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), teal jewel accents (#F0FFFC, #A8F4E8, #40D8C8, #18A098, #0E6466), a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C), a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A), a rock amber-brown stone-and-dust ramp (#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10).
Effect: AN ENCHANT SWIRL, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat gold ground ellipse 26 squares wide and 6 tall lighting up at the bottom; 2 two gold-teal light ribbons rising from it at both sides; 3 the ribbons high at both sides, small green, blue and amber motes along them; 4 fading motes. The middle EMPTY where her body is.
Layout: one horizontal row of 4 equal 30:34 cells, image size 1920x544 (each cell 480x544, 16 px a square); the ellipse on the cell's bottom rows; she stands in the middle, not drawn: 40 squares from her crest to her soles, her body about 14 squares wide (her soles on the cell's bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `qiyana_fx_q_swing.png`：Q 以绪塔尔之锋（没有元素）：圆环横扫，4 帧

没有元素时的 Q：圆环往前横扫出一道宽宽的金色月牙刃光（芯白，边上一点青绿），从她身前左上扫到右下。**朝右画，不对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), teal jewel accents (#F0FFFC, #A8F4E8, #40D8C8, #18A098, #0E6466).
Effect: A SWEEPING CRESCENT, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): 1 the start of a thick gold crescent at her front, upper left; 2 the whole crescent sweeping out to the right, 30 squares long and 8 thick at its middle, a white leading edge, a thin teal rim; 3 the crescent thinning at the right; 4 gold sparks fading at its end.
Layout: one horizontal row of 4 equal 40:26 cells, image size 2560x416 (each cell 640x416, 16 px a square); she stands at the cell's LEFT edge, not drawn (her front - the side she faces - at about 8 squares from the left edge, her soles on the cell's bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `qiyana_fx_q_w.png`：Q 河流：水与冰的横扫，4 帧

河流元素的 Q：横扫出一道蓝色的水浪月牙，浪尖上凝出几片白蓝色的冰晶（参考 q_iceshards、q_water_tar_icetex）。**朝右画，不对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A).
Effect: A WATER CRESCENT, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): 1 a curl of blue water starting at her front; 2 a thick crescent wave of blue water sweeping out to the right, 34 squares long, white spray on its crest; 3 the wave freezing at its end into a few pale blue ice shards; 4 the shards and droplets falling. SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none.
Layout: one horizontal row of 4 equal 44:26 cells, image size 2816x416 (each cell 704x416, 16 px a square); she stands at the cell's LEFT edge, not drawn (her front - the side she faces - at about 8 squares from the left edge, her soles on the cell's bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `qiyana_fx_q_r.png`：Q 岩石：地刺破土，5 帧

岩石元素的 Q：圆环砸向前方的地面，一排琥珀棕色的尖石从地里接连冒出，越往前越高，扬起尘土（参考 q_earth_break、w_mis_rock_spikes）。**朝右画，不对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rock amber-brown stone-and-dust ramp (#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10), a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210).
Effect: A ROW OF ROCK SPIKES, 5 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): 1 a gold flash and cracks on the ground at her front; 2 three jagged amber-brown stone spikes bursting up in a row to the right, growing taller (6, 10 and 14 squares); 3 all spikes up, dust clouds at their feet, stone chips flying; 4 the spikes crumbling; 5 dust and falling chips. SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none.
Layout: one horizontal row of 5 equal 44:28 cells, image size 3520x448 (each cell 704x448, 16 px a square); the spikes stand on the cell's bottom row; she stands at the cell's LEFT edge, not drawn (her front - the side she faces - at about 8 squares from the left edge, her soles on the cell's bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `qiyana_fx_q_g.png`：Q 草丛：草叶刃风，4 帧

草丛元素的 Q：横扫出一阵绿色的风，卷着一片片细长的草叶刃往前飞（参考 q_mis_grass_bw、z_grass）。**朝右画，不对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C), a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210).
Effect: A GUST OF GRASS BLADES, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): 1 a green swirl starting at her front; 2 a crescent of green wind sweeping out to the right, 34 squares long, full of long thin grass blades and leaves; 3 the blades flying on ahead of it; 4 a few leaves fluttering away.
Layout: one horizontal row of 4 equal 44:26 cells, image size 2816x416 (each cell 704x416, 16 px a square); she stands at the cell's LEFT edge, not drawn (her front - the side she faces - at about 8 squares from the left edge, her soles on the cell's bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `qiyana_fx_q_hit.png`：Q 打中（没有元素），3 帧

横扫打中：一道横的金色刃光带一圈小火星。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), teal jewel accents (#F0FFFC, #A8F4E8, #40D8C8, #18A098, #0E6466).
Effect: A SWEEP HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a horizontal gold slash streak 11 squares long with a white core; 2 it breaking into gold and teal sparks flying out to both sides; 3 fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `qiyana_fx_q_w_hit.png`：Q 河流打中：冰定身，4 帧

被河流 Q 打中、定在原地：水花溅开，目标脚下冻出一圈尖尖的冰晶把脚锁住（0.5 秒）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A).
Effect: A FREEZING SPLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a blue water splash bursting up in the middle; 2 the water falling, a ring of pale blue ice shards growing up round the bottom (where the feet are), 6 squares tall; 3 the ice ring full, white glints on it; 4 the ice cracking into small shards. SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none.
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); the ice ring on the cell's bottom rows; the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (only its lower 16 squares are in the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `qiyana_fx_q_r_hit.png`：Q 岩石打中，4 帧

被岩石 Q 打中：一团琥珀色的石块迸开，尘土四散，中间一闪金光。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rock amber-brown stone-and-dust ramp (#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10), a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210).
Effect: A ROCK BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold flash with a white core in the middle; 2 amber-brown stone chips (2-3 squares each) bursting out to both sides with dust; 3 the chips farther, the dust spreading; 4 dust fading. SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `qiyana_fx_q_g_hit.png`：Q 草丛打中，3 帧

被草丛 Q 打中：几片锋利的草叶从两边划过，留下两道绿色的刃痕。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C).
Effect: A LEAF CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two green slash streaks crossing in an X with a pale core, leaves at their ends; 2 the streaks fading, 4 leaves fluttering out to both sides; 3 fading leaves.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `qiyana_fx_e_hit.png`：E 天纵之勇：突进砍中，3 帧

突进砍中：一个大的金色 X 刃光，中间一颗青绿色的星点。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), teal jewel accents (#F0FFFC, #A8F4E8, #40D8C8, #18A098, #0E6466).
Effect: A DASH STRIKE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big gold X of two slash streaks 12 squares across, a white core and a teal star in the middle; 2 the X fading, gold sparks flying out; 3 fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `qiyana_fx_r_swing.png`：大招 惊才绝景：圆环抡一大圈，4 帧

大招起手：她把圆环抡过头顶往前一挥，留下一道几乎一整圈的金色刃光，青绿色的边，往前（右）收尾最亮。**朝右画，不对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), teal jewel accents (#F0FFFC, #A8F4E8, #40D8C8, #18A098, #0E6466).
Effect: A GREAT CIRCLE SWING, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): 1 a gold arc starting behind her at the upper left; 2 the arc sweeping over the top, a thick gold ring two thirds round, white leading edge, teal rim; 3 the arc coming down in front at the right, brightest there; 4 gold sparks fading at the front.
Layout: one horizontal row of 4 equal square cells, image size 2304x576 (each cell 576x576, 16 px a square); she stands in the middle of the cell, not drawn (40 squares tall: her head reaches the top rows), her soles on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `qiyana_fx_r_burst.png`：大招：冲击波在她脚前爆开，4 帧

圆环砸地、冲击波出发的一刻：她身前的地面炸开，石块、水花、草叶三样一起往前（右）喷出去（参考 r_cas_wave、r_explode_ground）。**朝右画，不对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), a rock amber-brown stone-and-dust ramp (#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10), a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A), a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C).
Effect: A GROUND BLAST, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): 1 a gold flash on the ground at her front; 2 the ground bursting forward: amber stone chips, blue water spray and green grass blades thrown up and to the right in a fan 14 squares tall; 3 the fan farther right, dust behind it; 4 falling bits and dust. SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none.
Layout: one horizontal row of 4 equal 40:20 cells, image size 2560x320 (each cell 640x320, 16 px a square); the blast on the cell's bottom rows; she stands at the cell's LEFT edge, not drawn (her front - the side she faces - at about 8 squares from the left edge, her soles on the cell's bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `qiyana_fx_r_wave.png`：大招的冲击波（飞行），4 帧

往前推进的冲击波：一道竖着的弧形波前（像一面往前推的墙），前沿金白色，里面混着碎石、水花和草叶，后面拖着尘土（参考 r_cas_wave、r_edge2、r_mis_water_freeze、r_windwall_rocks_tex）。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), a rock amber-brown stone-and-dust ramp (#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10), a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A), a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C).
Effect: A ROLLING SHOCKWAVE, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a tall curved wave front (a ')' shape 20 squares tall at the right), its leading edge gold-white, inside it tumbling amber stone chips, blue water spray and green grass blades (placed square for square the same above and below the middle line), a trail of dust and spray 14 squares long behind it on the left; the bits tumble a little each frame. SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none.
Layout: one horizontal row of 4 equal 32:22 cells, image size 2048x352 (each cell 512x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `qiyana_fx_r_hit.png`：大招打中：击退后眩晕，4 帧

被冲击波打中：一大团爆开——金光、石块、冰晶、草叶一起迸出（三种元素一起引爆）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a royal gold light ramp (#FFFFFF, #FFF4C8, #FFD870, #F0B030, #B87818, #6E4210), a rock amber-brown stone-and-dust ramp (#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10), a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A), a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C).
Effect: AN ELEMENTAL BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big gold flash 12 squares across with a white core; 2 a ring bursting out of it: amber stone chips, pale blue ice shards and green leaves, placed in mirror pairs; 3 the ring wider, dust and spray; 4 fading bits. SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `qiyana_fx_el_g.png`：带着草丛元素（循环），4 帧

武器附了草丛：她腰部一圈有三四片绿色的小叶子绕着转（前面的叶子亮、后面的暗）。**中间她的身体位置留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C).
Effect: ORBITING LEAVES, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): four small green leaves (2-3 squares) on a flat ellipse 30 squares wide and 8 tall round her waist, placed in mirror pairs, stepping round it each frame, the front ones brighter; the middle EMPTY.
Layout: one horizontal row of 4 equal 34:12 cells, image size 2176x192 (each cell 544x192, 16 px a square); the ellipse on the cell's middle; she stands in the middle, not drawn: 40 squares from her crest to her soles, her body about 14 squares wide (the cell is at her waist). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `qiyana_fx_el_w.png`：带着河流元素（循环），4 帧

武器附了河流：她腰部一圈有几颗蓝色的水珠绕着转，带一点白色的水光。**中间留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A).
Effect: ORBITING WATER DROPS, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): four blue water drops (2 squares, a white glint) on a flat ellipse 30 squares wide and 8 tall round her waist, placed in mirror pairs, stepping round it each frame, the front ones brighter, a thin stream of droplets between them; the middle EMPTY.
Layout: one horizontal row of 4 equal 34:12 cells, image size 2176x192 (each cell 544x192, 16 px a square); the ellipse on the cell's middle; she stands in the middle, not drawn: 40 squares from her crest to her soles, her body about 14 squares wide (the cell is at her waist). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `qiyana_fx_el_r.png`：带着岩石元素（循环），4 帧

武器附了岩石：她腰部一圈有几块琥珀色的小石块绕着转，带一点尘土。**中间留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rock amber-brown stone-and-dust ramp (#FFE8B8, #E0B070, #B07C40, #7A5028, #4A3018, #2A1C10).
Effect: ORBITING STONES, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): four small amber-brown stone chips (2-3 squares) on a flat ellipse 30 squares wide and 8 tall round her waist, placed in mirror pairs, stepping round it each frame, the front ones brighter, a little dust behind each; the middle EMPTY. SOLID BITS (stone chips, ice shards) have a 1-square near-black outline; light, water, leaves and dust have none.
Layout: one horizontal row of 4 equal 34:12 cells, image size 2176x192 (each cell 544x192, 16 px a square); the ellipse on the cell's middle; she stands in the middle, not drawn: 40 squares from her crest to her soles, her body about 14 squares wide (the cell is at her waist). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `qiyana_fx_q_slow.png`：河流 Q 之后减速（循环），4 帧

被减速的敌人：脚下一小片蓝色的水洼，冒着白色的寒气。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river blue water-and-ice ramp (#FFFFFF, #D0F4FF, #78D0FF, #3A90E8, #1C52B0, #0E2A6A).
Effect: A COLD PUDDLE, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat blue puddle ellipse 16 squares wide and 4 tall on the cell's bottom rows, two or three small white frost wisps rising from it in turn.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall (only its feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `qiyana_fx_q_haste.png`：草丛 Q 之后加速（循环），4 帧

草丛 Q 的伪装加速：她脚下有一圈细细的绿色风痕，几片草叶贴地打转。**中间留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grass-green ramp (#F4FFD8, #B8F070, #6CCB3A, #3A9028, #1E5A1C).
Effect: A GRASS WIND AT THE FEET, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin green wind ellipse 26 squares wide and 6 tall on the cell's bottom rows (only its rim drawn), three small grass blades whirling along it in mirror pairs; the middle EMPTY.
Layout: one horizontal row of 4 equal 30:10 cells, image size 1920x160 (each cell 480x160, 16 px a square); she stands in the middle, not drawn: 40 squares from her crest to her soles, her body about 14 squares wide (only her feet reach the cell). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `qiyana_fx_a_hit` | view_effects `league_qiyana_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `qiyana_fx_w_hit` | view_effects `league_qiyana_w_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `qiyana_fx_p_hit` | view_effects `league_qiyana_p_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `qiyana_fx_w_on` | view_effects `league_qiyana_w_on`（她身上，z 3；左右对称） | 30 × 34 |
| `qiyana_fx_q_swing` | 画进她的 skill 帧（朝右，不对称） | 40 × 26 |
| `qiyana_fx_q_w` | 画进她的 skill_w 帧（朝右，不对称） | 44 × 26 |
| `qiyana_fx_q_r` | 画进她的 skill_r 帧（朝右，不对称） | 44 × 28 |
| `qiyana_fx_q_g` | 画进她的 skill_g 帧（朝右，不对称） | 44 × 26 |
| `qiyana_fx_q_hit` | view_effects `league_qiyana_q_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `qiyana_fx_q_w_hit` | view_effects `league_qiyana_q_w_hit`（跟随目标，z 2；左右对称） | 18 × 16 |
| `qiyana_fx_q_r_hit` | view_effects `league_qiyana_q_r_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `qiyana_fx_q_g_hit` | view_effects `league_qiyana_q_g_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `qiyana_fx_e_hit` | view_effects `league_qiyana_e_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `qiyana_fx_r_swing` | 画进她的 ult 帧（朝右，不对称） | 36 × 36 |
| `qiyana_fx_r_burst` | 画进她的 ult 帧（朝右，不对称） | 40 × 20 |
| `qiyana_fx_r_wave` | view_projectiles `league_qiyana_r_wave`（随飞行方向转；上下对称） | 32 × 22 |
| `qiyana_fx_r_hit` | view_effects `league_qiyana_r_hit`（跟随目标，z 2；左右对称） | 20 × 20 |
| `qiyana_fx_el_g` | view_buffs `league_qiyana_el_g`（跟着她，循环，z 3；左右对称） | 34 × 12 |
| `qiyana_fx_el_w` | view_buffs `league_qiyana_el_w`（跟着她，循环，z 3；左右对称） | 34 × 12 |
| `qiyana_fx_el_r` | view_buffs `league_qiyana_el_r`（跟着她，循环，z 3；左右对称） | 34 × 12 |
| `qiyana_fx_q_slow` | view_buffs `league_qiyana_q_slow`（跟着目标，循环，z 3；左右对称） | 18 × 8 |
| `qiyana_fx_q_haste` | view_buffs `league_qiyana_q_haste`（跟着她，循环，z -1；左右对称） | 30 × 10 |

- 两张表：`asset/league/effects/league_qiyana_fx`（小的）和 `league_qiyana_big`（q_swing、q_w、q_r、q_g、r_swing、r_burst、r_wave），tag = 名字（build_qiyana.py 的 views）。
- 弹道（r_wave）断言上下对称；朝前的（q_swing、q_w、q_r、q_g、r_swing、r_burst）用 tools/fix/bake_caster_fx.py 画进她的帧（Q 的四种各一份 skill 动作：skill / skill_w / skill_r / skill_g，build_qiyana.py 里的 cview 换成对应的 CasterAnimation）；其余断言左右对称；w_on、el_*、q_haste 跟随她。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
