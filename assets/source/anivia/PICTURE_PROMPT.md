# 艾尼维亚（冰晶凤凰）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 艾尼维亚是一只**冰晶做成的大鸟（凤凰）**：全身是**蓝色的冰晶羽毛**，一片片像碎冰块一样有棱有角；**翅膀又宽又长**，外侧是浅冰蓝色，里面有**深蓝色的纹路**（像冰里的裂纹）；身体和脖子是**深蓝色**，背上有**紫色的花纹**；头上一圈**冰刺头冠**（中间一根最高），额头正中一颗**紫色的菱形宝石**；**尖尖的冰蓝色鸟喙**，**眼睛是亮洋红色**；腿和爪子是**深海军蓝色**，爪尖弯钩。请 Codex 画**两张图**（同一个艾尼维亚、同样的**格子大小**；两张**都要用**，不是二选一）：
> - **A：平时的样子**（英雄联盟里的待机，附图 1）：她**悬停在空中**，近侧的翅膀（画面左边）向下展开、几乎垂到地面，远侧的翅膀（画面右边）高高扬起、翼尖向下弯；身体微微前倾，头朝右前方，两只爪子垂在身体下面。
> - **B：寒霜涅槃的冰蛋**（被动：阵亡时变成冰蛋）。照英雄联盟自己的冰蛋模型画（附图 8、9）：**一个直立的椭圆冰蛋**（浅冰蓝色、带一点霜白，下半部颜色更深更蓝，隐约有冰的棱面），**坐在一圈向外张开的冰晶巢里**（一片片尖尖的冰块，亮青色）。蛋里面**不画**她的影子（英雄联盟里没有）。**和 A 用同样的格子大小**，蛋连巢从顶到底约 35 格（附图 10b）。B 用来做阵亡变蛋、蛋待机、孵化。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（PPU 1.2）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的塔姆、内瑟斯、斯维因和丽桑卓，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：她是大型生物，**不要 Q 版大头**；头（连冰刺头冠）**约占身体高度的五分之一**（约 12 格，比英雄联盟原版稍大一点，让脸在游戏里看得清），翅膀是她最大的形状。
> - **头**（附图 3 特写）：冰刺头冠分几档冰蓝（亮青、冰蓝、蓝、深蓝，不要一片浅蓝）；额头的**紫色菱形宝石**要清楚（至少 2×2 格）；**尖鸟喙**向前；**眼睛亮洋红色**（这个颜色只用在眼睛上），在喙的上方、宝石的下方。
> - **翅膀**：一片片有棱角的冰晶羽毛，外缘亮、里面深蓝的裂纹；近侧翅膀（画面左边）大、颜色亮；远侧翅膀（画面右边）稍暗。**翼尖、尾羽要完整画出来**，形状清楚，不要变成一根细线。
> - **身体**：深蓝色的胸口和脖子，背上的紫色花纹；**两条腿、两只爪子**（深海军蓝，爪尖弯钩）垂在身体下面。
> - **位置**：3/4 正面朝右（头朝右前方）。她悬停着，但**最低的那根翼尖（或尾羽）正好碰到地面线**——身体下面不要留一大块空。
> - **画布用正方形 1536×1536**。**A：从头冠顶到最低的翼尖约 704 px，也就是约 64 格**；最低处在离画布底边约 146 px 的地方（附图 10a 的灰线）。两只翅膀张开，整个宽度约 90 格，全在画面里，不能出画。**B：同样每格 11 像素，蛋连巢约 387 px 高（约 35 格）**，巢底在同一条线上（附图 10b）。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的深色描边**（很深的海军蓝，接近黑色）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。冰蓝羽毛、深蓝裂纹、深蓝身体、紫色花纹、紫色宝石、洋红眼睛、海军蓝爪子要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**深蓝的身体和爪子很暗，一定要有偏亮的冰蓝亮边**，不然在深色背景上会糊成一团。
> - 不画任何特效（冰雾、雪花、风暴、Q 的冰球都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/anivia-picture/anivia-A.png`、`anivia-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/anivia-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/anivia_picture_done.zip`。

## 附图（在压缩包 `anivia_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_anivia_idle.png` | 英雄联盟原版艾尼维亚的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势和两只翅膀的位置 |
| `refs/2_anivia_frontal.png` | 同一帧，正面 | 头冠、额头宝石、喙、胸口、两条腿和爪子怎么排 |
| `refs/3_anivia_head.png` | 头部特写 | 冰刺头冠、紫色菱形宝石、洋红眼睛、尖喙 |
| `refs/4_anivia_back.png` | 同一帧的背后 | 背上的紫色花纹、翅膀背面、尾羽 |
| `refs/5_anivia_splash.png` | 官方加载画面 | 气质、冰晶羽毛的颜色和光泽 |
| `refs/6_anivia_flight.png` | 飞行（英雄联盟的跑步）的一帧 | 翅膀完全张开时的形状、爪子收在身下 |
| `refs/7_anivia_q_cast.png` | Q 寒冰闪耀施法的一帧 | 翅膀扬起时的形状 |
| `refs/8_anivia_egg.png` | 英雄联盟的冰蛋（寒霜涅槃），3/4 | B 的样子：直立的冰蛋 + 一圈冰晶巢 |
| `refs/9_anivia_egg_side.png` | 同一个冰蛋，侧面 | 冰晶巢的冰块怎么排 |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/10b_layout_B.png` | B 的布局示意（同样的格子） | 蛋和巢的位置和大小、地面线（灰） |
| `style/11_style_tahmkench.png` | 本包的塔姆，8 倍放大，一格 = 一个像素（PPU 1.2，和艾尼维亚一样） | **只看风格**：大个子怎么分档、怎么留亮边 |
| `style/12_style_nasus.png` | 本包的内瑟斯（8 倍，PPU 1.2） | **只看风格**：大型生物的头占多少、暗色身体的亮边 |
| `style/13_style_swain.png` | 本包的斯维因（8 倍，PPU 1.5） | **只看风格**：小小的脸上眼睛怎么画清楚 |
| `style/14_style_lissandra.png` | 本包的丽桑卓（8 倍，1 倍密度），冰系英雄 | **只看风格**：冰蓝色在格子上怎么分档 |

## 提示词：`anivia-A.png` / `anivia-B.png`（同一段提示词，只换最后一句）

十五张图都附上，顺序同上表。

```text
Fifteen attached images. Images 1-9 are 3D renders and art of a character from the game: a LARGE BIRD MADE OF ICE CRYSTAL (a cryophoenix) - her whole body covered in BLUE ICE-CRYSTAL FEATHERS, each one an angular shard like broken ice; HUGE LONG WINGS, light ice-blue on the outside with DARK-BLUE VEINS inside like cracks in ice; a DARK-BLUE body and neck with VIOLET SWIRL MARKINGS on the back; a CROWN OF ICE SPIKES on her head (the middle one tallest) with a VIOLET DIAMOND GEM on the brow; a sharp ice-blue BEAK; bright MAGENTA EYES; DARK NAVY legs and hooked talons (1 her idle, 3/4 view facing right - the look, the ANGLE and pose A: hovering, the near wing spread DOWN almost to the ground, the far wing raised HIGH with its tip curling down; 2 the same from the front: the crown, the brow gem, the beak, the chest, both legs and talons; 3 the head close-up: the ice-spike crown, the violet gem, the magenta eye, the beak; 4 the same from behind: the violet markings, the wing backs, the tail feathers; 5 the official illustration: her mood and the colours and shine of her ice feathers; 6 her flight: the wings fully spread, talons tucked; 7 her spell cast: the wings raised; 8 and 9 her REBIRTH EGG from the game: an upright oval ice egg sitting in a ring of outward-pointing ice crystals). Images 10a and 10b are layout guides: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the dark outline, flat 3-4 step shading, how a huge body is split into clear shades with lit edges (11), how much of a big creature the head takes and lit edges on a dark body (12), a small face with two clear eyes (13), ice blues shaded on the grid (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (both wings, every wing tip and the tail whole); the lowest point on one ground line about 146 px above the bottom edge (the grey line of images 10a and 10b).
PROPORTIONS: a big creature, NOT a big-headed doll: the head with its ice-spike crown about one fifth of her body height (about 12 squares in A, a little bigger than in images 1-3 so the face reads at game size); the wings are her biggest shapes.
THE HEAD: the ice-spike crown in bright cyan / ice blue / blue / dark blue (never one flat light blue); the VIOLET DIAMOND GEM on the brow clear (at least 2x2 squares); the sharp beak pointing forward; the eye BRIGHT MAGENTA (that colour on the eye only), above the beak and below the gem.
THE WINGS: angular ice-crystal feathers, bright outer edges, dark-blue cracks inside; the NEAR wing (image left) big and bright, the FAR wing (image right) a step darker; every wing tip and the tail feathers drawn whole with clear shapes (never just a thin line).
THE BODY: a dark-blue chest and neck, the violet markings on the back; TWO LEGS with hooked DARK NAVY TALONS hanging under the body.
THE VIEW: 3/4 view facing right (the head to the front-right). She hovers, but her LOWEST wing tip or tail feather TOUCHES THE GROUND LINE - no big empty gap under her.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square very dark navy (almost black) outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the ice-blue feathers, the dark-blue cracks, the dark-blue body, the violet markings and gem, the magenta eye, the navy talons clearly separated; the DARK BODY AND TALONS WITH LIGHT ICE-BLUE LIT EDGES so they never turn into one dark mass; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no frost mist, no snowflakes, no storm, no ice ball), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (anivia-A.png): her idle (image 1) - hovering, the near wing spread down almost to the ground, the far wing raised high with its tip curling down, the body leaning a little forward, the head to the front-right, the talons hanging under the body. She is about 704 px (about 64 squares) from the top of her crown to her lowest wing tip, and about 90 squares wide with both wings.
POSE B (anivia-B.png): HER REBIRTH EGG (images 8 and 9) with the SAME 11-px squares: an UPRIGHT OVAL ICE EGG - pale ice blue with frosty white highlights, deeper blue in its lower half, faint ice facets - sitting in a RING OF OUTWARD-POINTING ICE CRYSTALS (sharp bright cyan shards); about 387 px (about 35 squares) from the top of the egg to the bottom of the nest, the nest's bottom on the same ground line (image 10b). Nothing inside the egg (no bird silhouette). No frost effects.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，两只翅膀、所有翼尖和尾羽完整，不出画。
- 比例：大型生物，不是大头娃娃；头连冰刺头冠约占身体高度五分之一（A 约 12 格）。
- 头：冰刺头冠分几档冰蓝；额头紫色菱形宝石清楚；尖喙向前；眼睛亮洋红色，洋红只用在眼睛上。
- 翅膀：有棱角的冰晶羽毛，外缘亮、里面深蓝裂纹；近侧翅膀（左）大而亮，远侧（右）稍暗。
- 身体：深蓝胸口和脖子，背上紫色花纹；两条腿、两只海军蓝弯钩爪子；深色部分有冰蓝亮边。
- A：待机姿势，悬停，最低的翼尖正好碰到地面线；从头冠顶到最低翼尖约 704 px（约 64 格），宽约 90 格。
- B：**同样每格 11 像素**；直立的椭圆冰蛋坐在一圈冰晶巢里，约 387 px 高（约 35 格），巢底在同一条地面线上；蛋里没有影子。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的深色外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- A、B 两张都画完后，最后写 `outputs/anivia-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/anivia_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/anivia/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_swain_hd.py` 的做法），和已合并的中单、大型生物（斯维因、丽桑卓、塔姆、内瑟斯、赫卡里姆）按游戏里的大小并排，给用户定大小；PPU 1.2（用户选的）。冰蛋按画面定大小（英雄联盟的蛋模型只有 40 码高，游戏里会放大）。
- 定下后第 1 步按游戏格子重画 A 和 B。动作参考英雄联盟的片段：anivia_idle1-3、anivia_run（飞行 = 跑步，扇翅膀，不换腿）、anivia_attack1/2、anivia_spell1（Q）、anivia_spell2（W）、anivia_spell3（E）、anivia_spell4 / anivia_channel（R）、anivia_death；冰蛋 RebirthEgg_Idle1 / RebirthEgg_death（碎蛋）。另外要做：变蛋（她缩进蛋里）、蛋待机、孵化（蛋裂开、她飞出来）。冰墙的冰块是英雄联盟的 AniviaIceblock 模型（第 3 步特效时渲染）。
