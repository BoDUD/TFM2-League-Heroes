# 翠神 艾翁：第 0 步，先画像素风原图（给 Codex 的提示词）

> 艾翁是英雄联盟里一个**会走路的树人**，森林的老好人，带着他的岩石好朋友**小菊**打架。这一步把他和小菊都画出来，用户从里面挑：
> - **艾翁**：一张**小小的圆脸**，是**浅灰白的树皮色**，一个**大鼻子**，咧着嘴**开心地笑**，一双**小小的琥珀色眼睛**；脸下面是**一大把亮绿色树叶做的胡子**（比脸大得多，一片片叶子朝下垂）；头两边各一只**浅灰绿色的弯羊角**，往两边伸出去再往上卷；头顶长着一个**红色带白点的小蘑菇**。身子是**棕色的木头**，腰上围着一圈**树叶裙**；两条**细长的树枝手臂**（一只手上翘着一根带两片叶子的小树枝，另一只手拿着一个**红苹果**）；两条**又细又长的高跷一样的腿**，是**深红棕色的树皮**，下面是**分叉的树根脚**，一条小腿上长着几颗**红色的浆果**。
> - **小菊（大招）**：一个**大块头的岩石傀儡**：弓着背，身子由**长着青苔的绿色石块**拼成，有的石面是**淡紫灰色**，上面刻着**螺旋形的花纹**；胸口开着**几朵小白花**，中间嵌着一颗**绿色的小水晶**；两只**巨大的石头拳头**垂到膝盖，两条**短粗的石头腿**；头是一块**深灰色的尖石头**，嵌在两肩之间，头顶冒出一株**三叶草的嫩芽**。
>
> 请 Codex 画**三张全身像**（**格子大小都一样**），用户从里面挑大小：
> - **A：艾翁，英雄联盟里的待机，3/4 正面朝右**（附图 1、2、10a）。
> - **SA：A 的侧面，朝右**（附图 6、10b）。
> - **D：小菊，正面**（附图 7、8、10c）。**正对着看画的人**，左右基本对称。
>
> **为什么小菊画正面**：游戏里小菊是跟着目标走的特效图，**两边阵营都不会左右翻转**；正对着看画的人，红蓝两边看起来都对。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的茂凯（树人）、婕拉（植物）、莉莉娅（森林配色）和加里奥（石头大块头），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–9）。
> - **比例**：Q 版。艾翁的**头（连角、连树叶胡子）大**，约占身高的三分之一；**腿比原版短很多**（原版腿占身高一半多，这里只要约三分之一），但还是细细的树干腿；**两条腿分开一点站着，两只根脚都踩在地上**（原版待机两腿并成一根，这里要看得出是两条腿）。小菊：身子、拳头都大，腿短粗，头小小地嵌在肩膀中间。
> - **艾翁的脸**（附图 3 特写）：浅灰白树皮色的脸，**两只琥珀色的小眼睛一样大、一样高、都看得见**（每只至少 2×2 格，深色瞳孔，一格亮色高光），**大鼻子**，**笑着的嘴**（露一点白牙）；两只羊角**不挡脸**，树叶胡子从嘴下面开始。
> - **颜色**：艾翁：脸浅灰白 3 档（暗处偏灰绿）；树叶胡子亮绿 4 档（暗处墨绿，亮处黄绿，**不要糊成一片绿**）；羊角浅灰绿 3 档；蘑菇红 2 档 + 白点；身子木头棕 3–4 档（亮处橙棕）；树叶裙绿 3 档；手臂浅棕 3 档；腿深红棕 3 档；浆果红 2 档；苹果红 2 档。小菊：石头青苔绿 3–4 档，淡紫灰的石面 2–3 档，花纹深绿 1 档，小白花白 2 档 + 黄心，水晶亮绿 2 档，头深灰 3 档，三叶草芽绿 2 档。
> - **画布用正方形 1536×1536**。**艾翁从角尖 / 蘑菇最高处到脚底约 640 px，也就是约 58 格；小菊从头顶的嫩芽到脚底约 506 px，约 46 格**（格子一样大）。脚底在离画布底边约 146 px 的地方（附图 10a–10c 的灰线）；站在画布中间（附图 10a–10c 的位置）。角、树枝、拳头全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（荆棘、草丛、护盾、种子、发光都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/ivern-picture/ivern-A.png`、`ivern-SA.png`、`ivern-D.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/ivern-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/ivern_picture_done.zip`。

## 附图（在压缩包 `ivern_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_ivern_idle.png` | 英雄联盟原版艾翁的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_ivern_frontal.png` | 同一帧，正面 | 胡子、身子、树叶裙、两只手、腿 |
| `refs/3_ivern_head.png` | 头部特写（3/4） | 脸、眼睛、鼻子、笑、羊角、蘑菇、树叶胡子 |
| `refs/4_ivern_back.png` | 同一帧的背后 | 背后的胡子、身子、腿 |
| `refs/5_ivern_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/6_ivern_side.png` | 同一帧，侧面朝右 | SA 的角度 |
| `refs/7_daisy_front.png` | 小菊，正面 | **D 的角度**、颜色、形状 |
| `refs/8_daisy_34.png` | 小菊，3/4 | 石块的厚度、头、花 |
| `refs/9_daisy_attack.png` | 小菊挥拳（正面） | 拳头多大、手臂怎么接 |
| `refs/10a_layout_ivern.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰） |
| `refs/10b_layout_ivern_side.png` | SA 的布局示意 | 同上，侧面 |
| `refs/10c_layout_daisy.png` | D 的布局示意 | 同上，小菊 |
| `style/11_style_maokai.png` | 本包的茂凯，8 倍放大，一格 = 一个像素 | **只看风格**：树人的木头、青苔、叶子在格子上怎么画 |
| `style/12_style_zyra.png` | 本包的婕拉（8 倍） | **只看风格**：植物、叶子分档 |
| `style/13_style_lillia.png` | 本包的莉莉娅（8 倍） | **只看风格**：森林配色、Q 版脸 |
| `style/14_style_galio.png` | 本包的加里奥（8 倍） | **只看风格**：石头大块头、大拳头、石块分档 |

## 提示词：`ivern-A.png` / `ivern-SA.png` / `ivern-D.png`（同一段提示词，只换最后一句）

十六张图都附上，顺序同上表。

```text
Sixteen attached images. Images 1-9 are 3D renders and art of a character and his companion from a game. THE TREE-MAN (images 1-6): a walking tree spirit - a SMALL ROUND FACE of PALE GREY-WHITE BARK with a BIG NOSE, a WIDE HAPPY GRIN and SMALL AMBER EYES; below it a HUGE BEARD OF BRIGHT GREEN LEAVES (much bigger than the face, leaves hanging down); two PALE SAGE-GREEN RAM'S HORNS curling out to the sides and up; a small RED WHITE-SPOTTED MUSHROOM on his crown; a BROWN WOODEN BODY with a SKIRT OF LEAVES at the waist; two LONG THIN BRANCH ARMS (one hand holds up a twig with two leaves, the other a RED APPLE); two very LONG THIN STILT LEGS of DARK RED-BROWN BARK ending in forked ROOT FEET, a few RED BERRIES growing on one shin. THE ROCK GOLEM DAISY (images 7-9): a BIG HUNCHED GOLEM made of MOSSY GREEN STONES, some stone faces PALE VIOLET-GREY with CARVED SPIRAL MARKS, a few SMALL WHITE FLOWERS and a SMALL GREEN CRYSTAL on the chest, two HUGE STONE FISTS hanging to the knees, SHORT THICK STONE LEGS, a small DARK GREY POINTED STONE HEAD sunk between the shoulders with a CLOVER SPROUT on top. (1 the tree-man's idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the beard, the body, the leaf skirt, both hands, the legs; 3 his head close-up: the face, the eyes, the nose, the grin, the horns, the mushroom, the leaf beard; 4 the same from behind; 5 the official illustration: his mood, colours and face; 6 the idle from the side, facing right - the angle of SA; 7 Daisy from the FRONT - the angle of D; 8 Daisy in 3/4 view - her look; 9 Daisy swinging a fist, from the front - how big the fists are.) Images 10a-10c are layout guides: where the character goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a tree creature's wood, moss and leaves on the grid (11), plants and leaves in flat shades (12), a forest palette and a clear chibi face (13), a big stone figure with big fists in flat shades (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for all three pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the horns, the twig, the fists); the feet level on one ground line about 146 px above the bottom edge (the grey line of images 10a-10c), standing where the guide shows the character (the centre). THE TREE-MAN is about 640 px (about 58 squares) from the top of his horns / mushroom to his soles; DAISY about 506 px (about 46 squares) from her sprout to her feet.
PROPORTIONS: chibi. The tree-man's HEAD with its horns and leaf beard BIG (about a third of his height); his LEGS MUCH SHORTER than in the renders (about a third of his height, not half) but still thin bark legs; he stands on TWO LEGS a little APART, both root feet on the ground (in the renders his idle crosses them into one trunk - here they read as two legs). Daisy: a big body and big fists, short thick legs, the small head sunk between the shoulders.
THE TREE-MAN'S FACE: pale grey-white bark; TWO AMBER EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, a dark pupil, one light highlight square); a BIG NOSE; a GRINNING mouth showing a little white; the horns never cover the face, the leaf beard starts below the mouth.
THE COLOURS: the tree-man: the face pale grey-white in 3 shades (grey-green shadows); the leaf beard bright green in 4 shades (DEEP GREEN in the shadows, YELLOW-GREEN lit, so it never turns into one green mass); the horns pale sage green in 3; the mushroom red in 2 with white spots; the body wood brown in 3-4 (orange-brown lit); the leaf skirt green in 3; the arms light brown in 3; the legs dark red-brown in 3; the berries and the apple red in 2. Daisy: the stones moss green in 3-4 shades, the violet-grey stone faces in 2-3, the spiral marks one dark green, the flowers white in 2 with yellow centres, the crystal bright green in 2, the head dark grey in 3, the sprout green in 2.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around each character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the pale face, the green beard, the pale horns, the brown body and the dark legs clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no thorns, no bushes, no shields, no seeds, no glow, no sparkles); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (ivern-A.png): THE TREE-MAN's idle in 3/4 view facing right (images 1, 2 and 10a) - standing relaxed and friendly, the face to the front-right; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker and a little higher; one arm raised a little holding the leafy twig, the other holding the red apple at his side.
PICTURE SA (ivern-SA.png): the SAME tree-man as A seen exactly from the SIDE, FACING RIGHT (images 6 and 10b) - the face to the image right with one eye visible, the leaf beard hanging in front of his chest, the horns curling back, both root feet on the ground line.
PICTURE D (ivern-D.png): DAISY seen from the FRONT (images 7, 8 and 10c) - facing the viewer, nearly left-right symmetric, hunched, both big fists hanging at her sides, her short legs on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，角、树枝、拳头完整，不出画。
- 艾翁：Q 版大头（连角、胡子）；**两只琥珀色眼睛一样大、一样高**、带高光；大鼻子、笑脸；树叶胡子亮绿（暗处墨绿、亮处黄绿，不糊成一片）；浅灰绿羊角；红蘑菇；棕木身子、树叶裙；**腿比原版短很多，两条腿分开站，两只根脚都在地上**；红苹果、带叶小树枝；腿上红浆果。
- 小菊：青苔绿石块 + 淡紫灰石面、螺旋花纹、小白花、绿水晶；大石拳；短粗腿；深灰小尖头嵌在肩膀中间，头顶三叶草芽。**正面、基本左右对称**。
- A 是 3/4 正面朝右，SA 是正侧面朝右，D 是正面；艾翁约 640 px（约 58 格），小菊约 506 px（约 46 格），脚底都在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 三张都画完后，最后写 `outputs/ivern-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ivern_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，三张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：艾翁的头（连角、胡子，一张脸用在所有帧）、两只树枝手臂（甩手放荆棘、抬手给队友套盾、举手召唤）、两条长腿（跑）；小菊的两只大拳头（砸、挥）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | Idle1 / Run_base / Attack01–02 / — / Death | 普攻是手一甩，扔出一颗小种子 |
| **种豆得瓜**（E，skill） | Spell3 | 抬手往队友身上一指，套上一个种子护盾，2 秒后爆开（特效第 3 步另画） |
| **根深敌固**（Q，skill2） | Spell1 | 手往前一甩，甩出一条荆棘，缠住敌人 |
| **小菊！**（R，大招） | Spell4 | 举手一召，小菊从地里钻出来，跟着敌人砸拳，第三拳把人震飞 |
| 小菊 出现 / 待机 / 挥拳 / 消失 | spawn / idle / attack1–3 / despawn | 小菊只出现在特效里，不单独做成英雄 |

连招：**Q → E**（荆棘缠住敌人，给冲上去的队友套盾，护盾爆炸必中被缠住的人）；**Q → R**（小菊冲向被缠住的人，第三拳击飞）；**W 揠苗助攻**折进被动：他身边长出草丛，队友在草丛里普攻附带魔法伤害。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/ivern/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的打野（沃里克、格雷福斯、奈亚菲利、希瓦娜、乌迪尔、奇亚娜）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）、小菊多大、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_<hero>_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Ivern`（片段名小写：ivern_idle1、ivern_run_base、ivern_attack01、ivern_spell1…；渲染用 `--hide-submeshes`，皮肤藏着 W 的草墙和松鼠）；小菊 `--champ IvernMinion --wad Ivern`（片段 ivernminion_*，模型高 236，艾翁 264）。加载画面在 WAD 里：`assets/characters/ivern/skins/base/ivernloadscreen.tex`。
