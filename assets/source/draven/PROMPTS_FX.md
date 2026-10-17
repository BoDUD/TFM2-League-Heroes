# 荣耀行刑官 德莱文：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型和动作已定（`design/draven_design.png`，52×54 格，8 倍）。
> - **斧头**：好几张特效里都有他那把双刃旋转飞斧，照 `design/draven_axe.png`（定稿里那把斧放大 16 倍：带刺圆环 + 两片弯刃，白刃口、黑内板、金钉、红宝石）画，在特效里按每条写的大小画小一点。
> - 大小对照 `design/draven_size.png`：定稿放大 4 倍，脚底在红线上，上面 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/draven_shots.png`：普攻出手、Q 转斧、E 双斧掷出、R 巨斧掷出、跑步、站姿那几帧（4 倍），青色十字是脚下。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里德莱文自己的特效贴图（只在本地用）：**颜色是血红到橙黄的火焰**（`Q_Color-madflame`、`DravenFlame`），接斧落点是一个圆环（`Q_Ring`），R 有火焰拖尾和地面尘土。被动兑现用**金色**（金币）。
> - **特效要亮**：每个火焰 / 光的形状都要有白色或最亮一档的芯，暗底上一眼能看见。斧头本身是钢，保留它自己的深色描边；火焰、光、火星**不要描边**。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样）：这些都要**左右对称**。飞行的斧头会转到飞行方向，所以**朝右画、上下对称**。`q_hit`、`q_fall`、`q_lost`、`p_cash` 是**竖着的画面**，上下不能颠倒。
> - 每张一个 PNG，文件名 `draven_fx_<名字>.png`，排版按每条最后一句的格子尺寸。生图原稿也交（`raw/`）：我按格读回、按技能范围定大小。**请用生图画，不要用代码拼方块**；交付前不要再挪动、缩放、重采样（只按网格取色可以）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**；打成 `draven_fx_done.zip` 放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 扔出一把旋转飞斧 | `a_axe` · `a_hit` |
| 技能 1 = Q「旋转飞斧」 | 手里转起一把斧（最多 2 把）；下次普攻扔出带火焰的旋转斧，砸中后斧头弹上天，0.7 秒后落回他脚下的落点圈，站在圈里就接住 | `q_axe` · `q_hit` · `q_zone` · `q_fall` · `q_catch` · `q_lost` · `ax1` · `ax2` |
| W「血性冲刺」（自动） | 对英雄出手时冲刺：移速、攻速提升；接住斧头就刷新 | `w_cast` · `w_ms` |
| 技能 2 = E「开道利斧」 | 并排扔出两把斧，贯穿一条直线，击退并减速 | `e_axes` · `e_hit` · `e_slow` |
| 大招 = R「冷血追命」 | 两把巨型旋转飞斧飞向远处，碰到第一个英雄（或飞到尽头）后折返，往返各斩一次 | `r_axes` · `r_hit` |
| 被动「德莱文联盟」 | 接住斧头叠崇拜层数；用斧头击杀英雄时兑现：回血 + 攻速 | `p_cash` · `p_6` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。火焰、光、火星没有黑描边，也不要用最深的颜色给形状描一圈边；斧头是钢，保留它自己的描边。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档。
- 颜色（按每条写的用）：
  - 血红火焰（W、E、落点圈）：`#FFFFFF`、`#FFE6D6`、`#FFA07C`、`#F2553E`、`#C8222E`、`#8E1424`、`#560A1C`；
  - 红橙火焰（Q 的火焰斧、R）：`#FFFFFF`、`#FFF4C8`、`#FFD266`、`#FF9A2E`、`#F0503C`、`#B81E28`；
  - 金色（被动兑现）：`#FFFFFF`、`#FFF6C8`、`#FFE07A`、`#F3CB57`、`#D69A2A`、`#9A6418`；
  - 尘土（掉在地上的斧头）：`#F0E6D2`、`#CDB896`、`#A08868`、`#74604A`；
  - 斧头：照定稿的钢色 #F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A。
- **飞行的画面朝右画，上下对称**（`a_axe`、`q_axe`、`e_axes`、`r_axes`）。
- **挂在人身上和地上的画面左右对称**，按每条写的站位画；命中居中画；地上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在人身上的特效：格子里留出空的人形位置，不要画人；光环只画外面一圈。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约 1000 距离单位：普攻射程 55000，接斧圈半径 12000，E 宽 16000，R 宽 18000）。

### 1. `draven_fx_a_axe.png`：普攻：飞出去的旋转飞斧（朝右，循环），4 帧

普攻扔出去的斧头：就是他手里那把双刃斧（带刺圆环 + 两片弯刃，见 `design/draven_axe.png`），在空中**转着飞**：4 帧每帧转 45°，后面拖一道很淡的白色弧线（转动的残影）。**朝右飞**；约 12 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a pale white trail (#FFFFFF, #E6EEF8).
Effect: a THROWN AXE flying RIGHT, 4 frames, a seamless loop: his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem, 10 squares across, turning 45 degrees clockwise each frame; a thin pale white arc of motion trailing behind its blades on the left. Symmetric above and below its middle line as a whole.
Layout: one horizontal row of 4 equal cells, each 224x224 (image 896x224) (16 px a square here); the axe's ring in the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `draven_fx_a_hit.png`：普攻命中：斧刃砍中的火花（目标身上），4 帧

斧头砍中：一道白色的斜斩光 + 几颗白、浅蓝和一点红色的火花往外溅。左右对称，居中画。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: an AXE HIT, 4 frames: 1 a white flash 4 squares across; 2 a crossed pair of short white slash streaks 10 squares long with pale steel-blue edges, sparks bursting out; 3 the streaks fading, white and crimson sparks flying outward; 4 a few fading sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `draven_fx_q_axe.png`：Q 旋转飞斧：带血红火焰的飞斧（朝右，循环），4 帧

强化普攻扔出的旋转飞斧：同一把斧头，但转得更快、整把裹着**血红色的火焰光**，后面拖一条红橙色的火焰尾巴（英雄联盟 Q 的颜色，参考 `Q_Color-madflame`、`Z_Flames`、`Z_WeaponTrail`）。**朝右飞**，上下对称；约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a red-orange flame ramp (#FFFFFF, #FFF4C8, #FFD266, #FF9A2E, #F0503C, #B81E28).
Effect: a SPINNING AXE WRAPPED IN CRIMSON FIRE flying RIGHT, 4 frames, a seamless loop: his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem, 10 squares across, turning 45 degrees each frame, a ring of red-orange flame light round it, a flame trail 6 squares long streaming LEFT behind it, white-yellow at the axe and red at the tail. Symmetric above and below its middle line as a whole.
Layout: one horizontal row of 4 equal cells, each 256x192 (image 1024x192) (16 px a square here); the axe's ring in the middle of every cell, a little right of centre. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `draven_fx_q_hit.png`：Q 命中：火焰爆开、斧头往上弹飞（目标身上），5 帧

旋转飞斧砸中：目标身上一团血红色火焰爆开，同时**斧头被弹起来、转着往正上方飞走**（第 2–5 帧斧头越来越高，最后飞出画面上沿）。竖着的画面，上下不能颠倒；左右对称。约 16 格宽、40 格高；爆点在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a red-orange flame ramp (#FFFFFF, #FFF4C8, #FFD266, #FF9A2E, #F0503C, #B81E28).
Effect: a FIERY HIT AND THE AXE BOUNCING UP, UPRIGHT (never upside down), 5 frames: 1 a white-yellow flash 6 squares across at the hit point; 2 a burst of crimson flame 14 squares across, and his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem (8 squares across) just above it starting to fly up; 3 the flame burst fading into sparks, the axe 12 squares higher, spinning; 4 the axe 24 squares above the hit point, a thin flame trail below it; 5 the axe at the top edge, leaving, a few sparks at the hit point. Left-right symmetric apart from the axe's spin.
Layout: one horizontal row of 5 equal cells, each 256x640 (image 1280x640) (16 px a square here); the hit point 8 squares (128 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `draven_fx_q_zone.png`：Q 接斧落点圈（地上，他脚下），7 帧

斧头弹起来以后，地上（他当时站的地方）出现**接斧落点圈**，0.7 秒后斧头掉进圈里：一个白红色的椭圆圈，里面一道红色的内圈从边缘往中间收紧（倒计时），最后一帧整个圈亮一下（斧头落下的瞬间）。参考英雄联盟 `Q_Ring`。左右对称，从斜上方看的椭圆；约 24 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: an AXE LANDING MARKER on the ground, 7 frames (100 ms each): an ellipse ring 24 x 12 squares, 1 square thick, white with a crimson outer edge, a faint red glow inside; a thinner crimson inner ring starts at the edge in frame 1 and closes in toward the middle frame by frame (frame 6: 4 x 2 squares); frame 7 the whole ring flashing white. Left-right symmetric; seen from above at an angle.
Layout: one horizontal row of 7 equal cells, each 448x256 (image 3136x256) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `draven_fx_q_fall.png`：Q 斧头从天上落回来（落点圈上方），7 帧

和落点圈同时播放：那把旋转飞斧从很高的地方**转着往下掉**，后面往上拖一条淡红的光尾，第 7 帧刚好落到他手的高度（落点上方约 16 格）。竖着的画面，上下不能颠倒；斧头竖直落在格子中线上。约 14 格宽、64 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: a SPINNING AXE FALLING STRAIGHT DOWN, UPRIGHT (never upside down), 7 frames (100 ms each): his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem, 9 squares across, turning 90 degrees each frame; its middle at 8, 14, 21, 28, 35, 41 and 47 squares from the TOP of the cell in frames 1-7, a faint crimson light trail 6-10 squares long streaming UP above it; frame 7 a small white glint at the axe (caught). Centered left to right.
Layout: one horizontal row of 7 equal cells, each 224x1024 (image 1568x1024) (16 px a square here); the ground point (the ring's middle) 1 square above the bottom, horizontally centered: in frame 7 the axe's middle is 16 squares above it. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `draven_fx_q_catch.png`：Q 接住斧头：手边一圈火花（跟随），4 帧

接住斧头的一瞬间：他胸口前方一圈白红色的光闪一下，几颗红橙色火星往外飞（英雄联盟接斧有很爽的一声和一闪）。只画光和火星，不要画斧头和人；左右对称。约 24 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a red-orange flame ramp (#FFFFFF, #FFF4C8, #FFD266, #FF9A2E, #F0503C, #B81E28).
Effect: a CATCH FLASH (do NOT draw a figure or an axe), 4 frames: 1 a white-yellow flash 6 squares across; 2 a ring of light 16 squares across, red-orange sparks bursting out; 3 the ring 22 squares across thinning, sparks farther out; 4 a few fading sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 384x384 (image 1536x384) (16 px a square here); the flash 16 squares (256 px) above the bottom, horizontally centered (the figure's feet on the bottom edge). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `draven_fx_q_lost.png`：Q 没接住：斧头掉在地上弹一下消失（落点），5 帧

没接住的斧头：斧头砸在地上，扬起一点尘土，弹起来一点再落下，然后慢慢变淡消失。竖着的画面；约 16 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a dust ramp (#F0E6D2, #CDB896, #A08868, #74604A).
Effect: a DROPPED AXE, UPRIGHT, 5 frames: 1 his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem (9 squares across) lying tilted on the ground point, a puff of dust; 2 the axe bounced 4 squares up, the dust spreading; 3 the axe back on the ground, flat; 4 the axe fading (fewer, paler squares); 5 only a faint glint left. Centered left to right.
Layout: one horizontal row of 5 equal cells, each 256x288 (image 1280x288) (16 px a square here); the ground point 2 squares (32 px) above the bottom, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `draven_fx_ax1.png`：Q 手里有 1 把旋转斧（头顶标记，循环），4 帧

身上有一把旋转飞斧时：他**头顶上方**一个小小的旋转斧标记在转，裹着淡淡的红光（英雄联盟里手上的斧头会转着发光；我们的人物每帧手的位置不同，所以放在头顶）。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: a SMALL SPINNING AXE ICON with a faint crimson glow, 4 frames, a seamless loop: his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem, 9 squares across, turning 45 degrees each frame, a soft red glow ring 12 squares across round it.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192) (16 px a square here); centered in every cell (Claude places it above the head). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `draven_fx_ax2.png`：Q 手里有 2 把旋转斧（头顶标记，循环），4 帧

身上有两把旋转飞斧时：头顶上方**并排两个**小旋转斧标记（和 `ax1` 同一个斧头，左右各一个，转的方向相反）。约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: TWO SMALL SPINNING AXE ICONS side by side, 4 frames, a seamless loop: two copies of his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem, each 9 squares across, their middles 12 squares apart, the left one turning clockwise and the right one counter-clockwise 45 degrees a frame, each in a soft red glow ring. Left-right symmetric as a pair.
Layout: one horizontal row of 4 equal cells, each 384x192 (image 1536x192) (16 px a square here); the pair centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `draven_fx_w_cast.png`：W 血性冲刺：身上一下血红色的冲刺光（跟随），5 帧

血性冲刺开启：他全身外面一圈血红色的光往外一炸，几道红色的速度线往后（左右两边）甩开，几缕红色火焰往上飘。只画外面一圈，**中间空着**，不要盖住人。左右对称。约 40 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: a BURST OF CRIMSON SPEED round a figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a thin bright red-white ring flaring round the rim of an upright oval 30 x 38 squares; 2 short crimson speed streaks shooting out to both sides from the rim, red flame wisps rising; 3 the streaks longest, wisps higher; 4 the ring fading; 5 a few wisps. Left-right symmetric overall.
Layout: one horizontal row of 5 equal cells, each 640x640 (image 3200x640) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `draven_fx_w_ms.png`：W 冲刺中：脚下的血红速度光（循环），4 帧

冲刺的 1.5 秒：他脚下一圈血红色的光，几道红色的速度线和火星在脚边往上飘、往后甩。只画脚下的，不要盖住人。左右对称，从斜上方看的椭圆。约 32 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: a LOOPING CRIMSON SPEED GLOW at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse of red light 28 x 7 squares, brighter in front, short red speed streaks and sparks lifting off it and drifting outward, changing each frame. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 512x192 (image 2048x192) (16 px a square here); the ellipse's middle 4 squares (64 px) above the bottom, horizontally centered (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `draven_fx_e_axes.png`：E 开道利斧：并排飞出的两把斧（朝右，循环），4 帧

E 扔出的一对斧头：**两把斧一上一下并排**往前飞、各自转，中间和后面拖着白红色的风压线（像把路劈开）。参考英雄联盟 `Z_Movequick`、`R_WeaponTrail`。**朝右飞**，上下对称；约 20 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: TWO AXES FLYING RIGHT side by side, 4 frames, a seamless loop: two copies of his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem, each 9 squares across, one above the other with their middles 9 squares apart, both turning 45 degrees a frame (the upper clockwise, the lower counter-clockwise), white-and-crimson wind streaks 10 squares long trailing LEFT behind and between them. Symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 320x288 (image 1280x288) (16 px a square here); the pair's middle in the middle of every cell, a little right of centre. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `draven_fx_e_hit.png`：E 命中：被劈开的冲击（目标身上），4 帧

被开道利斧打中（会被击退）：一道白色的横向冲击光 + 红色的冲击波往后推，几颗火星。左右对称，居中画。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: a KNOCK-BACK IMPACT, 4 frames: 1 a white flash 5 squares across; 2 a burst of white and crimson light 14 squares across with short streaks pushing outward to both sides; 3 the streaks longer and thinner, sparks; 4 fading sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x256 (image 1024x256) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `draven_fx_e_slow.png`：E 减速：脚下的红色拖拽痕（循环），4 帧

被开道利斧减速 2 秒：脚下一小圈暗红色的光拖着，像被拽住一样，几颗暗红火星慢慢往下落。只画脚下的，不要盖住人。左右对称的椭圆；约 18 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a crimson flame ramp (#FFFFFF, #FFE6D6, #FFA07C, #F2553E, #C8222E, #8E1424, #560A1C).
Effect: a LOOPING DULL RED DRAG MARK at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 16 x 5 squares of dim crimson light with a darker inner ring, a few dim red motes sinking down, pulsing slowly. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 288x96 (image 1152x96) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `draven_fx_r_axes.png`：R 冷血追命：两把巨大的旋转飞斧（朝右，循环），4 帧

大招扔出去、又飞回来的两把巨斧：两把**很大**的双刃斧交叉叠成一个十字 / 风车，一起高速旋转，整团裹着血红色和橙色的火焰光，外圈一道红色的旋转残影，后面拖火焰尾巴（参考 `R_WeaponTrail`、`Z_RingswirlBlur`、`Q_Color-madflame`）。**朝右飞**，上下对称；约 36 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axes' own steel colours (#F5F8FF, #B0C6DE, #71829D, #474958, #292A32, #1A0E0E, gold #F3CB57, gem #CA224A) and a red-orange flame ramp (#FFFFFF, #FFF4C8, #FFD266, #FF9A2E, #F0503C, #B81E28).
Effect: TWO HUGE SPINNING AXES IN CRIMSON FIRE flying RIGHT, 4 frames, a seamless loop: two big copies of his SPINNING AXE (the attached axe close-up): a round spiked dark-steel ring in the middle and two curved silver-blue blades on opposite sides like an S / a pinwheel, each blade with a white edge, a dark inner panel, a gold stud and a red gem, each 24 squares across, crossed into a pinwheel and turning together 45 degrees a frame, wrapped in red-orange flame light with a white-yellow centre, a circular crimson spin blur round the blade tips 32 squares across, a flame trail 10 squares long streaming LEFT. Symmetric above and below its middle line as a whole.
Layout: one horizontal row of 4 equal cells, each 640x640 (image 2560x640) (16 px a square here); the pinwheel's middle in the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `draven_fx_r_hit.png`：R 命中：血红火焰的斩击（目标身上），5 帧

被大招巨斧斩到：一个大大的血红色交叉斩痕（X 形）闪过，红橙色火焰爆开、火星四溅。左右对称，居中画。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a red-orange flame ramp (#FFFFFF, #FFF4C8, #FFD266, #FF9A2E, #F0503C, #B81E28).
Effect: a HEAVY FLAMING X-SLASH HIT, 5 frames: 1 a white-yellow flash 6 squares across; 2 two crossed slash streaks 20 squares long, white in the middle and crimson at the ends; 3 a burst of red-orange flame 18 squares across behind the slashes, sparks flying; 4 the flames rising and thinning; 5 a few fading embers. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 352x352 (image 1760x352) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `draven_fx_p_cash.png`：被动德莱文联盟：击杀兑现，金币和崇拜光喷出（跟随），6 帧

用斧头击杀英雄、兑现崇拜层数：他身边一下金光爆开，一把**金币**往上喷出再落下，金色的星光闪闪（英雄联盟里是观众欢呼 + 金币）。只画光和金币，**中间空着**不要盖住人；左右对称，竖着的画面。约 32 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6C8, #FFE07A, #F3CB57, #D69A2A, #9A6418).
Effect: a BURST OF GOLD COINS AND GLORY round a figure (do NOT draw the figure; keep the middle mostly empty), UPRIGHT, 6 frames: 1 a white-gold flash at chest height 8 squares across; 2 a fountain of small gold coins (2-3 squares each, a bright edge) shooting up from both sides, gold sparkles; 3 the coins at their highest (36 squares up), four-pointed gold stars twinkling round the figure; 4 the coins falling, the stars fading; 5 a few coins near the ground; 6 a few fading sparkles. Left-right symmetric overall.
Layout: one horizontal row of 6 equal cells, each 512x704 (image 3072x704) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `draven_fx_p_6.png`：被动：崇拜满层（身上金色星光，循环），4 帧

崇拜叠满 6 层时：他身边零星几颗金色的四角星在闪（一闪一灭，位置每帧换），表示随时可以兑现。只画零星的星光，不要盖住人；左右对称。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, sparks or glows (the steel axes keep their own 1-square dark outline), BRIGHT colours (each flame and glow lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6C8, #FFE07A, #F3CB57, #D69A2A, #9A6418).
Effect: LOOPING GOLD TWINKLES round a figure (do NOT draw the figure; keep the middle empty), 4 frames, a seamless loop: 3-4 small four-pointed gold stars (3-5 squares) scattered round an upright oval 26 x 36 squares, each blinking on and off in a different frame. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 480x640 (image 1920x640) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `draven_fx_a_axe` | view_projectiles `league_draven_a_axe`（循环，朝飞行方向转） | 12 × 12 |
| `draven_fx_a_hit` | view_effects `league_draven_a_hit`（跟随，画在人物上面） | 12 |
| `draven_fx_q_axe` | view_projectiles `league_draven_q_axe`（循环，朝飞行方向转） | 16 × 12 |
| `draven_fx_q_hit` | view_effects `league_draven_q_hit`（跟随，画在人物上面） | 16 × 40 |
| `draven_fx_q_zone` | view_effects `league_draven_q_zone`（不跟随，画在人物下面；0.7 秒） | 24 × 12 |
| `draven_fx_q_fall` | view_effects `league_draven_q_fall`（不跟随，画在人物上面；0.7 秒） | 14 × 64 |
| `draven_fx_q_catch` | view_effects `league_draven_q_catch`（跟随，画在人物上面） | 24 × 24 |
| `draven_fx_q_lost` | view_effects `league_draven_q_lost`（不跟随，画在人物下面；落点上） | 16 × 18 |
| `draven_fx_ax1` | view_buffs `league_draven_ax1`（循环，跟随，画在人物上面） | 12 × 12 |
| `draven_fx_ax2` | view_buffs `league_draven_ax2`（循环，跟随，画在人物上面） | 24 × 12 |
| `draven_fx_w_cast` | view_effects `league_draven_w_cast`（跟随，画在人物上面） | 40 × 40 |
| `draven_fx_w_ms` | view_buffs `league_draven_w_ms`（循环，跟随，画在人物下面；1.5 秒） | 32 × 12 |
| `draven_fx_e_axes` | view_projectiles `league_draven_e_axes`（循环，朝飞行方向转） | 20 × 18 |
| `draven_fx_e_hit` | view_effects `league_draven_e_hit`（跟随，画在人物上面） | 16 |
| `draven_fx_e_slow` | view_buffs `league_draven_e_slow`（循环，跟随，画在人物下面） | 18 × 6 |
| `draven_fx_r_axes` | view_projectiles `league_draven_r_out` 和 `league_draven_r_back`（循环，朝飞行方向转） | 36 × 36 |
| `draven_fx_r_hit` | view_effects `league_draven_r_hit`（跟随，画在人物上面） | 22 |
| `draven_fx_p_cash` | view_effects `league_draven_p_cash`（跟随，画在人物上面） | 32 × 44 |
| `draven_fx_p_6` | view_buffs `league_draven_p_6`（循环，跟随，画在人物上面） | 30 × 40 |

- `q_zone` 和 `q_fall` 在斧头弹起的同一刻一起播（不跟随：留在他当时站的地方），都是 0.7 秒 = 7 帧 × 100 毫秒；`q_fall` 第 7 帧斧头在他手的高度。
- `ax1` / `ax2` 放在头顶（定稿头顶约在脚上方 40 格）：导入时整张往上挪。
- `r_axes` 同时给 `r_out`（飞出去）和 `r_back`（飞回来）用。
- 清掉 Codex 给光描的最深色边（`unrim`）；核对交回张数；量亮度。
