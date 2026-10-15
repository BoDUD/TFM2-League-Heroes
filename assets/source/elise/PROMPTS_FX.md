# 蜘蛛女皇 伊莉丝：给 Codex 的特效提示词（第 3 步）

> **这一份是 22 张特效图。** 造型和动作已定（`design/elise_idle.png`：人形 3/4 正面待机，背后六条蜘蛛腿；蜘蛛 3/4 视角朝右）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），人形连背后的蜘蛛腿 48 格高、32 格宽，蜘蛛 28 格高、44 格长；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/elise_size.png`：两种形态的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/elise_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里伊莉丝自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**毒液和撕咬是深红色的光（白芯）配紫色的毒烟**，**茧和蛛丝是灰白色的丝（白芯）带一点红光**，**小蜘蛛是黑色的、背上发红光**，**变身是暗紫色的烟加深红的火星**。
> - **特效要亮**：每团光、每根丝都要有白色或最亮一档的芯，暗底上一眼能看见（她本人很暗，特效尤其要亮）。
> - **围着人的光圈、火焰只画外圈和两边，中间身体位置留空**（变身 `tf_spider` / `tf_human` 例外：那一下就是要把她盖住；茧 `e_hit` 的丝可以横着盖过身体，但要有空隙）。
> - **方向（重要，红色方不会镜像）**：飞出去的 `a_spit`、`q_bolt`、`e_web`、`w_spider`（从上往下看的小蜘蛛）画成朝右，**上下对称**（往左飞时会上下翻）。其余所有画面（打中、身上、脚下、头顶、地上的爆炸和落地、蛛丝）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）——刺痕、毒牙一律两边同时合拢，不要画成往一个方向斜的。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `elise_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `elise_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「蜘蛛女皇」 | 人形吐毒液 / 蜘蛛前腿刺击；人形技能命中积攒小蜘蛛，蜘蛛普攻时小蜘蛛扑上去撕咬 | `a_spit` · `a_hit` · `c_hit` · `sl_bite1` · `sl_bite2` · `sl_bite3` |
| 技能 1 = Q「神经毒素 / 剧毒之蜇」 | 人形：毒液弹；蜘蛛：扑上去咬 | `q_bolt` · `q_hit` · `cq_hit` |
| 技能 2 = E「结茧」+ W「自爆蜘蛛」/ E「盘丝」+ W「掠行狂暴」 | 人形：吐茧晕眩、放会爆炸的小蜘蛛；蜘蛛：顺着丝升空落到英雄身上、狂暴加攻速 | `e_web` · `e_hit` · `w_spider` · `w_boom` · `w_hit` · `ce_up` · `ce_land` · `ce_hit` · `cw_frenzy` · `cw_on` |
| 变身（普攻时自动）+ 大招「蜘蛛形态」茧缚猎杀 | 人和蜘蛛来回切换；5 级大招吐茧、变蜘蛛、盘丝落到英雄身上咬 | `tf_spider` · `tf_human` · `r_cast` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、火星、蛛丝、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（小蜘蛛例外：它的黑色身体可以有一圈深色边）。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 深红毒液（毒液、撕咬、狂暴）：`#FFFFFF`、`#FFD1DA`、`#FF5C7A`、`#E0143C`、`#9E0A2A`、`#4F0618`；
  - 紫色毒烟（毒烟、变身）：`#F3E6FF`、`#C9A6F2`、`#8E5BD0`、`#5B2E94`、`#2E1452`；
  - 蛛丝（茧、盘丝的丝）：`#FFFFFF`、`#ECEAF2`、`#C9C6D6`、`#9D99B0`、`#6E6A82`；
  - 小蜘蛛的身体：`#4A3550`、`#2A1E30`、`#120C16`；
  - 尘土（落地）：`#F2E6CF`、`#D6C3A0`、`#B39B76`、`#8A7255`、`#5E4C39`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人或蜘蛛**（小蜘蛛的几张除外：小蜘蛛本身就是特效）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（22 张）

22 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：人形普攻距离 50000，结茧射程 75000，自爆蜘蛛爆炸半径 10000，盘丝落地半径 12000）。

### 1. `elise_fx_a_spit.png`：普攻：吐出去的毒液（朝目标飞，循环），2 帧

人形普攻甩出去的毒液：一团深红色的毒液球（白芯），后面一小段紫色的烟尾（参考 BA_Head_01、BA_Streak、BA_GlowTrail）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618) and a violet smoke ramp (#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452).
Effect: a VENOM GLOB flying to the RIGHT, 2 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a crimson venom drop 5 squares long and 3 tall with a white core at its front; a short violet smoke tail 5 squares long behind it, flickering between the two frames.
Layout: one horizontal row of 2 equal 14:6 cells, image size 448x96 (each cell 224x96, 16 px a square); the glob's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `elise_fx_q_bolt.png`：Q 神经毒素：毒液弹（朝目标飞，循环），4 帧

神经毒素：一颗更大的毒液弹，深红色的芯外面缠着一圈紫色的毒烟，后面拖一条渐细的紫红色尾巴和几点毒液火星（参考 Q_Mis_Shockwaves、Elise_Qtrail、Q_Sharp）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618) and a violet smoke ramp (#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452).
Effect: a NEUROTOXIN BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a crimson venom orb 6 squares across with a white core, wrapped in a ring of violet toxic smoke 2 squares thick; a tapering violet-and-crimson trail 10 squares long behind it; 2 crimson motes at mirrored places flickering in turn.
Layout: one horizontal row of 4 equal 22:10 cells, image size 1408x160 (each cell 352x160, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `elise_fx_a_hit.png`：普攻打中（目标身上），4 帧

毒液打中：一小团深红色的毒液溅开（白芯），几滴往外飞（参考 Star_Flash）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a SMALL VENOM SPLASH on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a crimson splash 7 squares across with a white core; 3 the splash 10 squares, 6 droplets flying out at mirrored places; 4 a few fading droplets.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `elise_fx_q_hit.png`：Q 神经毒素打中（目标身上），5 帧

神经毒素命中：一团深红色的毒液炸开（白芯），外面一圈紫色的毒烟往外翻卷，几滴毒液溅出（参考 Q_Impact03、Q_SmokeErosionT）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618) and a violet smoke ramp (#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452).
Effect: a NEUROTOXIN IMPACT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a crimson venom burst 10 squares across with a white core; 3 the burst 16 squares across, violet smoke curling out at both sides; 4 the smoke 18 squares, venom droplets at mirrored places; 5 fading smoke and droplets.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `elise_fx_c_hit.png`：蜘蛛普攻打中（目标身上），4 帧

蜘蛛前腿刺中：两道深红色的弯钩刺痕从左右两边同时划下、交在中间，交点一闪（参考 Q_bite、Impacts02_ErosionSheet）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a STAB-HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two curved crimson hook marks sweeping DOWN from the upper left and upper right at once, meeting in the middle; 1 the two hooks starting 8 squares apart; 2 the hooks meeting, a white flash 3 squares where they meet; 3 the marks 12 squares tall, the flash fading; 4 the marks fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `elise_fx_cq_hit.png`：Q 剧毒之蜇打中（目标身上），5 帧

剧毒之蜇：两颗巨大的弯毒牙从左右两边合拢咬下（参考 Q_bite 那对白色的弯牙），咬合处喷出一团深红的毒液和紫色的毒烟。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618) and a violet smoke ramp (#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452).
Effect: a VENOMOUS BITE on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two huge curved fangs, white with crimson tips, closing in from the left and the right; 1 the fangs wide apart 18 squares, open; 2 the fangs closing; 3 the fangs meeting in the middle, a crimson venom burst 12 squares with a white core between them; 4 the burst 20 squares, violet smoke at both sides; 5 the fangs gone, fading venom droplets.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `elise_fx_sl_bite1.png`：被动 小蜘蛛撕咬（1 只，目标身上），3 帧

蜘蛛形普攻时小蜘蛛扑在目标身上撕咬：1 只黑色小蜘蛛（背上发红光、红眼睛，参考 EliseSpiderling 和 W_SpiderShape），咬下去时有一小点深红的咬痕闪光。**左右对称**，中间人形位置留空（只画小蜘蛛扑上来的位置）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chitin ramp (#4A3550, #2A1E30, #120C16) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: SPIDERLINGS BITING a figure, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY except where they cling (an upright figure 10 squares wide and 22 tall stands there, not drawn): ONE spiderling clinging at the top middle (on the head's place); each spiderling 5 squares wide and 4 tall seen from the front, a black body with a glowing crimson back and two red eye dots, legs splayed; 1 the spiderlings leaping on; 2 biting, a small crimson bite flash 3 squares at each; 3 holding on, the flashes fading.
Layout: one horizontal row of 3 equal 16:26 cells, image size 768x416 (each cell 256x416, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `elise_fx_sl_bite2.png`：被动 小蜘蛛撕咬（2 只，目标身上），3 帧

蜘蛛形普攻时小蜘蛛扑在目标身上撕咬：2 只黑色小蜘蛛（背上发红光、红眼睛，参考 EliseSpiderling 和 W_SpiderShape），咬下去时有一小点深红的咬痕闪光。**左右对称**，中间人形位置留空（只画小蜘蛛扑上来的位置）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chitin ramp (#4A3550, #2A1E30, #120C16) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: SPIDERLINGS BITING a figure, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY except where they cling (an upright figure 10 squares wide and 22 tall stands there, not drawn): TWO spiderlings clinging at the left and right sides at waist height, mirrored; each spiderling 5 squares wide and 4 tall seen from the front, a black body with a glowing crimson back and two red eye dots, legs splayed; 1 the spiderlings leaping on; 2 biting, a small crimson bite flash 3 squares at each; 3 holding on, the flashes fading.
Layout: one horizontal row of 3 equal 16:26 cells, image size 768x416 (each cell 256x416, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `elise_fx_sl_bite3.png`：被动 小蜘蛛撕咬（3 只，目标身上），3 帧

蜘蛛形普攻时小蜘蛛扑在目标身上撕咬：3 只黑色小蜘蛛（背上发红光、红眼睛，参考 EliseSpiderling 和 W_SpiderShape），咬下去时有一小点深红的咬痕闪光。**左右对称**，中间人形位置留空（只画小蜘蛛扑上来的位置）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chitin ramp (#4A3550, #2A1E30, #120C16) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: SPIDERLINGS BITING a figure, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY except where they cling (an upright figure 10 squares wide and 22 tall stands there, not drawn): THREE spiderlings: one at the top middle and two at the left and right sides at waist height, mirrored; each spiderling 5 squares wide and 4 tall seen from the front, a black body with a glowing crimson back and two red eye dots, legs splayed; 1 the spiderlings leaping on; 2 biting, a small crimson bite flash 3 squares at each; 3 holding on, the flashes fading.
Layout: one horizontal row of 3 equal 16:26 cells, image size 768x416 (each cell 256x416, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `elise_fx_e_web.png`：E 结茧：飞出去的茧（朝目标飞，循环），4 帧

结茧：一团旋转的蛛丝茧（灰白色的丝一圈圈缠着，中间一点红光），后面拖几根蛛丝（参考 E_Cocoon、E_SpiderWeb_01、E_Trail）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silk ramp (#FFFFFF, #ECEAF2, #C9C6D6, #9D99B0, #6E6A82) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a SPINNING COCOON flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a ball of grey-white silk 7 squares across, strands wound round it, a small crimson glint at its centre, the strands' bright lines moving round between frames; 3 silk threads 7 squares long trailing behind it, mirrored above and below.
Layout: one horizontal row of 4 equal 18:10 cells, image size 1152x160 (each cell 288x160, 16 px a square); the ball's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `elise_fx_e_hit.png`：E 结茧：被茧住的目标（目标身上），6 帧

被茧住（晕眩）：一层层灰白色的蛛丝从脚下往上缠住目标，缠成一个茧的轮廓，丝上有几点红光（参考 E_Cocoon、Elise_OuterWeb、E_SoftStrings）。第 4 帧会停很久（晕眩约 1.7 秒）。**左右对称**，丝可以横着盖过身体，但不要画成实心的一团。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silk ramp (#FFFFFF, #ECEAF2, #C9C6D6, #9D99B0, #6E6A82) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a SILK COCOON wrapping a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 10 squares wide and 22 tall stands in the middle, not drawn): 1 silk strands shooting up from the ground at both sides; 2 strands wrapping round the legs, crossing in front; 3 the strands up to the shoulders, a cocoon outline 14 squares wide and 24 tall; 4 the full cocoon of crossing strands with gaps between them, 3 crimson glints at mirrored places (this frame is held for a second and a half); 5 the strands snapping at both sides; 6 loose strands falling.
Layout: one horizontal row of 6 equal 16:28 cells, image size 1536x448 (each cell 256x448, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `elise_fx_w_spider.png`：W 自爆蜘蛛：爬过去的小蜘蛛（朝目标走，循环），4 帧

自爆蜘蛛：一只从上往下看的黑色小蜘蛛，头朝右，背上发着红光，八条腿上下对称地交替迈步（参考 W_SpiderShape、W_SpiderEyes_01、EliseSpiderling）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a chitin ramp (#4A3550, #2A1E30, #120C16) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a SMALL SPIDER seen from ABOVE crawling to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a black body 5 squares long, a glowing crimson back with a white-hot spot, red eye dots at the head's front (right), four legs above and four below mirrored, stepping in turn (frames 1-2 the front pairs forward, 3-4 the back pairs), the back's glow pulsing.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `elise_fx_w_boom.png`：W 自爆蜘蛛爆炸（地上，不跟随），6 帧

小蜘蛛爆炸：地上炸开一团深红色的毒液火光（白芯），一圈扁扁的冲击环在地面扩开，紫色的毒烟往上翻，几块小碎片飞出（参考 W_WaveExplosion、W_Flame_Ring、W_GroundDecal）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618) and a violet smoke ramp (#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452).
Effect: a SPIDERLING BLAST on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares on the ground; 2 a crimson fireball 10 squares across with a white core, a flat ground ring 14 wide and 5 tall; 3 the blast 16 squares, the ring 20 wide; 4 violet smoke rising at both sides, the ring 22 wide and fading, small bits flying out at mirrored places; 5 smoke and a few embers; 6 the last wisps.
Layout: one horizontal row of 6 equal 24:20 cells, image size 2304x320 (each cell 384x320, 16 px a square); centered across, the ground ring's middle 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `elise_fx_w_hit.png`：W 自爆蜘蛛波及（被炸到的目标身上），3 帧

被爆炸波及：目标身上一小团深红的毒火闪一下。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a SMALL BLAST-HIT on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a crimson flash 6 squares with a white core; 2 the flash 10 squares with 4 short rays; 3 fading embers.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `elise_fx_ce_up.png`：E 盘丝：升空的蛛丝（她身上，跟随），5 帧

盘丝：一根白亮的蛛丝从天上垂下来粘在她背上，绷紧，把她拉上去（丝从上往下垂、最后整根往上收回）（参考 E_SoftStrings、E_DebrisString）。**左右对称**，丝在格子正中间竖直。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silk ramp (#FFFFFF, #ECEAF2, #C9C6D6, #9D99B0, #6E6A82) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a SILK THREAD from the sky, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): one vertical grey-white silk thread 1 square thick with a bright white core line, in the middle column; 1 the thread dropping from the cell's top, its end 20 squares down; 2 the thread reaching down to a small 4-square web anchor at 16 squares above the cell's bottom (the creature's back), a crimson glint at the anchor; 3 the thread taut, a few short silk strands at the anchor; 4 the anchor and the thread pulled UP to halfway; 5 only the top of the thread, pulled up out of sight.
Layout: one horizontal row of 5 equal 12:60 cells, image size 960x960 (each cell 192x960, 16 px a square); the thread in the middle column of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `elise_fx_ce_land.png`：E 盘丝落地（地上，不跟随），6 帧

盘丝落地：地面一圈尘土和碎石溅起，地上留下一张蛛网形状的裂纹，几根断丝飘起（参考 E_FootCrater、E_Rocks_2X2、E_DebrisString）。**左右对称**，中间落地的身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39) and a silk ramp (#FFFFFF, #ECEAF2, #C9C6D6, #9D99B0, #6E6A82).
Effect: a HEAVY LANDING on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle above the ground EMPTY (the spider lands there): 1 a flat dust ring 10 wide and 3 tall; 2 the dust ring 20 wide, 6 rock chips flying up at mirrored places; 3 the dust 26 wide and 8 tall at both sides, a spider-web crack 16 wide and 4 tall on the ground under it in grey-white silk; 4 the dust settling, the web crack clear; 5 the web crack and a few broken silk strands floating up; 6 the crack fading.
Layout: one horizontal row of 6 equal 28:14 cells, image size 2688x224 (each cell 448x224, 16 px a square); centered across, the ground crack's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `elise_fx_ce_hit.png`：E 盘丝落地打中（目标身上），4 帧

盘丝落地砸中：目标身上一闪深红的冲击光，几根白丝溅开。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618) and a silk ramp (#FFFFFF, #ECEAF2, #C9C6D6, #9D99B0, #6E6A82).
Effect: a LANDING IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a crimson burst 9 squares with a white core; 3 the burst 12 squares, 4 short silk strands flying out at mirrored places; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `elise_fx_cw_frenzy.png`：W 掠行狂暴：狂暴发作（她身上），5 帧

掠行狂暴：蜘蛛身上腾起一圈深红色的狂暴火焰和红色的速度光痕，从身体两边往上冲（参考 W_Glow、W_Sparks）。**左右对称**，中间蜘蛛的身体位置留空（只画外圈）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a FRENZY FLARE round a wide crouching creature, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 44 squares wide and 26 tall where the creature is, not drawn): 1 crimson sparks at both sides on the ground; 2 crimson flame tongues rising at both sides 16 squares tall with white cores; 3 the flames 26 squares tall, red speed streaks at mirrored places; 4 the flames breaking into sparks; 5 a few last sparks.
Layout: one horizontal row of 5 equal 52:34 cells, image size 4160x544 (each cell 832x544, 16 px a square); centered across, the creature's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `elise_fx_cw_on.png`：W 掠行狂暴：攻速加成（她脚下，循环），4 帧

狂暴中：蜘蛛脚下一圈深红色的光环（扁椭圆，几点红光轮流闪）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a CRIMSON RING under a wide creature's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin flat ellipse 40 squares wide and 6 tall in crimson, 4 bright motes on it at mirrored places taking turns to light up.
Layout: one horizontal row of 4 equal 44:8 cells, image size 2816x128 (each cell 704x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `elise_fx_tf_spider.png`：变成蜘蛛（她身上，跟随），6 帧

人变蜘蛛：一团暗紫色的烟从她身上卷起把她整个盖住，烟里闪着深红的火星，烟散开时露出蜘蛛（参考 Tendril_Smoke、Smoke_01、E_SpiderDesign_BackgroundBlur、R_LensFlare）。**左右对称**。这一下要把她盖住。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet smoke ramp (#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a DARK TRANSFORMATION burst over a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 violet smoke tendrils curling up at both sides of the ground; 2 the smoke 24 squares tall, crimson sparks inside; 3 the smoke a full cloud 40 squares wide and 40 tall covering the middle, a white-crimson flash at its centre; 4 the cloud breaking open from the top, crimson sparks flying out at mirrored places; 5 smoke wisps low at both sides; 6 the last wisps.
Layout: one horizontal row of 6 equal square cells, image size 4224x704 (each cell 704x704, 16 px a square); centered across, the cloud's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `elise_fx_tf_human.png`：变回人形（她身上，跟随），6 帧

蜘蛛变回人：暗紫色的烟从地面往上旋起、裹成一个人形高的烟柱，顶上一闪深红的光，烟往上散开（同一套颜色）。**左右对称**。这一下要把她盖住。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet smoke ramp (#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452) and a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618).
Effect: a DARK TRANSFORMATION rising over a creature, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 violet smoke spreading flat on the ground 40 squares wide; 2 the smoke swirling up into a column 30 squares tall; 3 the column 40 tall and 24 wide covering the middle, crimson sparks spiralling in it; 4 a crimson-white flash at the top, the column opening; 5 smoke wisps drifting up at both sides; 6 the last wisps high up.
Layout: one horizontal row of 6 equal square cells, image size 4224x704 (each cell 704x704, 16 px a square); centered across, the smoke's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `elise_fx_r_cast.png`：大招 茧缚猎杀：发动（她头顶，跟随），5 帧

茧缚猎杀发动：她头顶浮出一个深红色发光的蜘蛛印记（参考 E_SpiderDesign_BackgroundBlur 的蜘蛛形状），八只红眼一闪，然后化成红光散开。**左右对称**。画在格子上部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, sparks, webs or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson venom ramp (#FFFFFF, #FFD1DA, #FF5C7A, #E0143C, #9E0A2A, #4F0618) and a violet smoke ramp (#F3E6FF, #C9A6F2, #8E5BD0, #5B2E94, #2E1452).
Effect: a SPIDER SIGIL over a head, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a crimson glow 4 squares; 2 a spider-shaped sigil 14 squares wide and 12 tall (a round body, eight thin legs spread, mirrored) in crimson with a white core outline; 3 the sigil brightest, eight red eye dots flashing on its head; 4 the sigil breaking into crimson motes; 5 a few last motes.
Layout: one horizontal row of 5 equal 20:44 cells, image size 1600x704 (each cell 320x704, 16 px a square); the sigil's middle 8 squares from the TOP of the cell, centered; the rest of the cell empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `elise_fx_a_spit` | view_projectiles `league_elise_a_spit`（朝飞行方向转，画成朝右飞；上下对称） | 12 × 5 |
| `elise_fx_q_bolt` | view_projectiles `league_elise_q_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 20 × 8 |
| `elise_fx_a_hit` | view_effects `league_elise_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `elise_fx_q_hit` | view_effects `league_elise_q_hit`（跟随，画在人物上面；左右对称） | 18 |
| `elise_fx_c_hit` | view_effects `league_elise_c_hit`（跟随，画在人物上面；左右对称） | 12 |
| `elise_fx_cq_hit` | view_effects `league_elise_cq_hit`（跟随，画在人物上面；左右对称） | 20 |
| `elise_fx_sl_bite1` | view_effects `league_elise_sl_bite1`（跟随，画在人物上面；左右对称） | 16 × 26 |
| `elise_fx_sl_bite2` | view_effects `league_elise_sl_bite2`（跟随，画在人物上面；左右对称） | 16 × 26 |
| `elise_fx_sl_bite3` | view_effects `league_elise_sl_bite3`（跟随，画在人物上面；左右对称） | 16 × 26 |
| `elise_fx_e_web` | view_projectiles `league_elise_e_web`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 9 |
| `elise_fx_e_hit` | view_effects `league_elise_e_hit`（跟随，画在人物上面；左右对称） | 16 × 26 |
| `elise_fx_w_spider` | view_projectiles `league_elise_w_spider`（朝飞行方向转，画成朝右爬；上下对称） | 10 × 10 |
| `elise_fx_w_boom` | view_effects `league_elise_w_boom`（不跟随，地上；左右对称；大图表） | 22 × 18 |
| `elise_fx_w_hit` | view_effects `league_elise_w_hit`（跟随，画在人物上面；左右对称） | 10 |
| `elise_fx_ce_up` | view_effects `league_elise_ce_up`（跟随她，画在人物上面；左右对称；大图表） | 12 × 60 |
| `elise_fx_ce_land` | view_effects `league_elise_ce_land`（不跟随，地上；左右对称；大图表） | 26 × 12 |
| `elise_fx_ce_hit` | view_effects `league_elise_ce_hit`（跟随，画在人物上面；左右对称） | 12 |
| `elise_fx_cw_frenzy` | view_effects `league_elise_cw_frenzy`（跟随她，画在人物上面；左右对称） | 52 × 34 |
| `elise_fx_cw_on` | view_buffs `league_elise_cw_on`（跟随，画在人物下面；左右对称） | 42 × 8 |
| `elise_fx_tf_spider` | view_effects `league_elise_tf_spider`（跟随她，画在人物上面；左右对称；大图表） | 44 × 44 |
| `elise_fx_tf_human` | view_effects `league_elise_tf_human`（跟随她，画在人物上面；左右对称；大图表） | 44 × 44 |
| `elise_fx_r_cast` | view_effects `league_elise_r_cast`（跟随她，画在人物上面；左右对称；大图表） | 20 × 44 |

- 两张表：`asset/league/effects/league_elise_fx`（小的）和 `league_elise_big`（w_boom、ce_up、ce_land、tf_spider、tf_human、r_cast），tag = 名字（build_elise.py 的 views）。
- `a_spit`、`q_bolt`、`e_web`、`w_spider` 是飞行投射物，画面朝飞行方向转；`w_boom`、`ce_land` 不跟随；`cw_on` 脚下 buff（z -1）；`r_cast` 头顶；`e_hit` 第 4 帧拉长到晕眩的 100 tick。
- 用 `pixel_1x/` 切格（import_nidalee 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
