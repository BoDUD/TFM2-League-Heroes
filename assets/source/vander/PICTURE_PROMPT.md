# 范德尔（金铲铲之战 · 第 13 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 范德尔是金铲铲之战第 13 赛季的二费卡（家人 / 监察），双城之战里祖安地下城的老拳手、蔚和爆爆的养父，**远处的手（画面左）戴着一只红铜色的大铁拳套**。金铲铲里他**挺着胸、放松地站着，铁拳套垂在身侧**；打架时**屈膝压低、双拳举起**。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **长相**：中年壮汉，**深棕近黑的头发全部往后梳**，后面垂到脖子、发尾有几缕往外翘，额前有一两缕散下来；**又粗又黑的浓眉**（眉心微皱）；**灰蓝色的眼睛**，眼神沉稳、有点疲惫；鼻子宽直；**修短的深色络腮胡**（深棕带灰，下巴和嘴上的胡子连在一起）；嘴角往下抿，一脸严肃；脸是晒过的暖肤色。
> - **身上**：**一件宽大的焦橙色 / 铁锈橙皮夹克**（大翻领、肩膀很宽，袖口卷起，有几颗**黄铜扣子**）；里面是**米白色带竖条纹的马甲**，领口露出**青绿色的内衬**；腰上是**暗红色的宽腰带，挂着黄铜扣环**；**深藏青色的牛仔裤**；**黑色的厚工装靴，靴筒上有黄铜扣带**。**远处那条前臂套着紫色的护臂**；**两只手都缠着灰白色的绷带（露指）**。人很壮：肩宽、胸厚、手臂粗，肚子有一点。
> - **铁拳套**（附图 4、7、9）：套在**远处的手**上，比拳头大一圈：**黄铜色的八角形外框**，正面是**两块红色的面板**，上面有**金色的六角形螺栓**，指节上是**黄铜色的护板**，手腕处接着紫色护臂。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：站姿**（金铲铲原样，附图 1、2、6、10a）：**3/4 朝右**，挺胸站直、两脚分开站稳，**远处的手（画面左）戴着铁拳套自然垂在身侧**，**近处的手（画面右）握拳放在腰边**；抬着下巴、沉着地看向右前方。
> - **B：格斗架势**（附图 7、10b）：**3/4 朝右**，**屈膝压低、前后脚分开**（前脚在右），身体前倾，**两只拳头举在胸前**：戴铁拳套的远处的手在下方往前伸，近处缠绷带的拳头在上方护住下巴；眼睛盯着右前方。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的沃里克（他后来变成的样子）、布隆（同样的壮汉）、希尔科和爆爆（本系列的金铲铲英雄，爆爆是他的养女），**只看风格**。
> - **长相照金铲铲的模型**（附图 1、2、5、7、8、9 是模型的渲染，附图 3 是脸部特写；附图 6 是官方原画，**头发、胡子、脸以原画和附图 3 为准**；附图 4 是他正面拉紧拳套的样子，看拳套和夹克正面；附图 8 是他的防御架势，附图 9 是挥拳，只看拳套多大）。
> - **比例**：Q 版人类，**头约占身高的三分之一**（脸要大、要清楚，头发算在头里），身材**比一般英雄更壮**：肩宽、胸厚、手臂粗；铁拳套要大、要显眼。
> - **脸要清楚**（附图 3 特写、附图 6 原画）：皮肤 3 档；**两只眼睛一样高**，每只至少 1×2 格，深灰蓝，各有一格白色反光；**粗黑浓眉**压在眼睛上；**短络腮胡**从耳朵下面包到下巴，2–3 档深棕带灰；嘴在胡子里露出一格暗色；头发往后梳，额前一两缕，**头发不能盖住眼睛**。
> - **画布用正方形 1536×1536**。**A：从头发顶到脚底约 638 px，也就是约 58 格**，宽约 24 格（最多 30 格）；**B：屈膝压低，从头发顶到脚底约 572 px，也就是约 52 格**，宽约 43 格（前后脚分开 + 拳头，最多 48 格）。脚底在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（拳风、冲击波、嘲讽标记都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/vander-picture/vander-A.png`、`vander-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/vander-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/vander_picture_done.zip`。

## 附图（在压缩包 `vander_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_vander_34.png` | 金铲铲范德尔的模型，待机，3/4 朝右 | **A** 的姿势、颜色、**角度** |
| `refs/2_vander_front.png` | 模型，正面 | 夹克、马甲、腰带、裤子、靴子 |
| `refs/3_vander_head.png` | 头部特写 | **头发、浓眉、眼睛、胡子、脸** |
| `refs/4_vander_gauntlet.png` | 模型正面，在胸前拉紧拳套 | **铁拳套**、紫色护臂、绷带 |
| `refs/5_vander_back.png` | 背后 | 头发后面、夹克背面 |
| `refs/6_vander_art.png` | 官方原画（棋子卡面） | **头发、胡子、脸、神情** |
| `refs/7_vander_stance.png` | 模型格斗架势 | **B** 的姿势 |
| `refs/8_vander_guard.png` | 模型防御架势（拳套举过脸） | 只看拳套和身体的大小 |
| `refs/9_vander_punch.png` | 模型挥拳 | 只看拳套多大 |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 头顶 |
| `refs/10b_layout_B.png` | B 的布局示意 | 只看位置、大小和地面线 |
| `style/11_style_warwick.png` | 本包的沃里克，8 倍放大，一格 = 一个像素 | **只看风格**：祖安的壮汉怎么画 |
| `style/12_style_braum.png` | 本包的布隆（8 倍） | **只看风格**：壮汉的身材、粗手臂 |
| `style/13_style_silco.png` | 本系列的希尔科（8 倍） | **只看风格**：金铲铲英雄在格子上的样子 |
| `style/14_style_powder.png` | 本系列的爆爆（8 倍，他的养女） | **只看风格** |

## 提示词：`vander-A.png` / `vander-B.png`（同一段提示词，先画 A 再画 B）

十五张图都附上，顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fifteen attached images. Images 1-9 show ONE character from a game: a big, burly middle-aged BRAWLER from an industrial undercity - DARK BROWN, ALMOST BLACK HAIR all SWEPT BACK, falling to the nape of his neck with a few ends flicking out, one or two strands over the forehead; THICK BLACK BROWS slightly knitted; GREY-BLUE eyes, a calm, tired look; a broad straight nose; a SHORT TRIMMED FULL BEARD (dark brown with grey, the moustache joined to it); the mouth pressed and turned down, a stern look; warm tanned skin. A big loose BURNT-ORANGE / RUST-ORANGE LEATHER JACKET (wide lapels, broad shoulders, rolled cuffs, a few BRASS BUTTONS); under it a CREAM WAISTCOAT-SHIRT with thin VERTICAL STRIPES, a TEAL undershirt collar at the neck; a wide DARK RED BELT with BRASS BUCKLES; DARK NAVY JEANS; heavy BLACK WORK BOOTS with BRASS-BUCKLED straps. A PURPLE BRACER on his FAR forearm; BOTH hands wrapped in GREY-WHITE fingerless BANDAGES. He is broad and strong: wide shoulders, deep chest, thick arms, a slight belly. THE GAUNTLET on his FAR hand, bigger than a fist: an OCTAGONAL BRASS FRAME, its face TWO RED PANELS with GOLD HEXAGONAL BOLTS, BRASS plates over the knuckles, joined to the purple bracer at the wrist. (1 his idle, 3/4 view facing right - for picture A, the look and the ANGLE; 2 the same model from the front: the jacket, the waistcoat, the belt, the jeans, the boots; 3 his head close-up: the HAIR, the BROWS, the EYES, the BEARD and the face; 4 from the front tightening the gauntlet at his chest: THE GAUNTLET, the purple bracer, the bandages; 5 from behind; 6 the official art of him: follow it for the hair, the beard and the face; 7 his model in the FIGHTING STANCE, for picture B; 8 his defensive guard and 9 his punch: only how big the gauntlet is.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the ground, the light line the top of his hair. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 a beast-man of the same undercity, 12 a big strong man, 13 and 14 heroes of this same series).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the hair, the fists, the boots); his soles level on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO effects (no punch wind, no shockwave, no sparkles, no marks); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi - his head (with the hair) about ONE THIRD of his body height, the face big and clear, turned to the front-right; a BROAD, STRONG body, wider than an ordinary hero; the gauntlet big and easy to read. FACE CLEAR: skin in 3 shades; TWO EYES at the SAME height, each at least 1x2 squares, dark grey-blue with one white glint square each; THICK BLACK BROWS just over them; the SHORT BEARD from below the ears round the jaw in 2-3 dark brown-grey shades; a one-square dark mouth inside the beard; the hair swept back, one or two strands over the forehead, the hair never over the eyes. THE COLOURS: hair dark brown-black in 3; skin warm tan in 3; beard dark brown-grey in 2-3; jacket burnt orange in 3-4 with brass buttons; waistcoat cream in 2-3 with thin darker stripes; collar teal in 2; belt dark red in 2 with brass buckles; jeans dark navy in 3; boots black in 2 with brass; bracer purple in 2-3; bandages grey-white in 2; gauntlet frame and bolts brass-gold in 3, panels red in 2-3.
PICTURE A (vander-A.png): STANDING EASY, 3/4 view facing right (images 1, 2, 6 and 10a): chest out, feet apart and planted; his FAR hand (image left) in the GAUNTLET hanging down at his side; his NEAR hand (image right) a bandaged fist resting at his hip; chin up, looking calmly to the front-right. About 638 px (about 58 squares) from the top of his hair to his soles, about 24 squares wide (never more than 30).
PICTURE B (vander-B.png): THE FIGHTING STANCE, 3/4 view facing right (images 7 and 10b): knees bent low, feet wide apart (the front foot on the right), the body leaning forward; BOTH FISTS UP in front of his chest - the GAUNTLET fist (his far hand) lower and pushed forward, the bandaged near fist higher, guarding his chin; eyes fixed to the front-right. About 572 px (about 52 squares) from the top of his hair to his soles, about 43 squares wide (never more than 48); his soles on the ground line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、拳头、靴子完整，不出画。
- **A**：约 638 px（约 58 格），3/4 朝右，**挺胸站直，远处的手戴铁拳套垂在身侧，近处的手握拳在腰边**；脚底在地面线上。
- **B**：约 572 px（约 52 格），**屈膝压低、前后脚分开、双拳举在胸前（拳套在下往前、绷带拳在上护下巴）**；脚底在地面线上。
- 两张都要：**往后梳的深色头发 + 粗黑浓眉 + 灰蓝眼睛 + 短络腮胡**；**焦橙色皮夹克（黄铜扣子）+ 米白竖条纹马甲 + 青绿领口 + 暗红腰带黄铜扣 + 深藏青牛仔裤 + 黑工装靴**；**远处前臂紫色护臂 + 两手灰白绷带**；**黄铜八角框、红面板、金色六角螺栓的大铁拳套**；身材壮实。
- 没有特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/vander-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/vander_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有范德尔自己的动作（我已经按动作片段渲染出来了），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸用在所有帧、两只手（戴拳套的重拳、缠绷带的拳头）、两条腿（跑步、屈膝、跳起落地）。

| 动作 | 金铲铲里怎么做 / 我们的技能 |
|---|---|
| 待机 | 选 A：挺胸站着、拳套垂在身侧；选 B：屈膝格斗架势 |
| 移动 | 双拳举着像拳手一样小跑（金铲铲原样） |
| 普攻「铁拳」 | 戴拳套的手从上往下抡一记重拳，前脚跨出（金铲铲原样） |
| 技能1「地下猎犬」 | 跳进防御架势，拳套举过脸挡住，嘲讽周围的敌人；下一拳换成一记重击（金铲铲的施法动作） |
| 技能2「铁拳突进」 | 压低身子冲向敌人，一记上勾拳把对方打晕（金铲铲的第二种攻击） |
| 大招「桥头死守」 | 从架势里高高跳起，落地时拳套砸向地面，冲击波击飞周围的敌人（金铲铲的跳起重击） |
| 死亡 | 踉跄几步，脸朝下扑倒在地（金铲铲原样） |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/vander/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和沃里克、布隆、希尔科、爆爆、洛里斯按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_vander_picture.py`（模型在 Riot 客户端的 `TFTSet13.wad.client`；一个子网格 Valder_MAT；十段动作只有路径哈希，`CLIPS` 里按内容命名）。
