# 痛苦之拥 伊芙琳：给 Codex 的特效提示词（第 3 步）

> **这一份是 31 张特效图。** 造型已定（`design/evelynn_design.png`，8 倍，41 行）。
> - 大小对照 `design/evelynn_size.png`：定稿造型放大 4 倍，鞋底在红色脚底线上，上面是 10 格一段的刻度，右边是原版舞娘。伊芙琳 36×41 格。每条写的大小都是游戏像素（格）。
> - `design/evelynn_shots.png`：Q、W 出手那一帧、强化鞭笞起跳和大招斩击那一帧的定稿动作（4 倍），青色十字是手或脚下的位置（导入时 Claude 把特效放到这里）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里伊芙琳自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行（普攻和 E、Q、W、魅影、R），只在本地用，不要提交。颜色和英雄联盟一样：**Q 是品红粉色的水晶尖刺配紫色光带；W 是粉色的心；E 是紫色的鞭痕；R 是粉色的交叉大斩痕和紫黑色的烟；魅影是暗紫色的烟**。
> - **特效要亮**：魔腾的特效画成了最深的几档颜色，叠在人身上看不见。每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见；烟也要有亮紫色的边。
> - **心形只用在不会转向的画面上**（头顶的印记、魅惑、命中）；飞行物和朝向的画面上下要对称（游戏往左时会把它们上下翻转，倒过来的心很怪）。
> - 特效照下面第 1–31 条和「所有特效图的规则」画，每张一个 PNG，文件名 `evelynn_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小（交付里有 `manifest.json` 写明每帧区域 `assets[].frames[].rect` = [x, y, 宽, 高] 时按它切）。但每张请保持等宽的格子，不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`evelynn_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + E「鞭笞」 | 爪击普攻；每 8 秒普攻变成鞭打（按最大生命的伤害 + 加速）；刚出魅影时变成冲刺鞭打，打穿沿途 | `evelynn_fx_a_hit` · `evelynn_fx_e_hit` · `evelynn_fx_e2_trail` · `evelynn_fx_e2_hit` · `evelynn_fx_e_emp` · `evelynn_fx_e_haste` |
| 技能 1 = Q「憎恨之刺」 | 甩出鞭子打第一个敌人并标记（她接下来 3 次普攻多一段伤害），随后自动射出 3 根尖刺 | `evelynn_fx_q_cast` · `evelynn_fx_q_lash` · `evelynn_fx_q_spike` · `evelynn_fx_q_hit` · `evelynn_fx_q_mark` · `evelynn_fx_qb_hit` · `evelynn_fx_sp_cast` · `evelynn_fx_sp_hit` |
| 技能 2 = W「引诱」 | 飞吻给敌人挂上印记，2.5 秒后成熟，她下一击魅惑目标并削魔抗 | `evelynn_fx_w_cast` · `evelynn_fx_w_bolt` · `evelynn_fx_w_hit` · `evelynn_fx_w_mark` · `evelynn_fx_w_ripen` · `evelynn_fx_w_ripe` · `evelynn_fx_w_pop` · `evelynn_fx_w_charmed` · `evelynn_fx_w_shred` |
| 被动「恶魔魅影」 | 4 秒不出手进入魅影：回血、5 级起隐身 | `evelynn_fx_sh_in` · `evelynn_fx_sh_loop` · `evelynn_fx_sh_out` |
| 大招 = R「最终抚慰」 | 恶魔爆发，前方扇形大斩击（打中英雄越多次伤害越高），不可选中并往后闪 | `evelynn_fx_r_cast` · `evelynn_fx_r_slash` · `evelynn_fx_r_hit` · `evelynn_fx_r_blink` · `evelynn_fx_r_land` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、烟、拖尾、星点都没有黑描边，也不要用最深的颜色给形状描一圈边**（特效和角色相反）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 粉色（心、尖刺、斩击）：`#FFFFFF`、`#FFE0F0`、`#FF9ACA`、`#F05AA0`、`#C0306A`、`#6E1240`；
  - 紫色（鞭子的光、光带、光环）：`#FFFFFF`、`#F4DEFF`、`#D2A4FF`、`#A468F0`、`#7034C8`、`#3A1A70`；
  - 烟（魅影、大招）：`#D2A4FF`、`#A468F0`、`#7A34D2`、`#4A1C96`、`#2A0E5C`；
- **飞行物朝右画，而且上下对称**（`q_lash`、`q_spike`、`w_bolt`、`r_slash`）：游戏会把它转到出招方向，朝左时整张会上下翻转。
- **从手上发出的特效朝右画，起点在格子左边的中点**（`q_cast`、`w_cast`、`e2_trail`）；画在伊芙琳身上的画面（`r_cast`、`r_blink`、`r_land`、魅影三张）按每条写的站位画，脚在格子底部往上 8 格的中间。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。挂在人身上或头顶上的循环画面（`q_mark`、`w_mark`、`w_ripe`、`w_charmed`、`w_shred`、`e_emp`、`e_haste`、魅影）左右对称或不分左右，因为人朝左朝右都用同一张。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（31 张）

31 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：Q 尖刺宽 7000、大招扇形半径 45000）。

### 1. `evelynn_fx_a_hit.png`：普攻打中（目标身上），4 帧

普攻的爪击打中：三道粉白色的爪痕斜着划过，一下紫色闪光，几颗粉色火星往外飞（参考 BasicAttack_tar、Q_Whip_Flashcap）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a CLAW HIT, 4 frames: 1 a white flash; 2 three parallel pink-white claw slashes 12 squares long cutting down from upper left to lower right, a violet glow behind them; 3 the slashes thinning, 4 pink sparks flying out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `evelynn_fx_e_hit.png`：E「鞭笞」打中（目标身上），5 帧

鞭子抽中：一道弯弯的紫色鞭痕从上往下甩过，末端一下粉色的心形闪光，鞭痕旁边几颗紫色火星（参考 E_HitEffect_2 的心形、Q_Mis_Ribbon、darksov_force 的弯月）。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70) and a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a WHIP CRACK, 5 frames: 1 a thin bright violet arc appears at the upper left; 2 the arc sweeps down to the lower right as a curved whip mark 16 squares long with a white core; 3 a pink heart-shaped flash 6 squares across bursts where the whip ends, violet sparks; 4 the whip mark fades, the heart breaks into pink sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `evelynn_fx_e2_trail.png`：强化鞭笞的冲刺拖尾（地上，留在原地），5 帧

出魅影后的第一鞭：她扑向目标，身后留下一道往右拉长的紫黑色烟带，边上亮紫色，几片粉色碎光（参考 R_MeshSwipe、Q_Tunnel_Smoke、R_Swipe_Curls）。朝右画：起点在格子左边中点。约 48 格长、12 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a smoke ramp (#D2A4FF, #A468F0, #7A34D2, #4A1C96, #2A0E5C) and a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a DASH TRAIL along the ground, pointing RIGHT, 5 frames: 1 a burst of violet smoke at the LEFT MIDDLE of the cell (where she leaps); 2 a long streak of violet-black smoke with bright violet edges stretches to the right edge of the cell, 8 squares thick, pink sparks along it; 3 the streak at full length; 4 it thins and breaks into wisps; 5 fading wisps.
Layout: one horizontal row of 5 equal 4:1 cells, image size 2560x128 (each cell 512x128); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `evelynn_fx_e2_hit.png`：强化鞭笞冲到目标的一击（目标身上），5 帧

冲刺到目标身上那一下：比普通鞭笞大的紫粉色爆开，中间白色闪光，一圈粉色的鞭痕和火星往外甩（参考 R_Crit 的粉色交叉、Q_Whip_Flashcap）。约 22 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70) and a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a POUNCE BURST, 5 frames: 1 a white flash; 2 two crossing pink-white slashes (an X 18 squares across) over a violet burst; 3 the X at full size, a ring of pink sparks flying out; 4 the slashes fading into violet wisps; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `evelynn_fx_e_emp.png`：强化鞭笞就绪（她身上循环，到下一鞭为止），4 帧

出魅影后，下一鞭会冲刺：她腰后的鞭子根部一圈紫色的光点慢慢往上飘（参考 E_SoulWispsAlpha2、Z_SPark_012）。左右对称或不分左右。约 24 格宽、20 格高，光点在格子下半部分（她的腰到膝盖）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a READY GLOW around a body, 4 frames, a seamless loop, left-right symmetric: 6 small bright violet sparks (2x2 squares with a white core) drifting upward in a loose ring around the lower half of the cell, two faint violet wisps rising between them; leave the middle of the cell empty (the body is there).
Layout: one horizontal row of 4 equal 6:5 cells, image size 1536x320 (each cell 384x320); the ring's middle at the cell's middle, 2/3 down. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `evelynn_fx_e_haste.png`：鞭笞的加速（脚下循环，2 秒），4 帧

鞭笞后她加速：脚下两三道紫色的速度线和几缕淡紫色的烟往后飘（参考 P_Stealth_Ribbon）。左右对称或不分左右（朝左不镜像）。约 24 格宽、6 格高，贴着地面。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: SPEED WISPS at the feet, 4 frames, a seamless loop: 3 short horizontal violet light streaks (6-10 squares long, 1 square thick) and 2 faint wisps sliding along the ground, left-right symmetric overall, a flat oval 24 squares wide and 6 tall.
Layout: one horizontal row of 4 equal 4:1 cells, image size 1536x96 (each cell 384x96); on the cell's middle line. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `evelynn_fx_q_cast.png`：Q 出手：手前面的紫粉色闪光（施法者身上），4 帧

她甩出鞭子的那只手前面一团紫粉色的光炸开，两三道尖刺状的光往右刺出去（参考 Q_Rdy、Q_Sharp、Q_Whip_Flashcap）。朝右画：手在格子左边中点。约 14 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a CAST FLASH at a hand, pointing RIGHT, 4 frames: 1 a pink-white star at the LEFT MIDDLE of the cell (the hand); 2 three sharp pink spikes of light shoot out to the right from that point over a violet burst; 3 the spikes thin, 4 sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal 7:5 cells, image size 1120x200 (each cell 280x200); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `evelynn_fx_q_lash.png`：Q 飞出去的鞭子（飞行中循环），4 帧

Q 的第一下：一道带尖刺的紫粉色鞭头往右飞，后面拖一小段紫色的彩带光（参考 Q_Hatespike_ModelTexture、Q_Mis_Ribbon、Q_Streaks）。上下对称（往左飞时游戏会把整张上下翻转）。约 18 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a FLYING THORNED LASH moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a sharp magenta-pink crystal spike head 6 squares long with a white core at the RIGHT end, small thorns above and below it; behind it to the LEFT a violet ribbon of light 12 squares long, rippling slightly from frame to frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the head at the RIGHT half, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `evelynn_fx_q_spike.png`：Q 自动射出的尖刺（飞行中循环），3 帧

Q 之后自动射出的三根尖刺：一串粉色水晶尖刺往右飞，像一排刺从紫色光里冒出来（参考 Q_Hatespike_ModelTexture 的粉色尖刺、Q_Streaks、Q_Veins）。上下对称。约 20 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a FLYING LINE OF SPIKES moving to the RIGHT, 3 frames, a seamless loop, SYMMETRIC above and below the middle line: three magenta-pink crystal spikes in a row, the front one biggest (5 squares) with a white tip at the RIGHT end, growing out of a violet streak 20 squares long; the spikes flicker in size from frame to frame.
Layout: one horizontal row of 3 equal 2:1 cells, image size 1536x256 (each cell 512x256); the front spike at the RIGHT end, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `evelynn_fx_q_hit.png`：Q 鞭子打中（目标身上），4 帧

鞭子打中：一下粉色的尖刺炸开，几根尖刺从中间往外刺出，紫色的光一闪（参考 Q_Hatespike、Q_CoreGlow、Mark_RGBA）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a SPIKE BURST, 4 frames: 1 a white flash; 2 five sharp pink crystal spikes (2-5 squares long) burst outward from the middle over a violet glow; 3 the spikes at full length, sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `evelynn_fx_q_mark.png`：Q 标记（目标头顶，循环 5 秒）：她接下来 3 次普攻多一段伤害，4 帧

被鞭子打中的目标头顶上方一圈紫粉色的小尖刺，像荆棘做的小冠，慢慢闪（参考 Q_Rdy、Q_Shred_shield）。左右对称。约 10 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a SMALL THORN CROWN floating over a head, 4 frames, a seamless loop, left-right symmetric: a ring of 5 small pink crystal thorns (2-3 squares each) with a faint violet glow between them, 10 squares wide, pulsing brighter and dimmer.
Layout: one horizontal row of 4 equal 5:3 cells, image size 1280x192 (each cell 320x192); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `evelynn_fx_qb_hit.png`：Q 标记的追加伤害（目标身上），3 帧

带标记的普攻打中：荆棘小冠上的一根刺弹出来、碎成粉色的光点（参考 Mark_RGBA、R_Sparks）。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a THORN POP, 3 frames: 1 a pink crystal thorn 4 squares long flashes white; 2 it shatters into 5 pink shards flying out; 3 fading shards.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `evelynn_fx_sp_cast.png`：自动尖刺射出时她身上的一闪（施法者身上），3 帧

每根尖刺射出时她身上一下粉紫色的光点炸开（参考 Q_Orbs_MissileFront、Z_SPark_012）。不分左右。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a SMALL BURST, 3 frames: 1 a pink-white spark 4 squares across; 2 a ring of 6 small pink and violet sparks flying out; 3 fading sparks. Left-right symmetric.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `evelynn_fx_sp_hit.png`：尖刺打中（目标身上），3 帧

尖刺扎中：一根粉色的刺扎进去，周围一圈小火星（参考 Q_Hatespike）。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a SPIKE STAB, 3 frames: 1 a pink crystal spike 6 squares long stabs in from the left with a white flash at its tip; 2 the spike breaks into 4 pink shards; 3 fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `evelynn_fx_w_cast.png`：W 出手：飞吻放出诅咒（施法者身上），4 帧

她飞吻放出诅咒：手前面冒出一颗小小的粉色爱心和几颗星点，往右飘出去（参考 W_Heart_Glow、Taunt_Half_heart）。朝右画：手在格子左边中点。约 14 格宽、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a BLOWN KISS from a hand, pointing RIGHT, 4 frames: 1 a pink-white spark at the LEFT MIDDLE of the cell (the hand); 2 a small bright pink heart (5 squares wide) pops out of it with 3 sparkles; 3 the heart drifts to the right, bigger; 4 the heart fades into sparkles.
Layout: one horizontal row of 4 equal 7:5 cells, image size 1120x200 (each cell 280x200); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `evelynn_fx_w_bolt.png`：W 飞向目标的诅咒（飞行中循环），4 帧

诅咒飞向目标：一颗粉色发光的四角星芯，后面拖一条紫粉色的彩带，彩带里有几颗小心形碎片（参考 W_Heart_Tendril_Fill、Q_Mis_Ribbon）。上下对称（不要画整颗爱心，往左飞会倒过来）。约 14 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a FLYING CURSE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a bright pink four-pointed star core 5 squares across with a white center at the RIGHT end, a pink-violet ribbon trailing 10 squares to the LEFT with tiny pink sparkles in it.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the core at the RIGHT half, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `evelynn_fx_w_hit.png`：W 印记落在目标身上，4 帧

诅咒落到目标身上：一圈粉色的光环从外往里收紧，收成目标头顶的半颗心（参考 W_mark_activate_ring、W_Ground_Ring）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a CURSE LANDING, 4 frames: 1 a thin pink ring 16 squares across; 2 the ring shrinks to 10 squares, sparkles; 3 it shrinks to a small pink spark at the upper middle of the cell; 4 a fading spark.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `evelynn_fx_w_mark.png`：W 印记（目标头顶，循环，前 2.5 秒）：半颗心，4 帧

被诅咒的目标头顶上方一颗只有轮廓、慢慢被填满的暗粉色心：前 2.5 秒是暗的、空心的（参考 W_Heart_Piece、W_Heart_Tendril_Fill）。左右对称。约 10 格宽、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a DIM HEART MARK floating over a head, 4 frames, a seamless loop, left-right symmetric: the outline of a heart 10 squares wide drawn in mid pink (no white), its inside empty, a soft pink glow pulsing slowly.
Layout: one horizontal row of 4 equal 10:9 cells, image size 1280x288 (each cell 320x288); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `evelynn_fx_w_ripen.png`：W 印记成熟（2.5 秒时一闪），4 帧

2.5 秒到：头顶的心被填满，一下亮粉白色的闪光（参考 W_Heart_Shine、W_spark）。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a HEART FILLING, 4 frames: 1 a heart outline 10 squares wide fills with bright pink from the bottom up; 2 full, a white flash and a ring of sparkles; 3 the flash fading; 4 the full heart alone, glowing.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the heart in the upper middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `evelynn_fx_w_ripe.png`：W 印记已成熟（目标头顶，循环）：亮粉色的心，4 帧

成熟后的印记：头顶一颗实心的亮粉色心，一跳一跳地发光，周围几颗小星点（参考 W_Heart_Glow）。左右对称。约 10 格宽、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a BRIGHT HEART MARK floating over a head, 4 frames, a seamless loop, left-right symmetric: a solid bright pink heart 10 squares wide with a white highlight, beating (a little bigger in frame 2), 2-3 sparkles around it.
Layout: one horizontal row of 4 equal 10:9 cells, image size 1280x288 (each cell 320x288); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `evelynn_fx_w_pop.png`：W 魅惑触发：心碎开（目标身上），5 帧

她打中成熟的目标：头顶的心炸开成粉色的碎片和小心，一圈粉色冲击光环（参考 Taunt_Half_heart 碎片、W_mark_activate_ring、E_HitEffect_2）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: a HEART BURST, 5 frames: 1 a bright pink heart 10 squares wide at the middle, a white flash; 2 the heart cracks and bursts into 6 pink heart-shaped shards flying out, a thin pink ring 14 squares across; 3 shards further out, the ring 20 squares; 4 the shards fading; 5 a few sparkles.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `evelynn_fx_w_charmed.png`：被魅惑（目标头顶，魅惑持续时间里循环）：转圈的小心，6 帧

被魅惑的目标头顶上方三颗小粉心绕着转圈（像眩晕的星星，但是心），整段魅惑时间都在（参考 P_charm_dots、W_Heart_Glow）。左右对称。约 14 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: THREE SMALL HEARTS CIRCLING over a head, 6 frames, a seamless loop: three bright pink hearts (3 squares wide each, a white highlight) moving round a flat ellipse 14 squares wide and 4 tall, the one in front bigger and brighter, the one behind smaller and dimmer.
Layout: one horizontal row of 6 equal 7:3 cells, image size 1680x120 (each cell 280x120); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `evelynn_fx_w_shred.png`：魔抗被削（目标脚下，循环 4 秒），4 帧

魅惑同时削掉魔抗：目标脚下一圈裂开的粉紫色符文环，慢慢闪（参考 W_Ground_Ring_RGBA、R_Mark_activate_ring）。不分左右。约 16 格宽、6 格高（从斜上方看的椭圆）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a CRACKED RUNE RING on the ground, 4 frames, a seamless loop: a flat ellipse 16 squares wide and 6 tall drawn as a broken pink-violet ring (4 arcs with gaps), small cracks of light across it, pulsing dim and bright.
Layout: one horizontal row of 4 equal 8:3 cells, image size 1280x120 (each cell 320x120); the ellipse on the cell's middle line. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `evelynn_fx_sh_in.png`：被动「恶魔魅影」：进入魅影（她身上），5 帧

4 秒没出手进入魅影：一圈暗紫色的烟从地面卷起，把她包住，烟的边上是亮紫色（参考 demonshade_TX、P_Stealth_Ribbon、Tendrils_Smoke）。左右对称或不分左右。约 36 格宽、40 格高，格子中间留出人形，不要画人。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a smoke ramp (#D2A4FF, #A468F0, #7A34D2, #4A1C96, #2A0E5C).
Effect: a SHADOW GATHERING around a standing figure, 5 frames: 1 a flat ring of dark violet smoke at the bottom of the cell; 2 wisps curl up both sides; 3 the wisps reach shoulder height, a thin veil of violet smoke around the figure's outline; 4 the veil closes into a loose shroud of wisps 36 squares wide; 5 settled - the same shroud as the loop's first frame. Leave the middle of the cell (the figure, about 24 squares wide and 40 tall) mostly empty; the smoke has bright violet edges and darker violet middles, no black.
Layout: one horizontal row of 5 equal 9:10 cells, image size 1440x320 (each cell 288x320); the figure's feet at the bottom middle of every cell, 8 squares above the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 25. `evelynn_fx_sh_loop.png`：魅影中（她身上循环），6 帧

魅影里：那层烟绕着她慢慢转，几缕往上飘、几颗紫色光点闪（和 sh_in 最后一帧接上）。约 36 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a smoke ramp (#D2A4FF, #A468F0, #7A34D2, #4A1C96, #2A0E5C).
Effect: a SHADOW SHROUD around a standing figure, 6 frames, a seamless loop: the loose shroud of violet wisps from the previous sheet's last frame, the wisps slowly turning and rising, 3 small violet sparks blinking; the middle of the cell mostly empty.
Layout: one horizontal row of 6 equal 9:10 cells, image size 1728x320 (each cell 288x320); the figure's feet at the bottom middle, 8 squares above the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 26. `evelynn_fx_sh_out.png`：离开魅影（她身上），4 帧

她一出手就现形：烟往外散开、消失（和 sh_loop 接上）。约 36 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a smoke ramp (#D2A4FF, #A468F0, #7A34D2, #4A1C96, #2A0E5C).
Effect: a SHADOW DISPERSING, 4 frames: 1 the shroud; 2 it blows outward into separate wisps; 3 wisps further out, thinning; 4 a few fading wisps at the edges.
Layout: one horizontal row of 4 equal 9:10 cells, image size 1152x320 (each cell 288x320); the figure's feet at the bottom middle, 8 squares above the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 27. `evelynn_fx_r_cast.png`：R 出手：恶魔的爆发（施法者身上），5 帧

大招起手：她身上爆出一团品红紫色的恶魔光，背后两条鞭子的影子张开，周围紫黑色的烟（参考 R_Arrival、R_Flash_sharp、R_Flames、R_Land_Smoke）。约 40 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240), a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70) and a smoke ramp (#D2A4FF, #A468F0, #7A34D2, #4A1C96, #2A0E5C).
Effect: a DEMONIC BURST around a standing figure, 5 frames: 1 a magenta-white flash at the figure's chest (the middle of the cell, 2/3 down); 2 a burst of magenta-violet light 30 squares across, violet smoke curling up both sides; 3 two shadowy wings of violet smoke spread behind (left and right), the light at full size; 4 the light fading, the smoke rising; 5 fading wisps.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320); the figure's feet at the bottom middle, 8 squares above the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 28. `evelynn_fx_r_slash.png`：R 扇形斩：往前扫出的粉色大斩击（朝右，不循环），6 帧

最终抚慰的斩击：她前面扫出两道交叉的粉色大斩痕，像一把打开的扇子往右展开，扇面里是紫粉色的光，边上几道细的爪痕（参考 R_Crit 的粉色 X、R_slash、R_MeshSwipe、R_Scratch）。朝右画，上下对称（往左时游戏会上下翻转）。约 56 格长、40 格高，起点在格子左边中点。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a WIDE FAN SLASH pointing RIGHT, 6 frames, not looping, SYMMETRIC above and below the middle line: 1 a white spark at the LEFT MIDDLE of the cell; 2 two crossing pink-white slash arcs sweep out to the right, opening like a fan of 100 degrees; 3 the fan at full size (56 squares long, 40 tall), a magenta-violet glow inside it, 4 thin claw scratches along its edge; 4 the slashes thinning; 5 breaking into pink sparks; 6 empty (the slash gone).
Layout: one horizontal row of 6 equal 7:5 cells, image size 2688x320 (each cell 448x320); the start point at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 29. `evelynn_fx_r_hit.png`：R 打中（目标身上），4 帧

大招打中：一个粉色的 X 斩痕，中间白色闪光，碎成粉紫色的光点（参考 R_Crit、R_Flash_sharp）。约 20 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a BIG X SLASH, 4 frames: 1 a white flash; 2 a bright pink X 18 squares across with a white core over a violet burst; 3 the X breaking into pink and violet sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 30. `evelynn_fx_r_blink.png`：R 往后闪：原地留下的影子（地上，不跟随），5 帧

她往后闪走的地方：留下一团紫黑色的人形烟影，马上散开成几缕烟和紫色碎光（参考 R_Land_Smoke、P_Stealth_Int、Tendrils_Smoke）。约 28 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a smoke ramp (#D2A4FF, #A468F0, #7A34D2, #4A1C96, #2A0E5C) and a violet ramp (#FFFFFF, #F4DEFF, #D2A4FF, #A468F0, #7034C8, #3A1A70).
Effect: a SHADOW AFTERIMAGE breaking up, 5 frames: 1 a standing smoke silhouette (a slim figure 14 squares wide, 34 tall) of dark violet smoke with bright violet edges; 2 it starts to blow apart from the top; 3 half of it is wisps; 4 only wisps and sparks; 5 fading wisps.
Layout: one horizontal row of 5 equal 7:9 cells, image size 1120x288 (each cell 224x288); the figure's feet at the bottom middle, 8 squares above the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 31. `evelynn_fx_r_land.png`：R 闪到的地方：重新出现（她身上，不跟随），4 帧

她在后面重新出现：一圈紫色的烟从脚下炸开，几颗粉色火星（参考 R_Land_Smoke、R_Reset_Ground）。不分左右。约 28 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, glows, smoke, trails or sparks, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield; the smoke keeps lit violet edges), colours only from a smoke ramp (#D2A4FF, #A468F0, #7A34D2, #4A1C96, #2A0E5C) and a pink ramp (#FFFFFF, #FFE0F0, #FF9ACA, #F05AA0, #C0306A, #6E1240).
Effect: an ARRIVAL PUFF, 4 frames: 1 a violet flash at the feet; 2 a ring of violet smoke bursts outward along the ground (a flat ellipse 28 squares wide), pink sparks rising; 3 the smoke ring wider and thinner; 4 fading wisps.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the feet at the bottom middle, 8 squares above the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `evelynn_fx_a_hit` | view_effects `league_evelynn_a_hit`（跟随，画在人物上面） | 14 |
| `evelynn_fx_e_hit` | view_effects `league_evelynn_e_hit`（跟随，画在人物上面） | 18 |
| `evelynn_fx_e2_trail` | view_effects `league_evelynn_e2_trail`（施法者身上，不跟随，朝左时镜像；格子左边中点放在她起跳的位置） | 48 × 12 |
| `evelynn_fx_e2_hit` | view_effects `league_evelynn_e2_hit`（跟随，画在人物上面） | 22 |
| `evelynn_fx_e_emp` | view_buffs `league_evelynn_e_emp`（画在她身上，跟着走，朝左不镜像） | 24 × 20 |
| `evelynn_fx_e_haste` | view_buffs `league_evelynn_e_haste`（画在脚下，跟着走） | 24 × 6 |
| `evelynn_fx_q_cast` | view_effects `league_evelynn_q_cast`（施法者身上，不跟随，朝左时镜像；格子左边中点放到 Q 第 3 帧的手） | 14 × 10 |
| `evelynn_fx_q_lash` | view_projectiles `league_evelynn_q_lash`（朝右，游戏转到飞行方向，上下对称） | 18 × 8 |
| `evelynn_fx_q_spike` | view_projectiles `league_evelynn_q_spike`（朝右，游戏转到飞行方向，上下对称） | 20 × 8 |
| `evelynn_fx_q_hit` | view_effects `league_evelynn_q_hit`（跟随，画在人物上面） | 14 |
| `evelynn_fx_q_mark` | view_buffs `league_evelynn_q_mark`（画在目标头顶上方，跟着走） | 10 × 6 |
| `evelynn_fx_qb_hit` | view_effects `league_evelynn_qb_hit`（跟随，画在人物上面） | 10 |
| `evelynn_fx_sp_cast` | view_effects `league_evelynn_sp_cast`（施法者身上，不跟随） | 12 |
| `evelynn_fx_sp_hit` | view_effects `league_evelynn_sp_hit`（跟随，画在人物上面） | 10 |
| `evelynn_fx_w_cast` | view_effects `league_evelynn_w_cast`（施法者身上，不跟随，朝左时镜像；格子左边中点放到 W 第 2 帧的手） | 14 × 10 |
| `evelynn_fx_w_bolt` | view_projectiles `league_evelynn_w_bolt`（朝右，游戏转到飞行方向，上下对称） | 14 × 8 |
| `evelynn_fx_w_hit` | view_effects `league_evelynn_w_hit`（跟随，画在人物上面） | 16 |
| `evelynn_fx_w_mark` | view_buffs `league_evelynn_w_mark`（画在目标头顶上方，跟着走） | 10 × 9 |
| `evelynn_fx_w_ripen` | view_effects `league_evelynn_w_ripen`（跟随，画在目标头顶） | 14 |
| `evelynn_fx_w_ripe` | view_buffs `league_evelynn_w_ripe`（画在目标头顶上方，跟着走） | 10 × 9 |
| `evelynn_fx_w_pop` | view_effects `league_evelynn_w_pop`（跟随，画在人物上面） | 20 |
| `evelynn_fx_w_charmed` | view_buffs `league_evelynn_w_charmed`（画在目标头顶上方，跟着走） | 14 × 6 |
| `evelynn_fx_w_shred` | view_buffs `league_evelynn_w_shred`（画在脚下，跟着走） | 16 × 6 |
| `evelynn_fx_sh_in` | view_buffs `league_evelynn_shade`（ThreePhase 的 pre_tag，画在她身上，z 在人物后面） | 36 × 40 |
| `evelynn_fx_sh_loop` | view_buffs `league_evelynn_shade`（ThreePhase 的 loop_tag） | 36 × 40 |
| `evelynn_fx_sh_out` | view_buffs `league_evelynn_shade`（ThreePhase 的 remove_tag） | 36 × 40 |
| `evelynn_fx_r_cast` | view_effects `league_evelynn_r_cast`（施法者身上，不跟随；脚在格子底部往上 8 格的中间） | 40 × 40 |
| `evelynn_fx_r_slash` | view_projectiles `league_evelynn_r_slash`（朝右，游戏转到目标方向，上下对称） | 56 × 40 |
| `evelynn_fx_r_hit` | view_effects `league_evelynn_r_hit`（跟随，画在人物上面） | 20 |
| `evelynn_fx_r_blink` | view_effects `league_evelynn_r_blink`（施法者身上，不跟随；脚在格子底部往上 8 格的中间） | 28 × 36 |
| `evelynn_fx_r_land` | view_effects `league_evelynn_r_land`（施法者身上，不跟随；脚在格子底部往上 8 格的中间） | 28 × 28 |

- 施法者身上的画面（`q_cast`、`w_cast` 在手上；`e2_trail`、`r_cast`、`r_blink`、`r_land` 在脚下）：按 `design/evelynn_shots.png` 的十字把格子的起点挪过去；晚于第一 tick 播放的 `is_follow` 为 false（红方方向）。
- 飞行物（`q_lash`、`q_spike`、`w_bolt`）第一帧前加一个空帧（出生那一 tick 画面朝上，`import_lucian.py` 的 `RAY_SKIP`）；`r_slash` 不循环，最后一帧空。
- `sh_in`/`sh_loop`/`sh_out` 合成一个 ThreePhase（`league_evelynn_shade`）；`w_charmed` 循环到魅惑结束（buff 的时长），`w_shred` 循环 4 秒。
- 清掉 Codex 给光和烟描的最深色边（`import_riven.py` 的 `unrim` 做法）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比（魔腾的教训）；Codex 交的如果是要求尺寸的 2 倍（娑娜那次），缩一半。
