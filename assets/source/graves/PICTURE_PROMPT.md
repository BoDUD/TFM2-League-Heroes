# 法外狂徒 格雷福斯：第 0 步，先画像素风原图（给 Codex 的提示词）

> 格雷福斯是一个**魁梧的枪手**：**往后梳的黑头发**，**浓密的黑络腮胡**，浓眉、眼神凶；肩上和背后围着一条**破边的深红色围巾 / 短斗篷**；身上是**棕色皮马甲**，近侧肩膀上一块**很大的棕色皮护肩**（铜色包边、铆钉），里面是**深藏青色的衬衫**，前臂有皮护腕、手上是皮手套，腰上一条宽皮带挂着弹药袋；下身是**宽松的深灰色裤子**，裤脚堆在**棕色靴子**上。武器是他的**霰弹枪"命运"**：**一把很大的双管霰弹枪，黑色钢管 + 亮金色 / 黄铜色的枪身**——后面是金色的两叉枪托和木头握把，中间一个金色的圆弹仓，前面两根**平行的黑色枪管**，枪口有金色的箍，枪管下面一个金色的前握把。他**两只手把枪平端在腰间，枪口朝右，枪管水平、笔直**。请 Codex 画**四张全身像**（同一个格雷福斯，长相、颜色、**格子大小**都一样），用户从里面挑：
> - **A：英雄联盟里的待机，3/4 正面朝右，枪照原版那么长**（附图 1、2、8a）。两腿分开微屈站着，两只手把霰弹枪平端在腰间，枪口朝右，枪管水平。
> - **B：同样的待机，枪短一些**。他和 A 一模一样，只是霰弹枪整体缩短：**枪管短一截，枪口只伸出他身体前面几格**（这样精灵图更紧凑），枪的样子（金色枪托、圆弹仓、两根黑枪管、金箍）都还在。
> - **SA：A 的正侧面，朝右**（附图 6、7、8b）。同一个格雷福斯**正侧面朝右**站着（脸朝画面右边，看得见一只眼睛和侧面的胡子），枪照 A 的长度平端在腰间。
> - **SB：B 的正侧面，朝右**。枪照 B 的长度。
>
> 选定后，第 1 步再按游戏格子做游戏尺寸的造型。你画的原图会按格子直接读回，所以**像素块要清楚、整齐、大小一致**。附图 11–13 是本包里的普朗克（大胡子、外套、手枪）、阿克尚（枪手）和德莱厄斯（魁梧的男人），**只看风格**。
> - **长相照英雄联盟原版**（附图 1–7）。
> - **比例**：Q 版，**头（连头发）约占身高的三分之一**，脸要大到看得清眼睛；肩膀宽、身子壮，腿短一些；不要细长的写实比例。
> - **脸**（附图 3 特写）：**两只眼睛一样大、一样高、都看得见**（每只至少 2 格，眼白 + 深色瞳孔），浓黑眉、黑络腮胡（分 2–3 档，不要糊成一块黑）。
> - **颜色**：深红围巾 3 档（亮边）、棕色皮马甲和护肩 3–4 档（铜色包边）、深藏青衬衫、深灰裤子和棕靴（**都要有偏亮的边，不要糊成一团黑**）；霰弹枪的枪管黑色钢 3 档（偏亮的高光线），枪身亮金色 3–4 档。
> - **枪必须笔直、水平**：两根枪管是两条横平竖直的平行线，不歪、不弯、不斜。
> - **画布用正方形 1536×1536**。**格雷福斯从头顶头发到鞋底约 748 px，也就是约 68 格**，鞋底在离画布底边约 146 px 的地方（附图 8a、8b 的灰线），站在附图 8a、8b 的位置。枪、围巾全在画面里，不能出画。
> - **像素块**：大小一致的方块，**每块 11 像素**，横平竖直对齐成网格；**外轮廓一圈 2 块宽的近黑描边**（枪也有）；每种材质内部 3–4 档平涂，不要零散的单个杂色格。暗处用这种材质自己最暗的一档，不要一圈黑。
> - 不画任何特效（枪口火光、子弹、烟雾、爆炸都放到第 3 步单独画）；不画地面，不画投影。
> - 交付：`outputs/graves-picture/graves-A.png`、`graves-B.png`、`graves-SA.png`、`graves-SB.png`（1536×1536，**真透明背景**）；原始生成图原样放进 `outputs/graves-picture/raw/`；附一个 `generation-prompts.txt`，写明实际用的提示词；**最后**在同一个文件夹写一个 `HANDOFF.md`（交付说明），再打包成 `outputs/graves_picture_done.zip`。

## 附图（在压缩包 `graves_pack0.zip` 里，按顺序附上）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_graves_idle.png` | 英雄联盟原版格雷福斯的待机，3/4 朝右 | 颜色、形状、**角度**、A / B 的姿势 |
| `refs/2_graves_frontal.png` | 同一帧，正面 | 围巾、护肩、马甲、皮带、裤子 |
| `refs/3_graves_head.png` | 头部特写（3/4） | 头发、脸、眼睛、胡子、围巾、护肩 |
| `refs/4_graves_back.png` | 同一帧的背后 | 围巾 / 斗篷的背面 |
| `refs/5_graves_splash.png` | 官方加载画面 | 气质、颜色 |
| `refs/6_graves_attack.png` | 开枪的一帧，侧面朝右 | **霰弹枪侧面的样子**（枪托、弹仓、两根枪管、前握把）、两只手怎么握枪 |
| `refs/7_graves_side.png` | 待机，侧面朝右 | SA / SB 的角度：身子的厚度、围巾、枪的位置 |
| `refs/8a_layout_front.png` | A / B 的布局示意（从模型上剪的，只看位置和大小） | 他在画布上的位置、大小、地面线（灰线）、头顶的高度（浅灰线） |
| `refs/8b_layout_side.png` | SA / SB 的布局示意 | 同上，侧面 |
| `style/11_style_gangplank.png` | 本包的普朗克，8 倍放大，一格 = 一个像素 | **只看风格**：络腮胡、外套、手枪在格子上怎么画 |
| `style/12_style_akshan.png` | 本包的阿克尚（8 倍） | **只看风格**：枪手、枪的金属分档 |
| `style/13_style_darius.png` | 本包的德莱厄斯（8 倍） | **只看风格**：魁梧的身材、深色衣服的亮边、脸 |

## 提示词：`graves-A.png` / `graves-B.png` / `graves-SA.png` / `graves-SB.png`（同一段提示词，只换最后一句）

十二张图都附上，顺序同上表。

```text
Twelve attached images. Images 1-7 are 3D renders and art of a character from the game: a BURLY GUNSLINGER with SLICKED-BACK BLACK HAIR, a FULL BLACK BEARD, thick black brows and a hard stare; a RAGGED DEEP CRIMSON SCARF / short poncho round his shoulders and down his back; a BROWN LEATHER VEST with a BIG BROWN LEATHER PAULDRON on the near shoulder (brass trim, rivets), a DARK NAVY SHIRT under it, leather bracers and gloves, a wide belt with shell pouches; LOOSE DARK GREY TROUSERS bunched over BROWN BOOTS; and his SHOTGUN: a HUGE DOUBLE-BARRELLED GUN of BLACK STEEL and POLISHED GOLD/BRASS - a two-pronged gold stock and a wooden grip at the back, a round gold drum chamber in the middle, TWO PARALLEL BLACK BARRELS in front with gold rings at the muzzles, a gold fore-grip under them - held LEVEL at his hip with both hands, the barrels pointing right (1 his idle, 3/4 view facing right - the look, the ANGLE and the pose of A and B; 2 the same from the front: the scarf, the pauldron, the vest, the belt, the trousers; 3 the head close-up: the hair, the face, the eyes, the beard, the scarf; 4 the same from behind; 5 the official illustration: his mood and colours; 6 a frame of his shot seen from the side facing right: the shotgun's side view and how both hands hold it; 7 the idle from the side, facing right - the angle of SA and SB). Images 8a and 8b are layout guides: where he goes on the canvas and how big, the grey line is the ground, the light grey line the top of his hair. Copy from the images the shapes, the colours and the construction - NOT their 3D shading. Images 11-13 are STYLE ONLY, other characters from the same game, each shown 8x so every square is one pixel: copy EXACTLY their pixel-art look - square size, the near-black outline, flat 3-4 step shading, a beard, a coat and a gun on the grid (11), a gunslinger and the shades of a gun's metal (12), a burly man with lit edges on dark clothes and a readable face (13).
Create ONE pixel-art picture, a 1536x1536 SQUARE PNG with a genuine transparent background (real alpha). Every square is 11 px. Everything whole inside the picture with comfortable transparent margins, nothing cut off (the whole shotgun, the scarf, both boots); his soles level on one ground line about 146 px above the bottom edge (the grey line of images 8a and 8b). He is about 748 px (about 68 squares) from the top of his hair to his soles and stands where images 8a / 8b show him.
PROPORTIONS: chibi - the head with the hair about a THIRD of his height, the face big enough that both eyes read clearly; broad shoulders, a sturdy body, shorter legs; NOT realistic slim proportions.
THE FACE: TWO EYES of the SAME size at the SAME height, both visible (each at least 2 squares, white with a dark pupil); thick black brows; the full black beard in 2-3 shades (never one black blob).
THE COLOURS: the crimson scarf in 3 shades with lit edges; the brown leather vest and pauldron in 3-4 shades with brass trim; the dark navy shirt; the dark grey trousers and the brown boots with LIGHTER EDGES so they never turn into one dark mass; the shotgun's barrels black steel in 3 shades with a lighter highlight line, its body bright gold in 3-4 shades.
THE SHOTGUN IS STRAIGHT AND LEVEL: the two barrels are two straight, parallel, perfectly HORIZONTAL lines of squares - never tilted, bent or skewed.
THE PIXEL GRID: every square the SAME size, 11 px, aligned on one straight grid (the picture is read back square for square); a 2-square near-black outline around him and around the gun; inside it every material in its own 3-4 flat shades, the shadow of a material its own darkest shade (never a second black ring), no stray single odd squares: the black hair and beard, the skin, the crimson scarf, the brown leather, the navy shirt, the grey trousers, the boots, the black barrels and the gold clearly separated; clear readable shapes, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects (no muzzle flash, no bullets, no smoke, no glow), no background, no ground plane, no cast shadow, no text, no frame, no other characters.
PICTURE A (graves-A.png): his idle in 3/4 view facing right (images 1, 2 and 8a) - feet apart, knees a little bent, both hands holding the shotgun LEVEL at his hip, the barrels pointing right at League's length; the NEAR side of the body on the image left in full tone, the FAR side a step darker.
PICTURE B (graves-B.png): the SAME Graves in the SAME idle, 3/4 view facing right; the shotgun SHORTER: the barrels cut down so the muzzles reach only a few squares past the front of his body (the gold stock, the drum, the two black barrels and the gold rings all still there); everything else exactly as in A.
PICTURE SA (graves-SA.png): the SAME Graves seen exactly from the SIDE, FACING RIGHT (images 6, 7 and 8b) - the face to the image right with one eye and the beard in profile, the shotgun held LEVEL at his hip with both hands, pointing right at League's length, the scarf hanging behind; his soles on the ground line, one leg a little in front of the other.
PICTURE SB (graves-SB.png): the SAME Graves exactly from the SIDE, FACING RIGHT (images 6, 7 and 8b); the shotgun shortened as in B.
```

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1536×1536；四周留边，枪、围巾、靴子完整，不出画。
- Q 版：头连头发约占身高三分之一；**两只眼睛一样大、一样高**；黑络腮胡分档。
- 深红围巾、棕色皮马甲和大护肩（铜边）、深藏青衬衫、深灰裤子、棕靴（深色都有亮边）；霰弹枪：金色两叉枪托、圆弹仓、**两根黑色平行枪管、笔直水平**、金色枪口箍和前握把。
- A / SA 是原版长度的枪，B / SB 的枪短一截；A / B 是 3/4 正面朝右，SA / SB 是正侧面朝右；四张都是从头顶到脚底约 748 px（约 68 格），脚底在地面线上。
- 没有任何特效。**每块 11 像素、大小一致、对齐网格**；2 块宽的近黑外描边；不糊、没有柔光、没有渐变、没有零散的杂色格；全硬 alpha（不要半透明的边）。
- 如果模型不肯画有名字的角色，把名字删掉，只留外观描述（提示词里本来就没写他的名字）。
- 四张都画完后，最后写 `outputs/graves-picture/HANDOFF.md`（列出交付的文件），再打包成 `outputs/graves_picture_done.zip`，这样我这边才知道已经交付完。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 把原画和 raw/ 放进 `assets/source/graves/codex_picture/`，**先在 8 倍下数描边台阶量出 Codex 实际的格子大小**（从来不是要求的 11 px），按它自己的格子读回（`design_zoe_hd.py` 的做法，绝不按更少的行采样），和已合并的枪手（阿克尚、普朗克、厄斐琉斯）按游戏里的大小并排，PPU 1.2 / 1.3 / 1.5 并排，给用户挑长枪还是短枪、定大小（PPU 不要超过 1.5）。
- 定下后第 1 步按游戏格子重画 3/4 正面和**侧面朝右**（动作都用侧面），一张脸用在所有帧。英雄联盟的动作（`tools/lol/anim_graph.py Graves`）：普攻 attack1（开枪 + 上膛 graves_reload）/ attack2（graves_reload_slow，弹药打光后的装弹）/ crit；Q spell1；W spell2；E spell3（快速拔枪，翻滚冲刺）；R spell4 + spell4_BACK（大招后坐力把他往后推）；跑 run；死亡 death。开枪的枪口火光烤进他自己的帧（游戏不镜像特效图，红色方会反）。
