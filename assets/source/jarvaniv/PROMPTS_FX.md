# 嘉文四世：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/jarvaniv_idle.png`：3/4 正面朝右的年轻王子，金色王冠头盔、深蓝羽冠，金色大肩甲和胸甲，深藏青的衣服和裙甲，护膝上镶蓝宝石，手里一根很长的银白枪头骑枪）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连竖着的骑枪 49 格高、23 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/jarvaniv_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/jarvaniv_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。他的普攻、Q 都是骑枪刺出去的，扔军旗、Q 冲刺、R 跳跃的飞行都在他自己的动作里，**特效都画在目标身上、他身上或地上，没有飞行的弹道**。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里嘉文四世自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**普攻和战争律动是金白色**，**巨龙撞击是青蓝色的速度光**，**它的破甲是英雄联盟的红色裂盾**，**德邦军旗是金色旗杆加蓝色旗帜**，**黄金圣盾是金色光壳加地上的蓝色冲击波**，**天崩地裂是灰褐色的岩石墙和尘土**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，不要盖住人。
> - **全部严格左右对称**（逐格对称）：这些画面在红色方不会镜像，他和目标朝左时也是同一张图（军旗也一样：旗帜从横杆上正面朝前直直垂下）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `jarvaniv_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/jarvaniv_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/jarvaniv_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「战争律动」 | 骑枪刺击；对同一个英雄隔一段时间的第一下按最大生命值额外伤害 | `a_hit` · `p_hit` |
| 技能 1 = E→Q「德邦军旗 → 巨龙撞击」 | 扔出军旗插在地上（砸到附近的敌人，8 秒里给身边的友方英雄加攻速），再刺出骑枪拖着自己冲到军旗那里，挑飞路上和落点周围的敌人，降低护甲 | `e_flag` · `e_hit` · `f_as` · `q_hit` · `q_shred` · `q_land` |
| 技能 2 = Q「巨龙撞击」单放 | 骑枪向前刺出一条直线，打中的敌人降低护甲 | `q_hit` · `q_shred` |
| 自动放的 W「黄金圣盾」 | 给自己一层护盾（4 秒），并减速身边的敌人 | `w_cast` · `w_on` · `w_hit` · `w_slow` |
| 大招「天崩地裂」 | 跳到敌方英雄身边砸下，周围升起一圈岩墙把敌人困住 3.5 秒；想跑出去的会被拉回来 | `r_ring` · `r_hit` · `r_zap` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、火星、烟、尘土、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：军旗、红色裂盾、岩石可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 金色光泽（普攻、战争律动、军旗的旗杆、黄金圣盾）：`#FFFFFF`、`#FFF4C8`、`#FFD86A`、`#E8A82C`、`#A86A14`、`#5C380A`；
  - 青蓝速度光（巨龙撞击、圣盾的冲击波）：`#FFFFFF`、`#DDF4FF`、`#8ED2FF`、`#3C96F0`、`#2258B8`、`#12306E`；
  - 红色（破甲裂盾）：`#FFFFFF`、`#FFD6C8`、`#FF8060`、`#E2341E`、`#9C1610`、`#520A08`；
  - 德玛西亚蓝（军旗的旗帜）：`#FFFFFF`、`#D2E2FF`、`#7CA4EA`、`#3566C4`、`#1F3E8A`、`#10224E`；
  - 灰褐岩石和尘土（天崩地裂、落地尘土）：`#EFE6D6`、`#CDBD9E`、`#A08C6C`、`#74624A`、`#4C4032`、`#2C241C`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：军旗砸中半径 16000，军旗光环半径 40000，黄金圣盾半径 30000，天崩地裂的岩墙环半径 36000）。

### 1. `jarvaniv_fx_a_hit.png`：普攻命中：骑枪枪尖刺中（目标身上），4 帧

枪尖刺中的一下：一颗白色的四芒星闪光，中间一道横着的金白色刺击光（往左右两边一样长），金色火星往外飞（参考 BA_HitEffect、BA_sliver、BA_color-firefade）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A).
Effect: a LANCE THRUST IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white four-pointed star flash 4 squares; 2 a gold-white horizontal thrust streak 12 squares wide and 2 tall through the middle with a white core, the star's thin rays 8 squares long; 3 the streak fading, 6 gold sparks flying out at mirrored places; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `jarvaniv_fx_p_hit.png`：被动「战争律动」触发（目标身上），5 帧

战争律动触发（按目标最大生命值额外伤害）：目标身上先一道金白闪光，然后白色的裂纹从中心往四周裂开（像盔甲被打裂，参考 P_Cracks），金色碎片往外飞，最后裂纹淡去。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A).
Effect: a MARTIAL CADENCE CRACK on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 6 squares; 2 white cracks bursting out from the centre (6 jagged lines 1 square thick and 5 squares long at mirrored angles) round a gold glow; 3 the cracks 8 squares long, gold shards flying out at mirrored places; 4 the cracks fading, the shards farther out; 5 faint cracks and two shards.
Layout: one horizontal row of 5 equal square cells, image size 1280x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `jarvaniv_fx_q_hit.png`：Q 巨龙撞击命中（目标身上），4 帧

骑枪带着蓝白色的冲击刺穿目标：一团白芯的青蓝色光爆，几道蓝白色的速度线往左右两边横着射出，蓝色火星（参考 Q_Streak、Q_ball01、Q_speedlines、Q_color-movequick）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue speed-light ramp (#FFFFFF, #DDF4FF, #8ED2FF, #3C96F0, #2258B8, #12306E).
Effect: a DRAGON STRIKE HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares with a cyan rim; 2 a cyan-blue burst 10 squares with a white core, 4 blue-white speed streaks 6 squares long shooting out sideways (2 to each side, mirrored); 3 the burst 14 squares and thinner, blue sparks at mirrored places; 4 fading blue motes.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `jarvaniv_fx_q_shred.png`：Q 破甲：头顶的红色裂盾（敌人身上，3 秒，循环），4 帧

被巨龙撞击打中的敌人护甲降低：头顶浮着一面**红色的小盾牌，中间一道裂缝**，裂缝发亮，一闪一闪（英雄联盟用的就是这个红色裂盾，参考 Q_armor_shred）。**左右对称**（裂缝画成竖直的对称折线）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFD6C8, #FF8060, #E2341E, #9C1610, #520A08).
Effect: a CRACKED RED SHIELD floating over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small heater shield 7 squares wide and 8 tall in crimson with a darker red rim (a 1-square dark edge is allowed: it is a solid thing), a jagged crack running straight down its middle (a symmetric zigzag 1 square wide) glowing white-orange; 1 the crack dim; 2 brighter; 3 brightest, 2 tiny red chips beside the shield at mirrored places; 4 like 2.
Layout: one horizontal row of 4 equal 10:12 cells, image size 640x192 (each cell 160x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `jarvaniv_fx_q_land.png`：E→Q 落地冲击：落到军旗处，挑飞周围的敌人（地上，不跟随），6 帧

他拖着骑枪冲到军旗那里落地，把周围的敌人挑飞：落点一道白蓝闪光，地上一圈青蓝色的冲击波往外扩（从斜上方看是扁椭圆，最大直径 34 格），几道蓝白色的光往上冲（挑飞的感觉），尘土和小石块往外、往上飞（参考 Q_GlobalTargetHit01、Q_SwirlRing_tx、DirtBits、X_Small_Stone）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue speed-light ramp (#FFFFFF, #DDF4FF, #8ED2FF, #3C96F0, #2258B8, #12306E) and a grey-brown rock and dust ramp (#EFE6D6, #CDBD9E, #A08C6C, #74624A, #4C4032, #2C241C).
Effect: a LANDING SHOCKWAVE on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue flash ellipse 12 squares wide and 4 tall at the ground's middle; 2 a cyan-blue shock ring on the ground (an ellipse 20 squares wide and 7 tall with a white inner edge), 4 blue-white streaks shooting UP from it at mirrored places (the knock-up), dust puffs; 3 the ring 30 squares wide and 10 tall, small stones and dirt bits flying up and out at mirrored places; 4 the ring 34 wide and fading, the stones at their highest; 5 dust settling, stones falling; 6 faint dust.
Layout: one horizontal row of 6 equal 40:24 cells, image size 3840x384 (each cell 640x384, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `jarvaniv_fx_e_flag.png`：E 德邦军旗：插在地上的军旗（地上，不跟随，8 秒），8 帧（1–2 落地、3–6 循环、7–8 消失）

他扔出的德邦军旗插进地里，站 8 秒：一根**金色的旗杆**（2 格粗、约 46 格高，顶上一个金色的翼形枪尖饰），尖饰下面一根金色横杆，横杆下面**垂着一面蓝色的旗帜**（约 14 格宽、20 格高，金边，中间一个金色的德玛西亚双翼徽记，下端剪成燕尾）。旗帜**正面朝前、直直往下垂，左右对称**（不往一边飘：游戏在红色方不会把图镜像）。第 1 帧旗从上往下落（整面旗在原位置上方 10 格，上面拖一道金光）；第 2 帧插进地面：杆脚一圈尘土和金色火花；第 3–6 帧旗帜轻轻起伏（下摆和两边微微波动，左右对称），杆脚一点淡金色的光一明一暗，第 6 帧接得回第 3 帧；第 7 帧整面旗变淡；第 8 帧只剩几粒金色光点。旗杆和旗帜是实心的东西，可以有一圈深色边（参考 E_Flag 的蓝金配色、英雄联盟里的德邦军旗）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A) and a royal blue banner ramp (#FFFFFF, #D2E2FF, #7CA4EA, #3566C4, #1F3E8A, #10224E) and a grey-brown rock and dust ramp (#EFE6D6, #CDBD9E, #A08C6C, #74624A, #4C4032, #2C241C).
Effect: THE DEMACIAN STANDARD planted in the ground, 8 frames (1-2 it lands, 3-6 a seamless loop while it stands, 7-8 it vanishes), SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a tall GOLD pole 2 squares thick and 46 squares tall standing upright in the middle, its foot 2 squares above the cell's bottom row, a gold winged spear-tip finial on top, a gold crossbar 16 squares wide under the finial; hanging straight down from the crossbar a ROYAL BLUE BANNER 14 squares wide and 20 tall with a gold border and a gold winged emblem in its middle, its bottom cut in a swallowtail (solid things: a 1-square dark outline is allowed round the pole and the banner); 1 the standard dropping from above: the whole standard 10 squares above its place, a gold streak of light trailing above it; 2 it strikes the ground: a dust ring round its foot (an ellipse 18 squares wide and 5 tall) and gold sparks at mirrored places; 3, 4, 5, 6 standing: the banner's lower edge and sides rippling gently (symmetric ripples), a soft gold glow at the pole's foot pulsing, frame 6 flows back into frame 3; 7 the whole standard faded (lighter, fewer details); 8 only a few gold sparkles where it stood.
Layout: one horizontal row of 8 equal 24:56 cells, image size 3072x896 (each cell 384x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `jarvaniv_fx_e_hit.png`：E 军旗砸中（目标身上），4 帧

军旗落地砸到附近的敌人：金白色的冲击闪光，金色和蓝色的碎光往外飞（参考 E_BlastShapes）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A) and a royal blue banner ramp (#FFFFFF, #D2E2FF, #7CA4EA, #3566C4, #1F3E8A, #10224E).
Effect: a STANDARD IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 5 squares; 2 a gold burst 10 squares with a white core and 4 blue shards at mirrored places; 3 the burst 14 squares and thinner, gold and blue sparks flying out; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `jarvaniv_fx_f_as.png`：军旗光环：友方英雄脚下的攻速光环（循环），4 帧

站在军旗附近的友方英雄攻速提高：脚下一圈细细的金色光环（扁椭圆，近的一边亮），往上飘几粒金色和蓝色的小光点。**左右对称**，只画在脚下，不要盖住人。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A) and a royal blue banner ramp (#FFFFFF, #D2E2FF, #7CA4EA, #3566C4, #1F3E8A, #10224E).
Effect: a RALLY AURA at a champion's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin gold ring on the ground (an ellipse 16 squares wide and 5 tall, brighter on its near side), 4 small gold and blue motes rising from it at mirrored places, each frame a little higher (frame 4 flows back into frame 1).
Layout: one horizontal row of 4 equal 18:10 cells, image size 1152x160 (each cell 288x160, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `jarvaniv_fx_w_cast.png`：W 黄金圣盾：施放（他身上，跟随），6 帧

他举起骑枪召唤黄金圣盾：胸口一道金白闪光，一层金色的护盾光壳从他身上撑开（包住全身的竖椭圆，只画 1–2 格粗的边和高光，中间身体位置留空），同时地上一圈蓝色的冲击波往外扩（减速身边的敌人）（参考 W_template_shield、W_template_shockwave_blue、W_color-righteousfury）。**左右对称**，中间身体位置留空（an armoured knight 18 squares wide and 40 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A) and a cyan-blue speed-light ramp (#FFFFFF, #DDF4FF, #8ED2FF, #3C96F0, #2258B8, #12306E).
Effect: GOLDEN AEGIS cast round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an armoured knight 18 squares wide and 40 tall stands in the middle, not drawn): 1 a white-gold flash 10 squares at its chest; 2 a golden shield shell springing up round the whole figure (an upright ellipse outline 34 squares wide and 46 tall, 1-2 squares thick, white-gold highlights on its upper left and right, the inside left empty), a blue shockwave ring starting on the ground (an ellipse 20 wide and 6 tall); 3 the shell brightest, the ground ring 36 wide and 11 tall in blue with a white inner edge; 4 the ring 46 wide and fading, gold sparks on the shell at mirrored places; 5 the shell dimmer; 6 the shell faint, a few gold motes.
Layout: one horizontal row of 6 equal 48:54 cells, image size 4608x864 (each cell 768x864, 16 px a square); centered across, the figure's feet (the ring's middle) 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `jarvaniv_fx_w_on.png`：W 圣盾持续：护盾光壳（他身上，4 秒，循环），4 帧

护盾还在的时候：他身上一层淡淡的金色光壳（竖椭圆的边，1 格粗），边上流动着金白色的高光，一闪一闪。只画边，中间身体位置留空（an armoured knight 18 squares wide and 40 tall stands in the middle, not drawn）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A).
Effect: a GOLDEN SHIELD SHELL round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an armoured knight 18 squares wide and 40 tall stands in the middle, not drawn): an upright ellipse outline 34 squares wide and 46 tall, 1 square thick, pale gold, the inside empty; bright white-gold glints sliding round it (2 at mirrored places in each frame, a little higher each frame); frame 4 flows back into frame 1.
Layout: one horizontal row of 4 equal 40:50 cells, image size 2560x800 (each cell 640x800, 16 px a square); centered across, the figure's feet 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `jarvaniv_fx_w_hit.png`：W 冲击命中（敌人身上），4 帧

圣盾的冲击波打中身边的敌人：一圈蓝色的冲击光，蓝白色的火星（参考 W_template_shockwave_blue）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue speed-light ramp (#FFFFFF, #DDF4FF, #8ED2FF, #3C96F0, #2258B8, #12306E).
Effect: a SHOCK HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a blue-white flash 4 squares; 2 a blue ring 8 squares with a white inner edge; 3 the ring 12 squares and thinner, blue sparks at mirrored places; 4 fading motes.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `jarvaniv_fx_w_slow.png`：W 减速（敌人脚下，2 秒，循环），4 帧

被减速的敌人脚下：一圈蓝色的光环，几道往下压的蓝色短线，一明一暗。**左右对称**，只画在脚下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan-blue speed-light ramp (#FFFFFF, #DDF4FF, #8ED2FF, #3C96F0, #2258B8, #12306E).
Effect: a SLOW at a unit's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a blue ring on the ground (an ellipse 14 squares wide and 4 tall), 4 short blue streaks pressing down onto it at mirrored places; 1 dim, 2 bright, 3 brightest, 4 bright.
Layout: one horizontal row of 4 equal 16:8 cells, image size 1024x128 (each cell 256x128, 16 px a square); centered across, the ellipse's middle 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `jarvaniv_fx_r_ring.png`：R 天崩地裂：围住敌人的岩墙环（地上，不跟随，3.5 秒），8 帧（1–3 升起、4–7 循环、8 崩塌）

他从天而降砸进地面，周围升起一圈岩石墙把敌人围在里面（从斜上方看是扁椭圆：宽 72 格、高 24 格）：第 1 帧落点一道金白闪光，地面裂开一道道裂纹伸到椭圆边（参考 R_slicegroundcracks）；第 2 帧沿着整个椭圆冒出尘土和碎石；第 3 帧一圈参差不齐的**灰褐色石墙**从地里升起（一块块石头 4–6 格宽、8–12 格高，近处的石头沿着椭圆的近边，远处的沿着远边、小一点），碎石往外飞；第 4–7 帧石墙立着（每帧石缝里冒一点尘土，第 7 帧接得回第 4 帧）；第 8 帧石墙崩塌成一圈矮矮的碎石和尘土（参考 R_Wall_TUpdate、R_Ground_rock、R_Smoke、R_Wall_death_01_Dust、X_Small_Stone）。**中间留空**（他和敌人站在里面）。**左右对称**。实心的石头可以有一圈深色边。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-brown rock and dust ramp (#EFE6D6, #CDBD9E, #A08C6C, #74624A, #4C4032, #2C241C) and a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A).
Effect: CATACLYSM: A RING OF ROCK WALLS rising round an arena seen from above at an angle, 8 frames (1-3 it rises, 4-7 a seamless loop while it stands, 8 it crumbles), SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the arena an ellipse 72 squares wide and 24 tall on the ground, its middle 12 squares above the cell's bottom row, the middle left empty (units stand there); 1 a gold-white flash 10 squares at the ellipse's middle and ground cracks (jagged dark lines) running out to the ellipse at mirrored angles; 2 dust and small stones bursting up all along the ellipse; 3 a ring of jagged grey-brown stone walls risen along the whole ellipse: separate rocks 4 to 6 squares wide and 8 to 12 squares tall standing side by side round it (the near rocks along the ellipse's near edge, the far rocks along its far edge and smaller), dust puffs at their feet, stones flying out; 4, 5, 6, 7 the walls standing, thin dust trickling from a few cracks between the rocks (different each frame, frame 7 flows back into frame 4); 8 the walls crumbled into a low ring of rubble and dust. Solid rocks may have a 1-square dark outline.
Layout: one horizontal row of 8 equal 80:40 cells, image size 10240x640 (each cell 1280x640, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `jarvaniv_fx_r_hit.png`：R 落地伤害（敌人身上），4 帧

天崩地裂砸到敌人：金白色的闪光，灰褐色的碎石和尘土往外炸开（参考 R_tar_gather、DirtBits）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-brown rock and dust ramp (#EFE6D6, #CDBD9E, #A08C6C, #74624A, #4C4032, #2C241C) and a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A).
Effect: a CRUSHING IMPACT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a gold-white flash 5 squares; 2 a burst of grey-brown rock chips and dust 10 squares with an orange-white core; 3 the chips 14 squares out at mirrored places, dust puffs; 4 settling dust.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `jarvaniv_fx_r_zap.png`：R 撞墙被拉回（敌人身上），4 帧

想跑出岩墙的敌人撞到墙被拉回圈里：一小团尘土加几粒金色火星。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sparks, smoke, dust or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grey-brown rock and dust ramp (#EFE6D6, #CDBD9E, #A08C6C, #74624A, #4C4032, #2C241C) and a gold gleam ramp (#FFFFFF, #FFF4C8, #FFD86A, #E8A82C, #A86A14, #5C380A).
Effect: a WALL BUMP on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small gold-white flash 3 squares; 2 a dust puff 8 squares with gold sparks; 3 the puff 12 squares and fading, sparks at mirrored places; 4 faint dust.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `jarvaniv_fx_a_hit` | view_effects `league_jarvaniv_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `jarvaniv_fx_p_hit` | view_effects `league_jarvaniv_p_hit`（跟随，画在人物上面；左右对称） | 16 |
| `jarvaniv_fx_q_hit` | view_effects `league_jarvaniv_q_hit`（跟随，画在人物上面；左右对称） | 14 |
| `jarvaniv_fx_q_shred` | view_buffs `league_jarvaniv_q_shred`（跟随，画在人物上面；左右对称；循环） | 10 × 12 |
| `jarvaniv_fx_q_land` | view_effects `league_jarvaniv_q_land`（不跟随，画在人物下面 z -1；左右对称；大图表） | 40 × 24 |
| `jarvaniv_fx_e_flag` | view_effects `league_jarvaniv_e_flag`（不跟随，画在人物上面 z 1；左右对称；大图表；3–6 帧循环铺满 8 秒） | 24 × 56 |
| `jarvaniv_fx_e_hit` | view_effects `league_jarvaniv_e_hit`（跟随，画在人物上面；左右对称） | 14 |
| `jarvaniv_fx_f_as` | view_buffs `league_jarvaniv_f_as`（跟随，画在人物下面；左右对称；循环） | 18 × 10 |
| `jarvaniv_fx_w_cast` | view_effects `league_jarvaniv_w_cast`（跟随，画在他上面 z 2；左右对称；大图表） | 48 × 54 |
| `jarvaniv_fx_w_on` | view_buffs `league_jarvaniv_w_on`（跟随，画在他上面；左右对称；循环） | 40 × 50 |
| `jarvaniv_fx_w_hit` | view_effects `league_jarvaniv_w_hit`（跟随，画在人物上面；左右对称） | 12 |
| `jarvaniv_fx_w_slow` | view_buffs `league_jarvaniv_w_slow`（跟随，画在人物下面；左右对称；循环） | 16 × 8 |
| `jarvaniv_fx_r_ring` | view_effects `league_jarvaniv_r_ring`（不跟随，画在人物下面 z -1；左右对称；大图表；4–7 帧循环铺满 3.5 秒） | 80 × 40 |
| `jarvaniv_fx_r_hit` | view_effects `league_jarvaniv_r_hit`（跟随，画在人物上面；左右对称） | 14 |
| `jarvaniv_fx_r_zap` | view_effects `league_jarvaniv_r_zap`（跟随，画在人物上面；左右对称） | 12 |

- 两张表：`asset/league/effects/league_jarvaniv_fx`（小的）和 `league_jarvaniv_big`（q_land、e_flag、w_cast、r_ring），tag = 名字（build_jarvaniv.py 的 views）。
- 没有投射物画面（views_p 为空）。`q_land`、`e_flag`、`r_ring` 不跟随（地上的晚播画面）；`q_land`、`r_ring` 画在人物下面（z -1），`e_flag` 在上面（z 1）；`e_flag` 第 3–6 帧循环铺满 8 秒（f_t 480 tick），`r_ring` 第 4–7 帧铺满 3.5 秒（r_t 210 tick）。
- 用 `pixel_1x/` 切格（import_nasus_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（内瑟斯的教训：别只信 pixel_1x）。
