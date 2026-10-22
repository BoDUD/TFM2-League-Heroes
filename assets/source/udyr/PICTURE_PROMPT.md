# 兽灵行者 乌迪尔：第 0 步，先画像素风原图（给 Codex 的提示词）

> 乌迪尔是英雄联盟里一个**光着膀子的魁梧武僧**：**晒黑的皮肤**，胸口、肩膀、手臂上有**暗红色的部落纹身**；**一头深棕色的长脏辫**，披在肩上，**浓密的深色络腮胡**；脸左边垂着**一根蓝色的羽毛发辫**；两只拳头缠着**白色绷带**，前臂是**橙色的护腕**；腰上围着**一圈大颗的橙红色念珠**，中间一块**青灰色的石头腰牌**（刻着符文），垂下**两根橙色的粗绳**；**宽松的深棕色裤子**，膝盖上是**青灰色的石头护膝**，护膝下面一圈**灰蓝色的毛皮**；小腿缠着**深青色的绑腿**，脚上是**露脚趾的凉鞋**。
>
> 他靠四种兽灵姿态战斗。用户已经定了：技能 = **熊**（Q 狂暴爪击）、技能2 = **公羊**（E 踏火蛮冲）、大招 = **凤凰**（R 极凌飓风），**每个姿态单独一套动作**。所以请 Codex 画**五张全身像**（同一个乌迪尔，长相、颜色、**格子大小**都一样）：
> - **A：平常的待机，3/4 正面朝右**（附图 1、2、9a）。他扎着马步，**两只缠绷带的拳头举在脸两边**护住头，身子微微前倾；没有任何兽灵的部件。
> - **SA：A 的侧面，朝右**（附图 4、9b）。同一个姿势**正侧面朝右**。
> - **Q：熊姿态的待机，3/4 正面朝右**（附图 5、9c）。他**弓着背往前扑**，两手放低像熊掌；**一张熊皮披在背上和前面那只胳膊上**，熊头（耳朵、长吻）盖在他前面那只拳头上，像一只熊掌手套。
> - **E：公羊姿态的待机，3/4 正面朝右**（附图 6、9d）。他低头往前顶，像要冲锋；**两只巨大的卷曲公羊角**从他肩背上长出来，绕过头顶弯成两个大圈（棕褐色，一圈圈深色的纹）。
> - **R：凤凰姿态的待机，3/4 正面朝右**（附图 7、9e）。他**两臂向两边张开**，半蹲；**两条胳膊上竖着一排排深蓝色的羽刃**（根部橙红），**头发往上飘起**，像要起飞的鸟。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的沃利贝尔、格雷福斯、塞拉斯、奥恩（都是壮汉），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–8）。
> - **比例**：Q 版但要壮——**头比写实大一些**（头发连脸约占身体的四分之一多），**肩膀很宽、胸膛和肚子厚**，手臂粗、拳头大，腿短而结实；不要细长的写实比例。举起的拳头和兽灵部件**不能挡住脸**。
> - **脸**（附图 3 特写）：**两只眼睛都看得见**（每只至少 2×2 格，眼白一格、深色瞳孔，冷蓝色的眼神），浓眉皱着，深色络腮胡包住下巴，嘴巴在胡子里看得见；脏辫从头顶垂到肩上，**蓝色羽毛发辫**垂在脸左边。
> - **颜色**：皮肤晒黑的暖棕 3–4 档（亮面偏暖橙），纹身暗红 1–2 档；头发、胡子深棕近黑 2–3 档（**不要和皮肤糊成一团**）；羽毛发辫亮蓝 2 档；绷带白灰 2–3 档；护腕橙色 2–3 档；念珠橙红 3 档；腰牌、护膝青灰石头 3 档；裤子深棕 2–3 档；毛皮灰蓝 2 档；绑腿深青 2–3 档；凉鞋深棕。熊皮棕色带深色条纹 3 档；公羊角棕褐 3 档加深色环纹；凤凰羽刃深蓝 3 档、根部橙红 2 档。
> - **画布用正方形 1536×1536**。**A 从举起的拳头顶到脚底约 506 px，也就是约 46 格**；熊、公羊、凤凰用**同样的格子大小**，从最高点到脚底分别约 47、55、52 格（附图 9c–9e）。脚底在离画布底边约 146 px 的地方（附图 9a–9e 的灰线），他站在附图里的位置。羊角、羽刃全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（闪电、火焰、冰风暴、护盾光、兽灵的虚影都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/udyr-picture/udyr-A.png`、`udyr-SA.png`、`udyr-Q.png`、`udyr-E.png`、`udyr-R.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/udyr-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/udyr_picture_done.zip`。

## 附图（在压缩包 `udyr_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_udyr_idle.png` | 英雄联盟原版乌迪尔的平常待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_udyr_frontal.png` | 同一帧，正面 | 纹身、念珠、腰牌、绳子、护膝、绑腿、凉鞋 |
| `refs/3_udyr_head.png` | 头部特写 | 脏辫、脸、胡子、蓝羽毛发辫 |
| `refs/4_udyr_side.png` | 同一帧，侧面朝右 | SA 的角度：身子厚度、拳头的位置 |
| `refs/5_bear_stance.png` | 熊姿态的待机，3/4 朝右 | Q 的姿势和熊皮、熊头 |
| `refs/6_ram_stance.png` | 公羊姿态的待机，3/4 朝右 | E 的姿势和两只羊角 |
| `refs/7_phoenix_stance.png` | 凤凰姿态的待机，3/4 朝右 | R 的姿势、羽刃、飘起的头发 |
| `refs/8_udyr_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/9a_layout_A.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰） |
| `refs/9b_layout_SA.png` | SA 的布局示意 | 同上，侧面 |
| `refs/9c_layout_Q.png` | Q 的布局示意 | 同上，熊 |
| `refs/9d_layout_E.png` | E 的布局示意 | 同上，公羊 |
| `refs/9e_layout_R.png` | R 的布局示意 | 同上，凤凰 |
| `style/11_style_volibear.png` | 本包的沃利贝尔，8 倍放大，一格 = 一个像素 | **只看风格**：熊的皮毛、壮汉的体块和分档 |
| `style/12_style_graves.png` | 本包的格雷福斯（8 倍） | **只看风格**：男人的脸、胡子 |
| `style/13_style_sylas.png` | 本包的塞拉斯（8 倍） | **只看风格**：光胳膊、长发的男人 |
| `style/14_style_ornn.png` | 本包的奥恩（8 倍） | **只看风格**：羊角怎么画在格子上 |

## 提示词：`udyr-A.png` / `udyr-SA.png` / `udyr-Q.png` / `udyr-E.png` / `udyr-R.png`（同一段提示词，只换最后一段）

十七张图都附上，顺序同上表。

```text
Seventeen attached images. Images 1-8 are 3D renders and art of a character from a game: a HUGE BARE-CHESTED MONK BRAWLER with TANNED warm-brown skin covered in DARK RED TRIBAL TATTOOS on the chest, shoulders and arms, LONG DARK BROWN DREADLOCKS falling to the shoulders, a THICK DARK FULL BEARD, ONE BRIGHT BLUE FEATHER BRAID hanging by the left side of his face, WHITE BANDAGE WRAPS on both fists, ORANGE BRACERS on the forearms, a belt of BIG ORANGE-RED PRAYER BEADS round the waist with a TEAL-GREY STONE PLAQUE carved with a rune in front and TWO THICK ORANGE ROPES hanging from it, BAGGY DARK BROWN TROUSERS, TEAL-GREY STONE KNEE GUARDS with a ruff of GREY-BLUE FUR under them, DARK TEAL LEG WRAPS and open SANDALS with bare toes. (1 his plain idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the tattoos, the beads, the plaque, the ropes, the knee guards, the wraps, the sandals; 3 the head close-up: the dreadlocks, the face, the beard, the blue feather braid; 4 the plain idle from the side, facing right - the angle of SA; 5 his BEAR stance - the pose and the bear hide of Q; 6 his RAM stance - the pose and the ram horns of E; 7 his PHOENIX stance - the pose, the feather blades and the hair of R; 8 the official illustration: his mood, his colours, his face.) Images 9a-9e are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, fur and a burly body in flat shades (11), a man's face and beard (12), bare arms and long hair (13), big curled horns on the grid (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the horns, the feather blades, the fists); his soles level on one ground line about 146 px above the bottom edge (the grey line of images 9a-9e). He stands where the matching layout guide shows him, at its size: in the PLAIN idle about 506 px (about 46 squares) from his raised fists to his soles; the stances on the SAME square size, as tall as their guides show (bear about 47 squares, ram about 55, phoenix about 52, from the highest point to the soles).
PROPORTIONS: stylised and BURLY - the head a bit bigger than realistic (with the hair more than a quarter of his body height), VERY WIDE shoulders, a thick chest and belly, thick arms with big fists, short sturdy legs; NOT realistic slim proportions. The fists and the spirit parts NEVER cover his face.
THE FACE: BOTH EYES visible (each at least 2x2 squares: one white square and a dark pupil, a cold blue look), heavy frowning brows, the dark beard wrapping the jaw with the mouth visible in it, the dreadlocks falling from the top of the head to the shoulders, the blue feather braid by the left side of the face.
THE COLOURS: the skin warm tanned brown in 3-4 shades with a warm orange lit edge, the tattoos dark red in 1-2 shades; the hair and beard dark brown to near-black in 2-3 shades, NEVER one mass with the skin; the feather braid bright blue in 2 shades; the bandages white-grey in 2-3 shades; the bracers orange in 2-3 shades; the beads orange-red in 3 shades; the plaque and knee guards teal-grey stone in 3 shades; the trousers dark brown in 2-3 shades; the fur grey-blue in 2 shades; the leg wraps dark teal in 2-3 shades; the sandals dark brown. The bear hide brown with dark stripes in 3 shades; the ram horns tan-brown in 3 shades with dark rings; the phoenix feather blades dark blue in 3 shades with orange-red roots in 2.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the brown skin, the red tattoos, the dark hair and beard, the blue feather, the white bandages, the orange bracers and beads, the teal stone, the brown trousers, the grey-blue fur and the teal wraps clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no lightning, no fire, no ice storm, no shield glow, no ghostly spirit animals, no sparkles), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
```

最后一段按图换：

```text
PICTURE A (udyr-A.png): his PLAIN idle in 3/4 view facing right (images 1, 2 and 9a) - a wide low horse stance, the knees bent, BOTH BANDAGED FISTS RAISED beside his face as a guard, the body leaning a little forward, no spirit parts at all; the face to the front-right, stern; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker.
```

```text
PICTURE SA (udyr-SA.png): the SAME plain idle seen exactly from the SIDE, FACING RIGHT (images 4 and 9b) - the face to the image right with one eye visible, the fists raised in front of his face (not over it), both soles on the ground line.
```

```text
PICTURE Q (udyr-Q.png): his BEAR stance idle in 3/4 view facing right (images 5 and 9c) - HUNCHED FORWARD like a bear about to pounce, the knees bent, both hands low and open like paws; a BEAR HIDE draped over his back and over his front arm, the BEAR'S HEAD (ears, long snout, teeth) sitting over his front fist like a gauntlet; the face to the front-right, fierce; the same man, the same outfit, the same square size as picture A.
```

```text
PICTURE E (udyr-E.png): his RAM stance idle in 3/4 view facing right (images 6 and 9d) - the head lowered and the shoulders forward, ready to charge, the knees bent; TWO HUGE CURLED RAM HORNS growing from his shoulders and back, sweeping up over his head and curling round in big loops, tan-brown with dark rings; the face to the front-right under the horns (the horns frame the face, they do not cover it); the same man, the same square size as picture A.
```

```text
PICTURE R (udyr-R.png): his PHOENIX stance idle in 3/4 view facing right (images 7 and 9e) - a wide half-squat, BOTH ARMS SPREAD OUT to the sides like wings, the fingers open; rows of DARK BLUE FEATHER BLADES with orange-red roots standing along both arms, his DREADLOCKS SWEPT UP and flaring behind his head as if in a wind; the face to the front-right, calm and fierce; the same man, the same square size as picture A.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，羊角、羽刃、拳头完整，不出画。
- 壮实的 Q 版比例，头稍大、肩很宽、胸膛厚；**两只眼睛都看得见**；深色头发胡子不和皮肤糊成一团；**蓝羽毛发辫**。
- 暗红纹身、白绷带拳头、橙护腕、橙红念珠、青灰石腰牌和两根橙绳、深棕裤子、青灰石护膝和灰蓝毛皮、深青绑腿、凉鞋。
- A / SA 平常姿态（拳头举在脸两边，**不挡脸**）；Q 熊皮熊头、E 两只大卷羊角、R 两臂张开带羽刃；五张**格子大小一样**，脚底都在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 五张都画完后，最后写 `outputs/udyr-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/udyr_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，五张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/udyr/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_shyvana_hd.py` 的做法），和已合并的打野壮汉（沃利贝尔、沃里克、格雷福斯）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_<hero>_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Udyr`）：平常（野猪）spell2_idle / Spell2_run / Spell2_attack，熊 spell1_idle / Spell1_Run / Spell1_attack1、2 / spell1（Spell1_activate），公羊 Spell3_Idle / Spell3_Run / Spell3_Attack1、2 / Spell3_enhanced_attack（晕眩那一下）/ Spell3，凤凰 Spell4_Idle / Spell4_run / Spell4_attack1、2 / Spell4，死亡 Death。渲染各姿态要只留它自己的兽灵部件（`pack_udyr_picture.py` 的 STANCES：BearArms / RamArms+RamHorns / PhoenixArms+HairUp）。
