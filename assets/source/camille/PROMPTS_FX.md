# 青钢影 卡蜜尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型已定（`design/camille_design.png`，8 倍，46 格）。
> - 大小对照 `design/camille_size.png`：定稿造型放大 4 倍，站在红色脚底线上，上面是 10 格一段的刻度，右边是本包的剑姬。卡蜜尔 21×46 格（头顶到刀尖 46 格）。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡蜜尔自己的特效贴图（多数是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（踢击和 Q、W 横扫、E 钩索和落地、被动护盾、R 力场），只在本地用，不要提交。颜色按下面写的色阶。
> - 特效照下面第 1–16 条和「所有特效图的规则」画，每张一个 PNG，文件名 `camille_fx_<名字>.png`，排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**不要用代码拼色块**，要画出来的光效。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。最好打成一个 zip 放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「适应性防御」 | 刀刃腿踢；每 10 秒踢中英雄时给自己一个护盾（2 秒） | `camille_fx_hit` · `camille_fx_p_shield` |
| 普攻里的 Q「精准礼仪」 | 第一踢加伤加速；蓄力 1.5 秒后的第二踢伤害翻倍、一半转真伤 | `camille_fx_q_hit` · `camille_fx_q2_hit` |
| 技能 1 = W「战术横扫」 | 蓄力后扇形横扫，外沿的敌人减速、额外受伤，她回血 | `camille_fx_w_arc` · `camille_fx_w_hit` · `camille_fx_w_edge` |
| 技能 2 = E「钩索」 | 钩索射向目标把她拉过去，落地范围伤害，被钩中的英雄眩晕，她加攻速 | `camille_fx_e_hook` · `camille_fx_e_land` · `camille_fx_e_hit` · `camille_fx_e_stun` |
| 大招 = R「海克斯最后通牒」 | 跳到敌方英雄身上，震开旁人，六边形力场罩住她 3 秒：目标逃不出去（撞墙被拽回），她每次踢中英雄多一份真实伤害 | `camille_fx_r_land` · `camille_fx_r_zone` · `camille_fx_r_mark` · `camille_fx_r_wall` · `camille_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电弧、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。只有钩索的金色钩爪可以有 1 格深色描边。
- 颜色（按每条写的用）：
  - 海克斯青（她的能量：踢击的光、W、E、R 的光墙、护盾）：`#FFFFFF`、`#CFFBFF`、`#6FF2FF`、`#00C8F0`、`#0089C7`、`#00457A`；
  - 深蓝（电弧、阴影）：`#B8D8FF`、`#5A9CFF`、`#2F5FD9`、`#1C2F80`；
  - 金（钩爪）：`#FFF4C2`、`#FFE487`、`#E2B644`、`#9A752C`；
  - 紫（力场墙对敌人的颜色、被锁目标的标记、撞墙）：`#F2D9FF`、`#C98CF0`、`#9447D1`、`#5E2491`；
  - 刀光银（刀刃踢的划光）：`#FFFFFF`、`#E6E8F0`、`#B8C4D8`、`#7F8CA8`、`#4A5470`；尘土：`#C8BCA8`、`#9A8C78`、`#6E6252`。
- **朝右画、上下对称**的有两张：W 的扇形刀光 `w_arc`（扇尖在格子左边中间）、E 的钩索 `e_hook`（钩头在格子中间，绳往左长）：游戏会把它们转到施法方向。
- 命中、爆点居中画，不旋转；地面上的圆和六边形是从斜上方看的（宽是高的 2 倍）；套在人物身上的护盾、落地和力场：中间留出人的位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `camille_fx_hit.png`：普攻命中（刀刃踢），5 帧

刀刃腿踢中目标：一道银蓝色的短斜划光，几点青色的电光火花往外飞（参考 BA_tar_impact、BA_tar_spark_tech、Z_Shin_Swipe）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from a steel ramp (#FFFFFF, #E6E8F0, #B8C4D8, #7F8CA8, #4A5470) with her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A).
Effect: a BLADE KICK HIT, 5 frames: 1 a small white flash at the center; 2 a short bright diagonal slash of light (a narrow crescent, white core, pale steel-blue edge) across the center from upper left to lower right; 3 the slash at full length with 3-4 small cyan sparks flying outward; 4 the slash thins, the sparks fly further and dim; 5 a few cyan specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `camille_fx_q_hit.png`：Q 精准礼仪第一踢命中，6 帧

第一踢：一颗青色的四芒星光炸开（白芯），外面一圈细细的青色光环扩开，几道青色的光针往外射（参考 Q_Hit_Spark、Q_tar_impact）。比普攻命中大一点。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A).
Effect: a PRECISE STRIKE HIT, 6 frames: 1 a bright white dot at the center; 2 a sharp four-pointed star of light (white core, cyan points, the points about 80% of the cell) flashes; 3 the star at full size, a thin cyan ring expands around it and 4-6 short cyan needles of light shoot outward; 4 the star shrinks, the ring widens and thins; 5 the needles fade to deep blue; 6 a few cyan specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `camille_fx_q2_hit.png`：Q 精准礼仪第二踢（下劈，真实伤害）命中，7 帧

蓄满的第二踢：更大更亮的爆点——白色的四芒星加一个十字闪光，两圈青色光环先后扩开，中心一团白光（真实伤害），四周飞出青色和白色的碎光，一看就比第一踢重（参考 Q_tar_impact、R_tarrainbowflash、Q_WujuStyle01）。约 28 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A) with pure white.
Effect: a CHARGED TRUE-DAMAGE STRIKE, 7 frames: 1 a bright white flash at the center; 2 a large white four-pointed star with a second, smaller diagonal star behind it (an eight-pointed burst), cyan edges, filling the cell; 3 the burst at full size, a white core blob, a cyan ring bursting outward and 8 cyan and white shards flying out; 4 a second, wider ring, the star shrinking; 5 the rings thin and the shards scatter; 6 fading to deep blue specks; 7 a few faint specks.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `camille_fx_w_arc.png`：W 战术横扫的扇形刀光（朝右画，游戏会转到施法方向），6 帧

横扫的刀光：从左边中间（卡蜜尔的位置）往右展开的一大片扇形弧光，张角约 90 度，外沿那一圈（扇形半径的外面四分之一）最亮（青白色的一条亮带，就是“外沿”），里面是淡青色的扫痕和几条海克斯电路纹，最后散成碎光（参考 W_Swipe、W_slash、W_sweet_spot、W_Swipe_Circuits、W_Hex_Indicator）。**上下对称**（游戏会把它转向，往左放时会翻过来）。约 46 格长、66 格高，扇形的尖在格子左边中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A) with the steel ramp (#FFFFFF, #E6E8F0, #B8C4D8, #7F8CA8, #4A5470).
Effect: a WIDE SWEEPING CRESCENT pointing RIGHT, 6 frames, SYMMETRIC above and below the middle line: the point of a fan (about 90 degrees wide) sits at the LEFT edge, middle height, and the fan opens to the right; 1 a thin bright line flashes along the fan's outer edge; 2 the whole fan fills with faint cyan streaks (sweep lines curving along the arc) and its outer edge (the outer quarter of the radius) becomes a thick bright band (white core, cyan sides); 3 the outer band at its brightest, short angular circuit lines glowing in the inner part; 4 the streaks thin, the band stays bright; 5 the band breaks into short bright dashes; 6 a few cyan specks along the arc.
Layout: one horizontal row of 6 equal cells, each 5 wide to 7 tall, image size 2400x560 (each cell 400x560); the fan's point at the left edge, middle height, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `camille_fx_w_hit.png`：W 横扫命中（内侧），4 帧

被扫中：一道短的青色划光加一小团电火花。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A).
Effect: a SWEEP HIT, 4 frames: 1 a small white-cyan flash; 2 a short horizontal slash of cyan light through the center with a crackle of tiny electric sparks; 3 the slash fades, the sparks jump outward; 4 two cyan specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `camille_fx_w_edge.png`：W 外沿命中（减速 + 额外伤害），6 帧

被外沿扫中：更亮的青白色划光，周围噼啪地缠着几道蓝色的电弧（表示被减速），往下散落几点电光（参考 W_Electricity、W_edge_Overlay）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A) with the deep blue (#B8D8FF, #5A9CFF, #2F5FD9, #1C2F80).
Effect: an EDGE SWEEP HIT with an electric slow, 6 frames: 1 a bright white flash; 2 a long bright horizontal slash (white core, cyan edges) through the center; 3 jagged blue electric arcs crackle around the body area (zigzag lines, branching); 4 the slash fades, the arcs jump and flicker; 5 a few arcs and sparks falling downward; 6 faint blue specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `camille_fx_e_hook.png`：E 钩索：飞出去的钩头和拖在后面的绳（朝右画），8 帧

钩索：一个金色和青色的小抓钩（钩头约 8 格，金色钩爪、中间一点亮青光）朝右飞，后面拖一条细细的青色光绳（中间暗芯、两边亮青），绳从钩头往左一直连回卡蜜尔。**钩头每帧都在格子正中间，绳一帧比一帧长**：第 1 帧 8 格，每帧多 8 格，第 8 帧 64 格（钩索射程 60000）。上下对称（参考 E_Beam_Reticle_RGB、E_mis_glow、E_cables_02、E_Device）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her gold (#FFF4C2, #FFE487, #E2B644, #9A752C) and her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A).
Effect: a GRAPPLING HOOK flying to the RIGHT with its cable, 8 frames, SYMMETRIC above and below the middle line: the hook head (about 8 squares long: a small three-pronged gold claw pointing right, a bright cyan glow at its base) is at the CENTER of every cell; behind it, to the LEFT, a thin glowing cable (2 squares thick: a dark blue core line with bright cyan edges) runs straight back toward the left edge; the cable grows each frame: 8 squares long in frame 1, 16 in frame 2, 24, 32, 40, 48, 56, and 64 squares in frame 8 (it never reaches past the left edge); a faint cyan shimmer runs along the cable.
Layout: one horizontal row of 8 equal cells, each 9 wide to 1 tall, image size 9216x128 (each cell 1152x128); the hook head at the center of every cell, the cable extending left from it. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `camille_fx_e_hit.png`：E 落地命中周围的敌人，5 帧

落地砸中：一团蓝白色的冲击光，向四周溅出几点青色火花。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A) with the deep blue (#B8D8FF, #5A9CFF, #2F5FD9, #1C2F80).
Effect: a HEAVY IMPACT, 5 frames: 1 a white flash at the center; 2 a round burst of blue-white light; 3 the burst breaks into 6 cyan sparks flying outward; 4 the sparks dim to deep blue; 5 a few specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `camille_fx_e_stun.png`：E 眩晕（被钩中的英雄头顶，约 0.75 秒），8 帧

被晕：头顶一圈转动的青色小六边形和星点（海克斯风格的眩晕星），一闪一闪。8 帧约 0.75 秒，第 1 帧出现、第 8 帧散去。约 16 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A) with pure white.
Effect: a STUN above a head, 8 frames: 1 small cyan sparks appear; 2-7 a flat ring (an ellipse, wider than tall) of 4 small glowing hexagons and white star points circling around, moving a little each frame; 8 the ring breaks into cyan specks.
Layout: one horizontal row of 8 equal cells, each 8 wide to 5 tall, image size 2048x160 (each cell 256x160); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `camille_fx_p_shield.png`：被动 适应性防御：护盾（盖住全身，护盾在时循环），6 帧

护盾：一层薄薄的青色六边形格子护罩，椭圆形，从头盖到刀尖，边上亮、里面几乎透明，人要看得清；格子一闪一闪地流动（参考 P_shield_hex、P_shield_hex_fresnel、Z_Hex_Shimmer）。约 30 格宽、50 格高；第 6 帧接第 1 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A).
Effect: a HEXAGONAL ENERGY SHIELD around a standing figure (do NOT draw the figure), 6 frames, a seamless loop: a tall oval (about 3 to 5) outlined by a bright cyan rim 1-2 squares thick, inside it a honeycomb of thin hexagon outlines in pale cyan, most of the inside left empty so the figure shows through; a band of brighter hexagons travels up the shield, a little higher each frame, and a few hexagon cells flash white.
Layout: one horizontal row of 6 equal cells, each 3 wide to 5 tall, image size 2304x640 (each cell 384x640); the oval centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `camille_fx_r_mark.png`：R 被锁定的目标脚下的标记（地面，循环），4 帧

被锁定的敌人脚下：一个小的海克斯六边形地面环（从斜上方看，宽是高的 2 倍），紫色的边、角上青色的亮点，一明一暗地跳动（参考 R_Hex_Indicator）。约 28 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from the violet (#F2D9FF, #C98CF0, #9447D1, #5E2491) with her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A).
Effect: a HEXAGON MARK on the ground (seen from above at an angle: twice as wide as tall), 4 frames, a seamless loop: a hexagon outline 1-2 squares thick in violet, a small bright cyan node at each corner; the outline brightens in frames 2-3 and dims in 4 and 1.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `camille_fx_r_wall.png`：R 目标撞到力场墙被拽回，5 帧

目标想逃、撞到力场墙：一片紫色和青色的电光在身上一闪（像撞到电网），带几道电弧（参考 R_edge_single_enemy、R_tarVi_Impact_01）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from the violet (#F2D9FF, #C98CF0, #9447D1, #5E2491) with her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A).
Effect: a FORCE FIELD ZAP, 5 frames: 1 a vertical flash of violet light through the center (a hit against an invisible wall); 2 a short violet energy line with cyan end nodes across the center and jagged violet arcs around it; 3 the arcs jump outward; 4 the line fades, a few arcs remain; 5 violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `camille_fx_r_hit.png`：R 期间普攻对英雄的额外真实伤害，4 帧

大招期间每次踢中英雄多出的伤害：一颗小的白紫色六边形火花（参考 R_Hit_Burst、R_tarFireHit）。约 14 格，经常出现，不要太大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from the violet (#F2D9FF, #C98CF0, #9447D1, #5E2491) with pure white.
Effect: a SMALL HEX SPARK, 4 frames: 1 a white flash; 2 a small hexagon of white-violet light bursting; 3 it breaks into 6 violet sparks; 4 two specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `camille_fx_e_land.png`：E 落地冲击（地面，不跟随，大图），7 帧

钩索落地：地上一圈青色的冲击波往外扩（从斜上方看的椭圆，宽是高的 2 倍），中间一下白光，扬起一圈尘土（参考 E_Ring、E_wind_hit_flash、BA_Hit_Impact）。中间不要画人。约 56 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A) with dust (#C8BCA8, #9A8C78, #6E6252).
Effect: a LANDING SHOCKWAVE on the ground (seen from above at an angle), 7 frames: 1 a bright white flash at the middle of the ground; 2 a thin ring of cyan light bursts out from it (an ellipse twice as wide as tall) and a ring of dust puffs; 3 the ring at half the cell, thick and bright; 4 the ring reaching the edges of the cell, thinning; 5 the ring breaks into bright dashes, the dust drifting; 6 faint dashes and dust; 7 a few specks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 3584x256 (each cell 512x256); the ground ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `camille_fx_r_land.png`：R 海克斯最后通牒：落地爆发、力场升起（地面，不跟随，大图），8 帧

大招落地：中间一下白青色的强光，一圈冲击波往外推（把旁边的敌人震开），然后地上亮起一个大的六边形（从斜上方看，宽是高的 2 倍），六条边上升起青色的光墙（每段墙从地面往上约 14 格，下亮上淡，墙的接缝是亮点），最后一帧就是力场的样子，接下一张 `r_zone`（参考 R_Hex_Indicator、R_edge_single、R_mesh_glow、R_TechBit_03）。中间不要画人。约 96 格宽、56 格高（六边形约 86 × 43）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A) with the deep blue (#B8D8FF, #5A9CFF, #2F5FD9, #1C2F80) and pure white.
Effect: a HEXTECH ARENA FORMING on the ground (seen from above at an angle, do NOT draw a figure), 8 frames: 1 a bright white-cyan flash at the middle; 2 a shock ring bursts outward on the ground (an ellipse twice as wide as tall); 3 the ring reaches the edges and a large HEXAGON outline lights up on the ground (about 86 wide by 43 tall, its corners marked by bright nodes); 4-6 from the hexagon's six edges glowing walls of cyan light rise: each wall a vertical band about 14 squares tall standing on its edge, bright at the bottom and fading toward the top, with a few angular tech lines in it - the walls behind (top of the hexagon) seen over the ground, the walls in front (bottom) drawn lower; 7 the walls at full height, the corner nodes flashing; 8 the arena standing steady (this frame matches the loop r_zone).
Layout: one horizontal row of 8 equal cells, each 12 wide to 7 tall, image size 6144x448 (each cell 768x448); the hexagon centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `camille_fx_r_zone.png`：R 力场（跟着卡蜜尔，大招期间循环），6 帧

力场循环：和 `r_land` 最后一帧同一个六边形和六面光墙，墙上的光一闪一闪地流动，角上的亮点轮流亮起；第 6 帧接第 1 帧（导入时每 0.5 秒播一遍，3 秒）。中间不要画人。约 96 格宽、56 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks or energy, colours only from her hextech cyan (#FFFFFF, #CFFBFF, #6FF2FF, #00C8F0, #0089C7, #00457A) with the deep blue (#B8D8FF, #5A9CFF, #2F5FD9, #1C2F80).
Effect: a HEXTECH ARENA standing on the ground (seen from above at an angle, do NOT draw a figure), 6 frames, a seamless loop: the same hexagon as the last frame of the arena forming (about 86 wide by 43 tall on the ground, corner nodes), with its six glowing walls of cyan light (vertical bands about 14 squares tall standing on the edges, bright at the bottom, fading toward the top, angular tech lines in them); a brighter shimmer runs along the walls a little further each frame and the corner nodes light up in turn.
Layout: one horizontal row of 6 equal cells, each 12 wide to 7 tall, image size 4608x448 (each cell 768x448); the hexagon centered in every cell, in the same place as in the arena forming. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `camille_fx_hit` | view_effects `league_camille_hit`（跟随） | 14 |
| `camille_fx_q_hit` | view_effects `league_camille_q_hit`（跟随） | 20 |
| `camille_fx_q2_hit` | view_effects `league_camille_q2_hit`（跟随） | 28 |
| `camille_fx_w_arc` | view_projectiles `league_camille_w_arc`（LineRangeProjectile，转向目标；扇形半径 46000，张角约 ±45°） | 46 × 66 |
| `camille_fx_w_hit` | view_effects `league_camille_w_hit`（跟随） | 14 |
| `camille_fx_w_edge` | view_effects `league_camille_w_edge`（跟随） | 20 |
| `camille_fx_e_hook` | view_projectiles `league_camille_e_hook`（TargetProjectile，不重复播放） | 144 × 16 |
| `camille_fx_e_hit` | view_effects `league_camille_e_hit`（跟随） | 16 |
| `camille_fx_e_stun` | view_effects `league_camille_e_stun`（跟随，画在人物上面） | 16 × 10 |
| `camille_fx_p_shield` | view_buffs `league_camille_p_on`（跟随，护盾破了就消失） | 30 × 50 |
| `camille_fx_r_mark` | view_buffs `league_camille_r_mark`（跟随，地面） | 28 × 14 |
| `camille_fx_r_wall` | view_effects `league_camille_r_wall`（跟随） | 20 |
| `camille_fx_r_hit` | view_effects `league_camille_r_hit`（跟随） | 14 |
| `camille_fx_e_land` | view_effects `league_camille_e_land`（施法者身上，地面，不跟随，大图 league_camille_big） | 56 × 28（半径 25000） |
| `camille_fx_r_land` | view_effects `league_camille_r_land`（施法者身上，地面，不跟随，大图） | 96 × 56 |
| `camille_fx_r_zone` | view_effects `league_camille_r_zone`（施法者身上，地面，跟随，大图；每 0.5 秒播一次） | 96 × 56 |

- `r_zone` 每片 30 tick（0.5 秒），大招 3 秒内播 6 片；`p_shield` 是护盾在时的 buff 循环；`r_mark` 是被锁目标脚下的 buff 循环。
- `e_hook` 的绳按帧变长（每帧 8 格），钩头在投射物的位置；帧时长按钩索速度定（6000/tick = 6 格/tick，约 1.33 tick 即 22 ms 一帧），绳尾就一直停在她手上。
- `w_arc` 导入时把扇尖放在投射物线段的起点（她的位置），按 DirDot 半径 46000 缩放。
- 清掉 Codex 给光描的最深色边（`unrim` 做法），钩爪的描边保留；核对交回的张数和这份清单。
