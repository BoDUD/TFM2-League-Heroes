# 瑟提（腕豪）：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型和动作已定（`design/sett_design.png`，8 倍，耳尖到鞋底 42 格，26 格宽）。
> - 大小对照 `design/sett_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，10 格一段的刻度；橙色箭头是 W 的出拳距离（从他身上往前 50 格），地上的橙色椭圆是 R 砸地的范围（52 × 26 格）。每条写的大小都是游戏像素（格）。
> - `design/sett_shots.png`：用到特效的几帧定稿动作（4 倍），青色十字是特效的中心（导入时 Claude 把特效放到这里）：待机时两只拳头（强化拳的金光）、E 第 6 帧两手对撞、W 第 5 帧出拳、R 砸地第 2 帧拳头落地。
> - 画风参考 `style/vi_effects.png`：包里蔚的特效（用户认可的，拳击手的命中、护盾、砸地），**只参考它的画法、大小和亮度，颜色按下面写的**。
> - 颜色照英雄联盟的瑟提：**拳头、命中、W 巨拳、E 对撞用橙金色**；W 的护盾用银白色；豪意满时的热浪用橙红色；R 砸地的土石用土黄色。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。**套在人身上的特效中间要空着**（护盾只画外壳的边和高光，拳光和热浪不挡人）。
> - 特效照下面第 1–14 条和「所有特效图的规则」画，每张一个 PNG，文件名 `sett_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**（上一步你用代码拼的动作碎成了杂点，最后用的是你的生图原稿）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`sett_fx_done.zip`）放在 outputs 里，**生图原稿一起交**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「沙场豪情」 | 左右拳交替：左拳刺拳，右拳重拳更快更重 | `sett_fx_a_hit` · `sett_fx_a2_hit` |
| 技能 1 = E「强手裂颅」（并入 Q「屈人之威」） | 双臂张开，把两边的敌人拽过来对撞（两边都有人时眩晕）；之后接下来两拳变成强化拳（拳头发金光，多打目标最大生命的伤害） | `sett_fx_e_hit` · `sett_fx_e_smash` · `sett_fx_q_glow` · `sett_fx_q_hit` |
| 技能 2 = W「蓄意轰拳」 + 豪意 | 挨打攒豪意（最多 5 层），蓄力后往前轰出一记巨拳：中线真伤，两侧物理伤害；同时得到护盾；豪意 4–5 层时脚下冒热浪 | `sett_fx_w_fist` · `sett_fx_w_true` · `sett_fx_w_hit` · `sett_fx_w_shield` · `sett_fx_grit` |
| 大招 = R「叹为观止」 | 抓住敌方英雄往前扔，自己跳过去砸地，砸到周围的敌人 | `sett_fx_r_grab` · `sett_fx_r_slam` · `sett_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击、火星、护盾、热浪没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。只有砸地坑里的土块和碎石可以有一格暗边。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的第四档，第五档（最深）只给很少的点缀。
- 颜色（按每条写的用）：
  - 橙金（拳头的光、命中、W 巨拳、E 对撞、强化拳）：`#FFFFFF`、`#FFF2C2`、`#FFCC4D`、`#F59A1E`、`#B85712`；
  - 银白（W 的护盾）：`#FFFFFF`、`#EEF1F6`、`#C9CEDB`、`#959CB0`、`#626A82`；
  - 橙红（豪意的热浪、R 砸地的火圈）：`#FFE6A8`、`#FFAA40`、`#F2662A`、`#C23A1E`、`#7A1E16`；
  - 土黄（R 砸地的裂地、土块、尘土）：`#F2DDB8`、`#CBA676`、`#94704A`、`#604834`、`#3C2C22`；
- 命中、闪光居中画；地面上的圈和坑是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（`q_glow`、`w_shield`、`grit`）**左右对称**，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人；也不要画敌人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `sett_fx_a_hit.png`：普攻·左拳刺拳打中，4 帧

左拳刺拳打中：一个小小的橙金色冲击星，三四道往外射的短速度线，几颗火星。约 12 格，不要太大（普攻每秒一下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: a SMALL PUNCH HIT (a jab), 4 frames: 1 a white flash 4 squares across at the center; 2 a white-gold four-pointed impact star 10 squares across, 3-4 short orange speed lines bursting out from it; 3 the star breaking into orange-gold sparks flying outward, the lines thinner; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sett_fx_a2_hit.png`：普攻·右拳重拳打中（更重），5 帧

右拳重拳打中：比刺拳大一号、更重，橙金色的冲击爆开，外面一圈橙色的冲击环，火星往外飞。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: a HEAVY PUNCH HIT (a cross), 5 frames: 1 a white flash 6 squares across; 2 a white-gold burst 12 squares across with 6 jagged rays; 3 an orange shock ring 16 squares across round a fading gold core, orange sparks flying out; 4 the ring thinner and broken, the sparks further out; 5 a few fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sett_fx_q_glow.png`：屈人之威：两只拳头上的金色拳光（他身上，循环），4 帧

E 之后接下来两拳是强化拳，这段时间他两只拳头上冒金色的光焰（英雄联盟的瑟提 Q：拳头发金光）。画在他身上，左右对称：**格子左右两边各一团拳头大小的金色光焰（约 6 × 8 格），两团中心相距 20 格，中间空着**（人在中间，不要画人和拳头）。光焰往上飘，4 帧无缝循环。整张约 30 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: GLOWING FISTS (do NOT draw the fists or the figure; draw only the glow round where two fists are), 4 frames, a seamless loop, symmetric left and right: in every cell two small golden flames, each about 6 squares wide and 8 tall, their centers 20 squares apart on the cell's middle row (one left of center, one right), each a white-gold core with orange tongues licking upward and 1-2 gold sparks rising above it; the tongues and sparks move up a little each frame. The middle of the cell between the two flames stays EMPTY.
Layout: one horizontal row of 4 equal cells, each 2 wide by 1 tall (512x256), image size 2048x256; the pair of flames centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sett_fx_q_hit.png`：强化拳打中，5 帧

强化拳打中：一记沉重的金色爆击，白芯、金色的拳形冲击（一个往外冲的拳头剪影一闪），外面一圈金环，金色碎片四溅（参考英雄联盟 Q 打中的金色爆光）。约 22 格，比普攻明显大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: an EMPOWERED PUNCH HIT, 5 frames: 1 a bright white flash 8 squares across; 2 a golden fist-shaped burst (the silhouette of a punching fist, white-gold, 12 squares) bursting toward the right with a big white-gold star behind it; 3 a gold ring 22 squares across round it, golden shards flying out in all directions; 4 the ring breaking up, the shards further out, the fist shape fading; 5 a few fading gold sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sett_fx_e_hit.png`：E 拽到的敌人身上，4 帧

E 把两边的敌人拽过来时，打在每个被拽的人身上：白金色的一下闪光，一道横向的冲击线（被拽向瑟提的方向，左右对称画就行），几颗火星。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: a GRAB HIT, 4 frames, symmetric left and right: 1 a white flash 5 squares across; 2 a white-gold impact star 10 squares across with a horizontal streak 14 squares long through it; 3 the star breaking into orange sparks, the streak thinner; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sett_fx_e_smash.png`：E 两手对撞（施法者身上，大图），5 帧

E 第 6 帧他双拳在胸前对撞（`design/sett_shots.png` 的十字）：两手之间白光一爆，橙金色的冲击往左右两边炸开成两道弧形冲击波，火星飞散（英雄联盟 E 两边的人撞在一起的那一下）。约 26 格宽，居中画，不画人。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: a CLAP SHOCKWAVE (two fists smashed together at the center; do NOT draw the fists), 5 frames: 1 a white flash 6 squares across at the center; 2 a white-gold starburst 14 squares across with long horizontal rays; 3 two curved orange-gold shockwave crescents bursting out to the left and to the right, 24 squares apart at their tips, sparks flying; 4 the crescents further out and thinner, 26 squares apart, the core fading; 5 a few fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sett_fx_w_fist.png`：W 蓄意轰拳：巨拳冲击（技能画面，大图），3 行 × 3 帧 = 9 帧

W 的画面沿出拳方向铺在地上：**画成朝右**，游戏会把整张转到出拳方向；格子左端是瑟提（出拳的人站在这里，不画他），往右 50 格是打得到的最远处。前 4 帧是蓄力时地上的预警：一个从左往右张开的扇形（从左端 4 格高张到右端约 36 格高），淡淡的橙色，越来越亮；第 5 帧轰出：一个巨大的半透明金色拳头（约 14 × 12 格，白金色的拳形，指节朝右）从左边冲出，后面拖着橙金色的冲击；第 6–7 帧拳头和冲击波一路扫到右端，扇形冲击越来越宽；第 8–9 帧散成火星和光尘。**上下对称**（往左出拳时整张会倒过来）。整张约 60 × 40 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: a GIANT FIST PUNCH SHOCKWAVE travelling to the RIGHT, symmetric top and bottom (the cell's middle row is its axis), the puncher stands at the LEFT end of every cell (do NOT draw him), 9 frames read left to right, top to bottom: 1 a faint orange fan-shaped warning on the ground opening to the right, from 4 squares tall at the left end to 36 squares tall at the right end, only its edges and a few dashes drawn; 2-3 the same fan a little brighter, a few gold sparks gathering at its left end; 4 the fan bright orange, a white-gold glow gathering at the left end; 5 THE PUNCH: a huge translucent white-gold FIST (14 squares wide, 12 tall, knuckles to the right) bursting out of the left end, a golden shock cone behind it; 6 the fist halfway along, the cone widening to 30 squares; 7 the fist at the right end, a wide golden shockwave arc 36 squares tall there; 8 the fist and the arc breaking into gold and orange sparks; 9 a few fading sparks and light dust.
Layout: three rows of 3 equal cells, each 3 wide by 2 tall (384x256), image size 1152x768; the axis on every cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sett_fx_w_shield.png`：W 的护盾（他身上，三段：出现、持续、消失），3 行 × 4 帧

W 轰拳时他得到一个护盾（最多 3 秒）：罩住他全身的银白色护壳（英雄联盟瑟提 W 的灰白护盾），边上亮、中间透明，几颗金色火星。**只画护壳的边和几处高光，中间一定要空着**（人要看得见），不要画人。第 1 行出现（从胸口一圈光涨成整个护壳，4 帧）；第 2 行持续（壳边的光慢慢流动，4 帧无缝循环）；第 3 行消失（护壳碎成几块银白色碎片落下、散开，4 帧）。左右对称。约 36 格宽、48 格高（他 26×42 格），护壳的中心在格子中间偏下（底部往上 22 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shields or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver ramp (#FFFFFF, #EEF1F6, #C9CEDB, #959CB0, #626A82) with a few sparks from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: a SILVER SHIELD SHELL round a standing muscular figure (do NOT draw the figure; the inside of the shell stays EMPTY - only its rim and a few highlights are drawn; symmetric left and right), 3 rows of 4 frames: ROW 1 (appear): 1 a white ring 6 squares across at the chest (14 squares up from the bottom of the shell); 2 the ring 16 squares across; 3 the shell half formed, 30 squares wide; 4 the full shell: a rounded rim 36 squares wide and 46 tall, 1-2 squares thick, white at the top left fading to grey-silver at the bottom right, a white highlight arc at the top left, 2-3 small gold sparks on it. ROW 2 (hold, a seamless loop): the full shell, a bright band of light sliding round the rim a quarter of the way each frame, the gold sparks twinkling. ROW 3 (break): 1 the rim cracks into 6-8 silver plates; 2 the plates falling apart and outward; 3 small silver shards and gold sparks falling; 4 a few fading shards.
Layout: three horizontal rows of 4 equal square cells each, image size 1536x1152 (each cell 384x384); the shell's center 22 squares up from the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sett_fx_w_true.png`：W 中线的真实伤害打中，5 帧

W 巨拳的正中间打到的人受到真实伤害：一下白得发亮的冲击，白金色的十字星（真伤是白色的），一圈金色的冲击环。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712), mostly its white and pale shades.
Effect: a TRUE DAMAGE HIT, 5 frames: 1 a pure white flash 8 squares across; 2 a big white four-pointed star 18 squares across with long thin rays, a pale gold glow round its core; 3 a gold ring 20 squares across round a fading white core; 4 the ring breaking into pale gold sparks; 5 a few fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sett_fx_w_hit.png`：W 两侧打中，4 帧

W 巨拳两侧扫到的人：橙色的冲击和一小团尘土。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712) and a few dust squares from (#F2DDB8, #CBA676, #94704A).
Effect: a SHOCKWAVE HIT, 4 frames: 1 a white flash 5 squares across; 2 an orange-gold burst 12 squares across with short rays; 3 the burst breaking into orange sparks, a small puff of pale dust under it; 4 a few fading sparks and dust.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sett_fx_r_grab.png`：R 抓住敌方英雄（目标身上），4 帧

R 一开始抓住英雄：目标身上两道金色的弧（像两只手合拢抓住）一合，白金色一闪。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, shockwaves or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712).
Effect: a GRAB, 4 frames, symmetric left and right: 1 two curved golden arcs (like two hands) 18 squares apart, left and right of the center, curving inward; 2 the arcs closing in to 10 squares apart, brighter; 3 they meet: a white-gold flash 12 squares across at the center, gold sparks; 4 the flash fading into a few sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `sett_fx_r_slam.png`：R 砸地大坑（施法者脚下，画在人物下面，大图），3 列 × 2 行 = 6 帧

R 落地砸下去：地上炸开一个大坑。从斜上方看的椭圆（宽是高的 2 倍），约 64 × 32 格：一圈橙红色的火光冲击环往外扩，地面裂开放射状的裂缝（土黄色），土块和碎石往外飞，尘土扬起；最后剩下一个裂开的坑慢慢淡掉。**画在地上，不画人**（他站在坑中间）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows or shockwaves (rocks and debris may have a 1-square dark edge), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fiery ramp (#FFE6A8, #FFAA40, #F2662A, #C23A1E, #7A1E16) and an earth ramp (#F2DDB8, #CBA676, #94704A, #604834, #3C2C22), white #FFFFFF for the flash.
Effect: a GROUND SLAM CRATER seen from above at an angle (every ring and crack is an ellipse twice as wide as tall), centered in the cell, nobody drawn, 6 frames read left to right, top to bottom: 1 a white-hot flash on the ground, an ellipse 16 squares wide at the center; 2 a fiery orange shock ring 40 squares wide bursting out, cracks radiating from the center, rocks and debris flying up; 3 the ring 60 squares wide and thinner, the cracks longer, a ring of earth-coloured dust; 4 the fire ring breaking up at 64 squares, dust spreading, debris falling; 5 the crater left: a cracked dark-earth ellipse 30 squares wide with glowing orange cracks, a little dust; 6 the crater faint, the cracks fading.
Layout: two rows of 3 equal cells, each 2 wide by 1 tall (512x256), image size 1536x512; the crater's center in the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `sett_fx_r_hit.png`：R 砸到周围的敌人，4 帧

R 砸地时周围被砸到的敌人身上：橙色的冲击和往上溅的土块。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows or shockwaves (small rocks may have a 1-square dark edge), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold ramp (#FFFFFF, #FFF2C2, #FFCC4D, #F59A1E, #B85712) and an earth ramp (#F2DDB8, #CBA676, #94704A, #604834).
Effect: a SLAM HIT, 4 frames: 1 a white-orange flash 6 squares across; 2 an orange burst 12 squares across, 3-4 small rocks flying up; 3 the burst fading, the rocks higher, a puff of dust; 4 a few falling rocks and fading dust.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `sett_fx_grit.png`：满豪意的热浪（他脚下，循环，画在人物下面），6 帧

豪意攒到 4–5 层（W 快满了）时，他脚下冒热浪：地上一圈淡淡的橙红色椭圆光，几缕橙红色的热气和火星往上飘到膝盖高。**左右对称、中间空着**（他站在中间，不画人）。约 32 × 22 格，椭圆在格子下部。6 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, flames or sparks, colours only from a fiery ramp (#FFE6A8, #FFAA40, #F2662A, #C23A1E, #7A1E16) - bright but thin, it sits under the figure all the time.
Effect: a HEAT AURA at a standing figure's feet (do NOT draw the figure; the middle stays EMPTY above the ground ring; symmetric left and right), 6 frames, a seamless loop: a thin glowing orange ellipse on the ground 28 squares wide and 10 tall near the bottom of the cell, and 4-6 wavy wisps of heat and small embers rising from its rim to about 12 squares above it, each wisp moving up 2 squares a frame and fading at the top while new ones start at the ring.
Layout: two rows of 3 equal cells, each 3 wide by 2 tall (384x256), image size 1152x512; the ellipse's center 6 squares up from the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定（`tools/kit/sett_kit.py`） | 大小（游戏像素） |
|---|---|---|
| `sett_fx_a_hit` | view_effects `league_sett_a_hit`（目标身上，跟随，z 2） | 12 |
| `sett_fx_a2_hit` | view_effects `league_sett_a2_hit`（同上） | 16 |
| `sett_fx_q_glow` | view_buffs `league_sett_q_1`，tag `q_glow`（循环，z 1；两团光焰对着待机两只拳头 (±10, −5)） | 30 × 16 |
| `sett_fx_q_hit` | view_effects `league_sett_q_hit`（目标身上，跟随） | 22 |
| `sett_fx_e_hit` | view_effects `league_sett_e_hit`（被拽的人身上，跟随） | 14 |
| `sett_fx_e_smash` | view_effects `league_sett_e_smash`（`league_sett_big`，施法者身上、不跟随，z 1；放到 E 第 6 帧双拳对撞的 (7, −11)，第 18 tick） | 26 |
| `sett_fx_w_fist` | view_projectiles `league_sett_w_fist`（`league_sett_big`，`LineRangeProjectile` 50000 长的画面：朝右画、居中在线的中点，左端在他身上；46 tick，第 5 帧的拳头在第 27 tick 出现，和打中、动作第 5 帧出拳同一刻） | 60 × 40 |
| `sett_fx_w_shield` | view_buffs `league_sett_w_shield`（ThreePhase：第 1 行 `w_pre`、第 2 行 `w_loop`、第 3 行 `w_remove`；z 1） | 36 × 48 |
| `sett_fx_w_true` | view_effects `league_sett_w_true`（目标身上，跟随，z 3） | 20 |
| `sett_fx_w_hit` | view_effects `league_sett_w_hit`（目标身上，跟随） | 14 |
| `sett_fx_r_grab` | view_effects `league_sett_r_grab`（被抓的英雄身上，跟随） | 18 |
| `sett_fx_r_slam` | view_effects `league_sett_r_slam`（`league_sett_big`，施法者脚下、不跟随，z −1，坑心在鞋底；落地第 4 tick） | 64 × 32 |
| `sett_fx_r_hit` | view_effects `league_sett_r_hit`（目标身上，跟随） | 14 |
| `sett_fx_grit` | view_buffs `league_sett_grit_4`、`league_sett_grit_5`，tag `grit`（循环，z −1，椭圆在鞋底） | 32 × 22 |

- 小图进 `league_sett_fx`，大图（`w_fist`、`e_smash`、`r_slam`）进 `league_sett_big`。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法，砸地的土块保留）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。
- `w_fist` 的帧长：前 4 帧共 27 tick（蓄力预警），第 5–9 帧共 19 tick；`grit`、`q_glow`、`w_loop` 循环；`r_slam` 6 帧约 0.7 秒。
