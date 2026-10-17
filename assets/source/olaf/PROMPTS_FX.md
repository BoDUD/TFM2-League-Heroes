# 狂战士 奥拉夫：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图。** 造型和动作已定（`design/olaf_design.png`，39×42 格，8 倍）。
> - 大小对照 `design/olaf_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度，右边是原版狂战士。每条写的大小都是游戏像素（格）。
> - `design/olaf_shots.png`：普攻劈中、Q 掷出、E 砸地、R 怒吼那几帧的动作和站姿（4 倍），青色十字是脚下。
> - 参考图：`refs/lol_icons.png` 是英雄联盟里他的 Q、E、R 技能图标——**颜色照它**；`refs/lol_fx_ref.png` 是他自己的特效贴图（不少是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行。两张都只在本地用。
> - 颜色：**斧光、刃光、闪电是冰蓝白色**（白色的芯、冰蓝色的边）；**诸神黄昏、狂战士之怒、挺过去的血气是红橙色的怒火**（白黄的芯、红橙色的火、暗红的边）。
> - **两张斧头图（`q_fly` 飞出去的斧、`q_axe` 插在地上的斧）画的是实物**：照造型图里的斧子画（棕色斧柄、蓝灰钢斧刃、白色刃口），**要有近黑描边**；它们的光晕和残影才是光，不描边。
> - **特效要亮**：每个形状都要有白色或最亮一档的芯，暗底上一眼能看见；最深的一档颜色只给很少的点缀。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**（插在地上的斧头是地上的实物，例外）。飞出去的斧头会转到飞行方向，**往右飞着画**。斧头落地、E 砸中、R 怒吼是**竖着的画面**（往上溅、往上冒），上下不能颠倒。
> - 特效照下面第 1–13 条和「所有特效图的规则」画，每张一个 PNG，文件名 `olaf_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`olaf_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 斧头劈砍；被动「狂战士之怒」：血越少攻速越快，满层时吸血 | `olaf_fx_a_hit` · `olaf_fx_p_4` |
| 技能 1 = Q「逆流投掷」 | 掷出一把斧头，路上砍中的敌人减速、减护甲；斧头插在落点，走过去捡起来刷新冷却 | `olaf_fx_q_fly` · `olaf_fx_q_land` · `olaf_fx_q_axe` · `olaf_fx_q_hit` · `olaf_fx_q_slow` · `olaf_fx_q_pick` |
| 技能 2 = E「鲁莽挥击」 | 双斧猛砸一个敌人，真实伤害，自己也掉血 | `olaf_fx_e_hit` |
| W「挺过去」（自动） | 攻速、吸血、护盾 | `olaf_fx_w_cast` · `olaf_fx_w_on` |
| 大招 = R「诸神黄昏」 | 怒吼，免疫控制、攻击力和移速提高 | `olaf_fx_r_cast` · `olaf_fx_r_on` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火花、闪电、寒气没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反；两张斧头实物除外）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 冰蓝钢光（斧光、刃光、闪电、寒气）：`#FFFFFF`、`#E6F6FF`、`#B4E2FF`、`#72B8F2`、`#3C7ED6`、`#1E4AA0`、`#10265C`；
  - 红橙怒火（R、被动、W 的血气）：`#FFFFFF`、`#FFF2C2`、`#FFCB5E`、`#FF8C1E`、`#E2461A`、`#A81E10`、`#5C0C08`；
  - 斧子实物（造型图的颜色）：`#2A1208`、`#4A2A1E`、`#74442C`、`#A06A44`、`#2E3448`、`#4E5E7E`、`#8494B2`、`#BCC4D8`、`#ECEAF0`、`#FFFFFF`；
- **飞出去的斧头往右飞着画**（`q_fly`）：游戏会把它转到飞行方向。
- **挂在人身上和地上的画面左右对称**，按每条写的站位画；命中居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。`q_land`、`e_hit`、`r_cast` 是竖着的画面，不能颠倒。
- 套在角色身上的特效（捡斧、挺过去、诸神黄昏、狂战士之怒）：格子里留出空的人形位置，不要画人；`w_on`、`r_on` 画在人**后面**，边缘最亮。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻射程约 25000，Q 斧头落点捡斧范围半径 9000，E 射程 28000）。

### 1. `olaf_fx_a_hit.png`：普攻命中：一道冰蓝色的劈砍光（目标身上），4 帧

斧头劈中：一道从上往下的白蓝色劈痕（竖直的一条亮光，中间白、两边冰蓝），劈痕两边对称地溅出钢火花，然后变细淡出（参考 Hit_Spark_blue、Flash、sparkMote）。左右对称，居中画。约 12 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an ice-blue steel-light ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C).
Effect: an AXE CHOP HIT, 4 frames: 1 a white flash 4 squares across; 2 a vertical slash streak of white-blue light 14 squares tall and 2 thick (white core, ice-blue edges), steel sparks bursting out to both sides; 3 the streak thinning, the sparks farther out (12 squares across); 4 a few fading sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x288 (image 1024x288) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `olaf_fx_q_fly.png`：Q 逆流投掷：飞出去的斧头（旋转，循环），4 帧

掷出去的斧头在空中翻滚着飞：**斧头本身照造型图的斧子画**（棕色斧柄 1 格宽、蓝灰钢斧刃、白色刃口、近黑描边——斧头是实物，要描边），每帧比上一帧顺时针多转 90°，4 帧转一整圈；斧子后面（左边）拖一道弧形的冰蓝色残影（残影是光，不描边）。斧子约 12 格长。往右飞（往左飞时游戏会把整张转过来）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axe's own colours (#2A1208, #4A2A1E, #74442C, #A06A44, #2E3448, #4E5E7E, #8494B2, #BCC4D8, #ECEAF0, #FFFFFF: near-black outline, brown leather handle, blue-grey steel blade with a white edge) for the axe, and an ice-blue ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C) for its glow and trail.
Effect: a SPINNING THROWN AXE flying RIGHT, 4 frames, a seamless loop: the axe itself drawn like the design's axe (a brown handle 1 square wide, a blue-grey steel blade with a white edge, a near-black outline - it is an object, so it has an outline), about 12 squares long, turned a quarter more clockwise every frame (one full turn in 4 frames), its middle at the middle of the cell; behind it (to the left) a curved ice-blue motion trail (light: no outline).
Layout: one horizontal row of 4 equal cells, each 288x288 (image 1152x288) (16 px a square here); the axe's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `olaf_fx_q_land.png`：Q 斧头落地：砸进地里的冲击（地上，向上溅），5 帧

斧头砸进地面的一下：落点一下白蓝色的光，地上裂开一圈冰蓝色发光的裂纹（从斜上方看的椭圆，约 18 × 9 格），碎石和尘土往上溅，然后尘土落下、裂纹的光暗下去（参考 Q_Impact、Q_GroundSmoke、Cracks）。**竖着的画面**（碎石往上溅），上下不能颠倒。左右对称。约 22 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an ice-blue steel-light ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C) and earthy dust (#8A7A66, #5E5244, #3C3428).
Effect: an AXE STRIKING THE GROUND, UPRIGHT (debris flies up; never upside down), 5 frames: 1 a white-blue flash at the ground point 6 squares across; 2 glowing ice-blue cracks spreading over the ground (an ellipse 18 x 9 squares seen from above at an angle), chips of rock and dust bursting up 8 squares; 3 the cracks at full size, the dust cloud at its biggest; 4 the dust settling, the cracks dimmer; 5 faint glowing cracks. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 384x256 (image 1920x256) (16 px a square here); the ground point 5 squares (80 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `olaf_fx_q_axe.png`：Q 插在地上的斧头（等他来捡，循环），3 帧

斧头插在地上等奥拉夫来捡：**斧子照造型图的斧子画**（棕色斧柄、蓝灰钢斧刃、白色刃口、近黑描边），斧刃朝下斜插进地里，斧柄朝上；斧刃上一圈淡淡的冰蓝色光一明一暗，刃口一点白光闪一下；地上插进去的地方一小圈裂纹。3 帧加起来约 0.25 秒，首尾能接上（游戏每 0.25 秒重放一次）。这是地上的实物，可以不左右对称。约 10 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from the axe's own colours (#2A1208, #4A2A1E, #74442C, #A06A44, #2E3448, #4E5E7E, #8494B2, #BCC4D8, #ECEAF0, #FFFFFF: near-black outline, brown leather handle, blue-grey steel blade with a white edge) for the axe, and an ice-blue ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C) for its glow and trail.
Effect: AN AXE STUCK IN THE GROUND, waiting to be picked up, 3 frames, a seamless loop: the design's axe (brown handle, blue-grey steel blade with a white edge, near-black outline - an object) planted blade-first in the ground at a slight slant, the handle pointing up, about 14 squares tall; a soft ice-blue glow round the blade pulsing brighter and dimmer, a white glint flashing on the edge in frame 2; a small ring of cracks where the blade enters the ground.
Layout: one horizontal row of 3 equal cells, each 224x288 (image 672x288) (16 px a square here); the point where the blade enters the ground 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `olaf_fx_q_hit.png`：Q 命中：斧头飞过时砍中（目标身上），4 帧

斧头飞过、砍到路上每个敌人：一下白光，一道横着的冰蓝色刃光从左到右扫过（左右对称：中间最亮、两头变细），冰蓝色的碎光往外炸开，然后淡出。左右对称，居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an ice-blue steel-light ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C).
Effect: a FLYING-AXE CUT HIT, 4 frames: 1 a white flash 5 squares across; 2 a horizontal streak of ice-blue blade light 14 squares long (brightest and thickest in the middle, thin at both ends), shards of blue light bursting out; 3 the shards farther out, the streak fading; 4 a few fading motes. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x256 (image 1024x256) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `olaf_fx_q_slow.png`：Q 减速：脚下一圈冰蓝色的寒气（循环），4 帧

被逆流投掷减速：脚下的地上一小圈冰蓝色的寒气在转，几颗小冰晶往上飘（参考 common_Slow-Wake）。只画脚下的一圈，不要盖住人。左右对称，从斜上方看的椭圆。约 16 格宽、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an ice-blue steel-light ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C).
Effect: LOOPING FROST WISPS at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 16 x 5 squares of ice-blue mist swirling on the ground, a few small ice glints rising. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 320x128 (image 1280x128) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `olaf_fx_q_pick.png`：Q 捡回斧头：他身上一圈冰蓝色的光（他身上），4 帧

奥拉夫走过斧头、把它捡回来的一下（Q 的冷却刷新）：腰间一圈冰蓝色的光环一闪，几道白蓝色的光带往上旋转升到肩膀，火花飞散，然后淡出。**中间空着**，不要盖住人。左右对称。约 26 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an ice-blue steel-light ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C).
Effect: A PICK-UP FLASH round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames: 1 a ring of ice-blue light round the waist (an ellipse 22 x 7 squares, its middle 14 squares above the feet) flashing white; 2 two or three white-blue light ribbons spiralling up round the body to the shoulders; 3 the ribbons at the top (26 squares above the feet), sparks flying; 4 a few fading sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 480x544 (image 1920x544) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `olaf_fx_e_hit.png`：E 鲁莽挥击：双斧砸中（目标身上，大图），5 帧

双斧一起砸下去（真实伤害）：目标身上一下刺眼的白光，两道冰蓝色的劈痕交叉成 X，一圈白蓝色的冲击光往外炸，几道细细的蓝白色闪电往四周窜，脚下的地上一圈冲击波，然后碎光和闪电散掉（参考 E_ChainElec、Q_Impact、blast_ring）。**竖着的画面**，上下不能颠倒。左右对称，居中画。约 28 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an ice-blue steel-light ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C).
Effect: a RECKLESS TWO-AXE SLAM HIT, UPRIGHT, 5 frames: 1 a blinding white flash 8 squares across; 2 two ice-blue slash streaks crossing in an X 22 squares tall, a ring of white-blue shock light bursting out, thin blue-white lightning bolts forking out to the sides; 3 the ring at 28 squares, the lightning at its longest, a shock ring on the ground under the target (an ellipse 26 x 8 squares); 4 the slashes fading, sparks and broken light flying; 5 a few fading sparks and a faint lightning flicker. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 512x512 (image 2560x512) (16 px a square here); centered in every cell (the target's middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `olaf_fx_w_cast.png`：W 挺过去：他身上爆出一团血红怒气和闪电（他身上），5 帧

挺过去开启的一下（攻速、吸血、护盾）：胸口一下红橙色的光，一圈血红色的怒气往外一炸，两条手臂周围窜起几道白蓝色的细闪电，身上罩起一个淡红色的圆护罩的边，然后闪电消失、护罩边变淡（参考 W_Lightning、W_ShieldAura、W_Smoke）。**中间大部分空着**，不要盖住人。左右对称。约 40 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an ice-blue steel-light ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C) and a red-orange rage-fire ramp (#FFFFFF, #FFF2C2, #FFCB5E, #FF8C1E, #E2461A, #A81E10, #5C0C08).
Effect: TOUGH IT OUT round a figure (do NOT draw the figure; leave the inside EMPTY), 5 frames: 1 a red-orange flash at chest height (18 squares above the feet) 8 squares across; 2 a ring of blood-red rage light bursting out to 30 squares, thin white-blue lightning bolts crackling round both sides of the body at arm height; 3 the rim of a round pale-red shield bubble 40 x 44 squares appearing, 1-2 squares thick, the lightning at its brightest; 4 the lightning gone, red embers drifting up; 5 the bubble rim fading. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 736x800 (image 3680x800) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `olaf_fx_w_on.png`：W 挺过去：身后的血红怒气（循环），4 帧

挺过去持续的 4 秒：人物**身后**一层淡淡的血红色光晕（从人物轮廓往外透出 2–4 格），光晕里几颗红色的火星往上飘，偶尔一道小小的白蓝色闪电一闪。画在人后面，所以中间可以有淡淡的光，但边缘最亮。左右对称。约 40 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an ice-blue steel-light ramp (#FFFFFF, #E6F6FF, #B4E2FF, #72B8F2, #3C7ED6, #1E4AA0, #10265C) and a red-orange rage-fire ramp (#FFFFFF, #FFF2C2, #FFCB5E, #FF8C1E, #E2461A, #A81E10, #5C0C08).
Effect: A LOOPING BLOOD-RED AURA behind a figure, 4 frames, a seamless loop: a soft blood-red glow shaped like a big upright oval 40 x 44 squares (it is drawn behind the figure, so it shows round the body's outline), brightest at its rim, a few red embers drifting up inside it, a tiny white-blue lightning flicker at one side in frame 2 and the other side in frame 4. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 736x800 (image 2944x800) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `olaf_fx_r_cast.png`：R 诸神黄昏：怒吼时爆开的怒火（他身上，大图），6 帧

开大怒吼的一下（不受控制、攻击力提高）：胸口一下白黄色的光，一圈红橙色的冲击波往外炸开，脚下地上展开一圈火环，一圈火焰从地上往上蹿、绕着身体升过头顶，灰烬和火星往上飘，然后火焰变成余烬淡出（参考 R_Fire2x2、R_Ash、R_mis_Ribbon）。**中间大部分空着**，不要盖住人。**竖着的画面**（火往上冒），上下不能颠倒。左右对称。约 48 格宽、50 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a red-orange rage-fire ramp (#FFFFFF, #FFF2C2, #FFCB5E, #FF8C1E, #E2461A, #A81E10, #5C0C08).
Effect: RAGNAROK'S ROAR round a figure (do NOT draw the figure; leave the inside EMPTY), UPRIGHT (flames rise; never upside down), 6 frames: 1 a white-yellow flash at chest height (18 squares above the feet) 8 squares across; 2 a red-orange shockwave ring bursting out to 32 squares, a ring of fire opening on the ground at the feet (an ellipse 30 x 10 squares); 3 flames leaping up from the ground ring round the body to above the head (40 squares), sparks flying; 4 the flames at full height, ash and embers rising; 5 the flames dying into embers; 6 a few embers and ash above the head. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 832x864 (image 4992x864) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `olaf_fx_r_on.png`：R 诸神黄昏：脚下和身后燃烧的怒火（循环，大图），4 帧

诸神黄昏持续的时候：脚下一圈红橙色的火焰在地上烧（从斜上方看的椭圆，约 30 × 10 格），火苗往上蹿到腰的高度，身后透出一层红色的光，几颗火星和灰烬往上飘。画在人**后面**。左右对称。约 36 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a red-orange rage-fire ramp (#FFFFFF, #FFF2C2, #FFCB5E, #FF8C1E, #E2461A, #A81E10, #5C0C08).
Effect: A LOOPING RAGE FIRE at and behind a figure, 4 frames, a seamless loop: a flat ellipse of red-orange flames burning on the ground round the feet (30 x 10 squares), the flames licking up to waist height (16 squares above the feet), a red glow rising behind the body to the shoulders (it is drawn behind the figure), sparks and ash drifting up. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 640x576 (image 2560x576) (16 px a square here); the figure's feet 6 squares (96 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `olaf_fx_p_4.png`：被动 狂战士之怒（满层）：身上冒出的红色怒气（循环），4 帧

血量很低、怒气满层的时候：几缕红橙色的怒气火焰从他的肩膀和头盔两边往上冒，几颗红色的火星往上飘，整体淡淡的、不要太大，不要盖住脸。**中间空着**，不要盖住人。左右对称。约 32 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, fire, sparks, lightning or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a red-orange rage-fire ramp (#FFFFFF, #FFF2C2, #FFCB5E, #FF8C1E, #E2461A, #A81E10, #5C0C08).
Effect: A LOOPING BERSERKER RAGE round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: a few thin red-orange rage flames rising off both shoulders (24 squares above the feet, 12 squares apart) and both sides of the head (34 squares above the feet), red embers drifting up, faint and small - never over the middle of the figure. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 576x704 (image 2304x704) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `olaf_fx_a_hit` | view_effects `league_olaf_a_hit`（跟随，画在人物上面） | 12 × 14 |
| `olaf_fx_q_fly` | view_projectiles `league_olaf_q_axe`（tag q_fly；循环，朝飞行方向转） | 14 × 14 |
| `olaf_fx_q_land` | view_effects `league_olaf_q_land`（不跟随，画在人物下面；落点） | 22 × 14 |
| `olaf_fx_q_axe` | view_effects `league_olaf_q_axe`（不跟随，画在人物下面；每 0.25 秒放一次，最多 5 秒） | 10 × 14 |
| `olaf_fx_q_hit` | view_effects `league_olaf_q_hit`（跟随，画在人物上面） | 14 |
| `olaf_fx_q_slow` | view_buffs `league_olaf_q_slow`（循环，跟随，画在人物下面；1.5 秒） | 16 × 5 |
| `olaf_fx_q_pick` | view_effects `league_olaf_q_pick`（跟随，画在人物上面；捡起斧头时） | 26 × 30 |
| `olaf_fx_e_hit` | view_effects `league_olaf_e_hit`（BIG；跟随，画在人物上面） | 28 × 30 |
| `olaf_fx_w_cast` | view_effects `league_olaf_w_cast`（跟随，画在人物上面） | 40 × 44 |
| `olaf_fx_w_on` | view_buffs `league_olaf_w_on`（循环，跟随，画在人物**后面**；4 秒） | 40 × 44 |
| `olaf_fx_r_cast` | view_effects `league_olaf_r_cast`（BIG；跟随，画在人物上面） | 48 × 50 |
| `olaf_fx_r_on` | view_buffs `league_olaf_r_on`（BIG；循环，跟随，画在人物**后面**；3 秒起） | 36 × 30 |
| `olaf_fx_p_4` | view_buffs `league_olaf_p_4`（循环，跟随，画在人物上面；血量很低时） | 32 × 40 |

- `league_olaf_fx`（跟随的小图、飞行物、buff）和 `league_olaf_big`（`e_hit`、`r_cast`、`r_on`）两张 sheet，和技能数据里写的一致。
- 技能数据要改一处：飞行中的斧头 view_projectiles `league_olaf_q_axe` 的 tag 从 `q_axe` 改成 `q_fly`（`q_axe` 留给插在地上的斧头，build_olaf.py 的 views_p）。
- `q_axe` 每 15 tick 重放一次（axe_step），3 帧加起来约 15 tick；斧头最多插 300 tick。`q_land`、`e_hit`、`r_cast` 是竖着的画面，放在 ViewEffect 里。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法，斧头实物除外）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半；红蓝两方都看一遍（左右对称）。
