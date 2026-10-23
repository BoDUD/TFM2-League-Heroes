# 雪原双子 努努和威朗普：第 0 步，先画像素风原图（给 Codex 的提示词）

> 努努和威朗普是英雄联盟里**一个小男孩骑着一只大雪人**的英雄，两个算**一个角色**。这一步把他们画出来，用户从里面挑：
> - **威朗普**：一只**又大又圆的雪人（雪怪）**，**淡蓝色的毛**，头顶、肩膀、前臂是**白色蓬松的长毛**，身上有**蓝色的螺旋花纹**；**发蓝光的眼睛**，**棕色的鼻头**，**咧开大嘴笑**，露出牙齿和两颗小獠牙；耳朵里面是**粉红色**；**深蓝色的爪子**；身体下半和腿是**深一点的蓝**；身后一条**蓬松的大尾巴**；头上长着**一对棕色的大木头鹿角**（分好几个叉，往两边张开）。
> - **努努**：骑在威朗普**头上**、两手扶着鹿角的**小男孩**；戴着**蓝色毛茸茸的兜帽**（帽子上有两只**里面粉红的猫耳朵**，顶上一撮**米白色的毛球**）；露出**棕色刘海**和**大眼睛**，笑嘻嘻的；披着**橙色的斗篷**，领口和下摆是**白色的毛边**，胸前一颗**蓝色的宝石扣**；**棕色手套、棕色靴子**、橄榄绿裤子；背后一个**棕色皮背包 / 弹弓**。
>
> 请 Codex 画**两张全身像**（**格子大小一样**），用户从里面挑大小：
> - **A：英雄联盟里的待机，3/4 正面朝右**（附图 1、2、8a）。
> - **SA：A 的侧面，朝右**（附图 6、8b）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 9–12 是本包里的沃利贝尔（大毛熊）、布隆（弗雷尔卓德）、奥恩（大块头、毛和角）和纳尔（毛茸茸的小家伙），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7；附图 5 官方原画看气质和颜色）。
> - **比例**：Q 版。威朗普的**头大、身子圆滚滚**，**腿短粗**，两脚分开稳稳站着，前臂长、爪子大；**鹿角要大**，往两边张开但不出画。努努也是 **Q 版大头**（头连兜帽约占他自己身高的一半），**坐在威朗普头顶、鹿角中间**，**不挡威朗普的脸**。从努努的毛球顶到威朗普脚底，努努约占上面三分之一。
> - **两张脸都要清楚**（附图 3 特写）：
>   - 努努：肤色 3 档；**两只眼睛一样大、一样高、都看得见**（每只至少 2×2 格，带一格高光）；咧嘴笑；棕色刘海。
>   - 威朗普：**两只发蓝光的眼睛**（各至少 2×2 格，最亮一格接近白色）；棕色鼻头；**大大的笑嘴**，白牙一排，两颗小獠牙。
> - **颜色**：威朗普的毛 淡蓝 4 档（亮处接近白的冰蓝，暗处中蓝），腿和下半身 深蓝 2–3 档，白色长毛 2–3 档（白、浅灰蓝），螺旋纹 亮蓝 1–2 档，眼睛 青白 2 档，鼻头 棕 2 档，耳内 粉红 2 档，爪子 深蓝 2 档，鹿角 棕色木头 3–4 档。努努：兜帽 蓝 3 档，毛球 米白 2 档，猫耳里 粉 1–2 档，皮肤 3 档，头发 棕 2 档，斗篷 橙 3–4 档，毛边 白 2 档，宝石扣 蓝 1–2 档，手套 / 靴子 / 背包 棕 3 档，裤子 橄榄绿 2 档。
> - **画布用正方形 1536×1536**。**从努努的毛球最高处到威朗普脚底约 660 px，也就是约 60 格**。脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）；站在画布中间（附图 8a、8b 的位置）。鹿角、尾巴全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（雪球、雪花、暴风雪、冰霜光都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/nunu-picture/nunu-A.png`、`nunu-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/nunu-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/nunu_picture_done.zip`。

## 附图（在压缩包 `nunu_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_nunu_idle.png` | 英雄联盟原版努努和威朗普的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_nunu_frontal.png` | 同一帧，正面 | 毛、螺旋纹、鹿角、努努的斗篷 |
| `refs/3_nunu_heads.png` | 两人的头部特写（3/4） | 努努的脸和兜帽；威朗普的眼睛、鼻头、笑嘴、獠牙、耳朵 |
| `refs/4_nunu_back.png` | 同一帧的背后 | 努努的背包、威朗普的背和尾巴 |
| `refs/5_nunu_splash.png` | 官方加载画面 | 气质、颜色、两张脸 |
| `refs/6_nunu_side.png` | 同一帧，侧面朝右 | SA 的角度、尾巴 |
| `refs/7_nunu_run.png` | 跑步的一帧（3/4） | 腿和手臂怎么动（这一步不画，后面用） |
| `refs/8a_layout_nunu.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 在画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_nunu_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/9_style_volibear.png` | 本包的沃利贝尔，8 倍放大，一格 = 一个像素 | **只看风格**：大毛兽的毛、爪子在格子上怎么画 |
| `style/10_style_braum.png` | 本包的布隆（8 倍） | **只看风格**：弗雷尔卓德的冰蓝配色、笑脸 |
| `style/11_style_ornn.png` | 本包的奥恩（8 倍） | **只看风格**：大块头、角、毛 |
| `style/12_style_gnar.png` | 本包的纳尔（8 倍） | **只看风格**：Q 版毛茸茸的小家伙、大眼睛 |

## 提示词：`nunu-A.png` / `nunu-SA.png`（同一段提示词，只换最后一句）

十三张图都附上，顺序同上表。

```text
Thirteen attached images. Images 1-7 are 3D renders and art of ONE character from a game: a BOY RIDING A BIG YETI. THE YETI: a BIG ROUND PALE-BLUE YETI, WHITE FLUFFY LONG FUR on the top of the head, the shoulders and the forearms, BLUE SWIRL MARKINGS on the fur, GLOWING BLUE EYES, a BROWN NOSE, a WIDE GRIN with a row of white teeth and two small tusks, PINK inner ears, DARK BLUE CLAWS, the lower body and legs a deeper blue, a big FLUFFY TAIL behind; a pair of BIG BROWN WOODEN ANTLERS (branching, spreading to both sides) on his head. THE BOY sits ON THE YETI'S HEAD between the antlers, holding on to them: a BLUE FURRY HOOD with two CAT EARS lined pink and a CREAM POMPOM on top, a brown fringe, BIG EYES, a cheeky smile; an ORANGE CAPE with WHITE FUR trim and a BLUE GEM clasp on the chest; brown gloves, brown boots, olive trousers; a brown leather satchel / slingshot on his back. (1 the idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the fur, the swirls, the antlers, the boy's cape; 3 the two heads close-up: the boy's face and hood, the yeti's eyes, nose, grin, tusks and ears; 4 the same from behind: the satchel, the yeti's back and tail; 5 the official illustration: the mood, the colours and both faces; 6 the idle from the side, facing right - the angle of SA, the tail; 7 a running frame - for later.) Images 8a-8b are layout guides: where the character goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 9-12 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a big furry beast's fur and claws on the grid (9), icy blue colours and a happy face (10), a big body with horns and fur (11), a chibi furry little one with big eyes (12).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the antlers, the pompom, the tail); the feet level on one ground line about 146 px above the bottom edge (the grey line of images 8a-8b), standing where the guide shows the character (the centre). The whole character is about 660 px (about 60 squares) from the top of the boy's pompom to the yeti's soles.
PROPORTIONS: chibi. The yeti's HEAD BIG, his body ROUND and broad, his LEGS SHORT and THICK, the two feet apart, planted on the ground; long forearms and big clawed hands; the ANTLERS BIG, spreading to both sides. The boy chibi too (his head with the hood about half of his own height), sitting on top of the yeti's head between the antlers, never covering the yeti's face; the boy takes about the top third of the whole height.
BOTH FACES CLEAR: the boy - skin in 3 shades, TWO EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, one light highlight square), a big grin, the brown fringe; the yeti - TWO GLOWING BLUE EYES (each at least 2x2 squares, the brightest square almost white), the brown nose, a BIG SMILING MOUTH with a row of white teeth and two small tusks.
THE COLOURS: the yeti's fur PALE BLUE in 4 shades (icy almost-white lit, mid blue in the shadows), the lower body and legs DEEP BLUE in 2-3, the long white fur in 2-3 (white, light grey-blue), the swirls bright blue in 1-2, the eyes cyan-white in 2, the nose brown in 2, the inner ears pink in 2, the claws dark blue in 2, the antlers BROWN WOOD in 3-4. The boy: the hood blue in 3, the pompom cream in 2, the cat ears' lining pink in 1-2, the skin in 3, the hair brown in 2, the cape ORANGE in 3-4, the fur trim white in 2, the gem blue in 1-2, the gloves / boots / satchel brown in 3, the trousers olive in 2.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the pale blue fur, the white fur, the deep blue legs, the brown antlers, the boy's blue hood and orange cape clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no snowballs, no snowflakes, no blizzard, no frost glow); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (nunu-A.png): the idle in 3/4 view facing right (images 1, 2 and 8a) - the yeti standing happy and steady, a little hunched, the faces to the front-right; the yeti's NEAR leg and arm on the image left in full tone, the FAR ones on the image right a step darker and a little higher; the boy on his head holding the antlers, grinning.
PICTURE SA (nunu-SA.png): the SAME character as A seen exactly from the SIDE, FACING RIGHT (images 6 and 8b) - both faces to the image right with one eye each visible, the boy on top, the tail behind on the image left, both feet on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，鹿角、毛球、尾巴完整，不出画。
- 威朗普：Q 版大头、圆身子、短粗腿；淡蓝毛 + 白色长毛 + 蓝色螺旋纹；**两只发蓝光的眼睛**、棕鼻头、**大笑嘴带白牙和小獠牙**、粉耳朵、深蓝爪子；棕色大鹿角。
- 努努：坐在威朗普头上、扶着鹿角；蓝兜帽 + 粉猫耳 + 米白毛球；**两只眼睛一样大、一样高**、带高光；橙斗篷白毛边、蓝宝石扣；棕手套靴子背包；**不挡威朗普的脸**。
- A 是 3/4 正面朝右，SA 是正侧面朝右；约 660 px（约 60 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/nunu-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/nunu_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：努努（头一张脸用在所有帧、扔雪球的手臂）、威朗普的头（咬、笑）、两条长手臂和爪子（拍、推雪球）、两条短腿（跑）、尾巴。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | Idle01 / Run01 / Attack01–02 / — / Death01 | 普攻是威朗普用爪子拍 |
| **史上最大雪球！**（W，skill） | Spell2_In / Spell2 / Spell2_Release | 威朗普推着一个越滚越大的雪球冲过去，撞上把敌人击飞（雪球第 3 步另画） |
| **雪球飞射**（E，skill2） | Spell3 / Spell3_Out | 努努在威朗普头上左右开弓连扔雪球；扔完威朗普把被打中的人冻住 |
| **绝对零度**（R，大招） | Channel_Windup / Channel / Spell4 | 两人举手引导一阵暴风雪，最后猛地一砸爆发 |
| **吞噬**（被动里的咬） | Spell1 / Spell1_Swallow | 威朗普一口咬下去，回血 |

连招：**W → E**（雪球把人撞飞，努努接着扔雪球）；**E → R**（扔完禁锢住的人，正好放大招）；**R → 咬**（大招结束，威朗普咬一口回血）。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/nunu/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的打野 / 大块头（沃利贝尔、瑟庄妮没有 → 布隆、奥恩、古拉加斯、沃里克、拉莫斯）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_illaoi_model.py` 的做法），两张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Nunu`（片段名：nunu_idle01、nunu_run01、nunu_attack01、nunu_spell2_in / nunu_spell2 / nunu_spell2_release、nunu_spell3、nunu_channel_windup / nunu_channel、nunu_spell4、nunu_spell1、nunu_death01）；渲染**必须**带 `pack_nunu_picture.py` 的 `SKIN` 参数（藏掉 snowman / claws_long / teeth_big / teeth_smile，威朗普用 Willump_Base 贴图，不然整个是努努的贴图，颜色全错）。加载画面在 WAD 里：`assets/characters/nunu/skins/base/nunuloadscreen.tex`。
