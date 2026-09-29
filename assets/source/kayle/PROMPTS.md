# 正义天使 凯尔：给 Codex 的特效提示词

> **这一轮只画 14 张特效图。**
> - 角色不用画：凯尔的模型由 Claude 做。头部（白发、琥珀色发光的眼睛、红唇，用户选了 K5）是逐格画的，每一帧贴在头部的位置；身体和翅膀用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`），走路是原版的 Run1（用户选了 A：原版动作、原版 2.13 秒节奏、原版浮动幅度）。
> - 定稿造型图 `native/kayle_native.png` 只用来参考配色和人物大小（连翅膀约 42 格高、约 26 格宽，平时离地悬浮 3 格），不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里凯尔自己的特效贴图（金橙色的圣火、金色的剑形、金色圆环、Q 的星体之剑、R 的天降火剑和光柱），只在本地用，不要提交。
> - 特效照下面第 1–14 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_kayle.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「登神长阶」 | 1–4 级近战挥剑；5 级「升腾」变远程，射出火焰弹；8 级「炽诚」昂扬状态下每次普攻多射一道焰浪；12 级「超然」永久昂扬。狂热叠满 5 层进入「昂扬」（身上燃起圣火）。每次升阶有一段升阶仪式 | `kayle_fx_hit` · `kayle_fx_bolt` · `kayle_fx_bolt_hit` · `kayle_fx_wave` · `kayle_fx_exalted` · `kayle_fx_ascend` |
| 技能 1 = Q「耀焰冲击」 | 射出一把星体之剑，停在第一个敌人处爆开，范围伤害 + 减速 + 降护甲魔抗 | `kayle_fx_q_sword` · `kayle_fx_q_blast` |
| 技能 2 = E「星火符刃」+ W「星界恩典」 | 射出一团星火（对英雄附带最大生命真实伤害），8 级起命中后爆炸；每 12 秒附带星界恩典，给自己和一名友方英雄回血加速 | `kayle_fx_e_bolt` · `kayle_fx_e_hit` · `kayle_fx_e_blast` · `kayle_fx_w_heal` |
| 大招 = R「圣裁之刻」 | 让一名被控制的友方英雄（没有就自己）无敌 2.5 秒，结束时圣剑从天而降，在周围一大圈爆开 | `kayle_fx_r_invuln` · `kayle_fx_r_blades` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（三套，别混用）：
  - 圣火（普攻、火焰弹、焰浪、E、昂扬、升阶，金橙）：`#FFFFFF`、`#FFF4C8`、`#FFD24A`、`#F7941D`、`#C4520E`、`#6E2608`；
  - 天界金（Q 的剑、R 的剑和圆环、无敌护盾，金白）：`#FFFFFF`、`#FFF8DC`、`#F6DC7C`、`#D8A838`、`#9A6A1C`、`#5A3A10`；
  - 治疗（W，嫩绿带一点金）：`#FFFFFF`、`#F2FFD8`、`#C8F27A`、`#86D045`、`#4A8A24`，点缀 `#F6DC7C`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- 命中、爆开、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在英雄身上的特效（昂扬、升阶、治疗、无敌护盾）：格子中间留出一个空的人形位置（按每条写的比例），不要画人，**不能挡住身体和脸**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `kayle_fx_hit.png`：近战普攻命中（1–4 级），5 帧

剑砍中目标：一道金橙色的弧形火焰刀光斜着划过，带几点火星。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy fire ramp (#FFFFFF, #FFF4C8, #FFD24A, #F7941D, #C4520E).
Effect: a FLAMING SWORD SLASH IMPACT, 5 frames: 1 a thin bright white line appears diagonally across the center (from upper left to lower right); 2 it widens into a crescent slash about 50% of the cell wide, golden yellow with an orange rim and a white core, three small orange sparks flying off; 3 the crescent at full size with little flame licks along its outer edge, the sparks further out; 4 the crescent thins and breaks into short orange dashes; 5 two faint dark orange dashes fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the slash centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `kayle_fx_bolt.png`：远程普攻的火焰弹（5 级起，飞行），4 帧循环

升腾后普攻射出一团圣火：前端是白金色的亮核，后面拖一条金橙色的火焰尾巴。约 14 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy fire ramp (#FFFFFF, #FFF4C8, #FFD24A, #F7941D, #C4520E).
Effect: a STARFIRE BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white-gold core (a small diamond) at 80% of the cell width, a tapering tail of golden and orange flame streaming to the left behind it over 70% of the cell width, the tail's flame tongues flickering differently in each frame, one or two small orange sparks trailing.
Layout: one horizontal row of 4 equal cells, each 5 wide to 2 tall, image size 1280x128 (each cell 320x128); the bolt on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `kayle_fx_bolt_hit.png`：火焰弹命中，5 帧

火焰弹打中目标：一个金色的星芒闪光，四周炸出一圈小火星。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy fire ramp (#FFFFFF, #FFF4C8, #FFD24A, #F7941D, #C4520E).
Effect: a STARFIRE IMPACT, 5 frames: 1 a small white point at the center; 2 an eight-pointed star flash, white core and golden points, about 40% of the cell wide; 3 the star at full size with a ring of small orange sparks around it; 4 the star shrinks, the sparks fly outward and turn dark orange; 5 faint orange specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `kayle_fx_wave.png`：焰浪（8 级「炽诚」昂扬普攻多射出的一道，飞行），4 帧循环

一道竖着的月牙形火焰波向前推进，凸面朝右，像一把展开的火扇。约 10 格厚、20 格高（判定半径 10000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy fire ramp (#FFFFFF, #FFF4C8, #FFD24A, #F7941D, #C4520E, #6E2608).
Effect: a WAVE OF HOLY FIRE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a tall crescent of flame bulging to the right, 90% of the cell height, its front edge bright white-gold, behind it layered golden and orange flame tongues trailing to the left and fading into dark orange embers, the two tips of the crescent curling back; the flame tongues flicker differently in each frame.
Layout: one horizontal row of 4 equal cells, each 1 wide to 2 tall, image size 512x256 (each cell 128x256); the crescent's front at 75% of the cell width, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `kayle_fx_q_sword.png`：耀焰冲击的星体之剑（飞行），4 帧循环

Q 射出的剑：一把金色的华丽长剑平着向右飞（剑尖朝右，剑柄在左，参考 `lol_fx_ref.png` 的 Kayle_Q_Mis），剑身发白光，后面拖一条金色光尾。约 26 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a celestial gold ramp (#FFFFFF, #FFF8DC, #F6DC7C, #D8A838, #9A6A1C).
Effect: a CELESTIAL SWORD flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: an ornate golden sword lying flat along the middle line, the pointed tip at the right at 95% of the cell width, a white glowing blade with a gold edge, a small winged golden crossguard and hilt at 35% of the cell width; behind the hilt a thin trail of golden light and small white sparkles streaming to the left edge; the trail and sparkles shift each frame, the sword itself stays the same.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1152x128 (each cell 384x128); the sword on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `kayle_fx_q_blast.png`：星体之剑爆开（地面范围），7 帧

剑停在第一个敌人处爆开：金白色的光爆，地上裂开金色的光纹（参考 Kayle_Base_Q_Cracks），一圈金环向外扩散。约 40 格宽（半径 20000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a celestial gold ramp (#FFFFFF, #FFF8DC, #F6DC7C, #D8A838, #9A6A1C, #5A3A10).
Effect: a RADIANT BLAST on the ground, 7 frames: 1 a bright white star flash at the center of the cell; 2 a burst of white and gold light, a vertical beam of light shooting up from the center; 3 a flat golden ring on the ground (an ellipse twice as wide as tall) expands to 60% of the cell width, glowing crack lines spread over the ground inside it like shattered glass; 4 the ring at 95% of the cell width, the cracks bright gold, small gold motes rising; 5 the beam gone, the ring thins, the cracks dim to dark gold; 6 broken ring segments and faint cracks; 7 the last gold specks.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; the blast centered in every cell (the ground ellipse centered at 55% of the cell height), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `kayle_fx_e_bolt.png`：星火符刃的星火（飞行），4 帧循环

E 射出的一团星火：比普攻的火焰弹更大更亮，火核外包着旋转的火舌。约 18 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy fire ramp (#FFFFFF, #FFF4C8, #FFD24A, #F7941D, #C4520E, #6E2608).
Effect: a BLAZING STARFIRE ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round white-gold core at 75% of the cell width, wrapped in golden flame tongues that swirl around it (turning a quarter each frame), a thick tail of orange and dark orange flame streaming to the left edge of the cell, a few embers trailing.
Layout: one horizontal row of 4 equal cells, each 5 wide to 2 tall, image size 1280x128 (each cell 320x128); the orb on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `kayle_fx_e_hit.png`：星火命中（跟着目标），6 帧

星火砸在目标身上：一道竖着的剑形火光从上往下劈下，炸开一团火焰。约 20 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy fire ramp (#FFFFFF, #FFF4C8, #FFD24A, #F7941D, #C4520E, #6E2608).
Effect: a STARFIRE STRIKE on an enemy, 6 frames: 1 a thin white vertical line of light from the top of the cell down to the center; 2 it becomes a blazing sword-shaped flame striking down, white core, golden edges; 3 it bursts at the center into a round explosion of golden and orange flame about 60% of the cell wide; 4 the flames billow outward, dark orange at the edges, sparks flying; 5 the flames break into rising embers; 6 the last dark orange embers fading.
Layout: one horizontal row of 6 equal cells, each 5 wide to 6 tall, image size 1440x288 (each cell 240x288); the burst centered horizontally at 55% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `kayle_fx_e_blast.png`：星火爆炸（8 级起，地面范围），7 帧

8 级起星火命中后在目标周围炸开一圈火：地上一个火环向外烧开。约 40 格宽（半径 20000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a holy fire ramp (#FFFFFF, #FFF4C8, #FFD24A, #F7941D, #C4520E, #6E2608).
Effect: a RING OF HOLY FIRE bursting on the ground, 7 frames: 1 a white-gold flash at the center of the cell; 2 a ring of flame (an ellipse twice as wide as tall) bursts out to 50% of the cell width, flame tongues standing up along it; 3 the ring at 95% of the cell width, tall golden flames with orange tips all around it, the inside glowing; 4 the flames at their highest, embers flying up and out; 5 the flames sink and turn orange and dark orange; 6 a ring of embers and small flames on the ground; 7 the last embers.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; the ring centered in every cell (the ground ellipse centered at 60% of the cell height), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `kayle_fx_w_heal.png`：星界恩典（跟着凯尔和友方英雄），8 帧

回血加速：身体周围升起嫩绿色的治疗光，几个绿色小十字往上飘，脚下几道金色的速度线。**不能挡住身体和脸**。人形空位约 36 格高、20 格宽（普通英雄的大小）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a healing ramp (#FFFFFF, #F2FFD8, #C8F27A, #86D045, #4A8A24) with a few gold accents (#F6DC7C).
Effect: CELESTIAL BLESSING around a hero, 8 frames. In the middle of every cell there is an EMPTY space the size of a small hero (75% of the cell height, 40% of the cell wide, feet at 88% of the cell height) - never draw the hero and never draw over that space. 1 a thin light green ring flashes on the ground under the space (an ellipse twice as wide as tall); 2 soft columns of light green light rise along both sides of the space; 3 three small green plus signs and white sparkles rise beside the space, short golden speed lines streak horizontally at its feet; 4 the plus signs higher, the light columns at full height; 5 the plus signs near the top, the columns thinning; 6 the speed lines fade, the ring fading; 7 a few green sparkles high up; 8 the last sparkles.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `kayle_fx_r_invuln.png`：圣裁之刻的无敌护盾（跟着目标，2.5 秒），6 帧，无缝循环

被保护的英雄身上一层金色的光罩：一个金白色的椭圆光球罩住全身，脚下一圈金色圆环（参考 Kayle_Base_R_circle），头顶有一道从天而降的细光柱。**不能挡住身体和脸**（光罩只画边，里面空着）。人形空位同第 10 条。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a celestial gold ramp (#FFFFFF, #FFF8DC, #F6DC7C, #D8A838, #9A6A1C).
Effect: DIVINE PROTECTION around a hero, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY space the size of a small hero (70% of the cell height, 38% of the cell wide, feet at 88% of the cell height) - never draw the hero and never draw over that space. Around it: the OUTLINE of a tall golden bubble (1-2 pixels thick, empty inside) hugging the space; an ornate golden ring on the ground under the feet (an ellipse twice as wide as tall, with small diamond ornaments at its left and right); a thin shaft of white-gold light coming down from the top edge of the cell onto the bubble's top; a bright glint travels around the bubble outline, a sixth of the way each frame; tiny gold motes drift up inside the ring; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1152x256 (each cell 192x256); centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `kayle_fx_r_blades.png`：天降圣剑（无敌结束时，在目标周围的大范围），8 帧

无敌结束的一刻：天上落下一圈燃着火的金剑（参考 Kayle_BeamswordShapes_Orange 和 R_SkyBeam），插进地上的金色大圆环里，然后整圈爆开。约 80 格宽（半径 40000）、60 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a celestial gold ramp (#FFFFFF, #FFF8DC, #F6DC7C, #D8A838, #9A6A1C) and holy fire (#FFD24A, #F7941D, #C4520E).
Effect: DIVINE JUDGMENT, flaming swords raining down in a wide circle, 8 frames: 1 a thin ornate golden ring appears on the ground (an ellipse twice as wide as tall, 95% of the cell width, centered at 70% of the cell height) with small diamond ornaments; 2 six long thin golden swords, point down, appear at the top of the cell above points spread over the ring, each with a short flame trail above it; 3 the swords fall halfway down, streaks of white light behind them; 4 the swords strike the ground on the ring and inside it, each impact a white flash; 5 every impact bursts into a column of golden flame, the ring blazing bright; 6 the flame columns at full height, embers flying; 7 the flames sink, the swords fade to gold light; 8 the ring and a few embers fading.
Layout: one horizontal row of 8 equal cells, each 4 wide to 3 tall, image size 4096x384 (each cell 512x384); the ring centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `kayle_fx_ascend.png`：升阶仪式（5、8、12 级各一次，跟着凯尔），10 帧

凯尔升阶的一刻：一道金色光柱从天而降罩住她，背后腾起一对火焰的羽翼轮廓，火星四散，脚下一圈金环。**不能挡住身体和脸**。人形空位约 42 格高、26 格宽（她连翅膀的大小，离地悬浮 3 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a celestial gold ramp (#FFFFFF, #FFF8DC, #F6DC7C, #D8A838) and holy fire (#FFD24A, #F7941D, #C4520E).
Effect: DIVINE ASCENT, an angel's rank-up ceremony, 10 frames. In the middle of every cell there is an EMPTY space the size of a winged hero (70% of the cell height, 45% of the cell wide, its bottom at 86% of the cell height) - never draw the hero and never draw over that space. 1 a thin golden ring appears on the ground under the space (an ellipse twice as wide as tall); 2 a shaft of white-gold light comes down from the top edge of the cell onto the space, as wide as the space; 3 the shaft at full brightness, its edges golden; 4 behind the space two big wing shapes of golden fire unfold upward and outward (outlines of flame feathers, larger than the space, never covering it); 5 the fire wings at full size, sparks bursting out; 6 the shaft fades, the wings still burning; 7 the wings break into rising flame feathers; 8 feathers and sparks drifting up and out; 9 a few golden sparks high up, the ring fading; 10 the last sparks.
Layout: one horizontal row of 10 equal cells, each 1 wide to 1 tall, image size 2560x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `kayle_fx_exalted.png`：昂扬（狂热满层时一直跟着凯尔；12 级「超然」永久），6 帧，无缝循环

昂扬状态下凯尔身上燃着圣火：肩膀和背后冒出一小簇一小簇的金橙色火苗往上飘，脚下几点余烬。**不能挡住身体和脸**，火只在人形空位的外沿和背后。人形空位同第 13 条。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a holy fire ramp (#FFFFFF, #FFF4C8, #FFD24A, #F7941D, #C4520E).
Effect: EXALTED, holy flames on a winged hero, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY space the size of a winged hero (70% of the cell height, 45% of the cell wide, its bottom at 86% of the cell height) - never draw the hero and never draw over that space. Small golden flame tongues (3 to 7 pixels tall) flicker along the outside of the space at the shoulders and upper back (left and upper left of the space, where her wings are), their tips drifting up and fading to orange; a few embers float up beside the space and two or three glow under its feet; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，头部从 `native/kayle_native.png` 贴在头部关节的位置，帧时长写在 `native/kayle_cells.json`。特效由 `tools/art/import_kayle.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `kayle_fx_hit.png` | 5 | 特效 `league_kayle_hit`（近战命中） | 5 × 50 |
| `kayle_fx_bolt.png` | 4 | 投射物 `league_kayle_bolt`（远程普攻，朝飞行方向转） | 4 × 60 循环 |
| `kayle_fx_bolt_hit.png` | 5 | 特效 `league_kayle_bolt_hit`（远程命中） | 5 × 50 |
| `kayle_fx_wave.png` | 4 | 投射物 `league_kayle_wave`（焰浪 70000 × 10000，朝飞行方向转） | 4 × 60 循环 |
| `kayle_fx_q_sword.png` | 4 | 投射物 `league_kayle_q_sword`（Q 的剑，朝飞行方向转） | 4 × 60 循环 |
| `kayle_fx_q_blast.png` | 7 | 特效 `league_kayle_q_blast`（半径 20000） | 7 × 60 |
| `kayle_fx_e_bolt.png` | 4 | 投射物 `league_kayle_e_bolt`（E 的星火，朝飞行方向转） | 4 × 60 循环 |
| `kayle_fx_e_hit.png` | 6 | 特效 `league_kayle_e_hit`（跟随目标） | 6 × 50 |
| `kayle_fx_e_blast.png` | 7 | 特效 `league_kayle_e_blast`（8 级起，半径 20000） | 7 × 60 |
| `kayle_fx_w_heal.png` | 8 | 特效 `league_kayle_w_heal`（跟随凯尔和友方英雄） | 8 × 80 |
| `kayle_fx_r_invuln.png` | 6 | 增益 `league_kayle_r_invuln`（无敌 2.5 秒循环） | 6 × 100 循环 |
| `kayle_fx_r_blades.png` | 8 | 特效 `league_kayle_r_blades`（半径 40000） | 8 × 70 |
| `kayle_fx_ascend.png` | 10 | 特效 `league_kayle_ascend1/2/3`（跟随凯尔，5/8/12 级） | 10 × 80 |
| `kayle_fx_exalted.png` | 6 | 增益 `league_kayle_zeal5`、`league_kayle_rank12`（昂扬循环） | 6 × 100 循环 |

特效表：`league_kayle_fx`（bolt、wave、q_sword、e_bolt、hit、bolt_hit、e_hit、w_heal、exalted），`league_kayle_big`（q_blast、e_blast、r_blades、ascend、r_invuln）。
