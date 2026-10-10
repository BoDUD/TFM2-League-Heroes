# 涤魂圣枪 赛娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 21 张特效图。** 造型和动作已定（`design/senna_design.png`，45×46 格，8 倍）。
> - 大小对照 `design/senna_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度。每条写的大小都是游戏像素（格）。
> - `design/senna_shots.png`：普攻开炮、Q 开炮、W 射出、R 开炮那几帧的动作和站姿（4 倍），青色十字是脚下。
> - 参考图：`refs/lol_icons.png` 是英雄联盟里她的 Q、W、R 技能图标——**颜色照它**；`refs/lol_fx_ref.png` 是她自己的特效贴图（不少是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行。两张都只在本地用。
> - 颜色：**黑雾（普攻、被动亡魂、Q 光束、W、E、R 的核心）是深青绿色的烟雾，中间发亮的青绿到白色的芯**；**圣光（Q 治疗、R 外面那层宽光和护盾）是金白色**。
> - **特效要亮**：黑雾也要有发亮的芯和亮边，暗底上一眼能看见；最深的烟雾颜色只给很少的点缀。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。飞出去的炮弹、W 的黑雾、R 的两道会转到飞行方向，**往右飞着画**；Q 的光束**横着画，左端是炮口**。W 炸开、E 的黑雾是**竖着的画面**（往上冒），上下不能颠倒。
> - 特效照下面第 1–21 条和「所有特效图的规则」画，每张一个 PNG，文件名 `senna_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`senna_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「赦除」 | 遗物炮打出黑雾炮弹；技能和普攻给敌方英雄打上印记，下一发普攻收走一缕亡魂，赛娜得到一层黑雾（攻击、射程变大） | `senna_fx_a_shot` · `senna_fx_a_hit` · `senna_fx_p_mark` · `senna_fx_p_take` · `senna_fx_p_gain` |
| 技能 1 = Q「黑暗洞灭」 | 一道穿过敌人的长光束：伤害、减速敌人，治疗光束上的友方英雄 | `senna_fx_q_beam` · `senna_fx_q_hit` · `senna_fx_q_heal` · `senna_fx_q_slow` |
| 技能 2 = W「无尽厮守」 | 射出一团黑雾，缠住第一个敌人，1 秒后炸开，定身周围的敌人 | `senna_fx_w_mist` · `senna_fx_w_hit` · `senna_fx_w_cling` · `senna_fx_w_burst` · `senna_fx_w_root` |
| E「黑雾咒附」（自动） | 被突脸时涌出黑雾，她和身边的队友隐身、加速 | `senna_fx_e_mist` · `senna_fx_e_ms` |
| 大招 = R「暗影燎原」 | 蓄力后打出横贯全场的一道光：中间的黑暗核心伤害敌方英雄，外面很宽的圣光给友方英雄护盾 | `senna_fx_r_core` · `senna_fx_r_light` · `senna_fx_r_hit` · `senna_fx_r_sh` · `senna_fx_r_shield` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 黑雾（普攻、被动、Q 光束、W、E、R 核心）：`#FFFFFF`、`#D8FFF0`、`#86F4CC`、`#3CCB9C`、`#1A8A6A`、`#0E5444`、`#08302A`；
  - 黑雾里最暗的烟（只给一点）：`#4A4F5E`、`#2C2F3A`、`#1A1B22`；
  - 圣光（Q 治疗、R 宽光和护盾）：`#FFFFFF`、`#FFF8DA`、`#FFE79A`、`#F7C65A`、`#D9952E`、`#9A5E1C`；
- **飞出去的东西往右飞着画**（`a_shot`、`w_mist`、`r_core`、`r_light`）：游戏会把它转到飞行方向。`q_beam` 横着画、左端是炮口。
- **挂在人身上和地上的画面左右对称**，按每条写的站位画；命中居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。`w_burst`、`e_mist` 是竖着的画面，不能颠倒。
- 套在角色身上的特效（印记、收魂、层数、治疗、缠身、护盾）：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（21 张）

21 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻射程约 62000，Q 光束长 130000，W 炸开半径 28000，E 隐身范围 40000，R 圣光半宽 100000）。

### 1. `senna_fx_a_shot.png`：普攻：遗物炮的黑雾炮弹（往右飞，循环），4 帧

遗物炮打出的一发炮弹：一团拉长的黑雾，中间一颗亮青绿色的芯（芯是白色到浅青），后面拖一小段飘散的黑雾尾巴。往右飞（往左飞时游戏会把整张转过来）。约 14 格长、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: a CANNON SHOT of the Black Mist flying RIGHT, 4 frames, a seamless loop: an elongated bolt 14 x 7 squares - a glowing sea-green core (white to pale green) at its front half, wrapped in swirling dark teal mist that trails off to the left in wisps; the wisps change shape every frame.
Layout: one horizontal row of 4 equal cells, each 288x160 (image 1152x160) (16 px a square here); the core 4 squares left of the cell's right edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `senna_fx_a_hit.png`：普攻命中：黑雾炸开（目标身上），4 帧

炮弹打中：一下白色的光，一团青绿色的雾往四周炸开，几颗亮绿的碎光飞散，然后变成淡淡的黑雾散掉（参考 AutoAttack_Mis_Energy、AutoAttack_RingMult）。左右对称，居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: a MIST SHOT HIT, 4 frames: 1 a white flash 5 squares across; 2 a burst of sea-green mist 12 squares across with a ring of bright motes; 3 the mist puffs at their widest (14 squares), motes flying out; 4 faint dark mist dissolving. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x256 (image 1024x256) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `senna_fx_p_mark.png`：被动 赦除：敌方英雄身上的印记（循环），4 帧

被赛娜标记的敌方英雄（下一发普攻会收走他的魂）：人物胸口高度一圈细细的青绿色光环（从斜上方看的椭圆，约 22 × 7 格），两小团发光的黑雾沿着光环转圈。**中间空着**，不要盖住人。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: A LOOPING MARK round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: a thin ring of sea-green light seen from above at an angle (an ellipse 22 x 7 squares, 1 square thick) at chest height, two small glowing wisps of mist circling along it (a quarter turn further each frame). Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 416x224 (image 1664x224) (16 px a square here); the ring's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `senna_fx_p_take.png`：被动 收魂：从目标身上抽出一缕亡魂（目标身上），5 帧

普攻收走印记：目标身上一下青绿色的光，一缕黑雾亡魂（一个小小的、有两点发光眼睛的鬼影，青绿色的雾做的身子）从目标胸口被扯出来，往上飘、消散（参考 Wraith_Alpha、halfWraith）。左右对称，居中画。约 18 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: A SOUL TORN OUT of a target, 5 frames: 1 a sea-green flash 6 squares across at chest height; 2 a small wraith of mist (a ghostly hooded shape 8 x 10 squares with two glowing pale-green eye dots) pulled out of the chest; 3 the wraith rising 8 squares higher, a mist trail below it; 4 the wraith near the top of the cell, fading; 5 a few rising wisps. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 320x448 (image 1600x448) (16 px a square here); the target's chest 9 squares (144 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `senna_fx_p_gain.png`：被动 黑雾层数+1：亡魂飞进赛娜的炮（她身上），4 帧

收下一层黑雾：一小团发光的亡魂雾从左右两边旋进来，在她腰间（炮的位置）合成一点亮光，一圈青绿色的光环一闪，然后淡出。**中间空着**，不要盖住人。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: A MIST STACK GAINED round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames: 1 two small glowing wisps entering from both sides at waist height (12 squares above the feet), 18 squares apart; 2 the wisps spiralling in, 8 squares apart; 3 they meet in a bright sea-green spark at waist height, a ring of light (an ellipse 20 x 6 squares) flashing; 4 the ring fading. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 384x480 (image 1536x480) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `senna_fx_q_beam.png`：Q 黑暗洞灭：从炮口穿过敌人的黑暗光束（长条，大图），5 帧

Q 打出的一道直直的光束（横着、往右）：先是一条细细的青绿色光线，然后一下变成粗的黑雾光束——中间一条白到浅青的亮芯，外面包着翻滚的青绿色雾，雾的上下边缘不齐、一缕一缕地往外冒，最后光束变细、雾散开（参考 Q_coreBolt、Q_BeamDissolve、Q_shotWave）。**很长：约 130 格长、10 格粗**。左端是炮口（起点），右端最远处。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: a LONG STRAIGHT BEAM of the Black Mist, horizontal, from its LEFT end (the cannon's muzzle) to its RIGHT end 130 squares away, 5 frames: 1 a thin sea-green line 1 square thick the whole length; 2 the full beam 8 squares thick - a white to pale-green core 2 squares thick along the middle, wrapped in rolling sea-green and dark teal mist with ragged edges curling out above and below; 3 the beam at its brightest, wisps peeling off its edges; 4 the beam thinning to 4 squares, the mist drifting apart; 5 a few fading wisps along the line.
Layout: one vertical column of 5 equal cells, each 1088x112 (image 1088x560) (8 px a square here); the beam's line along the middle of every cell, its left end 2 squares from the cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `senna_fx_q_hit.png`：Q 命中敌人：黑雾刺穿（目标身上），4 帧

光束扫过的每个敌人：一道横着的黑雾刺痕（中间亮、两头细），青绿色碎光往外炸，然后雾散掉。左右对称，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: a PIERCING HIT, 4 frames: 1 a white flash 5 squares across; 2 a horizontal streak of mist 16 squares long (brightest and thickest in the middle, thin at both ends), sea-green shards bursting out; 3 the shards farther out, the streak fading; 4 faint wisps. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 288x256 (image 1152x256) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `senna_fx_q_heal.png`：Q 治疗队友：金白色的圣光从身上升起（队友身上），4 帧

光束穿过的友方英雄被治疗：脚下一圈金色的光，几道金白色的光柱和小十字光点从脚下往上升到头顶，然后淡出（参考 W_healWave）。**中间空着**，不要盖住人。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a holy-light ramp (#FFFFFF, #FFF8DA, #FFE79A, #F7C65A, #D9952E, #9A5E1C).
Effect: A HEAL round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames: 1 a ring of gold light at the feet (an ellipse 20 x 6 squares); 2 thin white-gold light rays and small plus-shaped sparkles rising from the ring up the sides of the body; 3 the sparkles near the head (26 squares above the feet), the ring fading; 4 a few fading sparkles. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 384x480 (image 1536x480) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `senna_fx_q_slow.png`：Q 减速：脚下的黑雾（循环），4 帧

被 Q 减速：脚下地上一圈黑雾在慢慢转，几缕雾往上飘一点。只画脚下一圈，不要盖住人。左右对称，从斜上方看的椭圆。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: LOOPING MIST at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 18 x 6 squares of dark teal mist swirling on the ground with a pale-green glow at its rim, a few wisps rising 3 squares. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 352x160 (image 1408x160) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `senna_fx_w_mist.png`：W 无尽厮守：飞出去的一团黑雾触手（往右飞，循环），4 帧

W 射出去的一团黑雾：一颗发亮的青绿色雾核，几条细细的黑雾触手在它后面和周围扭动（像小蛇一样一扭一扭），往右飞（参考 W_Tendrils、W_worm）。约 16 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: a CLUMP OF MIST TENDRILS flying RIGHT, 4 frames, a seamless loop: a glowing sea-green mist core 5 squares across at the front, three or four thin dark-teal tendrils (1-2 squares thick) writhing behind and around it like small snakes, their curves changing every frame; 16 x 9 squares in all.
Layout: one horizontal row of 4 equal cells, each 320x192 (image 1280x192) (16 px a square here); the core 4 squares left of the cell's right edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `senna_fx_w_hit.png`：W 命中：黑雾扑到敌人身上（目标身上），4 帧

黑雾打中第一个敌人：一下青绿色的光，黑雾像泼出去一样扑满目标的身体轮廓周围，几条触手甩出去，然后贴到身上（接着由 w_cling 循环）。左右对称，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: a MIST SPLASH HIT, 4 frames: 1 a sea-green flash 6 squares across; 2 dark teal mist splashing out 18 squares across, tendrils flung out to the sides; 3 the tendrils curling back in; 4 thin mist clinging in a ring 14 squares across. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 320x320 (image 1280x320) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `senna_fx_w_cling.png`：W 缠身：黑雾缠在敌人身上（循环），4 帧

黑雾缠着目标 1 秒（然后炸开定身周围的敌人）：几条黑雾触手绕着身体从脚往上缠，一明一暗地发着青绿色的光。**中间空着**，不要盖住人。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: LOOPING MIST TENDRILS clinging round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: three thin dark-teal tendrils spiralling up round the body from the feet to the shoulders (20 x 26 squares in all), glowing sea-green and pulsing brighter in frames 2 and 4, a few wisps drifting off. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 384x448 (image 1536x448) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `senna_fx_w_burst.png`：W 炸开：黑雾在地上炸成一圈触手（地上，大图），6 帧

1 秒后黑雾炸开、定住周围的敌人：中间一下白绿色的光，一圈黑雾冲击波沿着地面往外推（从斜上方看的椭圆，最大约 56 × 20 格），一圈触手从地里往上钻出来抓，然后触手缩回、雾散（参考 W_Circle、W_Ground_A_Errode、W_Root_EnergyBlurry）。**竖着的画面**（触手往上钻），上下不能颠倒。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: A MIST ERUPTION ON THE GROUND, UPRIGHT (tendrils reach up; never upside down), 6 frames: 1 a white-green flash 8 squares across at the ground point; 2 a shockwave ring of dark mist rolling out along the ground (an ellipse 34 x 12 squares) with a glowing rim; 3 the ring at its widest (56 x 20), a ring of tendrils bursting up out of the ground 10 squares tall; 4 the tendrils grasping, curling over; 5 the tendrils sinking back, mist drifting; 6 faint mist on the ground. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 496x256 (image 2976x256) (8 px a square here); the ground point 10 squares (80 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `senna_fx_w_root.png`：W 定身：脚下的触手抓住双腿（循环），4 帧

被定身：脚下地上一摊黑雾，几条触手从里面钻出来缠住小腿（到膝盖高度），一明一暗地发光。只画脚下和小腿高度。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: LOOPING ROOTING TENDRILS at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a pool of dark mist on the ground (an ellipse 20 x 6 squares) with four short tendrils rising out of it to knee height (8 squares) round the legs, glowing sea-green, pulsing. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 384x256 (image 1536x256) (16 px a square here); the pool's middle 4 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `senna_fx_e_mist.png`：E 黑雾咒附：她身边涌出的一大团黑雾（地上，大图），6 帧

开 E：黑雾从她脚下涌出来，在地上铺开成一大片（从斜上方看的椭圆，约 80 × 28 格），雾往上翻腾到大约 12 格高，雾里有几点青绿色的光点，然后雾慢慢淡去（参考 E_mistTrail、E_mistWipe、Senna_E_mistWall）。画在人物下面，**中间不要太浓**（人站在里面）。竖着的画面（雾往上翻），上下不能颠倒。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: A BLACK MIST SHROUD ON THE GROUND, UPRIGHT (the mist billows up; never upside down), 6 frames: 1 mist pouring out at the middle (an ellipse 20 x 8 squares); 2 the mist spreading over the ground (50 x 18); 3 the mist at its widest (80 x 28 squares), billowing up 12 squares at its back edge, a few sea-green motes glinting in it; 4 the mist rolling; 5 thinning; 6 faint patches. Thinner in the middle (figures stand inside it). Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 704x352 (image 4224x352) (8 px a square here); the ellipse's middle 16 squares (128 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `senna_fx_e_ms.png`：E 加速：脚下飘散的黑雾（循环），4 帧

隐身加速的时候：脚下一小团黑雾往两边飘散，几缕雾往上飘。只画脚下。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: LOOPING MIST WISPS streaming off a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat cloud of dark teal mist on the ground (16 x 5 squares) with wisps curling off both ends and rising 4 squares. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 352x192 (image 1408x192) (16 px a square here); the cloud's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `senna_fx_r_core.png`：R 暗影燎原：飞过去的黑暗核心（往右飞，循环，大图），4 帧

大招的核心光束头：一根粗粗的黑雾长矛往右冲，最前面一点白到浅青的亮光，身子是翻滚的青绿色和深青的雾，后面拖着长长的黑雾尾巴（参考 R_coreBolt、R_swirlingSmokeBeam）。往右飞。约 44 格长、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) with a few dark smoke squares (#4A4F5E, #2C2F3A, #1A1B22).
Effect: the DARK CORE OF A HUGE SHOT flying RIGHT, 4 frames, a seamless loop: a thick lance of the Black Mist 44 x 16 squares - a white to pale-green spearhead of light at its right end 8 squares long, a body of rolling sea-green and dark teal mist behind it, a long ragged mist tail streaming off to the left; the swirls change every frame.
Layout: one horizontal row of 4 equal cells, each 384x160 (image 1536x160) (8 px a square here); the spearhead 2 squares left of the cell's right edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `senna_fx_r_light.png`：R 暗影燎原：跟在外面的一大片金色圣光（往右飞，循环，大图），4 帧

大招外面那层很宽的光：一道竖着的、很高的金白色光幕往右推进（像一面光墙的前沿：最右边一条亮白色的边，往左慢慢变成金色、再变透明），光幕上有几条往后拖的光带和小光点（参考 R_holyWave_Grad、R_runeLines）。**竖着的长条**：约 24 格宽、96 格高。往右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a holy-light ramp (#FFFFFF, #FFF8DA, #FFE79A, #F7C65A, #D9952E, #9A5E1C).
Effect: a WIDE WALL OF HOLY LIGHT moving RIGHT, 4 frames, a seamless loop: a very tall upright band 24 x 96 squares - its right edge a bright white line 2 squares thick, fading leftwards through pale gold and amber to transparent, long streaks of light trailing left along it and small sparkles drifting; brightest in its middle third, softer toward the top and bottom ends.
Layout: one horizontal row of 4 equal cells, each 256x816 (image 1024x816) (8 px a square here); the band's middle at the middle of every cell, its bright edge 2 squares left of the cell's right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `senna_fx_r_hit.png`：R 命中敌方英雄：黑雾炸开（目标身上，大图），5 帧

大招打中敌方英雄：刺眼的白光，一圈黑雾冲击波炸开，青绿色的碎光往四周飞，几点金光闪一下，然后黑雾散掉。左右对称，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a Black Mist ramp (#FFFFFF, #D8FFF0, #86F4CC, #3CCB9C, #1A8A6A, #0E5444, #08302A) and a holy-light ramp (#FFFFFF, #FFF8DA, #FFE79A, #F7C65A, #D9952E, #9A5E1C).
Effect: a HUGE MIST BLAST HIT, 5 frames: 1 a blinding white flash 10 squares across; 2 a ring of dark teal mist bursting out to 24 squares, sea-green shards and a few gold sparks flying; 3 the ring at 28 x 30 squares, the shards at their farthest; 4 the mist breaking up; 5 a few fading wisps. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 512x544 (image 2560x544) (16 px a square here); centered in every cell (the target's middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `senna_fx_r_sh.png`：R 护盾到身上：金光落下罩住队友（队友身上），4 帧

圣光扫过友方英雄、给上护盾的一下：头顶一下金白色的光往下落，变成一圈金色的光环从头滑到脚，再升起一个淡金色的圆罩子的边（之后由 r_shield 循环）。**中间空着**，不要盖住人。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a holy-light ramp (#FFFFFF, #FFF8DA, #FFE79A, #F7C65A, #D9952E, #9A5E1C).
Effect: A SHIELD GRANTED round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames: 1 a white-gold flash above the head (30 squares above the feet); 2 a ring of gold light (an ellipse 24 x 7 squares) sliding down the body to the waist; 3 the ring at the feet, the rim of a round pale-gold shield bubble (28 x 34 squares, 1-2 squares thick) rising; 4 the bubble rim complete, softer. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 512x608 (image 2048x608) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `senna_fx_r_shield.png`：R 护盾：队友身上的金色护罩（循环），4 帧

护盾还在的时候：一个淡淡的金白色圆罩子的边（1–2 格粗，左上最亮）罩着人，罩边上几个小光点慢慢转。**中间空着**，不要盖住人。左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a holy-light ramp (#FFFFFF, #FFF8DA, #FFE79A, #F7C65A, #D9952E, #9A5E1C).
Effect: A LOOPING SHIELD BUBBLE round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: the rim of a round pale-gold bubble 28 x 34 squares, 1-2 squares thick, brightest at the upper left, a few small sparkles travelling along the rim. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 512x608 (image 2048x608) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `senna_fx_a_shot` | view_projectiles `league_senna_a_shot`（循环，朝飞行方向转） | 14 × 7 |
| `senna_fx_a_hit` | view_effects `league_senna_a_hit`（跟随，画在人物上面） | 14 × 14 |
| `senna_fx_p_mark` | view_buffs `league_senna_p_mark`（循环，跟随，画在人物上面；4 秒） | 22 × 10 |
| `senna_fx_p_take` | view_effects `league_senna_p_take`（跟随，画在人物上面） | 18 × 26 |
| `senna_fx_p_gain` | view_effects `league_senna_p_gain`（跟随，画在人物最上面） | 22 × 28 |
| `senna_fx_q_beam` | view_projectiles `league_senna_q_beam`（BIG；光束，从她身前一直伸到 130 格外） | 130 × 10 |
| `senna_fx_q_hit` | view_effects `league_senna_q_hit`（跟随，画在人物上面） | 16 × 14 |
| `senna_fx_q_heal` | view_effects `league_senna_q_heal`（跟随，画在人物上面） | 22 × 28 |
| `senna_fx_q_slow` | view_buffs `league_senna_q_slow`（循环，跟随，画在人物下面；1.25 秒） | 18 × 6 |
| `senna_fx_w_mist` | view_projectiles `league_senna_w_mist`（循环，朝飞行方向转） | 16 × 9 |
| `senna_fx_w_hit` | view_effects `league_senna_w_hit`（跟随，画在人物上面） | 18 × 18 |
| `senna_fx_w_cling` | view_buffs `league_senna_w_cling`（循环，跟随，画在人物上面；1 秒后炸开） | 20 × 26 |
| `senna_fx_w_burst` | view_effects `league_senna_w_burst`（BIG；不跟随，画在人物上面；炸开的位置） | 58 × 30 |
| `senna_fx_w_root` | view_buffs `league_senna_w_root`（循环，跟随，画在人物下面；1.5 秒） | 20 × 12 |
| `senna_fx_e_mist` | view_effects `league_senna_e_mist`（BIG；不跟随，画在人物下面；她的位置，半径约 40 格内的队友一起隐身） | 84 × 40 |
| `senna_fx_e_ms` | view_buffs `league_senna_e_ms`（循环，跟随，画在人物下面；4 秒） | 18 × 8 |
| `senna_fx_r_core` | view_projectiles `league_senna_r_core`（BIG；循环，朝飞行方向转；伤害敌方英雄的那一道） | 44 × 16 |
| `senna_fx_r_light` | view_projectiles `league_senna_r_light`（BIG；循环，朝飞行方向转；给友方英雄护盾的那一道，很宽） | 24 × 96 |
| `senna_fx_r_hit` | view_effects `league_senna_r_hit`（BIG；跟随，画在人物上面） | 28 × 30 |
| `senna_fx_r_sh` | view_effects `league_senna_r_sh`（跟随，画在人物上面） | 28 × 34 |
| `senna_fx_r_shield` | view_buffs `league_senna_r_shield`（循环，跟随，画在人物上面；有护盾时） | 28 × 34 |

- `league_senna_fx`（跟随的小图、飞行物、buff）和 `league_senna_big`（`q_beam`、`w_burst`、`e_mist`、`r_core`、`r_light`、`r_hit`）两张 sheet，和技能数据里写的一致（build_senna.py 的 views）。
- `q_beam` 是 LineRange 光束的画：按光束线居中放（Kayn W 的做法），左端对炮口；`r_light` 很高，导入时量一下它在 1080p 下的样子，太大就缩到 72 格高。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半；红蓝两方都看一遍（左右对称）。
