# 机械公敌 兰博：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型已定（`design/rumble_design.png`：Q 版蓝毛约德尔人坐在黄铜色的废铁机甲里——亮蓝莫西干、红镜片护目镜、坏笑；往前伸的长喷火炮管、后面那只机械手握着带刺铁球、背上两个红头火箭舱、短腿和红色圆盘脚）。兰博在游戏里是**高清**的（每个游戏格子里 1.75×1.75 个细像素），36 格高、53 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/rumble_size.png`：兰博缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里兰博自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**兰博是约德尔人的废铁机甲**，特效都是**机械和火**：喷火炮的**橙黄火焰**、**黑烟**、过热的**白色蒸汽**、鱼叉的**蓝白电弧**、护盾的**黄铜和钢铁废料**；不要魔法符文，也不要光滑的霓虹光束。
> - **特效要亮**：每道火、每道电都有最亮一档或白色的高光，暗底上一眼能看见。
> - **火、电、烟、蒸汽没有黑描边**（用它自己最深的一档）；**只有火箭、鱼叉、废铁片这些“东西”有 1 格近黑描边**。
> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人（`w_shield`、`dz_on`、`oh_on`、`r_launch` 罩着兰博自己）。
> - **对称**：所有不飞的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`e_harpoon`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**`q_flame` 例外**：它画进兰博自己的动作帧里、跟着他一起翻，所以**朝右、不用对称**。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `rumble_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/rumble_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/rumble_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 抡带刺铁球砸；过热时每一击都着火 | `a_hit` · `oh_hit` |
| 被动「废品巨像」（热量） | 放技能攒热量；热量过半进危险地带（技能加强、冒蒸汽）；热量满了过热（几秒不能放技能，普攻着火、冒黑烟） | `dz_on` · `dz_steam` · `oh_on` · `oh_smoke` |
| 技能 1 =「纵火盛宴」 | 喷火炮往前喷一大股火，烧锥形范围里的人 | `q_flame` · `q_hit` |
| 破碎护盾（W，并入被动） | 附近有敌方英雄时自动套上废铁护盾，加一点移速 | `w_shield` · `haste` |
| 技能 2 =「电子鱼叉」 | 射鱼叉：伤害、减速；打中英雄后再射第二发（更痛、减速更多） | `e_harpoon` · `e_hit` · `e2_hit` · `e_zap` |
| 大招 =「恒温灼烧」 | 背上的火箭一齐打出去，沿一条线落下，地上烧出一条火线，烧到的人减速 | `r_launch` · `r_fall` · `burn` |

连招：**鱼叉打中英雄 → 第二发鱼叉**，**第二发打中 → 马上喷火**，**火箭落地 → 马上射鱼叉**，**进危险地带 → 马上套护盾**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、电、烟、蒸汽没有黑描边，也不要用最深的颜色给形状描一圈边**（火箭、鱼叉、废铁片除外）。
- **都是废铁机甲**：火、烟、蒸汽、电、黄铜和钢；每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 火：`#FFFFFF`、`#FFF4A8`、`#FFCC3C`、`#FF8A1C`、`#E8441A`、`#9C2010`；
  - 烟·煤灰：`#D0C8C0`、`#948C86`、`#605A56`、`#3A3634`、`#1E1C1C`；
  - 电：`#FFFFFF`、`#CCF6FF`、`#70DCFF`、`#2C98F4`、`#1A4CB8`；
  - 蒸汽：`#FFFFFF`、`#E6EEF2`、`#BCCAD2`、`#8A9CA8`；
  - 黄铜：`#FFF2C4`、`#ECBE56`、`#B47E2C`、`#72501C`、`#3C2A12`；
  - 钢：`#E2E6EA`、`#A0A8B0`、`#646C74`、`#3A4046`；
- 打中、爆发居中画，不旋转；地面上的圈（火区、尾气）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `rumble_fx_a_hit.png`：普攻：铁球砸中，3 帧

带刺铁球砸在敌人身上：一个白色的闪光，几块铁片和橙色火星往外弹（参考 hiteffect、sharp_flash、metal_shards）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#E2E6EA, #A0A8B0, #646C74, #3A4046), a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010).
Effect: A SPIKED IRON BALL STRIKE LANDING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares across; 2 a ring of short orange sparks and little grey metal shards bursting out 11 across at mirrored places; 3 the sparks further out, dimming. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `rumble_fx_oh_hit.png`：过热：烧着的一击，4 帧

过热时的普攻：铁球砸中处炸开一团火，火舌往上窜、冒黑烟（参考 fireball_hit、overheat_plasma）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010), a soot and smoke ramp (#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C).
Effect: A BURNING STRIKE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 across; 2 an orange fire burst 12 across, flame tongues licking up at mirrored places; 3 the flames 8 squares tall, black smoke curls rising from them; 4 smoke and embers. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `rumble_fx_q_flame.png`：纵火盛宴：喷火炮喷出的火，4 帧循环（画进他自己的动作帧）

喷火炮喷出的**一大股火**：从格子左边中间（炮口）喷出，往右越来越宽、越来越暗，最前面卷成翻滚的火团、冒黑烟（参考 flames_flamethrower、color-flamethrower、flames02/03）。**朝右，不用对称**（这张画进他自己的动作帧，会跟着他一起翻），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010), a soot and smoke ramp (#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C).
Effect: A FLAMETHROWER BLAST, 4 looping frames, pointing RIGHT, NOT symmetric (drawn into his own skill frames at the cannon's muzzle; the game mirrors his frames with him): the fire pours out of a nozzle at the MIDDLE of the cell's LEFT edge: a white-yellow core 3 squares tall at the nozzle, widening to the right into a roaring orange cone 14 squares tall at 30 squares, its far end breaking into rolling red-orange fireballs and curls of black smoke at the right edge; the tongues and fireballs shift a step forward each frame so it loops. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal 40:18 cells, image size 2560x288 (each cell 640x288, 16 px a square); the nozzle at the middle of the left edge in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `rumble_fx_q_hit.png`：纵火盛宴：被火烧到，3 帧

被喷火烧到：身上冒起几簇小火苗和火星。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010), a soot and smoke ramp (#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C).
Effect: A SCORCH ON A UNIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two small orange flames 4 squares tall at mirrored places 6 apart; 2 the flames 7 tall, embers flying up; 3 the flames shrinking, a wisp of black smoke. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `rumble_fx_e_harpoon.png`：电子鱼叉：飞出去的鱼叉，4 帧循环

射出去的**电子鱼叉**：一支钢鱼叉头朝右，叉身缠着蓝白色的电弧，后面拖着一条电光尾巴（参考 taze_mis_missile、taze_mis_electric、taze_mis_trail）。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#E2E6EA, #A0A8B0, #646C74, #3A4046), an electric ramp (#FFFFFF, #CCF6FF, #70DCFF, #2C98F4, #1A4CB8).
Effect: AN ELECTRO-HARPOON IN FLIGHT, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a steel harpoon 9 squares long, its barbed head at the right, crackling cyan-blue electric arcs wrapped round its shaft, a jagged cyan-white lightning trail 6 long behind it; the arcs jump to new places each frame (mirrored top and bottom). everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `rumble_fx_e_hit.png`：电子鱼叉：打中，3 帧

鱼叉打中：蓝白色的电光炸开，几道电弧往外窜（参考 taze_tar_plasma、taze_tar_sphere）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric ramp (#FFFFFF, #CCF6FF, #70DCFF, #2C98F4, #1A4CB8).
Effect: AN ELECTRIC JOLT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan flash 6 across; 2 a ball of crackling blue sparks 10 across with jagged arcs shooting out at mirrored places to 13 across; 3 a few arcs and sparks dimming. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `rumble_fx_e2_hit.png`：电子鱼叉：第二发打中（更强），4 帧

第二发鱼叉打中同一个人：比第一发更大的电光爆开，一圈蓝色电环往外扩（参考 blue_rings、flare-rainbow_blue）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric ramp (#FFFFFF, #CCF6FF, #70DCFF, #2C98F4, #1A4CB8).
Effect: A BIGGER ELECTRIC BLAST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white star flash 8 across; 2 a cyan-blue ring 14 across with jagged arcs sticking out at mirrored places; 3 the ring 17 across breaking into sparks; 4 sparks and two small arcs fading. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `rumble_fx_e_zap.png`：电子鱼叉：被减速的人身上噼啪的电，4 帧循环

被鱼叉减速的敌人：身体两边一闪一闪地爬着几道小电弧（**身体位置留空**，只画在外圈）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric ramp (#FFFFFF, #CCF6FF, #70DCFF, #2C98F4, #1A4CB8).
Effect: CRACKLING ELECTRICITY ON A UNIT, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit (16 wide, 28 tall) in the middle not drawn: small jagged cyan-blue arcs 3-5 squares long crawling up its left and right edges at mirrored places, a few white sparks; the arcs jump to new places each frame; the middle left empty. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal 20:30 cells, image size 1280x480 (each cell 320x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `rumble_fx_w_shield.png`：破碎护盾：围着他的废铁护盾，4 帧循环

破碎护盾：**一圈半透明的护盾罩着整个机甲**，罩子的边上转着一圈废铁（黄铜板、螺母、螺丝、钢片），蓝白色的光边一闪一闪（参考 shield_01_flash、mord_energy_ball、nut、screw）。他走路时也挂着，**中间他的身体位置留空**（只画罩子的边和废铁）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a brass ramp (#FFF2C4, #ECBE56, #B47E2C, #72501C, #3C2A12), a steel ramp (#E2E6EA, #A0A8B0, #646C74, #3A4046), an electric ramp (#FFFFFF, #CCF6FF, #70DCFF, #2C98F4, #1A4CB8).
Effect: A SCRAP SHIELD AROUND THE MECH, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Rumble's mech stands in the middle, not drawn: 36 squares from the mohawk to the ground, its hull about 24 squares wide (the cell's bottom on the ground): a dome outline 52 squares wide and 40 tall round him, a thin bright cyan-white rim 1-2 squares wide with a faint blue glint here and there, and a ring of junk riding on the rim at mirrored places - brass plates, hex nuts, screws, bent steel sheets, each 2-4 squares; the junk shifts a step round the rim each frame and the rim flickers; the inside left EMPTY (he shows through). everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal 56:42 cells, image size 3584x672 (each cell 896x672, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `rumble_fx_haste.png`：破碎护盾：加速时脚下的尾气，4 帧循环

护盾带的加速：机甲脚下两边喷出一股股灰白的尾气和几粒火星，像引擎全开。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steam ramp (#FFFFFF, #E6EEF2, #BCCAD2, #8A9CA8), a soot and smoke ramp (#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C), a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010).
Effect: EXHAUST PUFFS AT THE FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), the middle 20 squares left empty: puffs of white-grey exhaust 4-6 squares rolling out to both sides along the ground, a few orange sparks; the puffs roll outward a step each frame. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal 40:10 cells, image size 2560x160 (each cell 640x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `rumble_fx_dz_on.png`：危险地带：热量过半那一下，5 帧

进入危险地带（热量 50 以上）：机甲两边猛地喷出两股白色蒸汽，一圈橙红色的热浪闪一下（参考 color-hex_steam、smoke_02、distort-heat）。**他的身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steam ramp (#FFFFFF, #E6EEF2, #BCCAD2, #8A9CA8), a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010).
Effect: STEAM VENTING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Rumble's mech stands in the middle, not drawn: 36 squares from the mohawk to the ground, its hull about 24 squares wide (the cell's bottom on the ground): 1 an orange-red heat flash ring 30 across round his middle (only the ring); 2 two jets of white steam bursting out sideways from his shoulders at mirrored places, 8 squares long; 3 the jets 14 long, rolling up; 4 the steam clouds rising and spreading; 5 wisps fading. The middle 24 squares left empty. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 5 equal square cells, image size 3200x640 (each cell 640x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `rumble_fx_dz_steam.png`：危险地带：热着的时候冒的蒸汽，4 帧循环

在危险地带里：机甲肩膀两边一缕缕往上冒白色蒸汽和热气（格子底边贴着他的肩膀）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steam ramp (#FFFFFF, #E6EEF2, #BCCAD2, #8A9CA8).
Effect: STEAM RISING FROM A HOT MECH, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two thin columns of white steam puffs at mirrored places 26 squares apart, rising from the cell's bottom (his shoulders) 12 squares up and curling outward; the puffs climb a step each frame. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal 36:16 cells, image size 2304x256 (each cell 576x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `rumble_fx_oh_on.png`：过热：炸出一团火和黑烟，6 帧

过热（热量满了）：机甲身上**轰地炸出一大团火和黑烟**，往上冲、往两边翻，火星四溅，几块废铁片弹飞（参考 overheat_plasma、poof_soot2、charred_billow、infernalguardian）。**他的身体位置大致留空**（火从他背后、两边冒）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010), a soot and smoke ramp (#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C).
Effect: AN OVERHEAT BLOWOUT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Rumble's mech stands in the middle, not drawn: 36 squares from the mohawk to the ground, its hull about 24 squares wide (the cell's bottom on the ground): 1 a white-yellow flash behind his top 14 across; 2 a fireball bursting up 24 across above and round him, flames licking out to both sides; 3 the fire 40 across, thick black smoke rolling up from it, sparks and a few small steel shards flying out at mirrored places; 4 the smoke billowing 48 across, the fire inside it dying; 5 a black smoke cloud with embers; 6 smoke thinning. His body (the middle 24 squares wide, 30 tall) never covered by solid fire. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 6 equal 56:50 cells, image size 5376x800 (each cell 896x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `rumble_fx_oh_smoke.png`：过热中：冒黑烟着火，4 帧循环

过热的几秒里：机甲肩膀两边窜着小火苗、往上冒滚滚黑烟（格子底边贴着他的肩膀）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010), a soot and smoke ramp (#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C).
Effect: AN OVERHEATED MECH SMOKING, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): at mirrored places 26 squares apart on the cell's bottom (his shoulders), small orange flames 4 squares tall and above them thick black smoke curling 16 squares up; the smoke rolls up a step each frame, embers drifting. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal 36:22 cells, image size 2304x352 (each cell 576x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `rumble_fx_r_launch.png`：恒温灼烧：背上的火箭一齐打出去，5 帧

发射火箭：机甲背后猛地一亮，**几枚火箭拖着火焰和白烟笔直往上飞出格子**，下面留一团硝烟（参考 r_burn_rocket、r_rockettrail、r_rocketsmoke）。**他的身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010), a soot and smoke ramp (#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C), a steam ramp (#FFFFFF, #E6EEF2, #BCCAD2, #8A9CA8), a steel ramp (#E2E6EA, #A0A8B0, #646C74, #3A4046).
Effect: ROCKETS LAUNCHING STRAIGHT UP from behind him, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Rumble's mech stands in the middle, not drawn: 36 squares from the mohawk to the ground, its hull about 24 squares wide at the bottom of the cell: 1 a white-orange flash 14 across just above his head; 2 three small rockets (steel bodies, red tips, 2 wide and 5 tall) leaving it straight up at mirrored places (one in the middle, two 8 squares to the sides), each with a white-yellow flame under it; 3 the rockets 20 squares higher, each trailing fire and a white smoke column; 4 the rockets at the top edge, the smoke columns to the cell's top; 5 the rockets gone, the smoke columns and a puff of smoke over him drifting. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 5 equal 36:60 cells, image size 2880x960 (each cell 576x960, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `rumble_fx_r_fall.png`：恒温灼烧：火箭落地烧一片，10 帧

一枚火箭从天上**笔直扎下来**、落地爆炸，然后地上**烧着一块火**（几块连成一条火线），烧一会儿后熄成火星（参考 r_impactcrater、r_impactflasha、r_burn_sparks、r_dirt_rock）。**左右对称**，10 帧（5–8 帧是火在地上烧，可以循环）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010), a soot and smoke ramp (#D0C8C0, #948C86, #605A56, #3A3634, #1E1C1C), a steel ramp (#E2E6EA, #A0A8B0, #646C74, #3A4046).
Effect: A ROCKET STRIKE AND A BURNING PATCH, 10 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the ground patch on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) at the bottom of the cell, about 20 squares wide and 7 tall: 1 a small steel rocket with a red tip pointing straight DOWN near the top middle, a fire trail above it; 2 the rocket just above the ground; 3 a white-yellow impact flash 12 across on the ground; 4 an orange blast 20 across, clods of dirt flying out to both sides; 5-8 a patch of burning ground 20 wide: orange flames 4-7 squares tall dancing on a dark scorched ellipse, the tongues changing a step each frame (5-8 loop); 9 the flames low, black smoke; 10 embers on the scorched ground. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 10 equal 24:40 cells, image size 3840x640 (each cell 384x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `rumble_fx_burn.png`：恒温灼烧：被烧的人脚下，4 帧循环

被火区烧到、减速的敌人脚下：一圈小火苗烧着脚。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire ramp (#FFFFFF, #FFF4A8, #FFCC3C, #FF8A1C, #E8441A, #9C2010).
Effect: FLAMES LICKING AT THE FEET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a band of small orange flames 16 squares wide and 3-5 squares tall, the middle a little lower; the tongues change a step each frame, mirrored. everything is a yordle's JUNKYARD TECH: roaring orange flamethrower fire, sooty black smoke, white steam, crackling cyan-blue electricity, brass and steel scrap; flat shades, crisp chunky shapes; no smooth neon beams, no magic runes.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `rumble_fx_a_hit` | view_effects `league_rumble_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `rumble_fx_oh_hit` | view_effects `league_rumble_oh_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `rumble_fx_q_flame` | 画进 skill 动作帧（q_spray 的炮口；跟着他翻转，可以有方向） | 40 × 18 |
| `rumble_fx_q_hit` | view_effects `league_rumble_q_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `rumble_fx_e_harpoon` | view_projectiles `league_rumble_e_harpoon`（弹道，z 2；上下对称） | 16 × 8 |
| `rumble_fx_e_hit` | view_effects `league_rumble_e_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `rumble_fx_e2_hit` | view_effects `league_rumble_e2_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `rumble_fx_e_zap` | view_buffs `league_rumble_e_zap`（跟随，身上，z 3；左右对称） | 20 × 30 |
| `rumble_fx_w_shield` | view_buffs `league_rumble_w_shield`（跟随，罩着他，z 3；左右对称） | 56 × 42 |
| `rumble_fx_haste` | view_buffs `league_rumble_haste`（跟随，脚下，z -1；左右对称） | 40 × 10 |
| `rumble_fx_dz_on` | view_effects `league_rumble_dz_on`（跟随他，z 3；左右对称） | 40 × 40 |
| `rumble_fx_dz_steam` | view_buffs `league_rumble_dz_steam`（跟随，头上，z 3；左右对称） | 36 × 16 |
| `rumble_fx_oh_on` | view_effects `league_rumble_oh_on`（大表，跟随他，z 3；左右对称） | 56 × 50 |
| `rumble_fx_oh_smoke` | view_buffs `league_rumble_oh_smoke`（跟随，头上，z 3；左右对称） | 36 × 22 |
| `rumble_fx_r_launch` | view_effects `league_rumble_r_launch`（大表，跟随他，z 3；左右对称） | 36 × 60 |
| `rumble_fx_r_fall` | view_effects `league_rumble_r_fall`（大表，地上，z -1，不跟随；左右对称；长度 = 火区的时间） | 24 × 40 |
| `rumble_fx_burn` | view_buffs `league_rumble_burn`（跟随，脚下，z -1；左右对称） | 18 × 8 |

- 两张表：`asset/league/effects/league_rumble_fx`（小的）和 `league_rumble_big`（oh_on、r_launch、r_fall），tag = 名字（build_rumble.py 的 views；w_shown → w_shield、w_ms → haste、dz → dz_steam、oh → oh_smoke、e_slow → e_zap、r_slow → burn）。r_fall 的 tag 和火区一样长（r_t），5–8 帧循环填满。
- 画进动作帧的 `q_flame`（skill）：rig_rumble.py 把它贴在 q_spray 的炮口（炮管方向），帧按 q_t 循环。
- 弹道（e_harpoon）断言上下对称；q_flame 不断言；其余断言左右对称。
- 用 `pixel_1x/` 切格（import_ivern_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
