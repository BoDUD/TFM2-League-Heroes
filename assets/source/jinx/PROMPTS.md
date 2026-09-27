# 金克丝：给 Codex 的特效提示词

> **这一轮只画 15 张特效图。**
> - 角色不用画：按新的分工，金克丝的模型由 Claude 做。造型图是在英雄联盟 34 格的剪影上按材质投色、再逐格画上眼睛和嘴（用户选了方案 B4：原版画法的眼睛，下巴正中一格她的唇色小嘴）；动作图用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`），和德莱厄斯、阿木木、亚索一样。
> - 定稿造型图 `native/jinx_native.png` 只用来参考配色，不要改它。
> - 特效照下面第 1–15 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_jinx.py --raw` 转成原尺寸条，再按技能范围定大小。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 = Q「枪炮交响曲！」 | 身边有敌人时用轻机枪「砰砰」（每发叠攻速）；附近没有敌人时换火箭发射器「鱼骨头」，射程更远，打中目标及周围的敌人 | `jinx_fx_bullets` · `jinx_fx_minigun_hit` · `jinx_fx_rocket` · `jinx_fx_rocket_hit` |
| 技能 1 = W「震荡电磁波！」 | 蓄力 0.4 秒，用电击枪射出一道电磁波，打中第一个敌人并减速 | `jinx_fx_w_charge` · `jinx_fx_zap` · `jinx_fx_zap_hit` |
| 技能 2 = E「嚼火者手雷！」 | 往敌方英雄脚下扔三只夹子，布好后最多留 5 秒；敌方英雄踩上时夹子咬合爆炸，定身 1.5 秒，随后夹子消失 | `jinx_fx_e_throw` · `jinx_fx_e_arm` · `jinx_fx_e_trap` · `jinx_fx_e_bite` · `jinx_fx_e_fizzle` |
| 大招 = R「超究极死神飞弹！」 | 飞越全图的鲨鱼飞弹，撞到第一个敌方英雄就爆炸 | `jinx_fx_r_rocket` · `jinx_fx_r_blast` |
| 被动「罪恶快感」 | 亲手击杀敌方英雄后，6 秒内攻速和移速大涨 | `jinx_fx_excited` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（金克丝的配色：粉、青、火）：
  - 粉：`#FFFFFF`、`#FFD1EC`、`#FF7AC6`、`#E8349A`、`#9E1F6B`；
  - 电光青：`#FFFFFF`、`#CFF8FF`、`#6EE7FF`、`#22B5E8`、`#1B6FB0`；
  - 火：`#FFFFFF`、`#FFF2A8`、`#FFC23F`、`#FF7A1F`、`#D6391A`、`#7A1E14`；
  - 烟：`#E8E0EA`、`#A89CB0`、`#5E5468`；
  - 火箭和夹子的金属：`#EDE6FF`、`#A9A6F0`、`#7F82D8`、`#4E4E9E`、`#2D2A5E`；牙 `#FFFFFF`；眼睛 `#FFD24A`；嘴里 `#B0243C`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。所以火箭、飞弹画成**从正上方往下看**的样子：鲨鱼头的两只眼睛分在上下两边，鳍上下各一片，牙齿沿着嘴的两边各一排，转过去也不会头朝下。
- 命中、爆炸、地面上的夹子居中画，不旋转（夹子有上下，按游戏的斜俯视角度画）。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `jinx_fx_bullets.png`：机枪子弹（飞行物），4 帧循环

普攻用「砰砰」时飞向目标，游戏按方向旋转。约 14 格长。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a hot pink ramp (#FFFFFF, #FFD1EC, #FF7AC6, #E8349A) with electric cyan (#CFF8FF, #6EE7FF).
Effect: a MINIGUN BURST flying to the RIGHT, 4 frames, a seamless loop: three short bright tracer bullets in a loose line one behind the other, each a white-hot tip with a pink streak trailing to the left, the middle one a little higher than the others; the burst is symmetric above and below its middle line; the streaks flicker (longer, shorter) from frame to frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each four times as wide as tall (4:1), image size 2048x128; the burst along the middle height of the cell, about 80% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `jinx_fx_minigun_hit.png`：机枪命中，5 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a hot pink ramp (#FFFFFF, #FFD1EC, #FF7AC6, #E8349A) with electric cyan (#CFF8FF, #6EE7FF).
Effect: a BULLET SPRAY HIT, 5 frames: 1 two small white sparks pop at the center; 2 three pink-and-white spark stars at slightly different spots around the center (a burst of bullets hitting); 3 the sparks at full size with tiny cyan chips flying out; 4 they shrink and scatter; 5 the last pink specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, the sparks at most 45% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `jinx_fx_rocket.png`：鱼骨头的小火箭（飞行物），4 帧循环

普攻用「鱼骨头」时飞向目标，游戏按方向旋转。约 20 格长。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline; metal (#EDE6FF, #A9A6F0, #7F82D8, #4E4E9E, #2D2A5E), teeth #FFFFFF, eyes #FFD24A, mouth #B0243C, fire (#FFFFFF, #FFF2A8, #FFC23F, #FF7A1F, #D6391A).
Effect: a small SHARK ROCKET flying to the RIGHT, seen from DIRECTLY ABOVE, 4 frames, a seamless loop: a stubby purple-blue rocket shaped like a shark, its rounded nose at the right with a wide toothy grin (a row of white teeth on the upper edge and a mirrored row on the lower edge, dark red between), one yellow eye on each side (upper and lower, mirrored), two small fins sticking out above and below, and a bright flame jet from its tail to the left (white at the nozzle, yellow, orange) with a few smoke puffs; the rocket is SYMMETRIC above and below its middle line; only the flame flickers from frame to frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), image size 2048x256; the rocket along the middle height of the cell, rocket plus flame about 85% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `jinx_fx_rocket_hit.png`：小火箭爆炸（溅射），6 帧

溅射半径 20000：爆炸约 40 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fire ramp (#FFFFFF, #FFF2A8, #FFC23F, #FF7A1F, #D6391A, #7A1E14), hot pink (#FF7AC6, #E8349A) and smoke (#E8E0EA, #A89CB0, #5E5468).
Effect: a ROCKET EXPLOSION, seen from a slightly top-down game camera, 6 frames: 1 a white flash at the center; 2 a round fireball bursts out, white-yellow core, orange edge, a few pink sparks; 3 the fireball at full size, about 75% of the cell wide, chunks of fire flying out; 4 it turns orange-red and breaks into lumps with dark smoke rising; 5 grey-purple smoke puffs with glowing embers; 6 the last smoke puffs fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the blast centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `jinx_fx_w_charge.png`：电击枪蓄力（金克丝手上），5 帧（0.4 秒）

金克丝抬起电击枪，枪口在她身前。只画枪口前的电光，不画人、不画枪。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, electric cyan (#FFFFFF, #CFF8FF, #6EE7FF, #22B5E8) with hot pink (#FF7AC6, #E8349A).
Effect: an ELECTRIC CHARGE gathering at a gun muzzle, 5 frames over 0.4 seconds: 1 two tiny cyan sparks at the center; 2 small crackling arcs (cyan and pink zigzags) gather toward the center from all sides; 3 a small bright ball of electricity forms at the center, white core; 4 the ball at full size, about 30% of the cell wide, arcs whipping around it; 5 it flashes white, the biggest, just before firing.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the charge centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `jinx_fx_zap.png`：电磁波（飞行物），4 帧循环

游戏按方向旋转。碰撞半径 15000：约 30 格长、8 格粗。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, electric cyan (#FFFFFF, #CFF8FF, #6EE7FF, #22B5E8, #1B6FB0) with hot pink (#FFD1EC, #FF7AC6, #E8349A).
Effect: ZAP!, a shock blast flying to the RIGHT, 4 frames, a seamless loop: a bright electric bolt - a white-hot core line with a thick cyan glow, pink lightning zigzags crackling along it above and below, a pointed glowing head at the right end and a short fading tail at the left; SYMMETRIC above and below its middle line; the zigzags change shape every frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each four times as wide as tall (4:1), image size 2048x128; the bolt along the middle height of the cell, about 90% of the cell wide and 40% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `jinx_fx_zap_hit.png`：电磁波命中（跟着目标），6 帧

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, electric cyan (#FFFFFF, #CFF8FF, #6EE7FF, #22B5E8) with hot pink (#FF7AC6, #E8349A).
Effect: an enemy SHOCKED AND SLOWED, 6 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a white-and-cyan burst hits the chest of the space; 2 cyan and pink lightning zigzags spread over the whole space; 3 crackling arcs around the body and down to the feet; 4 a few arcs left, small sparks falling to the feet; 5 a faint cyan ring on the ground under the feet (the slow); 6 the last sparks fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `jinx_fx_e_throw.png`：扔出去的三只夹子（飞行物），4 帧循环

游戏按方向旋转，所以三只夹子画成一团转着的样子。约 18 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline; metal (#EDE6FF, #A9A6F0, #7F82D8, #4E4E9E, #2D2A5E), hot pink (#FF7AC6, #E8349A), teeth #FFFFFF, eyes #FFD24A, fire (#FFF2A8, #FFC23F, #FF7A1F).
Effect: THREE FLAME CHOMPERS tumbling through the air, 4 frames, a seamless loop: three small round metal jaw traps (each a purple-and-pink ball with a zigzag row of white teeth, a yellow eye and a tiny flame fuse) flying close together in a triangle; the three tumble - each frame they turn a quarter around the middle of the group; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the group centered in every cell, about 70% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `jinx_fx_e_arm.png`：夹子落地张开（地面），3 帧（0.25 秒）

从这一张开始的四张夹子图都画在地上，**同一个位置、同一个大小**：三只夹子横着排成一排，约 32 格宽（判定半径 15000）。游戏里一张接一张地播放。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera; metal (#EDE6FF, #A9A6F0, #7F82D8, #4E4E9E, #2D2A5E), hot pink (#FF7AC6, #E8349A), teeth #FFFFFF, eyes #FFD24A, fire (#FFF2A8, #FFC23F, #FF7A1F), dust (#E8E0EA, #A89CB0).
Effect: THREE FLAME CHOMPERS landing and ARMING on the ground, 3 frames: three small metal jaw traps side by side in a row on the ground (the row about 80% of the cell wide, each trap about a quarter of the cell wide), each a squat purple-and-pink dome with a yellow eye; 1 they hit the ground closed, small dust puffs under them; 2 they spring OPEN like bear traps, upper jaw lifted, a zigzag row of white teeth on both jaws, dark red inside; 3 open and armed, a tiny orange flame flickering on the back of each.
Layout: one horizontal row of 3 equal cells, each twice as wide as tall (2:1), image size 1536x384; the row of traps centered horizontally, standing on a ground line at 75% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `jinx_fx_e_trap.png`：布好的夹子（地面），3 帧，无缝循环

最多循环 5 秒。**和第 9 张最后一帧的位置、大小、样子完全一样**，只有火苗和眼睛在动。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera; the same three armed FLAME CHOMPERS as in jinx_fx_e_arm.png frame 3, in the same place and size.
Effect: THE ARMED TRAPS WAITING, 3 frames, a seamless loop: the three open jaw traps sit still in their row on the ground; only the small orange flames on their backs flicker (smaller, bigger, smaller) and their yellow eyes blink once (open, half, open); frame 3 leads back into frame 1.
Layout: identical to jinx_fx_e_arm.png: one horizontal row of 3 equal cells, each twice as wide as tall (2:1), image size 1536x384; the traps standing on a ground line at 75% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `jinx_fx_e_bite.png`：夹子咬住敌人并爆炸（跟着目标），8 帧（约 1.3 秒）

踩中的敌方英雄被定身 1.5 秒。前 3 帧咬合爆炸，后 5 帧夹子咬在脚上冒火。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera; metal (#A9A6F0, #7F82D8, #4E4E9E, #2D2A5E), teeth #FFFFFF, fire (#FFFFFF, #FFF2A8, #FFC23F, #FF7A1F, #D6391A), smoke (#A89CB0, #5E5468), hot pink (#FF7AC6).
Effect: a FLAME CHOMPER BITES an enemy's feet and explodes, rooting it, 8 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 two open metal jaws with white teeth at the feet of the space, on the ground; 2 they SNAP SHUT around the feet, a white flash; 3 a fiery explosion bursts up around the lower body (up to the waist), orange and yellow with pink sparks; 4 the fire drops, the closed jaws clamped on the feet, smoke rising; 5-8 the clamped jaws stay on the feet with small flickering flames and a thin smoke curl, a little different each frame (the root).
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the effect at most 60% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `jinx_fx_e_fizzle.png`：夹子到时间消失（地面），4 帧

5 秒没人踩时播放。**起始画面和第 10 张一样**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera; the same three armed FLAME CHOMPERS as in jinx_fx_e_trap.png, in the same place and size; smoke (#E8E0EA, #A89CB0, #5E5468), fire (#FFC23F, #FF7A1F).
Effect: THE TRAPS FIZZLE OUT, 4 frames: 1 the three open traps, their flames going out; 2 their jaws clap shut; 3 each pops into a small puff of grey-purple smoke with a few orange embers; 4 the last smoke wisps fading.
Layout: identical to jinx_fx_e_arm.png: one horizontal row of 4 equal cells, each twice as wide as tall (2:1), image size 2048x512; the traps standing on a ground line at 75% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `jinx_fx_r_rocket.png`：超究极死神飞弹（飞行物），4 帧循环

游戏按方向旋转。碰撞半径 28000：飞弹加火焰约 60 格长。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline; metal (#EDE6FF, #A9A6F0, #7F82D8, #4E4E9E, #2D2A5E), teeth #FFFFFF, eyes #FFD24A, mouth #B0243C, hot pink (#FF7AC6, #E8349A), fire (#FFFFFF, #FFF2A8, #FFC23F, #FF7A1F, #D6391A), smoke (#E8E0EA, #A89CB0).
Effect: SUPER MEGA DEATH ROCKET, a huge shark-shaped rocket flying to the RIGHT, seen from DIRECTLY ABOVE, 4 frames, a seamless loop: a big fat purple-blue rocket with a shark face at its rounded nose on the right - a wide evil grin full of white teeth along the upper edge and a mirrored row along the lower edge, dark red inside, one angry yellow eye on each side (upper and lower, mirrored), pink stripes on the body, four fins (two above, two below, mirrored), and a long roaring flame jet from its tail to the left (white core, yellow, orange, red edge) breaking into smoke puffs; the rocket is SYMMETRIC above and below its middle line; only the flame and smoke move from frame to frame; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each three times as wide as tall (3:1), image size 3072x256; the rocket along the middle height of the cell, rocket plus flame about 90% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `jinx_fx_r_blast.png`：飞弹大爆炸，8 帧

爆炸半径 62000：约 120 格宽，是全英雄最大的爆炸。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fire ramp (#FFFFFF, #FFF2A8, #FFC23F, #FF7A1F, #D6391A, #7A1E14), hot pink (#FFD1EC, #FF7AC6, #E8349A) and smoke (#E8E0EA, #A89CB0, #5E5468).
Effect: a HUGE ROCKET EXPLOSION on the ground, seen from a slightly top-down game camera, 8 frames: 1 a blinding white flash at the center; 2 a big fireball swells up, white-yellow core; 3 THE FULL BLAST: a giant fireball with a flattened shockwave ring racing out along the ground (the ring about 2 times wider than tall, 90% of the cell wide), pink and orange sparks flying; 4 the fireball rises into a mushroom of fire, the ring still spreading; 5 it turns orange-red, chunks of fire and debris falling; 6 thick grey-purple smoke with glowing embers, the ring fading; 7 the smoke column thins; 8 the last smoke puffs fading.
Layout: one horizontal row of 8 equal cells, each twice as wide as tall (2:1), image size 4096x256; the blast centered, standing on a ground line at 70% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `jinx_fx_excited.png`：罪恶快感（金克丝身上），8 帧（约 0.8 秒）

击杀敌方英雄后在金克丝身上爆一下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a hot pink ramp (#FFFFFF, #FFD1EC, #FF7AC6, #E8349A) with electric cyan (#CFF8FF, #6EE7FF, #22B5E8).
Effect: GET EXCITED!, a burst of crazy joy around a girl, 8 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a pink flash pops at the chest of the space; 2 a ring of pink and cyan sparkles bursts outward around the whole space, with small pink hearts and stars; 3 zigzag speed streaks shoot from the feet backward to the LEFT; 4-6 the sparkles spin around the space and drift up, the speed streaks flicker at the feet; 7 fewer sparkles; 8 the last specks fading.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the effect at most 80% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，帧时长写在 `native/jinx_cells.json`。特效由 `tools/art/import_jinx.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `jinx_fx_bullets.png` | 4 | 投射物 `league_jinx_bullets`（机枪） | 4 × 50 循环 |
| `jinx_fx_minigun_hit.png` | 5 | 特效 `league_jinx_minigun_hit`（跟随目标） | 5 × 50 |
| `jinx_fx_rocket.png` | 4 | 投射物 `league_jinx_rocket`（鱼骨头） | 4 × 60 循环 |
| `jinx_fx_rocket_hit.png` | 6 | 特效 `league_jinx_rocket_hit`（溅射半径 20000） | 6 × 60 |
| `jinx_fx_w_charge.png` | 5 | 特效 `league_jinx_w_charge`（金克丝的枪口，0.4 秒） | 5 × 80 |
| `jinx_fx_zap.png` | 4 | 投射物 `league_jinx_zap`（半径 15000） | 4 × 50 循环 |
| `jinx_fx_zap_hit.png` | 6 | 特效 `league_jinx_zap_hit`（跟随目标） | 6 × 60 |
| `jinx_fx_e_throw.png` | 4 | 投射物 `league_jinx_e_throw`（抛物线，0.4 秒） | 4 × 60 循环 |
| `jinx_fx_e_arm.png` | 3 | 特效 `league_jinx_e_arm`（夹子链第 1 段，0.25 秒） | 3 × 83 |
| `jinx_fx_e_trap.png` | 3 | 特效 `league_jinx_e_trap`（第 2–20 段，每段 0.25 秒） | 3 × 83 |
| `jinx_fx_e_bite.png` | 8 | 特效 `league_jinx_e_bite`（跟随被咬的英雄） | 60/60/70/180/240/240/240/240 |
| `jinx_fx_e_fizzle.png` | 4 | 特效 `league_jinx_e_fizzle`（5 秒没人踩） | 4 × 70 |
| `jinx_fx_r_rocket.png` | 4 | 投射物 `league_jinx_r_rocket`（半径 28000） | 4 × 60 循环 |
| `jinx_fx_r_blast.png` | 8 | 特效 `league_jinx_r_blast`（半径 62000） | 8 × 70 |
| `jinx_fx_excited.png` | 8 | 特效 `league_jinx_excited`（跟随金克丝） | 8 × 100 |

特效表：`league_jinx_fx`（除飞弹和大爆炸外的全部），`league_jinx_big`（r_rocket、r_blast）。
