# 戏命师 烬：给 Codex 的特效提示词（第 3 步）

> **这一份是 27 张特效图。** 造型和动作已定（`design/jhin_design.png`，8 倍，41 格）。
> - 大小对照 `design/jhin_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，右边是原版枪手。烬 29×41 格（兜帽顶到鞋底 41 格）。每条写的大小都是游戏像素（格）。
> - `design/jhin_shots.png`：开枪、扔手雷那几帧的定稿动作（4 倍），青色十字是枪口火焰、出手闪光的起点（导入时 Claude 把特效放到这里）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里烬自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（普攻和第四枪、Q 手雷、W、E 莲花、R、减速），只在本地用，不要提交。颜色按下面写的色阶：**子弹、手雷爆炸、莲花火焰用金色；第四枪、大招、花瓣、减速用玫红；W 的光晕和定身用紫色；低语的枪口火和手雷的小灯用青色**，和英雄联盟一样。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **花瓣要像花瓣**：烬的特效里到处是玫瑰花瓣和莲花——小小的水滴形（2×3 格左右），玫红或金色，亮边，不是圆点。
> - 特效照下面第 1–27 条和「所有特效图的规则」画，每张一个 PNG，文件名 `jhin_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`jhin_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「低语」 | 每 4 发一轮，第四发必定暴击（加最大生命值伤害），然后边走边装弹 2.2 秒 | `jhin_fx_a_bolt` · `jhin_fx_a_cast` · `jhin_fx_a_muzzle` · `jhin_fx_a_hit` · `jhin_fx_a4_bolt` · `jhin_fx_a4_muzzle` · `jhin_fx_a4_hit` · `jhin_fx_a_reload` |
| 技能 1 = Q「曼舞手雷」 | 扔一颗手雷，打中后在附近的敌人之间弹跳，最多打 4 个，每击杀一个伤害提高 | `jhin_fx_q_nade` · `jhin_fx_q_throw` · `jhin_fx_q_boom` · `jhin_fx_q_drop` |
| 技能 2 = W「致命华彩」+ E「万众倾倒」 | E 有充能时先在敌方英雄脚下扔一朵莲花（踩到就开花减速，2 秒后爆炸；被烬打死的英雄身上也会开花）；然后手杖枪射出一道很远的子弹，打到第一个英雄，被队友打过的英雄会被定身 | `jhin_fx_w_shot` · `jhin_fx_w_muzzle` · `jhin_fx_w_hit` · `jhin_fx_w_root` · `jhin_fx_e_seed` · `jhin_fx_e_land` · `jhin_fx_e_bloom` · `jhin_fx_e_boom` · `jhin_fx_e_hit` · `jhin_fx_slowed`（第 1 行） |
| 大招 = R「完美谢幕」 | 跪地架起大炮，向远处的英雄连开 4 炮（减速，每打中一发后面的更痛，第四发必定暴击） | `jhin_fx_r_deploy` · `jhin_fx_r_muzzle` · `jhin_fx_r_bullet` · `jhin_fx_r_hit` · `jhin_fx_r_crit` · `jhin_fx_slowed`（第 2 行） |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火焰、花瓣、火星没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。只有两个物体——手雷罐（`q_nade`、`q_drop`）和莲花（`e_seed`、`e_land`）——像角色一样有 1 格深色描边。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的第四档，第五档（最深）只给很少的点缀。
- 颜色（按每条写的用）：
  - 金色（子弹、爆炸、莲花、火焰）：`#FFFFFF`、`#FFF3C4`、`#FFD45E`、`#F0A030`、`#A85E14`；
  - 玫红（第四枪、大招、花瓣、减速）：`#FFFFFF`、`#FFD6E2`、`#FF7FA6`、`#E0306A`、`#8A1240`；
  - 紫色（W 的光晕、定身）：`#FFFFFF`、`#EEDCFF`、`#C49CFF`、`#8E5BEA`、`#4E2A9E`；
  - 青色（低语的枪口火、手雷的小灯）：`#FFFFFF`、`#D2FFF6`、`#7EF2D8`、`#22B28A`、`#126858`；
  - 铁灰（手雷罐）：`#E6ECF2`、`#A8B4C4`、`#6A7890`、`#3A4458`、`#1E2230`；
  - 烟（手雷、莲花的烟）：`#F4F0E8`、`#D2CABC`、`#A69C8C`、`#746A5C`；
- **飞行类特效朝右画，而且上下对称**（`a_bolt`、`a4_bolt`、`w_shot`、`r_bullet`）：游戏会把它转到飞行方向，朝左飞时整张会上下翻转，所以里面不要有分上下的东西。翻滚的手雷和莲花（`q_nade`、`e_seed`）怎么转都行。
- **枪口火焰朝右画，枪口在格子左边的中点**（`a_muzzle`、`a4_muzzle`、`w_muzzle`、`r_muzzle`）：游戏把它画在烬身上，他朝左时整张左右镜像。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（减速）左右对称，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（27 张）

27 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `jhin_fx_a_bolt.png`：普攻：低语射出的子弹（飞行中循环），4 帧

烬的普攻子弹：一颗白金色的小子弹朝右飞，后面拖一小段金色的光尾（参考 BA_Bullet、BA_mis_add、BA_bullet_glow）。上下对称（朝左飞时会上下翻转）。约 10 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14).
Effect: a small FLYING BULLET moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white-gold bullet head 3 squares tall at the front (right), a thin gold tracer tail 6-7 squares long behind it, getting fainter to the left, flickering a little each frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the bullet on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `jhin_fx_a4_bolt.png`：强化第四枪：必定暴击的第四发子弹（飞行中循环），4 帧

第四发子弹：比普通子弹更大更亮的白金色子弹，后面拖着一圈一圈玫红色的螺旋光环（参考 BA_4th_shot_swirl、BA_Ring_cas、BA_SmokeTrail）。上下对称。约 18 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a big FLYING BULLET moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white-gold bullet head 4 squares tall at the front, behind it a gold core streak 12 squares long wrapped in 3 thin rose-crimson spiral rings (rings seen from the side, like tall narrow ellipses), the rings drifting backward and fading each frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the bullet on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `jhin_fx_a_cast.png`：普攻抬枪：低语上闪一下（施法者身上），4 帧

普攻抬枪的一瞬间，枪上闪一个小小的白金色光圈，带几颗小火星（参考 BA_cas_ring、BA_ready_Sparks）。只画闪光，不画人和枪。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14).
Effect: a SMALL READY GLINT, 4 frames: 1 a white point; 2 a thin gold ring 6 squares across round it, 4 tiny sparkles; 3 the ring wider and fainter; 4 two fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `jhin_fx_a_muzzle.png`：普攻枪口火焰，4 帧

低语开枪的枪口火焰：白色和淡青白色的火舌朝右喷出（参考 BA_muzzle_flash）。朝右画：枪口在格子左边的中点，火从那里往右喷。约 12 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal ramp (#FFFFFF, #D2FFF6, #7EF2D8, #22B28A, #126858) and a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14).
Effect: a MUZZLE FLASH pointing RIGHT, 4 frames: 1 a white star flash at the LEFT MIDDLE of the cell (the muzzle); 2 a burst of white and pale-teal flame tongues fanning out to the right, 10 squares long, a gold spark in it; 3 the flames thinner and broken, a small puff of pale smoke; 4 a few fading wisps.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the muzzle point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `jhin_fx_a_hit.png`：普攻打中，4 帧

普攻子弹打中：一个白金色的小闪光，几道细细的光线射开（参考 BA_hit_glow、BA_hit_ray）。约 10 格，不要太大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14).
Effect: a SMALL BULLET HIT, 4 frames: 1 a white flash at the center; 2 a four-pointed white-gold star with 4 thin gold rays; 3 the star smaller, the rays longer and thinner; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `jhin_fx_a4_muzzle.png`：第四枪的枪口：大火焰加玫红光环（施法者身上），5 帧

第四发的枪口：比普攻更大的白金色火焰朝右喷，火焰外面绕着两圈玫红色的螺旋光环（参考 BA_muzzle_flash、BA_4th_shot_swirl、BA_Ring_cas）。枪口在格子左边的中点。约 20 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a BIG MUZZLE FLASH pointing RIGHT, 5 frames: 1 a white star flash at the LEFT MIDDLE of the cell (the muzzle); 2 a big burst of white-gold flame tongues fanning out to the right, 14 squares long; 3 two rose-crimson rings (tall narrow ellipses) spin out along the flame; 4 the flames break up, the rings wider and fainter; 5 a few fading rose sparks.
Layout: one horizontal row of 5 equal 3:2 cells, image size 1920x256 (each cell 384x256); the muzzle point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `jhin_fx_a4_hit.png`：第四枪打中：暴击，5 帧

第四发打中（必定暴击）：一个白金色的爆闪，外面一圈玫红色的旋涡炸开，几片玫瑰花瓣飞出去（参考 BA_hit_glow、BA_4th_shot_swirl、R_Rose_petals）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a CRITICAL HIT, 5 frames: 1 a white flash; 2 a bright white-gold starburst with a rose-crimson swirl ring round it; 3 the burst at full size, 4 rose petals (small teardrop shapes, 2x3 squares) flying outward; 4 the ring breaks, the petals fly further; 5 a few petals and sparks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `jhin_fx_a_reload.png`：第四枪后装弹（头顶 4 颗子弹依次装上），8 帧

开完第四枪以后装弹 2.2 秒：烬的头顶上横排 4 颗金色的子弹，一颗一颗亮起来（装上），最后 4 颗一起闪一下（参考 BA_white_RGB、BA_ready_Sparks、英雄联盟烬的装弹）。只画子弹，不画人。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14).
Effect: a RELOAD CUE, 8 frames: four small bullet shapes (each 2 squares wide and 4 tall, pointing up: a white-gold tip on a gold case) in a row, 2 squares apart, in the middle of the cell; 1 all four dim (only their darkest gold outlines); 2 the first lights up bright with a sparkle; 3 the first lit; 4 the second lights up with a sparkle; 5 the third lights up; 6 the fourth lights up; 7 all four flash white together; 8 all four lit, fading a little.
Layout: one horizontal row of 8 equal 2:1 cells, image size 4096x256 (each cell 512x256); the row of bullets centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `jhin_fx_q_nade.png`：Q 曼舞手雷：飞行中翻滚的手雷，4 帧

曼舞手雷：一个小小的金属手雷罐在空中翻滚（参考 Q_Canister、Q_Canister_blur：铁灰色的罐身、两道金色的箍、中间一圈发光的青色小灯），后面带一点金色火星。4 帧转一圈。约 8×8 格。手雷是物体，可以有 1 格深色描边（光和火星没有）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a metal ramp (#E6ECF2, #A8B4C4, #6A7890, #3A4458, #1E2230), a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a teal ramp (#FFFFFF, #D2FFF6, #7EF2D8, #22B28A, #126858).
Effect: a small TUMBLING GRENADE, 4 frames, a seamless loop: a gunmetal canister 6 squares long and 4 wide with two gold bands and a ring of small glowing teal lights round its middle, turning a quarter turn each frame, a faint trail of 2-3 gold sparks behind it. The object itself (not its glow) has a 1-square dark outline like a game sprite.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the grenade centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `jhin_fx_q_throw.png`：Q 出手：金手上的白星闪光（施法者身上），4 帧

扔手雷的一瞬间，金色的拳头前一个白色的四角星闪光（参考 Q_flash_cas、Q_ring_cas）。只画闪光。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14).
Effect: a SMALL THROW FLASH, 4 frames: 1 a white point; 2 a four-pointed white star with a gold glow; 3 the star wider and thinner, a thin gold ring round it; 4 fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `jhin_fx_q_boom.png`：Q 手雷炸开，5 帧

手雷打中炸开：白金色的爆炸，一圈火星，几团淡灰色的烟往上冒（参考 Q_flash_cas、Q_ring_cas、E_smoke）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a smoke ramp (#F4F0E8, #D2CABC, #A69C8C, #746A5C).
Effect: a GRENADE BLAST, 5 frames: 1 a white flash; 2 a round white-gold burst with a gold ring of sparks; 3 the burst at full size, sparks flying out, two puffs of pale smoke rising; 4 the burst fades, the smoke puffs bigger and higher; 5 thin smoke and a few sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `jhin_fx_q_drop.png`：Q 手雷弹到下一个目标：从上方落下，4 帧

手雷打中后弹到旁边的下一个敌人：同一个手雷罐从格子上方翻滚着落下来，落到格子中间偏下（导入时那里对着下一个目标），后面拖一道金色的弧线（参考 Q_Canister）。约 8 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a metal ramp (#E6ECF2, #A8B4C4, #6A7890, #3A4458, #1E2230), a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a teal ramp (#FFFFFF, #D2FFF6, #7EF2D8, #22B28A, #126858).
Effect: a GRENADE DROPPING, 4 frames: the same small gunmetal canister as the flying grenade (6x4 squares, gold bands, teal lights) tumbling down from the top of the cell: 1 at the top; 2 a third of the way down, turned; 3 two thirds down, turned again, a short gold arc trail above it; 4 at the landing point (two thirds of the way down the cell), a tiny white spark under it. The object itself (not its glow) has a 1-square dark outline like a game sprite.
Layout: one horizontal row of 4 equal 1:3 cells, image size 1024x768 (each cell 256x768); the landing point two thirds down every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `jhin_fx_w_shot.png`：W 致命华彩：射出去的长子弹（飞行中循环），4 帧

致命华彩：一道很快很长的子弹光束，白金色的芯，外面一层紫色的光晕，沿线闪着小金星（参考 W_swirl_beam、W_beam_glow、W_indicator）。上下对称。约 32 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a violet ramp (#FFFFFF, #EEDCFF, #C49CFF, #8E5BEA, #4E2A9E).
Effect: a long FAST BULLET STREAK moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white bullet head at the front (right), a straight streak 28 squares long behind it: a white-gold core line 1-2 squares thick inside a violet glow 1 square thick on each side, getting thinner and fainter toward the back (left), small gold sparks flickering along it.
Layout: one horizontal row of 4 equal 6:1 cells, image size 3072x128 (each cell 768x128); the streak on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `jhin_fx_w_muzzle.png`：W 枪口火焰（施法者身上），5 帧

致命华彩开枪：手杖枪口喷出白色的星形闪光和橙粉色的火舌，外面一圈淡紫色的光（参考 W_muzzle_flash、W_flash_cas、W_cas_ring）。枪口在格子左边的中点。约 22 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14), a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240) and a violet ramp (#FFFFFF, #EEDCFF, #C49CFF, #8E5BEA, #4E2A9E).
Effect: a RIFLE MUZZLE FLASH pointing RIGHT, 5 frames: 1 a white four-pointed star at the LEFT MIDDLE of the cell (the muzzle), long thin rays; 2 a burst of white, light-gold and rose flame tongues fanning out to the right, 14 squares long, a pale violet ring round the muzzle; 3 the flames longer and thinner, the ring wider; 4 the flames break into sparks; 5 a few fading sparks.
Layout: one horizontal row of 5 equal 3:2 cells, image size 1920x256 (each cell 384x256); the muzzle point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `jhin_fx_w_hit.png`：W 打中，5 帧

致命华彩打中：一个尖锐的白色闪光，深红色的碎片往后飞溅（参考 W_flash_cas、W_hit_bits_tar、W_bigglow）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14), a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240) and a violet ramp (#FFFFFF, #EEDCFF, #C49CFF, #8E5BEA, #4E2A9E).
Effect: a PIERCING HIT, 5 frames: 1 a white flash; 2 a sharp white four-pointed star with a violet glow; 3 the star with long thin horizontal rays, 5-6 small crimson shards flying out; 4 the rays fade, the shards further; 5 a few shards.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `jhin_fx_w_root.png`：W 定身（目标脚下，持续约 1.7 秒），8 帧

被致命华彩定身：目标脚下一圈淡紫色和玫红色的光圈，圈上长出 4 根细细的玫瑰荆棘缠住腿（参考 W_root_decal、R_Rose_petals）。中间是人，不要画人：只画脚下的圈和腿边的荆棘，人的位置留空。第 1–2 帧出现，3–6 帧保持（导入时重复），7–8 帧消散。约 22 格宽、18 格高，圈的中心在格子底部往上 3 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #EEDCFF, #C49CFF, #8E5BEA, #4E2A9E) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a ROOT round a figure's feet (do NOT draw the figure; leave its place empty), 8 frames: 1 a pale violet ring appears on the ground (a flattened ellipse twice as wide as tall); 2 four thin rose-crimson thorny vines shoot up from the ring, curling round where the legs are; 3-6 held: the ring glowing, the vines up to a third of the cell's height with a small rose bud on each, pulsing a little each frame; 7 the vines fade; 8 the ring breaks into rose specks.
Layout: one horizontal row of 8 equal 5:4 cells, image size 2560x256 (each cell 320x256); the ring's center 3 squares (24 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `jhin_fx_e_seed.png`：E 万众倾倒：扔出去的莲花（飞行中），4 帧

W 之前先扔一朵莲花陷阱：一个合拢的金色莲花苞（中间一颗粉色宝石）在空中翻转，后面带两颗金色小火星（参考 E_trap_mis）。约 8×8 格。是物体，可以有 1 格深色描边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a small FLYING LOTUS BUD, 4 frames, a seamless loop: a closed golden lotus bud 6 squares tall (4-5 pointed gold petals with light-gold edges, a small glowing pink gem in the middle), turning a little each frame, two tiny gold sparkles trailing it. The object itself (not its glow) has a 1-square dark outline like a game sprite.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the bud centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `jhin_fx_e_land.png`：E 莲花落地、布好（然后隐身），8 帧

莲花落地：金色的莲花苞落在地上弹一下，花瓣微微张开、粉色宝石亮一下（布好了），然后慢慢变淡隐身（英雄联盟里陷阱布好后敌人看不见）（参考 E_trap_mis、E_activate_circle）。约 14 格宽、10 格高，莲花底部在格子底部往上 2 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a LOTUS TRAP SET ON THE GROUND, 8 frames: 1 the closed golden lotus bud (6 squares tall, pink gem in the middle) lands with a small puff of gold dust; 2 it bounces a square up; 3 it settles, a faint gold ring on the ground round it (a flattened ellipse); 4 its petals open a little, the pink gem glows; 5 a pink pulse ring spreads on the ground; 6 the lotus half transparent (only its outline and the gem); 7 only a faint gold outline; 8 nearly gone, a single pink glint. The object itself (not its glow) has a 1-square dark outline like a game sprite.
Layout: one horizontal row of 8 equal 3:2 cells, image size 3072x256 (each cell 384x256); the lotus's base 2 squares (16 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `jhin_fx_e_bloom.png`：E 莲花绽放（目标脚下，2 秒后爆炸，大图），10 帧

有敌方英雄踩到莲花（或被烬打死的英雄身上）：地上一朵大大的金色莲花绽开，花瓣一层层张开，中间粉红色的光越来越亮，地上的金色光圈慢慢转（这 2 秒里周围的敌人减速），最后一帧花瓣收紧发白，接爆炸（参考 E_trap_mis、E_trap_petal、E_activate_circle、E_indicator_red）。从斜上方看，宽是高的 2 倍。约 36 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a GIANT LOTUS BLOOMING on the ground, seen from above at an angle (a flattened shape TWICE as wide as tall), 10 frames: 1 a small closed bud at the center with a pink glint; 2-3 the petals open in two layers (8 pointed gold petals with light-gold edges, inner petals rose-pink), a thin gold ring on the ground round it; 4-8 the full bloom held: the ring turning a little each frame, the pink heart of the flower pulsing brighter frame by frame, a few gold motes rising (these frames loop); 9 the petals curl inward, glowing white at the tips; 10 a white-hot flash at the heart.
Layout: one horizontal row of 10 equal 2:1 cells, image size 5120x256 (each cell 512x256); the flower centered in every cell, filling it. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `jhin_fx_e_boom.png`：E 莲花爆炸（大图），7 帧

莲花爆炸：一团橙金色的火焰炸开，中间白色的闪光，火焰往上冲，金色的花瓣和灰烬向四周飞散（参考 E_burning_mult、E_centerFlare、E_explosion_swirl、E_Ash_01、E_trap_petal）。地面上的爆炸圈是扁椭圆。约 40 格宽、40 格高，爆炸的中心在格子底部往上 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14), a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240) and a smoke ramp (#F4F0E8, #D2CABC, #A69C8C, #746A5C).
Effect: a FIRE BLOSSOM EXPLOSION, 7 frames: 1 a white flash at the center and a flat bright ring on the ground (an ellipse twice as wide as tall); 2 a ball of orange-gold fire with a white core bursts up from it; 3 the fire at full size, tongues of flame rising, 6-8 gold petals and rose sparks flying outward; 4 the fire breaks into curling flames, petals further out, dark-gold embers; 5 the flames shrink and rise, grey smoke puffs; 6 smoke and falling embers; 7 a few embers and thin smoke.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; the blast's center 12 squares up from the bottom of every cell (a little below the middle), horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `jhin_fx_e_hit.png`：E 爆炸打中（目标身上），4 帧

莲花爆炸打到的每个敌人身上：一小团橙金色的火光和几片花瓣（参考 E_burning_mult、E_spark）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a SMALL FIRE HIT, 4 frames: 1 a white-gold flash; 2 a small orange-gold flame burst with a white core; 3 the flames flicker up, 2 small gold petals flying off; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `jhin_fx_r_deploy.png`：R 完美谢幕：架起大炮（施法者身上），8 帧

开大的一瞬间：烬身边一圈玫红色和金色的光往上升，玫瑰花瓣绕着他飘起来，地上一个淡金色的圈（英雄联盟里是一个穹顶样的光幕，参考 R_Dome_cas、R_Rose_petals、R_Spark）。中间是人，不要画人。约 36 格宽、30 格高，地上的圈中心在格子底部往上 3 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240) and a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14).
Effect: a CURTAIN RISING round a figure (do NOT draw the figure; leave its place empty), 8 frames: 1 a thin gold ring flashes on the ground (an ellipse twice as wide as tall); 2 a curtain of rose-crimson light rises from the ring, lighter at the bottom; 3 the curtain at half the cell's height, 6 rose petals lifting round it; 4 the curtain at full height, gold sparks; 5 the curtain thins, the petals spiral upward; 6 the curtain fades from the bottom; 7 only petals and sparks high up; 8 a few petals.
Layout: one horizontal row of 8 equal 6:5 cells, image size 3072x320 (each cell 384x320); the ring's center 3 squares (24 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `jhin_fx_r_muzzle.png`：R 大炮的枪口火焰（施法者身上），5 帧

完美谢幕开炮：炮口喷出很大的白色闪光和粉橙色的火舌，几片玫瑰花瓣跟着冲出去（参考 R_muzzle_flash、R_Spark、R_Rose_petals）。炮口在格子左边的中点。约 24 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a CANNON MUZZLE FLASH pointing RIGHT, 5 frames: 1 a big white star flash at the LEFT MIDDLE of the cell (the muzzle); 2 a large burst of white, gold and rose-orange flame tongues fanning out to the right, 18 squares long; 3 the flames longer, 3 rose petals shooting out with them; 4 the flames break into sparks and smoke wisps; 5 fading sparks and a petal.
Layout: one horizontal row of 5 equal 3:2 cells, image size 1920x256 (each cell 384x256); the muzzle point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `jhin_fx_r_bullet.png`：R 完美谢幕：大炮的子弹（飞行中循环），4 帧

完美谢幕的子弹：一颗白金色的大弹头，后面拖一道金色和玫红色互相缠绕的长光尾，后面掉几片花瓣（参考 R_mis_big、R_mis_core、R_mis_smoke、R_Rose_petals）。上下对称。约 30 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a big FLYING SHELL moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white-gold shell head 5 squares tall at the front, behind it a 24-square trail of a gold ribbon and a rose-crimson ribbon twisted round each other (crossing every 6 squares), a few rose sparks shed behind, the twist moving backward each frame.
Layout: one horizontal row of 4 equal 4:1 cells, image size 2048x128 (each cell 512x128); the shell on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 25. `jhin_fx_r_hit.png`：R 打中，5 帧

大炮子弹打中：一个红金色的爆闪，几道竖直的粉色光线（参考 R_hit_ray、R_Spark）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a HEAVY HIT, 5 frames: 1 a white flash; 2 a round white-gold burst with a rose rim; 3 the burst at full size, 3-4 thin vertical rose light rays shooting up through it; 4 the burst fades, the rays thin; 5 a few rose sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 26. `jhin_fx_r_crit.png`：R 第四发打中（暴击），6 帧

大招第四发打中（必定暴击）：更大的爆炸，一圈玫红色的旋涡和玫瑰花瓣炸开，中间金色的闪光（参考 R_hit_ray、BA_4th_shot_swirl、R_Rose_petals、Z_Petal_Amber）。约 26 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14) and a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240).
Effect: a GRAND FINALE HIT, 6 frames: 1 a white flash; 2 a big white-gold starburst with a rose-crimson swirl ring; 3 the burst at full size, 8 rose petals and gold sparks flying outward, thin vertical rose rays; 4 the ring wider and breaking, the petals further; 5 the petals drifting and fading; 6 a few petals.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 27. `jhin_fx_slowed.png`：减速（目标脚下，循环），4 帧：E 莲花减速和 R 怯场各一行

两种减速：第 1 行是莲花开花时的减速——几片金色和玫红色的花瓣绕着敌人的脚慢慢转；第 2 行是大招的「怯场」——一圈暗玫红色的光在脚下转，带两三片花瓣（参考 E_passive_Mark、E_passive_Mark_bright、R_Rose_petals）。中间是人，不要画人。左右对称（人朝左朝右都用同一张），4 帧无缝循环。约 20 格宽、8 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, flames, petals or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rose ramp (#FFFFFF, #FFD6E2, #FF7FA6, #E0306A, #8A1240) and a gold ramp (#FFFFFF, #FFF3C4, #FFD45E, #F0A030, #A85E14).
Effect: SLOW MARKS at a figure's feet (do NOT draw the figure; symmetric left and right), 4 frames per row, a seamless loop: ROW 1 four small petals (gold and rose, teardrop shapes 2x3 squares) circling a flattened ellipse on the ground (twice as wide as tall), a quarter of the way each frame, a faint gold ring joining them; ROW 2 a dim rose-crimson ring of light on the ground (a flattened ellipse) turning, two small rose petals riding it, a few rose specks.
Layout: two horizontal rows of 4 equal cells each, each cell 5 wide to 2 tall, image size 2560x512 (each cell 640x256); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `jhin_fx_a_bolt` | view_projectiles `league_jhin_a_bolt`（朝右，游戏转到飞行方向） | 10 × 4 |
| `jhin_fx_a4_bolt` | view_projectiles `league_jhin_a4_bolt`（朝右，游戏转到飞行方向） | 18 × 8 |
| `jhin_fx_a_cast` | view_effects `league_jhin_a_cast`（施法者身上，不跟随（动作中途播放，跟随的话红色方会画反）；Claude 放到普攻第 2 帧低语的位置） | 10 |
| `jhin_fx_a_muzzle` | view_effects `league_jhin_a_muzzle`（施法者身上，不跟随（动作中途播放，跟随的话红色方会画反），朝左时游戏左右镜像；格子左边中点放到普攻第 3 帧的枪口） | 12 × 10 |
| `jhin_fx_a_hit` | view_effects `league_jhin_a_hit`（跟随） | 10 |
| `jhin_fx_a4_muzzle` | view_effects `league_jhin_a4_muzzle`（施法者身上，不跟随（动作中途播放，跟随的话红色方会画反），朝左时镜像；格子左边中点放到第四枪第 4 帧的枪口） | 20 × 14 |
| `jhin_fx_a4_hit` | view_effects `league_jhin_a4_hit`（跟随，画在人物上面） | 18 |
| `jhin_fx_a_reload` | view_effects `league_jhin_a_reload`（施法者身上，跟随，画在头顶上；导入时拉长到装弹的 2.2 秒） | 18 × 8 |
| `jhin_fx_q_nade` | view_projectiles `league_jhin_q_nade`（循环，游戏转到飞行方向） | 8 × 8 |
| `jhin_fx_q_throw` | view_effects `league_jhin_q_throw`（施法者身上，跟随；放到 Q 第 3 帧金拳头的位置） | 10 |
| `jhin_fx_q_boom` | view_effects `league_jhin_q_boom`（跟随，画在人物上面） | 18 |
| `jhin_fx_q_drop` | view_effects `league_jhin_q_drop`（跟随；落到底以后接 `q_boom`） | 8 × 24 |
| `jhin_fx_w_shot` | view_projectiles `league_jhin_w_shot`（朝右，游戏转到飞行方向） | 32 × 5 |
| `jhin_fx_w_muzzle` | view_effects `league_jhin_w_muzzle`（施法者身上，不跟随（动作中途播放，跟随的话红色方会画反），朝左时镜像；格子左边中点放到 W 第 7 帧的枪口） | 22 × 14 |
| `jhin_fx_w_hit` | view_effects `league_jhin_w_hit`（跟随，画在人物上面） | 16 |
| `jhin_fx_w_root` | view_effects `league_jhin_w_root`（跟随；3–6 帧导入时重复到定身结束） | 22 × 18 |
| `jhin_fx_e_seed` | view_projectiles `league_jhin_e_seed`（游戏转到飞行方向） | 8 × 8 |
| `jhin_fx_e_land` | view_effects `league_jhin_e_land`（地面，画在人物下面，不跟随） | 14 × 10 |
| `jhin_fx_e_bloom` | view_effects `league_jhin_e_bloom`（地面，画在人物下面，不跟随，大图；4–8 帧导入时重复到 2 秒） | 36 × 18 |
| `jhin_fx_e_boom` | view_effects `league_jhin_e_boom`（不跟随，画在人物上面，大图） | 40 × 40 |
| `jhin_fx_e_hit` | view_effects `league_jhin_e_hit`（跟随，画在人物上面） | 14 |
| `jhin_fx_r_deploy` | view_effects `league_jhin_r_deploy`（施法者身上，跟随，朝左时镜像） | 36 × 30 |
| `jhin_fx_r_muzzle` | view_effects `league_jhin_r_muzzle`（施法者身上，不跟随（动作中途播放，跟随的话红色方会画反），朝左时镜像；格子左边中点放到 R 开炮帧的炮口） | 24 × 16 |
| `jhin_fx_r_bullet` | view_projectiles `league_jhin_r_bullet`（朝右，游戏转到飞行方向） | 30 × 8 |
| `jhin_fx_r_hit` | view_effects `league_jhin_r_hit`（跟随，画在人物上面） | 18 |
| `jhin_fx_r_crit` | view_effects `league_jhin_r_crit`（跟随，画在人物上面） | 26 |
| `jhin_fx_slowed` | view_buffs `league_jhin_e_slowed`（第 1 行）/ `league_jhin_r_slowed`（第 2 行）（循环，画在脚下） | 20 × 8 |

- 施法者身上的画面（`a_cast`、`a_muzzle`、`a4_muzzle`、`q_throw`、`w_muzzle`、`r_muzzle`、`r_deploy`、`a_reload`）画在站位点上：按 `design/jhin_shots.png` 的十字（定稿动作里量的枪口、金拳头）把格子的起点挪过去；`a_reload` 放在头顶上方（兜帽顶往上 3 格）、帧拉长到装弹的 130 tick。
- 飞行物（`a_bolt`、`a4_bolt`、`w_shot`、`r_bullet`）第一帧前加一个空帧（出生那一 tick 画面朝上，`import_lucian.py` 的 `RAY_SKIP`）；`w_root` 的 3–6 帧重复到定身的 100 tick；`e_bloom` 的 4–8 帧循环到 120 tick 爆炸；`e_land` 照原样播（布好后隐身）。
- 清掉 Codex 给光和花瓣描的最深色边（`import_riven.py` 的 `unrim` 做法，手雷罐和莲花保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
