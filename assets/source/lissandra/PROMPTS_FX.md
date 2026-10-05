# 冰霜女巫 丽桑卓：给 Codex 的特效提示词（第 3 步）

> **这一份是 21 张特效图。** 造型和动作已定（`design/lissandra_design.png`，8 倍，42 行）。
> - 大小对照 `design/lissandra_size.png`：定稿造型放大 4 倍，裙摆在红线上，上面是 10 格一段的刻度，右边是原版冰法师。丽桑卓 27×42 格。每条写的大小都是游戏像素（格）。
> - `design/lissandra_shots.png`：Q 第 4 帧、E 第 2 帧（手）和 W、R、冻自己的定稿动作（4 倍），青色十字是手或脚下的位置（导入时 Claude 把特效放到这里）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里丽桑卓自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟：**冰锥、冰环、冰爪、冰墓是白色和浅蓝的冰，带白色高光；被动的冰仆、冰墓周围的冰爆和冰地是她自己的黑冰（深蓝、钢蓝的冰晶，和她裙摆上的冰晶一样）；手上的光是青色**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见；黑冰也要有钢蓝亮边和白色闪光，不能糊成一块黑。
> - **冰块、冰墓套在人身上时只画冰的边、棱和高光，中间留空**，不然会把人整个挡住（游戏里冰块画在人物上面）。
> - 特效照下面第 1–21 条和「所有特效图的规则」画，每张一个 PNG，文件名 `lissandra_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`lissandra_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 射出一颗小冰弹 | `lissandra_fx_a_bolt` · `lissandra_fx_a_hit` |
| 被动「冰脉驱役」 | 她击杀的敌方英雄化成冰仆，1.5 秒后碎裂，炸伤周围敌人并减速 | `lissandra_fx_p_thrall` · `lissandra_fx_p_burst` · `lissandra_fx_slow` |
| 技能 1 = Q「寒冰碎片」 | 一根直线飞行的冰锥，穿过路上的敌人，伤害并减速 | `lissandra_fx_q_cast` · `lissandra_fx_q_shard` · `lissandra_fx_q_hit` · `lissandra_fx_slow` |
| 技能 2 = W「冰霜之环」+ E「冰川之径」 | 身边炸开冰环，伤害并定身；身边没人时先掷出冰爪，滑过去再放冰环 | `lissandra_fx_w_ring` · `lissandra_fx_w_hit` · `lissandra_fx_w_root` · `lissandra_fx_e_cast` · `lissandra_fx_e_claw` · `lissandra_fx_e_hit` · `lissandra_fx_e_port` |
| 大招 = R「冰封陵墓」 | 冻住敌方英雄（冰墓、周围冰爆、留下减速冰地）；被围时冻住自己 2.5 秒（无敌、回血） | `lissandra_fx_r_cast` · `lissandra_fx_r_tomb` · `lissandra_fx_r_burst` · `lissandra_fx_r_field` · `lissandra_fx_r_self_cast` · `lissandra_fx_r_stasis` · `lissandra_fx_slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、寒雾、雪花、拖尾没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的冰（冰锥、冰晶、冰块、冰爪、冰仆）是物体，有 1 格深色描边（`#0B0A14`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 白蓝的冰（冰锥、冰环、冰爪、冰墓）：`#FFFFFF`、`#E2F6FF`、`#A8E4FF`、`#5CC0F8`、`#2A84E0`、`#1A4AA0`；
  - 寒雾、雪花：`#FFFFFF`、`#E6F8FF`、`#B4E6FA`、`#78C8F0`；
  - 手上的青光：`#FFFFFF`、`#C8F4FF`、`#7AD8FF`、`#40B4FF`、`#1E78D0`；
  - 她的黑冰（冰仆、冰爆、冰地）：`#C8D4FF`、`#7F9CDA`、`#4A64A8`、`#2C3C70`、`#1B1F42`、`#0F1028`；
- **飞行物朝右画，而且上下对称**（`a_bolt`、`q_shard`、`e_claw`）：游戏会把它转到出招方向，朝左时整张会上下翻转。
- **从手上发出的特效朝右画，起点在格子左边的中点**（`q_cast`、`e_cast`）；画在她身上或脚下的画面（`w_ring`、`e_port`、`r_cast`、`r_self_cast`、`r_stasis`）按每条写的站位画，脚在格子底部往上 8 格的中间。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上或脚下的循环画面（`slow`、`w_root`、`r_tomb`、`r_stasis`）左右对称或不分左右，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（21 张）

21 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：冰环半径 26000、冰地半径 30000、冰仆碎裂半径 25000）。

### 1. `lissandra_fx_a_bolt.png`：普攻飞出去的冰弹（飞行中循环），4 帧

普攻射出的一颗小冰弹：一枚尖尖的冰晶（像小冰锥）往右飞，后面拖一小段白蓝色的霜雾（参考 Spear_Diff、ba_crystal、Trail_Smoke）。冰晶是物体，有 1 格深色描边；霜雾没有。上下对称。约 12 格长、6 格高（冰晶约 6 × 4 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a FLYING ICE BOLT moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a small pointed ice crystal (6 squares long, 4 tall, pale blue facets with a white edge, a 1-square dark outline) pointing right, a short white-blue frost streak 6 squares long trailing behind it to the LEFT that flickers each frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the crystal at the RIGHT half, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `lissandra_fx_a_hit.png`：普攻打中（目标身上），4 帧

冰弹打中：一下白蓝色闪光，几片碎冰往外飞（参考 hitsparks、Q_impact_01、Blue_Flare_Flash）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: an ICE HIT, 4 frames: 1 a white flash with a pale blue rim; 2 a small four-pointed star of white-blue light 10 squares across, 4 tiny ice chips (outlined) flying out; 3 the star fading, chips further out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `lissandra_fx_q_cast.png`：Q 出手：手上的寒气（施法者身上），4 帧

Q「寒冰碎片」出手的一瞬间：她伸出的爪手前面炸开一团白蓝色的寒气和雪花，往右喷（参考 E_cas、Blue_Flare_Flash、W_Flurrys）。朝右画：手在格子左边中点。约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glow ramp (#FFFFFF, #C8F4FF, #7AD8FF, #40B4FF, #1E78D0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a FROST CAST FLASH at a hand, pointing RIGHT, 4 frames: 1 a cyan-white star at the LEFT MIDDLE of the cell (the hand); 2 a cone of white-blue frost and snowflakes bursts to the right from that point; 3 the frost spreads further right and thins; 4 fading snowflakes.
Layout: one horizontal row of 4 equal 4:3 cells, image size 1024x192 (each cell 256x192); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `lissandra_fx_q_shard.png`：Q 飞出去的冰锥（飞行中循环），4 帧

Q 飞出去的一根大冰锥（判定宽约 14 格）：长长的尖冰晶往右飞，冰锥本体是浅蓝和白色的几个切面，后面拖一道白蓝色的霜雾和碎冰屑（参考 Spear_Diff、Q_mis_Sidewall、Q_Fog、lissandra_Q_flakes）。冰锥有描边，霜雾没有。上下对称。约 26 格长、12 格高（冰锥约 14 × 7 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a FLYING ICE SHARD moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a long pointed spear of ice 14 squares long and 7 tall (faceted: a white top facet, pale blue sides, a deeper blue core line, a 1-square dark outline) pointing right; a white-blue frost trail 12 squares long behind it to the LEFT with 4 tiny ice flakes that shift each frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the shard at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `lissandra_fx_q_hit.png`：Q 冰锥打中（目标身上），5 帧

冰锥打中：冰锥碎成几块尖冰往外飞，中间一下白色闪光和一圈寒气（参考 Q_impact_02、Q_Blastback、Q_bubble_impact、ShardFlashBlue）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a SHATTERING SHARD, 5 frames: 1 a white flash; 2 a burst of 6 sharp ice shards (outlined) flying outward from the center, a ring of white-blue frost 12 squares across; 3 the shards further out, the frost spreading; 4 the shards small, snowflakes; 5 fading flakes.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `lissandra_fx_slow.png`：减速：脚下的霜（循环），4 帧（Q、R 冰地、冰仆三处减速共用）

被冻住减速的敌人脚下：地上一圈白蓝色的霜，几根小冰刺和飘起来的雪花（参考 color_lissandra_q_slow、FrostGround、W_Flurrys）。中间是人，不要画人。左右对称，4 帧无缝循环。约 18 格宽、7 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a FROST SLOW MARK at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a flattened ellipse of white-blue frost on the ground round the feet (twice as wide as tall), 4 tiny ice spikes on its rim, 3 snowflakes drifting up a square each frame.
Layout: one horizontal row of 4 equal 5:2 cells, image size 2560x256 (each cell 640x256); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `lissandra_fx_w_ring.png`：W 冰霜之环：身边炸开的冰环（地面上，以她为中心），6 帧

W 的冰环：以她为中心，地上一圈冰刺猛地冒出来（从斜上方看是扁椭圆，宽是高的 2 倍，范围半径约 26 格），冰刺是白蓝色的尖冰晶，圈里一层寒雾和冰裂纹（参考 W_Nova_Ground、W_Cracks、W_Rocks、W_Flurrys、lissandra_w_praxisWave_tex）。中间是人的位置，不要画人。约 60 格宽、34 格高（地上 56 × 28 的椭圆加上往上冒的冰刺）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a RING OF FROST ON THE GROUND seen from above at an angle, round a figure (do NOT draw the figure; leave its place empty), 6 frames: 1 a white flash on the ground at the center; 2 a ring of white-blue frost expands over a flattened ellipse twice as wide as tall (56 squares wide); 3 at the ellipse's edge a ring of sharp ice spikes (outlined, 4-6 squares tall, pale blue with white tips) shoots up, frost cracks inside; 4 the spikes at full height, snow bursting off them; 5 the spikes crack, frost mist; 6 the spikes shatter into flakes and fade.
Layout: one horizontal row of 6 equal 30:17 cells, image size 2880x272 (each cell 480x272); the ellipse's center 8 squares (64 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `lissandra_fx_w_hit.png`：W 打中：冰冻（目标身上），4 帧

被冰环打中：一下白蓝色闪光，碎冰飞溅（参考 hitsparks、Blue_Flare_Flash）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: an ICE STRIKE, 4 frames: 1 a white-blue flash; 2 a burst of white-blue light 12 squares across with 5 ice chips (outlined) flying out; 3 chips further out, frost; 4 fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `lissandra_fx_w_root.png`：W 定身：冻住脚的冰（目标脚下，循环），4 帧

被冰环定住的敌人：脚下冒出一丛冰晶把脚冻住（几根往上的尖冰，白蓝色带描边，参考 crystal_root、W_Root_Fog、ba_crystal），冰面轻轻闪光。中间是人，冰晶在人的前面和两边，只到小腿高。左右对称，4 帧无缝循环。约 20 格宽、12 格高，底边贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: an ICE ROOT at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a cluster of 7 sharp ice crystals (outlined, pale blue with white edges) rising from the ground round the feet up to shin height (10 squares tall in the middle, lower to the sides), a frost ellipse under them; a white glint wandering over the crystals each frame.
Layout: one horizontal row of 4 equal 5:3 cells, image size 2560x384 (each cell 640x384); the crystals' base at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `lissandra_fx_e_cast.png`：E 掷出冰爪：手上的寒光（施法者身上），4 帧

E「冰川之径」出手：手前一下青白色的光和雪花往右甩出（参考 E_cas、E_Swirl_Wispy）。朝右画：手在格子左边中点。约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glow ramp (#FFFFFF, #C8F4FF, #7AD8FF, #40B4FF, #1E78D0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a CLAW-THROW FLASH at a hand, pointing RIGHT, 4 frames: 1 a cyan-white star at the LEFT MIDDLE of the cell; 2 a sweep of cyan light curling to the right with snowflakes; 3 the sweep stretched further right, thinning; 4 fading flakes.
Layout: one horizontal row of 4 equal 4:3 cells, image size 1024x192 (each cell 256x192); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `lissandra_fx_e_claw.png`：E 飞出去的冰爪（飞行中循环），4 帧

E 的冰爪：一只由尖冰晶组成的爪子（三根弯曲的冰爪尖，朝右）贴着地面往右滑，后面留下一道冰晶的小路（一排小冰刺），带寒雾（参考 E_Crystal、E_GroundCrystal、E_End_fire、Spear_Diff）。爪子有描边。上下对称。约 22 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0), a glow ramp (#FFFFFF, #C8F4FF, #7AD8FF, #40B4FF, #1E78D0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a FLYING ICE CLAW moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a claw of three curved ice talons (outlined, pale blue with white edges, a cyan glow at the palm) pointing right, 10 squares long; behind it to the LEFT a trail of small ice spikes and white-blue frost 12 squares long, the spikes shifting each frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the claw at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `lissandra_fx_e_hit.png`：E 冰爪划过（目标身上），4 帧

冰爪划过敌人：三道白蓝色的斜爪痕一闪，碎冰飞溅（参考 R_Mark_Swipe、hitsparks）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a CLAW SLASH, 4 frames: 1 three diagonal white-blue slash lines appear (12 squares long); 2 the slashes at full brightness, 4 ice chips flying; 3 the slashes thin and fade, frost; 4 fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `lissandra_fx_e_port.png`：E 滑到冰爪那里：落地的冰晶（施法者脚下，不跟随），5 帧

她顺着冰路滑到冰爪的位置：落地的地方地面冒出一圈冰晶、炸开寒雾（参考 E_End_fire、E_GroundCrystal、Snow_Dirt_Spike）。中间是人，不要画人。脚在格子底部往上 8 格的中间。约 34 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: an ICY ARRIVAL at a figure's place (do NOT draw the figure; leave its place empty), 5 frames: 1 a white-blue flash on the ground at the feet; 2 a ring of frost on the ground (an ellipse twice as wide as tall, 30 squares wide) and a column of white-blue mist rising; 3 small ice crystals (outlined) jut up round the feet, snow bursting; 4 the mist thins, the crystals crack; 5 fading flakes.
Layout: one horizontal row of 5 equal 17:15 cells, image size 2040x360 (each cell 408x360); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `lissandra_fx_r_cast.png`：R 冰封陵墓施放：举起的手（施法者身上），5 帧

冻住敌人的那一下：她身边卷起一圈青白色的寒风和雪花，往前扑（参考 R_LensFlash、R_flurries、R_Mark_Swipe、R_Ground_Flare）。中间是人，不要画人。脚在格子底部往上 8 格的中间。约 40 格宽、50 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glow ramp (#FFFFFF, #C8F4FF, #7AD8FF, #40B4FF, #1E78D0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a FREEZING GUST round a figure (do NOT draw the figure; leave its place empty), 5 frames: 1 a cyan-white flash high above the figure's head (her raised hands); 2 a spiral of white-blue wind and snow sweeping down round the figure; 3 the gust sweeps forward to the RIGHT at chest height; 4 snow flying right; 5 fading flakes.
Layout: one horizontal row of 5 equal 4:5 cells, image size 1600x400 (each cell 320x400); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `lissandra_fx_r_tomb.png`：R 冻住敌人：冰墓（目标身上，1.5 秒循环），4 帧

被冰封陵墓冻住的敌方英雄：整个人被包在一块高高的冰块里（冰块是几个大切面，白蓝色半透明感，用浅色的面和白色的高光边画出来，**中间留出能看见人的地方**：只画冰块的边、棱和高光，不要把人整个涂满），脚下一圈冰（参考 R_IceBlock_Diff、R_IceShard_Animated、IceBlock）。冰块有描边。左右对称或不分左右。4 帧无缝循环（高光在冰面上慢慢移动）。约 30 格宽、44 格高，底边贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: an ICE TOMB encasing a figure (do NOT draw the figure; leave its place empty - the tomb is drawn as a frame of ice round the empty middle so the figure stays visible inside), 4 frames, a seamless loop: a tall jagged block of ice 30 squares wide and 44 tall standing on the ground: thick faceted ice edges on both sides and a jagged crown of ice shards on top (outlined, pale blue and white facets), only thin pale facet lines across the middle, ice crystals at its base; a white glint sliding down the facets over the loop.
Layout: one horizontal row of 4 equal 15:22 cells, image size 960x352 (each cell 240x352); the block's base at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `lissandra_fx_r_burst.png`：R 冰墓炸开：周围的冰爆（地面上），6 帧

冰墓成形的同时周围炸开：地上一圈深色的冰（她的黑冰：深蓝、钢蓝色的冰晶）猛地冒出来，冰裂纹往外蔓延，冰屑飞溅（参考 R_Burst、R_Nova_Ground、R_Slice_Cracks、R_groundChunks）。范围半径约 26 格。中间是人的位置，不要画人。约 56 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-ice ramp (#C8D4FF, #7F9CDA, #4A64A8, #2C3C70, #1B1F42, #0F1028), an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a BLACK-ICE ERUPTION ON THE GROUND seen from above at an angle, round a figure (do NOT draw the figure; leave its place empty), 6 frames: 1 a white-blue flash at the center; 2 dark ice cracks race outward over a flattened ellipse twice as wide as tall (52 squares wide); 3 jagged dark navy and steel-blue ice crystals (outlined, white glints) burst up along the cracks, 6-8 squares tall; 4 ice chunks flying out, frost; 5 the crystals crack; 6 fading flakes and frost.
Layout: one horizontal row of 6 equal 14:9 cells, image size 2688x288 (each cell 448x288); the ellipse's center 8 squares (64 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `lissandra_fx_r_field.png`：R 冰地：减速的黑冰地面（地面上，3 秒循环），4 帧

冰墓留下的一片冰地：地上一个扁椭圆的黑冰面（深蓝色的冰，上面一道道发青光的冰裂纹，边缘几簇小冰晶），范围半径约 30 格，慢慢闪光（参考 R_Cracks、R_Cracks_Glow、FrostGround、R_groundChunks_growFlat）。贴着地面，不往上冒。4 帧无缝循环。约 60 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-ice ramp (#C8D4FF, #7F9CDA, #4A64A8, #2C3C70, #1B1F42, #0F1028) and a glow ramp (#FFFFFF, #C8F4FF, #7AD8FF, #40B4FF, #1E78D0).
Effect: a FROZEN GROUND FIELD seen from above at an angle, 4 frames, a seamless loop: a flattened ellipse twice as wide as tall (60 squares wide) of dark navy ice with branching cyan-glowing cracks across it and small dark ice crystals (outlined) round its rim; the cracks' glow pulses brighter and dimmer over the loop. Flat on the ground.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `lissandra_fx_r_self_cast.png`：R 冻自己：冰块成形（施法者身上），4 帧

她把自己冻住的一瞬间：脚下冰晶从地面往上一层层长，把她包起来（参考 R_SelfCast_Swipe、R_IceBlock_Diff、R_flurries）。中间是人，不要画人，**冰只画边和棱，留出能看见她的地方**。脚在格子底部往上 8 格的中间。约 34 格宽、50 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: an ICE BLOCK FORMING round a figure (do NOT draw the figure; leave its place empty; the ice is drawn as edges and facets so the figure stays visible), 4 frames: 1 ice crystals burst up round the feet, snow swirling; 2 the ice climbs to the waist on both sides; 3 to the shoulders; 4 a full tall jagged block of ice (outlined, pale blue and white facets) closes round the figure's place, a white flash on its top.
Layout: one horizontal row of 4 equal 17:25 cells, image size 1088x400 (each cell 272x400); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `lissandra_fx_r_stasis.png`：R 冻自己：冰块（施法者身上，2.5 秒循环），4 帧

她冻在冰块里的 2.5 秒：和 r_self_cast 最后一帧同一个冰块，高光在冰面上慢慢移动，偶尔飘几颗雪花。**中间留出能看见她的地方**。4 帧无缝循环。约 34 格宽、50 格高，底边贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E2F6FF, #A8E4FF, #5CC0F8, #2A84E0, #1A4AA0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: an ICE BLOCK round a figure (do NOT draw the figure; leave its place empty; edges and facets only, the middle open), 4 frames, a seamless loop: the same tall jagged block of ice as the last frame of r_self_cast (34 squares wide, 50 tall, outlined), a white glint sliding along its facets, 2 snowflakes drifting.
Layout: one horizontal row of 4 equal 17:25 cells, image size 1088x400 (each cell 272x400); the block's base at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `lissandra_fx_p_thrall.png`：被动「冰脉驱役」：冰仆（敌方英雄倒下的地方，1.5 秒），8 帧

她击杀的敌方英雄化成冰仆：一个由黑冰组成的人形（深蓝、钢蓝色的冰晶身体，没有脸，眼睛位置两点青光，身上冰晶尖刺，参考 Passive_black_water_spike、Passive_Pillar_Glow、P_Freeze、LissandraDeath）。前 3 帧从地面的冰里站起来，4–7 帧站着微微晃动、冰晶上的青光一明一暗，第 8 帧冰身裂开发出青白色的光（马上要碎）。冰仆是物体，有描边。约 26 格宽、40 格高，脚在格子底部往上 8 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-ice ramp (#C8D4FF, #7F9CDA, #4A64A8, #2C3C70, #1B1F42, #0F1028) and a glow ramp (#FFFFFF, #C8F4FF, #7AD8FF, #40B4FF, #1E78D0).
Effect: an ICE THRALL rising, 8 frames: a hunched humanoid figure made of dark navy and steel-blue ice crystals (outlined, jagged ice spikes on its shoulders and back, no face - two small cyan glowing eyes), 22 squares tall; 1 a dark ice patch on the ground with crystals jutting; 2 the thrall rising waist-high out of the ice; 3 standing, arms hanging; 4-7 standing, swaying a square, the cyan glow in its cracks pulsing; 8 bright cyan-white cracks split its body.
Layout: one horizontal row of 8 equal 13:20 cells, image size 1664x320 (each cell 208x320); its feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `lissandra_fx_p_burst.png`：被动冰仆碎裂：黑冰爆炸（地面上），6 帧

冰仆碎开：黑冰碎块往四周炸开，中间青白色的闪光，地上一圈冰霜扩散（范围半径约 25 格，参考 Passive_Shockwave_Scroll、P_AOE_Indicator、R_Burst、Q_impact_02）。约 50 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, glows or sparks (only solid ICE - shards, crystals, blocks, the thrall - gets a 1-square dark outline #0B0A14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black-ice ramp (#C8D4FF, #7F9CDA, #4A64A8, #2C3C70, #1B1F42, #0F1028), a glow ramp (#FFFFFF, #C8F4FF, #7AD8FF, #40B4FF, #1E78D0) and a frost ramp (#FFFFFF, #E6F8FF, #B4E6FA, #78C8F0).
Effect: a BLACK-ICE SHATTER, 6 frames: 1 a cyan-white flash where the thrall stood (22 squares tall column of light); 2 dark ice chunks (outlined) explode outward in all directions, a white-blue shock ring expanding on the ground (a flattened ellipse twice as wide as tall); 3 the ring at 48 squares wide, the chunks flying further; 4 chunks falling, frost; 5 the ring fading, small crystals left on the ground; 6 fading frost.
Layout: one horizontal row of 6 equal 25:17 cells, image size 2400x272 (each cell 400x272); the ellipse's center 8 squares (64 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `lissandra_fx_a_bolt` | view_projectiles `league_lissandra_a_bolt`（朝右，游戏转到飞行方向，上下对称） | 12 × 6 |
| `lissandra_fx_a_hit` | view_effects `league_lissandra_a_hit`（跟随，画在人物上面） | 12 |
| `lissandra_fx_q_cast` | view_effects `league_lissandra_q_cast`（施法者身上，跟随第一 tick；格子左边中点放到 Q 第 4 帧的手） | 16 × 12 |
| `lissandra_fx_q_shard` | view_projectiles `league_lissandra_q_shard`（朝右，游戏转到飞行方向，上下对称） | 26 × 12 |
| `lissandra_fx_q_hit` | view_effects `league_lissandra_q_hit`（跟随，画在人物上面） | 16 |
| `lissandra_fx_slow` | view_buffs `league_lissandra_q_slow` / `r_slow` / `p_slow`（同一张，循环，画在脚下） | 18 × 7 |
| `lissandra_fx_w_ring` | view_effects `league_lissandra_w_ring`（BIG，施法者身上，第一 tick 跟随，画在人物下面）和 `w_ring_late`（同一张，E 落地时，不跟随） | 60 × 34 |
| `lissandra_fx_w_hit` | view_effects `league_lissandra_w_hit`（跟随，画在人物上面） | 14 |
| `lissandra_fx_w_root` | view_buffs `league_lissandra_w_root`（循环，画在脚下，1.25 秒） | 20 × 12 |
| `lissandra_fx_e_cast` | view_effects `league_lissandra_e_cast`（施法者身上，跟随第一 tick；格子左边中点放到 E 第 2 帧的手） | 16 × 12 |
| `lissandra_fx_e_claw` | view_projectiles `league_lissandra_e_claw`（朝右，游戏转到飞行方向，上下对称） | 22 × 12 |
| `lissandra_fx_e_hit` | view_effects `league_lissandra_e_hit`（跟随，画在人物上面） | 14 |
| `lissandra_fx_e_port` | view_effects `league_lissandra_e_port`（BIG，画在她落地的位置，不跟随） | 34 × 30 |
| `lissandra_fx_r_cast` | view_effects `league_lissandra_r_cast`（BIG，施法者身上，不跟随） | 40 × 50 |
| `lissandra_fx_r_tomb` | view_buffs `league_lissandra_r_tomb`（BIG，循环，画在人物上面） | 30 × 44 |
| `lissandra_fx_r_burst` | view_effects `league_lissandra_r_burst`（BIG，画在冰墓的位置，不跟随） | 56 × 36 |
| `lissandra_fx_r_field` | view_projectiles `league_lissandra_r_field`（BIG，地面上，画在人物下面） | 60 × 30 |
| `lissandra_fx_r_self_cast` | view_effects `league_lissandra_r_self_cast`（BIG，施法者身上，不跟随） | 34 × 50 |
| `lissandra_fx_r_stasis` | view_buffs `league_lissandra_r_stasis`（BIG，循环，画在人物上面） | 34 × 50 |
| `lissandra_fx_p_thrall` | view_effects `league_lissandra_p_thrall`（BIG，画在尸体的位置，不跟随） | 26 × 40 |
| `lissandra_fx_p_burst` | view_effects `league_lissandra_p_burst`（BIG，画在冰仆的位置，不跟随） | 50 × 34 |

- `slow` 一张导成 `q_slow`、`r_slow`、`p_slow` 三个标签；`w_ring` 一张导成 `w_ring`、`w_ring_late` 两个标签。
- 施法者身上的画面按 `design/lissandra_shots.png` 的十字把格子的起点挪过去；晚于第一 tick 播放的（`e_port`、`r_cast`、`r_self_cast`、`w_ring_late`）`is_follow` 为 false（红方方向）。
- 飞行物第一帧前加一个空帧（出生那一 tick 画面朝上）；`r_tomb`、`r_stasis` 画在人物上面，冰只画边；`r_field` 是投射物视图（地面，人物下面）。
- 清掉 Codex 给光和寒雾描的最深色边（`import_riven.py` 的 `unrim`，实心冰保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。
