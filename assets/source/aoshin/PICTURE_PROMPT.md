# 敖兴（金铲铲之战 · 第 7 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 敖兴是金铲铲之战第 7 赛季（巨龙之巢）的五费卡（风暴龙 / 龙神），**一条在空中悬浮的风暴之龙**，不走路，一直飘着。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **身体**：**蛇一样修长的龙身**，全身是**青绿 / 湖蓝色的鳞片**（亮青、湖蓝、深青三四档），背上、尾巴上一路长着**一排浅青色的尖刺鬃毛**（像火苗一样往后飘，看附图 1、7、8）；**长尾巴**在身下卷起来，**尾巴尖化成几缕青色的风 / 水雾**（画成几块成形的青色碎片，不要柔光）。肚皮是更深的青蓝色、横着的腹鳞。
> - **头和脸**：**金色的龙面具**盖住了上半张脸（看附图 3、6）：面具正中一道**往上竖起的金色尖棱**，两侧是**弯曲的深色龙角**（深青灰带金边，向外向上弯）；面具上两只**细长、发光的眼睛**；面具下面是**浅青色的龙须 / 胡子**（毛茸茸往下垂），能看到一点张开的嘴。脸（面具 + 眼睛 + 龙角）是全图最好认的地方。
> - **铠甲和手**：胸前一块**深青色的胸甲，金色描边，V 字形**；两肩是**金色的大护肩**，上面镶着**蓝色宝石**；手臂上是**棕铜色的皮甲 / 护腕**；**两只蓝紫色的龙爪手**，指尖是深色的利爪。身下还有**两条短小的后腿**（蓝紫色，带爪）。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：悬浮待机**（金铲铲原样待机，附图 1、2、10a）：**3/4 朝右**，**上身竖直地浮在空中**，胸口朝前，两只龙爪张开在身体两侧，长尾巴从身后绕到身下卷起来，尾巴尖的风雾在左下方。
> - **B：前扑攻击**（他普攻时向前扑的那一下，附图 4、8、10b）：**3/4 朝右**，**身体横过来、向右前方扑出去**，头和面具在最右边、略低，两只龙爪伸在前面，长长的身体和尾巴拖在身后（左边），背上的尖刺鬃毛一路飘向后。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的奥瑞利安·索尔（龙）、希瓦娜的龙形态、拉露恩和远古石甲虫（都是金铲铲英雄），**只看风格**。
> - **长相照金铲铲的模型**（附图 1、2、4、5、7、8 是模型的渲染；附图 3、6 是头部特写，**面具、眼睛、龙角、胡子以附图 3、6 为准**；附图 7 是侧面，看清**身体怎么弯、手脚和尾巴在哪**；附图 8 是 B 的侧面，看清**扑出去时身体有多长**）。
> - **比例**：Q 版，**头和面具画大一点**（约占 A 高度的四分之一），身体圆润、尾巴可以卷得紧一点；**脸一定要清楚**。
> - **脸要清楚**（附图 3、6 特写）：金面具 3–4 档（深金 / 金 / 浅金 / 一格高光），中间竖棱 1 列浅色高光；**两只眼睛**各至少 2×1 格，发亮的浅青白色（发光就用更亮的一档平涂，不要柔光）；**两只龙角**各至少 2 格粗，深青灰 3 档、金色描边，和面具分得开；面具下面的**浅青色胡子**成块、成束。
> - **画布用正方形 1536×1536**。**A：从龙角顶到尾巴最低处约 572 px，也就是约 52 格**，宽约 50–58 格（最多 62 格）；**B：同样的身体大小，因为横过来了，从最高点到最低点约 352 px，也就是约 32 格**，宽约 52–60 格（最多 66 格）。身体最低处在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。龙角、爪子、尾巴全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。**鳞片**用成块的 3–4 档青色表现（亮面朝左上），**尖刺鬃毛**画成一片片清楚的尖角，不要碎点、不要柔光。
> - 不画任何技能特效（闪电、雷云、风暴、护盾都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/aoshin-picture/aoshin-A.png`、`aoshin-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/aoshin-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/aoshin_picture_done.zip`。

## 附图（在压缩包 `aoshin_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_aoshin_34.png` | 金铲铲敖兴的模型，悬浮待机，3/4 朝右 | **A** 的姿势、颜色、**角度** |
| `refs/2_aoshin_front.png` | 模型，待机，正面 | 胸甲、护肩、两只手、后腿在哪 |
| `refs/3_aoshin_head.png` | 头部特写（3/4） | **金面具、眼睛、龙角、胡子** |
| `refs/4_aoshin_lunge.png` | 模型，攻击时前扑，3/4 朝右 | **B** 的姿势 |
| `refs/5_aoshin_back.png` | 背后 | 背上的尖刺鬃毛、尾巴 |
| `refs/6_aoshin_head_front.png` | 头部特写（正面） | **脸**：竖棱、两只眼睛、两只角怎么排 |
| `refs/7_aoshin_side.png` | 侧面 | 身体怎么弯、手、后腿、尾巴的位置 |
| `refs/8_aoshin_lunge_side.png` | B 的侧面 | 扑出去时身体有多长、头在哪 |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 龙角顶 |
| `refs/10b_layout_B.png` | B 的大小示意 | 只看大小和地面线 |
| `style/11_style_aurelionsol.png` | 本包的奥瑞利安·索尔（龙），8 倍放大，一格 = 一个像素 | **只看风格**：龙的鳞片、金饰怎么画 |
| `style/12_style_shyvana_dragon.png` | 本包的希瓦娜龙形态（8 倍） | **只看风格**：龙的身体、尖刺、尾巴怎么画 |
| `style/13_style_alune.png` | 本系列的拉露恩（8 倍） | **只看风格**：金铲铲英雄在格子上的样子 |
| `style/14_style_krug.png` | 本系列的远古石甲虫（8 倍） | **只看风格**：怪物在格子上的样子 |

## 提示词：`aoshin-A.png` / `aoshin-B.png`（同一段提示词，先画 A 再画 B）

十四张图都附上，顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fourteen attached images. Images 1-8 show ONE creature from a game: a STORM DRAGON that HOVERS in the air and never walks. A long SERPENT-LIKE BODY covered in CYAN / TURQUOISE SCALES (bright cyan, turquoise, deep teal), a row of PALE CYAN SPIKY MANE running down the back and the tail, the spikes streaming backwards like flames; a LONG TAIL curling under him, its tip breaking into a few CYAN WISPS of wind and spray; a darker blue-teal belly of horizontal scales. HIS HEAD: a GOLD DRAGON MASK covers the upper face, a tall gold CREST SPIKE rising up its middle, two CURVED DARK HORNS (dark teal-grey with gold edges) sweeping out and up on each side, two NARROW GLOWING EYES in the mask, and under the mask a PALE CYAN BEARD / MANE hanging down, a little of the open jaw showing. HIS ARMOUR: a DARK TEAL BREASTPLATE with GOLD TRIM in a V shape on the chest; two BIG GOLD SHOULDER GUARDS each set with a BLUE GEM; BRONZE-BROWN LEATHER BRACERS on the arms; two BLUE-VIOLET CLAWED HANDS with dark talons; under the body two SHORT BLUE-VIOLET HIND LEGS with claws. (1 his idle, hovering upright, 3/4 view facing right - for picture A, the look and the ANGLE; 2 the same from the front: the breastplate, the shoulder guards, both hands, the hind legs; 3 his head close-up, 3/4: the MASK, the EYES, the HORNS, the BEARD; 4 lunging forward in his attack, 3/4 facing right - for picture B; 5 from behind: the spiky mane and the tail; 6 his head from the front: how the crest, the two eyes and the two horns sit; 7 from the side: how the body curves, where the hands, hind legs and tail are; 8 the lunge from the side: how long the body is, where the head is.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the lowest point of the figure, the light line the top of the horns. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 a dragon hero, 12 a dragon, 13 and 14 heroes of this same series).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the horns, the claws, the tail and its wisps); the lowest point of the figure on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; the SCALES as solid blocks of 3-4 cyan shades (the light side to the upper left); the SPIKY MANE as clear separate pointed spikes; the TAIL WISPS as a few solid cyan shapes, never noisy dots; GLOW drawn only as a brighter flat shade (the eyes, the gems), never a soft halo; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO effects (no lightning, no storm cloud, no wind swirl, no shield); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi - the HEAD AND MASK BIG (about a quarter of picture A's height), a rounded body, the tail curled fairly tight; the FACE IS THE CLEAREST PART of the picture. FACE CLEAR: the gold mask in 3-4 shades (deep gold, gold, pale gold, one highlight) with a 1-square pale highlight down its crest; TWO EYES, each at least 2x1 squares, glowing pale cyan-white; TWO HORNS, each at least 2 squares thick, dark teal-grey in 3 shades with gold edges, clearly apart from the mask; the PALE CYAN BEARD under the mask in solid tufts. THE COLOURS: scales bright cyan / turquoise / deep teal in 4; mane and beard pale cyan / white-cyan in 3; belly blue-teal in 3; mask and shoulder guards gold in 3-4; gems blue; breastplate dark teal with gold trim; bracers bronze-brown in 3; hands and hind legs blue-violet in 3 with dark talons.
PICTURE A (aoshin-A.png): HOVERING UPRIGHT, 3/4 view facing right (images 1, 2, 3 and 10a): the upper body straight up in the air, the chest to the front, both clawed hands spread out at his sides, the long tail coming round from behind and curling under him, the tail wisps at the lower left. About 572 px (about 52 squares) from the tip of the horns to the lowest curl of the tail, about 50-58 squares wide (never more than 62).
PICTURE B (aoshin-B.png): LUNGING FORWARD, 3/4 view facing right (images 4, 8 and 10b): the body turned level and thrown forward to the front-right, the head and mask at the far right and a little low, both clawed hands reaching forward, the long body and tail trailing behind to the left, the spiky mane streaming back. The SAME body size as A; about 352 px (about 32 squares) from the highest point to the lowest, about 52-60 squares wide (never more than 66); the lowest point on the line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，龙角、爪子、尾巴完整，不出画。
- **A**：约 572 px（约 52 格），3/4 朝右，**竖直悬浮**，两只龙爪张开，尾巴在身下卷起；最低处在灰线上。
- **B**：约 352 px（约 32 格），和 A 一样大的身体，**横过来向右前方扑出**，头在最右、龙爪在前，身体和尾巴拖在后面；最低处在灰线上。
- 两张都要：**青绿鳞片的长身体 + 浅青尖刺鬃毛**；**金面具 + 竖起的金棱 + 两只弯角 + 发亮的眼睛 + 浅青胡子**；**深青胸甲金边 + 金护肩蓝宝石 + 棕铜护腕 + 蓝紫龙爪**；**两条短后腿**；**尾巴尖的青色风雾（成块）**。
- 没有特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/aoshin-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/aoshin_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有敖兴自己的动作（我已经按动作片段渲染出来了，后面会照着做动作帧），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸（面具、角、胡子）用在所有帧、两只龙爪（张开、前抓、举起召雷）、长身体和尾巴（飞行时拉长、悬浮时卷起）、两条短后腿。

| 动作 | 金铲铲里怎么做 / 我们的技能 |
|---|---|
| 待机 | 选 A：竖直悬浮、呼吸起伏；选 B：横着飘 |
| 移动 | 身体放平、向前飞（金铲铲原样，没有走路） |
| 普攻「球状闪电」 | 向前一扑，从口中吐出一团球状闪电（远程） |
| 被动「风暴龙威」 | 开战数秒后，天雷劈向周围所有敌方英雄：最大生命值百分比真实伤害 + 晕眩，之后自身伤害提高 |
| 技能1「雷息」 | 张口喷出一道直线闪电，命中的敌人技能冷却变长 |
| 技能2「腾云」 | 向后飞掠拉开距离，身上一层风暴护盾 |
| 大招「闪电暴雨」 | 立起身子、张开双爪召来雷云，一连串闪电随机劈向区域里的敌人（金铲铲的施法动作） |
| 死亡 | 向后仰倒，从空中坠下（金铲铲原样） |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/aoshin/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和奥瑞利安·索尔、希瓦娜龙形态、拉露恩、远古石甲虫按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_aoshin_picture.py`（模型在 Riot 客户端的 `TFTSet7.wad.client`，`tft7_aoshin.skn/.skl`，104 个关节；动作在 `data/characters/tft7_aoshin/animations/skin0.bin`，只有路径哈希，`CLIPS` 里按内容命名；客户端里没有他的原画，所以用头部特写代替）。
- 音效：`tools/lol/extract_aoshin.py`（第 7 赛季的音效库客户端里已经没有了：云端亚龙 + 沃利贝尔 / 凯南 / 迦娜）。
