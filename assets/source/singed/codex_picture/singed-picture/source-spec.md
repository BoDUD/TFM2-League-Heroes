# 炼金术士 辛吉德：第 0 步，先画像素风原图（给 Codex 的提示词）

> 辛吉德是英雄联盟里**祖安的疯狂炼金术士**：又高又瘦、驼着背的老头，背着一个大药罐，一路跑一路喷毒雾。这一步把他画出来，用户从里面挑：
> - **辛吉德**：**光头**，头皮上有疤，脸瘦长、颧骨突出、眼窝深，**一只眼睛发白**（另一只正常）；**口鼻蒙着一块灰绿色的布**（像口罩），脖子上围一条**灰蓝色的大围巾**；**红色皮夹克**，**金色方扣带**交叉在胸前，两肩是**带尖刺的大护肩**（红底金边）；**背上绑着一个发光的亮绿色大药罐**（圆滚滚，上面一圈铆钉，顶上一个深灰金属盖），药罐顶比头还高；**靠近我们这只手臂上挂着一块高高的灰绿色金属盾板**（带铆钉，边上几根尖刺，中间一条木杆）；**另一只手握着一个圆圆的绿色药瓶**；腰上一条棕色皮带挂着几个小药管，腰下一圈破布条；**深蓝色的瘦长裤子**；**一双很大的红棕色靴子**，靴口一圈尖刺。手是又长又瘦的爪子手（暗红色破手套）。
>
> 请 Codex 画**两张全身像**（**格子大小一样**），用户从里面挑大小：
> - **A：辛吉德，英雄联盟里的待机，3/4 正面朝右**（附图 1、2、9a）。
> - **SA：A 的侧面，朝右**（附图 6、9b）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的蒙多医生、厄加特、普朗克、弗拉基米尔，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–8；附图 5 官方原画看气质和颜色——**蒙脸布、光头、发白的眼睛、背后发光的绿药罐最重要**）。
> - **比例**：Q 版。辛吉德的**头比原版大一些**（约占头顶到脚底的四分之一），**脖子往前探、背微驼**；身子瘦，**腿细长**，**靴子又大又重**，两脚分开站稳；**背上的绿药罐很显眼**，从右肩后面（画面里）往上冒，罐顶比头顶高约 9 格；**盾板竖在靠近我们这一侧**，比他的肩膀高一点，下端到膝盖附近，**不能挡住脸**，也不要挡住整个身体（只挡住靠近我们这侧的手臂和一点身体）。
> - **辛吉德的脸**（附图 3 特写）：光头，**两只眼睛一样高、都看得见**（每只至少 2×2 格）：一只**发白（近白的灰）**，一只正常（小黑瞳孔）；眼窝深色；眉头皱着，看起来阴沉、疯狂；**鼻子以下被灰绿色蒙脸布盖住**（布上 2–3 档，有几道褶）；耳朵小而尖一点。
> - **颜色**：皮肤 苍白偏粉 3 档（暗处偏紫灰）；蒙脸布 灰绿 3 档；围巾 灰蓝 3 档；夹克 红 3–4 档；扣带和护肩边 金黄 3 档；护肩尖刺 银灰 2 档；**药罐 荧光亮绿 4 档**（最亮一档带一点黄，像发光的液体），罐上的铆钉和盖子 深灰 2–3 档；盾板 灰绿金属 3 档 + 铆钉；手套 暗红棕 2 档；裤子 深蓝 3 档；靴子 红棕 3 档 + 银灰尖刺；手里的药瓶 亮绿 2–3 档。
> - **画布用正方形 1536×1536**。**辛吉德从头顶到脚底约 572 px，也就是约 52 格；药罐顶再往上约 9 格，药罐顶到脚底约 61 格（约 671 px）**。脚底在离画布底边约 146 px 的地方（附图 9a、9b 的灰线）；站在画布中间（附图 9a、9b 的位置）。药罐、盾板、两只脚全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。**药罐的“发光”只用平涂的亮绿和高光块表现，不要柔光、不要半透明像素。**
> - 不画任何技能特效（毒雾、强力粘胶、过肩摔、喝药水的光都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/singed-picture/singed-A.png`、`singed-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/singed-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/singed_picture_done.zip`。

## 附图（在压缩包 `singed_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_singed_idle.png` | 英雄联盟原版辛吉德的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_singed_frontal.png` | 同一帧，正面 | 夹克、扣带、盾板、药瓶、腿和靴子 |
| `refs/3_singed_head.png` | 头部特写（3/4） | 光头、发白的眼睛、蒙脸布、围巾、护肩、药罐顶 |
| `refs/4_singed_back.png` | 同一帧的背后 | 背上的药罐怎么绑、盾板背面 |
| `refs/5_singed_splash.png` | 官方加载画面 | 气质、**脸和蒙脸布**、绿药罐的颜色 |
| `refs/6_singed_side.png` | 同一帧，侧面朝右 | SA 的角度 |
| `refs/7_singed_run.png` | 跑步的一帧（3/4） | 腿和手臂怎么动（这一步不画，后面用） |
| `refs/8_singed_fling.png` | E 过肩摔的一帧 | 盾板抡起来的样子（这一步不画，后面用） |
| `refs/9a_layout_singed.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 在画布上的位置、大小、地面线（灰）；浅灰线 = 药罐顶 |
| `refs/9b_layout_singed_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/10_style_drmundo.png` | 本包的蒙多医生，8 倍放大，一格 = 一个像素 | **只看风格**：祖安配色、光头怎么分档 |
| `style/11_style_urgot.png` | 本包的厄加特（8 倍） | **只看风格**：祖安的金属、铆钉、尖刺 |
| `style/12_style_gangplank.png` | 本包的普朗克（8 倍） | **只看风格**：红外套、金扣、高个子男人 |
| `style/13_style_vladimir.png` | 本包的弗拉基米尔（8 倍） | **只看风格**：又高又瘦的身子、苍白的脸 |

## 提示词：`singed-A.png` / `singed-SA.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-8 are 3D renders and art of a character from a game. THE MAD CHEMIST (images 1-8): a TALL, LANKY, HUNCHED old man with his neck pushed forward - BALD and scarred, a long gaunt face with sharp cheekbones and deep dark eye sockets, ONE EYE MILKY WHITE and the other normal, a GREY-GREEN CLOTH MASK over his mouth and nose, a big GREY-BLUE SCARF round his neck; a RED LEATHER JACKET with GOLD BUCKLED STRAPS crossing the chest and big SPIKED SHOULDER PADS (red with gold rims, silver spikes); a big GLOWING BRIGHT GREEN CHEMICAL TANK strapped on his back (round and bulging, a ring of rivets, a dark grey metal cap on top) rising above his head; a TALL GREY-GREEN RIVETED METAL PLATE (a shield with a few spikes on its edge and a wooden pole down it) hanging on his NEAR arm; a ROUND GREEN FLASK in his far hand; long thin claw-like hands in torn dark red gloves; a brown belt with little vials and torn cloth strips below it; THIN DARK BLUE trousers; HUGE HEAVY RED-BROWN BOOTS with spiked cuffs. (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the jacket, the straps, the shield plate, the flask, the legs and boots; 3 his head close-up: the bald head, the white eye, the cloth mask, the scarf, the shoulder pads, the tank top; 4 the same from behind: how the tank is strapped on, the back of the shield; 5 the official illustration: his mood, the FACE AND MASK, the green of the tank; 6 the idle from the side, facing right - the angle of SA; 7 a running frame and 8 the shield swung in a throw - both for later.) Images 9a-9b are layout guides: where the character goes on the canvas and how big, the grey line is the ground, the light line the tank top. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a bald head and sickly colours (10), riveted spiked metal (11), a red coat with gold buckles on a tall man (12), a tall thin body with a pale face (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the tank, the shield plate, the boots); the feet on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing where the guide shows the character (the centre). THE MAD CHEMIST is about 572 px (about 52 squares) from the top of his HEAD to his soles; the TANK rises about 9 squares above the head top (about 61 squares from the tank top to the soles).
PROPORTIONS: chibi. The HEAD BIGGER than in the renders (about a quarter of head-top-to-soles), the neck pushed forward, the back a little hunched; a thin body, LONG THIN LEGS, the BOOTS BIG and heavy, the two feet apart and planted; the green TANK big and clear behind his far shoulder; the shield plate standing on his near side, its top a little above his shoulder and its bottom near his knee - it NEVER covers the face and hides only his near arm and a little of the body.
THE FACE: bald, both eyes at the SAME height and both visible (each at least 2x2 squares): one MILKY near-white grey, one normal with a small dark pupil; dark eye sockets; a frowning brow, a grim mad look; everything below the nose covered by the GREY-GREEN CLOTH MASK (2-3 shades, a few folds); small slightly pointed ears.
THE COLOURS: the skin pale pinkish in 3 shades (purplish grey in the shadows); the cloth mask grey-green in 3; the scarf grey-blue in 3; the jacket red in 3-4; the straps, buckles and pad rims gold-yellow in 3; the spikes silver-grey in 2; the TANK glowing BRIGHT GREEN in 4 (the lightest a little yellow, like glowing liquid), its rivets and cap dark grey in 2-3; the shield plate grey-green metal in 3 with rivets; the gloves dark red-brown in 2; the trousers dark blue in 3; the boots red-brown in 3 with silver-grey spikes; the flask bright green in 2-3. Show the glow of the tank only with flat bright blocks - every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the pale face, the cloth mask, the red jacket, the gold straps, the green tank and the grey shield clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no poison cloud, no glue, no potion glow, no splashes); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (singed-A.png): THE MAD CHEMIST's idle in 3/4 view facing right (images 1, 2 and 9a) - standing hunched and ready, the face to the front-right; the NEAR arm with the shield plate and the NEAR leg on the image left in full tone, the FAR arm holding the green flask and the FAR leg on the image right a step darker and a little higher; the tank rising behind the far shoulder; nothing covering the face.
PICTURE SA (singed-SA.png): the SAME chemist as A seen exactly from the SIDE, FACING RIGHT (images 6 and 9b) - the face to the image right with one eye visible and the mask in profile, the shield plate on the near arm at his side, the tank on his back behind him, both feet on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，药罐、盾板、两只靴子完整，不出画。
- 辛吉德：Q 版但又高又瘦、驼背、脖子前探；**光头**；**两只眼睛一样高**，一只发白一只正常；**蒙脸布盖住鼻子以下**；灰蓝围巾；红夹克 + 金扣带 + 带刺护肩；**背后发光的亮绿药罐比头高约 9 格**；靠近我们一侧的灰绿盾板**不挡脸**；另一只手握绿药瓶；深蓝细腿 + 大红棕靴子。
- A 是 3/4 正面朝右，SA 是正侧面朝右；头顶到脚底约 572 px（约 52 格），药罐顶到脚底约 671 px（约 61 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/singed-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/singed_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：辛吉德的头（一张脸用在所有帧）、背上的药罐（跟着身体走，后面喷毒雾的口在罐子下面）、挂盾板的手臂（过肩摔要抡起来）、拿药瓶的手（扔粘胶、喝药）、两条细长腿和大靴子（跑）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | singed_idle1 / singed_run / singed_attack1–2 / — / singed_death | 普攻是用盾板砸 |
| **剧毒踪迹**（Q） | singed_spell1（跑的时候背后一直冒毒雾） | 毒雾是特效，后面单独画 |
| **强力粘胶**（W） | singed_spell2 | 把一瓶粘胶扔到远处，地上一大摊黄绿粘胶 |
| **过肩摔**（E） | singed_spell3 | 抓住敌人，抡过肩膀扔到身后 |
| **疯狂药剂**（R） | singed_spell4 | 仰头喝药，全身冒绿光 |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/singed/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的上路英雄（诺手、蒙多、厄加特、弗拉基米尔、普朗克）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_zac_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Singed`（singed_idle1、singed_run、singed_attack1/2、singed_spell1…4、singed_death）；不需要 `--hide-submeshes`。加载画面：`assets/characters/singed/skins/base/singedloadscreen.tex`。
