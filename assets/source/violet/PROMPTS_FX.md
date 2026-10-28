# 蔚奥莱：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图 + 3 个技能图标。** 造型已定（`design/violet_design.png`：祖安街头的少女拳手，洋红色头发，两只手各戴一只比头还大的铁拳套（蓝灰钢板、金黄方框拳头），双拳举起的格斗架势）。蔚奥莱在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），38 格高、34 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/violet_size.png`：蔚奥莱缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里蔚奥莱自己的特效贴图（**灰色的形状，游戏里再染色**：星形打击、电光、旋风、尘土、光点），按用在我们哪张特效分好了行。只在本地用。
> - **蔚奥莱是祖安的街头拳手，特效都是她的两只铁拳套**：白热的星形拳光、金色和钢灰色的金属火星、青色的短电光（金铲铲里她连招带电）、厚重的冲击环、祖安的尘土和碎石；大招之后的怒火是她头发的粉红色，回气是清新的绿色；不要魔法符文，不要光滑的霓虹光束，不要火柱。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、电光、冲击波、尘土没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。她没有飞行道具，没有要朝向的画面。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `violet_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）；图标交付 `violet_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/violet_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/violet_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「搏击手」 | 每一下都附带额外真实伤害、全能吸血；每条命第一次掉到半血时，2 秒里回一口气 | `p_burst` · `p_wind` |
| 普攻 | 拳套一记直拳 | `a_hit` |
| 技能 1 =「1-2-3连招」 | 两记刺拳，再一记上勾拳把目标打飞 | `q_jab` · `q_up` |
| 技能 2 =「冲拳」 | 冲到敌人身上一拳打退 | `e_dash` · `e_hit` |
| 大招 =「底城怒拳」 | 跳进敌群双拳砸地，冲击波击飞周围的敌人；之后几秒打红了眼：攻速、吸血提高（队里家人越多攻速越高） | `r_slam` · `r_hit` · `r_fury` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 金色（拳套的拳头框、图标边框）：`#FFF6C8`、`#FCD65A`、`#E8A52A`、`#A8641A`、`#5A3010`；
  - 钢灰（拳套钢板）：`#F0F6FA`、`#C4D2DC`、`#8A9CAC`、`#566676`、`#2C3640`；
  - 白热拳光：`#FFFFFF`、`#FFF0C0`、`#FFB850`、`#F06A1E`、`#A0300C`；
  - 青色电光：`#FFFFFF`、`#D8FAFF`、`#7EE6FF`、`#2EA8E8`、`#145A9A`；
  - 粉红（怒火）：`#FFE0F0`、`#FF8ACB`、`#F53F8D`、`#B22059`、`#5C0E30`；
  - 尘土：`#F0E2C8`、`#C8AE88`、`#9A7E5C`、`#64503A`；
  - 绿色（回气）：`#F2FFE8`、`#BFF0A0`、`#7ED460`、`#3E9A3A`、`#1E5A22`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `violet_fx_a_hit.png`：普攻：铁拳直拳打中，4 帧

拳套打在人身上：一个白热的**星形闪光**，几颗金色和钢灰色的火星往两边崩开，一小圈冲击环。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010).
Effect: A PUNCH IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot four-pointed STAR flash 8 squares across; 2 a short orange shock ring 12 squares wide and 6 tall, gold and steel sparks flying out to both sides (mirrored); 3 the ring thinner and wider, the sparks farther, a puff of dust in the middle; 4 the last dust fading. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `violet_fx_q_jab.png`：1-2-3连招：刺拳打中（前两拳），4 帧

连招的前两拳，又快又脆：一个比普攻更亮的白热**星形闪光**，带几道**短短的电光**（青色的小闪电）往两边跳，几颗金色火星。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), an electric cyan ramp (#FFFFFF, #D8FAFF, #7EE6FF, #2EA8E8, #145A9A), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010).
Effect: A QUICK JAB HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a bright white-hot STAR flash 10 squares across with two short electric-cyan zigzag crackles jumping out to both sides (mirrored, 4 squares long); 2 a small orange shock ring 14 squares wide and 6 tall, gold sparks; 3 the ring thin, the crackles gone, a few sparks; 4 fading glints. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `violet_fx_q_up.png`：1-2-3连招：第 3 拳上勾拳打中（击飞），6 帧

第三拳从下往上的上勾拳：一道**竖直往上冲的旋风光柱**（白热的芯、外面一圈青色的电光），金色和橙色的火星呈 V 字往两边上方喷出，脚下一小圈冲击环，最后电光散掉。比刺拳狠得多。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), an electric cyan ramp (#FFFFFF, #D8FAFF, #7EE6FF, #2EA8E8, #145A9A), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: AN UPPERCUT THAT THROWS THE TARGET UP, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-hot flash at the bottom middle 10 squares across; 2 a tall narrow WHIRLWIND column shooting UP 28 squares from the middle - a white-hot core 4 squares wide wrapped in curling electric-cyan streaks - gold and orange sparks spraying up and out in a V to both sides (mirrored), a shock ring at the bottom 18 squares wide and 6 tall; 3 the column at its full height (34 squares), cyan crackles jumping off it; 4 the column thinner, the sparks higher; 5 the sparks falling, dust at the bottom; 6 the last sparks and crackles fading. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 24:36 cells, image size 2304x576 (each cell 384x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `violet_fx_e_dash.png`：冲拳：起步踢起的尘土，5 帧

冲出去那一脚：地上「轰」地踢起一团尘土和碎石，往两边扩散开再落下。留在她起跑的地上（不跟着她），画成圆的，往哪边冲都能用。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010).
Effect: A DASH'S KICK-OFF DUST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a burst of dust 10 squares wide at the bottom middle, two small grit stones flung up to both sides (mirrored); 2 the dust spreading 18 squares wide and 7 tall, rolling puffs; 3 28 squares wide, the stones falling; 4 thinning; 5 the last thin puffs. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 5 equal 30:12 cells, image size 2400x192 (each cell 480x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `violet_fx_e_hit.png`：冲拳：一拳打中（打退），5 帧

冲到身上的那一拳：一下很大的白热**星形闪光**，一个**方方的金色冲击波**（拳套正面的形状，带几排深色的小方孔）往外炸开，橙色火星和碎石往两边四溅，留一团尘土。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A RUSHING GAUNTLET BLOW, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-hot STAR flash 12 squares across; 2 a SQUARE gold shock wave (the gauntlet's fist face, with a row of dark rivet holes) 14 squares across bursting out, orange sparks flying out to both sides (mirrored); 3 a wide orange shock ring 24 squares wide and 10 tall, the sparks farther, grit stones; 4 the ring thin, dust puffs in the middle; 5 the dust fading. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 5 equal square cells, image size 2080x416 (each cell 416x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `violet_fx_r_slam.png`：底城怒拳：双拳砸地的冲击波，8 帧

大招：从半空落下，两只拳套狠狠砸进地面，**地面炸开一圈很大的冲击波**（从中间往外推的橙色和金色的环，环上跳着青色的电光），地上裂开几道裂缝，碎石和尘土往四周飞，裂缝里透出一点橙色的热光，最后慢慢暗下去。这是画在**地上**的（从斜上方看的扁椭圆），中心在格子底部中间（她的脚下）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), an electric cyan ramp (#FFFFFF, #D8FAFF, #7EE6FF, #2EA8E8, #145A9A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A GROUND SHOCKWAVE, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell (her feet): 1 a white-hot flash 16 squares wide; 2 a thick orange shock ring 34 squares wide and 12 tall with a gold outer edge, CRACKS (dark brown lines 1 square wide) starting out from the middle (mirrored); 3 the ring 54 wide and 18 tall, short electric-cyan crackles jumping along it, the cracks longer, chunks of stone and dust flung up to both sides; 4 the ring 76 wide and 26 tall, thinner; 5 the ring at the edge breaking into bright segments, dust billowing; 6 the dust settling, the cracks glowing orange; 7 the cracks dimming; 8 faint cracks and thin dust. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 8 equal 84:30 cells, image size 10752x480 (each cell 1344x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `violet_fx_r_hit.png`：底城怒拳：被击飞，4 帧

被冲击波掀起来的人：脚下「砰」地一下橙色的闪光，尘土往上喷，两边几颗碎石。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A UNIT THROWN UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an orange-white flash at the bottom middle 10 squares wide; 2 a jet of dust shooting upward 14 squares high, grit stones to both sides (mirrored); 3 the dust spreading and thinning; 4 the last puffs. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `violet_fx_r_fury.png`：底城怒拳：怒火（越打越快、吸血），6 帧循环

砸地之后她打红了眼：两只拳套的位置（身体两侧、胸口高度）各绕着**几道粉红色和青色的短电光**，一跳一跳地噼啪作响，脚下一圈淡淡的粉红色光圈，几点粉色火星往上飘。身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot pink ramp (#FFE0F0, #FF8ACB, #F53F8D, #B22059, #5C0E30), an electric cyan ramp (#FFFFFF, #D8FAFF, #7EE6FF, #2EA8E8, #145A9A), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010).
Effect: A FIGHTER IN A FURY, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the slim girl with the two huge gauntlets stands in the middle, not drawn: 34 squares wide and 38 tall: at both sides of her at chest height (where her gauntlets are, mirrored) a small knot of three or four short crackling ZIGZAG sparks in hot pink and electric cyan (each 3-5 squares long), a faint pink ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 30 squares wide and 7 tall at the bottom, and a few pink embers (1-2 squares) drifting up from it; frames 1-6 the crackles jumping to new places, the embers rising. The middle (the body) left empty. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 40:44 cells, image size 3840x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `violet_fx_p_burst.png`：搏击手：回气的一下（半血时触发一次），5 帧

她第一次被打到半血时缓过一口气：脚下「呼」地一圈**清新的绿色光环**往外一荡，身体两侧往上冒一串绿色和白色的光点，头顶一闪。身体位置留空。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fresh green ramp (#F2FFE8, #BFF0A0, #7ED460, #3E9A3A, #1E5A22), a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C).
Effect: A SECOND WIND, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the slim girl with the two huge gauntlets stands in the middle, not drawn: 34 squares wide and 38 tall: 1 a fresh green flash ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 14 squares wide; 2 the ring 30 squares wide and 8 tall, two columns of green and white light motes rising at both sides of her (mirrored); 3 the motes up at her shoulders, a white glint over her head; 4 the ring fading, the motes higher; 5 the last motes. The middle (the body) left empty. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 5 equal 40:44 cells, image size 3200x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `violet_fx_p_wind.png`：搏击手：回气中（持续回血），6 帧循环

回气的 2 秒里：身体两侧几点**绿色的小光点**慢慢往上飘，脚下一圈很淡的绿色光圈。要淡，不要盖住她。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fresh green ramp (#F2FFE8, #BFF0A0, #7ED460, #3E9A3A, #1E5A22).
Effect: HEALING OVER TIME, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the slim girl with the two huge gauntlets stands in the middle, not drawn: 34 squares wide and 38 tall: a faint thin green ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 28 squares wide and 7 tall at the bottom, and at both sides of her (mirrored) a few small green and white motes (1-2 squares) drifting slowly upward from the ring to her shoulders; frames 1-6 the motes rising and new ones starting. Subtle. The middle (the body) left empty. everything is a young UNDERCITY STREET FIGHTER's two huge IRON GAUNTLETS at work: hot white-orange punch flashes, star-shaped impact bursts, gold and steel metal glints, short crackles of electric cyan, heavy shock rings, Zaun dust and grit, cracked stone; flat shades, crisp shapes; no magic runes, no smooth neon beams, no fire columns.
Layout: one horizontal row of 6 equal 36:40 cells, image size 3456x640 (each cell 576x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `violet_icon_skill.png`：技能 1「1-2-3连招」图标

两只大铁拳套一左一右往前打，中间一记往上的上勾拳带着青色电光和白热的闪光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a deep plum-brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: her huge IRON GAUNTLET (blue-grey steel plates on the forearm, copper piston rods, a square gold-yellow fist frame with rows of dark rivets, a thick gold knuckle plate) driving UP in an uppercut at the centre, a white-hot star flash at its knuckles and short electric-cyan crackles round it, two small speed lines below it for the two jabs before. Colours: a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), a steel blue-grey ramp (#F0F6FA, #C4D2DC, #8A9CAC, #566676, #2C3640), a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), an electric cyan ramp (#FFFFFF, #D8FAFF, #7EE6FF, #2EA8E8, #145A9A). No text, no letters.
```

### 图标 2. `violet_icon_skill2.png`：技能 2「冲拳」图标

一只大铁拳套从左往右冲出来，后面拖着橙色的速度线和尘土，拳头前一个白热的星形闪光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a deep plum-brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: her huge IRON GAUNTLET (blue-grey steel plates on the forearm, copper piston rods, a square gold-yellow fist frame with rows of dark rivets, a thick gold knuckle plate) rushing forward from the left to the right, bold orange speed lines and a puff of dust trailing behind it, a white-hot star flash at its knuckles. Colours: a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), a steel blue-grey ramp (#F0F6FA, #C4D2DC, #8A9CAC, #566676, #2C3640), a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A). No text, no letters.
```

### 图标 3. `violet_icon_ult.png`：大招「底城怒拳」图标

两只大铁拳套从上往下砸进地面，地面炸开一圈橙色和金色的冲击波，裂缝四散，粉红色的电光往上跳。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little riveted corners, a deep plum-brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: two huge iron gauntlets (gold fist frames, blue-grey steel) smashing DOWN together into the ground at the centre, an orange-and-gold SHOCKWAVE ring bursting out flat around them, cracks spreading through the ground, hot pink crackles jumping up. Colours: a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), a steel blue-grey ramp (#F0F6FA, #C4D2DC, #8A9CAC, #566676, #2C3640), a hot impact ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a hot pink ramp (#FFE0F0, #FF8ACB, #F53F8D, #B22059, #5C0E30). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `violet_fx_a_hit` | view_effects `tft_violet_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `violet_fx_q_jab` | view_effects `tft_violet_q_jab`（跟随目标，z 2；左右对称） | 18 × 18 |
| `violet_fx_q_up` | view_effects `tft_violet_q_up`（跟随目标，z 2；左右对称） | 24 × 36 |
| `violet_fx_e_dash` | view_effects `tft_violet_e_dash`（留在起跑的地上，z 1；左右对称） | 30 × 12 |
| `violet_fx_e_hit` | view_effects `tft_violet_e_hit`（跟随目标，z 2；左右对称） | 26 × 26 |
| `violet_fx_r_slam` | view_effects `tft_violet_r_slam`（大表，留在她脚下的地上，z -1；左右对称） | 84 × 30 |
| `violet_fx_r_hit` | view_effects `tft_violet_r_hit`（跟随被击飞的人，z 2；左右对称） | 18 × 20 |
| `violet_fx_r_fury` | view_buffs `tft_violet_r_fury`（跟随她，z 3；左右对称） | 40 × 44 |
| `violet_fx_p_burst` | view_effects `tft_violet_p_burst`（跟随她，z 3；左右对称） | 40 × 44 |
| `violet_fx_p_wind` | view_buffs `tft_violet_p_wind`（跟随她，z 3；左右对称） | 36 × 40 |
| `violet_icon_skill` | skill_icons[0] `asset/tft/icons/tft_violet_skill` | 64 × 64 |
| `violet_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_violet_skill2` | 64 × 64 |
| `violet_icon_ult` | skill_icons[2] `asset/tft/icons/tft_violet_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_violet_fx`（小的）和 `tft_violet_big`（r_slam），tag = 名字。
- 全部断言左右对称。
- p_burst / p_wind 由 tft.dll 在她第一次掉到半血时播 / 挂上；r_fury 由 tft.dll 在砸地时挂上。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
