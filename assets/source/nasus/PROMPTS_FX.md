# 沙漠死神 内瑟斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 11 张特效图。** 造型和动作已定（`design/nasus_idle.png`：3/4 正面朝右的豺狼头战士，金色头冠和大肩甲，黑褐色的毛，青绿腰布，两手握着长法杖、月牙斧刃在前面；右边是大招「死神降临」时变大的样子，眼睛和宝石发青白光）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），44 格高、连法杖 60 格宽，大招形态 59 格高；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/nasus_size.png`：他两种形态的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/nasus_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。他的普攻、Q、E 都是法杖打出去的，**特效都画在目标身上或地上，没有飞行的弹道**。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里内瑟斯自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**汲魂痛击、灵魂烈焰、枯萎是紫色的灵魂之火（白芯）**，**灵魂烈焰的地面符文是蓝紫色**，**死神降临是金黄的沙尘加紫色能量**，**减护甲是英雄联盟的金色裂盾**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。
> - **全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他和目标朝左时也是同一张图。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nasus_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/nasus_fx/` 里，再打包成 `outputs/nasus_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「吞噬灵魂」 | 月牙斧刃从上往下劈，附带生命偷取 | `a_hit` |
| 技能 1 = Q「汲魂痛击」 | 灌满灵魂的一击；用它打死单位会叠层（叠层加 Q 的伤害） | `q_hit` · `q_soul` |
| 技能 2 = E「灵魂烈焰」 | 目标脚下燃起一圈灵魂火：燃起时爆发一次，之后 5 秒里站在圈里的敌人持续受伤、护甲降低 | `e_fire` · `e_hit` · `e_shred` |
| 被动自动放的 W「枯萎」 | 让一个敌方英雄衰老：5 秒里减速、减攻速，越来越强 | `w_hit` · `w_slow` |
| 大招「死神降临」 | 变成大号，身边刮起沙暴，每半秒按最大生命扣身边敌人的血 | `r_cast` · `r_on` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火、火星、烟、沙尘、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（裂盾例外：实心的东西可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 紫色灵魂之火（Q、E 的火、W）：`#FFFFFF`、`#EBDDFF`、`#C29BFF`、`#9558F2`、`#6A2FD0`、`#3D1580`；
  - 蓝紫符文（E 的地面符文、Q 的星芒）：`#FFFFFF`、`#DCE4FF`、`#9AAEFF`、`#5A6CF2`、`#3238C0`、`#1A1A70`；
  - 金黄沙尘（死神降临）：`#FFF8DC`、`#F5DC96`、`#E0B65E`、`#B5863A`、`#7D5726`、`#4A3216`；
  - 金色光泽（斧刃的劈光、裂盾）：`#FFFFFF`、`#FFF4C8`、`#FFD86A`、`#E8A82C`、`#A86A14`、`#5C380A`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（11 张）

11 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：灵魂烈焰半径 28000，死神降临的沙暴半径 30000）。

### 1. `nasus_fx_a_hit.png`：普攻命中：月牙斧刃劈中（目标身上），4 帧

法杖的月牙斧刃从上往下劈中：一道金白色的竖劈光，劈中处横着炸开一道短冲击线（十字形），金色火星往两边飞，带一点沙尘（参考 AA_Weapon_Trail、Flare-Omnimax）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A) and a golden sand ramp (#FFF8DC, #F5DC96, #E0B65E, #B5863A, #7D5726, #4A3216).
Effect: a STAFF BLADE IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares; 2 a gold-white vertical slash streak 10 squares tall with a white core and a short horizontal impact line 8 squares wide across its middle (a cross of light); 3 the slash fading, 6 gold sparks flying out at mirrored places, small sand-coloured dust bits at the bottom; 4 fading sparks and dust.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `nasus_fx_q_hit.png`：Q 汲魂痛击命中（目标身上），5 帧

灌满灵魂之力的一击：先是一颗白色的四芒星闪光，然后紫色的灵魂之力炸开，带白芯，一圈紫色的冲击波纹往外扩（参考 Q_Cas_Activate、Q_Hit_Glow、Q_Waves）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580) and a blue-violet rune ramp (#FFFFFF, #DCE4FF, #9AAEFF, #5A6CF2, #3238C0, #1A1A70).
Effect: a SIPHONING STRIKE HIT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white four-pointed star flash (thin rays 8 squares long up, down, left and right); 2 a violet spirit burst 12 squares with a white core, the star's rays 14 squares long tinted blue-violet; 3 the burst 16 squares, short violet streaks radiating out all round like a shockwave, a darker violet ring at its edge; 4 the ring 18 squares wide and thinner, violet motes; 5 fading violet motes.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `nasus_fx_q_soul.png`：Q 击杀吸魂：灵魂被吸进他身体（他身上，跟随），6 帧

汲魂痛击打死目标、叠层的时候：两团紫色的小灵魂从左右两边飘进来，在他胸口合成一团紫白的光，被吸进身体，再往外荡一圈细光环（参考 Q_Staff_Swirl、Q_Hand_Swirl）。**左右对称**，中间身体位置留空（a jackal-headed warrior 30 squares wide and 44 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580).
Effect: a SOUL ABSORBED by a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a jackal-headed warrior 30 squares wide and 44 tall stands in the middle, not drawn): 1 two small violet soul wisps (each a teardrop flame 3 squares wide and 5 tall with a white core and a thin curling tail) at the left and right edges at chest height (14 squares under the head's top); 2 the wisps halfway in, curving; 3 the wisps at the figure's sides; 4 the wisps merged into one violet-white glow 8 squares at the chest middle; 5 the glow smaller (4 squares), a thin violet ring 24 squares wide and 8 tall pulsing out round the chest; 6 a few violet motes rising.
Layout: one horizontal row of 6 equal 40:48 cells, image size 3840x768 (each cell 640x768, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `nasus_fx_e_fire.png`：E 灵魂烈焰：地上的灵魂火圈（地上，不跟随，5 秒），8 帧（1–2 燃起、3–6 循环、7–8 熄灭）

目标脚下燃起一圈**灵魂烈焰**（从斜上方看是扁椭圆，直径 56 格）：第 1 帧一道蓝紫色的光柱从天上落下来；第 2 帧地上亮起蓝紫色的符文圈（圈里一个三叉轮形的紫色符文），紫火开始冒；第 3–6 帧是循环的燃烧（紫色的灵魂火沿着整个圈往上窜，6–10 格高，白芯，每帧火苗不一样，第 6 帧接得回第 3 帧）；第 7 帧火变矮、符文变暗；第 8 帧只剩淡淡的圈和几粒余烬（参考 E_Ground_Rune、E_Clynder_Scroll、E_Fire_Scroll、E_Energy_Beam、E_SpiritFire_ColorMap）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580) and a blue-violet rune ramp (#FFFFFF, #DCE4FF, #9AAEFF, #5A6CF2, #3238C0, #1A1A70).
Effect: SPIRIT FIRE ON THE GROUND seen from above at an angle, 8 frames (1-2 it starts, 3-6 a seamless loop of the burning, 7-8 it dies), SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin blue-violet beam of light 4 squares wide falling from the top of the cell onto the ground's middle, a white-blue flash ellipse 20 squares wide and 6 tall where it lands; 2 a rune circle on the ground: an ellipse 56 squares wide and 18 tall, a bright blue-violet ring line with a darker blue rim, a three-spoked violet rune inside it (like a wheel), the first violet flames 4 squares tall rising along the ring; 3, 4, 5, 6 the burning loop: the same rune ellipse glowing, violet spirit flames 6 to 10 squares tall licking up along the whole ring and a few inside, white-violet cores, the flames different in each frame (frame 6 flows back into frame 3); 7 the flames low (3 squares), the rune dimmer; 8 only the faint blue-violet ring and a few violet embers.
Layout: one horizontal row of 8 equal 64:44 cells, image size 8192x704 (each cell 1024x704, 16 px a square); centered across, the ellipse's middle 14 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `nasus_fx_e_hit.png`：E 爆发命中（目标身上），4 帧

灵魂烈焰燃起的一瞬间烧到目标：一团紫色的灵魂火炸开往上窜，蓝紫色的火星往外飞（参考 E_Fire_Scroll）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580) and a blue-violet rune ramp (#FFFFFF, #DCE4FF, #9AAEFF, #5A6CF2, #3238C0, #1A1A70).
Effect: a SPIRIT FIRE BURST on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 5 squares; 2 a violet flame burst 12 squares wide with a white core, its flame tongues pointing up; 3 the flames 16 squares tall, blue-violet sparks flying out at mirrored places; 4 fading violet embers rising.
Layout: one horizontal row of 4 equal 16:18 cells, image size 1024x288 (each cell 256x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `nasus_fx_e_shred.png`：E 减护甲：头顶裂开的盾牌（站在火里的敌人身上，循环），4 帧

站在灵魂烈焰里的敌人护甲被削弱：头顶一面**金色的小盾牌，中间一道裂缝**，裂缝发紫光，一闪一闪（英雄联盟用的就是这个金色裂盾，参考 Armor_Pen）。**左右对称**（裂缝画成竖直的折线，左右对称）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A) and a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580).
Effect: a CRACKED SHIELD floating over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small heater shield 7 squares wide and 8 tall in amber gold with a darker gold rim (a 1-square dark brown edge is allowed: it is a solid thing), a jagged crack running straight down its middle (a symmetric zigzag 1 square wide) glowing violet-white; 1 the crack dim violet; 2 brighter; 3 brightest, 2 tiny violet chips beside the shield at mirrored places; 4 like 2.
Layout: one horizontal row of 4 equal 10:12 cells, image size 640x192 (each cell 160x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `nasus_fx_w_hit.png`：W 枯萎命中（目标身上），5 帧

枯萎打中：一颗紫色的四芒星闪光，一圈带符文的紫色光环套住目标的腰，往里收紧、沉下去，冒出灰紫色的衰败气息（参考 W_Cas_Flare、W_Runes、W_Wither_Swirl）。**左右对称**。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580).
Effect: WITHER STRIKING a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a violet four-pointed star flash 8 squares (thin rays, white centre); 2 a ring of violet light round the unit's middle (an ellipse 20 squares wide and 7 tall) with 6 small bright rune marks on it at mirrored places, a white-violet glow at its centre; 3 the ring tightening (16 wide), the runes brighter, dark violet wisps; 4 the ring 12 wide sinking lower, grey-violet motes; 5 fading motes.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `nasus_fx_w_slow.png`：W 枯萎持续：头顶的枯萎符文（目标身上，5 秒，循环），4 帧

被枯萎的英雄身上：头顶浮着一个紫色的枯萎符文（倒三角里一只眼睛），一亮一暗；两肩往下飘灰紫色的衰败气息，小小的暗紫色微粒往下落（参考 W_Tar_Rune_Anim、W_Wither_Swirl、W_Locus）。**左右对称**，中间身体位置留空（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580).
Effect: a WITHERING CURSE on a champion, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): a violet withering glyph floating over its head (an eye inside a downward-pointing triangle, 7 squares wide and 6 tall, violet-white lines), pulsing: 1 dim, 2 bright, 3 brightest, 4 bright; grey-violet wisps of age curling down from both shoulders (mirrored), small dark violet motes falling past the body's edges, each frame a little lower.
Layout: one horizontal row of 4 equal 20:44 cells, image size 1280x704 (each cell 320x704, 16 px a square); centered across, the figure's feet on the cell's bottom row, the glyph's top 1 square under the cell's top. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `nasus_fx_r_cast.png`：R 死神降临：变身爆发（他身上，不跟随），7 帧

他变成大号的一瞬间：胸口一道紫白闪光，两条紫色能量带从脚下盘旋着往上绕到头顶，地上炸开一圈沙尘，金色沙粒往外飞，头顶闪过一个紫色符文；然后沙尘卷到肩高，慢慢落下（参考 R_Transform_Wave_Swirl、R_Transform_Smoke、R_Symbol_Anim、R_Sparks、R_Swirl_Energy、Z_Taunt_Bits4x4）。**左右对称**，中间身体位置留空（a giant jackal-headed warrior 40 squares wide and 59 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580) and a golden sand ramp (#FFF8DC, #F5DC96, #E0B65E, #B5863A, #7D5726, #4A3216).
Effect: FURY OF THE SANDS: a TRANSFORMATION BURST round a figure, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a giant jackal-headed warrior 40 squares wide and 59 tall stands in the middle, not drawn): 1 a white-violet flash 14 squares at its chest; 2 two violet energy ribbons spiralling up round the figure from its feet to above its head (crossing at mirrored places), a ring of sand dust bursting out on the ground (an ellipse 40 squares wide, 10 tall); 3 the ribbons 6 squares above the head, the dust ring 64 wide and 16 tall, golden sand grains flying out at mirrored places, a violet rune symbol 10 squares wide flashing above the head; 4 the widest: the dust 76 squares wide, sand swirling up to shoulder height on both sides; 5 the ribbons thinning, sand falling; 6 the dust settling low; 7 a few violet sparks and sand grains.
Layout: one horizontal row of 7 equal 80:76 cells, image size 8960x1216 (each cell 1280x1216, 16 px a square); centered across, the figure's feet (the dust ring's middle) 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `nasus_fx_r_hit.png`：R 沙暴伤害（敌人身上，每半秒一次），4 帧

沙暴刮到身边的敌人：一小团金色沙粒打在身上，中间一点紫光，灰黄的沙尘散开（参考 Z_Taunt_Bits4x4、R_Sparks）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden sand ramp (#FFF8DC, #F5DC96, #E0B65E, #B5863A, #7D5726, #4A3216) and a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580).
Effect: a SANDSTORM BITE on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small white-violet flash 3 squares; 2 a burst of golden sand grains 10 squares with a violet core; 3 the grains flying out at mirrored places, pale dust puffs; 4 settling dust.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `nasus_fx_r_on.png`：R 沙暴光环（他脚下和身后，跟随，循环），6 帧

大招期间围着他的**沙暴**：地上一圈打旋的金色沙尘（扁椭圆，直径 64 格，近的一边亮），两边各有一股沙流夹着紫色能量从地面盘旋往上卷到他肩膀那么高，沙粒绕着他飞，圈里有淡淡的紫光；每帧沙流往上走一点，第 6 帧接得回第 1 帧（参考 R_Aura_Swirl、R_Ground_Rune_Scroll、R_Swirl、Z_Taunt_TrailCourse、Z_Taunt_Bits4x4）。这张**画在他身后**（他挡住的地方画了也看不见），**左右对称**，中间身体位置留空（a giant jackal-headed warrior 40 squares wide and 59 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, sand or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden sand ramp (#FFF8DC, #F5DC96, #E0B65E, #B5863A, #7D5726, #4A3216) and a violet spirit-fire ramp (#FFFFFF, #EBDDFF, #C29BFF, #9558F2, #6A2FD0, #3D1580).
Effect: a SANDSTORM AURA round a giant figure, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a giant jackal-headed warrior 40 squares wide and 59 tall stands in the middle, not drawn; the picture is drawn behind him): a ring of swirling sand on the ground (an ellipse 64 squares wide and 20 tall, golden dust with darker sand streaks, brighter on its near side), streams of sand mixed with violet energy spiralling up on both sides of the figure from the ground to its shoulders (mirrored), golden sand grains orbiting, a faint violet glow inside the ring; each frame the streams a little higher (frame 6 flows back into frame 1).
Layout: one horizontal row of 6 equal 76:68 cells, image size 7296x1088 (each cell 1216x1088, 16 px a square); centered across, the figure's feet (the ring's middle) 10 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `nasus_fx_a_hit` | view_effects `league_nasus_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `nasus_fx_q_hit` | view_effects `league_nasus_q_hit`（跟随，画在人物上面；左右对称） | 18 |
| `nasus_fx_q_soul` | view_effects `league_nasus_q_soul`（跟随，画在他上面；左右对称） | 40 × 48 |
| `nasus_fx_e_fire` | view_effects `league_nasus_e_fire`（不跟随，画在人物下面；左右对称；大图表；3–6 帧循环铺满 5 秒） | 64 × 44 |
| `nasus_fx_e_hit` | view_effects `league_nasus_e_hit`（跟随，画在人物上面；左右对称） | 16 |
| `nasus_fx_e_shred` | view_buffs `league_nasus_e_shred`（跟随，画在人物上面；左右对称；循环） | 10 × 12 |
| `nasus_fx_w_hit` | view_effects `league_nasus_w_hit`（跟随，画在人物上面；左右对称） | 22 |
| `nasus_fx_w_slow` | view_buffs `league_nasus_w_slow`（跟随，画在人物上面；左右对称；循环） | 20 × 44 |
| `nasus_fx_r_cast` | view_effects `league_nasus_r_cast`（他身上播一次，不跟随；左右对称；大图表） | 80 × 76 |
| `nasus_fx_r_hit` | view_effects `league_nasus_r_hit`（跟随，画在人物上面；左右对称） | 12 |
| `nasus_fx_r_on` | view_buffs `league_nasus_r_on`（跟随，画在他下面：z -1；左右对称；循环；大图表） | 76 × 68 |

- 两张表：`asset/league/effects/league_nasus_fx`（小的）和 `league_nasus_big`（e_fire、r_cast、r_on），tag = 名字（build_nasus.py 的 views）。
- 没有投射物画面（views_p 为空）。`e_fire`、`r_cast` 不跟随（地上 / 他身上的晚播画面，红色方规则）；`e_fire`、`r_on` 画在人物下面（z -1）；`e_fire` 第 3–6 帧循环铺满 5 秒（e_t 300 tick）。
- 用 `pixel_1x/` 切格（import_swain_fx / import_urgot_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
