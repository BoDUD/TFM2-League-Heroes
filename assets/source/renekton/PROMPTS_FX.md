# 荒漠屠夫 雷克顿：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/renekton_design.png`，8 倍，41 行、65 格宽）。
> - 大小对照 `design/renekton_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。雷克顿 65×41 格。每条写的大小都是游戏像素（格）。
> - `design/renekton_shots.png`：定稿动作（4 倍），青色十字是特效的起点（刀刃中点、站位点），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里雷克顿自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版皮肤：**刀光是象牙白；怒气（满怒气、强化技能、大招）是红橙色；冲刺和大招的沙暴是沙黄色；眩晕的星星是金色**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **围着人的刀光圈、怒气、沙暴只画外圈，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：游戏不会翻转特效图片，只翻转人物的动作帧。所以：打中目标的（`a_hit`、`q_hit`、`e_hit`、`w_hit`、`r_burn`）、画在他身上的（`q_spin`、`q_spin_e`、`w_glow`、`r_cast`）和挂着循环的（`f5`、`w_stun`、`e_shred`、`r_on`）都要**每一帧严格左右对称**（逐格对称）。只有 `a_slash`（普攻刀光）和 `e_dash`（冲刺风痕）是朝右的：它们会烘进动作帧里，跟着人物一起翻转。
> - 特效照下面第 1–15 条和「所有特效图的规则」画，每张一个 PNG，文件名 `renekton_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。
> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`renekton_fx_done.zip`）放在 outputs 里，或放在 `outputs/renekton-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「怒之领域」 | 挥刀攻击，积攒怒气；满怒气时下一个技能被强化 | `a_slash` · `a_hit` · `f5` |
| 技能 1 = Q「巨鳄狂袭」 | 横扫一圈、回血；强化时更大更红 | `q_spin` · `q_spin_e` · `q_hit` |
| 技能 2 = E「横冲直撞」→ W「冷酷捕猎」 | 冲过去砍，接连劈两刀眩晕（强化三刀、晕更久），再冲一次（强化削甲） | `e_dash` · `e_hit` · `w_hit` · `w_glow` · `w_stun` · `e_shred` |
| 大招 = R「终极统治」 | 变身：加生命、脚下沙暴光环每半秒烫周围的敌人 | `r_cast` · `r_on` · `r_burn` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、沙、火星没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 刀光象牙白（普攻、Q、E、W）：`#FFFFFF`、`#FFF6E0`、`#F0E0B8`、`#D8C090`、`#A88C5C`；
  - 怒气红（强化、满怒气、大招）：`#FFFFFF`、`#FFE0C8`、`#FF9A5A`、`#F0502A`、`#B81E18`、`#6A0E0E`；
  - 沙暴沙黄（E、R）：`#FFF6D8`、`#F4DC98`、`#DCB460`、`#B88838`、`#84602A`；
  - 金色（眩晕星星、大招的神像符号）：`#FFFFFF`、`#FFF6C0`、`#FFE68A`、`#FCC23A`、`#C88A1C`；
- 打中的画面居中画，不旋转；地面上、绕身体的圈是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 25000，Q 半径 32000，R 光环半径 30000）。

### 1. `renekton_fx_a_slash.png`：普攻刀光（烘进普攻第 3 帧），3 帧

月牙刀砍出去的那一道刀光：一道象牙白的弧形刀光从左上扫到右前方，弧的外缘最亮（参考 BA_trail、Q_cas_swipetrail、Z_Glow_Trail）。朝右砍。3 帧：亮出、拖长、消散。约 30 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C).
Effect: a CRESCENT SLASH ARC swung to the RIGHT, 3 frames: 1 a thick bright white-ivory arc 24 squares wide curving from the upper left down to the right, its outer edge white, thinning to a point at both ends; 2 the arc longer (28 squares) and thinner, pale ivory, a few sparks at its front end; 3 the arc breaking into fading ivory streaks.
Layout: one horizontal row of 3 equal 32:20 cells, image size 1536x320 (each cell 512x320, 16 px a square); the arc's middle at the center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `renekton_fx_a_hit.png`：普攻打中（目标身上），4 帧

刀砍中：一个象牙白的 X 形十字刀痕，几粒白色火星往外溅（参考 common_HitEffect、common_color-hit-physical）。**左右对称**（X 形）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C).
Effect: a CROSS SLASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 a white X of two crossing slash marks 8 squares across at the center; 2 the X 12 squares across, ivory, 6 sparks flying out evenly on both sides; 3 the X fading, sparks farther; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `renekton_fx_q_spin.png`：Q 巨鳄狂袭：绕身一圈的刀光（脚下到腰，地上的椭圆），6 帧

Q 横扫一圈：一圈象牙白的弧形刀光绕着他转一圈，是斜上方看下去的扁椭圆（宽是高的约 3 倍），刀光前面亮、后面淡，地上扬起一点沙尘（参考 Q_cas_swipetrail、Q_cas_color-swipetrail、Q_cas_Shadow、Oriental_Dust_2x2）。**只画外圈，中间留空**（人站在中间）。**每一帧都左右对称**（不要画成转动的方向：用一整圈同时变亮再散开表现横扫）。约 64 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C) and a desert sand ramp (#FFF6D8, #F4DC98, #DCB460, #B88838, #84602A).
Effect: a SPIN SLASH RING round a figure, seen from above at an angle (a flat ellipse three times as wide as tall), 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, do NOT draw the figure; leave its place empty: 1 a thin pale ivory ellipse 40 squares wide appears at waist height; 2 the ring of blade light widens to 56 squares, a thick bright white-ivory band, brightest at its front (bottom) edge; 3 the full ring 62 squares wide, white sparks flung out on both sides, a little sand dust rising from the ground on both sides; 4 the ring thinning, the dust spreading; 5 fading streaks of ivory and sand; 6 last motes. The middle of the ellipse stays EMPTY.
Layout: one horizontal row of 6 equal 66:24 cells, image size 6336x384 (each cell 1056x384, 16 px a square); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `renekton_fx_q_spin_e.png`：Q 强化（满怒气）：更大的红色刀光圈，6 帧

满怒气的 Q：同一圈刀光，但更大、是怒气的红橙色，带一圈热浪和火星（参考 Q_cas_rage_swipetrail、Q_cas_rage_renekton_runewars_swipe、Q_cas_rage_Aura_self、Q_cas_rage_color-bellcurve32）。**只画外圈，中间留空**；**每一帧左右对称**。约 72 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E) and an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C).
Effect: an EMPOWERED SPIN SLASH RING round a figure, a flat ellipse three times as wide as tall, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, do NOT draw the figure; leave its place empty: 1 a red-orange ellipse 46 squares wide flares at waist height; 2 a thick ring of red fury light with a white-hot inner edge, 64 squares wide; 3 the full ring 70 squares wide, red and orange sparks and heat flames licking up on both sides; 4 the ring breaking into red streaks; 5 fading embers; 6 last sparks. The middle of the ellipse stays EMPTY.
Layout: one horizontal row of 6 equal 74:28 cells, image size 7104x448 (each cell 1184x448, 16 px a square); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `renekton_fx_q_hit.png`：Q 打中（每个被扫到的敌人身上），4 帧

Q 扫中：一道横着的象牙白刀痕穿过身体，两边溅出几粒火星和一点红色（参考 common_HitEffect、Q_cas_White_Tip）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C) and a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E).
Effect: a HORIZONTAL CUT HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 a white horizontal slash 10 squares long through the center; 2 the slash 12 squares, ivory, with 2 red drops and 4 sparks flying out evenly to both sides; 3 fading, sparks farther; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `renekton_fx_e_dash.png`：E 横冲直撞：冲刺的残影和沙尘（烘进冲刺的动作帧），4 帧

冲刺：他身后拖一道长长的沙色风痕和几道象牙白的速度线，脚下扬起沙尘（参考 E_cas_spiralwind、E_cas_alpha_12、Oriental_Dust_2x2）。人朝右冲，所以风痕在**左边**（身后），从站位点往左拖。4 帧：拉出、最长、散开、消失。约 34 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#FFF6D8, #F4DC98, #DCB460, #B88838, #84602A) and an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C).
Effect: a DASH STREAK behind a figure dashing to the RIGHT, 4 frames, do NOT draw the figure; leave its place empty: 1 four horizontal ivory speed lines and a band of sand-coloured wind 20 squares long trailing to the LEFT from the right edge, a puff of sand dust at the bottom; 2 the streak 32 squares long, the wind swirling, the dust cloud bigger; 3 the lines breaking up, the sand drifting; 4 fading sand motes.
Layout: one horizontal row of 4 equal 36:18 cells, image size 2304x288 (each cell 576x288, 16 px a square); the streak starts at the RIGHT edge's middle of every cell and trails left. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `renekton_fx_e_hit.png`：E 冲刺砍中（每个被穿过的人身上），4 帧

冲刺砍中：一道斜的象牙白刀痕加一团沙尘，**左右对称**（两道交叉的斜刀痕），约 12 格，居中画（参考 common_HitEffect、Oriental_Dust_2x2）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C) and a desert sand ramp (#FFF6D8, #F4DC98, #DCB460, #B88838, #84602A).
Effect: a DASH CUT HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 two crossing white diagonal slashes 10 squares across; 2 the slashes ivory with a burst of sand dust 12 squares across; 3 the dust drifting out to both sides; 4 fading dust.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `renekton_fx_w_hit.png`：W 冷酷捕猎：每一刀劈中（目标身上），4 帧

W 劈中：一道从上往下的重劈刀痕（竖的象牙白粗线），落点炸开一圈红色的冲击和火星（参考 Z_Glow_Trail、skin05_W_sub_flash、common_angstlines）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C) and a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E).
Effect: a HEAVY CHOP HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 a thick vertical white slash 14 squares tall down the center; 2 the slash ivory, a burst of red impact 14 squares across at its lower end with 6 sparks flying out evenly to both sides; 3 the red burst breaking up; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `renekton_fx_w_glow.png`：W 强化（满怒气）：身上一团红色的怒气爆发，5 帧

满怒气的 W：举刀时全身冒出一团红色怒气，向上窜的红焰和热浪（参考 Q_cas_rage_Aura_self、R_buf_renekton_runewars_flare_reddish、Renekton_runewars_hot）。**只画外圈，中间留空**；**每一帧左右对称**。约 44 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E).
Effect: a FURY FLARE round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, do NOT draw the figure; leave its place empty: 1 a red-orange glow outline round the figure's place 30 squares tall; 2 red flames licking UP on both sides, 40 squares tall, a white-hot flash at the top; 3 the flames tallest, sparks rising; 4 the flames thinning; 5 fading embers. The figure's place in the middle stays EMPTY.
Layout: one horizontal row of 5 equal square cells, image size 3680x736 (each cell 736x736, 16 px a square); the figure's place (20 squares wide, 38 tall, its soles 4 squares above the bottom) centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `renekton_fx_w_stun.png`：W 眩晕（被晕的人头顶，循环），4 帧

眩晕：头顶一圈转的金色小星星（3 颗），**每一帧左右对称**（用星星一闪一闪表现，不要画旋转）。约 14 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: STUN STARS above a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame: three small gold stars 3 squares across on a flat ellipse 14 squares wide (one at the center, one at each side); each frame the stars twinkle in turn (bigger and white, then smaller and gold).
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `renekton_fx_e_shred.png`：E 强化：被削甲的标记（目标头顶，循环），4 帧

削甲：头顶一个裂开的小盾牌（灰银色，中间一道红色裂痕），**左右对称**，红光一闪一闪。约 8 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E) and an ivory blade-light ramp (#FFFFFF, #FFF6E0, #F0E0B8, #D8C090, #A88C5C).
Effect: a CRACKED SHIELD MARK, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame: a small pale silver-ivory shield 7 squares across with a red crack down its middle; each frame the crack glows brighter and dimmer.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `renekton_fx_f5.png`：满怒气（他身上，循环），6 帧

满怒气：脚下一圈红光，身上往上冒红色的怒气火焰和热浪，在身后（参考 Passive_ring_red_03、Passive_Renekton_VG_Q_Fire_Cas、Passive_xerath_Magma_Strands）。**只画外圈，中间留空**；**每一帧左右对称**。约 48 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E).
Effect: a FULL FURY AURA behind a figure, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, do NOT draw the figure; leave its place empty: a flat red ellipse 40 squares wide on the ground at the bottom, red-orange flames and heat wisps rising on both sides of the figure's place up to 40 squares high, flickering each frame; a few embers floating up.
Layout: one horizontal row of 6 equal 50:46 cells, image size 4800x736 (each cell 800x736, 16 px a square); the ground ellipse 2 squares above the bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `renekton_fx_r_cast.png`：R 终极统治：变身爆发（他身上），8 帧

大招变身：脚下炸开一圈沙暴，一个金色的鳄鱼神（索贝克）符号在他头顶亮一下，红色怒气冲天，沙子旋转着往外扫（参考 R_cas_sobeksymbol、R_Sand_01、R_Sand_02、R_buf_renekton_runewars_transform_swirl、R_end_Geo_ConeBurst、R_Scarab）。**只画外圈，中间留空**；**每一帧左右对称**。约 72 格宽、60 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#FFF6D8, #F4DC98, #DCB460, #B88838, #84602A), a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E) and a gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: a TRANSFORMATION BURST round a figure, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, do NOT draw the figure; leave its place empty: 1 a red-gold flash at the figure's feet; 2 a ring of sand blasting outward along the ground, 40 squares wide; 3 the sand storm rising in a wide funnel on both sides, red fury flames inside it, a gold crocodile-god sigil appearing above the head; 4 the funnel tallest (56 squares), the sigil brightest; 5-6 the sand swirling outward and thinning, the sigil fading; 7-8 drifting sand and embers. The figure's place in the middle stays EMPTY.
Layout: one horizontal row of 8 equal 74:62 cells, image size 9472x992 (each cell 1184x992, 16 px a square); the funnel's base 3 squares above the bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `renekton_fx_r_on.png`：R 变身期间：脚下的沙暴光环（循环），6 帧

变身期间：脚下一圈旋转的沙暴（扁椭圆），里面红色的热浪往上冒（参考 R_AuraTwirl、R_buf_Aura_Self、R_Buff_Decal_BG、R_Sand_02）。也是伤害光环的范围。**只画外圈，中间留空**；**每一帧左右对称**（用沙粒一闪一闪表现旋转）。约 64 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#FFF6D8, #F4DC98, #DCB460, #B88838, #84602A) and a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E).
Effect: a SAND STORM AURA at a figure's feet, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, do NOT draw the figure; leave its place empty: a flat ellipse 60 squares wide of swirling sand on the ground, thick at its front (bottom) edge, red heat wisps rising from it up to 20 squares on both sides; each frame the sand grains shift and twinkle.
Layout: one horizontal row of 6 equal 66:30 cells, image size 6336x480 (each cell 1056x480, 16 px a square); the ellipse's center 6 squares above the bottom, centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `renekton_fx_r_burn.png`：R 光环烧到的敌人（目标身上），4 帧

大招光环每半秒烫一下：一小团沙尘加红色火星，**左右对称**，约 10 格，居中画（参考 R_Sand_01、Z_Speck）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sand, sparks or splashes, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert sand ramp (#FFF6D8, #F4DC98, #DCB460, #B88838, #84602A) and a fury red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #F0502A, #B81E18, #6A0E0E).
Effect: a SMALL SAND BURN, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame: 1 a red-gold spark 4 squares at the center; 2 a puff of sand 9 squares across with 4 red embers; 3 the sand drifting out; 4 fading grains.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `renekton_fx_a_slash` | 烘进普攻出手帧（`renekton_bake.json`：刀刃中点，随人物朝向翻转） | 30 × 18 |
| `renekton_fx_a_hit` | view_effects `league_renekton_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `renekton_fx_q_spin` | view_effects `league_renekton_q_spin`（画在他身上，`is_follow` false；左右对称） | 64 × 22 |
| `renekton_fx_q_spin_e` | view_effects `league_renekton_q_spin_e`（画在他身上，`is_follow` false；左右对称） | 72 × 26 |
| `renekton_fx_q_hit` | view_effects `league_renekton_q_hit`（跟随，画在人物上面；左右对称） | 12 |
| `renekton_fx_e_dash` | 烘进 E 的动作帧（`renekton_bake.json`：站位点后面，随人物朝向翻转） | 34 × 16 |
| `renekton_fx_e_hit` | view_effects `league_renekton_e_hit`（跟随，画在人物上面；左右对称） | 12 |
| `renekton_fx_w_hit` | view_effects `league_renekton_w_hit`（跟随，画在人物上面；左右对称） | 16 |
| `renekton_fx_w_glow` | view_effects `league_renekton_w_glow`（画在他身上，`is_follow` false；左右对称） | 44 × 44 |
| `renekton_fx_w_stun` | view_buffs `league_renekton_w_stun`（挂在目标头顶；左右对称） | 14 × 6 |
| `renekton_fx_e_shred` | view_buffs `league_renekton_e_shred`（挂在目标头顶；左右对称） | 8 × 8 |
| `renekton_fx_f5` | view_buffs `league_renekton_f5`（挂在他身上、画在身后；左右对称） | 48 × 44 |
| `renekton_fx_r_cast` | view_effects `league_renekton_r_cast`（画在他身上，`is_follow` false；左右对称） | 72 × 60 |
| `renekton_fx_r_on` | view_buffs `league_renekton_r_on`（挂在他身上、画在身后；左右对称） | 64 × 28 |
| `renekton_fx_r_burn` | view_effects `league_renekton_r_burn`（跟随，画在人物上面；左右对称） | 10 |

- `a_slash` 烘进普攻第 3 帧（刀刃中点：站位点前 33 格、脚底上 32 格），`e_dash` 烘进 E 的第 1–3 帧（站位点往后拖），都写在 `renekton_bake.json`，不做成特效（红色方翻转）。`q_spin`、`q_spin_e`、`w_glow`、`r_cast` 的 `is_follow` 为 false，逐格左右对称；`f5`、`r_on` 在他身后（z −1）。
- 用 `pixel_1x/` 切格（import_twitch 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比。Q 圈按半径 32000 对宽度，R 光环按 30000。
