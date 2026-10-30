# 石傲玉：给 Codex 的特效提示词（第 3 步）

> **这一份是 13 张特效图 + 3 个技能图标。** 造型已定（`design/shiohyu_design.png`：侧身朝右、直立站着的玉石龙人武者：翡翠青绿的皮肤、浅玉色的大胡子、金边的深青胸甲、深紫水晶肩甲；青绿眉盔、两根金角、紫色额角、橙黄发光的眼睛；珊瑚橙的爪子；背后两片高高竖起的翅膀（深紫翼骨、金到玫瑰色的翼膜）；尾巴尖一片带刺的叶形尾鳍）。石傲玉在游戏里是**高清**的（每个游戏格子里约 2.46×2.46 个细像素），42 格高、30 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/shiohyu_size.png`：石傲玉缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里石傲玉自己的特效贴图（爪痕、砸地的裂缝和碎石、玉龙形态的光环、第三击的光刺和地裂）（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **石傲玉是玉龙，特效都是玉石的力量**：白芯的翡翠玉光、有棱角的玉石碎晶和尖晶、几点金色火星（他角和胸甲边的金色），砸地时灰褐色的碎石和尘土；不要火、不要紫色光、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或白色的芯，暗底上一眼能看见。**光、冲击波、尘土没有黑描边**（玉石碎晶用自己最深的一档做暗面）。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：画在人身上和地上的画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；**沿直线打出去的画面（r3_wave）朝右、严格上下对称**（游戏会按方向转）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `shiohyu_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `shiohyu_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/shiohyu_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/shiohyu_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「龙爪三连」 | 左右爪交替挥，第三下更重 | `a_hit` |
| 被动「玉石之肤」 | 血量掉到一半以下时全身化作玉石，几秒内大幅减伤 | `p` · `p_skin` |
| 技能 1 =「玉拳连打」 | 冲到目标面前连打 4 拳 | `q_hit` |
| 技能 2 =「震地」 | 一拳砸地，周围敌人被震飞并减速 | `e_slam` · `e_hit` · `e_slow` |
| 大招 =「玉龙形态」 | 减伤、免控，接下来 3 次普攻：晕眩 / 真实伤害 / 直线玉石冲击波 + 晕眩 | `r` · `r_jade` · `r1_hit` · `r2_hit` · `r3_wave` · `r3_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 玉（白、薄荷、翡翠、深玉）：`#F4FFF9`、`#C2F7E0`、`#7BE3BC`、`#35BC8E`、`#13805F`；
  - 金（他角和胸甲边的颜色）：`#FFF7D6`、`#FFDD7A`、`#F0B23A`、`#B97A1C`；
  - 碎石和尘土：`#E3DCCB`、`#B0A690`、`#7A705C`、`#4A4336`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（13 张）

13 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `shiohyu_fx_a_hit.png`：普攻：爪痕，4 帧

龙爪打中：两道交叉成 X 的玉色爪痕（每道三条平行的细爪痕），中间一下白光，几颗玉屑飞出。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F).
Effect: A CLAW HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 two sets of three thin parallel jade claw marks crossing in an X, 14 squares across, white along their middles; 3 the marks fading from their ends, small jade chips flying out symmetrically; 4 a few fading chips. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `shiohyu_fx_q_hit.png`：玉拳连打：拳头打中，3 帧

一拳打中：一个白芯的玉色冲击星（四个尖角），一圈小冲击环，两三点金色火星。**左右对称**，3 帧（快，每拳一下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a gold ramp (#FFF7D6, #FFDD7A, #F0B23A, #B97A1C).
Effect: A PUNCH IMPACT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a four-pointed jade impact star 8 squares across with a white core; 2 a thin jade ring round it 11 squares wide, two or three gold sparks flying out mirrored; 3 the ring broken into fading bits. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `shiohyu_fx_e_slam.png`：震地：地面裂开的冲击，6 帧

他一拳砸进地面：脚下的地面**裂开一圈发着玉光的裂缝**（从中心往外放射，从斜上方看的椭圆，宽是高的 3 倍左右），一圈冲击波往外推，碎石块和尘土往两边飞起来。**左右对称**，6 帧（砸下、裂开、冲击波推出去、尘土落下）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a rock-dust ramp (#E3DCCB, #B0A690, #7A705C, #4A4336).
Effect: A GROUND SLAM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND, an ellipse seen from above, about 50 squares wide and 16 tall, its middle where his fist hits: 1 a white-jade flash at the middle; 2 jagged cracks glowing jade running out from the middle in a symmetric star, a jade ring pushing out; 3 the ring at full width, chunky grey-brown rock chunks and dust puffs thrown up to both sides (mirrored, up to 6 squares above the ellipse); 4-5 the rocks falling, the dust spreading, the cracks still glowing; 6 the cracks dim, a little dust. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 52:22 cells, image size 4992x352 (each cell 832x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `shiohyu_fx_e_hit.png`：震地：被震飞，4 帧

被震到的人脚下：地面迸起一圈碎石和尘土，几颗玉屑。**只在脚下**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rock-dust ramp (#E3DCCB, #B0A690, #7A705C, #4A4336), a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F).
Effect: A ROCK BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): at the unit's FEET only (the bottom of the cell): 1 a small jade flash on the ground; 2 small rock chunks and dust puffs bursting up to both sides (mirrored), 10 squares high at most; 3 the rocks at the top of their arc; 4 the dust settling. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:14 cells, image size 1152x224 (each cell 288x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `shiohyu_fx_e_slow.png`：震地：减速，6 帧循环

被减速：脚下一圈裂开的地面和慢慢冒起的尘土（从斜上方看的椭圆，宽是高的 3 倍），几颗小碎石在抖。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rock-dust ramp (#E3DCCB, #B0A690, #7A705C, #4A4336), a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F).
Effect: A CRACKED GROUND SNARE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND round the unit's feet, an ellipse seen from above, about 18 squares wide and 6 tall: short cracks with a faint jade glow, small dust puffs rising and falling, a few pebbles trembling; frames 1-6 the dust breathing (keep every frame left-right symmetric). Nothing above the feet. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:8 cells, image size 1920x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `shiohyu_fx_r.png`：玉龙形态（开启）：玉光迸发，6 帧

他进入玉龙形态的一下：脚下一圈玉光猛地亮起，一圈玉石碎晶和几片小叶子从脚下沿着身体**两侧**往上卷起来，头顶上方一下金色和玉色的光芒。**身体位置留空**（只画脚下、两侧边缘、头顶）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a gold ramp (#FFF7D6, #FFDD7A, #F0B23A, #B97A1C).
Effect: A JADE AWAKENING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon-man stands in the middle, not drawn: 30 squares wide and 42 tall, his head near the top right: 1 a bright jade ring flashing on the ground under his feet (an ellipse 36 squares wide, 10 tall); 2-3 a whirl of faceted jade shards and a few small jade leaves spiralling up along BOTH SIDES of him from the ring to above his head, a starburst of jade and gold rays above his head; 4-5 the shards scattering outward and fading, the ring dimming; 6 a few last glints. The middle of the cell (his body) stays EMPTY. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 44:52 cells, image size 4224x832 (each cell 704x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `shiohyu_fx_r_jade.png`：玉龙形态：持续的玉光，6 帧循环

玉龙形态持续时：脚下一圈慢慢转的玉光圈，身体两侧几颗玉色光点往上飘，头顶上方一个小小的玉色光芒在闪。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a gold ramp (#FFF7D6, #FFDD7A, #F0B23A, #B97A1C).
Effect: A JADE STANCE AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon-man stands in the middle, not drawn: 30 squares wide and 42 tall, his head near the top right: under his feet a glowing jade ring (an ellipse 34 squares wide, 9 tall) with small runes of light turning round it; small jade motes drifting up along both sides of him; a small jade-and-gold glint above his head; frames 1-6 the motes rising and the glint twinkling (every frame left-right symmetric). The middle of the cell (his body) stays EMPTY. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 40:50 cells, image size 3840x800 (each cell 640x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `shiohyu_fx_r1_hit.png`：玉龙形态第 1 击：晕眩的重击，5 帧

第 1 击打中：一下很亮的玉色重击闪光，一圈粗的冲击环，玉石碎片往四周炸开。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a gold ramp (#FFF7D6, #FFDD7A, #F0B23A, #B97A1C).
Effect: A HEAVY JADE BLOW, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-jade flash 8 squares across; 2 a thick jade shock ring bursting out to 20 squares, faceted jade shards flying out in a symmetric star; 3-4 the ring thinning, the shards spinning out; 5 fading shards. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `shiohyu_fx_r2_hit.png`：玉龙形态第 2 击：真实伤害，5 帧

第 2 击打中（真实伤害）：一道竖直的白金色刺穿光，从中心往上下劈开，金色火星和玉屑飞出。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF7D6, #FFDD7A, #F0B23A, #B97A1C), a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F).
Effect: A PIERCING TRUE STRIKE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white point of light; 2 a tall thin VERTICAL slash of white and gold light 22 squares tall splitting up and down from the middle, a small jade diamond flash at its centre; 3 gold sparks and jade chips flying out to both sides (mirrored); 4-5 the slash thinning and fading. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 5 equal 20:24 cells, image size 1600x384 (each cell 320x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `shiohyu_fx_r3_wave.png`：玉龙形态第 3 击：直线玉石冲击波，6 帧

第 3 击打出的**直线冲击波**：从左端（他身前）往右，地面上一道发着玉光的裂缝一路冲出去，裂缝两边一排排玉石尖晶从地里刺出来（从左往右一个接一个冒出），最前端一团玉光。**朝右、上下对称**，6 帧（从左往右冲出去、尖晶立起、碎开）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a rock-dust ramp (#E3DCCB, #B0A690, #7A705C, #4A4336).
Effect: A JADE SPIKE WAVE, 6 frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its direction; turned half round to the left it must read the same): a long band from the LEFT edge (in front of him) to the RIGHT end: along its middle a glowing jade crack racing to the right; along both sides of the crack (mirrored) rows of sharp faceted jade crystal spikes bursting out, pointing outward, up to 9 squares long; a ball of jade light with a white core at the leading edge; 1-2 the crack and the first spikes at the left, the light rushing right; 3-4 the spikes along the whole length, the light at the right end; 5-6 the spikes cracking into jade shards and dust and fading from the left. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 92:24 cells, image size 8832x384 (each cell 1472x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `shiohyu_fx_r3_hit.png`：冲击波打中，4 帧

冲击波打中：被打中的人脚下一下玉光，几根玉石尖晶从脚下刺起来又碎掉。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a rock-dust ramp (#E3DCCB, #B0A690, #7A705C, #4A4336).
Effect: A JADE SPIKE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a jade flash 6 squares across; 2 three faceted jade spikes stabbing up from the ground at the unit's feet (one in the middle, two leaning out mirrored), 14 squares tall; 3 the spikes shattering into shards; 4 fading shards and dust. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `shiohyu_fx_p.png`：被动「玉石之肤」：化作玉石，5 帧

他的皮肤一下化成玉石：身体**两侧**一圈玉石晶片从外往里合拢闪一下，脚下一圈石质的光环，头顶一下白光。**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a rock-dust ramp (#E3DCCB, #B0A690, #7A705C, #4A4336).
Effect: A STONE SKIN FLASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon-man stands in the middle, not drawn: 30 squares wide and 42 tall, his head near the top right: 1 a ring of faceted jade plates appearing on both sides of him (mirrored) a little away from his outline; 2-3 the plates closing in to his sides with a white glint on each, a stone-grey and jade ring on the ground under him (an ellipse 34 squares wide, 9 tall), a white flash above his head; 4-5 the plates and the ring fading. The middle of the cell (his body) stays EMPTY. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 5 equal 40:50 cells, image size 3200x800 (each cell 640x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `shiohyu_fx_p_skin.png`：被动「玉石之肤」：持续，6 帧循环

玉石之肤持续时：身体两侧各有两三片玉石晶片慢慢上下浮动，边上一闪一闪的白色高光；脚下一圈淡淡的石质光环。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a jade ramp (#F4FFF9, #C2F7E0, #7BE3BC, #35BC8E, #13805F), a rock-dust ramp (#E3DCCB, #B0A690, #7A705C, #4A4336).
Effect: A STONE SKIN AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the dragon-man stands in the middle, not drawn: 30 squares wide and 42 tall, his head near the top right: two or three faceted jade plates floating on EACH side of him (mirrored), bobbing gently up and down, white glints winking on their edges; a faint stone-grey and jade ring on the ground under him (an ellipse 32 squares wide, 8 tall). The middle of the cell (his body) stays EMPTY. everything is a JADE DRAGON martial artist's power: faceted jade crystal shards, jade light with a white core, a few gold sparks, chunky rock and dust where the ground breaks; flat shades, crisp angular shapes; no fire, no purple, no smooth neon beams.
Layout: one horizontal row of 6 equal 38:48 cells, image size 3648x768 (each cell 608x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `shiohyu_icon_skill.png`：技能 1「玉拳连打」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark gold frame with little jade corners, a deep green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a coral-orange dragon fist punching to the right with two fading jade afterimages of it behind, a four-pointed jade impact star where it lands. No text, no letters.
```

### 图标 2. `shiohyu_icon_skill2.png`：技能 2「震地」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark gold frame with little jade corners, a deep green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a coral-orange dragon fist smashing down into the ground, jade-glowing cracks radiating from it, rock chunks flying up to both sides. No text, no letters.
```

### 图标 3. `shiohyu_icon_ult.png`：大招「玉龙形态」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark gold frame with little jade corners, a deep green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: the head of a jade dragon (a teal brow, two curved gold horns, a small purple horn on the forehead, glowing orange eyes) roaring, jade light rays bursting behind it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `shiohyu_fx_a_hit` | view_effects `tft_shiohyu_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `shiohyu_fx_q_hit` | view_effects `tft_shiohyu_q_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `shiohyu_fx_e_slam` | view_effects `tft_shiohyu_e_slam`（大表，砸地时在他脚下的地面上，不跟随，z 1；左右对称） | 52 × 22 |
| `shiohyu_fx_e_hit` | view_effects `tft_shiohyu_e_hit`（跟随被打中的人，z 2；左右对称） | 18 × 14 |
| `shiohyu_fx_e_slow` | view_buffs `tft_shiohyu_e_slow`（跟随被减速的人，脚下地面，z 3；左右对称） | 20 × 8 |
| `shiohyu_fx_r` | view_effects `tft_shiohyu_r`（大表，跟随他，z 4；左右对称） | 44 × 52 |
| `shiohyu_fx_r_jade` | view_buffs `tft_shiohyu_r_jade`（大表，跟随他，z 3；左右对称） | 40 × 50 |
| `shiohyu_fx_r1_hit` | view_effects `tft_shiohyu_r1_hit`（跟随目标，z 3；左右对称） | 22 × 22 |
| `shiohyu_fx_r2_hit` | view_effects `tft_shiohyu_r2_hit`（跟随目标，z 3；左右对称） | 20 × 24 |
| `shiohyu_fx_r3_wave` | view_projectiles `tft_shiohyu_r3_wave`（大表，从他身前指向目标的一条线，随方向旋转；上下对称、朝右） | 92 × 24 |
| `shiohyu_fx_r3_hit` | view_effects `tft_shiohyu_r3_hit`（跟随被打中的人，z 3；左右对称） | 18 × 18 |
| `shiohyu_fx_p` | view_effects `tft_shiohyu_p`（大表，跟随他，z 4；左右对称） | 40 × 50 |
| `shiohyu_fx_p_skin` | view_buffs `tft_shiohyu_p_skin`（大表，跟随他，z 3；左右对称） | 38 × 48 |
| `shiohyu_icon_skill` | skill_icons[0] `asset/tft/icons/tft_shiohyu_skill` | 64 × 64 |
| `shiohyu_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_shiohyu_skill2` | 64 × 64 |
| `shiohyu_icon_ult` | skill_icons[2] `asset/tft/icons/tft_shiohyu_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_shiohyu_fx`（小的）和 `tft_shiohyu_big`（e_slam、r、r_jade、r3_wave、p、p_skin），tag = 名字。
- r3_wave 断言上下对称（朝右），其余断言左右对称。
- r3_wave 是从他身前出发、指向目标的一条线（LineRangeProjectile，左端对着他身前）；e_slam 放在砸地点的地面上（不跟随）；r_jade、p_skin 是他身上的 caster buff（z 3）；r、p 是他身上的一下（z 4）。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
