# 龙血武姬 希瓦娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 26 张特效图。** 造型已定（`design/shyvana_designs.png`：左边人形——3/4 正面朝右、淡紫皮肤、金橙长发、深红龙角冠、青银胸甲、深红长尾；右边龙形——深红巨龙、两只抬起的翅膀、橙黄火焰鬃毛）。她在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），人形 42 格高、27 格宽，龙形 43 格高、71 格长；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/shyvana_size.png`：人形和龙形放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/shyvana_shots.png`：动作帧（4 倍），青色十字是她的站位点；每张写了特效出现在哪里（人形的动作还在画，用待机代替）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里希瓦娜和她的龙自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的火焰是橙色和金色的、芯是白的，边缘变成深红**；**龙的火（龙息、大火球）更深一些，橙红色**；**撕咬（真实伤害）是白金色**；**龙形回血是绿金色**。
> - **特效要亮**：每团火、每道光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **火焰、光、光环、冲击波都没有黑描边**；**灰烟**可以有 1 格暗边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、地上、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（火球、大火球、龙息）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图，往左时是倒过来的）。**两张斩击**（q_slash、d_q_slash）**朝右画**，会画进她的动作帧里，不用对称。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `shyvana_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/shyvana_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/shyvana_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（W「烈火圣盾」在里面） | 爪击；每 12 秒的普攻带出火焰护盾，2.5 秒后爆炸，龙形时炸到英雄回血 | `a_hit` · `w_aegis` · `w_blast` · `w_hit` · `w_heal` |
| 技能 1 = Q「焚焰打击」 | 人形：斩击 → 横扫；龙形：翼击 → 甩尾 → 撕咬（接在之后的普攻上） | `q_slash` · `d_q_slash` · `q_hit` · `q2_wave` · `d_q2_wave` · `q2_hit` · `q3_hit` |
| 技能 2 = E「爆炎吐息」 | 人形掷火球，命中或到终点爆炸并减速；龙形喷大火球，穿透、终点炸开、留下燃烧的地面 | `e_ball` · `e_hit` · `e_blast` · `e_slow` · `de_ball` · `de_hit` · `de_blast` · `de_singe` |
| 大招「魔龙降世」 | 龙怒攒满时化身为龙，飞向敌方英雄，一路喷火使敌人恐惧，落地 | `fury_full` · `tf_dragon` · `r_breath` · `r_hit` · `r_land` · `tf_human` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**火焰、光、光环、冲击波没有黑描边，也不要用最深的颜色给形状描一圈边**（灰烟可以有 1 格暗边）。
- **要亮**：每个火焰、光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 她的火焰（橙金色）：`#FFFFFF`、`#FFF4B0`、`#FFD54A`、`#FF9E22`、`#F2601E`、`#C42E1C`、`#7E1420`；
  - 龙的火（橙红色）：`#FFFFFF`、`#FFE27A`、`#FFAE2E`、`#FF6A1A`、`#E0321C`、`#A0161E`、`#5C0A1A`；
  - 撕咬、护盾光边（白金色）：`#FFFFFF`、`#FFF6C8`、`#FFE07A`、`#F6B83A`、`#C8862A`；
  - 龙形回血（绿金色）：`#F4FFE6`、`#D2F58C`、`#8AD84E`、`#4AA444`、`#2A6E3A`；
  - 灰烟（变回人）：`#B8AAA0`、`#847872`、`#5A4E4C`、`#3A3032`；
- 打中、爆发居中画，不旋转；地面上的圆（火环、爆炸、余烬）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（26 张）

26 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 二段的半径 26000，W 爆炸半径 33000，E 射程 70000、落点半径 15000，龙形 E 射程 90000、终点半径 30000，R 的龙息宽 18000）。

### 1. `shyvana_fx_a_hit.png`：普攻：爪击打中目标，3 帧

龙爪抓中：三道短短的橙红色爪痕交叉一闪，迸出几点火星（参考 claw_slashforward、tar_flash_fire、base_generic_sparks_add）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A CLAW HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 5 squares across with three short orange claw streaks crossing it (an X and a vertical stroke); 2 the streaks fading to red, 4 sparks flying out diagonally; 3 only the fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `shyvana_fx_q_slash.png`：Q 焚焰打击（人形）：前方的火焰斩击，4 帧

她的爪子往前横斩，在身前划出一道弯月形的火焰爪痕（三道平行的火弧，参考 claw_slashforward、fire_claw、shyvana_base_ba_edgeaoe）。**朝右画**（会画进她的动作帧里，不用左右对称），4 帧：起、最亮、散开、余烬。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A FIERY CLAW SLASH, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): three parallel curved flame streaks sweeping in a crescent from the upper left to the lower right in front of her, 22 squares long, white-gold at their leading edge, orange behind, crimson at the tail; 1 the streaks half drawn; 2 full and brightest; 3 breaking into flame tongues; 4 only embers drifting.
Layout: one horizontal row of 4 equal 30:22 cells, image size 1920x352 (each cell 480x352, 16 px a square); the crescent's middle on the cell's middle, its points toward the right; she stands in the middle, not drawn: 27 squares wide and 42 tall at the cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `shyvana_fx_d_q_slash.png`：Q 焚焰打击（龙形）：翼击掀起的火焰气浪，4 帧

龙的翅膀往前一拍，前方卷起一大片带火的气浪（一道宽的弧形火浪往前推，参考 shyvanadragon_base_q_swipe_a、shyvana_q_cloudtextures、shyvana_base_tileflames02）。**朝右画**（会画进龙的动作帧），4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A WING-GUST OF FIRE, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): a wide curved wave of flame and hot wind pushing forward to the right, 34 squares tall at its front, tongues of flame along its front edge, a white-yellow inner rim; 1 forming; 2 full; 3 rolling forward and thinning; 4 only flame wisps.
Layout: one horizontal row of 4 equal 48:34 cells, image size 3072x544 (each cell 768x544, 16 px a square); the wave's front edge 4 squares from the right of the cell; the dragon stands in the middle, not drawn: 71 squares long and 43 tall, low on four legs to the left of the cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `shyvana_fx_q_hit.png`：Q：斩击打中目标，3 帧

斩击打中：一团橙色火焰溅开（参考 shyvana_base_q_impact_tarsplash）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A FIERY SPLASH HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white core 4 squares across with a jagged orange splash 10 squares across; 2 the splash breaking into 8 flame tongues; 3 small flames and embers.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `shyvana_fx_q2_wave.png`：Q 二段（人形）：横扫时脚下一圈火，5 帧

她转身横扫，脚下贴着地面炸开一圈火焰（地上的椭圆火环，往外扩散，参考 shyvana_base_ba_edgeaoe、shyvana_base_ground01、shyvana_base_ring_softglow2）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A RING OF FIRE ON THE GROUND, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at an angle (about 3 times as wide as tall), its middle where the feet are; 1 a thin bright ring 30 squares wide; 2 grown to 50 wide with short flame tongues rising along its far half; 3 full, 58 wide, flames 8 squares tall; 4 the flames sinking; 5 only a faint scorched ring with embers.
Layout: one horizontal row of 5 equal 60:24 cells, image size 4800x384 (each cell 960x384, 16 px a square); the ellipse's middle 6 squares above the cell's bottom; she stands in the middle, not drawn: 27 squares wide and 42 tall in the middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `shyvana_fx_d_q2_wave.png`：Q 二段（龙形）：甩尾扫出的大火弧，5 帧

龙转身甩尾，尾巴扫过的地方贴地掀起一大圈火焰（比人形的大，参考 shyvanadragon_base_emote_linearsplashes_02_gs、shyvana_base_ba_edgeaoe、shyvana_base_ground02）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A BIG SWEEPING FIRE RING ON THE GROUND, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at an angle (about 3 times as wide as tall), its middle where the feet are; 1 a bright ring 50 squares wide; 2 grown to 76 wide with flames rising along it; 3 full, 88 wide, flames 12 squares tall; 4 the flames sinking; 5 scorched ring and embers.
Layout: one horizontal row of 5 equal 90:34 cells, image size 7200x544 (each cell 1440x544, 16 px a square); the ellipse's middle 8 squares above the cell's bottom; the dragon stands in the middle, not drawn: 71 squares long and 43 tall, low on four legs in the middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `shyvana_fx_q2_hit.png`：Q 二段：扫中目标，3 帧

扫中：一团火焰爆开（参考 tar_flash_fire）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A FIRE BURST HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-orange star flash 7 squares across; 2 a round burst of flame 11 squares across; 3 small flames and embers rising.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `shyvana_fx_q3_hit.png`：Q 三段（龙形）：撕咬，4 帧

龙一口咬下（真实伤害）：上下两排白金色的獠牙从两边合拢，咬住时一闪白光（参考 sowflash_spark）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-gold light ramp (#FFFFFF, #FFF6C8, #FFE07A, #F6B83A, #C8862A).
Effect: A DRAGON BITE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two curved rows of 5 white-gold fangs, one above and one below, 10 squares apart; 2 the rows closing to 4 squares apart; 3 snapped shut with a white flash 12 squares across; 4 gold sparks scattering.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `shyvana_fx_w_aegis.png`：W 烈火圣盾：包着她的火焰护盾（循环），6 帧

一圈烈焰包着她：外面一层淡金色的护盾光边，火焰在护盾边上往上窜（参考 shyvana_base_w_shield_mesh2、shyvana_base_w_shieldfresnelring、shyvana_base_vgu_w_ele_flat_energy、shyvana_base_tileflames02）。**中间她的身体位置留空**，**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A FLAME SHIELD AROUND A BODY, 6 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a gold dome outline 40 squares wide and 46 tall (1 square thick, pale gold, broken in places) with orange flames 4-8 squares tall licking up along its lower two thirds on both sides, and a flat ring of fire on the ground; the inside EMPTY where her body is (only the dome's thin rim crosses in front at the bottom); each frame the flames rise and flicker in turn.
Layout: one horizontal row of 6 equal 44:50 cells, image size 4224x800 (each cell 704x800, 16 px a square); the dome's bottom 3 squares above the cell's bottom; she stands in the middle, not drawn: 27 squares wide and 42 tall in the middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `shyvana_fx_w_blast.png`：W 烈火圣盾：护盾爆开，6 帧

护盾时间到，烈焰向四周炸开：先是一圈很亮的火环贴地扩散，再冲起一圈火焰（参考 shyvana_base_ba_edgeaoe、shyvana_base_ring_softglow2、tar_flash_fire）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A FIRE NOVA AROUND A BODY, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash at the feet, a ring 20 squares wide; 2 the ring racing out to 48 wide, flames bursting up around it 16 tall; 3 full, 70 wide, a wall of flame 24 squares tall round the ring's far half, low flames on its near half; 4 the flames curling and fading to red; 5 smoke-orange wisps; 6 a faint scorched ring.
Layout: one horizontal row of 6 equal 72:46 cells, image size 6912x736 (each cell 1152x736, 16 px a square); the ground ellipse's middle 8 squares above the cell's bottom; she stands in the middle, not drawn: 27 squares wide and 42 tall in the middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `shyvana_fx_w_hit.png`：W：爆炸打中目标，3 帧

被爆炸波及：身上一团火（参考 tar_flash_fire）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A SMALL FIRE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an orange flash 6 squares across; 2 three flame tongues rising 9 squares; 3 embers.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `shyvana_fx_w_heal.png`：W（龙形）：爆炸打中英雄时回血，5 帧

龙形时护盾爆炸打中英雄会回血：身上冒起一圈绿金色的光点往上飘（参考 shyvana_base_w_heal_ray、shyvana_base_w_heal_spark）。**中间身体位置留空，左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green-gold heal ramp (#F4FFE6, #D2F58C, #8AD84E, #4AA444, #2A6E3A).
Effect: A HEAL BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): soft green-gold light rising round a body: 1 a ring of 8 bright green-gold motes at the feet; 2 the motes rising as short vertical streaks 6 squares long; 3 at chest height with a small white plus sign over the head; 4 near the top, fading; 5 a few last motes. The middle EMPTY where the body is.
Layout: one horizontal row of 5 equal 26:30 cells, image size 2080x480 (each cell 416x480, 16 px a square); the motes start 2 squares above the cell's bottom; she stands in the middle, not drawn: 27 squares wide and 42 tall in the middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `shyvana_fx_e_ball.png`：E 爆炎吐息（人形）：火球（弹道，循环），4 帧

她掷出的火球：白黄色的芯，橙色的火团，后面拖一截飘动的火焰尾巴（参考 shyvana_base_missilehead01、shyvana_base_e_mis_flametrail、shyvana_base_foundation_missile02）。**朝右飞、尾巴在左边，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A FIREBALL, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round fireball 6 squares across with a white-yellow core 2-3 squares, a tapering flame trail 8 squares long behind it on the left; each frame the flames of the trail shift back a square and the core flickers.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); the ball's middle on the cell's middle row, its front 1 square from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `shyvana_fx_e_hit.png`：E：火球打中目标，3 帧

火球砸中：一团火焰（参考 tar_flash_fire）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A FIREBALL HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-orange flash 6 squares across; 2 a burst of flame 10 squares across; 3 small flames.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `shyvana_fx_e_blast.png`：E：火球在落点炸开，5 帧

火球炸开：地上一圈火，往上冒起火焰（参考 shyvana_base_e_ground_mask、shyvana_base_e_decalglow、tar_flash_fire）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A FIREBALL BURST ON THE GROUND, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at an angle (about 3 times as wide as tall), its middle where the feet are; 1 a white flash 10 squares across; 2 a ring of fire 26 wide with flames bursting up 16 squares; 3 full, 32 wide, flames 22 tall; 4 the flames sinking; 5 a scorched patch with embers.
Layout: one horizontal row of 5 equal 34:30 cells, image size 2720x480 (each cell 544x480, 16 px a square); the ground ellipse's middle 5 squares above the cell's bottom; centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `shyvana_fx_de_ball.png`：E（龙形）：大火球（弹道，循环），4 帧

龙喷出的大火球：比人形的大一倍，深橙红色，拖着一大截火焰（参考 shyvana_base_e_mis_flametrail、shyvana_e_flameoutline、shyvana_base_missilehead01）。**朝右飞、尾巴在左边，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A BIG DRAGON FIREBALL, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a fireball 10 squares across with a white-yellow core 4 squares, a wide flame trail 14 squares long behind it on the left; each frame the trail's flames shift back and the core pulses.
Layout: one horizontal row of 4 equal 26:16 cells, image size 1664x256 (each cell 416x256, 16 px a square); the ball's middle on the cell's middle row, its front 1 square from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `shyvana_fx_de_hit.png`：E（龙形）：大火球穿过打中的目标，3 帧

大火球穿过时身上一团火（参考 tar_flash_fire）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A BIG FIRE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-orange flash 7 squares across; 2 a burst of deep orange flame 12 squares across; 3 flames and embers.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `shyvana_fx_de_blast.png`：E（龙形）：大火球在终点炸开，6 帧

大火球在终点炸开一大片火海（参考 shyvana_base_ground03、shyvana_base_ba_edgeaoe、tar_flash_fire）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A BIG FIRE EXPLOSION ON THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at an angle (about 3 times as wide as tall), its middle where the feet are; 1 a white flash 16 squares across; 2 a ring of fire 44 wide, flames bursting up 26 squares; 3 full, 60 wide, flames 34 tall; 4 the flames curling and reddening; 5 low flames; 6 a scorched patch with embers.
Layout: one horizontal row of 6 equal 64:44 cells, image size 6144x704 (each cell 1024x704, 16 px a square); the ground ellipse's middle 7 squares above the cell's bottom; centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `shyvana_fx_de_singe.png`：E（龙形）：燃烧的地面烧到目标，3 帧

站在燃烧的地面上被烧：脚下冒出几簇小火苗（参考 shyvana_base_fire_2x2）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: SMALL FLAMES AT THE FEET, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three small flame tongues 4-7 squares tall rising from the bottom middle of the cell, flickering frame to frame, a few embers above.
Layout: one horizontal row of 3 equal 10:12 cells, image size 480x192 (each cell 160x192, 16 px a square); the flames rise from the cell's bottom middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `shyvana_fx_e_slow.png`：E：被减速（循环），4 帧

被火球减速：脚下一圈慢慢冒烟的余烬（参考 shyvana_base_burning_ash）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: SMOULDERING EMBERS AT THE FEET, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at an angle (about 3 times as wide as tall), its middle where the feet are 14 squares wide of glowing orange embers and dark ash, two thin wisps of grey-orange smoke rising 3-4 squares; each frame the embers glow in turn.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); the ellipse's middle 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `shyvana_fx_r_breath.png`：R 魔龙降世：沿途喷出的龙息（弹道，循环），4 帧

龙飞过去时往下喷的一大股火焰：一条宽宽的火流往前冲（参考 shyvana_base_vgu_w_ele_flat_energy、shyvana_base_tileflames02、shyvana_base_e_mis_flametrail）。**朝右飞、后面在左边，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A STREAM OF DRAGON FIRE, 4 frames, a seamless loop, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a wide rolling stream of flame 40 squares long and 16 tall, a white-yellow core along its middle, orange then red-crimson flame tongues at its top and bottom edges, its front rounded and brightest; each frame the flame tongues roll back along the stream.
Layout: one horizontal row of 4 equal 44:20 cells, image size 2816x320 (each cell 704x320, 16 px a square); the stream's middle on the cell's middle row, its front 2 squares from the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `shyvana_fx_r_hit.png`：R：被龙息烧到（恐惧），4 帧

被龙息喷中：身上一团火，冒起几缕往上飘的黑紫色恐惧烟（参考 tar_flash_fire、shyvana_base_burning_ash）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A DRAGON-FIRE HIT WITH FEAR, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an orange flash 8 squares across at chest height; 2 a burst of flame 12 across; 3 the flames rising with two dark violet smoke wisps curling up above the head; 4 wisps and embers.
Layout: one horizontal row of 4 equal 14:18 cells, image size 896x288 (each cell 224x288, 16 px a square); the burst 7 squares above the cell's bottom; centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `shyvana_fx_r_land.png`：R：龙落地的冲击，6 帧

龙从空中砸到地上：一圈火焰和尘土贴地冲开（参考 shyvana_base_ground01、shyvana_base_vgu_distortring、shyvana_base_ba_edgeaoe）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A FIERY LANDING SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse on the ground seen from above at an angle (about 3 times as wide as tall), its middle where the feet are; 1 a white flash under the body 20 squares wide; 2 a ring of fire and dust 50 wide racing out, cracks of glowing orange on the ground; 3 full, 84 wide, flames 10 squares tall along the ring; 4 the ring fading, dust rising; 5 glowing cracks and embers; 6 faint embers.
Layout: one horizontal row of 6 equal 86:36 cells, image size 8256x576 (each cell 1376x576, 16 px a square); the ground ellipse's middle 8 squares above the cell's bottom; the dragon stands in the middle, not drawn: 71 squares long and 43 tall, low on four legs in the middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `shyvana_fx_tf_dragon.png`：R：化身为龙的火焰，6 帧

她在空中化龙：一团火焰把她整个包住然后炸开（火柱、往外甩的火翼形状，参考 shyvana_base_vgu_awaken_sharpshape、shyvana_base_vgu_awaken_tile03、shyvana_base_vgu_awaken_ribbonmask01）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep orange-red dragon-fire ramp (#FFFFFF, #FFE27A, #FFAE2E, #FF6A1A, #E0321C, #A0161E, #5C0A1A).
Effect: A DRAGON TRANSFORMATION BURST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 16 squares across in the middle; 2 a column of fire 40 squares tall wrapping the middle; 3 the fire flaring out into two huge wing-shaped flame sheets to both sides, 60 squares wide; 4 the flame wings breaking into tongues; 5 embers spiralling out; 6 a few embers.
Layout: one horizontal row of 6 equal square cells, image size 6144x1024 (each cell 1024x1024, 16 px a square); centered in every cell (the middle of the burst on the cell's middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 25. `shyvana_fx_tf_human.png`：龙形结束：变回人的烟火，5 帧

魔龙时间到，变回人形：一团火焰收拢、散成火星和灰烟（参考 shyvana_base_burning_ash、tar_flash_fire_dissolve）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A TURN-BACK BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a ring of fire 40 squares wide collapsing inward; 2 a bright orange flash 20 across in the middle; 3 the flash breaking into embers and grey ash puffs (#B8AAA0, #847872, #5A4E4C, #3A3032); 4 ash and embers drifting up; 5 a few last embers.
Layout: one horizontal row of 5 equal square cells, image size 3840x768 (each cell 768x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 26. `shyvana_fx_fury_full.png`：龙怒攒满（循环），4 帧

龙怒攒满、可以化龙：她身边一圈跳动的小火苗往上窜（两侧肩膀和手边，参考 shyvana_base_fire_2x2、shyvana_base_w_sparks）。**中间她的身体位置留空**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an orange fire ramp (#FFFFFF, #FFF4B0, #FFD54A, #FF9E22, #F2601E, #C42E1C, #7E1420).
Effect: A DRAGON-FURY AURA, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): small orange flame tongues 3-6 squares tall rising at both sides of a standing body (at the shoulders and at the hands), a few gold sparks drifting up; the middle EMPTY where the body is; each frame the flames flicker in turn.
Layout: one horizontal row of 4 equal 30:44 cells, image size 1920x704 (each cell 480x704, 16 px a square); she stands in the middle, not drawn: 27 squares wide and 42 tall in the middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `shyvana_fx_a_hit` | view_effects `league_shyvana_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 12 × 12 |
| `shyvana_fx_q_slash` | view_effects `league_shyvana_q_slash`（她身上，画进她的动作帧；朝右） | 30 × 22 |
| `shyvana_fx_d_q_slash` | view_effects `league_shyvana_d_q_slash`（龙身上，画进龙的动作帧；朝右） | 48 × 34 |
| `shyvana_fx_q_hit` | view_effects `league_shyvana_q_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `shyvana_fx_q2_wave` | view_effects `league_shyvana_q2_wave`（跟随她，画在人物后面 z -1；左右对称） | 60 × 24 |
| `shyvana_fx_d_q2_wave` | view_effects `league_shyvana_d_q2_wave`（跟随龙，z -1；左右对称） | 90 × 34 |
| `shyvana_fx_q2_hit` | view_effects `league_shyvana_q2_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `shyvana_fx_q3_hit` | view_effects `league_shyvana_q3_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `shyvana_fx_w_aegis` | view_buffs `league_shyvana_w_on`（tag w_aegis；跟着她，循环，z 2；左右对称；龙形也用这张） | 44 × 50 |
| `shyvana_fx_w_blast` | view_effects `league_shyvana_w_blast`（跟随她，z -1；左右对称） | 72 × 46 |
| `shyvana_fx_w_hit` | view_effects `league_shyvana_w_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `shyvana_fx_w_heal` | view_effects `league_shyvana_w_heal`（跟随她，z 3；左右对称） | 26 × 30 |
| `shyvana_fx_e_ball` | view_projectiles `league_shyvana_e_ball`（跟着弹道转向；上下对称） | 16 × 10 |
| `shyvana_fx_e_hit` | view_effects `league_shyvana_e_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `shyvana_fx_e_blast` | view_effects `league_shyvana_e_blast`（落点，不跟随，z -1；左右对称） | 34 × 30 |
| `shyvana_fx_de_ball` | view_projectiles `league_shyvana_de_ball`（跟着弹道转向；上下对称） | 26 × 16 |
| `shyvana_fx_de_hit` | view_effects `league_shyvana_de_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `shyvana_fx_de_blast` | view_effects `league_shyvana_de_blast`（落点，不跟随，z -1；左右对称） | 64 × 44 |
| `shyvana_fx_de_singe` | view_effects `league_shyvana_de_singe`（跟随目标，z 2；左右对称） | 10 × 12 |
| `shyvana_fx_e_slow` | view_buffs `league_shyvana_e_slow`（跟着目标，循环，z 3；左右对称） | 16 × 8 |
| `shyvana_fx_r_breath` | view_projectiles `league_shyvana_r_breath`（跟着弹道转向；上下对称） | 44 × 20 |
| `shyvana_fx_r_hit` | view_effects `league_shyvana_r_hit`（跟随目标，z 2；左右对称） | 14 × 18 |
| `shyvana_fx_r_land` | view_effects `league_shyvana_r_land`（跟随龙，z -1；左右对称） | 86 × 36 |
| `shyvana_fx_tf_dragon` | view_effects `league_shyvana_tf_dragon`（跟随她，z 3；左右对称） | 64 × 64 |
| `shyvana_fx_tf_human` | view_effects `league_shyvana_tf_human`（跟随她，z 3；左右对称） | 48 × 48 |
| `shyvana_fx_fury_full` | view_buffs `league_shyvana_full`（tag fury_full；跟着她，循环，z 3；左右对称） | 30 × 44 |

- 两张表：`asset/league/effects/league_shyvana_fx`（小的）和 `league_shyvana_big`（d_q_slash、q2_wave、d_q2_wave、w_aegis、w_blast、e_blast、de_ball、de_blast、r_breath、r_land、tf_dragon、tf_human），tag = 名字（build_shyvana.py 的 views；buff w_on 的 tag 是 w_aegis，full 的 tag 是 fury_full）。
- 弹道（e_ball、de_ball、r_breath）断言上下对称；斩击（q_slash、d_q_slash）朝右、用 tools/fix/bake_caster_fx.py 画进她的帧（人形 skill、龙形 d_skill 的出手帧）；其余断言左右对称；e_blast、de_blast 不跟随（落点）。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给火焰描的最深色边（灰烟的暗边保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
