# 潮汐海灵 菲兹：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图。** 造型已定（`design/fizz_design.png`，8 倍），动作条已经画好；这一轮只画特效。
> - 大小对照 `design/fizz_size.png`：定稿造型放大 4 倍，站在红色脚底线上，上面是 10 格一段的刻度，右边是原版骑士。菲兹 55×32 格（头顶到鞋底 32 格，横着的三叉戟占去大半宽度），原版英雄约 35 格高。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里菲兹自己的特效贴图，按用在我们哪张特效分好了行（普攻和技能的水花、E 的溅水和波纹、R 的鱼、鲨鱼牙圈和鲨鱼鳍），只在本地用，不要提交。
> - 特效照下面第 1–12 条和「所有特效图的规则」画，每张一个 PNG，文件名 `fizz_fx_<名字>.png`，排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。最好打成一个 zip（`fizz_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「伶俐斗士」 | 三叉戟戳击（附带流血）；受到的普攻伤害降低 | `fizz_fx_hit` |
| 技能 1 = Q「淘气打击」+ W「海石三叉戟」 | 穿过目标冲刺（出发点留下水痕）；海石三叉戟每 5 秒强化一次普攻或 Q：一个三叉戟亮光加大水花 | `fizz_fx_q_dash` · `fizz_fx_q_hit` · `fizz_fx_w_hit` |
| 技能 2 = E「古灵精怪」 | 跳上三叉戟（脚下溅水），悬空躲技能，然后砸地：一大圈水花冠，周围敌人减速 | `fizz_fx_e_up` · `fizz_fx_e_slam` · `fizz_fx_e_slow` |
| 大招 = R「巨鲨强袭」 | 扔出一条鱼，粘在第一个敌方英雄身上，他脚下出现鲨鱼牙的预警圈，2 秒后鲨鱼从地下冲出把周围敌人顶飞；鱼飞得越远鲨鱼越大（三档）；没粘到人，鱼掉在地上蹦，2 秒后在那里冲出大鲨鱼 | `fizz_fx_r_fish` · `fizz_fx_r_stuck` · `fizz_fx_r_ring` · `fizz_fx_r_fish_ground` · `fizz_fx_r_shark` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反；之前的交付每个形状都被描了深色边，还得清掉）。鱼和鲨鱼是例外：它们是「东西」，可以用自己最深的颜色勾一圈细边，但不要近黑。
- 颜色（按每条写的用）：
  - 水（水花、波纹、水珠）：`#FFFFFF`、`#D8F8FF`、`#8CE6FF`、`#3CC0F0`、`#1A84D0`、`#0E4A94`；
  - 青绿（海石三叉戟的亮光）：`#E8FFF6`、`#9EF2D8`、`#3FD0B0`、`#16947E`、`#0A5B4A`；
  - 鱼（橙白小丑鱼）：`#FFF4E0`、`#FFC878`、`#FF8C34`、`#D85A18`、`#8C3412`；
  - 鲨鱼：`#F0F6FA`、`#B4CCDC`、`#6E90AC`、`#3E5C7C`、`#22344C`、`#121C2C`，嘴和牙 `#FFFFFF`、`#E8E0D0`、`#B03A48`、`#6A1828`。
- **飞行的鱼朝右画，而且上下对称**（`r_fish`）：游戏会把它转到飞的方向，向左时整张图转 180°。
- 命中、水花、鲨鱼、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在英雄身上的特效（粘住的鱼、鲨鱼预警圈、减速）：格子里留出空的人形位置，不要画人，**不能挡住身体和脸**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `fizz_fx_hit.png`：普攻命中，5 帧

三叉戟戳中目标：一小朵青蓝色的水花星形闪光，周围溅出几滴水珠（参考 BA_Impact_Flash、BA_LinearSplash）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a SMALL WATER HIT, 5 frames: 1 a small white flash at the center; 2 a bright cyan four-pointed splash star (white core, cyan arms); 3 the star at full size with 4-5 small water droplets flying outward; 4 the star breaks into droplets, turning blue; 5 a few blue droplets.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `fizz_fx_w_hit.png`：W 海石三叉戟 强化打击命中，6 帧

强化的一击：一个三叉戟形状的青绿亮光（三根尖朝上，参考 R_DmgMarker 那个三叉戟图样）在目标身上一闪，同时炸开一大圈水花和水珠，比普攻命中大一圈（参考 Q_Dash_Tar_Splash）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94) with teal (#E8FFF6, #9EF2D8, #3FD0B0, #16947E, #0A5B4A).
Effect: a SEASTONE TRIDENT STRIKE, 6 frames: 1 a white flash at the center; 2 a glowing teal TRIDENT sign (three points up, like a small trident emblem, about 60% of the cell tall) flashes at the center over a round burst of water; 3 the trident sign at full brightness, a ring of water splashes and 6-8 droplets flying outward; 4 the sign fades, the splash ring widens; 5 the splash breaks into droplets; 6 a few blue droplets.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `fizz_fx_q_hit.png`：Q 淘气打击 穿过目标的命中，5 帧

冲过去打中目标：一道往右的水流冲击（水平拉长的水花），中心一朵蓝色的水爆（参考 Q_Dash_Tar_Splash、Q_LinearSplash）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: an URCHIN STRIKE HIT, 5 frames: 1 a white flash at the center; 2 a horizontal gush of water from the left edge through the center, a round blue water burst at the center; 3 the burst at full size, foamy edges, droplets flying to the right; 4 the burst breaks into droplets; 5 a few droplets.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `fizz_fx_q_dash.png`：Q 出发点（地面，不跟随），5 帧

菲兹冲出去时留在原地的地面效果：一圈扁的水花加两三道往右拉长的水痕（他往右冲），很快散开（参考 Q_Dash_Ground、E_trail）。约 32 格宽、12 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a DASH START on the ground (a figure dashes to the RIGHT from the left part of the cell; do NOT draw the figure), 5 frames: 1 a small flat splash of water at the bottom left; 2 the water spreads flat along the ground and two or three long thin water streaks stretch from it to the right; 3 the streaks reach the right side, droplets jump; 4 the streaks thin and break; 5 a faint wet ring.
Layout: one horizontal row of 5 equal cells, each 8 wide to 3 tall, image size 2560x384 (each cell 512x384); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `fizz_fx_e_up.png`：E 起跳（地面，不跟随），5 帧

跳上三叉戟时脚下溅起的一圈水花：扁椭圆的水圈和几股往上溅的水（参考 E_Splashes）。约 24 格宽、12 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a JUMP SPLASH on the ground, 5 frames: 1 a small flat ring of water at the bottom middle (an ellipse twice as wide as tall); 2 the ring spreads and three or four short jets of water shoot up from its edge; 3 the jets at full height, droplets; 4 the jets fall back, the ring widens; 5 a faint wet ring.
Layout: one horizontal row of 5 equal cells, each 2 wide to 1 tall, image size 1536x384 (each cell 768x384); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `fizz_fx_e_slam.png`：E 砸地（大范围，地面，大图），7 帧

从三叉戟上砸下来：地上炸开一大圈水花冠（一圈往上溅的水墙），中心一圈扩散的波纹，水滴往外飞，然后落下变成一圈湿痕（参考 E_Splashes、E_LinearSplash、ripple）。宽 64 格、高 40 格，水圈底部的椭圆宽是高的 2 倍。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a BIG WATER SLAM on the ground, 7 frames: 1 a white flash at the bottom middle; 2 a flat ellipse ring of water (twice as wide as tall, filling the cell width) bursts out from the center and a crown of water walls shoots up all around its edge; 3 the crown at full height with many droplets flying out and up, ripples inside the ring; 4 the walls start to fall, droplets everywhere; 5 the water falls back into the ring; 6 a foamy ring of ripples; 7 a faint wet ring.
Layout: one horizontal row of 7 equal cells, each 8 wide to 5 tall, image size 3584x320 (each cell 512x320); the ellipse's bottom near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `fizz_fx_e_slow.png`：E 减速（敌人身上，2 秒），6 帧

被砸中减速：人形脚下一圈蓝色的水圈，几颗往下滴的水珠，身上挂着水（不要画人）。约 18 格宽、20 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a SLOW on a standing figure (do NOT draw the figure), 6 frames: 1 a flat blue ring of water appears on the ground at the bottom middle (an ellipse twice as wide as tall); 2-3 the ring spreads, drops of water fall from the figure's place down to the ring; 4-5 the drops reach the ground, small splashes; 6 faint blue drops.
Layout: one horizontal row of 6 equal cells, each 5 wide to 6 tall, image size 1920x384 (each cell 320x384); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `fizz_fx_r_fish.png`：R 扔出去的鱼（飞行，朝右），4 帧循环

飞出去的鱼：一条橙白条纹的小鱼（参考 R_fish 里的小丑鱼），头朝右，一边飞一边甩尾巴，身后几滴水珠。**上下对称**画（背鳍和腹鳍一样大），这样往左飞时转过来也一样。约 14 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a fish ramp (#FFF4E0, #FFC878, #FF8C34, #D85A18, #8C3412) with white and a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a FLYING FISH heading to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line (the fins on top and bottom the same size): a small round orange fish with two white stripes, its head and one dark eye on the right, its tail on the left flapping (up, middle, down, middle across the frames), two or three water droplets trailing behind it.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 768x128 (each cell 192x128); the fish on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `fizz_fx_r_stuck.png`：R 粘在英雄身上的鱼（2 秒），4 帧循环

鱼粘在被命中的英雄身上：同一条橙白小鱼，斜着贴在人形的胸口、尾巴乱甩，滴着水；不要画人，鱼在格子中间偏上。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a fish ramp (#FFF4E0, #FFC878, #FF8C34, #D85A18, #8C3412) with white and a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a FISH STUCK on a figure (do NOT draw the figure), 4 frames, a seamless loop: the same small round orange fish with two white stripes, stuck diagonally (head down-right) at the middle of the cell, wriggling: its tail flicks up and down across the frames, one or two water drops falling from it.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `fizz_fx_r_ring.png`：R 鲨鱼的预警（被粘住的英雄脚下，2 秒），4 帧循环

地上一圈要冒出鲨鱼的预警：深蓝的水圈，圈边一排白色的鲨鱼牙（参考 R_Decal），水圈里的水在打转，越转越急。中间留空人形。约 48 格宽、24 格高（椭圆，宽是高的 2 倍）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94) with a shark ramp (#F0F6FA, #B4CCDC, #6E90AC, #3E5C7C, #22344C, #121C2C) and white teeth.
Effect: a SHARK WARNING on the ground around a standing figure (the figure is NOT drawn), 4 frames, a seamless loop: a flat dark-blue ellipse of churning water (twice as wide as tall, filling the cell), its rim lined with a ring of white triangular SHARK TEETH pointing inward like an open jaw seen from above, ripples swirling inside it, turning a little each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x512 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `fizz_fx_r_fish_ground.png`：R 落空：鱼掉在地上（2 秒），4 帧循环

鱼没粘到人，掉在地上蹦：橙白小鱼侧躺在地上一蹦一蹦，身边一小摊水（不旋转、地面在格子底部）。约 16 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a fish ramp (#FFF4E0, #FFC878, #FF8C34, #D85A18, #8C3412) with white and a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a FISH FLOPPING on the ground, 4 frames, a seamless loop: the same small round orange fish with two white stripes lying on its side on a small puddle at the bottom of the cell; it flops: frame 1 lying, 2 its body bent up with the tail high and a splash, 3 a small hop, 4 back down.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 768x128 (each cell 192x128); the puddle at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `fizz_fx_r_shark.png`：R 巨鲨冲出（小、中、大三档，大图），3 行 × 8 帧

一张图 3 行：小、中、大三条鲨鱼，同一个动作。地上水圈炸开，一条深蓝色的大鲨鱼张着嘴从水里竖着冲出来（白肚皮、红色嘴里一圈白牙），冲到最高点咬合，再落回水里溅起水花。第 1 行小（水圈宽 48 格、鲨鱼约 36 格高），第 2 行中（60 格、约 46 格高），第 3 行大（72 格、约 56 格高）。头朝上、正对镜头偏右，不旋转。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a shark ramp (#F0F6FA, #B4CCDC, #6E90AC, #3E5C7C, #22344C, #121C2C), a maw ramp (#FFFFFF, #E8E0D0, #B03A48, #6A1828) and a water ramp (#FFFFFF, #D8F8FF, #8CE6FF, #3CC0F0, #1A84D0, #0E4A94).
Effect: a GIANT SHARK BURSTING OUT OF THE GROUND, 3 rows x 8 frames, the same motion in every row at three sizes: 1 the ground water ring (a flat ellipse twice as wide as tall) bulges and foams; 2 a big dark-blue shark snout bursts up through the middle with a crown of splashing water; 3 the shark shoots straight up out of the water, jaws wide open (a red mouth ringed with white teeth), white belly toward us; 4 at the top, jaws snapping shut; 5 jaws closed, it starts to fall back; 6 it dives back down into the water, a big splash; 7 the splash falls, foam ring; 8 a fading foam ring. Row 1 SMALL: the water ring 48 squares wide, the shark about 36 squares tall at its top; row 2 MEDIUM: the ring 60, the shark about 46; row 3 LARGE: the ring 72, the shark about 56. The ring's bottom on the same line in every row.
Layout: a grid of 8 columns x 3 rows of equal cells, each 9 wide to 8 tall, image size 4608x1536 (each cell 576x512); the water ring's center at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `fizz_fx_hit` | view_effects `league_fizz_hit`（跟随） | 14 |
| `fizz_fx_w_hit` | view_effects `league_fizz_w_hit`（跟随） | 22 |
| `fizz_fx_q_hit` | view_effects `league_fizz_q_hit`（跟随） | 20 |
| `fizz_fx_q_dash` | view_effects `league_fizz_q_dash`（施法者身上，不跟随，画在人物下面） | 32 × 12 |
| `fizz_fx_e_up` | view_effects `league_fizz_e_up`（施法者身上，不跟随，画在人物下面） | 24 × 12 |
| `fizz_fx_e_slam` | view_effects `league_fizz_e_slam`（施法者身上，不跟随，画在人物下面；大图 league_fizz_big） | 64 × 40（半径 30000） |
| `fizz_fx_e_slow` | view_effects `league_fizz_e_slow`（跟随） | 18 × 20 |
| `fizz_fx_r_fish` | view_projectiles `league_fizz_r_fish`（游戏会转到飞的方向） | 14 × 10 |
| `fizz_fx_r_stuck` | view_buffs `league_fizz_r_fish1/2/3`（跟随，在人物上面） | 16 × 16 |
| `fizz_fx_r_ring` | view_buffs `league_fizz_r_ring1/2/3`（跟随，画在人物下面） | 48 × 24 |
| `fizz_fx_r_fish_ground` | view_effects `league_fizz_r_fish_ground`（地面，不跟随） | 16 × 10 |
| `fizz_fx_r_shark` | view_effects `league_fizz_r_shark1`、`r_shark2`、`r_shark3`（地面上，不跟随，在人物上面；大图 league_fizz_big） | 48 / 60 / 72 宽 |

- 鲨鱼三档按 R 的半径缩放（24000 / 30000 / 36000 = 水圈宽 48 / 60 / 72 格），落空的大鲨鱼用第 3 行；预警圈跟着鱼的档位（`r_ring1/2/3`，和 `r_fish1/2/3` 一起加）。
- 清掉 Codex 给水花描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单。
- 鱼是 `LinearProjectile` 的画面（朝右，上下对称）；Q 出发点、E 起跳和砸地、预警圈画在人物下面（`z` −1）；鲨鱼在人物上面。
