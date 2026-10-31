# 绯红印记树怪：给 Codex 的特效提示词（第 3 步）

> **这一份是 9 张特效图 + 3 个技能图标。** 造型已定（`design/brambleback_design.png`：3/4 朝右、四肢着地弓背蹲着的深红褐树皮巨兽：两条长前臂、三根红橙大爪；脖子上一圈绿叶领子；背上弯曲的深色树枝和发光的红橙核心；楔子形树皮脑袋低在领子下，两只红眼、额头橙色螺旋；树皮上发光的红色裂纹）。树怪在游戏里是**高清**的（每个游戏格子里约 1.7×1.7 个细像素），40 格高、62 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/brambleback_size.png`：树怪缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是峡谷红 buff 自己（爪痕、红霸符的火光）、狼人（爪击、恐惧波纹）、布兰德（火焰）和内瑟斯（光环）的特效贴图（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **树怪是峡谷的红 buff 野兽，特效都是它的味道**：猩红到橙色的火焰和火星、发光的红色爪痕、深红褐的碎树皮和带刺的荆棘藤、被扯下来的绿叶；不要闪电、不要蓝色、不要光滑的霓虹光束。
> - **特效要亮**：每个火光和爪痕都有最亮一档的黄白色芯，暗底上一眼能看见。**火焰、爪痕、冲击环没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `brambleback_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `brambleback_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/brambleback_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/brambleback_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「荆爪横扫」 | 一只大爪举起往前往下横扫 | `a_hit` |
| 被动「红霸符」 | 普攻让目标灼烧（按最大生命的真实伤害），自己回血；杀了人自动扑向下一个敌人 | `p_burn` · `q_hit` |
| 技能 1 =「荆棘飞扑」 | 跃起扑到目标身上，物理伤害并减速 | `q_hit` · `q_slow` |
| 技能 2 =「绯红咆哮」 | 人立怒吼，周围敌人减速、攻击力降低，自己受到的伤害降低 | `e_cast` · `e_slow` · `e_guard` |
| 大招 =「猩红之怒」 | 全身红纹烧起来狂暴：攻击力、攻速大涨，无视一部分护甲 | `r_cast` · `r_fury` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 猩红火焰（它发光的红纹、红核和爪子）：`#FFF6C8`、`#FFD23A`、`#FF8A1E`、`#E8361A`、`#9E1410`、`#5A0A0C`；
  - 树皮（深红褐）：`#C9925C`、`#9B6741`、`#6E4430`、`#42271D`、`#24140F`；
  - 树叶：`#B8DC6A`、`#72AE45`、`#3F7A36`、`#24492A`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（9 张）

9 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `brambleback_fx_a_hit.png`：普攻「荆爪横扫」：爪击，4 帧

大爪抓中：**三道红橙色的爪痕**（中间一道竖的，两边两道往外斜，像爪子从上往下抓过），一下火星和几片碎树皮往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a bark ramp (#C9925C, #9B6741, #6E4430, #42271D, #24140F).
Effect: A CLAW RAKE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small hot yellow-white flash 5 squares across; 2 THREE glowing red-orange CLAW MARKS raked from top to bottom, 12 squares tall - the middle one straight down, the two outer ones leaning outward (mirrored) - each 2 squares thick with a near-white core, a few embers flying out to both sides; 3 the marks fading to dark red from the top, small bark chips and embers falling outward; 4 the last faint marks and one falling ember on each side. everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:16 cells, image size 1152x256 (each cell 288x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `brambleback_fx_q_hit.png`：技能 1「荆棘飞扑」：扑落冲击，6 帧

扑落砸中：被扑中的人脚下**一圈红橙色的冲击**（从斜上方看的扁椭圆），两边各三道爪痕往外划开，碎树皮、火星和几片绿叶往两边飞。**人站的地方留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a bark ramp (#C9925C, #9B6741, #6E4430, #42271D, #24140F), a leaf ramp (#B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A POUNCE IMPACT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn, low on the ground at its feet: 1 a bright yellow-white flash at the feet, 10 squares wide; 2 a flat ring of red-orange impact (an ellipse 26 squares wide, 8 tall) and on EACH side three short glowing CLAW MARKS raking outward along the ground (mirrored); 3 the ring 36 squares wide, bark chips, embers and two or three GREEN LEAVES flying out to both sides; 4 the ring thinning, chips falling; 5 the claw marks fading to dark red, a little dust; 6 the last embers. The middle (its body) stays EMPTY. everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 6 equal 40:24 cells, image size 3840x384 (each cell 640x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `brambleback_fx_q_slow.png`：技能 1「荆棘飞扑」：减速，6 帧循环

被减速的人：脚边**几根带红刺的荆棘藤缠着脚踝**，藤上冒一点红光，像脚被荆棘绊住。很淡、只在脚下。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark ramp (#C9925C, #9B6741, #6E4430, #42271D, #24140F), a leaf ramp (#B8DC6A, #72AE45, #3F7A36, #24492A), a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: BRAMBLE SNARE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low round a unit's feet only (the unit not drawn): on EACH side (mirrored) two thorny dark bark-brown BRAMBLE VINES curling round the ankle line, small red thorns on them, one tiny green leaf, a faint red glint; frames 1-6 the vines tightening and loosening a square and the glints moving (every frame left-right symmetric). Subtle. everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 6 equal 24:8 cells, image size 2304x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `brambleback_fx_e_cast.png`：技能 2「绯红咆哮」：怒吼声波，5 帧

它人立起来怒吼：身体两侧**一层层红色的声波弧线**往外推开（像括号一样的弧，左右各三层），被吹起的绿叶和火星往外飞。**它的身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a leaf ramp (#B8DC6A, #72AE45, #3F7A36, #24492A).
Effect: A ROAR SHOCKWAVE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the beast crouches in the middle, not drawn: about 61 squares wide and 40 tall, on all fours, its long arms and claws in front, its wedge head low at the right: 1 a short red flash at the upper right and upper left edges (mirrored); 2 on EACH side two curved crimson SOUND-WAVE ARCS like big brackets, 3 squares thick, bright orange cores, pushed out from the body's edges; 3 three arcs on each side, the outer ones near the cell's edges, green leaves and embers blown outward; 4 the arcs fading to dark red and breaking into short dashes, leaves still flying; 5 the last dashes and two leaves at the edges. The middle of the cell (its body) stays EMPTY. everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 5 equal 72:48 cells, image size 5760x768 (each cell 1152x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `brambleback_fx_e_slow.png`：技能 2「绯红咆哮」：被吼得减速减攻，6 帧循环

被吼过的人头顶：**一个暗红色的三道爪痕印记**（圆形，里面三道往下的爪痕，表示被吓得变弱），一跳一跳地发光。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C), a bark ramp (#C9925C, #9B6741, #6E4430, #42271D, #24140F).
Effect: A FEAR MARK, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): above a unit's head: a round dark bark-brown disc 10 squares across with THREE glowing red CLAW SCRATCHES cut down through it (the middle straight, the outer two leaning out), a thin red ring round the disc; frames 1-6 the scratches pulsing brighter and dimmer and the disc bobbing one square up and down. everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 6 equal square cells, image size 1152x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `brambleback_fx_e_guard.png`：技能 2「绯红咆哮」：树皮护体（减伤），6 帧循环

它减伤的时候：身子外面**一圈厚树皮甲片和带刺的荆棘藤**围成的护壳（横着的椭圆，只画外圈），甲片缝里透红光，几片绿叶挂在上面。**里面它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark ramp (#C9925C, #9B6741, #6E4430, #42271D, #24140F), a leaf ramp (#B8DC6A, #72AE45, #3F7A36, #24492A), a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A BARK AND BRAMBLE GUARD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the beast crouches in the middle, not drawn: about 61 squares wide and 40 tall, on all fours, its long arms and claws in front, its wedge head low at the right: a ring of THICK BARK PLATES and THORNY BRAMBLE VINES (a wide ellipse 70 squares wide and 46 tall, only its 3-square rim drawn), dark reddish-brown plates with glowing red seams, red thorns on the vines, a few green leaves on it; frames 1-6 the red seams lighting up in turn round the ring (mirrored pairs) and the thorns twitching (every frame left-right symmetric). INSIDE the ring stays EMPTY (its body). everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 6 equal 74:50 cells, image size 7104x800 (each cell 1184x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `brambleback_fx_r_cast.png`：大招「猩红之怒」：狂暴爆发，6 帧

它开大的一下：从它背上的红核和全身**猛地爆出一圈猩红的火焰**往上往外冲，火星四溅，地面上一圈火光。**它的身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A CRIMSON FURY BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the beast crouches in the middle, not drawn: about 61 squares wide and 40 tall, on all fours, its long arms and claws in front, its wedge head low at the right: 1 a hot yellow-white flash at the top of its back (where its red core is); 2 a ring of crimson-orange FLAMES bursting up all round the body's edges, tallest at the top, a flat ring of fire light on the ground under it (an ellipse 60 squares wide, 10 tall); 3 the flames at their tallest (the top flames 14 squares tall), embers flying out to both sides (mirrored); 4 the flames sinking to the edges, embers rising; 5 small flames and the ground glow fading; 6 the last rising embers. The middle (its body) stays EMPTY. everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 6 equal 76:56 cells, image size 7296x896 (each cell 1216x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `brambleback_fx_r_fury.png`：大招「猩红之怒」：狂暴火焰，6 帧循环

它狂暴期间：**猩红的火苗沿着身子两侧和背上往上舔**，一颗颗火星往上飘，像全身的红纹烧起来了。不要太满，只在身体边缘。**它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A FURY BLAZE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the beast crouches in the middle, not drawn: about 61 squares wide and 40 tall, on all fours, its long arms and claws in front, its wedge head low at the right: small crimson-orange FLAME TONGUES licking up along the edges of its body - both sides and above its back (mirrored), each 4-8 squares tall with a yellow core - and single embers rising above it; frames 1-6 the flames flickering up and down in turn and the embers rising a few squares a frame (every frame left-right symmetric). Only at the body's edges, never over it. INSIDE stays EMPTY (its body). everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 6 equal 70:54 cells, image size 6720x864 (each cell 1120x864, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `brambleback_fx_p_burn.png`：被动「红霸符」：灼烧，6 帧循环

被红霸符烧着的人：身体两侧下半身**几簇小小的红橙火苗**往上窜，几颗火星往上飘（像英雄联盟里红 buff 的灼烧）。很小，不要盖住人。**人站的地方留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson fire ramp (#FFF6C8, #FFD23A, #FF8A1E, #E8361A, #9E1410, #5A0A0C).
Effect: A RED BUFF BURN, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round an upright champion 16 squares wide and 30 tall stands in the middle, not drawn: on EACH side of its lower body (mirrored) two small crimson-orange FLAME TONGUES 3-6 squares tall with yellow cores, and two or three single embers rising beside its body; frames 1-6 the flames flickering up and down in turn and the embers rising (every frame left-right symmetric). Small; the middle (its body) stays EMPTY. everything is a RED BUFF BEAST's power: crimson-orange flames and embers, glowing red claw marks, dark reddish-brown bark chips and thorny bramble vines, green leaves torn loose; flat shades, crisp blocky shapes; no lightning, no blue, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:26 cells, image size 1920x416 (each cell 320x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `brambleback_icon_skill.png`：技能 1「荆棘飞扑」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bark-brown frame with little red ember corners, a deep red-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a huge dark bark-brown arm with three big red-orange claws lunging down from the upper left toward the lower right, three glowing red claw streaks behind it, a few green leaves. No text, no letters.
```

### 图标 2. `brambleback_icon_skill2.png`：技能 2「绯红咆哮」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bark-brown frame with little red ember corners, a deep red-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: the beast's wedge-shaped bark head roaring, seen from the side facing right, two red eyes, under a green leaf collar, three curved crimson sound-wave arcs coming out in front of it. No text, no letters.
```

### 图标 3. `brambleback_icon_ult.png`：大招「猩红之怒」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark bark-brown frame with little red ember corners, a deep red-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big red-orange claw raised and wreathed in crimson flames, a glowing red-orange ember core behind it, embers flying up. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `brambleback_fx_a_hit` | view_effects `tft_brambleback_a_hit`（跟随目标，z 2；左右对称） | 18 × 16 |
| `brambleback_fx_q_hit` | view_effects `tft_brambleback_q_hit`（跟随被扑中的人，z 3；左右对称；tft.dll 的「扑向下一个」落地时也用） | 40 × 24 |
| `brambleback_fx_q_slow` | view_buffs `tft_brambleback_q_slow`（跟随被减速的人，脚下，z 3；左右对称） | 24 × 8 |
| `brambleback_fx_e_cast` | view_effects `tft_brambleback_e_cast`（大表，跟随它，z 3；左右对称） | 72 × 48 |
| `brambleback_fx_e_slow` | view_buffs `tft_brambleback_e_slow`（跟随被吼的人，头顶上方，z 3；左右对称） | 12 × 12 |
| `brambleback_fx_e_guard` | view_buffs `tft_brambleback_e_guard`（大表，跟随它，z 3；左右对称） | 74 × 50 |
| `brambleback_fx_r_cast` | view_effects `tft_brambleback_r_cast`（大表，跟随它，z 3；左右对称） | 76 × 56 |
| `brambleback_fx_r_fury` | view_buffs `tft_brambleback_r_fury`（大表，跟随它，z 3；左右对称） | 70 × 54 |
| `brambleback_fx_p_burn` | view_buffs `tft_brambleback_p_burn`（跟随被烧的人，z 4；左右对称；tft.dll 给） | 20 × 26 |
| `brambleback_icon_skill` | skill_icons[0] `asset/tft/icons/tft_brambleback_skill` | 64 × 64 |
| `brambleback_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_brambleback_skill2` | 64 × 64 |
| `brambleback_icon_ult` | skill_icons[2] `asset/tft/icons/tft_brambleback_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_brambleback_fx`（小的）和 `tft_brambleback_big`（e_cast、e_guard、r_cast、r_fury），tag = 名字。
- 全部断言左右对称。
- a_hit 跟随目标；q_hit 跟随被扑中的人（tft.dll 的「扑向下一个」落地时也用 play_view_effect 放它）；e_cast、r_cast 是它身上的 caster 画面；e_guard、r_fury 是它身上的 buff；q_slow、e_slow 是敌人身上的 buff；p_burn 是 tft.dll 给被烧的人挂的 buff。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
