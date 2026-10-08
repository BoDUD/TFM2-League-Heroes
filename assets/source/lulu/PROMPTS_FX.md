# 仙灵女巫 璐璐：给 Codex 的特效提示词（第 3 步）

> **这一份是 21 张特效图。** 造型和动作已定（`design/lulu_design.png`，43×44 格，8 倍）。
> - 大小对照 `design/lulu_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/lulu_shots.png`：普攻、Q、W+E 出手和 R 施法那几帧的动作（4 倍），青色十字是脚下（魔弹从法杖头飞出去）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里璐璐自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。颜色和英雄联盟一样：**粉、品红、紫色的闪粉（普攻、Q、W 变形、皮克斯），里面夹几点金色；E 的护盾是淡紫粉色；R 狂野生长是黄绿色和金色**。
> - **特效要亮**：以前魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色或淡色的芯，暗底上一眼能看见。
> - **挂在别人身上的画面游戏不会左右翻**（敌人在红色方朝左也一样画）：变形的小动物和护盾上的皮克斯都要**正面朝着我们、左右对称**。飞行的画面会转到飞行方向，所以朝右画、上下大致对称；飞向队友的皮克斯画成一团光球，免得往左飞时头朝下。
> - 特效照下面第 1–21 条和「所有特效图的规则」画，每张一个 PNG，文件名 `lulu_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`lulu_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「皮克斯，仙灵伙伴」 | 璐璐射一颗魔弹；皮克斯跟着朝同一个目标射 3 颗小飞弹 | `lulu_fx_a_bolt` · `lulu_fx_a_hit` · `lulu_fx_p_bolt` · `lulu_fx_p_hit` |
| 技能 1 = Q「闪耀长枪」 | 璐璐和皮克斯各射一道贯穿的闪粉长枪，打中的敌人减速，减速慢慢变弱 | `lulu_fx_q_lance` · `lulu_fx_q_pix` · `lulu_fx_q_hit` · `lulu_fx_q_slow2` |
| 技能 2 = W「奇思妙想」+ E「帮忙，皮克斯！」 | 把一个敌方英雄变成小动物（不能攻击、不能放技能、减速），同时皮克斯飞到身边一个队友身上，给护盾和加速 | `lulu_fx_w_bolt` · `lulu_fx_w_poly_in` · `lulu_fx_w_poly` · `lulu_fx_w_poly_out` · `lulu_fx_e_pix` · `lulu_fx_e_land` · `lulu_fx_e_on` · `lulu_fx_w_haste` |
| 大招 = R「狂野生长」 | 交战时让一个队友变大：加生命，击飞他身边的敌人，7 秒里身边的敌人减速 | `lulu_fx_r_burst` · `lulu_fx_r_hit` · `lulu_fx_r_on_in` · `lulu_fx_r_on` · `lulu_fx_r_on_out` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、闪粉、火星、光晕、烟雾没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。**例外：变形的小动物和护盾上的皮克斯是“角色”，要描一圈深紫色的边。**
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 粉色闪粉（普攻、Q、W、皮克斯的主色）：`#FFFFFF`、`#FFE6FA`、`#FFB0F0`、`#FF70E0`、`#E040D0`、`#B020B8`、`#7A1890`；
  - 紫色（皮克斯的光、护盾、魔弹的边）：`#FFFFFF`、`#E8E0FF`、`#C0B0FF`、`#9A80FF`、`#7A50F0`、`#5A30C8`、`#3A1C90`；
  - 金色（闪粉里的金点、W 给队友的加速）：`#FFFFFF`、`#FFF8D6`、`#FFE47A`、`#FFC63A`、`#FF9E21`；
  - 黄绿色（R 狂野生长）：`#FFFFFF`、`#F4FFD6`、`#DCFF8A`、`#B4F04E`、`#7CD83A`、`#4AAE2C`、`#2A7A22`；
  - 小动物的毛（只给变形的小动物）：`#FFFFFF`、`#FFE6F2`、`#F8C0DC`、`#E890C0`、`#C068A8`、`#8A4A8A`、`#5A2E66`、`#2A1430`；
- **飞行的画面朝右画，而且上下大致对称**（`a_bolt`、`p_bolt`、`q_lance`、`q_pix`、`w_bolt`、`e_pix`）：游戏会把它转到飞行方向，往左飞时整张会上下翻过来。
- **挂在人身上的画面左右对称**（`w_poly_in`、`w_poly`、`w_poly_out`、`e_on`、`w_haste`、`q_slow2`、`r_on_in`、`r_on`、`r_on_out`），按每条写的站位画；命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- **变形要盖住人**（`w_poly_in`、`w_poly`）：英雄联盟里被变形的人会整个变成小动物；游戏里换不了敌人的模型，所以用一大团烟雾把人盖住、小动物坐在烟雾前面。其他套在角色身上的特效：格子里留出空的人形位置，不要画人；护盾只画边，不要盖住人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（21 张）

21 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 长枪宽 6000，R 光环半径 22000）。

### 1. `lulu_fx_a_bolt.png`：普攻魔弹（飞行中，朝右，循环），3 帧

璐璐法杖射出的一颗魔弹：白芯的粉紫色四角星光，后面拖一小串粉色闪粉，尾巴一点紫（参考 Flare-Rainbow_pink、pink_flare、Z_trail）。星光朝右飞，上下大致对称。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and a few gold glints (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21).
Effect: a FLYING MAGIC BOLT going to the RIGHT, 3 frames, a seamless loop: a white-cored four-pointed star of pink and violet light 5 squares across at the right end, a short stream of pink glitter specks trailing 5 squares to the LEFT behind it, one gold glint; the star twinkles and the glitter flickers from frame to frame; roughly symmetric above and below the middle line.
Layout: one horizontal row of 3 equal cells, each 192x128 (image 576x128); the star on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `lulu_fx_p_bolt.png`：皮克斯的小飞弹（飞行中，朝右，循环），3 帧

皮克斯跟着射出的 3 颗小飞弹：一颗白芯的品红小光点，后面拖 2–3 格紫粉色的光尾（参考 Z_pink_flare_01、Z_sparks_bw）。比普攻魔弹小一半，朝右飞，上下对称。约 6 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890) and a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90).
Effect: a TINY FAERIE SPARK flying to the RIGHT, 3 frames, a seamless loop: a white-cored magenta dot of light 3 squares across near the right end, a thin violet-pink tail 3 squares long trailing to the LEFT; it pulses a little from frame to frame; symmetric above and below the middle line.
Layout: one horizontal row of 3 equal cells, each 128x96 (image 384x96); the spark on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `lulu_fx_a_hit.png`：普攻打中（目标身上），4 帧

魔弹打中：一下白芯的粉紫色星光，周围炸开几粒粉色、金色的闪粉（参考 E_Star_1、Flare-Rainbow_pink）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and a few gold glints (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21).
Effect: a small MAGIC BOLT HIT, 4 frames: 1 a white-pink four-pointed star flash 8 squares across; 2 the star with a ring of pink light, 5 glitter specks (pink and one gold) bursting out; 3 the specks farther out, the light dimming to violet; 4 two fading specks.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `lulu_fx_p_hit.png`：皮克斯飞弹打中（目标身上），3 帧

皮克斯的小飞弹打中：一个小小的品红光点闪一下，迸出 3 粒紫色闪粉。约 8 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890) and a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90).
Effect: a TINY SPARK HIT, 3 frames: 1 a white-magenta dot flash 4 squares across; 2 three violet glitter specks pop out; 3 the specks fading.
Layout: one horizontal row of 3 equal cells, each 128x128 (image 384x128); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `lulu_fx_q_lance.png`：Q 闪耀长枪：璐璐的贯穿魔弹（飞行中，朝右，循环），4 帧

Q 射出一道闪闪发光的长枪：白芯的粉紫色光束，前头一颗亮星，身后拖一长串粉色、紫色、几点金色的闪粉，像一道彩色的亮片流（参考 Q_Shape、W_Trail、Z_dragontrainer_glitter、Flare-Rainbow_pink）。朝右飞，上下大致对称。约 20 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and a few gold glints (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21).
Effect: a GLITTERING LANCE flying to the RIGHT, 4 frames, a seamless loop: a bright white-cored beam of pink and violet light 12 squares long ending in a four-pointed star at the right, a long stream of pink, violet and a few gold glitter specks trailing 8 squares further to the LEFT and spreading a little; the specks twinkle and drift from frame to frame; roughly symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 384x160 (image 1536x160); the lance on the middle line of every cell, its star near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `lulu_fx_q_pix.png`：Q 皮克斯的那一道（飞行中，朝右，循环），4 帧

皮克斯跟着射出的第二道：和璐璐那道一样的闪粉长枪，小一号、更偏紫、更淡一点（英雄联盟里两道并排飞）。朝右飞，上下大致对称。约 16 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890) and a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90).
Effect: a SMALLER GLITTERING LANCE flying to the RIGHT, 4 frames, a seamless loop: like a slimmer copy of a pink lance - a white-cored violet-pink beam 9 squares long ending in a small star at the right, violet and pink glitter trailing 7 squares to the LEFT; paler and more violet than pink; twinkling from frame to frame; roughly symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 320x128 (image 1280x128); the lance on the middle line of every cell, its star near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `lulu_fx_q_hit.png`：Q 打中（目标身上），5 帧

长枪穿过敌人：一下白芯的粉色星光爆开，几颗小紫星和一圈闪粉往外散（参考 E_Star_1、Z_dragontrainer_glitter）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and a few gold glints (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21).
Effect: a GLITTER BURST HIT, 5 frames: 1 a white-pink star flash 10 squares across; 2 a ring of pink glitter bursts out round it, 3 tiny violet stars flying out; 3 the glitter ring at full size (14 squares), gold glints; 4 the glitter drifting out and dimming; 5 a few fading specks.
Layout: one horizontal row of 5 equal cells, each 256x256 (image 1280x256); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `lulu_fx_q_slow2.png`：Q 减速（敌人脚下，循环），4 帧

被长枪减速的敌人脚边：一圈慢慢转的粉紫色闪粉和两三颗小星星，贴着地面（参考 Z_dragontrainer_slowrings、Z_dust）。只画闪粉，左右对称，不要盖住人。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890) and a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90).
Effect: a LOOPING SLOW SPARKLE at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse of pink and violet glitter specks (16 x 6 squares) slowly circling on the ground round the feet, 2-3 tiny stars twinkling in it; left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 288x128 (image 1152x128); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `lulu_fx_w_bolt.png`：W 奇思妙想：变形魔弹（飞行中，朝右，循环），4 帧

变形魔法飞向敌方英雄：一团旋转的粉紫色和金色闪粉，中间一颗白亮的星，后面拖一点彩色亮片（参考 W_Trail、Z_flare-Rainbow_pink、Z_orbelectron）。朝右飞，上下大致对称。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and a few gold glints (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21).
Effect: a WHIRLING SPELL BOLT flying to the RIGHT, 4 frames, a seamless loop: a spinning ball of pink, violet and gold glitter 7 squares across near the right end with a bright white star in its middle, the glitter swirling round the star a quarter turn each frame, a few coloured specks trailing 4 squares to the LEFT; roughly symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 224x160 (image 896x160); the ball on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `lulu_fx_w_poly_in.png`：W 变形：烟雾冒出来（敌人身上），4 帧

敌方英雄被变成小动物的一瞬间：一团粉紫色的魔法烟雾“砰”地冒出来，把人整个罩住，烟里闪着亮片，最后一帧烟雾上坐着一只小动物（同下一条的小动物）。烟雾要大，能把一般英雄（约 40 格高）大半个盖住。左右对称（敌人朝哪边都一样画）。约 32 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and, for the critter only, a fur ramp (#FFFFFF, #FFE6F2, #F8C0DC, #E890C0, #C068A8, #8A4A8A, #5A2E66, #2A1430) with a 1-square dark plum outline round the critter.
Effect: a MAGIC PUFF that swallows a figure (do NOT draw the figure), 4 frames: 1 a white-pink flash at the middle of the cell; 2 a big round puff of pink and violet magic smoke bursts out, 28 squares wide and 30 tall, glitter and small stars in it; 3 the puff at full size, billowing, covering the middle of the cell; 4 the puff settling a little lower, and a small cute critter (the one described in the next effect) popping out sitting on the front of the puff. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 512x576 (image 2048x576) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `lulu_fx_w_poly.png`：W 变形中：小动物（敌人身上，循环），6 帧

变形的 1.75 秒：英雄联盟里被变形的人会变成一只可爱的小动物。我们没法把敌人的模型换掉，所以画一团低一点的粉紫烟雾把人的下半身和身体盖住，烟雾前面坐着一只**正面朝着我们的小动物**：圆滚滚、毛茸茸，像小松鼠，大耳朵、大眼睛、一条卷起来的大尾巴，奶油粉色和紫色的毛（这只小动物要描一圈深紫色的边，和角色一样；烟雾和闪粉不描边）。小动物一跳一跳、尾巴晃，烟雾慢慢翻滚，头上冒几颗小星星。左右对称。烟雾约 28 格宽、24 格高，小动物约 12 格宽、12 格高。6 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and, for the critter only, a fur ramp (#FFFFFF, #FFE6F2, #F8C0DC, #E890C0, #C068A8, #8A4A8A, #5A2E66, #2A1430) with a 1-square dark plum outline round the critter.
Effect: a LOOPING POLYMORPH over a figure (do NOT draw the figure - the smoke hides it), 6 frames, a seamless loop: a billowing cloud of pink and violet magic smoke 28 squares wide and 24 tall covering the middle and lower part of the cell, glitter twinkling in it; in front of the smoke, at its lower middle, a small CUTE CRITTER sitting and FACING THE VIEWER: round and fluffy like a little squirrel, 12 squares wide and 12 tall, big ears, big shiny eyes, a big curled tail, cream-pink and lilac fur with a plum outline (the critter only is outlined, like a character); it hops 1 square up and down and its tail sways, the smoke rolls slowly, 2-3 tiny stars twinkle over it. Left-right symmetric overall.
Layout: one horizontal row of 6 equal cells, each 448x512 (image 2688x512) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `lulu_fx_w_poly_out.png`：W 变形结束：烟雾散开（敌人身上），4 帧

变形结束：小动物“噗”地一下不见了，烟雾往四周散开变成闪粉，露出下面的人。左右对称。约 32 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and, for the critter only, a fur ramp (#FFFFFF, #FFE6F2, #F8C0DC, #E890C0, #C068A8, #8A4A8A, #5A2E66, #2A1430) with a 1-square dark plum outline round the critter.
Effect: the POLYMORPH ENDING (do NOT draw the figure), 4 frames: 1 a white-pink flash where the critter sat (the critter gone), the smoke cloud still there; 2 the smoke bursts outward into big puffs, thinning in the middle; 3 the puffs at the cell's edges breaking into pink and violet glitter, the middle empty; 4 a few fading specks. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 512x576 (image 2048x576) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `lulu_fx_e_pix.png`：E 帮忙皮克斯！：飞向队友的皮克斯（飞行中，朝右，循环），4 帧

皮克斯飞到队友身边：画成一团发光的小光球（皮克斯飞得太快，看不清身体），白芯、紫粉色的光，四周四道翅膀似的淡紫光芒一闪一闪，后面拖一串亮片（参考 Z_flare-Rainbow_pink、Z_dragontrainer_glitter）。因为游戏会把它转到飞行方向，所以**上下对称，不要画成有头有脚的皮克斯**。朝右飞。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890) and a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90).
Effect: a FLYING FAERIE LIGHT going to the RIGHT, 4 frames, a seamless loop: a glowing ball of light 6 squares across near the right end, white core, pink and violet glow, four pale lilac wing-like glints flicking round it (up and down alternately), a trail of glitter specks 5 squares to the LEFT; no body, no face - symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 224x160 (image 896x160); the light on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `lulu_fx_e_land.png`：E 皮克斯落到队友身上（目标身上），5 帧

皮克斯落到队友身边、护盾张开的一下：胸口一下粉紫色的闪光，一圈淡紫色的光环从身上扩开，几颗小星星和亮片往上飘（参考 E_Circle_normal、E_Sparks、E_Star_1）。中间是人，不要画人。左右对称。约 20 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and a few gold glints (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21).
Effect: a SHIELD SPARKLE on a figure (do NOT draw the figure), 5 frames: 1 a white-pink flash at chest height (the middle of the cell); 2 a ring of pale violet light spreads out from the chest, 4 small stars pop out; 3 the ring at full size (18 x 24 squares, an upright oval round the body), pink glitter rising; 4 the ring fading, the glitter higher; 5 a few fading specks. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 320x416 (image 1600x416); centered in every cell (the figure's chest at the middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `lulu_fx_e_on.png`：E 护盾持续：皮克斯和护盾（队友身上，循环），6 帧

护盾在队友身上的时候：身边一圈淡紫粉色的护盾边（**只画边，里面空着**，左右两边亮），边上闪着小亮片；皮克斯在队友头顶上方飘着：**正面朝着我们**的小仙灵，深色小身体、发品红光的小脸、一对淡紫色的翅膀上下扇（翅膀一帧上一帧下），身后掉一点闪粉（参考 E_Circle_normal、Z_ShieldEdge、E_Sparks）。皮克斯画小（身体 4 格、翅膀展开 10 格宽）。左右对称。中间是人，不要画人，别盖住人。6 帧无缝循环。护盾约 24 格宽、36 格高，整张约 28 × 44 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890), a violet ramp (#FFFFFF, #E8E0FF, #C0B0FF, #9A80FF, #7A50F0, #5A30C8, #3A1C90) and a few gold glints (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21).
Effect: a LOOPING FAERIE SHIELD round a figure (do NOT draw the figure; leave the whole inside EMPTY - draw only the rim and the faerie), 6 frames, a seamless loop: the rim of an upright oval shield round the figure (24 x 36 squares), 1 square of pale violet-pink light thick, brightest at the sides, small glitter specks running round it; above the figure's head, at the top middle of the cell, a TINY FAERIE hovering and FACING THE VIEWER: a dark plum body 2 squares wide and 4 tall, a glowing magenta face, two pale lilac insect wings spread 10 squares wide that flap up and down every frame, a little glitter falling from it; the faerie bobs 1 square. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 448x704 (image 2688x704) (16 px a square here); the figure's feet 4 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `lulu_fx_w_haste.png`：W 奇思妙想（对队友）：加速（队友身上，循环），4 帧

皮克斯同时给队友加速：脚边一圈金色、粉色的小光点绕着转，两三颗小星星往上飘一点（英雄联盟奇思妙想给队友时的金粉色闪光）。只画光点，左右对称，不要盖住人。约 20 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21) and a pink glitter ramp (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890).
Effect: a LOOPING HASTE SPARKLE at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a ring of small gold and pink motes (an ellipse 18 x 6 squares) circling round the feet, 2-3 tiny gold stars drifting up a little from it; left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 320x160 (image 1280x160); the ellipse's middle 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `lulu_fx_r_burst.png`：R 狂野生长：队友变大的一下（目标身上），7 帧

大招放到队友身上、队友变大的一下（游戏里没法把模型放大，就靠这一下撑场面）：队友身上一下白金绿色的闪光，一圈大大的金绿色光环往外炸开，一道光柱从脚下往上冲，绿色、金色的光点和几片小叶子、粉色亮片往上往外飞，整个比人大一圈（参考 R_IndicatorRing、BlastRing、Z_Shockwave、Z_GlowFlare）。中间是人，不要画人。左右对称。约 44 格宽、52 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a lime-green ramp (#FFFFFF, #F4FFD6, #DCFF8A, #B4F04E, #7CD83A, #4AAE2C, #2A7A22), a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21) and a few pink glints (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890).
Effect: a GROWTH BURST round a figure (do NOT draw the figure; leave its place empty), 7 frames: 1 a white-green flash at the figure's chest; 2 a column of lime-green and gold light shoots up from the feet to the top of the cell, a big ring of green light bursts out round the figure; 3 the ring at full size (40 squares wide), green and gold motes, a few small leaves and pink glitter flying up and out; 4 the column at full height and brightness, an outline of light swelling round the figure's place as if it grew; 5 the ring breaks into motes, the column thins; 6 leaves and motes drifting; 7 a few fading motes. Left-right symmetric.
Layout: one horizontal row of 7 equal cells, each 352x416 (image 2464x416) (8 px a square here); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `lulu_fx_r_hit.png`：R 击飞（敌人身上），5 帧

被变大的队友击飞的敌人身上：一道金绿色的光从脚下往上冲，几片小叶子和光点跟着旋上去（参考 R_IndicatorMult、Z_Shockwave）。中间是人，不要画人。左右对称。约 16 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a lime-green ramp (#FFFFFF, #F4FFD6, #DCFF8A, #B4F04E, #7CD83A, #4AAE2C, #2A7A22), a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21) and a few pink glints (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890).
Effect: an UPWARD BURST HIT on a figure (do NOT draw the figure), 5 frames: 1 a white-green flash at the bottom middle; 2 a burst of lime-green and gold light shoots up 20 squares from the bottom, 3 small leaves swirling up with it; 3 the streak at full height, gold motes; 4 the streak fading, the leaves at the top; 5 fading motes. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 256x416 (image 1280x416); the figure's feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `lulu_fx_r_on_in.png`：R 光环展开（队友脚下），4 帧

变大后的 7 秒，队友脚下有一个减速光环（游戏里就是减速的范围）：这一条是光环从脚下展开的那一下——一圈金绿色的光从中间扩开成大椭圆。从斜上方看的椭圆（宽是高的 2 倍）。左右对称。约 48 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a lime-green ramp (#FFFFFF, #F4FFD6, #DCFF8A, #B4F04E, #7CD83A, #4AAE2C, #2A7A22), a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21) and a few pink glints (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890).
Effect: a GROUND AURA OPENING at a figure's feet (do NOT draw the figure), 4 frames: 1 a small bright green-gold ellipse at the middle of the cell; 2 a ring of lime-green light spreads out (an ellipse 30 x 15 squares); 3 the ring at full size (an ellipse 44 x 22 squares), 1-2 squares thick, gold sparkles on it; 4 the ring settles, a faint green glow filling it. Left-right symmetric; an ellipse seen from above at an angle (twice as wide as tall).
Layout: one horizontal row of 4 equal cells, each 384x192 (image 1536x192) (8 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `lulu_fx_r_on.png`：R 光环持续（队友脚下，循环），6 帧

光环持续：地上一个金绿色的大椭圆光环（44 × 22 格，边 1–2 格粗），环上几片小叶子和金色、粉色的亮片绕着转，环里一层淡淡的绿光，边上往上冒几点光（参考 R_IndicatorRing、R_IndicatorMult、Z_InnerRing）。左右对称。6 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a lime-green ramp (#FFFFFF, #F4FFD6, #DCFF8A, #B4F04E, #7CD83A, #4AAE2C, #2A7A22), a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21) and a few pink glints (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890).
Effect: a LOOPING GROUND AURA at a figure's feet (do NOT draw the figure), 6 frames, a seamless loop: a ring of lime-green light on the ground (an ellipse 44 x 22 squares, 1-2 squares thick), a faint green glow inside it, a few small leaves and gold and pink glints circling along the ring (a sixth of the way each frame), 2-3 motes rising a little from its edge. Left-right symmetric; an ellipse seen from above at an angle.
Layout: one horizontal row of 6 equal cells, each 384x192 (image 2304x192) (8 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `lulu_fx_r_on_out.png`：R 光环消失（队友脚下），4 帧

7 秒到了光环消失：环碎成金绿色的光点，往上飘着散掉。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glitter, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a lime-green ramp (#FFFFFF, #F4FFD6, #DCFF8A, #B4F04E, #7CD83A, #4AAE2C, #2A7A22), a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21) and a few pink glints (#FFFFFF, #FFE6FA, #FFB0F0, #FF70E0, #E040D0, #B020B8, #7A1890).
Effect: a GROUND AURA FADING at a figure's feet (do NOT draw the figure), 4 frames: 1 the full ring (an ellipse 44 x 22 squares) flashing brighter; 2 the ring breaking into green and gold motes; 3 the motes drifting up and out; 4 a few fading motes. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 384x192 (image 1536x192) (8 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `lulu_fx_a_bolt` | view_projectiles `league_lulu_a_bolt`（循环，朝飞行方向转） | 10 × 6 |
| `lulu_fx_p_bolt` | view_projectiles `league_lulu_p_bolt`（循环，朝飞行方向转，一次 3 颗） | 6 × 4 |
| `lulu_fx_a_hit` | view_effects `league_lulu_a_hit`（跟随，画在人物上面） | 12 |
| `lulu_fx_p_hit` | view_effects `league_lulu_p_hit`（跟随，画在人物上面） | 8 |
| `lulu_fx_q_lance` | view_projectiles `league_lulu_q_lance`（循环，朝飞行方向转） | 20 × 8 |
| `lulu_fx_q_pix` | view_projectiles `league_lulu_q_pix`（循环，朝飞行方向转，比璐璐那道高一点飞） | 16 × 6 |
| `lulu_fx_q_hit` | view_effects `league_lulu_q_hit`（跟随，画在人物上面） | 16 |
| `lulu_fx_q_slow2` | view_buffs `league_lulu_q_slow2`（循环，画在人物上面） | 18 × 8 |
| `lulu_fx_w_bolt` | view_projectiles `league_lulu_w_bolt`（循环，朝飞行方向转） | 12 × 8 |
| `lulu_fx_w_poly_in` | view_buffs `league_lulu_w_poly`（ThreePhase 的 pre：变形开始） | 32 × 36 |
| `lulu_fx_w_poly` | view_buffs `league_lulu_w_poly`（ThreePhase 的 loop：变形中，画在人物上面） | 28 × 32 |
| `lulu_fx_w_poly_out` | view_buffs `league_lulu_w_poly`（ThreePhase 的 remove：变回来） | 32 × 36 |
| `lulu_fx_e_pix` | view_projectiles `league_lulu_e_pix`（循环，朝飞行方向转） | 12 × 8 |
| `lulu_fx_e_land` | view_effects `league_lulu_e_land`（跟随，画在人物上面） | 20 × 26 |
| `lulu_fx_e_on` | view_buffs `league_lulu_e_on`（循环，画在人物上面） | 28 × 44 |
| `lulu_fx_w_haste` | view_buffs `league_lulu_w_haste`（循环，画在人物上面） | 20 × 10 |
| `lulu_fx_r_burst` | view_effects `league_lulu_r_burst`（BIG，跟随，画在人物上面） | 44 × 52 |
| `lulu_fx_r_hit` | view_effects `league_lulu_r_hit`（跟随，画在人物上面） | 16 × 26 |
| `lulu_fx_r_on_in` | view_buffs `league_lulu_r_on`（ThreePhase 的 pre，BIG，画在人物下面） | 48 × 24 |
| `lulu_fx_r_on` | view_buffs `league_lulu_r_on`（ThreePhase 的 loop，BIG，画在人物下面） | 48 × 24 |
| `lulu_fx_r_on_out` | view_buffs `league_lulu_r_on`（ThreePhase 的 remove，BIG，画在人物下面） | 48 × 24 |

- `w_poly_in` / `w_poly` / `w_poly_out` 是同一个 ThreePhase buff（`league_lulu_w_poly`，z 2，盖在人物上面）的三段；`r_on_in` / `r_on` / `r_on_out` 是 `league_lulu_r_on`（z -1，画在人物下面）。
- 魔弹的出生高度按 `design/lulu_shots.png` 里法杖头的位置定（`y_offset`），归位的子弹不要高过目标中心 8 格以上（凯特琳的教训）。
- R 的击飞和光环现在在施法那一刻就生效，`ult` 动作第 3 帧（tick 7）才是举杖：导入时把 R 的效果往后挪 7 tick，和动作对上。
- 清掉 Codex 给光和闪粉描的最深色边（`import_riven.py` 的 `unrim` 做法，小动物和皮克斯除外）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
