# 解脱者 塞拉斯：第 0 步，先画像素风原图（给 Codex 的提示词）

> 塞拉斯是一个**精瘦结实、赤裸上身的男人**（胸口、肩膀有旧伤疤，近侧肩头有一个暗红色的菱形烙印），**黑色长发往后梳、扎在脑后**，几缕垂到脸旁，**短而整齐的黑胡子**，眉毛浓、眼神凶；脖子上围着一圈**高高的深青灰色围巾 / 领子**，胸前挂着一块**金色的护颈片**和一个**深色的菱形坠子**；下身是**深青绿色的长裤**，腰上一条**宽的棕色皮带**（金属扣，青色的布片垂在扣子两边），小腿裹着灰布，**赤脚**踩着深色的绑带鞋底；两只前臂上是**巨大的禁魔石镣铐**（**白色的石头，像大理石，带金色的边**，比他的拳头还大），镣铐上挂着**金色的大方块锁链**，一直垂到地上。请 Codex 画**两张全身像**（同一个塞拉斯，长相、颜色、**格子大小**都一样），都是 **3/4 正面朝右**（**不画正侧面**），用户从里面挑：
> - **A：英雄联盟里的待机**（附图 1、2、8a）：两腿分开站稳、膝盖微屈，两只戴镣铐的手垂在身体两侧、拳头握着，锁链从镣铐垂到地上，在他脚边和身后拖几节。
> - **B：同样的待机，锁链短一些（更紧凑）**：锁链在每个镣铐上绕一圈，剩下的一截只垂到**膝盖高**，**不碰地**；其余（长相、颜色、镣铐的大小）和 A 一模一样。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的德莱厄斯、格雷福斯和杰斯，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–6）。
> - **比例**：Q 版，**头约占身高的四分之一到三分之一**，脸要大到看得清眼睛和胡子；肩膀宽、胳膊粗，腿短一些；不要细长的写实比例。**镣铐要大**（在原版里是他身上最显眼的东西）。
> - **脸**（附图 3 特写）：**两只眼睛一样大、一样高、都看得见**（每只至少 2 格，眼白 + 深色瞳孔），浓眉，短黑胡子分得出胡子和嘴，皮肤 3 档。
> - **颜色**：皮肤 3–4 档（暖肤色，暗处偏红棕，**不要灰**）；黑发 3 档（亮边偏蓝紫）；围巾 / 领子深青灰 3 档；金色护颈片和锁链 3 档（亮金、金、暗金棕）；**镣铐白色石头 3 档**（白、浅灰、灰，带金边）；长裤深青绿 3 档；皮带棕色 2–3 档。
> - **画布用正方形 1536×1536**。**塞拉斯从头顶到脚底约 748 px，也就是约 68 格**，脚底在离画布底边约 146 px 的地方（附图 8a 的灰线），站在附图 8a 的位置。头发、镣铐、锁链全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（蓝色的魔法闪电、锁链的光、发光都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/sylas-picture/sylas-A.png`、`sylas-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/sylas-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/sylas_picture_done.zip`。

## 附图（在压缩包 `sylas_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_sylas_idle.png` | 英雄联盟原版塞拉斯的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_sylas_frontal.png` | 同一帧，正面 | 围巾、护颈片、皮带、长裤、两只镣铐 |
| `refs/3_sylas_head.png` | 头部特写（3/4） | 头发、脸、胡子、围巾、金色护颈片和菱形坠子 |
| `refs/4_sylas_back.png` | 同一帧的背后 | 扎起来的头发、背、锁链从镣铐垂下来的样子 |
| `refs/5_sylas_splash.png` | 官方加载画面 | 气质、颜色（白色石头镣铐、金色锁链） |
| `refs/6_sylas_attack.png` | 甩锁链普攻的一帧，3/4 朝右 | 镣铐和锁链甩出去的样子 |
| `refs/8a_layout_front.png` | 布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰线）、头顶的高度（浅灰线）；**B 的锁链只到膝盖，不碰地** |
| `style/11_style_darius.png` | 本包的德莱厄斯，8 倍放大，一格 = 一个像素 | **只看风格**：壮汉的身体、胳膊、脸在格子上怎么画 |
| `style/12_style_graves.png` | 本包的格雷福斯（8 倍） | **只看风格**：黑发、胡子、皮肤的分档 |
| `style/13_style_jayce.png` | 本包的杰斯（8 倍） | **只看风格**：金属和石头的高光、描边 |

## 提示词：`sylas-A.png` / `sylas-B.png`（同一段提示词，只换最后一句）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-6 are 3D renders and art of a character from the game: a LEAN, MUSCULAR, BARE-CHESTED MAN (old scars on his chest and shoulders, a dark red diamond-shaped brand on his near shoulder), LONG BLACK HAIR swept back and tied behind his head with a few strands by his face, a SHORT NEAT BLACK BEARD, thick brows and a fierce look; a HIGH DARK TEAL-GREY SCARF / COLLAR wrapped round his neck with a GOLD NECK PLATE on his chest and a dark diamond-shaped pendant; DARK TEAL-GREEN TROUSERS, a WIDE BROWN BELT with a metal buckle and teal cloth flaps, grey cloth wraps on his shins, BARE FEET on dark strapped soles; on BOTH FOREARMS HUGE STONE MANACLES of WHITE MARBLE-LIKE STONE with GOLD TRIM (bigger than his fists), and from each manacle a heavy GOLD CHAIN of big square links hangs down to the ground (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the scarf, the neck plate, the belt, the trousers, both manacles; 3 the head close-up: the hair, the face, the beard, the scarf, the gold neck plate and the pendant; 4 the same from behind: the tied hair, the back, the chains hanging from the manacles; 5 the official illustration: his mood and colours - white stone manacles, gold chains; 6 a chain swing, 3/4 view: the manacles and chains flung out). Image 8a is a layout guide: where he goes on the canvas and how big, the grey line is the ground, the light grey line the top of his head. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a strong man's body, arms and face on the grid (11), black hair, a beard and skin in steps (12), metal and stone with hard highlights (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the hair, both manacles, the whole chains, both feet); his soles level on one ground line about 146 px above the bottom edge (the grey line of image 8a). He is about 748 px (about 68 squares) from the top of his head to his soles and stands where image 8a shows him.
THE VIEW: 3/4 front, FACING RIGHT (image 1) - NOT a side view, NOT a front view; the NEAR side of the body on the image left in full tone, the FAR side a step darker.
PROPORTIONS: chibi - the head between a quarter and a third of his height, the face big enough that both eyes and the beard read clearly; broad shoulders, thick arms, shorter legs; NOT realistic slim proportions. The MANACLES are BIG - the most striking thing on him.
THE FACE: TWO EYES of the SAME size at the SAME height, both visible (each at least 2 squares, white and a dark pupil); thick brows; the short black beard clearly apart from the mouth; the skin in 3 shades.
THE COLOURS: warm skin in 3-4 shades (red-brown shadows, never grey); black hair in 3 shades (blue-violet lit edges); the dark teal-grey scarf in 3 shades; the gold neck plate and the gold chains in 3 shades (bright gold, gold, dark gold-brown); the WHITE STONE MANACLES in 3 shades (white, light grey, grey) with gold trim; the dark teal-green trousers in 3 shades; the brown belt in 2-3 shades.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the skin, the hair and beard, the eyes, the scarf, the gold, the white stone, the trousers and the belt clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no blue magic, no lightning, no glow on the chains), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (sylas-A.png): his idle as in League (images 1, 2 and 8a) - feet apart and planted, knees a little bent, both manacled hands hanging at his sides with the fists closed, the gold chains hanging from the manacles down to the ground and trailing a few links by his feet and behind him.
PICTURE B (sylas-B.png): the SAME Sylas in the same 3/4 view and idle, with the chains SHORTER: each chain wound once round its manacle and the loose end hanging only to KNEE height, never touching the ground, so the whole figure is compact; everything else (look, colours, the size of the manacles, square size) exactly as in A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、镣铐、锁链、脚完整，不出画。
- 两张都是 **3/4 正面朝右**（不是侧面、不是正面）；B 的锁链只到膝盖、不碰地。
- Q 版：头约占身高四分之一到三分之一；**两只眼睛一样大、一样高**；胡子和嘴分得清；**镣铐大、白色石头带金边**；锁链金色。
- 暖色皮肤、黑发、深青灰围巾、金色护颈片、深青绿长裤、棕皮带；两张都是从头顶到脚底约 748 px（约 68 格），脚底在地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 两张都画完后，最后写 `outputs/sylas-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sylas_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/sylas/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_warwick_hd.py` 的做法），和已合并的同类英雄（德莱厄斯、格雷福斯、杰斯）按游戏里的大小并排，PPU 1.2 / 1.5 并排，给用户挑 A 还是 B、定大小。
- 用户 2026-10-20：只做 3/4 正面（不做侧面），动作「Codex 照骨架画关键姿势」（沃里克最后的做法：pack_warwick_poses.py）；一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Sylas`）：普攻 Sylas_Attack_01 / 02（甩链）、被动 Sylas_Attack_Passive（转身甩一圈）、Q Sylas_Spell1_Cast（双手甩出两条链交叉）、W Sylas_Spell2 / Spell2_B（跃起突刺）、E Sylas_Spell3_Dash（冲刺）+ Sylas_Spell3_Bhit_Cast / Spell3_Bhit（甩链拉过去）、R Sylas_Spell4_Cast（甩链偷大招）、跑 Sylas_Run、死亡 Sylas_Death。贴图：镣铐和锁链用 `--submesh-texture gauntlet_left=Shackles_TX_CM ... Sylas_Base_ChainLock_Mat=Chain_Lock_TX`（pack_sylas_picture.SUBTEX）。
