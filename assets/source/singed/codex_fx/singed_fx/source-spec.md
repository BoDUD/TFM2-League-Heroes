# 炼金术士 辛吉德：给 Codex 的特效提示词（第 3 步）

> **这一份是 14 张特效图。** 造型已定（`design/singed_design.png`：又高又瘦的驼背光头老头，灰绿蒙脸布，红夹克金扣带，带刺的护肩，背上发光的亮绿药罐，近侧手臂上一块带刺的灰绿盾板，远侧手里一个绿药瓶，深蓝细腿，大红棕靴子）。他在游戏里是**高清**的（每个游戏格子里约 1.4×1.4 个细像素），45 格高、32 格宽（高×宽，连药罐）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/singed_size.png`：辛吉德放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里辛吉德自己的特效贴图（大多是灰度或绿色的形状），按用在我们哪张特效分好了行，只在本地用。**辛吉德是疯狂炼金术士**：毒雾是**一团团圆圆的毒绿色烟**（上面亮黄绿、下面暗绿），强力粘胶是**浅琥珀黄的黏胶**（有光泽、拉丝、冒泡、几块黄色的结晶碎片），疯狂药剂是**黄绿色的药剂泡沫和蒸汽**，重伤是**紫色**；不要火、不要电、不要光滑的霓虹光束。
> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。
> - **毒雾、黏胶、蒸汽、冲击波、尘土都没有黑描边**（用它自己最深的一档）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`w_vial`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - **持续的画面**（毒雾 3 秒、地上的胶 3 秒、粘住 1 秒）只画几帧：开头、中间循环的几帧、结尾，Claude 导入时按时长拉开循环。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `singed_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/singed_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/singed_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 用盾板砸 | `a_hit` |
| 被动「剧毒踪迹」+「剧毒冲流」 | 走过的地方一直留下毒雾，踩在里面的敌人持续掉血；从敌方英雄身边冲过时加速 | `q_cloud` · `p_fast` · `haste` |
| 技能 1 =「过肩摔」 | 抓住敌人从肩膀上扔到身后；落进强力粘胶里就被粘住（禁锢） | `e_hit` · `e_land` · `e_root` |
| 技能 2 =「强力粘胶」 | 扔出一瓶粘胶，地上一大摊胶，里面的敌人减速、不能位移 | `w_vial` · `w_glue` · `slow` |
| 大招 =「疯狂药剂」 | 喝下药剂，25 秒内各项属性大涨，毒雾更大更浓、附带重伤 | `r_drink` · `r_aura` · `q_cloud_r` · `gw` |

连招：**粘胶 → 过肩摔**（把人扔进胶里粘住），**过肩摔 → 加速**（扔完马上冲过去），**喝药 → 马上扔粘胶**，**药效期间毒雾变强**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**毒雾、黏胶、蒸汽、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的亮点。
- 颜色（按每条写的用）：
  - 毒雾·毒绿：`#F2FFB4`、`#C6F25C`、`#8CD43C`、`#509E2C`、`#2C6420`、`#143814`；
  - 烟·暗绿：`#C4DC98`、`#92B468`、`#64844A`、`#3E5A32`、`#24361E`；
  - 粘胶·琥珀黄：`#FFF8D2`、`#F4DC8C`、`#DAB858`、`#AC863C`、`#725628`；
  - 闪光·白绿：`#FFFFFF`、`#F6FFE2`、`#E0F6AA`；
  - 重伤·紫：`#ECCEFF`、`#BC84EC`、`#8048BE`、`#4A2672`；
  - 尘土·浅灰黄：`#E6E0C8`、`#BDB394`、`#8C8466`、`#5E5844`；
- 打中、爆发居中画，不旋转；地面上的东西（毒雾的底、胶、冲击波、脚下的胶）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（14 张）

14 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `singed_fx_a_hit.png`：普攻：盾板砸中，3 帧

盾板砸中敌人：中间一个白绿色的闪光，四周飞出几块碎屑和两三颗绿色的毒液滴。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-green flash ramp (#FFFFFF, #F6FFE2, #E0F6AA), a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814).
Effect: A HEAVY BASH LANDING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-green impact flash 6 squares across, a short cross of light; 2 a burst ring 13 across with grey-green metal chips and green droplets flying out at mirrored places; 3 the chips and droplets further out and smaller, dimming to their darker shades. everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `singed_fx_q_cloud.png`：剧毒踪迹：他身后的一团毒雾，6 帧（约 3 秒）

剧毒踪迹（参考 q_smoke、smoke_clouds、q_breathtrail）：辛吉德走过的地方留下**一团贴着地面的绿色毒雾**——几团圆圆的烟团挤在一起，上面亮黄绿、下面暗绿，里面冒一两个小泡。第 1 帧冒出来（小、亮），2–4 帧胀大慢慢翻滚（这三帧会循环），5–6 帧变淡、散成几小团。**左右对称**，6 帧。毒雾贴着地，顶部不超过 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814), a murky green smoke ramp (#C4DC98, #92B468, #64844A, #3E5A32, #24361E).
Effect: A POISON CLOUD ON THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small bright puff of toxic green smoke 10 squares wide sitting on the ground; 2 it swelling into a low cloud of five round smoke puffs 24 wide and 14 tall, lime-yellow on top, murky green below, a dark green base on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 3 and 4 the puffs rolling slowly - the same size, the puffs and two small bubbles shifting at mirrored places (frames 2-4 loop); 5 the cloud thinner and paler, breaking into three puffs; 6 two faint wisps. everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 6 equal 26:18 cells, image size 2496x288 (each cell 416x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `singed_fx_q_cloud_r.png`：疯狂药剂期间的毒雾：更大更浓、带紫色，6 帧（约 3 秒）

开了大招以后的毒雾（重伤）：和上一张一样的毒雾，但**更大、更浓**，烟团之间夹着**紫色的毒丝和气泡**（附带重伤），冒的泡更多。**左右对称**，6 帧（2–4 帧循环）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814), a murky green smoke ramp (#C4DC98, #92B468, #64844A, #3E5A32, #24361E), a sickly violet ramp (#ECCEFF, #BC84EC, #8048BE, #4A2672).
Effect: A THICKER POISON CLOUD, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the same as the poison cloud but bigger and denser - 1 a bright puff 12 wide; 2 a low cloud of six round toxic green puffs 30 wide and 18 tall with sickly violet streaks and violet bubbles between them on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 3 and 4 rolling, the bubbles rising and popping at mirrored places (frames 2-4 loop); 5 thinner and paler, breaking up; 6 faint wisps. everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 6 equal 32:22 cells, image size 3072x352 (each cell 512x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `singed_fx_e_hit.png`：过肩摔：抓住，3 帧

过肩摔抓住敌人：敌人身上一下白绿色闪光，一圈短短的冲击线往外，几滴绿色毒液溅开。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-green flash ramp (#FFFFFF, #F6FFE2, #E0F6AA), a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814).
Effect: A GRAB AND HEAVE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-green flash 6 squares across on the target's chest; 2 a ring of short impact streaks 15 across with green droplets thrown out at mirrored places; 3 the droplets falling, fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal 16:18 cells, image size 768x288 (each cell 256x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `singed_fx_e_land.png`：过肩摔：摔在地上，4 帧

被扔到辛吉德身后的敌人落地：脚下砸起**一圈尘土**，地上一圈浅浅的冲击波往外推。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale dust ramp (#E6E0C8, #BDB394, #8C8466, #5E5844), a white-green flash ramp (#FFFFFF, #F6FFE2, #E0F6AA).
Effect: A BODY HITTING THE GROUND, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white impact flash 10 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 pale dust bursting up at both sides and a shock ring 22 wide on the ground; 3 the ring 28 wide, the dust puffs rising and spreading at mirrored places; 4 settling dust, fading. Flat shades, crisp shapes.
Layout: one horizontal row of 4 equal 30:12 cells, image size 1920x192 (each cell 480x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `singed_fx_e_root.png`：过肩摔：摔进胶里被粘住，4 帧

落进强力粘胶被禁锢（参考 w_root_slime、goo_strands）：敌人脚下的黏胶**一下子往上包住他的脚**——几根黄色的黏胶丝往上拉起来缠住小腿，胶面冒泡。**左右对称**，4 帧（第 4 帧停住，会持续约 1 秒）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale amber glue ramp (#FFF8D2, #F4DC8C, #DAB858, #AC863C, #725628), a white-green flash ramp (#FFFFFF, #F6FFE2, #E0F6AA).
Effect: STUCK IN THE GLUE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a splash of pale amber glue round the target's feet 16 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 thick glue strands rising from it at mirrored places up to the target's knees, 10 squares tall; 3 the strands wrapping in, glossy highlights, two bubbles on the glue; 4 the same, holding (the frame that stays). the glue is THICK STICKY ADHESIVE: pale amber-yellow, glossy, with stretched strands, drips, a few small yellow crystal chunks and round bubbles; flat shades, crisp shapes. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 20:14 cells, image size 1280x224 (each cell 320x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `singed_fx_w_vial.png`：强力粘胶：飞出去的药瓶，4 帧循环

扔出去的强力粘胶药瓶（参考 w_bottle、w_mis_blur）：一个**圆圆的玻璃瓶**，里面是黄色的黏胶，瓶口深灰，转着往前飞，后面拖一两滴黏胶。**朝右飞、上下对称**，4 帧循环（瓶子转一圈：瓶口朝右、朝上下……要上下对称就画成瓶口朝右、朝左、侧着的轮流）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale amber glue ramp (#FFF8D2, #F4DC8C, #DAB858, #AC863C, #725628), a white-green flash ramp (#FFFFFF, #F6FFE2, #E0F6AA).
Effect: A SPINNING GLASS VIAL, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round glass bottle 6 squares across full of pale amber glue with a white glint, its dark grey neck pointing right in frame 1, toward the viewer (a round cap in the middle) in frame 2, left in frame 3, toward the viewer again in frame 4; two small glue drops trailing on the left. the glue is THICK STICKY ADHESIVE: pale amber-yellow, glossy, with stretched strands, drips, a few small yellow crystal chunks and round bubbles; flat shades, crisp shapes.
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `singed_fx_w_glue.png`：强力粘胶：地上一大摊胶，8 帧（约 3 秒）

强力粘胶落地（参考 w_singed_experiment_glue、megaadhesive、w_aoe_petals、splat_dissolve）：药瓶砸碎，**地上溅开一大摊黄色的黏胶**（椭圆，边缘一个个圆鼓鼓的瓣，像溅开的蜂蜜），胶面有光泽，冒几个泡，边上散着几小块黄色的结晶碎片。第 1–2 帧溅开（玻璃碎片和白光），3–6 帧躺在地上冒泡（循环），7–8 帧变暗变小干掉。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale amber glue ramp (#FFF8D2, #F4DC8C, #DAB858, #AC863C, #725628), a white-green flash ramp (#FFFFFF, #F6FFE2, #E0F6AA).
Effect: A POOL OF GLUE ON THE GROUND, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash and glass shards where the vial bursts, a glue splash 20 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 the glue spreading into a wide pool 40 wide and 14 tall with round petal-like lobes on its rim, a few small yellow crystal chunks at mirrored places; 3, 4, 5 and 6 the pool lying still and glossy, two or three bubbles swelling and popping at mirrored places, a highlight sliding across (frames 3-6 loop); 7 the pool darker and a little smaller; 8 a dull thin film, fading. the glue is THICK STICKY ADHESIVE: pale amber-yellow, glossy, with stretched strands, drips, a few small yellow crystal chunks and round bubbles; flat shades, crisp shapes.
Layout: one horizontal row of 8 equal 44:18 cells, image size 5632x288 (each cell 704x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `singed_fx_slow.png`：强力粘胶：脚下粘着的胶，4 帧循环

被粘胶减速、缚地的敌人脚下：一小滩**黄色的黏胶**粘着脚，拉出两根短短的黏丝，冒一个小泡。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale amber glue ramp (#FFF8D2, #F4DC8C, #DAB858, #AC863C, #725628).
Effect: A STICKY GLUE PATCH, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat glossy pale amber glue patch on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 wide and 5 tall with a darker rim, two short sticky strands at mirrored places that stretch and shorten, a small bubble swelling and popping in turn. the glue is THICK STICKY ADHESIVE: pale amber-yellow, glossy, with stretched strands, drips, a few small yellow crystal chunks and round bubbles; flat shades, crisp shapes.
Layout: one horizontal row of 4 equal 18:7 cells, image size 1152x112 (each cell 288x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `singed_fx_r_drink.png`：疯狂药剂：一口喝下，5 帧

疯狂药剂（参考 color-potionfroth、color-insanity-strand、ult_spatter）：辛吉德一口喝下，**全身爆出一圈黄绿色的药剂泡沫和蒸汽**——先是身上一下亮光，然后黄绿色的泡泡、水滴和几缕蒸汽从他身边往四周和往上冒。辛吉德在中间不画，**身体的位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814), a white-green flash ramp (#FFFFFF, #F6FFE2, #E0F6AA).
Effect: A POTION RUSH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Singed stands in the middle, not drawn: 32 squares wide and 45 tall (to the tank's cap) - leave his body's place EMPTY: 1 a green-white glow hugging his outline; 2 a ring of green-yellow froth bursting out round him, round bubbles 1 to 3 squares at mirrored places; 3 the bubbles and droplets flying out and up, three curls of green steam rising from his shoulders; 4 the steam higher, the bubbles popping at the cell's edge; 5 a few bubbles and wisps fading. everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 5 equal 40:50 cells, image size 3200x800 (each cell 640x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `singed_fx_r_aura.png`：疯狂药剂：喝完后身上一直冒的蒸汽，4 帧循环

疯狂药剂生效期间：辛吉德身边一直**冒着几缕绿色的蒸汽和小泡泡**往上飘（从肩膀、背后的药罐往上），脚下一圈淡淡的绿色光。辛吉德在中间不画，**身体的位置留空**；画在他身后，要淡一点。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814), a murky green smoke ramp (#C4DC98, #92B468, #64844A, #3E5A32, #24361E).
Effect: A LINGERING POTION STEAM, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Singed stands in the middle, not drawn: 32 squares wide and 45 tall (to the tank's cap) - leave his body's place EMPTY: three thin curls of pale green steam rising from the shoulders and the top of the body at mirrored places, small bubbles drifting up between them, a faint green glow ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 30 wide; the curls and bubbles rising frame to frame so the loop flows upward. Sparse and light - it plays behind him for 25 seconds. everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 36:50 cells, image size 2304x800 (each cell 576x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `singed_fx_gw.png`：重伤：头上的紫绿色标记，4 帧循环

被大招毒雾附上重伤的敌人头上：一个**裂开的紫色小十字**（治疗被削弱的标记），上面挂着一滴绿色毒液，一闪一闪。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sickly violet ramp (#ECCEFF, #BC84EC, #8048BE, #4A2672), a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814).
Effect: A GRIEVOUS WOUND MARK, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small violet plus sign 7 squares across cracked down its middle with a dark violet crack, a green poison drop hanging under it; it pulses - brighter, then dimmer - and the drop swells and falls in turn. everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `singed_fx_p_fast.png`：剧毒冲流：加速的一下，3 帧

剧毒冲流（参考 p_wispy、q_breathtrail）：从敌方英雄身边冲过去时一下加速——**脚下一圈绿色的气流往两边冲开**，几缕毒雾被甩开。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814), a murky green smoke ramp (#C4DC98, #92B468, #64844A, #3E5A32, #24361E).
Effect: A BURST OF SPEED, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat green swirl on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 wide; 2 two sweeping gusts of toxic green wisps rushing out to both sides 30 wide, small puffs at their tips; 3 the gusts thin and fading. everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 3 equal 34:12 cells, image size 1632x192 (each cell 544x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `singed_fx_haste.png`：剧毒冲流：加速期间脚下的气流，4 帧循环

加速期间：辛吉德脚下**两缕绿色的气流**一闪一闪往两边飘（左右对称，不分前后）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic green poison ramp (#F2FFB4, #C6F25C, #8CD43C, #509E2C, #2C6420, #143814), a murky green smoke ramp (#C4DC98, #92B468, #64844A, #3E5A32, #24361E).
Effect: A SPEED WISP, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two thin toxic green wisps curling out from under the feet to both sides on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 22 wide, small puffs drifting off their ends; the wisps flicker and shift frame to frame. everything is a MAD CHEMIST's brew: toxic green poison smoke in soft round puffs with lime highlights and dark green depths, bubbles, drips and splashes; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 24:8 cells, image size 1536x128 (each cell 384x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `singed_fx_a_hit` | view_effects `league_singed_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `singed_fx_q_cloud` | view_effects `league_singed_q_cloud`（大表，在他走过的地上，不跟随，z -1；左右对称；冒出 → 飘着 → 散掉，3 秒） | 26 × 18 |
| `singed_fx_q_cloud_r` | view_effects `league_singed_q_cloud_r`（大表，在地上，不跟随，z -1；左右对称；3 秒） | 32 × 22 |
| `singed_fx_e_hit` | view_effects `league_singed_e_hit`（跟随目标，z 2；左右对称） | 16 × 18 |
| `singed_fx_e_land` | view_effects `league_singed_e_land`（在落地的人脚下，不跟随，z -1；左右对称） | 30 × 12 |
| `singed_fx_e_root` | view_effects `league_singed_e_root`（跟随目标，脚下，z 2；左右对称；约 1 秒） | 20 × 14 |
| `singed_fx_w_vial` | view_projectiles `league_singed_w_vial`（抛物线弹道，z 2；上下对称） | 10 × 8 |
| `singed_fx_w_glue` | view_effects `league_singed_w_glue`（大表，在落点的地上，不跟随，z -1；左右对称；溅开 → 躺着冒泡 → 干掉，3 秒） | 44 × 18 |
| `singed_fx_slow` | view_buffs `league_singed_w_slow`（tag `slow`，跟随，脚下，z -1；左右对称） | 18 × 7 |
| `singed_fx_r_drink` | view_effects `league_singed_r_drink`（跟随他，z 2；左右对称） | 40 × 50 |
| `singed_fx_r_aura` | view_buffs `league_singed_r_on`（tag `r_aura`，跟随他，z -1，在他身后；左右对称；约 25 秒） | 36 × 50 |
| `singed_fx_gw` | view_buffs `league_singed_q_gw`（tag `gw`，跟随，头上，z 3；左右对称） | 10 × 10 |
| `singed_fx_p_fast` | view_effects `league_singed_p_fast`（跟随他，脚下，z -1；左右对称） | 34 × 12 |
| `singed_fx_haste` | view_buffs `league_singed_p_fast`（tag `haste`，跟随，脚下，z -1；左右对称） | 24 × 8 |

- 两张表：`asset/league/effects/league_singed_fx`（小的）和 `league_singed_big`（q_cloud、q_cloud_r、w_glue），tag = 名字（build_singed.py 的 views；w_slow 用 `slow`，q_gw 用 `gw`，r_on 用 `r_aura`，p_fast 的 buff 用 `haste`）。
- 弹道（w_vial）断言上下对称；其余断言左右对称。q_cloud / q_cloud_r 拉到 q_t（180 tick）：1 开 + 2–4 循环 + 5–6 散；w_glue 拉到 w_t（180 tick）：1–2 开 + 3–6 循环 + 7–8 散；e_root 第 4 帧停到 e_root（60 tick）；r_aura 循环 r_t。
- 用 `pixel_1x/` 切格（import_zac_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
