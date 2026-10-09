# 天启者 卡尔玛：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型和动作已定（`design/karma_design.png`，28×42 格，8 倍）。
> - 大小对照 `design/karma_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/karma_shots.png`：普攻甩出、Q 双掌推出、W 伸掌、E 举手、R 合十那几帧的动作（4 倍），青色十字是脚下。
> - 参考图：`refs/lol_icons.png` 是英雄联盟里她的 Q、W、R 技能图标——**颜色照它**；`refs/lol_fx_ref.png` 是她自己的特效贴图（不少是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行。两张都只在本地用。
> - 颜色：**她的灵能全是翡翠青绿色，白色的芯**（和她头上的翡翠玉环一个颜色）；**Q 心灵烈焰和灵光闪耀的火苗是洋红粉色**（和她的裙摆一个颜色），青绿和粉色交织。
> - **特效要亮**：每个形状都要有白色或最亮一档的芯，暗底上一眼能看见；最深的一档颜色只给很少的点缀。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。飞行的灵弹、火球、光束头和连线光段会转到飞行方向，所以**朝右画、上下对称**。Q 的爆开、灵光闪耀的爆开和火圈爆发是**竖着的画面**（火往上冒），上下不能颠倒。
> - 特效照下面第 1–24 条和「所有特效图的规则」画，每张一个 PNG，文件名 `karma_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`karma_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 掌心射出一道灵能飞弹 | `karma_fx_a_bolt` · `karma_fx_a_hit` |
| 技能 1 = Q「心灵烈焰」 | 双掌推出一团灵火，打中第一个敌人炸开（半径 14 格），减速 | `karma_fx_q_ball` · `karma_fx_q_boom` · `karma_fx_q_hit` · `karma_fx_q_slow` |
| 真言 Q「灵光闪耀」 | 更大的灵火，炸开后地上留一个火圈（半径 20 格），1.5 秒后整圈爆发、强减速 | `karma_fx_rq_ball` · `karma_fx_rq_boom` · `karma_fx_rq_field` · `karma_fx_rq_blast` · `karma_fx_rq_slow` |
| 技能 2 = W「坚定专注」 | 一道光束射中敌人，连线拴住 1.3 秒，没挣脱就定身 | `karma_fx_w_beam` · `karma_fx_w_tether` · `karma_fx_w_hit` · `karma_fx_w_mark` · `karma_fx_w_snap` · `karma_fx_w_root` |
| 真言 W「重焕新生」 | 她回血，定身更久 | `karma_fx_rw_heal` |
| E「鼓舞」（自动） | 给有危险的队友或自己套护盾并加速 | `karma_fx_e_land` · `karma_fx_e_on` · `karma_fx_e_haste` |
| 真言 E「不屈之心」 | 以队友为中心一圈灵光扩散（半径 30 格），周围队友都上护盾 | `karma_fx_re_wave` |
| 大招 = R「真言」 | 双手合十，强化下一个技能（最多 6 秒） | `karma_fx_r_cast` · `karma_fx_mantra` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火花、灵气没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 翡翠灵光（所有技能）：`#FFFFFF`、`#E2FFF4`、`#A8F7DC`、`#62E4BA`、`#2FC196`、`#188F6E`、`#0C5E4A`；
  - 洋红粉色火苗（Q、灵光闪耀、真言光点）：`#FFFFFF`、`#FFE2F6`、`#FFA6DE`、`#F462C4`、`#D032A2`、`#941A78`、`#5A0E4C`；
- **飞行的画面朝右画，而且上下对称**（`a_bolt`、`q_ball`、`rq_ball`、`w_beam`、`w_tether`）：游戏会把它转到飞行方向，往左时整张会上下翻过来。`w_tether` 是一节一节首尾相接连成一条线的光段：**画满格子的左右两边**，左右两头要能接上。
- **挂在人身上和地上的画面左右对称**，按每条写的站位画；命中居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。`q_boom`、`rq_boom`、`rq_blast` 是竖着的画面（火往上冒），不能颠倒。
- 套在角色身上的特效（护盾、真言光、定身、治疗）：格子里留出空的人形位置，不要画人；光罩只画边，不要盖住人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻射程约 55000，Q 爆炸半径 14000，灵光闪耀火圈半径 20000，不屈之心半径 30000）。

### 1. `karma_fx_a_bolt.png`：普攻：飞出去的灵能飞弹（朝右，循环），4 帧

掌心射出的一道小小的灵能飞弹：一根白翠色的光针，头上一点白光，外面一圈青绿色的光晕，后面拖几颗青绿色光点和一两点粉色火星（参考 Basic_Projectile、BA_Cas_Flare）。**朝右画**，上下对称（往左飞时游戏会把整张转过来）。约 10 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: a small FLYING SPIRIT BOLT pointing RIGHT, 4 frames, a seamless loop: a needle of white-jade light 6 squares long and 2 thick with a bright white tip at the right, a soft teal glow round it, a short trail of 3-4 jade motes and one or two tiny pink sparks streaming left behind it; the motes shift from frame to frame. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 192x96 (image 768x96) (16 px a square here); the needle's middle on the middle line of every cell, its tip near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `karma_fx_a_hit.png`：普攻命中：一下青绿色的灵光火花（目标身上），4 帧

飞弹打中：一下白光，一小圈青绿色的灵光和火花往外炸开，里面夹一点粉色火星。左右对称，居中画。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: a JADE SPARK HIT, 4 frames: 1 a white flash 4 squares across; 2 jade sparks and a small ring of jade light bursting out, 10 squares across; 3 the sparks farther out, thinning, a tiny pink spark among them; 4 a few fading motes. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `karma_fx_q_ball.png`：Q 心灵烈焰：飞出去的灵火球（朝右，循环），4 帧

Q 推出去的一团灵火（英雄联盟 Q 图标的样子）：前头一个白色、外面淡翠色的圆核，往后舔出几条洋红粉色的火舌，再拖一条青绿色的火焰尾巴（参考 Q_Gold、BeamShapes_Pink、Q_Trail_Fire_erosion）。**朝右画**，上下对称。约 16 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: a FLYING SPIRIT FIREBALL pointing RIGHT, 4 frames, a seamless loop: a round core 6 squares across at the front (right), white in the middle and pale jade round it; magenta-pink flame tongues licking back from it and a jade flame tail 10 squares long streaming left; the tongues flicker from frame to frame. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 320x192 (image 1280x192) (16 px a square here); the core's middle on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `karma_fx_q_boom.png`：Q 爆开：灵火在落点炸开（地上，向上冒火），6 帧

火球打中第一个敌人或飞到尽头时炸开（范围半径 14 格）：落点一下白光，一团青绿色的灵火往外炸开，洋红粉色的火舌往上蹿，地上一圈火环扩到 28 格宽，然后火苗变小、冒一点烟、剩几点余烬（参考 Q_hit_flash、Q_dash_burst、Q_Flames_Floor）。**竖着的画面**（火往上冒），上下不能颠倒。左右对称。约 28 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: a SPIRIT FLAME BURST on the ground, UPRIGHT (flames rise; never upside down), 6 frames: 1 a white-jade flash at the ground point 6 squares across; 2 a ball of jade fire 14 squares across bursting out, magenta-pink flame tongues licking up; 3 a ring of jade fire on the ground at full size (an ellipse 28 x 14 squares) with flames leaping up 10 squares and sparks flying; 4 the flames dying down, smoke wisps rising; 5 embers along the ground ring; 6 a few fading embers. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 512x448 (image 3072x448) (16 px a square here); the ground point 9 squares (144 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `karma_fx_q_hit.png`：Q 命中：被灵火烧到（目标身上），5 帧

被灵火炸到的每个敌人身上：一下白翠色的光，一团青绿色的火带着粉色火舌烧起来，火星飞散，然后变成几点余烬。左右对称，居中画。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: a SPIRIT FLAME HIT, 5 frames: 1 a white-jade flash 5 squares across; 2 a burst of jade fire with magenta-pink flame tongues 12 squares across; 3 the flames at full size (16 squares), sparks flying; 4 the flames shrinking and rising, smoke wisps; 5 a few embers. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 288x288 (image 1440x288) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `karma_fx_q_slow.png`：Q 减速：脚下一圈小灵火（循环），4 帧

被 Q 减速：脚下的地上一小圈青绿色和粉色的小火苗在跳，几颗火星往上飘。只画脚下的一圈，不要盖住人。左右对称，从斜上方看的椭圆。约 16 格宽、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: LOOPING SPIRIT EMBERS at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 16 x 5 squares of small jade and magenta-pink flames flickering on the ground, a few embers rising. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 320x128 (image 1280x128) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `karma_fx_rq_ball.png`：真言 Q 灵光闪耀：更大更亮的灵火球（朝右，循环），4 帧

带真言的 Q：比普通 Q 更大更亮的灵火球——白热的核心，一圈亮翠色的光环，更大的洋红粉色火舌，青绿和粉色交织的火焰尾巴，飞散几颗火星（参考 Q_head_core_empowered、Q_feather_glow_rainbow_empowered）。**朝右画**，上下对称。约 22 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: a BIGGER, BRIGHTER EMPOWERED SPIRIT FIREBALL pointing RIGHT, 4 frames, a seamless loop: a white-hot core 8 squares across ringed by a bright jade halo, big magenta-pink flame tongues and a jade-and-pink flame tail 14 squares long streaming left, a few sparks flying off; flickering from frame to frame. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 416x256 (image 1664x256) (16 px a square here); the core's middle on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `karma_fx_rq_boom.png`：灵光闪耀：落点炸开（地上，向上冒火），6 帧

带真言的 Q 炸开：和 Q 爆开一样，但更大更亮、粉色更多，中心一下白热的光，火环扩到 32 格宽，火往上蹿得更高。**竖着的画面**，上下不能颠倒。左右对称。约 32 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: a BIG EMPOWERED SPIRIT FLAME BURST on the ground, UPRIGHT (never upside down), 6 frames: 1 a white-hot flash at the ground point 8 squares across; 2 a ball of jade-and-pink fire 18 squares across bursting out, magenta-pink flame tongues leaping up; 3 a ring of fire on the ground at full size (an ellipse 32 x 16 squares) with flames 14 squares high and sparks flying; 4 the flames dying down, smoke wisps; 5 embers along the ring; 6 a few fading embers. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 576x512 (image 3456x512) (16 px a square here); the ground point 10 squares (160 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `karma_fx_rq_field.png`：灵光闪耀：地上留下的灵火圈（1.5 秒后爆发），8 帧

灵光闪耀炸开后地上留下一个灵火圈（半径 20 格），1.5 秒里越来越亮，然后整圈爆发：圈的边上一圈青绿色的火，沿着边跳着小小的洋红粉色火苗；圈里地面裂开青绿色发光的裂纹，从中心往外长，一帧比一帧多、一帧比一帧亮，第 8 帧整个圈底泛着淡翠色的光、边上的火最高最白（参考 Q_Groundcracks、Q_Groundcracks_Glow、Q_Flames_Floor）。左右对称，从斜上方看的椭圆（宽是高的 2 倍）。约 40 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: a CIRCLE OF SPIRIT FIRE on the ground that builds up before it blows, seen from above at an angle, 8 frames: an ellipse 40 x 20 squares; its rim a ring of jade fire with small magenta-pink flames flickering along it; inside, glowing jade cracks in the ground spreading out from the middle - frame 1 a few short cracks, every frame more and brighter cracks and taller rim flames, frame 8 the whole floor of the circle glowing pale jade and the rim flames white-hot. Left-right symmetric.
Layout: one horizontal row of 8 equal cells, each 704x384 (image 5632x384) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `karma_fx_rq_blast.png`：灵光闪耀：灵火圈整圈爆发（地上，向上冒火），6 帧

灵火圈 1.5 秒后整圈爆发：整个椭圆一下白粉色的光，沿着圈蹿起一圈青绿和洋红粉色的火墙，火墙冲到最高，火星往外飞，然后散成余烬和烟（参考 karma_blastwave）。**竖着的画面**（火往上冒），上下不能颠倒。左右对称。约 40 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: THE CIRCLE ERUPTING, UPRIGHT (never upside down), 6 frames: 1 a white-pink flash over the whole ellipse (40 x 20 squares, seen from above at an angle); 2 a wall of jade and magenta-pink flames leaping up from the ring 16 squares high; 3 the flames at full height (22 squares), sparks flying out; 4 the flames falling apart into embers and smoke; 5 smoke wisps rising, embers on the ground; 6 a few fading embers. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 704x640 (image 4224x640) (16 px a square here); the ellipse's middle 12 squares (192 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `karma_fx_rq_slow.png`：灵光闪耀减速：脚下更大的一圈灵火（循环），4 帧

被灵火圈爆发减速：和 Q 减速一样但更大更亮，粉色火苗更多。只画脚下的一圈。左右对称，从斜上方看的椭圆。约 20 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: LOOPING BRIGHT SPIRIT FLAMES at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 20 x 6 squares of jade and magenta-pink flames, taller and brighter than embers, flickering on the ground, sparks rising. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 384x160 (image 1536x160) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `karma_fx_w_beam.png`：W 坚定专注：射向敌人的灵能光束头（朝右，循环），4 帧

W 一出手，从她掌心射向敌人的一道翠绿灵光：一道直直的青绿色光束，中间一条白色的芯，最前面一个亮白翠色的光点，光束外面缠着细细的灵气（参考 karma_spiritbeam、WispTrail_Add、smoke_Trail）。**朝右画**，上下对称。约 18 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: the HEAD OF A SPIRIT BEAM pointing RIGHT, 4 frames, a seamless loop: a straight streak of jade light 18 squares long and 2 thick, white at its core, ending at the right in a bright white-jade spark 4 squares across; thin wisps curling round the streak. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 320x128 (image 1280x128) (16 px a square here); the streak on the middle line of every cell, the spark near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `karma_fx_w_tether.png`：W 连线：从敌人连回她身边的一节灵能链（朝右，循环），4 帧

W 拴住敌人的那 1.3 秒里，她和敌人之间连着一条翠绿色的灵能链。游戏里是一节一节的短光段从敌人飞回她身边，首尾相接连成一条线：所以这一张画**一节**光段——横着的一条青绿色能量带，中间一条白芯，外面缠着细细的灵气，**从格子最左边画到最右边**，左右两头能和下一节接上。上下对称。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: ONE SEGMENT OF A SPIRIT TETHER, horizontal, 4 frames, a seamless loop: a band of jade energy 10 squares long filling the cell from the left edge to the right edge (so segments laid end to end join into one long beam), 2 squares thick with a white core line, thin jade wisps twisting round it and moving right a little each frame. Symmetric above and below its middle line.
Layout: one horizontal row of 4 equal cells, each 160x96 (image 640x96) (16 px a square here); the band on the middle line of every cell, touching both side edges. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `karma_fx_w_hit.png`：W 命中：灵光缠上敌人（目标身上），4 帧

W 打中敌人：一下白光，一圈青绿色的灵光往外一炸，几缕灵气绕着打转。左右对称，居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: a SPIRIT LINK HIT, 4 frames: 1 a white flash 4 squares across; 2 a ring of jade light 10 squares across bursting out, wisps wrapping round; 3 the ring at 14 squares, the wisps curling; 4 fading motes. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x256 (image 1024x256) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `karma_fx_w_mark.png`：W 被拴住：敌人腰间一圈灵光（循环），4 帧

被连线拴住的 1.3 秒：敌人腰间绕着一圈细细的青绿色灵光（从斜上方看的椭圆），三颗小光点沿着圈转，圈的前面一点亮光一闪一闪（连线拴在这里）。只画这一圈，**中间空着**，不要盖住人。左右对称。约 20 格宽，圈离脚底 14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: A LOOPING SPIRIT MARK round a tethered figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: a thin ring of jade light round the figure's waist (an ellipse 20 x 6 squares whose middle is 14 squares above the feet), three small jade motes travelling round it, a faint jade glow pulsing at the front of the ring. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 416x512 (image 1664x512) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `karma_fx_w_snap.png`：W 定身：灵能锁扣紧（目标身上），5 帧

连线拴满 1.3 秒没挣脱，敌人被定住的那一下：脚下一圈翠绿色的光环一闪，四条短短的灵光锁链从光环往上蹿、绕着腿缠紧，一道光往上一冲，然后散成光点（参考 W_Root_Circle、W_Fire_Trail_Up）。**中间空着**，不要盖住人。左右对称。约 22 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: SPIRIT BONDS SNAPPING SHUT round a figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a bright jade ring at the figure's feet (an ellipse 22 x 8 squares) flashing white; 2 four short jade light-chains shooting up from the ring round the body to waist height; 3 the chains tightening, wrapped round the legs, sparks; 4 the chains glowing, a pulse of light up to the chest; 5 the light breaking into motes. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 416x448 (image 2080x448) (16 px a square here); the figure's feet 4 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `karma_fx_w_root.png`：W 定身中：脚下一圈翠绿光环（循环），4 帧

被定身的 1.7 秒：脚下的地上一圈亮翠色的光环，从环上长出几根短短的灵光触须围着脚，一明一暗地跳。只画脚下的一圈。左右对称，从斜上方看的椭圆。约 24 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: A LOOPING SPIRIT ROOT at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a bright jade ring on the ground (an ellipse 24 x 8 squares, 1-2 squares thick) with short jade light-tendrils rising 4 squares from it round the feet, pulsing brighter and dimmer. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 448x224 (image 1792x224) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `karma_fx_rw_heal.png`：真言 W 重焕新生：她身上的治疗光（她身上），5 帧

带真言的 W：她回一口血——胸口一团柔和的翠白色光，一颗颗青绿色的光点和四角星形的小闪光从脚下往上升，绕着身体飘到头顶散掉。**中间大部分空着**。左右对称。约 24 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: A HEALING GLOW round a figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a soft jade-white glow at chest height; 2 jade motes and small four-pointed sparkles rising round the body from the feet; 3 more sparkles higher, a ring of light at the feet; 4 the sparkles near the head; 5 a few fading sparkles above the head. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 448x640 (image 2240x640) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `karma_fx_e_land.png`：E 鼓舞：护盾罩上来（目标身上），5 帧

E 给队友或自己套上护盾的那一下：胸口一下白光，一个竖着的椭圆光罩的边缘亮起来（翠绿色，1–2 格粗），一道白光从下往上扫过光罩，光罩最亮的时候几颗光点飘起来，然后边缘变细稳定下来（参考 E_ShieldRing、E_ShieldWipe、E_Sheen）。**只画光罩的边，中间空着**，不要盖住人。左右对称。约 26 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: A SPIRIT SHIELD FORMING round a figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a white flash at chest height; 2 the rim of an upright oval bubble 26 x 34 squares appearing in jade light, 1-2 squares thick; 3 a band of white light rising over the bubble from the bottom up; 4 the rim at full brightness, a few jade motes lifting off it; 5 the rim settling, thinner. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 512x640 (image 2560x640) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `karma_fx_e_on.png`：E 护盾：罩在身上的护盾（循环），4 帧

护盾还在的时候：身上一个竖着的椭圆光罩，只有一圈淡翠色的边（1 格粗），边上几点白色高光一帧一帧沿着边慢慢转，两三颗光点在边上飘。**中间空着**，不要盖住人。左右对称（高光左右对称地转）。约 26 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: A LOOPING SPIRIT SHIELD round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: the rim of an upright oval bubble 26 x 34 squares, 1 square thick, pale jade, with white highlights that travel a little along the rim each frame (mirrored on both sides), two or three jade motes drifting on it. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 480x608 (image 1920x608) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `karma_fx_e_haste.png`：E 加速：脚下的翠绿风（循环），4 帧

护盾附带的加速：脚下一片柔和的翠绿色光，几缕青绿色的风和光点绕着脚打转往上飘（不能只往一边吹：游戏不会左右翻）。只画脚下。左右对称，从斜上方看的椭圆。约 24 格宽、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: LOOPING HASTE WISPS at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse of soft jade light 24 x 7 squares on the ground, small jade wisps and motes swirling round it and lifting off, brighter at the front. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 448x192 (image 1792x192) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `karma_fx_re_wave.png`：真言 E 不屈之心：地上扩散开的一圈灵光（地上），6 帧

带真言的 E：以被保护的队友为中心，地上一圈翠绿色的灵光往外扩散（半径 30 格），把周围的队友都罩上护盾：中心一片白翠色的光，一圈亮边往外推，圈里浮着淡淡的符文一样的光纹，扩到最大后变细淡出（参考 R_Q_TeamRing、common_Shockwave_Simple、karma_blastwave）。左右对称，从斜上方看的椭圆。约 60 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: A WAVE OF SPIRIT LIGHT spreading over the ground, seen from above at an angle, 6 frames: 1 a bright jade-white disc 8 x 4 squares at the middle; 2 a ring of jade light expanding to 24 x 12, a soft glow inside; 3 the ring at 44 x 22 with faint glyph-like lines inside; 4 the ring at 60 x 30 (its full size), bright rim; 5 the rim thinning, the inside glow fading; 6 the rim fading. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 1024x544 (image 6144x544) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `karma_fx_r_cast.png`：R 真言：她身上一下翠绿灵光（她身上），5 帧

开真言的一瞬间（她双手合十）：胸口合掌的地方一下白翠色的光，一圈光芒往外放射，脚下地上展开一圈翠绿光环，一道柔和的翠绿光柱绕着身体往上升过头顶，符文一样的光点往上飘，然后淡出（参考 R_Q_TeamRing、common_Galio_Gatekeeper_Spiritswirl、common_AirSpiritStreak）。**中间大部分空着**，不要盖住人。左右对称。约 32 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A).
Effect: THE MANTRA AWAKENING round a figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a white-jade flash at chest height (where her palms meet) 6 squares across; 2 rays of jade light bursting out round the body, a jade ring opening on the ground at the feet (an ellipse 24 x 8 squares); 3 a tall column of soft jade light 20 squares wide rising round the body to above the head, glowing motes floating up, the ring at 32 x 11; 4 the column fading upward, the motes higher; 5 a few motes above the head. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 576x704 (image 2880x704) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `karma_fx_mantra.png`：R 真言准备中：身边绕着的灵光（循环），4 帧

真言开着、等她放下一个技能的 6 秒：四五颗白翠色的光点和小小的灵火（一两颗是粉色）绕着她从腰往头顶慢慢螺旋上升，头顶上（她的翡翠玉环那里，离脚底约 34 格）一团柔和的翠绿光。**中间大部分空着**，不要盖住人。左右对称。约 26 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a jade spirit-light ramp (#FFFFFF, #E2FFF4, #A8F7DC, #62E4BA, #2FC196, #188F6E, #0C5E4A) and a magenta-pink flame ramp (#FFFFFF, #FFE2F6, #FFA6DE, #F462C4, #D032A2, #941A78, #5A0E4C).
Effect: A LOOPING MANTRA AURA round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: four or five jade-white motes and tiny spirit flames (one or two of them pink) spiralling slowly up round the figure from the waist to above the head, a soft jade glow floating just above the head (34 squares above the feet). Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 448x672 (image 1792x672) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `karma_fx_a_bolt` | view_projectiles `league_karma_a_bolt`（循环，朝飞行方向转） | 10 × 4 |
| `karma_fx_a_hit` | view_effects `league_karma_a_hit`（跟随，画在人物上面） | 10 |
| `karma_fx_q_ball` | view_projectiles `league_karma_q_ball`（循环，朝飞行方向转） | 16 × 9 |
| `karma_fx_q_boom` | view_effects `league_karma_q_boom`（不跟随，画在人物上面；爆炸点） | 28 × 22 |
| `karma_fx_q_hit` | view_effects `league_karma_q_hit`（跟随，画在人物上面） | 16 |
| `karma_fx_q_slow` | view_buffs `league_karma_q_slow`（循环，跟随，画在人物下面；1.5 秒） | 16 × 5 |
| `karma_fx_rq_ball` | view_projectiles `league_karma_rq_ball`（循环，朝飞行方向转） | 22 × 12 |
| `karma_fx_rq_boom` | view_effects `league_karma_rq_boom`（不跟随，画在人物上面；爆炸点） | 32 × 26 |
| `karma_fx_rq_field` | view_effects `league_karma_rq_field`（不跟随，画在人物下面；爆炸点） | 40 × 20 |
| `karma_fx_rq_blast` | view_effects `league_karma_rq_blast`（不跟随，画在人物上面；爆炸点） | 40 × 32 |
| `karma_fx_rq_slow` | view_buffs `league_karma_rq_slow`（循环，跟随，画在人物下面；1 秒） | 20 × 6 |
| `karma_fx_w_beam` | view_projectiles `league_karma_w_beam`（循环，朝飞行方向转） | 18 × 6 |
| `karma_fx_w_tether` | view_projectiles `league_karma_w_tether`（循环，从目标飞回她身边，每隔几 tick 发一节，连起来就是一条线；朝右画） | 10 × 6 |
| `karma_fx_w_hit` | view_effects `league_karma_w_hit`（跟随，画在人物上面） | 14 |
| `karma_fx_w_mark` | view_buffs `league_karma_w_mark`（循环，跟随，画在人物上面；1.3 秒） | 20 × 18 |
| `karma_fx_w_snap` | view_effects `league_karma_w_snap`（跟随，画在人物上面） | 22 × 24 |
| `karma_fx_w_root` | view_buffs `league_karma_w_root`（循环，跟随，画在人物下面；1.7 秒） | 24 × 8 |
| `karma_fx_rw_heal` | view_effects `league_karma_rw_heal`（跟随，画在人物上面） | 24 × 36 |
| `karma_fx_e_land` | view_effects `league_karma_e_land`（跟随，画在人物上面） | 26 × 34 |
| `karma_fx_e_on` | view_buffs `league_karma_e_on`（循环，跟随，画在人物上面；护盾在时） | 26 × 34 |
| `karma_fx_e_haste` | view_buffs `league_karma_e_haste`（循环，跟随，画在人物下面；1.5 秒） | 24 × 7 |
| `karma_fx_re_wave` | view_effects `league_karma_re_wave`（不跟随，画在人物下面；被保护的队友脚下） | 60 × 30 |
| `karma_fx_r_cast` | view_effects `league_karma_r_cast`（跟随，画在人物上面） | 32 × 42 |
| `karma_fx_mantra` | view_buffs `league_karma_mantra`（循环，跟随，画在人物上面；最多 6 秒） | 26 × 40 |

- `league_karma_fx`（跟随的小图、飞行物、buff）和 `league_karma_big`（地上的大图：`q_boom`、`rq_boom`、`rq_field`、`rq_blast`、`re_wave`）两张 sheet，和技能数据里写的一致。
- `rq_field` 播 1.5 秒（技能数据 rq_wait 90 tick）：8 帧的时长加起来约 1.45 秒，最后接 `rq_blast`（rq_wait - 4 tick 时播放）。
- `q_boom`、`rq_boom`、`rq_blast` 是竖着的画面：放在 ViewEffect 里（不随方向转），不要挂在 RangeProjectile 的 view 上（红色方会倒过来，蕾欧娜的教训）。
- `w_tether` 量乐芙兰 `e_tether` 的摆法（一节节飞回施法者，首尾相接）；`w_beam` 是一瞬间的光束头。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
