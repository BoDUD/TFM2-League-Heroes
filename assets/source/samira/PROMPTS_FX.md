# 沙漠玫瑰 莎弥拉：给 Codex 的特效提示词（第 3 步）

> **这一份是 23 张特效图。** 造型和动作已定（`design/samira_design.png`，8 倍，40 行）。
> - 大小对照 `design/samira_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。莎弥拉 32×40 格。每条写的大小都是游戏像素（格）。
> - `design/samira_shots.png`：定稿动作（4 倍），青色十字是特效的起点（枪口、剑弧中心、脚下、头顶），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里莎弥拉自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版皮肤：**枪火和子弹是白热的金黄、橙色；大剑的火焰是深红到红橙；R 有深红色的玫瑰花瓣；E 冲刺扬起黄沙；被动评分字母金黄到红**。
> - **特效要亮**：每个形状都要用最亮的几档和白热的芯，暗底上一眼能看见。
> - **围着人的剑环、枪火只画外圈，中间留空**，不然会把人整个挡住。
> - **方向（重要）**：子弹一律画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。枪口火光、挥剑弧光、Q 的半月斩、E 的拖尾都画成**朝右**。挂在她身上循环的画面（`w_spin`、`r_on`）和 `e_reset`、`g_up`、`g_s` 要**左右对称**，人朝左朝右都用同一张。评分字母**不要镜像**。
> - 特效照下面第 1–23 条和「所有特效图的规则」画，每张一个 PNG，文件名 `samira_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`samira_fx_done.zip`）放在 outputs 里，或放在 `outputs/samira-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「悍勇本色」 | 远处开枪、近身挥剑；被控住的敌方英雄会被她冲过去挑飞；打出不同的招式时评分从 E 升到 S，头顶显示字母 | `a_bullet` · `a_flash` · `a_hit` · `a_slash` · `a_slash_hit` · `j_up` · `g_letters` · `g_up` · `g_s` |
| 技能 1 = Q「交火」 | 敌人在身边就用剑横扫面前的半月范围，否则开枪打出一发直线子弹（打中第一个敌人） | `q_flash` · `q_bullet` · `q_hit` · `q_slash` · `q_slash_hit` |
| 技能 2 = E「狂飙」→ W「锋旋」 | 冲向敌方英雄并穿过去，路上砍中的敌人受伤；落地接锋旋：原地转圈挥剑砍两下，转的时候受到的普攻伤害降低；击杀英雄刷新 E | `e_dash` · `e_hit` · `e_reset` · `w_spin` · `w_hit` |
| 大招 = R「炼狱扳机」 | 评分到 S 才能放：原地转圈双枪乱射 2 秒，周围的敌人每 0.2 秒挨一枪，期间吸血 | `r_on` · `r_flash` · `r_bullet` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、刀光、烟、火星没有黑描边，也不要用最深的颜色给形状描一圈边**。只有被动的评分字母有 1 格深色描边（`#1A0A0E`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 枪火（枪口火光、子弹、枪打中）：`#FFFFFF`、`#FFF4C2`、`#FFD24A`、`#FF9A1E`、`#E8520E`、`#9E2208`；
  - 剑火（挥剑弧光、半月斩、锋旋、剑打中、挑飞）：`#FFFFFF`、`#FFE2D2`、`#FF8A64`、`#F0402A`、`#C8102A`、`#6E0A18`；
  - 玫瑰花瓣（R）：`#FFB4C4`、`#F25A7E`、`#C8264A`、`#7E1230`；
  - 金色（评分字母、升级闪光、E 刷新）：`#FFFFFF`、`#FFF0A0`、`#FFD040`、`#E89A10`、`#A85A08`；
  - 黄沙（E 冲刺、挑飞的尘土）：`#F2DDB4`、`#D2B07C`、`#A8844E`、`#6E5232`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（23 张）

23 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，Q 半月斩半径 32000、子弹宽 5000，E 冲刺砍中的范围半径 22000，W 锋旋半径 32000，R 的射程半径 55000）。

### 1. `samira_fx_a_bullet.png`：普攻子弹（飞行中，循环），4 帧

莎弥拉普攻打出的子弹：一颗短短的白金色发光弹头，后面一小段橙色的曳光尾巴（参考 BA_MuzzleGradients、Q_Bullet_Glow、Q_Trail）。朝右飞（尾巴在左）。**上下对称**（往左飞时会上下翻）。4 帧无缝循环（弹头一闪一闪、尾巴抖动）。约 12 格长、4 格高，弹头在格子右边四分之三处。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208).
Effect: a BULLET TRACER in flight to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a white-hot slug 3 squares long and 2 tall at the front, a tapering gold-to-orange tracer trail 9 squares long to its LEFT; the slug flickers and the trail shimmers each frame.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); the slug's front 3/4 of the way across and vertically centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `samira_fx_a_flash.png`：普攻开火：枪口火光（画进她自己的开火帧），3 帧

左轮开火的那一下：枪口前一团白金色的星形火光，往右喷出一小束橙色的火舌，几道尖细的光芒（参考 BA_MuzzleFlash_Backdrop、BA_Sharp_Ray、BA_MuzzleGradients）。**朝右**（枪口在格子左边中间）。3 帧：1 最亮最大，2 变小、火舌往右，3 几点火星。约 14 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208).
Effect: a GUN MUZZLE FLASH pointing RIGHT, 3 frames: the muzzle point is 2 squares from the LEFT edge, vertically centered; 1 a white-hot star flash 6 squares across at the muzzle with 4 sharp rays and a gold-orange flame cone shooting 10 squares to the RIGHT; 2 the flash smaller, the cone thinner; 3 a few fading sparks.
Layout: one horizontal row of 3 equal 16:12 cells, image size 768x192 (each cell 256x192, 16 px a square); the muzzle point 2 squares from the left edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `samira_fx_a_hit.png`：普攻子弹打中（目标身上），4 帧

子弹打中：一个白金色的四角星形闪光，几点橙色火星飞出去（参考 BA_Tar_Flare、Q_Impact_Flare、Q_Embers）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208).
Effect: a BULLET HIT, 4 frames: 1 a white-hot four-pointed star flash 8 squares across at the center; 2 the star smaller, 5 gold-orange sparks flying out; 3 sparks further out; 4 a few fading embers.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `samira_fx_a_slash.png`：普攻挥剑：剑砍下去的火焰弧光（画进她自己的挥砍帧），3 帧

近身普攻那一剑：大剑从右上往右下劈下去，剑身后面拖一道新月形的红橙色火焰弧光，边缘白亮（参考 BA_Outer_Flare、BA_Outer_Flare_Erode、R_Swipe_Edge、Q_Swipe_Erode）。**朝右**：弧从格子右上方弯到右下方，凸的一边朝右。3 帧：1 整道弧最亮，2 弧变细、尾端碎成火星，3 几点火星。约 28 格宽、30 格高，弧的圆心在格子左边三分之一处的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18).
Effect: a SWORD SLASH ARC facing RIGHT, 3 frames: a crescent of crimson blade-fire 4 squares thick at its middle, bulging to the RIGHT, sweeping from the top right of the cell down to the bottom right, a white-hot leading edge on its outer side, the inner edge fading to red; 1 the whole arc at its brightest; 2 the arc thinner, its tail breaking into sparks; 3 a few fading sparks along the path.
Layout: one horizontal row of 3 equal 30:32 cells, image size 1440x512 (each cell 480x512, 16 px a square); the arc's center of curvature 1/3 of the way across and vertically centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `samira_fx_a_slash_hit.png`：普攻挥剑打中（目标身上），4 帧

大剑砍中：一道斜着的红色刀痕闪过，白色的芯，几点火星（参考 Q_Impact_Flare、Q_Melee_Flash）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18).
Effect: a SWORD HIT, 4 frames: 1 a diagonal crimson slash streak 14 squares long through the center (from the top right down to the bottom left), a white-hot core; 2 the streak thinner, a flash 6 squares across at its middle, sparks; 3 sparks scattering; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `samira_fx_j_up.png`：被动：挑飞（被控住的敌方英雄身上），4 帧

被动的连击：莎弥拉冲到被控住的敌人身边，从下往上一剑把他挑起来：一道从地面往上撩的红橙色弧光，脚下一小团沙尘（参考 Q_Air_swoosh、BA_Outer_Flare、E_Dash_DirtTrail）。中间是人，不要画人。4 帧：1 脚下沙尘、弧光从脚下起，2 弧光往上最亮，3 弧光到头顶、火星，4 淡去。约 20 格宽、28 格高，敌人的站位点在格子底部往上 4 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18) and a desert-sand ramp (#F2DDB4, #D2B07C, #A8844E, #6E5232).
Effect: an UPWARD SWORD SWOOSH lifting a figure (do NOT draw the figure; leave its place empty), 4 frames: 1 a puff of sand dust 12 squares wide at the standing point, a crimson blade-fire arc starting at the ground; 2 the arc sweeping UP past the figure's place, at its brightest, 4 squares thick, white-hot edge; 3 the arc's tip above the figure's head, sparks; 4 fading sparks and dust.
Layout: one horizontal row of 4 equal 22:30 cells, image size 1408x480 (each cell 352x480, 16 px a square); the standing point 4 squares above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `samira_fx_q_bullet.png`：Q 交火：远程的子弹（飞行中，循环），4 帧

Q 用枪时射出的子弹：比普攻的大一号，白热的弹头外面一圈金色的光，后面一道长长的橙红色火焰尾巴，两边几道细细的气流线（参考 Q_Bullet_Glow、Q_Trail、Q_SideTrail、Q_Flare_Ray）。朝右飞。**上下对称**。4 帧无缝循环。约 22 格长、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208).
Effect: a BIG FLAMING BULLET in flight to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a white-hot slug 4 squares long and 3 tall with a gold glow round it at the front, a tapering orange-to-red flame trail 16 squares long to its LEFT, two thin pale streaks along its sides; the flame flickers each frame.
Layout: one horizontal row of 4 equal 24:10 cells, image size 1536x160 (each cell 384x160, 16 px a square); the slug's front 7/8 of the way across and vertically centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `samira_fx_q_flash.png`：Q 开枪：更大的枪口火光（画进她自己的开火帧），3 帧

Q 用枪的那一下：比普攻大一圈的枪口火光，一团白金色的爆闪，往右喷出一大束橙红色火舌和尖锐光芒，几点火星（参考 Q_Muzzle_Flash、Q_Flare_Ray、BA_Sharp_Ray）。**朝右**（枪口在格子左边中间）。3 帧：1 最大最亮，2 火舌往右变长变细，3 火星。约 20 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208).
Effect: a BIG MUZZLE BLAST pointing RIGHT, 3 frames: the muzzle point 2 squares from the LEFT edge, vertically centered; 1 a white-hot burst 8 squares across at the muzzle with 6 sharp rays and a big gold-orange flame cone shooting 14 squares to the RIGHT; 2 the cone longer and thinner, red at its edges; 3 fading sparks.
Layout: one horizontal row of 3 equal 22:16 cells, image size 1056x256 (each cell 352x256, 16 px a square); the muzzle point 2 squares from the left edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `samira_fx_q_hit.png`：Q 子弹打中（目标身上），4 帧

Q 的子弹打中：一下大一点的白金色爆闪，四片尖锐的光刺往外，几点橙色火星（参考 Q_Impact_Flare、Q_Embers、Q_Throw_Sparks）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208).
Effect: a BIG BULLET IMPACT, 4 frames: 1 a white-hot flash 10 squares across with 4 sharp shard-like rays; 2 a gold ring 14 squares across spreading, 6 orange sparks; 3 sparks further out; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `samira_fx_q_slash.png`：Q 交火：近身的半月剑斩（施法者身上，大），4 帧

Q 在近身时用剑：一记横扫面前的半月斩，一大道新月形的红橙色火焰弧光从她头顶上方扫到身前的地面，凸的一边朝右，边缘白亮，扫过的地方几片火星（参考 Q_Melee_Border、Q_Melee_Border_Burn_In、Q_Melee_Flash、Q_Swipe_Filler、Q_Swipe_Erode）。中间是人，不要画人。**朝右**。4 帧：1 弧光从头顶上方起、最亮，2 整道弧扫完（最大，约 40 格高），3 弧光变细碎成火星，4 淡去。约 44 格见方，站位点在格子左边 12 格、底部往上 6 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18).
Effect: a HUGE HALF-MOON SWORD SWEEP in front of a figure (do NOT draw the figure; leave its place empty), facing RIGHT, 4 frames: a crescent of crimson blade-fire bulging to the RIGHT, its inner edge 6 squares in front of the figure's place; 1 the arc starting above the figure's head, white-hot; 2 the full arc swept from above the head down to the ground in front, 40 squares tall and 6 thick at its middle, white-hot outer edge, red inner edge, sparks along it; 3 the arc thinner, breaking into sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 2816x704 (each cell 704x704, 16 px a square); the standing point 12 squares from the left edge and 6 squares above the bottom in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `samira_fx_q_slash_hit.png`：Q 剑斩打中（目标身上），4 帧

半月斩砍中：一个红色的刀痕交叉，白色的芯，一圈火星（参考 Q_Melee_Flash、Q_Impact_Flare）。约 18 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18).
Effect: a HEAVY SWORD HIT, 4 frames: 1 two crossing crimson slash streaks 16 squares long (an X) with a white-hot center 6 squares across; 2 the streaks thinner, a ring of 8 sparks; 3 sparks further out; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `samira_fx_e_dash.png`：E 狂飙：冲刺的拖尾（施法者身上，大），4 帧

E 冲刺：她身后拖出几道红橙色的速度线，脚下扬起一路黄沙，几颗弹壳和小石子飞起来（参考 Samira_E_Dash、E_Dash_DirtTrail、E_Rocks、E_Shells）。中间是人，不要画人。**朝右冲**：拖尾和沙尘都在站位点的**左边**（身后）。4 帧：1 速度线和沙尘从脚下起，2 拖尾最长（往左约 36 格），3 变淡、沙尘散开，4 几点沙。约 48 格宽、24 格高，站位点在格子右边往左 8 格、底部往上 4 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18) and a desert-sand ramp (#F2DDB4, #D2B07C, #A8844E, #6E5232).
Effect: a DASH TRAIL behind a figure rushing to the RIGHT (do NOT draw the figure; leave its place empty), 4 frames: 1 three crimson-orange speed streaks and a kick of sand dust starting at the standing point; 2 the streaks at their longest, trailing 36 squares to the LEFT of the standing point at waist and knee height, the dust cloud along the ground behind, 2-3 small brass shell casings and pebbles flying; 3 the streaks fading, the dust spreading; 4 a few drifting dust specks.
Layout: one horizontal row of 4 equal 48:24 cells, image size 3072x384 (each cell 768x384, 16 px a square); the standing point 8 squares from the right edge and 4 squares above the bottom in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `samira_fx_e_hit.png`：E 冲刺砍中（目标身上），4 帧

冲过去砍中：一道横着的红色刀痕，一小团沙尘（参考 Q_Melee_Flash、E_Dash_DirtTrail）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18) and a desert-sand ramp (#F2DDB4, #D2B07C, #A8844E, #6E5232).
Effect: a DASH SLASH HIT, 4 frames: 1 a horizontal crimson slash streak 14 squares long through the center with a white-hot core; 2 the streak thinner, a puff of sand dust; 3 sparks and dust; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `samira_fx_e_reset.png`：E 刷新：击杀后的金光（施法者身上），4 帧

E 的击杀刷新：她身上一下金色的光环往外扩，几颗金色的星光往上飘（参考 Taunt_Star、Ring_Glow）。**左右对称**。约 22 格，居中画（她的腰部）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #E89A10, #A85A08).
Effect: a RESET FLASH round a figure, SYMMETRIC LEFT AND RIGHT, 4 frames: 1 a gold ring 10 squares across with a white flash; 2 the ring spreading to 18 squares, 4 four-pointed gold stars rising; 3 the ring fading, stars higher; 4 a few fading stars.
Layout: one horizontal row of 4 equal square cells, image size 1536x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `samira_fx_w_spin.png`：W 锋旋：绕身旋转的剑刃火环（她身上，循环，大），4 帧

W 锋旋：她原地转圈挥剑，身边一圈扁扁的红橙色剑刃火环在转，环上几道白亮的刀光，几点火星甩出去（参考 W_Border、W_Block_Flash、R_Swipe_Edge）。中间是人，不要画人：**只画环，人的位置留空**（环从人的前面和后面绕过，前面那一段可以盖住一点腰）。**左右对称**（人朝左朝右都用这一张）。4 帧无缝循环（刀光每帧往前转四分之一圈）。环约 60 格宽、22 格高，环的中心在站位点上面 14 格；格子 64 格宽、40 格高，站位点在底部往上 6 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18).
Effect: a SPINNING BLADE RING round a figure (do NOT draw the figure; leave its place empty; draw only the ring), SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless loop: a flattened ring of crimson blade-fire 60 squares wide and 22 tall (seen from above at an angle), its center 14 squares above the standing point, 2-3 squares thick, with 3 bright white-hot blade glints on it that move a quarter of the way round each frame, a few sparks flung outward; the figure's place inside the ring stays empty.
Layout: one horizontal row of 4 equal 64:40 cells, image size 4096x640 (each cell 1024x640, 16 px a square); the standing point 6 squares above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `samira_fx_w_hit.png`：W 锋旋砍中（目标身上），4 帧

被锋旋砍中：一道弯弯的红色刀痕扫过，白色的芯，几点火星（参考 R_Swipe_Edge、Q_Melee_Flash）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18).
Effect: a WHIRL SLASH HIT, 4 frames: 1 a curved crimson slash streak 14 squares long sweeping across the center, white-hot core; 2 the streak thinner, 5 sparks; 3 sparks further out; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `samira_fx_r_on.png`：R 炼狱扳机：开大时身边的枪火和玫瑰花瓣（她身上，循环，大），4 帧

R 炼狱扳机：她原地转圈双枪乱射，身边一圈一闪一闪的金橙色枪火和曳光、几道红色的气旋，深红色的玫瑰花瓣往外飘（参考 R_Swipe、R_Swipe_Edge、R_Electric_Energy、R_Energy_Ray、R_Rose_Petals）。中间是人，不要画人：**只画周围，人的位置留空**。**左右对称**。4 帧无缝循环（枪火每帧换位置、花瓣往外飘）。约 64 格宽、56 格高，站位点在格子底部往上 6 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208), a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18) and a rose-petal ramp (#FFB4C4, #F25A7E, #C8264A, #7E1230).
Effect: a GUNFIRE STORM round a spinning figure (do NOT draw the figure; leave its place empty; draw only round it), SYMMETRIC LEFT AND RIGHT, 4 frames, a seamless loop: a flattened swirl of crimson fire 56 squares wide round the figure's waist, 6-8 short white-gold tracer streaks and muzzle sparks flashing outward in all directions at shoulder height (in new places each frame), 8-10 crimson rose petals (each 2-3 squares) drifting outward; the figure's place stays empty.
Layout: one horizontal row of 4 equal 64:56 cells, image size 4096x896 (each cell 1024x896, 16 px a square); the standing point 6 squares above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `samira_fx_r_flash.png`：R 开火：两把枪口的小火光（画进她自己的开大帧），2 帧

开大时每一发：枪口一小团白金色的火光，往右喷一点火舌（参考 BA_MuzzleFlash_Backdrop、BA_Sharp_Ray）。**朝右**（枪口在格子左边中间）。2 帧：1 亮，2 小。约 10 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208).
Effect: a SMALL MUZZLE FLASH pointing RIGHT, 2 frames: the muzzle point 2 squares from the LEFT edge, vertically centered; 1 a white-hot flash 4 squares across with 3 short rays and a gold flame 6 squares to the RIGHT; 2 smaller, sparks.
Layout: one horizontal row of 2 equal 12:10 cells, image size 384x160 (each cell 192x160, 16 px a square); the muzzle point 2 squares from the left edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `samira_fx_r_bullet.png`：R 的子弹（飞行中，循环），3 帧

炼狱扳机射向周围敌人的子弹：一颗红橙色的曳光弹，后面一段淡淡的烟尾（参考 R_Tracer、R_Bullet、R_Smoke_Trail）。朝右飞。**上下对称**。3 帧无缝循环。约 16 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208).
Effect: a RED TRACER ROUND in flight to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a white-hot slug 3 squares long at the front, an orange-red tracer 7 squares long behind it, then a faint grey-orange smoke wisp 5 squares long to its LEFT (use the darker gunfire shades for the smoke).
Layout: one horizontal row of 3 equal 18:8 cells, image size 864x128 (each cell 288x128, 16 px a square); the slug's front 7/8 of the way across and vertically centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `samira_fx_r_hit.png`：R 子弹打中（敌人身上），4 帧

被炼狱扳机打中：一小团橙红色的火光，一片深红色的玫瑰花瓣飘开（参考 BA_Tar_Flare、R_Rose_Petals）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gunfire ramp (#FFFFFF, #FFF4C2, #FFD24A, #FF9A1E, #E8520E, #9E2208) and a rose-petal ramp (#FFB4C4, #F25A7E, #C8264A, #7E1230).
Effect: a FIERY HIT, 4 frames: 1 a white-gold flash 8 squares across; 2 a small orange-red burst 12 squares across, one crimson rose petal (3 squares) flying off; 3 embers and the petal drifting; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `samira_fx_g_letters.png`：被动「悍勇本色」：头顶的连招评分字母 E D C B A S（她身上，常驻），6 格（每格一个字母）

被动的连招评分：每打出一种不同的招式升一级，从 E 升到 S，字母显示在她头顶。6 个格子依次是 **E、D、C、B、A、S** 六个粗体像素字母，像格斗游戏的评分：E、D、C 偏金黄，B、A 金橙，**S 最大最亮**，带一点火焰和红色的边（参考 Passive_timer_ring、P_Screen_Flames）。这里字母要有 1 格深色描边，才能在战斗里看清；字母**不要镜像**，正常的方向。每格一个字母，居中。约 10 格高（S 约 12 格）。

```text
Pixel art game UI sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, bold blocky letters with a 1-square dark outline #1A0A0E so they read over the battle, colours only from a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #E89A10, #A85A08) and a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18).
Effect: SIX STYLE GRADE LETTERS, one per cell, in this order: E, D, C, B, A, S - bold blocky pixel letters (upright, normal reading direction, NOT mirrored) like a fighting game's style rank: E, D and C 9 squares tall in gold, B and A 10 squares tall in gold-orange with a white highlight on their top edges, S 12 squares tall, the brightest - gold with a white-hot top edge, a crimson underside and 3-4 small flame tongues licking up from it.
Layout: one horizontal row of 6 equal square cells, image size 1536x256 (each cell 256x256, 16 px a square); each letter centered in its cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `samira_fx_g_up.png`：被动升级：头顶的金色闪光（她身上），3 帧

评分升一级的那一下：头顶一下金色的星形闪光，几颗小星星往外蹦（参考 Taunt_Star、Ring_Glow）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #E89A10, #A85A08).
Effect: a GRADE-UP SPARKLE, SYMMETRIC LEFT AND RIGHT, 3 frames: 1 a white-gold four-pointed star flash 10 squares across; 2 a thin gold ring 14 squares across, 4 tiny stars popping out; 3 fading stars.
Layout: one horizontal row of 3 equal square cells, image size 864x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `samira_fx_g_s.png`：被动到 S：头顶的火焰金光（她身上），4 帧

评分到 S 的那一下：头顶一下大团金红色的爆闪，一圈火焰光环往外扩，火星往上窜（参考 Passive_timer_ring、P_Screen_Flames、Ring_Glow）。**左右对称**。约 28 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF0A0, #FFD040, #E89A10, #A85A08) and a crimson blade-fire ramp (#FFFFFF, #FFE2D2, #FF8A64, #F0402A, #C8102A, #6E0A18).
Effect: an S-RANK BURST, SYMMETRIC LEFT AND RIGHT, 4 frames: 1 a white-gold flash 12 squares across; 2 a ring of crimson and gold flame 22 squares across spreading, 6 sparks shooting up; 3 the ring at 28 squares, thinner, sparks higher; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1920x480 (each cell 480x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `samira_fx_a_bullet` | view_projectiles `league_samira_a_bullet`（朝飞行方向转，画成朝右飞；上下对称） | 12 × 4 |
| `samira_fx_a_flash` | 画进 `samira_attack` 第 4 帧起（枪口，`design/samira_shots.png` attack 4 的十字；导入时烘进精灵帧） | 14 × 10 |
| `samira_fx_a_hit` | view_effects `league_samira_a_hit`（跟随，画在人物上面） | 12 |
| `samira_fx_a_slash` | 画进 `samira_attack_m` 第 4 帧起（`design/samira_shots.png` attack_m 4 的十字是弧的中心；导入时烘进精灵帧） | 28 × 30 |
| `samira_fx_a_slash_hit` | view_effects `league_samira_a_slash_hit`（跟随，画在人物上面） | 16 |
| `samira_fx_j_up` | view_effects `league_samira_j_up`（跟随，画在人物上面） | 20 × 28 |
| `samira_fx_q_bullet` | view_projectiles `league_samira_q_bullet`（朝飞行方向转，画成朝右飞；上下对称） | 22 × 7 |
| `samira_fx_q_flash` | 画进 `samira_skill` 第 3 帧起（枪口，`design/samira_shots.png` skill 3 的十字；导入时烘进精灵帧） | 20 × 14 |
| `samira_fx_q_hit` | view_effects `league_samira_q_hit`（跟随，画在人物上面） | 16 |
| `samira_fx_q_slash` | view_effects `league_samira_q_slash`（BIG，施法者身上，跟随；格子里的站位点放到她脚下，导入时前面补空帧对上挥剑帧） | 44 × 44 |
| `samira_fx_q_slash_hit` | view_effects `league_samira_q_slash_hit`（跟随，画在人物上面） | 18 |
| `samira_fx_e_dash` | view_effects `league_samira_e_dash`（BIG，施法者身上，跟随；格子里的站位点放到她脚下） | 48 × 24 |
| `samira_fx_e_hit` | view_effects `league_samira_e_hit`（跟随，画在人物上面） | 16 |
| `samira_fx_e_reset` | view_effects `league_samira_e_reset`（施法者身上，不跟随；左右对称） | 22 |
| `samira_fx_w_spin` | view_buffs `league_samira_w_spin`（BIG，循环，画在人物上面；左右对称） | 64 × 40 |
| `samira_fx_w_hit` | view_effects `league_samira_w_hit`（跟随，画在人物上面） | 16 |
| `samira_fx_r_on` | view_buffs `league_samira_r_on`（BIG，循环，画在人物上面；左右对称） | 64 × 56 |
| `samira_fx_r_flash` | 画进 `samira_ult` 第 2–9 帧（两把枪口，`design/samira_shots.png` ult 2 的两个十字；朝左那把用镜像；导入时烘进精灵帧） | 10 × 8 |
| `samira_fx_r_bullet` | view_projectiles `league_samira_r_bullet`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 5 |
| `samira_fx_r_hit` | view_effects `league_samira_r_hit`（跟随，画在人物上面） | 14 |
| `samira_fx_g_letters` | view_buffs `league_samira_g1`…`g6`（每格一个字母：g1 = E … g6 = S；画在头顶，不旋转） | 10 × 10（S 12 × 12） |
| `samira_fx_g_up` | view_effects `league_samira_g_up`（施法者身上，不跟随，头顶；左右对称） | 16 |
| `samira_fx_g_s` | view_effects `league_samira_g_s`（施法者身上，不跟随，头顶；左右对称） | 28 |

- 画进精灵帧的（`a_flash`、`q_flash`、`r_flash`、`a_slash`）写进 `assets/source/native/samira_bake.json`，`import_native.py` 烘进 attack / skill / ult / attack_m 的帧（客户端只镜像英雄自己的帧，不镜像特效图：烬的枪口火光）；`r_flash` 朝左那把用镜像；火光在开火帧之内结束。
- 子弹从枪口出（开火帧枪口在站位点上面约 11.5 格）：`y_offset` 不超过 8000（子弹会朝目标的站位点斜飞），画面开头补几帧空的，让子弹飞过枪口（23 格）再出现；开枪的声音和火光、子弹在同一个 `Delayed` 里。
- `q_slash`、`e_dash` 在动作第一 tick 播放，跟随；`q_slash` 前面补空帧对上 skill_m 第 4 帧（140 ms）。`e_reset`、`g_up`、`g_s` 晚于第一 tick，`is_follow` 为 false，左右对称；`w_spin`、`r_on` 循环、左右对称；评分字母画在头顶（站位点上面约 34 格），不镜像。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim`，评分字母保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；子弹上下对称；Codex 交的如果是要求尺寸的 2 倍，缩一半。
