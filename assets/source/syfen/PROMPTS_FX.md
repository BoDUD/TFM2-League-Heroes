# 赛芬：给 Codex 的特效提示词（第 3 步）

> **这一份是 12 张特效图 + 3 个技能图标。** 造型已定（`design/syfen_design.png`：侧身朝右、弓着身子直立的幽影飞龙：灰白皮肤、深青黑的横肋甲、宝蓝到紫色的背甲；品红头甲、蓝紫长嘴、白牙、两根暗红弯角、粉紫色发光的眼睛；两条浅灰长前臂就是翅膀（紫到品红的翼膜、钢蓝利爪）；长尾巴，尾尖一把钢灰弯刀刃）。赛芬在游戏里是**高清**的（每个游戏格子里约 2.52×2.52 个细像素），40 格高、52 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/syfen_size.png`：赛芬缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里赛芬自己的特效贴图（打中的光、暴走的音波和警示圈、冲锋的拖尾、大爆炸、幽影龙的烟）（**灰色的形状，游戏里再染色**），按用在我们哪张特效分好了行。只在本地用。
> - **赛芬是幽影龙，特效都是幽影的力量**：粉白芯的紫色 / 品红烟丝和光、锐利的月牙斩痕、钢蓝色的爪尖闪光、冲锋时灰褐色的尘土；不要火、不要绿色、不要光滑的霓虹光束。
> - **特效要亮**：每个光都有最亮一档或粉白色的芯，暗底上一眼能看见。**光、烟、冲击波、尘土没有黑描边**。
> - **围着人的画面只画头上、脚下、身体两侧边缘，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `syfen_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入）；图标交付 `syfen_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/syfen_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/syfen_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻「翼爪连击」 | 翼爪抓一下、甩尾抽一下，交替 | `a_hit` |
| 被动「幽影低语」 | 他的伤害让敌人缩小几秒（护甲、魔抗降低）；打缩小的敌人越打越强 | `p` · `p_shrink` · `p_rage` |
| 技能 1 =「噬咬」 | 扑上去狠咬一口，无视一部分护甲，回一点血 | `q_bite` |
| 技能 2 =「翼刃横扫」 | 张开翅膀往前合拢扫一大片，扫中的减速 | `e_sweep` · `e_hit` · `e_slow` |
| 大招 =「暴走」 | 龙吼，冲向最远的敌人，路上撞到的全部晕眩，冲到后再狠咬一口 | `r` · `r_dash` · `r_hit` · `r_bite` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 紫 / 品红（他的翼膜和头甲）：`#FFF0FF`、`#F7A8F5`、`#E040D8`、`#9A1FB8`、`#4E0F7A`；
  - 蓝紫（他的口鼻和背甲）：`#E6EEFF`、`#8FA8FF`、`#4F5BEA`、`#2A2A9A`；
  - 钢蓝（利爪、尾刃）：`#F2F4FA`、`#B8C2D8`、`#7E8AA8`、`#4A5270`；
  - 尘土：`#E3DCCB`、`#B0A690`、`#7A705C`、`#4A4336`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `syfen_fx_a_hit.png`：普攻：爪痕，4 帧

翼爪 / 甩尾打中：两组交叉成 X 的品红爪痕（每组三条平行的细爪痕），中间一下粉白光，几缕紫色烟丝散开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A), a steel ramp (#F2F4FA, #B8C2D8, #7E8AA8, #4A5270).
Effect: A CLAW HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 4 squares across; 2 two sets of three thin parallel magenta claw marks crossing in an X, 14 squares across, white-pink along their middles, a steel-blue glint at each end; 3 the marks fading from their ends, small violet wisps curling out symmetrically; 4 a few fading wisps. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `syfen_fx_q_bite.png`：噬咬：一口咬下，5 帧

咬中：上下两排**粉白色的獠牙虚影**从上下合拢咬在一起（像一张发光的龙嘴咬下去），合拢的一下品红光爆开，几滴紫色的光点往两边溅出。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A), a steel ramp (#F2F4FA, #B8C2D8, #7E8AA8, #4A5270).
Effect: A BITE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two glowing jaw outlines open wide, an upper row of 5 white-pink fangs pointing down at the top and a lower row of 5 pointing up at the bottom, 18 squares wide; 2 the jaws snapping half shut; 3 the fangs meeting in the middle with a bright magenta burst 12 squares across; 4 violet droplets of light splashing out to both sides (mirrored), the fangs fading; 5 a few fading sparks. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `syfen_fx_e_sweep.png`：翼刃横扫：两侧的翼刃弧光，6 帧

他张开翅膀往前合拢扫过：身体**两侧**各一道很大的品红月牙弧光（翼膜扫过的轨迹），从后上方往前下方扫过去，弧光边缘一排钢蓝色的爪尖闪光，弧光后面拖着紫色的烟。**身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A), a steel ramp (#F2F4FA, #B8C2D8, #7E8AA8, #4A5270).
Effect: A DOUBLE WING SWEEP, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the wyvern stands in the middle, not drawn: 52 squares wide and 40 tall, hunched, his head at the top right: 1 two thin violet arcs appearing high on BOTH sides of him (mirrored); 2-3 each arc swelling into a big magenta crescent blade sweeping down and inward, 20 squares long, white-pink along its leading edge, a row of steel-blue talon glints on its rim; 4 the two crescents meeting low in front of and behind his feet; 5 the crescents breaking into trailing violet smoke; 6 a few wisps. The middle of the cell (his body) stays EMPTY. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 64:36 cells, image size 6144x576 (each cell 1024x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `syfen_fx_e_hit.png`：翼刃横扫：被扫中，4 帧

被翼刃扫中：一道横着的品红斩痕，中间一下白光，两边几缕紫烟。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A).
Effect: A WING SLASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 4 squares across; 2 one HORIZONTAL magenta slash 12 squares long through the middle, white-pink along its centre; 3 the slash splitting into small violet wisps curling out to both sides; 4 fading wisps. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `syfen_fx_e_slow.png`：翼刃横扫：减速，6 帧循环

被减速：脚下一圈紫色的烟雾缠着脚（从斜上方看的椭圆，宽是高的 3 倍），几缕烟丝像手一样往上抓。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A).
Effect: A CLINGING SHADOW SNARE, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND round the unit's feet, an ellipse seen from above, about 18 squares wide and 6 tall, of violet-purple smoke; a few thin wisps reaching up like small claws and sinking back; frames 1-6 the wisps rising and falling (keep every frame left-right symmetric). Nothing above the feet. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 20:8 cells, image size 1920x128 (each cell 320x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `syfen_fx_r.png`：暴走（开启）：龙吼音波，6 帧

他挺身咆哮的一下：从他身上往外**一圈圈扩散的品红音波环**（从斜上方看的椭圆，一圈比一圈大），脚下一圈紫色的警示光圈亮起，两侧几缕紫烟被吹开。**身体位置留空**（只画外面的环、脚下和两侧）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A), a blue-violet ramp (#E6EEFF, #8FA8FF, #4F5BEA, #2A2A9A).
Effect: A ROAR OF SOUND WAVES, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the wyvern stands in the middle, not drawn: 52 squares wide and 40 tall, hunched, his head at the top right: 1 a violet warning ring flashing on the ground under his feet (an ellipse 40 squares wide, 11 tall); 2-4 three concentric magenta SOUND-WAVE RINGS (ellipses, each 2 squares thick, white-pink on their front edge, blue-violet behind) bursting outward from him one after another, the outer one reaching the cell edge; violet smoke blown out to both sides; 5 the rings thinning; 6 the last ring fading. The middle of the cell (his body) stays EMPTY. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:48 cells, image size 5376x768 (each cell 896x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `syfen_fx_r_dash.png`：暴走冲锋：起步的尘土，4 帧

他蹬地冲出去的一下：脚下的地面爆起一圈灰褐色的尘土和紫色的烟，往两边散开。**只在地面上**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dust ramp (#E3DCCB, #B0A690, #7A705C, #4A4336), a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A).
Effect: A CHARGE KICK-OFF, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND only (the bottom of the cell), an ellipse about 30 squares wide and 8 tall: 1 a small violet flash at the middle; 2 chunky grey-brown dust puffs and violet smoke bursting out to both sides (mirrored), up to 8 squares high; 3 the puffs spreading wider; 4 the dust settling. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 4 equal 32:12 cells, image size 2048x192 (each cell 512x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `syfen_fx_r_hit.png`：暴走冲锋：被撞晕，5 帧

被冲锋撞到：一下很亮的品红撞击闪光，一圈冲击环，几颗紫色的星星在头上绕（晕眩）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A), a blue-violet ramp (#E6EEFF, #8FA8FF, #4F5BEA, #2A2A9A).
Effect: A RAMMED-AND-STUNNED IMPACT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a big white-pink flash 8 squares across in the middle; 2 a thick magenta shock ring bursting out to 18 squares, violet shards flying out in a symmetric star; 3 the ring thinning; 4-5 three small violet stars circling in the top of the cell (a stun), the ring gone. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `syfen_fx_r_bite.png`：暴走猛咬：大咬，6 帧

暴走最后的一口：一张很大的**紫色幽影龙嘴虚影**（上下两排粉白獠牙）从上下猛地合拢咬住目标，咬合的一下品红光大爆炸，紫色的烟和光点往四周炸开。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A), a blue-violet ramp (#E6EEFF, #8FA8FF, #4F5BEA, #2A2A9A), a steel ramp (#F2F4FA, #B8C2D8, #7E8AA8, #4A5270).
Effect: A GREAT SHADOW BITE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a huge ghostly violet dragon's jaw outline opening wide around the middle, 30 squares wide, an upper row of 6 big white-pink fangs at the top and a lower row of 6 at the bottom; 2 the jaws slamming half shut; 3 the fangs meeting with a big magenta explosion 20 squares across, a white-pink core; 4 violet smoke and sparks bursting out in a symmetric star; 5-6 the smoke fading. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal square cells, image size 3072x512 (each cell 512x512, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `syfen_fx_p.png`：被动「幽影低语」：缩小，5 帧

敌人被缩小的一下：一圈紫色的低语烟丝从外往里**螺旋着收紧**到目标身上，几个往下的小箭头形光点，最后一下轻轻的粉光。**身体位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A).
Effect: A SHRINKING WHISPER, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round a unit 14 squares wide and 20 tall in the middle (not drawn): 1 a ring of thin violet whisper wisps appearing at the cell edge; 2-3 the wisps spiralling INWARD and down toward the unit (mirrored), small downward-pointing chevrons of pink light on both sides; 4 the wisps tight round the unit's middle, a soft pink flash; 5 fading wisps. The middle of the cell stays EMPTY. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 5 equal 20:24 cells, image size 1600x384 (each cell 320x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `syfen_fx_p_shrink.png`：被动「幽影低语」：缩小中，6 帧循环

被缩小的人脚下：一个淡紫色的旋涡印记（从斜上方看的椭圆）慢慢转，几缕细烟往上飘一点。**左右对称**，6 帧循环（和减速的烟不一样：这是一个转动的符印）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A).
Effect: A WHISPER SIGIL, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): on the GROUND round the unit's feet, an ellipse seen from above, about 16 squares wide and 6 tall: a thin violet ring with a small swirl sigil inside, its marks seeming to turn (keep every frame left-right symmetric), two or three thin wisps rising 2-3 squares and fading. Nothing above the feet. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 18:8 cells, image size 1728x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `syfen_fx_p_rage.png`：被动「幽影低语」：越打越强，6 帧循环

他叠起力量时：身体**两侧**和两只利爪附近飘着紫色的火焰状烟丝，往上卷，脚下一圈淡淡的品红光。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFF0FF, #F7A8F5, #E040D8, #9A1FB8, #4E0F7A), a blue-violet ramp (#E6EEFF, #8FA8FF, #4F5BEA, #2A2A9A).
Effect: A SHADOW FURY AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): round the wyvern stands in the middle, not drawn: 52 squares wide and 40 tall, hunched, his head at the top right: flame-like violet-magenta wisps curling upward along BOTH sides of him (mirrored) and at the outer edges low down where his talons are, white-pink tips on the brightest wisps; a faint magenta ring on the ground under him (an ellipse 40 squares wide, 10 tall); frames 1-6 the wisps flickering upward (every frame left-right symmetric). The middle of the cell (his body) stays EMPTY. everything is a SHADOW WYVERN's power: whispering violet-magenta wisps and smoke with a white-pink core, sharp crescent slashes, steel-blue talon glints, chunky grey-brown dust where he charges; flat shades, crisp shapes; no fire, no green, no smooth neon beams.
Layout: one horizontal row of 6 equal 56:44 cells, image size 5376x704 (each cell 896x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `syfen_icon_skill.png`：技能 1「噬咬」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a wyvern's long blue-violet snout with a magenta head plate seen from the side, its jaws snapping shut on a glowing magenta bite flash, rows of white fangs. No text, no letters.
```

### 图标 2. `syfen_icon_skill2.png`：技能 2「翼刃横扫」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a purple-to-magenta bat-like wing with steel-blue talons sweeping across, a big magenta crescent arc trailing behind it. No text, no letters.
```

### 图标 3. `syfen_icon_ult.png`：大招「暴走」图标

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark violet frame with little magenta corners, a deep purple-black inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: the head of a shadow wyvern (a magenta head plate, two curved dark crimson horns, a glowing pink eye, open jaws with white fangs) charging to the right, violet speed streaks and smoke behind it. No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `syfen_fx_a_hit` | view_effects `tft_syfen_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `syfen_fx_q_bite` | view_effects `tft_syfen_q_bite`（跟随目标，z 3；左右对称） | 20 × 20 |
| `syfen_fx_e_sweep` | view_effects `tft_syfen_e_sweep`（大表，跟随他，z 4；左右对称） | 64 × 36 |
| `syfen_fx_e_hit` | view_effects `tft_syfen_e_hit`（跟随被打中的人，z 2；左右对称） | 14 × 14 |
| `syfen_fx_e_slow` | view_buffs `tft_syfen_e_slow`（跟随被减速的人，脚下地面，z 3；左右对称） | 20 × 8 |
| `syfen_fx_r` | view_effects `tft_syfen_r`（大表，跟随他，z 4；左右对称） | 56 × 48 |
| `syfen_fx_r_dash` | view_effects `tft_syfen_r_dash`（冲锋开始时在他脚下的地面上，不跟随，z 1；左右对称） | 32 × 12 |
| `syfen_fx_r_hit` | view_effects `tft_syfen_r_hit`（跟随被撞到的人，z 3；左右对称） | 20 × 20 |
| `syfen_fx_r_bite` | view_effects `tft_syfen_r_bite`（大表，跟随目标，z 4；左右对称） | 32 × 32 |
| `syfen_fx_p` | view_effects `tft_syfen_p`（跟随被缩小的人，z 3；左右对称） | 20 × 24 |
| `syfen_fx_p_shrink` | view_buffs `tft_syfen_p_shrink`（跟随被缩小的人，脚下地面，z 3；左右对称） | 18 × 8 |
| `syfen_fx_p_rage` | view_buffs `tft_syfen_p_rage`（大表，跟随他，z 3；左右对称） | 56 × 44 |
| `syfen_icon_skill` | skill_icons[0] `asset/tft/icons/tft_syfen_skill` | 64 × 64 |
| `syfen_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_syfen_skill2` | 64 × 64 |
| `syfen_icon_ult` | skill_icons[2] `asset/tft/icons/tft_syfen_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_syfen_fx`（小的）和 `tft_syfen_big`（e_sweep、r、r_bite、p_rage），tag = 名字。
- 全部断言左右对称。
- e_sweep、r 是他身上的一下（跟随他，z 4）；p_rage 是他身上的 caster buff（z 3）；r_dash 放在冲锋起点的地面上（不跟随）；p_shrink、e_slow 是敌人身上的 buff（脚下，z 3）；q_bite、r_bite、r_hit、p 打在目标身上。
- 用 `pixel_1x/` 切格（import_nomsy_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
