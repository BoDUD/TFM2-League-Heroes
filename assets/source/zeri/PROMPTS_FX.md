# 祖安花火 泽丽：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型和动作已定（`design/zeri_design.png`，8 倍，40 行、24 格宽）。
> - 大小对照 `design/zeri_size.png`：定稿造型放大 4 倍，鞋底在红线上，上面是 10 格一段的刻度，右边是原版斗士。泽丽 24×40 格。每条写的大小都是游戏像素（格）。
> - `design/zeri_shots.png`：定稿动作的出手帧（4 倍），青色十字是特效的起点（平端的步枪枪口、脚下），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里泽丽自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的电是明亮的柠檬黄绿色、白色的芯、青色的边；W 的激光从黄色渐变到青色；R 的新星和超载外面带一点彩虹色的边**。
> - **特效要亮**：每个电光、光束、火花都用最亮的几档和白色的芯，暗底上一眼能看见。
> - **围着人的电光（充满电、蓄力、护盾、E 生效、超载）只画外圈和两边，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：飞出去的电弹、脉冲、电击弹、三连发、附加包的激光段（`a_burst`、`p_spark`、`w_pulse`、`w_wall`、`e_shot`、`r_shot`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。长激光 `w_laser` 是**线的画面**：游戏把整张图的**中心**放在脉冲停下的点上、朝「泽丽→那一点」的方向转，所以**激光只画在格子右半边、从正中间往右射**，同样**上下对称**。画在人身上、脚下的（打中、减速、加速、护盾、充满电、蓄力、冲刺电光、E 生效、超载、连锁闪电）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；地上的电新星 `r_nova` 上下左右都对称。
> - 特效照下面第 1–24 条和「所有特效图的规则」画，每张一个 PNG，文件名 `zeri_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。
> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`zeri_fx_done.zip`）放在 outputs 里，或放在 `outputs/zeri-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 = Q「电火迸射」 | 一串 7 发的连射，打第一个挡路的敌人 | `a_burst` · `a_hit` |
| 被动「内能迁转」 | 普攻充电，充满后下一发变成追踪的电击弹（魔法伤害 + 减速，命中英雄得护盾和加速） | `p_ready` · `p_spark` · `p_hit` · `p_slow` · `p_shv` · `p_haste` |
| 技能 1 = W「强穿激光」 | 射出电脉冲打第一个敌人（伤害 + 减速）；先打中小兵或野怪时从那里化成一道长激光（附加包：打到墙也会） | `w_cast` · `w_pulse` · `w_laser` · `w_wall` · `w_hit` · `w_slow` |
| 技能 2 = E「灿丽花火」 | 按局势冲刺，之后 5 秒普攻贯穿并附带魔法伤害 | `e_cast` · `e_on` · `e_shot` · `e_hit` |
| 大招 = R「超限爆闪」 | 以她为中心的电新星，然后超载：攻速、移速，普攻变三连发并在敌人间连锁闪电 | `r_nova` · `r_hit` · `r_on` · `r_st2` · `r_shot` · `r_zap` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**电光、光束、火花、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只做很少的点缀。
- 颜色（按每条写的用）：
  - 柠檬黄绿的电（子弹、电弧、新星、护盾）：`#FFFFFF`、`#FFFFC8`、`#F4FF50`、`#C4F024`、`#72CC14`、`#2E7E0C`；
  - 青色（边、W 激光的尾端、E 的贯穿弹、速度线）：`#FFFFFF`、`#D8FFFF`、`#7CF0FF`、`#24BCF0`、`#1270B8`；
  - 彩虹色的边（只在 R 的新星、超载、打中上细细一圈）：`#FF8CF0`、`#B080FF`、`#FFB040`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 60000，W 激光长 100000、宽 9000，E 冲刺 30000，R 新星半径 75000，连锁闪电半径 30000）。

### 1. `zeri_fx_a_burst.png`：普攻 电火迸射：一串 7 发的连射弹（飞行中，循环），4 帧

泽丽的普攻是一串连发的电弹：画成一行 4–5 颗短短的黄绿色电弹（每颗 2–3 格长，白芯、柠檬黄光），前后排成一条约 18 格长的虚线，最前面一颗最亮（参考 Q_MissileHead01、Bullet_Front、Q_Electricity02）。朝右飞。**上下对称**。4 帧无缝循环（虚线往前挪一格、电光闪动）。约 18 格长、3 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a BURST OF ELECTRIC ROUNDS flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): five short slugs in one row, each 3 squares long and 1-2 tall (a white core, a lime-yellow glow, a faint cyan tip), spaced 1 square apart, 18 squares from the first to the last; the front slug the brightest; the row shifts forward one square each frame.
Layout: one horizontal row of 4 equal 20:5 cells, image size 1280x80 (each cell 320x80, 16 px a square); the front slug 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `zeri_fx_a_hit.png`：普攻打中（目标身上），4 帧

电弹打中：一小团黄绿色的电火花炸开，几根短短的电光往外跳（参考 Q_HitCircle、Hit01_vertical）。**左右对称**。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a SMALL ELECTRIC HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 4 squares across; 2 a lime burst 8 squares across with short zigzag sparks at mirrored places; 3 the sparks flying out, cyan tips; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `zeri_fx_p_spark.png`：被动 内能迁转：充满电后的电击弹（追踪，飞行中，循环），4 帧

充满电的那一发：一颗噼啪作响的电球（白芯、柠檬黄、外圈青色电弧），后面拖一小段锯齿状的电光尾（参考 Q_MissileHead01、W_electricity02、Flare）。朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a CHARGED ELECTRIC SPARK flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a crackling ball 6 squares across at the right (a white core, lime-yellow, a ring of short cyan arcs), a jagged lightning tail 6 squares long behind it; the arcs jump round the ball frame to frame (keep each frame mirrored top to bottom).
Layout: one horizontal row of 4 equal 14:11 cells, image size 896x176 (each cell 224x176, 16 px a square); the ball's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `zeri_fx_p_hit.png`：电击弹打中（目标身上），5 帧

电击弹打中：一团更大的电爆，中心白光，外面一圈黄绿色的电弧，几道青色的电光往外劈（参考 Hit02_vertical、Q_HitCircle、W_Flash01）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a CHARGED ELECTRIC BLAST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a lime-yellow burst 12 squares across with a white core; 3 zigzag lightning bolts out to mirrored places, cyan edges, 16 squares across; 4 the bolts breaking into sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `zeri_fx_p_ready.png`：电量充满（她身上，充满的一刻），6 帧

电池充满：她身边噼啪闪过一圈电光（从脚下往上窜到头顶），最后头顶上方一下亮光（参考 Flare、W_electricity02_Vertical、Glow06）。**中间人站的位置留空**，**左右对称**（逐格对称）。约 30 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a FULL CHARGE CRACKLE round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (14 x 36 squares, its bottom on the cell's bottom) EMPTY: 1 two short lime arcs at the feet on both sides; 2 the arcs climbing to the hips, small white sparks; 3 the arcs at the chest, cyan edges; 4 the arcs at the head, brightest; 5 a white-yellow star 6 squares across above the head, the arcs fading; 6 a few fading sparks.
Layout: one horizontal row of 6 equal 32:44 cells, image size 3072x704 (each cell 512x704, 16 px a square); centered across, the figure area's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `zeri_fx_p_shv.png`：护盾（她身上，持续 3 秒，循环），4 帧

电击弹命中英雄后的护盾（装附加包时是偷来的盾）：围着她一圈椭圆形的电光护罩，只画外圈（柠檬黄的边、几处青色的电弧沿着边流动），里面空着让人能看见（参考 W_Shield、P_Shield_Reveal、EdgeGlow）。**左右对称**。4 帧无缝循环。约 30 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: an ELECTRIC SHIELD round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the inside EMPTY: an upright oval ring 28 squares wide and 42 tall, 1-2 squares thick, lime-yellow with a white highlight at the top, a few short cyan arcs running along the ring at mirrored places (they step round the ring each frame).
Layout: one horizontal row of 4 equal 32:46 cells, image size 2048x736 (each cell 512x736, 16 px a square); centered across, the oval's bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `zeri_fx_p_slow.png`：电击弹的减速（被减速的人脚下，循环），4 帧

被电击弹减速：脚下一圈细细的黄绿色电环，环上有几个跳动的电火花（左右对称）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C).
Effect: an ELECTRIC SLOW RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin lime ellipse 12 squares wide and 3 tall, small white-yellow sparks on it at mirrored places that flicker.
Layout: one horizontal row of 4 equal 16:7 cells, image size 1024x112 (each cell 256x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `zeri_fx_p_haste.png`：被动的加速（她脚下，1.5 秒，循环），4 帧

命中英雄后的加速：她脚边两侧几道短短的青色速度线和电火花（左右对称）（参考 W_Speedline、ZoomLines）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8) and a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C).
Effect: SPEED STREAKS at a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on each side of the feet two short cyan streaks 3-4 squares long and a small lime spark, mirrored; they flicker and shift one square up or down.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `zeri_fx_w_cast.png`：W 强穿激光：蓄力（她身上，施法时），5 帧

W 蓄力：她身边几道电弧往中间收、越来越亮，然后一下闪光（参考 W_Wirlpool01、W_electricity02、W_Flash01）。**中间人站的位置留空**，**左右对称**。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a CHARGING SURGE round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (14 x 36 squares, its bottom on the cell's bottom) EMPTY: 1 four faint lime arcs at the corners; 2 the arcs curving inward toward the chest, brighter; 3 the arcs close to the figure, white sparks; 4 a bright yellow-white ring 20 squares wide and 6 tall at chest height (only its left and right ends show beside the figure); 5 fading.
Layout: one horizontal row of 5 equal 32:42 cells, image size 2560x672 (each cell 512x672, 16 px a square); centered across, the figure area's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `zeri_fx_w_pulse.png`：W 射出的电脉冲（飞行中，循环），4 帧

W 的电脉冲：一道又亮又长的电弹（白芯、柠檬黄、尾巴渐变成青色），前端尖、后面一条细的光尾（参考 W_mis_glowTrail、W_Trail03、W_color）。朝右飞。**上下对称**。4 帧无缝循环。约 16 格长、7 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: an ELECTRIC PULSE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a pointed bolt 7 squares long and 5 tall at the right (a white core, lime-yellow body), a tapering trail 9 squares long behind it that turns from yellow to cyan, small arcs flickering along it.
Layout: one horizontal row of 4 equal 18:9 cells, image size 1152x144 (each cell 288x144, 16 px a square); the bolt's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `zeri_fx_w_laser.png`：W 打中小兵后化成的长激光（地上的线，朝方向转），6 帧

W 打中小兵或野怪后，从那里往外射出一道 100 格长的激光：白色的芯、柠檬黄的光、边上青色，越往外越变青（参考 W_color、W_BeamGrad、W_electricity02）。光束从起点往右「射」出去，第 2 帧射满，然后变细、碎成电火花。**整张图左半边是空的**（游戏把这张图的中心放在脉冲停下的点上，往外射）。**上下对称**。光束约 7 格高，起点处一团闪光。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a LASER BEAM shooting to the RIGHT from the cell's CENTER, 6 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): the LEFT HALF of every cell stays EMPTY; the beam starts exactly at the cell's center: a white core 3 squares tall, lime-yellow round it, cyan edges, 7 squares tall, its color turning from yellow at the start to cyan at the far end, a bright white-yellow flash 9 squares across at the start; 1 the beam 40 squares long; 2 the full 100 squares, brightest; 3 the full beam; 4 the beam thinner (3 tall); 5 breaking into sparks along the line; 6 fading sparks.
Layout: one horizontal row of 6 equal 204:15 cells, image size 19584x240 (each cell 3264x240, 16 px a square); the beam's start on the cell's exact center column, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `zeri_fx_w_wall.png`：（附加包）W 撞墙后的长激光（飞行中，循环），4 帧

装了附加包时，W 打到墙后变成一道飞出去的长激光：一段很长的光束（白芯、柠檬黄、青色的边），前端最亮、后面渐渐淡成青色（参考 W_color、W_mis_glowTrail02）。朝右飞。**上下对称**。4 帧无缝循环。约 40 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a FLYING LASER SEGMENT to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a beam 40 squares long and 7 tall (a white core 3 tall, lime-yellow, cyan edges), its front a bright rounded head, fading to cyan toward its tail; small arcs flicker along it.
Layout: one horizontal row of 4 equal 42:11 cells, image size 2688x176 (each cell 672x176, 16 px a square); the beam's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `zeri_fx_w_hit.png`：W 打中（目标身上），4 帧

W 打中：一团黄绿到青色的电爆，几道电弧往外劈（参考 W_Flash01、W_tar_Sphere）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a LASER HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a lime-yellow burst 10 squares across with a cyan rim; 3 zigzag arcs out to mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `zeri_fx_w_slow.png`：W 的减速（被减速的人脚下，循环），4 帧

被 W 减速：脚下一圈青色的电环，环上几道往中间收的短电弧（左右对称）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8) and a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C).
Effect: a CYAN SLOW RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin cyan ellipse 14 squares wide and 4 tall, four short lime arcs at mirrored places that slide toward the center each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `zeri_fx_e_cast.png`：E 灿丽花火：冲刺起步的电光（她脚下，施法时），5 帧

E 冲刺起步：脚下一圈电光炸开，两边各几道青色和黄绿色的速度线、电火花往外甩（参考 E_Dash、E_Lightning_flipbook、W_Speedline）。**左右对称**。约 44 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a DASH BURST on the ground round a figure's feet, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 10 squares wide at the feet; 2 a lime ring 24 squares wide and 8 tall with cyan streaks out to both sides; 3 the ring 36 wide, zigzag sparks thrown out at mirrored places; 4 the ring 44 wide and 16 tall, thinner; 5 fading sparks.
Layout: one horizontal row of 5 equal 46:20 cells, image size 3680x320 (each cell 736x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `zeri_fx_e_on.png`：E 生效中：步枪带电（她身上，持续 5 秒，循环），4 帧

E 之后的 5 秒普攻贯穿：她身边两侧噼啪闪着小电弧（左右对称地分布在肩、腰、膝旁边），中间留空（参考 E_Lightning_flipbook、R_Electricity_4x4）。**左右对称**。4 帧无缝循环。约 28 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: CRACKLING ARCS round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (14 x 36 squares, its bottom on the cell's bottom) EMPTY: short lime zigzag arcs 3-4 squares long beside the shoulders, the waist and the knees on both sides, cyan tips, small white sparks; each frame the arcs jump to the next place (keep each frame mirrored).
Layout: one horizontal row of 4 equal 30:42 cells, image size 1920x672 (each cell 480x672, 16 px a square); centered across, the figure area's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `zeri_fx_e_shot.png`：E 生效时的贯穿弹（飞行中，循环），4 帧

E 的贯穿弹：一道细长锋利的电弹（白芯、青色），后面拖一条长的黄绿色光尾，前端一个小尖（参考 ER_MissileHead、Bullet_Front）。朝右飞。**上下对称**。4 帧无缝循环。约 18 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8) and a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C).
Effect: a PIERCING ROUND flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a sharp slug 5 squares long and 2 tall at the right (a white core, cyan edges), a thin lime trail 13 squares long behind it, a tiny white tip; the trail flickers.
Layout: one horizontal row of 4 equal 20:6 cells, image size 1280x96 (each cell 320x96, 16 px a square); the tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `zeri_fx_e_hit.png`：贯穿弹打中（目标身上），4 帧

贯穿弹打中：一小团青色带黄绿芯的电火花，几根细电光往两边跳（左右对称）。**左右对称**。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8) and a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C).
Effect: a PIERCE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a cyan burst 8 squares across with a lime core; 3 thin sparks out to both sides; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `zeri_fx_r_nova.png`：R 超限爆闪：以她为中心的电新星（地上，施法时），6 帧

R：以她为中心炸开一圈巨大的电新星：一圈黄绿色的电光环从脚下往外扩到 150 格宽，环上有锯齿状的电弧和一点彩虹色的边，中心一下白光（参考 Shockwave01_Color、R_RainbowGlow、R_Electricity_4x4、R_Ray）。这是技能的范围（半径 75 格），从斜上方看的扁椭圆。**上下左右都对称**。约 150 格宽、60 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C), a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8) and a rainbow fringe (#FF8CF0, #B080FF, #FFB040, only as thin edges).
Effect: a HUGE LIGHTNING NOVA on the ground round a figure, seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 a white-yellow flash 20 squares wide at the center; 2 a bright lime ring 60 squares wide and 24 tall with jagged arcs on it; 3 the ring 100 wide, cyan edges, a thin rainbow fringe outside; 4 the ring 140 wide; 5 the ring 150 wide and 60 tall, thinner, arcs flickering on it; 6 fading sparks along the ellipse.
Layout: one horizontal row of 6 equal 152:62 cells, image size 14592x992 (each cell 2432x992, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `zeri_fx_r_on.png`：R 超载中（她身上，持续 5 秒，循环），4 帧

超载 5 秒：她全身绕着明亮的电光（左右两侧各几道长的锯齿电弧从脚到头，外面一点彩虹色的边），头顶偶尔一下亮光，中间留空（参考 R_Electricity_4x4、R_ChainLightning01、R_RainbowGlow）。**左右对称**。4 帧无缝循环。约 34 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C), a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8) and a rainbow fringe (#FF8CF0, #B080FF, #FFB040, only as thin edges).
Effect: an OVERCHARGE AURA round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (14 x 36 squares, its bottom on the cell's bottom) EMPTY: on each side two long jagged lightning arcs from the feet to above the head (lime-yellow, white cores, cyan edges, a thin rainbow fringe), small sparks; the arcs change shape every frame (keep each frame mirrored); frame 3 a small white star above the head.
Layout: one horizontal row of 4 equal 36:50 cells, image size 2304x800 (each cell 576x800, 16 px a square); centered across, the figure area's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `zeri_fx_r_st2.png`：R 超载被延长（她身上，循环），4 帧

超载被命中英雄延长时：和超载一样的电光，但弱一些（两侧各一道电弧、没有头顶的亮光），表示快结束了。**左右对称**。4 帧无缝循环。约 34 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a FADING OVERCHARGE round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (14 x 36 squares, its bottom on the cell's bottom) EMPTY: on each side one jagged lightning arc from the hip to the shoulder (lime-yellow, white core, cyan edges), dimmer than a full aura, a few sparks; the arcs change shape every frame (keep each frame mirrored).
Layout: one horizontal row of 4 equal 36:50 cells, image size 2304x800 (each cell 576x800, 16 px a square); centered across, the figure area's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `zeri_fx_r_shot.png`：R 超载时的三连发（飞行中，循环），4 帧

超载时普攻变成三连发：三道平行的电弹线（中间一道最亮最长，上下两道短一点），白芯、柠檬黄、青色的尖（参考 R_MissileHead01、Q_MissileHead01）。朝右飞。**上下对称**。4 帧无缝循环。约 18 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: THREE PARALLEL ELECTRIC ROUNDS flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a middle round 16 squares long and 2 tall (a white core, lime-yellow, a cyan tip) and two rounds 12 long and 1-2 tall 3 squares above and below it, mirrored; small sparks between them flicker.
Layout: one horizontal row of 4 equal 20:11 cells, image size 1280x176 (each cell 320x176, 16 px a square); the middle round's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `zeri_fx_r_hit.png`：R 电新星打中（目标身上），5 帧

电新星打中：一团明亮的电爆（白芯、柠檬黄、青色的边、一点彩虹色），几道锯齿电弧往外劈（参考 Hit02_vertical、R_RainbowGlow）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C), a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8) and a rainbow fringe (#FF8CF0, #B080FF, #FFB040, only as thin edges).
Effect: a NOVA HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a lime-yellow burst 12 squares across with cyan edges; 3 jagged bolts to mirrored places, a thin rainbow fringe; 4 sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `zeri_fx_r_zap.png`：R 连锁闪电打中（每个被连锁的人身上），4 帧

三连发打中后的连锁闪电：一道闪电从上方劈到这个人身上（两股对称的锯齿电光从格子顶部往下汇到身体中间），落点一下电火花（参考 R_ChainLightning01、Hit01_vertical）。**左右对称**。约 14 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bolts, sparks, beams or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime electricity ramp (#FFFFFF, #FFFFC8, #F4FF50, #C4F024, #72CC14, #2E7E0C) and a cyan ramp (#FFFFFF, #D8FFFF, #7CF0FF, #24BCF0, #1270B8).
Effect: a CHAIN LIGHTNING STRIKE on a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two mirrored zigzag bolts from the cell's top corners meeting at the cell's middle (white cores, lime-yellow, cyan edges); 2 the bolts brightest, a white-yellow burst 6 squares across where they meet; 3 the bolts breaking up, sparks; 4 fading sparks at the middle.
Layout: one horizontal row of 4 equal 16:32 cells, image size 1024x512 (each cell 256x512, 16 px a square); centered across, the meeting point on the cell's middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `zeri_fx_a_burst` | view_projectiles `league_zeri_a_burst`（直线弹，朝飞行方向转，画成朝右飞；上下对称） | 18 × 3 |
| `zeri_fx_a_hit` | view_effects `league_zeri_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `zeri_fx_p_spark` | view_projectiles `league_zeri_p_spark`（追踪弹，朝飞行方向转；上下对称） | 12 × 9 |
| `zeri_fx_p_hit` | view_effects `league_zeri_p_hit`（跟随；左右对称） | 16 |
| `zeri_fx_p_ready` | view_effects `league_zeri_p_ready`（跟随她，画在人物上面；左右对称；中间留空） | 30 × 42 |
| `zeri_fx_p_shv` | view_buffs `league_zeri_p_shv`（画在人物上面；左右对称；只画外圈，中间留空） | 30 × 44 |
| `zeri_fx_p_slow` | view_buffs `league_zeri_p_slow`（画在脚下；左右对称） | 14 × 5 |
| `zeri_fx_p_haste` | view_buffs `league_zeri_p_haste`（画在脚下；左右对称） | 18 × 6 |
| `zeri_fx_w_cast` | view_effects `league_zeri_w_cast`（施法时跟随她，画在人物上面；左右对称；中间留空） | 30 × 40 |
| `zeri_fx_w_pulse` | view_projectiles `league_zeri_w_pulse`（直线弹，朝飞行方向转；上下对称） | 16 × 7 |
| `zeri_fx_w_laser` | view_projectiles `league_zeri_w_laser`（线的画面：以脉冲停下的点为中心、朝泽丽→那一点的方向转；**画在格子右半边**；上下对称） | 200 × 13 |
| `zeri_fx_w_wall` | view_projectiles `league_zeri_w_wall`（附加包生成的直线弹，朝飞行方向转；上下对称） | 40 × 9 |
| `zeri_fx_w_hit` | view_effects `league_zeri_w_hit`（跟随；左右对称） | 14 |
| `zeri_fx_w_slow` | view_buffs `league_zeri_w_slow`（画在脚下；左右对称） | 16 × 6 |
| `zeri_fx_e_cast` | view_effects `league_zeri_e_cast`（跟随她，画在人物下面；左右对称） | 44 × 18 |
| `zeri_fx_e_on` | view_buffs `league_zeri_e_on`（画在人物上面；左右对称；中间留空） | 28 × 40 |
| `zeri_fx_e_shot` | view_projectiles `league_zeri_e_shot`（直线弹，朝飞行方向转；上下对称） | 18 × 4 |
| `zeri_fx_e_hit` | view_effects `league_zeri_e_hit`（跟随；左右对称） | 10 |
| `zeri_fx_r_nova` | view_effects `league_zeri_r_nova`（跟随她，画在人物下面；上下左右都对称） | 150 × 60 |
| `zeri_fx_r_on` | view_buffs `league_zeri_r_on`（画在人物上面；左右对称；中间留空） | 34 × 48 |
| `zeri_fx_r_st2` | view_buffs `league_zeri_r_st2`（画在人物上面；左右对称；中间留空） | 34 × 48 |
| `zeri_fx_r_shot` | view_projectiles `league_zeri_r_shot`（直线弹，朝飞行方向转；上下对称） | 18 × 9 |
| `zeri_fx_r_hit` | view_effects `league_zeri_r_hit`（跟随；左右对称） | 16 |
| `zeri_fx_r_zap` | view_effects `league_zeri_r_zap`（跟随；左右对称） | 14 × 30 |

- 子弹、电击弹、贯穿弹、三连发、电脉冲从平端步枪的枪口出（出手帧枪口在站位点前 25–26 格、脚底上 17–18 格）；`a_y` 按这个量（太高的直线弹会斜：最多抬到 13 格左右），画面开头补空帧走过枪口前的距离（追踪弹第一 tick 朝上）。
- `w_laser`：线的画面在脉冲停下的点、朝泽丽→那一点转（champion-data section 6）；按 204 格宽切格，确认左半边是空的、上下对称。`w_wall` 是附加包生成的直线弹（league_zeri:laser 效果），朝飞行方向转。
- `r_nova`：R 的出手 tick 跟随她播放（画在人物下面，z -1），上下左右逐格对称；`p_ready`、`w_cast`、`e_cast` 也跟随她、逐格左右对称；`e_on` 300 tick、`r_on` 300 tick、`r_st2` 最多 150 tick、`p_shv` 180 tick 循环。
- 用 `pixel_1x/` 切格（import_syndra 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
