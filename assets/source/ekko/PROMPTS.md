# 时间刺客 艾克：给 Codex 的特效提示词

> **这一轮只画 14 张特效图。**
> - 角色不用画：艾克的模型由 Claude 做（头部逐格画好贴在肩上，身体用英雄联盟原版动画重新上色，`tools/art/restyle_native.py`）。大招留在原地的"全息残影"也由 Claude 用艾克自己的模型生成，不在这 14 张里。
> - 定稿造型图 `native/ekko_native.png` 只用来参考配色和人物大小（约 34 格高、36 格宽，低蹲、球棒前指），不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里艾克自己的特效贴图（青绿色的光、齿轮形的 Q 装置、带三角刻度的时钟光环、时间符文、W 引爆时的紫白色碎裂、E 命中的黄白核心），只在本地用，不要提交。
> - 特效照下面第 1–14 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_ekko.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「Z型驱动共振」 | 球棒挥击；普攻、Q 每一趟、E 的闪击各记一层，第 3 层额外爆一次魔法伤害并减速 | `ekko_fx_hit` · `ekko_fx_z_proc` |
| 技能 1 = Q「时间卷曲器」 | 掷出齿轮装置穿过路径上的敌人，在尽头展开减速力场，然后飞回艾克 | `ekko_fx_q_device` · `ekko_fx_q_field` |
| 技能 2 = E「相位俯冲」+ W「时光交错」 | 冲向目标并闪击；W 另有冷却：在附近敌方英雄脚下 1.5 秒后形成时间球，艾克在球里时引爆，眩晕球内敌人并给艾克护盾 | `ekko_fx_e_dash` · `ekko_fx_e_hit` · `ekko_fx_w_forming` · `ekko_fx_w_sphere` · `ekko_fx_w_shatter` · `ekko_fx_w_stun` · `ekko_fx_w_shield` |
| 大招 = R「时空断裂」 | 在脚下留下时间锚点，4 秒后瞬间回到锚点，回血并在落点爆炸 | `ekko_fx_r_depart` · `ekko_fx_r_arrive` · `ekko_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（都从英雄联盟艾克的特效里取）：
  - 时间之光（青绿，白到深）：`#F2FFFB`、`#A8FFE8`、`#5CEACB`、`#2CB89C`、`#1E7E6E`；
  - 全息 / 残影（薄荷）：`#D8FFF0`、`#9CE8D0`、`#5CC4AC`、`#3A8C7E`；
  - 碎裂和引爆的点缀（紫）：`#F0DCFF`、`#C8A0F8`、`#8E62D8`、`#5A3A9A`；
  - E 命中的核心（黄白）：`#FFFBE0`、`#FFF0A0`、`#FFD24A`；
  - Q 装置的金属：`#D8E0E8`、`#8E9AAE`、`#4A5468`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、爆裂、眩晕标记居中画，不旋转；地面上的圈按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在艾克身上的特效（护盾）：格子中间留出一个空的人形位置（按那条写的比例：他低蹲、比较宽），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `ekko_fx_hit.png`：普攻命中，5 帧

球棒打中目标：一个青绿色的小闪光，带两三片时间碎片飞出。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C, #1E7E6E).
Effect: a TIME-BAT HIT, 5 frames: 1 a small white-hot star at the center; 2 it flashes into a four-pointed teal star with a thin broken ring around it; 3 the star at full size, about 45% of the cell wide, three small square teal shards flying out; 4 the star shrinks, the shards further out; 5 two or three shards fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the hit at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `ekko_fx_z_proc.png`：Z型驱动共振触发（跟着目标），6 帧

第 3 层共振爆开：一个带三个三角刻度的青绿色时钟环在目标身上收紧，然后炸成碎片。约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C, #1E7E6E) and a violet accent (#C8A0F8, #8E62D8).
Effect: Z-DRIVE RESONANCE, a clock ring snapping shut on a target and bursting, 6 frames: 1 a thin teal ring, about 80% of the cell wide, with three small triangle notches on it (at the top, lower left and lower right, like a clock face); 2 the ring shrinks to 55% of the cell wide and turns a little, the notches brighter; 3 the ring snaps to 30% of the cell wide with a bright white core; 4 it bursts: a white flash and eight square teal shards flying outward, two of them violet; 5 the shards further out, the flash gone; 6 the last shards fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `ekko_fx_q_device.png`：时间卷曲器（飞行，去程和回程共用），4 帧循环

一个旋转的齿轮装置：金属外圈、青绿色发光的核心，后面拖一小段青绿光带。约 16 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a metal ramp (#D8E0E8, #8E9AAE, #4A5468) and a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C).
Effect: TIMEWINDER, a spinning time device flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line. At the right half of the cell a round gear-shaped device about 40% of the cell tall: a grey metal cog ring with six short teeth around a glowing teal-white core; the cog turns one tooth further each frame. Behind it to the left a short tapering teal light trail with two or three small square sparks.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 1024x170 (each cell 256x170); the device at the right half of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `ekko_fx_q_field.png`：时间力场（装置飞到尽头展开），6 帧

装置停下时展开的减速力场：地面上一圈青绿色的环，环上有刻度，里面是淡淡的扭曲波纹，慢慢收缩后消失（画在人物下层）。圈最大约 44 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C, #1E7E6E).
Effect: TIME FIELD on the ground, 6 frames. A flat ellipse, twice as wide as tall, centered in the cell. 1 a bright teal-white spark at the center; 2 a ring snaps open to 60% of the cell wide, with twelve short tick marks around it like a clock face; 3 the ring at 95% of the cell wide, inside it two faint wavy teal ripples; 4 the ripples turn slowly, the ring holds; 5 the ring starts to shrink toward the center, the ticks dimmer; 6 a small fading ring at 30% of the cell wide.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); the ellipse's center at the same place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `ekko_fx_e_dash.png`：相位俯冲的残影（留在起点），5 帧

艾克冲出去的一瞬间留在原地的残影：一个向右拉长的薄荷色人影轮廓，化成往右飘的小方块消散。约 28 格宽、30 格高（参考定稿造型图里他低蹲的身形）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a mint hologram ramp (#D8FFF0, #9CE8D0, #5CC4AC, #3A8C7E) and a teal light ramp (#A8FFE8, #5CEACB).
Effect: PHASE DIVE AFTERIMAGE, the ghost a boy leaves behind as he dashes to the RIGHT, 5 frames. 1 a flat mint silhouette of a crouching boy with a spiky mohawk, facing right, about 60% of the cell tall, its right edge smeared into horizontal streaks; 2 the silhouette stretched to the right into speed streaks, its left half breaking into small squares; 3 mostly streaks and squares drifting right; 4 a few squares and one thin streak; 5 the last two squares fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the silhouette's feet at 88% of the cell height, its body at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `ekko_fx_e_hit.png`：相位俯冲的闪击命中，6 帧

从天而降的一击：黄白色的核心，外面一圈青绿和紫色的尖刺光，碎片飞散。约 28 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a core ramp (#FFFBE0, #FFF0A0, #FFD24A), a teal light ramp (#A8FFE8, #5CEACB, #2CB89C) and a violet accent (#C8A0F8, #8E62D8).
Effect: PHASE DIVE STRIKE, a blink strike landing on a target, 6 frames: 1 a vertical white slash from the top of the cell down to the center; 2 at the center a bright pale-yellow core bursts, with eight sharp teal spikes radiating out like a star; 3 the burst at full size, about 60% of the cell wide, violet glints between the spikes; 4 the spikes break into square shards flying outward; 5 the shards further out, the core gone; 6 the last shards fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the burst at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `ekko_fx_w_forming.png`：时光交错成形中（预警，1.5 秒），10 帧

球体要出现的地方：地面上浮现一圈时间符文，里面一圈虚线像时钟一样顺时针慢慢补满（画在人物下层）。圈约 80 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a teal light ramp (#A8FFE8, #5CEACB, #2CB89C, #1E7E6E) and a violet accent (#C8A0F8).
Effect: PARALLEL CONVERGENCE FORMING, a time anomaly about to appear, 10 frames. A flat ellipse on the ground, twice as wide as tall, filling the cell. 1 a dim outer ring, dashed; 2-3 ten small glowing rune glyphs (simple squares, triangles and hooks, 2 to 3 pixels each) appear one by one along the outer ring; 4-9 an inner dotted ring at 70% of the cell wide fills clockwise, one tenth more each frame, starting from the top, getting brighter; 10 both rings complete and bright, the runes flaring white.
Layout: one horizontal row of 10 equal cells, each 2 wide to 1 tall, image size 2560x128 (each cell 256x128); the ellipse's center at the same place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `ekko_fx_w_sphere.png`：时光交错的球体（持续中），4 帧无缝循环

成形后的时间球：地面上的符文环外罩一层半透明青绿色的半球光罩，符文慢慢绕圈（画在人物下层，人站在里面）。约 80 格宽、50 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C, #1E7E6E) and a violet accent (#C8A0F8, #8E62D8).
Effect: PARALLEL CONVERGENCE SPHERE, a dome of frozen time, 4 frames, a seamless loop. At the bottom of the cell a flat glowing ring on the ground (an ellipse twice as wide as tall, 95% of the cell wide) with ten small rune glyphs on it; over it a dome drawn only as its outline and a few curved highlight bands (the inside stays EMPTY, people stand in it), reaching 85% of the cell height; the runes move a little clockwise each frame and a highlight band slides over the dome; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each 8 wide to 5 tall, image size 1024x160 (each cell 256x160); the ground ring's center at the same place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `ekko_fx_w_shatter.png`：时光交错引爆，7 帧

艾克走进球里时引爆：光罩向内一缩，紫白色闪光，碎成玻璃一样的碎片向外飞。约 90 格宽、60 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C) and a violet ramp (#F0DCFF, #C8A0F8, #8E62D8, #5A3A9A).
Effect: PARALLEL CONVERGENCE DETONATION, a time dome shattering, 7 frames. 1 a teal dome outline over a ground ring, 80% of the cell wide, the dome pulled slightly inward; 2 it collapses into a bright violet-white flash at the middle; 3 the flash at full size, about 60% of the cell wide, a ring of light racing outward along the ground; 4 the dome shatters into fifteen angular glass-like shards (teal and violet) flying outward and up; 5 the shards further out, the ground ring breaking into arcs; 6 shards falling and fading; 7 a few sparks left.
Layout: one horizontal row of 7 equal cells, each 3 wide to 2 tall, image size 1792x170 (each cell 256x170); the ground ring's center at the same place in every cell (at 75% of the cell height), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `ekko_fx_w_stun.png`：被时间冻住（眩晕，跟着目标头顶），6 帧循环

眩晕的敌人头上：一个小小的青绿色表盘，指针飞快倒转，旁边绕着两个小方块。约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C) and a violet accent (#C8A0F8).
Effect: TIME-STOP STUN marker above a head, 6 frames, a seamless loop. A small flat clock face (a teal ring about 45% of the cell wide, drawn as an ellipse twice as wide as tall) with one bright white hand that turns BACKWARD (counter-clockwise) one sixth of a turn each frame; two tiny teal squares orbit around the clock on the same flat ellipse, one violet glint.
Layout: one horizontal row of 6 equal cells, each 4 wide to 3 tall, image size 1536x192 (each cell 256x192); the clock at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `ekko_fx_w_shield.png`：时光交错的护盾（跟着艾克），4 帧无缝循环

引爆后艾克身上的护盾：一层青绿色的六边形格子光罩包住他，边缘有细小的电弧跳动。**不能挡住他的身体和脸**。人形空位约 34 格高、36 格宽（他低蹲、比较宽）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C).
Effect: TIME SHIELD around a crouching boy, 4 frames, a seamless loop. In the middle of every cell there is an EMPTY space the size of a crouching boy (70% of the cell height, 80% of the cell wide, feet at 88% of the cell height) - never draw the boy and never draw over that space. Around it: the outline of a rounded bubble made of a thin teal hexagon grid (only the bubble's edge and a few hexagon lines near the edge are drawn), and two or three tiny white electric sparks jumping along the edge, at different places each frame.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `ekko_fx_r_depart.png`：时空断裂的消失（离开的地方），6 帧

艾克回溯时离开的位置：一个薄荷色人影一闪，被一圈倒转的时钟光环吸进去，化成往上飘的小方块。约 34 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a mint hologram ramp (#D8FFF0, #9CE8D0, #5CC4AC, #3A8C7E) and a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB).
Effect: CHRONOBREAK VANISH, a boy rewinding out of the present, 6 frames. 1 a flat mint silhouette of a crouching boy with a spiky mohawk, facing right, 60% of the cell tall, a thin teal ring around its waist; 2 the ring spins and shrinks, the silhouette flickering with horizontal scan lines; 3 the silhouette squeezes toward its middle into a tall bright column; 4 the column pops into a white flash and twelve small mint squares; 5 the squares drift upward and fade; 6 three last squares.
Layout: one horizontal row of 6 equal cells, each 4 wide to 5 tall, image size 1536x320 (each cell 256x320); the feet at 88% of the cell height, centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `ekko_fx_r_arrive.png`：时空断裂落地（大爆炸），8 帧

艾克回到锚点的那一刻：地面上炸开一个带三个三角刻度的青绿色时钟圆盘，一道白光和往上的光束，冲击环向外扩开（画在人物下层，艾克站在中间）。圈最大约 70 格宽、35 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C, #1E7E6E) and a violet accent (#C8A0F8, #8E62D8).
Effect: CHRONOBREAK ARRIVAL BLAST on the ground, 8 frames. A flat ellipse, twice as wide as tall, centered at 60% of the cell height; the middle of it stays EMPTY (the boy stands there). 1 a blinding white flash on the ground at the center; 2 a teal clock ring snaps open to 50% of the cell wide with three bright triangle markers on it (like a clock face), short vertical light beams rising from the ring; 3 the clock ring at 75%, a thin second shockwave ring racing ahead of it; 4 the shockwave ring at its widest, about 95% of the cell wide, the clock ring glowing; 5 the shockwave fades, violet sparks along it; 6 the clock ring turns a little and dims; 7 the ring breaks into arcs; 8 the last arcs fading.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 2048x128 (each cell 256x128); the ellipse's center at the same place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `ekko_fx_r_hit.png`：时空断裂打中的敌人（跟着目标），5 帧

大招爆炸波及的每个敌人身上：一团青绿色的冲击，里面闪一下紫白色。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a teal light ramp (#F2FFFB, #A8FFE8, #5CEACB, #2CB89C) and a violet accent (#F0DCFF, #C8A0F8).
Effect: CHRONOBREAK HIT on an enemy, 5 frames: 1 a violet-white spark at the center; 2 a round teal burst about 40% of the cell wide with six short rays; 3 the burst at 60% of the cell wide, its middle hollow, square shards flying out; 4 the shards further out, the ring thinning; 5 the last shards fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the hit at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，头部从 `native/ekko_native.png` 贴在肩上，帧时长写在 `native/ekko_cells.json`。特效由 `tools/art/import_ekko.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）；大招的全息残影 `r_ghost` 由它从待机帧生成。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `ekko_fx_hit.png` | 5 | 特效 `league_ekko_hit`（普攻命中）；Q 命中 `league_ekko_q_hit` 共用 | 5 × 50 |
| `ekko_fx_z_proc.png` | 6 | 特效 `league_ekko_z_proc`（共振触发，跟随目标） | 6 × 50 |
| `ekko_fx_q_device.png` | 4 | 投射物 `league_ekko_q_out` / `league_ekko_q_back`（朝飞行方向转） | 4 × 60 循环 |
| `ekko_fx_q_field.png` | 6 | 特效 `league_ekko_q_field`（装置尽头，半径 22000，地面，0.75 秒） | 6 × 125 |
| `ekko_fx_e_dash.png` | 5 | 特效 `league_ekko_e_dash`（冲刺起点，艾克身上放，不跟随） | 5 × 60 |
| `ekko_fx_e_hit.png` | 6 | 特效 `league_ekko_e_hit`（闪击命中） | 6 × 50 |
| `ekko_fx_w_forming.png` | 10 | 抛物线落点预警 `league_ekko_w_forming`（半径 40000，地面，1.5 秒） | 10 × 150 |
| `ekko_fx_w_sphere.png` | 4 | 特效 `league_ekko_w_sphere`（每 15 帧播一次，一段 0.25 秒，地面） | 4 × 62 |
| `ekko_fx_w_shatter.png` | 7 | 特效 `league_ekko_w_shatter`（引爆，球心） | 7 × 60 |
| `ekko_fx_w_stun.png` | 6 | 特效 `league_ekko_w_stun`（眩晕 1 秒，跟随目标头顶） | 6 × 83 循环两遍 |
| `ekko_fx_w_shield.png` | 4 | 增益 `league_ekko_w_shield`（护盾在时一直循环） | 4 × 100 循环 |
| `ekko_fx_r_depart.png` | 6 | 特效 `league_ekko_r_depart`（离开的位置，不跟随） | 6 × 60 |
| `ekko_fx_r_arrive.png` | 8 | 特效 `league_ekko_r_arrive`（落点，半径 35000，地面） | 8 × 70 |
| `ekko_fx_r_hit.png` | 5 | 特效 `league_ekko_r_hit`（跟随目标） | 5 × 60 |

特效表：`league_ekko_fx`（hit、q_hit、z_proc、q_device、e_dash、e_hit、w_stun、w_shield、r_hit），`league_ekko_big`（q_field、w_forming、w_sphere、w_shatter、r_ghost、r_depart、r_arrive）。
