# 狂暴之心 凯南：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型已定（`design/kennen_design.png`，8 倍，你画的版本 A，裁到 37 格）。
> - 大小对照 `design/kennen_size.png`：定稿造型放大 4 倍，脚在红色脚底线上，上面是 10 格一段的刻度，右边是原版雷电法师。凯南 27×37 格（含背上的手里剑），是约德尔人，比原版英雄（约 31–36 格高）还小一点。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里凯南自己的特效贴图（多数是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（手里剑和 Q、标记/眩晕/W 的闪电、E 的闪电球、R 的雷暴），只在本地用，不要提交。颜色按下面写的色阶。
> - 特效照下面第 1–19 条和「所有特效图的规则」画，每张一个 PNG，文件名 `kennen_fx_<名字>.png`，排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、画了几帧、有没有没做到的地方）。最好打成一个 zip（`kennen_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + W 被动 | 甩手里剑；每第 5 下带电，额外魔法伤害并上一层标记 | `kennen_fx_a_star` · `a_cast` · `a_hit` · `a_cast2` · `a_hit2` |
| 被动「雷缚印」 | 技能打中英雄留下标记，第三层眩晕 1.25 秒 | `kennen_fx_k_mark1` · `k_mark2` · `k_stun` |
| 技能 1 = Q「千鸟」 | 掷出雷电手里剑，打中第一个敌方英雄 | `kennen_fx_q_star` · `q_cast` · `q_hit` |
| 技能 2 = E「雷铠」（+ W「电刃」） | 化作闪电冲过敌群，冲完放电（W），之后攻速提升；大招好了就接大招 | `kennen_fx_e_in` · `e_ball` · `e_hit` · `e_out` · `w_burst` · `w_hit` |
| 大招 = R「万雷天牢引」 | 跟随自己的雷暴 3 秒，每 0.5 秒雷击风暴里的敌方英雄 | `kennen_fx_r_storm` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**闪电、电光、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮、看得清**：游戏地面偏暗，特效小，所以每个闪电都要有白色的芯和亮紫白色，暗紫只用在边缘和消散的时候；青蓝色只做电光的边和火花。
- 颜色（按每条写的用）：
  - 紫白闪电（他的主色）：`#FFFFFF`、`#EDE4FF`、`#C3A6FF`、`#9466F2`、`#6232C4`；
  - 青蓝电光边（E 的闪电球、火花）：`#F2FFFF`、`#A8F0FF`、`#4CC8F5`；
  - 金色（手里剑）：`#FFF4C8`、`#FEDC80`、`#F8A23B`、`#CB7420`；
  - 暗紫风暴云（只用在 R 的雷暴）：`#2A1446`、`#3E2066`、`#5B3590`。
- **飞行类特效朝右画，而且上下对称**（普攻手里剑、千鸟）：游戏会把它转到飞行方向。
- 命中、爆炸、放电圈居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在角色身上的特效（眩晕、闪电球、放电、雷暴）：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `kennen_fx_a_star.png`：普攻手里剑（飞行中循环），4 帧

普攻甩出的手里剑：一枚旋转的金色四角手里剑（中间一个小孔），每帧转 22.5 度，后面不拖尾。约 9 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) with a white highlight.
Effect: a SMALL SPINNING SHURIKEN, 4 frames, a seamless loop: a gold four-pointed throwing star with a tiny dark hole in its middle and a white glint on one point, turning a quarter of 90 degrees each frame so the 4 frames loop.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kennen_fx_a_cast.png`：普攻出手：手上的闪光，3 帧

甩出手里剑的一瞬：手边一小团金白色的闪光，带两道短短的风痕。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) with white.
Effect: a SMALL THROW FLASH, 3 frames: 1 a tiny white point; 2 a small four-pointed gold-white flash with two short wind streaks to the right; 3 the flash fades to two gold specks.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kennen_fx_a_hit.png`：普攻命中，4 帧

手里剑打中：一小团金色火花向外溅。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) with white.
Effect: a SMALL SHURIKEN HIT, 4 frames: 1 a white flash; 2 a gold burst with 4 short spikes; 3 the spikes break into small gold sparks flying outward; 4 a few fading specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kennen_fx_a_cast2.png`：第 5 次普攻（W 被动）出手：带电的闪光，4 帧

W 被动强化的第五下：出手时手边一团紫白色的电光炸开，几道细小的闪电向外跳。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a CHARGED THROW FLASH, 4 frames: 1 a white point; 2 a violet-white electric flash with 3 short jagged lightning forks jumping out; 3 the forks flicker to new places, cyan sparks; 4 they fade.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kennen_fx_a_hit2.png`：第 5 次普攻打中：电击，5 帧

强化的一下打中：目标身上一团紫白色的电击，几道锯齿闪电绕着它跳（参考 P_Proc_Lightning）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: an ELECTRIC HIT, 5 frames: 1 a white flash at the center; 2 a violet-white burst with 4 jagged lightning forks shooting out; 3 the forks jump to new places around the center, cyan sparks; 4 thinner forks, sparks flying out; 5 a few fading violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kennen_fx_k_mark1.png`：被动雷缚印：一层标记（头顶），4 帧

被动标记一层：目标头顶出现三个小的闪电符号排成一排，第一个点亮（亮紫白），另外两个是暗紫的空槽。出现时一闪，然后保持（4 帧）。约 14 格宽、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4).
Effect: a MARK COUNTER floating over a head, 4 frames: three small lightning-bolt symbols side by side (each about 4 squares tall, zigzag shaped); the LEFT one lit bright violet-white, the other two dark violet empty slots; 1 the lit symbol flashes white; 2-4 it settles to bright violet and the row stays.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the row of symbols centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kennen_fx_k_mark2.png`：被动雷缚印：两层标记（头顶），4 帧

两层：同样三个闪电符号，前两个点亮，第三个还是暗槽，点亮的两个微微闪动（再中一下就眩晕）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4).
Effect: a MARK COUNTER floating over a head, 4 frames: the same three small lightning-bolt symbols; the LEFT TWO lit bright violet-white, the right one a dark violet empty slot; 1 the second symbol flashes white; 2-4 both lit symbols crackle slightly.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the row of symbols centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kennen_fx_k_stun.png`：被动雷缚印：第三层眩晕（1.25 秒），10 帧

第三层标记把目标电晕：三个闪电符号一起亮起炸开，目标全身被紫白色的电流包住（几道锯齿闪电从头到脚跳动），头顶一圈小火花在转。1–2 帧炸开，3–9 帧电流持续（每帧换位置），10 帧散掉。中间留出人的位置，不要画人。约 24 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a LIGHTNING STUN around a standing figure (do NOT draw the figure), 10 frames: 1-2 three small lightning-bolt symbols flash white over the head and burst; 3-9 jagged violet-white lightning crackles all over the figure's outline from head to feet - 3-4 forks that jump to new places every frame - and a small ring of violet sparks spins over the head; 10 the lightning fades to a few sparks.
Layout: one horizontal row of 10 equal cells, each 4 wide to 5 tall, image size 5120x1280 (each cell 512x640); the figure's place centered at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kennen_fx_q_star.png`：Q 千鸟：飞出去的雷电手里剑（飞行中循环），4 帧

掷出的千鸟：一枚飞速旋转的金色手里剑，缠着紫白色的电光，后面拖一条锯齿状的闪电尾巴（参考 Q_Beam、shuriken-zap）。上下对称。约 18 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a gold ramp (#FFF4C8, #FEDC80, #F8A23B, #CB7420) for the shuriken and a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a FLYING LIGHTNING SHURIKEN moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a gold four-pointed throwing star, spinning (a quarter turn over the 4 frames), wrapped in flickering violet-white electric sparks; behind it (to the left) a jagged violet lightning trail that changes shape every frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the shuriken on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kennen_fx_q_cast.png`：Q 出手：手上的电光，4 帧

甩出千鸟的一瞬：手边一团紫白色的电光和一圈小火花（只画闪光，不画飞出去的手里剑）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with gold sparks (#FFF4C8, #FEDC80, #F8A23B, #CB7420).
Effect: a LIGHTNING THROW FLASH, 4 frames: 1 a white point; 2 a violet-white electric flash, 2 short lightning forks and a few gold sparks; 3 the flash at full size; 4 it fades.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kennen_fx_q_hit.png`：Q 千鸟打中，5 帧

千鸟打中目标：一下白光，紫白色的电击炸开，几道闪电和金色碎片向外飞（参考 Q_Impact_Flash、W_Impact）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5) and gold sparks (#FFF4C8, #FEDC80, #F8A23B, #CB7420).
Effect: a LIGHTNING SHURIKEN IMPACT, 5 frames: 1 a white flash; 2 a star-shaped violet-white electric burst with gold sparks; 3 5-6 jagged lightning forks shoot outward; 4 the forks break into cyan and violet sparks; 5 fading specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kennen_fx_w_burst.png`：W 电刃：以凯南为中心的放电（地面 + 闪电，大图），7 帧

电刃放电：凯南周围一圈紫白色的电光从脚下炸开向外扩（地上是扁椭圆，宽是高的 2 倍），同时十几道锯齿闪电从中心向四周射出（参考 W_Electric_Arcs、W_Glow_Blue）。中间留出凯南的位置，不要画人。约 100 格宽、50 格高（地上的圈），闪电可以高出一点。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: an ELECTRIC SURGE around a figure (do NOT draw the figure), 7 frames: 1 a white flash at the center bottom; 2 a ring of violet-white electricity starts on the ground (a flattened ellipse, twice as wide as tall) and 6-8 jagged lightning forks shoot outward from the center; 3 THE SURGE: the ring at two thirds of the cell's width, 10-12 forks reaching outward, cyan sparks; 4 the ring reaches the cell's edges, the forks flicker; 5 the ring thins and breaks into arcs; 6 the forks fade to violet; 7 a few sparks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 3584x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `kennen_fx_w_hit.png`：W 电刃打中的敌人：从凯南劈来的电击，4 帧

被电刃电到：敌人身上一团紫白色的电光炸开，两三道小闪电跳动。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a SMALL ELECTRIC SHOCK, 4 frames: 1 a white flash; 2 a violet-white burst with 3 short lightning forks; 3 the forks jump to new places, cyan sparks; 4 they fade.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `kennen_fx_e_in.png`：E 雷铠：化身闪电（起点），4 帧

凯南化作闪电冲出去的一瞬：原地一团紫白色的电光炸开，几道闪电向右甩出（参考 E_Lightball_Edge、E_Lightning）。约 24 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a LIGHTNING TRANSFORM FLASH, 4 frames: 1 a white flash; 2 a round violet-white electric burst with a cyan jagged edge; 3 the burst stretches to the right, 3 lightning forks whipping right; 4 it fades to sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `kennen_fx_e_ball.png`：E 雷铠：冲刺时包住凯南的闪电球（跟随，循环），4 帧

冲刺时包着凯南的闪电球：一圈锯齿状的紫白色电光球壳（中间空着，能看到里面的凯南），球的边缘是青蓝色的尖刺，后面（左边）拖几道闪电残影（参考 E_Lightball_Edge、E_Model_Blur、E_Ribbon）。中间留出凯南的位置（他压低身子冲刺），不要画人。约 30 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a BALL OF LIGHTNING around a small dashing figure (do NOT draw the figure; keep the middle open so the figure shows through), 4 frames, a seamless loop: a round shell of jagged violet-white electricity with spiky cyan edges, 3-4 lightning forks crawling over it that change place every frame, and 3 short lightning streaks trailing to the LEFT behind it.
Layout: one horizontal row of 4 equal cells, each 6 wide to 5 tall, image size 3072x640 (each cell 768x640); the ball centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `kennen_fx_e_hit.png`：E 冲过时电到的敌人，4 帧

被冲过的敌人身上一下紫白色的电击。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a SMALL ELECTRIC ZAP, 4 frames: 1 a white flash; 2 a small violet-white burst with 2 lightning forks; 3 cyan sparks; 4 fading specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `kennen_fx_e_out.png`：E 雷铠：冲刺结束，闪电散开（终点），5 帧

冲刺结束：闪电球炸开散掉，凯南重新出现（只画炸开的电光和火花）。约 28 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a LIGHTNING BALL BREAKING, 5 frames: 1 a round violet-white electric shell with cyan spikes; 2 it bursts: a white flash and 6 lightning forks shooting outward; 3 the forks break into sparks; 4 sparks fly out and fade; 5 a few specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `kennen_fx_r_storm.png`：R 万雷天牢引：跟随凯南的雷暴（3 秒，地面 + 闪电，大图），12 帧循环

凯南的大招：以他为中心的一圈旋转的雷暴（地上是扁椭圆，宽是高的 2 倍）——暗紫色的风暴云和飞旋的小手里剑绕着圈转，圈上不停有紫白色的闪电劈下（参考 R_LightningErosion、W_Electric_Arcs）。1–2 帧成形，3–10 帧循环旋转（每帧云和手里剑转一点、闪电换位置），11–12 帧消散。中间留出凯南的位置，不要画人。约 110 格宽、56 格高，闪电可以高出椭圆 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5), dark storm clouds (#2A1446, #3E2066, #5B3590) and gold (#FFF4C8, #FEDC80, #F8A23B, #CB7420) for the small shurikens.
Effect: a SWIRLING LIGHTNING STORM around a figure (do NOT draw the figure), 12 frames: a wide flattened ring on the ground (twice as wide as tall) made of dark violet storm clouds and 6-8 small spinning gold shurikens circling around the center; 2-3 jagged violet-white lightning bolts strike down onto the ring from above in every frame, at new places each frame; 1-2 the ring forms from the center outward; 3-10 the ring turns (the clouds and shurikens move a little around the circle each frame) - a seamless loop from 10 back to 3; 11-12 the ring breaks up and fades.
Layout: one horizontal row of 12 equal cells, each 2 wide to 1 tall, image size 6144x256 (each cell 512x256); the ellipse centered in the lower part of every cell, the lightning reaching up. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `kennen_fx_r_hit.png`：R 雷暴劈中敌方英雄：从天而降的闪电（大图），5 帧

雷暴每 0.5 秒劈中风暴里的敌方英雄：一道粗的紫白色锯齿闪电从上方劈到目标身上，落点炸开一团电光。约 16 格宽、48 格高（落点在格子底部）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning or sparks, colours only from a violet lightning ramp (#FFFFFF, #EDE4FF, #C3A6FF, #9466F2, #6232C4) with cyan edges (#F2FFFF, #A8F0FF, #4CC8F5).
Effect: a LIGHTNING BOLT STRIKE, 5 frames: 1 a thin white bolt appears from the top of the cell down to the bottom; 2 the bolt at full thickness, jagged, violet-white with a white core, and a burst of electricity where it hits the bottom; 3 the bolt flickers to a new jagged shape, the burst widens, cyan sparks; 4 the bolt breaks into short pieces; 5 a fading glow at the bottom.
Layout: one horizontal row of 5 equal cells, each 1 wide to 3 tall, image size 1280x768 (each cell 256x768); the bolt centered, its impact at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kennen_fx_a_star` | view_projectiles `league_kennen_a_star`（朝右，游戏转到飞行方向） | 9 × 9 |
| `kennen_fx_a_cast` | view_effects `league_kennen_a_cast`（施法者身上，跟随） | 10 |
| `kennen_fx_a_hit` | view_effects `league_kennen_a_hit`（跟随） | 12 |
| `kennen_fx_a_cast2` | view_effects `league_kennen_a_cast2`（施法者身上，跟随） | 14 |
| `kennen_fx_a_hit2` | view_effects `league_kennen_a_hit2`（跟随） | 18 |
| `kennen_fx_k_mark1` | view_effects `league_kennen_k_mark1`（目标头顶，跟随） | 14 × 7 |
| `kennen_fx_k_mark2` | view_effects `league_kennen_k_mark2`（目标头顶，跟随） | 14 × 7 |
| `kennen_fx_k_stun` | view_effects `league_kennen_k_stun`（目标身上，跟随；一次播完 1.25 秒） | 24 × 30 |
| `kennen_fx_q_star` | view_projectiles `league_kennen_q_star`（朝右，游戏转到飞行方向） | 18 × 10 |
| `kennen_fx_q_cast` | view_effects `league_kennen_q_cast`（施法者身上，跟随） | 14 |
| `kennen_fx_q_hit` | view_effects `league_kennen_q_hit`（跟随） | 20 |
| `kennen_fx_w_burst` | view_effects `league_kennen_w_burst`（施法者身上，跟随；大图 league_kennen_big） | 100 × 50（半径 50000） |
| `kennen_fx_w_hit` | view_effects `league_kennen_w_hit`（跟随） | 16 |
| `kennen_fx_e_in` | view_effects `league_kennen_e_in`（出发的地方，不跟随） | 24 |
| `kennen_fx_e_ball` | view_effects `league_kennen_e_ball`（施法者身上，跟随，冲刺的 0.3 秒里循环） | 30 × 26 |
| `kennen_fx_e_hit` | view_effects `league_kennen_e_hit`（跟随） | 14 |
| `kennen_fx_e_out` | view_effects `league_kennen_e_out`（终点，不跟随） | 28 |
| `kennen_fx_r_storm` | view_effects `league_kennen_r_storm`（施法者身上，跟随；大图 league_kennen_big；12 帧 × 0.25 秒） | 110 × 56（半径 55000） |
| `kennen_fx_r_hit` | view_effects `league_kennen_r_hit`（目标身上，跟随；大图） | 16 × 48 |

- `k_mark1/2` 挂在目标头顶（按目标身高），`k_stun` 12 帧撑满眩晕 75 tick（第二次 30 tick 时只播前 5 帧 + 最后 1 帧）。
- `e_ball` 是新加的 CasterViewEffect（跟随），冲刺 18 tick 循环播；`r_storm` 3 秒 = 3–10 帧循环重复到 180 tick。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法）；量新特效的亮度和包里其他英雄比（见 effects-match-league）；核对交回的张数和这份清单。
