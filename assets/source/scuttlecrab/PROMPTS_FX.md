# 迅捷蟹：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图 + 3 个技能图标。** 造型已定（`design/scuttle_design.png`：3/4 朝右、背着青绿色叠片甲壳的河蟹：甲片边缘柠檬黄绿、后沿一排尖刺；正前方灰色石头面甲、两只发光的柠檬黄绿眼睛；两根一节一节的长触角往后弯；甲壳下面一圈深青色尖叶形的短腿和小钳子）。迅捷蟹在游戏里是**高清**的（每个游戏格子里约 2.7×2.7 个细像素），30 格高、46 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/scuttle_size.png`：迅捷蟹缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是雷克塞（钻地、钻出击飞）、娑娜（加速）、索拉卡（治疗）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **迅捷蟹是河道里的螃蟹，特效都是它的味道**：溅开的河水和涟漪、青绿色带黄绿边的甲片、河岸的泥土和小石子（大招是钻地）、治疗用叶子的嫩绿色光；不要火焰、不要闪电、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；地上的神龛 `q_shrine` **左右、上下都对称**（游戏可能把它转半圈）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `scuttle_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `scuttle_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/scuttle_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/scuttle_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「螃蟹舞」 | 跳一段舞，踩中身边一圈的敌人 | `a_hit` |
| 被动「绿霸符」 | 身边的队友掉到 40% 血以下时回一大口血（每人 10 秒一次） | `p_heal` |
| 技能 1 =「疾行神龛」 | 脚下放一个河水神龛，水花溅伤身边的敌人；队友站在里面移动和攻击变快 | `q_shrine` · `q_haste` |
| 技能 2 =「蟹壳护盾」 | 缩进壳里得到护盾；护盾打光时蟹壳炸开，伤害、减速、短暂眩晕身边的敌人 | `e_shell` · `e_burst` · `e_slow` |
| 大招 =「你挖得动吗？」 | 钻进地下大幅减伤、持续回血，然后钻出来把身边的敌人击飞 | `r_dig` · `r_burst` · `r_up` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 甲壳青绿（黄绿边）：`#F2FFE0`、`#C8F07A`、`#7CD6A0`、`#3FA88C`、`#23756E`、`#144548`；
  - 河水：`#FFFFFF`、`#D6F6FF`、`#8EE0F4`、`#4AB4E0`、`#2A7CB8`、`#1A4C80`；
  - 泥土：`#F0DCB4`、`#C8A276`、`#9A7450`、`#6E4E34`、`#44301E`；
  - 叶绿（治疗）：`#F6FFE4`、`#D4F794`、`#96DC5A`、`#58B034`、`#2E7A22`、`#184A16`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `scuttle_fx_a_hit.png`：普攻「螃蟹舞」：踩中，4 帧

跳舞踩中身边的敌人：一下**河水溅开**，水花往两边飞，中间一颗**柠檬黄绿的小星闪光**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80), a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548).
Effect: A SPLASHING STOMP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan flash 5 squares across with a small lime-yellow four-point star in its middle; 2 a splash of river water bursting out to both sides, 14 squares across, droplets flying up and out (mirrored), the lime star at its brightest; 3 the droplets arcing outward and falling, a low ripple spreading; 4 the last droplets on each side. everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:14 cells, image size 1152x224 (each cell 288x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `scuttle_fx_p_heal.png`：被动「绿霸符」：给低血队友回血，5 帧

队友血量掉到 40% 以下时：脚下一圈**绿色的符文光环**亮起，绿色的叶子和光点**绕着身体两侧旋转往上飘**，头顶一下亮起一个**绿色小十字**。**人站的地方留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green heal ramp (#F6FFE4, #D4F794, #96DC5A, #58B034, #2E7A22, #184A16), a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548).
Effect: A GREEN BUFF HEAL, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: 1 a bright leaf-green rune ring flashing on the ground at its feet (an ellipse 22 squares wide, 6 tall); 2 small green leaves and lime motes swirling up both sides of the body (mirrored), the ring glowing; 3 the leaves at chest height, a small green PLUS sign (a heal cross, 5 squares) lighting above its head; 4 the leaves above its head, the cross bright, the ring fading; 5 the last motes drifting up. The middle of the cell (its body) stays EMPTY. everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 26:34 cells, image size 2080x544 (each cell 416x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `scuttle_fx_q_shrine.png`：技能 1「疾行神龛」：地上的加速神龛，6 帧循环

它脚下的地面上，**一圈河水做的神龛**：从斜上方看的椭圆，外圈一道打转的水流波纹，里面几圈一圈圈往外扩的涟漪，水面上一点点柠檬黄绿的亮光闪烁，像一个会发光的小水潭。**只画平平的地面，不要往上冒的东西**（游戏可能把它转半圈，往上的东西会倒过来）。**左右对称、上下也对称（以中心为准）**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80), a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548).
Effect: A RIVER SPEED SHRINE, 6 looping frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square, about its centre (the game may turn it half round: it must read the same): FLAT ON THE GROUND, seen from above at a slant: a big ellipse 90 squares wide and 26 tall centred in the cell - its rim a ring of swirling river water (a band 3 squares wide of white-cyan foam and blue water), inside it 2-3 thin concentric RIPPLE rings spreading outward from the centre, a few small lime-yellow glints twinkling on the water (placed mirror-symmetric); frames 1-6 the ripples moving outward one step and a new one starting at the centre, the rim's foam swirling, the glints twinkling in turn. NOTHING sticking up from the ground (no spouts, no rising motes). everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 96:30 cells, image size 9216x480 (each cell 1536x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `scuttle_fx_q_haste.png`：技能 1「疾行神龛」：加速，6 帧循环

站在神龛里被加速的队友：脚边两侧**几道蓝白的水流速度线**往后飘，脚下一圈小涟漪，偶尔一点柠檬黄绿的亮光。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80), a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548).
Effect: RIVER HASTE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): a small ripple ring under the feet (an ellipse 18 squares wide, 4 tall), on EACH side (mirrored) two short white-cyan water streaks flowing outward like speed lines, one tiny lime glint; frames 1-6 the streaks flowing out and fading, new ones starting at the feet, the ripple breathing (every frame left-right symmetric). Subtle. everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 26:10 cells, image size 2496x160 (each cell 416x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `scuttle_fx_e_shell.png`：技能 2「蟹壳护盾」：护盾，6 帧循环

它缩壳得到护盾的时候：身上罩着**一层半透明的青绿色甲片护盾**（一片片六边形的甲片拼成的圆罩），罩子边缘柠檬黄绿亮边，上面偶尔一道亮光扫过。**只画罩子的边和几片甲片，它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548), a river-water ramp (#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80).
Effect: A SHELL SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the crab sits in the middle, not drawn: about 45 squares wide and 30 tall, low on its legs, its teal shell domed over it, its stone face at the right, its two long antennae curving back over the shell: a dome-shaped shield over it, 52 squares wide and 38 tall, drawn as an OUTLINE of hexagonal teal shell plates (each plate's edge 1-2 squares, lime-yellow on its upper rim, the plates themselves left EMPTY so the crab shows through), a few small white glints on the dome; frames 1-6 a band of light sweeping across the plates from both sides to the top (mirrored), the rim breathing a square. The middle of the cell (its body) stays EMPTY. everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 54:40 cells, image size 5184x640 (each cell 864x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `scuttle_fx_e_burst.png`：技能 2「蟹壳护盾」：蟹壳碎裂，5 帧

护盾被打光（或者时间到）时：罩子**一下炸开**，一片片青绿色带黄绿边的**甲片碎块往四周飞**，中间一圈河水溅开，落到地上成一圈水渍（让周围的敌人减速）。**它的身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548), a river-water ramp (#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80).
Effect: THE SHELL BURSTS, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the crab sits in the middle, not drawn: about 45 squares wide and 30 tall, low on its legs, its teal shell domed over it, its stone face at the right, its two long antennae curving back over the shell: 1 a white-cyan flash over its shell, cracks of light across a dome 52 squares wide; 2 the dome breaking into teal shell SHARDS (pointed plates 4-6 squares with lime edges) flying out to both sides and up (mirrored), a ring of river water splashing out low on the ground; 3 the shards further out, tumbling, the water ring 66 squares wide; 4 the shards falling at the cell's edges, droplets raining; 5 a few shards and a thin wet ring on the ground. The middle of the cell (its body) stays EMPTY. everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 70:44 cells, image size 5600x704 (each cell 1120x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `scuttle_fx_e_slow.png`：技能 2「蟹壳护盾」：减速，6 帧循环

被碎壳水花减速的人：脚下**一摊黏糊糊的河水**，几块小甲壳碎片粘在脚边，水滴一滴滴往下掉，像踩在泥水里走不动。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a river-water ramp (#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80), a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548).
Effect: WATERLOGGED, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): a dark wet puddle of river water round the ankle line (an ellipse 20 squares wide, 4 tall), on EACH side (mirrored) a small teal shell chip stuck in it and a drop falling; frames 1-6 the puddle rippling a square, the drops falling in turn (every frame left-right symmetric). Subtle. everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:8 cells, image size 2304x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `scuttle_fx_r_dig.png`：大招「你挖得动吗？」：钻进地下，8 帧

它钻进地下的这 2.5 秒：先是**泥土往两边翻飞**（它在往下挖），然后地上鼓起**一个土包**，土包顶上露出**两根柠檬黄绿的触角尖**一抖一抖，土包边上小土块轻轻滚落。**只在地面和低处**。**左右对称**，8 帧（1–2 挖土，3–8 土包，最后一帧和第 3 帧接得上）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth ramp (#F0DCB4, #C8A276, #9A7450, #6E4E34, #44301E), a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548).
Effect: DIGGING IN, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND and low above it, seen from above at a slant: 1 clods of earth and pebbles flung up to both sides (mirrored) from a hole 30 squares wide; 2 more earth flying, the hole filling; 3 a round EARTH MOUND 34 squares wide and 12 tall, two short LIME-YELLOW ANTENNA TIPS (hooked, 1 square wide, 4 tall) poking out of its top side by side; 4-8 the mound breathing a square up and down, the antenna tips twitching (mirrored), small clods rolling down both sides in turn (frame 8 runs on into frame 3). everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 8 equal 60:26 cells, image size 7680x416 (each cell 960x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `scuttle_fx_r_burst.png`：大招「你挖得动吗？」：钻出地面，6 帧

它从地下钻出来的一下：土包**一下炸开**，泥土、石块和草皮往上往四周飞，地上一圈尘土冲击环扩开（把身边的敌人击飞），空中夹着几点河水和柠檬黄绿的亮光。**它的身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth ramp (#F0DCB4, #C8A276, #9A7450, #6E4E34, #44301E), a river-water ramp (#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80), a teal shell ramp (#F2FFE0, #C8F07A, #7CD6A0, #3FA88C, #23756E, #144548).
Effect: BURSTING OUT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the crab sits in the middle, not drawn: about 45 squares wide and 30 tall, low on its legs, its teal shell domed over it, its stone face at the right, its two long antennae curving back over the shell: 1 a bright flash at the middle bottom and a ring of cracks in the ground 30 squares wide; 2 EARTH ERUPTING - clods, pebbles and dirt shooting UP and out on both sides (mirrored) to the cell's top, a ring of dust bursting open on the ground (an ellipse 50 squares wide, 14 tall), a few water droplets and lime glints among the earth; 3 the clods at their highest, the dust ring 76 squares wide; 4 the clods falling, the ring thinning at the cell's edge; 5 the settling dust and a few pebbles; 6 the last specks. The middle of the cell (its body) stays EMPTY. everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 6 equal 84:48 cells, image size 8064x768 (each cell 1344x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `scuttle_fx_r_up.png`：大招「你挖得动吗？」：被击飞，5 帧

被钻出来的螃蟹顶飞的人：脚下**一下土块和尘土冲上来**，两边几块小石头往上飞。**人站的地方留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth ramp (#F0DCB4, #C8A276, #9A7450, #6E4E34, #44301E), a river-water ramp (#FFFFFF, #D6F6FF, #8EE0F4, #4AB4E0, #2A7CB8, #1A4C80).
Effect: AN EARTHEN KNOCK-UP, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: 1 a puff of earth shooting up under its feet; 2 dirt clods and small pebbles flying up both sides of its legs (mirrored), a dust streak up each side; 3 the clods at its chest, the dust high; 4 the clods above its shoulders, falling back; 5 the last pebbles and settling dust. The middle of the cell (its body) stays EMPTY. everything belongs to a RIVER CRAB with a teal plated shell: splashing river water and ripples, teal shell plates with lime-yellow edges, river-bank earth and pebbles, leaf-green glow for the heals; flat shades, crisp blocky shapes; no fire, no lightning bolts, no smooth neon beams.
Layout: one horizontal row of 5 equal 22:28 cells, image size 1760x448 (each cell 352x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `scuttle_icon_skill.png`：技能 1「疾行神龛」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark teal frame with little lime corners, a deep river-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a glowing ring of swirling river water seen from above at a slant, rippling, with two lime-yellow chevron arrows pointing right above it (speed). No text, no letters.
```

### 图标 2. `scuttle_icon_skill2.png`：技能 2「蟹壳护盾」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark teal frame with little lime corners, a deep river-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a round teal crab shell of overlapping plates with lime-yellow edges, wrapped in a bright hexagonal shield outline, a few shell shards breaking off at its side. No text, no letters.
```

### 图标 3. `scuttle_icon_ult.png`：大招「你挖得动吗？」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark teal frame with little lime corners, a deep river-blue inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a brown earth mound bursting open, clods and pebbles flying up, two lime-yellow hooked crab antenna tips and the top of a teal shell popping out of it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `scuttle_fx_a_hit` | view_effects `tft_scuttlecrab_a_hit`（跟随被打中的人，z 2；左右对称） | 18 × 14 |
| `scuttle_fx_p_heal` | view_effects `tft_scuttlecrab_p_heal`（tft.dll 在被治疗的人身上播，z 3；左右对称） | 26 × 34 |
| `scuttle_fx_q_shrine` | view_projectiles `tft_scuttlecrab_q_shrine`（大表，神龛范围的画面，放在它脚下的地面上，游戏可能把它转半圈；左右上下都对称，z -1） | 96 × 30 |
| `scuttle_fx_q_haste` | view_buffs `tft_scuttlecrab_q_haste`（跟随被加速的队友，脚下，z 3；左右对称） | 26 × 10 |
| `scuttle_fx_e_shell` | view_buffs `tft_scuttlecrab_e_shell`（跟随它，z 3；左右对称） | 54 × 40 |
| `scuttle_fx_e_burst` | view_effects `tft_scuttlecrab_e_burst`（大表，tft.dll 在它身上播，z 3；左右对称） | 70 × 44 |
| `scuttle_fx_e_slow` | view_buffs `tft_scuttlecrab_e_slow`（跟随被减速的人，脚下，z 3；左右对称） | 24 × 8 |
| `scuttle_fx_r_dig` | view_effects `tft_scuttlecrab_r_dig`（大表，跟随它，地面上，z -1；左右对称） | 60 × 26 |
| `scuttle_fx_r_burst` | view_effects `tft_scuttlecrab_r_burst`（大表，跟随它，z 3；左右对称） | 84 × 48 |
| `scuttle_fx_r_up` | view_effects `tft_scuttlecrab_r_up`（跟随被击飞的人，z 3；左右对称） | 22 × 28 |
| `scuttle_icon_skill` | skill_icons[0] `asset/tft/icons/tft_scuttlecrab_skill` | 64 × 64 |
| `scuttle_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_scuttlecrab_skill2` | 64 × 64 |
| `scuttle_icon_ult` | skill_icons[2] `asset/tft/icons/tft_scuttlecrab_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_scuttlecrab_fx`（小的）和 `tft_scuttlecrab_big`（q_shrine、e_burst、r_dig、r_burst），tag = 名字。
- q_shrine 断言左右上下都对称（神龛范围的画面，会随方向转），其余断言左右对称。
- q_shrine 是神龛范围（RangePeriodProjectile）的画面，在它脚下的地面上（z -1）；r_dig 是它身上的 caster 画面（跟随、地面 z -1，整段钻地 2.5 秒，第 3–8 帧循环）；r_burst 是钻出那一拍的 caster 画面；e_burst、p_heal 是 tft.dll 播的（蟹壳碎、绿霸符）；a_hit、r_up 是打中的画面；q_haste 是队友身上的 buff，e_slow 是敌人身上的 buff，e_shell 是它自己身上的 buff。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
