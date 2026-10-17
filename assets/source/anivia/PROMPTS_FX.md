# 冰晶凤凰 艾尼维亚：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/anivia_idle.png`：3/4 正面朝右的冰晶凤凰，冰蓝色的冰晶羽毛，冰刺头冠、紫色额晶、洋红眼睛，近侧翅膀向下展开、远侧翅膀扬起；右边是寒霜涅槃的冰蛋）。她在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），38 格高、61 格宽，冰蛋 19 格高；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/anivia_size.png`：鸟和冰蛋的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/anivia_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效在哪一帧、出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里艾尼维亚自己的特效贴图和模型（大多是灰度或单色的形状，游戏里再上色；`iceblock` 是冰墙的冰块模型，`egg_break` 是冰蛋碎开的一帧），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**冰是白芯、青色、深蓝**，**雪和霜雾是白到淡蓝灰**，**风暴的地面是暗一些的霜蓝**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人（变蛋那张例外，写在那条里）。
> - **飞行物（a_bolt、q_ball、e_shard）画成往右飞、上下对称**：游戏按飞行方向转它，往左飞时整张图转半圈，上下对称才不会倒过来。
> - **其余全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，她和目标朝左时也是同一张图。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `anivia_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/anivia_fx/` 里，再打包成 `outputs/anivia_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 一枚冰弹飞向目标 | `a_bolt` · `a_hit` |
| 技能 1 = Q「寒冰闪耀」 | 大冰球飞向落点，碰到第一个英雄或到点就引爆，范围眩晕；晕到英雄时顺带 W「寒冰屏障」在原地竖起一面冰墙 5 秒 | `q_ball` · `q_blast` · `q_stun` · `w_wall` |
| 技能 2 = E「霜寒刺骨」 | 一根冰锥打一个目标，打冻住的目标伤害翻倍 | `e_shard` · `e_hit` · `e_iced` |
| 大招「冰川风暴」 | 目标处落下暴风雪，1.5 秒里从小长大，长满后伤害变 3 倍 | `r_cast` · `r_storm` · `r_formed` |
| 冰冻标记 | 被 Q 或长满的风暴打中的英雄 3 秒里头顶一枚雪花（这时 E 翻倍） | `iced` |
| 被动「寒霜涅槃」（扩展包） | 受到致命伤害变成冰蛋，撑过去就孵化 | `p_egg_in` · `p_hatch` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冰的反光、雪、霜雾、风、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（冰柱、冰晶这种实心的东西可以有深蓝的暗面，但不要一圈黑）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 冰（冰弹、冰球、冰锥、冰墙、冰爆）：`#FFFFFF`、`#E4FBFF`、`#A6EEFF`、`#5CCBF5`、`#2C8FD8`、`#155AA6`；
  - 雪、霜雾、风（拖尾、冷气、暴风雪）：`#FFFFFF`、`#EEF8FF`、`#CDE6FA`、`#9CC4EA`、`#6F94C8`、`#46669E`；
  - 风暴冻住的地面：`#BFD9F2`、`#7FA6D6`、`#4D6FB0`、`#2E4A8A`、`#1B2E60`、`#0E1A3A`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：Q 的爆炸半径 14000，冰墙长 50000，风暴半径 12000 → 32000）。

### 1. `anivia_fx_a_bolt.png`：普攻冰弹（飞行物，循环），4 帧

一小枚冰弹往右飞：尖尖的冰晶头（白芯、青色身体），后面拖 3 格霜雾和两三粒雪星，每帧闪光不一样（参考 IceArrow03、FrostCrystals）。**画成朝右飞，上下对称**（游戏会按飞行方向转它）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: an ICE BOLT, a seamless loop of 4 frames, drawn FLYING TO THE RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight: flying left it is upside down): a pointed ice crystal 6 squares long and 3 tall at the right with a white core and a cyan body, a short trail of frost mist 4 squares long behind it to the left with two or three tiny snow sparkles (mirrored top to bottom), the sparkles twinkling differently in each frame.
Layout: one horizontal row of 4 equal 12:6 cells, image size 768x96 (each cell 192x96, 16 px a square); the bolt's tip 1 square from the cell's right edge, its middle on the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `anivia_fx_a_hit.png`：普攻命中：冰屑炸开（目标身上），4 帧

冰弹打中：一闪白光，碎冰屑和雪星往四周溅开（参考 FrostCrystals、Flare-Rainbow_frost）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: an ICE BOLT HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white four-pointed flash 4 squares; 2 a burst of cyan ice chips 8 squares wide with a white core; 3 the chips flying out at mirrored places, snow sparkles; 4 fading frost mist.
Layout: one horizontal row of 4 equal square cells, image size 640x160 (each cell 160x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `anivia_fx_q_ball.png`：Q 寒冰闪耀：大冰球（飞行物，循环），4 帧

一颗大冰球往右飞（英雄联盟里是一颗晶莹的冰晶球，外面一层霜气）：球直径约 9 格，表面有冰晶的棱面，白芯；后面拖着一大团霜雾和雪星，冰屑在球边上转（参考 Q_TX、Q_Tar_Sphere、DirtBits_frost、snowflake）。**画成朝右飞，上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: a FLASH FROST ORB, a seamless loop of 4 frames, drawn FLYING TO THE RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight: flying left it is upside down): a big round ice orb 9 squares wide at the right of the cell, faceted like a crystal (bright facets, a white core, a deep blue rim), a thick trail of frost mist 8 squares long and tapering to the left, small ice chips and snow sparkles circling the orb at mirrored places (top and bottom), the mist and the sparkles different in each frame.
Layout: one horizontal row of 4 equal 18:12 cells, image size 1152x192 (each cell 288x192, 16 px a square); the orb's right edge 1 square from the cell's right edge, its middle on the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `anivia_fx_q_blast.png`：Q 引爆：冰爆（落点处，不跟随），6 帧

冰球炸开：一团白光，一圈冰碴往外飞，地上冒出一圈尖冰（扁椭圆，宽 30 格），霜雾腾起再散（参考 Q_GroundLight、groundflash、DirtBits_frost、Flare-Rainbow_frost）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: a FLASH FROST DETONATION at a spot on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares with short white rays; 2 a cyan-white burst 20 squares, a ring of ice shards flying out; 3 the shards 30 squares wide, a ring of sharp ice spikes jutting up from the ground (an ellipse 30 squares wide and 10 tall, spikes 4 to 8 squares tall), frost mist billowing; 4 the spikes at their tallest, the mist 36 squares wide; 5 the spikes cracking, the mist thinning; 6 a few ice chips and faint mist on the ground.
Layout: one horizontal row of 6 equal 40:36 cells, image size 3840x576 (each cell 640x576, 16 px a square); centered across, the ground ellipse's middle 10 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `anivia_fx_q_stun.png`：Q 冰冻眩晕（被晕的目标身上，约 1.1 秒），6 帧

被寒冰闪耀晕住的人：脚下迅速冻起一层冰壳（到膝盖高），身边竖起几根冰晶，头顶冒冷气；最后冰壳裂开碎掉（参考 FrostCrystals、IceShards、snowdust）。**左右对称**，中间身体位置留空（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn），冰壳画在脚和小腿的外缘、两边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: a FREEZE round a stunned champion, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): 1 frost creeping out round the feet (a pale ellipse 16 squares wide and 4 tall); 2 an ice crust growing up both sides of the legs to the knees (12 squares tall), 3 sharp ice crystals 6 to 8 squares tall at its sides, cold mist curling over the head; 3 and 4 the crust whole and glinting (a white glint moving up it); 5 the crust cracked with white lines; 6 shattering into ice chips flying out at mirrored places.
Layout: one horizontal row of 6 equal 22:40 cells, image size 2112x640 (each cell 352x640, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `anivia_fx_w_wall.png`：W 寒冰屏障：一排冰墙（墙心在落点，不跟随，5 秒），8 帧（1–2 长出、3–6 循环、7–8 融化碎掉）

一面**竖着的冰墙**：英雄联盟里是一排冰块（附图 iceblock：一根高高的锯齿状冰柱，旁边几根小冰晶，底下一圈雪）。在我们的画面里墙是**沿着屏幕上下方向排开的 5 根冰柱**（远的在上、近的在下，互相叠一点），每根约 12 格高、10 格宽；墙心（落点）在格子中间那一行，最上面一根冰柱的底在墙心上方 25 格，最下面一根的底在墙心下方 25 格。第 1 帧冰柱从地里冒出来（矮，冰屑飞溅）；第 2 帧长到全高；第 3–6 帧循环（冰柱上的高光一闪一闪、地面冒冷气，第 6 帧接得回第 3 帧）；第 7 帧冰柱出现裂纹、变矮；第 8 帧碎成冰碴。**左右对称**（每根冰柱都画成左右对称的）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: an ICE WALL, 8 frames (1-2 it rises, 3-6 a seamless loop, 7-8 it breaks), SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): five upright ice pillars in a vertical column down the cell (the far ones higher up, the near ones lower down, each overlapping the one behind), each pillar a tall jagged ice crystal 12 squares tall and 10 wide with two small crystals at its foot and a ring of snow at its base, white-cyan facets, a white glint, a deep blue shadowed side (each pillar symmetric left to right); the pillars' bases on rows 13, 25, 38, 50 and 63 of the cell (row 38 the wall's middle); 1 the pillars only 4 squares tall bursting from the ground with ice chips flying; 2 full height; 3, 4, 5, 6 the loop: glints running up the pillars, cold mist at their feet, different in each frame (6 flows back into 3); 7 the pillars cracked with white lines and a little shorter; 8 shattered into falling ice chips and mist.
Layout: one horizontal row of 8 equal 20:76 cells, image size 2560x1216 (each cell 320x1216, 16 px a square); centered across; the wall's middle (where it was cast) on the cell's middle row (row 38). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `anivia_fx_e_shard.png`：E 霜寒刺骨：冰锥（飞行物，循环），3 帧

一根冰锥往右飞：长 10 格的尖冰锥（白色刃边、青色锥身），后面一小缕霜雾（参考 IceArrow03、E_GroundLight）。**画成朝右飞，上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: a FROSTBITE ICICLE, a seamless loop of 3 frames, drawn FLYING TO THE RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it with its flight: flying left it is upside down): a sharp icicle 10 squares long and 3 tall pointing right, white edges, a cyan body, a white glint, a thin wisp of frost mist 3 squares long behind it, the glint and the wisp different in each frame.
Layout: one horizontal row of 3 equal 14:6 cells, image size 672x96 (each cell 224x96, 16 px a square); the tip 1 square from the cell's right edge, its middle on the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `anivia_fx_e_hit.png`：E 命中：冰锥碎裂（目标身上），4 帧

冰锥打中碎开：白光一闪，尖冰碎片往外飞，冷气散开。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: an ICICLE SHATTERING on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a cyan-white burst 10 squares, sharp ice splinters; 3 the splinters 14 squares out at mirrored places, frost mist; 4 fading mist and two or three chips.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `anivia_fx_e_iced.png`：E 打冰冻目标：加倍的冰爆（目标身上），5 帧

打中被冻住的目标（伤害翻倍）：比普通命中大一圈的冰爆，中间闪出一枚大雪花，冰碴和雪星往外炸（参考 snowflake、Flare-Rainbow_frost、frost_sprites）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: a DOUBLED FROSTBITE on a frozen unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white star flash 8 squares; 2 a big six-armed snowflake 14 squares wide flashing white-cyan, a cyan burst behind it; 3 the snowflake 18 squares, ice shards bursting out at mirrored places; 4 the snowflake breaking into sparkles, the shards 20 squares out; 5 fading sparkles and mist.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `anivia_fx_r_cast.png`：R 冰川风暴施法：双翼卷起风雪（她身上，跟随），6 帧

她高举双翼召唤风暴：身边卷起两股风雪，从地面往上盘旋到翅膀高处，雪花、冷风纹绕着她飞，最后散开（参考 R_Frost、wind_streaks、WindSwirl、snowdust）。**左右对称**，中间她的位置留空（a large ice phoenix 61 squares wide and 38 tall hovers in the middle, not drawn），风雪画在她两边和身后的外缘。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E) and an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6).
Effect: a BLIZZARD CALLED round a hovering phoenix, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a large ice phoenix 61 squares wide and 38 tall hovers in the middle, not drawn): 1 a cold gust ring on the ground under her (an ellipse 40 squares wide and 8 tall of white wind streaks); 2 two spirals of snow and wind rising on both sides from the ground; 3 the spirals up to her wings' height (40 squares), snowflakes swirling; 4 the widest, wind streaks curving round her; 5 the spirals breaking into snow; 6 falling snowflakes.
Layout: one horizontal row of 6 equal 70:52 cells, image size 6720x832 (each cell 1120x832, 16 px a square); centered across, her lowest point (the ground) on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `anivia_fx_r_storm.png`：R 风暴生长：从小变大（落点，不跟随，1.5 秒），6 帧

冰川风暴落地、一点点变大：每两帧大一档（地面上冻结的圆：宽 26 → 38 → 50 格），圆里地面结霜发暗，边上一圈白色风雪往里打旋，风雪柱 8–14 格高（参考 R_Frost、R_Ground_Darkness、wind_Streaks、snowdust）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep frost-blue ramp (#BFD9F2, #7FA6D6, #4D6FB0, #2E4A8A, #1B2E60, #0E1A3A), a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E) and an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6).
Effect: a GLACIAL STORM GROWING on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): frames 1-2 a frozen disc (an ellipse 26 squares wide and 10 tall: frosted ground in the deep blue ramp, darker at its rim) with a ring of white snow and wind swirling round its edge 8 squares tall; frames 3-4 the same 38 squares wide and 14 tall, the swirl 11 squares tall; frames 5-6 50 squares wide and 18 tall, the swirl 14 squares tall; snowflakes and wind streaks different in each frame, sparkling ice crystals at the rim.
Layout: one horizontal row of 6 equal 72:48 cells, image size 6912x768 (each cell 1152x768, 16 px a square); centered across, the ellipse's middle 14 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `anivia_fx_r_formed.png`：R 风暴成形：大暴风雪（落点，不跟随，约 4.5 秒），8 帧（1–2 长满、3–6 循环、7–8 散去）

风暴长满（伤害变 3 倍）：一大片冻住的地面（宽 64 格），整圈白色暴风雪墙往上卷到 20 格高，冰晶在边上闪，雪花在圈里飞；第 1 帧一道白蓝的闪光表示成形；第 3–6 帧循环（第 6 帧接得回第 3 帧）；第 7–8 帧风雪变弱、散开。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a deep frost-blue ramp (#BFD9F2, #7FA6D6, #4D6FB0, #2E4A8A, #1B2E60, #0E1A3A), a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E) and an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6).
Effect: a FULL GLACIAL STORM on the ground seen from above at an angle, 8 frames (1-2 it forms, 3-6 a seamless loop, 7-8 it dies), SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a frozen disc (an ellipse 64 squares wide and 24 tall, frosted ground in the deep blue ramp, its rim darker), a wall of white blizzard swirling round its whole edge up to 20 squares tall (snow, wind streaks, the near side brighter), ice crystals glinting at the rim, snowflakes flying inside; 1 a white-blue flash ring as it forms; 2 the blizzard rising; 3, 4, 5, 6 the loop, the swirl turning (6 flows back into 3); 7 the blizzard low, the disc fading; 8 a faint frosted ellipse and falling snow.
Layout: one horizontal row of 8 equal 76:52 cells, image size 9728x832 (each cell 1216x832, 16 px a square); centered across, the ellipse's middle 14 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `anivia_fx_iced.png`：冰冻标记：头顶的雪花（被冻住的英雄身上，约 3 秒，循环），4 帧

被寒冰闪耀或成形的风暴冻住的英雄（这时霜寒刺骨伤害翻倍）：头顶浮着一枚冰蓝色的雪花，一亮一暗；身上飘几粒雪星，脚边一圈淡淡的白霜（参考 snowflake、frost_sprites）。**左右对称**，中间身体位置留空（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: an ICED MARK on a champion, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): a six-armed ice-blue snowflake 7 squares wide floating over its head (1 dim, 2 bright, 3 brightest with a white centre, 4 bright), two or three tiny snow sparkles drifting down past the body's sides, a faint white frost ellipse round the feet (14 squares wide, 3 tall).
Layout: one horizontal row of 4 equal 20:44 cells, image size 1280x704 (each cell 320x704, 16 px a square); centered across, the figure's feet on the cell's bottom row, the snowflake's top 1 square under the cell's top. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `anivia_fx_p_egg_in.png`：寒霜涅槃：变成冰蛋的冰爆（她身上，跟随），4 帧

受到致命伤害、缩进冰蛋的一瞬间：一团白光把她整个包住，冰晶从四周往中间合拢，冷气爆开，最后剩一圈霜雾（这团冰爆要盖住「鸟变成蛋」的那一下）（参考 FrostOut、SoftShockwave、snowdust、英雄联盟碎蛋 egg_break）。**左右对称**（a large ice phoenix 61 squares wide and 38 tall hovers in the middle, not drawn，这次**要**盖住她）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: a REBIRTH FLASH: a hovering phoenix turning into an ice egg, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a large ice phoenix 61 squares wide and 38 tall hovers in the middle, not drawn; this one DOES cover her): 1 a big white-cyan flash 40 squares wide covering her body; 2 ice crystals closing in from all sides towards the middle, a white core 30 squares; 3 the crystals meeting low in the middle (where the egg will sit, 27 squares wide and 19 tall on the ground), cold mist bursting out; 4 a ring of frost mist settling round the bottom.
Layout: one horizontal row of 4 equal 64:48 cells, image size 4096x768 (each cell 1024x768, 16 px a square); centered across, the ground on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `anivia_fx_p_hatch.png`：寒霜涅槃：破壳孵化（她身上，跟随），4 帧

冰蛋撑过去、破壳：蛋壳碎片往上、往两边飞，白光一闪，雪星和冷气散开（参考 egg_break、IceShards、snowdust）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, ice glow, snow, frost mist, wind or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ice ramp (#FFFFFF, #E4FBFF, #A6EEFF, #5CCBF5, #2C8FD8, #155AA6) and a snow and frost-mist ramp (#FFFFFF, #EEF8FF, #CDE6FA, #9CC4EA, #6F94C8, #46669E).
Effect: an ICE EGG HATCHING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 14 squares low in the middle (where an egg 27 squares wide and 19 tall sat on the ground); 2 curved shell fragments (pale ice blue with frosty white edges) flying up and out at mirrored places, snow sparkles; 3 the fragments 36 squares apart and falling, cold mist; 4 a few fragments and sparkles on the ground.
Layout: one horizontal row of 4 equal 40:32 cells, image size 2560x512 (each cell 640x512, 16 px a square); centered across, the ground on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `anivia_fx_a_bolt` | view_projectiles `league_anivia_a_bolt`（随飞行方向旋转：画成朝右飞、上下对称） | 12 × 6 |
| `anivia_fx_a_hit` | view_effects `league_anivia_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `anivia_fx_q_ball` | view_projectiles `league_anivia_q_ball`（随飞行方向旋转：画成朝右飞、上下对称） | 18 × 12 |
| `anivia_fx_q_blast` | view_effects `league_anivia_q_blast`（不跟随，画在人物上面；左右对称；大图表） | 40 × 36 |
| `anivia_fx_q_stun` | view_effects `league_anivia_q_stun`（跟随，画在人物上面；左右对称） | 22 × 40 |
| `anivia_fx_w_wall` | view_effects `league_anivia_w_wall`（不跟随，画在人物上面；左右对称；大图表；3–6 帧循环铺满 5 秒） | 20 × 76 |
| `anivia_fx_e_shard` | view_projectiles `league_anivia_e_shard`（随飞行方向旋转：画成朝右飞、上下对称） | 14 × 6 |
| `anivia_fx_e_hit` | view_effects `league_anivia_e_hit`（跟随，画在人物上面；左右对称） | 14 |
| `anivia_fx_e_iced` | view_effects `league_anivia_e_iced`（跟随，画在人物上面；左右对称） | 20 |
| `anivia_fx_r_cast` | view_effects `league_anivia_r_cast`（跟随，画在人物上面；左右对称） | 70 × 52 |
| `anivia_fx_r_storm` | view_effects `league_anivia_r_storm`（不跟随，画在人物下面；左右对称；大图表） | 72 × 48 |
| `anivia_fx_r_formed` | view_effects `league_anivia_r_formed`（不跟随，画在人物下面；左右对称；大图表；3–6 帧循环铺满） | 76 × 52 |
| `anivia_fx_iced` | view_buffs `league_anivia_iced`（跟随，画在人物上面；左右对称；循环） | 20 × 44 |
| `anivia_fx_p_egg_in` | view_effects `league_anivia_p_egg_in`（跟随，画在人物上面；左右对称） | 64 × 48 |
| `anivia_fx_p_hatch` | view_effects `league_anivia_p_hatch`（跟随，画在人物上面；左右对称） | 40 × 32 |

- 两张表：`asset/league/effects/league_anivia_fx`（小的）和 `league_anivia_big`（q_blast、w_wall、r_storm、r_formed），tag = 名字（build_anivia.py 的 views）。
- 飞行物 a_bolt、q_ball、e_shard（连招的 e_combo 用 e_shard 的 tag）随飞行方向旋转，导入时断言上下对称；其余断言左右对称。`q_blast`、`w_wall`、`r_storm`、`r_formed` 不跟随（地上的画面）；`r_storm`、`r_formed` 画在人物下面（z -1）；`w_wall` 第 3–6 帧循环铺满 5 秒（w_t 300 tick），`r_formed` 第 3–6 帧循环铺满 r_t - 3 r_grow = 270 tick；`r_storm` 6 帧铺满 3 r_grow = 90 tick；`q_stun` 铺满 q_stun 66 tick。
- 用 `pixel_1x/` 切格（import_nasus_fx / import_swain_fx 的做法），清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
