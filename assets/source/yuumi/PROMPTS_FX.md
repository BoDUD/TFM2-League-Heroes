# 魔法猫咪 悠米：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型和动作已定（`design/yuumi_idle.png`：淡紫蓝色的 Q 版小猫，坐在一本会飞的深红金边魔法书里，金色头饰、金触须挂着蓝色小球，尾巴尖一簇金毛）。她在游戏里是**高清**的、而且**画小了**（25 格高、23 格宽，比一般英雄矮一截）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/yuumi_size.png`：她在游戏里的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士（一般英雄的大小）。每条写的大小都是游戏像素（格）。
> - `design/yuumi_shots.png`：定稿动作（游戏里的大小，4 倍），青色十字是她的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里悠米自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的光是金色的星光和粉紫色的魔法**，**治疗是粉色的小爱心**，**大招的波纹是粉紫色带金边**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、头上、脚下、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道图**（光弹、飞弹、波纹）**朝右飞、尾巴在左边，严格上下对称**（游戏按飞行方向转这张图，往左飞时是倒过来的）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `yuumi_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/yuumi_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/yuumi_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（被动「猫的博爱」在里面） | 射出一颗小光弹；每隔几秒普攻英雄多一段伤害并给自己回血 | `a_bolt` · `a_hit` · `p_hit` · `p_heal` |
| 技能 1 = Q「摸鱼飞弹」 | 飞弹直线飞向敌人，飞得够久就强化：伤害更高、减速更强 | `q_missile` · `q_hit` · `q_ehit` · `q_slow` · `q_eslow` |
| 技能 2 = W「悠米出动！」+ E「旺盛精力」 | 扑到交战中的队友身上附身（趴在他头上），给他护盾、攻速移速，附身期间他持续回血；时间到跳下来 | `w_jump` · `e_hit` · `e_haste` · `w_heal` · `w_land`（头上的小猫另有一包） |
| 大招「魔典终章」 | 把书立起来，朝目标连发 5 道波纹：伤敌减速、治疗沿途队友，第 3 道定身 | `r_cast` · `r_wave` · `r_hit` · `r_heal` · `r_root` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、星点、爱心、波纹、光环、魔法阵都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 金色的星光：`#FFFFFF`、`#FFF4C8`、`#FFDC6E`、`#F5B33A`、`#C97A1C`、`#7A4210`；
  - 粉紫色的魔法：`#FFFFFF`、`#FFE0F6`、`#FFA3DE`、`#E070D8`、`#A848C8`、`#5E2488`；
  - 粉色的爱心（治疗）：`#FFFFFF`、`#FFE4EE`、`#FF9EC4`、`#F0628E`、`#C03A6A`、`#6E1E3E`；
- 打中、爆发居中画，不旋转；地面上的圆（魔法阵、减速圈、加速圈、落地的光环）是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：她的普攻射程 50000，飞弹最远飞 100000，大招的波纹宽 24000）。

### 1. `yuumi_fx_a_bolt.png`：普攻：书页光弹（弹道，循环），4 帧

她普攻弹出去的小光弹：一颗粉紫色的小魔法球，白芯，后面拖一小串金色的星点（参考 core、sparkle、z_spark）。**朝右飞，尾巴在左边，上下严格对称**（游戏按飞行方向转这张图，往左飞时是倒过来的），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A LITTLE MAGIC BOLT, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round pink-violet orb 4 squares across with a white core at the right, a short trail of 3-4 gold sparkle squares behind it to the left; each frame the core flickers and the sparkles shift.
Layout: one horizontal row of 4 equal 10:8 cells, image size 640x128 (each cell 160x128, 16 px a square); the orb's middle on the cell's middle row, 3 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `yuumi_fx_a_hit.png`：普攻：光弹打中目标，3 帧

光弹打中的一下：一团粉紫色的小闪光，四周溅出几粒金色的星点（参考 e_flash、z_spark）。**左右对称**，约 12 × 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A SMALL MAGIC HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink four-pointed flash 6 squares across; 2 the flash 9 across with 6 gold sparkle squares flying out; 3 only the sparkles further out, fading.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `yuumi_fx_p_hit.png`：猫的博爱：强化普攻打中，4 帧

被动「猫的博爱」那一下：一颗金白色的星形闪光，中间冒出一个粉色的小爱心，一圈金色、粉紫色的星点往外散（参考 ba_tar_star、z_scribbles 的爱心、sparkle）。**左右对称**，约 16 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210), a pink heart ramp (#FFFFFF, #FFE4EE, #FF9EC4, #F0628E, #C03A6A, #6E1E3E) and a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488).
Effect: A STAR-AND-HEART BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold star flash 8 squares across; 2 the flash 12 across with a small pink heart (5 squares wide) in its middle; 3 a ring of 8 gold and pink-violet sparkles 15 across, the heart rising a square; 4 only twinkling sparkles at the edge.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `yuumi_fx_p_heal.png`：猫的博爱：她自己回血（她身上，跟随），4 帧

被动给自己（附身时也给队友）回血：几个粉色的小爱心和金色星点从她身边慢慢往上飘（参考 z_scribbles 的爱心、p_glow、sparkle）。**围着人画，身体位置留空**，**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink heart ramp (#FFFFFF, #FFE4EE, #FF9EC4, #F0628E, #C03A6A, #6E1E3E) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: HEALING HEARTS round a small unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small cat in her book stands in the middle, not drawn: 24 squares from the top of her antenna to the ground, about 22 squares wide): 1 two small pink hearts (3 squares wide) low at her left and right; 2 the hearts 4 squares higher, two gold sparkles above them; 3 the hearts higher still and a third heart at the top middle, more sparkles; 4 the hearts near the top, fading, the sparkles twinkling out.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered across, the middle of the cell on her middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `yuumi_fx_q_missile.png`：Q 摸鱼飞弹：飞弹（弹道，循环），4 帧

她甩出去的摸鱼飞弹：一颗粉紫色的魔法光球，白芯外面一圈粉紫色的光晕，后面拖一条长长的金色星光尾巴（参考 q_flash、e_flash、wisptrail_add、sparkle）。**朝右飞，尾巴在左边，上下严格对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A PROWLING MAGIC MISSILE, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round pink-violet orb 6 squares across with a white core inside a soft pink glow ring at the right, a tapering trail of gold starlight squares 9 squares long behind it to the left, widest next to the orb; each frame the core pulses and the trail's sparkles drift.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); the orb's middle on the cell's middle row, 4 squares from its right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `yuumi_fx_q_hit.png`：Q：飞弹打中，4 帧

飞弹打中目标：一团粉紫色的闪光，一圈粉紫色的魔法环炸开，几粒金色星点往外飞（参考 q_flash、e_ring、z_spark）。**左右对称**，约 18 × 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A MAGIC IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 8 squares across; 2 the flash 12 across and a thin pink-violet ring 14 across; 3 the ring 18 across, 6 gold sparkles flying out; 4 only fading sparkles and a faint ring.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `yuumi_fx_q_ehit.png`：Q：飞了很远的强化命中，4 帧

飞弹飞得够久、强化打中：比普通命中更大更亮，金白色的星形大闪光，一圈粉紫色的魔法环和一圈金色星点同时炸开（参考 qbv2_gold、fire_tile_gold、q_flash、ba_tar_star）。**左右对称**，约 24 × 24 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210) and a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488).
Effect: A BIG EMPOWERED IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold star flash 10 squares across with 4 long rays; 2 the flash 16 across inside a pink-violet ring 18 across; 3 the ring 22 across and a ring of 8 gold sparkles outside it; 4 only twinkling sparkles and a faint ring.
Layout: one horizontal row of 4 equal square cells, image size 1536x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `yuumi_fx_q_slow.png`：Q：减速（脚下，循环），4 帧

被飞弹减速：敌人脚下贴着地面一小圈粉紫色的魔法光点慢慢转（参考 e_ring、sparkle）。**只画在脚下的地面上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488).
Effect: A SLOWING RING on the ground at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 14 squares wide and 4 tall drawn only as short pink-violet light streaks (1-3 squares) and a few white sparkle squares, mirrored; each frame the streaks move round the ellipse.
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `yuumi_fx_q_eslow.png`：Q：强化减速（脚下，循环），4 帧

强化命中后的大减速：脚下更大更亮的一圈，粉紫色的光环里夹着金色星点（参考 e_ring、qbv2_gold）。**只画在脚下的地面上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A STRONG SLOWING RING on the ground at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 18 squares wide and 6 tall: a thin pink-violet light ring with 6 gold sparkle squares on it at mirrored places; each frame the sparkles move round the ring and the ring brightens and dims.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `yuumi_fx_e_hit.png`：W+E：旺盛精力给到队友（他身上），5 帧

她附身时把「旺盛精力」给队友：队友身上闪起一个金色的护盾泡（只画外圈），两边对称地划过几道金色、粉紫色的速度线，护盾泡收成星点（参考 wv3_shield_trail、e_streak、e_flash）。**围着人画，身体位置留空**，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210) and a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488).
Effect: A SHIELD-AND-SPEED BURST round an ally, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): 1 a thin gold shield outline (an upright oval 22 squares wide and 32 tall, only its rim, 1-2 squares thick) appearing; 2 the rim bright with white highlight squares and 4 gold and pink-violet speed streaks (6-8 squares long) flashing up at its left and right; 3 the rim pulsing, the streaks higher; 4 the rim breaking into gold sparkles; 5 only sparkles drifting up.
Layout: one horizontal row of 5 equal 28:36 cells, image size 2240x576 (each cell 448x576, 16 px a square); centered across, the cell's bottom on the ground. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `yuumi_fx_e_haste.png`：W+E：加速（他脚下，循环），4 帧

旺盛精力的攻速移速：队友脚下贴着地面转的一圈金色、粉紫色的星光条纹（参考 e_streak、wisptrail_add、sparkle）。**只画在脚下的地面上**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210) and a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488).
Effect: A SPEED SWIRL on the ground at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 24 squares wide and 6 tall drawn only as short curved streaks (2-4 squares long) of gold and pink-violet light, mirrored, with a few white sparkle squares; each frame the streaks move round the ellipse.
Layout: one horizontal row of 4 equal 26:8 cells, image size 1664x128 (each cell 416x128, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `yuumi_fx_w_heal.png`：W：附身期间队友回血（他身上），4 帧

她趴在队友头上时，队友每秒回一点血：两三个粉色的小爱心从他胸口往上冒，带几粒金色星点（参考 z_scribbles 的爱心、sparkle）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink heart ramp (#FFFFFF, #FFE4EE, #FF9EC4, #F0628E, #C03A6A, #6E1E3E) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: SMALL HEALING HEARTS on an ally, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 one pink heart 3 squares wide at the middle; 2 two hearts rising at mirrored places, two gold sparkles; 3 the hearts higher, a third small heart; 4 the hearts fading at the top, sparkles twinkling out.
Layout: one horizontal row of 4 equal 16:18 cells, image size 1024x288 (each cell 256x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `yuumi_fx_w_jump.png`：W：她跳走的地方（地上，不跟随），4 帧

她扑向队友时原地留下的一下：一团粉紫色、金色的星光小爆，几粒星点往上飘（参考 e_flash、sparkle、smokeerode）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A SPARKLE PUFF where a small unit leaps away, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink-white flash 8 squares across low over the ground; 2 a puff of pink-violet glow 14 across with 6 gold sparkles; 3 the sparkles drifting up and out, the glow thinner; 4 only a few sparkles high up.
Layout: one horizontal row of 4 equal 18:14 cells, image size 1152x224 (each cell 288x224, 16 px a square); centered across, the puff's bottom 1 square above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `yuumi_fx_w_land.png`：W：她从队友身上跳下来落地（地上，不跟随），4 帧

附身结束、她跳下来落地：脚下一圈金色、粉紫色的星点往两边溅开，一道扁扁的光环（参考 e_ring、sparkle）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210) and a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488).
Effect: A LANDING SPARKLE on the ground, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat white-gold flash 10 squares wide and 3 tall on the ground; 2 a flat pink-violet ring 16 wide and 4 tall, 6 gold sparkles splashing out to the left and right; 3 the ring 20 wide and fainter, the sparkles further out; 4 only a few sparkles.
Layout: one horizontal row of 4 equal 20:12 cells, image size 1280x192 (each cell 320x192, 16 px a square); centered across, the ring's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `yuumi_fx_r_cast.png`：R 魔典终章：翻开魔典时脚下的魔法阵（跟随，大图表），6 帧

她把书立起来放大招：脚下的地面上展开一个粉紫色和金色的魔法阵（椭圆，外圈一道金色的光环，里面一圈粉紫色的花纹和小爱心符号），几片发光的书页从阵里往上飘，然后阵收拢（参考 r_indicator、r_glow、p_decal、z_scribbles）。**只画在地面上（她站在中间，不画人）**，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488), a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210) and a pink heart ramp (#FFFFFF, #FFE4EE, #FF9EC4, #F0628E, #C03A6A, #6E1E3E).
Effect: A MAGIC CIRCLE OPENING on the ground under a small caster, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the small cat in her book stands in the middle, not drawn: 24 squares from the top of her antenna to the ground, about 22 squares wide): 1 a small gold ring on the ground (an ellipse 12 wide and 4 tall); 2 the circle 28 wide and 9 tall, a gold rim with an inner ring of pink-violet scroll-work; 3 the circle 36 wide and 12 tall, small pink heart and spiral glyphs on it at mirrored places, 4 glowing cream page shapes (3x4 squares) rising above it at mirrored places; 4 the same, the pages higher; 5 the circle shrinking to 22 wide; 6 only a thin fading ring and a few sparkles.
Layout: one horizontal row of 6 equal 40:20 cells, image size 3840x320 (each cell 640x320, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `yuumi_fx_r_wave.png`：R：魔典的波纹（弹道，循环，大图表），4 帧

魔典连发出去的波纹：一道竖着的弯月形光波，凸面朝右（朝飞的方向），粉紫色的光身、金色的亮边，后面带几粒金色星点和小书页的光片（参考 r_glow、r_indicator、wisptrail_add、fire_tile_gold）。**朝右飞，严格上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A MAGIC WAVE, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a tall crescent of light 26 squares tall and 6 thick, bulging to the RIGHT (the way it flies), its body pink-violet, its leading (right) edge a bright gold-white line, 4-5 gold sparkle squares and 2 small glowing page flecks trailing behind it on the left at mirrored places; each frame the gold edge shimmers and the sparkles drift back.
Layout: one horizontal row of 4 equal 18:30 cells, image size 1152x480 (each cell 288x480, 16 px a square); the crescent's middle on the cell's middle row, its gold edge 2 squares from the cell's right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `yuumi_fx_r_hit.png`：R：波纹打中敌人，4 帧

波纹扫过敌人：一团粉紫色的闪光，几片发光的书页碎片和金色星点散开（参考 r_glow、q_flash、sparkle）。**左右对称**，约 16 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A WAVE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink-white flash 7 squares across; 2 the flash 11 across with 4 glowing cream page flecks (2x3 squares) flying out at mirrored places; 3 the flecks further out with gold sparkles; 4 only fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `yuumi_fx_r_heal.png`：R：波纹治疗队友，4 帧

波纹扫过队友：队友身上冒起一个粉色的爱心和几粒金色星点（参考 z_scribbles 的爱心、p_glow）。**左右对称**，约 14 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink heart ramp (#FFFFFF, #FFE4EE, #FF9EC4, #F0628E, #C03A6A, #6E1E3E) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A HEALING HEART on an ally, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a pink glow 6 squares across; 2 a pink heart 6 squares wide inside it, 4 gold sparkles round it; 3 the heart rising 3 squares, the sparkles further out; 4 the heart fading at the top.
Layout: one horizontal row of 4 equal 14:16 cells, image size 896x256 (each cell 224x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `yuumi_fx_r_root.png`：R：第三道波纹的定身（脚下，循环），4 帧

被第三道波纹定住：敌人脚下缠着几圈粉紫色的发光书页丝带，带金色的边，丝带上的光一闪一闪（参考 r_indicator、z_scribbles、wisptrail_add）。**只画在脚和小腿的位置**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparkles, hearts, waves, rings or magic circles, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet magic ramp (#FFFFFF, #FFE0F6, #FFA3DE, #E070D8, #A848C8, #5E2488) and a gold starlight ramp (#FFFFFF, #FFF4C8, #FFDC6E, #F5B33A, #C97A1C, #7A4210).
Effect: A BINDING OF GLOWING PAGE-RIBBONS round a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two flat ellipse loops (18 squares wide, 4 tall, one 2 squares above the other) of pink-violet ribbon 1-2 squares thick with a gold edge, wrapped round the space where the legs are (the middle left open), small cream page flecks on them; each frame a bright white-gold glint runs along the ribbons (mirrored).
Layout: one horizontal row of 4 equal 22:14 cells, image size 1408x224 (each cell 352x224, 16 px a square); centered across, the lower loop's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `yuumi_fx_a_bolt` | view_projectiles `league_yuumi_a_bolt`（跟着弹道转向；上下对称） | 10 × 8 |
| `yuumi_fx_a_hit` | view_effects `league_yuumi_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 12 × 12 |
| `yuumi_fx_p_hit` | view_effects `league_yuumi_p_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `yuumi_fx_p_heal` | view_effects `league_yuumi_p_heal`（跟随，画在人物上面 z 2；左右对称） | 18 × 20 |
| `yuumi_fx_q_missile` | view_projectiles `league_yuumi_q_missile`（跟着弹道转向；上下对称） | 16 × 10 |
| `yuumi_fx_q_hit` | view_effects `league_yuumi_q_hit`（跟随目标，画在人物上面 z 2；左右对称） | 18 × 18 |
| `yuumi_fx_q_ehit` | view_effects `league_yuumi_q_ehit`（跟随目标，画在人物上面 z 2；左右对称） | 24 × 24 |
| `yuumi_fx_q_slow` | view_buffs `league_yuumi_q_slow`（跟随，画在人物下面 z 1；左右对称；循环） | 16 × 6 |
| `yuumi_fx_q_eslow` | view_buffs `league_yuumi_q_eslow`（跟随，画在人物下面 z 1；左右对称；循环） | 20 × 8 |
| `yuumi_fx_e_hit` | view_effects `league_yuumi_e_hit`（跟随，画在人物上面 z 2；左右对称） | 28 × 36 |
| `yuumi_fx_e_haste` | view_buffs `league_yuumi_e_haste`（跟随，画在人物下面 z -1；左右对称；循环） | 26 × 8 |
| `yuumi_fx_w_heal` | view_effects `league_yuumi_w_heal`（跟随，画在人物上面 z 2；左右对称） | 16 × 18 |
| `yuumi_fx_w_jump` | view_effects `league_yuumi_w_jump`（不跟随，画在人物下面 z 2；左右对称） | 18 × 14 |
| `yuumi_fx_w_land` | view_effects `league_yuumi_w_land`（不跟随，画在人物下面 z 2；左右对称） | 20 × 12 |
| `yuumi_fx_r_cast` | view_effects `league_yuumi_r_cast`（跟随，画在人物下面 z -1；左右对称；大图表） | 40 × 20 |
| `yuumi_fx_r_wave` | view_projectiles `league_yuumi_r_wave`（跟着弹道转向；上下对称；大图表） | 18 × 30 |
| `yuumi_fx_r_hit` | view_effects `league_yuumi_r_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `yuumi_fx_r_heal` | view_effects `league_yuumi_r_heal`（跟随目标，画在人物上面 z 2；左右对称） | 14 × 16 |
| `yuumi_fx_r_root` | view_buffs `league_yuumi_r_root`（跟随，画在人物上面 z 1；左右对称；循环） | 22 × 14 |

- 两张表：`asset/league/effects/league_yuumi_fx`（小的）和 `league_yuumi_big`（r_cast、r_wave），tag = 名字（build_yuumi.py 的 views）；`w_ride`（附身的小猫）来自 pack_yuumi_ride.py 的交付，也进 `league_yuumi_big`。
- 弹道图（a_bolt、q_missile、r_wave）断言上下对称，其余断言左右对称；`w_jump`、`w_land` 不跟随（起跳点、落点）。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
