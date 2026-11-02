# 暗影狼：给 Codex 的特效提示词（第 3 步）

> **这一份是 9 张特效图 + 3 个技能图标。** 造型已定，见 `design/murkwolf_design.png`：
>   - 3/4 朝右、四条腿压低身子的**双头狼**，灰蓝色的毛；
>   - 背上紫色鬃毛和一排墨绿尖刺，蓬松的大尾巴往左上方翘；
>   - 两个狼头并排，青色发光的眼睛、粉色大嘴、奶黄色尖牙、白色腮毛；
>   - 黑色弯钩爪。
>
> 暗影狼在游戏里是**高清**的（每个游戏格子里约 1.67×1.67 个细像素），36 格高、50 格宽（高×宽）。**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/murkwolf_size.png`：暗影狼缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是纳亚菲利（尖牙、猎犬）、莎弥拉和沃利贝尔（爪痕、地裂）、沃里克（火星、烟）的特效贴图。这些是**灰色的形状，游戏里再染色**，已经按用在我们哪张特效分好了行。只在本地用。
> - **暗影狼是峡谷里的野狼，特效都是它的味道**：爪痕、咬痕、奶白色尖牙、粉红色的伤口、像它眼睛一样的青色闪光、紫黑色的暗影烟。不要符文魔法、不要闪电、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、烟、尘土没有黑描边**；尖牙和小狼可以有深色描边。
> - **围着它的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住它。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。`r_pack` 的两只小狼**正面朝着我们**，所以左右对称也自然。
> - 交付方式：
>   - 每张生成后按格子取回（每格取多数颜色）。
>   - 交付 8 倍的 `murkwolf_fx_<名字>.png`，和原尺寸的 `pixel_1x/`：严格按格子取色、透明度只有 0 和 255、逐格对称。Claude 直接用 `pixel_1x/` 切格导入。
>   - 图标交付 `murkwolf_icon_<名字>.png`（64×64）。
>   - 另附 `manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`。
>   - 都放在 `outputs/murkwolf_fx/` 里。**最后**写 `HANDOFF.md`，再打包成 `outputs/murkwolf_fx_pack_done.zip`。
>   - **请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「双头撕咬」 | 两个头一起咬 | `a_hit` |
| 被动「灰霸符」 | 血越少暴击越高，技能也能暴击 | `p_hit`（技能暴击时） |
| 技能 1 =「撕裂之爪」 | 跳到附近血最少的敌人身边撕一口，之后 3 次攻击加攻速、多打伤害 | `q_land` · `q_hit` · `q_emp` |
| 技能 2 =「狂战士之嚎」 | 仰头长嚎，5 秒吸血、伤害提高，对残血更高 | `e_howl` |
| 大招 =「狼群攻击」 | 叫来两只小暗影狼，先扑向目标，之后它每次攻击小狼跟着咬两口 | `r_pack` · `r_hit` · `r_bite` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**（尖牙、小狼可以有深色描边）。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 暗影紫（鬃毛、暗影烟）：`#C9B8F0`、`#8E70D0`、`#5C4399`、`#36255E`、`#1A1030`；
  - 青光（眼睛、爪光）：`#F0FFFF`、`#9CF5FF`、`#36D6F2`、`#1690B8`、`#0C4E70`；
  - 尖牙奶黄：`#FFFCEB`、`#F7E9AE`、`#DCC062`、`#9E812F`；
  - 伤口粉红（嘴、撕开的伤口）：`#FFD6E6`、`#F57FB4`、`#D63F78`、`#8C1F46`、`#4A0E26`；
  - 灰蓝毛（小狼）：`#DCE4F5`、`#9AA9D1`、`#6A78A8`、`#444E78`、`#262B47`；
- 打中的画面居中画，不旋转；地面上的尘土是从斜上方看的扁平一团。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（9 张）

9 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `murkwolf_fx_a_hit.png`：普攻「双头撕咬」：咬中，4 帧

两个头一口咬下：**上下两排奶白色尖牙**一下合拢，中间一闪粉红色，两边崩出两点粉色血星。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fang cream ramp (#FFFCEB, #F7E9AE, #DCC062, #9E812F), a gash pink-crimson ramp (#FFD6E6, #F57FB4, #D63F78, #8C1F46, #4A0E26).
Effect: A SNAPPING BITE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two curved rows of cream FANGS (an upper row pointing down and a lower row pointing up, each 10 squares wide with 4 sharp teeth) wide apart, top and bottom of the cell; 2 the rows snapping shut in the middle, a pink-white flash 6 squares across where they meet; 3 the fangs gone, a pink-crimson burst 10 squares across with two pink droplets flying out to both sides (mirrored); 4 the droplets falling, one on each side. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `murkwolf_fx_q_land.png`：技能 1「撕裂之爪」：落地的尘土，5 帧

它扑落的地面：**一圈紫黑色的暗影尘土往两边炸开**，地上裂开几道短裂缝，透出青色微光。**只在地面和低处**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a murk purple ramp (#C9B8F0, #8E70D0, #5C4399, #36255E, #1A1030), a cyan glow ramp (#F0FFFF, #9CF5FF, #36D6F2, #1690B8, #0C4E70).
Effect: A POUNCE LANDING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND and low above it, seen from above at a slant: 1 a flat dark purple murk puff 14 squares wide at the bottom middle; 2 two murk clouds bursting out to both sides (mirrored), 34 squares wide and 8 tall, three short jagged ground CRACKS under them glowing cyan; 3 the clouds 42 squares wide and thinner, the cracks' glow fading; 4 the murk settling low; 5 the last wisps on each side. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 5 equal 44:12 cells, image size 3520x192 (each cell 704x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `murkwolf_fx_q_hit.png`：技能 1「撕裂之爪」：撕裂，5 帧

撕裂之爪抓中：**两组三道爪痕交叉成 X**（左上往右下三道、右上往左下三道），爪痕边缘青白色、里面是粉红色的伤口，周围一圈紫色暗影。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan glow ramp (#F0FFFF, #9CF5FF, #36D6F2, #1690B8, #0C4E70), a gash pink-crimson ramp (#FFD6E6, #F57FB4, #D63F78, #8C1F46, #4A0E26), a murk purple ramp (#C9B8F0, #8E70D0, #5C4399, #36255E, #1A1030).
Effect: A RENDING CLAW X, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a cyan-white flash 6 squares across; 2 TWO SETS OF THREE parallel CLAW GASHES crossing in a big X 16 squares across (three from the upper left down to the lower right and the mirror three from the upper right), each gash near-white and cyan along its edges with a hot pink-crimson core; 3 the gashes at full length, dark purple murk wisps puffing out at the four tips; 4 the gashes fading to pink-crimson, a few pink droplets; 5 the last murk wisps. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 5 equal 20:18 cells, image size 1600x288 (each cell 320x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `murkwolf_fx_p_hit.png`：被动「灰霸符」：技能暴击，4 帧

技能暴击：**一个锋利的银白色四角星**一闪，星芯青色，外面一圈锯齿状的灰紫色尖刺往外扎。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan glow ramp (#F0FFFF, #9CF5FF, #36D6F2, #1690B8, #0C4E70), a murk purple ramp (#C9B8F0, #8E70D0, #5C4399, #36255E, #1A1030).
Effect: A CRITICAL STRIKE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a tiny near-white point; 2 a sharp silver-white FOUR-POINT STAR 14 squares across with a cyan core, a ring of eight short jagged grey-purple spikes round it; 3 the star shrinking, the spikes flying outward; 4 four small cyan sparks at the corners. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `murkwolf_fx_r_hit.png`：大招「狼群攻击」：小狼扑中，5 帧

两只小狼从两边扑上来：**左右各一道弯弯的爪痕**向中间划过，中间一团紫色暗影炸开，两点青色眼光一闪。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan glow ramp (#F0FFFF, #9CF5FF, #36D6F2, #1690B8, #0C4E70), a gash pink-crimson ramp (#FFD6E6, #F57FB4, #D63F78, #8C1F46, #4A0E26), a murk purple ramp (#C9B8F0, #8E70D0, #5C4399, #36255E, #1A1030).
Effect: A PACK POUNCE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two cyan eye glints (2x1 squares) at the left and right edges; 2 from each side a curved claw swipe of two parallel gashes sweeping in toward the middle (mirrored), cyan-white edges, pink-crimson cores, 9 squares long; 3 the swipes meeting, a dark purple murk burst 12 squares across in the middle; 4 the murk spreading and thinning, pink droplets; 5 the last wisps. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 5 equal 22:16 cells, image size 1760x256 (each cell 352x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `murkwolf_fx_r_bite.png`：大招「狼群攻击」：小狼咬一口，4 帧

小狼咬一口：**一对小小的奶白色尖牙**一下合拢，一点粉红色。比普攻的小。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fang cream ramp (#FFFCEB, #F7E9AE, #DCC062, #9E812F), a gash pink-crimson ramp (#FFD6E6, #F57FB4, #D63F78, #8C1F46, #4A0E26).
Effect: A SMALL NIP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two tiny rows of cream fangs (6 squares wide, 3 teeth each) apart; 2 snapping shut; 3 a small pink burst 6 squares across; 4 one pink droplet on each side. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `murkwolf_fx_q_emp.png`：技能 1「撕裂之爪」：强化攻击，6 帧循环

撕裂之爪后面三次攻击被强化（攻速加快）：它**脚下两边各一道青白色的爪光**一闪一闪，身子轮廓外面几点青色小火星和短短的速度线往后掠。**它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan glow ramp (#F0FFFF, #9CF5FF, #36D6F2, #1690B8, #0C4E70), a murk purple ramp (#C9B8F0, #8E70D0, #5C4399, #36255E, #1A1030).
Effect: SHARPENED CLAWS, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the wolf stands in the middle, not drawn: about 50 squares wide and 36 tall, a crouched four-legged TWO-HEADED wolf, its two heads at the right, its bushy tail up at the upper left, its feet on the bottom line of the cell: at the bottom on EACH side (mirrored), where its front and hind paws touch the ground, three short bright cyan-white CLAW GLINTS (thin slanted lines 4 squares long); a few small cyan sparks (1x1 and 2x2 squares) blinking just outside its outline, two short cyan speed streaks on each side sweeping up and outward; frames 1-6 the glints flashing in turn and the sparks blinking (every frame left-right symmetric). The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 60:40 cells, image size 5760x640 (each cell 960x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `murkwolf_fx_e_howl.png`：技能 2「狂战士之嚎」：嚎叫之后，6 帧循环

狂战士之嚎（吸血、伤害提高）：它身子两侧**紫黑色的暗影烟往上蹿**，烟里飘着粉红色的小火星，头顶一圈淡淡的粉红色光边。**它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a murk purple ramp (#C9B8F0, #8E70D0, #5C4399, #36255E, #1A1030), a gash pink-crimson ramp (#FFD6E6, #F57FB4, #D63F78, #8C1F46, #4A0E26).
Effect: A BERSERK AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the wolf stands in the middle, not drawn: about 50 squares wide and 36 tall, a crouched four-legged TWO-HEADED wolf, its two heads at the right, its bushy tail up at the upper left, its feet on the bottom line of the cell: on EACH side of its body (mirrored) tongues of DARK PURPLE MURK SMOKE licking up along its outline from the ground to above its back, small hot pink-crimson embers rising through the smoke, a thin pink-red rim glow along the top edge above it; frames 1-6 the smoke tongues rising and curling, the embers drifting up (every frame left-right symmetric). The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 64:48 cells, image size 6144x768 (each cell 1024x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `murkwolf_fx_r_pack.png`：大招「狼群攻击」：身边的两只小暗影狼，6 帧循环

狼群攻击：**两只小暗影狼**站在它身体左右两边的地上。小狼是峡谷里的小狼、**只有一个头**、**正面朝着我们**：灰蓝色的毛、背上一小撮紫色鬃毛、尖耳朵、两只发光的青色眼睛、龇着牙伸着粉色舌头，约 14 格宽、13 格高。轮流低吼、喘气、往前一顿。**中间它的身体位置留空**（小狼画在它后面一层）。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a slate-blue fur ramp (#DCE4F5, #9AA9D1, #6A78A8, #444E78, #262B47), a murk purple ramp (#C9B8F0, #8E70D0, #5C4399, #36255E, #1A1030), a cyan glow ramp (#F0FFFF, #9CF5FF, #36D6F2, #1690B8, #0C4E70), a gash pink-crimson ramp (#FFD6E6, #F57FB4, #D63F78, #8C1F46, #4A0E26).
Effect: THE PACK, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the wolf stands in the middle, not drawn: about 50 squares wide and 36 tall, a crouched four-legged TWO-HEADED wolf, its two heads at the right, its bushy tail up at the upper left, its feet on the bottom line of the cell: TWO WOLF PUPS (little one-headed murk wolves, each about 14 squares wide and 13 tall, seen FROM THE FRONT facing us so they read the same both ways: slate-blue fur with a lighter chest, a small tuft of DARK PURPLE MANE on the back of the neck, two upright pointed ears with pink insides, two glowing CYAN eyes, a snarling mouth with tiny cream fangs and a pink tongue, four short legs with black claws) placed mirrored: one pup standing on the bottom line on EACH side just outside its outline; frames 1-6 the pups growling, panting and lunging one square forward in turn, a small murk wisp at their paws, every frame left-right symmetric. The middle of the cell (its body) stays EMPTY. everything is a WILD RIFT MURK WOLF's: sharp CLAW SLASHES and BITE MARKS with cream fangs, hot pink-crimson gashes, glowing CYAN glints like its eyes, DARK PURPLE MURK smoke; flat shades, crisp blocky shapes; no magic runes, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 100:40 cells, image size 9600x640 (each cell 1600x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `murkwolf_icon_skill.png`：技能 1「撕裂之爪」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little cyan corner studs, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a slate-blue two-headed wolf leaping toward the upper right, both mouths open, its front claws spread, three cyan-white claw gashes slashing across the corner in front of it. No text, no letters.
```

### 图标 2. `murkwolf_icon_skill2.png`：技能 2「狂战士之嚎」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little cyan corner studs, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: two slate-blue wolf heads side by side with white cheek ruffs, muzzles thrown up to the sky howling, glowing cyan eyes, dark purple murk smoke and pink embers rising round them. No text, no letters.
```

### 图标 3. `murkwolf_icon_ult.png`：大招「狼群攻击」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark slate frame with little cyan corner studs, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big two-headed slate-blue wolf with a purple mane snarling at the back, two small one-headed wolf pups with glowing cyan eyes lunging forward in front of it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `murkwolf_fx_a_hit` | view_effects `tft_murkwolf_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `murkwolf_fx_q_land` | view_effects `tft_murkwolf_q_land`（放在它落地的地面上，不跟随，z -1；左右对称） | 44 × 12 |
| `murkwolf_fx_q_hit` | view_effects `tft_murkwolf_q_hit`（跟随目标，z 2；左右对称） | 20 × 18 |
| `murkwolf_fx_p_hit` | view_effects `tft_murkwolf_p_hit`（跟随目标，z 3；左右对称） | 16 × 16 |
| `murkwolf_fx_r_hit` | view_effects `tft_murkwolf_r_hit`（跟随目标，z 2；左右对称） | 22 × 16 |
| `murkwolf_fx_r_bite` | view_effects `tft_murkwolf_r_bite`（跟随目标，z 2；左右对称） | 10 × 10 |
| `murkwolf_fx_q_emp` | view_buffs `tft_murkwolf_q_emp`（跟随它，z 3；左右对称） | 60 × 40 |
| `murkwolf_fx_e_howl` | view_buffs `tft_murkwolf_e_howl`（跟随它，z 3；左右对称） | 64 × 48 |
| `murkwolf_fx_r_pack` | view_buffs `tft_murkwolf_r_pack`（大表，跟随它，z -1；左右对称） | 100 × 40 |
| `murkwolf_icon_skill` | skill_icons[0] `asset/tft/icons/tft_murkwolf_skill` | 64 × 64 |
| `murkwolf_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_murkwolf_skill2` | 64 × 64 |
| `murkwolf_icon_ult` | skill_icons[2] `asset/tft/icons/tft_murkwolf_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_murkwolf_fx`（小的）和 `tft_murkwolf_big`（r_pack），tag = 名字。
- 全部断言左右对称。
- a_hit、q_hit、r_hit、r_bite、p_hit 在被打中的人身上（tft.dll 放 q_land、q_hit、r_hit、r_bite、p_hit）；q_land 放在它落地的地面上（不跟随，z -1）；q_emp、e_howl 是它身上的 buff；r_pack 是大表上的 buff（z -1，小狼在它后面一层）。
- 用 `pixel_1x/` 切格（import_raptor_fx 的做法，改成 import_murkwolf_fx）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
