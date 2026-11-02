# 峡谷先锋（金铲铲之战 · 第 16 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 峡谷先锋是金铲铲之战第 16 赛季的四费卡（虚空 / 斗士），技能「扭曲护甲」：**一只弓着背的虚空巨兽，背上扣着一个巨大的晶体甲壳**。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **甲壳**（附图 1、3、7）：一个**很大的圆顶甲壳**，从头顶一直盖到背上，由一块块**带棱面的蓝紫色晶体甲片**拼成（亮面偏青蓝，暗面深靛紫，3–4 档），**每块甲片中间嵌着一个发光的洋红色菱形小斑**，像一排排小眼睛；甲壳前沿有一圈**金色的小尖刺**。
> - **身体**：**深紫黑色（茄子色）**的粗壮身体，弓着背，**两条短粗的后腿**站着，后面拖着一条**细长、往上卷的尾巴**。
> - **爪子**（附图 1、2、7）：**两条很粗的前臂**，末端是**大大的蟹钳一样的爪子**（深紫色的甲片，爪尖和边缘是金色），垂在身体前面；前臂后面还有**两条小一点的后臂**。
> - **头和脸**（附图 3、6 特写）：脸很小，藏在甲壳前沿下面；**两只发光的洋红色眼睛**，一排**金色小尖牙**；脸两边各长着一根**又大又弯的金色獠牙 / 角**（往上弯，很显眼）；脸正上方还有**一根金色的小尖角**。
> - **背后**（附图 5）：甲壳后面正中有一只**竖着的粉红色裂眼**（这是它最有名的特征，3/4 角度下可以在背上露出一点）。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：待机**（金铲铲原样待机，附图 1、2、10a）：**3/4 朝右**，弓着背缩在甲壳下面，两只大钳爪垂在身前，尾巴在身后往上卷。
> - **B：直立长啸**（它放大招「扭曲护甲」时用后腿站起来的那一下，附图 4、10b）：**3/4 朝右**，用两条后腿**直立起来**，两只大钳爪**张开举在身前**，头往上仰，金色獠牙朝上；甲壳在背后，尾巴在脚边卷着。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的暗影狼、绯红印记树怪（都是本系列的峡谷野怪，**最接近的参考**）、科加斯和雷克塞（虚空生物：甲壳、尖刺、紫色怎么画），**只看风格**。
> - **长相照金铲铲的模型**（附图 1、2、4、5、7 是模型的渲染；附图 3、6 是头部特写，**脸、洋红眼睛、金色獠牙以附图 3、6 为准**；附图 7 是侧面，看清**甲壳有多高、尾巴多长**；附图 8 是它冲锋时翻过身用甲壳往前撞，附图 9 是它转圈横扫，**这两张只看动作**）。
> - **比例**：Q 版、敦实的大块头，**甲壳是最显眼的地方**；**头可以比模型大一些**（模型的脸太小，看不清），但仍然藏在甲壳前沿下面；**钳爪要大**；**脸（洋红眼睛 + 两根金獠牙）一定要清楚**，是全图最好认的地方。
> - **脸要清楚**（附图 3、6 特写）：脸 3 档蓝紫色，边缘一圈深色；**两只眼睛**各至少 2×2 格的洋红色（近处那只 3×2），中间一格最亮（发光就用更亮的一档平涂，不要柔光）；**两根金獠牙**各至少 2 格粗、5–7 格长，3 档金色（亮金 / 金 / 暗金）。
> - **画布用正方形 1536×1536**。**A：从最高点（甲壳顶 / 獠牙尖）到脚底约 460 px，也就是约 42 格**，宽约 43–50 格（最多 56 格，算上尾巴和钳爪）；**B：同样的身体大小**，因为站起来了所以更高：从最高点到脚底约 670 px，也就是约 61 格，宽约 44–50 格。脚底在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。甲壳、钳爪、獠牙、尾巴全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。**甲壳**画成一块块棱面甲片（亮面朝左上，甲片之间一道深色缝），每块中间一个洋红小菱形；**身体**是成块的 3 档深紫；**金色**部分（獠牙、尖刺、爪尖）是成条的 3 档金色，不要碎点。
> - 不画任何技能特效（冲击波、紫色虚空光、裂地、尘土、光圈都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/riftherald-picture/riftherald-A.png`、`riftherald-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/riftherald-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/riftherald_picture_done.zip`。

## 附图（在压缩包 `riftherald_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_herald_34.png` | 金铲铲峡谷先锋的模型，待机，3/4 朝右 | **A** 的姿势、颜色、**角度** |
| `refs/2_herald_front.png` | 模型，待机，正面 | 两只钳爪、甲壳前沿下的脸、两根獠牙 |
| `refs/3_herald_head.png` | 头部特写（3/4） | **脸、洋红眼睛、金獠牙、甲壳前沿的金刺** |
| `refs/4_herald_rear.png` | 模型，后腿直立、钳爪举起，3/4 朝右 | **B** 的姿势 |
| `refs/5_herald_back.png` | 背后 | 甲壳后面的**粉红竖眼** |
| `refs/6_herald_head_front.png` | 头部特写（正面） | **脸**：两只眼睛、两根獠牙、头顶的小角怎么排 |
| `refs/7_herald_side.png` | 侧面 | 甲壳有多高、尾巴多长 |
| `refs/8_herald_charge.png` | 冲锋（翻过身用甲壳往前撞） | **只看动作** |
| `refs/9_herald_spin.png` | 转圈横扫 | **只看动作** |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 最高点 |
| `refs/10b_layout_B.png` | B 的大小示意（和 A 同样的身体大小） | 只看大小和地面线 |
| `style/11_style_murkwolf.png` | 本系列的暗影狼（峡谷野怪），8 倍放大，一格 = 一个像素 | **只看风格**：野怪在格子上怎么画（**最接近**） |
| `style/12_style_brambleback.png` | 本系列的绯红印记树怪（8 倍） | **只看风格**：大块头的四足野怪、背上的大块甲 |
| `style/13_style_chogath.png` | 本包的科加斯（虚空巨兽，8 倍） | **只看风格**：紫色虚空甲壳、尖刺 |
| `style/14_style_reksai.png` | 本包的雷克塞（虚空生物，8 倍） | **只看风格**：蓝紫色甲片怎么分档 |

## 提示词：`riftherald-A.png` / `riftherald-B.png`（同一段提示词，先画 A 再画 B）

十五张图都附上，顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fifteen attached images. Images 1-9 show ONE creature from a game: a hunched, heavy VOID BEAST under a HUGE DOMED SHELL. The shell covers its head and back like a big dome, built of FACETED BLUE-VIOLET CRYSTAL PLATES (light faces teal-blue, dark faces deep indigo-violet, 3-4 flat shades); in the middle of EVERY plate sits a small GLOWING MAGENTA DIAMOND SPOT, rows of them like little eyes; a row of small GOLDEN THORNS lines the shell's front rim. Under the shell a thick DARK PLUM / AUBERGINE BODY, hunched, standing on TWO SHORT THICK HIND LEGS, a LONG THIN TAIL curling up behind it. TWO VERY THICK FRONT ARMS end in BIG CRAB-LIKE PINCER CLAWS (dark violet armour plates, golden tips and edges), hanging in front of the body; two smaller rear arms behind them. A SMALL FACE tucked under the shell's front rim: TWO GLOWING MAGENTA EYES, a row of small golden fangs, and on each side of the face a BIG CURVED GOLDEN TUSK / HORN sweeping upward - very striking; one small golden horn above the middle of the face. On the back of the shell, in its middle, a VERTICAL PINK SLIT EYE (its most famous feature; in 3/4 view a little of it may show on the back). (1 its idle, 3/4 view facing right - for picture A, the look and the ANGLE; 2 the same from the front: the claws, the face under the shell, the two tusks; 3 its face close-up, 3/4: the MAGENTA EYES, the GOLDEN TUSKS, the golden thorns on the rim; 4 reared up on its hind legs, claws raised - for picture B; 5 from behind: the PINK SLIT EYE on the back; 6 its face from the front: how the eyes, tusks and the small horn sit; 7 from the side: how tall the shell is, how long the tail; 8 charging shell-first - pose only; 9 spinning with a sweep - pose only.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the ground, the light line the highest point. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 a wolf monster of this same series - the closest one, 12 a big beast of this series with a heavy back, 13 a purple void beast: shell and spikes, 14 a void creature: how blue-violet plates are shaded).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the shell, the claws, the tusks, the tail); its soles level on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; the SHELL as clear faceted plates in 3-4 shades (the light side to the upper left, a dark line between plates), each plate with ONE small magenta diamond; the BODY as solid areas in 3 dark plums; the GOLD (tusks, thorns, claw tips) as connected bands in 3 golds, never noisy dots; GLOW drawn only as a brighter flat shade (the eyes, the magenta spots, the pink back eye), never a soft halo; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO effects (no shockwave, no void glow, no cracks in the ground, no dust, no glow rings); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi and chunky - a heavy, compact body on short legs; the SHELL BIG, its most striking part; the CLAWS BIG; the face may be a little bigger than the model's (the model's is tiny) but stays tucked under the shell's front rim, and the FACE IS THE CLEAREST PART of the picture. FACE CLEAR: the face in 3 blue-violet shades with a dark rim; TWO MAGENTA EYES, each at least 2x2 squares (the near one 3x2) with its brightest square in the middle; TWO GOLDEN TUSKS, each at least 2 squares thick and 5-7 squares long, in 3 golds. THE COLOURS: shell teal-blue / blue-violet / indigo in 4; spots magenta in 2; body dark plum / aubergine in 3; claws dark violet in 3 with gold tips; gold (tusks, thorns, trims) in 3; eyes magenta-pink, glowing; back eye pink.
PICTURE A (riftherald-A.png): IDLE, 3/4 view facing right (images 1, 2, 3 and 10a): hunched under its big shell, both huge pincer claws hanging low in front of the body, the face under the shell's rim looking to the front-right, the golden tusks curving up, the tail curling up behind. About 460 px (about 42 squares) from the highest point (the shell top / the tusk tips) to its soles, about 43-50 squares wide with the tail and claws (never more than 56).
PICTURE B (riftherald-B.png): REARED UP, 3/4 view facing right (images 4, 6 and 10b): standing UPRIGHT on its two hind legs, both huge pincer claws OPEN and raised in front of it, the head tilted up, the golden tusks pointing up, the shell on its back, the tail curled at its feet. The SAME body size as A, taller only because it stands up: about 670 px (about 61 squares) from the highest point to its soles, about 44-50 squares wide; its soles on the ground line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，甲壳、钳爪、獠牙、尾巴完整，不出画。
- **A**：约 460 px（约 42 格），3/4 朝右，**弓着背缩在甲壳下、两只大钳爪垂在身前**；脚底在地面线上。
- **B**：约 670 px（约 61 格），和 A 一样大的身体，**后腿直立、两只钳爪张开举在身前**、头往上仰；脚底在地面线上。
- 两张都要：**蓝紫晶体甲壳 + 每块甲片一个洋红小菱形 + 前沿金色小尖刺**；**深紫色身体 + 细长卷尾**；**两只大蟹钳（金色爪尖）**；**洋红眼睛 + 两根大金獠牙 + 头顶小金角**。
- 没有特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/riftherald-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/riftherald_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有峡谷先锋自己的动作（我已经按动作片段渲染出来了，后面的骨架包会附上），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸用在所有帧、甲壳（冲锋时翻过来用它撞）、两只大钳爪（横扫、举起、砸下）、两条后腿（小跑、直立、跳）、尾巴（转圈时甩出去）。

| 动作 | 金铲铲里怎么做 / 我们的技能（方案待用户定） |
|---|---|
| 待机 | 选 A：弓背缩在甲壳下；选 B：后腿直立、钳爪举起 |
| 移动 | 弓着身子小跑（金铲铲原样） |
| 被动「虚空甲壳」 | 身边每有一名敌方英雄，自己受到的伤害降低一点（金铲铲「每有一个敌人以它为目标，伤害减免 +1%」的放大版） |
| 普攻「裂钳」 | 钳爪举起往前砸（金铲铲原样的两种爪击，交替） |
| 技能1「回旋横扫」 | 原地转一圈，钳爪和尾巴扫过身边一圈的敌人，造成伤害并短暂减速（金铲铲原样的转圈攻击） |
| 技能2「虚空冲锋」 | 先后腿直立长啸蓄力，然后翻过身用甲壳朝目标直线冲撞：沿途敌人受伤并被撞开，撞到的第一个英雄晕眩（英雄联盟里峡谷先锋的冲锋 + 金铲铲第 9 赛季的「虚空冲锋」） |
| 大招「扭曲护甲」 | 长啸着体型变大、获得额外最大生命，然后猛击以目标为中心 2 格的范围（伤害随最大生命提高）；之后 4 秒获得伤害减免，身边敌人越多减免越多（金铲铲原样） |
| 死亡 | 翻倒在甲壳上（金铲铲原样） |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/riftherald/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和暗影狼、绯红印记树怪、科加斯、雷克塞按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_riftherald_picture.py`（模型在 Riot 客户端的 `TFTSet16.wad.client`，`TFT16_RiftHerald_16.skn/.skl`，76 个关节；十段动作在 `data/characters/tft16_riftherald/animations/skin0.bin`，只有路径哈希，`CLIPS` 里按内容命名；客户端里没有它的原画，所以用头部特写代替）。
- 音效：`tools/lol/extract_riftherald.py`（金铲铲 S16 音效库 + 召唤师峡谷的峡谷先锋自己的音效库，全是它自己的声音）。
