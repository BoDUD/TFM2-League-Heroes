# 绯红树怪：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图 + 3 个技能图标。** 造型已定（`design/cinderling_design.png`：3/4 朝右、四脚着地蹲着的矮胖小树皮兽：深紫褐的树皮身子，前腿上暖褐的木头甲片和青苔；背上一排浅绿色的高尖叶；脸是圆圆的木头面具，左边一只发光的橙色大眼睛，右边一个发光的螺旋纹，下面一排尖牙）。它在游戏里是**高清**的（每个游戏格子里约 2.3×2.3 个细像素），30 格高、40 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/cinderling_size.png`：它缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是峡谷红 buff 营地（火星、红霸符的火光）、婕拉（叶子、草根）、布兰德（火焰）和雷克塞（钻地的泥土）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **绯红树怪是红 buff 营地的小树苗兽，特效都是它的味道**：**锋利的绿叶刃（边缘是发光的橙红刃口）**、红 buff 的**火星和橙红小火苗**、**棕色的泥块和草根**、一点树皮；不要闪电、不要蓝色、不要紫色魔法、不要光滑的霓虹光束。
> - **特效要亮**：每个火光和刃口都有最亮一档的黄白色芯，暗底上一眼能看见。**火焰、冲击环、尘土没有黑描边**（叶子和泥块可以有深色的边）。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：飞行的三张（a_leaf、q_leaf、r_leaf）**上下对称、朝右**（游戏按飞行方向转）；其余所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 交付方式：
>   - 每张生成后按格子取回（每格取多数颜色）。
>   - 交付 8 倍的 `cinderling_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。
>   - 图标交付 `cinderling_icon_<名字>.png`（64×64）。
>   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。
>   - 都放在 `outputs/cinderling_fx/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/cinderling_fx_pack_done.zip`。
> - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「余烬叶」 | 往前一蹦，甩出一片带火星的叶子 | `a_leaf` · `a_hit` |
| 被动「绯红霸符」 | 每放一个技能攻击力叠一层；叠满后普攻带灼烧 | `p_full` · `p_burn` |
| 技能 1「刃叶」 | 五片叶刃绕弧聚向目标：物理伤害 + 重伤 + 灼烧 | `q_leaf` · `q_hit` · `q_wound` · `p_burn` |
| 技能 2「钻土突袭」 | 钻进地里，从离敌人远的地方钻出来，周围敌人减速 | `e_dig` · `e_pop` · `e_slow` |
| 大招「燎原叶暴」 | 站起来，背上的叶子着火；几秒内不停朝附近敌人射燃烧的叶刃，自己攻速变快 | `r_cast` · `r_blaze` · `r_leaf` · `r_hit` · `p_burn` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 余烬火光（它的眼睛和螺旋纹）：`#FFF6C8`、`#FFD23A`、`#FF8A1E`、`#E8361A`、`#9E1410`、`#5A0A0C`；
  - 叶子：`#E2F08A`、`#B8DC6A`、`#72AE45`、`#3F7A36`、`#24492A`；
  - 木头（面具、腿上的甲片）：`#E0A878`、`#B97A4E`、`#8A5536`、`#5A3524`；
  - 树皮（深紫褐）：`#7A5A6A`、`#54384A`、`#3A2433`、`#22141E`；
  - 泥土：`#A88A62`、`#7A6044`、`#54402E`、`#33261C`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `cinderling_fx_a_leaf.png`：普攻「余烬叶」：飞出去的一片燃烧的叶子，4 帧循环

一片**边缘烧着橙红火光的绿叶**，叶尖朝右，后面拖两三颗火星。4 帧循环：叶子微微翻动、火星闪。**上下对称、朝右**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A), an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A FLYING EMBER LEAF, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a pointed green leaf 7 squares long and 3 tall, its tip to the right, a 1-square glowing orange-red rim along its edges and a light vein down the middle, two or three tiny embers trailing behind it on the left (mirrored top and bottom); frames 1-4 the leaf's light and dark halves swapping as it flutters and the embers flickering. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 4 equal 10:6 cells, image size 640x96 (each cell 160x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `cinderling_fx_a_hit.png`：普攻：叶子打中，4 帧

叶子打中：一下橙黄的小闪光，**两道交叉的绿色叶痕**（像叶刃划过），几颗火星和两片碎叶往两边飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A), an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A LEAF CUT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small hot yellow-white flash 4 squares across; 2 TWO short green LEAF SLASHES crossing in an X, 8 squares tall, glowing orange-red edges, a few embers flying out to both sides; 3 the slashes fading, two torn leaf bits falling outward; 4 the last embers. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `cinderling_fx_p_full.png`：被动「绯红霸符」：叠满层，6 帧循环

霸符叠满的时候：它**背上的叶尖冒出小小的橙红火苗**，一颗颗火星往上飘，身体两侧边缘有一点红光。很淡，只在叶尖和边缘。**它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: AN EMBER CROWN, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the critter crouches in the middle, not drawn: about 40 squares wide and 30 tall from its tallest leaf to the ground, on all fours, its round wooden mask at the front right, its leaf spines on top: small orange-red FLAME TIPS 2-4 squares tall at the tips of its leaf spines along the top of the cell (mirrored), single embers rising above them, a faint red glint at both side edges of the body; frames 1-6 the flame tips flickering in turn and the embers rising a few squares a frame (every frame left-right symmetric). Only at the top and the edges; INSIDE stays EMPTY (its body). everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 6 equal 44:36 cells, image size 4224x576 (each cell 704x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `cinderling_fx_p_burn.png`：灼烧（被动叠满的普攻、刃叶、大招都用），6 帧循环

被烧着的人：身体两侧下半身**几簇小小的橙红火苗**往上窜，夹着一两片烧焦的小叶子，几颗火星往上飘。很小，不要盖住人。**人站的地方留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A LEAF-FIRE BURN, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: on EACH side of its lower body (mirrored) two small orange-red FLAME TONGUES 3-6 squares tall with yellow cores, one tiny scorched leaf curling in the flames, two or three single embers rising beside its body; frames 1-6 the flames flickering up and down in turn and the embers rising (every frame left-right symmetric). Small; the middle (its body) stays EMPTY. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:26 cells, image size 1920x416 (each cell 320x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `cinderling_fx_q_leaf.png`：技能 1「刃叶」：飞出去的锋利叶刃，4 帧循环

一片**又细又尖的锋利绿叶刃**（比普攻的叶子更长更尖、边缘是亮橙红的刃口），叶尖朝右，后面一道短短的绿色残影。4 帧循环：叶刃转动发亮。**上下对称、朝右**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A), an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A RAZOR LEAF, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a long narrow pointed green LEAF BLADE 9 squares long and 3 tall, its tip to the right, its two edges a bright orange-red cutting line, a pale vein, and a short faint green streak behind it on the left; frames 1-4 the blade spinning along its length (the light edge moving from top to bottom and back, mirrored) and a glint running along it. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 4 equal 12:7 cells, image size 768x112 (each cell 192x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `cinderling_fx_q_hit.png`：技能 1「刃叶」：五片叶刃聚在目标身上，5 帧

五片叶刃从四周**一起扎到目标身上**：一圈叶刃划痕从外往里聚拢成星形，中间爆一下橙红的火花，碎叶和火星往外飞。**人站的地方留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A), an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A FIVE-LEAF CONVERGENCE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn (only its middle third): 1 five short green LEAF SLASHES at the edges of the cell, pointing inward like a star (one from the top, two from the upper sides, two from the lower sides, mirrored); 2 the slashes meeting at the body's middle, glowing orange-red edges, a small yellow-white flash where they meet; 3 an orange-red spark burst 10 squares across, torn leaf bits and embers flying out; 4 the slashes and sparks fading to dark red, leaf bits falling; 5 the last embers and one falling leaf on each side. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 5 equal 26:22 cells, image size 2080x352 (each cell 416x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `cinderling_fx_q_wound.png`：技能 1「刃叶」：重伤印记，6 帧循环

被重伤（受到的治疗变少）的人头顶：**一片裂成两半的绿叶**，裂口冒橙红的光，下面一个小小的暗红「十」字被叶子划破（表示治疗被削弱）。一跳一跳地发光。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A), an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A WOUND MARK, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head: a small round green LEAF 8 squares tall SPLIT down the middle by a glowing orange-red crack, the two halves a square apart, a small dark red PLUS SIGN behind it cut through by the crack (healing cut); frames 1-6 the crack pulsing brighter and dimmer and the mark bobbing one square up and down. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 6 equal square cells, image size 960x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `cinderling_fx_e_dig.png`：技能 2「钻土突袭」：钻进地里，5 帧

它钻进地里的地方：**地面裂开一个土坑**，一圈泥块、草屑和几片叶子往两边上方喷起再落下，最后留一小堆土。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth ramp (#A88A62, #7A6044, #54402E, #33261C), a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A DIG-IN BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low on the ground (a flat ellipse, seen from above at an angle): 1 the ground cracking in a ring 24 squares wide; 2 clods of brown EARTH, grass bits and two green leaves thrown up and out to both sides, a dark hole in the middle (an ellipse 16 squares wide, 4 tall); 3 the clods at their highest (10 squares up), dust puffs; 4 the clods falling back; 5 a small mound of loose earth over the hole and a few last falling bits. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 5 equal 40:18 cells, image size 3200x288 (each cell 640x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `cinderling_fx_e_pop.png`：技能 2「钻土突袭」：钻出来的冲击，6 帧

它从地里钻出来：**地面炸开**，一圈泥土冲击环往外扩（扁椭圆），大块泥块、草根和绿叶往上往两边飞，周围的人被震得减速。**中间（它的位置）留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth ramp (#A88A62, #7A6044, #54402E, #33261C), a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A BURST OUT OF THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low on the ground: 1 a crack ring and a puff of dust 16 squares wide; 2 the ground bursting: big clods of brown EARTH, roots and green leaves thrown up and out to both sides, a flat ring of dust and earth (an ellipse 34 squares wide, 8 tall); 3 the ring 46 squares wide, clods at their highest (14 squares up); 4 the ring thinning into dust, clods falling; 5 dust settling, leaves fluttering down; 6 the last dust. The middle (where it lands) stays EMPTY. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 6 equal 48:26 cells, image size 4608x416 (each cell 768x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `cinderling_fx_e_slow.png`：技能 2「钻土突袭」：被震得减速，6 帧循环

被减速的人：脚边**一圈松土和几根细草根缠着脚踝**，几粒泥土轻轻跳动。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth ramp (#A88A62, #7A6044, #54402E, #33261C), a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: MUD AND ROOTS, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): on EACH side (mirrored) a low heap of loose brown earth and two thin pale ROOTS curling round the ankle line, a tiny green sprout; frames 1-6 the roots tightening and loosening a square and a few earth grains hopping (every frame left-right symmetric). Subtle. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 6 equal 22:8 cells, image size 2112x128 (each cell 352x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `cinderling_fx_r_cast.png`：大招「燎原叶暴」：叶子着火，6 帧

它站起来开大的一下：**背上的叶子一下子烧起来**，一圈橙红的火焰从它身后往上冲，火星和燃烧的叶片往四周炸开，地面一圈火光。**它的身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A WILDFIRE IGNITION, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the critter standing up on its back legs in the middle, not drawn (about 26 squares wide and 40 tall): 1 a hot yellow-white flash behind its upper back; 2 a fan of orange-red FLAMES bursting up behind and round its upper body, tallest at the top (12 squares), a flat ring of fire light on the ground (an ellipse 40 squares wide, 8 tall); 3 BURNING LEAVES (green with orange flaming edges) blown out to both sides (mirrored), embers everywhere; 4 the flames sinking to the edges, the leaves still flying; 5 small flames and the ground glow fading; 6 the last rising embers. The middle (its body) stays EMPTY. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:48 cells, image size 5376x768 (each cell 896x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `cinderling_fx_r_blaze.png`：大招「燎原叶暴」：燃烧的叶子环绕，6 帧循环

大招期间：**几片燃烧的叶子绕着它转**（前后各几片，像一圈火叶旋风），叶尖拖着火星，背上叶尖有火苗。**它的身体位置留空**，叶子只在身体外圈。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A RING OF BURNING LEAVES, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the critter crouches in the middle, not drawn: about 40 squares wide and 30 tall from its tallest leaf to the ground, on all fours, its round wooden mask at the front right, its leaf spines on top: six small BURNING LEAVES (green, 4 squares long, orange-red flaming edges, a tiny ember trail) circling round the body on a flat ellipse 48 squares wide and 14 tall at the body's middle height, three on each side in mirrored positions, the ones behind the body darker; small flame tips on its leaf spines along the top; frames 1-6 the leaves moving round the ellipse (mirrored pairs: every frame left-right symmetric) and embers rising. Only round the body's edge; INSIDE stays EMPTY (its body). everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 6 equal 52:40 cells, image size 4992x640 (each cell 832x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `cinderling_fx_r_leaf.png`：大招「燎原叶暴」：射出去的燃烧叶刃，4 帧循环

一片**整个烧着的叶刃**：叶子被火包住，叶尖朝右，后面拖一道短短的火焰尾巴。4 帧循环：火焰跳动。**上下对称、朝右**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A FLAMING LEAF BLADE, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a pointed leaf 7 squares long wrapped in orange-red FLAME, its tip to the right (a hot yellow core along the leaf, the green showing at its middle), a short flame tail 4 squares long streaming to the left (mirrored top and bottom); frames 1-4 the flames flickering and the tail waving. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `cinderling_fx_r_hit.png`：大招：燃烧叶刃打中，4 帧

燃烧的叶刃打中：一下橙黄的火花爆开，几片烧焦的碎叶和火星往外飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a leaf green ramp (#E2F08A, #B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A FIERY LEAF IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a hot yellow-white flash 5 squares across; 2 an orange-red burst of flame 12 squares across, two scorched leaf bits and embers flying out to both sides; 3 the flames breaking into embers, the leaf bits falling; 4 the last embers. everything is a little RED-CAMP SAPLING CRITTER's power: RAZOR-SHARP GREEN LEAVES with glowing orange-red edges, EMBERS and small orange-red flames (the red buff's fire), clods of brown EARTH and torn grass, a little bark; flat shades, crisp blocky shapes; no lightning, no blue, no purple magic, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `cinderling_icon_skill.png`：技能 1「刃叶」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square warm wood frame with little orange ember corners, a deep green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: five sharp green leaf blades with glowing orange-red edges flying in a curve from the left and converging on one point at the right, small embers. No text, no letters.
```

### 图标 2. `cinderling_icon_skill2.png`：技能 2「钻土突袭」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square warm wood frame with little orange ember corners, a deep green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a little round wooden mask with one glowing orange eye bursting up out of cracked brown earth, clods and green leaves flying up. No text, no letters.
```

### 图标 3. `cinderling_icon_ult.png`：大招「燎原叶暴」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square warm wood frame with little orange ember corners, a deep green-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a whirl of burning green leaves wreathed in orange-red flames spiralling round a hot ember core, sparks flying. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `cinderling_fx_a_leaf` | view_projectiles `tft_cinderling_a_leaf`（追踪弹道，随飞行方向转；上下对称、朝右） | 10 × 6 |
| `cinderling_fx_a_hit` | view_effects `tft_cinderling_a_hit`（跟随目标，z 2；左右对称） | 14 × 12 |
| `cinderling_fx_p_full` | view_buffs `tft_cinderling_p_full`（大表，跟随它，z 3；左右对称） | 44 × 36 |
| `cinderling_fx_p_burn` | view_buffs `tft_cinderling_p_burn`（跟随被烧的人，z 4；左右对称） | 20 × 26 |
| `cinderling_fx_q_leaf` | view_projectiles `tft_cinderling_q_leaf`（五片一起绕弧飞向目标，随飞行方向转；上下对称、朝右） | 12 × 7 |
| `cinderling_fx_q_hit` | view_effects `tft_cinderling_q_hit`（跟随目标，z 3；左右对称） | 26 × 22 |
| `cinderling_fx_q_wound` | view_buffs `tft_cinderling_q_wound`（跟随被重伤的人，头顶上方，z 3；左右对称） | 10 × 10 |
| `cinderling_fx_e_dig` | view_effects `tft_cinderling_e_dig`（它钻下去的地方，地面上，z 3；左右对称） | 40 × 18 |
| `cinderling_fx_e_pop` | view_effects `tft_cinderling_e_pop`（它钻出来的地方，地面上，z 3；左右对称） | 48 × 26 |
| `cinderling_fx_e_slow` | view_buffs `tft_cinderling_e_slow`（跟随被减速的人，脚下，z 3；左右对称） | 22 × 8 |
| `cinderling_fx_r_cast` | view_effects `tft_cinderling_r_cast`（大表，跟随它，z 3；左右对称） | 56 × 48 |
| `cinderling_fx_r_blaze` | view_buffs `tft_cinderling_r_blaze`（大表，跟随它，z 3；左右对称） | 52 × 40 |
| `cinderling_fx_r_leaf` | view_projectiles `tft_cinderling_r_leaf`（追踪弹道，随飞行方向转；上下对称、朝右） | 12 × 8 |
| `cinderling_fx_r_hit` | view_effects `tft_cinderling_r_hit`（跟随目标，z 3；左右对称） | 16 × 16 |
| `cinderling_icon_skill` | skill_icons[0] `asset/tft/icons/tft_cinderling_skill` | 64 × 64 |
| `cinderling_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_cinderling_skill2` | 64 × 64 |
| `cinderling_icon_ult` | skill_icons[2] `asset/tft/icons/tft_cinderling_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_cinderling_fx`（小的）和 `tft_cinderling_big`（p_full、r_cast、r_blaze），tag = 名字。
- a_leaf、q_leaf、r_leaf 断言上下对称（朝右），其余断言左右对称。
- a_leaf 是普攻的追踪弹道；q_leaf 是五片绕弧的追踪弹（伤害在它身上）；r_leaf 是大招每一下的追踪弹；a_hit、q_hit、r_hit 跟随目标；e_dig 在它钻下去的地方，e_pop 在它钻出来的地方；r_cast 是它身上的 caster 画面；p_full、r_blaze 是它身上的 buff；p_burn、q_wound、e_slow 是敌人身上的 buff。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
