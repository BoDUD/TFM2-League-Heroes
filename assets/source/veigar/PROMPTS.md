# 维迦：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图。** 造型（用户选的 B，法杖最下面错开的一小块删掉了）和 8 个动作（Codex 拼的动作帧，法杖单独转正）已经导入游戏，这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里维迦自己的特效贴图（E 牢笼的紫色光柱和黄色符文 `Veigar_Base_E_Pillar`、牢笼墙的能量 `E_WallEnergy`、地面光 `E_GroundGlow`，W 的圆环和天光 `W_Circle`、`W_SkyRays`，R 的空心球和电弧 `R_HollowOrb`、`R_Arcs`、地面灼痕 `R_ground_burn`，Q 和普攻的拖尾 `Q_Mis_Trail`、`BA_Trail`），只在本地用，不要提交。颜色和画风对照 `design/veigar_design.png`（定稿造型，8 倍）；大小对照 `design/veigar_ingame.png`（游戏里的全部帧，3 倍，绿线是脚底线）：维迦帽尖到脚底 40 格，其他英雄约 35–47 格。
> - 特效照下面第 1–12 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里的 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「超凡邪力」 | 法杖射出暗能量弹；技能每打中敌方英雄、黑暗祭祀每击杀单位、每击杀英雄，维迦永久叠法术强度（死亡清空），叠层时身上闪一下紫光 | `veigar_fx_orb` · `veigar_fx_hit` · `veigar_fx_p_gain` |
| 技能 1 = Q「黑暗祭祀」 | 一束黑暗能量飞出去，打中最先碰到的两个敌人 | `veigar_fx_q_bolt` · `veigar_fx_q_hit` |
| 技能 2 = E「扭曲空间」+ W「黑暗物质」 | 在敌方英雄脚下 0.4 秒后成形一个牢笼，持续 3 秒，碰到的敌人眩晕 1 秒；牢笼成形 0.75 秒后黑暗物质从天上砸进牢笼中心 | `veigar_fx_e_cage` · `veigar_fx_e_stun` · `veigar_fx_w_fall` · `veigar_fx_w_hit` |
| 大招 = R「能量爆裂」 | 跳起高举法杖，射出一团原始魔法轰向敌方英雄 | `veigar_fx_r_cast` · `veigar_fx_r_bolt` · `veigar_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（三套，按每条写的用）：
  - 暗紫能量（主体，维迦的招牌色）：`#FFFFFF`、`#EBDDFF`、`#BE95FF`、`#8F52F5`、`#5E27C8`、`#3B138A`、`#210A52`；
  - 虚空暗色（黑暗物质的核、地面焦痕）：`#2A1A40`、`#1A0E2E`、`#0E0718`；
  - 金色符文（牢笼的符文、叠层的火花，和他的眼睛、法杖水晶同一种邪恶的黄）：`#FFF6B0`、`#FFD84A`、`#E8A020`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- 命中、爆开、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在英雄身上的特效（叠层的光）：格子中间留出一个空的人形位置（约 36 格宽、40 格高，脚在格子下方），不要画人，**不能挡住身体和脸**，只画围在外面的光和火花。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `veigar_fx_orb.png`：普攻暗能量弹（飞行，循环），4 帧

法杖射出的小暗能量弹：一颗紫白色的亮核，外面裹一圈暗紫的能量，后面拖一小截紫色的尾巴（参考 `Veigar_Base_BA_Trail2`）。**朝右飞，上下对称。** 约 12 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A, #210A52).
Effect: a small DARK MAGIC BOLT flying to the right, 4 frames, a seamless loop: a white-violet core at the right end wrapped in dark violet energy, a short tapering violet tail trailing to the left; the tail flickers and its wisps shift a little each frame. Symmetric top to bottom.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the bolt centered in every cell, about 80% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `veigar_fx_hit.png`：普攻命中，5 帧

暗能量弹打中：一个紫白色的小爆点，几道暗紫的碎光往外迸。约 12 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A).
Effect: a small DARK MAGIC IMPACT, 5 frames: 1 a tiny white flash; 2 a white-violet burst about half the cell wide with short violet rays; 3 the burst opens into a violet ring, a few dark violet shards flying outward; 4 the ring thins, the shards scatter; 5 a few faint dark violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `veigar_fx_p_gain.png`：超凡邪力叠层（在他身上），5 帧

维迦叠到一层邪力时身上闪一下：几颗紫色的小光点从四周飞进他的身体，带一点金色火花（英雄联盟里是小紫球飞向维迦），最后在胸口一闪。**中间留空人形，不挡脸。** 约 44 格宽、46 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8) with a few evil gold sparks (#FFF6B0, #FFD84A, #E8A020).
Effect: EVIL POWER ABSORBED around a standing figure (leave a figure-shaped empty space in the middle, about 80% of the cell width and 85% of the cell height, feet at the bottom - do NOT draw the figure), 5 frames: 1 four small violet motes appear at the edges of the cell; 2 they streak inward toward the figure's chest with short violet trails and tiny gold sparks; 3 they reach the empty figure's outline; 4 a small violet-white flash at chest height on the figure's outline, a few gold sparks; 5 the last faint sparks fade.
Layout: one horizontal row of 5 equal cells, each 1 wide to 1 tall, image size 1280x256 (each cell 256x256), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `veigar_fx_q_bolt.png`：黑暗祭祀（飞行，循环），4 帧

Q 的能量束：比普攻大得多的一团暗紫能量，前面是白紫色的亮核，身上缠着几道紫色的电弧，后面拖一条长长的、边缘撕裂的暗紫尾巴（参考 `Veigar_Base_Q_Mis_Trail`、`Q_Trail2`）。**朝右飞，上下对称。** 约 22 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A, #210A52).
Effect: a BOLT OF DARK ENERGY flying to the right, 4 frames, a seamless loop: a bright white-violet head at the right end, a thick dark violet body with two thin violet lightning arcs crackling around it, and a long ragged dark violet tail trailing to the left that breaks into wisps; the arcs and the tail's wisps change every frame. Symmetric top to bottom.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the bolt about 90% of the cell wide, centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `veigar_fx_q_hit.png`：黑暗祭祀命中，5 帧

能量束打中：暗紫色的能量炸开，中间一个暗色的漩涡一闪，四周迸出紫色碎片。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A) with void darks (#2A1A40, #1A0E2E).
Effect: a DARK ENERGY BURST, 5 frames: 1 a white-violet flash; 2 a violet burst about 70% of the cell wide with a dark void swirl at its center; 3 the burst at full size, jagged violet shards flying outward; 4 the burst breaks apart into shards and dark wisps; 5 a few fading violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `veigar_fx_e_cage.png`：扭曲空间的牢笼（地面，3 秒），10 帧

E 的牢笼：地面上一个紫色的椭圆边界，边上立起一圈暗紫色的能量墙，墙上闪着几个金色的符文（参考 `Veigar_Base_E_Pillar`、`E_WallEnergy`、`E_GroundGlow`、`E_warning_Trail`）。第 1–3 帧成形（边界亮起、墙从地面升起），第 4–7 帧是循环（墙上的能量往上流动、符文闪烁），第 8–10 帧消散。**中间是空的**（被困的人站在里面），只画边界和墙。约 64 格宽；墙高约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A, #210A52) with evil gold runes (#FFF6B0, #FFD84A, #E8A020).
Effect: an ENERGY CAGE on the ground, seen from above at an angle: its boundary is an ellipse twice as wide as it is tall at the bottom of the cell, and a ring of translucent-looking (but solid-pixel) dark violet energy walls rises from that ellipse about a third of the cell height; the inside of the ring stays EMPTY (a trapped figure stands there). 10 frames: 1 a thin bright violet ellipse flashes on the ground; 2 low violet walls begin to rise from it; 3 the walls at full height, a few gold runes lighting up on them; 4-7 a seamless loop: energy streaks flow upward along the walls, the gold runes flicker, the ground ellipse pulses a little; 8 the walls sink; 9 only the ellipse remains, dimming; 10 faint violet specks.
Layout: one horizontal row of 10 equal cells, each 2 wide to 1 tall, image size 2560x128 (each cell 256x128); the ellipse about 90% of each cell wide with its bottom near the cell's bottom edge, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `veigar_fx_e_stun.png`：牢笼眩晕（在被晕的人头顶，循环），4 帧

被牢笼晕住：头顶一圈暗紫色的扭曲星环，转着两颗金色的小星（和普通眩晕星区别开：是紫色的空间扭曲）。4 帧循环。约 16 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8) with gold stars (#FFF6B0, #FFD84A).
Effect: a STUN MARK above a head, 4 frames, a seamless loop: a small flat violet ellipse of twisted space (twice as wide as tall) with two tiny gold four-point stars circling along it; each frame the stars move a quarter of the way round and the ellipse's bright spot shifts.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `veigar_fx_w_fall.png`：黑暗物质下落并爆炸，9 帧

W：牢笼成形的同时，天上一团黑暗物质（黑紫色的球体，边缘一圈紫色的光，拖着向上的紫色尾迹）往下砸（参考 `W_SkyRays`、`W_Circle`）。第 1–5 帧下落（第 1 帧地上先出现一个暗紫色的落点圈，球从格子顶部落下，越来越低），第 6 帧砸到地面（落点圈的正中）：白紫色的闪光，第 7–9 帧爆开：一圈暗紫色的冲击波在地面扩散、碎片飞起、留下暗色的焦痕然后消失。爆炸宽约 44 格；格子是竖的（上面留出下落的空间）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A, #210A52) with void darks (#2A1A40, #1A0E2E, #0E0718).
Effect: DARK MATTER FALLING ONTO THE GROUND, 9 frames; the landing point is the center of a ground ellipse (twice as wide as tall) at the bottom of every cell: 1 a dim violet target ellipse appears on the ground, and a dark sphere (void black-violet core, a glowing violet rim) appears at the top of the cell; 2-5 the sphere falls straight down toward the ellipse's center, a violet trail streaming up behind it, the target ellipse brightening; 6 the impact: a white-violet flash at the ellipse's center, as wide as the ellipse; 7 a violet shockwave ring spreads along the ground to the ellipse's edge, dark shards thrown up; 8 the ring fades, a dark scorched ellipse on the ground with violet embers; 9 faint embers.
Layout: one horizontal row of 9 equal cells, each 3 wide to 4 tall (192x256), image size 1728x256; the ground ellipse about 90% of each cell wide at its bottom, the sphere starting near the cell's top, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `veigar_fx_w_hit.png`：黑暗物质命中（在被砸中的人身上），5 帧

被黑暗物质砸中：身上迸出一团暗紫色的能量和黑色的碎块。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A) with void darks (#2A1A40, #1A0E2E).
Effect: a DARK MATTER HIT on a target, 5 frames: 1 a violet flash; 2 a burst of dark violet energy with black void chunks; 3 the chunks fly up and outward, violet sparks; 4 the chunks fall, the energy thins; 5 a few fading specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `veigar_fx_r_cast.png`：能量爆裂施法（在他高举的法杖头上），5 帧

维迦跳起高举法杖时，法杖头上聚起一团原始魔法：紫白色的光球迅速变大，四周转着几道紫色电弧，最后一闪（光球从这里飞出去）。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A) with a few gold sparks (#FFF6B0, #FFD84A).
Effect: PRIMAL MAGIC GATHERING at a staff's tip, 5 frames: 1 a small violet spark with a few gold motes drawn in; 2 a violet-white orb grows, two violet lightning arcs crackling round it; 3 the orb at full size (about 60% of the cell), bright white core, arcs flaring; 4 a bright white-violet flash as it is released; 5 fading violet sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `veigar_fx_r_bolt.png`：能量爆裂（飞行，循环），4 帧

R 射出的一团原始魔法：一个大的暗紫色光球，中间白紫色的亮核，外面一圈空心的紫色光环（参考 `Veigar_Base_R_HollowOrb`），缠着紫色电弧（`R_Arcs`），后面拖一条短的紫色尾巴。**朝右飞，上下对称。** 约 20 格长、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A, #210A52).
Effect: an ORB OF PRIMAL MAGIC flying to the right, 4 frames, a seamless loop: a big round orb with a bright white-violet core and a hollow violet halo ring around it, violet lightning arcs crackling on the halo, a short violet tail trailing to the left; the arcs change every frame and the halo pulses. Symmetric top to bottom.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 1152x192 (each cell 288x192); the orb centered toward the right of each cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `veigar_fx_r_hit.png`：能量爆裂命中，7 帧

原始魔法轰中敌方英雄：一个大爆炸——白紫色的强光、暗紫色的能量球炸开、一圈电弧向外甩、地上留下紫黑色的灼痕（参考 `R_ground_burn`）。是维迦最大的一下，约 30 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dark violet energy ramp (#FFFFFF, #EBDDFF, #BE95FF, #8F52F5, #5E27C8, #3B138A, #210A52) with void darks (#2A1A40, #1A0E2E) and a few gold sparks (#FFF6B0, #FFD84A).
Effect: a PRIMAL BURST EXPLOSION on a target, 7 frames: 1 a white flash; 2 a violet-white sphere bursts out to about 60% of the cell; 3 the sphere at full size (about 90% of the cell), violet lightning arcs whipping outward, gold sparks; 4 the sphere breaks into a ring of violet energy and dark void shards; 5 the ring expands and thins, arcs fading; 6 dark violet smoke and a few embers; 7 faint embers.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```
