# 九尾妖狐 阿狸：给 Codex 的特效提示词

> **这一轮只画 15 张特效图。**
> - 角色不用画：阿狸的模型由 Claude 做（英雄联盟原版动画按像素风重新上色；头部是逐格手画的：蓝黑长发和刘海、两只狐耳（外黑内粉）、金色的三行大眼，用户选定的方案 A，贴在每一帧上）。
> - 定稿造型图 `native/ahri_native.png` 只用来参考配色和人物大小（连狐耳约 38 格高，九条白尾巴在身后展开约 20 格宽），不要改它。模型预览 `ahri_model_preview.gif` 可以看每个动作（扔宝珠、飞吻、冲刺）的样子。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里阿狸自己的特效贴图（多为灰度遮罩：宝珠里的狐灵 `Orb_Fox`、宝珠边缘、狐火 `FireShapes`（蓝色和粉紫色两套）、爱心 `E_Heart`、冲刺拖尾、精魄光点），只在本地用，不要提交。
> - 特效照下面第 1–15 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_ahri.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「摄魂夺魄」 | 发射一颗粉紫色的妖力球；技能命中 3 次后，下一个技能每命中一个敌人给阿狸回血（攒满时身上有精魄光点环绕） | `ahri_fx_orb` · `ahri_fx_hit` · `ahri_fx_heal` · `ahri_fx_essence` |
| 技能 1 = Q「欺诈宝珠」+ W「妖异狐火」 | 宝珠直线飞出再飞回，往返各打一次路上的敌人（回程无视魔抗）；每 9 秒同时放出 3 团狐火，绕身一圈后追向附近敌人 | `ahri_fx_q_orb` · `ahri_fx_q_hit` · `ahri_fx_q_true` · `ahri_fx_w_orbit` · `ahri_fx_w_fire` · `ahri_fx_w_hit` |
| 技能 2 = E「魅惑妖术」 | 飞吻：一颗爱心飞出去，命中第一个敌方英雄，把它魅惑 1.25 秒（头上冒爱心，朝阿狸走过来） | `ahri_fx_e_kiss` · `ahri_fx_e_charm` |
| 大招 = R「灵魄突袭」 | 连续 3 次：每次冲刺一段，出发的地方留下一团灵气，再向附近 3 个敌人射出精魄弹 | `ahri_fx_r_dash` · `ahri_fx_r_bolt` · `ahri_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（四套，别混用）：
  - 狐灵蓝（宝珠、狐火）：`#FFFFFF`、`#D8F4FF`、`#88D0FF`、`#4A9CF0`、`#2A5AC8`、`#1A2E7A`；
  - 魅惑粉（爱心、魅惑）：`#FFFFFF`、`#FFD8F0`、`#FF8CD0`、`#F04AA8`、`#B01C78`；
  - 精魄紫（普攻、灵魄突袭、被动）：`#FFFFFF`、`#F0E0FF`、`#C8A0FF`、`#8C64F0`、`#5A38C0`、`#2E1C78`；
  - 回程的真实伤害：以白色和淡银蓝为主（`#FFFFFF`、`#E8F4FF`、`#B8D8F0`），少量狐灵蓝。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°（所以爱心要横着放、尖朝右，上下对称）。
- 命中、爆开、标记居中画，不旋转。
- 套在人身上的特效（狐火绕身、回血、精魄光点）：格子中间留出一个空的人形位置（按每条写的比例），不要画人，也不要挡住脸。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `ahri_fx_orb.png`：普攻（飞向目标的妖力球），4 帧，循环

一颗小小的粉紫色妖力球，后面拖一小段精魄光尾。朝右飞。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit violet ramp (#FFFFFF, #F0E0FF, #C8A0FF, #8C64F0, #5A38C0).
Effect: a small magic ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right a round orb (about 35% of the cell height) with a white-hot core and a violet rim, behind it to the left a short tapering violet trail with two tiny sparkles; each frame the core pulses a little and the trail flickers.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256 wide, 128 tall); the orb's center at 75% of the cell width, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `ahri_fx_hit.png`：普攻命中，5 帧

妖力球打中：一小团粉紫色的星形闪光，碎成几点光屑。约 12 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit violet ramp (#FFFFFF, #F0E0FF, #C8A0FF, #8C64F0, #5A38C0).
Effect: a small MAGIC IMPACT, 5 frames: 1 a tiny white dot at the center; 2 it bursts into a four-pointed violet star flash about 40% of the cell wide with a white core; 3 the star at full size, a thin ring around it, four small motes flying outward; 4 the star shrinks, the motes further out; 5 a few faint motes fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `ahri_fx_q_orb.png`：欺诈宝珠（飞出去、飞回来的宝珠，同一张），6 帧，循环

阿狸的宝珠：一颗透明的蓝白色大球，球里转着一只狐灵（参考 `lol_fx_ref.png` 的 `Orb_Fox`：白色的狐狸头和尾巴绕成一圈），外圈一道亮边，后面拖一段短短的蓝色光尾。朝右飞（飞回来时游戏会把它转向阿狸）。约 16 格高、24 格长（含光尾）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fox spirit blue ramp (#FFFFFF, #D8F4FF, #88D0FF, #4A9CF0, #2A5AC8, #1A2E7A).
Effect: the ORB OF DECEPTION flying to the RIGHT, 6 frames, a seamless loop, SYMMETRIC above and below the middle line in outline: at the right a large round orb (about 55% of the cell height) with a bright white-blue rim and a translucent blue inside; inside the orb a small white fox spirit (a fox head and a curling tail) circling around the center - it moves one sixth of the circle each frame; behind the orb to the left a short tapering blue trail with two or three sparkles, reaching the left edge.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the orb's center at 65% of the cell width, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `ahri_fx_q_hit.png`：宝珠去程命中，5 帧

宝珠穿过敌人：一团蓝色的魔法爆光，带几片碎光。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fox spirit blue ramp (#FFFFFF, #D8F4FF, #88D0FF, #4A9CF0, #2A5AC8).
Effect: a BLUE MAGIC IMPACT, 5 frames: 1 a bright white-blue dot at the center; 2 a round blue burst about 45% of the cell wide with a white core and a jagged edge; 3 the burst at full size (60%), a thin blue ring outside it, small blue shards flying out; 4 the burst breaks into swirling blue wisps; 5 faint wisps fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `ahri_fx_q_true.png`：宝珠回程命中（真实伤害），5 帧

回程的伤害无视魔抗，画得更"锐"：一道白色的十字闪光，外面一圈淡银蓝的碎光。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, white and pale silver-blue (#FFFFFF, #E8F4FF, #B8D8F0) with a little fox spirit blue (#88D0FF, #4A9CF0).
Effect: a SHARP TRUE-DAMAGE IMPACT, 5 frames: 1 a tiny white point at the center; 2 a sharp white four-pointed cross flash (long thin rays, about 60% of the cell wide); 3 the cross at full size with a pale silver-blue diamond in the middle and small shards around it; 4 the rays retract, shards drift out; 5 faint silver specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the flash centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `ahri_fx_w_orbit.png`：妖异狐火绕身（跟着阿狸），8 帧

放 W 的时候：三团蓝色的狐火绕着阿狸转一圈（从上往下斜看是一个扁的椭圆轨道，在胸口高度），第 8 帧狐火飞走、只剩几点火星。**不能挡住脸**。人形空位约 36 格高、18 格宽；椭圆轨道约 30 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a fox spirit blue ramp (#FFFFFF, #D8F4FF, #88D0FF, #4A9CF0, #2A5AC8) with a few violet accents (#C8A0FF).
Effect: FOX-FIRE, three small blue spirit flames orbiting a hero, 8 frames, around an EMPTY space the size of a small chibi hero in the middle of every cell (80% of the cell height, 40% of the cell width, feet at 90% of the cell height) - never draw the hero and never draw over its head: the three flames (each a small teardrop flame about 12% of the cell height, white core, blue edge, a short curling tail) travel on a flat ellipse at chest height (the ellipse 85% of the cell wide, 25% of the cell high, centered at 45% of the cell height), 120 degrees apart, moving a quarter turn every two frames; the flame at the back of the ellipse is smaller and dimmer; 1 the flames appear with a small flash; 2 to 7 they circle; 8 they shoot outward and leave only a few sparks.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `ahri_fx_w_fire.png`：狐火（追向敌人的一团火），4 帧，循环

一团蓝色的狐火，头圆、尾巴长长地往后甩，朝右飞。约 12 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fox spirit blue ramp (#FFFFFF, #D8F4FF, #88D0FF, #4A9CF0, #2A5AC8) with a few violet sparks (#C8A0FF).
Effect: a FOX-FIRE flame flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right a round flame head (about 45% of the cell height) with a white core, behind it a long wavy blue flame tail tapering to a point at the left, two small sparks; each frame the tail waves and the flame edge flickers.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256 wide, 128 tall); the flame head's center at 75% of the cell width, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `ahri_fx_w_hit.png`：狐火命中，5 帧

狐火打中：一团蓝色的火苗炸开，往上飘几缕。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fox spirit blue ramp (#FFFFFF, #D8F4FF, #88D0FF, #4A9CF0, #2A5AC8).
Effect: a BLUE FLAME BURST, 5 frames: 1 a small white-blue flash at the center; 2 a round burst of blue flame tongues about 45% of the cell wide; 3 the flames at full size, licking upward; 4 the flames break into small blue flame wisps rising; 5 two faint wisps near the top fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `ahri_fx_e_kiss.png`：魅惑妖术（飞出去的飞吻爱心），4 帧，循环

一颗粉色的爱心，**横着放、尖朝右**（朝飞行方向），上下对称，后面拖一道粉色的闪光尾巴。约 16 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a charm pink ramp (#FFFFFF, #FFD8F0, #FF8CD0, #F04AA8, #B01C78).
Effect: a KISS HEART flying to the RIGHT, 4 frames, a seamless loop, lying on its side and SYMMETRIC above and below the middle line: at the right a bright pink heart turned 90 degrees so that its POINT faces RIGHT (the direction of flight) and its two round lobes are at the left, a white highlight on each lobe, a soft pink glow edge; behind it to the left a tapering trail of small pink sparkles and two tiny hearts; each frame the heart pulses (slightly bigger, then smaller) and the sparkles twinkle.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256 wide, 128 tall); the heart's center at 70% of the cell width, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `ahri_fx_e_charm.png`：被魅惑（跟着目标，1.25 秒），10 帧

被魅惑的敌人头顶：几颗小爱心一颗接一颗冒出来、往上飘、变淡，头顶上方一直有一两颗。**只画在头顶上方，不能挡住脸**。约 14 格宽、12 格高，画在格子上半部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a charm pink ramp (#FFFFFF, #FFD8F0, #FF8CD0, #F04AA8, #B01C78).
Effect: CHARMED, little hearts floating above a hero's head, 10 frames: in the UPPER HALF of the cell only (never below 55% of the cell height - the hero's face is there), small pink hearts (each about 12% of the cell width, upright, white highlight) pop up one after another just above the head position (centered, at about 50% of the cell height), float upward and to the sides, shrink and fade near the top; at any time two or three hearts are visible; 1 a small pink sparkle burst; 2 to 9 the hearts rise in turn; 10 the last heart fading.
Layout: one horizontal row of 10 equal square cells, image size 2560x256; centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `ahri_fx_r_dash.png`：灵魄突袭（冲刺出发点留下的灵气），6 帧

阿狸冲刺时在出发的地方留下一团紫色的灵气：一个淡淡的狐灵残影（像一团紫色的狐火烟）+ 一圈往外散的精魄光点，**不朝任何方向**（她可能往前冲也可能往后冲）。约 30 格宽、30 格高，中心在人形的腰部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit violet ramp (#FFFFFF, #F0E0FF, #C8A0FF, #8C64F0, #5A38C0, #2E1C78).
Effect: SPIRIT RUSH departure, a burst of violet spirit essence left where a hero dashed from, 6 frames, NOT pointing any direction (symmetric left and right): 1 a white-violet flash about 40% of the cell tall at the center; 2 it swells into a violet spirit cloud shaped like a soft vertical flame with small fox-ear points at the top (a ghostly silhouette about 70% of the cell tall), a ring of violet motes around it; 3 the cloud at full size, motes spreading outward in all directions; 4 the cloud thins and rises; 5 wisps and motes drifting up and out; 6 faint motes fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `ahri_fx_r_bolt.png`：精魄弹（追向敌人），4 帧，循环

一颗紫白色的精魄弹，后面拖一道卷曲的紫色光尾，朝右飞。约 12 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit violet ramp (#FFFFFF, #F0E0FF, #C8A0FF, #8C64F0, #5A38C0).
Effect: an ESSENCE BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right a bright white-violet bolt head (a small elongated diamond, about 40% of the cell height), behind it a violet trail that curls in a gentle wave toward the left edge, tiny sparkles along it; each frame the wave moves along the trail.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256 wide, 128 tall); the bolt's tip at 90% of the cell width, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `ahri_fx_r_hit.png`：精魄弹命中，5 帧

一团紫色的精魄爆光，星形，带几点光屑。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit violet ramp (#FFFFFF, #F0E0FF, #C8A0FF, #8C64F0, #5A38C0).
Effect: an ESSENCE IMPACT, 5 frames: 1 a white dot at the center; 2 a six-pointed violet star burst about 45% of the cell wide with a white core; 3 the star at full size, a thin violet ring outside, small motes flying out; 4 the star breaks into violet wisps; 5 faint motes fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `ahri_fx_heal.png`：摄魂夺魄回血（跟着阿狸），6 帧

被动回血：几颗粉紫色的精魄光点从四周飞进阿狸身体，身上一闪，几个小小的加号往上飘。**不能挡住脸**。人形空位约 36 格高、18 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit violet ramp (#FFFFFF, #F0E0FF, #C8A0FF, #8C64F0) with charm pink (#FF8CD0) and a soft heal green (#B8FFC8, #5CD878).
Effect: ESSENCE THEFT HEAL, 6 frames, around an EMPTY space the size of a small chibi hero in the middle of every cell (80% of the cell height, 40% of the cell width, feet at 90% of the cell height) - never draw the hero and never draw over its head: 1 five small pink-violet essence orbs appear around the hero at the cell's edges; 2 they fly inward on curving paths leaving short trails; 3 they reach the hero's chest and flash; 4 a soft violet shimmer outline around the hero's body edge (only a few pixels, not covering it) and two small green plus signs rising beside the shoulders; 5 the plus signs rise higher; 6 the last sparkles fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `ahri_fx_essence.png`：摄魂夺魄攒满（跟着阿狸，一直循环到下一个技能），6 帧，无缝循环

被动攒满时的提示：三颗小小的粉紫色精魄光点绕着阿狸的腰慢慢转，很淡，**不能挡住身体和脸**。人形空位约 36 格高、18 格宽；光点轨道约 24 格宽、6 格高，在腰部高度。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a spirit violet ramp (#FFFFFF, #F0E0FF, #C8A0FF, #8C64F0) with charm pink (#FF8CD0).
Effect: ESSENCE READY, a subtle loop around a hero, 6 frames, a seamless loop, around an EMPTY space the size of a small chibi hero in the middle of every cell (80% of the cell height, 40% of the cell width, feet at 90% of the cell height) - never draw the hero: three tiny pink-violet essence motes (each 5% of the cell wide, white center) travel on a flat ellipse at waist height (the ellipse 70% of the cell wide, 12% of the cell high, centered at 62% of the cell height), 120 degrees apart, moving one sixth of the turn each frame; the mote at the back is smaller and dimmer; each mote leaves a two-pixel trail.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`（头部是手画的方案 A，贴在 League 的头骨骼上），帧时长写在 `native/ahri_cells.json`。特效由 `tools/art/import_ahri.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `ahri_fx_orb.png` | 4 | 投射物 `league_ahri_orb`（普攻，朝飞行方向转） | 4 × 60 循环 |
| `ahri_fx_hit.png` | 5 | 特效 `league_ahri_hit`（跟随目标） | 5 × 50 |
| `ahri_fx_q_orb.png` | 6 | 投射物 `league_ahri_q_out` / `league_ahri_q_back`（去程 75000 远，回程飞向阿狸） | 6 × 60 循环 |
| `ahri_fx_q_hit.png` | 5 | 特效 `league_ahri_q_hit`（跟随目标） | 5 × 50 |
| `ahri_fx_q_true.png` | 5 | 特效 `league_ahri_q_true_hit`（回程命中，跟随目标） | 5 × 50 |
| `ahri_fx_w_orbit.png` | 8 | 特效 `league_ahri_w_orbit`（跟随阿狸，放狐火时） | 8 × 60 |
| `ahri_fx_w_fire.png` | 4 | 投射物 `league_ahri_w_fire`（追向目标） | 4 × 60 循环 |
| `ahri_fx_w_hit.png` | 5 | 特效 `league_ahri_w_hit`（跟随目标） | 5 × 50 |
| `ahri_fx_e_kiss.png` | 4 | 投射物 `league_ahri_e_kiss`（80000 远，朝飞行方向转） | 4 × 70 循环 |
| `ahri_fx_e_charm.png` | 10 | 特效 `league_ahri_e_charm`（跟随目标，魅惑 1.25 秒） | 10 × 125 |
| `ahri_fx_r_dash.png` | 6 | 特效 `league_ahri_r_dash`（留在出发点，不跟随） | 6 × 70 |
| `ahri_fx_r_bolt.png` | 4 | 投射物 `league_ahri_r_bolt`（追向目标） | 4 × 50 循环 |
| `ahri_fx_r_hit.png` | 5 | 特效 `league_ahri_r_hit`（跟随目标） | 5 × 50 |
| `ahri_fx_heal.png` | 6 | 特效 `league_ahri_heal`（跟随阿狸） | 6 × 70 |
| `ahri_fx_essence.png` | 6 | 增益 `league_ahri_et_ready`（攒满时一直循环） | 6 × 100 循环 |
