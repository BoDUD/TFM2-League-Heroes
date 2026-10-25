# 战争女族长 安蓓萨：给 Codex 的特效提示词（第 3 步）

> **这一份是 20 张特效图。** 造型已定（`design/ambessa_design.png`：Q 版的诺克萨斯女军阀——银白色往后梳的波浪短发、深棕色皮肤、红唇、金耳环；肩上一圈深青绿色的尖毛领；黑铁胸甲、红围巾、红腰布；黑色的大护臂；**两只手各握一把带钩的月牙形龙犬刃**，刀柄连着粗铁链）。她在游戏里是**高清**的（每个游戏格子里 2×2 个细像素），48 格高、59 格宽（高×宽，连两把刀）；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/ambessa_size.png`：安蓓萨放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里安蓓萨自己的特效贴图（大多是灰度的形状），按用在我们哪张特效分好了行，只在本地用。**安蓓萨的特效是她那两把连着铁链的龙犬刃**：**锋利的银白色月牙刀光**，前沿**琥珀金色**，甩出**琥珀色的火星**，加上**暗色的烟尘和碎石**；拒斥的护盾是**青铜金色**的光；公开处决加一点**诺克萨斯的深红**。不要魔法光晕、不要电、不要光滑的霓虹光束。
> - **特效要亮**：每个形状都有最亮一档或白色的亮点，暗底上一眼能看见。
> - **刀光、冲击波、火星、烟尘都没有黑描边**（用它自己最深的一档）；只有碎石、铁链这种实心的东西有深色的边。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：打中、脚下、身上、地上的画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。**弹道**（`q2_crack`）**朝右画、后面在左边，严格上下对称**（游戏按方向转这张图）。**画进她自己帧里的**（`q_sweep`、`st_dash`）**朝右画，不用对称**（她的帧在红色方会镜像）。
> - **持续的画面**（强化期间的气流、减速、压制）只画几帧循环，Claude 导入时按时长拉开循环。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `ambessa_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、该对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/ambessa_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/ambessa_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 双刀左右开弓地砍 | `a_hit` |
| 被动「龙犬之步」 | 每放一个技能就往目标冲一步，之后几秒攻速变快、下一刀强化 | `st_dash` · `st_land` · `pw_aura` · `pw_hit` |
| 技能 1 =「狡诈横扫」→「裂地重击」 | 身前横扫半圈（刀尖扫到的多吃伤害）；扫中以后马上双刀砸地，一道裂缝沿直线往前 | `q_sweep` · `q_hit` · `q_tip` · `q2_crack` · `q2_hit` |
| 技能 2 =「割裂」 | 抡着铁链甩刀绕身一圈，打中的减速；冲刺以后再甩一圈 | `e_lash` · `e_hit` · `slow` |
| 自动放的「拒斥」 | 敌方英雄靠近时格挡（护盾），然后砸地；格挡时挨了打砸地更狠 | `w_brace` · `w_slam` · `w_hit` · `w_crit` |
| 大招 =「公开处决」 | 闪到敌方英雄身边，按住（压制），再把它砸进地里（眩晕） | `r_blink` · `r_pin` · `r_crash` |

连招：**横扫扫中 → 马上裂地重击**，**每个技能 → 龙犬之步冲刺 → 强化普攻**，**割裂 → 冲刺 → 再甩一圈**，**公开处决砸下 → 马上横扫 → 裂地重击**，拒斥也重新可用。`q_tip`、`w_crit` 只在附加包里播。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**刀光、冲击波、火星、烟尘没有黑描边，也不要用最深的颜色给形状描一圈边**。
- 每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的亮点。
- 颜色（按每条写的用）：
  - 刀光·银白：`#FFFFFF`、`#EEF1F6`、`#C6CCD8`、`#8E96A6`、`#5A6272`；
  - 火星·琥珀金：`#FFF6D6`、`#FFD67A`、`#F6A23A`、`#D2661E`、`#8A3410`；
  - 护盾·青铜金：`#FFF6CC`、`#EED088`、`#C49446`、`#865A22`、`#4E3212`；
  - 诺克萨斯·深红：`#FFE0D6`、`#F47A62`、`#CC3226`、`#8A161C`、`#4C0A10`；
  - 烟尘·暗灰褐：`#E6DED4`、`#B6AA9C`、`#807468`、`#4E4640`、`#2A2422`；
  - 碎石：`#D2C6B6`、`#A09080`、`#6E6052`、`#443A32`、`#26201C`；
- 打中、爆发居中画，不旋转；地面上的东西（冲击波、裂缝、坑、脚下的圈）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（20 张）

20 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `ambessa_fx_a_hit.png`：普攻：双刀砍中，3 帧

左右开弓的双刀砍中敌人（参考 ba_autoattacks_alpha）：中间一下白色的闪光，**两道银白色的月牙刀痕交叉成 X**，刀痕前沿是琥珀金色，边上溅开几颗琥珀色的火星。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410).
Effect: A TWIN BLADE STRIKE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 two sharp silver-white crescent cuts crossing in an X 13 across, amber-gold edges, a few amber sparks flying out at mirrored places; 3 the cuts thinner and dimmer, the sparks further out, fading. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `ambessa_fx_pw_hit.png`：龙犬之步：冲刺后强化的那一刀砍中，4 帧

龙犬之步以后强化的普攻（参考 p_specialattack_swipe_shape、p_specialattack_flow_shape）：比普通一刀大得多——**一道竖着的粗月牙刀光劈下来**，落点炸开一圈琥珀金色的火花，几块火星往上飞。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410).
Effect: A HEAVY CLEAVE, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a tall white-silver vertical crescent slash 18 squares tall coming down through the middle, pointed at both ends, amber edges; 2 an amber-gold burst of sparks 20 wide where it lands, the slash at its brightest; 3 the sparks flying up and out at mirrored places, the slash thinning; 4 a few embers drifting, fading. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 22:20 cells, image size 1408x320 (each cell 352x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `ambessa_fx_pw_aura.png`：龙犬之步：强化期间脚下的琥珀色气流，4 帧循环

冲刺以后攻速变快、下一刀强化的那几秒：她脚下**两缕琥珀色的气流**往两边打旋，几颗火星往上飘。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422).
Effect: AN EMBER STIR, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): two thin amber-gold swirls curling out from under her to both sides on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 38 wide, three small embers rising at mirrored places, a faint dark smoke wisp at each end; the swirls turn and the embers rise frame to frame so the loop flows. Sparse and light. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 40:10 cells, image size 2560x160 (each cell 640x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `ambessa_fx_st_dash.png`：龙犬之步：往前冲刺的拖影（画进她的帧），4 帧

每放完一个技能往前冲的那一步（参考 z_dash_indicator_alpha、z_chainsmask_alpha、z_generic_smoke_shape1）：她身后**拖着几道横着的银白色速度线**，两条铁链在身后甩成弧，脚下扬起一小团暗色的尘土。**朝右**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272), a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410).
Effect: A DASH TRAIL, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): 1 three long horizontal silver-white speed streaks behind her (on the cell's left), a small dark dust puff at her heels; 2 the streaks longest (30 squares), two curved dark iron chain arcs trailing behind with amber glints; 3 the streaks breaking up, the dust rolling back; 4 a few streaks and dust fading. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 44:22 cells, image size 2816x352 (each cell 704x352, 16 px a square); she stands at the cell's RIGHT part (not drawn, her feet on the cell's bottom row, her body about 26 squares wide at the right edge); everything trails behind her on the left. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `ambessa_fx_st_land.png`：龙犬之步：冲到的地方扬起的尘土，3 帧

冲刺停下的地方：脚下**一圈暗色的尘土往两边扬开**，几颗小石子和火星弹起来。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a rock ramp (#D2C6B6, #A09080, #6E6052, #443A32, #26201C).
Effect: A SKID OF DUST, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat dark dust ring 14 wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 the dust puffing out to both sides 26 wide, a few pebbles and amber sparks bouncing up at mirrored places; 3 the dust thinning, fading.
Layout: one horizontal row of 3 equal 28:10 cells, image size 1344x160 (each cell 448x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `ambessa_fx_q_sweep.png`：狡诈横扫：身前的半圈刀光（画进她的帧），4 帧

狡诈横扫（参考 q_broad_swipe_stylized_alpha、q_broad_swipe_chains_shape、q_broad_sweetspot_shape）：两把刀连着铁链**在她身前横扫出半个圆**——一道宽宽的银白色月牙刀光从她背后扫到身前，**最外面的一圈（刀尖扫到的地方）最亮、是琥珀金色**，铁链在刀光里面，火星从外圈甩出去。**朝右**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422).
Effect: A HALF-CIRCLE SWEEP, 4 frames, pointing FORWARD to the RIGHT (it is drawn into her own frames, so it needs no left-right symmetry): 1 a thin silver-white arc starting above and behind her; 2 a broad silver-white crescent sweeping round in FRONT of her (a half circle 30 squares in radius, from above her to below in front, the open side towards her), dark iron chain links inside it, its OUTER rim - the blades' edge - the brightest amber-gold; 3 the crescent complete, amber sparks thrown out from the outer rim; 4 the crescent breaking into fading streaks. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams.
Layout: one horizontal row of 4 equal 60:34 cells, image size 3840x544 (each cell 960x544, 16 px a square); she stands at the cell's LEFT part (not drawn: her feet on the cell's bottom row, the middle of her body 14 squares from the left edge, 48 tall); the half circle in front of her, to the right. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `ambessa_fx_q_hit.png`：狡诈横扫：被扫中，3 帧

被横扫扫中：一道**横着的银白色刀痕**从中间划过（两头一样尖），上下崩开几颗琥珀色的火星。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410).
Effect: A PASSING CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-silver horizontal slash 16 squares long, pointed at both ends, through the middle; 2 the slash wider with amber edges, amber sparks bursting up and down at mirrored places; 3 the sparks drifting out, fading. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal 18:14 cells, image size 864x224 (each cell 288x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `ambessa_fx_q_tip.png`：狡诈横扫：刀尖扫中（附加包），3 帧

附加包：只有被**刀尖**扫中的敌人才多吃伤害（参考 q_broad_tar_shape、q_broad_tar2_shape）：比 q_hit 更狠——**两道琥珀金色的刀痕交叉成一个大 X**（英雄联盟里就是这个 X），一圈锋利的银白色小碎光往外炸。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272).
Effect: A CRITICAL EDGE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a bright white-gold flash 8 squares across; 2 two thick amber-gold slash marks crossing in a big X 18 squares across, white cores, a ring of small sharp silver glints bursting out at mirrored places; 3 the X thinner, the glints further out, fading. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 960x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `ambessa_fx_q2_crack.png`：裂地重击：沿直线往前裂开的地面，4 帧循环

裂地重击（参考 q_precise_whipsmash_dirwave、q_precise_whip_decal_shape、q_precise_whipexposion_shape_1）：双刀砸在地上，**一道裂缝沿直线往前裂开**，裂缝里透出琥珀色的光，前头翻起碎石和尘土。**朝右飞、上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422), a rock ramp (#D2C6B6, #A09080, #6E6052, #443A32, #26201C).
Effect: A GROUND RIFT, 4 looping frames, flying RIGHT, the trail behind it on the LEFT, SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns the picture with its flight, so flying left it is upside down): a jagged crack 40 squares long along the middle line glowing amber inside, its front a burst of rock chips and dark dust thrown up and down equally, dust settling behind on the left; the rock chips rise and fall in turn so the loop surges.
Layout: one horizontal row of 4 equal 44:12 cells, image size 2816x192 (each cell 704x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `ambessa_fx_q2_hit.png`：裂地重击：被砸中，3 帧

被裂地重击砸中（参考 q_precise_whipsmash_impact_shape）：脚下**一团琥珀色的冲击往上炸**，碎石往两边飞。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a rock ramp (#D2C6B6, #A09080, #6E6052, #443A32, #26201C), a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422).
Effect: A SLAM FROM ABOVE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 an amber-gold impact burst on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 14 wide and a white flash on the target; 2 rock chips and dark dust flying up and out 18 wide at mirrored places; 3 the dust settling, fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal 18:20 cells, image size 864x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `ambessa_fx_e_lash.png`：割裂：铁链甩着刀绕身转一圈，5 帧

割裂（参考 e_swirl_sharpedge_shape、e_oneshot_ring_swipe_shape、e_swipetrail）：她抡着铁链，**两把刀在身边甩出一整圈银白色的刀光**（一圈椭圆形的旋风，外圈锋利、琥珀金色的边），铁链在里面，脚下扬起一圈暗色的尘土。她在中间不画，**身体的位置留空**。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422).
Effect: A WHIRL OF CHAINED BLADES, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Ambessa stands in the middle, not drawn: 59 squares wide (with her blades) and 48 tall - leave her body's place EMPTY: 1 two thin silver arcs starting at her sides at mirrored places; 2 a full whirling ring of silver-white crescent slashes round her (69 wide and 30 tall, an ellipse), dark iron chain links inside it, amber-gold outer edges; 3 the ring at its brightest, amber sparks thrown out at mirrored places, a dark dust ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 4 the ring breaking into streaks; 5 fading streaks and dust. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams.
Layout: one horizontal row of 5 equal 73:36 cells, image size 5840x576 (each cell 1168x576, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `ambessa_fx_e_hit.png`：割裂：被甩中，3 帧

被铁链甩来的刀割中（参考 e_oneshot_tar_dirimpact_shape）：**一道竖着的银白色月牙刀痕**加几颗琥珀色的火星。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410).
Effect: A LASH CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-silver vertical crescent slash 12 squares tall in the middle, pointed at both ends; 2 the slash with amber edges, amber sparks splashing out at mirrored places; 3 fading. her power is her two hooked crescent DRAKEHOUND BLADES on chains: sharp silver-white crescent slashes with amber-gold leading edges, amber sparks and embers thrown off, dark grey iron chain links where a chain is drawn; flat shades, crisp blade-like shapes; no magic glow, no electricity, no smooth neon beams. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `ambessa_fx_slow.png`：割裂：减速，脚下缠着的暗色尘土，4 帧循环

被割裂减速的敌人脚下：一小圈**暗色的尘土**绕着脚转，几道细细的银白色划痕一闪一闪。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422), a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272).
Effect: A HOBBLE, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat dark dust ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 16 wide and 5 tall, two short thin silver scratch marks at mirrored places flashing in turn, a dust puff going round.
Layout: one horizontal row of 4 equal 18:7 cells, image size 1152x112 (each cell 288x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `ambessa_fx_w_brace.png`：拒斥：格挡时身前的护盾光，4 帧

拒斥格挡（参考 w_shieldgradient_shape、w_parry_wind_shape、w_flash_shape）：她举刀挡住，身边**一层青铜金色的护盾光**罩住她（一个半透明的弧形外壳，边上亮、中间很淡），外面一圈风往两边卷。她在中间不画，**身体的位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold shield light ramp (#FFF6CC, #EED088, #C49446, #865A22, #4E3212), a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272).
Effect: A BRACING SHELL, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side); Ambessa stands in the middle, not drawn: 59 squares wide (with her blades) and 48 tall - leave her body's place EMPTY: 1 a bronze-gold flash at her chest 10 wide; 2 a shell of bronze-gold light round her (a tall dome 65 wide and 42 tall: only its rim drawn, bright and 2 squares thick, a few faint inner shimmer marks), thin silver wind curls at both sides at mirrored places; 3 the shell steady, the curls further out; 4 the shell flickering, thinner. Light and sparse inside: she must stay readable.
Layout: one horizontal row of 4 equal 67:44 cells, image size 4288x704 (each cell 1072x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `ambessa_fx_w_slam.png`：拒斥：双刀砸地的冲击波，5 帧

拒斥砸地（参考 w_release_shockwave_shape、w_release_ring_shape、w_distortion）：双刀砸在身边的地上，**地面炸开一圈青铜金色的冲击波**，暗色的尘土和碎石往两边溅起来。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold shield light ramp (#FFF6CC, #EED088, #C49446, #865A22, #4E3212), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422), a rock ramp (#D2C6B6, #A09080, #6E6052, #443A32, #26201C).
Effect: A SLAM SHOCKWAVE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold impact flash 16 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 a bronze-gold shock ring 36 wide, dark dust bursting up at both sides; 3 the ring 52 wide, rock chips flying up at mirrored places; 4 the rocks falling, amber cracks on the ground; 5 the cracks and the ring fading.
Layout: one horizontal row of 5 equal 54:20 cells, image size 4320x320 (each cell 864x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `ambessa_fx_w_hit.png`：拒斥：被砸地打中，3 帧

被拒斥的砸地打中：身上一下青铜金色的闪光，几块碎石往两边弹开。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold shield light ramp (#FFF6CC, #EED088, #C49446, #865A22, #4E3212), a rock ramp (#D2C6B6, #A09080, #6E6052, #443A32, #26201C).
Effect: A SHOCK HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 6 squares across on the target's chest; 2 a bronze-gold burst 14 across, rock chips bouncing out at mirrored places; 3 fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `ambessa_fx_w_crit.png`：拒斥：格挡时挨了打，砸地加强（附加包），4 帧

附加包：格挡时被敌方英雄或野怪打到，砸地就加强——打中的敌人身上**炸开一圈亮金色带一点深红的冲击**，比 w_hit 大一圈、亮一档。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a bronze-gold shield light ramp (#FFF6CC, #EED088, #C49446, #865A22, #4E3212), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a Noxian crimson ramp (#FFE0D6, #F47A62, #CC3226, #8A161C, #4C0A10).
Effect: A RETALIATION BURST, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 10 squares across; 2 a bronze-gold burst ring 20 across with crimson inner sparks at mirrored places; 3 the ring thinning, amber shards flying out; 4 fading. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal square cells, image size 1408x352 (each cell 352x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `ambessa_fx_r_blink.png`：公开处决：闪走的地方留下的暗影，4 帧

公开处决（参考 r_warning_wind_alpha、z_distortion_shape、z_generic_smoke_shape1）：她一下闪到敌人身边，原地**炸开一团暗色的烟**，几道深红色的风痕往两边卷，烟里是她身体的轮廓、正在散开。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422), a Noxian crimson ramp (#FFE0D6, #F47A62, #CC3226, #8A161C, #4C0A10).
Effect: A VANISHING, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 her silhouette's place filled with a burst of dark smoke 61 wide and 44 tall, two crimson wind streaks curling out to both sides at mirrored places; 2 the smoke bursting outward, the streaks longer; 3 the smoke thinning into curls; 4 a few wisps fading.
Layout: one horizontal row of 4 equal 65:48 cells, image size 4160x768 (each cell 1040x768, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `ambessa_fx_r_pin.png`：公开处决：被按住压制，4 帧循环

被她抓住、压制的敌人（参考 ambessa_r_marker、r_position_marker_shape1）：身上**缠着一圈深红色的光**，脚下一个深红色的标记圈，头顶两道交叉的深红色刀痕（诺克萨斯的处决标记）。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Noxian crimson ramp (#FFE0D6, #F47A62, #CC3226, #8A161C, #4C0A10), a silver-white steel ramp (#FFFFFF, #EEF1F6, #C6CCD8, #8E96A6, #5A6272).
Effect: A SUPPRESSION MARK, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a crimson ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 20 wide, a thin crimson band circling the target's waist, above its head a small crimson X of two crossed blade marks 10 squares across with silver edges; the ring and the band pulse brighter and dimmer in turn. the champion hit stands in the middle, not drawn: 16 squares wide and 36 tall.
Layout: one horizontal row of 4 equal 22:30 cells, image size 1408x480 (each cell 352x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `ambessa_fx_r_crash.png`：公开处决：把敌人砸进地里，6 帧

公开处决砸下（参考 r_hurl_impact_shape、r_hurl_impact_decal_shape、r_decalorganic_alpha、r_residual_decal_shape）：把敌人狠狠砸进地里，**地面砸出一个大坑**——一下白金色的闪光，一圈深红带琥珀色的冲击波贴着地往外推，碎石和暗色的尘土往上往两边飞，最后地上留下一圈裂开的坑。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a Noxian crimson ramp (#FFE0D6, #F47A62, #CC3226, #8A161C, #4C0A10), an amber-gold ember ramp (#FFF6D6, #FFD67A, #F6A23A, #D2661E, #8A3410), a dark smoke and dust ramp (#E6DED4, #B6AA9C, #807468, #4E4640, #2A2422), a rock ramp (#D2C6B6, #A09080, #6E6052, #443A32, #26201C).
Effect: A CRATERING SLAM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold impact flash 20 squares wide on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall); 2 a crimson and amber shock ring 40 wide on the ground, rock chips and dark dust bursting up at mirrored places; 3 the ring 60 wide, the rocks high; 4 the rocks falling, a cracked crater on the ground 30 wide with glowing amber cracks; 5 the ring thin, dust settling; 6 the crater and the cracks fading.
Layout: one horizontal row of 6 equal 64:30 cells, image size 6144x480 (each cell 1024x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `ambessa_fx_a_hit` | view_effects `league_ambessa_a_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `ambessa_fx_pw_hit` | view_effects `league_ambessa_pw_hit`（跟随目标，z 2；左右对称） | 22 × 20 |
| `ambessa_fx_pw_aura` | view_buffs `league_ambessa_pw`（tag `pw_aura`，跟随她，脚下，z -1；左右对称；约 3 秒） | 40 × 10 |
| `ambessa_fx_st_dash` | 画进她自己的 step 帧（bake_caster_fx；朝右；kit 的 st_dash 去掉） | 44 × 22 |
| `ambessa_fx_st_land` | view_effects `league_ambessa_st_land`（在落脚的地上，不跟随，z -1；左右对称） | 28 × 10 |
| `ambessa_fx_q_sweep` | 画进她自己的 skill 帧（bake_caster_fx；朝右；kit 的 q_sweep 去掉） | 60 × 34 |
| `ambessa_fx_q_hit` | view_effects `league_ambessa_q_hit`（跟随目标，z 2；左右对称） | 18 × 14 |
| `ambessa_fx_q_tip` | view_effects `league_ambessa_q_tip`（附加包播，跟随目标，z 2；左右对称） | 20 × 20 |
| `ambessa_fx_q2_crack` | view_projectiles `league_ambessa_q2_crack`（大表，直线，z 2；上下对称） | 44 × 12 |
| `ambessa_fx_q2_hit` | view_effects `league_ambessa_q2_hit`（跟随目标，z 2；左右对称） | 18 × 20 |
| `ambessa_fx_e_lash` | view_effects `league_ambessa_e_lash`（大表，跟随她，z 3；左右对称） | 73 × 36 |
| `ambessa_fx_e_hit` | view_effects `league_ambessa_e_hit`（跟随目标，z 2；左右对称） | 14 × 14 |
| `ambessa_fx_slow` | view_buffs `league_ambessa_e_slow`（tag `slow`，跟随，脚下，z -1；左右对称） | 18 × 7 |
| `ambessa_fx_w_brace` | view_effects `league_ambessa_w_brace`（跟随她，z 3；左右对称；约 0.4 秒） | 67 × 44 |
| `ambessa_fx_w_slam` | view_effects `league_ambessa_w_slam`（大表，在她身边的地上，跟随她，z -1；左右对称） | 54 × 20 |
| `ambessa_fx_w_hit` | view_effects `league_ambessa_w_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `ambessa_fx_w_crit` | view_effects `league_ambessa_w_crit`（附加包，跟随目标，z 2；左右对称） | 22 × 22 |
| `ambessa_fx_r_blink` | view_effects `league_ambessa_r_blink`（大表，在她出发的地方，不跟随，z 3；左右对称） | 65 × 48 |
| `ambessa_fx_r_pin` | view_effects `league_ambessa_r_pin`（跟随目标，z 2；左右对称；约 0.6 秒） | 22 × 30 |
| `ambessa_fx_r_crash` | view_effects `league_ambessa_r_crash`（大表，在目标的地上，不跟随，z -1；左右对称） | 64 × 30 |

- 两张表：`asset/league/effects/league_ambessa_fx`（小的）和 `league_ambessa_big`（q2_crack、e_lash、w_slam、r_blink、r_crash），tag = 名字（build_ambessa.py 的 views；e_slow 用 `slow`，pw 用 `pw_aura`）。
- 弹道（q2_crack）断言上下对称；朝前的（q_sweep、st_dash）用 tools/fix/bake_caster_fx.py 画进她的 skill / step 帧，build_ambessa.py 里的 `q_sweep`、`st_dash` 两个 view 去掉；其余断言左右对称。pw_aura 循环 pw_t，slow 循环 e_slow_t，r_pin 循环 r_sup。
- 附加包的（q_tip、w_crit）只进 `--native` 的副本（addons/league_ambessa 的 override）。
- 用 `pixel_1x/` 切格（import_zac_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
