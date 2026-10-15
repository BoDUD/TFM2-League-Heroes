# 复仇之矛 卡莉丝塔：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/kalista_idle.png`：3/4 正面朝右的低蹲，近侧手低握长矛、矛头指向身后，背上两支备用矛）。她在游戏里是**高清**的（每个游戏格子里 1.4×1.4 个细像素），连长矛 41 格高、51 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/kalista_size.png`：她的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/kalista_shots.png`：定稿动作（4 倍），青色十字是她的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里卡莉丝塔自己的特效贴图（大多是灰度或单色的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**矛是黑色的、带青绿色的幽灵光纹**，**打中和撕裂是青绿偏白的幽灵光（白芯）**，**大招「命运的召唤」是偏深的灵魂蓝**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光圈、光带只画外圈和两边，中间身体位置留空**（`r_take` 的光带可以横着盖过身体，但要有空隙）。
> - **方向（重要，红色方不会镜像）**：飞出去的 `a_spear`、`q_spear` 画成朝右，**上下对称**（往左飞时会上下翻）。其余所有画面（打中、身上、脚下、头顶、地上的冲击）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）——插在身上的矛竖直、拔矛竖直往上，不要画成斜的。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `kalista_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `kalista_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「武术姿态」+ W「哨兵」 | 投矛，矛插在目标身上；被贴身时投矛后往后跳；队友在目标身边时额外伤害 | `a_spear` · `a_hit` · `sp_mark` · `w_hit` |
| 技能 1 = Q「穿刺」 | 投出长矛，击杀则穿过去打下一个 | `q_spear` · `q_hit` |
| 技能 2 = E「撕裂」 | 拔出所有矛：每支矛一次伤害和减速；击杀英雄刷新 | `e_rip` · `e_cast` · `e_reset` · `e_slow` |
| 大招「命运的召唤」 | 把身边队友拉进身体保护，再甩向目标，落地击飞周围敌人 | `r_take` · `r_safe` · `r_fly` · `r_land` · `r_up` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、雾、火星、碎片、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（矛例外：黑色的矛身可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 幽灵青绿（打中、撕裂、她的光）：`#FFFFFF`、`#D9FFF1`、`#7CF5C8`、`#22D9A0`、`#0E9C78`、`#075443`；
  - 黑矛（矛身、矛头）：`#E8F4F8`、`#8A8FA0`、`#4C4F60`、`#26262F`、`#121217`；
  - 灵魂蓝（大招）：`#FFFFFF`、`#CFE9FF`、`#7EB8FF`、`#3C7BE0`、`#1D3E8A`；
  - 尘土（大招落地）：`#F2E6CF`、`#D6C3A0`、`#B39B76`、`#8A7255`、`#5E4C39`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上、脚下、头顶的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 52500，Q 射程 100000，大招落地击飞半径 26000）。

### 1. `kalista_fx_a_spear.png`：普攻：投出去的幽灵矛（朝目标飞，循环），2 帧

普攻投出去的矛：一支细长的黑色矛（矛头尖、在右边），矛身有青绿色的发光条纹，后面拖一小段青绿偏白的幽灵光尾（参考 BA_Spear_CA、BA_Spear_Glow、BA_trail）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black spear ramp (#E8F4F8, #8A8FA0, #4C4F60, #26262F, #121217) and a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a GHOST SPEAR flying to the RIGHT, 2 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a slim black spear 12 squares long and 1 square thick with a pointed leaf blade 3 squares long and 3 tall at its RIGHT end, 2 sea-green glowing streaks along the shaft; a green-white ghost trail 4 squares long behind it, flickering between the two frames.
Layout: one horizontal row of 2 equal 18:6 cells, image size 576x96 (each cell 288x96, 16 px a square); the blade's tip 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `kalista_fx_q_spear.png`：Q 穿刺：投出去的长矛（朝目标飞，循环），4 帧

穿刺：一支更长更亮的黑矛，矛头整个包在青绿偏白的幽灵光里，后面拖一条长长的青绿色光尾和几缕幽灵烟（参考 Q_Mis_Glow、Q_Mis_Trail、Q_GhostTrail、Q_Mist）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black spear ramp (#E8F4F8, #8A8FA0, #4C4F60, #26262F, #121217) and a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a PIERCING SPEAR flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a black spear 14 squares long, its leaf blade 4 squares long wrapped in a bright green-white glow 6 squares across; a tapering sea-green trail 10 squares long behind it with ghostly wisps above and below it at mirrored places, drifting between frames.
Layout: one horizontal row of 4 equal 26:10 cells, image size 1664x160 (each cell 416x160, 16 px a square); the glow's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `kalista_fx_a_hit.png`：普攻打中（目标身上），4 帧

矛打中：一小团青绿偏白的闪光，几道短短的青绿色光线往外射（参考 BA_flash、BA_Hit_Poof、Cross_Stars）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a SMALL SPECTRAL HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a green-white flash 7 squares with a white core; 3 the flash 10 squares, 6 short sea-green rays at mirrored places; 4 a few fading sea-green motes.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `kalista_fx_q_hit.png`：Q 穿刺打中（目标身上），5 帧

穿刺命中：一圈青绿色的冲击波炸开（白芯），几道青绿色的光痕往外射，几块碎光飞出（参考 Q_Tar_Shockwave_1/2、Q_Tar_Streaks_4x1、Q_Tar_Bits_4x4）。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a PIERCING IMPACT on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a sea-green burst 10 squares across with a white core; 3 a sea-green shockwave ring 16 squares across, 8 sea-green streaks shooting out at mirrored places; 4 the ring 18 squares and fading, small sea-green bits flying out; 5 fading motes.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `kalista_fx_w_hit.png`：W 哨兵（灵魂绑定）：额外伤害（目标身上），4 帧

灵魂绑定触发：目标身上浮出一个青绿色的幽灵手印 / 灵魂标记，一闪后化成光点（参考 W_Radial_1、P_Hit_Splat）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a SOUL MARK flaring on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a sea-green glow 4 squares; 2 a sea-green rune 12 squares wide - a ring with four short spikes pointing in, mirrored - with a white core; 3 the rune brightest, 14 squares; 4 the rune breaking into sea-green motes.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `kalista_fx_sp_mark.png`：插在敌人身上的矛（目标身上，循环），2 帧

插在敌人身上的矛（撕裂的层数）：一支短短的黑矛竖着从上往下插进目标的身体，矛尾露在外面，矛身上一圈青绿色的幽灵光微微闪（参考 P_blade3_full、P_Hit_Tips、BackSpear_rgba）。**左右对称**：矛竖直、在格子正中。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a black spear ramp (#E8F4F8, #8A8FA0, #4C4F60, #26262F, #121217) and a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a SPEAR STUCK in a unit, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a short black spear standing straight UP in the middle column, its blunt end at the top, 12 squares long and 2 squares thick, its lower 3 squares hidden (stuck in the body: the cell's bottom 3 rows empty); a faint sea-green glow 4 squares wide round its middle that pulses between the frames.
Layout: one horizontal row of 2 equal 8:16 cells, image size 256x256 (each cell 128x256, 16 px a square); the spear in the middle column of every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `kalista_fx_e_rip.png`：E 撕裂：拔出一支矛（目标身上），5 帧

撕裂：插着的矛被猛地往上拔出，拔出的地方一团青绿色的光爆开，几块青绿色的碎片往外飞（参考 P_PullOut、DarkImpact_01、ImpactSparks_4x4）。**左右对称**。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443) and a black spear ramp (#E8F4F8, #8A8FA0, #4C4F60, #26262F, #121217).
Effect: a SPEAR RIPPED OUT of a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a short black spear standing up in the middle, a sea-green glow at its foot; 2 the spear jerked UP 6 squares, a green-white burst 8 squares where it was; 3 the spear gone above the cell's top, the burst 14 squares with 6 sea-green shards flying out at mirrored places; 4 the burst 16 squares and fading, the shards further out; 5 a few fading motes.
Layout: one horizontal row of 5 equal 18:22 cells, image size 1440x352 (each cell 288x352, 16 px a square); the burst's middle 6 squares above the cell's bottom row, centered across. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `kalista_fx_e_cast.png`：E 撕裂：发动（她身上，不跟随），5 帧

撕裂发动：她握拳往回一扯，身边一圈青绿色的幽灵光往里一收（像一圈线被扯紧），然后散成光点。**左右对称**，中间她的身体位置留空（只画外圈）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a PULL-IN RING round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a clear area 18 squares wide and 26 tall where she is, not drawn): 1 a thin sea-green ellipse 36 wide and 10 tall round her waist; 2 eight sea-green threads from the ring's edge pointing in toward her, mirrored; 3 the ring and threads snapping inward to 24 wide, brightest; 4 the threads breaking into sea-green motes; 5 the last motes.
Layout: one horizontal row of 5 equal 38:30 cells, image size 3040x480 (each cell 608x480, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `kalista_fx_e_reset.png`：E 撕裂击杀刷新（她头顶，不跟随），4 帧

撕裂击杀返还冷却：她头顶一闪青绿色的十字星光（参考 Cross_Stars、Q_LensFlare）。**左右对称**。约 12 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a STAR FLARE over a head, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a four-pointed sea-green star 10 squares with a white core; 3 the star 12 squares, a ring 8 squares round it; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `kalista_fx_r_take.png`：大招 命运的召唤：把队友拉进来（队友身上），6 帧

命运的召唤：被召唤的队友身上缠上几道蓝色的灵魂锁链 / 光带，从脚下往上缠住，全身泛起一层蓝光（参考 R_Charged_Glow、R_Charged_Sphere、P_Link_Swirls、R_Start_Waves）。**左右对称**，光带可以横着盖过身体，但不要画成实心的一团。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul blue ramp (#FFFFFF, #CFE9FF, #7EB8FF, #3C7BE0, #1D3E8A) and a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: SOUL BONDS wrapping a figure, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 10 squares wide and 22 tall stands in the middle, not drawn): 1 blue soul light rising from the ground at both sides; 2 two blue bands spiralling up round the legs, crossing in front; 3 the bands up to the shoulders, a soft blue glow outline round the figure 16 wide and 26 tall; 4 the bands and glow brightest with a white core line; 5 the bands drawing in tight; 6 a blue shimmer left round the figure.
Layout: one horizontal row of 6 equal 18:30 cells, image size 1728x480 (each cell 288x480, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `kalista_fx_r_fly.png`：大招：被甩出去的队友（队友身上，跟随），4 帧

被甩出去：飞行中的队友全身包着一层蓝色的灵魂光，身后拖着上下两条光带（参考 R_Trail、R_Knockup_Trail、R_mis_tube）。**左右对称**（光往上下两边散，不画方向）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul blue ramp (#FFFFFF, #CFE9FF, #7EB8FF, #3C7BE0, #1D3E8A) and a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a SOUL AURA round a flying figure, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a figure 10 squares wide and 22 tall in the middle, not drawn): a blue glow outline 18 wide and 26 tall round it, white-blue light flickering on it, streaks of blue light peeling off its top and bottom at mirrored places, changing between frames.
Layout: one horizontal row of 4 equal 20:30 cells, image size 1280x480 (each cell 320x480, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `kalista_fx_r_land.png`：大招：落地冲击（地上，不跟随），6 帧

落地：地面炸开一圈蓝色的灵魂冲击波（扁椭圆），中间一团白蓝色的光往上冲，尘土往两边溅（参考 R_Shockwave、R_Shockwave_Ring、R_Hit_Shockwave、R_Ground_rgba、R_Push_Out_Smoke）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul blue ramp (#FFFFFF, #CFE9FF, #7EB8FF, #3C7BE0, #1D3E8A) and an earth-dust ramp (#F2E6CF, #D6C3A0, #B39B76, #8A7255, #5E4C39).
Effect: a SOUL SHOCKWAVE on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares on the ground; 2 a blue burst 12 squares wide rising 10 squares, a flat ground ring 20 wide and 6 tall; 3 the ring 32 wide, dust kicked out at both sides; 4 the ring 40 wide and fading, the burst breaking into blue motes, dust settling; 5 the last ring arcs and motes; 6 a faint glow.
Layout: one horizontal row of 6 equal 42:20 cells, image size 4032x320 (each cell 672x320, 16 px a square); centered across, the ground ring's middle 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `kalista_fx_r_up.png`：大招：被击飞的敌人（目标身上），5 帧

被击飞：敌人身边几道蓝色的光痕往上冲（参考 R_Knockup_Trail、R_Flare）。**左右对称**，中间身体位置留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul blue ramp (#FFFFFF, #CFE9FF, #7EB8FF, #3C7BE0, #1D3E8A).
Effect: UPWARD SOUL STREAKS round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the middle EMPTY (a figure 10 squares wide and 22 tall, not drawn): 1 blue light at both sides of the feet; 2 four blue streaks shooting up at both sides, mirrored, 12 squares tall with white cores; 3 the streaks 24 squares tall; 4 the streaks thinning; 5 a few blue motes.
Layout: one horizontal row of 5 equal 16:28 cells, image size 1280x448 (each cell 256x448, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `kalista_fx_e_slow.png`：E 撕裂减速（敌人脚下，循环），4 帧

被撕裂减速：敌人脚下一圈淡淡的青绿色幽灵环，几点青绿光轮流闪。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a spectral sea-green ramp (#FFFFFF, #D9FFF1, #7CF5C8, #22D9A0, #0E9C78, #075443).
Effect: a FAINT CYAN RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin flat ellipse 14 squares wide and 4 tall in sea-green, 4 brighter motes on it at mirrored places taking turns to light up.
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `kalista_fx_r_safe.png`：大招：被保护的队友（队友身上，循环），4 帧

在她体内被保护：队友身上一层半透明感的蓝色灵魂光晕（用稀疏的蓝色光点和外圈光边表现，不要实心），慢慢呼吸。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, mist, sparks, shards or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a soul blue ramp (#FFFFFF, #CFE9FF, #7EB8FF, #3C7BE0, #1D3E8A).
Effect: a SOUL SHROUD round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (a figure 10 squares wide and 22 tall in the middle, not drawn): a blue glow outline 14 wide and 24 tall, sparse blue light dots inside it, the outline brightening and dimming through the loop.
Layout: one horizontal row of 4 equal 16:28 cells, image size 1024x448 (each cell 256x448, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `kalista_fx_a_spear` | view_projectiles `league_kalista_a_spear`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 5 |
| `kalista_fx_q_spear` | view_projectiles `league_kalista_q_spear`（朝飞行方向转，画成朝右飞；上下对称） | 24 × 8 |
| `kalista_fx_a_hit` | view_effects `league_kalista_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `kalista_fx_q_hit` | view_effects `league_kalista_q_hit`（跟随，画在人物上面；左右对称） | 18 |
| `kalista_fx_w_hit` | view_effects `league_kalista_w_hit`（跟随，画在人物上面；左右对称） | 14 |
| `kalista_fx_sp_mark` | view_effects `league_kalista_sp_mark`（跟随，画在人物上面；左右对称） | 6 × 14 |
| `kalista_fx_e_rip` | view_effects `league_kalista_e_rip`（跟随，画在人物上面；左右对称） | 16 |
| `kalista_fx_e_cast` | view_effects `league_kalista_e_cast`（不跟随，画在她身上；左右对称；大图表） | 36 × 28 |
| `kalista_fx_e_reset` | view_effects `league_kalista_e_reset`（不跟随，她头顶；左右对称） | 12 |
| `kalista_fx_r_take` | view_effects `league_kalista_r_take`（跟随队友，画在人物上面；左右对称；大图表） | 18 × 28 |
| `kalista_fx_r_fly` | view_effects `league_kalista_r_fly`（跟随队友，画在人物上面；左右对称；大图表） | 20 × 28 |
| `kalista_fx_r_land` | view_effects `league_kalista_r_land`（不跟随，地上；左右对称；大图表） | 40 × 18 |
| `kalista_fx_r_up` | view_effects `league_kalista_r_up`（跟随，画在人物上面；左右对称） | 14 × 26 |
| `kalista_fx_e_slow` | view_buffs `league_kalista_e_slow`（跟随，画在人物下面；左右对称） | 16 × 5 |
| `kalista_fx_r_safe` | view_buffs `league_kalista_r_safe`（跟随队友，画在人物上面；左右对称；大图表） | 16 × 26 |

- 两张表：`asset/league/effects/league_kalista_fx`（小的）和 `league_kalista_big`（e_cast、r_take、r_fly、r_land、r_safe），tag = 名字（build_kalista.py 的 views）。
- `a_spear`、`q_spear` 是飞行投射物，画面朝飞行方向转；`e_cast`、`e_reset`、`r_land` 不跟随；`e_slow` 脚下 buff（z -1）；`sp_mark` 每 12 tick 播一次（循环 2 帧）。
- 用 `pixel_1x/` 切格（import_nidalee 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
