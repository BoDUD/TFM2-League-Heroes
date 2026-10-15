# 杰斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 21 张特效图 + 10 张画进他动作帧的图。** 造型和动作已定（`design/jayce_designs.png`：锤形正面、锤形侧身、炮形正面、炮形侧身；动作都是侧身朝右）。**全部用生图（image_gen）画，不要用代码拼方块。**
> - 他在游戏里是**高清**的：每个游戏像素里 1.5×1.5 个细格子；1 倍时锤形待机 38×49 格（连锤）。
> - **两种画法**：
> 1. 第一部分 21 张普通特效（电光弹、电球、打中、落地冲击、闪电领域、加速之门、身上的 buff）**照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。大小对照 `design/jayce_size.png`（1 倍待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士）；`design/jayce_shots.png` 是定稿动作（4 倍），青色十字是电光弹 / 电球飞出、锤头砸地的位置。
> 2. 第二部分是**画进他自己动作帧**的图（他的帧会随朝向镜像，特效图不会，所以炮口火光、炮口蓄能、锤头的电光拖影和砸地这些有方向的东西必须画进帧里）。这些按**他的高清细格子**画：`bake/jayce_bake_<名字>_<帧>.png` 是那一帧的定位图（横图 256×170 格或竖图 170×256 格，每格 6 像素；他本人画成淡灰色、只用来对位置；灰框是这一帧的范围，红线是地面，每 10 格一道浅线；青色十字是起点：炮口或锤头）。**在同样大小、同样格子的图上只画特效，背景透明，不要画他本人**；Claude 按格子取回，直接叠进他的帧。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里杰斯自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**海克斯科技的电光：白亮的芯、淡青、青色到深一点的电蓝**；**锤子砸中的地方加海克斯金色火星**；**加速之门是金色门柱 + 青色能量门面**；**削甲标记是左金右蓝的碎盾牌**。
> - **特效要亮**：每道电光、每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画两边，中间身体位置留空**；地上的冲击圈和闪电领域里面基本是空的，不要涂满；**他身上的 buff（超能电荷、护甲加成）要克制**。
> - **方向（重要，红色方不会镜像）**：飞行的电光弹 / 电球画成**朝右飞、上下对称**（游戏会把它转向飞行方向）；打中、目标身上、地上的画面、加速之门和身上的 buff 都要**严格左右对称**（逐格对称）。第二部分画进帧里的图照定位图的方向画（往右喷），不用对称。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `jayce_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（第一部分），以及 `jayce_bake_<名字>_<帧>.png`（第二部分，和定位图一样大、格子对齐）和它的 `pixel_1x/` 读回（256×170 或 170×256）。透明度只有 0 和 255、要求对称的逐格对称。附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`（**原样，不要自己整理**），打包成 `jayce_fx_pack_done.zip`。**每张图单独交付，不要只给一张总览图**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 变形（锤 ↔ 炮）+ 被动「海克斯科技电容」 | 锤形大锤横扫 / 炮形电光弹；变形时一闪 + 加速，变炮后第一发削甲，变锤后加护甲 | `a_swipe`（帧里）· `a_hit` · `c_flash`（帧里）· `c_bolt` · `c_hit` · `tf_spark` · `haste` · `shred` · `guard` |
| 技能 1 = 锤形 Q「苍穹之跃」/ 炮形 Q「电能震荡」 | 锤形跳起砸向敌人，落点范围伤害 + 减速；炮形打出电球，撞到第一个敌人爆炸 | `q_slam`（帧里）· `q_land` · `q_hit` · `q_slow` · `cq_charge`（帧里）· `cq_fire`（帧里）· `cq_orb` · `cq_boom` · `cq_hit` |
| 技能 2 = 锤形 E「雷霆一击」+ W「闪电领域」/ 炮形 W「超能电荷」 | E 把敌人击飞；E 冷却时开闪电领域（脚下电场每半秒电一次周围敌人）；炮形 W 接下来 3 发更快更痛 | `e_arc`（帧里）· `e_blow` · `w_crown`（帧里）· `w_field` · `w_zap` · `hyper_glow`（帧里）· `hyper` |
| 大招「加速电炮」 | 立刻变炮，放下加速之门，打出穿门的大电球（更快、更远、更痛、爆炸更大） | `gate` · `g_charge`（帧里）· `g_fire`（帧里）· `gq_orb` · `gq_boom` · `gq_hit` · `haste` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**电光、光、火星都没有黑描边，也不要用最深的颜色给形状描一圈边**（加速之门的门柱是实物，可以有描边）。
- **要亮**：每个形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 海克斯电光（电光弹、电球、打中、闪电领域、超能电荷）：`#FFFFFF`、`#E6FDFF`、`#9FEFFF`、`#4FD2FF`、`#2C8FE8`、`#2350B8`；
  - 海克斯金色火星（锤子砸中、护甲加成）：`#FFFFFF`、`#FFF4C8`、`#FFD86A`、`#F5A93A`、`#C8741E`；
  - 加速之门：`#FFFFFF`、`#CFF8FF`、`#5EE6F2`、`#2BB0C8`、`#1F6F96`、`#E8C46A`、`#A9782E`；
  - 削甲标记：`#FFFFFF`、`#9FE6FF`、`#3FA9F5`、`#FFD25A`、`#E08A2A`、`#7A4A9E`；
  - 加速：`#FFFFFF`、`#D6F6FF`、`#8FE3FF`、`#48B9F0`；
- 打中、爆炸居中画，不旋转；地上的圈是从斜上方看的扁椭圆（宽是高的 2.5 倍左右）。
- 画在别人身上的画面**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 第一部分：特效（21 张，游戏格子）

21 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：苍穹之跃落点半径 18000，闪电领域半径 20000，电能震荡爆炸半径 15000，加速电炮爆炸半径 21000）。大图（cq_boom、gate、gq_boom、gq_orb、q_land、w_field）按每格 8 像素画，其余每格 16 像素。

### 1. `jayce_fx_c_bolt.png`：炮形普攻：电光弹（飞行中，循环），4 帧

加农炮打出的电光弹：一颗白亮的小能量弹，青蓝色外圈，后面拖一小段电光尾巴（参考 Jayce_Base_Projectile、Lightning_Trail）。朝右飞。**上下对称**。4 帧无缝循环（尾巴的电光一闪一闪）。约 10 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: a SMALL ENERGY BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a bright oval head 4 squares long and 3 tall with a white core and pale cyan round it, a cyan-blue tail 6 squares long tapering behind it with tiny lightning kinks mirrored above and below; the tail flickers each frame.
Layout: one horizontal row of 4 equal 12:7 cells, image size 768x112 (each cell 192x112, 16 px a square); the head's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `jayce_fx_cq_orb.png`：炮形 Q 电能震荡：电球（飞行中，循环），4 帧

电能震荡的电球：一颗圆滚滚的能量球，白亮的芯、淡青到青蓝，外面绕着几道细细的电弧，后面一条短短的电光尾巴（参考 Jayce_Base_Projectile、Lightning_flipbook、SphereWaves）。朝右飞。**上下对称**。4 帧无缝循环（电弧转动）。约 16 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: an ELECTRIC ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a round orb 8 squares across - a white core 3 squares, pale cyan and cyan round it, a thin blue rim - with 2-3 thin lightning arcs (1 square thick) crackling over its surface mirrored top and bottom, and a short cyan tail 7 squares long behind it; the arcs move each frame.
Layout: one horizontal row of 4 equal 18:12 cells, image size 1152x192 (each cell 288x192, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `jayce_fx_gq_orb.png`：大招 加速电炮：穿过加速门的大电球（飞行中，循环，大），4 帧

穿过加速之门后的大电球：比电能震荡的电球大一圈、更亮，外面绕着更多电弧，后面一条长长的电光尾巴，尾巴边上几道金色的加速线（参考 Jayce_Base_Projectile、Lightning_Trail、Jayce_speedlines）。朝右飞。**上下对称**。4 帧无缝循环。约 26 格长、14 格高。这张很大：按**每格 8 像素**画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: an ACCELERATED ELECTRIC ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a round orb 12 squares across - a white core 5 squares, pale cyan and cyan round it, a blue rim - with 4 lightning arcs crackling over it mirrored top and bottom, a cyan tail 14 squares long behind it and 2 thin gold speed lines along the tail mirrored above and below; the arcs and the tail flicker each frame.
Layout: one horizontal row of 4 equal 30:18 cells, image size 960x144 (each cell 240x144, 8 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `jayce_fx_a_hit.png`：锤形普攻打中（目标身上），4 帧

大锤砸中：一团白亮的冲击，带金色火星和几道短短的电光往外蹦（参考 Jayce_Hit_Flash、Hammer_Burst）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a HAMMER HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares across; 2 a burst 11 squares across - a white core, pale cyan, 4 short cyan lightning kinks and 4 gold sparks at mirrored places; 3 the kinks and sparks flying out to 14 squares; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `jayce_fx_c_hit.png`：炮形普攻打中（目标身上），4 帧

电光弹打中：小小的一团电光炸开，几颗青蓝色电火花（参考 Jayce_Hit_Flash、Lightning_flipbook）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: a SMALL ELECTRIC HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 a burst 9 squares across - white core, pale cyan, 4 tiny lightning sparks at mirrored places; 3 the sparks at 12 squares; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `jayce_fx_q_hit.png`：锤形 Q 苍穹之跃砸中的敌人（每个目标身上），4 帧

苍穹之跃砸到的敌人：身上一下电击——几道竖着的电光从脚下往上跳，带金色火星（参考 Lightning_02、Jayce_Base_Energy）。**左右对称**，中间人形位置大致留空（6 格宽）。约 16 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a SHOCK on a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), a clear upright gap 6 squares wide in the middle: 1 small jagged lightning bolts 4 squares tall at both sides near the bottom; 2 the bolts jumping up to 14 squares, gold sparks; 3 the bolts at their brightest, 18 squares; 4 the last sparks.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered across, the bolts' roots on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `jayce_fx_e_blow.png`：锤形 E 雷霆一击打中（目标身上，把它击飞），5 帧

雷霆一击把敌人打飞：一个大一点的冲击——白亮的闪光，一圈青蓝色的电环往外冲，几道电弧和金色火星（参考 Jayce_Base_Shockwave、Hammer_Burst、Hit_Flash）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a THUNDERING IMPACT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a white-cyan burst 12 squares across with a ring of cyan lightning round it; 3 the ring 20 squares across, 6 lightning arcs and 6 gold sparks thrown out at mirrored places; 4 the ring breaking into arcs; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `jayce_fx_w_zap.png`：锤形 W 闪电领域电到的敌人（目标身上，每半秒），3 帧

闪电领域每半秒电一下周围的敌人：一道竖着的细闪电从上面劈下来，落点一小团白光（参考 Lightning_02、Plasma_Beam1）。**左右对称**（闪电画在正中间，左右的折线对称）。约 10 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: a SMALL LIGHTNING STRIKE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a thin jagged lightning bolt 1-2 squares thick from the top of the cell down the middle to the bottom, its kinks mirrored left and right, a white flash 4 squares at its foot; 2 the bolt at its brightest with 2 tiny side branches mirrored; 3 the bolt fading, sparks at the foot.
Layout: one horizontal row of 3 equal 12:18 cells, image size 576x288 (each cell 192x288, 16 px a square); centered across, the bolt's foot on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `jayce_fx_cq_hit.png`：炮形 Q 电球打中的敌人（目标身上），4 帧

电能震荡炸到的敌人：身上一团电光，几道细电弧（参考 Lightning_flipbook、Hit_Flash）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: an ELECTRIC SHOCK on a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan flash 6 squares across; 2 a burst 12 squares across with 4 thin lightning arcs at mirrored places; 3 the arcs at 14 squares; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `jayce_fx_gq_hit.png`：大招 加速电炮打中的敌人（目标身上），5 帧

加速电炮炸到的敌人：比普通电球更猛的电击，一圈电环 + 多道电弧（参考 Jayce_Base_Shockwave、Lightning_flipbook）。**左右对称**。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: a BIG ELECTRIC SHOCK on a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares across; 2 a burst 16 squares across with a ring of cyan lightning; 3 the ring 20 squares across, 8 lightning arcs at mirrored places; 4 the arcs breaking up; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `jayce_fx_tf_spark.png`：变形（锤 ↔ 炮）的瞬间（他身上，跟着他），4 帧

变形的一瞬间：他身边亮起一圈海克斯能量——两边各几道往上窜的电光和金色齿轮状的小光点，脚下一圈亮环（参考 Jayce_Base_Energy、Jayce_Aura、Color_Flashes）。**严格左右对称**（这张画在他身上，游戏不会镜像），中间人形位置留空（10 格宽、26 格高）。约 28 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a HEXTECH TRANSFORM FLASH round a figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 10 squares wide and 26 tall): 1 a thin bright ellipse ring 20 squares wide on the ground at the bottom; 2 cyan lightning wisps and gold spark motes rising at both sides to 24 squares; 3 the wisps at their top (34 squares), 4 small gold gear-shaped glints at mirrored places; 4 fading motes.
Layout: one horizontal row of 4 equal 30:36 cells, image size 1920x576 (each cell 480x576, 16 px a square); centered across, the ground ring on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `jayce_fx_q_land.png`：锤形 Q 苍穹之跃落地（地上，大），6 帧

他从天上砸下来：落点炸开一团白亮的冲击，一圈电光冲击波沿着地面往外推到半径 18 个游戏像素（从斜上方看的扁椭圆），地面裂开几道发光的裂纹，几块金色火星往四周飞（参考 Jayce_Base_Shockwave、Jayce_Base_Crack、Hammer_Burst）。要亮，但地上的圈里面别涂满。**左右对称**。这张很大：按**每格 8 像素**画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a HAMMER SLAM SHOCKWAVE, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares across at the ground point; 2 a burst of white-cyan light 16 squares wide and 14 tall rising from it, a ring of lightning starting out along the ground; 3 the ring a flat ellipse 30 squares wide and 12 tall made of short jagged lightning (1-2 squares thick), 4 glowing cracks 6 squares long on the ground from the centre at mirrored places; 4 the ring at full size (40 wide, 16 tall), 8 gold sparks flying out at mirrored places; 5 the ring thinning, the cracks fading; 6 fading sparks. The inside of the ring stays mostly empty.
Layout: one horizontal row of 6 equal 44:28 cells, image size 2112x224 (each cell 352x224, 8 px a square); centered across, the ground point (the ellipse's center) 10 squares above the cell's bottom edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `jayce_fx_w_field.png`：锤形 W 闪电领域（他脚下跟着他，4 秒，大），8 帧

闪电领域：他脚下一圈跟着他走的电场——从斜上方看的扁椭圆（半径 20 个游戏像素），边上一圈噼啪跳动的细电光，偶尔一道电弧跳过椭圆，里面是空的、只有极淡的几点青光（参考 SphereWaves、Lightning_flipbook、Jayce_Aura）。不能挡住站在里面的他。**左右对称**、**上下对称**。8 帧（每帧电光位置都变一点，前后连起来像一直在噼啪响）。这张很大：按**每格 8 像素**画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: an ELECTRIC FIELD RING on the ground seen from above at an angle, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) and top to bottom: a flat ellipse 44 squares wide and 18 tall whose rim is a ring of short crackling lightning (1-2 squares thick, white-cyan with blue) with a thin cyan glow line; 2 small lightning arcs jumping along the rim at mirrored places, in different places each frame; the inside EMPTY but for 6 tiny faint cyan dots; mirrored in every frame.
Layout: one horizontal row of 8 equal 48:22 cells, image size 3072x176 (each cell 384x176, 8 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `jayce_fx_cq_boom.png`：炮形 Q 电球爆炸（落点，大），5 帧

电能震荡的电球撞到敌人炸开：一团白亮的电光炸起，一圈青蓝色的电环冲到半径 15 个游戏像素，几道电弧往外蹦（参考 Jayce_Base_Shockwave、Lightning_flipbook、SphereWaves）。**左右对称**。这张很大：按**每格 8 像素**画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: an ELECTRIC BLAST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares across; 2 a ball of white-cyan light 16 squares across; 3 a ring of cyan lightning 26 squares across round a fading core, 8 lightning arcs at mirrored places; 4 the ring at 30 squares, breaking up; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1360x272 (each cell 272x272, 8 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `jayce_fx_gq_boom.png`：大招 加速电炮爆炸（落点，大），6 帧

加速电炮的大电球炸开：比普通的更大更猛——白亮的核心，两圈电环冲到半径 21 个游戏像素，很多道电弧和金色火星（参考 Jayce_Base_Shockwave、Lightning_flipbook、Color_Flashes）。**左右对称**。这张很大：按**每格 8 像素**画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a BIG ELECTRIC BLAST, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares across; 2 a ball of white-cyan light 22 squares across; 3 an inner ring 26 and an outer ring 34 squares across of cyan lightning, 10 arcs at mirrored places; 4 the outer ring at 42 squares, 8 gold sparks; 5 the rings breaking up; 6 fading sparks.
Layout: one horizontal row of 6 equal square cells, image size 2208x368 (each cell 368x368, 8 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `jayce_fx_gate.png`：大招：加速之门（放在他面前，大），6 帧

加速之门：一座海克斯科技的拱门立起来——两根金色的门柱（海克斯机械的样子），中间是一片发光的青色能量门面，门顶一道弧（参考 Jayce_Gent_GateBlue_TX_CM 的门柱、Jayce_Aura）。从正面看（**严格左右对称**，游戏不会镜像）。第 1–2 帧门柱从地上升起，第 3–5 帧能量门面亮起、闪烁，第 6 帧变淡。约 34 格宽、40 格高。这张很大：按**每格 8 像素**画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gate ramp (#FFFFFF, #CFF8FF, #5EE6F2, #2BB0C8, #1F6F96, #E8C46A, #A9782E).
Effect: an ACCELERATION GATE seen from the front, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two upright hextech pillars 4 squares wide and 36 tall (gold frames with cyan glowing slots) standing 30 squares apart on the ground, an arch across their tops; between them a sheet of glowing cyan energy (semi-solid squares in 2-3 cyan shades, a few white streaks); 1 the pillars rising out of the ground, 12 squares tall; 2 the pillars full height; 3 the energy sheet lighting up from the bottom; 4 the sheet full and bright; 5 the sheet flickering, streaks moving up; 6 the whole gate faded to half.
Layout: one horizontal row of 6 equal 38:44 cells, image size 1824x352 (each cell 304x352, 8 px a square); centered across, the pillars' feet on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `jayce_fx_q_slow.png`：Q 苍穹之跃的减速（敌人脚下，2 秒，循环），4 帧

被砸中减速的敌人：脚下一小圈静电，几颗电火花跳动（参考 Lightning_flipbook、common_Slow-Wake）。**左右对称**。4 帧无缝循环。约 16 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: STATIC at a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 16 squares wide and 5 tall of faint cyan static (dots and 1-square kinks) on the ground, 4 tiny sparks jumping up 2-3 squares at mirrored places; the sparks change places each frame.
Layout: one horizontal row of 4 equal 18:10 cells, image size 1152x160 (each cell 288x160, 16 px a square); centered across, the ellipse on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `jayce_fx_hyper.png`：炮形 W 超能电荷（他身上，3 发，循环），4 帧

超能电荷：他身边环绕着蓝色电光——两边各一道绕身的电弧，几颗电火花往上飘，**要克制**、别盖住他（参考 Lightning_flipbook、Jayce_Base_Energy）。**左右对称**，中间人形位置留空（10 格宽、24 格高）。4 帧无缝循环。约 26 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: a HYPER CHARGE AURA round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear upright area 10 squares wide and 24 tall): a thin curved lightning arc (1 square thick) at each side from hip to shoulder height, 6 small sparks rising at mirrored places; the arcs flicker and the sparks rise a square each frame; SUBTLE - thin and sparse.
Layout: one horizontal row of 4 equal 28:32 cells, image size 1792x512 (each cell 448x512, 16 px a square); centered across, the lowest sparks on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `jayce_fx_shred.png`：变炮后第一发打中的削甲（敌人头上，5 秒，循环），4 帧

被削甲削魔抗的敌人：头上一个小小的碎裂护盾标记——左半边金色、右半边蓝色的盾牌被一道裂缝劈开，轻轻闪（参考 Global_Debuff_Armor_MR_Shred）。**左右对称**（裂缝画在正中间竖直，左右两半形状对称，颜色左金右蓝也可以）。4 帧无缝循环（轻轻上下浮动 1 格、闪光）。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a shred-sign ramp (#FFFFFF, #9FE6FF, #3FA9F5, #FFD25A, #E08A2A, #7A4A9E).
Effect: a SHREDDED SHIELD SIGN, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) in shape (left half gold, right half blue is fine): a small shield 10 squares wide and 11 tall split down the middle by a jagged vertical crack 1 square wide, a 1-square violet rim; 1 at rest; 2 one square higher, a white glint on its top edge; 3 at rest; 4 one square lower.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `jayce_fx_haste.png`：被动 / 加速之门的加速（他脚下，循环），4 帧

海克斯科技电容 / 加速之门的加速：脚下一圈淡蓝的光，两边各几道短短的速度线往上飘（参考 Jayce_speedlines、Jayce_Aura）。**左右对称**（速度线画成竖直往上飘，不要朝左或朝右）。4 帧无缝循环。约 20 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a speed ramp (#FFFFFF, #D6F6FF, #8FE3FF, #48B9F0).
Effect: a HASTE GLOW at a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 20 squares wide and 5 tall of light cyan glow on the ground, 3 short vertical streaks (1 square wide, 2-4 tall) rising at each side at mirrored places; the streaks move up and fade each frame.
Layout: one horizontal row of 4 equal 22:10 cells, image size 1408x160 (each cell 352x160, 16 px a square); centered across, the ellipse on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `jayce_fx_guard.png`：变锤形的护甲 / 魔抗加成（他身上，4 秒，循环），4 帧

变成锤形后短暂的护甲加成：他身边一个淡淡的金色六边形护盾——只有一圈细细的边（1 格），中间完全空着，边上几点光一闪一闪（参考 Jayce_Color_Fade、Jayce_Base_Glow）。**要克制**。**左右对称**。4 帧无缝循环。约 26 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a THIN HEXAGON SHIELD round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the outline of an upright hexagon 26 squares wide and 32 tall, 1 square thick, pale gold with white highlights, completely EMPTY inside; 4 white-gold glints on the outline at mirrored places, moving along it each frame; SUBTLE.
Layout: one horizontal row of 4 equal 28:34 cells, image size 1792x544 (each cell 448x544, 16 px a square); centered across, the hexagon's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 第二部分：画进他动作帧的图（10 张，他的高清格子）

每张都在对应的定位图 `bake/jayce_bake_<名字>_<帧>.png` 上画：同样大小（横图 1536×1020、竖图 1020×1536 像素）、每格 6 像素，格子和定位图完全对齐；**只画特效，不画他**，背景透明。他本人在定位图里是淡灰色，只用来对位置。青色十字是起点（炮口或锤头）。画在他**上面**的会盖住他（所以都别盖住他的脸）。尽量画在灰框里，喷出去的电球和光可以伸出灰框。注意这里 1 格只有游戏里的 0.67 个像素，所以线条至少 3 格粗，太细的进游戏就看不见了。

### 22. 锤形普攻：大锤横扫的电光拖影（画进普攻第 4 帧）

大锤横着扫到最前面：锤头（青色十字）后面拖一道弧形的电光拖影（从上往下弯到锤头），锤头一圈电火花。画在他**上面**，别挡住脸。

**`jayce_bake_a_swipe_4.png`**（定位图 `bake/jayce_bake_a_swipe_4.png`，256×170 格，青色十字在第 189 列、第 67 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a LIGHTNING SWIPE behind the swinging hammer head: a curved trail of crackling white-cyan light 4-6 squares thick arcing from above his shoulder down to the cyan cross (the hammer head), 6 gold and cyan sparks round the cyan cross; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (189, 67), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. 锤形 Q 苍穹之跃：锤头砸地的电光（画进 Q 第 5 帧）

锤头砸进地面（青色十字）：锤头四周炸开一团白亮的电光，几道电弧往上窜，金色火星往两边飞。画在他**上面**。

**`jayce_bake_q_slam_5.png`**（定位图 `bake/jayce_bake_q_slam_5.png`，256×170 格，青色十字在第 191 列、第 88 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a LIGHTNING SLAM at the hammer head on the ground: a white flash 16 squares across centered on the cyan cross, 4 jagged lightning arcs (2 squares thick) leaping up 14-20 squares from it, 8 gold sparks flying out low to both sides; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (191, 88), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. 锤形 E 雷霆一击：往上挑的锤头带出的电弧（画进 E 第 4 帧）

大锤往右上方挑起（青色十字是锤头）：锤头后面一道往上弯的电弧拖影，锤头一团电光爆开。画在他**上面**，别挡住脸。

**`jayce_bake_e_arc_4.png`**（定位图 `bake/jayce_bake_e_arc_4.png`，256×170 格，青色十字在第 188 列、第 20 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: a THUNDER ARC: a curved trail of crackling white-cyan lightning 4-6 squares thick sweeping up from below to the cyan cross (the raised hammer head), a burst of white-cyan light 14 squares across at the cyan cross with 6 gold sparks; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (188, 20), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 25. 锤形 W 闪电领域：高举的锤头上噼啪的闪电（画进 W 第 3 帧）

大锤竖直高举（青色十字是锤头）：锤头周围噼啪地缠着几道闪电，一道闪电往天上窜，锤头一团白光。画在他**上面**。

**`jayce_bake_w_crown_3.png`**（定位图 `bake/jayce_bake_w_crown_3.png`，170×256 格，青色十字在第 77 列、第 39 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: LIGHTNING CROWNING the raised hammer head: a white-cyan glow 14 squares across round the cyan cross (the hammer head), 5 jagged lightning arcs (2 squares thick) crackling round it, one bolt shooting straight up 20 squares from it; nothing over his face.
Layout: ONE image 1020x1536, the same size and 6-px square grid as the guide picture (a 170 x 256 square grid); the cyan cross of the guide is at square (77, 39), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 26. 炮形普攻：炮口火光（画进炮形普攻第 2 帧）

开炮的一下：炮口（青色十字）前面一团白亮的炮口火光，往右喷出一小股电光。画在他**上面**。

**`jayce_bake_c_flash_2.png`**（定位图 `bake/jayce_bake_c_flash_2.png`，256×170 格，青色十字在第 174 列、第 71 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: a MUZZLE FLASH at the cannon's muzzle: a burst of white-cyan light 12 squares across centered 4 squares RIGHT of the cyan cross (the muzzle), 3 short spikes of light pointing right (the middle one longest, 10 squares), a ring of tiny sparks; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (174, 71), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 27. 炮形 Q 电能震荡：竖起的炮口蓄能（画进炮形 Q 第 3 帧）

炮几乎竖起来蓄能（青色十字是炮口）：炮口上方聚起一团旋转的电球，几道细电弧往里收。画在他**上面**。

**`jayce_bake_cq_charge_3.png`**（定位图 `bake/jayce_bake_cq_charge_3.png`，256×170 格，青色十字在第 146 列、第 19 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: CHARGING at the raised muzzle: a round glowing orb 10 squares across just above the cyan cross (the muzzle) - white core, pale cyan, cyan - with 5 thin lightning arcs curling inward to it; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (146, 19), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 28. 炮形 Q 电能震荡：电球出膛（画进炮形 Q 第 4 帧）

电球从炮口（青色十字）喷出去：炮口一团大的炮口火光，电球刚离开炮口往右飞（球心离炮口 12 格左右，后面拖电光）。画在他**上面**。

**`jayce_bake_cq_fire_4.png`**（定位图 `bake/jayce_bake_cq_fire_4.png`，256×170 格，青色十字在第 178 列、第 72 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: the ORB FIRED: a muzzle flash of white-cyan light 16 squares across at the cyan cross (the muzzle), the electric orb (10 squares across, white core, cyan, thin arcs) flying off to the RIGHT with its center 14 squares right of the cyan cross, a cyan trail between the muzzle and the orb; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (178, 72), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 29. 炮形 W 超能电荷：炮身充能（画进炮形 W 第 3 帧）

炮斜举着充能（青色十字是炮口）：炮口一团电光，沿着炮身跳几道细电弧。画在他**上面**，别挡住脸。

**`jayce_bake_hyper_glow_3.png`**（定位图 `bake/jayce_bake_hyper_glow_3.png`，256×170 格，青色十字在第 168 列、第 40 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8).
Effect: CHARGING the cannon: a white-cyan glow 10 squares across at the cyan cross (the muzzle), 4 thin lightning arcs (1-2 squares thick) jumping along the barrel back from the muzzle 20 squares, a few sparks; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (168, 40), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 30. 大招 加速电炮：竖起的炮口蓄满能（画进大招第 4 帧）

炮竖起来蓄满能（青色十字是炮口）：炮口上方一团更大的电球，几道电弧往里收，旁边几道金色的光往上冲。画在他**上面**。

**`jayce_bake_g_charge_4.png`**（定位图 `bake/jayce_bake_g_charge_4.png`，256×170 格，青色十字在第 151 列、第 16 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: FULL CHARGE at the raised muzzle: a big round glowing orb 14 squares across just above the cyan cross (the muzzle), 6 lightning arcs curling inward to it, 4 gold streaks rising beside it; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (151, 16), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 31. 大招 加速电炮：大电球出膛（画进大招第 5 帧）

大电球从炮口（青色十字）喷出去：炮口一大团炮口火光，大电球刚离开炮口往右飞（球心离炮口 16 格左右，后面拖长长的电光和金色加速线）。画在他**上面**。

**`jayce_bake_g_fire_5.png`**（定位图 `bake/jayce_bake_g_fire_5.png`，256×170 格，青色十字在第 193 列、第 67 行）：

```text
Pixel art game VFX overlay on a character frame for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around lightning, light, sparks or energy, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hextech lightning ramp (#FFFFFF, #E6FDFF, #9FEFFF, #4FD2FF, #2C8FE8, #2350B8) and a hextech gold ramp (#FFFFFF, #FFF4C8, #FFD86A, #F5A93A, #C8741E).
Effect: the BIG ORB FIRED: a muzzle blast of white-cyan light 20 squares across at the cyan cross (the muzzle), the big orb (14 squares across, white core, cyan, arcs) flying off to the RIGHT with its center 18 squares right of the cyan cross, a long cyan trail and 2 thin gold speed lines between the muzzle and the orb; nothing over his face.
Layout: ONE image 1536x1020, the same size and 6-px square grid as the guide picture (a 256 x 170 square grid); the cyan cross of the guide is at square (193, 67), counted from the top-left; draw ONLY the effect in place - do NOT draw the faded figure, the grid, the box, the cross or the lines. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `jayce_fx_c_bolt` | view_projectiles `league_jayce_c_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 10 × 5 |
| `jayce_fx_cq_orb` | view_projectiles `league_jayce_cq_orb`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 10 |
| `jayce_fx_gq_orb` | view_projectiles `league_jayce_gq_orb`（BIG，朝飞行方向转，画成朝右飞；上下对称） | 26 × 14 |
| `jayce_fx_a_hit` | view_effects `league_jayce_a_hit`（跟随，画在人物上面；左右对称） | 14 |
| `jayce_fx_c_hit` | view_effects `league_jayce_c_hit`（跟随，画在人物上面；左右对称） | 12 |
| `jayce_fx_q_hit` | view_effects `league_jayce_q_hit`（跟随，画在人物上面；左右对称） | 16 × 18 |
| `jayce_fx_e_blow` | view_effects `league_jayce_e_blow`（跟随，画在人物上面；左右对称） | 20 |
| `jayce_fx_w_zap` | view_effects `league_jayce_w_zap`（跟随，画在人物上面；左右对称） | 10 × 16 |
| `jayce_fx_cq_hit` | view_effects `league_jayce_cq_hit`（跟随，画在人物上面；左右对称） | 14 |
| `jayce_fx_gq_hit` | view_effects `league_jayce_gq_hit`（跟随，画在人物上面；左右对称） | 20 |
| `jayce_fx_tf_spark` | view_effects `league_jayce_tf_spark`（CasterViewEffect，跟随，画在人物上面；**严格左右对称**） | 28 × 34 |
| `jayce_fx_q_land` | view_effects `league_jayce_q_land`（BIG，不跟随，留在落点；左右对称） | 40 × 24 |
| `jayce_fx_w_field` | view_effects `league_jayce_w_field`（BIG，跟随，画在人物下面；左右对称、上下对称；8 帧摊满 4 秒） | 44 × 18 |
| `jayce_fx_cq_boom` | view_effects `league_jayce_cq_boom`（BIG，不跟随，留在爆点；左右对称） | 30 |
| `jayce_fx_gq_boom` | view_effects `league_jayce_gq_boom`（BIG，不跟随，留在爆点；左右对称） | 42 |
| `jayce_fx_gate` | view_effects `league_jayce_gate`（BIG，不跟随，留在放门的地方；**严格左右对称**） | 34 × 40 |
| `jayce_fx_q_slow` | view_buffs `league_jayce_q_slow`（跟随，画在人物下面；左右对称） | 16 × 8 |
| `jayce_fx_hyper` | view_buffs `league_jayce_hyper`（跟随，画在人物上面；左右对称） | 26 × 30 |
| `jayce_fx_shred` | view_buffs `league_jayce_shred`（跟随，画在人物上面；左右对称） | 12 × 12 |
| `jayce_fx_haste` | view_buffs `league_jayce_haste`、`league_jayce_g_haste`（跟随，画在人物下面；左右对称） | 20 × 8 |
| `jayce_fx_guard` | view_buffs `league_jayce_guard`（跟随，画在人物上面；左右对称） | 26 × 32 |
| `jayce_bake_a_swipe_<帧>` | 画进 `hd_attack` 第 4 帧（人物上面） | 高清格子 |
| `jayce_bake_q_slam_<帧>` | 画进 `hd_skill` 第 5 帧（人物上面） | 高清格子 |
| `jayce_bake_e_arc_<帧>` | 画进 `hd_skill2` 第 4 帧（人物上面） | 高清格子 |
| `jayce_bake_w_crown_<帧>` | 画进 `hd_w_cast` 第 3 帧（人物上面） | 高清格子 |
| `jayce_bake_c_flash_<帧>` | 画进 `hd_c_attack` 第 2 帧（人物上面） | 高清格子 |
| `jayce_bake_cq_charge_<帧>` | 画进 `hd_c_skill` 第 3 帧（人物上面） | 高清格子 |
| `jayce_bake_cq_fire_<帧>` | 画进 `hd_c_skill` 第 4 帧（人物上面） | 高清格子 |
| `jayce_bake_hyper_glow_<帧>` | 画进 `hd_c_skill2` 第 3 帧（人物上面） | 高清格子 |
| `jayce_bake_g_charge_<帧>` | 画进 `hd_ult` 第 4 帧（人物上面） | 高清格子 |
| `jayce_bake_g_fire_<帧>` | 画进 `hd_ult` 第 5 帧（人物上面） | 高清格子 |

- 两张表：`asset/league/effects/league_jayce_fx`（小的）和 `league_jayce_big`（cq_boom、gate、gq_boom、gq_orb、q_land、w_field），tag = 名字（build_jayce.py 的 views）。
- 目标身上的 q_hit、w_zap、hyper、guard、tf_spark 底边放在脚底线（站位点下方 11.5 格）；地上的 w_field 椭圆中心、q_land 的落点、gate 的门柱底放在脚底线；w_field 8 帧摊满 240 tick；gate 6 帧约 1.2 秒；炮弹 / 电球的 y_offset 按 `design/jayce_shots.png` 的炮口高度重设（build_jayce c_y / cq_y / r_y）。
- 画进帧的图在 restyle 之后（rig_jayce.py --pinholes 那一步）按 `fx_bake_cells.json` 从画布上切下这一帧的范围，叠到 `assets/source/ppu/jayce_<tag>.png` 的高清帧上，伸出帧外的地方两边一样加宽；1 倍表按格子投票一起更新（rig_milio.bake 的做法）。
- 用 `pixel_1x/` 切格（import_milio_fx 的做法；Codex 自己读回太小太糊时从 raw 重读），断言对称；清掉 Codex 给电光描的最深色边；核对交回的张数和这份清单。
