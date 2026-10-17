# 卡莎：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型和 9 个动作已经做完并导入（`design/kaisa_ingame.png` 是游戏里的全部帧，3 倍；跑步另外在重画），这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡莎经典皮肤自己的特效贴图（电浆层数 P_Stack_Empty / Packed_Stacks、普攻电浆弹 AA_Mis_Bullet、W 的光束 W_Bullet / W_Trail / W_plasma、E 的电流 E_electrictity、进化光柱 E_evolve_godlay、R 的护盾 R_ShieldPlasmaShapes 和冲刺拖尾 R_DashTrail、引爆的闪电 P_FullStack_bolts），只在本地用，不要提交。颜色和画风对照 `design/kaisa_design.png`（定稿造型，8 倍）：她从翼舱尖到鞋底 44 格，其他英雄约 35–40 格。
> - 她通身深紫，游戏地面也偏暗：**特效要亮**——每个特效都要有白粉色的亮芯和亮洋红，暗紫色只做最外层，不要整团都是深紫（之前魔腾的特效太暗，在场上看不见）。
> - 特效照下面每一条和「所有特效图的规则」画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`，**不要品红**，特效本身就是洋红色）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最好打成一个 zip，放在 `outputs/kaisa-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「体表活肤」 | 手掌射出电浆弹；打中英雄叠电浆（头顶标记 1–4 层），第 5 层引爆 | `kaisa_fx_bolt` · `kaisa_fx_shot` · `kaisa_fx_hit` · `kaisa_fx_pl_stack` · `kaisa_fx_p_burst` |
| E「极限超载」（并在普攻里） | 开打时自动超载：先加移速（全身窜电），再 4 秒攻速（身上电弧）；进化后隐身 0.5 秒 | `kaisa_fx_e_cast` · `kaisa_fx_e_aura` · `kaisa_fx_e_invis` |
| 技能 1 = Q「艾卡西亚暴雨」 | 背后两个翼舱张开，射出 6 发（进化 12 发）追踪导弹，分给附近的敌人 | `kaisa_fx_q_pod` · `kaisa_fx_q_missile` · `kaisa_fx_q_hit` |
| 技能 2 = W「虚空索敌」 | 前臂炮蓄能、开火，一道很长的虚空光束打中第一个敌方英雄 | `kaisa_fx_w_charge` · `kaisa_fx_w_muzzle` · `kaisa_fx_w_bolt` · `kaisa_fx_w_hit` |
| 大招 = R「猎手本能」 | 起跳（原地爆发），化成紫色拖尾冲到目标身边落地，得到护盾 2 秒 | `kaisa_fx_r_launch` · `kaisa_fx_r_trail` · `kaisa_fx_r_land` · `kaisa_fx_r_shield` |
| 活体武器（进化） | Q、E、W 进化的那一刻 | `kaisa_fx_evolve` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光、没有半透明（要透出人的地方用隔格的点）。**没有黑描边**（特效和角色相反），也不要用最暗的颜色给特效描一圈边。
- 颜色（按每条写的用）：
  - 电浆洋红：`#4A0C63`、`#8E1FB8`、`#D23CF0`、`#F408EA`、`#FF9BF5`；亮芯：`#FFFFFF`、`#FFE3FB`、`#FFC2F6`；
  - 虚空紫：`#2B1450`、`#5226A0`、`#8A55E6`、`#BFA2FF`；紫烟：`#2A1F46`、`#463970`、`#6D5EA2`、`#A99BD6`；金（少用）：`#8D6246`、`#D7A965`、`#F7D896`。
- **飞行类特效（电浆弹、导弹、W 光束）一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- **掌心闪光、炮口蓄能和爆风画在她自己身上**：格子的左边中间就是掌心 / 炮口的位置，往右喷；她朝左时游戏会整张左右镜像。
- 命中、引爆、电浆标记居中画，不旋转；画在她身上的光环（E、护盾、进化）按每条写的格子，脚在格子底部；地面上的东西是从斜上方看的扁椭圆（宽是高的 2 倍左右）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `kaisa_fx_bolt.png`：普攻电浆弹（飞行），4 帧循环

从她手掌射出的一颗电浆弹：亮粉白的针形弹头，外面裹一层洋红色的光，后面拖一道短短的紫色光迹（参考图 AA_Mis_Bullet、AA_Mis_Trail）。约 12 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink core (#FFFFFF, #FFE3FB, #FFC2F6) wrapped in magenta and purple plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5).
Effect: a small PLASMA BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white-pink needle-shaped head at 80% of the cell width wrapped in a magenta glow, a short purple trail behind it to the left edge with two tiny sparks, flickering each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1152x128 (each cell 288x96); the bolt on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kaisa_fx_q_missile.png`：Q 艾卡西亚暴雨的导弹（飞行），4 帧循环

从背后翼舱射出的小导弹：一颗洋红色的小弹头（白粉色的芯），后面一缕扭动的紫色烟迹，飞行时尾迹左右摆动（参考图 Q_mis_dots、AA_Mis_AnimeShapes）。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink core (#FFFFFF, #FFE3FB, #FFC2F6), magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and a purple smoke trail (#2A1F46, #463970, #6D5EA2, #A99BD6).
Effect: a small HOMING MISSILE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a rounded magenta warhead with a white-pink core at 80% of the cell width, a short wavy purple trail of plasma puffs behind it to the left edge that wiggles up and down a square each frame.
Layout: one horizontal row of 4 equal cells, each 5 wide to 3 tall, image size 1280x192 (each cell 320x192); the missile on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kaisa_fx_w_bolt.png`：W 虚空索敌的光束（飞行），4 帧循环

虚空索敌：一道很长的紫色虚空能量弹，弹头是亮白粉色的尖锥，外面一层洋红色光，后面拖一道长长的紫色光迹，光迹上缠着两条细细的紫色闪电（参考图 W_Bullet、W_Trail、W_plasma）。约 26 格长、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink head (#FFFFFF, #FFE3FB, #FFC2F6), magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and void violet lightning (#2B1450, #5226A0, #8A55E6, #BFA2FF).
Effect: a long VOID BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white-pink cone-shaped head at 85% of the cell width wrapped in a magenta glow, a long violet trail behind it to the left edge, two thin zig-zag violet lightning lines twisting round the trail (their zig-zags change each frame).
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1728x192 (each cell 432x144); the bolt on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kaisa_fx_shot.png`：普攻掌心闪光（她的手掌，朝右），4 帧

开火时手掌那一下：掌心一颗白粉色的亮点，往右喷出一小团洋红色的电浆火焰，上下两粒紫色火花，最后散成紫色光点。格子左边中间就是她的掌心。约 10 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink flash (#FFFFFF, #FFE3FB, #FFC2F6) and magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5).
Effect: a small PALM FLASH blasting to the RIGHT from the middle of the cell's LEFT edge (the palm is there), 4 frames: 1 a white-pink star at the left edge; 2 a short cone of magenta plasma to 70% of the cell width, two tiny purple sparks above and below; 3 the cone breaks into purple sparks; 4 faint sparks.
Layout: one horizontal row of 4 equal cells, each 5 wide to 4 tall, image size 1280x256 (each cell 320x256); the palm at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kaisa_fx_hit.png`：普攻命中（目标身上），4 帧

电浆弹打中：一小团洋红色的电浆溅开，几粒紫色光点往外飞（参考图 AA_hit_tar_muzzle）。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink flash (#FFFFFF, #FFE3FB, #FFC2F6) and magenta sparks (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5).
Effect: a small PLASMA SPLASH, 4 frames: 1 a white-pink flash at the centre; 2 a star of magenta plasma with short curved spikes; 3 purple sparks flying out; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kaisa_fx_pl_stack.png`：电浆层数标记（目标头顶），4 行 × 6 帧

电浆叠层的标记：目标头顶上方一个紫色的「虚空角冠」图案（像参考图 P_Stack_Empty / Packed_Stacks：中间一个圆点，两边各两只往上弯的角），下面一排 4 个小格子表示层数。第 1 行亮 1 格、第 2 行亮 2 格……第 4 行亮 4 格（亮的格子是洋红色，暗的格子是深紫色）。每行 6 帧：1 弹出（稍大），2–5 保持（轻轻一闪），6 变淡。约 14 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5), dark void violet (#2B1450, #5226A0, #8A55E6, #BFA2FF) and a white-pink sparkle (#FFFFFF, #FFE3FB, #FFC2F6).
Effect: a PLASMA STACK MARK that floats over a target's head, 4 rows (row k = k stacks) of 6 frames: a small purple horned crest (a round dot in the middle with two horns curving up on each side, like the reference icon P_Stack_Empty) above a row of 4 small square pips; in row k the first k pips are lit bright magenta with a white centre and the rest are dark violet. Frame 1 the mark pops in a square bigger; frames 2-5 it holds, the lit pips blinking a little brighter in 3 and 5; frame 6 it fades to half size.
Layout: 4 rows of 6 equal cells, each 7 wide to 4 tall, image size 1344x512 (each cell 224x128); the mark centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kaisa_fx_p_burst.png`：电浆引爆（第 5 层，目标身上），7 帧

叠满 5 层引爆：目标身上猛地炸开一大团洋红色的电浆，几道紫色闪电向四周劈出去（参考图 P_FullStack_bolts、BA_Plasma），中间一个白粉色的爆心，最后剩下紫色的电火花。约 26 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink core (#FFFFFF, #FFE3FB, #FFC2F6), magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and violet lightning (#2B1450, #5226A0, #8A55E6, #BFA2FF).
Effect: a PLASMA RUPTURE, 7 frames: 1 a bright white-pink flash at the centre; 2 a burst of magenta plasma with four zig-zag violet lightning bolts shooting out; 3 the burst at its biggest (90% of the cell), the bolts branching; 4 the plasma breaking into curved magenta shards; 5 violet sparks and small arcs; 6 fading sparks; 7 a few specks.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kaisa_fx_e_cast.png`：E 极限超载启动（她身上），6 帧

极限超载：她全身窜起紫色的电流（参考图 E_electrictity、P_electricity），几道闪电从脚下往上爬，身体周围一圈洋红色的光闪一下，背后翼舱的位置迸出火花。格子中间下部是她（约 33 格宽、44 格高的人，不画人），电流画在她身体外围和身上。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, violet electricity (#2B1450, #5226A0, #8A55E6, #BFA2FF), magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and white-pink sparks (#FFFFFF, #FFE3FB, #FFC2F6).
Effect: a SUPERCHARGE burst round a character (the character is not drawn: imagine a 30x40-pixel figure standing in the middle of the cell, feet on the bottom row), 6 frames: 1 a ring of magenta light flashes round the feet; 2-3 several thin zig-zag violet lightning lines climb up round the figure's outline to its shoulders, white-pink sparks at their tips; 4 a burst of sparks at shoulder height on both sides (where the wing-pods are); 5 the lightning flickers and breaks up; 6 a few sparks.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1440x640 (each cell 240x320, the feet on the bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kaisa_fx_e_aura.png`：E 攻速加成期间的电流（她身上，循环），6 帧循环

攻速加成的那 4 秒：她身上不停跳动的细细紫色电弧，手和脚边几粒火花，不要太大，不要挡住人。首尾帧能接上。约 26 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, violet electricity (#2B1450, #5226A0, #8A55E6, #BFA2FF) and magenta sparks (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5).
Effect: a light ELECTRIC AURA round a character (not drawn: a 26x36-pixel figure in the middle, feet on the bottom row), 6 frames, a seamless loop: three or four short thin violet arcs jumping at different places on the figure's outline (hands, knees, shoulders), each lasting one or two frames, a few magenta sparks; never more than a few squares wide, the figure must stay visible.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 1440x640 (each cell 240x320, the feet on the bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kaisa_fx_e_invis.png`：E 进化后的隐身（她身上），5 帧

进化后的极限超载会隐身 0.5 秒：她身上漾开一圈紫色的半透明涟漪，像融进虚空（参考图 E_evolve_light、Death_dissorve）。约 28 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, void violet (#2B1450, #5226A0, #8A55E6, #BFA2FF) and magenta (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) dissolving specks.
Effect: a VOID CLOAK shimmer over a character (not drawn: a 28x40-pixel figure in the middle, feet on the bottom row), 5 frames: 1 a thin violet outline of light wraps the figure's shape; 2-3 the outline breaks into drifting violet and magenta specks rising up; 4 the specks thin out; 5 a few specks. Use a checker of violet specks (every other square) for the see-through parts, no semi-transparency.
Layout: one horizontal row of 5 equal cells, each 3 wide to 4 tall, image size 1200x640 (each cell 240x320, the feet on the bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kaisa_fx_q_pod.png`：Q 翼舱发射闪光（单个翼舱口），5 帧

艾卡西亚暴雨发射时一个翼舱口的闪光：一团洋红色的火光从翼舱的光眼里喷出，几粒火花和一缕紫色的烟（参考图 Q_cas_smoke）。只画一个，Claude 会放到两个翼舱上。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink flash (#FFFFFF, #FFE3FB, #FFC2F6), magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and purple smoke (#2A1F46, #463970, #6D5EA2, #A99BD6).
Effect: a MISSILE LAUNCH FLASH from a pod's opening, 5 frames: 1 a white-pink flash at the centre; 2 a burst of magenta fire spraying up and out, small sparks; 3 the fire at its biggest with a ring of sparks; 4 a puff of purple smoke; 5 faint smoke.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kaisa_fx_q_hit.png`：Q 导弹命中（目标身上），5 帧

导弹打中：一团洋红色的小爆炸，紫色碎光往外飞（参考图 Q_Tar_Impact）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink core (#FFFFFF, #FFE3FB, #FFC2F6), magenta (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and violet (#2B1450, #5226A0, #8A55E6, #BFA2FF).
Effect: a MISSILE IMPACT, 5 frames: 1 a white-pink flash at the centre; 2 a round burst of magenta fire with short spikes; 3 the burst at its biggest, violet shards flying out; 4 fading sparks and a small purple puff; 5 specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `kaisa_fx_w_charge.png`：W 前臂炮蓄能（炮口，朝右），5 帧

虚空索敌出手前：前臂炮的炮口聚起一团紫色能量，周围的紫色光点往炮口里吸，越来越亮。格子左边中间是炮口。约 14 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5), void violet (#2B1450, #5226A0, #8A55E6, #BFA2FF) and a white-pink core (#FFFFFF, #FFE3FB, #FFC2F6).
Effect: an ENERGY CHARGE at a cannon's mouth, the mouth at the middle of the cell's LEFT edge, 5 frames: 1 a few violet specks scattered round the mouth; 2 the specks drawn in toward the mouth in curved lines; 3 a small magenta orb forming at the mouth; 4 the orb brighter with a white-pink core and short rays; 5 the orb at its brightest.
Layout: one horizontal row of 5 equal cells, each 7 wide to 6 tall, image size 1400x240 (each cell 280x240); the cannon's mouth at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `kaisa_fx_w_muzzle.png`：W 炮口爆风（炮口，朝右），5 帧

虚空索敌开火：炮口一团白粉色的闪光，一圈紫色的冲击环往右扩，往右喷出紫色的光锥（参考图 W_flash）。格子左边中间是炮口。约 20 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink flash (#FFFFFF, #FFE3FB, #FFC2F6), magenta (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and violet (#2B1450, #5226A0, #8A55E6, #BFA2FF).
Effect: a VOID MUZZLE BLAST to the RIGHT from the middle of the cell's LEFT edge, 5 frames: 1 a big white-pink flash; 2 a cone of magenta and violet light to 90% of the cell width and a violet shock ring (an ellipse, taller than wide) round the mouth; 3 the ring moving right and widening, short white rays; 4 the light breaking into violet sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal cells, each 10 wide to 7 tall, image size 2000x280 (each cell 400x280); the mouth at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `kaisa_fx_w_hit.png`：W 命中（目标身上），6 帧

虚空索敌打中：一圈紫色的虚空冲击环炸开，中间一颗白粉色的光，几道紫色闪电往外劈（参考图 W_Sona_Base_E_Zone_AOE_Glow、W_plasma）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink core (#FFFFFF, #FFE3FB, #FFC2F6), void violet (#2B1450, #5226A0, #8A55E6, #BFA2FF) and magenta (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5).
Effect: a VOID IMPACT, 6 frames: 1 a white-pink flash at the centre; 2 a violet shock ring bursting out and three short zig-zag lightning bolts; 3 the ring at 85% of the cell, magenta plasma inside it; 4 the ring breaking into arcs; 5 violet sparks; 6 specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `kaisa_fx_r_launch.png`：R 起跳爆发（她起跳的位置，地面），6 帧

猎手本能起跳：她起跳的地方炸开一团紫色的虚空能量和烟，地上一圈紫色的冲击环（参考图 R_side_flash、R_Smoke_01）。从斜上方看，地面是扁椭圆。约 28 格宽、18 格高，地面在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, void violet (#2B1450, #5226A0, #8A55E6, #BFA2FF), magenta (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5), a white-pink flash (#FFFFFF, #FFE3FB, #FFC2F6) and purple smoke (#2A1F46, #463970, #6D5EA2, #A99BD6).
Effect: a LAUNCH BURST on the ground (seen from above at an angle: flat, an ellipse twice as wide as tall), 6 frames: 1 a white-pink flash on the ground; 2 a violet shock ring spreading on the ground and a burst of magenta energy shooting up and to the RIGHT (the way she dashes); 3 the ring at its widest, purple smoke rolling; 4 smoke and sparks; 5 thin smoke; 6 faint smoke.
Layout: one horizontal row of 6 equal cells, each 14 wide to 9 tall, image size 2352x216 (each cell 392x252); the ground at 80% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `kaisa_fx_r_trail.png`：R 冲刺拖尾（她身上，朝右），4 帧循环

冲刺时身后的拖尾：一道往左（身后）拉长的紫色能量尾迹，边上缠着洋红色的电浆和细细的闪电（参考图 R_DashTrail、R_DashTrailSimple）。格子右边中间是她（不画人），尾迹往左拖。约 36 格长、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5), void violet (#2B1450, #5226A0, #8A55E6, #BFA2FF) and white-pink sparks (#FFFFFF, #FFE3FB, #FFC2F6).
Effect: a DASH TRAIL behind a character flying to the RIGHT (the character is not drawn: she is at the middle of the cell's RIGHT edge), 4 frames, a seamless loop: a long streak of violet energy stretching from the right edge to the left, wide (12 squares) near her and thinning to a point on the left, magenta plasma wisps along its edges and two thin violet lightning lines, flickering each frame.
Layout: one horizontal row of 4 equal cells, each 9 wide to 4 tall, image size 1728x192 (each cell 432x192); the character at the middle of each cell's right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `kaisa_fx_r_land.png`：R 落地（她身上，脚下），5 帧

落地：她脚下一圈紫色的冲击环和一团烟，几粒洋红色的火花往上溅。地面是扁椭圆。约 26 格宽、14 格高，地面在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, void violet (#2B1450, #5226A0, #8A55E6, #BFA2FF), magenta (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and purple smoke (#2A1F46, #463970, #6D5EA2, #A99BD6).
Effect: a LANDING IMPACT at a character's feet (seen from above at an angle: flat), 5 frames: 1 a white-pink flash on the ground; 2 a violet shock ring spreading on the ground, magenta sparks flying up; 3 the ring at its widest, a puff of purple smoke; 4 smoke; 5 faint smoke.
Layout: one horizontal row of 5 equal cells, each 13 wide to 7 tall, image size 1820x280 (each cell 364x196); the ground at 80% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `kaisa_fx_r_shield.png`：R 护盾（她身上，2 秒），12 帧

猎手本能的护盾：她周围一层紫色的电浆护壳（参考图 R_ShieldPlasmaShapes、R_ShieldFresnelRing），外缘亮洋红色，里面淡淡的紫色网纹（用隔格的点画，不要半透明），表面电浆流动；第 1–2 帧形成，3–10 帧保持（流动），11–12 帧碎开消失。格子中间是她（不画人，约 28×40 格）。约 30 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, magenta plasma (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5), void violet (#2B1450, #5226A0, #8A55E6, #BFA2FF) and white-pink highlights (#FFFFFF, #FFE3FB, #FFC2F6).
Effect: a PLASMA SHIELD round a character (not drawn: a 28x40-pixel figure in the middle, feet on the bottom row), 12 frames: 1-2 a shell forms from the feet up: an egg-shaped outline 2 squares thick in bright magenta with a white-pink highlight on its upper left; 3-10 holding: the outline steady, a sparse checker of violet specks (every other square) inside it so the figure stays visible, a few curved plasma streaks sliding round the shell (moving each frame); 11 the shell cracks into arcs; 12 the arcs fade.
Layout: two rows of 6 equal cells, each 3 wide to 4 tall, image size 1440x1280 (each cell 240x320, the feet on the bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `kaisa_fx_evolve.png`：进化（她身上），8 帧

活体武器进化：她脚下亮起紫色的光圈，一道紫白色的光柱从脚下往上冲过她的头顶（参考图 E_evolve_godlay、E_evolve_blast），光柱散开时四周落下洋红色的光点。约 28 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white-pink core (#FFFFFF, #FFE3FB, #FFC2F6), magenta (#4A0C63, #8E1FB8, #D23CF0, #F408EA, #FF9BF5) and violet (#2B1450, #5226A0, #8A55E6, #BFA2FF).
Effect: an EVOLUTION burst round a character (not drawn: a 28x40-pixel figure in the middle, feet 2 squares above the bottom), 8 frames: 1 a violet ring lights on the ground round the feet; 2-3 a column of white-pink and violet light rises from the ring through the figure and above its head; 4 the column at its tallest, short rays out of it; 5 it bursts into a ring of magenta sparks at head height; 6-7 the sparks fall gently; 8 a few specks.
Layout: one horizontal row of 8 equal cells, each 7 wide to 12 tall, image size 1680x2880 (each cell 210x360). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kaisa_fx_bolt` | view_projectiles `league_kaisa_bolt` | 12 × 5 |
| `kaisa_fx_q_missile` | view_projectiles `league_kaisa_q_missile`（6 发，进化后 12 发） | 10 × 6 |
| `kaisa_fx_w_bolt` | view_projectiles `league_kaisa_w_bolt` | 26 × 9 |
| `kaisa_fx_shot` | view_effects `league_kaisa_shot`（她身上，跟随） | 10 × 8 |
| `kaisa_fx_hit` | view_effects `league_kaisa_hit`（跟随） | 10 |
| `kaisa_fx_pl_stack` | view_effects `league_kaisa_pl_1`…`pl_4`（跟随目标，每命中一次播 1 秒） | 14 × 8 |
| `kaisa_fx_p_burst` | view_effects `league_kaisa_p_burst`（跟随） | 26 |
| `kaisa_fx_e_cast` | view_effects `league_kaisa_e_cast`（跟随） | 30 × 40 |
| `kaisa_fx_e_aura` | view_effects `league_kaisa_e_aura`（跟随，4 秒内每秒重播） | 26 × 36 |
| `kaisa_fx_e_invis` | view_effects `league_kaisa_e_invis`（跟随） | 28 × 40 |
| `kaisa_fx_q_pod` | view_effects `league_kaisa_q_cast`（Claude 把它放到两个翼舱的光眼上） | 12 |
| `kaisa_fx_q_hit` | view_effects `league_kaisa_q_hit`（跟随） | 14 |
| `kaisa_fx_w_charge` | view_effects `league_kaisa_w_charge`（跟随，放在炮口） | 14 × 12 |
| `kaisa_fx_w_muzzle` | view_effects `league_kaisa_w_muzzle`（不跟随：动作中途播放，跟随的话红色方会画反；放在炮口） | 20 × 14 |
| `kaisa_fx_w_hit` | view_effects `league_kaisa_w_hit`（跟随） | 22 |
| `kaisa_fx_r_launch` | view_effects `league_kaisa_r_launch`（不跟随，留在原地） | 28 × 18 |
| `kaisa_fx_r_trail` | view_effects `league_kaisa_r_trail`（跟随；大招第一个 tick 播放，冲刺前的 7 tick 是空帧） | 36 × 16 |
| `kaisa_fx_r_land` | view_effects `league_kaisa_r_land`（跟随） | 26 × 14 |
| `kaisa_fx_r_shield` | view_effects `league_kaisa_r_shield`（跟随） | 30 × 42 |
| `kaisa_fx_evolve` | view_effects `league_kaisa_evolve`（跟随） | 28 × 48 |

- 掌心闪光、W 蓄能 / 爆风按动作条出手帧量的掌心和炮口位置放；Q 的翼舱闪光放两份，在 Q 第 3 帧两个翼舱的洋红光眼上。
- 电浆弹、导弹、W 光束的出手点按出手帧的掌心 / 翼舱 / 炮口量，写进各自的 `y_offset`（只抬画面）；导弹从翼舱往下追向目标，斜着飞是对的；电浆弹和光束出手点要低（离站位点 8 格以内），否则看起来是歪的。
- 电浆标记 4 行分别导成 `pl_1`…`pl_4` 四个标签，各 1 秒；护盾 120 tick；E 光环每秒重播；R 拖尾在冲刺期间跟着她。
- 交回后先量平均亮度和最亮一成，和包里其他英雄比；Codex 给特效描的暗色外圈去掉。
