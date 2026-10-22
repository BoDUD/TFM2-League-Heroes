# 海兽祭司 俄洛伊：第 0 步，先画像素风原图（给 Codex 的提示词）

> 俄洛伊是英雄联盟里**海兽之神的女祭司**，扛着一尊**金色神像**，从地里召唤**触手**抽人。这一步把她和触手都画出来，用户从里面挑：
> - **俄洛伊**：一个**高大、肩膀很宽、很结实的女人**，**深棕色皮肤**；**黑头发**在头顶扎成一个**高高的发髻**，上面套着**金环**；**绿色的眼睛**，眉毛浓，表情自信严厉，鼻子上一个**金鼻环**；肩膀、前臂、小腿是**金色带青绿纹样的护甲**（刻着螺旋纹）；胸口裹着**青绿色的布**，腰上一圈**金色腰带**，下面垂着**暗红色的腰布**；**手臂和大腿露在外面，肌肉结实**；脚上是**墨绿色的高靴**。她的**神像**是一个**很大的圆形金色雕刻圆盘**（像一面厚厚的金色大石盘，刻满螺旋花纹，中间一只**发绿光的螺旋眼**），待机时**扛在肩上**，一只手扶着。
> - **触手（被动、W、大招都用）**：一条从地里长出来的**粗触手**，下粗上细，**尖端卷成一个钩**，背上一排**鳍一样的锯齿**，身上刻着**发光的螺旋花纹**，根部是一圈地面裂开的石块。
>
> 请 Codex 画**三张全身像**（**格子大小都一样**），用户从里面挑大小：
> - **A：俄洛伊，英雄联盟里的待机，3/4 正面朝右**（附图 1、2、10a）。
> - **SA：A 的侧面，朝右**（附图 6、10b）。
> - **T：触手，正面**（附图 7、8、10c）。**正对着看画的人**，尖端的钩可以往一边卷，但整体站直、居中。
>
> **为什么触手画正面**：游戏里触手是地面上的特效图，**两边阵营都不会左右翻转**；正对着看画的人，红蓝两边看起来都对。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的奎桑提（深肤色、金色护甲的上单）、乌迪尔（肌肉）、尼菈（海边女战士）和娜美（海洋配色），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–9；附图 5 官方原画看气质和颜色）。
> - **比例**：Q 版。俄洛伊的**头（连发髻）大**，约占身高的三分之一不到一点；身子宽、结实；**腿短一些但粗壮**，两脚分开稳稳站着；**神像要大**（直径约她身高的 40%），扛在**远处的肩膀**上，**不挡脸**。触手：粗壮，下粗上细，尖端卷钩。
> - **俄洛伊的脸**（附图 3 特写）：深棕色皮肤 3 档；**两只绿眼睛一样大、一样高、都看得见**（每只至少 2×2 格，亮绿色，一格亮色高光）；浓眉；嘴紧抿或带一点自信的笑；**金鼻环**一格亮金。
> - **颜色**：皮肤深棕 3–4 档（亮处暖橙棕）；头发黑 2–3 档（亮处深蓝灰）；金色护甲、金环、腰带、神像 金 4 档（暗处橄榄棕，亮处浅黄）；护甲和胸布上的青绿 3 档；腰布暗红 2–3 档；靴子墨绿 3 档；神像的螺旋眼亮绿 2 档。触手：**深海绿 3–4 档**（背上暗、肚子亮青绿），**发光的螺旋花纹浅青绿 1–2 档**，背鳍深一档，根部石块灰褐 2 档。
> - **画布用正方形 1536×1536**。**俄洛伊从发髻最高处到脚底约 640 px，也就是约 58 格；触手从卷钩最高处到根部约 550 px，约 50 格**（格子一样大）。脚底 / 触手根部在离画布底边约 146 px 的地方（附图 10a–10c 的灰线）；站在画布中间（附图 10a–10c 的位置）。神像、卷钩全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（灵魂、光环、冲击波、发光雾都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/illaoi-picture/illaoi-A.png`、`illaoi-SA.png`、`illaoi-T.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/illaoi-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/illaoi_picture_done.zip`。

## 附图（在压缩包 `illaoi_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_illaoi_idle.png` | 英雄联盟原版俄洛伊的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势（神像扛在肩上） |
| `refs/2_illaoi_frontal.png` | 同一帧，正面 | 护甲、胸布、腰带、腰布、靴子 |
| `refs/3_illaoi_head.png` | 头部特写（3/4） | 脸、绿眼睛、眉、鼻环、发髻和金环 |
| `refs/4_illaoi_back.png` | 同一帧的背后 | 背后的头发、神像怎么扛 |
| `refs/5_illaoi_splash.png` | 官方加载画面 | 气质、颜色、脸、触手的颜色 |
| `refs/6_illaoi_side.png` | 同一帧，侧面朝右 | SA 的角度 |
| `refs/7_tentacle_front.png` | 触手，正面 | **T 的角度**、形状（模型贴图偏青，颜色照附图 5 的深海绿） |
| `refs/8_tentacle_34.png` | 触手，3/4 | 粗细、背鳍 |
| `refs/9_tentacle_slam.png` | 触手砸下去（侧面） | 砸地时怎么弯（这一步不画，第 3 步用） |
| `refs/10a_layout_illaoi.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰） |
| `refs/10b_layout_illaoi_side.png` | SA 的布局示意 | 同上，侧面 |
| `refs/10c_layout_tentacle.png` | T 的布局示意 | 同上，触手 |
| `style/11_style_ksante.png` | 本包的奎桑提，8 倍放大，一格 = 一个像素 | **只看风格**：深肤色、金色护甲在格子上怎么画 |
| `style/12_style_udyr.png` | 本包的乌迪尔（8 倍） | **只看风格**：结实的手臂、肌肉分档 |
| `style/13_style_nilah.png` | 本包的尼菈（8 倍） | **只看风格**：Q 版女战士的脸、深肤色 |
| `style/14_style_nami.png` | 本包的娜美（8 倍） | **只看风格**：海洋的青绿配色、鳍 |

## 提示词：`illaoi-A.png` / `illaoi-SA.png` / `illaoi-T.png`（同一段提示词，只换最后一句）

十六张图都附上，顺序同上表。

```text
Sixteen attached images. Images 1-9 are 3D renders and art of a character and her summoned tentacle from a game. THE PRIESTESS (images 1-6): a TALL, BROAD-SHOULDERED, STRONG WOMAN with DARK BROWN SKIN; BLACK HAIR tied in a HIGH BUN with GOLD RINGS; GREEN EYES, thick brows, a confident stern look, a GOLD NOSE RING; GOLD ARMOUR with TEAL carved spiral patterns on the shoulders, the forearms and the shins; a TEAL cloth wrap over the chest, a GOLD belt and a DARK RED loincloth; BARE MUSCULAR ARMS and thighs; DARK GREEN tall boots. Her IDOL is a BIG ROUND CARVED GOLD DISC (thick, like a heavy golden stone wheel covered in spiral carvings, a GLOWING GREEN SPIRAL EYE in the middle), resting on her shoulder in the idle, one hand holding it. THE TENTACLE (images 7-9): a THICK TENTACLE growing out of the ground, thick at the base and thinner up, its TIP CURLED INTO A HOOK, a row of FIN-LIKE SPIKES along its back, GLOWING carved spiral patterns on it, a ring of cracked ground stones at its root. (1 the priestess's idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the armour, the chest wrap, the belt, the loincloth, the boots; 3 her head close-up: the face, the green eyes, the brows, the nose ring, the bun and its gold rings; 4 the same from behind: the hair, how the idol rests; 5 the official illustration: her mood, colours and face, and the tentacles' DEEP SEA-GREEN colour; 6 the idle from the side, facing right - the angle of SA; 7 the tentacle from the FRONT - the angle and shape of T (the render's texture is too cyan: colour it like image 5); 8 the tentacle in 3/4 view - its thickness and fins; 9 the tentacle slamming down, from the side - for later.) Images 10a-10c are layout guides: where the character goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, dark skin and gold armour on the grid (11), strong muscled arms in flat shades (12), a clear chibi woman's face with dark skin (13), sea-green and teal shades and fins (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for all three pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the idol, the bun, the tentacle's hook); the feet / the tentacle's root level on one ground line about 146 px above the bottom edge (the grey line of images 10a-10c), standing where the guide shows the character (the centre). THE PRIESTESS is about 640 px (about 58 squares) from the top of her hair bun to her soles; THE TENTACLE about 550 px (about 50 squares) from the top of its hook to its root.
PROPORTIONS: chibi. The priestess's HEAD with its bun BIG (a little under a third of her height); a broad strong body; LEGS shorter than in the renders but THICK and strong, the two feet apart, planted on the ground; the IDOL BIG (its diameter about 40% of her height), resting on her FAR shoulder, never covering her face. The tentacle: thick and strong, tapering up, the tip curled into a hook.
THE PRIESTESS'S FACE: dark brown skin in 3 shades; TWO GREEN EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, bright green, one light highlight square); thick brows; a firm mouth or a small confident smile; the GOLD NOSE RING one bright gold square.
THE COLOURS: the priestess: the skin dark brown in 3-4 shades (warm orange-brown lit); the hair black in 2-3 (dark blue-grey lit); the gold armour, rings, belt and idol GOLD in 4 shades (olive-brown in the shadows, pale yellow lit); the teal on the armour and chest wrap in 3; the loincloth dark red in 2-3; the boots dark green in 3; the idol's spiral eye bright green in 2. The tentacle: DEEP SEA-GREEN in 3-4 shades (dark on its back, lighter teal-green on its belly), the glowing spiral patterns pale aqua in 1-2, the back fins one shade darker, the root stones grey-brown in 2.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around each character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the dark skin, the black hair, the gold armour, the teal cloth, the red loincloth and the green boots clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no spirits, no auras, no shockwaves, no glowing mist, no sparkles); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (illaoi-A.png): THE PRIESTESS's idle in 3/4 view facing right (images 1, 2 and 10a) - standing proud and steady, the face to the front-right; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker and a little higher; the big gold idol resting on her far shoulder (behind her head on the image left, never over the face), one hand holding it, the other fist on her hip.
PICTURE SA (illaoi-SA.png): the SAME priestess as A seen exactly from the SIDE, FACING RIGHT (images 6 and 10b) - the face to the image right with one eye visible, the bun on top, the idol on her shoulder behind her head, both feet on the ground line.
PICTURE T (illaoi-T.png): THE TENTACLE seen from the FRONT (images 7, 8 and 10c) - facing the viewer, standing up straight out of its root stones in the middle, the tip curled into a hook at the top, the fins along its back showing a little at the sides.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，神像、发髻、触手的卷钩完整，不出画。
- 俄洛伊：Q 版大头（连发髻）；**两只绿眼睛一样大、一样高**、带高光；浓眉、金鼻环；深棕皮肤；黑发高髻带金环；金色带青绿纹的护甲；青绿胸布、金腰带、暗红腰布、墨绿靴子；**手臂结实**；**大金色神像扛在远处的肩上，不挡脸**，中间绿色螺旋眼；两脚分开稳稳站在地上。
- 触手：深海绿（背暗、肚子亮）、浅青色发光螺旋纹、背鳍、尖端卷钩、根部石块。**正面、站直、居中**。
- A 是 3/4 正面朝右，SA 是正侧面朝右，T 是正面；俄洛伊约 640 px（约 58 格），触手约 550 px（约 50 格），脚底 / 根部都在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 三张都画完后，最后写 `outputs/illaoi-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/illaoi_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，三张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：俄洛伊的头（一张脸用在所有帧）、扛神像的手臂和神像（挥、砸）、另一只手臂（扯灵魂）、两条腿（跑、跳）；触手的身子（抬起、砸下）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | Idle1 / Run_base / attack1–3 / — / Death | 普攻是抡神像砸 |
| **严酷训诫**（W，skill） | spell2 / spell2_long | 跃向目标，神像砸下去，附近的触手一起抽 |
| **灵魂试炼**（E，skill2） | Spell3_a / spell3_b | 手往前一伸，把敌人的灵魂扯出来拉到身前（灵魂特效第 3 步另画） |
| **过界信仰**（R，大招） | spell4 | 跳起来把神像砸进地里，周围冒出一圈触手 |
| 触手 出现 / 待机 / 砸下 | Spawn / IdleAngry / Attack1 | 触手只出现在特效里，不单独做成英雄 |

连招：**E → W**（扯出灵魂后跃过去砸，触手一起抽）；**R → W**（大招期间 W 冷却减半，砸完接着跳）；**W → 触手齐抽**（被 W 打中的人，身边所有触手都抽他）。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/illaoi/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的上单（奎桑提、格温、雷克顿、纳尔、沃利贝尔）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）、触手多大、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_ivern_model.py` 的做法：英雄 + 召唤物），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Illaoi`（片段名小写：illaoi_idle1、illaoi_run1、illaoi_attack1、illaoi_spell2、illaoi_spell3_a、illaoi_spell4…；渲染**不要**用 `--hide-submeshes`，会把她整个藏掉）；触手 `--champ IllaoiMinion --wad Illaoi`（片段 illaoiminion_spawn / idleangry / attack1 / death）。加载画面在 WAD 里：`assets/characters/illaoi/skins/base/illaoiloadscreen.tex`。
