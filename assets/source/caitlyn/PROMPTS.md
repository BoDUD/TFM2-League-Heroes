# 凯特琳：给 Codex 的特效提示词（第 3 步）

> **这一份是 22 张特效图。** 造型和 9 个动作已经做完并导入（`design/caitlyn_ingame.png` 是游戏里的全部帧，3 倍），这一轮只画特效。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里凯特琳经典皮肤自己的特效贴图（Q 的蓝色子弹 Q2_Bullet / Q_FlameHead、R 的瞄准圈 R_Decal 和十字准星 R_SniperSight、W 夹子 W_Trap_gadget、E 的绳网 entrapment_mis_Net、爆头的放射弧 Radial_Headshot），只在本地用，不要提交。颜色和画风对照 `design/caitlyn_design.png`（定稿造型，8 倍）：她从帽顶到鞋底 41 格，其他英雄约 35–40 格。
> - 特效照下面每一条和「所有特效图的规则」画，每张一个 PNG，文件名和排版按每条写的来。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最好打成一个 zip。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「爆头」 | 步枪开枪；每第 6 枪爆头（更大的子弹、更亮的枪口和命中）；被夹子夹住的英雄优先被爆头 | `caitlyn_fx_bolt` · `caitlyn_fx_shot` · `caitlyn_fx_hit` · `caitlyn_fx_hs_bolt` · `caitlyn_fx_hs_shot` · `caitlyn_fx_hs_hit` |
| E「90口径绳网」（并在普攻里） | 敌方英雄贴身时这一枪改射网：枪口一团烟，网飞出去罩住目标 1 秒（减速），她向后跳开 | `caitlyn_fx_e_shot` · `caitlyn_fx_e_net` · `caitlyn_fx_e_hit` · `caitlyn_fx_e_slow` |
| 技能 1 = Q「和平使者」 | 瞄准后射出一发穿透的蓝白能量弹，打中的每个敌人身上炸开蓝光 | `caitlyn_fx_q_muzzle` · `caitlyn_fx_q_bolt` · `caitlyn_fx_q_hit` |
| 技能 2 = W「约德尔诱捕器」 | 把夹子扔到敌方英雄脚下：落地张开、埋伏 8 秒（每 0.25 秒重播一次埋伏图），踩中就合上夹住脚 1.25 秒；没踩中就消失 | `caitlyn_fx_w_throw` · `caitlyn_fx_w_land` · `caitlyn_fx_w_trap` · `caitlyn_fx_w_fade` · `caitlyn_fx_w_snap` |
| 大招 = R「让子弹飞」 | 瞄准目标 1 秒（目标身上一个准星），然后开枪：枪口大爆风、一发很快的长子弹，打中路上第一个敌方英雄 | `caitlyn_fx_r_mark` · `caitlyn_fx_r_muzzle` · `caitlyn_fx_r_bullet` · `caitlyn_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**没有黑描边**（特效和角色相反）。
- 颜色（按每条写的用）：
  - 步枪金：`#5E3B12`、`#A0702A`、`#D7AE50`、`#F2D98A`；海克斯青：`#0E5A7A`、`#1E9FC4`、`#27CCE2`、`#9FF3FF`；白热：`#FFFFFF`、`#FFF6C8`、`#FFE27A`；
  - 烟：`#E6E0D8`、`#B9B0A6`、`#857B72`、`#574F4A`；绳网：`#3A2414`、`#6F4434`、`#A07335`、`#D9B77A`；夹子的钢：`#283447`、`#445E80`、`#8FA6C1`、`#D5E2EE`；准星红：`#7A1020`、`#D13845`、`#FF6A6A`。
- **飞行类特效（子弹、Q 能量弹、R 子弹、绳网）一律朝右画，而且上下对称**：游戏会把它转到飞行方向，向左时整张图转 180°。
- **枪口火光（普攻、爆头、E、Q、R）画在她自己身上**：格子的左边中间就是枪口的位置，火往右喷；她朝左时游戏会整张左右镜像。
- 命中、夹子、准星居中画，不旋转；地面上的东西（夹子、减速标记）是从斜上方看的扁椭圆（宽是高的 2 倍左右）。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（22 张）

大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位）。

### 1. `caitlyn_fx_bolt.png`：普攻子弹（飞行），4 帧循环

从枪口打出去的一颗子弹：短短的白金色弹头，后面拖一道细细的青白色光迹（往左）。约 12 格长、4 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold-white bullet (#FFFFFF, #FFF6C8, #FFE27A, #5E3B12, #A0702A, #D7AE50, #F2D98A) with a thin cyan streak (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF).
Effect: a small RIFLE ROUND flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a short bright white-gold bullet at 80% of the cell width, a thin straight cyan-white streak behind it reaching the left edge, flickering slightly each frame.
Layout: one horizontal row of 4 equal cells, each 4 wide to 1 tall, image size 1024x64 (each cell 256x64); the bullet on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `caitlyn_fx_hs_bolt.png`：爆头子弹（飞行，更大更亮），4 帧循环

爆头的那一发：比普攻大、更亮的子弹，弹头外裹一圈青色的光，后面拖一道长长的青色光迹，光迹两边各一条细细的金色火花线。约 18 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a bright bullet (#FFFFFF, #FFF6C8, #FFE27A) in a cyan glow (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF) with gold sparks (#5E3B12, #A0702A, #D7AE50, #F2D98A).
Effect: a HEADSHOT ROUND flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright white bullet at 80% of the cell width wrapped in a small cyan glow, a long cyan streak behind it to the left edge, two thin lines of gold sparks along the streak's edges, flickering each frame.
Layout: one horizontal row of 4 equal cells, each 3 wide to 1 tall, image size 1152x96 (each cell 288x96); the bullet on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `caitlyn_fx_q_bolt.png`：Q 和平使者的子弹（飞行），4 帧循环

和平使者的大子弹：一枚亮蓝白色的能量弹，前端是箭头形的青蓝光，后面拖一道长长的青蓝色光迹，弹头两侧张开两条蓝色的箭羽形光翼（参考图里的 Q 子弹 Q2_Bullet 和 Q_FlameHead）。约 24 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, blue-white energy (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF, #FFFFFF, #FFF6C8, #FFE27A).
Effect: a PIERCING ENERGY ROUND flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: an arrow-shaped head of white and cyan light at 80% of the cell width, two swept-back wings of blue light opening behind it like the fletching of an arrow, a long cyan trail to the left edge, flickering each frame.
Layout: one horizontal row of 4 equal cells, each 12 wide to 5 tall, image size 1536x160 (each cell 384x160); the round on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `caitlyn_fx_e_net.png`：E 绳网（飞行），4 帧

射出去的绳网：棕色粗绳编成的方格网，四角挂着金色的小铁坠；飞出去时一帧一帧张开（第 1 帧收成一团，第 4 帧完全张开）。约 16 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, brown rope (#3A2414, #6F4434, #A07335, #D9B77A) with small gold weights (#5E3B12, #A0702A, #D7AE50, #F2D98A).
Effect: a NET flying to the RIGHT, 4 frames (not a loop, it ends open): 1 a small bundle of brown rope with four gold weights; 2 opening, the weights pulling the corners out; 3 mostly open, a diamond-shaped mesh of thick brown rope; 4 fully open, a square mesh of 4x4 holes with a gold weight at each corner, SYMMETRIC above and below the middle line, leaning a little forward.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the net centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `caitlyn_fx_w_throw.png`：W 夹子（飞行，翻转），4 帧循环

扔出去的约德尔诱捕器：一个合拢的金色圆形夹子（像个小铁饼，中间一个深色方块，参考图的 W_Trap_gadget），飞的时候翻转（正面、侧面、背面、侧面）。约 8 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold trap (#5E3B12, #A0702A, #D7AE50, #F2D98A) with steel jaws (#283447, #445E80, #8FA6C1, #D5E2EE).
Effect: a CLOSED TRAP tumbling through the air, 4 frames, a seamless loop: a round gold disc with a dark steel square in its middle and a thin steel rim; frame 1 seen face-on (a circle), frame 2 tilted (an ellipse), frame 3 edge-on (a thick line with the jaws' teeth), frame 4 tilted the other way.
Layout: one horizontal row of 4 equal square cells, image size 512x128; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `caitlyn_fx_r_bullet.png`：R 让子弹飞的子弹（飞行），4 帧循环

大招的那一发：很长的金白色子弹，弹头白热，外面裹一层青色光，后面拖一条很长的光迹（快到像一道光束）。约 32 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a white-hot bullet (#FFFFFF, #FFF6C8, #FFE27A, #5E3B12, #A0702A, #D7AE50, #F2D98A) with a cyan glow and trail (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF).
Effect: a SNIPER ROUND flying to the RIGHT very fast, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a long white-hot bullet at 85% of the cell width with a gold rim, wrapped in a thin cyan glow; behind it a long straight beam-like trail of cyan and white light to the left edge, thinning out, a few gold sparks along it.
Layout: one horizontal row of 4 equal cells, each 5 wide to 1 tall, image size 1600x80 (each cell 400x80); the bullet on the middle line of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `caitlyn_fx_shot.png`：普攻枪口火光（她的枪口，朝右），4 帧

开枪时枪口的火光：白热的芯，往右喷出一小团金黄的火焰，上下一点青色火花，最后一缕白烟。格子左边中间就是枪口。约 10 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, hot light (#FFFFFF, #FFF6C8, #FFE27A), gold fire (#5E3B12, #A0702A, #D7AE50, #F2D98A), cyan sparks (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A).
Effect: a small MUZZLE FLASH blasting to the RIGHT from the middle of the cell's LEFT edge (the muzzle is there), 4 frames: 1 a white-hot star at the left edge; 2 a short cone of yellow-gold flame to 70% of the cell width, two tiny cyan sparks above and below; 3 the flame shrinks into a puff of white smoke; 4 faint smoke.
Layout: one horizontal row of 4 equal cells, each 5 wide to 4 tall, image size 1280x256 (each cell 320x256); the muzzle at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `caitlyn_fx_hs_shot.png`：爆头枪口火光，5 帧

爆头那一枪的枪口：更大的白金色火光，外面一圈青色的冲击环往右扩，几道放射状的青白光线。格子左边中间是枪口。约 16 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, hot light (#FFFFFF, #FFF6C8, #FFE27A), gold fire (#5E3B12, #A0702A, #D7AE50, #F2D98A) and a cyan ring (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF).
Effect: a STRONG MUZZLE FLASH to the RIGHT from the middle of the cell's LEFT edge, 5 frames: 1 a big white-hot star at the left edge; 2 a cone of white and gold flame to 80% of the cell width and a thin cyan shock ring (an ellipse, taller than wide) round the muzzle; 3 the ring moves right and widens, short white rays shoot out; 4 the flame breaks into gold sparks, the ring fades; 5 a wisp of white smoke.
Layout: one horizontal row of 5 equal cells, each 4 wide to 3 tall, image size 1280x192 (each cell 256x192); the muzzle at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `caitlyn_fx_e_shot.png`：E 射网的枪口火光，4 帧

射网的后坐力：枪口喷出一团白烟和金色火光，几段绳头往右甩出去。格子左边中间是枪口。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A), gold fire (#5E3B12, #A0702A, #D7AE50, #F2D98A) and rope (#3A2414, #6F4434, #A07335, #D9B77A).
Effect: a NET LAUNCH PUFF from the middle of the cell's LEFT edge, 4 frames: 1 a white flash at the left edge; 2 a round burst of white smoke and gold fire, two short brown rope ends whipping out to the right; 3 a big puff of grey-white smoke; 4 faint smoke.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the muzzle at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `caitlyn_fx_q_muzzle.png`：Q 和平使者出膛（枪口爆风），5 帧

和平使者出膛：枪口一团亮蓝白的闪光，外面一圈青蓝色的冲击环，往右喷出蓝色的光锥，最后散成蓝色光点。格子左边中间是枪口。约 18 格宽、14 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, blue-white energy (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF, #FFFFFF, #FFF6C8, #FFE27A).
Effect: an ENERGY MUZZLE BLAST to the RIGHT from the middle of the cell's LEFT edge, 5 frames: 1 a bright white-cyan flash; 2 a cone of cyan and blue light shooting right to 90% of the cell width, a cyan shock ring round the muzzle; 3 the cone at its biggest with white streaks inside it; 4 the light breaks into blue sparks drifting right; 5 a few fading sparks.
Layout: one horizontal row of 5 equal cells, each 9 wide to 7 tall, image size 1800x280 (each cell 360x280); the muzzle at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `caitlyn_fx_r_muzzle.png`：R 让子弹飞的枪口爆风，6 帧

大招开枪：枪口一大团白金色的闪光，往右冲出一道长长的光锥，枪口外一圈青色和金色的冲击环往外扩，最后是一团白烟。格子左边中间是枪口。约 26 格宽、18 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, hot light (#FFFFFF, #FFF6C8, #FFE27A), gold (#5E3B12, #A0702A, #D7AE50, #F2D98A), cyan (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A).
Effect: a HUGE MUZZLE BLAST to the RIGHT from the middle of the cell's LEFT edge, 6 frames: 1 a big white-hot flash; 2 a long cone of white and gold light shooting right to 95% of the cell width, a cyan and a gold shock ring round the muzzle; 3 the cone at its biggest, the rings spreading; 4 the cone breaks up, white smoke rolling; 5 smoke drifting right; 6 faint smoke.
Layout: one horizontal row of 6 equal cells, each 13 wide to 9 tall, image size 2496x288 (each cell 416x288); the muzzle at the middle of each cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `caitlyn_fx_hit.png`：普攻命中（目标身上），4 帧

子弹打中：一个小小的白金色火花炸开，几粒金色碎屑往外飞。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, hot light (#FFFFFF, #FFF6C8, #FFE27A) and gold sparks (#5E3B12, #A0702A, #D7AE50, #F2D98A).
Effect: a BULLET IMPACT, 4 frames: 1 a small white flash at the centre; 2 a star of white and gold sparks; 3 a few gold sparks flying out; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `caitlyn_fx_hs_hit.png`：爆头命中（目标身上），6 帧

爆头命中：一道白色闪光，一圈青色的放射弧线（参考图的 Radial_Headshot / bolts_Headshot），中间一个小小的十字准星一闪，再散成火花。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, hot light (#FFFFFF, #FFF6C8, #FFE27A), cyan arcs (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF) and gold sparks (#5E3B12, #A0702A, #D7AE50, #F2D98A).
Effect: a HEADSHOT IMPACT, 6 frames: 1 a bright white flash at the centre; 2 a ring of short curved cyan arcs bursting out and a small white crosshair (+) at the centre; 3 the arcs at 80% of the cell, white rays between them; 4 the arcs break into cyan and gold sparks, the crosshair fades; 5 sparks flying out; 6 faint sparks.
Layout: one horizontal row of 6 equal square cells, image size 1536x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `caitlyn_fx_q_hit.png`：Q 命中（目标身上），5 帧

和平使者打中：一团蓝白色的能量火花炸开，蓝色的碎光往外飞。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, blue-white energy (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF, #FFFFFF, #FFF6C8, #FFE27A).
Effect: an ENERGY IMPACT, 5 frames: 1 a white-cyan flash at the centre; 2 a burst of cyan and blue light with sharp rays; 3 blue shards flying out to the right and the sides; 4 fading blue sparks; 5 faint specks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `caitlyn_fx_e_hit.png`：E 网住目标（目标身上，1 秒），10 帧

绳网罩在目标身上：网从上面落下来盖住（第 1–3 帧），收紧（第 4 帧），然后保持（第 5–9 帧，网上的金坠一闪一闪），最后散开消失（第 10 帧）。格子中间是目标的身体（约 14 格宽、20 格高的人），网盖在外面。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, brown rope (#3A2414, #6F4434, #A07335, #D9B77A) with gold weights (#5E3B12, #A0702A, #D7AE50, #F2D98A).
Effect: a NET WRAPPED ROUND A TARGET (the target is not drawn: imagine a 14x20-pixel figure in the middle of the cell), 10 frames: 1-3 an open square net of thick brown rope drops from the top and drapes over the figure's shape; 4 it pulls tight round the figure, the gold weights at the bottom corners; 5-9 holding: the same tight net, the gold weights blinking (bright in 6 and 8); 10 the rope loosens and frays away. The middle of the net is open mesh, so the figure would show through.
Layout: two rows of 5 equal square cells, image size 1280x512 (each cell 256x256); the net centred in every cell, its bottom at 90% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `caitlyn_fx_r_hit.png`：R 大子弹命中（目标身上），7 帧

大子弹打中：一大团白金色的闪光，一圈青色和一圈金色的冲击环往外扩，火花和碎屑往右后方飞（子弹从左边来）。约 28 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, hot light (#FFFFFF, #FFF6C8, #FFE27A), gold (#5E3B12, #A0702A, #D7AE50, #F2D98A), cyan (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF) and smoke (#E6E0D8, #B9B0A6, #857B72, #574F4A).
Effect: a BIG IMPACT, 7 frames: 1 a large white flash at the centre; 2 a white-gold burst with sharp rays, a cyan shock ring and a gold one spreading; 3 the burst at its biggest, sparks and debris flying out mostly to the right; 4 the rings fade, gold sparks fall; 5 white smoke; 6 thin smoke; 7 a few fading sparks.
Layout: one horizontal row of 7 equal square cells, image size 1792x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `caitlyn_fx_w_land.png`：W 夹子落地张开（地面，画在人物下面），5 帧

夹子落地：金色圆形夹子落在地上弹一下，两片带齿的铁颚咔地往两边张开（从斜上方看，整个夹子是扁椭圆），中间一盏青色小灯亮起。约 16 格宽、10 格高，地面在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold trap (#5E3B12, #A0702A, #D7AE50, #F2D98A) with steel jaws (#283447, #445E80, #8FA6C1, #D5E2EE) and a cyan light (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF).
Effect: a TRAP LANDING on the ground seen from above at an angle (flat, an ellipse twice as wide as tall), 5 frames: 1 the closed round gold trap lands with a small puff of dust; 2 it bounces a square up; 3 it settles, the two toothed steel jaws start to open left and right; 4 the jaws wide open, a small cyan light in the middle switches on; 5 open and still, the cyan light bright.
Layout: one horizontal row of 5 equal cells, each 8 wide to 5 tall, image size 1280x160 (each cell 256x160); the ground at 80% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `caitlyn_fx_w_trap.png`：W 夹子埋伏（地面，循环），2 帧

张开的夹子静静躺在地上：两片张开的铁颚，中间的青色小灯一闪（第 1 帧暗、第 2 帧亮）。每 0.25 秒重播一次，所以两帧首尾要能接上，位置和大小和上一张最后一帧一样。约 16 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold trap (#5E3B12, #A0702A, #D7AE50, #F2D98A) with steel jaws (#283447, #445E80, #8FA6C1, #D5E2EE) and a cyan light (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF).
Effect: an ARMED TRAP lying open on the ground (exactly the last frame of the landing sheet), 2 frames, a seamless loop: the flat gold base, the two toothed steel jaws open to the left and right; frame 1 the cyan light dim, frame 2 bright with a tiny glow.
Layout: one horizontal row of 2 equal cells, each 8 wide to 5 tall, image size 512x160 (each cell 256x160); the ground at 80% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `caitlyn_fx_w_fade.png`：W 夹子消失（地面），3 帧

夹子时间到了没踩中：夹子合上，变淡，化成几粒金色火花消失。位置和大小同上。约 16 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold trap (#5E3B12, #A0702A, #D7AE50, #F2D98A), steel (#283447, #445E80, #8FA6C1, #D5E2EE) and gold sparks.
Effect: a TRAP VANISHING, 3 frames: 1 the open trap's jaws snap shut, the light goes out; 2 the closed trap paler and smaller; 3 a few gold sparks where it was.
Layout: one horizontal row of 3 equal cells, each 8 wide to 5 tall, image size 768x160 (each cell 256x160); the ground at 80% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `caitlyn_fx_w_snap.png`：W 夹住目标（目标脚下，1.25 秒），9 帧

夹子咔地合上夹住敌人的脚：第 1 帧铁颚猛地合拢、火花迸出；第 2–8 帧夹着（铁颚合拢咬住，一根短铁链抖动，青色小灯一闪一闪）；第 9 帧松开消失。格子下部中间是目标的脚。约 18 格宽、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, a gold trap (#5E3B12, #A0702A, #D7AE50, #F2D98A) with steel jaws and chain (#283447, #445E80, #8FA6C1, #D5E2EE), a cyan light (#0E5A7A, #1E9FC4, #27CCE2, #9FF3FF) and sparks (#FFFFFF, #FFF6C8, #FFE27A).
Effect: a TRAP SNAPPING SHUT round a target's feet (the target is not drawn; its feet are at the bottom middle of the cell), 9 frames: 1 the two toothed steel jaws slam shut from the sides with white and gold sparks; 2-8 holding: the closed jaws biting, a short steel chain from the gold base rattling (it moves a square each frame), the cyan light blinking (bright in 3, 5 and 7); 9 the jaws spring open and the trap fades.
Layout: one horizontal row of 9 equal cells, each 3 wide to 2 tall, image size 2304x170 (each cell 256x170); the target's feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `caitlyn_fx_r_mark.png`：R 瞄准准星（目标身上，循环），4 帧循环

大招瞄准时罩在目标身上的准星：一个红金色的瞄准圈（外圈带齿轮纹，参考图的 R_Decal 和 R_SniperSight），中间一个细十字，圈慢慢转、一收一放。约 24 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, red (#7A1020, #D13845, #FF6A6A) and gold (#5E3B12, #A0702A, #D7AE50, #F2D98A) lines.
Effect: a SNIPER CROSSHAIR over a target, 4 frames, a seamless loop: a thin red circle with small gold gear teeth round its outside, a thin red cross (+) through the middle with a gap at the centre, small gold corner ticks; the ring turns an eighth of a turn each frame and pulses a little smaller and bigger (frames 1-2-3-4: big, smaller, smallest, smaller).
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centred in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `caitlyn_fx_e_slow.png`：E 减速标记（目标身上，循环），4 帧循环

被网减速时目标脚边：几根断掉的棕色绳头拖在地上，后面几道往后飘的白色速度线。约 16 格宽、8 格高，地面在格子下部。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no outline, brown rope (#3A2414, #6F4434, #A07335, #D9B77A) and white lines (#E6E0D8, #B9B0A6, #857B72, #574F4A).
Effect: a SLOW MARK at a target's feet, 4 frames, a seamless loop: two or three frayed brown rope ends trailing on the ground and three short white speed lines behind them, the lines sliding left a square each frame.
Layout: one horizontal row of 4 equal cells, each 2 wide to 1 tall, image size 1024x128 (each cell 256x128); the ground at 85% of the cell height. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `caitlyn_fx_bolt` | view_projectiles `league_caitlyn_bolt` | 12 × 4 |
| `caitlyn_fx_hs_bolt` | view_projectiles `league_caitlyn_hs_bolt`（夹子爆头也用它） | 18 × 6 |
| `caitlyn_fx_q_bolt` | view_projectiles `league_caitlyn_q_bolt` | 24 × 10 |
| `caitlyn_fx_e_net` | view_projectiles `league_caitlyn_e_net`（不循环，最后一帧停住） | 16 × 14 |
| `caitlyn_fx_w_throw` | view_projectiles `league_caitlyn_w_throw` | 8 × 8 |
| `caitlyn_fx_r_bullet` | view_projectiles `league_caitlyn_r_bullet` | 32 × 6 |
| `caitlyn_fx_shot` | view_effects `league_caitlyn_shot`（她身上，跟随） | 10 × 8 |
| `caitlyn_fx_hs_shot` | view_effects `league_caitlyn_hs_shot`（她身上，跟随） | 16 × 12 |
| `caitlyn_fx_e_shot` | view_effects `league_caitlyn_e_shot`（她身上，跟随） | 12 × 12 |
| `caitlyn_fx_q_muzzle` | view_effects `league_caitlyn_q_muzzle`（她身上，跟随） | 18 × 14 |
| `caitlyn_fx_r_muzzle` | view_effects `league_caitlyn_r_muzzle`（她身上，跟随） | 26 × 18 |
| `caitlyn_fx_hit` | view_effects `league_caitlyn_hit`（跟随） | 10 |
| `caitlyn_fx_hs_hit` | view_effects `league_caitlyn_hs_hit`（跟随） | 20 |
| `caitlyn_fx_q_hit` | view_effects `league_caitlyn_q_hit`（跟随） | 16 |
| `caitlyn_fx_e_hit` | view_effects `league_caitlyn_e_hit`（跟随） | 22 × 22 |
| `caitlyn_fx_r_hit` | view_effects `league_caitlyn_r_hit`（大图，跟随） | 28 |
| `caitlyn_fx_w_land` | view_effects `league_caitlyn_w_land`（不跟随，z −1） | 16 × 10 |
| `caitlyn_fx_w_trap` | view_effects `league_caitlyn_w_trap`（不跟随，z −1，每 0.25 秒重播） | 16 × 10 |
| `caitlyn_fx_w_fade` | view_effects `league_caitlyn_w_fade`（不跟随，z −1） | 16 × 10 |
| `caitlyn_fx_w_snap` | view_effects `league_caitlyn_w_snap`（跟随） | 18 × 12 |
| `caitlyn_fx_r_mark` | view_buffs `league_caitlyn_r_mark` | 24 × 24 |
| `caitlyn_fx_e_slow` | view_buffs `league_caitlyn_e_slow` | 16 × 8 |

- 枪口火光只在枪口不动的帧里烧（挂在她身上的 CasterViewEffect 只跟着她转身，不跟着精灵图里的枪走）：按动作条出手帧和下一帧的枪口位置放，枪一动就只留烟。
- 子弹、Q 能量弹、R 子弹、绳网的出手点按出手帧的枪口量，写进各自的 `y_offset`（只抬画面）；前几 tick 空着（从站位点飞到枪口的时间）。
- 夹子埋伏图每 15 tick 重播一次（两帧各 7–8 tick）；夹住目标的那张跟着目标，演 75 tick（1.25 秒）；绳网罩人的那张 60 tick（1 秒）。
