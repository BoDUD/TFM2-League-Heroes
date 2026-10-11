# 深海泰坦 诺提勒斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型和动作已定（`design/nautilus_idle.png`：游戏里的侧身待机，8 倍，连背上的锚 50 行、41 格宽）。
> - 大小对照 `design/nautilus_size.png`：待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/nautilus_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里诺提勒斯自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**深海的水 = 白色泡沫 + 浅青、海蓝绿，里面是深蓝绿**；W 的护盾是他身上缝线那种海绿色的光；飞出去的锚是定稿的灰色铁锚。
> - **特效要亮**：每团水花都要用最亮的几档和白色泡沫芯，暗底上一眼能看见；深水色只在水的里面，**边缘一定是亮的泡沫和浅青**。
> - **围着人的护盾、水柱只画外圈和两边，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：飞出去的锚和冲击波（`q_anchor`、`r_wave`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻；锚爪一上一下对称张开）。画在人身上、脚下、头顶的（打中、禁锢、护盾、减速、晕眩、掀起）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；地上的 `e_wave1-3` 上下左右都对称；`r_cast` 左右对称。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nautilus_fx_<名字>.png` 和原尺寸的 `pixel_1x/`，附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `nautilus_fx_pack_done.zip`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「排山倒海」 | 抡锚砸；打英雄时把它定在原地（之后 6 秒不再触发） | `a_hit` · `p_hit` · `p_root` |
| 技能 1 = Q「疏通航道」 | 抛出铁锚，钩中第一个敌方英雄，把两人拉到一起 | `q_anchor` · `q_hit` |
| 技能 2 = W「泰坦之怒」+ E「暗流涌动」 | 护盾（期间普攻伤到目标周围）；捶地，三波浪往外，冲中的人减速 | `w_on` · `w_hit` · `e_wave1` · `e_wave2` · `e_wave3` · `e_hit` · `e_slow` |
| 大招 = R「深海冲击」 | 砸地，冲击波从地下冲向一名敌方英雄，沿途的人被掀起，目标被巨大的水柱冲上天再晕住 | `r_cast` · `r_wave` · `r_up` · `r_hit` · `r_stun` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水花、光、浪、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**；只有飞出去的铁锚（实物）有 1 格黑描边。
- **要亮**：每个形状都有白色泡沫或最亮一档的芯；深水色只在里面。
- 颜色（按每条写的用）：
  - 海水泡沫（水花、浪尖、闪光）：`#FFFFFF`、`#D8FFF7`、`#8CF2E6`、`#3FD3C8`、`#12A3A8`；
  - 深水（水的身体：深色只在里面）：`#0E7C86`、`#0B5D6E`、`#0A4158`、`#082A3F`；
  - 海绿光（W 护盾）：`#FFFFFF`、`#CFFFE9`、`#7DF5C8`、`#00E9BE`、`#03A688`；
  - 铁锚的灰（定稿，#070211 是描边）：`#F6E4C8`、`#B2B0A8`、`#70747A`、`#3D4150`、`#2D3041`、`#070211`；
  - 铜锈（锚上的红箍和绳）：`#FAAC2A`、`#DC741C`、`#A84217`、`#6F2610`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，Q 飞 85000，W 余波半径 18000，E 半径 32000，R 射程 80000）。

### 1. `nautilus_fx_a_hit.png`：普攻砸中（目标身上），4 帧

铁锚砸中：一团白色水花往四周溅开（左右对称），中间一道白光，几颗水珠飞出去（参考 BA_Hit_tar_sharp、BA_waterbits）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: an ANCHOR SMASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares across; 2 a burst of white-aqua water splashing out 12 squares across, white foam in the middle; 3 the splash wider and thinner, water drops flying out at mirrored places; 4 a few fading drops.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `nautilus_fx_p_hit.png`：被动排山倒海：禁锢时的一击（目标身上），5 帧

排山倒海定身的那一下：一道竖直的水柱从地面往上冲起（居中），四周溅开一圈水花，一圈蓝绿色的光环往外扩（参考 P_land_splash、P_splash_circular）。**左右对称**。约 18 格宽、22 格高，水柱底在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a WATER SURGE on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat white-aqua splash 10 squares wide on the ground; 2 a column of water 6 squares wide shooting up the middle 20 squares tall, white foam at its top; 3 the column breaking into foam, a ring of splashes 18 squares wide at the bottom; 4 drops falling at mirrored places; 5 fading drops.
Layout: one horizontal row of 5 equal 20:24 cells, image size 1600x384 (each cell 320x384, 16 px a square); centered across, the splash on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `nautilus_fx_p_root.png`：被动的禁锢（被定住的人脚下，循环），4 帧

被定在原地：脚下一圈从斜上方看的扁椭圆漩涡水圈，蓝绿色亮边，里面深水色，几条水纹往中间收（参考 Passive_timer_ring、Seafoam）。**左右对称**（水纹每帧换到对称的位置，不画朝一个方向转）。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a WATER SNARE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ellipse of swirling water 16 squares wide and 5 tall, a bright aqua foam edge, deep water inside, 4 short foam ripples at mirrored places that move inward each frame.
Layout: one horizontal row of 4 equal 20:9 cells, image size 1280x144 (each cell 320x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `nautilus_fx_q_anchor.png`：Q 疏通航道：飞出去的铁锚（飞行中，循环），4 帧

Q 抛出去的铁锚：从侧面看的整把锚朝右飞——右边是锚冠（两只弯钩锚爪**上下对称**地张开），中间是锚杆和一圈红箍，左边拖一段铁链（链环一节一节），锚冠前面一点白色水花（参考 Q_MissileHead、Q_rope_chain）。锚是铁的实物，用定稿的灰色，有 1 格黑描边。**上下对称**。4 帧无缝循环（水花和链环抖动）。约 22 格长、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from the anchor's iron greys (#F6E4C8, #B2B0A8, #70747A, #3D4150, #2D3041, #070211; #070211 is its 1-square outline), bronze and rust (#FAAC2A, #DC741C, #A84217, #6F2610) and a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a FLYING ANCHOR to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): at the right the anchor's crown seen from the side, its two hooked flukes curving back, one up and one down (mirrored), 12 squares tall; a straight iron shank 10 squares long to the left with one red-rust band; behind it a short iron chain of 4 links trailing to the left edge; a little white-aqua foam splashing off the crown's front (mirrored). The anchor and the chain are solid iron with a 1-square #070211 outline; the foam has no outline. The foam and the chain links jiggle each frame.
Layout: one horizontal row of 4 equal 24:16 cells, image size 1536x256 (each cell 384x256, 16 px a square); the crown's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `nautilus_fx_q_hit.png`：Q 钩中（被钩中的英雄身上），4 帧

铁锚钩中：一团大的白色水花炸开，一圈铁链环形的水纹往外（参考 Q_land_splash、Q_splash_circular）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: an ANCHOR HOOK HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a big burst of white-aqua water 14 squares across; 3 a thin foam ring 16 squares across, drops at mirrored places; 4 fading drops.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `nautilus_fx_w_on.png`：W 泰坦之怒：护盾（他身上，循环），4 帧

护盾期间：他周围一层细的蓝绿色发光外壳（竖的椭圆，只画外圈），外圈上几道流动的光纹（参考 W_shield_glow、W_Nautilus_Skin04_W_Shield、W_blue_green_light）。**中间留空、左右对称**。4 帧无缝循环。约 30 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-green glow ramp (#FFFFFF, #CFFFE9, #7DF5C8, #00E9BE, #03A688).
Effect: a SEA-GREEN SHIELD round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY: an upright ellipse outline 28 squares wide and 40 tall, 1-2 squares thick, glowing sea-green with white glints at mirrored places that move to new mirrored places each frame.
Layout: one horizontal row of 4 equal 32:44 cells, image size 2048x704 (each cell 512x704, 16 px a square); the shell centered in every cell, its bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `nautilus_fx_w_hit.png`：W 护盾期间的普攻余波（目标周围），4 帧

护盾时普攻会伤到目标周围：目标脚下一圈蓝绿色的电光水波往外扩（从斜上方看的扁椭圆）（参考 W_EnergyStreak、W_ping_light）。**左右对称**。约 20 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-green glow ramp (#FFFFFF, #CFFFE9, #7DF5C8, #00E9BE, #03A688) and a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a GLOWING SPLASH RING round a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a sea-green flash 6 squares wide; 2 a sea-green ellipse ring 14 squares wide and 6 tall with short sparks; 3 the ring 20 wide, thinner; 4 fading sparks at mirrored places.
Layout: one horizontal row of 4 equal 22:12 cells, image size 1408x192 (each cell 352x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `nautilus_fx_e_wave1.png`：E 暗流涌动：第一波（他脚下，地面），5 帧

他捶地后地面炸起三波浪：第一波是一圈小的、从斜上方看的扁椭圆水浪，浪尖白色泡沫，里面深水色（参考 E_Splash_Ring、E_Cas_Puddle_Ripples、E_explosion_tar_SplashFlip）。**上下左右都对称**。约 36 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a GROUND WAVE (the first and smallest), 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: an elliptical ring of crashing water seen from above at an angle, white foam crests along it; 1 a ring 14 squares wide; 2 24 wide, foam spraying up; 3 30 wide; 4 36 wide and 14 tall, breaking; 5 foam fading.
Layout: one horizontal row of 5 equal 38:16 cells, image size 3040x256 (each cell 608x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `nautilus_fx_e_wave2.png`：E 暗流涌动：第二波（地面），5 帧

第二波：同样的浪圈，更大一圈（参考同上）。**上下左右都对称**。约 52 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a GROUND WAVE (the second), 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: an elliptical ring of crashing water seen from above at an angle, white foam crests; 1 a ring 26 squares wide; 2 38 wide, foam spraying up; 3 46 wide; 4 52 wide and 20 tall, breaking; 5 foam fading.
Layout: one horizontal row of 5 equal 54:22 cells, image size 4320x352 (each cell 864x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `nautilus_fx_e_wave3.png`：E 暗流涌动：第三波（地面），5 帧

第三波：最大的一圈，就是 E 的范围（半径 32 格）（参考同上）。**上下左右都对称**。约 68 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a GROUND WAVE (the third and largest), 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: an elliptical ring of crashing water seen from above at an angle, white foam crests; 1 a ring 36 squares wide; 2 52 wide, foam spraying up; 3 62 wide; 4 68 wide and 26 tall, breaking; 5 foam fading.
Layout: one horizontal row of 5 equal 70:28 cells, image size 5600x448 (each cell 1120x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `nautilus_fx_e_hit.png`：E 冲中（每个被浪打中的人身上），4 帧

被浪冲中：一团小水花往上溅（参考 E_impact_flash、E_water_bolts）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a WAVE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 water splashing up 10 squares wide; 3 drops at mirrored places; 4 fading drops.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `nautilus_fx_e_slow.png`：E 的减速（被减速的人脚下，循环），4 帧

被暗流减速：脚下一圈浅浅的水洼，泡沫亮边，几条水纹往中间收。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a PUDDLE SLOW under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a shallow water ellipse 14 squares wide and 4 tall with a white-aqua foam edge, 4 short ripples at mirrored places drifting inward each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `nautilus_fx_r_cast.png`：R 深海冲击：起手（他脚下），5 帧

R 砸地：他脚下炸起一圈白色水花和尘土，中间一道青色的光往下钻进地里（参考 R_impact_flash、R_groundDust、R_greenRing）。**左右对称**，只在脚边。约 28 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a DEPTH CHARGE LAUNCH at a figure's feet, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat white-aqua flash 12 squares wide on the ground; 2 water and dust bursting out to both sides 24 squares wide; 3 a teal ring 28 wide; 4 thinning; 5 fading drops.
Layout: one horizontal row of 5 equal 30:14 cells, image size 2400x224 (each cell 480x224, 16 px a square); centered across, the bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `nautilus_fx_r_wave.png`：R 深海冲击：地下冲过去的冲击波（飞行中，循环），4 帧

冲击波从地下朝目标冲过去：一道朝右走的水浪隆起，前端白色浪花高高翻起，后面拖一串越来越小的水花和裂开的地面（参考 R_waterspike32、R_aqua_nova、Crater）。朝右走。**上下对称**（游戏会把它转向；往左走时上下翻）。4 帧无缝循环。约 24 格长、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a SHOCKWAVE RUSHING to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): at the right a crest of white-aqua water spikes 12 squares tall bursting up and down (mirrored), deep water in its middle, a trail of smaller splashes 12 squares long behind it to the left (mirrored); the spikes and splashes change each frame.
Layout: one horizontal row of 4 equal 26:16 cells, image size 1664x256 (each cell 416x256, 16 px a square); the crest's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `nautilus_fx_r_up.png`：R 冲击波掀起沿途的敌人（身上），4 帧

沿途被掀起：脚下一根水柱把人顶起来（竖直居中），水花往两边溅（参考 R_waterspike32）。**左右对称**。约 14 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a WATER SPIKE under a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white splash 8 squares wide on the ground; 2 a spike of water 6 squares wide shooting up 16 squares tall in the middle; 3 the spike breaking into foam; 4 fading drops.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); centered across, the splash on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `nautilus_fx_r_hit.png`：R 命中目标（目标身上，大），6 帧

深海冲击命中：目标脚下炸起一根巨大的水柱，把人冲上天（中间留出人的位置，水柱在人的两边和身后往上冲），顶上白色浪花散开，地面一圈蓝绿色冲击环（参考 R_aqua_nova、R_waterspike32、R_greenRing、R_impact_flash）。**左右对称**。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a GREAT WATER ERUPTION round a unit, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit's place in the middle (12 x 24 squares, from the bottom) EMPTY: 1 a white flash 14 squares wide on the ground and a teal ring 24 wide; 2 two thick columns of water bursting up both sides 36 squares tall, deep water inside, white foam edges; 3 the columns' tops crashing into white foam over the middle; 4 water falling at mirrored places; 5 drops and thin foam; 6 fading drops.
Layout: one horizontal row of 6 equal 32:42 cells, image size 3072x672 (each cell 512x672, 16 px a square); centered across, the ground ring's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `nautilus_fx_r_stun.png`：R 的眩晕（头顶，循环），4 帧

被晕住：头顶绕着一圈扁扁的水泡和小鱼形状的光点（参考 waterdots）。**左右对称**（光点每帧换到对称的位置）。4 帧无缝循环。约 16 格宽、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a DAZE RING of bubbles over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 16 squares wide and 5 tall of small white-aqua bubbles, 4 bright bubbles on it at mirrored places that step to new mirrored places each frame.
Layout: one horizontal row of 4 equal 18:9 cells, image size 1152x144 (each cell 288x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `nautilus_fx_a_hit` | view_effects `league_nautilus_a_hit`（跟随，画在人物上面；左右对称） | 14 |
| `nautilus_fx_p_hit` | view_effects `league_nautilus_p_hit`（跟随，画在人物上面；左右对称） | 18 |
| `nautilus_fx_p_root` | view_buffs `league_nautilus_p_root`（跟随，画在人物下面；左右对称） | 18 × 7 |
| `nautilus_fx_q_anchor` | view_projectiles `league_nautilus_q_anchor`（朝飞行方向转，画成朝右飞；上下对称） | 22 × 14 |
| `nautilus_fx_q_hit` | view_effects `league_nautilus_q_hit`（跟随，画在人物上面；左右对称） | 16 |
| `nautilus_fx_w_on` | view_buffs `league_nautilus_w_on`（跟随，画在人物上面；左右对称） | 30 × 42 |
| `nautilus_fx_w_hit` | view_effects `league_nautilus_w_hit`（跟随；左右对称） | 20 × 10 |
| `nautilus_fx_e_wave1` | view_effects `league_nautilus_e_wave1`（施法时，不跟随，画在人物下面；上下左右都对称） | 36 × 14 |
| `nautilus_fx_e_wave2` | view_effects `league_nautilus_e_wave2`（施法时，不跟随，画在人物下面；上下左右都对称） | 52 × 20 |
| `nautilus_fx_e_wave3` | view_effects `league_nautilus_e_wave3`（施法时，不跟随，画在人物下面；上下左右都对称） | 68 × 26 |
| `nautilus_fx_e_hit` | view_effects `league_nautilus_e_hit`（跟随；左右对称） | 12 |
| `nautilus_fx_e_slow` | view_buffs `league_nautilus_e_slow`（跟随，画在人物下面；左右对称） | 16 × 6 |
| `nautilus_fx_r_cast` | view_effects `league_nautilus_r_cast`（施法时，不跟随，画在人物下面；左右对称） | 28 × 12 |
| `nautilus_fx_r_wave` | view_projectiles `league_nautilus_r_wave`（朝飞行方向转，画成朝右走；上下对称） | 24 × 14 |
| `nautilus_fx_r_up` | view_effects `league_nautilus_r_up`（跟随；左右对称） | 14 × 18 |
| `nautilus_fx_r_hit` | view_effects `league_nautilus_r_hit`（跟随，画在人物上面；左右对称） | 30 × 40 |
| `nautilus_fx_r_stun` | view_buffs `league_nautilus_r_stun`（跟随；左右对称） | 16 × 7 |

- 两张表：`asset/league/effects/league_nautilus_fx`（小的）和 `league_nautilus_big`（r_hit、r_wave、e_wave1-3），tag = 名字（build_nautilus.py 的 views）。
- `q_anchor` 是直线飞的（line），`y_offset` 3000；`r_wave` 是追踪弹（homing）：画面开头补一帧空的（追踪弹第一 tick 朝上）。
- `e_wave1-3`、`r_cast` 不跟随、画在人物下面（z -1）；`p_root`、`e_slow` 是脚下的 buff（z -1）；`w_on`、`r_stun` 画在人物上面（z 3），所以 `w_on` 中间必须是空的。
- 用 `pixel_1x/` 切格（import_viktor / import_seraphine 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
