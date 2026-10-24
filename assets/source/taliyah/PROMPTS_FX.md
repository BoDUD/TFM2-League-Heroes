# 岩雀 塔莉垭：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型已定（`design/taliyah_design.png`：小麦色皮肤的恕瑞玛少女，往上盘起的棕色大头发和金色发饰，米白石片披肩，深靛紫上衣和金边，红色长外套和两条挂灰石头的垂带，棕色长靴；移动时蹲在一块裹着红布的大石头上冲浪）。她在游戏里是**高清**的（每个游戏格子里约 1.75×1.75 个细像素），40 格高、20 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/taliyah_size.png`：塔莉垭放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里塔莉垭自己的特效贴图（大多是灰度的形状），按用在我们哪张特效分好了行，只在本地用。**塔莉垭是织石者**：她的东西都是**有棱角的砂岩石头**（暖黄褐色，亮面是浅沙色），被她「编织」过的大地有**细细的金色丝线和发光的金色裂缝**（恕瑞玛的金色），再加**浅色的沙尘**；不要火、不要电、不要光滑的霓虹光束、不要魔法亮点。
> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。
> - **沙尘、光、冲击波、金线都没有黑描边**（用它自己最深的一档）；石头可以用它自己最深的棕色勾边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`a_rock`、`q_rock`、`q_boulder`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - **持续的画面**（掘石场 8 秒、石雷阵 4 秒、石墙 5 秒）只画几帧：开头、中间循环的几帧、结尾，Claude 导入时按时长拉开循环。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `taliyah_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/taliyah_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/taliyah_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 甩出一块小石子 | `a_rock` · `a_hit` |
| 被动「浮石冲」 | 不在战斗中时踩着大石头冲浪加速（移动动作就是冲浪）；放完大招也冲浪加速 | `surf` |
| 技能 1 =「石穿」 | 朝一个方向连射 5 颗石头，脚下留下一块掘石场；站在掘石场上再放，就扔出一颗大石头（减速） | `q_rock` · `q_hit` · `q_ground` · `q_boulder` · `q_big_hit` · `slow` |
| 技能 2 =「岩突」+「撒石阵」 | 先在目标处撒一片石雷（减速），地面隆起把敌人往她这边掀，穿过雷区时石雷炸开把人晕住 | `e_mines` · `w_erupt` · `w_hit` · `e_blast` · `slow` |
| 大招 =「墙幔」 | 在目标处竖起一道很长的石墙，墙上的人被拖到她这边，碰到墙就走不动；接着马上一个岩突把人推到墙上撞晕 | `r_wall` · `w_erupt` · `e_blast` · `slow` |

连招：**岩突把人掀过雷区 → 眩晕**，**掘石场上再放石穿 → 大石头**，**墙幔 → 马上岩突推到墙上撞晕**，**放完墙幔冲浪加速**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**沙尘、光、冲击波、金线没有黑描边**；石头用它自己最深的棕色勾边，不要黑边。
- 每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的亮点。
- 颜色（按每条写的用）：
  - 砂岩·黄褐：`#F4E2BC`、`#DABE8C`、`#B8945E`、`#8C6A40`、`#624628`、`#3C2A18`；
  - 灰石：`#E8E4DC`、`#BAB4A8`、`#8C867A`、`#605A52`、`#3A3632`；
  - 编织的金线·金：`#FFF6C8`、`#FFE07A`、`#F2B83C`、`#C8862A`、`#8A5418`；
  - 沙尘·浅沙：`#F6ECD4`、`#E2D0A8`、`#C4AE84`、`#9A8662`、`#6E6046`；
  - 闪光·白金：`#FFFFFF`、`#FFF8E4`、`#FFE8B0`；
- 打中、爆发居中画，不旋转；地面上的东西（掘石场、石雷阵、裂缝、脚下的沙尘）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `taliyah_fx_a_rock.png`：普攻：飞出去的小石子，4 帧循环

普攻甩出的一块小石头（参考 q_stone_mis、x_small_stone）：一块棱角分明的砂岩小石子，转着往前飞，后面拖一缕淡淡的沙尘。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A SPINNING PEBBLE, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): an angular sandstone pebble 4 squares across with a pale sandy highlight, its facets turning frame to frame, a thin streak of pale dust trailing on the left. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 4 equal 8:6 cells, image size 512x96 (each cell 128x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `taliyah_fx_a_hit.png`：普攻：石子打中，3 帧

小石子打中敌人：一下白金色的闪光，石子碎成几块小碎石往外溅，一小团沙尘。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold flash ramp (#FFFFFF, #FFF8E4, #FFE8B0), a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A PEBBLE SHATTERING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold impact flash 5 squares across; 2 the pebble bursting into four or five small sandstone chips flying out at mirrored places, a puff of pale dust 10 across; 3 the chips further out and smaller, the dust fading. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `taliyah_fx_q_rock.png`：石穿：一串石头里的一颗，4 帧循环

石穿射出的石头（参考 q_stone_mis、q_rocks_2x2、q_trail）：一块比普攻大一点的尖头砂岩石块，前面尖、后面拖一条金色的细线和沙尘（像被线串着的石头）。**朝右飞、上下对称**，4 帧循环。一次会连着射出 5 颗。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a woven gold ramp (#FFF6C8, #FFE07A, #F2B83C, #C8862A, #8A5418), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A THREADED ROCK, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a pointed sandstone rock 6 squares long and 4 tall, its point to the right, a pale highlight on its upper and lower faces alike, a thin GOLDEN thread streaming behind it on the left with two small dust puffs; the rock's facets and the thread's flicker change frame to frame. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `taliyah_fx_q_hit.png`：石穿：石头打中，3 帧

石穿的石头打中敌人（参考 q_hit_dust、q_hit_ring）：白金色的闪光，石头砸碎成几块，一圈沙尘往外。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold flash ramp (#FFFFFF, #FFF8E4, #FFE8B0), a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A ROCK STRIKE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 6 squares across with a short cross of light; 2 a ring of pale dust 12 across, sandstone chips flying out at mirrored places; 3 the chips falling, the dust fading. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `taliyah_fx_q_boulder.png`：石穿（掘石场上）：一颗大石头，4 帧循环

在掘石场上放石穿：扔出**一颗大圆石头**（参考 q_mis_slow_reaper_glow、r_rock_main）：比普通的石头大好几倍，砂岩表面有几道发光的金色裂纹，滚着往前飞，后面拖一大团沙尘和几块碎石。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a woven gold ramp (#FFF6C8, #FFE07A, #F2B83C, #C8862A, #8A5418), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A BIG BOULDER, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round sandstone boulder 12 squares across with flat facets and two or three glowing GOLDEN cracks, rolling - its facets and cracks turning frame to frame; behind it on the left a wide plume of pale dust 10 squares long and a few small rock chips at mirrored places above and below. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 4 equal 22:16 cells, image size 1408x256 (each cell 352x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `taliyah_fx_q_big_hit.png`：石穿（大石头）：砸中，4 帧

大石头砸中敌人：一下大的白金色闪光，大石头碎成好几块大碎石往外飞，一圈沙尘冲开，脚下溅起尘土（被减速）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold flash ramp (#FFFFFF, #FFF8E4, #FFE8B0), a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A BOULDER SMASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 10 squares across; 2 the boulder breaking into six chunky sandstone pieces flying out at mirrored places, a ring of dust 18 across; 3 the pieces further out, dust spraying up from the feet on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 4 small chips and settling dust, fading. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 22:20 cells, image size 1408x320 (each cell 352x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `taliyah_fx_q_ground.png`：掘石场：她脚下被翻过的地，6 帧（约 8 秒）

掘石场（参考 q_aoe_ring、q_craterobsi_tremors、p_down_move_crack）：塔莉垭放过石穿的地方，**地面被翻过一圈**——一个扁扁的椭圆，里面是裂开的砂岩地面和散落的小石子，裂缝里透出淡淡的金色。第 1 帧裂开（亮），2–5 帧躺着（裂缝里的金光一闪一闪，这四帧循环），6 帧变暗消失。**左右对称**，6 帧。贴着地，很扁。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a woven gold ramp (#FFF6C8, #FFE07A, #F2B83C, #C8862A, #8A5418).
Effect: WORKED GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat ellipse of freshly cracked sandstone ground 28 squares wide and 8 tall on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), bright golden light in its cracks, small pebbles lifted at mirrored places; 2, 3, 4 and 5 the same patch lying still, scattered pebbles on it, the gold in the cracks pulsing gently - brighter, then dimmer (frames 2-5 loop); 6 the patch darker, the gold gone, fading. Flat on the ground, never rising above 10 squares. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 6 equal 30:10 cells, image size 2880x160 (each cell 480x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `taliyah_fx_e_mines.png`：撒石阵：地上一片石雷，8 帧（约 4 秒）

撒石阵的雷区（参考 e_stone_mine、e_decal、e_rocks_2x2）：地上一大片**散开的石雷**——十来颗圆圆的砂岩石块，每颗中间一道发光的金色裂缝，下面一块扁扁的翻土。第 1–2 帧石头撒下来落地（溅起一点尘土），3–6 帧躺着（金色裂缝一亮一暗，循环），7–8 帧石头裂开变暗、碎成沙。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a woven gold ramp (#FFF6C8, #FFE07A, #F2B83C, #C8862A, #8A5418), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A MINEFIELD, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 ten round sandstone stones falling onto the ground at mirrored places, small dust splashes; 2 the stones landed in a wide flat ellipse 44 squares wide and 14 tall on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), each stone 3 to 4 squares with a glowing GOLDEN crack across it, churned earth under them; 3, 4, 5 and 6 the stones lying still, the gold cracks pulsing brighter and dimmer at mirrored places (frames 3-6 loop); 7 the stones cracking and darkening; 8 crumbling into sand, fading. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 8 equal 46:16 cells, image size 5888x256 (each cell 736x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `taliyah_fx_w_erupt.png`：岩突：地面隆起，5 帧

岩突（参考 w_knockupstone、w_mound_shadow、w_indicator_cracks、w_dustpuffs）：落点的地面**猛地拱起来**——先是地上一圈裂缝亮起金光，然后一堆尖尖的砂岩石柱从地里冲出来（中间最高），尘土往四周喷，最后石柱塌回去、尘土落下。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a woven gold ramp (#FFF6C8, #FFE07A, #F2B83C, #C8862A, #8A5418), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: THE GROUND ERUPTING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a ring of glowing GOLDEN cracks on the ground 26 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 a cluster of jagged sandstone spikes bursting up from the ring, the middle one tallest (20 squares), the others shorter at mirrored places, dust spraying out; 3 the spikes at full height (28 squares tall), a burst of pale dust 36 wide at their feet, rock chips flying up; 4 the spikes cracking and sinking, the dust rising; 5 a low heap of broken rock and settling dust, fading. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 5 equal 36:32 cells, image size 2880x512 (each cell 576x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `taliyah_fx_w_hit.png`：岩突：被掀飞的人身上，3 帧

被岩突掀飞的敌人身上：一下白金色闪光，身边几块碎石往上飞，一圈尘土。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold flash ramp (#FFFFFF, #FFF8E4, #FFE8B0), a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A HEAVE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 7 squares across on the target's middle; 2 rock chips flying up and out at mirrored places, a ring of dust 16 across; 3 the chips higher and smaller, fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal 18:20 cells, image size 864x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `taliyah_fx_e_blast.png`：石雷爆炸 / 撞墙：眩晕，4 帧

被掀飞穿过雷区、石雷在身上炸开（参考 e_burst、e_stone_spike、e_land_splash2），或被推到石墙上撞晕：脚下一下炸开碎石和金色的光，然后头上一圈**小石子绕着转**（眩晕）。**左右对称**，4 帧（第 3–4 帧是头上转的小石子，会循环到眩晕结束）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold flash ramp (#FFFFFF, #FFF8E4, #FFE8B0), a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a woven gold ramp (#FFF6C8, #FFE07A, #F2B83C, #C8862A, #8A5418).
Effect: A MINE BLAST AND A STUN, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold burst 12 squares wide at the target's feet with rock shards flying out at mirrored places; 2 the shards higher, a puff of dust, a small golden ring appearing over the head; 3 a ring of five small sandstone pebbles circling over the target's head 12 wide, pebbles at mirrored places; 4 the same ring turned half a step (frames 3-4 loop). everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 20:24 cells, image size 1280x384 (each cell 320x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `taliyah_fx_slow.png`：减速：脚下的沙土，4 帧循环

被大石头、雷区减速或被石墙挡住的敌人脚下：一小圈**翻起的沙土和小石子**，一缕沙尘绕着脚。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046), a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18).
Effect: A DRAGGING DUST PATCH, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ring of churned sand and small pebbles on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 wide and 5 tall, two thin dust wisps at mirrored places curling and settling in turn. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 4 equal 18:7 cells, image size 1152x112 (each cell 288x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `taliyah_fx_r_wall.png`：墙幔：一道长石墙，8 帧（约 5 秒）

墙幔（参考 r_rock_main、r_rock_side、r_ground_crack、r_smoke_dust）：一道**很长的石墙**。在我们的画面里墙是**沿着屏幕上下方向排开的一列尖尖的砂岩石柱**（远的在上、近的在下，互相叠一点，越往下越亮），一共约 9 根，每根约 14 格高、12 格宽，石面上有金色的细线；墙心（落点）在格子中间那一行，最上面一根石柱的底在墙心上方 60 格，最下面一根的底在墙心下方 60 格。第 1 帧地面裂开、石柱冒头（矮，碎石飞溅）；第 2 帧长到全高；第 3–6 帧循环（石柱上的金线一亮一暗，脚下飘一点沙尘，第 6 帧接得回第 3 帧）；第 7 帧石柱裂开、变矮；第 8 帧塌成碎石和沙。**左右对称**（每根石柱都画成左右对称的）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18), a woven gold ramp (#FFF6C8, #FFE07A, #F2B83C, #C8862A, #8A5418), a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046).
Effect: A LONG STONE WALL, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a column of NINE jagged sandstone pillars standing in a line down the picture (the far ones at the top, the near ones at the bottom, each overlapping the one behind it a little, the nearer ones a step brighter), each pillar 14 squares tall and 12 wide, symmetric left to right, thin GOLDEN threads across its faces, a crack of ground and a little dust at its foot; the wall's middle on the cell's middle row, the top pillar's foot 60 squares above it and the bottom pillar's foot 60 squares below it. 1 the ground cracking along the line and the pillars' tips breaking out, low, with rock chips flying; 2 the pillars at full height; 3, 4, 5 and 6 standing, the gold threads pulsing brighter and dimmer and a little dust drifting at their feet (frames 3-6 loop, frame 6 flowing back into 3); 7 the pillars cracked and lower; 8 collapsed into rubble and sand, fading. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 8 equal 16:126 cells, image size 2048x2016 (each cell 256x2016, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `taliyah_fx_surf.png`：浮石冲：冲浪时脚下的沙尘，4 帧循环

塔莉垭踩着大石头冲浪时（参考 r_dust_trail_mult、p_ground_burn、sandstreaks）：石头底下**往两边喷开的沙尘**和几块蹦起来的小石子，地上一道浅浅的擦痕。因为红色方不镜像，画成两边一样（不分前后）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a desert dust ramp (#F6ECD4, #E2D0A8, #C4AE84, #9A8662, #6E6046), a sandstone ramp (#F4E2BC, #DABE8C, #B8945E, #8C6A40, #624628, #3C2A18).
Effect: SURF DUST, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat scraped streak on the ground on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 30 squares wide, pale dust spraying out low to both sides from under its middle, three small pebbles hopping at mirrored places; the dust plumes and pebbles shift frame to frame so the loop keeps moving. everything is STONEWEAVING: chunky sandstone rocks with flat faces and pale sandy highlights, thin GOLDEN threads and glowing gold cracks where the earth is woven, puffs of pale desert dust; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams, no magic sparkles.
Layout: one horizontal row of 4 equal 36:8 cells, image size 2304x128 (each cell 576x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `taliyah_fx_a_rock` | view_projectiles `league_taliyah_a_rock`（追踪弹，z 2；上下对称） | 8 × 6 |
| `taliyah_fx_a_hit` | view_effects `league_taliyah_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `taliyah_fx_q_rock` | view_projectiles `league_taliyah_q_rock`（直线弹道，z 2；上下对称） | 12 × 8 |
| `taliyah_fx_q_hit` | view_effects `league_taliyah_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `taliyah_fx_q_boulder` | view_projectiles `league_taliyah_q_boulder`（直线弹道，穿透，z 2；上下对称） | 22 × 16 |
| `taliyah_fx_q_big_hit` | view_effects `league_taliyah_q_big_hit`（跟随目标，z 2；左右对称） | 22 × 20 |
| `taliyah_fx_q_ground` | view_effects `league_taliyah_q_ground`（大表，在她放石穿的地上，不跟随，z -2；左右对称；出现 → 躺着 → 消失，8 秒） | 30 × 10 |
| `taliyah_fx_e_mines` | view_effects `league_taliyah_e_mines`（大表，在岩突的落点，不跟随，z -2；左右对称；撒下 → 躺着 → 碎掉，4 秒） | 46 × 16 |
| `taliyah_fx_w_erupt` | view_effects `league_taliyah_w_erupt`（大表，在落点，不跟随，z 2；左右对称） | 36 × 32 |
| `taliyah_fx_w_hit` | view_effects `league_taliyah_w_hit`（跟随目标，z 2；左右对称） | 18 × 20 |
| `taliyah_fx_e_blast` | view_effects `league_taliyah_e_blast`（跟随目标，z 2；左右对称；被眩晕时） | 20 × 24 |
| `taliyah_fx_slow` | view_buffs `league_taliyah_q_slow` / `e_slow` / `r_stuck`（tag `slow`，跟随，脚下，z -1；左右对称） | 18 × 7 |
| `taliyah_fx_r_wall` | view_effects `league_taliyah_r_wall`（大表，墙心在落点，不跟随，z -1；左右对称；升起 → 立着 → 塌掉，5 秒） | 16 × 126 |
| `taliyah_fx_surf` | view_buffs `league_taliyah_surf` / `r_surf`（tag `surf`，跟随，脚下 = 冲浪石底下，z -1；左右对称） | 36 × 8 |

- 两张表：`asset/league/effects/league_taliyah_fx`（小的）和 `league_taliyah_big`（q_ground、e_mines、w_erupt、r_wall），tag = 名字（build_taliyah.py 的 views；q_slow / e_slow / r_stuck 用 `slow`，surf / r_surf 用 `surf`）。
- 弹道（a_rock、q_rock、q_boulder）断言上下对称；其余断言左右对称。q_ground 拉到 q_gt（480 tick）：1 开 + 2–5 循环 + 6 散；e_mines 拉到 e_t（240 tick）：1–2 开 + 3–6 循环 + 7–8 散；r_wall 拉到 r_t（300 tick）：1–2 升 + 3–6 循环 + 7–8 塌；e_blast 3–4 循环到眩晕结束（e_stun / r_wstun）。
- 用 `pixel_1x/` 切格（import_zac_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
