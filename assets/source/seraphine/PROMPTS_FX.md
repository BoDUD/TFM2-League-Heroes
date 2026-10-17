# 星籁歌姬 萨勒芬妮：给 Codex 的特效提示词（第 3 步）

> **这一份是 25 张特效图。** 造型和动作已定（`design/seraphine_design.png`，8 倍，416 行、304 格宽，连脚下的浮空舞台）。
> - 大小对照 `design/seraphine_size.png`：定稿造型放大 4 倍，舞台底在红线上，上面是 10 格一段的刻度，右边是原版斗士。萨勒芬妮 304×416 格。每条写的大小都是游戏像素（格）。
> - `design/seraphine_shots.png`：定稿动作（4 倍），青色十字是特效的起点（伸出去的手、脚下），导入时 Claude 把特效放到这里。
> - 参考图 `refs/lol_fx_ref.png` 是英雄联盟里萨勒芬妮自己的特效贴图（大多是灰度的形状，游戏里再上色），按用在我们哪张特效分好了行，只在本地用，不要提交。颜色照英雄联盟原版：**她的光是粉白色和青色，音符和声波上带一点彩虹光；舞台灯是金粉色；治疗是绿白色；魅惑是粉色爱心**。
> - **特效要亮**：每个形状都要用最亮的几档和白色的芯，暗底上一眼能看见。
> - **围着人的光环、泡泡、聚光灯、音符只画外圈，中间留空**，不然会把人整个挡住。
> - **方向（重要，红色方会镜像）**：飞出去的音球、高音、声波、大招音波画成朝右飞，游戏会按飞行方向转，而且要**上下对称**（往左飞时会上下翻）。画在人身上、脚下的（打中、定身、眩晕、治疗、魅惑、回音、聚光灯、护盾泡泡、音符、减速）都要**严格左右对称**（逐格对称，游戏不会给它们镜像）；地上的 `q_land`、`w_cast` 上下左右都对称。
> - 特效照下面第 1–25 条和「所有特效图的规则」画，每张一个 PNG，文件名 `seraphine_fx_<名字>.png`，排版按每条写的来（每条最后一句的格子尺寸为准，1 格 = 16 像素）。
> - **请同时交游戏尺寸版**：每张再整理一份 1 格 = 1 像素的原尺寸条，放在 `pixel_1x/`（文件名一样），严格按格子取色、透明度只有 0 和 255、要求对称的逐格对称——Claude 直接用这一份切格导入。
> - 生图原稿（半透明边、格子比例不准）也一起交在 `raw/`。每张请保持等宽的格子（比例按每条写的），不要标签、不要边框，背景透明（做不到就用纯黑 `#000000`）。**请用生图画，不要用代码拼方块**。
> - 交回时附 `HANDOFF.md`（每张用了哪条提示词、画了几帧、有没有没做到的地方），最后写。最好打成一个 zip（`seraphine_fx_done.zip`）放在 outputs 里，或放在 `outputs/seraphine-fx/`。

## 技能方案（每张图用在哪里）

| 技能位 | 内容 | 用到的图 |
|---|---|---|
| 普攻 + 被动「星光漫射」 | 音球普攻；放技能攒音符（最多 4 个），下次普攻带音符多打一下；每第 3 个技能回音再放一次 | `a_bolt` · `a_note` · `a_hit` · `a_note_hit` · `n1`–`n4` · `echo` · `echo_ready` |
| 技能 1 = Q「清籁穿云」 | 抛出高音，落地炸开一圈声波；对被控制的英雄多打 | `q_note` · `q_land` · `q_hit` · `q_amp` |
| 技能 2 = E「增幅节拍」→ W「聚和心声」 | 往前推一道声波：减速，回音那道定身，已被控制的眩晕；接着唱歌给身边友军护盾加速，之后治疗 | `e_wave` · `e_hit` · `e_slow` · `e_root` · `e_stun` · `w_cast` · `w_on` · `w_heal` |
| 大招 = R「炫音返场」 | 舞台灯亮起，推出一道很宽的音波，魅惑敌方英雄 | `r_cast` · `r_wave` · `r_hit` |

## 所有特效图的规则

- 像素画：方块清楚、硬边、没有抗锯齿、没有模糊和柔光。**光、声波、星光、光环都没有黑描边，也不要用最深的颜色给形状描一圈边**。
- **要亮**：每个形状都有白色或最亮一档的芯，暗部最多用到每个色阶的倒数第二档，最深的一档只给很少的点缀；彩虹色只做点缀（细细的一道或几个点）。
- 颜色（按每条写的用）：
  - 粉白舞台光（音球、音符、声波）：`#FFFFFF`、`#FFE6F6`、`#FF9AD8`、`#F04AA8`、`#A8207A`；
  - 青色声波：`#FFFFFF`、`#D8FBFF`、`#8AEFFF`、`#30C8F0`、`#1878B8`；
  - 金色星光、舞台灯：`#FFFFFF`、`#FFF6C0`、`#FFE68A`、`#FCC23A`、`#C88A1C`；
  - 彩虹点缀：`#FF6E8E`、`#FFC44A`、`#FFF06A`、`#7CF07A`、`#5FD8FF`、`#9A7CFF`；
  - 绿白治疗：`#FFFFFF`、`#E6FFE0`、`#A8F5A0`、`#5CDC6A`、`#2E9A44`；
  - 白蓝护盾：`#FFFFFF`、`#F0F8FF`、`#C8E8FF`、`#9ACCF8`、`#5A9AE0`；
- 打中、爆发居中画，不旋转；地面上、绕身体的圆是从斜上方看的椭圆（宽是高的 2–3 倍）。
- 画在她或别人身上、脚下的画面按每条写的站位画，**格子里留出空的人形位置，不要画人**。
- 背景透明（做不到时用纯黑 `#000000`）。不要网格线、边框、文字、编号。

---

## 特效（25 张）

25 张特效的提示词都以同一段画风开头。大小写在每条里，导入时 Claude 按技能范围缩放（1 个游戏像素约等于 1000 距离单位：攻击距离 55000，高音半径 30000，声波宽 9000，大招音波宽 18000，护盾范围 50000）。

### 1. `seraphine_fx_a_bolt.png`：普攻：飞出去的音波光点（飞行中，循环），4 帧

萨勒芬妮的普攻：一颗粉白色的发光小音球，前面亮、后面拖两道弧形的青色声波 `)`（参考 BasicAttack、Flash、Q_Cas_Soundwaves）。朝右飞。**上下对称**。4 帧无缝循环（光点闪、声波一闪一闪往后退）。约 10 格长、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a SOUND ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a bright white-pink orb 3 squares across at the right, a soft pink glow round it, two thin cyan arcs ')' 4 squares tall trailing behind it to the left; each frame the arcs step back one square and the glow pulses.
Layout: one horizontal row of 4 equal 12:8 cells, image size 768x128 (each cell 192x128, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 2. `seraphine_fx_a_note.png`：普攻（带音符）：更大的彩色音波光点（飞行中，循环），4 帧

攒满音符后的普攻：一颗更大的粉白发光音球，外面绕一圈彩虹光，后面拖三道青粉相间的声波弧，周围有几颗小星光（参考 P_LensFlare、Light_sparks、Q_RainbowMult）。朝右飞。**上下对称**。4 帧无缝循环。约 14 格长、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a CHARGED SOUND ORB flying to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a bright white-pink orb 5 squares across with a thin rainbow ring round it, three arcs ')' trailing behind (cyan, pink, cyan, the outer ones 6 squares tall), 4 tiny white star glints placed symmetrically above and below; the arcs step back and the glints twinkle each frame.
Layout: one horizontal row of 4 equal 16:10 cells, image size 1024x160 (each cell 256x160, 16 px a square); the orb's front 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 3. `seraphine_fx_a_hit.png`：普攻打中（目标身上），4 帧

普攻打中：一小朵粉白色的星光炸开，一圈青色小声波往外扩（参考 Flash、Base_GlowRing）。**左右对称**。约 12 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a SOUND SPARK HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink 4-point star 6 squares across at the center; 2 a pink burst 8 squares across with a thin cyan ring 10 squares across round it; 3 the ring wider and thinner, 4 sparkles; 4 a few fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 896x224 (each cell 224x224, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 4. `seraphine_fx_a_note_hit.png`：带音符的普攻打中，5 帧

带音符的普攻打中：一团更大的粉白光炸开，一圈彩虹声波环，几颗音符形状的小光点往上飘（参考 E_Passive_Mark 音符、Light_sparks、Q_LeadingEdge_Ring）。**左右对称**（音符光点左右各一个，镜像摆）。约 16 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a CHARGED NOTE HIT, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 8 squares across; 2 a pink burst 12 squares across inside a thin rainbow ring 14 squares across; 3 the ring wider, two small glowing note marks (a dot with a short stem) rising at mirrored places left and right; 4 the notes higher, the ring fading; 5 the notes fading.
Layout: one horizontal row of 5 equal square cells, image size 1440x288 (each cell 288x288, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 5. `seraphine_fx_q_note.png`：Q 清籁穿云：抛出去的高音（飞行中，循环），4 帧

萨勒芬妮抛出的高音：一颗亮粉色的大音球，外面一圈青色光环，环上有一道彩虹光，后面拖一点星光（参考 Diana_Base_Q_Glow、Base_Q_GlowGrid、Q_RainbowMult）。**上下对称**。4 帧无缝循环（光环一亮一暗，不画旋转）。约 10 格。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a HIGH NOTE ORB in flight, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a bright white-pink orb 6 squares across with a cyan ring 9 squares across round it and a thin rainbow band on the ring, 2 small sparkles trailing to the LEFT at mirrored heights; the ring brightens and dims frame to frame (no spinning).
Layout: one horizontal row of 4 equal square cells, image size 768x192 (each cell 192x192, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 6. `seraphine_fx_q_land.png`：Q 高音落地：地上炸开的声波环（地上，画在人物下面），6 帧

高音落地：地上一圈从斜上方看的扁椭圆声波环从中间扩开，环上有彩虹光，中间往上射出几道短光柱（参考 Q_LeadingEdge_Ring、Seraphine_Q_Ring、Q_4x1_Rays、Radialring）。**上下左右都对称**。这是技能的范围（半径 30 格），最大一帧画满：约 60 格宽、24 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a HIGH NOTE SHOCKWAVE on the ground seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame: 1 a bright white-pink ellipse spark 12 squares wide at the center; 2 an elliptical ring 30 squares wide, 2 squares thick, pink with a cyan outer edge, 4 short white light rays rising from the center; 3 the ring 46 squares wide with a thin rainbow band, the rays tallest (8 squares); 4 the ring 58 squares wide and 22 tall, thinner; 5 the ring breaking into sparkles; 6 a few fading sparkles.
Layout: one horizontal row of 6 equal 62:26 cells, image size 5952x416 (each cell 992x416, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 7. `seraphine_fx_q_hit.png`：Q 打中（每个被高音打中的人身上），4 帧

被高音打中：人身上一朵粉白色的星光炸开，几道青色的短声波往外（参考 Flash、Q_Cas_Soundwaves）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a HIGH NOTE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink star 7 squares across; 2 a pink burst 10 squares across with short cyan arcs '( )' on both sides; 3 the arcs moving out, 4 sparkles; 4 fading sparkles.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 8. `seraphine_fx_q_amp.png`：Q 对被控制英雄的加伤（他身上），5 帧

高音对被控制的英雄多打一下：一颗金粉色的大星光在他身上炸开，金色光芒往四周射（参考 FlashGreen 的形状、common_flareblue）。**左右对称**。约 18 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C) and a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A).
Effect: a CRITICAL HIGH NOTE BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white 8-point star 8 squares across; 2 a gold-pink burst 14 squares across with 8 long gold rays; 3 the rays longest (18 squares across), a white core; 4 the rays breaking into sparkles; 5 fading sparkles.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 9. `seraphine_fx_e_wave.png`：E 增幅节拍：往前推的声波（飞行中，循环），4 帧

萨勒芬妮往前推出的一道声波：一道竖着的弧形声波前沿 `)`，前沿最亮（白粉色），后面跟两道淡一点的青色弧，弧上有一丝彩虹光，几颗音符光点（参考 E_Wave_Alphablend、E_Trail_01/02、E_Electric_Arcs）。朝右推。**上下对称**。4 帧无缝循环（后面的弧一闪一闪）。约 14 格长、18 格高（这是声波的宽度）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a SOUND WAVE FRONT moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a tall bright white-pink arc ')' 18 squares tall and 2 squares thick at the right, a thin rainbow sheen along it, two fainter cyan arcs behind it to the left, 4 small sparkles at mirrored heights; the back arcs flicker and step each frame.
Layout: one horizontal row of 4 equal 16:20 cells, image size 1024x320 (each cell 256x320, 16 px a square); the front arc 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 10. `seraphine_fx_e_hit.png`：E 打中（每个被声波打中的人身上），4 帧

被声波打中：人身上一圈青粉色的声波涟漪往外扩，几颗小光点（参考 Shockwave02、Base_GlowRing）。**左右对称**。约 14 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A).
Effect: a SOUND RIPPLE HIT, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-cyan flash 6 squares across; 2 two concentric rings (cyan outside, pink inside) 10 squares across; 3 the rings 14 squares across, thinner, 4 sparkles; 4 fading.
Layout: one horizontal row of 4 equal square cells, image size 1024x256 (each cell 256x256, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 11. `seraphine_fx_e_root.png`：E 定身（被定住的人脚下），6 帧

被回音的声波定住：脚下一圈五线谱一样的光环把他圈住（几条平行的亮线组成的扁椭圆环），环上挂几个音符光点（参考 E_Passive_Mark_2_Rooted、E_Passive_Mark_2_Background、E_Dots）。**左右对称**。6 帧（约 0.75 秒）：亮起、收紧、闪两下、淡去。约 20 格宽、10 格高，**中间留空**（人在中间）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: a MUSIC STAFF SHACKLE round a figure's feet, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an elliptical ring made of 3 thin parallel glowing lines (like a music staff) 20 squares wide and 8 tall round an empty center, pink and cyan, 4 small gold note dots on it at mirrored places; 1 it appears wide and faint, 2-3 it tightens and shines, 4 it flashes, 5 it dims, 6 it fades.
Layout: one horizontal row of 6 equal 22:12 cells, image size 2112x192 (each cell 352x192, 16 px a square); the ring centered in every cell, its middle empty. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 12. `seraphine_fx_e_stun.png`：E 眩晕（被晕的人头顶，循环），4 帧

被眩晕：头顶一圈绕着转的小音符光点和小星星（参考 E_Passive_Mark 音符、Light_sparks）。**左右对称**（每一帧都对称：光点在两边对称地一闪一闪，不画转圈）。约 18 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C), a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a DIZZY CROWN of notes over a head, 4 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse 16 squares wide and 5 tall made of 6 small glowing note marks and stars (gold, pink, a rainbow glint) placed symmetrically; each frame a different pair brightens (mirrored), the others dim.
Layout: one horizontal row of 4 equal 20:10 cells, image size 1280x160 (each cell 320x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 13. `seraphine_fx_w_cast.png`：W 聚和心声：她身边扩开的歌声光环（地上，画在人物下面），6 帧

萨勒芬妮唱歌：从她脚下扩开一圈很大的扁椭圆光环（白蓝色，带一层粉光），环上往上射几道短光柱，几颗音符光点往外飘（参考 Seraphine_W_ShieldRing、W_Light、W_ShieldHighlight、P_StageLights_Up）。**上下左右都对称**，**中间留空**（她站在中间）。这是护盾的范围（半径 50 格），最大一帧约 100 格宽、36 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue shield ramp (#FFFFFF, #F0F8FF, #C8E8FF, #9ACCF8, #5A9AE0), a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a SONG RING spreading on the ground from her feet, seen from above at an angle, 6 frames, SYMMETRIC LEFT TO RIGHT AND TOP TO BOTTOM in every frame, its middle empty: 1 a bright white-blue ellipse 20 squares wide; 2 an elliptical ring 50 squares wide, 2 squares thick, white-blue with a pink inner edge, 6 short light pillars rising from it; 3 the ring 80 squares wide, a thin rainbow band, the pillars tallest (10 squares); 4 the ring 98 squares wide and 34 tall, thinner, note sparkles drifting up; 5 the ring fading into sparkles; 6 a few fading sparkles.
Layout: one horizontal row of 6 equal 102:38 cells, image size 9792x608 (each cell 1632x608, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 14. `seraphine_fx_w_on.png`：W 护盾 + 加速（友方英雄身上，循环），4 帧

被唱歌护住的友方英雄：身上罩一层淡淡的白蓝色泡泡（只画轮廓一圈亮边和一两道高光），脚下两道向后的小速度线（参考 Seraphine_W_ShieldRing、W_ShieldHighlight）。**左右对称**，**中间留空**（人在泡泡里，只画外圈）。4 帧无缝循环（亮边一闪一闪）。约 26 格宽、34 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a white-blue shield ramp (#FFFFFF, #F0F8FF, #C8E8FF, #9ACCF8, #5A9AE0).
Effect: a SHIELD BUBBLE round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its inside EMPTY: an upright ellipse outline 24 squares wide and 32 tall, 1 square thick, white-blue, brighter at the top, two short highlight arcs at mirrored places near the top, two short speed streaks under it at mirrored places; the outline's bright part shimmers frame to frame.
Layout: one horizontal row of 4 equal 28:36 cells, image size 1792x576 (each cell 448x576, 16 px a square); the bubble centered in every cell, its bottom 2 squares above the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 15. `seraphine_fx_w_heal.png`：W 治疗（友方英雄身上），6 帧

护盾之后的治疗：友方英雄身上冒出一团绿白色的光，几颗粉色小爱心和绿色十字光点往上飘（参考 P_HeartSparkles、global_ss_heal_sparkle）。**左右对称**。约 16 格宽、22 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a green-white heal ramp (#FFFFFF, #E6FFE0, #A8F5A0, #5CDC6A, #2E9A44) and a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A).
Effect: a HEAL, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a soft green-white glow 10 squares across at the bottom; 2 the glow rising, 2 small pink hearts and 2 green plus-sparkles at mirrored places; 3-4 the hearts and sparkles rising higher; 5 fading near the top; 6 a few fading sparkles.
Layout: one horizontal row of 6 equal 18:24 cells, image size 1728x384 (each cell 288x384, 16 px a square); centered across, the glow at the bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 16. `seraphine_fx_r_wave.png`：R 炫音返场：往前推的大声波（飞行中，循环），4 帧

大招的音波：一道很宽的弧形声浪往前推，前沿是亮粉白色的厚弧，后面拖三层越来越淡的粉、青弧，弧上有彩虹光，里面飘着几个音符光点和小爱心（参考 R_Front_Wave_Soft、R_Trail、R_Fill、Shockwave02）。朝右推。**上下对称**。4 帧无缝循环。约 26 格长、36 格高（这是音波的宽度）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a GREAT SOUND WAVE moving to the RIGHT, 4 frames, a seamless loop, SYMMETRIC TOP TO BOTTOM in every frame (the game turns it to its flight; flying left it is flipped upside down): a thick bright white-pink arc ')' 36 squares tall and 3 squares thick at the right with a rainbow sheen, three fading arcs behind it (pink, cyan, pink), 6 small note marks and tiny hearts floating between the arcs at mirrored heights; the back arcs ripple each frame.
Layout: one horizontal row of 4 equal 28:38 cells, image size 1792x608 (each cell 448x608, 16 px a square); the front arc 1 square from the RIGHT edge, vertically centered, in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 17. `seraphine_fx_r_cast.png`：R 炫音返场：她身边的舞台灯光（施法后，她身上），6 帧

萨勒芬妮开唱大招：头顶打下一束金粉色的舞台聚光灯，两边各一束斜着的舞台光，脚下一圈亮光，几颗星光闪（参考 R_Spotlight_Ground、P_StageLights_Up、MSI_Trophy_LightBeam）。**左右对称**，**中间留空**（她站在中间，光只画边缘和外面）。6 帧：亮起、最亮、淡去。约 44 格宽、56 格高，底边是她的脚底。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C), a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a STAGE SPOTLIGHT round her, 6 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: a cone of gold-pink light from the top of the cell widening down to a bright ellipse on the ground 30 squares wide at the bottom, drawn only as its two edges and soft streaks (not filled over the figure), two thinner slanted stage-light beams from the top corners, 6 star sparkles at mirrored places; 1 faint, 2-3 brightest, 4 beginning to fade, 5-6 fading.
Layout: one horizontal row of 6 equal 46:58 cells, image size 4416x928 (each cell 736x928, 16 px a square); centered across, the ground ellipse on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 18. `seraphine_fx_r_hit.png`：R 魅惑（被打中的敌方英雄身上），5 帧

被大招魅惑：人身上炸开一团粉色的爱心光，几颗小爱心往上飘（参考 P_HeartSparkles）。**左右对称**。约 18 格，居中画。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: a CHARM BURST, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): 1 a white-pink flash 8 squares across; 2 a pink burst 14 squares across with a big pink heart 6 squares across at its center; 3 the big heart and 4 small hearts rising at mirrored places; 4 the hearts higher, fading; 5 a few fading sparkles.
Layout: one horizontal row of 5 equal square cells, image size 1600x320 (each cell 320x320, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 19. `seraphine_fx_echo.png`：回音：第三个技能再放一次时她身上的回音光（施法后），5 帧

回音：她身边“叮”地亮起一圈彩虹色的光环和一圈星光，往外扩开（参考 Light_sparks、Dance_Sparks、Bokeh_Hex、Emote_Stardust）。**左右对称**，**中间留空**（她在中间）。5 帧。约 34 格宽、44 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly, a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: an ECHO RING round a figure, 5 frames, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), its middle EMPTY: 1 an upright ellipse outline 20 squares wide and 30 tall, white; 2 the ellipse 28 wide and 38 tall with a rainbow band (red at the top through violet at the bottom, mirrored left and right), 8 white star sparkles round it; 3 the widest (32 x 42), sparkles flying out; 4 the band fading, sparkles farther; 5 a few fading sparkles.
Layout: one horizontal row of 5 equal 36:46 cells, image size 2880x736 (each cell 576x736, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 20. `seraphine_fx_n1.png`：被动音符：她身边环绕的 1 个音符（循环），4 帧

攒了 1 个音符：她头顶正上方飘着 1 个粉色的发光音符光点（圆点加一小截竖杆，杆在正中，左右对称），上下轻轻浮动（参考 E_Passive_Mark 音符、P_Reveal）。**左右对称**，**中间留空**（她在中间）。4 帧无缝循环。约 30 格宽、40 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: ONE FLOATING NOTE over a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: one glowing pink note mark (a round dot 3 squares across with a short upright stem in the middle, symmetric) 2 squares above the top center of the cell's figure area, a tiny gold glint on it; it bobs 1 square up and down through the loop.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure area is the middle 18 x 34 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 21. `seraphine_fx_n2.png`：被动音符：环绕的 2 个音符（循环），4 帧

攒了 2 个音符：她头顶两侧各 1 个（左右镜像），上下轻轻浮动（两个交替）。**左右对称**，中间留空。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: TWO FLOATING NOTES round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: two glowing pink note marks (as n1) above the figure's head, one left and one right, mirrored; they bob 1 square up and down together.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure area is the middle 18 x 34 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 22. `seraphine_fx_n3.png`：被动音符：环绕的 3 个音符（循环），4 帧

攒了 3 个音符：头顶正上方 1 个、两侧各 1 个（左右镜像）。**左右对称**，中间留空。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8) and a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C).
Effect: THREE FLOATING NOTES round a figure, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: one glowing pink note mark above the head's center and two cyan-pink ones at the sides of the head, mirrored; they bob 1 square.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure area is the middle 18 x 34 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 23. `seraphine_fx_n4.png`：被动音符：环绕的 4 个音符（满了，循环），4 帧

攒满 4 个音符：头顶两侧各 1 个、腰两侧各 1 个（左右镜像），都更亮、带一点彩虹光。**左右对称**，中间留空。4 帧无缝循环。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A), a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8), a gold sparkle ramp (#FFFFFF, #FFF6C0, #FFE68A, #FCC23A, #C88A1C) and rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly.
Effect: FOUR FLOATING NOTES round a figure (full), 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side), the figure's place EMPTY: four brighter glowing note marks with a rainbow glint, two beside the head and two beside the waist, mirrored; they bob 1 square, the upper pair and the lower pair alternating.
Layout: one horizontal row of 4 equal 32:42 cells, image size 2048x672 (each cell 512x672, 16 px a square); the figure area is the middle 18 x 34 squares, its bottom on the cell's bottom. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 24. `seraphine_fx_echo_ready.png`：回音就绪（下一个技能会回音，循环），4 帧

回音就绪：她舞台下面一圈淡淡的彩虹光一闪一闪（参考 P_Reveal、Idle_Platformhover_Whoosh）。**左右对称**。4 帧无缝循环。约 30 格宽、8 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from rainbow accents (#FF6E8E, #FFC44A, #FFF06A, #7CF07A, #5FD8FF, #9A7CFF) used sparingly and a pink stage-light ramp (#FFFFFF, #FFE6F6, #FF9AD8, #F04AA8, #A8207A).
Effect: an ECHO-READY GLOW under a floating stage, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): a flat ellipse glow 28 squares wide and 6 tall, a thin rainbow band round a pale pink middle, 4 sparkles at mirrored places; it pulses brighter and dimmer.
Layout: one horizontal row of 4 equal 32:10 cells, image size 2048x160 (each cell 512x160, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

### 25. `seraphine_fx_e_slow.png`：E 减速（被减速的人脚下，循环），4 帧

被声波减速：脚下一圈淡青色的五线谱光（两三条平行的弧线组成的扁椭圆），一闪一闪（参考 E_Passive_Mark_2_Slowed）。**左右对称**。4 帧无缝循环。约 16 格宽、6 格高。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels, hard edges, no anti-aliasing, NO outline around light, waves, sparkles or rings, BRIGHT colours (each shape lit with its lightest shades and a white core - it must read on a dark battlefield), colours only from a cyan sound ramp (#FFFFFF, #D8FBFF, #8AEFFF, #30C8F0, #1878B8).
Effect: a SLOWING STAFF under a figure's feet, 4 frames, a seamless loop, SYMMETRIC LEFT TO RIGHT in every frame, square for square (the game never mirrors it on the red side): an elliptical ring 14 squares wide and 4 tall made of 2 thin parallel cyan lines, a pale glow inside; it pulses.
Layout: one horizontal row of 4 equal 18:8 cells, image size 1152x128 (each cell 288x128, 16 px a square); centered in every cell. Transparent background (if not possible: pure black #000000). No gaps, no borders, no labels.
```

---

## Claude 导入时的对应关系（给 Claude 看）

| 特效图 | 绑定 | 大小（游戏像素） |
|---|---|---|
| `seraphine_fx_a_bolt` | view_projectiles `league_seraphine_a_bolt`（朝飞行方向转，画成朝右飞；上下对称） | 10 × 6 |
| `seraphine_fx_a_note` | view_projectiles `league_seraphine_a_note`（同上；上下对称） | 14 × 8 |
| `seraphine_fx_a_hit` | view_effects `league_seraphine_a_hit`（跟随，画在人物上面；左右对称） | 12 |
| `seraphine_fx_a_note_hit` | view_effects `league_seraphine_a_note_hit`（跟随；左右对称） | 16 |
| `seraphine_fx_q_note` | view_projectiles `league_seraphine_q_note`（抛物线飞行；上下对称） | 10 × 10 |
| `seraphine_fx_q_land` | view_effects `league_seraphine_q_land`（落点上，不旋转，画在人物下面；上下左右都对称） | 60 × 24 |
| `seraphine_fx_q_hit` | view_effects `league_seraphine_q_hit`（跟随；左右对称） | 14 |
| `seraphine_fx_q_amp` | view_effects `league_seraphine_q_amp`（跟随；左右对称） | 18 |
| `seraphine_fx_e_wave` | view_projectiles `league_seraphine_e_wave`（直线飞行，朝飞行方向转，画成朝右；上下对称） | 14 × 18 |
| `seraphine_fx_e_hit` | view_effects `league_seraphine_e_hit`（跟随；左右对称） | 14 |
| `seraphine_fx_e_root` | view_effects `league_seraphine_e_root`（跟随，画在人物下面；左右对称） | 20 × 10 |
| `seraphine_fx_e_stun` | view_effects `league_seraphine_e_stun`（跟随；左右对称） | 18 × 8 |
| `seraphine_fx_w_cast` | view_effects `league_seraphine_w_cast`（施法后播放、不跟随，画在人物下面；上下左右都对称） | 100 × 36 |
| `seraphine_fx_w_on` | view_buffs `league_seraphine_w_on`（跟随；左右对称） | 26 × 34 |
| `seraphine_fx_w_heal` | view_effects `league_seraphine_w_heal`（跟随；左右对称） | 16 × 22 |
| `seraphine_fx_r_wave` | view_projectiles `league_seraphine_r_wave`（直线飞行，朝飞行方向转，画成朝右；上下对称） | 26 × 36 |
| `seraphine_fx_r_cast` | view_effects `league_seraphine_r_cast`（施法后播放、不跟随，画在人物上面；左右对称） | 44 × 56 |
| `seraphine_fx_r_hit` | view_effects `league_seraphine_r_hit`（跟随；左右对称） | 18 |
| `seraphine_fx_echo` | view_effects `league_seraphine_echo`（施法后播放、不跟随，画在人物上面；左右对称） | 34 × 44 |
| `seraphine_fx_n1` | view_buffs `league_seraphine_n1`（跟随；左右对称） | 30 × 40 |
| `seraphine_fx_n2` | view_buffs `league_seraphine_n2`（跟随；左右对称） | 30 × 40 |
| `seraphine_fx_n3` | view_buffs `league_seraphine_n3`（跟随；左右对称） | 30 × 40 |
| `seraphine_fx_n4` | view_buffs `league_seraphine_n4`（跟随；左右对称） | 30 × 40 |
| `seraphine_fx_echo_ready` | view_buffs `league_seraphine_echo`（跟随；左右对称） | 30 × 8 |
| `seraphine_fx_e_slow` | view_buffs `league_seraphine_e_slow`（画在脚下；左右对称） | 16 × 6 |

- 音球、高音、声波、大招音波都从伸出去的手出（出手帧手在站位点前面 20–22 格、上面 26–36 格）；`bolt_y` 不超过约 8 格（太高的弹道会斜），画面开头补几帧空的，让音球离开手再出现。
- 没有烘进动作帧的特效：她的手发出所有东西，`w_cast`、`r_cast`、`echo` 晚于第一 tick，`is_follow` 为 false，逐格左右对称；`q_land`、`w_cast` 画在人物下面（z -1）。
- 用 `pixel_1x/` 切格（import_twitch 的做法），断言对称；清掉 Codex 给光描的最深色边；核对交回的张数和这份清单（`echo_ready` 的文件绑定 view_buffs 的 `echo`）；量每张的平均亮度和最亮的一成，和包里别的英雄比。
