# 刀锋之影 泰隆：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型和动作已定（`design/talon_design.png`，32×42 格，8 倍）。
> - 大小对照 `design/talon_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/talon_shots.png`：普攻刺中、W 甩出刀刃、Q 落地刺击、Q 近身回旋斩、E 落地、R 刀刃甩出那几帧的动作（4 倍），青色十字是脚下。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里泰隆自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。颜色：**刀刃是亮银白带冰蓝刃光；血、被动、W 回程的刀痕是暗红；隐身是暗蓝紫的影子烟；火星白金；回血用绿**。
> - **特效要看得见**：每个形状都要有亮的芯或亮边（银白、冰蓝、亮红），暗色只用在里面，在深色战场上一眼能看见。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。飞行的两张刀刃（`w_out`、`w_back`）会转到飞行方向，所以朝右画、上下对称。
> - 每张一个 PNG，文件名 `talon_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子，不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`talon_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「刀锋之末」 | 腕刃前刺；技能打中英雄叠伤口，叠满 3 层后下一次普攻让他流血 | `talon_fx_a_hit` · `talon_fx_p_wound` · `talon_fx_p_bleed` |
| 技能 1 = W「斩草除根」 | 扇形甩出一排刀刃，飞到尽头再飞回来，回程减速 | `talon_fx_w_out` · `talon_fx_w_back` · `talon_fx_w_hit` · `talon_fx_w_slow` |
| 技能 2 = Q「诺克萨斯式外交」 | 跃向目标刺击（身边有敌人时原地回旋斩）；击杀回血 | `talon_fx_q_leap` · `talon_fx_q_hit` · `talon_fx_q_heal` |
| 自动「刺客之道」 | 被包围时翻身跃开并加速 | `talon_fx_e_vault` · `talon_fx_e_haste` |
| 大招 = R「暗影突袭」 | 一圈刀刃向四周甩出，隐身加速；隐身结束或出手时刀刃飞回 | `talon_fx_r_out` · `talon_fx_r_back` · `talon_fx_r_hit` · `talon_fx_r_on` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、刀光、火星、血雾、烟没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **刀刃**画成清楚的弯刃形状（刃尖、刃背），亮银白身、冰蓝刃光、白色高光，一眼能认出是刀，不要糊成一团光。
- 颜色（按每条写的用）：
  - 银白（刀刃）：`#FFFFFF`、`#EEF4FF`、`#C9D4E8`、`#93A2BE`、`#63708C`、`#3C4560`；
  - 冰蓝（刃光）：`#FFFFFF`、`#D8ECFF`、`#8EC4FF`、`#4A86F0`、`#2A4FC0`、`#1A2A78`；
  - 暗红（血、刀痕）：`#FFE0D8`、`#FF8A7A`、`#F23A30`、`#C0141C`、`#7A0810`、`#400408`；
  - 暗蓝紫（隐身的影子）：`#C8D4FF`、`#8A9AF0`、`#5A5CC8`、`#3A3490`、`#241E5A`、`#140F30`；
  - 火星：`#FFFFFF`、`#FFF2D8`、`#FFD08A`、`#F59A3A`；
  - 回血：`#F0FFF0`、`#B8F5B0`、`#6AD860`、`#2E9A3A`；
- **飞行的画面朝右画，而且上下对称**（`w_out`、`w_back`）：游戏会把它转到飞行方向。
- **挂在人身上和地上的画面左右对称**，按每条写的站位画；命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人；光环、烟只画外面一圈，不要盖住人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：R 的刀圈半径约 30000）。

### 1. `talon_fx_a_hit.png`：普攻命中：腕刃刺击（目标身上），4 帧

腕刃刺中：一道银白的短刃光斜着交叉成小 X，交点一下白光，带一点冰蓝的刃光和几颗火星。左右对称，居中画。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78) and a spark ramp (#FFFFFF, #FFF2D8, #FFD08A, #F59A3A).
Effect: a BLADE STAB HIT, 4 frames: 1 a white flash 4 squares across; 2 two thin bright silver-white blade streaks 10 squares long crossing in an X through the middle, an ice-blue gleam along them, sparks flying out; 3 the streaks thinning, sparks farther out; 4 fading lines. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `talon_fx_p_wound.png`：被动「刀锋之末」：伤口层数（敌人头顶，循环），4 帧

被泰隆的技能划伤：敌人头顶上方三道并排的红色短刀痕（像被刀划过的三道口子），一明一暗地脉动，滴下一两滴血。只画刀痕，不要画人，在格子上半部。左右对称。约 10 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blood ramp (#FFE0D8, #FF8A7A, #F23A30, #C0141C, #7A0810, #400408).
Effect: a small LOOPING WOUND MARK above a head (do NOT draw the figure), 4 frames, a seamless loop: three short parallel slanted crimson slash marks side by side (each 6 squares long, 2 apart), a thin silver glint on each, pulsing brighter and dimmer, one or two drops of blood falling below. Left-right symmetric (the middle slash upright, the outer two mirrored).
Layout: one horizontal row of 4 equal cells, each 160x128 (image 640x128) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `talon_fx_p_bleed.png`：被动触发：流血爆发（目标身上），6 帧

第三层伤口被普攻引爆：目标身上一下子迸出一团暗红的血雾和血滴（参考原版的 P_blood_drop 和 bloodcloud），三道刀痕一闪，然后血雾慢慢散开往下滴。左右对称，居中画。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a blood ramp (#FFE0D8, #FF8A7A, #F23A30, #C0141C, #7A0810, #400408) and a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560).
Effect: a BLEED BURST on a target, 6 frames: 1 three bright silver-red slash lines flashing across the middle; 2 a burst of crimson blood drops and a dark red mist cloud 14 squares across; 3 the cloud at 18 squares, drops flying out and down; 4 the cloud thinning, drops falling; 5 a few drops and wisps of dark red; 6 faint drops. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 320x320 (image 1920x320) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `talon_fx_q_leap.png`：Q 跃击起跳：脚下的刀光和尘土（地上），4 帧

泰隆蹬地跃起：脚下一圈小小的尘土往两边溅开，加上一道往上的冰蓝色刃光残影。左右对称，脚下居中。约 24 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78) and a dust ramp (#E8DCC8, #B8A890, #807060).
Effect: a LEAP-OFF PUFF on the ground (do NOT draw the figure), 4 frames: 1 a small burst of dust at the middle of the bottom; 2 dust splashing out to both sides (an ellipse 20 x 5 squares) and a thin ice-blue vertical streak rising from the middle 10 squares tall; 3 the dust spreading thinner, the streak fading upward; 4 faint dust. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 384x224 (image 1536x224) (16 px a square here); the dust's middle at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `talon_fx_q_hit.png`：Q 命中：跃击刺中（目标身上），5 帧

从天而降的一刺：目标身上一道很亮的竖直银白刀光往下劈，接着一个暗红的血花 X 字迸开（参考原版 Q1_blood），几颗火星。左右对称，居中画。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blood ramp (#FFE0D8, #FF8A7A, #F23A30, #C0141C, #7A0810, #400408) and a spark ramp (#FFFFFF, #FFF2D8, #FFD08A, #F59A3A).
Effect: a HEAVY STAB HIT, 5 frames: 1 a bright vertical silver-white blade streak 14 squares long striking down through the middle; 2 a white flash at the middle and a crimson X of two blood slashes 14 squares long bursting out; 3 blood drops and sparks flying out, the X at full size; 4 the X fading to dark red, drops falling; 5 faint drops. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 288x288 (image 1440x288) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `talon_fx_q_heal.png`：Q 击杀回血（泰隆身上），5 帧

Q 击杀目标回血：泰隆身边升起几个小小的绿色十字和光点，从脚下往上飘，最后散开。不要画人，左右对称，人形的位置留空。约 16 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a heal ramp (#F0FFF0, #B8F5B0, #6AD860, #2E9A3A).
Effect: a HEAL around a standing figure (do NOT draw the figure), 5 frames: 1 a soft green glint at the feet; 2 four small pale green plus signs and sparkles rising beside the figure's outline (two each side); 3 higher, brighter; 4 near the top, fading; 5 a few sparkles. Left-right symmetric; the middle of the cell left empty for the figure.
Layout: one horizontal row of 5 equal cells, each 256x384 (image 1280x384) (16 px a square here); the feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `talon_fx_w_out.png`：W 斩草除根：飞出去的一扇刀刃（随飞行方向转），4 帧循环

泰隆扇形甩出的刀刃：四把银色的弯刃排成一个扇形一起往右飞（像四把小镰刀，刃尖朝前，上下对称地张开），刃上有冰蓝色的刃光，后面几道短短的银白拖尾。朝右画（游戏会转到飞行方向），上下对称。约 14 格长、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78).
Effect: a FAN OF FOUR FLYING BLADES going to the RIGHT, 4 frames, a seamless loop: four curved silver sickle blades side by side in a fan (the two outer ones angled 20 degrees up and down, the two inner ones nearly level), each 7 squares long with its hooked point forward, a bright ice-blue gleam on every edge, short silver-white streaks trailing behind them to the left; the gleam travels along the edges each frame. Symmetric above and below the flight line.
Layout: one horizontal row of 4 equal cells, each 288x352 (image 1152x352) (16 px a square here); the fan's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `talon_fx_w_back.png`：W 回程：飞回来的刀刃（随飞行方向转），4 帧循环

刀刃飞回泰隆：同一扇四把弯刃，但刃尖还是朝飞行方向，后面拖着弯弯的暗红色刀痕（参考原版 w_blade_return 的红色波浪拖尾）。朝右画，上下对称。约 14 格长、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blood ramp (#FFE0D8, #FF8A7A, #F23A30, #C0141C, #7A0810, #400408).
Effect: the same FAN OF FOUR CURVED SILVER BLADES flying to the RIGHT, but trailing long wavy CRIMSON streaks behind them to the left (each blade drags a 10-square red ribbon that waves a little each frame); 4 frames, a seamless loop. Symmetric above and below the flight line.
Layout: one horizontal row of 4 equal cells, each 352x352 (image 1408x352) (16 px a square here); the blades' middle at the middle of the right half of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `talon_fx_w_hit.png`：W 命中（目标身上），3 帧

刀刃划过：一道横着的银白刀光一闪，几颗冰蓝色的碎光。左右对称，居中画。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78).
Effect: a SMALL BLADE CUT, 3 frames: 1 a bright silver-white horizontal slash streak 9 squares long through the middle with an ice-blue edge; 2 the streak with small blue and silver shards flying up and down; 3 fading glints. Left-right symmetric.
Layout: one horizontal row of 3 equal cells, each 160x160 (image 480x160) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `talon_fx_w_slow.png`：W 回程减速（敌人脚下，循环），4 帧

被回程的刀刃减速：敌人脚下一小圈暗红色的刀痕在地上，几道细细的冰蓝刃光缠着脚闪烁。只画脚下一圈，不要画人。左右对称，斜上方看的椭圆。约 16 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blood ramp (#FFE0D8, #FF8A7A, #F23A30, #C0141C, #7A0810, #400408).
Effect: a LOOPING SLOW MARK at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 14 x 5 squares of short crimson slash marks on the ground, thin silver-blue glints flickering round it. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 288x128 (image 1152x128) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `talon_fx_e_vault.png`：E 刺客之道：翻越起跳（地上），5 帧

泰隆翻身跃开：脚下尘土往两边溅起，一道弯弯的冰蓝色弧光从地面翻上去（像翻跟头划出的弧线）。左右对称，脚下居中。约 26 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78) and a dust ramp (#E8DCC8, #B8A890, #807060).
Effect: a VAULT on the ground (do NOT draw the figure), 5 frames: 1 a burst of dust at the bottom middle; 2 dust splashing to both sides (an ellipse 22 x 6) and a thin ice-blue arc rising from the middle, curving over like a somersault path, 16 squares tall; 3 the arc complete, bright; 4 the arc fading from its base, the dust thinner; 5 faint. Left-right symmetric (the arc goes straight up and folds over symmetrically, like a fountain).
Layout: one horizontal row of 5 equal cells, each 416x288 (image 2080x288) (16 px a square here); the dust's middle at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `talon_fx_e_haste.png`：E 加速（脚下，循环），4 帧

翻越后加速跑：脚下几道冰蓝色的风线往两边掠过，一点小尘土。只画脚下，不要画人。左右对称，斜上方看。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78).
Effect: LOOPING SPEED LINES at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: short ice-blue and white horizontal streaks streaming out to both sides from under the feet (an ellipse 16 x 6), a few dust specks, moving outward each frame. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 320x144 (image 1280x144) (16 px a square here); the middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `talon_fx_r_out.png`：R 暗影突袭：刀刃向四周甩出（地上，围着泰隆），6 帧

泰隆原地旋身，一圈银色的刀刃从他身上往四周飞出去：十几把带冰蓝刃光的弯刃从中间向外呈放射状飞散，到外圈停住，地上一圈暗蓝色的影子冲击环。左右对称，从斜上方看的椭圆（宽是高的 2 倍）。约 60 格宽、30 格高。中间留出人形的位置。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78) and a shadow ramp (#C8D4FF, #8A9AF0, #5A5CC8, #3A3490, #241E5A, #140F30).
Effect: a RING OF BLADES BURSTING OUT round a standing figure (do NOT draw the figure), 6 frames: 1 a bright blue-white flash at the middle; 2 twelve curved silver blades (each 6 squares long, ice-blue gleam) flying outward in all directions, at a third of the way out, a dark blue shadow shock ring under them; 3 the blades two thirds out; 4 the blades at the outer ellipse (58 x 28 squares), spinning in place, the shock ring at full size; 5 the ring fading to blue-violet smoke, the blades still there, dimmer; 6 faint blades and smoke. Left-right symmetric; seen from above at an angle (an ellipse twice as wide as tall); the middle of the cell left empty for the figure.
Layout: one horizontal row of 6 equal cells, each 1024x512 (image 6144x512) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `talon_fx_r_back.png`：R 收刀：刀刃从四周飞回泰隆（地上），6 帧

隐身结束，外圈的刀刃一起飞回泰隆：十几把弯刃从外圈椭圆向中间收拢，每把后面拖一道暗红色的刀痕，最后在中间一下亮光。左右对称，斜上方看的椭圆。约 60 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blood ramp (#FFE0D8, #FF8A7A, #F23A30, #C0141C, #7A0810, #400408).
Effect: a RING OF BLADES CONVERGING round a standing figure (do NOT draw the figure), 6 frames: 1 twelve curved silver blades on the outer ellipse (58 x 28 squares) turning their points inward; 2 the blades flying inward, a third of the way, each trailing a crimson streak behind it; 3 two thirds in, the streaks long; 4 the blades meeting at the middle in a bright white-red flash; 5 the flash fading, crimson streaks fading; 6 faint red sparks. Left-right symmetric; seen from above at an angle.
Layout: one horizontal row of 6 equal cells, each 1024x512 (image 6144x512) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `talon_fx_r_hit.png`：R 刀刃命中（目标身上），4 帧

刀刃扫中：一道银白刀光斜着划过，冰蓝的刃光，迸出一点暗红。左右对称（交叉成 X），居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a steel ramp (#FFFFFF, #EEF4FF, #C9D4E8, #93A2BE, #63708C, #3C4560) and a blood ramp (#FFE0D8, #FF8A7A, #F23A30, #C0141C, #7A0810, #400408) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78).
Effect: a BLADE HIT, 4 frames: 1 a white flash 4 squares across; 2 a bright silver X of two slash streaks 12 squares long with ice-blue edges, a few crimson drops bursting out; 3 the streaks thinning, drops farther out; 4 fading. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 224x224 (image 896x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `talon_fx_r_on.png`：R 隐身（泰隆脚下和身边，循环），4 帧

泰隆隐身疾行：身边一层暗蓝紫色的影子烟在慢慢盘旋（参考原版 r_caS_invis_swirl），脚下一小圈影子，几缕烟往上飘，一两道冰蓝光点闪过。只画烟，不要画人，人形的位置留空，烟是半透明感觉但用实色像素画（稀疏的像素点）。左右对称。约 24 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (bright cores, dark parts only inside), colours only from a shadow ramp (#C8D4FF, #8A9AF0, #5A5CC8, #3A3490, #241E5A, #140F30) and a blue gleam ramp (#FFFFFF, #D8ECFF, #8EC4FF, #4A86F0, #2A4FC0, #1A2A78).
Effect: a LOOPING STEALTH SHROUD round a standing figure (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse of dark blue-violet shadow at the feet (20 x 5 squares) with a pale blue rim, thin wisps of blue-violet smoke spiralling up both sides of the figure's outline to 30 squares high, drawn sparse (scattered pixels, not a solid mass), one or two ice-blue sparkles; the wisps turning a little each frame. Left-right symmetric; the middle of the cell left empty for the figure.
Layout: one horizontal row of 4 equal cells, each 384x544 (image 1536x544) (16 px a square here); the feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `talon_fx_a_hit` | view_effects `league_talon_a_hit`（跟随，画在人物上面） | 12 |
| `talon_fx_p_wound` | view_buffs `league_talon_p_wound`（循环，跟随；技能打中英雄后挂在他身上） | 10 × 8 |
| `talon_fx_p_bleed` | view_effects `league_talon_p_bleed`（跟随，画在人物上面） | 20 |
| `talon_fx_q_leap` | view_effects `league_talon_q_leap`（不跟随，画在人物下面；起跳的地方） | 24 × 14 |
| `talon_fx_q_hit` | view_effects `league_talon_q_hit`（跟随，画在人物上面） | 18 |
| `talon_fx_q_heal` | view_effects `league_talon_q_heal`（不跟随，画在人物上面） | 16 × 24 |
| `talon_fx_w_out` | view_projectiles `league_talon_w_out`（朝飞行方向转） | 14 × 20 |
| `talon_fx_w_back` | view_projectiles `league_talon_w_back`（朝飞行方向转；从远处飞回泰隆） | 14 × 20 |
| `talon_fx_w_hit` | view_effects `league_talon_w_hit`（跟随） | 10 |
| `talon_fx_w_slow` | view_buffs `league_talon_w_slow`（循环，跟随，画在人物上面） | 16 × 6 |
| `talon_fx_e_vault` | view_effects `league_talon_e_vault`（不跟随，画在人物下面） | 26 × 18 |
| `talon_fx_e_haste` | view_buffs `league_talon_e_haste`（循环，跟随，画在人物下面） | 18 × 8 |
| `talon_fx_r_out` | view_effects `league_talon_r_out`（不跟随，画在人物上面；半径约 30 格） | 60 × 30 |
| `talon_fx_r_back` | view_effects `league_talon_r_back`（不跟随，画在人物上面） | 60 × 30 |
| `talon_fx_r_hit` | view_effects `league_talon_r_hit`（跟随，画在人物上面） | 14 |
| `talon_fx_r_on` | view_buffs `league_talon_r_on`（循环，跟随，画在人物下面） | 24 × 34 |

- `q_leap`、`e_vault`、`r_out`、`r_back`、`q_heal` 是 CasterViewEffect 不跟随：画面左右对称，红色方不会反。
- 清掉 Codex 给光描的最深色边（`import_hecarim.py` / `import_zed.py` 的做法）；核对交回的张数和这份清单；量每张的亮度和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。
