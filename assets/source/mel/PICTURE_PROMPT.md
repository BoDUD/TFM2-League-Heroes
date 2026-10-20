# 流光镜影 梅尔：第 0 步，先画像素风原图（给 Codex 的提示词）

> 梅尔是一位**高挑优雅的诺克萨斯贵族女法师**：**深棕色的皮肤**；**黑色卷发盘成高高的发髻**（头顶一大团卷发，几缕卷发垂在两鬓），发髻上插着**金色的发饰**，额头上一个小小的**金色额饰**；耳朵上一对**很大的金色圆耳环**，脖子上一圈**金色的项圈**；身上是**青绿色（墨绿偏青）的紧身连体衣**，胸口和腰上是**银白色的尖角护甲片**，肩膀上一对**青绿色带银边的小肩甲**；外面披一件**深红色的长袍**：袍子里面是**金色的衬里**，边上一道**深蓝黑色的滚边**，**袖子是又宽又长的喇叭袖**（外面红、里面金）；腿上是青绿色的紧身裤，脚上是**银青色的高跟鞋**。她的待机：**一只手叉在腰上，另一只手臂向前伸出、手心朝上**（像在托着一团光——光不要画，放到第 3 步特效里）。请 Codex 画**两张全身像**（同一个梅尔，长相、颜色、**格子大小**都一样），都是 **3/4 正面朝右**（**不画正侧面**），用户从里面挑：
> - **A：英雄联盟里的待机，长袍拖地**（附图 1、2、8a）：袍子从腰后垂下来，**在地上铺成一条拖尾**（往她身后、画面左边铺开，拖尾**最多比她的身体宽出半个身高**，不要铺满画布）。
> - **B：同样的待机，袍子收短（Q 版）**：袍子只到**脚踝上面一点**，**不拖地**，袖子也收窄一些，整个人更紧凑，看得见两条腿和高跟鞋。长相、颜色和 A 一模一样。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的婕拉、乐芙兰和莫甘娜（都是女法师），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–6）。
> - **比例**：Q 版，**头大**（头连发髻约占身高的三分之一，脸本身清楚），身子短，腿还是细长一点（她是高挑的贵族女子），不要写实的八头身。
> - **脸**（附图 3 特写）：深棕色的小脸，**两只眼睛一样大、一样高、都看得见**（每只至少 2×2 格，眼白 + 深棕色的瞳孔，带一格高光），细细的眉毛，深色的嘴唇；金色的额饰和大耳环要清楚。
> - **颜色**：深棕色皮肤 3 档（亮处偏暖，**不要一团黑**），黑色头发 3 档（亮边偏深棕，不要一团黑），金色（发饰、耳环、项圈、袍子衬里）3 档，青绿色连体衣 3–4 档，银白护甲 2–3 档，深红长袍 3–4 档，深蓝黑滚边 2 档，银青高跟鞋 2–3 档。
> - **画布用正方形 1536×1536**。**梅尔从发髻顶端到脚底约 726 px，也就是约 66 格**，脚底在离画布底边约 146 px 的地方（附图 8a 的灰线），站在附图 8a 的位置。发髻、伸出去的手、袖子、拖尾全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（手上的光、金色的飞弹、屏障都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/mel-picture/mel-A.png`、`mel-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/mel-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/mel_picture_done.zip`。

## 附图（在压缩包 `mel_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_mel_idle.png` | 英雄联盟原版梅尔的待机，3/4 朝右 | 颜色、形状、**角度**、待机姿势 |
| `refs/2_mel_frontal.png` | 同一帧，正面 | 连体衣、护甲片、袍子、腿 |
| `refs/3_mel_head.png` | 头部特写（3/4） | 发髻、发饰、额饰、脸、耳环、项圈、肩甲 |
| `refs/4_mel_back.png` | 同一帧的背后 | 袍子背面、发髻背面 |
| `refs/5_mel_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_mel_cast.png` | 施法的一帧，3/4 朝右 | 喇叭袖和伸出去的手 |
| `refs/8a_layout_front.png` | 布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰线）、发髻顶端的高度（浅灰线）；**示意图里拖尾很宽，A 的拖尾最多比身体宽出半个身高，B 不拖地** |
| `style/11_style_zyra.png` | 本包的婕拉，8 倍放大，一格 = 一个像素 | **只看风格**：女法师的脸、眼睛、头发在格子上怎么画 |
| `style/12_style_leblanc.png` | 本包的乐芙兰（8 倍） | **只看风格**：贵族长袍、金色装饰 |
| `style/13_style_morgana.png` | 本包的莫甘娜（8 倍） | **只看风格**：长袍、袖子、深色皮肤和头发的亮边 |

## 提示词：`mel-A.png` / `mel-B.png`（同一段提示词，只换最后一句）

十张图都附上，顺序同上表。

```text
Ten attached images. Images 1-6 are 3D renders and art of a character from the game: a TALL ELEGANT NOBLEWOMAN MAGE with DEEP BROWN SKIN; BLACK CURLY HAIR in a HIGH UPDO (a big bun of curls on top, a few curls at the temples) with GOLD hair ornaments and a small GOLD forehead piece; LARGE GOLD HOOP EARRINGS and a GOLD COLLAR; a fitted TEAL-GREEN BODYSUIT with pointed SILVER-WHITE ARMOUR PLATES on the chest and waist, small teal shoulder pieces with silver edges; over it a long CRIMSON-RED OPEN ROBE with a GOLD LINING and a DARK NAVY-BLACK HEM, its sleeves WIDE LONG BELL SLEEVES (red outside, gold inside); teal leggings and SILVER-TEAL HIGH HEELS (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose; 2 the same from the front: the bodysuit, the plates, the robe, the legs; 3 the head close-up: the updo, the ornaments, the face, the earrings, the collar, the shoulder pieces; 4 the same from behind: the robe's back and the bun; 5 the official illustration: her mood and colours; 6 a casting pose, 3/4 view: the bell sleeves and the reaching hand). Image 8a is a layout guide: where she goes on the canvas and how big, the grey line is the ground, the light grey line the top of the bun; in it the train of the robe spreads very wide - see the last sentence for how long it is in your picture. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a woman mage's face, eyes and hair on the grid (11), a noble robe with gold trim (12), a long robe and sleeves, dark skin and hair with lit edges (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the bun, the reaching hand, both sleeves, the robe, both feet); her soles level on one ground line about 146 px above the bottom edge (the grey line of image 8a). She is about 726 px (about 66 squares) from the top of the bun to her soles and stands where image 8a shows her.
THE VIEW: 3/4 front, FACING RIGHT (image 1) - NOT a side view, NOT a front view; the NEAR side of the body on the image left in full tone, the FAR side a step darker.
THE POSE: her idle (image 1): one hand on her hip, the other arm reaching forward to the right with the palm up (as if holding a light - draw NO light), standing tall with the feet close together.
PROPORTIONS: chibi - the head with the updo about a THIRD of her height, a clear face; a short body; the legs still a little long and slim (she is a tall noblewoman); NOT realistic slim proportions.
THE FACE: small, deep brown; TWO EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares: white with a dark brown iris and one highlight square), thin brows, dark lips; the gold forehead piece and the big gold hoop earrings clearly readable.
THE COLOURS: the deep brown skin in 3 shades (warm light side, never one black mass); the black hair in 3 shades (dark brown lit edges, never one black mass); gold (ornaments, earrings, collar, the robe's lining) in 3 shades; the teal-green bodysuit in 3-4 shades; the silver-white plates in 2-3 shades; the crimson robe in 3-4 shades; the navy-black hem in 2 shades; the silver-teal heels in 2-3 shades.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around her; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the skin, the hair, the gold, the teal bodysuit, the silver plates, the red robe, the navy hem and the heels clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no light in her hand, no golden bolts, no barrier, no glow), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (mel-A.png): her idle as in League (images 1, 2 and 8a) - the robe falls from her waist and lies on the ground as a TRAIN spreading back behind her (to the image left); the train reaches at most HALF her height beyond her body, it does not fill the canvas.
PICTURE B (mel-B.png): the SAME Mel in 3/4 view facing right, the robe made SHORTER: it ends a little ABOVE THE ANKLES and does NOT touch the ground, the bell sleeves a little narrower, so the whole figure is more compact and both legs and the heels show; everything else (look, colours, square size, the pose) exactly as in A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，发髻、手、袖子、袍子、脚完整，不出画。
- 两张都是 **3/4 正面朝右**（不是侧面、不是正面）；一只手叉腰、一只手向前伸、手心朝上，**手上不画光**。
- Q 版：头连发髻约占身高三分之一；**两只眼睛一样大、一样高**；金色额饰、大耳环看得清。
- 深棕色皮肤（不是一团黑）、黑发（有亮边）、金饰、青绿连体衣、银白护甲、深红长袍（金衬里、深蓝黑滚边）、银青高跟鞋；两张都是从发髻顶端到脚底约 726 px（约 66 格），脚底在地面线上。
- A 的拖尾最多比身体宽出半个身高；B 的袍子到脚踝上面、不拖地。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- 两张都画完后，最后写 `outputs/mel-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/mel_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/mel/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_warwick_hd.py` 的做法），和已合并的女法师（婕拉、乐芙兰、莫甘娜）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑 A 还是 B、定大小（PPU 不要超过 1.5），再问动作是我自己照英雄联盟摆，还是 Codex 照骨架画关键姿势。
- 用户 2026-10-20：只做 3/4 正面（不做侧面）——第 1 步只在游戏格子上画 3/4 正面，动作都在 3/4 的造型上摆；一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Mel`）：普攻 Attack1 / Attack2-new / Attack1Emp（灼灼之光的强化普攻）、Q Spell1（耀光齐射）、W Spell2（灵魂折镜）、E Spell3（阳炎涡旋）、R Spell4（鎏金蚀日）、跑 Run（移速 395 以上 Run_Fast）、死亡 Death。渲染时她的贴图要 `--submesh-texture Body=Mel_Base_TX_CM --submesh-texture Sleeve=Mel_Base_TX_CM --submesh-texture Dress=Mel_Base_TX_CM`（否则拿到的是白色的 DressMask）。
