# 符文法师 瑞兹：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型已定（`design/ryze_design.png`，8 倍，A40，40 格）。
> - 大小对照 `design/ryze_size.png`：定稿造型放大 4 倍，靴底在红色脚底线上，上面是 10 格一段的刻度，右边是原版武僧。瑞兹 29×40 格（卷轴顶到靴底 40 格），原版英雄约 33–36 格高。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里瑞兹自己的特效贴图（多数是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（普攻和 Q、E 法术涌动、W 符文禁锢、R 传送门、符文和传送），只在本地用，不要提交。颜色按下面写的色阶：**超负荷、符文、符文禁锢、曲境折跃用亮蓝；法术涌动和涌动标记用紫色**，和英雄联盟一样。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **符文要像符文**：英雄联盟瑞兹的符文是棱角分明的小符号（像带钩的 Z、带一撇的月牙、分叉的 Y），每个 3–5 格高，1 格粗的笔画，浅蓝（或紫）色、中间一格白。
> - 特效照下面第 1–19 条和「所有特效图的规则」画，每张一个 PNG，文件名 `ryze_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**（上一轮的造型就是代码拼的，没有被选中）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`ryze_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「奥术专精」 | 符文法球；技能伤害额外加最大生命值的一部分 | `ryze_fx_orb` · `ryze_fx_hit` |
| 技能 1 = Q「超负荷」 | 直线能量弹打第一个敌人；有涌动时所有带涌动的敌人身上炸开（弹射） | `ryze_fx_q_bolt` · `ryze_fx_q_cast` · `ryze_fx_q_hit` · `ryze_fx_q_pop` |
| 技能 2 = 连招 E→W→Q | 法术涌动（紫色法球，给目标和附近敌人挂涌动）→ 符文禁锢（有涌动就禁锢，否则减速）→ 超负荷（两枚符文放出，加速） | `ryze_fx_e_orb` · `ryze_fx_e_cast` · `ryze_fx_e_hit` · `ryze_fx_flux` · `ryze_fx_w_cage` · `ryze_fx_w_slow` · `ryze_fx_runes` · `ryze_fx_rune_out` · `ryze_fx_q_haste` |
| 大招 = R「曲境折跃」 | 脚下和目的地各开一个传送门，引导 1 秒后瑞兹和门里的队友一起传送过去，落地补一发法术涌动 | `ryze_fx_r_portal` · `ryze_fx_r_out` · `ryze_fx_r_in` · `ryze_fx_r_ally` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、符文、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的第四档，第五档（最深）只给很少的点缀（传送门中间的旋涡除外）。
- 颜色（按每条写的用）：
  - 符文蓝（Q、符文、W、R、普攻）：`#FFFFFF`、`#D6F4FF`、`#7FDBFF`、`#2E9BF0`、`#1A4FB8`；
  - 涌动紫（E、涌动标记、普攻）：`#FFFFFF`、`#EAD8FF`、`#B98CFF`、`#7B4BF0`、`#4724A8`。
- **飞行类特效朝右画，而且上下对称**（普攻法球 `orb`、Q 能量弹 `q_bolt`、E 法球 `e_orb`）：游戏会把它转到飞行方向，朝左飞时整张会上下翻转，所以里面不要有分上下的东西。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（涌动、符文、减速、加速）左右对称，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `ryze_fx_orb.png`：普攻：飞出去的符文法球（飞行中循环），4 帧

瑞兹的普攻：一颗蓝紫色的小法球朝右飞，后面拖一小段蓝色的光尾（参考 missile_E_BA、Q_Circle）。上下对称（飞向左边时会上下翻转）。约 10 格长、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8) and a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8).
Effect: a small FLYING MAGIC ORB moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round glowing head (white core, light-blue then violet rim) at the front (right), a short tapering light-blue tail behind it to the left, two tiny sparks flickering beside the tail.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the orb on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `ryze_fx_hit.png`：普攻命中，4 帧

法球打中：一个蓝紫色的小星形光闪（参考 E_Flash、Z_BrightSpark）。约 12 格，不要太大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8) and a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8).
Effect: a SMALL MAGIC HIT, 4 frames: 1 a white flash at the center; 2 a four-pointed light-blue star with a violet rim; 3 the star wider and thinner, a few violet sparks flying out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `ryze_fx_q_bolt.png`：Q 超负荷：飞出去的符文能量弹（飞行中循环），4 帧

超负荷：一颗亮蓝色的能量弹朝右飞，白色的弹头，后面拖着一串蓝色的符文尾巴（参考 Q_Mis_trail、Q_mis_Trail_shape、Q_Circle、R_Q_Mis_center）。上下对称。约 20 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a FLYING RUNE BOLT moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a bright round head 5-6 squares across (white core, light-blue rim, a thin cyan ring round it); behind it to the left a tapering trail of light-blue energy carrying 2-3 small RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square), getting fainter; the runes in the trail shift a little each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the bolt on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `ryze_fx_q_cast.png`：Q 出手：瑞兹手上的符文闪光（施法者身上），4 帧

超负荷出手：手掌前一个小小的蓝色符文圈一闪（参考 Q_mis_ring、Q_Circle）。只画闪光，不画人。约 14 格，居中画（导入时放到他手的位置）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a SMALL RUNE FLASH at a hand, 4 frames: 1 a white point; 2 a small light-blue rune circle (a ring 8-10 squares across with 3 tiny RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square) on it) flares round it; 3 the ring wider and thinner, a burst of 4 short rays; 4 the ring breaks into a few blue specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `ryze_fx_q_hit.png`：Q 打中，5 帧

超负荷打中：亮蓝色的爆炸，白色的芯，几块符文碎片飞出去（参考 Q_Circle、Break_Runes、Z_Flare）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a BLUE RUNE BLAST, 5 frames: 1 a white flash; 2 a round light-blue burst with a white core; 3 the burst at full size, a ring of energy round it, 3-4 small RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square) flying outward; 4 the ring thins and breaks, the runes fly further; 5 a few blue sparks and rune fragments.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `ryze_fx_q_pop.png`：Q 引爆涌动：每个带涌动的敌人身上的弹射爆发，5 帧

超负荷打到带涌动的目标：涌动在每个带涌动的敌人身上炸开——紫色和蓝色的符文爆开，一道蓝色的闪电弧从上方劈下来（英雄联盟里是超负荷在涌动目标之间弹射，参考 E_Flash_2x2、E_Break_Runes、Z_energylines）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8) and a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a FLUX DETONATION on a figure (do NOT draw the figure), 5 frames: 1 a blue-white lightning arc strikes down from the top of the cell to the center; 2 a violet-and-blue starburst at the center, white core; 3 the burst at full size, 4 violet RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in violet with a white core square) flying outward; 4 the burst fades, the runes break apart; 5 a few violet sparks.
Layout: one horizontal row of 5 equal cells, each 4 wide to 5 tall, image size 1280x400 (each cell 256x320); the burst centered a little below the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `ryze_fx_e_orb.png`：E 法术涌动：飞向目标的紫色法球（飞行中循环），4 帧

法术涌动：一颗紫色的法球朝右飞，表面绕着小符文，后面拖紫色的火焰尾（参考 missile_E_BA、E_bounce_mis_symbols、E_Wisps）。上下对称。约 12 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8).
Effect: a FLYING VIOLET ORB moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round orb 6-7 squares across (white core, light-violet body, violet rim) with two tiny violet rune glyphs circling it, a short flickering violet flame tail behind it to the left.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the orb on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `ryze_fx_e_cast.png`：E 出手：手上的紫色闪光（施法者身上），4 帧

法术涌动出手：手掌前一个紫色的小星形闪光（参考 E_Flash）。只画闪光。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8).
Effect: a SMALL VIOLET FLASH at a hand, 4 frames: 1 a white point; 2 a four-pointed violet star with a white core; 3 the star wider, a few violet sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `ryze_fx_e_hit.png`：E 打中：涌动炸开，5 帧

法术涌动打中：紫色的法球炸开，一圈紫色符文向四周扩散（英雄联盟里涌动从这里传给附近的敌人，参考 E_Flash_2x2、E_timer_ring_runes、Break_Runes）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8).
Effect: a VIOLET FLUX BURST, 5 frames: 1 a white flash; 2 a violet burst with a white core; 3 the burst at full size, a ring of 6 violet RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in violet with a white core square) expanding round it; 4 the ring wider and fainter; 5 a few violet sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `ryze_fx_flux.png`：涌动标记（带涌动的敌人身上，循环），4 帧

涌动：带涌动的敌人身上绕着一圈紫色的符文慢慢转（参考 E_timer_ring_runes、E_Timer_Ring_Minion、E_bounce_mis_symbols）。中间是人，不要画人；符文在格子中间（胸口的高度）绕一个扁椭圆，4 帧正好转完一段、能无缝接上。约 20 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #EAD8FF, #B98CFF, #7B4BF0, #4724A8).
Effect: a FLUX MARK round a figure's chest (do NOT draw the figure; leave the middle empty), 4 frames, a seamless loop: 4 violet RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in violet with a white core square) spaced round a flattened ellipse (twice as wide as tall) at the middle of the cell, moving a quarter of the way to the next one each frame, a faint violet ring joining them.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `ryze_fx_w_cage.png`：W 符文禁锢：罩住目标的符文牢笼（禁锢 1.25 秒 / 减速），8 帧

符文禁锢：目标脚下一个蓝色的符文圆圈，从圈上升起一圈发光的蓝色光栅（牢笼的栏杆），栏杆上闪着符文（参考 W_bars、W_Bar_Blur、W_ground_decal、W_prison_mult、W_Empowered_Hero_Rune）。中间是人，不要画人：只画脚下的圈和人前后的栏杆，人的位置留空。第 1–2 帧出现，3–6 帧保持（导入时重复到禁锢结束），7–8 帧消散。约 24 格宽、30 格高，圈的中心在格子底部往上 4 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a RUNE PRISON round a figure (do NOT draw the figure; leave its place empty), 8 frames: 1 a light-blue rune circle appears on the ground (a flattened ellipse twice as wide as tall, with 4 small RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square) on it); 2 thin bright blue bars of light shoot up from the circle; 3-6 the cage held: 6-7 vertical light-blue bars (white cores) standing on the ellipse, the ones in front brighter, the ones behind dimmer, runes flickering on the bars and round the circle, the light pulsing a little each frame; 7 the bars fade upward; 8 the circle breaks into blue specks.
Layout: one horizontal row of 8 equal cells, each 4 wide to 5 tall, image size 2048x320 (each cell 256x320); the circle's center 4 squares (32 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `ryze_fx_rune_out.png`：两枚符文放出（Q 时加速），5 帧

连招最后的超负荷放出两枚符文：瑞兹身边两个发光的蓝色符文炸开，变成一圈风往两边散开（加移速）（参考 R_aura_runeline、R_speedbuf、Z_BrightSpark）。中间是人，不要画人。约 26 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: TWO RUNES BURSTING round a figure (do NOT draw the figure; leave the middle empty), 5 frames: 1 two bright RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square), one on each side of the figure's waist, glowing white; 2 both flare into small blue starbursts; 3 a ring of light-blue wind sweeps out to both sides from them; 4 the wind wider and fainter, a few sparks; 5 fading specks.
Layout: one horizontal row of 5 equal cells, each 5 wide to 4 tall, image size 1600x256 (each cell 320x256); centered in every cell, a little below the middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `ryze_fx_runes.png`：符文充能（瑞兹身上绕着转，循环），6 帧：一枚和两枚各一行

连招里 E、W 各充一枚符文：一枚 / 两枚蓝色的发光符文绕着瑞兹的腰转圈（参考 R_aura_shards、R_SliceRunes、Q_mis_ring）。中间是人，不要画人。第 1 行一枚符文，第 2 行两枚（相对的位置），6 帧转一圈、无缝循环。约 28 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: ORBITING RUNES round a figure's waist (do NOT draw the figure; leave the middle empty), 6 frames per row, a seamless loop: ROW 1 one glowing RUNE (a rune glyph 4-5 squares tall, white core, light-blue glow) moving round a flattened ellipse (twice as wide as tall), a sixth of the way each frame, a faint blue trail behind it; ROW 2 the same with TWO runes on opposite sides of the ellipse.
Layout: two horizontal rows of 6 equal cells each, each cell 2 wide to 1 tall, image size 3072x512 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `ryze_fx_w_slow.png`：W 减速（没有涌动时，敌人脚下，循环），4 帧

符文禁锢没有涌动时只减速：敌人脚下一圈暗一点的蓝色符文锁链慢慢转（参考 W_ground_decal、R_aoe_runes）。中间是人，不要画人。约 22 格宽、8 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a SLOW MARK at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ring (twice as wide as tall) of light-blue rune chain links on the ground with 3 small RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square) on it, turning a little each frame.
Layout: one horizontal row of 4 equal cells, each 5 wide to 2 tall, image size 2560x256 (each cell 640x256); the ring at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `ryze_fx_q_haste.png`：符文加速（瑞兹脚下，循环），4 帧

两枚符文放出后的加速：瑞兹脚边绕着蓝色的风和小符文（左右对称，因为他朝左朝右都用同一张）（参考 R_speedbuf、R_telewarning_wisps）。中间是人，不要画人。约 24 格宽、10 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a BLUE SPEED WIND at a figure's feet (do NOT draw the figure; symmetric left and right), 4 frames, a seamless loop: curling light-blue wind streaks swirl round the figure's feet on both sides, two tiny runes riding them, a few white sparkles, moving each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the swirl at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `ryze_fx_r_portal.png`：R 曲境折跃：传送门（瑞兹脚下和目的地，地面，大图），10 帧

曲境折跃的传送门：地上一个巨大的蓝色符文法阵（从斜上方看是扁椭圆，宽是高的 2 倍），外圈一圈符文、内圈一圈发光的环，中间是深蓝色的旋涡，边上冒着蓝白色的光（参考 R_circle_rune、R_circle_rune_Inner/Outer、R_aoe_runes、R_PortalSolidEdge、R_portalDome_swoosh）。第 1–2 帧展开，3–8 帧转动（导入时循环到引导结束），9–10 帧收起。约 60 格宽、30 格高（中间的人站得下，队友也站得下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a GROUND PORTAL, a big rune circle on the floor seen from above at an angle (a flattened ellipse TWICE as wide as tall), 10 frames: 1-2 it opens from the center outward; 3-8 the full portal turning: an outer ring of 10-12 RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square) (white cores), a glowing light-blue inner ring, between them thin rune lines, the middle a dark-blue swirl (the darkest ramp shades, with lighter streaks spiralling in), light-blue sparks rising from the rim; the runes move round a little each frame so frames 3-8 loop; 9-10 it closes to the center and vanishes.
Layout: one horizontal row of 10 equal cells, each 2 wide to 1 tall, image size 5120x256 (each cell 512x256); the ellipse centered in every cell, filling it. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `ryze_fx_r_out.png`：R 传送离开：原地的蓝色光柱（不跟随，大图），6 帧

瑞兹从传送门离开的一瞬间：原地冲起一道蓝白色的光柱，几个符文往上飞散（参考 R_SpikeRay、R_telewarning_Streak、R_core_2x2）。中间是人的位置，光柱罩住它；底部在格子下沿往上 2 格。约 28 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a TELEPORT COLUMN, 6 frames: 1 a ring of light flashes on the ground (a flattened ellipse); 2 a tall column of light-blue light with a white core shoots up from it to the top of the cell; 3 the column at full brightness, 4-5 RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square) flying up and outward; 4 the column narrows to a thin white line; 5 the line vanishes upward, the runes drift; 6 a few blue specks.
Layout: one horizontal row of 6 equal cells, each 2 wide to 3 tall, image size 1536x768 (each cell 256x384); the column centered horizontally, its foot 2 squares (16 px) above the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `ryze_fx_r_in.png`：R 传送到达：落地的符文爆发（跟随），6 帧

瑞兹从目的地的传送门里出现：一圈蓝白色的光从地上的椭圆向上收拢，符文向外散开（参考 R_core_2x2、R_aura_shards、Z_Flare）。中间是人，不要画人。约 34 格宽、34 格高，底部是地面的椭圆。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a TELEPORT ARRIVAL round a figure (do NOT draw the figure; leave its place empty), 6 frames: 1 a bright flash and a glowing ellipse on the ground; 2 a ring of light-blue light rises up round the figure's place; 3 the ring at chest height bursts outward, 6 RUNES (League's rune glyphs: small angular symbols like a hooked Z, a crescent with a tick, a forked Y - each 3-5 squares tall, drawn with 1-square strokes in light blue with a white core square) flying out; 4 the runes fly further, fading; 5 sparks; 6 a few specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256 (each cell 256x256); the ground ellipse 2 squares above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `ryze_fx_r_ally.png`：R 队友被传送：队友身上的蓝色闪光，4 帧

站在传送门里的队友被一起传送：队友身上一闪蓝白色的光，几道竖直的光线（参考 R_telewarning_Streak、R_SpikeRay）。中间是人，不要画人。约 16 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, runes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #D6F4FF, #7FDBFF, #2E9BF0, #1A4FB8).
Effect: a TELEPORT FLASH on a figure (do NOT draw the figure), 4 frames: 1 three thin vertical light-blue streaks flash over the figure's place, white cores; 2 they brighten, a small ring of light at the feet; 3 the streaks shoot upward and thin out; 4 a few blue specks.
Layout: one horizontal row of 4 equal cells, each 2 wide to 3 tall, image size 1024x768 (each cell 256x384); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `ryze_fx_orb` | view_projectiles `league_ryze_orb`（朝右，游戏转到飞行方向） | 10 × 7 |
| `ryze_fx_hit` | view_effects `league_ryze_hit`（跟随） | 12 |
| `ryze_fx_q_bolt` | view_projectiles `league_ryze_q_bolt`（朝右，游戏转到飞行方向） | 20 × 9 |
| `ryze_fx_q_cast` | view_effects `league_ryze_q_cast`（施法者身上，跟随；Claude 按动作帧的手放到手的位置） | 14 |
| `ryze_fx_q_hit` | view_effects `league_ryze_q_hit`（跟随） | 18 |
| `ryze_fx_q_pop` | view_effects `league_ryze_q_pop`（跟随，画在人物上面） | 20 |
| `ryze_fx_e_orb` | view_projectiles `league_ryze_e_orb`（朝右，游戏转到飞行方向） | 12 × 10 |
| `ryze_fx_e_cast` | view_effects `league_ryze_e_cast`（施法者身上，跟随；导入时放到手的位置） | 12 |
| `ryze_fx_e_hit` | view_effects `league_ryze_e_hit`（跟随） | 22 |
| `ryze_fx_flux` | view_effects `league_ryze_flux`（跟随，每 12 tick 播一次，4 帧 × 50 ms 正好接上） | 20 × 10 |
| `ryze_fx_w_cage` | view_effects `league_ryze_w_root` / `league_ryze_w_cage`（跟随；中间几帧导入时重复到禁锢结束） | 24 × 30 |
| `ryze_fx_rune_out` | view_effects `league_ryze_rune_out`（施法者身上，跟随） | 26 × 20 |
| `ryze_fx_runes` | view_buffs `league_ryze_rune1`（第 1 行）/ `league_ryze_rune2`（第 2 行）（循环） | 28 × 14 |
| `ryze_fx_w_slow` | view_buffs `league_ryze_w_slow`（循环，画在脚下） | 22 × 8 |
| `ryze_fx_q_haste` | view_buffs `league_ryze_q_haste`（循环，画在脚下） | 24 × 10 |
| `ryze_fx_r_portal` | view_effects `league_ryze_r_portal` / `league_ryze_r_dest`（地面，不跟随，大图；3–8 帧导入时重复到 1 秒） | 60 × 30 |
| `ryze_fx_r_out` | view_effects `league_ryze_r_out`（施法者原地，不跟随） | 28 × 44 |
| `ryze_fx_r_in` | view_effects `league_ryze_r_in`（施法者身上，跟随） | 34 × 34 |
| `ryze_fx_r_ally` | view_effects `league_ryze_r_ally`（跟随） | 16 × 24 |

- `q_cast` / `e_cast` 放到动作帧里手的位置（施法者身上的画面画在站位点上，按出手帧量手的偏移）；`flux` 每 12 tick 播一次（4 帧 × 50 ms）；`w_cage` 中间几帧重复到禁锢结束（禁锢 75 tick），减速版用短一点的；`r_portal` 的转动帧循环到 60 tick 引导结束，目的地的 `r_dest` 用同一张。
- 清掉 Codex 给光和符文描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
