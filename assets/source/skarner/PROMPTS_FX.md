# 上古领主 斯卡纳：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图。** 造型已定（`design/skarner_design.png`：左边是 Q 版水晶蝎子——青绿甲壳、橙白花纹、骨白骷髅小脸和银白头甲、两只大钳子、三根带青绿水晶毒刺和橙色核心的尾巴、六条钩爪腿；右边是同一个他用尾巴举着**灰绿色的大巨石**）。斯卡纳在游戏里是**高清**的（每个游戏格子里约 1.75×1.75 个细像素），34 格高、46 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/skarner_size.png`：斯卡纳（和举石的他）缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里斯卡纳自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**斯卡纳是以绪塔尔的上古水晶蝎子，特效都是水晶和大地**：**青绿水晶**（白色棱面到深青）、毒刺的**橙色核心**、地震的**沙尘、碎石**、巨石的**灰绿色石头**；不要光滑的霓虹光束，不要火，也不要魔法漩涡。
> - **特效要亮**：每道光、每片水晶都有最亮一档或白色的高光，暗底上一眼能看见。
> - **光、沙尘、速度线没有黑描边**（碎水晶、碎石也不要描黑边，用它自己最深的一档）；**只有巨石（`q_rock`、`q_held`）和尾巴毒刺（`r_spike`）这几个“东西”有 1 格近黑描边**。
> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人。
> - **对称**：除了两个弹道，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`q_rock`、`r_spike`）**朝右飞、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `skarner_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/skarner_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/skarner_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 毒刺扎 + 钳子夹 | `a_hit` |
| 被动「战栗」（并入 W 震地壁垒） | 普攻、巨石、毒刺贯体叠战栗，满层每秒掉最大生命值；冲锋拖完人时出护盾 + 地震波 | `p_quake` · `p_burst` · `w_quake` · `w_shield` · `w_hit` · `slow` |
| 技能 1 =「撼地 / 擎天」 | 从地里掘出巨石举着，强化 3 下普攻（周围的人一起受伤，第 3 下打最大生命值 + 减速）；举久了就扔出去 | `q_held` · `q_hit` · `q_rock` · `q_land` · `slow` |
| 技能 2 =「以绪塔尔冲击」 | 往前冲锋，撞上英雄拖着走，砸停晕眩 | `e_hit` · `e_slam` · `stun` |
| 大招 =「毒刺贯体」 | 三根尾巴往前扎，压制线上的英雄并拖着走，自己加速 | `r_spike` · `r_hit` · `r_held` · `r_haste` |

连招：**举着巨石放大招 → 先扔出擎天**，**冲锋拖完人 → 撼地马上好**，**大招扎中 → 战栗直接叠满**，**巨石第 3 下打中英雄 → 冲锋冷却缩短**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、沙尘、速度线没有黑描边，也不要用最深的颜色给形状描一圈边**（巨石、毒刺除外）。
- **都是水晶和大地**：青绿、橙、沙土、灰绿；每个形状 2–3 档平涂，水晶用棱角分明的几何面。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 水晶·青绿：`#FFFFFF`、`#D2FBFF`、`#84F0F0`、`#33C8D2`、`#138C9E`、`#0B5468`；
  - 核心·橙：`#FFF4CC`、`#FFC462`、`#FF7A1E`、`#D8400C`、`#8A2006`；
  - 大地·沙尘：`#F0E6D0`、`#CDBB98`、`#9C8A6A`、`#6E5E46`、`#463A2A`；
  - 巨石·灰绿：`#DCE4D0`、`#AABA9E`、`#7E8E74`、`#56644E`、`#38422F`；
- 打中、爆发居中画，不旋转；地面上的圈（地震、裂纹、沙尘）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `skarner_fx_a_hit.png`：普攻：毒刺扎中，3 帧

水晶毒刺扎在敌人身上：中间一下白光，一圈青绿的碎水晶往外崩，夹着两三点橙色火星（参考 hiteffect、r_hit_flash_spikes、p_impacttero）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468), an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006).
Effect: A CRYSTAL STINGER STAB LANDING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-teal flash 6 squares across with a small orange core; 2 a ring of angular teal crystal shards bursting out 12 across at mirrored places, two orange sparks; 3 the shards further out, dimming into dust. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `skarner_fx_p_quake.png`：战栗：脚下一直在震，4 帧循环

被战栗的人（掉最大生命值的魔法伤害，4 秒）：脚下的地面裂开、一圈细裂纹一闪一闪，裂缝里透出橙色的光，几颗小石子往上跳（参考 w_cracks_light、revive_ground_crack、p_rockbits）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A), an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006).
Effect: A QUAKING GROUND AT THE FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): an ellipse of cracked ground 16 wide, thin dark cracks glowing orange inside; frames 1-4 the cracks flickering in turn and a few small pebbles hopping up 2-3 squares and falling at mirrored places. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `skarner_fx_p_burst.png`：战栗：满层开始战栗，5 帧

战栗叠满的一刻：目标身上一圈震波往外一荡，几片青绿水晶和橙色碎光往外崩（参考 distortion_soundwaves、ba_ring、spark_round_bloom）。光只画在外圈，**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468), an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006), an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A).
Effect: A TREMOR BURSTING AROUND A UNIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a thin orange ring 8 across at the middle; 2 a teal-and-white vibration ring 18 across with small crystal shards on it; 3 the ring 22 across, orange sparks flying out at mirrored places; 4 two faint ripple arcs at both sides, dust; 5 the last sparks fading. The middle (the body) left empty. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 5 equal square cells, image size 1920x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `skarner_fx_q_hit.png`：撼地：举着巨石砸中，4 帧

举着巨石时的强化普攻打中（周围的人一起受伤）：一下白光，一圈灰绿的碎石块和沙尘往四周崩开（参考 q_impact_cross、q_impactspike、q_rocks、q_smoke_dust）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-green stone ramp (#DCE4D0, #AABA9E, #7E8E74, #56644E, #38422F), an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A).
Effect: A BOULDER-EMPOWERED BLOW LANDING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 across; 2 a burst of grey-green rock chunks (2-3 squares each) flying out 16 across at mirrored places; 3 the chunks further out and a puff of sand dust 18 across; 4 the dust settling, a few pebbles falling. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 4 equal 20:18 cells, image size 1280x288 (each cell 320x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `skarner_fx_q_land.png`：擎天：巨石砸在地上，5 帧

扔出去的巨石落地砸开：地上砸出一个坑，一圈碎石和尘土往外炸开（参考 q_craterobsi、q_rockpickup_halfcrater、q_blastshapes、q_groundsmoke）。**正面看，左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-green stone ramp (#DCE4D0, #AABA9E, #7E8E74, #56644E, #38422F), an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A).
Effect: A BOULDER CRASHING INTO THE GROUND, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), seen from the front-above, centred on the ground point: 1 a white impact flash 10 wide; 2 a dark crater ellipse 18 wide, grey-green rock fragments flying up and out to both sides; 3 a ring of sand dust 30 wide rolling out, fragments at their highest; 4 the dust ring 34 wide, fragments falling; 5 the dust thinning around a cracked crater. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 5 equal 36:18 cells, image size 2880x288 (each cell 576x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `skarner_fx_q_rock.png`：擎天：飞出去的巨石，2 帧循环

扔出去在空中飞的巨石：照 `design/skarner_design.png` 右边那块**灰绿色多面体巨石**画（缩到游戏大小，几道裂缝），后面拖一缕沙尘。**朝右飞、上下对称**，2 帧循环（石头稍微转一下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-green stone ramp (#DCE4D0, #AABA9E, #7E8E74, #56644E, #38422F), an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A).
Effect: THE THROWN BOULDER IN FLIGHT, 2 looping frames, drawn FLYING TO THE RIGHT (its back on the left) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight): a faceted grey-green boulder 11 wide and 10 tall with a few dark cracks (the boulder of the design picture), a short trail of sand dust behind it on the left; frame 2 the boulder turned a little, its facets shifted. Every stone square has a 1-square near-black outline (it is a solid thing), the dust none. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 2 equal 16:14 cells, image size 512x224 (each cell 256x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `skarner_fx_q_held.png`：撼地：举在背上的巨石，4 帧循环

举着巨石的时候（强化 3 下普攻或者扔出去之前），他背上一直有这块巨石：照 `design/skarner_design.png` 右边那块巨石画（灰绿色多面体、几道裂缝），**横着摆、在格子的上半部、左右居中**，大约 34 格宽、16 格高，底边差不多在格子从下往上 28 格的地方（他的三根毒刺就扎在巨石底下）；石头下面几颗小石子和沙往下掉。格子下半部是他自己的身体，**留空、不要画他**。**左右对称**，4 帧循环（只有掉下来的小石子在动）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-green stone ramp (#DCE4D0, #AABA9E, #7E8E74, #56644E, #38422F), an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A).
Effect: A BIG BOULDER HELD UP OVER A SCORPION'S BACK, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Skarner stands in the middle, not drawn: about 46 squares wide and 34 tall (a low, wide scorpion) in the lower part of the cell: in the UPPER part, centred left to right, a long faceted grey-green boulder lying sideways, 34 squares wide and 16 tall, its bottom edge about 28 squares above the bottom of the cell, a few dark cracks across it (the boulder of the design picture); frames 1-4 the boulder still, small pebbles and sand trickling down from its underside at mirrored places. The lower part (his body) left empty. Every stone square has a 1-square near-black outline (it is a solid thing), the sand none. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 4 equal 64:56 cells, image size 4096x896 (each cell 1024x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `skarner_fx_slow.png`：减速：脚下一圈沙尘，4 帧循环

被减速：脚下一圈翻起来的沙尘和小石子，裂纹里一点点青光。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A), a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468).
Effect: A DUST SLOW AT THE FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a thin ellipse of churned sand 14 wide with small pebbles and two faint teal glints; frames 1-4 the sand swirling slowly and a few grains drifting up. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `skarner_fx_w_quake.png`：震地壁垒：地震冲击波，6 帧

冲锋拖完人以后他砸地：从他脚下**一圈地震波往外推开**——地面裂开、一圈碎石和沙尘往外滚，裂缝里透出橙色和青色的光（参考 w_ring_shockwave、shockwave、w_cracks_erosion、w_rocks、w_smoke）。地震的范围要大：最大时**横向 80 格、纵向 26 格**（比他身子宽一倍）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A), an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006), a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468).
Effect: AN EARTHQUAKE SHOCKWAVE AROUND HIM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred, growing to a BIG ellipse 80 squares wide and 26 tall: 1 a bright crack star 16 wide, orange light in the cracks; 2 a ring of churned ground and rock bits 36 wide rolling out; 3 the ring 56 wide, rock chunks thrown up at both sides, teal crystal glints in the cracks; 4 the ring 72 wide, a wall of sand dust along it; 5 the ring 80 wide breaking into dust puffs, the cracked ground behind it; 6 the dust thinning, the last cracks fading. Frames 4-6 MUST reach 80 squares across. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 6 equal 84:28 cells, image size 8064x448 (each cell 1344x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `skarner_fx_w_shield.png`：震地壁垒：身上的水晶护盾，6 帧循环

护盾在的 3 秒里：他身外一层**半透明感的青绿水晶外壳**——用一圈棱角分明的水晶面围住他的轮廓（只画边缘那一圈和几块亮面，中间是他自己），几处亮面一闪一闪（参考 w_shield_pan、w_sheen、shield_bubble）。**只画外圈，身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468).
Effect: A CRYSTAL SHIELD AROUND A SCORPION, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Skarner stands in the middle, not drawn: about 46 squares wide and 34 tall (a low, wide scorpion): a ring of angular teal crystal facets outlining him, 50 squares wide and 38 tall, drawn as a thin shell (2-3 squares thick) with a few bigger bright facets on top; frames 1-6 a white glint travelling over the facets around the shell. The middle (his body) left empty. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 6 equal 54:42 cells, image size 5184x672 (each cell 864x672, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `skarner_fx_w_hit.png`：震地壁垒：被地震打中，4 帧

地震波打到的人：脚下的地面往上一顶，碎石和沙尘从他脚下冲上来。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A), an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006).
Effect: A QUAKE HITTING A UNIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a crack with orange light at the feet; 2 rock bits and sand bursting up 10 squares at both sides of the feet; 3 the bits at their highest, a dust cloud 16 wide; 4 the dust settling. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `skarner_fx_e_hit.png`：以绪塔尔冲击：撞上英雄，4 帧

冲锋撞上英雄的一下（接着把他拖走）：一下白光，一圈沙尘和碎水晶往两边炸开（参考 e_skirt、p_dust、sandstreaks）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A), a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468).
Effect: A CHARGE SLAMMING INTO A UNIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 across; 2 a burst of sand dust and teal crystal shards 18 across at mirrored places; 3 two dust plumes thrown out to both sides; 4 the dust thinning. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 4 equal 22:20 cells, image size 1408x320 (each cell 352x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `skarner_fx_e_slam.png`：以绪塔尔冲击：砸停、晕眩，5 帧

拖着的英雄被砸停（晕眩）：他身上炸开一圈碎石和水晶，橙色的光一冲，周围的地面裂开（附加包里是撞在墙上）（参考 crater_mesh_erode、q_impactspike、r_impact_flare）。光和碎石只画在外圈，**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A), a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468), an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006).
Effect: A UNIT SLAMMED HARD AND STUNNED, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 an orange flash at the middle 10 across; 2 a ring of rock chunks and teal crystal shards bursting out 24 across; 3 orange light flaring up 20 squares at both sides, cracks in the ground at the feet; 4 dust rolling out at both sides; 5 the last bits falling. The middle (the body) left empty. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 5 equal 28:30 cells, image size 2240x480 (each cell 448x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `skarner_fx_stun.png`：晕眩：头上转圈的水晶碎片，4 帧循环

被晕住的人：头顶一圈小小的青绿水晶碎片和橙色亮点在转。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468), an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006).
Effect: A STUN OVER THE HEAD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small flat ellipse 14 wide of four tiny teal crystal shards and two orange sparks circling; frames 1-4 the shards moved a quarter round each frame, mirrored left to right. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `skarner_fx_r_spike.png`：毒刺贯体：尾巴扫出去的那一下，3 帧循环

三根尾巴往前一起扎出去：一道往前飞的冲击——**三枚青绿水晶毒刺**一前两后排成一个箭头，尖朝右，后面拖着橙色和青色的速度线（参考 r_tap_spear_sharp、r_wave_texture、r_wave_child_speedlines、r_missile_head）。**朝右飞、上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468), an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006).
Effect: THREE CRYSTAL STINGERS LASHING FORWARD, 3 looping frames, drawn FLYING TO THE RIGHT (its back on the left) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight): three teal crystal stinger tips with orange cores, one in front at the middle and two a little behind above and below (an arrowhead 14 squares long, 10 tall), all pointing right, with streaks of orange and teal speed lines trailing 20 squares behind them; frames 1-3 the speed lines flickering and the tips glinting in turn. Every crystal square has a 1-square near-black outline, the speed lines none. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 3 equal 36:14 cells, image size 1728x224 (each cell 576x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `skarner_fx_r_hit.png`：毒刺贯体：扎中英雄，5 帧

毒刺扎中、把人压制住：目标身上一下橙色的亮闪，一圈尖尖的水晶刺往外炸，然后几道橙色的光丝缠住他（参考 r_hit_flash_spikes、r_impact_flare、suppress、r_mark_distort）。光只画在外圈，**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006), a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468).
Effect: A UNIT IMPALED AND SUPPRESSED, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 an orange-white flash 10 across at the middle; 2 a star of sharp teal crystal spikes bursting out 24 across; 3 the spikes breaking off, thin orange light threads wrapping around the unit at both sides; 4 the threads tightening, orange motes; 5 a faint orange ring. The middle (the body) left empty. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 5 equal 26:30 cells, image size 2080x480 (each cell 416x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `skarner_fx_r_held.png`：毒刺贯体：被压制拖着走，6 帧循环

被压制的 1.5 秒里：目标身上**一圈橙色的光丝**把他捆住，头顶上方三枚小小的水晶毒刺尖朝下扎着他（参考 suppress、suppress_dark、generic_string_strands）。只画外圈和头顶，**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange core ramp (#FFF4CC, #FFC462, #FF7A1E, #D8400C, #8A2006), a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468).
Effect: A SUPPRESSED UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: a loose ring of thin glowing orange threads around the unit's middle, 24 wide, seen slightly from above, and above its head three small teal crystal stinger tips pointing down at it; frames 1-6 the threads pulsing brighter in turn, a few orange motes drifting. The middle (the body) left empty. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 6 equal 26:34 cells, image size 2496x544 (each cell 416x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `skarner_fx_r_haste.png`：毒刺贯体：加速的沙尘，4 帧循环

扎中人以后他加速：脚下两边扬起一溜沙尘和速度线（参考 sandstreaks、r_air_trail）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth and dust ramp (#F0E6D0, #CDBB98, #9C8A6A, #6E5E46, #463A2A), a teal crystal ramp (#FFFFFF, #D2FBFF, #84F0F0, #33C8D2, #138C9E, #0B5468).
Effect: A HASTE AT A SCORPION'S FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), Skarner stands in the middle, not drawn: about 46 squares wide and 34 tall (a low, wide scorpion): a flat band of sand dust 48 wide along the ground with short horizontal speed streaks at both ends and two faint teal glints; frames 1-4 the streaks flickering and the dust puffs rolling outward at both ends. everything is IXTAL'S LIVING CRYSTAL and the EARTH of a giant scorpion: faceted teal crystal with white facets and deep-teal shade, glowing orange crystal cores, sand, dust and brown rock bits, the boulder's grey-green stone; flat shades, crisp angular shapes; no smooth neon beams, no fire, no magic swirls.
Layout: one horizontal row of 4 equal 50:12 cells, image size 3200x192 (each cell 800x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `skarner_fx_a_hit` | view_effects `league_skarner_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `skarner_fx_p_quake` | view_buffs `league_skarner_p_quake`（跟随目标，脚下，z -1；左右对称） | 18 × 8 |
| `skarner_fx_p_burst` | view_effects `league_skarner_p_burst`（跟随目标，z 2；左右对称） | 24 × 24 |
| `skarner_fx_q_hit` | view_effects `league_skarner_q_hit`（跟随目标，z 2；左右对称） | 20 × 18 |
| `skarner_fx_q_land` | view_effects `league_skarner_q_land`（地上，z 1，不跟随；左右对称） | 36 × 18 |
| `skarner_fx_q_rock` | view_projectiles `league_skarner_q_throw`（弹道，z 2；朝右画、上下对称） | 16 × 14 |
| `skarner_fx_q_held` | view_buffs `league_skarner_rock`（大表，跟随斯卡纳，z 3；左右对称） | 64 × 56 |
| `skarner_fx_slow` | view_buffs `league_skarner_q_slow` / `league_skarner_w_slow`（跟随，脚下，z -1；左右对称） | 16 × 8 |
| `skarner_fx_w_quake` | view_effects `league_skarner_w_quake`（大表，地上，z -1，不跟随；左右对称） | 84 × 28 |
| `skarner_fx_w_shield` | view_buffs `league_skarner_w_on`（跟随斯卡纳，z 3；左右对称） | 54 × 42 |
| `skarner_fx_w_hit` | view_effects `league_skarner_w_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `skarner_fx_e_hit` | view_effects `league_skarner_e_hit`（跟随目标，z 2；左右对称） | 22 × 20 |
| `skarner_fx_e_slam` | view_effects `league_skarner_e_slam`（跟随目标，z 2；左右对称） | 28 × 30 |
| `skarner_fx_stun` | view_buffs `league_skarner_e_stun`（跟随目标，头顶，z 3；左右对称） | 16 × 8 |
| `skarner_fx_r_spike` | view_projectiles `league_skarner_r_lash`（大表，弹道，z 2；朝右画、上下对称） | 36 × 14 |
| `skarner_fx_r_hit` | view_effects `league_skarner_r_hit`（跟随目标，z 2；左右对称） | 26 × 30 |
| `skarner_fx_r_held` | view_buffs `league_skarner_r_held`（跟随目标，z 3；左右对称） | 26 × 34 |
| `skarner_fx_r_haste` | view_buffs `league_skarner_r_haste`（跟随斯卡纳，脚下，z -1；左右对称） | 50 × 12 |

- 两张表：`asset/league/effects/league_skarner_fx`（小的）和 `league_skarner_big`（q_held、w_quake、r_spike），tag = 名字（build_skarner.py 的 views；buff 的 tag：q_slow / w_slow → slow、w_on → w_shield、e_stun → stun、rock → q_held；弹道：q_throw → q_rock、r_lash → r_spike）。
- 弹道（q_rock、r_spike）断言上下对称，其余断言左右对称。
- q_held 的格子下半部是他自己：导入时让巨石的底边落在 idle 三根毒刺的高度（hd/idle.png 第 10–22 行，PPU 1.75）。
- 用 `pixel_1x/` 切格（import_trundle_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
