# 迷失之牙 纳尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 24 张特效图。** 造型和动作已定（`design/gnar_idle.png`：左边迷你纳尔——橙色毛茸茸的小约德尔、大耳朵、骨头头盔、手里一把骨头回力标；右边巨型纳尔——弓着背的深红色巨兽、电光蓝毛刺、两根大獠牙、巨大的拳头）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），迷你 32 格高、31 格宽，巨型 44 格高、约 62 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/gnar_size.png`：迷你纳尔的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/gnar_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里纳尔自己的特效贴图（迷你和巨型两套），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**迷你的回力标是象牙色骨头，带白蓝色的风弧**；**怒气和变身是红橙色的火光、白热的闪光**；**巨型的拳头、石头、砸地是褐色尘土、灰色碎石和白色冲击闪光**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **实心的东西（回力标、石头、碎石）有 1 格近黑描边**，像人物一样；**光、风弧、尘土、烟、冲击波没有描边**。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（变身的前几帧除外，写在那一条里）。
> - **对称**：打中、脚下、地上、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（两种回力标、石头）**朝右飞、后面在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的；回力标转圈的几帧用横、竖、斜叉、弧光圈，每帧都上下对称）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `gnar_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/gnar_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/gnar_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 迷你扔小回力标（每第 3 下亢奋）；巨型一拳砸下 | `a_boom` · `a_hit` · `a_hyper` · `hyper` · `m_hit` |
| 被动「狂怒基因」 | 怒气满了身上冒怒火，变成巨型 / 变回迷你 | `full` · `tf_mega` · `tf_mini` |
| 技能 1 = Q | 迷你：回力标飞出去再飞回来、接住；巨型：扔大石头，石头停在地上可以捡回来 | `q_boom` · `q_hit` · `q_catch` · `q_slow` · `q_rock` · `q2_hit` · `q_rest` · `q_pick` · `q2_slow` |
| 技能 2 = E / W | 迷你：轻跳踩敌人的头弹起来；巨型：猛踏跳起来砸地，接痛殴双拳砸地晕眩前面的敌人 | `e_hit` · `c_slam` · `c_hit` · `w_quake` · `w_hit` |
| 大招「呐啊！」 | 巨型一吼把周围的敌人全掀飞 | `r_wave` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、风弧、尘土、烟、冲击波没有黑描边**；**回力标、石头、碎石有 1 格近黑描边**。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 怒气、变身的红橙火光：`#FFFFFF`、`#FFF2C8`、`#FFC46A`、`#FF8A2E`、`#E2451C`、`#9E2412`；
  - 回力标的象牙色骨头和棕色皮条：`#FFFDF2`、`#F4E8C4`、`#DCC48E`、`#B4935E`、`#7E6238`、`#4A3820`；
  - 回力标的白蓝风弧：`#FFFFFF`、`#E2F6FF`、`#A8DCFF`、`#62B0F0`、`#2E72C8`；
  - 褐色尘土：`#F6EDDC`、`#DCC8A4`、`#B89C70`、`#8A6E4A`、`#5A462E`、`#34281A`；
  - 灰色石头、碎石：`#ECEAE4`、`#C4C0B6`、`#96928A`、`#6C6862`、`#46423E`、`#262422`；
  - 巨型的电光蓝：`#F2FDFF`、`#A6F0FF`、`#4CC8FF`、`#1E86E8`、`#0E46A8`；
- 打中、爆发居中画，不旋转；地面上的圆（冲击波、尘土环、裂缝）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（24 张）

24 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：迷你普攻射程 42000，巨型的石头砸中半径 16000，猛踏半径 18000，大招半径 30000）。

### 1. `gnar_fx_a_boom.png`：迷你普攻：小回力标（弹道，循环），4 帧

迷你纳尔普攻扔出去的小回力标在空中旋转：象牙色的弯骨头，中间缠着棕色皮条，转起来带一圈白蓝色的弧线残影（参考 q_weapon、q_weapon_blur）。**朝右飞，残影在左边，上下严格对称**：4 帧循环里骨头分别是横着、竖着、两个斜着的叠影、一圈转动的弧光。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory bone ramp (#FFFDF2, #F4E8C4, #DCC48E, #B4935E, #7E6238, #4A3820) and a white-blue swoosh ramp (#FFFFFF, #E2F6FF, #A8DCFF, #62B0F0, #2E72C8).
Effect: A SMALL SPINNING BOOMERANG, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): 1 the ivory bone boomerang lying flat across the cell (8 squares long, 2 thick, brown leather wrapped round its middle, 1-square near-black outline); 2 the bone standing upright through the middle (the same bone turned a quarter); 3 the bone's two diagonals crossing (an X, the spin's blur); 4 a white-blue ring of motion arcs 8 across with the bone's ends as two ivory dots at left and right; each frame a short white-blue swoosh trail at the left.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); the boomerang's middle on the cell's middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `gnar_fx_a_hit.png`：迷你普攻：打中目标，3 帧

回力标打中目标：一下白色和象牙色的小闪光，几道短短的白蓝色弧线往外弹（参考 ba_hit、ba_hit_spike）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue swoosh ramp (#FFFFFF, #E2F6FF, #A8DCFF, #62B0F0, #2E72C8) and an ivory bone ramp (#FFFDF2, #F4E8C4, #DCC48E, #B4935E, #7E6238, #4A3820).
Effect: A SMALL BOOMERANG HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white four-pointed flash 6 squares across; 2 the flash 9 across with 4 short white-blue arcs flying out at mirrored diagonals and 2 ivory chips; 3 only the arcs further out, fading.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `gnar_fx_a_hyper.png`：亢奋：第 3 下的强化命中，4 帧

亢奋（W 被动）第 3 下打中：一圈橙红色的爆发，中间白色的芯，几颗黄色的小星星往外蹦，带一圈冲击波（参考 enrage_buf_star、ba_tar_centerflare、ba_crack_radial）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412).
Effect: A HYPER BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot core 4 across inside an orange flare 8 across; 2 a red-orange starburst 14 across with 6 small yellow-orange stars flung out at mirrored places; 3 an orange shock ring 16 across (1-2 squares thick), the stars further out; 4 the ring breaking into embers, two stars left, fading.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `gnar_fx_hyper.png`：亢奋：加速的时候（身上，循环），4 帧

亢奋加速时：迷你纳尔脚下两边几道橙黄色的速度线和小尘土，一闪一闪（参考 p_speed_trail、p_dust）。**只画在脚下的地面上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412) and a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A).
Effect: HYPER SPEED LINES at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (Mini Gnar stands in the middle, not drawn: 32 squares tall (his huge ears and skull cap included), 30 wide, only the bottom 8 squares used, his feet's area in the middle left EMPTY): on each side 3 short orange-yellow speed streaks (3-6 squares) along the ground and 2 small dust puffs; each frame the streaks slide outward and fade, new ones start near the feet.
Layout: one horizontal row of 4 equal 24:8 cells, image size 1536x128 (each cell 384x128, 16 px a square); centered across, the streaks' bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `gnar_fx_full.png`：狂怒基因：怒气满了（身上，循环），4 帧

怒气满、马上要变身的时候：迷你纳尔身上冒出一圈红橙色的怒火光焰和热气，几颗火星往上飘（参考 p_fur_red、p_radial、p_transform_hotpoint、z_glow_maroon）。**围着人画，身体位置留空**（只画外圈和头顶），**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412).
Effect: A RAGE AURA round a unit, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (Mini Gnar stands in the middle, not drawn: 32 squares tall (his huge ears and skull cap included), 30 wide, his body area left EMPTY): flickering red-orange flame tongues rising round his outline (3-6 squares tall, brighter at the top), white-hot sparks and small steam puffs rising above his head; each frame the tongues sway and the sparks climb 2 squares.
Layout: one horizontal row of 4 equal 34:36 cells, image size 2176x576 (each cell 544x576, 16 px a square); centered across, the flames' bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `gnar_fx_q_boom.png`：迷你 Q：大回力标（弹道，循环），4 帧

Q 扔出去的大回力标：和普攻一样的象牙色骨头回力标，大一倍，转起来一圈白蓝色的弧光更明显，后面一道白蓝色的风尾（参考 q_weapon、q_weapon_blur、q_rip_ani）。**朝右飞，风尾在左边，上下严格对称**，4 帧循环（横、竖、斜叉、弧光圈）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory bone ramp (#FFFDF2, #F4E8C4, #DCC48E, #B4935E, #7E6238, #4A3820) and a white-blue swoosh ramp (#FFFFFF, #E2F6FF, #A8DCFF, #62B0F0, #2E72C8).
Effect: A BIG SPINNING BOOMERANG, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): 1 the ivory bone boomerang flat across the cell (13 squares long, 3 thick, brown leather wrapped round its middle, 1-square near-black outline, a white glint); 2 the bone upright through the middle; 3 the bone's two diagonals crossing (the spin's blur); 4 a bright white-blue ring of motion arcs 13 across with the bone's ends as two ivory chunks at left and right; each frame a white-blue wind streak 5 squares long at the left.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); the boomerang's middle on the cell's middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `gnar_fx_q_hit.png`：迷你 Q：回力标打中，3 帧

大回力标打中敌人：一下白色闪光，一道交叉的白蓝色斩痕，几块碎屑（参考 q_hit、q_hit_dot）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue swoosh ramp (#FFFFFF, #E2F6FF, #A8DCFF, #62B0F0, #2E72C8) and an ivory bone ramp (#FFFDF2, #F4E8C4, #DCC48E, #B4935E, #7E6238, #4A3820).
Effect: A BOOMERANG STRIKE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 7 across; 2 two crossing white-blue slash arcs (an X 13 wide) over the flash, 4 ivory chips flying out at mirrored diagonals; 3 only the chips and two fading arc ends.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `gnar_fx_q_catch.png`：迷你 Q：接住回力标，3 帧

回力标飞回来、纳尔接住：一圈白蓝色的小闪光和一圈转动的弧线，像收回来时最后一转（参考 q_weapon_catch1）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue swoosh ramp (#FFFFFF, #E2F6FF, #A8DCFF, #62B0F0, #2E72C8).
Effect: A CATCH FLASH, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue ring of motion arcs 12 across closing in; 2 a bright white star flash 8 across at the middle with 4 tiny sparkles at mirrored places; 3 two small fading sparkles.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `gnar_fx_q_slow.png`：迷你 Q：被回力标减速（身上，循环），4 帧

被回力标减速：敌人头顶上一圈慢慢转的白蓝色小弧线（像被风卷住）。**只画在头顶上方**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue swoosh ramp (#FFFFFF, #E2F6FF, #A8DCFF, #62B0F0, #2E72C8).
Effect: A SLOW SWIRL above a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat white-blue ring of 4 short arcs (an ellipse 14 wide and 4 tall); each frame the arcs move a quarter round (mirrored left and right).
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered across, the ring in the cell's middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `gnar_fx_e_hit.png`：迷你 E：踩着敌人弹起来，3 帧

迷你纳尔从敌人头上弹起来：一下白蓝色的星形闪光（英雄联盟里是蓝色的星），几颗小星星和一小团尘土（参考 e_hitstar、e_dustcloud）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue swoosh ramp (#FFFFFF, #E2F6FF, #A8DCFF, #62B0F0, #2E72C8) and a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A).
Effect: A HOP BOUNCE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue four-pointed star flash 6 across; 2 the star 10 across, 4 small white-blue stars popping out at mirrored places, a small dust puff under it; 3 only the small stars and the puff, fading.
Layout: one horizontal row of 3 equal 16:14 cells, image size 768x224 (each cell 256x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `gnar_fx_m_hit.png`：巨型普攻：拳头砸中，4 帧

巨型纳尔一拳砸中：一大团白色冲击闪光，四周的褐色尘土和几块碎石飞出去（参考 gnarbig ba_rocks、ba_dot_tar、w_flashwhite）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A), a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422) and a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412).
Effect: A HEAVY PUNCH IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white impact flash 8 across with an orange rim; 2 a white-orange starburst 14 across, 4 grey rock chips (outlined) flying out at mirrored diagonals; 3 a brown dust cloud ring 18 across, the chips further out; 4 only drifting dust, fading.
Layout: one horizontal row of 4 equal 20:18 cells, image size 1280x288 (each cell 320x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `gnar_fx_q_rock.png`：巨型 Q：大石头（弹道，循环），4 帧

巨型纳尔扔出去的大石头：一块圆圆的灰色巨石，上面有裂纹和一点青苔，转着飞，后面拖一道褐色的尘土尾巴（参考 q_rock、q_swoosh、q_dirtbits）。**朝右飞，尘土尾在左边，上下严格对称**，4 帧循环（石头的裂纹转一圈）。实心的石头有 1 格近黑描边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422) and a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A).
Effect: A FLYING BOULDER, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round grey boulder 12 squares across at the right (cracks and chips drawn so the boulder looks the same turned upside down, 1-square near-black outline, a light top-left edge mirrored by a light bottom-left edge), each frame its cracks turned a step (rolling); a brown dust trail 6 squares long at its left with 2 small pebbles above and below (mirrored).
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); the boulder's middle on the cell's middle row, 6 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `gnar_fx_q2_hit.png`：巨型 Q：石头砸中，5 帧

石头砸中第一个敌人、周围都受伤：一大团白色冲击闪光，一圈褐色的尘土冲击波往外推，碎石飞溅（参考 q_hit_shock、q_rock_crater、q_dust_shadow）。**左右对称**，范围约 32 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A), a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422) and a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412).
Effect: A BOULDER SMASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 across; 2 a white-orange burst 18 across, 6 grey rock chips (outlined) flying out at mirrored places; 3 a brown dust shock ring 30 across and 10 tall (an ellipse seen from above), the chips at its rim; 4 the ring 32 across breaking into dust clouds; 5 only drifting dust, fading.
Layout: one horizontal row of 5 equal 34:24 cells, image size 2720x384 (each cell 544x384, 16 px a square); centered across, the ring's middle 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `gnar_fx_q_rest.png`：巨型 Q：落在地上的石头（3 秒，循环），4 帧

石头停下来以后落在地上等纳尔来捡：一块灰色巨石半埋在一小圈裂开的地面里，周围一点尘土慢慢落下，石头上偶尔闪一下（参考 q_rock、q_rock_crater、q_rockhud）。**左右对称**，4 帧循环（尘土落下、闪光）。实心的石头有 1 格近黑描边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422) and a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A).
Effect: A BOULDER RESTING ON THE GROUND, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a round grey boulder 11 squares across sitting in a small cracked dent in the ground (a flat ellipse 15 wide and 4 tall), 1-square near-black outline round the boulder; 1-2 a few dust specks settling round it; 3 a white glint on its top; 4 still.
Layout: one horizontal row of 4 equal 16:12 cells, image size 1024x192 (each cell 256x192, 16 px a square); centered across, the dent's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `gnar_fx_q_pick.png`：巨型 Q：捡回石头，3 帧

纳尔把石头捡回来：一团褐色的尘土扬起来，中间一下白色闪光（参考 q_dirtbits、p_dust）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A).
Effect: A PICK-UP PUFF, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 across low in the cell; 2 a brown dust puff 16 across rising around it, 4 pebbles at mirrored places; 3 the dust thinning and drifting up, fading.
Layout: one horizontal row of 3 equal 20:16 cells, image size 960x256 (each cell 320x256, 16 px a square); centered across, the puff's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `gnar_fx_q2_slow.png`：巨型 Q：被石头减速（身上，循环），4 帧

被石头砸中减速：敌人脚下一小圈翻起的碎土和小石子（参考 q_dirtbits）。**只画在脚下的地面上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A) and a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422).
Effect: STIRRED EARTH at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat brown dirt ellipse 16 wide and 3 tall with 4 pebbles bobbing at mirrored places; each frame the pebbles hop a square and dust drifts.
Layout: one horizontal row of 4 equal 18:6 cells, image size 1152x96 (each cell 288x96, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `gnar_fx_c_slam.png`：巨型 E：猛踏落地（地面冲击，大图），5 帧

巨型纳尔跳起来砸在地上：地面炸开一圈白色冲击波，一圈褐色尘土环往外推，地上裂开几道缝，碎石飞起来（参考 e_big_aoe_dustring、e_big_aoe_pebbles、e_land_hit、e_crackflash）。**左右对称**，范围约 44 格宽（从斜上方看的椭圆）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A), a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422) and a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412).
Effect: CRUNCH LANDING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash on the ground 16 across with 4 short cracks radiating from it; 2 a white-orange shock ring 30 across and 9 tall (an ellipse seen from above), 6 grey rock chips (outlined) flying up at mirrored places; 3 a brown dust ring 44 across and 14 tall rolling outward, the cracks glowing orange; 4 the dust ring breaking into clouds, the chips falling; 5 only fading dust and the cracks.
Layout: one horizontal row of 5 equal 48:26 cells, image size 3840x416 (each cell 768x416, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `gnar_fx_c_hit.png`：巨型 E：猛踏打中，3 帧

猛踏打中敌人：一下橙白色的闪光，一小团尘土（参考 gnarbig e_hitbubble、e_land_hit_spike）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412) and a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A).
Effect: A CRUNCH HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an orange-white flash 7 across; 2 the flash 11 across with a small dust puff under it and 2 chips at mirrored places; 3 only the dust, fading.
Layout: one horizontal row of 3 equal 16:14 cells, image size 768x224 (each cell 256x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `gnar_fx_w_quake.png`：巨型 W：痛殴砸地（围着他，大图），5 帧

巨型纳尔双拳砸地：以他为中心地面裂开放射状的大裂缝，裂缝里闪白光，一圈褐色尘土冲起来，碎石飞溅（参考 gnarbig w_cracks_radial、w_pow_area、w_dust、gnar w_groundcrack、w_impactpuffs）。**左右对称**，范围约 56 格宽（从斜上方看的椭圆），中间他站的地方留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A), a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422) and a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412).
Effect: WALLOP SMASH round a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (Mega Gnar stands in the middle, not drawn: 44 squares tall, about 62 wide (a hunched beast on his knuckles), only the ground drawn): 1 white flashes where his fists hit at both sides of the middle, 6 cracks radiating across the ground (an ellipse 40 wide and 12 tall); 2 the cracks 56 wide glowing white-orange, a brown dust wall bursting up 8 squares at the cracks' ends, 6 rock chips (outlined) flying at mirrored places; 3 the dust 12 tall rolling outward; 4 the dust settling, the cracks dimming; 5 only faint cracks and drifting dust.
Layout: one horizontal row of 5 equal 60:26 cells, image size 4800x416 (each cell 960x416, 16 px a square); centered across, the ellipse's middle 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `gnar_fx_w_hit.png`：巨型 W：痛殴打中、眩晕，5 帧

痛殴打中敌人：身上一下白色冲击闪光，然后头顶一圈转圈的黄色小星星（被打晕了）（参考 w_flashwhite、enrage_buf_star）。**人站在中间不画**，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412) and a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A).
Effect: A STUNNING BLOW, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a champion stands in the middle, not drawn: about 16 squares wide and 36 tall, its body area left EMPTY): 1 a white impact flash 10 across at the cell's middle height; 2 the flash 14 across with dust at its sides; 3 a ring of 5 small yellow stars appearing above the head (an ellipse 12 wide and 4 tall at the cell's top); 4 the stars a quarter round; 5 the stars another quarter round, dimmer.
Layout: one horizontal row of 5 equal 20:30 cells, image size 1600x480 (each cell 320x480, 16 px a square); centered across, the stars' ring 3 squares from the cell's top. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `gnar_fx_r_wave.png`：巨型 R：呐啊！冲击波（围着他，大图），6 帧

大招：巨型纳尔一吼把周围的敌人全掀飞：以他为中心一圈巨大的白色冲击波环往外推，地面碎石和尘土被卷起来，几道红橙色的爪痕状气浪往四周扫（参考 gnarbig r_aoe、r_distort、r_debris1、r_scratch、gnar r_rocks、r_trail）。**左右对称**，范围约 64 格宽（从斜上方看的椭圆）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412), a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A) and a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422).
Effect: A GNAR! SHOCKWAVE round a unit, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (Mega Gnar stands in the middle, not drawn: 44 squares tall, about 62 wide (a hunched beast on his knuckles), only the ground and the air round him drawn, his body area left EMPTY): 1 a white shock ring 24 across and 8 tall on the ground round him; 2 the ring 46 across, 4 red-orange claw-swipe gusts (curved streaks 10 long) sweeping outward at mirrored diagonals, rock chips (outlined) and dust lifting; 3 the ring 64 across and 20 tall, the gusts at its rim, debris flying outward; 4 the ring breaking into dust clouds; 5 the dust and debris settling; 6 faint dust only.
Layout: one horizontal row of 6 equal 70:40 cells, image size 6720x640 (each cell 1120x640, 16 px a square); centered across, the ellipse's middle 12 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `gnar_fx_r_hit.png`：巨型 R：被掀飞的敌人，4 帧

被呐啊掀飞的敌人：一下红橙白色的闪光，几道往外甩的气浪和碎石（参考 gnarbig r_land_hit、r_scratch）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412), a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A) and a grey rock ramp (#ECEAE4, #C4C0B6, #96928A, #6C6862, #46423E, #262422).
Effect: A THROWN IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a red-orange-white flash 8 across; 2 a burst 14 across with 4 curved gust streaks flung out at mirrored diagonals; 3 2 rock chips (outlined) and dust at mirrored places, the streaks fading; 4 only fading dust.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `gnar_fx_tf_mega.png`：变身：迷你变巨型（大图），6 帧

迷你纳尔怒气满变成巨型纳尔：先一团白热的光把他包住，然后炸开一大团红橙色的怒火、热气和飞起的红毛，最后烟散开露出巨型纳尔（参考 p_transform_white、p_transform_hotpoint、p_transform_zap_ani、p_fur_red、p_pop_rgba、p_radial）。**围着人画、中间留空不要盖住他**（第 1–3 帧可以盖住中间：那时他正在变），**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412).
Effect: A RAGE TRANSFORMATION, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small cub grows into the beast in the middle, not drawn: 32 tall at the start, 44 tall and 62 wide at the end): 1 a white-hot glow ball 20 across low in the middle; 2 the glow 32 across with red-orange zaps crackling round it; 3 a huge red-orange blast 60 across and 48 tall covering the middle, tufts of red fur flying out; 4 the blast opening into a ring of flame and steam round the edge (the middle clear), fur tufts further out; 5 the ring thinning into smoke puffs and sparks; 6 only a few drifting smoke puffs and sparks.
Layout: one horizontal row of 6 equal 72:56 cells, image size 6912x896 (each cell 1152x896, 16 px a square); centered across, the blast's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `gnar_fx_tf_mini.png`：变回：巨型变迷你（大图），5 帧

巨型纳尔变回迷你：一团白色的烟“噗”地炸开把他包住，烟散开时飘出几撮红毛（参考 p_pop_dust_rgba、p_transform_shrink_rgba、p_trans）。**左右对称**，5 帧（第 1–2 帧盖住中间）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flashes, swooshes, dust, smoke, rings or shockwaves; solid things - the boomerang, the boulder, rock chips - DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brown dust ramp (#F6EDDC, #DCC8A4, #B89C70, #8A6E4A, #5A462E, #34281A) and a red-orange rage ramp (#FFFFFF, #FFF2C8, #FFC46A, #FF8A2E, #E2451C, #9E2412).
Effect: A POOF BACK TO SMALL, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the beast shrinks back into the cub in the middle, not drawn): 1 a white smoke cloud 40 across and 36 tall puffing out over the middle; 2 the cloud 56 across, round billowy puffs; 3 the cloud opening (the middle clear), 4 small red fur tufts drifting; 4 the puffs thinning at the edge; 5 a few faint puffs only.
Layout: one horizontal row of 5 equal 60:46 cells, image size 4800x736 (each cell 960x736, 16 px a square); centered across, the cloud's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `gnar_fx_a_boom` | view_projectiles `league_gnar_a_boom`（跟着弹道转向；上下对称） | 10 × 10 |
| `gnar_fx_a_hit` | view_effects `league_gnar_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 12 × 12 |
| `gnar_fx_a_hyper` | view_effects `league_gnar_a_hyper`（跟随目标，z 2；左右对称） | 18 × 18 |
| `gnar_fx_hyper` | view_buffs `league_gnar_hyper`（跟随，画在人物下面 z -1；左右对称；循环） | 24 × 8 |
| `gnar_fx_full` | view_buffs `league_gnar_full`（跟随，画在人物上面 z 3；左右对称；循环） | 34 × 36 |
| `gnar_fx_q_boom` | view_projectiles `league_gnar_q_boom` 和 `q_back`（飞出去和飞回来都用；跟着弹道转向；上下对称） | 16 × 16 |
| `gnar_fx_q_hit` | view_effects `league_gnar_q_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `gnar_fx_q_catch` | view_effects `league_gnar_q_catch`（跟随纳尔，z 3；左右对称） | 16 × 16 |
| `gnar_fx_q_slow` | view_buffs `league_gnar_q_slow`（跟随，z 3；左右对称；循环） | 16 × 8 |
| `gnar_fx_e_hit` | view_effects `league_gnar_e_hit`（跟随目标，z 2；左右对称） | 16 × 14 |
| `gnar_fx_m_hit` | view_effects `league_gnar_m_hit`（跟随目标，z 2；左右对称） | 20 × 18 |
| `gnar_fx_q_rock` | view_projectiles `league_gnar_q_rock`（跟着弹道转向；上下对称） | 18 × 16 |
| `gnar_fx_q2_hit` | view_effects `league_gnar_q2_hit`（不跟随，z 2；左右对称） | 34 × 24 |
| `gnar_fx_q_rest` | view_effects `league_gnar_q_rest`（不跟随，画在人物下面 z -1；左右对称） | 16 × 12 |
| `gnar_fx_q_pick` | view_effects `league_gnar_q_pick`（跟随纳尔，z 3；左右对称） | 20 × 16 |
| `gnar_fx_q2_slow` | view_buffs `league_gnar_q2_slow`（跟随，画在人物下面 z -1；左右对称；循环） | 18 × 6 |
| `gnar_fx_c_slam` | view_effects `league_gnar_c_slam`（不跟随，画在人物下面 z -1；左右对称） | 48 × 26 |
| `gnar_fx_c_hit` | view_effects `league_gnar_c_hit`（跟随目标，z 2；左右对称） | 16 × 14 |
| `gnar_fx_w_quake` | view_effects `league_gnar_w_quake`（跟随纳尔，画在人物下面 z -1；左右对称） | 60 × 26 |
| `gnar_fx_w_hit` | view_effects `league_gnar_w_hit`（跟随目标，z 3；左右对称） | 20 × 30 |
| `gnar_fx_r_wave` | view_effects `league_gnar_r_wave`（不跟随，画在人物下面 z -1；左右对称） | 70 × 40 |
| `gnar_fx_r_hit` | view_effects `league_gnar_r_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `gnar_fx_tf_mega` | view_effects `league_gnar_tf_mega`（跟随纳尔，画在人物上面 z 3；左右对称） | 72 × 56 |
| `gnar_fx_tf_mini` | view_effects `league_gnar_tf_mini`（跟随纳尔，z 3；左右对称） | 60 × 46 |

- 两张表：`asset/league/effects/league_gnar_fx`（小的）和 `league_gnar_big`（c_slam、w_quake、r_wave、tf_mega、tf_mini），tag = 名字（build_gnar.py 的 views；q_back 用 q_boom 的帧）。
- 弹道图（a_boom、q_boom、q_rock）断言上下对称，其余断言左右对称；q2_hit、q_rest、c_slam、r_wave 不跟随（落点）；w_quake 是新加的CasterViewEffect（痛殴砸地那一 tick）。
- q_rest 循环到 pick_t（3 秒）；full、hyper、q_slow、q2_slow 是 buff 循环。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（回力标、石头、碎石的描边保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
