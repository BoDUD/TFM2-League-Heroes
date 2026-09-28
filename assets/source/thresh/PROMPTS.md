# 魂锁典狱长 锤石：给 Codex 的特效提示词

> **这一轮只画 14 张特效图。**
> - 角色不用画：锤石的模型由 Claude 做（英雄联盟原版动画重新上色，头部就是原版模型投票出来的暗色骷髅、两点绿光眼睛和向后甩的锁链尖刺，用户选定）。
> - 定稿造型图 `native/thresh_native.png` 只用来参考配色和人物大小（连头顶尖刺约 36 格高、身体约 38 格宽，左手镰刀、右手灯笼），不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里锤石自己的特效贴图（多为灰度遮罩：钩子头的光团、锁链、骨柱 `Thresh_BonePost`、灵魂滴 `soul_drops`、烟雾），只在本地用，不要提交。游戏里这些遮罩被染成灵魂绿。
> - 特效照下面第 1–14 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_thresh.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「厄运钟摆」「地狱诅咒」 | 甩出锁链镰刀打人；超过 2 秒没普攻时，下一次普攻附带魔法伤害（绿火更大） | `thresh_fx_lash` · `thresh_fx_lash_flay` · `thresh_fx_hit` · `thresh_fx_flay_hit` |
| 技能 1 = Q「死亡判决」+ W「魂引之灯」 | 掷出镰刀钩住第一个敌方英雄，眩晕并拉到锤石身前，镰刀连着锁链收回；每 14 秒同时甩出灯笼，给自己和身边一名队友加护盾 | `thresh_fx_q_hook` · `thresh_fx_q_return` · `thresh_fx_q_hit` · `thresh_fx_w_lantern` · `thresh_fx_w_shield` |
| 技能 2 = E「厄运钟摆」 | 锁链从身后横扫到身前，把周围的敌人拉向并越过锤石，减速 | `thresh_fx_e_sweep` · `thresh_fx_e_hit` |
| 大招 = R「幽冥监牢」 | 在脚下立起一圈五面灵魂墙，5 秒；碰到墙的敌方英雄受伤并几乎定住（减速 99%） | `thresh_fx_r_box` · `thresh_fx_r_hit` · `thresh_fx_r_slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（三套，别混用）：
  - 灵魂绿（钩子、锁链的光、钟摆、监牢、命中）：`#FFFFFF`、`#D8FFE8`、`#7CF5B0`、`#2FD47A`、`#148C4E`、`#0A4A2C`；
  - 灯笼黄绿（灯笼和护盾）：`#FFFFFF`、`#F4FFC0`、`#C8F060`、`#8CC83A`、`#4C8A2A`；
  - 锁链和镰刀柄的金属（暗紫灰，少量）：`#C8B8B8`、`#8A7470`、`#4E3C3E`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、爆开、标记居中画，不旋转。
- 套在人身上的特效（护盾、减速锁链）：格子中间留出一个空的人形位置（按每条写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `thresh_fx_lash.png`：普攻（飞向目标的锁链镰刀头），4 帧，循环

普攻甩出去打人的东西：一个小的发绿光的镰刀头，后面拖一小段锁链。朝右飞。约 16 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E) and a little dark metal (#8A7470, #4E3C3E).
Effect: a small spectral SICKLE HEAD flying to the RIGHT with a short chain behind it, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right a curved green blade glowing white at its edge (about 30% of the cell width), behind it to the left three small chain links (dark metal with a green glow) and a thin green trail fading toward the left edge; each frame the glow on the blade flickers and the trail shifts a little.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256 wide, 128 tall); the blade's tip at 90% of the cell width, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `thresh_fx_lash_flay.png`：蓄满「厄运钟摆」的普攻，4 帧，循环

同第 1 条，但更大更亮：镰刀头裹着一团绿色的灵魂火，后面拖着更长的绿火尾巴。约 22 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E, #0A4A2C) and a little dark metal (#8A7470, #4E3C3E).
Effect: an EMPOWERED spectral SICKLE HEAD flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: the curved green blade at the right wrapped in green soul fire with a white-hot edge, behind it a chain of four links and a long flickering green flame trail tapering to the left edge; small green soul sparks flying off; each frame the flames flicker.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256 wide, 128 tall); the blade's tip at 90% of the cell width, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `thresh_fx_hit.png`：普攻命中，5 帧

镰刀划中目标：一道绿色的弧形划痕，带几点灵魂火星。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E).
Effect: a SICKLE SLASH IMPACT, 5 frames: 1 a thin bright line appears diagonally across the center (from upper right to lower left, a hooked curve); 2 it widens into a green crescent slash about 50% of the cell wide with a white core, two small green sparks flying off; 3 the crescent at full size, sparks further out; 4 the crescent thins and breaks into short green dashes; 5 two faint dashes fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the slash centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `thresh_fx_flay_hit.png`：蓄满的普攻命中，6 帧

比第 3 条大：划痕炸开成一团绿色的灵魂火，几缕灵魂烟往上飘。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E, #0A4A2C).
Effect: an EMPOWERED SICKLE IMPACT, 6 frames: 1 a bright white hooked slash line across the center; 2 it bursts into a large green crescent with a white-hot core and a ring of green soul fire; 3 the burst at full size (about 70% of the cell), green flames licking outward, small soul wisps (little round green lights with tails) rising; 4 the flames break up; 5 green wisps drifting up and fading; 6 the last faint wisps.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `thresh_fx_q_hook.png`：死亡判决（飞出去的镰刀和锁链），4 帧，循环

钩子朝右飞：最前面是一把大的发绿光的镰刀刃（刃口朝前弯），后面拖着一长串锁链一直到格子左边，锁链节之间透着绿光。约 48 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E) and dark metal for the chain (#C8B8B8, #8A7470, #4E3C3E).
Effect: DEATH SENTENCE, a thrown scythe on a chain flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right end a large curved scythe blade (about 25% of the cell width, 80% of the cell height), its sharp edge bright white-green, the blade glowing green; from the blade back to the LEFT EDGE of the cell a straight chain of small oval links (dark metal) with a thin green glow line running along it; faint green sparks along the chain; each frame the glow runs along the links toward the blade.
Layout: one horizontal row of 4 equal cells, each 4 wide to 1 tall, image size 2048x128 (each cell 512 wide, 128 tall); the blade's tip at 95% of the cell width, the chain reaching the left edge, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `thresh_fx_q_return.png`：收回的钩子，4 帧，循环

钩子被拉回锤石身边（这张图朝右飞 = 朝锤石飞）：**锁链在前（右边），镰刀刃在最后面（左端），刃口朝后钩着**，像是刃挂在被拉的敌人身上。约 40 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E) and dark metal for the chain (#C8B8B8, #8A7470, #4E3C3E).
Effect: the scythe being PULLED BACK, moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: the chain leads - a straight chain of small oval links with a green glow from the RIGHT EDGE of the cell toward the left; at the LEFT END the scythe blade trails behind, its curved hook pointing backward (to the left), glowing green; green motion streaks along the chain pointing right; each frame the glow runs along the links to the right.
Layout: one horizontal row of 4 equal cells, each 4 wide to 1 tall, image size 2048x128 (each cell 512 wide, 128 tall); the chain reaching the right edge, the blade at the left end, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `thresh_fx_q_hit.png`：钩中目标（跟着目标，眩晕 1 秒），8 帧

镰刀钩进敌人身上：先一下绿色的闪光，然后几圈绿光锁链缠在目标身上（腰部一圈、斜着一圈），一直亮着，最后散掉。**不能挡住目标的脸**。人形空位约 36 格高、20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E) and dark metal chain links (#8A7470, #4E3C3E).
Effect: HOOKED AND BOUND, 8 frames, around an EMPTY space the size of a small chibi hero in the middle of every cell (80% of the cell height, 45% of the cell wide, feet at 90% of the cell height) - never draw the hero and never draw over its head: 1 a bright green flash burst at the hero's chest height; 2 the flash fades, two spectral chains appear, one wrapping around the waist on a flat ellipse, one crossing diagonally from shoulder to hip; 3 to 6 the chains glow, green light running along the links, a few green soul sparks; 7 the chains start to break into glowing fragments; 8 the last fragments fading.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `thresh_fx_w_lantern.png`：魂引之灯（飞向队友的灯笼），4 帧，循环

锤石甩出去的灯笼：一盏方形的笼子灯，尖顶，四面窗里亮着黄绿色的灵魂火，飞的时候轻轻转，后面拖一道黄绿色的光尾。约 14 格宽（含光尾 24 格）、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, lantern metal (#8A7470, #4E3C3E, #C8B8B8) and a lantern yellow-green glow (#FFFFFF, #F4FFC0, #C8F060, #8CC83A, #4C8A2A).
Effect: THRESH'S LANTERN flying to the RIGHT, 4 frames, a seamless loop: at the right half a square cage lantern with a pointed roof and a ring on top, its windows glowing bright yellow-green, a soft yellow-green halo of hard-edged pixels around it; behind it to the left a short trail of yellow-green light and three small glowing motes; each frame the lantern tilts a little (a gentle swing) and the flame inside flickers.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256 wide, 128 tall); the lantern centered at 70% of the cell width, on the middle line, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `thresh_fx_w_shield.png`：灯笼的护盾（跟着被保护的人），6 帧，无缝循环

被魂引之灯保护时身上的护盾：一层黄绿色的半透明灵光罩着全身（用硬边像素和少量亮点画出罩子的边），罩子上缓缓飘着几个灵魂光点。**不能挡住人的身体和脸**（罩子只画边缘和少量亮点）。人形空位约 36 格高、24 格宽（锤石本人更宽，也要装得下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a lantern yellow-green glow (#FFFFFF, #F4FFC0, #C8F060, #8CC83A, #4C8A2A).
Effect: LANTERN SHIELD around a hero, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY space the size of a chibi hero (75% of the cell height, 50% of the cell wide, feet at 90% of the cell height) - never draw the hero. Around it: the outline of a tall rounded bubble drawn as a thin broken line of yellow-green pixels (brighter on top and on the front), a flat glowing ellipse on the ground under the feet, and four or five small yellow-green soul motes slowly circling the bubble; the bubble's rim shimmers (a bright segment running around it); frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `thresh_fx_e_sweep.png`：厄运钟摆（绕着锤石横扫的锁链弧），7 帧

锁链从锤石身后甩到身前：一道很宽的绿色弧光贴着地面从左后方扫过身前到右边，弧的前端是镰刀刃的亮光，后面拖着锁链的残影。中间留锤石站的位置。整体约 70 格宽、30 格高（地面上的扁圆），**这张不会被旋转，锤石朝左时会左右翻转**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E, #0A4A2C) and dark metal chain links (#8A7470, #4E3C3E).
Effect: FLAY, a chain swept around the hero along the ground, 7 frames. In the middle of every cell stands an EMPTY space for the hero (60% of the cell height, 25% of the cell wide, feet at 75% of the cell height) - never draw the hero. The sweep follows a wide flat ellipse on the ground centered on the hero's feet (90% of the cell width, 45% of the cell height): 1 a bright green scythe glint at the far left of the ellipse behind the hero; 2 the glint swings forward along the lower (front) half of the ellipse, a green arc of light and chain links trailing behind it; 3 the head of the arc passes in front of the hero's feet, the trail covering the left half; 4 the head reaches the right end of the ellipse, the whole lower half of the ellipse lit as a wide green crescent with a white-hot leading edge; 5 the crescent fades from the left, green sparks thrown outward; 6 only the right end still glowing; 7 faint green sparks fading.
Layout: one horizontal row of 7 equal cells, each 7 wide to 4 tall, image size 3136x256 (each cell 448 wide, 256 tall); the hero's feet at the center of every cell's ellipse, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `thresh_fx_e_hit.png`：被钟摆扫中（跟着目标），5 帧

被扫中的敌人身上一道横着的绿色锁链抽痕，带灵魂火星。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E) and dark metal (#8A7470).
Effect: a CHAIN LASH IMPACT, 5 frames: 1 a horizontal white line across the center; 2 it thickens into a green whip streak with a few chain links visible in it, about 60% of the cell wide; 3 the streak at full size, small green sparks bursting up and down; 4 the streak breaks into short green dashes drifting sideways; 5 faint dashes fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the lash centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `thresh_fx_r_box.png`：幽冥监牢（地上的五面灵魂墙，5 秒），10 帧

大招：以锤石脚下为中心的一个五边形监牢（从上方斜看是一个扁的五边形，约 80 格宽、40 格深）。五个角上各立一根骨柱（参考 `lol_fx_ref.png` 的 `Thresh_BonePost`：一节一节的脊椎骨，青绿色），相邻骨柱之间是一面半透明的绿色灵魂墙（竖着的光幕，约 14 格高，上沿亮、下沿淡，墙面里有竖向流动的光纹）。第 1–3 帧：骨柱从地里冒出、墙从地面升起；第 4–7 帧：墙立着，光纹往上流（这 4 帧会反复播放约 4 秒）；第 8–10 帧：墙碎成绿色碎片、骨柱沉下去。整体约 90 格宽、56 格高，中心（锤石脚下）在格子正中偏下。**这张不旋转**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E, #0A4A2C) and pale teal bone (#D8FFE8, #7CC8B0, #3A7A6A).
Effect: THE BOX, a pentagon prison of spectral walls on the ground, 10 frames. The pentagon lies flat on the ground, seen from above at an angle: a flattened regular pentagon about 90% of the cell width and 55% of the cell height, centered horizontally, its center at 60% of the cell height (the middle stays EMPTY - the hero stands there). At each of the 5 corners stands a short pillar of stacked vertebra bones (pale teal, glowing green between the bones, about 25% of the cell height); between neighbouring pillars stands a translucent wall of green spectral light (drawn with hard-edged pixels: a bright top edge, vertical light streaks, fading toward the ground), the walls at the back drawn a little dimmer than the walls in front. 1 green cracks glow on the ground along the pentagon's outline; 2 the five bone pillars burst up from the ground, green light at their feet; 3 the walls rise between the pillars to half height; 4 to 7 the walls stand at full height (about 25% of the cell height), light streaks running upward inside them, a seamless loop from 7 back to 4; 8 the walls crack into green shards; 9 the shards fall and fade, the pillars sink; 10 faint green specks on the ground outline.
Layout: one horizontal row of 10 equal cells, each 8 wide to 5 tall, image size 2560x160 (each cell 256 wide, 160 tall); the pentagon's center at the center of every cell horizontally and at 60% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `thresh_fx_r_hit.png`：撞上监牢的墙（跟着目标），6 帧

敌方英雄撞到墙：一块绿色的灵魂墙碎片在它身上炸开，碎成绿光碎片，外加一圈锁链缠一下。约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a soul green ramp (#FFFFFF, #D8FFE8, #7CF5B0, #2FD47A, #148C4E, #0A4A2C).
Effect: a SPECTRAL WALL SHATTERS on an enemy, 6 frames: 1 a vertical pane of green light (with a bright top edge) flashes across the center; 2 the pane cracks with white lines; 3 it bursts into many angular green shards flying outward, a bright flash in the middle; 4 the shards spread to 80% of the cell, spinning; 5 the shards fade, a few green soul wisps rising; 6 faint specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the burst centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `thresh_fx_r_slow.png`：被监牢减速（脚下的灵魂锁链，跟着目标），4 帧，无缝循环

被减速 99% 的敌人脚下：一圈绿色的灵魂锁链缠着脚踝，地上一个暗绿色的扁圆光环，几缕灵魂烟往上飘。**只画在脚边，不能挡住身体**。约 24 格宽、12 格高，画在格子下半部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a soul green ramp (#D8FFE8, #7CF5B0, #2FD47A, #148C4E, #0A4A2C) and dark metal chain links (#8A7470, #4E3C3E).
Effect: SPECTRAL SHACKLES at a hero's feet, 4 frames, a seamless loop: in the lower half of the cell a flat dark green glowing ellipse on the ground (70% of the cell width, 20% of the cell height, centered at 85% of the cell height); a ring of green spectral chain links wrapped around where the ankles would be, just above the ellipse (never draw the hero); two or three thin green wisps rising from the ellipse and fading; each frame the light runs around the chain ring and the wisps rise.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered horizontally, the ellipse near the bottom of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`（头部是原版模型投票出来的），帧时长写在 `native/thresh_cells.json`。特效由 `tools/art/import_thresh.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `thresh_fx_lash.png` | 4 | 投射物 `league_thresh_lash`（普攻，朝飞行方向转） | 4 × 60 循环 |
| `thresh_fx_lash_flay.png` | 4 | 投射物 `league_thresh_lash_flay`（蓄满的普攻） | 4 × 60 循环 |
| `thresh_fx_hit.png` | 5 | 特效 `league_thresh_hit` | 5 × 50 |
| `thresh_fx_flay_hit.png` | 6 | 特效 `league_thresh_flay_hit`（跟随目标） | 6 × 60 |
| `thresh_fx_q_hook.png` | 4 | 投射物 `league_thresh_q_hook`（72000 远，朝飞行方向转） | 4 × 60 循环 |
| `thresh_fx_q_return.png` | 4 | 投射物 `league_thresh_q_return`（飞回锤石，朝飞行方向转） | 4 × 60 循环 |
| `thresh_fx_q_hit.png` | 8 | 特效 `league_thresh_q_hit`（跟随目标，眩晕 1 秒） | 1 × 80 + 6 × 120 + 1 × 100 |
| `thresh_fx_w_lantern.png` | 4 | 投射物 `league_thresh_w_lantern`（飞向队友） | 4 × 70 循环 |
| `thresh_fx_w_shield.png` | 6 | 增益 `league_thresh_w_shield`（护盾在时一直循环） | 6 × 100 循环 |
| `thresh_fx_e_sweep.png` | 7 | 特效 `league_thresh_e_sweep`（跟随锤石，锤石朝左时左右翻转） | 7 × 50 |
| `thresh_fx_e_hit.png` | 5 | 特效 `league_thresh_e_hit`（跟随目标） | 5 × 50 |
| `thresh_fx_r_box.png` | 10 | 特效 `league_thresh_r_box`（地上 5 秒：升起 3 帧，立着 4 帧重复，碎掉 3 帧） | 按 5 秒拼 |
| `thresh_fx_r_hit.png` | 6 | 特效 `league_thresh_r_hit`（跟随目标） | 6 × 60 |
| `thresh_fx_r_slow.png` | 4 | 增益 `league_thresh_r_slow`（减速期间循环） | 4 × 100 循环 |
