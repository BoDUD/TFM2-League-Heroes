# 傲之追猎者 雷恩加尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型和动作已定（`design/rengar_design.png`，41×40 格，8 倍）。
> - 大小对照 `design/rengar_size.png`：定稿造型放大 4 倍，脚底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/rengar_shots.png`：普攻砍中、飞扑落地、Q 下砸和上挑、E 甩出、W 咆哮、R 伏低那几帧的动作（4 倍），青色十字是脚下。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里雷恩加尔自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。颜色：**爪痕、刀光是金白色；凶残值满了的强化技能是红橙色；伪装是淡蓝灰的烟；R 的猎手之眼是红色；回血是绿色；彩蛋里卡兹克是紫色**。
> - **特效要亮**：以前魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。飞行的套索会转到飞行方向，所以朝右画、上下大致对称。
> - 特效照下面第 1–20 条和「所有特效图的规则」画，每张一个 PNG，文件名 `rengar_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`rengar_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「无形潜行」 | 挥刀爪砍；在草丛里 / 伪装着的时候下一次普攻从远处飞扑上去 | `rengar_fx_a_hit` · `rengar_fx_l_dust` · `rengar_fx_l_hit` · `rengar_fx_p_ready` |
| 凶残值 | 每放一个技能 / 飞扑一次攒 1 层，4 层满了下一个技能变强化 | `rengar_fx_f_stack` |
| Q「野蛮打击」（自动） | Q 冷却好后的下一次普攻变成跳起猛砸再上挑，之后几秒攻速变快；强化版更痛、攻速更快 | `rengar_fx_q_slam` · `rengar_fx_q_rip` · `rengar_fx_q_buff` · `rengar_fx_q_emp` |
| 技能 1 = W「战吼」 | 咆哮：伤害周围的敌人，给自己回血；强化版短时间不受控制 | `rengar_fx_w_roar` · `rengar_fx_w_heal` · `rengar_fx_w_emp` |
| 技能 2 = E「套索打击」 | 甩出套索，打中的敌人减速；强化版定身 | `rengar_fx_e_bola` · `rengar_fx_e_slow` · `rengar_fx_e_root` |
| 大招 = R「狩猎律动」 | 伪装消失、加速，盯上一个敌方英雄，从伪装里扑上去打出暴击 | `rengar_fx_r_smoke` · `rengar_fx_r_mark` · `rengar_fx_r_hit` |
| 彩蛋：宿敌卡兹克 | 第一次碰面两人头顶冒怒火；雷恩加尔第一次杀死卡兹克时头顶弹出卡兹克的头颅战利品 | `rengar_fx_k_meet` · `rengar_fx_t_trophy` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、刀光、火星、烟雾没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反；套索的石锤和战利品是实物，可以有自己的深色边）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 金白（爪痕、刀光、冲击）：`#FFFFFF`、`#FFF6D8`、`#FFE29A`、`#FFC24A`、`#F09A1E`、`#C86A10`、`#8A4208`；
  - 红橙（凶残满了的强化）：`#FFFFFF`、`#FFE0C8`、`#FFAA70`、`#FF6A3A`、`#E8361E`、`#B01810`、`#700A08`；
  - 骨色和皮绳（套索、骨牙）：`#FFFFFF`、`#F6E0B6`、`#D9A060`、`#A86A34`、`#6E4220`、`#3E2414`；
  - 尘土：`#FFFFFF`、`#EEE6D8`、`#D2C2A6`、`#A8967A`、`#7A6A54`；
  - 淡蓝灰（伪装烟雾）：`#FFFFFF`、`#E4E8F4`、`#B8C0DC`、`#8A92B8`、`#5A6290`、`#3A3E60`；
  - 红（猎手之眼）：`#FFFFFF`、`#FFD8C8`、`#FF8A60`、`#FF3A20`、`#C01408`；
  - 绿（回血）：`#FFFFFF`、`#ECFFE4`、`#BDF5A6`、`#7EDD68`、`#3FB44C`；
  - 紫（卡兹克）：`#FFFFFF`、`#E8D8FF`、`#B890F0`、`#8A58D8`、`#5A30A8`、`#341870`；
- **飞行的画面朝右画，而且上下大致对称**（`e_bola`）：游戏会把它转到飞行方向，往左飞时整张会上下翻过来。
- **挂在人身上和地上的画面左右对称**（除了 `e_bola` 全部），按每条写的站位画；命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人；光环只画外面一圈，不要盖住人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：W 咆哮半径约 20000，飞扑距离约 30000）。

### 1. `rengar_fx_a_hit.png`：普攻命中：刀爪划痕（目标身上），4 帧

弯刀和爪刃砍中：两道金白色的划痕交叉成一个 X，交点一下白光，迸出几颗金色火星（参考 Q_Slash_New 的爪痕、Talon 的火花）。左右对称，居中画。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a CLAW SLASH HIT, 4 frames: 1 a white flash 5 squares across; 2 two bright gold-white slash streaks 12 squares long crossing in an X through the middle, sparks flying out; 3 the streaks thinning to gold, sparks farther out; 4 two fading gold lines and a few sparks. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 224x224 (image 896x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `rengar_fx_l_dust.png`：飞扑起跳 / 落地扬起的尘土（脚下），4 帧

雷恩加尔蹬地扑出去、落下来时脚下扬起的一圈尘土：地上一个扁扁的尘土环往外散，几团小土块往两边飞。左右对称，从斜上方看的椭圆（宽是高的 2 倍多）。约 22 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a dust ramp (#FFFFFF, #EEE6D8, #D2C2A6, #A8967A, #7A6A54).
Effect: a DUST BURST on the ground, 4 frames: 1 a small flat puff of pale dust at the middle; 2 a ring of dust spreading out on the ground (an ellipse 16 x 5 squares), clods flying to both sides; 3 the ring at full size (20 x 7), thinner; 4 a few fading wisps. Left-right symmetric; seen from above at an angle.
Layout: one horizontal row of 4 equal cells, each 352x128 (image 1408x128) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `rengar_fx_l_hit.png`：飞扑落地抓击（目标身上），5 帧

从草丛 / 伪装里扑出来落地的那一抓：三道很大的金白色爪痕从上往下划过（中间一道，两边两道对称地斜着），一下白光，碎光往外迸（参考 Q_Slash_New 的三道爪痕）。左右对称，居中画。约 18 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a POUNCE CLAW STRIKE, 5 frames: 1 a white flash at the middle; 2 three big claw rakes slashing DOWN through the middle - one straight in the centre, two slanted mirror-wise on both sides - bright white-gold, 16 squares tall; 3 the rakes at full length, sparks bursting out sideways; 4 the rakes fading to amber, sparks farther out; 5 three faint lines. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 288x320 (image 1440x320) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `rengar_fx_p_ready.png`：被动「无形潜行」就绪：猎手之眼（头顶，循环），4 帧

能飞扑的时候（在草丛里 / 伪装着）：他头顶上方一只小小的金色猎手眼睛在发光、一闪一闪（参考 R_tar_vision_eye_glow 的眼形）。只画眼睛，不要画人，眼睛在格子上半部。左右对称。约 10 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a small LOOPING GLOWING HUNTER'S EYE, 4 frames, a seamless loop: an almond-shaped eye 8 squares wide and 4 tall, a white-gold glowing core with a slit pupil, two short gold glints at its corners; it pulses brighter and dimmer from frame to frame. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 160x96 (image 640x96) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `rengar_fx_f_stack.png`：凶残值 1–4 层（头顶），4 格各 1 帧

英雄联盟里雷恩加尔的凶残值是 4 格：头顶一排 4 颗小小的骨牙。第 1 格只亮 1 颗（金色），第 2 格亮 2 颗，第 3 格亮 3 颗，第 4 格 4 颗全亮、而且变成发光的红橙色（满了，下一个技能是强化的）。没亮的牙是暗的骨色。左右对称。约 14 格宽、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a ferocity ramp (#FFFFFF, #FFE0C8, #FFAA70, #FF6A3A, #E8361E, #B01810, #700A08) and a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208) and a bone ramp (#FFFFFF, #F6E0B6, #D9A060, #A86A34, #6E4220, #3E2414).
Effect: a FEROCITY BAR of four small fang shapes in a row (each fang 2 squares wide, 4 tall, pointing down, 1 square apart), 4 cells, each a still picture: cell 1 - the first fang lit gold-white, the other three dull dark bone; cell 2 - two lit; cell 3 - three lit; cell 4 - all four glowing bright red-orange with a white core and a faint red glow round the bar. Left-right symmetric bar.
Layout: one horizontal row of 4 equal cells, each 224x80 (image 896x80) (16 px a square here); the bar centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `rengar_fx_q_slam.png`：Q 野蛮打击：下砸的冲击（地上，目标脚下），5 帧

Q 跳起来猛砸下来的那一下：地上一圈金橙色的冲击，裂开几道亮的裂纹，碎石往两边飞。左右对称，从斜上方看的椭圆。约 24 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208) and a dust ramp (#FFFFFF, #EEE6D8, #D2C2A6, #A8967A, #7A6A54).
Effect: a GROUND SLAM IMPACT, 5 frames: 1 a bright white-gold flash on the ground at the middle; 2 a ring of gold light bursting out (an ellipse 14 x 6 squares), short bright cracks radiating; 3 the ring at full size (22 x 10), dust and pebbles thrown to both sides; 4 the ring fading to amber, the dust settling; 5 faint cracks. Left-right symmetric; seen from above at an angle.
Layout: one horizontal row of 5 equal cells, each 384x192 (image 1920x192) (16 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `rengar_fx_q_rip.png`：Q 上挑撕裂（目标身上），4 帧

Q 的第二下往上一挑：一道竖着的金白色刀光从下往上划过，顶端一下白光，碎光往上飞。左右对称，居中画。约 12 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a RISING SLASH, 4 frames: 1 a short bright streak at the bottom middle; 2 a vertical white-gold slash streak 18 squares tall sweeping UP through the middle, a flash at its top; 3 the streak at full length, sparks flying up and out; 4 the streak fading to amber. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x320 (image 768x320) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `rengar_fx_q_buff.png`：Q 攻速加成（脚下，循环），4 帧

Q 之后几秒攻速变快：他脚下一圈金色的小刀光在转（像几道短短的爪痕绕着脚转圈）。只画脚下的一圈，不要盖住人。左右对称。约 22 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a LOOPING RING OF SHORT GOLD CLAW STREAKS at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: 6 short bright streaks spaced round a flat ellipse on the ground (20 x 6 squares), moving a sixth of the way round each frame, brighter in front, a faint gold glow under them. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 352x128 (image 1408x128) (16 px a square here); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `rengar_fx_q_emp.png`：强化 Q（凶残满：身上红橙色的光，循环），4 帧

凶残满了放的强化 Q：他全身冒着红橙色的凶光，像一圈往上窜的火苗一样的光边绕着他。只画外面一圈光和往上飘的光点，**里面空着**，不要盖住人。左右对称。约 28 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a ferocity ramp (#FFFFFF, #FFE0C8, #FFAA70, #FF6A3A, #E8361E, #B01810, #700A08) and a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a LOOPING RED-ORANGE FEROCITY AURA round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: tongues of red-orange light licking upward round the rim of an upright oval 26 x 28 squares, white-orange at their tips, embers rising; the tongues shift from frame to frame. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 448x480 (image 1792x480) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `rengar_fx_w_roar.png`：W 战吼冲击波（地上，脚下），6 帧

W 一声咆哮：从他脚下炸开两圈金白色的冲击波环往外扩，环上一道道短的声波弧线（参考 W_Swirl_Mask、W_VerticalStreak_Mask 的形状）。左右对称，从斜上方看的椭圆（宽是高的 2 倍）。约 40 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a ROAR SHOCKWAVE on the ground, 6 frames: 1 a white-gold flash ring at the middle (an ellipse 8 x 4 squares); 2 the ring spreading (20 x 10), short curved sound-wave arcs on it; 3 a second ring following inside, the first at 30 x 15; 4 the first ring at full size (38 x 19), 2 squares thick, the second at 26 x 13; 5 both thinning and fading to amber; 6 faint broken arcs. Left-right symmetric; seen from above at an angle.
Layout: one horizontal row of 6 equal cells, each 320x160 (image 1920x160) (8 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `rengar_fx_w_heal.png`：W 回血（身上），5 帧

W 回血：胸口一下白绿色的光，一圈绿色的光点从身上冒出来往上飘（参考 W_Heal_Spark）。中间是人，不要画人。左右对称。约 18 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a heal ramp (#FFFFFF, #ECFFE4, #BDF5A6, #7EDD68, #3FB44C).
Effect: a HEAL ON A FIGURE (do NOT draw the figure), 5 frames: 1 a pale green-white flash at chest height (the middle of the cell); 2 green motes popping out round the body (an upright oval 16 x 22 squares); 3 the motes rising, small plus-shaped sparkles among them; 4 the motes higher and fading; 5 a few fading motes near the top. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 288x384 (image 1440x384) (16 px a square here); centered in every cell (the figure's chest at the middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `rengar_fx_w_emp.png`：强化 W（凶残满：不受控制，身上，循环），4 帧

凶残满了放的强化 W：他摆脱控制、短时间不受控制——全身一圈金红色的护身光边，光边上有几道往外崩开的碎光（像挣断了锁链）。只画外面一圈，**里面空着**，不要盖住人。左右对称。约 26 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a ferocity ramp (#FFFFFF, #FFE0C8, #FFAA70, #FF6A3A, #E8361E, #B01810, #700A08) and a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a LOOPING UNSTOPPABLE GLOW round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: a bright gold-red rim of light round an upright oval 24 x 28 squares, short shards flying off it like broken chain links, the rim pulsing from frame to frame. Left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 416x480 (image 1664x480) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `rengar_fx_e_bola.png`：E 套索打击：飞行的套索（朝右，循环），4 帧

E 甩出去的套索：两颗骨色的石锤（流星锤）用一根皮绳连着，绳子在空中旋转（每帧转四分之一圈），后面拖一道淡淡的金色风痕。朝右飞，**上下大致对称**。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a bone ramp (#FFFFFF, #F6E0B6, #D9A060, #A86A34, #6E4220, #3E2414) and a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a SPINNING BOLA flying to the RIGHT, 4 frames, a seamless loop: two round bone-coloured weights (3 squares each) joined by a 6-square leather cord, the pair spinning a quarter turn each frame round the middle point near the right end, a faint gold motion streak 4 squares long trailing to the LEFT; roughly symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 192x128 (image 768x128) (16 px a square here); the bola's middle on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `rengar_fx_e_slow.png`：E 减速：套索缠在腿上（目标脚下，循环），4 帧

被套索打中减速：皮绳缠在目标腿上（脚上方一圈），两颗骨色的石锤垂在两边晃。只画绳子和石锤，不要画人。左右对称。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a bone ramp (#FFFFFF, #F6E0B6, #D9A060, #A86A34, #6E4220, #3E2414).
Effect: a LOOPING BOLA TANGLED ROUND A FIGURE'S LEGS (do NOT draw the figure), 4 frames, a seamless loop: a leather cord wound round the shins as a flat loop (16 x 4 squares), two bone weights hanging at its left and right ends swinging a square in and out from frame to frame. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 288x128 (image 1152x128) (16 px a square here); the loop's middle at the middle of every cell (the shins). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `rengar_fx_e_root.png`：强化 E：定身（目标脚下，循环），4 帧

凶残满了的强化 E：套索死死勒住，皮绳发着红橙色的光，脚下一圈红光，石锤钉在地上两边。只画绳子、光和石锤，不要画人。左右对称。约 20 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a ferocity ramp (#FFFFFF, #FFE0C8, #FFAA70, #FF6A3A, #E8361E, #B01810, #700A08) and a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208) and a bone ramp (#FFFFFF, #F6E0B6, #D9A060, #A86A34, #6E4220, #3E2414).
Effect: a LOOPING ROOT: a glowing BOLA BINDING A FIGURE'S LEGS (do NOT draw the figure), 4 frames, a seamless loop: two tight loops of cord round the shins glowing red-orange with white-hot highlights, a flat red-orange ring of light on the ground round the feet (18 x 5 squares), the two bone weights pinned on the ground at the left and right; the glow pulses from frame to frame. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 320x192 (image 1280x192) (16 px a square here); the feet at the middle of every cell, 2 squares below the centre. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `rengar_fx_r_smoke.png`：R 伪装烟雾（脚下 / 身上），6 帧

R 开启伪装消失、或者从伪装里扑出来的那一下：一团淡蓝灰色的烟雾从他身上炸开再散掉（参考 P_CloudTxt06、z_mult 的云）。左右对称。约 28 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a smoke ramp (#FFFFFF, #E4E8F4, #B8C0DC, #8A92B8, #5A6290, #3A3E60).
Effect: a CAMOUFLAGE SMOKE PUFF, 6 frames: 1 a small pale flash at the middle; 2 a burst of round pale blue-grey smoke clouds puffing out to 16 squares; 3 the clouds at full size (26 x 22), billowing; 4 the clouds thinning, drifting up and out; 5 a few wisps; 6 the last faint wisps. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 448x384 (image 2688x384) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `rengar_fx_r_mark.png`：R 被猎杀标记：猎手之眼（目标头顶，循环），4 帧

被雷恩加尔的大招盯上的敌方英雄头顶：一只红色发光的猎手眼睛（英雄联盟 R 的那只眼，参考 R_tar_vision_eye_glow / eye_pulse），一闪一闪、往外冒红光。只画眼睛，左右对称。约 12 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from an eye ramp (#FFFFFF, #FFD8C8, #FF8A60, #FF3A20, #C01408).
Effect: a LOOPING GLOWING RED HUNTER'S EYE, 4 frames, a seamless loop: an almond-shaped eye 10 squares wide and 5 tall, a white-hot core and a slit pupil, a red glow round it, two short red flares at its corners; it pulses bigger and smaller from frame to frame. Left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 192x128 (image 768x128) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `rengar_fx_r_hit.png`：R 扑杀暴击（目标身上），6 帧

大招从伪装里扑到目标身上的暴击：一下白光，三道巨大的红橙色爪痕（中间一道，两边对称斜着）从上往下撕开，碎光和血红的火星往四周迸。左右对称，居中画。约 24 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a ferocity ramp (#FFFFFF, #FFE0C8, #FFAA70, #FF6A3A, #E8361E, #B01810, #700A08) and a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a HUGE CRITICAL CLAW STRIKE, 6 frames: 1 a white flash 8 squares across; 2 three huge red-orange claw rakes slashing DOWN through the middle (one straight in the centre, two slanted mirror-wise), white-hot cores, 22 squares tall; 3 a burst of red-orange shards flying out all round; 4 the rakes at full length, shards farther out; 5 the rakes fading to dark red; 6 three faint lines and embers. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 384x384 (image 2304x384) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `rengar_fx_t_trophy.png`：彩蛋：卡兹克的头颅（战利品，头顶弹出），6 帧

雷恩加尔第一次亲手杀死宿敌卡兹克（英雄联盟里那只紫色的虚空螳螂）时，头顶弹出一个战利品：卡兹克的头（紫色甲壳、两只发光的眼睛、两边的口器）挂在一串骨牙项链上，周围一圈金色的光点，弹出来闪一下再慢慢消失。左右对称。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a void ramp (#FFFFFF, #E8D8FF, #B890F0, #8A58D8, #5A30A8, #341870), a bone ramp (#FFFFFF, #F6E0B6, #D9A060, #A86A34, #6E4220, #3E2414) and a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: a TROPHY POPPING UP, 6 frames: 1 a gold sparkle at the middle; 2 the trophy pops up: a small purple insect-like head (a chitin crest, two glowing pale-violet eyes, two mandibles at the sides; 8 squares wide) hanging on a short string of bone fangs, gold sparkles round it; 3 the trophy brightest, a gold ring flashing behind it; 4 the same, the sparkles farther out; 5 the trophy fading; 6 a few gold sparkles. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 224x224 (image 1344x224) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `rengar_fx_k_meet.png`：彩蛋：狮子狗与螳螂碰面（头顶的怒火标记），5 帧

雷恩加尔和卡兹克第一次在场上碰面：头顶冒出一个红色的「怒」字青筋标记（漫画里生气的那个十字形），一下炸开带几颗金色火星，再消失。左右对称。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, sparks, smoke or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a ferocity ramp (#FFFFFF, #FFE0C8, #FFAA70, #FF6A3A, #E8361E, #B01810, #700A08) and a gold ramp (#FFFFFF, #FFF6D8, #FFE29A, #FFC24A, #F09A1E, #C86A10, #8A4208).
Effect: an ANGER MARK POPPING, 5 frames: 1 a small red spark at the middle; 2 a bold red anime anger-vein mark (four curved strokes meeting in a cross, 9 squares across) pops up, gold sparks round it; 3 the mark biggest and brightest, a white core on each stroke; 4 the mark shaking a square, sparks farther out; 5 the mark fading. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 192x192 (image 960x192) (16 px a square here); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `rengar_fx_a_hit` | view_effects `league_rengar_a_hit`（跟随，画在人物上面） | 14 |
| `rengar_fx_l_dust` | view_effects `league_rengar_l_dust`（不跟随，画在人物下面；起跳和落地各一次） | 22 × 8 |
| `rengar_fx_l_hit` | view_effects `league_rengar_l_hit`（跟随，画在人物上面；被动飞扑落地那一下） | 18 × 20 |
| `rengar_fx_p_ready` | view_buffs `league_rengar_p_ready`（循环，跟随；下一次普攻会飞扑的时候一直在） | 10 × 6 |
| `rengar_fx_f_stack` | view_buffs `league_rengar_f1`…`f4`（每层用一格，跟随，在头顶） | 14 × 5 |
| `rengar_fx_q_slam` | view_effects `league_rengar_q_slam`（不跟随，画在人物下面） | 24 × 12 |
| `rengar_fx_q_rip` | view_effects `league_rengar_q_rip`（跟随，画在人物上面；Q 的第二下） | 12 × 20 |
| `rengar_fx_q_buff` | view_buffs `league_rengar_q_buff`（循环，跟随，画在人物下面；Q 之后 3 秒攻速） | 22 × 8 |
| `rengar_fx_q_emp` | view_buffs `league_rengar_q_emp`（循环，跟随，画在人物上面；强化 Q 的攻速期间） | 28 × 30 |
| `rengar_fx_w_roar` | view_effects `league_rengar_w_roar`（不跟随，画在人物下面） | 40 × 20 |
| `rengar_fx_w_heal` | view_effects `league_rengar_w_heal`（跟随，画在人物上面） | 18 × 24 |
| `rengar_fx_w_emp` | view_buffs `league_rengar_w_emp`（循环，跟随，画在人物上面；1.5 秒） | 26 × 30 |
| `rengar_fx_e_bola` | view_projectiles `league_rengar_e_bola`（循环，朝飞行方向转） | 12 × 8 |
| `rengar_fx_e_slow` | view_buffs `league_rengar_e_slow`（循环，跟随，画在人物上面） | 18 × 8 |
| `rengar_fx_e_root` | view_buffs `league_rengar_e_root`（循环，跟随，画在人物上面） | 20 × 12 |
| `rengar_fx_r_smoke` | view_effects `league_rengar_r_smoke`（不跟随，画在人物上面；开 R 隐身和扑出去的时候） | 28 × 24 |
| `rengar_fx_r_mark` | view_buffs `league_rengar_r_mark`（循环，跟随，在目标头顶） | 12 × 8 |
| `rengar_fx_r_hit` | view_effects `league_rengar_r_hit`（跟随，画在人物上面；大招扑上去那一下） | 24 × 24 |
| `rengar_fx_t_trophy` | view_effects `league_rengar_t_trophy`（跟随，在他头顶；第一次杀死卡兹克时） | 14 × 14 |
| `rengar_fx_k_meet` | view_effects `league_rengar_k_meet`（跟随，在头顶；两人第一次碰面时，两边都放） | 12 × 12 |

- 刀光挥砍的方向性画面不做成特效：动作帧里已经有挥刀的姿势；命中特效都左右对称。
- `l_dust`、`q_slam`、`w_roar`、`r_smoke` 是地上 / 脚下的画面：放在 ViewEffect 里（不随飞行转），不要挂在 RangeProjectile 的 view 上（红色方会倒过来，蕾欧娜的教训）。
- `f_stack` 一张图四格：每层凶残值的 view_buffs 用其中一格（f1…f4）。
- 清掉 Codex 给光描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
