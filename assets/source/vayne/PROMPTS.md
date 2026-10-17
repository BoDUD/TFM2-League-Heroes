# 薇恩：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型和动作已经做完并导入游戏（跑步的腿另外在重画），这一轮只画特效，不画人。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里薇恩原皮自己的特效贴图（普攻的光斑和烟尾、圣银弩箭的三个环、闪避突袭的烟、恶魔审判撞墙的尘土、终极时刻的四角星地纹和蝙蝠），只在本地用，不要提交。英雄联盟的贴图大多是灰白的遮罩，游戏里才上色：**形状照它，颜色照下面的规则**。
> - 颜色和画风对照 `design/vayne_design.png`（定稿造型，8 倍）；大小对照 `design/vayne_ingame.png`（游戏里的全部帧，3 倍，绿线是脚底线，蓝线是站位点）：薇恩从马尾顶到脚底 48 格，其他英雄约 35 格。
> - 特效照下面第 1–14 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「暗夜猎手」+ W「圣银弩箭」 | 右前臂的腕弩射出银色弩箭；她的命中在目标身上叠圣银环，第 3 次命中爆开造成真实伤害（附近有敌方英雄时加移速，不用画） | `vayne_fx_bolt` · `vayne_fx_hit` · `vayne_fx_sb_ring1` · `vayne_fx_sb_ring2` · `vayne_fx_sb_proc` |
| 技能 1 = Q「闪避突袭」 | 翻滚一下（出发的地方留一团烟），下一次普攻是强化箭，额外伤害 | `vayne_fx_q_roll` · `vayne_fx_q_bolt` · `vayne_fx_q_hit` |
| 技能 2 = E「恶魔审判」 | 用背后的大弩射出重箭，打中英雄把他击退，落地时再受伤并眩晕 1 秒（英雄联盟里是撞到墙） | `vayne_fx_e_bolt` · `vayne_fx_e_hit` · `vayne_fx_e_stun` |
| 大招 = R「终极时刻」 | 8 秒内攻击力提高、技能冷却变快，翻滚时隐身；期间击杀英雄会刷新 | `vayne_fx_r_cast` · `vayne_fx_r_aura` · `vayne_fx_r_refresh` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（四套，从她的造型取：银弩和银甲、暗夜猎手的夜色、红披风；按每条写的用）：
  - 银光（主体）：`#FFFFFF`、`#EEF0FF`、`#C8CAE8`、`#9A9CC8`、`#6A6E9E`；
  - 夜紫烟（暗部、烟、蝙蝠）：`#5A3C84`、`#3A2660`、`#22163C`、`#140C24`；
  - 猩红（圣银弩箭爆开、重箭的光、终极时刻的刷新）：`#FFD0D6`、`#FF5A6E`、`#D8203E`、`#8F0B24`；
  - 尘土（恶魔审判的撞击）：`#E0D2B0`、`#B09878`、`#7A6448`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、爆开、标记居中画，不旋转；地面上的形状按游戏的斜俯视角度画成扁的（宽约是高的 2 倍）。
- 套在薇恩身上的特效（终极时刻）：格子中间留出一个空的人形位置（按那条写的比例），不要画人，**不能挡住身体和脸**，只画围在外面的光、烟和蝙蝠。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `vayne_fx_bolt.png`：普攻弩箭（飞行），4 帧循环

腕弩射出的一支银色弩箭：细长的钢杆、尖尖的银色箭头、尾部两片小尾羽，后面拖一小段夜紫色的烟尾（参考 BA_SmokeTip、BA_LensFlare）。约 12 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E) with night-purple smoke (#5A3C84, #3A2660, #22163C).
Effect: a CROSSBOW BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a thin steel shaft with a sharp bright silver arrowhead at 80% of the cell width and two small fletchings at its back end; behind it a short tapering night-purple smoke trail to the left edge of the cell; a tiny white glint on the arrowhead moves each frame and the trail's wisps change shape.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the bolt on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `vayne_fx_q_bolt.png`：闪避突袭的强化箭（飞行），4 帧循环

翻滚后那一箭：比普攻箭大，整支箭裹着亮银白的光，箭头前有一个小十字光点，后面拖着一道更长、更浓的夜紫色烟尾，烟里闪着银色碎光（参考 Q_Glow、Q_WispySmoke）。约 18 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E) with night-purple smoke (#5A3C84, #3A2660, #22163C, #140C24).
Effect: an EMPOWERED CROSSBOW BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bolt wrapped in bright silver-white light at 75% of the cell width, a small four-pointed white glint in front of its tip; behind it a long thick night-purple smoke trail swirling to the left edge, with small silver sparkles inside the smoke; the glint pulses and the smoke curls change each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1536x128 (each cell 384x128); the bolt on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `vayne_fx_e_bolt.png`：恶魔审判的重箭（飞行），4 帧循环

背后大弩射出的重箭：粗大的银色箭杆，宽大的三角形银箭头，箭头上一道猩红的反光，后面拖着一道粗的夜紫色烟尾和几缕猩红火星（参考 E_Glow、E_SmokeShape01）。约 24 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E), night-purple smoke (#5A3C84, #3A2660, #22163C, #140C24) and crimson accents (#FF5A6E, #D8203E).
Effect: a HEAVY SILVER BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a thick silver shaft with a broad triangular silver arrowhead at 80% of the cell width, a crimson glint along the arrowhead's edge; behind it a thick night-purple smoke trail with a few crimson sparks streaming to the left edge; the glint and the sparks move each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1536x128 (each cell 384x128); the bolt on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `vayne_fx_hit.png`：普攻命中，5 帧

弩箭打中目标：一个小小的银白色 V 形火花（参考 Hit_Spark），中心一下白光，几粒夜紫色的碎屑。约 12 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8) with night-purple specks (#5A3C84, #3A2660).
Effect: a BOLT IMPACT, 5 frames: 1 a tiny white flash at the center; 2 a sharp silver V-shaped spark opening to the right with a white core, about 50% of the cell wide; 3 the spark breaks into a few silver chips flying outward, small purple specks; 4 the chips fly further and dim; 5 two or three faint specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `vayne_fx_q_hit.png`：强化箭命中，6 帧

强化箭打中：一颗亮白的四角星闪光，外面炸开一团夜紫色的烟，银色碎片往外飞。比普攻命中大。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E) with night-purple smoke (#5A3C84, #3A2660, #22163C).
Effect: an EMPOWERED BOLT IMPACT, 6 frames: 1 a bright white four-pointed star flash at the center; 2 the star at full size (about 60% of the cell wide) with a silver ring around it, a puff of night-purple smoke bursting behind it; 3 the smoke puff spreads into round curls, silver shards flying outward; 4 the star fades, the curls drift outward and darken; 5 thin smoke wisps and a few silver chips; 6 faint purple specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `vayne_fx_sb_ring1.png`：圣银弩箭第 1 层（目标身上），6 帧

第一次命中后，目标胸口套上一个立着的银色圆环（参考 W_Ring_1：一个完整的细圆环，正对着看的人），圆环亮一下、停一会儿、慢慢淡掉。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E).
Effect: a SILVER RING MARK standing upright and facing the viewer (a full circle, not flattened), 6 frames: 1 a small bright silver ring at the center, 40% of the cell wide; 2 the ring grows to 70% of the cell wide, 2 squares thick, a white highlight on its upper left; 3 the same ring, the highlight moved a little along it; 4 the same ring, slightly dimmer; 5 the ring thinner and darker silver; 6 faint broken arcs of the ring.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the ring centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `vayne_fx_sb_ring2.png`：圣银弩箭第 2 层（目标身上），6 帧

第二次命中：两个套在一起的银环——外面一个完整的环，里面一个底部有小缺口的环（参考 W_Ring_2），一起亮起、停一会儿、淡掉。约 18 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E).
Effect: TWO SILVER RING MARKS standing upright and facing the viewer, one inside the other, 6 frames: 1 two small bright rings at the center; 2 they grow: the outer ring a full circle at 80% of the cell wide, the inner ring at 55% with a small gap at its bottom, both 2 squares thick, white highlights; 3 the same, the highlights moved a little; 4 the same, slightly dimmer; 5 both rings thinner and darker; 6 faint broken arcs.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `vayne_fx_sb_proc.png`：圣银弩箭第 3 下（爆开，真实伤害），7 帧

第三次命中：三个银环（第三个底部有箭头形的缺口，参考 W_Ring_3）一下子收紧到中心，"锵"地爆出一团白光和猩红、银色的碎片（真实伤害）。约 26 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E) with crimson accents (#FFD0D6, #FF5A6E, #D8203E, #8F0B24).
Effect: a SILVER BOLTS BURST, 7 frames: 1 three nested silver rings standing upright facing the viewer, the outer at 90% of the cell wide, the innermost with an arrow-shaped notch at its bottom; 2 the three rings shrink toward the center; 3 they snap together into one bright white point with a crimson ring around it; 4 a big white-and-crimson starburst, about 80% of the cell wide, crimson and silver shards flying out; 5 the burst breaks up, the shards fly further; 6 the shards dim to dark crimson; 7 faint specks.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `vayne_fx_q_roll.png`：翻滚的烟（地面，留在出发的地方），6 帧

她翻滚出去时，原地腾起一团贴着地面的夜紫色烟（参考 Q_WispySmoke、Taunt_Flecks），里面夹着几点银色的亮屑，往两边散开、淡掉。约 28 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, night-purple smoke (#5A3C84, #3A2660, #22163C, #140C24) with silver flecks (#FFFFFF, #C8CAE8, #9A9CC8).
Effect: a TUMBLE SMOKE PUFF on the ground, 6 frames: 1 a small puff of night-purple smoke at the bottom middle of the cell; 2 the smoke spreads sideways into a low flat cloud (twice as wide as tall), a few silver flecks inside; 3 the cloud at 90% of the cell width, round curls on top; 4 the cloud thins, the curls drift up and apart; 5 thin wisps; 6 a few faint purple specks.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); the cloud centered horizontally and sitting on the bottom of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `vayne_fx_e_hit.png`：重箭命中，5 帧

重箭打中英雄：一下很亮的银白闪光，一圈夜紫色的冲击波，几片猩红和银色的碎片。比强化箭命中更重。约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E), night-purple (#5A3C84, #3A2660, #22163C) and crimson accents (#FF5A6E, #D8203E).
Effect: a HEAVY BOLT IMPACT, 5 frames: 1 a big bright white flash at the center, about 40% of the cell wide; 2 a thick night-purple shock ring around the flash at 70% of the cell width, silver and crimson shards bursting out; 3 the ring at 95% of the cell width and thinner, the shards flying further; 4 the ring breaks into dark purple arcs; 5 faint specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `vayne_fx_e_stun.png`：落地撞击 + 眩晕（1 秒），8 帧

被击退的英雄落地时"砰"地撞上（英雄联盟里是撞墙，参考 E_tar_terrain_dust、E_terrain_dirt）：第 1–4 帧在身体中间炸开一团尘土和碎石、一下银色闪光；第 5–8 帧（循环）头顶转着三颗银色小星星（眩晕）。约 20 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, dust (#E0D2B0, #B09878, #7A6448) with a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8).
Effect: a SLAM IMPACT then a daze, 8 frames: 1 a white-silver flash at 55% of the cell height; 2 a burst of dust clouds and small stone chips around it, about 80% of the cell wide; 3 the dust spreads and the chips fall; 4 the dust fades to thin puffs; 5-8 (a seamless loop) three small silver five-pointed stars with white centers circling on a flat elliptical path (twice as wide as tall) at 15% of the cell height (above a head), each frame a quarter turn, the stars at the back smaller and darker.
Layout: one horizontal row of 8 equal cells, each 6 wide to 7 tall, image size 1920x280 (each cell 240x280); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `vayne_fx_r_cast.png`：终极时刻发动（在她身上），7 帧

发动大招：她身后猛地亮起一颗巨大的银白四角星光（参考 R_Ground_03、R_LensFlare），一群夜紫色的小蝙蝠从她身边往外飞散（参考 common_Bats32），脚下一圈银光的地纹一闪。约 44 格宽、56 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E) with night-purple bats and smoke (#5A3C84, #3A2660, #22163C, #140C24).
Effect: a FINAL HOUR burst around a standing figure (leave a figure-shaped empty space in the middle of the cell, about 55% of the cell width and 75% of the cell height, feet at 92% of the cell height - do NOT draw the figure), 7 frames: 1 a bright white point behind the figure's chest; 2 a huge silver-white four-pointed star flare bursts out from behind the figure, its long rays reaching up, down, left and right to the cell's edges (the figure's space stays empty in front of it); 3 the flare at full size, a flat ring of silver light flashes on the ground at the feet (an ellipse twice as wide as tall), a flock of small night-purple bats bursts out from around the figure; 4 the bats fly outward in all directions, the flare's rays shorten; 5 the bats reach the cell edges, the flare fades to pale silver; 6 a few bats and fading rays; 7 faint silver specks.
Layout: one horizontal row of 7 equal cells, each 3 wide to 4 tall, image size 2016x384 (each cell 288x384); the figure space and the ground ring centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `vayne_fx_r_refresh.png`：终极时刻刷新（击杀，在她身上），5 帧

大招期间击杀英雄、终极时刻刷新：她身上一闪猩红的光环往外扩，胸口高度一颗小小的银色四角星，几点猩红火星往上飘。约 32 格宽、40 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, crimson (#FFD0D6, #FF5A6E, #D8203E, #8F0B24) with a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8).
Effect: a FINAL HOUR REFRESH around a standing figure (leave a figure-shaped empty space in the middle of the cell, about 55% of the cell width and 75% of the cell height - do NOT draw the figure), 5 frames: 1 a small silver four-pointed star glint beside the figure's chest (at 40% of the cell height, on the right edge of the figure's space); 2 a thin crimson ring expands around the whole figure space, the star glint at full size; 3 the ring at the cell's edges, crimson sparks rising along both sides of the figure; 4 the sparks rise to above the figure's head and dim; 5 faint crimson specks.
Layout: one horizontal row of 5 equal cells, each 3 wide to 4 tall, image size 1440x384 (each cell 288x384); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `vayne_fx_r_aura.png`：终极时刻（在她身上，8 秒），4 帧循环

大招期间她脚下一个扁的银色四角星地纹（参考 R_Ground_03），身体两侧往上飘着银色的光点和几缕夜紫色的蝙蝠形烟丝，**不挡脸和身体**。4 帧循环。约 40 格宽、54 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver light ramp (#FFFFFF, #EEF0FF, #C8CAE8, #9A9CC8, #6A6E9E) with night-purple wisps (#5A3C84, #3A2660, #22163C).
Effect: a FINAL HOUR AURA around a standing figure (leave a figure-shaped empty space in the middle of the cell, about 55% of the cell width and 75% of the cell height, feet at 92% of the cell height - do NOT draw the figure), 4 frames, a seamless loop: a flat silver four-pointed star sigil on the ground at the feet (seen from a slightly top-down camera: twice as wide as tall), its points glinting in turn; small silver motes rising along both sides of the empty figure from the feet to above the head; two or three thin night-purple wisps shaped like small bats drifting up beside the figure; the motes and wisps move up each frame; nothing crosses the middle of the figure.
Layout: one horizontal row of 4 equal cells, each 3 wide to 4 tall, image size 1152x384 (each cell 288x384); the ground sigil centered horizontally at 92% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `vayne_fx_bolt` | `view_projectiles` `league_vayne_bolt`（普攻，朝飞行方向转） | 12 × 4 |
| `vayne_fx_q_bolt` | `view_projectiles` `league_vayne_q_bolt`（强化箭） | 18 × 6 |
| `vayne_fx_e_bolt` | `view_projectiles` `league_vayne_e_bolt`（重箭） | 24 × 8 |
| `vayne_fx_hit` | `view_effects` `league_vayne_hit`（普攻命中，跟随） | 12 |
| `vayne_fx_q_hit` | `league_vayne_q_hit`（强化箭命中） | 20 |
| `vayne_fx_sb_ring1` | `league_vayne_sb_ring1`（第 1 层，目标胸口） | 16 |
| `vayne_fx_sb_ring2` | `league_vayne_sb_ring2`（第 2 层） | 18 |
| `vayne_fx_sb_proc` | `league_vayne_sb_proc`（第 3 下，真实伤害） | 26 |
| `vayne_fx_q_roll` | `league_vayne_q_roll`（CasterViewEffect，地面，不跟随） | 28 × 14 |
| `vayne_fx_e_hit` | `league_vayne_e_hit`（重箭命中） | 24 |
| `vayne_fx_e_stun` | `league_vayne_e_stun`（落地撞击 + 头顶眩晕星循环 1 秒） | 20 × 24 |
| `vayne_fx_r_cast` | `league_vayne_r_cast`（CasterViewEffect，她身上） | 44 × 56 |
| `vayne_fx_r_refresh` | `league_vayne_r_refresh`（CasterViewEffect，她身上） | 32 × 40 |
| `vayne_fx_r_aura` | `view_buffs` `league_vayne_r`（终极时刻 8 秒） | 40 × 54 |
