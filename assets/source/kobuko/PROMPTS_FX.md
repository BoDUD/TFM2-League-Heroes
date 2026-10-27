# 可酷伯：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图 + 3 个技能图标。** 造型已定（`design/kobuko_design.png`：金橙色的约德尔功夫老猫，雪白的胡子和发髻，火焰纹的粗手臂，掌心一个金色漩涡，蓝白短褂）。可酷伯在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），40 格高、38 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/kobuko_size.png`：可酷伯缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里可酷伯自己的特效贴图（第 15、14 赛季，**灰色的形状，游戏里再染色**：金色护盾、掌击、星星、地面冲击、第二阶段的火、尘土），按用在我们哪张特效分好了行。只在本地用。
> - **可酷伯是功夫老宗师，特效都是他的气劲**：温暖的**金色**光和圆圆的**漩涡纹**（和他掌心的金色漩涡一样）、狂怒时**橙红色的火焰**（和他手臂的火焰纹一样）、落地砸地时的尘土和碎石；不要蓝色，不要魔法符文，不要光滑的霓虹光束。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、护盾、冲击波、尘土没有黑描边**（星星、漩涡印记、石块这些实物可以有一圈深色描边）。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。他没有飞行道具，没有要朝向的画面。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kobuko_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）；图标交付 `kobuko_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/kobuko_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/kobuko_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「第二阶段」 | 每条命第一次掉到一半血时怒吼，进入狂怒直到死亡：攻速、吸血 | `p_burst` · `p_rage` |
| 普攻 | 大爪子一掌拍出去 | `a_hit` |
| 技能 1 =「金爪真言」 | 双臂一张套上金色护盾，下一掌变成金爪重掌：额外伤害 + 晕眩 | `q_shield` · `q_on` · `q_hit` · `q_stun` |
| 技能 2 =「猛虎扑」 | 扑到一个敌人身上，落地把周围的敌人击飞 | `e_land` · `e_hit` |
| 大招 =「游戏结束！」 | 一跃冲天（目标脚下出现落点圈），从天而降砸在目标身上，冲击波击飞周围的敌人 | `r_jump` · `r_mark` · `r_slam` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、护盾、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 金色气劲（护盾、掌印、漩涡、冲击环、图标边框）：`#FFFDE8`、`#FFE98A`、`#F7C53A`、`#D88A16`、`#8A4A0A`；
  - 火焰橙红（狂怒、火星）：`#FFF4C8`、`#FFC24A`、`#FF7A1E`、`#D8341A`、`#7A140E`；
  - 尘土：`#F0E2C8`、`#C8AE88`、`#9A7E5C`、`#64503A`；
  - 碎石、裂缝：`#D8D0C0`、`#A89C88`、`#74695A`、`#463E34`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `kobuko_fx_a_hit.png`：普攻：猫爪掌打中，4 帧

大爪子一掌拍中：一下白色的闪光，一圈金橙色的冲击环，几点火星往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E).
Effect: A HEAVY PALM STRIKE IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white star flash 8 squares across; 2 a short golden shock ring 12 squares wide and 6 tall, orange sparks flying out to both sides (mirrored); 3 the ring thinner and wider, the sparks farther; 4 the last sparks fading. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kobuko_fx_q_shield.png`：金爪真言：身上套上金色护盾，6 帧

可酷伯放技能 1 时双臂一张，身上「嗡」地套上一层**金色的气劲护盾**：从胸前一点金光往外张开成一个包住全身的圆罩，罩边上转着几个金色的漩涡纹，最后只剩一圈淡淡的金色外轮廓。身体位置留空（只画外圈）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A).
Effect: A GOLDEN CHI SHIELD SNAPPING ON, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the round, broad cat master stands in the middle, not drawn: 38 squares wide and 40 tall: 1 a small white-gold spark at his chest; 2 a ring of golden light bursting out from it; 3 a round dome 42 squares wide and 46 tall around him, its edge a golden band 2 squares thick with four round SPIRAL swirls on it (each 5 squares across, at mirrored places); 4 the spirals turning, light running round the edge; 5 the whole edge bright with a white rim; 6 settling to a thin pale gold outline. Only the outer edge: the middle (the body) left empty. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 44:48 cells, image size 4224x768 (each cell 704x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kobuko_fx_q_on.png`：金爪真言：金爪蓄好（下一掌加强），6 帧循环

技能 1 之后、下一掌打出去之前：他头顶上方转着一个**金色的漩涡印记**（和他掌心的漩涡一样），身体两侧往上飘几点金色光点。身体位置留空。不要太显眼。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A).
Effect: A CHARGED GOLDEN CLAW, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the round, broad cat master stands in the middle, not drawn: 38 squares wide and 40 tall: over his head (the top 8 squares of the cell) a golden SPIRAL sigil 7 squares across, glowing; at both sides of him (mirrored) a few golden motes (1-2 squares) drifting up; frames 1-6 the spiral pulsing brighter and back, the motes rising and fading in turn. The middle (the body) left empty. Subtle. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 40:48 cells, image size 3840x768 (each cell 640x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kobuko_fx_q_hit.png`：金爪重掌：打中（加伤 + 晕眩），5 帧

金爪重掌打中：一下大大的白金色闪光，中间印出一个**金色的漩涡掌印**，金色的冲击环往外炸开，火星四溅。比普攻狠得多。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E).
Effect: A GOLDEN CLAW SLAMMING INTO A UNIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-gold flash 14 squares across; 2 a golden SPIRAL imprint 12 squares across glowing in the middle, a golden shock ring bursting out, orange sparks flying out to both sides (mirrored); 3 a wide gold ring 24 squares wide and 12 tall, the spiral turning, the sparks farther; 4 the ring thin, the spiral fading; 5 the last sparks. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 2080x416 (each cell 416x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kobuko_fx_q_stun.png`：金爪真言：晕眩，6 帧循环

被拍晕的人：头顶上一圈**金色的小星星**和小漩涡绕着转。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A).
Effect: A STUNNED UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 10 squares of the cell) a flat ring of three small golden STARS and two tiny SPIRALS (each 3x3 squares) circling round, seen from the side (an ellipse 14 wide and 4 tall); frames 1-6 them moving round the ring (the ones in front brighter, mirrored positions). The rest of the cell empty. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 18:44 cells, image size 1728x704 (each cell 288x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kobuko_fx_e_land.png`：猛虎扑：落地的冲击，6 帧

可酷伯扑到敌人身上落地：地上「咚」地一圈**金橙色的冲击环**往外推开，尘土和小石块往两边飞，再落下。画在**地上**（扁椭圆），中心在格子底部中间。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A), a broken stone grey-brown ramp (#D8D0C0, #A89C88, #74695A, #463E34).
Effect: A POUNCE LANDING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell: 1 a white-gold flash 12 squares wide; 2 a golden shock ring 24 squares wide and 8 tall, dust puffs to both sides (mirrored); 3 the ring 36 wide and 12 tall, small stones flung up; 4 the ring 42 wide, thinner, the stones falling; 5 dust settling; 6 the last thin dust. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 44:16 cells, image size 4224x256 (each cell 704x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kobuko_fx_e_hit.png`：猛虎扑：被击飞，4 帧

被扑击掀起来的人：脚下「砰」地一下金色的闪光，尘土往上喷，两边几颗小石头。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A UNIT THROWN UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash at the bottom middle 10 squares wide; 2 a jet of dust shooting upward 14 squares high, small stones to both sides (mirrored); 3 the dust spreading and thinning; 4 the last puffs. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kobuko_fx_r_jump.png`：游戏结束！：一跃冲天的起跳尘土，5 帧

可酷伯从这里一跃冲天：地上「轰」地踢起一圈尘土，几道金色的风线往上直冲出去（他已经飞走了，不画他）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A MIGHTY LEAP'S TAKE-OFF, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a burst of dust 14 squares wide at the bottom middle on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), two golden WIND STREAKS (1 square wide) shooting straight up from it 20 squares high (mirrored); 2 the dust ring 26 wide and 8 tall, the streaks reaching the top of the cell; 3 the streaks thinning and breaking upward, the dust 32 wide; 4 the streaks gone, the dust rolling; 5 the last thin dust. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 5 equal 32:30 cells, image size 2560x480 (each cell 512x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kobuko_fx_r_mark.png`：游戏结束！：落点预警，6 帧

他在天上的这一会儿，目标脚下出现一个**金橙色的落点圈**，从大往小收紧、越来越亮（中间一个金色漩涡），提示他要从天而降砸在这里。画在**地上**（扁椭圆）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E).
Effect: A LANDING WARNING ON THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred in the cell: 1 a thin golden ring 28 squares wide and 10 tall; 2-5 the ring tightening frame by frame to 14 wide and 5 tall, thicker and brighter, turning orange, a golden SPIRAL 6 wide and 2 tall appearing in its middle; 6 the ring small and blazing white-gold. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 30:12 cells, image size 2880x192 (each cell 480x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kobuko_fx_r_slam.png`：游戏结束！：从天而降砸地的冲击波，8 帧

大招：可酷伯从天而降砸在敌人身上，**地面炸开一圈很大的冲击波**（从中间往外推的金色和橙红色的环），地上裂开几道裂缝，尘土和碎石往四周飞，最后裂缝慢慢暗下去。这是画在**地上**的（扁椭圆），中心在格子底部中间。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A), a broken stone grey-brown ramp (#D8D0C0, #A89C88, #74695A, #463E34).
Effect: A GROUND-SHATTERING CRASH, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell: 1 a white-gold flash 18 squares wide; 2 a thick golden shock ring 38 squares wide and 12 tall with a flame orange outer edge, CRACKS (dark stone lines 1 square wide) starting out from the middle (mirrored); 3 the ring 58 wide and 20 tall, the cracks longer, dust and broken stones flung up to both sides; 4 the ring 80 wide and 28 tall, thinner; 5 the ring at the edge breaking into bright segments, dust billowing; 6 the dust settling, the cracks glowing gold; 7 the cracks dimming; 8 faint cracks and thin dust. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 8 equal 90:32 cells, image size 11520x512 (each cell 1440x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kobuko_fx_r_hit.png`：游戏结束！：被砸飞，4 帧

被砸落的冲击掀起来的人：脚下「砰」地一下金橙色的大闪光，尘土和碎石往上喷。比猛虎扑更猛。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A UNIT BLASTED UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big gold-white flash at the bottom middle 14 squares wide; 2 a jet of dust and flame-orange sparks shooting upward 18 squares high, broken stones to both sides (mirrored); 3 the dust spreading and thinning; 4 the last puffs. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 4 equal 20:24 cells, image size 1280x384 (each cell 320x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kobuko_fx_p_burst.png`：第二阶段：血量掉到一半，进入狂怒，6 帧

第二阶段触发：可酷伯怒吼一声，身上「轰」地炸开一圈**橙红色的火焰**，一圈冲击环往外推，火舌往上窜，最后剩下身边几簇火苗。身体位置留空（只画外圈和上面的火舌）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E), a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A).
Effect: A ROARING RAGE BURSTING OUT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the round, broad cat master stands in the middle, not drawn: 38 squares wide and 40 tall: 1 a white-orange flash ring around his chest; 2 a ring of FLAME orange-red fire bursting out to 44 squares wide, a golden shock ring on the ground; 3 tall flame TONGUES licking up at both sides of him (mirrored) to over his head; 4 the flames at their tallest, sparks flying up; 5 the flames dropping; 6 a few small flames left at his sides and feet. After frame 1 the middle (the body) left empty. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 46:52 cells, image size 4416x832 (each cell 736x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `kobuko_fx_p_rage.png`：第二阶段：狂怒中，6 帧循环

狂怒中的可酷伯：身体两侧各有几簇**橙红色的火苗**往上窜，脚下一圈暗红色的火圈，火星往上飘。身体位置留空（只画两侧和脚下）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E).
Effect: AN ENRAGED AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the round, broad cat master stands in the middle, not drawn: 38 squares wide and 40 tall: at both sides of him (mirrored) three small flame TONGUES (each 4 squares wide and 6-9 tall) at his shoulder, waist and knee height, and a dark red ring of fire on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 34 squares wide and 6 tall at the bottom; frames 1-6 the flames flickering up and down in turn, sparks drifting up. The middle (the body) left empty. everything is an old KUNG-FU MASTER CAT's chi: warm GOLDEN light with round SPIRAL swirls (the golden spiral on his palms), FLAME orange-red fire like the flame pattern of his fur when he is enraged, heavy dust and broken stones where he lands; flat shades, crisp shapes; no blue, no magic runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 42:48 cells, image size 4032x768 (each cell 672x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `kobuko_icon_skill.png`：技能 1「金爪真言」图标

一只火焰纹的大猫爪张开、掌心朝前，掌心一个发光的金色漩涡，四周一圈金色的护盾光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little round spiral corners, a deep warm brown-red inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big flame-patterned CAT PAW (orange-red fur, short black claws) open with the palm to the viewer, a glowing GOLDEN SPIRAL on the palm, a round golden chi shield ring around it. Colours: a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E). No text, no letters.
```

### 图标 2. `kobuko_icon_skill2.png`：技能 2「猛虎扑」图标

一只张开爪子的大猫爪从左上方扑下来，爪尖拖着金色的速度线，下面一圈尘土。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little round spiral corners, a deep warm brown-red inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big flame-patterned CAT PAW with its black claws spread, pouncing down from the upper left toward the lower right, golden speed lines trailing behind it, a burst of dust under it. Colours: a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E), a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A). No text, no letters.
```

### 图标 3. `kobuko_icon_ult.png`：大招「游戏结束！」图标

一只巨大的猫爪从天上砸进地里，地面炸开一圈金色和橙红色的冲击波，裂缝四散，碎石飞起。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square GOLD frame with little round spiral corners, a deep warm brown-red inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge flame-patterned CAT PAW slammed down from above into the ground at the centre, a gold-and-orange SHOCKWAVE ring bursting out flat around it, cracks spreading through the ground, broken stones flying up. Colours: a golden chi ramp (#FFFDE8, #FFE98A, #F7C53A, #D88A16, #8A4A0A), a flame orange-red ramp (#FFF4C8, #FFC24A, #FF7A1E, #D8341A, #7A140E), a broken stone grey-brown ramp (#D8D0C0, #A89C88, #74695A, #463E34). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kobuko_fx_a_hit` | view_effects `tft_kobuko_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `kobuko_fx_q_shield` | view_effects `tft_kobuko_q_shield`（跟随他，z 3；左右对称） | 44 × 48 |
| `kobuko_fx_q_on` | view_buffs `tft_kobuko_q_on`（跟随他，z 3；左右对称） | 40 × 48 |
| `kobuko_fx_q_hit` | view_effects `tft_kobuko_q_hit`（跟随被打的人，z 2；左右对称） | 26 × 26 |
| `kobuko_fx_q_stun` | view_buffs `tft_kobuko_q_stun`（跟随被晕的人，z 3；左右对称） | 18 × 44 |
| `kobuko_fx_e_land` | view_effects `tft_kobuko_e_land`（留在他落地的地上，z -1；左右对称） | 44 × 16 |
| `kobuko_fx_e_hit` | view_effects `tft_kobuko_e_hit`（跟随被击飞的人，z 2；左右对称） | 18 × 20 |
| `kobuko_fx_r_jump` | view_effects `tft_kobuko_r_jump`（留在起跳的地上，z 1；左右对称） | 32 × 30 |
| `kobuko_fx_r_mark` | view_effects `tft_kobuko_r_mark`（跟随被砸的目标，z -1；左右对称） | 30 × 12 |
| `kobuko_fx_r_slam` | view_effects `tft_kobuko_r_slam`（大表，留在他砸落的地上，z -1；左右对称） | 90 × 32 |
| `kobuko_fx_r_hit` | view_effects `tft_kobuko_r_hit`（跟随被击飞的人，z 2；左右对称） | 20 × 24 |
| `kobuko_fx_p_burst` | view_effects `tft_kobuko_p_burst`（跟随他，z 3；左右对称） | 46 × 52 |
| `kobuko_fx_p_rage` | view_buffs `tft_kobuko_p_rage`（跟随他，z 3；左右对称） | 42 × 48 |
| `kobuko_icon_skill` | skill_icons[0] `asset/tft/icons/tft_kobuko_skill` | 64 × 64 |
| `kobuko_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_kobuko_skill2` | 64 × 64 |
| `kobuko_icon_ult` | skill_icons[2] `asset/tft/icons/tft_kobuko_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_kobuko_fx`（小的）和 `tft_kobuko_big`（r_slam），tag = 名字。
- 全部断言左右对称。
- p_burst 由 tft.dll 在第二阶段触发时播；q_shield 在技能 1 出手时播；r_jump 在大招起跳时留在原地，r_mark 跟着目标。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
