# 战争女族长 安蓓萨：第 0 步，先画像素风原图（给 Codex 的提示词）

> 安蓓萨是英雄联盟里**诺克萨斯的女军阀**（梅尔的母亲）：一个**又高又壮、肩膀很宽的女战士**，**深棕色皮肤**，**很短的浅色（银白）头发**，**表情冷峻**、下巴抬着，像一个习惯发号施令的将军；全身**深色的重甲**（黑 / 深铁灰的甲片），配**深红色的布**和**金色 / 铜色的镶边**；两只手各拿一把**又宽又长的大刀**，刀后面连着**铁链**（她的 E 技能就是抡铁链）。**具体的甲片、刀和铁链的形状、颜色照附图 1–5 画——文字和附图不一样的地方，以附图为准。**
>
> 请 Codex 画**两张全身像**（**格子大小一样**），用户从里面挑大小：
> - **A：安蓓萨，英雄联盟里的待机，3/4 正面朝右**（附图 1、2、3、9a）。
> - **SA：A 的侧面，朝右**（附图 6、9b）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的德莱厄斯（诺克萨斯的重甲和深红）、俄洛伊（高大结实的深肤色女战士）、锐雯（诺克萨斯女剑士、大刀）、奎桑提（深肤色、重甲），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–8；附图 5 官方原画看气质和颜色——**深棕色皮肤、很短的浅色头发、冷峻的脸、深色重甲加深红布和金边、两把大刀和铁链最重要**）。
> - **比例**：Q 版。**头大**（约占身高的三分之一不到一点），脸朝右前方；身子**宽、结实**，肩膀宽；**腿短一些但粗壮**，两脚分开稳稳站着；**两把刀要大**（刀身大约她身高的一半），握在两只手里、刀尖朝下或斜向下，**不挡脸**；铁链从刀柄垂下来、绕在小臂上，画成几格一节的粗链，不要细到看不清。
> - **脸要清楚**（附图 3 特写）：深棕色皮肤 3 档；**两只眼睛一样大、一样高、都看得见**（每只至少 2×2 格，一格亮色高光）；眉毛压得低、眼神锐利；嘴紧抿，嘴角往下；颧骨高；浅色短发在头顶，不遮眼睛。
> - **颜色**：皮肤 深棕 3–4 档（亮处暖橙棕）；头发 浅银白 2–3 档（暗处浅灰紫）；眼睛 深色 + 一格高光；重甲 黑 / 深铁灰 3–4 档 + 一档亮边；布 深红 3 档；镶边 金 / 铜 3 档；两把刀 钢灰 3–4 档 + 一格亮刃（刀身上有颜色的地方照附图）；铁链 深铁灰 2–3 档；靴子 黑 2–3 档。
> - **画布用正方形 1536×1536**。**从最高处（头顶，或高过头的肩甲 / 刀，哪个高算哪个）到脚底约 640 px，也就是约 58 格**；宽最多 50 格（含两把刀）。脚底在离画布底边约 146 px 的地方（附图 9a、9b 的灰线）；站在画布中间（附图 9a、9b 的位置）。刀、铁链、肩甲全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（刀光、冲刺的残影、冲击波、铁链甩出的弧线都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/ambessa-picture/ambessa-A.png`、`ambessa-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/ambessa-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/ambessa_picture_done.zip`。

## 附图（在压缩包 `ambessa_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_ambessa_idle.png` | 英雄联盟原版安蓓萨的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_ambessa_frontal.png` | 同一帧，正面 | 胸甲、腰、布、腿甲、靴子 |
| `refs/3_ambessa_head.png` | 头部和肩甲特写（3/4） | **脸、眼睛、短发**；肩甲 |
| `refs/4_ambessa_back.png` | 同一帧的背后 | 背后的甲和布、刀和铁链从背后看 |
| `refs/5_ambessa_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/6_ambessa_side.png` | 同一帧，侧面朝右 | SA 的角度 |
| `refs/7_ambessa_q.png` | Q 横扫的一帧 | 刀挥起来的样子（这一步不画动作，后面用） |
| `refs/8_ambessa_e.png` | E 抡铁链的一帧 | 同上（这一步不画） |
| `refs/9a_layout_ambessa.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰）；浅灰线 = 最高处 |
| `refs/9b_layout_ambessa_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/10_style_darius.png` | 本包的德莱厄斯，8 倍放大，一格 = 一个像素 | **只看风格**：诺克萨斯的重甲、深红布、金边在格子上怎么画 |
| `style/11_style_illaoi.png` | 本包的俄洛伊（8 倍） | **只看风格**：高大结实的深肤色女战士、Q 版的脸 |
| `style/12_style_riven.png` | 本包的锐雯（8 倍） | **只看风格**：诺克萨斯女剑士、大刀在格子上怎么画 |
| `style/13_style_ksante.png` | 本包的奎桑提（8 倍） | **只看风格**：深肤色、宽肩膀、重甲 |

## 提示词：`ambessa-A.png` / `ambessa-SA.png`（同一段提示词，只换最后一句）

十五张图都附上，顺序同上表。

```text
Fifteen attached images. Images 1-8 are 3D renders and art of ONE character from a game: a TALL, BROAD-SHOULDERED, MUSCULAR WARLORD WOMAN with DARK BROWN SKIN and VERY SHORT PALE (silver-white) HAIR, a stern commanding face with high cheekbones, her chin up; HEAVY DARK PLATE ARMOUR (black / dark iron-grey plates) with DEEP CRIMSON cloth and GOLD / BRONZE trim; in each hand a BIG, BROAD, LONG BLADE, with IRON CHAINS trailing from the blades and wrapped round her forearms. The renders are the authority: copy the exact shapes and colours of her armour, her blades and her chains from images 1-5 wherever this text and the images differ. (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the breastplate, the waist, the cloth, the leg plates, the boots; 3 her head and shoulders close-up: the FACE, the eyes, the short hair, the pauldrons; 4 the same from behind: the back plates and cloth, the blades and chains from behind; 5 the official illustration: her mood, her colours and her face; 6 the idle from the side, facing right - the angle of SA; 7 a blade sweep and 8 a chain lash - both for later.) Images 9a-9b are layout guides: where she goes on the canvas and how big, the grey line is the ground, the light line the top of the figure. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions; dark heavy armour with crimson cloth and gold trim on the grid (10), a tall strong dark-skinned woman warrior and her chibi face (11), a woman with a big blade on the grid (12), dark skin and broad armoured shoulders (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the blades, the chains, the pauldrons); the feet level on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing where the guide shows her (the centre). She is about 640 px (about 58 squares) from her highest point (the top of her head, or a pauldron or blade above it) to her soles, and never more than 50 squares wide with both blades.
PROPORTIONS: chibi. Her HEAD BIG (a little under a third of her height), the face turned to the front-right; a broad, strong body with wide shoulders; LEGS shorter than in the renders but THICK and strong, the two feet apart, planted on the ground; the TWO BLADES BIG (each blade about half her height), one in each hand, points down or angled down, never covering her face; the chains hanging from the blades and wrapped round her forearms, drawn as THICK links a few squares each, never thinner than one square.
HER FACE: dark brown skin in 3 shades; TWO EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, dark with one light highlight square); low brows, a sharp gaze; a firm mouth with downturned corners; high cheekbones; the short pale hair on top, never over the eyes.
THE COLOURS: the skin dark brown in 3-4 shades (warm orange-brown lit); the hair pale silver-white in 2-3 (pale grey-violet in the shadow); the eyes dark with one highlight square; the armour black / dark iron-grey in 3-4 with one lighter edge shade; the cloth deep crimson in 3; the trim gold / bronze in 3; the blades steel grey in 3-4 with one bright edge square (any colour on the blades as in images 1-5); the chains dark iron in 2-3; the boots black in 2-3. Every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around her; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark skin, the pale hair, the dark armour, the crimson cloth, the gold trim and the steel blades clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no blade trails, no dash afterimages, no shockwaves, no chain arcs, no sparks); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (ambessa-A.png): her idle in 3/4 view facing right (images 1, 2, 3 and 9a) - standing tall and steady like a general, the face to the front-right; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker and a little higher; a blade in each hand as in image 1, the chains hanging from them.
PICTURE SA (ambessa-SA.png): the SAME woman as A seen exactly from the SIDE, FACING RIGHT (images 6 and 9b) - the face to the image right with one eye visible, the near blade in front of her body, the far one a step darker behind it, both feet on the ground line.
```

## 没有附图 1–8 时：压缩包 `ambessa_pack0_noref.zip`（只有布局示意和风格图）

云端会话连不上英雄联盟的资源站，没法渲染她的模型，这个包只有 6 张图：`refs/9a_layout_ambessa.png`、`refs/9b_layout_ambessa_side.png`（灰框 = 她大约占的位置和大小，灰线 = 地面，浅灰线 = 最高处）和 `style/10–13`。**如果你能查图，先找几张她在英雄联盟里的游戏模型 / 官方原画看清楚样子**（重甲的形状、两把刀和铁链），再照下面的提示词画；查不到就按文字画。

```text
Six attached images. Images 9a-9b are layout guides: the grey box is where she stands on the canvas and about how big she is, the grey line is the ground, the light line the top of the figure. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions; dark heavy armour with crimson cloth and gold trim on the grid (10), a tall strong dark-skinned woman warrior and her chibi face (11), a woman with a big blade on the grid (12), dark skin and broad armoured shoulders (13).
THE CHARACTER (no render attached - if you can look up pictures, look up the Noxian warlord Ambessa Medarda from the game League of Legends first and follow her in-game model and official art; otherwise follow this text): a TALL, BROAD-SHOULDERED, MUSCULAR WARLORD WOMAN in her fifties, DARK BROWN SKIN, VERY SHORT PALE (silver-white) HAIR, a stern commanding face with high cheekbones, her chin up; HEAVY DARK PLATE ARMOUR (black / dark iron-grey plates, big layered pauldrons) with DEEP CRIMSON cloth and GOLD / BRONZE trim; in each hand a BIG, BROAD, LONG BLADE, with IRON CHAINS trailing from the blades and wrapped round her forearms.
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the blades, the chains, the pauldrons); the feet level on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing in the centre where the guide's box is. She is about 640 px (about 58 squares) from her highest point (the top of her head, or a pauldron or blade above it) to her soles, and never more than 50 squares wide with both blades.
PROPORTIONS: chibi. Her HEAD BIG (a little under a third of her height), the face turned to the front-right; a broad, strong body with wide shoulders; LEGS short but THICK and strong, the two feet apart, planted on the ground; the TWO BLADES BIG (each blade about half her height), one in each hand, points down or angled down, never covering her face; the chains hanging from the blades and wrapped round her forearms, drawn as THICK links a few squares each, never thinner than one square.
HER FACE: dark brown skin in 3 shades; TWO EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, dark with one light highlight square); low brows, a sharp gaze; a firm mouth with downturned corners; high cheekbones; the short pale hair on top, never over the eyes.
THE COLOURS: the skin dark brown in 3-4 shades (warm orange-brown lit); the hair pale silver-white in 2-3 (pale grey-violet in the shadow); the eyes dark with one highlight square; the armour black / dark iron-grey in 3-4 with one lighter edge shade; the cloth deep crimson in 3; the trim gold / bronze in 3; the blades steel grey in 3-4 with one bright edge square; the chains dark iron in 2-3; the boots black in 2-3. Every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around her; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark skin, the pale hair, the dark armour, the crimson cloth, the gold trim and the steel blades clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no blade trails, no dash afterimages, no shockwaves, no chain arcs, no sparks); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (ambessa-A.png): her idle in 3/4 view facing right (image 9a) - standing tall and steady like a general, the face to the front-right; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker and a little higher; a blade in each hand, points down, the chains hanging from them.
PICTURE SA (ambessa-SA.png): the SAME woman as A seen exactly from the SIDE, FACING RIGHT (image 9b) - the face to the image right with one eye visible, the near blade in front of her body, the far one a step darker behind it, both feet on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，两把刀、铁链、肩甲完整，不出画。
- 安蓓萨：Q 版大头；**两只眼睛一样大、一样高**、带高光；深棕色皮肤；**很短的浅色头发**；冷峻的脸；**深色重甲 + 深红布 + 金边**（照附图）；**两只手各一把大刀**、刀后拖着**粗铁链**绕在小臂上；两脚分开稳稳站在地上。
- A 是 3/4 正面朝右，SA 是正侧面朝右；约 640 px（约 58 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/ambessa-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ambessa_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：头（一张脸用在所有帧）、两条拿刀的胳膊和两把刀（横扫、砸地、交叉格挡）、铁链（甩）、两条腿（冲刺、跳）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | idle / run / attack1–3 / — / death | 普攻是双刀交替砍 |
| **龙犬之步**（被动） | 每个技能之后 | 每放一个技能就朝目标冲一小步，下一刀更快更重 |
| **狡诈横扫 → 裂地重击**（Q，skill） | spell1 / spell1 第二段 | 先双刀往前扫半圈，扫中人后接一刀竖着劈下去的直线重击 |
| **割裂**（E，skill2） | spell3 | 原地抡铁链转一圈，冲刺后再抡一圈 |
| **拒斥**（W，自动） | spell2 | 双刀交叉护在身前挡一下（护盾），然后砸地 |
| **公开处决**（R，大招） | spell4 | 闪到敌人身边把他按住，再狠狠砸进地里 |

连招：**Q 扫中 → 裂地重击**（英雄联盟的第二段）；**每个技能 → 冲一步 → 强化普攻**；**E → 冲一步 → 再抡一圈**；**R 砸中 → 马上 Q 两段**；**R → 拒斥就绪**。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/ambessa/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和已合并的上单（俄洛伊、奎桑提、德莱厄斯、锐雯、约里克）按游戏里的大小并排，PPU 1.5 / 1.75 / 2.0 并排，给用户定大小、PPU。
- 渲染：`pose_ref.py --champ Ambessa`，片段名、子网格和贴图在 `assets/source/ambessa/lol_names.txt`（打包脚本在用户本机跑时写的）；都加 `--fit-all`。动作：`tools/lol/anim_graph.py Ambessa`。
