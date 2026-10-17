# 暗黑元首 辛德拉：给 Codex 的特效提示词（第 3 步）

> **这一份是 17 张特效图。** 造型和动作已定（`design/syndra_design.png`，8 倍，336 行、208 格宽）。
> - 大小对照 `design/syndra_size.png`：定稿造型放大 4 倍，最低的脚尖在红线上，上面是 10 格一段的刻度，右边是原版斗士。辛德拉 208×336 格。每条写的大小都是游戏像素（格）。
> - `design/syndra_shots.png`：定稿动作的出手帧（4 倍），青色十字是特效的起点（伸出的右手、脚下），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里辛德拉自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**暗黑法球是近黑的深紫色球体、外面一圈亮紫色光、洋红色的边光；她的念力、推波是亮紫色；打中是洋红白色**。
> - **特效要亮**：法球的球体可以暗，但外圈的光、边光和高光要亮，暗底上一眼能看见；其他光、波、火花都用最亮的几档和白色的芯。
> - **围着人的法球圈、晕眩、升级光只画外圈和两边，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：飞出去的光弹和法球（`a_bolt`、`w_throw`、`r_orb`）画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。推波 `e_wave` 是**线的画面**：游戏把整张图的**中心**放在辛德拉身上、朝目标的方向转，所以**冲击波只画在格子右半边、从正中间往右推**，同样**上下对称**。画在人身上、脚下的（打中、晕眩、减速、法球圈、升级光）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；地上的 `q_form`、`q_blast`、`w_land` 上下左右都对称；地上停留的法球 `orb` 左右对称。
> - 特效照下面第 1–17 条和「所有特效图的规则」画，每张一个 PNG，文件名 `syndra_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。
> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`syndra_fx_done.zip`）放在 outputs 里，或放在 `outputs/syndra-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「卓尔不凡」 | 暗黑小光弹普攻；按等级依次强化 Q、W、E、R（升级时身上亮暗紫光） | `a_bolt` · `a_hit` · `evo` |
| 技能 1 = Q「暗黑法球」 | 在目标处凝聚一颗法球，0.5 秒后砸下造成伤害；法球留在原地 6 秒 | `q_form` · `q_blast` · `q_hit` · `orb` |
| 技能 2 = W「驱使念力」→ E「弱者退散」 | 抓起法球掷向敌方英雄（伤害 + 减速，法球留在落点）；接着往前推出锥形冲击波，被推开的法球撞到的人被晕眩 | `w_throw` · `w_land` · `w_hit` · `w_slow` · `e_wave` · `e_hit` · `e_stun` · `orb` |
| 大招 = R「能量倾泻」 | 身边聚起法球，向一名敌方英雄发射 3 颗 + 场上法球数（最多 7 颗） | `r_cast` · `r_orb` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、冲击波、火花、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**（法球的球体本身可以深色，但外面不要再加黑圈）。
- **要亮**：每个光的形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给法球的球体和很少的点缀。
- 颜色（按每条写的用）：
  - 念力亮紫（推波、掷出的光、晕眩、减速）：`#FFFFFF`、`#F0DCFF`、`#C890FF`、`#9048E8`、`#5A1CA8`；
  - 暗黑法球（球体、碎片）：`#E8C8FF`、`#9A5AE0`、`#5A2098`、`#2E0A58`、`#160430`；
  - 洋红（法球边光、打中、宝石光）：`#FFFFFF`、`#FFD8F2`、`#FF80DC`、`#E838B8`、`#A01480`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（17 张）

17 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，Q 半径 20000，W 半径 21000，E 推波长 70000，法球的晕眩范围半径 24000）。

### 1. `syndra_fx_a_bolt.png`：普攻：飞出去的暗黑小光弹（飞行中，循环），4 帧

辛德拉的普攻：一颗深紫色的小暗黑弹，外面一圈亮紫光，前面一点洋红白芯，后面拖一小段紫色光尾（参考 basatk_core、P_Mis_AnimeShapes、P_trail）。朝右飞。**上下对称**。4 帧无缝循环。约 8 格长、5 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430), a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a small DARK BOLT flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a round near-black violet core 3 squares across at the right with a bright violet glow round it and a 1-square magenta-white glint at its front, a short tapering violet trail 4 squares long behind it to the left; the trail flickers frame to frame.
Layout: one horizontal row of 4 equal 10:6 cells, image size 640x96 (each cell 160x96, 16 px a square); the bolt's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `syndra_fx_a_hit.png`：普攻打中（目标身上），4 帧

普攻打中：一朵紫色带洋红芯的小星光炸开（参考 HitEffect、darksov_Sparkle）。**左右对称**。约 10 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a DARK SPARK HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-magenta 4-point star 5 squares across; 2 a violet burst 7 squares across; 3 four violet sparks flying out diagonally; 4 a few fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `syndra_fx_q_form.png`：Q 暗黑法球成形：落点上法球凝聚（地上，0.5 秒），6 帧

Q 的法球在落点凝聚（0.5 秒后砸下）：地上一个从斜上方看的扁椭圆，紫色的暗影从四周往中心旋进来，中心慢慢亮起一个洋红色的光点（参考 Q_Orb_Core、darksov_force、Q_Lightning02）。这是技能的范围（半径 20 格），约 40 格宽、16 格高。**上下左右都对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8), a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a DARK SPHERE FORMING on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: a thin violet ellipse 38 squares wide and 14 tall (the area), 1 faint; 2-5 dark violet wisps at mirrored places drawing in from the ellipse toward the center, the ellipse brighter each frame, a magenta point growing at the center (1, 2, 3, 4 squares); 6 the ellipse brightest, the center a white-magenta spark.
Layout: one horizontal row of 6 equal 42:18 cells, image size 4032x288 (each cell 672x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `syndra_fx_q_blast.png`：Q 法球砸下的爆发（地上），5 帧

法球砸下爆发：中间一下紫白色的闪光，一圈紫色冲击波从中心往外扩到椭圆边缘，地上几道洋红色的裂纹光（参考 2021_Q_Flash_01、2021_Q_Cracks、darksov_blasthole）。**上下左右都对称**。约 40 格宽、16 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a DARK SPHERE IMPACT on the ground seen from above at an angle, 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 a white-violet flash 12 squares wide at the center; 2 a violet shockwave ring 24 squares wide with short magenta crack lines at mirrored places; 3 the ring 34 wide; 4 the ring 40 wide and 16 tall, thinner; 5 fading sparks on the ellipse.
Layout: one horizontal row of 5 equal 42:18 cells, image size 3360x288 (each cell 672x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `syndra_fx_q_hit.png`：Q 打中（目标身上），4 帧

Q 打中：一团紫白色的爆光，四周几块深紫色的碎片往外飞（参考 2021_Q_flashPiece_1、Q_ErosionShapes01）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8), a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a DARK BLAST HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 6 squares across; 2 a violet burst 10 squares across with a magenta core; 3 four dark violet shards flying out diagonally at mirrored places; 4 fading shards and sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `syndra_fx_orb.png`：地上停留的暗黑法球（落点上空，持续 6 秒），12 帧

法球留在原地 6 秒：一颗悬浮的暗黑法球（球体深紫、外圈亮紫光、洋红色的边光、一点白色高光），离地约 8 格浮着，地上一个扁椭圆的紫色影子（参考 common_darksov_orb_outlines、Q_Orb_Core、justicar_SphereGlow）。帧 1–2 球出现（从小变大），帧 3–10 球上下浮动 1 格、光圈一明一暗（循环感），帧 11–12 球淡出（变暗、缩小）。**左右对称**。球直径约 10 格，整张约 16 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430), a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a DARK SPHERE: a round orb, its body near-black violet with a darker core, a bright violet glow ring 1 square thick round it, a thin magenta rim light on its top-left and bottom-right, a tiny white glint, 10 squares across, FLOATING above its shadow, 12 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): the shadow a flat violet ellipse 12 squares wide and 3 tall on the cell's bottom, the orb's bottom 6 squares above it; 1 the orb 4 squares across, faint; 2 the orb 8 across; 3-10 the full orb rising and sinking 1 square (3-4 up, 5-6 middle, 7-8 down, 9-10 middle), its glow ring brighter on odd frames; 11 the orb darker and 8 across; 12 a faint 4-square orb and shadow.
Layout: one horizontal row of 12 equal 18:24 cells, image size 3456x384 (each cell 288x384, 16 px a square); centered across, the shadow on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `syndra_fx_w_throw.png`：W 掷出的法球（飞行中，循环），4 帧

W 抓起的法球被掷出去：一颗暗黑法球，外面裹着一层亮紫色的念力光，后面拖一道短的紫色光尾（参考 darksov_forcetrail、darksov_forcebubble）。朝右飞。**上下对称**。4 帧无缝循环。约 12 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430), a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a THROWN DARK SPHERE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a DARK SPHERE: a round orb, its body near-black violet with a darker core, a bright violet glow ring 1 square thick round it, a thin magenta rim light on its top-left and bottom-right, a tiny white glint, 8 squares across at the right, wrapped in a bright violet force glow, a violet trail 4 squares long behind it; the glow pulses.
Layout: one horizontal row of 4 equal 14:12 cells, image size 896x192 (each cell 224x192, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `syndra_fx_w_land.png`：W 法球砸地的冲击（地上），5 帧

W 的法球砸到地上：一圈紫色的念力冲击波往外扩，中心一下洋红白光，地上几道紫色的压痕（参考 darksov_crushwave、W_Circle_normal、W_Void_Background）。这是技能的范围（半径 21 格），约 44 格宽、18 格高。**上下左右都对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a FORCE SLAM on the ground seen from above at an angle, 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 a white-magenta flash 10 squares wide; 2 a bright violet ring 24 squares wide with a darker violet dent inside; 3 the ring 36 wide; 4 the ring 44 wide and 18 tall, thinner, violet sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal 46:20 cells, image size 3680x320 (each cell 736x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `syndra_fx_w_hit.png`：W 打中（目标身上），4 帧

W 打中：紫色念力的爆光，几道往下压的紫色光线（参考 darksov_force2、darksov_blastflash）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a FORCE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 6 squares across; 2 a violet burst 10 squares across with short downward streaks at mirrored places; 3 the burst breaking into sparks; 4 fading sparks.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `syndra_fx_w_slow.png`：W 减速（被减速的人脚下，循环），4 帧

被 W 减速：脚下一圈紫色的细光环，环里有往中间收的短线（左右对称）。**左右对称**。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8).
Effect: a SLOWING RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin violet ellipse 14 squares wide and 4 tall, 4 short inward ticks at mirrored places that slide toward the center each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `syndra_fx_e_wave.png`：E 弱者退散：往前推出去的锥形冲击波（线的画面，朝方向转），5 帧

E：从辛德拉身前（格子正中）往右推出一道扇形的紫色冲击波：一道弯弯的弧形波前从中心往右推到 70 格远，越远越宽（扇形张角约 56°，到末端约 64 格高），波前亮紫白色，后面拖着几道紫色的气流和一点洋红碎光（参考 2021_E_Core、2021_E_Lead、2021_E_Edge_2、E_Wisps、DarkSov_W5_Waves）。**整张图左半边是空的**（游戏把这张图的中心放在辛德拉身上，朝目标转）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a CONE SHOCKWAVE pushing to the RIGHT from the cell's CENTER, 5 frames, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): the LEFT HALF of every cell stays EMPTY; a bright curved wavefront (an arc bulging to the right, white-violet, 2 squares thick) inside a cone opening from the center to the right (56 degrees wide), violet wisps streaming behind it and a few magenta sparks: 1 the arc 12 squares right of the center, 14 tall; 2 the arc at 30, 32 tall; 3 the arc at 48, 48 tall, brightest; 4 the arc at 64, 60 tall, thinner; 5 the arc at 70 fading into sparks.
Layout: one horizontal row of 5 equal 144:66 cells, image size 11520x1056 (each cell 2304x1056, 16 px a square); the cone's tip on the cell's exact center, the cone vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `syndra_fx_e_hit.png`：E 打中（被推开的人身上），4 帧

被 E 推开：人身上一团紫色的冲击光，两边各几道往外的气流线（左右对称）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8).
Effect: a PUSH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet flash 6 squares across; 2 a violet burst 10 squares across with short streaks out to both sides at mirrored places; 3 the streaks longer, fading; 4 a few sparks.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `syndra_fx_e_stun.png`：E 法球撞人晕眩（被晕的人身上），8 帧

被推开的法球撞到人：先在人身上炸开一团暗紫色带洋红边的爆光（法球碎掉），然后头顶出现一圈紫色的晕眩小星（左右对称的位置），晃一会儿（参考 2021_R_HitFlash_Core、2021_R_HitFlash_Ring、darksov_Sparkle）。**左右对称**。下半部分是撞击（人身体的位置），上面是头顶的晕眩星。约 18 格宽、30 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430), a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a SPHERE CRASH AND STUN on a figure, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): frames 1-3 a burst at the cell's lower middle (the body): 1 a dark sphere 8 squares across with a magenta rim cracking; 2 a white-magenta flash 12 squares across with dark violet shards; 3 the shards flying out at mirrored places, fading; frames 4-8 a stun halo at the top of the cell: a flat violet ellipse 12 squares wide and 4 tall with 4 small white-violet stars on it at mirrored places that step round the ring each frame (keep each frame mirrored); in 8 the halo fading.
Layout: one horizontal row of 8 equal 20:32 cells, image size 2560x512 (each cell 320x512, 16 px a square); centered across, the burst in the lower half, the halo in the top quarter. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `syndra_fx_r_cast.png`：R 能量倾泻：法球聚到她身边（她身上，施法时），6 帧

R：她身边浮起一圈暗黑法球（7 颗，左右对称地排成一个椭圆，环绕在她周围，中间人站的位置留空），法球一颗颗亮起、往她身边收，最后一下发出去前最亮（参考 darksov_orb_outlines、justicar_SphereGlow、common_Darksov_Blackhole）。**中间留空**，**左右对称**（逐格对称）。约 56 格宽、48 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430), a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: SEVEN DARK SPHERES round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place in the middle (16 x 36 squares, its bottom on the cell's bottom) EMPTY: the spheres (each a near-black violet orb 6 squares across with a bright violet glow and a magenta rim) placed on an ellipse 50 squares wide and 40 tall round the figure at mirrored places (one at the top center, three on each side); 1 the spheres faint and small (4 across); 2 full size; 3 a violet glow line linking them; 4 the spheres brighter and 3 squares closer to the figure; 5 brightest, white glints; 6 fading.
Layout: one horizontal row of 6 equal 58:50 cells, image size 5568x800 (each cell 928x800, 16 px a square); centered across, the figure area's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `syndra_fx_r_orb.png`：R 飞向敌人的法球（飞行中，循环），4 帧

R 发出的法球：一颗暗黑法球拖着一道紫色彗星尾，尾巴里有洋红色的光点（参考 2021_R_Mis_Core、2021_R_Mis_Lead）。朝右飞。**上下对称**。4 帧无缝循环。约 14 格长、10 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430), a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a DARK SPHERE MISSILE flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a DARK SPHERE: a round orb, its body near-black violet with a darker core, a bright violet glow ring 1 square thick round it, a thin magenta rim light on its top-left and bottom-right, a tiny white glint, 8 squares across at the right, a violet comet tail 6 squares long behind it with magenta sparks in it; the tail flickers.
Layout: one horizontal row of 4 equal 16:12 cells, image size 1024x192 (each cell 256x192, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `syndra_fx_r_hit.png`：R 每颗法球打中（目标身上），5 帧

R 的法球打中：一团暗紫色的爆炸，外圈一道洋红色的光环，中心白光（参考 2021_R_HitFlash_Core、2021_R_HitFlash_Ring、darksov_blastflash）。**左右对称**。约 18 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a dark sphere ramp (#E8C8FF, #9A5AE0, #5A2098, #2E0A58, #160430), a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a DARK SPHERE EXPLOSION, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-magenta flash 8 squares across; 2 a dark violet blast 14 squares across with a bright magenta ring round it; 3 the ring 18 across, dark shards at mirrored places; 4 the ring thinner, sparks; 5 fading sparks.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `syndra_fx_evo.png`：卓尔不凡：技能升级时她身上的暗紫光（她身上），6 帧

卓尔不凡升级一个技能：她脚下亮起一圈紫色的光环往上升，几片紫色的水晶碎片往上飘，身边飘起洋红色的小光点（只画外圈和碎片，中间留空）（参考 2021_P_GlassCrystals、P_Flash_sharp、P_GroundLight_01）。**左右对称**。约 30 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparks or rings, BRIGHT colours (each glow lit with its lightest shades and a white core - it must read on a dark battlefield; a Dark Sphere's body may be dark but its rim and glow are bright), colours only from a force violet ramp (#FFFFFF, #F0DCFF, #C890FF, #9048E8, #5A1CA8) and a magenta ramp (#FFFFFF, #FFD8F2, #FF80DC, #E838B8, #A01480).
Effect: a DARK ASCENSION round a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: 1 a violet ellipse ring 24 squares wide and 6 tall at the feet; 2 the ring rising to the waist, small violet crystal shards (2x3 squares) at mirrored places beside the figure; 3 the ring at the chest, the shards higher, magenta sparks rising; 4 the ring at the head, bright; 5 the ring above the head, fading, shards and sparks; 6 fading sparks.
Layout: one horizontal row of 6 equal 32:46 cells, image size 3072x736 (each cell 512x736, 16 px a square); centered across, the feet ring on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `syndra_fx_a_bolt` | view_projectiles `league_syndra_a_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 8 × 5 |
| `syndra_fx_a_hit` | view_effects `league_syndra_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `syndra_fx_q_form` | view_effects `league_syndra_q_form`（Q 发出时在落点播放，不旋转，画在人物下面；上下左右都对称） | 40 × 16 |
| `syndra_fx_q_blast` | view_effects `league_syndra_q_blast`（落点上，不旋转，画在人物下面；上下左右都对称） | 40 × 16 |
| `syndra_fx_q_hit` | view_effects `league_syndra_q_hit`（跟随；左右对称） | 14 |
| `syndra_fx_orb` | view_effects `league_syndra_orb`（落点上，不旋转，画在人物上面；左右对称；12 帧共 6 秒） | 16 × 22 |
| `syndra_fx_w_throw` | view_projectiles `league_syndra_w_throw`（抛物线飞行、朝方向转；上下对称） | 12 × 10 |
| `syndra_fx_w_land` | view_effects `league_syndra_w_land`（落点上，不旋转，画在人物下面；上下左右都对称） | 44 × 18 |
| `syndra_fx_w_hit` | view_effects `league_syndra_w_hit`（跟随；左右对称） | 14 |
| `syndra_fx_w_slow` | view_buffs `league_syndra_w_slow`（画在脚下；左右对称） | 16 × 6 |
| `syndra_fx_e_wave` | view_projectiles `league_syndra_e_wave`（线的画面：以辛德拉为中心、朝目标的方向转；**画在格子右半边**；上下对称） | 140 × 64 |
| `syndra_fx_e_hit` | view_effects `league_syndra_e_hit`（跟随；左右对称） | 12 |
| `syndra_fx_e_stun` | view_effects `league_syndra_e_stun`（跟随；左右对称；8 帧共约 1.25 秒） | 18 × 30 |
| `syndra_fx_r_cast` | view_effects `league_syndra_r_cast`（施法时、跟随她，画在人物上面；左右对称） | 56 × 48 |
| `syndra_fx_r_orb` | view_projectiles `league_syndra_r_orb`（追踪弹、朝方向转；上下对称） | 14 × 10 |
| `syndra_fx_r_hit` | view_effects `league_syndra_r_hit`（跟随；左右对称） | 18 |
| `syndra_fx_evo` | view_effects `league_syndra_evo`（施法后，不跟随，画在人物上面；左右对称） | 30 × 44 |

- 光弹、掷出的法球、R 的法球从伸出的右手出（出手帧手在站位点前 6–7 格、脚底上 24–26 格）；`bolt_y` / `r_y` 按这个量（太高的弹道会斜），画面开头补一帧空的（追踪弹第一 tick 朝上）。
- `e_wave`：线的画面在辛德拉身上、朝目标转（champion-data section 6）；按 144 格宽切格，确认左半边是空的、上下对称；QE 时它也从辛德拉出发（模拟日志核对线的出生点）。
- `orb`：12 帧共 6 秒（orb_t 360 tick），落点画在人物上面；`q_form` 6 帧共 0.5 秒（q_fall 30 tick，`range_effect_name`）；`e_stun` 8 帧共约 1.25 秒（e_stun 75 tick）。
- 没有烘进动作帧的特效：`evo` 晚于第一 tick，`is_follow` 为 false，逐格左右对称；`r_cast` 在 R 第一 tick 跟随播放、逐格左右对称；`q_form`、`q_blast`、`w_land` 画在人物下面（z -2 / -1）。
- 用 `pixel_1x/` 切格（import_viktor / import_senna 的做法），断言对称；清掉 Codex 给光描的最深色边（法球球体的深色保留）；核对交回的张数和这份清单。
