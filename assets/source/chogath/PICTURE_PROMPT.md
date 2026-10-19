# 虚空恐惧 科加斯：第 0 步，先画像素风原图（给 Codex 的提示词）

> 科加斯是虚空里爬出来的**巨兽**：**四肢着地**，身体披着**深紫色的甲壳**，甲壳的边缘和底面是**深红 / 酒红色**，接缝里透出一点红光。**头又大又低、往前探**，几乎贴着地：宽大的嘴、两排**白色的尖牙**、嘴里一条**紫色的舌头**（舌尖带一点青白色的虚空光）、两只**发青色光的小眼睛**、下巴两边一对**弯曲的红色獠牙**；头顶和后脑是层层的**酒红色甲片**。**两只粗壮的前爪**撑在地上、**两条短粗的后腿**，爪尖都是**红色的钩爪**。最显眼的是从肩膀长出来的**两条细长的上臂**，像**镰刀**一样高高举在背上，末端各是一把**长长的红色刃爪**。背上一排**紫色的骨刺**，身后拖着一条**长长的、分节的甲壳尾巴**，尾尖是**红色的尖刺**。请 Codex 画**两张全身像**（同一只科加斯，长相、颜色、**格子大小**都一样），用户从里面挑一张做游戏里的待机：
> - **A：英雄联盟里的待机**（附图 1、2、8a）。四肢着地、身子压低，**两条镰刀上臂高高举在背上**，头低低地往前探、张着嘴；尾巴拖在身后。
> - **B：收着上臂的备战姿势**（附图 8b 只看大小和地面线）。同样四肢着地，**两条镰刀上臂往后收、贴着肩膀和背**（不举起来，刃爪朝后），头稍微抬一点、张嘴；**尾巴往身体收近一些**，不要拖得很长。整个身子比 A 横向窄、上面矮。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的雷克塞、沃利贝尔、卡兹克和内瑟斯（雷克塞、卡兹克同是虚空生物），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–4、7）。
> - **比例**：他是**巨大的野兽，不要画成大头娃娃**，也不要画成站起来的人形：**四肢着地**，身体是一个**宽厚、压低的甲壳躯干**；头大但不夸张（约占身长的四分之一）；前爪粗、后腿短。
> - **头**（附图 3 特写）：酒红色的甲片头冠，张开的大嘴里两排白色尖牙（牙要一颗颗看得清）、紫色舌头；**两只青色的眼睛一样大、都看得见**（平涂的亮青色，不要柔光），眼神凶；下巴两边的红色弯獠牙。
> - **颜色**：甲壳主体是**深紫 / 紫罗兰色**（3–4 档），甲片的边、头冠、爪子、镰刀刃、尾尖是**深红 / 酒红色**（3–4 档），两种颜色分得清，**不要渐变**，用平涂的色块。深紫的腿和尾巴一定要有**偏亮的边**，不然在深色背景上会糊成一团。
> - **发光的部分**：眼睛、舌尖的虚空光、甲壳接缝里的红光，用平涂的亮色，不要柔光。
> - **姿势**：3/4 正面朝右（头在画面右边、脸朝右前方，尾巴在画面左边）。**近侧的前爪、后腿和镰刀臂在画面左前、颜色亮；远侧的在后面、稍暗**。四只脚落在同一条地面线上。
> - **画布用正方形 1536×1536**。**从最高点（A 是举起的镰刀刃尖，B 是背上骨刺的顶）到脚底约 792 px，也就是约 72 格**，脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）。镰刀臂、尾巴、爪子全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。深紫甲壳、酒红甲片、白牙、紫舌头、青色眼睛要分得开；暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（地刺、尖叫的声波、尖刺弹、吞噬都放到第 3 步单独画；眼睛和舌尖的光是身体的一部分，用平涂的亮色画）；不画地面，不画影子。
> - 交付：`outputs/chogath-picture/chogath-A.png`、`chogath-B.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/chogath-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/chogath_picture_done.zip`。

## 附图（在压缩包 `chogath_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_chogath_idle.png` | 英雄联盟原版科加斯的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_chogath_frontal.png` | 同一帧，正面 | 甲壳和酒红甲片怎么分、两条镰刀臂、前爪 |
| `refs/3_chogath_head.png` | 头部特写 | 大嘴、尖牙、紫舌头、青色眼睛、红獠牙、头冠甲片 |
| `refs/4_chogath_back.png` | 同一帧的背后 | 背上的骨刺、甲壳的宽度 |
| `refs/5_chogath_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/7_chogath_side.png` | 同一帧，接近侧面 | 头的长度、尾巴、身体的厚度 |
| `refs/8a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_B.png` | B 的布局示意（淡色，只看大小和地面线） | 他的大小、地面线（灰）；**姿势按文字：镰刀臂收在背上、尾巴收近** |
| `style/11_style_reksai.png` | 本包的雷克塞，8 倍放大，一格 = 一个像素 | **只看风格**：四脚着地的虚空巨兽在格子上怎么画 |
| `style/12_style_volibear.png` | 本包的沃利贝尔（8 倍） | **只看风格**：大体型野兽的分档和亮边 |
| `style/13_style_khazix.png` | 本包的卡兹克（8 倍） | **只看风格**：虚空甲壳、刃爪 |
| `style/14_style_nasus.png` | 本包的内瑟斯（8 倍） | **只看风格**：大个子的描边和暗色的亮边 |

## 提示词：`chogath-A.png` / `chogath-B.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a HUGE VOID BEAST ON ALL FOURS, its body armoured in DARK VIOLET-PURPLE CARAPACE plates with CRIMSON / WINE-RED edges and undersides and faint red glowing seams; a BIG LOW HEAD thrust forward near the ground with a WIDE MAW: two rows of WHITE FANGS, a PURPLE TONGUE with a pale cyan void glow at its tip, TWO SMALL GLOWING CYAN EYES, a pair of CURVED RED TUSKS at the jaw, layered wine-red plates on the crown; TWO THICK FRONT CLAWS planted on the ground and TWO SHORT HIND LEGS, all with RED HOOKED TALONS; TWO LONG THIN UPPER ARMS growing from the shoulders like SCYTHES, each ending in a LONG RED BLADE-CLAW; a row of PURPLE SPINES along the back; a LONG SEGMENTED ARMOURED TAIL behind with a SPIKED RED TIP (1 his idle, 3/4 view facing right - the look, the ANGLE and pose A; 2 the same from the front: where the purple carapace turns red, the two scythe arms, the front claws; 3 the head close-up: the maw, the fangs, the tongue, the cyan eyes, the tusks, the crown plates; 4 the same from behind: the spines, the width of the carapace; 5 the official illustration: his mood and colours; 7 the idle nearly from the side: the length of the head, the tail, the depth of the body). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a void beast on all fours on the grid (11), a big beast's shades and lit edges (12), void carapace and blade claws (13), a big body's outline and the lit edges of its dark parts (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (both scythe arms, the tail, every claw whole); all four feet level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 792 px (about 72 squares) from his highest point to his soles.
PROPORTIONS: a HUGE BEAST ON ALL FOURS, NOT a big-headed doll and NOT standing up like a man: a broad, low armoured body; the head big but not exaggerated (about a quarter of his body's length); thick front claws, short hind legs.
THE HEAD: the wine-red plated crown; the open maw with two rows of white fangs, each fang readable, and the purple tongue; TWO CYAN EYES of the SAME size, both visible (flat bright squares, no glow halo), fierce; the curved red tusks at the jaw.
THE COLOURS: the carapace dark violet-purple (3-4 shades); the plate edges, the crown, the talons, the scythe blades and the tail tip crimson / wine-red (3-4 shades); the two clearly separated, NO gradient - flat colour areas; the dark legs and tail with LIGHTER EDGES so they never turn into one dark mass.
THE GLOWING PARTS: the eyes, the void glow at the tongue's tip and the red seams in the carapace in flat bright colours, no soft glow.
THE VIEW: 3/4 view facing right (the head on the image right, the face to the front-right, the tail on the image left): the NEAR front claw, hind leg and scythe arm in front in full tone, the FAR ones behind a step darker.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the whole figure; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the purple carapace, the wine-red plates, the white fangs, the purple tongue and the cyan eyes clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no ground spikes, no sound wave, no flying spikes, no void energy), no background, no ground plane, no shadow, no text, no frame, no other characters.
POSE A (chogath-A.png): his idle (images 1, 2 and 8a) - on all fours, the body low, BOTH SCYTHE ARMS RAISED HIGH over his back, the head low and thrust forward with the maw open, the tail trailing behind.
POSE B (chogath-B.png): a COMPACT READY STANCE - the SAME beast with the SAME 11-px squares: on all fours, BOTH SCYTHE ARMS FOLDED BACK along the shoulders and back (not raised, the blades pointing backward), the head a little higher with the maw open, the TAIL CURLED CLOSE to the body, not trailing far (image 8b shows only his size and the ground line). Narrower and lower than pose A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，镰刀臂、尾巴、爪子完整，不出画。
- 比例：四肢着地的巨兽，不是站起来的人形，也不是大头娃娃；身体宽厚压低，头约占身长四分之一。
- 头：酒红甲片头冠、张开的大嘴、一颗颗看得清的白牙、紫舌头；**两只青色眼睛一样大、都看得见**；下巴两边红獠牙。
- 颜色：甲壳深紫、甲片边缘 / 爪 / 刃 / 尾尖酒红，平涂的色块、没有渐变；深色的腿和尾巴有亮边。
- A：镰刀上臂高高举在背上、头低、尾巴拖在后面；B：镰刀上臂**往后收**贴着背、尾巴收近，比 A 窄、矮。从最高点到脚底约 792 px（约 72 格），四只脚底都在同一条地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- A、B 两张都画完后，最后写 `outputs/chogath-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/chogath_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/chogath/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`tools/art/design_volibear_hd.py` 的做法，绝不按更少的行采样），和已合并的大体型英雄（沃利贝尔、雷克塞、内瑟斯、加里奥、布隆）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑 A / B 和定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画（3/4 正面 + **侧面朝右**两种角度），再自己做动作帧（无损：只整格平移、绕半格枢轴的四分之一转、镜像；一张脸用在所有帧）。英雄联盟的动作：普攻 chogath_attack1 / _2；E 恐惧之刺的攻击 chogath_crit；Q 破裂 chogath_spell4；W 野性尖叫 chogath_spell1；R 盛宴 chogath_spell2；跑 chogath_run；死亡 chogath_death。
