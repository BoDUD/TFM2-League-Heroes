# 暮光之眼 慎：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/shen_design.png`，37×46 格，8 倍）。
> - 大小对照 `design/shen_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度，右边是原版骑士。每条写的大小都是游戏像素（格）。
> - `design/shen_shots.png`：普攻横扫、Q 推掌召剑、E 飞扑、R 合十引导那几帧的动作和站姿（4 倍），青色十字是脚下。
> - 参考图：`refs/lol_icons.png` 是英雄联盟里他的 Q、E、R 技能图标——**颜色照它**；`refs/lol_fx_ref.png` 是他自己的特效贴图（不少是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行。两张都只在本地用。
> - 颜色：**灵剑、刃光、气合盾、R 都是紫色的灵光**（白色的芯、紫色的边）；**魂佑结界是蓝色的护光**；**影缚是暗紫色的影子烟**，烟里一条亮紫的光。
> - **灵剑（`q_blade`）是光做的剑**：照剑的形状画，但它是光，**不描黑边**。
> - **特效要亮**：每个形状都要有白色或最亮一档的芯，暗底上一眼能看见；最深的一档颜色只给很少的点缀（影子烟的暗色例外，但烟里要有亮紫的光）。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。飞回来的灵剑、冲刺的影子会转到飞行方向，**往右飞着画**。魂佑结界、E 撞中、R 开始和落地是**竖着的画面**（往上飘、往上升），上下不能颠倒。
> - 特效照下面第 1–15 条和「所有特效图的规则」画，每张一个 PNG，文件名 `shen_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`shen_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 剑劈；Q 之后的 3 次普攻被灵剑强化（额外打掉最大生命的一部分） | `shen_fx_a_hit` · `shen_fx_a_emp` |
| 被动 = 忍法！气合盾 | 放技能时给自己一个护盾 | `shen_fx_p_on` |
| 技能 1 = Q「奥义！暮临」 | 召回灵剑：灵剑从前方飞回他身边，路上砍中的敌人减速；回来后强化 3 次普攻 | `shen_fx_q_blade` · `shen_fx_q_hit` · `shen_fx_q_slow` · `shen_fx_q_1` |
| W「奥义！魂佑」（自动） | 灵剑回到身边、附近有敌方英雄时，在脚下展开结界：结界里的友方英雄格挡普攻 | `shen_fx_w_zone` · `shen_fx_w_safe` |
| 技能 2 = E「奥义！影缚」 | 冲向敌方英雄，路上撞到的敌人受伤并被嘲讽 | `shen_fx_e_dash` · `shen_fx_e_hit` |
| 大招 = R「秘奥义！慈悲度魂落」 | 给远处被控或被围的队友一个护盾，引导 2.5 秒后传送到他身边 | `shen_fx_r_cast` · `shen_fx_r_ch` · `shen_fx_r_shield` · `shen_fx_r_land` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、火花、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反；灵剑也是光，不描边）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 紫色灵光（灵剑、刃光、护盾、R）：`#FFFFFF`、`#F3EAFF`、`#D9C2FF`、`#B18AFF`、`#8456F2`、`#5A2EC2`、`#31167A`；
  - 蓝色护光（W 结界）：`#FFFFFF`、`#E4F3FF`、`#ABD8FF`、`#63AEF7`、`#3277DE`、`#1D49AB`、`#102866`；
  - 影子烟（E）：`#E9E2F5`、`#B9A9D6`、`#8572AE`、`#5A4884`、`#3A2C5C`、`#22183A`；
- **飞回来的灵剑、冲刺的影子往右飞着画**（`q_blade`、`e_dash`）：游戏会把它们转到飞行方向。
- **挂在人身上和地上的画面左右对称**，按每条写的站位画；命中居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2.5–3 倍）。`w_zone`、`e_hit`、`r_cast`、`r_land` 是竖着的画面，不能颠倒。
- 套在角色身上的特效（强化待命、气合盾、结界里的友方、R 的引导和护盾）：格子里留出空的人形位置，不要画人；护盾只画边。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻射程约 25000，灵剑的打击半径 6000，W 结界半径 22000，E 冲刺 66000、撞击半径 7000）。

### 1. `shen_fx_a_hit.png`：普攻命中：一道弧形的紫白刃光（目标身上），4 帧

剑砍中：一下白光，一道从目标头顶划过的弧形刃光（像倒过来的 U：∩，中间白、边缘紫，两头变细），几颗紫白火花，然后刃光变细、往上飘着淡出（参考 BA_Swipe、HitEffect）。左右对称，居中画。约 14 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: a SWORD SLASH HIT, 4 frames: 1 a white flash 4 squares across; 2 a curved crescent of blade light arching over the target like an upside-down U, 14 squares wide and 7 tall, 2 squares thick in the middle and thin at both ends (white core, violet edges), a few white-violet sparks; 3 the crescent thinner and 2 squares higher, the sparks farther out; 4 a few fading violet motes. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x224 (image 1024x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `shen_fx_a_emp.png`：强化普攻命中：两道交叠的弧光 + 灵剑碎光（目标身上），5 帧

灵剑强化过的普攻（额外打掉对方最大生命的一部分）：比普通的亮、大一圈——两道叠在一起的弧形刃光（∩，一大一小），中间一颗紫白色的星芒一闪，紫色的剑形碎光往四周飞，然后碎光淡出（参考 Crit_Swipe、BA_Flare-Sun、P_sword_shards）。左右对称，居中画。约 20 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: an EMPOWERED SWORD HIT, brighter and bigger than a plain hit, 5 frames: 1 a white-violet star flare 6 squares across; 2 two stacked crescents of blade light arching over the target (upside-down U shapes, 20 and 14 squares wide, white cores, violet edges); 3 the crescents at their brightest, small violet blade-shaped shards (2 x 4 squares) flying out in all directions; 4 the crescents thinning, the shards farther out (18 squares across); 5 a few fading shards and motes. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 352x320 (image 1760x320) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `shen_fx_q_blade.png`：Q 暮临：飞回来的灵剑（循环），4 帧

被召回、飞回慎身边的灵剑：一把**光做的剑**（不是金属、不描边）——直直的剑身 2 格粗、约 18 格长，**剑尖朝右**（白蓝色的芯、紫色的边），左端短短的护手和剑柄是更亮一点的紫色，柄头一点冰蓝色的光；剑后面（左边）拖一道 10 格长、飘动的紫色光尾，尾巴上掉下几颗小光点；4 帧光尾摆动，首尾能接上（参考 Q_sword_alpha、Q_mis_head、Q_mis_trail_empowered）。往右飞（往左飞时游戏会把整张转过来）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A) and, for the blade's cold core and the pommel glint, an azure ramp (#FFFFFF, #E4F3FF, #ABD8FF, #63AEF7, #3277DE, #1D49AB, #102866).
Effect: THE SPIRIT BLADE flying RIGHT, 4 frames, a seamless loop: a ghostly sword made of light (NOT metal: NO outline), a straight blade 2 squares thick and about 18 squares long with its POINT TO THE RIGHT (a pale white-blue core, violet edges), a short guard and hilt at its left end in brighter violet with an ice-blue glint on the pommel; behind it (to the left) a wavering violet light trail 10 squares long that sways a little every frame, small sparkles falling off the trail.
Layout: one horizontal row of 4 equal cells, each 512x224 (image 2048x224) (16 px a square here); the blade's middle at the middle of every cell, its point 4 squares (64 px) from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `shen_fx_q_hit.png`：Q 命中：灵剑穿过敌人（目标身上），4 帧

灵剑飞过、砍到路上每个敌人：一下白光，一道竖着的细长紫光（中间白、两头尖，像一根纺锤，约 14 格高、2 格宽），一道短短的横向光痕穿过它，周围一圈紫色的光旋往外转，然后淡出（参考 Q_hit_tar、Q_hit_swirls）。左右对称，居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: a SPIRIT BLADE PASSING HIT, 4 frames: 1 a white flash 5 squares across; 2 a tall thin spindle of violet light 14 squares tall and 2 wide (white core, pointed ends) crossed by a short horizontal streak 8 squares long, a ring of violet swirl motes round it; 3 the spindle thinner, the motes spiralling out to 14 squares; 4 a few fading motes. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x256 (image 1024x256) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `shen_fx_q_slow.png`：Q 减速：脚下一圈紫色的波纹（循环），4 帧

被灵剑减速：脚下的地上一圈紫色的波浪光带在转（参考 Q_SlowRing：两条起伏的紫白光带），几颗小光点往上飘。只画脚下的一圈，不要盖住人。左右对称，从斜上方看的椭圆。约 16 格宽、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: LOOPING SLOW WAVES at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse 16 x 5 squares made of two wavy violet-white light bands circling on the ground, the waves moving round a little every frame, a few small motes rising. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 320x128 (image 1280x128) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `shen_fx_q_1.png`：Q 强化普攻待命：腰间绕着转的三团紫色灵气（循环），4 帧

灵剑回来以后，接下来 3 次普攻被强化：腰的高度有三小团紫白色的灵气火（每团约 3 × 4 格，白芯紫边），沿着一个扁椭圆（约 30 × 8 格，从斜上方看）绕着他转，每帧转 1/4 圈；转到身后的那团暗一点。**中间空着**，不要盖住人。约 34 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: LOOPING CHARGED KI round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: three small violet-white ki flames (3 x 4 squares each, white cores, violet edges) orbiting the body at waist height on a flat ellipse 30 x 8 squares (seen from above at an angle), a quarter of a turn further every frame, the one passing behind the body dimmer, each leaving a short fading arc. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 576x416 (image 2304x416) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, the orbit's middle 16 squares (256 px) above the feet, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `shen_fx_p_on.png`：被动 气合盾：罩住他的紫色护盾（循环），4 帧

放技能时得到的护盾：一个罩住全身的圆护罩，**只画边**——边是一圈紫白色的光（1–2 格粗），外面一圈细细的紫色光芒往外放射（参考 P_shield：黑色的中心、紫色的光芒），边上几处更亮的光点慢慢转；中间是空的（顶多贴着边有极淡的一层紫光）。4 帧首尾能接上。**中间空着**，不要盖住人。左右对称。约 44 格宽、52 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: A LOOPING KI SHIELD round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: the rim of a round upright shield bubble 44 x 52 squares, 1-2 squares thick, white-violet light, short thin violet rays pointing outwards all round it, three brighter glints sliding round the rim a little every frame; the inside empty (at most a very faint violet haze near the rim). Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 768x896 (image 3072x896) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `shen_fx_w_zone.png`：W 魂佑：地上展开的蓝色结界（只放一次，大图），7 帧

灵剑回到身边时展开的结界（里面的友方英雄格挡普攻）：脚下的地上一圈蓝色的结界——1 中心一下白蓝色的光、一个小圈；2 光圈扩到全尺寸（从斜上方看的椭圆，约 46 × 18 格），沿着边扫过一道亮光；3–6 结界撑着：边是一圈 1–2 格粗的亮蓝光，里面淡淡的蓝光和几道灵气旋纹，边上不断有小光点往上飘（最高到地面上 12 格），这 4 帧彼此略有不同、连起来像在流动；7 结界淡出（参考 W_zone、W_Buf_Ring、W_Swipe、W_spark）。**竖着的画面**（光点往上飘），上下不能颠倒。左右对称。约 46 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an azure ward-light ramp (#FFFFFF, #E4F3FF, #ABD8FF, #63AEF7, #3277DE, #1D49AB, #102866) and, for small accents, a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: A WARD ZONE OPENING ON THE GROUND, UPRIGHT (motes rise; never upside down), played once, 7 frames: 1 a white-blue flash at the middle 6 squares across and a small ring; 2 the ring spreading to its full size - an ellipse 46 x 18 squares seen from above at an angle - a sweep of bright light running round its rim; 3, 4, 5, 6 the zone held: a bright azure rim 1-2 squares thick, a faint blue glow inside with a few soft spiral ki marks, small azure motes rising from the rim up to 12 squares above the ground, each frame a little different so they flow; 7 the zone fading. Left-right symmetric.
Layout: one horizontal row of 7 equal cells, each 800x544 (image 5600x544) (16 px a square here); the ellipse's middle 10 squares (160 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `shen_fx_w_safe.png`：W 结界里的友方：一圈护身的蓝光（循环），4 帧

站在结界里、普攻打不进来的友方：脚下一圈细细的蓝色护圈（约 22 × 6 格的椭圆），胸口高度两三颗蓝白色的小光点绕着身体飘，整体淡、不要太大。4 帧几乎一样（只是光点挪一点，游戏随时可能从头放）。**中间空着**，不要盖住人。左右对称。约 24 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an azure ward-light ramp (#FFFFFF, #E4F3FF, #ABD8FF, #63AEF7, #3277DE, #1D49AB, #102866) and, for small accents, a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: A LOOPING WARD round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop with frames nearly alike (it may restart at any frame): a thin azure ring on the ground at the feet (an ellipse 22 x 6 squares, 1 square thick), two or three small azure-white glints drifting round the body at chest height (16-20 squares above the feet), faint and small. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 480x576 (image 1920x576) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `shen_fx_e_dash.png`：E 影缚：冲刺时身后拖的影子（循环），3 帧

慎往前冲时身后拖着的一道影子：暗紫色的烟影（约 24 格长、8 格高，边缘破碎飘散），中间一条细细的亮紫色光线，越往左越淡；**只画在格子左半边**——影子的前端在中线左边 6 格（他本人在格子中间，影子在他身后），格子右半边空着。往右冲（往左时游戏会把整张转过来）。3 帧烟影翻动，首尾能接上（参考 E_color-smoke、AirSpiritStreak）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a dusky shadow-smoke ramp (#E9E2F5, #B9A9D6, #8572AE, #5A4884, #3A2C5C, #22183A) for the smoke and a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A) for its glow.
Effect: A SHADOW DASH TRAIL for a figure dashing RIGHT (do NOT draw the figure), 3 frames, a seamless loop: a streak of dusky violet shadow smoke 24 squares long and 8 tall with ragged drifting edges and a thin bright violet line through its core, fading out towards its left end; its front (right) end 6 squares LEFT of the middle column - the figure is at the middle, the trail behind it - the right half of the cell EMPTY; the smoke curls a little differently every frame.
Layout: one horizontal row of 3 equal cells, each 1024x256 (image 3072x256) (16 px a square here); the trail's middle row at the middle row of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `shen_fx_e_hit.png`：E 撞中并嘲讽：紫色的冲击圈 + 影子烟（目标身上），5 帧

冲刺撞中敌人（并嘲讽）：一下白光，一圈紫色的冲击光环往外炸（参考 E_blast_ring），后面一团暗紫色的影子烟往外喷，一道短短的紫色 X 刃光，然后光环变细、烟散掉（参考 E_Flare-Rainbow、E_sand、E_color-smoke）。**竖着的画面**，上下不能颠倒。左右对称，居中画。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a dusky shadow-smoke ramp (#E9E2F5, #B9A9D6, #8572AE, #5A4884, #3A2C5C, #22183A) for the smoke and a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A) for its glow.
Effect: a SHADOW DASH IMPACT, UPRIGHT, 5 frames: 1 a white flash 6 squares across; 2 a violet shock ring bursting out to 14 squares, a puff of dusky shadow smoke behind it, a short X of violet slash light at the middle; 3 the ring at 22 squares and thinner, smoke wisps flying out; 4 the ring breaking up, the smoke thinning; 5 a few fading smoke wisps and motes. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 448x448 (image 2240x448) (16 px a square here); centered in every cell (the target's middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `shen_fx_r_cast.png`：R 慈悲度魂落：开始引导时升起的紫色灵光（他身上，大图），6 帧

开大的一下（给远处的队友护盾，引导 2.5 秒后传送过去）：胸口一颗洋红紫的星芒一闪，脚下地上展开一圈紫色的光环，两条紫白色的光带从地上绕着身体螺旋往上升，升过头顶，火花和光点往上飘，然后光带化成光点淡出（参考 R_Flare-Rainbow、R_spiral-teleport、ring_purp）。**中间大部分空着**，不要盖住人。**竖着的画面**，上下不能颠倒。左右对称。约 44 格宽、60 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: STAND UNITED'S CALL round a figure (do NOT draw the figure; leave the inside EMPTY), UPRIGHT (light rises; never upside down), 6 frames: 1 a magenta-violet star flare at chest height (20 squares above the feet) 10 squares across; 2 a violet light ring opening on the ground at the feet (an ellipse 36 x 12 squares), two white-violet light ribbons starting to spiral up round the body; 3 the ribbons spiralling up past the shoulders, sparks flying; 4 the ribbons above the head (56 squares above the feet), motes rising; 5 the ribbons breaking into motes; 6 a few motes above the head. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 768x1024 (image 4608x1024) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `shen_fx_r_ch.png`：R 引导中：脚下光环 + 往上升的光柱（循环，大图），4 帧

引导的 2.5 秒：脚下地上一圈发光的紫色光环（约 34 × 11 格的椭圆），从光环升起一道光柱——**只画光柱的两条边**（两条竖着的亮紫光，相距约 34 格，往上越来越淡，最高到脚上 56 格），光柱里有紫色的光点和细细的光线不断往上升；4 帧首尾能接上（参考 R_spiral-teleport、R_ghost_overlay、cylinderlines）。**中间空着**，不要盖住人。左右对称。约 40 格宽、60 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: A LOOPING CHANNEL round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: a glowing violet ring on the ground at the feet (an ellipse 34 x 11 squares), a column of light rising from it drawn ONLY as its two side edges (two vertical violet-white light bands 34 squares apart, fading upwards, reaching 56 squares above the feet), violet motes and thin streaks rising inside the column, a little higher every frame. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 704x1024 (image 2816x1024) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `shen_fx_r_shield.png`：R 队友身上的护盾 + 头顶的紫色箭头（循环，大图），4 帧

被慎保护的队友：罩住全身的圆护罩，**只画边**（紫白色的光，1–2 格粗，比被动的护盾更亮、边上的光点更多），脚下一圈紫色的光环，头顶上浮着一个朝下指的紫色小箭头（约 6 × 6 格，像 P_arrow_ally 的形状，紫白色），箭头每帧上下浮动 1 格。**中间空着**，不要盖住人。左右对称。约 44 格宽、60 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: A LOOPING GUARDIAN SHIELD round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: the rim of a round upright shield bubble 44 x 52 squares, 1-2 squares thick, bright white-violet light, glints sliding round it; a thin violet ring on the ground at the feet (an ellipse 30 x 9 squares); above the head (54 squares above the feet) a small violet-white chevron arrow 6 x 6 squares pointing DOWN, bobbing up and down 1 square. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 768x1024 (image 3072x1024) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `shen_fx_r_land.png`：R 传送落地：从天而降的紫色光柱（大图），6 帧

引导结束、慎传送到队友身边的一下：一道细细的紫白光从上往下落到地面，变成一道约 10 格宽的紫色光柱砸在地上，脚下一下白光，地上炸开一圈紫色的冲击光环（约 44 × 14 格的椭圆），光点往上飞，然后光柱变细消失、光环淡出（参考 R_Laser、R_teleport_color-spiral、Shen_ring_purp）。**竖着的画面**，上下不能颠倒。左右对称。约 48 格宽、64 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a violet spirit-light ramp (#FFFFFF, #F3EAFF, #D9C2FF, #B18AFF, #8456F2, #5A2EC2, #31167A).
Effect: A TELEPORT LANDING, UPRIGHT (never upside down), 6 frames: 1 a thin vertical line of white-violet light dropping from the top of the cell to the ground; 2 a column of violet light 10 squares wide striking the ground, a white flash 12 squares across at the feet; 3 a violet shock ring bursting out on the ground (an ellipse 44 x 14 squares), motes flying up; 4 the column thinning, the ring at full size; 5 the column gone, the ring fading, motes rising; 6 a few faint motes. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 832x1152 (image 4992x1152) (16 px a square here); the feet (the ground point) 8 squares (128 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `shen_fx_a_hit` | view_effects `league_shen_a_hit`（跟随，画在人物上面） | 14 × 12 |
| `shen_fx_a_emp` | view_effects `league_shen_a_emp`（跟随，画在人物上面；Q 之后的 3 次普攻） | 20 × 18 |
| `shen_fx_q_blade` | view_projectiles `league_shen_q_blade`（循环，朝飞行方向转） | 30 × 12 |
| `shen_fx_q_hit` | view_effects `league_shen_q_hit`（跟随，画在人物上面） | 14 × 14 |
| `shen_fx_q_slow` | view_buffs `league_shen_q_slow`（循环，跟随，画在人物下面；1.5 秒） | 16 × 5 |
| `shen_fx_q_1` | view_buffs `league_shen_q_1`（循环，跟随，画在人物上面；强化普攻还没用完时） | 34 × 10 |
| `shen_fx_p_on` | view_buffs `league_shen_p_on`（循环，跟随，画在人物上面；2 秒） | 44 × 52 |
| `shen_fx_w_zone` | view_effects `league_shen_w_zone`（BIG；不跟随，画在人物下面；1.75 秒） | 46 × 30 |
| `shen_fx_w_safe` | view_buffs `league_shen_w_safe`（循环，跟随，画在人物上面；站在结界里时） | 24 × 30 |
| `shen_fx_e_dash` | view_projectiles `league_shen_e_dash`（循环，和他一起飞，朝飞行方向转） | 30 × 10 |
| `shen_fx_e_hit` | view_effects `league_shen_e_hit`（跟随，画在人物上面） | 22 × 22 |
| `shen_fx_r_cast` | view_effects `league_shen_r_cast`（BIG；跟随，画在人物上面） | 44 × 60 |
| `shen_fx_r_ch` | view_buffs `league_shen_r_ch`（BIG；循环，跟随，画在人物上面；引导的 2.5 秒） | 40 × 60 |
| `shen_fx_r_shield` | view_buffs `league_shen_r_shield`（BIG；循环，跟随，画在**队友**身上；5 秒） | 44 × 60 |
| `shen_fx_r_land` | view_effects `league_shen_r_land`（BIG；跟随，画在人物上面；传送到队友身边时） | 48 × 64 |

- `league_shen_fx`（跟随的小图、飞行物、buff）和 `league_shen_big`（`w_zone`、`r_cast`、`r_ch`、`r_shield`、`r_land`）两张 sheet，和技能数据里写的一致（build_shen.py 的 views）。
- `w_zone` 只放一次：7 帧加起来 105 tick（w_t；第 3–6 帧撑住）。`r_cast` 6 帧约 0.5 秒，`r_ch` 循环到引导结束（r_ch 150 tick），`r_shield` 循环 5 秒（r_sh_t 300）。`w_safe` 每 3 tick 重加一次（4 tick 的 buff），4 帧要几乎一样。
- `r_cast` 是 R 救人时（探针命中之后，晚于动作开始）放的跟随特效：画面左右对称，所以红色方不会反；`e_dash` 是 E 的 e_dash 线形投射物的画面（和他同速同程），影子画在格子左半边。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半；红蓝两方都看一遍（左右对称）。
