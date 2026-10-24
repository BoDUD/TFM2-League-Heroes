# 岩雀 塔莉垭：第 0 步，先画像素风原图（给 Codex 的提示词）

> 塔莉垭是英雄联盟里的**岩雀**：一个恕瑞玛的少女织石者，能操纵岩石，会踩着一块大石头"冲浪"滑行。这一步把她画出来，用户从里面挑：
> - **塔莉垭**：**小麦色皮肤**的少女，脸颊上有一点雀斑；**一大团往上盘起、蓬松的棕色头发**（像一朵往上翻的云，发尾一缕缕翘起），头顶正前方一个**金色的圆形发饰**（中间一颗奶白色的石头）；肩上披一件**米白 / 沙色的石片披肩**（像一片片叠起来的石头羽毛，领子高高立起）；里面是**深靛紫色的长上衣和紧身裤**，腰上一圈金边；外面一件**红色的长外套**，金色描边，外套前面**两条长长的红色垂带一直垂到小腿**，**垂带末端挂着几块灰色的石头**；**紫色的袖子 + 米白色的护腕**；**棕色的长靴**。
>
> 请 Codex 画**两张全身像**（**格子大小一样**，都是 **3/4 正面朝右**），用户从里面挑：
> - **A：站立待机**——英雄联盟里的待机：站得笔直、两手自然垂在身侧，手指微微张开（附图 1、2、9a）。
> - **B：踩石冲浪**——她的被动"浮石冲"：蹲在一块**裹着红布的大石头**上滑行，一只手往前伸、一只手撑在石头上，身后飞起几块碎石（附图 6、9b）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的奇亚娜、阿兹尔、佐伊、阿萝拉，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–8；附图 5 官方原画看气质和颜色——**盘起的棕色大头发 + 金色发饰、石片披肩、红色长外套和挂石头的垂带最重要**）。
> - **比例**：Q 版。**头比原版大很多**（头发顶到下巴约占全身的三分之一出头），脸朝右前方；身子小巧；披肩又宽又显眼；两条垂带和末端的石头清楚；腿分开稳稳站着。**头发和披肩都不能挡住脸。**
> - **塔莉垭的脸**（附图 3 特写）：小麦色皮肤（3 档），**两只眼睛一样高、都看得见**（每只至少 2×2 格），**深棕色的眼睛**带一格高光；眉毛浓一点；表情认真、有点倔强；脸颊几颗浅色雀斑可以省略。
> - **颜色**：皮肤 小麦色 3 档；头发 棕色 3–4 档；发饰 金色 2 档 + 奶白石头 1–2 档；披肩 米白 / 沙色 3 档（石片之间用最暗一档分开）；上衣和裤子 深靛紫 3 档；外套和垂带 红色 3 档 + 金色描边 2 档；垂带上的石头 灰色 3 档；袖子 紫色 2 档、护腕 米白 2 档；靴子 棕色 3 档。B 的大石头：棕色岩石 3 档 + 裹着的红布 3 档 + 金边。
> - **画布用正方形 1536×1536**。**A：从头发顶到鞋底约 594 px，也就是约 54 格**；宽约 29 格（含两条垂带）。**B：同样的格子大小**，从头发顶到石头底约 57 格，宽约 46 格（含飞起的碎石，可以窄一点，但不能超过 52 格）。鞋底 / 石头底在离画布底边约 146 px 的地方（附图 9a、9b 的灰线）；站在画布中间（附图 9a、9b 的位置）。头发、垂带、碎石全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（飞出去的石子串、地面隆起、石雷阵、石墙都放到后面单独画；B 身后的几块碎石是她冲浪的一部分，可以画，但要少、要清楚）；不画地面，不画投影。
> - 交付：`outputs/taliyah-picture/taliyah-A.png`、`taliyah-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/taliyah-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/taliyah_picture_done.zip`。

## 附图（在压缩包 `taliyah_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_taliyah_idle.png` | 英雄联盟原版塔莉垭的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_taliyah_frontal.png` | 同一帧，正面 | 披肩、上衣的金边、两条垂带和末端的石头 |
| `refs/3_taliyah_head.png` | 头部特写（3/4） | **盘起的头发、金色发饰、脸**、石片披肩的领子 |
| `refs/4_taliyah_back.png` | 同一帧的背后 | 头发后面、披肩和红外套的背面 |
| `refs/5_taliyah_splash.png` | 官方加载画面 | 气质、**脸**、颜色 |
| `refs/6_taliyah_surf.png` | 被动冲浪，3/4 朝右 | **B 的姿势**：蹲在裹红布的大石头上，手往前伸 |
| `refs/7_taliyah_run.png` | 跑步的一帧（3/4） | 她怎么跑（这一步不画，后面用） |
| `refs/8_taliyah_cast.png` | Q 扔石头的一帧 | 抬手召石头的样子（这一步不画，后面用） |
| `refs/9a_layout_taliyah.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 在画布上的位置、大小、地面线（灰）；浅灰线 = 头发顶 |
| `refs/9b_layout_taliyah_surf.png` | B 的布局示意 | 同上，冲浪；和 A 同一个比例，石头底在地面线上 |
| `style/10_style_qiyana.png` | 本包的奇亚娜，8 倍放大，一格 = 一个像素 | **只看风格**：恕瑞玛 / 大地系的 Q 版女孩、金饰 |
| `style/11_style_azir.png` | 本包的阿兹尔（8 倍） | **只看风格**：恕瑞玛的金边、沙色 |
| `style/12_style_zoe.png` | 本包的佐伊（8 倍） | **只看风格**：Q 版少女的大头发和脸 |
| `style/13_style_aurora.png` | 本包的阿萝拉（8 倍） | **只看风格**：中路法师少女、长外套 |

## 提示词：`taliyah-A.png` / `taliyah-B.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-8 are 3D renders and art of a character from a game. THE STONEWEAVER GIRL (images 1-8): a young desert girl with TANNED SKIN, a BIG SWEPT-UP MASS OF BROWN HAIR piled high on her head like an upturned cloud with tufts curling out, a small ROUND GOLD ORNAMENT with a cream stone in its middle at the front top of the hair; a high CREAM / SAND-COLOURED MANTLE OF STONE PLATES over her shoulders (overlapping stone "feathers", the collar standing up); under it a long DARK INDIGO-PURPLE TUNIC and leggings with a gold-trimmed waist; over it a long RED COAT with GOLD TRIM whose TWO LONG RED FRONT PANELS hang down to her shins, each ending in a few GREY STONES; PURPLE SLEEVES with CREAM CUFFS; BROWN BOOTS. (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the mantle, the tunic's gold trim, the two panels and their stones; 3 her head close-up: the piled hair, the gold ornament, the FACE, the stone collar; 4 the same from behind; 5 the official illustration: her mood, the FACE, the colours; 6 her rock surf, 3/4 view facing right - the pose of B, crouching on a big boulder wrapped in red cloth, one hand reaching forward, a few stone chips flying behind; 7 a running frame and 8 a casting frame - both for later.) Images 9a-9b are layout guides: where the character goes on the canvas and how big, the grey line is the ground, the light line the top of the figure. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a chibi desert girl with gold ornaments (10), desert gold trim and sand colours (11), a chibi girl's big hair and face (12), a mage girl in a long coat (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the hair, the panels and their stones, the flying chips); the soles (in B the bottom of the boulder) on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing where the guide shows the character (the centre). In picture A THE STONEWEAVER GIRL is about 594 px (about 54 squares) from the top of her hair to her soles and about 29 squares wide with both panels; in picture B, at the same square size, about 57 squares from the top of her hair to the bottom of the boulder and about 46 squares wide with the flying chips (narrower is fine, never more than 52).
PROPORTIONS: chibi. The HEAD MUCH BIGGER than in the renders (from the top of the hair to the chin a bit more than a third of the whole figure) so the face reads clearly, turned to the front-right; a small body; the stone mantle wide and clear; the two red panels and their end stones clear; the legs apart and planted. The hair and the mantle NEVER cover the face.
THE FACE: tanned skin in 3 shades, both eyes at the SAME height and both visible (each at least 2x2 squares), DARK BROWN with one highlight square; strong eyebrows; an earnest, stubborn look.
THE COLOURS: the skin tan in 3 shades; the hair brown in 3-4; the ornament gold in 2 with a cream stone in 1-2; the mantle cream / sand in 3 (the plates parted by its darkest shade); the tunic and leggings dark indigo-purple in 3; the coat and its panels red in 3 with gold trim in 2; the panel stones grey in 3; the sleeves purple in 2, the cuffs cream in 2; the boots brown in 3. B's boulder: brown rock in 3 with red cloth wrapped round it in 3 and a gold edge. Every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the tan face, the brown hair, the cream mantle, the indigo tunic, the red coat and the grey stones clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no volley of flying rocks, no ground eruption, no minefield, no stone wall); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (taliyah-A.png): THE STONEWEAVER GIRL standing idle in 3/4 view facing right (images 1 and 9a) - standing straight and calm on two legs apart, the face to the front-right, both arms hanging at her sides with the fingers a little spread; the near panel on the image left in full tone, the far one a step darker; nothing covering the face.
PICTURE B (taliyah-B.png): the SAME girl as A surfing on her boulder in 3/4 view facing right (images 6 and 9b) - crouching low on a big brown boulder wrapped in red cloth with a gold edge, her near hand resting on the boulder, her far arm reaching forward to the image right, her coat flying back; three or four stone chips flying behind her on the image left; nothing covering the face.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、垂带、碎石完整，不出画。
- 塔莉垭：Q 版，**头比原版大很多**、脸清楚；**小麦色皮肤**，**两只眼睛一样高、深棕色**；盘起的棕色大头发 + 金色发饰**不挡脸**；米白石片披肩；深靛紫上衣；红色长外套 + 金边 + 两条挂石头的垂带；紫袖子米白护腕；棕靴子。
- A 是站立待机，B 是蹲在裹红布的大石头上冲浪；都是 3/4 正面朝右；A 从头发顶到鞋底约 594 px（约 54 格），B 同样的格子大小；鞋底 / 石头底在地面线上。
- 没有技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/taliyah-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/taliyah_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：塔莉垭的头（一张脸用在所有帧）、两只手臂（她用手召石头、推地面）、两条垂带（跑动时会飘）、冲浪的大石头（被动 / 大招冲浪）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 移动 / 普攻 / 死亡 | Taliyah_Idle1 / Taliyah_Run1（被动时 Run_Passive 冲浪）/ Attack1、Attack2 / Death | 普攻是抬手甩出一块石头 |
| **石穿**（Q） | Spell1_0 | 抬手连续扔出一串石子，边走边放 |
| **岩突**（W） | Spell2_0 | 两手往下一按再往一个方向推，地面隆起把敌人掀飞 |
| **撒石阵**（E） | Spell3 | 双手一扫，往前撒出一片石雷 |
| **墙幔**（R） | Spell4 → Spell4_Run | 拉出一道长石墙，踩在墙上冲浪 |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/taliyah/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出；`regrid` 的格子要给得比实际略大，否则会拆行），和已合并的中路英雄（阿萝拉、佐伊、奇亚娜、薇古丝、辛德拉）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小、站立还是冲浪当待机。
- 定下后第 1 步按游戏格子重画（`pack_singed_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Taliyah`（taliyah_idle1、taliyah_run1、taliyah_run_passive、taliyah_attack1/2、taliyah_spell1_0、taliyah_spell2_0、taliyah_spell3、taliyah_spell4、taliyah_spell4_run、taliyah_death）。皮肤藏着三个道具（SurfRock、RecallRock、TauntRock）：普通渲染用 `--hide-submeshes`，冲浪只藏 `--hide-submesh TauntRock --hide-submesh RecallRock`；所有渲染加 `--fit-all`，比例才一致。加载画面：`assets/characters/taliyah/skins/base/taliyahloadscreen.tex`（不带 `_0`）。
