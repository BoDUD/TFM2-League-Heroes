# 不羁之悦 尼菈：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图 + 9 张画进她动作帧的鞭子 / 水痕图。** 造型和动作已定（`design/nilah_designs.png`：3/4 正面待机和侧面；动作都是侧面朝右）。
> - 她在游戏里是**高清**的：每个游戏像素里 2.5×2.5 个细格子；1 倍时 26×43 格（连举起的刃），游戏里再按 90% 显示。
> - **两种画法**：
> 1. 第一部分 15 张普通特效（打中、绕身、纱幕）**照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。大小对照 `design/nilah_size.png`（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士）；`design/nilah_shots.png` 是定稿动作（4 倍），青色十字是绕身特效的中心。
> 2. 第二部分是**画进她自己动作帧**的鞭子和水痕（她的帧会随朝向镜像，特效图不会，所以有方向的鞭子必须画进帧里）。这些按**她的高清细格子**画：`bake/nilah_bake_<名字>_<帧>.png` 是那一帧的定位图（260×146 格，每格 7 像素，她本人画成淡灰色、只用来对位置，青色十字是起点，红线是地面，每 10 格一道浅线）。**在同样大小、同样格子的图上只画特效，背景透明，不要画她本人**；Claude 按格子取回，直接叠进她的帧。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里尼菈自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的鞭刃和招式都是水：白芯、天蓝到深蓝的水光、水珠和水花**；**W 纱幕和大招的治疗带着彩虹般的粉、淡紫、薄荷、金色光**。
> - **特效要亮**：每道水光、每个亮片都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的环、纱幕只画外圈和两边，中间身体位置留空**。
> - **方向（重要，红色方不会镜像）**：第一部分所有画面（打中、她身上、队友身上、绕身的环和纱幕）都要**严格左右对称**（逐格对称）——划痕一律竖直或 X 形。第二部分画进帧里的鞭子和水痕照定位图的方向画（鞭子朝右，水痕朝左），不用对称。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nilah_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），以及 `nilah_bake_<名字>_<帧>.png`（第二部分，1820×1022，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（260×146）。透明度只有 0 和 255、要求对称的逐格对称。附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `nilah_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「喜色川流」 | 鞭刃抽击；Q 强化期间攻击距离变长、横扫扇形、吸血 | `a_lash`（帧里）· `a_hit` · `qa_lash`（帧里）· `qa_hit` · `q_on` |
| 技能 1 = Q「游刃万变」 | 鞭子甩成一条直线长鞭抽过去，之后 4 秒强化；E 之后是原地旋转一圈 | `q_lash`（帧里）· `q_hit` · `eq_spin` · `eq_hit` |
| 技能 2 = E「纵情逐流」+ W「轻纱飞漾」 | E 冲刺穿过敌人（两层充能）；E 都用掉时开 W：躲开普攻、加速，碰到的队友也有纱幕 | `e_trail`（帧里）· `e_hit` · `w_on` · `w_ally`（碰到的那一下）· `w_ally_veil`（队友身上的纱幕） |
| 大招「神恩激荡」 | 原地旋转 1 秒连续打，最后把周围敌人拉过来；伤害转成队友和自己的治疗、护盾 | `r_spin` · `r_hit` · `r_burst` · `r_pull` · `r_heal` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水光、水花、亮片、光带都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 水（鞭子、打中、旋转、水痕）：`#FFFFFF`、`#DFFBFF`、`#9EEBFF`、`#4FC8F2`、`#1E8FD0`、`#0E5294`；
  - 彩虹（W 纱幕、大招的治疗和光）：`#FFFFFF`、`#FFE3F4`、`#F7A6DA`、`#CDA2FF`、`#9FC4FF`、`#8EF2DC`、`#FFE68A`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 第一部分：特效（15 张，游戏格子）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 30000，Q 直线 62000，E 后旋转半径 28000，E 落点半径 16000，大招半径 38000）。

### 1. `nilah_fx_a_hit.png`：普攻打中（目标身上），4 帧

鞭刃抽中：一小团水花炸开，白芯，几滴蓝色水珠往外溅（参考 BA_LinearSplashes、BA_Crit_Tar、Splash_2x2）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a SMALL WATER-WHIP HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a round water splash 9 squares across with a white core, 6 droplets at mirrored places; 3 the splash 12 squares, droplets flying out; 4 a few fading droplets.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `nilah_fx_qa_hit.png`：强化普攻打中（被扫到的每个敌人），4 帧

游刃万变期间的普攻扫中：比普攻大一点的水花，中间一道竖直的白亮水刃划痕，边上几点彩色亮光（参考 BA_Swipe、Light_sparks）。**左右对称**（划痕竖直）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294) and an iridescent joy ramp (#FFFFFF, #FFE3F4, #F7A6DA, #CDA2FF, #9FC4FF, #8EF2DC, #FFE68A).
Effect: a WATER SLASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a vertical slash streak of white-blue water 12 squares tall through the center, a splash 10 squares round it; 3 the splash 14 squares, 4 tiny iridescent glints at mirrored places; 4 fading droplets and glints.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `nilah_fx_q_hit.png`：Q 游刃万变：鞭子抽中（直线上的每个敌人），5 帧

Q 的长鞭抽中：一个白亮的 X 形水刃交叉划痕，水花往两边对称溅开（参考 Q_Swipe、Q_Water、Q_MissBubbles）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a WHIP-LASH HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 two crossing water streaks (an X) 14 squares long with white cores; 3 the X at its brightest, a splash 16 squares round it, droplets at mirrored places; 4 the X breaking into spray; 5 fading droplets.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `nilah_fx_eq_hit.png`：E 之后的旋转斩：扫中（每个敌人），4 帧

旋转一圈扫中：一圈小小的水环炸开，白芯（参考 E_Q_Fill、E_WaterCrescent）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a SPIN-CUT HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a small water ring 10 squares across, white inner edge; 3 the ring 14 squares, breaking into 6 droplets at mirrored places; 4 fading droplets.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `nilah_fx_e_hit.png`：E 纵情逐流：冲过去时打中（每个敌人），4 帧

冲刺穿过时的打中：一道竖直的水浪冲起来又落下，两边溅水花（参考 E_Dash_Tar_Splash、E_AirBullet）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a DASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a vertical column of white-blue water 12 squares tall, splashes at both sides; 3 the column falling into a splash 14 squares wide; 4 fading droplets.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `nilah_fx_r_hit.png`：R 神恩激荡：旋转中每一下打中（每个敌人），4 帧

大招旋转时一下一下打中：小小的白亮 X 划痕加几点水珠（参考 R_Cone_Hit、R_Swipe_Mult）。**左右对称**。约 12 格（这张会连着出现很多次，要小、要快）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a QUICK CUT HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 3 squares; 2 a small X of white-blue streaks 9 squares across; 3 the X 12 squares, 4 droplets at mirrored places; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `nilah_fx_r_pull.png`：R 神恩激荡：最后一下把敌人拉过来（每个敌人），5 帧

大招最后一击：敌人身上一个水的漩涡往里收，再炸开一团大水花（参考 R_buf_Shock、R_splash_ring、R_Flash）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a PULL-IN BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a ring of water 18 squares across; 2 the ring drawn inward to 10 squares, curling streaks at mirrored places; 3 a white flash 8 squares at the center; 4 a water burst 18 squares across with droplets at mirrored places; 5 fading droplets.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `nilah_fx_w_ally.png`：W 轻纱飞漾：碰到队友的那一下（队友身上），5 帧

队友被纱幕碰到：一团欢快的彩色光丝和亮片往外绽开（粉、淡紫、薄荷、金，白芯；参考 W_Sparkle、W_WaterThreads、W_Halo）。**左右对称**，中间人形位置留空。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an iridescent joy ramp (#FFFFFF, #FFE3F4, #F7A6DA, #CDA2FF, #9FC4FF, #8EF2DC, #FFE68A).
Effect: a JOYFUL SPARKLE BURST round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 8 squares wide and 14 tall): 1 4 white sparkles at mirrored places; 2 curling iridescent ribbons rising at both sides 16 squares tall; 3 the ribbons and 8 sparkles at their brightest, 18 squares across; 4 the ribbons thinning; 5 a few fading sparkles.
Layout: one horizontal row of 5 equal 20:22 cells, image size 1600x352 (each cell 320x352, 16 px a square); centered across, the bottom of the shape 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `nilah_fx_r_heal.png`：R 神恩激荡：治疗和护盾（队友和她自己身上），5 帧

大招把伤害转成治疗和护盾：队友身上一层水光从脚下升起，几个水泡和彩色亮片往上飘，最后在身前合成一层淡淡的光罩（参考 R_Waves_color、R_GradientV、common_waterdots）。**左右对称**，中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294) and an iridescent joy ramp (#FFFFFF, #FFE3F4, #F7A6DA, #CDA2FF, #9FC4FF, #8EF2DC, #FFE68A).
Effect: a HEAL-AND-SHIELD RISE round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 8 squares wide and 18 tall): 1 a water glow on the ground 12 squares wide; 2 water light rising at both sides 16 squares tall, 3 bubbles; 3 the light at its top, iridescent sparkles at mirrored places; 4 a thin bright arc over the empty middle (the shield); 5 fading bubbles.
Layout: one horizontal row of 5 equal 18:24 cells, image size 1440x384 (each cell 288x384, 16 px a square); centered across, the glow's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `nilah_fx_eq_spin.png`：E 之后的旋转斩：鞭子绕她一圈（她身上，大），5 帧

E 冲过去后接 Q 的旋转：鞭刃带着水光在她腰间绕一整圈（从斜上方看的扁椭圆环，前后都画），水花往外甩（参考 E_Q_Wave_Mask、E_WaterCrescent、Q_Swipe2）。**左右对称**，中间她的身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a WHIP SPIN RING round a figure at waist height, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 12 squares wide and 20 tall over the center): 1 a thin white-blue arc across the front of an ellipse 40 squares wide; 2 the whole ellipse ring 52 squares wide and 20 tall, 3 squares thick, white leading edge; 3 the ring at its brightest, 56 squares wide, spray flying out at mirrored places; 4 the ring breaking into a circle of droplets; 5 fading droplets.
Layout: one horizontal row of 5 equal 58:26 cells, image size 4640x416 (each cell 928x416, 16 px a square); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `nilah_fx_r_spin.png`：R 神恩激荡：旋转的鞭刃风暴（她身上，大，1 秒），8 帧

大招 1 秒的旋转：几道带水光的鞭刃环一层层绕着她转（扁椭圆，内圈快外圈慢），水珠和彩色亮片被甩出去，地上一圈涟漪（参考 R_Orbit、R_Sword_Trail2、R_trail、R_Puddle_Ripples、RainbowGrad_Soft）。**左右对称**，中间她的身体位置留空。8 帧连着播一秒，最后一帧接下一张爆发。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294) and an iridescent joy ramp (#FFFFFF, #FFE3F4, #F7A6DA, #CDA2FF, #9FC4FF, #8EF2DC, #FFE68A).
Effect: a WHIRLING WHIP STORM round a figure, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 14 squares wide and 26 tall over the center): two or three nested elliptical rings of white-blue water light (the outer 76 squares wide and 30 tall, the inner 50 wide), each 2-3 squares thick, their bright arcs moving round frame to frame; droplets and iridescent glints thrown outward at mirrored places; a thin ripple ellipse on the ground under them; the rings grow from frame 1 to frame 3, stay at full size 4-7, and tighten in frame 8.
Layout: one horizontal row of 8 equal 78:34 cells, image size 9984x544 (each cell 1248x544, 16 px a square); the ellipses centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `nilah_fx_r_burst.png`：R 神恩激荡：最后的爆发（她身上，大），5 帧

大招最后把人拉过来的一下：一圈大水浪从她身边往外炸开，带着彩色的光，再落成水珠（参考 BlastRing、R_splash_ring、R_EnergyStreaksAdd、R_Flash）。**左右对称**，中间她的身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294) and an iridescent joy ramp (#FFFFFF, #FFE3F4, #F7A6DA, #CDA2FF, #9FC4FF, #8EF2DC, #FFE68A).
Effect: a GREAT WATER BURST round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 14 squares wide and 26 tall over the center): 1 a white flash ring 30 squares wide; 2 a thick ring of water 56 squares wide and 24 tall bursting outward, iridescent edge; 3 the ring 80 squares wide, spray at mirrored places; 4 the ring breaking into droplets; 5 fading droplets and glints.
Layout: one horizontal row of 5 equal 82:38 cells, image size 6560x608 (each cell 1312x608, 16 px a square); the rings centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `nilah_fx_q_on.png`：Q 游刃万变：4 秒强化（她身上，循环），4 帧

游刃万变期间（攻击距离变长、普攻横扫、吸血）：她身上淡淡的一圈水光，几滴水珠绕着她慢慢转（参考 Q_cas_glow、Droplet_Rotate、common_waterdots）。要淡，不能挡住她。**左右对称**，中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a FAINT WATER AURA round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 12 squares wide and 24 tall): 6 small droplets (2 squares each) at mirrored places round the empty middle, taking turns to brighten, and thin pale-blue arcs at both sides that shimmer.
Layout: one horizontal row of 4 equal 26:32 cells, image size 1664x512 (each cell 416x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `nilah_fx_w_on.png`：W 轻纱飞漾：她身上的纱幕（循环，大），6 帧

纱幕（2.25 秒躲开所有普攻）：一层半透明感的彩色薄纱绕着她飘（粉、淡紫、薄荷、金色的光带，像流动的丝），几个亮片闪烁（参考 W_Aura_Flames、W_WispTrail_Add、W_Halo_1、W_Sparkle）。像素画里不要半透明：用细的光带和亮片表现轻盈。**左右对称**，中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an iridescent joy ramp (#FFFFFF, #FFE3F4, #F7A6DA, #CDA2FF, #9FC4FF, #8EF2DC, #FFE68A).
Effect: a FLOWING IRIDESCENT VEIL round a figure, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 14 squares wide and 36 tall): thin flowing ribbons of pink, lilac, mint and gold light (2 squares thick) rising and curling up both sides to 46 squares tall, 6 white sparkles at mirrored places taking turns; the ribbons' waves move up a little each frame.
Layout: one horizontal row of 6 equal 36:48 cells, image size 3456x768 (each cell 576x768, 16 px a square); centered across, the ribbons' bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `nilah_fx_w_ally_veil.png`：W 轻纱飞漾：队友身上的纱幕（循环，大），6 帧

被碰到的队友 1.5 秒也有纱幕：和她身上那张一样的彩色光带，细一点、少一点。**左右对称**，中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an iridescent joy ramp (#FFFFFF, #FFE3F4, #F7A6DA, #CDA2FF, #9FC4FF, #8EF2DC, #FFE68A).
Effect: a THIN IRIDESCENT VEIL round a figure, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 12 squares wide and 32 tall): two thin flowing ribbons of pink, lilac, mint and gold light (1-2 squares thick) curling up both sides to 42 squares tall, 4 white sparkles at mirrored places taking turns.
Layout: one horizontal row of 6 equal 32:44 cells, image size 3072x704 (each cell 512x704, 16 px a square); centered across, the ribbons' bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 第二部分：画进她动作帧的鞭子和水痕（9 张，她的高清格子）

每张都在对应的定位图 `bake/nilah_bake_<名字>_<帧>.png` 上画：同样 1820×1022 像素、每格 7 像素、260×146 格，格子和定位图完全对齐；**只画特效，不画她**，背景透明。她本人在定位图里是淡灰色，只用来对位置。鞭子从青色十字（刃尖）开始；她身前的鞭子画在她**上面**（会盖住她），身后的水痕画在她**后面**（被她挡住的部分不用画）。

### 16. 普攻：鞭刃从刃尖甩出去（画进她的普攻第 3、4 帧）

普攻刺出去那一下，折叠的鞭刃从刃尖松开甩出去，像一条带水光的细鞭：第 3 帧伸出一半、波浪形；第 4 帧伸直到最远，鞭尖炸开一小团水花。鞭子从图上青色十字（刃尖）开始往**右**伸。

**`nilah_bake_a_lash_3.png`**（定位图 `bake/nilah_bake_a_lash_3.png`，起点青色十字在第 166 列、第 78 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a THIN WATER-LIGHT WHIP uncoiling to the RIGHT from the cyan cross (the blade's tip): a wavy ribbon 2-3 squares thick and 14 squares long with a white core, a few droplets along it.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (166, 78) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

**`nilah_bake_a_lash_4.png`**（定位图 `bake/nilah_bake_a_lash_4.png`，起点青色十字在第 168 列、第 74 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: the WHIP fully out to the RIGHT from the cyan cross: a nearly straight ribbon 2-3 squares thick and 20 squares long with a white core, ending in a small crack-splash 6 squares across at its tip, droplets flying.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (168, 74) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. 强化普攻：更长的鞭子加扇形水刃（画进她的强化普攻第 3、4 帧）

游刃万变期间的普攻：鞭子甩得更远（攻击距离 +12.5），鞭尖前面扇开一片扇形的水刃，扫中扇形里的敌人。第 3 帧鞭子伸出、扇形刚出现；第 4 帧扇形最大，带水花。从青色十字（刃尖）往**右**。

**`nilah_bake_qa_lash_3.png`**（定位图 `bake/nilah_bake_qa_lash_3.png`，起点青色十字在第 169 列、第 65 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a WATER-LIGHT WHIP to the RIGHT from the cyan cross: a ribbon 3 squares thick and 26 squares long with a white core, a narrow fan of water starting to open ahead of its tip.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (169, 65) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

**`nilah_bake_qa_lash_4.png`**（定位图 `bake/nilah_bake_qa_lash_4.png`，起点青色十字在第 164 列、第 69 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: the WHIP 32 squares long to the RIGHT from the cyan cross, and ahead of its tip a WIDE FAN of water slashes opening to the right (about 40 degrees across, 30 squares deep, 3-4 curved white-edged streaks), spray at its rim.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (164, 69) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. Q 游刃万变：直线长鞭（画进她的 Q 第 4、5 帧）

Q 把鞭刃甩成一条笔直的长鞭，一直抽到 62 个游戏像素远（格子里第 235 列，图上有黄线标出）：第 4 帧整条鞭子伸直，细长（2-3 格粗）、白芯、沿路有水珠，鞭尖一团水花；第 5 帧鞭子收回，原来的位置留下一道正在散开的水雾线。从青色十字（刃尖）往**右**。

**`nilah_bake_q_lash_4.png`**（定位图 `bake/nilah_bake_q_lash_4.png`，起点青色十字在第 191 列、第 70 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a LONG STRAIGHT WATER-LIGHT WHIP to the RIGHT from the cyan cross to the yellow line: 2-3 squares thick with a white core, small droplets along it, a splash 8 squares across at its tip on the yellow line.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (191, 70) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

**`nilah_bake_q_lash_5.png`**（定位图 `bake/nilah_bake_q_lash_5.png`，起点青色十字在第 129 列、第 86 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: the whip gone: along the same line a thin fading streak of water spray and droplets, brightest near the tip, breaking up.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (129, 86) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. E 纵情逐流：冲刺时身后的水痕（画进她的 E 第 1、2、3 帧，画在她身后）

冲刺穿过敌人时，她身后拖一条流动的水带（从她的腰和拖在后面的鞭刃往**左**拖出去，约 40 格长），水珠往后飞，第 1 帧短，第 2 帧最长，第 3 帧开始散。画在人物**后面**（被人物挡住的地方不用画）。

**`nilah_bake_e_trail_1.png`**（定位图 `bake/nilah_bake_e_trail_1.png`，起点青色十字在第 98 列、第 102 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: a FLOWING WATER WAKE trailing to the LEFT from the figure's waist: a wavy ribbon 4-6 squares thick and 24 squares long, white crest along its top, droplets behind.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (98, 102) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

**`nilah_bake_e_trail_2.png`**（定位图 `bake/nilah_bake_e_trail_2.png`，起点青色十字在第 109 列、第 108 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: the WAKE at its longest: 40 squares to the LEFT from the figure's waist, 6 squares thick near her thinning to the end, white crest, droplets flying back.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (109, 108) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

**`nilah_bake_e_trail_3.png`**（定位图 `bake/nilah_bake_e_trail_3.png`，起点青色十字在第 110 列、第 102 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around water, light, spray or sparkles, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a water ramp (#FFFFFF, #DFFBFF, #9EEBFF, #4FC8F2, #1E8FD0, #0E5294).
Effect: the WAKE breaking up: 36 squares long, its far half turning into spray and droplets.
Layout: ONE image 1820x1022, the same size and 7-px square grid as the guide picture (a 260 x 146 square grid); the cyan cross of the guide is at square (110, 102) counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `nilah_fx_a_hit` | view_effects `league_nilah_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `nilah_fx_qa_hit` | view_effects `league_nilah_qa_hit`（跟随，画在人物上面；左右对称） | 14 |
| `nilah_fx_q_hit` | view_effects `league_nilah_q_hit`（跟随，画在人物上面；左右对称） | 16 |
| `nilah_fx_eq_hit` | view_effects `league_nilah_eq_hit`（跟随，画在人物上面；左右对称） | 14 |
| `nilah_fx_e_hit` | view_effects `league_nilah_e_hit`（跟随，画在人物上面；左右对称） | 14 |
| `nilah_fx_r_hit` | view_effects `league_nilah_r_hit`（跟随，画在人物上面；左右对称） | 12 |
| `nilah_fx_r_pull` | view_effects `league_nilah_r_pull`（跟随，画在人物上面；左右对称） | 18 |
| `nilah_fx_w_ally` | view_effects `league_nilah_w_ally`（跟随，画在人物上面；左右对称） | 18 |
| `nilah_fx_r_heal` | view_effects `league_nilah_r_heal`（跟随，画在人物上面；左右对称） | 16 × 22 |
| `nilah_fx_eq_spin` | view_effects `league_nilah_eq_spin`（BIG，她身上，跟随；左右对称） | 56 × 24 |
| `nilah_fx_r_spin` | view_effects `league_nilah_r_spin`（BIG，她身上，跟随；左右对称） | 76 × 32 |
| `nilah_fx_r_burst` | view_effects `league_nilah_r_burst`（BIG，她身上，跟随；左右对称） | 80 × 36 |
| `nilah_fx_q_on` | view_buffs `league_nilah_q_on`（跟随，画在人物上面；左右对称） | 24 × 30 |
| `nilah_fx_w_on` | view_buffs `league_nilah_w_on`（BIG，跟随，画在人物上面；左右对称） | 34 × 46 |
| `nilah_fx_w_ally_veil` | view_buffs `league_nilah_w_ally`（BIG 表里 tag 叫 w_ally；跟随，画在人物上面；左右对称） | 30 × 42 |
| `nilah_bake_a_lash_<帧>` | 画进 `attack` 第 3、4 帧（人物上面） | 高清格子 |
| `nilah_bake_qa_lash_<帧>` | 画进 `attack_q` 第 3、4 帧（人物上面） | 高清格子 |
| `nilah_bake_q_lash_<帧>` | 画进 `skill` 第 4、5 帧（人物上面） | 高清格子 |
| `nilah_bake_e_trail_<帧>` | 画进 `skill2` 第 1、2、3 帧（人物后面） | 高清格子 |

- 两张表：`asset/league/effects/league_nilah_fx`（小的）和 `league_nilah_big`（eq_spin、r_spin、r_burst、w_on，和 tag 叫 w_ally 的 `w_ally_veil`），tag = 名字（build_nilah.py 的 views）。
- 画进帧的四张在 restyle 加粗外描边之后叠到高清帧上（它们没有描边），1 倍表一起更新；`e_trail` 画进帧以后，技能里的 `cview("e_trail")` 和它的 view 一起删掉。
- 用 `pixel_1x/` 切格（import_nidalee / import_braum 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
