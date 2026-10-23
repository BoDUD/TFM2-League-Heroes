# 双界灵兔 阿萝拉：第 0 步，先画像素风原图（给 Codex 的提示词）

> 阿萝拉是英雄联盟里**来往于两个世界的兔子女巫**（瓦斯塔亚人），用魔杖从敌人身上抽出灵物。这一步把她画出来，用户从里面挑：
> - **阿萝拉**：一个**娇小的女孩**；**铜红色的卷发**，两侧各一条短麻花辫；**圆形的金框眼镜**，镜片后面是**紫蓝色的大眼睛**；头上一顶**宽檐的青绿色女巫帽**，帽子里**竖着两只很长的兔耳朵**（橙红色的毛，耳朵里面浅色），帽带上插着**红色的羽毛**；脖子上是**米白色的高领毛衣**；肩上披着**浅蓝白色的毛边披肩**，里面是**米白色的长外套**（后摆长长地垂下来，带浅蓝色的里子）；胸前和裙摆是**青绿色带金色符文**的布；腰上一条**棕色的编织腰带**；身后一条**蓬松的橙色兔尾巴**；**深棕色的过膝长袜**，脚上是**带白毛边的短靴**；一只手拿着一根**细长的魔杖**（深色杖身、金色装饰、末端一点蓝光），待机时**扛在肩上，往后上方斜指**。
>
> 请 Codex 画**两张全身像**（**格子大小一样**），用户从里面挑大小：
> - **A：阿萝拉，英雄联盟里的待机，3/4 正面朝右**（附图 1、2、10a）。
> - **SA：A 的侧面，朝右**（附图 6、10b）。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的妮蔻、佐伊、悠米、彗，**只看风格**。
> - **长相照英雄联盟原版**（附图 1–6；附图 5 官方原画看气质和颜色）。
> - **比例**：Q 版。阿萝拉的**头（连帽子，不算耳朵）大**，约占帽顶到脚底的三分之一；身子小巧；**腿短一些**，两脚分开站稳；**兔耳朵很长**，从帽子里竖起来，高出帽顶约 12 格，可以一只直一只稍微弯；尾巴、魔杖、披肩都要画得清楚，**魔杖不挡脸**。
> - **阿萝拉的脸**（附图 3 特写）：浅肤色 3 档；**圆眼镜**（金色细框，每只镜片约 4×4 格）；**镜片后两只紫蓝色的眼睛一样大、一样高、都看得见**（每只至少 2×2 格，一格亮色高光）；脸颊一点淡粉；小嘴带一点好奇的笑。
> - **颜色**：皮肤浅暖色 3 档；头发铜红 3–4 档（亮处橙）；兔耳外侧橙红 3 档、里面浅粉白 2 档；帽子青绿 3–4 档（帽檐金边 2 档）；羽毛红 2–3 档；高领毛衣和外套米白 3 档；披肩浅蓝白 3 档（毛边一格一格的蓬松感）；青绿布和金色符文；腰带棕 2–3 档；尾巴橙 3 档；长袜深棕 2–3 档；靴子深色带白毛边；魔杖深棕 + 金 + 一格蓝光。
> - **画布用正方形 1536×1536**。**阿萝拉从帽顶（不算耳朵）到脚底约 595 px，也就是约 54 格；兔耳朵再往上约 12 格，耳尖到脚底约 66 格（约 726 px）**。脚底在离画布底边约 146 px 的地方（附图 10a、10b 的灰线）；站在画布中间（附图 10a、10b 的位置）。耳朵、魔杖、尾巴全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（灵物、诅咒、冲击波、发光雾都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/aurora-picture/aurora-A.png`、`aurora-SA.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/aurora-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/aurora_picture_done.zip`。

## 附图（在压缩包 `aurora_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_aurora_idle.png` | 英雄联盟原版阿萝拉的待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_aurora_frontal.png` | 同一帧，正面 | 帽子、披肩、外套、腰带、长袜、靴子 |
| `refs/3_aurora_head.png` | 头部特写（3/4） | 脸、眼镜、紫蓝眼睛、麻花辫、帽檐 |
| `refs/4_aurora_back.png` | 同一帧的背后 | 外套后摆、尾巴、耳朵从帽子里怎么穿出来 |
| `refs/5_aurora_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/6_aurora_side.png` | 同一帧，侧面朝右 | SA 的角度 |
| `refs/10a_layout_aurora.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 她在画布上的位置、大小、地面线（灰）；浅灰线 = 耳尖、帽顶 |
| `refs/10b_layout_aurora_side.png` | SA 的布局示意 | 同上，侧面 |
| `style/11_style_neeko.png` | 本包的妮蔻，8 倍放大，一格 = 一个像素 | **只看风格**：Q 版瓦斯塔亚女孩的脸、大眼睛 |
| `style/12_style_zoe.png` | 本包的佐伊（8 倍） | **只看风格**：小个子女孩、头发分档 |
| `style/13_style_yuumi.png` | 本包的悠米（8 倍） | **只看风格**：白色毛茸茸的毛边、耳朵 |
| `style/14_style_hwei.png` | 本包的彗（8 倍） | **只看风格**：长外套、后摆、衣料分档 |

## 提示词：`aurora-A.png` / `aurora-SA.png`（同一段提示词，只换最后一句）

十四张图都附上，顺序同上表。

```text
Fourteen attached images. Images 1-6 are 3D renders and art of a character from a game. THE WITCH (images 1-6): a PETITE young woman with BUNNY features; CURLY COPPER-RED HAIR with a short braid on each side; ROUND THIN GOLD GLASSES over big VIOLET-BLUE EYES; a WIDE-BRIMMED TEAL WITCH HAT with a gold-trimmed brim, TWO LONG RABBIT EARS (orange-red fur, pale pink-white inside) standing up through the hat, RED FEATHERS at the hat band; a CREAM cable-knit HIGH COLLAR; a PALE BLUE-WHITE FUR-TRIMMED SHAWL over her shoulders; a CREAM LONG COAT with long tails behind (pale blue lining); a TEAL tunic panel with GOLD RUNES; a BROWN BRAIDED BELT; a FLUFFY ORANGE BUNNY TAIL behind; DARK BROWN THIGH-HIGH STOCKINGS and short boots with white fur trim; a SLIM WAND in one hand (dark shaft, gold fittings, a tiny blue glow at the tip). (1 her idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the hat, the shawl, the coat, the belt, the stockings, the boots; 3 her head close-up: the face, the glasses, the eyes, the braids, the hat brim; 4 the same from behind: the coat tails, the tail, how the ears come through the hat; 5 the official illustration: her mood, colours and face; 6 the idle from the side, facing right - the angle of SA.) Images 10a-10b are layout guides: where the character goes on the canvas and how big, the grey line is the ground, the light lines the ear tips and the hat top. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a clear chibi girl's face with big eyes (11), a small girl and her hair in flat shades (12), white fluffy fur trim and ears on the grid (13), a long coat with tails in flat shades (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px, the SAME square size for both pictures. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the ear tips, the wand, the tail); the feet on one ground line about 146 px above the bottom edge (the grey line of images 10a-10b), standing where the guide shows the character (the centre). THE WITCH is about 595 px (about 54 squares) from the top of her HAT to her soles; the RABBIT EARS rise about 12 squares above the hat top (about 66 squares from the ear tips to the soles).
PROPORTIONS: chibi. The HEAD with the hat (not the ears) BIG (about a third of hat-top-to-soles); a small slender body; LEGS shorter than in the renders, the two feet apart, planted on the ground; the RABBIT EARS LONG and clear (one may bend a little); the tail, the wand and the shawl clearly drawn; the wand never covering the face.
THE WITCH'S FACE: light warm skin in 3 shades; ROUND GOLD GLASSES (thin frames, each lens about 4x4 squares); behind them TWO VIOLET-BLUE EYES of the SAME size at the SAME height, both visible (each at least 2x2 squares, one light highlight square); a little pink on the cheeks; a small curious smile.
THE COLOURS: the skin light warm in 3 shades; the hair COPPER-RED in 3-4 (orange lit); the ears orange-red in 3 outside, pale pink-white in 2 inside; the hat TEAL in 3-4 with a gold brim edge in 2; the feathers red in 2-3; the collar and the coat CREAM in 3; the shawl pale blue-white in 3 with a fluffy stepped fur edge; the teal cloth with gold runes; the belt brown in 2-3; the tail orange in 3; the stockings dark brown in 2-3; the boots dark with white fur trim; the wand dark brown + gold + one blue glow square.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around the character; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the copper hair, the teal hat, the orange ears, the cream coat, the pale blue shawl and the dark stockings clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no spirits, no curses, no shockwaves, no glowing mist, no sparkles); no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (aurora-A.png): THE WITCH's idle in 3/4 view facing right (images 1, 2 and 10a) - standing light and playful, the face to the front-right; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker and a little higher; the wand resting on her shoulder as in image 1, held in one hand, pointing up and back behind her head (never over the face), the other hand relaxed at her side; the coat tails and the tail behind her on the image left; the two long ears up through the hat.
PICTURE SA (aurora-SA.png): the SAME witch as A seen exactly from the SIDE, FACING RIGHT (images 6 and 10b) - the face to the image right with one eye and one lens visible, the ears up through the hat, the wand on her shoulder pointing up and back over her back (image 6), the coat tails and the tail behind her on the image left, both feet on the ground line.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，兔耳朵、魔杖、尾巴完整，不出画。
- 阿萝拉：Q 版大头（连帽子）；**圆金框眼镜**，镜片后**两只紫蓝眼睛一样大、一样高**、带高光；铜红卷发和两条短麻花辫；**青绿宽檐女巫帽**，**两只长兔耳朵**从帽子里竖起来，红羽毛；米白高领、浅蓝白毛边披肩、米白长外套（后摆）、青绿布金符文、棕腰带、橙色兔尾巴、深棕长袜、白毛边短靴；魔杖扛在肩上往后上方斜指，**不挡脸**；两脚分开站在地上。
- A 是 3/4 正面朝右，SA 是正侧面朝右；帽顶到脚底约 595 px（约 54 格），耳尖到脚底约 726 px（约 66 格），脚底在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写名字）。
- 两张都画完后，最后写 `outputs/aurora-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/aurora_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，两张都画完再交。

## 后面要用到的动作（这一步**不画**，只是让你画造型时心里有数）

动作帧由 Claude 按英雄联盟的动作逐帧拼（必要时再请你照骨架画关键姿势），所以造型里这些部件要**画得清楚、彼此分得开**：阿萝拉的头（一张脸用在所有帧，帽子和耳朵跟着头走）、拿魔杖的手臂和魔杖（挥、指）、另一只手臂（施法）、两条腿（跑、跳）、外套后摆和尾巴。

| 动作 | 英雄联盟的片段 | 说明 |
|---|---|---|
| 待机 / 跑 / 普攻 / 受击 / 死亡 | Idle / run_new_4 / attack6、attack8 / — / Death | 普攻是挥魔杖射出一道灵光 |
| **飞去来咒**（Q，skill） | Spell1 / Spell1_Recast / Spell1_Recast_Catch | 魔杖往前一甩射出飞弹，再一招手把诅咒收回来 |
| **怪奇喷涌**（E，skill2） | Spell3_reblock3 | 双手往前推出一道灵魂冲击，然后向后一跳 |
| **双界合一**（R，大招） | Spell4_E | 跳向前方，落地放出冲击波，脚下张开一片领域 |
| 灵纱洞开（W，并入被动） | Spell2 | 残血时向后一跳，隐身加速 |

连招：**E 命中 → Q**（冲击减速命中英雄，Q 就绪就立刻放）；**R 落地 → E**（大招落地马上接冲击）；**Q 去回两次命中都叠驱灵层**，满 3 层立刻抽出灵物回血；**R 领域还在时目标走到另一侧，她就传送过去接着打**。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/aurora/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（读 raw 原稿，不只看它自己的导出），和已合并的中路法师（彗、佐伊、薇古丝、妮蔻、维克托、辛德拉）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小（PPU 不要超过 1.5）、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_hwei_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作：`tools/lol/anim_graph.py Aurora`（片段名是 .anm 文件名：idle、run_new_4、attack6、attack8、spell1、spell1_recast、spell2、spell3_reblock3、spell4_e、death…）。加载画面在 WAD 里：`assets/characters/aurora/skins/base/auroraloadscreen_0.tex`。
