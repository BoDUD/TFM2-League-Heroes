# 祖安怒兽 沃里克：第 0 步，先画像素风原图（给 Codex 的提示词）

> 沃里克是一头**弓着背的狼人**：**蓝紫色的毛**，胸口和两颊是**蓬松的白色鬃毛**，一对**很大的尖耳朵**（耳朵里面偏粉），**张着嘴龇牙咆哮**（黄白色的尖牙、红色的口腔），**发光的黄眼睛**；背上是祖安的**炼金装置**——脖子后面竖着一个**发绿光的药瓶，顶上一根铜色的尖刺**；两只前臂戴着**铜色的护臂**（近侧那只嵌着几管绿色药剂），手上是深色的爪子；下身是**橄榄色 / 卡其色的短工装裤**，腰上一条皮带；**反关节的狼腿**，脚上是深色的爪子；身后一条**又长又蓬的深蓝色尾巴**。请 Codex 画**两张全身像**（同一个沃里克，长相、颜色、**格子大小**都一样），都是 **3/4 正面朝右**（**不画正侧面**），用户从里面挑：
> - **A：英雄联盟里的待机，弓着背**（附图 1、2、8a）：身子前倾、头往前探，两条长胳膊垂在身前、爪子张开，两腿分开微屈站着。
> - **B：同样的待机，站得直一些、更紧凑（Q 版）**：背只微微弓，头在肩膀上方，胳膊收在身体两侧，整个人更高更窄。长相、颜色和 A 一模一样。
> - **两张图里尾巴都要抬离地面**：尾巴从屁股后面往后上方翘起、弯成一道弧，尾巴尖不碰地（英雄联盟里尾巴拖在地上，这里不要）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的沃利贝尔（熊）、内瑟斯（狗头人）和雷恩加尔（猫科野兽），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–6）。
> - **比例**：Q 版，**头（连耳朵）约占身高的三分之一**，脸要大到看得清眼睛和牙；肩膀宽、胳膊粗，腿短一些；不要细长的写实比例。
> - **脸**（附图 3 特写）：**两只黄眼睛一样大、一样高、都看得见**（每只至少 2 格），鼻子是深色的，张开的嘴里看得见上下的尖牙（白色，每颗至少 1 格）和红色的口腔；白色鬃毛分 2–3 档，不要糊成一块白。
> - **颜色**：蓝紫色的毛 3–4 档（亮边偏浅蓝，暗处深靛蓝，**不要一团黑**），白色鬃毛 2–3 档（暗处偏淡蓝灰），铜色护臂和尖刺 3 档，绿色药瓶 2–3 档（亮绿，平涂，不要柔光），橄榄色短裤 3 档，深色爪子有偏亮的边。
> - **画布用正方形 1536×1536**。**沃里克从背上尖刺的顶端到脚底约 748 px，也就是约 68 格**，脚底在离画布底边约 146 px 的地方（附图 8a 的灰线），站在附图 8a 的位置。尖刺、耳朵、尾巴全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（血雾、爪痕、嚎叫的冲击波、发光都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/warwick-picture/warwick-A.png`、`warwick-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/warwick-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/warwick_picture_done.zip`。

## 附图（在压缩包 `warwick_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_warwick_idle.png` | 英雄联盟原版沃里克的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_warwick_frontal.png` | 同一帧，正面 | 鬃毛、护臂、短裤、腿 |
| `refs/3_warwick_head.png` | 头部特写（3/4） | 耳朵、眼睛、牙、鬃毛、背上的药瓶和尖刺 |
| `refs/4_warwick_back.png` | 同一帧的背后 | 背上的炼金装置、尾巴 |
| `refs/5_warwick_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_warwick_attack.png` | 挥爪的一帧，3/4 朝右 | 爪子和护臂的样子 |
| `refs/8a_layout_front.png` | 布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰线）、尖刺顶端的高度（浅灰线）；**示意图里尾巴拖在地上，你画的时候要把尾巴抬起来** |
| `style/11_style_volibear.png` | 本包的沃利贝尔，8 倍放大，一格 = 一个像素 | **只看风格**：野兽的毛、爪子、张开的嘴在格子上怎么画 |
| `style/12_style_nasus.png` | 本包的内瑟斯（8 倍） | **只看风格**：兽头、大耳朵、深色毛的亮边 |
| `style/13_style_rengar.png` | 本包的雷恩加尔（8 倍） | **只看风格**：弓背的野兽、尾巴 |

## 提示词：`warwick-A.png` / `warwick-B.png`（同一段提示词，只换最后一句）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-6 are 3D renders and art of a character from the game: a HUNCHED WEREWOLF with BLUE-VIOLET FUR, a SHAGGY WHITE MANE on his chest and cheeks, HUGE POINTED EARS (pinkish inside), a SNARLING OPEN JAW with yellow-white fangs and a red mouth, GLOWING YELLOW EYES; a chemtech rig on his back - a GREEN GLOWING VIAL with a COPPER SPIKE on top standing up behind his neck; COPPER GAUNTLETS on both forearms (the near one with green vials set in it), dark claws; OLIVE-KHAKI CARGO SHORTS with a belt; digitigrade wolf legs with clawed feet; a LONG BUSHY DARK BLUE TAIL (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the mane, the gauntlets, the shorts, the legs; 3 the head close-up: the ears, the eyes, the fangs, the mane, the vial and spike; 4 the same from behind: the rig on his back and the tail; 5 the official illustration: his mood and colours; 6 a claw swipe, 3/4 view: the claws and the gauntlets). Image 8a is a layout guide: where he goes on the canvas and how big, the grey line is the ground, the light grey line the top of the spike; in it the tail lies on the ground - in your picture the tail is LIFTED OFF THE GROUND. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a beast's fur, claws and open mouth on the grid (11), a beast's head with big ears and lit edges on dark fur (12), a hunched beast with a tail (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the spike, both ears, the whole tail, both feet); his soles level on one ground line about 146 px above the bottom edge (the grey line of image 8a). He is about 748 px (about 68 squares) from the tip of the spike to his soles and stands where image 8a shows him.
THE VIEW: 3/4 front, FACING RIGHT (image 1) - NOT a side view, NOT a front view; the NEAR side of the body on the image left in full tone, the FAR side a step darker.
PROPORTIONS: chibi - the head with the ears about a THIRD of his height, the face big enough that both eyes and the fangs read clearly; broad shoulders, thick arms, shorter legs; NOT realistic slim proportions.
THE FACE: TWO YELLOW EYES of the SAME size at the SAME height, both visible (each at least 2 squares); a dark nose; the open jaw showing upper and lower white fangs (each at least 1 square) and the red mouth; the white mane in 2-3 shades (never one white blob).
THE TAIL: lifted OFF THE GROUND - it rises from behind his hips back and up in one bushy curve, the tip well above the ground line; it never lies or drags on the ground.
THE COLOURS: the blue-violet fur in 3-4 shades (light blue edges, deep indigo shadows - never one black mass); the white mane in 2-3 shades (pale blue-grey shadows); the copper gauntlets and spike in 3 shades; the green vials in 2-3 flat bright greens (no glow); the olive shorts in 3 shades; the dark claws with lighter edges.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the blue fur, the white mane, the eyes, the fangs and mouth, the copper, the green vials, the olive shorts and the claws clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no blood mist, no claw trails, no shockwave, no glow), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (warwick-A.png): his idle as in League (images 1, 2 and 8a) - hunched forward, the head pushed out in front of the shoulders, the long arms hanging in front of him with the claws open, feet apart and knees bent.
PICTURE B (warwick-B.png): the SAME Warwick in 3/4 view facing right, standing MORE UPRIGHT and COMPACT: the back only a little bent, the head above the shoulders, the arms close to the sides of the body with the claws down, so the whole figure is taller and narrower; everything else (look, colours, square size, the lifted tail) exactly as in A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，尖刺、耳朵、尾巴、脚完整，不出画。
- 两张都是 **3/4 正面朝右**（不是侧面、不是正面）；**尾巴抬离地面**。
- Q 版：头连耳朵约占身高三分之一；**两只黄眼睛一样大、一样高**；看得见尖牙和红色的嘴；白鬃毛分档。
- 蓝紫色的毛（亮边，不是一团黑）、白鬃毛、铜护臂和尖刺、绿药瓶、橄榄色短裤、深色爪子；两张都是从尖刺顶端到脚底约 748 px（约 68 格），脚底在地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 两张都画完后，最后写 `outputs/warwick-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/warwick_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/warwick/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_graves_hd.py` 的做法），和已合并的野兽（沃利贝尔、内瑟斯、雷恩加尔）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑 A 还是 B、定大小（PPU 不要超过 1.5）。
- 用户：「不做侧面 只做四分之三的侧面」——第 1 步只在游戏格子上画 3/4 正面，动作都在 3/4 的造型上摆（婕拉的做法）；一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Warwick`）：普攻 Attack1–4（挥爪）、Q Spell1（扑咬，Spell1_Release）、E Spell3 / Spell3_Howl（嚎叫）、R Spell4Dash / Spell4Hit（扑过去压住、连抓三下）、跑 run_base / RunHunt（鲜血追猎时四肢着地狂奔）、死亡 Death。尾巴在待机和走路时不碰地。
