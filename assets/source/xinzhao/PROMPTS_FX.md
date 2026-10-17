# 德邦总管 赵信：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型和动作已定（`design/xinzhao_design.png`，8 倍，42 行）。
> - 大小对照 `design/xinzhao_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。赵信 65×42 格（含斜架在身后的长枪，人约 30 格宽）。每条写的大小都是游戏像素（格）。
> - `design/xinzhao_shots.png`：E、W、R、被动第三下和待机的定稿动作（4 倍），青色十字是特效的起点（站位点或胸口），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里赵信自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟：**普攻、Q 三重爪击、被动、挑战标记、大招护卫光是德玛西亚金色（白色的芯）；W 的电刺、E 的冲锋、R 的新月刃光是电光蓝白色（带一点金边）；减速和尘土用暗蓝紫色**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **绕着人的刃光、围着人的光只画边，中间留空**，不然会把人整个挡住。
> - 特效照下面第 1–20 条和「所有特效图的规则」画，每张一个 PNG，文件名 `xinzhao_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`xinzhao_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「果决」 | 长枪突刺；每第三下大挥，额外伤害并回血 | `xinzhao_fx_a_hit` · `xinzhao_fx_p_hit` · `xinzhao_fx_p_heal` |
| 技能 1 = E「无畏冲锋」+ Q「三重爪击」 | 冲向目标，落地时周围敌人受到伤害并减速；之后 3 下强化普攻，第 3 下击飞 | `xinzhao_fx_e_dash` · `xinzhao_fx_e_land` · `xinzhao_fx_e_hit` · `xinzhao_fx_e_slow` · `xinzhao_fx_q_marks` · `xinzhao_fx_q_hit` · `xinzhao_fx_q3_up` |
| 技能 2 = W「风斩电刺」 | 先在身前横扫一刀，再往前直刺一道电光，打中的减速 | `xinzhao_fx_w_slash` · `xinzhao_fx_w_thrust` · `xinzhao_fx_w_hit` · `xinzhao_fx_w_hit2` · `xinzhao_fx_w_slow` |
| 大招 = R「新月护卫」 | 绕身横扫一圈，被挑战的目标留在身边，其余敌人被击退；之后 3 秒减伤 | `xinzhao_fx_r_tell` · `xinzhao_fx_r_sweep` · `xinzhao_fx_r_hit` · `xinzhao_fx_r_chal` · `xinzhao_fx_r_guard` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刃光、光、闪电、尘土、火花没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的挑战纹章有 1 格深色描边（`#10102A`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 德玛西亚金（普攻、Q、被动、挑战、护卫光）：`#FFFFFF`、`#FFF4C0`、`#FFD45A`、`#F0A020`、`#C06A10`、`#7A3A08`；
  - 电光蓝白（W 电刺、E 冲锋、R 新月刃光）：`#FFFFFF`、`#D8F4FF`、`#8AD8FF`、`#3A9CF0`、`#1E5AC0`、`#12307A`；
  - 暗蓝紫（减速、尘土、阴影）：`#6A5AC8`、`#4A3A9A`、`#2E2468`、`#1C1640`；
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- **`w_thrust` 上下必须对称**：它是一条直线的画面，游戏里会按施放方向转动，朝左放时整张转半圈，不对称的话会上下颠倒（红色方朝左放最常见）。
- 画在他身上或脚下的画面（`e_dash`、`e_land`、`w_slash`、`p_heal`、`r_tell`、`r_sweep`、`r_guard`）按每条写的站位画，**格子里留出空的人形位置，不要画人**。挂在人身上或脚下的循环画面（`r_guard`、`q_marks`、`r_chal`、`e_slow`、`w_slow`）左右对称或不分左右，因为人朝左朝右都用同一张。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：E 落地的范围半径 20000、W 电刺长 60000、R 横扫半径 36000）。

### 1. `xinzhao_fx_a_hit.png`：普攻刺中（目标身上），4 帧

长枪刺中：一道从左往右的白金色突刺光，刺中的地方一下白色闪光，几点金色火星往前飞（参考 HIT02、Spark_Vertical、Star）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: a SPEAR THRUST HIT, 4 frames: 1 a short straight streak of white-gold light 12 squares long coming in from the left to the center; 2 a white four-pointed star flash at the center 8 squares across, 5 gold sparks flying out to the right; 3 the flash gone, sparks further out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `xinzhao_fx_p_hit.png`：被动「果决」第三下打中（目标身上），5 帧

每第三下：长枪大挥砍中，一道从上往下的宽金色月牙弧光，砍中处白光炸开，金色火星四散（参考 Passive_Swipe_B_Alpha、BlastShapes、Z_StarGlow）。约 20 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: a HEAVY SPEAR SWING HIT, 5 frames: 1 a wide crescent arc of gold light 18 squares long sweeping from the upper left down through the center; 2 a white burst at the center 12 squares across, the arc thinning; 3 eight gold sparks and four small four-pointed stars flying out; 4 sparks further out; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `xinzhao_fx_p_heal.png`：被动「果决」回血（施法者身上），5 帧

第三下回血：他身上一下暖金色的光，几个金色光点和小「+」形火花从身上往上升（参考 Q_StarGlow、Z_Glow01、Passive_heal）。中间是人，不要画人。左右对称。5 帧：1 胸口金光，2–4 光点和「+」往上升，5 淡去。约 22 格宽、32 格高，胸口在格子中间偏下（格子底部往上 12 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: a WARM GOLDEN HEAL on a figure (do NOT draw the figure; leave its place empty; symmetric left and right), 5 frames: 1 a soft gold glow at the chest point 10 squares across; 2 six small gold plus-shaped sparks and light motes rising from it; 3 the sparks 8-16 squares above the chest; 4 near the top of the cell; 5 fading.
Layout: one horizontal row of 5 equal 11:16 cells, image size 1100x320 (each cell 220x320); the chest point 12 squares (96 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `xinzhao_fx_e_dash.png`：E 无畏冲锋：冲刺时身后的光痕（施法者身上，跟着冲过去），5 帧

E「无畏冲锋」：他持枪飞身往前扑，身后拖着一道蓝白色的电光冲刺痕，枪头前一点金光（参考 E_Wave_Texture、W_SpearSmear、Typhoon、R_frost_line）。画在人物上面，中间是人，不要画人：光痕从人的位置往**左后方**拖出去，人前面（右边）只有一点枪头的金光。5 帧：1 光痕出现，2–3 最长（约 30 格），4 变短、碎成电光丝，5 散去。约 44 格宽、24 格高，站位点在格子底部往上 4 格、左右正中。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A) and a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: a CHARGE STREAK behind a leaping figure (do NOT draw the figure; leave its place empty), 5 frames: 1 a streak of electric blue-white light appears behind the figure's place; 2-3 the streak at its longest, trailing 30 squares to the LEFT behind the figure at waist height (7-12 squares above the standing point), thin white lightning threads along it, a small gold glint at the spear's point 8 squares right of the figure; 4 the streak shorter, breaking into blue threads; 5 fading threads.
Layout: one horizontal row of 5 equal 11:6 cells, image size 1760x192 (each cell 352x192); the standing point 4 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `xinzhao_fx_e_land.png`：E 落地：脚下的冲击圈（落地点，不跟随，画在人物下面），5 帧

冲到目标身边落地：脚下一圈蓝白色的冲击波往外扩（从斜上方看是扁椭圆，宽是高的 2 倍，约 40 格宽），带一点金色火星和地面的裂纹尘土（参考 E_Nova_Mult、BA_Underglow、Q_WallDestruction、Z_explosion_smoke）。中间是人，不要画人。左右对称。5 帧：1 脚下白光，2–3 圈往外扩，4 圈到边变细、尘土，5 散去。约 44 格宽、20 格高，圈的中心在格子正中。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A), a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08) and a dusk violet ramp (#6A5AC8, #4A3A9A, #2E2468, #1C1640).
Effect: a LANDING SHOCKWAVE on the ground round a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), seen from above at an angle, 5 frames: 1 a white flash at the center; 2-3 a ring of electric blue-white light expanding over a flattened ellipse twice as wide as tall up to 40 squares wide, gold sparks thrown up along it; 4 the ring thin at its edge, violet dust; 5 fading dust.
Layout: one horizontal row of 5 equal 11:5 cells, image size 1760x160 (each cell 352x160); the ellipse's center at the center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `xinzhao_fx_e_hit.png`：E 冲锋命中（敌人身上），4 帧

冲锋撞到周围的敌人：一下蓝白色的电光爆开，几道短短的闪电和金色火星（参考 R_Braum_Base_E_Block_Spark、W_Global_SS_Ghost_Swirl）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A) and a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: a CHARGE IMPACT, 4 frames: 1 a white flash at the center 8 squares across; 2 an electric blue-white burst 14 squares across with 4 short jagged lightning threads, 3 gold sparks; 3 the burst breaking up; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `xinzhao_fx_e_slow.png`：E 减速：脚下的标记（敌人身上，循环 0.5 秒），4 帧

被冲锋减速：脚下一圈淡蓝紫色的光圈，几道短短的电光丝往下滑。中间是人，不要画人。左右对称，4 帧无缝循环。约 16 格宽、6 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A) and a dusk violet ramp (#6A5AC8, #4A3A9A, #2E2468, #1C1640).
Effect: a SLOW MARK at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a flattened ellipse of pale blue-violet light on the ground round the feet (twice as wide as tall, 14 squares wide), 3 short blue streaks sliding DOWN into it a square each frame.
Layout: one horizontal row of 4 equal 8:3 cells, image size 2048x192 (each cell 512x192); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `xinzhao_fx_q_marks.png`：Q 三重爪击：头上的剩余次数标记（自己身上，循环），3 行 × 4 帧

冲锋落地后接三重爪击：他头顶亮着金色的爪印标记，还剩几下就有几道（第 1 行 3 道、第 2 行 2 道、第 3 行 1 道，每道是一条斜着的金色光爪痕），金光一明一暗（参考 Q_StarGlow、Q_Spark、Z_Streak）。每行 4 帧无缝循环。约 14 格宽、8 格高，标记的底边在格子底部（导入时放到头顶）。**三行的爪痕大小、位置要一样**，只差道数。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: COMBO COUNT MARKS over a head, 3 rows of 4 frames, each row a seamless loop: row 1 THREE short slanted claw strokes of gold light side by side (each 6 squares tall, 3 squares apart, leaning right like talon marks, white cores), row 2 the same marks but only the left TWO, row 3 only the left ONE, in the same places; in each row a soft gold glow pulsing brighter and dimmer, a tiny spark twinkling.
Layout: a grid of 3 rows x 4 columns of equal 7:4 cells, image size 1792x768 (each cell 448x256); the marks centered, their bottom near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `xinzhao_fx_q_hit.png`：Q 三重爪击前两下打中（敌人身上），4 帧

三重爪击的强化刺击：一道金色的爪痕突刺光，刺中处金星闪光（参考 Q_Swipe_C、Q_2_Swipe_Mid、Q_StarGlow）。比普攻的刺中亮、金。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: an EMPOWERED THRUST HIT, 4 frames: 1 three parallel slanted gold claw streaks 12 squares long striking into the center; 2 a bright gold star flash at the center 10 squares across; 3 gold sparks flying out; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `xinzhao_fx_q3_up.png`：Q 第三下击飞（敌人身上），5 帧

第三下把敌人挑上天：从脚下往上一道竖直的金色上挑弧光，脚下一圈尘土，几块碎石和金色火星往上飞（参考 Q_Swipe_B、Q_Mound_Shadow、Q_Smoke_3、Q_WallDestruction）。中间是人，不要画人。5 帧：1 脚下金光和尘土，2 上挑的弧光从下往上冲到头顶，3 最高、火星往上，4 尘土落下，5 散去。约 20 格宽、32 格高，人的脚在格子底部往上 4 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08) and a dusk violet ramp (#6A5AC8, #4A3A9A, #2E2468, #1C1640).
Effect: a KNOCK-UP STRIKE on a figure (do NOT draw the figure; leave its place empty), 5 frames: 1 a gold flash and a puff of violet dust at the feet; 2 a tall upward crescent slash of gold light rising from the feet past the head (28 squares tall); 3 the slash at its top, gold sparks and small rock chips flying up; 4 the dust settling, sparks falling; 5 fading.
Layout: one horizontal row of 5 equal 5:8 cells, image size 1000x320 (each cell 200x320); the figure's feet 4 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `xinzhao_fx_w_slash.png`：W 风斩：身前的横扫月牙（施法者身上，不跟随），4 帧

W「风斩电刺」的第一下：长枪在**身前**横扫出一道宽的半月形风刃，金白色的刃带一点蓝色的风（参考 W_swipe、W_Swipe_B_Dissolve、Typhoon、Z_SwipeText01）。半月从他身后上方扫到身前下方，开口朝左，刃在右半边。不要画人。4 帧：1 刃从上方出现，2 扫满半圈（最亮），3 变细、风丝飘散，4 散去。约 40 格宽、30 格高，站位点在格子底部往上 4 格、左边 12 格处（刃在人前面）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08) and an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A).
Effect: a WIDE CRESCENT WIND SLASH in front of a figure (do NOT draw the figure; leave its place empty), 4 frames: 1 the head of a broad crescent blade of white-gold light appears above the figure's place; 2 the full crescent sweeping round in FRONT of the figure (on the right side of it), 26 squares tall and 22 wide, its opening facing left toward the figure, thin blue wind strands along its outer edge; 3 the crescent thinning, the wind strands drifting off to the right; 4 fading strands.
Layout: one horizontal row of 4 equal 4:3 cells, image size 1280x240 (each cell 320x240); the figure's standing point 4 squares (32 px) above the bottom and 12 squares (96 px) from the cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `xinzhao_fx_w_thrust.png`：W 电刺：向前直刺出去的闪电（一条线，按方向转动），5 帧

W 的第二下：从他身前往前射出一道长长的蓝白色电光枪刺，像一支闪电化成的长枪往前冲，尖头在右（参考 W_Mis_Base、W_Mis_BrightLead、W_SpearSmear_v2、W_LungeMult、R_frost_line）。这张会按施放方向转动（朝左放时转半圈），所以**上下要对称**（上面和下面一样，不分上下）。5 帧：1 左端一点白光，2 电光枪往右冲到一半，3 冲满整条（约 58 格长，枪尖在右端），4 变细、碎成电光丝，5 散去。约 60 格长、10 格高，整条居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A).
Effect: a LIGHTNING SPEAR THRUST along a line, 5 frames, the picture SYMMETRIC TOP AND BOTTOM (it is turned to face the cast direction): 1 a white spark at the left end of the line; 2 a long spear-shaped bolt of electric blue-white light shooting right, reaching the middle, a white core, short lightning threads above and below it mirrored; 3 the bolt along the whole line, 58 squares long, its sharp white point at the right end, 7 squares thick at its widest; 4 the bolt thinning, breaking into blue threads; 5 fading threads.
Layout: one horizontal row of 5 equal 6:1 cells, image size 3840x128 (each cell 768x128 - keep the 6:1 shape); the line along the horizontal center of every cell, from 1 square inside the left edge to 1 square inside the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `xinzhao_fx_w_hit.png`：W 风斩打中（敌人身上），4 帧

被横扫的风刃扫到：一道金白色的横斩光和几缕风（参考 W_swipe、Typhoon）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08) and an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A).
Effect: a SLASH HIT, 4 frames: 1 a horizontal white-gold slash streak 14 squares long through the center; 2 a white flash at the center 7 squares across, thin blue wind wisps; 3 sparks and wisps drifting; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `xinzhao_fx_w_hit2.png`：W 电刺打中（敌人身上），4 帧

被电光枪刺中：一下蓝白色的电光爆开，几道闪电劈出去（参考 R_Braum_Base_E_Block_Spark、W_Global_SS_Ghost_Swirl、W_PassiveMark）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A).
Effect: a LIGHTNING THRUST HIT, 4 frames: 1 a white flash at the center 8 squares across; 2 an electric blue-white burst with 5 jagged lightning threads 8 squares long forking out; 3 the threads flickering, smaller; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `xinzhao_fx_w_slow.png`：W 减速：脚下的标记（敌人身上，循环 1.5 秒），4 帧

被电刺减速：脚下一圈蓝白色的电光圈，几道细闪电在圈上跳。中间是人，不要画人。左右对称，4 帧无缝循环。约 18 格宽、8 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A) and a dusk violet ramp (#6A5AC8, #4A3A9A, #2E2468, #1C1640).
Effect: a SHOCK SLOW MARK at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a flattened ellipse of electric blue light on the ground round the feet (twice as wide as tall, 16 squares wide), 3 tiny lightning threads jumping along it, moving each frame.
Layout: one horizontal row of 4 equal 9:4 cells, image size 2304x256 (each cell 576x256); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `xinzhao_fx_r_tell.png`：R 新月护卫起手：长枪转动的金光（施法者身上，跟随），4 帧

R 起手：他把长枪抡起来，身边一圈金色的转动光（像枪头转出来的圆，参考 R_Tell_WeaponSpin、R_Tell_WeaponSpin_EndGlow、R_Cas_Edge）。中间是人，不要画人。4 帧：亮的弧头每帧转 90°，后面拖着变暗的弧。约 30 格见方，胸口在格子正中。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08) and an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A).
Effect: a SPINNING SPEAR GLOW round a figure's chest (do NOT draw the figure; leave its place empty), 4 frames: a ring path 26 squares across round the center; a bright white-gold arc head moving a quarter turn each frame along it, a fading gold and pale blue trail behind it covering half the ring; small sparks thrown off.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the ring centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `xinzhao_fx_r_sweep.png`：R 新月护卫：绕身一圈的新月刃光（施法者脚下，不跟随），6 帧

R「新月护卫」：长枪绕着身体横扫一圈，地面上划出一圈蓝白色的新月形刃光（从斜上方看是扁椭圆，宽是高的 2 倍，半径约 36 格，所以约 72 格宽），刃的外沿是金色的亮边，冲击把尘土往外推（参考 R_BladeSwipe、R_BladeSwipe_AddLayer、R_Credscent_FlashFrame、R_GroundSwipe、R_Blast_Ring、R_ring）。中间是人，不要画人：前面一段从人身前（下方）经过，后面一段在人身后（上方）。6 帧：1 一段刃光在右边出现，2–3 扫满一圈（亮的刃头每帧转小半圈），4 整圈一下闪亮、往外冲，5 变细、尘土往外，6 散去。约 76 格宽、44 格高，站位点在格子正中偏下（格子底部往上 20 格）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A), a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08) and a dusk violet ramp (#6A5AC8, #4A3A9A, #2E2468, #1C1640).
Effect: a CRESCENT SWEEP all round a figure (do NOT draw the figure; leave its place empty), seen from above at an angle, 6 frames: 1 the bright head of a crescent blade of blue-white light with a gold outer edge appears at the right of the figure's place on the ground; 2-3 it sweeps round a flattened ellipse 72 squares wide and 36 tall (twice as wide as tall) round the standing point, a fading blue trail behind it; 4 the whole ring flashing bright white-blue at once, a pale shockwave pushing outward; 5 the ring thin, violet dust thrown outward; 6 fading dust.
Layout: one horizontal row of 6 equal 19:11 cells, image size 3648x528 (each cell 608x352 - keep the 19:11 shape); the figure's standing point 20 squares (160 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `xinzhao_fx_r_hit.png`：R 横扫打中（敌人身上），4 帧

被新月刃扫中：一道蓝白色的弧形斩光，金色火花（参考 R_Impact_Slash、R_Block_Spark）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A) and a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: a CRESCENT SLASH HIT, 4 frames: 1 a curved slash streak of blue-white light with a gold edge 14 squares long through the center; 2 a white flash at the center 8 squares across; 3 blue and gold sparks flying out; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `xinzhao_fx_r_chal.png`：R 挑战标记（被挑战的敌人身上，头顶，循环 1.5 秒），4 帧

被他挑战、留在身边单挑的那个敌人：头顶一个金色的德玛西亚式挑战纹章（两把交叉的长枪，中间一个小盾，有 1 格深色描边），金光一明一暗（参考 W_PassiveMark、W_Marker_Cross、R_EyeforanEye01）。4 帧无缝循环。约 12 格见方，纹章的底边在格子底部（导入时放到头顶）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08) and an electric blue-white ramp (#FFFFFF, #D8F4FF, #8AD8FF, #3A9CF0, #1E5AC0, #12307A).
Effect: a CHALLENGE EMBLEM over a head, 4 frames, a seamless loop: a small gold emblem 10 squares tall - two crossed spears behind a tiny shield, a 1-square dark outline #10102A - with a white glint; a soft gold glow round it pulsing brighter and dimmer; the emblem bobs a square.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the emblem centered, its bottom near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `xinzhao_fx_r_guard.png`：R 之后 3 秒：身上的护卫光（循环），4 帧

R 之后 3 秒减伤：他身后一道金橙色的护卫光——身后背上一对展开的金色光翼标志（参考 R_InvulnShield_Symbol 的橙金色翼形），身体两边一圈淡淡的金色光罩边，脚下一圈扁的金光（参考 R_InvulnShield_Sphere、R_Aura_Self、R_Braum_Base_I_shield_glow）。画在人物下面，所以只有从人身边、头顶露出来的部分看得见。中间是人，不要画人。**左右对称**（人朝左朝右都用同一张）。4 帧无缝循环（光罩边一明一暗、光翼微微扇动）。约 30 格宽、44 格高，脚在格子底部往上 4 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, lightning or sparks (only the solid challenge emblem gets a 1-square dark outline #10102A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Demacian gold ramp (#FFFFFF, #FFF4C0, #FFD45A, #F0A020, #C06A10, #7A3A08).
Effect: a GUARDIAN AURA round a standing figure (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: behind the figure's upper body a pair of spread wing shapes of orange-gold light (each 10 squares long, rising from the shoulders' height outward and up, like a heraldic winged emblem), a thin dome-shaped rim of pale gold light round the figure's place (28 squares wide, 40 tall, edge only, the middle empty), a flattened ellipse of gold light on the ground round the feet; the rim and wings pulse a little each frame.
Layout: one horizontal row of 4 equal 15:22 cells, image size 960x352 (each cell 240x352); the figure's feet 4 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `xinzhao_fx_a_hit` | view_effects `league_xinzhao_a_hit`（跟随，画在人物上面） | 14 |
| `xinzhao_fx_p_hit` | view_effects `league_xinzhao_p_hit`（跟随，画在人物上面） | 20 |
| `xinzhao_fx_p_heal` | view_effects `league_xinzhao_p_heal`（施法者身上，不跟随；格子中心放到他的胸口） | 22 × 32 |
| `xinzhao_fx_e_dash` | view_effects `league_xinzhao_e_dash`（BIG，施法者身上，跟随；格子里的站位点放到他的站位点） | 44 × 24 |
| `xinzhao_fx_e_land` | view_effects `league_xinzhao_e_land`（BIG，施法者脚下，不跟随，z -1） | 44 × 20 |
| `xinzhao_fx_e_hit` | view_effects `league_xinzhao_e_hit`（跟随，画在人物上面） | 16 |
| `xinzhao_fx_e_slow` | view_buffs `league_xinzhao_e_slow`（循环，画在脚下） | 16 × 6 |
| `xinzhao_fx_q_marks` | view_buffs `league_xinzhao_q_1` / `q_2` / `q_3`（循环，画在人物上面，头顶） | 14 × 8 |
| `xinzhao_fx_q_hit` | view_effects `league_xinzhao_q_hit`（跟随，画在人物上面） | 16 |
| `xinzhao_fx_q3_up` | view_effects `league_xinzhao_q3_up`（跟随，画在人物上面） | 20 × 32 |
| `xinzhao_fx_w_slash` | view_effects `league_xinzhao_w_slash`（BIG，施法者身上，不跟随；格子里的站位点放到他的站位点） | 40 × 30 |
| `xinzhao_fx_w_thrust` | view_projectiles `league_xinzhao_w_thrust`（BIG，LineRangeProjectile 60000 长：画面按方向转动，所以**上下必须对称**） | 60 × 10 |
| `xinzhao_fx_w_hit` | view_effects `league_xinzhao_w_hit`（跟随，画在人物上面） | 14 |
| `xinzhao_fx_w_hit2` | view_effects `league_xinzhao_w_hit2`（跟随，画在人物上面） | 16 |
| `xinzhao_fx_w_slow` | view_buffs `league_xinzhao_w_slow`（循环，画在脚下） | 18 × 8 |
| `xinzhao_fx_r_tell` | view_effects `league_xinzhao_r_tell`（BIG，施法者身上，跟随；格子中心放到他的胸口） | 30 × 30 |
| `xinzhao_fx_r_sweep` | view_effects `league_xinzhao_r_sweep`（BIG，施法者身上，不跟随；格子里的站位点放到他的站位点） | 76 × 44 |
| `xinzhao_fx_r_hit` | view_effects `league_xinzhao_r_hit`（跟随，画在人物上面） | 16 |
| `xinzhao_fx_r_chal` | view_buffs `league_xinzhao_r_chal`（循环，画在人物上面，头顶） | 12 × 12 |
| `xinzhao_fx_r_guard` | view_buffs `league_xinzhao_r_guard`（BIG，循环，画在人物下面，z -1） | 30 × 44 |

- `q_marks` 的三行拆成 view_buffs `q_1`（3 道）、`q_2`（2 道）、`q_3`（1 道）；`r_guard`、`e_land` 的 z 是 -1（人物下面），`q_marks`、`r_chal` 画在头顶。
- 施法者身上的画面按 `design/xinzhao_shots.png` 的十字把起点挪过去；晚于第一 tick 播放的（`p_heal`、`e_land`、`w_slash`、`r_sweep`）`is_follow` 为 false（红方方向）；`e_dash`、`r_tell` 在动作第一 tick 播、跟随。
- `w_thrust` 是 LineRangeProjectile 的画面：60 格长、按方向转动，导入后用 `lint_mod.py` 量它上下翻转后的差别（要几乎为 0）。
- 清掉 Codex 给光和闪电描的最深色边（`import_riven.py` 的 `unrim`，挑战纹章保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。
