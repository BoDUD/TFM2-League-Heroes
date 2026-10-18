# 吉格斯（爆破鬼才）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 吉格斯是**约德尔人（矮小的毛茸茸小个子）爆破专家**：大脑袋、**长长的尖耳朵**向两边伸出，**咧到耳根的大白牙笑容**，**浓密的米黄色络腮胡和鬓毛**（毛茸茸一圈）。头上一顶**圆形头盔，蓝色和红色的条纹**，前面推上去一副**大大的绿色护目镜**（两个圆镜片，红色的镜框）——**这两个绿色镜片就是他的"眼睛"**。身上**红色的短外套（红袖子）**，外面套**牛仔蓝的背带裤**，**橙色的手套**，**蓝钢色的护膝和护腿**，**又大又圆的灰钢色靴子**；背后背着一个**红色的炸药包**。两只手各拿一颗**红色的圆炸弹**，炸弹上有**白色骷髅头标记**，顶上一根**冒着火星的引线**。请 Codex 画**两张全身像**（同一个吉格斯，长相、颜色、**格子大小**都一样），用户从里面挑一张做游戏里的待机：
> - **A：英雄联盟里的待机**（附图 1、8a）。两脚分得很开、膝盖微弯，**两只手向两边伸开，各托着一颗炸弹**，咧嘴大笑，有点调皮地弓着身子。
> - **B：收拢的备战姿势**（附图 8b 只看大小和地面线）。站姿稍窄、膝盖微弯，**两只手肘收在身边，两颗炸弹捧在肚子前面**（近侧手的炸弹稍高、远侧的稍低），这样整个人横向窄一些。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型（PPU 1.5）。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的库奇（同是约德尔人，PPU 2.2）、崔丝塔娜（约德尔人，原尺寸）和嘉文四世（PPU 1.5，和吉格斯一样），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6、7）。
> - **比例**：约德尔人，**头（连头盔、护目镜、耳朵和胡子）约占身高的五分之二**（约 27 格），身子短、腿短、手脚大；不要细长的写实比例。
> - **头**（附图 3 特写）：蓝红条纹的圆头盔（每种颜色分几档，有亮边）；**两个绿色圆镜片一样大、一样高**，红色镜框，镜片上有一个亮白的高光点；两只长尖耳朵向两边伸出，耳朵里面颜色稍粉；**大大的笑容露出一排白牙**（牙齿要能看清，用白和浅灰两档，不要一片白）；米黄色的毛胡子围着脸，有几档颜色，边上毛茸茸的锯齿。
> - **衣服**：红外套和红袖子，牛仔蓝背带裤（前面一块护胸），橙色手套，蓝钢护膝护腿，灰钢大靴子；背后露出一点红色炸药包。
> - **炸弹**：红色圆炸弹，**白色骷髅头**标记清楚，顶上一小截深色引线和**黄橙色的火星**；炸弹要圆、要完整，大约是他头的一半大。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**。两只鞋底落在同一条地面线上。
> - **画布用正方形 1536×1536**。**从头盔顶到鞋底约 748 px，也就是约 68 格**（引线火星不算），鞋底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。耳朵、炸弹、引线全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。头盔的蓝和红、绿镜片、白牙、米黄胡子、红外套、牛仔蓝裤子、橙手套、蓝钢护腿、灰钢靴子、红炸弹要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。**牛仔蓝和蓝钢很暗，一定要有偏亮的边**，不然在深色背景上会糊成一团。
> - 不画任何特效（爆炸、炸药包爆破、雷区、大炸弹都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/ziggs-picture/ziggs-A.png`、`ziggs-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/ziggs-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/ziggs_picture_done.zip`。

## 附图（在压缩包 `ziggs_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_ziggs_idle.png` | 英雄联盟原版吉格斯的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势和拿炸弹的方法 |
| `refs/2_ziggs_frontal.png` | 同一帧，正面 | 背带裤、护胸、护膝怎么排，左右对称的样子 |
| `refs/3_ziggs_head.png` | 头部特写 | 条纹头盔、绿色护目镜、尖耳朵、白牙、胡子 |
| `refs/4_ziggs_back.png` | 同一帧的背后 | 背后的红色炸药包、头盔后面 |
| `refs/5_ziggs_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_ziggs_throw.png` | 普攻扔炸弹的一帧 | 炸弹、引线的样子，扔的时候身体怎么拧 |
| `refs/7_ziggs_side.png` | 同一帧，接近侧面 | 头盔、耳朵、炸药包从侧面看的厚度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 他的大小、地面线（灰）；**姿势按文字：手肘收拢，炸弹捧在肚子前** |
| `style/11_style_corki.png` | 本包的库奇，8 倍放大，一格 = 一个像素 | **只看风格**：约德尔人的脸、胡子、护目镜在格子上怎么画 |
| `style/12_style_tristana.png` | 本包的崔丝塔娜（8 倍，原尺寸） | **只看风格**：约德尔人的耳朵、矮小的身子 |
| `style/13_style_jarvaniv.png` | 本包的嘉文四世（8 倍，PPU 1.5，和吉格斯一样） | **只看风格**：格子密度、描边、每种材质分几档 |

## 提示词：`ziggs-A.png` / `ziggs-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a YORDLE (a small furry humanoid) BOMB EXPERT - a big head with LONG POINTED EARS sticking out to the sides, a HUGE TOOTHY GRIN, a BUSHY BLOND-TAN BEARD and mutton chops framing the face; a ROUND HELMET with BLUE AND RED STRIPES and BIG GREEN GOGGLES (two round green lenses in red rims) on its front - the two green lenses are his "eyes"; a RED JACKET with red sleeves under DENIM-BLUE OVERALLS (a bib in front), ORANGE GLOVES, BLUE-STEEL knee and shin guards, BIG ROUND GREY-STEEL BOOTS; a RED BOMB SATCHEL on his back; in EACH HAND a ROUND RED BOMB with a WHITE SKULL mark and a short dark fuse with a yellow-orange spark on top (1 his idle, 3/4 view facing right - the look, the ANGLE, pose A and how he holds the bombs; 2 the same from the front: the overalls, the bib, the knee guards; 3 the head close-up: the striped helmet, the goggles, the ears, the teeth, the beard; 4 the same from behind: the red satchel, the helmet's back; 5 the official illustration: his mood and colours; 6 one of his throws: the bomb, the fuse, how he twists; 7 the idle nearly from the side: the depth of the helmet, the ears and the satchel). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a yordle face with goggles and a moustache on the grid (11), yordle ears and a small body (12), the square density, the outline and the number of shades a material gets (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the ears, both bombs and their fuses whole); both soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 748 px (about 68 squares) from the top of his helmet to his soles - the fuse sparks not counted.
PROPORTIONS: a yordle - the head with the helmet, goggles, ears and beard about TWO FIFTHS of his height (about 27 squares); a short body, short legs, big hands and big boots; NOT realistic slim proportions.
THE HEAD: the round helmet with blue and red stripes, each colour in a few shades with a light edge; TWO GREEN GOGGLE LENSES of the SAME size at the SAME height in red rims, each with one bright white highlight square; two long pointed ears out to the sides, a little pink inside; a BIG GRIN with a row of WHITE TEETH clearly readable (white and light grey, not one white blob); the blond-tan beard round the face in a few shades with a furry jagged edge.
THE CLOTHES: the red jacket and sleeves, the denim-blue overalls with a bib, orange gloves, blue-steel knee and shin guards, big grey-steel boots; a little of the red satchel showing behind him.
THE BOMBS: round red bombs, the WHITE SKULL mark clear, a short dark fuse with a yellow-orange spark on top; each bomb round and whole, about half the size of his head.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the denim-blue overalls and the blue-steel guards with LIGHTER EDGES so they never turn into one dark mass, the helmet's blue and red, the green lenses, the white teeth, the blond beard, the red jacket, the orange gloves, the grey boots and the red bombs clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no explosion, no blast, no mines, no glow), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (ziggs-A.png): his idle (images 1 and 8a) - feet wide apart, knees slightly bent, hunched a little like a mischievous imp, BOTH ARMS HELD OUT TO THE SIDES, a bomb resting in each hand; the face to the front-right, grinning.
POSE B (ziggs-B.png): a NARROWER READY STANCE - the SAME yordle with the SAME 11-px squares: feet a little apart, knees slightly bent, ELBOWS IN at his sides, BOTH BOMBS HELD IN FRONT OF HIS BELLY (the near hand's bomb a little higher, the far one a little lower), so he is narrower than in A; the face to the front-right, grinning (image 8b shows only his size and the ground line).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，耳朵、两颗炸弹、引线完整，不出画。
- 比例：约德尔人，头（连头盔、护目镜、耳朵、胡子）约占身高五分之二（约 27 格）；身子短、腿短、手脚大。
- 头：蓝红条纹圆头盔分几档颜色；**两个绿色镜片一样大、一样高**，红框、白高光；长尖耳朵向两边；咧嘴露出一排白牙；米黄色毛胡子分几档。
- 衣服：红外套红袖子、牛仔蓝背带裤带护胸、橙手套、蓝钢护膝护腿、灰钢大靴子，背后露一点红炸药包。
- 炸弹：红色圆炸弹、白色骷髅头、顶上引线和黄橙色火星，大约头的一半大。
- A：两脚分开、两手向两边伸开托着炸弹；B：手肘收拢、炸弹捧在肚子前，比 A 窄。从头盔顶到鞋底约 748 px（约 68 格），鞋底都在同一条地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/ziggs-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ziggs_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/ziggs/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_jarvaniv_hd.py` / `design_nasus_hd.py` 的做法，绝不按更少的行采样），和已合并的约德尔人（库奇、小鱼人、崔丝塔娜、提莫、璐璐、维迦）按游戏里的大小并排，给用户挑 A / B 和定大小；PPU 1.5（用户选的），游戏里约 32–34 个游戏像素高。
- 定下后第 1 步按游戏格子重画，再自己做动作帧（嘉文 / 内瑟斯的方式，无损：只平移、整块直角转、整行移；**炸弹是刚体，每帧都用设计里的同一颗**）；走路：两腿用设计里自己的整条腿（不用 Codex 画的腿）。英雄联盟的动作：普攻 Ziggs_Attack1 / Attack2 / Crit（扔炸弹）；Q 弹跳炸弹 Ziggs_Spell1；W 定点爆破 Ziggs_Spell2；E 海克斯爆破雷区 Ziggs_Spell3；R 科学的地狱火炮 Ziggs_Spell4（跳起来抛出大炸弹）；跑 Ziggs_Run；死亡 Ziggs_Death。
