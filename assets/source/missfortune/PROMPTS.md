# 赏金猎人 厄运小姐：给 Codex 的特效提示词

> **这一轮只画 12 张特效图。**
> - 角色不用画：厄运小姐的模型由 Claude 做。头部（深青色三角帽、红发、蓝眼睛、暗红唇，用户选了方案 C1）是逐格画的，每一帧贴在英雄联盟头部关节的位置；身体用英雄联盟原版动画重新上色（`tools/art/restyle_native.py`）。
> - 定稿造型图 `native/missfortune_native.png` 只用来参考配色和人物大小，不要改它。
> - 参考图 `lol_fx_ref.png` 是英雄联盟里厄运小姐自己的特效贴图（爱心、枪口火光、E 的子弹、弹丸），只在本地用，不要提交。她的爱心是**红色**的。
> - 特效照下面第 1–12 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会用 `tools/art/import_missfortune.py --raw` 转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「厄运的眷顾」 | 双枪射出子弹；打新目标的第一枪多造成伤害，目标身上爆一颗红心 | `missfortune_fx_bullet` · `missfortune_fx_hit` · `missfortune_fx_bullet_lt` · `missfortune_fx_lovetap` |
| 技能 1 = Q「一箭双雕」 | 一发子弹打中第一个敌人，再穿到它身后的下一个敌人（第二发带红心）；第一发打死目标时第二发暴击 | `missfortune_fx_q_bullet` · `missfortune_fx_q_hit` · `missfortune_fx_q_bounce` · `missfortune_fx_q_crit` |
| 技能 2 = E「枪林弹雨」+ W「大步流星」 | 在目标区域下 2 秒子弹雨（减速）；随后她加攻速和移速 | `missfortune_fx_e_rain` · `missfortune_fx_strut` |
| 大招 = R「弹幕时间」 | 原地 3 秒，朝前方 40° 的扇形连射 12 波子弹 | `missfortune_fx_r_wave` · `missfortune_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色：
  - 枪火和子弹（金白）：`#FFFFFF`、`#FFF3B0`、`#FFD84A`、`#F2A82A`、`#C8741A`，枪口火光外缘加橙 `#FF9A30`、`#E8501E`；
  - 红心（厄运的眷顾、大步流星）：`#FFFFFF`（高光）、`#FF8A9A`、`#F0384C`、`#C01E32`、`#7A1020`；
  - 暴击的红金爆炸：金白色之外加 `#FF5A3A`、`#D0241E`；
  - 弹雨区域的地面圈：`#FF9A30`、`#E8501E`、`#A8281A`；
  - 烟和尘土：`#8A7A6A`、`#5A4E46`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左飞时整张图转 180°。大招的扇形弹幕（第 12 条）也会被转到施法方向，所以同样朝右、上下对称。
- 命中、红心、火花居中画，不旋转；地面上的圈按游戏的斜俯视角度画成扁的椭圆（宽约是高的 2 倍）。
- 套在人身上的特效：格子中间留出一个空的人形位置（按每条提示词写的比例），不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（12 张）

12 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `missfortune_fx_bullet.png`：普攻子弹，3 帧循环

手枪射出的一颗金色弹丸，拖一小段白黄色的尾迹。约 10 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A).
Effect: a PISTOL BULLET flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC above and below the middle line. A small round golden musket ball with a white-hot core at the right, a short tapering streak of pale yellow light trailing to the left (about three times as long as the ball); the streak flickers a little between the frames.
Layout: one horizontal row of 3 equal cells, each 2 wide to 1 tall, image size 768x128 (each cell 256x128); the ball at the right third of every cell, the streak reaching the left third, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `missfortune_fx_bullet_lt.png`：厄运的眷顾的子弹，3 帧循环

打新目标的那一枪：同样的弹丸，尾迹换成红色，尾巴里带一颗小红心。约 12 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A) and a red heart ramp (#FFFFFF, #FF8A9A, #F0384C, #C01E32, #7A1020).
Effect: a LOVE TAP BULLET flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC above and below the middle line. A small round golden musket ball with a white-hot core at the right, a tapering trail of red and pink light to the left, and inside the trail one tiny red heart (5 pixels wide) that glints white on one frame.
Layout: one horizontal row of 3 equal cells, each 2 wide to 1 tall, image size 768x128 (each cell 256x128); the ball at the right third of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `missfortune_fx_hit.png`：普攻命中，5 帧

子弹打中目标时的一小团火光和火花。约 14 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A) with orange edges (#FF9A30, #E8501E).
Effect: a BULLET IMPACT, 5 frames: 1 a tiny white-hot point at the center; 2 it bursts into a small jagged flash, white core, yellow and orange edges, like a muzzle flash seen head-on; 3 the flash at full size, about 40% of the cell wide, four short sparks flying out diagonally; 4 the flash breaks into sparks; 5 two or three orange specks fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `missfortune_fx_lovetap.png`：厄运的眷顾（跟着目标），6 帧

打中新目标时，目标胸口蹦出一颗红心，放大后炸成红色火花和几颗小红心。约 18 格宽（参考 `lol_fx_ref.png` 里的红心）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a red heart ramp (#FFFFFF, #FF8A9A, #F0384C, #C01E32, #7A1020).
Effect: LOVE TAP, a red heart popping on the target, 6 frames: 1 a small red heart appears at the center with a white glint; 2 it pops bigger with a thin bright outline of light around it (not black); 3 the heart at full size, about 45% of the cell wide, a white highlight on its upper left lobe; 4 the heart bursts into red sparks flying outward and two or three tiny hearts floating up; 5 the sparks and the tiny hearts drift up and fade; 6 the last red specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the heart at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `missfortune_fx_q_bullet.png`：一箭双雕的子弹，3 帧循环

比普攻大的一发子弹，拖着一道长长的白金色光迹（要穿过第一个敌人再打第二个）。约 20 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A).
Effect: a RICOCHET SHOT, a heavy bullet flying fast to the RIGHT, 3 frames, a seamless loop, SYMMETRIC above and below the middle line. A bright golden ball with a white-hot core at the right end, a long straight streak of white and gold light trailing to the left (four times as long as the ball), thin golden speed sparks along the streak that shift a little each frame.
Layout: one horizontal row of 3 equal cells, each 3 wide to 1 tall, image size 768x86 (each cell 256x86); the ball at the right end of every cell, the streak reaching the left edge, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `missfortune_fx_q_hit.png`：一箭双雕第一发命中，6 帧

第一发打中时的金色星芒爆闪（四角星形光芒 + 火花）。约 22 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A).
Effect: a RICOCHET IMPACT, 6 frames: 1 a white-hot point at the center; 2 it flares into a four-pointed golden star, the horizontal points longer; 3 the star at full size, about 55% of the cell wide, a small round flash in its middle and sparks flying out; 4 the star shrinks, a spark shoots off to the right (the bullet going on to the next enemy); 5 sparks drifting; 6 the last golden specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the star at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `missfortune_fx_q_bounce.png`：一箭双雕第二发命中（带红心），6 帧

第二发打中身后的敌人：金色星芒中间蹦出一颗红心（第二发带「厄运的眷顾」）。约 24 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A) and a red heart ramp (#FFFFFF, #FF8A9A, #F0384C, #C01E32, #7A1020).
Effect: a RICOCHET IMPACT WITH A HEART, 6 frames: 1 a white-hot point at the center; 2 a four-pointed golden star flares out and a small red heart appears in its middle; 3 the star and the heart at full size, the star about 60% of the cell wide, the heart about 30%, golden sparks flying out; 4 the star fades, the heart bursts into red sparks; 5 red and gold specks drifting outward; 6 the last specks fading.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the heart at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `missfortune_fx_q_crit.png`：一箭双雕暴击，7 帧

第一发打死目标、第二发暴击时：一团红金色的大爆炸，锯齿状的星芒和四散的火花，比普通命中大得多。约 32 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A) with red (#FF5A3A, #D0241E).
Effect: a CRITICAL HIT BLAST, 7 frames: 1 a white-hot flash point at the center; 2 a big jagged eight-pointed starburst explodes, white core, gold rays, red tips; 3 the starburst at full size, about 70% of the cell wide, a ring of sparks flying out; 4 the rays break apart into sharp shards and sparks, a red glow in the middle; 5 shards and sparks spreading, a little grey smoke (#8A7A6A, #5A4E46); 6 sparks and smoke fading; 7 the last specks.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; the blast at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `missfortune_fx_r_hit.png`：弹幕时间的命中火花，4 帧

大招每一波打到敌人身上时的一小簇火花（一次会有很多个，所以要小、要快）。约 10 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A) with orange (#FF9A30).
Effect: a small BULLET SPARK SPRAY, 4 frames: 1 two tiny white-hot points close together at the center; 2 they burst into a small cluster of yellow sparks, about 35% of the cell wide; 3 the sparks fly apart and turn orange; 4 three orange specks fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the cluster at the center of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `missfortune_fx_strut.png`：大步流星（跟着厄运小姐），7 帧

放完 E 后她进入大步流星：脚下亮起一圈金光，红心和金色亮片从脚边升起，绕身体飘上去。约 36 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a golden ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A) and a red heart ramp (#FFFFFF, #FF8A9A, #F0384C, #C01E32).
Effect: STRUT, a confident gunslinger's speed boost, 7 frames. In the middle of every cell there is an EMPTY person-sized space (a person about 55% of the cell height stands there, feet at 85% of the cell height) - never draw the person. 1 a thin golden ring flashes on the ground around the feet (a flat ellipse twice as wide as tall, about 45% of the cell wide); 2 small red hearts and golden sparkles pop up from the ring; 3-5 three or four red hearts (5 to 7 pixels wide) and golden sparkles spiral up around the body to above the head, the ring fading; 6 the hearts reach head height and start to fade; 7 the last sparkles.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; centered on the empty space, the effect at most 60% of the cell wide, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `missfortune_fx_e_rain.png`：枪林弹雨（地面区域），8 帧，无缝循环

E 在目标区域下 2 秒子弹雨：地上一个发橙红光的扁圆区域，一道道白金色的子弹光迹从右上方斜落下来，落点炸起小火花和尘土（参考 `lol_fx_ref.png` 里的 E 子弹）。区域约 60 格宽、30 格高，画在人物下层。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, seen from a slightly top-down game camera, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A), an orange-red ground glow (#FF9A30, #E8501E, #A8281A) and dust (#8A7A6A, #5A4E46).
Effect: MAKE IT RAIN, a rain of bullets on an area of ground, 8 frames, a seamless loop. On the ground a flat ellipse, twice as wide as tall, about 80% of the cell wide, its center at 65% of the cell height: a thin bright orange rim with a faint dark-red glow inside (no fill in the middle). Every frame, five or six short white-and-gold bullet streaks (tear-drop shaped, bright head at the bottom) fall steeply from the upper right into the ellipse at different places, and where earlier streaks landed small yellow sparks and little puffs of dust burst on the ground; streaks never fall outside the ellipse; frame 8 leads back into frame 1.
Layout: one horizontal row of 8 equal square cells, image size 2048x256; the ellipse at the same place in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `missfortune_fx_r_wave.png`：弹幕时间的一波子弹，4 帧（0.25 秒）

大招每 0.25 秒一波：从她的枪口（格子左边正中）朝右打出一扇形的子弹光迹。**扇形尖端在格子左边正中，向右张开 40°**，一直打到格子右边。游戏会把整张图转到施法方向。约 100 格长、72 格高（格子就是这个比例）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gunfire ramp (#FFFFFF, #FFF3B0, #FFD84A, #F2A82A, #C8741A) with orange (#FF9A30, #E8501E).
Effect: BULLET TIME, one wave of a two-pistol barrage fired to the RIGHT, 4 frames. The fan's point is at the MIDDLE of the LEFT edge of the cell and it opens to the right at 40 degrees in total, reaching the right edge of the cell, so at the right edge it is about 70% of the cell's height; SYMMETRIC above and below the middle line. Inside the fan fly seven thin straight bullet streaks along different angles (the middle one along the middle line), each a white-hot head with a short golden tail. 1 a bright orange-white muzzle flash at the point, the seven streaks just leaving it; 2 the streaks at a third to half of the way; 3 the streak heads near the right edge, the tails stretched long, the muzzle flash gone; 4 the heads at the right edge breaking into small sparks, the tails fading.
Layout: one horizontal row of 4 equal cells, each 4 wide to 3 tall, image size 1024x192 (each cell 256x192); no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

动作图（身体）来自 `tools/art/restyle_native.py`，头部从 `native/missfortune_native.png` 贴上，帧时长写在 `native/missfortune_cells.json`。特效由 `tools/art/import_missfortune.py` 导入（`--raw` 先把生图原稿转成原尺寸条，再按技能范围定大小）。

| 文件 | 帧数 | 游戏里的用途 | 帧时长（毫秒） |
|---|---:|---|---|
| `missfortune_fx_bullet.png` | 3 | 投射物 `league_missfortune_bullet`（普攻） | 3 × 50 循环 |
| `missfortune_fx_bullet_lt.png` | 3 | 投射物 `league_missfortune_bullet_lt`（厄运的眷顾那一枪） | 3 × 50 循环 |
| `missfortune_fx_hit.png` | 5 | 特效 `league_missfortune_hit`（普攻命中，跟随目标） | 5 × 50 |
| `missfortune_fx_lovetap.png` | 6 | 特效 `league_missfortune_lovetap`（跟随目标） | 6 × 60 |
| `missfortune_fx_q_bullet.png` | 3 | 投射物 `league_missfortune_q_bullet`（穿透直线） | 3 × 40 循环 |
| `missfortune_fx_q_hit.png` | 6 | 特效 `league_missfortune_q_hit`（跟随目标） | 6 × 50 |
| `missfortune_fx_q_bounce.png` | 6 | 特效 `league_missfortune_q_bounce`（跟随目标） | 6 × 50 |
| `missfortune_fx_q_crit.png` | 7 | 特效 `league_missfortune_q_crit`（跟随目标） | 7 × 50 |
| `missfortune_fx_r_hit.png` | 4 | 特效 `league_missfortune_r_hit`（跟随目标，每波一次） | 4 × 50 |
| `missfortune_fx_strut.png` | 7 | 特效 `league_missfortune_strut`（跟随厄运小姐） | 7 × 70 |
| `missfortune_fx_e_rain.png` | 8 | 投射物 `league_missfortune_e_rain`（半径 30000 的区域，地面，循环 2 秒） | 8 × 125 循环 |
| `missfortune_fx_r_wave.png` | 4 | 投射物 `league_missfortune_r_wave`（100000 × 36000，朝施法方向转，每波 0.25 秒） | 4 × 62 |

特效表：`league_missfortune_fx`（bullet、bullet_lt、hit、lovetap、q_bullet、q_hit、q_bounce、q_crit、r_hit、strut），`league_missfortune_big`（e_rain、r_wave）。

## 交付和导入结果（2026-09-28）

- Codex 交了 12 张生图原稿（`missfortune_fx_delivery.zip`：2172×724、1983×793、1659×948 等画布，半透明边），附 `manifest.json`（schema `missfortune-vfx-raw-v1`，每帧的 `source_rect`）、`HANDOFF.md`、`GENERATION_PROMPTS.json` 和 `PREVIEW.html`。R 的一波是黑底，其余 11 张透明。原稿不进仓库。
- `tools/art/import_missfortune.py --raw <交付文件夹>` 按 manifest 切帧，黑底按亮度转透明，每张 16 色，每个游戏像素取覆盖它的原稿像素里最多的颜色，写成这里的 `missfortune_fx_*.png`（8×8 方块的原尺寸条）和 `missfortune_fx_anchors.json`。
- 大小按技能范围：普攻子弹 12 px、红心子弹 14 px、命中 14 px、红心爆开 18 px、Q 子弹 20 px、Q 命中 22 px、弹射命中 24 px、暴击 32 px、R 火花 10 px、大步流星的地圈 20 px、弹雨地圈 60 px 宽（半径 30000；Codex 画得比 2:1 更扁，约 3:1）。R 的一波横竖分开缩放到 100 × 72 px（长 100000 的矩形、±20°），锚点固定在每格同一列（第 1 帧的枪口），这样七发子弹逐帧往前飞。
- 命中、红心和星芒按格子中心定位（Codex 每帧都画在格子正中，画面自己的包围盒会随散开的火花漂移）；大步流星和弹雨按 Codex 画的地圈中心行贴在脚下；弹雨 1 秒一循环，列两遍覆盖 2 秒。
