# 诺提勒斯最后一步：17 张技能特效

完成 17 条、共 75 帧特效：普攻与被动 3 条、Q 2 条、W/E 7 条、R 5 条。最终透明 PNG 为 8 倍，pixel_1x/ 为相同逻辑网格的原尺寸版，raw/ 保留 18 张生图原稿且没有重采样。

## 制作与检查

使用内置 image_gen，逐条按输入 PROMPTS.md 的 17 段提示词生成。Q 飞锚使用本包定稿动作图作为实物外观参考；原版 LOL 贴图仅在本地查看，没有放入交付包。

最终尺寸是示范生图提示词中 16 倍尺寸的一半：逻辑格数不变，严格放大 8 倍。按区域多数色读取，不取中心点；透明阈值 160，区域内不透明覆盖超过 20% 才保留；归并至每条指定色板。沿透明间隙分帧，各帧按统一缩放比例读取逻辑格并居中，避免分别按 bbox 放大造成尺度漂移。身体附着效果逐格复制左半到右半，飞行效果上下半合并后逐格镜像，三波 E 同时执行两个方向；再将水光外边缘的暗色改为允许的浅青亮色。仅铁锚保留深色描边。W 护盾中间留空，R 命中保留底部 12×24 格的人形通道。没有画人物。

validation.json 已检查 17 张数量、75 帧数量、尺寸、8×8 纯色块、0/255 透明度、各条指定色板、逐格严格对称和 W/R 中间留空。manifest.json 记录每帧矩形、bbox、pivot、绑定信息与原稿哈希。

## 使用时需注意

- 输入包未给出每帧时长，所以 manifest 的 duration_ms 为 null。GIF 统一用 100ms，仅作视觉预览，不能当作游戏时序。效果循环、持续时间和 E 三波错峰应由导入侧技能数据决定。
- 水花轮廓和飞锚为生成后按小尺寸整理，未逐格复刻参考纹理。清单中“约多少格”的可见范围是目标，最终精确可见范围请读 bbox；原稿构图与像素归并会产生少量尺寸差异，不能声称已通过实际战场可读性或遮挡测试。
- 对称处理会统一两侧水花，不是保留生图里的每一处随机细节。护盾与水柱的中间留空由透明掩模强制保证。
- 本次完成的是特效素材交付。附件中 Claude 导入表仅保留为绑定信息，没有改仓库、运行游戏、提交或发布；R 追踪弹首 tick 的空白帧应在导入时添加，未改变本包要求的 4 帧 r_wave。
- tools/build_workflow_record.py 是本次处理脚本的记录，路径指向原工作目录，并非独立安装工具。

Q 飞锚另生成一版粗像素修正，最终选择 raw/q_anchor_coarse.png，原版本 raw/q_anchor.png 也保留；追加编辑提示词见 q_anchor_edit_prompt.txt。

## 每张实际提示词


### a_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: an ANCHOR SMASH HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 5 squares across; 2 a burst of white-aqua water splashing out 12 squares across, white foam in the middle; 3 the splash wider and thinner, water drops flying out at mirrored places; 4 a few fading drops.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 16 by 16 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### p_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a WATER SURGE on a unit, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat white-aqua splash 10 squares wide on the ground; 2 a column of water 6 squares wide shooting up the middle 20 squares tall, white foam at its top; 3 the column breaking into foam, a ring of splashes 18 squares wide at the bottom; 4 drops falling at mirrored places; 5 fading drops.
Layout: one horizontal row of 5 equal 20:24 cells, image size 1600x384 (each cell 320x384, 16 px a square); centered across, the splash on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 20 by 24 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### p_root

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a WATER SNARE under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an ellipse of swirling water 16 squares wide and 5 tall, a bright aqua foam edge, deep water inside, 4 short foam ripples at mirrored places that move inward each frame.
Layout: one horizontal row of 4 equal 20:9 cells, image size 1280x144 (each cell 320x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 20 by 9 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### q_anchor

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from the anchor's iron greys (#F6E4C8, #B2B0A8, #70747A, #3D4150, #2D3041, #070211; #070211 is its 1-square outline), bronze and rust (#FAAC2A, #DC741C, #A84217, #6F2610) and a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a FLYING ANCHOR to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): at the right the anchor's crown seen from the side, its two hooked flukes curving back, one up and one down (mirrored), 12 squares tall; a straight iron shank 10 squares long to the left with one red-rust band; behind it a short iron chain of 4 links trailing to the left edge; a little white-aqua foam splashing off the crown's front (mirrored). The anchor and the chain are solid iron with a 1-square #070211 outline; the foam has no outline. The foam and the chain links jiggle each frame.
Layout: one horizontal row of 4 equal 24:16 cells, image size 1536x256 (each cell 384x256, 16 px a square); the crown's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 24 by 16 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### q_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: an ANCHOR HOOK HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 6 squares across; 2 a big burst of white-aqua water 14 squares across; 3 a thin foam ring 16 squares across, drops at mirrored places; 4 fading drops.
Layout: one horizontal row of 4 equal square cells, image size 1152x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 18 by 18 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### w_on

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-green glow ramp (#FFFFFF, #CFFFE9, #7DF5C8, #00E9BE, #03A688).
Effect: a SEA-GREEN SHIELD round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY: an upright ellipse outline 28 squares wide and 40 tall, 1-2 squares thick, glowing sea-green with white glints at mirrored places that move to new mirrored places each frame.
Layout: one horizontal row of 4 equal 32:44 cells, image size 2048x704 (each cell 512x704, 16 px a square); the shell centered in every cell, its bottom 1 square above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 32 by 44 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### w_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-green glow ramp (#FFFFFF, #CFFFE9, #7DF5C8, #00E9BE, #03A688) and a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a GLOWING SPLASH RING round a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a sea-green flash 6 squares wide; 2 a sea-green ellipse ring 14 squares wide and 6 tall with short sparks; 3 the ring 20 wide, thinner; 4 fading sparks at mirrored places.
Layout: one horizontal row of 4 equal 22:12 cells, image size 1408x192 (each cell 352x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 22 by 12 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### e_wave1

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a GROUND WAVE (the first and smallest), 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: an elliptical ring of crashing water seen from above at an angle, white foam crests along it; 1 a ring 14 squares wide; 2 24 wide, foam spraying up; 3 30 wide; 4 36 wide and 14 tall, breaking; 5 foam fading.
Layout: one horizontal row of 5 equal 38:16 cells, image size 3040x256 (each cell 608x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 38 by 16 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### e_wave2

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a GROUND WAVE (the second), 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: an elliptical ring of crashing water seen from above at an angle, white foam crests; 1 a ring 26 squares wide; 2 38 wide, foam spraying up; 3 46 wide; 4 52 wide and 20 tall, breaking; 5 foam fading.
Layout: one horizontal row of 5 equal 54:22 cells, image size 4320x352 (each cell 864x352, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 54 by 22 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### e_wave3

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a GROUND WAVE (the third and largest), 5 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: an elliptical ring of crashing water seen from above at an angle, white foam crests; 1 a ring 36 squares wide; 2 52 wide, foam spraying up; 3 62 wide; 4 68 wide and 26 tall, breaking; 5 foam fading.
Layout: one horizontal row of 5 equal 70:28 cells, image size 5600x448 (each cell 1120x448, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 70 by 28 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### e_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a WAVE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white flash 4 squares across; 2 water splashing up 10 squares wide; 3 drops at mirrored places; 4 fading drops.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 14 by 14 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### e_slow

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a PUDDLE SLOW under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a shallow water ellipse 14 squares wide and 4 tall with a white-aqua foam edge, 4 short ripples at mirrored places drifting inward each frame.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 18 by 8 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### r_cast

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a DEPTH CHARGE LAUNCH at a figure's feet, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a flat white-aqua flash 12 squares wide on the ground; 2 water and dust bursting out to both sides 24 squares wide; 3 a teal ring 28 wide; 4 thinning; 5 fading drops.
Layout: one horizontal row of 5 equal 30:14 cells, image size 2400x224 (each cell 480x224, 16 px a square); centered across, the bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 30 by 14 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### r_wave

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a SHOCKWAVE RUSHING to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): at the right a crest of white-aqua water spikes 12 squares tall bursting up and down (mirrored), deep water in its middle, a trail of smaller splashes 12 squares long behind it to the left (mirrored); the spikes and splashes change each frame.
Layout: one horizontal row of 4 equal 26:16 cells, image size 1664x256 (each cell 416x256, 16 px a square); the crest's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 26 by 16 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### r_up

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a WATER SPIKE under a unit, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white splash 8 squares wide on the ground; 2 a spike of water 6 squares wide shooting up 16 squares tall in the middle; 3 the spike breaking into foam; 4 fading drops.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); centered across, the splash on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 16 by 20 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### r_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8) and a deep water ramp (#0E7C86, #0B5D6E, #0A4158, #082A3F; its darkest shades only inside the water, every edge in the lighter shades).
Effect: a GREAT WATER ERUPTION round a unit, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the unit's place in the middle (12 x 24 squares, from the bottom) EMPTY: 1 a white flash 14 squares wide on the ground and a teal ring 24 wide; 2 two thick columns of water bursting up both sides 36 squares tall, deep water inside, white foam edges; 3 the columns' tops crashing into white foam over the middle; 4 water falling at mirrored places; 5 drops and thin foam; 6 fading drops.
Layout: one horizontal row of 6 equal 32:42 cells, image size 3072x672 (each cell 512x672, 16 px a square); centered across, the ground ring's bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 32 by 42 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```

### r_stun

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, water or rings, BRIGHT colours (each splash lit with its lightest shades and a white foam core - it must read on a dark battlefield), colours only from a sea-foam ramp (#FFFFFF, #D8FFF7, #8CF2E6, #3FD3C8, #12A3A8).
Effect: a DAZE RING of bubbles over a head, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 16 squares wide and 5 tall of small white-aqua bubbles, 4 bright bubbles on it at mirrored places that step to new mirrored places each frame.
Layout: one horizontal row of 4 equal 18:9 cells, image size 1152x144 (each cell 288x144, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Draw the smallest detail as ONE large square: the actual logical cell is 18 by 9 pixels. Effects only, NO character. Keep all frames separate and completely inside their equal cells.
```
