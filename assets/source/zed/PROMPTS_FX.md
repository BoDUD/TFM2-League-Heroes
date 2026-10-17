# 影流之主 劫：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型和动作已定（`design/zed_design.png`，27×40 格，8 倍）。
> - 大小对照 `design/zed_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/zed_shots.png`：普攻刺中、W 甩出影子、Q 扔出、E 旋斩、R 突刺那几帧的动作（4 倍），青色十字是脚下。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里劫自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。颜色：**影子是黑紫色的烟（外沿亮紫）；手里剑和刃光是银白；死亡印记和被动是暗红 / 红；火星是白金**。
> - **特效要看得见**：劫的特效是暗色的影子，但以前魔腾的特效画成最深的几档颜色、叠在人身上看不见。每个暗色形状都要有一圈亮紫色的外沿，亮的地方有白色或最亮一档的芯，暗底上一眼能看见。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。**影子人形要从正面画**（左右对称），因为它站在地上不会跟着朝向翻转。飞行的手里剑会转到飞行方向，所以朝右画、上下对称。
> - 特效照下面第 1–19 条和「所有特效图的规则」画，每张一个 PNG，文件名 `zed_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`zed_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「影忍法！灭魂劫」 | 腕刃前刺；对残血英雄的普攻额外造成其最大生命的伤害 | `zed_fx_a_hit` · `zed_fx_cw_hit` · `zed_fx_cw_ready` |
| 自动「影奥义！鬼斩」 | 身边有敌人时普攻变成原地旋斩，减速英雄（影子同时模仿） | `zed_fx_e_spin` · `zed_fx_sh_spin` · `zed_fx_e_hit` · `zed_fx_e_slow` |
| 技能 1 = W「影奥义！分身」 | 把影子甩到敌方英雄脚下，接着鬼斩和手里剑（影子同时模仿）；之后可以和影子换位追击 | `zed_fx_w_dash` · `zed_fx_sh_in` · `zed_fx_sh_stand` · `zed_fx_sh_throw` · `zed_fx_sh_out` · `zed_fx_w_swap` |
| 技能 2 = Q「影奥义！诸刃」 | 扔出贯穿的大手里剑；影子扔的那一枚从影子飞回劫、穿过目标 | `zed_fx_q_star` · `zed_fx_sh_star` · `zed_fx_q_hit` |
| 大招 = R「禁奥义！瞬狱影杀阵」 | 无法选中，冲过敌方英雄打上死亡印记，原地留下影子；3 秒后印记爆发；被包围时换回影子 | `zed_fx_r_hit` · `zed_fx_r_mark` · `zed_fx_r_pop` · `zed_fx_sh_stand` · `zed_fx_w_swap` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、刀光、火星、烟雾没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反；影子人形可以有自己最深那档的内轮廓，外面一圈用亮紫色）。
- **要看得见**：每个形状都有亮紫、红或白的亮部，暗部最多用到每个色阶的倒数第二档，最深的一档只给影子的内部。
- 颜色（按每条写的用）：
  - 银白（手里剑、刃光）：`#FFFFFF`、`#EEF2FA`、`#C6D0E0`、`#8FA0B7`、`#5E6A84`、`#3A4258`；
  - 影子（黑紫烟，亮紫外沿）：`#F2ECFF`、`#C8B4F4`、`#9A7AE0`、`#6A48B8`、`#44287E`、`#261447`、`#120A22`；
  - 红（死亡印记、被动、眼睛）：`#FFFFFF`、`#FFD8C8`、`#FF8A6A`、`#F23A24`、`#C01410`、`#7A0808`；
  - 火星：`#FFFFFF`、`#FFF2D8`、`#FFD08A`、`#F59A3A`；
- **飞行的画面朝右画，而且上下对称**（`q_star`、`sh_star`）：游戏会把它转到飞行方向，往左飞时整张会上下翻过来。
- **挂在人身上和地上的画面左右对称**（除了两张手里剑全部），按每条写的站位画；命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- **影子人形**（`sh_in` 最后一帧、`sh_stand`、`sh_out` 第一帧）是同一个从正面看的劫的影子：第一张附图 `design/zed_design.png` 的劫（头盔两根尖刺、兜帽、两边弯肩甲、背后刃饰、长前摆、每只手腕两根长刃），但全身是黑紫色的影子，外轮廓一圈亮紫色，两道眼缝发红光；约 30 格高、26 格宽，三张里一模一样（只有烟和轮廓光在变）。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人；光环只画外面一圈，不要盖住人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：鬼斩半径约 24000）。画影子的三张（`sh_in`、`sh_stand`、`sh_out`）请把 `design/zed_design.png` 作为第一张附图一起附上。

### 1. `zed_fx_a_hit.png`：普攻命中：腕刃刺击（目标身上），4 帧

腕刃刺中：两道平行的银白短刃光交叉成一个小 X，交点一下白光，几颗火星和一点暗红碎光。左右对称，居中画。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a silver ramp (#FFFFFF, #EEF2FA, #C6D0E0, #8FA0B7, #5E6A84, #3A4258) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808) and a spark ramp (#FFFFFF, #FFF2D8, #FFD08A, #F59A3A).
Effect: a BLADE STAB HIT, 4 frames: 1 a white flash 4 squares across; 2 two pairs of thin bright silver-white blade streaks 10 squares long crossing in an X through the middle, sparks flying out, a few red glints; 3 the streaks thinning, sparks farther out; 4 fading lines. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `zed_fx_cw_hit.png`：被动「影忍法！灭魂劫」：残血敌人身上的暗红爆裂（目标身上），5 帧

对残血的敌人补上一刀：目标身上一个暗红色的手里剑形印记一下子炸开，暗红 + 黑紫的碎刃往外飞，中间一下白红色的光（参考 zed_atk_crit 的爆光）。左右对称，居中画。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: a CRIMSON BURST on a target, 5 frames: 1 a small bright red-white flash at the middle; 2 a four-pointed crimson shuriken-shaped sigil 12 squares across flaring out, a white core; 3 the sigil breaking into shards of dark violet and red flying outward, a red glow ring; 4 the shards farther out, fading to dark violet; 5 a few faint red sparks. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 288x288 (image 1440x288) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `zed_fx_cw_ready.png`：被动就绪（主包）：头顶暗红的小手里剑印（循环），4 帧

被动准备好的时候：头顶上方一个小小的暗红四角手里剑印在慢慢转、一明一暗。只画印记，不要画人，在格子上半部。左右对称（转的时候四个角对称）。约 10 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: a small LOOPING SIGIL above a head (do NOT draw the figure), 4 frames, a seamless loop: a four-pointed crimson shuriken mark 8 squares across with a pale red core and a dark violet rim, turning an eighth of a turn each frame and pulsing brighter and dimmer. Left-right symmetric in every frame.
Layout: one horizontal row of 4 equal cells, each 160x128 (image 640x128) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `zed_fx_q_star.png`：Q 影奥义！诸刃：飞行的手里剑（随飞行方向转），4 帧循环

劫扔出的大手里剑：一个四角的银色大手里剑在飞速旋转（四个弯刃，中间一个暗红的芯），后面一小段银白和暗红的拖尾往左。朝右画（游戏会转到飞行方向），上下对称。约 12 格见方（不算拖尾）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a silver ramp (#FFFFFF, #EEF2FA, #C6D0E0, #8FA0B7, #5E6A84, #3A4258) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: a SPINNING SHURIKEN flying to the RIGHT, 4 frames, a seamless loop: a big four-bladed silver shuriken 11 squares across (four curved hooked blades round a small dark red core), bright white glints on the edges, turning a quarter of a blade each frame; a short motion trail of silver and red streaks behind it to the left. Symmetric above and below its flight line.
Layout: one horizontal row of 4 equal cells, each 320x192 (image 1280x192) (16 px a square here); the shuriken's centre at the middle of the right half of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `zed_fx_sh_star.png`：影子的手里剑（随飞行方向转），4 帧循环

影子扔出的手里剑：形状和上一张一样，但是暗紫色的影子做的（黑紫色刃、亮紫色的边、暗红的芯），拖尾是紫黑色的烟。朝右画，上下对称。约 12 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: the same SPINNING SHURIKEN as the previous image but made of SHADOW: near-black violet blades with a bright pale-violet rim, a small red core, a trail of violet smoke streaks behind it to the left; 4 frames, a seamless loop, flying to the RIGHT, symmetric above and below its flight line.
Layout: one horizontal row of 4 equal cells, each 320x192 (image 1280x192) (16 px a square here); the shuriken's centre at the middle of the right half of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `zed_fx_q_hit.png`：Q 命中（目标身上），4 帧

手里剑打中：一道银白的斜切光（左右对称地交叉成 X），迸出银色和暗红的碎光。左右对称，居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a silver ramp (#FFFFFF, #EEF2FA, #C6D0E0, #8FA0B7, #5E6A84, #3A4258) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808) and a spark ramp (#FFFFFF, #FFF2D8, #FFD08A, #F59A3A).
Effect: a SHURIKEN HIT, 4 frames: 1 a white flash 5 squares across; 2 a bright silver-white X of two slash streaks 12 squares long, silver and red shards bursting out; 3 the shards farther out, the streaks thinning; 4 fading. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 224x224 (image 896x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `zed_fx_e_spin.png`：E 影奥义！鬼斩：劫周围一圈旋斩（地上，脚下），5 帧

劫原地旋身一斩：脚下一圈暗紫色的斩击波往外扫（像一圈弯刀光连成环），外沿亮紫、里面黑紫，带几道银白的刃光。左右对称，从斜上方看的椭圆（宽是高的 2 倍多）。约 48 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a silver ramp (#FFFFFF, #EEF2FA, #C6D0E0, #8FA0B7, #5E6A84, #3A4258).
Effect: a SPINNING SHADOW SLASH RING on the ground round a standing figure (do NOT draw the figure), 5 frames: 1 a small dark violet ring at the middle with a bright rim; 2 a ring of curved slash crescents sweeping outward (an ellipse 30 x 14 squares), the outer edge bright pale violet, the inside near-black violet, 3-4 silver-white blade glints on it; 3 the ring at full size (46 x 20), sharpest; 4 the ring thinning and fading to dark violet smoke; 5 faint wisps. Left-right symmetric; seen from above at an angle; the middle of the cell left empty for the figure.
Layout: one horizontal row of 5 equal cells, each 768x352 (image 3840x352) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `zed_fx_sh_spin.png`：影子的旋斩（地上，影子脚下），5 帧

影子模仿劫的鬼斩：和上一张一样的斩击圈，但更暗、更像烟（黑紫色为主，红色的小火星代替银白刃光）。左右对称、斜上方看的椭圆。约 48 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: the same SHADOW SLASH RING as the previous image, darker and smokier: mostly near-black violet with a pale violet rim, small red glints instead of the silver blade glints; 5 frames, left-right symmetric, an ellipse seen from above, the middle left empty.
Layout: one horizontal row of 5 equal cells, each 768x352 (image 3840x352) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `zed_fx_e_hit.png`：E 命中（目标身上），3 帧

鬼斩扫中：一道横着的暗紫刃光一闪，几颗紫色碎光。左右对称，居中画。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22).
Effect: a SMALL SHADOW SLASH HIT, 3 frames: 1 a bright pale-violet horizontal slash streak 9 squares long through the middle; 2 the streak with violet shards flying up and down; 3 fading wisps. Left-right symmetric.
Layout: one horizontal row of 3 equal cells, each 160x160 (image 480x160) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `zed_fx_e_slow.png`：E 减速（敌人脚下，循环），4 帧

被鬼斩减速：敌人脚下一小圈紫黑色的影子在慢慢翻涌，几缕细烟缠着脚。只画脚下一圈，不要画人。左右对称，斜上方看的椭圆。约 16 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22).
Effect: a LOOPING SHADOW POOL at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse of dark violet shadow 14 x 5 squares with a pale violet rim, a few thin smoke wisps curling up from it, churning a little each frame. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 288x128 (image 1152x128) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `zed_fx_w_dash.png`：W 影奥义！分身：影子离开劫时的烟（劫身边），4 帧

劫甩出影子：他身上一团紫黑色的影子烟一下子爆开往外散。左右对称，居中画。约 16 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22).
Effect: a SHADOW PUFF bursting from a figure (do NOT draw the figure), 4 frames: 1 a burst of dark violet smoke with a bright pale-violet rim at the middle; 2 the smoke spreading to 14 x 12 squares, wisps flying out to both sides; 3 thinner, curling; 4 fading wisps. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x224 (image 1024x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `zed_fx_sh_in.png`：影子出现（影子落点，地上），5 帧

影子落地成形：地上先冒出一团黑紫色的影子漩涡，往上长成劫的影子人形（下一张那个从正面看的影子），最后一帧就是站好的影子。左右对称，脚底在格子靠下的同一条线上。约 30 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: the SHADOW APPEARING, 5 frames: 1 a swirl of dark violet smoke on the ground (an ellipse 16 x 5 squares) with a pale violet rim; 2 the smoke rising in a column 20 squares tall; 3 the column taking the outline of the figure below, red eye slits lighting up; 4 the figure nearly formed, smoke peeling off; 5 the finished figure: ZED'S SHADOW, seen exactly FROM THE FRONT (left-right symmetric), standing: the FIRST attached image's character (the closed helmet with the two curved spikes on top, the hooded head, the big curved pauldrons, the spiky blade ornament rising behind both shoulders, the long tabard, the two arms hanging with two long wrist blades on each), but made of SHADOW - a near-black violet silhouette with dark violet shading, a bright pale-violet rim light round the whole silhouette, the two eye slits glowing RED, a few wisps of violet smoke rising from the shoulders and swirling at the feet; about 30 squares tall and 26 wide. Left-right symmetric; the feet on the same ground line, 5 squares above the bottom of the cell.
Layout: one horizontal row of 5 equal cells, each 480x704 (image 2400x704) (16 px a square here); the figure centered across every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `zed_fx_sh_stand.png`：影子站着（影子落点，循环），4 帧

W 和 R 留下的影子：从正面看的劫的影子人形站着不动（参考第一张附图的劫，但完全是黑紫色的影子，外轮廓一圈亮紫色，两道眼缝发红光），肩上和脚下有紫色的细烟在飘。4 帧循环，只是烟在动、轮廓光一明一暗。左右对称。约 30 格高、26 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: a LOOPING STANDING SHADOW, 4 frames, a seamless loop: ZED'S SHADOW, seen exactly FROM THE FRONT (left-right symmetric), standing: the FIRST attached image's character (the closed helmet with the two curved spikes on top, the hooded head, the big curved pauldrons, the spiky blade ornament rising behind both shoulders, the long tabard, the two arms hanging with two long wrist blades on each), but made of SHADOW - a near-black violet silhouette with dark violet shading, a bright pale-violet rim light round the whole silhouette, the two eye slits glowing RED, a few wisps of violet smoke rising from the shoulders and swirling at the feet; about 30 squares tall and 26 wide; only the smoke wisps move and the rim light pulses from frame to frame, the silhouette itself stays the same. Left-right symmetric; the feet on the same ground line, 5 squares above the bottom of the cell.
Layout: one horizontal row of 4 equal cells, each 480x672 (image 1920x672) (16 px a square here); the figure centered across every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `zed_fx_sh_throw.png`：影子出手（影子身上），3 帧

影子扔出手里剑的一下：影子身上一团紫黑色的光爆开，中间一点红白光。左右对称，居中画。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: a SHADOW FLARE on a figure (do NOT draw the figure), 3 frames: 1 a bright pale-violet and red-white flash 6 squares across at the middle; 2 a burst of dark violet energy 16 squares across with a bright rim, red sparks; 3 fading smoke. Left-right symmetric.
Layout: one horizontal row of 3 equal cells, each 288x288 (image 864x288) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `zed_fx_sh_out.png`：影子消散（影子落点），4 帧

影子消失：站着的影子人形从上往下散成紫黑色的烟，烟往上飘走，最后什么都不剩。左右对称，脚底在同一条线上。约 30 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: the SHADOW DISSOLVING, 4 frames: 1 the standing figure (ZED'S SHADOW, seen exactly FROM THE FRONT (left-right symmetric), standing: the FIRST attached image's character (the closed helmet with the two curved spikes on top, the hooded head, the big curved pauldrons, the spiky blade ornament rising behind both shoulders, the long tabard, the two arms hanging with two long wrist blades on each), but made of SHADOW - a near-black violet silhouette with dark violet shading, a bright pale-violet rim light round the whole silhouette, the two eye slits glowing RED, a few wisps of violet smoke rising from the shoulders and swirling at the feet; about 30 squares tall and 26 wide) starting to break into smoke from the top; 2 half the figure gone into rising violet smoke, the red eyes fading; 3 only smoke drifting up and a dark pool on the ground; 4 a few faint wisps. Left-right symmetric; the feet on the same ground line, 5 squares above the bottom of the cell.
Layout: one horizontal row of 4 equal cells, each 480x672 (image 1920x672) (16 px a square here); the figure centered across every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `zed_fx_w_swap.png`：换位（劫和影子交换位置，劫身上），5 帧

劫和影子换位：原地一根紫黑色的影子烟柱一下子卷起又散开，中间一道亮紫色的竖光。左右对称，脚底在格子靠下。约 24 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22).
Effect: a SWAP COLUMN of shadow (do NOT draw a figure), 5 frames: 1 a bright pale-violet vertical streak 30 squares tall on the ground line; 2 a column of dark violet smoke swirling round it, 18 squares wide; 3 the column bursting outward; 4 thinning smoke rising; 5 a few wisps on the ground. Left-right symmetric; the base 5 squares above the bottom of the cell.
Layout: one horizontal row of 5 equal cells, each 384x640 (image 1920x640) (16 px a square here); the column centered across every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `zed_fx_r_hit.png`：R 禁奥义！瞬狱影杀阵：突刺打中（目标身上），5 帧

大招冲过目标的那一刀：一个很大的暗红 + 黑紫的 X 形斩痕，交点白红色的光，黑紫色的碎刃往外飞（参考 zed_basicatk_slashult）。左右对称，居中画。约 24 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: a DEATH MARK STRIKE, 5 frames: 1 a red-white flash 6 squares across; 2 a big X of two crimson slash streaks 22 squares long with near-black violet edges and a white-hot centre; 3 the X at full length, dark violet blade shards bursting out; 4 the streaks fading to dark red, shards farther out; 5 faint red lines. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 384x384 (image 1920x384) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `zed_fx_r_mark.png`：死亡印记（目标头顶，循环 3 秒），4 帧

被标上死亡印记：目标头顶一个红色发光的手里剑形印记在慢慢转、一下一下地脉动（参考 Zed_R_Marker 的红光），外面一圈黑紫色的烟边。只画印记，不要画人，在格子上半部。左右对称。约 14 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: a LOOPING DEATH MARK above a head (do NOT draw the figure), 4 frames, a seamless loop: a glowing crimson four-pointed shuriken sigil 12 squares across with a white-red core and a dark violet smoky rim, turning an eighth of a turn each frame and pulsing brighter and dimmer. Left-right symmetric in every frame.
Layout: one horizontal row of 4 equal cells, each 224x224 (image 896x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `zed_fx_r_pop.png`：死亡印记爆发（目标身上），6 帧

印记爆发：目标身上一个大的暗红爆炸，红色的手里剑印炸开成很多黑紫色的碎刃往四周飞，中间一下白红色的光，外面一圈暗红的冲击环。左右对称，居中画。约 36 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, the shapes readable on a dark battlefield (dark smoke gets a bright violet rim and a pale core where it is lit; red and silver parts are bright), colours only from a shadow ramp (#F2ECFF, #C8B4F4, #9A7AE0, #6A48B8, #44287E, #261447, #120A22) and a red ramp (#FFFFFF, #FFD8C8, #FF8A6A, #F23A24, #C01410, #7A0808).
Effect: a DEATH MARK DETONATION, 6 frames: 1 the crimson shuriken sigil 12 squares across flaring white-hot at the middle; 2 a red-white burst 16 squares across; 3 a crimson shock ring 30 squares across, dozens of dark violet blade shards flying outward; 4 the ring at full size (34), the shards at the edge; 5 the ring fading to dark red smoke; 6 faint smoke and sparks. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 576x576 (image 3456x576) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `zed_fx_a_hit` | view_effects `league_zed_a_hit`（跟随，画在人物上面） | 12 |
| `zed_fx_cw_hit` | view_effects `league_zed_cw_hit`（跟随，画在人物上面；对残血英雄的那一下普攻） | 18 |
| `zed_fx_cw_ready` | view_buffs `league_zed_cw_ready`（循环，跟随；技能刚打中英雄、下一次普攻会触发被动的时候） | 10 × 8 |
| `zed_fx_q_star` | view_projectiles `league_zed_q_star`（劫自己扔的手里剑，朝飞行方向转） | 12 × 12（拖尾向左） |
| `zed_fx_sh_star` | view_projectiles `league_zed_sh_star`（影子扔的手里剑：从影子飞回劫，穿过目标） | 12 × 12（拖尾向左） |
| `zed_fx_q_hit` | view_effects `league_zed_q_hit`（跟随，画在人物上面） | 14 |
| `zed_fx_e_spin` | view_effects `league_zed_e_spin`（不跟随，画在人物下面；半径约 24 格） | 48 × 22 |
| `zed_fx_sh_spin` | view_effects `league_zed_sh_spin`（不跟随，画在影子下面） | 48 × 22 |
| `zed_fx_e_hit` | view_effects `league_zed_e_hit`（跟随） | 10 |
| `zed_fx_e_slow` | view_buffs `league_zed_e_slow`（循环，跟随，画在人物下面） | 16 × 6 |
| `zed_fx_w_dash` | view_effects `league_zed_w_dash`（不跟随；扔出影子那一下，在劫身上） | 16 × 14 |
| `zed_fx_sh_in` | view_effects `league_zed_sh_in`（不跟随；影子落到目标脚下时） | 30 × 44 |
| `zed_fx_sh_stand` | view_effects `league_zed_sh_stand`（每 0.75 秒播一次，一共 5 秒）；R 留下的影子也用这张 | 30 × 42 |
| `zed_fx_sh_throw` | view_effects `league_zed_sh_throw`（不跟随；影子模仿手里剑那一下） | 18 |
| `zed_fx_sh_out` | view_effects `league_zed_sh_out`（不跟随；影子时间到了） | 30 × 42 |
| `zed_fx_w_swap` | view_effects `league_zed_w_swap`（不跟随；W 二段 / R 二段换位时） | 24 × 40 |
| `zed_fx_r_hit` | view_effects `league_zed_r_hit`（跟随，画在人物上面） | 24 |
| `zed_fx_r_mark` | view_buffs `league_zed_r_mark`（循环，跟随；印记期间一直在） | 14 × 14 |
| `zed_fx_r_pop` | view_effects `league_zed_r_pop`（跟随，画在人物上面；3 秒后爆发） | 36 |

- `r_shadow`（R 留下的影子）用 `sh_stand` 的画面另做一个 6 秒的标签（帧时长拉长），不另画。
- `e_spin`、`sh_spin`、`e_slow`、`sh_in`、`sh_stand`、`sh_out`、`w_swap` 是地上 / 脚下的画面：放在 ViewEffect 里（不随飞行转），不要挂在 RangeProjectile 的 view 上（红色方会倒过来，蕾欧娜的教训）。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法，但影子人形保留自己的内轮廓）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
