# 逆羽 霞：给 Codex 的特效提示词（第 3 步）

> **这一份是 21 张特效图。** 造型和动作已定（`design/xayah_design.png`，8 倍，44 行）。
> - 大小对照 `design/xayah_size.png`：定稿造型放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版弓箭手。霞 34×44 格。每条写的大小都是游戏像素（格）。
> - `design/xayah_shots.png`：普攻出手、Q 出手、E、W、R 出手、待机的定稿动作（4 倍），青色十字是手（或胸口）的位置，导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里霞自己的特效贴图（很多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟：**羽刃和羽毛是品红粉色（白色刃边、紫色羽轴），禁锢和匕首雨的冲击是深红色，斗篷羽毛溅出的火花是金橙色**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **套在人身上、脚下的光只画边，中间留出人形的空位**，不然会把人整个挡住。
> - 特效照下面第 1–21 条和「所有特效图的规则」画，每张一个 PNG，文件名 `xayah_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准）。
> - 生图原稿（半透明边、格子比例不准）也可以交：Claude 会转成原尺寸条，再按技能范围定大小。但每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），**最后写**。最好打成一个 zip（`xayah_fx_done.zip`）放在 outputs 里。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「锐切」 | 甩出羽刃；放技能后 3 次普攻变成穿透的强化羽刃，在目标身后留下一根插在地上的羽毛 | `xayah_fx_a_blade` · `xayah_fx_a_pierce` · `xayah_fx_a_hit` · `xayah_fx_p_on` · `xayah_fx_f_drop` · `xayah_fx_f_lie` |
| 技能 1 = Q「双刃」→ E「倒钩」 | 扔出两把穿透匕首，各留一根羽毛；约 1 秒后自动收回场上所有羽毛，路过的敌人受伤，一次收回第 3 次命中英雄起禁锢 | `xayah_fx_q_dagger` · `xayah_fx_q_flash` · `xayah_fx_q_hit` · `xayah_fx_e_cast` · `xayah_fx_feather` · `xayah_fx_e_hit` · `xayah_fx_e_root` · `xayah_fx_e_bind` |
| 技能 2 = W「致死羽衣」 | 4 秒攻速大增，每次普攻多甩出一片羽刃，命中英雄加移速（洛在附近时他也获得） | `xayah_fx_w_cast` · `xayah_fx_w_on` · `xayah_fx_w_flash` · `xayah_fx_w_ms`（第二片羽刃用 `a_blade`） |
| 大招 = R「暴风羽刃」 | 腾空，短时间内不受伤害和控制，然后向前方扇形降下匕首雨，留下一排羽毛并随即收回 | `xayah_fx_r_cast` · `xayah_fx_r_rain` · `xayah_fx_r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、风、火花、拖尾没有黑描边，也不要用最深的颜色给形状描一圈边**。只有实心的物体（羽刃、匕首、插在地上的羽毛）有 1 格深色描边（`#0B040E`）。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀。
- 颜色（按每条写的用）：
  - 品红（羽刃、羽毛、命中）：`#FFFFFF`、`#FFD6F2`、`#FF7AD8`、`#F02D9C`、`#C0207A`、`#7A1450`；
  - 紫色（羽轴、被动、W 的风暴）：`#FFFFFF`、`#ECD8FF`、`#B87AF0`、`#8A3CD8`、`#5A1FA0`、`#2A1050`；
  - 深红（禁锢、匕首雨的冲击）：`#FFE6E6`、`#FF8A9A`、`#F02D50`、`#B0123A`、`#600A24`；
  - 金橙（斗篷羽毛的火花）：`#FFF4C8`、`#FCC24F`、`#F08122`、`#B84313`；
- **飞行物朝右画，而且上下对称**（`a_blade`、`a_pierce`、`feather`、`q_dagger`）：游戏会把它转到出手方向，朝左时整张会上下翻转。
- **匕首雨 `r_rain` 是地面区域，也会跟着方向翻转**：朝右画、扇形的尖在格子左边中点、**上下对称**。
- **插在地上的羽毛（`f_drop`、`f_lie`）竖直插地、左右对称**：地上的图不会随方向翻转，斜着画的话红方会朝错方向。
- 从手上发出的特效朝右画，起点在格子左边的中点（`q_flash`）；画在她身上、脚下的画面（`e_cast`、`w_cast`、`w_on`、`w_ms`、`r_cast`、`p_on`、`w_flash`）**左右对称**，因为人朝左朝右都用同一张。
- 命中、爆发居中画，不旋转；地面上的圆是从斜上方看的椭圆（宽是高的 2 倍左右）。
- 套在角色身上的特效：格子里留出空的人形位置，不要画人。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（21 张）

21 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：匕首雨扇形长 90000、宽 40000，禁锢只在脚下）。

### 1. `xayah_fx_a_blade.png`：普攻甩出的羽刃（飞行中循环），4 帧

普攻甩出的一片羽刃：细长的品红色锋利羽毛，中间一道紫色羽轴，刃边发白，后面拖一小段粉色光尾（参考 Q_feather、BA_Mis3_trail）。羽刃是物体，有 1 格深色描边；光尾没有。**上下对称**。约 11 格长、4 格高（羽刃约 8 × 3 格）。W 的第二片羽刃也用这张。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a FLYING FEATHER BLADE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a slim sharp magenta feather 8 squares long and 3 tall, pointed at the RIGHT, a violet quill down its middle, white edges, a 1-square dark outline; a short pink light streak 3 squares long trailing behind it to the LEFT that flickers each frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 2048x256 (each cell 512x256); the blade's tip at the RIGHT half, on the middle line, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `xayah_fx_a_pierce.png`：被动强化普攻：穿透的羽刃（飞行中循环），4 帧

放技能后的 3 次强化普攻：比普通的更大更亮的羽刃，穿过沿途所有敌人，后面一道长长的品红光尾，两侧有几片小羽毛碎光（参考 Passive_SmokeTrail_sharp、Q_feather_glow_pierce）。约 16 格长、6 格高（羽刃约 10 × 4 格）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450), a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050) and a gold ramp (#FFF4C8, #FCC24F, #F08122, #B84313).
Effect: an EMPOWERED PIERCING BLADE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a big glowing magenta feather blade 10 squares long and 4 tall with a white-hot edge and a violet core, a 1-square dark outline; behind it to the LEFT a long bright pink streak 6 squares long with tiny gold sparks above and below it, flickering.
Layout: one horizontal row of 4 equal 8:3 cells, image size 2048x192 (each cell 512x192); the blade's tip at the right, on the middle line. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `xayah_fx_a_hit.png`：羽刃打中（目标身上），4 帧

羽刃打中：一下白色闪光，几道品红色的细线向外斜切（像被羽刃划过），几粒粉色碎光（参考 BA_Hit_flash、BA_tar_hitflash）。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a BLADE HIT, 4 frames: 1 a white flash; 2 two crossing magenta slash lines 10 squares long through the centre with a white middle, 4 pink sparks; 3 the slashes fading, sparks flying out; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `xayah_fx_p_on.png`：被动锐切就绪：手上的羽刃发亮（施法者身上），4 帧

放技能后接下来 3 次普攻变强：她手里的羽刃周围亮起一圈品红光，几片小羽毛光点绕着手转（参考 Passive_core_glow、Passive_Sparks）。约 10 格，居中画，**左右对称**（人朝左朝右都用这张）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: an EMPOWER GLOW round a hand (symmetric left and right), 4 frames: 1 a small white-pink spark at the centre; 2 a ring of magenta light 8 squares across with 4 tiny feather-shaped glints on it; 3 the glints turning a quarter round, the ring brighter; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `xayah_fx_f_drop.png`：羽毛落地：羽刃插进地面，3 帧

羽刃飞到尽头**竖直插进地面**：一下白色小闪光，羽毛落定，脚下一圈小粉色光点（参考 P_feather、P_feather_ground_glow）。**羽毛竖直插在地上、左右对称**（地上的图不会随方向翻转）。约 6 格宽、10 格高，插地点在格子底部中间。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a FEATHER BLADE STABBING INTO THE GROUND, 3 frames, symmetric left and right: 1 the blade (magenta, a violet quill, white edge, a 1-square dark outline, 3 squares wide and 8 tall, point DOWN) dropping in with a white flash at its point; 2 it stands upright stuck in the ground, a small flat ring of pink light on the ground round its foot (6 squares wide, 2 tall); 3 the ring fading, the blade standing.
Layout: one horizontal row of 3 equal 3:5 cells, image size 576x960 (each cell 192x320); the blade's point at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `xayah_fx_f_lie.png`：地上的羽毛（等待收回，循环），2 帧

插在地上等着被倒钩收回的羽刃：竖直插地，刃边微微闪光（两帧交替），脚下一点粉光。和 `f_drop` 第 3 帧同样大小同样位置。**左右对称**。约 5 格宽、9 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a FEATHER BLADE STUCK UPRIGHT IN THE GROUND, 2 frames, a loop, symmetric left and right: the same blade as a stuck feather (magenta, violet quill, white edge, dark outline, 3 squares wide and 8 tall, point down into the ground) with a faint pink glow at its foot; frame 2 the white edge glints one square higher.
Layout: one horizontal row of 2 equal 3:5 cells, image size 384x640 (each cell 192x320); the blade's point at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `xayah_fx_feather.png`：倒钩收回的羽毛（飞回霞身边，循环），4 帧

倒钩召回：地上的羽刃飞回霞的手里，路过的敌人被划伤。画成**朝右飞**的羽刃（和普攻羽刃一样的形状），后面拖一条更长的品红色光带（参考 E_feather_transition、E_trail）。约 13 格长、5 格高。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a RETURNING FEATHER BLADE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a magenta feather blade 8 squares long and 3 tall (violet quill, white edge, dark outline) pointing RIGHT, with a long bright magenta ribbon of light 5 squares long trailing to the LEFT that ripples each frame.
Layout: one horizontal row of 4 equal 5:2 cells, image size 2560x1024 (each cell 640x256); the blade's tip at the right, on the middle line. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `xayah_fx_q_dagger.png`：Q 双刃：飞出去的匕首（飞行中循环），4 帧

Q 扔出的匕首：比普攻羽刃更长更直的羽刃匕首，刃尖发白，后面拖一段品红火焰般的光尾（参考 Q_mis_FireTrail、Q_feather_glow、Q_mis_glowTrail）。约 14 格长、5 格高（匕首约 10 × 3 格）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450), a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050) and a gold ramp (#FFF4C8, #FCC24F, #F08122, #B84313).
Effect: a THROWN FEATHER DAGGER moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC above and below the middle line: a long straight magenta feather dagger 10 squares long and 3 tall (a violet quill, a white tip, a 1-square dark outline) pointing RIGHT; behind it to the LEFT a flickering pink-magenta flame trail 4 squares long with 2 gold sparks.
Layout: one horizontal row of 4 equal 5:2 cells, image size 2560x1024 (each cell 640x256); the dagger's tip at the right, on the middle line. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `xayah_fx_q_flash.png`：Q 出手：手上的闪光（施法者身上），3 帧

Q 扔出匕首的一瞬间：手边一下品红白色闪光，往右喷出两道细光（两把匕首）。朝右画：手在格子左边中点。约 12 格宽、8 格高，只 3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a THROW FLASH, pointing RIGHT, 3 frames: 1 a white-magenta star at the LEFT MIDDLE of the cell (the hand); 2 two short magenta light rays shooting right from that point, slightly spread; 3 the rays fading.
Layout: one horizontal row of 3 equal 3:2 cells, image size 720x480 (each cell 240x160); the start point at the left edge, halfway down. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `xayah_fx_q_hit.png`：Q 匕首打中（目标身上），4 帧

匕首打中：比普攻更大的品红斜划，加一圈白色冲击光（参考 Q_tar_glow、Q_tar_pulse）。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a DAGGER HIT, 4 frames: 1 a white flash; 2 a big magenta slash 12 squares long diagonally through the centre with a white core and a thin ring of pink light 10 squares across; 3 the ring expanding, the slash fading; 4 sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `xayah_fx_e_cast.png`：E 倒钩：召回羽毛（施法者身上），4 帧

倒钩施放的一瞬间：她身边一圈品红色的风，几片羽毛光影往她身上收拢（参考 E_Root_wind、E_wispy_smoke、E_feather_transition_mult）。约 24 格，居中画，**中间留出人形的空位，左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a FEATHER CALL round a figure (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames: 1 six small magenta feather glints far out on a ring 24 squares across; 2 the glints rushing inward along curved pink wind streaks; 3 they reach a ring 10 squares across with a white flash; 4 a fading pink swirl.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; the figure's place at the centre of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `xayah_fx_e_hit.png`：收回的羽毛划过敌人（目标身上），3 帧

飞回的羽毛划过一个敌人：一道细长的品红色划痕和几粒碎光（参考 E_hit_tar_muzzle、E_tar_hitflash2）。约 12 格，居中画，左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a FEATHER CUT, 3 frames, symmetric left and right: 1 a thin horizontal magenta slash line 10 squares long with a white middle; 2 the line splitting into a few pink sparks; 3 fading sparks.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `xayah_fx_e_root.png`：倒钩禁锢：被羽毛钉住（目标身上），5 帧

被 3 支以上的羽毛命中时禁锢：几片品红色羽刃斜插在敌人脚边，地面一圈深红色的光，向上溅起一下（参考 E_root_feathers、E_tar_ring、DaggerReturn_RootSuccess）。约 20 格宽、12 格高，脚在格子底部中间，**中间留出人形的空位，左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a crimson ramp (#FFE6E6, #FF8A9A, #F02D50, #B0123A, #600A24).
Effect: a ROOT BY FEATHERS at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 5 frames: 1 a crimson flash on the ground round the feet; 2 four magenta feather blades (dark outline, white edges) stabbing slantwise into the ground round the feet, two on each side, a flat crimson ring 20 squares wide and 5 tall; 3 the ring flaring brighter, pink sparks thrown up; 4-5 the blades standing, the ring dimming.
Layout: one horizontal row of 5 equal 5:3 cells, image size 1600x192 (each cell 320x192); the feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `xayah_fx_e_bind.png`：被禁锢中（目标脚下循环），4 帧

禁锢持续中：敌人脚边插着的羽刃一闪一闪，地上淡淡的深红光圈（参考 R_root_tar_pulse）。约 16 格宽、8 格高，**中间留出人形的空位，左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a crimson ramp (#FFE6E6, #FF8A9A, #F02D50, #B0123A, #600A24).
Effect: a ROOTED LOOP at a figure's feet (do NOT draw the figure; leave its place empty; symmetric left and right), 4 frames, a seamless loop: four small magenta feather blades stuck in the ground round the feet (two each side, dark outline), a flat crimson ring 16 squares wide pulsing dim-bright-dim, a white glint running up one blade per frame.
Layout: one horizontal row of 4 equal 2:1 cells, image size 1536x768 (each cell 384x192); the feet at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `xayah_fx_w_cast.png`：W 致死羽衣：开启（施法者身上），5 帧

开启致死羽衣：她身边卷起一圈品红和紫色的羽刃风暴，几片羽毛绕着她转一圈（参考 W_buf_swirls、W_buf_feather_cas、W_feathers）。约 26 格，居中画，**中间留出人形的空位，左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a BLADE STORM ignites round a figure (do NOT draw the figure; leave its place empty; symmetric left and right), 5 frames: 1 a burst of pink light at the centre; 2 a ring of 8 small magenta feather blades (dark outline) spinning round on an oval 26 squares wide and 12 tall, violet wind streaks; 3-4 the blades a quarter turn further round each frame; 5 the ring thinning.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the figure's place at the centre of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `xayah_fx_w_on.png`：W 致死羽衣持续中（施法者脚下循环），4 帧

致死羽衣持续中：她脚下一个扁扁的椭圆光环，几片小羽毛绕着转（参考 W_buf_mult、W_orb_darkglow）。约 22 格宽、8 格高，环在格子底部中间，左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050).
Effect: a SPINNING FEATHER RING on the ground (symmetric left and right), 4 frames, a seamless loop: a flat oval of violet light 22 squares wide and 7 tall, 6 tiny magenta feather glints on it moving a step round each frame.
Layout: one horizontal row of 4 equal 11:4 cells, image size 2816x256 (each cell 704x256); the ring at the bottom middle of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `xayah_fx_w_flash.png`：W 第二片羽刃出手（施法者身上），3 帧

致死羽衣期间每次普攻多甩出一片羽刃：手边一个小小的紫色闪光。约 10 格，居中画，左右对称，只 3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050) and a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450).
Effect: a SMALL HAND FLASH (symmetric left and right), 3 frames: 1 a white-violet spark 4 squares across; 2 a violet four-pointed star 8 squares across; 3 fading.
Layout: one horizontal row of 3 equal square cells, image size 768x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `xayah_fx_w_ms.png`：W 加速（施法者脚下循环），4 帧

羽刃命中英雄后加移速：脚边几道往后飘的粉色速度线和小羽毛（参考 Z_Flecks、Z_Feathers）。约 18 格宽、6 格高，在格子底部，**左右对称**（向两边飘）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a gold ramp (#FFF4C8, #FCC24F, #F08122, #B84313).
Effect: SPEED WISPS at the feet (symmetric left and right), 4 frames, a seamless loop: short pink speed streaks and 2 tiny gold-tipped feathers drifting outward to both sides along the ground, 18 squares wide and 6 tall, moving a step outward each frame.
Layout: one horizontal row of 4 equal 3:1 cells, image size 2304x768 (each cell 576x192); the streaks at the bottom of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `xayah_fx_r_cast.png`：R 暴风羽刃：腾空（施法者身上），5 帧

暴风羽刃起手：她身后张开一对由羽刃组成的翅膀（参考 Passive_wing_avatar、R_feathers），向上扬起一圈品红色的羽毛风。约 28 格，居中画，**中间留出人形的空位，左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450), a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050) and a gold ramp (#FFF4C8, #FCC24F, #F08122, #B84313).
Effect: FEATHER WINGS opening round a figure (do NOT draw the figure; leave its place empty; symmetric left and right), 5 frames: 1 a flash of pink light; 2 two wings of layered magenta feather blades (dark outline, white edges, gold tips) spreading out to both sides, 28 squares across; 3 the wings at their widest, small feathers swirling up; 4-5 the wings folding up and fading.
Layout: one horizontal row of 5 equal square cells, image size 1280x256; the figure's place at the centre of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `xayah_fx_r_rain.png`：R 匕首雨：朝前方扇形落下（地面区域），6 帧

暴风羽刃落下：从她身前（格子左边中点）向右扇形散开，几十把品红色羽刃匕首从上方斜着落下插进地面，落点一串白色闪光，最后插满一地的羽毛（参考 R_feathers_color、R_Tar_impact、R_tar_ground）。**朝右画、上下对称**（游戏会转到施法方向；朝左时整张会上下翻转，所以上下必须对称）。约 90 格长、50 格宽的扇形。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450), a violet ramp (#FFFFFF, #ECD8FF, #B87AF0, #8A3CD8, #5A1FA0, #2A1050) and a crimson ramp (#FFE6E6, #FF8A9A, #F02D50, #B0123A, #600A24).
Effect: a FAN OF RAINING FEATHER DAGGERS spreading to the RIGHT, 6 frames, SYMMETRIC above and below the middle line: the fan's tip at the LEFT MIDDLE of the cell, opening to the right (90 squares long, 50 wide at the far end); 1 a spray of thin magenta streaks shooting out along the fan; 2-3 dozens of small magenta daggers (dark outline, white tips) landing all over the fan with white impact flashes; 4 crimson impact sparks across the fan; 5 the daggers stuck in the ground across the fan; 6 fading.
Layout: one horizontal row of 6 equal 9:5 cells, image size 2880x320 (each cell 480x320... at 8x: 720x400; any equal cells 9:5); the fan's tip at the left edge, halfway down, of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `xayah_fx_r_hit.png`：R 匕首打中（目标身上），4 帧

匕首雨打中：一把羽刃从上方插下，一下深红白色冲击（参考 R_Tar_impact）。约 16 格，居中画，左右对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, no soft gradients, bright saturated colours with white cores so it reads on a dark ground, colours from a magenta ramp (#FFFFFF, #FFD6F2, #FF7AD8, #F02D9C, #C0207A, #7A1450) and a crimson ramp (#FFE6E6, #FF8A9A, #F02D50, #B0123A, #600A24).
Effect: a DAGGER STRIKE FROM ABOVE (symmetric left and right), 4 frames: 1 a magenta dagger (dark outline) diving straight down into the centre; 2 a white-crimson impact burst 14 squares across; 3 a crimson ring with sparks; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256; centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `xayah_fx_a_blade` | view_projectiles `league_xayah_a_blade`、`league_xayah_w_blade`（朝右，游戏转到飞行方向，上下对称） | 11 × 4 |
| `xayah_fx_a_pierce` | view_projectiles `league_xayah_a_pierce`（朝右，上下对称） | 16 × 6 |
| `xayah_fx_a_hit` | view_effects `league_xayah_a_hit`（跟随，画在人物上面） | 12 |
| `xayah_fx_p_on` | view_effects `league_xayah_p_on`（施法者身上，不跟随；格子中心放到手） | 10 |
| `xayah_fx_f_drop` | view_effects `league_xayah_f_drop`（地面上的点，不旋转） | 6 × 10 |
| `xayah_fx_f_lie` | view_effects `league_xayah_f_lie`（地面上的点，每 1/3 秒重播一次，不旋转） | 5 × 9 |
| `xayah_fx_feather` | view_projectiles `league_xayah_feather`（朝右，游戏转到飞行方向，上下对称） | 13 × 5 |
| `xayah_fx_q_dagger` | view_projectiles `league_xayah_q_dagger`（朝右，上下对称） | 14 × 5 |
| `xayah_fx_q_flash` | view_effects `league_xayah_q_flash`（施法者身上，不跟随；格子左边中点放到手） | 12 × 8 |
| `xayah_fx_q_hit` | view_effects `league_xayah_q_hit`（跟随，画在人物上面） | 14 |
| `xayah_fx_e_cast` | view_effects `league_xayah_e_cast`（施法者身上，不跟随；格子中心放到她胸口） | 24 |
| `xayah_fx_e_hit` | view_effects `league_xayah_e_hit`（跟随，画在人物上面） | 12 |
| `xayah_fx_e_root` | view_effects `league_xayah_e_root`（跟随，画在人物上面） | 20 × 12 |
| `xayah_fx_e_bind` | view_buffs `league_xayah_e_bind`（跟随，画在人物上面） | 16 × 8 |
| `xayah_fx_w_cast` | view_effects `league_xayah_w_cast`（施法者身上，跟随；格子中心放到她胸口） | 26 |
| `xayah_fx_w_on` | view_buffs `league_xayah_w_on`（跟随，画在人物下面） | 22 × 8 |
| `xayah_fx_w_flash` | view_effects `league_xayah_w_flash`（施法者身上，不跟随；格子中心放到手） | 10 |
| `xayah_fx_w_ms` | view_buffs `league_xayah_w_ms`（跟随，画在人物下面） | 18 × 6 |
| `xayah_fx_r_cast` | view_effects `league_xayah_r_cast`（施法者身上，跟随；格子中心放到她胸口） | 28 |
| `xayah_fx_r_rain` | view_projectiles `league_xayah_r_rain`（LineRangeProjectile 的画面：朝右画，扇形的尖在格子左边中点，上下对称） | 90 × 50 |
| `xayah_fx_r_hit` | view_effects `league_xayah_r_hit`（跟随，画在人物上面） | 16 |

- `a_blade` 同时导成 `a_blade` 和 `w_blade`；`f_lie` 每次播一帧（技能数据里每 20 tick 重播一次）。
- 施法者身上的画面按 `design/xayah_shots.png` 的十字把起点挪过去；有前后之分的手上闪光（`q_flash`）按红方规则画进她的动作帧（`tools/fix/bake_caster_fx.py`），左右对称的画面留作 CasterViewEffect。
- 飞行物第一帧前加空帧（出生那一 tick 刚离开手）；`e_bind`、`e_root` 画在人物上面，只画脚边；`w_on`、`w_ms` 画在人物下面。
- 清掉 Codex 给光和风描的最深色边（`import_riven.py` 的 `unrim`，实心物体保留描边）；核对交回的张数和这份清单；量每张的平均亮度和最亮的一成，和包里别的英雄比；Codex 交的如果是要求尺寸的 2 倍，缩一半。
