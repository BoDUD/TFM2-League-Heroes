# 超级机甲：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图 + 3 个技能图标。** 造型已定（`design/mightymech_design.png`：3/4 朝右、红银黑三色的超级机器人：小红头盔、银色 V 形角、黄色眼罩；宽厚的红色胸甲、银色星形大护肩；背后扇形红色刃翼；双手握着一把比身体还长的红银巨剑，剑格中间一颗橙色发光圆核）。超级机甲在游戏里是**高清**的（每个游戏格子里约 2×2 个细像素），40 格高、48 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/mightymech_size.png`：超级机甲缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是超级机甲自己的特效贴图（金铲铲第 17 季的引力矩阵、冲击环、变形，第 15 季机甲的剑光、剑击、护盾、金色火花）（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **超级机甲是巨型机器人，特效都是机甲动画的味道**：干脆的直线速度线、硬朗的菱形和箭头状火花、白芯的**红色**刀光、剑核的**橙金色**光、银色金属碎片；只有引力矩阵（`q_*`）用**紫色**引力；不要绿色、不要树叶、不要烟火。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：除了贴着地面扫出去的剑气 `r_slash`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `mightymech_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `mightymech_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/mightymech_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/mightymech_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「旅人护航」 | 每条命开打时给自己和血最少的队友上护盾（自己双倍） | `p_shield` |
| 普攻「活塞重斩」 | 巨剑砍下；每第三下活塞推着剑重砸，多打一下并减速 | `a_hit` · `a_crush` · `a_slow` |
| 技能 =「引力矩阵」 | 刃翼张开防御：减伤、把附近敌人吸过来打自己（嘲讽）、回血；结束时一圈冲击波 | `q_stance` · `q_taunt` · `q_wave` · `q_hit` |
| 技能 2 =「机甲飞跃」 | 跳到正在冲我方后排的敌人身上砸下：伤害、击飞 | `e_slam` · `e_up` |
| 大招 =「究极变形·超级战刃」 | 变形（护盾、加双抗），剑核爆燃、剑刃变长，往前劈出一道剑气：伤害、击飞 | `r_transform` · `r_sword` · `r_slash` · `r_hit` · `r_form` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 机甲红（刃翼、刀光、剑气）：`#FFD6CF`、`#FF6B5A`、`#E0242B`、`#9E1220`、`#55091A`；
  - 橙金（剑核、究极形态、护盾）：`#FFFBE0`、`#FFE070`、`#FFAA2E`、`#F06A12`、`#A33A0A`；
  - 银（金属碎片）：`#F4F7FA`、`#C9D2DC`、`#8D99A8`、`#56606E`；
  - 引力紫（只给引力矩阵）：`#F0E9FF`、`#B9A4FF`、`#7B62F0`、`#4A36B8`、`#261B6E`；
  - 尘土和碎石：`#ECE6DA`、`#B8AE9E`、`#7E7466`、`#4A433B`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `mightymech_fx_a_hit.png`：普攻「活塞重斩」：剑砍中，3 帧

巨剑砍中：**一道竖着的白芯红色刀光**从上往下一闪，两边溅几粒银色火花。**左右对称**，3 帧（要快）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A), a silver steel ramp (#F4F7FA, #C9D2DC, #8D99A8, #56606E).
Effect: A SWORD CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin vertical white-red slash line 12 squares tall in the middle; 2 the slash 3 squares wide, white core with red edges, a few silver chevron sparks flying out to both sides (mirrored); 3 the slash fading to dark red, the last sparks. Small and quick. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `mightymech_fx_a_crush.png`：普攻：每第三下「活塞重斩」砸中，4 帧

每第三下活塞推着剑重重砸下：**一道更粗的竖刀光 + 橙金色的冲击闪光**炸开，两边各一小股白色**活塞蒸汽**喷出，银色碎片往两边飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A), an orange-gold core ramp (#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A), a silver steel ramp (#F4F7FA, #C9D2DC, #8D99A8, #56606E).
Effect: A HEAVY PISTON CHOP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thick vertical white-red slash 18 squares tall; 2 an orange-gold IMPACT FLASH 14 squares across where it lands (bottom middle), a white core, two short white STEAM jets bursting out sideways (mirrored); 3 a red-orange burst ring 20 squares across, silver shards flying out to both sides, the steam spreading; 4 the last embers and steam. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 4 equal 24:22 cells, image size 1536x352 (each cell 384x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `mightymech_fx_a_slow.png`：普攻第三下：减速，6 帧循环

被重斩减速的人：脚边**几道红色的小裂痕电光**一闪一闪，一点银色碎屑。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A), a silver steel ramp (#F4F7FA, #C9D2DC, #8D99A8, #56606E).
Effect: A CRACKLE AT THE FEET, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): on EACH side (mirrored) two tiny red energy cracks (2-3 square zigzags on the ground line) and one silver speck; frames 1-6 the cracks flickering on and off in new spots (every frame left-right symmetric). Subtle. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 6 equal 24:8 cells, image size 2304x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `mightymech_fx_q_stance.png`：技能「引力矩阵」：引力罩，6 帧循环

它张开刃翼进入防御姿态：身子外面**一圈紫色的引力罩**（横着的椭圆，只画外圈：一圈由**小六边形**拼成的紫色格子，边缘奶白），罩子外面几道**往里吸的紫色弧线**（像把东西吸过来）。**里面它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gravity violet ramp (#F0E9FF, #B9A4FF, #7B62F0, #4A36B8, #261B6E).
Effect: A GRAVITY FIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the mech stands in the middle, not drawn: about 47 squares wide and 40 tall, crouched, its blade-wings fanned behind it, its giant sword held forward: a ring of small HEXAGON cells (an ellipse 60 squares wide and 48 tall, only its 3-square rim drawn, hexagons 4 squares across with thin bright edges), gravity violet with pale white edges; outside the ring on each side (mirrored) two short curved violet arcs pointing INWARD (things being pulled in); frames 1-6 the arcs sliding inward toward the ring and a few hexagons lighting up white in turn (mirrored pairs; every frame left-right symmetric). INSIDE the ring stays EMPTY (its body). everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 6 equal 64:52 cells, image size 6144x832 (each cell 1024x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `mightymech_fx_q_taunt.png`：技能「引力矩阵」：被吸住（嘲讽），4 帧

被引力吸住、只能打它的人：头顶**一个紫色的小引力漩涡**（两三圈椭圆弧），一个小小的红色感叹号形状在中间亮一下。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gravity violet ramp (#F0E9FF, #B9A4FF, #7B62F0, #4A36B8, #261B6E), a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A).
Effect: A GRAVITY MARK ABOVE A HEAD, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head (the unit not drawn, the bottom of the cell is the top of its head): 1 a small violet ellipse ring 8 squares wide; 2 two nested violet ellipse rings 14 squares wide, a small red exclamation mark (2 squares wide, 5 tall) flashing in the middle; 3 the rings tightening inward, the mark bright; 4 the rings fading. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 4 equal 16:12 cells, image size 1024x192 (each cell 256x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `mightymech_fx_q_wave.png`：技能「引力矩阵」结束：冲击波，6 帧

防御结束时释放的冲击波：**一圈紫色加奶白的冲击环贴着地面往外推开**（半径两格），环上带着小六边形碎片和银色碎屑。**只在地面和低处**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gravity violet ramp (#F0E9FF, #B9A4FF, #7B62F0, #4A36B8, #261B6E), a silver steel ramp (#F4F7FA, #C9D2DC, #8D99A8, #56606E).
Effect: A GROUND SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND seen from above at an angle (ellipses 3 times as wide as tall): 1 a bright white-violet flash ellipse 20 squares wide in the middle; 2 a thick violet SHOCKWAVE RING 44 squares wide with a white leading edge; 3 the ring 66 squares wide, small hexagon fragments and silver specks flying off it low to both sides (mirrored); 4 the ring 82 squares wide, thinning; 5 the ring at the cell's edge, broken into arcs; 6 the last faint arcs. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 6 equal 90:30 cells, image size 8640x480 (each cell 1440x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `mightymech_fx_q_hit.png`：技能「引力矩阵」：被冲击波打中，3 帧

被冲击波打中的人：**一下紫白色的冲击闪光**，几道紫色短线往外炸开。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gravity violet ramp (#F0E9FF, #B9A4FF, #7B62F0, #4A36B8, #261B6E).
Effect: A GRAVITY IMPACT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 6 squares across; 2 a violet burst 14 squares across with a white core and six short straight rays (mirrored); 3 the rays fading, small violet sparks. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `mightymech_fx_e_slam.png`：技能 2「机甲飞跃」：落地砸出的坑，6 帧

它从天上砸下来：落点**一下橙金色的冲击闪光**，地上**裂开一圈放射状的红色裂纹**，**灰土和碎石往两边低低溅起**，最后剩一点尘土。**只在地面和低处**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold core ramp (#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A), a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A), a dust ramp (#ECE6DA, #B8AE9E, #7E7466, #4A433B).
Effect: A LANDING SLAM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND seen from above at an angle: 1 a bright white-gold flash ellipse 18 squares wide in the middle; 2 an orange-gold impact ring 34 squares wide, red glowing CRACKS radiating out on the ground (mirrored); 3 dust and small rocks bursting out low to both sides (mirrored), the ring 50 squares wide; 4 the dust rolling outward, the cracks dimming to dark red; 5 the dust thinning; 6 the last dust and faint cracks. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 6 equal 60:24 cells, image size 5760x384 (each cell 960x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `mightymech_fx_e_up.png`：技能 2「机甲飞跃」：被击飞，4 帧

被击飞的人：身子两边**几道往上的白色速度线**和几块小碎石往上飞。**身体位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver steel ramp (#F4F7FA, #C9D2DC, #8D99A8, #56606E), a dust ramp (#ECE6DA, #B8AE9E, #7E7466, #4A433B).
Effect: A KNOCK-UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round a small unit (not drawn) in the middle: on EACH side (mirrored) two straight white-silver SPEED LINES pointing up (1 square wide, 6-10 long) and two small rocks flying up; frames 1-4 the lines rising and fading, the rocks higher; the middle stays EMPTY. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `mightymech_fx_r_transform.png`：大招「究极变形」：变形闪光，6 帧

它变形成究极形态：身后**一圈放射状的红色光芒**一下炸开（像刃翼的形状一片片射出去），中间一圈**橙金色的光环**，几颗**菱形的金色亮星**闪一下。**光都在它身后和四周，身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A), an orange-gold core ramp (#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A).
Effect: A MECHA TRANSFORMATION FLARE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the mech stands in the middle, not drawn: about 47 squares wide and 40 tall, crouched, its blade-wings fanned behind it, its giant sword held forward: 1 a white-gold flash ring 30 squares across behind it; 2 long straight RED LIGHT BLADES bursting out radially behind it like a fan (12 blades, mirrored), an orange-gold halo ring 44 squares across; 3 the blades at full length to the cell's edges, four gold DIAMOND STARS flashing at the corners (mirrored); 4 the blades thinning, the halo widening; 5 the blades fading to dark red, small gold sparks; 6 the last sparks. The middle stays EMPTY (its body). everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 6 equal 70:56 cells, image size 6720x896 (each cell 1120x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `mightymech_fx_r_sword.png`：大招「超级战刃」：剑核爆燃，6 帧

剑的橙色核心爆燃、剑刃变长之前的蓄力：**橙金色的能量粒子从四周往它身上（中间偏下）汇聚**，身后**一道橙金色的光柱**往上冲。**身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold core ramp (#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A), a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A).
Effect: A SUPER BLADE CHARGE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the mech stands in the middle, not drawn: about 47 squares wide and 40 tall, crouched, its blade-wings fanned behind it, its giant sword held forward: 1 small orange-gold sparks appearing at the cell's edges on both sides (mirrored); 2 the sparks streaming INWARD toward the middle along straight lines; 3 a tall orange-gold LIGHT PILLAR rising behind it (10 squares wide, the full height of the cell, white core), the sparks nearer; 4 the pillar at its brightest, the sparks gathered in a ring 30 squares across at mid height; 5 a flash of white-gold at the middle, the pillar thinning; 6 the last gold sparks. The middle stays EMPTY (its body). everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 6 equal square cells, image size 5376x896 (each cell 896x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `mightymech_fx_r_slash.png`：大招「超级战刃」：一剑劈出的剑气，4 帧

巨剑往前劈出的剑气：**一道长长的红色月牙形剑气贴着地面往右扫出去**，白芯、橙金色的边，后面拖着红色的速度线。**上下对称、朝右**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A), an orange-gold core ramp (#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A).
Effect: A SWORD WAVE, 4 frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with the cast; turned half round to the left it must read the same): a long energy blade wave across the cell: 1 a short bright white-red crescent (its curve bulging to the right) at the left third of the cell; 2 the crescent 14 squares tall at the middle, white core, orange-gold edge, straight red speed lines trailing behind it to the left (mirrored top and bottom); 3 the crescent at the right part of the cell, the trail the whole length; 4 the crescent leaving the right edge, the trail fading. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 4 equal 80:18 cells, image size 5120x288 (each cell 1280x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `mightymech_fx_r_hit.png`：大招「超级战刃」：被剑气砍中，4 帧

被剑气砍中的人：**一个红色的大 X 形十字刀光**一闪，中间橙金色的闪光，银色碎片往外飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A), an orange-gold core ramp (#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A), a silver steel ramp (#F4F7FA, #C9D2DC, #8D99A8, #56606E).
Effect: A BIG CROSS SLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two thin white-red slash lines crossing in an X, 18 squares across; 2 the X 3 squares thick, white core, red edges, an orange-gold flash at the crossing; 3 silver shards flying out from the middle to both sides (mirrored), the X fading to dark red; 4 the last shards. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 4 equal square cells, image size 1408x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `mightymech_fx_r_form.png`：大招：究极形态的余光，6 帧循环

究极形态持续的那几秒：身子两边**几粒橙金色的小火光往上飘**，偶尔一道很细的红色光线一闪。很淡。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold core ramp (#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A), a mecha red ramp (#FFD6CF, #FF6B5A, #E0242B, #9E1220, #55091A).
Effect: AN ULTIMATE-FORM GLOW, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the mech stands in the middle, not drawn: about 47 squares wide and 40 tall, crouched, its blade-wings fanned behind it, its giant sword held forward: on EACH side (mirrored) three small orange-gold embers (1-2 squares) drifting upward along its flanks, and one thin red light line flickering; frames 1-6 the embers rising and reappearing at the bottom (every frame left-right symmetric). Subtle. The middle stays EMPTY (its body). everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 6 equal 52:44 cells, image size 4992x704 (each cell 832x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `mightymech_fx_p_shield.png`：被动「旅人护航」：护盾，6 帧循环

被动给自己和队友的护盾：人外面**一圈很薄的橙金色护盾外框**（竖着的椭圆，只画外圈，边上几个小菱形），一道亮光沿着外框往上扫。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange-gold core ramp (#FFFBE0, #FFE070, #FFAA2E, #F06A12, #A33A0A).
Effect: A VOYAGER SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: a thin orange-gold shield outline (an upright ellipse 22 squares wide and 34 tall, only its 2-square rim drawn, pale gold with a white outer edge), four small gold DIAMOND studs on it (mirrored pairs); frames 1-6 a bright white-gold glint sweeping up both sides of the rim (mirrored; every frame left-right symmetric). INSIDE stays EMPTY. everything is the power of a SUPER ROBOT (a red, silver and black mecha with blade-wings and a giant sword with a glowing orange core): sharp mecha-anime shapes - straight speed lines, hard diamond and chevron sparks, clean energy arcs - bright red and orange-gold light with white cores, silver metal shards, violet gravity rings only where said; flat shades, crisp blocky shapes; no green, no leaves, no fire smoke.
Layout: one horizontal row of 6 equal 24:36 cells, image size 2304x576 (each cell 384x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `mightymech_icon_skill.png`：技能「引力矩阵」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark steel frame with small red chevron corners, a deep navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a ring of small violet hexagons forming a dome, red blade-wing shapes spread round it, violet arcs curving inward toward its centre, a bright white-violet core. No text, no letters.
```

### 图标 2. `mightymech_icon_skill2.png`：技能 2「机甲飞跃」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark steel frame with small red chevron corners, a deep navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a red mecha silhouette with spread blade-wings diving down at the lower right, its sword pointing down, an orange-gold impact burst and red ground cracks under it, white speed lines above. No text, no letters.
```

### 图标 3. `mightymech_icon_ult.png`：大招「究极变形·超级战刃」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark steel frame with small red chevron corners, a deep navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a giant red-and-silver sword drawn diagonally from the lower left to the upper right, its round orange core blazing white-gold in the middle, a red crescent energy wave sweeping off its blade, gold diamond sparks. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `mightymech_fx_a_hit` | view_effects `tft_mightymech_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `mightymech_fx_a_crush` | view_effects `tft_mightymech_a_crush`（跟随目标，z 2；左右对称） | 24 × 22 |
| `mightymech_fx_a_slow` | view_buffs `tft_mightymech_a_slow`（跟随被减速的人，脚下，z 3；左右对称） | 24 × 8 |
| `mightymech_fx_q_stance` | view_buffs `tft_mightymech_q_stance`（大表，跟随超级机甲，z 3；左右对称） | 64 × 52 |
| `mightymech_fx_q_taunt` | view_effects `tft_mightymech_q_taunt`（跟随被嘲讽的人，头上，z 3；左右对称） | 16 × 12 |
| `mightymech_fx_q_wave` | view_effects `tft_mightymech_q_wave`（大表，放在它脚下的地面上，不跟随，z -1；左右对称） | 90 × 30 |
| `mightymech_fx_q_hit` | view_effects `tft_mightymech_q_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `mightymech_fx_e_slam` | view_effects `tft_mightymech_e_slam`（大表，放在落点的地面上，不跟随，z -1；左右对称） | 60 × 24 |
| `mightymech_fx_e_up` | view_effects `tft_mightymech_e_up`（跟随被击飞的人，z 3；左右对称） | 16 × 20 |
| `mightymech_fx_r_transform` | view_effects `tft_mightymech_r_transform`（大表，跟随超级机甲，z 3；左右对称） | 70 × 56 |
| `mightymech_fx_r_sword` | view_effects `tft_mightymech_r_sword`（大表，跟随超级机甲，z 3；左右对称） | 56 × 56 |
| `mightymech_fx_r_slash` | view_projectiles `tft_mightymech_r_slash`（大表，直线范围，贴着地面沿出手方向；上下对称、朝右） | 80 × 18 |
| `mightymech_fx_r_hit` | view_effects `tft_mightymech_r_hit`（跟随目标，z 2；左右对称） | 22 × 22 |
| `mightymech_fx_r_form` | view_buffs `tft_mightymech_r_form`（跟随超级机甲，z 1；左右对称） | 52 × 44 |
| `mightymech_fx_p_shield` | view_buffs `tft_mightymech_p_shield`（跟随被护盾的人，z 3；左右对称） | 24 × 36 |
| `mightymech_icon_skill` | skill_icons[0] `asset/tft/icons/tft_mightymech_skill` | 64 × 64 |
| `mightymech_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_mightymech_skill2` | 64 × 64 |
| `mightymech_icon_ult` | skill_icons[2] `asset/tft/icons/tft_mightymech_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_mightymech_fx`（小的）和 `tft_mightymech_big`（q_stance、q_wave、e_slam、r_transform、r_sword、r_slash），tag = 名字。
- r_slash 断言上下对称（朝右），其余断言左右对称。
- q_wave、e_slam 放在地面上（不跟随，z -1）；r_transform、r_sword 跟随它；q_stance、r_form 是它身上的 buff，p_shield 是被护盾的人身上的 buff（mightymech.rs 挂）；a_slow 是敌人身上的 buff；r_slash 是直线范围（LineRangeProjectile）的画面，贴着地面沿出手方向。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
