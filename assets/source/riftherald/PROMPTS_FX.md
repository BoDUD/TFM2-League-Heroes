# 峡谷先锋：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图 + 3 个技能图标。** 造型已定（`design/riftherald_design.png`：3/4 朝右、弓着背缩在大圆顶甲壳下的虚空巨兽：蓝紫色晶体甲片拼成的甲壳，每块甲片中间一个洋红小菱形，前沿一圈金色小尖刺；深紫色身体、两条短粗后腿、细长卷尾；两只大蟹钳；脸在甲壳前沿下面，洋红眼睛、金色獠牙）。它在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），44 格高、52 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/riftherald_size.png`：它缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是它自己的特效贴图（金铲铲第 16 赛季的钳爪刀光、砸地裂缝，召唤师峡谷峡谷先锋的旋转攻击、冲锋、碎石、虚空）和科加斯的虚空声波（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **峡谷先锋是虚空巨兽，特效都是它的味道**：**洋红色的虚空光**（它的眼睛和甲壳上的小眼睛）、**蓝紫色的晶体碎片**（像它的甲片）、一点**金色火星**（像它的獠牙）、**灰紫色的碎石和尘土**；又重又有力；不要闪电、不要火焰、不要绿色、不要光滑的霓虹光束。
> - **特效要亮**：每道虚空光都有最亮一档的粉白色芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**（晶体碎片和碎石可以有深色的边）。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 交付方式：
>   - 每张生成后按格子取回（每格取多数颜色）。
>   - 交付 8 倍的 `riftherald_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。
>   - 图标交付 `riftherald_icon_<名字>.png`（64×64）。
>   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。
>   - 都放在 `outputs/riftherald_fx/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/riftherald_fx_pack_done.zip`。
> - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「裂钳」 | 钳爪举起往前砸 | `a_hit` |
| 被动「虚空甲壳」 | 身边每有一名敌方英雄，受到的伤害少一点（不需要画面） | — |
| 技能 1「回旋横扫」 | 原地转一圈，扫过身边一圈的敌人：伤害 + 减速 | `q_spin` · `q_hit` · `q_slow` |
| 技能 2「虚空冲锋」 | 直立蓄力，翻身用甲壳冲撞：沿途撞开，撞到的英雄晕眩 | `e_hit` · `e_crash` · `e_stun` |
| 大招「扭曲护甲」 | 长啸变大，猛击前方地面；4 秒内伤害减免 | `r_roar` · `r_slam` · `r_armor` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 虚空洋红（它的眼睛和甲壳上的小眼睛）：`#FFE8FF`、`#FF8CF0`、`#E040C8`、`#A0209E`、`#5A1260`；
  - 晶体甲壳（蓝紫）：`#A8E0F4`、`#70A2E4`、`#5662C4`、`#3A348C`、`#221A52`；
  - 金色（獠牙、尖刺、爪尖）：`#FFF2A6`、`#EAC254`、`#B28A32`、`#6C4E1C`；
  - 身体（深紫）：`#7A5084`、`#563460`、`#3A203F`、`#22122A`；
  - 尘土和碎石：`#B4A8BC`、`#847494`、`#5A4C68`、`#362C42`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `riftherald_fx_a_hit.png`：普攻「裂钳」：钳爪砸中，4 帧

钳爪砸中：一下洋红色的闪光，**两道交叉的粗爪痕**（像蟹钳夹过），几块蓝紫晶体碎片和金色火星往两边飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a crystal shell ramp (#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52), a gold ramp (#FFF2A6, #EAC254, #B28A32, #6C4E1C).
Effect: A PINCER STRIKE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small hot pink-white flash 5 squares across; 2 TWO thick curved CLAW GASHES crossing in an X, 10 squares tall, magenta with pale pink cores, small blue-violet crystal chips and gold sparks flying out to both sides; 3 the gashes fading to dark violet, the chips falling outward; 4 the last chips and sparks. everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:14 cells, image size 1024x224 (each cell 256x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `riftherald_fx_q_spin.png`：技能 1「回旋横扫」：转一圈扫过地面，6 帧

它原地转一圈：**脚下一圈洋红色的横扫弧光贴着地面转开**，像钳爪和尾巴扫出的刀光，夹着蓝紫晶体碎屑和尘土往外甩，最后散成一圈尘土。**中间它站的地方留空**。**左右对称**（逐帧左右对称：左右两边的弧同时扫出），6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a crystal shell ramp (#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52), a violet dust ramp (#B4A8BC, #847494, #5A4C68, #362C42).
Effect: A GROUND SWEEP, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at a slant (about 3 times as wide as tall) round the beast stands in the middle, not drawn: about 52 squares wide and 44 tall from its shell's top to the ground, hunched under a big domed shell, its face and pincers at the front right (leave its feet's middle empty): 1 two short magenta SWIPE ARCS starting at its sides on the ground; 2-3 the arcs sweeping out round both sides into a full ring 70 squares wide and 22 tall, thick bright magenta with pink-white leading edges, small blue-violet crystal chips and dust flung out of it; 4 the ring at full size, beginning to break; 5 the ring breaking into dark violet arcs and a ring of violet dust; 6 the last dust. everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 76:28 cells, image size 7296x448 (each cell 1216x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `riftherald_fx_q_hit.png`：技能 1「回旋横扫」：被扫中，4 帧

被扫中：一道**横着的洋红扫痕**划过身体中间，两边飞出晶体碎屑。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a crystal shell ramp (#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52).
Effect: A SWEEP HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat horizontal magenta SLASH 12 squares wide across the middle, a pink-white core; 2 the slash at full brightness, small blue-violet crystal chips flying out to both sides; 3 the slash fading to dark violet, chips falling; 4 the last chips. everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `riftherald_fx_q_slow.png`：技能 1「回旋横扫」：减速，6 帧循环

被减速的人脚下：**一圈贴地的紫色虚空小触须**从地上冒出来缠着脚，几颗洋红光点往上飘。**中间人站的地方留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a dark plum ramp (#7A5084, #563460, #3A203F, #22122A).
Effect: A VOID DRAG, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at a slant (about 3 times as wide as tall) 16 squares wide under a unit's feet (its feet's middle empty): small dark plum and magenta VOID TENDRILS 2-4 squares tall curling up from the ground round the feet (mirrored), two or three single magenta motes rising; frames 1-6 the tendrils swaying in and out in turn and the motes rising. Small. everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 18:8 cells, image size 1728x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `riftherald_fx_e_hit.png`：技能 2「虚空冲锋」：被撞中，5 帧

被冲锋撞中：**一下很重的撞击**：洋红色的冲击星爆开，一圈蓝紫晶体碎片和碎石往外飞。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a crystal shell ramp (#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52), a violet dust ramp (#B4A8BC, #847494, #5A4C68, #362C42).
Effect: A RAM IMPACT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a hot pink-white flash 6 squares across; 2 a jagged magenta IMPACT STAR 18 squares across with a pale core, blue-violet crystal shards and grey rock chips bursting out; 3 the star breaking into shards flying outward and down; 4 the shards and a little dust falling; 5 the last dust. everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 5 equal 22:20 cells, image size 1760x320 (each cell 352x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `riftherald_fx_e_crash.png`：技能 2「虚空冲锋」：冲锋撞停的地面，6 帧

冲锋撞停的地方：**地面裂开几道发洋红光的裂缝**，一圈尘土和碎石往两边喷起再落下，最后留一点发光的裂缝慢慢熄灭。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a violet dust ramp (#B4A8BC, #847494, #5A4C68, #362C42).
Effect: A CRASH LANDING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at a slant (about 3 times as wide as tall): 1 a flat violet DUST BURST along the ground 30 squares wide; 2 a ring of dust and grey-violet rock chunks thrown up and out to both sides, 50 squares wide, and short glowing magenta CRACKS opening in the ground from the middle; 3 the dust at its highest, the cracks at full glow; 4 the rocks falling back, the dust settling; 5 a thin dust ring and the cracks dimming to dark violet; 6 the last faint cracks. everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:26 cells, image size 5376x416 (each cell 896x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `riftherald_fx_e_stun.png`：技能 2「虚空冲锋」：被晕眩，6 帧循环

被撞晕的人头顶：**三颗小小的洋红色虚空眼睛绕圈转**（像峡谷先锋甲壳上的小眼睛）。**左右对称**（逐帧对称），6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a crystal shell ramp (#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52).
Effect: A STUN RING, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head, a flat ellipse on the ground seen from above at a slant (about 3 times as wide as tall) 14 squares wide: three small magenta VOID EYES (a 3x2 diamond each, a pale pink centre, like the eyes on its shell) circling round it; every frame left-right symmetric (one eye in front at the middle, two at the sides, the far ones a step darker and smaller), the eyes blinking in turn. everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 16:8 cells, image size 1536x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `riftherald_fx_r_roar.png`：大招「扭曲护甲」：长啸变大，6 帧

它直立长啸、身体变大：**从它身上往外扩散两三圈洋红色的声波环**，几块蓝紫晶体碎片往外飞。**它的身体位置留空**，只画身体外面一圈和边缘。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a crystal shell ramp (#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52).
Effect: A VOID ROAR, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the beast stands in the middle, not drawn: about 52 squares wide and 44 tall from its shell's top to the ground, hunched under a big domed shell, its face and pincers at the front right (rearing up, about 60 squares tall in this frame): 1 a thin magenta glow along the body's outline; 2-4 two or three jagged magenta SOUND RINGS expanding outward from the body (each an open ring broken into thick arcs, pink-white leading edges), small blue-violet crystal shards flying out with them; 5 the rings reaching the cell's edges and thinning to dark violet; 6 the last arcs at the edges. INSIDE stays EMPTY (its body). everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 68:56 cells, image size 6528x896 (each cell 1088x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `riftherald_fx_r_slam.png`：大招「扭曲护甲」：猛击地面，7 帧

两只钳爪一起砸地：**一个大的洋红冲击环在地上炸开**，地面裂成放射状的发光裂缝，碎石和蓝紫晶体碎块往上喷，最后裂缝慢慢熄灭。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260), a crystal shell ramp (#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52), a violet dust ramp (#B4A8BC, #847494, #5A4C68, #362C42).
Effect: A VOID SLAM, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at a slant (about 3 times as wide as tall): 1 a hot pink-white flash 10 squares across on the ground; 2 a thick magenta SHOCK RING 40 squares wide bursting out, glowing magenta CRACKS radiating from the middle; 3 the ring 84 squares wide and 30 tall, rock chunks and blue-violet crystal shards thrown up above it; 4 the ring thinning and breaking into arcs, the chunks at their highest; 5 the chunks falling, a ring of violet dust; 6 the dust settling, the cracks dimming; 7 the last faint cracks. everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 7 equal 88:34 cells, image size 9856x544 (each cell 1408x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `riftherald_fx_r_armor.png`：大招「扭曲护甲」：护甲，6 帧循环

扭曲护甲生效的 4 秒：**它身体外面浮着一圈蓝紫晶体甲片**（像它甲壳的甲片，一片片围在身体两侧和头顶），甲片中间的洋红小眼睛一闪一闪，偶尔一道洋红光沿着甲片边缘流过。**它的身体位置留空**，只画外面一圈。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crystal shell ramp (#A8E0F4, #70A2E4, #5662C4, #3A348C, #221A52), a void magenta ramp (#FFE8FF, #FF8CF0, #E040C8, #A0209E, #5A1260).
Effect: A WARP ARMOR, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the beast stands in the middle, not drawn: about 52 squares wide and 44 tall from its shell's top to the ground, hunched under a big domed shell, its face and pincers at the front right: a loose ring of floating faceted BLUE-VIOLET CRYSTAL PLATES (6-8 squares each, like its shell plates, each with a small magenta diamond) hovering just outside its outline - along both sides and over the top (mirrored); frames 1-6 the plates bobbing a square up and down in turn, their magenta diamonds blinking, a magenta glint running round the ring's edges. INSIDE stays EMPTY (its body). everything is a VOID BEAST's raw power: MAGENTA-PINK VOID GLOW, faceted BLUE-VIOLET CRYSTAL SHARDS like its shell plates, a few GOLD sparks like its tusks, chunks of violet-grey ROCK and DUST; heavy and physical; flat shades, crisp blocky shapes; no lightning, no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 64:52 cells, image size 6144x832 (each cell 1024x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `riftherald_icon_skill.png`：技能 1「回旋横扫」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little gold thorn corners, a deep indigo-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big curved magenta sweep arc going round in a circle like a whirl, a blue-violet crab pincer at its head and a tail at its end, crystal chips flying. No text, no letters.
```

### 图标 2. `riftherald_icon_skill2.png`：技能 2「虚空冲锋」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little gold thorn corners, a deep indigo-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a domed blue-violet crystal shell with magenta spots charging to the right, speed lines and a magenta impact star where it rams, two golden tusks at its front. No text, no letters.
```

### 图标 3. `riftherald_icon_ult.png`：大招「扭曲护甲」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little gold thorn corners, a deep indigo-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a roaring void beast's face under a domed crystal shell, two big golden tusks, glowing magenta eyes, magenta sound rings around it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `riftherald_fx_a_hit` | view_effects `tft_riftherald_a_hit`（跟随目标，z 2；左右对称） | 16 × 14 |
| `riftherald_fx_q_spin` | view_effects `tft_riftherald_q_spin`（大表，它脚下的地面，z -1，不跟随；左右对称） | 76 × 28 |
| `riftherald_fx_q_hit` | view_effects `tft_riftherald_q_hit`（跟随目标，z 3；左右对称） | 14 × 12 |
| `riftherald_fx_q_slow` | view_buffs `tft_riftherald_q_slow`（跟随被减速的人，脚下，z 3；左右对称） | 18 × 8 |
| `riftherald_fx_e_hit` | view_effects `tft_riftherald_e_hit`（跟随被撞的人，z 3；左右对称） | 22 × 20 |
| `riftherald_fx_e_crash` | view_effects `tft_riftherald_e_crash`（大表，它撞停的地方，地面上，z -1，不跟随；左右对称） | 56 × 26 |
| `riftherald_fx_e_stun` | view_buffs `tft_riftherald_e_stun`（跟随被晕的人，头顶上方，z 3；左右对称） | 16 × 8 |
| `riftherald_fx_r_roar` | view_effects `tft_riftherald_r_roar`（大表，跟随它，z 3；左右对称） | 68 × 56 |
| `riftherald_fx_r_slam` | view_effects `tft_riftherald_r_slam`（大表，砸的地方，地面上，z -1，不跟随；左右对称） | 88 × 34 |
| `riftherald_fx_r_armor` | view_buffs `tft_riftherald_r_armor`（大表，跟随它，z 3；左右对称） | 64 × 52 |
| `riftherald_icon_skill` | skill_icons[0] `asset/tft/icons/tft_riftherald_skill` | 64 × 64 |
| `riftherald_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_riftherald_skill2` | 64 × 64 |
| `riftherald_icon_ult` | skill_icons[2] `asset/tft/icons/tft_riftherald_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_riftherald_fx`（小的）和 `tft_riftherald_big`（q_spin、e_crash、r_roar、r_slam、r_armor），tag = 名字。
- 全部断言左右对称（没有飞行弹道）。
- a_hit、q_hit、e_hit 跟随目标；q_spin 在它脚下的地面（caster 画面，不跟随），e_crash 在它冲锋撞停的地方（caster 画面），r_slam 在它砸的地方（ViewEffect，地面）；r_roar 是它身上的 caster 画面；r_armor 是它身上的 buff；q_slow、e_stun 是敌人身上的 buff。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
