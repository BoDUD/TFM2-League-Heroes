# 不落魔锋 亚恒：给 Codex 的特效提示词（第 3 步）

> **这一份是 16 张特效图。** 造型已定（`design/zaahen_design.png`：Q 版暗裔武士，浅蓝灰皮肤、红眼睛、两只金角、白金板甲、深宝蓝腰布、背后收拢的暗裔翅膀、比人还长的金色长刀）。亚恒在游戏里是**高清**的（每个游戏格子里约 1.75×1.75 个细像素），48 格高、50 格宽（高×宽，含长刀和翅膀）；**特效按游戏格子画**（每格 = 一个游戏像素）。
> - 大小对照 `design/zaahen_size.png`：亚恒缩到游戏里的大小、放大 4 倍，地面在红线上，上面是 10 格一段的刻度，右边是原版斗士。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里亚恒自己的特效贴图（大多是灰度形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用。
> - **特效要亮**：每道刀光、每团能量都有最亮一档或白色的高光，暗底上一眼能看见。
> - **光、能量、火焰、尘土、花瓣都没有黑描边**。
> - **围着人的画面只画外圈、脚下、头上或身后，身体位置留空**，不要盖住人。
> - **对称**：除了 W 的弹道，所有画面**严格左右对称**（逐格对称：这些画面在红色方不会镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `zaahen_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 / 255），附 `manifest.json`（每张的帧数、格子大小、对称方式）和生图原稿 `raw/`，都放在 `outputs/zaahen_fx/` 里，**最后**写 `HANDOFF.md`，再打包成 `outputs/zaahen_fx_pack_done.zip`。中间不要停，16 张都画完再交。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 长刀横扫 | `a_hit` |
| 被动「不落之志」 | 打英雄叠果决（加攻击力），叠满攻击力翻倍、Q 和 W 马上好；主包叠满给护盾，附加包是真复活（倒下 4 秒后站起来） | `p_full` · `p_aura` · `p_shield` · `rv_glow` |
| 技能 1 =「暗裔长刀」 | 两连斩并回血；再按一次是上挑，把人挑飞 | `q_hit` · `q_hit2` · `q_uphit` |
| 技能 2 =「厄影回锋」 | 往前直刺，刺中的人被拽回来、短暂眩晕；主包里接着绕身一斩（赤金突袭并进来），附加包里 E 有自己的冲刺 | `w_glaive` · `w_hit` · `e_spin` · `e_hit` |
| 大招 =「大赦」 | 展翼升空（免控、减伤），冲向英雄、插刀落地：范围伤害，每打中一个英雄回血 | `r_rise` · `r_guard` · `r_slam` · `r_hit` |

连招：**W 拽中英雄 → Q 马上好**，**Q 挑飞英雄 → 大招冷却缩短**，**大招砸中英雄 → 果决一下涨一大截**，**果决叠满 → Q、W 马上好**。

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、能量、尘土没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **都是暗裔的力量**：白金到琥珀的金光（他的长刀）、血红到深褐红的暗裔能量和花瓣、一点翅膀的深海军蓝暗部、几点白色的星光；每个形状 2–3 档平涂。
- **要亮**：每个形状都有最亮一档或白色的高光。
- 颜色（按每条写的用）：
  - 暗裔金：`#FFFFFF`、`#FFF2C2`、`#FFD45A`、`#F0A82A`、`#B8661A`；
  - 暗裔红：`#FFD0C8`、`#FF5A4A`、`#D21E2E`、`#8A0E22`、`#4A0616`；
  - 翅膀深蓝：`#C8D4FF`、`#6E7EE0`、`#33409E`、`#1C2260`、`#0E1030`；
  - 星光：`#FFFFFF`、`#D8F4FF`、`#9ED8F0`；
  - 尘土：`#E8DCC8`、`#B8A68C`、`#7E6E5A`、`#4A4036`；
- 打中、爆发居中画，不旋转；地面上的圈（冲击波、法阵、裂缝）是从斜上方看的椭圆（宽是高的 3 倍左右）。
- 画在别人身上、脚下、身后的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（16 张）

16 张的提示词都以同一段画风开头。大小写在每条里（1 个游戏像素约等于 1000 距离单位）。

### 1. `zaahen_fx_w_glaive.png`：厄影回锋：刺出去的刀光，4 帧循环

W 往前刺出去的**暗裔刀光**：一道金色的长矛形刀芒，尖头朝右，后面拖着一条暗红的能量尾，两侧几根往后弯的小倒钩（参考 w_missile、w_missilehooks：英雄联盟里它刺出去再把人钩回来）。**朝右飞，上下对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616).
Effect: A FLYING DARKIN GLAIVE THRUST, 4 looping frames, pointing RIGHT (its tail on the left), SYMMETRIC TOP TO BOTTOM in every frame, square for square (the game turns it to its flight): a long spear-shaped blade of white-gold light 14 squares long with its sharp point on the right, small backward-curving crimson hooks on both sides near the point, a tapering blood-crimson energy tail 14 squares long behind it on the left; frames 1-4 the tail rippling and the hooks glinting. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 4 equal 32:10 cells, image size 2048x160 (each cell 512x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `zaahen_fx_a_hit.png`：普攻：长刀砍中，3 帧

长刀砍中：一个金色的 X 形斩痕闪光，四周迸出几点暗红火星（参考 ba_glowstar、z_swipe）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616).
Effect: A GLAIVE STRIKE, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold X of two crossing slash marks 8 squares across; 2 the X 12 across, blood-crimson sparks bursting out at mirrored places; 3 the slashes thinning to gold lines, the sparks further out and dimming. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `zaahen_fx_q_hit.png`：暗裔长刀：第一斩，3 帧

Q 第一斩：一道横着的金色月牙斩痕（左右两头对称地往上翘），中间一下白光，暗红的血色能量从斩痕里溅出来（参考 q_glaive_mask、swipe_trail）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616).
Effect: A FIRST GLAIVE CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a level white-gold crescent slash 16 squares wide across the middle, both ends curling up at mirrored places, a white flash at its centre; 2 crimson energy spraying out of the slash up and down; 3 the slash fading to a thin gold line, the crimson drops falling. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 3 equal 20:16 cells, image size 960x256 (each cell 320x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `zaahen_fx_q_hit2.png`：暗裔长刀：第二斩，3 帧

Q 第二斩：比第一斩更大，两道金色斩痕交叉成一个大 X，交叉处一团暗红爆开，回血的感觉（一两点亮红往上飘）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616).
Effect: A SECOND GLAIVE CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 two big white-gold slashes crossing in an X 16 squares across; 2 a blood-crimson burst 12 across where they cross, a few bright red motes rising; 3 the X fading to thin gold lines, the motes drifting up. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 3 equal square cells, image size 960x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `zaahen_fx_q_uphit.png`：暗裔长刀：挑飞，5 帧

Q 再按一次的上挑：脚下地面一道金色裂缝亮起（参考 q_groundcrack），一股金色的冲击**从下往上竖着冲起来**把人挑飞，两边几片暗红的碎光往上飞。**身体位置留空**，光只在身后和两侧。**左右对称**，5 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616), a dust ramp (#E8DCC8, #B8A68C, #7E6E5A, #4A4036).
Effect: AN UPWARD GLAIVE STRIKE, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit hit stands in the middle, not drawn: 16 squares wide and 36 tall: 1 a short glowing gold crack on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 14 wide; 2 a white-gold column of force 8 wide shooting up from the crack behind the body to 30 tall, crimson shards at both sides; 3 the column at its full 40 tall with a bright tip, the shards flying higher; 4 the column thinning; 5 gold sparks and dust left at the top and bottom. The middle (the body) mostly empty. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 5 equal 20:44 cells, image size 1600x704 (each cell 320x704, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `zaahen_fx_w_hit.png`：厄影回锋：刺中、拽回，4 帧

W 刺中：一下金色的穿刺星闪，然后几根暗红的能量倒钩**从两边钩住目标**、往回收（把人拽回来的感觉）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616).
Effect: A DREADED HOOK, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold piercing star 8 squares across; 2 two curved blood-crimson hooks 6 squares long closing in from both sides at mirrored places; 3 the hooks clamped round the middle, a crimson flash; 4 the hooks fading into crimson motes. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `zaahen_fx_e_spin.png`：赤金突袭：绕身一斩，6 帧

E 的**绕身一斩**：一圈金色的刀光在他腰的高度横着扫过一整圈（一个扁扁的金色光环，前半圈亮、后半圈暗一档），外圈带一层暗红的能量边（英雄联盟里外圈伤害更高），脚下一圈金色的地面光环（参考 e_swipe_glaiveshape、e_swipe_darkintrail、e_nova）。**中间他站的位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616), a dust ramp (#E8DCC8, #B8A68C, #7E6E5A, #4A4036).
Effect: A GOLDEN SPIN SLASH AROUND HIM, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Zaahen stands in the middle, not drawn: about 50 squares wide with his glaive and wings, 48 tall: 1 a thin gold ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 40 wide; 2 a flat ring of white-gold blade light 50 wide and 14 tall at his waist height (the front half bright, the back half one step darker), its outer edge crimson; 3 the ring at full brightness, crimson energy flaring at its outer edge, gold sparks thrown out at mirrored places; 4 the ring widening to 54, thinning; 5 gold arcs breaking up, dust kicked up at the ground ring; 6 the last sparks and dust fading. The middle (his body) left empty. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 6 equal 56:30 cells, image size 5376x480 (each cell 896x480, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `zaahen_fx_e_hit.png`：赤金突袭：外圈打中，3 帧

被绕身斩的外圈打中：一道横着的金色斩痕，带一圈暗红的冲击（英雄联盟：外圈多一截最大生命的魔法伤害）。**左右对称**，3 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616).
Effect: AN AUREATE CUT, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a level white-gold slash 12 squares wide; 2 a crimson ring 10 across bursting out from its middle; 3 the slash and ring fading into gold and crimson motes. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 3 equal square cells, image size 768x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `zaahen_fx_r_rise.png`：大赦：展翼升空，6 帧

大招升空：他身后爆开一对**金红色的能量翅膀**（比他自己的翅膀更大，左右对称地张开，翅尖是金色的长羽刃），脚下一圈暗红的气浪往外推，几道金色光线往上冲（参考 p_wing_mask、r_fire_trail_up、r_screen_flames）。**中间他身体的位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616), a navy wing ramp (#C8D4FF, #6E7EE0, #33409E, #1C2260, #0E1030).
Effect: SPREADING WINGS OF LIGHT, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Zaahen stands in the middle, not drawn: about 50 squares wide with his glaive and wings, 48 tall: 1 a crimson shock ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 40 wide and gold streaks shooting up behind him; 2 a pair of huge wings of crimson and gold energy unfolding from behind his shoulders, up and out to both sides, 60 squares tip to tip, the wing tips long white-gold feather blades, deep navy shadow at the wing roots; 3 the wings fully open and blazing; 4 the wings beating down, gold sparks falling; 5 the wings fading to crimson outlines; 6 only gold motes left. The middle (his body) left empty. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 6 equal 64:56 cells, image size 6144x896 (each cell 1024x896, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `zaahen_fx_r_slam.png`：大赦：插刀落地的冲击波，8 帧

大招插进地里：落点一圈**金色的冲击波贴地往外推开**（从斜上方看的扁椭圆），地面裂开金色发光的裂缝，裂缝里往上喷暗红的能量和金色火星，尘土飞起（参考 r_slam_glow、z_cracks、ground_splash、dust_cloud）。**左右对称**，8 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616), a dust ramp (#E8DCC8, #B8A68C, #7E6E5A, #4A4036).
Effect: A GRIM DELIVERANCE SLAM, 8 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold flash 10 wide at the middle of the ground; 2 a gold shock ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 24 wide, glowing gold cracks running out from the middle; 3 the ring 40 wide, blood-crimson energy and gold sparks bursting up from the cracks; 4 the ring 54 wide, dust thrown up at its edge; 5 the ring 60 wide and thinning, the cracks still glowing; 6 the cracks dimming to amber, the dust settling; 7 dark cracks and drifting dust; 8 the last motes fading. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 8 equal 64:34 cells, image size 8192x544 (each cell 1024x544, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `zaahen_fx_r_hit.png`：大赦：被砸中，4 帧

被大招砸中：一下金色的爆光，暗红的能量往四周溅开，然后几点亮红往他那边飘（回血）。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616).
Effect: A DELIVERANCE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-gold burst 10 squares across; 2 blood-crimson energy splashing out at mirrored places 16 across; 3 the splash breaking into crimson drops; 4 bright red motes drifting up. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 4 equal 18:20 cells, image size 1152x320 (each cell 288x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `zaahen_fx_r_guard.png`：大赦：施法时的金光护体，4 帧循环

放大招期间（免控、减伤）：身体外圈一层淡淡的金色光边，几点金色火星绕着他转。**身体位置留空**。**左右对称**，4 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a starlight ramp (#FFFFFF, #D8F4FF, #9ED8F0).
Effect: A GOLDEN GUARD, 4 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Zaahen stands in the middle, not drawn: about 50 squares wide with his glaive and wings, 48 tall: a thin broken outline of white-gold light 40 wide and 46 tall around him, a few gold sparks circling him at mirrored places; frames 1-4 the sparks moving round and the outline shimmering. The middle (his body) left empty. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 4 equal 44:50 cells, image size 2816x800 (each cell 704x800, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `zaahen_fx_p_full.png`：不落之志：果决叠满，6 帧

果决叠满的一刻：他身上爆开一圈金红色的光，背后一闪而过一对金色的翅膀轮廓，几道光往上冲（Q、W 马上好了）。**身体位置留空**。**左右对称**，6 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616), a starlight ramp (#FFFFFF, #D8F4FF, #9ED8F0).
Effect: DETERMINATION FULL, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Zaahen stands in the middle, not drawn: about 50 squares wide with his glaive and wings, 48 tall: 1 a crimson ring on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 30 wide; 2 a burst of white-gold light around him 40 wide; 3 the outline of a pair of golden wings flashing behind his shoulders, up and out, 40 tip to tip; 4 gold streaks shooting up at mirrored places; 5 the wings fading, starlight glints; 6 gold motes left. The middle (his body) left empty. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 6 equal 44:52 cells, image size 4224x832 (each cell 704x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `zaahen_fx_p_aura.png`：不落之志：叠满时身上的暗裔气焰，6 帧循环

果决叠满期间：他身后、脚下燃着暗红和金色的气焰，像暗裔的火往上窜（参考 flames、emote_flames）。**画在他身后，身体位置留空**。**左右对称**，6 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616), a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A).
Effect: A DARKIN AURA, 6 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Zaahen stands in the middle, not drawn: about 50 squares wide with his glaive and wings, 48 tall: a ring of crimson flame on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 36 wide, tongues of crimson and gold flame rising behind him to 46 tall at mirrored places; frames 1-6 the tongues flickering up in turn. The middle (his body) left empty. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 6 equal 44:52 cells, image size 4224x832 (each cell 704x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `zaahen_fx_p_shield.png`：不落之志（主包）：叠满时的金色护盾，4 帧

主包叠满时给一个护盾（附加包是真复活）：一层金色的蛋形护盾罩住他，护盾上几道暗红的纹路一亮，然后淡成一层薄光。**身体位置留空**。**左右对称**，4 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616).
Effect: A DARKIN SHELL, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Zaahen stands in the middle, not drawn: about 50 squares wide with his glaive and wings, 48 tall: 1 a white-gold egg-shaped shell outline 40 wide and 48 tall around him; 2 the shell bright with crimson rune lines on it at mirrored places; 3 the lines fading; 4 a thin gold shimmer left. The middle (his body) left empty. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 4 equal 44:52 cells, image size 2816x832 (each cell 704x832, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `zaahen_fx_rv_glow.png`：不落之志（附加包）：复活时的光，8 帧循环

附加包的复活（他倒下后 4 秒内无敌、选不中，再站起来）：一道**金色的光柱从地面往上照**，里面飘着暗红的花瓣（亚托克斯那种暗裔花瓣，参考 r_petal_amber），脚下一圈金红的法阵慢慢转（参考 p_revive_energystreak）。**中间他身体的位置留空**（他跪着、慢慢站起来）。**左右对称**，8 帧循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, energy, dust, smoke, rings or shockwaves, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a darkin gold ramp (#FFFFFF, #FFF2C2, #FFD45A, #F0A82A, #B8661A), a darkin crimson ramp (#FFD0C8, #FF5A4A, #D21E2E, #8A0E22, #4A0616), a starlight ramp (#FFFFFF, #D8F4FF, #9ED8F0).
Effect: A DARKIN RESURRECTION LIGHT, 8 looping frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), Zaahen stands in the middle, not drawn: about 50 squares wide with his glaive and wings, 48 tall (kneeling, then rising): a ring of gold and crimson runes on the GROUND under the unit's feet (an ellipse seen from above, three times as wide as tall) 44 wide; a column of soft white-gold light 30 wide rising from it to the top of the cell, brighter at its edges; blood-crimson petals drifting up inside the column at mirrored places; frames 1-8 the runes turning, the petals rising and the column's edges shimmering. The middle (his body) left empty. everything is DARKIN POWER: blazing white-gold to amber light (his glaive), blood-crimson energy and petals, a touch of deep navy shadow from his wings, a few white starlight glints; flat shades, crisp shapes; no smooth neon beams, no green, no purple.
Layout: one horizontal row of 8 equal 56:70 cells, image size 7168x1120 (each cell 896x1120, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `zaahen_fx_w_glaive` | view_projectiles `league_zaahen_w_glaive`（弹道，z 2；朝右、上下对称） | 32 × 10 |
| `zaahen_fx_a_hit` | view_effects `league_zaahen_a_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `zaahen_fx_q_hit` | view_effects `league_zaahen_q_hit`（跟随目标，z 2；左右对称） | 20 × 16 |
| `zaahen_fx_q_hit2` | view_effects `league_zaahen_q_hit2`（跟随目标，z 2；左右对称） | 20 × 20 |
| `zaahen_fx_q_uphit` | view_effects `league_zaahen_q_uphit`（跟随目标，z 2；左右对称） | 20 × 44 |
| `zaahen_fx_w_hit` | view_effects `league_zaahen_w_hit`（跟随目标，z 2；左右对称） | 18 × 18 |
| `zaahen_fx_e_spin` | view_effects `league_zaahen_e_spin`（大表，在亚恒脚下，z 1，不跟随；左右对称） | 56 × 30 |
| `zaahen_fx_e_hit` | view_effects `league_zaahen_e_hit`（跟随目标，z 2；左右对称） | 16 × 16 |
| `zaahen_fx_r_rise` | view_effects `league_zaahen_r_rise`（大表，跟随亚恒，z 1；左右对称） | 64 × 56 |
| `zaahen_fx_r_slam` | view_effects `league_zaahen_r_slam`（大表，落点，z -1，不跟随；左右对称） | 64 × 34 |
| `zaahen_fx_r_hit` | view_effects `league_zaahen_r_hit`（跟随目标，z 2；左右对称） | 18 × 20 |
| `zaahen_fx_r_guard` | view_buffs `league_zaahen_r_guard`（跟随亚恒，z 3；左右对称） | 44 × 50 |
| `zaahen_fx_p_full` | view_effects `league_zaahen_p_full`（跟随亚恒，z 2；左右对称） | 44 × 52 |
| `zaahen_fx_p_aura` | view_buffs `league_zaahen_full`（跟随亚恒，z -1，在他身后；左右对称） | 44 × 52 |
| `zaahen_fx_p_shield` | view_effects `league_zaahen_p_shield`（跟随亚恒，z 2；左右对称） | 44 × 52 |
| `zaahen_fx_rv_glow` | 复活画面 `rv_rise` 的光（我把它和他跪起的动作帧合成，大表；左右对称） | 56 × 70 |

- 两张表：`asset/league/effects/league_zaahen_fx`（小的）和 `league_zaahen_big`（e_spin、r_rise、r_slam、rv_glow），tag = 名字（`p_aura` 的 tag 绑在 view_buffs `league_zaahen_full` 上；`rv_glow` 和他 d_down → rv_kneel → B 的帧合成 `rv_rise`，附加包禁锢期间播它）。
- 弹道（w_glaive）断言上下对称；其余断言左右对称。
- 用 `pixel_1x/` 切格（import_trundle_fx 的做法）；核对交回的张数和这份清单；和 `raw/` 原稿对照读回（必要时从 raw/ 读回）。
