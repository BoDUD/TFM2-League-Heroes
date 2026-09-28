# 熔岩巨兽 墨菲特：给 Codex 的特效提示词

> **这一轮只画 10 张特效图。**
> - 角色不用画：墨菲特的模型由 Claude 做。头部（深色犀牛般的石头脑袋、从口鼻长出的浅色大石角、眉骨下发黄光的眼睛，用户选了方案 V12a）是逐格画的，每一帧贴在两肩中间；身体用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）。
> - 定稿造型图 `native/malphite_native.png` 只用来参考配色和人物大小（约 45 格高、43 格宽），不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里墨菲特自己的特效贴图（棕褐色碎石、奶白色烟尘、护盾的淡金色边、W 的熔岩红橙色岩块），只在本地用，不要提交。
> - 特效照下面第 1–10 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_malphite.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「花岗岩护盾」 | 岩石拳头猛砸；身上有一层岩石护盾，盾破 10 秒后重新长出来，护盾在时护甲更高 | `malphite_fx_hit` · `malphite_fx_granite` |
| 技能 1 = Q「地震碎片」 | 朝目标掷出一块碎石，造成魔法伤害并减速，墨菲特偷走这部分移速 | `malphite_fx_q_shard` · `malphite_fx_q_hit` |
| 技能 2 = E「大地震颤」+ W「雷霆拍击」 | 双拳砸地，周围敌人受伤并降低攻速；之后 4 秒普攻变成雷霆拍击，对前方扇形的敌人溅射 | `malphite_fx_e_slam` · `malphite_fx_e_hit` · `malphite_fx_thunder` · `malphite_fx_w_hit` |
| 大招 = R「势不可挡」 | 冲向一名敌方英雄，落地砸出大坑，把周围敌人击飞 | `malphite_fx_r_slam` · `malphite_fx_r_knockup` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色：
  - 碎石和岩块（棕褐）：`#D8C8B0`、`#B89878`、`#8A6A52`、`#6A4E3E`、`#4A362C`；
  - 墨菲特自己的石头（Q 的碎石、护盾的石片，灰紫）：`#D4C4C8`、`#B4A0AC`、`#8E7886`、`#6A5664`；
  - 烟尘（奶白到灰褐）：`#F0E6D2`、`#D8CCB8`、`#B0A28C`、`#8A7C6A`；
  - 花岗岩护盾的边（淡金）：`#FFF6D0`、`#F2DC98`、`#D8BA6A`、`#A8884A`；
  - 雷霆拍击和冲击的熔岩光（金白到暗红）：`#FFF3B0`、`#FFD24A`、`#FF9A30`、`#E8501E`、`#A8281A`、`#5A1410`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、碎裂、尘土居中画，不旋转；地面上的圈和坑按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在墨菲特身上的特效（护盾、雷霆拍击）：格子中间留出一个空的人形位置（按每条提示词写的比例，他又宽又壮），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `malphite_fx_hit.png`：普攻命中，5 帧

石头拳头砸中目标：一团碎石和尘土。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rock ramp (#D8C8B0, #B89878, #8A6A52, #6A4E3E) and a dust ramp (#F0E6D2, #D8CCB8, #B0A28C).
Effect: a STONE FIST IMPACT, 5 frames: 1 a small cream-white flash at the center; 2 it bursts into a puff of pale dust with four or five small brown rock chips flying out; 3 the puff at full size, about 45% of the cell wide, the chips further out; 4 the dust thins, the chips falling; 5 two or three chips and a wisp of dust fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `malphite_fx_w_hit.png`：雷霆拍击的普攻命中，6 帧

放完 E 之后 4 秒内的普攻：一声雷响般的熔岩冲击，金白色的闪光外面是橙红色的裂纹光和飞出的岩块。约 26 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a magma ramp (#FFF3B0, #FFD24A, #FF9A30, #E8501E, #A8281A) and a rock ramp (#B89878, #8A6A52, #6A4E3E).
Effect: THUNDERCLAP, a thunderous magma impact of a stone fist, 6 frames: 1 a white-hot point at the center; 2 a jagged golden flash bursts out, like a clap of thunder, with short orange lightning-like cracks radiating from it; 3 the flash at full size, about 60% of the cell wide, a ring of orange light around it and five or six dark rock chunks flying outward; 4 the flash breaks up, the orange cracks glow deep red, the rocks further out; 5 red embers and rock bits drifting; 6 the last embers fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the impact at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `malphite_fx_q_shard.png`：地震碎片（飞行），4 帧循环

一块翻滚着飞出去的灰紫色碎石，裂缝里透出一点金橙色的光，后面拖一小段棕色尘土。约 16 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a mauve stone ramp (#D4C4C8, #B4A0AC, #8E7886, #6A5664), a glow (#FFD24A, #FF9A30) and a dust ramp (#D8CCB8, #B0A28C, #8A7C6A).
Effect: a SEISMIC SHARD flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line. A jagged chunk of mauve-grey stone with a glowing golden-orange crack across it, at the right half of the cell, tumbling: it turns a quarter each frame; behind it to the left a short tapering trail of brown dust and two or three small pebbles.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 1024x170 (each cell 256x170); the shard at the right half of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `malphite_fx_q_hit.png`：地震碎片命中，6 帧

碎石砸中目标后碎裂：石片四散，扬起一团尘土，裂缝里的光闪一下。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a mauve stone ramp (#D4C4C8, #B4A0AC, #8E7886, #6A5664), a glow (#FFF3B0, #FFD24A, #FF9A30) and a dust ramp (#F0E6D2, #D8CCB8, #B0A28C).
Effect: the SEISMIC SHARD SHATTERS on its target, 6 frames: 1 a stone chunk at the center with a bright golden crack; 2 it cracks apart in a golden flash; 3 six or seven stone fragments fly outward and a round puff of dust grows, about 55% of the cell wide; 4 the fragments further out and falling, the dust at full size; 5 the dust thins, small fragments on the way down; 6 the last specks of dust.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the shatter at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `malphite_fx_e_hit.png`：大地震颤打中的敌人，4 帧

E 砸地时，被波及的每个敌人脚边弹起一小团尘土和碎石。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a dust ramp (#F0E6D2, #D8CCB8, #B0A28C, #8A7C6A) and a rock ramp (#B89878, #8A6A52, #6A4E3E).
Effect: a small GROUND JOLT under an enemy, 4 frames: 1 a flat crack of dust on the ground at the lower middle of the cell; 2 a small puff of dust and three pebbles jump up from it; 3 the puff at full size, about 40% of the cell wide, the pebbles at the top of their hop; 4 the dust settling, the pebbles falling back.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the ground line at 70% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `malphite_fx_r_knockup.png`：势不可挡的击飞（跟着目标），6 帧

大招落地时，被击飞的敌人脚下地面炸开，岩块和尘土往上喷，把人顶上天。约 24 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a rock ramp (#D8C8B0, #B89878, #8A6A52, #6A4E3E, #4A362C) and a dust ramp (#F0E6D2, #D8CCB8, #B0A28C).
Effect: KNOCK-UP ERUPTION, the ground bursting upward under an enemy, 6 frames: 1 the ground cracks at the bottom middle of the cell (a flat jagged crack); 2 a column of rock chunks and dust shoots straight up from the crack, reaching half of the cell height; 3 the column at full height, about 80% of the cell height and 45% of the cell wide, rocks at its top; 4 the column breaks up, rocks flying outward and up; 5 rocks falling back, dust hanging; 6 the dust fading, a few pebbles on the ground.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1152x256 (each cell 192x256); the crack at the bottom middle of every cell (ground line at 90% of the cell height), no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `malphite_fx_granite.png`：花岗岩护盾（跟着墨菲特），8 帧，无缝循环

护盾在的时候一直显示：墨菲特周围绕着几片小石板，外面一道淡金色的弧光在身体边缘流动（参考 `lol_fx_ref.png` 里的护盾光圈）。**不能挡住他的身体和脸**。人形空位约 45 格高、43 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a mauve stone ramp (#D4C4C8, #B4A0AC, #8E7886) and a pale gold ramp (#FFF6D0, #F2DC98, #D8BA6A, #A8884A).
Effect: GRANITE SHIELD, a stone barrier around a huge rock giant, 8 frames, a seamless loop. In the middle of every cell there is an EMPTY space the size of a bulky giant (70% of the cell height, 65% of the cell wide, feet at 88% of the cell height) - never draw the giant and never draw over that space. Around it: five small flat stone plates (3 to 5 pixels each) slowly orbiting at chest height on a flat ellipse, the ones in front brighter; and a thin broken arc of pale gold light (1 pixel wide) hugging the outside of the empty space, a bright glint running along the arc from frame to frame; frame 8 leads back into frame 1.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `malphite_fx_thunder.png`：雷霆拍击待发（跟着墨菲特），4 帧，无缝循环

放完 E 后 4 秒内：两只拳头边上噼啪闪着熔岩红橙色的电弧和火星，表示接下来的普攻会溅射。人形空位同上；两团电弧在空位左下和右下（拳头垂在那里）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a magma ramp (#FFF3B0, #FFD24A, #FF9A30, #E8501E, #A8281A).
Effect: THUNDERCLAP READY, crackling magma energy around a rock giant's two fists, 4 frames, a seamless loop. In the middle of every cell there is an EMPTY space the size of a bulky giant (70% of the cell height, 65% of the cell wide, feet at 88% of the cell height) - never draw the giant. At the lower left and lower right edges of that space, at about 60% of the cell height (where his big fists hang), two small clusters of jagged orange-gold lightning arcs and sparks, each about 15% of the cell wide, flickering: the arcs change shape every frame and a few embers jump off.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered on the empty space, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `malphite_fx_e_slam.png`：大地震颤（地面冲击波），7 帧

双拳砸地：地面裂开，一圈冲击波带着尘土和碎石向外扩开（画在人物下层，墨菲特站在圈中间）。圈最大约 72 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a dust ramp (#F0E6D2, #D8CCB8, #B0A28C, #8A7C6A) and a rock ramp (#B89878, #8A6A52, #6A4E3E, #4A362C).
Effect: GROUND SLAM SHOCKWAVE, 7 frames. On the ground a flat ellipse, twice as wide as tall, centered at 60% of the cell height; the middle of it stays EMPTY (the giant stands there). 1 a bright cream flash on the ground at the center with short cracks radiating out; 2 a ring of dust and rubble bursts outward, about 40% of the cell wide, dark jagged cracks running across the ground inside it; 3 the ring at 70% of the cell wide, rocks tossed up along it; 4 the ring at its widest, about 95% of the cell wide, thick rolling dust along the rim; 5 the dust rim breaks up, rocks falling; 6 dust fading, the cracks still visible; 7 the last dust and cracks fading.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 1792x128 (each cell 256x128); the ellipse's center at the same place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `malphite_fx_r_slam.png`：势不可挡落地（大坑），8 帧

墨菲特冲到目标身边砸落：一道白光，地面炸出一个带放射裂纹的大坑，厚厚一圈尘土向外翻滚，坑边岩块飞起（画在人物下层，墨菲特站在坑中间）。坑最大约 64 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a dust ramp (#F0E6D2, #D8CCB8, #B0A28C, #8A7C6A), a rock ramp (#D8C8B0, #B89878, #8A6A52, #6A4E3E, #4A362C) and an impact glow (#FFF3B0, #FFD24A, #FF9A30).
Effect: UNSTOPPABLE FORCE LANDING, a huge crater smashed into the ground, 8 frames. On the ground a flat ellipse, twice as wide as tall, centered at 60% of the cell height; the middle of it stays EMPTY (the giant stands there). 1 a blinding white-gold flash on the ground at the center; 2 the ground caves in: a dark crater appears with jagged radial cracks glowing orange, a ring of dust bursts out, about 50% of the cell wide; 3 big rock slabs heave up around the crater's rim, the dust ring at 75% of the cell wide; 4 the dust ring at its widest, about 95% of the cell wide, rocks flying up and outward; 5 rocks falling back, the dust rolling; 6 the dust thins, the crater and its cracks still dark; 7 the cracks stop glowing, dust fading; 8 the last dust around the crater.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 2048x128 (each cell 256x128); the crater's center at the same place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，头部从 `native/malphite_native.png` 贴在两肩中间（`poses.json` 的 `"anchor"`），帧时长写在 `native/malphite_cells.json`。特效由 `tools/art/import_malphite.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `malphite_fx_hit.png` | 5 | 特效 `league_malphite_hit`（普攻命中） | 5 × 50 |
| `malphite_fx_w_hit.png` | 6 | 特效 `league_malphite_w_hit`（雷霆拍击命中，跟随目标） | 6 × 50 |
| `malphite_fx_q_shard.png` | 4 | 投射物 `league_malphite_q_shard`（追踪弹，朝飞行方向转） | 4 × 60 循环 |
| `malphite_fx_q_hit.png` | 6 | 特效 `league_malphite_q_hit`（跟随目标） | 6 × 50 |
| `malphite_fx_e_hit.png` | 4 | 特效 `league_malphite_e_hit`（跟随目标） | 4 × 60 |
| `malphite_fx_r_knockup.png` | 6 | 特效 `league_malphite_r_knockup`（跟随目标，击飞 1.25 秒） | 6 × 80 |
| `malphite_fx_granite.png` | 8 | 增益 `league_malphite_granite`（护盾在时一直循环） | 8 × 100 循环 |
| `malphite_fx_thunder.png` | 4 | 增益 `league_malphite_thunder`（雷霆拍击待发 4 秒） | 4 × 80 循环 |
| `malphite_fx_e_slam.png` | 7 | 特效 `league_malphite_e_slam`（在墨菲特脚下，半径 36000，地面） | 7 × 60 |
| `malphite_fx_r_slam.png` | 8 | 特效 `league_malphite_r_slam`（在落点，半径 30000，地面） | 8 × 70 |

特效表：`league_malphite_fx`（hit、w_hit、q_shard、q_hit、e_hit、r_knockup、granite、thunder），`league_malphite_big`（e_slam、r_slam）。

## 交付和导入结果（2026-09-28）

- Codex 交了 10 张生图原稿（`malphite_fx_generated.zip`：2172×724、1983×793、1944×809 等画布，半透明边，58 帧），附 `manifest.json`（schema `malphite-vfx-raw-handoff-v1`，每帧的 `rect` 是 [x, y, 宽, 高]，帧宽不完全相等，另有每帧画面的 `content_bbox_local`）、`HANDOFF.md`、`PROMPTS_USED.json` 和 `preview.html`。原稿不进仓库。
- `tools/art/import_malphite.py --raw <交付文件夹>` 按清单切帧，每张 16 色，每个游戏像素取覆盖它的原稿像素里最多的颜色，写成这里的 `malphite_fx_*.png`（8×8 方块的原尺寸条）和 `malphite_fx_anchors.json`。
- 大小按技能范围，比例在画面上量（每条动画最宽的一帧，击飞石柱量最高的一帧）：普攻命中 14 px、雷霆拍击 26 px、Q 碎石连尾迹 16 px、Q 碎裂 22 px、E 敌人脚下 14 px、击飞石柱 32 px 高（照原宽度会有 39 px，比被击飞的人还高）、护盾石圈 50 px（包住他 43 px 宽的身体）、拳边两道电弧相距 40 px、E 冲击波 72 px 宽（半径 36000）、R 大坑 64 px 宽（半径 30000）。
- 定位：Q 碎石按石头前端；命中、碎裂、雷霆拍击按格子中心（每帧画面自己的包围盒会随碎片漂移）；E 敌人脚下和击飞石柱按画面最下一行（地面）贴在脚底；护盾石圈和电弧按画面中间贴在他身体中间和拳头的高度；冲击波和大坑按画布 60% 高度处的椭圆中心贴在脚底。
