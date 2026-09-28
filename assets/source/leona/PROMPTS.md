# 莱昂娜：给 Codex 的特效提示词

> **这一轮只画 10 张特效图。**
> - 角色不用画：莱昂娜的模型由 Claude 做（和金克丝一样）。造型图是英雄联盟的模型按材质投色，再逐格画上脸（用户选了方案 C：原版画法的三行眼睛、上扬眼线、下巴正中一格暗红小嘴）；动作图用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）。
> - 定稿造型图 `native/leona_native.png` 只用来参考配色，不要改它。
> - 特效照下面第 1–10 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_leona.py --raw` 转成原尺寸条，再按技能范围定大小。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 剑劈 | `leona_fx_hit` |
| 被动「日光」 | 技能命中的敌人被标记 1.5 秒，期间受到的伤害提高 | `leona_fx_sunlight` |
| 技能 1 = Q「破晓之盾」 | 用盾猛击身边的敌人，眩晕 1 秒 | `leona_fx_q_hit` |
| 技能 2 = E「天顶之刃」+ W「日蚀」 | 掷出剑光，直线上的敌人受到伤害，第一个敌方英雄被禁锢，莱昂娜冲到它身边；同时举盾（减伤 3 秒），3 秒后盾牌爆发，伤害周围敌人 | `leona_fx_e_blade` · `leona_fx_e_hit` · `leona_fx_e_root` · `leona_fx_eclipse` · `leona_fx_w_burst` |
| 大招 = R「日炎耀斑」 | 敌方英雄脚下出现光圈，0.6 秒后一道阳光落下：范围内减速，中心眩晕 1.75 秒 | `leona_fx_r_flare` · `leona_fx_r_stun` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（莱昂娜的日光）：
  - 日光：`#FFFFFF`、`#FFF6C8`、`#FFE27A`、`#FFC23F`、`#FF9A2E`、`#E8641E`、`#B8361A`；
  - 日蚀的暗盘：`#3A1A2E`、`#6B2A48`；
  - 眩晕的星：`#FFFFFF`、`#FFE27A`、`#FFC23F`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、光圈、光柱、标记居中画，不旋转；地面上的圈按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `leona_fx_hit.png`：普攻命中，5 帧

剑砍中目标时的金色斩光。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E).
Effect: a SWORD SLASH HIT, 5 frames: 1 a thin white-hot diagonal cut line appears at the center, from upper left to lower right; 2 the cut widens into a bright crescent of gold light with a white core, a few sparks; 3 the crescent at full size, about 45% of the cell wide, small gold sparks flying outward; 4 it breaks into sparks; 5 the last gold specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `leona_fx_q_hit.png`：破晓之盾命中 + 眩晕（跟着目标），6 帧

盾砸中敌人：先爆一个太阳形的金光，然后几颗小金星在它头顶打转（眩晕 1 秒）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E, #E8641E).
Effect: SHIELD OF DAYBREAK, an enemy bashed by a sun shield and STUNNED, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a white flash hits the chest of the space from the LEFT; 2 a round golden SUNBURST bursts at the chest, a bright disc with eight short sharp rays, white core, orange tips; 3 the sunburst at full size, about 45% of the cell wide, gold sparks thrown to the right; 4 it fades, and three small gold stars appear above the head of the space; 5-6 the three stars circle above the head (they move a quarter turn each frame), a faint gold glow on the body.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `leona_fx_e_blade.png`：天顶之刃的剑光（飞行物），4 帧循环

游戏按方向旋转。碰撞半径 7000：剑光约 28 格长、8 格粗。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E, #E8641E).
Effect: ZENITH BLADE, a solar image of a sword flying to the RIGHT, 4 frames, a seamless loop: a glowing golden longsword made of sunlight, its point to the RIGHT and its crossguard near the left end - a white-hot blade core, a gold glow around it, a small sun-shaped jewel at the crossguard - with a short trail of gold light streaks and sparks streaming to the left; SYMMETRIC above and below its middle line; only the trail and the glow flicker from frame to frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each four times as wide as tall (4:1), image size 2048x128; the blade along the middle height of the cell, blade plus trail about 90% of the cell wide and 40% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `leona_fx_e_hit.png`：剑光命中（跟着目标），5 帧

剑光穿过路径上的每个敌人时播放。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E).
Effect: a SOLAR BLADE HIT, 5 frames: 1 a white-hot horizontal streak crosses the center from left to right; 2 it flares into a bright gold star with four long points (horizontal points longer), white core; 3 the star at full size, about 50% of the cell wide, gold sparks spraying to the right; 4 the star shrinks, sparks drifting; 5 the last gold specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `leona_fx_e_root.png`：禁锢（被冲到的英雄脚下），6 帧（0.5 秒）

第一个被剑光命中的敌方英雄被禁锢 0.5 秒，莱昂娜冲过去。画在地上，按斜俯视角度画成扁圆，约 26 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E, #E8641E).
Effect: a SUN SIGIL ROOT on the ground, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a thin gold ring flashes on the ground around the feet (a flat ellipse about twice as wide as tall, 60% of the cell wide); 2 a sun sigil lights up inside it: the ring plus eight short rays pointing outward, white inner glow; 3 two bands of gold light wrap around the ankles of the space; 4-5 the sigil and the bands glow steadily, small light motes rising from the ring; 6 everything fades to a faint ring.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the ring centered under the empty space's feet, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `leona_fx_sunlight.png`：日光标记（敌人头顶），6 帧，无缝循环

被技能命中的敌人头顶亮起一个小太阳，持续 1.5 秒。约 12 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E).
Effect: the SUNLIGHT MARK, a small sun emblem hovering, 6 frames, a seamless loop: a small round golden sun disc with a white center and eight short pointed rays (alternating long and short), slowly turning - the rays turn a little each frame - and pulsing (the glow a little bigger in frames 3-4); frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the emblem centered in every cell, about 50% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `leona_fx_eclipse.png`：日蚀护盾（莱昂娜身上），8 帧，无缝循环

举盾后 3 秒内受到的伤害降低：她身边罩着一层金色日光，腰间有几颗光珠绕着转。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E) with an eclipse disc (#3A1A2E, #6B2A48).
Effect: ECLIPSE, a solar barrier around a warrior, 8 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. A thin shimmering outline of gold light traces around the whole space like a shell (broken into short dashes that crawl upward frame by frame); four small bright sun beads orbit around the waist on a flat ellipse (they move an eighth of a turn each frame; the ones behind the space are hidden); a faint gold ring glows on the ground under the feet; frame 8 leads back into frame 1.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `leona_fx_w_burst.png`：日蚀爆发（莱昂娜周围），7 帧

3 秒后盾牌爆发，伤害周围 35000 内的敌人：地上一圈日光向外炸开，约 70 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E, #E8641E, #B8361A) with an eclipse disc (#3A1A2E, #6B2A48).
Effect: the ECLIPSE BURST around a warrior, 7 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 40% of the cell height stands there, feet at 75% of the cell height) - never draw the person. 1 a dark eclipse disc with a blinding white-gold corona flashes at the chest of the space; 2 the corona bursts: a ring of sunfire races out along the ground around the feet (a flat ellipse twice as wide as tall); 3 the ring at 70% of the cell wide, rays of light shooting up from it, white-hot inner edge; 4 the ring at full size, 90% of the cell wide, orange outer edge, sparks thrown up; 5 the ring breaks into flames on the ground; 6 embers and light motes rising; 7 the last motes fading.
Layout: one horizontal row of 7 equal cells, each twice as wide as tall (2:1), image size 3584x256; the ring centered under the empty space's feet, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `leona_fx_r_flare.png`：日炎耀斑（落点），12 帧（1 秒）

画在敌方英雄脚下，不旋转。前 6 帧是预警光圈（0.6 秒），第 7 帧光柱从天而降（伤害在这一帧），后 5 帧爆开、消散。外圈半径 36000（约 72 格宽，减速），内圈半径 16000（约 32 格宽，眩晕）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a sunlight ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23F, #FF9A2E, #E8641E, #B8361A).
Effect: SOLAR FLARE, a beam of sunlight called down from the sky onto a spot on the ground, 12 frames. The ground is a line at 80% of the cell height; the circles lie on it as flat ellipses twice as wide as tall. 1 a thin gold circle appears on the ground (80% of the cell wide) with a smaller inner circle (35% of the cell wide); 2-5 the circles glow brighter frame by frame, sun rays pattern appears between them, a small white-hot sun glints at the top of the cell and grows; 6 the whole circle burns bright, the inner circle white-hot; 7 A MASSIVE PILLAR OF SUNLIGHT slams straight down from the top of the cell onto the inner circle - white core, gold, orange edges, about 30% of the cell wide; 8 the blast: a flattened ring of sunfire races outward along the ground to the outer circle, the pillar thinning; 9 the pillar gone, the ring of fire at full size with sparks flying up; 10 the fire breaks into embers; 11 light motes rising; 12 the last motes fading.
Layout: one horizontal row of 12 equal cells, each as wide as tall (1:1), image size 3072x256; everything centered horizontally, the circles on the ground line at 80% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `leona_fx_r_stun.png`：日炎耀斑的眩晕（跟着目标），8 帧，可循环

处在光圈中心的敌人眩晕 1.75 秒：头顶一圈金星打转，身上残留一点金光。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, stars (#FFFFFF, #FFE27A, #FFC23F) and a sunlight glow (#FFF6C8, #FF9A2E).
Effect: STUNNED BY SUNLIGHT, 8 frames, a seamless loop. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. Four small bright gold stars circle above the head of the space on a flat ellipse (they move an eighth of a turn each frame; the ones behind the head are smaller), a few gold light motes drift down over the body; frame 8 leads back into frame 1.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the effect at most 50% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，帧时长写在 `native/leona_cells.json`。特效由 `tools/art/import_leona.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `leona_fx_hit.png` | 5 | 特效 `league_leona_hit`（普攻命中） | 5 × 50 |
| `leona_fx_q_hit.png` | 6 | 特效 `league_leona_q_hit`（跟随目标，眩晕 1 秒） | 60/60/80/100/180/180 |
| `leona_fx_e_blade.png` | 4 | 投射物 `league_leona_e_blade`（半径 7000） | 4 × 50 循环 |
| `leona_fx_e_hit.png` | 5 | 特效 `league_leona_e_hit`（跟随目标） | 5 × 60 |
| `leona_fx_e_root.png` | 6 | 特效 `league_leona_e_root`（跟随目标，地面，0.5 秒） | 6 × 85 |
| `leona_fx_sunlight.png` | 6 | buff `league_leona_sunlight`（敌人头顶，1.5 秒） | 6 × 100 循环 |
| `leona_fx_eclipse.png` | 8 | buff `league_leona_eclipse`（莱昂娜身上，3 秒） | 8 × 100 循环 |
| `leona_fx_w_burst.png` | 7 | 特效 `league_leona_w_burst`（跟随莱昂娜，半径 35000） | 7 × 70 |
| `leona_fx_r_flare.png` | 12 | 投射物 `league_leona_r_flare`（落点，半径 36000 / 中心 16000，存在 1 秒，第 0.62 秒结算） | 6 × 100，50，5 × 70 |
| `leona_fx_r_stun.png` | 8 | 特效 `league_leona_r_stun`（跟随目标，1.75 秒） | 8 × 110，重复两遍 |

特效表：`league_leona_fx`（hit、q_hit、e_blade、e_hit、e_root、sunlight、eclipse、r_stun），`league_leona_big`（w_burst、r_flare）。
