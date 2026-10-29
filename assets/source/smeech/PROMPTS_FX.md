# 史密奇：给 Codex 的特效提示词（第 3 步）

> **这一份是 8 张特效图 + 3 个技能图标。** 造型已定（`design/smeech_design.png`：祖安的炼金男爵小怪物，青绿高礼帽、横着的红尖耳、灰褐绒毛脸，两条橄榄绿机械手臂末端是细长的黄铜爪，蹲得很低、双爪张开）。史密奇在游戏里是**高清**的（每个游戏格子里约 2.4×2.4 个细像素），37 格高、54 格宽（高×宽）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/smeech_size.png`：史密奇缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/tft_fx_ref.png` 是金铲铲里史密奇自己的特效贴图（**灰色的形状，游戏里再染色**：爪痕、光晕、尘土、绿色拖尾），按用在我们哪张特效分好了行。只在本地用。
> - **史密奇是祖安的废铁小怪物，特效都是他的机械爪**：**白金色的细长爪痕**（三道一组、两头尖），机械臂里的**荧光绿**光，暴击时**红橙色的锯齿爆星**，灰色的废铁碎屑和撕下来的护甲片，祖安的灰土；不要魔法符文，不要光滑的霓虹光束，不要闪电。
> - **特效要亮**：每道光都有最亮一档或白色的高光，暗底上一眼能看见。**光、爪痕、冲击波、尘土没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面都**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。跳跃和挥爪的动作画在他自己的动作帧里，这里不画。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `smeech_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格左右对称——Claude 直接用这一份切格导入）；图标交付 `smeech_icon_<名字>.png`（64×64），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/smeech_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/smeech_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 被动「伏击」 | 自带暴击率；技能也能暴击，技能暴击伤害更高 | `p_hit` |
| 普攻「双爪连撕」 | 左右爪轮流挥抓 | `a_hit` |
| 技能 1 =「废铁黑客」 | 跳到射程内血最少的敌人身前，连斩 3 下；目标死了再跳一次 | `q_land` · `q_hit` |
| 技能 2 =「拆解」 | 双爪一撕，造成伤害并撕掉对方护甲几秒 | `e_hit` · `e_shred` |
| 大招 =「废铁狂潮」 | 不受控制，接连跳斩最多 5 个敌人，每跳一下叠暴击率 | `r_hit` · `r_frenzy` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、爪痕、冲击波、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- 颜色（按每条写的用）：
  - 爪痕白金（爪子的光）：`#FFFFFF`、`#FFF6D0`、`#F6D77A`、`#D9A43A`、`#8A5A1C`；
  - 荧光绿（机械臂的化学光）：`#F2FFE8`、`#B8FF8A`、`#5CF04A`、`#22B83A`、`#0E6A2A`；
  - 暴击红橙：`#FFFFFF`、`#FFE8B0`、`#FF9A3C`、`#E8402A`、`#8E1426`；
  - 废铁灰（碎屑、护甲片）：`#E8ECF0`、`#B0B8C0`、`#7A8490`、`#4A525C`、`#262A30`；
  - 祖安灰土：`#E6DCC4`、`#B8A684`、`#847250`、`#54482E`；
- 打中居中画，不旋转；地面上的圈是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、头上的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（8 张）

8 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `smeech_fx_a_hit.png`：普攻：爪子抓中，4 帧

爪子抓在人身上：**两组爪痕交叉成 X**（每组三道细长的白金色爪痕，两头尖），中心一个小白闪，几颗灰色金属碎屑往两边崩开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C), a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30).
Effect: A CLAW SCRATCH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small white flash 6 squares across in the middle; 2 two sets of THREE thin curved white-gold claw lines crossing in an X, each line 14 squares long and pointed at both ends (the X mirrored); 3 the lines thinner and fading to brass, grey steel chips flying out to both sides; 4 the last glints and chips. everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `smeech_fx_p_hit.png`：伏击：技能暴击，5 帧

技能暴击时在目标身上亮一下：一个**红橙色的锯齿爆星**（八个尖角），白色的芯，外面一圈碎裂的冲击环，几块金属碎片往四周飞。比普攻显眼得多。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a hot crit red-orange ramp (#FFFFFF, #FFE8B0, #FF9A3C, #E8402A, #8E1426), a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C), a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30).
Effect: A CRITICAL HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white core 8 squares across; 2 a jagged EIGHT-POINTED STARBURST 22 squares across, hot red-orange with a white-yellow core; 3 the star bigger and its points thinner, a broken shock ring around it, grey steel shards flying out to both sides (mirrored); 4 the star breaking into red sparks; 5 the last sparks. everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal square cells, image size 2080x416 (each cell 416x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `smeech_fx_q_land.png`：废铁黑客：落地的尘土，5 帧

他跳到目标身前落地：脚下「噗」地炸开一圈**灰土和碎屑**，几颗绿色的小火花往两边弹，最后尘土落下。画在**地上**（扁椭圆），中心在格子底部中间。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a grime dust ramp (#E6DCC4, #B8A684, #847250, #54482E), a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30), a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A).
Effect: A LANDING PUFF, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): everything on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall), centred at the bottom middle of the cell: 1 a flat dust ring 14 squares wide and 4 tall; 2 the ring 30 wide and 8 tall, puffs of grime dust rising at both ends, steel chips and a few neon-green sparks kicked out to both sides (mirrored); 3 the ring 40 wide, the dust higher and thinner; 4 the dust settling; 5 faint specks. everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal 44:16 cells, image size 3520x256 (each cell 704x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `smeech_fx_q_hit.png`：废铁黑客：连斩，4 帧

三连斩每一下：**三道竖着往下的爪痕**（中间那道直，两边的往外弯，像扇子一样张开），白金色的爪痕边上带一点**荧光绿**的光，火花往两边溅。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C), a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A), a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30).
Effect: A TRIPLE CLAW SLASH, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 three thin white-gold slash lines 18 squares long raking DOWN, the middle one straight, the outer two curving outwards like a fan (mirrored), each pointed at both ends; 2 the lines fully drawn with a neon-green glow along their edges, sparks spraying to both sides; 3 the lines thinner, fading to brass and green; 4 the last glints. everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 4 equal 22:24 cells, image size 1408x384 (each cell 352x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `smeech_fx_e_hit.png`：拆解：撕开护甲，5 帧

双爪往两边一撕：**两道大爪痕从中间往左右两边撕开**（像把东西扯成两半），中间迸出几块**灰色的碎甲片**往两边飞，绿色火花。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C), a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30), a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A).
Effect: A TEARING RIP, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 8 squares across in the middle; 2 two big curved claw sweeps (each three white-gold lines) tearing from the middle out to the left and to the right, 26 squares across in all (mirrored); 3 grey steel ARMOUR PLATE fragments (3-5 squares, angular, a lit edge) bursting out of the middle to both sides with neon-green sparks; 4 the plates farther and tumbling, the claw lines fading; 5 the last chips. everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal 30:26 cells, image size 2400x416 (each cell 480x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `smeech_fx_e_shred.png`：拆解：被撕掉护甲（减护甲），6 帧循环

被撕掉护甲的人头顶：一块**裂成两半的灰色小盾牌**（中间一道锯齿裂缝），两半慢慢往外掉，裂缝里闪一点绿光。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30), a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A).
Effect: A BROKEN ARMOUR MARK OVER THE HEAD, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): in the cell (it rides over the unit's head) a small grey steel SHIELD shape 10 squares wide and 11 tall split down the middle by a jagged crack, the two halves a square apart; frames 1-6 the halves rocking a square outwards and back, a neon-green glint flickering in the crack. everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 16:14 cells, image size 1536x224 (each cell 256x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `smeech_fx_r_hit.png`：废铁狂潮：跳斩打中，5 帧

大招每跳一下打中：**两组三道的大爪痕交叉成 X**，比普攻大得多，爪痕周围裹着**荧光绿**的光，中心白闪，火花和碎屑往四周飞。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C), a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A), a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30).
Effect: A FRENZY SLASH, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares across; 2 two sets of THREE thick claw lines crossing in a big X 26 squares across, white-gold cores with neon-green glowing edges (the X mirrored); 3 the lines at full length, sparks and steel chips flying out in all directions (mirrored); 4 the lines thinning to green; 5 the last green glints. everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 5 equal square cells, image size 2400x480 (each cell 480x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `smeech_fx_r_frenzy.png`：废铁狂潮：狂潮状态，6 帧循环

大招期间他身上：身体两侧往上窜**荧光绿的速度线**（细长的竖条，一闪一闪），脚下一圈淡绿光圈，几点绿色光点往上飘。身体位置留空。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A), a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C).
Effect: A FRENZY AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the crouching gremlin stands in the middle, not drawn: 53 squares wide and 36 tall: at both sides of him (mirrored) a few thin vertical neon-green SPEED STREAKS (1 square wide, 6-14 tall) flickering upward, a faint green ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 50 squares wide and 8 tall at the bottom, a few bright green motes drifting up; frames 1-6 the streaks shooting up and fading in turn. The middle (the body) left empty. everything is a ZAUN GREMLIN's scrap-metal claws: sharp white-gold CLAW SLASH lines (thin, curved, pointed at both ends, in sets of three like claw marks), NEON-GREEN chem glow from his mechanical arms, sparks and chips of grey scrap steel, Zaun grime; flat shades, crisp shapes; no magic runes, no smooth neon beams, no lightning.
Layout: one horizontal row of 6 equal 60:44 cells, image size 5760x704 (each cell 960x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## 技能图标（3 个，64×64）

### 图标 1. `smeech_icon_skill.png`：技能 1「废铁黑客」图标

一只黄铜机械爪从右上往左下扑下来，后面拖着三道白金色的爪痕，爪子上的绿灯发亮。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive-green frame with little riveted brass corners, a deep grimy purple-navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a big brass MECHANICAL CLAW (an olive-green metal bracer with a glowing neon-green diamond light, five long thin hooked brass fingers) diving down from the upper right to the lower left, three white-gold claw slash lines trailing behind it, its green light glowing. Colours: a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C), a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A), a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30). No text, no letters.
```

### 图标 2. `smeech_icon_skill2.png`：技能 2「拆解」图标

两只爪子把一块灰色的盾牌从中间撕成两半，碎甲片往两边飞，裂缝里冒绿光。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive-green frame with little riveted brass corners, a deep grimy purple-navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: two brass claws tearing a grey steel SHIELD apart down the middle, the halves pulled to the left and to the right, armour chips flying, neon-green light bursting from the crack. Colours: a scrap steel ramp (#E8ECF0, #B0B8C0, #7A8490, #4A525C, #262A30), a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C), a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A). No text, no letters.
```

### 图标 3. `smeech_icon_ult.png`：大招「废铁狂潮」图标

一串折线形的绿色跳跃轨迹在画面里来回折，每个折点上一个白金色的 X 爪痕，正中一个红橙色的暴击爆星。

```text
A 64x64 SKILL ICON (one picture, not a sheet): a square tile with a 2-square dark olive-green frame with little riveted brass corners, a deep grimy purple-navy inside, the symbol big and centred, lit from the upper left; pixel art at 2 px a square (32 x 32 squares), chunky and readable at 64 px: a ZIGZAG trail of neon-green leaps bouncing across the tile, a small white-gold X of claw marks at each corner of the zigzag, a red-orange critical starburst in the middle. Colours: a neon chem green ramp (#F2FFE8, #B8FF8A, #5CF04A, #22B83A, #0E6A2A), a white-to-brass claw light ramp (#FFFFFF, #FFF6D0, #F6D77A, #D9A43A, #8A5A1C), a hot crit red-orange ramp (#FFFFFF, #FFE8B0, #FF9A3C, #E8402A, #8E1426). No text, no letters.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `smeech_fx_a_hit` | view_effects `tft_smeech_a_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `smeech_fx_p_hit` | view_effects `tft_smeech_p_hit`（跟随目标，z 3；左右对称） | 26 × 26 |
| `smeech_fx_q_land` | view_effects `tft_smeech_q_land`（留在他落地的地上，z -1；左右对称） | 44 × 16 |
| `smeech_fx_q_hit` | view_effects `tft_smeech_q_hit`（跟随目标，z 2；左右对称） | 22 × 24 |
| `smeech_fx_e_hit` | view_effects `tft_smeech_e_hit`（跟随目标，z 2；左右对称） | 30 × 26 |
| `smeech_fx_e_shred` | view_buffs `tft_smeech_e_shred`（跟随被撕的人，头顶，z 3；左右对称） | 16 × 14 |
| `smeech_fx_r_hit` | view_effects `tft_smeech_r_hit`（跟随目标，z 2；左右对称） | 30 × 30 |
| `smeech_fx_r_frenzy` | view_buffs `tft_smeech_r_frenzy`（跟随他，z 3；左右对称） | 60 × 44 |
| `smeech_icon_skill` | skill_icons[0] `asset/tft/icons/tft_smeech_skill` | 64 × 64 |
| `smeech_icon_skill2` | skill_icons[1] `asset/tft/icons/tft_smeech_skill2` | 64 × 64 |
| `smeech_icon_ult` | skill_icons[2] `asset/tft/icons/tft_smeech_ult` | 64 × 64 |

- 一张表：`asset/tft/effects/tft_smeech_fx`，tag = 名字。
- 全部断言左右对称。
- q_land / q_hit / r_hit / p_hit 由 tft.dll 播（--plain 的数据自己播 q_land / q_hit / r_hit）。
- 用 `pixel_1x/` 切格（import_scar_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
