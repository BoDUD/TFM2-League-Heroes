# 幻翎 洛：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/rakan_design.png`，32×40 格，8 倍）。
> - 大小对照 `design/rakan_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/rakan_shots.png`：普攻、Q 出手、W 旋升、E 落地、R 开始那几帧的动作（4 倍），青色十字是脚下（导入时 Claude 把套在人身上的特效对到这里）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里洛自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，最后一行是英雄联盟给洛的特效上色用的色带，只在本地用，不要提交。颜色和英雄联盟一样：**金色、橙色到深红（羽毛、W、R），青、蓝、紫的虹彩（Q 的光尾、披风的羽尖、被动护盾），Q 的治疗是黄绿色，R 的魅惑是金色的爱心**。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色或淡色的芯，暗底上一眼能看见。
> - 特效照下面第 1–15 条和「所有特效图的规则」画，每张一个 PNG，文件名 `rakan_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`rakan_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「异色羽裳」 | 甩出一根金色羽毛；被动每隔一段时间给自己一个护盾，打英雄会缩短等待 | `rakan_fx_a_feather` · `rakan_fx_a_hit` · `rakan_fx_p_on` |
| 技能 1 = Q「微光飞翎」 | 射出一根发光的羽毛，打中第一个敌人；打中英雄后身上带着治疗，3 秒内碰到队友（或时间到）就给自己和身边队友回血 | `rakan_fx_q_feather` · `rakan_fx_q_hit` · `rakan_fx_q_heal` · `rakan_fx_q_burst` · `rakan_fx_q_healed` |
| 技能 2 = W「盛大登场」→ E「轻舞成双」 | 冲到敌方英雄身上落地、旋转升空把周围敌人击飞；随后飞到最近的队友身边给他护盾 | `rakan_fx_w_burst` · `rakan_fx_w_hit` · `rakan_fx_e_shield` · `rakan_fx_e_on` |
| 大招 = R「惊鸿过隙」 | 4 秒里移速大增，碰到的每个敌人受到伤害并被魅惑 | `rakan_fx_r_start` · `rakan_fx_r_on` · `rakan_fx_r_charmed` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、羽毛、火星、光晕没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 金色（羽毛、W、R 的主色）：`#FFFFFF`、`#FFF8D6`、`#FFE47A`、`#FFC63A`、`#FF9E21`、`#F07018`、`#D04A1A`、`#9A2A1C`；
  - 虹彩（Q 的光尾、被动护盾、R 的光尾）：`#FFFFFF`、`#DBF7FF`、`#94F7EF`、`#4FE0C8`、`#5AA0F0`、`#7A6CE8`、`#A64CD0`、`#6A2A9A`；
  - 治疗（Q 的治疗）：`#FFFFFF`、`#F6FFD6`、`#E2FF7A`、`#C6F04E`、`#9AD83A`、`#6AAE2C`、`#3E7A22`；
  - 爱心（R 的魅惑）：`#FFFFFF`、`#FFF3C6`、`#FFD554`、`#FFAC12`、`#F06A2A`、`#E0405A`、`#A82048`；
- **飞行的羽毛朝右画，而且上下大致对称**（`a_feather`、`q_feather`）：游戏会把它转到飞行方向，往左飞时整张会上下翻过来。
- **画在洛身上的特效按每条写的站位画**（`q_heal`、`q_burst`、`w_burst`、`p_on`、`r_start`、`r_on`）：游戏把它画在洛身上，他朝左时整张左右镜像；`r_on` 的光尾画在人身后（左边）。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在别人身上的画面（`q_healed`、`w_hit`、`e_shield`、`e_on`、`r_charmed`）左右对称或接近对称。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人；护盾、光环不要盖住人（`p_on` 只画护罩的边）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 治疗半径 40000，W 击飞半径 12000，R 碰撞半径 10000）。

### 1. `rakan_fx_a_feather.png`：普攻甩出的羽毛（飞行中，朝右，循环），3 帧

普攻是甩出去的一根金色羽毛：羽毛尖朝右（游戏会转到飞行方向），后面拖一小段金橙色的光，光尾末端一点青色（参考 BA_trail_01、BA_flare）。上下大致对称（往左飞时整张会上下翻过来）。约 12 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C) and an iridescent ramp (#FFFFFF, #DBF7FF, #94F7EF, #4FE0C8, #5AA0F0, #7A6CE8, #A64CD0, #6A2A9A).
Effect: a FLYING GOLDEN FEATHER pointing to the RIGHT, 3 frames, a seamless loop: a slim golden feather 7 squares long, its quill tip at the right, a white-gold shine along its shaft; a streak of gold-orange light trailing 5 squares to the LEFT behind it with a tiny cyan glint at the streak's end; the vanes flutter and the streak flickers from frame to frame; roughly symmetric above and below the middle line.
Layout: one horizontal row of 3 equal cells, each 256x128 (image 768x128); the feather on the middle line of every cell, its tip near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `rakan_fx_a_hit.png`：普攻打中（目标身上），4 帧

羽毛打中：白金色的星形闪光一下，一圈金光，几片金色的羽毛碎片飞散（参考 BA_hit_flash、BA_flare）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C) and an iridescent ramp (#FFFFFF, #DBF7FF, #94F7EF, #4FE0C8, #5AA0F0, #7A6CE8, #A64CD0, #6A2A9A).
Effect: a small FEATHER HIT, 4 frames: 1 a white-gold star flash 8 squares across; 2 the flash inside a ring of golden light, 3 tiny golden feather bits flying out, one cyan glint; 3 the bits farther out, the light dimming to orange; 4 two fading sparks.
Layout: one horizontal row of 4 equal cells, each 256x256 (image 1024x256); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `rakan_fx_q_feather.png`：Q 微光飞翎：飞出去的发光羽毛（飞行中，朝右，循环），4 帧

Q 射出一根发光的大羽毛，像孔雀翎：金橙色的羽片、白金色的羽轴，靠尖的地方一个青蓝色的“眼”，后面拖一道青、蓝、紫的虹彩光尾，光尾里几点星光（参考 Q_peacock_feather、Q_feather_tras_RGB、Q_trail_blur_01、Q_Shrine_spark）。羽毛尖朝右，上下大致对称。约 22 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C) and an iridescent ramp (#FFFFFF, #DBF7FF, #94F7EF, #4FE0C8, #5AA0F0, #7A6CE8, #A64CD0, #6A2A9A).
Effect: a GLEAMING FEATHER MISSILE flying to the RIGHT, 4 frames, a seamless loop: a large glowing feather 12 squares long pointing right, gold-orange vanes and a white-gold shaft, an 'eye' spot of teal and blue near its tip (like a peacock feather); behind it an iridescent trail of cyan, blue and violet light 10 squares long tapering to the LEFT, with 3-4 white sparkles; the trail's colour bands shimmer and shift every frame; roughly symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 448x192 (image 1792x192); the feather on the middle line of every cell, its tip near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `rakan_fx_q_hit.png`：Q 打中（目标身上），5 帧

Q 的羽毛打中敌人：一团金橙色的星芒炸开，白芯，光芒尖上带一点青紫色的虹彩，金色的羽毛碎片往外飞（参考 Q_hit_flare、Q_Shrine_spark）。约 18 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C) and an iridescent ramp (#FFFFFF, #DBF7FF, #94F7EF, #4FE0C8, #5AA0F0, #7A6CE8, #A64CD0, #6A2A9A).
Effect: a GLEAMING FEATHER BURST, 5 frames: 1 a white flash; 2 a bright gold-orange starburst 14 squares across with a white core and 6 short rays, iridescent cyan and violet glints at the ray tips; 3 the burst at full size, small golden feather shards thrown outward; 4 the rays fade to orange, the shards falling; 5 fading glints.
Layout: one horizontal row of 5 equal cells, each 320x320 (image 1600x320); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `rakan_fx_q_heal.png`：Q 待发的治疗（洛脚下，循环），4 帧

Q 打中英雄以后洛身上带着治疗，3 秒内碰到队友（或时间到）就放出来：脚下一圈细细的黄绿色光环（像英雄联盟的治疗指示圈，左右两头有叶子形的卷纹），几点金绿色的光从圈上往上飘（参考 Q_heal_indicator、Q_heal_trans_RGB、Q_Glow-soft）。中间是人，不要画人。4 帧无缝循环。约 32 格宽、24 格高（地上的圈 30 × 12）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a heal ramp (#FFFFFF, #F6FFD6, #E2FF7A, #C6F04E, #9AD83A, #6AAE2C, #3E7A22) and a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C).
Effect: a LOOPING HEAL-READY RING at a figure's feet (do NOT draw the figure; leave its place empty), 4 frames, a seamless loop: a thin ring of yellow-green light lying on the ground round the feet (an ellipse 30 squares wide and 12 tall, 1-2 squares thick) with small leaf-like curls at its left and right ends and a soft pale green glow along it; 3 golden-green motes rise from the ring beside the body, each a little higher every frame; the ring's brightness pulses.
Layout: one horizontal row of 4 equal cells, each 512x384 (image 2048x384); the ellipse's middle 6 squares (96 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `rakan_fx_q_burst.png`：Q 的治疗放出来（洛脚下，不跟随），6 帧

治疗放出来：脚下一圈黄绿色的光一下扩到治疗范围（地上的椭圆 80 × 40，就是治疗半径），圈里飘起金绿色的光点和几片小羽毛，然后淡掉（参考 Q_heal_indicator、Q_heal_trans_RGB、Q_cas）。中间是人，不要画人。约 84 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a heal ramp (#FFFFFF, #F6FFD6, #E2FF7A, #C6F04E, #9AD83A, #6AAE2C, #3E7A22) and a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C).
Effect: a HEALING WAVE spreading over the ground from a figure's feet (do NOT draw the figure; leave its place empty), 6 frames: 1 a bright pale green-gold flash at the feet; 2 a ring of yellow-green light expands to half size (an ellipse 40 x 20 squares, twice as wide as tall) with a white inner edge; 3 the ring at full size (80 x 40 squares), 2 squares thick, a faint green glow inside it, golden-green motes and 4 tiny golden feathers rising inside; 4 the ring fades from its inside, the motes higher; 5 a thin fading ring and motes; 6 a few motes.
Layout: one horizontal row of 6 equal cells, each 672x384 (image 4032x384) (8 px a square here); the ellipse's middle 22 squares (176 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `rakan_fx_q_healed.png`：治疗到人身上（目标身上），5 帧

治疗落到洛和身边队友身上：一层淡绿色的光，金绿色的光点和几个小十字星往上飘（参考 Q_heal_trans_RGB、Q_Glow-soft）。中间是人，不要画人。约 16 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a heal ramp (#FFFFFF, #F6FFD6, #E2FF7A, #C6F04E, #9AD83A, #6AAE2C, #3E7A22) and a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C).
Effect: a HEAL SPARKLE on a figure (do NOT draw the figure), 5 frames: 1 a soft pale green glow in the middle; 2 golden-green motes and 3 small plus-shaped sparkles rise from the bottom of the cell; 3 the motes at mid height, the glow at its brightest; 4 the motes near the top, fading; 5 two last motes.
Layout: one horizontal row of 5 equal cells, each 256x384 (image 1280x384); the figure's feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `rakan_fx_w_burst.png`：W 落地旋升击飞（洛脚下，不跟随），7 帧

W 冲到敌人中间落地、旋转着升起来：脚下一圈金橙色的螺旋裂纹炸开，一圈金色的光和小白羽毛从地上旋转着往上冲（像一个金色的火焰圆筒），火星和小碎石往外飞（参考 W_Ground_crack、W_crack_light、w_up_cylinder、W_swirl、W_feather、W_sparks、W_rock_debris）。中间是人，不要画人。约 32 格宽、40 格高（地上的圈 26 × 12，就是击飞范围）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C).
Effect: a SPIRALLING LAUNCH round a figure (do NOT draw the figure; leave its place empty), 7 frames: 1 a gold-white flash on the ground at the feet; 2 glowing orange spiral cracks spread over the ground round the feet (an ellipse 26 x 12 squares), golden light rising at its edge; 3 a swirling column of golden light and small white-gold feathers spirals up round the figure to 34 squares high, sparks and a few small dark rock chips thrown out; 4 the column at full height and brightness, the feathers turning; 5 the column thins and lifts off the ground, the cracks dim to orange; 6 feathers and sparks falling, faint cracks; 7 a few fading feathers.
Layout: one horizontal row of 7 equal cells, each 256x320 (image 1792x320) (8 px a square here); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `rakan_fx_w_hit.png`：W 击飞（目标身上），5 帧

被 W 击飞的敌人身上：一道金光从脚下往上冲，几片小白羽毛跟着旋上去，金色火星（参考 W_flash_tar、W_feather、W_sparks）。中间是人，不要画人。约 16 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C).
Effect: an UPWARD LAUNCH HIT on a figure (do NOT draw the figure), 5 frames: 1 a white-gold flash at the bottom middle; 2 a burst of golden light shoots up 20 squares from the bottom, 3 small white feathers swirling up with it; 3 the streak at full height, gold sparks; 4 the streak fading to orange, the feathers at the top; 5 fading sparks.
Layout: one horizontal row of 5 equal cells, each 256x416 (image 1280x416); the figure's feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `rakan_fx_e_shield.png`：E 护盾落到队友身上（目标身上），6 帧

洛飞到队友身边给他上盾的一下：队友胸前金光一闪，亮起一个金色火焰形的羽饰（英雄联盟 E 的护盾标志：上尖下圆的火焰、中间一个环），两道金色的弧光绕着队友合成一圈，然后化成金色光点（参考 E_shield_arrow、E_beam、E_dash_swirl）。中间是人，不要画人。约 26 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C).
Effect: a GOLDEN WARD appearing on a figure (do NOT draw the figure), 6 frames: 1 a gold-white flash at chest height (the middle of the cell); 2 a golden flame-shaped crest 12 squares tall (a teardrop flame with a ring in its lower middle, like a feather emblem) appears in the middle, white-gold core, orange edges; 3 the crest at full brightness, two curved arcs of golden light sweep round the figure; 4 the arcs close into a faint oval of golden light round the figure (22 x 28 squares); 5 the crest dissolves into golden motes; 6 a few motes.
Layout: one horizontal row of 6 equal cells, each 416x480 (image 2496x480); centered in every cell (the figure's chest at the middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `rakan_fx_e_on.png`：E 护盾持续（队友身上，循环），6 帧

E 的护盾在队友身上的 3 秒：两根小金羽毛绕着队友的胸口转，身边一圈细的金色光边（左右两边亮、上下断开），脚下一团淡金色的光，几点淡金色光点往上飘（参考 E_shield_arrow、E_shield_Mult、Q_Shrine_spark）。中间是人，不要画人，别盖住人。6 帧无缝循环。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C).
Effect: a LOOPING GOLDEN GUARD round a figure (do NOT draw the figure; leave its place empty), 6 frames, a seamless loop: two small golden feathers with white-gold shafts circle the figure at chest height (one sweeping across in front while the other passes behind); a thin oval of golden light round the body (26 x 36 squares, 1 square thick, brightest at the sides, broken at the top and the bottom); a soft gold glow on the ground at the feet (an ellipse 20 x 6 squares); a few pale gold motes drift up.
Layout: one horizontal row of 6 equal cells, each 480x640 (image 2880x640); the figure's feet 4 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `rakan_fx_p_on.png`：被动「异色羽裳」的护盾（洛身上，循环），6 帧

被动护盾挂在洛身上的时候：身边一圈带虹彩的金色护罩，**只画边，里面空着**，青色、紫色的亮光沿着边转，护罩上下两头有羽毛形的卷纹，三根小羽毛绕着它慢慢飘（参考 P_Shield_circle、P_Shield_decal、P_dot_circle）。中间是人，不要画人，别盖住人。6 帧无缝循环。约 34 格宽、46 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C) and an iridescent ramp (#FFFFFF, #DBF7FF, #94F7EF, #4FE0C8, #5AA0F0, #7A6CE8, #A64CD0, #6A2A9A).
Effect: a LOOPING FEATHER SHIELD round a figure (do NOT draw the figure; leave the whole inside EMPTY - draw only the rim), 6 frames, a seamless loop: the rim of an upright oval shield round the figure (30 x 42 squares), 1-2 squares of golden light thick, iridescent cyan and violet highlights running round it (a sixth of the way each frame), fine feather-like curls at the rim's top and bottom; 3 tiny golden feathers drifting round the rim; the oval's bottom at the feet.
Layout: one horizontal row of 6 equal cells, each 544x736 (image 3264x736); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `rakan_fx_r_start.png`：R 惊鸿过隙：开大的一下（洛身上），6 帧

开大：洛身上一道白金色的闪光，一圈金光和金色、青色、紫色的羽毛从他身上往四面炸开，几道金橙色的光箭往身后（左）射出去（参考 R_flarebuilding、R_activate_arrow、R_bigglow02、R_swirl_sharp、R_gradient_RGB）。中间是人，不要画人。约 40 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C) and an iridescent ramp (#FFFFFF, #DBF7FF, #94F7EF, #4FE0C8, #5AA0F0, #7A6CE8, #A64CD0, #6A2A9A).
Effect: a DAZZLING ACTIVATION BURST on a figure (do NOT draw the figure; leave its place empty), 6 frames: 1 a white-gold star flash at the figure's chest; 2 a ring of golden light bursts out round the figure, 8 small feathers in gold, cyan and violet flying out in all directions; 3 the ring at full size (36 squares wide), 3 streaks of orange-gold light shooting off to the LEFT behind the figure; 4 the feathers farther out, the streaks long; 5 the ring breaks into sparkles; 6 fading sparkles.
Layout: one horizontal row of 6 equal cells, each 320x352 (image 1920x352) (8 px a square here); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `rakan_fx_r_on.png`：R 持续：身后的光尾（洛身上，循环），4 帧

大招的 4 秒里洛跑得飞快：身后拖着三条波浪形的光带，中间一条金橙色、外面两条青色和紫色（像羽毛的虹彩），光带里闪着白金色的星点，往后慢慢淡掉；人身边一层淡淡的金光（参考 R_Trail、R_Trail_02、R_swirl_sharp、R_glow_distort、R_gradient_RGB）。人往右跑，光尾在左边。中间是人，不要画人。4 帧无缝循环。约 48 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF8D6, #FFE47A, #FFC63A, #FF9E21, #F07018, #D04A1A, #9A2A1C) and an iridescent ramp (#FFFFFF, #DBF7FF, #94F7EF, #4FE0C8, #5AA0F0, #7A6CE8, #A64CD0, #6A2A9A).
Effect: a LOOPING SPEED TRAIL behind a figure running to the RIGHT (do NOT draw the figure; its place is at the right part of the cell), 4 frames, a seamless loop: 3 wavy ribbons of light stream 34 squares to the LEFT behind the figure at hip to chest height - gold and orange in the middle ribbon, cyan and violet in the outer two (an iridescent feather trail) - fading out toward the left end; small white-gold sparkles twinkle along them; a faint golden glow round the figure's place; the ribbons' waves move a little to the left every frame.
Layout: one horizontal row of 4 equal cells, each 384x240 (image 1536x240) (8 px a square here); the figure's place at the RIGHT end - its feet 8 squares (64 px) from the right edge and 4 squares (32 px) above the bottom - in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `rakan_fx_r_charmed.png`：R 魅惑（目标头上），8 帧

被洛碰到的敌人被魅惑（约 1.2 秒）：头上冒出几颗金色的爱心，白芯、金橙色的心、玫红色的边，一边晃一边往上飘（参考 R_charm_heart、R_charm_dots）。只画爱心和小光点。约 18 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, feathers, sparks or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a heart ramp (#FFFFFF, #FFF3C6, #FFD554, #FFAC12, #F06A2A, #E0405A, #A82048).
Effect: CHARM HEARTS rising from a point (do NOT draw a figure), 8 frames: 1 a gold-pink sparkle at the lower middle of the cell; 2 a heart 6 squares wide pops out there: white-gold core, gold and orange body, a rose-red rim; 3 a second, smaller heart pops out beside it, both rising; 4-6 the hearts float up and sway left and right, a third small heart appears, tiny sparkles round them; 7 the hearts near the top, fading; 8 two fading sparkles.
Layout: one horizontal row of 8 equal cells, each 288x384 (image 2304x384); the hearts start at the lower middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `rakan_fx_a_feather` | view_projectiles `league_rakan_a_feather`（循环，朝飞行方向转） | 12 × 5 |
| `rakan_fx_a_hit` | view_effects `league_rakan_a_hit`（跟随，画在人物上面） | 12 |
| `rakan_fx_q_feather` | view_projectiles `league_rakan_q_feather`（循环，朝飞行方向转） | 22 × 9 |
| `rakan_fx_q_hit` | view_effects `league_rakan_q_hit`（跟随，画在人物上面） | 18 |
| `rakan_fx_q_heal` | view_buffs `league_rakan_q_heal`（循环，画在人物下面） | 32 × 24 |
| `rakan_fx_q_burst` | view_effects `league_rakan_q_burst`（BIG，洛脚下，不跟随，画在人物下面） | 84 × 48 |
| `rakan_fx_q_healed` | view_effects `league_rakan_q_healed`（跟随，画在人物上面） | 16 × 24 |
| `rakan_fx_w_burst` | view_effects `league_rakan_w_burst`（BIG，洛脚下，不跟随，画在人物下面） | 32 × 40 |
| `rakan_fx_w_hit` | view_effects `league_rakan_w_hit`（跟随，画在人物上面） | 16 × 26 |
| `rakan_fx_e_shield` | view_effects `league_rakan_e_shield`（跟随，画在人物上面） | 26 × 30 |
| `rakan_fx_e_on` | view_buffs `league_rakan_e_on`（循环，画在人物上面） | 30 × 40 |
| `rakan_fx_p_on` | view_buffs `league_rakan_p_on`（循环，画在人物上面） | 34 × 46 |
| `rakan_fx_r_start` | view_effects `league_rakan_r_start`（跟随，开大第一 tick 放，画在人物上面） | 40 × 44 |
| `rakan_fx_r_on` | view_buffs `league_rakan_r_on`（循环，画在人物下面，朝左时镜像） | 48 × 30 |
| `rakan_fx_r_charmed` | view_effects `league_rakan_r_charmed`（跟随，画在人物上面） | 18 × 24 |

- 技能数据要跟着改：`q_heal` 的 view_buffs `z` 改成 -1（脚下的圈画在人下面）；加 `r_on` 的 view_buffs（R 的加速 buff，循环，`z` -1）；R 的碰撞圈 `r_ring` 去掉画面（英雄联盟的 R 地上没有圈）。
- 施法者身上的画面（`q_burst`、`w_burst`、`r_start`）画在站位点上：按 `design/rakan_shots.png` 的十字（脚下）把格子的起点挪过去；`q_burst` 的椭圆按治疗半径 40000 缩放（80 格宽），`w_burst` 的地面裂纹按 12000（24 格宽）。
- `p_on`、`q_heal`、`e_on`、`r_on` 是跟着人的循环 buff 画面；`r_charmed` 对到目标头顶上方。
- 清掉 Codex 给光和羽毛描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
