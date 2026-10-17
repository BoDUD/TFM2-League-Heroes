# 瘟疫之源 图奇：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型和动作已定（`design/twitch_design.png`，8 倍，38 行、44 格宽）。
> - 大小对照 `design/twitch_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。图奇 44×38 格。每条写的大小都是游戏像素（格）。
> - `design/twitch_shots.png`：定稿动作（4 倍），青色十字是特效的起点（弩尖、扔桶的手、脚下），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里图奇自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版皮肤：**毒液是亮绿色（被动、W、E、R）；隐身的烟是紫黑色；弩和火星是黄铜色**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **围着人的烟雾、光环、火光只画外圈，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：飞出去的弩箭、大招的穿透箭、毒桶画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。画在他身上、晚于技能开始播放的（`q_out`、`q_reset`、`e_cast`、`r_cast`）和挂在他身上、脚下循环的（`q_as`、`r_on`、`w_slow`）要**严格左右对称**（逐格对称）；地上的毒池 `w_pool` 上下左右都对称。只有 `a_flash`（弩口火光）是朝右的：它会烘进普攻的动作帧里，跟着人物一起翻转。
> - 特效照下面第 1–17 条和「所有特效图的规则」画，每张一个 PNG，文件名 `twitch_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。
> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`twitch_fx_done.zip`）放在 outputs 里，或放在 `outputs/twitch-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「死亡毒液」 | 弩箭攻击，每一下给目标挂一层毒（每秒真实伤害） | `a_bolt` · `a_flash` · `a_hit` |
| 技能 1 = Q「埋伏」 | 隐身接近，出手现形后加攻速；击杀英雄刷新 | `q_cast` · `q_out` · `q_as` · `q_reset` |
| 技能 2 = W「剧毒之桶」→ E「毒性爆发」 | 扔毒桶（减速、上毒、留下毒池），再引爆所有中毒敌人身上的毒 | `w_cask` · `w_hit` · `w_pool` · `w_slow` · `e_cast` · `v_pop` |
| 大招 = R「火力全开」 | 6 秒内射程变长、弩箭变成直线穿透 | `r_cast` · `r_on` · `r_bolt` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、毒液、火星没有黑描边，也不要用最深的颜色给形状描一圈边**。只有弩箭和毒桶（实物）有 1 格深色描边（`#0A0806`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 毒液绿（被动、W、E、R）：`#FFFFFF`、`#F2FFD0`、`#C8F060`、`#8CD82A`、`#4E9A18`、`#24500C`；
  - 隐身的紫黑烟（Q）：`#F4E8FF`、`#C8A8F0`、`#8A5CC0`、`#56347E`、`#2E1A48`；
  - 黄铜火星（弩口、刷新）：`#FFFFFF`、`#FFF6C0`、`#FFE68A`、`#FCC23A`、`#C88A1C`；
  - 弩箭和毒桶（实物）：`#0A0806`、`#7A4A10`、`#C88A1C`、`#FCC23A`、`#FFE68A`、`#8CD82A`、`#F2FFD0`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他身上或脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，毒桶半径 28000，大招箭宽 6000）。

### 1. `twitch_fx_a_bolt.png`：普攻弩箭（飞行中，循环），4 帧

图奇的弩箭：一根黄铜色的短箭，箭头是金色、带一点绿色毒液的光，后面拖两格淡绿光迹（参考 Arrow_Txt、AA_Posion_Smoke_Cloud）。朝右飞。**上下对称**。4 帧无缝循环（光迹闪一闪）。约 12 格长、4 格高。

```text
Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, a 1-square dark outline #0A0806 around the object, colours only from brass and venom (#0A0806, #7A4A10, #C88A1C, #FCC23A, #FFE68A, #8CD82A, #F2FFD0).
Effect: a CROSSBOW BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a brass bolt 9 squares long and 1 square thick with a 3-square gold arrowhead pointing RIGHT, a tiny venom green glint on the head, a short pale green trail 3 squares long behind it; the trail flickers each frame.
Layout: one horizontal row of 4 equal 14:6 cells, image size 896x96 (each cell 224x96, 16 px a square); the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `twitch_fx_a_flash.png`：普攻弩口的火光（烘进普攻第 3 帧），3 帧

弩箭射出去那一下弩口的一团绿色毒烟和黄铜色火星（参考 Z_Muzzle_Flash、AA_Posion_Smoke_Cloud）。朝右喷。3 帧。约 10 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C) and a brass spark ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: a MUZZLE PUFF blowing to the RIGHT, 3 frames: 1 a bright pale green and white flash 6 squares across at the left middle with 3 brass sparks; 2 a puff of venom green smoke 8 squares across drifting right, 2 sparks; 3 the puff thinning into 3 small fading motes.
Layout: one horizontal row of 3 equal 12:10 cells, image size 576x160 (each cell 192x160, 16 px a square); the flash starts at the left middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `twitch_fx_a_hit.png`：普攻打中（目标身上），4 帧

弩箭打中、上了一层毒：一小团绿色毒液溅开，几滴绿毒往外飞（参考 P_Impact、common_aciddrops32）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a VENOM SPLAT HIT, 4 frames: 1 a pale green-white splat 6 squares across at the center; 2 a venom green splash 10 squares across, 5 droplets flying out; 3 droplets falling, the splash breaking up; 4 a few fading drops.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `twitch_fx_v_pop.png`：E 毒性爆发：每个中毒的敌人身上炸开，6 帧

毒性爆发：中毒的敌人身上炸开一团绿色的毒液爆炸，一圈毒刺往外扎，一团毒烟往上冒（参考 E_Tar_Spikes、E_Tar_Flash、E_Posion_Smoke_Cloud）。约 22 格，居中画。一个人身上有几层毒就会同时播几次（叠在一起），所以**每一帧都要亮**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a TOXIC BURST, 6 frames: 1 a pale green-white flash 8 squares across at the center; 2 a venom green explosion 16 squares across with 8 sharp green spikes stabbing outward; 3 the spikes longest (20 squares across), a white core; 4 the spikes breaking off, a cloud of green smoke rising; 5 the smoke drifting up, thinning; 6 a few fading wisps.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `twitch_fx_w_cask.png`：W 剧毒之桶：飞出去的毒桶（飞行中，循环），4 帧

图奇扔出去的毒桶：一个圆滚滚的小木桶，黄铜箍，桶口冒绿光，后面拖一小段绿色毒液（参考 W_Bottle_Txt、W_Acidball_Orb_Color、W_Mis_Trail）。**上下对称**（每一帧都对称：只让绿光和高光一闪一闪，不画旋转）。4 帧无缝循环。约 6 格。

```text
Pixel art game sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, a 1-square dark outline #0A0806 around the object, colours only from brass and venom (#0A0806, #7A4A10, #C88A1C, #FCC23A, #FFE68A, #8CD82A, #F2FFD0).
Effect: a VENOM CASK in flight, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame: a round wooden cask 5 squares across with two brass hoops, its middle glowing venom green, 2 green droplets trailing to the LEFT; each frame the glow and the droplets pulse (no spinning).
Layout: one horizontal row of 4 equal square cells, image size 512x128 (each cell 128x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `twitch_fx_w_hit.png`：W 毒桶砸中（每个被砸中的人身上），5 帧

毒桶砸中：人身上溅满绿色毒液，几块碎木片和黄铜箍飞出去（参考 W_Splash、twitch_venom_bomb_splash、Venom_Bomb_Splash_A）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C) and a brass spark ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: a VENOM SPLASH on a figure, 5 frames: 1 a pale green-white splash 8 squares across; 2 green venom splashing 14 squares across, 3 small brass splinters flying out; 3 venom dripping down, the splinters farther; 4 drips; 5 a few fading drops.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `twitch_fx_w_pool.png`：W 毒池（地上，持续 3 秒，循环），4 帧

毒桶砸碎后地上的一滩绿色毒液：从斜上方看的扁椭圆，边上一圈亮绿，中间冒泡，几缕毒烟往上飘（参考 W_Splat_anim、W_Persist_Smoke_Color、W_Green_Ring）。**上下左右都对称**。4 帧无缝循环（气泡和烟换位置，但每一帧都对称）。约 56 格宽、22 格高——这是技能的范围（半径 28 格），画满。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a TOXIC PUDDLE on the ground seen from above at an angle, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: a flat venom green ellipse 54 squares wide and 20 tall with a bright pale green rim 1-2 squares thick and a darker green inside, 6 bubbles placed symmetrically (popping and growing frame to frame), a few thin green smoke wisps rising from it, symmetric too.
Layout: one horizontal row of 4 equal 58:24 cells, image size 3712x384 (each cell 928x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `twitch_fx_w_slow.png`：W 减速（目标脚下，循环），4 帧

被毒桶减速：脚下一小滩绿色毒液，几滴绿毒往下滴（参考 common_aciddrops32、stinkDrops_02）。**左右对称**。4 帧无缝循环。约 16 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a SLOWING VENOM PUDDLE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: a flat green ellipse puddle 14 squares wide and 4 tall, bubbling, 2 small drips falling into it each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `twitch_fx_q_cast.png`：Q 埋伏：隐身时炸开的毒烟（他身上），6 帧

图奇隐身：身边“噗”地炸开一团紫黑色的烟，烟里转着一圈绿光，几个小点散开（参考 Q_Bamf_Smoke_4x4、Q_Bamf_Swirl、Q_Cas_Dots）。**左右对称**，**中间留空**（人在中间）。6 帧：1 一圈光，2–4 烟炸开扩大，5–6 烟散开淡去。约 34 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet smoke ramp (#F4E8FF, #C8A8F0, #8A5CC0, #56347E, #2E1A48) and a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a STEALTH SMOKE POOF around a figure (do NOT draw the figure; leave its place empty), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left mostly empty: 1 a thin pale green ring 14 squares across at the center; 2-4 puffs of violet-black smoke bursting out round it to 32 squares across, a swirl of green motes inside; 5-6 the smoke thinning and fading upward.
Layout: one horizontal row of 6 equal square cells, image size 3456x576 (each cell 576x576, 16 px a square); the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `twitch_fx_q_out.png`：Q 现形（他身上，一闪），5 帧

从隐身里现形、攻速加成开始：一圈紫烟往外散开，一圈绿光闪一下（参考 Q_Camouflage_Ring_RGB、Q_Smoke）。**左右对称**，**中间留空**。约 28 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet smoke ramp (#F4E8FF, #C8A8F0, #8A5CC0, #56347E, #2E1A48) and a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a REVEAL FLASH around a figure (do NOT draw the figure; leave its place empty), 5 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left empty: 1 a flattened green ring 12 squares wide bright at his waist; 2-3 the ring widening to 26 squares, violet smoke wisps peeling off outward; 4 the smoke fading; 5 a few motes.
Layout: one horizontal row of 5 equal square cells, image size 2400x480 (each cell 480x480, 16 px a square); the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `twitch_fx_q_as.png`：Q 攻速加成（他身上，循环），4 帧

出隐身后的攻速加成：他腰两侧各一团小小的绿色毒火在跳（参考 Z_Green_Glow、Q_Buff_Colormap）。**左右对称**，**中间留空**（人在中间）。4 帧无缝循环。约 26 格宽、12 格高，两团各约 5 格，相距约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: two small VENOM FLAMES at a figure's waist (do NOT draw the figure; leave its place empty), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT: one green-white flame 5 squares across on each side, 16 squares apart, the middle 12 squares empty; each frame the flames flicker and 2 tiny motes rise.
Layout: one horizontal row of 4 equal 28:14 cells, image size 1792x224 (each cell 448x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `twitch_fx_q_reset.png`：Q 刷新（击杀英雄，他头顶一闪），5 帧

击杀英雄、埋伏刷新：他头顶亮一下一个小老鼠头的绿色标记（英雄联盟里中毒的人头上的小老鼠；参考 P_Rat_Icon）。**左右对称**。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C) and a brass spark ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: a RAT-HEAD GLINT, 5 frames, SYMMETRIC LEFT TO RIGHT: 1 a small green dot; 2 it opens into a simple rat-head icon 12 squares wide (two round ears, a pointed snout downward) in bright green with a white edge; 3 the icon brightest, 4 short brass rays round it; 4 the icon shrinking; 5 a fading dot.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `twitch_fx_e_cast.png`：E 毒性爆发：他身边炸开的毒云，6 帧

图奇放毒性爆发：身边一圈绿色毒云往外炸开，毒液像触手一样往四周甩（参考 E_Posion_Smoke_Cloud、E_Tar_Flash、W_Nova）。**左右对称**，**中间留空**（人在中间）。6 帧：1 一圈亮绿，2–4 毒云炸开扩大，5–6 散开淡去。约 44 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a TOXIC CLOUD BURST around a figure (do NOT draw the figure; leave its place empty), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 14 squares left mostly empty: 1 a flattened pale green ring 16 squares wide at his waist; 2-4 green poison clouds and splashing venom streaks bursting outward to 42 squares wide and 28 tall; 5-6 the clouds thinning and fading.
Layout: one horizontal row of 6 equal 46:32 cells, image size 4416x512 (each cell 736x512, 16 px a square); the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `twitch_fx_r_cast.png`：R 火力全开：开大的一下（他身上），6 帧

图奇开大：身边一圈绿色的能量冲击波往外扩，几道绿色的光柱往上冲（参考 R_EnergyWave、R_Spotlight、R_Wispy_Ribbon）。**左右对称**，**中间留空**（人在中间）。6 帧：1 一圈光，2–4 冲击波扩大、光柱往上，5–6 散开。约 36 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C) and a brass spark ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: a POWER-UP SURGE around a figure (do NOT draw the figure; leave its place empty), 6 frames, SYMMETRIC LEFT TO RIGHT, the middle 12 squares left mostly empty: 1 a bright green ring 14 squares across at his waist; 2-4 the ring widening to 34 squares as a flattened shockwave, 4 thin green light ribbons shooting up round him to 34 squares high, brass sparks; 5-6 the ribbons fading upward.
Layout: one horizontal row of 6 equal square cells, image size 3648x608 (each cell 608x608, 16 px a square); the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `twitch_fx_r_on.png`：R 火力全开中（他身上，循环，6 秒），4 帧

开大的 6 秒里：他身边一圈绿色的光丝在转，脚下一圈淡绿光（参考 R_Wispy_Ribbon、Z_Green_Glow）。**左右对称**，**中间留空**（人在中间）。4 帧无缝循环。约 30 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a GREEN POWER AURA around a figure (do NOT draw the figure; leave its place empty), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT, the middle 18 squares wide left empty: thin green and pale green light ribbons (1 square thick) rising round the figure's place in a tall oval 28 squares wide and 34 tall, a flattened pale green ring at the feet, a few motes drifting up; each frame the ribbons move up a step.
Layout: one horizontal row of 4 equal 32:38 cells, image size 2048x608 (each cell 512x608, 16 px a square); the figure's place horizontally centered, its feet 2 squares above the bottom, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `twitch_fx_r_bolt.png`：R 穿透弩箭（飞行中，循环），4 帧

大招的穿透箭：一道绿色的能量箭，比普攻箭长一倍，箭头白亮，后面拖一条长长的绿光尾巴（参考 R_EnergyWave、common_AirSpiritStreak）。朝右飞。**上下对称**。4 帧无缝循环。约 22 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C).
Effect: a PIERCING ENERGY BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM: a bright white-green arrowhead 4 squares long pointing RIGHT, a glowing green shaft 8 squares long, a tapering green light trail 10 squares long behind it; the trail ripples each frame.
Layout: one horizontal row of 4 equal 24:8 cells, image size 1536x128 (each cell 384x128, 16 px a square); the arrowhead's point 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `twitch_fx_r_hit.png`：R 穿透箭打中（每个被穿过的人身上），4 帧

穿透箭打中：一道绿色的能量火花横着炸开，几滴毒液溅出（参考 R_EnergyWave、P_Impact）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, smoke, splashes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a venom green ramp (#FFFFFF, #F2FFD0, #C8F060, #8CD82A, #4E9A18, #24500C) and a brass spark ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: an ENERGY PIERCE HIT, 4 frames: 1 a horizontal white-green streak 12 squares long through the center; 2 a green burst 10 squares across, 4 droplets and 3 brass sparks flying out; 3 sparks scattering; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `twitch_fx_a_bolt` | view_projectiles `league_twitch_a_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 12 × 4 |
| `twitch_fx_a_flash` | 烘进普攻出手帧（`twitch_bake.json`：弩尖的位置，随人物朝向翻转） | 10 × 8 |
| `twitch_fx_a_hit` | view_effects `league_twitch_a_hit`（跟随，画在人物上面） | 12 |
| `twitch_fx_v_pop` | view_effects `league_twitch_v_pop`（跟随，画在人物上面） | 22 |
| `twitch_fx_w_cask` | view_projectiles `league_twitch_w_cask`（抛物线飞行；上下对称） | 6 × 6 |
| `twitch_fx_w_hit` | view_effects `league_twitch_w_hit`（跟随，画在人物上面） | 16 |
| `twitch_fx_w_pool` | view_projectiles `league_twitch_w_pool`（地上，不旋转，画在人物下面；上下左右都对称） | 56 × 22 |
| `twitch_fx_w_slow` | view_buffs `league_twitch_w_slow`（画在脚下，左右对称） | 16 × 6 |
| `twitch_fx_q_cast` | view_effects `league_twitch_q_cast`（技能第一 tick 播放、跟随；中心在站位点上面约 16 格） | 34 × 34 |
| `twitch_fx_q_out` | view_effects `league_twitch_q_out`（不跟随，左右对称；中心在站位点上面约 16 格） | 28 |
| `twitch_fx_q_as` | view_buffs `league_twitch_q_as`（跟随，画在他身上，左右对称） | 26 × 12 |
| `twitch_fx_q_reset` | view_effects `league_twitch_q_reset`（不跟随，左右对称；中心在站位点上面约 34 格） | 16 |
| `twitch_fx_e_cast` | view_effects `league_twitch_e_cast`（不跟随，画在人物下面，左右对称；中心在站位点上面约 12 格） | 44 × 30 |
| `twitch_fx_r_cast` | view_effects `league_twitch_r_cast`（不跟随，左右对称；中心在站位点上面约 16 格） | 36 × 36 |
| `twitch_fx_r_on` | view_buffs `league_twitch_r_on`（跟随，画在他身上，左右对称） | 30 × 36 |
| `twitch_fx_r_bolt` | view_projectiles `league_twitch_r_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 22 × 6 |
| `twitch_fx_r_hit` | view_effects `league_twitch_r_hit`（跟随，画在人物上面） | 14 |

- `a_bolt` 从弩尖出（出手帧弩尖在站位点前面约 19 格、脚底上面 11 格，和站位点同高：`y_offset` 0），画面开头补几帧空的，让箭离开弩再出现；`r_bolt` 同一个出手点。
- `a_flash` 烘进普攻第 3 帧（`twitch_bake.json`），不做成特效（红色方翻转）。`q_cast` 在动作第一 tick 播放、跟随；`q_out`、`q_reset`、`e_cast`、`r_cast` 晚于第一 tick，`is_follow` 为 false，逐格左右对称；`w_pool` 是地上的投射物画面。
- 用 `pixel_1x/` 切格（import_twitch 的做法），断言对称；清掉 Codex 给光描的最深色边（尖刺、毒桶保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比。
