# 北地之怒 瑟庄妮：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型已定（`design/sejuani_design.png`：Q 版的瑟庄妮——青铜金头盔、两只蓝冰角、紫皮甲、米白毛领、棕黑相间的链枷和蓝色冰锤头——骑在灰蓝毛、白鬃毛、两根象牙色大獠牙的野猪钢鬃背上）。她在游戏里是**高清**的（每个游戏格子里约 2×2 个细像素），36 格高、42 格宽（高×宽，冰角尖到蹄子）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/sejuani_size.png`：瑟庄妮放大 4 倍，最低点在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里瑟庄妮自己的特效贴图（大多是灰度的形状），按用在我们哪张特效分好了行，只在本地用。**瑟庄妮是北地之怒**：她的力量是**冰霜**——白色到淡蓝的**有棱角的冰晶和冰碴**、**青色的冰光**、冰里深蓝的暗部、**白色的雪粉和风雪**；不要火、不要电、不要烟。
> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。
> - **冰、雪、冲击都没有黑描边**（用它自己最深的一档）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人（冻住的冰笼也是：冰在两边，中间留空）。
> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`w_line`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）；`r_bola` 是圆的，**左右、上下都对称**。
> - **持续的画面**（冰风暴 2 秒、冰霜护甲、减速、霜冻层数）只画几帧循环，Claude 导入时按时长拉开循环；冻住的两张（`e_freeze`、`r_hit`）最后一帧会停住。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `sejuani_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/sejuani_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/sejuani_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 冰锤链枷砸下 | `a_hit` |
| 被动「北地之怒」 | 脱战时冰霜护甲（免疫减速）；霜冻叠满冻住（永冻领域）；打晕住的敌人碎冰 | `fa_armour` · `frost` · `e_freeze` · `sh_hit` |
| 技能 1 =「极寒突袭」 | 钢鬃冲锋，撞飞路上的敌人，撞到英雄停下 | `q_dash` · `q_hit` · `f_mark` |
| 技能 2 =「凛冬之怒」 | 链枷先横扫一圈，再往前砸出一道冰；减速、叠霜冻 | `w_sweep` · `w_line` · `w_hit` · `slow` |
| 大招 =「极冰寒狱」 | 甩出冰套索，冻住第一个英雄，落点冰风暴减速 | `r_bola` · `r_hit` · `r_storm` · `slow` |

连招：**Q 撞飞 → 马上 W**，**W 叠满霜冻 → 冻住**，**晕住（谁晕的都算）→ 碎冰**，**R 冻住 → Q 冲过去**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**冰、雪、冲击没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂；冰晶是有棱角的块，不是圆团。
- **要亮**：每个形状都有最亮一档或白色的亮点。
- 颜色（按每条写的用）：
  - 冰·白到深蓝：`#FFFFFF`、`#E4F8FF`、`#A8E4FF`、`#5CC0F0`、`#2A88D0`、`#14509A`；
  - 冰光·青：`#E8FFFF`、`#8AF4FF`、`#2ED0F0`、`#1488B8`；
  - 雪·白到灰蓝：`#FFFFFF`、`#EEF4FA`、`#CAD8E6`、`#9AAEC4`、`#6A80A0`；
  - 冰里的暗部·深蓝：`#0A2A5A`、`#143C7A`、`#2A5CA8`；
  - 闪光·白：`#FFFFFF`、`#F4FBFF`、`#DCF0FF`；
- 打中、爆发居中画，不旋转；地面上的东西（横扫的环、冰风暴、脚下的冰环）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `sejuani_fx_a_hit.png`：普攻：冰锤砸中，3 帧

冰锤头砸中敌人（参考 basicattack_trail、frostcrystals、sparkles）：中间一下白色闪光，炸开**几块淡蓝色的碎冰**和一点白色雪粉。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF), an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a snow ramp (#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0).
Effect: AN ICE SMACK, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a burst 13 across - four to six pale blue angular ice shards flying out at mirrored places with a puff of white snow powder; 3 the shards further out and smaller, fading. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sejuani_fx_q_dash.png`：极寒突袭：起冲时踢起的雪，4 帧

钢鬃起冲时蹄子底下**踢起一大片雪雾和冰碴**（参考 dust_01、z_smoke_4x4、flurrys）：贴着地面往两边散开的白色雪粉，几块小冰碴飞起来。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0), an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A).
Effect: A SNOW KICK-UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 1 a low puff of white snow 16 squares wide; 2 the snow powder spreading to both sides 30 wide and 8 tall, a few small ice chips flying up at mirrored places; 3 38 wide, thinner; 4 fading wisps at both ends. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 40:12 cells, image size 2560x192 (each cell 640x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sejuani_fx_q_hit.png`：极寒突袭：撞飞，4 帧

被钢鬃撞中挑飞（参考 hiteffect、z_iceshards、sejuani_frostout）：白色的冲击闪光，**一圈冰碴和雪粉往上溅**，像被撞上天。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF), an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a snow ramp (#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0).
Effect: A TUSK IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white impact flash 10 squares across low on the target; 2 ice shards and snow powder bursting UP and out 18 across in a V at mirrored places; 3 the shards high, 21 tall; 4 fading snow specks. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 20:22 cells, image size 1280x352 (each cell 320x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sejuani_fx_f_mark.png`：极寒突袭：撞中英雄的一闪，3 帧

冲锋撞中第一个英雄时，敌人头上一闪的**小冰晶**（参考 e_frostcrystal、sparkles）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8), a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF).
Effect: A FROST GLINT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a tiny white sparkle 3 squares; 2 a cyan six-pointed ice crystal 9 across with a white centre; 3 the crystal fading. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 3 equal square cells, image size 480x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sejuani_fx_w_sweep.png`：凛冬之怒：链枷横扫一圈，5 帧

凛冬之怒第一下（参考 w_swipe_01、w2a_swipe、w_swipepan_mask）：链枷在她身边**横扫一圈**，地上留下一道**冰蓝色的弧形风雪**，弧的两头甩出雪粉和冰碴。从斜上方看是一个扁椭圆的环。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a snow ramp (#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8).
Effect: A SWEEPING FROST ARC, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 1 a thin pale blue arc starting at the front 20 squares wide; 2 the arc grown into a ring 50 wide and 16 tall, white at its leading edges, snow powder streaming off it; 3 the full ring 58 wide and 22 tall, cyan ice light along it, ice chips flung out at mirrored places; 4 the ring breaking into snow; 5 fading. The middle (her body) left empty. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke. Sejuani on her boar stands in the middle, not drawn: 41 squares wide and 36 tall (the ice horn's tip to the hooves).
Layout: one horizontal row of 5 equal 60:24 cells, image size 4800x384 (each cell 960x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sejuani_fx_w_line.png`：凛冬之怒：往前砸出的一道冰，3 帧循环

凛冬之怒第二下（参考 w_tar_hit_flash、w_swipe_01、z_iceshards）：链枷往前猛砸，**一排冰刺沿着地面往前冲**——前头一块大冰刺，后面一串越来越小的冰碴和雪粉。**朝右飞、上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a snow ramp (#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0), a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF).
Effect: A RACING LINE OF ICE, 3 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a jagged pale blue ice spike 8 squares long at the front (white glints on its edges), behind it on the left a row of smaller ice shards and white snow powder 30 long, the shards getting smaller toward the tail; the shards flicker and shift a step back frame to frame. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 3 equal 40:10 cells, image size 1920x160 (each cell 640x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sejuani_fx_w_hit.png`：凛冬之怒：被链枷打中，3 帧

被链枷打中（参考 w_tar_sphere、w_tar_hit_flash）：一团**冰蓝色的光球**炸开，几片碎冰往外飞。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF), an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8).
Effect: A FROST BURST, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan sphere of light 7 squares across on the target's chest; 2 the sphere bursting 15 across into pale blue ice shards at mirrored places; 3 the shards out and fading. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sejuani_fx_e_freeze.png`：永冻领域：冻住，5 帧

霜冻叠满被冻住（参考 e_icering、e_frostcrystal、r_frostmaterial、frostcrystals）：脚下一圈冰环亮起，**一根根冰柱从地上往上长**，围着敌人结成冰笼（**冰柱在两边，身体中间留空**），顶上几颗冰晶闪光。最后一帧冰笼完整、停住。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8), a deep blue ramp for shadows in the ice (#0A2A5A, #143C7A, #2A5CA8), a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF).
Effect: A FREEZE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a cyan ice ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 20 wide; 2 short pale blue ice spikes rising from the ring on both sides, 10 tall; 3 the spikes 24 tall leaning in round the body, deep blue inside the ice, white glints on the edges; 4 the ice cage 36 tall with a few crystals sparkling on top; 5 the full cage held (the last frame, it stays while the stun lasts). The body area in the middle left EMPTY (the unit stays visible through it). everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 5 equal 24:40 cells, image size 1920x640 (each cell 384x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sejuani_fx_sh_hit.png`：碎冰：冰碎开，4 帧

碎冰（参考 z_iceshards、frostout、shockwave）：被冻住的敌人身上**冰块炸成碎片**——白色闪光，大小冰片往四周飞，下面一圈雪粉。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF), an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a snow ramp (#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0).
Effect: A SHATTER, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 12 squares across on the target; 2 big pale blue ice chunks breaking apart and flying out 26 across at mirrored places, a ring of snow powder at the feet; 3 the chunks smaller and further out, 30 tall; 4 a few last shards and snow specks fading. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 28:32 cells, image size 1792x512 (each cell 448x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sejuani_fx_fa_armour.png`：冰霜护甲：她身上的冰霜，4 帧循环

冰霜护甲在身时（参考 passive_shield、passive_shield_activated、sejuani_sheen）：**她和钢鬃外圈一层淡淡的冰蓝色霜光**，几颗小冰晶在外圈一闪一闪。**只画外圈，身体位置留空**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8), an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF).
Effect: A FROST ARMOUR SHEEN, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin broken outline of pale cyan frost light round the unit (1 square thick, gaps in it), 44 squares wide and 38 tall, with three or four small white-cyan ice crystals at mirrored places on it twinkling in turn; the middle EMPTY. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke. Sejuani on her boar stands in the middle, not drawn: 41 squares wide and 36 tall (the ice horn's tip to the hooves).
Layout: one horizontal row of 4 equal 46:40 cells, image size 2944x640 (each cell 736x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sejuani_fx_frost.png`：霜冻层数：敌人头上的雪花，2 帧循环

附加包里每层霜冻挂在敌人身上：头上一个**小雪花**（参考 e_stack_1_c…e_stack_4_c）。**左右对称**，2 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8), a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF).
Effect: A SNOWFLAKE MARK, 2 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small six-armed cyan-white snowflake 7 squares across; frame 2 its centre one shade brighter. Drawn at the TOP of the cell (it sits over the unit's head). everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 2 equal square cells, image size 224x112 (each cell 112x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `sejuani_fx_slow.png`：减速：脚下的风雪，4 帧循环

被减速的敌人脚下：一圈**白色雪粉和冰碴**绕着脚慢慢转。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow ramp (#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0), an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A).
Effect: A SNOW SNARE, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ring of white snow powder and small pale blue ice chips on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 wide and 5 tall, the chips at mirrored places stepping round frame to frame. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 4 equal 18:7 cells, image size 1152x112 (each cell 288x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `sejuani_fx_r_bola.png`：极冰寒狱：飞出去的冰套索，3 帧循环

甩出去的**冰套索**（参考 r_smallbola、r_mis_bolablur、bola_flash）：中间一颗冰蓝色的冰球，外面一圈旋转的白色模糊光环（像绳子转成的圈）。**圆的：左右、上下都对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8), a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF).
Effect: A SPINNING ICE BOLA, 3 looping frames, ROUND: SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, square for square (the game turns it with its flight): a pale blue ice ball 6 squares across with a white glint in the middle, a spinning white-cyan blur ring round it 13 across, its brighter arcs at mirrored places moving round frame to frame (each frame itself symmetric). everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `sejuani_fx_r_hit.png`：极冰寒狱：套中冻住，5 帧

套索打中第一个英雄（参考 r_groundfreeze、r_groundfreezeflash、r_frostmaterial、frostcrystals）：白色闪光，**大块的冰晶从地上猛地长起来把它冻在里面**（比永冻领域的冰笼更大更粗），脚下一片冰面。**冰在两边，身体中间留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #F4FBFF, #DCF0FF), an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a deep blue ramp for shadows in the ice (#0A2A5A, #143C7A, #2A5CA8), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8).
Effect: A GLACIAL PRISON, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 14 squares across; 2 a frozen patch on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 26 wide and big pale blue ice crystals bursting up on both sides 20 tall; 3 the crystals 36 tall, thick and angular, deep blue inside, white edges; 4 the prison 42 tall with cyan light along the cracks; 5 the prison held, a few glints (the last frame). The body area in the middle left EMPTY. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 5 equal 28:44 cells, image size 2240x704 (each cell 448x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `sejuani_fx_r_storm.png`：极冰寒狱：冰风暴，6 帧循环

套索落下的地方（参考 r_groundfreeze、flurrys、clouds、sejuani_mist、temp_r_tempsnow_chunks）：地上冻出一大片**冰面**，上面**风雪在转圈**——白色雪粉和冰碴沿着圈旋转，边上几块冰晶竖起来。要持续 2 秒，画成循环。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp from white to deep blue (#FFFFFF, #E4F8FF, #A8E4FF, #5CC0F0, #2A88D0, #14509A), a snow ramp (#FFFFFF, #EEF4FA, #CAD8E6, #9AAEC4, #6A80A0), a glowing cyan ramp (#E8FFFF, #8AF4FF, #2ED0F0, #1488B8).
Effect: AN ICE STORM ON THE GROUND, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), a frozen pale blue patch 50 squares wide and 16 tall with cyan cracks, white snow powder and small ice chips swirling round it in a ring 62 wide and 28 tall (in frame k the left and right halves mirror each other, the specks a step further round each frame), a few short ice crystals standing at the rim at mirrored places. everything is FROZEN: crisp angular ice crystals and shards with white glints, pale blue frost, cyan ice light, white snow powder; flat shades, crisp shapes; no fire, no electricity, no smoke.
Layout: one horizontal row of 6 equal 64:30 cells, image size 6144x480 (each cell 1024x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `sejuani_fx_a_hit` | view_effects `league_sejuani_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `sejuani_fx_q_dash` | view_effects `league_sejuani_q_dash`（起冲的地方，不跟随，z -1；左右对称） | 40 × 12 |
| `sejuani_fx_q_hit` | view_effects `league_sejuani_q_hit`（跟随目标，z 2；左右对称） | 20 × 22 |
| `sejuani_fx_f_mark` | view_effects `league_sejuani_f_mark`（跟随目标，z 3；左右对称） | 10 × 10 |
| `sejuani_fx_w_sweep` | view_effects `league_sejuani_w_sweep`（大表，在她脚下，跟随，z -1；左右对称） | 60 × 24 |
| `sejuani_fx_w_line` | view_projectiles `league_sejuani_w_line`（直线弹道，很快，z 2；上下对称） | 40 × 10 |
| `sejuani_fx_w_hit` | view_effects `league_sejuani_w_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `sejuani_fx_e_freeze` | view_effects `league_sejuani_e_freeze`（跟随目标，z 2；左右对称；约 1 秒） | 24 × 40 |
| `sejuani_fx_sh_hit` | view_effects `league_sejuani_sh_hit`（跟随目标，z 2；左右对称） | 28 × 32 |
| `sejuani_fx_fa_armour` | view_buffs `league_sejuani_fa`（tag `fa_armour`，跟随，z 3；左右对称） | 46 × 40 |
| `sejuani_fx_frost` | view_buffs `league_sejuani_frost`（附加包的霜冻层，跟随，头上，z 3；左右对称） | 7 × 7 |
| `sejuani_fx_slow` | view_buffs `league_sejuani_w_slow` / `league_sejuani_r_slow`（tag `slow`，跟随，脚下，z -1；左右对称） | 18 × 7 |
| `sejuani_fx_r_bola` | view_projectiles `league_sejuani_r_bola`（直线弹道，z 2；圆形，两个方向都对称） | 14 × 14 |
| `sejuani_fx_r_hit` | view_effects `league_sejuani_r_hit`（跟随目标，z 2；左右对称） | 28 × 44 |
| `sejuani_fx_r_storm` | view_effects `league_sejuani_r_storm`（大表，落点的地上，不跟随，z -1；左右对称；约 2 秒） | 64 × 30 |

- 两张表：`asset/league/effects/league_sejuani_fx`（小的）和 `league_sejuani_big`（w_sweep、r_storm），tag = 名字（build_sejuani.py 的 views；w_slow 和 r_slow 用 `slow`，fa 用 `fa_armour`，附加包的 frost 用 `frost`）。
- 弹道（w_line）断言上下对称，r_bola 两个方向都对称；其余断言左右对称。r_storm 循环 r_storm（120 tick），fa_armour / slow / frost 循环；e_freeze 的最后一帧停到 e_stun，r_hit 的最后一帧停到 r_stun。
- 用 `pixel_1x/` 切格（import_belveth_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
