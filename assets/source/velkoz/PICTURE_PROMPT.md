# 虚空之眼 维克兹：第 0 步，先画像素风原图（给 Codex 的提示词）

> 维克兹是一颗**漂浮的虚空之眼，没有腿**：身体就是一个大头——正中一只**发光的品红色大眼睛**，包在**卡其金色的甲壳**里（一层层叠起来的甲片，头顶一圈**尖刺冠**，大眼睛周围是**红紫色的肉质边缘**，大眼睛上方还有**三只品红色的小眼睛**）；甲壳下面和两侧伸出几条**又长又卷的深青黑色触手**，触手的尖端和内侧**透出品红色的光**。他**浮在空中**：最低的那圈触手也离地面有一点距离。请 Codex 画**两张全身像**（同一个维克兹，长相、颜色、**格子大小**都一样），都是 **3/4 正面朝右**（**不画正侧面**），用户从里面挑：
> - **A：英雄联盟里的待机**（附图 1、2、8a）：触手向两侧卷开，比较宽。
> - **B：更紧凑的 Q 版**：眼睛和甲壳占得更大，触手收在身体下面、往下垂着打卷，整体更窄更高。长相、颜色和 A 一模一样。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的科加斯、玛尔扎哈和克格莫（都是虚空的），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：Q 版，**甲壳和大眼睛约占身高的一半**，大眼睛要大、要清楚（瞳孔、亮的虹膜、暗的外圈分得开）；触手粗一点，不要细成一根线。
> - **眼睛**（附图 3 特写）：大眼睛是品红色、中间亮、外圈暗，有一个深色的竖瞳；上方三只小眼睛一样是品红色，每只至少 2 格；眼睛周围的红紫色肉边分 2 档。
> - **颜色**：卡其金色甲壳 3–4 档（亮边偏浅黄，暗处偏橄榄褐，**不要一团黑**），红紫色肉边 2–3 档，品红色的眼睛 3 档（最亮接近白粉），深青黑色触手 3 档（亮边偏青绿，暗处深蓝黑），触手尖端和内侧品红色 2 档。
> - **画布用正方形 1536×1536**。**维克兹从头顶尖刺冠的顶端到最低那圈触手约 682 px，也就是约 62 格**；他是飘着的，**最低的触手在地面线（附图 8a 的灰线）上方约 2 格**，站在附图 8a 的位置。尖刺冠、所有触手全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（等离子球、射线、裂隙、发光的光晕都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/velkoz-picture/velkoz-A.png`、`velkoz-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/velkoz-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/velkoz_picture_done.zip`。

## 附图（在压缩包 `velkoz_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_velkoz_idle.png` | 英雄联盟原版维克兹的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_velkoz_frontal.png` | 同一帧，正面 | 甲壳、大眼睛、三只小眼睛、触手从哪里长出来 |
| `refs/3_velkoz_eye.png` | 头部特写（3/4） | 大眼睛、小眼睛、肉边、尖刺冠 |
| `refs/4_velkoz_back.png` | 同一帧的背后 | 背面的甲片、触手根部 |
| `refs/5_velkoz_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_velkoz_attack.png` | 普攻的一帧，3/4 朝右 | 触手和眼睛在动作里的样子 |
| `refs/7_velkoz_side.png` | 待机的侧面 | 只看甲壳的厚度和触手的走向（**不要画侧面**） |
| `refs/8a_layout_front.png` | 布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰线）、尖刺冠顶端的高度（浅灰线）；最低的触手在灰线上方约 2 格 |
| `style/11_style_chogath.png` | 本包的科加斯，8 倍放大，一格 = 一个像素 | **只看风格**：虚空生物的甲壳、尖刺、深色身体的亮边 |
| `style/12_style_malzahar.png` | 本包的玛尔扎哈（8 倍） | **只看风格**：漂浮的人物、品红 / 紫色的虚空光 |
| `style/13_style_kogmaw.png` | 本包的克格莫（8 倍） | **只看风格**：虚空生物的眼睛、甲片 |

## 提示词：`velkoz-A.png` / `velkoz-B.png`（同一段提示词，只换最后一句）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-7 are 3D renders and art of a character from the game: a FLOATING VOID EYE WITH NO LEGS - his body is one big head: ONE HUGE GLOWING MAGENTA EYE in the middle of a KHAKI-GOLD ARMOURED CARAPACE (overlapping plates, a CROWN OF SPIKES on top, RED-VIOLET FLESHY RIMS round the big eye, THREE SMALL MAGENTA EYES above it); several LONG CURLING DARK TEAL-BLACK TENTACLES come out under and beside the carapace, their tips and undersides glowing MAGENTA (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the carapace, the big eye, the three small eyes, where the tentacles grow; 3 the head close-up: the eyes, the fleshy rims, the spike crown; 4 the same from behind: the back plates and the tentacle roots; 5 the official illustration: his mood and colours; 6 an attack, 3/4 view: the tentacles and the eye in motion; 7 the idle from the side: only how thick the carapace is and where the tentacles go - do NOT draw a side view). Image 8a is a layout guide: where he goes on the canvas and how big, the grey line is the ground, the light grey line the top of the spike crown; he FLOATS - the lowest tentacle about 2 squares above the ground line. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other void creatures from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a carapace with spikes and lit edges on a dark body (11), a floating figure and magenta-violet void light (12), a void creature's eyes and plates (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the spike crown, every tentacle); the lowest tentacle about 2 squares (22 px) ABOVE the ground line, which is about 146 px above the bottom edge (the grey line of image 8a) - he hovers, nothing touches the ground. He is about 682 px (about 62 squares) from the top of the spike crown to the lowest tentacle and floats where image 8a shows him.
THE VIEW: 3/4 front, FACING RIGHT (image 1) - NOT a side view, NOT a front view; the big eye turned toward the image right, the NEAR side of the carapace on the image left in full tone, the FAR side a step darker.
PROPORTIONS: chibi - the carapace with the big eye about HALF of his height, the big eye large and clear (a dark slit pupil, a bright iris, a darker outer ring); the tentacles thick enough to read (at least 3 squares wide near the root), never thin lines.
THE EYES: the big eye magenta, bright in the middle and darker outside, with a dark vertical slit pupil; the three small eyes above it also magenta, each at least 2 squares; the red-violet fleshy rims round the eyes in 2 shades.
THE COLOURS: the khaki-gold carapace in 3-4 shades (pale yellow lit edges, olive-brown shadows - never one black mass); the red-violet flesh in 2-3 shades; the magenta eyes in 3 shades (the brightest almost white-pink); the dark teal-black tentacles in 3 shades (teal-green lit edges, deep blue-black shadows); the tentacle tips and undersides in 2 magenta shades.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the khaki carapace, the red-violet flesh, the magenta eyes, the teal tentacles and their magenta tips clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no plasma bolts, no beam, no rift, no glow halo), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (velkoz-A.png): his idle as in League (images 1, 2 and 8a) - the tentacles curling out to both sides, a wide figure.
PICTURE B (velkoz-B.png): the SAME Vel'Koz in 3/4 view facing right, MORE COMPACT: the carapace and the big eye a little bigger, the tentacles gathered UNDER him, hanging down in curls, so the whole figure is narrower and taller; everything else (look, colours, square size, floating above the ground) exactly as in A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，尖刺冠、所有触手完整，不出画。
- 两张都是 **3/4 正面朝右**（不是侧面、不是正面）；**他飘着**，最低的触手在地面线上方约 2 格。
- Q 版：甲壳和大眼睛约占身高一半；大眼睛有深色竖瞳、亮虹膜、暗外圈；**三只小眼睛**看得见；肉边分档。
- 卡其金甲壳（亮边，不是一团黑）、红紫色肉边、品红眼睛、深青黑触手（尖端品红）；两张都是从尖刺冠顶端到最低触手约 682 px（约 62 格）。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 两张都画完后，最后写 `outputs/velkoz-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/velkoz_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/velkoz/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_warwick_hd.py` 的做法），和已合并的虚空英雄（科加斯、玛尔扎哈、卡萨丁）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑 A 还是 B、定大小（PPU 不要超过 1.5）。
- 用户：只做 3/4 面——第 1 步只在游戏格子上画 3/4 正面，动作都在 3/4 的造型上摆（婕拉、沃里克、梅尔的做法）；一张脸（大眼睛）用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Velkoz`）：普攻 Attack1–3 / Crit、Q Spell1（等离子裂变）、W Spell2（虚空裂隙）、E Spell3（构造分解）、R Spell4_in / Channel / Spell4（射线引导）、跑 run（漂浮）、死亡 Death。没有腿：走路就是整体飘、触手摆动（玛尔扎哈的漂浮做法）。
