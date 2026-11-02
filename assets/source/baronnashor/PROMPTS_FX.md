# 纳什男爵：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图 + 3 个技能图标。** 造型已定（`design/baronnashor_design.png`：3/4 朝右、虚空巨蛇：S 形紫色鳞甲身躯、正面青绿色分节腹甲；蓝紫硬甲头、黄色菱形大眼、红嘴白牙、象牙白獠牙；紫色鳍刺头冠、洋红鳍尖；两只小蛇头、两只象牙白大弯爪、两条紫色短腿）。纳什男爵在游戏里是**高清**的（每个游戏格子里约 2×2 个细像素），46 格高、28 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/baronnashor_size.png`：纳什男爵缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是纳什男爵自己（金铲铲的钻地裂缝、石块、尖刺、酸液、触手）和召唤师峡谷纳什男爵的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **纳什男爵是虚空最大的巨兽，特效都是它的味道**：淡粉芯的**虚空紫 / 洋红**光、冒泡的**亮紫色腐蚀酸液**（金铲铲里它的酸液就是紫色的）、裂开的棕色**土地和飞石**、象牙白的尖牙形状；不要火、不要蓝色电光、不要树叶。
> - **特效要亮**：每个光都有最亮一档或淡粉色的芯，暗底上一眼能看见。**光、冲击环、尘土、酸液没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：除了飞行的酸液 `q_spray`（上下对称、朝右），所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `baronnashor_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `baronnashor_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/baronnashor_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/baronnashor_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「虚空裂隙」 | 战斗中每隔几秒，在附近随机一名敌方英雄脚下喷出虚空触手，伤害并击飞 | `p_tent` |
| 普攻「腐蚀撕咬」 | 往前猛咬，咬到目标和它身后一条直线上的敌人 | `a_hit` |
| 技能 1 =「腐蚀吐息」 | 往前喷一扇形酸液：伤害，护甲和魔抗降低 | `q_spray` · `q_hit` · `q_acid` |
| 技能 2 =「钻地突袭」 | 钻进地里冲到目标脚下破土而出，伤害并击飞身边的敌人 | `e_burst` · `e_hit` |
| 大招 =「虚空之怒」 | 猛砸地面，一圈尖刺从地里刺出；然后连续吐出 10 团酸液落在附近的敌人身上 | `r_spikes` · `r_hit` · `r_fall` · `q_acid` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土、酸液没有黑描边，也不要用最深的颜色给形状描一圈边**（石块和尖刺可以有自己最暗一档的边）。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 虚空紫（裂隙、触手、尖刺的光）：`#FFE8FF`、`#FF8AEC`、`#D83CD0`、`#8A2AB0`、`#43186E`；
  - 腐蚀酸液：`#FFEAFF`、`#EBA8FF`、`#B464F2`、`#7834C2`、`#3C1A72`；
  - 土地和石块：`#D8C8B4`、`#A08870`、`#6E5A4A`、`#47392F`、`#2A211C`；
  - 象牙白（尖牙）：`#FFF6DC`、`#F2D8A0`、`#C9A46E`、`#8A6A44`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `baronnashor_fx_a_hit.png`：普攻「腐蚀撕咬」：咬中，4 帧

一口咬中：**上下两排象牙白的尖牙形状一下合拢**，中间一下紫色冲击闪光，几滴紫色酸液往两边溅。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ivory ramp (#FFF6DC, #F2D8A0, #C9A46E, #8A6A44), a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E), a corrosive acid ramp (#FFEAFF, #EBA8FF, #B464F2, #7834C2, #3C1A72).
Effect: A VOID BITE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of ivory FANG shapes, one at the top of the cell pointing down and one at the bottom pointing up, wide apart (each row 12 squares wide, four fangs); 2 the rows snapped together in the middle, a bright pale-pink and violet flash between them; 3 the fangs fading, a violet burst 14 squares across, a few glossy violet acid drops flying out to both sides (mirrored); 4 the last drops falling. everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `baronnashor_fx_q_spray.png`：技能 1「腐蚀吐息」：从嘴里喷出的一股酸液，4 帧循环

一股往前喷的酸液：**左边窄、右边张开的一团扇形酸雾**（往右喷），里面是亮紫色的酸液团和泡泡，边缘一圈紫色的虚空雾气，最前端几滴大酸滴。**上下对称、朝右**，4 帧循环（酸液团和泡泡往前滚）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a corrosive acid ramp (#FFEAFF, #EBA8FF, #B464F2, #7834C2, #3C1A72), a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E).
Effect: A SPRAY OF CORROSIVE ACID, 4 looping frames, SYMMETRIC TOP TO BOTTOM in every frame, square for square, pointing RIGHT (the game turns it with its flight; turned half round to the left it must read the same): a fan-shaped gush flying RIGHT - narrow at the left edge (6 squares tall), opening to 20 squares tall at the right; inside it blobs and bubbles of bright glossy violet acid with pale pink highlights, a thin haze of void violet along its top and bottom edges (mirrored), a few big acid drops leading at the right; frames 1-4 the blobs and bubbles rolling to the right. everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 4 equal 48:22 cells, image size 3072x352 (each cell 768x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `baronnashor_fx_q_hit.png`：技能 1「腐蚀吐息」：被酸液泼中，4 帧

被酸液泼中：一团**亮紫色的酸液啪地溅开**，几滴往两边飞，冒起一缕淡紫色的腐蚀烟。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a corrosive acid ramp (#FFEAFF, #EBA8FF, #B464F2, #7834C2, #3C1A72), a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E).
Effect: AN ACID SPLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a glossy violet blob 6 squares across with a pale pink core; 2 the blob bursting into a splash 16 squares across, drops flying out to both sides (mirrored); 3 the drops falling, small bubbles, a thin violet hiss of smoke rising from the middle; 4 the last bubbles and smoke. everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `baronnashor_fx_q_acid.png`：技能 1：被腐蚀（护甲魔抗降低），6 帧循环

被腐蚀的人：**身体两侧边缘几滴亮紫色酸液往下滴**，脚下一小滩冒泡的酸液，偶尔冒一缕淡紫色的烟。**身体位置留空**、很淡。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a corrosive acid ramp (#FFEAFF, #EBA8FF, #B464F2, #7834C2, #3C1A72), a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E).
Effect: CORROSION ON A UNIT, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 24 tall stands in the middle, not drawn: on EACH side (mirrored) along the body's edges two or three glossy violet acid DRIPS sliding down, a small bubbling acid puddle at the feet (an ellipse 18 squares wide, 3 tall) with bubbles popping, now and then a thin violet smoke wisp rising from the shoulders; frames 1-6 the drips falling and the bubbles popping in turn (every frame left-right symmetric). Subtle. The middle stays EMPTY (the unit). everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 6 equal 22:26 cells, image size 2112x416 (each cell 352x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `baronnashor_fx_e_burst.png`：技能 2「钻地突袭」：破土而出，6 帧

它从地里冲出来：**地面一圈裂开**（椭圆的裂缝，缝里透出紫色的虚空光），**土块和石头往上、往两边飞**，最后一圈尘土。**中间它的位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth and rock ramp (#D8C8B4, #A08870, #6E5A4A, #47392F, #2A211C), a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E).
Effect: THE GROUND BURSTING OPEN, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the bottom of the cell is the ground, the serpent bursts up through the middle (not drawn): 1 a ring of CRACKS in the ground round the middle (an ellipse 30 squares wide, 8 tall), void-violet light glowing in the cracks; 2 the ground broken open, brown earth chunks and grey-brown rocks thrown up and out to both sides (mirrored), violet light bursting up from the cracks; 3 the rocks at their highest, a dust ring 50 squares wide on the ground; 4 the rocks falling, the dust rolling outward; 5 rubble on the ground round the middle, the cracks dimming; 6 the last dust. The middle above the ground stays EMPTY. everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 6 equal 60:40 cells, image size 5760x640 (each cell 960x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `baronnashor_fx_e_hit.png`：技能 2「钻地突袭」：被击飞，4 帧

身边被击飞的人：脚下**一下紫色的冲击**，几块小石头往上蹦，一圈短短的往上的速度线。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E), an earth and rock ramp (#D8C8B4, #A08870, #6E5A4A, #47392F, #2A211C).
Effect: A KNOCK-UP HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a violet flash 8 squares across at the bottom middle; 2 a violet burst 14 squares across with a pale pink core, three short upward streaks on each side (mirrored), small rocks popping up; 3 the burst fading, the rocks at their highest; 4 the rocks falling, the last violet sparks. everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `baronnashor_fx_r_spikes.png`：大招「虚空之怒」：一圈尖刺从地里刺出来，7 帧

它猛砸地面：**以它为中心的一大圈地面裂开**，**一圈尖锐的紫色虚空尖刺从地里刺出来**（里圈矮、外圈高，尖端洋红色发光），然后尖刺碎掉缩回地里，剩一圈裂缝和尘土。**中间它的位置留空**。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E), an earth and rock ramp (#D8C8B4, #A08870, #6E5A4A, #47392F, #2A211C).
Effect: A RING OF VOID SPIKES, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the bottom of the cell is the ground, round the serpent stands in the middle, not drawn: about 28 squares wide and 46 tall, a tall S-curved body on two short legs, its big crested head at the top: 1 a ring of glowing violet CRACKS spreading on the ground (an ellipse 80 squares wide, 22 tall); 2 sharp dark-violet SPIKES punching up out of the cracks all round the ring (each 3-4 squares wide at its base, 8-16 tall, pointing up, their tips bright magenta), the far ones smaller and higher in the cell, the near ones bigger and lower (mirrored); 3 the spikes at full height, magenta glow at their tips, earth chunks flying; 4 the spikes cracking; 5 the spikes shattering into violet shards and falling back; 6 a ring of rubble and glowing cracks; 7 the last dust and glow. The middle stays EMPTY (its body). everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 7 equal 96:48 cells, image size 10752x768 (each cell 1536x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `baronnashor_fx_r_hit.png`：大招「虚空之怒」：被尖刺刺中，4 帧

被尖刺刺中的人：**脚下一根紫色尖刺往上一刺**，一下洋红色闪光，几块碎片往两边飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E), an earth and rock ramp (#D8C8B4, #A08870, #6E5A4A, #47392F, #2A211C).
Effect: A SPIKE PIERCE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small magenta flash at the bottom middle; 2 one sharp dark-violet SPIKE 3 squares wide shooting straight up from the bottom, 16 squares tall, its tip bright magenta, a violet burst at its base; 3 the spike cracking, violet shards flying out to both sides (mirrored); 4 the last shards. everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 4 equal 18:22 cells, image size 1152x352 (each cell 288x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `baronnashor_fx_r_fall.png`：大招「虚空之怒」：一团酸液从天上落下溅开，7 帧

一团酸液从天上落下来：**一团冒泡的亮紫色酸液球（外面一圈紫色雾气）从格子最上面直直落下来**，后面拖着几滴酸液，砸在格子最下面的地上，**啪地溅开一大滩冒泡的酸液**，一圈紫色的腐蚀烟。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a corrosive acid ramp (#FFEAFF, #EBA8FF, #B464F2, #7834C2, #3C1A72), a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E).
Effect: A FALLING ACID BALL, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the bottom of the cell is the ground: 1 a round bubbling ACID BALL 8 squares across (glossy violet, a pale pink highlight, a thin violet haze round it) at the very top of the cell, a few drops trailing above it; 2 the ball a third of the way down; 3 the ball two thirds down; 4 the ball hitting the ground at the bottom, a bright pale-pink splash flash; 5 a wide SPLASH of acid 20 squares across at the bottom, drops flying out low to both sides (mirrored); 6 a bubbling acid puddle on the ground (an ellipse 18 squares wide), violet smoke hissing up; 7 the puddle fading, the last smoke. everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 7 equal 24:52 cells, image size 2688x832 (each cell 384x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `baronnashor_fx_p_tent.png`：被动「虚空裂隙」：敌人脚下冒出一条虚空触手，7 帧

一条虚空触手从地里冒出来把人顶飞：地面先**裂开一个透着紫光的小洞**，然后**一条粗壮的紫色触手（尖端洋红、表面一圈圈的环纹）笔直往上窜出来**，到最高后缩回洞里，洞口留一点紫光和碎土。触手**笔直朝上、左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void-violet ramp (#FFE8FF, #FF8AEC, #D83CD0, #8A2AB0, #43186E), an earth and rock ramp (#D8C8B4, #A08870, #6E5A4A, #47392F, #2A211C).
Effect: A VOID TENTACLE BURSTING UP, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the bottom of the cell is the ground: 1 a small hole cracking open at the bottom middle (an ellipse 12 squares wide, 4 tall), violet light inside it; 2 the tip of a thick TENTACLE pushing out of the hole, earth chunks flying to both sides (mirrored); 3 the tentacle shooting STRAIGHT UP, 6 squares thick at its base narrowing to a bright magenta tip, dark violet with lighter ring bands, 30 squares tall; 4 the tentacle at its full height 50 squares tall, its tip pointing straight up, a violet glow at the hole; 5 the tentacle sinking back, 30 squares; 6 only its tip at the hole; 7 the hole closing, the last violet light and rubble. The tentacle stays upright and left-right symmetric in every frame. everything is the power of the VOID'S GREATEST BEAST, a giant serpent that bursts out of the earth: glowing VOID VIOLET-MAGENTA light with pale pink cores, bubbling glossy VIOLET CORROSIVE ACID, cracked brown EARTH and flying rocks, ivory fang shapes; flat shades, crisp blocky shapes; no fire, no blue electricity, no leaves.
Layout: one horizontal row of 7 equal 28:60 cells, image size 3136x960 (each cell 448x960, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `baronnashor_icon_skill.png`：技能 1「腐蚀吐息」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a blue-violet serpent head with a yellow eye seen from the side, its jaws wide open with ivory fangs, a fan of bubbling glossy violet acid gushing out of its mouth to the right. No text, no letters.
```

### 图标 2. `baronnashor_icon_skill2.png`：技能 2「钻地突袭」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: purple crest fins with magenta tips cutting through broken brown earth, rocks flying up, a glowing violet crack beneath. No text, no letters.
```

### 图标 3. `baronnashor_icon_ult.png`：大招「虚空之怒」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a ring of sharp violet spikes with magenta tips bursting out of cracked ground, a big blue-violet serpent head roaring above them, glossy violet acid drops falling round it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `baronnashor_fx_a_hit` | view_effects `tft_baronnashor_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `baronnashor_fx_q_spray` | view_projectiles `tft_baronnashor_q_spray`（大表，直线弹道，从嘴里喷出飞得很快，随飞行方向旋转；上下对称、朝右） | 48 × 22 |
| `baronnashor_fx_q_hit` | view_effects `tft_baronnashor_q_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `baronnashor_fx_q_acid` | view_buffs `tft_baronnashor_q_acid`（跟随被腐蚀的人，z 3；左右对称） | 22 × 26 |
| `baronnashor_fx_e_burst` | view_effects `tft_baronnashor_e_burst`（大表，放在它冒出来的地面上，不跟随，z -1；画面最下面是地面；左右对称） | 60 × 40 |
| `baronnashor_fx_e_hit` | view_effects `tft_baronnashor_e_hit`（跟随目标，z 2；左右对称） | 18 × 20 |
| `baronnashor_fx_r_spikes` | view_effects `tft_baronnashor_r_spikes`（大表，放在它脚下的地面上，不跟随，z -1；画面最下面是地面；左右对称） | 96 × 48 |
| `baronnashor_fx_r_hit` | view_effects `tft_baronnashor_r_hit`（跟随目标，z 2；左右对称） | 18 × 22 |
| `baronnashor_fx_r_fall` | view_effects `tft_baronnashor_r_fall`（大表，放在落点的地面上，不跟随，z 2；画面最下面是地面；左右对称） | 24 × 52 |
| `baronnashor_fx_p_tent` | view_effects `tft_baronnashor_p_tent`（大表，放在被选中的人脚下的地面上，不跟随，z 2；画面最下面是地面；左右对称） | 28 × 60 |
| `baronnashor_icon_skill` | skill_icons[0] `asset/tft/icons/tft_baronnashor_skill` | 64 × 64 |
| `baronnashor_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_baronnashor_skill2` | 64 × 64 |
| `baronnashor_icon_ult` | skill_icons[2] `asset/tft/icons/tft_baronnashor_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_baronnashor_fx`（小的）和 `tft_baronnashor_big`（q_spray、e_burst、r_spikes、r_fall、p_tent），tag = 名字。
- q_spray 断言上下对称（朝右），其余断言左右对称。
- e_burst、r_spikes 放在地面上（不跟随，z -1）；r_fall、p_tent 放在落点（不跟随，p_tent 由 tft.dll 播）；q_acid 是敌人身上的 buff；q_spray 是直线弹道（从嘴里喷出）。钻地时的 `dig` 帧（只露鳍刺）是精灵帧，不是特效。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
