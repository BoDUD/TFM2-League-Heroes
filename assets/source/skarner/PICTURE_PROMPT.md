# 上古领主 斯卡纳：第 0 步，先画像素风原图（给 Codex 的提示词）

> 斯卡纳是英雄联盟里**以绪塔尔的上古领主**（2024 年重做后的样子）：一只**巨大的水晶蝎子**，用三根尾巴上的水晶毒刺扎人、拖人，从地里掘出巨石来砸人。这一步画两张，用户从里面挑定样子：
> - **身体**：**又宽又厚的甲壳身体**，青绿 / 深石板蓝色的甲片，甲片表面有浅青色的高光；身上有**橙红色和白色的花纹**（像古老的部族纹样，一道道橙色线条镶白边）；身子下面是**六条弯弯的节肢腿**，腿是深石板色，**脚尖是深紫黑色的钩爪**。
> - **头和脸**：脸在身体**最前面、甲壳的下沿**，是一张**骨白色、像骷髅一样的小脸**，上面有几道橙色纹路，两只**小小的亮青色眼睛**；脸上面罩着一圈**银白色的头甲**（像兜帽，镶橙色条纹）。
> - **钳子**：身前两只**很大的钳子**，深青绿色的大钳，钳口内侧是**骨白色**，上面有橙色和白色的纹。
> - **尾巴**：背后**三根长长的分节尾巴**，一节一节的深青色甲片，从背上往上弯，末端是**三枚大大的青绿色水晶毒刺**，毒刺中间一块**橙红色的核心**、外圈一道浅青高光——这是他的招牌。
>
> 请 Codex 画**两张**（**格子大小一样**，都是 **3/4 正面朝右**），用户从里面挑一张当造型：
> - **A：待机**——英雄联盟里的待机：**六条腿稳稳站着、身子压低**，两只大钳子在身前（近的那只在画面右边伸向前方），**三根尾巴从背上往上、往前弯起来**，毒刺高高翘在头顶上方（附图 1、2、3、9a）。
> - **B：举着巨石**（他的 Q"撼地"）——同样的站姿，**三根尾巴把一块大巨石举在背上 / 头顶**：巨石是**灰绿色的多面体大石头**（几块平面、几道裂缝），毒刺从上面扎住它（附图 6、9b）。**和 A 同样的格子大小**。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 10–13 是本包里的雷克塞、卑尔维斯、塔莉垭和拉莫斯，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、6；附图 5 官方原画看气质和颜色——**三根带青绿水晶毒刺的尾巴、橙色核心、两只大钳子、骨白色骷髅小脸和银白头甲、青绿甲壳上的橙白花纹、六条钩爪腿最重要**）。
> - **比例**：Q 版。**头和脸比原版大很多**（脸要清楚地看得到，不能缩在钳子后面），**钳子和毒刺也画大**；身子短一点、敦实；尾巴还是三根、要分得开，但不要比他整个身子还宽太多。
> - **脸要清楚**（附图 3 特写）：骨白色的脸 3 档；**两只亮青色的眼睛一样高**，每只至少 2×2 格（一格最亮）；脸上两三道橙色纹；银白色头甲压在脸上面，**钳子不能挡住脸**。
> - **颜色**：甲壳 青绿 / 深石板蓝 4 档（一档浅青高光）；花纹 橙红 2–3 档 + 白 2 档；脸和钳口内侧 骨白 / 浅灰 3 档；头甲 银白 3 档；眼睛 亮青 2 档；腿 深石板色 3 档，钩爪 深紫黑 2 档；毒刺 青绿水晶 3–4 档（一档近白的亮面）+ 橙红核心 2–3 档；B 的巨石 灰绿 3–4 档 + 深一档的裂缝。
> - **画布用正方形 1536×1536**。**A：从毒刺最高处到脚底约 484 px，也就是约 44 格**；宽约 42 格（含钳子和尾巴，最多 48 格）。**B：同样的格子大小**，巨石让他更宽一点：宽最多 55 格（附图 9b），高还是约 44 格（巨石顶最多到 47 格）。脚底在离画布底边约 146 px 的地方（附图 9a、9b 的灰线）；站的位置照附图 9a、9b。尾巴、毒刺、钳子、巨石全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（地震波、冲锋、尾巴压制的特效都放到后面单独画；毒刺本身是水晶，可以有亮面，但不要外发光）；不画地面，不画投影。
> - 交付：`outputs/skarner-picture/skarner-A.png`、`skarner-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/skarner-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/skarner_picture_done.zip`。

## 附图（在压缩包 `skarner_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_skarner_idle.png` | 英雄联盟原版斯卡纳的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_skarner_side.png` | 同一帧，正侧面 | 身体长度、六条腿、尾巴怎么从背上弯起来 |
| `refs/3_skarner_head.png` | 脸和钳子特写（3/4） | **骷髅小脸、眼睛、银白头甲**、钳子、前腿 |
| `refs/4_skarner_back.png` | 同一帧的背后 | 三根尾巴的根、背甲 |
| `refs/5_skarner_splash.png` | 官方加载画面 | 气质、颜色、脸、毒刺 |
| `refs/6_skarner_rock.png` | 举着巨石的待机，3/4 朝右 | **B 的姿势**、巨石的样子 |
| `refs/7_skarner_ult.png` | 大招的一帧：三根尾巴往前扎 | 后面用（这一步不画） |
| `refs/8_skarner_attack.png` | 普攻的一帧 | 同上（这一步不画） |
| `refs/9a_layout_idle.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 在画布上的位置、大小、地面线（灰）；浅灰线 = 头顶 |
| `refs/9b_layout_rock.png` | B 的布局示意 | 和 A 同一个比例 |
| `style/10_style_reksai.png` | 本包的雷克塞，8 倍放大，一格 = 一个像素 | **只看风格**：四脚大怪兽、甲壳、Q 版比例 |
| `style/11_style_belveth.png` | 本包的卑尔维斯（8 倍） | **只看风格**：节肢、尖刺、甲片在格子上怎么画 |
| `style/12_style_taliyah.png` | 本包的塔莉垭（8 倍） | **只看风格**：石头的颜色和画法（B 的巨石） |
| `style/13_style_rammus.png` | 本包的拉莫斯（8 倍） | **只看风格**：小个子甲壳兽、壳的高光 |

## 提示词：`skarner-A.png` / `skarner-B.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-8 are 3D renders and art of ONE character from a game: a HUGE CRYSTAL SCORPION. A broad, thick ARMOURED BODY of TEAL-GREEN / DARK SLATE-BLUE carapace plates with pale teal highlights, covered in ancient tribal markings: ORANGE-RED LINES edged with WHITE; SIX CURVED JOINTED LEGS underneath, dark slate, ending in DARK PURPLE-BLACK HOOKED CLAWS. The face sits at the very FRONT of the body, under the lower edge of the carapace: a small BONE-WHITE, SKULL-LIKE FACE with a few orange markings and two small BRIGHT CYAN EYES, under a SILVER-WHITE HEAD PLATE like a hood with orange stripes. Two BIG PINCERS in front of him, dark teal, bone-white on the inner side of the jaws, with orange and white markings. THREE LONG SEGMENTED TAILS rise from his back, plate after plate of dark teal armour, curving up and forward, each ending in a BIG TEAL CRYSTAL STINGER with an ORANGE-RED CORE and a pale teal rim - his signature. (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the side: the body length, the six legs, how the tails curve up from the back; 3 his face and pincer close-up: the skull face, eyes, the silver head plate, the pincers, the front legs; 4 the same from behind: the roots of the three tails, the back plates; 5 the official illustration: the mood, the colours, the face, the stingers; 6 the same idle holding a big boulder up in his three tails - the pose of B and the look of the boulder; 7 his ult, the tails stabbing forward and 8 an attack - both for later.) Images 9a-9b are layout guides: where the figure goes on the canvas and how big, the grey line is the ground, the light line the top of the figure. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 10-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, chibi proportions for a big four-legged armoured beast (10), jointed legs, spikes and plates on the grid (11), how stone is drawn (12, for the boulder), a small armoured shell creature and its shell highlights (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the tails, the stingers, the pincers, the boulder); the feet level on one ground line about 146 px above the bottom edge (the grey line of images 9a-9b), standing where the guide shows the figure. In picture A he is about 484 px (about 44 squares) from the top of the highest stinger to his feet and about 42 squares wide (never more than 48, with the pincers and the tails); in picture B, at the same square size, he is about as tall (the boulder's top at most 47 squares above the feet) and at most 55 squares wide.
PROPORTIONS: chibi. His FACE AND HEAD PLATE MUCH BIGGER than in the renders so the face reads clearly and is never hidden behind the pincers; the pincers and the stingers big too; a shorter, stocky body; still THREE tails, clearly apart from each other, but never much wider than his body.
FACE CLEAR: the bone-white face in 3 shades; TWO BRIGHT CYAN EYES at the SAME height, each at least 2x2 squares with one brightest square; two or three orange marks on the face; the silver-white head plate over it; the pincers never over the face.
THE COLOURS: the carapace teal-green / dark slate-blue in 4 (one pale teal highlight); the markings orange-red in 2-3 plus white in 2; the face and the pincers' inner jaws bone-white / light grey in 3; the head plate silver-white in 3; the eyes bright cyan in 2; the legs dark slate in 3 with dark purple-black claws in 2; the stingers teal crystal in 3-4 (one near-white bright face) with orange-red cores in 2-3; in B the boulder grey-green in 3-4 with cracks one shade darker. Every pixel fully opaque.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: his teal carapace, orange markings, bone-white face, dark legs and crystal stingers clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing (the crystals' highlights are bright squares, not a halo).
No spell effects (no shockwave, no dust, no charge trail, no glow); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (skarner-A.png): his idle in 3/4 view facing right (images 1, 2, 3 and 9a) - standing low and steady on his six legs, the two big pincers in front of him (the near one on the image right reaching forward), the three tails curving up and forward from his back with the stingers held high above his head; the near legs and pincer in full tone, the far ones a step darker.
PICTURE B (skarner-B.png): the same idle in 3/4 view facing right (images 6 and 9b) - his three tails holding a BIG BOULDER up on his back above his head, the stingers gripping it from above; the boulder a faceted grey-green rock with a few flat faces and cracks; at the SAME square size as picture A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，尾巴、毒刺、钳子、巨石完整，不出画。
- Q 版，**脸比原版大很多**、清楚；**骨白骷髅小脸 + 银白头甲**；**两只亮青眼睛一样高**；**两只大钳子**；**三根分节尾巴 + 青绿水晶毒刺 + 橙色核心**；**青绿甲壳上的橙白花纹**；**六条腿、深紫黑钩爪**。
- A 约 484 px（约 44 格）高、宽约 42 格；B 和 A 同样的格子大小，尾巴举着巨石，宽最多 55 格；都是 3/4 正面朝右；脚底在地面线上。
- 没有技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/skarner-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/skarner_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧后面会按英雄联盟的动作做（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：一张脸用在所有帧、两只钳子、三根尾巴（每根能单独弯）、六条腿、巨石。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 | Idlebase / Runbase / BaseAttack1、BaseAttack2 | 普攻是钳子夹 + 尾巴扎；举着巨石时有 _Rock 版本 |
| **撼地 / 擎天**（Q） | Spell1_Pickup（掘石）、Spell1_Toss（扔石） | 用尾巴从地里掘出巨石举着，再扔出去 |
| **震地壁垒**（W） | Spell2 | 一跺，护盾 + 一圈地震波 |
| **以绪塔尔冲击**（E） | Spell3_Startup / Spell3_Run / Spell3_Grab | 往前冲锋，撞到人就夹着拖走、撞墙晕眩 |
| **毒刺贯体**（R） | Spell4_Hit1 / Spell4_channel | 三根尾巴往前扎、把人压制着拖走 |
| 死亡 | Death | |

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/skarner/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿），和已合并的大块头（雷克塞、卑尔维斯、拉莫斯、特朗德尔、瑟庄妮）按游戏里的大小并排，给用户定大小、PPU。
- 渲染：`pose_ref.py --champ Skarner --fit-all`；巨石是皮肤里的 `Stone` 子网格，平时藏着（A 用 `--hide-submeshes`），举石的帧用 `--submesh-texture Stone=Props`。加载画面：`assets/characters/skarner/skins/base/skarnerloadscreen_0.tex`。动作：`tools/lol/anim_graph.py Skarner`（举石的待机 / 跑 / 普攻是 `*_Rock` 片段，Q 是 `spell1` = Spell1_Pickup_v2 / Spell1_Pickup_Moving）。
