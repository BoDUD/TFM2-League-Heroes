# 蔚：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作条已经做完（`design/vi_ingame.png` 是游戏里的帧，3 倍；跑步另外在重画），这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里蔚经典皮肤自己的特效贴图（Q 冲刺的热芯 VI_Q_Dash_Hot_Center、地面划痕 Q_Ground_trench、土块 Q_dirst_clump、撞击球 Vi_Q_Dash_Head；被动的冲击弧 Vi_W_Shockwaves 和锯齿纹 Pass_DeBuff_squigeles；E 的拳套光 E_Activation_Hand；R 的地裂 R_ground_crack；海克斯蓝的光环 Blue_Ring），只在本地用，不要提交。颜色和画风对照 `design/vi_design.png`（定稿造型，8 倍）：她从护目镜到鞋底 40 格。
> - **特效要亮**：每个特效都要有白色 / 青白色的亮芯，海克斯蓝和金色要亮，暗色只做最外层（游戏地面偏暗，暗特效看不见）。
> - 每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`，**不要品红**）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），都放在 **`outputs/vi-fx/`**，最好再打成一个 zip。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + W「爆弹重拳」 | 直拳；每第 3 拳额外伤害、破甲、加攻速 | `vi_fx_hit` · `vi_fx_w_proc` |
| 被动「爆裂护盾」 | 技能打中敌人时得到护盾 3 秒 | `vi_fx_bs_on` |
| 技能 1 = Q「强能冲拳」 | 原地蓄力 0.5 秒，往前冲刺打穿路上的敌人，撞到第一个英雄停下并把他击退 | `vi_fx_q_charge` · `vi_fx_q_go` · `vi_fx_q_hit` · `vi_fx_q_stop` |
| 技能 2 = E「透体之劲」 | 拳套充能，下一拳打出扇形冲击波，打穿目标身后的敌人 | `vi_fx_e_arm` · `vi_fx_e_cone` · `vi_fx_e_hit` |
| 大招 = R「天霸横空烈轰」 | 锁定一个英雄冲过去（撞开路上的敌人），上勾拳把他打飞，砸地 | `vi_fx_r_cast` · `vi_fx_r_trail` · `vi_fx_r_side` · `vi_fx_r_hit` · `vi_fx_r_slam` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光、没有半透明（要透出人的地方用隔格的点）。**没有黑描边**（特效和角色相反），也不要用最暗的颜色给特效描一圈边。
- 颜色（按每条写的用）：
  - 海克斯蓝：`#0D2A6E`、`#1E5BD8`、`#3FA8FF`、`#8FE3FF`；亮芯：`#FFFFFF`、`#E8FBFF`；
  - Q 的热橙：`#7A2E08`、`#D2601A`、`#FF9A2E`、`#FFD27A`、`#FFF4D6`；金：`#8D6246`、`#D7A965`、`#F7D896`；尘土：`#3A3030`、`#6B5A50`、`#9C8A7A`、`#CFC2B0`。
- **画在她身上的（护盾、R 起步）**：格子底部是她的脚，人不画；**从拳头往外的（E 冲击波）**：格子左边中间是拳头，往右；她朝左时游戏会整张左右镜像。**R 拖尾**：格子右边中间是她，往左拖。
- 命中、拳套充能、蓄力居中画，不旋转；地面上的东西是从斜上方看的扁椭圆（宽是高的 2–3 倍）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `vi_fx_hit.png`：普攻命中（目标身上），4 帧

拳头打中：中心一颗白金色的星形闪光，几道白色短线和金色火花往外迸，最后一圈蓝色的海克斯火花散开。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white core (#FFFFFF, #E8FBFF), gold sparks (#8D6246, #D7A965, #F7D896) and hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF).
Effect: a PUNCH IMPACT, 4 frames: 1 a white-gold star flash at the centre; 2 short white speed lines and gold sparks bursting out all round; 3 a ring of small blue hextech sparks; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `vi_fx_w_proc.png`：爆弹重拳·第 3 下（目标身上），6 帧

每第 3 拳的「爆弹重拳」：目标身上猛地一闪，左右两道弯弯的白色冲击弧往外弹（像参考图 Vi_W_Shockwaves），弧里夹着蓝色的海克斯锯齿纹（Vi_Pass_DeBuff_squigeles），最后碎成蓝火花。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, a white flash (#FFFFFF, #E8FBFF), white shockwave arcs and hextech blue squiggles (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF).
Effect: a DENTING BLOW, 6 frames: 1 a bright white-blue flash at the centre; 2 two curved white shockwave arcs bursting out to the left and right (like brackets ( ) opening); 3 the arcs at their widest, short blue zig-zag squiggles between them; 4 the arcs breaking into white dashes and blue sparks; 5-6 fading sparks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `vi_fx_bs_on.png`：爆裂护盾（她身上），10 帧

被动「爆裂护盾」：技能打中敌人时，她胸口一闪，一个圆形的蓝色海克斯护盾泡把她罩住（亮青色的外圈，顶上一道白色高光，泡面上隔格的六边形小点），能看见泡里的人；高光绕着泡转一圈，最后碎成蓝色碎片。格子中间下部是她（27 格宽、40 格高的人，脚在格子底部，不画人）。约 36 格宽、46 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF) and white highlights (#FFFFFF, #E8FBFF).
Effect: a BLAST SHIELD round a character (the character is not drawn: imagine a 27x40-pixel figure standing in the middle of the cell, feet on the bottom row), 10 frames: 1 a flash of blue light at chest height; 2-3 a round hextech bubble grows round the figure: a bright cyan outline ring (2 squares), a white highlight arc on its upper left, a checker of small blue hexagon specks on its surface so the figure stays visible inside; 4-8 the bubble holds, its white highlight sliding round the ring a little each frame; 9 the ring cracks; 10 it breaks into blue shards.
Layout: one horizontal row of 10 equal cells, each 3 wide to 4 tall, image size 1920x256 (each cell 192x256, the feet on the bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `vi_fx_q_charge.png`：Q 强能冲拳·蓄力（拉后的拳套上），5 帧

Q 蓄力 0.5 秒：她拉到身后的拳套上聚起能量：蓝色的光点往拳头吸，形成一颗青白色的能量球，周围有橙金色的热火花和噼啪的蓝色小电弧，越来越亮。格子中间就是拳头。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF), a white-cyan core (#FFFFFF, #E8FBFF) and hot orange sparks (#7A2E08, #D2601A, #FF9A2E, #FFD27A, #FFF4D6).
Effect: a CHARGING GAUNTLET, the fist at the middle of the cell, 5 frames: 1 a few blue specks drawn in toward the centre along curved lines; 2 a small white-cyan orb at the centre with short rays; 3 the orb bigger, small orange-gold heat sparks round it; 4-5 the orb pulsing at its brightest with two short crackling blue arcs.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `vi_fx_q_go.png`：Q 强能冲拳·冲刺起点（地面），6 帧

Q 冲出去的那一下：她起冲的地方炸开一团橙白色的热光（参考图 VI_Q_Dash_Hot_Center），地上一道橙色的划痕往左拖（Vi_Base_Q_Ground_trench），棕色的土块和灰色的尘土被踢起来（Vi_Base_Q_dirst_clump、Q_Smoke），从斜上方看是一个扁椭圆。格子右边是她冲出去的方向。约 30 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hot orange (#7A2E08, #D2601A, #FF9A2E, #FFD27A, #FFF4D6), dust (#3A3030, #6B5A50, #9C8A7A, #CFC2B0).
Effect: a DASH LAUNCH BLAST on the ground behind a charging fighter (she rockets off to the RIGHT), seen from above at an angle, 6 frames: 1 a hot orange-white flash at the right of the cell; 2 brown dirt clumps and grey dust kicked up, a short glowing orange scorch line on the ground trailing to the left; 3 the dust cloud at its widest (a flat oval, twice as wide as tall), small orange sparks; 4-6 the dust settling and fading, the scorch line cooling to brown.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `vi_fx_q_hit.png`：Q 路过命中（目标身上），4 帧

Q 冲刺路上撞到的敌人：一团橙白色的冲击闪光，几粒橙金色火花往外飞。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hot orange (#7A2E08, #D2601A, #FF9A2E, #FFD27A, #FFF4D6).
Effect: an orange IMPACT, 4 frames: 1 a white-yellow flash at the centre; 2 a star of orange fire with short spikes; 3 orange-gold sparks flying out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `vi_fx_q_stop.png`：Q 撞停英雄（目标身上），6 帧

Q 撞到第一个英雄、把他击退：一颗蓝色的海克斯能量球在撞击点炸开（参考图 Vi_Q_Dash_Head：蓝色球壳、白热的芯），一圈白色冲击环往外扩，带橙色火花，最后碎成蓝色碎片。约 26 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF), a white core (#FFFFFF, #E8FBFF) and hot orange sparks (#7A2E08, #D2601A, #FF9A2E, #FFD27A, #FFF4D6).
Effect: a big COLLISION BLAST, 6 frames: 1 a white flash at the centre; 2 a round blue hextech sphere bursting, a white-hot core, orange sparks; 3 a white shockwave ring expanding round it (70% of the cell); 4 the ring at its widest and breaking into white dashes, blue shards flying; 5-6 fading shards and sparks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `vi_fx_e_arm.png`：E 透体之劲·拳套充能（她的拳头上），5 帧

E 施放的那一下（给下一拳充能）：拳套的指节上亮起青蓝色的光（参考图 Vi_E_Activation_Hand_Col / Glo），一圈小光点绕着拳头一闪。格子中间就是拳头。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF) and a white-cyan core (#FFFFFF, #E8FBFF).
Effect: a GAUNTLET POWER-UP on a fist at the middle of the cell, 5 frames: 1 a cyan glint on the knuckles; 2 cyan-blue light spreading over a fist-sized block (8x8 squares) with a white core; 3 a small ring of blue specks flashing round it; 4 the glow at its brightest with short rays; 5 the glow shrinking to a few specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `vi_fx_e_cone.png`：E 透体之劲·冲击波（拳头往前的扇形），6 帧

E 的强化拳打出去：从拳头往前（右）炸开一个扇形冲击波——几道弯弯的白蓝色冲击弧一层层往右扩（参考图 Vi_W_Shockwaves、Vi_Shockwave_Lines），扇形里有蓝色的海克斯锯齿纹和速度线，打穿目标后面的敌人。格子左边中间是她的拳头。约 44 格宽、26 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, white arcs (#FFFFFF, #E8FBFF), hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF).
Effect: a CONE SHOCKWAVE blasting to the RIGHT from a fist at the middle of the cell's LEFT edge, 6 frames: 1 a white flash at the left edge; 2 three curved white-blue shockwave arcs ) ) ) opening to the right, the cone 60% of the cell wide; 3 the arcs reach the right edge, the cone at its widest (spreading to 80% of the cell's height at the right), blue zig-zag squiggles and speed lines inside it; 4 the arcs breaking into white dashes; 5-6 fading blue sparks.
Layout: one horizontal row of 6 equal cells, each 3 wide to 2 tall, image size 2304x256 (each cell 384x256); the fist at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `vi_fx_e_hit.png`：E 命中（目标和后面的敌人身上），4 帧

E 的冲击波打中：一团白蓝色的小冲击，几粒蓝色火花。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, white (#FFFFFF, #E8FBFF) and hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF).
Effect: a small white-blue IMPACT, 4 frames: 1 a white flash; 2 a burst of blue sparks with a white core; 3 sparks flying out; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `vi_fx_r_cast.png`：R 天霸横空烈轰·起步（她身上），5 帧

R 锁定目标、起冲的那一下：她脚下一圈蓝色的光环一闪，几道蓝白色的光柱从地面往上冲，身上一层蓝光。格子中间下部是她（27×40 的人，脚在格子底部，不画人）。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF) and white (#FFFFFF, #E8FBFF).
Effect: a POWER-UP FLASH round a character (not drawn: a 27x40-pixel figure in the middle, feet on the bottom row), 5 frames: 1 a flat blue ring of light flashes round the feet (an oval, twice as wide as tall); 2 several thin blue-white light rays shoot up from the ring past the figure's shoulders; 3 the rays at their tallest, white sparks at their tips; 4 the rays fading upward; 5 a few rising specks.
Layout: one horizontal row of 5 equal cells, each 3 wide to 4 tall, image size 960x256 (each cell 192x256, the feet on the bottom row). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `vi_fx_r_trail.png`：R 冲锋拖尾（她身后），6 帧循环

R 冲向目标时身后的拖尾：一道蓝白色的速度线束往左拖，越往左越细，里面夹着隔格的蓝色光带，每帧闪动。格子右边中间就是她（不画人）。首尾能接上。约 40 格宽、20 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF) and white speed lines (#FFFFFF, #E8FBFF).
Effect: a SPEED TRAIL behind a charging fighter (the fighter is at the middle of the cell's RIGHT edge, not drawn), 6 frames, a seamless loop: long white and blue speed lines streaming to the left from the right edge, tapering and thinning toward the left, a checker band of blue light along the middle, the lines shifting and flickering each frame.
Layout: one horizontal row of 6 equal cells, each 2 wide to 1 tall, image size 1536x128 (each cell 256x128); the fighter at the middle of each cell's right edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `vi_fx_r_side.png`：R 撞开路上的敌人（目标身上），4 帧

R 冲锋路上被撞开、眩晕的敌人：一团蓝白色的撞击闪光，几颗小星星在头顶一闪（眩晕）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF), white (#FFFFFF, #E8FBFF) and gold stars (#8D6246, #D7A965, #F7D896).
Effect: a KNOCK-ASIDE IMPACT, 4 frames: 1 a white-blue flash at the centre; 2 a burst of blue sparks and two small white speed lines; 3 three small gold stars popping above the centre (dazed); 4 the stars and sparks fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `vi_fx_r_hit.png`：R 上勾拳打中目标（目标身上），6 帧

R 的上勾拳把目标打飞：目标脚下一闪，一道蓝白色的能量柱和速度线往上冲（比宽高很多），带金色火花，最后化成往上飘的火花。约 20 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, hextech blue (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF), white (#FFFFFF, #E8FBFF) and gold sparks (#8D6246, #D7A965, #F7D896).
Effect: an UPPERCUT IMPACT that knocks the target up, 6 frames: 1 a white-hot flash low in the cell; 2 a column of blue-white energy and vertical speed lines shooting UP from it (taller than wide); 3 the column at its tallest, gold sparks along it; 4 the column breaking into rising white dashes; 5-6 a few rising sparks fading.
Layout: one horizontal row of 6 equal cells, each 2 wide to 3 tall, image size 1152x288 (each cell 192x288). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `vi_fx_r_slam.png`：R 落地砸地（地面），8 帧

R 上勾拳把目标打飞后砸地：地上一闪，一圈尘土往外炸开，深棕色的地裂往四周裂开，裂缝里透出蓝色的海克斯光（参考图 Vi_Base_R_ground_crack），从斜上方看是扁椭圆。约 40 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, bright glowing colours that read on a dark battlefield, dust (#3A3030, #6B5A50, #9C8A7A, #CFC2B0), dark cracks and hextech blue light (#0D2A6E, #1E5BD8, #3FA8FF, #8FE3FF), a white flash (#FFFFFF, #E8FBFF).
Effect: a GROUND SLAM seen from above at an angle (a flat oval), 8 frames: 1 a white flash at the centre; 2 a ring of dust bursting outward; 3 dark brown cracks radiating from the centre, glowing blue hextech light inside them; 4-6 the cracks glowing and pulsing, the dust settling; 7 the glow fading; 8 faint cracks.
Layout: one horizontal row of 8 equal cells, each 3 wide to 1 tall, image size 3072x128 (each cell 384x128). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `vi_fx_hit` | view_effects `league_vi_hit`（跟随目标） | 12 |
| `vi_fx_w_proc` | view_effects `league_vi_w_proc`（跟随目标，盖在最上层） | 22 |
| `vi_fx_bs_on` | view_effects `league_vi_bs_on`（跟随她，盖在最上层） | 36 × 46 |
| `vi_fx_q_charge` | view_effects `league_vi_q_charge`（跟随她，放在拉后的拳头上） | 14 |
| `vi_fx_q_go` | view_effects `league_vi_q_go`（地面，起冲点，不跟随） | 30 × 14 |
| `vi_fx_q_hit` | view_effects `league_vi_q_hit`（跟随目标） | 12 |
| `vi_fx_q_stop` | view_effects `league_vi_q_stop`（跟随目标） | 26 |
| `vi_fx_e_arm` | view_effects `league_vi_e_arm`（跟随她，放在拳头上） | 14 |
| `vi_fx_e_cone` | view_effects `league_vi_e_cone`（跟随她，从出拳的拳头往右） | 44 × 26 |
| `vi_fx_e_hit` | view_effects `league_vi_e_hit`（跟随目标） | 12 |
| `vi_fx_r_cast` | view_effects `league_vi_r_cast`（跟随她） | 30 × 40 |
| `vi_fx_r_trail` | view_effects `league_vi_r_trail`（跟随她，画在她身后） | 40 × 20 |
| `vi_fx_r_side` | view_effects `league_vi_r_side`（跟随目标） | 14 |
| `vi_fx_r_hit` | view_effects `league_vi_r_hit`（跟随目标） | 20 × 36 |
| `vi_fx_r_slam` | view_effects `league_vi_r_slam`（地面，不跟随） | 40 × 14 |

- Q 蓄力放在 Q 蓄力帧拉后的拳头上，E 充能放在待机的近手拳头上，E 冲击波从 E 第 4 帧（砸拳）的拳头往右，按动作条量位置；R 拖尾的右端在她的站位点后面。
- 护盾 180 tick（3 秒）：动画按 10 帧 + 循环帧铺满；R 拖尾在冲锋期间重复。
- 交回后先量平均亮度和最亮一成，和包里其他英雄比；Codex 给特效描的暗色外圈去掉。
