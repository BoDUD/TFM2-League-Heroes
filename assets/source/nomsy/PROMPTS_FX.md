# 诺姆希：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图 + 3 个技能图标。** 造型已定（`design/nomsy_design.png`：四肢着地蹲坐的胖小龙，粉色大圆肚子和粉色的脸、绿眼睛、白獠牙、头顶三根紫刺，深紫蓝的背鳞，紫红翼膜的翅膀，短粗的尾巴）。诺姆希在游戏里是**高清**的（每个游戏格子里约 2.6×2.6 个细像素），36 格高、50 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/nomsy_size.png`：诺姆希缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里诺姆希自己的特效贴图和英雄联盟里斯莫德、小龙的火焰贴图（**灰色的形状，游戏里再染色**：火球、爆炸、喷火、火球雨、烟和火星），按用在我们哪张特效分好了行。只在本地用。
> - **诺姆希是一只小火龙，特效都是龙火**：圆滚滚的**火球**（白黄的芯、橙红的火舌）、翻滚的火焰、火星和一点黑烟，龙的魔法带一点她自己的**洋红紫色**（翅膀翼膜的颜色）；不要蓝色，不要闪电，不要符文，不要光滑的霓虹光束。
> - **特效要亮**：每团火都有最亮一档或白黄色的芯，暗底上一眼能看见。**火、光、烟没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：画在人身上和地上的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；**四张飞行的画面（a_bolt、q_ball、q_bounce、e_flame）朝右、严格上下对称**（游戏会按飞行方向转）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nomsy_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `nomsy_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/nomsy_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/nomsy_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「龙神之躯」 | 龙的生命值；血量低于 40% 时每秒回复最大生命值的 3% | `p_heal` |
| 普攻 | 张嘴吐一颗小火团 | `a_bolt` · `a_hit` |
| 技能 1 =「火球！」 | 跳起来吼一声，朝目标抛出大火球，落地爆炸伤害周围的敌人，再弹出两颗小火球打附近别的敌人 | `q_ball` · `q_hit` · `q_bounce` · `q_bounce_hit` |
| 技能 2 =「龙息」 | 往后一仰、张大嘴往前喷出扇形火焰：伤害、灼烧、降低魔抗 | `e_flame` · `e_burn` |
| 大招 =「龙神飞升」 | 展开翅膀飞上天盘旋（减伤、免控），十颗火球从天而降砸向随机敌人；落地后几秒内攻速、法强提高 | `r_fly` · `r_fall` · `r_hit` · `r_up` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、烟没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 龙火（火球、火焰、火星）：`#FFFBE0`、`#FFE27A`、`#FFB23A`、`#FF7A1E`、`#E0431A`、`#8E1E12`；
  - 她的洋红紫（龙火光、鳞片光、图标边框）：`#FFE0F4`、`#FF9AD8`、`#E84CB4`、`#A82C8E`、`#5E1A62`；
  - 回血的绿光：`#F6FFE8`、`#C8F58A`、`#7EDB5A`、`#3A9E46`；
  - 黑烟：`#E6DAD2`、`#A8968E`、`#6A5A5A`、`#3A3036`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `nomsy_fx_a_bolt.png`：普攻：小火团飞行中，4 帧循环

她吐出来的**小火团**：一颗圆圆的小火球在右边（白黄的芯、橙色外圈），后面拖着一小截往左飘的火尾巴和一两点火星。**朝右、上下对称**（游戏会按飞行方向转），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036).
Effect: A LITTLE FIRE BOLT IN FLIGHT, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): at the RIGHT a round fireball 6 squares across (a white-yellow core, orange, a red-orange rim), behind it to the LEFT a short licking flame tail 6 squares long tapering to a point, one or two embers; frames 1-4 the flames flickering. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `nomsy_fx_a_hit.png`：普攻：小火团打中，4 帧

小火团打中：一下白黄色的小火花，一圈橙色的小火焰往两边炸开，几点火星，最后一缕小黑烟。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036).
Effect: A LITTLE FIRE POP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares across; 2 a small burst of orange flame tongues out to both sides (mirrored) 12 squares across, a few embers; 3 the flames smaller, the embers farther; 4 a little soot puff fading. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `nomsy_fx_q_ball.png`：火球！：大火球飞行中，6 帧循环

她抛出去的**大火球**：一个胖胖的圆火球在右边（大大的白黄芯，橙色和红橙的火焰往后舔），后面拖着一条往左的火焰尾巴和一缕黑烟，外圈夹着一点洋红色的龙火光。**朝右、上下对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a magenta-violet dragon ramp (#FFE0F4, #FF9AD8, #E84CB4, #A82C8E, #5E1A62), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036).
Effect: A BIG FIREBALL IN FLIGHT, 6 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): at the RIGHT a fat round fireball 12 squares across (a big white-yellow core, orange, red-orange flames licking backwards, a thin magenta glint at its rim), behind it to the LEFT a fire tail 10 squares long with a soot streak; frames 1-6 the flames rolling and flickering. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 22:16 cells, image size 2112x256 (each cell 352x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `nomsy_fx_q_hit.png`：火球！：大火球爆炸，7 帧

大火球落地爆炸：先一下白黄色的大闪光，然后一大团**橙红色的火焰**往上翻滚、往两边炸开，脚下一圈火焰冲击环（地上的扁椭圆），飞出几颗火星，最后一团黑烟往上散。这是 Q 的主角。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036), a magenta-violet dragon ramp (#FFE0F4, #FF9AD8, #E84CB4, #A82C8E, #5E1A62).
Effect: A FIREBALL EXPLOSION, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 16 squares across in the lower middle; 2 a ball of fire 26 squares across billowing up, a ring of flame on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 36 squares wide at the bottom; 3 the fire 34 squares across and 28 tall, flame tongues and embers flying out to both sides (mirrored), the ground ring 42 wide; 4 the fire at its biggest, a few magenta sparks in it; 5 the fire breaking up into tongues, soot smoke rising at the top; 6 the smoke cloud, small flames at the bottom; 7 the last smoke. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 7 equal 44:34 cells, image size 4928x544 (each cell 704x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `nomsy_fx_q_bounce.png`：火球！：弹出去的小火球，4 帧循环

爆炸后弹出去的**小火球**：比大火球小一号、比普攻的小火团亮一点（芯更白），后面一截短火尾。**朝右、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a magenta-violet dragon ramp (#FFE0F4, #FF9AD8, #E84CB4, #A82C8E, #5E1A62).
Effect: A SMALL BOUNCING FIREBALL IN FLIGHT, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): at the RIGHT a round fireball 6 squares across with a bright white core, orange flames, one magenta glint, behind it to the LEFT a short flame tail 6 squares long; frames 1-4 flickering. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `nomsy_fx_q_bounce_hit.png`：火球！：小火球打中，4 帧

弹出去的小火球打中：一个比普攻打中大一点的小火焰爆开，带一圈火星。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036).
Effect: A SMALL FIREBALL HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 8 squares across; 2 a burst of orange flame 14 squares across, embers out to both sides (mirrored); 3 the flame breaking up; 4 a soot puff fading. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `nomsy_fx_e_flame.png`：龙息：喷出的火焰，6 帧循环

她张大嘴喷出来的**龙息**：从格子**左边中间**（她的嘴）喷出，往右越喷越宽，像一个横放的喇叭；中心白黄、外圈橙红，前端翻滚着一团团火舌和几缕黑烟，夹着几点洋红色的龙火星。**朝右、上下对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a magenta-violet dragon ramp (#FFE0F4, #FF9AD8, #E84CB4, #A82C8E, #5E1A62), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036).
Effect: A DRAGON'S FIRE BREATH, 6 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): the fire starts at the LEFT EDGE of the cell, in the middle of its height (her mouth), and roars out to the RIGHT, widening like a horizontal cone: 4 squares tall at the left edge, 18 squares tall at the right end; a white-yellow core along the middle, orange around it, red-orange puffy flame tongues at the edges, rolling fire puffs and a few soot wisps at the far right end, a few magenta sparks; frames 1-6 the puffs rolling forward and flickering. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 48:20 cells, image size 4608x320 (each cell 768x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `nomsy_fx_e_burn.png`：龙息：被灼烧，6 帧循环

被龙息烧着的人身上（灼烧、减魔抗）：几簇**小火苗**从身上往上窜，带着几点火星和一缕烟，脚边一点烧焦的黑灰。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036).
Effect: A UNIT ON FIRE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: three or four small flame tufts (3-5 squares tall) licking up at mirrored places over the body area, embers rising, a thin soot wisp above, a little scorch dark at the feet; frames 1-6 the flames flickering and swapping heights. Small and light: the unit stays visible. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 16:24 cells, image size 1536x384 (each cell 256x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `nomsy_fx_r_fall.png`：龙神飞升：从天而降的火球，7 帧

火球雨的一颗：一个大火球从**格子最上面笔直往下掉**（火尾巴朝上），最后一帧砸到格子底部（人的脚下）炸开一小团火。竖着画，**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a magenta-violet dragon ramp (#FFE0F4, #FF9AD8, #E84CB4, #A82C8E, #5E1A62), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036).
Effect: A FIREBALL FALLING FROM THE SKY, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the target stands at the bottom of the cell, not drawn: a round fireball 10 squares across (a white-yellow core, orange, red-orange, a magenta glint) falling STRAIGHT DOWN, its flame tail pointing straight UP behind it (8-14 squares long): 1 at the very top; 2-5 lower and lower, the tail longer; 6 at the bottom, touching down; 7 a small burst of flame at the bottom. Upright, never tilted. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 7 equal 18:56 cells, image size 2016x896 (each cell 288x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `nomsy_fx_r_hit.png`：龙神飞升：火球砸中，6 帧

火球雨砸到人：脚下一下白黄色的闪光，一团火焰往上翻起、往两边炸开，地上留一圈烧焦的火痕，再升起一团黑烟。比 Q 的爆炸小一号。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a soot smoke ramp (#E6DAD2, #A8968E, #6A5A5A, #3A3036).
Effect: A FIREBALL IMPACT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 12 squares across at the bottom middle; 2 a burst of fire 24 squares across rising, a flame ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 30 squares wide; 3 flame tongues and embers out to both sides (mirrored); 4 the fire breaking up, a scorch ring on the ground; 5 soot smoke rising; 6 the last smoke. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 34:26 cells, image size 3264x416 (each cell 544x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `nomsy_fx_r_fly.png`：龙神飞升：她在天上时地上的火光，6 帧循环

她飞在天上盘旋的时候：地上（她的正下方）一圈**橙红色的火光圈**一明一暗，圈里有几点火星往上飘——标出她在哪。画在**地上**（扁椭圆），中心在格子中间。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12), a magenta-violet dragon ramp (#FFE0F4, #FF9AD8, #E84CB4, #A82C8E, #5E1A62).
Effect: A FIERY GLOW UNDER A FLYING DRAGON, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred in the cell: a ring of orange-red fire glow 48 squares wide and 14 tall with a soft magenta inner edge, its brightness pulsing; a few embers drifting up from it at mirrored places; frames 1-6 the pulse and the embers rising. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 52:16 cells, image size 4992x256 (each cell 832x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `nomsy_fx_r_up.png`：龙神飞升：落地后的飞升光环，6 帧循环

落地后飞升状态（攻速、法强提高）：身体外面一圈**洋红色和金色的龙火光焰**往上飘，像龙神的气焰，几点金色火星绕着她转。身体位置留空，只画外圈。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-violet dragon ramp (#FFE0F4, #FF9AD8, #E84CB4, #A82C8E, #5E1A62), a dragon fire ramp (#FFFBE0, #FFE27A, #FFB23A, #FF7A1E, #E0431A, #8E1E12).
Effect: AN ASCENDED DRAGON'S AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the chubby dragon stands in the middle, not drawn: 49 squares wide and 36 tall: flame-shaped wisps of magenta and golden dragon fire rising round her outline (an outline 54 squares wide and 42 tall, 2-3 squares thick, only the edge), a few golden embers circling at mirrored places; frames 1-6 the wisps rising and fading in turn. The middle (the body) left empty. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:44 cells, image size 5376x704 (each cell 896x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `nomsy_fx_p_heal.png`：龙神之躯：低血时回血，6 帧

血量低时龙神之躯回血：她身上冒起几片**绿色的小光点和小十字**往上飘，外圈一圈淡淡的洋红色龙鳞光（像鳞片一闪一闪）。身体位置留空。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fresh green healing ramp (#F6FFE8, #C8F58A, #7EDB5A, #3A9E46), a magenta-violet dragon ramp (#FFE0F4, #FF9AD8, #E84CB4, #A82C8E, #5E1A62).
Effect: A DRAGON BODY MENDING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the chubby dragon stands in the middle, not drawn: 49 squares wide and 36 tall: small fresh green motes and little green plus-crosses (2-3 squares) rising from her at mirrored places; round her outline a faint ring of magenta dragon-scale glints (tiny scale shapes flashing); 1 the glints appearing; 2-4 the motes and crosses rising; 5 the glints fading; 6 the last motes at the top. The middle (the body) left empty. everything is a BABY DRAGON's fire: round puffy FIREBALLS with a white-yellow core and orange-red licking flames, curling fire tongues, embers and a little soot smoke, touches of her own MAGENTA-VIOLET (her wing membranes) in the dragon's magic; flat shades, cute chunky shapes; no blue, no lightning, no runes, no smooth neon beams.
Layout: one horizontal row of 6 equal 52:44 cells, image size 4992x704 (each cell 832x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `nomsy_icon_skill.png`：技能 1「火球！」图标

火球！：一个大火球从左上往右下飞来，右下角已经炸开，弹出两颗小火球。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta dragon-scale corners, a deep warm maroon inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big round FIREBALL flying in from the upper left with a fire tail, at the lower right a burst of flame with two small fireballs bouncing out of it. No text, no letters.
```

### 图标 2. `nomsy_icon_skill2.png`：技能 2「龙息」图标

龙息：左边一张粉色的小龙大嘴（白獠牙），往右喷出一大片扇形的火焰。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta dragon-scale corners, a deep warm maroon inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: at the left a chubby pink baby dragon's wide open mouth with two white tusks, a big cone of fire breath roaring out of it to the right. No text, no letters.
```

### 图标 3. `nomsy_icon_ult.png`：大招「龙神飞升」图标

龙神飞升：一对展开的紫红色龙翼在上面，下面几颗火球往下落。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta dragon-scale corners, a deep warm maroon inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a pair of spread magenta-violet DRAGON WINGS at the top, three fireballs with upward fire tails falling down below them. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `nomsy_fx_a_bolt` | view_projectiles `tft_nomsy_a_bolt`（飞向目标，随飞行方向旋转；上下对称、朝右） | 12 × 8 |
| `nomsy_fx_a_hit` | view_effects `tft_nomsy_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `nomsy_fx_q_ball` | view_projectiles `tft_nomsy_q_ball`（大表，抛物线飞向目标，随飞行方向旋转；上下对称、朝右） | 22 × 16 |
| `nomsy_fx_q_hit` | view_effects `tft_nomsy_q_hit`（大表，在被炸到的人身上，z 3；左右对称） | 44 × 34 |
| `nomsy_fx_q_bounce` | view_projectiles `tft_nomsy_q_bounce`（tft.dll 从爆炸处飞向别的敌人，随方向旋转；上下对称、朝右） | 12 × 8 |
| `nomsy_fx_q_bounce_hit` | view_effects `tft_nomsy_q_bounce_hit`（tft.dll 播，跟随目标，z 2；左右对称） | 16 × 16 |
| `nomsy_fx_e_flame` | view_projectiles `tft_nomsy_e_flame`（大表，一道从她嘴边指向目标的线，随方向旋转；上下对称、朝右） | 48 × 20 |
| `nomsy_fx_e_burn` | view_buffs `tft_nomsy_e_burn`（跟随被烧的人，身上，z 3；左右对称） | 16 × 24 |
| `nomsy_fx_r_fall` | view_effects `tft_nomsy_r_fall`（大表，在被砸的人身上，不旋转，z 3；左右对称） | 18 × 56 |
| `nomsy_fx_r_hit` | view_effects `tft_nomsy_r_hit`（大表，在被砸的人身上，z 3；左右对称） | 34 × 26 |
| `nomsy_fx_r_fly` | view_buffs `tft_nomsy_r_fly`（跟随她，脚下地面，z -1；左右对称） | 52 × 16 |
| `nomsy_fx_r_up` | view_buffs `tft_nomsy_r_up`（跟随她，z 3；左右对称） | 56 × 44 |
| `nomsy_fx_p_heal` | view_buffs `tft_nomsy_p_heal`（tft.dll 挂，跟随她，z 3；左右对称） | 52 × 44 |
| `nomsy_icon_skill` | skill_icons[0] `asset/tft/icons/tft_nomsy_skill` | 64 × 64 |
| `nomsy_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_nomsy_skill2` | 64 × 64 |
| `nomsy_icon_ult` | skill_icons[2] `asset/tft/icons/tft_nomsy_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_nomsy_fx`（小的）和 `tft_nomsy_big`（q_ball、q_hit、e_flame、r_fall、r_hit），tag = 名字。
- a_bolt、q_ball、q_bounce、e_flame 断言上下对称（朝右），其余断言左右对称。
- q_bounce、q_bounce_hit、p_heal 由 tft.dll 播（小火球从爆炸处生成、低血回血挂的 buff）；e_flame 是从她嘴边出发的一条只有画面的线（它的左端对着她的嘴）；r_fall 是 ViewEffect（不旋转），r_fall_t tick 后才是 r_hit。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
