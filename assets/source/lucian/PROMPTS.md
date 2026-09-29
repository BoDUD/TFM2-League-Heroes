# 圣枪游侠 卢锡安：给 Codex 的特效提示词

> **这一轮只画 14 张特效图。**
> - 角色（模型和动作图）另有一份 `MODEL_PROMPTS.md`，这里不用画人。
> - 定稿造型图 `native/lucian_native.png` 只用来参考配色和人物大小（约 34 格高：深色皮肤、脑后扎起的短脏辫，白色长外套配金边，深色长裤，双手各一把圣物手枪，枪口是青蓝色的发光晶体），不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里卢锡安自己的特效贴图（Q 的蓝白光束、W 的金色十字星和地面十字印记、标记的菱形印记、被动的蓝色十字火花、E 的几何光片、R 的子弹光痕），只在本地用，不要提交。
> - 特效照下面第 1–14 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_lucian.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「圣光银弹」「警惕」 | 手枪射出一发光弹；每放一个技能，下次普攻连开两枪（第二枪金色）；附近敌方英雄被定身后，接下来两次普攻多一道紫蓝色的魔能 | `lucian_fx_bullet` · `lucian_fx_bullet2` · `lucian_fx_hit` · `lucian_fx_vig_hit` · `lucian_fx_vig_glow` |
| 技能 1 = Q「透体圣光」 | 蓄力后射出一道穿透目标的长光束，直线上的敌人都受伤 | `lucian_fx_q_beam` · `lucian_fx_q_hit` |
| 技能 2 = E「冷酷追击」+ W「热诚烈弹」 | 冲刺（往前、往后或后跳），再射出一颗金色烈弹，碰到第一个敌人或飞到尽头时炸成十字星，标记被炸到的敌人 6 秒；标记期间他每次命中都会加速 1 秒 | `lucian_fx_e_dash` · `lucian_fx_w_bolt` · `lucian_fx_w_burst` · `lucian_fx_w_mark` · `lucian_fx_w_haste` |
| 大招 = R「圣枪洗礼」 | 站定 3 秒，双枪交替连射 20 发子弹，每发射向最近的敌方英雄 | `lucian_fx_r_bullet` · `lucian_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（都从英雄联盟卢锡安的特效里取）：
  - 圣光蓝（光束、子弹、火花）：`#102A8C`、`#1F4FD8`、`#4F8BFF`、`#A8CCFF`，白热的芯 `#F4FAFF`；
  - 圣光金（第二枪、烈弹、十字星、冲刺光片）：`#8A6420`、`#C8962E`、`#F0C85A`、`#FFF0B8`；
  - 魔能紫（警惕）：`#3A1E8C`、`#7A4AE8`、`#C0A8FF`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。
- 命中、爆炸、标记居中画，不旋转；地面上的形状按游戏的斜俯视角度画成扁的（宽约是高的 2 倍）。
- 套在卢锡安身上的特效（警惕的电光、加速）：格子中间留出一个空的人形位置（按那条写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `lucian_fx_bullet.png`：普攻光弹（飞行），4 帧循环

手枪射出的一发圣光子弹：一颗短短的白芯蓝边光弹，前端尖、后面拖一小段蓝色光痕。约 12 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy blue ramp (#102A8C, #1F4FD8, #4F8BFF, #A8CCFF) with a white-hot core (#F4FAFF).
Effect: a small HOLY LIGHT BULLET flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right part of the cell a short pointed bolt of light about 40% of the cell long and 25% of the cell tall, a white-hot core, pale blue edges, a sharp tip at the right; behind it to the left a thin tapering blue streak; the streak flickers a little from frame to frame (one or two squares longer or shorter), the bolt itself stays the same.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1024x86 (each cell 256x86); the bolt at the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `lucian_fx_bullet2.png`：圣光银弹的第二枪（飞行），4 帧循环

连开两枪的第二发：和第 1 张一样的光弹，但是金色（白芯、金边、金色光痕），稍大一点。约 14 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy gold ramp (#8A6420, #C8962E, #F0C85A, #FFF0B8) with a white-hot core (#F4FAFF).
Effect: a small GOLDEN LIGHT BULLET flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right part of the cell a pointed bolt of light about 45% of the cell long and 30% of the cell tall, a white-hot core, golden edges, a sharp tip at the right; behind it to the left a thin tapering golden streak with two tiny gold sparks; the streak and the sparks flicker from frame to frame, the bolt itself stays the same.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1024x86 (each cell 256x86); the bolt at the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `lucian_fx_hit.png`：普攻命中，5 帧

光弹打中目标：一个蓝白色的小十字火花（像原版被动的蓝色十字闪光），向外崩出几个小光点。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy blue ramp (#1F4FD8, #4F8BFF, #A8CCFF) with a white-hot core (#F4FAFF).
Effect: a small HOLY HIT SPARK, 5 frames: 1 a white-hot dot at the center; 2 a four-pointed cross flash about 50% of the cell wide, white core, pale blue arms (the horizontal arms a little longer than the vertical ones); 3 the cross at 70% of the cell wide, four tiny blue squares flying out diagonally; 4 the cross shrinking to blue, the squares further out; 5 two or three fading blue squares.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the spark at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `lucian_fx_vig_hit.png`：警惕的额外伤害（命中），5 帧

警惕充能后的一枪多出的魔能：一个紫蓝色的菱形闪光，外面一圈裂开的小电弧。约 18 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane violet ramp (#3A1E8C, #7A4AE8, #C0A8FF), holy blue (#4F8BFF, #A8CCFF) and a white-hot core (#F4FAFF).
Effect: an OVERCHARGED MAGIC HIT, 5 frames: 1 a small violet diamond at the center with a white dot; 2 the diamond at 45% of the cell wide, a white core, a violet rim, four short jagged violet lightning arcs sticking out; 3 the diamond at 60% of the cell wide, the arcs longer and forked, pale blue sparks; 4 the diamond breaking into four violet shards flying outward; 5 the shards and one arc fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the hit at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `lucian_fx_vig_glow.png`：警惕充能（套在卢锡安身上，循环），4 帧

警惕充能、还没打出去的时候：他胸口到双手的高度，几道紫蓝色的小电光噼啪跳动。这张会一直循环，最后一帧要能接回第一帧。约 26 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an arcane violet ramp (#3A1E8C, #7A4AE8, #C0A8FF) and holy blue (#4F8BFF, #A8CCFF).
Effect: OVERCHARGED PISTOLS aura around an EMPTY person-sized space (the person's chest in the middle of the cell, his two hands at the left and right thirds of the cell - never draw the person), 4 frames, a seamless loop: at the left and right hand points small clusters of violet energy crackle - two or three short jagged lightning arcs each, a few violet and pale blue sparks around them; the arcs jump to a different shape every frame; the middle of the cell stays clear.
Layout: one horizontal row of 4 equal cells, each 4 wide to 3 tall, image size 1024x192 (each cell 256x192); centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `lucian_fx_q_beam.png`：透体圣光光束（按施法方向转），6 帧

Q 的长光束：从卢锡安的枪口（左端）直射到右端，白色的芯、深蓝和亮蓝的边，像原版的蓝白激光。先是一道细线，再变成粗光束，最后变细消失。约 100 格长、12 格高（**图会按施法方向转，向左施放时整张转 180°，所以上下对称**）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy blue ramp (#102A8C, #1F4FD8, #4F8BFF, #A8CCFF) with a white-hot core (#F4FAFF).
Effect: PIERCING LIGHT, a long straight BEAM OF LIGHT across the whole cell from the LEFT edge to the RIGHT edge, 6 frames, SYMMETRIC above and below the middle line: 1 a thin bright white line (one square tall) across the whole cell with a small white flash at the left end (the muzzle); 2 the beam grows to about 60% of the cell tall: a white-hot core two squares tall, pale blue then bright blue then deep blue edges, a bright round flare at the left end; 3 the beam at full strength, 80% of the cell tall, tiny white sparks along its edges; 4 the beam narrowing to 40% of the cell tall, the edges deep blue; 5 a thin pale blue line, broken into dashes; 6 a few fading blue squares along the line.
Layout: one horizontal row of 6 equal cells, each 8 wide to 1 tall, image size 3072x64 (each cell 512x64); the beam on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `lucian_fx_q_hit.png`：透体圣光命中，5 帧

光束扫过每个敌人时：一道竖着的蓝白光柱在他身上闪一下，两边溅出几个光点。约 12 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy blue ramp (#1F4FD8, #4F8BFF, #A8CCFF) with a white-hot core (#F4FAFF).
Effect: a HOLY LIGHT IMPACT on an enemy, 5 frames: 1 a white-hot dot at 60% of the cell height; 2 a tall thin vertical flare, about 70% of the cell tall and 25% wide, white core, blue edges, pointed at both ends; 3 the flare at full height with a small horizontal cross flare at its middle and four blue sparks flying out; 4 the flare thinning and fading to blue, sparks further out; 5 two fading blue squares.
Layout: one horizontal row of 5 equal cells, each 1 wide to 2 tall, image size 640x256 (each cell 128x256); the flare centered across every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `lucian_fx_e_dash.png`：冷酷追击冲刺（起点和落点，不跟随），6 帧

冲刺开始和落地的地方：一圈金白色的几何光片（像原版 E 的菱形光框碎片）向外飞散，脚下一小团尘土。它会在起点和落点各播一次，不分方向。约 32 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy gold ramp (#8A6420, #C8962E, #F0C85A, #FFF0B8), pale holy blue (#A8CCFF) and dust greys (#6E6A62, #9C968A).
Effect: a DASH BURST where a person-sized figure stands (feet at 85% of the cell height - never draw the person), 6 frames: 1 a flat bright ring of light on the ground around the feet (an ellipse twice as wide as tall, 40% of the cell wide); 2 six thin angular golden light shards (narrow diamonds and chevrons, like broken frames of light) burst out from the feet and the waist, a small grey dust puff at the feet; 3 the shards flying outward and upward, 80% of the cell wide, pale blue glints on them; 4 the shards thinning into single golden lines, the dust spreading low along the ground; 5 a few golden squares and a thin dust cloud; 6 the last specks fading.
Layout: one horizontal row of 6 equal cells, each 4 wide to 3 tall, image size 1536x192 (each cell 256x192); centered across every cell with the feet at 85% of the cell height, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `lucian_fx_w_bolt.png`：热诚烈弹（飞行），4 帧循环

W 射出的烈弹：一颗金白色的小星形光弹（四个尖角，前后两个尖角长），后面拖一道金色火痕和几点火星。约 14 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy gold ramp (#8A6420, #C8962E, #F0C85A, #FFF0B8) with a white-hot core (#F4FAFF) and a little holy blue (#4F8BFF).
Effect: ARDENT BLAZE, a small golden STAR-SHAPED BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the right part of the cell a four-pointed star about 45% of the cell tall, its front and back points longer than the top and bottom ones, a white-hot center, golden points with a thin blue rim; behind it to the left a tapering golden fire trail and two or three tiny golden sparks; the star turns a little each frame (its top and bottom points one square longer or shorter), the trail flickers.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the star at the right part of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `lucian_fx_w_burst.png`：烈弹十字爆炸（地面，不旋转），7 帧

烈弹碰到敌人或飞到尽头时：在地上炸出一个金白色的大十字星（像原版 W 的地面十字：横向两臂长、纵向两臂短，中间一个小菱形），十字的四臂一闪，再碎成光点消失。约 52 格宽、28 格高（地面的扁十字）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy gold ramp (#8A6420, #C8962E, #F0C85A, #FFF0B8), a white-hot core (#F4FAFF) and a holy blue ramp (#1F4FD8, #4F8BFF, #A8CCFF).
Effect: ARDENT BLAZE EXPLOSION on the ground, a big four-pointed STAR CROSS seen from a 3/4 top-down view (flattened: the left and right arms long, reaching 95% of the cell width; the up and down arms short, reaching 90% of the cell height), 7 frames: 1 a white-hot flash at the center with a small golden diamond; 2 the four arms shoot out to half length, thin and white-hot, golden edges; 3 the full star cross: white-hot arms narrowing to sharp points, golden edges, a small golden diamond ring at the center, a thin blue outline flicker along the arms; 4 the arms at full length, fading to gold, small golden sparks spraying out from the center; 5 the arms breaking into dashes, blue glints; 6 scattered golden squares along where the arms were; 7 a few fading specks and the center diamond vanishing.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 1792x128 (each cell 256x128); the star centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `lucian_fx_w_mark.png`：烈弹标记（被标记的敌人脚下，跟着他，循环），4 帧

被烈弹炸到的敌人脚下：一个扁的金色菱形印记（像原版 W 的菱形标记：外菱形框、内小菱形、中间一个光点），轻轻闪烁。持续 6 秒，一直循环，最后一帧要能接回第一帧。约 22 格宽、11 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy gold ramp (#8A6420, #C8962E, #F0C85A, #FFF0B8) and holy blue (#4F8BFF, #A8CCFF).
Effect: ARDENT BLAZE MARK on the ground under a marked unit, seen from a 3/4 top-down view (flattened, twice as wide as tall), 4 frames, a seamless loop: an outer thin golden diamond frame filling 90% of the cell width, an inner smaller golden diamond, a bright white-gold dot at the center, two tiny golden circles at the left and right corners of the outer diamond; frame 1 dim gold, frame 2 brighter with a thin blue edge on the inner diamond, frame 3 brightest (the center dot white), frame 4 back to dim.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the diamond centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `lucian_fx_w_haste.png`：加速（套在卢锡安脚下，循环），4 帧

标记期间他命中敌人后加速的 1 秒：脚边几道金色的速度线和一点尘土往后（左）拖。这张会循环，最后一帧要能接回第一帧。约 24 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy gold ramp (#C8962E, #F0C85A, #FFF0B8) and dust greys (#6E6A62, #9C968A).
Effect: SPEED BOOST at the feet of an EMPTY person-sized space (the feet at the middle of the cell, never draw the person), 4 frames, a seamless loop: three or four thin horizontal golden speed lines streaming out to the LEFT behind the feet, at different heights close to the ground, each one moving further left every frame while a new one starts at the feet; one small grey dust puff kicked up behind the feet.
Layout: one horizontal row of 4 equal cells, each 5 wide to 2 tall, image size 1280x128 (each cell 320x128); the feet at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `lucian_fx_r_bullet.png`：圣枪洗礼子弹（飞行），3 帧循环

大招连射的子弹：比普攻光弹更细更长的一道白蓝光痕，快速飞行。约 16 格长、3 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy blue ramp (#1F4FD8, #4F8BFF, #A8CCFF) with a white-hot core (#F4FAFF).
Effect: a THIN FAST LIGHT BULLET flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC above and below the middle line: a long thin streak of light filling 90% of the cell width and about 20% of the cell height, a white-hot tip at the right, fading to pale blue then blue toward the left end; every frame the streak's tail is a square longer or shorter and its tip flickers.
Layout: one horizontal row of 3 equal cells, each 5 wide to 1 tall, image size 960x64 (each cell 320x64); the streak on the middle line of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `lucian_fx_r_hit.png`：圣枪洗礼命中，3 帧

每发子弹打中时：一个很小的白蓝火花。约 10 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a holy blue ramp (#1F4FD8, #4F8BFF, #A8CCFF) with a white-hot core (#F4FAFF).
Effect: a TINY BULLET HIT SPARK, 3 frames: 1 a white-hot dot with four short pale blue rays, about 50% of the cell wide; 2 the rays at 80% of the cell wide, two tiny blue squares flying out; 3 two fading blue squares.
Layout: one horizontal row of 3 equal square cells, image size 384x128; the spark at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

特效由 `tools/art/import_lucian.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小），全部放在特效表 `league_lucian_fx`。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `lucian_fx_bullet.png` | 4 | 投射物 `league_lucian_bullet`（普攻、连开两枪的第一枪，朝飞行方向转） | 4 × 50 循环 |
| `lucian_fx_bullet2.png` | 4 | 投射物 `league_lucian_bullet2`（第二枪，朝飞行方向转） | 4 × 50 循环 |
| `lucian_fx_hit.png` | 5 | 特效 `league_lucian_hit`（普攻命中，跟随目标） | 5 × 40 |
| `lucian_fx_vig_hit.png` | 5 | 特效 `league_lucian_vig_hit`（警惕的额外伤害，跟随目标） | 5 × 50 |
| `lucian_fx_vig_glow.png` | 4 | 状态 `league_lucian_vig_glow`（警惕充能，最长 4 秒，跟随他） | 4 × 80 循环 |
| `lucian_fx_q_beam.png` | 6 | 投射物 `league_lucian_q_beam`（光束，长 100000、宽 12000，按施法方向转） | 6 × 40 |
| `lucian_fx_q_hit.png` | 5 | 特效 `league_lucian_q_hit`（光束命中，跟随目标） | 5 × 40 |
| `lucian_fx_e_dash.png` | 6 | 特效 `league_lucian_e_dash`（冲刺起点、落点，不跟随） | 6 × 50 |
| `lucian_fx_w_bolt.png` | 4 | 投射物 `league_lucian_w_bolt`（烈弹，朝飞行方向转） | 4 × 50 循环 |
| `lucian_fx_w_burst.png` | 7 | 特效 `league_lucian_w_burst`（爆炸点，地面，半径 20000，不旋转） | 7 × 50 |
| `lucian_fx_w_mark.png` | 4 | 状态 `league_lucian_w_mark`（被标记的敌人脚下，6 秒，跟随） | 4 × 120 循环 |
| `lucian_fx_w_haste.png` | 4 | 状态 `league_lucian_w_haste`（加速 1 秒，他脚下，跟随） | 4 × 60 循环 |
| `lucian_fx_r_bullet.png` | 3 | 投射物 `league_lucian_r_bullet`（大招子弹，朝飞行方向转） | 3 × 40 循环 |
| `lucian_fx_r_hit.png` | 3 | 特效 `league_lucian_r_hit`（大招命中，跟随目标） | 3 × 40 |
