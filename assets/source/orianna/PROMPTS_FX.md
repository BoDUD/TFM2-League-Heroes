# 发条魔灵 奥莉安娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张图：她的球（3 张）和技能特效。** 造型和动作已定（`design/orianna_idle.png`：3/4 正面朝右，金色短发和发髻、瓷白的脸、青绿眼睛、银色胸甲、金色齿轮裙、分节金属四肢）。她在游戏里是**高清**的（每个游戏格子里 2.2×2.2 个细像素），38 格高、21 格宽；**特效和球照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - **球**是她的武器，游戏里是单独的一张图，会出现在三个地方：漂在她（或被 E 送到的队友）身边、Q 扔出去后停在地上、飞来飞去。三张球的图都照 `design/orianna_ball.png`（你第 1 步画的第 2 稿球，8 倍放大）画，**直径 10 格**，银色金属球、两道铜金色环、顶上金脊、淡紫色小窗格，**球是实物，保留一圈近黑描边**。
> - 大小对照 `design/orianna_size.png`：她的待机放大 4 倍，脚底在红线上，黄线是脚下中点（她的站位点），**青色圈是球漂在她身边的位置**（脚下中点右边 12 格、离地 20 格），上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/orianna_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里奥莉安娜自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**球的能量是蓝白色的电光（白芯、青色到深蓝）**，**符文圈和齿轮是发条金色**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈，中间身体位置留空**，要淡一点，不要盖住人。
> - **方向（重要，红色方不会镜像）**：飞出去的 `ball_fly`、`a_bolt` 画成朝右，**上下对称**（往左时会上下翻；球自己的花纹可以照原样）。`ball_side`、`b_home_in` 的球在人物右边（这两张不对称，游戏里红色方时球会漂在她身后，没关系）。其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `orianna_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `orianna_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「发条协奏」 | 手一挥射出发条电弹，连续普攻叠加魔法伤害 | `a_bolt` · `a_hit` |
| 球 | 漂在她身边；Q 扔出去停在地上；E 送到队友身上；离太远或停太久会飞回来 | `ball_side` · `ball_ground` · `ball_fly` · `b_home_in` |
| 技能 1 = Q「指令：攻击」+ W「指令：杂音」 | Q 把球扔到敌人脚下；球附近有敌人时 W 自动放电，敌人减速、队友加速 | `q_land` · `q_hit` · `w_ring` · `w_hit` · `w_slow` · `w_haste` |
| 技能 2 = E「指令：防卫」 | 把球送给队友（或自己），加护盾，路过的敌人受伤 | `e_shield` · `e_hit` |
| 大招「指令：冲击波」 | 球蓄力 0.5 秒后放出冲击波，把周围敌人甩向球 | `r_wave` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电弧、火星、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**（球例外：球是实物，有一圈近黑描边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 电光蓝（球的能量、电弧、冲击波）：`#FFFFFF`、`#DDFBFF`、`#93EDFF`、`#45C6F7`、`#2183DC`、`#143F8E`；
  - 发条金（符文圈、齿轮碎光）：`#FFF4C4`、`#FFD75E`、`#E7A41C`、`#A36608`；
  - 球本身：`#EDECEC`、`#ADADAF`、`#706F73`、`#323231`、`#FDE949`、`#F39D00`、`#C26700`、`#3C2003`、`#C59DF7`、`#040208`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在人物身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张图的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 落点半径 16000，W 半径 24000，R 半径 36000）。

### 1. `orianna_fx_ball_side.png`：球漂在英雄身边（跟随，循环），6 帧

球在她（或队友）身边漂着：照附图 2 的球画成 10 格大，**中心在人物脚下中点右边 12 格、离地 20 格**的地方（附图 4 里的位置），上下慢慢浮动 1 格，球面上的高光轻轻转，周围一圈很淡的蓝色电光、偶尔一两道小电弧。人物不画（格子中间留空）。**这张不左右对称**（球在右边），游戏不会镜像它。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from the Ball's own colours (#EDECEC, #ADADAF, #706F73, #323231, #FDE949, #F39D00, #C26700, #3C2003, #C59DF7, #040208) and an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: THE BALL FLOATING BESIDE A FIGURE, 6 frames, a seamless loop (an upright girl 21 squares wide and 38 tall stands in the middle, not drawn). THE BALL (image 2 shows it at 8x): a round SILVER METAL SPHERE 10 squares across with a 1-square near-black outline (the Ball is a solid object: it keeps its outline), steel-silver shades lit from the upper left, dark engraved swirls, two small pale violet window panels, TWO COPPER-GOLD BANDS round its middle and a golden curved ridge over its top; its centre 12 squares RIGHT of the figure's middle and 20 squares above the ground, bobbing up and down by 1 square (frames 1-6: 0, -1, -1, 0, +1, +1), its highlight sliding round a little; round it a faint electric blue glow 1-2 squares wide, a tiny blue arc crackling on frames 2 and 5. Nothing else in the cell.
Layout: one horizontal row of 6 equal 48:44 cells, image size 4608x704 (each cell 768x704, 16 px a square); the figure's feet (not drawn) on the cell's bottom row, its middle at column 24. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `orianna_fx_ball_ground.png`：球停在地上（不跟随，每 0.25 秒盖一次），2 帧

Q 扔出去后球停在落点：同一个球，浮在离地 5 格的地方，脚下一小块深蓝色的影子，带很淡的蓝色电光。两帧：球高一格、低一格（游戏里每 0.25 秒盖一次，两帧要能连着循环）。**左右对称**（球本身的花纹可以照原样，不用强行对称）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from the Ball's own colours (#EDECEC, #ADADAF, #706F73, #323231, #FDE949, #F39D00, #C26700, #3C2003, #C59DF7, #040208) and an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: THE BALL HOVERING OVER THE GROUND, 2 frames, a seamless loop. THE BALL (image 2 shows it at 8x): a round SILVER METAL SPHERE 10 squares across with a 1-square near-black outline (the Ball is a solid object: it keeps its outline), steel-silver shades lit from the upper left, dark engraved swirls, two small pale violet window panels, TWO COPPER-GOLD BANDS round its middle and a golden curved ridge over its top; its bottom 5 squares above the cell's bottom row (frame 2: 1 square lower); a flat dark navy shadow ellipse 8 squares wide and 2 tall on the bottom row under it; a faint electric blue glow 1 square round the Ball.
Layout: one horizontal row of 2 equal 14:18 cells, image size 448x288 (each cell 224x288, 16 px a square); the Ball centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `orianna_fx_ball_fly.png`：球飞出去（投射物，朝飞行方向转，循环），4 帧

Q 扔球、E 送球、球飞回来都用这张：球（10 格）在右边，身后拖一条蓝白色的电光尾迹，往左变细变淡，几颗电火星。**上下对称**（球的花纹可以照原样）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from the Ball's own colours (#EDECEC, #ADADAF, #706F73, #323231, #FDE949, #F39D00, #C26700, #3C2003, #C59DF7, #040208) and an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: THE BALL FLYING to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down) (the Ball's own markings may stay as they are). THE BALL (image 2 shows it at 8x): a round SILVER METAL SPHERE 10 squares across with a 1-square near-black outline (the Ball is a solid object: it keeps its outline), steel-silver shades lit from the upper left, dark engraved swirls, two small pale violet window panels, TWO COPPER-GOLD BANDS round its middle and a golden curved ridge over its top; the Ball at the RIGHT end of the cell, behind it a tapering electric blue-white trail 14 squares long, brightest next to the Ball, 2-3 small blue sparks along it at mirrored places, flickering between frames.
Layout: one horizontal row of 4 equal 26:12 cells, image size 1664x192 (each cell 416x192, 16 px a square); the Ball 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `orianna_fx_a_bolt.png`：普攻：发条电弹（投射物，朝目标飞），3 帧

她手一挥射出的小电弹：一颗蓝白色的电光小球，后面一小段电光尾巴（参考 BA_Lightning、BA_Sparks）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: a SMALL ELECTRIC BOLT flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white-cyan orb 3 squares at the right end, a thin blue crackling tail 6 squares long behind it.
Layout: one horizontal row of 3 equal 10:6 cells, image size 480x96 (each cell 160x96, 16 px a square); the orb 1 square from the RIGHT edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `orianna_fx_a_hit.png`：普攻命中（目标身上），4 帧

电弹打中：一小团蓝白色电光炸开，几道短电弧。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: a SMALL ELECTRIC HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a cyan flash 7 squares with a white core; 3 the flash 10 squares, 4 short blue arcs at mirrored places; 4 a few fading blue motes.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `orianna_fx_q_land.png`：Q 指令：攻击：球落地的电击（地上，不跟随），5 帧

球砸到落点：地上炸开一圈蓝白色的电光环（扁椭圆，直径 32 格），中间一下白色闪光，几道电弧往外跳（参考 BA_Shockwave、Z_shockWave、BA_Sparks）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: an ELECTRIC BURST on the ground, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares on the ground; 2 a flat cyan ring 18 wide and 6 tall with a bright white rim, a short burst of light rising 6 squares in the middle; 3 the ring 30 wide and 10 tall, 6 short blue arcs jumping out at mirrored places; 4 the ring 34 wide and fading; 5 the last motes.
Layout: one horizontal row of 5 equal 36:18 cells, image size 2880x288 (each cell 576x288, 16 px a square); centered across, the ring's middle 5 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `orianna_fx_q_hit.png`：Q 命中（目标身上），5 帧

球打中：一团蓝白色电光，一颗四角星光闪一下，几道电弧。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: an ELECTRIC IMPACT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a cyan burst 9 squares with a white core; 3 a four-pointed white-cyan star 14 squares across over the burst, 6 short blue arcs at mirrored places; 4 the star fading, sparks flying out; 5 fading motes.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `orianna_fx_b_home_in.png`：球回到她身边的一闪（她身边，不跟随），4 帧

球飞回来、落回她身边的那一下：在 ball_side 的球的位置（人物脚下中点右边 12 格、离地 20 格）一下蓝白色闪光和一圈小光环。人物和球都不画。**不左右对称**（在球的位置）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: a SMALL ELECTRIC SPARKLE where the floating Ball sits, 4 frames (an upright girl 21 squares wide and 38 tall stands in the middle, not drawn): centred 12 squares RIGHT of the figure's middle and 20 squares above the ground: 1 a white flash 4 squares; 2 a cyan ring 12 squares across with a white core; 3 the ring 14 squares and fading, 4 tiny sparks; 4 the last motes. No Ball, no figure.
Layout: one horizontal row of 4 equal 48:44 cells, image size 3072x704 (each cell 768x704, 16 px a square); the figure's feet (not drawn) on the cell's bottom row, its middle at column 24. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `orianna_fx_w_ring.png`：W 指令：杂音：球的电磁脉冲（地上，不跟随），6 帧

W：以球为中心炸开一个电磁场：地上一圈蓝色的电光环（扁椭圆，直径 48 格），环上是金色的发条符文圈（四个菱形尖角，参考 Orb_Rune、W_timerwheels），圈里噼啪跳着蓝白色的电弧，中间往上冲起一下蓝白色的脉冲光（参考 W_Flare、W_Shockwave、W_Gears、BA_Lightning）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E) and a clockwork gold ramp (#FFF4C4, #FFD75E, #E7A41C, #A36608).
Effect: an ELECTROMAGNETIC PULSE on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares on the ground and a short white-cyan column of light 12 squares tall rising from it; 2 a flat cyan ring 28 wide and 9 tall with a white rim, the light column brightest; 3 the ring 48 wide and 16 tall, a thin golden clockwork rune circle just inside it with four small diamond points at front, back, left and right, white-blue lightning arcs crackling between the middle and the ring at mirrored places; 4 the same, the arcs moved, the column fading; 5 the ring and the runes fading, a few arcs left; 6 the last motes on the ring.
Layout: one horizontal row of 6 equal 50:24 cells, image size 4800x384 (each cell 800x384, 16 px a square); centered across, the ring's middle 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `orianna_fx_w_hit.png`：W 命中（目标身上），4 帧

被杂音电到：目标身上一团蓝白色电光和几道往外的电弧。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: an ELECTRIC ZAP on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a cyan burst 10 squares with a white core; 3 the burst 14 squares with 6 zigzag blue arcs at mirrored places; 4 fading motes.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `orianna_fx_w_slow.png`：W 减速（敌人脚下，循环），4 帧

被杂音减速：敌人脚下一圈淡淡的蓝色电光环，几道小电弧轮流闪。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: a FAINT ELECTRIC RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin flat ellipse 14 squares wide and 4 tall in dim blue, 2 tiny white-blue arcs on it at mirrored places taking turns to flash.
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `orianna_fx_w_haste.png`：W 加速（队友脚下，循环），4 帧

被杂音加速：队友脚下一圈淡淡的亮青色光环，两边几道往后飘的青色速度线。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: a FAINT CYAN SPEED RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin flat ellipse 16 squares wide and 5 tall in pale cyan, at both ends 2 short cyan streaks rising and fading in turns.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `orianna_fx_e_shield.png`：E 指令：防卫：护盾（人物身上，跟随），6 帧

球送到身上的护盾：一层淡淡的蓝白色光罩包住人物（椭圆，宽 26、高 40），顶上一道亮的月牙形高光慢慢转，几颗小电光点在罩子上闪（参考 Shield、Ring_Smooth）。**左右对称**，中间身体位置留空（an upright girl 21 squares wide and 38 tall stands in the middle, not drawn），罩子要淡，不要盖住人。最后一帧淡出。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: a FAINT ELECTRIC SHIELD BUBBLE round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright girl 21 squares wide and 38 tall stands in the middle, not drawn): an ellipse outline 26 wide and 40 tall in pale cyan 1 square thick, a bright white crescent highlight on its top third; frames 1-5 the crescent sliding a little left and right symmetrically while 4 tiny white sparks twinkle on the bubble at mirrored places; frame 6 the bubble fading.
Layout: one horizontal row of 6 equal 28:42 cells, image size 2688x672 (each cell 448x672, 16 px a square); centered across, the figure's feet (not drawn) 1 square above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `orianna_fx_e_hit.png`：E 球路过打中的敌人（目标身上），4 帧

E 的球路过时打中：一小团蓝色电光和两道短电弧。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: a SMALL ELECTRIC HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 3 squares; 2 a cyan flash 8 squares; 3 the flash 12 squares with 4 short blue arcs at mirrored places; 4 fading motes.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `orianna_fx_r_wave.png`：R 指令：冲击波：球的蓄力和冲击波（地上，不跟随），9 帧

R：先蓄力 0.5 秒：以球的位置为中心，四周的蓝色电光和金色发条碎光旋转着往中间收（参考 R_Swirl_OuterRing、R_ballswirl、R_Streaks、R_Swipe），中间越来越亮；然后爆开：一道往上冲的蓝白色强光柱，地上一个巨大的蓝色冲击波环往外推开（扁椭圆，直径 72 格），环里是旋转的电光条纹，最后淡掉（参考 R_Shockwave_Pan、R_InvertedGlow、Z_shockWave）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E) and a clockwork gold ramp (#FFF4C4, #FFD75E, #E7A41C, #A36608).
Effect: a GATHERING VORTEX then a SHOCKWAVE, 9 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); the centre is a point 8 squares above the cell's bottom row (where the Ball hovers): 1 a faint blue swirl 40 squares wide and 14 tall round the centre on the ground, small gold clockwork sparks on it; 2 the swirl 32 wide, brighter, blue streaks curving inward at mirrored places; 3 the swirl 24 wide, a white-cyan glow 6 squares at the centre; 4 the swirl 14 wide, the glow 10 squares, brightest; 5 everything sucked into a white point 4 squares; 6 THE BLAST: a white-cyan column of light 8 squares wide rising 36 squares from the centre, a flat cyan shockwave ring 36 wide and 12 tall with a white rim on the ground; 7 the ring 60 wide and 20 tall, blue electric streaks swirling inside it, the column fading; 8 the ring 72 wide and 24 tall, fading, sparks at its rim at mirrored places; 9 the last faint arcs of the ring.
Layout: one horizontal row of 9 equal 76:44 cells, image size 10944x704 (each cell 1216x704, 16 px a square); centered across, the centre 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `orianna_fx_r_hit.png`：R 命中（目标身上），4 帧

被冲击波打中：目标身上一团大的蓝白色电光爆开，几道往外的电弧。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, lightning, rings, sparks or glow, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue ramp (#FFFFFF, #DDFBFF, #93EDFF, #45C6F7, #2183DC, #143F8E).
Effect: a BIG ELECTRIC IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a cyan burst 12 squares with a white core; 3 the burst 18 squares with 8 zigzag blue arcs at mirrored places; 4 fading motes.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `orianna_fx_ball_side` | view_buffs `league_orianna_home`（在她身上）和 `league_orianna_e_def`（挂在队友身上），tag `ball_side` | 48 × 44 |
| `orianna_fx_ball_ground` | view_effects `league_orianna_b_ground`（不跟随，地上；左右对称） | 14 × 18 |
| `orianna_fx_ball_fly` | view_projectiles `league_orianna_q_ball`、`e_ball`、`b_back`（朝飞行方向转，画成朝右飞；上下对称），tag `ball_fly` | 26 × 12 |
| `orianna_fx_a_bolt` | view_projectiles `league_orianna_a_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 10 × 6 |
| `orianna_fx_a_hit` | view_effects `league_orianna_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `orianna_fx_q_land` | view_effects `league_orianna_q_land`（不跟随，地上、人物下面；左右对称） | 34 × 16 |
| `orianna_fx_q_hit` | view_effects `league_orianna_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `orianna_fx_b_home_in` | view_effects `league_orianna_b_home_in`（在她身上，不跟随），位置和 ball_side 的球一样 | 48 × 44 |
| `orianna_fx_w_ring` | view_effects `league_orianna_w_ring`（不跟随，地上、人物下面；左右对称；大图表） | 50 × 22 |
| `orianna_fx_w_hit` | view_effects `league_orianna_w_hit`（跟随，画在人物上面；左右对称） | 14 |
| `orianna_fx_w_slow` | view_buffs `league_orianna_w_slow`（跟随，画在人物下面；左右对称） | 16 × 5 |
| `orianna_fx_w_haste` | view_buffs `league_orianna_w_haste`（跟随，画在人物下面；左右对称） | 18 × 8 |
| `orianna_fx_e_shield` | view_effects `league_orianna_e_shield`（跟随，画在人物上面；左右对称） | 28 × 42 |
| `orianna_fx_e_hit` | view_effects `league_orianna_e_hit`（跟随，画在人物上面；左右对称） | 12 |
| `orianna_fx_r_wave` | view_effects `league_orianna_r_wave`（不跟随，地上、人物下面；左右对称；大图表） | 76 × 44 |
| `orianna_fx_r_hit` | view_effects `league_orianna_r_hit`（跟随，画在人物上面；左右对称） | 18 |

- 两张表：`asset/league/effects/league_orianna_fx`（小的）和 `league_orianna_big`（w_ring、r_wave），tag = 名字；build_orianna.py 的 views 里 home 和 e_def 绑 tag `ball_side`，q_ball / e_ball / b_back 绑 tag `ball_fly`（b_ally 不再用：球挂在队友身上改为 e_def 的 view_buffs）。
- `ball_ground` 每 b_step（15 tick = 250 ms）盖一次：两帧各 125 ms；`r_wave` 的第 6 帧（冲击）要在 r_delay（30 tick = 500 ms）时出现；`e_shield` 盖满护盾 e_t（150 tick）。
- 用 `pixel_1x/` 切格（import_pantheon_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（球除外）；核对交回的张数和这份清单。
