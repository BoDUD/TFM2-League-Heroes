# 奥术先驱 维克托：给 Codex 的特效提示词（第 3 步）

> **这一份是 23 张特效图。** 造型和动作已定（`design/viktor_design.png`，8 倍，42 行、30 格宽）。
> - 大小对照 `design/viktor_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。维克托 30×42 格。每条写的大小都是游戏像素（格）。
> - `design/viktor_shots.png`：定稿动作（4 倍），青色十字是特效的起点（伸出去的手、法杖头、脚下），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里维克托自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**他的奥术光是蓝紫色（机械臂、重力场、风暴），海克斯光是金橙色带白芯（Q、射线），Q 的护盾和机械臂的光核是青色**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见；风暴云可以用一点深紫，但边缘要亮。
> - **围着人的光环、护盾泡泡、风暴、进化光只画外圈和两边，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：飞出去的光弹（`a_bolt`、`a_blast`、`q_bolt`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。射线 `e_ray`、余波 `e_after` 是**线的画面**：游戏把整张图的**中心**放在目标脚下、朝「维克托→目标」的方向转，所以**光束只画在格子右半边、从正中间往右扫**，同样**上下对称**。画在人身上、脚下的（打中、晕眩、减速、护盾、强化光点、风暴、进化）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；地上的 `w_field`、`w_burst`、`r_land` 上下左右都对称。
> - 特效照下面第 1–23 条和「所有特效图的规则」画，每张一个 PNG，文件名 `viktor_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。
> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`viktor_fx_done.zip`）放在 outputs 里，或放在 `outputs/viktor-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「光荣进化」 | 奥术光弹普攻；按等级依次升级 E、Q、W、R（升级时身上亮金光） | `a_bolt` · `a_hit` · `evo` · `evo_slow` |
| 技能 1 = Q「虹吸能量」 | 法杖射出海克斯光弹，打中得到护盾；4 秒内下一次普攻强化；升级后护盾更强并加速 | `q_bolt` · `q_hit` · `q_shield` · `q_charged` · `q_ms` · `a_blast` · `a_blast_hit` |
| 技能 2 = W「重力场」→ E「海克斯射线」 | 敌方英雄脚下放重力场：减速，1.25 秒后场内的人被晕；接着从目标处往外扫一道射线；升级后射线 1 秒后有余波 | `w_field` · `w_slow` · `w_burst` · `w_stun` · `e_ray` · `e_hit` · `e_after` · `e_after_hit` |
| 大招 = R「奥术风暴」 | 风暴落在敌方英雄身上、跟着他走，每秒打一下；目标阵亡就转到附近英雄；升级后风暴变大 | `r_land` · `r_storm` · `r_storm_big` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、射线、闪电、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀（风暴云可以多用一点）。
- 颜色（按每条写的用）：
  - 蓝紫奥术光（普攻、重力场、风暴、闪电）：`#FFFFFF`、`#E8E0FF`、`#B9A4FF`、`#7E62F0`、`#4A34B8`；
  - 青色海克斯光（光核、Q 护盾、电弧）：`#FFFFFF`、`#D8FBFF`、`#8AEFFF`、`#30C8F0`、`#1878B8`；
  - 金橙海克斯光（Q、射线、余波、进化）：`#FFFFFF`、`#FFF6C0`、`#FFE68A`、`#FCC23A`、`#E07A1C`；
  - 风暴深紫（风暴云）：`#FFFFFF`、`#D8D0FF`、`#8C7CF0`、`#4A3CB0`、`#241A60`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（23 张）

23 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，重力场半径 30000，射线长 70000，风暴半径 30000（升级后 38000））。

### 1. `viktor_fx_a_bolt.png`：普攻：飞出去的奥术光弹（飞行中，循环），4 帧

维克托的普攻：一颗蓝紫色的小光弹，前面一颗白芯，后面拖一小段蓝紫光尾（参考 BA_Muzzle、BA_Trail、BA_GlowAlpha）。朝右飞。**上下对称**。4 帧无缝循环。约 8 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8).
Effect: an ARCANE BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a white core 2 squares across at the right, a violet glow round it, a short tapering violet trail 5 squares long behind it to the left; the trail flickers frame to frame.
Layout: one horizontal row of 4 equal 10:6 cells, image size 640x96 (each cell 160x96, 16 px a square); the bolt's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `viktor_fx_a_blast.png`：Q 强化后的普攻：更大的金色海克斯光弹（飞行中，循环），4 帧

虹吸能量强化的下一次普攻：一颗更大的金白色光弹，外面一圈细的青色电弧，后面拖金色光尾（参考 Q_Sphere、Q_mis_glowTrail02、Q_ElecAnim）。朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a CHARGED HEXTECH BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a bright white-gold orb 4 squares across at the right, a thin cyan electric arc crackling round it, a gold trail 6 squares long behind it; the arcs jump to mirrored places each frame.
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `viktor_fx_a_hit.png`：普攻打中（目标身上），4 帧

普攻打中：一朵蓝紫色的小星光炸开（参考 Flash、Hit_Spark_blue）。**左右对称**。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8).
Effect: an ARCANE SPARK HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet 4-point star 5 squares across; 2 a violet burst 7 squares across; 3 four sparks flying out diagonally; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `viktor_fx_a_blast_hit.png`：强化普攻打中，5 帧

强化普攻打中：一团金白色的海克斯光炸开，一圈青色电弧往外扩（参考 Q_Buf_Hit_Burst、Q_Impact_Cross）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a HEXTECH BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 8 squares across; 2 a gold cross-shaped burst 12 squares across; 3 a thin cyan ring 14 squares across with small electric arcs; 4 the ring wider and fading, sparks; 5 a few fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `viktor_fx_q_bolt.png`：Q 虹吸能量：法杖射出的海克斯光弹（飞行中，循环），4 帧

Q 的光弹：一颗金白色的海克斯光球，外面一圈青色的六边形光环，后面拖一道金色光尾（参考 Q_Missile_Head、Q_HextechRing04、Q_mis_glowTrail02）。朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a HEXTECH MISSILE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a bright white-gold orb 4 squares across inside a thin cyan hexagon ring 7 squares across, a gold trail 6 squares long behind it; the ring brightens and dims frame to frame (no spinning).
Layout: one horizontal row of 4 equal 14:10 cells, image size 896x160 (each cell 224x160, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `viktor_fx_q_hit.png`：Q 打中（目标身上），4 帧

Q 打中：金白色的星光炸开，一圈六边形的青色光环往外扩（参考 Q_Ring、Q_Flares_03）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a HEXTECH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold star 7 squares across; 2 a gold burst 10 squares across inside a thin cyan hexagon outline 12 squares across; 3 the hexagon wider and thinner, sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `viktor_fx_q_shield.png`：Q 护盾：打中后他身上亮起的护盾（他身上），5 帧

Q 打中后维克托得到护盾：他身上亮起一层青白色的六边形能量泡（只画外圈，中间留空），从下往上亮起再淡下去（参考 Q_template_shield、Q_shield_Mult、Shield_gradient）。**左右对称**。约 26 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a HEXTECH SHIELD BUBBLE round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY: an upright ellipse outline 24 squares wide and 32 tall made of small cyan hexagon segments, 1 the bottom third lit; 2 the whole outline lit, white highlights at the top; 3 brightest, a few hexagons flashing white; 4 dimmer; 5 fading to a few segments.
Layout: one horizontal row of 5 equal 28:36 cells, image size 2240x576 (each cell 448x576, 16 px a square); the bubble centered in every cell, its bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `viktor_fx_q_charged.png`：Q 强化普攻就绪（他身上，循环），4 帧

Q 之后下一次普攻会强化：维克托身边绕着两颗金色的小光点（左右对称地上下浮动，中间留空，不挡人）（参考 idle_BightSpark、Glow5）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C).
Effect: TWO HEXTECH SPARKS floating round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: two small white-gold glowing sparks (3 squares across, a 1-square white core) at mirrored places beside the figure's waist, rising and falling 2 squares together.
Layout: one horizontal row of 4 equal 28:36 cells, image size 1792x576 (each cell 448x576, 16 px a square); the figure area is the middle 16 x 32 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `viktor_fx_q_ms.png`：Q 升级后的加速（脚下，循环），4 帧

Q 升级后的移速：脚下一圈细的青色光环，两边各几道往后的短光线（左右对称）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a SPEED RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin cyan ellipse 16 squares wide and 4 tall, 2 short horizontal light dashes on each side at mirrored places; the dashes slide outward each frame.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `viktor_fx_w_field.png`：W 重力场：地上的引力场（地上，画在人物下面，持续 4 秒），10 帧

重力场：地上一个从斜上方看的扁椭圆引力场，外圈一道蓝紫色光环，里面几圈细的同心环慢慢往中间收，中间一颗发光的小核（参考 W_Circle_normal、W_Pulses、W_TrampleAOE_Glow、W_LightBeam）。**上下左右都对称**。这是技能的范围（半径 30 格），约 64 格宽、26 格高。帧 1–2 展开，3–8 循环收缩（引力往里吸），9–10 淡出。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a GRAVITY FIELD on the ground seen from above at an angle, 10 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: an elliptical field 60 squares wide and 24 tall: a bright violet outer ring 2 squares thick, 3 thin inner violet rings, a small glowing white-cyan core at the center; 1-2 the field opening from the center to full size; 3-8 the inner rings stepping inward toward the core one ring per frame (a pull), the outer ring pulsing; 9-10 fading out.
Layout: one horizontal row of 10 equal 64:28 cells, image size 10240x448 (each cell 1024x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `viktor_fx_w_burst.png`：W 晕眩爆发：力场里的人被晕的那一下（地上），5 帧

1.25 秒后力场爆发晕眩：整个椭圆一下子亮起，从中心往外炸开一圈亮紫白色的冲击波（参考 Shockwave_SpaceNoise、W_SetShine01）。**上下左右都对称**。约 64 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a GRAVITY BURST on the ground seen from above at an angle, 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 the whole ellipse (60 x 24 squares) flashes white-violet; 2 a bright shockwave ring 2 squares thick racing out from the center, 30 squares wide; 3 the ring 50 wide; 4 the ring 60 wide and thin; 5 fading sparks.
Layout: one horizontal row of 5 equal 64:28 cells, image size 5120x448 (each cell 1024x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `viktor_fx_w_stun.png`：W 晕眩（被晕的人头顶，循环），4 帧

被重力场晕住：头顶一圈扁扁的蓝紫色引力环，环上几颗小光点在转（参考 Viktor_Base_Ringlight、W_Aug_ElecNoise）。**左右对称**。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8).
Effect: a GRAVITY HALO over a head, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat violet ellipse 16 squares wide and 5 tall, 4 small white-violet dots on it at mirrored places that step round the ring each frame (keep each frame mirrored), a faint glow inside.
Layout: one horizontal row of 4 equal 20:10 cells, image size 1280x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `viktor_fx_w_slow.png`：W 减速（被减速的人脚下，循环），4 帧

被重力场减速：脚下一圈蓝紫色的细光环，环里有往中间收的短线（左右对称）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8).
Effect: a SLOWING RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin violet ellipse 14 squares wide and 4 tall, 4 short inward ticks at mirrored places that slide toward the center each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `viktor_fx_evo_slow.png`：进化后技能附带的减速（被减速的人脚下，循环），4 帧

升级后技能附带的减速：脚下一圈细的金色光环，两边各一个小光点（左右对称）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C).
Effect: a GOLD SLOW RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin gold ellipse 12 squares wide and 3 tall with a small white-gold spark on each side at mirrored places, brightening and dimming.
Layout: one horizontal row of 4 equal 16:7 cells, image size 1024x112 (each cell 256x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `viktor_fx_e_ray.png`：E 海克斯射线：从目标处往外扫的光束（地上的线，朝方向转），6 帧

海克斯射线：从落点（格子正中）往右射出一道 70 格长的光束，白色的芯、金橙色的光、边上一点蓝紫，光束从起点往右「扫」出去，第 3 帧扫满，然后淡出（参考 E_Trail_55、E_Trench、E_Flare、Beamhead_Centre）。**整张图左半边是空的**（游戏把这张图的中心放在目标脚下，往外扫）。**上下对称**。光束起点处窄（约 4 格高），越往外越宽（末端约 10 格高）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C) and an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8).
Effect: a HEXTECH RAY sweeping to the RIGHT from the cell's CENTER, 6 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): the LEFT HALF of every cell stays EMPTY; the beam starts exactly at the cell's center and reaches right: a white core 2 squares tall, a gold-orange glow round it, thin violet edges, 4 squares tall at the start widening to 10 squares at its end, a bright gold-white flare at its tip; 1 the beam 20 squares long; 2 50 long; 3 the full 70 squares, brightest; 4 the full beam; 5 the beam thinner, breaking into sparks; 6 fading sparks along the line.
Layout: one horizontal row of 6 equal 144:28 cells, image size 13824x448 (each cell 2304x448, 16 px a square); the beam's start on the cell's exact center column, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `viktor_fx_e_after.png`：E 升级的余波：沿射线路径的一串爆炸（地上的线，朝方向转），6 帧

余波：射线 1 秒后沿同一条路径炸开一串金橙色的小爆炸，从起点往外依次炸开（参考 Foundation_ImpactSpike、Ground_Trail、E_ErosionShapes）。**整张图左半边是空的**，**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C) and an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8).
Effect: an AFTERSHOCK along a line to the RIGHT from the cell's CENTER, 6 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): the LEFT HALF of every cell stays EMPTY; along a 70-square line from the center to the right, a chain of round gold-orange blasts 8 squares across (white cores, violet sparks) bursting one after another from the start outward: 1 two blasts near the start; 2 four blasts to 30 squares; 3 six blasts to 50; 4 the whole line of blasts to 70, brightest; 5 the blasts shrinking into sparks; 6 fading sparks.
Layout: one horizontal row of 6 equal 144:28 cells, image size 13824x448 (each cell 2304x448, 16 px a square); the line's start on the cell's exact center column, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `viktor_fx_e_hit.png`：E 打中（每个被射线打中的人身上），4 帧

被射线打中：人身上一团金白色的灼烧光，几颗金色火星往上飞（参考 E_Flare、Ember_Sharp）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C).
Effect: a RAY BURN HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 6 squares across; 2 a gold-orange burst 10 squares across; 3 embers rising at mirrored places; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `viktor_fx_e_after_hit.png`：E 余波打中，4 帧

被余波打中：一团更大的金橙色爆炸，带蓝紫色的火花（参考 Foundation_ImpactSpike、Paint_Sparks）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C) and an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8).
Effect: an AFTERSHOCK BLAST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 8 squares across; 2 a round gold-orange blast 12 squares across with violet sparks; 3 the blast breaking up; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `viktor_fx_r_land.png`：R 奥术风暴落下的爆发（地上），6 帧

风暴落下：地上一圈从斜上方看的扁椭圆，蓝紫色的冲击波从中间炸开，环上有海克斯符文的光点（参考 R_RadiusRing_Glows、R_HextechRing02、R_ground_glow、R_Runes）。**上下左右都对称**。这是风暴的范围（半径 30 格），约 64 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: an ARCANE STORM IMPACT on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 a white-violet flash 14 squares wide at the center; 2 a violet ring 30 squares wide with small cyan rune dots on it; 3 the ring 46 wide, the inside glowing; 4 the ring 60 wide and 24 tall; 5 the ring thinner, sparks; 6 fading sparks.
Layout: one horizontal row of 6 equal 64:28 cells, image size 6144x448 (each cell 1024x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `viktor_fx_r_storm.png`：R 奥术风暴：跟着英雄走的风暴（他身上，每秒播一次），6 帧

奥术风暴：英雄头顶一团旋转的蓝紫色风暴云，几道白紫色的闪电往下劈到他脚边，脚下一圈扁椭圆的紫色光环（参考 R_Stormwall_02、R_Bolts、R_beam_Bolts、R_Proc_Lightning、R_Glow_Edge）。**中间人站的位置留空、不画实心的东西**（闪电只在两边），**左右对称**（旋涡用对称的形状表现，不画朝一个方向转）。6 帧连起来 1 秒，循环播放。约 60 格宽、56 格高（风暴云在上，光环在下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a storm violet ramp (#FFFFFF, #D8D0FF, #8C7CF0, #4A3CB0, #241A60), an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: an ARCANE STORM over a figure, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle EMPTY: at the top a swirling storm cloud 40 squares wide and 12 tall (dark violet with brighter violet and white edges, its swirl drawn as a symmetric spiral pattern, no one-way spin), at the bottom a flat violet ring 56 squares wide and 20 tall on the ground; two jagged white-violet lightning bolts striking down from the cloud to the ring at mirrored places LEFT and RIGHT of the figure (never through the middle); each frame the bolts and the cloud's bright edges change (keep every frame mirrored).
Layout: one horizontal row of 6 equal 62:58 cells, image size 5952x928 (each cell 992x928, 16 px a square); the ring's bottom on the cell's bottom, centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `viktor_fx_r_storm_big.png`：R 升级后变大的风暴（他身上，每秒播一次），6 帧

同 r_storm，但更大更亮（范围半径 38 格）：风暴云更宽、闪电三道（两边各一道 + 背后一道细的往两边分叉），光环约 76 格宽。**中间留空，左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a storm violet ramp (#FFFFFF, #D8D0FF, #8C7CF0, #4A3CB0, #241A60), an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a GREATER ARCANE STORM over a figure, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle EMPTY: as a storm cloud 52 squares wide and 14 tall at the top, a flat violet ring 72 squares wide and 26 tall at the bottom, lightning bolts striking down at mirrored places left and right of the figure (two on each side), brighter cyan sparks on the ring; each frame changes, every frame mirrored.
Layout: one horizontal row of 6 equal 78:66 cells, image size 7488x1056 (each cell 1248x1056, 16 px a square); the ring's bottom on the cell's bottom, centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `viktor_fx_r_hit.png`：R 风暴每秒打中（每个被打中的人身上），4 帧

被风暴打中：一道细的白紫色闪电从上往下劈到人身上，落点炸开一小圈紫色火花（参考 R_hit_sparks、R_Proc_Lightning）。**左右对称**（闪电竖直居中）。约 12 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an arcane violet ramp (#FFFFFF, #E8E0FF, #B9A4FF, #7E62F0, #4A34B8) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a LIGHTNING STRIKE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin white-violet lightning bolt striking straight down the middle, 16 squares tall, its zigzag mirrored; 2 the bolt brightest, a violet spark burst 8 squares across at its foot; 3 the bolt gone, sparks flying out at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal 14:20 cells, image size 896x320 (each cell 224x320, 16 px a square); the burst at the bottom-center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `viktor_fx_evo.png`：光荣进化：升级技能时他身上的海克斯光（他身上），6 帧

光荣进化升级一个技能：他脚下亮起一圈金色的海克斯光环往上升，几道金色光线往上射，身边飘起金色和青色的小光点（只画外圈和光线，中间留空）（参考 Star_Rays、Stardust、Skin18_Add_Gold、Ringlight）。**左右对称**。约 30 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, beams, sparks or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #E07A1C) and a hextech cyan ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a HEXTECH EVOLUTION round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: 1 a gold ellipse ring 24 squares wide and 6 tall at the feet; 2 the ring rising to the waist, 4 thin vertical gold light rays at mirrored places; 3 the ring at the chest, the rays tallest, small gold and cyan sparks rising; 4 the ring at the head, bright; 5 the ring above the head, fading, sparks; 6 fading sparks.
Layout: one horizontal row of 6 equal 32:46 cells, image size 3072x736 (each cell 512x736, 16 px a square); centered across, the feet ring on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `viktor_fx_a_bolt` | view_projectiles `league_viktor_a_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 8 × 5 |
| `viktor_fx_a_blast` | view_projectiles `league_viktor_a_blast`（同上；上下对称） | 12 × 8 |
| `viktor_fx_a_hit` | view_effects `league_viktor_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `viktor_fx_a_blast_hit` | view_effects `league_viktor_a_blast_hit`（跟随；左右对称） | 16 |
| `viktor_fx_q_bolt` | view_projectiles `league_viktor_q_bolt`（朝飞行方向转；上下对称） | 12 × 8 |
| `viktor_fx_q_hit` | view_effects `league_viktor_q_hit`（跟随；左右对称） | 14 |
| `viktor_fx_q_shield` | view_effects `league_viktor_q_shield`（施法后，不跟随，画在人物上面；左右对称） | 26 × 34 |
| `viktor_fx_q_charged` | view_buffs `league_viktor_q_buff`（跟随；左右对称） | 26 × 34 |
| `viktor_fx_q_ms` | view_buffs `league_viktor_q_ms`（画在脚下；左右对称） | 18 × 6 |
| `viktor_fx_w_field` | view_effects `league_viktor_w_field`（落点上，不旋转，画在人物下面；上下左右都对称） | 64 × 26 |
| `viktor_fx_w_burst` | view_effects `league_viktor_w_burst`（落点上，不旋转，画在人物下面；上下左右都对称） | 64 × 26 |
| `viktor_fx_w_stun` | view_effects `league_viktor_w_stun`（跟随；左右对称） | 18 × 8 |
| `viktor_fx_w_slow` | view_buffs `league_viktor_w_slow`（画在脚下；左右对称） | 16 × 6 |
| `viktor_fx_evo_slow` | view_buffs `league_viktor_evo_slow`（画在脚下；左右对称） | 14 × 5 |
| `viktor_fx_e_ray` | view_projectiles `league_viktor_e_ray`（线的画面：以落点为中心、朝维克托→落点的方向转；**画在格子右半边**；上下对称） | 140 × 26 |
| `viktor_fx_e_after` | view_projectiles `league_viktor_e_after`（同 e_ray：格子右半边、上下对称） | 140 × 26 |
| `viktor_fx_e_hit` | view_effects `league_viktor_e_hit`（跟随；左右对称） | 12 |
| `viktor_fx_e_after_hit` | view_effects `league_viktor_e_after_hit`（跟随；左右对称） | 14 |
| `viktor_fx_r_land` | view_effects `league_viktor_r_land`（落点上，不旋转，画在人物下面；上下左右都对称） | 64 × 26 |
| `viktor_fx_r_storm` | view_effects `league_viktor_r_storm`（跟随英雄，画在人物上面；左右对称） | 60 × 56 |
| `viktor_fx_r_storm_big` | view_effects `league_viktor_r_storm_big`（同上；左右对称） | 76 × 64 |
| `viktor_fx_r_hit` | view_effects `league_viktor_r_hit`（跟随；左右对称） | 12 × 18 |
| `viktor_fx_evo` | view_effects `league_viktor_evo`（施法后，不跟随，画在人物上面；左右对称） | 30 × 44 |

- 光弹从远侧手（普攻，出手帧手在站位点前 18 格、脚底上 18 格）和法杖头（Q）出；`bolt_y` 不超过约 8 格（太高的弹道会斜），画面开头补一帧空的（追踪弹第一 tick 朝上）。
- `e_ray` / `e_after`：线的画面在落点、朝施法者→落点转（champion-data section 6；hit = DirDot 锥形）；按 140 格宽切格，确认左半边是空的、上下对称。
- 没有烘进动作帧的特效：`q_shield`、`evo` 晚于第一 tick，`is_follow` 为 false，逐格左右对称；`w_field`、`w_burst`、`r_land` 画在人物下面（z -2 / -1）；`r_storm` 每秒一次，帧长合计约 1 秒。
- 用 `pixel_1x/` 切格（import_twitch / import_seraphine 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单（`q_charged` 的文件绑定 view_buffs 的 `q_buff`）。
