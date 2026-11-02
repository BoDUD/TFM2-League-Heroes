# 岩宝（金铲铲之战 · 第 16 赛季）：第 0 步，先画像素风原图（给 Codex 的提示词）

> 岩宝是金铲铲之战第 16 赛季的五费卡（以绪塔尔），技能「震地猛击」：**一个高大、粗壮的岩石魔像，身上缠着树根，肩上长着一棵小盆景树**。这一步画两张，**格子大小一样**，用户从里面选一种做游戏造型：
> - **身体**：**深青灰 / 板岩蓝绿色的大块石头**拼成的身体（亮面偏浅灰蓝，暗面深墨绿，3–4 档），**胸口一块深色石板，正中嵌着一个紫色的三角形水晶纹章**（附图 2）。**两条短粗的石腿**，脚是方方的大石块。
> - **两只巨大的石拳**（附图 1、2、7）：手臂像几块叠起来的大圆石，**拳头比头大好几倍**，垂在身体两侧、离身体有点远，指节是几块钝石头。
> - **树根和植物**（附图 1、5）：**棕褐色的粗树根 / 藤蔓**一圈圈缠在肩膀、手臂和腰上；肩上和背上有几片**铺开的亮绿色苔藓 / 叶丛**；**一边肩膀上长着一棵小小的盆景树**（细弯的树干 + 两三层扁平的绿叶冠，附图 5 看得最清楚）；**两根往上弯的树皮色尖角**从肩膀两边翘起来，像一对弯弯的木刺；肩甲上有几道**橙红色的苔藓斑纹**。
> - **头和脸**（附图 3、6 特写）：头**很小，缩在两个肩膀之间**，外面是一个**尖顶的石头兜帽**（浅灰蓝，3 档）；兜帽里是一块**橙色的脸板**（上浅黄、下深橙的发光色，像一片橙色的叶子 / 一团火）；脸板上是**两只黄色的圆环眼睛**（亮黄圈，中间一格深色），近处那只大一点。没有嘴巴。
>
> 请 Codex 画**两张**（**格子大小一样**）：
> - **A：待机**（金铲铲原样待机，附图 1、2、10a）：**3/4 朝右**，站直，两只大石拳垂在身体两侧、略微张开，小头缩在肩膀中间朝右前方，盆景树和两根木刺在肩上。
> - **B：举拳**（他普攻砸地前举起双拳的那一下，附图 4、10b）：**3/4 朝右**，两只大石拳**高高举过头顶、并在一起**，准备砸下来；身体微微后仰，腿叉开站稳。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的苍蓝雕纹魔像（同样是岩石魔像，**最接近的参考**）、远古石甲虫（金铲铲的岩石怪物）、加里奥（石像）和艾翁（树精，树根和叶子怎么画），**只看风格**。
> - **长相照金铲铲的模型**（附图 1、2、4、5、7 是模型的渲染；附图 3、6 是头部特写，**兜帽、橙色脸板、两只圆环眼睛以附图 3、6 为准**；附图 7 是侧面，看清**石拳和身体有多厚**；附图 8 是他跳起砸地落下时蹲着的样子，附图 9 是他跑步，**这两张只看动作**）。
> - **比例**：Q 版、敦实的大块头，**头可以比模型大一些**（模型的头太小，看不清），但仍然缩在两肩之间、戴着兜帽；**石拳要大**，是他最显眼的地方；**脸（橙色脸板和两只眼睛）一定要清楚**，是全图最好认的地方。
> - **脸要清楚**（附图 3、6 特写）：兜帽 3 档浅灰蓝，边缘一圈深色；**橙色脸板**至少 5×6 格，3 档（浅黄 / 橙 / 深橙）；**两只眼睛**各至少 2×2 格的亮黄圆环（近处那只 3×3），中间一格深色（发光就用更亮的一档平涂，不要柔光）。
> - **画布用正方形 1536×1536**。**A：从最高点（盆景树顶 / 木刺尖）到脚底约 550 px，也就是约 50 格**，宽约 58–64 格（最多 70 格，两只石拳张开）；**B：同样的身体大小**，因为举着拳头所以更高：从拳头顶到脚底约 770 px，也就是约 70 格，宽约 40–46 格。脚底在离画布底边约 146 px 的地方（附图 10a、10b 的灰线），位置照附图 10a、10b。石拳、盆景树、木刺全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。**石块**画成几大块棱面（亮面朝左上，石缝一道深色线），**树根**是连成条的 2–3 档棕色，**叶丛**是成块的 3 档绿色，不要碎点。
> - 不画任何技能特效（落石、冲击波、尘土、裂地、光圈都放到后面单独画）；不画地面，不画投影。
> - 交付：`outputs/brock-picture/brock-A.png`、`brock-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/brock-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/brock_picture_done.zip`。

## 附图（在压缩包 `brock_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_brock_34.png` | 金铲铲岩宝的模型，待机，3/4 朝右 | **A** 的姿势、颜色、**角度** |
| `refs/2_brock_front.png` | 模型，待机，正面 | 两只石拳、胸口的紫色水晶纹章、头在两肩之间 |
| `refs/3_brock_head.png` | 头部特写（3/4） | **兜帽、橙色脸板、圆环眼睛** |
| `refs/4_brock_slam.png` | 模型，双拳举过头顶，3/4 朝右 | **B** 的姿势 |
| `refs/5_brock_back.png` | 背后 | 树根怎么缠、**盆景树**、叶丛 |
| `refs/6_brock_head_front.png` | 头部特写（正面） | **脸**：两只眼睛怎么排 |
| `refs/7_brock_side.png` | 侧面 | 石拳和身体有多厚 |
| `refs/8_brock_landing.png` | 跳起砸地落下时蹲着 | **只看动作** |
| `refs/9_brock_run.png` | 跑步 | **只看动作** |
| `refs/10a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰）；浅灰线 = 最高点 |
| `refs/10b_layout_B.png` | B 的大小示意（和 A 同样的身体大小） | 只看大小和地面线 |
| `style/11_style_sentinel.png` | 本系列的苍蓝雕纹魔像（岩石魔像），8 倍放大，一格 = 一个像素 | **只看风格**：岩石魔像在格子上怎么画（**最接近**） |
| `style/12_style_krug.png` | 本系列的远古石甲虫（8 倍） | **只看风格**：岩石棱面、发光的缝 |
| `style/13_style_galio.png` | 本包的加里奥（石像，8 倍） | **只看风格**：大块头的石头身体 |
| `style/14_style_ivern.png` | 本包的艾翁（树精，8 倍） | **只看风格**：树根、树皮和叶子怎么画 |

## 提示词：`brock-A.png` / `brock-B.png`（同一段提示词，先画 A 再画 B）

十五张图都附上，顺序同上表。先画 A，再画 B（同样的格子大小）。

```text
Fifteen attached images. Images 1-9 show ONE character from a game: a big, chunky STONE GOLEM overgrown with nature. His body is built of big DARK SLATE-TEAL STONE blocks (light faces pale grey-blue, dark faces deep ink-green, 3-4 flat shades); on his chest a dark stone plate with a VIOLET TRIANGULAR CRYSTAL EMBLEM in its middle; two SHORT THICK STONE LEGS with blocky stone feet. TWO HUGE STONE FISTS: the arms are stacked round boulders and the fists are several times bigger than his head, hanging at his sides a little away from the body, blunt stone knuckles. THICK BROWN ROOTS / VINES wind round his shoulders, arms and waist; flat BRIGHT GREEN MOSS / LEAF TUFTS lie on his shoulders and back; a SMALL BONSAI TREE grows on one shoulder (where images 1 and 5 show it) (a thin bent trunk and two or three flat green leaf crowns); TWO CURVED BARK-COLOURED HORNS / thorns rise from his shoulders; a few ORANGE-RED LICHEN streaks on the shoulder stones. A SMALL HEAD sunk between his shoulders: a POINTED STONE HOOD (pale grey-blue) around an ORANGE FACE PLATE that glows (pale yellow at the top, orange, deep orange at the bottom, like an orange leaf or a flame), on it TWO GLOWING YELLOW RING EYES (a bright yellow ring with one dark square in the middle), the near one a bit bigger. No mouth. (1 his idle, 3/4 view facing right - for picture A, the look and the ANGLE; 2 the same from the front: the fists, the violet chest emblem, the head between the shoulders; 3 his head close-up, 3/4: the HOOD, the ORANGE FACE PLATE, the RING EYES; 4 both fists raised over his head - for picture B; 5 from behind: the roots, the BONSAI TREE, the leaf tufts; 6 his head from the front: how the two eyes sit; 7 from the side: how deep the fists and the body are; 8 crouched as he lands from a jump-slam - pose only; 9 running - pose only.) Images 10a-10b are layout guides: where the figure goes on the canvas and how big, the grey line is the ground, the light line the highest point. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions (11 a stone golem of this same series - the closest one, 12 a stone beast of this series, 13 a stone statue, 14 a tree spirit: how roots, bark and leaves are drawn).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the fists, the bonsai tree, the horns); his soles level on one line about 146 px above the bottom edge (the grey line of images 10a-10b), placed where the guide shows the figure.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares; the STONES as big flat facets in 3-4 shades (the light side to the upper left, a dark line in the seams); the ROOTS as connected bands in 2-3 browns; the LEAVES as solid clumps in 3 greens, never noisy dots; GLOW drawn only as a brighter flat shade (the face plate, the eyes, the violet emblem), never a soft halo; clear readable shapes, no dithering, no gradients, no blur, no anti-aliasing. Every pixel fully opaque. NO effects (no falling rocks, no shockwave, no dust, no cracks in the ground, no glow rings); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PROPORTIONS: chibi and chunky - a heavy, compact body on short legs; the FISTS BIG, his most striking part; the head may be a little bigger than the model's (the model's is tiny) but stays sunk between the shoulders inside its hood, and the FACE IS THE CLEAREST PART of the picture. FACE CLEAR: the hood in 3 pale grey-blue shades with a dark rim; the ORANGE FACE PLATE at least 5x6 squares in 3 shades (pale yellow, orange, deep orange); TWO EYES, each a bright yellow ring at least 2x2 squares (the near one 3x3) with one dark square in the middle. THE COLOURS: stone slate-teal / grey-blue / ink-green in 4; chest emblem violet in 2-3; roots brown in 3; leaves and moss bright green in 3; horns bark brown-beige in 2-3; lichen orange-red in 2; hood pale grey-blue in 3; face plate pale yellow / orange / deep orange; eyes bright yellow.
PICTURE A (brock-A.png): IDLE, 3/4 view facing right (images 1, 2, 3 and 10a): standing upright, both huge stone fists hanging at his sides, a little spread; the small hooded head between the shoulders looking to the front-right; the bonsai tree and the two horns on his shoulders. About 550 px (about 50 squares) from the highest point (the bonsai top / the horn tips) to his soles, about 58-64 squares wide with the fists spread (never more than 70).
PICTURE B (brock-B.png): FISTS RAISED, 3/4 view facing right (images 4, 6 and 10b): both huge stone fists lifted HIGH OVER HIS HEAD, held together, ready to slam down; the body leaning back a little, the legs apart and planted. The SAME body size as A, taller only because of the raised fists: about 770 px (about 70 squares) from the top of the fists to his soles, about 40-46 squares wide; his soles on the ground line of image 10b.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，石拳、盆景树、木刺完整，不出画。
- **A**：约 550 px（约 50 格），3/4 朝右，**站直、两只大石拳垂在两侧**，小头缩在两肩之间；脚底在地面线上。
- **B**：约 770 px（约 70 格），和 A 一样大的身体，**双拳高高举过头顶并在一起**、身体微微后仰；脚底在地面线上。
- 两张都要：**深青灰板岩色的石头身体 + 胸口紫色三角水晶纹章**；**两只巨大的石拳**；**棕色树根缠身 + 亮绿叶丛 + 肩上的小盆景树 + 两根弯木刺 + 橙红苔藓斑**；**尖顶石兜帽 + 发光的橙色脸板 + 两只黄色圆环眼睛**。
- 没有特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/brock-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/brock_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

客户端里有岩宝自己的动作（我已经按动作片段渲染出来了，后面的骨架包会附上），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸用在所有帧、两只大石拳（砸地、勾拳、举起、抓石头扔出去）、两条腿（奔跑、蹲下、跳起、落地）、肩上的盆景树和木刺（跟着身体动）。

| 动作 | 金铲铲里怎么做 / 我们的技能（方案 A，等用户定） |
|---|---|
| 待机 | 选 A：站直、双拳垂下；选 B：双拳举过头顶 |
| 移动 | 弓着身子、沉重地小跑（金铲铲原样） |
| 被动「岩心不动」 | 不受控制效果影响（金铲铲原样） |
| 普攻「震地拳」 | 双拳砸下，目标周围一小圈溅射伤害；每第三下把目标短暂击飞（金铲铲原样的砸拳） |
| 技能1「巨岩投掷」 | 从地上掰起一块大石头扔向目标，造成伤害并减速 |
| 技能2「苔藤缠握」 | 身上的树根伸出去缠住最近的敌人（定身），自己获得一层护盾 |
| 大招「震地猛击」 | 高高跃起砸进敌群：范围伤害（离落点越远越低），第一次被砸中的敌人被击飞，随后天上落下一阵碎石（金铲铲原样） |
| 死亡 | 往前扑倒在地（金铲铲原样） |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/brock/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和苍蓝雕纹魔像、远古石甲虫、加里奥、艾翁按游戏里的大小并排，给用户定 A / B、大小、PPU。
- 渲染：`tools/art/pack_brock_picture.py`（模型在 Riot 客户端的 `TFTSet16.wad.client`，`TFT16_Brock_16.skn/.skl`，57 个关节；八段动作在 `data/characters/tft16_brock/animations/skin0.bin`，只有路径哈希，`CLIPS` 里按内容命名；客户端里没有他的原画，所以用头部特写代替）。
