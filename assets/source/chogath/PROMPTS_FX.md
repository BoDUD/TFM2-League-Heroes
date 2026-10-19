# 虚空恐惧 科加斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 15 张特效图。** 造型和动作已定（`design/chogath_idle.png`：3/4 正面朝右、四肢着地的虚空巨兽，深紫甲壳、酒红甲片，大嘴里两排白牙、紫舌头、青色眼睛，背上两条镰刀臂）。他在游戏里是**高清**的（每个游戏格子里 1.2×1.2 个细像素），38 格高、57 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 大小对照 `design/chogath_size.png`：他的待机放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/chogath_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效出现在哪里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里科加斯自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**虚空的紫色和品红**（破裂的地刺和光、恐惧之刺、盛宴的漩涡），**破裂掀起土黄色的碎石**，**野性尖叫是蓝紫色的声波**，**盛宴是一圈红色的牙咬下去**，**被动回血是常见的绿色**。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的画面只画外圈、脚下或头上，身体位置留空**，不要盖住人。
> - **对称**：13 张严格**左右对称**（逐格对称：这些画面在红色方不会镜像）；两张弹道图（`e_pic` 尖刺、`w_wave` 声波）**朝右画、上下对称**（游戏把它们转到飞行方向，往左时上下颠倒）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `chogath_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json`（每张的帧数、每格大小 `cell_1x`、对称方式）和生图原稿 `raw/`，都放在 `outputs/chogath_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/chogath_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。中间不要停，全部画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻（被动「肉食者」和 E「恐惧之刺」在里面） | 直立起来再扑下来砸；打死单位回血；每 6 秒接下来 3 次攻击射出一排尖刺 | `a_hit` · `p_heal` · `e_arm` · `e_pic` · `e_hit` · `e_slow` |
| 技能 1 = Q「破裂」 | 目标点地面裂开，0.6 秒后冲出地刺，击飞、减速 | `q_crack` · `q_spikes` · `q_hit` · `q_slow` |
| 技能 2 = W「野性尖叫」 | 朝前方扇形尖叫，魔法伤害、沉默 | `w_wave` · `w_hit` · `w_sil` |
| 大招「盛宴」 | 咬一口受伤的敌方英雄，吃死就叠一层、身体变大 | `r_hit` · `r_grow` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、声波、光环、冲击波都没有黑描边，也不要用最深的颜色给形状描一圈边**（实心的东西例外：地刺、尖刺、碎石可以有一圈深色边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 虚空的紫色 / 品红光：`#FFFFFF`、`#F8D0FF`、`#E27CFF`、`#B640EE`、`#7A22B8`、`#44127A`；
  - 实心的虚空尖刺：`#F4E0FF`、`#C890F0`、`#9A58D0`、`#6A3098`、`#3E1A60`、`#22102E`；
  - 碎石（实心）：`#E6D2AA`、`#C2A470`、`#927448`、`#60482C`、`#34261A`；
  - 蓝紫色声波：`#FFFFFF`、`#DCE6FF`、`#A0B6FF`、`#6E78F2`、`#4C3ECA`、`#2C1E84`；
  - 盛宴的红牙：`#FFFFFF`、`#FFD0D0`、`#FF6E6E`、`#E42A3A`、`#A41426`、`#5C0A16`；
  - 回血的绿色：`#FFFFFF`、`#DAFFD2`、`#90F088`、`#42C858`、`#1E8A3A`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–4 倍）。
- 画在别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（15 张）

15 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位：破裂的半径 25000，尖叫的扇形 55000 长，尖刺的直线 50000 长、17000 宽）。

### 1. `chogath_fx_a_hit.png`：普攻：直立后扑下来砸中目标，3 帧

他直立起来、整个扑下来砸中目标的一下：一团紫白色的冲击闪光，四道短短的紫色爪痕往外劈开，溅出几点品红（参考 flash、r_spike_slash、z_sparks）。**左右对称**，约 16 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A).
Effect: A HEAVY VOID IMPACT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-violet burst 8 squares across with 4 short magenta claw streaks slashing outward diagonally (mirrored pairs); 2 the burst 12 squares across, the streaks longer, 6 magenta sparks (1-2 squares) flying out; 3 only a fading violet ring 14 squares across and the sparks further out.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `chogath_fx_p_heal.png`：被动肉食者：吃掉小兵回血（他身上，跟随），4 帧

他的攻击打死一个单位、回血的一下：他身上冒起一圈绿色的十字小光点，往上飘，中间一团淡淡的紫色虚空雾一闪（参考 z_star、z_glow、mist）。**只画他身上、往上飘的光点，身体轮廓不要画**（the void beast stands in the middle, not drawn: 38 squares from his raised scythe tips to the ground, about 58 squares wide, his body a low mass 24 squares tall）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green heal ramp (#FFFFFF, #DAFFD2, #90F088, #42C858, #1E8A3A) and a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A).
Effect: A HEAL over a big beast, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the void beast stands in the middle, not drawn: 38 squares from his raised scythe tips to the ground, about 58 squares wide, his body a low mass 24 squares tall): 1 a faint violet puff 14 squares across in the middle and 6 small green plus-shaped sparkles (3x3) round it at mirrored places 6-14 squares up; 2 the sparkles 4 squares higher, white cores, the puff fading; 3 the sparkles 8 squares higher and smaller; 4 only 4 tiny green dots near the top.
Layout: one horizontal row of 4 equal 40:36 cells, image size 2560x576 (each cell 640x576, 16 px a square); centered across, the cell's bottom row is the ground under him (the sparkles' lowest row 6 squares above it). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `chogath_fx_e_arm.png`：E 恐惧之刺：背上的刺充能（他身上，跟随），4 帧

恐惧之刺准备好的一下（接下来 3 次攻击会射刺）：他背上一排尖刺亮起紫红色的光，一圈紫色的光从背上往外一闪（参考 e_cas_glowmask、e_cas_spikes_mult、e_swirltrail）。**只画背上那一排亮起的刺和外圈的光，身体留空**（the void beast stands in the middle, not drawn: 38 squares from his raised scythe tips to the ground, about 58 squares wide, his body a low mass 24 squares tall，背在 18–24 格高）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A) and a solid void spike ramp (#F4E0FF, #C890F0, #9A58D0, #6A3098, #3E1A60, #22102E; spikes are solid: a dark edge allowed).
Effect: SPIKES LIGHTING UP along a beast's back, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the void beast stands in the middle, not drawn: 38 squares from his raised scythe tips to the ground, about 58 squares wide, his body a low mass 24 squares tall, his back 18-24 squares up): 1 a row of 7 small glowing violet spike tips (2 squares wide, 4 tall, pointing up) along an arc 40 squares wide, 20-26 squares up; 2 the tips magenta with white cores, a thin violet arc of light under them; 3 the arc flaring 4 squares outward, the tips brightest; 4 only the tips, dimmer.
Layout: one horizontal row of 4 equal 48:30 cells, image size 3072x480 (each cell 768x480, 16 px a square); centered across, the cell's bottom row is the ground under him (the arc's middle 20 squares above it). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `chogath_fx_e_pic.png`：E：一排尖刺飞出去（弹道，转向飞行方向），4 帧

攻击时射出的一排尖刺：从左边（他嘴前）往右飞出去的 5–6 根紫色尖刺，每根后面拖一道品红的光尾，刺尖朝右（参考 e_cas_spikes_mult、e_trail、directionalshapes）。**朝右画、上下对称**（游戏会把它转到飞行方向，往左射时上下颠倒）。4 帧：刺从左往右飞过整条线。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a solid void spike ramp (#F4E0FF, #C890F0, #9A58D0, #6A3098, #3E1A60, #22102E; spikes are solid: a dark edge allowed) and a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A).
Effect: A VOLLEY OF FLYING SPIKES, 4 frames, POINTING RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to the way it flies, so cast to the left it is turned upside down): 5 solid violet spikes (each 6 squares long, 2 tall, the point to the right) in a fan 14 squares tall, each with a magenta light trail behind it; 1 the spikes at the cell's left quarter, trails short; 2 at the middle, trails 10 squares; 3 at the right quarter, trails 14; 4 at the right edge, the trails fading behind them.
Layout: one horizontal row of 4 equal 52:18 cells, image size 3328x288 (each cell 832x288, 16 px a square); the fan's middle on the cell's middle row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `chogath_fx_e_hit.png`：E：被尖刺打中的敌人身上，3 帧

被尖刺打中：几根紫色的小刺扎上去碎开，一点品红的闪光（参考 flash、z_sparks）。**左右对称**，约 14 × 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a solid void spike ramp (#F4E0FF, #C890F0, #9A58D0, #6A3098, #3E1A60, #22102E; spikes are solid: a dark edge allowed) and a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A).
Effect: A SPIKE HIT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a magenta-white flash 6 squares across; 2 the flash 9 across, 4 small violet spike shards (2 squares) breaking off outward at mirrored places; 3 the shards further out, the flash fading.
Layout: one horizontal row of 3 equal square cells, image size 672x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `chogath_fx_e_slow.png`：E：被减速的敌人脚下扎着的刺（循环），2 帧

被恐惧之刺减速的敌人脚下：地上扎着几根紫色的小刺，刺尖一明一暗（参考 e_cas_spikes_mult）。**左右对称**，2 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a solid void spike ramp (#F4E0FF, #C890F0, #9A58D0, #6A3098, #3E1A60, #22102E; spikes are solid: a dark edge allowed) and a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A).
Effect: SPIKES STUCK IN THE GROUND round a unit's feet, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 6 small solid violet spikes (1-2 squares wide, 3-4 tall, slanting outward) on a flat ellipse 16 squares wide and 5 tall; 1 their tips dim; 2 their tips glowing magenta.
Layout: one horizontal row of 2 equal 18:8 cells, image size 576x128 (each cell 288x128, 16 px a square); centered across, the spikes' feet on the cell's bottom rows. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `chogath_fx_q_crack.png`：Q 破裂：目标点地面裂开（地上，不跟随，0.6 秒后地刺冲出），6 帧

破裂的预警：目标点的地面上，一圈裂缝从中间往外裂开（半径约 25 格，地上的椭圆），裂缝里透出紫色和品红的光，越来越亮，几粒碎石在裂缝边跳起来（参考 q_cas_spikegradient、w_grounddecalfinal、q_rockshards）。**左右对称**，6 帧（约 0.6 秒）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A) and a rock ramp (#E6D2AA, #C2A470, #927448, #60482C, #34261A; rocks are solid: a dark edge allowed).
Effect: THE GROUND CRACKING OPEN, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small glowing violet crack star in the middle (6 short cracks, 10 squares across); 2 the cracks 24 squares across, magenta glow in them; 3 the cracks reaching an ellipse 40 wide and 14 tall, a faint violet glow filling it; 4 the cracks 50 wide and 18 tall, brighter, 4 small rock grains (2x2, solid) hopping at their edges; 5 the whole ellipse glowing, the cracks white-magenta; 6 the brightest, about to burst. Flat on the ground, nothing tall.
Layout: one horizontal row of 6 equal 54:20 cells, image size 5184x320 (each cell 864x320, 16 px a square); centered across, the ellipse's middle 9 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `chogath_fx_q_spikes.png`：Q：地刺冲出（地上，不跟随），6 帧

裂开的地面里冲出一丛紫色的巨大地刺（中间最高约 30 格，两边矮），刺上流着品红的光，碎石和土块往外飞，之后地刺缩回地里（参考 q_cas_spikegradient、r_indicator_spikes、q_rockshards）。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a solid void spike ramp (#F4E0FF, #C890F0, #9A58D0, #6A3098, #3E1A60, #22102E; spikes are solid: a dark edge allowed), a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A) and a rock ramp (#E6D2AA, #C2A470, #927448, #60482C, #34261A; rocks are solid: a dark edge allowed).
Effect: GIANT VOID SPIKES BURSTING FROM THE GROUND, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flash of magenta light on the ground (an ellipse 40 wide and 12 tall); 2 a cluster of 7 solid violet spikes shooting up from it (the middle one 22 squares tall, the side ones 10-16, slanting outward), magenta light running up their edges; 3 the spikes at full height (the middle one 32 squares), 8 rock chunks (2-3 squares, solid) flying up and out at mirrored places; 4 the spikes still, the rocks higher; 5 the spikes sinking back (half height), the rocks falling; 6 only spike stubs and dust puffs on the ground.
Layout: one horizontal row of 6 equal 56:46 cells, image size 5376x736 (each cell 896x736, 16 px a square); centered across, the spikes' feet 8 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `chogath_fx_q_hit.png`：Q：被地刺顶飞的敌人身上，3 帧

被地刺顶飞的敌人：一团紫色的冲击闪光，几块碎石往外飞（参考 flash、q_rockshards）。**左右对称**，约 16 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A) and a rock ramp (#E6D2AA, #C2A470, #927448, #60482C, #34261A; rocks are solid: a dark edge allowed).
Effect: AN UPWARD IMPACT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a violet-white flash 7 squares across; 2 the flash 11 across, 4 rock chips (2x2, solid) flying up and out at mirrored places; 3 the flash fading, the chips further out.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `chogath_fx_q_slow.png`：Q：被减速的敌人脚下裂开的地面（循环），2 帧

被破裂减速的敌人脚下：一小片裂开的地面，裂缝里透着紫光，一明一暗（参考 w_grounddecalfinal）。**左右对称**，2 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a rock ramp (#E6D2AA, #C2A470, #927448, #60482C, #34261A; rocks are solid: a dark edge allowed) and a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A).
Effect: CRACKED GROUND GLOWING VIOLET at a unit's feet, 2 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat patch of dark cracked earth (an ellipse 18 wide and 6 tall) with 5 thin glowing cracks; 1 the cracks dim violet; 2 the cracks bright magenta.
Layout: one horizontal row of 2 equal 20:8 cells, image size 640x128 (each cell 320x128, 16 px a square); centered across, the ellipse's bottom on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `chogath_fx_w_wave.png`：W 野性尖叫：往前一扇形的声波（弹道，转向前方），5 帧

他直立起来朝前尖叫：从左边（他的嘴）往右扩散的一扇蓝紫色声波（60° 的扇形，最远约 55 格），几道弧形的声浪一层层往外推，夹着几道短短的冲击条纹（参考 w_cas_coneaoe、w_cas_soundring、w_chogath_distortion_waves、w_sound_waves_styled_impact）。**朝右画、上下对称**（游戏会把它转到他面对的方向）。5 帧：声浪从左往右推出去。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet sound ramp (#FFFFFF, #DCE6FF, #A0B6FF, #6E78F2, #4C3ECA, #2C1E84).
Effect: A CONE OF SOUND WAVES, 5 frames, POINTING RIGHT and SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to the way it flies, so cast to the left it is turned upside down): a 60-degree cone opening from the middle of the cell's left edge to the right, filled by curved wave arcs (each 2 squares thick, white cores, curving like ')' ); 1 two small arcs near the left edge; 2 three arcs reaching 20 squares out; 3 four arcs reaching 38 squares out, 6 short straight streaks between them; 4 the arcs reaching the right edge, the nearest ones fading; 5 only the 2 farthest arcs, faint.
Layout: one horizontal row of 5 equal 56:32 cells, image size 4480x512 (each cell 896x512, 16 px a square); the cone's tip on the middle of the cell's left edge. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `chogath_fx_w_hit.png`：W：被尖叫打中的敌人身上，3 帧

被尖叫打中：一圈蓝紫色的声波环在他身上炸开（参考 w_soundwave_blue_hit、w_cas_soundringwhite）。**左右对称**，约 16 × 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet sound ramp (#FFFFFF, #DCE6FF, #A0B6FF, #6E78F2, #4C3ECA, #2C1E84).
Effect: A SOUND RING BURST, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-blue ring 6 squares across; 2 two rings, 9 and 13 across, the inner brighter; 3 one faint ring 15 across.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `chogath_fx_w_sil.png`：W：被沉默的敌人头上（循环），4 帧

被沉默期间敌人头上：一个蓝紫色的小声波圈，中间一道斜杠（禁止说话的标记），一明一暗（参考 w_cas_soundringwhite）。**画在头上**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn，标记在 36–44 格高）。**左右对称**（斜杠用竖杠或 X 保持对称）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a blue-violet sound ramp (#FFFFFF, #DCE6FF, #A0B6FF, #6E78F2, #4C3ECA, #2C1E84).
Effect: A SILENCE MARK over a unit's head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a small blue-violet ring 8 squares across (2 squares thick, white core) with an X of 1-square lines inside it; frames 2 and 3 the ring a shade brighter and 1 square bigger, frame 4 back to frame 1.
Layout: one horizontal row of 4 equal 12:10 cells, image size 768x160 (each cell 192x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `chogath_fx_r_hit.png`：R 盛宴：一口咬下去（被咬的敌人身上，跟随），5 帧

盛宴咬下的一口：一圈红色的牙从上下两边合拢咬住敌人（上排、下排两排尖牙），中间一团紫色的虚空漩涡（参考 r_tooth_target_ring、r_tar_voidswirl、r_tar_voidplasmas）。**左右对称**（an upright champion 16 squares wide and 36 tall stands in the middle, not drawn），5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a red teeth-ring ramp (#FFFFFF, #FFD0D0, #FF6E6E, #E42A3A, #A41426, #5C0A16) and a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A).
Effect: A GIANT BITE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright champion 16 squares wide and 36 tall stands in the middle, not drawn): 1 a red ring of teeth wide open round it (an upper row of 7 white fangs 3 squares long pointing down along an arc 28 squares wide, 30 squares up, and a lower row pointing up along an arc 2 squares up); 2 the two rows closing to 22 and 8 squares up, a violet swirl filling the middle; 3 the rows meeting at 15 squares up, the swirl bright magenta; 4 the teeth gone, the swirl collapsing inward; 5 only a fading violet spark in the middle.
Layout: one horizontal row of 5 equal 32:34 cells, image size 2560x544 (each cell 512x544, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `chogath_fx_r_grow.png`：R：吃掉英雄、身体变大（他身上，跟随），5 帧

盛宴吃死一个英雄、叠一层变大的一下：他身体外面一圈紫色的虚空能量往上冒，一圈品红的光环从他身上往外一胀，几缕虚空的火苗往上飘（参考 r_tar_voidwisps、r_tar_voidplasmas、z_glow）。**只画外圈，身体留空**（the void beast stands in the middle, not drawn: 38 squares from his raised scythe tips to the ground, about 58 squares wide, his body a low mass 24 squares tall）。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, sound, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a void violet-magenta light ramp (#FFFFFF, #F8D0FF, #E27CFF, #B640EE, #7A22B8, #44127A).
Effect: A VOID SURGE round a big beast, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (the void beast stands in the middle, not drawn: 38 squares from his raised scythe tips to the ground, about 58 squares wide, his body a low mass 24 squares tall): 1 a thin magenta outline of light round an empty oval 56 squares wide and 30 tall (his body); 2 the outline 2 squares thick and 4 squares outside it, 8 violet flame wisps (3 squares wide, 6 tall) rising from it at mirrored places; 3 the ring swelling to 62 wide and 36 tall, the wisps higher with white tips; 4 the ring fading, the wisps at the top; 5 only 4 small wisps near the top.
Layout: one horizontal row of 5 equal 64:48 cells, image size 5120x768 (each cell 1024x768, 16 px a square); centered across, the cell's bottom row is the ground under him (the oval's bottom on it). Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `chogath_fx_a_hit` | view_effects `league_chogath_a_hit`（跟随目标，画在人物上面 z 2；左右对称） | 16 × 16 |
| `chogath_fx_p_heal` | view_effects `league_chogath_p_heal`（跟随，画在人物上面 z 2；左右对称） | 40 × 36 |
| `chogath_fx_e_arm` | view_effects `league_chogath_e_arm`（跟随，画在人物上面 z 2；左右对称） | 48 × 30 |
| `chogath_fx_e_pic` | view_projectiles `league_chogath_e_pic`（只画图的直线，长 50 宽 17，画在直线中点，跟着方向转；上下对称） | 52 × 18 |
| `chogath_fx_e_hit` | view_effects `league_chogath_e_hit`（跟随敌人，画在人物上面 z 2；左右对称） | 14 × 14 |
| `chogath_fx_e_slow` | view_buffs `league_chogath_e_slow`（跟随，画在人物下面 z 3；左右对称；循环，1.5 秒） | 18 × 8 |
| `chogath_fx_q_crack` | view_effects `league_chogath_q_crack`（不跟随，画在人物下面 z -1；左右对称；大图表） | 54 × 20 |
| `chogath_fx_q_spikes` | view_effects `league_chogath_q_spikes`（不跟随，画在人物上面 z 3；左右对称；大图表） | 56 × 46 |
| `chogath_fx_q_hit` | view_effects `league_chogath_q_hit`（跟随敌人，画在人物上面 z 2；左右对称） | 16 × 16 |
| `chogath_fx_q_slow` | view_buffs `league_chogath_q_slow`（跟随，画在人物下面 z 3；左右对称；循环，1.5 秒） | 20 × 8 |
| `chogath_fx_w_wave` | view_projectiles `league_chogath_w_wave`（只画图的直线，长 55，画在直线中点，跟着方向转；上下对称；大图表） | 56 × 32 |
| `chogath_fx_w_hit` | view_effects `league_chogath_w_hit`（跟随敌人，画在人物上面 z 2；左右对称） | 16 × 16 |
| `chogath_fx_w_sil` | view_buffs `league_chogath_w_sil`（跟随，画在人物上面 z 3；左右对称；循环，1.8 秒） | 12 × 10 |
| `chogath_fx_r_hit` | view_effects `league_chogath_r_hit`（跟随敌人，画在人物上面 z 2；左右对称；大图表） | 32 × 34 |
| `chogath_fx_r_grow` | view_effects `league_chogath_r_grow`（跟随，画在人物上面 z 2；左右对称；大图表） | 64 × 48 |

- 两张表：`asset/league/effects/league_chogath_fx`（小的）和 `league_chogath_big`（q_crack、q_spikes、w_wave、r_hit、r_grow），tag = 名字（build_chogath.py 的 views）。
- `e_pic` / `w_wave` 是只画图的直线（Ally，没有效果）上的画面，直线的持续时间（build_chogath P e_pic_t / w_pic_t）要等于画面的时长；画在直线中点、跟着方向转，所以上下对称、朝右。`q_crack` / `q_spikes` 不跟随（地上的点）。其余跟随、左右对称。
- 用 `pixel_1x/` 切格（import_rammus_fx 的做法），断言对称；清掉 Codex 给光描的最深色边（尖刺、碎石保留描边）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
