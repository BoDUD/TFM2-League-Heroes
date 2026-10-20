# 祖安怒兽 沃里克：给 Codex 的特效提示词（第 3 步）

> **这一份是 10 张特效图。** 造型已定（`design/warwick_idle.png`：3/4 正面朝右、弓着背的狼人，蓝紫色的毛、白色鬃毛、黄眼睛、张着嘴，背上竖着绿药瓶和铜尖刺，两只铜护臂，橄榄色短裤，一条翘起来的大尾巴）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），46 格高、63 格宽（连尾巴）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/warwick_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/warwick_shots.png`：动作帧（4 倍），青色十字是他的站位点；每张写了特效出现在哪里（动作还在改，只看位置和大小）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里沃里克自己的特效贴图（不少是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**他的爪子、撕咬、吸血、压制和鲜血追猎都是血红色的**，**远祖嗥叫的护体是淡钢蓝色的护罩**，**嚎叫的冲击波和声浪是淡紫灰色的**，**恐惧是紫色的狼头**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯；血红色要有亮红 / 白的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。没有弹道图。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `warwick_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/warwick_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/warwick_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（被动「血之饥渴」和 W「鲜血追猎」在里面） | 挥爪；附带魔法伤害并吸血；追猎残血的英雄时加速 | `a_hit` · `q_heal` · `w_hunt` |
| 技能 1 = Q「野兽之口」 | 扑到目标身上咬一口，回血 | `q_hit` · `q_heal` |
| 技能 2 = E「远祖嗥叫」 | 减伤护体，结束时仰天嚎叫让周围的敌人恐惧 | `e_guard` · `e_howl` · `e_roar` · `e_fear` |
| 大招「无尽束缚」 | 朝前飞扑，压住第一个英雄 1.5 秒连抓三下 | `r_bind` · `r_hit` · `q_heal` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、烟、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**（恐惧的狼头可以有一圈暗紫色的边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 血红色（爪痕、撕咬、吸血、压制、追猎）：`#FFFFFF`、`#FFD6CC`、`#FF7466`、`#E8242E`、`#A8101E`、`#5C0812`；
  - 淡钢蓝色（护体的罩子）：`#FFFFFF`、`#E6EEFF`、`#BACAEA`、`#8494C4`、`#525E94`、`#2C3262`；
  - 淡紫灰色（嚎叫的冲击波、声浪）：`#FFFFFF`、`#ECE6FF`、`#C0B2E6`、`#8A7ABA`、`#544488`、`#2C2054`；
  - 紫色（恐惧的狼头）：`#FFFFFF`、`#FFC0F2`、`#DA56E8`、`#9424B2`、`#520E6E`；
- 打中、爆发居中画，不旋转；地面上的圆（冲击波、光晕）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、他身边的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（10 张）

10 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：他的普攻射程 25000，嚎叫的半径 40000）。

### 1. `warwick_fx_a_hit.png`：普攻：爪子撕中目标，3 帧

他挥爪打中目标：三道并排、竖着往下的血红色爪痕一闪（中间白、边上血红），然后散成几点血珠（参考 q_wolfmanclaw、q_slash、q_shred）。**左右对称**（三道爪痕都是竖的，中间那道最长）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFD6CC, #FF7466, #E8242E, #A8101E, #5C0812).
Effect: A CLAW RAKE ON A TARGET, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 three parallel VERTICAL claw streaks 12 squares tall, 3 squares apart, the middle one the longest, each white in the middle and blood red at its edges, tapering to points at both ends; 2 the streaks thinner and darker red, a few blood droplets flying out to both sides at mirrored places; 3 only the droplets and the faint streak tails, fading.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `warwick_fx_q_hit.png`：Q 野兽之口：獠牙咬合，5 帧

Q 咬中目标：一副大狼嘴的上下两排白色獠牙从上下两边合拢、在目标身上咬住，咬合处爆出一团血红色的血花（参考 q_biteswipe、q_swipetrail、q_shred）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFD6CC, #FF7466, #E8242E, #A8101E, #5C0812).
Effect: A BEAST'S BITE ON A TARGET, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an upper row of 5 big white fangs (each 2 wide, 4 tall, pointing down) on a dark red gum at the top of the cell and a lower row of 4 fangs (pointing up) at the bottom, far apart; 2 the two rows half-way closed; 3 the rows SNAPPED SHUT in the middle, a bright white-red flash where they meet; 4 the fangs gone, a blood-red burst 18 squares across with droplets flying out; 5 only droplets and wisps, fading.
Layout: one horizontal row of 5 equal square cells, image size 1760x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `warwick_fx_q_heal.png`：Q / 血之饥渴：吸血回复（他身上，跟随），5 帧

他咬中或者残血时回血：一圈血红色的光从他脚下亮起，一颗颗血珠从两边往上飘、往他胸口的高度聚过去（参考 z_bightspark、idle_plasma）。**他站在中间不画人，只画外圈和脚下**，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFD6CC, #FF7466, #E8242E, #A8101E, #5C0812).
Effect: A BLOOD HEAL ROUND A BIG BEAST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the hunched werewolf stands in the middle, not drawn: 46 squares from the spike on his back to the ground, about 40 squares wide without his tail, his body area left EMPTY): 1 a thin blood-red ellipse lighting up on the ground under him (40 wide, 9 tall); 2 eight round blood droplets (2-3 squares each) rising from the ellipse at his left and right; 3 the droplets higher, curving in toward the middle at his chest height (two thirds up), a soft red glint on each; 4 the droplets reaching the middle and flashing white; 5 only the fading ellipse and two sparks.
Layout: one horizontal row of 5 equal 44:50 cells, image size 3520x800 (each cell 704x800, 16 px a square); centered across, the ellipse's middle 4 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `warwick_fx_e_guard.png`：E 远祖嗥叫：护体（buff，循环），4 帧

E 开着时他受到的伤害减少：一层淡钢蓝色的护罩罩住他，罩子是一个扁圆的半透明壳（只画边：2 格宽的亮边，几道弧形的高光），上面有一圈圈波纹慢慢流动（参考 w_deflectionbubble、w_deflectionripples）。**他站在中间不画人，只画罩子的边和高光**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale steel-blue ramp (#FFFFFF, #E6EEFF, #BACAEA, #8494C4, #525E94, #2C3262).
Effect: A STEEL-BLUE GUARD SHELL ROUND A BIG BEAST, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the hunched werewolf stands in the middle, not drawn: 46 squares from the spike on his back to the ground, about 40 squares wide without his tail, his body area left EMPTY): a wide dome-shaped shell outline round him, 60 squares wide and 50 tall, its bottom open at the ground, its rim 2 squares of pale steel-blue with a white inner edge; two curved white highlight arcs on its upper left and upper right; each frame a ripple ring of lighter blue travels a few squares up the rim and the highlights shimmer.
Layout: one horizontal row of 4 equal 64:54 cells, image size 4096x864 (each cell 1024x864, 16 px a square); centered across, the dome's open bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `warwick_fx_e_howl.png`：E：嚎叫冲击波（地上，跟随），6 帧

嚎叫的一下：贴着地面一圈淡紫灰色的冲击波往外扩，带一圈灰白色的尘土，范围约 80 格宽（参考 z_shockwave、e_fearlines、z_smokepoofs）。**只画在地面上（他站在中间，不画人）**，**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale violet-grey ramp (#FFFFFF, #ECE6FF, #C0B2E6, #8A7ABA, #544488, #2C2054).
Effect: A HOWL'S SHOCKWAVE along the ground round him, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the hunched werewolf stands in the middle, not drawn: 46 squares from the spike on his back to the ground, about 40 squares wide without his tail): 1 a small bright ring on the ground (an ellipse 24 wide and 8 tall), white-violet; 2 the ring 46 wide and 15 tall, 2 squares thick, with a second fainter ring inside; 3 the outer ring 66 wide and 22 tall, small grey dust puffs kicked up along it at mirrored places; 4 the ring 80 wide and 27 tall, thinning, the dust rising; 5 only broken arcs of the ring and the dust; 6 faint dust, fading.
Layout: one horizontal row of 6 equal 88:32 cells, image size 8448x512 (each cell 1408x512, 16 px a square); centered across, the ellipse's middle 3 squares above the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `warwick_fx_e_roar.png`：E：嚎叫的声浪（他头顶上方，跟随），5 帧

他仰天嚎叫时从头顶往外扩的声浪：三道弧形的淡紫灰色声波一道接一道往上、往两边扩开（像括号形的弧），中间夹着几道白色的短线（参考 e_fearlines、z_eyeripples）。**画在他头顶上方，下面留空**，**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale violet-grey ramp (#FFFFFF, #ECE6FF, #C0B2E6, #8A7ABA, #544488, #2C2054).
Effect: A ROAR'S SOUND WAVES over a head, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): three wide upward-opening ARCS (like the top of a ring, each 2 squares thick) rising one after another from the bottom middle of the cell: 1 a small bright arc 10 wide just above the bottom; 2 that arc 20 wide and higher, a second small one under it; 3 the first 32 wide, the second 20, a third small one; 4 the arcs 42, 30 and 18 wide, the outer one fading, short white lines between them radiating out; 5 only faint outer arcs, fading.
Layout: one horizontal row of 5 equal 44:26 cells, image size 3520x416 (each cell 704x416, 16 px a square); centered across; the arcs start from the cell's bottom middle. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `warwick_fx_e_fear.png`：E：恐惧（敌人头上），6 帧

被嚎叫吓到的敌人头上冒出一个紫色的狼头（龇牙咧嘴、两只尖耳朵，正面），一闪一闪地抖动（参考 w_warn_solid、e_fearlines）。**左右对称**（狼头是正面的），6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a purple ramp (#FFFFFF, #FFC0F2, #DA56E8, #9424B2, #520E6E).
Effect: A FEAR MARK over a head, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small snarling WOLF HEAD seen from the front (two pointed ears, two slanted white eyes, an open jaw with white fangs), 12 squares wide, purple with a pale pink rim; 1 it pops in small; 2 full size; 3 shaken one square up; 4 back, two short purple jitter lines at its sides; 5 like 2; 6 fading.
Layout: one horizontal row of 6 equal 16:14 cells, image size 1536x224 (each cell 256x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `warwick_fx_r_bind.png`：R 无尽束缚：压制（目标身上），8 帧

R 扑中的英雄被压住 1.5 秒：两道血红色的能量环一上一下箍住他（扁圆环，一前一后），环上缠着暗红色的爪痕和锁链样的纹路，一闪一闪地收紧（参考 r_missscratches、warwick_temp_r_wolfmanclaw、r_rangeringmult）。**被压住的人站在中间不画，只画环和爪痕**，**左右对称**，8 帧（一共约 1.5 秒）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFD6CC, #FF7466, #E8242E, #A8101E, #5C0812).
Effect: A BLOOD SHACKLE ROUND A CHAMPION, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn, the body area left EMPTY): two flat blood-red rings (ellipses 26 wide and 7 tall, 2 squares thick, white-hot inner edge) around the body, one at its waist and one at its chest; dark red claw scratches (short diagonal triple streaks, mirrored) on both sides between them; the rings pulse tighter and brighter on frames 1, 4 and 7 and fade a little between; frame 8 the rings breaking into red sparks.
Layout: one horizontal row of 8 equal 28:36 cells, image size 3584x576 (each cell 448x576, 16 px a square); centered across, the waist ring 12 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `warwick_fx_r_hit.png`：R：撕扯（目标身上），4 帧

R 压住时每一下抓：一个大大的血红色 X 形爪痕（两组三道爪痕交叉）在目标身上炸开，中间白光，血珠四溅（参考 q_wolfmanclaw、q_shred、z_blaststreaks）。**左右对称**，比普攻的打中大。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFD6CC, #FF7466, #E8242E, #A8101E, #5C0812).
Effect: A BIG CROSSED CLAW TEAR, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 two sets of three claw streaks crossing in an X, 20 squares across, white in the middle and blood red at their edges; 3 the X darker, blood droplets bursting out at mirrored places; 4 only droplets and faint streak ends.
Layout: one horizontal row of 4 equal square cells, image size 1536x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `warwick_fx_w_hunt.png`：W 鲜血追猎：追猎中（buff，他脚下，循环），4 帧

他嗅到残血的猎物、加速追过去：脚下一圈血红色的光晕，两边有血红色的细烟往上飘，像血的气味在他周围翻腾（参考 w_scenttrail_blend、w_deathwisps、w_arrow_directional_red）。**只画在他脚下和两边下方，不画人**，**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blood-red ramp (#FFFFFF, #FFD6CC, #FF7466, #E8242E, #A8101E, #5C0812).
Effect: A BLOOD-SCENT AURA under a big beast, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the hunched werewolf stands in the middle, not drawn: 46 squares from the spike on his back to the ground, about 40 squares wide without his tail): a glowing blood-red ellipse on the ground under him (46 wide, 11 tall, its rim brightest), thin red wisps of scent curling up 8-10 squares at its left and right ends; each frame the wisps curl a little higher and fade while new ones start low, the rim flickering.
Layout: one horizontal row of 4 equal 52:22 cells, image size 3328x352 (each cell 832x352, 16 px a square); centered across, the ellipse's middle 6 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `warwick_fx_a_hit` | view_effects `league_warwick_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `warwick_fx_q_hit` | view_effects `league_warwick_q_hit`（跟随目标，画在人物上面 z 2；左右对称） | 22 × 22 |
| `warwick_fx_q_heal` | view_effects `league_warwick_q_heal`（跟随他，画在人物上面 z 2；左右对称） | 44 × 50 |
| `warwick_fx_e_guard` | view_buffs `league_warwick_e_on`（跟随他，画在人物上面 z 2；左右对称；循环） | 64 × 54 |
| `warwick_fx_e_howl` | view_effects `league_warwick_e_howl`（跟随他，画在人物下面 z -1；左右对称；大图表） | 88 × 32 |
| `warwick_fx_e_roar` | view_effects `league_warwick_e_roar`（跟随他，画在人物上面 z 3；左右对称） | 44 × 26 |
| `warwick_fx_e_fear` | view_effects `league_warwick_e_fear`（跟随目标，画在人物上面 z 3；左右对称） | 16 × 14 |
| `warwick_fx_r_bind` | view_effects `league_warwick_r_bind`（跟随目标，画在人物上面 z 2；左右对称） | 28 × 36 |
| `warwick_fx_r_hit` | view_effects `league_warwick_r_hit`（跟随目标，画在人物上面 z 2；左右对称） | 24 × 24 |
| `warwick_fx_w_hunt` | view_buffs `league_warwick_w_hunt`（跟随他，画在人物下面 z -1；左右对称；循环） | 52 × 22 |

- 两张表：`asset/league/effects/league_warwick_fx`（小的）和 `league_warwick_big`（e_howl、e_guard），tag = 名字（build_warwick.py 的 views；e_guard 绑在 buff `league_warwick_e_on` 上，w_hunt 绑在 `league_warwick_w_hunt` 上）。
- 全部断言左右对称；`e_howl`、`w_hunt` 画在他下面（z -1），`e_roar`、`e_fear` 在上面（z 3）。
- 用 `pixel_1x/` 切格（import_zoe_fx 的做法）；清掉 Codex 给光描的最深色边（恐惧狼头的暗紫边保留）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
