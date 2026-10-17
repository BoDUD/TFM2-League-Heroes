# 萨勒芬妮最后一步：特效素材交接

完成范围：依据用户“完成最后一步”的请求生成 25 项 FX，整理为 114 帧。附件文本作为美术规格使用；其中给 Claude 的运行时绑定、导入、Git 操作不是本次实际执行的操作。

## 文件用途

- 根目录 `seraphine_fx_*.png`：25 张精确 16× 最近邻放大的透明水平条带；每格 16×16 像素。
- `pixel_1x/`：25 张游戏尺寸透明条带，每逻辑格 1 像素。
- `raw/`：未经处理的生成原稿；`superseded_*` 是重生前版本，不用于导入。原稿含半透明软边、非规定尺寸等问题。
- `FX_ANIMATED_PREVIEW.gif`：深色背景总览，100 ms/帧，全部效果循环展示，仅用于审阅，不表示运行时播放时序。
- `FX_CONTACT_SHEET.png`、`preview/`：静态检视。
- `manifest.json`：帧数、尺寸、原稿分界、采样范围。
- `QA_REPORT.json`：自动格式检查结果。
- `fx_list.json`：从用户素材包原样复制的绑定参考，尚未接入游戏。

## 处理与验证

所有特效外形来自图像生成工具，没有用代码绘制替代光球、音环或心形。后处理仅分帧、重新定位、按指定调色板多数采样、二值透明化、成对像素对称校正及清理角色占位。原稿不是可靠的原生 16× 格网，因此游戏版经过重新采样，而非无损缩小。镜像会合并或加粗局部亮点。

格式检查 PASS：25 项、114 帧；每项文件尺寸正确；各帧非空；Alpha 仅 0/255；颜色来自对应提示调色板；逐帧指定轴完全对称；16× 文件逐像素等于 1× 的最近邻放大；被动音符中央 18×34 留空；护盾及聚光灯中央检查区留空。

**这不表示逐格美术规格全部通过，也不表示已完成游戏内验收。** 首尾顺滑、音符数量与具体轮廓、光环半径、技能锚点和实际遮挡仍需在游戏中确认。文中要求的若干 3 格形状，在偶数尺寸单元的中心严格对称时会变为偶数宽度。

## 逐项结果

| 文件名 | 帧数 | 每帧 1× 尺寸 | 对称轴 | 说明 |
|---|---:|---|---|---|
| seraphine_fx_a_bolt.png | 4 | 12×8 | y | 重生了右凸弧；原稿最后一个音球仍靠近图边。整理版留有透明边，但球径与提示中的 3 格不完全一致。 |
| seraphine_fx_a_note.png | 4 | 16×10 | y | 彩虹带、尾弧和闪点在小尺寸中合并为较简洁的亮块；不是逐个闪点的精确复刻。 |
| seraphine_fx_a_hit.png | 4 | 14×14 | x | 保留亮芯、扩散青环、碎光消散；星芒分支数在 1× 版减少。 |
| seraphine_fx_a_note_hit.png | 5 | 18×18 | x | 保留扩圈与上升音符的阶段；后两帧细音符退化成竖线和闪点。 |
| seraphine_fx_q_note.png | 4 | 12×12 | y | 保留粉白音球和青/彩虹环；原稿音球及环的占格数、前缘锚点需要游戏内确认。 |
| seraphine_fx_q_land.png | 6 | 62×26 | xy | 对原稿不均匀帧距做了分界校正；双轴对称通过。扩圈各阶段直径没有严格复刻 12/30/46/58 格。 |
| seraphine_fx_q_hit.png | 4 | 16×16 | x | 保留亮芯、两侧弧、碎光；细弧与星芒在 1× 中简化。 |
| seraphine_fx_q_amp.png | 5 | 20×20 | x | 保留金粉爆发、扩张、碎光消散；射线和八角星的格数为采样结果。 |
| seraphine_fx_e_wave.png | 4 | 16×20 | y | 保留向右前弧及后弧，上下对称；厚度与提示中的 2 格存在偏差。 |
| seraphine_fx_e_hit.png | 4 | 16×16 | x | 保留青白亮芯、双色扩圈、碎光；扩圈形状为采样校正结果。 |
| seraphine_fx_e_root.png | 6 | 22×12 | x | 为保留淡入首帧采用较低的原稿 Alpha 阈值，再输出二值 Alpha。三条五线谱与四个金音符在 1× 中未全部保持独立。 |
| seraphine_fx_e_stun.png | 4 | 20×10 | x | 保留围绕中心的金粉亮点；六音符的具体轮廓在 1× 中偏抽象，需美术复核。 |
| seraphine_fx_w_cast.png | 6 | 102×38 | xy | 保留地面音环、音符立柱及消散过程，双轴对称。原稿细节较密，后段仍较碎；扩张半径不是精确的 20/50/80/98 格。 |
| seraphine_fx_w_on.png | 4 | 28×36 | x | 中央留空及左右对称通过。护盾边缘和双侧速度线已简化；整体形状接近竖直椭圆，未严格逐格复刻 24×32。 |
| seraphine_fx_w_heal.png | 6 | 18×24 | x | 保留绿色底部亮芯、上升心形及加号；小心形与加号的边缘在 1× 中合并。 |
| seraphine_fx_r_wave.png | 4 | 28×38 | y | 保留粉/青多重右弧、音符与心形；上下对称通过，但光弧厚度和数量需最终美术复核。 |
| seraphine_fx_r_cast.png | 6 | 46×58 | x | 实心光柱版本已弃用并保留在 raw/superseded_*。采用重生空心光锥，清理角色中央占位；地面环宽及星光数量是近似值。 |
| seraphine_fx_r_hit.png | 5 | 20×20 | x | 保留白粉爆发、心形与上升碎光；最终帧残留弧形闪点，不是逐像素指定的心形布局。 |
| seraphine_fx_echo.png | 5 | 36×46 | x | 保留竖直白圈→彩虹扩圈→碎光过程，左右对称；扩圈各阶段的实际占格尺寸与文本不同。 |
| seraphine_fx_n1.png | 4 | 32×42 | x | 重生为中央直杆圆点音符。6×6 采样范围及左右镜像会放大轮廓，未精确满足 3 格圆点；中央 18×34 角色区域全透明。 |
| seraphine_fx_n2.png | 4 | 32×42 | x | 双音符在顶部左右成对，角色区域留空；音符是少数像素构成的简化标记。 |
| seraphine_fx_n3.png | 4 | 32×42 | x | 中央粉色音符与两侧青色音符，角色区域留空；中央轮廓与侧边细节经过缩小和镜像。 |
| seraphine_fx_n4.png | 4 | 32×42 | x | 保留头部/腰部成对音符与上下交替运动，角色区域留空；彩虹闪点和音符轮廓较简化。 |
| seraphine_fx_echo_ready.png | 4 | 32×10 | x | 保留扁椭圆彩虹边与粉白中心的脉冲；少量边缘星光保留，不是严格 28×6 格轮廓。 |
| seraphine_fx_e_slow.png | 4 | 18×8 | x | 重生为上下两条青色椭圆环，输出左右对称；1× 中环内浅色点与环边有合并，需游戏内评估识别度。 |

`x` = 左右对称；`y` = 上下对称；`xy` = 双轴。

## 实际采用的生成提示

每项独立调用图像生成工具，透明背景开启。首轮引用 `lol_fx_ref.png` 只取形状灵感；重生的 a_bolt、e_slow、r_cast、n1、n3 没有引用该图。参考图不包含在交付包。下面记录最终采用原稿的完整实际提示。

### 1. a_bolt

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a SOUND ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a bright white-pink orb 3 squares across at the right, a soft pink glow round it, two thin cyan arcs ')' 4 squares tall trailing behind it to the left; each frame the arcs step back one square and the glow pulses.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
CRITICAL: Generous transparent margin inside every frame; do not clip the last frame. Exactly four equal-width cells. No blur or glow, pure flat squares. Both cyan trailing arcs bulge to RIGHT like ')' and orb at right.
```

### 2. a_note

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a CHARGED SOUND ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a bright white-pink orb 5 squares across with a thin rainbow ring round it, three arcs ')' trailing behind (cyan, pink, cyan, the outer ones 6 squares tall), 4 tiny white star glints placed symmetrically above and below; the arcs step back and the glints twinkle each frame.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 3. a_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a SOUND SPARK HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink 4-point star 6 squares across at the center; 2 a pink burst 8 squares across with a thin cyan ring 10 squares across round it; 3 the ring wider and thinner, 4 sparkles; 4 a few fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 4. a_note_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a CHARGED NOTE HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 8 squares across; 2 a pink burst 12 squares across inside a thin rainbow ring 14 squares across; 3 the ring wider, two small glowing note marks (a dot with a short stem) rising at mirrored places left and right; 4 the notes higher, the ring fading; 5 the notes fading.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 5. q_note

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a HIGH NOTE ORB in flight, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a bright white-pink orb 6 squares across with a cyan ring 9 squares across round it and a thin rainbow band on the ring, 2 small sparkles trailing to the LEFT at mirrored heights; the ring brightens and dims frame to frame (no spinning).
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 6. q_land

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a HIGH NOTE SHOCKWAVE on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 a bright white-pink ellipse spark 12 squares wide at the center; 2 an elliptical ring 30 squares wide, 2 squares thick, pink with a cyan outer edge, 4 short white light rays rising from the center; 3 the ring 46 squares wide with a thin rainbow band, the rays tallest (8 squares); 4 the ring 58 squares wide and 22 tall, thinner; 5 the ring breaking into sparkles; 6 a few fading sparkles.
Layout: one horizontal row of 6 equal 62:26 cells, image size 5952x416 (each cell 992x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 7. q_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a HIGH NOTE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink star 7 squares across; 2 a pink burst 10 squares across with short cyan arcs '( )' on both sides; 3 the arcs moving out, 4 sparkles; 4 fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 8. q_amp

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C) and a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A).
Effect: a CRITICAL HIGH NOTE BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white 8-point star 8 squares across; 2 a gold-pink burst 14 squares across with 8 long gold rays; 3 the rays longest (18 squares across), a white core; 4 the rays breaking into sparkles; 5 fading sparkles.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 9. e_wave

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a SOUND WAVE FRONT moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a tall bright white-pink arc ')' 18 squares tall and 2 squares thick at the right, a thin rainbow sheen along it, two fainter cyan arcs behind it to the left, 4 small sparkles at mirrored heights; the back arcs flicker and step each frame.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); the front arc 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 10. e_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A).
Effect: a SOUND RIPPLE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan flash 6 squares across; 2 two concentric rings (cyan outside, pink inside) 10 squares across; 3 the rings 14 squares across, thinner, 4 sparkles; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration from the corresponding effect family, NOT its texture softness, labels or backdrop. Draw ONLY this effect and exactly the requested frame count, no characters. Directly author true tiny pixel shapes, each logical square one flat color. No dark outline, no gradients or soft halos. Background must have genuine transparent alpha.
```

### 11. e_root

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: a MUSIC STAFF SHACKLE round a figure's feet, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an elliptical ring made of 3 thin parallel glowing lines (like a music staff) 20 squares wide and 8 tall round an empty center, pink and cyan, 4 small gold note dots on it at mirrored places; 1 it appears wide and faint, 2-3 it tightens and shines, 4 it flashes, 5 it dims, 6 it fades.
Layout: one horizontal row of 6 equal 22:12 cells, image size 2112x192 (each cell 352x192, 16 px a square); the ring centered in every cell, its middle empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha.
```

### 12. e_stun

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C), a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a DIZZY CROWN of notes over a head, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 16 squares wide and 5 tall made of 6 small glowing note marks and stars (gold, pink, a rainbow glint) placed symmetrically; each frame a different pair brightens (mirrored), the others dim.
Layout: one horizontal row of 4 equal 20:10 cells, image size 1280x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha.
```

### 13. w_cast

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue shield ramp (#FFFFFF, #F0F8FF, #C8E8FF, #9ACCF8, #5A9AE0), a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a SONG RING spreading on the ground from her feet, seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, its middle empty: 1 a bright white-blue ellipse 20 squares wide; 2 an elliptical ring 50 squares wide, 2 squares thick, white-blue with a pink inner edge, 6 short light pillars rising from it; 3 the ring 80 squares wide, a thin rainbow band, the pillars tallest (10 squares); 4 the ring 98 squares wide and 34 tall, thinner, note sparkles drifting up; 5 the ring fading into sparkles; 6 a few fading sparkles.
Layout: one horizontal row of 6 equal 102:38 cells, image size 9792x608 (each cell 1632x608, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha.
```

### 14. w_on

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue shield ramp (#FFFFFF, #F0F8FF, #C8E8FF, #9ACCF8, #5A9AE0).
Effect: a SHIELD BUBBLE round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY: an upright ellipse outline 24 squares wide and 32 tall, 1 square thick, white-blue, brighter at the top, two short highlight arcs at mirrored places near the top, two short speed streaks under it at mirrored places; the outline's bright part shimmers frame to frame.
Layout: one horizontal row of 4 equal 28:36 cells, image size 1792x576 (each cell 448x576, 16 px a square); the bubble centered in every cell, its bottom 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha.
```

### 15. w_heal

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green-white heal ramp (#FFFFFF, #E6FFE0, #A8F5A0, #5CDC6A, #2E9A44) and a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A).
Effect: a HEAL, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a soft green-white glow 10 squares across at the bottom; 2 the glow rising, 2 small pink hearts and 2 green plus-sparkles at mirrored places; 3-4 the hearts and sparkles rising higher; 5 fading near the top; 6 a few fading sparkles.
Layout: one horizontal row of 6 equal 18:24 cells, image size 1728x384 (each cell 288x384, 16 px a square); centered across, the glow at the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha.
```

### 16. r_wave

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a GREAT SOUND WAVE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a thick bright white-pink arc ')' 36 squares tall and 3 squares thick at the right with a rainbow sheen, three fading arcs behind it (pink, cyan, pink), 6 small note marks and tiny hearts floating between the arcs at mirrored heights; the back arcs ripple each frame.
Layout: one horizontal row of 4 equal 28:38 cells, image size 1792x608 (each cell 448x608, 16 px a square); the front arc 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha. Leave generous blank gutters between equal width frames.
```

### 17. r_cast

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C), a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a STAGE SPOTLIGHT round her, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: a cone of gold-pink light from the top of the cell widening down to a bright ellipse on the ground 30 squares wide at the bottom, drawn only as its two edges and soft streaks (not filled over the figure), two thinner slanted stage-light beams from the top corners, 6 star sparkles at mirrored places; 1 faint, 2-3 brightest, 4 beginning to fade, 5-6 fading.
Layout: one horizontal row of 6 equal 46:58 cells, image size 4416x928 (each cell 736x928, 16 px a square); centered across, the ground ellipse on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
CRITICAL: Every frame is a HOLLOW light cone, just two thin pink-gold boundary lines. The ENTIRE interior is transparent. NO central beam, NO filled cone, NO broad glowing curtain. Empty torso space is vital. Ground ring also hollow. Each frame keeps the same geometry but gradually fades by reducing opaque pixels.
True transparent background. ONLY effect; no characters, no backdrop, no labels, no blur. Exactly requested equal frame cells.
```

### 18. r_hit

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a CHARM BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 8 squares across; 2 a pink burst 14 squares across with a big pink heart 6 squares across at its center; 3 the big heart and 4 small hearts rising at mirrored places; 4 the hearts higher, fading; 5 a few fading sparkles.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha. Leave generous blank gutters between equal width frames.
```

### 19. echo

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly, a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: an ECHO RING round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its middle EMPTY: 1 an upright ellipse outline 20 squares wide and 30 tall, white; 2 the ellipse 28 wide and 38 tall with a rainbow band (red at the top through violet at the bottom, mirrored left and right), 8 white star sparkles round it; 3 the widest (32 x 42), sparkles flying out; 4 the band fading, sparkles farther; 5 a few fading sparkles.
Layout: one horizontal row of 5 equal 36:46 cells, image size 2880x736 (each cell 576x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha. Leave generous blank gutters between equal width frames.
```

### 20. n1

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: ONE FLOATING NOTE over a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: one glowing pink note mark (a round dot 3 squares across with a short upright stem in the middle, symmetric) 2 squares above the top center of the cell's figure area, a tiny gold glint on it; it bobs 1 square up and down through the loop.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure area is the middle 18 x 34 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
CRITICAL: Center-top note is NOT the conventional leaning eighth-note silhouette. It is a perfectly symmetric round dot with a straight central vertical stem, like a round bulb on a stick. Keep each note only 3-4 logical squares wide, 5 high. Notes sit OUTSIDE the middle 18x34 figure area, which stays entirely transparent. Preserve all blank margins and precise 32x42 cell layout. 4 equal frames.
True transparent background. ONLY effect; no characters, no backdrop, no labels, no blur. Exactly requested equal frame cells.
```

### 21. n2

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: TWO FLOATING NOTES round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: two glowing pink note marks (as n1) above the figure's head, one left and one right, mirrored; they bob 1 square up and down together.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure area is the middle 18 x 34 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha. Leave generous blank gutters between equal width frames.
```

### 22. n3

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: THREE FLOATING NOTES round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: one glowing pink note mark above the head's center and two cyan-pink ones at the sides of the head, mirrored; they bob 1 square.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure area is the middle 18 x 34 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
CRITICAL: Center-top note is NOT the conventional leaning eighth-note silhouette. It is a perfectly symmetric round dot with a straight central vertical stem, like a round bulb on a stick. Keep each note only 3-4 logical squares wide, 5 high. Notes sit OUTSIDE the middle 18x34 figure area, which stays entirely transparent. Preserve all blank margins and precise 32x42 cell layout. 4 equal frames.
True transparent background. ONLY effect; no characters, no backdrop, no labels, no blur. Exactly requested equal frame cells.
```

### 23. n4

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8), a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: FOUR FLOATING NOTES round a figure (full), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: four brighter glowing note marks with a rainbow glint, two beside the head and two beside the waist, mirrored; they bob 1 square, the upper pair and the lower pair alternating.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure area is the middle 18 x 34 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha. Leave generous blank gutters between equal width frames.
```

### 24. echo_ready

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly and a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A).
Effect: an ECHO-READY GLOW under a floating stage, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse glow 28 squares wide and 6 tall, a thin rainbow band round a pale pink middle, 4 sparkles at mirrored places; it pulses brighter and dimmer.
Layout: one horizontal row of 4 equal 32:10 cells, image size 2048x160 (each cell 512x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
Reference image is ONLY shape inspiration, NOT softness, labels or backdrop. Generate ONLY this effect, exact requested frame count, no characters. Each logical square a flat color. No dark outlines, gradients or soft halos. Genuine transparent alpha. Leave generous blank gutters between equal width frames.
```

### 25. e_slow

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a SLOWING STAFF under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an elliptical ring 14 squares wide and 4 tall made of 2 thin parallel cyan lines, a pale glow inside; it pulses.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
CRITICAL: Generous transparent margin inside every frame; do not clip the last frame. Exactly four equal-width cells. No blur or glow, pure flat squares. TWO SEPARATE parallel flat elliptical cyan rings, stacked vertically a little, BOTH centers hollow except a few pale pixels; no central starburst. Rings 14x4 logical squares each.
```
