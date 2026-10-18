# 吉格斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型和动作已定（`design/ziggs_idle.png`：3/4 正面朝右的约德尔爆破专家，蓝红条纹头盔、绿色护目镜、尖耳朵、咧嘴白牙、米黄胡子，红外套、牛仔蓝背带裤，两只手各托一颗带白骷髅的红炸弹）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连两颗炸弹 32 格高、41 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/ziggs_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/ziggs_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里吉格斯自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**炸弹是带白骷髅的红色圆炸弹**，**爆炸是橙黄色的火加灰烟**，**被动和地雷的火花带蓝白色的海克斯光**，**大招落点是红色的圆圈加骷髅标记**。
> - **特效要亮**：每团光、每次爆炸都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **飞行中的炸弹（a_bomb、p_bomb、e_throw、r_bomb）上下对称**：游戏会把飞行的图按飞的方向转，往左飞时整张图上下翻过来，所以飞行中的炸弹不画骷髅，引线的火星画成拖在身后（左边）的尾巴，上下对称。
> - **其余全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他朝左时也是同一张图。
> - **围着人的画面中间身体位置留空**，不要盖住人。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ziggs_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/ziggs_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/ziggs_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「一触即发」 | 扔小炸弹；每隔一段时间下一次普攻扔一颗海克斯强化炸弹，多一份魔法伤害 | `a_bomb` · `a_hit` · `p_bomb` · `p_hit` |
| 技能 1 = Q「弹跳炸弹」 | 炸弹沿直线一跳一跳（最多落地三次），落地时附近有敌人就爆炸 | `q_bomb`（空中） · `q_bounce` · `q_blast` · `q_hit` |
| 技能 2 = E「海克斯爆破雷区」 | 扔出一把地雷散在地上 5 秒，敌人踩到就炸并减速 | `e_throw` · `e_land` · `e_field` · `e_hit` · `e_slow` |
| 自动放的 W「定点爆破」 | 敌人贴脸时炸药包在脚下炸开，把敌人炸开、自己也被炸飞 | `w_blast` · `w_hit` |
| 大招「科学的地狱火炮」 | 举起超大炸弹扔到很远的地方，落点先有红圈预警，中心伤害更高 | `r_cast` · `r_bomb` · `r_warn` · `r_boom` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、火星、烟、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：炸弹、地雷、炸药包可以有一圈深色边）。
- **要亮**：每个光和火的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 火和火星（所有爆炸、引线）：`#FFFFFF`、`#FFF6C0`、`#FFD25A`、`#FF9A28`、`#E2541A`、`#8E2410`；
  - 海克斯蓝白光（被动、地雷的火花）：`#FFFFFF`、`#E4F6FF`、`#9ADCFF`、`#46A8F0`、`#2462C0`、`#123274`；
  - 炸弹的红色外壳（加纯白的骷髅）：`#FFE8E0`、`#F2564A`、`#C8281E`、`#8A1612`、`#4E0A0A`、`#1E0606`；
  - 烟和尘土、炸药包的灰：`#F4F0EA`、`#CFC8BE`、`#A29A90`、`#756E68`、`#4A4644`、`#262424`；
  - 预警红（大招落点、地雷的红灯）：`#FFFFFF`、`#FFD0C8`、`#FF7A66`、`#E8302A`、`#A0141A`、`#560A10`；
- 打中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 爆炸半径 20000，雷区半径 30000，炸药包半径 30000，大招外圈 40000、中心 18000）。

### 1. `ziggs_fx_a_bomb.png`：普攻的小炸弹（飞行中），3 帧循环

普攻扔出去的小炸弹：一颗红色圆炸弹（约 6 格），身后（左边）拖着引线冒出的黄橙色火星尾巴。**上下对称**（飞向左边时游戏会把图上下翻过来），所以炸弹上不画骷髅，引线火星画在身后。三帧火星闪动。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bomb-shell red ramp (#FFE8E0, #F2564A, #C8281E, #8A1612, #4E0A0A, #1E0606) with pure white for the skull and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a SMALL ROUND BOMB in flight, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: flying left it is flipped over): a round red bomb 6 squares across with a white highlight on its upper right and the same on its lower right, a short trail of yellow-orange fuse sparks streaming behind it (to the left, 4 squares long, mirrored top to bottom); the sparks flicker differently in each frame.
Layout: one horizontal row of 3 equal 10:8 cells, image size 480x128 (each cell 160x128, 16 px a square); the bomb flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `ziggs_fx_p_bomb.png`：被动「一触即发」的强化炸弹（飞行中），3 帧循环

被动触发时扔出去的大一号炸弹：红色圆炸弹（约 8 格）外面裹着一圈蓝白色的海克斯电光，身后拖着更长的火星和蓝光尾巴（参考 P_Flare）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bomb-shell red ramp (#FFE8E0, #F2564A, #C8281E, #8A1612, #4E0A0A, #1E0606) with pure white for the skull and a Hextech blue-white light ramp (#FFFFFF, #E4F6FF, #9ADCFF, #46A8F0, #2462C0, #123274) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a BIG HEXTECH BOMB in flight, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: flying left it is flipped over): a round red bomb 8 squares across ringed by a crackling Hextech blue-white glow 1-2 squares thick, a trail of yellow-orange sparks and blue-white motes 6 squares long streaming behind it (to the left), mirrored top to bottom; the glow and sparks flicker differently each frame.
Layout: one horizontal row of 3 equal 14:10 cells, image size 672x160 (each cell 224x160, 16 px a square); the bomb flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `ziggs_fx_a_hit.png`：普攻命中：小爆炸（目标身上），4 帧

小炸弹炸开：白芯的橙黄色小火球，几粒火星往外飞，一缕灰烟（参考 FireHit、FlashOrange）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a SMALL BOMB BLAST on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 an orange-yellow fireball 9 squares with a white core; 3 the fireball 12 squares breaking up, sparks flying out at mirrored places, a little grey smoke; 4 grey smoke puffs and two embers.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `ziggs_fx_p_hit.png`：被动命中：海克斯爆炸（目标身上），5 帧

强化炸弹炸开：先一道蓝白色的海克斯星芒闪光（参考 P_Flare、Q_FlareOmni），再一团橙黄色的火球，蓝色电光和火星往外飞。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Hextech blue-white light ramp (#FFFFFF, #E4F6FF, #9ADCFF, #46A8F0, #2462C0, #123274) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a HEXTECH BLAST on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a blue-white star flare 8 squares (4 thin rays); 2 an orange-yellow fireball 12 squares with a white core inside a blue-white ring; 3 the fireball 16 squares, blue sparks and orange embers flying out at mirrored places; 4 the fire breaking into smoke, the ring faint; 5 smoke puffs and blue motes.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `ziggs_fx_q_bomb.png`：Q 弹跳炸弹：空中的炸弹（会被我按不同高度贴在路径上），3 帧

Q 扔出去一跳一跳的炸弹本身：一颗**正立**的红色圆炸弹（约 8 格），正面一个**白色骷髅**，顶上一小截深色引线和黄橙色火星。三帧只是火星闪动（炸弹不转）。**左右对称**。我会把它按弧线的高度一帧帧贴在弹跳路径上，所以这里只画一颗炸弹，炸弹的底边放在格子最底行。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bomb-shell red ramp (#FFE8E0, #F2564A, #C8281E, #8A1612, #4E0A0A, #1E0606) with pure white for the skull and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: THE BOUNCING BOMB itself, upright, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a round red bomb 8 squares across, a clear WHITE SKULL on its front (3 squares wide), a white highlight on its upper left and right, a short dark fuse on top and a yellow-orange spark 2-3 squares on the fuse; the frames differ only in the spark's flicker (the bomb does not turn). Solid: a 1-square dark outline round the bomb is allowed.
Layout: one horizontal row of 3 equal 12:14 cells, image size 576x224 (each cell 192x224, 16 px a square); centered across, the bomb's lowest square on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `ziggs_fx_q_bounce.png`：Q 弹跳：落地没炸的一下（地上），3 帧

炸弹落地弹起（附近没有敌人，没有爆炸）：地上一小圈尘土往两边溅开，几粒火星。**左右对称**，画在格子底部（地面）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a BOUNCE on the ground, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small dust splash 6 squares wide on the ground line with two sparks; 2 the dust thrown out to both sides 14 squares wide and 4 tall; 3 faint settling dust.
Layout: one horizontal row of 3 equal 16:8 cells, image size 768x128 (each cell 256x128, 16 px a square); centered across, the dust's base on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `ziggs_fx_q_hit.png`：Q 炸中（目标身上），4 帧

弹跳炸弹炸到敌人：白芯的橙色火光加黑灰色的冲击碎片（参考 Q_BlastShapes、Q_cinder）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a BOMB HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 an orange burst 10 squares with a white core and dark spiky blast shapes round it at mirrored places; 3 the burst 14 squares and thinner, embers flying out; 4 smoke wisps and embers.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `ziggs_fx_q_blast.png`：Q 爆炸：炸弹在地上炸开（地上，不跟随），6 帧

弹跳炸弹在落点炸开（半径约 20 格）：一道白光，地上冒起一团橙黄色的火球，周围一圈尖刺状的爆炸冲击（参考 Q_BlastShapes、Q_explosion_smoke、Q_ringglow），然后变成一团往上翻的灰烟，地上留下一圈焦黑的痕迹淡去。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a BOMB EXPLOSION on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares just above the ground; 2 an orange-yellow fireball 18 squares wide rising from the ground with a white core, a ring of spiky orange blast shapes along the ground (an ellipse 30 squares wide and 9 tall); 3 the fireball 26 squares wide and 22 tall, dark debris and embers flying out and up at mirrored places; 4 the fire turning into rolling grey smoke 30 squares wide, its top 30 squares above the ground; 5 the smoke thinner and higher, a dark scorch ellipse on the ground; 6 faint smoke and the scorch fading.
Layout: one horizontal row of 6 equal 40:36 cells, image size 3840x576 (each cell 640x576, 16 px a square); centered across, the ground (the explosion's base) 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `ziggs_fx_e_throw.png`：E 雷区：飞出去的一把地雷（飞行中），2 帧循环

扔出去的一把地雷：三颗小小的圆地雷（每颗 4 格，深灰金属壳、中间一点红灯）挤成一团，身后一点火星。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424) and a warning red ramp (#FFFFFF, #FFD0C8, #FF7A66, #E8302A, #A0141A, #560A10) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: A HANDFUL OF MINES in flight, 2 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: flying left it is flipped over): three small round mines 4 squares each (dark grey metal shells, a red light in each middle) clustered together (one in front, two behind mirrored top and bottom), a few sparks trailing to the left; the red lights blink between the frames.
Layout: one horizontal row of 2 equal 12:10 cells, image size 384x160 (each cell 192x160, 16 px a square); the bomb flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `ziggs_fx_e_land.png`：E 地雷落地散开（地上，不跟随），4 帧

一把地雷落在地上四散开（雷区是从斜上方看的扁椭圆：宽 60 格、高 22 格）：中间一点白光，尘土往外溅成一圈（参考 BlastRing、E_SoftIndicator），最后尘土淡去。**左右对称**，中间空着（地雷本身在 e_field 里画）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: MINES LANDING on the ground seen from above at an angle, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares at the ellipse's middle; 2 a ring of dust thrown out along an ellipse 40 squares wide and 15 tall; 3 the dust ring 60 squares wide and 22 tall and thinner; 4 faint dust on the ellipse.
Layout: one horizontal row of 4 equal 64:26 cells, image size 4096x416 (each cell 1024x416, 16 px a square); centered across, the ellipse's middle 11 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `ziggs_fx_e_field.png`：E 雷区：躺在地上的地雷（地上，不跟随，循环），3 帧

雷区持续的时候：扁椭圆范围（宽 60 格、高 22 格）里散着**十颗小地雷**（每颗约 4×3 格：深灰金属壳，顶上一个红灯，近的大一点、远的小一点），地上一圈很淡的红色范围线（参考 E_SoftIndicator、color-bombground）。三帧里地雷的红灯轮流一亮一暗，第 3 帧接得回第 1 帧。**左右对称**（十颗地雷左右成对摆）。地雷是实心的东西，可以有一圈深色边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424) and a warning red ramp (#FFFFFF, #FFD0C8, #FF7A66, #E8302A, #A0141A, #560A10).
Effect: A MINEFIELD lying on the ground seen from above at an angle, 3 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a faint thin red ring on the ground (an ellipse 60 squares wide and 22 tall, 1 square thick, dotted so it reads faint); inside it TEN SMALL MINES scattered evenly in mirrored pairs (each 4 squares wide and 3 tall: a dark grey metal dome with a lighter top edge and a red light on top; the near ones (lower) a little bigger, the far ones smaller); the red lights blink in turn (in each frame a different set is bright red with a white centre, the rest dark red); frame 3 flows back into frame 1. Solid mines may have a 1-square dark outline.
Layout: one horizontal row of 3 equal 64:26 cells, image size 3072x416 (each cell 1024x416, 16 px a square); centered across, the ellipse's middle 11 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `ziggs_fx_e_hit.png`：E 地雷炸中（目标身上），4 帧

踩中地雷：脚下一团橙色的小爆炸，夹着蓝白色的海克斯火花（参考 Q_Sparks、FlashOrange）。**左右对称**。约 16 格，偏低（在脚边）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a Hextech blue-white light ramp (#FFFFFF, #E4F6FF, #9ADCFF, #46A8F0, #2462C0, #123274).
Effect: a MINE BLAST at a unit's feet, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash 5 squares low in the cell; 2 an orange burst 12 squares with a white core, blue-white sparks at mirrored places; 3 the burst 16 squares wide breaking up, embers flying up; 4 grey smoke puffs.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered across, the blast's middle 5 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `ziggs_fx_e_slow.png`：E 减速（敌人脚下，1.5 秒，循环），4 帧

被地雷减速的敌人脚下：一圈焦黑冒烟的地面加几粒火星，往下压的感觉。**左右对称**，只画在脚下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424) and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: a SLOW at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a dark smoky ring on the ground (an ellipse 14 squares wide and 4 tall), 4 orange embers on it at mirrored places and small grey smoke wisps; 1 dim, 2 bright, 3 brightest, 4 bright.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered across, the ellipse's middle 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `ziggs_fx_w_blast.png`：W 定点爆破：脚下的炸药包炸开（他脚下，不跟随），6 帧

炸药包在他脚下炸开，把敌人和他自己都炸飞（半径约 30 格）：第 1 帧地上一个灰色的炸药包（参考 Ziggs_Satchel 的样子：灰色帆布包、一圈金属扣）亮起来；第 2 帧白光一闪；第 3 帧一团大的橙黄色爆炸往四周冲开，两边各有几道白色的气浪弧线往外推（参考 Mult_Windblast、Q_Swipe01）；第 4–5 帧碎石和灰烟往外、往上飞（参考 W_rock_debris_blur）；第 6 帧只剩灰烟。**左右对称**，中间身体位置不要整块盖死（a small figure 40 squares wide and 32 tall stands in the middle, not drawn，他在第 3 帧已经被炸飞）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: A SATCHEL CHARGE BLAST at a figure's feet, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a small figure 40 squares wide and 32 tall stands in the middle, not drawn): 1 a grey canvas satchel 8 squares wide and 5 tall with metal clasps on the ground in the middle, glowing orange at its seams; 2 a white flash 14 squares from the satchel; 3 a big orange-yellow blast 34 squares wide and 22 tall bursting out along the ground with a white core, white blast-wave arcs pushing outward on both sides at mirrored places; 4 the blast 44 squares wide, rock chips and dark debris flying out and up; 5 rolling grey smoke 46 squares wide, embers; 6 thin smoke.
Layout: one horizontal row of 6 equal 52:44 cells, image size 4992x704 (each cell 832x704, 16 px a square); centered across, the ground (the satchel's base) 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `ziggs_fx_w_hit.png`：W 炸中（目标身上），4 帧

被炸药包炸飞的敌人身上：橙色火光加白色的气浪弧线。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a BLAST HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 an orange burst 9 squares with white blast-wave arcs on both sides; 3 the burst 12 squares fading, embers; 4 smoke wisps.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `ziggs_fx_r_cast.png`：R 科学的地狱火炮：举在头顶的大炸弹（他身上，跟随），4 帧

他举起超大号的炸弹准备扔：头顶上方一颗**正立的大红炸弹**（约 22 格圆，正面一个大大的白色骷髅（参考 Ziggs_R_Skull），几道金属箍，顶上粗引线和一大团黄橙色火星）。第 1 帧炸弹出现（一圈白光）；第 2–3 帧举着（火星闪动）；第 4 帧炸弹没了（已经扔出去），只剩几粒火星。**左右对称**。炸弹的底边在格子底边往上 32 格（他两只举起的手在炸弹两边下方）；格子下面空着（a small figure 40 squares wide and 32 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bomb-shell red ramp (#FFE8E0, #F2564A, #C8281E, #8A1612, #4E0A0A, #1E0606) with pure white for the skull and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410).
Effect: THE MEGA BOMB held over a figure's head, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a small figure 40 squares wide and 32 tall stands in the middle, not drawn): a BIG upright round red bomb 22 squares across, a big WHITE SKULL on its front (8 squares wide), two dark metal bands round it, a white highlight on its upper left and right, a thick dark fuse on top with a big yellow-orange spark 4 squares; 1 the bomb appearing in a white ring flash; 2 held, the spark bright; 3 held, the spark flickering differently; 4 the bomb gone, only 4 sparks where it was. Solid: a 1-square dark outline round the bomb is allowed.
Layout: one horizontal row of 4 equal 30:60 cells, image size 1920x960 (each cell 480x960, 16 px a square); centered across, the bomb's lowest square 32 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `ziggs_fx_r_bomb.png`：R 飞行中的大炸弹，3 帧循环

飞出去的超大炸弹：红色大圆炸弹（约 16 格）有几道深色金属箍，身后拖着一大串火焰和烟（参考 R_SmokeTrail、Flame_trail_gradient）。**上下对称**（飞向左边时会被上下翻过来），所以飞行中的炸弹上不画骷髅。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bomb-shell red ramp (#FFE8E0, #F2564A, #C8281E, #8A1612, #4E0A0A, #1E0606) with pure white for the skull and a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: THE MEGA BOMB in flight, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (a projectile's picture is turned with its flight: flying left it is flipped over): a big round red bomb 16 squares across with two dark metal bands (straight across, symmetric), a white highlight top and bottom (mirrored), a thick trail of yellow-orange flame and grey smoke 12 squares long streaming behind it (to the left); the flames flicker each frame.
Layout: one horizontal row of 3 equal 28:20 cells, image size 1344x320 (each cell 448x320, 16 px a square); the bomb flies toward the cell's RIGHT edge, its trail behind it on the left, centered vertically. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `ziggs_fx_r_warn.png`：R 落点预警（地上，不跟随，约 1.2 秒），8 帧

大炸弹飞行的 1.2 秒里，落点地上的预警：一圈**红色的圆圈**（从斜上方看的扁椭圆：宽 80 格、高 30 格，参考 R_Ring_Indicator、R_Circle_normal），中间一个小一点的内圈（中心爆炸区，宽 36 格、高 14 格），正中间一个**红白色的骷髅标记**（参考 Ziggs_R_Center_Indicator），8 帧里红圈越来越亮、内圈往里收、骷髅一闪一闪，最后一帧最亮（马上要炸）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a warning red ramp (#FFFFFF, #FFD0C8, #FF7A66, #E8302A, #A0141A, #560A10).
Effect: A TARGET WARNING on the ground seen from above at an angle, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an outer red ring (an ellipse 80 squares wide and 30 tall, 1-2 squares thick) and an inner ring (an ellipse 36 wide and 14 tall), a red-and-white skull mark 10 squares wide flat on the ground in the middle; over the 8 frames the rings grow brighter and the inner ring shrinks a little each frame (36 -> 24 squares wide), the skull blinking (bright in 2, 4, 6, 8); frame 8 the brightest with white edges.
Layout: one horizontal row of 8 equal 84:34 cells, image size 10752x544 (each cell 1344x544, 16 px a square); centered across, the ellipse's middle 15 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `ziggs_fx_r_boom.png`：R 大爆炸（地上，不跟随），8 帧

超大炸弹落地爆炸（外圈半径约 40 格，中心 18 格）：白光一闪，一个巨大的橙黄色火球从地上升起，地上一圈红橙色的冲击波往外扩，火球变成一朵往上翻的蘑菇状灰黑烟云，碎石火星往四周飞，最后地上留下一圈焦黑的痕迹（参考 R_Storm_R_Dome、R_BlastStreaks、R_Colors、common_FB_explosion）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424) and a warning red ramp (#FFFFFF, #FFD0C8, #FF7A66, #E8302A, #A0141A, #560A10).
Effect: A HUGE EXPLOSION on the ground, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 20 squares just above the ground; 2 a huge orange-yellow fireball dome 40 squares wide and 26 tall rising from the ground with a white core; 3 the dome 60 squares wide and 40 tall, a red-orange shockwave ring along the ground (an ellipse 80 squares wide and 28 tall), blast streaks shooting up and out at mirrored angles; 4 the fireball rising into a mushroom of fire and dark smoke 60 squares tall, debris and embers flying out; 5 the mushroom of grey-black smoke 70 tall, the fire inside dimmer; 6 the smoke spreading 80 wide, the ring fading; 7 thinner smoke, a dark scorch ellipse on the ground; 8 faint smoke and the scorch.
Layout: one horizontal row of 8 equal 96:72 cells, image size 12288x1152 (each cell 1536x1152, 16 px a square); centered across, the ground (the explosion's base) 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `ziggs_fx_r_hit.png`：R 炸中（敌人身上），4 帧

被大炸弹炸中的敌人身上：橙红色火光加黑烟和火星。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a fire and spark ramp (#FFFFFF, #FFF6C0, #FFD25A, #FF9A28, #E2541A, #8E2410) and a smoke and dust grey ramp (#F4F0EA, #CFC8BE, #A29A90, #756E68, #4A4644, #262424).
Effect: a HEAVY BLAST HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 an orange-red burst 11 squares with a white core; 3 the burst 14 squares, black smoke and embers at mirrored places; 4 smoke wisps.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `ziggs_fx_a_bomb` | view_projectiles `league_ziggs_a_bomb`（随飞行方向转动；上下对称；循环） | 10 × 8 |
| `ziggs_fx_p_bomb` | view_projectiles `league_ziggs_p_bomb`（随飞行方向转动；上下对称；循环） | 14 × 10 |
| `ziggs_fx_a_hit` | view_effects `league_ziggs_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `ziggs_fx_p_hit` | view_effects `league_ziggs_p_hit`（跟随，画在人物上面；左右对称） | 18 |
| `ziggs_fx_q_bomb` | view_effects `league_ziggs_q_air<高度>`（不跟随；左右对称；由导入脚本按高度抬起） | 12 × 14 |
| `ziggs_fx_q_bounce` | view_effects `league_ziggs_q_bounce`（不跟随，画在人物上面 z 1；左右对称） | 16 × 8 |
| `ziggs_fx_q_hit` | view_effects `league_ziggs_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `ziggs_fx_q_blast` | view_effects `league_ziggs_q_blast`（不跟随，画在人物上面 z 2；左右对称；大图表） | 40 × 36 |
| `ziggs_fx_e_throw` | view_projectiles `league_ziggs_e_throw`（随飞行方向转动；上下对称；循环） | 12 × 10 |
| `ziggs_fx_e_land` | view_effects `league_ziggs_e_land`（不跟随，画在人物下面 z -1；左右对称；大图表） | 64 × 26 |
| `ziggs_fx_e_field` | view_effects `league_ziggs_e_field`（不跟随，画在人物下面 z -1；左右对称；大图表；每 0.25 秒重贴一次，共 5 秒） | 64 × 26 |
| `ziggs_fx_e_hit` | view_effects `league_ziggs_e_hit`（跟随，画在人物上面；左右对称） | 16 |
| `ziggs_fx_e_slow` | view_buffs `league_ziggs_e_slow`（跟随，画在人物下面；左右对称；循环） | 16 × 8 |
| `ziggs_fx_w_blast` | view_effects `league_ziggs_w_blast`（施放者身上播、不跟随，画在人物上面 z 2；左右对称；大图表） | 52 × 44 |
| `ziggs_fx_w_hit` | view_effects `league_ziggs_w_hit`（跟随，画在人物上面；左右对称） | 12 |
| `ziggs_fx_r_cast` | view_effects `league_ziggs_r_cast`（跟随，画在他上面 z 3；左右对称；大图表） | 30 × 60 |
| `ziggs_fx_r_bomb` | view_projectiles `league_ziggs_r_bomb`（随飞行方向转动；上下对称；循环；大图表） | 28 × 20 |
| `ziggs_fx_r_warn` | view_effects `league_ziggs_r_warn`（不跟随，画在人物下面 z -2；左右对称；大图表） | 84 × 34 |
| `ziggs_fx_r_boom` | view_effects `league_ziggs_r_boom`（不跟随，画在人物上面 z 2；左右对称；大图表） | 96 × 72 |
| `ziggs_fx_r_hit` | view_effects `league_ziggs_r_hit`（跟随，画在人物上面；左右对称） | 14 |

- 两张表：`asset/league/effects/league_ziggs_fx`（小的）和 `league_ziggs_big`（q_blast、e_land、e_field、w_blast、r_cast、r_bomb、r_warn、r_boom），tag = 名字（build_ziggs.py 的 views）。`q_bomb` 不直接绑定：导入时按 build_ziggs.air_heights 的高度把它抬起，生成 `q_air<h>` 各 tag（每个 3 帧，50 ms）。
- 投射物 `a_bomb`、`p_bomb`、`e_throw`、`r_bomb` 是 view_projectiles（随飞行方向转动，断言上下对称）；其余断言左右对称。`e_field` 每 15 tick 在落点重贴一次（3 帧 × 83 ms），`r_warn` 8 帧铺满飞行的 70 tick。`w_blast` 不跟随（他被炸飞后爆炸留在原地）。
- 用 `pixel_1x/` 切格（import_jarvaniv_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。
