# 影哨 阿克尚：第 0 步，先画像素风原图（给 Codex 的提示词）

> 阿克尚是一个**游侠枪手**：**棕色的皮肤**，**深棕色的长卷发**（头顶扎一个小发髻，其余披到肩后），**短络腮胡**，眉眼清楚、神情自信。**上身赤膊、肌肉结实**；脖子和肩膀上围着一条**浅蓝白色的大围巾 / 兜帽披肩**，两肩各有一块**灰色的护肩**（金色包边、一个金色尖角饰片）；一条**橙红色的宽饰带**从近侧肩膀斜挎到远侧腰间，中间套着一个**金色的宽箍**；背后垂着一件**长长的暗红色披风**（披风背面是橙色底、金色花纹，边上浅蓝）；腰上系着**青绿色的腰带**，前面垂下一条**青绿色的长布片**（中间一个金环）；下身是**深灰黑色的裤子**，**黑色的高筒靴**；两只前臂各戴一个**金色的护腕**，手上是**浅蓝色的无指手套**。武器是他的**遗迹手枪**：一把**很大的暗红色带青铜色的枪**，枪口前端是**两道弯钩、像回旋镖一样的形状**，握把是青白色。请 Codex 画**两张全身像**（同一个阿克尚，长相、颜色、**格子大小**都一样），用户从里面挑一张做游戏里的待机：
> - **A：英雄联盟里的待机**（附图 1、8a）。站直、两腿分开，**近侧的手把枪举在头边、枪口朝上**（枪在头的上方），**远侧的手叉在腰上**，披风垂在身后，脸朝右前方。
> - **B：备战姿势**（附图 8b 只看大小和地面线）。两腿分开微屈，**近侧的手把枪平端在胸前、枪口朝右**（像要开枪，参考附图 6 的手臂方向，但不要伸得那么远，手肘弯着），**远侧的手叉在腰上**；这样整个人不高出头太多。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的普朗克（拿手枪、长外套）、赵信和斯维因（长披风），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：Q 版，**头（连头发）约占身高的三分之一**（约 23 格）；身子和腿短一些，手和枪大；不要细长的写实比例。
> - **头**（附图 3 特写）：深棕长卷发分几档颜色，头顶的小发髻要看得出；棕色的脸要清楚；**两只眼睛一样大、一样高、都看得见**（每只至少 2 格，眼白 + 深色瞳孔），浓眉，短胡子（比头发稍浅一点的深棕），嘴角带点笑。
> - **衣服**：浅蓝白围巾和灰色护肩（金边）、斜挎的橙红饰带和金箍、背后的暗红长披风、青绿腰带和青绿长布片（金环）、深灰黑裤子、黑高筒靴、金护腕、浅蓝无指手套。赤膊的胸口和手臂是棕色皮肤，**要有亮一点的边**，不要糊成一块。
> - **枪**：暗红色带青铜色、前端两道回旋镖一样的弯钩，握把青白；**形状完整、轮廓清楚**，比他的头稍大一点。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。两只鞋底落在同一条地面线上。
> - **画布用正方形 1536×1536**。**从头顶头发到鞋底约 770 px，也就是约 70 格**（A 里举高的枪可以高出头顶，不算在内），鞋底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。枪、披风、手全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。棕色皮肤、深棕头发、浅蓝白围巾、灰护肩、金色、橙红饰带、暗红披风、青绿腰带、深灰黑裤子、黑靴、暗红青铜的枪要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**暗红披风、黑裤子和黑靴很暗，一定要有偏亮的边**，不然在深色背景上会糊成一团。
> - 不画任何特效（枪口火光、子弹、回旋镖飞行、钩索、伪装都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/akshan-picture/akshan-A.png`、`akshan-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/akshan-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/akshan_picture_done.zip`。

## 附图（在压缩包 `akshan_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_akshan_idle.png` | 英雄联盟原版阿克尚的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势和举枪的方法 |
| `refs/2_akshan_frontal.png` | 同一帧，正面 | 围巾、饰带、腰带、布片怎么排 |
| `refs/3_akshan_head.png` | 头部特写（没有枪） | 卷发和发髻、脸、眼睛、胡子、围巾、护肩 |
| `refs/4_akshan_back.png` | 同一帧的背后 | 披风背面的颜色和花纹、发髻 |
| `refs/5_akshan_splash.png` | 官方加载画面 | 气质、颜色、枪的样子 |
| `refs/6_akshan_attack.png` | 普攻开枪的一帧 | 枪平端朝右时的样子（B 的手臂方向，但手肘弯着、不要伸那么远） |
| `refs/7_akshan_side.png` | 同一帧，接近侧面 | 披风、布片、枪从侧面看的厚度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 他的大小、地面线（灰）；**姿势按文字：枪平端在胸前朝右** |
| `style/11_style_gangplank.png` | 本包的普朗克，8 倍放大，一格 = 一个像素 | **只看风格**：手枪、外套、络腮胡在格子上怎么画 |
| `style/12_style_xinzhao.png` | 本包的赵信（8 倍） | **只看风格**：格子密度、描边、每种材质分几档 |
| `style/13_style_swain.png` | 本包的斯维因（8 倍） | **只看风格**：长披风在格子上怎么画、暗色衣服的亮边 |

## 提示词：`akshan-A.png` / `akshan-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a ROGUE GUNSLINGER - BROWN SKIN, LONG WAVY DARK-BROWN HAIR with a small TOPKNOT on the crown and the rest falling behind the shoulders, a SHORT BEARD, thick brows, a confident half smile; a BARE MUSCULAR CHEST; a PALE BLUE-WHITE SCARF / hooded cowl round the neck and shoulders, a GREY SHOULDER PAD on each shoulder trimmed with gold (a gold pointed plate on each); a WIDE ORANGE-RED SASH slung diagonally from the near shoulder to the far hip with a WIDE GOLD BAND round it; a LONG DARK-RED CAPE hanging behind (its back orange with a gold pattern, a pale blue edge); a TEAL BELT with a LONG TEAL CLOTH hanging down the front (a gold ring on it); DARK GREY-BLACK TROUSERS, TALL BLACK BOOTS; a GOLD BRACER on each forearm and PALE BLUE FINGERLESS GLOVES; his weapon, a BIG RELIC PISTOL - dark crimson with bronze, its front two CURVED HOOKS like a boomerang, a pale teal-white grip (1 his idle, 3/4 view facing right - the look, the ANGLE, pose A and how he raises the gun; 2 the same from the front: the scarf, the sash, the belt and the cloth; 3 the head close-up without the gun: the hair and topknot, the face, the eyes, the beard, the scarf, the shoulder pads; 4 the same from behind: the cape's back and the topknot; 5 the official illustration: his mood, colours and the gun; 6 a frame of his shot: the gun held level pointing right; 7 the idle nearly from the side: the depth of the cape, the cloth and the gun). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a pistol, a coat and a beard on the grid (11), the square density, the outline and the number of shades a material gets (12), a long cape on the grid with light edges on dark cloth (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the gun, the cape and both hands whole); both soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 770 px (about 70 squares) from the top of his hair to his soles - a gun raised above his head is not counted.
PROPORTIONS: chibi - the head with the hair about ONE THIRD of his height (about 23 squares); a shorter body and legs, big hands and a big gun; NOT realistic slim proportions.
THE HEAD: the long wavy dark-brown hair in a few shades with the small topknot readable; the brown face clearly readable; TWO EYES of the SAME size at the SAME height, both visible (each at least 2 squares, white with a dark pupil); thick brows; a short beard a shade lighter than the hair; a half smile.
THE CLOTHES: the pale blue-white scarf and the grey gold-trimmed shoulder pads, the diagonal orange-red sash with its gold band, the long dark-red cape behind, the teal belt and the long teal front cloth with its gold ring, the dark grey-black trousers, the tall black boots, the gold bracers, the pale blue fingerless gloves; the bare chest and arms brown skin with LIGHTER EDGES.
THE GUN: dark crimson with bronze, the two boomerang-like hooks at its front, the pale teal-white grip; a WHOLE clear silhouette, a little bigger than his head.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark-red cape, the black trousers and the black boots with LIGHTER EDGES so they never turn into one dark mass, the brown skin, the dark-brown hair, the pale blue scarf, the grey pads, the gold, the orange-red sash, the teal cloth and the crimson gun clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no muzzle flash, no bullet, no flying boomerang, no rope, no camouflage shimmer, no glow), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (akshan-A.png): his idle (images 1 and 8a) - standing upright, feet apart, the NEAR hand raising the gun beside his head with its front pointing UP (the gun above his head), the FAR hand on his hip, the cape hanging behind him; the face to the front-right.
POSE B (akshan-B.png): a READY STANCE - the SAME gunslinger with the SAME 11-px squares: feet apart, knees a little bent, the NEAR hand holding the gun LEVEL in front of his chest pointing RIGHT (the elbow bent, not stretched as far as in image 6), the FAR hand on his hip, the cape hanging behind him, so nothing rises much above his head; the face to the front-right (image 8b shows only his size and the ground line).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，枪、披风、两只手完整，不出画。
- 比例：Q 版，头（连头发）约占身高三分之一（约 23 格）；手和枪大。
- 头：深棕长卷发分几档、小发髻看得出；**两只眼睛一样大、一样高、都看得见**；浓眉、短胡子、嘴角带笑。
- 衣服：浅蓝白围巾、灰色金边护肩、斜挎橙红饰带和金箍、暗红长披风、青绿腰带和长布片（金环）、深灰黑裤子、黑高筒靴、金护腕、浅蓝无指手套；棕色皮肤有亮边。
- 枪：暗红带青铜、前端两道回旋镖弯钩、青白握把，轮廓完整。
- A：站直、近侧手把枪举在头边朝上、远侧手叉腰；B：微屈、近侧手把枪平端在胸前朝右（手肘弯着）、远侧手叉腰。从头顶到鞋底约 770 px（约 70 格），鞋底都在同一条地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/akshan-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/akshan_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/akshan/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_wukong_hd.py` 的做法，绝不按更少的行采样），和已合并的远程（卢锡安、烬、凯特琳、伊泽瑞尔、普朗克、赵信）按游戏里的大小并排，**早点给用户看 PPU 对比**（茂凯的教训：1.2 / 1.3 / 1.5 并排），给用户挑 A / B 和定大小。
- 定下后第 1 步按游戏格子重画，再自己做动作帧（茂凯 / 悟空的方式，无损：只平移、整块直角转、整行移；**枪是刚体，每帧都用设计里的同一把**，不旋转出锯齿）；走路：两腿用设计里自己的整条腿。删行删列后检查前臂、手腕、枪管这些细的连接处（茂凯的教训）。英雄联盟的动作：普攻 Attack1 / Attack2 / Crit（双发）；Q 去而复还 Spell1 / Spell1_Catch；W 赴险夺人 Spell2_Intro / Spell2_Sneak_Walk；E 骄行荡寇 Akshan_Spell3 / Akshan_Spell3_Swing_shooting_0 / Akshan_Spell3_Roll；R 恩怨相抵 Channel / Akshan_Base_Spell4_Cast_Nomove / Spell4_hit / Spell4_lasthit；跑 Run；死亡 Death；复活 Respawn。
