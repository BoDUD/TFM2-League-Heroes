# 纳祖芒荣耀 奎桑提：第 0 步，先画像素风原图（给 Codex 的提示词）

> 奎桑提是英雄联盟里一个**高大魁梧的坦克战士**：**深棕色皮肤**，**一头短短的黑色小脏辫**（往上翘），**修整过的黑色络腮胡**，左耳一个金色小耳环；脖子上围着**一条蓝紫色的围巾**；上身是**一件厚实的深红色棉甲外套**，袖子上有**金色和紫色的菱形花纹**；两肩是**巨大的古铜金色护肩**，前臂是**古铜金色的护腕和深色的拳套**；胸前挂着**一圈粗粗的金色绳索**和**好几块金色的圆形徽章**；腰下垂着**一片紫色的长围裙**（下摆是锯齿形）；**深紫色的裤子**，膝盖上是**古铜金色的护膝**，脚上一双**棕色的厚靴子**。
> 他的武器是两把**巨大的石头盾牌陀斧（ntofo）**：**青灰色的石头**，表面有**一块块亮青色的水晶**嵌在里面，边上一圈**金色的纹路**，一头有**一块金色的圆形徽章**，每把都比他还高。
>
> 他有**两种姿态**，用户已经定了：**全盛姿态单独一套动作**。所以请 Codex 画**四张全身像**（同一个奎桑提，长相、颜色、**格子大小**都一样），用户从里面挑大小：
> - **A：普通姿态的待机，3/4 正面朝右**（附图 1、2、8a）。他挺直站着，两手握着两把陀斧**竖在身体两侧**，陀斧的顶端高过他的头，像两面墙；脸朝右前方，表情沉稳自信。
> - **SA：A 的侧面，朝右**（附图 4、8b）。同一个姿势**正侧面朝右**（脸朝画面右边，看得见一只眼睛），陀斧竖在他身前和身后。
> - **O：全盛姿态的待机，3/4 正面朝右**（附图 5、8c）。他**弓着背往前压**，两脚分开半蹲，两只拳头放低，**两把陀斧甩开成长长的棍子，一头搁在地面上**，一副要冲上去的样子（附图 8c、8d 里陀斧尖比脚低，那是透视，**画的时候靴子和陀斧尖都踩在地面线上**）；表情凶狠、咧嘴。
> - **SO：O 的侧面，朝右**（附图 6、8d）。全盛姿态正侧面朝右，身子前倾，陀斧往前下方伸出去。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–14 是本包里的布隆、沃利贝尔、格雷福斯、加里奥（都是大块头），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：Q 版但要壮——**头比写实大一些**（头发连脸约占身体（不算陀斧）的四分之一多），**肩膀和护肩很宽**，手臂粗，腿短而结实；不要细长的写实比例。陀斧是他最醒目的轮廓，要画得清楚，但**不能挡住脸**。
> - **脸**（附图 3 特写）：深棕色的脸，**两只眼睛都看得见**（每只至少 2×2 格，眼白一格、深色瞳孔），浓眉，黑色络腮胡把下巴包住，嘴巴在胡子里看得见；头顶短短的黑色小脏辫往上翘。
> - **颜色**：皮肤深棕 3 档（亮面偏暖，**不要和胡子、头发糊成一团黑**）；头发、胡子近黑 2 档；围巾蓝紫 3 档；外套深红 3–4 档加金色、紫色的菱形花纹；护肩、护腕、护膝、徽章、绳索古铜金 3–4 档（亮边偏浅金）；围裙紫色 3 档；裤子深紫 2–3 档；靴子棕色 2–3 档；陀斧青灰石头 3–4 档，嵌的水晶亮青色 2 档，边纹金色。
> - **画布用正方形 1536×1536**。**普通姿态从陀斧最高的顶端到脚底约 616 px，也就是约 56 格**；全盛姿态用**同样的格子大小**，从最高点到脚底约 57 格（附图 8c）。脚底在离画布底边约 146 px 的地方（附图 8a–8d 的灰线），他站在附图里的位置。陀斧、护肩全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何技能特效（冲击波、护盾光、冲刺的风、裂纹的光都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/ksante-picture/ksante-A.png`、`ksante-SA.png`、`ksante-O.png`、`ksante-SO.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/ksante-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/ksante_picture_done.zip`。

## 附图（在压缩包 `ksante_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_ksante_idle.png` | 英雄联盟原版奎桑提的普通待机，3/4 朝右 | 颜色、形状、**角度**、A 的姿势 |
| `refs/2_ksante_frontal.png` | 同一帧，正面 | 外套花纹、绳索、徽章、围裙、护膝、靴子 |
| `refs/3_ksante_head.png` | 头部特写 | 头发、脸、胡子、耳环、围巾 |
| `refs/4_ksante_side.png` | 同一帧，侧面朝右 | SA 的角度：身子厚度、陀斧怎么竖在身前身后 |
| `refs/5_allout_idle.png` | 全盛姿态的待机，3/4 朝右 | O 的姿势：弓背、半蹲、陀斧甩开 |
| `refs/6_allout_side.png` | 全盛姿态，侧面朝右 | SO 的角度 |
| `refs/7_ksante_splash.png` | 官方加载画面 | 气质、颜色、脸 |
| `refs/8a_layout_base.png` | A 的布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰） |
| `refs/8b_layout_base_side.png` | SA 的布局示意 | 同上，侧面 |
| `refs/8c_layout_allout.png` | O 的布局示意 | 同上，全盛 |
| `refs/8d_layout_allout_side.png` | SO 的布局示意 | 同上，全盛侧面 |
| `style/11_style_braum.png` | 本包的布隆，8 倍放大，一格 = 一个像素 | **只看风格**：大块头、大盾、胡子怎么画在格子上 |
| `style/12_style_volibear.png` | 本包的沃利贝尔（8 倍） | **只看风格**：壮汉的体块和分档 |
| `style/13_style_graves.png` | 本包的格雷福斯（8 倍） | **只看风格**：男人的脸、胡子、外套 |
| `style/14_style_galio.png` | 本包的加里奥（8 倍） | **只看风格**：石头材质、金边怎么分档 |

## 提示词：`ksante-A.png` / `ksante-SA.png` / `ksante-O.png` / `ksante-SO.png`（同一段提示词，只换最后一段）

十五张图都附上，顺序同上表。

```text
Fifteen attached images. Images 1-7 are 3D renders and art of a character from a game: a HUGE BROAD-SHOULDERED TANK WARRIOR with DARK BROWN SKIN, short black TWISTS of hair standing up, a trimmed BLACK FULL BEARD, a small gold earring, a BLUE-VIOLET SCARF round his neck, a thick padded CRIMSON COAT with GOLD-AND-VIOLET DIAMOND PATTERNS on the sleeves, HUGE BRONZE-GOLD PAULDRONS, bronze-gold bracers and dark gauntlets, THICK GOLD ROPES and several round GOLD MEDALLION DISCS hung over his chest, a long VIOLET TABARD with a jagged hem, DARK PLUM TROUSERS with BRONZE-GOLD KNEE GUARDS and heavy BROWN BOOTS. His weapons are TWO GIANT STONE SHIELD-TONFAS: teal-grey stone slabs with BRIGHT TEAL CRYSTALS set in them, a gold trim line round the edge and a round gold medallion at one end, each one TALLER THAN HE IS. (1 his normal idle, 3/4 view facing right - the look, the ANGLE and the pose of A; 2 the same from the front: the coat patterns, the ropes, the medallions, the tabard, the knee guards, the boots; 3 the head close-up: the hair, the face, the beard, the earring, the scarf; 4 the normal idle from the side, facing right - the angle of SA; 5 his ALL OUT stance, 3/4 facing right - the pose of O; 6 the All Out stance from the side, facing right - the angle of SO; 7 the official illustration: his mood, his colours, his face.) Images 8a-8d are layout guides: where he goes on the canvas and how big, the grey line is the ground. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-14 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a big man with a big shield and a beard on the grid (11), a burly body in flat shades (12), a man's face, beard and coat (13), stone and gold trim in flat shades (14).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the tonfas, the pauldrons); his soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a-8d). He stands where the matching layout guide shows him, at its size: in the NORMAL stance about 616 px (about 56 squares) from the highest tonfa top to his soles; in the ALL OUT stance the SAME square size, about 57 squares from his highest point to his soles.
PROPORTIONS: stylised and BURLY - the head a bit bigger than realistic (with the hair more than a quarter of his body height, the tonfas not counted), VERY WIDE shoulders and pauldrons, thick arms, short sturdy legs; NOT realistic slim proportions. The tonfas are his strongest shape, clear and readable, but they NEVER cover his face.
THE FACE: dark brown; BOTH EYES visible (each at least 2x2 squares: one white square and a dark pupil), heavy brows, the black beard wrapping the jaw with the mouth visible in it, the short black twists standing up on top.
THE COLOURS: the skin dark brown in 3 shades with a warm lit edge, NEVER one black mass with the beard and hair; hair and beard near-black in 2 shades; the scarf blue-violet in 3 shades; the coat crimson in 3-4 shades with gold and violet diamond patterns; the pauldrons, bracers, knee guards, medallions and ropes bronze-gold in 3-4 shades with pale-gold lit edges; the tabard violet in 3 shades; the trousers dark plum in 2-3 shades; the boots brown in 2-3 shades; the tonfas teal-grey stone in 3-4 shades, their crystals bright teal in 2 shades, the trim gold.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him and his tonfas; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the brown skin, the black hair and beard, the blue-violet scarf, the crimson coat, the bronze-gold armour and ropes, the violet tabard, the plum trousers, the brown boots and the teal stone tonfas clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No spell effects (no shock waves, no shield glow, no dash wind, no glowing cracks, no sparkles), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
```

最后一段按图换：

```text
PICTURE A (ksante-A.png): his NORMAL idle in 3/4 view facing right (images 1, 2 and 8a) - standing tall and steady, each fist holding a tonfa UPRIGHT beside his body like two walls, their tops above his head, the face to the front-right, calm and confident; the NEAR leg on the image left in full tone, the FAR one on the image right a step darker.
```

```text
PICTURE SA (ksante-SA.png): the SAME normal idle seen exactly from the SIDE, FACING RIGHT (images 4 and 8b) - the face to the image right with one eye visible, the tonfas upright in front of him and behind him, both soles on the ground line.
```

```text
PICTURE O (ksante-O.png): his ALL OUT idle in 3/4 view facing right (images 5 and 8c) - HUNCHED FORWARD, the back bent, the knees bent in a wide half-squat, both fists low, the two tonfas swung out as LONG CLUBS reaching down toward the ground on both sides, ready to charge; his BOOTS stand ON the ground line and the tonfa ends rest on the ground beside and in front of them (in guide 8c the tips hang lower than the boots - do not copy that, keep both on the ground); the face to the front-right, fierce, teeth showing; the same man, the same outfit, the same square size as picture A.
```

```text
PICTURE SO (ksante-SO.png): the SAME All Out idle seen from the SIDE, FACING RIGHT (images 6 and 8d) - leaning forward, the face to the image right with one eye visible, the tonfas reaching forward and down, their ends resting on the ground in front of him, both soles on the ground line (not floating above it as in guide 8d).
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，陀斧、护肩完整，不出画。
- 壮实的 Q 版比例，头稍大、肩很宽；**两只眼睛都看得见**；黑色络腮胡和头发不和深棕的脸糊成一团；蓝紫围巾。
- 深红外套和金紫菱形花纹、古铜金护肩护腕护膝、金绳索和圆徽章、紫色锯齿围裙、深紫裤子、棕靴子。
- 两把**青灰石头陀斧**，嵌亮青色水晶、金边、金徽章；**不挡脸**。
- A / SA 普通姿态（陀斧竖着，顶端高过头）；O / SO 全盛姿态（弓背半蹲，陀斧甩开拖向地面）；四张**格子大小一样**，脚底都在地面线上。
- 没有任何技能特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 四张都画完后，最后写 `outputs/ksante-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/ksante_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/ksante/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_shyvana_hd.py` 的做法），和已合并的上单大块头（布隆、沃利贝尔、加里奥、蒙多）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户定大小、要不要侧面。
- 定下后第 1 步按游戏格子重画（`pack_<hero>_model.py` 的做法），一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py KSante`）：普通 attack1 / attack2，被动标记后的 Attack_Passive，Q Spell1_A / B / C（第三段冲击波），W spell2（Spell2_Enter + Spell2_Loop 蓄力，Spell2_Dash 冲刺），R spell4（Spell4_A 踢人，Spell4_dash 追上去），跑 Run1，死亡 Death；全盛（ao_）：Idle1_AllOut、Run_AllOut、Attack1_AllOut / Attack2_AllOut、Attack_Passive_AllOut、Spell1_A/B/C_AllOut、Spell2_Enter_AllOut / Spell2_Dash_AllOut。渲染陀斧要带 `--submesh-texture` 武器贴图并隐藏拖影和刀刃（`pack_ksante_picture.py` 的 PARTS）。
