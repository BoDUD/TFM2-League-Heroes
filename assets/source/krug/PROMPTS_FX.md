# 远古石甲虫：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图 + 3 个技能图标。** 造型已定（`design/krug_design.png`：四肢着地、驼着砂岩巨石背的石头巨兽，巨石上发光的橙金裂缝，深紫褐的石头身体和大石拳，右下方小小的硬壳脸和两只琥珀眼睛）。远古石甲虫在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），38 格高、44 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/krug_size.png`：他缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是英雄联盟里峡谷石甲虫、墨菲特的特效贴图（金铲铲第 18 赛季的石甲虫没有自己的特效贴图；**灰色的形状，游戏里再染色**：石甲、石块冲击、地面裂缝、碎裂的碎石、尘土），按用在我们哪张特效分好了行。只在本地用。
> - **远古石甲虫是一块会动的岩石，特效都是石头**：棱角分明的**石块和砂岩碎片**、发光的**橙金色裂缝**（和他巨石背上的裂缝一样）、滚动和砸地时的尘土；不要蓝色，不要魔法符文，不要光滑的霓虹光束，不要软软的圆泡泡。
> - **特效要亮**：每道光、每道裂缝都有最亮一档或白黄色的高光，暗底上一眼能看见。**光、冲击波、尘土没有黑描边**（石块、碎片、怒气符号这些实物可以有一圈深色描边）。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。他没有飞行道具，没有要朝向的画面。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `krug_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）；图标交付 `krug_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/krug_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/krug_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「碎岩重生」 | 每条命第一次受到致命伤害时碎成一堆石头，片刻后以小石甲虫站起来（部分血量、攻速提高），嘲讽周围的敌人 | `p_burst` · `p_up` · `p_mini` · `e_taunt` |
| 普攻 | 立起身子，两只石拳砸下去 | `a_hit` |
| 技能 1 =「岩之摇滚」 | 身上包上一层石头（护盾），缩成大石球滚向目标，撞上造成伤害并击退 | `q_shield` · `q_hit` |
| 技能 2 =「坚岩外壳」 | 缩进巨石里，护甲魔抗大增，嘲讽周围的敌人 | `e_cast` · `e_shell` · `e_taunt` |
| 大招 =「远古崩落」 | 一跃而起（目标脚下出现落点圈），砸进敌群：冲击波击飞周围的敌人，半秒后天上落下碎石 | `r_jump` · `r_mark` · `r_slam` · `r_hit` · `r_rocks` · `r_rock_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、护盾、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 发光的橙金裂缝（裂纹、光缝、闪光、怒气符号）：`#FFF6C8`、`#FFD84A`、`#F79A1E`、`#C8540E`、`#6A2408`；
  - 砂岩（石块、碎片、图标里的巨石）：`#F2E6BE`、`#D2C08C`、`#A8946A`、`#74644A`；
  - 深色石头（大石块、石拳、描边）：`#9A8A84`、`#6E5E5A`、`#4A3C3C`、`#2C2228`；
  - 尘土：`#F0E2C8`、`#C8AE88`、`#9A7E5C`、`#64503A`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `krug_fx_a_hit.png`：普攻：岩拳砸中，4 帧

石拳砸中：一下白黄色的闪光，几块尖尖的碎石往两边崩开，一圈尘土。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A HEAVY STONE FIST IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow star flash 8 squares across; 2 a short burst of angular sandstone chips (2-3 squares each) flying out to both sides (mirrored), a dust puff 12 squares wide and 5 tall at the bottom; 3 the chips farther and falling, the dust wider; 4 the last dust fading. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `krug_fx_q_shield.png`：岩之摇滚：身上包上一层石头（护盾），5 帧

放技能 1 时：一圈棱角分明的**石块**从地上飞起、贴到他身上，石块之间亮着橙金色的光缝，最后只剩一圈石块描出的外轮廓。身体位置留空（只画外圈）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a dark violet-brown stone ramp (#9A8A84, #6E5E5A, #4A3C3C, #2C2228), a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408).
Effect: A STONE ARMOUR SNAPPING ON, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the hunched boulder beast stands in the middle, not drawn: 43 squares wide and 38 tall: 1 a ring of angular rocks (3-5 squares each) rising from the ground at both sides; 2 the rocks flying in around his outline, glowing orange-gold seams between them; 3 the rocks set into a jagged shell outline 46 squares wide and 42 tall around him (2-3 squares thick), the seams bright; 4 a white-yellow glint running along the seams; 5 settling to a thin outline of rocks with faint glowing seams. Only the outer edge: the middle (the body) left empty. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 5 equal 48:44 cells, image size 3840x704 (each cell 768x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `krug_fx_q_hit.png`：岩之摇滚：滚过来撞上，5 帧

大石球撞上目标：一下大的白黄闪光，一圈尘土和碎石往两边炸开，中间亮出一道橙金色的裂纹星。比普攻狠得多。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A ROLLING BOULDER SMASHING INTO A UNIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-yellow flash 14 squares across; 2 a glowing orange-gold CRACK STAR (jagged lines) 14 squares across in the middle, sandstone chips and dust bursting out to both sides (mirrored); 3 a wide dust cloud 26 squares wide and 10 tall at the bottom, the chips farther; 4 the crack star fading, the chips falling; 5 the last dust. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 5 equal 28:24 cells, image size 2240x384 (each cell 448x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `krug_fx_e_cast.png`：坚岩外壳：缩进巨石（震地），5 帧

缩进巨石的一下：脚下「咚」地一圈尘土往外推开，地上裂开几道橙金色的光缝，几块小石子跳起来。画在**地上**（扁椭圆），中心在格子底部中间。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A), a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A).
Effect: A SHELL STOMP, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell: 1 a dust ring 20 squares wide and 6 tall; 2 the ring 36 wide and 10 tall, four short glowing orange-gold CRACKS running out on the ground (mirrored), little pebbles hopping up; 3 the ring 48 wide, thinner, the cracks bright; 4 the cracks dimming, the pebbles down; 5 the last thin dust. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 5 equal 50:20 cells, image size 4000x320 (each cell 800x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `krug_fx_e_shell.png`：坚岩外壳：石壳护着（双抗），6 帧循环

缩在石壳里的时候：身体外面一圈若隐若现的**石块外壳**（和 q_shield 最后一帧差不多，但更淡），光缝一明一暗，脚边偶尔掉一点碎屑。身体位置留空。不要太显眼。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408).
Effect: A STONE SHELL HELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the hunched boulder beast stands in the middle, not drawn: 43 squares wide and 38 tall: a faint jagged outline of rocks 46 squares wide and 42 tall around him (1-2 squares thick, half of it shown at a time), the glowing seams between the rocks pulsing brighter and dimmer in turn; a few tiny sandstone flakes dropping at his feet (mirrored). The middle (the body) left empty. Subtle. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 6 equal 48:44 cells, image size 4608x704 (each cell 768x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `krug_fx_e_taunt.png`：嘲讽：被嘲讽的人头上冒火，6 帧循环

被石甲虫嘲讽（坚岩外壳、碎岩重生都会）：头顶上一个**橙金色的怒气符号**（两道交叉的裂纹，像石头裂开）一跳一跳。身体位置留空，只画格子最上面 10 格。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a dark violet-brown stone ramp (#9A8A84, #6E5E5A, #4A3C3C, #2C2228).
Effect: A TAUNTED UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit stands in the middle, not drawn: 16 squares wide and 36 tall: over the head (the top 10 squares of the cell) an ANGER MARK made of two crossed glowing orange-gold CRACKS (each 7 squares long, outlined dark stone), with two tiny rock chips beside it (mirrored); frames 1-6 it throbbing bigger and smaller, the chips bobbing. The rest of the cell empty. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 6 equal 18:44 cells, image size 1728x704 (each cell 288x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `krug_fx_r_jump.png`：远古崩落：起跳的尘土，5 帧

他一跃而起的地方：地上一圈尘土喷起来，两边几块碎石飞起，地上留下一圈浅浅的裂纹。中心在格子底部中间。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408).
Effect: A HEAVY JUMP-OFF, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a dust ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 20 squares wide and 6 tall at the bottom middle, two dust jets shooting up from it 20 squares high (mirrored); 2 the ring 34 wide, sandstone chips flying up at both sides; 3 the jets spreading and thinning, the chips at the top; 4 the chips falling, a faint glowing crack ring on the ground; 5 the last dust. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 5 equal 40:30 cells, image size 3200x480 (each cell 640x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `krug_fx_r_mark.png`：远古崩落：落点预警，6 帧

大招起跳后、砸下来之前：目标脚下的地面一圈**裂开的橙金色光圈**一点点亮起来，裂纹往中间爬。画在**地上**（扁椭圆）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a dark violet-brown stone ramp (#9A8A84, #6E5E5A, #4A3C3C, #2C2228).
Effect: A LANDING WARNING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred in the cell: 1 a thin dark crack ring 34 squares wide and 12 tall; 2 orange-gold light starting to glow in its cracks; 3 six short cracks running in toward the middle (mirrored); 4 the cracks reaching the middle, brighter; 5 the whole ring glowing, a white-yellow edge; 6 at its brightest. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 6 equal 36:14 cells, image size 3456x224 (each cell 576x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `krug_fx_r_slam.png`：远古崩落：砸地的冲击波，8 帧

他从天上砸进敌群：地面**「轰」地裂开**，一圈巨大的尘土冲击环往外推开，地上裂出一圈发光的橙金色裂缝，大块碎石往两边飞起再落下。画在**地上**（扁椭圆），中心在格子底部中间。这是全套最大的特效。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a dark violet-brown stone ramp (#9A8A84, #6E5E5A, #4A3C3C, #2C2228), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A MASSIVE GROUND SLAM, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell: 1 a white-yellow flash 30 squares wide; 2 a dust shock ring 50 squares wide and 16 tall, the ground under it SPLIT by glowing orange-gold cracks running out (mirrored); 3 the ring 74 wide and 24 tall, big angular rocks (4-6 squares) and sandstone chips flung up at both sides; 4 the ring 90 wide, the cracks at their brightest, the rocks high; 5 the ring thinner, the rocks falling; 6 the rocks landing, small dust puffs; 7 the cracks dimming to dark, dust settling; 8 the last faint glow in the cracks. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 8 equal 96:34 cells, image size 12288x544 (each cell 1536x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `krug_fx_r_hit.png`：远古崩落：被砸飞，4 帧

被砸飞的人：脚下一下橙金色的闪光，尘土和碎石往上喷。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A).
Effect: A UNIT THROWN UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash at the bottom middle 10 squares wide; 2 a jet of dust shooting upward 18 squares high, small sandstone chips to both sides (mirrored); 3 the dust spreading and thinning; 4 the last wisps. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 4 equal 20:24 cells, image size 1280x384 (each cell 320x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `krug_fx_r_rocks.png`：远古崩落：落石，8 帧

砸地后半秒，被震下来的大石头从天上掉下来：五六块棱角分明的大石头（带橙金色的裂缝）从格子上方落下来，砸在他周围的地上碎开、扬起尘土。石头落在格子底部的地上（中间留出他的位置）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a dark violet-brown stone ramp (#9A8A84, #6E5E5A, #4A3C3C, #2C2228), a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: FALLING ROCKS, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): six big angular ROCKS (5-8 squares each, sandstone with a glowing orange-gold crack, a dark stone outline) falling from the top of the cell at mirrored places around the middle (the middle 30 squares at the bottom left free for him): 1 the rocks at the top; 2-3 falling (a short dust trail above each); 4 the first two hitting the ground at the bottom, bursting into chips and dust; 5-6 the others hitting; 7 dust clouds at the six spots; 8 the last dust. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 8 equal 80:60 cells, image size 10240x960 (each cell 1280x960, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `krug_fx_r_rock_hit.png`：远古崩落：被落石砸中，4 帧

被落石砸中的人：一块石头从头顶落下砸碎，碎石往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A ROCK FALLING ON A UNIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an angular rock 6 squares across at the top of the cell; 2 the rock at the middle, about to hit; 3 the rock bursting into sandstone chips flying out to both sides (mirrored), a white-yellow flash; 4 the chips falling, a little dust. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 4 equal 18:30 cells, image size 1152x480 (each cell 288x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `krug_fx_p_burst.png`：碎岩重生：碎裂，6 帧

受到致命伤害时：他「砰」地碎开——一道橙金色的闪光从身体中间炸开，大大小小的砂岩碎块往四周飞散，扬起一大团尘土，碎块落回地上堆着。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a dark violet-brown stone ramp (#9A8A84, #6E5E5A, #4A3C3C, #2C2228), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A STONE BODY SHATTERING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the hunched boulder beast stands in the middle, not drawn: 43 squares wide and 38 tall: 1 a bright orange-gold flash bursting out from his middle with jagged glowing cracks; 2 big sandstone chunks (4-6 squares) and dark stone pieces flying out in every direction (mirrored), a big dust cloud; 3 the chunks at their widest (50 squares across), the dust thick; 4 the chunks falling; 5 the chunks landing at the bottom in a heap round the middle, the dust thinning; 6 the last dust, a faint glow between the pieces. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 6 equal 52:46 cells, image size 4992x736 (each cell 832x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `krug_fx_p_up.png`：碎岩重生：重新站起来（小石甲虫），6 帧

碎块重新聚起来：地上的碎石和尘土往中间吸，一圈橙金色的光缝亮起来，然后「轰」地一下尘土往外推开（这时周围的敌人被嘲讽）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A STONE BODY REFORMING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 small sandstone chips lying round the bottom middle, glowing seams between them; 2 the chips pulled up and inward toward the middle (mirrored); 3 an orange-gold glow ring 30 squares wide and 10 tall on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) at the bottom; 4 a burst: a dust ring pushed out 42 squares wide and a white-yellow flash in the middle; 5 the dust thinning, little pebbles falling; 6 the last dust. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 6 equal 44:40 cells, image size 4224x640 (each cell 704x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `krug_fx_p_mini.png`：碎岩重生：小石甲虫（剩下这条命），6 帧循环

重生后的小石甲虫：脚下一圈若隐若现的**橙金色裂纹圈**，一明一暗，偶尔有小石子掉下。画在**地上**（扁椭圆），不要太显眼。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing lava orange-gold ramp (#FFF6C8, #FFD84A, #F79A1E, #C8540E, #6A2408), a pale sandstone ramp (#F2E6BE, #D2C08C, #A8946A, #74644A).
Effect: A REBORN STONE AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred in the cell: a thin ring of glowing orange-gold CRACKS 32 squares wide and 8 tall, broken into segments; frames 1-6 the segments glowing brighter and dimmer in turn (mirrored), a tiny pebble or two at the edge. Subtle. everything is the ANCIENT KRUG's stone: chunky angular ROCKS and sandstone chips, glowing LAVA orange-gold cracks and seams (like the cracks in his boulder back), heavy dust where he lands and rolls; flat shades, crisp angular shapes; no blue, no magic runes, no smooth neon beams, no round soft bubbles.
Layout: one horizontal row of 6 equal 34:10 cells, image size 3264x160 (each cell 544x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `krug_icon_skill.png`：技能 1「岩之摇滚」图标

大石球：一块带橙金裂缝的圆形砂岩巨石正往右滚，后面拖着尘土和速度线。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark STONE frame cracked with glowing orange-gold seams at the corners, a deep warm brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big round SANDSTONE BOULDER with glowing orange-gold cracks rolling to the right, a trail of dust and two short speed streaks behind it at the left. No text, no letters.
```

### 图标 2. `krug_icon_skill2.png`：技能 2「坚岩外壳」图标

石壳：一块厚厚的棱角巨石像盾牌一样挡在中间，下面露出一只发光的琥珀色眼睛。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark STONE frame cracked with glowing orange-gold seams at the corners, a deep warm brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a thick angular sandstone BOULDER SHELL like a shield in the middle, glowing orange-gold seams on it, one glowing amber eye peeking out from under its lower edge. No text, no letters.
```

### 图标 3. `krug_icon_ult.png`：大招「远古崩落」图标

崩落：一只大石拳从上往下砸进地面，地面裂开发光，碎石往两边飞。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark STONE frame cracked with glowing orange-gold seams at the corners, a deep warm brown inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge dark STONE FIST slammed down from above into the ground at the centre, the ground split by glowing orange-gold cracks, angular rocks flying out to both sides. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `krug_fx_a_hit` | view_effects `tft_krug_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `krug_fx_q_shield` | view_effects `tft_krug_q_shield`（跟随他，z 3；左右对称） | 48 × 44 |
| `krug_fx_q_hit` | view_effects `tft_krug_q_hit`（跟随被撞的人，z 2；左右对称） | 28 × 24 |
| `krug_fx_e_cast` | view_effects `tft_krug_e_cast`（跟随他，z 3；左右对称） | 50 × 20 |
| `krug_fx_e_shell` | view_buffs `tft_krug_e_shell`（跟随他，z 3；左右对称） | 48 × 44 |
| `krug_fx_e_taunt` | view_buffs `tft_krug_e_taunt`（跟随被嘲讽的人，z 4；左右对称） | 18 × 44 |
| `krug_fx_r_jump` | view_effects `tft_krug_r_jump`（留在起跳的地上，z 1；左右对称） | 40 × 30 |
| `krug_fx_r_mark` | view_effects `tft_krug_r_mark`（跟随被砸的目标，z -1；左右对称） | 36 × 14 |
| `krug_fx_r_slam` | view_effects `tft_krug_r_slam`（大表，留在他砸落的地上，z -1；左右对称） | 96 × 34 |
| `krug_fx_r_hit` | view_effects `tft_krug_r_hit`（跟随被击飞的人，z 2；左右对称） | 20 × 24 |
| `krug_fx_r_rocks` | view_effects `tft_krug_r_rocks`（大表，留在他身边的地上，z 3；左右对称） | 80 × 60 |
| `krug_fx_r_rock_hit` | view_effects `tft_krug_r_rock_hit`（跟随被砸的人，z 2；左右对称） | 18 × 30 |
| `krug_fx_p_burst` | view_effects `tft_krug_p_burst`（留在他倒下的地方，z 3；左右对称） | 52 × 46 |
| `krug_fx_p_up` | view_effects `tft_krug_p_up`（跟随他，z 3；左右对称） | 44 × 40 |
| `krug_fx_p_mini` | view_buffs `tft_krug_p_mini`（跟随他，z -1；左右对称） | 34 × 10 |
| `krug_icon_skill` | skill_icons[0] `asset/tft/icons/tft_krug_skill` | 64 × 64 |
| `krug_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_krug_skill2` | 64 × 64 |
| `krug_icon_ult` | skill_icons[2] `asset/tft/icons/tft_krug_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_krug_fx`（小的）和 `tft_krug_big`（r_slam、r_rocks），tag = 名字。
- 全部断言左右对称。
- p_burst、p_up 由 tft.dll 在碎岩重生时播（p_mini、e_taunt 是它挂的 buff）；q_shield 在技能 1 出手时播；r_jump 在大招起跳时留在原地，r_mark 跟着目标，r_rocks 在砸地后 30 tick 播。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
