# 索姆：给 Codex 的特效提示词（第 3 步）

> **这一份是 11 张特效图 + 3 个技能图标。** 造型已定（`design/sohm_design.png`：正侧面朝右、浮在空中、身子在身下盘成一圈的东方海龙：浅水蓝的蛇形身子、粉色背鳍、深绿海草尾鳍；青绿到深紫的鬃毛；金橙头冠、紫色宝石、两根珊瑚红鹿角、尖耳朵、蓝色杏仁眼）。索姆在游戏里是**高清**的（每个游戏格子里约 1.8×1.8 个细像素），40 格高、32 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/sohm_size.png`：索姆缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里索姆自己的特效贴图（水弹、潮涌的水流和浪花、水之花、水花爆开、波纹）（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **索姆是海龙，特效都是水**：清澈的浅青到海蓝的水、近白的高光、翻卷的浪头、圆圆的水珠和气泡、白色泡沫；**水之花**是一朵水做的莲花，花瓣尖是她背鳍的粉色，花心是她头冠的金色。不要火、不要闪电、不要紫烟、不要光滑的霓虹光束。
> - **特效要亮**：每个水花都有最亮一档或近白的高光，暗底上一眼能看见。**水、泡沫、波纹没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人（水盾只画水泡的边）。
> - **对称**：**三张飞行的画面（a_bolt、q_wave、q_jump）朝右、严格上下对称**（游戏会按飞行方向转）；其余所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sohm_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `sohm_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/sohm_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/sohm_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「水泡弹」 | 吐出一颗水弹 | `a_bolt` · `a_hit` |
| 被动「碧波之力」 | 每放一个技能叠一层潮汐（法强、攻速），最多 5 层 | `p_glow` |
| 技能 1 =「潮涌」 | 一道水浪冲向还没开花的敌人，沿途都受伤，目标头上开出水之花；带花的人倒下，花飞到附近的敌人身上 | `q_wave` · `q_hit` · `q_flower` · `q_jump` |
| 技能 2 =「海潮护佑」 | 小爪一推，给身边血最少的队友一个水盾、加攻速 | `e` · `e_shield` |
| 大招 =「潮汐绽放」 | 所有水之花同时炸开成巨大的水莲，周围的敌人都受伤 | `r_bloom` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**水、泡沫、波纹没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 海水（她的身子和水）：`#F2FFFF`、`#9EF0FF`、`#3CC8F0`、`#1A7FD0`、`#123E8C`；
  - 泡沫和水花：`#FFFFFF`、`#DDF6FF`、`#A8DCEF`；
  - 花瓣粉（她的背鳍）：`#FFE6F8`、`#FF9AD8`、`#E85AB8`、`#A02C88`；
  - 金（她的头冠）：`#FFF4C0`、`#FFD25A`、`#F0A020`、`#A8640C`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（11 张）

11 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `sohm_fx_a_bolt.png`：普攻：水泡弹飞行中，4 帧循环

她吐出来的**水泡弹**：一颗圆圆的水球在右边（近白的高光、浅青到海蓝），后面拖着一小截往左的水花尾巴和两三颗小水珠。**朝右、上下对称**（游戏会按飞行方向转），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a foam ramp (#FFFFFF, #DDF6FF, #A8DCEF).
Effect: A WATER BOLT IN FLIGHT, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): at the RIGHT a round water ball 6 squares across (a white-cyan highlight, aqua, a sea-blue rim), behind it to the LEFT a short spray tail 4 squares long tapering to a point, two or three tiny droplets; frames 1-4 the water rippling. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sohm_fx_a_hit.png`：普攻：水泡弹打中，4 帧

水泡弹打中：一下白色的水花，一圈浅青色的水滴往两边溅开，最后几颗小水泡。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a foam ramp (#FFFFFF, #DDF6FF, #A8DCEF).
Effect: A WATER SPLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan burst 4 squares across in the middle; 2 a crown of aqua water drops splashing up and out to both sides, 12 squares across; 3 the drops falling outward, a thin foam ring; 4 a few small bubbles. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sohm_fx_q_wave.png`：潮涌：冲出去的水浪，6 帧循环

「潮涌」冲出去的**一道水浪**：横着躺在飞行方向上的一股水流，**右边是翻卷的浪头**（上下两边都卷着白色浪花），往左越来越细，拖着一串水珠和泡沫；中间亮青色、外圈海蓝。**朝右、上下对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a foam ramp (#FFFFFF, #DDF6FF, #A8DCEF).
Effect: A RUSHING TORRENT OF WATER, 6 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): lying along the flight, the HEAD of the torrent at the RIGHT is a round churning mass of water 14 squares tall, its top and bottom edges curling into white foam crests (mirrored top to bottom), a white-cyan core; behind it to the LEFT the stream narrowing to 4 squares at the left edge, aqua in the middle, sea blue at the edges, a trail of droplets and foam flecks; frames 1-6 the crests rolling and the foam streaming back. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 6 equal 40:16 cells, image size 3840x256 (each cell 640x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sohm_fx_q_hit.png`：潮涌：水浪冲过，4 帧

被水浪冲到：一下大一点的水花，水往上冲起再往两边落下，带一圈白色泡沫。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a foam ramp (#FFFFFF, #DDF6FF, #A8DCEF).
Effect: A WAVE SPLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan flash 6 squares across; 2 a column of aqua water bursting up and out, foam at its rim, 14 squares across; 3 the water falling back to both sides in curling drops; 4 a fading ring of foam and bubbles. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sohm_fx_q_flower.png`：潮涌：头上的水之花，6 帧循环

带标记的敌人**头顶上飘着一朵水做的莲花**：几片半透明感的水蓝色花瓣，花瓣尖是粉色，花心一点金色，花下面滴下一两颗水珠；轻轻上下浮动、发光。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a pink petal ramp (#FFE6F8, #FF9AD8, #E85AB8, #A02C88), a gold ramp (#FFF4C0, #FFD25A, #F0A020, #A8640C).
Effect: A FLOATING WATER LOTUS, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a lotus flower made of water, 12 squares wide and 9 tall, seen a little from the side: five aqua water petals (white-cyan highlights) opening upward with PINK TIPS, a small GOLD heart in the middle, one or two droplets falling from under it; frames 1-6 the flower bobbing up and down one square and its glow pulsing (every frame left-right symmetric). everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 6 equal 14:12 cells, image size 1344x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sohm_fx_q_jump.png`：潮涌：飞走的花，4 帧循环

带花的人倒下时**飞走的那朵花**：一朵收拢的小水莲花苞在右边（粉色的尖、金色的芯），后面拖着一小串往左的水珠。**朝右、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a pink petal ramp (#FFE6F8, #FF9AD8, #E85AB8, #A02C88), a gold ramp (#FFF4C0, #FFD25A, #F0A020, #A8640C).
Effect: A FLYING LOTUS BUD, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): at the RIGHT a closed water lotus bud 5 squares across (aqua petals with pink tips, a gold glint at its heart), behind it to the LEFT a short trail of droplets and sparkles 4 squares long; frames 1-4 the bud glowing. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sohm_fx_e.png`：海潮护佑：爪前的水波，5 帧

她小爪往前一推：身前**一圈水波纹扩散开**（竖着的椭圆，像推开的水面），几颗水珠往外飞。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a foam ramp (#FFFFFF, #DDF6FF, #A8DCEF).
Effect: A PUSHED RIPPLE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small white-cyan glow 4 squares across in the middle; 2-3 two concentric aqua ripple rings (upright ellipses, 2 squares thick, white-cyan on their edges) spreading out from the middle, a few droplets flying outward to both sides; 4 the rings reaching the cell edge and thinning; 5 a few fading droplets. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 5 equal 24:16 cells, image size 1920x256 (each cell 384x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sohm_fx_e_shield.png`：海潮护佑：水盾，6 帧循环

被保护的队友**被一个水泡罩住**：一个竖着的椭圆水泡，只画**边上一圈**（浅青色、亮的地方近白），左上一道高光，里面几乎透明，几颗小气泡沿着边往上飘。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a foam ramp (#FFFFFF, #DDF6FF, #A8DCEF).
Effect: A WATER BUBBLE SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round a champion 16 squares wide and 34 tall stands in the middle, not drawn: a tall upright ellipse 22 squares wide and 36 tall, ONLY ITS RIM drawn, 2 squares thick, aqua with white-cyan highlights where it is thinnest, a curved highlight streak on its upper left and the same on its upper right (mirrored); a few small bubbles rising along the rim on both sides; frames 1-6 the rim shimmering and the bubbles rising (every frame left-right symmetric). The inside of the bubble (the body) stays EMPTY. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:38 cells, image size 2304x608 (each cell 384x608, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sohm_fx_r_bloom.png`：潮汐绽放：水莲爆开，7 帧

大招在每朵花的位置**炸开一朵巨大的水莲**：先是一朵大花苞在中间亮起，然后水做的花瓣往外、往上猛地绽开，中间冲起一根水柱，粉色的花瓣尖和金色的光点往四周飞，最后变成落下的水花和泡沫。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a foam ramp (#FFFFFF, #DDF6FF, #A8DCEF), a pink petal ramp (#FFE6F8, #FF9AD8, #E85AB8, #A02C88), a gold ramp (#FFF4C0, #FFD25A, #F0A020, #A8640C).
Effect: A GIANT WATER LOTUS BURSTING, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a glowing closed water lotus bud 10 squares across in the middle of the lower half, a gold light at its heart; 2 the bud swelling, its pink tips opening; 3 big aqua water petals bursting OPEN outward and upward, 36 squares across, white-cyan edges, PINK TIPS; 4 a column of water and foam shooting up from the heart to the top of the cell, gold sparks flying out in a symmetric star; 5 the petals breaking into big drops falling outward to both sides; 6 a wide ring of splash and foam at the bottom; 7 a few fading drops and bubbles. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 7 equal square cells, image size 4480x640 (each cell 640x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sohm_fx_r_hit.png`：潮汐绽放：被水花打中，4 帧

被绽放的水花打中：一下白色的冲击，几片粉尖的水花瓣往两边飞散，几颗水珠。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a pink petal ramp (#FFE6F8, #FF9AD8, #E85AB8, #A02C88).
Effect: A PETAL SPLASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan flash 6 squares across; 2 four aqua water petals with pink tips flung out to the four diagonals (mirrored), 14 squares across, droplets between them; 3 the petals breaking into drops; 4 a few fading drops. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sohm_fx_p_glow.png`：被动「碧波之力」：身边的潮水，6 帧循环

她叠起潮汐时：身体**两侧和下面**绕着一圈流动的水（像小小的潮水环），几颗气泡往上冒，身下一圈淡淡的水光。**身体位置留空**（画在她身后，只露出边上）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sea water ramp (#F2FFFF, #9EF0FF, #3CC8F0, #1A7FD0, #123E8C), a foam ramp (#FFFFFF, #DDF6FF, #A8DCEF).
Effect: A SWIRLING TIDE AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the sea dragon floats in the middle, not drawn: 32 squares wide and 40 tall, her head at the top right: a flowing ribbon of aqua water curling round her on BOTH sides (mirrored) from her middle down under her, 2-3 squares thick, white-cyan crests on it, small bubbles rising along both sides, a faint aqua glow ring under her (an ellipse 36 squares wide, 9 tall); frames 1-6 the water flowing round and the bubbles rising (every frame left-right symmetric). The middle of the cell (her body) stays EMPTY. everything is a SEA DRAGON's water: clear aqua and deep blue water with white-cyan highlights, curling wave crests, round droplets and bubbles, white foam and spray, a WATER LOTUS with pink petal tips and a gold heart; flat shades, crisp rounded shapes; no fire, no lightning, no purple smoke, no smooth neon beams.
Layout: one horizontal row of 6 equal 44:48 cells, image size 4224x768 (each cell 704x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `sohm_icon_skill.png`：技能 1「潮涌」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square deep blue frame with little gold corners, a dark sea-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big curling aqua wave crest rushing to the right, white foam on its lip, and above it a small water lotus with pink petal tips and a gold heart. No text, no letters.
```

### 图标 2. `sohm_icon_skill2.png`：技能 2「海潮护佑」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square deep blue frame with little gold corners, a dark sea-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a round shining water bubble shield with a white highlight, a little pale blue dragon claw held up in front of it, small bubbles rising. No text, no letters.
```

### 图标 3. `sohm_icon_ult.png`：大招「潮汐绽放」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square deep blue frame with little gold corners, a dark sea-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge water lotus bursting open, aqua petals with pink tips flung outward, a column of water and gold sparks rising from its heart. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `sohm_fx_a_bolt` | view_projectiles `tft_sohm_a_bolt`（飞向目标，随飞行方向旋转；上下对称、朝右） | 10 × 8 |
| `sohm_fx_a_hit` | view_effects `tft_sohm_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `sohm_fx_q_wave` | view_projectiles `tft_sohm_q_wave`（大表，从她身上朝目标直线飞，随飞行方向旋转；上下对称、朝右） | 40 × 16 |
| `sohm_fx_q_hit` | view_effects `tft_sohm_q_hit`（跟随被冲到的人，z 2；左右对称） | 16 × 16 |
| `sohm_fx_q_flower` | view_buffs `tft_sohm_q_flower`（跟随带标记的敌人，在他头顶上方，z 3；左右对称） | 14 × 12 |
| `sohm_fx_q_jump` | view_projectiles `tft_sohm_q_jump`（从倒下的人飞向下一个敌人，随方向旋转；上下对称、朝右） | 10 × 8 |
| `sohm_fx_e` | view_effects `tft_sohm_e`（跟随她，z 3；左右对称） | 24 × 16 |
| `sohm_fx_e_shield` | view_buffs `tft_sohm_e_shield`（跟随被保护的队友，罩住全身，z 3；左右对称） | 24 × 38 |
| `sohm_fx_r_bloom` | view_effects `tft_sohm_r_bloom`（大表，在每朵花的人身上，不跟随，z 3；左右对称） | 40 × 40 |
| `sohm_fx_r_hit` | view_effects `tft_sohm_r_hit`（在被炸到的人身上，z 3；左右对称） | 16 × 16 |
| `sohm_fx_p_glow` | view_buffs `tft_sohm_p_glow`（大表，跟随她，在她身后，z -1；左右对称） | 44 × 48 |
| `sohm_icon_skill` | skill_icons[0] `asset/tft/icons/tft_sohm_skill` | 64 × 64 |
| `sohm_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_sohm_skill2` | 64 × 64 |
| `sohm_icon_ult` | skill_icons[2] `asset/tft/icons/tft_sohm_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_sohm_fx`（小的）和 `tft_sohm_big`（q_wave、r_bloom、p_glow），tag = 名字。
- a_bolt、q_wave、q_jump 断言上下对称（朝右），其余断言左右对称。
- q_wave 由 tft.dll 直线发射（穿过所有人）；q_jump 由 tft.dll 从倒下的人发出；q_flower 挂在敌人头顶（buff，z 3）；e_shield 罩住被保护的队友（buff，z 3）；p_glow 是她身后的 caster buff（z -1）；r_bloom 在每朵花的人身上（不跟随，z 3）；a_hit、q_hit、r_hit 打在目标身上；e 跟随她。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
