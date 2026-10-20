# 流光镜影 梅尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图。** 造型已定（`design/mel_idle.png`：3/4 正面朝右的诺克萨斯贵族女法师，深棕色皮肤、高高的黑色卷发髻、金色额饰和大耳环，青绿色紧身连体衣、银白护甲，深红色长袍和喇叭袖、金色衬里，身后一条拖地的长袍）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），44 格高、39 格宽（连拖尾）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/mel_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/mel_shots.png`：动作帧（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里梅尔自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的魔法是耀眼的金色光**（白芯、金身），**带一点她长袍那种深红-粉红的火花和拖尾**；**大招鎏金蚀日是一轮金色的日蚀**（深色的圆盘、耀眼的金色日冕）；**W 是镜子一样的金色屏障**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：除了三张弹道图（a_bolt、p_bolt 头朝右；e_orb 本来就是圆的），其余**全部严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `mel_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/mel_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/mel_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（被动「灼灼之光」和 W「灵魂折镜」在里面） | 射出金色光弹；放技能后下次普攻多射 3 / 6 / 9 颗小光弹；每 25 秒第一次打中英雄时张开屏障 | `a_bolt` · `a_hit` · `p_bolt` · `p_hit` · `p_3` · `p_6` · `p_9` · `w_on` |
| 技能 1 = Q「耀光齐射」 | 一阵光弹落在目标那一点，连续爆炸 6 次 | `q_volley` · `q_hit` |
| 技能 2 = E「阳炎涡旋」 | 射出阳炎法球，中心禁锢、外圈减速并灼烧 | `e_orb` · `e_bound` · `e_slow` · `e_burn` |
| 大招「鎏金蚀日」 | 头顶升起日蚀，天降金光打所有带残影的敌人 | `r_cast` · `r_hit` |
| 附加包 | 夺命残影的印记、残影够了直接处决 | `m_mark` · `x_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、光环、光柱都没有黑描边，也不要用最深的颜色给形状描一圈边**（日蚀中间的深色圆盘本身是深色，可以）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 金色光（光弹、光雨、法球、光柱、屏障、光球）：`#FFFFFF`、`#FFF6C8`、`#FFE27A`、`#FFC23A`、`#E8921A`、`#A85A10`；
  - 深红-粉红的火花（拖尾、火花、点缀）：`#FFFFFF`、`#FFD0DC`、`#FF6F8E`、`#E3204E`、`#9C0F33`；
  - 日蚀（日冕和深色圆盘）：`#FFFFFF`、`#FFF2B0`、`#FFC94A`、`#D4831C`、`#5A2A1A`、`#24101A`；
- 打中、爆发居中画，不旋转；地面上的圆（光晕）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、她身边的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，Q 每次爆炸的半径 20000）。

### 1. `mel_fx_a_bolt.png`：普攻：金色光弹（弹道，循环），3 帧

她的普攻：一颗金色的光弹，**头朝右**（游戏会转到飞行方向）：亮白的菱形弹头，后面拖一小段由金到粉红的尾巴，尾巴一帧一帧闪动（参考 basicattack_constellation_line、basicattack_wisps、p_yellow_ray）。3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10) and a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: A RADIANT BOLT, 3 frames, a loop, pointing RIGHT (its head at the cell's right, its tail toward the left; the game turns it to its flight): a bright white-gold diamond head 4 squares long, behind it a tapering tail 7 squares long going from gold to crimson-pink, two tiny pink sparks trailing; each frame the tail flickers (its sparks at other places).
Layout: one horizontal row of 3 equal 12:7 cells, image size 576x112 (each cell 192x112, 16 px a square); the bolt centred vertically, its head touching the cell's right side. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `mel_fx_p_bolt.png`：灼灼之光：小光弹（弹道，循环），3 帧

放技能后下一次普攻多射出的小光弹：比普攻的小一号，粉金色，**头朝右**，3 帧循环（参考 p_flecks、p_glowdust）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33) and a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10).
Effect: A SMALL SPARK BOLT, 3 frames, a loop, pointing RIGHT (its head at the cell's right, its tail toward the left; the game turns it to its flight): a white-pink head 2 squares long with a short gold-pink tail 4 squares long; the tail flickering.
Layout: one horizontal row of 3 equal 8:5 cells, image size 384x80 (each cell 128x80, 16 px a square); the bolt centred vertically, its head touching the cell's right side. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `mel_fx_a_hit.png`：普攻打中：金色星芒，4 帧

光弹打中目标：一颗金色的星芒炸开（白芯、四道长芒四道短芒），然后散成几点金色和粉红的光点（参考 basicattack_mark_mult、w_impact_flare、r_hit1）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10) and a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: A RADIANT HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white core flash 4 squares across; 2 an eight-point gold star 14 squares across (four long rays, four short diagonal ones); 3 the star thinner, gold and pink motes flying out at mirrored places; 4 only fading motes.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `mel_fx_p_hit.png`：小光弹打中，3 帧

小光弹打中：一个小小的粉金色火花，3 帧，**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: A SMALL SPARK, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink plus sign 5 squares across; 2 a pink four-point star 8 across; 3 two fading pink motes at mirrored places.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `mel_fx_p_3.png`：灼灼之光：蓄好 3 颗光弹（她身上，循环），4 帧

放了一个技能后，下一次普攻会多射 3 颗光弹：她腰两边浮着 **3 颗**小小的金色光球（中间一颗、左右各一颗，排成一道微弯的弧），一闪一闪地上下浮动（参考 p_glowdust、packed_glows）。**她站在中间不画人**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10).
Effect: THREE FLOATING LIGHT ORBS round a mage's waist, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the noblewoman mage stands in the middle, not drawn: 43 squares from the top of her hair bun to the ground, about 40 squares wide with her robe, her body area left EMPTY): three small gold orbs, each 3 squares across with a white core, on a gentle arc across the cell (one at the middle top, one at each end a little lower, 36 squares apart end to end); each frame they bob a square up or down in turn and glimmer.
Layout: one horizontal row of 4 equal 44:14 cells, image size 2816x224 (each cell 704x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `mel_fx_p_6.png`：灼灼之光：蓄好 6 颗光弹（她身上，循环），4 帧

放了两个技能：**6 颗**光球（左右各 3 颗，排成两道弧），其它同 p_3。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10).
Effect: SIX FLOATING LIGHT ORBS round a mage's waist, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the noblewoman mage stands in the middle, not drawn: 43 squares from the top of her hair bun to the ground, about 40 squares wide with her robe, her body area left EMPTY): six small gold orbs (3 squares across, white cores), three on each side on two mirrored arcs, 40 squares apart end to end; they bob and glimmer in turn.
Layout: one horizontal row of 4 equal 48:18 cells, image size 3072x288 (each cell 768x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `mel_fx_p_9.png`：灼灼之光：蓄满 9 颗光弹（她身上，循环），4 帧

蓄满了：**9 颗**光球围成一个扁圆的环（前面中间一颗最亮），金色更亮，带一点粉红的光晕，其它同 p_3。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10) and a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: NINE FLOATING LIGHT ORBS in a flat ring round a mage's waist, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the noblewoman mage stands in the middle, not drawn: 43 squares from the top of her hair bun to the ground, about 40 squares wide with her robe, her body area left EMPTY): nine gold orbs (3 squares across, white cores, a faint pink halo) on a flat ellipse 46 squares wide and 16 tall, the front middle one the brightest; each frame they glimmer in turn.
Layout: one horizontal row of 4 equal 52:22 cells, image size 3328x352 (each cell 832x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `mel_fx_q_volley.png`：Q 耀光齐射：一阵光弹从天而降（地上那一点，不跟随），8 帧

Q 的落点：**六颗金色光弹从正上方一颗接一颗砸下来**，落在一个约 36 格宽的椭圆范围里（落点左右对称地分布），每颗落地炸成一朵小金星，地上一圈淡淡的金色光晕（参考 q_flame_ring、r_airbullet、r_hit3）。一共 8 帧（约 0.6 秒，和 Q 连续 6 次爆炸对上）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10) and a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: A VOLLEY OF FALLING BOLTS onto a spot, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a faint gold ground ellipse 36 squares wide and 10 tall at the cell's bottom; six radiant bolts (each a white-gold streak 2 squares wide, 10 tall, a pink tail above it) fall STRAIGHT DOWN from the top of the cell one after another, landing at mirrored spots inside the ellipse, two at a time: 1 two streaks high up; 2 those two lower, two more appearing at the top; 3 the first two land - two small gold stars (8 across) on the ground; 4-6 the same for the next pairs, the stars of the earlier ones fading into motes; 7 the last stars and motes; 8 only the fading ground ellipse and motes.
Layout: one horizontal row of 8 equal 48:56 cells, image size 6144x896 (each cell 768x896, 16 px a square); centered across, the ground ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `mel_fx_q_hit.png`：Q：爆炸打中（敌人身上），3 帧

每次爆炸打中一个敌人：一朵金粉色的小爆光，3 帧，**左右对称**（参考 r_hit3）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10) and a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: A SMALL GOLD-PINK BURST, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white core 4 squares; 2 a round gold burst 12 across with pink edges; 3 broken into pink and gold motes, fading.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `mel_fx_e_orb.png`：E 阳炎涡旋：阳炎法球（弹道，循环），4 帧

E 射出的阳炎法球：一颗小太阳，白芯金身，外面一圈短短的金色光芒（像太阳的光刺），再外面一圈淡淡的粉红光晕，光芒一帧一帧转动（参考 e_tar_center、e_tar_centerglowpattern、e_scroll、q_flame_ring）。圆的，**上下左右都对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10) and a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: A RADIANT SUN ORB in flight, 4 frames, a loop, symmetric in every direction: a white-gold core 10 squares across, a ring of twelve short gold sun rays round it (each 3-4 squares), a faint crimson-pink halo ring outside them; each frame the rays turn a little (one twelfth of a turn) and the core pulses.
Layout: one horizontal row of 4 equal square cells, image size 1792x448 (each cell 448x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `mel_fx_e_bound.png`：E：禁锢（被禁锢的敌人身上，循环），4 帧

被法球中心禁锢住的敌人：两道扁扁的金色光环一上一下箍住他的腿和腰，环上带着太阳光刺，一闪一闪地收紧（参考 e_wall、e_aoe_mult、e_binarymult）。**被禁锢的人站在中间不画**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10).
Effect: A SOLAR SNARE ROUND A CHAMPION, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn, the body area left EMPTY): two flat gold light rings (ellipses 22 wide and 6 tall, 2 squares thick, white inner edge), one at the knees and one at the waist, short sun-ray spikes standing out of them at mirrored places; the rings pulse tighter and brighter on frames 1 and 3.
Layout: one horizontal row of 4 equal 26:30 cells, image size 1664x480 (each cell 416x480, 16 px a square); centered across, the lower ring 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `mel_fx_e_slow.png`：E：外圈减速的光晕（敌人脚下，循环），4 帧

被法球外圈扫到、减速中的敌人：脚下一圈金色的光晕，几点金色的光尘往上飘（参考 e_aoe_damagehotspot、e_groundtrail）。**只画在脚下**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10).
Effect: A GOLD GLOW under a champion's feet, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a glowing gold ellipse on the ground 22 squares wide and 6 tall, its rim brightest; a few gold dust motes rising from it at mirrored places, a little higher each frame, new ones starting low.
Layout: one horizontal row of 4 equal 26:10 cells, image size 1664x160 (each cell 416x160, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `mel_fx_e_burn.png`：E：灼烧（敌人身上），3 帧

外圈的持续伤害每跳一次：一小簇金橙色的火苗往上一窜（参考 deathfire_mask、q_flame_ring），3 帧，**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10).
Effect: A SMALL GOLD FLAME LICK, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small gold flame 4 wide, 5 tall at the bottom middle; 2 it rises to 9 tall with a white core and two tongues; 3 broken into gold sparks drifting up.
Layout: one horizontal row of 3 equal 12:14 cells, image size 576x224 (each cell 192x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `mel_fx_r_cast.png`：R 鎏金蚀日：头顶升起日蚀（她身上，跟随），8 帧

R：她头顶上方升起一轮**金色的日蚀**——中间一个深色的圆盘（深紫黑），一圈耀眼的金色日冕，长长的细金光往四周放射，越来越亮，最后一闪（参考 r_centershine、r_glow、r_s_05、r_space、r_zone_aoe_glow）。**她站在格子下半部不画人，日蚀在她头顶上方**，**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an eclipse ramp (#FFFFFF, #FFF2B0, #FFC94A, #D4831C, #5A2A1A, #24101A).
Effect: A GOLDEN ECLIPSE rising over a mage's head, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the noblewoman mage stands in the middle, not drawn: 43 squares from the top of her hair bun to the ground, about 40 squares wide with her robe in the lower part of the cell, her standing point at the bottom middle, her body area left EMPTY): high above her (its centre 14 squares under the cell's top) 1 a small gold spark; 2 a gold ring 8 across; 3 the ring 16 across with a DARK DISC (deep plum-black) filling it; 4 the corona - a blazing gold rim 2-3 squares thick round the dark disc, eight long thin gold rays reaching out 10-14 squares; 5 the rays longer, a white flash on the rim; 6 like 4, brighter; 7 the rays shrinking, the disc fading to gold; 8 only fading gold motes.
Layout: one horizontal row of 8 equal 64:80 cells, image size 8192x1280 (each cell 1024x1280, 16 px a square); centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `mel_fx_r_hit.png`：R：天降金光（每个带残影的敌人身上），6 帧

R 打中每一个带残影的敌人：一道金色的光柱从天上直直劈到他身上，脚下炸开一朵金星，光柱慢慢变细消失（参考 r_skybeam、r_evolve_godlay、r_hit1、r_hit3）。**光柱竖直、从格子顶上一直到底**，敌人站在格子底部中间（不画人），**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10) and a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: A GOLDEN SKY BEAM striking a champion, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn at the bottom middle, not drawn): 1 a thin white line straight down from the top of the cell to the ground at the bottom middle; 2 the beam 6 squares wide, white core, gold edges, the full height; 3 the beam full and a gold star 18 squares across bursting on the ground at its foot, pink sparks; 4 the beam thinner, the star becoming a ring; 5 only a thin beam and motes; 6 fading motes.
Layout: one horizontal row of 6 equal 24:60 cells, image size 2304x960 (each cell 384x960, 16 px a square); centered across, the beam's foot on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `mel_fx_w_on.png`：W 灵魂折镜：屏障（她身上，循环），4 帧

W 的屏障：一层**像镜子一样的金色护罩**罩住她：高高的蛋形外壳（只画边：2 格宽的淡金亮边），上面有几道直直的折线像镜面的切面，几处白色的反光一帧一帧移动（参考 shield、w_shieldmask28、w_reflect_color_ramp、w_impact_flare）。**她站在中间不画人，只画罩子的边、切面线和反光**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a radiant gold ramp (#FFFFFF, #FFF6C8, #FFE27A, #FFC23A, #E8921A, #A85A10).
Effect: A MIRROR-GOLD BARRIER round a mage, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the noblewoman mage stands in the middle, not drawn: 43 squares from the top of her hair bun to the ground, about 40 squares wide with her robe, her body area left EMPTY): a tall egg-shaped shell outline round her, 56 squares wide and 62 tall, its bottom open at the ground, its rim 2 squares of pale gold with a white inner edge; a few straight facet lines across its upper part like the cuts of a mirror (mirrored left and right); white glints on the rim that move a few squares round it each frame.
Layout: one horizontal row of 4 equal 60:64 cells, image size 3840x1024 (each cell 960x1024, 16 px a square); centered across, the shell's open bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `mel_fx_m_mark.png`：附加包：夺命残影（敌人头上，循环），4 帧

附加包里带残影的敌人头上：一个小小的金色日蚀印记（金环、深色的芯），一明一暗地跳动（参考 basicattack_mark_mult、r_circle_normal）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an eclipse ramp (#FFFFFF, #FFF2B0, #FFC94A, #D4831C, #5A2A1A, #24101A).
Effect: A SMALL ECLIPSE SIGIL over a head, 4 frames, a loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a gold ring 8 squares across, 2 squares thick, round a dark plum-black core, four tiny gold rays (up, down, left, right); 1 dim, 2 bright, 3 the brightest with a white glint on the rim, 4 dim again.
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `mel_fx_x_hit.png`：附加包：残影处决（敌人身上），6 帧

附加包里残影够了直接处决：敌人身上的日蚀印记猛地一亮，炸成一大片金色碎片和粉红的火花，中间一道竖直的金光（参考 r_evolve_blast、z_backblast、r_hit1）。**被处决的人站在中间不画**，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an eclipse ramp (#FFFFFF, #FFF2B0, #FFC94A, #D4831C, #5A2A1A, #24101A) and a crimson-pink spark ramp (#FFFFFF, #FFD0DC, #FF6F8E, #E3204E, #9C0F33).
Effect: AN ECLIPSE EXECUTION BURST on a champion, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn, the body area left EMPTY in frames 1-2): 1 an eclipse sigil (gold ring, dark core) 10 squares across at chest height; 2 the sigil flashing white, 16 across; 3 it bursts - gold shards (small triangles) flying out in a mirrored ring 36 across, a white vertical light 14 squares tall at the middle, pink sparks; 4 the shards further out, smaller; 5 only shards and motes; 6 fading motes.
Layout: one horizontal row of 6 equal 40:48 cells, image size 3840x768 (each cell 640x768, 16 px a square); centered across, the sigil's middle 26 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `mel_fx_a_bolt` | view_projectiles `league_mel_a_bolt`（弹道：游戏会把它转到飞行方向；附加包反弹回去的光弹也用这张） | 12 × 7 |
| `mel_fx_p_bolt` | view_projectiles `league_mel_p_bolt`（弹道，游戏会转到飞行方向） | 8 × 5 |
| `mel_fx_a_hit` | view_effects `league_mel_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `mel_fx_p_hit` | view_effects `league_mel_p_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `mel_fx_p_3` | view_buffs `league_mel_p_3`（跟随她，z 2；左右对称；循环） | 44 × 14 |
| `mel_fx_p_6` | view_buffs `league_mel_p_6`（跟随她，z 2；左右对称；循环） | 48 × 18 |
| `mel_fx_p_9` | view_buffs `league_mel_p_9`（跟随她，z 2；左右对称；循环） | 52 × 22 |
| `mel_fx_q_volley` | view_effects `league_mel_q_volley`（放在落点上，不跟随，画在人物上面 z 3；左右对称；大图表） | 48 × 56 |
| `mel_fx_q_hit` | view_effects `league_mel_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `mel_fx_e_orb` | view_projectiles `league_mel_e_orb`（弹道，游戏会转到飞行方向；大图表） | 28 × 28 |
| `mel_fx_e_bound` | view_buffs `league_mel_e_bound`（跟随目标，z 3；左右对称；循环） | 26 × 30 |
| `mel_fx_e_slow` | view_buffs `league_mel_e_slow`（跟随目标，画在人物下面 z -1；左右对称；循环） | 26 × 10 |
| `mel_fx_e_burn` | view_effects `league_mel_e_burn`（跟随目标，z 2；左右对称） | 12 × 14 |
| `mel_fx_r_cast` | view_effects `league_mel_r_cast`（跟随她，画在人物上面 z 2；左右对称；大图表） | 64 × 80 |
| `mel_fx_r_hit` | view_effects `league_mel_r_hit`（跟随目标，z 2；左右对称；大图表） | 24 × 60 |
| `mel_fx_w_on` | view_buffs `league_mel_w_on`（跟随她，画在人物上面 z 3；左右对称；循环；大图表） | 60 × 64 |
| `mel_fx_m_mark` | view_buffs `league_mel_m_mark`（附加包；跟随目标，z 3；左右对称；循环） | 14 × 12 |
| `mel_fx_x_hit` | view_effects `league_mel_x_hit`（附加包；跟随目标，z 2；左右对称；大图表） | 40 × 48 |

- 两张表：`asset/league/effects/league_mel_fx`（小的）和 `league_mel_big`（q_volley、e_orb、r_cast、r_hit、w_on、x_hit），tag = 名字（build_mel.py 的 views；w_on 绑在 buff `league_mel_w_on` 上，p_3 / p_6 / p_9 绑在同名 buff 上；附加包的反弹光弹 w_back 用 a_bolt 的帧）。
- 除了三张弹道图，全部断言左右对称；`e_slow` 画在人物下面（z -1），`q_volley`、`e_bound`、`m_mark`、`w_on` 在上面（z 3）。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉给光描的最深色边（日蚀的深色圆盘保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。用户也可能用 Gemini 画好直接给图片（沃里克的做法：process_warwick_fx.py）。
