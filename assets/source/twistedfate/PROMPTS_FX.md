# 卡牌大师 崔斯特：给 Codex 的特效提示词（第 3 步）

> **这一份是 29 张特效图。** 造型和动作已定（`design/twistedfate_design.png`，8 倍，41 行）。
> - 大小对照 `design/twistedfate_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，右边是原版赌徒。崔斯特 24×41 格。每条写的大小都是游戏像素（格）。
> - `design/twistedfate_shots.png`：普攻第 4 帧、Q 第 4 帧（右手扔牌）和大招两帧的定稿动作（4 倍），青色十字是手或脚下的位置（导入时 Claude 把特效放到这里）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里崔斯特自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（普攻和 E、被动骰子、W 的三种牌、W 的命中、Q、R），只在本地用，不要提交。颜色和英雄联盟一样：**蓝牌白蓝、红牌红橙火焰、黄牌金黄带尖刺；普攻和 Q 是紫色牌背的牌拖着淡紫白的光；E 是洋红紫；R 的命运之眼和传送门是金色**。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **牌和骰子在游戏尺寸很小（牌约 5×7 格）**：三种牌一定要靠颜色一眼分清（蓝、红、金黄），骰子的点数要看得清（点是 1 格的深色方块）。
> - 特效照下面第 1–29 条和「所有特效图的规则」画，每张一个 PNG，文件名 `twistedfate_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**（动作条那一轮用代码拼的手臂和腿被用户否了）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`twistedfate_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + E「卡牌骗术」 | 扔牌普攻；每第 4 次普攻是强化牌，多一段法术伤害 | `twistedfate_fx_a_card` · `twistedfate_fx_a_card_e` · `twistedfate_fx_a_hit` · `twistedfate_fx_e_cast` · `twistedfate_fx_e_hit` |
| 被动「灌铅骰子」 | 每次击杀，头顶上抛一颗骰子，按点数加一点法强（死了清空） | `twistedfate_fx_dice_roll` · `twistedfate_fx_dice_faces` · `twistedfate_fx_dice_out` |
| 技能 2 = W「选牌」 | 头顶上蓝、红、黄三张牌轮流换，选中一张后下一次普攻扔出：蓝牌伤害高并返还冷却，红牌范围伤害并减速，黄牌眩晕 | `twistedfate_fx_w_show` · `twistedfate_fx_w_blue` · `twistedfate_fx_w_red` · `twistedfate_fx_w_gold` · `twistedfate_fx_wb_card` · `twistedfate_fx_wr_card` · `twistedfate_fx_wg_card` · `twistedfate_fx_wb_hit` · `twistedfate_fx_wr_hit` · `twistedfate_fx_wr_burst` · `twistedfate_fx_wr_slow` · `twistedfate_fx_wg_hit` |
| 技能 1 = Q「万能牌」 | 扔出一条直线飞行的牌带（三张牌），穿过路上的所有敌人 | `twistedfate_fx_q_cast` · `twistedfate_fx_q_cards` · `twistedfate_fx_q_hit` |
| 大招 = R「命运」+「传送之门」 | 所有敌方英雄头上出现命运之眼；引导 1.5 秒后传送到队友正在打的远处敌人身边，落地扔一张黄牌 | `twistedfate_fx_r_seen` · `twistedfate_fx_r_cast` · `twistedfate_fx_r_gate` · `twistedfate_fx_r_dest` · `twistedfate_fx_r_out` · `twistedfate_fx_r_in` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、火焰、拖尾、星点没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。只有牌和骰子是物体，有 1 格深色描边（`#2A1E14`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 蓝牌：`#FFFFFF`、`#D6ECFF`、`#8CC4FF`、`#4A8CFF`、`#2456D6`、`#142E80`；
  - 红牌（火焰）：`#FFFFFF`、`#FFD6C8`、`#FF8A6A`、`#F03C30`、`#B01824`、`#5C0C14`；
  - 黄牌、命运之眼、传送门：`#FFFFFF`、`#FFF4BE`、`#FFD84E`、`#F2B21E`、`#C07A10`、`#6B400A`；
  - 紫色牌背、拖尾、E：`#FFFFFF`、`#F4DEFF`、`#D2A4FF`、`#A468F0`、`#7034C8`、`#3A1A70`；
  - 牌面纸色（牌、骰子）：`#FFFFFF`、`#F4EEDC`、`#D6C9A4`、`#9C8A62`；
- **飞行的牌朝右画，而且上下对称**（`a_card`、`a_card_e`、`wb_card`、`wr_card`、`wg_card`、`q_cards`）：游戏会把它转到出招方向，朝左时整张会上下翻转，所以里面不要有分上下的东西（牌在翻转，正反面交替正好）。
- **从手上发出的特效朝右画，起点在格子左边的中点**（`e_cast`、`q_cast`）；画在崔斯特身上的大招画面（`r_cast`、`r_gate`、`r_out`、`r_in`）按每条写的站位画，脚在格子底部往上 8 格的中间。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上或头顶上的循环画面（`wr_slow`、`r_seen`、`w_show`、`w_blue`、`w_red`、`w_gold`、骰子）左右对称或不分左右，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（29 张）

29 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 牌带宽 18000、红牌爆炸半径 25000）。

### 1. `twistedfate_fx_a_card.png`：普攻飞出去的牌（飞行中循环），4 帧

普攻扔出的一张牌：紫色牌背的小牌在空中翻转（正面、侧面、背面、侧面），后面拖一小段淡紫白色的光（参考 BA_Cards、Z_CardBackTXT、BA_FlameHead、Trail_2）。牌是物体，有 1 格深色描边；光没有描边。上下对称。约 16 格长、8 格高（牌约 7 × 5 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a FLYING PLAYING CARD moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a small playing card (5 squares wide, 7 tall, or lying 7 wide and 5 tall when flying), cream paper with a thin gold rim and a 1-square dark outline, its back violet with a pale star; it flips as it flies (1 face up, 2 edge-on as a thin bar, 3 the violet back, 4 edge-on); a short pale violet-white light streak 8 squares long trails behind it to the LEFT.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the card at the RIGHT half, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `twistedfate_fx_a_card_e.png`：E「卡牌骗术」第 4 下的强化牌（飞行中循环），4 帧

每第 4 次普攻扔出的强化牌：比普通牌大一点，牌身发出洋红紫色的光，后面拖一道更长更亮的洋红紫色光带，带几颗星点（参考 common_cardglows、BA_Cards 粉色牌、Q_30）。牌有描边，光没有。上下对称。约 22 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62) and a violet-magenta ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: an EMPOWERED FLYING CARD moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a small playing card (5 squares wide, 7 tall, or lying 7 wide and 5 tall when flying), cream paper with a thin gold rim and a 1-square dark outline, wrapped in a bright magenta-violet glow 2 squares thick; it flips as it flies (face, edge, back, edge); a bright magenta-violet streak 14 squares long trails behind it to the LEFT with 3 small white star sparks.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the card at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `twistedfate_fx_a_hit.png`：普攻打中（目标身上），4 帧

普攻的牌打中：一下白紫色的闪光，几片很小的牌碎片和星点往外飞（参考 BA_Tar_impact、Hit_01、BA_flash_01）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a CARD HIT, 4 frames: 1 a white flash with a pale violet rim; 2 a small four-pointed star of violet-white light 10 squares across, 4 tiny violet card shards flying out; 3 the star fading, shards further out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `twistedfate_fx_e_cast.png`：E 第 4 下出手：手上的洋红光（施法者身上），4 帧

第 4 次普攻出手时，崔斯特甩出牌的右手前面一团洋红紫色的光炸开，三张小牌像扇子一样一闪（参考 common_cardglows、W_swirlBurst）。朝右画：手在格子左边中点。约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a CAST FLASH at a hand, pointing RIGHT, 4 frames: 1 a magenta-white star at the LEFT MIDDLE of the cell (the hand); 2 three small playing cards (with dark outlines) fan out to the right from that point in a magenta-violet burst; 3 the cards fade, the burst spreads to the right with 4 sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal 4:3 cells, image size 1024x192 (each cell 256x192); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `twistedfate_fx_e_hit.png`：E 强化牌打中（目标身上），5 帧

强化牌打中：比普攻大的洋红紫色爆开，中间白色闪光，一圈牌的碎片和星星往外飞（参考 common_tf_card_buff_rgb、W_Impact、Hit_03）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet-magenta ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a MAGIC CARD BURST, 5 frames: 1 a white flash; 2 a round burst of magenta-violet light with a white core, 6 card shards and star sparks flying outward; 3 the burst at full size (16 squares), a thin violet ring; 4 the light breaks into violet wisps; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `twistedfate_fx_dice_roll.png`：被动「灌铅骰子」：头顶上翻滚的骰子（击杀时出现），5 帧

崔斯特击杀后头顶上方抛起一颗金边白骰子，在空中翻滚落下（参考 Spark_Star、common_Flare-Sun_12）。骰子是物体，有 1 格深色描边，约 8 格大；带几颗金色的闪光。约 12 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62) for the die and a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) for the sparkle.
Effect: a TUMBLING DIE in the air, 5 frames: a white six-sided die with a thin gold rim and a 1-square dark outline, about 8 squares across, drawn as a small cube seen from slightly above (front face, top face lit); 1 the die high at the top of the cell, a gold sparkle; 2-4 it tumbles down to the middle, turning a quarter turn each frame (pips blurred into dots), gold sparks trailing; 5 it lands at the middle showing its front face (blank pips there - the result is drawn separately).
Layout: one horizontal row of 5 equal 6:7 cells, image size 1280x298 (each cell 256x298); the die's resting place in the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `twistedfate_fx_dice_faces.png`：骰子停下的六个点数（头顶上，1–6 各一格），6 格

骰子停下后亮出的点数，每格一个面：1 点、2 点……6 点，从左到右。和 dice_roll 最后一帧同一个骰子、同一个位置，前面那一面是点数。点数一定要在游戏尺寸看得清：点是深色的方块（1 点在中间是红色），骰子周围一圈淡金色的光（参考 common_glow-soft）。约 10 × 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62) for the die, red #F03C30 for the one pip, dark #2A1E14 for the other pips and a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) for the glow.
Effect: SIX RESTING DICE FACES, one per cell, left to right showing 1, 2, 3, 4, 5, 6 pips: the same white cube die as before (8 squares across, a thin gold rim, a 1-square dark outline, seen from slightly above), its FRONT face toward us with the pips as 1-square dark dots in the usual dice layout (the single pip of the 1 is red and 2x2), a soft pale gold glow 2 squares round the die.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the die in the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `twistedfate_fx_dice_out.png`：骰子消失（头顶上），3 帧

骰子散成金色的星点消失（参考 R_StardustMote）。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a DIE VANISHING, 3 frames: 1 the white die (as in dice_faces, pips gone) flashes gold; 2 it breaks into 8 gold sparkles spreading out; 3 a few fading sparkles.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `twistedfate_fx_w_show.png`：W 选牌：头顶上轮换的蓝 / 红 / 黄牌（三格，每格一种）

选牌时头顶上方飘着一张牌，蓝、红、黄三种轮流换（游戏里每 0.5 秒换一张）。三格从左到右：蓝牌、红牌、黄牌。牌面要在游戏尺寸一眼分清颜色：蓝牌是深蓝色牌面中间一个白色的水滴标志，红牌是红色牌面中间一把小剑，黄牌是金黄色牌面中间一个链环（参考 Z_BlueCardTXT、Z_RedCardTXT、W_YellowCard、BA_Cards）。牌有描边，牌周围一圈同色的淡光。约 10 格宽、13 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8CFF, #2456D6, #142E80), a red ramp (#FFFFFF, #FFD6C8, #FF8A6A, #F03C30, #B01824, #5C0C14), a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: THREE FLOATING CARDS, one per cell: 1 a BLUE card (deep blue face, a white teardrop emblem in the middle), 2 a RED card (red face, a small white-gold sword emblem), 3 a GOLD card (golden-yellow face, a dark chain-link emblem); each card 7 squares wide and 10 tall, upright, a thin gold rim and a 1-square dark outline, a soft glow of its own colour 2 squares round it.
Layout: one horizontal row of 3 equal 10:13 cells, image size 768x333 (each cell 256x333); the card in the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `twistedfate_fx_w_blue.png`：W 锁定蓝牌：头顶上燃着蓝光的牌（循环），4 帧

选中蓝牌后，下一次普攻前头顶上一直亮着这张蓝牌：牌周围燃着明亮的白蓝色光焰，往上飘（参考 W_BlueCard_Point、common_tf_card_blue_hit_rgb、W_Fire_Trail_Up）。和 w_show 的蓝牌同一张牌，只是更亮。4 帧无缝循环。约 14 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8CFF, #2456D6, #142E80) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a LOCKED BLUE CARD floating, 4 frames, a seamless loop: the blue card of w_show (7x10 squares, white teardrop emblem, dark outline) upright in the lower middle of the cell, wrapped in bright white-blue flame-like light licking upward 4-6 squares above it, 3 blue sparks rising; the flames flicker each frame.
Layout: one horizontal row of 4 equal 7:9 cells, image size 1024x329 (each cell 256x329); the card's middle 7 squares above the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `twistedfate_fx_w_red.png`：W 锁定红牌：头顶上燃着红焰的牌（循环），4 帧

选中红牌：头顶上的红牌燃着红橙色的火焰往上冒（参考 W_RedCard_Simplified、W_Flames、W_Fire_Trail_Up）。和 w_show 的红牌同一张。4 帧无缝循环。约 14 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red ramp (#FFFFFF, #FFD6C8, #FF8A6A, #F03C30, #B01824, #5C0C14) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a LOCKED RED CARD floating, 4 frames, a seamless loop: the red card of w_show (7x10 squares, sword emblem, dark outline) upright in the lower middle of the cell, bright red-orange flames with yellow-white tips rising 5-7 squares above it, 3 embers; the flames flicker each frame.
Layout: one horizontal row of 4 equal 7:9 cells, image size 1024x329 (each cell 256x329); the card's middle 7 squares above the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `twistedfate_fx_w_gold.png`：W 锁定黄牌：头顶上闪着金光的牌（循环），4 帧

选中黄牌（金牌）：头顶上的黄牌放出金色的光芒，周围一圈尖刺状的金光在闪（参考 W_YellowCard、W_Spikes、common_tf_card_gold_hit_rgb）。和 w_show 的黄牌同一张。4 帧无缝循环。约 14 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a LOCKED GOLD CARD floating, 4 frames, a seamless loop: the gold card of w_show (7x10 squares, chain-link emblem, dark outline) upright in the lower middle of the cell, a halo of sharp golden spikes round it (8 spikes, alternating long and short each frame) and white-gold glints; bright, it must read as the strongest of the three.
Layout: one horizontal row of 4 equal 7:9 cells, image size 1024x329 (each cell 256x329); the card's middle 7 squares above the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `twistedfate_fx_wb_card.png`：W 扔出去的蓝牌（飞行中循环），4 帧

扔出去的蓝牌：蓝色牌面的牌在空中翻转，后面拖一道白蓝色的光（参考 W_Mis_Trail、common_tf_card_mis）。牌有描边，光没有。上下对称。约 20 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8CFF, #2456D6, #142E80) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a FLYING BLUE CARD moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: the blue card (blue face, white emblem, dark outline, lying 7 wide and 5 tall) flipping as it flies (face, edge, back, edge), wrapped in white-blue glow, a bright white-blue streak 12 squares long behind it to the LEFT.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the card at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `twistedfate_fx_wr_card.png`：W 扔出去的红牌（飞行中循环），4 帧

扔出去的红牌：红色牌面的牌在空中翻转，后面拖一道红橙色的火焰（参考 W_Mis_Trail、W_Flames）。上下对称。约 20 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red ramp (#FFFFFF, #FFD6C8, #FF8A6A, #F03C30, #B01824, #5C0C14) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a FLYING RED CARD moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: the red card (red face, sword emblem, dark outline, lying 7 wide and 5 tall) flipping as it flies, a trail of red-orange flame 12 squares long behind it to the LEFT with yellow-white tips.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the card at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `twistedfate_fx_wg_card.png`：W 扔出去的黄牌（飞行中循环），4 帧

扔出去的黄牌：金黄色牌面的牌在空中翻转，后面拖一道金色的光和尖尖的星点（参考 W_Mis_Trail、W_Spikes）。上下对称。约 20 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a FLYING GOLD CARD moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: the gold card (golden face, chain-link emblem, dark outline, lying 7 wide and 5 tall) flipping as it flies, a bright golden streak 12 squares long behind it to the LEFT with 3 sharp white-gold star glints.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the card at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `twistedfate_fx_wb_hit.png`：W 蓝牌打中（目标身上），5 帧

蓝牌打中：一大团白蓝色的光炸开，像水花一样溅出蓝色的光点（参考 common_tf_card_blue_hit_rgb、W_Impact、W_Cracks_Flash）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue ramp (#FFFFFF, #D6ECFF, #8CC4FF, #4A8CFF, #2456D6, #142E80).
Effect: a BLUE CARD BURST, 5 frames: 1 a white flash; 2 a round splash of white-blue light 14 squares across, 8 blue droplets flying out; 3 the splash at full size with a thin bright ring, droplets further out; 4 breaking into blue wisps; 5 fading droplets.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `twistedfate_fx_wr_hit.png`：W 红牌打中（每个被溅到的目标身上），4 帧

红牌溅到的每个敌人身上：一小团红橙色的火（参考 common_tf_card_red_hit_rgb、W_Flames）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red ramp (#FFFFFF, #FFD6C8, #FF8A6A, #F03C30, #B01824, #5C0C14).
Effect: a SMALL FIRE HIT, 4 frames: 1 a yellow-white flash; 2 a burst of red-orange flame tongues 10 squares across; 3 the flames rising and thinning; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `twistedfate_fx_wr_burst.png`：W 红牌的范围爆炸（地面上，不跟随），6 帧

红牌在打中的地方炸开一圈：地上一个红色的火焰圆（从斜上方看是扁椭圆，宽是高的 2 倍，范围半径约 25 格），圈边上一圈火苗往上冒，中间一张红牌一闪（参考 W_RedCard_Simplified、W_Spikes、Shockwave、W_swirlBurst）。约 50 格宽、30 格高（地上 50 × 25 的椭圆加上往上冒的火）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red ramp (#FFFFFF, #FFD6C8, #FF8A6A, #F03C30, #B01824, #5C0C14) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a FIRE BLAST ON THE GROUND seen from above at an angle, 6 frames: 1 a red card flashes at the center; 2 a ring of red-orange fire expands from the center over a flattened ellipse twice as wide as tall (50 squares wide); 3 the ring at the ellipse's edge, flame tongues rising 6 squares from it, the center a bright yellow-white glow; 4 the flames taller and ragged, embers; 5 the ring breaks into separate flames; 6 fading embers and red smoke.
Layout: one horizontal row of 6 equal 25:18 cells, image size 3000x360 (each cell 500x360); the ellipse's center 7 squares (56 px) above the bottom of every cell, horizontally centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `twistedfate_fx_wr_slow.png`：W 红牌减速（目标脚下，循环），4 帧

被红牌减速的敌人脚下：一圈暗红色的光，带几簇小火苗，慢慢转（参考 W_Flames）。中间是人，不要画人。左右对称，4 帧无缝循环。约 18 格宽、7 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red ramp (#FFFFFF, #FFD6C8, #FF8A6A, #F03C30, #B01824, #5C0C14).
Effect: a SLOW MARK at a figure's feet (do NOT draw the figure; symmetric left and right), 4 frames, a seamless loop: a ring of dim red glow on the ground round the feet (a flattened ellipse twice as wide as tall) with 4 small red-orange flame tongues on it, the tongues shifting a quarter of the way round each frame.
Layout: one horizontal row of 4 equal 5:2 cells, image size 2560x256 (each cell 640x256); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `twistedfate_fx_wg_hit.png`：W 黄牌打中：眩晕（目标身上），5 帧

黄牌打中：一个很亮的金色尖刺星形炸开（英雄联盟黄牌的眩晕就是这个刺星），中间白色闪光，几颗金星往外飞（参考 W_Spikes、common_tf_card_gold_hit_rgb、Q_30、W_YellowCard）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A).
Effect: a GOLDEN STUN BURST, 5 frames: 1 a white flash; 2 a sharp golden star of 10 long spikes bursts out, 16 squares across, a white-gold core; 3 the star at full size, 4 small gold stars flying out; 4 the spikes shorten, a thin gold ring; 5 fading gold glints.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `twistedfate_fx_q_cast.png`：Q 出手：手上的牌扇（施法者身上），4 帧

Q「万能牌」出手的一瞬间：右手前面三张牌像扇子一样张开往右甩出去，带一圈淡紫白色的光（参考 Q_30、BA_flash_01、Z_CardBackTXT）。朝右画：手在格子左边中点。约 18 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a FAN OF THREE CARDS thrown to the RIGHT from a hand, 4 frames: 1 a white-violet star at the LEFT MIDDLE of the cell (the hand); 2 three violet-backed playing cards (dark outlines) fan out from that point - one straight right, one up-right, one down-right - in a pale violet flash; 3 the cards further out, fading; 4 fading sparks.
Layout: one horizontal row of 4 equal 9:7 cells, image size 1152x224 (each cell 288x224); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `twistedfate_fx_q_cards.png`：Q 飞出去的三张牌（牌带），6 帧

Q 飞出去的是一条牌带（判定是一条直线，宽约 18 格）：画面是三张紫背的牌一起往右飞，中间一张直飞，上下两张慢慢往外散开，每张牌后面拖一道淡紫白色的光（参考 Q_30、Trail_2、BA_FlameHead、Z_CardBackTXT）。牌有描边，光没有。上下对称。约 32 格长、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: THREE FLYING CARDS moving to the RIGHT, 6 frames, SYMMETRIC above and below the middle line: three violet-backed playing cards (each lying 7 wide and 5 tall, dark outline) at the RIGHT end of the cell - one on the middle line, one above and one below it; frame by frame the upper and lower cards drift further apart (from 6 to 13 squares off the middle line), all three flipping as they fly (face, edge, back...); each card trails a pale violet-white light streak to the LEFT that grows from 6 to 18 squares long.
Layout: one horizontal row of 6 equal 128:81 cells, image size 3072x324 (each cell 512x324); the middle card on the middle line, at the RIGHT end, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `twistedfate_fx_q_hit.png`：Q 牌打中（目标身上），4 帧

Q 的牌打中：一下白紫色闪光和一张碎开的牌（参考 Hit_01、BA_Tar_impact）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a CARD STRIKE, 4 frames: 1 a white-violet flash; 2 a sharp four-pointed star of violet-white light 12 squares across, a card broken into 3 violet shards; 3 the shards flying apart, the star fading; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `twistedfate_fx_r_seen.png`：R「命运」：敌方英雄头上的命运之眼（循环），4 帧

开大后所有敌方英雄头上出现一只金色的眼睛（英雄联盟命运的标记）：尖角的金色眼眶，中间一颗发光的眼珠，慢慢一明一暗（参考 BA_R_Eye、BA_R_EyeCenter、BA_R_EyeGlow、R_GlassShape_Back）。要在游戏尺寸认得出是「眼睛」。4 帧无缝循环。约 12 格宽、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) and red #F03C30 / dark #2A1E14 for the pupil.
Effect: a GLOWING EYE MARK, 4 frames, a seamless loop: an almond-shaped eye 11 squares wide and 7 tall with a sharp golden rim (pointed corners left and right, a small spike above and below), a dark pupil with a red-orange glowing core in the middle, a thin pale-gold glow round it that brightens and dims over the loop.
Layout: one horizontal row of 4 equal 4:3 cells, image size 1024x192 (each cell 256x192); the eye in the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 25. `twistedfate_fx_r_cast.png`：R「命运」施放（施法者身上），7 帧

开大的一瞬间：崔斯特身边一圈金白色的光往外扩，一叠牌往上撒开，头顶上方一只大眼睛一闪（参考 BA_R_Eye、R_LensFlare、R_Recall_Wings_Pop_BurstRing、Z_CardBackTXT）。中间是人，不要画人。脚在格子底部往上 8 格的中间。约 56 格宽、56 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A), a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a FATEFUL BURST round a figure (do NOT draw the figure; leave its place empty), 7 frames: 1 a white-gold flash at the figure's chest; 2 a flat gold shock ring on the ground round the feet (an ellipse twice as wide as tall) and 8 cards flung up and out in a fan; 3 the ring wider, the cards higher, a big golden eye (as r_seen, 20 squares wide) opens above the head; 4 the eye fully open and bright, golden rays; 5 the eye closes, the cards spinning down; 6 the ring at the cell's edge, fading; 7 a few gold glints.
Layout: one horizontal row of 7 equal square cells, image size 3584x512 (each cell 512x512); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 26. `twistedfate_fx_r_gate.png`：R 传送之门：引导时身边的金色传送门（施法者身上，1.5 秒），8 帧

引导传送的 1.5 秒：崔斯特脚下一圈金色的光圈，几张牌围着他转，金色的光点往上飘，身上罩着一层淡金色的光（参考 Z_TeleportCard、R_GlassShape、R_Recall_Wings_Pop_BurstRing、R_StardustMote）。中间是人，不要画人。第 1–2 帧出现，3–8 帧无缝循环。脚在格子底部往上 8 格的中间。约 44 格宽、50 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a TELEPORT GATE round a figure (do NOT draw the figure; leave its place empty), 8 frames: 1 a gold ring appears on the ground round the feet (an ellipse twice as wide as tall, 40 squares wide); 2 a tall pale-gold light column rises round the figure's place, 5 cards appear round it; 3-8 (a seamless loop) the 5 cards circle round the figure (in front and behind, a sixth of a turn per frame), gold motes rise in the column, the ring pulses.
Layout: one horizontal row of 8 equal 22:25 cells, image size 3520x500 (each cell 440x500); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 27. `twistedfate_fx_r_dest.png`：R 传送目的地的金色标记（地面上，1.5 秒），6 帧

传送的目的地：地上一个金色的圆（从斜上方看是扁椭圆，宽是高的 2 倍），中间一张发光的牌的图案，圈慢慢转（参考 Z_TeleportCard、R_Mark_distort_RGBA、Shockwave）。第 1–2 帧出现，3–6 帧无缝循环。约 40 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A).
Effect: a GOLD SIGIL ON THE GROUND seen from above at an angle (a flattened ellipse twice as wide as tall), 6 frames: 1 a gold point at the center; 2 a thin gold ring expands to the ellipse's edge; 3-6 (a seamless loop) a double gold ring with small diamond marks round it, a glowing card-shaped diamond in the middle, the marks moving a quarter of the way round per loop, the glow pulsing.
Layout: one horizontal row of 6 equal 2:1 cells, image size 3072x256 (each cell 512x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 28. `twistedfate_fx_r_out.png`：R 传送离开：原地的金色消散（不跟随），5 帧

传走的一瞬间：原地一道金色的光柱往上冲，一叠牌往上散开，人消失在光里（参考 R_Fire_Trail_Up、Z_TeleportCard、R_LensFlare）。中间是人的位置，不要画人。脚在格子底部往上 8 格的中间。约 36 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: a VANISHING FLASH at a figure's place (do NOT draw the figure), 5 frames: 1 a bright gold column of light swallows the figure's place, a gold ring on the ground; 2 the column at full height (to the top of the cell), 6 cards scattering upward; 3 the column thins to a line, cards flying out; 4 gold motes; 5 fading motes.
Layout: one horizontal row of 5 equal 9:11 cells, image size 2000x489 (each cell 400x489); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 29. `twistedfate_fx_r_in.png`：R 传送到达：目的地的金色出现（不跟随），5 帧

到达的一瞬间：从天上落下一道金色的光柱，地上炸开一圈金光，几张牌从光里飞出来（参考 R_LensFlare、Shockwave、Z_TeleportCard）。中间是人的位置，不要画人。脚在格子底部往上 8 格的中间。约 36 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, trails or sparks (only the playing cards and the dice, which are objects, get a 1-square dark outline #2A1E14), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold ramp (#FFFFFF, #FFF4BE, #FFD84E, #F2B21E, #C07A10, #6B400A) and a card ramp (#FFFFFF, #F4EEDC, #D6C9A4, #9C8A62).
Effect: an ARRIVAL FLASH at a figure's place (do NOT draw the figure), 5 frames: 1 a thin gold beam comes down from the top of the cell to the feet; 2 the beam widens, a gold shock ring bursts on the ground (an ellipse twice as wide as tall, 34 squares wide); 3 the beam fades from the top, 6 cards fly out sideways from the feet; 4 the ring at the edge, gold motes; 5 fading motes.
Layout: one horizontal row of 5 equal 9:11 cells, image size 2000x489 (each cell 400x489); the figure's feet 8 squares (64 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `twistedfate_fx_a_card` | view_projectiles `league_twistedfate_a_card`（朝右，游戏转到飞行方向，上下对称） | 16 × 8 |
| `twistedfate_fx_a_card_e` | view_projectiles `league_twistedfate_a_card_e`（朝右，游戏转到飞行方向，上下对称） | 22 × 10 |
| `twistedfate_fx_a_hit` | view_effects `league_twistedfate_a_hit`（跟随，画在人物上面） | 12 |
| `twistedfate_fx_e_cast` | view_effects `league_twistedfate_e_cast`（施法者身上，不跟随，朝左时镜像；格子左边中点放到普攻第 4 帧的右手） | 16 × 12 |
| `twistedfate_fx_e_hit` | view_effects `league_twistedfate_e_hit`（跟随，画在人物上面） | 18 |
| `twistedfate_fx_dice_roll` | view_buffs `league_twistedfate_dice_k` 的开头（pre_tag `dice_roll`，画在头顶上方） | 12 × 14 |
| `twistedfate_fx_dice_faces` | view_buffs `league_twistedfate_dice_1` … `dice_6`（loop_tag，各取一格，画在头顶上方） | 10 × 10 |
| `twistedfate_fx_dice_out` | view_buffs `league_twistedfate_dice_k` 的结尾（remove_tag `dice_out`） | 12 |
| `twistedfate_fx_w_show` | view_buffs `league_twistedfate_w_show_blue` / `_red` / `_gold`（各取一格，循环，画在头顶上方） | 10 × 13 |
| `twistedfate_fx_w_blue` | view_buffs `league_twistedfate_w_blue`（循环，画在头顶上方） | 14 × 18 |
| `twistedfate_fx_w_red` | view_buffs `league_twistedfate_w_red`（循环，画在头顶上方） | 14 × 18 |
| `twistedfate_fx_w_gold` | view_buffs `league_twistedfate_w_gold`（循环，画在头顶上方） | 14 × 18 |
| `twistedfate_fx_wb_card` | view_projectiles `league_twistedfate_wb_card`（朝右，游戏转到飞行方向，上下对称） | 20 × 10 |
| `twistedfate_fx_wr_card` | view_projectiles `league_twistedfate_wr_card`（朝右，上下对称） | 20 × 10 |
| `twistedfate_fx_wg_card` | view_projectiles `league_twistedfate_wg_card`（朝右，上下对称） | 20 × 10 |
| `twistedfate_fx_wb_hit` | view_effects `league_twistedfate_wb_hit`（跟随，画在人物上面） | 18 |
| `twistedfate_fx_wr_hit` | view_effects `league_twistedfate_wr_hit`（跟随，画在人物上面） | 14 |
| `twistedfate_fx_wr_burst` | view_effects `league_twistedfate_wr_burst`（BIG，画在打中点的地面上） | 50 × 30 |
| `twistedfate_fx_wr_slow` | view_buffs `league_twistedfate_wr_slow`（循环，画在脚下） | 18 × 7 |
| `twistedfate_fx_wg_hit` | view_effects `league_twistedfate_wg_hit`（跟随，画在人物上面） | 20 |
| `twistedfate_fx_q_cast` | view_effects `league_twistedfate_q_cast`（施法者身上，不跟随，朝左时镜像；格子左边中点放到 Q 第 4 帧的右手） | 18 × 14 |
| `twistedfate_fx_q_cards` | view_projectiles `league_twistedfate_q_cards`（BIG，朝右，游戏转到飞行方向，上下对称，播一次） | 32 × 18 |
| `twistedfate_fx_q_hit` | view_effects `league_twistedfate_q_hit`（跟随，画在人物上面） | 14 |
| `twistedfate_fx_r_seen` | view_buffs `league_twistedfate_r_seen`（循环，画在头顶上方） | 12 × 9 |
| `twistedfate_fx_r_cast` | view_effects `league_twistedfate_r_cast`（BIG，施法者身上，不跟随） | 56 × 56 |
| `twistedfate_fx_r_gate` | view_effects `league_twistedfate_r_gate`（BIG，施法者身上，不跟随） | 44 × 50 |
| `twistedfate_fx_r_dest` | view_effects `league_twistedfate_r_dest`（BIG，画在地面上，不跟随，在人物下面） | 40 × 20 |
| `twistedfate_fx_r_out` | view_effects `league_twistedfate_r_out`（BIG，画在出发点，不跟随） | 36 × 44 |
| `twistedfate_fx_r_in` | view_effects `league_twistedfate_r_in`（BIG，画在到达点，不跟随） | 36 × 44 |

- 施法者身上的画面（`e_cast`、`q_cast` 在手上；`r_cast`、`r_gate`、`r_out`、`r_in` 在脚下）：按 `design/twistedfate_shots.png` 的十字把格子的起点挪过去；`e_cast`、`q_cast`、`r_cast`、`r_gate` 晚于第一 tick 播放，`is_follow` 为 false（红方方向）。
- 飞行物（`a_card`、`a_card_e`、`wb_card`、`wr_card`、`wg_card`）第一帧前加一个空帧（出生那一 tick 画面朝上，`import_lucian.py` 的 `RAY_SKIP`）；近距离第一 tick 就打中的牌看不见（剑魔 W 的教训），命中特效要够大；`q_cards` 不循环，按飞行时间排帧。
- `w_show` 三格拆成 `w_show_blue`、`w_show_red`、`w_show_gold` 三个标签；`dice_faces` 六格拆成 `dice_1`…`dice_6`；`r_gate` 的 3–8 帧循环到 90 tick（1.5 秒），`r_dest` 的 3–6 帧同样。
- 清掉 Codex 给光和火焰描的最深色边（`import_riven.py` 的 `unrim` 做法，牌和骰子保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
