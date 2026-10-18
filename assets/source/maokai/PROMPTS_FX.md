# 茂凯：给 Codex 的特效提示词（第 3 步）

> **这一份是 21 张特效图。** 造型和动作已定（`design/maokai_idle.png`：3/4 正面朝右的巨大树精，背上青绿苔藓树冠，脸长在树干中间、两只蓝眼睛，近侧一条巨大的浅褐色木头手臂、拳头上刻着发蓝光的鬼脸，远侧绿爪子拿着小树苗，背后树枝挂着蓝色水晶灯笼，腰间紫布）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），41 格高、39 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/maokai_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/maokai_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - `design/maokai_sapling.png`：**树苗的造型**（8 倍）。和树苗有关的几张（`e_land`、`e_idle`、`e_burst`）照它的样子画，但**地上的树苗要画成正面朝前、左右对称**（脸朝着看的人：游戏在红色方不会把图镜像，侧面的树苗到了红色方会朝反方向）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里茂凯自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**被动回血是绿色的自然魔法**，**荆棘重击是橄榄褐的尘土加白色光刺**，**扭曲突刺是带青色光纹的树根和泥土**，**树苗的爆炸是青绿色**，**自然之握是带刺的树根、绿色荆棘和发青光的裂纹**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。
> - **地上、身上的图全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像。
> - **4 张飞出去的图（`e_lob`、`q_wave`、`w_trail`、`r_wall`）朝右画、严格上下对称**：游戏会把它们转到飞行方向，往左飞的时候是上下颠倒的，所以上下必须一样。荆棘墙 `r_wall` 在图里是**竖着的一条宽带**（游戏里它横在前进方向上）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `maokai_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/maokai_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/maokai_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「吸元秘术」 | 巨臂砸击；技能打中敌人后，下一次普攻额外造成魔法伤害并给自己回血 | `a_hit` · `p_hit` · `p_heal` |
| 技能 1 = Q「荆棘重击」 | 拳头砸地，推开身边的敌人，一道冲击波沿地面往前推，打中的敌人减速 | `q_cast` · `q_wave` · `q_hit` · `q_slow` |
| 技能 2 = W「扭曲突刺」 | 化作树根钻进地里冲向敌方英雄（冲刺时他看不见、免伤），冒出来禁锢目标 | `w_trail` · `w_land` · `w_hit` · `root` |
| 自动放的 E「树苗投掷」 | 把树苗扔到敌人脚下，树苗扎根站岗，敌人靠近就扑上去爆炸，炸到的敌人减速 | `e_lob` · `e_land` · `e_idle` · `e_burst` · `e_hit` · `e_slow` |
| 大招「自然之握」 | 两臂砸地，一道很宽的荆棘墙慢慢往前推，碰到的敌人受伤并被禁锢（推得越远禁锢越久），撞到英雄后他加速 | `r_cast` · `r_wall` · `r_hit` · `root` · `r_haste` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：树苗、树根、树皮、石块可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 绿色自然魔法（被动、加速）：`#FFFFFF`、`#E6FFE0`、`#9CF5A8`、`#3FD98A`、`#1F9E6E`、`#0E5A48`；
  - 青色发光（树苗爆炸、发光的裂纹和根上的纹路）：`#FFFFFF`、`#D8FFF8`、`#7CF2E4`、`#22C9C0`、`#138A92`、`#0A4A58`；
  - 橄榄褐尘土泥块（荆棘重击、落地的尘土）：`#F4ECD8`、`#D8C69C`、`#B09A6A`、`#857048`、`#5A4A30`、`#352C1E`；
  - 树皮树根（树根、木屑）：`#E8B888`、`#C08458`、`#8E5A3C`、`#643C2C`、`#42282A`、`#24161C`；
  - 叶子苔藓荆棘（叶子、荆棘藤）：`#F2FFB0`、`#C8EA5A`、`#8CC23C`、`#5A9030`、`#36602A`、`#1E3A1E`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（21 张）

21 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：荆棘重击推开半径 16000、冲击波宽 20000，树苗爆炸半径 24000，荆棘墙宽 56000）。

### 1. `maokai_fx_a_hit.png`：普攻命中：巨臂砸中（目标身上），4 帧

巨大的木头手臂砸中目标：一团偏黄绿的白色闪光，几块浅褐色的木屑和尘土往外飞（参考 BA_Hit_flash、BA_Hitorbs）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green-teal nature magic ramp (#FFFFFF, #E6FFE0, #9CF5A8, #3FD98A, #1F9E6E, #0E5A48) and a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C).
Effect: a HEAVY WOODEN BLOW on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares with a pale green rim; 2 a pale green-white burst 10 squares, 4 light brown wood chips flying out at mirrored places; 3 the burst thinner and 12 squares, the chips farther, a little dust; 4 fading chips and dust.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `maokai_fx_p_hit.png`：被动「吸元秘术」强化普攻命中（目标身上），5 帧

吸元秘术这一下额外的魔法伤害：目标身上一团绿色的自然魔法爆开，几缕绿色光丝往外甩，绿色的星形闪光（参考 Passive_Heal_Impact_sparkle、flash_core、P_Soraka_Skin04_R_SparkleGreen）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green-teal nature magic ramp (#FFFFFF, #E6FFE0, #9CF5A8, #3FD98A, #1F9E6E, #0E5A48).
Effect: a NATURE MAGIC BURST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-green flash 5 squares; 2 a green burst 11 squares with a white core, 4 green star sparkles at mirrored places; 3 thin green wisps (curved strands 1 square thick) flung out at mirrored angles, the burst 14 squares; 4 the wisps farther and fading; 5 a few green sparkles.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `maokai_fx_p_heal.png`：被动「吸元秘术」回血（他身上，跟随），6 帧

吸元秘术给他回血：一股绿色的光从他脚下往上卷（两边各一道螺旋的绿色光丝，只画在身体两侧和头顶上方），绿色的十字闪光一闪一闪，最后在头顶散成光点（参考 Passive_Heal_Impact_Vortex、Wisps、Beam、sparkle）。**左右对称**，中间身体位置留空（a huge hunched tree creature 38 squares wide and 40 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green-teal nature magic ramp (#FFFFFF, #E6FFE0, #9CF5A8, #3FD98A, #1F9E6E, #0E5A48).
Effect: A HEALING SURGE round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a huge hunched tree creature 38 squares wide and 40 tall stands in the middle, not drawn): 1 a green glow ring on the ground at its feet (an ellipse 30 squares wide and 7 tall, white inner edge); 2 two green spiralling wisps rising from the ring along both sides of the figure (1-2 squares thick, the inside left empty), 6 green cross sparkles at mirrored places; 3 the wisps at the figure's middle, brightest; 4 the wisps at its top, curling inward over its head; 5 the wisps breaking into green motes above its head, the ring faded; 6 a few rising motes.
Layout: one horizontal row of 6 equal 50:48 cells, image size 4800x768 (each cell 800x768, 16 px a square); centered across, the figure's feet (the ring's middle) 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `maokai_fx_q_cast.png`：Q 荆棘重击：拳头砸地（他脚下，跟随），6 帧

他把巨拳砸进地里：落拳处一道白光，几道白色光刺往上冲，地面裂开一道道裂纹，一圈橄榄褐的尘土和冲击环往外扩（把身边的敌人推开），小石块和泥块往外飞（参考 Q_flash、Q_cas_lightspikes、Q_groundcracks、Q_dustcloud、Q_Cas_aoering、W_dirtbits）。**左右对称**（从斜上方看，地上的环是扁椭圆）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive-brown dust and dirt ramp (#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E) and a green-teal nature magic ramp (#FFFFFF, #E6FFE0, #9CF5A8, #3FD98A, #1F9E6E, #0E5A48).
Effect: A FIST SLAMMED INTO THE GROUND seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares at the ground's middle, 4 white light spikes shooting UP from it (1-2 squares thick, 6-10 tall, at mirrored places); 2 dark ground cracks running out at mirrored angles, an olive-brown dust ring starting (an ellipse 24 squares wide and 7 tall with a pale inner edge); 3 the dust ring 40 wide and 12 tall, small stones and dirt clods flying up and out at mirrored places; 4 the ring 54 wide and 16 tall, thinner, the stones at their highest; 5 dust settling, stones falling; 6 faint dust and the cracks fading.
Layout: one horizontal row of 6 equal 60:28 cells, image size 5760x448 (each cell 960x448, 16 px a square); centered across, the ellipse's middle 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `maokai_fx_q_wave.png`：Q 冲击波：沿地面往前推的冲击（投射物，向前飞），4 帧循环

Q 的冲击波沿着地面往前推出去（会打中前面一段的敌人）：一道往前（画面右边）推进的弧形尘土冲击前沿，前沿亮（白黄色），后面拖着橄榄褐的尘土和碎石，几道小小的绿色荆棘刺（参考 Q_leadingedge、Q_mis_groundcracks、Q_mis_sand、Q_mis_wake_tex）。**朝右画、上下对称**（游戏会把图转到飞行方向）。4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive-brown dust and dirt ramp (#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E).
Effect: A GROUND SHOCKWAVE travelling forward, 4 frames, a seamless loop, pointing RIGHT (the way it flies) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight, so flying left it is drawn upside down): a curved bright front 3 squares thick at the cell's right part (pale yellow-white, an arc bulging to the right, 12 squares tall), behind it (to the left) rolling olive-brown dust and small stones fading out to the left, 4 small green bramble thorns sticking out of the dust at mirrored places (top and bottom); each frame the dust and stones churn (frame 4 flows back into frame 1).
Layout: one horizontal row of 4 equal 20:14 cells, image size 1280x224 (each cell 320x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `maokai_fx_q_hit.png`：Q 命中（目标身上），4 帧

冲击波打中并推开敌人：一团尘土炸开，几块碎石，中间一道白黄色的闪光，几根绿色荆棘刺扎出来（参考 Q_tar_shards、Q_Tar_glow）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an olive-brown dust and dirt ramp (#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E).
Effect: a BRAMBLE SHOCK HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pale yellow-white flash 5 squares; 2 an olive-brown dust burst 10 squares, 4 green thorns jutting out at mirrored angles (1 square thick, 4 long); 3 the dust 14 squares, small stones flying out at mirrored places; 4 settling dust.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `maokai_fx_q_slow.png`：Q 减速（敌人脚下，循环），4 帧

被荆棘重击减速的敌人：脚下缠着几根带刺的绿色荆棘藤，一闪一闪。**左右对称**，只画在脚下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E) and a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C).
Effect: BRAMBLES SLOWING a unit at its feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the ground a tangle of thorny green bramble vines (an ellipse 14 squares wide and 4 tall made of curling vines 1 square thick with small thorns), brown root bits under them; 1 dim, 2 brighter, 3 brightest (the thorns' tips lit), 4 like 2.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered across, the ellipse's middle 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `maokai_fx_w_trail.png`：W 扭曲突刺：化作树根在地下穿行（投射物，向前飞），4 帧循环

他化作一团扭动的树根钻进地里冲向目标（他自己在冲刺时看不见，这一团就是他）：一团纠缠在一起的深褐色树根，根上有青色的发光纹路，往前（画面右边）扭动，前面带起泥块和碎石，后面拖一道浅浅的土痕（参考 W_Tar_Root_TX、w_mis_leadingedge、W_dirtbits、W_rocks）。**朝右画、上下对称**。4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and an olive-brown dust and dirt ramp (#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E).
Effect: A WRITHING MASS OF ROOTS burrowing forward, 4 frames, a seamless loop, pointing RIGHT (the way it flies) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight, so flying left it is drawn upside down): a tangle of dark brown bark roots 16 squares long and 10 tall in the middle (thick roots 2 squares wide twisting round each other, thin glowing teal veins along them, a 1-square dark outline: solid things), the front end (right) a bulge of roots pushing forward with dirt clods and small stones thrown out at mirrored places (top and bottom), behind it (left) a faint trail of dirt; each frame the roots twist a little (frame 4 flows back into frame 1).
Layout: one horizontal row of 4 equal 24:16 cells, image size 1536x256 (each cell 384x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `maokai_fx_w_land.png`：W 冲到目标处：树根从地里冒出（地上，跟随），6 帧

他在目标身边从地里冒出来：地面裂开，一圈粗树根从地里猛地刺出来（左右各几根往上冲，带青色光纹），泥块和碎石往外飞，最后树根缩回地下，留下一点尘土（参考 W_Tar_Root_TX、w_targround、W_rocks、W_dirtbits）。**左右对称**，中间留空（他从中间冒出来）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and an olive-brown dust and dirt ramp (#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E).
Effect: ROOTS BURSTING OUT OF THE GROUND seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the middle 16 squares wide left empty (he rises there); 1 dark cracks opening on the ground (an ellipse 30 squares wide and 8 tall) with a teal glow in them; 2 thick bark roots stabbing UP out of the ground along both sides of the ellipse (2-3 squares thick, 8-14 squares tall, teal veins, a 1-square dark outline), dirt clods flying; 3 the roots at their tallest, stones and dirt at their highest, a dust ring 40 wide; 4 the roots sinking back; 5 the roots half gone, dust settling; 6 faint dust and cracks.
Layout: one horizontal row of 6 equal 48:30 cells, image size 4608x480 (each cell 768x480, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `maokai_fx_w_hit.png`：W 禁锢命中（目标身上），4 帧

扭曲突刺打中目标：一道青色的闪光，几根深褐色的根刺从目标身上往外扎，青色火星（参考 E_tar_hitspikes）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58).
Effect: a ROOT STRIKE on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white flash 5 squares; 2 a teal burst 10 squares with a white core, 4 dark root spikes jutting out at mirrored angles (2 squares thick at the base, 5 long, a dark outline); 3 the spikes withdrawing, teal sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `maokai_fx_root.png`：W / R 禁锢：缠住敌人脚的树根（敌人脚下，循环），4 帧

被扭曲突刺或自然之握禁锢的敌人：几根深褐色的粗树根从地里伸出来缠住他的腿和脚（左右两边各两根往上弯，缠到膝盖高度），根上的青色光纹一明一暗。**左右对称**，中间人的腿留出来（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，只画在他小腿和脚的两边和前面，不要盖住上身）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58).
Effect: ROOTS BINDING a unit's legs, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): from the ground round its feet thick dark bark roots (2 squares thick, a 1-square dark outline) curling up both sides of its legs to knee height (about 12 squares up), two on each side, their tips hooking inward; a ring of disturbed earth on the ground (an ellipse 20 wide and 5 tall); thin teal veins on the roots: 1 dim, 2 brighter, 3 brightest, 4 like 2.
Layout: one horizontal row of 4 equal 22:16 cells, image size 1408x256 (each cell 352x256, 16 px a square); centered across, the feet (the ellipse's middle) 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `maokai_fx_e_lob.png`：E 树苗投掷：飞出去的树苗（投射物，向前飞），4 帧循环

扔出去的树苗在空中翻滚着飞：树苗缩成一团（叶子包着木头身体，一点蓝色眼睛的光），整团是圆的、**上下对称**，后面拖一道淡绿的光痕（参考 E_SaplingTrail_ColorBlur、E_Miss_trail）。4 帧循环（翻滚）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E) and a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58).
Effect: A SAPLING TUMBLING THROUGH THE AIR, 4 frames, a seamless loop, pointing RIGHT (the way it flies) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight, so flying left it is drawn upside down): a round curled-up sapling 7 squares across in the cell's right part (pale brown wood wrapped in green leaves, a 1-square dark outline, one bright blue glint on its middle), a soft pale green trail 4 squares long behind it (left); each frame the leaves are turned a little (a tumbling look) while the whole stays symmetric top to bottom.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `maokai_fx_e_land.png`：E 树苗落地扎根（地上，不跟随），4 帧

树苗落地、扎进土里：第 1 帧一团泥土溅起；第 2 帧树苗从泥土里冒出（正面朝前）；第 3 帧站直，顶上的叶子一抖，几片小叶子飘起；第 4 帧站好，和下面的「站岗」第 1 帧一样。树苗是HIS SAPLING (the attached design picture, 8x: a small wooden seedling with a carved face, one glowing blue eye, a young leaf on top, two leaves as arms, a pointed root)的样子，但**正面朝前**（左右对称：游戏在红色方不会把图镜像），约 8 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E) and a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and an olive-brown dust and dirt ramp (#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E).
Effect: A SAPLING LANDING AND TAKING ROOT on the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a dirt splash on the ground (an ellipse 12 squares wide and 4 tall, dirt clods flying up at mirrored places); 2 HIS SAPLING (the attached design picture, 8x: a small wooden seedling with a carved face, one glowing blue eye, a young leaf on top, two leaves as arms, a pointed root) seen FROM THE FRONT: its face looking at the viewer, symmetric left to right, about 8 squares wide and 12 tall, in its own colours (pale brown and yellow-green wood, a bright blue eye glint, green leaves) with a 1-square dark outline (it is a solid thing) rising halfway out of the soil; 3 the sapling standing, its top leaf shaking, 4 tiny leaves floating up at mirrored places; 4 the sapling standing still exactly as in the first frame of the next sheet (e_idle). Its root tip on the cell's bottom row.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `maokai_fx_e_idle.png`：E 树苗站岗（地上，不跟随，循环），4 帧

树苗插在地上戒备，最多站 12 秒：HIS SAPLING (the attached design picture, 8x: a small wooden seedling with a carved face, one glowing blue eye, a young leaf on top, two leaves as arms, a pointed root)，**正面朝前**、左右对称。4 帧循环：顶上的叶子轻轻晃，身体上下起伏 1 格，蓝眼睛一亮一暗，脚下一小圈青色的光（参考 E_TEAMID_Ring）。第 4 帧接得回第 1 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E) and a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58).
Effect: A SAPLING STANDING GUARD on the ground, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): HIS SAPLING (the attached design picture, 8x: a small wooden seedling with a carved face, one glowing blue eye, a young leaf on top, two leaves as arms, a pointed root) seen FROM THE FRONT: its face looking at the viewer, symmetric left to right, about 8 squares wide and 12 tall, in its own colours (pale brown and yellow-green wood, a bright blue eye glint, green leaves) with a 1-square dark outline (it is a solid thing), standing with its root tip on the cell's bottom row; a faint teal ring on the ground round its root (an ellipse 10 squares wide and 3 tall); 1 still; 2 its body a square lower, its top leaf tilted, the eye brighter; 3 like 1 with the eye brightest; 4 like 2 with the eye dimmer (frame 4 flows back into frame 1).
Layout: one horizontal row of 4 equal 14:16 cells, image size 896x256 (each cell 224x256, 16 px a square); centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `maokai_fx_e_burst.png`：E 树苗扑向敌人爆炸（敌人身上，不跟随），6 帧

有敌人靠近，树苗跳起来扑到他身上炸开：第 1 帧树苗（正面朝前）跳在敌人头顶上方；第 2 帧往下扑，身上裂缝发青光；第 3 帧一个青绿色的魔法爆炸（白芯，外面一圈青色的爆炸环，参考 E_BigExplosion_Blast_Ring、Maokai_base_E_tar_clouds）；第 4 帧爆炸最大（扁圆形，约 44 格宽），木屑、叶子往外飞；第 5 帧变淡，叶子飘落；第 6 帧几片叶子和光点。**左右对称**，中间敌人的位置在爆炸里（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and a green-teal nature magic ramp (#FFFFFF, #E6FFE0, #9CF5A8, #3FD98A, #1F9E6E, #0E5A48) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E) and a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C).
Effect: A SAPLING POUNCING AND EXPLODING on a unit, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): 1 HIS SAPLING (the attached design picture, 8x: a small wooden seedling with a carved face, one glowing blue eye, a young leaf on top, two leaves as arms, a pointed root) seen FROM THE FRONT: its face looking at the viewer, symmetric left to right, about 8 squares wide and 12 tall, in its own colours (pale brown and yellow-green wood, a bright blue eye glint, green leaves) with a 1-square dark outline (it is a solid thing) leaping, high over the champion's head (near the cell's top); 2 the sapling diving down onto it, glowing teal cracks across its body; 3 a teal-green magic explosion at the champion's middle, a white core 10 squares, a bright teal blast ring round it (an ellipse 28 squares wide and 18 tall); 4 the blast at its biggest (44 wide and 26 tall), wood chips and green leaves flying out at mirrored places; 5 the blast faded, leaves drifting down; 6 a few leaves and teal motes.
Layout: one horizontal row of 6 equal 48:40 cells, image size 4608x640 (each cell 768x640, 16 px a square); centered across, the champion's feet 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `maokai_fx_e_hit.png`：E 爆炸命中（敌人身上），4 帧

树苗的爆炸炸到附近的敌人：一团青绿色的闪光，几片叶子和木屑（参考 Maokai_base_E_tar_clouds、E_Sapling_Bits）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E).
Effect: a SAPLING BLAST HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white flash 5 squares; 2 a teal-green burst 10 squares with a white core, 4 green leaves at mirrored places; 3 the burst 14 squares and thinner, leaves and wood chips flying out; 4 fading leaves.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `maokai_fx_e_slow.png`：E 减速（敌人脚下，循环），4 帧

被树苗炸到的敌人减速：脚下一摊发青光的黏液和几片落叶，一明一暗。**左右对称**，只画在脚下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E).
Effect: STICKY SAP SLOWING a unit at its feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the ground a puddle of glowing teal sap (an ellipse 14 squares wide and 4 tall) with 4 small green leaves on it at mirrored places; 1 dim, 2 brighter, 3 brightest, 4 like 2.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered across, the ellipse's middle 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `maokai_fx_r_cast.png`：R 自然之握：两臂砸地召唤（他脚下，跟随），6 帧

他两臂砸地召唤荆棘墙：落点一道青白光，地面裂开一圈发青光的裂纹（参考 R_Crater_01、R_Trail_Cracks_Glow），一圈尘土和碎石往外炸开（参考 R_rock_debris、R_clouds），几根带刺的树根从裂缝里冒头。**左右对称**（地上的圈是扁椭圆）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and an olive-brown dust and dirt ramp (#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E) and a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C).
Effect: A GROUND-SHAKING SUMMONING seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white flash 12 squares at the ground's middle; 2 a ring of glowing teal cracks opening on the ground (an ellipse 30 squares wide and 9 tall, the cracks jagged lines 1 square thick), dust bursting; 3 the cracks out to 46 wide, grey-brown rock debris and dust flying out at mirrored places, 4 short thorny root tips poking up out of the cracks (dark bark, a dark outline); 4 a dust ring 60 wide, the debris at its highest; 5 dust settling, the cracks' glow dimmer; 6 faint glowing cracks.
Layout: one horizontal row of 6 equal 64:30 cells, image size 6144x480 (each cell 1024x480, 16 px a square); centered across, the ellipse's middle 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `maokai_fx_r_wall.png`：R 自然之握：慢慢往前推进的荆棘墙（投射物，向前飞），4 帧循环

一道很宽的荆棘墙贴着地面慢慢往前（画面右边）推：墙是**竖着的一条宽带**（画面里竖着约 56 格长、10 格宽：游戏里它横在前进方向上，所以朝右飞的时候是竖的），由纠缠的带刺树根和荆棘组成（深褐色树根、绿色荆棘、青色发光的刺尖），墙的前沿（右边）有一点尘土翻起，后面（左边）拖一道发青光的裂纹（参考 R_Root_A、Maokai_Skin04_R_Root_A、R_Trail_Cracks_Glow、R_sparklines）。**朝右画、上下对称**（游戏会把图转到飞行方向）。4 帧循环（树根扭动、刺尖一闪一闪）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E) and a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and an olive-brown dust and dirt ramp (#F4ECD8, #D8C69C, #B09A6A, #857048, #5A4A30, #352C1E).
Effect: A WALL OF BRAMBLES advancing, 4 frames, a seamless loop, pointing RIGHT (the way it flies) and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight, so flying left it is drawn upside down): a tall vertical band in the middle of the cell, 10 squares wide and 56 squares tall, made of thick twisting dark bark roots (2-3 squares thick, a 1-square dark outline: solid things) woven with green thorny bramble vines, thorn tips glowing bright teal all along it; at its right edge (the front) dust and dirt clods kicked up; behind it (left) a thin trail of glowing teal ground cracks 4 squares long; each frame the roots writhe and different thorn tips glint (frame 4 flows back into frame 1).
Layout: one horizontal row of 4 equal 18:60 cells, image size 1152x960 (each cell 288x960, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `maokai_fx_r_hit.png`：R 荆棘墙撞到敌人（敌人身上），4 帧

荆棘墙撞到敌人：青色的闪光，几根带刺的树根从下往上扎（参考 E_tar_hitspikes、R_sparklines），绿色和青色的碎光。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright teal glow ramp (#FFFFFF, #D8FFF8, #7CF2E4, #22C9C0, #138A92, #0A4A58) and a bark and root ramp (#E8B888, #C08458, #8E5A3C, #643C2C, #42282A, #24161C) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E).
Effect: a BRAMBLE IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a teal-white flash 6 squares; 2 a teal burst 11 squares with a white core, 4 thorny root spikes stabbing up and out at mirrored angles (dark bark, a dark outline, glowing teal tips); 3 the spikes withdrawing, teal and green sparks at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `maokai_fx_r_haste.png`：R 撞到英雄后的加速（他脚下，循环），4 帧

自然之握撞到敌方英雄后他跑得更快：脚下一圈绿色的风，几片叶子往后飘（左右两边一样）。**左右对称**，只画在脚下（a huge hunched tree creature 38 squares wide and 40 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green-teal nature magic ramp (#FFFFFF, #E6FFE0, #9CF5A8, #3FD98A, #1F9E6E, #0E5A48) and a leaf and moss green ramp (#F2FFB0, #C8EA5A, #8CC23C, #5A9030, #36602A, #1E3A1E).
Effect: A NATURE'S HASTE at a huge figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a huge hunched tree creature 38 squares wide and 40 tall stands in the middle, not drawn): a green wind ring on the ground (an ellipse 34 squares wide and 7 tall, 1 square thick, brighter on its near side), 6 small green leaves riding it at mirrored places, each frame a little farther round (frame 4 flows back into frame 1).
Layout: one horizontal row of 4 equal 40:12 cells, image size 2560x192 (each cell 640x192, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `maokai_fx_a_hit` | view_effects `league_maokai_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `maokai_fx_p_hit` | view_effects `league_maokai_p_hit`（跟随，画在人物上面；左右对称） | 16 |
| `maokai_fx_p_heal` | view_effects `league_maokai_p_heal`（跟随，画在他上面 z 2；左右对称；大图表） | 50 × 48 |
| `maokai_fx_q_cast` | view_effects `league_maokai_q_cast`（跟随，画在人物下面 z -1；左右对称；大图表） | 60 × 28 |
| `maokai_fx_q_wave` | view_projectiles `league_maokai_q_wave`（画在人物下面 z -1；**朝右画、上下对称**：图跟着飞行方向转；大图表） | 20 × 14 |
| `maokai_fx_q_hit` | view_effects `league_maokai_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `maokai_fx_q_slow` | view_buffs `league_maokai_q_s1`（跟随，画在人物下面；左右对称；循环） | 16 × 8 |
| `maokai_fx_w_trail` | view_projectiles `league_maokai_w_trail`（画在人物下面 z -1；**朝右画、上下对称**；大图表） | 24 × 16 |
| `maokai_fx_w_land` | view_effects `league_maokai_w_land`（跟随，画在人物下面 z -1；左右对称；大图表） | 48 × 30 |
| `maokai_fx_w_hit` | view_effects `league_maokai_w_hit`（跟随，画在人物上面；左右对称） | 14 |
| `maokai_fx_root` | view_buffs `league_maokai_w_bound` 和 `league_maokai_r_bound`（同一张图，跟随，画在人物上面；左右对称；循环） | 22 × 16 |
| `maokai_fx_e_lob` | view_projectiles `league_maokai_e_lob`（画在人物上面；**朝右画、上下对称**：图跟着飞行方向转） | 12 × 12 |
| `maokai_fx_e_land` | view_effects `league_maokai_e_land`（不跟随，画在人物下面 z 0；左右对称） | 18 × 18 |
| `maokai_fx_e_idle` | view_effects `league_maokai_e_idle`（不跟随，画在人物下面 z 0；左右对称；每 0.5 秒重放一次，所以 4 帧要能首尾相接） | 14 × 16 |
| `maokai_fx_e_burst` | view_effects `league_maokai_e_burst`（不跟随，画在人物上面 z 2；左右对称；大图表） | 48 × 40 |
| `maokai_fx_e_hit` | view_effects `league_maokai_e_hit`（跟随，画在人物上面；左右对称） | 14 |
| `maokai_fx_e_slow` | view_buffs `league_maokai_e_slow`（跟随，画在人物下面；左右对称；循环） | 16 × 8 |
| `maokai_fx_r_cast` | view_effects `league_maokai_r_cast`（跟随，画在人物下面 z -1；左右对称；大图表） | 64 × 30 |
| `maokai_fx_r_wall` | view_projectiles `league_maokai_r_wall`（画在人物下面 z -1；**朝右画、上下对称**：图跟着飞行方向转，斜着放就是斜的墙；大图表） | 18 × 60 |
| `maokai_fx_r_hit` | view_effects `league_maokai_r_hit`（跟随，画在人物上面；左右对称） | 16 |
| `maokai_fx_r_haste` | view_buffs `league_maokai_r_h2`（跟随，画在人物下面 z -1；左右对称；循环） | 40 × 12 |

- 两张表：`asset/league/effects/league_maokai_fx`（小的）和 `league_maokai_big`（p_heal、q_cast、q_wave、w_trail、w_land、e_burst、r_cast、r_wall、r_haste），tag = 名字（build_maokai.py 的 views；`q_slow` 绑 buff `q_s1`，`r_haste` 绑 `r_h2`，`root` 绑 `w_bound` 和 `r_bound`）。
- 投射物（`e_lob`、`q_wave`、`w_trail`、`r_wall`）朝右、上下对称；`e_land`、`e_idle`、`e_burst` 不跟随（地上的晚播画面）；`e_idle` 每 30 tick 重放一次（e_link），4 帧共 0.5 秒。
- 用 `pixel_1x/` 切格（import_nasus_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。
