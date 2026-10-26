# 诺拉：补充特效（给 Codex 的提示词，第 3 步补充）

> **这一份是 12 张特效图 + 3 个技能图标。** 诺拉的技能改成了**英雄联盟手游**里她的技能（被动「寄情琐物」、Q「回忆涌现」、W「奇异旅程」、E「思乡线缕」、R「传送门欢腾！」），上一份特效里普攻的魔法弹、Q 的球和爆炸**继续用**，这一份只画新技能需要的画面。
> - **画风和颜色照你上一次的交付**（`refs/first_delivery.png`：金色花纹、紫色漩涡、粉金小星星，硬边像素、没有柔光），样子照手游（`refs/wr_*.jpg` 是手游官方技能介绍视频的截图：琐物、奇异旅程、思乡线缕、传送门欢腾！）。
> - 诺拉在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），36 格高、24 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素）。大小对照 `design/norra_size.png`（诺拉缩到游戏大小、放大 4 倍，红线是地面，右边是原版斗士）。
> - **特效要亮**；**光、门、线、星星没有黑描边**；**只有茶杯（`p_trinkets`）有 1 格近黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**（`w_in` 例外：人被放逐时看不见，可以盖住）。
> - **所有画面严格左右对称**（逐格对称：这些画面在红色方不会镜像），都是**正着**的画面（游戏不会转它们）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `norra_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）。**量画面大小时只量实心的形状，不要把柔光、光晕、零散噪点算进去**（上一次大招的门就因为光晕被缩小了），形状要填到每条写的大小。附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`；技能图标交付 `icons/norra_icon_*.png`（64 × 64）。都放在 `outputs/norra_fx2/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/norra_fx2_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「寄情琐物」 | 技能落地时在地上留下琐物，敌方英雄踩到，琐物飞到他身上爆开（伤害 + 线缕） | `p_trinkets` · `p_burst` |
| 被动里的 W「奇异旅程」 | 敌方英雄贴近时，诺拉在他脚下开门把他放逐 1.5 秒，然后吐回原地 | `w_in` · `w_lock` · `w_out` |
| 技能 1 =「回忆涌现」 | 蓄力后发射魔法弹，落点爆炸（上一份的球和爆炸）；挂线缕 | （已有） |
| 技能 2 =「思乡线缕」 | 目标两侧开门，线缕从两边射出、交织，伤害并挂线缕（减速、变大） | `e_threads` · `t_hit` · `t_mark` |
| 大招 =「传送门欢腾！」 | 目标脚下展开大裂隙，四波毛线球横穿，砸中的英雄减速 | `r_rift` · `r_yarn` · `r_hit` · `r_slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、门、线没有黑描边**（茶杯除外）。
- 颜色（按每条写的用）：
  - 金色花纹：`#FFFFFF`、`#FFF4C4`、`#FFD95A`、`#F2B12E`、`#C77A16`、`#7E4410`；
  - 紫色漩涡：`#F4E6FF`、`#C9A2FF`、`#9A62F0`、`#6A34D0`、`#3E1C8C`、`#22104E`；
  - 粉金星星：`#FFE8F4`、`#FF9CCB`、`#F05A9E`、`#B02A6E`；
  - 毛线：`#FFFFFF`、`#FFE8F4`、`#FF9CCB`、`#F05A9E`、`#8FF0F0`、`#44C8D2`、`#FFD95A`；
  - 回忆水晶：`#FFFFFF`、`#F4E6FF`、`#C9A2FF`、`#9A62F0`、`#6A34D0`；
- 地面上的圈（琐物脚下的光、门、裂隙）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

### 1. `norra_fx_p_trinkets.png`：寄情琐物：地上的琐物，4 帧循环

诺拉的技能落地时撒在地上的**琐物**（她带着的回忆小物件）：地上三个发着紫光的小东西——中间一个**小茶杯**，两边各一个**小水晶**（菱形、紫色发光），每个脚下一小圈淡紫色的光，几颗小星星一闪一闪（手游里是地上发紫光的小晶体，参考 `refs/wr_trinkets.jpg`）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet memory-crystal ramp (#FFFFFF, #F4E6FF, #C9A2FF, #9A62F0, #6A34D0), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: MEMORY TRINKETS ON THE GROUND, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three small keepsakes standing on the ground line 4 squares above the bottom: in the middle a tiny teacup (6 squares wide, white-and-violet porcelain with a gold rim and a 1-square near-black outline), at each side 14 squares out a small violet memory crystal (a diamond 4 wide and 7 tall, glowing, a white core); under each a faint violet glow ellipse; frames 1-4 the crystals pulsing and little gold stars twinkling in turn above them. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal 44:20 cells, image size 2816x320 (each cell 704x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `norra_fx_p_burst.png`：寄情琐物：琐物飞到敌人身上爆开，5 帧

敌方英雄踩到琐物：一颗紫色的回忆水晶**从上面飞落到他身上**，啪地炸成一团**粉紫色的光泡**和几颗小星星（手游里琐物炸开是粉色的光球，参考 `refs/wr_trinkets.jpg` 第一格）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet memory-crystal ramp (#FFFFFF, #F4E6FF, #C9A2FF, #9A62F0, #6A34D0), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410).
Effect: A TRINKET STRIKES, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the lower middle, not drawn: 1 a small violet memory crystal (4 wide, 6 tall) high in the cell; 2 the crystal dropping, a short violet streak above it; 3 a pink-violet bubble burst 12 squares across at the middle; 4 the bubble 16 across, thin, little gold stars flying out at mirrored places; 5 fading sparkles. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 5 equal 18:24 cells, image size 1440x384 (each cell 288x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `norra_fx_w_in.png`：奇异旅程：开门吸走，5 帧

诺拉把贴近的敌人**放逐到异空间**：他脚下一圈**粉橙色的门环**亮起（地面上的椭圆，手游参考 `refs/wr_w_banish.jpg` 82 秒那格），门里紫色的漩涡往上卷，把人整个吸进去（人被放逐后看不见了，所以这几帧可以盖住人的位置）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410).
Effect: A PORTAL SWALLOWS THE UNIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle (36 squares tall) with its feet on the ground line 6 squares above the bottom; it vanishes into this picture: 1 a thin pink-orange ring 18 wide and 6 tall on the ground under it; 2 the ring 26 wide, a violet swirl filling it; 3 a violet whirl rising from the ring to 36 squares tall, spiralling, covering the unit's place; 4 the whirl drawn down into the ring; 5 the ring flashing and shrinking. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 5 equal 30:46 cells, image size 2400x736 (each cell 480x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `norra_fx_w_lock.png`：奇异旅程：放逐中，门在原地转，4 帧循环

敌人被放逐的这段时间（1.5 秒），他原来站的地上留着一个**小小的紫色漩涡门**慢慢转，边上一圈粉橙色。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A HUMMING PORTAL ON THE GROUND, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a violet swirl ellipse 20 wide and 7 tall with a thin pink-orange rim; frames 1-4 the swirl turning and two tiny sparks orbiting. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal 24:12 cells, image size 1536x192 (each cell 384x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `norra_fx_w_out.png`：奇异旅程：被吐回来，4 帧

放逐结束，门把人**吐回原地**：一道紫色的光柱从地上的门里冲起来、一闪，人重新出现（人会出现在中间，所以中间留空），然后门合上。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410).
Effect: SPAT BACK OUT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit reappears in the middle (36 squares tall, feet on the ground line 6 squares above the bottom; its place left mostly empty): 1 the violet ground ring 24 wide flashing white; 2 a ring of violet light rising round the unit's place to its waist, sparks; 3 the light fading upward, small gold stars; 4 the ring on the ground shrinking to nothing. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal 30:46 cells, image size 1920x736 (each cell 480x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `norra_fx_e_threads.png`：思乡线缕：两侧开门、射出线缕，6 帧

E：目标的**左右两侧各开一个紫色的圆形门**（地上的椭圆，手游参考 `refs/wr_e_threads.jpg` 104 秒那格），短短一下后，**粉、青、金三色的毛线一样的线缕**从两个门里一起射出来，在中间交织穿过目标的位置，再慢慢散开。门之间 50 格左右。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a yarn ramp (#FFFFFF, #FFE8F4, #FF9CCB, #F05A9E, #8FF0F0, #44C8D2, #FFD95A), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410).
Effect: THREADS BETWEEN TWO PORTALS, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the target stands in the middle (not drawn); 1 two violet portal ellipses (10 wide and 4 tall, a gold rim) opening on the ground 25 squares to the left and right of the middle; 2 the portals glowing, rising into upright swirls 10 tall; 3 bright yarn threads (pink, teal and gold strands, 1 square thick, slightly wavy) shooting from both portals toward the middle at waist height; 4 the threads meeting and crossing over the middle, a white spark where they cross; 5 the threads loosening into curls; 6 the portals closing, the threads fading. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 76:30 cells, image size 7296x480 (each cell 1216x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `norra_fx_t_hit.png`：思乡线缕：被线缕打中，3 帧

被线缕打中：一圈粉、青色的线头一甩、一下白光。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a yarn ramp (#FFFFFF, #FFE8F4, #FF9CCB, #F05A9E, #8FF0F0, #44C8D2, #FFD95A).
Effect: A THREAD LASH, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white spark 4 squares across; 2 pink and teal thread ends whipping out 10 across at mirrored places; 3 the threads curling and fading. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `norra_fx_t_mark.png`：线缕印记：身上缠着线缕，6 帧循环

被挂上**线缕**的敌人（减速、变大、更好被打中）：身上松松地缠着几圈**粉、青、金色的线**（腰和膝盖），头顶一个小小的**紫色线团**慢慢转（手游里被缠住的人身上裹着紫色的漩涡线，参考 `refs/wr_e_threads.jpg` 100 秒那格）。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a yarn ramp (#FFFFFF, #FFE8F4, #FF9CCB, #F05A9E, #8FF0F0, #44C8D2, #FFD95A), a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E).
Effect: WRAPPED IN THREADS, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: two loose loops of yarn thread round the unit (pink, teal and gold strands, 1 square thick) - one at its waist 24 wide and 6 tall, one at its knees 20 wide - seen slightly from above (their back halves behind the unit's place), and a small violet yarn ball 5 squares across with a loose end floating over its head; frames 1-6 the loops slowly turning round and the ball bobbing. The middle (the body) left empty. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 26:42 cells, image size 2496x672 (each cell 416x672, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `norra_fx_r_rift.png`：传送门欢腾！：地上的大裂隙，6 帧循环

大招：目标脚下展开一个**巨大的粉紫色圆形裂隙**（地上的椭圆，横 70 格、纵 24 格）：一圈粉紫色发光的边，边上有金色的小花纹，里面淡淡的紫色漩涡，几颗小星星往上飘（手游参考 `refs/wr_r_rift.jpg`：整个圈子很大、粉紫色）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet portal ramp (#F4E6FF, #C9A2FF, #9A62F0, #6A34D0, #3E1C8C, #22104E), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410).
Effect: A GREAT RIFT ON THE GROUND, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a big ring 70 squares wide and 24 tall: its rim 2 squares thick, glowing pink-violet with small gold filigree curls along it, inside a faint violet swirl (a few thin curved streaks, mostly see-through - units stand on it); frames 1-6 the swirl slowly turning, the rim's glow running round it, little stars rising at mirrored places. Frames MUST fill 70 squares across. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 76:28 cells, image size 7296x448 (each cell 1216x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `norra_fx_r_yarn.png`：传送门欢腾！：一波毛线球，6 帧

每一波：**两个毛线球**（一个粉色、一个金黄色，都拖着一根线）从裂隙的**左右两头**滚着飞进来，在中间撞到一起，炸开成一团毛茸茸的线和小星星（手游参考 `refs/wr_r_rift.jpg` 118、122、128 秒那几格：粉色和金色的球横穿裂隙）。为了左右对称，两个球大小、位置对称（颜色可以一粉一金对称摆）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a yarn ramp (#FFFFFF, #FFE8F4, #FF9CCB, #F05A9E, #8FF0F0, #44C8D2, #FFD95A), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E), a gold filigree ramp (#FFFFFF, #FFF4C4, #FFD95A, #F2B12E, #C77A16, #7E4410).
Effect: TWO YARN BALLS CROSS THE RIFT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the balls fly at waist height (the middle of the cell's lower half): 1 two yarn balls 6 squares across (wound pink and gold strands, a few loose loops) at the far left and right edges, each trailing a thin thread; 2 the balls a third of the way in, spinning, the threads trailing behind them; 3 the balls two thirds in; 4 the balls meeting in the middle with a white-pink flash 12 across; 5 a fluffy burst of yarn curls and little gold stars 24 across; 6 the curls drifting down and fading. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 6 equal 76:40 cells, image size 7296x640 (each cell 1216x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `norra_fx_r_hit.png`：传送门欢腾！：被毛线球砸中，4 帧

被毛线球砸中：一团粉金色的毛线炸开、几个线头乱飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a yarn ramp (#FFFFFF, #FFE8F4, #FF9CCB, #F05A9E, #8FF0F0, #44C8D2, #FFD95A), a pink star ramp (#FFE8F4, #FF9CCB, #F05A9E, #B02A6E).
Effect: A YARN BALL HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink-gold yarn ball 6 squares across in the middle; 2 the ball bursting into loose curls 12 across with a white flash; 3 the curls flying out at mirrored places; 4 fading curls. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `norra_fx_r_slow.png`：传送门欢腾！：被缠住减速，4 帧循环

被第一个毛线球打中、减速 80% 的那一下：脚下缠着一团乱糟糟的**粉、青色毛线**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a yarn ramp (#FFFFFF, #FFE8F4, #FF9CCB, #F05A9E, #8FF0F0, #44C8D2, #FFD95A).
Effect: TANGLED FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a messy tangle of pink and teal yarn round the unit's feet 20 wide and 6 tall, a few loose ends; frames 1-4 the loose ends wiggling. everything is a YORDLE PORTAL MAGE'S whimsical magic as in Wild Rift: VIOLET portal swirls, GOLD filigree, little pink-gold STARS, soft YARN threads in pink, teal and gold; flat shades, crisp shapes; no smooth neon beams, no realistic fire or smoke.
Layout: one horizontal row of 4 equal 22:10 cells, image size 1408x160 (each cell 352x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

## 技能图标（3 个，64 × 64）

### `norra_icon_skill.png`：技能 1 图标「回忆涌现」

```text
A 64x64 pixel-art skill icon for a small tactics game, chunky square pixels, hard edges, no anti-aliasing, a 1-pixel dark frame, bright and readable at small size: a glowing violet memory orb wrapped in a gold filigree ring, little pink stars streaming from it to the right, on a deep violet background. Colours from the same violet, gold, pink and teal shades as the effects. No text.
```

### `norra_icon_skill2.png`：技能 2 图标「思乡线缕」

```text
A 64x64 pixel-art skill icon for a small tactics game, chunky square pixels, hard edges, no anti-aliasing, a 1-pixel dark frame, bright and readable at small size: two small violet portals at the left and right with bright pink, teal and gold threads crossing between them, on a deep violet background. Colours from the same violet, gold, pink and teal shades as the effects. No text.
```

### `norra_icon_ult.png`：大招图标「传送门欢腾！」

```text
A 64x64 pixel-art skill icon for a small tactics game, chunky square pixels, hard edges, no anti-aliasing, a 1-pixel dark frame, bright and readable at small size: a big pink-violet ring rift seen from above with two yarn balls (one pink, one gold) rolling across it, on a deep violet background. Colours from the same violet, gold, pink and teal shades as the effects. No text.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `norra_fx_p_trinkets` | view_effects `tft_norra_p_trinkets`（大表，落点，地面，z -1，不跟随；左右对称） | 44 × 20 |
| `norra_fx_p_burst` | view_effects `tft_norra_p_burst`（跟随目标，z 2；左右对称） | 18 × 24 |
| `norra_fx_w_in` | view_effects `tft_norra_w_in`（目标脚下，z 2，不跟随；左右对称） | 30 × 46 |
| `norra_fx_w_lock` | view_effects `tft_norra_w_lock`（放逐的位置，z 2，不跟随；左右对称） | 24 × 12 |
| `norra_fx_w_out` | view_effects `tft_norra_w_out`（放逐的位置，z 2，不跟随；左右对称） | 30 × 46 |
| `norra_fx_e_threads` | view_effects `tft_norra_e_threads`（大表，目标位置，z 2，不跟随；左右对称） | 76 × 30 |
| `norra_fx_t_hit` | view_effects `tft_norra_t_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `norra_fx_t_mark` | view_buffs `tft_norra_t_mark`（跟随目标，z 3；左右对称） | 26 × 42 |
| `norra_fx_r_rift` | view_effects `tft_norra_r_rift`（大表，落点，地面，z -2，不跟随；左右对称） | 76 × 28 |
| `norra_fx_r_yarn` | view_effects `tft_norra_r_yarn`（大表，落点，z 2，不跟随；左右对称） | 76 × 40 |
| `norra_fx_r_hit` | view_effects `tft_norra_r_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `norra_fx_r_slow` | view_buffs `tft_norra_r_slow`（跟随，脚下，z 3；左右对称） | 22 × 10 |

- 大表 `tft_norra_big`（p_trinkets、e_threads、r_rift、r_yarn），其余在 `tft_norra_fx`；全部断言左右对称。图标 -> `tft/icons/tft_norra_skill` / `_skill2` / `_ult`。
- 用 `pixel_1x/` 切格（import_norra_fx 的做法）；和 `raw/` 原稿对照读回，形状小了就从 raw/ 按 process_norra_fx.reread 的办法放大读回。
