# 披甲龙龟 拉莫斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图。** 造型和动作已定（`design/rammus_idle.png`：3/4 正面朝右的矮胖犰狳，橙金色带尖刺的大甲壳，甲壳前缘下探出绿色的小乌龟头和红眼睛，青绿鳞皮、米白爪子、黄褐肚子、暗红挽具）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），35 格高、35 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/rammus_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/rammus_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里拉莫斯自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**他的光是甲壳的金色**（尖刺护盾、撞击），**动力冲刺和冲天猛撞掀起沙漠的黄沙和碎石**，**砸出的坑里透着橙色的熔岩裂纹**，**嘲讽是红橙色的火光**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像（这个英雄没有弹道图：动力冲刺就是他自己滚过去）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `rammus_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/rammus_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/rammus_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（被动「锥刺甲壳」在里面） | 整个翻一个跟头用甲壳撞过去，多一段魔法伤害 | `a_hit` |
| 技能 1 = Q「动力冲刺」 | 缩成刺球滚向敌人，撞上炸开，击退、减速 | `q_dust` · `q_burst` · `q_hit` · `q_slow` |
| W「尖刺防御」（敌方英雄靠近时自动开） | 蜷起来，7 秒内护甲魔抗提升、反伤 | `w_cast` · `w_on` |
| 技能 2 = E「狂乱嘲讽」 | 嘲讽一个敌方英雄 | `e_hit` · `e_taunt` |
| 大招「冲天猛撞」 | 缩成球跳起来砸进一片区域，减速，之后余震 3 次（刚滚完时中间的人被击飞） | `r_land` · `r_shock` · `r_hit` · `r_slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、沙尘、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：碎石可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 金色的光（尖刺护盾、撞击）：`#FFFFFF`、`#FFF2C0`、`#FFD266`、`#F2A630`、`#C06E18`、`#7A3E10`；
  - 沙漠黄沙：`#F6E8C4`、`#E2C690`、`#C6A064`、`#9E7A44`、`#6E522C`、`#46321A`；
  - 碎石（实心）：`#D8C8A8`、`#A89070`、`#7A6448`、`#50402E`、`#2E241A`；
  - 熔岩裂纹的橙光：`#FFF4B0`、`#FFC040`、`#FF7A1A`、`#C83C10`、`#6E1C0A`；
  - 嘲讽的红橙火光：`#FFFFFF`、`#FFD8B0`、`#FF9A4A`、`#F05A24`、`#B8301A`、`#6E1A12`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 撞击的半径 18000，大招的半径 36000、中心 18000）。

### 1. `rammus_fx_a_hit.png`：普攻：翻跟头撞中目标，3 帧

他整个翻过去用甲壳撞中目标的一下：一团金白色的撞击闪光，四周溅出几粒沙子（参考 common_hiteffect、spark）。**左右对称**，约 16 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF2C0, #FFD266, #F2A630, #C06E18, #7A3E10) and a desert sand ramp (#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A).
Effect: A HEAVY IMPACT FLASH, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold burst 8 squares across with 8 short rays; 2 the burst 12 squares across, its rays longer and gold, 6 sand grains (1-2 squares) flying out; 3 only a fading gold ring 14 squares across and the grains further out.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `rammus_fx_q_dust.png`：Q 动力冲刺：滚动时球下的沙尘（跟着他，循环），4 帧

缩成球滚动的时候，球底下翻起的一团沙尘：贴着地面的扁扁的沙团，左右两边各甩起一小股沙，几道金色的速度线（参考 rollingforce、sandstreaks、smokeerode）。**只画在地面线附近（球在上面，不画球）**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A) and a gold light ramp (#FFFFFF, #FFF2C0, #FFD266, #F2A630, #C06E18, #7A3E10).
Effect: ROLLING DUST under a ball, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a low flat cloud of sand on the ground (an ellipse 40 squares wide and 8 tall, puffy edge, lighter on top), two small sand plumes kicked up at its left and right ends (mirrored), 4 short gold speed streaks just above it; each frame the puffs boil and the plumes rise and fall.
Layout: one horizontal row of 4 equal 44:14 cells, image size 2816x224 (each cell 704x224, 16 px a square); centered across, the cloud's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `rammus_fx_q_burst.png`：Q：撞上目标时炸开（他身边，跟随），5 帧

球撞上敌人的一瞬间：脚下炸开一圈沙尘冲击波（半径约 18 格，地上的椭圆），中间一团金色的闪光，碎沙往外飞（参考 cloudring、air_swoosh、common_dustcloud）。**他的身体位置留空**（the squat armadillo stands in the middle, not drawn: 36 squares from his tallest spike to the ground, about 35 squares wide）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A) and a gold light ramp (#FFFFFF, #FFF2C0, #FFD266, #F2A630, #C06E18, #7A3E10).
Effect: A SAND SHOCKWAVE bursting out on the ground round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the squat armadillo stands in the middle, not drawn: 36 squares from his tallest spike to the ground, about 35 squares wide): 1 a gold flash 12 squares across at the ground; 2 a sand ring on the ground (an ellipse 24 squares wide and 9 tall, 2-3 squares thick, puffy) and the flash fading; 3 the ring 36 wide and 14 tall, sand grains flying out above it; 4 the ring 44 wide and 18 tall, thinner, breaking into puffs; 5 only scattered thin puffs. The middle above the ground empty.
Layout: one horizontal row of 5 equal 48:28 cells, image size 3840x448 (each cell 768x448, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `rammus_fx_q_hit.png`：Q：撞中的敌人身上，3 帧

被球撞中的敌人：一团金色的撞击闪光和几粒飞溅的沙（参考 common_hiteffect、spark_round_bloom）。**左右对称**，约 16 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF2C0, #FFD266, #F2A630, #C06E18, #7A3E10) and a desert sand ramp (#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A).
Effect: AN IMPACT FLASH, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold star 7 squares across; 2 the star 11 across with 4 sand grains flying out; 3 a fading gold ring 13 across and the grains further out.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `rammus_fx_q_slow.png`：Q：被减速的敌人脚下的沙（循环），4 帧

被撞减速的敌人脚下：一小圈卷着的沙尘贴着地面转（参考 sandstreaks、smokeerode）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A).
Effect: SWIRLING SAND at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ring of sand puffs on the ground (an ellipse 18 squares wide and 6 tall, 2 squares thick), a few grains lifting off it; each frame the puffs move round.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `rammus_fx_w_cast.png`：W 尖刺防御：蜷起来的一下（他身上，跟随），4 帧

他蜷起来进入防御的一下：一圈金色的尖刺光从他身上往外一亮（像甲壳上的刺都在发光），一圈金色的光环炸开（参考 w_spikeshield、w_spikes、w_deflectionripples）。**只画外圈，他的身体位置留空**（the squat armadillo stands in the middle, not drawn: 36 squares from his tallest spike to the ground, about 35 squares wide）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF2C0, #FFD266, #F2A630, #C06E18, #7A3E10).
Effect: A GOLD SPIKE-SHIELD FLARE round a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the squat armadillo stands in the middle, not drawn: 36 squares from his tallest spike to the ground, about 35 squares wide): 1 a ring of 12 short gold light spikes pointing outward round an empty oval 34 squares wide and 34 tall; 2 the spikes longer (5 squares) with white tips and a thin gold ring behind them; 3 the ring 44 squares across expanding, the spikes fading; 4 only a faint thin ring 46 across. The middle (the figure) empty.
Layout: one horizontal row of 4 equal 48:46 cells, image size 3072x736 (each cell 768x736, 16 px a square); centered across, the oval's middle 18 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `rammus_fx_w_on.png`：W：尖刺防御开着（他身上，循环），4 帧

防御开着的 7 秒：他身边一圈淡淡的金色光壳，壳上几根金色小尖刺一闪一闪（参考 w_spikeshield_blur、soccershield）。**只画外圈的壳和刺，中间留空**（the squat armadillo stands in the middle, not drawn: 36 squares from his tallest spike to the ground, about 35 squares wide）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold light ramp (#FFFFFF, #FFF2C0, #FFD266, #F2A630, #C06E18, #7A3E10).
Effect: A FAINT GOLD SPIKED SHELL round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the squat armadillo stands in the middle, not drawn: 36 squares from his tallest spike to the ground, about 35 squares wide): a thin gold outline of light (1 square, no fill) round an empty oval 40 squares wide and 38 tall, 8 small gold spikes (3 squares) on it at mirrored places; each frame a different pair of spikes glints white.
Layout: one horizontal row of 4 equal 44:42 cells, image size 2816x672 (each cell 704x672, 16 px a square); centered across, the oval's bottom 1 square above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `rammus_fx_e_hit.png`：E 狂乱嘲讽：被嘲讽的敌人身上（跟随），4 帧

被嘲讽的一瞬间：敌人身上一团红橙色的火光往上冲，两道红橙色的光弧绕着他（参考 e_terrify_beam、e_energy_01、e_slash）。**左右对称**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange flare ramp (#FFFFFF, #FFD8B0, #FF9A4A, #F05A24, #B8301A, #6E1A12).
Effect: A RED-ORANGE TAUNT FLARE on a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): 1 a red-orange flash 10 squares across at its chest (18 squares up); 2 two mirrored flame-like arcs rising round it from the ground to 30 squares up, white cores; 3 the arcs higher and thinner, a ring of sparks at its feet; 4 only fading sparks rising.
Layout: one horizontal row of 4 equal 24:28 cells, image size 1536x448 (each cell 384x448, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `rammus_fx_e_taunt.png`：E：被嘲讽的敌人头上（循环），4 帧

被嘲讽期间敌人头上：一个红橙色的怒气标记（两道交叉的小火焰 / 一个红色的「！」形光），一跳一跳（参考 e_buff、e_solar_tag）。**画在头上**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，标记在 36–44 格高）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange flare ramp (#FFFFFF, #FFD8B0, #FF9A4A, #F05A24, #B8301A, #6E1A12).
Effect: AN ANGER MARK over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small red-orange flame-like mark (a vertical bar 2 squares wide and 6 tall with a dot under it, white core, glowing edge) with 2 tiny sparks at its sides; each frame it pulses (1 row taller on frames 2 and 3) and the sparks flicker.
Layout: one horizontal row of 4 equal 12:10 cells, image size 768x160 (each cell 192x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `rammus_fx_r_land.png`：R 冲天猛撞：砸在地上（地上，不跟随），6 帧

他从空中砸下来的一下：地面上炸开一个大的沙尘冲击波环（半径约 36 格，地上的椭圆），中间砸出一个裂开的坑，裂缝里透出橙色的熔岩光，碎石往外飞（参考 r_ring_shockwave、r_craterobsi、r_craterlava、r_rocks、r_sand_smoke）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A), a rock ramp (#D8C8A8, #A89070, #7A6448, #50402E, #2E241A) and a glowing lava-crack ramp (#FFF4B0, #FFC040, #FF7A1A, #C83C10, #6E1C0A).
Effect: A GROUND SLAM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 14 squares across on the ground; 2 a cracked crater on the ground (an ellipse 26 wide and 9 tall, dark rock with 6 glowing orange cracks running out) and a sand ring round it (an ellipse 40 wide and 14 tall, puffy, 3 squares thick); 3 the sand ring 60 wide and 22 tall, 6 rock chips (3x3, solid, a dark edge) flying out above it at mirrored places; 4 the ring 76 wide and 28 tall, thinner, the chips falling; 5 the ring breaking into puffs, the crater's cracks dimmer; 6 only the crater with faint cracks and thin puffs.
Layout: one horizontal row of 6 equal 80:40 cells, image size 7680x640 (each cell 1280x640, 16 px a square); centered across, the ellipses' middle 14 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `rammus_fx_r_shock.png`：R：余震（地上，不跟随），4 帧

砸地之后的余震：同一个地方地面又震一下，一圈沙尘波从中间往外推（比落地那圈细），裂缝里的橙光闪一下（参考 r_ring_shockwave、crack_dissolve）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A) and a glowing lava-crack ramp (#FFF4B0, #FFC040, #FF7A1A, #C83C10, #6E1C0A).
Effect: AN AFTERSHOCK on the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 six short glowing orange cracks round an empty middle (an ellipse 24 wide and 8 tall); 2 a thin sand ring (2 squares thick) an ellipse 44 wide and 16 tall, the cracks bright; 3 the ring 64 wide and 24 tall, fainter, the cracks dimming; 4 the ring 74 wide and 28 tall breaking into puffs.
Layout: one horizontal row of 4 equal 76:32 cells, image size 4864x512 (each cell 1216x512, 16 px a square); centered across, the ellipses' middle 12 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `rammus_fx_r_hit.png`：R：被砸中的敌人身上，3 帧

被砸中的敌人：一团沙尘和几块飞起来的碎石（参考 r_rocks、r_burstsmoke）。**左右对称**，约 16 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#F6E8C4, #E2C690, #C6A064, #9E7A44, #6E522C, #46321A) and a rock ramp (#D8C8A8, #A89070, #7A6448, #50402E, #2E241A).
Effect: A SAND AND ROCK BURST, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a sand puff 8 squares across with a gold-white core; 2 the puff 12 across, 4 rock chips (2x2, solid, a dark edge) flying out at mirrored places; 3 the puff fading, the chips further out and lower.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `rammus_fx_r_slow.png`：R：被减速的敌人脚下裂开的地面（循环），2 帧

被冲天猛撞减速的敌人脚下：一小片裂开的地面，裂缝透着橙光，一明一暗（参考 r_craterlava、crack_dissolve）。**左右对称**，2 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rock ramp (#D8C8A8, #A89070, #7A6448, #50402E, #2E241A) and a glowing lava-crack ramp (#FFF4B0, #FFC040, #FF7A1A, #C83C10, #6E1C0A).
Effect: CRACKED GLOWING GROUND at a unit's feet, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat patch of dark cracked rock (an ellipse 18 wide and 6 tall) with 5 thin glowing orange cracks; 1 the cracks dim orange; 2 the cracks bright yellow.
Layout: one horizontal row of 2 equal 20:8 cells, image size 640x128 (each cell 320x128, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `rammus_fx_a_hit` | view_effects `league_rammus_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `rammus_fx_q_dust` | view_effects `league_rammus_q_dust`（跟随，画在人物下面 z -1；左右对称；滚动时一直在放） | 44 × 14 |
| `rammus_fx_q_burst` | view_effects `league_rammus_q_burst`（跟随，画在人物下面 z -1；左右对称；大图表） | 48 × 28 |
| `rammus_fx_q_hit` | view_effects `league_rammus_q_hit`（跟随敌人，画在人物上面 z 2；左右对称） | 16 × 16 |
| `rammus_fx_q_slow` | view_buffs `league_rammus_q_slow`（跟随，画在人物下面 z 3；左右对称；循环，1 秒） | 20 × 8 |
| `rammus_fx_w_cast` | view_effects `league_rammus_w_cast`（跟随，画在人物上面 z 2；左右对称；大图表） | 48 × 46 |
| `rammus_fx_w_on` | view_buffs `league_rammus_w_on`（跟随，画在人物上面 z 3；左右对称；循环，7 秒） | 44 × 42 |
| `rammus_fx_e_hit` | view_effects `league_rammus_e_hit`（跟随敌人，画在人物上面 z 2；左右对称） | 24 × 28 |
| `rammus_fx_e_taunt` | view_buffs `league_rammus_e_taunt`（跟随，画在人物上面 z 3；左右对称；循环） | 12 × 10 |
| `rammus_fx_r_land` | view_effects `league_rammus_r_land`（不跟随，画在人物下面 z -1；左右对称；大图表） | 80 × 40 |
| `rammus_fx_r_shock` | view_effects `league_rammus_r_shock`（不跟随，画在人物下面 z -1；左右对称；大图表；落地后放 3 次） | 76 × 32 |
| `rammus_fx_r_hit` | view_effects `league_rammus_r_hit`（跟随敌人，画在人物上面 z 2；左右对称） | 16 × 16 |
| `rammus_fx_r_slow` | view_buffs `league_rammus_r_slow`（跟随，画在人物下面 z 3；左右对称；循环，1.5 秒） | 20 × 8 |

- 两张表：`asset/league/effects/league_rammus_fx`（小的）和 `league_rammus_big`（q_burst、w_cast、r_land、r_shock），tag = 名字（build_rammus.py 的 views）。
- `q_dust` 在滚动时循环（附加包的整身滚球也放它）；`r_shock` 落地后每 70 tick 放一次、共 3 次；`r_land`、`r_shock` 不跟随（地上的点）。全部左右对称。
- 用 `pixel_1x/` 切格（import_poppy_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（碎石保留描边）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
