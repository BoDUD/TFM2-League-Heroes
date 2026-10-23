# 生化魔人 扎克：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型已定（`design/zac_design.png`：半透明亮绿色黏液做的大块头，身体里深绿色的纹路，驼着背，头埋在两个大肩膀中间，两只发黄光的眼睛，咧开的大嘴和尖牙，头顶一根弯触须，两条又粗又长的手臂、三根粗手指的大手，短粗的腿）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），44 格高、58 格宽（高×宽，连触须）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/zac_size.png`：扎克放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里扎克自己的特效贴图（大多是灰度或绿色的形状），按用在我们哪张特效分好了行，只在本地用。**扎克是活的黏液，所有特效都是他的黏液**：亮绿色、半透明的光泽、几块大的黄绿色湿亮高光和白色亮点、深绿色的暗部；黏液块、水花、水滴、往下滴的丝、拉长的橡皮手臂；不要火、不要电、不要光滑的霓虹光束。
> - **特效要亮**：每块黏液都有最亮一档或白色的亮点，暗底上一眼能看见。
> - **黏液、水花、冲击波、尘土都没有黑描边**（用它自己最深的一档）。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`q_fist`、`b_fly`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `zac_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/zac_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/zac_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 大拳头砸 | `a_hit` |
| 被动「细胞分裂」 | 技能打中英雄时甩出一块黏液落在地上，扎克走过去吃掉回血（复活在扩展包里） | `b_fly` · `b_lie` · `b_pick` |
| 普攻里的「不稳定物质」（W） | 冷却好了普攻时身上的黏液往四周炸开，按敌人最大生命值加伤害 | `w_burst` · `w_hit` |
| 技能 1 =「延伸打击」 | 手臂像橡皮一样拉长抓住敌人，再把他甩过来砸在地上 | `q_fist` · `q_hit` · `q_held` · `q_slam` · `slow` |
| 技能 2 =「橡筋弹弓」 | 两手按地把自己拉成弹弓，远远飞过去砸在地上，击飞一圈 | `e_land` · `e_hit` |
| 大招 =「动感弹球」 | 压扁身体连弹 4 次，每次落地击飞、减速 | `r_land` · `r_hit` · `slow` |

连招：**弹弓落地 → 不稳定物质**（落地马上炸开），**弹弓击飞 → 延伸打击**（马上抓住被击飞的英雄），**延伸打击甩人 → 动感弹球**，**最后一弹 → 不稳定物质**（并刷新）。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**黏液、水花、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **都是扎克的黏液**：亮绿、黄绿高光、白色亮点、深绿暗部；每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的亮点。
- 颜色（按每条写的用）：
  - 黏液·绿：`#F6FFC0`、`#D8F878`、`#8EE050`、`#48B848`、`#24823E`、`#104A2A`；
  - 暗部·深绿：`#3A9A66`、`#1E6448`、`#0E3A2C`、`#06201A`；
  - 亮点·白：`#FFFFFF`、`#F2FFE0`、`#D2F6A0`；
  - 尘土·浅灰黄：`#E6E0C8`、`#BDB394`、`#8C8466`、`#5E5844`；
- 打中、爆发居中画，不旋转；地面上的圈（水花圈、冲击波、脚下的黏液）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `zac_fx_a_hit.png`：普攻：大拳头砸中，3 帧

拳头砸中敌人：一团绿色黏液啪地溅开，中间一个白亮的闪光，四周甩出几颗圆圆的黏液滴。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A GOO PUNCH LANDING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-green flash 5 squares across with a splat of green goo round it; 2 the goo splashing out into a ring of round droplets and short drips 13 across at mirrored places; 3 the droplets further out and smaller, dimming to their darker shades. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `zac_fx_w_burst.png`：不稳定物质：扎克身上爆开的黏液，6 帧

不稳定物质（参考 goo_02、chunk、goo_e_pool）：扎克**整个人往外一鼓，一圈黏液从他身上往四周炸开**——地上溅开一个绿色的椭圆水花圈，空中飞出十几块大小不一的黏液块和水滴，越飞越远越小。扎克站在正中间不画（58 格宽、44 格高），**身体的位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a dark green depth ramp (#3A9A66, #1E6448, #0E3A2C, #06201A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: AN EXPLOSION OF GOO, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Zac stands in the middle, not drawn: 58 squares wide and 44 tall (to the tendril's tip) - leave his body's place EMPTY: 1 a bulging green rim hugging his outline with white glints; 2 the rim bursting outward: a dozen goo chunks and round droplets (2 to 5 squares) flying out all round at mirrored places, a green splash ring opening on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 40 wide; 3 the chunks further out, the ring 56 wide with goo drips rising from its edge; 4 the chunks at the cell's edge, smaller, the ring 62 wide and thinner; 5 a few drops left, the ring breaking into puddle spots; 6 the last spots fading. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 6 equal 64:44 cells, image size 6144x704 (each cell 1024x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `zac_fx_w_hit.png`：不稳定物质：黏液砸中，3 帧

被不稳定物质的黏液块砸中：一块黏液啪地糊在敌人身上溅开，几颗小水滴。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A GOO CHUNK SPLATTING, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a green goo chunk 5 squares across with a white glint; 2 it splatting flat into a wide splash 11 across with four short drips at mirrored places; 3 the splash dripping down, fading. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `zac_fx_q_fist.png`：延伸打击：拉长的手臂和大手，4 帧循环

延伸打击（参考 q_stretcharm、q_orb_mis）：扎克**像橡皮一样拉长的绿色手臂**——一截长长的黏液手臂，前面是**张开的大手（三根粗手指朝右张开）**，后面的手臂一截截有点波纹。**朝右飞、上下对称**，4 帧循环（手指一张一合、手臂上的高光往后走）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a dark green depth ramp (#3A9A66, #1E6448, #0E3A2C, #06201A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A STRETCHED RUBBER ARM, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): at the right a BIG OPEN GREEN HAND 10 squares tall with three thick fingers spread forward (one in the middle, two mirrored above and below it), behind it a long stretched arm of glossy green goo 20 squares long and 6 thick with a dark green underside on both edges (mirrored) and a yellow-green highlight band along its middle; the fingers open and close a little and the highlight slides back along the arm frame to frame. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 30:12 cells, image size 1920x192 (each cell 480x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `zac_fx_q_hit.png`：延伸打击：抓中，4 帧

大手抓中敌人：一团绿色黏液啪地糊在敌人身上，拉出几根黏糊糊的丝往下滴，白色闪光一下。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a dark green depth ramp (#3A9A66, #1E6448, #0E3A2C, #06201A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A GOOEY GRAB, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares across on the target's chest; 2 a big green goo splat 15 across wrapping round it; 3 sticky strands stretching down from the splat at mirrored places, a few drops; 4 the strands dripping, fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 16:18 cells, image size 1024x288 (each cell 256x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `zac_fx_q_held.png`：延伸打击：被抓住的敌人身上的黏液手印，4 帧循环

被扎克抓住的敌人胸口：一团**黏在身上的绿色黏液**（像一只手按着），边缘慢慢往下滴，一闪一闪的高光。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A GOO GRIP STUCK ON THE TARGET, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a glossy green goo blob 10 squares across like a hand pressed on the chest, three short drips under it at mirrored places that stretch and shorten, a yellow-green highlight that pulses. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `zac_fx_q_slam.png`：延伸打击：甩人砸地，6 帧

把人甩过来砸在地上（参考 goo_e_pool、dust）：地上溅起一个**绿色的黏液水花圈**，中间一下白光，四周飞起黏液滴和尘土。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a pale dust ramp (#E6E0C8, #BDB394, #8C8466, #5E5844), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A SLAM ON THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-green flash 10 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 a splash of green goo bursting up from it 30 wide with pale dust puffs at both sides; 3 a goo splash ring 46 wide on the ground with droplets thrown up in arcs at mirrored places; 4 the ring 54 wide, the droplets falling, the dust spreading; 5 puddle spots and settling dust; 6 fading. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:26 cells, image size 5376x416 (each cell 896x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `zac_fx_slow.png`：减速：脚下的黏液，4 帧循环（Q 和 R 的减速共用）

被减速的敌人脚下：一小滩**黏糊糊的绿色黏液**粘着脚，边上冒一两个小泡。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a dark green depth ramp (#3A9A66, #1E6448, #0E3A2C, #06201A).
Effect: A STICKY GOO PUDDLE, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat glossy green puddle on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 wide and 5 tall with a darker rim, two small bubbles at mirrored places that swell and pop in turn, a highlight sliding across. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 18:7 cells, image size 1152x112 (each cell 288x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `zac_fx_e_land.png`：橡筋弹弓：落地，6 帧

弹弓落地（参考 goo_e、goo_e_pool、dust）：扎克重重砸在地上，**一大圈绿色黏液水花炸开**，地上一圈波纹往外推，尘土和黏液滴飞起。比甩人砸地更大。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a pale dust ramp (#E6E0C8, #BDB394, #8C8466, #5E5844), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A HEAVY LANDING, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Zac stands in the middle, not drawn: 58 squares wide and 44 tall (to the tendril's tip) - leave his body's place EMPTY: 1 a white-green impact flash 24 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 a crown of green goo splashing up all round 40 wide with pale dust bursting out at both sides; 3 a goo shockwave ring 56 wide on the ground, droplets and dust thrown out at mirrored places; 4 the ring 64 wide, thinner, the droplets falling; 5 puddle spots and settling dust; 6 fading. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 6 equal 66:28 cells, image size 6336x448 (each cell 1056x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `zac_fx_e_hit.png`：橡筋弹弓：被撞飞，4 帧

被弹弓砸中击飞的敌人：脚下一团黏液往上溅，几颗水滴往上飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A KNOCK-UP SPLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a green goo splash bursting up from the target's feet 12 wide; 2 goo spikes and droplets flying upward past the target's sides at mirrored places; 3 the droplets high, the splash falling; 4 fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 14:20 cells, image size 896x320 (each cell 224x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `zac_fx_r_land.png`：动感弹球：每一下落地，5 帧

弹球每一次落地（参考 r_puddle、r_bubble）：扎克压扁砸在地上，**地上溅开一个绿色黏液水花圈**，几个泡泡和水滴弹起来。比弹弓落地小一点、快一点。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a dark green depth ramp (#3A9A66, #1E6448, #0E3A2C, #06201A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A BOUNCE LANDING, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Zac stands in the middle, not drawn: 58 squares wide and 44 tall (to the tendril's tip) - leave his body's place EMPTY: 1 a flat green goo splat 36 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) with a white glint; 2 a splash ring 50 wide with goo bubbles and droplets bouncing up at mirrored places; 3 the ring 56 wide, the bubbles popping; 4 puddle spots; 5 fading. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 5 equal 58:24 cells, image size 4640x384 (each cell 928x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `zac_fx_r_hit.png`：动感弹球：被弹中，3 帧

被弹球砸中击飞的敌人：一团黏液从脚下弹起来糊在身上，几颗泡泡。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A BOUNCE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a green goo splash rising from the target's feet 12 wide; 2 goo droplets and two bubbles flying up past its sides at mirrored places; 3 fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal 14:18 cells, image size 672x288 (each cell 224x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `zac_fx_b_fly.png`：细胞分裂：甩出去的黏液块，3 帧循环

技能打中英雄时从扎克身上甩出去的一小块黏液：一颗圆圆的绿色黏液球，后面拖两三颗小水滴。**朝右飞、上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A FLYING GOO BLOB, 3 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a round glossy green goo blob 5 squares across at the right with a white glint, two or three tiny droplets trailing behind it on the left that shift frame to frame. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 3 equal 10:6 cells, image size 480x96 (each cell 160x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `zac_fx_b_lie.png`：细胞分裂：地上的黏液块，3 帧循环

掉在地上等扎克去吃的黏液块（参考 blob_health）：一小团**圆鼓鼓的绿色黏液**趴在地上，轻轻地一鼓一缩，顶上一格白亮。**左右对称**，3 帧循环（一共 15 帧长，循环放）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a dark green depth ramp (#3A9A66, #1E6448, #0E3A2C, #06201A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: A GOO BLOB ON THE GROUND, 3 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small round glossy green blob 8 squares wide and 5 tall sitting on the ground, a darker flat rim at its foot, a white glint on top; it wobbles - a little taller and narrower, then lower and wider. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 3 equal 10:7 cells, image size 480x112 (each cell 160x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `zac_fx_b_pick.png`：细胞分裂：吃回黏液块回血，4 帧

扎克走过去把黏液块吸回身上：几团绿色黏液往他身上飞回去融进身体，冒出一圈淡绿色的小光点（回血）。扎克在中间不画，**身体的位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a living green goo ramp (#F6FFC0, #D8F878, #8EE050, #48B848, #24823E, #104A2A), a wet white glint ramp (#FFFFFF, #F2FFE0, #D2F6A0).
Effect: ABSORBING A BLOB, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); the body in the middle not drawn (leave a place 26 squares wide and 36 tall EMPTY): 1 two goo blobs at the bottom corners moving in; 2 the blobs merging into the body's lower edge with a green splash; 3 small pale green sparkles rising up both sides at mirrored places; 4 the sparkles at the top, fading. everything is Zac's LIVING GOO: glossy translucent green slime with a few big yellow-green wet highlights and white glints, dark green depths, round droplets, drips and stretched strands; flat shades, crisp shapes; no fire, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 30:40 cells, image size 1920x640 (each cell 480x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `zac_fx_a_hit` | view_effects `league_zac_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `zac_fx_w_burst` | view_effects `league_zac_w_burst`（大表，在他身上，不跟随，z -1；左右对称） | 64 × 44 |
| `zac_fx_w_hit` | view_effects `league_zac_w_hit`（跟随目标，z 2；左右对称） | 12 × 12 |
| `zac_fx_q_fist` | view_projectiles `league_zac_q_fist`（弹道，z 2；上下对称） | 30 × 12 |
| `zac_fx_q_hit` | view_effects `league_zac_q_hit`（跟随目标，z 2；左右对称） | 16 × 18 |
| `zac_fx_q_held` | view_buffs `league_zac_q_held`（跟随，胸口，z 3；左右对称） | 12 × 12 |
| `zac_fx_q_slam` | view_effects `league_zac_q_slam`（大表，在他身前的地上，不跟随，z 2；左右对称） | 56 × 26 |
| `zac_fx_slow` | view_buffs `league_zac_q_slow` / `r_slow`（tag `slow`，跟随，脚下，z -1；左右对称） | 18 × 7 |
| `zac_fx_e_land` | view_effects `league_zac_e_land`（大表，在他落地的地方，不跟随，z -1；左右对称） | 66 × 28 |
| `zac_fx_e_hit` | view_effects `league_zac_e_hit`（跟随目标，z 2；左右对称） | 14 × 20 |
| `zac_fx_r_land` | view_effects `league_zac_r_land`（大表，在他落地的地方，不跟随，z -1；左右对称） | 58 × 24 |
| `zac_fx_r_hit` | view_effects `league_zac_r_hit`（跟随目标，z 2；左右对称） | 14 × 18 |
| `zac_fx_b_fly` | view_projectiles `league_zac_b_fly`（弹道，z 2；上下对称） | 10 × 6 |
| `zac_fx_b_lie` | view_effects `league_zac_b_lie`（在地上，不跟随，z -1；左右对称；每 15 帧放一次） | 10 × 7 |
| `zac_fx_b_pick` | view_effects `league_zac_b_pick`（跟随他，z 3；左右对称） | 30 × 40 |

- 两张表：`asset/league/effects/league_zac_fx`（小的）和 `league_zac_big`（w_burst、q_slam、e_land、r_land），tag = 名字（build_zac.py 的 views；两个减速用 `slow`）。
- 弹道（q_fist、b_fly）断言上下对称；其余断言左右对称；b_lie 每 15 帧盖一次（3 帧循环），q_held 跟随约 34 帧，slow 1 秒。
- 用 `pixel_1x/` 切格（import_aurora_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
