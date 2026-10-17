# 芸阿娜（不破之誓）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 芸阿娜是一个**清瘦、沉静的艾欧尼亚女武者**。她的头发是**淡紫色**，编成两条长辫垂在胸前，头顶两侧各有一个**金色、像弯角一样的发饰**；眼睛半闭，神情平静，额头正中有一个小小的**银色额饰**。上身穿**深藏青色的长袖短上衣**，露出腰；前臂戴**金色护腕**，手是**蓝色的露指手套**。下身是**很宽的淡紫色薄纱长裤**（站着时像一条长裙），腰上一块**深紫色的围布**，镶着一排铜扣，旁边有一条金边；脚上是**深紫色的绑腿**和**木头的厚底凉鞋**。她身边漂浮着**八颗铜色的念珠**（圆球，上面有凸起的圆钉）和**一颗紫色水晶的龙头珠**（龙头后面拖着两三道紫色的长光尾）。请 Codex 画**三张图**：两张全身像（同一个芸阿娜，长相、衣服、颜色、格子大小都一样，只是姿势不同，我从中挑一张），再加一张念珠表。
> - **A**：英雄联盟里的待机（附图 1）。她站得笔直，两只手在身前，一高一低像在托着什么；念珠漂在她身边，龙头珠在她近侧的手下面。
> - **B**：普攻掌击的那一瞬间（附图 6）。两条手臂向两边张开，远侧的手掌朝前推出，身体微微下蹲；念珠在她头顶排成一道弧线，龙头珠冲在弧线最前面。
> - **W**：念珠表（附图 8c、9、10）。不画人，八颗铜念珠和龙头珠彼此分开，和 A 同一个比例、同一个格子大小，以后按它把念珠画进动作里。
>
> 选定一张后，第 1 步再按它做游戏尺寸的造型。这一版每个游戏像素约 **1.8 格**，读回后再降到 PPU 1.5。附图 11–14 是本包里的卡特琳娜、卡莉丝塔、尼菈（同样是武者）、厄斐琉斯，都是 1.4–1.5 的密度。你画的原图会按格子直接读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：清瘦修长的女性，**头稍大一点**（约占身高的五分之一），肩窄、腰细、腿长；不要画成大头娃娃，也不要壮硕。
> - **头和脸**（附图 3 特写）：
>   - **淡紫色头发**（亮淡紫到深紫三四档），前额分开，两侧垂下，**两条粗辫子**垂到胸前，辫子末端有**金色的环扣和紫色的穗子**。
>   - 头顶两侧各一个**金色的弯角发饰**（像两只往外弯的金角，根部有一点棕红色），从头发后面向上翘起。
>   - **白皙的皮肤**，**半闭的眼睛**（眼皮下垂，睫毛深色），眼睛的颜色是**淡紫偏蓝**，只用在眼睛上；额头正中一个小小的**银色额饰**；嘴唇淡粉。
> - **衣服**（附图 1、2、4）：
>   - **深藏青色的长袖短上衣**，立领，胸前一枚**金色的圆形领扣**；肩头和袖子有更深一档的藏青色和一点紫色的高光；露出一截**腰腹**。
>   - 前臂戴**金色的宽护腕**，手是**蓝色的露指手套**。
>   - 腰上一条**金色的腰带**，前面垂一块**深紫色的围布**，上面一排**铜色的圆扣**，围布侧面有一道**金色的宽边**，腰侧挂一个**铜色的螺旋形小饰物**。
>   - **很宽的淡紫色薄纱长裤**（淡紫、浅蓝紫、深一点的蓝紫三四档，下摆颜色偏蓝），站着时像一条落到脚踝的长裙。
>   - **深紫色的绑腿**，**木头的厚底凉鞋**（棕色木底，紫色鞋面）。
> - **念珠**（附图 1、6、9、10）：
>   - **八颗铜念珠**：圆球，铜金色（亮金、铜色、暗棕三四档），表面有几颗**凸起的圆钉**和一道弯弯的纹路；每颗大约和她的头一样大或小一点。
>   - **龙头珠**：一颗**紫色水晶的龙头**（亮淡紫、紫、深紫三四档，带白色高光），龙头后面拖着两三道**细长的紫色光尾**，像飘带。
>   - 念珠是**浮在空中的**，不用线串起来，彼此之间留出空隙。
> - **姿势**：3/4 正面朝右（脸朝右前方）。**近侧的手臂和腿在画面左边、颜色亮；远侧的在画面右边、稍暗**，两只脚底落在同一条地面线上。
> - **画布用正方形 1536×1536**：**从金色发饰的顶端到脚底约 792 px，也就是约 72 格**，脚底在离画布底边约 136 px 的地方（附图 8a、8b 的灰线）。念珠全在画面里，B 里头顶的念珠弧线也不能出画。念珠表 W 按附图 8c 的大小和位置摆。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。淡紫头发、金色发饰和护腕、深藏青上衣、深紫围布、淡紫纱裤、铜念珠、紫水晶龙头要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。深藏青的上衣边上要有亮一点的高光，免得在深色背景上看不清。
> - 不画任何特效（灵气、光弹、射线、旋转的光环都放到第 3 步单独画）；不画地面，不画影子。
> - 交付：`outputs/yunara-picture/yunara-A.png`、`yunara-B.png`、`yunara-W.png`（都是 1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/yunara-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/yunara_picture_done.zip`。

## 附图（在压缩包 `yunara_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_yunara_idle.png` | 英雄联盟原版芸阿娜的待机，3/4 朝右，念珠在身边 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_yunara_frontal.png` | 同一帧，正面（不带念珠） | 上衣、领扣、护腕、腰带、围布、纱裤、凉鞋 |
| `refs/3_yunara_head.png` | 头部特写 | 头发、辫子、金色弯角发饰、半闭的眼睛、额饰 |
| `refs/4_yunara_back.png` | 同一帧的背后 | 头发和发饰的背面、上衣背面 |
| `refs/5_yunara_splash.png` | 官方加载画面 | 气质（沉静、有力）、脸、颜色 |
| `refs/6_yunara_attack.png` | 普攻掌击的瞬间，3/4 朝右 | B 的姿势、头顶的念珠弧线 |
| `refs/7_yunara_attack_side.png` | 同一帧，接近侧面 | B 里两条手臂怎么张开、腿怎么站 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上她的位置、大小、脚底线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（同一比例） | 画布上她的位置、大小、脚底线（灰） |
| `refs/8c_layout_W.png` | 念珠表的布局示意（和 A 同一比例） | 念珠有多大 |
| `refs/9_yunara_beads.png` | 只有念珠和龙头珠（待机时的位置） | 念珠的形状、颜色 |
| `refs/10_yunara_dragon_bead.png` | 龙头珠和它的光尾特写 | 龙头珠的形状 |
| `style/11_style_katarina.png` | 本包的卡特琳娜，8 倍放大，一格 = 一个像素 | **只看风格**：像素粗细、描边、清瘦的身材、脸和头发 |
| `style/12_style_kalista.png` | 本包的卡莉丝塔（8 倍） | **只看风格**：冷色调怎么分档 |
| `style/13_style_nilah.png` | 本包的尼菈（8 倍），同样是武者 | **只看风格**：长发、宽裤、饰物怎么画 |
| `style/14_style_aphelios.png` | 本包的厄斐琉斯（8 倍） | **只看风格**：这个密度下格子有多细 |

## 提示词：`yunara-A.png` / `yunara-B.png` / `yunara-W.png`（同一段提示词，只换最后一句）

十六张图都附上，顺序同上表。

```text
Sixteen attached images. Images 1-7 are 3D renders and art of a character from the game: a SLIM, CALM YOUNG FEMALE MARTIAL ARTIST from an East-Asian-inspired land, with LILAC HAIR in two long braids, two GOLDEN HORN-LIKE HAIR ORNAMENTS, a DARK NAVY long-sleeved cropped top, golden bracers, WIDE LAVENDER GAUZE TROUSERS and wooden platform sandals, with BRONZE PRAYER BEADS and a VIOLET CRYSTAL DRAGON-HEAD BEAD floating around her (1 her idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front, without the beads: the top, the round golden collar clasp, the bracers, the belt, the dark purple front panel with its bronze studs, the trousers, the sandals; 3 the head close-up: the hair, the braids, the golden horn ornaments, the half-closed eyes, the small silver forehead jewel; 4 the same from behind; 5 the official illustration: her mood, calm and strong, and her face; 6 the instant of her palm strike - pose B, the beads in an arc over her head; 7 the same from nearer the side: how her arms spread and how she stands). Images 8a, 8b and 8c are layout guides of A, B and the bead sheet W: where things go on the canvas and how big, the grey line is the ground. Image 9 shows the beads alone where they float in her idle; image 10 is a close-up of the crystal dragon-head bead and its streamers. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how a slim face and long hair are drawn (11, 13), how wide trousers and ornaments are drawn (13). Image 14 shows the square density this picture needs.
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). In the full-body pictures she is about 792 px (about 72 squares) from the top of her golden hair ornaments to the soles of her feet, the soles about 136 px above the bottom edge (the grey line of images 8a / 8b); every bead whole inside the picture (the arc of beads over her head in pose B too), comfortable transparent margins, nothing cut off; both soles level on one ground line.
PROPORTIONS: a slim woman with a slightly big head - the head about a fifth of her height - narrow shoulders, a slim waist, long legs; not a big-headed doll, not a bulky build.
THE HEAD: LILAC HAIR (bright pale lilac to deep violet in 3-4 shades) parted at the forehead, falling at the sides, TWO THICK BRAIDS hanging over her chest, each ending in a golden ring and a purple tassel; TWO GOLDEN HORN-LIKE ORNAMENTS rising from the back of her head on both sides, curving outward, a touch of red-brown at their roots; FAIR skin; HALF-CLOSED calm eyes with dark lashes, the eye colour pale violet-blue used ONLY in the eyes; a small SILVER JEWEL in the middle of the forehead; pale pink lips.
THE CLOTHES: a DARK NAVY LONG-SLEEVED CROPPED TOP with a standing collar and a ROUND GOLDEN CLASP on the chest, the shoulders and sleeves shaded a step darker with a touch of violet highlight, the midriff bare; WIDE GOLDEN BRACERS on the forearms, BLUE FINGERLESS GLOVES; a GOLDEN BELT with a DARK PURPLE FRONT PANEL hanging from it, a row of round BRONZE STUDS across the panel and a wide golden edge on its side, a small bronze spiral ornament at the hip; VERY WIDE LAVENDER GAUZE TROUSERS (pale lavender, light blue-violet and a deeper blue-violet, bluer at the hem) that look like a long skirt down to the ankles when she stands; DARK PURPLE leg wraps, WOODEN PLATFORM SANDALS (brown wooden soles, purple straps).
THE BEADS: EIGHT BRONZE PRAYER BEADS - round balls of bronze-gold (bright gold, bronze, dark brown in 3-4 shades) with a few raised round studs and a curved groove, each about the size of her head or a little smaller; ONE VIOLET CRYSTAL DRAGON-HEAD BEAD (bright pale violet, violet, deep violet with white highlights) trailing two or three long thin violet streamers. The beads FLOAT freely in the air, no string, with gaps between them.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR arm and leg on the image LEFT in full tone, the FAR ones on the image RIGHT a step darker; both soles on one ground line.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure and every bead; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the hair lilac, the ornaments, bracers and belt gold, the top dark navy with lighter edges so it reads on a dark background, the front panel dark purple, the trousers lavender, the skin fair, the beads bronze, the dragon bead violet crystal; light and dark parts clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no aura, no energy blasts, no beams, no glowing rings), no background, no ground, no shadow, no text, no frame, no other characters.
POSE A (yunara-A.png): her idle (image 1) - standing upright and calm, both hands held in front of her body at different heights as if cradling something, the beads floating around her, the dragon-head bead below her near hand.
POSE B (yunara-B.png): the instant of her palm strike (image 6) - both arms spread wide, the far palm pushed forward (image right), the body slightly lowered with the knees bent, the eight beads in an arc over her head with the dragon-head bead leading at the front of the arc.
SHEET W (yunara-W.png): no character - the eight bronze beads and the dragon-head bead apart, each at the scale it has in A (the same 11 px squares), laid out in two rows like image 8c: the eight beads on the top row (they may differ slightly in the angle of their studs and groove), the dragon-head bead with its streamers below; every bead whole, at least 3 squares of transparent space between them.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，念珠和发饰完整，不出画。
- 比例：清瘦修长，头稍大（约占身高五分之一），不是大头娃娃。
- 头：淡紫色头发、**两条粗辫子**垂在胸前、**两个金色弯角发饰**；白皙皮肤、**半闭的眼睛**、额头银色额饰；眼睛的颜色只用在眼睛上。
- 衣服：深藏青长袖短上衣（立领、金色圆领扣、露腰）、金色护腕、蓝色露指手套、金腰带、深紫围布带铜扣、**很宽的淡紫纱裤**、深紫绑腿、木头厚底凉鞋。
- 念珠：八颗铜念珠（带凸钉）、一颗紫水晶龙头珠（带光尾），都浮在空中，不用线串。
- A：站直，两手在身前一高一低，念珠在身边；B：两臂张开、远侧手掌推出、微蹲，念珠在头顶排成弧线、龙头珠在最前；W：八颗念珠一排，龙头珠在下面，和 A 同一个比例。
- 从发饰顶端到脚底约 792 px（约 72 格）；近侧手脚在画面左边、颜色亮，远侧在右边、稍暗；脚底在同一条水平线上；没有任何特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- A、B、W 三张都画完后，最后写 `outputs/yunara-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/yunara_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，三张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/yunara/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_<hero>_hd.py` 的做法），和同位置英雄（卡莉丝塔、厄斐琉斯、金克丝、卡莎、泽丽）按游戏里的大小并排，给用户挑 A / B；PPU 已定 1.5，再出 2–3 个大小（约 38 / 40 / 42 行）的对比让用户定。念珠表 W 按 A 的格子读回，每颗念珠单独存一张。
- 第 1 步除了造型，还要一张**超凡形态**的版本（同一个造型，头发和衣服边缘泛金白色的光、身后一圈淡金的光环），给附加包 R 期间换待机 / 跑步用。
- 选定后写第 2 步动作包：念珠是刚体部件，动作里只平移，不变形；跑步照英雄联盟（run）；普攻（attack1 / attack2，掌击、念珠飞出）；Q 开启（Spell1 的强化普攻 Spell1_Attack1）；W 念珠（Spell2）；R 射线（Spell4_W）；R 冲刺（Spell4_E）；R 开启（Spell4_Nomove）；死亡（Death）。
