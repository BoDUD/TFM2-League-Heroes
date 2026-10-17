# 放逐之刃 锐雯：给 Codex 的特效提示词

> **这一份是 15 张特效图。** 模型（用户给的原图、版本 1）和 10 个动作做完后才画特效（造型 `design/riven_native.png`、动作 `MODEL_STRIPS.md`）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里锐雯自己的特效贴图（Q 的白色斩痕和月牙、Q3 的地面裂纹、W 的放射状爆发和地面符文、E 护盾上发绿光的符文碎片、R 的绿光剑身和疾风斩月牙），只在本地用，不要提交。颜色和画风对照 `design/riven_native.png`（定稿造型，8 倍）；大小对照 `design/riven_ingame.png`（游戏里的动作帧，4 倍，绿线是脚底和站位）：锐雯从头顶翘发到脚底 46 格，其他英雄约 35 格。
> - 特效照下面第 1–15 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_riven.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「符文之刃」 | 断剑劈砍；每放一次技能得一层符文（最多 3 层），普攻用掉一层，多打一段伤害 | `riven_fx_hit` · `riven_fx_rune_hit` · `riven_fx_rune` |
| 技能 1 = Q「折翼之舞」（3 次充能） | 第一、二段：跃向目标，周围一圈斩击；第三段：跃起砸地，击飞周围敌人 0.75 秒 | `riven_fx_q1_slash` · `riven_fx_q2_slash` · `riven_fx_q3_slam` · `riven_fx_q_hit` · `riven_fx_knockup` |
| 技能 2 = E「勇往直前」+ W「震魂怒吼」 | 冲到目标身边并获得护盾 1.5 秒，落地怒吼：周围敌人受伤并眩晕 0.75 秒 | `riven_fx_shield` · `riven_fx_w_burst` · `riven_fx_stun` |
| 大招 = R「放逐之锋」+ 疾风斩 | 断剑重铸 15 秒（攻击力、攻击距离、Q 和 W 范围提高）；5 秒后向身边的敌方英雄挥出疾风斩：一道月牙形的剑气向前飞 | `riven_fx_r_cast` · `riven_fx_r_aura` · `riven_fx_r_wave` · `riven_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（三套，按每条写的用）：
  - 剑光白（斩击、命中、Q3 的裂纹）：`#FFFFFF`、`#E8F4EE`、`#B9D4C6`、`#7E9C8E`、`#4A6458`；
  - 符文绿（被动、R、疾风斩、W 的地面符文、E 护盾的符文碎片）：`#F0FFE6`、`#A8FF7E`、`#4EE05A`、`#1FA045`、`#0E5A2A`；
  - 气劲蓝白（W 的爆发）：`#FFFFFF`、`#DDF6FF`、`#9ADCF2`、`#4E9EC4`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- 命中、爆开、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 在锐雯身前的斩击（Q 第一、二段）画在格子右半边：锐雯站在格子中间偏左（她的站位点在格子宽度的 35%、高度的 70%），斩击从她身前扫过。
- 套在英雄身上的特效（护盾、R 的光环、眩晕、击飞、符文）：格子中间留出一个空的人形位置（约 24 格宽、44 格高，脚在格子下方），不要画人，**不能挡住身体和脸**，只画套在外面的光、碎片和符文。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `riven_fx_hit.png`：普攻命中，5 帧

断剑砍中目标：一道白色的斜向斩痕，几点白色碎光。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blade-white ramp (#FFFFFF, #E8F4EE, #B9D4C6, #7E9C8E, #4A6458).
Effect: a HEAVY SWORD HIT, 5 frames: 1 a thin white diagonal slash line from upper left to lower right through the center; 2 the slash at full length and 2-3 squares thick, a small white flash at its middle; 3 the slash starts to break apart, white sparks flying out to both sides; 4 the slash fades to grey-green fragments; 5 a few faint grey-green specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the hit centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `riven_fx_rune_hit.png`：符文之刃强化的普攻命中，6 帧

用掉一层符文的那一下：斩痕更大、带绿色符文光，炸开几块发绿光的小符文碎片（参考 `glove_rune_quad`、`slash_green`）。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blade-white ramp (#FFFFFF, #E8F4EE, #B9D4C6) with a rune-green ramp (#F0FFE6, #A8FF7E, #4EE05A, #1FA045, #0E5A2A).
Effect: a RUNIC BLADE HIT, 6 frames: 1 a green-white spark at the center; 2 a thick white slash crescent cuts diagonally through the center, rimmed with bright green; 3 a second, crossing green slash appears, making an X, a white flash where they cross; 4 four small square green rune glyphs burst out of the X toward the corners; 5 the slashes fade to green, the glyphs flying further and dimming; 6 faint green specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the hit centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `riven_fx_rune.png`：身上的符文层数（有符文时一直播），4 帧循环

有符文的时候，她握剑那只手边上浮着一块发绿光的小符文（参考 `glove_rune_quad`：方形的绿色符文字）。约 8 格宽，很小，不挡身体。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rune-green ramp (#F0FFE6, #A8FF7E, #4EE05A, #1FA045, #0E5A2A).
Effect: a small FLOATING RUNE GLYPH, 4 frames, a seamless loop: a small square green glyph (a squarish rune sign, about 40% of the cell wide) with a bright pale-green core line, bobbing one square up and down, its glow pulsing brighter and darker, one or two green sparks drifting off it.
Layout: one horizontal row of 4 equal square cells, image size 512x128; the glyph centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `riven_fx_q1_slash.png`：Q 第一段的斩击（她身前），5 帧

她向前突刺时身前扫过的一道白色月牙斩（参考 `Q1_SlashText`、`slash_green`：白色的弧形斩痕，边缘带一点绿），从上往下斜着扫。约 44 格宽、34 格高（Q 的斩击半径 22000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blade-white ramp (#FFFFFF, #E8F4EE, #B9D4C6, #7E9C8E) with a thin rune-green edge (#A8FF7E, #4EE05A).
Effect: a WIDE SWORD SLASH sweeping in front of a fighter who stands at 35% of the cell width (do NOT draw her), 5 frames: 1 a thin white arc appears high in front of her, at the right half of the cell; 2 the arc sweeps down and forward into a big crescent (convex to the right), 3-4 squares thick in the middle and tapering to points, a pale green edge on its outer rim, spanning from the top right to the bottom right of the cell; 3 the crescent at full size with white streaks trailing behind it; 4 the crescent thins and breaks into short white streaks; 5 fading grey-green streaks.
Layout: one horizontal row of 5 equal cells, each 4 wide to 3 tall, image size 2560x384 (each cell 512x384); the slash in the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `riven_fx_q2_slash.png`：Q 第二段的斩击（她身前），5 帧

第二段是反手从下往上挑的一斩：白色月牙从她身前左下扫到右上。和第 4 张同样大小、同样的站位。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blade-white ramp (#FFFFFF, #E8F4EE, #B9D4C6, #7E9C8E) with a thin rune-green edge (#A8FF7E, #4EE05A).
Effect: a RISING BACKHAND SLASH in front of a fighter who stands at 35% of the cell width (do NOT draw her), 5 frames: 1 a thin white arc low in front of her, near the ground at the right half of the cell; 2 the arc sweeps upward and forward into a big crescent (convex to the right) from the bottom right to the top right, 3-4 squares thick in the middle and tapering to points, a pale green outer rim; 3 the crescent at full size, white streaks trailing below it; 4 the crescent thins and breaks into short white streaks; 5 fading grey-green streaks.
Layout: one horizontal row of 5 equal cells, each 4 wide to 3 tall, image size 2560x384 (each cell 512x384); the slash in the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `riven_fx_q3_slam.png`：Q 第三段砸地（地面），7 帧

她跃起后把剑砸进地面：落点炸开一圈白色冲击波（参考 `Q_GroundSlice`：一圈斩出来的地面圆环），地面裂开（参考 `Q_03_detonate_CracksDark`：从中心放射出去的裂纹），碎石和尘土往上飞。约 52 格宽、26 格高的椭圆（第三段半径 26000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a blade-white ramp (#FFFFFF, #E8F4EE, #B9D4C6, #7E9C8E, #4A6458) with a few rune-green glints (#A8FF7E, #4EE05A).
Effect: a SWORD SLAM SHOCKWAVE on the ground, 7 frames: 1 a bright white flash at the center of the ground; 2 a flat white ring bursts outward (an ellipse twice as wide as tall) to 50% of the cell width, dark grey cracks radiating from the center under it; 3 the ring at 90% of the cell width, thinner, chunks of grey rock and white dust thrown up above the ring; 4 the ring fades, the cracks at full length with a green glint in them, the rocks falling; 5 only the cracks and settling dust; 6 the cracks fading; 7 faint grey specks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 3584x256 (each cell 512x256); the slam centered in every cell, the thrown rocks may reach the top of the cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `riven_fx_q_hit.png`：Q 斩中的目标，5 帧

被 Q 斩到的每个敌人身上：一道白色斩痕加一点绿光。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blade-white ramp (#FFFFFF, #E8F4EE, #B9D4C6) with a touch of rune green (#A8FF7E, #4EE05A).
Effect: a SLASH IMPACT, 5 frames: 1 a thin white horizontal cut through the center; 2 the cut at full width with a bright white flash in the middle and a green rim; 3 white sparks burst up and down from the cut; 4 the cut breaks into short grey-green dashes, the sparks fading; 5 two faint green specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `riven_fx_knockup.png`：被击飞的目标（0.75 秒），6 帧

被 Q3 击飞的敌人：脚下卷起一圈白色的旋风尘土，几块碎石跟着往上飞。约 26 格宽、36 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a blade-white ramp (#FFFFFF, #E8F4EE, #B9D4C6, #7E9C8E, #4A6458).
Effect: a KNOCK-UP DUST SWIRL around a standing figure (leave a figure-shaped empty space in the middle of the cell, about 60% of the cell width and 75% of the cell height - do NOT draw the figure), 6 frames: 1 a white dust puff bursts on the ground at the feet (an ellipse twice as wide as tall); 2 two white wind streaks spiral up from it around the empty figure, small grey rocks flying up; 3 the streaks reach the figure's waist; 4 the streaks thin, the rocks at their highest; 5 the streaks break into wisps, the rocks falling; 6 faint dust at the feet.
Layout: one horizontal row of 6 equal cells, each 4 wide to 5 tall, image size 1536x320 (each cell 256x320); the dust centered horizontally at 90% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `riven_fx_shield.png`：勇往直前的护盾（套在她身上，最长 1.5 秒），8 帧

冲刺时身上出现的护盾（参考 `E_SheildMeshText`：发绿光的符文碎片；`E_SheildMult`）：几块半透明感的淡绿色碎片（用硬边色块表现，不要真的半透明）围着她转成一圈，碎片上有发亮的绿色符文。中间留空。第 1–2 帧出现，第 3–6 帧循环（护盾在的时候一直播），第 7–8 帧碎开消失。约 34 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rune-green ramp (#F0FFE6, #A8FF7E, #4EE05A, #1FA045, #0E5A2A) with blade-white glints (#FFFFFF, #E8F4EE).
Effect: a RUNE SHARD SHIELD around a standing figure (leave the middle EMPTY so the figure shows through - do NOT draw the figure or fill the middle), 8 frames: 1 small pale green shards appear at the figure's feet; 2 five shards (flat angular plates, each with a bright green square rune glyph) rise around the figure; 3-6 a seamless loop: the five shards orbit the figure in a tilted ellipse at waist height, the ones in front passing in front of the empty figure's legs, never over the head or face, a thin pale green shell line joining them, the glyphs pulsing; 7 the shards crack; 8 green specks falling.
Layout: one horizontal row of 8 equal cells, each 5 wide to 7 tall, image size 2560x448 (each cell 320x448); centered horizontally, the feet at 92% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `riven_fx_w_burst.png`：震魂怒吼（她周围的地面和空中），7 帧

她举剑怒吼的一刻：以她为中心炸开一圈蓝白色的气劲（参考 `W_Praxis`：放射状的爆发；`W_Electric_Arcs`：细小的电弧），地面上亮起一圈绿色符文（参考 `W_GroundRunes`）。约 50 格宽、30 格高（半径 25000），中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a ki blue-white ramp (#FFFFFF, #DDF6FF, #9ADCF2, #4E9EC4) with rune-green glyphs (#A8FF7E, #4EE05A, #1FA045).
Effect: a KI BURST around a fighter standing in the middle (leave her figure empty: about 24% of the cell width and 60% of the cell height above the ground ellipse - do NOT draw her), 7 frames: 1 a bright white flash at her feet; 2 a ring of blue-white energy bursts outward flat on the ground (an ellipse twice as wide as tall) to 50% of the cell width, short spiky rays pointing out of its edge, small crackling arcs; 3 the ring at 95% of the cell width, a circle of square green rune glyphs lighting up on the ground inside it; 4 the ring fades to pale blue, the glyphs bright; 5 the glyphs dim, a few arcs crackle; 6 the glyphs fading; 7 faint green specks.
Layout: one horizontal row of 7 equal cells, each 5 wide to 3 tall, image size 3360x288 (each cell 480x288); the burst centered in every cell with the ground ellipse at 70% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `riven_fx_stun.png`：被眩晕的目标（0.75 秒），6 帧

被震魂怒吼眩晕的敌人头顶：一圈绿色的小符文和白色的小星在转。约 20 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rune-green ramp (#F0FFE6, #A8FF7E, #4EE05A, #1FA045) with white (#FFFFFF).
Effect: a STUN above a head, 6 frames, a seamless loop: a small flat ellipse of light (twice as wide as tall) with three small square green rune glyphs and two tiny white stars spaced around it, turning one sixth of a circle each frame; the glyphs in front drawn brighter.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `riven_fx_r_cast.png`：放逐之锋开启（她身上），7 帧

开大的一刻：绿色的符文能量从地面涌上来，灌进断剑（参考 `sword_profile_glow`：发绿光的完整剑形；`Riven_Base_Z_Glow`），一圈绿光炸开。约 44 格宽、56 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rune-green ramp (#F0FFE6, #A8FF7E, #4EE05A, #1FA045, #0E5A2A) with white (#FFFFFF).
Effect: an EXILE BLADE AWAKENING around a standing fighter (leave her figure empty: about 50% of the cell width and 75% of the cell height, feet at 90% of the cell height - do NOT draw her), 7 frames: 1 a green glow on the ground at her feet (an ellipse); 2 four streams of green rune light spiral up around the empty figure; 3 the streams meet above her head in a bright white-green flash; 4 a ring of green light bursts outward from her waist, small square rune glyphs flying out; 5 the ring at the cell's edge, thinner; 6 the glyphs fading, a few green sparks rising; 7 faint green specks.
Layout: one horizontal row of 7 equal cells, each 5 wide to 7 tall, image size 2240x448 (each cell 320x448); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `riven_fx_r_aura.png`：放逐之锋持续中（套在她身上，15 秒循环），4 帧

开大期间：她身边一直飘着绿色的符文光和细碎的剑形光点（参考 `P_MiniSwordMask`、`glove_rune_quad`），脚下一圈淡绿的光。不能挡住身体和脸。约 32 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rune-green ramp (#F0FFE6, #A8FF7E, #4EE05A, #1FA045, #0E5A2A).
Effect: a RUNIC AURA around a standing fighter (leave her figure empty: about 60% of the cell width and 80% of the cell height, feet at 92% of the cell height - do NOT draw her, do NOT cover her), 4 frames, a seamless loop: a faint green ellipse of light on the ground at her feet; small green sparks and tiny sword-shaped green glints rise along both sides of the empty figure, each frame a little higher, new ones appearing at the bottom; one or two small square rune glyphs drifting upward.
Layout: one horizontal row of 4 equal cells, each 2 wide to 3 tall, image size 1024x384 (each cell 256x384); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `riven_fx_r_wave.png`：疾风斩（飞行），4 帧循环

一道巨大的月牙形剑气向前飞（参考 `R_SlashTip`、`slash_green`：向右凸的月牙，白色的芯、绿色的边），后面拖着绿色的风。约 26 格长、34 格高（剑气宽度约 32000）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rune-green ramp (#F0FFE6, #A8FF7E, #4EE05A, #1FA045, #0E5A2A) with a white core (#FFFFFF).
Effect: a WIND SLASH flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a tall crescent of energy (convex to the right) at 70% of the cell width, spanning 90% of the cell height, 4 squares thick in the middle with a white core and green edges, tapering to sharp points at the top and bottom; behind it to the left, three thinner green wind streaks and small green sparks, flickering differently in each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 4 tall, image size 768x256 (each cell 192x256); the crescent on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `riven_fx_r_hit.png`：疾风斩命中，6 帧

疾风斩打中的敌人身上：一团白绿色的剑气炸开，几道绿色的风痕飞散。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rune-green ramp (#F0FFE6, #A8FF7E, #4EE05A, #1FA045, #0E5A2A) with white (#FFFFFF).
Effect: a WIND SLASH IMPACT, 6 frames: 1 a bright white point at the center; 2 a vertical white-green crescent cut appears through the center; 3 it bursts into a round flash of green, white core, about 60% of the cell wide; 4 green wind streaks fly out to the left and right; 5 the streaks thin and fade; 6 faint green specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

- `tools/art/import_riven.py --raw <交付文件夹>`：按 `manifest.json` 或等宽格子切帧，按技能范围缩放（Q 斩击半径 22000、Q3 半径 26000、W 半径 25000、疾风斩宽度约 32000，锐雯 46 像素高），合成 `league/effects/league_riven_fx`（命中、符文、击飞、眩晕、护盾、R 光环）和 `league_riven_big`（Q 斩击、Q3 砸地、W 爆发、R 开启、疾风斩）两张图集；护盾（三段：出现 / 循环 / 碎开）、R 光环、符文按 buff 循环，击飞和眩晕的循环帧重复到 0.75 秒。
- 视图绑定在 `league_riven.data_champion`：`view_projectiles` r_wave；`view_effects` hit / rune_hit / q_hit / knockup / stun / r_hit / q1_slash / q2_slash / q3_slam / w_burst / r_cast；`view_buffs` e_shield、r、rune_1。
