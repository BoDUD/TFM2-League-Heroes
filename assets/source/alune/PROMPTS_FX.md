# 拉露恩：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图 + 3 个技能图标。** 造型已定（`design/alune_design.png`：侧坐在青铜月牙法杖上漂浮的月之女祭司，银白短发、月牙角饰、额头月珠，紫色长袍）。拉露恩在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），45 格高、30 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/alune_size.png`：拉露恩缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里拉露恩自己的特效贴图（**灰色的形状，游戏里再染色**：月缘光、月亮符号、星芒、碎片），按用在我们哪张特效分好了行；`refs/video_moonfall.jpg` 是金铲铲第 18 赛季对局里三星拉露恩的**月曜降临**（一轮巨大的淡蓝白满月压在棋盘上）。只在本地用。
> - **拉露恩是月之教派的女祭司，特效都是冷色的月光**：白、冰蓝、淡紫的月光，月牙和圆月的形状，柔和的漩涡环形山，四角小星芒，衬着她长袍的深紫夜色；不要光滑的霓虹光束，不要火和烟。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、月亮、碎片没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：除了弹道，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道 `a_ring` 朝右画、尾巴在左边，严格上下对称**（游戏按方向转这张图）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `alune_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、按上面的要求逐格对称——Claude 直接用这一份切格导入）；图标交付 `alune_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/alune_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/alune_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「月相」 | 每放一次技能，她头顶的月亮长一档（新月 → 半月 → 满月），大招砸得越狠，砸完月亮回到新月 | `p_moon` |
| 普攻 | 把螺旋月环像飞盘一样甩出去（装了附加包还会飞回来，回程也打人） | `a_ring` · `a_hit` |
| 技能 1 =「月之降临」 | 月光碎片从天上落到 3 个敌人身上（附加包：最近的 3 个），魔法伤害、降魔抗 | `q_drop` · `q_hit` · `q_shred` |
| 技能 2 =「月华」 | 她和身边的队友攻速提高 | `e_glow` |
| 大招 =「月曜降临」 | 敌人脚下出现月影，一轮满月砸下来：伤害（附加包：命中的敌人分摊，人越少越痛）、中心眩晕 | `r_warn` · `r_moon` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、月亮、碎片没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **都是冷色的月光**：每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 月光：`#FFFFFF`、`#EAF6FF`、`#BFE4FF`、`#8CC8FF`、`#5C9CF0`；
  - 淡紫：`#F2E8FF`、`#CDB8FF`、`#9E86F0`、`#6E5AD0`；
  - 夜色：`#5A3CC8`、`#3A2490`、`#241560`、`#140A36`；
  - 青色流光：`#E6FFFF`、`#8FF0F8`、`#44D0E8`、`#1E90B8`；
  - 青铜（图标边框）：`#FFE9A8`、`#E2B85A`、`#B08530`、`#7A5418`、`#42280A`；
- 打中、爆发居中画，不旋转；地面上的圈（预警圈、冲击圈）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `alune_fx_a_ring.png`：普攻：飞出去的螺旋月环，4 帧循环

她甩出去的**螺旋月环**（就是法杖中间那个环，平着飞像飞盘）：侧面看是一个扁扁的亮蓝色椭圆环，中间一颗淡蓝的小月球，环边一圈青色的流光，后面拖两三粒白色星屑。**朝右飞，上下对称**，4 帧循环（环在转：亮的地方绕一圈）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a cyan swirl ramp (#E6FFFF, #8FF0F8, #44D0E8, #1E90B8).
Effect: A SPINNING MOON RING, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a flat bright blue ring seen nearly edge-on (an ellipse 12 squares wide and 5 tall) with a pale blue moon orb 3 squares across in its middle and a white glint, a thin cyan streak trailing 3 squares behind it with two white star flecks; frames 1-4 the bright part of the ring running round it (spinning). everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 4 equal 14:8 cells, image size 896x128 (each cell 224x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `alune_fx_a_hit.png`：普攻：打中，3 帧

月环打中：一下冷白的闪光，一圈细细的月牙形光弧向外一扩，几颗小星芒。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0).
Effect: A MOONLIGHT HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash 6 squares across; 2 two thin mirrored crescent arcs of ice-blue light 12 across opening outwards, four small four-point white star glints at mirrored places; 3 the arcs fading, the glints smaller and further out. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `alune_fx_q_drop.png`：月之降临：月光碎片从天上落下，6 帧

一枚**月光碎片**从天上直直落下来：一片竖着的冰蓝色水晶月牙碎片（尖朝下，左右对称），后面拖一道淡紫白的长光尾，四周两三颗星芒；最后一帧碎片到达格子底部往上 4 格（地面，砸开的是另一张 `q_hit`）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0), a cyan swirl ramp (#E6FFFF, #8FF0F8, #44D0E8, #1E90B8).
Effect: A FALLING MOONSHARD, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a long narrow crystal shard of moonlight, pointed at the BOTTOM (a diamond 5 squares wide and 10 tall, white core, ice blue edges, a cyan rim), with a pale lavender-white light trail 3 squares wide stretching up behind it; 1 the shard appearing at the very top of the cell with a little white glint; 2-5 the shard falling straight down the middle, the trail growing longer behind it (up to 30 squares), two four-point star glints at mirrored places; 6 the shard's tip touching the ground line 4 squares above the bottom, the trail thinning. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 6 equal 16:56 cells, image size 1536x896 (each cell 256x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `alune_fx_q_hit.png`：月之降临：碎片砸地，5 帧

月光碎片砸到地上：碎片炸成冰蓝的水晶碎屑往两边溅，地上一圈白蓝的月光冲击圈（从斜上方看的椭圆），几颗星芒往上飘（被砸的人魔抗下降）。砸的地方在格子底部往上 4 格。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a cyan swirl ramp (#E6FFFF, #8FF0F8, #44D0E8, #1E90B8), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0).
Effect: A MOONSHARD IMPACT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the impact sits on the ground line 4 squares above the bottom. 1 a white-blue flash 8 squares across; 2 crystal splinters of ice blue flying out to both sides (mirrored), a white ring on the ground 16 wide and 5 tall; 3 the ring 26 wide and 8 tall, splinters higher and further out, small star glints rising; 4 the ring fading, splinters falling; 5 a few fading glints. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 5 equal 30:22 cells, image size 2400x352 (each cell 480x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `alune_fx_q_shred.png`：月之降临：月蚀印记（魔抗降低），6 帧循环

被月光碎片砸过的人魔抗降低：**头顶上方一个小小的暗紫色月蚀标记**（一个被黑影咬掉一块的月亮，边缘一圈冷白的光），慢慢一明一暗，身边两三颗小小的淡紫光点往下落。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet night ramp (#5A3CC8, #3A2490, #241560, #140A36), a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0).
Effect: AN ECLIPSE MARK, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: over the unit's head (the top 8 squares of the cell) a small ECLIPSED MOON 6 squares across - a dark violet disc with a thin cold white rim of light, a darker bite across it, seen from the front; two or three tiny pale lavender motes drifting down at mirrored places beside the body; frames 1-6 the rim brightening and dimming slowly, the motes falling. The middle (the body) left empty. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 6 equal 16:44 cells, image size 1536x704 (each cell 256x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `alune_fx_e_glow.png`：月华：攻速加成，6 帧循环

月华加速：人脚下一圈淡淡的**月光圆环**（从斜上方看的椭圆），身体两边各一道细细的冰蓝色月光流往上飘，几颗星芒一闪一闪。**身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0), a cyan swirl ramp (#E6FFFF, #8FF0F8, #44D0E8, #1E90B8).
Effect: A MOONLIGHT BLESSING, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: a faint ring of moonlight on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 22 squares wide and 7 tall, two thin ribbons of ice-blue light rising on both sides of the body (mirrored) up to its shoulders, three four-point white star glints; frames 1-6 the ribbons flowing upward and the glints winking in turn. The middle (the body) left empty. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 6 equal 26:42 cells, image size 2496x672 (each cell 416x672, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `alune_fx_p_moon.png`：月相：头顶的月亮，3 格（上弦 / 半月 / 满月）

被动月相：她头顶上方的小月亮，**一张图三格**，每格一个月相：1 一弯细细的新月（月牙口朝上，左右对称）；2 半个月亮（上半亮、下半暗，左右对称）；3 满月（圆圆的、淡蓝白、有两三块浅色的漩涡环形山，一圈冷光）。每个都在格子正中、约 8 格大、带一点点星芒。**每格都左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0), a violet night ramp (#5A3CC8, #3A2490, #241560, #140A36).
Effect: THREE MOON PHASES, 3 cells (each its own picture, not an animation), each SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small moon 8 squares across in the middle of its cell with a soft cold rim; 1 a thin CRESCENT with its horns pointing UP (a smile shape), the rest of the disc a faint dark violet; 2 a HALF moon, the TOP half lit white-blue, the bottom half dark violet; 3 a FULL moon, pale blue-white with two or three soft swirl craters and a white glint, a faint lavender glow ring. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `alune_fx_r_warn.png`：月曜降临：地上的预警圈，6 帧

满月要砸下来的地方：地上一圈越来越亮的**冷白月光圈**（从斜上方看的椭圆），圈里一片淡淡的月影慢慢变大（满月越来越近），圈边一圈细细的月牙形花纹。最大 **横 54 格、纵 18 格**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0), a violet night ramp (#5A3CC8, #3A2490, #241560, #140A36).
Effect: A MOON'S SHADOW, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall): 1 a thin cold white ring 20 squares wide; 2 the ring 36 wide, a faint dark violet shadow inside it; 3 the ring 54 wide and 18 tall with small crescent marks around its edge, the violet shadow filling it; 4-6 the ring brightening, the shadow darkening, little white motes rising from the edge. Flat colours, crisp pixel shapes. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 6 equal 60:22 cells, image size 5760x352 (each cell 960x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `alune_fx_r_moon.png`：月曜降临：满月砸下来，10 帧

大招：**一轮巨大的满月**从天上压下来（看附图 `video_moonfall.jpg`：金铲铲里三星拉露恩的月曜降临——淡蓝白、带漩涡环形山的大圆月，外圈一层冷光），四周飞着深紫色的碎片；月亮砸到地上一下白光，炸出一圈月光冲击波和冰蓝碎屑，最后月光消散。砸的地方在格子底部往上 8 格。**左右对称**，10 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0), a violet night ramp (#5A3CC8, #3A2490, #241560, #140A36), a cyan swirl ramp (#E6FFFF, #8FF0F8, #44D0E8, #1E90B8).
Effect: THE MOON FALLS, 10 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 the bottom edge of a HUGE FULL MOON appearing at the top of the cell (a pale blue-white disc 56 squares across with soft swirling craters and a cold white rim, a faint lavender halo); 2-4 the moon coming straight down, more of it showing, dark violet shards flying at mirrored places around it; 5 the moon's bottom touching the ground line 8 squares above the bottom, a white flash 40 wide; 6 the moon crumbling into light, a white-blue shockwave ellipse 64 wide and 16 tall on the ground, ice blue splinters thrown up to both sides; 7 the shockwave at its widest (70), splinters falling; 8-9 the light fading, a few violet shards and white glints; 10 the last glints. Frames 2-6 MUST fill 56 squares across. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 10 equal 72:90 cells, image size 11520x1440 (each cell 1152x1440, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `alune_fx_r_hit.png`：月曜降临：被砸中，4 帧

被满月砸中：一下冷白的闪光，几片冰蓝月光碎屑和星芒往外飞（被砸晕的人）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0).
Effect: A MOONLIGHT BLOW, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash 8 squares across; 2 ice blue splinters and white four-point glints 14 across flying out at mirrored places; 3 further out, smaller; 4 fading glints. everything is a MOON PRIESTESS'S lunar magic: cold MOONLIGHT (white, ice blue, pale lavender), crescent shapes, round moons with soft swirling craters, little four-point star glints, against the deep violet night of her robe; flat shades, crisp shapes; no smooth neon beams, no fire, no smoke.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `alune_icon_skill.png`：技能 1「月之降临」图标

三枚冰蓝的月光碎片（尖朝下）从上方斜斜落下，下面一小弯新月。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRONZE frame with little crescent corners, a deep violet-navy night inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: THREE ice-blue crystal MOONSHARDS (pointed at the bottom, white cores) falling slantwise from the upper left with short pale trails, over a small thin crescent moon low in the tile. Colours: a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a violet night ramp (#5A3CC8, #3A2490, #241560, #140A36), a bronze ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A). No text, no letters.
```

### 图标 2. `alune_icon_skill2.png`：技能 2「月华」图标

一只张开的手掌朝上，掌心上方一弯发光的月牙，四周几道往上飘的月光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRONZE frame with little crescent corners, a deep violet-navy night inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: an OPEN PALE HAND seen from the front, palm up, a glowing white-blue CRESCENT floating over the palm, thin ribbons of moonlight rising around it, two star glints. Colours: a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0), a violet night ramp (#5A3CC8, #3A2490, #241560, #140A36), a bronze ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A). No text, no letters.
```

### 图标 3. `alune_icon_ult.png`：大招「月曜降临」图标

一轮巨大的满月压下来，占满大半个图标，下面一圈冲击波。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square BRONZE frame with little crescent corners, a deep violet-navy night inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a HUGE FULL MOON (pale blue-white with soft swirl craters and a cold rim) pressing down from the top, filling most of the tile, a white shockwave arc below it, dark violet shards at both sides. Colours: a moonlight ramp (#FFFFFF, #EAF6FF, #BFE4FF, #8CC8FF, #5C9CF0), a pale lavender ramp (#F2E8FF, #CDB8FF, #9E86F0, #6E5AD0), a violet night ramp (#5A3CC8, #3A2490, #241560, #140A36), a bronze ramp (#FFE9A8, #E2B85A, #B08530, #7A5418, #42280A). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `alune_fx_a_ring` | view_projectiles `tft_alune_a_ring`（弹道，z 2；朝右、上下对称；附加包的回程 a_back 也用它） | 14 × 8 |
| `alune_fx_a_hit` | view_effects `tft_alune_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `alune_fx_q_drop` | view_effects `tft_alune_q_drop`（大表，碎片落点，z 3，不跟随；左右对称） | 16 × 56 |
| `alune_fx_q_hit` | view_effects `tft_alune_q_hit`（碎片落点，z 2，不跟随；左右对称） | 30 × 22 |
| `alune_fx_q_shred` | view_buffs `tft_alune_q_shred`（跟随目标，z 3；左右对称） | 16 × 44 |
| `alune_fx_e_glow` | view_buffs `tft_alune_e_glow`（跟随每个加速的队友和她自己，z 3；左右对称） | 26 × 42 |
| `alune_fx_p_moon` | view_buffs `tft_alune_ph1` / `_ph2` / `_ph3`（跟随她，z 4；每格一个 tag：p_moon1 / p_moon2 / p_moon3；左右对称） | 12 × 12（每格） |
| `alune_fx_r_warn` | view_effects `tft_alune_r_warn`（大表，落点，地面，z -2，不跟随；左右对称） | 60 × 22 |
| `alune_fx_r_moon` | view_effects `tft_alune_r_moon`（大表，落点，z 3，不跟随；左右对称） | 72 × 90 |
| `alune_fx_r_hit` | view_effects `tft_alune_r_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `alune_icon_skill` | skill_icons[0] `asset/tft/icons/tft_alune_skill` | 64 × 64 |
| `alune_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_alune_skill2` | 64 × 64 |
| `alune_icon_ult` | skill_icons[2] `asset/tft/icons/tft_alune_ult` | 64 × 64 |

- 两张表：`asset/tft/effects/tft_alune_fx`（小的）和 `tft_alune_big`（q_drop、r_warn、r_moon），tag = 名字；p_moon 的三格拆成 p_moon1 / p_moon2 / p_moon3 三个 tag（build_alune.py 的 views：ph1-3 → p_moon1-3，a_back → a_ring）。
- 弹道（a_ring）断言上下对称；其余断言左右对称。
- r_warn 在 R 的月亮飞行的 r_open 帧里一直显示（拉长到那么长）；q_drop 在碎片的 q_fall 帧里放完。
- 用 `pixel_1x/` 切格（import_locke_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
