# 阿卡丽：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型（用户选定的 ①：你直接按游戏尺寸画的那一版）和 10 个动作（含三帧武器修正）已经做完并导入游戏，这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里阿卡丽自己的特效贴图（普攻的斩痕、被动的翡翠绿新月和漩涡纹圆环、Q 的苦无、E 的手里剑和标记图标、W 的烟雾、R 的锥形和指示圈），只在本地用，不要提交。颜色和画风对照 `design/akali_design.png`（定稿造型，8 倍）；大小对照 `design/akali_ingame.png`（游戏里的全部帧，3 倍）：阿卡丽头顶到脚底约 43 格（含马尾 47 格），其他英雄约 35–47 格。
> - 特效照下面第 1–15 条和"所有特效图的规则"画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持一行等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方）。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「我流忍法！潜龙印」 | 镰刀横斩；技能打中英雄后在它脚下出现印记圆环，4 秒内下一次普攻射程翻倍、镰刀甩出去砍远处 | `akali_fx_hit` · `akali_fx_p_ring` · `akali_fx_p_ready` · `akali_fx_p_hit` |
| 技能 1 = Q「我流奥义！寒影」+ W「我流奥义！霞阵」 | 扇形甩出五支苦无，末端减速；身边有敌方英雄时脚下放烟雾 5 秒，她在烟里隐身 | `akali_fx_q_fan` · `akali_fx_q_hit` · `akali_fx_w_smoke` |
| 技能 2 = E「我流奥义！隼舞」 | 后跃并掷出手里剑，标记打中的第一个敌人，0.5 秒后冲过去再斩一刀 | `akali_fx_e_shuriken` · `akali_fx_e_hit` · `akali_fx_e_mark` · `akali_fx_e_dash` · `akali_fx_e2_hit` |
| 大招 = R「我流秘奥义！表里杀缭乱」 | 从目标身上穿过去（路上的敌人都被斩到），2.5 秒后再穿一次，第二段是斩杀 | `akali_fx_r_dash` · `akali_fx_r1_hit` · `akali_fx_r2_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（三套，按每条写的用）：
  - 翡翠绿（主体，阿卡丽的招牌色）：`#FFFFFF`、`#D9FFF0`、`#8CF2CB`、`#2FD99C`、`#12A878`、`#0A6E52`、`#063D2F`；
  - 烟雾暗色（烟、地面、残影）：`#3A4150`、`#272C38`、`#181B24`、`#0E1016`；
  - 钢白（苦无、手里剑、镰刀的刃光）：`#FFFFFF`、`#E4ECEF`、`#AEBDC4`、`#6E7F88`。
- **飞行类特效一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- 命中、爆开、范围特效居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在英雄身上的特效（被动准备好的光）：格子中间留出一个空的人形位置（约 24 格宽、43 格高，脚在格子下方），不要画人，**不能挡住身体和脸**，只画围在外面的光和符号。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `akali_fx_hit.png`：普攻命中，5 帧

镰刀横斩打中目标：一道翡翠绿边的白色弧形斩痕（参考 AA_Swipe），再迸出几点钢白的碎光。约 16 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52) with steel-white sparks (#FFFFFF, #E4ECEF, #AEBDC4).
Effect: a KAMA SLASH IMPACT, 5 frames: 1 a thin bright white curved slash across the center from upper left to lower right; 2 the slash at full size (about 60% of the cell wide), white core with an emerald rim, a few steel-white sparks bursting from its middle; 3 the slash thins and turns emerald, the sparks fly outward; 4 the slash fades to dark green, the sparks shrink; 5 a few small dark green specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the impact centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 2. `akali_fx_p_hit.png`：强化普攻命中（被动），6 帧

被动那一下：镰刀从远处甩过来斩中目标——一道大的翡翠绿新月斩（参考 P_Spin_Ring、P_Swipe_Glow），白色刃光，斩中处爆开一圈绿色碎光。比普攻大得多。约 28 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52, #063D2F).
Effect: an EMPOWERED CRESCENT STRIKE, 6 frames: 1 a thin emerald arc appears at the upper right of the cell; 2 a big crescent slash sweeps down across the center (about 80% of the cell wide), a white-hot edge with a thick emerald body; 3 the crescent at full size, a bright white flash where it crosses the center, emerald shards bursting outward; 4 the crescent thins, the shards fly further; 5 the crescent and the shards fade to dark green; 6 a few faint green specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 3. `akali_fx_p_ring.png`：刺客印记圆环（在被打中的英雄脚下），6 帧

技能打中敌方英雄时它脚下出现的印记：地面上一个翡翠绿的椭圆环，三道新月形的漩涡纹沿着环转（参考 R_Indicator、P_Indicator_Smaller），出现、转一下、淡掉。约 36 格宽、18 格高（从斜上方看的椭圆）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52).
Effect: an ASSASSIN'S MARK RING on the ground, seen from above at an angle (an ellipse twice as wide as it is tall), 6 frames: 1 a thin emerald ellipse appears; 2 the ellipse brightens, three curved crescent flourishes with small curls grow along it, evenly spaced; 3 the flourishes glow white-green, turning a little clockwise; 4 turned a little further; 5 the ring and the flourishes dim to dark green; 6 faint dark green arcs.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); the ellipse fills about 90% of each cell, centered, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 4. `akali_fx_p_ready.png`：印记准备好（在她身上，循环），4 帧

被动准备好时她身边转着几点翡翠绿的光（下一次普攻射程翻倍），在腰和手的高度，**不挡脸和身体**。4 帧循环。约 34 格宽、32 格高，中间留空人形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878).
Effect: a READY GLOW around a standing figure (leave a figure-shaped empty space in the middle, about 60% of the cell width and 80% of the cell height - do NOT draw the figure), 4 frames, a seamless loop: three small emerald motes with white cores circle around the empty figure at waist and hand height, leaving short curved emerald trails; each frame they move a quarter of the way round.
Layout: one horizontal row of 4 equal cells, each 4 wide to 5 tall, image size 1024x320 (each cell 256x320); centered horizontally, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 5. `akali_fx_q_fan.png`：五点破（苦无扇飞出），6 帧

Q 甩出的五支苦无：从左边中点（她的手）呈扇形向右飞出，每支苦无后面拖一道白绿色的短光痕（参考 Q_blades_tex_add_blur），扇形张开约 60°（上下各 30°）。**朝右画，上下对称**，扇形的尖在图的左边正中间。约 45 格长、45 格宽。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, steel-white kunai (#FFFFFF, #E4ECEF, #AEBDC4, #6E7F88) with emerald trails (#D9FFF0, #8CF2CB, #2FD99C, #12A878).
Effect: a FAN OF FIVE KUNAI flying out to the right from one point, 6 frames: the point is the middle of the left edge of each cell; the five kunai spread in a fan about 60 degrees wide (the middle one straight right, two above and two below, mirror-symmetric top to bottom), each a small steel dagger pointing outward with a short emerald-white streak behind it. 1 the five kunai just leaving the point, very close together; 2 a third of the way out; 3 two thirds of the way; 4 at the far right edge of the fan, the streaks longest; 5 the kunai gone, only fading emerald streaks along the five lines; 6 faint dark green specks at the ends.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; the fan's point at the middle of the left edge of every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 6. `akali_fx_q_hit.png`：苦无命中，4 帧

苦无扎中：一个小的翡翠绿四角星闪光（参考 Qv4_star），碎成几点。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52).
Effect: a small KUNAI HIT, 4 frames: 1 a tiny white four-pointed star at the center; 2 the star at full size (about 70% of the cell), white core, emerald points; 3 the star breaks into four emerald chips flying outward; 4 a few dark green specks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 7. `akali_fx_w_smoke.png`：霞阵烟雾（地面，5 秒），10 帧

W 的烟雾：她脚下炸开一团深蓝灰色的烟，铺成地面上的一大圈烟雾（从斜上方看的椭圆），烟团边缘翻滚上升，边上夹着几丝翡翠绿的微光（参考 W_SmokeMult、R_SmokeErode）。第 1–3 帧炸开，第 4–7 帧循环（烟慢慢翻滚），第 8–10 帧散掉。**中间是空的（她站在里面），前面的烟不要高过她的腰**。约 70 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, dark blue-grey smoke (#3A4150, #272C38, #181B24, #0E1016) with a few emerald glints (#8CF2CB, #2FD99C, #12A878).
Effect: a SMOKE SCREEN on the ground around a standing figure (keep the middle of the cloud low and open - the figure stands inside it, do NOT draw a figure), seen from above at an angle: a wide ring of billowing smoke puffs (an ellipse twice as wide as it is tall, lying on the ground), taller puffs at the back, low puffs at the front, a few thin emerald glints drifting in the smoke. 10 frames: 1 a small dark burst at the bottom middle; 2 the burst spreads into a ring of puffs; 3 the ring at full size; 4-7 a seamless loop: the puffs roll slowly around the ring, the glints drift up; 8 the puffs thin out; 9 the ring breaks into scattered wisps; 10 a few faint wisps.
Layout: one horizontal row of 10 equal cells, each 7 wide to 4 tall, image size 2800x160 (each cell 280x160); the ring fills about 90% of each cell's width, its bottom near the cell's bottom, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 8. `akali_fx_e_shuriken.png`：手里剑（飞行），4 帧循环

E 掷出的手里剑：一枚四角钢白手里剑，刃上翡翠绿的边光，中间一个暗色的圆孔，飞行时旋转（参考 E_Shuriken_Blur2、E_Target_Icon_Shuriken）。**朝右画，上下对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, steel-white (#FFFFFF, #E4ECEF, #AEBDC4, #6E7F88) with an emerald rim (#8CF2CB, #2FD99C, #12A878) and a dark hub (#181B24).
Effect: a SPINNING SHURIKEN flying to the right, 4 frames, a seamless loop: a four-pointed throwing star with a dark round hub, steel-white blades with emerald edges, a short emerald speed streak behind it on the left; each frame the star is turned 22.5 degrees further (the loop looks like it spins fast); mirror-symmetric top to bottom apart from the turn.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 9. `akali_fx_e_hit.png`：手里剑命中，5 帧

手里剑打中：一圈翡翠绿的冲击小环，白色的星形闪光，几片钢白碎光（参考 E_hit_Tar_muzzle）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52) with steel-white chips (#E4ECEF, #AEBDC4).
Effect: a SHURIKEN IMPACT, 5 frames: 1 a small white star flash at the center; 2 the star with a round emerald shock ring around it; 3 the ring spreads to about 80% of the cell and thins, steel-white chips flying out; 4 the ring fades to dark green; 5 a few specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 10. `akali_fx_e_mark.png`：手里剑标记（被打中的敌人头顶，循环），4 帧

被手里剑打中的敌人头顶浮着一个翡翠绿的手里剑标记（就是参考图里的 E_Target_Icon_Shuriken），慢慢转，发光。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52).
Effect: a MARK ICON floating above a head, 4 frames, a seamless loop: a flat emerald four-pointed shuriken symbol with a round hole in the middle and a thin bright outline glow; it turns slowly (22.5 degrees a frame) and its glow pulses brighter in frame 3.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 11. `akali_fx_e_dash.png`：隼舞突进残影（留在起点），5 帧

E 第二段冲出去时起点留下的残影：一道向右拉长的深色残影，边上翡翠绿的速度线，向右越来越细，然后散掉。约 48 格长、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, dark smoke (#3A4150, #272C38, #181B24) with emerald speed lines (#D9FFF0, #8CF2CB, #2FD99C, #12A878).
Effect: a DASH AFTERIMAGE streak pointing right, 5 frames: 1 a dark blurred silhouette smear at the left of the cell with short emerald speed lines; 2 the smear stretches to the right edge, thick at the left, thin at the right, emerald lines along its top and bottom; 3 the streak at full length, a white-green line along its middle; 4 the streak breaks into dark wisps and emerald dashes; 5 faint wisps.
Layout: one horizontal row of 5 equal cells, each 3 wide to 1 tall, image size 1920x128 (each cell 384x128); no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 12. `akali_fx_e2_hit.png`：隼舞突进斩中，5 帧

冲到目标身边的那一斩：一道由下往上的翡翠绿斩痕，白色刃光，斩中处一个小闪光。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52).
Effect: a RISING SLASH, 5 frames: 1 a thin white line at the lower left of the cell; 2 a curved slash sweeping up from lower left to upper right across the center, white edge, emerald body; 3 the slash at full size with a white flash at the center; 4 the slash thins and turns dark green, small emerald sparks falling; 5 a few specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 13. `akali_fx_r_dash.png`：表里杀缭乱突进残影（两段都用），6 帧

R 冲刺留下的残影：一道很长、向右的深色斩线（参考 R_ConeTexture、R_Beam_Mult），上下是翡翠绿的刃光，中间一条白线，残影后面散出烟丝。约 64 格长、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, dark smoke (#3A4150, #272C38, #181B24, #0E1016) with an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52).
Effect: a LONG EXECUTION DASH streak pointing right, 6 frames: 1 a thin white line appears across the middle of the cell from left to right; 2 the line thickens into a long dark blade-shaped streak with emerald edges above and below, pointed at both ends; 3 the streak at full size, a bright white-green core; 4 dark smoke wisps peel off its top and bottom; 5 the streak breaks into dark wisps and emerald dashes; 6 faint wisps.
Layout: one horizontal row of 6 equal cells, each 3 wide to 1 tall, image size 2304x128 (each cell 384x128); no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 14. `akali_fx_r1_hit.png`：第一段穿过时的斩中，5 帧

R 第一段从敌人身上穿过去时，敌人身上一道横向的翡翠绿斩痕，白色刃光，斩痕两端细长。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52).
Effect: a HORIZONTAL PASS-THROUGH SLASH, 5 frames: 1 a thin white line across the center; 2 a long thin crescent slash, slightly curved, white edge and emerald body, across about 85% of the cell width; 3 the slash with a bright white flash at its middle and emerald sparks; 4 the slash splits into two thin fading emerald lines; 5 a few specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

### 15. `akali_fx_r2_hit.png`：第二段斩杀，6 帧

R 第二段（斩杀）打中：一个大的 X 形交叉斩，深色的斩痕中心、翡翠绿的刃光、白色的交叉闪光，然后深色的烟和绿色碎光向外炸开。比第一段大、更狠。约 30 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, an emerald ramp (#FFFFFF, #D9FFF0, #8CF2CB, #2FD99C, #12A878, #0A6E52, #063D2F) with dark smoke (#3A4150, #272C38, #181B24).
Effect: an EXECUTION X-SLASH, 6 frames: 1 one diagonal white slash line from upper left to lower right; 2 a second slash from upper right to lower left, forming an X, both with dark cores and emerald edges; 3 the X at full size (about 85% of the cell), a big white flash at the crossing; 4 dark smoke and emerald shards burst outward from the crossing; 5 the X fades, the shards fly further; 6 faint wisps and specks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centered in every cell, no gaps, no borders, no labels. Transparent background (if not possible: pure black #000000).
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `akali_fx_hit` | `view_effects` `league_akali_hit`（普攻命中，跟随） | 16 宽 |
| `akali_fx_p_hit` | `league_akali_p_hit`（强化普攻命中） | 28 |
| `akali_fx_p_ring` | `league_akali_p_ring`（英雄脚下，z -1，跟随） | 36 × 18 |
| `akali_fx_p_ready` | `view_buffs` `league_akali_p_ready` | 24 × 30 |
| `akali_fx_q_fan` | `view_projectiles` `league_akali_q_fan`（LineRangeProjectile，朝施法方向转） | 45 × 45（锥形半径 45000） |
| `akali_fx_q_hit` | `league_akali_q_hit` | 12 |
| `akali_fx_w_smoke` | `league_akali_w_smoke`（CasterViewEffect，地面，不跟随，5 秒：循环帧重复） | 70 × 40（烟雾半径 30000） |
| `akali_fx_e_shuriken` | `view_projectiles` `league_akali_e_shuriken` | 12 |
| `akali_fx_e_hit` | `league_akali_e_hit` | 16 |
| `akali_fx_e_mark` | `view_buffs` `league_akali_e_mark`（头顶，0.7 秒） | 12 |
| `akali_fx_e_dash` | `league_akali_e_dash`（CasterViewEffect，不跟随） | 48 × 16 |
| `akali_fx_e2_hit` | `league_akali_e2_hit` | 20 |
| `akali_fx_r_dash` | `league_akali_r_dash`（CasterViewEffect，不跟随，两段都用） | 64 × 20 |
| `akali_fx_r1_hit` | `league_akali_r1_hit` | 22 |
| `akali_fx_r2_hit` | `league_akali_r2_hit` | 30 |
