# 元素女皇 奇亚娜：第 0 步，先画像素风原图（给 Codex 的提示词）

> 奇亚娜是英雄联盟里一个**高傲的年轻女王**：**暖棕色的皮肤**；**一头长长的、微卷的银白色头发**（齐刘海，两边垂到胸前，阴影带一点淡紫）；头上戴着**金色的王冠**，王冠正中一块**翠绿色的宝石**，往上竖起**一个高高的白玉色尖冠**；**琥珀金色的眼睛**，黑色的眼线，眉毛微挑，一脸看不起人的神气；脖子上一圈**翠绿和金色相间的珠子项圈**；上身是**青绿色（土耳其蓝）的抹胸短裙**，镶**金色的边**和金色的花纹，身后垂着一片**墨绿近黑的裙摆**；上臂戴**金色的臂环**，手腕戴**金色的手镯**（嵌青绿色）；下身是**深棕近黑的紧身裤**，上面有**金色的三角花纹**；脚上是**紫棕色的凉鞋**，镶金。
> 她的武器是**一个巨大的圆环刀刃**（附图 7 最清楚）：环身是**深棕近黑的弯刃**（暗处带一点紫），**内圈一道青绿色的边**，环上几道**金色和青绿色的箍**，靠近两端是**玫瑰金 / 铜色的护手**，环上两个对角的位置各装着**一颗白玉色的水晶刃头**，刃头里嵌**青绿色的宝石**。
>
> 请 Codex 画**两张全身像**（同一个奇亚娜，长相、颜色、**格子大小**都一样），用户从里面挑大小：
> - **A：英雄联盟里的待机，3/4 正面朝右**（附图 1、2、8a）。她站着，一只手叉腰，一副高傲的样子，脸朝右前方、下巴微抬；**圆环刀刃用远侧的手拿着，竖立在她身侧偏后（画面左边）**，环的下沿贴近地面但不躺在地上。
> - **SA：A 的侧面，朝右**（附图 6、8b）。同一个奇亚娜**正侧面朝右**站着（脸朝画面右边，看得见一只眼睛），圆环竖在她身后。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的尼菈（深肤色女战士）、艾瑞莉娅（拿大刀刃的女战士）和妮蔻（Q 版大头女孩），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：Q 版，**头大**（头发连脸约占身高的三分之一，尖冠另算），身子短、腿短一点；不要细长的写实比例。**圆环比原版小一些**：直径大约是她身高的三分之二，环身粗一点、看得清；圆环是她最醒目的轮廓，但**绝不能挡住脸**（环的上沿最高到她肩膀）。
> - **脸**（附图 3 特写）：暖棕色的脸；**两只琥珀金色的眼睛一样大、一样高、都看得见**（每只至少 3×3 格，深色瞳孔，一格白色高光，上面一道黑色的眼线）；眉毛微挑；小嘴，嘴唇比皮肤深一档；银白色的齐刘海盖住额头，王冠压在刘海上。
> - **颜色**：皮肤暖棕 3 档（亮边偏橙金）；头发银白 3–4 档（暗处淡紫灰，**不要糊成一片白**）；王冠和所有首饰金色 3 档，宝石翠绿 2–3 档；尖冠白玉色 2–3 档；抹胸短裙青绿 3–4 档加金边；身后裙摆墨绿 2 档；紧身裤深棕近黑 2–3 档加金色三角纹；凉鞋紫棕 2 档；圆环：环身深棕近黑 3 档（暗处带紫），内圈青绿 2 档，金色 / 青绿的箍，玫瑰铜色护手 2 档，水晶刃头白玉 2–3 档加青绿宝石。
> - **画布用正方形 1536×1536**。**奇亚娜从尖冠顶到脚底约 660 px，也就是约 60 格**（圆环也在这个高度以内），脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）；她站在画布中间（附图 8a、8b 的位置）。尖冠、头发、圆环全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（元素的光、草叶、水花、碎石、冲击波、突进的残影都放到第 3 步单独画）；圆环上**不要**画元素的颜色（宝石就是青绿色）；不画地面，不画投影。
> - 交付：`outputs/qiyana-picture/qiyana-A.png`、`qiyana-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/qiyana-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/qiyana_picture_done.zip`。

## 附图（在压缩包 `qiyana_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_qiyana_idle.png` | 英雄联盟原版奇亚娜的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_qiyana_frontal.png` | 同一帧，正面 | 抹胸短裙、项圈、首饰、紧身裤的花纹、拿圆环的手 |
| `refs/3_qiyana_head.png` | 头部特写（3/4，不带圆环） | 王冠、尖冠、头发、脸、眼睛 |
| `refs/4_qiyana_back.png` | 同一帧的背后 | 头发背后、身后的裙摆、圆环背面 |
| `refs/5_qiyana_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/6_qiyana_side.png` | 同一帧，侧面朝右 | SA 的角度：头发的长度、身子的厚度、圆环 |
| `refs/7_qiyana_weapon.png` | 战斗待机（圆环举起来，看得最全） | **只看圆环**：弯刃、内圈、箍、护手、两颗水晶刃头 |
| `refs/8a_layout_front.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/11_style_nilah.png` | 本包的尼菈，8 倍放大，一格 = 一个像素 | **只看风格**：深肤色、白发、女战士在格子上怎么画 |
| `style/12_style_irelia.png` | 本包的艾瑞莉娅（8 倍） | **只看风格**：大刀刃、金属和首饰怎么分档 |
| `style/13_style_neeko.png` | 本包的妮蔻（8 倍） | **只看风格**：Q 版大头、脸、眼睛、短身子的比例 |

## 提示词：`qiyana-A.png` / `qiyana-SA.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from a game: a PROUD YOUNG EMPRESS with WARM TAN-BROWN SKIN, LONG SLIGHTLY WAVY SILVER-WHITE HAIR (straight bangs, two long locks down to her chest, pale lavender-grey shadows), a GOLD TIARA with an EMERALD-TEAL GEM in the middle and a TALL WHITE-JADE CREST rising from it, AMBER-GOLD EYES with black eyeliner and a raised, haughty brow, a CHOKER of emerald and gold beads, a TURQUOISE-TEAL STRAPLESS SHORT DRESS with GOLD TRIM and gold patterns and a DARK GREEN-BLACK FLAP hanging behind, GOLD ARMLETS on the upper arms and GOLD BRACELETS set with teal, DARK BROWN-BLACK LEGGINGS with GOLD TRIANGLE MARKINGS, PURPLE-BROWN SANDALS with gold, and her weapon: a HUGE RING BLADE (a dark brown-black curved blade with violet in its shadows, a TEAL INNER RIM, gold and teal bands, ROSE-COPPER GUARDS near its ends, and two WHITE-JADE CRYSTAL BLADE HEADS set with teal gems at opposite points of the ring). (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the dress, the choker, the jewellery, the leggings' markings, the hand holding the ring; 3 the head close-up without the ring: the tiara, the crest, the hair, the face, the eyes; 4 the same from behind: the back of the hair, the flap, the back of the ring; 5 the official illustration: her mood, her colours, her face; 6 the idle from the side, facing right - the angle of SA; 7 her battle stance, ONLY for the ring blade's construction.) Images 8a and 8b are layout guides: where she goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, dark skin, white hair and a woman warrior on the grid (11), a big blade, metal and jewellery in flat shades (12), chibi proportions with a big head, a clear face and a short body (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the crest, the hair, the ring); her soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). She is about 660 px (about 60 squares) from the top of her crest to her soles, the ring inside that height, and stands where images 8a / 8b show her (the centre).
PROPORTIONS: chibi - the head with its hair BIG (about a third of her height, the crest on top of that), a short body, shortish legs; NOT realistic slim proportions. The RING BLADE SMALLER than in the renders: its diameter about two thirds of her height, the blade a little thicker so it reads clearly; it is her strongest shape but it NEVER covers her face (its top edge no higher than her shoulders).
THE FACE: warm tan-brown; TWO AMBER-GOLD EYES of the SAME size at the SAME height, both visible (each at least 3x3 squares, a dark pupil, one white highlight square, a black eyeliner line above); a raised brow; a small mouth, the lips one shade darker than the skin; silver-white straight bangs over the forehead with the tiara on them.
THE COLOURS: the skin warm tan-brown in 3 shades with ORANGE-GOLD LIT EDGES; the hair silver-white in 3-4 shades with PALE LAVENDER-GREY SHADOWS so it never turns into one white mass; the tiara and all the jewellery gold in 3 shades, the gems emerald-teal in 2-3; the crest white jade in 2-3; the dress turquoise-teal in 3-4 shades with gold trim; the back flap dark green in 2; the leggings dark brown-black in 2-3 shades with gold triangle markings; the sandals purple-brown in 2; the ring: the blade dark brown-black in 3 shades with violet in the shadows, the inner rim teal in 2, gold and teal bands, the guards rose-copper in 2, the crystal heads white jade in 2-3 with teal gems.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around her and her ring; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the brown skin, the white hair, the gold jewellery, the teal dress, the dark leggings and the dark ring blade clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no elemental glow, no leaves, no water, no rocks, no shock waves, no dash trails, no sparkles), no element colours on the ring (its gems are teal), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (qiyana-A.png): her idle in 3/4 view facing right (images 1, 2 and 8a) - standing proudly, the near hand on her hip, the face to the front-right with the chin a little raised; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker; THE RING BLADE held in her FAR hand, standing upright beside and behind her on the image left, its lower edge near the ground but never lying on it.
PICTURE SA (qiyana-SA.png): the SAME empress seen exactly from the SIDE, FACING RIGHT (images 6 and 8b) - the face to the image right with one eye visible, one hand on her hip, both soles on the ground line, the ring blade standing upright behind her (image left).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，尖冠、头发、圆环完整，不出画。
- Q 版大头；**两只琥珀金色眼睛一样大、一样高**、带白色高光和黑眼线；眉毛微挑、一脸高傲；暖棕色皮肤；银白色头发（暗处淡紫灰，不糊成一片白）；金王冠、翠绿宝石、白玉尖冠。
- 青绿抹胸短裙加金边、墨绿裙摆、金臂环和手镯、翠绿金珠项圈、深棕紧身裤和金色三角纹、紫棕凉鞋。
- **圆环比原版小（直径约身高的三分之二），竖在她身侧偏后，不挡脸**；深色弯刃、青绿内圈、金箍、玫瑰铜护手、两颗白玉水晶刃头；**没有元素颜色**。
- A 是 3/4 正面朝右，SA 是正侧面朝右；两张都是从尖冠顶到脚底约 660 px（约 60 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写她的名字）。
- 两张都画完后，最后写 `outputs/qiyana-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/qiyana_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：头（一张脸用在所有帧）、两只手臂（挥环、叉腰）、圆环（会被挥起来横扫、举过头顶）、两条腿（跑、突进、落地）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | Idle / Run / Attack1–3 / — / Death | 普攻是挥圆环砍 |
| **Q 以绪塔尔之锋** | Spell1（River / Wall / Grass 三种） | 挥圆环往前横扫（元素的效果第 3 步另画） |
| **E 天纵之勇**（并入 W 方圆塑令） | Spell3 → Spell3_Hit，Spell2 | 突进到敌人身上砍一下；突进时武器附上元素 |
| **R 惊才绝景**（大招） | Spell4 | 把圆环往前一挥，放出一道冲击波 |

连招：**E → Q**（突进接横扫）、**R → Q**（大招晕住接岩石斩杀）、**Q → E → Q**（W 的元素附魔刷新 Q）。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/qiyana/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的打野 / 女战士（尼菈、艾瑞莉娅、纳亚菲利、妮蔻）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_<hero>_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Qiyana`；渲染时**不要** `--hide-submeshes`（皮肤把圆环藏起来了）。
