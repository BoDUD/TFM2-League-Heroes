# 刀疤：给 Codex 的特效提示词（第 3 步）

> **这一份是 11 张特效图 + 3 个技能图标。** 造型已定（`design/scar_design.png`：野火帮的哨兵，瘦高的紫皮肤祖安人，白骷髅面具、蓝紫尖发、两只红尖耳，双手横握一杆紫金色的长矛、矛尖朝前）。刀疤在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），38 格高、42 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/scar_size.png`：刀疤缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里刀疤自己的特效贴图（**灰色的形状，游戏里再染色**：星形打击、炸弹、涂鸦颜料、火、尘土、光点），按用在我们哪张特效分好了行。只在本地用。
> - **刀疤是祖安的野火帮，特效都是他的土炸弹、长矛和滑板**：野火帮的**青绿色**光（他金铲铲炸弹上就是这个颜色）、白热和橙色的爆炸、**紫红色的涂鸦颜料**（他矛头的颜色，野火帮到处喷涂鸦）、矛尖的金色闪光、祖安的尘土和碎石；不要魔法符文，不要光滑的霓虹光束，不要闪电。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、电光、冲击波、尘土没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。唯一的飞行道具是炸弹 `q_bomb`，飞的时候整张图跟着方向转，所以画成**圆的**。悬浮滑板和横扫的动作画在他自己的动作帧里，这里不画。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `scar_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）；图标交付 `scar_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/scar_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/scar_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「野火冲刺 + 监察」 | 每 6 秒下一次普攻变成踩滑板冲到目标身上捅一矛，回复上次冲刺以来受到伤害的一部分；血量越高减伤越多 | `p_hit` · `p_heal` |
| 普攻 | 长矛往前一刺 | `a_hit` |
| 技能 1 =「水坑狙击惊喜」 | 向最近的 3 名敌人各扔一颗炸弹：魔法伤害 + 晕眩，自己回血 | `q_bomb` · `q_hit` · `q_stun` |
| 技能 2 =「长矛横扫」 | 长矛往前方横扫，把敌人打退 | `e_hit` |
| 大招 =「野火突袭」 | 踩滑板冲向敌人，一路丢下燃烧弹；落地大爆炸击飞周围的敌人，之后几秒大幅减伤 | `r_bomb` · `r_land` · `r_hit` · `r_guard` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、电光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 野火青绿（炸弹、滑板、回血、护体）：`#E8FFF4`、`#9CF5D0`、`#3FE0A0`、`#17A874`、`#0B5E48`；
  - 白热和橙色（爆炸）：`#FFFFFF`、`#FFF0C0`、`#FFB850`、`#F06A1E`、`#A0300C`；
  - 紫红涂鸦颜料（矛头的颜色）：`#FFD8F6`、`#F27AD8`、`#C23AB8`、`#7A1E86`、`#3E0E50`；
  - 金色（矛头花纹、图标角）：`#FFF6C8`、`#FCD65A`、`#E8A52A`、`#A8641A`、`#5A3010`；
  - 深色金属（炸弹壳）：`#E8ECF4`、`#B4BCCC`、`#7C8698`、`#4A5262`、`#262A34`；
  - 尘土：`#F0E2C8`、`#C8AE88`、`#9A7E5C`、`#64503A`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（11 张）

11 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `scar_fx_a_hit.png`：普攻：长矛刺中，4 帧

矛尖扎在人身上：一个白热的**四角星闪光**，几颗金色和紫色的碎屑往两边崩开，一小圈冲击环。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), a graffiti paint ramp (#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50).
Effect: A SPEAR STAB IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot four-pointed STAR flash 8 squares across; 2 a short orange shock ring 12 squares wide and 6 tall, gold and purple chips flying out to both sides (mirrored); 3 the ring thinner and wider, the chips farther; 4 the last glints fading. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `scar_fx_p_hit.png`：野火冲刺：滑板冲过去捅一矛，5 帧

被动冲刺的那一矛：比普攻大，一个白热的星形闪光外面裹着一圈**青绿色的野火光**，青绿色和金色的火星往两边四溅，最后几缕青绿色的烟。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010).
Effect: A FIRELIGHT DASH STRIKE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-hot STAR flash 10 squares across ringed with teal-green glow; 2 a teal-green shock ring 20 squares wide and 8 tall, teal and gold sparks spraying out to both sides (mirrored); 3 the ring wider and thinner, the sparks farther, two small teal smoke puffs; 4 the smoke rising and thinning; 5 the last wisps. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal square cells, image size 1920x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `scar_fx_p_heal.png`：野火冲刺：冲完回血，5 帧

冲刺打中后回一口血：脚下「呼」地一圈**青绿色的光环**，身体两侧往上冒一串青绿色和白色的小光点（像野火帮的萤火），头顶一闪。身体位置留空。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48).
Effect: A FIRELIGHT HEAL, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the lanky masked man stands in the middle, not drawn: 30 squares wide and 38 tall: 1 a teal-green flash ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 14 squares wide; 2 the ring 28 squares wide and 8 tall, two columns of teal-green and white firefly motes (1-2 squares) rising at both sides of him (mirrored); 3 the motes up at his shoulders, a white glint over his head; 4 the ring fading, the motes higher; 5 the last motes. The middle (the body) left empty. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal 36:42 cells, image size 2880x672 (each cell 576x672, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `scar_fx_q_bomb.png`：水坑狙击惊喜：飞出去的炸弹，4 帧循环

他扔出去的土炸弹：一个**圆圆的深色金属球**，中间一圈发光的**青绿色**条纹，顶上一根引线冒着小火星。飞行时整张图会跟着方向转，所以**画成圆的、转起来一样**：引线的火星画小一点，4 帧里球慢慢转（条纹的位置变），火星一闪一闪。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark metal ramp (#E8ECF4, #B4BCCC, #7C8698, #4A5262, #262A34), a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C).
Effect: A THROWN BOMB IN FLIGHT, 4 looping frames, ROUND and the same turned any way (the picture is rotated with its flight): a ball 8 squares across of dark metal with a glowing teal-green band round its middle and a tiny spark (1-2 squares) at its fuse on top; frames 1-4 the band shifting round the ball as it spins, the spark flickering. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `scar_fx_q_hit.png`：水坑狙击惊喜：炸弹炸开（晕眩），6 帧

炸弹在人身上炸开：一团**青绿色和橙色**的爆炸火球，往外喷出几块**紫红色的涂鸦颜料**（像泼出去的颜料点），金属碎片往两边飞，最后剩一团烟。比普攻大得多。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a graffiti paint ramp (#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A BOMB BLAST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-hot flash 10 squares across; 2 a round fireball 22 squares across - a teal-green outer burst with a hot orange-white core; 3 the fireball at 30 squares, splats of purple-magenta GRAFFITI PAINT (blobs and drops 2-4 squares) and dark metal shards flung out to both sides (mirrored); 4 the fire breaking into puffs, the paint drops falling; 5 grey-green smoke rising; 6 the last smoke and paint specks. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal square cells, image size 3264x544 (each cell 544x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `scar_fx_q_stun.png`：水坑狙击惊喜：被炸晕，6 帧循环

被炸晕的人头顶：几颗**青绿色和金色的小星星**转圈，中间一点小烟。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010).
Effect: A STUN OVER THE HEAD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): in the cell (it rides over the unit's head) three small stars (3 squares) in teal-green and gold circling on a flat ring 16 squares wide and 4 tall, a tiny smoke puff in the middle; frames 1-6 the stars going round. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 20:10 cells, image size 1920x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `scar_fx_e_hit.png`：长矛横扫：扫中（打退），4 帧

长矛横着扫到人：一道**横向的白热光弧**（左右对称的扁月牙，两头尖），金色碎屑往两边飞，一团尘土。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A SWEEPING SPEAR HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat white-hot slash ARC 18 squares wide and 5 tall, both ends pointed, centred (the same mirrored); 2 the arc wider and thinner, gold chips flying out to both sides; 3 a puff of dust in the middle, the arc fading; 4 the last dust. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal square cells, image size 1408x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `scar_fx_r_bomb.png`：野火突袭：一路丢下的燃烧弹，6 帧

他踩着滑板冲过去时丢在地上的燃烧弹：地上「轰」地炸开一团**青绿色和橙色的火**，往上窜几簇火苗，地上溅开一圈紫红色的涂鸦颜料，最后火苗变小、剩一片烧焦的痕迹。画在**地上**（从斜上方看的扁椭圆），中心在格子底部中间。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a graffiti paint ramp (#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A FIRE BOMB ON THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell: 1 a white-hot flash 10 squares wide; 2 a burst of teal-green and orange fire 24 squares wide, a few flame tongues shooting up 14 squares; 3 the fire at 34 squares wide, a ring of purple-magenta PAINT splats on the ground (mirrored); 4 the flames lower and flickering; 5 small flames and smoke; 6 a scorched patch with paint specks fading. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 40:24 cells, image size 3840x384 (each cell 640x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `scar_fx_r_land.png`：野火突袭：落地大爆炸，8 帧

大招冲到头、跳下滑板落地：地面炸开**一圈很大的青绿色和橙色冲击波**，环上溅着紫红色的涂鸦颜料，碎石和尘土往四周飞，几簇青绿色的火苗留在地上，最后慢慢暗下去。这是画在**地上**的（从斜上方看的扁椭圆），中心在格子底部中间（他的脚下）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a graffiti paint ramp (#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A BIG GROUND BLAST, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell (his feet): 1 a white-hot flash 16 squares wide; 2 a thick teal-green shock ring 34 squares wide and 12 tall with a hot orange inner edge; 3 the ring 54 wide and 18 tall, purple-magenta PAINT splats thrown along it, chunks of stone and dust flung up to both sides (mirrored); 4 the ring 76 wide and 26 tall, thinner; 5 the ring at the edge breaking into bright segments, small teal flames left on the ground; 6 the dust settling, the flames flickering; 7 the flames dimming; 8 faint paint specks and thin dust. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 8 equal 84:34 cells, image size 10752x544 (each cell 1344x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `scar_fx_r_hit.png`：野火突袭：被炸到 / 击飞，4 帧

被燃烧弹和落地爆炸炸到的人：脚下「砰」地一下青绿色和橙色的闪光，尘土往上喷，两边几点紫红色颜料。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a graffiti paint ramp (#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50), a dust brown ramp (#F0E2C8, #C8AE88, #9A7E5C, #64503A).
Effect: A UNIT CAUGHT IN A BLAST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-green and orange flash at the bottom middle 10 squares wide; 2 a jet of dust and teal sparks shooting upward 14 squares high, paint specks to both sides (mirrored); 3 the dust spreading and thinning; 4 the last puffs. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `scar_fx_r_guard.png`：野火突袭：落地后的减伤护体，6 帧循环

落地后几秒大幅减伤：他身体两侧各一道**半透明感的青绿色护罩弧**（像一层野火的光幕，只画轮廓的几格亮边），脚下一圈淡淡的青绿色光圈，几点青绿色光点往上飘。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010).
Effect: A GUARD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the lanky masked man stands in the middle, not drawn: 30 squares wide and 38 tall: at both sides of him (mirrored) a tall curved teal-green shield ARC 4 squares wide and 34 tall (only a bright rim and a few lit squares, the inside empty), a faint teal ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 30 squares wide and 7 tall at the bottom, a few teal motes drifting up; frames 1-6 a glint running up the arcs, the motes rising. The middle (the body) left empty. everything is an UNDERCITY REBEL's street gear: home-made BOMBS that burst in TEAL-GREEN Firelight glow and hot orange, splats of purple-magenta GRAFFITI PAINT, a long spear's sharp glints, Zaun dust and grit; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 40:44 cells, image size 3840x704 (each cell 640x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `scar_icon_skill.png`：技能 1「水坑狙击惊喜」图标

三颗冒着引线火星的圆炸弹飞出去，中间一颗炸开青绿色和橙色的火球，溅出紫红色颜料。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark purple frame with little riveted gold corners, a deep navy-teal inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: three round dark metal BOMBS with teal-green bands and sparking fuses flying out in a fan from the lower left, the middle one bursting in a teal-green and orange blast with purple-magenta paint splats. Colours: a dark metal ramp (#E8ECF4, #B4BCCC, #7C8698, #4A5262, #262A34), a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a graffiti paint ramp (#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50). No text, no letters.
```

### 图标 2. `scar_icon_skill2.png`：技能 2「长矛横扫」图标

一杆长矛横着扫过画面，矛头后面拖着一道白热的光弧和金色碎屑。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark purple frame with little riveted gold corners, a deep navy-teal inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: his long SPEAR (a dark purple shaft with copper bands, a broad purple arrowhead blade with gold graffiti marks) swung across the tile from the left to the right, a white-hot curved slash ARC trailing behind its blade, gold chips flying. Colours: a gold ramp (#FFF6C8, #FCD65A, #E8A52A, #A8641A, #5A3010), a graffiti paint ramp (#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50), a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C). No text, no letters.
```

### 图标 3. `scar_icon_ult.png`：大招「野火突袭」图标

一块野火帮的悬浮滑板从左下往右上冲，底下喷着青绿色的推进火，后面一路掉下炸开的燃烧弹。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark purple frame with little riveted gold corners, a deep navy-teal inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a small Firelight HOVERBOARD (a dark grey-brown deck with a raised nose, a row of glowing teal-green thruster vents underneath) rushing from the lower left to the upper right with teal-green thruster flames, a line of small fire bombs bursting behind it in teal-green and orange. Colours: a dark metal ramp (#E8ECF4, #B4BCCC, #7C8698, #4A5262, #262A34), a Firelight teal-green ramp (#E8FFF4, #9CF5D0, #3FE0A0, #17A874, #0B5E48), a hot blast ramp (#FFFFFF, #FFF0C0, #FFB850, #F06A1E, #A0300C), a graffiti paint ramp (#FFD8F6, #F27AD8, #C23AB8, #7A1E86, #3E0E50). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `scar_fx_a_hit` | view_effects `tft_scar_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `scar_fx_p_hit` | view_effects `tft_scar_p_hit`（跟随目标，z 2；左右对称） | 24 × 24 |
| `scar_fx_p_heal` | view_effects `tft_scar_p_heal`（跟随他，z 3；左右对称） | 36 × 42 |
| `scar_fx_q_bomb` | view_projectiles `tft_scar_q_bomb`（随飞行方向转；必须是圆的） | 10 × 10 |
| `scar_fx_q_hit` | view_effects `tft_scar_q_hit`（跟随目标，z 2；左右对称） | 34 × 34 |
| `scar_fx_q_stun` | view_buffs `tft_scar_q_stun`（跟随被晕的人，头顶，z 3；左右对称） | 20 × 10 |
| `scar_fx_e_hit` | view_effects `tft_scar_e_hit`（跟随目标，z 2；左右对称） | 22 × 22 |
| `scar_fx_r_bomb` | view_effects `tft_scar_r_bomb`（留在他经过的地上，z -1；左右对称） | 40 × 24 |
| `scar_fx_r_land` | view_effects `tft_scar_r_land`（大表，留在他脚下的地上，z -1；左右对称） | 84 × 34 |
| `scar_fx_r_hit` | view_effects `tft_scar_r_hit`（跟随被炸的人，z 2；左右对称） | 18 × 20 |
| `scar_fx_r_guard` | view_buffs `tft_scar_r_guard`（跟随他，z 3；左右对称） | 40 × 44 |
| `scar_icon_skill` | skill_icons[0] `asset/tft/icons/tft_scar_skill` | 64 × 64 |
| `scar_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_scar_skill2` | 64 × 64 |
| `scar_icon_ult` | skill_icons[2] `asset/tft/icons/tft_scar_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_scar_fx`（小的）和 `tft_scar_big`（r_land），tag = 名字。
- 全部断言左右对称；q_bomb 断言转 180 度也一样（圆的）。
- p_heal 由 tft.dll 在冲刺打中时播；q_hit / q_stun 由 tft.dll 在炸弹打中时播 / 挂上（--plain 的数据自己播）。
- 用 `pixel_1x/` 切格（import_maddie_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
