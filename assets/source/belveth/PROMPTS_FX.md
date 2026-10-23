# 虚空女皇 卑尔维斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型已定（`design/belveth_design.png`：深紫色的脸、两只发光的品红眼睛、头顶品红的冠，两肩高高的深紫长刺，两只收拢像斗篷一样的深灰青膜翼，下面粉紫色的爪子，左边拖在地上的长尾巴）。她在游戏里是**高清**的（每个游戏格子里约 1.75×1.75 个细像素），47 格高、50 格宽（高×宽，连肩刺和尾巴）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/belveth_size.png`：卑尔维斯放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卑尔维斯自己的特效贴图（大多是灰度的形状），按用在我们哪张特效分好了行，只在本地用。**卑尔维斯是虚空女皇**：她的力量是**锋利的淡紫 / 紫色虚空能量**（月牙刀光、尖尖的碎片，边缘品红，中心近白），吞下的是**粉紫色的虚空珊瑚**，旋风里夹着**青白色的海水泡沫**（她从海底来）；不要火、不要电、不要光滑的霓虹光束。
> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。
> - **能量、刀光、冲击波、水花、尘土都没有黑描边**（用它自己最深的一档）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`w_tail`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - **持续的画面**（真身光 15 秒、刀光风暴 1.5 秒、减速、攻速）只画几帧循环，Claude 导入时按时长拉开循环。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `belveth_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/belveth_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/belveth_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 用膜翼像刀一样劈砍，打得很快 | `a_hit` |
| 被动「溶烛化紫」 | 每放一个技能攻速变快几秒；击杀英雄叠永久攻速、吃掉虚空珊瑚 | `p_as` · `c_eat` |
| 技能 1 =「虚空激流」 | 朝目标冲过去，穿过的敌人都受伤 | `q_dash` · `q_hit` |
| 技能 2 =「上觐沉渊」 | 尾巴砸地，一道地裂沿直线往前冲，打中的敌人被击飞、减速 | `w_slam` · `w_tail` · `w_hit` · `slow` |
| 大招 =「万载豪筵」 | 吞下虚空珊瑚爆开（伤害、减速），化为真身 15 秒（生命、攻击距离、攻速、移速变高） | `r_burst` · `r_hit` · `r_aura` · `slow` |
| 真身里的「搠面皇锋」 | 被围住时原地化成刀光风暴：减伤、吸血，斩最近被打的敌人 | `e_storm` · `e_hit` |

连招：**尾巴击飞英雄 → 立刻再冲一次**，**冲过英雄 → 马上甩尾**，**敌方英雄阵亡 → 吃珊瑚**（真身续上或大招冷却缩短），**真身期间冲得更远更快**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**能量、刀光、冲击波、水花、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的亮点。
- 颜色（按每条写的用）：
  - 虚空·淡紫到深紫：`#FBE8FF`、`#E8B4FF`、`#C47CF4`、`#9248D8`、`#5E26A0`、`#321258`；
  - 品红：`#FFE0F6`、`#FF8AE2`、`#EE36C4`、`#B0188E`、`#6A0C58`；
  - 虚空珊瑚·粉紫：`#FFE8F4`、`#F6B4DA`、`#DA7CBE`、`#A44C96`、`#622C60`；
  - 海水泡沫·青白：`#E8FFFC`、`#A8E8E8`、`#5CB4C4`、`#2E7088`；
  - 闪光·白紫：`#FFFFFF`、`#FCF2FF`、`#EED2FF`；
  - 尘土·紫灰：`#E2DCEA`、`#B2A8C4`、`#807496`、`#4E4462`；
- 打中、爆发居中画，不旋转；地面上的东西（冲击波、地裂、脚下的光圈和水纹）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `belveth_fx_a_hit.png`：普攻：翼刃劈中，3 帧

膜翼像刀一样劈中敌人（参考 ba_attacklead、hitflash_core、tar_spark）：中间一下白紫色的闪光，一个 **X 形的两道淡紫色刀痕**交叉划过，边上溅开几颗品红的火星。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF), a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58).
Effect: A BLADE STRIKE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-lilac flash 6 squares across; 2 two sharp lavender crescent cuts crossing in an X 13 across, magenta edges, a few magenta sparks flying out at mirrored places; 3 the cuts thinner and dimmer, the sparks further out, fading. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `belveth_fx_p_as.png`：溶烛化紫：放技能后攻速变快，脚下的紫色气流，4 帧循环

放完技能攻速变快的那几秒：她脚下**两缕淡紫色的气流**往两边打旋，几片小小的薰衣草色光点往上飘。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58).
Effect: A LAVENDER FRENZY, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two thin lavender swirls curling out from under her to both sides on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 28 wide, three small lilac motes rising at mirrored places; the swirls turn and the motes rise frame to frame so the loop flows. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 30:10 cells, image size 1920x160 (each cell 480x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `belveth_fx_q_dash.png`：虚空激流：起步的地方，4 帧

虚空激流（参考 q_dashnoise、q_trail_soft、q_lightning_flipbook）：她猛地冲出去的地方，**地上一圈紫色的虚空能量炸开**，几道尖尖的紫色碎片和品红的电弧往两边甩出去。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58), a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF).
Effect: A VOID LAUNCH ON THE GROUND, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-lilac flash 10 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 a violet ring bursting out 26 wide with sharp lavender shards thrown out to both sides; 3 the ring 32 wide, thin magenta arcs at its ends at mirrored places; 4 the ring breaking into fading shards. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 34:14 cells, image size 2176x224 (each cell 544x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `belveth_fx_q_hit.png`：虚空激流：穿过时打中，3 帧

冲过去时打中的敌人：一道**横着的白紫色刀光**从中间划过（左右对称：两头一样尖），上下各崩出几片紫色碎片。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF), a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58).
Effect: A PASSING CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-lilac horizontal slash 16 squares long, pointed at both ends, through the middle; 2 the slash wider with magenta edges, violet shards bursting up and down at mirrored places; 3 the shards drifting out, fading. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal 18:16 cells, image size 864x256 (each cell 288x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `belveth_fx_w_tail.png`：上觐沉渊：沿直线往前冲的地裂，4 帧循环

尾巴砸地后沿着一条直线往前冲的冲击（参考 w_rift、w_impactspike、w_ring_shockwave）：一道**紫色的地裂波**往前推，前头翻起几根尖尖的紫色岩刺，后面拖一条品红的光。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58), a lilac-grey dust ramp (#E2DCEA, #B2A8C4, #807496, #4E4462).
Effect: A RIFT WAVE, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a surging violet rift 20 squares long, its front a cluster of sharp lavender spikes bursting up and down equally from the middle line, a magenta glow and lilac-grey rock bits trailing behind on the left; the spikes rise and fall in turn so the loop surges. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 22:10 cells, image size 1408x160 (each cell 352x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `belveth_fx_w_slam.png`：上觐沉渊：尾巴砸地，5 帧

上觐沉渊（参考 w_splash、w_basetexture、w_ring_shockwave、medrock）：尾巴砸在地上，**地面裂开一圈紫色的冲击波**，几块岩石和紫色的水花往两边溅起来。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58), a lilac-grey dust ramp (#E2DCEA, #B2A8C4, #807496, #4E4462), a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF).
Effect: A TAIL SLAM ON THE GROUND, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-lilac impact flash 16 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 the ground cracking in violet lines and a shock ring 36 wide, lavender splashes bursting up at both sides; 3 the ring 46 wide, lilac-grey rock chunks flying up at mirrored places; 4 the rocks falling, the cracks glowing magenta; 5 the cracks and the ring fading. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 5 equal 48:20 cells, image size 3840x320 (each cell 768x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `belveth_fx_w_hit.png`：上觐沉渊：被击飞，4 帧

被尾巴砸中击飞的敌人（参考 w_impactspike、w_comet）：脚下**一股紫色的能量往上喷**，把人顶起来，几根尖尖的紫色碎片往上飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58), a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF).
Effect: A LAUNCH FROM BELOW, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a violet burst on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 12 wide; 2 a column of lavender energy shooting up through the target 24 squares tall with sharp shards rising at mirrored places; 3 the column thinning, the shards high; 4 a few shards and sparkles falling, fading. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 18:26 cells, image size 1152x416 (each cell 288x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `belveth_fx_slow.png`：减速：脚下缠着的紫色虚空，4 帧循环

被减速的敌人脚下：一小圈**紫色的虚空能量**缠着脚，几缕细细的紫色触须一伸一缩。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58).
Effect: A VOID SNARE, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat violet ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 wide and 5 tall, two thin lavender tendrils at mirrored places curling up and down in turn, a magenta glint going round. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:7 cells, image size 1152x112 (each cell 288x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `belveth_fx_r_burst.png`：万载豪筵：吞下珊瑚、化为真身的爆发，6 帧

万载豪筵（参考 r_coral_base、r_flash、r_flashes_rays、r_shards、r_wave_mult、r_voidtentacles）：她脚下的**虚空珊瑚一下子炸开**——先是一下白紫色的闪光，一圈品红的冲击波贴着地往外推，粉紫色的珊瑚碎片和尖尖的紫色碎片往四周和往上飞，几根细细的虚空触须从地上扬起来。她在中间不画，**身体的位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF), a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58), a void coral pink-lilac ramp (#FFE8F4, #F6B4DA, #DA7CBE, #A44C96, #622C60).
Effect: A VOID CORAL BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Bel'Veth stands in the middle, not drawn: 46 squares wide and 47 tall (to the shoulder spikes) - leave her body's place EMPTY: 1 a white-lilac flash round her feet 20 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) and light rays rising; 2 a magenta shock ring 44 wide on the ground, pink-lilac coral shards bursting out and up at mirrored places; 3 the ring 60 wide, the shards high, four thin violet tentacles rising from the ground at mirrored places; 4 the shards falling, the tentacles curling; 5 the ring thin, a few shards; 6 sparkles fading. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 6 equal 64:48 cells, image size 6144x768 (each cell 1024x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `belveth_fx_r_hit.png`：万载豪筵：被珊瑚爆发打中，3 帧

被珊瑚爆发打中的敌人：身上一下白紫色闪光，几片粉紫色的珊瑚碎片扎上来、往两边弹开。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF), a void coral pink-lilac ramp (#FFE8F4, #F6B4DA, #DA7CBE, #A44C96, #622C60), a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258).
Effect: A CORAL HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-lilac flash 6 squares across on the target's chest; 2 pink-lilac coral shards bursting out 15 across at mirrored places; 3 the shards falling, fading. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal 16:18 cells, image size 768x288 (each cell 256x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `belveth_fx_r_aura.png`：真身：化身期间身边一直冒的虚空光，4 帧循环

真身期间：她身边一直**往上飘着淡紫色的虚空光点和几缕品红的光丝**，脚下一圈淡紫色的光，背后隐约张开一圈尖尖的紫色光芒（像女皇的冠）。她在中间不画，**身体的位置留空**；画在她身后，要淡一点。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58).
Effect: A VOID EMPRESS AURA, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Bel'Veth stands in the middle, not drawn: 46 squares wide and 47 tall (to the shoulder spikes) - leave her body's place EMPTY: a faint fan of sharp violet light spikes behind her shoulders like a crown, small lavender motes and two thin magenta wisps rising at mirrored places, a faint violet glow ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 40 wide; the motes and wisps rising frame to frame so the loop flows upward. Sparse and light - it plays behind her for 15 seconds. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 50:56 cells, image size 3200x896 (each cell 800x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `belveth_fx_c_eat.png`：吃珊瑚：击杀后珊瑚碎片飞进她身体，4 帧

击杀以后吃掉虚空珊瑚（参考 p_coral_tx、r_onkillray、r_minion_ringflare）：**几块粉紫色的珊瑚碎片从四周飞向她**，到身上化成一圈淡紫色的光。她在中间不画，**身体的位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void coral pink-lilac ramp (#FFE8F4, #F6B4DA, #DA7CBE, #A44C96, #622C60), a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF).
Effect: CORAL DRAWN IN, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); she stands in the middle, not drawn - leave the middle 18 squares wide EMPTY: 1 four pink-lilac coral shards at the cell's corners at mirrored places; 2 the shards halfway in with lavender trails; 3 the shards reaching her outline, a white-lilac glint; 4 a lavender ring round her fading. everything is the VOID's energy: sharp lavender and violet crescents and shards with hot magenta edges, pale lilac-white cores, deep purple depths; flat shades, crisp blade-like shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 30:36 cells, image size 1920x576 (each cell 480x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `belveth_fx_e_storm.png`：搠面皇锋：身边旋转的刀光风暴，6 帧循环

搠面皇锋（参考 e_wingflurry、eswirl、e_splashes、e_tether_crescent、swipes）：她原地不动，**身边一圈淡紫色的月牙刀光飞快地旋转**，刀光之间溅起青白色的水花（她是从海里来的），脚下一圈旋转的水纹。她在中间不画，**身体的位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a hot magenta ramp (#FFE0F6, #FF8AE2, #EE36C4, #B0188E, #6A0C58), a sea-foam teal ramp (#E8FFFC, #A8E8E8, #5CB4C4, #2E7088).
Effect: A STORM OF SLASHES, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Bel'Veth stands in the middle, not drawn: 46 squares wide and 47 tall (to the shoulder spikes) - leave her body's place EMPTY: a whirling ring 56 wide and 40 tall of sharp lavender crescent slashes with magenta edges round her, pale teal sea-foam flecks and droplets between them, a swirling water ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 50 wide; the crescents at mirrored places move round frame to frame (in frame k the left and right halves mirror each other) so the loop spins. her maelstrom is a whirling storm of blade-sharp lavender crescents with flecks of pale teal sea foam and droplets; flat shades, crisp shapes.
Layout: one horizontal row of 6 equal 60:44 cells, image size 5760x704 (each cell 960x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `belveth_fx_e_hit.png`：搠面皇锋：被风暴斩中，3 帧

被风暴的刀光斩中：一道**竖着的淡紫色月牙刀痕**（左右对称）加几滴青白色的水花。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-lilac flash ramp (#FFFFFF, #FCF2FF, #EED2FF), a void lavender-violet ramp (#FBE8FF, #E8B4FF, #C47CF4, #9248D8, #5E26A0, #321258), a sea-foam teal ramp (#E8FFFC, #A8E8E8, #5CB4C4, #2E7088).
Effect: A STORM CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-lilac vertical crescent slash 12 squares tall in the middle; 2 the slash with magenta edges, pale teal droplets splashing out at mirrored places; 3 fading. her maelstrom is a whirling storm of blade-sharp lavender crescents with flecks of pale teal sea foam and droplets; flat shades, crisp shapes.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `belveth_fx_a_hit` | view_effects `league_belveth_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `belveth_fx_p_as` | view_buffs `league_belveth_p_as`（tag `p_as`，跟随她，脚下，z -1；左右对称；约 4 秒） | 30 × 10 |
| `belveth_fx_q_dash` | view_effects `league_belveth_q_dash`（在她起步的地上，不跟随，z -1；左右对称） | 34 × 14 |
| `belveth_fx_q_hit` | view_effects `league_belveth_q_hit`（跟随目标，z 2；左右对称） | 18 × 16 |
| `belveth_fx_w_tail` | view_projectiles `league_belveth_w_tail`（直线弹道，z 2；上下对称） | 22 × 10 |
| `belveth_fx_w_slam` | view_effects `league_belveth_w_slam`（大表，在她身边的地上，不跟随，z -1；左右对称） | 48 × 20 |
| `belveth_fx_w_hit` | view_effects `league_belveth_w_hit`（跟随目标，z 2；左右对称） | 18 × 26 |
| `belveth_fx_slow` | view_buffs `league_belveth_w_slow` / `league_belveth_r_slow`（tag `slow`，跟随，脚下，z -1；左右对称） | 18 × 7 |
| `belveth_fx_r_burst` | view_effects `league_belveth_r_burst`（大表，在她身边的地上和身上，不跟随，z -1；左右对称） | 64 × 48 |
| `belveth_fx_r_hit` | view_effects `league_belveth_r_hit`（跟随目标，z 2；左右对称） | 16 × 18 |
| `belveth_fx_r_aura` | view_buffs `league_belveth_r_on`（tag `r_aura`，跟随她，z -1，在她身后；左右对称；约 15 秒） | 50 × 56 |
| `belveth_fx_c_eat` | view_effects `league_belveth_c_eat`（跟随她，z 2；左右对称） | 30 × 36 |
| `belveth_fx_e_storm` | view_buffs `league_belveth_e_on`（tag `e_storm`，大表，跟随她，z 3；左右对称；约 1.5 秒） | 60 × 44 |
| `belveth_fx_e_hit` | view_effects `league_belveth_e_hit`（跟随目标，z 2；左右对称） | 14 × 14 |

- 两张表：`asset/league/effects/league_belveth_fx`（小的）和 `league_belveth_big`（w_slam、r_burst、e_storm），tag = 名字（build_belveth.py 的 views；w_slow 和 r_slow 用 `slow`，r_on 用 `r_aura`，e_on 用 `e_storm`，p_as 用 `p_as`）。
- 弹道（w_tail）断言上下对称；其余断言左右对称。e_storm 循环 e_t（90 tick），r_aura 循环 r_t，p_as 循环 p_t，slow 循环。
- 用 `pixel_1x/` 切格（import_zac_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
