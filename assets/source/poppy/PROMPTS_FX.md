# 圣锤之毅 波比：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型和动作已定（`design/poppy_idle.png`：3/4 正面朝右的约德尔女孩，浅蓝皮肤、浅金色双马尾、紫红眼睛、红围巾、深紫褐皮甲和铜金甲片，身边竖着一把灰钢锤头、红锤柄的巨锤）。她在游戏里是**高清**的（每个游戏格子里 1.3×1.3 个细像素），42 格高、34 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/poppy_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/poppy_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里波比自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的光是暖金色 / 琥珀色**（圆盾、护盾、光环、锤子的光），**砸地是棕色的尘土和碎石**，**撞墙眩晕是紫金色的闪光**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **两张弹道图（`p_buckler`、`r_wave`）画成朝右飞、上下对称**：游戏会按飞的方向把它转过去，往左飞时转半圈，上下对称才不会倒过来。**其余所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `poppy_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/poppy_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/poppy_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「钢铁大使」（在普攻里） | 每隔一段时间下一次普攻扔出圆盾，圆盾弹回来落在地上，她走过去捡起来得到护盾 | `p_buckler` · `p_lie` · `p_pick` · `p_shown` |
| 普攻 | 锤子横扫 | `a_hit` |
| 技能 1 = Q「圣锤猛击」 | 锤子砸地，地面裂开减速，1 秒后再炸一次 | `q_slam` · `q_crack` · `q_burst` · `q_hit` |
| W「坚定风采」（跟着她的其他技能自动开） | 加移速，身边 2 秒的光环挡下冲进来的突进 | `w_cast` · `w_on` · `w_block` |
| 技能 2 = E「英勇冲锋」 | 冲向目标撞上去并推着走，撞到墙上就眩晕 | `e_hit` · `e_wall` · `e_stun` |
| 大招「持卫的裁决」 | 蓄力后抡锤推出冲击波，把敌人打飞很远；近身时点放砸地击飞 | `r_charge` · `r_wave` · `r_tap` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、毒液、毒雾、毒泡、光环、光波都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：石壳、石屑可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 暖金色的光（圆盾、护盾、光环、锤击）：`#FFFFFF`、`#FFF4C8`、`#FFDA6A`、`#F2AE34`、`#C77A1E`、`#7A4614`；
  - 钢铁（圆盾的盾面）：`#FFFFFF`、`#E4E6EA`、`#B8BCC6`、`#8A8F9C`、`#5E6270`、`#383B46`；
  - 棕色尘土和碎石：`#F4E6C8`、`#D8BC8C`、`#B08E5E`、`#866640`、`#5C4428`、`#3A2A18`；
  - 紫色闪光（撞墙眩晕）：`#FFFFFF`、`#F2D8FF`、`#C890FF`、`#9A5AE6`、`#6A34B4`、`#3E1C70`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 的半径 18000，W 光环的半径 35000，大招点放的半径 28000，大招冲击波宽 18000）。

### 1. `poppy_fx_p_buckler.png`：被动钢铁大使：扔出去的圆盾（弹道），4 帧（循环）

她扔出去的圆盾：一面**圆形的小盾牌**，铁灰色的盾面，**金色的盾边**，中间一个金色的圆钉，飞的时候在转（每帧盾面上的亮光转一点），后面拖一小段金色的光尾（参考 P_Shield_v2、P_shield_trail、P_mis_edge）。**上下对称**（游戏按飞的方向转它）。约 12 × 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a steel ramp (#FFFFFF, #E4E6EA, #B8BCC6, #8A8F9C, #5E6270, #383B46).
Effect: A SPINNING ROUND BUCKLER in flight, 4 frames, a seamless loop, pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight: flying left it is turned half round and must not stand upside down): a round shield 9 squares across seen face-on - a steel-grey face, a 1-square bright GOLD rim, a 2x2 gold boss in the middle (a 1-square dark edge round the rim: it is solid metal) - a short gold light trail 3 squares behind it (to the left); each frame the white glint on its face moves a quarter round the boss.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `poppy_fx_p_lie.png`：被动：落在地上的圆盾（地上，不跟随，每 1/4 秒接着放），2 帧

弹回来落在地上、等她去捡的圆盾：**平躺在地上的圆盾**（从斜上方看是扁椭圆），金边铁面，下面一圈淡淡的金光，一闪一闪（参考 P_Shield_ground_v2、P_ground_indicator_ring、P_shield_ground_vertglow）。**左右对称**。约 14 × 8 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a steel ramp (#FFFFFF, #E4E6EA, #B8BCC6, #8A8F9C, #5E6270, #383B46).
Effect: A BUCKLER LYING ON THE GROUND seen from above at an angle, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat round shield (an ellipse 10 squares wide and 4 tall: the steel face, a 1-square gold rim, the gold boss, a 1-square dark edge: solid) with a faint gold glow ring round it on the ground (an ellipse 13 wide and 6 tall, no outline); 1 the glow dim; 2 the glow brighter with a white glint on the rim's top.
Layout: one horizontal row of 2 equal 14:8 cells, image size 448x128 (each cell 224x128, 16 px a square); centered across, the shield's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `poppy_fx_p_pick.png`：被动：捡起圆盾（她身上，跟随），4 帧

她走过去捡起圆盾的一瞬间：从地上往上冲起一圈金光，金色的光点往上飘，她身上亮一下（the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 squares wide, her head 20-36 squares above the ground；身体留空不画）（参考 P_activate_flash、P_Buff_glow、P_bokeh_dots）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614).
Effect: A GOLD PICK-UP FLASH round a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 squares wide, her head 20-36 squares above the ground): 1 a gold ring on the ground (an ellipse 20 squares wide and 6 tall) and a white star 3 squares at her feet; 2 gold light streaks rising from the ring 14 squares up at mirrored places, a few gold sparkles; 3 the streaks 24 squares up and thinner, sparkles round her waist; 4 fading sparkles high up; the middle (her body) left clear.
Layout: one horizontal row of 4 equal 28:40 cells, image size 1792x640 (each cell 448x640, 16 px a square); centered across, the figure's ground 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `poppy_fx_p_shown.png`：被动：盾的护盾（她身上，循环）

捡起圆盾后她身上的护盾：**一圈半透明感的金色光罩**围着她（只画边缘：一道金色的弧线轮廓，顶上最亮），上面几道金色的光纹慢慢流动（参考 P_Aura_Self_02、R_Shield_ring、P_shield_glow）。**只画外圈，她的身体位置留空**（the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 squares wide, her head 20-36 squares above the ground）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614).
Effect: A GOLD SHIELD BUBBLE round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 squares wide, her head 20-36 squares above the ground): a rounded shield outline (an upright oval 26 squares wide and 36 tall, sitting on the ground) drawn only as a 1-2 square gold edge, brightest at its top, a lighter inner line 1 square inside it on the top third; 3 short gold light lines running round it at mirrored places; each frame the lines move 2 squares along the edge; everything inside the oval left clear.
Layout: one horizontal row of 4 equal 30:40 cells, image size 1920x640 (each cell 480x640, 16 px a square); centered across, the oval's bottom 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `poppy_fx_a_hit.png`：普攻 / 圆盾命中（目标身上），4 帧

锤子或圆盾打中目标：一下金白色的闪光，几道金色的短尖刺往外，几颗棕色的小石屑（参考 BA_flash、E_impact_flash、R_dirtbits）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A HAMMER BLOW on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 5 squares; 2 a gold star burst 11 squares with a white core, 4 short sharp gold spikes at mirrored angles; 3 the burst a thin ring 13 squares, 4 small brown rock chips (2x2 squares, a dark edge: solid) flying out at mirrored places; 4 fading chips.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `poppy_fx_q_slam.png`：Q 圣锤猛击：锤子砸地（地上，不跟随），5 帧

锤子砸到地上：地面猛地一亮，一圈扁的金色冲击环往外扩，一团棕色的尘土和碎石往上崩，几道裂纹往外射（参考 poppy_base_Q_mis_ground_hit1、poppy_base_Q_mis_ground_hit2、Q_dust_SandSlam、poppy_base_Q_Hit_Rocks、Q_crack_radial）。**左右对称**，落点在格子中间偏下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A HAMMER SLAM INTO THE GROUND seen from above at an angle, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash on the ground 12 squares wide; 2 a flat gold shock ring on the ground (an ellipse 26 wide and 8 tall) and brown dust bursting up 12 squares, 6 brown rock chips (2x2 / 3x2 squares, a dark edge: solid) flung up at mirrored places; 3 the ring 38 wide and 12 tall, the dust 18 squares tall, short dark cracks running out on the ground; 4 the dust opening and falling, the chips coming down; 5 thin dust and the cracks.
Layout: one horizontal row of 5 equal 44:30 cells, image size 3520x480 (each cell 704x480, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `poppy_fx_q_crack.png`：Q：裂开的地面（地上，不跟随，每 1/4 秒接着放），4 帧

锤子砸过的地方：地上一片**裂开的地面**（从斜上方看是扁椭圆），裂缝里透出金色的光，一闪一闪地越来越亮（1 秒后要再炸一次）（参考 poppy_base_Q_mis_ground_hit_buildup、poppy_base_Q_mis_ground_hit2_glow、Q_crack_radial）。**只画地面**，站在上面的人要看得见。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: CRACKED GLOWING GROUND seen from above at an angle, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 36 squares wide and 12 tall of brown cracked ground (darker cracks radiating from the middle, a few loose chips), gold light glowing out of the cracks; frame by frame the gold glow pulses brighter (1 dim, 2 brighter, 3 brightest with white in the middle crack, 4 like 2); nothing taller than 3 squares above the ground.
Layout: one horizontal row of 4 equal 40:16 cells, image size 2560x256 (each cell 640x256, 16 px a square); centered across, the ellipse's middle 7 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `poppy_fx_q_burst.png`：Q：地面再炸一次（地上，不跟随），5 帧

1 秒后裂开的地面再炸一次：裂缝里猛地喷出金色的光柱和尘土，一圈更大的金色冲击环，碎石往上崩（参考 poppy_base_Q_mis_ground_hit2_glow2、R_Nova_Ground、R_Impact_Rock_Crater、poppy_base_Q_Hit2_Rocks）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A RUPTURE OF THE CRACKED GROUND seen from above at an angle, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 the cracks flash white-gold (an ellipse 30 wide and 10 tall); 2 gold light jets bursting up out of the cracks (4 jets at mirrored places, 3 squares wide, 16 tall, white cores) and a gold shock ring 34 wide and 10 tall; 3 the jets 24 tall, brown dust and rock chips (a dark edge: solid) thrown up at mirrored places; 4 the jets thinning, the dust 20 tall; 5 dust settling.
Layout: one horizontal row of 5 equal 44:34 cells, image size 3520x544 (each cell 704x544, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `poppy_fx_q_hit.png`：Q 命中（目标身上），4 帧

被震到的敌人：脚下崩起一小团棕色尘土，几颗碎石，一圈金色的小冲击（参考 poppy_base_Q_Hit_streaks、poppy_base_Q_Hit_Rocks）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A SHOCK HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold flash 6 squares; 2 a gold ring 12 squares, brown dust puffing up at mirrored places; 3 4 rock chips (2x2 squares, a dark edge) flying up, the ring thinner; 4 fading dust.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `poppy_fx_w_cast.png`：W 坚定风采：开启（她身上，跟随），4 帧

她开启坚定风采：脚下猛地亮起一圈金色的光环，往上冲起一道**金色的光罩**（半个圆顶，只画边缘），几道金光往上射，然后光罩收回去变成脚下的光环（参考 W_groundIcon、W_dome_mult、Poppy_base_W_Shield_edge、W_speed_sparks）。**她的身体位置留空**（the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 squares wide, her head 20-36 squares above the ground）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614).
Effect: A GOLD DOME RISING round a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 squares wide, her head 20-36 squares above the ground): 1 a bright gold ring on the ground (an ellipse 30 squares wide and 9 tall) with a white glint; 2 a dome outline rising from it (a half oval 34 wide and 26 tall, a 1-2 square gold edge, brightest at its top) and 4 gold streaks shooting up at mirrored places; 3 the dome 40 wide and 38 tall, thinner, gold sparkles on it; 4 the dome fading, the ground ring left; everything inside the dome clear.
Layout: one horizontal row of 4 equal square cells, image size 2816x704 (each cell 704x704, 16 px a square); centered across, the figure's ground 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `poppy_fx_w_on.png`：W：光环（她脚下，循环）

坚定风采开着的 2 秒：她脚下一个**大大的金色光环**（光环就是阻挡突进的范围），光环边上几道金色的光纹慢慢转，几颗金色的光点往上飘（参考 poppy_base_W_buff_ground、poppy_base_W_buff_ground2、W_Block_ripples）。**只画地上的环，中间不填满**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614).
Effect: A WIDE GOLD AURA RING on the ground round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a gold ring seen from above at an angle (an ellipse 70 squares wide and 22 tall, 1-2 squares thick, a lighter top edge), 6 short gold rune marks on it at mirrored places, 4 small gold sparkles rising from it; each frame the marks move 3 squares along the ring and the sparkles rise; the inside left empty.
Layout: one horizontal row of 4 equal 72:26 cells, image size 4608x416 (each cell 1152x416, 16 px a square); centered across, the ellipse's middle 12 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `poppy_fx_w_block.png`：W：挡下突进（被挡下的敌人身上），4 帧

冲进光环被挡下的敌人：撞上一道金色的光墙（一圈金色的波纹炸开），金色的盾形光一闪，几道冲击线（参考 W_hit_ripple、W_hit_tar、Poppy_base_W_Shield_edge_lines_hit）。**左右对称**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614).
Effect: A DASH BLOCKED by a gold barrier on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): 1 a white-gold flash 8 squares at its chest; 2 a gold ripple ring 16 squares across (2 squares thick, white inside edge) with a small gold shield shape in its middle; 3 the ripple 22 squares, thinner, 6 short gold impact lines at mirrored angles; 4 fading sparkles.
Layout: one horizontal row of 4 equal 24:28 cells, image size 1536x448 (each cell 384x448, 16 px a square); centered across, the unit's feet 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `poppy_fx_e_hit.png`：E 英勇冲锋：撞上目标（目标身上），4 帧

她冲上去撞中目标：一下金白色的大闪光，一圈冲击，几道往外的速度线和尘土（参考 E_Impact_glow、E_impact_flash、E_swooshLines）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A CHARGE IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 8 squares; 2 a gold burst 15 squares with a white core, 6 sharp gold rays at mirrored angles; 3 a gold ring 17 squares and brown dust puffs at both sides; 4 fading dust and sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `poppy_fx_e_wall.png`：E：撞到墙上（目标身上，扩展包用），5 帧

被她推着撞到墙上的敌人：碎石崩飞，一大团尘土，一下**紫色的闪光**（英雄联盟里撞墙眩晕是紫金色的）（参考 E_impact_flash_purple、E_Stun_Smoke、poppy_base_E_Hit_Rocks、E_SmokeCloud）。**左右对称**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a purple flash ramp (#FFFFFF, #F2D8FF, #C890FF, #9A5AE6, #6A34B4, #3E1C70), a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A SLAM INTO A WALL on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): 1 a white-purple flash 10 squares at its chest; 2 a purple and gold star burst 20 squares, 6 brown rock chips (2x2 / 3x3 squares, a dark edge: solid) flying out at mirrored places; 3 a big brown dust cloud 24 squares round it (lighter top, no outline), the chips farther; 4 the dust thinning, purple sparkles; 5 thin dust.
Layout: one horizontal row of 5 equal 26:30 cells, image size 2080x480 (each cell 416x480, 16 px a square); centered across, the unit's feet 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `poppy_fx_e_stun.png`：E：眩晕（敌人头上，循环），4 帧

被撞晕的敌人头上：几颗转圈的金色和紫色小星星（参考 E_Stun_Smoke、E_spark）。**画在头上**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，星星在 34–42 格高）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a purple flash ramp (#FFFFFF, #F2D8FF, #C890FF, #9A5AE6, #6A34B4, #3E1C70) and a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614).
Effect: STUN STARS circling over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 3 small stars (3x3 squares, white cores; gold and purple) on a flat ellipse 14 squares wide and 4 tall; each frame they move a quarter round it.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `poppy_fx_r_charge.png`：R 持卫的裁决：蓄力（她身上，跟随，循环），4 帧

她压低身子蓄力的时候：身边一圈越来越亮的金色旋光（金色的光往她身上收），脚下一圈金光，几颗金色的光点被吸过来（参考 poppy_base_R_channel_spin、poppy_base_R_channel_Ball、R_Cas_sparks_instant、R_hammer_spark）。**她的身体位置留空**（the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 squares wide, her head 20-36 squares above the ground）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614).
Effect: GATHERING GOLD POWER round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small yordle girl stands in the middle, not drawn: 36 squares from her pigtails to the ground, about 22 squares wide, her head 20-36 squares above the ground): a gold ring on the ground (an ellipse 30 squares wide and 8 tall), 6 gold light streaks curving in toward her from 18 squares out at mirrored places, 6 small gold sparkles drawn in; each frame the streaks move 2 squares inward and the ring brightens; the middle (her body) left clear.
Layout: one horizontal row of 4 equal 40:44 cells, image size 2560x704 (each cell 640x704, 16 px a square); centered across, the figure's ground 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `poppy_fx_r_wave.png`：R：往前推出去的锤击冲击波（弹道），4 帧（循环）

她抡锤推出去的冲击波：一道**向右凸的弧形金色冲击波**（月牙形，凸面朝右），前面最亮是白色，后面拖着棕色的尘土和几颗碎石（参考 R_Mis_ground、poppy_base_R_mis_Light、R_mis_dust、poppy_base_R_tarTrail）。**朝右、上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A HAMMER SHOCKWAVE in flight, 4 frames, a seamless loop, pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight: flying left it is turned half round and must not stand upside down): a crescent-shaped gold shockwave 18 squares tall and 4 thick, bulging to the RIGHT, a white edge on its front, brown dust 10 squares trailing behind it (to the left), 4 small rock chips (2x2, a dark edge) in the dust at mirrored heights; each frame the dust churns and the crescent flickers.
Layout: one horizontal row of 4 equal 26:22 cells, image size 1664x352 (each cell 416x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `poppy_fx_r_tap.png`：R：点放的砸地（地上，不跟随），5 帧

没蓄力就放的大招：锤子砸在她身前的地上，一圈大大的金色冲击环往外扩，尘土和碎石往上冲（附近的敌人都被击飞）（参考 R_land_ring、R_Nova_Ground、R_Hammer_hit_dustSpikes、R_dustCloud）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A BIG HAMMER QUAKE seen from above at an angle, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash on the ground 14 squares wide; 2 a gold shock ring (an ellipse 36 wide and 10 tall) and dust spikes shooting up round it (8 spikes at mirrored places, 2 squares wide, 8-12 tall); 3 the ring 54 wide and 16 tall, brown dust 16 squares tall, rock chips (a dark edge: solid) flung up; 4 the dust falling; 5 thin dust and a faint ring.
Layout: one horizontal row of 5 equal 60:32 cells, image size 4800x512 (each cell 960x512, 16 px a square); centered across, the ellipse's middle 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `poppy_fx_r_hit.png`：R 命中（目标身上），4 帧

被大招打中的敌人：一下很大的金白色闪光，金色的冲击环，几道往外的光线和碎石（参考 R_Hit_Flash、R_impact_sharpFlash、R_hit_hammer_glow、R_dirtbits）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warm gold light ramp (#FFFFFF, #FFF4C8, #FFDA6A, #F2AE34, #C77A1E, #7A4614) and a dusty brown ramp (#F4E6C8, #D8BC8C, #B08E5E, #866640, #5C4428, #3A2A18).
Effect: A HEAVY HAMMER HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 9 squares; 2 a gold star burst 17 squares with a white core, 8 sharp rays at mirrored angles; 3 a gold ring 19 squares, 4 rock chips (a dark edge) flying out; 4 fading sparkles and chips.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `poppy_fx_p_buckler` | view_projectiles `league_poppy_p_buckler`（随飞行方向转；画成**朝右**、**上下对称**） | 12 × 12 |
| `poppy_fx_p_lie` | view_effects `league_poppy_p_lie`（不跟随，画在人物下面 z -1；左右对称；落地后 4 秒内每 15 tick 再放一次：2 帧连起来要能接上） | 14 × 8 |
| `poppy_fx_p_pick` | view_effects `league_poppy_p_pick`（跟随，画在人物上面 z 2；左右对称） | 28 × 40 |
| `poppy_fx_p_shown` | view_buffs `league_poppy_p_shown`（跟随，画在人物下面 z -1；左右对称；循环，护盾 3 秒内一直在） | 30 × 40 |
| `poppy_fx_a_hit` | view_effects `league_poppy_a_hit`（跟随，画在人物上面；左右对称） | 14 |
| `poppy_fx_q_slam` | view_effects `league_poppy_q_slam`（不跟随，画在人物上面 z -1；左右对称；大图表） | 44 × 30 |
| `poppy_fx_q_crack` | view_effects `league_poppy_q_crack`（不跟随，画在人物下面 z -2；左右对称；1 秒内每 15 tick 再放一次：4 帧连起来要能无缝接上；大图表） | 40 × 16 |
| `poppy_fx_q_burst` | view_effects `league_poppy_q_burst`（不跟随，画在人物上面 z -1；左右对称；大图表） | 44 × 34 |
| `poppy_fx_q_hit` | view_effects `league_poppy_q_hit`（跟随，画在人物上面；左右对称） | 16 |
| `poppy_fx_w_cast` | view_effects `league_poppy_w_cast`（跟随，画在人物下面 z -1；左右对称；大图表） | 44 × 44 |
| `poppy_fx_w_on` | view_buffs `league_poppy_w_on`（跟随，画在人物下面 z -1；左右对称；循环，2 秒内一直在；大图表） | 72 × 26 |
| `poppy_fx_w_block` | view_effects `league_poppy_w_block`（跟随，画在人物上面 z 2；左右对称） | 24 × 28 |
| `poppy_fx_e_hit` | view_effects `league_poppy_e_hit`（跟随，画在人物上面；左右对称） | 18 |
| `poppy_fx_e_wall` | view_effects `league_poppy_e_wall`（跟随，画在人物上面 z 2；左右对称） | 26 × 30 |
| `poppy_fx_e_stun` | view_buffs `league_poppy_e_stun`（跟随，画在人物上面 z 3；左右对称；循环） | 16 × 10 |
| `poppy_fx_r_charge` | view_effects `league_poppy_r_charge`（跟随，画在人物上面 z 3；左右对称；蓄力 40 tick 里一直在放；大图表） | 40 × 44 |
| `poppy_fx_r_wave` | view_projectiles `league_poppy_r_wave`（随飞行方向转；画成**朝右**、**上下对称**；大图表） | 26 × 22 |
| `poppy_fx_r_tap` | view_effects `league_poppy_r_tap`（不跟随，画在人物上面 z -1；左右对称；大图表） | 60 × 32 |
| `poppy_fx_r_hit` | view_effects `league_poppy_r_hit`（跟随，画在人物上面；左右对称） | 20 |

- 两张表：`asset/league/effects/league_poppy_fx`（小的）和 `league_poppy_big`（q_slam、q_crack、q_burst、w_cast、w_on、r_charge、r_wave、r_tap），tag = 名字（build_poppy.py 的 views）。
- `p_lie` 落地后 4 秒里每 15 tick 再放一次；`q_crack` 1 秒里每 15 tick 再放一次；`r_charge` 在蓄力的 40 tick 里循环；`p_lie`、`q_slam`、`q_crack`、`q_burst`、`r_tap` 不跟随（地上的点）。弹道图朝右、上下对称（随飞行转）；其余全部左右对称。
- 用 `pixel_1x/` 切格（import_cassiopeia_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（圆盾、碎石保留描边）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（普朗克的教训：Codex 自己的 1 倍图可能洗白颜色，必要时从 raw/ 读回）。
