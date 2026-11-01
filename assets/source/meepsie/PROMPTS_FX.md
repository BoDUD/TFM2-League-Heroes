# 小木灵：给 Codex 的特效提示词（第 3 步）

> **这一份是 9 张特效图 + 3 个技能图标。** 造型已定（`design/meepsie_design.png`：3/4 朝右、没有脑袋的浅蓝白月岩巨像：带陨石坑的大石块、两只巨拳、靛蓝短腿、紫色腰带；头顶和背上长着绿叶和紫蘑菇；胸口高处的白边陨石坑驾驶舱里坐着绿色小木灵）。小木灵在游戏里是**高清**的（每个游戏格子里约 2.9×2.9 个细像素），40 格高、48 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/meepsie_size.png`：小木灵缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是它自己（金铲铲第 17 季）、小菊（艾翁的石头巨像：砸地、冲击波）、艾翁和巴德（小木灵）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **小木灵是月岩巨像加一只绿色小木灵驾驶员，特效都是它的味道**：浅蓝白的月尘、带陨石坑的小月岩、紫色的星光和五角小星星（大招是「宇宙大爆炸」）、治疗用小木灵的嫩绿色光；不要火焰、不要闪电、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：除了往前推的月尘震波 `q_wave` 和飞行的小木灵 `e_meep`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `meepsie_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `meepsie_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/meepsie_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/meepsie_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「月岩重拳」+ 被动「木灵驾驶员」 | 一拳砸下，小木灵每拳附带魔法伤害 | `a_hit` |
| 技能 1 =「月尘震地」 | 一拳砸地，月尘震波往前扇形推开：魔法伤害、减速 | `q_wave` · `q_hit` · `q_slow` |
| 技能 2 =「治疗木灵」 | 四只小木灵飞向血量最低的队友（和它自己），持续治疗 | `e_cast` · `e_meep` · `e_hot` |
| 大招 =「宇宙大爆炸」 | 跳到敌人最多的地方砸地：中心伤害最高、往外递减，最近的三个敌人被击飞 | `r_slam` · `r_up` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 月岩（浅蓝白）：`#FFFFFF`、`#E6F4FF`、`#B8D8F2`、`#86A8D6`、`#5A6EA8`、`#353E70`；
  - 月尘：`#EEF1F6`、`#C6CCD8`、`#959DB2`、`#646C86`、`#3E445A`；
  - 星光紫（它的腰带和蘑菇）：`#FFF6FF`、`#F2CCFF`、`#CC8EF2`、`#9C58D8`、`#6A30AA`、`#3C1A6A`；
  - 木灵绿（治疗）：`#FAFFE2`、`#E2F78C`、`#B6E04C`、`#7EB82E`、`#4C8A22`、`#2A5418`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（9 张）

9 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `meepsie_fx_a_hit.png`：普攻「月岩重拳」+ 被动「木灵驾驶员」：拳头砸中，4 帧

拳头砸中：一团浅蓝白的**月尘**往两边崩开，几块带陨石坑的小月岩飞出去，中间一下**紫色的小星星闪光**（小木灵附带的魔法伤害）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-dust ramp (#EEF1F6, #C6CCD8, #959DB2, #646C86, #3E445A), a moon-rock ramp (#FFFFFF, #E6F4FF, #B8D8F2, #86A8D6, #5A6EA8, #353E70), a violet starlight ramp (#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A).
Effect: A MOON-ROCK PUNCH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale white-blue flash 5 squares across with a small violet FIVE-POINT STAR in its middle; 2 a puff of pale moon dust bursting out to both sides, 12 squares across, a few small cratered moon-rock chips flying out (mirrored), the violet star at its brightest; 3 the chips falling outward, the dust spreading low, two tiny violet sparkles; 4 the last dust and one chip on each side. everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 4 equal 16:14 cells, image size 1024x224 (each cell 256x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `meepsie_fx_q_wave.png`：技能 1「月尘震地」：往前推的月尘震波，6 帧循环

拳头砸地后，地面上**一股月尘震波往右推开**：左端（拳头砸地的地方）窄，往右越来越宽，像扇形；一路上小月岩一块块跳起来又落下，前沿是一道翻滚的浅蓝白尘浪，里面夹着几点紫色星光。**上下对称、朝右**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-dust ramp (#EEF1F6, #C6CCD8, #959DB2, #646C86, #3E445A), a moon-rock ramp (#FFFFFF, #E6F4FF, #B8D8F2, #86A8D6, #5A6EA8, #353E70), a violet starlight ramp (#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A).
Effect: A MOON-DUST QUAKE WAVE, 6 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): on the ground, seen from above at a slant: a FAN of rolling pale moon dust spreading from the LEFT edge (6 squares wide there, where the fist struck) to the RIGHT (24 squares wide at the right edge), its front a curling wave of white-blue dust; small cratered moon-rock chips hopping up and dropping along it (mirrored top and bottom), a few tiny violet star sparkles inside the dust; frames 1-6 the dust rolling forward, the chips hopping in turn, the front wave curling (every frame top-bottom symmetric). everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 60:26 cells, image size 5760x416 (each cell 960x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `meepsie_fx_q_hit.png`：技能 1「月尘震地」：被震中，4 帧

被震波打中的人：脚下的地面**一下震起一圈月尘**，几块小月岩跳起来，一点紫色星光一闪。**人站的地方留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-dust ramp (#EEF1F6, #C6CCD8, #959DB2, #646C86, #3E445A), a moon-rock ramp (#FFFFFF, #E6F4FF, #B8D8F2, #86A8D6, #5A6EA8, #353E70), a violet starlight ramp (#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A).
Effect: A QUAKE JOLT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the FEET and lower legs of an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: 1 a pale flash on the ground under its feet with a small violet star; 2 a ring of moon dust jumping up round its feet (an ellipse 20 squares wide, 6 tall), three small moon-rock chips hopping up beside its legs (mirrored); 3 the dust high as its knees, the chips at their highest; 4 the dust settling, the chips dropping. The middle of the cell (its body) stays EMPTY. everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 4 equal 22:18 cells, image size 1408x288 (each cell 352x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `meepsie_fx_q_slow.png`：技能 1「月尘震地」：减速，6 帧循环

被减速的人：脚边**一层沉沉的月尘**粘着脚踝，几块小月岩在脚边滚，像踩在月球表面一样走不动。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-dust ramp (#EEF1F6, #C6CCD8, #959DB2, #646C86, #3E445A), a moon-rock ramp (#FFFFFF, #E6F4FF, #B8D8F2, #86A8D6, #5A6EA8, #353E70).
Effect: MOON-DUST DRAG, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): a heavy low haze of pale moon dust clinging round the ankle line, on EACH side (mirrored) two small cratered moon-rock pebbles rolling slowly; frames 1-6 the dust swelling and sinking a square, the pebbles rolling a square (every frame left-right symmetric). Subtle. everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:8 cells, image size 2304x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `meepsie_fx_e_cast.png`：技能 2「治疗木灵」：木灵飞出，5 帧

驾驶员一招手，**四只绿色小木灵从它身上蹦出来**，往左右两边飞起（左边两只、右边两只，对称），身后拖着绿色亮点和几颗紫色小星星，最后化成光点往上飘。**它的身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime meep-green ramp (#FAFFE2, #E2F78C, #B6E04C, #7EB82E, #4C8A22, #2A5418), a violet starlight ramp (#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A).
Effect: MEEPS POPPING OUT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the golem stands in the middle, not drawn: about 48 squares wide and 40 tall, its two huge fists low at its sides, its leaf-and-mushroom cap on top, its crater cockpit with the little meep at the upper right: 1 a ring of small lime-green sparkles appearing round the top of its body; 2 FOUR little lime-green MEEPS (round bean bodies 5 squares across, two big black eye squares, a tiny antenna) popping up from its top edge, two flying out to the LEFT and two to the RIGHT (mirrored), a trail of green sparkles behind each; 3 the meeps higher and further out, small violet stars twinkling round them; 4 the meeps at the cell's upper corners, the trails fading; 5 only green and violet motes drifting UP. The middle of the cell (its body) stays EMPTY. everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 60:52 cells, image size 4800x832 (each cell 960x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `meepsie_fx_e_meep.png`：技能 2「治疗木灵」：飞向队友的小木灵，4 帧循环

飞去治疗队友的小木灵：**一只缩成一团的绿色小木灵，裹在绿色光球里**往右飞，身后一道短短的绿色亮点尾巴，夹着一两颗紫色小星星。**上下对称、朝右**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime meep-green ramp (#FAFFE2, #E2F78C, #B6E04C, #7EB82E, #4C8A22, #2A5418), a violet starlight ramp (#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A).
Effect: A FLYING MEEP, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a little lime-green meep curled up into a round GLOWING BALL 6 squares across at the RIGHT, a near-white core, a soft lime glow ring round it, a short trail of lime sparkles behind it to the LEFT with one tiny violet star; frames 1-4 the ball pulsing and the sparkles trailing (every frame top-bottom symmetric). everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 4 equal 14:8 cells, image size 896x128 (each cell 224x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `meepsie_fx_e_hot.png`：技能 2「治疗木灵」：持续治疗，6 帧循环

被小木灵治疗的人：脚下一圈**淡绿色的小光环**，绿色的光点和几片小叶子沿着身子两侧往上飘，头顶偶尔一颗紫色小星星。**人站的地方留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a lime meep-green ramp (#FAFFE2, #E2F78C, #B6E04C, #7EB82E, #4C8A22, #2A5418), a violet starlight ramp (#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A).
Effect: A MEEP MENDING GLOW, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: a thin lime-green ring on the ground at its feet (an ellipse 20 squares wide, 6 tall); small lime motes (2x2 and 1x1 squares) and tiny green leaves rising up both sides of the body (mirrored), one small violet star twinkling above its head; frames 1-6 the motes and leaves rising and fading at the top, new ones from the ring, the ring breathing (every frame left-right symmetric). The middle (its body) stays EMPTY. everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:32 cells, image size 2304x512 (each cell 384x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `meepsie_fx_r_slam.png`：大招「宇宙大爆炸」：落地爆炸，6 帧

它从天上砸回地面：一下巨大的白紫色闪光，地面上**一个很大的星光冲击环**炸开（从斜上方看的椭圆），环上全是紫色星光和浅蓝白月尘，大块月岩翘起、碎石往两边飞，空中散开一片紫色星云和小星星。**只在地面和低处**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet starlight ramp (#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A), a moon-dust ramp (#EEF1F6, #C6CCD8, #959DB2, #646C86, #3E445A), a moon-rock ramp (#FFFFFF, #E6F4FF, #B8D8F2, #86A8D6, #5A6EA8, #353E70).
Effect: THE BIG BANG, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND and low above it, seen from above at a slant: 1 a huge white-violet flash at the middle bottom, 24 squares wide, a burst of short star rays; 2 a thick bright violet STARLIGHT SHOCKWAVE RING bursting open on the ground (an ellipse 50 squares wide, 16 tall), pale moon dust rolling out with it, big cratered moon-rock slabs tilting up on both sides (mirrored), small five-point stars flung up; 3 the ring 84 squares wide, a low violet NEBULA puff over the middle, stars and chips flying out; 4 the ring at the cell's edge and thinning, the slabs sinking, the stars twinkling as they fall; 5 the settling dust and a few stars; 6 the last sparkles. everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 96:44 cells, image size 9216x704 (each cell 1536x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `meepsie_fx_r_up.png`：大招「宇宙大爆炸」：被击飞，5 帧

离落点最近、被击飞的人：身边**一圈紫色星星绕着转**着往上飞，脚下一下月尘冲起来。**人站的地方留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet starlight ramp (#FFF6FF, #F2CCFF, #CC8EF2, #9C58D8, #6A30AA, #3C1A6A), a moon-dust ramp (#EEF1F6, #C6CCD8, #959DB2, #646C86, #3E445A).
Effect: A STARRY KNOCK-UP, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: 1 a puff of moon dust shooting up under its feet; 2 a ring of small violet five-point STARS round its waist (mirrored), a thin violet streak up each side; 3 the stars swirled up to its chest and head, bright; 4 the stars above its head, twinkling; 5 the last two stars and falling dust. The middle of the cell (its body) stays EMPTY. everything is a MOON-ROCK GOLEM piloted by a little MEEP: pale moon dust and chunky cratered moon-rock chips, purple-violet STARLIGHT and little five-point STARS, round lime-green meep glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 22:28 cells, image size 1760x448 (each cell 352x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `meepsie_icon_skill.png`：技能 1「月尘震地」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark indigo frame with little violet star corners, a deep night-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge pale cratered moon-rock fist smashed into the ground at the lower left, a fan of moon dust and hopping rock chips rolling out toward the upper right, a few violet star sparkles in it. No text, no letters.
```

### 图标 2. `meepsie_icon_skill2.png`：技能 2「治疗木灵」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark indigo frame with little violet star corners, a deep night-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: three little lime-green meeps (big black eyes, tiny antennae) flying in an arc, each in a soft green glow, a green heal cross sparkle between them. No text, no letters.
```

### 图标 3. `meepsie_icon_ult.png`：大招「宇宙大爆炸」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark indigo frame with little violet star corners, a deep night-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a pale moon-rock golem crashing down fists first into a bursting violet starlight explosion, a ring of stars and moon dust flying out, a tiny green meep in its chest cockpit. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `meepsie_fx_a_hit` | view_effects `tft_meepsie_a_hit`（跟随目标，z 2；左右对称） | 16 × 14 |
| `meepsie_fx_q_wave` | view_projectiles `tft_meepsie_q_wave`（大表，一道从它拳头指向前方的线，随方向旋转；上下对称、朝右） | 60 × 26 |
| `meepsie_fx_q_hit` | view_effects `tft_meepsie_q_hit`（跟随被震中的人，z 3；左右对称） | 22 × 18 |
| `meepsie_fx_q_slow` | view_buffs `tft_meepsie_q_slow`（跟随被减速的人，脚下，z 3；左右对称） | 24 × 8 |
| `meepsie_fx_e_cast` | view_effects `tft_meepsie_e_cast`（大表，跟随它，z 3；左右对称） | 60 × 52 |
| `meepsie_fx_e_meep` | view_projectiles `tft_meepsie_e_meep`（tft.dll 放的追踪弹道，随飞行方向旋转；上下对称、朝右） | 14 × 8 |
| `meepsie_fx_e_hot` | view_buffs `tft_meepsie_e_hot`（跟随被治疗的人，z 3；左右对称） | 24 × 32 |
| `meepsie_fx_r_slam` | view_effects `tft_meepsie_r_slam`（大表，放在它落地的地面上，不跟随，z -1；左右对称） | 96 × 44 |
| `meepsie_fx_r_up` | view_effects `tft_meepsie_r_up`（跟随被击飞的人，z 3；左右对称） | 22 × 28 |
| `meepsie_icon_skill` | skill_icons[0] `asset/tft/icons/tft_meepsie_skill` | 64 × 64 |
| `meepsie_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_meepsie_skill2` | 64 × 64 |
| `meepsie_icon_ult` | skill_icons[2] `asset/tft/icons/tft_meepsie_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_meepsie_fx`（小的）和 `tft_meepsie_big`（q_wave、e_cast、r_slam），tag = 名字。
- q_wave、e_meep 断言上下对称（朝右），其余断言左右对称。
- q_wave 是从它拳头出发的一条只有画面的线（它的左端对着拳头）；e_meep 是 tft.dll 放的追踪弹道（飞向队友）；r_slam 放在它落地的地面上（不跟随，z -1）；e_cast 是它身上的 caster 画面；a_hit、q_hit 是打中的画面；r_up 是 tft.dll 在被击飞的人身上播的；q_slow 是敌人身上的 buff，e_hot 是队友身上的 buff。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
