# 蛮族之王 泰达米尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 11 张特效图。** 造型和动作已定（`design/tryndamere_design.png`，8 倍，40 行）。
> - 大小对照 `design/tryndamere_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。蛮王 57×40 格（含拖在身后的大剑，人约 40 格宽）。每条写的大小都是游戏像素（格）。
> - `design/tryndamere_shots.png`：E、W、Q、R 和待机的定稿动作（4 倍），青色十字是特效的起点（脚下、腰、胸口或嘴），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里蛮王自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟：**刀光、怒吼、嗜血是血红色带白芯；大招的不死怒火是橙红色的火焰（白黄色的芯）和黑色的灰烬；减益标记是暗红色**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **绕着人的刀光、围着人的火和光只画边，中间留空**，不然会把人整个挡住。
> - 特效照下面第 1–11 条和「所有特效图的规则」画，每张一个 PNG，文件名 `tryndamere_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`tryndamere_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「战斗狂怒」 | 大剑砍，会暴击；普攻、E 和击杀叠怒气（5 层，每层加暴击率），叠满时身上烧着红光 | `tryndamere_fx_a_hit` · `tryndamere_fx_f_full` |
| 技能 1 = E「旋风斩」 | 旋转着冲向目标并穿过去，砍到路上所有敌人，每砍一个叠一层怒气 | `tryndamere_fx_e_spin` · `tryndamere_fx_e_hit` |
| 技能 2 = W「蔑视」 | 怒吼，附近敌方英雄攻击力降低 4 秒，背对他（远一点）的还被减速 2 秒 | `tryndamere_fx_w_shout` · `tryndamere_fx_w_hit` · `tryndamere_fx_w_weak` · `tryndamere_fx_w_slow` |
| 大招 = R「不灭狂暴」 + Q「嗜血」 | 危险时触发：5 秒内血量不会低于 1，怒气直接叠满；结束时喝 Q 按怒气回血 | `tryndamere_fx_r_cast` · `tryndamere_fx_r_rage` · `tryndamere_fx_q_heal` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刀光、光、火焰、烟、火花没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的东西（灰烬片、断剑标记）有 1 格深色描边（`#12040A`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 血红（刀光、命中、怒吼、嗜血、怒气）：`#FFFFFF`、`#FFE0C8`、`#FF9A5A`、`#FF3A1E`、`#D0141E`、`#8A0A1A`；
  - 余烬橙（大招的火焰、白热的芯）：`#FFFFFF`、`#FFF2A8`、`#FFC83A`、`#FF8A1E`、`#E0501A`、`#9A2A10`；
  - 暗红（减益标记、烟尘、灰烬）：`#C02040`、`#8A1030`、`#5A0A24`、`#3A0618`、`#1E040C`；
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 画在他身上或脚下的画面（`e_spin`、`w_shout`、`q_heal`、`r_cast`、`r_rage`、`f_full`）按每条写的站位画，**格子里留出空的人形位置，不要画人**。挂在人身上或脚下的循环画面（`f_full`、`r_rage`、`w_weak`、`w_slow`）左右对称或不分左右，因为人朝左朝右都用同一张。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（11 张）

11 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：E 的刀光半径 15000、W 的怒吼半径 40000）。

### 1. `tryndamere_fx_a_hit.png`：普攻打中（目标身上），4 帧

大剑砍中：一道从右上往左下的红白色斩击弧光，砍中的地方一下白色闪光，几点红色火星飞出去（参考 E_SlashUlt、common_SlashWave、E_Sparks）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A) and an ember ramp (#FFFFFF, #FFF2A8, #FFC83A, #FF8A1E, #E0501A, #9A2A10).
Effect: a GREATSWORD HIT, 4 frames: 1 a crescent slash arc of white-red light 14 squares long cutting from the upper right to the lower left through the center; 2 a white flash at the center 8 squares across, the arc thinning, 5 red-orange sparks flying out; 3 the arc gone, sparks further out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `tryndamere_fx_f_full.png`：被动 怒气满了：脚下和身上的红光（循环），4 帧

怒气叠满（暴击率最高）时：蛮王身后和脚下烧着一层红色的怒气光，几缕红光往上飘（参考 Q_bigglow02、common_color-aura-red、Aura_Self）。画在人物下面，所以只有从人身边露出来的部分看得见：脚下一圈扁的红光，身体两边往上飘的红色光丝，到头顶为止。中间是人，不要画人。左右对称，4 帧无缝循环。约 26 格宽、40 格高，脚在格子底部往上 4 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A) and an ember ramp (#FFFFFF, #FFF2A8, #FFC83A, #FF8A1E, #E0501A, #9A2A10).
Effect: a FURY AURA round a standing figure (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a flattened ellipse of red light on the ground round the feet (twice as wide as tall, 22 squares wide), 6 thin red-orange light wisps rising along both sides of the figure's place up to head height (36 squares), small ember sparks; the wisps climb a few squares each frame and flicker.
Layout: one horizontal row of 4 equal 13:20 cells, image size 832x320 (each cell 208x320); the figure's feet 4 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `tryndamere_fx_e_spin.png`：E 旋风斩：绕着身体转的刀光（施法者身上，跟着冲过去），6 帧

E「旋风斩」：蛮王一边旋转一边往前冲，大剑在身边转出一圈红白色的刀光（从斜上方看是扁的椭圆，宽是高的 2 倍左右），刀光带一点火焰的橙色尾巴（参考 E_SlashUlt、E_FlameHead、E_Outerring、E_Erode_01、E_Mis_Tail_V2）。中间是人，不要画人：刀光绕着人的位置转，前面一段从人身前经过，后面一段在人身后。6 帧转一圈多：1 刀光出现，2–5 转（亮的刀头每帧往前转 90°，后面拖着变暗的弧），6 散开。约 40 格宽、30 格高，腰在格子正中。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A) and an ember ramp (#FFFFFF, #FFF2A8, #FFC83A, #FF8A1E, #E0501A, #9A2A10).
Effect: a SPINNING SWORD SLASH round a figure (do NOT draw the figure; leave its place empty), seen from above at an angle, 6 frames: 1 a short bright white-red blade arc appears at the right of the figure's place; 2-5 the arc sweeps round the figure's place along a flattened ellipse 38 squares wide and 18 tall (its bright head moving a quarter turn each frame, a fading red and orange trail behind it covering half the ellipse; small flame licks on the trail); 6 the trail breaks into red sparks.
Layout: one horizontal row of 6 equal 4:3 cells, image size 1920x480 (each cell 320x240 - keep the 4:3 shape); the figure's waist (the ellipse's center) at the center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `tryndamere_fx_e_hit.png`：E 砍中（目标身上），4 帧

旋风斩从身边扫过：一道横着的红白色刀光划过，一下闪光和红色火星（参考 E_SlashUlt、E_Sparks、common_SlashWave）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A) and an ember ramp (#FFFFFF, #FFF2A8, #FFC83A, #FF8A1E, #E0501A, #9A2A10).
Effect: a SWEEPING SLASH HIT, 4 frames: 1 a horizontal white-red slash streak 16 squares long through the center; 2 a white flash at the center 8 squares across, the streak thinning, 4 orange sparks; 3 sparks flying out; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `tryndamere_fx_w_shout.png`：W 蔑视怒吼：从他嘴里吼出去的冲击波（施法者身上），6 帧

W「蔑视」：蛮王仰头怒吼，嘴前喷出一下红色的吼声，地面上一圈红色的冲击波往外推到很远（从斜上方看的扁椭圆，宽是高的 2 倍，半径约 40 格，所以外圈约 80 格宽），几道红色的声波弧从头的位置往两边散开（参考 W_Dissolve_Cloudy_01、Orianna distort-wave、R_speed_blur、common_SRU_Tower_Explosion_Glow）。中间是人，不要画人。6 帧：1 嘴前红光，2–4 冲击波从脚下往外扩、声波弧往外，5 冲击波到边变细，6 散去。约 84 格宽、48 格高，脚在格子底部往上 14 格的中间，嘴在脚上方 28 格、往右 15 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A) and a dark crimson ramp (#C02040, #8A1030, #5A0A24, #3A0618, #1E040C).
Effect: a BATTLE ROAR from a figure (do NOT draw the figure; leave its place empty), seen from above at an angle, 6 frames: 1 a burst of red light at the mouth's point (28 squares above the feet, 15 squares right of them); 2 three curved red sound-wave arcs spreading left and right from the head, a red shockwave ring starting on the ground round the feet; 3-4 the ring expanding over a flattened ellipse twice as wide as tall up to 80 squares wide, dark crimson dust kicked up along it, the arcs further out; 5 the ring thin at its edge; 6 fading dust.
Layout: one horizontal row of 6 equal 7:4 cells, image size 3360x480 (each cell 560x320 - keep the 7:4 shape; 48 squares tall); the figure's feet 14 squares (about 93 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `tryndamere_fx_w_hit.png`：W 吼中（敌人身上），4 帧

被吼中的敌人：头那里一下暗红色的冲击，几道红色的声波弧打在他身上（参考 W_Dissolve_Cloudy_01、R_speed_blur）。中间是人，不要画人。约 16 格宽、20 格高，居中画（中心在人的胸口）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A) and a dark crimson ramp (#C02040, #8A1030, #5A0A24, #3A0618, #1E040C).
Effect: a ROAR STRIKING a figure (do NOT draw the figure; leave its place empty), 4 frames: 1 three curved red sound-wave arcs coming in from the left; 2 the arcs hit the center with a dark crimson burst 12 squares across; 3 red dust puffs, the burst fading; 4 fading wisps.
Layout: one horizontal row of 4 equal 4:5 cells, image size 1024x320 (each cell 256x320); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `tryndamere_fx_w_weak.png`：W 攻击力降低：头上的标记（敌人身上，循环 4 秒），4 帧

被吼了的敌人攻击力降低：头顶一个暗红色的「断剑」标记（一把小剑断成两截，有描边），下面一个往下的红色箭头，暗红光一明一暗（参考 common_color-aura-red）。4 帧无缝循环。约 12 格见方，标记的底边在格子底部（导入时放到头顶）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark crimson ramp (#C02040, #8A1030, #5A0A24, #3A0618, #1E040C) and a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A).
Effect: an ATTACK-DOWN MARK over a head, 4 frames, a seamless loop: a small broken sword icon 8 squares tall (a blade snapped in two, the halves a square apart, a 1-square dark outline, dark crimson with a red glint) above a small red arrow pointing DOWN; a dim crimson glow round it pulsing brighter and dimmer; the icon bobs a square.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the icon centered, its bottom near the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `tryndamere_fx_w_slow.png`：W 减速：脚下的标记（敌人身上，循环 2 秒），4 帧

背对着他跑的敌人被减速：脚下一圈暗红色的光，几道往下的红色光痕（像被吓得腿软）（参考 common_color-aura-red、Aura_Self）。中间是人，不要画人。左右对称，4 帧无缝循环。约 18 格宽、8 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark crimson ramp (#C02040, #8A1030, #5A0A24, #3A0618, #1E040C) and a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A).
Effect: a SLOW MARK at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a flattened ellipse of dark crimson light on the ground round the feet (twice as wide as tall, 16 squares wide), 4 short red streaks sliding DOWN into it a square each frame, 2 small dust puffs.
Layout: one horizontal row of 4 equal 9:4 cells, image size 2304x256 (each cell 576x256); the ellipse at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `tryndamere_fx_q_heal.png`：Q 嗜血：吸血回血的红光（施法者身上），5 帧

Q「嗜血」（R 结束时和危险时喝）：四周的红色光点和血色光丝往他身上吸过去，胸口一下红白色的光爆开，几点红色的「+」形火花往上升（参考 Temp_Q_Heal_01_Spark_RGBA、Q_bigglow02、Q_WeaponTrail、Flicker_04）。中间是人，不要画人。5 帧：1–2 光点往里吸，3 胸口爆光，4 火花上升，5 淡去。约 30 格宽、44 格高，胸口在格子正中。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A) and an ember ramp (#FFFFFF, #FFF2A8, #FFC83A, #FF8A1E, #E0501A, #9A2A10).
Effect: a BLOOD HEAL on a figure (do NOT draw the figure; leave its place empty), 5 frames: 1 ten red light motes and thin blood-red streaks 14 squares out from the center, drawn inward; 2 the motes closer, a red glow at the center; 3 a red-white flash at the center 14 squares across; 4 six small red plus-shaped sparks rising from it 8-16 squares above the center; 5 the sparks fading near the top of the cell.
Layout: one horizontal row of 5 equal 15:22 cells, image size 1200x352 (each cell 240x352); the figure's chest at the center of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `tryndamere_fx_r_cast.png`：R 不死怒火爆发（施法者身上），6 帧

R「不灭狂暴」触发：蛮王身上猛地炸开一团橙红色的怒火，地上一圈耀斑一样的火环往外冲，火焰从脚下往上窜过头顶，几片灰烬飞起来（参考 R_Flare、R_dome_flames、R_FireStrands_4x1_Darker、R_FlameErosion、R_Ash01、common_flames03）。中间是人，不要画人。6 帧：1 身上白橙色的闪光，2 火环往外冲、火焰往上窜，3 火焰最高（过头顶），4–5 火焰往下落、灰烬飘，6 剩几点火星。约 48 格宽、56 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember ramp (#FFFFFF, #FFF2A8, #FFC83A, #FF8A1E, #E0501A, #9A2A10), a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A) and a dark crimson ramp (#C02040, #8A1030, #5A0A24, #3A0618, #1E040C).
Effect: an UNDYING RAGE ERUPTION round a figure (do NOT draw the figure; leave its place empty), 6 frames: 1 a white-orange flash at the figure's chest (16 squares above the feet); 2 a jagged flare ring of orange fire bursting outward along the ground (a flattened ellipse twice as wide as tall), tongues of red and orange flame shooting up round the figure's place; 3 the flames at their tallest, 50 squares above the feet, the ring 44 squares wide; 4 the flames sinking, dark ash flakes (outlined) drifting up; 5 low flames and ash; 6 a few embers.
Layout: one horizontal row of 6 equal 6:7 cells, image size 2304x448 (each cell 384x448); the figure's feet 4 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `tryndamere_fx_r_rage.png`：R 不死期间：身上烧着的怒火（循环 5 秒），4 帧

不死的 5 秒里：蛮王全身被橙红色的火焰包着往上烧，脚下一圈火（参考 R_dome_flames、R_FireStrands_4x1_Darker、R_buf_01_GroundFlame、R_Small_Mote、common_flames03）。画在人物下面，所以火从人身边和头顶露出来：两边和头顶往上蹿的火舌，脚下一圈扁的火环。中间是人，不要画人。左右对称，4 帧无缝循环（火舌每帧往上跳几格、换形状）。约 34 格宽、50 格高，脚在格子底部往上 4 格的中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, slashes, flames, smoke or sparks (only the solid ash flakes and the broken-sword icon get a 1-square dark outline #12040A), BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an ember ramp (#FFFFFF, #FFF2A8, #FFC83A, #FF8A1E, #E0501A, #9A2A10) and a blood-red ramp (#FFFFFF, #FFE0C8, #FF9A5A, #FF3A1E, #D0141E, #8A0A1A).
Effect: RAGE FLAMES burning round a standing figure (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: a flattened ring of orange fire on the ground round the feet (twice as wide as tall, 30 squares wide), tall tongues of red and orange flame with white-yellow cores rising along both sides of the figure's place and above its head (up to 46 squares above the feet), embers; the flames leap and change shape each frame.
Layout: one horizontal row of 4 equal 17:25 cells, image size 1088x400 (each cell 272x400); the figure's feet 4 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `tryndamere_fx_a_hit` | view_effects `league_tryndamere_a_hit`（跟随，画在人物上面） | 16 |
| `tryndamere_fx_f_full` | view_buffs `league_tryndamere_f_5`（满 5 层怒气时，循环，画在人物下面） | 26 × 40 |
| `tryndamere_fx_e_spin` | view_effects `league_tryndamere_e_spin`（BIG，施法者身上，跟随；格子中心放到他的腰） | 40 × 30 |
| `tryndamere_fx_e_hit` | view_effects `league_tryndamere_e_hit`（跟随，画在人物上面） | 16 |
| `tryndamere_fx_w_shout` | view_effects `league_tryndamere_w_shout`（BIG，施法者身上，跟随；格子里的脚放到他脚下） | 84 × 48 |
| `tryndamere_fx_w_hit` | view_effects `league_tryndamere_w_hit`（跟随，画在人物上面） | 16 × 20 |
| `tryndamere_fx_w_weak` | view_buffs `league_tryndamere_w_weak`（循环，画在人物上面，头顶） | 12 × 12 |
| `tryndamere_fx_w_slow` | view_buffs `league_tryndamere_w_slow`（循环，画在脚下） | 18 × 8 |
| `tryndamere_fx_q_heal` | view_effects `league_tryndamere_q_heal`（施法者身上，不跟随；格子中心放到他的胸口） | 30 × 44 |
| `tryndamere_fx_r_cast` | view_effects `league_tryndamere_r_cast`（BIG，施法者身上，不跟随；格子里的脚放到他脚下） | 48 × 56 |
| `tryndamere_fx_r_rage` | view_buffs `league_tryndamere_r_rage`（BIG，循环，画在人物下面） | 34 × 50 |

- `f_full` 导成 view_buffs `f_5`（只有满怒气的那一层有画面）；`r_rage`、`f_full` 的 z 是 -1（人物下面），`w_weak` 画在头顶。
- 施法者身上的画面按 `design/tryndamere_shots.png` 的十字把起点挪过去；晚于第一 tick 播放的（`r_cast`、`q_heal`）`is_follow` 为 false（红方方向）。`e_spin` 跟着他冲过去（跟随）。
- 清掉 Codex 给光和火描的最深色边（`import_riven.py` 的 `unrim`，灰烬和断剑保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。
