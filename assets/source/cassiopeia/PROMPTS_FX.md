# 魔蛇之拥 卡西奥佩娅：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型和动作已定（`design/cassiopeia_idle.png`：3/4 正面朝右的蛇身女人，金边翠绿蛇冠、额头蓝宝石、紫眼影、金爪手套、金色胸衣和腰带，下半身是深绿色的蛇尾，蛇尾平铺在身后往左伸）。她在游戏里是**高清**的（每个游戏格子里 1.3×1.3 个细像素），44 格高、49 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/cassiopeia_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/cassiopeia_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡西奥佩娅自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**双生毒牙和瘟毒爆炸是亮的毒绿色（芯是白黄色）**，**剧毒迷雾是深一点的绿色毒雾**，**石化凝视是金绿色的光**，**被石化是灰色的石头**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（`r_stone` 例外：石壳就是要包住他的下半身）。
> - **三张弹道图（`a_fang`、`w_bolt`、`r_wave`）画成朝右飞、上下对称**：游戏会按飞的方向把它转过去，往左飞时转半圈，上下对称才不会倒过来。**其余所有图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `cassiopeia_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/cassiopeia_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/cassiopeia_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 = E「双生毒牙」 | 每 0.75 秒甩出一颗追踪的毒牙，打中毒的目标伤害更高、给她回血 | `a_fang` · `a_hit` |
| 技能 1 = Q「瘟毒爆炸」 | 往目标脚下放，0.4 秒后炸开，范围里的敌人中毒 3 秒；打中英雄她加移速 | `q_warn` · `q_blast` · `q_hit` |
| 技能 2 = W「剧毒迷雾」 | 甩出毒液弹，落地后留下一片 5 秒的毒雾：持续掉血、减速、不能用位移技能 | `w_bolt` · `w_land` · `w_field` · `w_slow` |
| 大招「石化凝视」 | 眼睛放光，往面前扇形推出凝视波：面朝她的敌人石化 2 秒，背对她的减速 | `r_cast` · `r_wave` · `r_hit` · `r_stone` · `r_slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、毒液、毒雾、毒泡、光环、光波都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：石壳、石屑可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 亮毒绿（毒牙、瘟毒爆炸）：`#FFFFFF`、`#F2FFB8`、`#C6F05A`、`#84D23A`、`#3E9A30`、`#1D5A2A`；
  - 深毒绿（剧毒迷雾）：`#E6FFB4`、`#B4EC66`、`#78C846`、`#4C9C3E`、`#2E6E3C`、`#1A442E`；
  - 金绿色的光（石化凝视）：`#FFFFFF`、`#FFF6C4`、`#FFE07A`、`#D6EA62`、`#8ACB4C`、`#3C7A38`；
  - 灰色石头（石化）：`#F0ECE4`、`#CBC3B6`、`#A1978A`、`#786E64`、`#534B45`、`#322D2A`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：瘟毒爆炸的半径 22000，剧毒迷雾的半径 30000，凝视的扇形 72000 长、左右各 40 度）。

### 1. `cassiopeia_fx_a_fang.png`：普攻双生毒牙：飞出去的毒牙（弹道），3 帧（循环）

她每 0.75 秒甩出的一颗毒牙：一颗发亮的绿色**蛇牙形状的毒液弹**（像一颗弯弯的尖牙，尖头朝右），中间白色，后面拖一小段绿色的尾迹，旁边一两颗绿色毒滴（参考 Cass_SnakeHead_E、E_Cass_Greek_Fang、Cass_E_SnakeTrail）。**尖头朝右、上下对称**（游戏会按飞的方向转它，往左飞时转半圈，上下对称才不会倒过来）。约 12 × 8 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright poison-green ramp (#FFFFFF, #F2FFB8, #C6F05A, #84D23A, #3E9A30, #1D5A2A).
Effect: a FLYING VENOM FANG, 3 frames, a seamless loop, pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight: flying left it is turned half round and must not stand upside down): a glowing green fang-shaped venom bolt 7 squares long and 4 tall, its sharp tip at the right, a white core along its middle, a short green trail 4 squares behind it (to the left), two tiny green drops at mirrored places above and below the trail; each frame the trail flickers.
Layout: one horizontal row of 3 equal 12:8 cells, image size 576x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `cassiopeia_fx_a_hit.png`：毒牙命中（目标身上），4 帧

毒牙咬中目标：一团绿色的毒液四溅，中间白黄色的闪光，几道短短的绿色尖刺往外甩，几滴毒液（参考 cass_greek_fang_hit、E_Tar_Flash、E_Tar_Spikes）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright poison-green ramp (#FFFFFF, #F2FFB8, #C6F05A, #84D23A, #3E9A30, #1D5A2A).
Effect: a VENOM BITE on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 5 squares; 2 a green splash 10 squares with a white core, 4 short sharp green spikes flung out at mirrored angles; 3 the splash thinner and 12 squares, a few green drops at mirrored places; 4 fading drops.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `cassiopeia_fx_q_warn.png`：Q 瘟毒爆炸：落点预警（地上，不跟随，循环），4 帧

瘟毒爆炸落下前地上的预警圈：一个**扁椭圆的绿色细圈**（从斜上方看的圆），圈里几道向中间收的短线，一闪一闪（参考 Q_Target、Q_Hit_Poison_Ring）。**只有圈，中间不填满**（敌人站在里面要看得见）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright poison-green ramp (#FFFFFF, #F2FFB8, #C6F05A, #84D23A, #3E9A30, #1D5A2A).
Effect: A GROUND TARGET RING seen from above at an angle, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin bright green ellipse 42 squares wide and 14 tall, 1 square thick (a lighter top edge), 6 short dashes inside it pointing at the middle (mirrored), the middle left empty; 1 dim; 2 brighter; 3 brightest with a white glint on the ring's top; 4 like 2.
Layout: one horizontal row of 4 equal 46:18 cells, image size 2944x288 (each cell 736x288, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `cassiopeia_fx_q_blast.png`：Q 瘟毒爆炸：落地炸开的毒爆（地上，不跟随），6 帧

毒爆落地：地上猛地炸开一团绿色的毒液（几个鼓起来的毒泡破开），一圈扁的绿色冲击环往外扩，一团团绿色毒烟往上冒，几道毒液丝往外甩，然后毒烟慢慢散开（参考 Q_Hit_slam02、Q_Hit_Smoke_Clouds、Q_tar_cloud、Q_Hit_strands、Q_Hit_PoisonRing_Pulse）。**左右对称**，落点在格子中间偏下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright poison-green ramp (#FFFFFF, #F2FFB8, #C6F05A, #84D23A, #3E9A30, #1D5A2A).
Effect: A POISON BLAST bursting out of the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-green flash on the ground 10 squares wide; 2 bubbling green poison bursting up (round bubbles 3-6 squares, white highlights) 20 squares wide and 16 tall, a flat green shock ring on the ground (an ellipse 30 wide and 8 tall); 3 the ring 44 wide and 12 tall, green poison smoke puffs rising 26 squares, thin poison strands flung out at mirrored angles; 4 the smoke 32 squares tall, opening; 5 the smoke thinning and drifting out at both sides; 6 faint wisps and drops.
Layout: one horizontal row of 6 equal 48:40 cells, image size 4608x640 (each cell 768x640, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `cassiopeia_fx_q_hit.png`：Q 中毒（目标身上），4 帧

被瘟毒爆炸毒到的敌人身上冒出一小团绿色毒气，几个往上飘的毒泡（参考 Q_Hit_Gen_Orb01、Q_Hit_ball32、Q_Hit_color-poison_bell）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright poison-green ramp (#FFFFFF, #F2FFB8, #C6F05A, #84D23A, #3E9A30, #1D5A2A).
Effect: POISONED: a puff on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small green puff 6 squares with a white-yellow core; 2 the puff 11 squares, 3 round green bubbles rising from it at mirrored places; 3 the bubbles higher, the puff thinning; 4 two small bubbles and wisps.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `cassiopeia_fx_w_bolt.png`：W 剧毒迷雾：飞出去的毒液弹（弹道），3 帧（循环）

她甩出去的毒液弹：一颗圆圆的深绿色毒液球，亮绿色的芯，后面拖一小段毒液尾巴（参考 W_Acidball_Color、W_Head_Lead_V3、W_Meteor_Tail）。**朝右、上下对称**。约 10 × 8 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep poison-green cloud ramp (#E6FFB4, #B4EC66, #78C846, #4C9C3E, #2E6E3C, #1A442E).
Effect: A FLYING ACID BALL, 3 frames, a seamless loop, pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight: flying left it is turned half round and must not stand upside down): a round green poison ball 5 squares across (a bright green core with a white glint in the middle row), a short tapering green tail 4 squares behind it (to the left), two tiny drops at mirrored places above and below the tail; each frame the tail wobbles.
Layout: one horizontal row of 3 equal 10:8 cells, image size 480x128 (each cell 160x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `cassiopeia_fx_w_land.png`：W 毒液落地（地上，不跟随），4 帧

毒液弹落地：地上啪地溅开一滩绿色毒液（扁椭圆），几滴往外溅，冒出第一团毒雾（参考 W_Splat、W_Spit、W_Color_Texture_Splash）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep poison-green cloud ramp (#E6FFB4, #B4EC66, #78C846, #4C9C3E, #2E6E3C, #1A442E).
Effect: A POISON SPLAT on the ground seen from above at an angle, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-green flash 8 squares wide on the ground; 2 a green splat (a flat ellipse 24 squares wide and 6 tall with ragged edges) and drops flung out at mirrored places; 3 the splat 34 wide and 9 tall, a first low green mist rising 4 squares; 4 the splat settling, the drops gone.
Layout: one horizontal row of 4 equal 40:16 cells, image size 2560x256 (each cell 640x256, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `cassiopeia_fx_w_field.png`：W 剧毒迷雾：地上的毒雾（地上，不跟随，每 1/4 秒接着放），4 帧

地上一大片低低的深绿色毒雾：几团圆滚滚的毒雾团（扁的，贴着地面），里面几个冒泡的毒泡，雾团慢慢翻滚（参考 W_Poison_Cloud_Shapes、W_Greek_PoisonPool_Color、W_voidooze_bubbles、W_Smoke_Color）。**雾要低、要透**：雾团之间留空隙、中间偏下最浓，**站在里面的人上半身要看得见**（雾高不超过 14 格）。**左右对称**，第 4 帧要能接回第 1 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep poison-green cloud ramp (#E6FFB4, #B4EC66, #78C846, #4C9C3E, #2E6E3C, #1A442E).
Effect: A LOW POISON MIASMA lying on the ground seen from above at an angle, 4 frames, a seamless loop (frame 4 flows back into frame 1), SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a field of flat rounded green poison cloud puffs (each 8-14 squares wide and 4-7 tall, a lighter top, a darker underside, no outline) filling an ellipse 60 squares wide and 18 tall, at most 14 squares high, with gaps between the puffs (units standing in it must stay visible), 4-6 small round poison bubbles rising and popping in it at mirrored places; each frame the puffs roll a square along the ring.
Layout: one horizontal row of 4 equal 64:28 cells, image size 4096x448 (each cell 1024x448, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `cassiopeia_fx_w_slow.png`：W 减速 + 禁锢（敌人脚下，循环），4 帧

在毒雾里被减速、不能用位移技能的敌人：脚下一圈绿色毒液缠着双脚（扁的毒液环），几个小毒泡往上冒（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，只画在他脚下，不要盖住身体）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep poison-green cloud ramp (#E6FFB4, #B4EC66, #78C846, #4C9C3E, #2E6E3C, #1A442E).
Effect: POISON AT A UNIT'S FEET, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): a flat green poison ring round its feet (an ellipse 16 squares wide and 5 tall, 2 squares thick, a lighter top edge), 3 tiny bubbles rising from it at mirrored places; each frame the bubbles rise a square and pop; nothing above 8 squares.
Layout: one horizontal row of 4 equal 20:12 cells, image size 1280x192 (each cell 320x192, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `cassiopeia_fx_r_cast.png`：R 石化凝视：她的眼睛放光（她身上，跟随），4 帧

她放大招时眼睛和头上猛地亮起金绿色的光：她的头上一团金绿色的光芒，几道放射状的光线往四周射，额头位置一颗白色的亮星（参考 R_cass_ult_eye、R_Flare-Sun_05、R_Light_Rays_01）。**左右对称**，光芒在她头的高度（the serpent woman stands in the middle, not drawn: 44 squares from her crest to the ground, her upper body about 20 squares wide above her coiled neck, her head 30-44 squares above the ground），身体留空不画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold-green light ramp (#FFFFFF, #FFF6C4, #FFE07A, #D6EA62, #8ACB4C, #3C7A38).
Effect: A GLARE OF LIGHT round a figure's head, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the serpent woman stands in the middle, not drawn: 44 squares from her crest to the ground, her upper body about 20 squares wide above her coiled neck, her head 30-44 squares above the ground): the light's middle 37 squares above the ground; 1 a white star 4 squares; 2 a gold-green burst 14 squares with a white core, 8 thin light rays shooting out in a star (mirrored); 3 the rays 24 squares across, thinner; 4 fading rays and a few sparkles; nothing below 26 squares.
Layout: one horizontal row of 4 equal 28:56 cells, image size 1792x896 (each cell 448x896, 16 px a square); centered across, the figure's ground 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `cassiopeia_fx_r_wave.png`：R 石化凝视：往前推出去的凝视波（弹道），4 帧（循环）

从她眼睛里推出去的石化凝视：一道**向右凸的弧形金绿色光波**（像一个月牙，凸面朝右），光波上有几道往右的光束，中间最亮是白色，后面拖几道淡淡的光线（参考 R_Lightbeam、R_lightbeams、R_Aoe_Decal_side）。**朝右、上下对称**（游戏按飞的方向转它）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold-green light ramp (#FFFFFF, #FFF6C4, #FFE07A, #D6EA62, #8ACB4C, #3C7A38).
Effect: A WAVE OF PETRIFYING LIGHT, 4 frames, a seamless loop, pointing RIGHT (its flight direction), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight: flying left it is turned half round and must not stand upside down): a crescent-shaped gold-green light wave 34 squares tall and 6 thick, bulging to the RIGHT, a white core along its middle, 5 short light beams pointing right out of its front at mirrored heights, faint trailing light streaks to the left; each frame the beams flicker and the crescent shimmers.
Layout: one horizontal row of 4 equal 24:40 cells, image size 1536x640 (each cell 384x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `cassiopeia_fx_r_hit.png`：R 命中（目标身上），4 帧

被凝视扫中：一圈金绿色的闪光，几块灰色的小石屑往外崩（参考 R_Stone_Mult、Cassiopeia_Base_rock_debris、Hit_1）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold-green light ramp (#FFFFFF, #FFF6C4, #FFE07A, #D6EA62, #8ACB4C, #3C7A38) and a grey stone ramp (#F0ECE4, #CBC3B6, #A1978A, #786E64, #534B45, #322D2A).
Effect: A GAZE HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 6 squares; 2 a gold-green burst 12 squares with a white core, 4 small grey stone chips (2x2 squares, a dark edge: solid) flying out at mirrored places; 3 the burst a thin ring 15 squares, the chips farther; 4 fading chips.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `cassiopeia_fx_r_stone.png`：R 石化（被石化的敌人身上，循环），4 帧

面朝她被石化的敌人：从脚往上长出一层**灰色的石壳**，把他的腿和腰包住（石块一块块的，亮面朝上，有裂纹），肩膀和头上落着几块石屑，一闪一闪的白色高光（参考 Death_stonecass、R_Stone_Mult、rock_debris）。**左右对称**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn；石壳包住他下半身——从地面到18 格高，上半身只有零散的石片，脸要看得见）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey stone ramp (#F0ECE4, #CBC3B6, #A1978A, #786E64, #534B45, #322D2A).
Effect: A STONE CRUST over a unit, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): grey stone blocks (a light top face, a darker side, a 1-square dark outline: solid, with a few cracks) wrapping its legs and waist from the ground up to 18 squares high (the crust 20 squares wide at the ground, 16 at its top), a few loose stone chips (2x2 squares) on its shoulders and head at mirrored places, the face and chest left clear; each frame a white glint moves over the blocks.
Layout: one horizontal row of 4 equal 24:44 cells, image size 1536x704 (each cell 384x704, 16 px a square); centered across, the unit's feet 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `cassiopeia_fx_r_slow.png`：R 减速（背对她的敌人脚下，循环），4 帧

背对她、只被减速的敌人：脚下一圈淡淡的金绿色光环，几颗灰色的小石屑在光环上（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，只画在他脚下）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, poison, smoke, clouds or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold-green light ramp (#FFFFFF, #FFF6C4, #FFE07A, #D6EA62, #8ACB4C, #3C7A38) and a grey stone ramp (#F0ECE4, #CBC3B6, #A1978A, #786E64, #534B45, #322D2A).
Effect: A SLOWING RING at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): a thin gold-green ellipse 16 squares wide and 5 tall round its feet (1 square thick, a lighter top), 4 tiny grey stone chips on it at mirrored places (1x1 or 2x1 squares, a dark edge); each frame a white glint moves along the ring; nothing above 8 squares.
Layout: one horizontal row of 4 equal 20:12 cells, image size 1280x192 (each cell 320x192, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `cassiopeia_fx_a_fang` | view_projectiles `league_cassiopeia_a_fang`（随飞行方向转；画成**朝右**、**上下对称**） | 12 × 8 |
| `cassiopeia_fx_a_hit` | view_effects `league_cassiopeia_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `cassiopeia_fx_q_warn` | view_effects `league_cassiopeia_q_warn`（不跟随，画在人物下面 z -2；左右对称；落下前 0.4 秒一直在放；大图表） | 46 × 18 |
| `cassiopeia_fx_q_blast` | view_effects `league_cassiopeia_q_blast`（不跟随，画在人物上面 z 2；左右对称；大图表） | 48 × 40 |
| `cassiopeia_fx_q_hit` | view_effects `league_cassiopeia_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `cassiopeia_fx_w_bolt` | view_projectiles `league_cassiopeia_w_bolt`（随飞行方向转；画成**朝右**、**上下对称**） | 10 × 8 |
| `cassiopeia_fx_w_land` | view_effects `league_cassiopeia_w_land`（不跟随，画在人物下面 z -1；左右对称；大图表） | 40 × 16 |
| `cassiopeia_fx_w_field` | view_effects `league_cassiopeia_w_field`（不跟随，画在人物下面 z -1；左右对称；5 秒内每 15 tick 再放一次：4 帧连起来要能无缝接上；大图表） | 64 × 28 |
| `cassiopeia_fx_w_slow` | view_buffs `league_cassiopeia_w_slow`（跟随，画在人物上面；左右对称；循环） | 20 × 12 |
| `cassiopeia_fx_r_cast` | view_effects `league_cassiopeia_r_cast`（跟随，画在人物上面 z 3；左右对称；大图表） | 28 × 56 |
| `cassiopeia_fx_r_wave` | view_projectiles `league_cassiopeia_r_wave`（随飞行方向转；画成**朝右**、**上下对称**；大图表） | 24 × 40 |
| `cassiopeia_fx_r_hit` | view_effects `league_cassiopeia_r_hit`（跟随，画在人物上面；左右对称） | 16 |
| `cassiopeia_fx_r_stone` | view_buffs `league_cassiopeia_r_stone`（跟随，画在人物上面 z 2；左右对称；循环，石化 2 秒内一直在） | 24 × 44 |
| `cassiopeia_fx_r_slow` | view_buffs `league_cassiopeia_r_slow`（跟随，画在人物上面；左右对称；循环） | 20 × 12 |

- 两张表：`asset/league/effects/league_cassiopeia_fx`（小的）和 `league_cassiopeia_big`（q_warn、q_blast、w_land、w_field、r_cast、r_wave），tag = 名字（build_cassiopeia.py 的 views）。
- `q_warn` 在落下前的 24 tick 里循环；`w_field` 每 15 tick 再放一次（4 帧共 250 毫秒），5 秒里接成一片；`q_blast`、`w_land`、`w_field` 不跟随（地上的点）。弹道图朝右、上下对称（随飞行转）；其余全部左右对称。
- 用 `pixel_1x/` 切格（import_maokai_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（石壳、石屑保留描边）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（普朗克的教训：Codex 自己的 1 倍图可能洗白颜色，必要时从 raw/ 读回）。
