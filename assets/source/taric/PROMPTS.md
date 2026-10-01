# 塔里克：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型已定（`design/taric_design.png`，8 倍），动作帧正在画；特效和动作是分开的图，可以先画。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里塔里克自己的特效贴图（蓝青星光、蓝紫宝石切面、Q 的星座符号、R 的金色日冕和光芒），只在本地用，不要提交。颜色和画风对照 `design/taric_design.png`；大小对照 `design/taric_size.png`（游戏里的塔里克 4 倍，红线是地面，白条 18 格、黄条 60 格）：塔里克发顶到脚底 40 格，其他英雄约 35–40 格。
> - 特效照下面第 1–14 条和「所有特效图的规则」画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后打一个 zip。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「正气凌人」 | 斧锤砸击；放完技能后 4 秒内的 2 次普攻变快、附带魔法伤害（身上有星光），命中时星光炸开 | `taric_fx_hit` · `taric_fx_p_hit` · `taric_fx_p_glow` |
| 技能 1 = E「炫光」 | 朝敌人射出一道地上的星光，0.75 秒后整条线爆开，晕眩线上的敌人；灵链相连的队友身边也同时爆开一圈 | `taric_fx_e_beam` · `taric_fx_e_hit` · `taric_fx_e_ally` |
| 技能 2 = Q「星光之触」+ W「坚毅壁垒」 | Q：脚下星光圈，给自己和附近友方英雄回血（相连队友身边也回）；W（12 秒一次）：飞出一颗宝石连到身边队友，给护盾和护甲，脚下留一个灵链印记 | `taric_fx_q_cast` · `taric_fx_q_heal` · `taric_fx_w_bolt` · `taric_fx_w_bind` · `taric_fx_w_link` |
| 大招 = R「宇宙之辉」 | 开团时召唤天上的星光：2.5 秒后自己和附近的友方英雄（相连队友身边也算）无敌 2.5 秒 | `taric_fx_r_call` · `taric_fx_r_shine` · `taric_fx_r_invuln` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（按每条写的用）：
  - 星光（主体，蓝青到白）：`#FFFFFF`、`#E4FAFF`、`#A8ECFF`、`#5CD2FF`、`#2A9BE8`、`#1F5FC8`、`#1A2E8A`；
  - 宝石（紫蓝，和他肩甲、武器上的宝石同色系）：`#F4EEFF`、`#C9B8FF`、`#9A7CF6`、`#6A4CE0`、`#45309E`；
  - 宇宙之辉的金光（只用在 R 的三张）：`#FFFFFF`、`#FFF6D6`、`#FFE08A`、`#F6B94A`、`#D97F2A`。
  - 塔里克眼睛的天蓝 `#279FF6` 不要用（游戏按这个颜色找他的眼睛）。
- **飞行类和光束类特效一律朝右画，而且上下对称**：游戏会把它转到方向上，向左时整张图转 180°。
- 命中、爆开、范围特效居中画，不旋转；地面上的圆是从斜上方看的扁椭圆（宽是高的 2 倍左右）。
- 套在英雄身上的特效（强化、晕眩、回血、护盾、无敌）：格子中间留出一个空的人形位置，不要画人，**不能挡住身体和脸**，只画外面的星光、宝石和光边。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张特效的提示词都以同一段画风开头。大小写在每条里（游戏像素），导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `taric_fx_hit.png`：普攻命中，5 帧

斧锤砸中目标：一道短的银紫色弧形斩光，中间一颗白色亮点，碎出几颗小星星（参考 BA 的扭曲环、z_little_spark）。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A) with lilac-silver gem tones (#F4EEFF, #C9B8FF, #9A7CF6, #6A4CE0, #45309E).
Effect: a MACE-AXE IMPACT, 5 frames: 1 a small white flash at the center; 2 a short curved slash of lilac-silver light across the center with a white core; 3 the slash breaks into small blue-white star sparks flying outward; 4 the sparks spread and dim; 5 a few faint violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `taric_fx_p_hit.png`：正气凌人的强化普攻命中，6 帧

强化普攻砸中：一颗亮白的四角星在目标身上炸开，外面一圈青蓝星光和几片紫色宝石碎片往外飞（参考 z_star、W_gem_tex）。比普攻命中大一点、亮一点。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A) with violet gem shards (#F4EEFF, #C9B8FF, #9A7CF6, #6A4CE0, #45309E).
Effect: a BRAVADO STRIKE, 6 frames: 1 a bright white four-pointed star flash at the center; 2 the star opens to full size, its long points white-cyan, a ring of blue starlight around it; 3 small violet crystal shards burst outward from it, the star fading to cyan; 4 the shards fly further, a few tiny white stars twinkle; 5 the shards and stars dim to deep blue; 6 two or three faint specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `taric_fx_p_glow.png`：正气凌人的强化状态（塔里克身上，循环），4 帧

放完技能后两次普攻变强的 4 秒里，塔里克身边绕着几颗小的青白星点和一两颗紫色宝石光点，在腰和武器的高度转（参考 P_buf_weapon、z_gem_whisps）。中间留空人形，不挡脸。约 36 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A) with violet gem sparks (#F4EEFF, #C9B8FF, #9A7CF6, #6A4CE0, #45309E).
Effect: BRAVADO, a charged aura around a standing figure (leave a figure-shaped empty space in the middle, about 60% of the cell width and 80% of the cell height - do NOT draw the figure), 4 frames, a seamless loop: five or six small blue-white four-pointed star sparks and two violet gem glints orbiting the figure at waist and hand height, the ones behind the figure dimmer; they move a quarter turn each frame and twinkle; nothing covers the face.
Layout: one horizontal row of 4 equal cells, each 3 wide to 4 tall, image size 1152x384 (each cell 288x384); centered horizontally. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `taric_fx_e_beam.png`：E 炫光的星光光束（地上一条线，先蓄力再爆开），12 帧

塔里克朝前方射出一道星光：先是地上一条细细的蓝白光线，线上一颗颗小星星慢慢亮起、变粗（蓄力 0.75 秒），然后整条线一起炸开成一道耀眼的白蓝光带、两边溅出星光，再很快散掉（参考 E_beam_mult、E_cas_boundingbox、z_light_rays）。**整张图朝右画、上下对称**，线从格子最左边一直到最右边（左端就是塔里克）。约 64 格长、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A).
Effect: DAZZLE, a beam of starlight lying straight along the ground from the LEFT edge to the RIGHT edge of the cell, SYMMETRIC above and below the middle line, 12 frames: 1 a thin faint blue line (1-2 squares thick) across the whole cell; 2-8 the charge: the line slowly brightens and thickens to about a quarter of the cell height, small four-pointed stars light up one by one along it, pale cyan (#A8ECFF) to white at its core; 9 the burst: the whole line flares into a wide dazzling white-cyan band filling the cell height, star sparks spraying off both edges; 10 the band breaks into a row of bright stars; 11 the stars fade to blue; 12 a few faint blue specks along the line.
Layout: one horizontal row of 12 equal cells, each 16 wide to 5 tall, image size 6144x384 (each cell 512x160) - or, if that is too wide for one image, 3 rows of 4 cells (2048x480), read left to right, top to bottom; the beam on the middle line of every cell, touching the left and right edges. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `taric_fx_e_hit.png`：E 炫光击中并晕眩敌人，6 帧

被光束晕眩的敌人身上：一团耀眼的白光闪一下，然后头顶一圈小星星转两圈（晕眩），星星是青白和淡紫色（参考 z_star、Q_star）。中间留空人形，不画人。约 26 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A) with lilac stars (#F4EEFF, #C9B8FF, #9A7CF6, #6A4CE0, #45309E).
Effect: a DAZZLING STUN on a standing figure (leave a figure-shaped empty space in the middle - do NOT draw the figure), 6 frames: 1 a burst of white-cyan light on the figure's chest with short rays; 2 the rays fade, a small ring of five tiny four-pointed stars appears above the figure's head (cyan and lilac); 3-5 the ring of stars circles over the head (a quarter turn each frame), twinkling; 6 the stars fade.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1728x384 (each cell 288x384); centered horizontally, the star ring near the top of the cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `taric_fx_e_ally.png`：E 炫光在相连队友身边爆开（地上一圈），12 帧

灵链相连的队友身边也放一次炫光：地上一个扁椭圆的星光圈，先蓄力 0.75 秒（圈上的小星星一颗颗亮起），然后整圈炸开成一圈耀眼的白蓝光、往上溅出星光，再散掉（参考 R_cas_ring、Passive 的双色光环）。宽是高的 2 倍。约 44 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A).
Effect: DAZZLE AROUND AN ALLY, a flat ellipse of starlight on the ground (twice as wide as tall) filling the cell, 12 frames with the same timing as a charge-and-burst: 1 a faint thin blue ellipse; 2-8 small four-pointed stars light up one by one around the ellipse, the ring brightening to pale cyan; 9 the burst: the whole ring flares white-cyan and thick, star sparks spraying up and out; 10 a wider, thinner bright ring; 11 it fades to blue; 12 a few faint specks.
Layout: one horizontal row of 12 equal cells, each 2 wide to 1 tall, image size 6144x256 (each cell 512x256) - or 3 rows of 4 cells (2048x768); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `taric_fx_q_cast.png`：Q 星光之触：塔里克脚下的星光圈，8 帧

塔里克举手召来星光：地上一个大的扁椭圆星光圈（就是回血范围），圈上的蓝白星星往外亮开，圈里升起几道细细的光（参考 Q_hand_symbol、Q_star、Bokeh_dots）。宽是高的 2 倍。约 64 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A).
Effect: STARLIGHT'S TOUCH, a circle of starlight on the ground around a standing figure (a flat ellipse twice as wide as tall filling the cell - do NOT draw the figure), 8 frames: 1 a small bright white-cyan spark at the center; 2 a ring of light expands outward from it; 3 the ring reaches the cell's edges as a thin bright ellipse, blue-white four-pointed stars appear on it; 4-5 thin vertical rays of pale starlight rise from inside the ring, the stars twinkle; 6 the rays fade upward; 7 the ring dims to blue; 8 a few faint specks.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 4096x256 (each cell 512x256) - or 2 rows of 4 cells (2048x512); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `taric_fx_q_heal.png`：Q 星光之触回血（每个被治疗的友方英雄身上），6 帧

被治疗的英雄身上：蓝白的小星星和一点淡绿的光从脚下往上升，旁边一个亮的小十字星，升到头顶散开（参考 Q_star、z_add_glow）。中间留空人形，不画人。约 24 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A) with a touch of healing mint (#D8FFE8, #8CF7C8).
Effect: a STARLIGHT HEAL rising around a standing figure (leave a figure-shaped empty space in the middle, about 60% of the cell width and 80% of the cell height - do NOT draw the figure), 6 frames: 1 a ring of small blue-white star sparks around the figure's feet; 2 the sparks rise to its waist, a bright four-pointed star appears beside its shoulder, a faint mint glow; 3 the sparks and the star rise to its chest, twinkling; 4 they reach the head height; 5 they fade to pale blue; 6 a few faint specks above the head.
Layout: one horizontal row of 6 equal cells, each 2 wide to 3 tall, image size 1536x384 (each cell 256x384); centered horizontally. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `taric_fx_w_bolt.png`：W 坚毅壁垒：塔里克连到队友的宝石星光（飞行），4 帧循环

从塔里克飞向队友的一颗小宝石：前面是一颗亮的蓝紫色宝石（带白色高光），后面拖着一道青白的星光尾巴和两三颗小星（参考 W_mis_stars、W_gem_tex）。朝右画、上下对称。约 16 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#F4EEFF, #C9B8FF, #9A7CF6, #6A4CE0, #45309E) with a starlight trail (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A).
Effect: BASTION, a small flying gem to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a faceted blue-violet gem with a white glint at 70% of the cell width, about 45% of the cell height; behind it a tapering trail of cyan-white starlight with two or three tiny stars to the left edge; the trail twinkles each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the gem on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `taric_fx_w_bind.png`：W 坚毅壁垒：队友得到护盾的瞬间，6 帧

被连上的队友身上：一面蓝紫色的晶体护盾（由几片棱面组成）在他身前闪现，外沿一圈白光，然后化成星光散开（参考 W_gem_sheen、W_solar-corona 的圆环、W_ally_ring）。中间留空人形，**不能挡住脸和身体**，护盾只画轮廓和几片透亮的棱面。约 32 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#F4EEFF, #C9B8FF, #9A7CF6, #6A4CE0, #45309E) with starlight edges (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A).
Effect: a CRYSTAL SHIELD forming around a standing figure (leave a figure-shaped empty space in the middle - do NOT draw the figure, and do not cover it: only the shield's outline and a few see-through facets), 6 frames: 1 small violet crystal shards gather around the figure; 2 they join into the outline of a faceted blue-violet crystal shell around the figure, a white rim of light; 3 the shell shines, a white glint sweeping across it; 4 the shell holds, facets glinting; 5 it breaks into small violet and cyan stars; 6 the stars fade.
Layout: one horizontal row of 6 equal cells, each 4 wide to 5 tall, image size 1536x320 (each cell 256x320); centered horizontally. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `taric_fx_w_link.png`：W 灵链：相连队友脚下的宝石印记（循环），4 帧

和塔里克相连的队友脚下：一个扁椭圆的蓝紫色细光圈，圈上一颗菱形宝石和几颗小星星慢慢转，表示灵链还连着（参考 W_ally_ring、z_ring_glow）。宽是高的 2.5 倍。约 30 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#F4EEFF, #C9B8FF, #9A7CF6, #6A4CE0, #45309E) with starlight sparks (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A).
Effect: the BASTION LINK, a sigil on the ground under a figure's feet (the figure is NOT drawn), 4 frames, a seamless loop: a flat thin ellipse (2.5 times as wide as tall) of blue-violet light filling the cell, a small diamond-shaped gem on its front edge and three tiny stars on the ring; the gem and the stars travel a quarter of the way round the ring each frame, the parts behind dimmer.
Layout: one horizontal row of 4 equal cells, each 5 wide to 2 tall, image size 1280x128 (each cell 320x128); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `taric_fx_r_call.png`：R 宇宙之辉：召唤星光（2.5 秒，塔里克和相连队友身上），10 帧

塔里克举起武器召唤天上的保护：头顶上方出现一个金白色的星座光环（像日冕的圆环，环上几颗星），慢慢变亮，一束金色的光柱从上往下一点点降下来，最后正好落到人身上爆亮（参考 R_cas_ring、R_cas_star、R_lightray、W_solar-corona）。这张图要撑满 2.5 秒。中间下半部分留空人形。约 48 格宽、96 格高（人站在格子最下面，光环在人头顶上方很高的地方）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #FFF6D6, #FFE08A, #F6B94A, #D97F2A) with a little starlight blue (#FFFFFF, #E4FAFF, #A8ECFF, #5CD2FF, #2A9BE8, #1F5FC8, #1A2E8A).
Effect: COSMIC RADIANCE, the heavens answer a standing figure: the figure stands at the BOTTOM of a tall cell (leave its space empty in the lower third - do NOT draw the figure), 10 frames: 1 a faint golden sparkle high in the top of the cell; 2-3 a golden-white halo ring like a solar corona forms there, a few four-pointed stars on it; 4-6 the halo brightens and thin golden rays begin to stream down from it; 7-8 a column of golden light descends step by step toward the figure's head, the halo blazing; 9 the column of light reaches the figure and floods its space with white-gold light; 10 a bright starburst flash where the figure stands, the halo gone.
Layout: one horizontal row of 10 equal cells, each 1 wide to 2 tall, image size 2560x512 (each cell 256x512); the figure's feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `taric_fx_r_shine.png`：R 宇宙之辉生效：每个友方英雄身上的金光一闪，6 帧

无敌生效的那一刻：金白色的光从人身上爆开，几道长长的金色光芒和四角星向外射，然后收成一层淡金的光（参考 R_cas_star、z_light_rays）。中间留空人形，不画人。约 36 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #FFF6D6, #FFE08A, #F6B94A, #D97F2A).
Effect: a RADIANT INVULNERABILITY FLASH on a standing figure (leave a figure-shaped empty space in the middle - do NOT draw the figure), 6 frames: 1 a burst of white-gold light at the figure's chest; 2 long golden rays shoot out in all directions, a big four-pointed star; 3 the rays at full length, small gold stars around the figure; 4 the rays shorten, a pale gold outline glows around the figure's space; 5 the outline glows fainter; 6 a few gold specks.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1728x384 (each cell 288x384); centered horizontally. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `taric_fx_r_invuln.png`：R 宇宙之辉：无敌期间身上的金色光罩（循环，2.5 秒），4 帧

无敌的 2.5 秒里：人身上罩着一层淡金色的光，外沿一圈金白色的细光边，几颗小金星绕着慢慢转（参考 R_Buff_body_glow）。中间留空人形，**只画外面的光边和星星，不能盖住人**。约 34 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, starlight colours (#FFFFFF, #FFF6D6, #FFE08A, #F6B94A, #D97F2A).
Effect: an INVULNERABILITY GLOW around a standing figure (leave a figure-shaped empty space in the middle - do NOT draw the figure and do not cover it), 4 frames, a seamless loop: a thin white-gold rim of light following the figure's silhouette, a soft pale-gold glow just outside it, four small gold four-pointed stars circling the figure (the ones behind dimmer); the stars move a quarter turn each frame and the rim shimmers.
Layout: one horizontal row of 4 equal cells, each 3 wide to 4 tall, image size 1152x384 (each cell 288x384); centered horizontally. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `taric_fx_hit` | view_effects `league_taric_hit` | 16 |
| `taric_fx_p_hit` | view_effects `league_taric_p_hit` | 22 |
| `taric_fx_p_glow` | view_buffs `league_taric_brav_as` | 36 × 40 |
| `taric_fx_e_beam` | view_projectiles `league_taric_e_beam`（光束本身） | 64 × 20 |
| `taric_fx_e_hit` | view_effects `league_taric_e_hit`（跟随） | 26 |
| `taric_fx_e_ally` | view_effects `league_taric_e_ally`（画在人物下面，不跟随） | 44 × 22 |
| `taric_fx_q_cast` | view_effects `league_taric_q_cast`（跟随，画在人物下面） | 64 × 32 |
| `taric_fx_q_heal` | view_effects `league_taric_q_heal`（跟随） | 24 × 34 |
| `taric_fx_w_bolt` | view_projectiles `league_taric_w_bolt` | 16 × 8 |
| `taric_fx_w_bind` | view_effects `league_taric_w_bind`（跟随） | 32 × 40 |
| `taric_fx_w_link` | view_buffs `league_taric_w_link`（画在人物下面） | 30 × 12 |
| `taric_fx_r_call` | view_effects `league_taric_r_call`、`league_taric_r_call_ally`（跟随） | 48 × 96 |
| `taric_fx_r_shine` | view_effects `league_taric_r_shine`（跟随） | 36 × 44 |
| `taric_fx_r_invuln` | view_buffs `league_taric_r_invuln` | 34 × 44 |

- 时长：E 的光束和队友身边的圈 12 帧，前 8 帧撑满 0.75 秒（出手后第 45 tick 爆开）、后 4 帧 0.2 秒；R 的召唤 10 帧撑满 2.5 秒，第 9–10 帧在第 150 tick；R 的光罩和正气凌人的强化是 buff 的循环画面。
- 光束（`e_beam`）是 `LineRangeProjectile` 的画面：中心在光束中点、朝施法方向转，左端在塔里克身上；长 62000、宽 18000（约 62×18 格，画得稍宽）。
- `e_ally`、`q_cast`、`w_link` 画在人物下面（z −1），放在脚底线上；`r_call` 的格子底部对着脚底。
