# 琴瑟仙女 娑娜：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型已定（`design/sona_design.png`，8 倍，你画的版本 B，40 格）。
> - 大小对照 `design/sona_size.png`：定稿造型放大 4 倍，裙摆在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。娑娜 34×40 格（马尾顶到裙摆 40 格），原版英雄约 31–36 格高。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里娑娜自己的特效贴图（多数是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（普攻和能量和弦、Q 英勇赞美诗、W 坚毅咏叹调、E 迅捷奏鸣曲、R 狂舞终乐章），只在本地用，不要提交。颜色按下面写的色阶：**Q 蓝、W 绿、E 粉紫、R 和能量和弦金**，和英雄联盟一样。
> - **特效要亮**：上一个英雄（魔腾）的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - 特效照下面第 1–20 条和「所有特效图的规则」画，每张一个 PNG，文件名 `sona_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`sona_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「能量和弦」 | 音波弹；每放 3 次技能，下一次打中英雄的普攻带上和弦，按最后一首歌：断奏（额外伤害）、渐弱（目标伤害降低）、节奏（减速） | `sona_fx_note` · `sona_fx_hit` · `sona_fx_pc_q` · `sona_fx_pc_w` · `sona_fx_pc_e` · `sona_fx_pc_glow` · `sona_fx_pc_tempo` · `sona_fx_pc_dim` |
| 技能 1 = Q「英勇赞美诗」 | 两道音波飞向最近的两个敌人；旋律光环 3 秒，碰到的队友加攻击力和法强 | `sona_fx_q_note` · `sona_fx_q_hit` · `sona_fx_q_aura` · `sona_fx_q_mel` |
| 技能 2 = W「坚毅咏叹调」+ E「迅捷奏鸣曲」 | 治疗自己和一名队友；旋律光环给碰到的队友护盾；E 每 14 秒一起弹：光环给队友加速 | `sona_fx_w_heal` · `sona_fx_w_aura` · `sona_fx_w_mel` · `sona_fx_e_aura` · `sona_fx_e_ally` |
| 大招 = R「狂舞终乐章」 | 琴抛到头顶，金色音波朝前推出，晕眩路上的敌方英雄 1.5 秒 | `sona_fx_r_cast` · `sona_fx_r_wave` · `sona_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、音符、火花没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的第四档，第五档（最深）只给很少的点缀。
- 颜色（按每条写的用）：
  - 赞美诗蓝（Q、普攻）：`#FFFFFF`、`#CFF4FF`、`#7FD8FF`、`#36A6F0`、`#1B5FC2`；
  - 咏叹调绿（W）：`#FFFFFF`、`#D8FFE0`、`#8CF5A0`、`#3CCB6B`、`#1E7F45`；
  - 奏鸣曲粉紫（E）：`#FFFFFF`、`#FFD8F6`、`#F59AE6`、`#D24FC8`、`#8A2A9E`；
  - 终乐章金（R、能量和弦）：`#FFFFFF`、`#FFF6C8`、`#FFD95C`、`#F0A830`、`#B06A1A`。
- **音符要像音符**：八分音符、四分音符、连音的符头和符干看得出来，至少 3 格高；高音谱号至少 7 格高。
- **飞行类特效朝右画，而且上下对称**（普攻音波 `note`、Q 音波 `q_note`、R 音波 `r_wave`）：游戏会把它转到飞行方向，朝左飞时整张会上下翻转，所以里面不要有分上下的东西（音符画在对称的位置，或者干脆不放）。
- 命中、爆发、光环居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（能量和弦的音符、旋律加攻、护盾、加速、减速、渐弱）左右对称，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人；头顶的标记（渐弱、晕眩）画在格子里，不挡脸。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `sona_fx_note.png`：普攻：飞出去的音波弹（飞行中循环），4 帧

娑娜的普攻：一颗蓝白色的发光音波弹朝右飞，后面拖两三道弯弯的音波弧线（参考 P_ProjectileHead、P_Trail、BA_Trail）。上下对称（飞向左边时会上下翻转）。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #CFF4FF, #7FD8FF, #36A6F0, #1B5FC2).
Effect: a small FLYING SOUND BOLT moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a round glowing head (white core, light-blue rim); behind it (to the left) two or three thin curved sound-wave arcs, open to the left, getting fainter; the arcs ripple a little each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the bolt on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `sona_fx_hit.png`：普攻命中，4 帧

音波弹打中：一圈蓝白色的小音波一闪，两个小音符飞出去（参考 Q_Target_Hit_Sparks、P_Note_Simple）。约 14 格，不要太大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #CFF4FF, #7FD8FF, #36A6F0, #1B5FC2).
Effect: a SMALL SOUND HIT, 4 frames: 1 a white flash at the center; 2 a ring of light-blue sound expands, two tiny music notes (eighth notes) pop out to the upper left and upper right; 3 the ring wider and thinner, the notes higher; 4 a few blue specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `sona_fx_pc_q.png`：能量和弦·断奏（Q 是最后一首歌时的强化普攻打中），5 帧

能量和弦打中（断奏 = 额外伤害）：中间一个金色的高音谱号，外面两圈蓝色的音波向外炸开，几个蓝白音符飞出（参考 P_Note_Simple、PCReady_RingWisps、P_ImpactRadial）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from gold (#FFFFFF, #FFF6C8, #FFD95C, #F0A830, #B06A1A) for the clef and a bright blue ramp (#FFFFFF, #CFF4FF, #7FD8FF, #36A6F0, #1B5FC2) for the rings.
Effect: a POWER CHORD HIT, 5 frames: 1 a white flash; 2 a golden treble clef appears at the center inside a burst of light-blue sound rings; 3 the rings at full size, 4-5 small blue-white music notes flying outward, the clef brightest; 4 the rings thin and break, the notes drift; 5 the clef fades, a few blue specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `sona_fx_pc_w.png`：能量和弦·渐弱（W 是最后一首歌），5 帧

和上一张同样的画面，只是音波和音符换成绿色（渐弱 = 目标造成的伤害降低）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from gold (#FFFFFF, #FFF6C8, #FFD95C, #F0A830, #B06A1A) for the clef and a green ramp (#FFFFFF, #D8FFE0, #8CF5A0, #3CCB6B, #1E7F45) for the rings.
Effect: the same POWER CHORD HIT as before but GREEN, 5 frames: 1 a white flash; 2 a golden treble clef at the center inside a burst of light-green sound rings; 3 the rings at full size, 4-5 small green-white music notes flying outward; 4 the rings thin and break; 5 the clef fades, a few green specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `sona_fx_pc_e.png`：能量和弦·节奏（E 是最后一首歌），5 帧

同样的画面，音波和音符换成粉紫色（节奏 = 减速）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from gold (#FFFFFF, #FFF6C8, #FFD95C, #F0A830, #B06A1A) for the clef and a pink-violet ramp (#FFFFFF, #FFD8F6, #F59AE6, #D24FC8, #8A2A9E) for the rings.
Effect: the same POWER CHORD HIT but PINK-VIOLET, 5 frames: 1 a white flash; 2 a golden treble clef at the center inside a burst of pink-violet sound rings; 3 the rings at full size, 4-5 small pink-white music notes flying outward; 4 the rings thin and break; 5 the clef fades, a few pink specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `sona_fx_pc_glow.png`：能量和弦准备好了（娑娜身上，循环），6 帧

能量和弦攒满：三个小小的金色音符绕着她腰前的琴慢慢转圈、上下飘（参考 PCReady_RingWisps、Z_Notes_01）。中间是娑娜，不要画人；音符在格子中间偏下（琴的高度），转一圈正好 6 帧循环。约 36 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from gold (#FFFFFF, #FFF6C8, #FFD95C, #F0A830, #B06A1A).
Effect: THREE SMALL GOLDEN MUSIC NOTES circling a figure's waist (do NOT draw the figure; leave the middle empty), 6 frames, a seamless loop: the three notes (an eighth note, a quarter note and a double note, each 3-4 squares tall with a white glint) move round a flattened ellipse (twice as wide as tall) at the cell's lower middle, a third of the way round each 2 frames, bobbing a little; a few gold sparkles trail them.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 3072x256 (each cell 512x256); the ellipse at the lower middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `sona_fx_pc_tempo.png`：节奏减速（被减速的敌人脚下，循环），4 帧

被节奏减速：敌人脚下一圈粉紫色的五线谱圆环慢慢转，上面挂着两三个小音符（参考 E_Zone_Ring、Z_Pentagram_02）。中间是人，不要画人。约 24 格宽、10 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet ramp (#FFFFFF, #FFD8F6, #F59AE6, #D24FC8, #8A2A9E).
Effect: a SLOW MARK at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ring of pink-violet music staff lines (twice as wide as tall) on the ground, two or three small notes sitting on it, the ring turning a little each frame.
Layout: one horizontal row of 4 equal cells, each 5 wide to 2 tall, image size 2560x256 (each cell 640x256); the ring at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `sona_fx_pc_dim.png`：渐弱（被削弱的敌人头顶，循环），4 帧

被渐弱削弱（造成的伤害降低）：敌人头顶一个往下垂的绿色音符，旁边一个向下的小箭头，一闪一闪（参考 Z_Notes_01）。约 14 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green ramp (#FFFFFF, #D8FFE0, #8CF5A0, #3CCB6B, #1E7F45).
Effect: a WEAKEN MARK above a head, 4 frames, a seamless loop: a small drooping green music note (an eighth note tilted down) beside a small green arrow pointing down, both bobbing down and up one square, glowing.
Layout: one horizontal row of 4 equal cells, each 3 wide to 2 tall, image size 1536x256 (each cell 384x256); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `sona_fx_q_note.png`：Q 英勇赞美诗：飞向敌人的蓝色音波（飞行中循环），4 帧

英勇赞美诗的飞弹：一道蓝色的音波朝右飞，前面是发白光的弹头，后面拖着两条互相缠绕的蓝色音波（参考 Q_TrailTwisted、Q_BigTrail、Q_LinearWaves）。上下对称。约 22 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #CFF4FF, #7FD8FF, #36A6F0, #1B5FC2).
Effect: a FLYING SOUND WAVE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: at the front (right) a bright glowing head (white core, light-blue rim); behind it two light-blue sound waves twisting round each other like a braid, narrowing to the left; the twist moves along each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the wave on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `sona_fx_q_hit.png`：Q 打中，5 帧

英勇赞美诗打中：蓝色的星形光爆，几道竖直的光束往上冲（参考 Q_Target_Hit_Nova、Q_Target_Hit_Beams、Q_Tar_Ring_Glow）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #CFF4FF, #7FD8FF, #36A6F0, #1B5FC2).
Effect: a BLUE NOVA HIT, 5 frames: 1 a white flash; 2 a star-shaped burst of light blue with a white core; 3 the burst at full size, three or four thin vertical light beams shooting up from it; 4 the beams fade upward, the burst becomes a ring; 5 a few blue sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `sona_fx_q_mel.png`：Q 旋律：友方英雄 3 秒加攻（他身上，循环），4 帧

英勇赞美诗的旋律：拿到加成的队友身边飘着几个蓝色的小音符和蓝白的光点（参考 Q_Buff_WispColor、Z_Notes_01）。中间是人，不要画人。约 20 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #CFF4FF, #7FD8FF, #36A6F0, #1B5FC2).
Effect: a BLUE MUSIC AURA round a figure's chest (do NOT draw the figure; leave the middle empty), 4 frames, a seamless loop: three small blue music notes and a few blue-white sparkles float round and up beside the figure's place, moving a little each frame.
Layout: one horizontal row of 4 equal cells, each 5 wide to 4 tall, image size 1280x256 (each cell 320x256); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `sona_fx_w_heal.png`：W 坚毅咏叹调：治疗（娑娜和被治疗的队友身上），6 帧

治疗：绿色的光从脚下升起，几个绿色的音符和十字光点往上飘（参考 W_13、W_Buff_WispColor）。中间是人，不要画人。约 18 格宽、24 格高，底部在脚下。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green ramp (#FFFFFF, #D8FFE0, #8CF5A0, #3CCB6B, #1E7F45).
Effect: a GREEN HEALING SONG round a figure (do NOT draw the figure), 6 frames: 1 a ring of green light on the ground; 2-4 green music notes and small plus-shaped sparkles rise from it up past the figure's place, a soft column of light green between them; 5 the notes reach the top and fade; 6 a few green sparkles.
Layout: one horizontal row of 6 equal cells, each 3 wide to 4 tall, image size 2304x512 (each cell 384x512); the ground ring near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `sona_fx_w_mel.png`：W 旋律：护盾（队友身上，护盾在就循环），4 帧

坚毅咏叹调的护盾：一层绿色的半透明感护罩罩住队友，表面有一圈转动的绿光（参考 W_Shield_Ring_Glow、W_Shield_Spinner、W_Shield_Shell）。只画护罩的边缘和光纹，中间留空。约 26 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green ramp (#FFFFFF, #D8FFE0, #8CF5A0, #3CCB6B, #1E7F45).
Effect: a GREEN SHIELD round a figure (do NOT draw the figure; leave the middle empty - only the shell's rim and the light on it), 4 frames, a seamless loop: a tall oval shell rim of light green with a white glint, one brighter arc of green light running round it a quarter turn each frame, two tiny notes on the rim.
Layout: one horizontal row of 4 equal cells, each 7 wide to 8 tall, image size 1792x512 (each cell 448x512); the oval centered in every cell, its bottom near the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `sona_fx_e_ally.png`：E 迅捷奏鸣曲：加速（娑娜和队友身上，循环），4 帧

迅捷奏鸣曲：加速的人脚边绕着粉紫色的风和音符（两边都有，因为人朝左朝右都会用这张图）（参考 E_Buff_SpeedShape、E_Buff_Sparks）。中间是人，不要画人。约 24 格宽、12 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet ramp (#FFFFFF, #FFD8F6, #F59AE6, #D24FC8, #8A2A9E).
Effect: a PINK SPEED WIND at a figure's feet (do NOT draw the figure; symmetric left and right), 4 frames, a seamless loop: curling pink-violet wind streaks swirl round the figure's feet on both sides, two small pink notes riding them, a few white sparkles, moving each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 2048x256 (each cell 512x256); the swirl at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `sona_fx_q_aura.png`：Q 旋律光环：娑娜脚下的蓝色音乐圈（跟着她 3 秒，大图），6 帧

英勇赞美诗的旋律光环：娑娜脚下一个蓝色的发光圆环（从斜上方看是扁椭圆，宽是高的 2 倍），环上有五线谱的纹路，几个蓝色音符从环上冒起来（参考 Q_Area_Circle、Q_Zone_AOE_Glow、Z_Zone_Ring_02、Z_Pentagram）。中间留空（娑娜站在那里）。约 84 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bright blue ramp (#FFFFFF, #CFF4FF, #7FD8FF, #36A6F0, #1B5FC2).
Effect: a MUSIC AURA RING on the ground (a flattened ellipse twice as wide as tall; leave the middle empty), 6 frames, a seamless loop: a glowing light-blue ring with thin music staff lines along it, small blue notes rising from it at a few places and fading, the brightest spot running round the ring each frame.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 4608x384 (each cell 768x384); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `sona_fx_w_aura.png`：W 旋律光环：绿色音乐圈（大图），6 帧

和上一张同样的光环，换成绿色（参考 W_Zone_Ring）。约 84 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green ramp (#FFFFFF, #D8FFE0, #8CF5A0, #3CCB6B, #1E7F45).
Effect: the same MUSIC AURA RING but GREEN (a flattened ellipse twice as wide as tall; leave the middle empty), 6 frames, a seamless loop: a glowing light-green ring with thin music staff lines, small green notes rising from it, the brightest spot running round the ring each frame.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 4608x384 (each cell 768x384); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `sona_fx_e_aura.png`：E 旋律光环：粉紫色音乐圈（大图），6 帧

同样的光环，换成粉紫色（参考 E_Zone_Ring）。约 84 格宽、42 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink-violet ramp (#FFFFFF, #FFD8F6, #F59AE6, #D24FC8, #8A2A9E).
Effect: the same MUSIC AURA RING but PINK-VIOLET (a flattened ellipse twice as wide as tall; leave the middle empty), 6 frames, a seamless loop: a glowing pink-violet ring with thin music staff lines, small pink notes rising from it, the brightest spot running round the ring each frame.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 4608x384 (each cell 768x384); the ellipse centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `sona_fx_r_wave.png`：R 狂舞终乐章：飞出去的金色音波（飞行中循环，大图），4 帧

狂舞终乐章：一道又高又窄的金色音波朝右推出去——一个弧形的光墙（凸向右边），里面有五线谱的线和金色音符，后面拖着淡淡的金光（参考 R_mis_bar、R_Shape_02、R_Notes2_2x2、R_Pentagram_02）。上下对称。约 16 格长（飞行方向）、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from gold (#FFFFFF, #FFF6C8, #FFD95C, #F0A830, #B06A1A).
Effect: a GOLDEN SOUND WAVE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a tall narrow crescent wall of golden light bulging to the right (white core along its front edge), inside it five thin horizontal music staff lines and 3-4 golden notes, a faint golden glow trailing behind it to the left; the notes and the glow shimmer each frame.
Layout: one horizontal row of 4 equal cells, each 1 wide to 2 tall, image size 1024x512 (each cell 256x512); the wave centered on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `sona_fx_r_cast.png`：R 施法：琴抛到头顶时的金色和弦爆发（娑娜身上，大图），6 帧

放大招：她把琴抛到头顶的时候，头顶炸开一个金色的星形光爆，一圈金色音符向外散开（参考 R_Cas_Burst、R_Notes2_2x2、Z_AuraBurst）。光爆在格子的上半部分（她的头顶），下半部分留空。约 48 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from gold (#FFFFFF, #FFF6C8, #FFD95C, #F0A830, #B06A1A).
Effect: a GOLDEN CHORD BURST above a figure's head (do NOT draw the figure; the burst is in the UPPER half of the cell), 6 frames: 1 a white flash; 2 a star-shaped burst of golden rays; 3 the burst at full size, 6-8 golden music notes flying outward in a ring; 4 the rays shrink, the notes fly further; 5 the notes fade; 6 a few golden sparkles.
Layout: one horizontal row of 6 equal cells, each 6 wide to 5 tall, image size 4608x640 (each cell 768x640); the burst centered in the upper half of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `sona_fx_r_hit.png`：R 晕眩（被晕的敌方英雄头顶，1.5 秒），12 帧

被狂舞终乐章晕眩（英雄联盟里是被迫跳舞）：头顶一圈金色的音符转圈，12 帧约 1.5 秒（转两圈），第 1 帧出现、最后一帧散去。约 18 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, notes or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from gold (#FFFFFF, #FFF6C8, #FFD95C, #F0A830, #B06A1A).
Effect: a STUN MARK above a head, 12 frames: 1 a golden flash; 2-11 four small golden music notes circling round a flattened ellipse above the head (twice as wide as tall), a quarter of the way round every 2 frames, a few golden sparkles; 12 the notes fade.
Layout: one horizontal row of 12 equal cells, each 2 wide to 1 tall, image size 3072x128 (each cell 256x128); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `sona_fx_note` | view_projectiles `league_sona_note`（朝右，游戏转到飞行方向） | 12 × 8 |
| `sona_fx_hit` | view_effects `league_sona_hit`（跟随） | 14 |
| `sona_fx_pc_q` | view_effects `league_sona_pc_q`（跟随） | 22 |
| `sona_fx_pc_w` | view_effects `league_sona_pc_w`（跟随） | 22 |
| `sona_fx_pc_e` | view_effects `league_sona_pc_e`（跟随） | 22 |
| `sona_fx_pc_glow` | view_buffs `league_sona_pc_glow`（循环，画在人物上面） | 36 × 20 |
| `sona_fx_pc_tempo` | view_buffs `league_sona_pc_tempo`（循环，画在脚下） | 24 × 10 |
| `sona_fx_pc_dim` | view_buffs `league_sona_pc_dim`（循环，画在人物上面） | 14 × 10 |
| `sona_fx_q_note` | view_projectiles `league_sona_q_note`（朝右，游戏转到飞行方向） | 22 × 10 |
| `sona_fx_q_hit` | view_effects `league_sona_q_hit`（跟随） | 22 |
| `sona_fx_q_mel` | view_buffs `league_sona_q_mel`（循环，画在人物上面） | 20 × 16 |
| `sona_fx_w_heal` | view_effects `league_sona_w_heal`（跟随） | 18 × 24 |
| `sona_fx_w_mel` | view_buffs `league_sona_w_mel`（循环，护盾破了就消失） | 26 × 30 |
| `sona_fx_e_ally` | view_buffs `league_sona_e_ally`（循环，画在脚下） | 24 × 12 |
| `sona_fx_q_aura` | view_projectiles `league_sona_q_aura`（跟随娑娜的光环，地面，循环，大图） | 84 × 42 |
| `sona_fx_w_aura` | view_projectiles `league_sona_w_aura`（同上，大图） | 84 × 42 |
| `sona_fx_e_aura` | view_projectiles `league_sona_e_aura`（同上，大图） | 84 × 42 |
| `sona_fx_r_wave` | view_projectiles `league_sona_r_wave`（朝右，游戏转到飞行方向，大图） | 16 × 44 |
| `sona_fx_r_cast` | view_effects `league_sona_r_cast`（施法者身上，跟随，大图） | 48 × 40 |
| `sona_fx_r_hit` | view_effects `league_sona_r_hit`（跟随，画在人物上面） | 18 × 10 |

- 三个旋律光环（`q_aura` / `w_aura` / `e_aura`）是跟着娑娜的 ApplyInProjectile 的画面，循环 3 秒（180 tick）；`r_hit` 12 帧共 90 tick（晕眩 1.5 秒）。
- 清掉 Codex 给光和音符描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）。
