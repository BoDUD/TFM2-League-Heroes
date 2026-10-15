# 炽炎雏龙 斯莫德：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型和动作已定（`design/smolder_idle.png`：游戏里的 3/4 正面待机，四条腿站着的小龙）。他在游戏里约 37 格宽、29 格高；**特效照常按游戏格子画**（1 格 = 1 个游戏像素）。
> - 大小对照 `design/smolder_size.png`：他在游戏里的样子放大 4 倍，红线是地面，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/smolder_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里斯莫德自己的特效贴图（火球、喷嚏的火、爆炸、妈妈的影子 `R_Mom_MisMask_v3`、地上的火带、回血的爱心），按用在我们哪张特效分好了行；只在本地用，不要提交。颜色照英雄联盟原版：**橙黄色的火、白热的火芯、他叠满层后火里的粉紫色、烟灰、妈妈深紫黑的影子**。
> - **特效要亮**：每团火都要有白黄色或最亮一档的芯，暗底上一眼能看见；烟和影子旁边要有亮一点的边或火光，不然在暗底上看不见。
> - **围着人的火、回血、升段闪光只画外圈，中间人形位置留空**。
> - **方向（重要，红色方不会镜像）**：飞出去的 `a_bolt`、`q_bolt`、`w_bolt`、`e_shot`、`r_mom` 和跟着施法方向转的 `q_t2`、`r_fire` 画成朝右，**上下对称**（往左时会上下翻）。其余所有画面（打中、身上、脚下、地上的爆炸）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `smolder_fx_<名字>.png`（`r_fire` 交 4 倍）和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `smolder_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「龙之研习」 | 吐小火球；技能打中英雄、Q 击杀叠层，10 / 25 / 40 层各升一段 | `a_bolt` · `a_hit` · `p_up` |
| 技能 1 = Q「超级灼热龙息」 | 大火球；一段在目标处爆炸，二段三颗回火弹往后飞散，三段附带灼烧 | `q_bolt` · `q_hit` · `q_t1` · `q_t2` · `q_t2_hit` · `q_burn` |
| 技能 2 = W「阿嚏！」+ E「扑棱，扑棱，扑棱！」 | 喷嚏火团（减速，打中英雄再爆炸）；E 起飞、加速、连吐 5 颗小火球 | `w_bolt` · `w_hit` · `w_boom` · `slow` · `e_shot` · `e_hit` · `e_haste` |
| 大招 = R「妈----！」 | 妈妈从头顶飞过，沿一条线喷火（减速），他站在中线上回血 | `r_mom` · `r_fire` · `r_hit` · `r_heal` · `slow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火、光、火花都没有黑描边，也不要用最深的颜色给火描一圈边**（烟、影子可以用自己最深一档收边）。
- **要亮**：每团火都有白黄色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 火：`#FFFFFF`、`#FFF6C8`、`#FFD95E`、`#FFA62E`、`#FF6E1F`、`#E8381A`、`#A8181E`；
  - 叠满层的粉紫火：`#FFF0FA`、`#FFB0DC`、`#FF6FC0`、`#E0409E`、`#A0287E`、`#5E1A6E`；
  - 烟灰：`#B8A89E`、`#7A6A62`、`#4A3A38`、`#2A1C22`；
  - 妈妈的影子：`#5A3A6A`、`#3E2450`、`#2A1638`、`#180C22`；
  - 回血：`#FFFFFF`、`#FFE6EE`、`#FFB8CC`、`#FF86A8`、`#E85A86`；
- 打中、爆发居中画，不旋转；地面上的爆炸、风圈、烟圈是从斜上方看的椭圆（宽是高的 2.5–3 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，Q 一段爆炸半径 22000，W 爆炸半径 25000，R 火线长 130000）。

### 1. `smolder_fx_a_bolt.png`：普攻：吐出去的小火球（朝目标飞，循环），4 帧

从嘴里吐出去的一颗小火球：白黄色的火芯，外面一层橙红色的火，后面拖一小截火尾和两三个小火星（参考 BA_Sparks、MisLead_Mask、YoungDragon_Q_Mis_Lvl1_Lead）。**上下对称**，朝右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: a SMALL FIREBALL flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white-yellow core 3 squares across at the front inside an orange flame, a short tapering flame tail 4 squares behind it, 2 tiny embers flickering in turn behind the tail.
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); the ball's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `smolder_fx_a_hit.png`：普攻打中（目标身上），4 帧

小火球打中：目标身上白黄色的光一闪，炸成一小团橙色火花（参考 BA_tar_alpha、BA_muzzle_flash）。**左右对称**，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: a SMALL FIRE HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 3 squares; 2 an orange four-pointed burst 8 squares across with a white core; 3 the burst breaking into 6 small orange sparks at mirrored places, 10 squares across; 4 two fading embers.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `smolder_fx_q_bolt.png`：Q 超级灼热龙息：喷出去的大火球（朝目标飞，循环），4 帧

龙息喷出的大火球：前头一团白黄色的火芯，外面一层层橙色到红色的火焰，像一颗往前冲的火流星，后面拖一条波浪形的火尾，尾巴边上一点点粉紫色（他叠层后的火，参考 Q_Mis_Lvl2_Lead、Q_Mis_Lvl3_Lead、Q_Mis_FireNoise_Horiz）。**上下对称**，朝右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E) and a pink-violet hot-flame ramp (#FFF0FA, #FFB0DC, #FF6FC0, #E0409E, #A0287E, #5E1A6E).
Effect: a BIG FIREBALL flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white-yellow core 5 squares across at the front wrapped in orange then red flame, a wavy flame tail 8 squares long behind it whose edges are mirrored top to bottom, a little pink-violet flame at the tail's tips, 3 embers trailing.
Layout: one horizontal row of 4 equal 16:11 cells, image size 1024x176 (each cell 256x176, 16 px a square); the ball's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `smolder_fx_q_hit.png`：Q 打中（目标身上），4 帧

大火球打中：目标身上白黄色的火一炸，散成一圈橙红色的火舌（参考 Q_Tar、Q_CenterShine_Tar、Q_Impactspike）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: a FIRE BLAST on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares; 2 an orange burst 14 squares across with a white core and 6 short flame tongues; 3 the burst opening into a ring of flame tongues 16 squares across at mirrored places; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `smolder_fx_q_t1.png`：Q 一段（10 层起）：火球在目标处炸开（地上，不跟随），6 帧

火球在目标处爆炸：地上一圈橙红色的冲击波往外扩（从斜上方看的扁椭圆，约 44 格宽），中间一团白黄色的火往上冒成一朵小火焰蘑菇，地上留一圈焦黑的痕迹，几块火星往两边飞（参考 Q_AoE_WaveOut、Q_AoE_ScorchDecal、Q_AoE_GroundEdge、Q_AoETar）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E) and a soot ramp (#B8A89E, #7A6A62, #4A3A38, #2A1C22).
Effect: a FIRE EXPLOSION on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 44 squares wide and 14 tall on the ground; 1 a white-yellow flash 8 squares at the center; 2 an orange fire burst rising 16 squares tall, a bright ring starting on the ground; 3 the shockwave ring 30 squares wide, the fire burst at its biggest with a white core; 4 the ring 44 squares wide and thinner, the burst breaking into flame tongues and embers flying out at mirrored places; 5 a dark soot scorch ellipse left on the ground with a few small flames; 6 the scorch fading.
Layout: one horizontal row of 6 equal 46:28 cells, image size 4416x448 (each cell 736x448, 16 px a square); centered across, the ground ellipse's center 7 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `smolder_fx_q_t2.png`：Q 二段（25 层起）：三颗回火弹从爆炸处往后飞散（朝施法方向转），5 帧

爆炸后往后弹出的三颗回火弹：从**格子左边**（爆炸的地方）出发，往右（远离斯莫德的方向）飞散成一个扇形——中间一颗直着飞，上下两颗斜着飞（**上下对称**），每颗是一个带短火尾的小火球，越飞越远、最后炸成小火花（参考 Q_Mis_Lvl2_Lead、Sparks_2x2）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: THREE BLOWBACK FIREBALLS fanning out to the RIGHT, 5 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): they start together at the LEFT edge (vertically centered) and fly right in a fan - one straight along the middle, two at mirrored angles up and down (15 degrees); each fireball a white-yellow core 3 squares across in orange flame with a short flame tail; 1 the three just leaving the left edge; 2 at 12 squares; 3 at 24 squares, the fan 10 squares tall; 4 at 36 squares; 5 each bursting into small orange sparks at the right end, the fan 16 squares tall.
Layout: one horizontal row of 5 equal 48:20 cells, image size 3840x320 (each cell 768x320, 16 px a square); vertically centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `smolder_fx_q_t2_hit.png`：Q 二段：回火弹打中身后的敌人（目标身上），3 帧

回火弹打中：目标身上一小团橙色火花一炸。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: a SMALL FIRE POP on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 4 squares; 2 an orange burst 9 squares with 4 sparks at mirrored places; 3 fading embers.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `smolder_fx_q_burn.png`：Q 三段（40 层起）：目标身上的灼烧（目标身上，每秒放一次，持续 3 秒），4 帧

被灼烧：目标身上两边一缕缕粉紫色和橙色的火苗往上蹿（他最高一段的火，参考 Q_Burn_ColorMask、Q_Mis_Lvl3_ColorMask、4x4Fire），中间人形位置留空。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a pink-violet hot-flame ramp (#FFF0FA, #FFB0DC, #FF6FC0, #E0409E, #A0287E, #5E1A6E) and an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: HOT FLAMES licking up a unit, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 8 squares wide and 18 tall): at each side 2-3 flame tongues 6-10 squares tall, pink-violet at their roots turning orange and white-yellow at their tips, flickering a step each frame (every frame mirrored), a few embers rising.
Layout: one horizontal row of 4 equal 20:24 cells, image size 1280x384 (each cell 320x384, 16 px a square); centered across, the flames' roots 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `smolder_fx_w_bolt.png`：W 阿嚏：喷嚏喷出去的一团火（朝目标飞，循环），4 帧

一个喷嚏打出去的火团：一团不太规整、圆鼓鼓的橙黄色火（像打喷嚏喷出的一口火，前头最亮），周围一圈灰白色的烟和几颗小火星，后面拖一小截烟尾（参考 W_Mis_FireMask、W_FlameBits、W_PopLead、YoungDragon_W_FlameOutline）。**上下对称**，朝右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E) and a soot ramp (#B8A89E, #7A6A62, #4A3A38, #2A1C22).
Effect: a SNEEZED FIRE PUFF flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a lumpy round puff of orange and yellow fire 8 squares across, brightest (white-yellow) at its front, a ring of grey-white smoke puffs round it and a short smoke tail behind, 3 tiny embers popping in turn.
Layout: one horizontal row of 4 equal 18:12 cells, image size 1152x192 (each cell 288x192, 16 px a square); the puff's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `smolder_fx_w_hit.png`：W 打中（目标身上），4 帧

喷嚏火团打中：目标身上一小团火和烟炸开。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E) and a soot ramp (#B8A89E, #7A6A62, #4A3A38, #2A1C22).
Effect: a FIRE-AND-SMOKE POP on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a yellow flash 4 squares; 2 an orange puff 10 squares with grey smoke round it; 3 the puff opening, 4 embers at mirrored places; 4 fading smoke.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `smolder_fx_w_boom.png`：W 打中英雄后的爆炸（地上，不跟随），6 帧

喷嚏打中英雄后炸开：一朵大的火焰爆炸，橙黄色的火团往上鼓起来，地上一圈岩浆一样的火浪往外推，外圈一圈灰烟，地上留焦痕（参考 W_AoE_PraxisFire、W_AoE_PraxisMagma_Dissolve、W_Cas_GroundScorch）。**左右对称**，约 50 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E) and a soot ramp (#B8A89E, #7A6A62, #4A3A38, #2A1C22).
Effect: a BIG FIRE EXPLOSION on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 50 squares wide and 16 tall on the ground; 1 a white-yellow flash 10 squares; 2 a round orange fireball 20 squares rising with a white core, a lava-like fire ring starting on the ground; 3 the fireball at its biggest (24 squares tall), the fire ring 36 squares wide; 4 the ring 50 squares wide with flame tongues at mirrored places, grey smoke puffs round its edge; 5 the fire sinking, a dark scorch ellipse; 6 smoke and the scorch fading.
Layout: one horizontal row of 6 equal 52:30 cells, image size 4992x480 (each cell 832x480, 16 px a square); centered across, the ground ellipse's center 8 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `smolder_fx_e_shot.png`：E 飞行时往下吐的小火球（朝目标飞，循环），3 帧

飞行时连吐的小火球：比普攻的更小，白黄色的芯，橙色的火，一小截火尾（参考 E_Mis_Head_Te、E_GlowStar）。**上下对称**，朝右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: a TINY FIREBALL flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white-yellow core 2 squares across inside orange flame, a 3-square flame tail flickering.
Layout: one horizontal row of 3 equal 8:6 cells, image size 384x96 (each cell 128x96, 16 px a square); the ball's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `smolder_fx_e_hit.png`：E 小火球打中（目标身上），3 帧

小火球打中：一小下火花。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: a TINY FIRE SPARK on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow dot 3 squares; 2 an orange four-pointed spark 7 squares; 3 two fading embers.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `smolder_fx_e_haste.png`：E 飞行时的加速（他身下，循环），4 帧

扑棱翅膀飞的时候，他身下地面上一圈被翅膀扇起来的风和火星：扁扁的一圈浅色气流（从斜上方看的椭圆），几道弯弯的风线，几颗橙色火星被吹起来（参考 SwirlLead、TinySparks）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E) and a soot ramp (#B8A89E, #7A6A62, #4A3A38, #2A1C22).
Effect: a WIND RING of flapping wings on the ground, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ring 30 squares wide and 8 tall drawn as 4-6 short curved pale grey-white wind strokes at mirrored places turning a step each frame, 3-4 small orange embers blown up from it.
Layout: one horizontal row of 4 equal 32:10 cells, image size 2048x160 (each cell 512x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `smolder_fx_r_mom.png`：R 妈----！：妈妈从头顶飞过的影子（沿施法方向飞，循环），4 帧

斯莫德的妈妈（一条巨大的成年龙）从高空飞过，地上看到的是她的**影子**：一个从正上方看下去的大龙剪影——头朝右，长脖子，两只巨大的翅膀往上下两边张开，后面一条长尾巴（参考 R_Mom_MisMask_v3 这张就是她的影子）。影子是深紫黑色，边缘一圈淡淡的橙红色火光（她嘴里的火映出来的），翅膀一帧一帧扇动。**上下对称**（两只翅膀是镜像），朝右飞。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a dark shadow ramp (#5A3A6A, #3E2450, #2A1638, #180C22) and an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: the SHADOW OF A HUGE DRAGON flying to the RIGHT seen from straight above, 4 frames, a seamless loop of wing beats, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): her head and long neck pointing right, two enormous wings spread up and down (mirrored), a long tail trailing left, the whole silhouette dark shadow purple-black with a soft 1-square orange glow rim; 1 the wings spread widest (40 squares tip to tip); 2 the wings sweeping back; 3 the wings folded half (28 squares); 4 the wings coming forward again.
Layout: one horizontal row of 4 equal 50:42 cells, image size 3200x672 (each cell 800x672, 16 px a square); the head 2 squares from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `smolder_fx_r_fire.png`：R：妈妈喷在地上的一整条火线（沿施法方向，约 0.75 秒），4 帧

妈妈喷下来的龙息在地上烧成一整条火带：**横着铺满整个格子**（从斯莫德脚下一直到 130 格外），带子中间一条最亮的白黄色火线（中线，伤害更高），两边橙红色的火焰往上蹿，边缘是熔岩一样的暗红和一点焦黑（参考 R_GroundTrail_Burn、R_FireNoise_2x2、R_GeneralFire_2x2、R_LavaNoise、R_AoE_PraxisMagma）。**上下对称**。四帧：点燃 → 烧到最旺 → 还在烧 → 熄灭成焦痕。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E) and a soot ramp (#B8A89E, #7A6A62, #4A3A38, #2A1C22).
Effect: a LONG BAND OF DRAGON FIRE on the ground, 4 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a horizontal band across the WHOLE cell width (132 squares) and 22 squares tall: a bright white-yellow center line 3 squares thick along its whole length, orange and red flames licking up and down from it (mirrored), lava-like dark red and a little soot at its two edges; 1 the fire catching, thinner (14 squares), brightest at the center line; 2 the fire at its fullest; 3 still burning, the flame tongues shifted; 4 burning out to a dark red scorched band with a few embers.
Layout: one horizontal row of 4 equal 132:24 cells, image size 4224x192 (each cell 1056x192, 8 px a square); the band vertically centered, touching both the LEFT and the RIGHT edge, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `smolder_fx_r_hit.png`：R 火线烧到（目标身上），4 帧

被妈妈的火烧到：目标身上一团大火一炸。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: a BIG FIRE HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares; 2 an orange-red burst 14 squares with a white core; 3 6 flame tongues at mirrored places, 16 squares; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `smolder_fx_r_heal.png`：R 站在中线上回血（他身上），5 帧

站在妈妈的火的中线上被治疗：他身上冒起一颗暖粉色的小爱心，周围几颗小亮点往上飘（参考 R_Heal_Heart、HealWisps）。**左右对称**，中间人形位置留空，爱心在头顶上方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a warm pink heal ramp (#FFFFFF, #FFE6EE, #FFB8CC, #FF86A8, #E85A86) and an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: a WARM HEAL rising round a small figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 8 squares wide and 14 tall): 1 4 warm pink sparkles at mirrored places low at both sides; 2 the sparkles rising, a small pink heart 5 squares wide appearing above the empty area with a white core; 3 the heart 7 squares wide, brightest; 4 the heart rising 2 squares, sparkles at the top; 5 fading sparkles.
Layout: one horizontal row of 5 equal 18:24 cells, image size 1440x384 (each cell 288x384, 16 px a square); centered across, the empty area's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `smolder_fx_p_up.png`：被动 龙之研习：升段（10 / 25 / 40 层）时他身上的火焰闪光，6 帧

叠层升段：他身边一圈火焰旋转着往上冲，头顶一闪，两边飞出火星，最后散开（参考 Base_E_GlowStar、SwirlLead、Sparks_2x2、Q_Mis_Lvl3_ColorMask 的粉紫）。火从橙色变成一点粉紫色（他越叠越强）。**左右对称**，中间人形位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E) and a pink-violet hot-flame ramp (#FFF0FA, #FFB0DC, #FF6FC0, #E0409E, #A0287E, #5E1A6E).
Effect: a POWER-UP FLARE round a small figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 22 squares wide and 22 tall): 1 a ring of small orange flames on the ground round the empty area; 2 the flames rising at both sides 12 squares; 3 the flames 26 squares tall, pink-violet at their tips, meeting above the area; 4 a white-yellow four-pointed star flash 8 squares above the area, sparks flying out at mirrored places; 5 sparks falling; 6 a few fading embers.
Layout: one horizontal row of 6 equal 34:36 cells, image size 3264x576 (each cell 544x576, 16 px a square); centered across, the empty area's bottom 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `smolder_fx_slow.png`：减速（W、R 打中的人身上，循环），4 帧

被减速：目标脚下一圈焦黑的烟灰和几颗暗红的余烬，烟一缕缕往上冒一点（参考 Smoke_4x4、R_SmokeTrail）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around fire, light, sparks or rings (smoke and the shadow may have their own darkest shade at their edge), BRIGHT fire (every flame lit with its lightest shades and a white-hot core - it must read on a dark battlefield), colours only from a soot ramp (#B8A89E, #7A6A62, #4A3A38, #2A1C22) and an orange-yellow fire ramp (#FFFFFF, #FFF6C8, #FFD95E, #FFA62E, #FF6E1F, #E8381A, #A8181E).
Effect: SMOULDERING SOOT at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat dark soot ring 18 squares wide and 6 tall, small grey smoke wisps rising 3 squares from it at mirrored places, 4 tiny dull red embers glowing in turn.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `smolder_fx_a_bolt` | view_projectiles `league_smolder_a_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 9 × 6 |
| `smolder_fx_a_hit` | view_effects `league_smolder_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `smolder_fx_q_bolt` | view_projectiles `league_smolder_q_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 14 × 9 |
| `smolder_fx_q_hit` | view_effects `league_smolder_q_hit`（跟随，画在人物上面；左右对称） | 16 |
| `smolder_fx_q_t1` | view_effects `league_smolder_q_t1`（不跟随，画在人物上面；左右对称）；表 `league_smolder_big` | 44 × 26 |
| `smolder_fx_q_t2` | view_projectiles `league_smolder_q_t2`（朝施法方向转，画成朝右；上下对称；从格子左边开始）；表 `league_smolder_big` | 46 × 18 |
| `smolder_fx_q_t2_hit` | view_effects `league_smolder_q_t2_hit`（跟随，画在人物上面；左右对称） | 10 |
| `smolder_fx_q_burn` | view_effects `league_smolder_q_burn`（跟随，画在人物上面；左右对称；4 帧约 1 秒） | 18 × 22 |
| `smolder_fx_w_bolt` | view_projectiles `league_smolder_w_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 10 |
| `smolder_fx_w_hit` | view_effects `league_smolder_w_hit`（跟随，画在人物上面；左右对称） | 12 |
| `smolder_fx_w_boom` | view_effects `league_smolder_w_boom`（不跟随，画在人物上面；左右对称）；表 `league_smolder_big` | 50 × 28 |
| `smolder_fx_e_shot` | view_projectiles `league_smolder_e_shot`（朝飞行方向转，画成朝右飞；上下对称） | 7 × 5 |
| `smolder_fx_e_hit` | view_effects `league_smolder_e_hit`（跟随，画在人物上面；左右对称） | 8 |
| `smolder_fx_e_haste` | view_buffs `league_smolder_e_haste`（跟随，画在人物下面；左右对称；飞行时一直放） | 30 × 8 |
| `smolder_fx_r_mom` | view_projectiles `league_smolder_r_mom`（朝飞行方向转，画成朝右飞；上下对称）；表 `league_smolder_big` | 48 × 40 |
| `smolder_fx_r_fire` | view_projectiles `league_smolder_r_fire`（朝施法方向转，画成朝右；上下对称；画在人物下面；一整条铺满格子）；表 `league_smolder_big` | 132 × 24 |
| `smolder_fx_r_hit` | view_effects `league_smolder_r_hit`（跟随，画在人物上面；左右对称） | 16 |
| `smolder_fx_r_heal` | view_effects `league_smolder_r_heal`（跟随，画在人物上面；左右对称） | 16 × 22 |
| `smolder_fx_p_up` | view_effects `league_smolder_p_up`（跟随，画在人物上面；左右对称） | 32 × 34 |
| `smolder_fx_slow` | view_buffs `league_smolder_w_slow` / `league_smolder_r_slow`（跟随，画在人物下面；左右对称；减速期间一直放） | 18 × 6 |

- 两张表：`asset/league/effects/league_smolder_fx`（小的）和 `league_smolder_big`（q_t1、q_t2、w_boom、r_mom、r_fire），tag = 名字（build_smolder.py 的 views；`e_shotm` 绑到 `e_shot`、`w_xhit` 绑到 `w_hit`、`w_slow` / `r_slow` 绑到 `slow`）。
- 飞行的 `a_bolt`、`q_bolt`、`w_bolt`、`e_shot`、`r_mom` 朝飞行方向转；`q_t2`（从爆炸点往后的线，图从格子左边起）和 `r_fire`（LineRangeProjectile 画在整条线的中点：130000 长的线，图铺满格子）朝施法方向转；`q_t1`、`w_boom` 不跟随；`q_burn` 4 帧约 1 秒（灼烧每 60 tick 放一次）；`r_fire` 拼到 45 tick（build_smolder r_pic）。
- 用 `pixel_1x/` 切格（import_bard_fx 的做法），断言对称；必要时从 raw 重读（Codex 的读回可能清掉中间）；核对交回的张数和这份清单。
