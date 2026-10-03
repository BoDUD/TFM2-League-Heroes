# 暗裔剑魔 亚托克斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型和动作已定（`design/aatrox_design.png`，8 倍，40 行）。
> - 大小对照 `design/aatrox_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，右边是原版剑士。剑魔 39×40 格。每条写的大小都是游戏像素（格）。
> - `design/aatrox_shots.png`：被动强化、三段 Q、W、大招那几帧的定稿动作（4 倍），青色十字是剑尖、红爪或脚下的位置（导入时 Claude 把特效放到这里）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里剑魔自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（普攻和被动、Q、E、W、R），只在本地用，不要提交。颜色和英雄联盟一样：**剑光、命中、Q、大招是「地狱火」——白芯、淡金、橙、血红、深红；烟、恐惧和大招的雾是暗紫；W 的锁链是暗铁色的物体，链子里发橙红色的光**。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色或淡金色的芯，暗底上一眼能看见。
> - 特效照下面第 1–24 条和「所有特效图的规则」画，每张一个 PNG，文件名 `aatrox_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**（上一轮动作条用代码画的多边形翅膀被用户否了）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`aatrox_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「赐死剑气」 | 每隔几秒下一次普攻是强化一击：更远、按目标最大生命值加伤害并回血；打中英雄、Q 甜点打中都会缩短被动冷却 | `aatrox_fx_a_hit` · `aatrox_fx_p_swing` · `aatrox_fx_p_hit` |
| 技能 1 = Q「暗裔利刃」+ E「暗影冲决」 | 三段：第一段举剑下劈（一条长线）、第二段横扫（扇形）、第三段跃起下砸（圆圈）；每段剑刃最远处是甜点，打中伤害更高并击飞；E 有冷却时先冲刺把目标放到甜点上 | `aatrox_fx_q1_slash` · `aatrox_fx_q2_slash` · `aatrox_fx_q3_slash` · `aatrox_fx_q1_body` · `aatrox_fx_q2_body` · `aatrox_fx_q3_body` · `aatrox_fx_q_hit` · `aatrox_fx_q_edge` · `aatrox_fx_e_dash` |
| 技能 2 = W「恶火束链」 | 甩出锁链打中第一个敌人并减速；打中英雄时在打中处留下锁链圈拴住他，1.5 秒后还在圈里就被拉回圈中心、再受一次伤害；走出圈锁链就断 | `aatrox_fx_w_throw` · `aatrox_fx_w_chain` · `aatrox_fx_w_link` · `aatrox_fx_w_hit` · `aatrox_fx_w_ring` · `aatrox_fx_w_snap` · `aatrox_fx_w_yank` · `aatrox_fx_w_slowed` |
| 大招 = R「大灭」 | 变身：攻击力、移速、自身回复提高，附近的小兵被吓跑；持续期间参与击杀英雄会刷新 | `aatrox_fx_r_transform` · `aatrox_fx_r_aura` · `aatrox_fx_r_feared` · `aatrox_fx_r_renew` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火焰、刀光、火星没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。只有锁链（`w_chain`、`w_link`、`w_ring` 上的铁钉和链环、`w_snap`、`w_yank`、`w_slowed`、`w_hit` 的碎链）像物体一样有 1 格深色描边。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 地狱火（剑光、命中、Q、大招）：`#FFFFFF`、`#FFF0B8`、`#FFB347`、`#FF5A2A`、`#E0202E`、`#8F0E2B`；
  - 暗紫（烟、恐惧、大招的雾）：`#C9A6D8`、`#8E5BA8`、`#5A2E6E`、`#34163F`、`#1A0A22`；
  - 暗铁（锁链，物体）：`#D9D4DE`、`#9A93A8`、`#625B74`、`#39334A`、`#1A1624`；
- **飞行类和贴地的方向类特效朝右画，而且上下对称**（`w_chain`、`w_link`、`q1_body`、`q2_body`）：游戏会把它转到出招方向，朝左时整张会上下翻转，所以里面不要有分上下的东西。
- **从剑尖、红爪发出的特效朝右画，起点在格子左边的中点**（`p_swing`、`w_throw`）；画在剑魔身上的刀光（`q1_slash`、`q2_slash`、`q3_slash`、`e_dash`）按每条写的站位画在他右边：游戏把它画在剑魔身上，他朝左时整张左右镜像。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（`w_slowed`、`w_yank`）左右对称，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 第一段长 46000、第三段圈半径 20000、W 圈半径 20000）。

### 1. `aatrox_fx_a_hit.png`：普攻打中（目标身上），4 帧

普攻砍中：一道斜着的血红色刀痕闪一下，带几颗橙色火星（参考 AA_hit_splash、AA_hit_flash）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a SWORD HIT, 4 frames: 1 a white-gold flash; 2 a sharp diagonal slash mark 12 squares long (from upper left to lower right) with a white core and blood-red edges, 4 orange sparks; 3 the slash thinner and darker, sparks flying out; 4 a few fading red sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `aatrox_fx_p_swing.png`：被动「赐死剑气」强化一击：剑上的血光（施法者身上），5 帧

剑魔的被动强化一击：剑往前刺出时，剑身拖出一道很粗的血红色火焰剑气，向右冲出去（参考 P_Sword_Mask、AA_Gradient_RGB、E_dash_burst）。朝右画：剑尖在格子左边的中点，剑气从那里往右冲。约 36 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a BLADE OF HELLFIRE thrust to the RIGHT, 5 frames: 1 a white-gold spark at the LEFT MIDDLE of the cell (the sword's tip); 2 a thick wedge of blood-red fire with a white-gold core shoots out to the right, 20 squares long, flame tongues along its top and bottom edges; 3 the wedge at full length (32 squares), its tip the brightest, orange sparks; 4 the fire breaks into ragged red tongues drifting right; 5 fading embers.
Layout: one horizontal row of 5 equal 2:1 cells, image size 2560x256 (each cell 512x256); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `aatrox_fx_p_hit.png`：被动强化一击打中（目标身上），5 帧

被动强化一击打中：一大团血红色的火爆开，中间白金色的闪光，几道尖刺状的火舌往外射，带暗紫色的烟（参考 Q_hit_burst、AA_hit_flash、Q_Smoke_01）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) and a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22).
Effect: a HEAVY BLOOD-FIRE HIT, 5 frames: 1 a white flash; 2 a round burst of blood-red fire with a white-gold core, 6 sharp flame spikes shooting outward; 3 the burst at full size (20 squares), the spikes longer, orange sparks; 4 the fire breaks into curls, dark plum smoke; 5 fading smoke and embers.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `aatrox_fx_q1_slash.png`：Q 第一段：举剑下劈的刀光（施法者身上），5 帧

Q 第一段：剑从头顶往前劈下去时，剑尖划出的一道弧形血红刀光——从头顶上方往右下方的地面划过去，像一个月牙（参考 Q_impact_swipe、AA_hit_splash）。中间是人，不要画人。剑魔站在格子左下角附近（脚在格子底部往上 4 格、左边往右 12 格），刀光在他前面（右边）。约 40 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a DOWNWARD SWORD ARC in front of a figure standing near the lower LEFT of the cell (do NOT draw the figure), 5 frames: 1 a bright point above the figure's head; 2 a thick crescent of blood-red light with a white-gold leading edge sweeps from above the head down to the ground in front (to the right), like the trail of a huge overhead swing; 3 the full crescent from top to the ground, 6 squares thick in its middle, orange sparks where it meets the ground; 4 the arc thinner and broken, a puff of dust at the ground; 5 fading red streaks.
Layout: one horizontal row of 5 equal 10:9 cells, image size 2560x460 (each cell 512x460); the figure's feet 4 squares (32 px) above the bottom and 12 squares (96 px) from the left of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `aatrox_fx_q2_slash.png`：Q 第二段：横扫的刀光（施法者身上），5 帧

Q 第二段：剑在身前横着扫过去，划出一道很宽的扇形血红刀光，外边缘最亮（外边缘就是甜点位置）。中间是人，不要画人。剑魔站在格子左边（脚在格子底部往上 4 格、左边往右 10 格），刀光在他前面（右边）。约 44 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a WIDE HORIZONTAL SWEEP in front of a figure standing at the LEFT of the cell (do NOT draw the figure), 5 frames: 1 a thin bright line behind the figure; 2 a broad fan-shaped arc of blood-red light sweeps across in front of the figure at hip height, its OUTER rim white-gold and brightest; 3 the full fan, 30 squares from the figure to its rim, the rim flaring with orange sparks; 4 the fan fades from the inside, the rim breaking into red streaks; 5 fading sparks on the rim.
Layout: one horizontal row of 5 equal 11:6 cells, image size 2560x280 (each cell 512x280); the figure's feet 4 squares (32 px) above the bottom and 10 squares (80 px) from the left of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `aatrox_fx_q3_slash.png`：Q 第三段：跃起下砸的刀光和地面爆裂（施法者身上），5 帧

Q 第三段：跳起来往前下砸，剑劈下的一道竖直血红刀光，砸到地面时炸起一圈火焰和碎石（参考 Q_hit_burst、Q_ground_crack、W_Ground_Clump）。中间是人，不要画人。剑魔站在格子左下（脚在格子底部往上 4 格、左边往右 12 格），砸地点在他前面 24 格的地方。约 40 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) and a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22).
Effect: an OVERHEAD SLAM in front of a figure standing near the lower LEFT of the cell (do NOT draw the figure), 5 frames: 1 a bright streak high above the figure; 2 a tall arc of blood-red light comes down in front of the figure to the ground 24 squares to its right; 3 the impact: a burst of blood-red fire bursts up from that ground point with a white-gold core, 4 dark rock chunks thrown up; 4 the fire falls back, red cracks on the ground, plum smoke; 5 smoke and embers.
Layout: one horizontal row of 5 equal square cells, image size 2560x512; the figure's feet 4 squares (32 px) above the bottom and 12 squares (96 px) from the left of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `aatrox_fx_q1_body.png`：Q 第一段的范围：一条长长的地面刀痕（朝右，游戏转到出招方向），4 帧

Q 第一段打中的范围：从剑魔脚下往前（右）一条很长很窄的血红色刀痕贴在地上，最远的那一头（剑尖，甜点）是一团最亮的白金色火光（参考 Q_ground_marks2、Q_indicator_03_mask）。上下对称。约 48 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a LONG SLASH ON THE GROUND pointing to the RIGHT, 4 frames, SYMMETRIC above and below the middle line: 1 a thin red line runs from the left end to the right; 2 the line widens into a sharp blood-red streak 4 squares thick in the middle, tapering at both ends, and its RIGHT END (the tip) flares into a bright white-gold glow 8 squares across; 3 the streak darkens to crimson, the tip still bright; 4 fading red cracks and a dim tip.
Layout: one horizontal row of 4 equal 5:1 cells, image size 2560x128 (each cell 640x128); the streak on the middle line of every cell, its LEFT end at the cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `aatrox_fx_q2_body.png`：Q 第二段的范围：扇形地面刀痕（朝右），4 帧

Q 第二段打中的范围：从剑魔脚下往前（右）的一大片扇形血红色刀痕贴在地上，外圈的弧边（甜点）最亮（参考 Q_impact_swipe、Q_indicator_03_mask）。上下对称。约 36 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a FAN-SHAPED SLASH ON THE GROUND opening to the RIGHT, 4 frames, SYMMETRIC above and below the middle line: 1 a thin bright arc appears at the right; 2 a fan of blood-red light from the left middle out to an arc rim at the right (the fan 28 squares tall at the rim), the RIM bright white-gold and 3 squares thick; 3 the fan darkens to crimson streaks, the rim still bright; 4 fading red streaks on the rim.
Layout: one horizontal row of 4 equal 9:7 cells, image size 2304x448 (each cell 576x448); the fan's point at the LEFT edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `aatrox_fx_q3_body.png`：Q 第三段的范围：砸地的圆圈（地面上，不旋转），5 帧

Q 第三段砸地的范围：地上一个血红色的圆（从斜上方看是扁椭圆，宽是高的 2 倍），中间一小圈（甜点）最亮，圆里有裂开的地缝（参考 Q_ground_crack_03、Q_indicator_03_mask、Basic_Impact_ring）。约 40 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) and a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22).
Effect: a CRATER ON THE GROUND seen from above at an angle (a flattened ellipse twice as wide as tall), 5 frames: 1 a bright white-gold point at the center; 2 a ring of blood-red fire expands to the ellipse's edge, the center a bright white-gold disc 10 squares wide; 3 red cracks run from the center to the ring, the ring flaring orange; 4 the ring fades, the cracks glow crimson, plum smoke at the edge; 5 dim cracks.
Layout: one horizontal row of 5 equal 2:1 cells, image size 2560x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `aatrox_fx_q_hit.png`：Q 普通命中（目标身上），4 帧

Q 的刀光打中敌人（不在甜点）：一道红色刀痕和一小团火（参考 AA_hit_splash、Q_hit_burst）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a SLASH HIT, 4 frames: 1 a white flash; 2 a crossing pair of blood-red slash marks 12 squares long with white cores, orange sparks; 3 the marks breaking into red streaks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `aatrox_fx_q_edge.png`：Q 甜点命中：更大的爆裂 + 击飞（目标身上），5 帧

Q 的剑刃甜点打中：比普通命中大得多的血红爆裂，一道白红色的光柱往上冲（被击飞），带火星和碎片（参考 Q_hit_burst、R_EnergyStreaksAdd、R_Petal_Amber）。约 24 格宽、30 格高，爆裂的中心在格子下半部分。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a CRITICAL SWEET-SPOT HIT that launches the target up, 5 frames: 1 a big white-gold flash in the lower middle; 2 a burst of blood-red fire with a white core, 8 flame spikes, and a bright vertical shaft of white-red light shooting upward from it; 3 the shaft at full height (to the top of the cell), orange sparks and 3 red shards flying up; 4 the shaft thins and breaks into streaks; 5 falling embers.
Layout: one horizontal row of 5 equal 4:5 cells, image size 2000x500 (each cell 400x500); the burst's center 10 squares (80 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `aatrox_fx_e_dash.png`：E 冲刺的残影（施法者身上），4 帧

E「暗影冲决」：剑魔往前（右）冲的时候身后拖着一道暗紫色和血红色的影子和火焰（参考 E_Dash_glow、E_dash_burst）。人往右冲，残影在左边。约 30 格宽、16 格高，残影贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22) and a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a DASH TRAIL behind a figure rushing to the RIGHT (do NOT draw the figure; it stands at the right end), 4 frames: 1 a streak of dark plum shadow and blood-red flame tongues stretches 24 squares to the LEFT behind the figure, low to the ground; 2 the trail longer, its flames flickering upward; 3 the trail breaking into plum wisps; 4 fading wisps.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the figure's place at the RIGHT end, the feet 2 squares above the bottom, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `aatrox_fx_w_throw.png`：W 甩出锁链：红爪上的闪光（施法者身上），4 帧

W 甩出锁链的一瞬间：红爪前面一团暗红色的光炸开，几个铁环一样的碎光往右飞（参考 W_cast_ground、W_chain_glow）。朝右画：爪子在格子左边中点。约 14 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) and a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22).
Effect: a CAST FLASH pointing RIGHT, 4 frames: 1 a red-orange star at the LEFT MIDDLE of the cell (the claw); 2 a burst of dark plum and blood-red light spreading to the right, 3 small bright ring-shaped sparks flying right; 3 the sparks further right, the burst fading; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `aatrox_fx_w_chain.png`：W 飞出去的锁链（飞行中循环），4 帧

W「恶火束链」飞出去的锁链头：一个暗铁色带尖钩的锁链头（前面），后面跟着 3–4 节锁链，链子中间发着橙红色的光（参考 W_mis_core、W_chain_mask、W_chain_glow）。锁链本身是物体，有 1 格深色描边；光没有描边。上下对称。约 24 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from an iron ramp (#D9D4DE, #9A93A8, #625B74, #39334A, #1A1624) for the chain and a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) for its glow.
Effect: a FLYING CHAIN moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a dark iron hook-shaped chain head 6 squares long with a glowing orange-red core; behind it 4 chain links (each 4 squares long, alternating flat and edge-on) trailing to the left; a red-orange glow around the head and faint sparks behind, flickering each frame. The iron chain has a 1-square dark outline; the glow does not.
Layout: one horizontal row of 4 equal 3:1 cells, image size 1536x128 (each cell 384x128); the chain on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `aatrox_fx_w_link.png`：W 拴住目标时的锁链（一节，循环），4 帧

锁链拴住敌人的 1.5 秒里，从地上圈的中心到被拴的人之间连着一条锁链（英雄联盟里能看到拴着），这里只画其中一节：几节暗铁色的链环横着连在一起，中间一道暗红色的光在流动。左右两头要能无缝接上下一节。上下对称。约 16 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from an iron ramp (#D9D4DE, #9A93A8, #625B74, #39334A, #1A1624) and a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a SEGMENT OF A TAUT CHAIN lying left to right, 4 frames, a seamless loop, SYMMETRIC above and below the middle line, the left and right ends joining seamlessly to the next segment: 4 dark iron chain links (alternating flat ovals 4x4 squares and edge-on bars 4x2), a thin dim red-orange glow running through them and moving to the right each frame. The iron has a 1-square dark outline; the glow does not.
Layout: one horizontal row of 4 equal 8:3 cells, image size 2048x192 (each cell 512x192); the chain on the middle line, touching both side edges, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `aatrox_fx_w_hit.png`：W 锁链打中第一个敌人（目标身上），4 帧

锁链打中：一团暗红色的冲击，几节断开的锁链碎片向外飞（参考 W_Splash_tar、W_mis_core）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) and an iron ramp (#D9D4DE, #9A93A8, #625B74, #39334A, #1A1624).
Effect: a CHAIN IMPACT, 4 frames: 1 a red-orange flash; 2 a burst of blood-red light with 3 small dark iron chain links flying outward; 3 the links further out, the burst fading to crimson; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `aatrox_fx_w_ring.png`：W 地上的锁链圈（拴住期间，1.5 秒），6 帧

锁链打中英雄后，在打中的地方地上出现一个暗红色的圆圈（从斜上方看是扁椭圆，宽是高的 2 倍），圈边上一圈锁链和铁钉，中间一个暗紫色的漩涡，被拴的人走出圈就挣脱，1.5 秒还在圈里就被拉回圈中心（参考 W_hole_mask、W_hole_gradient、W_Ground_Clump、W_noise_mult）。第 1–2 帧圈出现，3–6 帧循环。约 40 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B), a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22) and an iron ramp (#D9D4DE, #9A93A8, #625B74, #39334A, #1A1624).
Effect: a CHAINED CIRCLE ON THE GROUND seen from above at an angle (a flattened ellipse twice as wide as tall), 6 frames: 1 a red-orange point flashes at the center; 2 a thin blood-red ring expands to the ellipse's edge, 8 small dark iron stakes stand on the ring; 3-6 (a seamless loop) the ring glows blood red and slowly pulses, dark iron chain links lie along the ring between the stakes, and a dark plum swirl turns slowly in the middle, a quarter turn per frame.
Layout: one horizontal row of 6 equal 2:1 cells, image size 3072x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `aatrox_fx_w_snap.png`：W 1.5 秒到：锁链收紧，把人拉回圈中心（地面上），5 帧

1.5 秒时还在圈里：圈上的锁链一下子全部收紧，往圈中心猛拉，中心炸开一团暗红色的光（参考 W_chain_glow、Basic_Impact_ring、W_Splash_tar）。约 40 格宽、24 格高（地上的扁椭圆加上往上冒的光）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) and an iron ramp (#D9D4DE, #9A93A8, #625B74, #39334A, #1A1624).
Effect: CHAINS SNAPPING TIGHT to the center of a flattened ellipse on the ground, 5 frames: 1 the blood-red ring flares; 2 six dark iron chains shoot from the ring toward the center in straight lines; 3 the chains meet at the center, a blood-red burst with a white-gold core jumps up there; 4 the burst fades, the chains break into links; 5 fading sparks at the center.
Layout: one horizontal row of 5 equal 5:3 cells, image size 2500x300 (each cell 500x300); the ellipse's center 6 squares (48 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `aatrox_fx_w_yank.png`：W 被拉回的目标：锁链缠身（目标身上），4 帧

被拉回圈中心的敌人身上：几道锁链缠住身体，暗红色的光一闪（参考 W_chain_mask、W_chain_glow）。中间是人，不要画人。约 18 格，左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from an iron ramp (#D9D4DE, #9A93A8, #625B74, #39334A, #1A1624) and a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: CHAINS WRAPPING a figure (do NOT draw the figure; symmetric left and right), 4 frames: 1 a red-orange flash round the figure's middle; 2 two dark iron chains wrap diagonally across the figure's place (an X), a blood-red glow along them; 3 the chains tighten, sparks; 4 the chains fade into red glints.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `aatrox_fx_w_slowed.png`：W 减速（目标脚下，循环），4 帧

锁链减速：被打中的敌人脚下一圈暗铁色的锁链，带一点暗红色的光，慢慢转（参考 W_slow_fade_in_out、W_chain_glow）。中间是人，不要画人。左右对称，4 帧无缝循环。约 20 格宽、8 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from an iron ramp (#D9D4DE, #9A93A8, #625B74, #39334A, #1A1624) and a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a CHAIN SHACKLE at a figure's feet (do NOT draw the figure; symmetric left and right), 4 frames, a seamless loop: a ring of dark iron chain links lying on the ground round the feet (a flattened ellipse twice as wide as tall), a dim blood-red glow along it, the links shifting a quarter of the way round each frame.
Layout: one horizontal row of 4 equal 5:2 cells, image size 2560x256 (each cell 640x256); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `aatrox_fx_r_transform.png`：R「大灭」变身爆发（施法者身上），8 帧

开大变身：剑魔身边炸开一团血红色的火焰往上冲，背后张开一对血红色光做的巨大翅膀的轮廓，地上一圈红色的冲击波（参考 R_wing_mask、R_swirl、R_glow_ring_mult001、R_EnergyStreaksAdd）。中间是人，不要画人。脚在格子底部往上 6 格的中间。约 48 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) and a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22).
Effect: a DEMONIC TRANSFORMATION BURST round a figure (do NOT draw the figure; leave its place empty), 8 frames: 1 a red flash at the figure's chest; 2 a column of blood-red fire bursts up round the figure, a flat red shock ring on the ground (an ellipse twice as wide as tall); 3 two huge bat-wing outlines of glowing blood-red light unfold behind the figure, one to each side, their tips at the top corners; 4 the wings at full size, white-gold edges, red energy streaks rising; 5 the fire column thins, the shock ring wide; 6 the wings fade from their tips; 7 rising embers and plum smoke; 8 a few embers.
Layout: one horizontal row of 8 equal square cells, image size 4096x512 (each cell 512x512); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `aatrox_fx_r_aura.png`：R 期间的血色光环（跟着人，循环），6 帧

大灭持续期间（10 秒）一直跟着他：身后一对半透明感的血红色光翼（只画光，像火焰组成的翅膀），脚下一圈暗红色的光和往上飘的火星（参考 R_wing_mask、R_body_mask、R_glow_distort）。中间是人，不要画人。脚在格子底部往上 6 格的中间。要亮，但别把人盖住：翅膀在人的两边和上方。6 帧无缝循环。约 56 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B) and a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22).
Effect: a LOOPING DEMONIC AURA round a figure (do NOT draw the figure; leave its place empty), 6 frames, a seamless loop: a pair of large bat wings made of blood-red flame and light spread behind the figure, one to each side, rising above its head (each wing 22 squares long, ragged flaming edges, a brighter orange-gold rim on the top edge); a ring of dim red light on the ground round the feet (an ellipse twice as wide as tall); embers rising; the wings beat gently (their tips 2 squares up and down over the loop) and the flames flicker.
Layout: one horizontal row of 6 equal 7:5 cells, image size 3360x400 (each cell 560x400); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `aatrox_fx_r_feared.png`：R 吓跑的小兵（目标头上，循环），4 帧

大灭期间附近的小兵被恐惧：头上一个暗紫红色的小漩涡在转（参考 R_Fear_Shock、R_swirl）。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a shade ramp (#C9A6D8, #8E5BA8, #5A2E6E, #34163F, #1A0A22) and a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a small FEAR MARK, 4 frames, a seamless loop: a dark plum and crimson swirl 8 squares across with a red core, turning a quarter turn each frame.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `aatrox_fx_r_renew.png`：R 击杀刷新（施法者身上），5 帧

大灭期间参与击杀英雄、大灭时间刷新：剑魔身边一圈红光往外扩，几道红色的能量往他身上收（参考 R_Revive_Circle、R_revive_energy、R_glow_ring_mult001）。中间是人，不要画人。约 30 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, slashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale-gold core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF0B8, #FFB347, #FF5A2A, #E0202E, #8F0E2B).
Effect: a RENEWAL PULSE round a figure (do NOT draw the figure), 5 frames: 1 a bright red ring flashes round the figure's middle; 2 the ring expands, 6 red energy streaks fly INWARD toward the figure; 3 the streaks reach the figure, a white-gold glint at its chest; 4 the ring fades at the edge; 5 a few rising embers.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `aatrox_fx_a_hit` | view_effects `league_aatrox_a_hit`（跟随，画在人物上面） | 14 |
| `aatrox_fx_p_swing` | view_effects `league_aatrox_p_swing`（施法者身上，跟随，朝左时镜像；格子左边中点放到被动强化第 4 帧的剑尖） | 36 × 16 |
| `aatrox_fx_p_hit` | view_effects `league_aatrox_p_hit`（跟随，画在人物上面） | 22 |
| `aatrox_fx_q1_slash` | view_effects `league_aatrox_q1_slash`（施法者身上，跟随，朝左时镜像） | 40 × 36 |
| `aatrox_fx_q2_slash` | view_effects `league_aatrox_q2_slash`（施法者身上，跟随，朝左时镜像） | 44 × 24 |
| `aatrox_fx_q3_slash` | view_effects `league_aatrox_q3_slash`（施法者身上，跟随，朝左时镜像） | 40 × 40 |
| `aatrox_fx_q1_body` | view_projectiles `league_aatrox_q1_body`（BIG，画在地面上，朝右画，上下对称） | 48 × 10 |
| `aatrox_fx_q2_body` | view_projectiles `league_aatrox_q2_body`（BIG，画在地面上，朝右画，上下对称） | 36 × 28 |
| `aatrox_fx_q3_body` | view_projectiles `league_aatrox_q3_body`（BIG，画在地面上，居中，不旋转） | 40 × 20 |
| `aatrox_fx_q_hit` | view_effects `league_aatrox_q_hit`（跟随，画在人物上面） | 16 |
| `aatrox_fx_q_edge` | view_effects `league_aatrox_q_edge`（跟随，画在人物上面） | 24 × 30 |
| `aatrox_fx_e_dash` | view_effects `league_aatrox_e_dash`（施法者身上，跟随，画在人物下面，朝左时镜像） | 30 × 16 |
| `aatrox_fx_w_throw` | view_effects `league_aatrox_w_throw`（施法者身上，跟随，朝左时镜像；格子左边中点放到 W 第 4 帧红爪的位置） | 14 × 12 |
| `aatrox_fx_w_chain` | view_projectiles `league_aatrox_w_chain`（朝右，游戏转到飞行方向，上下对称） | 24 × 8 |
| `aatrox_fx_w_link` | view_projectiles `league_aatrox_w_link`（朝右，游戏转到连线方向，上下对称；从地上的圈中心到被拴的人一节节接起来） | 16 × 6 |
| `aatrox_fx_w_hit` | view_effects `league_aatrox_w_hit`（跟随，画在人物上面） | 16 |
| `aatrox_fx_w_ring` | view_effects `league_aatrox_w_ring`（BIG，画在地面上，不跟随，循环到 1.5 秒） | 40 × 20 |
| `aatrox_fx_w_snap` | view_effects `league_aatrox_w_snap`（BIG，画在地面上，不跟随） | 40 × 24 |
| `aatrox_fx_w_yank` | view_effects `league_aatrox_w_yank`（跟随，画在人物上面） | 18 |
| `aatrox_fx_w_slowed` | view_buffs `league_aatrox_w_slowed`（循环，画在脚下） | 20 × 8 |
| `aatrox_fx_r_transform` | view_effects `league_aatrox_r_transform`（BIG，施法者身上，跟随，朝左时镜像） | 48 × 48 |
| `aatrox_fx_r_aura` | view_buffs `league_aatrox_r`（BIG，tag `r_aura`，循环，画在人物下面，朝左时镜像） | 56 × 40 |
| `aatrox_fx_r_feared` | view_effects `league_aatrox_r_feared`（跟随，画在人物上面） | 10 |
| `aatrox_fx_r_renew` | view_effects `league_aatrox_r_renew`（施法者身上，跟随） | 30 |

- 施法者身上的画面（`p_swing`、`q1_slash`、`q2_slash`、`q3_slash`、`e_dash`、`w_throw`、`r_transform`、`r_renew`）画在站位点上：按 `design/aatrox_shots.png` 的十字把格子的起点挪过去。
- 飞行物（`w_chain`、`w_link`）第一帧前加一个空帧（出生那一 tick 画面朝上，`import_lucian.py` 的 `RAY_SKIP`）；`q1_body`、`q2_body`、`q3_body` 是技能范围的投射物画面（不循环，播一次）；`w_ring` 的 3–6 帧循环到 90 tick（1.5 秒）；`r_aura` 循环 600 tick。
- `w_link` 给 W 补丁（`addons/league_aatrox_chain`）画拴住的锁链：每隔几 tick 从圈中心到被拴的人飞一节（和费德提克 W 的链条一样一节节接起来）。
- 清掉 Codex 给光和火焰描的最深色边（`import_riven.py` 的 `unrim` 做法，锁链保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
