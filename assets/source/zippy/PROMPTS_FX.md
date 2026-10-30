# 呲呲：给 Codex 的特效提示词（第 3 步）

> **这一份是 9 张特效图 + 3 个技能图标。** 造型已定（`design/zippy_design.png`：3/4 朝右、两条腿站得笔直的小迅猛龙：圆圆的橙褐色脑袋、头顶玫红尖刺、脸周围黑色尖片、半闭的大紫眼；喉咙到肚子一块紫色围兜；脖子两侧垂着玫红长羽毛；背上洋红马鞍（金边、金环）；橙褐色的腿、紫色脚踝绑带、黑色大爪；尾巴上一排粉色尖鳍）。呲呲在游戏里是**高清**的（每个游戏格子里约 2.2×2.2 个细像素），38 格高、24 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/zippy_size.png`：呲呲缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里呲呲自己的特效贴图（翻滚、冲击环、打中的闪光、护盾泡泡）和克烈的（斯嘎尔的冲锋尘土、护盾）（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **呲呲是机灵的冒险家小龙，特效都是它的味道**：玫红色的羽毛丝和小羽毛、金色的闪光和四角小星星、褐色的尘土团，只有护盾用天蓝色的泡泡光；不要火焰、不要闪电、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或奶白色的芯，暗底上一眼能看见。**光、冲击环、尘土没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `zippy_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `zippy_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/zippy_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/zippy_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「利爪踢」 | 抬腿往前一蹬 | `a_hit` |
| 被动「冒险家之魂」 | 身边每有一个友方英雄，护甲和魔抗多一点 | `p_guild` |
| 技能 1 =「后空翻踢」 | 后空翻，两只脚往上踢中敌人，把它踢飞一下 | `q_hit` |
| 技能 2 =「翻滚冲锋」 | 缩成羽毛球滚向敌人，路上撞到的受伤，身边友军加速 | `e` · `e_hit` · `e_speed` |
| 大招 =「翻滚突袭」 | 套护盾，跃起缩成球砸向生命百分比最高的敌人：伤害、晕眩、小击退 | `r` · `r_hit` · `r_shield` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击环、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 玫红（它的羽毛）：`#FFC2E4`、`#FF6FB8`、`#E8288A`、`#A8135F`、`#5E0A36`；
  - 金（马鞍的金边、星星）：`#FFF4C2`、`#FFD24A`、`#E39A1A`、`#9A5A0E`；
  - 天蓝（护盾泡泡）：`#F2FCFF`、`#AEEBFF`、`#5CC6F0`、`#2A86C2`；
  - 尘土：`#F0E2C8`、`#C9AE86`、`#94775A`、`#5E4A38`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（9 张）

9 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `zippy_fx_a_hit.png`：普攻「利爪踢」：爪子踢中，4 帧

利爪踢中：一下金色的闪光，三道交叉的玫红爪痕，几根玫红小羽毛和金色小星星往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a feather-pink ramp (#FFC2E4, #FF6FB8, #E8288A, #A8135F, #5E0A36), a gold ramp (#FFF4C2, #FFD24A, #E39A1A, #9A5A0E).
Effect: A CLAW KICK HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a cream-gold flash 4 squares across; 2 three short thick hot-pink claw marks crossing in a fan, 12 squares across, pale pink along their middles; 3 the marks breaking into small pink feather tufts and gold sparkles flying out to both sides (mirrored); 4 a few drifting tufts and a puff of dust. everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `zippy_fx_q_hit.png`：技能 1「后空翻踢」：往上踢中，5 帧

后空翻踢中：从下往上**一道玫红色的大弧线**（像脚踢过的轨迹，左右对称的两道弧向上合拢），弧顶一下金光爆开，被踢飞的人周围几颗金色四角星往上飞、羽毛往两边飘。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a feather-pink ramp (#FFC2E4, #FF6FB8, #E8288A, #A8135F, #5E0A36), a gold ramp (#FFF4C2, #FFD24A, #E39A1A, #9A5A0E).
Effect: AN UPWARD KICK BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold flash low in the cell; 2 two hot-pink crescent ARCS sweeping UP from the bottom on both sides (mirrored), meeting at the top, 18 squares wide and 20 tall, pale pink on their leading edges; 3 a bright cream-gold burst at the top where they meet, 10 squares across, little rays; 4 three or four gold four-point stars shooting UPWARD from it and pink feather tufts drifting out to both sides; 5 the stars fading at the top, a last feather. everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 5 equal 20:24 cells, image size 1600x384 (each cell 320x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `zippy_fx_e.png`：技能 2「翻滚冲锋」：起滚扬尘，4 帧

它缩成球滚出去的那一下：地上**一团褐色尘土往两边扬开**，几根玫红小羽毛被带起来。**只在地面上**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp (#F0E2C8, #C9AE86, #94775A, #5E4A38), a feather-pink ramp (#FFC2E4, #FF6FB8, #E8288A, #A8135F, #5E0A36).
Effect: A DUST KICK-OFF, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND only (the bottom of the cell): 1 a small dust puff in the middle, 8 squares wide; 2 brown dust billowing out low to both sides (mirrored), 26 squares wide, 6 tall, pale tops; 3 the puffs rolling outward and thinning, two small pink feather tufts tossed up; 4 the last dust fading. everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 30:10 cells, image size 1920x160 (each cell 480x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `zippy_fx_e_hit.png`：技能 2「翻滚冲锋」：撞到，4 帧

被羽毛球撞到：一圈玫红色的冲击小环一下撑开，几根羽毛和金色小星星往两边弹开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a feather-pink ramp (#FFC2E4, #FF6FB8, #E8288A, #A8135F, #5E0A36), a gold ramp (#FFF4C2, #FFD24A, #E39A1A, #9A5A0E).
Effect: A BUMP HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round a unit standing in the middle (not drawn): 1 a pale-pink flash 5 squares across; 2 a hot-pink impact ring (a circle 14 squares across, 2 squares thick) bursting open; 3 the ring breaking into pink feather tufts and gold sparkles bouncing out to both sides (mirrored); 4 a few fading sparkles. everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `zippy_fx_r.png`：大招「翻滚突袭」：起跳，4 帧

它蹬地高高跃起的一下：脚下地面**一圈尘土环**往外推开（从斜上方看的椭圆，宽是高的 3 倍），几道金色的小光线往上射。**只在地面上**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp (#F0E2C8, #C9AE86, #94775A, #5E4A38), a gold ramp (#FFF4C2, #FFD24A, #E39A1A, #9A5A0E).
Effect: A SPRING-OFF RING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND only (the bottom of the cell): 1 a gold glint in the middle; 2 a ring of brown dust pushed outward (an ellipse 30 squares wide, 9 tall), pale on its top edge, three short gold light streaks shooting straight UP from the middle; 3 the dust ring wider and thinner, the streaks gone; 4 the last dust fading. everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 4 equal 34:12 cells, image size 2176x192 (each cell 544x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `zippy_fx_r_hit.png`：大招「翻滚突袭」：砸中，6 帧

羽毛球从天上砸下来：一下奶黄的大闪光，地上**一圈玫红 + 金色的冲击环**猛地撑开（从斜上方看的椭圆），尘土和羽毛往两边炸开，最后被砸晕的人头顶上方转着**三颗金色的小星星**。**人站的地方留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a feather-pink ramp (#FFC2E4, #FF6FB8, #E8288A, #A8135F, #5E0A36), a gold ramp (#FFF4C2, #FFD24A, #E39A1A, #9A5A0E), a dust ramp (#F0E2C8, #C9AE86, #94775A, #5E4A38).
Effect: A CRASH LANDING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round a unit standing in the middle (not drawn, 16 squares wide, 30 tall): 1 a big cream-gold flash at its feet, 14 squares across, short rays; 2 a hot-pink and gold SHOCK RING bursting open on the ground (an ellipse 50 squares wide, 14 tall, 2 squares thick), brown dust thrown up low to both sides (mirrored); 3 the ring at the cell's edge, pink feather tufts flying out and up on both sides; 4 the dust rolling out, the ring thinning; 5 three small gold four-point STARS appearing in a row above where its head is (the top of the cell), the dust settling; 6 the stars, the last dust. The middle of the cell (the unit's body) stays EMPTY. everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:40 cells, image size 5376x640 (each cell 896x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `zippy_fx_p_guild.png`：被动「冒险家之魂」：护甲光，6 帧循环

身边有队友时它的被动：脚下一圈**淡淡的金色小光环**（从斜上方看的椭圆），上面几颗小金星一闪一闪。很淡，不抢眼。**只在地面上**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFF4C2, #FFD24A, #E39A1A, #9A5A0E).
Effect: A FAINT GUILD RING, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND round its feet only: a thin gold ring (an ellipse 26 squares wide, 6 tall, 1 square thick, its back half fainter), two or three tiny gold four-point stars twinkling on it in turn; frames 1-6 the twinkles moving round and the ring breathing a little brighter and dimmer (every frame left-right symmetric). Subtle: mostly mid and dark gold, only the twinkles bright. everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 30:8 cells, image size 2880x128 (each cell 480x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `zippy_fx_e_speed.png`：技能 2「翻滚冲锋」：加速，6 帧循环

被加速的友军：脚边**两侧几道玫红色的风线**往外飘（像跑起来带的风），一两根小羽毛跟着飘。**只在脚边两侧**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a feather-pink ramp (#FFC2E4, #FF6FB8, #E8288A, #A8135F, #5E0A36).
Effect: SPEED WISPS, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): low beside a unit's feet (the unit not drawn, the middle 10 squares of the cell empty): on EACH side (mirrored) two or three short horizontal hot-pink wind lines 5-8 squares long, pale pink at their inner ends, streaming outward, one small pink feather tuft drifting with them; frames 1-6 the lines sliding outward and new ones appearing near the feet (every frame left-right symmetric). everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 30:14 cells, image size 2880x224 (each cell 480x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `zippy_fx_r_shield.png`：大招「翻滚突袭」：护盾，6 帧循环

它的护盾：一个**天蓝色的泡泡护盾**罩着它（竖着的椭圆，只画边，2 格厚，亮的一边奶白），边上几点玫红和金色的光点转着；**泡泡里面它的身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a sky-blue ramp (#F2FCFF, #AEEBFF, #5CC6F0, #2A86C2), a feather-pink ramp (#FFC2E4, #FF6FB8, #E8288A, #A8135F, #5E0A36), a gold ramp (#FFF4C2, #FFD24A, #E39A1A, #9A5A0E).
Effect: A BUBBLE SHIELD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the raptor stands in the middle, not drawn: 24 squares wide and 38 tall, upright on two legs, its head at the upper right: a sky-blue BUBBLE (an upright ellipse 40 squares wide and 46 tall, only its 2-square rim drawn, pale sky-white on the upper left of the rim, deeper blue below), a faint sky shimmer band across its top; small pink and gold glints running round the rim; frames 1-6 the glints moving round and the rim breathing (every frame left-right symmetric). INSIDE the bubble stays EMPTY (its body). everything is a nimble ADVENTURER RAPTOR's power: hot-pink feather wisps and feather tufts, gold sparkles and four-point stars, soft brown dust puffs, a sky-blue shimmer only for its shield; flat shades, crisp blocky shapes; no fire, no lightning, no smooth neon beams.
Layout: one horizontal row of 6 equal 44:50 cells, image size 4224x800 (each cell 704x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `zippy_icon_skill.png`：技能 1「后空翻踢」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little gold corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a little pink-feathered orange raptor upside down in a backflip, both clawed feet kicking up, a hot-pink crescent arc following the kick, gold stars bursting at its tip. No text, no letters.
```

### 图标 2. `zippy_icon_skill2.png`：技能 2「翻滚冲锋」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little gold corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a round ball wrapped in hot-pink feathers rolling to the right, a gold saddle edge showing, brown dust and pink speed lines trailing behind it. No text, no letters.
```

### 图标 3. `zippy_icon_ult.png`：大招「翻滚突袭」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark plum frame with little gold corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a pink feather ball diving down from the upper left onto the ground, a hot-pink and gold shock ring bursting under it, a sky-blue shield glint round the ball, three gold stars. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `zippy_fx_a_hit` | view_effects `tft_zippy_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `zippy_fx_q_hit` | view_effects `tft_zippy_q_hit`（跟随目标，z 3；左右对称） | 20 × 24 |
| `zippy_fx_e` | view_effects `tft_zippy_e`（放在它起滚的地面上，不跟随，z 1；左右对称） | 30 × 10 |
| `zippy_fx_e_hit` | view_effects `tft_zippy_e_hit`（跟随被撞到的人，z 3；左右对称） | 16 × 16 |
| `zippy_fx_r` | view_effects `tft_zippy_r`（放在它起跳的地面上，不跟随，z 1；左右对称） | 34 × 12 |
| `zippy_fx_r_hit` | view_effects `tft_zippy_r_hit`（大表，跟随被砸中的人，z 4；左右对称） | 56 × 40 |
| `zippy_fx_p_guild` | view_buffs `tft_zippy_p_guild`（跟随它，脚下地面，z 3；左右对称） | 30 × 8 |
| `zippy_fx_e_speed` | view_buffs `tft_zippy_e_speed`（跟随加速的友军，脚下，z 3；左右对称） | 30 × 14 |
| `zippy_fx_r_shield` | view_buffs `tft_zippy_r_shield`（大表，跟随它，z 3；左右对称） | 44 × 50 |
| `zippy_icon_skill` | skill_icons[0] `asset/tft/icons/tft_zippy_skill` | 64 × 64 |
| `zippy_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_zippy_skill2` | 64 × 64 |
| `zippy_icon_ult` | skill_icons[2] `asset/tft/icons/tft_zippy_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_zippy_fx`（小的）和 `tft_zippy_big`（r_hit、r_shield），tag = 名字。
- 全部断言左右对称。
- e、r 放在它起滚 / 起跳的地面上（不跟随，z 1）；p_guild 是它脚下的 caster buff，r_shield 是它身上的 caster buff（z 3）；e_speed 是被加速的友军脚边的 buff（z 3）；a_hit、q_hit、e_hit、r_hit 打在目标身上（r_hit 是 tft.dll 落地时放的）。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
