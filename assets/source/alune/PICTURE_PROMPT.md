# 拉露恩（金铲铲之战 · 第 18 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 拉露恩是金铲铲之战第 18 赛季的五费卡（月华神女 / 月蚀骑士 / 法师），厄斐琉斯的妹妹、月之教派的女祭司。她**侧坐在一把巨大的月牙法杖上漂浮**，双手抱在胸前；法杖就是她的武器。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **长相**：年轻女子，**银白 / 淡冰蓝色的短发**（齐下巴的蓬松短发，发尾微翘），**头上一对深蓝紫色的月牙形角饰**（一大一小，从头顶左右伸出、往上弯，像新月），额头正中一颗**发光的白蓝色圆形月珠**（第三只眼）；**脸色白皙**，**青绿色眼影**，深色嘴唇，眼睛淡紫 / 灰蓝；小耳坠；
> - **身上**：**深海军蓝高领**、领口和前襟镶**金边**，脖子上一串**青绿色水晶项链**；外面一件**宽袖的紫色长袍**（亮蓝紫 / 靛紫，袖子和下摆上有**青色发光的卷云纹**），腰间一条**墨绿色宽腰带**、挂着深色的饰扣；长袍下摆很长、像裙子一样散开，下端是**一圈波浪状的深紫火焰形下摆**；手是白皙的，指甲淡紫。
> - **武器（月牙法杖）**：一把**比她还大的新月形长柄刃**：**青铜 / 暗金色的弯月骨架**，外缘是**发光的亮蓝色刀刃**（刃上有浅蓝的卷纹），月牙中间是**一圈螺旋形的蓝色圆环**，环中心是**一颗发光的淡蓝色月球**，被两片青铜的托爪夹着；月牙的下端有一个**青铜的尖头底座**。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：骑在月牙上**（金铲铲原样，附图 1–6、10a）：**3/4 朝右**，她**侧坐在月牙法杖的上沿**，双手交叉抱在胸前，脸朝右前方；**月牙在她身下和身后**——弯月的弧从她身后（画面左）绕下来，**螺旋圆环和月球在她腿边（画面左下）**，月牙的尖头底座是整个图最低的点；长袍下摆从她腿上垂下来、盖住月牙的一部分。她是**漂浮**的，不站在地上。
> - **B：站着拿着法杖**（附图 7、8、10b）：**3/4 朝右**，她**自己站在地上**（长袍下摆到脚面，露一点鞋尖），**近处的手（画面右）握着月牙法杖竖在身体前侧**，法杖的长柄着地或略离地，螺旋圆环和月球在她肩膀旁边；远处的手放在胸前。法杖整根在画面里。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的厄斐琉斯（她哥哥）、拉克丝、佐伊和爆爆（本系列第一个金铲铲英雄），**只看风格**。
> - **长相照金铲铲的模型**（附图 1–5 是模型的待机渲染，附图 3 是脸部特写；附图 6 是官方原画看气质和颜色；附图 7、8 是模型的站姿，只看站着时法杖拿在哪、多大）。
> - **比例**：Q 版人类，**头约占身高的三分之一**（脸要大、要清楚）；长袍是往下变宽的梯形。
> - **脸要清楚**（附图 3 特写）：皮肤 3 档；**两只眼睛一样大、一样高**，每只至少 2×2 格，看得见淡紫的眼珠和一格白色反光；**额头中间的月珠 2×2 格、亮白蓝**；青绿眼影一格；深色嘴一格；头发不能盖住眼睛；**月牙角饰**在头顶清楚地翘起来。
> - **画布用正方形 1536×1536**。**A：从角饰顶到月牙尖头底座约 660 px，也就是约 60 格**；宽约 30 格（含月牙和圆环，最多 36 格）。**B：从法杖顶到脚底约 572 px，也就是约 52 格**；宽约 36 格（含法杖，最多 44 格）。最低点在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。角饰、法杖、圆环全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。发光的地方（月珠、刀刃、圆环、袍子上的卷云纹）用**更亮的一档平涂**表示，不要柔光。
> - 不画任何技能特效（月光碎片、月亮、星光都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/alune-picture/alune-A.png`、`alune-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/alune-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/alune_picture_done.zip`。

## 附图（在压缩包 `alune_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_alune_34.png` | 金铲铲拉露恩的模型，待机，3/4 朝右 | 颜色、形状、**角度**、她怎么坐在月牙上 |
| `refs/2_alune_front.png` | 同一个待机，正面 | 高领、项链、腰带、抱臂 |
| `refs/3_alune_head.png` | 头部特写（3/4） | **头发、月牙角饰、额头月珠、脸、眼影** |
| `refs/4_alune_side.png` | 侧面（右） | 月牙法杖侧面、长袍下摆 |
| `refs/5_alune_back.png` | 背后 | 头发后面、长袍背面 |
| `refs/6_alune_art.png` | 官方原画（棋子卡面） | 气质、脸、颜色 |
| `refs/7_alune_standing.png` | 模型站姿（施法时），圆环举在身侧 | **B**：站着时的身材、圆环的大小 |
| `refs/8_alune_attack.png` | 模型站姿（普攻时），法杖横着挥 | **B**：站着时法杖的长度和样子 |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 角饰顶 |
| `refs/10b_layout_B.png` | B 的大小示意 | 只看大小和地面线（法杖要竖着拿，不是横着） |
| `style/11_style_aphelios.png` | 本包的厄斐琉斯（她哥哥），8 倍放大，一格 = 一个像素 | **只看风格**：同一个教派的衣服和白发怎么画 |
| `style/12_style_lux.png` | 本包的拉克丝（8 倍） | **只看风格**：女法师、大脸、长袍 |
| `style/13_style_zoe.png` | 本包的佐伊（8 倍） | **只看风格**：发光的东西用平涂亮色 |
| `style/14_style_powder.png` | 本系列的爆爆（8 倍） | **只看风格**：金铲铲英雄在格子上的样子 |

## 提示词：`alune-A.png` / `alune-B.png`（同一段提示词，只换最后一段）

十四张图都附上（没有 9 号），顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fourteen attached images. Images 1-8 show ONE character from a game: a young MOON PRIESTESS - pale skin, a fluffy chin-length bob of SILVER-WHITE / ICE-BLUE HAIR, a pair of DARK BLUE-VIOLET CRESCENT HORN ornaments rising and curving up from the top of her head (one big, one small, like new moons), a GLOWING WHITE-BLUE ROUND MOON GEM in the middle of her forehead, TEAL eye shadow, pale violet eyes, dark lips, small earrings. A DARK NAVY HIGH COLLAR with GOLD TRIM down the front, a TEAL CRYSTAL NECKLACE; over it a WIDE-SLEEVED PURPLE ROBE (bright blue-violet / indigo) with GLOWING CYAN SWIRL embroidery on the sleeves and skirt, a wide DARK GREEN SASH at the waist with dark buckles; the robe falls long like a skirt and ends in a WAVY flame-like dark violet hem; pale hands, lilac nails. Her WEAPON is a CRESCENT-MOON GLAIVE bigger than herself: a BRONZE / DARK GOLD crescent frame with GLOWING BRIGHT BLUE BLADES along its outer edge (pale blue swirls on the blades), inside the crescent a SPIRAL BLUE RING holding a GLOWING PALE BLUE MOON ORB in two bronze claws, a pointed bronze foot at the crescent's lower end. (1 her idle, 3/4 view facing right - the look, the ANGLE and HOW SHE SITS ON THE CRESCENT; 2 the same idle from the front: the collar, the necklace, the sash, the crossed arms; 3 her head close-up: the HAIR, the CRESCENT HORNS, the FOREHEAD MOON GEM, the face, the eye shadow; 4 from the side: the glaive edge-on, the hem; 5 from behind; 6 the official art: her face and colours; 7 and 8 her model standing on her feet with the glaive, for picture B: how big the glaive is next to her.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the lowest point, the light line the top of the figure. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 her brother in the same order's clothes with white hair, 12 a girl mage in a robe with a big face, 13 glowing things drawn as flat bright shades, 14 a hero of this same series).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the horns, the glaive, the ring); the lowest point level on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; GLOW drawn only as a brighter flat shade (the moon gem, the blades, the ring, the swirls), never a soft halo; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO spell effects (no moonshards, no falling moon, no stars, no sparkles); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi - her head about ONE THIRD of her body height (without the glaive), the face big and clear, turned to the front-right; the robe a trapezoid widening down. FACE CLEAR: skin in 3 shades; TWO EYES the SAME size and at the SAME height, each at least 2x2 squares, pale violet with one white glint square; the FOREHEAD MOON GEM 2x2 squares, bright white-blue; one square of teal eye shadow over each eye; a dark one-square mouth; the hair never over the eyes; the CRESCENT HORNS clearly rising from the top of her head. THE COLOURS: hair silver-white / ice blue in 3-4; horns dark blue-violet in 3 with a lighter violet edge; skin pale in 3; collar dark navy in 2-3 with gold trim in 2; necklace teal in 2; robe blue-violet / indigo in 3-4 with cyan swirls in 2, the hem dark violet; sash dark green in 2-3; glaive frame bronze / dark gold in 3-4; blades and spiral ring bright blue in 3 with pale blue swirls; moon orb pale blue in 2 with a white glint.
PICTURE A (alune-A.png): RIDING THE CRESCENT, 3/4 view facing right (images 1-6 and 10a): she SITS SIDEWAYS on the upper edge of the crescent glaive, both arms CROSSED over her chest, her face to the front-right; the crescent is UNDER and BEHIND her - its arc sweeps down behind her (image left), the SPIRAL RING with the MOON ORB beside her legs (image lower-left), the bronze pointed foot of the crescent the LOWEST point of the whole picture; the robe's skirt hangs down from her lap over part of the crescent. She FLOATS - no feet on the ground. About 660 px (about 60 squares) from the top of the horns to the crescent's foot, about 30 squares wide with the crescent and the ring (never more than 36).
PICTURE B (alune-B.png): STANDING WITH THE GLAIVE, 3/4 view facing right (images 7, 8 and 10b): she STANDS on her own feet (the robe down to her feet, the tips of her shoes just showing), her NEAR hand (image right) holding the crescent glaive UPRIGHT in front of her side, its pointed foot on the ground line or just above it, the spiral ring and the moon orb beside her shoulder, the crescent's blade curving over her head; her far hand resting on her chest. About 572 px (about 52 squares) from the top of the glaive to her soles, about 36 squares wide with the glaive (never more than 44); the lowest point on the ground line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，角饰、法杖、圆环完整，不出画。
- **A**：约 660 px（约 60 格），3/4 朝右，**侧坐在月牙上、双手抱胸**，螺旋圆环和月球在她腿边，月牙尖头底座是最低点；她是漂浮的。
- **B**：约 572 px（约 52 格），**自己站着**，近处的手**竖着握住月牙法杖**，圆环和月球在肩旁；脚底在地面线上。
- 两张都要：**银白短发 + 深蓝紫月牙角饰 + 额头发光月珠**；两只眼睛一样大、一样高；**紫色长袍 + 青色卷云纹 + 墨绿腰带 + 金边高领**；**青铜月牙 + 亮蓝刀刃 + 螺旋环 + 淡蓝月球**。
- 没有技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/alune-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/alune_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有拉露恩自己的动作（我已经按动作片段渲染出来了，后面的骨架包会附上），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸用在所有帧、两只手（施法时会举起来）、月牙角饰、长袍下摆、月牙法杖的骨架、**螺旋圆环和月球（会从月牙上取下来单独转）**。

| 动作 | 金铲铲里怎么做 |
|---|---|
| 待机 | 侧坐在月牙上漂浮，双手抱胸，轻轻上下浮动 |
| 移动 | 从月牙上站起来，**站在月牙上滑行**（像踩着冲浪板），圆环收进月牙里 |
| 普攻 | 站起来把螺旋圆环像飞盘一样平着甩出去 |
| 施法（月之降临） | 把圆环举到脑后像一圈光环，双手张开引导，月光碎片从天上落到敌人身上 |
| 满月（大招） | 举起圆环，一轮巨大的满月从天上砸下来（三星时的样子，视频里确认过） |
| 死亡 | 往后倒，月牙法杖碎成几个圆环散落 |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/alune/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和厄斐琉斯、拉克丝、爆爆按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_alune_picture.py`（模型在 Riot 客户端的 `TFTSet18.wad.client`，WeGame 客户端只到第 17 赛季；武器和下摆用第 11 赛季的贴图；动作片段只有路径哈希，`CLIPS` 里按内容命名）。
