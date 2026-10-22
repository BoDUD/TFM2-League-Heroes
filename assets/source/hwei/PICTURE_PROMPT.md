# 异画师 彗：第 0 步，先画像素风原图（给 Codex 的提示词）

> 彗是英雄联盟里一个**艾欧尼亚的画家**：**瘦高的年轻男子**，**皮肤苍白**；**一头凌乱的墨绿近黑的头发**（亮处带青绿色，刘海斜着垂下来遮住一点眼睛，后面长到脖子）；**一双墨绿色的眼睛**，眼皮半垂，眼下有一点阴影，一副疲惫、忧郁、心事重重的神情；耳朵上戴着小小的彩色耳饰；脖子上一圈**深紫色的颈环**。
> 他穿一件**露出一边肩膀的靛蓝色画师外套**：**宽大的青绿色翻领**，翻领和衣边镶**金色的花纹**，**袖口是红橙色**；里面是**红橙色的衬衫**和一件**棕色的马甲**；下身是**墨绿色的七分裤**，小腿上用**青绿色的丝带**扎住；一只脚踝戴**粉色的珠串**；脚上是**棕色的便鞋**。
> 他的武器是**一支巨大的画笔**（附图 1、2 最清楚）：深色的笔杆，笔头是**红色和深蓝色**的，末端收成一个**木色的笔尖**；待机时他用**画面右边那只手**握着笔杆，笔头**斜着朝前下方指向地面**。他背后还**浮着一道弯月形的墨痕**（深蓝色为主，夹着**橙色、青绿和金色**的笔触），从身后绕过头顶弯下来，末端**滴下三滴墨**。
>
> 请 Codex 画**两张全身像**（同一个彗，长相、颜色、**格子大小**都一样），用户从里面挑大小：
> - **A：英雄联盟里的待机，3/4 正面朝右**（附图 1、2、8a）。他懒懒地站着，一只手插在外套口袋附近，另一只手（画面右边）握着画笔斜指地面；脸朝右前方，微微低头。
> - **SA：A 的侧面，朝右**（附图 6、8b）。同一个彗**正侧面朝右**站着（脸朝画面右边，看得见一只眼睛），画笔斜指前下方，弯月墨痕在他身后。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的塞拉斯（男性英雄）、玛尔扎哈（瘦长的法师）和佐伊（Q 版大头、蓝绿配色），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–6）。
> - **比例**：Q 版，**头大**（头发连脸约占身高的三分之一），身子短、腿短一点；不要原版那种细长的写实比例。**画笔比原版短一些**：大约是他身高的四分之三，笔杆粗一点、看得清。**弯月墨痕比原版小**：在他身后，最高只比头发顶高出约 5 格，**绝不能挡住脸**。
> - **脸**（附图 3 特写）：苍白的脸；**两只墨绿色的眼睛一样大、一样高、都看得见**（每只至少 3×3 格，深色瞳孔，一格白色高光，上面一道深色的眼皮线，眼皮半垂）；细眉；小嘴，不笑；刘海斜着盖住一点额头和一边眼角，但**两只眼睛都要露出来**。
> - **颜色**：皮肤苍白 3 档（暗处偏淡紫灰）；头发墨绿近黑 3–4 档（亮处青绿，**不要糊成一片黑**）；颈环深紫 2 档；外套靛蓝 3–4 档，翻领青绿 3 档，金色花纹 2–3 档，袖口红橙 2–3 档；衬衫红橙 3 档，马甲棕色 2 档；裤子墨绿 2–3 档，丝带青绿 2 档；珠串粉色；鞋棕色 2 档；画笔：笔杆深棕近黑 2 档，笔头红色 2 档 + 深蓝 2–3 档，笔尖木色 2 档；弯月墨痕：深蓝 3 档，夹橙色、青绿、金色的笔触，墨滴深蓝。
> - **画布用正方形 1536×1536**。**彗从头发顶到脚底约 640 px，也就是约 58 格**（弯月墨痕在头顶上方，另算），脚底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线）；他站在画布中间（附图 8a、8b 的位置）。头发、墨痕、画笔全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（颜料飞溅、火、雷、岩浆、眼睛、画卷、发光都放到第 3 步单独画）；弯月墨痕是他造型的一部分，**画成平涂的笔触，不发光**；不画地面，不画投影。
> - 交付：`outputs/hwei-picture/hwei-A.png`、`hwei-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/hwei-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/hwei_picture_done.zip`。

## 附图（在压缩包 `hwei_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_hwei_idle.png` | 英雄联盟原版彗的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_hwei_frontal.png` | 同一帧，正面 | 外套、翻领、衬衫、马甲、裤子、握笔的手 |
| `refs/3_hwei_head.png` | 头部特写（3/4） | 头发、脸、眼睛、耳饰、颈环 |
| `refs/4_hwei_back.png` | 同一帧的背后 | 头发背后、外套背面、弯月墨痕 |
| `refs/5_hwei_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/6_hwei_side.png` | 同一帧，侧面朝右 | SA 的角度：头发、身子的厚度、画笔、墨痕 |
| `refs/8a_layout_front.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/11_style_sylas.png` | 本包的塞拉斯，8 倍放大，一格 = 一个像素 | **只看风格**：男性英雄的脸、头发、衣服在格子上怎么画 |
| `style/12_style_malzahar.png` | 本包的玛尔扎哈（8 倍） | **只看风格**：瘦长的法师、长外袍怎么分档 |
| `style/13_style_zoe.png` | 本包的佐伊（8 倍） | **只看风格**：Q 版大头、脸、眼睛、蓝绿橙配色 |

## 提示词：`hwei-A.png` / `hwei-SA.png`（同一段提示词，只换最后一句）

十一张图都附上，顺序同上表。

```text
Eleven attached images. Images 1-6 are 3D renders and art of a character from a game: a SLIM YOUNG PAINTER with PALE SKIN, MESSY DARK GREEN-BLACK HAIR with TEAL highlights (side-swept bangs falling over one eye, the back down to his neck), DARK GREEN EYES with HEAVY HALF-CLOSED LIDS and faint shadows under them - a tired, brooding, melancholic face - small colourful earrings and a DARK PURPLE CHOKER; an OFF-SHOULDER INDIGO PAINTER'S COAT with a WIDE TURQUOISE COLLAR, GOLD ORNAMENTAL TRIM and RED-ORANGE CUFFS, over a RED-ORANGE SHIRT and a BROWN VEST; DARK GREEN CROPPED TROUSERS tied with TEAL RIBBONS at the calves, a PINK BEAD ANKLET, BROWN LOAFERS; his weapon, a GIANT PAINTBRUSH (a dark shaft, a RED and NAVY brush head ending in a WOODEN POINT), and a FLOATING CRESCENT OF PAINT STROKES (mostly navy with ORANGE, TEAL and GOLD strokes) curling from behind his back over his head and down, dripping three ink drops. (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the coat, the collar, the shirt, the vest, the trousers, the hand holding the brush; 3 the head close-up: the hair, the face, the eyes, the earrings, the choker; 4 the same from behind: the back of the hair and coat, the crescent; 5 the official illustration: his mood, his colours, his face; 6 the idle from the side, facing right - the angle of SA.) Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a man's face, hair and clothes on the grid (11), a slim mage in a long robe in flat shades (12), chibi proportions with a big head, a clear face, a short body and a navy-teal-orange palette (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the hair, the crescent, the brush); his soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 640 px (about 58 squares) from the top of his hair to his soles, the crescent above that, and stands where images 8a / 8b show him (the centre).
PROPORTIONS: chibi - the head with its hair BIG (about a third of his height), a short body, shortish legs; NOT realistic slim proportions. The PAINTBRUSH SHORTER than in the renders: about three quarters of his height, the shaft a little thicker so it reads clearly. The CRESCENT SMALLER than in the renders: behind him, its top no more than about 5 squares above his hair; it NEVER covers his face.
THE FACE: pale; TWO DARK GREEN EYES of the SAME size at the SAME height, both visible (each at least 3x3 squares, a dark pupil, one white highlight square, a dark lid line above, the lids half closed); thin brows; a small unsmiling mouth; the bangs fall over the forehead and the corner of one eye but BOTH eyes stay visible.
THE COLOURS: the skin pale in 3 shades with PALE LAVENDER-GREY SHADOWS; the hair dark green-black in 3-4 shades with TEAL LIGHTS so it never turns into one black mass; the choker dark purple in 2; the coat indigo in 3-4 shades, the collar turquoise in 3, the trim gold in 2-3, the cuffs red-orange in 2-3; the shirt red-orange in 3, the vest brown in 2; the trousers dark green in 2-3 shades, the ribbons teal in 2; the anklet pink; the loafers brown in 2; the brush: the shaft dark brown-black in 2, the head red in 2 and navy in 2-3, the point wood in 2; the crescent navy in 3 shades with orange, teal and gold strokes, the drops navy.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him, his brush and the crescent; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the pale skin, the dark hair, the indigo coat, the turquoise collar, the orange shirt and the green trousers clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no paint splashes, no fire, no lightning, no lava, no eyes, no scrolls, no glow, no sparkles); the crescent is part of his look, drawn as flat painted strokes, not glowing; no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (hwei-A.png): his idle in 3/4 view facing right (images 1, 2 and 8a) - standing loosely, one hand near his coat pocket, the face to the front-right and a little lowered; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker; THE PAINTBRUSH held in the hand on the image right, slanting forward and down so its point nears the ground in front of him (never lying on it); the crescent behind his back and over his head.
PICTURE SA (hwei-SA.png): the SAME painter seen exactly from the SIDE, FACING RIGHT (images 6 and 8b) - the face to the image right with one eye visible, both soles on the ground line, the paintbrush slanting forward and down in front of him, the crescent behind him (image left).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，头发、墨痕、画笔完整，不出画。
- Q 版大头；**两只墨绿色眼睛一样大、一样高**、眼皮半垂、带白色高光；苍白皮肤；墨绿近黑的头发（亮处青绿，不糊成一片黑）；深紫颈环。
- 靛蓝外套、青绿翻领、金色花纹、红橙袖口；红橙衬衫、棕色马甲；墨绿七分裤、青绿丝带、粉色珠串、棕色便鞋。
- **画笔比原版短（约身高的四分之三）**，斜指前下方；红 + 深蓝的笔头、木色笔尖。**弯月墨痕比原版小，在身后，不挡脸**，平涂不发光。
- A 是 3/4 正面朝右，SA 是正侧面朝右；两张都是从头发顶到脚底约 640 px（约 58 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 两张都画完后，最后写 `outputs/hwei-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/hwei_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：头（一张脸用在所有帧）、两只手臂（挥笔、抬手）、画笔（会被挥起来、举高、往前点）、弯月墨痕（跟着身子走）、两条腿（跑、后退一步）。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | Idle_base / RunSlow / Attack01–02 / — / Death | 普攻是用画笔往前一挥，甩出一道颜料 |
| **主题：灾**（没骨火 / 攒聚雷 / 连皴山） | Spell1Q / Spell1W / Spell1E | 挥笔作画，放出火球 / 雷 / 岩浆裂地（特效第 3 步另画） |
| **主题：悚**（阴沉变意 / 滞涩幽瞳 / 双钩血喉） | Spell3W / Spell3E 等 | 挥笔画出恐惧的面孔 / 一只眼睛 / 两只钩爪 |
| **焚心绚华绘**（大招） | Spell4_alex | 举笔往前一甩，画卷在敌人身上展开 |

连招：**悚 → 灾**（先控住，再用攒聚雷 / 没骨火打）、**两个伤害技能命中 → 落款引爆**、**大招 → 灾**。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/hwei/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的中路法师（塞拉斯、玛尔扎哈、佐伊、维克兹、薇古丝）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_<hero>_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Hwei`（片段名小写：idle_base、runslow、attack01、spell1q…）；他的皮肤没有 loadscreen 贴图，加载画面用 Data Dragon 的 `Hwei_0.jpg`。
