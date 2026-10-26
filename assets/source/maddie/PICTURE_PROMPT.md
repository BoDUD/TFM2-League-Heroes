# 麦迪（金铲铲之战 · 第 13 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 麦迪是金铲铲之战第 13 赛季（双城之战）的一费卡（执法官 / 狙神），皮尔特沃夫的女执法官、神枪手。金铲铲里她**站得笔直，把一杆粗长的海克斯步枪扛在近处的肩膀上，枪口朝后**。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **长相**：年轻女人，**橙红色的短发**（齐下巴的波波头，额前一排齐刘海，发尾往外翘），**灰蓝色的大眼睛**，脸颊和鼻梁上有**淡淡的雀斑**，表情冷静、略带一点不屑；
> - **帽子**：一顶**深灰绿色的贝雷帽**，斜戴，往画面右边歪；帽檐一圈**金色的帽带**，帽子前面一枚**金色的六边形帽徽**；
> - **身上**：**白色的高立领**；**宝蓝色的执法官制服外套**，肩上有**金色的肩章**，领口、前襟、袖口、下摆都镶**金边**；胸前一块**深藏青色的前片**，上面一枚**金色的皮尔特沃夫徽章**（中间一颗**发光的蓝色宝石**）；腰间一条**金色的腰带**；外套下摆在胯两边张开成两片燕尾；**黑色的长手套**；**淡紫灰色的宽松马裤**（大腿鼓起来，胯边有带金扣的口袋）；**黑色（带一点墨绿）的及膝长靴**，膝盖有**金色的护膝**，靴口和脚踝一圈金环。
> - **步枪**：一杆**粗长的海克斯步枪**（比她的手臂长得多）：**深藏青 / 黑色的枪身**，**金色的箍和配件**，枪管前端粗、开口大，握把前面嵌着一颗**发光的蓝色海克斯水晶**（看附图 6 原画）。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：扛枪**（金铲铲原样，附图 1–6、10a）：**3/4 朝右**，站得笔直，**近处的手（画面右）把步枪扛在近处的肩膀上，枪口朝后（画面左）**，枪身斜着架在肩上、从她的头后面伸出去；**远处的手（画面左）自然垂在身侧**；双脚并拢站稳，抬着下巴、冷冷地看向右前方。
> - **B：端枪**（附图 8、10b）：**3/4 朝右**，双脚前后分开站稳，**两只手把步枪端平在腰间**，**枪口朝右前方**（画面右）；身体微微前倾，盯着右前方，随时要开枪的样子。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的凯特琳（她的上司，皮城女警）、杰斯、金克丝（同一个故事）和爆爆（本系列第一个金铲铲英雄），**只看风格**。
> - **长相照金铲铲的模型**（附图 1–5 是模型的待机渲染，附图 3 是脸部特写；附图 6 是官方原画，**发型、雀斑、帽子、步枪的颜色以原画为准**；附图 7 是步枪单独的形状，**模型贴图是乱的，只看形状**；附图 9 是她蹲着连开数枪的样子，只看手臂和步枪有多长）。
> - **比例**：Q 版人类，**头约占身高的三分之一**（脸要大、要清楚，贝雷帽算在头里），身材匀称。
> - **脸要清楚**（附图 3 特写、附图 6 原画）：皮肤 3 档；**两只眼睛一样高**，每只至少 2×2 格，**灰蓝色**，各有一格白色反光；细细的橙棕色眉毛；嘴一格暗粉色；脸颊上一两格浅棕的雀斑；刘海不能盖住眼睛。
> - **画布用正方形 1536×1536**。**A 和 B：从贝雷帽顶到脚底都约 616 px，也就是约 56 格**；A 宽约 24 格（含扛在肩上的步枪，最多 32 格），B 宽约 30 格（含端平的步枪，最多 38 格）。脚底在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。步枪全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。发光的地方（步枪上的蓝水晶、胸前徽章的蓝宝石）用**更亮的一档平涂**表示，不要柔光。
> - 不画任何技能特效（枪口火光、子弹、通缉标记都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/maddie-picture/maddie-A.png`、`maddie-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/maddie-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/maddie_picture_done.zip`。

## 附图（在压缩包 `maddie_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_maddie_34.png` | 金铲铲麦迪的模型，待机，3/4 朝右 | 颜色、形状、**角度**、步枪怎么扛 |
| `refs/2_maddie_front.png` | 同一个待机，正面 | 制服、金边、胸前徽章、腰带、马裤 |
| `refs/3_maddie_head.png` | 头部特写 | **贝雷帽、头发、脸、立领** |
| `refs/4_maddie_side.png` | 侧面（右） | 身材厚度、燕尾下摆、靴子 |
| `refs/5_maddie_back.png` | 背后 | 头发后面、外套背面 |
| `refs/6_maddie_art.png` | 官方原画（棋子卡面） | **发型、雀斑、贝雷帽、步枪的颜色和蓝水晶** |
| `refs/7_maddie_rifle.png` | 步枪单独，侧面 | **只看形状**（模型贴图是乱的，颜色看原画） |
| `refs/8_maddie_ready.png` | 模型端枪的样子 | **B**：步枪端平在腰间 |
| `refs/9_maddie_spell.png` | 模型蹲着连开数枪 | 只看手臂和步枪的长度 |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 帽顶 |
| `refs/10b_layout_B.png` | B 的大小示意 | 只看大小和地面线 |
| `style/11_style_caitlyn.png` | 本包的凯特琳（皮城女警、她的上司），8 倍放大，一格 = 一个像素 | **只看风格**：皮城执法官、长枪怎么画 |
| `style/12_style_jayce.png` | 本包的杰斯（8 倍） | **只看风格**：皮尔特沃夫的蓝金配色 |
| `style/13_style_jinx.png` | 本包的金克丝（8 倍） | **只看风格**：双城之战的人物、大号枪械 |
| `style/14_style_powder.png` | 本系列的爆爆（8 倍） | **只看风格**：金铲铲英雄在格子上的样子 |

## 提示词：`maddie-A.png` / `maddie-B.png`（同一段提示词，先画 A 再画 B）

十五张图都附上，顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fifteen attached images. Images 1-9 show ONE character from a game: a young POLICEWOMAN SHARPSHOOTER - short ORANGE-GINGER HAIR in a chin-length bob with a straight fringe and the ends flicking out, big GREY-BLUE eyes, light FRECKLES on her cheeks and nose, a calm, slightly scornful look. A DARK GREY-GREEN BERET worn tilted toward image right, a GOLD band round its rim and a GOLD HEXAGON BADGE on its front. A WHITE HIGH COLLAR; a ROYAL BLUE uniform jacket with GOLD EPAULETTES and GOLD TRIM on the collar, the front edges, the cuffs and the hem; a DARK NAVY chest panel with a GOLD crest in the middle holding a GLOWING BLUE GEM; a GOLD belt; the jacket's hem opening into two short tails at her hips; long BLACK GLOVES; baggy LAVENDER-GREY riding trousers puffed at the thighs, with gold-buckled pockets at the hips; KNEE-HIGH BLACK BOOTS (a little dark teal in the light) with GOLD KNEE GUARDS and gold rings at the top and the ankle. She carries a big LONG HEXTECH RIFLE, much longer than her arm: a DARK NAVY / BLACK body, GOLD bands and fittings, a thick barrel with a wide muzzle, a GLOWING BLUE HEXTECH CRYSTAL set in front of the grip. (1 her idle, 3/4 view facing right - the look, the ANGLE, how the rifle rests on her shoulder; 2 the same idle from the front: the jacket, the gold trim, the crest, the belt, the trousers; 3 her head close-up: the BERET, the HAIR and the face; 4 from the side; 5 from behind; 6 the official art: her hair, freckles, beret and the rifle's COLOURS with its blue crystal - follow it for the face and the rifle colours; 7 the rifle alone: its SHAPE only, its texture there is broken; 8 her model holding the rifle level at her hip, for picture B; 9 her model crouched firing: how long her arms and the rifle are.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the ground, the light line the top of her beret. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 a policewoman with a long rifle from the same city, 12 a man in the same blue and gold, 13 a girl from the same story with big guns, 14 a hero of this same series).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the beret, the rifle); her soles level on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; GLOW drawn only as a brighter flat shade (the rifle's blue crystal, the blue gem on her chest), never a soft halo; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO effects (no muzzle flash, no bullets, no smoke, no sparkles, no target marks); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi - her head (with the beret) about ONE THIRD of her body height, the face big and clear, turned to the front-right; a trim, upright body. FACE CLEAR: skin in 3 shades; TWO EYES at the SAME height, each at least 2x2 squares, GREY-BLUE with one white glint square each; thin orange-brown brows; a one-square dark pink mouth; one or two light brown freckle squares on the cheeks; the fringe never over the eyes. THE COLOURS: hair orange-ginger in 3-4; skin warm light in 3; beret dark grey-green in 3 with a gold band and badge in 2; collar white in 2; jacket royal blue in 3-4 with gold trim in 2; chest panel dark navy in 2 with a gold crest and a bright blue gem; belt gold in 2; gloves black in 2; trousers lavender-grey in 3; boots black / dark teal in 2-3 with gold guards and rings in 2; rifle dark navy / black in 3 with gold bands in 2 and a glowing blue crystal in 2.
PICTURE A (maddie-A.png): THE RIFLE ON HER SHOULDER, 3/4 view facing right (images 1-6 and 10a): she stands tall, feet together; her NEAR hand (image right) holds the rifle resting on her near shoulder, the rifle lying slanted across behind her head with its MUZZLE pointing BACK (image left, a little up); her FAR arm hangs at her side; chin up, looking coolly to the front-right. About 616 px (about 56 squares) from the top of her beret to her soles, about 24 squares wide with the rifle (never more than 32).
PICTURE B (maddie-B.png): THE RIFLE LEVEL AT HER HIP, 3/4 view facing right (images 8 and 10b): feet apart one before the other, standing firm; BOTH HANDS hold the rifle level at her waist, its MUZZLE pointing to the FRONT-RIGHT (image right); leaning a little forward, eyes on the front-right, ready to fire. About 616 px (about 56 squares) from the top of her beret to her soles, about 30 squares wide with the rifle (never more than 38); her soles on the ground line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，贝雷帽、步枪完整，不出画。
- **A**：约 616 px（约 56 格），3/4 朝右，**近处的手把步枪扛在肩上、枪口朝后（画面左）**，远处的手垂在身侧；脚底在地面线上。
- **B**：约 616 px（约 56 格），**两只手把步枪端平在腰间、枪口朝右前方**；脚底在地面线上。
- 两张都要：**橙红短波波头 + 齐刘海 + 雀斑 + 灰蓝眼睛**；**歪戴的深灰绿贝雷帽 + 金帽徽**；**白立领 + 金边宝蓝制服 + 胸前金徽章蓝宝石 + 金腰带 + 黑手套 + 淡紫灰马裤 + 黑长靴金护膝**；**深藏青金箍的海克斯步枪 + 蓝水晶**。
- 没有特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/maddie-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/maddie_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有麦迪自己的动作（我已经按动作片段渲染出来了，后面的骨架包会附上），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸用在所有帧、两只手（端枪、开枪、换弹时会动）、整杆步枪（会从肩上放下来端平、开枪后枪口上扬）、外套燕尾下摆、两条腿（跑步、蹲射）。

| 动作 | 金铲铲里怎么做 / 我们的技能 |
|---|---|
| 待机 | 步枪扛在肩上站得笔直 |
| 移动 | 端着步枪低姿小跑（金铲铲原样） |
| 普攻 | 端枪开一枪，后坐力把枪口顶起来，再放平（金铲铲原样） |
| 技能1「连拨击锤」 | 单膝半蹲、枪托抵肩，朝最远的敌人连开 6 枪（金铲铲的施法动作） |
| 技能2「通缉令」 | 一只手举起来指向目标，在它头上打出通缉标记 |
| 大招「执法狙杀」 | 半蹲架枪瞄准 1 秒，一发贯穿全场的狙击 |
| 死亡 | 被打得向后仰倒在地（金铲铲原样） |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/maddie/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和凯特琳、爆爆、诺拉、拉露恩按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_maddie_picture.py`（模型在 Riot 客户端的 `TFTSet13.wad.client`；子网格 Maddie_Mat / Maddie_Weapon_Mat（步枪，贴图对不上）；七段动作只有路径哈希，`CLIPS` 里按内容命名）。
