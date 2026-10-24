# 暴怒骑士 克烈：给 Codex 的特效提示词（第 3 步）

> **这一份是 21 张特效图。** 造型已定（`design/kled_design.png`：Q 版的约德尔老兵克烈——大尖耳朵、青绿红边帽子上的钢尖刺、米白大胡子、狂笑的尖牙、一只瞎眼，拿着小双刃斧和绳子拴的捕熊夹——骑在橙黄鳞片、紫肚子、青蓝头刺的大蜥蜴斯嘎尔背上；斯嘎尔被打跑后他下马步行，双手拿大斧，还会掏一把短火枪）。他在游戏里是**高清**的（每个游戏格子里约 2×2 个细像素），骑乘时 40 格高、32 格宽（高×宽，帽尖到爪子）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/kled_size.png`：克烈放大 4 倍，最低点在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里克烈自己的特效贴图（大多是发光的形状），按用在我们哪张特效分好了行，只在本地用。**克烈是暴怒骑士**：他的特效是**怒气**——白黄色的亮心、**橙色到红色的火星和火苗**、火星尖上一点**暗紫红**；冲刺和冲锋是**土黄色的尘土**；捕熊夹是**钢灰色**加**棕色绳子**；手枪是**青绿色的火药烟**。不要冰、不要电、不要魔法光。
> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。
> - **光、火、尘土、冲击都没有黑描边**（用它自己最深的一档）；捕熊夹和绳子是实物，用它们自己最暗的一档勾边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`q_trap`、`p_blast`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。
> - **持续的画面**（怒气光环、被拴住、加速风线、冲锋护盾）只画几帧循环，Claude 导入时按时长拉开循环。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kled_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/kled_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/kled_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 暴烈秉性（W，并进普攻） | 挥斧；隔一阵四下快攻，第四下重击 | `a_hit` · `w_on` · `w_aura` · `w_hit` · `w_ready` |
| 被动「怯战蜥蜴斯嘎尔」 | 斯嘎尔的血打空就逃跑、克烈下马；打人攒勇气，攒满斯嘎尔回来 | `dismount` · `remount` · `haste` |
| 技能 1 =「飞索捕熊器」 | 扔出拴绳的捕熊夹，夹住英雄，过一会儿拽过来 | `q_trap` · `q_hit` · `q_mark` · `q_rope` · `q_yank` |
| 技能 1（下马时）=「随身手枪」 | 往前喷一枪霰弹，后坐力把自己弹开 | `p_blast` · `p_flash` · `p_hit` |
| 技能 2 =「比武」 | 斯嘎尔冲过目标，穿过英雄还能再冲回来；冲完加速 | `e_dust` · `e_hit` · `haste` |
| 大招 =「冲啊——！！」 | 带护盾冲向英雄、给队友加速、撞上去击退 | `r_trail` · `r_crash` · `r_hit` · `haste` |

连招：**Q 拽过来 → 马上 E**，**E 穿过英雄 → 再冲一次 → 暴烈秉性就绪**，**R 撞中 → 马上 Q**，**上马 → 暴烈秉性就绪**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火、尘土、冲击没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂；火星是有棱角的尖块，不是圆团。
- **要亮**：每个形状都有最亮一档或白色的亮点。
- 颜色（按每条写的用）：
  - 怒气·白黄到橙红：`#FFFFFF`、`#FFF6B8`、`#FFD848`、`#FFA020`、`#F06418`、`#C02C14`；
  - 火星尖·暗紫红：`#7A1838`、`#4E1030`、`#2E0A22`；
  - 尘土·米黄到棕：`#F6EAD0`、`#DCC49A`、`#B49470`、`#86684C`、`#5C4634`；
  - 钢·捕熊夹：`#FFFFFF`、`#DCE2EA`、`#AEB6C4`、`#767E8E`、`#4A505E`；
  - 绳子·棕：`#D29A60`、`#A06A3C`、`#6E4426`；
  - 火药烟·青绿：`#ECFFF6`、`#A4F2D4`、`#4ECDAA`、`#24907E`；
  - 闪光·白：`#FFFFFF`、`#FFFDF0`、`#FFF2C8`；
- 打中、爆发居中画，不旋转；地面上的东西（尘土、冲击波）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（21 张）

21 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `kled_fx_a_hit.png`：普攻：斧头砍中，3 帧

斧头砍中敌人（参考 ba_hit_flash、ba_hit_blast、ba_hit_splash）：中间一下白黄色闪光，**几道橙红色的火星往外溅**，尖端暗紫红。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dark purple-red ramp only for the outer tips of sparks (#7A1838, #4E1030, #2E0A22).
Effect: AN AXE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares across; 2 a burst 13 across - five or six short orange-red spark streaks flying out at mirrored places, dark purple-red tips; 3 the sparks further out and smaller, fading. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kled_fx_w_on.png`：暴烈秉性：怒气爆发，4 帧

暴烈秉性开始（参考 w_hand_glow、w_weapon_swirl、w_swirl）：克烈身上**猛地冒出一圈橙红色的怒气火焰**，往上窜，几道火星飞出。**只画外圈，身体位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dark purple-red ramp only for the outer tips of sparks (#7A1838, #4E1030, #2E0A22), a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8).
Effect: A RAGE FLARE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a ring of orange flame licks round the unit's feet 20 wide; 2 the flames shooting up both sides 30 tall, white-yellow at their roots; 3 the flames 42 tall with sparks flying off at mirrored places; 4 the flames thinning to wisps. The middle EMPTY. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow. Kled on his lizard stands in the middle, not drawn: 31 squares wide and 40 tall (the hat spike to the claws).
Layout: one horizontal row of 4 equal 36:44 cells, image size 2304x704 (each cell 576x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kled_fx_w_aura.png`：暴烈秉性：快攻期间的怒气，4 帧循环

暴烈秉性的四下快攻期间（参考 w_trail_01、w_weapon_noise）：脚下**一圈橙红色的小火苗在跳**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dark purple-red ramp only for the outer tips of sparks (#7A1838, #4E1030, #2E0A22).
Effect: A RAGE RING, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), a flat ring of small orange-red flame licks 32 wide and 8 tall, the licks at mirrored places flickering up and down in turn. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow.
Layout: one horizontal row of 4 equal 34:10 cells, image size 2176x160 (each cell 544x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kled_fx_w_hit.png`：暴烈秉性：第四下重击，4 帧

第四下打中（参考 w_hit_spark、w_hit_bits、ba_crit_splash）：**一个大的白黄色爆点**，一圈锯齿状的橙红火星炸开，比普攻大一圈。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dark purple-red ramp only for the outer tips of sparks (#7A1838, #4E1030, #2E0A22).
Effect: A HEAVY CRIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow burst 9 squares across; 2 a jagged ring of orange-red spikes 20 across round it at mirrored places; 3 the spikes breaking into sparks flying out; 4 fading sparks. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal square cells, image size 1408x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kled_fx_w_ready.png`：暴烈秉性就绪：头上的怒气，3 帧

比武冲回来以后暴烈秉性重新就绪（参考 p_warning_swirl）：他头上一个**橙色的怒气标记**一闪（像漫画里的青筋）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8).
Effect: A RAGE MARK, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small white-yellow spark 3 squares; 2 a jagged orange anger mark (four short bent strokes, like a cartoon vein) 11 across; 3 it fading. Drawn at the TOP of the cell. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kled_fx_q_trap.png`：飞索捕熊器：飞出去的捕熊夹，3 帧循环

扔出去的**捕熊夹**（参考 q_trap_head、q_rope）：前头一个张开的钢灰色捕熊夹（两排尖齿），后面拖着一截棕色的绳子。**朝右飞、上下对称**，3 帧循环（绳子抖）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#FFFFFF, #DCE2EA, #AEB6C4, #767E8E, #4A505E), a rope ramp (#D29A60, #A06A3C, #6E4426).
Effect: A FLYING BEAR TRAP, 3 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): at the front a steel bear trap seen from the side, its two jaws OPEN like a V pointing right with a row of sharp teeth on each jaw, 8 squares long; behind it on the left a brown rope 1 square thick and 14 long, its knots stepping back frame to frame. Steel and rope only, no glow.
Layout: one horizontal row of 3 equal 22:10 cells, image size 1056x160 (each cell 352x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kled_fx_q_hit.png`：飞索捕熊器：夹子咬中，3 帧

捕熊夹咬中敌人：一下白色闪光，几块钢屑和火星往外溅。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a steel ramp (#FFFFFF, #DCE2EA, #AEB6C4, #767E8E, #4A505E), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14).
Effect: A TRAP SNAP, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 7 squares across; 2 small steel splinters and orange sparks flying out 15 across at mirrored places; 3 fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kled_fx_q_mark.png`：飞索捕熊器：夹住英雄的一闪，3 帧

夹住英雄时它头上一闪的**感叹号火花**（参考 q_indicator_mult、e_mark）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8).
Effect: AN ALERT FLASH, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small white-yellow spark; 2 a bold orange exclamation mark 9 tall inside a jagged ring 11 across; 3 fading. Drawn at the TOP of the cell (over the head). a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kled_fx_q_rope.png`：飞索捕熊器：被拴住，4 帧循环

被捕熊夹拴住的 1.5 秒（参考 q_trap_head、q_rope、q_rope_break）：**脚上咬着一个钢灰色的捕熊夹**，两边各垂着一小截棕色绳子，夹子一抖一抖。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a steel ramp (#FFFFFF, #DCE2EA, #AEB6C4, #767E8E, #4A505E), a rope ramp (#D29A60, #A06A3C, #6E4426).
Effect: A TRAP ON THE ANKLES, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): at the BOTTOM of the cell (the unit's feet) a CLOSED steel bear trap seen from the front, 12 squares wide and 5 tall, its teeth biting, a short brown rope end hanging on each side; the trap jolting up and down one square in turn.
Layout: one horizontal row of 4 equal 18:10 cells, image size 1152x160 (each cell 288x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kled_fx_q_yank.png`：飞索捕熊器：拽回来，4 帧

敌人被拽过来的一下（参考 q_rope_break、e_rock_debris）：一下白闪，**几截断开的棕色绳头往两边甩**，脚下一团尘土。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a rope ramp (#D29A60, #A06A3C, #6E4426), a dust ramp from beige to brown (#F6EAD0, #DCC49A, #B49470, #86684C, #5C4634).
Effect: A YANK, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares across; 2 snapped brown rope ends whipping out to both sides 20 across and a puff of beige dust at the feet; 3 the dust spreading; 4 fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 22:20 cells, image size 1408x320 (each cell 352x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kled_fx_p_blast.png`：随身手枪：喷出去的霰弹，3 帧循环

随身手枪的霰弹（参考 kledrider_q_cas、ba_trail_head）：**一扇形的五颗白黄色弹丸**往前飞，后面拖着短短的火线和一点青绿色的烟。**朝右飞、上下对称**，3 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a teal-green smoke ramp (#ECFFF6, #A4F2D4, #4ECDAA, #24907E), a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8).
Effect: A SHOTGUN SPRAY, 3 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): five bright white-yellow pellets in a fan spreading to the right (the middle one in front, two above and two below at mirrored places), each with a short orange streak behind it, a little teal-green smoke at the left end; the streaks flickering. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow.
Layout: one horizontal row of 3 equal 30:14 cells, image size 1440x224 (each cell 480x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kled_fx_p_flash.png`：随身手枪：开枪的烟，4 帧

开枪的一下（参考 kledrider_q_cas、r_smoke_dust）：他身前**一团青绿色的火药烟**炸开，中间一点白黄闪光，往两边散。（这张跟着他，两边都会用，所以**左右对称**）4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a teal-green smoke ramp (#ECFFF6, #A4F2D4, #4ECDAA, #24907E), a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14).
Effect: A GUNSMOKE PUFF, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow flash 6 squares across in the middle at chest height; 2 a round puff of teal-green smoke 18 across with a few orange sparks at mirrored places; 3 the smoke spreading to both sides 28 across; 4 thin wisps. Kled on foot stands in the middle, not drawn: 29 squares wide and 30 tall.
Layout: one horizontal row of 4 equal 30:22 cells, image size 1920x352 (each cell 480x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `kled_fx_p_hit.png`：随身手枪：被霰弹打中，3 帧

被霰弹打中：几个白黄色的小爆点，一点青绿色的烟。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a teal-green smoke ramp (#ECFFF6, #A4F2D4, #4ECDAA, #24907E).
Effect: PELLET HITS, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 four small white-yellow pops at mirrored places 12 across; 2 they bursting into orange sparks with a little teal-green smoke; 3 fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `kled_fx_e_dust.png`：比武：冲出去踢起的土，4 帧

斯嘎尔起冲时（参考 e_ground_burn、e_rock_debris、i_footstep）：脚下**踢起一大片土黄色的尘土和小石块**，贴着地往两边散。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp from beige to brown (#F6EAD0, #DCC49A, #B49470, #86684C, #5C4634), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14).
Effect: A DUST KICK-UP, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 1 a low puff of beige dust 16 squares wide; 2 the dust spreading to both sides 30 wide and 8 tall, a few small brown rocks flying up at mirrored places, two short orange scorch streaks on the ground; 3 38 wide, thinner; 4 fading wisps at both ends.
Layout: one horizontal row of 4 equal 40:12 cells, image size 2560x192 (each cell 640x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `kled_fx_e_hit.png`：比武：冲过去撞中，3 帧

冲刺穿过敌人（参考 ba_crit_swipe、e_mark）：**一道白黄色的交叉斩光**（X 形，左右对称），几颗火星。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dark purple-red ramp only for the outer tips of sparks (#7A1838, #4E1030, #2E0A22).
Effect: A JOUSTING SLASH, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-yellow X of two crossing slash streaks 16 across; 2 the X orange with sparks flying out at mirrored places; 3 fading. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 864x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `kled_fx_haste.png`：加速：身边的风线，4 帧循环

比武、冲锋的加速和重新上马的加速（参考 r_speed_wind、r_speed_wind_side、common_global_speedbuff）：身子两边**几道浅黄白色的风线**往外掠。**左右对称**（两边的风线互为镜像），4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a dust ramp from beige to brown (#F6EAD0, #DCC49A, #B49470, #86684C, #5C4634).
Effect: SPEED LINES, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on BOTH sides of the unit (the middle empty) three short pale yellow-white streaks 6-9 squares long, the left side's and the right side's mirroring each other, stepping outward frame to frame and fading at their ends. Kled on his lizard stands in the middle, not drawn: 31 squares wide and 40 tall (the hat spike to the claws).
Layout: one horizontal row of 4 equal 30:16 cells, image size 1920x256 (each cell 480x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `kled_fx_r_trail.png`：冲啊：冲锋时罩着的护盾，4 帧循环

冲锋的一路（参考 r_shield_base、r_shield_outer、r_trail、r_smoke_dust）：**一圈橙色的护盾光环罩着克烈和斯嘎尔**（外圈亮、中间留空），脚下两边各一团尘土。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dark purple-red ramp only for the outer tips of sparks (#7A1838, #4E1030, #2E0A22), a dust ramp from beige to brown (#F6EAD0, #DCC49A, #B49470, #86684C, #5C4634).
Effect: A CHARGE SHIELD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an oval ring of orange shield light round the unit 40 squares wide and 44 tall, 1-2 squares thick, brighter white-yellow arcs at mirrored places moving round, a low puff of beige dust at the feet on both sides; the middle EMPTY. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow. Kled on his lizard stands in the middle, not drawn: 31 squares wide and 40 tall (the hat spike to the claws).
Layout: one horizontal row of 4 equal 44:46 cells, image size 2816x736 (each cell 704x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `kled_fx_r_crash.png`：冲啊：撞上去，5 帧

斯嘎尔撞上第一个英雄（参考 r_destination_mark、r_glow、r_smoke_dust、e_rock_debris）：地上**一圈冲击波**，**尘土和石块往四周炸开**，中间一下白黄闪光。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dust ramp from beige to brown (#F6EAD0, #DCC49A, #B49470, #86684C, #5C4634).
Effect: A CRASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), 1 a white-yellow flash 14 wide; 2 an orange shockwave ring 34 wide and 11 tall with dust bursting up; 3 the ring 50 wide, beige dust clouds and brown rocks flying out at mirrored places; 4 the dust settling; 5 fading wisps. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow.
Layout: one horizontal row of 5 equal 52:26 cells, image size 4160x416 (each cell 832x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `kled_fx_r_hit.png`：冲啊：被撞中，4 帧

被斯嘎尔撞中：一个**大的白黄色冲击星**，一圈橙红色的锯齿和尘土。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dust ramp from beige to brown (#F6EAD0, #DCC49A, #B49470, #86684C, #5C4634).
Effect: A RAM IMPACT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-yellow impact star 12 across; 2 a jagged orange-red ring 22 across with beige dust puffs at mirrored places; 3 sparks and dust out; 4 fading. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal square cells, image size 1536x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `kled_fx_dismount.png`：斯嘎尔逃跑：下马的一下，5 帧

斯嘎尔的血打空、吓得逃跑（参考 p_offmount_mark、p_distortion、r_smoke_dust）：**一大团土黄色的烟尘炸开**，几片橙色的鳞片和青蓝色的刺往外飞，中间上方一个**大大的橙色感叹号火花**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp from beige to brown (#F6EAD0, #DCC49A, #B49470, #86684C, #5C4634), a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8).
Effect: A POOF, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 12 across; 2 a big round cloud of beige dust 36 across bursting out, a bold orange exclamation spark above its middle; 3 the cloud 48 wide, a few small orange scales and teal-blue spines flying out at mirrored places; 4 the cloud thinning; 5 wisps. Kled on his lizard stands in the middle, not drawn: 31 squares wide and 40 tall (the hat spike to the claws).
Layout: one horizontal row of 5 equal 50:46 cells, image size 4000x736 (each cell 800x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `kled_fx_remount.png`：斯嘎尔回来：上马的一下，5 帧

勇气攒满、斯嘎尔回来（参考 r_glow、p_warning_swirl、ba_hit_flash）：**一圈橙红色的怒气火焰往上冲**，尘土从两边卷起来，顶上几颗火星。**只画外圈，身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rage ramp from white-yellow to orange and red (#FFFFFF, #FFF6B8, #FFD848, #FFA020, #F06418, #C02C14), a dust ramp from beige to brown (#F6EAD0, #DCC49A, #B49470, #86684C, #5C4634), a white flash ramp (#FFFFFF, #FFFDF0, #FFF2C8).
Effect: A REMOUNT BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a ring of white-yellow light at the feet 24 wide; 2 orange-red flames and beige dust swirling up both sides 30 tall; 3 the flames 44 tall with sparks at mirrored places on top; 4 the flames breaking up; 5 sparks fading. The middle EMPTY. a grumpy warrior's RAGE: hot white-yellow cores, orange and red sparks and streaks with dark purple-red tips, beige dust; flat shades, crisp shapes; no ice, no electricity, no magic glow. Kled on his lizard stands in the middle, not drawn: 31 squares wide and 40 tall (the hat spike to the claws).
Layout: one horizontal row of 5 equal 50:46 cells, image size 4000x736 (each cell 800x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kled_fx_a_hit` | view_effects `league_kled_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `kled_fx_w_on` | view_effects `league_kled_w_on`（跟随他，z 3；左右对称） | 36 × 44 |
| `kled_fx_w_aura` | view_buffs `league_kled_vt`（tag `w_aura`，跟随，脚下，z -1；左右对称） | 34 × 10 |
| `kled_fx_w_hit` | view_effects `league_kled_w_hit`（跟随目标，z 2；左右对称） | 22 × 22 |
| `kled_fx_w_ready` | view_effects `league_kled_w_ready`（跟随他，头上，z 3；左右对称） | 12 × 12 |
| `kled_fx_q_trap` | view_projectiles `league_kled_q_trap`（直线弹道，z 2；上下对称） | 22 × 10 |
| `kled_fx_q_hit` | view_effects `league_kled_q_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `kled_fx_q_mark` | view_effects `league_kled_q_mark`（跟随目标，头上，z 3；左右对称） | 12 × 12 |
| `kled_fx_q_rope` | view_buffs `league_kled_q_slow`（tag `q_rope`，跟随，脚下，z 3；左右对称） | 18 × 10 |
| `kled_fx_q_yank` | view_effects `league_kled_q_yank`（跟随目标，z 2；左右对称） | 22 × 20 |
| `kled_fx_p_blast` | view_projectiles `league_kled_p_blast`（直线弹道，很快，z 2；上下对称） | 30 × 14 |
| `kled_fx_p_flash` | view_effects `league_kled_p_flash`（跟随他，z 3；左右对称） | 30 × 22 |
| `kled_fx_p_hit` | view_effects `league_kled_p_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `kled_fx_e_dust` | view_effects `league_kled_e_dust`（大表，起冲的地方，不跟随，z -1；左右对称） | 40 × 12 |
| `kled_fx_e_hit` | view_effects `league_kled_e_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `kled_fx_haste` | view_buffs `league_kled_e_ms` / `league_kled_r_ms` / `league_kled_re_ms`（tag `haste`，跟随，z -1；左右对称） | 30 × 16 |
| `kled_fx_r_trail` | view_effects `league_kled_r_trail`（大表，跟随他，z 3；左右对称） | 44 × 46 |
| `kled_fx_r_crash` | view_effects `league_kled_r_crash`（大表，撞的地方，不跟随，z -1；左右对称） | 52 × 26 |
| `kled_fx_r_hit` | view_effects `league_kled_r_hit`（跟随目标，z 2；左右对称） | 24 × 24 |
| `kled_fx_dismount` | view_effects `league_kled_dismount`（大表，在他身上，不跟随，z 3；左右对称） | 50 × 46 |
| `kled_fx_remount` | view_effects `league_kled_remount`（大表，跟随他，z 3；左右对称） | 50 × 46 |

- 两张表：`asset/league/effects/league_kled_fx`（小的）和 `league_kled_big`（e_dust、r_trail、r_crash、dismount、remount），tag = 名字（build_kled.py 的 views；vt 用 `w_aura`，q_slow 用 `q_rope`，e_ms / r_ms / re_ms 用 `haste`）。
- 弹道（q_trap、p_blast）断言上下对称；其余断言左右对称。w_aura / q_rope / haste / r_trail 循环。
- 用 `pixel_1x/` 切格（import_sejuani_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
