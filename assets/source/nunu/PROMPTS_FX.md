# 雪原双子 努努和威朗普：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型已定（`design/nunu_design.png`：Q 版的大雪人威朗普——淡蓝白毛、蓝色螺旋纹、发蓝光的眼睛、棕色大鹿角——头上骑着小男孩努努，蓝兜帽、橙斗篷）。他们在游戏里是**高清**的（每个游戏格子里 1.37×1.37 个细像素），46 格高、38 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/nunu_size.png`：努努和威朗普放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里努努自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。**努努和威朗普来自冰雪的弗雷尔卓德，所有特效都是冬天的魔法**：压实的**白雪**、**冰蓝色的冰和寒气**、威朗普身上**发光的青色螺旋**、**冰晶**、雪粉和一点泥土，不要光滑的霓虹光束，也不要火。
> - **威朗普推的大雪球不在这份里**：它画在他推雪球的动作帧里（姿势包）；这里只画雪球滚动扬起的雪尘、撞碎时的爆开和打中的人身上。
> - **特效要亮**：每片雪、每道冰光都有最亮一档或白色的高光，暗底上一眼能看见。
> - **雪、冰光、寒气、冲击波都没有黑描边**（雪块和冰块也不要描黑边，用它自己最深的一档）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`e_ball`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `nunu_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/nunu_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/nunu_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 威朗普用爪子拍 | `a_hit` |
| 被动「弗雷尔卓德的召唤」（并入 Q 吞噬） | 每第 3 下普攻是威朗普咬一口（回血，对小兵野怪更痛）；咬完他们和一个队友加攻速移速，普攻溅射周围 | `q_hit` · `p_on` · `p_buff` · `p_hit` |
| 技能 1 =「史上最大雪球！」 | 威朗普推着雪球冲向敌人，滚得越远越大，撞上把人击飞 | `w_dust` · `w_hit` · `w_burst` · `w_big` |
| 技能 2 =「雪球飞射」 | 努努连扔 6 个雪球（打中减速），扔完把被打中的英雄冻住 | `e_ball` · `e_hit` · `e_slow` · `e_mark` · `e_root_hit` · `e_root` |
| 大招 =「绝对零度」 | 原地引导一阵大暴风雪，圈里的人越来越慢，自己有冰护盾，结束时整圈爆开 | `r_storm` · `r_slow` · `r_shield` · `r_burst` · `r_hit` |

连招：**雪球 → 雪球飞射**（雪球把人撞飞，努努接着扔），**雪球飞射 → 绝对零度**（冻住的人跑不掉，大招引导更快），**绝对零度 → 吞噬**（暴风雪爆开后威朗普咬一口）。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**雪、冰光、寒气、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **都是冬天的魔法**：白雪、冰蓝寒气、青色螺旋光、冰晶、雪粉；每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 白雪：`#FFFFFF`、`#F2FAFF`、`#D4ECFA`、`#A8CCE8`、`#7898C0`；
  - 冰蓝寒气：`#FFFFFF`、`#D8F4FF`、`#96DCFF`、`#4CA8F0`、`#2468C8`、`#10347A`；
  - 威朗普的青光：`#FFFFFF`、`#C8FFFF`、`#6CF0FF`、`#20C0E8`、`#0A7AB0`；
  - 冰晶：`#FFFFFF`、`#E4FAFF`、`#B4E8F8`、`#74C0E0`、`#3C88B0`；
  - 泥土：`#E8DCC8`、`#B8A890`、`#887860`、`#584C3C`；
- 打中、爆发居中画，不旋转；地面上的圈（雪尘、冰圈、冲击波）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `nunu_fx_a_hit.png`：普攻：威朗普的爪子拍中，3 帧

威朗普一爪子拍在敌人身上：一团白色的雪粉炸开，几道冰蓝色的爪痕光（参考 attack_swipe、ba_flash_sharp）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A).
Effect: A CLAW SWIPE LANDING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares across; 2 a puff of white snow powder 11 across with two short frost-blue claw streaks crossing in an X; 3 the snow powder drifting out and fading. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `nunu_fx_p_hit.png`：被动溅射：拍到周围的人，3 帧

弗雷尔卓德的召唤期间，威朗普的普攻溅到旁边的敌人：一小团冰蓝色的雪雾。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A), a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0).
Effect: A SMALL SPLASH OF FROST on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a frost-blue flash 3 across; 2 a ring of frost-blue snow powder 9 across; 3 the powder fading. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `nunu_fx_q_hit.png`：被动里的吞噬：威朗普咬一口，4 帧

威朗普张嘴一口咬下去：**上下两排白色的大牙印**合上（参考 q_biteswipe），一团雪粉和冰屑炸开，几颗青色的光点往上飘。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a glowing cyan ramp (#FFFFFF, #C8FFFF, #6CF0FF, #20C0E8, #0A7AB0).
Effect: A BIG BITE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two rows of big white pointed teeth shapes, an upper row and a lower row 14 squares wide, open with a gap of 8 squares; 2 the rows snapping shut in the middle, a white flash; 3 a burst of snow powder and ice chips 15 across; 4 the powder fading, a few glowing cyan motes rising. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `nunu_fx_p_on.png`：弗雷尔卓德的召唤：自己脚下的寒风，4 帧循环

被动触发后努努和威朗普脚下：一圈**青色发光的寒风旋**往前卷（参考 nunu_wind_swirl、p_bufftransfer），几粒雪花。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing cyan ramp (#FFFFFF, #C8FFFF, #6CF0FF, #20C0E8, #0A7AB0), a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0).
Effect: A WINTER WIND on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Nunu & Willump stand in the middle, not drawn: 37 squares wide and 46 tall: a ring of glowing cyan wind streaks 38 squares wide and 10 tall swirling round the feet, mirrored, a few white snowflakes in it; the streaks turn a step round the ring each frame. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 40:12 cells, image size 2560x192 (each cell 640x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `nunu_fx_p_buff.png`：弗雷尔卓德的召唤：队友脚下的寒风，4 帧循环

被动给附近一个队友加攻速移速：他脚下一圈小的青色寒风旋，和 p_on 一样的画法，小一号。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing cyan ramp (#FFFFFF, #C8FFFF, #6CF0FF, #20C0E8, #0A7AB0), a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0).
Effect: A SMALL WINTER WIND on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a ring of glowing cyan wind streaks 18 squares wide and 6 tall, mirrored, two snowflakes; the streaks turn a step each frame. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 20:8 cells, image size 1280x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `nunu_fx_w_dust.png`：史上最大雪球：滚动时扬起的雪尘，6 帧

威朗普推着雪球开始滚的那一下，地上扬起的一团雪尘和碎冰（参考 w_hit_dust、w_trail、snowdust）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a dirt ramp (#E8DCC8, #B8A890, #887860, #584C3C).
Effect: SNOW KICKED UP, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred: 1 a low white puff 8 wide; 2 two puffs of snow rolling out to both sides 18 wide, a few dirt pebbles; 3 the puffs 24 wide and 6 tall; 4 the puffs 26 wide, thinning; 5 wisps of snow; 6 a few flakes. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 28:12 cells, image size 2688x192 (each cell 448x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `nunu_fx_w_hit.png`：史上最大雪球：撞中的人身上，4 帧

被雪球撞飞的人身上：一团白色的雪块和冰屑炸开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A).
Effect: A SNOWBALL HIT ON A UNIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 across; 2 chunks of packed snow bursting out 14 across at mirrored places, frost-blue shading on their undersides; 3 the chunks 17 across, smaller, with snow powder; 4 the powder fading. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `nunu_fx_w_burst.png`：史上最大雪球：小雪球撞碎，6 帧

雪球滚得不远就撞上：雪球**炸成一大团雪块**，雪粉往两边喷，地上一圈白雪（参考 w_hit_flash、w_hit_dust、snow_chunks）。**左右对称**，6 帧。**只画爆开的雪球本身，背景纯黑：不要画雪地、沙地、地面、天空或任何风景**（第一次交回的图画了一片雪地和沙地当背景，抠不出来）；6 格一样宽、等距排成一排。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A), a dirt ramp (#E8DCC8, #B8A890, #887860, #584C3C).
Effect: A SNOWBALL SHATTERING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the ball's centre 8 squares above the ground in the cell's middle: 1 a white flash 14 across; 2 the ball bursting into big chunks of packed snow flying out 28 across at mirrored places, frost-blue shading under them; 3 the chunks 36 across and falling, snow powder spraying up 10 squares; 4 the chunks landing in a ring of snow 38 wide on the ground; 5 the powder settling; 6 a low drift of snow and a few flakes. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire. ONLY the burst itself on a PLAIN BLACK background: no snowfield, no sand, no ground strip, no sky, no scenery behind or under it (the snow ring on the ground is part of the burst, drawn on the black).
Layout: one horizontal row of 6 equal 40:26 cells, image size 3840x416 (each cell 640x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `nunu_fx_w_big.png`：史上最大雪球：滚大了的雪球撞碎，7 帧

雪球滚得远、滚得大再撞上：比 w_burst 大一圈，**一圈冰蓝色的冲击波**贴着地面扩开，雪块飞得更高更远。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A), a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0).
Effect: A GIANT SNOWBALL SHATTERING, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the ball's centre 12 squares above the ground in the cell's middle: 1 a white flash 20 across; 2 the ball bursting, big snow chunks flying out 36 across; 3 a frost-blue shockwave ring on the ground 40 wide and 12 tall, the chunks 48 across and rising, snow powder spraying 16 up; 4 the ring 52 wide, the chunks falling; 5 the chunks landing in a snow ring, ice crystals glinting; 6 the powder settling; 7 a low drift and a few glints. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 7 equal 56:34 cells, image size 6272x544 (each cell 896x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `nunu_fx_e_ball.png`：雪球飞射：飞出去的小雪球，4 帧循环

努努扔出的小雪球：一颗白色的雪球（4 格大），后面一道冰蓝色的雪粉尾巴（参考 e_snowball、e_missile_trail）。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A).
Effect: A SMALL FLYING SNOWBALL, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round white snowball 4 squares across at the front (right), one white highlight square in its middle row, frost-blue shading on its back half, and a trail of frost-blue snow powder 7 squares long behind it on the left; the trail flickers a step each frame. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `nunu_fx_e_hit.png`：雪球飞射：雪球打中，3 帧

小雪球砸在人身上：一小团白色雪粉炸开（参考 e_hit_flash、e_snow_spark）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A).
Effect: A SNOWBALL SPLAT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 3 across; 2 a star of white snow powder 9 across; 3 the powder falling and fading. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `nunu_fx_e_slow.png`：雪球飞射：被打中减速，4 帧循环

被雪球打中的人脚下：一圈积雪和冰蓝色的寒气（参考 e_ground_pool_erosion）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A).
Effect: A PATCH OF SNOW on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a low patch of white snow 14 squares wide and 4 tall with frost-blue cold mist curling over it, mirrored; the mist curls a step each frame. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `nunu_fx_e_mark.png`：雪球飞射：被打中的英雄头上的雪花记号，4 帧循环

被雪球打中的英雄头顶：一枚**冰蓝色的雪花记号**一闪一闪（参考 e_mark），提醒扔完会把他冻住。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0), a glowing cyan ramp (#FFFFFF, #C8FFFF, #6CF0FF, #20C0E8, #0A7AB0).
Effect: A SNOWFLAKE MARK floating over a head, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a six-armed snowflake 8 squares across drawn in pale ice-blue lines with a glowing cyan centre; it pulses brighter in frames 2-3. The cell's bottom sits on top of the head. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `nunu_fx_e_root_hit.png`：雪球飞射：冻住的那一下，5 帧

扔完雪球后，被打中的英雄**脚下冒出冰柱把他冻住**的那一下：冰尖从地里刺出来，冰屑炸开（参考 e_icerock、e_vfx_root_snow、e_ice_sparks）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A), a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0).
Effect: ICE BURSTING UP AROUND A UNIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a frost-blue crack on the ground 16 wide; 2 pale ice spikes stabbing up round the feet to 8 squares high at mirrored places; 3 the spikes 14 high with ice chips and snow flying out; 4 the spikes standing, a white glint on each; 5 the chips gone, the spikes still. The body's place left empty. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 5 equal 22:30 cells, image size 1760x480 (each cell 352x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `nunu_fx_e_root.png`：雪球飞射：被冻住，4 帧循环

被冻住的英雄：**腿上包着一圈冰块**（从脚到膝盖），冰上一点白色的反光在闪。**只画腿外面一圈冰，身体位置留空**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0), a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A).
Effect: ICE SHACKLES on the legs, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the bottom of a standing unit 16 squares wide in the middle, not drawn: a jagged block of pale ice 18 squares wide and 12 tall round the feet and shins, its outer facets in 3 ice shades, a few frost-blue cracks, a white glint that moves to a new facet each frame. The legs' place inside left mostly see-through: only the ice's rim and facets. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 20:14 cells, image size 1280x224 (each cell 320x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `nunu_fx_r_storm.png`：绝对零度：引导中的暴风雪，6 帧循环

努努和威朗普引导大招：脚下一大圈**冰蓝色的冰霜圆**（参考 r_ground、r_ring_outer、r_icecrack），圈里刮着**白色的雪花**和寒风往中间卷（参考 r_snow_flake、r_snowdrift）。圈很大（直径约 110 格），**只画地上的冰圈和飘的雪，中间他们站的位置留空**。**左右对称**，6 帧循环（引导约 2.5 秒）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A), a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0), a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0).
Effect: A BLIZZARD ON THE GROUND, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): a big frost-blue ring 108 squares wide and 36 tall on the ground, its edge a band of ice crystals and frost cracks, a faint frost fill inside; white snowflakes and streaks of wind swirling over the ring towards its middle at mirrored places, up to 8 squares above the ground; the flakes and streaks move a step round the ring each frame. The middle 40 squares left clear (they stand there). everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 110:44 cells, image size 10560x704 (each cell 1760x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `nunu_fx_r_burst.png`：绝对零度：引导结束的爆发，7 帧

大招结束那一下：整个冰圈**猛地炸开**，白光一闪，冰柱和冰屑从圈里往上刺，一圈白色的寒气冲击波往外扩（参考 r_circle_splash、p_nova_ground、z_crystals）。**左右对称**，7 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a frost-blue ramp (#FFFFFF, #D8F4FF, #96DCFF, #4CA8F0, #2468C8, #10347A), a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0), a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0).
Effect: THE BLIZZARD EXPLODING, 7 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred: 1 a huge white-blue flash over the whole ring 100 wide and 30 tall; 2 jagged ice spikes stabbing up across the ring to 16 squares high, a frost-blue shockwave ring 104 wide; 3 the spikes shattering into ice chips flying up and out, white cold mist rolling; 4 the chips falling, the mist ring 108 wide and low; 5 frost cracks glowing on the ground; 6 the mist thinning; 7 a few flakes and glints. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 7 equal 110:50 cells, image size 12320x800 (each cell 1760x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `nunu_fx_r_hit.png`：绝对零度：爆发打中的人，4 帧

被大招爆发打中的人身上：一团冰屑和白色寒气炸开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0), a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0).
Effect: A FROST BURST ON A UNIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 across; 2 shards of pale ice bursting out 13 across; 3 the shards 15 across with white cold mist; 4 the mist fading. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `nunu_fx_r_slow.png`：绝对零度：圈里被减速，4 帧循环

在暴风雪里被减速的人：身上**结了一层霜**（身体外圈一圈白色的霜边），雪花打在他身上。**只画外圈，身体位置留空**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0), a snow ramp (#FFFFFF, #F2FAFF, #D4ECFA, #A8CCE8, #7898C0).
Effect: FROSTED OVER, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall: a thin rim of white frost 1 square outside the body's edge (an upright shape 16 wide and 34 tall, drawn only as its rim, the inside empty), little ice crystals stuck on it at mirrored places, a few snowflakes blowing past; the flakes move a step each frame. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 4 equal 18:36 cells, image size 1152x576 (each cell 288x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `nunu_fx_r_shield.png`：绝对零度：引导中的冰护盾，6 帧循环

引导大招时努努和威朗普身上的护盾：一层**半透明的淡冰蓝色冰壳**围着他们（只画外圈的冰棱和几道反光），上面有寒气飘（参考 z_shieldring）。**只画外圈，身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale ice ramp (#FFFFFF, #E4FAFF, #B4E8F8, #74C0E0, #3C88B0), a glowing cyan ramp (#FFFFFF, #C8FFFF, #6CF0FF, #20C0E8, #0A7AB0).
Effect: AN ICE SHELL round them, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Nunu & Willump stand in the middle, not drawn: 37 squares wide and 46 tall: a dome-shaped rim of pale ice 42 squares wide and 48 tall drawn only as its edge (2 squares thick) with ice facets and 3-4 white glints, a glowing cyan line along its base on the ground, wisps of cold mist rising from it; the glints move round the rim a step each frame. The inside left empty. everything is the FRELJORD's winter magic: packed white snow, frost-blue ice, glowing cyan swirls, pale ice crystals, snow puffs and a little dirt; flat shades, crisp shapes; no smooth neon beams, no fire.
Layout: one horizontal row of 6 equal 44:50 cells, image size 4224x800 (each cell 704x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `nunu_fx_a_hit` | view_effects `league_nunu_a_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `nunu_fx_p_hit` | view_effects `league_nunu_p_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `nunu_fx_q_hit` | view_effects `league_nunu_q_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `nunu_fx_p_on` | view_buffs `league_nunu_p_on`（跟随，脚下，z -1；左右对称） | 40 × 12 |
| `nunu_fx_p_buff` | view_buffs `league_nunu_p_buff`（跟随队友，脚下，z -1；左右对称） | 20 × 8 |
| `nunu_fx_w_dust` | view_effects `league_nunu_w_dust`（地上，不跟随，z -1；左右对称） | 28 × 12 |
| `nunu_fx_w_hit` | view_effects `league_nunu_w_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `nunu_fx_w_burst` | view_effects `league_nunu_w_burst`（大表，地上，不跟随，z 2；左右对称） | 40 × 26 |
| `nunu_fx_w_big` | view_effects `league_nunu_w_big`（大表，地上，不跟随，z 2；左右对称） | 56 × 34 |
| `nunu_fx_e_ball` | view_projectiles `league_nunu_e_ball`（弹道，z 2；上下对称） | 12 × 8 |
| `nunu_fx_e_hit` | view_effects `league_nunu_e_hit`（跟随目标，z 2；左右对称） | 10 × 10 |
| `nunu_fx_e_slow` | view_buffs `league_nunu_e_slow`（跟随，脚下，z -1；左右对称） | 16 × 8 |
| `nunu_fx_e_mark` | view_buffs `league_nunu_e_mark`（跟随，头顶，z 3；左右对称） | 10 × 10 |
| `nunu_fx_e_root_hit` | view_effects `league_nunu_e_root_hit`（跟随目标，z 2；左右对称） | 22 × 30 |
| `nunu_fx_e_root` | view_buffs `league_nunu_e_root`（跟随，脚下，z 3；左右对称） | 20 × 14 |
| `nunu_fx_r_storm` | view_effects `league_nunu_r_storm`（大表，跟随，z -1；左右对称） | 110 × 44 |
| `nunu_fx_r_burst` | view_effects `league_nunu_r_burst`（大表，地上，不跟随，z 2；左右对称） | 110 × 50 |
| `nunu_fx_r_hit` | view_effects `league_nunu_r_hit`（跟随目标，z 2；左右对称） | 16 × 20 |
| `nunu_fx_r_slow` | view_buffs `league_nunu_r_slow`（跟随，身上，z 3；左右对称） | 18 × 36 |
| `nunu_fx_r_shield` | view_buffs `league_nunu_r_shield`（跟随他们，z 3；左右对称） | 44 × 50 |

- 两张表：`asset/league/effects/league_nunu_fx`（小的）和 `league_nunu_big`（w_burst、w_big、r_storm、r_burst），tag = 名字（build_nunu.py 的 views）。雪球本身在威朗普的 skill / skill_roll 帧里（姿势包），w_dust 垫在起滚那一下，w_burst / w_big 是撞上的那一下（滚的时间短 / 长）。
- 弹道（e_ball）断言上下对称；其余断言左右对称；r_storm 跟随他们引导约 2.5 秒（循环），r_shield 同时长，e_root 0.75 秒。
- 用 `pixel_1x/` 切格（import_illaoi_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
