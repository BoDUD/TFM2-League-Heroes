# 安妮：给 Codex 的特效提示词

> **这一轮只画 13 张特效图。**
> - 角色不用画：安妮的模型由 Claude 做。头部（猫耳发箍、洋红短发、绿眼睛、暗红小嘴，用户选了方案 B）是逐格画的，每一帧贴在英雄联盟头部关节的位置；身体用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）。
> - 定稿造型图 `native/annie_native.png` 只用来参考配色，不要改它。
> - 提伯斯是特效，不是单位：他落地、站着喷火、消失都画成特效图（第 10–12 条），参考图 `tibbers_ref_*.png` 是英雄联盟里提伯斯的模型（只在本地用，不要提交）。
> - 火焰的画风参考 `base_fire_ref.png`：本体火法的普攻火球、技能爆炸、大招火圈和眩晕星星（红色外缘、橙色中间、白黄火心，火舌带尖角）。
> - 特效照下面第 1–13 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_annie.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 扔出小火球 | `annie_fx_bolt` · `annie_fx_hit` |
| 被动「嗜火」 | 每施放 4 次技能，下一个伤害技能眩晕命中的英雄 1 秒；眩晕就绪时身上有一圈白金色火光 | `annie_fx_pyro_ready` · `annie_fx_stun` |
| 技能 1 = Q「碎裂之火」 | 追踪的大火球，命中爆炸 | `annie_fx_q_ball` · `annie_fx_q_hit` |
| 技能 2 = W「焚烧」+ E「熔岩护盾」 | 朝目标喷出 50° 的扇形火焰，被烧到的敌人身上冒火；同时给自己套上熔岩护盾 3 秒（护盾在时反伤） | `annie_fx_w_cone` · `annie_fx_burn` · `annie_fx_e_shield` |
| 大招 = R「提伯斯之怒」 | 召唤提伯斯砸在敌方英雄身上（半径 30000 的范围伤害），提伯斯原地站 6 秒，每秒灼烧周围敌人，然后消失 | `annie_fx_tibbers_drop` · `annie_fx_tibbers` · `annie_fx_r_ring` · `annie_fx_tibbers_vanish` · `annie_fx_burn` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。火焰、火光、护盾**没有黑描边**（特效和角色相反）；只有提伯斯本人有一圈深褐色描边 `#1E120C`，因为他是个"角色"。
- 颜色：
  - 火焰（火球、爆炸、扇形火、灼烧、地面火圈）：`#FFFBE0`（白热火心）、`#FFE680`、`#FFB23A`、`#FF7A1E`、`#E8401C`、`#B0201A`、`#5A1410`，和本体火法一样外缘偏红、中间橙、火心白黄；
  - 嗜火就绪的火光：`#FFFFFF`、`#FFF4C8`、`#FFE08A`、`#FFB84A`（白金色，比火焰浅）；
  - 熔岩护盾：`#FFE680`、`#FF9A30`、`#E8501E`、`#A8281A`、`#4A1410`，熔岩壳 `#2A1410`；
  - 眩晕星星：`#FFFBE0`、`#FFE680`、`#FFB23A`、`#E8401C`；
  - 提伯斯：毛 `#2E1A12`、`#4E2C1C`、`#74432A`、`#9A5E3A`，肚皮和补丁 `#B07A52`、`#C99468`，缝线和眼睛发橙光 `#FFE680`、`#FF9A30`、`#FF7A1E`，爪子 `#E8DCC8`、`#8A7A6A`，描边 `#1E120C`；
  - 烟：`#6A5A56`、`#4A3E3A`、`#2E2624`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。扇形火（第 5 条）也会被转到施法方向，所以同样朝右、上下对称。
- 命中、灼烧、眩晕居中画，不旋转；地面上的圈按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 提伯斯（第 10–12 条）**不会被旋转**：他永远面朝右边、站在格子里的地面线上。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位；安妮本人头顶到脚底 34 格）。

### 1. `annie_fx_bolt.png`：普攻小火球（飞行物），3 帧循环

安妮随手扔出的小火球，游戏按方向旋转。约 10 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fire ramp (#FFFBE0, #FFE680, #FFB23A, #FF7A1E, #E8401C, #B0201A).
Effect: a SMALL FIREBALL flying to the RIGHT, 3 frames, a seamless loop: a round ball of fire with a white-yellow core at the RIGHT end, orange around it and a red outer edge, three short flame tongues licking backward to the left; SYMMETRIC above and below its middle line; only the flame tongues flicker from frame to frame; frame 3 leads back into frame 1.
Layout: one horizontal row of 3 equal cells, each four times as wide as tall (4:1), image size 1536x128; the fireball along the middle height of the cell, ball plus flames about 70% of the cell wide and 45% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `annie_fx_hit.png`：小火球命中，5 帧

小火球打中目标时炸开一小团火。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fire ramp (#FFFBE0, #FFE680, #FFB23A, #FF7A1E, #E8401C, #B0201A, #5A1410).
Effect: a SMALL FIRE HIT, 5 frames: 1 a small white-yellow flash at the center; 2 a burst of flame tongues shooting outward, bright yellow core, orange and red edges; 3 the burst at full size, about 45% of the cell wide, a few sparks flying out; 4 the flames shrink into small flickers, a wisp of dark red; 5 the last sparks and embers fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact point at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `annie_fx_q_ball.png`：碎裂之火大火球（飞行物），4 帧循环

Q 扔出的大火球，比普攻大一倍，拖着一条火尾巴，游戏按方向旋转。约 20 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fire ramp (#FFFBE0, #FFE680, #FFB23A, #FF7A1E, #E8401C, #B0201A, #5A1410).
Effect: a BIG FIREBALL (Disintegrate) flying to the RIGHT, 4 frames, a seamless loop: a large round ball of roaring fire with a white-hot core at the RIGHT end, a thick yellow-orange body and a red outer edge; behind it a long tail of flame tongues and sparks streaming to the left, darker red at the tail's end; SYMMETRIC above and below its middle line; the tail and the flame tongues change from frame to frame, the ball stays the same size; frame 4 leads back into frame 1.
Layout: one horizontal row of 4 equal cells, each four times as wide as tall (4:1), image size 2048x128; the fireball along the middle height of the cell, ball plus tail about 90% of the cell wide and 60% of its height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `annie_fx_q_hit.png`：大火球爆炸（跟着目标），6 帧

大火球打中目标时的爆炸，参考 `base_fire_ref.png` 里火法技能的爆炸（skill_boom_effect）。约 28 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fire ramp (#FFFBE0, #FFE680, #FFB23A, #FF7A1E, #E8401C, #B0201A, #5A1410) and a little grey smoke (#6A5A56, #4A3E3A).
Effect: a FIREBALL EXPLOSION, 6 frames: 1 a round white-yellow flash at the center; 2 a star-shaped burst of fire, yellow core, orange body, red spiky edge, a ring of grey smoke puffs around it; 3 the explosion at full size, about 55% of the cell wide, flame tongues and sparks shooting out in all directions; 4 the fire breaks into several rising flame tongues, the smoke ring spreading; 5 small flames and flying embers; 6 the last embers and smoke fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the explosion centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `annie_fx_w_cone.png`：焚烧的扇形火焰，6 帧（0.4 秒）

W 朝目标喷出的扇形火。**扇形的尖端在格子左边正中（安妮站的地方），向右张开 50°**，一直烧到格子右边。游戏会把整张图转到施法方向。约 56 格长、50 格高（格子就是这个比例）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fire ramp (#FFFBE0, #FFE680, #FFB23A, #FF7A1E, #E8401C, #B0201A, #5A1410).
Effect: a CONE OF FIRE (Incinerate) blasting to the RIGHT, 6 frames. The cone's point is at the MIDDLE of the LEFT edge of the cell and it opens to the right at 50 degrees in total, reaching the right edge of the cell, so at the right edge it is about 90% of the cell's height; SYMMETRIC above and below the middle line. 1 a bright white-yellow burst at the point, a few flame tongues shooting a third of the way to the right; 2 the fire rushes out to two thirds of the way, a white-yellow core along the middle line, orange body, red wavy edges along the cone's two sides; 3 the whole cone filled with roaring fire up to the right edge, flame tongues curling at the far end; 4 the full cone, the flames rolling and flickering; 5 the fire breaks up from the point outward, gaps appear, the far end turns dark red; 6 only scattered embers and small flames at the far end, fading.
Layout: one horizontal row of 6 equal cells, each 8 wide to 7 tall, image size 1536x224 (each cell 256x224); no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `annie_fx_burn.png`：灼烧（跟着目标），5 帧

被焚烧、提伯斯落地或灼烧打中的敌人身上冒出一团火。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a fire ramp (#FFFBE0, #FFE680, #FFB23A, #FF7A1E, #E8401C, #B0201A, #5A1410).
Effect: BURNING, 5 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 three small flame tongues spring up on the body of the space; 2 the flames grow and lick upward to the shoulders, yellow cores, orange and red tips; 3 the flames at full height, a few sparks rising above the head of the space; 4 the flames shrink, embers rising; 5 the last small flickers and embers fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the effect at most 45% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `annie_fx_e_shield.png`：熔岩护盾（套在安妮身上），6 帧，无缝循环

安妮身上套着一圈翻滚的熔岩火环，护盾在就一直循环，破了就消失。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, molten lava (#FFE680, #FF9A30, #E8501E, #A8281A, #4A1410) with dark crust flecks (#2A1410).
Effect: MOLTEN SHIELD around a small girl, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY small person-sized space (a small girl about 50% of the cell height stands there, feet at 85% of the cell height) - never draw the person. Around the space: an upright oval shell made of two or three bands of glowing molten lava that swirl around her, bright yellow-orange where they pass in front, darker red with black crust flecks where they curve behind, small blobs of lava dripping and flying off; the inside of the oval stays EMPTY and see-through; the bands turn a little each frame; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the oval about 45% of the cell wide and 70% of its height, its bottom at the feet of the space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `annie_fx_pyro_ready.png`：嗜火就绪（套在安妮身上），6 帧，无缝循环

攒满 4 次施法后，安妮身上绕着一圈白金色的火光，表示下一个技能会眩晕。要看得见但不能太抢眼。约 26 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a pale white-gold glow (#FFFFFF, #FFF4C8, #FFE08A, #FFB84A).
Effect: PYROMANIA READY, a charged glow around a small girl, 6 frames, a seamless loop. In the middle of every cell there is an EMPTY small person-sized space (a small girl about 50% of the cell height stands there, feet at 85% of the cell height) - never draw the person. Two thin ribbons of pale white-gold flame spiral around the space from the ankles up to the shoulders, like a slow whirlwind, with a few small white sparks orbiting her hands; where the ribbons pass behind the space they are hidden; the ribbons climb a little each frame; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the effect at most 40% of the cell wide, centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `annie_fx_stun.png`：眩晕（敌人头顶），6 帧，无缝循环

被嗜火眩晕的敌人头顶转着一圈小火星星，持续 1 秒。参考 `base_fire_ref.png` 最后一行的本体眩晕星星。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, fiery stars (#FFFBE0, #FFE680, #FFB23A, #E8401C).
Effect: STUNNED by fire, 6 frames, a seamless loop: three small four-pointed stars made of fire, white-yellow cores with orange and red tips, circling in a flat ellipse (twice as wide as tall) above a head; the stars move a sixth of the way round each frame, the star in front a little bigger than the ones behind, a tiny ember trail behind each; frame 6 leads back into frame 1.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the ellipse centered in every cell, about 60% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `annie_fx_tibbers_drop.png`：提伯斯砸下来（落点），6 帧（0.4 秒）

一团火从天而降，砸在地上炸开，提伯斯从火里站起来。提伯斯是一只巨大的棕色泰迪熊（见 `tibbers_ref_*.png`）：比安妮高得多（约 44 格），面朝右，弓着背，两只长手臂垂在身前、爪子深色，肚子上一块浅褐色的补丁，缝着三个 X 形针脚，中间一道发光的橙色裂缝（像岩浆），手臂上也有几道发光的裂缝，一双发光的橙色眼睛，龇着尖牙。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, seen from a slightly top-down game camera; fire (#FFFBE0, #FFE680, #FFB23A, #FF7A1E, #E8401C, #B0201A) without outline; the bear with a 1-pixel dark brown outline (#1E120C), fur (#2E1A12, #4E2C1C, #74432A, #9A5E3A), belly and patches (#B07A52, #C99468), glowing stitches and eyes (#FFE680, #FF9A30, #FF7A1E), claws (#E8DCC8, #8A7A6A).
Effect: TIBBERS SUMMONED, a giant teddy bear crashing down in fire, 6 frames. The ground is a line at 85% of the cell height. 1 a fireball streaks down from the top of the cell toward the ground, a long flame trail above it; 2 it hits the ground: a white-yellow flash and a wide burst of fire and dust along the ground (a flat ellipse); 3 inside the flames rises the dark silhouette of a huge hunched bear; 4 TIBBERS stands on the ground line, facing RIGHT: a giant brown teddy bear monster, hunched, big round head with small round ears, glowing orange eyes, snarling mouth with fangs, a pale tan belly panel with three X-shaped stitches and a glowing orange lava crack down its middle, glowing orange cracks on his arms, two long heavy arms hanging in front with dark claws, short thick legs; the bear is about 70% of the cell height; fire bursting around his feet; 5 he roars, arms spread a little, the fire at his feet settling into a ring of flames; 6 he stands, a ring of low flames around his feet.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the bear centered horizontally, his feet on the ground line at 85% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `annie_fx_tibbers.png`：提伯斯站着灼烧（落点），8 帧，1 秒一循环

落地后提伯斯原地站 6 秒，这张图每秒从头播一遍（所以正好 1 秒一圈）：喘气、身上的火苗跳动，中间挥一次爪子。**和第 10 条第 6 帧同一只熊、同样大小、同样站位**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, seen from a slightly top-down game camera; the same giant teddy bear as in the summoning sheet, with a 1-pixel dark brown outline (#1E120C), fur (#2E1A12, #4E2C1C, #74432A, #9A5E3A), belly and patches (#B07A52, #C99468), glowing stitches and eyes (#FFE680, #FF9A30, #FF7A1E), claws (#E8DCC8, #8A7A6A); small flames (#FFE680, #FFB23A, #FF7A1E, #E8401C) without outline.
Effect: TIBBERS BURNING, 8 frames, a seamless loop of exactly one second. The ground is a line at 85% of the cell height. The giant brown teddy bear monster stands on the ground line facing RIGHT, hunched, glowing orange eyes, snarling fangs, a pale tan belly panel with X-shaped stitches and a glowing orange lava crack down its middle, glowing cracks on his arms, long heavy arms with dark claws, about 70% of the cell height; small flames flicker on his shoulders and back in every frame. 1-3 he breathes, his shoulders rising and falling by one pixel; 4 he raises his right (front) arm; 5 he swipes it down and forward, three short orange claw trails in the air in front of him; 6 the arm at the bottom of the swipe; 7-8 he settles back into the breathing pose of frame 1; frame 8 leads back into frame 1.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the bear centered horizontally, his feet on the ground line at 85% of the cell height, exactly the same size and place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `annie_fx_tibbers_vanish.png`：提伯斯消失（落点），6 帧（0.5 秒）

6 秒到了，提伯斯化成一团烟和火星不见了。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, seen from a slightly top-down game camera; the same giant teddy bear as in the other sheets (1-pixel dark brown outline #1E120C, fur #2E1A12, #4E2C1C, #74432A, #9A5E3A, belly #B07A52, #C99468, glowing stitches #FFE680, #FF9A30); smoke (#6A5A56, #4A3E3A, #2E2624) and embers (#FFE680, #FFB23A, #E8401C) without outline.
Effect: TIBBERS VANISHING, 6 frames. The ground is a line at 85% of the cell height. 1 the bear stands facing RIGHT as in the burning sheet, his glow dimming; 2 he slumps, a puff of dark smoke bursts from his feet; 3 the smoke swallows his body, only his head and glowing eyes show above it; 4 a big round puff of grey smoke where he stood, orange embers flying up; 5 the smoke thins and drifts up, a few embers; 6 the last wisps and embers fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered horizontally, the ground line at 85% of the cell height, the bear the same size as in the other two sheets, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `annie_fx_r_ring.png`：提伯斯脚下的火圈（地面，画在单位下面），8 帧，1 秒一循环

提伯斯灼烧的范围：地面上一圈跳动的矮火苗，半径 30000，约 60 格宽、26 格高。每秒从头播一遍。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a fire ramp (#FFE680, #FFB23A, #FF7A1E, #E8401C, #B0201A, #5A1410).
Effect: a RING OF FIRE ON THE GROUND, 8 frames, a seamless loop of exactly one second: a flat ellipse on the ground, twice as wide as tall, made of short flickering flame tongues standing up along its rim, bright yellow-orange at the front of the rim, darker red at the back; a faint dark red scorched glow on the ground inside the ring; a few embers rising; the flame tongues flicker and change height from frame to frame; frame 8 leads back into frame 1.
Layout: one horizontal row of 8 equal cells, each twice as wide as tall (2:1), image size 4096x256; the ellipse centered in every cell, about 90% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，帧时长写在 `native/annie_cells.json`。特效由 `tools/art/import_annie.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `annie_fx_bolt.png` | 3 | 投射物 `league_annie_bolt`（普攻） | 3 × 50 循环 |
| `annie_fx_hit.png` | 5 | 特效 `league_annie_hit`（普攻命中） | 5 × 50 |
| `annie_fx_q_ball.png` | 4 | 投射物 `league_annie_q` | 4 × 50 循环 |
| `annie_fx_q_hit.png` | 6 | 特效 `league_annie_q_hit`（跟随目标） | 6 × 60 |
| `annie_fx_w_cone.png` | 6 | 投射物 `league_annie_w_cone`（56000 × 50000 的矩形，朝施法方向转） | 6 × 65（0.4 秒） |
| `annie_fx_burn.png` | 5 | 特效 `league_annie_burn`（跟随目标） | 5 × 70 |
| `annie_fx_e_shield.png` | 6 | buff `league_annie_e_shield`（护盾在时循环） | 6 × 90 循环 |
| `annie_fx_pyro_ready.png` | 6 | buff `league_annie_pyro_glow`（眩晕就绪时循环） | 6 × 110 循环 |
| `annie_fx_stun.png` | 6 | 特效 `league_annie_stun`（跟随目标，1 秒） | 6 × 85，重复两遍 |
| `annie_fx_tibbers_drop.png` | 6 | 特效 `league_annie_tibbers_drop`（落点，第 2 帧砸中 = 施放后 0.1 秒结算伤害） | 100，60，60，60，60，60 |
| `annie_fx_tibbers.png` | 8 | 特效 `league_annie_tibbers`（落点，每秒一段，共 6 段） | 8 × 125 |
| `annie_fx_tibbers_vanish.png` | 6 | 特效 `league_annie_tibbers_vanish`（落点） | 6 × 85 |
| `annie_fx_r_ring.png` | 8 | 特效 `league_annie_r_ring`（落点，地面，每秒一段，半径 30000） | 8 × 125 |

特效表：`league_annie_fx`（bolt、hit、q_ball、q_hit、burn、e_shield、pyro_ready、stun），`league_annie_big`（w_cone、tibbers_drop、tibbers、tibbers_vanish、r_ring）。

## 交付和导入结果（2026-09-28）

- Codex 交了 13 张生图原稿（`annie_fx_delivery.zip`：2172×724 等画布、半透明边），附 `manifest.json`（每帧的切图矩形）、`HANDOFF.md` 和 `preview.html`。原稿不进仓库。
- `tools/art/import_annie.py --raw <交付文件夹>` 按 manifest 切帧、每张 16 色（提伯斯三张共用 20 色）、每个游戏像素取覆盖它的原稿像素里最多的颜色，写成这里的 `annie_fx_*.png`（8×8 方块的原尺寸条）和 `annie_fx_anchors.json`（每张的格子和锚点）。
- 大小按技能范围：普攻火球 12 px、命中 16 px、碎裂之火 20 px、爆炸 28 px、灼烧 16 px 宽、熔岩护盾 42 px 高、嗜火火光 30 px 高、眩晕星 16 px、火圈 60 px 宽。焚烧的扇形 Codex 画得比 50° 宽，横竖分别缩放到技能的 56 × 50 矩形，尖端在格子左边。提伯斯三张里熊的大小不一（235、218、约 270 原稿像素），各自缩放到耳朵到脚底 42 px。
- 提伯斯的三张画在单位下层（`z` −1，火圈 −2）：他落在目标脚下，画在上面会挡住刚被眩晕的英雄。
