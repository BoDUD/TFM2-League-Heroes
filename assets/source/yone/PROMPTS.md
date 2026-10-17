# 封魔剑魂 永恩：给 Codex 的特效提示词

> **这一轮只画 16 张特效图。**
> - 角色不用画：永恩的模型由 Claude 做。头部（红色 V 字恶魔面具、两根红角、面具下两只发紫光的眼睛、黑色长发，用户选了方案 A）是逐格画的，每一帧贴在头部的位置；身体用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）。灵魂出窍时原地留下的身体也由 Claude 从动画里做。
> - 定稿造型图 `native/yone_native.png` 只用来参考配色和人物大小（连角约 41 格高、身体约 20 格宽），不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里永恩自己的特效贴图（Q 的青白色风、恶魔刀的红色、E 的蓝紫色火焰和墨迹、R 的红白斩痕），只在本地用，不要提交。
> - 特效照下面第 1–16 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_yone.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「狩人之道」 | 钢刀和恶魔刀轮流砍：第一刀钢刀（物理），第二刀恶魔刀（一部分真实伤害）；暴击几率 20% | `yone_fx_hit` · `yone_fx_hit2` |
| 技能 1 = Q「错玉切」 | 向前突刺；命中两次后身上起风，下一次向前冲刺，带着旋风击飞路径上的敌人 | `yone_fx_q_thrust` · `yone_fx_q_hit` · `yone_fx_q_ready` · `yone_fx_q3_wave` · `yone_fx_knockup` |
| 技能 2 = W「凛神斩」+ E「破障之锋」 | 向前扇形顺劈，每命中一名英雄获得一层护盾；每 15 秒先灵魂出窍：身体留在原地，灵体冲向英雄，4 秒后被拉回身体，期间命中的敌人被标记，拉回时标记引爆 | `yone_fx_w_cone` · `yone_fx_w_hit` · `yone_fx_shield` · `yone_fx_e_cast` · `yone_fx_spirit` · `yone_fx_e_mark` · `yone_fx_e_pop` · `yone_fx_e_return` |
| 大招 = R「封尘绝念斩」 | 蓄力后沿一条直线斩出，线上所有敌人被击飞，永恩出现在目标身后 | `yone_fx_r_line` · `yone_fx_r_slash` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（三套，别混用）：
  - 风（Q、Q3、击飞，青白）：`#FFFFFF`、`#D8F4F4`、`#8EDCE0`、`#4AA8B8`、`#2A6E80`；
  - 恶魔刀（第二刀、W、R，红）：`#FFE6EE`、`#FF7A9A`、`#E02844`、`#A8162E`、`#5A0E22`；
  - 灵魂（E、标记、护盾的光，蓝紫）：`#F0EAFF`、`#B8A8FF`、`#7C62E8`、`#4A36A8`、`#1E1648`；
  - 钢刀的斩光（普攻第一刀，银白）：`#FFFFFF`、`#E4F0F0`、`#A8C8CC`、`#6E9296`。
- **飞行类和直线类特效一律朝右画，而且上下对称**：游戏会把它转到施放方向，向左时整张图转 180°。
- 命中、爆开、标记居中画，不旋转。
- 套在永恩身上的特效（护盾、起风、灵体光）：格子中间留出一个空的人形位置（按每条写的比例，他又高又瘦，头上有两根角），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `yone_fx_hit.png`：普攻第一刀（钢刀）命中，5 帧

钢刀斩中目标：一道银白色的弧形刀光斜着划过，带几点火星。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a silver-white ramp (#FFFFFF, #E4F0F0, #A8C8CC, #6E9296).
Effect: a KATANA SLASH IMPACT, 5 frames: 1 a thin bright white line appears diagonally across the center (from upper left to lower right); 2 it widens into a crescent slash about 50% of the cell wide, silver edges, white core, with three small white sparks flying off; 3 the crescent at full size, the sparks further out; 4 the crescent thins and breaks into short silver dashes; 5 two faint dashes fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the slash centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `yone_fx_hit2.png`：普攻第二刀（恶魔刀）命中，6 帧

恶魔刀斩中目标：一道比钢刀更粗的红色弧形刀光，边上带红色碎屑，刀光中心发白。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a demon red ramp (#FFE6EE, #FF7A9A, #E02844, #A8162E, #5A0E22).
Effect: a DEMON BLADE SLASH IMPACT, 6 frames: 1 a thin white-pink line appears diagonally across the center (from lower left to upper right); 2 it bursts into a thick crimson crescent slash about 55% of the cell wide with a white-hot core; 3 the crescent at full size, small dark red shards flying off its edges; 4 the crescent darkens to deep red and starts to split; 5 red fragments drifting apart; 6 the last maroon specks fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the slash centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `yone_fx_q_thrust.png`：错玉切突刺（直线），5 帧

向前一刺带出一道青白色的风刃：一根细长的风之矛从左往右刺出去，前端尖。约 45 格长、12 格高（技能的判定是 45000 × 12000 的长条）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #D8F4F4, #8EDCE0, #4AA8B8, #2A6E80).
Effect: MORTAL STEEL THRUST, a spear of wind thrust to the RIGHT, 5 frames, SYMMETRIC above and below the middle line: 1 a short bright streak at the left end of the cell; 2 the streak shoots right as a long thin lance of white wind with a sharp pointed tip, reaching 70% of the cell width, cyan edges, two thin wind streaks alongside it; 3 the lance at full length, 95% of the cell width, the tip bright white; 4 the lance breaks up into long cyan streaks from the left; 5 thin streaks fading at the right end.
Layout: one horizontal row of 5 equal cells, each 4 wide to 1 tall, image size 2560x128 (each cell 512x128); the lance on the middle line of every cell, starting at the cell's left edge, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `yone_fx_q_hit.png`：错玉切命中，5 帧

突刺刺中目标：一个青白色的刺击星芒，横向拉长，带几道短风纹。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #D8F4F4, #8EDCE0, #4AA8B8).
Effect: a PIERCING WIND IMPACT, 5 frames: 1 a small white point at the center; 2 a four-pointed star flash, stretched horizontally (the horizontal points twice as long as the vertical ones), about 45% of the cell wide; 3 the star at full size with a ring of short cyan wind streaks around it; 4 the star shrinks, the streaks spin outward; 5 faint cyan streaks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `yone_fx_q_ready.png`：风暴聚集（第三段就绪，跟着永恩），6 帧，无缝循环

Q 叠满两层后身上起风，表示下一次 Q 会冲刺击飞：一圈青白色的风在他腰部和刀边打转。**不能挡住他的身体和脸**。人形空位约 41 格高、20 格宽（瘦高，头上两根角）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a wind ramp (#FFFFFF, #D8F4F4, #8EDCE0, #4AA8B8).
Effect: GATHERING STORM, wind swirling around a slim swordsman, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY space the size of a tall slim warrior (80% of the cell height, 35% of the cell wide, feet at 90% of the cell height) - never draw the warrior and never draw over that space. Around its waist and lower body: two or three thin curved wind streaks (1-2 pixels wide) circling on a flat ellipse, the front ones bright white, the back ones cyan, turning a sixth of a circle each frame; a few small white wisps rising; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `yone_fx_q3_wave.png`：错玉切第三段（冲刺的旋风，跟着永恩飞），4 帧循环

冲刺时身前带着一股横着翻滚的旋风，把路上的人卷起来。约 30 格长、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #D8F4F4, #8EDCE0, #4AA8B8, #2A6E80).
Effect: a GUST OF WIND rushing to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line. A rolling wave of wind shaped like a sideways cone opening to the right: its leading edge at the right is a bright white curved front about 90% of the cell height, behind it three or four layered cyan wind streaks tapering to the left, curling like a breaking wave; small white wisps spin off the edges; each frame the curls turn a little.
Layout: one horizontal row of 4 equal cells, each 5 wide to 4 tall, image size 1280x256 (each cell 320x256); the wave's front at 85% of the cell width, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `yone_fx_knockup.png`：击飞（Q3 和 R，跟着目标），6 帧

被卷上天的敌人脚下一股往上冲的小旋风。约 20 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a wind ramp (#FFFFFF, #D8F4F4, #8EDCE0, #4AA8B8).
Effect: KNOCK-UP WHIRLWIND under an enemy, 6 frames: 1 a flat ring of wind on the ground at the bottom middle of the cell; 2 a narrow whirlwind spirals up from it to half of the cell height; 3 the whirlwind at full height, 85% of the cell height and 50% of the cell wide, white streaks spiraling up, cyan at the edges; 4 the top of the whirlwind frays outward; 5 loose wind streaks rising and fading; 6 the last wisps at the top.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1152x256 (each cell 192x256); the base at the bottom middle of every cell (ground line at 92% of the cell height), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `yone_fx_w_cone.png`：凛神斩（扇形顺劈），6 帧

恶魔刀向前一扫：一道红色的大弧形刀光从左边的尖端向右扇开，像一把张开的扇子（扇形约 100°）。约 45 格长、40 格宽，尖端在格子左边正中。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a demon red ramp (#FFE6EE, #FF7A9A, #E02844, #A8162E, #5A0E22).
Effect: SPIRIT CLEAVE, a wide sweeping blade arc opening to the RIGHT, 6 frames, SYMMETRIC above and below the middle line: 1 a thin bright line at the upper part of the fan (the blade starts high); 2 a thick crimson crescent sweeps down across the fan, from its apex at the LEFT EDGE MIDDLE of the cell out to its curved rim at the right, white-hot along the rim; 3 the crescent covers the whole fan (about 100 degrees wide), the rim bright pink-white, streaks of red trailing inside toward the apex; 4 the arc darkens to deep red and breaks into curved streaks; 5 red streaks and small shards drifting outward; 6 the last maroon specks fading near the rim.
Layout: one horizontal row of 6 equal cells, each 9 wide to 8 tall, image size 1728x256 (each cell 288x256); the fan's apex at the left edge middle of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `yone_fx_w_hit.png`：凛神斩命中，5 帧

被扫中的敌人身上一个红色的交叉斩痕。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a demon red ramp (#FFE6EE, #FF7A9A, #E02844, #A8162E).
Effect: a CROSS CUT on an enemy, 5 frames: 1 one bright slash line from upper left to lower right through the center; 2 a second slash crosses it from lower left to upper right, both crimson with white cores, about 50% of the cell wide; 3 the X at full size with small red sparks; 4 the X darkens and the lines break into dashes; 5 faint red dashes fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the X centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `yone_fx_shield.png`：凛神斩护盾（跟着永恩），6 帧

W 命中后身上的护盾：一层淡蓝紫色的灵光贴着身体轮廓外面流动，前后两道弧。**不能挡住他的身体和脸**。人形空位同第 5 条。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a spirit ramp (#F0EAFF, #B8A8FF, #7C62E8, #4A36A8).
Effect: SPIRIT SHIELD around a slim swordsman, 6 frames. In the middle of every cell there is an EMPTY space the size of a tall slim warrior (80% of the cell height, 35% of the cell wide, feet at 90% of the cell height) - never draw the warrior. 1 a thin lavender outline flickers on around the empty space; 2 it becomes a glowing shell 1-2 pixels thick hugging the outside of the space, brighter at the top and at the shoulders; 3 a bright white glint runs down the shell; 4 the shell steady with a few small lavender motes floating off; 5 the shell dims to violet; 6 the shell fading into scattered violet specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `yone_fx_e_cast.png`：破障之锋灵魂出窍（在永恩出发的地方），6 帧

灵体离开身体的一瞬：一团蓝紫色的灵火往上炸开，带墨色的烟。也用在他被拉回之前消失的地方。约 28 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit ramp (#F0EAFF, #B8A8FF, #7C62E8, #4A36A8, #1E1648).
Effect: SOUL UNBOUND, a spirit bursting out of a body, 6 frames: 1 a bright white-violet flash at the middle of the cell; 2 blue-violet ghost flames burst up and out from it, taller than wide, about 60% of the cell height; 3 the flames at full size with dark ink-like wisps (#1E1648) curling at their edges; 4 the flames rise and thin out, the ink wisps drifting; 5 a few violet flames and ink curls high in the cell; 6 the last violet specks fading.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1152x256 (each cell 192x256); the burst centered horizontally, its base at 80% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `yone_fx_spirit.png`：灵体形态（跟着永恩，4 秒），6 帧，无缝循环

灵魂出窍的 4 秒里：他身上一直缭绕着一层蓝紫色的灵火，从脚下往上飘，表示现在是灵体。**不能挡住他的身体和脸**。人形空位同第 5 条。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a spirit ramp (#F0EAFF, #B8A8FF, #7C62E8, #4A36A8).
Effect: SPIRIT FORM aura around a slim swordsman, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY space the size of a tall slim warrior (80% of the cell height, 35% of the cell wide, feet at 90% of the cell height) - never draw the warrior. Small blue-violet ghost flames (3 to 6 pixels tall) flicker along the outside edges of the space from the feet up to the shoulders, a few more at the feet, their tips drifting upward and fading, white-violet at the bottoms; a thin lavender ring on the ground under the space; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `yone_fx_e_mark.png`：灵魂印记（跟着目标），6 帧

灵体期间被打中的敌人身上出现一个印记：两笔交叉的蓝紫色墨迹刀痕（像英雄联盟里永恩 E 的印记，参考 `lol_fx_ref.png` 的 E_Mark），闪一下后留着。约 12 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit ramp (#F0EAFF, #B8A8FF, #7C62E8, #4A36A8, #1E1648).
Effect: SOUL MARK on an enemy, 6 frames: 1 a small violet flash at the center; 2 an ink brush sigil appears - two crossed blade-like brush strokes forming an X, one stroke longer and sweeping, dark ink edges with a glowing violet core, about 45% of the cell wide; 3 the sigil glows brighter; 4 the sigil steady, two small violet motes circling it; 5 the same, the motes on the other side; 6 the sigil dims a little.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the sigil centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `yone_fx_e_pop.png`：印记引爆（跟着目标），6 帧

永恩被拉回身体时，被标记的敌人身上的印记炸开：一道蓝紫色的斩痕从印记里切出来，碎成墨色的碎片。约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit ramp (#F0EAFF, #B8A8FF, #7C62E8, #4A36A8, #1E1648).
Effect: SOUL MARK BURST, 6 frames: 1 the X-shaped violet brush sigil at the center flashes white; 2 a sharp white-violet slash cuts through it horizontally, about 70% of the cell wide; 3 a second slash cuts diagonally, the sigil shatters into violet shards and dark ink splashes; 4 the shards fly outward, the ink splashes spread; 5 ink drops falling, violet specks fading; 6 the last ink specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `yone_fx_e_return.png`：拉回身体（在身体的地方），6 帧

灵体被拉回身体的一瞬：蓝紫色的灵火往里一收，身体周围一圈灵光闪开。约 30 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a spirit ramp (#F0EAFF, #B8A8FF, #7C62E8, #4A36A8, #1E1648).
Effect: SPIRIT RETURNS to its body, 6 frames: 1 streaks of violet light converge from both sides toward the middle of the cell; 2 they meet in a tall white-violet flash, 60% of the cell height, narrow; 3 the flash bursts into a flat ring of lavender light on the ground (an ellipse twice as wide as tall at 85% of the cell height) and a pillar of violet sparks; 4 the ring widens to 90% of the cell width, the pillar fading; 5 the ring thins into violet specks; 6 the last specks.
Layout: one horizontal row of 6 equal cells, each 5 wide to 6 tall, image size 1440x288 (each cell 240x288); the flash centered horizontally, the ground ellipse at 85% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 16. `yone_fx_r_line.png`：封尘绝念斩（直线斩），8 帧

大招：先在地上画出一道细长的红线（蓄力约 0.25 秒），然后整条线炸成一道巨大的红白斩痕。约 90 格长、20 格宽（判定是 90000 × 20000 的长条），从格子左边往右画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a demon red ramp (#FFE6EE, #FF7A9A, #E02844, #A8162E, #5A0E22) and white.
Effect: FATE SEALED, a long straight slash to the RIGHT, 8 frames, SYMMETRIC above and below the middle line: 1 a thin dark red line appears along the middle of the cell from the left edge to the right edge (a telegraph); 2 the line glows brighter crimson; 3 it pulses pink, a few red sparks along it; 4 the whole line explodes into a huge white-hot slash, as tall as 40% of the cell height in the middle, tapering to sharp points at both ends, crimson edges; 5 the slash at full size with red shards and wind flying off both sides; 6 the slash splits along its length into two red streaks; 7 the streaks fade to deep red, shards drifting; 8 faint maroon specks along the line.
Layout: one horizontal row of 8 equal cells, each 9 wide to 2 tall, image size 4608x128 (each cell 576x128); the line on the middle row of every cell from its left edge to its right edge, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，头部从 `native/yone_native.png` 贴在头部关节的位置，帧时长写在 `native/yone_cells.json`。灵魂出窍时留在原地的身体（`e_body`）也来自动画（League 的 `Spell3_bodyLoop`）。特效由 `tools/art/import_yone.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `yone_fx_hit.png` | 5 | 特效 `league_yone_hit`（钢刀命中） | 5 × 50 |
| `yone_fx_hit2.png` | 6 | 特效 `league_yone_hit2`（恶魔刀命中） | 6 × 50 |
| `yone_fx_q_thrust.png` | 5 | 直线 `league_yone_q_thrust`（45000 × 12000，朝施放方向转） | 5 × 40 |
| `yone_fx_q_hit.png` | 5 | 特效 `league_yone_q_hit`（跟随目标） | 5 × 50 |
| `yone_fx_q_ready.png` | 6 | 增益 `league_yone_q_ready`（风暴聚集时一直循环） | 6 × 80 循环 |
| `yone_fx_q3_wave.png` | 4 | 投射物 `league_yone_q3_wave`（跟着冲刺，朝飞行方向转） | 4 × 60 循环 |
| `yone_fx_knockup.png` | 6 | 特效 `league_yone_knockup`（跟随目标，击飞约 1 秒） | 6 × 80 |
| `yone_fx_w_cone.png` | 6 | 直线 `league_yone_w_cone`（扇形画面，尖端在永恩，朝施放方向转） | 6 × 40 |
| `yone_fx_w_hit.png` | 5 | 特效 `league_yone_w_hit`、`league_yone_r_slash`（跟随目标） | 5 × 50 |
| `yone_fx_shield.png` | 6 | 特效 `league_yone_shield`（跟随永恩，护盾 1.5 秒） | 6 × 250 |
| `yone_fx_e_cast.png` | 6 | 特效 `league_yone_e_cast`、`league_yone_e_leave`（出窍和拉回前的原地） | 6 × 60 |
| `yone_fx_spirit.png` | 6 | 增益 `league_yone_spirit`（灵体形态 4 秒循环） | 6 × 100 循环 |
| `yone_fx_e_mark.png` | 6 | 特效 `league_yone_e_mark`（跟随目标） | 6 × 80 |
| `yone_fx_e_pop.png` | 6 | 特效 `league_yone_e_pop`（跟随目标） | 6 × 60 |
| `yone_fx_e_return.png` | 6 | 特效 `league_yone_e_return`（拉回到身体） | 6 × 60 |
| `yone_fx_r_line.png` | 8 | 直线 `league_yone_r_line`（90000 × 20000，朝目标转） | 8 × 60 |

特效表：`league_yone_fx`（hit、hit2、q_hit、q_ready、knockup、w_hit、shield、e_cast、spirit、e_mark、e_pop、e_return），`league_yone_big`（q_thrust、q3_wave、w_cone、r_line）。R 线上每个敌人身上的斩痕（`league_yone_r_slash`）用 w_hit 那一条；灵魂出窍时留在原地的身体（`league_yone_e_body`）是角色图里的 `e_body` 动作。
