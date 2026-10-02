# 诡术妖姬 乐芙兰：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型已定（`design/leblanc_design.png`，8 倍，你画的版本 B，裁到 43 格）。
> - 大小对照 `design/leblanc_size.png`：定稿造型放大 4 倍，脚在红色脚底线上，上面是 10 格一段的刻度，右边是原版火法师。乐芙兰 32×43 格（含法杖），原版英雄约 31–36 格高。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里乐芙兰自己的特效贴图（多数是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（Q 的眼形魔印和符文圈、E 的光链、W 的魔法阵和玻璃碎片、法球和命中），只在本地用，不要提交。颜色按下面写的色阶。
> - 特效照下面第 1–19 条和「所有特效图的规则」画，每张一个 PNG，文件名 `leblanc_fx_<名字>.png`，排版按每条写的来。
> - **大招「故技重施」的强化版（`rq_*`、`re_*`、`rw_*`）和被动的分身不用画**：Claude 导入时用这些基础特效调亮、放大做出来，分身用她的待机精灵染色做。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、画了几帧、有没有没做到的地方）。最好打成一个 zip（`leblanc_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「镜花水月」 | 法杖射出法球；被两个以上敌方英雄围住时隐身、往后跳开、原地留一个分身 | `leblanc_fx_a_orb` · `leblanc_fx_a_cast` · `leblanc_fx_a_hit`（分身导入时做） |
| 技能 1 = Q「恶意魔印」 | 掷出魔印打中目标，留下 3.5 秒印记；她的下一个技能打中就引爆再伤一次 | `leblanc_fx_q_orb` · `leblanc_fx_q_cast` · `leblanc_fx_q_hit` · `leblanc_fx_q_mark` · `leblanc_fx_q_pop` |
| 技能 2 = W「魔影迷踪」 | 冲向目标、落地爆炸；起点留一个魔法阵，1.25 秒后闪回 | `leblanc_fx_w_pad` · `leblanc_fx_w_trail` · `leblanc_fx_w_blast` · `leblanc_fx_w_hit` · `leblanc_fx_w_out` · `leblanc_fx_w_in` |
| 普攻里的 E「幻影锁链」 | 每 10 秒对英雄甩出锁链，拴住 1.5 秒，没挣脱就定身 | `leblanc_fx_e_chain` · `leblanc_fx_e_tether` · `leblanc_fx_e_cast` · `leblanc_fx_e_hit` · `leblanc_fx_e_root` |
| 大招 = R「故技重施」 | 重放上一个技能（伤害约两倍） | 导入时由上面的特效调亮放大 |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、玻璃碎片、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮、看得清**：游戏地面偏暗，特效小，所以每个特效都要有白粉色的亮芯和明亮的洋红，暗紫只用在边缘和消散的时候。
- 颜色（按每条写的用）：
  - 洋红魔法（她的主色）：`#FFF2FC`、`#FFA8EE`、`#E651D3`、`#A42BB5`、`#5C1A74`；
  - 镜面玻璃的亮光（碎片的高光）：`#FFFFFF`、`#ECE6FF`、`#B8A8F2`；
  - 金色（她的头冠、法杖，少量点缀）：`#FFF4C8`、`#F9CF6E`、`#D9963A`；
  - 深红（魔印的瞳孔）：`#FF9AB0`、`#E8264B`、`#9B1032`。
- **飞行类特效朝右画，而且上下对称**（法球、魔印、链头、链环）：游戏会把它转到飞行方向。链环 `e_tether` 一节一节首尾相接，左右两端要能接上。
- 命中、爆炸、魔法阵居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在角色身上的特效（拖尾、定身）：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `leblanc_fx_a_orb.png`：普攻法球（飞行中循环），4 帧

法杖水晶射出的一颗小魔法球：洋红色的光球（白粉色的芯），后面拖一小段闪光尾巴，朝右飞。上下对称。约 10 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a SMALL MAGIC ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a round magenta orb with a white-pink core at the front (right), a short tail of 2-3 magenta sparkles behind it (to the left) that flicker from frame to frame; the orb pulses slightly.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the orb on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `leblanc_fx_a_cast.png`：普攻出手：水晶上的闪光，4 帧

法杖水晶放出法球的一瞬：一小团洋红色的闪光，四个尖角向外一闪就收（参考 Flare、Petal）。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a SMALL CAST FLASH, 4 frames: 1 a tiny white-pink point; 2 a four-pointed magenta star flash with a white core; 3 the star at full size with 3-4 tiny sparkles around it; 4 the sparkles fade.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `leblanc_fx_a_hit.png`：普攻命中，4 帧

法球打中：一团洋红色的小爆闪，几点碎光向外飞（参考 ImpactSpike）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a SMALL MAGIC IMPACT, 4 frames: 1 a white-pink flash at the center; 2 a round magenta burst with a white core and 4-5 short spikes; 3 the spikes break into small sparkles flying outward; 4 a few fading violet specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `leblanc_fx_q_orb.png`：Q 恶意魔印：飞出去的魔印（飞行中循环），4 帧

掷出的恶意魔印：一枚发光的洋红色眼形符文（像一只张开的眼睛：中间一颗深红的瞳，外面一圈弯钩形的符文尖角，参考 Base_VFX_Icon01/02），在空中转着往右飞，后面拖一条洋红的光尾。上下对称。约 16 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with crimson (#FF9AB0, #E8264B, #9B1032) and glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a FLYING SIGIL moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a glowing magenta EYE-SHAPED RUNE - an almond eye outline of magenta light with a crimson pupil in its middle and small hooked rune points around it - that pulses and turns slightly each frame; behind it (to the left) a tapering magenta light trail with a few sparkles.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the sigil on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `leblanc_fx_q_cast.png`：Q 出手：魔印在水晶上成形，4 帧

魔印在法杖水晶前成形：一圈洋红色的符文光圈一亮，中间出现眼形魔印，然后飞走（只画成形和闪光，不画飞出去的魔印）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with crimson (#FF9AB0, #E8264B, #9B1032).
Effect: a SIGIL FORMING, 4 frames: 1 a small ring of magenta rune light appears; 2 the ring brightens and an eye-shaped rune with a crimson pupil glows in its middle; 3 a bright white-pink flash as the rune is thrown; 4 the ring breaks into fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `leblanc_fx_q_hit.png`：Q 魔印打中，5 帧

魔印打中目标：一下白粉色的闪光，眼形魔印拍在目标身上亮起，碎光向外溅（参考 Q_Mark_Mult）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with crimson (#FF9AB0, #E8264B, #9B1032) and glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a SIGIL STRIKE, 5 frames: 1 a white-pink flash at the center; 2 the eye-shaped magenta rune slams in, bright, its crimson pupil glowing, a ring of light around it; 3 the rune at full brightness, 5-6 magenta sparks flying out; 4 the ring widens and thins, the sparks fly further; 5 the rune dims, a few violet specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `leblanc_fx_q_mark.png`：Q 魔印印记：留在目标身上的魔印（每 0.2 秒重播一次，要能无缝循环），4 帧

被打中的目标身上留着魔印（3.5 秒内她再用技能打中就会引爆）：一枚发光的眼形魔印浮在目标胸前，微微脉动、外圈的符文尖角转动（参考 Base_VFX_Icon、Rune04）。4 帧要首尾无缝（游戏每 0.2 秒从第 1 帧重播）。约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with crimson (#FF9AB0, #E8264B, #9B1032).
Effect: a FLOATING SIGIL MARK, 4 frames, a SEAMLESS LOOP: a glowing magenta eye-shaped rune with a crimson pupil, hooked rune points around it; over the 4 frames the glow pulses (dim, bright, brighter, bright) and the rune points rotate a little; frame 4 flows back into frame 1. Semi-bright, not too large: it floats on a character's chest.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `leblanc_fx_q_pop.png`：Q 魔印引爆（大图），6 帧

魔印被她的下一个技能引爆：魔印碎成一团洋红色的玻璃碎片向四周炸开，中间一圈光环扩散（参考 LBVU_Shard、Donut）。约 32 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2) and crimson (#FF9AB0, #E8264B, #9B1032).
Effect: a SIGIL SHATTERING, 6 frames: 1 the eye-shaped magenta rune flares white; 2 it cracks - bright lines of light across it; 3 THE BURST: it shatters into 8-10 angular magenta glass shards flying outward, a ring of magenta light expanding from the center; 4 the shards fly further and spin, the ring widens and thins; 5 the shards fade to violet, the ring breaks up; 6 a few fading specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `leblanc_fx_e_chain.png`：E 幻影锁链：飞出去的链头（飞行中循环），4 帧

甩出去的幻影锁链：最前面一个发光的洋红色链环（像一节空心的光环），后面接两三节越来越淡的链环和一条紫色光带（参考 LBVU_RibTile、EBeam）。上下对称。约 16 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a FLYING ETHEREAL CHAIN moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a bright hollow chain link of magenta light (an oval ring with a white-pink highlight), behind it 2-3 more links, each fainter and smaller, joined by a thin violet light ribbon that ripples; the links alternate flat / edge-on like a real chain.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the chain on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `leblanc_fx_e_tether.png`：E 锁链拴住目标：飞回她身边的一节链环（飞行中循环），4 帧

锁链拴住目标的 1.5 秒里，一节一节的光链环从目标飞回乐芙兰，连成一条锁链：每张只画一节发光的洋红色空心链环，左右两端有一点光丝，要能和前后一节接上。上下对称。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: ONE CHAIN LINK OF LIGHT moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a hollow oval link of magenta light with a white-pink highlight, a short thin violet light thread leaving it on the left and on the right (so that links in a row read as one chain); the link turns from flat to edge-on and back over the 4 frames and shimmers.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the link on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `leblanc_fx_e_cast.png`：E 出手：甩出锁链的闪光，4 帧

法杖甩出锁链的一瞬：一道洋红色的弧光一闪，带出两三节光链环的残影。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a CHAIN CAST FLASH, 4 frames: 1 a white-pink flash; 2 a short magenta arc of light sweeping to the right with 2 chain links of light in it; 3 the arc at full length, sparkles; 4 the arc and links fade.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `leblanc_fx_e_hit.png`：E 锁链打中，4 帧

锁链缠上目标：一下闪光，一圈光链环在目标身上一闪而收。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a CHAIN STRIKE, 4 frames: 1 a white-pink flash; 2 a ring of 5-6 magenta chain links of light snaps around the center; 3 the ring tightens, sparks fly off; 4 it fades to violet specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `leblanc_fx_e_root.png`：E 定身：锁链缠住目标的脚（1.5 秒），12 帧

锁链没被挣脱时定住目标 1.5 秒：地上一个洋红色的光圈（从斜上方看是扁椭圆，宽是高的 2 倍），几条发光的链子从光圈里升起缠住目标的脚和小腿。1–3 帧出现，4–9 帧持续（链子闪动），10–12 帧碎掉散开。中间留出人的位置（脚在椭圆中心），不要画人。约 26 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a CHAIN ROOT on the ground round a figure's feet (do NOT draw the figure), 12 frames: a flattened ellipse of magenta light on the ground (twice as wide as tall) at the bottom of the cell; 1-3 the ellipse appears and 3-4 chains of glowing magenta links rise from it and wrap round where the legs are (up to a third of the cell's height); 4-9 the chains hold, their links shimmering, the ellipse pulsing (a loop); 10-12 the chains shatter into magenta glass shards and fade. Leave the middle above the ellipse empty except for the chains.
Layout: one horizontal row of 12 equal cells, each 3 wide to 2 tall, image size 9216x512 (each cell 768x512); the ellipse centered at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `leblanc_fx_w_pad.png`：W 魔影迷踪：起点的魔法阵（地面，1.25 秒，大图），10 帧

她冲刺出去时在原地留下的魔法阵（1.25 秒后她会闪回这里）：地上一个发光的洋红色圆阵（从斜上方看是扁椭圆），里面一圈旋转的符文和她的眼形魔印（参考 Donut、Decal001_Dissolve、Rune04）。1–2 帧亮起，3–8 帧持续（符文转动、一闪一闪），9–10 帧收缩。约 30 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with crimson (#FF9AB0, #E8264B, #9B1032).
Effect: a MAGIC CIRCLE ON THE GROUND seen from above (a flattened ellipse, twice as wide as tall), 10 frames: 1-2 a ring of magenta light appears; 3-8 the circle glows: an outer ring, an inner ring of small rune marks that turn a little each frame, an eye-shaped rune with a crimson pupil in the middle, the glow pulsing; 9-10 the circle shrinks into its center and fades.
Layout: one horizontal row of 10 equal cells, each 2 wide to 1 tall, image size 5120x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `leblanc_fx_w_trail.png`：W 冲刺时身后的残影（跟随），5 帧

她冲向目标时身后的残影：几道洋红色的横向光痕从她身上向后（左边）拖出，夹着几片玻璃碎光（参考 Z_Streak、LBVU_Shard）。中间偏右是她的位置，不要画人。约 26 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a DASH TRAIL behind a figure that moves to the RIGHT (do NOT draw the figure), 5 frames: 4-5 horizontal streaks of magenta light trailing to the LEFT from the right part of the cell, with a few small angular glass shards between them; 1 the streaks start short and bright; 2-3 they stretch long to the left; 4 they thin and break; 5 they fade to violet specks.
Layout: one horizontal row of 5 equal cells, each 3 wide to 2 tall, image size 3840x512 (each cell 768x512); the streaks on the cell's middle height, starting near the right. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `leblanc_fx_w_blast.png`：W 落地爆炸（大图），7 帧

她落地时周围炸开：地上一圈洋红色的冲击波（扁椭圆，从中间往外扩），中间向上炸起一团玻璃碎片和光（参考 Donut、LBVU_Shard、ImpactSpike）。约 56 格宽、28 格高（地上的圈），碎片可以高出一点。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a MAGIC BLAST ON THE GROUND, 7 frames: 1 a white-pink flash at the center; 2 a bright magenta burst rises from the center and a ring of light starts on the ground (a flattened ellipse, twice as wide as tall); 3 THE BLAST: the ring at two thirds of the cell's width, 8-10 angular magenta glass shards thrown up and out; 4 the ring reaches the cell's edges, the shards fly further; 5 the ring thins and breaks into arcs; 6 the shards fall and fade to violet; 7 a few specks.
Layout: one horizontal row of 7 equal cells, each 2 wide to 1 tall, image size 3584x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `leblanc_fx_w_hit.png`：W 爆炸打中的敌人，4 帧

被爆炸打中：一团洋红色的碎光在敌人身上炸开。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a SHARD HIT, 4 frames: 1 a white-pink flash; 2 a magenta burst with 4-5 small angular glass shards flying out; 3 the shards spread; 4 they fade.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `leblanc_fx_w_out.png`：W 闪回：从落点消失，5 帧

她从落点闪回原处的一瞬：原地一道竖直的洋红色光柱，人的形状碎成玻璃碎片向上飘散。约 22 格宽、30 格高（和她差不多高）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: a VANISH, 5 frames: 1 a tall narrow column of magenta light (as tall as the cell) appears; 2 it brightens, a figure-sized cloud of small angular glass shards in it; 3 the shards drift up and apart; 4 the column thins; 5 a few fading shards near the top.
Layout: one horizontal row of 5 equal cells, each 3 wide to 4 tall, image size 1920x1024 (each cell 384x512); centered at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `leblanc_fx_w_in.png`：W 闪回：在起点出现，5 帧

她在起点重新出现：玻璃碎片从四周向中间聚拢成人形，一道竖直光柱一闪。约 22 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, glass or sparks, colours only from a magenta ramp (#FFF2FC, #FFA8EE, #E651D3, #A42BB5, #5C1A74) with glass highlights (#FFFFFF, #ECE6FF, #B8A8F2).
Effect: an APPEAR, 5 frames: 1 small angular magenta glass shards scattered around the cell; 2 they fly inward toward the middle; 3 they gather into a tall narrow column of bright magenta light (as tall as the cell); 4 a white-pink flash in the column; 5 the column fades.
Layout: one horizontal row of 5 equal cells, each 3 wide to 4 tall, image size 1920x1024 (each cell 384x512); centered at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `leblanc_fx_a_orb` | view_projectiles `league_leblanc_a_orb`（朝右，游戏转到飞行方向） | 10 × 8 |
| `leblanc_fx_a_cast` | view_effects `league_leblanc_a_cast`（施法者身上，跟随） | 12 |
| `leblanc_fx_a_hit` | view_effects `league_leblanc_a_hit`（跟随） | 14 |
| `leblanc_fx_q_orb` | view_projectiles `league_leblanc_q_orb`（朝右，游戏转到飞行方向） | 16 × 12 |
| `leblanc_fx_q_cast` | view_effects `league_leblanc_q_cast`（施法者身上，跟随） | 16 |
| `leblanc_fx_q_hit` | view_effects `league_leblanc_q_hit`（跟随） | 18 |
| `leblanc_fx_q_mark` | view_effects `league_leblanc_q_mark`（目标身上，跟随，每 12 tick 重播） | 16 × 12 |
| `leblanc_fx_q_pop` | view_effects `league_leblanc_q_pop`（目标身上，跟随；大图 league_leblanc_big） | 32 |
| `leblanc_fx_e_chain` | view_projectiles `league_leblanc_e_chain`（朝右，游戏转到飞行方向） | 16 × 8 |
| `leblanc_fx_e_tether` | view_projectiles `league_leblanc_e_tether`（从目标飞回她身边，每隔几 tick 发一节，连起来就是锁链；朝右画） | 10 × 6 |
| `leblanc_fx_e_cast` | view_effects `league_leblanc_e_cast`（施法者身上，跟随） | 14 |
| `leblanc_fx_e_hit` | view_effects `league_leblanc_e_hit`（跟随） | 16 |
| `leblanc_fx_e_root` | view_effects `league_leblanc_e_root`（目标身上，跟随；一次播完 1.5 秒） | 26 × 16 |
| `leblanc_fx_w_pad` | view_effects `league_leblanc_w_pad`（她冲刺前站的地方，不跟随，地面层；大图 league_leblanc_big） | 30 × 14 |
| `leblanc_fx_w_trail` | view_effects `league_leblanc_w_trail`（施法者身上，跟随，冲刺时） | 26 × 18 |
| `leblanc_fx_w_blast` | view_effects `league_leblanc_w_blast`（她落地的地方，不跟随，地面层；大图 league_leblanc_big） | 56 × 28（半径 26000） |
| `leblanc_fx_w_hit` | view_effects `league_leblanc_w_hit`（跟随） | 16 |
| `leblanc_fx_w_out` | view_effects `league_leblanc_w_out`（她消失的地方，不跟随） | 22 × 30 |
| `leblanc_fx_w_in` | view_effects `league_leblanc_w_in`（她出现的地方，不跟随） | 22 × 30 |

- `q_mark` 每 12 tick 重播（4 帧 × 3 tick），`e_root` 12 帧共 90 tick（1.5 秒），`w_pad` 10 帧撑满回程 75 tick。
- 大招版：`rq_orb/cast/hit/mark/pop`、`re_chain/tether/cast/hit/root`、`rw_trail/blast/hit` 由基础图调亮（偏白粉）并放大约 1.25 倍（`rw_blast` 按 RW 半径 30000）；`p_clone` 用待机第 1 帧染成半透明感的紫色、8 帧淡出。
- 清掉 Codex 给光和碎片描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单。
