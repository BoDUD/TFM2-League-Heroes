# 蒙多医生（祖安狂人）：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型和动作已定（`design/drmundo_idle.png`：3/4 正面朝右的紫色大块头，近侧手拎着骨锯）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连骨锯 43 格高、54 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/drmundo_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/drmundo_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。`design/drmundo_saw.png`：他的骨锯（8 倍），飞出去的 `q_saw` 就是这把锯。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里蒙多自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色：**化学药剂是毒绿色**（骨锯的残影、减速黏液、药罐、极限剂量），**电击疗法是青蓝色的电**，**砍中、砸中是白热的冲击光**，药剂里点缀几颗**粉红**火花（他肩上宝石的颜色）。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着他的光环、电流、液体只画外圈和两边，中间他的身体位置留空**——他是个大块头（宽约 28 格、高约 30 格），每条都写了留空多大。
> - **方向（重要，红色方不会镜像）**：飞出去的 `q_saw`（骨锯）和 `e_fling`（被打飞的尸体）在空中**打转 / 翻滚**，倒过来看也一样，所以随便哪一面朝上都行。`p_tank`（地上的药罐）在红色方会被**转 180°**，所以要**中心对称**（转半圈一模一样）。其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `drmundo_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `drmundo_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + E「大力行医」 | 骨锯劈砍；每隔几秒一次抡药箱的强化普攻，打死的小兵被打飞撞伤后面的敌人 | `a_hit` · `e_hit` · `e_fling` · `e_fling_hit` |
| 技能 1 = Q「病毒屠刀」 | 扔出骨锯，打中第一个单位：伤害、减速、回血 | `q_saw` · `q_hit` · `q_heal` · `q_slow` |
| 技能 2 = W「电击疗法」 | 开启后身边持续电人，结束时放电，打中英雄回灰色生命 | `w_start` · `w_on` · `w_zap` · `w_burst` · `w_end_hit` |
| 大招「极限剂量」 | 给自己注射：回血、加最大生命、移速 | `r_cast` · `r_on` |
| 被动「想去哪就去哪」 | 挣脱控制，丢下药罐；捡起回血，被敌人踩到就碎 | `p_shake` · `p_tank` · `p_land` · `p_pick` · `p_break` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、黏液、火花、闪电、碎片、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（例外：骨锯、药罐的金属和玻璃、被打飞的尸体，可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 毒绿化学药剂：`#F4FFE0`、`#C8FF7A`、`#8EE83C`、`#4CB82A`、`#237A2C`、`#0F4220`；
  - 青蓝电流：`#FFFFFF`、`#E0FDFF`、`#8CEBFF`、`#38C2F5`、`#1C78C8`、`#0F3A78`；
  - 白热冲击：`#FFFFFF`、`#FFF4CF`、`#FFD27A`、`#FF9A3C`、`#D85A20`；
  - 钢 / 玻璃 / 金属：`#F2FAFA`、`#C4D8D8`、`#8FA6AA`、`#5C6E74`、`#2E3A40`；
  - 尘土：`#F2E6CF`、`#D6C3A0`、`#B39B76`、`#8A7255`、`#5E4C39`；
  - 粉红火花：`#FFE0F2`、`#FF7CC8`、`#F0309A`、`#A8166A`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 25000，Q 射程 70000，电击疗法半径 22000）。

### 1. `drmundo_fx_q_saw.png`：Q 病毒屠刀：飞出去的骨锯（朝目标飞，循环），4 帧

扔出去的骨锯：就是他手里那把（`design/drmundo_saw.png`：钢青刀身、下缘大锯齿、锈橙刀背、青蓝刀箍），**整把在空中打转**，4 帧各转 90°，后面拖一圈绿色的化学残影 / 液滴（参考 Q_Trail、Q_Bonesaw_Glow、Q_OilySmoke）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#F2FAFA, #C4D8D8, #8FA6AA, #5C6E74, #2E3A40), a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220) and the saw's own rusty orange and teal.
Effect: his BONE SAW (the attached saw picture: teal-steel blade, a row of big saw teeth on one edge, a rusty orange back, a teal band at the grip) SPINNING in flight, 4 frames, a seamless loop: the whole saw turned 90 degrees further each frame round its middle, 16 squares long; a curved smear of toxic green light and a few green droplets trailing the turning blade.
Layout: one horizontal row of 4 equal square cells, image size 1408x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `drmundo_fx_q_hit.png`：Q 骨锯命中（目标身上），5 帧

骨锯砍中：一道白热的交叉斩痕一闪，绿色的化学液体往两边溅开（参考 Q_Spear_Impact_Diust_burst、Q_OilySmoke、Droplets）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-hot impact ramp (#FFFFFF, #FFF4CF, #FFD27A, #FF9A3C, #D85A20) and a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220).
Effect: a SAW HIT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 an X of two white-hot slash lines 12 squares across with a white core; 3 the X fading, toxic green goo bursting out to both sides 16 squares wide in mirrored splashes; 4 green droplets flying out and falling; 5 a few fading green drops.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `drmundo_fx_q_heal.png`：Q 打中回血（他身上），4 帧

打中回血：他身边几个绿色的「+」和光点往上飘。**左右对称**，中间他的身体位置留空（只画两边和头顶）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220).
Effect: HEALING PLUSES rising round a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 10 squares wide where he stands): 1 two small green plus signs at his sides at waist height; 2 the pluses 3 squares bigger, rising 4 squares, two more motes; 3 rising to his shoulders, a small plus over his head; 4 fading up.
Layout: one horizontal row of 4 equal 16:22 cells, image size 1024x352 (each cell 256x352, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `drmundo_fx_q_slow.png`：Q 减速（敌人脚下，循环），4 帧

被骨锯减速：敌人脚下一摊冒泡的绿色化学黏液（扁椭圆），几个小泡轮流冒起来。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220).
Effect: a TOXIC GOO PUDDLE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse of green goo 14 squares wide and 4 tall, a lighter rim; small bubbles at mirrored places taking turns to swell and pop.
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `drmundo_fx_a_hit.png`：普攻打中（目标身上），4 帧

骨锯劈中：一小团白热的冲击闪光，几道短光线往外射。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-hot impact ramp (#FFFFFF, #FFF4CF, #FFD27A, #FF9A3C, #D85A20).
Effect: a SMALL CHOP HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a white-hot flash 7 squares with a white core; 3 the flash 10 squares, 6 short warm rays at mirrored places; 4 a few fading warm sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `drmundo_fx_e_hit.png`：E 大力行医：药箱砸中（目标身上），5 帧

药箱砸中：一个大大的白热冲击星（四角星）+ 一圈冲击环炸开，几颗绿色药丸 / 碎片和星星往外飞（参考 Q_Rocks、Wukong_Base_Sparkles、Dr_Mundo_Base_E_BuffDrips）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-hot impact ramp (#FFFFFF, #FFF4CF, #FFD27A, #FF9A3C, #D85A20) and a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220).
Effect: a HEAVY BASH on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a four-pointed white-hot impact star 16 squares with a white core; 3 the star and a warm shock ring 20 squares across, small green pill-shaped bits and white stars flying out at mirrored places; 4 the ring fading, the bits further out; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `drmundo_fx_e_fling.png`：E 打飞的尸体（朝后方飞，循环），4 帧

被药箱打飞的小兵尸体：一团软塌塌的深灰紫色小身体在空中翻滚，4 帧各转 90°，后面拖两三道白色的速度线（参考 Sion_Skin05_Sl_Dust、Q_Smoke）。不用画清楚是哪种小兵。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39), a dark grey-purple body ramp (#B8A8C8, #7A6890, #4C3E60, #2A2038) and white speed lines.
Effect: a LIMP SMALL BODY TUMBLING through the air, 4 frames, a seamless loop: a vague dark grey-purple rag-doll shape 9 squares long (a round head, a lump of a body, two floppy limbs), turned 90 degrees further each frame round its middle; three short white speed lines behind it and a puff of dust at its tail.
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `drmundo_fx_e_fling_hit.png`：E 尸体撞到敌人（目标身上），4 帧

尸体撞中：一团土黄色的撞击尘土炸开，中间一下白光。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39) and a white-hot impact ramp (#FFFFFF, #FFF4CF, #FFD27A, #FF9A3C, #D85A20).
Effect: a THUD on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a puff of dust 10 squares with a white-hot core; 3 the dust 14 squares, clods flying out at mirrored places; 4 settling dust.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `drmundo_fx_w_on.png`：W 电击疗法：开着的电流光环（他身上，循环），4 帧

电击疗法开着时：他身边一圈噼啪作响的青蓝色电流——腰部一圈扁扁的电光椭圆，几道小闪电从肩上（电极）往下跳到椭圆上，4 帧闪电位置轮流变（参考 P_Lightning03、W_LightningErosion03）。**左右对称**（闪电可以左右对称地成对出现），中间他的身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric cyan ramp (#FFFFFF, #E0FDFF, #8CEBFF, #38C2F5, #1C78C8, #0F3A78).
Effect: a CRACKLING ELECTRIC AURA round a big figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 28 squares wide and 30 tall where he stands): a flat crackling ring of cyan electricity 44 squares wide and 10 tall round his waist; small jagged cyan-white bolts jumping down from his shoulders (16 squares above the ring, both sides, mirrored) to the ring, in different places each frame; a few blue sparks.
Layout: one horizontal row of 4 equal 46:34 cells, image size 2944x544 (each cell 736x544, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `drmundo_fx_w_start.png`：W 开启：心脏电击（他身上，不跟随），4 帧

开启电击疗法：他两边肩头（电极）各炸出一团青白色的电火花，两道电弧往胸口汇合，一闪（参考 P_Capacitor_Erode、P_Ray_Mult）。**左右对称**，中间身体留空（只画两肩和胸前的电弧）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric cyan ramp (#FFFFFF, #E0FDFF, #8CEBFF, #38C2F5, #1C78C8, #0F3A78).
Effect: a HEART SHOCK on a big figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a figure 28 squares wide and 30 tall in the middle, not drawn - only the sparks on him): 1 two cyan-white sparks at his shoulders, 22 squares apart, 20 squares up; 2 the sparks 6 squares across, two jagged bolts arcing from them toward the middle of his chest; 3 the bolts meeting in a white flash 8 squares on his chest; 4 fading sparks.
Layout: one horizontal row of 4 equal 34:32 cells, image size 2176x512 (each cell 544x512, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `drmundo_fx_w_zap.png`：W 每跳电到的敌人（目标身上），3 帧

电流每跳一次：目标身上一道竖着的小闪电劈下来，脚边几点火花。**左右对称**（闪电竖直、左右对称地画两道细的）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric cyan ramp (#FFFFFF, #E0FDFF, #8CEBFF, #38C2F5, #1C78C8, #0F3A78).
Effect: a SMALL ZAP on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two thin jagged cyan-white bolts coming down from 14 squares up, mirrored; 2 the bolts reaching the bottom, a white flash 4 squares there, a few sparks out to both sides; 3 fading sparks.
Layout: one horizontal row of 3 equal 12:18 cells, image size 576x288 (each cell 192x288, 16 px a square); centered across, the bolts' ends on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `drmundo_fx_w_burst.png`：W 放电：一圈电流炸开（他身上，不跟随），5 帧

结束放电：以他为中心炸开一大圈青蓝色的电流冲击环（扁椭圆，从腰部往外扩到 48 格宽），一圈闪电往外射，中间一团白光（参考 W_LightningErosion03、Bubble）。**左右对称**，中间身体留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric cyan ramp (#FFFFFF, #E0FDFF, #8CEBFF, #38C2F5, #1C78C8, #0F3A78).
Effect: an ELECTRIC DISCHARGE round a big figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 28 squares wide and 30 tall): 1 a white flash on his chest 10 squares; 2 a flat cyan shock ring 28 squares wide and 8 tall round his waist with a white core line; 3 the ring 40 wide, 8 jagged bolts shooting out of it at mirrored places; 4 the ring 48 wide and breaking up, sparks; 5 the last sparks.
Layout: one horizontal row of 5 equal 50:34 cells, image size 4000x544 (each cell 800x544, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `drmundo_fx_w_end_hit.png`：W 放电电到的敌人（目标身上），4 帧

放电电中：目标全身被一团青白色的电网包住一闪。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric cyan ramp (#FFFFFF, #E0FDFF, #8CEBFF, #38C2F5, #1C78C8, #0F3A78).
Effect: an ELECTROCUTION on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a tangle of jagged cyan bolts 14 squares wide and 16 tall with a white core; 3 the tangle brightest, sparks out at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `drmundo_fx_r_cast.png`：R 极限剂量：注射发动（他身上，不跟随），6 帧

极限剂量：他身上爆出一大团绿色的化学液体和光（从胸口往外、往上冲），几颗粉红色的火花，绿色的泡泡往上冒（参考 R_Chemical_Mult、R_Droplets、R_ClothRing、R_Eye_Glow、Bubble）。**左右对称**，中间身体留空（只画四周和头顶）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220) and a pink ramp (#FFE0F2, #FF7CC8, #F0309A, #A8166A).
Effect: a CHEMICAL SURGE round a big figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 26 squares wide and 30 tall where he stands): 1 a green glow ring 30 wide and 8 tall round his feet; 2 toxic green liquid splashing up at both sides to his shoulders in mirrored arcs, a white-lime core; 3 the splash at its highest, 40 squares tall, bubbles and a few pink sparks flying up; 4 the splash falling, bubbles rising over his head; 5 droplets falling, bubbles popping; 6 a faint green shimmer.
Layout: one horizontal row of 6 equal square cells, image size 4032x672 (each cell 672x672, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `drmundo_fx_r_on.png`：R 生效中（他身上，循环），4 帧

极限剂量生效的 10 秒：他身边几颗绿色的泡泡慢慢往上冒、偶尔一滴绿色液体往下滴，眼睛那里一点粉红光（不用画眼睛，只画身体两边和头顶的泡泡）。**左右对称**，要稀疏，不要遮住他。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220) and a pink ramp (#FFE0F2, #FF7CC8, #F0309A, #A8166A).
Effect: RISING BUBBLES round a big figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 24 squares wide and 30 tall): 4-6 small toxic green bubbles (2-3 squares) at both sides at mirrored places drifting up 3 squares a frame and popping at his shoulders, one green drip falling at each side; sparse - most of the cell empty.
Layout: one horizontal row of 4 equal 32:36 cells, image size 2048x576 (each cell 512x576, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `drmundo_fx_p_shake.png`：被动：挣脱控制（他身上），5 帧

想去哪就去哪：他把控制甩开——一圈白绿色的碎玻璃 / 碎光片从他身上往外炸开（参考 P_Glass_Shards_2x2、R_Eye_Glow）。**左右对称**，中间身体留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220) and a steel ramp (#F2FAFA, #C4D8D8, #8FA6AA, #5C6E74, #2E3A40).
Effect: a SHRUG-OFF BURST round a big figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 24 squares wide and 28 tall): 1 a green-white ring of light 26 squares wide round his chest; 2 the ring shattering into glassy shards and green sparks; 3 the shards flying out at mirrored places, 30 squares across; 4 the shards spinning further and dimming; 5 a few motes.
Layout: one horizontal row of 5 equal square cells, image size 2560x512 (each cell 512x512, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `drmundo_fx_p_tank.png`：被动：地上的药罐（地上，循环），2 帧

掉在地上的化学药罐（捡起来回血、减被动冷却）：一个**矮胖的圆罐子，从斜上方看**——金属的圆形罐口和罐底边、玻璃罐身里装着发光的绿色药水、罐子周围地上一圈淡绿光，药水的亮光 2 帧轮流闪。**中心对称**：整张转 180° 必须一模一样（不要画有上下、左右之分的东西，例如标签、斜放的罐子、只在一边的高光）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220) and a steel ramp (#F2FAFA, #C4D8D8, #8FA6AA, #5C6E74, #2E3A40).
Effect: a SQUAT CHEMICAL TANK lying on the ground seen from above at an angle, 2 frames, a seamless loop, POINT-SYMMETRIC in every frame: it looks EXACTLY the same turned half round (180 degrees) about the cell's centre (the game turns it upside down on the red side): an oval glass canister 10 squares wide and 6 tall with a steel rim all round, filled with glowing toxic green liquid, two steel clasps at its left and right ends (mirrored), a faint green glow ring on the ground round it 12 wide and 8 tall; the liquid's brightness pulsing between the frames - every highlight placed so the picture turned 180 degrees is the same.
Layout: one horizontal row of 2 equal 14:10 cells, image size 448x160 (each cell 224x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `drmundo_fx_p_land.png`：被动：药罐落地（地上，不跟随），4 帧

药罐落地：落点一小股尘土往两边溅，一圈绿色的光环一闪。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39) and a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220).
Effect: a LANDING PUFF on the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 squares on the ground; 2 dust kicked out to both sides 12 squares wide, a flat green ring 10 wide; 3 the dust 16 wide and settling, the ring fading; 4 faint dust.
Layout: one horizontal row of 4 equal 18:10 cells, image size 1152x160 (each cell 288x160, 16 px a square); centered across, the ground's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `drmundo_fx_p_pick.png`：被动：捡起药罐回血（地上，不跟随），4 帧

捡起药罐：一团绿色的光往上冲，几个绿色的「+」往上飘。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220).
Effect: a HEALING BURST rising, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a green flash 6 squares at the bottom; 2 a column of green light 8 wide rising 14 squares, two plus signs at its sides; 3 the column fading up, the pluses at 18 squares; 4 a few rising motes.
Layout: one horizontal row of 4 equal 18:22 cells, image size 1152x352 (each cell 288x352, 16 px a square); centered across, the burst's foot on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `drmundo_fx_p_break.png`：被动：药罐被敌人踩碎（地上，不跟随），4 帧

药罐被踩碎：碎玻璃片往两边飞，绿色的药水溅开成一摊。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, goo, sparks, bolts, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#F2FAFA, #C4D8D8, #8FA6AA, #5C6E74, #2E3A40) and a toxic chemical green ramp (#F4FFE0, #C8FF7A, #8EE83C, #4CB82A, #237A2C, #0F4220).
Effect: a SMASHED TANK on the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 glass shards flying out to both sides at mirrored places, green liquid splashing up 6 squares; 3 the splash falling into a flat green puddle 14 wide and 4 tall, shards on the ground; 4 the puddle fading.
Layout: one horizontal row of 4 equal 18:12 cells, image size 1152x192 (each cell 288x192, 16 px a square); centered across, the ground's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `drmundo_fx_q_saw` | view_projectiles `league_drmundo_q_saw`（朝飞行方向转；它在转，倒过来也一样） | 20 × 20 |
| `drmundo_fx_q_hit` | view_effects `league_drmundo_q_hit`（跟随，画在人物上面；左右对称） | 16 |
| `drmundo_fx_q_heal` | view_effects `league_drmundo_q_heal`（跟随，画在他身上；左右对称） | 14 × 20 |
| `drmundo_fx_q_slow` | view_buffs `league_drmundo_q_slow`（跟随，画在人物下面；左右对称） | 16 × 5 |
| `drmundo_fx_a_hit` | view_effects `league_drmundo_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `drmundo_fx_e_hit` | view_effects `league_drmundo_e_hit`（跟随，画在人物上面；左右对称） | 20 |
| `drmundo_fx_e_fling` | view_projectiles `league_drmundo_e_fling`（朝飞行方向转；它在翻滚，倒过来也一样） | 12 × 10 |
| `drmundo_fx_e_fling_hit` | view_effects `league_drmundo_e_fling_hit`（跟随，画在人物上面；左右对称） | 14 |
| `drmundo_fx_w_on` | view_buffs `league_drmundo_w_on`（跟随，画在他下面一层；左右对称；大图表） | 44 × 30 |
| `drmundo_fx_w_start` | view_effects `league_drmundo_w_start`（跟随，画在他身上；左右对称；大图表） | 32 × 30 |
| `drmundo_fx_w_zap` | view_effects `league_drmundo_w_zap`（跟随，画在人物上面；左右对称） | 10 × 16 |
| `drmundo_fx_w_burst` | view_effects `league_drmundo_w_burst`（跟随，画在他身上；左右对称；大图表） | 48 × 32 |
| `drmundo_fx_w_end_hit` | view_effects `league_drmundo_w_end_hit`（跟随，画在人物上面；左右对称） | 16 |
| `drmundo_fx_r_cast` | view_effects `league_drmundo_r_cast`（跟随，画在他身上；左右对称；大图表） | 40 × 40 |
| `drmundo_fx_r_on` | view_buffs `league_drmundo_r_on`（跟随，画在他身上；左右对称） | 30 × 34 |
| `drmundo_fx_p_shake` | view_effects `league_drmundo_p_shake`（跟随，画在他身上；左右对称） | 30 × 30 |
| `drmundo_fx_p_tank` | view_projectiles `league_drmundo_p_tank`（区域的画面：红色方会转 180°，所以要中心对称） | 12 × 8 |
| `drmundo_fx_p_land` | view_effects `league_drmundo_p_land`（不跟随，地上；左右对称） | 16 × 8 |
| `drmundo_fx_p_pick` | view_effects `league_drmundo_p_pick`（不跟随；左右对称） | 16 × 20 |
| `drmundo_fx_p_break` | view_effects `league_drmundo_p_break`（不跟随，地上；左右对称） | 16 × 10 |

- 两张表：`asset/league/effects/league_drmundo_fx`（小的）和 `league_drmundo_big`（r_cast、w_burst、w_on、w_start），tag = 名字（build_drmundo.py 的 views）。
- `q_saw`、`e_fling` 是飞行投射物（画面朝飞行方向转，它们本来就在转）；`p_tank` 是地上区域的画面（会转 180°，断言中心对称）；`p_land`、`p_pick`、`p_break` 不跟随；`q_slow` 脚下 buff（z -1）；`w_on` 他下面一层（z -1）。
- 用 `pixel_1x/` 切格，断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
