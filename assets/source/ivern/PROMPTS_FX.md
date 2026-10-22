# 翠神 艾翁：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型已定（`design/ivern_design.png`：左边是艾翁——Q 版树人，浅灰白树皮脸、大鼻子、笑脸、一大把绿叶胡子、两只浅灰绿羊角、头顶红蘑菇、一手小树枝一手苹果、树根脚；右边是他的岩石好朋友小菊）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），40 格高、41 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/ivern_size.png`：艾翁、小菊放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里艾翁自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**艾翁是森林之神，所有特效都是自然的魔法**：清脆的叶子、卷曲的藤和刺、金色的光点和花瓣、泥土和碎石，不要光滑的霓虹能量。颜色：**嫩绿的叶子 + 金色的阳光光点**是他的魔法，**棕色**是藤和树根，**粉白**是花瓣，**土黄和青苔灰绿**是小菊的尘土和石块。
> - **小菊本人不在这份里**：她的身体动作在姿势包里画；这里只画她脚下的尘土、冲击波和拳头打中的石屑。
> - **特效要亮**：每片叶子、每道光都有最亮一档或白色的高光，暗底上一眼能看见。
> - **光、尘土、冲击波都没有黑描边**（叶子、藤、石块也不要描黑边，用它自己最深的一档）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`a_seed`、`q_vine`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ivern_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/ivern_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/ivern_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 扔出一颗发光的种子 | `a_seed` · `a_hit` |
| 被动里的「揠苗助攻」 | 每次放 E，脚下长出一片草丛：站在里面的队友加攻击，他自己的普攻带魔法伤害 | `w_brush` · `w_buff` · `w_hit` |
| 技能 1 =「种豆得瓜」 | 给身边的队友（没人就给自己）套种子护盾，2 秒后爆开，伤害并减速周围的敌人 | `e_seed` · `e_burst` · `e_slow` |
| 技能 2 =「根深敌固」 | 甩出荆棘藤，打中禁锢，身边的队友加速冲过去 | `q_vine` · `q_hit` · `q_root` · `q_rush` |
| 大招 =「小菊！」 | 小菊从地里钻到敌方英雄身边，一拳一拳打，第三拳双拳砸地把人震飞 | `r_dust` · `r_hit` · `r_shock`（小菊本人在姿势包） |

连招：**根深敌固 → 种豆得瓜**（藤打中时 E 好了就马上给队友套盾），**小菊！ → 根深敌固**（小菊落地时 Q 好了就缠住同一个人）。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、尘土、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **都是自然的魔法**：叶子、藤、刺、光点、花瓣、尘土、碎石；每片叶子 2–3 档平涂，亮的一边浅一档。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 叶子·嫩绿：`#FFFFFF`、`#F4FFB8`、`#C8F04A`、`#7CC828`、`#3E8A1E`、`#1C4A14`；
  - 阳光·金色：`#FFFFFF`、`#FFF8C8`、`#FFE070`、`#F2B830`、`#B8781A`；
  - 藤和树根·棕色：`#E8B878`、`#B87A3E`、`#7A4A22`、`#4A2A14`；
  - 花瓣·粉白：`#FFFFFF`、`#FFE0F0`、`#FFA8D0`、`#E86AA8`；
  - 尘土·土黄：`#F0E2C4`、`#C8AE84`、`#96785A`、`#62503A`、`#3A2E22`；
  - 小菊的石块·青苔灰：`#C8CCB4`、`#949A80`、`#646A54`、`#3C4034`；
- 打中、爆发居中画，不旋转；地面上的圈（草丛、尘土、冲击波）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：草丛半径 26000，种子爆炸半径 22000）。

### 1. `ivern_fx_a_seed.png`：普攻：扔出去的种子，4 帧循环

一颗发着金绿色光的小种子往前飞，后面拖两片小叶子和一串金色光点。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: A GLOWING SEED, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round seed 3 squares across with a gold-white core in front, two small leaves trailing behind it at mirrored places, a tail of 3 golden light-motes 6 squares long; the leaves flutter each frame. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 4 equal 12:6 cells, image size 768x96 (each cell 192x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `ivern_fx_a_hit.png`：普攻：种子打中，3 帧

种子在目标身上啪地裂开：一圈绿叶向外弹，中间一个金白色的小闪。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: A SEED POPPING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 3 squares across; 2 six small green leaves bursting out at mirrored places, 8 squares across; 3 the leaves further out, turning to their darkest shade. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `ivern_fx_w_hit.png`：草丛里普攻的额外魔法伤害，3 帧

站在艾翁草丛里的人打中敌人：一小撮草叶和金色光点在敌人身上炸开。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: A BURST OF GRASS MAGIC, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white spark 4 across with a ring of thin grass blades pointing out; 2 the blades 10 across with golden light-motes between them; 3 a few motes and blade tips fading. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `ivern_fx_w_brush.png`：揠苗助攻：脚下长出的草丛，12 帧（4 秒）

艾翁脚下一下子长出一片**高高的草丛**（参考 w_brush：一丛丛长长的草叶，叶尖往上、往两边翘），草叶在风里摇，最后枯萎缩回地里。先长出来（3 帧）、在风里摇（7 帧）、再缩回去（2 帧）。**左右对称**，12 帧，一共约 4 秒（草丛持续的时间）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: A PATCH OF TALL BRUSH growing on the ground, 12 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an oval patch on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 48 squares wide and 14 deep, filled with clumps of tall grass blades 8-14 squares high, their tips pointing up and curving out to both sides, darker blades at the back, lighter at the front, a few golden motes floating between them; 1-3 the blades sprouting from the ground and shooting up; 4-10 full brush swaying gently in the wind, the blade tips bending a square to the left and back again, mirrored; 11-12 the blades sinking and wilting back into the ground. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 12 equal 52:28 cells, image size 9984x448 (each cell 832x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `ivern_fx_w_buff.png`：草丛加成：队友脚下的叶子光点，4 帧循环

站进艾翁草丛的队友脚下：几片小叶子和金色光点绕着脚转。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: LEAVES CIRCLING THE FEET on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a faint green ring 14 squares wide and 4 tall, two small leaves and two golden motes riding round it at mirrored places, moving a step each frame. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `ivern_fx_e_seed.png`：种豆得瓜：套在人身上的种子护盾，6 帧循环

被套上护盾的人：身外一圈**绿色的叶脉护盾**（参考 e_shield_pattern：像叶子的叶脉一样的网纹，边上一圈亮绿），胸口浮着一颗发光的金绿色种子，护盾一闪一闪地在长、快要爆了。**只画外圈和种子，身体位置留空**。**左右对称**，6 帧循环（2 秒后爆开）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: A SEED SHIELD round a unit, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: an upright oval shell 22 squares wide and 38 tall drawn only as its rim - a bright green edge 1-2 squares thick with a leaf-vein pattern of thin lines branching inward from it, the inside left empty for the body - and a glowing seed 4 squares across floating at chest height in the middle, gold-white core; the vein lines and the seed pulse brighter in turn, the rim swelling one square in frames 3-4. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 6 equal 24:40 cells, image size 2304x640 (each cell 384x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `ivern_fx_e_burst.png`：种豆得瓜：种子护盾爆开，7 帧

护盾爆开：中间一团金绿色的光炸开，一圈绿叶、尖刺碎片和金色光点往外飞，地上一圈绿色的冲击（参考 e_explosion_edge、e_sharpbits）。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A), a bark-brown ramp (#E8B878, #B87A3E, #7A4A22, #4A2A14).
Effect: THE SEED BURSTING, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the burst centred on the unit's chest (the cell's middle, a little above the bottom third): 1 a gold-white flash 8 across; 2 a round burst of green light 18 across with a bright rim; 3 the burst 30 across, sharp green thorn shards and leaves flying out at mirrored places, a green ring on the ground 32 wide and 8 tall; 4 the shards further out, the light fading to green; 5 leaves drifting and golden motes; 6 a few leaves falling; 7 two or three motes. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 7 equal 36:32 cells, image size 4032x512 (each cell 576x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `ivern_fx_e_slow.png`：减速：脚下缠着的嫩藤，4 帧循环

被种子爆炸减速的敌人脚下：几根绿色的嫩藤从地里伸出来缠住脚，叶子在抖。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a bark-brown ramp (#E8B878, #B87A3E, #7A4A22, #4A2A14).
Effect: CREEPERS ROUND THE FEET on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a dark green patch 14 squares wide and 4 tall with four thin green creepers curling up 4-5 squares at mirrored places, a small leaf on each tip; the creepers sway a square in and out through the frames. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `ivern_fx_q_vine.png`：根深敌固：飞出去的荆棘藤，4 帧循环

一根带刺的**棕绿色荆棘藤**往前甩出去（参考 q_mis_vines、q_mis_frontedge），前头一团绿光，藤上长着小叶子，后面一道淡淡的绿色拖尾。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a bark-brown ramp (#E8B878, #B87A3E, #7A4A22, #4A2A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: A THORNY VINE LASHING FORWARD, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a bright green-gold knot of light 5 squares across at the front, behind it a twisted bark-brown vine 2 squares thick and 20 squares long with small thorns and leaves sticking out at mirrored places above and below, a faint green trail at its far end; the twist shifts a square along the vine each frame. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 4 equal 28:10 cells, image size 1792x160 (each cell 448x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `ivern_fx_q_hit.png`：根深敌固：荆棘藤缠上去，5 帧

荆棘藤打中：一团绿光炸开，几根带刺的藤从四面卷向敌人身上（**只画外圈，身体位置留空**）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a bark-brown ramp (#E8B878, #B87A3E, #7A4A22, #4A2A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: VINES STRIKING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a green-gold flash 8 across at the chest; 2 four thorny vines whipping in from the four diagonals toward the body, mirrored; 3 the vines curling round the body's edge (the body itself left empty), leaves bursting off; 4 the vines tightening, a few leaves falling; 5 the leaves and motes fading. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 5 equal square cells, image size 1920x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `ivern_fx_q_root.png`：根深敌固：缠住两腿的荆棘，4 帧循环

被禁锢的敌人腿上：几根粗粗的**带刺的棕绿荆棘**从地里长出来，一圈一圈缠住两条腿，脚下一圈草根（参考 thorns2）。**只画缠在外面的藤，身体位置留空**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark-brown ramp (#E8B878, #B87A3E, #7A4A22, #4A2A14), a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14).
Effect: THORNY ROOTS BINDING THE LEGS, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the lower half of a standing unit (its legs in the middle, not drawn), three thick bark-brown thorny vines rising from the ground and wrapped round at 3 heights like loose bands (front halves only, each 14 squares wide), small green leaves and thorns on them, a ring of roots on the ground 18 wide and 5 tall; the bands squeeze a little tighter and loosen in turn through the frames. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `ivern_fx_q_rush.png`：根深敌固：冲向被缠住的人的队友，脚下的叶旋风，4 帧循环

加速冲向被禁锢敌人的队友脚下：一圈绿叶和光点卷成的小旋风。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: A LEAF WHIRL AT THE FEET on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a swirl of small leaves and golden motes spinning round an ellipse 16 squares wide and 5 tall, a few streaks of green behind them, moving round a step each frame. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `ivern_fx_r_dust.png`：小菊！：钻出地面的尘土，6 帧

小菊从地里钻出来时脚下的一团**尘土和碎石**：地面裂开，土块和长着青苔的碎石往上、往两边飞，尘土团慢慢散开（参考 r_dirt_splatter、r_dust_ring）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#F0E2C4, #C8AE84, #96785A, #62503A, #3A2E22), a mossy rock ramp (#C8CCB4, #949A80, #646A54, #3C4034), a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14).
Effect: EARTH BURSTING UP, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the ground line on the bottom of the cell: 1 dark cracks in the ground, an oval 30 wide and 8 tall; 2 clods of earth and mossy rock chunks flying up and out to both sides, a dust cloud rising 10 squares; 3 the dust cloud 44 wide and 18 tall, rocks at their highest; 4 the rocks falling, the dust rolling out low; 5 a low ring of dust 46 wide; 6 thin wisps. Dust is soft round puffs in flat shades. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 6 equal 48:24 cells, image size 4608x384 (each cell 768x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `ivern_fx_r_shock.png`：小菊第三拳：砸地的冲击波，6 帧

小菊双拳砸地：地上一圈**冲击波**往外扩（参考 r_shockwave_ground、r_shockwave_rock），一圈石块从地里翘起来，尘土飞扬，把敌人震飞。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#F0E2C4, #C8AE84, #96785A, #62503A, #3A2E22), a mossy rock ramp (#C8CCB4, #949A80, #646A54, #3C4034), a golden sunlight ramp (#FFFFFF, #FFF8C8, #FFE070, #F2B830, #B8781A).
Effect: A GROUND SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred: 1 a bright gold-white crack-star on the ground 12 wide; 2 a ring of jagged rock slabs jutting up round it, 26 wide and 9 tall, dust puffs at their bases; 3 the ring 44 wide, the slabs tilting out, rock chips flying; 4 the ring 54 wide and low, dust rolling; 5 the slabs sinking, a faint dust ring; 6 a few chips and wisps. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 6 equal 56:24 cells, image size 5376x384 (each cell 896x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `ivern_fx_r_hit.png`：小菊的拳头打中，4 帧

小菊一拳打在敌人身上：石屑、尘土和一片青苔溅开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a mossy rock ramp (#C8CCB4, #949A80, #646A54, #3C4034), an earth-dust ramp (#F0E2C4, #C8AE84, #96785A, #62503A, #3A2E22), a leaf-green ramp (#FFFFFF, #F4FFB8, #C8F04A, #7CC828, #3E8A1E, #1C4A14).
Effect: A STONE PUNCH LANDING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 across; 2 grey-green rock chips and dust bursting out 14 across at mirrored places; 3 the chips further out, a moss fleck or two; 4 dust wisps. everything is NATURE MAGIC: crisp leaves, curling vines and thorns, golden light-motes and petals, earthy dust; flat shades, each leaf with a lighter edge; no smooth neon energy.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `ivern_fx_a_seed` | view_projectiles `league_ivern_a_seed`（弹道，z 2；上下对称） | 12 × 6 |
| `ivern_fx_a_hit` | view_effects `league_ivern_a_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `ivern_fx_w_hit` | view_effects `league_ivern_w_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `ivern_fx_w_brush` | view_effects `league_ivern_w_brush`（大表，地上不跟随，z -1；左右对称） | 52 × 28 |
| `ivern_fx_w_buff` | view_buffs `league_ivern_w_buff`（跟随，z -1；左右对称） | 16 × 8 |
| `ivern_fx_e_seed` | view_buffs `league_ivern_e_seed`（跟随，z 3；左右对称） | 24 × 40 |
| `ivern_fx_e_burst` | view_effects `league_ivern_e_burst` / `e_burst_me`（大表，z 3；左右对称） | 36 × 32 |
| `ivern_fx_e_slow` | view_buffs `league_ivern_e_slow`（跟随，z -1；左右对称） | 16 × 10 |
| `ivern_fx_q_vine` | view_projectiles `league_ivern_q_vine`（弹道，z 2；上下对称） | 28 × 10 |
| `ivern_fx_q_hit` | view_effects `league_ivern_q_hit`（跟随目标，z 3；左右对称） | 24 × 24 |
| `ivern_fx_q_root` | view_buffs `league_ivern_q_root`（跟随，z 3；左右对称） | 20 × 20 |
| `ivern_fx_q_rush` | view_buffs `league_ivern_q_rush`（跟随，z -1；左右对称） | 18 × 8 |
| `ivern_fx_r_dust` | view_effects `league_ivern_r_dust`（大表，地上，z -1；左右对称） | 48 × 24 |
| `ivern_fx_r_shock` | view_effects `league_ivern_r_shock`（大表，跟随目标，z -1；左右对称） | 56 × 24 |
| `ivern_fx_r_hit` | view_effects `league_ivern_r_hit`（跟随目标，z 2；左右对称） | 16 × 16 |

- 两张表：`asset/league/effects/league_ivern_fx`（小的）和 `league_ivern_big`（w_brush、e_burst、r_dust、r_shock），tag = 名字（build_ivern.py 的 views；e_burst_me 用 e_burst）。小菊的 r_drop / r_punch / r_slam 由姿势包的小菊帧拼成（PPU 1.9），r_dust 垫在 r_drop 下面、r_shock 垫在 r_slam 下面、r_hit 是每一拳打中的目标身上。
- 弹道（a_seed、q_vine）断言上下对称；其余断言左右对称；w_brush 帧长合计 4 秒（w_t 240 tick），e_seed 跟随被套盾的人、2 秒。
- 用 `pixel_1x/` 切格（import_neeko_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
- 附加包那一步：艾翁的草丛要让**雷恩加尔能扑跳**、**奇亚娜拿到草元素**（用户 2026-10-22），草丛的位置和时长要能被附加包读到。
