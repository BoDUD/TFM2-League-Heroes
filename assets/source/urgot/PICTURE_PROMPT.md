# 厄加特（无畏战车）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 厄加特是一个**半人半机械的巨大战车**：上半身是一个**苍白、肌肉虬结的光头男人**，脸下半部戴着**深钢色的防毒面具**，几根**亮毒绿色的软管**从面具里垂下来插进胸口和背后；他的下半身装在一个**青铜色的圆桶形底盘**里，底盘下面是**六条机械蜘蛛腿**，每条腿上挂着一大块**青铜金色的盾形护甲**，护甲下面藏着一根**带孔的霰弹枪管**（膝炮）；他的一条手臂换成了**举在头顶的巨大霰弹炮臂**。请 Codex 画**两张全身像**（同一个厄加特，长相、颜色、格子大小都一样，只是姿势不同，我从中挑一张）：
> - **A**：英雄联盟里的待机（附图 1）。炮臂高高举在头顶、炮口朝前（画面右边）向下勾着；近侧那只人手搭在底盘前沿；六条腿稳稳撑地。
> - **B**：开枪的瞬间（附图 6）。炮臂压下来，炮口斜着朝前下方对准目标，上身往前倾，六条腿不动。
>
> 选定一张后，第 1 步再按它做游戏尺寸的造型。这一版每个游戏像素约 **1.8 格**，读回后再降到 PPU 1.5。附图 11–14 是本包里的蒙多、塔姆、杰斯、潘森，都是 1.2–1.5 的密度。你画的原图会按格子直接读回成游戏里的造型，所以**像素块要清楚、整齐、大小一致**。
> - **长相和结构照英雄联盟原版**（附图 1–7、9）。
> - **比例**：英雄联盟里他的头很小（在游戏尺寸下只剩两三个像素，看不清）。所以**把头和上半身放大**：头（光头 + 面具）约占从炮顶到腿尖总高的**七分之一，约 10 格高**，肩膀、胸口和那只人手跟着放大；底盘和六条腿保持英雄联盟的样子。不要画成大头娃娃，头也不能小到看不出脸。
> - **头和脸**（附图 3 特写）：
>   - **光头**，灰白的皮肤，头顶有几道缝合的疤；眉骨很重，**深陷的眼睛带一点红色的光**（眼睛的红只用在眼睛上）。
>   - 鼻子以下是**深钢色的防毒面具**（暗青灰金属，几道横纹），面具一侧伸出 **3–4 根亮毒绿色的粗软管**，弯下来插进胸口。
>   - 脖子周围一圈**很高的深石板蓝色硬领**，头后面竖着一块**弯弯的青铜盾板**，盾板里面是**暗红色**的。
> - **上半身**（附图 1、2、4）：**苍白、灰白带一点青色**的皮肤，肌肉夸张（大胸肌、粗壮的上臂），身上有几道**深色的缝线和纹路**；近侧那只人手又粗又大，搭在底盘前沿。背后有一个**深褐色的卷轴 / 弹簧鼓**（附图 1 里底盘左上方那个圆筒）。
> - **炮臂**（附图 1、6）：从远侧肩膀长出来的**巨型霰弹炮**，枪管是**深铁灰色的方块金属**，接口处有**青铜金色的夹箍**，肘部有一个**带金色尖刺的齿轮环**，炮口是方形的，下面伸出一块短短的「下颚」，侧面一个**小红灯**。
> - **底盘**：**青铜 / 黄铜色的圆桶形底盘**，边缘有亮金色的滚边和铆钉，前面几块深铁灰色的护板；底盘正面两个圆形的铜盖。
> - **六条腿**（附图 9 特写）：每条腿的大腿上挂着一大块**青铜金色的盾形护甲**（下端是尖的，金色描边，上面两道深色的槽），盾下面是**深铁灰色带小孔的霰弹枪管**，腿的关节是深铁灰色，腿尖是**深钢色的尖爪**；**毒绿色的软管**从底盘绕到每条腿上。近侧三条腿在画面前面、亮；远侧三条在后面、暗一档。
> - **姿势**：3/4 正面朝右（脸朝右前方）。近侧（画面左边）的腿和人手颜色亮，远侧的稍暗；**六个腿尖落在同一条地面线附近**（远侧的腿尖可以略高一点，但不能低于地面线）。
> - **画布用正方形 1536×1536**：**从炮臂的最高点到腿尖约 792 px，也就是约 72 格**，腿尖在离画布底边约 136 px 的地方（附图 8a、8b 的灰线）。他横着比竖着宽，左右要留够边，炮口、腿尖全在画面里。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。青铜金、深铁灰、苍白皮肤、毒绿软管、暗红盾板里面要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。铜甲的上沿和铁管的边缘要有亮的高光，免得在深色背景上糊成一团。
> - 不画任何特效（子弹、枪口火光、毒气、绿色的光都放到第 3 步单独画；软管本身是亮绿色的，照画）；不画地面，不画影子，不画别的角色。
> - 交付：`outputs/urgot-picture/urgot-A.png`、`urgot-B.png`（都是 1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/urgot-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/urgot_picture_done.zip`。

## 附图（在压缩包 `urgot_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_urgot_idle.png` | 英雄联盟原版厄加特的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_urgot_frontal.png` | 同一帧，正面 | 底盘、六条腿怎么排、软管 |
| `refs/3_urgot_head.png` | 头部特写 | 光头、红眼、防毒面具、绿软管、高领、背后的盾板 |
| `refs/4_urgot_back.png` | 同一帧的背后 | 背后的卷轴鼓、炮臂怎么从肩膀长出来 |
| `refs/5_urgot_splash.png` | 官方加载画面 | 气质（阴沉、凶狠、毒绿） |
| `refs/6_urgot_shot.png` | 开枪的瞬间，3/4 朝右 | B 的姿势 |
| `refs/7_urgot_shot_side.png` | 同一帧，接近侧面 | B 里炮臂压下来的角度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小；头在这里还是原版的小头） | 画布上他的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（同一比例） | 画布上他的位置、大小、地面线（灰） |
| `refs/9_urgot_legs.png` | 底盘和腿的特写 | 铜盾护甲、带孔的膝炮、尖爪、软管 |
| `style/11_style_drmundo.png` | 本包的蒙多（壮汉），8 倍放大，一格 = 一个像素 | **只看风格**：苍白肌肉、粗手臂怎么分档 |
| `style/12_style_tahmkench.png` | 本包的塔姆（大块头，8 倍） | **只看风格**：大块头的头身比、描边 |
| `style/13_style_jayce.png` | 本包的杰斯（8 倍） | **只看风格**：金属和金色装饰怎么分档 |
| `style/14_style_pantheon.png` | 本包的潘森（8 倍） | **只看风格**：青铜盔甲；这个密度下格子有多细 |

## 提示词：`urgot-A.png` / `urgot-B.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-7 and 9 are 3D renders and art of a character from the game: a HUGE HALF-MAN HALF-MACHINE WALKER - the upper body of a PALE, heavily MUSCLED BALD MAN with a dark steel GAS MASK over his mouth and jaw and bright TOXIC-GREEN HOSES running from the mask into his chest; his lower body sits in a BRONZE barrel-shaped CHASSIS carried on SIX MECHANICAL SPIDER LEGS, each leg wearing a big bronze-gold shield-shaped armour plate over a perforated dark steel SHOTGUN BARREL; one of his arms is a GIANT SHOTGUN CANNON held over his head (1 his idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: the chassis, how the six legs spread, the hoses; 3 the head close-up: the bald head, the red-lit deep-set eyes, the gas mask, the green hoses, the high collar, the curved bronze plate behind his head with its dark red inside; 4 the same from behind: the coiled drum on his back, how the cannon arm grows from his shoulder; 5 the official illustration: his mood, grim and brutal, toxic green; 6 the instant he fires - pose B; 7 the same from nearer the side: the angle of the lowered cannon; 9 a close-up of the chassis and legs: the bronze shield plates, the perforated knee barrels, the pointed steel claws, the hoses). Images 8a and 8b are layout guides of A and B: where he goes on the canvas and how big, the grey line is the ground (their head is still League's tiny head - make it bigger as written below). Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, how pale muscles and thick arms are shaded (11), how a big creature is proportioned (12), how metal and gold trim are split into clear shades (13, 14). Image 14 shows the square density this picture needs.
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). He is about 792 px (about 72 squares) from the highest point of the cannon arm to the tips of his legs, the leg tips about 136 px above the bottom edge (the grey line of images 8a / 8b); he is wider than tall - the cannon muzzle and every leg tip whole inside the picture, comfortable transparent margins, nothing cut off; the leg tips on or just above one ground line, none below it.
PROPORTIONS: in the game his head is tiny; here the HEAD AND UPPER BODY ARE ENLARGED - the head (bald head + mask) about one seventh of the total height, about 10 squares tall, the shoulders, chest and the human arm enlarged with it; the chassis and the six legs as in images 1, 2 and 9. Not a big-headed doll, but a face that reads clearly.
THE HEAD: BALD, grey-white skin with a few stitched scars on the scalp; a heavy brow, DEEP-SET EYES with a faint RED glow (the red used ONLY in the eyes); below the nose a DARK STEEL GAS MASK (dark teal-grey metal with a few ridges), 3-4 thick BRIGHT TOXIC-GREEN HOSES coming out of one side of the mask and curving down into the chest; a very HIGH DARK SLATE-BLUE COLLAR round the neck; behind the head a tall CURVED BRONZE PLATE, DARK RED on its inside.
THE UPPER BODY: PALE grey-white skin with a faint cold tint, exaggerated muscles (a big chest, thick upper arms), a few dark stitch lines and markings on the skin; the NEAR arm a huge human arm resting its hand on the front edge of the chassis; on his back a DARK BROWN COILED DRUM (the cylinder above the chassis on the image left in image 1).
THE CANNON ARM (images 1, 6): his FAR arm is a GIANT SHOTGUN CANNON growing from the far shoulder: a blocky DARK IRON-GREY barrel with BRONZE-GOLD clamps, a TOOTHED RING WITH GOLD SPIKES at the elbow, a squared muzzle with a short downward jaw under it and a small RED light on its side.
THE CHASSIS: a BRONZE / BRASS BARREL-SHAPED HULL with bright gold trim and rivets, a few dark iron-grey plates on its front, two round copper caps on its front.
THE SIX LEGS (image 9): on each upper leg a big BRONZE-GOLD SHIELD-SHAPED ARMOUR PLATE (pointed at the bottom, gold rim, two dark slots), under it a DARK IRON-GREY PERFORATED SHOTGUN BARREL, dark iron-grey joints, DARK STEEL POINTED CLAWS at the tips; TOXIC-GREEN HOSES looping from the chassis to every leg. The three NEAR legs in front in full tone, the three FAR legs behind a step darker.
THE VIEW: 3/4 view facing right (the face to the front-right): the NEAR legs and the human arm on the image LEFT in full tone, the FAR ones a step darker; the leg tips level on one ground line (the far ones may sit a little higher, never lower).
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the bronze-gold armour, the dark iron-grey metal, the pale skin, the toxic-green hoses, the dark red inside the head plate clearly separated; bright highlights on the top edges of the bronze plates and on the edges of the iron barrels so the shapes read on a dark background; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no bullets, no muzzle flash, no gas, no green glow around him - the hoses themselves are bright green), no background, no ground, no shadow, no text, no frame, no other characters.
POSE A (urgot-A.png): his idle (image 1) - the cannon arm raised high over his head, the muzzle pointing forward (image right) and hooking down, the near human hand resting on the front edge of the chassis, the six legs planted.
POSE B (urgot-B.png): the instant he fires (image 6) - the cannon arm swung down, the muzzle aimed forward and down at the target, the upper body leaning forward, the six legs planted as in A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，炮口和腿尖完整，不出画。
- 比例：**头和上半身放大**（头约占总高七分之一，约 10 格），脸看得清；底盘和六条腿照原版。
- 头：光头带缝疤、**深陷的红眼**（红色只用在眼睛上）、**深钢色防毒面具**、3–4 根**亮毒绿软管**、深石板蓝高领、头后的**青铜盾板（里面暗红）**。
- 上身：苍白肌肉、深色缝线；近侧人手搭在底盘前沿；背后深褐色卷轴鼓。
- 炮臂：深铁灰方块枪管、青铜金夹箍、**金色尖刺齿轮环**、方炮口带下颚和小红灯。
- 底盘：青铜圆桶、亮金滚边和铆钉。六条腿：**青铜金盾形护甲**、带孔的深铁灰膝炮、深钢尖爪、毒绿软管；近侧三条亮、远侧三条暗。
- A：炮臂高举在头顶，炮口朝前向下勾；B：炮臂压下，炮口朝前下方，上身前倾。
- 从炮臂最高点到腿尖约 792 px（约 72 格）；腿尖在同一条地面线附近，不低于它；没有任何特效。
- **每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/urgot-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/urgot_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/urgot/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_<hero>_hd.py` 的做法），和已合并的大块头上单（蒙多、赛恩、塔姆、德莱厄斯、潘森）按游戏里的大小并排，给用户挑 A / B；PPU 已定 1.5，再出 2–3 个大小的对比让用户定（**每个动作的显示高度**都要和德莱厄斯比，潘森的教训）。头的大小按 oppi 大块头的比例检查（赫卡里姆的教训）。
- 选定后第 1 步按游戏格子重画（潘森 / 厄斐琉斯的做法），再做动作帧：炮臂、六条腿的铜甲是刚体部件，只平移和整块转直角，不变形；跑步照 Urgot_RunSlow_Fwd（六条腿两组交替）；普攻 Urgot_Attack1_InCombat_Fwd（炮臂压下开火）；Q Urgot_Spell1_Fwd；W 机枪 Urgot_channel；E Urgot_spell3 / Spell3_GrabThrow_Fwd；R Urgot_Spell4_Fwd（上身升起、钻头发射器）；死亡 Urgot_death。腿上的霰弹（被动）和枪口火光画进他自己的帧（红色方规则）。
