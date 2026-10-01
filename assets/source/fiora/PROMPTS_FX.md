# 无双剑姬 菲奥娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 18 张特效图。** 造型已定（`design/fiora_design.png`，8 倍），动作条正在另一轮画；用户要求特效先做，这一轮只画特效。
> - 大小对照 `design/fiora_size.png`：定稿造型放大 4 倍，站在红色脚底线上，上面是 10 格一段的刻度，右边是原版骑士。剑姬 62×40 格（头顶到鞋底 40 格，平举的细剑占去右边一大半宽度），原版英雄约 35 格高。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里剑姬自己的特效贴图，按用在我们哪张特效分好了行（刺光和剑光、破绽的玫瑰纹和大招的碎片、格挡闪光和强化的金环），只在本地用，不要提交。
> - 特效照下面第 1–18 条和「所有特效图的规则」画，每张一个 PNG，文件名 `fiora_fx_<名字>.png`，排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。最好打成一个 zip 放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「决斗之舞」 | 细剑刺击；每 3–4 秒，打中敌方英雄时在他身上亮出一处破绽（蓝色菱形纹章），下一次打中英雄就刺中它：碎裂、真实伤害、回血、加速 | `fiora_fx_hit` · `fiora_fx_vital_mark` · `fiora_fx_vital_hit` · `fiora_fx_v_ms` |
| 技能 1 = Q「破空斩」+ E「夺命连刺」 | 冲向敌人刺一剑（出发点留下风痕）；之后两下普攻加攻速，第一下减速，第二下暴击 | `fiora_fx_q_dash` · `fiora_fx_q_hit` · `fiora_fx_e_glint` · `fiora_fx_e_hit` · `fiora_fx_e_crit` |
| 技能 2 = W「劳伦特心眼刀」 | 招架 0.75 秒（身前的剑光屏障），然后向前刺出一道剑气，直线上的敌人受伤；第一个敌方英雄减速，招架时挡下过伤害就改为眩晕 1 秒 | `fiora_fx_w_parry` · `fiora_fx_w_line` · `fiora_fx_w_hit` · `fiora_fx_w_slow` · `fiora_fx_w_stun` |
| 大招 = R「无双挑战」 | 锁定一名敌方英雄 8 秒，他身上亮出 4 处破绽（剩几处显示几处），每刺中一处碎裂一次；4 处都刺中或他死掉，地上留下 3 秒的胜利之地给友军回血 | `fiora_fx_r_on` · `fiora_fx_r_marks` · `fiora_fx_r_hit` · `fiora_fx_r_zone` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反；之前的交付每个形状都被描了深色边，还得清掉）。
- 颜色（按每条写的用）：
  - 剑光（刺光、剑气）：`#FFFFFF`、`#E6E8F0`、`#B8D8F8`、`#6FA8E8`、`#3A6FC0`；
  - 破绽蓝（破绽纹章、碎片、剑气的光）：`#FFFFFF`、`#CFF4FF`、`#7FDFFF`、`#2FB0F0`、`#1470C8`、`#0B3F86`；
  - 金色（暴击、大招、眩晕星）：`#FFFFFF`、`#FFF4C0`、`#FCD87A`、`#F9C740`、`#C99631`、`#784C17`；
  - 治疗的薄荷绿（胜利之地的光点）：`#FFFFFF`、`#E4FFF4`、`#8CF7C8`、`#36D99A`。
- **破绽纹章在所有图里是同一个样子**：竖长的菱形，里面是简单的玫瑰花纹（一个小圆加几片花瓣的浅色线），白蓝色的边。
- **飞行、直线类特效朝右画，而且上下对称**（只有 W 的剑气 `w_line`）：游戏会把它转到刺的方向，向左时整张图转 180°。
- 命中、碎裂、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在英雄身上的特效（招架、强化、挑战、剩下的破绽、减速）：格子里留出空的人形位置，不要画人，**不能挡住身体和脸**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（18 张）

18 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `fiora_fx_hit.png`：普攻命中，5 帧

细剑刺中目标：一道银白的斜向刺光（细长的菱形闪光）加几条向外飞的细线火花（参考 E_sword_sheen、W_sword_sharpFlash）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a steel ramp (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0).
Effect: a RAPIER HIT, 5 frames: 1 a small white flash at the center; 2 a thin bright diagonal slash of light (a long narrow diamond, white core, pale-blue edge) across the center from lower left to upper right; 3 the slash at full length with 4-5 thin spark lines flying outward; 4 the slash thins and the sparks fly further, turning blue; 5 a few blue specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `fiora_fx_e_hit.png`：夺命连刺第一下（减速）命中，5 帧

强化第一击：一道横向的蓝色刺光，刺中点炸开一圈淡蓝的冰霜碎片，表示减速（参考 E_cas_trails、E_sword_glow）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a steel ramp (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0) with the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86).
Effect: a CHILLING THRUST HIT, 5 frames: 1 a white flash at the center; 2 a straight horizontal thrust of light from the left edge to the center, bright white core with a blue glow; 3 a burst of small pale-blue ice-like shards around the center, a thin blue ring; 4 the shards drift outward and down, the ring widens; 5 a few blue specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `fiora_fx_e_crit.png`：夺命连刺第二下（暴击）命中，6 帧

暴击：比普通命中大一圈的 X 形交叉闪光，白芯、金边、外面一圈蓝光，四周飞出金色和蓝色的火花（参考 E_buff_mult_yellow、Q_swordGlow）。约 26 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a steel ramp (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0) with gold (#FFFFFF, #FFF4C0, #FCD87A, #F9C740, #C99631, #784C17).
Effect: a CRITICAL STRIKE, 6 frames: 1 a bright white flash at the center; 2 a big X-shaped cross of light (two long narrow diamonds, white cores, gold edges) filling 80% of the cell; 3 the X at full size with a pale-blue glow ring and 6-8 gold and blue sparks flying outward; 4 the X shrinks, the sparks fly further; 5 the ring fades to blue, sparks scatter; 6 a few gold specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `fiora_fx_q_hit.png`：Q 破空斩的刺击命中，5 帧

冲刺后的一刺：一道很长的水平刺光从左边扎进来，刺中点一个金白色的星形闪光（参考 Q_swordGlow）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a steel ramp (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0) with gold (#FFFFFF, #FFF4C0, #FCD87A, #F9C740, #C99631, #784C17).
Effect: a LUNGE STAB HIT, 5 frames: 1 a long thin horizontal streak of white light entering from the left edge to the center; 2 a bright four-pointed star flash (white core, pale-gold rays) at the center where the streak ends; 3 the star at full size, the streak fading, small sparks; 4 the star shrinks, sparks fly outward; 5 a few pale-gold specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `fiora_fx_q_dash.png`：Q 破空斩出发点（地面，不跟随），5 帧

剑姬冲出去时留在原地的地面效果：一团扁的尘土加两三道往右拉长的风痕（她往右冲），很快散开。约 32 格宽、12 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from a steel ramp (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0) with dust (#C8BCA8, #9A8C78, #6E6252).
Effect: a DASH START on the ground (a figure dashes to the RIGHT from the left part of the cell; do NOT draw the figure), 5 frames: 1 a small flat puff of dust at the bottom left; 2 the dust spreads flat along the ground and two or three long thin white-blue wind streaks stretch from it to the right; 3 the streaks reach the right side, the dust rolls; 4 the streaks thin and break; 5 faint dust.
Layout: one horizontal row of 5 equal cells, each 8 wide to 3 tall, image size 2560x384 (each cell 512x384); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `fiora_fx_vital_mark.png`：被动 破绽标记（敌方英雄身上，持续显示），4 帧循环

敌方英雄身上亮出的一处破绽：一枚发光的蓝白色菱形纹章，里面是玫瑰花纹的线条（参考 Passive_hit_tar_pattern），外面一圈细光，轻轻呼吸闪动。4 帧正好一圈呼吸（播完接着播不跳）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86).
Effect: a VITAL MARK, 4 frames, a seamless loop: a glowing diamond-shaped crest (taller than wide, about 60% of the cell) with a simple rose pattern of pale lines inside (a small circle with petals), a bright white-blue border, a thin halo around it; it pulses: frame 1 normal, 2 brighter and a pixel bigger halo, 3 brightest, 4 back to normal.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `fiora_fx_vital_hit.png`：被动 刺中破绽（碎裂 + 回血加速），6 帧

刺中破绽：菱形纹章一闪炸成碎片，一大圈蓝白色的玫瑰花纹光环扩开，碎片往外飞（参考 Passive_hit_tar_pattern、R_flying_shards）。约 30 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86).
Effect: a VITAL STRUCK, 6 frames: 1 the diamond crest at the center flashes white; 2 it shatters: 6-8 small blue crystal shards fly outward and a round rose-pattern emblem of light (a circle of petals, pale blue lines) flashes behind; 3 the emblem expands to fill the cell, the shards fly further; 4 the emblem thins to an outline, the shards spin; 5 the emblem fades, the shards dim to deep blue; 6 a few blue specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `fiora_fx_w_parry.png`：W 劳伦特心眼刀 招架（0.75 秒，身上），4 帧循环

招架架势：她身前一道竖着的半透明蓝白色月牙形剑光屏障，上面流动着亮线，周围几点闪光；中间和左边留空人形（不要画人），屏障在人形右前方。约 28 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86) with steel (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0).
Effect: a PARRY GUARD in front of a standing figure facing right (leave the figure's place empty on the left 60% of the cell; do NOT draw the figure), 4 frames, a seamless loop: a tall crescent of blue-white light (a curved vertical blade of light, bowed to the right, as tall as the cell) in the right part of the cell, a bright white line flowing along it from top to bottom each frame, a few white-blue sparkles around it.
Layout: one horizontal row of 4 equal cells, each 2 wide to 3 tall, image size 1024x384 (each cell 256x384); the crescent in the right half of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `fiora_fx_w_line.png`：W 刺出的剑气（直线，朝右），4 帧

招架后向前的一刺：一道很长的蓝白色剑气从左端（剑姬）一直扎到右端，尖头朝右，后面拖着细光纹，上下对称。整张图朝右，上下对称。约 56 格长、16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86) with steel (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0).
Effect: a PIERCING THRUST WAVE flying to the RIGHT, 4 frames, SYMMETRIC above and below the middle line: 1 a thin bright line of white-blue light from the left edge to the middle; 2 the thrust reaches the right edge: a long narrow spear of light (white core, blue glow) ending in a sharp point at the right, two thin streaks along its sides; 3 at full length, the glow widening a little, small sparks along it; 4 the thrust fades from the left, only the point bright.
Layout: one horizontal row of 4 equal cells, each 7 wide to 2 tall, image size 1792x128 (each cell 448x128); the thrust on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `fiora_fx_w_hit.png`：W 剑气打中敌人，5 帧

剑气刺穿敌人：一道水平的蓝白刺光穿过中心，中心一个小的蓝色爆点（参考 W_sword_sharpFlash）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86) with steel (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0).
Effect: a THRUST HIT, 5 frames: 1 a white flash at the center; 2 a horizontal line of blue-white light pierces through the center from left to right; 3 a small round blue burst at the center, the line at full length; 4 the burst breaks into sparks, the line thins; 5 a few blue specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `fiora_fx_w_slow.png`：W 减速（第一个敌方英雄身上），6 帧

被减速：人形脚下一圈淡蓝的寒气贴着地面扩开，几道往下垂的蓝色线条（重力感），不要画人。约 20 格宽、24 格高，地面在格子底部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86).
Effect: a SLOW on a standing figure (do NOT draw the figure), 6 frames: 1 a flat pale-blue ring appears on the ground at the bottom middle (an ellipse twice as wide as tall); 2-3 the ring spreads, 3-4 short blue lines fall down around the figure's place like heavy rain; 4-5 the lines reach the ground, the ring pulses; 6 faint blue specks.
Layout: one horizontal row of 6 equal cells, each 5 wide to 6 tall, image size 1920x384 (each cell 320x384); the ground line near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `fiora_fx_w_stun.png`：W 眩晕（第一个敌方英雄头顶，1 秒），8 帧循环

被晕住：头顶一圈转着的金色小星星和一道蓝白的剑光小圈（参考原版的眩晕星）。8 帧转一圈，正好 1 秒。约 18 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from gold (#FFFFFF, #FFF4C0, #FCD87A, #F9C740, #C99631, #784C17) with the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86).
Effect: STUN STARS circling above a head, 8 frames, a seamless loop: an ellipse (twice as wide as tall) of 3 small bright gold four-pointed stars and a thin blue-white ring, the stars moving an eighth of the way around the ellipse each frame (the ones at the back smaller and dimmer).
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 2048x128 (each cell 256x128); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `fiora_fx_r_on.png`：R 无双挑战 发起（目标身上），6 帧

锁定挑战的对手：目标周围先闪起一圈金白色的光环，四枚蓝色菱形破绽纹章从光环上亮起、落到目标的前后左右四个位置（参考 R_color-rampdown、E_buff_mult_yellow）。中间留空人形。约 40 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from gold (#FFFFFF, #FFF4C0, #FCD87A, #F9C740, #C99631, #784C17) with the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86).
Effect: a CHALLENGE on a standing figure (leave the figure's place empty in the middle; do NOT draw it), 6 frames: 1 a bright gold-white ring flashes around the figure at waist height (an ellipse twice as wide as tall); 2 the ring spreads and four small blue diamond crests light up on it at its left, right, front (lower) and back (upper) points; 3 the crests at full brightness, the ring glowing gold; 4-5 the ring fades, the crests stay; 6 only the four crests, dimmer.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the ring centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `fiora_fx_r_marks.png`：R 剩下的破绽（目标身上，8 秒，按剩几个显示），4 行 × 4 帧循环

一张图 4 行：第 1 行 4 枚破绽纹章（左、右、前下、后上），第 2 行 3 枚（左边那枚不见了），第 3 行 2 枚（再少右边那枚），第 4 行 1 枚（只剩后上那枚）。每行 4 帧是一圈呼吸闪动，播完接着播不跳。纹章和被动的破绽标记同一个样子，小一号。中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86).
Effect: the REMAINING VITALS around a standing figure (the figure is NOT drawn), 4 rows x 4 frames: each row is a seamless 4-frame loop (pulse: normal, brighter, brightest, normal) of small glowing blue diamond crests (the same design as a vital mark: a pale rose pattern inside, a white-blue border, about 10 squares tall) placed on an ellipse around the figure's waist: row 1 FOUR crests at the left, right, front (lower middle) and back (upper middle) points; row 2 the same without the left one (THREE); row 3 only the front and back ones (TWO); row 4 only the back one (ONE). The crests stay exactly in the same places in every row.
Layout: a grid of 4 columns x 4 rows of equal square cells, image size 1024x1024 (each cell 256x256); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `fiora_fx_r_hit.png`：R 刺中破绽（比被动的更大），6 帧

刺中无双挑战的破绽：和被动碎裂一样，但更大更亮，金色的玫瑰花纹光环加蓝色碎片（参考 R_flying_shards、Passive_hit_tar_pattern）。约 32 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86) with gold (#FFFFFF, #FFF4C0, #FCD87A, #F9C740, #C99631, #784C17).
Effect: a GRAND VITAL STRUCK, 6 frames: 1 a white flash at the center; 2 a blue diamond crest shatters into 8-10 blue crystal shards flying outward and a large round rose-pattern emblem of GOLD light flashes behind; 3 the emblem fills the cell, shards further out; 4 the emblem thins to a gold outline; 5 it fades, the shards dim; 6 a few gold and blue specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `fiora_fx_r_zone.png`：R 胜利之地（地面治疗区，3 秒，大图），8 帧

赢下挑战后留下的治疗区：地上一个扁椭圆的金白色光圈，中间是大的玫瑰花纹纹章（金色线条），往上冒淡绿和金色的光点；1–2 帧展开，3–6 帧循环（导入时重复到 3 秒），7–8 帧散去。宽是高的 2 倍。约 72 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from gold (#FFFFFF, #FFF4C0, #FCD87A, #F9C740, #C99631, #784C17) with a mint healing glow (#FFFFFF, #E4FFF4, #8CF7C8, #36D99A).
Effect: a VICTORY ZONE on the ground (seen from above at an angle: an ellipse twice as wide as tall filling the cell), 8 frames: 1 a bright gold-white ring appears small at the center; 2 it opens to the full ellipse, a large rose emblem (a circle of petals in gold lines) drawn on the ground inside it; 3-6 a seamless loop: the ring and the emblem glow, small mint-green and gold sparkles rise from inside the zone and fade (different sparkles each frame); 7 the emblem fades, the ring thins; 8 a faint gold ring.
Layout: one horizontal row of 8 equal cells, each 2 wide to 1 tall, image size 4608x288 (each cell 576x288); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `fiora_fx_e_glint.png`：夺命连刺准备好（身上，最多 4 秒），4 帧循环

接下来两下普攻被强化：她身边绕着几道蓝白的细光线和闪点，从下往上飘（参考 E_sword_sheen、E_buff_mult）。中间留空人形，不挡脸和身体。约 36 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86) with steel (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0).
Effect: a BLADE-WORK AURA around a standing figure (leave the figure's place empty in the middle, about 60% of the cell width and 85% of its height; do NOT draw it and do not cover it), 4 frames, a seamless loop: 3-4 thin short streaks of blue-white light and small sparkles rising around the figure's sides and in front of its chest, each frame moving up a little and fading at the top while new ones appear at the bottom.
Layout: one horizontal row of 4 equal cells, each 9 wide to 10 tall, image size 1152x320 (each cell 288x320); centered horizontally. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `fiora_fx_v_ms.png`：被动 刺中破绽后的加速（脚下，1.5 秒），4 帧循环

刺中破绽后加速：脚下两三道往左拖的蓝白色风痕（人往右跑），一小团扬起的尘（参考 E_cas_trails）。不画人。约 26 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline, colours only from the vital blue (#FFFFFF, #CFF4FF, #7FDFFF, #2FB0F0, #1470C8, #0B3F86) with steel (#FFFFFF, #E6E8F0, #B8D8F8, #6FA8E8, #3A6FC0).
Effect: SPEED LINES at a figure's feet (the figure is NOT drawn), 4 frames, a seamless loop: two or three long thin streaks of blue-white wind trailing to the LEFT from the bottom middle of the cell (the figure runs right), and a small puff of pale dust at the heel; the streaks flicker and shift each frame.
Layout: one horizontal row of 4 equal cells, each 5 wide to 2 tall, image size 1280x128 (each cell 320x128); at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `fiora_fx_hit` | view_effects `league_fiora_hit`（跟随） | 16 |
| `fiora_fx_e_hit` | view_effects `league_fiora_e_hit`（跟随） | 18 |
| `fiora_fx_e_crit` | view_effects `league_fiora_e_crit`（跟随） | 26 |
| `fiora_fx_q_hit` | view_effects `league_fiora_q_hit`（跟随） | 20 |
| `fiora_fx_q_dash` | view_effects `league_fiora_q_dash`（施法者身上，不跟随，画在人物下面） | 32 × 12 |
| `fiora_fx_vital_mark` | view_effects `league_fiora_vital_mark`（跟随，每 20 tick 播一次，连起来一直亮） | 14 |
| `fiora_fx_vital_hit` | view_effects `league_fiora_vital_hit`（跟随） | 30 |
| `fiora_fx_w_parry` | view_buffs `league_fiora_w_parry` | 28 × 44 |
| `fiora_fx_w_line` | view_projectiles `league_fiora_w_line`（直线范围，游戏会转到刺的方向） | 56 × 16 |
| `fiora_fx_w_hit` | view_effects `league_fiora_w_hit`（跟随） | 18 |
| `fiora_fx_w_slow` | view_effects `league_fiora_w_slow`（跟随） | 20 × 24 |
| `fiora_fx_w_stun` | view_effects `league_fiora_w_stun`（跟随，头顶） | 18 × 10 |
| `fiora_fx_r_on` | view_effects `league_fiora_r_on`（跟随） | 40 |
| `fiora_fx_r_marks` | view_effects `league_fiora_r_m4`、`r_m3`、`r_m2`、`r_m1`（跟随，每 20 tick 播一次） | 44 × 44 |
| `fiora_fx_r_hit` | view_effects `league_fiora_r_hit`（跟随） | 32 |
| `fiora_fx_r_zone` | view_effects `league_fiora_r_zone`（地面，不跟随，画在人物下面；大图 league_fiora_big） | 72 × 36（半径 35000） |
| `fiora_fx_e_glint` | view_buffs `league_fiora_e_as` | 36 × 40 |
| `fiora_fx_v_ms` | view_buffs `league_fiora_v_ms1` | 26 × 10 |

- 破绽标记和剩下的破绽每 20 tick 播一段（技能数据里的链），4 帧各 83 ms 正好 20 tick；胜利之地的 3–6 帧循环重复到 180 tick。
- 清掉 Codex 给形状描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单。
- W 剑气是 `LineRangeProjectile` 的画面（55000 × 16000），图的左端在剑姬身上；Q 出发点、胜利之地画在人物下面（`z` −1）。
