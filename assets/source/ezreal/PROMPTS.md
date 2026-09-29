# 探险家 伊泽瑞尔：给 Codex 的特效提示词

> **这一轮只画 15 张特效图。**
> - 角色不用画：伊泽瑞尔的模型由 Claude 做（头部逐格画好贴在肩上，身体用英雄联盟原版动画重新上色，`tools/art/restyle_native.py`）。
> - 定稿造型图 `native/ezreal_native.png` 只用来参考配色和人物大小（约 34 格高、18 格宽，金发、头顶白框护目镜、棕夹克、左臂金色手甲），不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里伊泽瑞尔自己的特效贴图（金黄色的奥术光球和能量线、Q 的青蓝色螺旋尾迹、R 弹头的橙金色弧光、被动的金色星芒），只在本地用，不要提交。
> - 特效照下面第 1–15 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_ezreal.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「咒能高涨」 | 手甲射出奥术光弹；技能每打中一个目标，攻速 +12%（最多 5 层，满层时手甲发光） | `ezreal_fx_bolt` · `ezreal_fx_hit` · `ezreal_fx_rsf` |
| 技能 1 = Q「秘术射击」+ W「精华跃动」 | Q：一道能量箭打中第一个敌人。W（有自己的冷却）：先朝敌方英雄扔出精华球，粘在他身上 4 秒，下一次普攻或技能打中英雄时引爆 | `ezreal_fx_q_bolt` · `ezreal_fx_q_hit` · `ezreal_fx_w_orb` · `ezreal_fx_w_stick` · `ezreal_fx_w_mark` · `ezreal_fx_w_boom` |
| 技能 2 = E「奥术跃迁」 | 敌方英雄贴近时往后闪开，再朝他射出一支追踪奥术箭 | `ezreal_fx_e_blink` · `ezreal_fx_e_bolt` · `ezreal_fx_e_hit` |
| 大招 = R「精准弹幕」 | 手甲蓄力 1 秒，射出一道横贯全图的巨大金色能量弧 | `ezreal_fx_r_charge` · `ezreal_fx_r_wave` · `ezreal_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（都从英雄联盟伊泽瑞尔的特效里取）：
  - 奥术金光（白到深）：`#FFFBEA`、`#FFEFA8`、`#FFD65A`、`#F0A830`、`#B8701C`、`#6E3E10`；
  - 青蓝点缀（Q 的尾迹、E 箭的尾巴）：`#E8FDFF`、`#9EEBFA`、`#46BEE6`、`#1E7AAE`；
  - R 弹头的橙色外缘：`#FFB24A`、`#F07A1E`、`#B8420E`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、爆裂、标记居中画，不旋转；地面上的圈按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在伊泽瑞尔身上的特效（闪现、满层光效）：格子中间留出一个空的人形位置（按那条写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `ezreal_fx_bolt.png`：普攻光弹（飞行），4 帧循环

手甲射出的小奥术光弹：金白色的核心，后面拖一小段金色光尾。约 12 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C).
Effect: an ARCANE BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line. At the right end of the cell a small round white-gold core about 35% of the cell tall, a pointed tip on its right; behind it to the left a short tapering gold light trail with one or two small square sparks that flicker from frame to frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the core at the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `ezreal_fx_hit.png`：普攻命中（E 箭命中也可共用），5 帧

光弹打中目标：一个金色的小星形闪光，四散几颗小方块火花。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C).
Effect: an ARCANE HIT, 5 frames: 1 a small white-hot dot at the center; 2 it flashes into a four-pointed gold star; 3 the star at full size, about 45% of the cell wide, with a thin gold ring and four small square sparks flying out diagonally; 4 the star shrinks, the sparks further out; 5 two or three sparks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the hit at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `ezreal_fx_q_bolt.png`：秘术射击（飞行），4 帧循环

Q 的能量箭：比普攻大，金白色的箭头，后面是两条交缠的青蓝色能量尾迹（像英雄联盟里 Q 的螺旋尾巴）。约 22 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830) and a cyan ramp (#E8FDFF, #9EEBFA, #46BEE6, #1E7AAE).
Effect: MYSTIC SHOT, an energy bolt flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line. At the right end a bright white-gold arrowhead of light, about 45% of the cell tall, pointing right, with a thin gold rim; behind it to the left two thin cyan energy strands twisting around each other like a braid, tapering toward the left end, the twist moving one step along the braid each frame; a few small square gold sparks.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the arrowhead at the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `ezreal_fx_q_hit.png`：秘术射击命中，6 帧

Q 打中目标：金色的冲击爆开，里面闪一下青蓝色的光，飞出几道短光线。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C) and a cyan accent (#9EEBFA, #46BEE6).
Effect: MYSTIC SHOT IMPACT, 6 frames: 1 a white flash at the center with a cyan edge; 2 a round gold burst about 40% of the cell wide with six short straight rays; 3 the burst at 60% of the cell wide, its middle hollow, cyan sparks at the ends of the rays; 4 a thin gold ring expanding to 75%, square shards flying out; 5 the ring breaking up; 6 the last shards fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the hit at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `ezreal_fx_w_orb.png`：精华跃动的精华球（飞行），4 帧循环

W 扔出的精华球：一颗发光的金色圆球，外面绕着一圈转动的细光环。约 16 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C).
Effect: ESSENCE FLUX ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line. In the right half of the cell a glowing round orb about 55% of the cell tall: a white-hot center, a gold body, a darker gold rim; around it a thin tilted gold ring that turns a quarter each frame; behind the orb to the left a short faint gold trail of three or four small squares.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 1024x170 (each cell 256x170); the orb at the right half of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `ezreal_fx_w_stick.png`：精华球粘上英雄（跟着目标），5 帧

精华球撞上英雄、粘住的一下：金光一闪，一圈光环收紧成一个亮点。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C).
Effect: ESSENCE FLUX STICKING to a target, 5 frames: 1 a gold orb at the center with a wide thin ring around it (80% of the cell wide); 2 the ring shrinks to 55%, the orb flashes white; 3 the ring snaps onto the orb, a burst of eight tiny sparks; 4 a small glowing gold orb with a tight ring, the sparks drifting out; 5 the small orb pulsing, one or two sparks left.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `ezreal_fx_w_mark.png`：精华印记（跟着目标，循环），4 帧

粘在英雄身上的印记：一个金色的菱形符文，外面一圈慢慢转的虚线光环，轻轻脉动。这张会连续播放，最后一帧要能接回第一帧。约 18 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C).
Effect: ESSENCE FLUX MARK on a target, 4 frames, a seamless loop: in the center a small glowing gold diamond rune about 30% of the cell wide with a white center; around it a dashed gold ring about 75% of the cell wide made of eight short arcs, the ring turning one arc further each frame; the diamond pulses slightly brighter in frames 2 and 3.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `ezreal_fx_w_boom.png`：精华跃动引爆，7 帧

印记被引爆：金色的爆炸，一圈冲击环向外扩开，碎光四溅。约 40 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C, #6E3E10) and an orange accent (#FFB24A, #F07A1E).
Effect: ESSENCE FLUX DETONATION, 7 frames: 1 the gold diamond rune flashing white at the center; 2 a round white-gold explosion about 35% of the cell wide; 3 the explosion at 60% of the cell wide with eight straight rays, orange at its edge; 4 a thick gold shockwave ring at 80% of the cell wide, the center hollowing out, square sparks flying; 5 the ring at 95% and thinning, sparks further out; 6 the ring breaking into arcs; 7 the last sparks fading.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `ezreal_fx_e_blink.png`：奥术跃迁的闪光（起点消失、落点出现共用），6 帧

伊泽瑞尔闪走的地方：一个人形大小的金色光柱一闪，化成往上飘的金色小方块（落点出现时 Claude 会倒着播）。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C) and a cyan accent (#9EEBFA, #46BEE6).
Effect: ARCANE SHIFT BLINK, 6 frames, a person-sized flash (a person about 60% of the cell tall stands in the middle, feet at 88% of the cell height - never draw the person). 1 a thin bright gold ring on the ground around the feet (a flat ellipse, twice as wide as tall) and a few gold sparks; 2 a bright white-gold vertical column of light rising from the ring to the height of the person, cyan edges; 3 the column at full brightness, wider, the ring flashing; 4 the column breaks into many small gold squares; 5 the squares float upward and spread out; 6 a few last squares high up, fading.
Layout: one horizontal row of 6 equal cells, each 4 wide to 5 tall, image size 1536x320 (each cell 256x320); the ring's center at 88% of the cell height, centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `ezreal_fx_e_bolt.png`：奥术跃迁的追踪箭（飞行），4 帧循环

E 射出的追踪奥术箭：细长的金白色箭，后面一条青蓝色的细尾巴。约 16 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830) and a cyan ramp (#E8FDFF, #9EEBFA, #46BEE6, #1E7AAE).
Effect: ARCANE SHIFT HOMING BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right end a slim white-gold dart of light about 30% of the cell tall with a sharp tip; behind it a long thin cyan tail that waves slightly from frame to frame and tapers to the left edge; two tiny gold sparks.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1024x85 (each cell 256x85); the dart at the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `ezreal_fx_e_hit.png`：追踪箭命中，5 帧

追踪箭打中目标：金色星形爆开，带一圈青蓝色的小火花。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C) and a cyan accent (#9EEBFA, #46BEE6).
Effect: HOMING BOLT IMPACT, 5 frames: 1 a white spark at the center; 2 a six-pointed gold star about 45% of the cell wide; 3 the star at 60% of the cell wide with a ring of eight small cyan sparks around it; 4 the star fading, the cyan sparks flying outward; 5 the last sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `ezreal_fx_r_charge.png`：精准弹幕蓄力（手甲前方），8 帧

大招蓄力 1 秒：金色的光点从四周被吸进一个越来越亮的光球，光球四周转着一圈光环，最后一帧最亮。约 26 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C) and an orange accent (#FFB24A, #F07A1E).
Effect: TRUESHOT BARRAGE CHARGE, energy gathering into a ball, 8 frames: 1 six small gold squares far out near the cell edges and a tiny glowing dot at the center; 2-4 the squares streak inward as short light lines, the ball at the center growing from 15% to 35% of the cell wide, a thin gold ring turning around it; 5-6 the ball at 45%, white-hot core, orange rim, two rings crossing around it; 7 the ball pulses brighter with short rays; 8 the brightest frame: a white-gold ball at 55% of the cell wide with eight rays.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `ezreal_fx_r_wave.png`：精准弹幕的能量弧（飞行，横贯全图），4 帧循环

大招射出的巨大能量波：前端是一道弯向右边的金白色大弧（像一弯新月立着，凸面朝前），弧的边缘是橙色，后面拖着一大片渐淡的金色光带。约 44 格长、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C, #6E3E10) and an orange ramp (#FFB24A, #F07A1E, #B8420E).
Effect: TRUESHOT BARRAGE, a massive energy wave flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line. At the right part of the cell a big standing crescent arc of light, as tall as 90% of the cell, bulging toward the RIGHT: a white-hot inner edge, a thick gold body, an orange outer rim. Behind it to the left a wide gold energy trail as tall as the arc, fading and breaking into horizontal streaks and square sparks toward the left edge; the streaks shift a little each frame so the wave looks like it is rushing forward.
Layout: one horizontal row of 4 equal cells, each 5 wide to 4 tall, image size 1280x256 (each cell 320x256); the arc at the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `ezreal_fx_r_hit.png`：精准弹幕打中（跟着目标），5 帧

能量弧扫过的每个敌人身上：一团金橙色的冲击，飞出几道光线。约 26 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830) and an orange accent (#FFB24A, #F07A1E).
Effect: TRUESHOT BARRAGE HIT on an enemy, 5 frames: 1 a white flash at the center; 2 a round gold-orange burst about 45% of the cell wide with rays streaking to the right (the wave passed from left to right); 3 the burst at 65% of the cell wide, hollow middle, square sparks flying right and up; 4 the sparks further out, the burst thinning; 5 the last sparks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `ezreal_fx_rsf.png`：咒能高涨满层（套在伊泽瑞尔身上，循环），6 帧

被动叠满 5 层时：金色的小光点和短光线绕着人往上飘，手甲的位置（人形的右侧、胸口高度）有一颗亮星一闪一闪。这张会连续播放，最后一帧要能接回第一帧。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane gold ramp (#FFFBEA, #FFEFA8, #FFD65A, #F0A830, #B8701C).
Effect: RISING SPELL FORCE at full stacks, an aura around an EMPTY person-sized space (a person about 60% of the cell tall stands in the middle, feet at 88% of the cell height - never draw the person), 6 frames, a seamless loop: small gold light motes and short gold streaks rising upward around the space; at the person's right side at chest height a small four-pointed white-gold star that twinkles (bigger in frames 1 and 4); a thin faint gold ring on the ground around the feet (a flat ellipse). Subtle, not covering the middle.
Layout: one horizontal row of 6 equal cells, each 4 wide to 5 tall, image size 1536x320 (each cell 256x320); the feet at 88% of the cell height, centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，头部从 `native/ezreal_native.png` 贴在肩上，帧时长写在 `native/ezreal_cells.json`。特效由 `tools/art/import_ezreal.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）；E 的闪光在起点正着播（`e_depart`），在落点倒着播（`e_arrive`）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `ezreal_fx_bolt.png` | 4 | 投射物 `league_ezreal_bolt`（普攻，朝飞行方向转） | 4 × 60 循环 |
| `ezreal_fx_hit.png` | 5 | 特效 `league_ezreal_hit`（普攻命中，跟随目标） | 5 × 50 |
| `ezreal_fx_q_bolt.png` | 4 | 投射物 `league_ezreal_q`（Q，半径 6000） | 4 × 60 循环 |
| `ezreal_fx_q_hit.png` | 6 | 特效 `league_ezreal_q_hit`（跟随目标） | 6 × 50 |
| `ezreal_fx_w_orb.png` | 4 | 投射物 `league_ezreal_w`（W，半径 8000） | 4 × 60 循环 |
| `ezreal_fx_w_stick.png` | 5 | 特效 `league_ezreal_w_stick`（粘住，跟随目标） | 5 × 50 |
| `ezreal_fx_w_mark.png` | 4 | 特效 `league_ezreal_w_mark`（每 15 帧播一次，一段 0.25 秒，跟随目标） | 4 × 62 |
| `ezreal_fx_w_boom.png` | 7 | 特效 `league_ezreal_w_boom`（引爆，跟随目标） | 7 × 55 |
| `ezreal_fx_e_blink.png` | 6 | 特效 `league_ezreal_e_depart`（起点，不跟随）/ `league_ezreal_e_arrive`（落点，倒放，跟随） | 6 × 50 |
| `ezreal_fx_e_bolt.png` | 4 | 投射物 `league_ezreal_e_bolt` | 4 × 60 循环 |
| `ezreal_fx_e_hit.png` | 5 | 特效 `league_ezreal_e_hit`（跟随目标） | 5 × 50 |
| `ezreal_fx_r_charge.png` | 8 | 特效 `league_ezreal_r_charge`（手甲前方，跟随伊泽瑞尔，1 秒） | 8 × 120 |
| `ezreal_fx_r_wave.png` | 4 | 投射物 `league_ezreal_r_wave`（半径 18000） | 4 × 70 循环 |
| `ezreal_fx_r_hit.png` | 5 | 特效 `league_ezreal_r_hit`（跟随目标） | 5 × 50 |
| `ezreal_fx_rsf.png` | 6 | 增益 `league_ezreal_rsf_5`（满层时一直循环） | 6 × 100 循环 |

特效表：`league_ezreal_fx`（bolt、hit、q_bolt、q_hit、w_orb、w_stick、w_mark、w_boom、e_depart、e_arrive、e_bolt、e_hit、r_hit、rsf_max），`league_ezreal_big`（r_charge、r_wave）。
