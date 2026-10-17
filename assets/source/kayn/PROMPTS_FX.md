# 影流之镰 凯隐：给 Codex 的特效提示词（第 3 步）

> **这一份是 23 张特效图。** 造型和动作已定（`design/kayn_design.png` 本体 40×40 格，`kayn_darkin_design.png` 暗裔杀手，`kayn_shadow_design.png` 影流刺客，都是 8 倍）。
> - 大小对照 `design/kayn_size.png`：三张定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，最右边是原版剑士。每条写的大小都是游戏像素（格）。
> - `design/kayn_shots.png`：普攻、Q 旋转、W 蓄力和下砸、R 俯冲、变身那几帧的动作（4 倍），青色十字是脚下的位置（导入时 Claude 把套在人身上的特效对到这里）。凯隐的动作条还在画，这张先用英雄联盟原版同一帧（按游戏尺寸取色）：看动作和大小用，长相以定稿造型为准。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里凯隐自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，最后一行是英雄联盟给三种形态上色用的色带，只在本地用，不要提交。颜色和英雄联盟一样：**本体是暗紫色的影子转成深红、亮红，白芯，Q 的刃光边缘是青蓝色；暗裔杀手（拉亚斯特）是黑红、血红、橙、淡金；影流刺客是靛蓝、蓝、青、淡青，配黑紫色的烟**。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。凯隐的颜色本来就暗，更要注意：每个形状都要用最亮的几档和白色或淡色的芯，暗底上一眼能看见；烟也要用烟色带里亮的几档。
> - 特效照下面第 1–23 条和「所有特效图的规则」画，每张一个 PNG，文件名 `kayn_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。另外 8 张（`hit_d`、`hit_s`、`q_spin_d`、`q_spin_s`、`w_wind_d`、`w_wind_s`、`r_mark_d`、`r_mark_s`）由 Claude 从本体那张换色，不用画。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`kayn_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「暗裔魔镰」 | 用技能打中英雄攒两种印记（主包：技能打中身边的英雄攒暗裔、W 只打中远处的英雄攒影流；装了扩展包照英雄联盟：打近战英雄攒暗裔、打远程英雄攒影流），先攒满的那种变身：暗裔杀手对英雄的伤害按比例回血，影流刺客进入战斗后几秒里打英雄追加一下伤害 | `kayn_fx_hit`（+ 换色 `hit_d`、`hit_s`）· `kayn_fx_sa_hit` · `kayn_fx_tf_d` · `kayn_fx_tf_s` · `kayn_fx_form_d` · `kayn_fx_form_s` |
| 技能 1 = Q「巨镰横扫」+ E「掠影步」 | 往前冲刺，原地转一圈镰刀，冲刺和旋转都造成伤害；暗裔杀手额外按最大生命值伤害；转完以后几秒里移速变快、能穿墙并回血 | `kayn_fx_q_dash` · `kayn_fx_q_spin`（+ 换色 `q_spin_d`、`q_spin_s`）· `kayn_fx_q_hit` · `kayn_fx_q_d_hit` · `kayn_fx_ghost` |
| 技能 2 = W「利刃纵贯」 | 蓄力 0.55 秒后往前劈出一长条，打中的减速；暗裔杀手的会把人击飞，影流刺客的打得更远 | `kayn_fx_w_wind`（+ 换色 `w_wind_d`、`w_wind_s`）· `kayn_fx_w_line` · `kayn_fx_w_line_d` · `kayn_fx_w_line_s` · `kayn_fx_w_hit` · `kayn_fx_w_slow` |
| 大招 = R「裂舍影」 | 扑向最近打过的敌方英雄、钻进他身体里（这段时间无法选中），2 秒后破体而出造成伤害；暗裔杀手按最大生命值伤害并回血，影流刺客刷新被动 | `kayn_fx_r_dive` · `kayn_fx_r_enter` · `kayn_fx_r_mark`（+ 换色 `r_mark_d`、`r_mark_s`）· `kayn_fx_r_exit` · `kayn_fx_r_exit_d` · `kayn_fx_r_exit_s` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、刀光、烟、火星没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用；本体那几张只用本体的色带，Claude 换色时按色带一档对一档换成暗裔、影流的）：
  - 本体：影子转深红（大部分本体特效）：`#FFFFFF`、`#FFC2CC`、`#FF4058`、`#D61C39`、`#8E1834`、`#46205E`、`#22163A`；
  - 本体 Q 的青蓝刃光：`#D6EFFF`、`#3FE9FC`、`#1BAEC3`、`#2165BD`；
  - 暗裔杀手：血红到淡金：`#FFFFFF`、`#FFEF9A`、`#F7D48E`、`#ECA173`、`#F74508`、`#C03233`、`#9C2429`、`#571E21`；
  - 影流刺客：靛蓝到淡青：`#FFFFFF`、`#D6F7FF`、`#8EE3F7`、`#3FE9FC`、`#73ABEC`、`#3C2EBA`、`#31209C`、`#2E1E57`；
  - 暗影烟（亮的在前）：`#9A8EC8`、`#6A5C9E`、`#463A74`、`#2C2250`、`#181030`；
- **贴地的方向类特效朝右画，而且上下对称**（`w_line`、`w_line_d`、`w_line_s`）：游戏会把它转到出招方向，朝左时整张会上下翻转，所以里面不要有分上下的东西。
- **画在凯隐身上的特效按每条写的站位画**（`q_dash`、`q_spin`、`r_dive`、`tf_d`、`tf_s`、`form_d`、`form_s`、`ghost`；`w_wind` 画在格子正中间）：游戏把它画在凯隐身上，他朝左时整张左右镜像。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。挂在人身上的循环画面（`w_slow`、`r_mark`）左右对称，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（23 张）

23 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 旋转半径 24000，W 长 62000、影流 80000、宽 7000）。

### 1. `kayn_fx_hit.png`：普攻打中（目标身上，本体），4 帧

本体普攻砍中：一道弯弯的深红色镰刀刀痕闪一下，刀痕外缘一道细的暗紫色影子，中间白芯（参考 BA2、BA1_tex、hit_radial、BasicAttack_color 最下一行）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a SCYTHE HIT, 4 frames: 1 a white-pink flash; 2 a sharp curved slash mark 12 squares long (a crescent from upper left to lower right) with a white core, red and crimson edges and a thin dark violet shadow along its outer curve; 3 the crescent thinner and darker, 4 crimson sparks flying off; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kayn_fx_sa_hit.png`：影流刺客被动「暗影之镰」追加伤害（目标身上），5 帧

影流刺客进入战斗后的几秒里打英雄会追加一下伤害：目标身上交叉闪过两道青白色的细刀光，带一团黑紫色的烟（参考 Assassin_thinslash、Assassin_fire、Primary_shadow_smoke_shard）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a shadow-blue ramp (#FFFFFF, #D6F7FF, #8EE3F7, #3FE9FC, #73ABEC, #3C2EBA, #31209C, #2E1E57) and a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030).
Effect: a SHADOW STRIKE, 5 frames: 1 a pale cyan glint; 2 two thin crossing slashes 14 squares long (an X) of white and pale cyan light with blue edges; 3 the slashes at full length, a puff of dark indigo smoke bursting out round their crossing; 4 the slashes fade, the smoke spreads into wisps; 5 fading wisps.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kayn_fx_tf_d.png`：变身暗裔杀手（施法者身上，不跟随），8 帧

形态定下、拉亚斯特吞掉凯隐：地上一圈血红色的裂纹炸开，一道红橙色的光柱从脚下冲上去，红色的闪电在身边乱跳，最后一阵火星往上飘（参考 Slayer_Transform、Slayer_lightning、Slayer_transform、Slayer_Transformation_ground_cracks、Slayer_Transform_beat4_beam、Slayer_orange_glow）。中间是人，不要画人。脚在格子底部往上 6 格的中间。约 48 格宽、52 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood-and-gold ramp (#FFFFFF, #FFEF9A, #F7D48E, #ECA173, #F74508, #C03233, #9C2429, #571E21).
Effect: a DEMONIC TRANSFORMATION BURST round a figure (do NOT draw the figure; leave its place empty), 8 frames: 1 a red flash at the figure's feet; 2 blood-red cracks run out over the ground round the feet (an ellipse twice as wide as tall), a pillar of red-orange light shoots up round the figure; 3 the pillar at full height with a pale gold core, 4 jagged red lightning bolts crackling round the figure; 4 the pillar flares orange, the cracks glow, sparks fly out; 5 the pillar thins, red lightning at the edges; 6 the light falls back, the cracks dimming; 7 rising embers; 8 a few embers.
Layout: one horizontal row of 8 equal 12:13 cells, image size 3840x520 (each cell 480x520); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kayn_fx_tf_s.png`：变身影流刺客（施法者身上，不跟随），8 帧

形态定下、凯隐压制了拉亚斯特：脚下一圈黑紫色的影子漩涡转起来，几条蓝色的暗影触手从地上卷上去缠住他，一道青蓝色的闪光，最后黑烟往上散（参考 Assassin_Transform_mesh、Assassin_transform_tendrils、assassin_transform_ground_swirl、Assassin_Transform_thinclouds、assassin_transform_weaponsmoke）。中间是人，不要画人。脚在格子底部往上 6 格的中间。约 48 格宽、52 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a shadow-blue ramp (#FFFFFF, #D6F7FF, #8EE3F7, #3FE9FC, #73ABEC, #3C2EBA, #31209C, #2E1E57) and a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030).
Effect: a SHADOW TRANSFORMATION round a figure (do NOT draw the figure; leave its place empty), 8 frames: 1 a dark swirl appears on the ground round the feet (an ellipse twice as wide as tall); 2 the swirl turns, 4 blue shadow tendrils rise from it round the figure; 3 the tendrils curl up to above the head, glowing cyan at their tips; 4 a bright pale cyan flash where they meet above the head, the swirl at full size; 5 the tendrils dissolve into indigo smoke; 6 smoke drifts up, cyan glints; 7 thin wisps; 8 a few wisps.
Layout: one horizontal row of 8 equal 12:13 cells, image size 3840x520 (each cell 480x520); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kayn_fx_form_d.png`：暗裔杀手形态的光环（跟着人，循环），6 帧

变成暗裔杀手以后一直跟着他：脚下一圈暗红色的光，身边几道细的红色闪电时有时无，几颗橙色的火星往上飘（参考 P_slayer_glow、Slayer_lightning、Slayer_orange_glow、P_aura）。中间是人，不要画人。脚在格子底部往上 6 格的中间。要看得出来但别盖住人：光在脚下和身体两边。6 帧无缝循环。约 36 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood-and-gold ramp (#FFFFFF, #FFEF9A, #F7D48E, #ECA173, #F74508, #C03233, #9C2429, #571E21).
Effect: a LOOPING DEMONIC AURA round a figure (do NOT draw the figure; leave its place empty), 6 frames, a seamless loop: a ring of dim blood-red light on the ground round the feet (an ellipse twice as wide as tall), red-orange embers rising beside the body, and a thin jagged red lightning crackle flickering at one side of the figure in frames 2 and 5 (left in 2, right in 5); the ring pulses a little.
Layout: one horizontal row of 6 equal 9:11 cells, image size 2160x440 (each cell 360x440); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kayn_fx_form_s.png`：影流刺客形态的光环（跟着人，循环），6 帧

变成影流刺客以后一直跟着他：脚下一圈黑紫色的影子，身边几缕黑烟往上飘，烟里几点青色的光（参考 Assassin_fire、Assassin_Hair_trail、darkclouds_mult、Buff_body_glow）。中间是人，不要画人。脚在格子底部往上 6 格的中间。6 帧无缝循环。约 36 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a shadow-blue ramp (#FFFFFF, #D6F7FF, #8EE3F7, #3FE9FC, #73ABEC, #3C2EBA, #31209C, #2E1E57) and a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030).
Effect: a LOOPING SHADOW AURA round a figure (do NOT draw the figure; leave its place empty), 6 frames, a seamless loop: a pool of dark indigo shadow on the ground round the feet (an ellipse twice as wide as tall) with a blue rim, 3 wisps of dark smoke rising beside the body and curling away, a few cyan glints drifting up in the smoke; each wisp rises a little each frame.
Layout: one horizontal row of 6 equal 9:11 cells, image size 2160x440 (each cell 360x440); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kayn_fx_q_dash.png`：Q 冲刺的残影（施法者身上，不跟随），4 帧

Q 往前（右）冲的时候身后拖一道黑紫色的影子，影子边上一点深红色（参考 e_shadow_trail、Kayne_Base_e_trail、Primary_Smoke）。人往右冲，残影在左边。约 36 格宽、16 格高，残影贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030) and his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a DASH TRAIL behind a figure rushing to the RIGHT (do NOT draw the figure; it stands at the right end), 4 frames: 1 a streak of dark violet shadow with a crimson edge stretches 28 squares to the LEFT behind the figure, low to the ground; 2 the trail longer, its tail breaking into wisps; 3 the trail breaking into violet wisps; 4 fading wisps.
Layout: one horizontal row of 4 equal 9:4 cells, image size 2304x256 (each cell 576x256); the figure's place at the RIGHT end, the feet 2 squares above the bottom, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kayn_fx_q_spin.png`：Q 旋转的一圈刀光（施法者脚下，不跟随，本体），5 帧

Q 冲到位以后原地转一圈：镰刀在身边扫出一整圈刀光，从斜上方看是扁椭圆（宽是高的 2 倍），外缘一道青蓝色的刃光、里面深红色和暗紫色的刀痕（参考 Q2_edge_color、Kayne_Base_q2_mesh_spin、Q_weapon_edge、Q_spikes_tex）。中间是人，不要画人。脚在格子底部往上 6 格的中间。约 52 格宽、30 格高（地上的圈 48 × 24，加上刀光的高度）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A) and a cyan edge ramp (#D6EFFF, #3FE9FC, #1BAEC3, #2165BD).
Effect: a SPINNING SCYTHE SWEEP round a figure (do NOT draw the figure; leave its place empty), 5 frames: 1 a bright arc starts at the right of the figure at hip height; 2 the arc sweeps round behind and in front of the figure - a full flattened ring (an ellipse twice as wide as tall, 48 squares wide), its OUTER rim a sharp cyan-white blade light, the inside crimson and dark violet slash streaks; 3 the whole ring at full brightness, crimson sparks thrown out; 4 the ring fades from the inside, the rim breaking into streaks; 5 fading sparks on the rim.
Layout: one horizontal row of 5 equal 13:8 cells, image size 2600x320 (each cell 520x320); the figure's feet 6 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kayn_fx_q_hit.png`：Q 打中（目标身上），4 帧

Q 的冲刺或旋转打中敌人：一道横着的深红刀痕，带青色的刃光和火星（参考 Q_weapon_edge、hit_radial、z_direction_hit）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A) and a cyan edge ramp (#D6EFFF, #3FE9FC, #1BAEC3, #2165BD).
Effect: a SWEEPING HIT, 4 frames: 1 a white flash; 2 a horizontal crimson slash 14 squares long with a white core and a thin cyan edge on top, 4 red sparks; 3 the slash breaking into streaks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kayn_fx_q_d_hit.png`：暗裔杀手 Q 打中：按最大生命值的血爆（目标身上），5 帧

暗裔杀手的 Q 额外按目标最大生命值造成伤害：目标身上炸开一团血红色和橙色的光，几根红色的尖刺往外戳（参考 Slayer_W_spiketex、Sion_Base_Q_Hit3_spikes、Slayer_orange_glow）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood-and-gold ramp (#FFFFFF, #FFEF9A, #F7D48E, #ECA173, #F74508, #C03233, #9C2429, #571E21).
Effect: a BLOOD BURST, 5 frames: 1 a pale gold flash; 2 a burst of blood-red and orange light with a white core, 6 sharp red spikes stabbing outward; 3 the burst at full size (18 squares), the spikes longest, orange sparks; 4 the spikes break, the light darkens to crimson; 5 fading embers.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kayn_fx_ghost.png`：掠影步：穿墙疾行（跟着人，循环），4 帧

Q 转完以后几秒里移速变快、能穿墙（英雄联盟的 E 并进了 Q）：脚下贴地一团黑紫色的影子，往后（左）拖着几缕烟（参考 Kayne_Base_e_glow、e_shadow_trail、Kayne_Base_e_trail）。中间是人，不要画人。4 帧无缝循环。约 28 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030) and his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a LOOPING SHADOW STEP at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat pool of dark violet shadow on the ground round the feet (an ellipse twice as wide as tall) with a faint crimson rim, 3 wisps of smoke trailing back to the LEFT from it and drifting further left each frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the feet at the middle of every cell, 2 squares above the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kayn_fx_w_wind.png`：W 蓄力：拉亚斯特的眼睛亮起、暗红色的力量聚到镰刀上（施法者身上，本体），6 帧

W 出手前 0.55 秒的蓄力（这段时间敌人看得到、能躲）：镰刀上拉亚斯特的红眼亮起来，暗红色和暗紫色的光一圈圈往红眼上收，越来越亮（参考 W_weapon_scroll、z_glow、Z_spark、W_Blast_energy）。只画这团光，**红眼在格子正中间**（导入时 Claude 把格子中心对到镰刀的红眼上）。约 24 格见方。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a CHARGING GLOW gathering into one point at the CENTER of the cell, 6 frames: 1 a small red eye-glint at the center; 2 dark violet and crimson wisps spiral in toward the glint from all round (from 10 squares out); 3 the glint grows into a red star with a white core, more wisps spiralling in; 4 the wisps closer, the star brighter; 5 the star at its brightest, 4 red sparks; 6 the star flares and the wisps vanish.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the glint at the center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `kayn_fx_w_line.png`：W 一长条地面斩击（朝右，游戏转到出招方向，本体），5 帧

W 打中的范围：从凯隐脚下往前（右）一条很长很窄的斩击贴着地面劈出去，深红色的刀痕、白芯，两边翻起暗紫色的影子和碎石（参考 W_cas_trail、W_ground_marks、Primary_w_blast、W_Blast_dust、W_rock_debris、W_indicator_color_pal）。上下对称。约 64 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a LONG GROUND SLASH pointing to the RIGHT, 5 frames, SYMMETRIC above and below the middle line: 1 a thin bright line runs from the left end to the right end; 2 the line bursts into a sharp crimson slash 5 squares thick in the middle with a white core, tapering at both ends, dark violet shadow flaring up along both sides; 3 the slash at full brightness, small dark rock chips thrown up along it; 4 the slash darkens to crimson cracks, violet smoke; 5 fading cracks and smoke.
Layout: one horizontal row of 5 equal cells, each 768x144 (image 3840x144); the slash on the middle line of every cell, its LEFT end at the cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `kayn_fx_w_line_d.png`：暗裔杀手 W：一长条从地里刺出来的血红尖刺（朝右），5 帧

暗裔杀手的 W 还会把人击飞：同样一长条，但是从地里一路刺出一排血红色和橙色的尖刺，尖刺之间是红色的裂纹（参考 Slayer_W_ground_marks、Slayer_W_spiketex、Slayer_W_ground_marks_glow、W_Slayer_meshtrail）。上下对称（尖刺往上下两边张开）。约 64 格长、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood-and-gold ramp (#FFFFFF, #FFEF9A, #F7D48E, #ECA173, #F74508, #C03233, #9C2429, #571E21).
Effect: a ROW OF BLOOD SPIKES bursting out of the ground along a line pointing to the RIGHT, 5 frames, SYMMETRIC above and below the middle line: 1 a red crack runs from the left end to the right end; 2 sharp blood-red spikes with orange and pale gold tips burst out along the whole crack, pointing up and down from it (each 4-6 squares), the crack glowing; 3 the spikes at full size, orange sparks; 4 the spikes crumble into red shards, the crack dims; 5 fading red cracks.
Layout: one horizontal row of 5 equal cells, each 768x192 (image 3840x192); the line on the middle of every cell, its LEFT end at the cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `kayn_fx_w_line_s.png`：影流刺客 W：更长的一条青蓝色暗影斩击（朝右），5 帧

影流刺客的 W 打得更远：更长的一条斩击，青白色的刃光、蓝色的刀痕，两边翻起黑紫色的烟（参考 Assassin_W_overlay_tex、Assassin_W_hit_groundflash、Assassin_Q1_color、W_indicator_color_pal 上面一行）。上下对称。约 82 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a shadow-blue ramp (#FFFFFF, #D6F7FF, #8EE3F7, #3FE9FC, #73ABEC, #3C2EBA, #31209C, #2E1E57) and a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030).
Effect: a LONG SHADOW SLASH pointing to the RIGHT, 5 frames, SYMMETRIC above and below the middle line: 1 a thin pale cyan line runs from the left end to the right end; 2 the line bursts into a sharp slash 5 squares thick in the middle, a white and pale cyan core with blue edges, tapering at both ends, dark indigo smoke flaring up along both sides; 3 the slash at full brightness, cyan glints along it; 4 the slash fades into blue streaks and smoke; 5 fading smoke.
Layout: one horizontal row of 5 equal cells, each 984x144 (image 4920x144); the slash on the middle line of every cell, its LEFT end at the cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `kayn_fx_w_hit.png`：W 打中（目标身上），4 帧

W 的斩击打中：一道竖着往上挑的深红刀痕，带碎石（参考 Primary_W_tar、W_rock_debris）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: an UPWARD SLASH HIT, 4 frames: 1 a white flash at the bottom middle; 2 a crimson slash 14 squares tall sweeping up with a white core, 3 small dark rock chips flying up; 3 the slash thinner, the chips higher; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `kayn_fx_w_slow.png`：W 减速（目标脚下，循环），4 帧

W 的减速：被打中的敌人脚下一圈暗紫色的影子缠着，带一点深红色的光，慢慢转（参考 darkclouds_mult、R_shadow_whisps）。中间是人，不要画人。左右对称，4 帧无缝循环。约 20 格宽、8 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030) and his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a SHADOW SNARE at a figure's feet (do NOT draw the figure; symmetric left and right), 4 frames, a seamless loop: a ring of dark violet shadow wisps lying on the ground round the feet (a flattened ellipse twice as wide as tall), a dim crimson glow along it, the wisps shifting a quarter of the way round each frame.
Layout: one horizontal row of 4 equal 5:2 cells, image size 2560x256 (each cell 640x256); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `kayn_fx_r_dive.png`：R 往敌人身上扑过去的残影（施法者脚下，不跟随），4 帧

R「裂舍影」往目标扑过去：身后拖着一道黑紫色的影子，影子里几道深红色的光（参考 Primary_R_cas_shadow、Primary_R_cas_poof、R_shadow_whisps）。人往右扑，残影在左边。约 36 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030) and his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a DIVE TRAIL behind a figure leaping to the RIGHT (do NOT draw the figure; it is at the right end), 4 frames: 1 a puff of dark violet smoke where it took off (at the left), a streak of shadow with crimson glints stretching to the right end; 2 the streak at full length, rising a little to the right; 3 the streak breaking into wisps; 4 fading wisps.
Layout: one horizontal row of 4 equal 9:5 cells, image size 2304x320 (each cell 576x320); the figure's place at the RIGHT end, the feet 2 squares above the bottom, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `kayn_fx_r_enter.png`：R 钻进敌人身体（目标身上），5 帧

凯隐钻进敌人身体：目标身上一团黑紫色的影子往里收，一道深红色的闪光（参考 Primary_R_cas_Tex_alpha、Primary_R_bodyglow、primary_R_flash）。约 24 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030) and his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a SHADOW SWALLOW, 5 frames: 1 a ring of dark violet smoke 22 squares across round the middle of the cell; 2 the smoke swirls inward, crimson streaks spiralling in with it; 3 the swirl small and dense at the center, a crimson flash; 4 a dark core with a red glint; 5 a last wisp.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `kayn_fx_r_mark.png`：R 被凯隐附身的目标身上的标记（目标头上，循环，本体），4 帧

凯隐在敌人身体里的 2 秒：目标头上一个小的暗紫色漩涡，中间一道深红色的镰刀形光在转（参考 primary_r_mark_target、slauer_r_mark_target、R_mark_color）。4 帧无缝循环。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a small LOOPING MARK, 4 frames, a seamless loop: a dark violet swirl 14 squares across with a crimson crescent (like a scythe's blade) of light turning in it, a quarter turn each frame, a white glint on the crescent's tip.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `kayn_fx_r_exit.png`：R 破体而出：本体的影子爆裂（目标身上），6 帧

凯隐从敌人身体里撕出来：一团黑紫色的影子炸开，三道深红色的大刀痕交叉划过，碎影四散（参考 Primary_R_tar_exit_hit、Primary_R_tar_exit_smoke、Primary_R_tar_slash、Primary_R_tar_scythe_black）。约 36 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030) and his shadow-and-crimson ramp (#FFFFFF, #FFC2CC, #FF4058, #D61C39, #8E1834, #46205E, #22163A).
Effect: a SHADOW BURST with slashes, 6 frames: 1 a crimson flash at the center; 2 dark violet smoke bursts out in all directions, three long crimson slash marks with white cores cross the center (one horizontal, two diagonal, each 30 squares long); 3 the slashes at full brightness, smoke shards flying out; 4 the slashes thin, the smoke wide; 5 smoke wisps and red sparks; 6 fading wisps.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `kayn_fx_r_exit_d.png`：暗裔杀手 R 破体而出：血肉爆裂（目标身上），6 帧

暗裔杀手的 R 按目标最大生命值伤害并回血：一团血红色和橙色的光炸开，红色的尖刺往外戳，几道深红色的大刀痕，红色的血滴四溅（参考 R_Aatrox_R_explosion_centerFlare1、Slayer_W_spiketex、Slayer_orange_glow、Primary_R_tar_slash）。约 36 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood-and-gold ramp (#FFFFFF, #FFEF9A, #F7D48E, #ECA173, #F74508, #C03233, #9C2429, #571E21).
Effect: a BLOOD-FIRE BURST with slashes, 6 frames: 1 a pale gold flash at the center; 2 a burst of blood-red and orange light with a white core, 8 sharp red spikes stabbing outward, two long crimson slash marks crossing the center; 3 the burst at full size (34 squares), orange sparks and red droplets flying out; 4 the spikes break, the light darkens to crimson; 5 embers and droplets; 6 fading embers.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `kayn_fx_r_exit_s.png`：影流刺客 R 破体而出：暗影刀光（目标身上），6 帧

影流刺客的 R：一团黑色和靛蓝色的烟炸开，三道青白色的细刀光交叉划过，青色的光点四散（参考 Assassin_thinslash、Assassin_Transform_thinclouds、Primary_shadow_smoke_shard）。约 36 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, smoke or sparks, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a shadow-blue ramp (#FFFFFF, #D6F7FF, #8EE3F7, #3FE9FC, #73ABEC, #3C2EBA, #31209C, #2E1E57) and a smoke ramp (#9A8EC8, #6A5C9E, #463A74, #2C2250, #181030).
Effect: a SHADOW BURST with thin blade lights, 6 frames: 1 a pale cyan flash at the center; 2 dark indigo smoke bursts out in all directions, three long thin slashes of white and pale cyan light with blue edges cross the center (each 30 squares long); 3 the slashes at full brightness, cyan glints flying out; 4 the slashes fade, the smoke wide; 5 smoke wisps and glints; 6 fading wisps.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kayn_fx_hit` | view_effects `league_kayn_hit`（跟随，画在人物上面）；导入时换色出 `hit_d`、`hit_s` | 14 |
| `kayn_fx_sa_hit` | view_effects `league_kayn_sa_hit`（跟随，画在人物上面，在普攻命中上面一层） | 18 |
| `kayn_fx_tf_d` | view_effects `league_kayn_tf_d`（BIG，施法者脚下，不跟随，画在人物上面） | 48 × 52 |
| `kayn_fx_tf_s` | view_effects `league_kayn_tf_s`（BIG，施法者脚下，不跟随，画在人物上面） | 48 × 52 |
| `kayn_fx_form_d` | view_buffs `league_kayn_form_d`（循环，画在人物下面，朝左时镜像） | 36 × 44 |
| `kayn_fx_form_s` | view_buffs `league_kayn_form_s`（循环，画在人物下面，朝左时镜像） | 36 × 44 |
| `kayn_fx_q_dash` | view_effects `league_kayn_q_dash`（施法者脚下，不跟随，画在人物下面，朝左时镜像） | 36 × 16 |
| `kayn_fx_q_spin` | view_effects `league_kayn_q_spin`（BIG，施法者脚下，不跟随）；导入时换色出 `q_spin_d`、`q_spin_s` | 52 × 30 |
| `kayn_fx_q_hit` | view_effects `league_kayn_q_hit`（跟随，画在人物上面） | 16 |
| `kayn_fx_q_d_hit` | view_effects `league_kayn_q_d_hit`（跟随，画在人物上面） | 20 |
| `kayn_fx_ghost` | view_buffs `league_kayn_ghost`（循环，画在人物下面，朝左时镜像） | 28 × 14 |
| `kayn_fx_w_wind` | view_effects `league_kayn_w_wind`（施法者身上，跟随，朝左时镜像；导入时把格子中心放到 W 第 1 帧镰刀上拉亚斯特红眼的位置）；导入时换色出 `w_wind_d`、`w_wind_s` | 24 × 24 |
| `kayn_fx_w_line` | view_projectiles `league_kayn_w_line`（BIG，画在地面上，朝右画，上下对称） | 64 × 12 |
| `kayn_fx_w_line_d` | view_projectiles `league_kayn_w_line_d`（BIG，画在地面上，朝右画，上下对称） | 64 × 16 |
| `kayn_fx_w_line_s` | view_projectiles `league_kayn_w_line_s`（BIG，画在地面上，朝右画，上下对称） | 82 × 12 |
| `kayn_fx_w_hit` | view_effects `league_kayn_w_hit`（跟随，画在人物上面） | 16 |
| `kayn_fx_w_slow` | view_buffs `league_kayn_w_slow`（循环，画在脚下） | 20 × 8 |
| `kayn_fx_r_dive` | view_effects `league_kayn_r_dive`（施法者脚下，不跟随，画在人物下面，朝左时镜像） | 36 × 20 |
| `kayn_fx_r_enter` | view_effects `league_kayn_r_enter`（跟随，画在人物上面） | 24 |
| `kayn_fx_r_mark` | view_buffs `league_kayn_r_mark`（循环，画在人物上面）；导入时换色出 `r_mark_d`、`r_mark_s` | 16 × 16 |
| `kayn_fx_r_exit` | view_effects `league_kayn_r_exit`（BIG，跟随，画在人物上面） | 36 |
| `kayn_fx_r_exit_d` | view_effects `league_kayn_r_exit_d`（BIG，跟随，画在人物上面） | 36 |
| `kayn_fx_r_exit_s` | view_effects `league_kayn_r_exit_s`（BIG，跟随，画在人物上面） | 36 |

- 换色：`hit_d` ← `hit`（暗裔色带），`hit_s` ← `hit`（影流色带），`q_spin_d` ← `q_spin`（暗裔色带），`q_spin_s` ← `q_spin`（影流色带），`w_wind_d` ← `w_wind`（暗裔色带），`w_wind_s` ← `w_wind`（影流色带），`r_mark_d` ← `r_mark`（暗裔色带），`r_mark_s` ← `r_mark`（影流色带）：每个像素按亮度找本体色带里对应的那一档，换成形态色带同一档（两条色带档数不同时按位置比例）。
- 施法者身上的画面（`q_dash`、`q_spin`、`r_dive`、`tf_d`、`tf_s`）画在站位点上：按 `design/kayn_shots.png` 的十字（脚下）把格子的起点挪过去；`w_wind` 的格子中心对到 W 第 1 帧镰刀上拉亚斯特的红眼（导入动作条后量）；`form_d`、`form_s`、`ghost` 是跟着人的循环 buff 画面。
- `w_line`、`w_line_d`、`w_line_s` 是 W 的范围投射物画面（不循环，播一次，出生那一 tick 画面朝上：第一帧前加一个空帧，`import_lucian.py` 的 `RAY_SKIP`）。
- 清掉 Codex 给光和烟描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
