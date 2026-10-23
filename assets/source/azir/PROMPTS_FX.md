# 沙漠皇帝 阿兹尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型已定（`design/azir_design.png`：Q 版沙漠皇帝，鹰首金盔、金甲青蓝宝石、深紫袍子披风、手里一根竖直的长权杖）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连权杖 49 格高、34 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。沙兵、禁军、太阳圆盘本人是另外的图，**特效里不要画他们**。
> - 大小对照 `design/azir_size.png`：阿兹尔、沙兵、太阳圆盘放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里阿兹尔自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**阿兹尔是恕瑞玛的沙漠皇帝，所有特效都是黄沙的魔法**：打旋的浅金色沙子、赭黄的沙尘、亮晶晶的沙粒、白金色的太阳光芒，点缀几颗青色的闪光（他宝石的颜色）；不要火，也不要光滑的霓虹光束。
> - **特效要亮**：每股沙流、每道光都有最亮一档或白色的高光，暗底上一眼能看见。
> - **光、沙、尘、冲击、光环都没有黑描边**。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`a_bolt`、`q_wave`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `azir_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/azir_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/azir_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 权杖一指，身边的沙兵替他刺；没有沙兵能刺时他自己射一道沙光 | `a_bolt` · `a_hit` · `s_stab` |
| 被动「沙兵现身」 | 普攻时在目标身边从沙里召出黄沙士兵（最多 3 个） | `s_spawn` · `s_stab` |
| 被动「太阳圆盘」（附加包） | 每局一次，在我方倒下的塔的废墟上立起太阳圆盘，向敌人射太阳光束 | `d_rise` · `d_beam` · `d_glow` |
| 技能 1 =「狂沙猛攻」 | 沙兵卷起沙浪冲向目标，落地马上刺：伤害、减速 | `q_wave` · `q_hit` · `q_land` · `slow` |
| 技能 2 =「流沙移形」 | 套上沙之护盾化沙冲向敌人（被贴身时往后跳），撞中时多召一个沙兵 | `e_shield` · `e_land` · `e_hit` |
| 大招 =「禁军之墙」 | 一排禁军从沙墙里冲出，撞飞敌人；正推把人推远，反推（E 之后）把人推回我方 | `r_rise` · `r_dust` · `r_hit` |

连招：**流沙移形撞中英雄 → 禁军之墙反推**，**狂沙猛攻落地 → 沙兵马上刺**，**禁军之墙撞飞 → 狂沙猛攻**，**流沙移形撞中 → 多一个沙兵**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、沙、尘没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **都是黄沙的魔法**：浅金、赭黄、棕色沙尘、白金色的光、几颗青色闪光；每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 恕瑞玛·黄沙：`#FFFFFF`、`#FFF2C8`、`#F2D282`、`#D8A850`、`#A87430`、`#6A4418`；
  - 太阳·金光：`#FFFFFF`、`#FFF8D8`、`#FFE47A`、`#F8BC2C`、`#C47A12`；
  - 宝石·青：`#FFFFFF`、`#D4FFFA`、`#74F0E6`、`#22B8C8`、`#106878`；
  - 沙尘·灰棕：`#E8D8B8`、`#C4A878`、`#8C7048`、`#5A4630`；
- 打中、爆发居中画，不旋转；地面上的圈（沙堆、沙尘、光环）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `azir_fx_a_bolt.png`：普攻：权杖射出的一道沙光，4 帧循环

没有沙兵能刺时，他权杖射出的一小道金色沙光：亮白金的核心，后面拖一条旋转的沙粒尾巴。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418).
Effect: A SMALL SAND BOLT, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a white-gold core 4 squares across at the right, a short tapering trail of swirling pale-gold sand grains 9 squares long behind it, the grains moving back frame to frame. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 14:8 cells, image size 896x128 (each cell 224x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `azir_fx_a_hit.png`：普攻：沙光打中，3 帧

沙光打中：一个白金色的闪光，四周喷出一圈沙粒。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418).
Effect: A SAND BOLT LANDING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 5 squares across; 2 a ring of pale-gold sand grains bursting out 11 across at mirrored places; 3 the grains further out, fading to ochre. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `azir_fx_s_spawn.png`：沙兵现身：地上隆起的沙堆，5 帧

沙兵出现的地方（参考 sandmound、blowing_sand）：地上一圈沙子打旋隆起成一个小沙堆，几颗亮晶晶的沙粒弹起来，然后散开落下。**画在地上（从斜上方看的椭圆）、左右对称**，5 帧。沙兵本人另画，不要画人。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a dull dust ramp (#E8D8B8, #C4A878, #8C7048, #5A4630).
Effect: SAND RISING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND (an ellipse seen from above, three times as wide as tall): 1 a small swirl of pale-gold sand 10 squares wide; 2 the swirl widening to 20, the sand heaping up in the middle into a mound 5 squares tall; 3 the mound at its highest with glittering grains and two white-gold glints jumping up; 4 the mound sinking and spreading; 5 a thin ring of settling dust. No soldier drawn. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 5 equal 24:12 cells, image size 1920x192 (each cell 384x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `azir_fx_s_stab.png`：沙兵刺中：一根沙矛刺在敌人身上，4 帧

沙兵刺中敌人（参考 soldier_spear、ba_yellow_ray）：一根**金色的沙矛**从上往下刺到敌人身上，矛尖一闪，刺中的地方炸开一圈沙粒。**竖直、左右对称**（游戏不会翻转它），4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a teal glint ramp (#FFFFFF, #D4FFFA, #74F0E6, #22B8C8, #106878).
Effect: A SAND SPEAR STRIKING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a vertical gold spear of packed sand 3 squares wide stabbing down from the top of the cell, its leaf-shaped white-gold tip at the target's chest; 2 the tip flashing white with a teal glint; 3 a burst of sand grains around the tip 12 squares across at mirrored places, the spear crumbling into sand from the top; 4 only falling grains. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 14:30 cells, image size 896x480 (each cell 224x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `azir_fx_q_wave.png`：狂沙猛攻：冲出去的一道沙浪，4 帧循环

沙兵冲锋时卷起的一道沙浪（参考 soldiersandtrail、wisps_mis）：前面一个尖尖的金色沙头，后面翻滚的沙尘带和亮晶晶的沙粒。**朝右飞、上下对称**，4 帧循环（沙浪翻滚）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a dull dust ramp (#E8D8B8, #C4A878, #8C7048, #5A4630).
Effect: A SAND RUSH, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): at the right a pointed white-gold head of packed sand 6 squares long, behind it a rolling band of pale-gold and ochre sand 18 squares long, wavy at its edges with glittering grains, the waves rolling back frame to frame. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 26:12 cells, image size 1664x192 (each cell 416x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `azir_fx_q_land.png`：狂沙猛攻：沙兵落地扬起的沙尘，5 帧

沙兵冲到落点时扬起的一大圈沙尘（参考 q_end、q_dust）：地上一圈沙子往外喷开，几道金光闪一下，沙尘慢慢落下。**地上的椭圆、左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a dull dust ramp (#E8D8B8, #C4A878, #8C7048, #5A4630).
Effect: SAND CRASHING DOWN, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND (an ellipse three times as wide as tall): 1 a white-gold flash 8 squares wide in the middle; 2 a ring of sand spraying out 24 wide with a few short gold rays; 3 the ring at 34 wide, puffs of ochre dust rising at mirrored places; 4 the dust drifting, thinning; 5 a faint ring settling. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 5 equal 36:14 cells, image size 2880x224 (each cell 576x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `azir_fx_q_hit.png`：狂沙猛攻：打中，4 帧

沙浪打中敌人：一团金色沙子撞上去炸开，沙粒四散。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12).
Effect: A SAND RUSH STRIKING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 6 squares across on the target's chest; 2 a burst of pale-gold sand 14 across; 3 sand grains flying out at mirrored places; 4 the grains falling, fading to ochre. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:18 cells, image size 1024x288 (each cell 256x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `azir_fx_slow.png`：狂沙猛攻：减速，脚下流沙，4 帧循环

被减速的敌人脚下：一圈慢慢打旋的流沙。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a dull dust ramp (#E8D8B8, #C4A878, #8C7048, #5A4630).
Effect: QUICKSAND, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the feet (an ellipse 14 squares wide and 5 tall): a slowly swirling ring of pale-gold and ochre sand, two sand ripples turning round it at mirrored places. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `azir_fx_e_shield.png`：流沙移形：身上的沙之护盾，4 帧

冲刺时他身上套的一层沙之护盾（参考 e_shield_base、outerring）：围着他一圈旋转的金色沙流，外圈一道亮金色的弧，上下两头有几颗青色的闪光。**只画外圈，身体位置留空，左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a teal glint ramp (#FFFFFF, #D4FFFA, #74F0E6, #22B8C8, #106878).
Effect: A SAND SHIELD, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a shell of swirling pale-gold sand streams around the body, 38 squares wide and 44 tall, a bright white-gold arc along its outer edge, two teal glints at the top and the bottom; the streams turning round frame to frame; the middle 30 x 38 squares left EMPTY for his body. he stands in the middle, not drawn: 34 squares wide and 40 tall (the sceptre not counted). everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 40:46 cells, image size 2560x736 (each cell 640x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `azir_fx_e_land.png`：流沙移形：冲到落点喷起的沙柱，5 帧

他化沙冲到敌人身上时，脚下喷起一圈沙柱（参考 e_geyser）：地上一圈沙子猛地往上喷，然后落下。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a dull dust ramp (#E8D8B8, #C4A878, #8C7048, #5A4630).
Effect: A SAND GEYSER, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a ring of sand on the ground 16 wide (an ellipse); 2 columns of sand bursting up 16 squares tall around the ring with a white-gold flash in the middle; 3 the columns at their highest, grains flying out at mirrored places; 4 the sand falling back; 5 a ring of settling dust 28 wide. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 5 equal 30:24 cells, image size 2400x384 (each cell 480x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `azir_fx_e_hit.png`：流沙移形：撞中，4 帧

冲刺撞中敌人：一团沙子炸开，几道金光。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12).
Effect: A SAND DASH STRIKING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash on the target's chest; 2 a burst of sand 14 across with four short gold rays at mirrored angles; 3 the sand flying out; 4 the grains falling. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `azir_fx_r_rise.png`：禁军之墙：一排沙墙从地里升起，6 帧

禁军出现的地方：地上一长条沙子猛地往上翻涌成一道沙墙（禁军从里面冲出来，禁军本人另画），然后沙墙塌落成沙尘。**横着的一长条、左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a dull dust ramp (#E8D8B8, #C4A878, #8C7048, #5A4630).
Effect: A WALL OF SAND RISING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a long line of churning sand on the ground 60 squares wide and 4 tall; 2 the sand surging up into a ragged wall 14 squares tall all along the line, white-gold glints on its crest; 3 the wall at its highest, 24 tall, grains blowing off its top; 4 the wall breaking apart into sand curtains; 5 the curtains falling; 6 a long low band of settling dust. No soldiers drawn. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 6 equal 70:30 cells, image size 6720x480 (each cell 1120x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `azir_fx_r_dust.png`：禁军之墙：冲锋时脚下扬起的沙尘，4 帧

禁军冲锋时脚下踢起的沙尘：地上一团团沙尘往两边扬起。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a dull dust ramp (#E8D8B8, #C4A878, #8C7048, #5A4630).
Effect: CHARGE DUST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND: 1 two puffs of ochre and pale-gold dust 8 squares wide at mirrored places; 2 the puffs growing and rising to 10 squares tall with grains kicked up; 3 the puffs drifting apart, thinning; 4 faint wisps. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 30:12 cells, image size 1920x192 (each cell 480x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `azir_fx_r_hit.png`：禁军之墙：撞飞，4 帧

禁军的盾撞中敌人：一个白金色的大冲击闪光，沙粒和金光向四面炸开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418).
Effect: A SHIELD SLAM, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-gold impact flash 10 squares across on the target's chest; 2 a star of six short gold rays 18 across at mirrored angles with sand bursting between them; 3 the sand flying out; 4 the grains falling, fading to ochre. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:22 cells, image size 1152x352 (each cell 288x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `azir_fx_d_rise.png`：太阳圆盘：从沙里升起，6 帧

太阳圆盘立起来的地方（参考 towersandbib、solarflare）：地上一大圈沙子打旋，中间一道金光冲天，沙子往外翻开。圆盘本人另画。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418), a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a teal glint ramp (#FFFFFF, #D4FFFA, #74F0E6, #22B8C8, #106878).
Effect: THE SUN DISC RISING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a wide swirl of sand on the ground 30 squares across (an ellipse); 2 the swirl at 50 across, a column of white-gold light 6 wide shooting up from its middle to the top of the cell; 3 the light at its brightest with teal glints, sand spraying out at mirrored places; 4 the column thinning; 5 the sand settling in a ring; 6 a faint gold ring. No disc drawn. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:26 cells, image size 5376x416 (each cell 896x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `azir_fx_d_beam.png`：太阳圆盘：射下来的太阳光束，5 帧

太阳圆盘攻击敌人（参考 z_beam_core、beam_outer）：一道从天上直直打下来的白金色光柱，打在敌人身上炸开一圈金光。**竖直、左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a teal glint ramp (#FFFFFF, #D4FFFA, #74F0E6, #22B8C8, #106878).
Effect: A SOLAR RAY, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin white-gold line 2 squares wide from the top of the cell down to the target's chest; 2 the ray 8 squares wide, a white core and sun-gold edges, a flash where it lands; 3 the ray at its widest, 12, a ring of gold light 14 across at its foot with two teal glints; 4 the ray thinning; 5 sparks fading at the foot. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall at the bottom of the cell. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 5 equal 16:60 cells, image size 1280x960 (each cell 256x960, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `azir_fx_d_glow.png`：太阳圆盘：脚下的光环，6 帧循环

太阳圆盘立着的时候，它脚下地上一圈慢慢转的金色光环和沙粒。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sun-gold light ramp (#FFFFFF, #FFF8D8, #FFE47A, #F8BC2C, #C47A12), a Shurima sand ramp (#FFFFFF, #FFF2C8, #F2D282, #D8A850, #A87430, #6A4418).
Effect: A SOLAR RING, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND (an ellipse 38 squares wide and 12 tall): a thin ring of sun-gold light with four short rays pointing out at mirrored angles, glittering grains drifting round it, the ring brightening and dimming. everything is the SAND MAGIC of a desert emperor: swirling pale-gold sand, ochre dust, glittering grains, white-gold sun flares and a few teal glints; flat shades, crisp shapes; no fire, no smooth neon beams.
Layout: one horizontal row of 6 equal 40:14 cells, image size 3840x224 (each cell 640x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `azir_fx_a_bolt` | view_projectiles `league_azir_a_bolt`（弹道，z 2；上下对称） | 14 × 8 |
| `azir_fx_a_hit` | view_effects `league_azir_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `azir_fx_s_spawn` | view_effects `league_azir_s_spawn`（在沙兵站的地方，地上，z 1，不跟随；左右对称） | 24 × 12 |
| `azir_fx_s_stab` | view_effects `league_azir_s_stab`（跟随目标，z 3；左右对称） | 14 × 30 |
| `azir_fx_q_wave` | view_projectiles `league_azir_q_wave`（弹道，z 2；上下对称） | 26 × 12 |
| `azir_fx_q_land` | view_effects `league_azir_q_land`（在落点，地上，z 1，不跟随；左右对称） | 36 × 14 |
| `azir_fx_q_hit` | view_effects `league_azir_q_hit`（跟随目标，z 2；左右对称） | 16 × 18 |
| `azir_fx_slow` | view_buffs `league_azir_q_slow`（tag `slow`，跟随，脚下，z -1；左右对称） | 16 × 8 |
| `azir_fx_e_shield` | view_effects `league_azir_e_shield`（在他身上，跟随，z 3；左右对称） | 40 × 46 |
| `azir_fx_e_land` | view_effects `league_azir_e_land`（在他落地的地方，地上，z 1，不跟随；左右对称） | 30 × 24 |
| `azir_fx_e_hit` | view_effects `league_azir_e_hit`（跟随目标，z 2；左右对称） | 16 × 20 |
| `azir_fx_r_rise` | view_effects `league_azir_r_rise`（大表，在他前面，地上，z 1，不跟随；左右对称） | 70 × 30 |
| `azir_fx_r_dust` | view_effects `league_azir_r_dust`（在冲锋的禁军脚下，地上，z 1，不跟随；左右对称） | 30 × 12 |
| `azir_fx_r_hit` | view_effects `league_azir_r_hit`（跟随目标，z 2；左右对称） | 18 × 22 |
| `azir_fx_d_rise` | view_effects `league_azir_d_rise`（大表，在我方塔的废墟上，地上，z 1，不跟随；左右对称；附加包放） | 56 × 26 |
| `azir_fx_d_beam` | view_effects `league_azir_d_beam`（大表，跟随目标，z 3；左右对称；附加包放） | 16 × 60 |
| `azir_fx_d_glow` | view_effects `league_azir_d_glow`（在圆盘脚下，地上，z -1，不跟随；左右对称；附加包放） | 40 × 14 |

- 两张表：`asset/league/effects/league_azir_fx`（小的）和 `league_azir_big`（r_rise、d_rise、d_beam），tag = 名字（build_azir.py 的 views；q_slow 用 `slow`）。沙兵 `league_azir_soldier`（tags soldier_a/b/c + 刺）、禁军 `league_azir_guard`（charge 朝右 / 朝左翻一份）、太阳圆盘是姿势那一轮的图做的表。
- 弹道（a_bolt、q_wave）断言上下对称；其余断言左右对称；d_glow 在圆盘立着时一直循环。
- 用 `pixel_1x/` 切格（import_aurora_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
