# 死亡颂唱者 卡尔萨斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型和动作已定（`design/karthus_idle.png`：3/4 正面朝右、又高又瘦的巫妖，深钢色主教冠和大肩甲、青色宝石，深红长袍和深紫破布，骷髅脸、发光的青色眼睛，手握长法杖）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），44 格高、26 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/karthus_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/karthus_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡尔萨斯自己的特效贴图（大多是单色形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**幽绿 / 青绿色的灵魂光**（普攻、荒芜、亵渎、痛苦之墙、安魂曲都是），光环和星芒带**蓝色的边**，暗处是**深色的灵魂烟**，安魂曲的光柱边缘带一点**深红**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：13 张严格**左右对称**（逐格对称：这些画面在红色方不会镜像）；弹道图 `a_bolt`（灵魂弹）**朝右画、上下对称**（游戏把它转到飞行方向，往左时上下颠倒）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `karthus_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/karthus_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/karthus_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（W「痛苦之墙」在里面） | 法杖射出灵魂弹；每 12 秒身边有敌方英雄时，攻击在那名英雄的位置立起一道墙：减速、降魔抗 | `a_bolt` · `a_hit` · `w_wall` · `w_slow` · `w_shred` |
| 技能 1 = Q「荒芜」 | 目标点先出预警圈，0.53 秒后炸开；只炸到一个敌人伤害翻倍 | `q_mark` · `q_boom` · `q_hit` · `q_lone` |
| 技能 2 = E「亵渎」 | 5 秒内脚下灵魂漩涡转动，烧身边的敌人 | `e_on` · `e_hit` |
| 大招「安魂曲」 | 浮空引导 3 秒，然后全图每个敌方英雄身上落下一道光 | `r_cast` · `r_hit` |
| 被动「死亡契约」（附加包） | 受到致命伤害时化为灵体 7 秒，继续放技能 | `p_spirit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、灵魂、烟、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 幽绿的灵魂光：`#FFFFFF`、`#D4FFF2`、`#8CF5D6`、`#3CD6B0`、`#1C9C88`、`#0E5C5A`；
  - 蓝色的光环边：`#FFFFFF`、`#CCF2FF`、`#7CD4FF`、`#3A9CF0`、`#1C5CC0`、`#102E78`；
  - 深色的灵魂烟：`#7C8AA8`、`#56607E`、`#3A4260`、`#262B42`、`#161A2A`；
  - 安魂曲光柱的深红边：`#FFE0E0`、`#FF9AA4`、`#E8364E`、`#A8122E`、`#5C0818`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：荒芜的半径 15000，亵渎的半径 30000，痛苦之墙宽 6000、长 60000）。

### 1. `karthus_fx_a_bolt.png`：普攻：一团幽绿的灵魂弹（弹道，转向飞行方向），4 帧

他用法杖射出的普攻：一团青绿色的灵魂光球，中间白芯，后面拖着一条飘动的青绿色尾巴（参考 aa_core、aa_mis_trail、aa_glows）。**朝右画、上下对称**（游戏会把它转到飞行方向）。4 帧循环：尾巴摆动、光球一明一暗。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A).
Effect: A GHOSTLY BOLT, 4 frames, a seamless loop, POINTING RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to the way it flies, so shot to the left it is turned upside down): a round teal-white orb 4 squares across with a white core, 3 squares from the cell's right edge, and a wavy teal soul trail 8 squares long behind it (to the left), 2-3 squares thick, fading to its tip; the trail's waves move along it frame by frame (mirrored top and bottom), the orb a shade brighter on frames 2 and 4.
Layout: one horizontal row of 4 equal 14:8 cells, image size 896x128 (each cell 224x128, 16 px a square); the orb on the cell's middle rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `karthus_fx_a_hit.png`：普攻：灵魂弹打中目标，3 帧

灵魂弹打中：一团青白色的闪光，四道短光芒，几点青绿色的灵魂碎屑飞散（参考 aa_flash、aa_tar）。**左右对称**，约 14 × 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A).
Effect: A SOUL IMPACT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-teal flash 6 squares across with 4 thin rays (up, down, left, right, 3 squares long); 2 the flash 9 squares across, the rays longer, 6 teal soul specks (1-2 squares) flying out at mirrored places; 3 only a fading teal ring 12 squares across and the specks further out.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `karthus_fx_q_mark.png`：Q 荒芜：目标点地上的预警圈（不跟随，0.53 秒后爆炸），6 帧

荒芜的预警：目标点的地面上一圈蓝色的细光环（地上的椭圆，宽约 34 格），圈里的地面裂开、裂缝透出青白色的光，越来越亮，几缕青绿色的灵魂从裂缝里冒起一点（参考 q_ring_blue、q_ground_cracks、q_wisps_add）。**左右对称**，6 帧（约 0.5 秒），**平贴在地上**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue rim ramp (#FFFFFF, #CCF2FF, #7CD4FF, #3A9CF0, #1C5CC0, #102E78) and a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A).
Effect: A WARNING CIRCLE CRACKING THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin blue rim ring on the ground (an ellipse 34 squares wide and 12 tall, 1 square thick, white highlights at its left and right ends); 1 the ring faint, a small teal crack star (8 squares) in the middle; 2 the ring brighter, the cracks 16 squares across; 3 the cracks 26 across, teal light in them; 4 the cracks reaching the ring, 4 small teal wisps (2x3) rising 2-4 squares at mirrored places; 5 the whole ellipse glowing pale teal, the cracks white; 6 the brightest, about to burst. Flat on the ground, nothing taller than 6 squares.
Layout: one horizontal row of 6 equal 40:16 cells, image size 3840x256 (each cell 640x256, 16 px a square); centered across, the ellipse's middle 7 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `karthus_fx_q_boom.png`：Q：落点爆炸（不跟随），5 帧

荒芜炸开：落点一颗蓝白色的星芒闪一下，接着一团青绿色的灵魂火往上喷起（约 26 格高），里面卷着几张模糊的鬼脸般的灵魂，地上一圈蓝色的冲击环往外扩，然后化成青灰色的烟散掉（参考 q_flare、q_swirl、q_torus_swirl、q_shockwave、q_wisps_add）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A), a blue rim ramp (#FFFFFF, #CCF2FF, #7CD4FF, #3A9CF0, #1C5CC0, #102E78) and a dark spirit smoke ramp (#7C8AA8, #56607E, #3A4260, #262B42, #161A2A).
Effect: A SOUL BLAST FROM THE GROUND, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a blue-white star flare in the middle of the ground (8 squares, 4 long thin rays) over a glowing ellipse 30 wide and 10 tall; 2 a column of teal soul fire bursting up from it, 20 squares tall and 16 wide, white at its core, 4 ghostly wisps curling out of it (mirrored pairs), a blue ring 34 wide and 12 tall on the ground; 3 the fire 26 squares tall, its top breaking into 6 wisps, the ring 38 wide; 4 the fire turning into dark spirit smoke puffs, teal embers flying up; 5 only a few smoke puffs and embers high up.
Layout: one horizontal row of 5 equal square cells, image size 3200x640 (each cell 640x640, 16 px a square); centered across, the blast's foot 7 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `karthus_fx_q_hit.png`：Q：被荒芜炸中的敌人身上，3 帧

被荒芜炸到：一团青绿色的灵魂火在他身上一闪，几缕往上飘（参考 q_wisps_add、aa_flash）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A).
Effect: A SOUL BURN HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white flash 7 squares across; 2 the flash 10 across with 4 teal flame tongues licking up (mirrored pairs, 2x4 squares); 3 only 4 small wisps higher up, fading.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `karthus_fx_q_lone.png`：Q：只炸中一个敌人时伤害翻倍（他身上，跟随），4 帧

荒芜只炸到一个敌人、伤害翻倍的强化爆点：比普通打中更大更亮——一圈白蓝色的环一胀，中间一个白色十字星芒，周围 8 道青色的光刺向外射（参考 q_flare、q_ring_blue、q_shockwave）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue rim ramp (#FFFFFF, #CCF2FF, #7CD4FF, #3A9CF0, #1C5CC0, #102E78) and a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A).
Effect: A DOUBLED HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white cross-star flare 8 squares across; 2 the flare 12 across inside a white-blue ring 14 across, 8 teal light spikes (1 square wide, 4 long) shooting out at mirrored angles; 3 the ring 18 across, the spikes further out and thinner; 4 only a faint ring 19 across.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `karthus_fx_e_on.png`：E 亵渎：他脚下转动的灵魂漩涡（跟随，循环 5 秒），4 帧

亵渎开着的 5 秒：他脚下一圈暗色的灵魂漩涡（地上的椭圆，宽约 60 格），青绿色的灵魂一缕缕绕着圈转，圈的边上几缕灵魂往上飘（参考 e_defile_ring_blue、e_defile_swirl_scroll、e_defile_waves、e_ground_swirl）。**只画地上的圈和往上飘的灵魂，他站在中间、身体位置留空**（the lich stands in the middle, not drawn: 40 squares from his crown tip to the ground, 26 squares wide, his staff 4 squares more）。**左右对称**，4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A), a dark spirit smoke ramp (#7C8AA8, #56607E, #3A4260, #262B42, #161A2A) and a blue rim ramp (#FFFFFF, #CCF2FF, #7CD4FF, #3A9CF0, #1C5CC0, #102E78).
Effect: A SOUL VORTEX ON THE GROUND round a standing figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the lich stands in the middle, not drawn: 40 squares from his crown tip to the ground, 26 squares wide, his staff 4 squares more): a flat ring on the ground - an ellipse 60 squares wide and 20 tall, 4 squares thick - of dark spirit smoke with a thin blue rim, and 8 teal-white soul wisps (3 squares long, curved) running round it at mirrored places; frame by frame the wisps move a quarter of the way round (mirrored, so the left and right halves stay mirror images); 4 small soul flames (2x4) rising 6-10 squares from the ring's left and right ends. The middle of the ellipse stays empty.
Layout: one horizontal row of 4 equal 64:26 cells, image size 4096x416 (each cell 1024x416, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom row (the ground he stands on). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `karthus_fx_e_hit.png`：E：被亵渎烧到的敌人身上，3 帧

亵渎每次烧到敌人：一小团青绿色的灵魂火苗在他身上跳一下（参考 e_defile_hit_bit、e_defile_hit_wake）。**左右对称**，小。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A).
Effect: A SMALL SOUL FLAME, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white spark 3 squares across; 2 a soul flame 6 squares wide and 8 tall, white core, its tip curling up; 3 the flame thinner and higher, fading.
Layout: one horizontal row of 3 equal 10:12 cells, image size 480x192 (each cell 160x192, 16 px a square); centered across, the flame's foot 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `karthus_fx_w_wall.png`：W 痛苦之墙：立在敌人位置的一道墙（不跟随，5 秒），8 帧

痛苦之墙：一道竖着的半透明灵魂墙，青绿色的雾里浮着一张张痛苦尖叫的鬼脸，墙脚的地面裂开透出青光（参考 w_wall_faces、w_wall_scroll_base、w_pillar_color_blue、w_pillar_fire）。墙宽约 12 格、高约 60 格，**以格子正中为地面上的那个点**（墙往上、往下各伸 30 格：在战场上是一道竖着的长条）。**左右对称**，8 帧：1–2 从中间往上下两头长出来，3–6 鬼脸慢慢往上飘（循环用），7–8 散掉。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A) and a dark spirit smoke ramp (#7C8AA8, #56607E, #3A4260, #262B42, #161A2A).
Effect: A WALL OF SCREAMING SOULS, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an upright band of translucent teal soul mist 12 squares wide and 60 squares tall, its middle at the cell's middle, with ghostly screaming faces in it (each 6 squares wide and 7 tall: two dark eye holes and an open dark mouth in pale teal mist, the faces themselves symmetric), dark smoke at its edges, pale teal light at its core; 1 a bright teal crack in the middle 16 squares tall; 2 the band growing to 40 squares tall, 3 faces; 3-6 the full band with 5 faces, the faces drifting 3 squares up each frame (frame 6 leads back into frame 3), wisps curling off both edges at mirrored places; 7 the band breaking into smoke puffs; 8 only faint puffs.
Layout: one horizontal row of 8 equal 16:64 cells, image size 2048x1024 (each cell 256x1024, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `karthus_fx_w_slow.png`：W：被减速的敌人脚下（循环），2 帧

穿过痛苦之墙被减速的敌人脚下：几只青绿色的灵魂鬼手从地上伸出来抓着他的脚（参考 w_tar_slow_tendrils）。**左右对称**，2 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A).
Effect: SOUL TENDRILS GRASPING at a unit's feet, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 4 small curling teal soul tendrils (1-2 squares wide, 4-5 tall, like thin ghostly fingers) rising from a flat teal glow ellipse 14 wide and 3 tall; 1 the tendrils curling inward; 2 curling outward, a shade brighter.
Layout: one horizontal row of 2 equal 16:8 cells, image size 512x128 (each cell 256x128, 16 px a square); centered across, the ellipse on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `karthus_fx_w_shred.png`：W：魔抗被削的敌人头上（循环），2 帧

魔抗被削弱期间他头上：一个裂开的青蓝色小盾形符文，一明一暗（参考 w_ground、q_ring_blue）。**画在头上**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，符文在 38–46 格高）。**左右对称**，2 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue rim ramp (#FFFFFF, #CCF2FF, #7CD4FF, #3A9CF0, #1C5CC0, #102E78) and a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A).
Effect: A CRACKED SHIELD RUNE over a unit's head, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small shield outline 8 squares wide and 8 tall drawn in 1-square blue-white light lines, a vertical crack down its middle (1 square, dark gap); 1 dim teal; 2 bright blue-white.
Layout: one horizontal row of 2 equal square cells, image size 320x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `karthus_fx_r_cast.png`：R 安魂曲：引导 3 秒时他周围的灵魂（他身上，跟随），6 帧

安魂曲引导的 3 秒：他浮在空中唱歌（身体升起约 9 格），身后一层淡淡的青色光，一圈圈青绿色的灵魂绕着他往上盘旋，从地面一直到头顶上方，几点白色的光屑往上飘（参考 r_swirl、r_hagasphere、r_nova_ground、p_rays）。**只画他周围的灵魂和光，身体位置留空**（the lich stands in the middle, not drawn: 40 squares from his crown tip to the ground, 26 squares wide, his staff 4 squares more，浮起时脚离地 9 格）。**左右对称**，6 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A), a dark spirit smoke ramp (#7C8AA8, #56607E, #3A4260, #262B42, #161A2A) and a blue rim ramp (#FFFFFF, #CCF2FF, #7CD4FF, #3A9CF0, #1C5CC0, #102E78).
Effect: SOULS SPIRALLING UP round a floating figure, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the lich stands in the middle, not drawn: 40 squares from his crown tip to the ground, 26 squares wide, his staff 4 squares more, floating with his feet 9 squares above the ground): a faint pale-teal glow behind where he floats (an oval 30 squares wide and 46 tall, its edge 2 squares of light, hollow in the middle), a dark smoke ring on the ground (an ellipse 40 wide and 12 tall), and 8 teal-white soul wisps (3x5 squares, curled) spiralling up round the oval from the ground to 6 squares above his crown at mirrored places, each frame a sixth of the way higher (the top ones fading, new ones at the bottom), 6 white sparkle squares drifting up.
Layout: one horizontal row of 6 equal 48:72 cells, image size 4608x1152 (each cell 768x1152, 16 px a square); centered across, the cell's bottom row is the ground under him. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `karthus_fx_r_hit.png`：R：落到每个敌方英雄身上的安魂曲（跟随），6 帧

安魂曲打中每个敌方英雄：一道青白色的光柱从天上直直落到他身上，光柱边缘带一点深红，落地时一团青绿色的灵魂火炸开，然后散成烟（参考 r_target_light、r_spirit_explosion、r_streak）。**左右对称**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn）。6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A), a crimson ramp (#FFE0E0, #FF9AA4, #E8364E, #A8122E, #5C0818) and a dark spirit smoke ramp (#7C8AA8, #56607E, #3A4260, #262B42, #161A2A).
Effect: A BEAM FROM THE SKY onto a champion, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): 1 a thin white-teal beam 2 squares wide from the cell's top down to 30 squares above the ground; 2 the beam 6 squares wide reaching the ground, crimson edges, a white core; 3 the beam 10 wide, a burst of teal soul fire 18 squares wide and 14 tall at his feet and body; 4 the beam thinning, the soul fire 22 wide, 6 wisps flying up and out at mirrored places; 5 only the soul fire fading into dark smoke; 6 a few smoke puffs and embers.
Layout: one horizontal row of 6 equal 24:60 cells, image size 2304x960 (each cell 384x960, 16 px a square); centered across, the beam's foot on the cell's bottom row (his feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `karthus_fx_p_spirit.png`：被动死亡契约（附加包）：灵体的光（他身上，跟随，循环 7 秒），4 帧

死亡契约的灵体：他身后一层淡淡的青绿色幽光（贴着他的轮廓，比他大一圈），几片青白色的灵魂碎屑从他身上往上飘（参考 p_swirl、p_deathflakes、z_soul_fire、z_glow_cloud）。**身体位置留空，只画外圈的光和飘起的碎屑**（the lich stands in the middle, not drawn: 40 squares from his crown tip to the ground, 26 squares wide, his staff 4 squares more）。**左右对称**，4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, smoke, souls, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a ghostly teal-green soul light ramp (#FFFFFF, #D4FFF2, #8CF5D6, #3CD6B0, #1C9C88, #0E5C5A) and a dark spirit smoke ramp (#7C8AA8, #56607E, #3A4260, #262B42, #161A2A).
Effect: A GHOST GLOW round a standing figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the lich stands in the middle, not drawn: 40 squares from his crown tip to the ground, 26 squares wide, his staff 4 squares more): a pale teal glow 2-3 squares thick round an empty space shaped like him (an oval 30 squares wide and 44 tall standing on the ground), its edge flickering; 8 white-teal soul flakes (1x2 to 2x3 squares) drifting up from his shoulders and robe at mirrored places, each frame 3 squares higher (the top ones fading); frames 2 and 4 the glow a shade brighter.
Layout: one horizontal row of 4 equal 40:56 cells, image size 2560x896 (each cell 640x896, 16 px a square); centered across, the cell's bottom row is the ground under him. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `karthus_fx_a_bolt` | view_projectiles `league_karthus_a_bolt`（追踪弹，跟着方向转；上下对称；循环） | 14 × 8 |
| `karthus_fx_a_hit` | view_effects `league_karthus_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 14 |
| `karthus_fx_q_mark` | range_effect_name of the hidden lob → view_effects `league_karthus_q_mark`（落点上，不跟随，画在人物下面 z -1；左右对称；大图表） | 40 × 16 |
| `karthus_fx_q_boom` | end_effects of the hidden lob → view_effects `league_karthus_q_boom`（落点，不跟随，画在人物上面 z 2；左右对称；大图表） | 40 × 40 |
| `karthus_fx_q_hit` | view_effects `league_karthus_q_hit`（跟随敌人，画在人物上面 z 2；左右对称） | 14 × 14 |
| `karthus_fx_q_lone` | view_effects `league_karthus_q_lone`（跟随敌人，画在人物上面 z 2；左右对称） | 20 × 20 |
| `karthus_fx_e_on` | view_buffs `league_karthus_e_on`（跟随他，画在人物下面 z -1；左右对称；循环；大图表） | 64 × 26 |
| `karthus_fx_e_hit` | view_effects `league_karthus_e_hit`（跟随敌人，画在人物上面 z 2；左右对称） | 10 × 12 |
| `karthus_fx_w_wall` | lob end_effects → view_effects `league_karthus_w_wall`（不跟随，画在人物下面 z -1；左右对称；大图表） | 16 × 64 |
| `karthus_fx_w_slow` | view_buffs `league_karthus_w_slow`（跟随，画在人物下面 z 3；左右对称；循环） | 16 × 8 |
| `karthus_fx_w_shred` | view_buffs `league_karthus_w_shred`（跟随，画在人物上面 z 3；左右对称；循环） | 10 × 10 |
| `karthus_fx_r_cast` | view_effects `league_karthus_r_cast`（CasterViewEffect，跟随他，画在人物下面 z -1；左右对称；大图表） | 48 × 72 |
| `karthus_fx_r_hit` | view_effects `league_karthus_r_hit`（跟随目标，画在人物上面 z 2；左右对称；大图表） | 24 × 60 |
| `karthus_fx_p_spirit` | view_buffs `league_karthus_p_spirit`（附加包的副本里绑；跟随他，画在人物下面 z -1；左右对称；循环；大图表） | 40 × 56 |

- 两张表：`asset/league/effects/league_karthus_fx`（小的）和 `league_karthus_big`（q_mark、q_boom、e_on、w_wall、r_cast、r_hit、p_spirit），tag = 名字（build_karthus.py 的 views）。
- `a_bolt` 是追踪弹的画面（跟着方向转，所以朝右、上下对称）。`q_mark` 是隐形抛物线弹的 range_effect_name（飞行 32 tick 的整段都放在落点上），`q_boom` 在它落地的 end_effects 里；`w_wall` 在痛苦之墙那颗 1 tick 抛物线弹的 end_effects 里，要放满 5 秒（w_t 300 tick：3–6 帧循环）；`r_cast` 是 CasterViewEffect，要放满 3 秒（r_ch 180 tick）；`e_on` / `w_slow` / `w_shred` / `p_spirit` 是循环的view_buffs。其余跟随、左右对称。
- 用 `pixel_1x/` 切格（import_chogath_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
