# 猩红收割者 弗拉基米尔：给 Codex 的特效提示词（第 3 步）

> **这一份是 19 张特效图。** 造型和动作已定（`design/vladimir_design.png`，28×40 格，8 倍）。
> - 大小对照 `design/vladimir_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，右边是原版吟游诗人。每条写的大小都是游戏像素（格）。
> - `design/vladimir_shots.png`：普攻、Q、E 释放、W 血池和 R 出手那几帧的动作（4 倍），青色十字是脚下（血弹从抬起的那只手飞出去）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里弗拉基米尔自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。颜色和英雄联盟一样：**所有技能都是血红色（从白粉色的芯到深红），R 血之瘟疫偏酒红、带一点紫；回血是淡粉白色**。
> - **特效要亮**：以前魔腾的特效画成了最深的几档颜色，叠在人身上看不见。弗拉基米尔全是红色，更要注意：每个形状都要有白色或淡粉色的芯和最亮的几档红，暗底上一眼能看见，不要整张都是深红。
> - **挂在人身上和地上的画面游戏不会左右翻**（红色方朝左也一样画）：这些都要**左右对称**。飞行的画面会转到飞行方向，所以朝右画、上下大致对称。
> - 特效照下面第 1–19 条和「所有特效图的规则」画，每张一个 PNG，文件名 `vladimir_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`vladimir_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「深红契约」 | 射一颗血弹；最大生命值越高，技能伤害越高 | `vladimir_fx_a_bolt` · `vladimir_fx_a_hit` |
| 技能 1 = Q「鲜血转换」 | 从一个敌人身上抽血：打伤害、血球飞回来给自己回血；每第二次是「血红狂潮」（回血翻倍、加速） | `vladimir_fx_q_drain` · `vladimir_fx_q_orb` · `vladimir_fx_q_rush` · `vladimir_fx_q_heal` · `vladimir_fx_q_ready` |
| 技能 2 = E「血之潮汐」 | 蓄力 1 秒，然后往四周放一圈血弹，打中的敌人减速 | `vladimir_fx_e_charge` · `vladimir_fx_e_burst` · `vladimir_fx_e_bolt` · `vladimir_fx_e_hit` |
| W「血池」（自动） | 危险时化成血池 2 秒：不能被选中，脚下的敌人减速、被吸血 | `vladimir_fx_w_splash` · `vladimir_fx_w_pool` · `vladimir_fx_w_drain` |
| 大招 = R「血之瘟疫」 | 丢进敌方英雄堆里：中了的人受到的伤害 +10%，3 秒后爆开，每个英雄给他回一次血 | `vladimir_fx_r_cloud` · `vladimir_fx_r_mark` · `vladimir_fx_r_burst` · `vladimir_fx_r_heal` |
| 高手连招 | 一「E→Q」：潮汐打中英雄后的 Q 直接是血红狂潮；二「E-W」：血池结束时 E 好了，钻出来直接甩一圈满蓄的潮汐；三「闪 R E」：R 落下时 E 好了，先化成血雾往敌人堆里闪一步，再甩一圈潮汐 | `vladimir_fx_q_rush` · `vladimir_fx_e_burst` · `vladimir_fx_c_blink` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**血、光、血雾、血点没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 血红（所有技能的主色）：`#FFFFFF`、`#FFE0E4`、`#FFA8B0`、`#FF5A64`、`#F01828`、`#B80A1C`、`#780614`；
  - 酒红（R 血之瘟疫）：`#FFFFFF`、`#FFD8EC`、`#F59AC8`、`#DC5A9C`、`#B42870`、`#7E1450`、`#4A0A30`；
  - 淡粉白（回血、强化 Q 的芯）：`#FFFFFF`、`#FFF2F4`、`#FFD0D8`、`#FF9CAC`、`#FF6C84`；
- **飞行的画面朝右画，而且上下大致对称**（`a_bolt`、`q_orb`、`q_rush`、`e_bolt`）：游戏会把它转到飞行方向，往左飞时整张会上下翻过来。
- **挂在人身上和地上的画面左右对称**（`q_ready`、`e_charge`、`e_burst`、`w_splash`、`w_pool`、`w_drain`、`r_cloud`、`r_mark`、`c_blink` 和所有命中、回血），按每条写的站位画；命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍）。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人；蓄力的血球罩子只画边和绕着转的血珠，不要盖住人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（19 张）

19 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：E 半径约 20000，W 血池半径约 18000，R 半径约 22000）。

### 1. `vladimir_fx_a_bolt.png`：普攻血弹（飞行中，朝右，循环），3 帧

弗拉基米尔的普攻：一颗白芯的血珠飞出去，后面拖一条短短的血色尾迹，甩出两三滴小血点（参考 Z_trail、common_BloodDrops）。朝右飞，上下大致对称。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a FLYING BLOOD BOLT going to the RIGHT, 3 frames, a seamless loop: a white-cored glossy ball of blood 4 squares across at the right end, a tapering crimson trail 6 squares long to the LEFT, 2-3 tiny droplets flicking off the trail; the trail ripples from frame to frame; roughly symmetric above and below the middle line.
Layout: one horizontal row of 3 equal cells, each 192x128 (image 576x128); the ball on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `vladimir_fx_a_hit.png`：普攻打中（目标身上），4 帧

血弹打中：一下白芯的血花溅开，几滴血点往外飞（参考 SplashParticles、common_BloodDrops）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a small BLOOD SPLASH HIT, 4 frames: 1 a white-pink flash 6 squares across; 2 a crown of red splashes bursting out to 10 squares, droplets flying out; 3 the droplets farther out, darker; 4 two fading droplets.
Layout: one horizontal row of 4 equal cells, each 192x192 (image 768x192); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `vladimir_fx_q_drain.png`：Q 鲜血转换：从敌人身上抽血（目标身上），5 帧

Q 打中：敌人胸口一下白芯的血花，几缕血丝从身上被扯出来、卷成一团往上冒（之后变成一颗血球飞回弗拉基米尔，见下一条）（参考 vlad_blood_transfusion_spin、common_BloodStrand、Q_P_Burst_Ring）。中间是人，不要画人。左右对称。约 16 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a BLOOD DRAIN on a figure (do NOT draw the figure), 5 frames: 1 a white-red flash at chest height (the middle of the cell); 2 a small ring of blood bursts out, 4-5 thin blood strands torn out of the chest curling outward; 3 the strands swirl together into a spinning knot of blood 6 squares across just above the chest; 4 the knot brightest, droplets spinning round it; 5 the knot gone, a few fading droplets. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 256x320 (image 1280x320); centered in every cell (the figure's chest at the middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `vladimir_fx_q_orb.png`：Q 血球飞回弗拉基米尔（飞行中，朝右，循环），4 帧

从敌人身上抽出来的血飞回弗拉基米尔：一颗旋转的血球，白芯，外面一圈卷着的血丝，后面拖一条血色尾迹（参考 vlad_blood_transfusion_spin、color-vladhealtrail）。朝右飞，上下大致对称。约 12 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a SPINNING BLOOD ORB flying to the RIGHT, 4 frames, a seamless loop: a white-cored ball of blood 5 squares across near the right end, two blood strands spiralling round it a quarter turn each frame, a crimson trail 6 squares long to the LEFT with 2 droplets; roughly symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 224x160 (image 896x160); the orb on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `vladimir_fx_q_rush.png`：Q 血红狂潮：强化的大血球（飞行中，朝右，循环），4 帧

强化的 Q（血红狂潮，英雄联盟里血条下面那根槽满了的那一下）：比普通血球大一圈、更亮，白芯更大，外面三道血丝绕着转，尾迹更长、甩出更多血点。朝右飞，上下大致对称。约 16 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614) and a pale heal ramp (#FFFFFF, #FFF2F4, #FFD0D8, #FF9CAC, #FF6C84).
Effect: a BIG BRIGHT BLOOD ORB flying to the RIGHT, 4 frames, a seamless loop: like a bigger, brighter copy of a blood orb - a white and pale-pink core 5 squares across inside a red ball 8 squares across near the right end, three blood strands spiralling round it, a long crimson trail 8 squares to the LEFT throwing off 3-4 droplets; roughly symmetric above and below the middle line.
Layout: one horizontal row of 4 equal cells, each 288x192 (image 1152x192); the orb on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `vladimir_fx_q_heal.png`：Q 回血（弗拉基米尔身上），5 帧

血球回到弗拉基米尔身上的回血：胸口一下淡粉白色的光，一圈血色的光从身上扩开，几颗淡粉色的小光点和血点往上飘（参考 Kindred_Base_R_Heal_spark、R_Heal_Target_Sparkies）。中间是人，不要画人。左右对称。约 18 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614) and a pale heal ramp (#FFFFFF, #FFF2F4, #FFD0D8, #FF9CAC, #FF6C84).
Effect: a HEAL ON A FIGURE (do NOT draw the figure), 5 frames: 1 a pale pink-white flash at chest height (the middle of the cell); 2 a ring of red light spreads out round the body (an upright oval 16 x 22 squares), pale pink motes popping out; 3 the oval at full size, motes and small droplets rising; 4 the oval fading, the motes higher; 5 a few fading motes near the top. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 288x384 (image 1440x384); centered in every cell (the figure's chest at the middle). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `vladimir_fx_q_ready.png`：Q 血红狂潮待命（弗拉基米尔脚下，循环），4 帧

下一个 Q 是血红狂潮的时候：弗拉基米尔脚下一圈慢慢转的血色光环，环上冒几个血泡和小血点（英雄联盟里他满槽时身上的血红光）（参考 Q_Buf_Blood、bloodring）。只画脚下的环，左右对称，不要盖住人。约 20 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a LOOPING BLOOD RING at a figure's feet (do NOT draw the figure), 4 frames, a seamless loop: a flat ellipse of red light on the ground (18 x 6 squares, 1 square thick, brighter at the front), small blood bubbles rising and popping on it, red motes circling along it; left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 320x128 (image 1280x128); the ellipse's middle at the middle of every cell (the feet). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `vladimir_fx_e_charge.png`：E 血之潮汐：蓄力（弗拉基米尔身上，循环），4 帧

E 蓄力的那 1 秒：弗拉基米尔身边一个慢慢转的血球罩子——一圈血丝和血珠绕着他转，越转越密，脚下一圈血色的光（参考 E_Bloodball_Stings、E_blood_core、E_TeamCircle）。罩子只画边和绕着转的血珠，**里面空着**，不要盖住人。左右对称。约 28 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a LOOPING BLOOD SPHERE CHARGING round a figure (do NOT draw the figure; leave the inside EMPTY), 4 frames, a seamless loop: blood strands and glossy blood beads circling round the figure along the rim of a sphere 26 squares wide and 28 tall, a quarter turn each frame, beads brighter in front; a flat red ring on the ground at the feet (an ellipse 22 x 8 squares); left-right symmetric overall.
Layout: one horizontal row of 4 equal cells, each 448x480 (image 1792x480) (16 px a square here); the figure's feet 3 squares (48 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `vladimir_fx_e_burst.png`：E 释放：血浪从身上炸开（弗拉基米尔身上），5 帧

E 蓄满放出去的那一下：一圈血浪从弗拉基米尔身上炸开，地上一个大大的血色冲击环往外扩（参考 E_tar_Wave_Base_v2、E_IndicatorRing_Strokes、vlad_king_blood_nova）。中间是人，不要画人。左右对称，地上的环是从斜上方看的椭圆（宽是高的 2 倍）。约 44 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a BLOOD NOVA bursting out of a figure (do NOT draw the figure), 5 frames: 1 a white-red flash round the figure's chest; 2 a ring of blood light spreads out on the ground (an ellipse 24 x 12 squares) and a burst of blood spray flies out sideways; 3 the ground ring at full size (an ellipse 42 x 21 squares, 2 squares thick), droplets in the air; 4 the ring thinning and darkening, droplets falling; 5 a faint broken ring. Left-right symmetric; the ring seen from above at an angle.
Layout: one horizontal row of 5 equal cells, each 352x240 (image 1760x240) (8 px a square here); the figure's feet 5 squares (40 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `vladimir_fx_e_bolt.png`：E 血之潮汐的血弹（飞行中，朝右，循环），3 帧

E 放出去的一圈血弹里的一颗：一道弯弯的血色弹头，白芯，后面拖一条血色的线（参考 vlad_bloodking_tidesofblood_mis_lines、E_Ryze_Base_Q_mis_Trail_shape、E_Ryze_Base_Q_leadingedge）。朝右飞，上下大致对称。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a BLOOD WAVE BOLT flying to the RIGHT, 3 frames, a seamless loop: a white-cored crescent-shaped head of blood 3 squares wide and 5 tall at the right end, curving forward, a thin crimson streak 7 squares long trailing to the LEFT with a droplet or two; roughly symmetric above and below the middle line.
Layout: one horizontal row of 3 equal cells, each 192x128 (image 576x128); the bolt on the middle line of every cell, near the right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `vladimir_fx_e_hit.png`：E 血弹打中（目标身上），4 帧

血弹打中：一下白芯的血花，一小圈血点溅开（参考 SplashParticles_4x2）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a BLOOD BURST HIT, 4 frames: 1 a white-red flash 7 squares across; 2 a ring of red splashes 12 squares across, droplets flying out; 3 the droplets farther out, the ring dimming; 4 fading droplets.
Layout: one horizontal row of 4 equal cells, each 224x224 (image 896x224); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `vladimir_fx_w_splash.png`：W 血池：化成血池的那一下（弗拉基米尔脚下），5 帧

弗拉基米尔化成一滩血（动作帧里自己画了脚下那滩血）：这一张是化进去和钻出来时脚下溅起的一圈血花——血往四周溅开、往上喷几股，落回地上（参考 common_SanguinePoolProj、SplashParticles_2x2、common_color-bloodpool-pink）。左右对称。约 36 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a BIG BLOOD SPLASH on the ground at a figure's feet (do NOT draw the figure), 5 frames: 1 a flat red splash on the ground (an ellipse 18 x 6 squares) with a white-red flash; 2 blood spurts shooting up and out in a crown, 14 squares high, droplets flying; 3 the crown at full size (32 squares wide), droplets at the top; 4 the blood falling back, splashes landing round the edge; 5 a few droplets on the ground. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 288x192 (image 1440x192) (8 px a square here); the feet 4 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `vladimir_fx_w_pool.png`：W 血池中（弗拉基米尔脚下，循环），6 帧

血池在地上的 2 秒：一大滩冒着泡的血池，边上翻着血浪，池面一层亮红的光，几个血泡冒上来破掉（参考 common_SanguinePoolProj、common_color-bloodpool-pink、Vladimir_Base_Mist）。从斜上方看的椭圆（宽是高的 2 倍），左右对称。6 帧无缝循环。约 40 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a LOOPING POOL OF BLOOD on the ground (do NOT draw a figure), 6 frames, a seamless loop: a pool of glossy blood (an ellipse 38 x 18 squares) with a bright red surface, a lighter rippling rim, 3-4 blood bubbles rising and popping at different spots, small ripples running round the edge; left-right symmetric overall; seen from above at an angle.
Layout: one horizontal row of 6 equal cells, each 320x160 (image 1920x160) (8 px a square here); the ellipse's middle at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `vladimir_fx_w_drain.png`：W 血池吸血（敌人身上，循环），4 帧

站在血池上的敌人被慢慢吸血：身上几缕细细的血丝往下流向地面，脚边几个血泡（参考 common_BloodStrand、common_webblood32）。中间是人，不要画人，不要盖住人。左右对称。约 14 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a LOOPING BLOOD SIPHON on a figure (do NOT draw the figure), 4 frames, a seamless loop: 3-4 thin blood strands trickling down from the figure's chest to the ground on both sides, droplets running along them, 2 small bubbles at the feet; left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 224x352 (image 896x352); the figure's feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `vladimir_fx_r_cloud.png`：R 血之瘟疫：落下的血云（地上，施法点），7 帧

大招丢在敌人堆里：一大团酒红色、血红色的瘟疫血雾在地上翻滚着炸开，雾里卷着血丝（参考 Vladimir_Base_Mist、R_Swirl_Trail、vlad_vert_purplered、color-bloodsmoke32）。从斜上方看，左右对称。约 52 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a plague ramp (#FFFFFF, #FFD8EC, #F59AC8, #DC5A9C, #B42870, #7E1450, #4A0A30) and a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a PLAGUE CLOUD bursting on the ground, 7 frames: 1 a small wine-red puff at the bottom middle; 2 a swirl of crimson and wine-magenta mist rolls out (30 squares wide), blood strands curling in it; 3 the cloud at full size (50 squares wide, 30 tall), billowing, a lighter pink rim on the puffs; 4 the cloud rolling, swirls turning; 5 the cloud thinning in the middle; 6 thin wisps; 7 fading wisps. Left-right symmetric overall.
Layout: one horizontal row of 7 equal cells, each 416x272 (image 2912x272) (8 px a square here); the cloud's bottom middle 3 squares (24 px) above the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `vladimir_fx_r_mark.png`：R 瘟疫标记（敌人身上，循环），4 帧

中了血之瘟疫的敌人：身上一层慢慢翻滚的酒红色血雾，头顶上方一个转着的血色瘟疫印记（一圈带刺的血环），几滴血往上飘（参考 R_Swirl_Trail、Vlad_Spiral_Purple_Flare_02、Q_P_Burst_Ring）。中间是人，不要盖住人。左右对称。约 16 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a plague ramp (#FFFFFF, #FFD8EC, #F59AC8, #DC5A9C, #B42870, #7E1450, #4A0A30) and a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a LOOPING PLAGUE MARK on a figure (do NOT draw the figure), 4 frames, a seamless loop: thin wisps of wine-red mist curling round the figure's body (an upright oval 14 x 20 squares, only wisps at its edge), and above the head, at the top middle of the cell, a spiky blood sigil (a ring of 6 short blood thorns, 7 squares across) turning a twelfth each frame with a bright pink core; 2 droplets drifting up; left-right symmetric.
Layout: one horizontal row of 4 equal cells, each 256x448 (image 1024x448) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `vladimir_fx_r_burst.png`：R 瘟疫爆开（敌人身上），6 帧

3 秒后瘟疫在敌人身上爆开：身上一下白粉色的闪光，一大团血花和酒红色的血雾从身体里炸出来，往四周喷，血点落下（参考 vlad_king_blood_nova、Vlad_Burst_Black、SplashParticles_4x2）。中间是人，不要画人。左右对称。约 24 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a plague ramp (#FFFFFF, #FFD8EC, #F59AC8, #DC5A9C, #B42870, #7E1450, #4A0A30) and a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a PLAGUE BURST on a figure (do NOT draw the figure), 6 frames: 1 a white-pink flash at chest height; 2 a big explosion of blood spray and wine-red mist bursts out of the chest (18 squares across); 3 the burst at full size (22 x 26 squares), blood strands flung out; 4 the mist rolling, droplets falling; 5 thin mist; 6 a few droplets. Left-right symmetric.
Layout: one horizontal row of 6 equal cells, each 384x480 (image 2304x480) (16 px a square here); the figure's chest at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `vladimir_fx_r_heal.png`：R 吸回来的血（弗拉基米尔身上），6 帧

瘟疫爆开后血回到弗拉基米尔身上：几道血色的光带从四面卷过来、绕着他转一圈收进身体，胸口一下淡粉白色的光，小光点往上飘（参考 R_Heal_Target_Swirl、R_Heal_Colors、R_Heal_Target_Sparkies）。中间是人，不要画人。左右对称。约 26 格宽、32 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614) and a pale heal ramp (#FFFFFF, #FFF2F4, #FFD0D8, #FF9CAC, #FF6C84).
Effect: a BLOOD-RETURN HEAL on a figure (do NOT draw the figure), 6 frames: 1 four ribbons of red light coming in from the cell's corners; 2 the ribbons spiralling round the figure (an upright oval 22 x 28 squares); 3 the ribbons tightening round the chest; 4 a pale pink-white flash at the chest as they sink in; 5 pale motes rising; 6 a few fading motes. Left-right symmetric overall.
Layout: one horizontal row of 6 equal cells, each 416x512 (image 2496x512) (16 px a square here); the figure's chest at the middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `vladimir_fx_c_blink.png`：连招「闪 R E」：血雾闪烁（地上，起点和落点各一次），5 帧

高手连招里，大招前往敌人堆里闪一步（游戏里没有闪现，用这一下代替）：弗拉基米尔化成一团血雾散开、在落点重新凝出来——一团血红的雾从脚下往上卷，里面闪着血点，最后散掉（参考 Vladimir_Base_Mist、Z_Smoke_Erode、SplashParticles_2x2）。中间是人，不要画人。左右对称。约 20 格宽、28 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around blood, light, droplets, mist or glows, BRIGHT colours (each shape lit with its lightest shades and a white or pale core - it must read on a dark battlefield), colours only from a blood ramp (#FFFFFF, #FFE0E4, #FFA8B0, #FF5A64, #F01828, #B80A1C, #780614).
Effect: a BLOOD MIST BLINK at a figure's place (do NOT draw the figure), 5 frames: 1 a white-red flash at the middle; 2 a column of crimson mist swirls up from the feet to above the head (18 x 26 squares), droplets glinting in it; 3 the mist billowing, a lighter pink rim; 4 the mist breaking into wisps and droplets; 5 fading wisps. Left-right symmetric.
Layout: one horizontal row of 5 equal cells, each 320x448 (image 1600x448) (16 px a square here); the figure's feet 2 squares (32 px) above the bottom, horizontally centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `vladimir_fx_a_bolt` | view_projectiles `league_vladimir_a_bolt`（循环，朝飞行方向转） | 10 × 6 |
| `vladimir_fx_a_hit` | view_effects `league_vladimir_a_hit`（跟随，画在人物上面） | 12 |
| `vladimir_fx_q_drain` | view_effects `league_vladimir_q_drain`（跟随，画在人物上面） | 16 × 20 |
| `vladimir_fx_q_orb` | view_projectiles `league_vladimir_q_orb`（循环，朝飞行方向转） | 12 × 8 |
| `vladimir_fx_q_rush` | view_projectiles `league_vladimir_q_rush`（循环，朝飞行方向转；第二次 Q 和连招一用） | 16 × 10 |
| `vladimir_fx_q_heal` | view_effects `league_vladimir_q_heal`（跟随，画在人物上面） | 18 × 24 |
| `vladimir_fx_q_ready` | view_buffs `league_vladimir_q_ready`（循环，画在人物下面；下一个 Q 是强化的时候一直在） | 20 × 8 |
| `vladimir_fx_e_charge` | view_buffs `league_vladimir_e_charge`（循环，画在人物上面；蓄力的 1 秒里） | 28 × 30 |
| `vladimir_fx_e_burst` | view_effects `league_vladimir_e_burst`（BIG，跟随，画在人物上面；释放的那一下，连招二、三也用） | 44 × 30 |
| `vladimir_fx_e_bolt` | view_projectiles `league_vladimir_e_bolt`（循环，朝飞行方向转；一圈 8 颗往外飞） | 10 × 6 |
| `vladimir_fx_e_hit` | view_effects `league_vladimir_e_hit`（跟随，画在人物上面） | 14 |
| `vladimir_fx_w_splash` | view_effects `league_vladimir_w_splash`（BIG，画在人物上面；进池和出池各放一次） | 36 × 24 |
| `vladimir_fx_w_pool` | view_buffs `league_vladimir_w_pool`（循环，BIG，画在人物下面；2 秒，就是减速吸血的范围） | 40 × 20 |
| `vladimir_fx_w_drain` | view_buffs `league_vladimir_w_drain`（循环，画在人物上面；站在血池里的敌人身上） | 14 × 22 |
| `vladimir_fx_r_cloud` | view_effects `league_vladimir_r_cloud`（BIG，画在人物上面；施法点） | 52 × 34 |
| `vladimir_fx_r_mark` | view_buffs `league_vladimir_r_mark`（循环，画在人物上面；3 秒，受到伤害 +10%） | 16 × 28 |
| `vladimir_fx_r_burst` | view_effects `league_vladimir_r_burst`（跟随，画在人物上面；3 秒后） | 24 × 30 |
| `vladimir_fx_r_heal` | view_effects `league_vladimir_r_heal`（跟随，画在人物上面；每打中一个英雄回一次血） | 26 × 32 |
| `vladimir_fx_c_blink` | view_effects `league_vladimir_c_blink`（画在人物上面；起点、落点各放一次） | 20 × 28 |

- 血池在 `skill_w` 动作帧里已经画了他脚下那一小滩（rig_vladimir.py 的 POOL）；`w_pool` 是减速吸血的范围，画在人物下面（z -1），和动作帧里那滩对齐。
- 血弹的出生高度按 `design/vladimir_shots.png` 里抬手的位置定（`y_offset`），归位的子弹不要高过目标中心 8 格以上（凯特琳的教训）。
- `e_burst`、`r_cloud`、`w_splash` 是地上的画面：放在 ViewEffect 里（不随飞行转），不要挂在 RangeProjectile 的 view 上（红色方会倒过来，蕾欧娜的教训）。
- 清掉 Codex 给光和血描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
