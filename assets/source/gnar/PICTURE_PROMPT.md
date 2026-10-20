# 迷失之牙 纳尔：第 0 步，先画像素风原图（给 Codex 的提示词）

> 纳尔有**两种形态**，这一步两种都画，用户从里面挑：
> - **迷你纳尔**：一只**小小的橙色毛茸茸的约德尔幼崽**：**一对超大的尖耳朵**（外面橙色毛，里面紫粉色，耳尖蓝色）；**又大又圆的深色眼睛**（带亮高光），粉红色小鼻子，嘴边一颗小獠牙；**头上顶着一个骨头头盔**（一个小动物头骨，横着插一根骨头）；身上是**深棕色皮毛的披肩和腰布**；**一条蓬松的大尾巴，橙色到尾尖变成蓝色**；小小的带爪的脚；手里拿着**一把很大的骨头回力标**（象牙色骨头，中间缠着棕色皮条）。
> - **巨型纳尔**：同一个纳尔变成的**一只巨大的、弓着背的野兽**：**深红色的毛**，背上、头上、手臂上是**一排排尖尖的电光蓝色毛刺**；**两根很大的弯弯的象牙色獠牙**；一张**宽宽的满是尖牙的嘴**；**发光的黄橙色眼睛**、眉头紧锁；额头上还顶着**那个小小的骨头头盔**；**两只巨大的带爪的拳头**撑在地上，指节和爪子是深灰紫色；一条**蓝红相间的毛刺尾巴**。
>
> 请 Codex 画**四张全身像**（同一个纳尔，**两种形态的格子大小一样**），用户从里面挑：
> - **A：迷你纳尔的待机，3/4 正面朝右**（附图 1、2、10a）。他站着，回力标拿在身侧，大尾巴在身后。
> - **SA：A 的侧面，朝右**（附图 4、10b）。同一个迷你纳尔**正侧面朝右**（脸朝画面右边，看得见一只眼睛），尾巴在背后（画面左边）。
> - **M：巨型纳尔的待机，3/4 正面朝右**（附图 5、6、10c）。弓着背、两只拳头撑地，头在前面（画面右边）。
> - **SM：M 的侧面，朝右**（附图 8、10d）。同一个巨型纳尔正侧面朝右。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的吉格斯（约德尔人）、悠米（小猫）、沃利贝尔（毛茸茸的大野兽）和科加斯（满嘴尖牙的怪兽），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–9）。
> - **比例**：迷你纳尔 Q 版，**头和耳朵很大**（头连耳朵约占身高的一半，脸本身清楚），身子小小的；巨型纳尔是一只又宽又壮的野兽，头大、拳头大。
> - **迷你纳尔的脸**（附图 3 特写）：橙色小脸，**两只大大的深色圆眼睛一样大、一样高、都看得见**（每只至少 3×3 格，深紫黑色，带一格白色高光），粉色小鼻子。
> - **巨型纳尔的脸**（附图 7 特写）：深红色，**两只黄橙色的眼睛**（每只至少 2×2 格）、蓝色的眉毛毛刺，宽嘴里一排象牙色尖牙，两根大獠牙从嘴角往外往上弯。
> - **颜色**：迷你：橙色毛 3–4 档（亮边偏黄，**不要糊成一团橙**），耳朵里面紫粉色，耳尖和尾尖蓝色 2–3 档，骨头头盔和回力标象牙色 3 档、皮条深棕，腰布和披肩深棕 3 档。巨型：深红毛 3–4 档（**不要糊成一团红**），毛刺电光蓝 3 档（亮边偏青），獠牙和牙齿象牙色 3 档，拳头和爪子深灰紫 3 档，嘴里红粉色。
> - **画布用正方形 1536×1536**。**迷你纳尔从头盔顶到脚底约 506 px，也就是约 46 格；巨型纳尔从最高的毛刺到脚底约 726 px，约 66 格**（两种形态格子一样大，所以巨型的大很多）。脚底在离画布底边约 146 px 的地方（附图 10a–10d 的灰线）；站在画布中间（附图 10a–10d 的位置）。耳朵、尾巴、回力标、獠牙、毛刺全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（回力标飞出去、石头、冲击波都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/gnar-picture/gnar-A.png`、`gnar-SA.png`、`gnar-M.png`、`gnar-SM.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/gnar-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/gnar_picture_done.zip`。

## 附图（在压缩包 `gnar_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_mini_idle.png` | 英雄联盟原版迷你纳尔的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_mini_frontal.png` | 同一帧，正面 | 耳朵、披肩、腰布、回力标 |
| `refs/3_mini_head.png` | 头部特写（3/4） | 骨头头盔、耳朵、眼睛、鼻子 |
| `refs/4_mini_side.png` | 同一帧，侧面朝右 | SA 的角度：尾巴、身子的厚度 |
| `refs/5_mega_idle.png` | 巨型纳尔的待机，3/4 朝右 | M 的颜色、形状、角度、姿势 |
| `refs/6_mega_frontal.png` | 同一帧，正面 | 獠牙、拳头、毛刺 |
| `refs/7_mega_head.png` | 巨型纳尔头部特写 | 眼睛、獠牙、牙齿、头盔、毛刺 |
| `refs/8_mega_side.png` | 同一帧，侧面朝右 | SM 的角度 |
| `refs/9_gnar_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/10a_layout_mini.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰） |
| `refs/10b_layout_mini_side.png` | SA 的布局示意 | 同上，侧面 |
| `refs/10c_layout_mega.png` | M 的布局示意 | 同上，巨型 |
| `refs/10d_layout_mega_side.png` | SM 的布局示意 | 同上，巨型侧面 |
| `style/11_style_ziggs.png` | 本包的吉格斯，8 倍放大，一格 = 一个像素 | **只看风格**：约德尔人的大耳朵、大眼睛在格子上怎么画 |
| `style/12_style_yuumi.png` | 本包的悠米（8 倍） | **只看风格**：小小的毛茸茸动物怎么画 |
| `style/13_style_volibear.png` | 本包的沃利贝尔（8 倍） | **只看风格**：大野兽的毛、毛刺、深色分档 |
| `style/14_style_chogath.png` | 本包的科加斯（8 倍） | **只看风格**：满嘴尖牙的怪兽 |

## 提示词：`gnar-A.png` / `gnar-SA.png` / `gnar-M.png` / `gnar-SM.png`（同一段提示词，只换最后一句）

十七张图都附上，顺序同上表。

```text
Seventeen attached images. Images 1-9 are 3D renders and art of one character from a game, in two forms. MINI FORM (images 1-4): a TINY ORANGE FURRY CUB with HUGE POINTED EARS (orange fur outside, violet-pink inside, blue tips), BIG ROUND DARK EYES with bright highlights, a small pink nose, one small fang, a BONE SKULL CAP on his head (a small animal skull with a bone stuck across it), a DARK BROWN FUR SHOULDER WRAP and LOINCLOTH, a BIG BUSHY TAIL orange fading to BLUE at its tip, small clawed feet, and a BIG BONE BOOMERANG (ivory bone, wrapped with brown leather in the middle) held at his side. MEGA FORM (images 5-8): the same character grown into a HUGE HUNCHED BEAST on its knuckles: DEEP CRIMSON-RED FUR with rows of SPIKY ELECTRIC-BLUE FUR CRESTS along the back, head and arms, TWO BIG CURVED IVORY TUSKS, a WIDE MOUTH full of ivory fangs, GLOWING YELLOW-ORANGE EYES under a frowning brow, the same SMALL SKULL CAP on his brow, two HUGE CLAWED FISTS with dark grey-violet knuckles and claws, a SPIKY BLUE-AND-RED TAIL. (1 Mini's idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front; 3 Mini's head close-up: the skull cap, the ears, the eyes; 4 Mini from the side, facing right - the angle of SA; 5 Mega's idle, 3/4 view facing right - the look, angle and pose of M; 6 the same from the front: the tusks, the fists, the crests; 7 Mega's head close-up: the eyes, the tusks, the fangs, the skull cap; 8 Mega from the side, facing right - the angle of SM; 9 the official illustration: mood and colours.) Images 10a-10d are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, big ears and big eyes of a small creature on the grid (11, 12), the fur, crests and dark shades of a big beast (13), a monster's fangs (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both forms. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the ears, the tail, the boomerang, the tusks, the crests); the soles level on one ground line about 146 px above the bottom edge (the grey line of images 10a-10d), standing where the guide shows him (the centre). MINI is about 506 px (about 46 squares) from the top of the skull cap to his soles; MEGA is about 726 px (about 66 squares) from his highest crest to his soles.
PROPORTIONS: Mini is chibi - the head with its ears about HALF of his height, a clear face, a small body; Mega is a wide heavy beast with a big head and huge fists.
MINI'S FACE: small and orange; TWO BIG ROUND DARK EYES of the SAME size at the SAME height, both visible (each at least 3x3 squares, dark violet-black with one white highlight square), a small pink nose.
MEGA'S FACE: crimson; TWO YELLOW-ORANGE EYES (each at least 2x2 squares) under blue brow crests, a wide mouth with a row of ivory fangs, two big tusks curving out and up from the corners of the mouth.
THE COLOURS: Mini - the orange fur in 3-4 shades with YELLOWER LIT EDGES so it never turns into one orange mass, violet-pink inside the ears, blue ear tips and tail tip in 2-3 shades, the skull cap and the boomerang ivory in 3 shades with dark brown leather, the wrap and loincloth dark brown in 3 shades. Mega - the crimson fur in 3-4 shades so it never turns into one red mass, the crests electric blue in 3 shades with CYAN LIT EDGES, the tusks and fangs ivory in 3 shades, the fists and claws dark grey-violet in 3 shades, the mouth red-pink inside.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no flying boomerang, no boulder, no shock waves, no sparkles), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (gnar-A.png): MINI's idle in 3/4 view facing right (images 1, 2 and 10a) - standing on both feet, the face to the front-right, the boomerang held at his side, the bushy tail curling behind him.
PICTURE SA (gnar-SA.png): the SAME Mini as A seen exactly from the SIDE, FACING RIGHT (images 4 and 10b) - the face to the image right with one eye visible, the tail behind him (image left), both soles on the ground line, the boomerang as in A.
PICTURE M (gnar-M.png): MEGA's idle in 3/4 view facing right (images 5, 6 and 10c) - hunched on his knuckles, the head low at the front (image right), the face to the front-right, the tail up behind him.
PICTURE SM (gnar-SM.png): the SAME Mega as M seen exactly from the SIDE, FACING RIGHT (images 8 and 10d) - the face to the image right with one eye and one tusk in front, the tail behind him (image left), fists and feet on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，耳朵、尾巴、回力标、獠牙、毛刺完整，不出画。
- 迷你：Q 版，头连耳朵约占身高一半；**两只大圆眼睛一样大、一样高**、带白色高光；骨头头盔、深棕披肩腰布、蓝尖大尾巴、骨头回力标。
- 巨型：深红毛、电光蓝毛刺、两根大獠牙、满嘴尖牙、黄橙色眼睛、额头的小头盔、大拳头撑地。
- A / M 是 3/4 正面朝右，SA / SM 是正侧面朝右；迷你从头盔顶到脚底约 506 px（约 46 格），巨型约 726 px（约 66 格），脚底都在地面线上。
- 没有任何技能特效。**每块 11 像素、两种形态大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 四张都画完后，最后写 `outputs/gnar-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/gnar_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/gnar/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_zyra_hd.py` 的做法），和已合并的约德尔人 / 野兽（吉格斯、提莫、沃利贝尔、拉莫斯）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定两种形态的大小（PPU 不要超过 1.5，除非用户要）。
- 定下后第 1 步按游戏格子重画两种形态的 3/4 正面和**侧面朝右**，一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Gnar` / `GnarBig --wad Gnar`）：迷你 普攻 Gnar_Attack1 / 2，Q Gnar_Spell1_0（接住 Gnar_Spell1_Catch），E Gnar_Spell3_Jump / _Bounce，跑 Gnar_Run1，变身前 Gnar_IdleRage，变回 Gnar_Revert，死亡 Gnar_Death；巨型 普攻 GnarBig_Attack1 / 2，Q GnarBig_Spell1，W GnarBig_Spell2，E GnarBig_Spell3，R GnarBig_Spell4，变身 GnarBig_Rage_stop（边放技能边变：_Spell1_trans / _Spell2_Tran / _Spell3_Trans / _Spell4_TRANS），跑 GnarBig_Run，死亡 GnarBig_Death。
