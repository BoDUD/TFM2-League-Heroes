# 深红锋喙鸟：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图 + 3 个技能图标。** 造型已定（`design/raptor_design.png`：3/4 朝右、压低身子蹲着的圆胖鸟：红色背羽和尾羽往后上方翘；紫色尖刺鬃毛围着脖子；棕色骨质鸟头、厚弯钩喙、两只发光的橙色眼睛，嘴里透橙光；头顶一个红色尖冠；两条短棕腿、深藏青弯钩大爪）。锋喙鸟在游戏里是**高清**的（每个游戏格子里约 1.56×1.56 个细像素），36 格高、48 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/raptor_size.png`：锋喙鸟缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是霞（羽毛、羽刃、命中）和奎因（华洛、风、烟）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **锋喙鸟是峡谷里的野鸟，特效都是它的味道**：尖尖的红色、橙红色羽毛（边缘亮橙色）、像它眼睛一样的橙色火星、少量紫色尖羽、棕色尘土；不要符文魔法、不要闪电、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、拖尾、尘土没有黑描边**；羽毛和小鸟可以有深色描边。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：飞出去的三种（`a_bolt`、`q_feather`、`r_peck`）**上下对称、朝右**（游戏按飞行方向旋转它们）；其余所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。`r_flock` 的四只小鸟**正面朝着我们**，所以左右对称也自然。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `raptor_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `raptor_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/raptor_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/raptor_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「锋羽射击」 | 甩出一根追踪的红色羽毛 | `a_bolt` · `a_hit` |
| 被动「橙霸符」 | 它的物理伤害减敌人护甲，最多叠 5 层 | `p_shred` |
| 技能 1 =「羽刃扇射」 | 张开翅膀和羽冠，扇形甩出五根羽刃，每根打中第一个敌人 | `q_feather` · `q_hit` |
| 技能 2 =「惊飞跃退」 | 尖叫一声往后一跳，之后几秒攻速大涨 | `e_jump` · `e_rush` |
| 大招 =「鸟群之家」 | 召唤四只小锋喙鸟围在身边，它每次普攻小鸟们一起扑上去啄同一个敌人 | `r_flock` · `r_peck` · `r_peck_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、拖尾、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**（羽毛、小鸟可以有深色描边）。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 羽毛红（背羽尾羽，深红到橙红）：`#FFD9B0`、`#FF7A3D`、`#E8331F`、`#A3122A`、`#5C0A26`；
  - 橙光（眼睛、嘴里的光、橙霸符）：`#FFF7CC`、`#FFD24A`、`#FF9A1F`、`#D9560F`、`#8A2A0A`；
  - 紫色鬃毛：`#CDBDFF`、`#8E6CF0`、`#5B3FC0`、`#35227A`、`#1C1240`；
  - 尘土：`#E8D9BF`、`#BFA27A`、`#8A6A48`、`#523C2A`；
- 打中居中画，不旋转；地面上的尘土是从斜上方看的扁平一团。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `raptor_fx_a_bolt.png`：普攻「锋羽射击」：飞出去的羽毛，4 帧循环

它甩出去的一根羽毛：**一根尖尖的红色羽毛**横着往右飞，羽尖朝右、亮橙色的边，羽根后面拖一小段橙红色的拖尾。**上下对称、朝右**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26), an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A).
Effect: A FLYING FEATHER DART, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): one sharp CRIMSON FEATHER lying along the flight, its pointed tip at the RIGHT, 9 squares long and 3 tall, a bright orange edge on both vanes (mirrored top and bottom), a darker red quill line along its middle, a short orange-red streak trailing off to the left (4 squares); frames 1-4 the trail flickering and one orange glint running along the edge. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 14:6 cells, image size 896x96 (each cell 224x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `raptor_fx_a_hit.png`：普攻「锋羽射击」：羽毛命中，4 帧

羽毛扎中：一下橙白色的小闪光，几片红色的碎羽往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A), a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26).
Effect: A FEATHER IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small orange-white flash 4 squares across; 2 a sharp four-point orange star 10 squares across, four tiny red feather shards flying out to both sides (mirrored); 3 the shards spinning outward and down, two orange sparks; 4 one shard falling on each side. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `raptor_fx_q_feather.png`：技能 1「羽刃扇射」：飞出去的羽刃，4 帧循环

羽刃：比普攻的羽毛**更大、更锋利的一片刀刃似的红羽**，边缘亮橙色像在发烫，后面拖一段带红羽碎片的拖尾。**上下对称、朝右**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26), an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A).
Effect: A FLYING BLADE FEATHER, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a big blade-like CRIMSON FEATHER along the flight, its point at the RIGHT, 13 squares long and 5 tall, both edges glowing hot orange to pale yellow (mirrored top and bottom), a dark red quill along its middle, behind it a 6-square streak of orange-red with two tiny feather flecks (one above, one below); frames 1-4 the edge glow pulsing and the flecks trailing. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `raptor_fx_q_hit.png`：技能 1「羽刃扇射」：羽刃划中，4 帧

羽刃划中：**一个橙色的 X 形划痕**一闪，红色碎羽往两边飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A), a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26).
Effect: A BLADE SLASH IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale yellow flash 5 squares across; 2 a bright orange X of two crossed slash marks 14 squares across, near-white along their middles, red feather shards bursting to both sides (mirrored); 3 the X fading to red, the shards flying out and down; 4 the last red sparks and one falling shard on each side. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `raptor_fx_r_peck.png`：大招「鸟群之家」：小锋喙鸟扑啄，4 帧循环

一只小锋喙鸟扑向敌人的残影：**一个小小的红色泪滴形身影**往右冲，最前面一个棕色的小尖喙，上下各一根紫色小尖羽，后面拖橙红色的速度线。**上下对称、朝右**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26), a purple ruff ramp (#CDBDFF, #8E6CF0, #5B3FC0, #35227A, #1C1240), an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A).
Effect: A DIVING CHICK STREAK, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a tiny crimson teardrop body 6 squares long and 4 tall rushing to the RIGHT, a small brown pointed beak at its right tip, one little purple spike feather above and one below (mirrored), a tiny orange eye glint on each side of its middle line, two thin orange-red speed lines trailing to the left; frames 1-4 the speed lines flickering. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 12:6 cells, image size 768x96 (each cell 192x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `raptor_fx_r_peck_hit.png`：大招「鸟群之家」：小锋喙鸟啄中，4 帧

被小鸟啄中：一下小小的橙色啄击闪光，**几根红色、紫色的小绒毛**往两边飘。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A), a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26), a purple ruff ramp (#CDBDFF, #8E6CF0, #5B3FC0, #35227A, #1C1240).
Effect: A PECK, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a tiny orange-white point; 2 a small orange three-ray peck flash 7 squares across; 3 four tiny fluff feathers (two red, two purple, mirrored) popping out to both sides; 4 the fluff drifting down. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `raptor_fx_e_jump.png`：技能 2「惊飞跃退」：起跳的尘土，5 帧

它受惊往后一跳：起跳的地面上**一团尘土往两边扬起**，几片红羽飘下来。**只在地面和低处**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp (#E8D9BF, #BFA27A, #8A6A48, #523C2A), a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26).
Effect: A TAKE-OFF PUFF, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND and low above it: 1 a flat dust puff 12 squares wide at the bottom middle; 2 two dust clouds rolling out to both sides (mirrored), 30 squares wide, 8 tall, three red feathers popping up from the middle; 3 the clouds 38 squares wide and thinner, the feathers fluttering higher; 4 the dust settling, the feathers drifting down on both sides; 5 the last wisps and one feather on each side. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 5 equal 40:14 cells, image size 3200x224 (each cell 640x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `raptor_fx_e_rush.png`：技能 2「惊飞跃退」：攻速大涨，6 帧循环

攻速大涨：它身子两侧**几道橙红色的速度线往后掠**，身子周围一闪一闪几点橙色火星，羽毛尖上一圈亮橙色。**它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A), a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26).
Effect: A FRENZY RUSH, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the raptor stands in the middle, not drawn: about 49 squares wide and 36 tall, a round crouched bird, its head at the right, its tail feathers at the upper left, its feet on the bottom line of the cell: on EACH side of its body (mirrored) three short orange-red speed streaks sweeping up and outward along its edge, small orange sparks (1x1 and 2x2 squares) blinking round its outline, a thin bright orange flicker along the top edge; frames 1-6 the streaks sliding and the sparks blinking in turn (every frame left-right symmetric). The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:40 cells, image size 5376x640 (each cell 896x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `raptor_fx_p_shred.png`：被动「橙霸符」：破甲标记，6 帧循环

被减护甲的人头顶：**一块裂开的橙色小盾牌**（中间一道锯齿裂缝，裂缝里透着亮橙光），轻轻上下浮动、一闪一闪。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A), a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26).
Effect: A CRACKED ARMOUR MARK, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head: a small orange heater SHIELD 8 squares wide and 10 tall, a jagged CRACK down its middle glowing pale yellow, a darker red rim, one tiny shard chipping off each side (mirrored); frames 1-6 it bobbing one square up and down, the crack's glow pulsing. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal square cells, image size 1152x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `raptor_fx_r_flock.png`：大招「鸟群之家」：围着它的四只小锋喙鸟，6 帧循环

鸟群之家：**四只小锋喙鸟**围在它身边——左右两边各有一只站在地上、一只在肩膀高度扑腾着飞。小鸟是它的缩小版、**正面朝着我们**：红色圆滚滚的绒毛身子、头顶一撮紫色尖毛、棕色小尖喙、两只橙色小眼睛、小短腿；每只约 10×10 格。轮流上下蹦跳、扑腾小翅膀。**中间它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson feather ramp (#FFD9B0, #FF7A3D, #E8331F, #A3122A, #5C0A26), a purple ruff ramp (#CDBDFF, #8E6CF0, #5B3FC0, #35227A, #1C1240), an orange glow ramp (#FFF7CC, #FFD24A, #FF9A1F, #D9560F, #8A2A0A), a dust ramp (#E8D9BF, #BFA27A, #8A6A48, #523C2A).
Effect: THE FLOCK, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the raptor stands in the middle, not drawn: about 49 squares wide and 36 tall, a round crouched bird, its head at the right, its tail feathers at the upper left, its feet on the bottom line of the cell: FOUR TINY BEAKS (baby raptors, each about 10 squares wide and 10 tall, seen FROM THE FRONT facing us so they read the same both ways: a round fluffy CRIMSON body, a little tuft of PURPLE spike feathers on top, a small brown pointed beak in the middle of the face, two tiny glowing ORANGE eyes, two stubby brown legs, two tiny red wings) placed mirrored: on EACH side one chick standing on the bottom line just outside its feet and one chick flapping in the air at its shoulder height just outside its outline; frames 1-6 the standing chicks hopping one square up and down in turn and the flying chicks flapping their wings (up, level, down), every frame left-right symmetric. The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT RAPTOR's: sharp pointed CRIMSON and ORANGE-RED FEATHERS with a bright orange edge, hot ORANGE glints like its eyes, a few PURPLE spike feathers, brown dust; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 84:44 cells, image size 8064x704 (each cell 1344x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `raptor_icon_skill.png`：技能 1「羽刃扇射」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little orange corner studs, a deep wine-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a fan of five sharp blade-like crimson feathers bursting out from the lower left to the upper right, their edges glowing hot orange, small orange sparks round them. No text, no letters.
```

### 图标 2. `raptor_icon_skill2.png`：技能 2「惊飞跃退」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little orange corner studs, a deep wine-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a round crimson raptor with a purple ruff hopping up and backward, its feathers bristling, orange-red speed streaks behind it and a puff of brown dust below. No text, no letters.
```

### 图标 3. `raptor_icon_ult.png`：大招「鸟群之家」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little orange corner studs, a deep wine-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big brown hooked-beak raptor head with a purple ruff and glowing orange eyes, beak open calling, and four tiny round red baby raptors gathered in front of it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `raptor_fx_a_bolt` | view_projectiles `tft_raptor_a_bolt`（随飞行方向旋转；上下对称、朝右） | 14 × 6 |
| `raptor_fx_a_hit` | view_effects `tft_raptor_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `raptor_fx_q_feather` | view_projectiles `tft_raptor_q_feather`（tft.dll 扇形放出的五根，随飞行方向旋转；上下对称、朝右） | 20 × 8 |
| `raptor_fx_q_hit` | view_effects `tft_raptor_q_hit`（跟随目标，z 2；左右对称） | 18 × 16 |
| `raptor_fx_r_peck` | view_projectiles `tft_raptor_r_peck`（随飞行方向旋转；上下对称、朝右） | 12 × 6 |
| `raptor_fx_r_peck_hit` | view_effects `tft_raptor_r_peck_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `raptor_fx_e_jump` | view_effects `tft_raptor_e_jump`（放在它起跳的地面上，不跟随，z -1；左右对称） | 40 × 14 |
| `raptor_fx_e_rush` | view_buffs `tft_raptor_e_rush`（跟随它，z 3；左右对称） | 56 × 40 |
| `raptor_fx_p_shred` | view_buffs `tft_raptor_p_shred`（跟随被减甲的人，头顶上方，z 3；左右对称） | 12 × 12 |
| `raptor_fx_r_flock` | view_buffs `tft_raptor_r_flock`（大表，跟随它，z 3；左右对称） | 84 × 44 |
| `raptor_icon_skill` | skill_icons[0] `asset/tft/icons/tft_raptor_skill` | 64 × 64 |
| `raptor_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_raptor_skill2` | 64 × 64 |
| `raptor_icon_ult` | skill_icons[2] `asset/tft/icons/tft_raptor_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_raptor_fx`（小的）和 `tft_raptor_big`（r_flock），tag = 名字。
- a_bolt、q_feather、r_peck 断言上下对称（朝右），其余断言左右对称。
- a_bolt、r_peck 是普攻的追踪弹道，q_feather 是 tft.dll 扇形放出的羽刃；a_hit、q_hit、r_peck_hit 在被打中的人身上；e_jump 放在它起跳的地面上（不跟随，z -1）；e_rush、r_flock 是它身上的 buff；p_shred 是 tft.dll 给敌人叠的减甲 buff。
- 用 `pixel_1x/` 切格（import_sentinel_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
