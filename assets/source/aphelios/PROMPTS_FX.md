# 残月之肃 厄斐琉斯：给 Codex 的特效提示词（第 3 步）

> **这一份是 28 张特效图。** 造型和动作已定（`design/aphelios_idle.png`：3/4 正面朝右，清瘦，黑发遮一只眼，灰蓝长外套、宽青绿围巾，背上靠着冰蓝色的长枪通碧）。他在游戏里是**高清**的（每个游戏格子里 1.5×1.5 个细像素），连背上的通碧 47 格高、18 格宽；**特效照常按游戏格子画**（1 格 = 1 个游戏像素），不用画成高清。
> - 他有**五把月石武器**，每把在英雄联盟里有自己的颜色，特效照这个配色：**通碧 月绿色**、**断魄 血红色**、**坠明 紫色**、**荧焰 天蓝色火焰**、**折镜 银白色**；换武器和大招是**淡蓝白的月光**（他姐姐 Alune 的月光）。
> - 大小对照 `design/aphelios_size.png`：他的待机放大 4 倍，脚底在红线上，上面是 10 格一段的刻度，右边是原版斗士。每条写的大小都是游戏像素（格）。
> - `design/aphelios_shots.png`：定稿动作（4 倍），青色十字是他的站位点；每张写了特效从哪里出来。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里厄斐琉斯自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。
> - **特效要亮**：每团光都要有白色或最亮一档的芯，暗底上一眼能看见。
> - **围着人的光只画外圈和两边，中间身体位置留空**，要淡一点，不要盖住他。
> - **方向（重要，红色方不会镜像）**：飞出去的子弹、光束、月光弹画成朝右，**上下对称**（往左时会上下翻）。折镜的哨塔要**中心对称**（转 180 度后和自己一样）。荧焰的余晖波和枪口火光画成朝右（有方向）。其余所有画面（打中、身上、脚下、地上）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）。
> - 每张生成后按格子取回（每格取多数颜色），交付 8 倍的 `aphelios_fx_<名字>.png` 和原尺寸的 `pixel_1x/`（严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入），附 `HANDOFF.md`、`manifest.json` 和生图原稿 `raw/`，打包成 `aphelios_fx_pack_done.zip`。**请用生图画，不要用代码拼方块**。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 | 主手武器开火：通碧狙击弹、断魄镰刃弹、坠明重力弹（减速）、荧焰蓝焰弹（溅射）、折镜回旋刃（叠层）；每把 20 发，打空换下一把 | `a_cal` · `a_sev` · `a_grav` · `a_inf` · `a_cre` · `a_hit` · `muzzle` · `swap` · `mw` · `g_slow` · `cre` |
| 技能 1 = Q「武器技能」 | 通碧狙杀（月痕 + 追射）、断魄恒月强袭（加速连射）、坠明引力枷锁（定身）、荧焰余晖波（扇形波 + 副手追击）、折镜驻灵哨卫（哨塔） | `q_c_shot` · `q_c_hit` · `q_c_pop` · `q_s_on` · `q_s_hit` · `q_s_haste` · `off_bolt` · `q_g_cast` · `q_g_hit` · `q_i_wave` · `q_i_hit` · `q_r_turret` · `q_r_hit` |
| 技能 2 = W「月相轮转」 | 主手和副手交换 | `swap` |
| 大招「清辉夜凝」 | 射出月光，在第一个英雄处爆炸，再按主手武器加效果 | `r_cast` · `r_moon` · `r_boom` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、子弹、火、烟、火星、星星、冲击环都没有黑描边，也不要用最深的颜色给形状描一圈边**（回旋刃、哨塔的飞轮例外：可以有一圈深银色的边）。
- **要亮**：每个光的形状都有白色或最亮一档的芯。
- 颜色（按每条写的用）：
  - 月绿（通碧）：`#FFFFFF`、`#DFFFF2`、`#93F5CB`、`#43DBA2`、`#1F9E7A`、`#0F5B4B`；
  - 血红（断魄）：`#FFFFFF`、`#FFD9D9`、`#FF8080`、`#E8394A`、`#A31D35`、`#5C0F22`；
  - 紫（坠明）：`#FFFFFF`、`#E8D9FF`、`#B78FFF`、`#7B4FE2`、`#4C2BA8`、`#25124F`；
  - 天蓝火焰（荧焰）：`#FFFFFF`、`#D9EFFF`、`#80C6FF`、`#3B87F0`、`#1F50B8`、`#0E2560`；
  - 银白（折镜）：`#FFFFFF`、`#F3F6FF`、`#CFD9F0`、`#9CAACC`、`#6B7899`、`#3C4560`；
  - 月光（换武器、大招）：`#FFFFFF`、`#F0FBFF`、`#BAE7F5`、`#7EC6E2`、`#4B90B9`、`#22466B`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在他或别人身上、脚下的画面按每条写的站位画，**格子里留出空的身体位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（28 张）

28 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：普攻距离 55000，荧焰波 45000，哨塔半径 35000，大招爆炸半径 22000）。

### 1. `aphelios_fx_a_cal.png`：通碧普攻：狙击子弹（朝目标飞，循环），3 帧

通碧的子弹：一颗细长的月绿色光弹，前端白色最亮，后面拖一条青绿色的细尾巴（参考 BA_calibrum_mis、BA_mis_core_radiance、BA_HexTrail）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-green ramp (#FFFFFF, #DFFFF2, #93F5CB, #43DBA2, #1F9E7A, #0F5B4B).
Effect: a SLIM MOON-GREEN SNIPER BULLET flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a bright white-green core 4 squares long and 2 thick at the RIGHT end, a tapering green trail 12 squares long behind it, flickering.
Layout: one horizontal row of 3 equal 18:7 cells, image size 864x112 (each cell 288x112, 16 px a square); the core's front 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `aphelios_fx_a_sev.png`：断魄普攻：镰刃弹（朝目标飞，循环），3 帧

断魄的子弹：一枚小小的血红色月牙形光弹（像一片弯刃），白芯，后面一点红色拖尾（参考 BA_severum_galaxy、BA_severum_hit_core）。**上下对称**（月牙开口朝后）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFD9D9, #FF8080, #E8394A, #A31D35, #5C0F22).
Effect: a SMALL CRIMSON CRESCENT BOLT flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a crescent 5 squares tall, its round side forward (RIGHT), opening backward, a white core line, a short red streak 4 squares behind it.
Layout: one horizontal row of 3 equal 11:9 cells, image size 528x144 (each cell 176x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `aphelios_fx_a_grav.png`：坠明普攻：重力弹（朝目标飞，循环），4 帧

坠明的子弹：一颗紫色的小月球（暗紫色外圈、亮紫白色的芯），后面拖一条紫色的旋涡尾巴（参考 BA_gravitum_mis_head_trail、Gravitum_weapon_eclipse）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #E8D9FF, #B78FFF, #7B4FE2, #4C2BA8, #25124F).
Effect: a VIOLET GRAVITY ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a round orb 5 squares across (deep violet rim, a white-violet core) at the RIGHT end, a swirling violet trail 6 squares behind it, the swirl turning between frames.
Layout: one horizontal row of 4 equal 12:9 cells, image size 768x144 (each cell 192x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `aphelios_fx_a_inf.png`：荧焰普攻：蓝焰弹（朝目标飞，循环），3 帧

荧焰的子弹：一团蓝色的火焰弹，前端白色，后面散开几缕蓝火（参考 BA_infernum_mis_shape、Q_infernum_flame）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an azure flame ramp (#FFFFFF, #D9EFFF, #80C6FF, #3B87F0, #1F50B8, #0E2560).
Effect: an AZURE FLAME BOLT flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a flame head 5 squares across with a white core at the RIGHT end, 3 tongues of blue fire trailing 7 squares behind it at mirrored places.
Layout: one horizontal row of 3 equal 14:9 cells, image size 672x144 (each cell 224x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `aphelios_fx_a_cre.png`：折镜普攻：回旋刃（朝目标飞，转着飞，循环），4 帧

折镜扔出去的回旋刃：一枚银白色的双月牙飞轮，转着飞，中间一个圆环（参考 BA_crescendum_trail、Ripper_Shuriken_Highlights）。每一帧**上下对称**（转的四个角度都要对称）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver ramp (#FFFFFF, #F3F6FF, #CFD9F0, #9CAACC, #6B7899, #3C4560).
Effect: a SPINNING SILVER CHAKRAM flying to the RIGHT, 4 frames of one turn, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): two crescent blades 9 squares across round a small ring, white-silver with a white core, a faint silver motion arc behind it; frame 1 the blades level, 2 turned 45 degrees, 3 upright, 4 turned 135 degrees (each frame mirrored top to bottom).
Layout: one horizontal row of 4 equal square cells, image size 704x176 (each cell 176x176, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `aphelios_fx_q_c_shot.png`：Q 通碧·狙杀：月光狙击弹（朝目标飞，循环），4 帧

通碧 Q 的狙击：一道又长又亮的月绿色光束弹，前端一颗白色的弹头，后面一条长长的绿色光尾，两边几颗绿色光点（参考 Q_calibrum_mis_02、Q_calibrum_mis_core、Q_beam_line_calibrum）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-green ramp (#FFFFFF, #DFFFF2, #93F5CB, #43DBA2, #1F9E7A, #0F5B4B).
Effect: a LONG MOON-GREEN SNIPER BEAM flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white bullet head 6 squares long and 3 thick at the RIGHT end in a green glow 7 squares tall, a straight green light trail 26 squares long behind it, fading toward the LEFT, a few green motes at mirrored places flickering.
Layout: one horizontal row of 4 equal 36:11 cells, image size 2304x176 (each cell 576x176, 16 px a square); the head's front 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `aphelios_fx_q_c_hit.png`：Q 通碧命中：月痕（目标身上），5 帧

通碧 Q 打中：一团绿白色的闪光，目标身上留下一个绿色的月牙标记符号（参考 BA_calibrum_symbol、Q_core_calibrum）。**左右对称**（月牙上下开口）。约 16 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-green ramp (#FFFFFF, #DFFFF2, #93F5CB, #43DBA2, #1F9E7A, #0F5B4B).
Effect: a MOON-GREEN MARK on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a green burst 12 squares with a white core; 3 a green crescent-moon sigil 10 squares across, its points up, a thin green ring 16 squares round it; 4 the ring fading, the sigil glowing; 5 the sigil fading.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `aphelios_fx_q_c_pop.png`：月痕引爆：追射弹（朝目标飞）+ 引爆（目标身上），飞行 3 帧 + 引爆 4 帧

画两张：① 追射弹：比普攻更亮更快的绿色光弹（**上下对称**）；② 引爆：月痕炸开，一团绿白色的爆闪和一圈绿色光环（**左右对称**）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-green ramp (#FFFFFF, #DFFFF2, #93F5CB, #43DBA2, #1F9E7A, #0F5B4B).
Effect: TWO STRIPS. (A) a FAST MOON-GREEN BOLT flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white-green core 4 squares long, a green trail 8 squares behind it. (B) a GREEN MARK BURSTING on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares; 2 a green burst 14 squares with a white core; 3 a green ring 18 squares across breaking into motes; 4 fading motes.
Layout: (A) one horizontal row of 3 equal 14:7 cells, image size 672x112 (each cell 224x112, 16 px a square); (B) one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `aphelios_fx_q_s_on.png`：Q 断魄·恒月强袭：他脚下的血色旋光（跟随，循环），4 帧

断魄 Q 的加速连射：他脚下一圈血红色的光环在转，几道红色弧光绕着他（参考 Q_severum_ground_ring、Q_severum_swirls、Q_Severum_cas_ground_glow）。**左右对称**，只画地上的环和绕身的弧，中间身体留空。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFD9D9, #FF8080, #E8394A, #A31D35, #5C0F22).
Effect: a CRIMSON GROUND SWIRL under a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat red ellipse ring 28 squares wide and 8 tall with a bright rim, 4 short red arcs on it at mirrored places moving round between frames, a few red motes.
Layout: one horizontal row of 4 equal 30:12 cells, image size 1920x192 (each cell 480x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `aphelios_fx_q_s_hit.png`：Q 断魄连射命中（目标身上），3 帧

断魄的每一发打中：一小道红色的十字刃光。**左右对称**。约 9 格（会连续出现很多次，要小）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFD9D9, #FF8080, #E8394A, #A31D35, #5C0F22).
Effect: a TINY CRIMSON SLASH on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a red X-shaped slash 8 squares; 3 fading red motes.
Layout: one horizontal row of 3 equal square cells, image size 528x176 (each cell 176x176, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `aphelios_fx_off_bolt.png`：副手追击弹（朝目标飞，循环），3 帧

副手武器的子弹（断魄 Q 的每第二发、荧焰 Q 波后的追击）：一颗银白带一点淡紫的月光弹，后面一条短尾巴（参考 BA_mis_cas、BA_mis_reaper_glow）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale moonlight ramp (#FFFFFF, #F0FBFF, #BAE7F5, #7EC6E2, #4B90B9, #22466B).
Effect: a PALE MOONLIGHT BOLT flying to the RIGHT, 3 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white core 4 squares long at the RIGHT end in a pale blue glow 4 squares tall, a pale trail 7 squares behind it.
Layout: one horizontal row of 3 equal 13:7 cells, image size 624x112 (each cell 208x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `aphelios_fx_q_g_cast.png`：Q 坠明·引力枷锁：施放时他脚下的月蚀（跟随），5 帧

坠明 Q 发动：他脚下一个紫色的月蚀圈（暗紫色的圆盘、亮紫色的边，中间一个黑色的月影），往外扩一下（参考 E_Eclips01、E_eclipse-bead、Gravitum_weapon_eclipse）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #E8D9FF, #B78FFF, #7B4FE2, #4C2BA8, #25124F).
Effect: a VIOLET ECLIPSE on the ground under a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a small violet ellipse 10 squares wide; 2 an eclipse ellipse 24 wide and 8 tall: a dark violet disc with a bright violet rim and a black moon-shadow in the middle; 3 the eclipse 36 wide, the rim brightest with violet beads round it at mirrored places; 4 the beads rising as motes; 5 fading.
Layout: one horizontal row of 5 equal 38:14 cells, image size 3040x224 (each cell 608x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `aphelios_fx_q_g_hit.png`：Q 坠明定身（目标身上），6 帧

被定身：目标脚下一圈紫色的月蚀环，几根紫色的光羽从环上竖起来把人钉住，头顶一颗小小的紫色月亮（参考 root_feathers、Q_gravitum_root_indicator、Radiance_Stun_ground_mult）。**左右对称**，中间身体留空（an upright slim figure 12 wide and 24 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #E8D9FF, #B78FFF, #7B4FE2, #4C2BA8, #25124F).
Effect: a VIOLET ROOT on a unit, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright figure 12 squares wide and 24 tall stands in the middle, not drawn): 1 a violet ring 18 squares wide and 5 tall at the feet; 2 four violet light feathers rising from the ring at mirrored places, 8 squares tall; 3 the feathers 14 squares tall, bright, a small violet moon 4 squares above the head; 4-5 the same pulsing; 6 fading.
Layout: one horizontal row of 6 equal 22:28 cells, image size 2112x448 (each cell 352x448, 16 px a square); centered across, the ring's middle 2 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `aphelios_fx_q_i_wave.png`：Q 荧焰·余晖波：向前喷出的扇形蓝焰（他身上，不跟随），5 帧

荧焰 Q：从他手上的荧焰往前（右边）喷出一道扇形的蓝色火焰波，从窄到宽向右推出去 45 格，边上是白色和最亮的蓝（参考 Q_infernum_cas_swipe、Q_infernum_flame_shapes、Q_infernum_ground）。**这张有方向**：画成朝右，扇形的尖在格子左边（他手的位置），往右张开，上下对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an azure flame ramp (#FFFFFF, #D9EFFF, #80C6FF, #3B87F0, #1F50B8, #0E2560).
Effect: an AZURE FLAME WAVE blasting to the RIGHT, 5 frames, symmetric top to bottom: the fan's point at the LEFT middle (the hand), opening to the RIGHT to 90 degrees; 1 a white-blue flash 6 squares at the point; 2 a flame fan 20 squares long; 3 the fan 40 squares long and 28 tall at its far end, brightest, white-blue leading edge; 4 the fan 46 squares long, breaking into blue flame tongues; 5 fading blue embers along the fan.
Layout: one horizontal row of 5 equal 50:32 cells, image size 4000x512 (each cell 800x512, 16 px a square); the fan's point 2 squares from the LEFT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `aphelios_fx_q_i_hit.png`：Q 荧焰命中（目标身上），4 帧

被蓝焰烧到：一团蓝色火焰往上窜（白芯）。**左右对称**。约 14 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from an azure flame ramp (#FFFFFF, #D9EFFF, #80C6FF, #3B87F0, #1F50B8, #0E2560).
Effect: an AZURE BURN on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares; 2 a blue flame burst 10 squares with a white core; 3 blue flames 14 squares rising; 4 fading embers.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `aphelios_fx_q_r_turret.png`：Q 折镜·驻灵哨卫：地上的哨塔（不跟随，循环），6 帧

折镜的哨塔：一个悬在半空的银白色双月牙飞轮在慢慢转，下面地上一圈淡淡的银白光环，飞轮周围有月光的光点（参考 Q_orbitum_ripple、Q_orbitum_blade_erode、Weapon_alphacircle）。**中心对称**（每一帧转 180 度后和自己一样：红色方游戏会把这张图倒过来）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver ramp (#FFFFFF, #F3F6FF, #CFD9F0, #9CAACC, #6B7899, #3C4560).
Effect: a HOVERING SILVER SENTRY, 6 frames, a seamless loop, POINT-SYMMETRIC in every frame (the same picture turned 180 degrees: on the red side the game turns it upside down and back to front): a double-crescent chakram 14 squares across hovering in the middle, turning 30 degrees a frame (a 180 degree turn over the loop), a white ring hub; a faint silver ground ring 20 squares wide and 6 tall under it, silver motes round it at point-mirrored places.
Layout: one horizontal row of 6 equal square cells, image size 2304x384 (each cell 384x384, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `aphelios_fx_q_r_hit.png`：Q 折镜哨塔击中（目标身上），3 帧

哨塔每一下打中：一小团银白色的闪光。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver ramp (#FFFFFF, #F3F6FF, #CFD9F0, #9CAACC, #6B7899, #3C4560).
Effect: a SMALL SILVER HIT on a unit, 3 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a silver star burst 9 squares; 3 fading motes.
Layout: one horizontal row of 3 equal square cells, image size 576x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `aphelios_fx_a_hit.png`：普攻命中（目标身上），4 帧

所有子弹打中：一小团月光白的闪光和几颗火星（参考 BA_Rifle_hit、BA_hit_tar_muzzle）。**左右对称**。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale moonlight ramp (#FFFFFF, #F0FBFF, #BAE7F5, #7EC6E2, #4B90B9, #22466B).
Effect: a SMALL MOONLIGHT HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white dot 2 squares; 2 a pale flash 7 squares with a white core; 3 the flash 10 squares, 6 short pale sparks at mirrored places; 4 a few fading motes.
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `aphelios_fx_muzzle.png`：枪口火光（他身上，跟随），3 帧

开枪那一刻枪口的闪光：一团朝右喷出的白绿色火光（画成通碧的绿色，Claude 换色给其他武器）（参考 BA_calibrum_cas_flash、BA_infernum_cas_flash）。画成朝右：火光的根部在格子左边中间（枪口），往右喷，上下对称。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-green ramp (#FFFFFF, #DFFFF2, #93F5CB, #43DBA2, #1F9E7A, #0F5B4B).
Effect: a MUZZLE FLASH blasting to the RIGHT, 3 frames, symmetric top to bottom: 1 a white star 4 squares at the LEFT middle; 2 a white-green flash 9 squares long shooting right, 2 small side spikes at mirrored places; 3 fading green motes.
Layout: one horizontal row of 3 equal 12:10 cells, image size 576x160 (each cell 192x160, 16 px a square); the flash's root 1 square from the LEFT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `aphelios_fx_swap.png`：换武器的月光（他身上，跟随），5 帧

换武器（打空换下一把、W 换手）：一道淡蓝白的月光从他身边划一圈，一弯月牙的光闪过他的身体，几片月光羽毛往上飘（参考 Weapon_color_hold、BA_feather_full_erosion、R_symbol_swipe）。**左右对称**，中间身体留空（an upright slim figure 18 squares wide and 46 tall stands in the middle, not drawn），要淡一点，不要盖住他。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale moonlight ramp (#FFFFFF, #F0FBFF, #BAE7F5, #7EC6E2, #4B90B9, #22466B).
Effect: a MOONLIGHT SWIRL round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright slim figure 18 squares wide and 46 tall stands in the middle, not drawn): 1 pale motes at both sides of the waist; 2 two thin moonlight arcs sweeping up both sides; 3 the arcs meeting above the head as a crescent 14 squares wide, brightest; 4 the crescent fading, 6 small light feathers drifting up at mirrored places; 5 the last feathers.
Layout: one horizontal row of 5 equal 28:50 cells, image size 2240x800 (each cell 448x800, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `aphelios_fx_r_cast.png`：大招 清辉夜凝：施放（他身上，跟随），5 帧

大招发动：他身后浮现姐姐 Alune 的淡淡月光身影（只画一个发光的月牙和光晕，不画人），脚下一圈月光的光环，光点往他手上收（参考 R_alune_figure、R_alune_shoulder_flare、R_cas_hand_motes、R_cas_Decal_base）。**左右对称**，中间身体留空（an upright slim figure 18 squares wide and 46 tall stands in the middle, not drawn）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale moonlight ramp (#FFFFFF, #F0FBFF, #BAE7F5, #7EC6E2, #4B90B9, #22466B).
Effect: a MOONLIGHT RISING behind a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright slim figure 18 squares wide and 46 tall stands in the middle, not drawn): 1 a pale ground ellipse 30 squares wide and 8 tall under the feet; 2 a large pale crescent moon 24 squares wide rising behind the head; 3 the crescent brightest with a soft halo 34 wide, pale motes drifting in toward the figure at mirrored places; 4 the motes gathering, the ellipse glowing; 5 fading.
Layout: one horizontal row of 5 equal 38:54 cells, image size 3040x864 (each cell 608x864, 16 px a square); centered across, the figure's feet on the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `aphelios_fx_r_moon.png`：大招：月光弹（朝目标飞，循环），4 帧

大招的月光：一颗发光的满月（白色的月面、淡蓝的光晕），后面一条长长的月光尾巴和几颗光点（参考 R_mis_moon、R_moonbeam、R_mis_beam_motes、R_mis_brightspot）。**上下对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale moonlight ramp (#FFFFFF, #F0FBFF, #BAE7F5, #7EC6E2, #4B90B9, #22466B).
Effect: a GLOWING FULL MOON flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its direction; going left it is flipped upside down): a white moon disc 9 squares across with a pale blue halo 13 squares at the RIGHT end, a moonlight trail 18 squares long behind it, a few pale motes at mirrored places flickering.
Layout: one horizontal row of 4 equal 30:15 cells, image size 1920x240 (each cell 480x240, 16 px a square); the halo's front 1 square from the RIGHT edge, vertically centered. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `aphelios_fx_r_boom.png`：大招：月光爆炸（地上，不跟随），6 帧

月光在第一个英雄身上炸开：一圈月光冲击环向外推，中间一根月光柱往上冲（白芯），地上一个月牙形的光印（参考 R_explosion_beam、R_explosion_beam_boom、R_explosion_shapes、R_ring_var1、R_Decal_RGB）。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale moonlight ramp (#FFFFFF, #F0FBFF, #BAE7F5, #7EC6E2, #4B90B9, #22466B).
Effect: a MOONLIGHT BURST on the ground, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 10 squares on the ground; 2 a pillar of white-blue light 8 squares wide rising 24 squares, a flat ground ring 24 wide and 8 tall; 3 the pillar 32 tall, the ring 40 wide with a bright rim, a crescent-moon sigil on the ground inside it; 4 the ring 48 wide, the pillar breaking into motes; 5 the motes rising, the sigil fading; 6 the last motes.
Layout: one horizontal row of 6 equal 50:36 cells, image size 4800x576 (each cell 800x576, 16 px a square); centered across, the ground ring's middle 5 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `aphelios_fx_r_hit.png`：大招命中（目标身上），4 帧

被月光炸到：一团淡蓝白的闪光和几道往外的月光。**左右对称**。约 18 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pale moonlight ramp (#FFFFFF, #F0FBFF, #BAE7F5, #7EC6E2, #4B90B9, #22466B).
Effect: a MOONLIGHT HIT on a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares; 2 a pale blue burst 12 squares with a white core; 3 the burst 18 squares with 8 light rays at mirrored places; 4 fading motes.
Layout: one horizontal row of 4 equal square cells, image size 1280x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 25. `aphelios_fx_mw.png`：主手武器光环（他脚下，循环），4 帧

他脚下一圈淡淡的武器光环，告诉玩家现在主手是哪把（画成通碧的绿色，Claude 换成五种颜色）：一个扁的光环，上面一弯小月牙，几颗光点轮流亮。**左右对称**，要淡。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a moon-green ramp (#FFFFFF, #DFFFF2, #93F5CB, #43DBA2, #1F9E7A, #0F5B4B).
Effect: a FAINT WEAPON SIGIL under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin flat ellipse ring 20 squares wide and 5 tall in dim green, a small crescent mark 4 squares wide at its front middle, 4 brighter motes on the ring at mirrored places taking turns to light up.
Layout: one horizontal row of 4 equal 22:7 cells, image size 1408x112 (each cell 352x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 26. `aphelios_fx_g_slow.png`：坠明减速（敌人脚下，循环），4 帧

被坠明打中减速：敌人脚下一圈淡紫色的重力环，几颗紫色光点往下沉。**左右对称**。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a violet ramp (#FFFFFF, #E8D9FF, #B78FFF, #7B4FE2, #4C2BA8, #25124F).
Effect: a FAINT GRAVITY RING under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a thin flat ellipse 14 squares wide and 4 tall in dim violet, 4 violet motes sinking onto it at mirrored places.
Layout: one horizontal row of 4 equal 16:6 cells, image size 1024x96 (each cell 256x96, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 27. `aphelios_fx_q_s_haste.png`：断魄加速（他脚下，循环），4 帧

断魄 Q 的移速加成：他脚下两侧几道红色的风痕往后拖。**左右对称**，要淡。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a crimson ramp (#FFFFFF, #FFD9D9, #FF8080, #E8394A, #A31D35, #5C0F22).
Effect: FAINT CRIMSON SPEED STREAKS under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 3 short red streaks at each side of a 16-square gap, flickering between frames.
Layout: one horizontal row of 4 equal 20:7 cells, image size 1280x112 (each cell 320x112, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 28. `aphelios_fx_cre.png`：折镜回旋刃层数（他身边环绕，循环），4 帧

折镜每叠一层：他身边绕着转的小回旋刃（画 3 枚，绕着他的胸口转一圈）（参考 BA_crescendum_trail）。**左右对称**，中间身体留空，要小，不要盖住他。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, bullets, flames, smoke, sparks, stars or rings, BRIGHT colours (each light shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a silver ramp (#FFFFFF, #F3F6FF, #CFD9F0, #9CAACC, #6B7899, #3C4560).
Effect: SMALL SILVER CHAKRAMS ORBITING a figure's chest, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side) (an upright slim figure 18 squares wide stands in the middle, not drawn): three tiny double-blade chakrams 4 squares across on an orbit ellipse 26 wide and 8 tall around the chest, placed so every frame mirrors left to right (two at the sides, one front or back), moving round between frames.
Layout: one horizontal row of 4 equal 28:32 cells, image size 1792x512 (each cell 448x512, 16 px a square); the orbit's middle 20 squares above the cell's bottom row. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `aphelios_fx_a_cal` | view_projectiles `league_aphelios_a_cal`（朝飞行方向转，画成朝右飞；上下对称） | 16 × 5 |
| `aphelios_fx_a_sev` | view_projectiles `league_aphelios_a_sev`，Q 断魄的连射 `q_s_bolt` 也用它（朝飞行方向转；上下对称） | 9 × 7 |
| `aphelios_fx_a_grav` | view_projectiles `league_aphelios_a_grav`（朝飞行方向转；上下对称） | 10 × 7 |
| `aphelios_fx_a_inf` | view_projectiles `league_aphelios_a_inf`，溅射弹 `a_inf_s` 也用它（朝飞行方向转；上下对称） | 12 × 7 |
| `aphelios_fx_a_cre` | view_projectiles `league_aphelios_a_cre`（朝飞行方向转；上下对称） | 9 × 9 |
| `aphelios_fx_q_c_shot` | view_projectiles `league_aphelios_q_c_shot`（朝飞行方向转；上下对称；大图表） | 34 × 9 |
| `aphelios_fx_q_c_hit` | view_effects `league_aphelios_q_c_hit`（跟随，画在人物上面；左右对称） | 16 |
| `aphelios_fx_q_c_pop` | view_projectiles `league_aphelios_q_c_pop`（追射弹，上下对称；大招的通碧追射 `r_c_shot` 也用它），view_effects `league_aphelios_q_c_pop`（引爆，跟随，左右对称） | 弹 12 × 5；引爆 18 |
| `aphelios_fx_q_s_on` | view_effects `league_aphelios_q_s_on`（跟随，画在他身上、人物下面；左右对称） | 30 × 10 |
| `aphelios_fx_q_s_hit` | view_effects `league_aphelios_q_s_hit`（跟随，画在人物上面；左右对称） | 9 |
| `aphelios_fx_off_bolt` | view_projectiles `league_aphelios_q_s_off` / `q_i_off`（副手武器的追击弹；上下对称） | 11 × 5 |
| `aphelios_fx_q_g_cast` | view_effects `league_aphelios_q_g_cast`（跟随，画在他身上、人物下面；左右对称；大图表） | 36 × 12 |
| `aphelios_fx_q_g_hit` | view_effects `league_aphelios_q_g_hit`（跟随，画在人物上面；左右对称） | 20 × 26 |
| `aphelios_fx_q_i_wave` | view_effects `league_aphelios_q_i_wave`（**不跟随**，画在他身上；有方向：画成朝右，大图表） | 48 × 30 |
| `aphelios_fx_q_i_hit` | view_effects `league_aphelios_q_i_hit`（跟随，画在人物上面；左右对称） | 14 |
| `aphelios_fx_q_r_turret` | view_projectiles `league_aphelios_q_r_turret`（哨塔区域的画面，持续 5 秒；**中心对称**；大图表） | 22 × 22 |
| `aphelios_fx_q_r_hit` | view_effects `league_aphelios_q_r_hit`（跟随，画在人物上面；左右对称） | 10 |
| `aphelios_fx_a_hit` | view_effects `league_aphelios_a_hit`（跟随，画在人物上面；左右对称） | 10 |
| `aphelios_fx_muzzle` | view_effects `league_aphelios_m_<武器>`（Claude 按五把武器换色、挪到各自的枪口；画成朝右） | 10 × 8 |
| `aphelios_fx_swap` | view_effects `league_aphelios_swap`（跟随，画在他身上；左右对称） | 26 × 48 |
| `aphelios_fx_r_cast` | view_effects `league_aphelios_r_cast`（跟随，画在他身上、人物下面；左右对称；大图表） | 36 × 52 |
| `aphelios_fx_r_moon` | view_projectiles `league_aphelios_r_moon`（朝飞行方向转；上下对称；大图表） | 28 × 13 |
| `aphelios_fx_r_boom` | view_effects `league_aphelios_r_boom`（不跟随，地上；左右对称；大图表） | 48 × 34 |
| `aphelios_fx_r_hit` | view_effects `league_aphelios_r_hit`（跟随，画在人物上面；左右对称） | 18 |
| `aphelios_fx_mw` | view_buffs `league_aphelios_mw_<武器>`（跟随，画在人物下面；左右对称；Claude 按五把武器换色） | 22 × 6 |
| `aphelios_fx_g_slow` | view_buffs `league_aphelios_g_slow`（跟随，画在人物下面；左右对称；大招坠明的减速 `r_slow` 也用它） | 16 × 5 |
| `aphelios_fx_q_s_haste` | view_buffs `league_aphelios_q_s_haste`（跟随，画在人物下面；左右对称） | 18 × 6 |
| `aphelios_fx_cre` | view_buffs `league_aphelios_cre`（跟随，画在他身上；左右对称） | 26 × 30 |

- 两张表：`asset/league/effects/league_aphelios_fx`（小的）和 `league_aphelios_big`（q_c_shot、q_g_cast、q_i_wave、q_r_turret、r_cast、r_moon、r_boom），tag = 名字（build_aphelios.py 的 views）。
- `mw` 换色成 mw_cal / mw_sev / mw_grav / mw_inf / mw_cre；`muzzle` 换色并按各武器的枪口位置画成 m_cal / m_sev / m_grav / m_inf / m_cre（开枪那一帧，攻击开始时播放、跟随，前面空帧补到开枪的时刻）；`q_c_pop` 拆成飞行弹和引爆两个 tag。
- `q_i_wave` 晚于动作第一刻播放，**is_follow false**（红色方的规则）；`r_boom` 不跟随；`q_s_on`、`q_g_cast`、`r_cast`、`mw`、`g_slow`、`q_s_haste` 画在人物下面（z -1）。
- 用 `pixel_1x/` 切格（import_kalista_fx 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单。
