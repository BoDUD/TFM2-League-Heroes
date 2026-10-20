# 荆棘之兴 婕拉：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型和动作已定（`design/zyra_idle.png`：3/4 正面朝右的植物女人，一大蓬深红-品红的头发、两只黄绿色的叶片角，绿叶抹胸和短裤，深紫色带刺的长腿，手腕上垂着品红色的鞭藤）。她在游戏里是**高清**的（每个游戏格子里 1.7×1.7 个细像素），44 格高、44 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/zyra_size.png`：她的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/zyra_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里婕拉自己的特效贴图和她的三种植物（荆棘喷射者、藤蔓鞭击者、种子），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的魔法是品红-粉红色的刺**，**绿色的叶子和汁液**，长在**深紫色的藤蔓**上。
> - **植物是她的标志**：Q 落点长出荆棘喷射者（粉红花苞头的植物），E 落点长出藤蔓鞭击者（带矛尖的长藤），大招是一整片扭曲的密林。植物在地上活 5 秒，图里画出**长出来 → 站着摇 → 出手 → 枯萎**，Claude 按时间拼成一条长动画。
> - **特效要亮**：每团光都要有白色或最亮一档的芯；深紫色的藤蔓要有偏紫的亮边，暗底上一眼能看见。
> - **实心的东西（植物、藤蔓、树根、刺）有 1 格近黑描边**，像人物一样；**光、汁液、闪光、符文环没有描边**。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、地上、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）；**植物从正面画**（正对着看的人，摇摆的那几帧左右各一次）。**弹道图**（种子、吐的刺、藤蔓）**朝右飞、后面在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `zyra_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/zyra_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/zyra_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 甩出一颗荆棘种子 | `a_seed` · `a_hit` |
| 技能 1 = Q「致命棘刺」 | 目标点地面炸出棘刺，种子长成荆棘喷射者，每秒吐刺打一个敌人 | `q_burst` · `q_hit` · `t_plant` · `t_hit` |
| 技能 2 = E「缠绕之根」 | 贯穿地面的藤蔓禁锢一条线上的敌人，种子长成藤蔓鞭击者，每秒抽打并减速 | `e_roots` · `e_bound` · `v_plant` · `v_hit` · `v_slow` |
| 大招「绞杀之藤」 | 目标点长出扭曲的密林，打中里面的敌人，2 秒后合拢把还在里面的敌人击飞 | `r_thicket` · `r_hit` · `r_knock` |
| 附加包（被动「荆棘花园」） | 种子落在她身边的地上，Q / E 落在种子旁边多长一株植物，植物吐出看得见的刺 | `s_seed` · `t_spit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、汁液、闪光、符文环没有黑描边**；**植物、藤蔓、树根、刺有 1 格近黑描边**。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 品红-粉红的刺和花：`#FFFFFF`、`#FFD6EE`、`#FF8AD0`、`#F23FA4`、`#B8187A`、`#6E0C4A`；
  - 叶子和藤蔓的绿：`#F4FFD6`、`#CDF27A`、`#93CF44`、`#57902E`、`#2E5622`、`#172E14`；
  - 深紫色的藤蔓、树根、植物的茎：`#E8CCFF`、`#B888E8`、`#8048B8`、`#55267E`、`#34144E`、`#1C0A2C`；
  - 亮绿色的汁液光：`#FFFFFF`、`#F6FFD2`、`#DCF58A`、`#A6DA48`；
- 打中、爆发居中画，不旋转；地面上的圆（棘刺的藤蔓、密林的符文环、减速的汁液）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 55000，Q 的爆炸半径 22000，大招密林的半径 32000）。

### 1. `zyra_fx_a_seed.png`：普攻：荆棘种子（弹道，循环），4 帧

她普攻甩出去的一颗荆棘种子：粉红色的小种球，两片小绿叶，后面拖一小段粉红色的火花尾迹（参考 w_seed、aa_mis_trail、flare_pink）。**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A) and a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14).
Effect: A THORNY SEED, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): at the right a magenta-pink seed bulb 4 squares across with a 1-square near-black outline and a white glint, two tiny green leaf flicks at its back (one above, one mirrored below); behind it to the left a short tapering pink spark trail 4 squares long; each frame the trail flickers (symmetric top and bottom).
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); the bulb's middle on the cell's middle row, 3 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `zyra_fx_a_hit.png`：普攻：打中目标，3 帧

种子打中目标：一团粉红色的小闪光，几片碎叶和绿色汁液溅开（参考 flare_pink、leaves、poison_spatter）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A), a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: A SMALL SEED HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink-white four-pointed flash 6 squares across; 2 the flash 9 across with 4 small green leaf bits and sap drops at mirrored places; 3 only the leaf bits further out, fading.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `zyra_fx_q_burst.png`：Q 致命棘刺：目标点地面炸出棘刺（地上，不跟随），6 帧

Q 落点：先是一片绿色的藤蔓在地上铺开（一个扁的椭圆），裂缝里透出粉红色的光，然后一簇又高又尖的粉红色棘刺从藤蔓里猛地刺出来，带着绿色汁液溅起，最后棘刺缩回、藤蔓碎叶散掉（参考 q_vinesbase、q_spines、q_leaves、ground_cracks）。**左右对称**，6 帧。范围约 44 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A), a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14), a dark purple vine ramp (#E8CCFF, #B888E8, #8048B8, #55267E, #34144E, #1C0A2C) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: DEADLY SPINES bursting from the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 thick green vines spreading flat across the ground (a flat ellipse 30 squares wide and 8 tall); 2 the vines covering an ellipse 44 wide and 13 tall, pink light glowing in the cracks between them; 3 a cluster of 9 tall magenta-pink thorn spikes bursting up out of the vines at mirrored places (the middle one 22 squares tall, the outer ones shorter), each spike with a 1-square near-black outline; 4 the spikes at full height, green sap splashing off them; 5 the spikes sinking back to half height; 6 only scattered vine bits and leaves on the ground, fading.
Layout: one horizontal row of 6 equal 48:30 cells, image size 4608x480 (each cell 768x480, 16 px a square); centered across, the ellipse's middle 7 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `zyra_fx_q_hit.png`：Q：棘刺扎中目标，4 帧

棘刺扎中目标：粉红色的尖刺从下往上扎了一下，闪一下光，绿色汁液溅开（参考 poison_spike、flare_pink）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: A SPINE STAB, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 three sharp pink thorn spikes stabbing up from the bottom (the middle one 8 tall); 2 a pink-white flash 9 across where they meet, green sap drops flying out; 3 the flash 13 across, the spikes gone; 4 only fading sap drops.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `zyra_fx_t_plant.png`：荆棘喷射者：种子长出来、站着摇、吐刺、枯萎（地上，不跟随），10 帧

Q 长出来的植物（英雄联盟的荆棘喷射者，附图里的 plant_thorn_spitter）：一株深紫色的弯茎植物，顶上一个**粉红色的大花苞头**，花苞外面包着绿色的萼片，根部是一圈深紫色的叶子。**从正面画**（花苞头正对着看的人），10 帧：1–3 从地上的种子长出来（种子裂开、冒出芽、长成整株）；4–7 站着轻轻摇摆（左、中、右、中）；8 吐刺（花苞张开、里面露出粉红色的光）；9–10 枯萎缩回地里。实心的植物有 1 格近黑描边，像人物一样。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple vine ramp (#E8CCFF, #B888E8, #8048B8, #55267E, #34144E, #1C0A2C), a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A) and a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14).
Effect: A THORN SPITTER PLANT, drawn FROM THE FRONT, facing the viewer, its stalk upright in the middle (the game never mirrors it: it must look right on both sides), 10 frames: 1 a pink seed bulb on the ground cracking open; 2 a dark purple sprout 8 squares tall with a small closed bud; 3 the grown plant - a dark purple stalk 14 squares tall rising from a ring of dark purple leaves at the ground, on top a big magenta-pink flower-bud head 8 squares across wrapped in green sepals, facing the viewer; 4 to 7 the plant swaying gently (the head a square left, back in the middle, a square right, back in the middle); 8 the bud opening wide, pink light glowing inside it (spitting); 9 the plant drooping, its head hanging; 10 it shrinking back into a small heap of withered leaves. 1-square near-black outline round the solid plant.
Layout: one horizontal row of 10 equal 20:26 cells, image size 3200x416 (each cell 320x416, 16 px a square); centered across, its leaves' bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `zyra_fx_t_hit.png`：荆棘喷射者：吐的刺打中，3 帧

植物吐的刺打中敌人：一下小小的粉红色刺爆（参考 poison_spike）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: A SMALL THORN HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink flash 4 across; 2 4 tiny pink thorn shards flying out at mirrored diagonals; 3 only two fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `zyra_fx_t_spit.png`：荆棘喷射者：吐出来的刺（弹道，附加包用，循环），2 帧

附加包里植物吐出去的一根刺：一根细长的粉红色尖刺，后面一点点火花。**朝右飞，上下严格对称**，2 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A).
Effect: A FLYING THORN, 2 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a slim magenta-pink spine 6 squares long, pointed at the right, 1-square near-black outline, a 2-square spark behind it that flickers.
Layout: one horizontal row of 2 equal 8:4 cells, image size 256x64 (each cell 128x64, 16 px a square); the spine on the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `zyra_fx_e_roots.png`：E 缠绕之根：贯穿地面的藤蔓（弹道，循环），4 帧

E 放出去的藤蔓：地面裂开往前窜，裂缝里冒出一丛丛带刺的深紫色藤蔓和绿叶，最前面的藤蔓头张开（参考 rootgrasp、props_vines_green、ground_cracks）。**朝右窜，后面在左边，上下严格对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple vine ramp (#E8CCFF, #B888E8, #8048B8, #55267E, #34144E, #1C0A2C), a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14) and a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A).
Effect: GRASPING ROOTS tearing along the ground, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a band of thorny dark purple vines and green leaves 22 squares long and 8 tall, thickest at the right where a cluster of vine tips curls open with pink thorns, thinning to a crack with small sprouts at the left; each frame the vines writhe and new sprouts pop up (symmetric top and bottom). 1-square near-black outline round the solid vines.
Layout: one horizontal row of 4 equal 22:10 cells, image size 1408x160 (each cell 352x160, 16 px a square); the band on the cell's middle row, its head 2 squares from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `zyra_fx_e_bound.png`：E：被藤蔓缠住脚（敌人脚下，循环），4 帧

被禁锢的时候：地上冒出几根深紫色带刺的藤蔓缠住敌人的脚和小腿，藤蔓尖上冒绿光（参考 rootgrasp、props_vines_green）。**只画藤蔓（人站在中间不画）**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple vine ramp (#E8CCFF, #B888E8, #8048B8, #55267E, #34144E, #1C0A2C), a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: ROOTS BINDING a unit's legs, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a champion stands in the middle, not drawn: about 16 squares wide and 36 tall, only the bottom 14 squares of the cell used): 4 thorny dark purple vines rising from the ground at both sides of the legs and coiling across in front of them up to 12 squares high, small green leaves on them, glowing green tips; each frame the vines tighten and loosen a square. 1-square near-black outline round the solid vines.
Layout: one horizontal row of 4 equal 20:16 cells, image size 1280x256 (each cell 320x256, 16 px a square); centered across, the roots' bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `zyra_fx_v_plant.png`：藤蔓鞭击者：种子长出来、站着摇、抽打、枯萎（地上，不跟随），10 帧

E 长出来的植物（英雄联盟的藤蔓鞭击者，附图里的 plant_vine_lasher）：一根深紫色带刺的长藤茎从一丛深紫色的叶子里竖起来，顶端是一个粉红色的矛尖，茎上一排粉红色的刺。**从正面画**，10 帧：1–3 从种子长出来；4–7 站着摇摆（左、中、右、中）；8 抽打（藤茎猛地卷成一个 S 形、矛尖一闪）；9–10 枯萎缩回地里。实心的植物有 1 格近黑描边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple vine ramp (#E8CCFF, #B888E8, #8048B8, #55267E, #34144E, #1C0A2C), a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A) and a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14).
Effect: A VINE LASHER PLANT, drawn FROM THE FRONT, facing the viewer, its stalk upright in the middle (the game never mirrors it: it must look right on both sides), 10 frames: 1 a pink seed bulb on the ground cracking open; 2 a dark purple sprout 9 squares tall; 3 the grown plant - a thorny dark purple vine stalk 22 squares tall rising from a clump of dark purple leaves at the ground, a row of small pink thorns along it, a magenta-pink spearhead tip at the top; 4 to 7 the stalk swaying (its top 2 squares left, back in the middle, 2 squares right, back in the middle); 8 the stalk whipping into an S-curve, its tip flashing pink-white (lashing); 9 the stalk drooping over; 10 it shrinking back into a small heap of withered leaves. 1-square near-black outline round the solid plant.
Layout: one horizontal row of 10 equal 18:28 cells, image size 2880x448 (each cell 288x448, 16 px a square); centered across, its leaves' bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `zyra_fx_v_hit.png`：藤蔓鞭击者：抽中目标，3 帧

藤蔓抽中敌人：一道交叉的绿色鞭痕闪一下，几片碎叶（参考 flash_green_sharp、leaves）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: A VINE LASH HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two crossing bright green lash streaks (an X 10 wide); 2 the X flashing green-white with 4 leaf bits flying out at mirrored places; 3 only the leaf bits, fading.
Layout: one horizontal row of 3 equal 14:12 cells, image size 672x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `zyra_fx_v_slow.png`：藤蔓鞭击者：被减速（敌人脚下，循环），4 帧

被藤蔓鞭击者减速：敌人脚下一小滩黏糊糊的绿色汁液，冒出几根细细的小藤须（参考 slime、poison_dots）。**只画在脚下的地面上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: STICKY SAP at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat green sap ellipse 16 wide and 3 tall with bright glints, 3 tiny curling vine tendrils (2-3 squares) rising from it at mirrored places; each frame the tendrils curl and the glints move.
Layout: one horizontal row of 4 equal 18:6 cells, image size 1152x96 (each cell 288x96, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `zyra_fx_r_thicket.png`：R 绞杀之藤：扭曲的密林（地上，不跟随），10 帧

大招：目标点的地上先亮起一圈绿色的符文环，里面藤蔓疯长，长成一片扭曲的带刺密林（深紫色的藤蔓纠缠成一圈矮丛，上面开着粉红色的刺和花苞），在里面扭动两秒，然后所有藤蔓**猛地往上一收、像笼子一样合拢**（把里面的人击飞），最后散成碎叶（参考 rootgrasp、e_groundring、plant_props、buf_enrage）。**左右对称**，10 帧。范围约 64 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple vine ramp (#E8CCFF, #B888E8, #8048B8, #55267E, #34144E, #1C0A2C), a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14), a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: STRANGLETHORNS, a twisted thicket, 10 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a bright green rune ring on the ground (a flat ellipse 64 squares wide and 20 tall) with 4 small leaf sigils at mirrored places; 2 green vines sprawling inside it; 3 dark purple thorny vines rising all round the ring into a low tangled thicket 10 squares tall; 4 to 6 the thicket writhing (3 frames that loop: the vines twist a square, pink thorns and buds on them pulse); 7 the vines whipping upward and inward like a closing cage, 30 squares tall in the middle; 8 the cage snapping shut with a burst of pink-white light at its top; 9 the vines falling apart; 10 only leaves and a fading ring. 1-square near-black outline round the solid vines (none round light or rings).
Layout: one horizontal row of 10 equal 70:44 cells, image size 11200x704 (each cell 1120x704, 16 px a square); centered across, the ellipse's middle 10 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `zyra_fx_r_hit.png`：R：密林打中，4 帧

密林长出来时打中里面的敌人：几根带刺的藤蔓抽过去，粉红绿色的闪光（参考 flare_pink、flash_green_sharp）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A), a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: A THORN BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink-white flash 7 across; 2 4 thorny vine lashes crossing it at mirrored diagonals; 3 a green sap ring 14 across, the lashes fading; 4 only sap drops.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `zyra_fx_r_knock.png`：R：藤蔓把敌人往上掀（他身上），4 帧

密林合拢、把敌人击飞：一丛带刺的深紫色藤蔓从他脚下猛地往上冲，藤蔓尖上闪粉红色的光（参考 rootgrasp、poison_spike）。**人站在中间不画**，**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark purple vine ramp (#E8CCFF, #B888E8, #8048B8, #55267E, #34144E, #1C0A2C), a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A) and a bright sap-green glow ramp (#FFFFFF, #F6FFD2, #DCF58A, #A6DA48).
Effect: VINES SURGING UP under a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a champion stands in the middle, not drawn: about 16 squares wide and 36 tall, its body area left EMPTY): 1 vine tips breaking the ground at both sides of its feet; 2 thorny dark purple vines shooting up both sides to 18 squares; 3 the vines at 24 squares, their pink tips flashing, curling in over its head; 4 the vines falling away, sap drops. 1-square near-black outline round the solid vines.
Layout: one horizontal row of 4 equal 16:26 cells, image size 1024x416 (each cell 256x416, 16 px a square); centered across, the vines' bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `zyra_fx_s_seed.png`：种子：落在地上的种子（地上，附加包用，循环），4 帧

附加包里掉在地上的种子（英雄联盟 W 的种子，附图里的 plant_seed）：一颗粉红色的种球，下面几片绿叶托着，一闪一闪地发光。**左右对称**，4 帧循环（1 秒一轮）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glow, sap splashes, dust or rings; solid plants, vines, roots and thorns DO have a 1-square near-black outline like a character, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a magenta-pink thorn ramp (#FFFFFF, #FFD6EE, #FF8AD0, #F23FA4, #B8187A, #6E0C4A) and a leaf-green ramp (#F4FFD6, #CDF27A, #93CF44, #57902E, #2E5622, #172E14).
Effect: A SEED ON THE GROUND, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a magenta-pink seed bulb 5 squares across, closed like a bud, cupped by 4 green leaves at the ground, 1-square near-black outline; each frame a soft pink glow round it pulses (1 square wider on frames 2 and 3).
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); centered across, the leaves' bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `zyra_fx_a_seed` | view_projectiles `league_zyra_a_seed`（跟着弹道转向；上下对称） | 10 × 8 |
| `zyra_fx_a_hit` | view_effects `league_zyra_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 12 × 12 |
| `zyra_fx_q_burst` | view_effects `league_zyra_q_burst`（不跟随，画在人物下面 z -1；左右对称；大图表） | 48 × 30 |
| `zyra_fx_q_hit` | view_effects `league_zyra_q_hit`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 14 |
| `zyra_fx_t_plant` | view_effects `league_zyra_t_plant`（不跟随，画在人物下面 z 0；左右对称；大图表；活 5 秒） | 20 × 26 |
| `zyra_fx_t_hit` | view_effects `league_zyra_t_hit`（跟随目标，画在人物上面 z 2；左右对称） | 10 × 10 |
| `zyra_fx_t_spit` | view_projectiles `league_zyra_t_spit`（附加包：种子长出来的植物吐的刺；跟着弹道转向；上下对称） | 8 × 4 |
| `zyra_fx_e_roots` | view_projectiles `league_zyra_e_roots`（跟着弹道转向；上下对称） | 22 × 10 |
| `zyra_fx_e_bound` | view_buffs `league_zyra_e_bound`（跟随，画在人物上面 z 3；左右对称；循环；禁锢期间） | 20 × 16 |
| `zyra_fx_v_plant` | view_effects `league_zyra_v_plant`（不跟随，画在人物下面 z 0；左右对称；大图表；活 5 秒） | 18 × 28 |
| `zyra_fx_v_hit` | view_effects `league_zyra_v_hit`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 12 |
| `zyra_fx_v_slow` | view_buffs `league_zyra_v_slow`（跟随，画在人物下面 z -1；左右对称；循环） | 18 × 6 |
| `zyra_fx_r_thicket` | view_effects `league_zyra_r_thicket`（不跟随，画在人物下面 z -1；左右对称；大图表；约 3 秒） | 70 × 44 |
| `zyra_fx_r_hit` | view_effects `league_zyra_r_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `zyra_fx_r_knock` | view_effects `league_zyra_r_knock`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 26 |
| `zyra_fx_s_seed` | view_effects `league_zyra_s_seed`（附加包：她身边掉在地上的种子，每 1 秒重放；不跟随；左右对称） | 10 × 8 |

- 两张表：`asset/league/effects/league_zyra_fx`（小的）和 `league_zyra_big`（q_burst、t_plant、v_plant、r_thicket），tag = 名字（build_zyra.py 的 views；s_seed、t_spit 是附加包副本的 views）。
- 弹道图（a_seed、t_spit、e_roots）断言上下对称，其余断言左右对称（植物的摇摆帧除外）；q_burst、t_plant、v_plant、r_thicket 不跟随（落点）。
- 植物的长 tag：长出来 3 帧（共约 0.3 秒，第一次出手前），之后每 1 秒一轮：出手帧 + 4 帧摇摆，最后 2 帧枯萎，总长 = 植物活的时间（build_zyra.P 的 t_life / v_life）；密林的 tag：符文环、长出来、扭动循环到 r_knock、合拢、散掉。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（实心植物的描边保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
