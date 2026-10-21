# 大发明家 黑默丁格：第 0 步，先画像素风原图（给 Codex 的提示词）

> 黑默丁格是英雄联盟里的**约德尔人老教授**，带着自己发明的**炮台**打架。这一步把他和两种炮台都画出来，用户从里面挑：
> - **黑默丁格**：一个矮小的约德尔老头：**一大团往后梳、炸开的金黄色头发**（比脑袋还大），头发里竖着**两撮尖尖的发角**；**一对大大的橙色尖耳朵**从头发两边伸出来；**红框护目镜**，镜片是**发光的青蓝色**；**一大把白色的八字胡和白胡子**，粉色的小鼻子；头发右上方一根小支架上顶着一个**红框的放大镜片**；身上一件**深墨绿 / 灰绿色的学院长外套**，腰上一条皮带配**黄铜色的 H 形带扣**，胸前几颗扣子；**黑色的靴子**；一只手拿着一把**橙色的海克斯科技多功能工具**，另一只手拿着一把**灰绿色的大扳手**（扳手头上有红色的小球）。
> - **炮台（H-28G 进化炮台，Q）**：一座**小炮台**：**灰色的方炮身**，正前方一根**粗炮管，炮口是一圈红色**，炮身两边各一个**浅灰绿色的大齿轮**，顶上一根小杆顶着**红色的小球**，两边两根**浅灰绿色的弯管**（管口红色），下面是一个**红色圆环的转盘**和**三条短短的灰色机械腿**，腿上有浅灰绿色的圆形关节，脚是暗红色的。
> - **巨型炮台（升级！！！强化的 Q）**：一座**大炮台**：**灰色的大方块炮身**，正前方一个**很大的红色八角形炮口**，两肩是**浅灰绿色的装甲板**（上面有排气栅格），肩上斜着伸出**两根浅灰绿色的粗排气筒**，顶上一个**红色的大圆球**，下面**两条粗壮的机械腿**往两边叉开，腿上有银色的关节，**脚是红色的大方块**。
>
> 请 Codex 画**四张全身像**（**三个角色的格子大小一样**，所以按下面的格数保持彼此的大小），用户从里面挑：
> - **A：黑默丁格的待机，3/4 正面朝右**（附图 1、2、3、10a）。站着，脸朝右前方，两只护目镜都看得见；一手扳手、一手工具，自然垂在身体两边。
> - **SA：A 的侧面，朝右**（附图 4、10b）。同一个黑默丁格**正侧面朝右**（脸朝画面右边，看得见一只护目镜），两只脚都在地面线上，大团头发往后（画面左边）。
> - **T：炮台，正面**（附图 5、6、10c）。**炮口正对着看画的人**，左右对称。
> - **X：巨型炮台，正面**（附图 7、8、10d）。**炮口正对着看画的人**，左右对称。
>
> **为什么炮台画正面**：游戏里炮台是放在地上的特效图，**两边阵营都不会左右翻转**；炮口朝着看画的人，红蓝两边看起来都对。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的吉格斯、库奇（约德尔人和机械）、波比（约德尔人）和杰斯的加农炮形态（海克斯科技机械），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–9）。
> - **比例**：黑默丁格本来就是 Q 版：**头（连头发）占身高的一半左右**，身子短小，腿很短；头发是他最醒目的轮廓，要大而清楚，但**不能挡住护目镜和胡子**。
> - **黑默丁格的脸**（附图 3 特写）：**两只护目镜一样大、一样高、都看得见**（每只至少 3×3 格：红框一圈，里面青蓝色的镜片，带一格白色高光）；护目镜下面是**白色的大八字胡**，往两边翘起，盖住嘴；中间一个粉色的小鼻子。
> - **颜色**：头发金黄 4 档（**不要糊成一团黄**，暗处偏橙棕，亮处偏淡黄），耳朵橙色 3 档，护目镜框红色 2–3 档、镜片青蓝 3 档，胡子白 / 米白 2–3 档，外套墨绿灰 3 档，带扣黄铜 2 档，靴子黑灰 2 档，多功能工具橙色 2–3 档，扳手灰绿 3 档加红色小球。炮台：炮身灰 3 档（偏紫灰），齿轮和弯管浅灰绿 3 档，炮口和小球红色 3 档，腿灰色 2–3 档，脚暗红 2 档。
> - **画布用正方形 1536×1536**。**黑默丁格从头发最高处到鞋底约 396 px，也就是约 36 格；炮台从顶上的红球到脚底约 220 px，约 20 格；巨型炮台约 330 px，约 30 格**（格子一样大）。脚底在离画布底边约 146 px 的地方（附图 10a–10d 的灰线）；站在画布中间（附图 10a–10d 的位置）。头发、扳手、排气筒、腿全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（炮弹、激光、导弹、手雷、电光、升级的光都放到第 3 步单独画）；不画地面，不画投影；一张图里只画一个。

## 附图（在压缩包 `heimerdinger_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_heimer_idle.png` | 英雄联盟原版黑默丁格的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_heimer_frontal.png` | 同一帧，正面 | 头发、外套、两只手里的工具 |
| `refs/3_heimer_head.png` | 头部特写（3/4） | 护目镜、胡子、耳朵、放大镜 |
| `refs/4_heimer_side.png` | 同一帧，侧面朝右 | SA 的角度：头发、背、靴子 |
| `refs/5_turret_34.png` | 炮台，3/4 | T 的颜色、形状 |
| `refs/6_turret_front.png` | 炮台，正面 | **T 的角度** |
| `refs/7_apex_34.png` | 巨型炮台，3/4 | X 的颜色、形状 |
| `refs/8_apex_front.png` | 巨型炮台，正面 | **X 的角度** |
| `refs/9_heimer_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/10a_layout_heimer.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰） |
| `refs/10b_layout_heimer_side.png` | SA 的布局示意 | 同上，侧面 |
| `refs/10c_layout_turret.png` | T 的布局示意 | 同上，炮台 |
| `refs/10d_layout_apex.png` | X 的布局示意 | 同上，巨型炮台 |
| `style/11_style_ziggs.png` | 本包的吉格斯，8 倍放大，一格 = 一个像素 | **只看风格**：约德尔人的大头和头发 |
| `style/12_style_corki.png` | 本包的库奇（8 倍） | **只看风格**：约德尔人、护目镜、机械 |
| `style/13_style_poppy.png` | 本包的波比（8 倍） | **只看风格**：约德尔人的小身子、短腿 |
| `style/14_style_jayce_cannon.png` | 本包的杰斯加农炮形态（8 倍） | **只看风格**：海克斯科技机械、炮管 |

## 提示词：`heimerdinger-A.png` / `heimerdinger-SA.png` / `heimerdinger-T.png` / `heimerdinger-X.png`（同一段提示词，只换最后一句）

十七张图都附上，顺序同上表。

```text
Seventeen attached images. Images 1-9 are 3D renders and art of a character and his two machines from a game. THE INVENTOR (images 1-4): a SHORT OLD YORDLE - a HUGE SPIKY MANE of GOLDEN-YELLOW HAIR swept back (bigger than his head) with two pointed tufts standing up, BIG POINTED ORANGE EARS sticking out of the hair, RED-RIMMED GOGGLES with GLOWING CYAN LENSES, a BUSHY WHITE MOUSTACHE and beard, a small pink nose, a small red-rimmed MAGNIFYING LENS on a stalk above his hair; a DARK GREEN-GREY ACADEMY LONG COAT with a belt and a BRASS H-SHAPED BUCKLE, buttons on the chest; BLACK BOOTS; an ORANGE HEXTECH MULTITOOL in one hand and a big GREY-GREEN WRENCH with a little red ball in the other. THE TURRET (images 5-6): a SMALL CANNON - a GREY BOX BODY with one thick barrel at the front and a RED MUZZLE RING, a PALE GREY-GREEN GEAR on each side, a red ball on a short stalk on top, two pale green bent pipes with red ends, a RED RING turntable under it and THREE SHORT GREY MECHANICAL LEGS with pale green round joints and dark red feet. THE APEX TURRET (images 7-8): a BIG CANNON - a GREY BLOCK BODY with a HUGE RED OCTAGONAL MUZZLE at the front, pale grey-green armour plates with vent grilles on the shoulders, TWO THICK PALE GREEN EXHAUST STACKS angled up from the shoulders, a big red ball on top, TWO STURDY MECHANICAL LEGS spread apart with silver joints and BIG RED BLOCK FEET. (1 the inventor's idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the hair, the coat, the tools in both hands; 3 the inventor's head close-up: the goggles, the moustache, the ears, the magnifying lens; 4 the inventor from the side, facing right - the angle of SA; 5 the turret in 3/4 view - its look; 6 the turret from the FRONT - the angle of T; 7 the apex turret in 3/4 view - its look; 8 the apex turret from the FRONT - the angle of X; 9 the official illustration: mood and colours.) Images 10a-10d are layout guides: where the character goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a small big-headed yordle and his hair (11), goggles and machinery (12), a small body on short legs (13), a hextech cannon (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for all three. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the hair, the wrench, the exhaust stacks, the legs); the feet level on one ground line about 146 px above the bottom edge (the grey line of images 10a-10d), standing where the guide shows the character (the centre). THE INVENTOR is about 396 px (about 36 squares) from the top of his hair to his soles; THE TURRET about 220 px (about 20 squares) from the ball on top to its feet; THE APEX TURRET about 330 px (about 30 squares).
PROPORTIONS: the inventor is already chibi - the head with the hair about HALF of his height, a short little body, very short legs; the mane is his strongest shape, big and clear, but it NEVER covers the goggles or the moustache.
THE INVENTOR'S FACE: TWO GOGGLES of the SAME size at the SAME height, both visible (each at least 3x3 squares: a red rim round a cyan lens with one white highlight square); under them the big WHITE MOUSTACHE curling out to both sides over the mouth; a small pink nose between.
THE COLOURS: the hair golden yellow in 4 shades (ORANGE-BROWN in the shadows, PALE YELLOW lit, so it never turns into one yellow mass), the ears orange in 3, the goggle rims red in 2-3 and the lenses cyan in 3, the moustache white / off-white in 2-3, the coat dark green-grey in 3, the buckle brass in 2, the boots black-grey in 2, the multitool orange in 2-3, the wrench grey-green in 3 with its red ball. The turrets: the body grey in 3 shades (a little purple-grey), the gears, pipes, plates and stacks pale grey-green in 3, the muzzles and balls red in 3, the legs grey in 2-3, the feet dark red in 2.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no cannon shots, no laser beams, no rockets, no grenades, no lightning, no upgrade glow, no sparkles), no background, no ground plane, no cast shadow, no text, no frame, ONE figure in each picture.
PICTURE A (heimerdinger-A.png): THE INVENTOR's idle in 3/4 view facing right (images 1, 2, 3 and 10a) - standing, the face to the front-right with both goggles visible, the wrench in one hand and the multitool in the other, hanging at his sides.
PICTURE SA (heimerdinger-SA.png): the SAME inventor as A seen exactly from the SIDE, FACING RIGHT (images 4 and 10b) - the face to the image right with one goggle visible, both boots on the ground line, the mane sweeping back (image left).
PICTURE T (heimerdinger-T.png): THE TURRET seen exactly from the FRONT (images 5, 6 and 10c) - the muzzle pointing straight at the viewer, left-right symmetric, its three legs on the ground line.
PICTURE X (heimerdinger-X.png): THE APEX TURRET seen exactly from the FRONT (images 7, 8 and 10d) - the big muzzle pointing straight at the viewer, left-right symmetric, both feet on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、扳手、排气筒、腿完整，不出画。
- 黑默丁格：大团金黄色头发（4 档，不糊）；橙色尖耳朵；**两只红框青蓝镜片的护目镜一样大、一样高**、带白色高光；白色大八字胡；放大镜支架；墨绿灰长外套、黄铜带扣、黑靴子；橙色多功能工具和灰绿扳手。
- 炮台：灰炮身、红炮口、两边齿轮、顶上红球、三条腿；巨型炮台：大红炮口、两根排气筒、顶上红球、两条腿、红色大脚。**两座炮台都是正面、左右对称、炮口对着看画的人**。
- A 是 3/4 正面朝右，SA 是正侧面朝右；黑默丁格约 396 px（约 36 格），炮台约 220 px（约 20 格），巨型炮台约 330 px（约 30 格），脚底都在地面线上。
- 没有任何技能特效。**每块 11 像素、三个大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 四张都画完后，最后写 `outputs/heimerdinger-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/heimerdinger_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，四张都画完再交。
- 交付：`outputs/heimerdinger-picture/heimerdinger-A.png`、`heimerdinger-SA.png`、`heimerdinger-T.png`、`heimerdinger-X.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/heimerdinger-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼，所以造型里这些部件要**画得清楚、彼此分得开**：黑默丁格的头（连头发）、两只手和手里的扳手 / 工具（放炮台时往地上一按、扔手雷时抡臂、打导弹时举起工具）、两条短腿（跑）；炮台的炮管（开火时往后一缩）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 黑默丁格 待机 / 跑 / 普攻 / 受击 / 死亡 | Idle1 / Run1 / Attack1–2 / — / Death | 普攻是举起工具射出一道电光 |
| **Q H-28G 进化炮台** | Spell1 | 弯腰把炮台往地上一放，炮台弹出来 |
| **W 海克斯科技微型导弹** | Spell2 | 举起工具，从背后打出一排小导弹（这里跟着普攻一起打出） |
| **E CH-2 电子风暴手雷** | Spell3 | 抡臂把手雷往前扔出去 |
| **R 升级！！！**（大招） | Spell4_IN → Spell4_LOOP | 举起双手，头上冒出升级的光，然后放出强化的炮台或手雷 |
| 炮台 / 巨型炮台 出现 / 待机 / 开火 / 消失 | Spawn / Idle1 / Attack1 / Death | 炮台只出现在特效里，不单独做成英雄 |

连招：**E → Q / W**（手雷晕住英雄，炮台和导弹集火被晕的人）；**R → E**（升级的手雷连环三颗，大范围晕）。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/heimerdinger/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_shyvana_hd.py` 的做法），和已合并的约德尔人（吉格斯、库奇、波比、提莫）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5，除非用户要；问用户要不要侧面）。
- 定下后第 1 步按游戏格子重画造型，一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Heimerdinger`；炮台 `--champ HeimerTBlue --wad Heimerdinger`（小炮台，片段 heimerturret_mega_*），巨型炮台 `HeimerTYellow`（片段 heimerturret_*）——WAD 里的名字和样子是反的，以渲染出来的样子为准。
